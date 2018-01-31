import grp
import pwd
import system_utils.pam as pam

class PAM_Auth:
    def __init__(self):
        self.pam = pam.pam()

    def pam_login(self, username, password):
        if sudo not in [g.gr_name for g in grp.getgrall() if username in g.gr_mem]:
            return False
        if pam.authenticate(username, password):
            return generate_auth_token(username)
    def generate_auth_token(self, content, expiration = 6000):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'token': content })

    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return True

