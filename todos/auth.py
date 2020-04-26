from flask import g, abort

from flask_httpauth import MultiAuth, HTTPBasicAuth, HTTPTokenAuth
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)

from models import User
from config import SECRET_KEY

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme="Bearer")
auth = MultiAuth(token_auth, basic_auth)

@basic_auth.verify_password
def verify_password(username, password):
    try:
        api_user = User.get(User.username == username)
    except User.DoesNotExist:
        return False
    user_verified = api_user.check_password(password)
    if user_verified:
        g.user = api_user
        return True
    return False

@token_auth.verify_token
def verify_token(token):
    timed_serializer = Serializer(SECRET_KEY)
    try:
        id = timed_serializer.loads(token)
        api_user = User.get_by_id(id)
    except (SignatureExpired, BadSignature) as e:
        abort(400, description=str(e))
    return True
