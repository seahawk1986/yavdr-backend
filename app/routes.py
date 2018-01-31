from app import app, api
from flask import render_template, request
from flask_restful import Resource, Api
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

import system_utils.pam as pam
import system_utils.usage as sys_usage
from . import auth
from . import api_collection as api_col
from . import vdr

import pydbus

# RESTful API
api.add_resource(api_col.SystemInfo, '/api/system/status')
api.add_resource(vdr.VDR_Recordings, '/api/vdr/recordings')
api.add_resource(vdr.VDR_Plugins, '/api/vdr/plugins')
api.add_resource(vdr.VDR_Timers, '/api/vdr/timers')
api.add_resource(vdr.VDR_Channels, '/api/vdr/channels')

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'alexander'}
    return render_template('index.html', title='Home', user=user)


@app.route('/login')
def login():
    return render_template('login.html', title='Login')

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

