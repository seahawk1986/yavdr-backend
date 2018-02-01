"""
This module provides a stateless PAM-authentification.
"""
import grp
from functools import wraps
from app import app, api
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import request, session
from flask_restful import Resource, reqparse
import system_utils.pam as pam

# TODO: generate random key for production usage
SECRET_KEY = 'https://xkcd.com/221/'

def check_login(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if 'userdata' and 'groups' in session:
            return f(*args, **kwds)
        try:
            auth_data = request.headers.get('Authorization')
            if not auth_data:
                raise ValueError
            token = auth_data.split()[-1]
            if token:
                token_data = PAM_Auth.verify_auth_token(token)
                if token_data is not None:
                    return f(*args, **kwds)
            raise ValueError
        except ValueError:
            return {'msg': 'invalid authorization, please log in and try again'}, 401
    return wrapper

class PAM_Auth:
    def __init__(self):
        self.pam = pam.pam()

    def pam_login(self, username, password):
        if pam.authenticate(username, password):
            groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
            return username, groups
        return None, None

    def generate_auth_token(self, content, expiration=6000):
        print(content)
        print(type(content))
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
        return data

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
                         "msg": "login successfull"},
                        200)
        return {"message": "invalid username or password"}, 401


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
                return ({
                         "msg": "login successfull"},
                        200)
        return {"message": "invalid username or password"}, 401

    @check_login
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
                token_dict = token_data.get('token')
                return {'msg': "valid token",
                        'username': token_dict.get('username'),
                        'groups': token_dict.get('groups')}, 200
            return {'msg': 'invalid token'}, 401
        else:
            return {}, 401
