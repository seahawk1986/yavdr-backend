"""
This module provides a stateless PAM-authentification.
"""
import grp
import json
from functools import wraps
from app import app, api
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import request, session, Response, jsonify
from flask_restful import Resource, reqparse
import system_utils.pam as pam

# TODO: generate random key for production usage
SECRET_KEY = 'https://xkcd.com/221/'

LOGIN_AUTH_ERROR = "invalid username or password"
AUTH_ERROR = "invalid authorization, please log in and try again"
LOGIN_AUTH_SUCCESSFULL = "login successfull"

def check_group_permissions(groups, limit_groups):
    if limit_groups:
        if set(limit_groups).intersection(groups):
            return True
        return False
    return True

def login_required(f=None, limit_groups=None):
    def actual_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            try:
                if 'username' in session and 'groups' in session:
                    if check_group_permissions(session['groups'], limit_groups):
                        return f(*args, **kwds)
                    raise PermissionError
                auth_data = request.headers.get('Authorization')
                if not auth_data:
                    raise PermissionError
                token = auth_data.split()[-1]
                if token:
                    token_data = PAM_Auth.verify_auth_token(token)
                    if (token_data is not None and
                    check_group_permissions(token_data['groups'], limit_groups)):
                        return f(*args, **kwds)
                raise PermissionError
            except PermissionError:
                return Response(json.dumps({"msg": AUTH_ERROR}), 401, {'WWW-Authenticate': 'Bearer realm="Login Required"'})
        return wrapper
    if not f:
        def waiting_for_f(f):
            return actual_decorator(f)
        return waiting_for_f
    return actual_decorator(f)

class PAM_Auth:
    def __init__(self):
        self.pam = pam.pam()

    def pam_login(self, username, password):
        if pam.authenticate(username, password):
            groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
            return username, groups
        return None, None

    def generate_auth_token(self, content, expiration=6000):
        #serializer = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        serializer = Serializer(SECRET_KEY, expires_in=expiration)
        return serializer.dumps({'token': content})

    @staticmethod
    def verify_auth_token(token):
        """
        verify and extract data from a given token. If the token is valid,
        it's signed content is returned, otherwise None is returned.
        """
        serializer = Serializer(SECRET_KEY)
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return data['token']

class TokenLogin(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        if username and password:
            pam_auth = PAM_Auth()
            user, *groups = pam_auth.pam_login(username, password)
            if user is not None:
                token = pam_auth.generate_auth_token({'username': username, 'groups': groups})
                return ({"token": token.decode('utf-8'), # the serializer returns a byte object
                         "msg": LOGIN_AUTH_SUCCESSFULL},
                        200)
        return {"msg": LOGIN_AUTH_ERROR}, 400


class Login(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        if username and password:
            pam_auth = PAM_Auth()
            user, groups = pam_auth.pam_login(username, password)  # the serializer returns a byte object
            if user is not None:
                session['username'] = username
                session['groups'] = groups
                return ({"msg": LOGIN_AUTH_SUCCESSFULL,
                         "groups": groups},
                        200)
        return {"msg": LOGIN_AUTH_ERROR}, 400

    def get(self):
        if 'username' in session and 'groups' in session:
            return {'msg': 'authenticated by cookie',
                    'username': session['username'],
                    'groups': session['groups']}, 200
        auth_data = request.headers.get('Authorization')
        token = auth_data.split()[-1]
        if token:
            token_data = PAM_Auth.verify_auth_token(token)
            if token_data is not None:
                return {'msg': "valid token",
                        'username': token_data.get('username'),
                        'groups': token_data.get('groups')}, 200
            return {'msg': 'invalid token'}, 401
        else:
            return {}, 401
