from sanic import Blueprint, exceptions
from sanic_ext import validate, openapi
from sanic.response import json
from . import schemas
from .utils import JWT, Audience
from .models import User
from tasks import send_mail
from settings import settings

bp = Blueprint('user')


@bp.post('/signUp')
@openapi.definition(body={'application/json': schemas.UserRequest.model_json_schema()})
@validate(json=schemas.UserRequest)
async def register_user(request, body: schemas.UserRequest):
    user = User(**body.model_dump())
    user.save_user()
    token = JWT.encode({'user': user.id, 'aud': Audience.register.value})
    url = f'{settings.base_url}:8000{request.app.url_for("user.verify_user")}?token={token}'
    payload = {'recipient': user.email,
               'subject': 'Sanic user registration',
               'message': url}
    request.app.add_task(send_mail(payload))
    return json({'message': 'User created', 'status': 201, 'data': user.to_json}, status=201)


@bp.post('/signIn')
@openapi.definition(body={'application/json': schemas.UserLogin.model_json_schema()})
@validate(json=schemas.UserLogin)
async def login_user(request, body: schemas.UserLogin):
    user = User.nodes.get_or_none(username=body.username)
    if not user or not user.check_password(body.password):
        raise exceptions.Unauthorized(message='Invalid username or password')
    if not user.is_verified:
        raise exceptions.BadRequest('User not verified')
    return json({'message': 'Login successful', 'status': 200, 'data': {
        'access': JWT.encode({'user': user.id, 'aud': Audience.login.value})
    }}, status=200)


@bp.get('/verify')
@openapi.definition(parameter={'name': 'token', 'required': True})
@validate(query_argument='token')
async def verify_user(request):
    token = request.args.get('token')
    if not token:
        raise exceptions.HTTPException('Token not found')
    payload = JWT.decode(token=token, aud=Audience.register.value)
    if 'user' not in payload:
        raise exceptions.HTTPException('Invalid token')
    user = User.nodes.get_or_none(id=payload['user'])
    if not user:
        raise exceptions.Unauthorized('User not found')
    user.is_verified = True
    user.save()
    return json({'message': 'User verified successfully', 'status': 200}, status=200)


@bp.post('/forgotPassword')
@openapi.definition(body={'application/json': {'email': str}})
async def forgot_password(request):
    user = User.nodes.get_or_none(email=request.json.get('email'))
    if not user:
        raise exceptions.HTTPException('Invalid email id')
    token = JWT.encode({'user': user.id, 'aud': Audience.reset.value})
    url = f'{request.url_for("user.reset_password", token=token)}'
    payload = {'recipient': user.email,
               'subject': 'Sanic reset password',
               'message': url}
    request.app.add_task(send_mail(payload=payload))
    return json({'message': 'Email sent successfully', 'status': 200}, status=200)


@bp.post('/resetPassword')
@openapi.definition(body={'application/json': schemas.ResetPassword.model_json_schema()},
                    parameter={'name': 'token', 'required': True})
@validate(json=schemas.ResetPassword)
def reset_password(request, body: schemas.ResetPassword):
    token = request.args.get('token')
    if not token:
        raise exceptions.HTTPException('Token not found')
    payload = JWT.decode(token=token, aud=Audience.reset.value)
    if 'user' not in payload:
        raise exceptions.HTTPException('Invalid token')
    if body.new_password != body.confirm_password:
        raise exceptions.HTTPException('password mismatch')
    user = User.nodes.get_or_none(id=payload['user'])
    if not user:
        raise exceptions.Unauthorized('User not found')
    user.make_password(body.confirm_password)
    user.save()
    return json({'message': 'Password reset successful', 'status': 200}, status=200)
