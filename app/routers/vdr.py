from functools import wraps
from fastapi import APIRouter, Depends, HTTPException

import pydbus2vdr
from gi.repository import GLib

from .auth import get_current_active_user, User

router = APIRouter()

vdr = None


def set_vdr(vdr):
    if vdr is None:
        try:
            vdr = pydbus2vdr.DBus2VDR()
        except GLib.Error:
            # Don't stop if vdr has no dbus interface
            vdr = None
            print("could not init pydbus2vdr.DBus2VDR :(")
    return vdr


def dbus_error_wrapper(f):
    global vdr
    vdr = set_vdr(vdr)

    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds)
        except (AttributeError, GLib.GError):
            raise HTTPException(status_code=503, detail="VDR did not respond")

    return wrapper


@router.get("/vdr/recordings")
@dbus_error_wrapper
def get_vdr_recordings(current_user: User = Depends(get_current_active_user)):
        recordings = []
        for n, r in vdr.Recordings.List():
            rec = dict([("RecNum", int(n)), *r])
            recordings.append(rec)
        return recordings


@router.get("/vdr/plugins")
@dbus_error_wrapper
def get_vdr_plugins(current_user: User = Depends(get_current_active_user)):
    return [p._asdict() for p in vdr.Plugins.list()]


@router.get("/vdr/timers")
@dbus_error_wrapper
def get_vdr_timers(current_user: User = Depends(get_current_active_user)):
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


@router.get("/vdr/channels")
@dbus_error_wrapper
def get_vdr_channels(current_user: User = Depends(get_current_active_user)):
    channels = []
    channels_raw, *_ = vdr.Channels.List()
    for channel in channels_raw:
        chan_num, chan_str = channel
        channels.append(
            {
                "channel_number": chan_num,
                "channel_string": chan_str,
            })
    return channels
