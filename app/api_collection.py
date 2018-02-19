import time
import pydbus        
from gi.repository import GLib
from flask import request
from flask_restful import Resource
import system_utils.usage as sys_usage
import system_utils.dbus as dbus_tools
from . import auth as pam_auth

system_bus = pydbus.SystemBus()

class SystemInfo(Resource):
    def get(self):
        return sys_usage.collect_data(), 200

class SystemAction(Resource):
    def post(self, action_name):
        try:
            backend = system_bus.get('de.yavdr.backend')
            data = request.get_json()
            if data is None:
                data = {}
            elif not isinstance(data, dict):
                return {'msg': 'you must pass a json object ("{}")' }, 402

            data = { key: dbus_tools.av(value) for key, value in data.items()}
            print(data)
            r_code, r_msg = backend.queue_action(action_name, data)
            if r_code == 200:
                return {'msg': 'action queued', 'job_id': r_msg }, r_code
            else:
                return {'msg': 'action rejected: {}'.format(r_msg)}, r_code
        except GLib.Error:
            return {'msg': 'yavdr-backend is not available'}, 503

class JobStatus(Resource):
    def get(self, job_id):
        try:
            backend = system_bus.get('de.yavdr.backend')
            response = backend.jobStatus(job_id)
            return {'msg': 'job is {}'.format(job_str),
                    'is_running': job_is_running,
                    'is_cancelled': 'job_is_cancelled',
                    'is_done': job_is_done,
            }, 200
        except GLib.Error:
            return {'msg': 'yavdr-backend is not available'}, 503


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
