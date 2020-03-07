from fastapi import APIRouter, Depends

router = APIRouter()

from flask_restful import Resource
import pydbus2vdr
from gi.repository import GLib
from functools import wraps
from . import auth as pam_auth

try:
    vdr = pydbus2vdr.DBus2VDR()
except GLib.Error:
    # Don't stop if vdr has no dbus interface
    pass


def dbus_error_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds), 200
        except (AttributeError, GLib.GError):
            return [], 503

    return wrapper


class VDR_Recordings(Resource):
    @pam_auth.login_required
    @dbus_error_wrapper
    def get(self):
        recordings = []
        for n, r in vdr.Recordings.List():
            rec = dict([("RecNum", int(n)), *r])
            recordings.append(rec)
        return recordings


class VDR_Plugins(Resource):
    @pam_auth.login_required
    @dbus_error_wrapper
    def get(self):
        return [p._asdict() for p in vdr.Plugins.list()]


class VDR_Timers(Resource):
    @pam_auth.login_required
    @dbus_error_wrapper
    def get(self):
        timers = vdr.Timers.List()
        t_data = []
        for timer in timers:
            (
                status,
                channel,
                day,
                start,
                stop,
                priority,
                lifetime,
                filename,
                aux,
            ) = timer.split(":")
            t_data.append(
                {
                    "raw": timer,
                    "status": int(status),
                    "channel": channel,
                    "day": day,
                    "start": int(start),
                    "stop": int(stop),
                    "priority": int(priority),
                    "lifetime": int(lifetime),
                    "filename": filename,
                    "aux": aux,
                }
            )
        return t_data


class VDR_Channels(Resource):
    @pam_auth.login_required
    @dbus_error_wrapper
    def get(self):
        channels = []
        channels_raw, *_ = vdr.Channels.List()
        for channel in channels_raw:
            chan_num, chan_str = channel
            channels.append({"channel_number": chan_num, "channel_string": chan_str})
        return channels
