import csv
import io
import os
import secrets
import subprocess
import uuid
from asyncio import sleep
from contextlib import contextmanager
from pathlib import Path

import modal
import requests
import stripe
import validators
from dotenv import load_dotenv
from fasthtml import common as fh
from PIL import Image
from simpleicons.icons import si_github, si_pypi
from sqlmodel import Session as DBSession
from sqlmodel import create_engine, select
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from db.models import (
    ApiKey,
    ApiKeyCreate,
    ApiKeyRead,
    Gen,
    GenCreate,
    GenRead,
    GlobalBalance,
    GlobalBalanceCreate,
    GlobalBalanceRead,
    init_balance,
)
from utils import (
    DB_VOLUME,
    IN_PROD,
    MINUTES,
    NAME,
    PARENT_PATH,
    PYTHON_VERSION,
    SECRETS,
    VOLUME_CONFIG,
)

# -----------------------------------------------------------------------------

FE_PATH = PARENT_PATH / "frontend"
DB_VOL_PATH = str(PARENT_PATH / "local_db") if modal.is_local() else f"/{DB_VOLUME}"
if modal.is_local():
    if not os.path.exists(DB_VOL_PATH):
        os.mkdir(DB_VOL_PATH)
        os.chmod(DB_VOL_PATH, 0o777)  # noqa: S103


def get_app():  # noqa: C901
    # setup
    def before(req, sess):
        req.scope["session_id"] = sess.setdefault("session_id", str(uuid.uuid4()))
        req.scope["csrf_token"] = sess.setdefault("csrf_token", secrets.token_hex(32))
        req.scope["gen_form"] = sess.setdefault("gen_form", "image-url")

    def _not_found(req, exc):
        message = "Page not found!"
        typing_steps = len(message)
        return (
            fh.Title(NAME + " | 404"),
            fh.Div(
                nav(),
                fh.Main(
                    fh.Div(
                        fh.P(
                            message,
                            hx_indicator="#spinner",
                            cls="text-2xl text-red-300 animate-typing overflow-hidden whitespace-nowrap border-r-4 border-red-300",
                            style=f"animation: typing 2s steps({typing_steps}, end), blink-caret .75s step-end infinite",
                        ),
                    ),  # to contain typing animation
                    cls="flex flex-col justify-center items-center grow gap-4 p-8",
                ),
                toast_container(),
                footer(),
                cls="flex flex-col justify-between min-h-screen text-slate-100 bg-zinc-900 w-full",
            ),
        )

    f_app, _ = fh.fast_app(
        ws_hdr=True,
        before=fh.Beforeware(before, skip=[r"/favicon\.ico", r"/static/.*", r".*\.css"]),
        exception_handlers={404: _not_found},
        hdrs=[
            fh.Script(src="https://cdn.tailwindcss.com"),
            fh.HighlightJS(langs=["python", "javascript", "html", "css"]),
            fh.Link(rel="icon", href="/favicon.ico", type="image/x-icon"),
            fh.Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
            fh.Style(
                """
                @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
                }
                @keyframes blink-caret {
                    from, to { border-color: transparent; }
                    50% { border-color: red; }
                }
                .htmx-swapping {
                    opacity: 0;
                    transition: opacity .25s ease-out;
                }
                """
            ),
        ],
        live=os.getenv("LIVE", False),
        debug=os.getenv("DEBUG", False),
        boost=True,
    )
    fh.setup_toasts(f_app)
    f_app.add_middleware(
        CORSMiddleware,
        allow_origins=["/"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ## db
    upload_dir = Path(f"{DB_VOL_PATH}/uploads")
    upload_dir.mkdir(exist_ok=True)

    engine = create_engine(
        url=os.getenv("POSTGRES_URL"),
        echo=not IN_PROD,
    )

    @contextmanager
    def get_db_session():
        with DBSession(engine) as session:
            yield session

    def get_curr_gens(
        session_id,
        number: int = None,
        offset: int = 0,
        ids: list[int] = None,
    ) -> list[Gen]:
        with get_db_session() as db_session:
            query = select(Gen).where(Gen.session_id == session_id).order_by(Gen.request_at.desc()).offset(offset)
            if number:
                query = query.limit(number)
            if ids:
                query = query.where(Gen.id.in_(ids))
            return db_session.exec(query).all()

    def get_curr_keys(
        session_id,
        number: int = None,
        offset: int = 0,
        ids: list[int] = None,
    ) -> list[ApiKey]:
        with get_db_session() as db_session:
            query = (
                select(ApiKey).where(ApiKey.session_id == session_id).order_by(ApiKey.granted_at.desc()).offset(offset)
            )
            if number:
                query = query.limit(number)
            if ids:
                query = query.where(ApiKey.id.in_(ids))
            return db_session.exec(query).all()

    def get_curr_balance() -> GlobalBalance:
        with get_db_session() as db_session:
            curr_balance = db_session.get(GlobalBalance, 1)
            if not curr_balance:
                new_balance = GlobalBalanceCreate(balance=init_balance)
                curr_balance = GlobalBalance.model_validate(new_balance)
                db_session.add(curr_balance)
                db_session.commit()
                db_session.refresh(curr_balance)
            return curr_balance

    ## stripe
    stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
    DOMAIN: str = os.environ["DOMAIN"]

    ## SSE state
    shutdown_event = fh.signal_shutdown()
    global shown_generations
    shown_generations = {}
    global shown_keys
    shown_keys = []
    global shown_balance
    shown_balance = 0

    ## pagination
    max_gens = 10
    max_keys = 20

    # ui
    limit_chars = 100

    ## components
    def gen_view(
        g: GenRead,
        session,
    ):
        ### check if g is valid
        if not modal.is_local():
            VOLUME_CONFIG[f"{DB_VOL_PATH}"].reload()
        with get_db_session() as db_session:
            if db_session.get(Gen, g.id) is None:
                fh.add_toast(session, "Please refresh the page", "error")
                return None
        if g.session_id != session["session_id"]:
            fh.add_toast(session, "Please refresh the page", "error")
            return None

        image_src = None
        if g.image_url and validate_image_url(g.image_url):
            image_src = g.image_url
        elif g.image_file and isinstance(validate_image_file(image_file=None, upload_path=Path(g.image_file)), Path):
            temp_path = FE_PATH / Path(g.image_file).name
            with open(temp_path, "wb") as f:
                f.write(open(g.image_file, "rb").read())
            image_src = f"/{Path(g.image_file).name}"

        if g.failed:
            return fh.Card(
                fh.Div(
                    fh.Input(
                        type="checkbox",
                        name="selected_gens",
                        value=g.id,
                        hx_target="#gen-manage",
                        hx_swap="outerHTML",
                        hx_trigger="change",
                        hx_post="/show-select-gen-delete",
                        hx_indicator="#spinner",
                    ),
                    fh.Button(
                        fh.Svg(
                            fh.NotStr(
                                """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                            ),
                            cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden",
                        ),
                        hx_delete=f"/gen/{g.id}",
                        hx_indicator="#spinner",
                        hx_target="closest card",
                        hx_swap="outerHTML swap:.25s",
                        hx_confirm="Are you sure?",
                    ),
                    cls="w-1/2 flex justify-start items-center gap-2",
                ),
                fh.Div(
                    fh.Img(
                        src=image_src,
                        alt="Card image",
                        cls="max-h-24 max-w-24 md:max-h-60 md:max-w-60 object-contain",
                    ),
                    cls="w-3/6 flex justify-center items-center",
                ),
                fh.Div(
                    fh.Div(
                        fh.P(
                            "Generation failed",
                            cls="text-red-300",
                            hx_ext="sse",
                            sse_connect=f"/stream-gens/{g.id}",
                            sse_swap="UpdateGens",
                        ),
                        cls="flex flex-col justify-center items-center gap-2",
                    ),
                    cls="w-2/6",
                ),
                cls="w-full flex justify-between items-center p-4",
                id=f"gen-{g.id}",
            )
        elif g.response:
            return fh.Card(
                fh.Div(
                    fh.Input(
                        type="checkbox",
                        name="selected_gens",
                        value=g.id,
                        hx_target="#gen-manage",
                        hx_swap="outerHTML",
                        hx_trigger="change",
                        hx_post="/show-select-gen-delete",
                        hx_indicator="#spinner",
                    ),
                    fh.Button(
                        fh.Svg(
                            fh.NotStr(
                                """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                            ),
                            cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden",
                        ),
                        hx_delete=f"/gen/{g.id}",
                        hx_indicator="#spinner",
                        hx_target="closest card",
                        hx_swap="outerHTML swap:.25s",
                        hx_confirm="Are you sure?",
                    ),
                    cls="w-1/6 flex justify-start items-center gap-2",
                ),
                fh.Div(
                    fh.Img(
                        src=image_src,
                        alt="Card image",
                        cls="max-h-24 max-w-24 md:max-h-60 md:max-w-60 object-contain",
                    ),
                    cls="w-3/6 flex justify-center items-center",
                ),
                fh.Div(
                    fh.Div(
                        fh.P(
                            g.response[:limit_chars] + ("..." if len(g.response) > limit_chars else ""),
                            onclick=f"navigator.clipboard.writeText('{g.response.replace(chr(92), chr(92)*2)}');",  # since latex includes backslashes
                            hx_post="/toast?message=Copied to clipboard!&type=success",
                            hx_indicator="#spinner",
                            hx_target="#toast-container",
                            hx_swap="outerHTML",
                            cls="text-blue-300 hover:text-blue-100 cursor-pointer max-w-full",
                            title="Click to copy",
                            hx_ext="sse",
                            sse_connect=f"/stream-gens/{g.id}",
                            sse_swap="UpdateGens",
                        ),
                        cls="flex flex-col justify-center items-center gap-2",
                    ),
                    cls="w-2/6",
                ),
                cls="w-full flex justify-between items-center p-4",
                id=f"gen-{g.id}",
            )
        return fh.Card(
            fh.Div(
                fh.Input(
                    type="checkbox",
                    name="selected_gens",
                    value=g.id,
                    hx_target="#gen-manage",
                    hx_swap="outerHTML",
                    hx_trigger="change",
                    hx_post="/show-select-gen-delete",
                    hx_indicator="#spinner",
                ),
                fh.Button(
                    fh.Svg(
                        fh.NotStr(
                            """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                        ),
                        cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer md:block hidden",
                    ),
                    hx_delete=f"/gen/{g.id}",
                    hx_indicator="#spinner",
                    hx_target="closest card",
                    hx_swap="outerHTML swap:.25s",
                    hx_confirm="Are you sure?",
                ),
                cls="w-1/6 flex justify-start items-center gap-2",
            ),
            fh.Div(
                fh.Img(
                    src=image_src,
                    alt="Card image",
                    cls="max-h-24 max-w-24 md:max-h-60 md:max-w-60 object-contain",
                ),
                cls="w-3/6 flex justify-center items-center",
            ),
            fh.Div(
                fh.Div(
                    fh.P(
                        "Scanning image ...",
                        hx_ext="sse",
                        sse_connect=f"/stream-gens/{g.id}",
                        sse_swap="UpdateGens",
                    ),
                    cls="flex flex-col justify-center items-center gap-2",
                ),
                cls="w-2/6",
            ),
            cls="w-full flex justify-between items-center p-4",
            id=f"gen-{g.id}",
        )

    def key_view(
        k: ApiKeyRead,
        session,
    ):
        with get_db_session() as db_session:
            if db_session.get(ApiKey, k.id) is None:
                fh.add_toast(session, "Please refresh the page", "error")
                return None
        if k.session_id != session["session_id"]:
            fh.add_toast(session, "Please refresh the page", "error")
            return None
        if not k.key or not k.granted_at:
            fh.add_toast(session, "Please refresh the page", "error")
            return None

        obscured_key = k.key[:4] + "*" * (len(k.key) - 4)
        short_key = obscured_key[:8] + "..."

        return (
            fh.Tr(
                fh.Td(
                    fh.Div(
                        fh.Input(
                            type="checkbox",
                            name="selected_keys",
                            value=k.id,
                            hx_target="#key-manage",
                            hx_swap="outerHTML",
                            hx_trigger="change",
                            hx_post="/show-select-key-delete",
                            hx_indicator="#spinner",
                        ),
                        fh.Button(
                            fh.Svg(
                                fh.NotStr(
                                    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" /></svg>"""
                                ),
                                cls="w-8 h-8 text-red-300 hover:text-red-100 cursor-pointer hidden md:block",
                            ),
                            hx_delete=f"/key/{k.id}",
                            hx_indicator="#spinner",
                            hx_target="closest tr",
                            hx_swap="outerHTML swap:.25s",
                            hx_confirm="Are you sure?",
                        ),
                        cls="w-1/6 flex justify-start items-center gap-2",
                    ),
                    fh.Div(
                        fh.P(
                            short_key,
                            onclick=f"navigator.clipboard.writeText('{k.key}');",
                            hx_post="/toast?message=Copied to clipboard!&type=success",
                            hx_indicator="#spinner",
                            hx_target="#toast-container",
                            hx_swap="outerHTML",
                            cls="text-blue-300 hover:text-blue-100 cursor-pointer",
                            title="Click to copy",
                            id=f"key-element-{k.id}",
                        ),
                        cls="w-3/6",
                    ),
                    fh.Div(
                        fh.P(
                            k.granted_at.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        cls="w-2/6",
                    ),
                    id=f"key-{k.id}",
                    cls="w-full flex justify-between items-center p-4",
                ),
                cls="flex grow",
            ),
        )

    def balance_view():
        return (
            fh.Div(
                fh.P("Global balance:"),
                fh.P(
                    f"{GlobalBalanceRead.model_validate(get_curr_balance()).balance} credits",
                    cls="font-bold",
                    hx_ext="sse",
                    sse_connect="/stream-balance",
                    sse_swap="UpdateBalance",
                ),
                cls="flex items-start gap-0.5 md:gap-1",
            ),
        )

    def gen_form_toggle(gen_form: str, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.Button(
                "Image URL",
                id="gen-form-toggle-url",
                cls="w-full h-full text-blue-100 bg-blue-500 p-2 border-blue-500 border-2"
                if gen_form == "image-url"
                else "w-full h-full text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100",
                hx_get="/get-gen-form?view=image-url",
                hx_indicator="#spinner",
                hx_target="#gen-form",
                hx_swap="innerHTML",
            ),
            fh.Button(
                "Image Upload",
                id="gen-form-toggle-upload",
                cls="w-full h-full text-blue-100 bg-blue-500 p-2 border-blue-500 border-2"
                if gen_form == "image-upload"
                else "w-full h-full text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100",
                hx_get="/get-gen-form?view=image-upload",
                hx_indicator="#spinner",
                hx_target="#gen-form",
                hx_swap="innerHTML",
            ),
            id="gen-form-toggle",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-full flex flex-col md:flex-row gap-2 md:gap-4",
        )

    def num_gens(gen_count, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.P(
                f"({gen_count} total generations)",
                cls="text-blue-300 text-md whitespace-nowrap",
            ),
            id="gen-count",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-auto h-full flex justify-center items-center",
        )

    def num_keys(key_count, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.P(
                f"({key_count} total keys)",
                cls="text-blue-300 text-md whitespace-nowrap",
            ),
            id="key-count",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-auto h-full flex justify-center items-center",
        )

    def gen_manage(gens_present: bool, gens_selected: bool = False, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.Button(
                "Delete selected",
                hx_delete="/gens/select",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if gens_present and gens_selected
            else None,
            fh.Button(
                "Delete all",
                hx_delete="/gens",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if gens_present
            else None,
            fh.Button(
                "Export to CSV",
                id="export-gens-csv",
                hx_get="/export-gens",
                hx_indicator="#spinner",
                hx_target="this",
                hx_swap="none",
                hx_boost="false",
                cls="text-green-300 hover:text-green-100 p-2 border-green-300 border-2 hover:border-green-100 w-full h-full",
            )
            if gens_present
            else None,
            id="gen-manage",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="flex flex-col md:flex-row justify-center items-center gap-4 w-full",
        )

    def key_manage(keys_present: bool, keys_selected: bool = False, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.Button(
                "Delete selected",
                hx_delete="/keys/select",
                hx_indicator="#spinner",
                hx_target="#api-key-table",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if keys_present and keys_selected
            else None,
            fh.Button(
                "Delete all",
                hx_delete="/keys",
                hx_indicator="#spinner",
                hx_target="#api-key-table",
                hx_confirm="Are you sure?",
                cls="text-red-300 hover:text-red-100 p-2 border-red-300 border-2 hover:border-red-100 w-full h-full",
            )
            if keys_present
            else None,
            fh.Button(
                "Export to CSV",
                id="export-keys-csv",
                hx_get="/export-keys",
                hx_indicator="#spinner",
                hx_target="this",
                hx_swap="none",
                hx_boost="false",
                cls="text-green-300 hover:text-green-100 p-2 border-green-300 border-2 hover:border-green-100 w-full h-full",
            )
            if keys_present
            else None,
            id="key-manage",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="flex flex-col md:flex-row justify-center items-center gap-4 w-full",
        )

    def gen_load_more(gens_present: bool, still_more: bool, idx: int = 2, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.Button(
                "Load More",
                hx_get=f"/page-gens?idx={idx}",
                hx_indicator="#spinner",
                hx_target="#gen-list",
                hx_swap="beforeend",
                cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100 w-full h-full",
            )
            if gens_present and still_more
            else None,
            id="load-more-gens",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-full md:w-2/3",
        )

    def key_load_more(keys_present: bool, still_more: bool, idx: int = 2, hx_swap_oob: bool = "false"):
        return fh.Div(
            fh.Button(
                "Load More",
                hx_get=f"/page-keys?idx={idx}",
                hx_indicator="#spinner",
                hx_target="#api-key-table",
                hx_swap="beforeend",
                cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100 w-full h-full",
            )
            if keys_present and still_more
            else None,
            id="load-more-keys",
            hx_swap_oob=hx_swap_oob if hx_swap_oob != "false" else None,
            cls="w-full md:w-2/3",
        )

    ## layout
    def nav():
        return fh.Nav(
            fh.A(
                f"{NAME}",
                href="/",
                cls="text-xl text-blue-300 hover:text-blue-100 font-mono font-family:Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'",
            ),
            fh.Svg(
                fh.NotStr(
                    """<style>
                    .spinner_zWVm { animation: spinner_5QiW 1.2s linear infinite, spinner_PnZo 1.2s linear infinite; }
                    .spinner_gfyD { animation: spinner_5QiW 1.2s linear infinite, spinner_4j7o 1.2s linear infinite; animation-delay: .1s; }
                    .spinner_T5JJ { animation: spinner_5QiW 1.2s linear infinite, spinner_fLK4 1.2s linear infinite; animation-delay: .1s; }
                    .spinner_E3Wz { animation: spinner_5QiW 1.2s linear infinite, spinner_tDji 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_g2vs { animation: spinner_5QiW 1.2s linear infinite, spinner_CMiT 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_ctYB { animation: spinner_5QiW 1.2s linear infinite, spinner_cHKR 1.2s linear infinite; animation-delay: .2s; }
                    .spinner_BDNj { animation: spinner_5QiW 1.2s linear infinite, spinner_Re6e 1.2s linear infinite; animation-delay: .3s; }
                    .spinner_rCw3 { animation: spinner_5QiW 1.2s linear infinite, spinner_EJmJ 1.2s linear infinite; animation-delay: .3s; }
                    .spinner_Rszm { animation: spinner_5QiW 1.2s linear infinite, spinner_YJOP 1.2s linear infinite; animation-delay: .4s; }
                    @keyframes spinner_5QiW { 0%, 50% { width: 7.33px; height: 7.33px; } 25% { width: 1.33px; height: 1.33px; } }
                    @keyframes spinner_PnZo { 0%, 50% { x: 1px; y: 1px; } 25% { x: 4px; y: 4px; } }
                    @keyframes spinner_4j7o { 0%, 50% { x: 8.33px; y: 1px; } 25% { x: 11.33px; y: 4px; } }
                    @keyframes spinner_fLK4 { 0%, 50% { x: 1px; y: 8.33px; } 25% { x: 4px; y: 11.33px; } }
                    @keyframes spinner_tDji { 0%, 50% { x: 15.66px; y: 1px; } 25% { x: 18.66px; y: 4px; } }
                    @keyframes spinner_CMiT { 0%, 50% { x: 8.33px; y: 8.33px; } 25% { x: 11.33px; y: 11.33px; } }
                    @keyframes spinner_cHKR { 0%, 50% { x: 1px; y: 15.66px; } 25% { x: 4px; y: 18.66px; } }
                    @keyframes spinner_Re6e { 0%, 50% { x: 15.66px; y: 8.33px; } 25% { x: 18.66px; y: 11.33px; } }
                    @keyframes spinner_EJmJ { 0%, 50% { x: 8.33px; y: 15.66px; } 25% { x: 11.33px; y: 18.66px; } }
                    @keyframes spinner_YJOP { 0%, 50% { x: 15.66px; y: 15.66px; } 25% { x: 18.66px; y: 18.66px; } }
                </style>
                <rect class="spinner_zWVm" x="1" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_gfyD" x="8.33" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_T5JJ" x="1" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_E3Wz" x="15.66" y="1" width="7.33" height="7.33"/>
                <rect class="spinner_g2vs" x="8.33" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_ctYB" x="1" y="15.66" width="7.33" height="7.33"/>
                <rect class="spinner_BDNj" x="15.66" y="8.33" width="7.33" height="7.33"/>
                <rect class="spinner_rCw3" x="8.33" y="15.66" width="7.33" height="7.33"/>
                <rect class="spinner_Rszm" x="15.66" y="15.66" width="7.33" height="7.33"/>
                """
                ),
                id="spinner",
                cls="htmx-indicator w-8 h-8 absolute top-12 md:top-6 left-1/2 transform -translate-x-1/2 fill-blue-300",
            ),
            fh.Div(
                fh.A(
                    "Developer",
                    href="/developer",
                    cls="text-lg text-blue-300 hover:text-blue-100 font-mono font-family:Consolas, Monaco, 'Lucida Console', 'Liberation Mono', 'DejaVu Sans Mono', 'Bitstream Vera Sans Mono', 'Courier New'",
                ),
                fh.Div(
                    fh.A(
                        fh.Svg(
                            fh.NotStr(
                                si_github.svg,
                            ),
                            cls="w-8 h-8 text-blue-300 hover:text-blue-100 cursor-pointer",
                        ),
                        href="https://github.com/andrewhinh/formless",
                        target="_blank",
                    ),
                    fh.A(
                        fh.Svg(
                            fh.NotStr(
                                si_pypi.svg,
                            ),
                            cls="w-8 h-8 text-blue-300 hover:text-blue-100 cursor-pointer",
                        ),
                        href="https://pypi.org/project/formless/",
                        target="_blank",
                    ),
                    cls="flex flex-row gap-4",
                ),
                cls="flex flex-col items-end md:flex-row md:items-center gap-2 md:gap-8",
            ),
            cls="flex justify-between items-center p-4 relative",
        )

    def main_content(
        session,
    ):
        curr_gen_form = session["gen_form"]
        gens_present = bool(get_curr_gens(session["session_id"], number=1))
        return fh.Main(
            fh.Div(
                gen_form_toggle(curr_gen_form),
                fh.Div(
                    id="gen-form",
                    hx_get=f"/get-gen-form?view={curr_gen_form}",
                    hx_indicator="#spinner",
                    hx_target="#gen-form",
                    hx_swap="outerHTML",
                    hx_trigger="load",
                ),
                cls="w-full md:w-2/3 flex flex-col gap-4 justify-center items-center items-center",
            ),
            num_gens(len(get_curr_gens(session["session_id"]))),
            fh.Form(
                gen_manage(gens_present),
                fh.Div(
                    get_gen_table_part(session),
                    id="gen-list",
                    cls="w-full flex flex-col gap-2",
                ),
                cls="w-full md:w-2/3 flex flex-col gap-4 justify-center items-center",
            ),
            gen_load_more(
                gens_present, len(get_curr_gens(session["session_id"], number=max_gens, offset=max_gens)) > 0
            ),
            cls="flex flex-col justify-start items-center grow gap-4 p-8",
        )

    def developer_page(
        session,
    ):
        keys_present = bool(get_curr_keys(session["session_id"], number=1))
        return fh.Main(
            fh.Button(
                "Request New Key",
                id="request-new-key",
                hx_post="/request-key",
                hx_indicator="#spinner",
                hx_target="#api-key-table",
                hx_swap="afterbegin",
                cls="text-blue-300 hover:text-blue-100 p-2 w-full md:w-2/3 border-blue-300 border-2 hover:border-blue-100",
            ),
            num_keys(len(get_curr_keys(session["session_id"]))),
            fh.Form(
                key_manage(keys_present),
                fh.Table(
                    fh.Thead(
                        fh.Tr(
                            fh.Th(
                                fh.P("Key", cls="font-bold w-3/6"),
                                fh.P("Granted At", cls="font-bold w-2/6"),
                                cls="w-full flex justify-end items-center p-4",
                            ),
                            cls="flex grow",
                        ),
                    ),
                    fh.Tbody(
                        get_key_table_part(session),
                        id="api-key-table",
                    ),
                    cls="w-full text-sm md:text-lg flex flex-col border-slate-500 border-2",
                ),
                cls="w-full md:w-2/3 flex flex-col gap-4 justify-center items-center",
            ),
            key_load_more(
                keys_present, len(get_curr_keys(session["session_id"], number=max_keys, offset=max_keys)) > 0
            ),
            cls="flex flex-col justify-start items-center grow gap-4 p-8",
        )

    def toast_container():
        return fh.Div(id="toast-container", cls="hidden")

    def footer():
        return fh.Footer(
            fh.Div(
                balance_view(),
                fh.P(
                    fh.A("Buy 50 more", href="/buy_global", cls="font-bold text-blue-300 hover:text-blue-100"),
                    " to share ($1)",
                ),
                cls="flex flex-col gap-0.5",
            ),
            fh.Div(
                fh.P("Made by"),
                fh.A(
                    "Andrew Hinh",
                    href="https://andrewhinh.github.io/",
                    cls="font-bold text-blue-300 hover:text-blue-100",
                ),
                cls="flex flex-col text-right gap-0.5",
            ),
            cls="flex justify-between items-center p-4 text-sm md:text-lg",
        )

    # helper fns
    ## validation
    def validate_image_url(image_url: str) -> bool:
        return validators.url(image_url)

    def validate_image_file(image_file: fh.UploadFile = None, upload_path: Path = None) -> str | Path:
        if image_file is not None:
            # Ensure extension is valid image
            valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
            file_extension = Path(image_file.filename).suffix.lower()
            if file_extension not in valid_extensions:
                return "Invalid file type. Please upload an image."

            # Write file to disk
            filebuffer = image_file.file.read()
            upload_path = upload_dir / f"{uuid.uuid4()}{file_extension}"
            upload_path.write_bytes(filebuffer)

        # Verify upload path
        if not upload_path.exists():
            return "Error: File not found."

        # Verify MIME type and magic #
        img = Image.open(upload_path)
        try:
            img.verify()
        except Exception as e:
            os.remove(upload_path)
            return f"Error: {e}"

        # Limit img size
        MAX_FILE_SIZE_MB = 5
        MAX_DIMENSIONS = (4096, 4096)
        if os.path.getsize(upload_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
            os.remove(upload_path)
            return f"File size exceeds {MAX_FILE_SIZE_MB}MB limit."
        with Image.open(upload_path) as img:
            if img.size[0] > MAX_DIMENSIONS[0] or img.size[1] > MAX_DIMENSIONS[1]:
                os.remove(upload_path)
                return f"Image dimensions exceed {MAX_DIMENSIONS[0]}x{MAX_DIMENSIONS[1]} pixels limit."

        # Run antivirus
        try:
            result = subprocess.run(  # noqa: S603
                ["python", "main.py", str(upload_path)],  # noqa: S607
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd="/Python-Antivirus",
            )
            scan_result = result.stdout.strip().lower()
            if scan_result == "infected":
                os.remove(upload_path)
                return "Potential threat detected."
        except Exception as e:
            os.remove(upload_path)
            return f"Error during antivirus scan: {e}"

        return upload_path

    ## generation
    @fh.threaded
    def generate_and_save(
        g: Gen,
        session,
    ):
        k = ApiKeyCreate(session_id=session["session_id"])
        k = generate_key_and_save(k)

        # TODO: uncomment for debugging
        # g.response = "temp"
        # with get_db_session() as db_session:
        #     db_session.add(g)
        #     db_session.commit()
        #     db_session.refresh(g)
        #     return

        # TODO: uncomment for debugging
        # g.failed = True
        # with get_db_session() as db_session:
        #     db_session.add(g)
        #     db_session.commit()
        #     db_session.refresh(g)
        #     return

        if g.image_url:
            response = requests.post(
                os.getenv("API_URL"),
                json={"image_url": g.image_url},
                headers={"X-API-Key": k.key},
            )
        elif g.image_file:
            response = requests.post(
                f"{os.getenv('API_URL')}/upload",
                files={"image": open(g.image_file, "rb")},
                headers={
                    "X-API-Key": k.key,
                },
            )

        if not response.ok:
            fh.add_toast(session, "Failed with status code: " + str(response.status_code), "error")
            g.failed = True
        else:
            g.response = response.json()
        with get_db_session() as db_session:
            db_session.add(g)
            db_session.commit()
            db_session.refresh(g)

    def generate_key_and_save(
        k: ApiKeyCreate,
    ) -> ApiKey:
        k.key = secrets.token_hex(32)
        k = ApiKey.model_validate(k)
        with get_db_session() as db_session:
            db_session.add(k)
            db_session.commit()
            db_session.refresh(k)
        return k

    ## SSE helpers
    async def stream_gen_updates(
        session,
        id: int,
    ):
        while not shutdown_event.is_set():
            curr_gen = get_curr_gens(session["session_id"], ids=[id])[0]
            curr_state = "response" if curr_gen.response else "failed" if curr_gen.failed else "loading"
            global shown_generations
            if shown_generations.get(id) != curr_state:
                shown_generations[id] = curr_state
                yield f"""event: UpdateGens\ndata: {fh.to_xml(
                    fh.P(
                        "Scanning image ...",
                        sse_swap="UpdateGens",
                    ) if curr_state == "loading" else
                    fh.P(
                        curr_gen.response[:limit_chars] + ("..." if len(curr_gen.response) > limit_chars else ""),
                        onclick=f"navigator.clipboard.writeText('{curr_gen.response.replace(chr(92), chr(92)*2)}');",
                        hx_post="/toast?message=Copied to clipboard!&type=success",
                        hx_indicator="#spinner",
                        hx_target="#toast-container",
                        hx_swap="outerHTML",
                        cls="text-blue-300 hover:text-blue-100 cursor-pointer max-w-full",
                        title="Click to copy",
                        sse_swap="UpdateGens",
                    ) if curr_state == "response" else
                    fh.P(
                        "Generation failed",
                        cls="text-red-300",
                        sse_swap="UpdateGens",
                    ))}\n\n"""
            await sleep(1)

    async def stream_balance_updates():
        while not shutdown_event.is_set():
            curr_balance = get_curr_balance().balance
            global shown_balance
            if shown_balance != curr_balance:
                shown_balance = curr_balance
                yield f"""event: UpdateBalance\ndata: {fh.to_xml(fh.P(f"{shown_balance} credits", cls="font-bold", sse_swap="UpdateBalance"))}\n\n"""
            await sleep(1)

    ## pagination
    def get_gen_table_part(session, part_num: int = 1, size: int = max_gens):
        curr_gens = get_curr_gens(session["session_id"], number=size, offset=(part_num - 1) * size)
        read_gens = [GenRead.model_validate(g) for g in curr_gens]
        paginated = [gen_view(g, session) for g in read_gens]
        return tuple(paginated)

    def get_key_table_part(session, part_num: int = 1, size: int = max_keys):
        curr_keys = get_curr_keys(session["session_id"], number=size, offset=(part_num - 1) * size)
        read_keys = [ApiKeyRead.model_validate(k) for k in curr_keys]
        paginated = [key_view(k, session) for k in read_keys]
        return tuple(paginated)

    # routes
    ## for images, CSS, etc.
    @f_app.get("/{fname:path}.{ext:static}")
    def static_files(fname: str, ext: str):
        static_file_path = FE_PATH / f"{fname}.{ext}"
        if static_file_path.exists():
            return fh.FileResponse(static_file_path)

    ## toasts without target
    @f_app.post("/toast")
    def toast(session, message: str, type: str):
        fh.add_toast(session, message, type)
        return toast_container()

    ## pages
    @f_app.get("/")
    def home(
        session,
    ):
        return (
            fh.Title(NAME),
            fh.Div(
                nav(),
                main_content(session),
                toast_container(),
                footer(),
                cls="flex flex-col justify-between min-h-screen text-slate-100 bg-zinc-900 w-full",
            ),
            fh.Script(
                """
                document.addEventListener('htmx:beforeRequest', (event) => {
                    if (event.target.id === 'export-gens-csv') {
                        event.preventDefault();
                        window.location.href = "/export-gens";
                    }
                });
            """
            ),
        )

    @f_app.get("/developer")
    def developer(
        session,
    ):
        return (
            fh.Title(NAME + " | " + "developer"),
            fh.Div(
                nav(),
                developer_page(session),
                toast_container(),
                footer(),
                cls="flex flex-col justify-between min-h-screen text-slate-100 bg-zinc-900 w-full",
            ),
            fh.Script(
                """
                document.addEventListener('htmx:beforeRequest', (event) => {
                    if (event.target.id === 'export-keys-csv') {
                        event.preventDefault();
                        window.location.href = "/export-keys";
                    }
                });
            """
            ),
        )

    @f_app.get("/stream-gens/{id}")
    async def stream_gens(session, id: int):
        """Stream generation updates to connected clients"""
        return StreamingResponse(stream_gen_updates(session, id), media_type="text/event-stream")

    @f_app.get("/stream-balance")
    async def stream_balance():
        """Stream balance updates to connected clients"""
        return StreamingResponse(stream_balance_updates(), media_type="text/event-stream")

    ## gen form view
    @f_app.get("/get-gen-form")
    def get_gen_form(session, view: str):
        session["gen_form"] = view
        return (
            (
                fh.Form(
                    fh.Input(
                        id="new-image-url",
                        name="image_url",  # passed to fn call for python syntax
                        placeholder="Enter an image url",
                        hx_target="this",
                        hx_swap="outerHTML",
                        hx_trigger="change, keyup delay:200ms changed",
                        hx_post="/check-url",
                        hx_indicator="#spinner",
                    ),
                    fh.Button(
                        "Scan",
                        type="submit",
                        cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100",
                    ),
                    hx_post="/url",
                    hx_indicator="#spinner",
                    hx_target="#gen-list",
                    hx_swap="afterbegin",
                    id="gen-form",
                    cls="flex flex-col md:gap-2 w-full h-full",
                )
                if view == "image-url"
                else fh.Form(
                    fh.Input(
                        id="new-image-upload",
                        name="image_file",
                        type="file",
                        accept="image/*",
                        hx_target="this",
                        hx_swap="none",
                        hx_trigger="change delay:200ms changed",
                        hx_post="/check-upload",
                        hx_indicator="#spinner",
                        hx_encoding="multipart/form-data",  # correct file encoding for check-upload since not in form
                    ),
                    fh.Button(
                        "Scan",
                        type="submit",
                        cls="text-blue-300 hover:text-blue-100 p-2 border-blue-300 border-2 hover:border-blue-100",
                    ),
                    hx_post="/upload",
                    hx_indicator="#spinner",
                    hx_target="#gen-list",
                    hx_swap="afterbegin",
                    id="gen-form",
                    cls="flex flex-col gap-4 w-full h-full",
                ),
            ),
            gen_form_toggle(view, "true"),
        )

    ## input validation
    @f_app.post("/check-url")
    def check_url(session, image_url: str):
        if not validate_image_url(image_url):
            fh.add_toast(session, "Invalid image URL", "error")
        return (
            fh.Input(
                value=image_url,
                id="new-image-url",
                name="image_url",
                placeholder="Enter an image url",
                hx_target="this",
                hx_swap="outerHTML",
                hx_trigger="change, keyup delay:200ms changed",
                hx_post="/check-url",
            ),
        )

    @f_app.post("/check-upload")
    def check_upload(
        session,
        image_file: fh.UploadFile,
    ):
        res = validate_image_file(image_file)
        if isinstance(res, str):
            fh.add_toast(session, res, "error")
        return fh.Div(cls="hidden")

    ## pagination
    @f_app.get("/page-gens")
    def page_gens(session, idx: int):
        return get_gen_table_part(session, idx), gen_load_more(
            bool(get_curr_gens(session["session_id"], number=1)),
            len(get_curr_gens(session["session_id"], number=max_gens, offset=max_gens * (idx + 1))) > 0,
            idx + 1,
            "true",
        )

    @f_app.get("/page-keys")
    def page_keys(session, idx: int):
        return get_key_table_part(session, idx), key_load_more(
            bool(get_curr_keys(session["session_id"], number=1)),
            len(get_curr_keys(session["session_id"], number=max_keys, offset=max_keys * (idx + 1))) > 0,
            idx + 1,
            "true",
        )

    ## generation routes
    @f_app.post("/url")
    def generate_from_url(
        session,
        image_url: str,
    ):
        # validation
        if not image_url:
            fh.add_toast(session, "No image URL provided", "error")
            return None
        if not validate_image_url(image_url):
            fh.add_toast(session, "Invalid image URL", "error")
            return None

        # Warn if we're out of balance
        curr_balance = get_curr_balance()
        if curr_balance.balance < 1:
            fh.add_toast(session, "Out of balance!", "error")
            return None

        # Decrement balance
        curr_balance.balance -= 1
        with get_db_session() as db_session:
            db_session.add(curr_balance)
            db_session.commit()
            db_session.refresh(curr_balance)

        # Clear input
        clear_img_input = fh.Input(
            id="new-image-url", name="image_url", placeholder="Enter an image url", hx_swap_oob="true"
        )

        # Generate as before
        g = GenCreate(
            image_url=image_url,
            session_id=session["session_id"],
        )
        ## need to put in db since generate_and_save is threaded
        g = Gen.model_validate(g)
        with get_db_session() as db_session:
            db_session.add(g)
            db_session.commit()
            db_session.refresh(g)
        global shown_generations
        shown_generations[g.id] = "loading"
        generate_and_save(g, session)
        g_read = GenRead.model_validate(g)
        gens_present = bool(get_curr_gens(session["session_id"], number=1))
        return (
            gen_view(g_read, session),
            clear_img_input,
            num_gens(len(get_curr_gens(session["session_id"])), "true"),
            gen_manage(gens_present, False, "true"),
            gen_load_more(
                gens_present,
                False,
                hx_swap_oob="true",
            ),
        )

    @f_app.post("/upload")
    def generate_from_upload(
        session,
        image_file: fh.UploadFile,
    ):
        if not image_file:
            fh.add_toast(session, "No image uploaded", "error")
            return None
        res = validate_image_file(image_file)
        if isinstance(res, str):
            fh.add_toast(session, res, "error")
            return None
        else:
            upload_path = res
        curr_balance = get_curr_balance()
        if curr_balance.balance < 1:
            fh.add_toast(session, "Out of balance!", "error")
            return None

        curr_balance.balance -= 1
        with get_db_session() as db_session:
            db_session.add(curr_balance)
            db_session.commit()
            db_session.refresh(curr_balance)

        # Clear input
        clear_img_input = fh.Input(
            id="new-image-upload", name="image_file", type="file", accept="image/*", hx_swap_oob="true"
        )

        # Generate as before
        g = GenCreate(
            image_file=str(upload_path),
            session_id=session["session_id"],
        )
        ## need to put in db since generate_and_save is threaded
        g = Gen.model_validate(g)
        with get_db_session() as db_session:
            db_session.add(g)
            db_session.commit()
            db_session.refresh(g)
        global shown_generations
        shown_generations[g.id] = "loading"
        generate_and_save(g, session)
        g_read = GenRead.model_validate(g)
        gens_present = bool(get_curr_gens(session["session_id"], number=1))
        return (
            gen_view(g_read, session),
            clear_img_input,
            num_gens(len(get_curr_gens(session["session_id"])), "true"),
            gen_manage(gens_present, False, "true"),
            gen_load_more(
                gens_present,
                False,
                hx_swap_oob="true",
            ),
        )

    ## api key request
    @f_app.post("/request-key")
    def generate_key(
        session,
    ):
        k = ApiKeyCreate(session_id=session["session_id"])
        k = generate_key_and_save(k)
        k_read = ApiKeyRead.model_validate(k)
        global shown_keys
        shown_keys.append(k.id)
        keys_present = bool(get_curr_keys(session["session_id"], number=1))
        return (
            key_view(k_read, session),
            num_keys(len(get_curr_keys(session["session_id"])), "true"),
            key_manage(
                keys_present,
                False,
                "true",
            ),
            key_load_more(
                keys_present,
                False,
                hx_swap_oob="true",
            ),
        )

    ## delete
    @f_app.delete("/gens")
    def delete_gens(
        session,
    ):
        gens = get_curr_gens(session["session_id"])
        global shown_generations
        for g in gens:
            if g and g.image_file and os.path.exists(g.image_file):
                os.remove(g.image_file)
            with get_db_session() as db_session:
                db_session.delete(g)
                db_session.commit()
                if not modal.is_local():
                    VOLUME_CONFIG[f"{DB_VOL_PATH}"].commit()
            shown_generations.pop(g.id, None)
        fh.add_toast(session, "Deleted generations.", "success")
        return (
            "",
            num_gens(len(get_curr_gens(session["session_id"])), "true"),
            gen_manage(
                bool(get_curr_gens(session["session_id"], number=1)),
                False,
                "true",
            ),
            gen_load_more(
                bool(get_curr_gens(session["session_id"], number=1)),
                False,
                hx_swap_oob="true",
            ),
        )

    @f_app.delete("/keys")
    def delete_keys(session):
        keys = get_curr_keys(session["session_id"])
        global shown_keys
        for k in keys:
            with get_db_session() as db_session:
                db_session.delete(k)
                db_session.commit()
            shown_keys = [key for key in shown_keys if key != k.id]
        fh.add_toast(session, "Deleted keys.", "success")
        return (
            "",
            num_keys(len(get_curr_keys(session["session_id"])), "true"),
            key_manage(
                bool(get_curr_keys(session["session_id"], number=1)),
                False,
                "true",
            ),
            key_load_more(
                bool(get_curr_keys(session["session_id"], number=1)),
                False,
                hx_swap_oob="true",
            ),
        )

    @f_app.delete("/gens/select")
    def delete_select_gens(session, selected_gens: list[int] = None):
        if selected_gens:
            global shown_generations
            select_gens = get_curr_gens(session["session_id"], ids=selected_gens)
            with get_db_session() as db_session:
                for g in select_gens:
                    if g and g.image_file and os.path.exists(g.image_file):
                        os.remove(g.image_file)
                    db_session.delete(g)
                    db_session.commit()
                    if not modal.is_local():
                        VOLUME_CONFIG[f"{DB_VOL_PATH}"].commit()
                    shown_generations.pop(g.id, None)
            fh.add_toast(session, "Deleted generations.", "success")
            gens_present = bool(get_curr_gens(session["session_id"], number=1))
            remain_gens = get_curr_gens(session["session_id"], ids=list(shown_generations.keys()))
            remain_view = [gen_view(GenRead.model_validate(g), session) for g in remain_gens[::-1]]
            return (
                remain_view,
                num_gens(len(get_curr_gens(session["session_id"])), "true"),
                gen_manage(
                    gens_present,
                    False,
                    "true",
                ),
                gen_load_more(
                    gens_present,
                    False,
                    hx_swap_oob="true",
                ),
            )
        else:
            fh.add_toast(session, "No generations selected.", "warning")
            return fh.Response(status_code=204)

    @f_app.delete("/keys/select")
    def delete_select_keys(session, selected_keys: list[int] = None):
        if selected_keys:
            global shown_keys
            select_keys = get_curr_keys(session["session_id"], ids=selected_keys)
            with get_db_session() as db_session:
                for k in select_keys:
                    db_session.delete(k)
                    db_session.commit()
                    shown_keys = [key for key in shown_keys if key != k.id]
            fh.add_toast(session, "Deleted keys.", "success")
            keys_present = bool(get_curr_keys(session["session_id"], number=1))
            remain_keys = get_curr_keys(session["session_id"], ids=list(shown_keys))
            remain_view = [key_view(ApiKeyRead.model_validate(k), session) for k in remain_keys[::-1]]
            return (
                remain_view,
                num_keys(len(get_curr_keys(session["session_id"])), "true"),
                key_manage(
                    keys_present,
                    False,
                    "true",
                ),
                key_load_more(
                    keys_present,
                    False,
                    hx_swap_oob="true",
                ),
            )
        else:
            fh.add_toast(session, "No keys selected.", "warning")
            return fh.Response(status_code=204)

    @f_app.post("/show-select-gen-delete")
    def show_select_gen_delete(session, selected_gens: list[int] = None):
        return gen_manage(bool(get_curr_gens(session["session_id"], number=1)), selected_gens is not None)

    @f_app.post("/show-select-key-delete")
    def show_select_key_delete(session, selected_keys: list[int] = None):
        return key_manage(bool(get_curr_keys(session["session_id"], number=1)), selected_keys is not None)

    @f_app.delete("/gen/{gen_id}")
    def delete_gen(
        session,
        gen_id: int,
    ):
        with get_db_session() as db_session:
            gen = db_session.get(Gen, gen_id)
            if gen and gen.image_file and os.path.exists(gen.image_file):
                os.remove(gen.image_file)
            db_session.delete(gen)
            db_session.commit()
            if not modal.is_local():
                VOLUME_CONFIG[f"{DB_VOL_PATH}"].commit()
        global shown_generations
        shown_generations.pop(gen_id, None)
        fh.add_toast(session, "Deleted generation.", "success")
        gens_present = bool(get_curr_gens(session["session_id"], number=1))
        return (
            "",
            num_gens(len(get_curr_gens(session["session_id"])), "true"),
            gen_manage(
                gens_present,
                False,
                "true",
            ),
            gen_load_more(
                gens_present,
                False,
                hx_swap_oob="true",
            ),
        )

    @f_app.delete("/key/{key_id}")
    def delete_key(
        session,
        key_id: int,
    ):
        with get_db_session() as db_session:
            key = db_session.get(ApiKey, key_id)
            db_session.delete(key)
            db_session.commit()
        global shown_keys
        shown_keys = [key for key in shown_keys if key != key_id]
        fh.add_toast(session, "Deleted key.", "success")
        keys_present = bool(get_curr_keys(session["session_id"], number=1))
        return (
            "",
            num_keys(len(get_curr_keys(session["session_id"])), "true"),
            key_manage(
                keys_present,
                False,
                "true",
            ),
            key_load_more(
                keys_present,
                False,
                hx_swap_oob="true",
            ),
        )

    ## export to CSV
    @f_app.get("/export-gens")
    def export_gens(
        req,
    ):
        session = req.session
        curr_gens = get_curr_gens(session["session_id"])
        if not curr_gens:
            return fh.Response(status_code=204)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["request_at", "image_url", "image_file", "response", "failed"])
        for g in curr_gens:
            writer.writerow([g.request_at, g.image_url, Path(g.image_file).name, g.response, g.failed])

        output.seek(0)
        response = fh.Response(
            output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=gens.csv"}
        )
        return response

    @f_app.get("/export-keys")
    def export_keys(
        req,
    ):
        session = req.session
        curr_keys = get_curr_keys(session["session_id"])
        if not curr_keys:
            return fh.Response(status_code=204)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["key", "granted_at"])
        for k in curr_keys:
            writer.writerow([k.key, k.granted_at])

        output.seek(0)
        response = fh.Response(
            output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=keys.csv"}
        )
        return response

    ## stripe
    ### send the user here to buy credits
    @f_app.get("/buy_global")
    def buy_credits():
        s = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": 100,
                        "product_data": {
                            "name": "Buy 50 credits for $1 (to share)",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=DOMAIN + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=DOMAIN + "/cancel",
        )
        ### send the USER to STRIPE
        return fh.RedirectResponse(s["url"])

    ### STRIPE sends the USER here after a payment was canceled.
    @f_app.get("/cancel")
    def cancel():
        return fh.RedirectResponse("/")

    ### STRIPE sends the USER here after a payment was 'successful'.
    @f_app.get("/success")
    def success():
        return fh.RedirectResponse("/")

    ### STRIPE calls this to tell APP when a payment was completed.
    @f_app.post("/webhook")
    async def stripe_webhook(
        request,
    ):
        # print(request)
        # print("Received webhook")
        payload = await request.body()
        payload = payload.decode("utf-8")
        signature = request.headers.get("stripe-signature")
        # print(payload)

        # verify the Stripe webhook signature
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
        except ValueError:
            # print("Invalid payload")
            return {"error": "Invalid payload"}, 400
        except stripe.error.SignatureVerificationError:
            # print("Invalid signature")
            return {"error": "Invalid signature"}, 400

        # handle the event
        if event["type"] == "checkout.session.completed":
            # session = event["data"]["object"]
            # print("Session completed", session)
            curr_balance = get_curr_balance()
            curr_balance.balance += 50
            with get_db_session() as db_session:
                db_session.add(curr_balance)
                db_session.commit()
                db_session.refresh(curr_balance)
            return {"status": "success"}, 200

    return f_app


load_dotenv(".env" if IN_PROD else ".env.dev")
f_app = get_app()

# -----------------------------------------------------------------------------

# Modal
IMAGE = (
    modal.Image.debian_slim(python_version=PYTHON_VERSION)
    .apt_install("git")
    .run_commands(["git clone https://github.com/Len-Stevens/Python-Antivirus.git"])
    .apt_install("libpq-dev")  # for psycopg2
    .pip_install(  # add Python dependencies
        "python-fasthtml==0.6.10",
        "sqlite-minutils==4.0.3",  # needed for fasthtml
        "simpleicons==7.21.0",
        "requests==2.32.3",
        "stripe==11.1.0",
        "validators==0.34.0",
        "pillow==11.0.0",
        "sqlmodel==0.0.22",
        "psycopg2==2.9.10",
    )
    .copy_local_file(FE_PATH / "favicon.ico", "/root/favicon.ico")
    .copy_local_dir(PARENT_PATH / "db", "/root/db")
)

FE_TIMEOUT = 5 * MINUTES  # max
FE_CONTAINER_IDLE_TIMEOUT = 15 * MINUTES  # max
FE_ALLOW_CONCURRENT_INPUTS = 1000  # max


APP_NAME = f"{NAME}-frontend"
app = modal.App(APP_NAME)

# -----------------------------------------------------------------------------


@app.function(
    image=IMAGE,
    volumes=VOLUME_CONFIG,
    secrets=SECRETS,
    timeout=FE_TIMEOUT,
    container_idle_timeout=FE_CONTAINER_IDLE_TIMEOUT,
    allow_concurrent_inputs=FE_ALLOW_CONCURRENT_INPUTS,
)
@modal.asgi_app()
def modal_get():
    return f_app


if __name__ == "__main__":
    fh.serve(app="f_app")


# TODO:
# - add multiple file urls/uploads: https://docs.fastht.ml/tutorials/quickstart_for_web_devs.html#multiple-file-uploads
# - add user authentication:
#   - save gens and keys to user account
#   - complete file upload security: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
#       - Only allow authorized users to upload files: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
