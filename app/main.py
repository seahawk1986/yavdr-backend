#!/usr/bin/env python3
import asyncio
import json
import socket
import sys
import time

from threading import Thread, Condition, Lock

import asgiref.sync
import pydbus
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from routers import auth, system, lircd2uinput, vdr, log
from tools import state, systeminfo
from tools.sse import SSE_StreamingResponse

# for production: think about locking down the docs:
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app = FastAPI()

# collect system stats continously
systemstat_collector = systeminfo.SystemStatHistory()


@app.on_event("startup")
async def system_info_tasks():
    asyncio.create_task(systemstat_collector.run_update())


# TODO: do we want to limit this explicitly?
# hostname = socket.gethostname()
# ip = socket.gethostbyname(hostname)
# origins = [
#     f"http://{hostname}:8080",
#     f"http://{ip}:8080",
#     "http://192.168.1.167:8080", # TODO: remove, this is a hack while the site is not delivered by fastapi or a webserver
#     "http://192.168.1.50:8080", # TODO: remove, this is a hack while the site is not delivered by fastapi or a webserver
#     "http://192.168.1.51:8080", # TODO: remove, this is a hack while the site is not delivered by fastapi or a webserver
#     "http://localhost",
#     "http://localhost:8080",
# ]

# print(origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # origins,  # TODO: see if origin limitations set above are needed
    allow_credentials=False,  # we don't need no cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """This method redirects to the openapi page of this app"""
    return RedirectResponse(url="/docs")


# mount the static ressources
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# DBus callbacks
bus = pydbus.SessionBus()
loop_control = {"stop_loops": False}
condition = Condition()
queue_lock = Lock()

active_clients = []


async def send_messages2clients(data) -> None:
    if data is None:
        pass
    for client in active_clients[:]:
        # print("adding data to client queue", client)
        client.messages.put_nowait(data)


def on_message(*args) -> None:
    data = args[4][0]
    data["server_ts"] = time.time()
    # print("on_message:", data)
    data = f"data: {json.dumps(data)}\n\n".encode()
    asgiref.sync.async_to_sync(send_messages2clients)(data)


def process_signals() -> None:
    bus.subscribe(object="/org/yavdr/backend/ansible", signal_fired=on_message)
    try:
        print("running loop")
        state.glib_loop.run()
    except Exception as err:
        print("quitting loop:", err, file=sys.stderr)
        state.glib_loop.quit()


@app.get("/run/messages", response_class=SSE_StreamingResponse)
async def stream_messages():
    global active_clients
    return SSE_StreamingResponse(active_clients, media_type="text/event-stream")


@app.on_event("startup")
async def startup_event():
    print("callback for fastapi startup event")
    t = Thread(target=process_signals)
    t.start()


@app.on_event("shutdown")
def shutdown_event():
    print("callback for fastapi shutdown event")
    # the other thread needs to be stopped when the application shuts down
    # so we stop the glib Mainloop
    state.glib_loop.quit()


@app.get("/system/status", response_model=systeminfo.SystemData)
def system_info():
    """
    Returns a json object containing system status information
    """
    return systeminfo.collect_data()
    return systemstat_collector.data()


# include the routes defined in other modules
app.include_router(auth.router)
app.include_router(system.router)
app.include_router(lircd2uinput.router)
app.include_router(vdr.router)
app.include_router(log.router)


# catch all redirect
@app.route("/static/{}")
async def default_redirect(*args, **kwargs):
    url = app.url_path_for("static")
    response = RedirectResponse(url=url)
    return response
