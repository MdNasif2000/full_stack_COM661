from flask import request, jsonify, make_response
from functools import wraps
import jwt

from database import blacklist_token
from config import SECRET_KEY



# Admin Wrapper
def admin_required(func):

    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):

        token = request.headers.get('x-access-token')

        if not token:
            return make_response(jsonify({
                'Message': 'Token is missing'
            }), 401)

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=['HS256']
            )

        except jwt.InvalidTokenError:
            return make_response(jsonify({
                'Message': 'Token is invalid'
            }), 401)

        if data['admin']:
            return func(*args, **kwargs)

        else:
            return make_response(jsonify({
                'Message': 'Admin access required!'
            }), 401)

    return admin_required_wrapper


# JWT Wrapper
def jwt_required(func):

    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):

        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response(jsonify({
                'Message': 'Token is missing'
            }), 401)

        try:
            data = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=['HS256']
            )

        except jwt.InvalidTokenError:
            return make_response(jsonify({
                'Message': 'Token is invalid'
            }), 401)

        bl_token = blacklist_token.find_one({
            'token': token
        })

        if bl_token is not None:
            return make_response(jsonify({
                'Message': 'Token has been cancelled!'
            }), 401)

        return func(*args, **kwargs)

    return jwt_required_wrapper
