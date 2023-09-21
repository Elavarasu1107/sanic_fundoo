import enum
from sanic import exceptions
import jwt
from datetime import datetime, timedelta
from settings import settings
from .models import User
from settings import settings

class Audience(enum.Enum):
    register = 'register'
    login = 'login'
    reset = 'reset password'


class JWT:

    @staticmethod
    def encode(payload):
        now = datetime.utcnow()
        payload['iat'] = now
        if 'exp' not in payload:
            payload.update(exp=now + timedelta(hours=settings.jwt_exp))
        return jwt.encode(payload=payload, key=settings.admin_key, algorithm=settings.jwt_algo)

    @staticmethod
    def decode(token, aud):
        try:
            return jwt.decode(jwt=token, key=settings.admin_key, algorithms=[settings.jwt_algo], audience=aud)
        except jwt.PyJWTError as ex:
            raise ex


def verify_user(function):
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('authorization')
        token = token.split(' ')[1]
        if not token:
            raise exceptions.Unauthorized('Auth token not found')
        payload = JWT.decode(token=token, aud=Audience.login.value)
        if 'user' not in payload:
            raise exceptions.Unauthorized('Invalid token')
        user = User.nodes.get_or_none(id=payload['user'])
        if not user:
            raise exceptions.Unauthorized('User not found')
        request.ctx.user = user
        # try:
        #     request.json.update(user_id=user.id)
        # except:
        #     pass
        return function(request, *args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper
