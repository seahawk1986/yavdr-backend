from app import app, api
from flask import render_template, request
from flask_restful import Resource, Api

import system_utils.usage as sys_usage
from . import api_collection as api_col
from . import vdr

import pydbus

api.add_resource(api_col.SystemInfo, '/api/usage')
api.add_resource(vdr.VDR_Recordings, '/api/vdr/recordings')
api.add_resource(vdr.VDR_Plugins, '/api/vdr/plugins')
api.add_resource(vdr.VDR_Timers, '/api/vdr/timers')
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'alexander'}
    return render_template('index.html', title='Home', user=user)

@app.route('/usage')
def usage():
    data = sys_usage.collect_data()
    return render_template('usage.html', title='System Information', data=data)

@app.route('/hitkey/<string:key>', methods=['POST'])
def hitkey(key):
    bus = pydbus.SystemBus()
    lircd2uinput = bus.get('de.yavdr.lircd2uinput', '/control')
    print(lircd2uinput.emit_key(key.upper()))
    return index()

