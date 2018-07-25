import os
from flask import render_template, session, redirect, url_for, jsonify, send_from_directory

from app import app, api
import system_utils.usage as sys_usage
from . import auth as pam_auth
from . import api_collection as api_col
from . import vdr


app.secret_key = os.urandom(24)

# RESTful API
api.add_resource(pam_auth.Login, '/api/login')
api.add_resource(pam_auth.TokenLogin, '/api/login/token')
api.add_resource(api_col.SystemInfo, '/api/system/status')
api.add_resource(api_col.SystemTask, '/api/system/task/<string:task>')
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

