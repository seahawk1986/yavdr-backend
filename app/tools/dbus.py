import asyncio
import sys
from functools import wraps


import dbussy as dbus
from dbussy import DBUS
from gi.repository import GLib

from starlette.responses import JSONResponse, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)


def message_filter(connection, message, data):
    if message.type == DBUS.MESSAGE_TYPE_SIGNAL:
        sys.stdout.write(
            "%s.%s[%s](%s)\n"
            % (
                message.interface,
                message.member,
                repr(message.path),
                ", ".join(repr(arg) for arg in message.objects),
            )
        )
    # end if
    return DBUS.HANDLER_RESULT_HANDLED


# connecto to session bus
conn = dbus.Connection.bus_get(DBUS.BUS_SESSION, private=False)
loop = asyncio.get_running_loop()
conn.attach_asyncio(loop)

conn.add_filter(message_filter, None)
conn.bus_add_match("type=signal")


def pydbus_error_handler(name="service"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            try:
                return f(*args, **kwds)
            except GLib.Error:
                return JSONResponse(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    content={"msg": f"{name} is not available"},
                )

        return wrapper

    return decorator
