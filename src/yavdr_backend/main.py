#!/usr/bin/env python3
import asyncio
from collections.abc import Awaitable, Callable, Generator
import logging
from threading import Condition, Lock
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
from httpx import AsyncClient, Timeout
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from yavdr_backend.routers import auth, system, lircd2uinput, vdr, log, audio, channelpedia
from yavdr_backend.tools import systeminfo
from yavdr_backend.tools.sse import SSE_StreamingResponse

load_dotenv()  # take environment variables from .env.
timeout = Timeout(10.0, connect=5.0)

@asynccontextmanager
async def lifespan_handler(app: FastAPI) -> AsyncGenerator[None, None]:
    # see https://fastapi.tiangolo.com/advanced/events/#lifespan
    print("callback on startup")
    # Initialize a shared HTTP/2 client for the application
    app.state.http_client = AsyncClient(http2=True, timeout=timeout) # TODO: check if this requires a more advanced proxy setting in nginx
    t = asyncio.create_task(systemstat_collector.run_update())
    yield
    print("shutdown of the fastapi app")
    t.cancel()
    await app.state.http_client.aclose()



# NOTE: for production: think about locking down the docs:
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI(lifespan=lifespan_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content: dict[str, Any] = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# tell the client not to cache repeated GET requests by default
@app.middleware("http")
async def disable_cache(request: Request, call_next: Callable[..., Awaitable[Response]]) -> Response:
    response: Response = await call_next(request)

    if request.method == "GET":
        response.headers.setdefault("Cache-Control", "no-store")

    return response

# collect system stats continously
systemstat_collector = systeminfo.SystemStatHistory()


# TODO: check if we need this with an nginx proxy
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "*",
#     ],  # origins,  # TODO: see if origin limitations set above are needed
#     allow_credentials=False,  # we don't need no cookies
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """This method redirects to the openapi page of this app"""
    return RedirectResponse(url="/docs")


# mount the static ressources
app.mount("/static", StaticFiles(directory="assets/static", html=True), name="static")

loop_control = {"stop_loops": False}
condition = Condition()
queue_lock = Lock()

active_clients: list[SSE_StreamingResponse] = []


async def send_messages2clients(data: None|str) -> None:
    if data is None:
        pass
    for client in active_clients[:]:
        # print("adding data to client queue", client)
        client.messages.put_nowait(data)


# def on_message(*args) -> None:
#     data = args[4][0]
#     data["server_ts"] = time.time()
#     # print("on_message:", data)
#     data = f"data: {json.dumps(data)}\n\n".encode()
#     asgiref.sync.async_to_sync(send_messages2clients)(data)


# def process_signals() -> None:
#     bus.subscribe(object="/org/yavdr/backend/ansible", signal_fired=on_message)
#     try:
#         print("running loop")
#         state.glib_loop.run()
#     except Exception as err:
#         print("quitting loop:", err, file=sys.stderr)
#         state.glib_loop.quit()


async def process_signals() -> None: ...


@app.get("/run/messages", response_class=SSE_StreamingResponse)
async def stream_messages() -> SSE_StreamingResponse:
    global active_clients
    return SSE_StreamingResponse(active_clients, media_type="text/event-stream")


@app.get("/system/status", response_model=systeminfo.SystemData)
def system_info():
    """
    Returns a json object containing system status information
    """
    return systeminfo.collect_data()
    # return systemstat_collector.data()


# include the routes defined in other modules
app.include_router(auth.router)
app.include_router(system.router)
app.include_router(lircd2uinput.router)
app.include_router(vdr.router)
app.include_router(log.router)
app.include_router(audio.router)
app.include_router(channelpedia.router)


# TODO: why is this needed again?
# catch all redirect
@app.route("/static/{}")
async def default_redirect(*args, **kwargs) -> RedirectResponse:
    url = app.url_path_for("static")
    response = RedirectResponse(url=url)
    return response