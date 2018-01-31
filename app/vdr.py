from flask_restful import Resource
import pydbus2vdr
from gi.repository import GLib
from functools import wraps

vdr = pydbus2vdr.DBus2VDR()

def dbus_error_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds), 200
        except (AttributeError, GLib.GError): 
            return [], 503
    return wrapper

class VDR_Recordings(Resource):
    @dbus_error_wrapper
    def get(self):
        recordings = []
        for n, r in vdr.Recordings.List():
            rec = dict([('RecNum', int(n)), *r])
            recordings.append(rec)
        return recordings

class VDR_Plugins(Resource):
    @dbus_error_wrapper
    def get(self):
        return [p._asdict() for p in vdr.Plugins.list()]

class VDR_Timers(Resource):
    @dbus_error_wrapper
    def get(self):
        return vdr.Timers.List()

class VDR_Channels(Resource):
    @dbus_error_wrapper
    def get(self):
        channels = []
        channels_raw, *_ = vdr.Channels.List()
        for channel in channels_raw:
            chan_num, chan_str = channel
            channels.append(
                    {'channel_number': chan_num, 'channel_string': chan_str})
        return channels
