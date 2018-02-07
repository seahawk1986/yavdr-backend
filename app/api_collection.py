import time
import pydbus        
from gi.repository import GLib
from flask import request
from flask_restful import Resource
import system_utils.usage as sys_usage
from . import auth as pam_auth

class SystemInfo(Resource):
    def get(self):
        return sys_usage.collect_data()

class VDR_Status(Resource):
    def get(self):
        return {
                'Recordings': [],
                'Timer': [],
                'Status': 'Ready',
                }

class HitKey(Resource):
    @pam_auth.login_required
    def post(self):
        try:
            json_data = request.get_json()
            if json_data:
                key = json_data.get('key')
                if key is not None:
                    key = key.upper()
                    bus = pydbus.SystemBus()
                    lircd2uinput = bus.get('de.yavdr.lircd2uinput', '/control')
                    success, key_code = lircd2uinput.emit_key(key)
                else:
                    success = False
                    key_code = None
        except GLib.Error:
            return {'msg': 'lircd2uinput is not available'}, 503
        if success:
            return {'msg': 'ok', 'key': key}, 200
        else:
            return {'msg': 'unknown key'}, 400

class HitKeys(Resource):
    @pam_auth.login_required
    def post(self):
        try:
            json_data = request.get_json()
            if json_data:
                keys = json_data.get('keys')
                if keys:
                    bus = pydbus.SystemBus()
                    lircd2uinput = bus.get('de.yavdr.lircd2uinput', '/control')
                    for key in keys:
                        key = key.upper()
                        success, key_code = lircd2uinput.emit_key(key)
                        if not success:
                            break
                        time.sleep(.1)
                else:
                    success = False
                    key_code = None
        except GLib.Error:
            return {'msg': 'lircd2uinput is not available'}, 503
        if success:
            return {'msg': 'ok', 'keys': keys}, 200
        else:
            return {'msg': 'unknown key: {}'.format(key)}, 400
