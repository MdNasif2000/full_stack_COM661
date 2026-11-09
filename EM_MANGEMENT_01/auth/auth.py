from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

from database import users, blacklist_token, employees
from config import SECRET_KEY
from decorators import jwt_required


auth_bp = Blueprint('auth', __name__)


# Route to register
@auth_bp.route("/api/v1.0/register", methods=["POST"])
def register():

    #Accept JSON or Form Data
    if request.is_json:

        data = request.get_json()

        if not isinstance(data, dict):
            return make_response(jsonify({
                'Error': 'Invalid JSON data'
            }), 400)

    elif request.mimetype in [
        'multipart/form-data',
        'application/x-www-form-urlencoded'
    ]:

        data = request.form.to_dict()

    else:
        return make_response(jsonify({
            'Error': 'Unsupported content type'
        }), 415)

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all(isinstance(value, str) for value in
            [username, email, password]):

        return make_response(jsonify({
            'Error': 'All fields must be provided as strings'
        }), 400)

    username = username.strip().lower()
    email = email.strip().lower()

    if not all([username, email, password]):

        return make_response(jsonify({
            'Error': 'All fields are required'
        }), 400)

    if len(username) < 3 or len(username) > 30:

        return make_response(jsonify({
            'Error': 'Username must be between 3 and 30 characters'
        }), 400)

    if '@' not in email or '.' not in email.split('@')[-1]:

        return make_response(jsonify({
            'Error': 'Please provide a valid email address'
        }), 400)
    
    if len(password) < 6 or len(password.encode('utf-8')) > 72:
        return make_response(jsonify({
            'Error': 'Password must be at least 6 characters and not exceed 72 bytes'
        }), 400)
    

    existing_user = users.find_one({
        '$or': [
            {'username': username},
            {'email': email}
        ]
    })

    if existing_user:

        return make_response(jsonify({
            'Error': 'Username or email already exists'
        }), 409)

    last_user = users.find_one(
        {},
        {'user_id': 1},
        sort=[('user_id', -1)]
    )

    if last_user:

        last_id = int(last_user['user_id'][3:])
        new_user_id = f'USR{last_id + 1:04d}'

    else:
        new_user_id = 'USR0001'

    # Hash password using bcrypt
    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    current_time = datetime.now(timezone.utc).isoformat()

    new_user = {

        'user_id': new_user_id,
        'username': username,
        'email': email,
        'password': hashed_password,
        'admin': False,
        'role': 'employee',
        'account_status': 'active',
        'created_at': current_time,
        'updated_at': current_time

    }

    users.insert_one(new_user)
    
    # Generate JWT token
    token = jwt.encode({

    'user': username,
    'admin': False,

    'exp': datetime.now(timezone.utc)
           + timedelta(minutes=30)
    },
    SECRET_KEY,
    algorithm="HS256")

    return make_response(jsonify({

        'Message': 'Registration successful',
        'token': token,
        'user': {
            'user_id': new_user_id,
            'username': username,
            'email': email,
            'admin': False,
            'role': 'employee',
            'account_status': 'active',
            'created_at': current_time,
            'updated_at': current_time
        }

    }), 201)




# Route to login
@auth_bp.route("/api/v1.0/login", methods=["GET"])
def login():

    auth = request.authorization

    if auth:

        user = users.find_one({
            'username': auth.username
        })

        if user is not None:

            if bcrypt.checkpw(
                auth.password.encode('utf-8'),
                user['password'].encode('utf-8')):

                token = jwt.encode({

                    'user': auth.username,
                    'admin': user['admin'],

                    'exp': datetime.now(timezone.utc)
                           + timedelta(minutes=30)

                },
                SECRET_KEY,
                algorithm="HS256")

                return make_response(
                    jsonify({"token": token}),
                    200
                )

            else:
                return make_response(jsonify({
                    'Error': 'Wrong Password'
                }), 401)

        else:
            return make_response(jsonify({
                'Error': 'Wrong username!'
            }), 401)

    return make_response(
        jsonify({"Error": "could not verify"}),
        401,
        {'WWW-Authenticate': 'Basic realm="login Required"'}
    )


# Route to logout
@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():

    token = request.headers['x-access-token']

    blacklist_token.insert_one({
        'token': token
    })

    return make_response(jsonify({
        'Message': 'Logout Successful'
    }), 200)
