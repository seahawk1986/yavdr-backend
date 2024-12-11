import logging
import time
from typing import List

import sdbus
from fastapi import APIRouter, Depends
# from gi.repository import GLib
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from interfaces.lircd2uinput import DeYavdrLircd2uinputInterface
# from tools.dbus import pydbus_error_handler


router = APIRouter()
# system_bus = pydbus.SystemBus()
system_bus = sdbus.sd_bus_open_system()
_lird2uinput = DeYavdrLircd2uinputInterface.new_proxy(service_name='de.yavdr.lircd2uinput', object_path='/control', bus=system_bus)


class SingleKeyData(BaseModel):
    key: str


class MultipleKeyData(BaseModel):
    keys: List[str]


class Message(BaseModel):
    msg: str


@router.post(
    "/hitkey",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "Keypress has been sent successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid key"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "lircd2uinput service is not available",
        },
    },
)
async def hitkey(*, key_data: SingleKeyData):
    key = key_data.key
    try:
        if key:
            key = key.upper()
            # lircd2uinput = system_bus.get("de.yavdr.lircd2uinput", "/control")
            success, key_code = await _lird2uinput.emit_key(key)
        else:
            success = False
            # key_code = None
    except Exception as _err:
        logging.exception(f"could not send {key}")
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={"msg": "lircd2uinput is not available"},
        )
    if success:
        return JSONResponse(status_code=HTTP_200_OK, content={"msg": "ok", "key": key},)
    else:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST, content={"msg": "unknown key"},
        )


@router.post(
    "/hitkeys",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "Keypress has been sent successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid key"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "lircd2uinput service is not available",
        },
    },
)
async def hitkeys(*, keys: MultipleKeyData):
    key_list: List[str] = keys.keys
    try:
        if key_list:
            for key in key_list:
                key = key.upper()
                # lircd2uinput = system_bus.get("de.yavdr.lircd2uinput", "/control")
                success, key_code = await _lird2uinput.emit_key(key)
                if not success:
                    return JSONResponse(
                        status_code=HTTP_400_BAD_REQUEST, content={"msg": f"unknown key '{key}'"},
                    )
                time.sleep(0.1)
        else:
            success = False
    except Exception as err:
        logging.exception("could not send keypresses")
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={"msg": f"lircd2uinput is not available: {err}"},
        )
    else:
        return JSONResponse(status_code=HTTP_200_OK, content={"msg": "ok", "keys": keys},)

