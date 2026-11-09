from flask import Blueprint, make_response,jsonify, request
from bson import ObjectId
import datetime
import jwt 
import bcrypt
import globals

users = globals.db.users
blacklist_token = globals.db.blacklist_token
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/api/v1.0/login",methods =["GET"])
def login():
    #auth = request.authorization
    
    auth = request.authorization
    if auth:
        user = users.find_one({
            'username' : auth.username
        })
        
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password,'utf-8'),user['password']):
                token = jwt.encode({
                    'user' : auth.username,
                    'admin' : user['admin'],
                    'exp'  : datetime.datetime.now(datetime.UTC)+ datetime.timedelta(minutes =30)
                },
                globals.config['SECRET_KEY'],
                algorithm  = "HS256")
                return make_response(jsonify({"token": token}),200)

            else:
                return make_response(jsonify({
                    'Error' : 'Wrong Password'
                }),401)
        else:
            return make_response(jsonify({
                'Error' : 'Wrong username !'
            }),401)
                        
    return make_response(jsonify({"Error":"could not verify"}),401, {'WWW-Authenticate': 'Basic realm = "login Required"'})

@auth_bp.route("/api/v1.0/logout",methods =["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist_token.insert_one({
        'token' : token
    })
    
    return make_response(jsonify({
        'Message' : 'Logout Successful '
    }),200)