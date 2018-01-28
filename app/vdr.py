from flask_restful import Resource
import pydbus2vdr
from gi.repository import GLib
from functools import wraps

vdr = pydbus2vdr.DBus2VDR()

def dbus_error_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds)
        except (AttributeError, GLib.GError): 
            return []
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
