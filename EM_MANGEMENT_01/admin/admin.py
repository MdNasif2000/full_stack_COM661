from flask import Blueprint, request, jsonify, make_response

from datetime import datetime

from database import (
    users,
    employees,
    departments,
    roles,
    attendance,
    leave_requests
)

from decorators import jwt_required, admin_required


admin_bp = Blueprint('admin', __name__)


#route to get all users 

@admin_bp.route('/api/v1.0/admin/users', methods=['GET'])
@jwt_required
@admin_required
def get_all_users():
    query = {}

    if request.args.get('username'):
        query['username'] = {
            '$regex': request.args.get('username').strip(),
            '$options': 'i'
        }

    if request.args.get('email'):
        query['email'] = {
            '$regex': request.args.get('email').strip(),
            '$options': 'i'
        }

    if request.args.get('role'):
        role = request.args.get('role').strip()

        if role not in ['admin', 'hr_staff', 'manager','employee']:
            return make_response(jsonify({
                'Error': 'Invalid user role.'
            }), 400)

        query['role'] = role

    data_to_return = []

    for user in users.find(query, {'password': 0}).sort('user_id', 1):
        user['_id'] = str(user['_id'])
        data_to_return.append(user)

    return make_response(jsonify(data_to_return), 200)

#route to get one user

@admin_bp.route('/api/v1.0/admin/users/<string:user_id>', methods=['GET'])
@jwt_required
@admin_required
def get_one_user(user_id):
    user = users.find_one(
        {'user_id': user_id},
        {'password': 0}
    )

    if user is None:
        return make_response(jsonify({
            'Error': 'User not found.'
        }), 404)

    user['_id'] = str(user['_id'])

    return make_response(jsonify(user), 200)

#route to update an user 

@admin_bp.route('/api/v1.0/admin/users/<string:user_id>', methods=['PUT'])
@jwt_required
@admin_required
def update_user(user_id):
    user = users.find_one({'user_id': user_id})

    if user is None:
        return make_response(jsonify({
            'Error': 'User not found.'
        }), 404)

    data = request.form.to_dict()

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    allowed_fields = ['username', 'email', 'role']

    invalid_fields = [
        field for field in data
        if field not in allowed_fields
    ]

    if invalid_fields:
        return make_response(jsonify({
            'Error': 'One or more fields cannot be updated.',
            'Invalid fields': invalid_fields
        }), 400)

    for field in data:
        data[field] = data[field].strip()

        if not data[field]:
            return make_response(jsonify({
                'Error': f'{field} cannot be empty.'
            }), 400)

    if 'role' in data:
        if data['role'] not in ['admin', 'hr_staff', 'manager','employee']:
            return make_response(jsonify({
                'Error': 'Invalid user role.'
            }), 400)

    if 'username' in data:
        existing_username = users.find_one({
            'username': data['username'],
            'user_id': {'$ne': user_id}
        })

        if existing_username:
            return make_response(jsonify({
                'Error': 'This username already exists.'
            }), 409)

    # Check for an existing email
    if 'email' in data:
        existing_email = users.find_one({
            'email': data['email'],
            'user_id': {'$ne': user_id}
        })

        if existing_email:
            return make_response(jsonify({
                'Error': 'This email already exists.'
            }), 409)

    data['updated_at'] = datetime.now().isoformat(timespec='seconds')

    users.update_one(
        {'user_id': user_id},
        {'$set': data}
    )

    updated_user = users.find_one(
        {'user_id': user_id},
        {'password': 0}
    )

    updated_user['_id'] = str(updated_user['_id'])

    return make_response(jsonify({
        'Message': 'User updated successfully.',
        'User': updated_user
    }), 200)

#route to delete a user 

@admin_bp.route('/api/v1.0/admin/users/<string:user_id>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_user(user_id):
    user = users.find_one({
        'user_id': user_id
    })

    if user is None:
        return make_response(jsonify({
            'Error': 'User not found.'
        }), 404)

    if user.get('role') == 'admin':
        admin_count = users.count_documents({
            'role': 'admin'
        })

        if admin_count <= 1:
            return make_response(jsonify({
                'Error': 'The last administrator account cannot be deleted.'
            }), 400)

    result = users.delete_one({
        'user_id': user_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'User could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'User deleted successfully.'
    }), 200)

#route for admin dashboard

@admin_bp.route('/api/v1.0/admin/dashboard', methods=['GET'])
@jwt_required
@admin_required
def get_admin_dashboard():
    dashboard = {
        'total_users': users.count_documents({}),

        'total_employees': employees.count_documents({}),

        'total_departments': departments.count_documents({}),

        'total_roles': roles.count_documents({}),

        'total_attendance_records': attendance.count_documents({}),

        'total_leave_requests': leave_requests.count_documents({}),

        'pending_leave_requests': leave_requests.count_documents({
            'status': 'Pending'
        }),

        'active_employees': employees.count_documents({
            'status': 'Active'
        })
    }

    return make_response(jsonify(dashboard), 200)
