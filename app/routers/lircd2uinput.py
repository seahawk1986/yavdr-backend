import time
from functools import wraps
from typing import List

import pydbus
from fastapi import APIRouter, Depends, HTTPException
from gi.repository import GLib
from pydantic import BaseModel, ValidationError
from starlette.responses import JSONResponse, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from tools.dbus import pydbus_error_handler

router = APIRouter()
system_bus = pydbus.SystemBus()


class Key(BaseModel):
    key: str


class Keys(BaseModel):
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
def hitkey(*, key: Key):
    try:
        key = key.key
        if key:
            key = key.upper()
            lircd2uinput = system_bus.get("de.yavdr.lircd2uinput", "/control")
            success, key_code = lircd2uinput.emit_key(key)
        else:
            success = False
            key_code = None
    except GLib.Error:
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
def hitkeys(*, keys: Keys):
    try:
        keys = keys.keys
        if keys:
            for key in keys:
                key = key.upper()
                lircd2uinput = system_bus.get("de.yavdr.lircd2uinput", "/control")
                success, key_code = lircd2uinput.emit_key(key)
                if not success:
                    break
                time.sleep(0.1)
        else:
            success = False
            key_code = None
    except GLib.Error:
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
