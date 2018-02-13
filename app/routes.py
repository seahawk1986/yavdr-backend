import os
from app import app, api
from flask import render_template, request, session, redirect, url_for, jsonify, send_from_directory
from flask_restful import Resource, Api
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from gi.repository import GLib

import system_utils.pam as pam
import system_utils.usage as sys_usage
from . import auth as pam_auth
from . import api_collection as api_col
from . import vdr

import pydbus

app.secret_key = os.urandom(24)

# RESTful API
api.add_resource(pam_auth.Login, '/api/login')
api.add_resource(pam_auth.TokenLogin, '/api/login/token')
api.add_resource(api_col.SystemInfo, '/api/system/status')
api.add_resource(api_col.HitKey, '/api/hitkey')
api.add_resource(api_col.HitKeys, '/api/hitkeys')
api.add_resource(vdr.VDR_Recordings, '/api/vdr/recordings')
api.add_resource(vdr.VDR_Plugins, '/api/vdr/plugins')
api.add_resource(vdr.VDR_Timers, '/api/vdr/timers')
api.add_resource(vdr.VDR_Channels, '/api/vdr/channels')

# resources
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static', os.path.join('js', path))

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static', os.path.join('css', path))

@app.route('/fonts/<path:path>')
def send_fonts(path):
    return send_from_directory('static', os.path.join('fonts', path))

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('static', os.path.join('images', path))

@app.route('/favicon.ico')
def send_favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/api')
def api_description():
    return render_template('api.html', title='yaVDR API Documentation')

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))
#@app.route('/login', methods=['GET', 'POST'])
#def login_auth():
#    if request.method == 'POST':
#        session['username'] = request.form['username']
#        return redirect(url_for('index'))
#    return '''
#        <form method="post">
#            <p><input type="text" name="username">
#            <p><input type="password" name="password">
#            <p><input type="submit" value="Login">
#        </form>'''
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('userdata', None)
    session.pop('groups', None)
    #return redirect(url_for('index'))
    return jsonify({'msg': 'logged out'}), 200

@app.route('/usage')
def usage():
    data = sys_usage.collect_data()
    return render_template('usage.html', title='System Information', data=data)

# @pam_auth.login_required
# @app.route('/api/hitkey', methods=['POST'])
# def hitkey(key):
#     try:
#         bus = pydbus.SystemBus()
#         lircd2uinput = bus.get('de.yavdr.lircd2uinput', '/control')
#         success, key_code = lircd2uinput.emit_key(key.upper())
#     except GLib.Error:
#         return jsonify({'msg': 'lircd2uinput is not available'}), 503
#     if success:
#         return jsonify({'msg': 'ok', 'key': key.upper()}), 200
#     else:
#         return jsonify({'msg': 'unknown key'}), 400

# @pam_auth.login_required
# @app.route('/api/hitkeys', methods=['POST'])
# def hitkey(key):
#     try:
#         bus = pydbus.SystemBus()
#         lircd2uinput = bus.get('de.yavdr.lircd2uinput', '/control')
#         success, key_code = lircd2uinput.emit_key(key.upper())
#     except GLib.Error:
#         return jsonify({'msg': 'lircd2uinput is not available'}), 503
#     if success:
#         return jsonify({'msg': 'ok', 'key': key.upper()}), 200
#     else:
#         return jsonify({'msg': 'unknown key'}), 400
