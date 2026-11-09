from flask import Blueprint, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from database import roles

from decorators import jwt_required, admin_required


role_bp = Blueprint('roles', __name__)


# Route to get all roles

@role_bp.route('/api/v1.0/roles', methods=['GET'])
@jwt_required
@admin_required
def get_all_roles():

    query = {}

    if request.args.get('name'):
        query['name'] = {
            '$regex': request.args.get('name').strip(),
            '$options': 'i'
        }

    data_to_return = []

    for role in roles.find(query).sort('role_id', 1):
        role['_id'] = str(role['_id'])
        data_to_return.append(role)

    return make_response(jsonify(data_to_return), 200)

# Route to get one role

@role_bp.route('/api/v1.0/roles/<string:role_id>', methods=['GET'])
@jwt_required
@admin_required
def get_one_role(role_id):

    role = roles.find_one({
        'role_id': role_id
    })

    if role is None:
        return make_response(jsonify({
            'Error': 'Role not found !'
        }), 404)

    role['_id'] = str(role['_id'])

    return make_response(jsonify(role), 200)

# Route to add a role

@role_bp.route('/api/v1.0/roles', methods=['POST'])
@jwt_required
@admin_required
def add_role():

    data = request.form

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    required_fields = [
        'role_id',
        'name',
        'min_salary',
        'max_salary'
    ]

    missing_fields = [
        field for field in required_fields
        if not data.get(field) or not data.get(field).strip()
    ]

    if missing_fields:
        return make_response(jsonify({
            'Error': 'Required fields are missing.',
            'Fields': missing_fields
        }), 400)

    role_id = data['role_id'].strip()
    name = data['name'].strip()
    description = data.get('description', '').strip()

    try:
        min_salary = float(data['min_salary'])
        max_salary = float(data['max_salary'])

    except ValueError:
        return make_response(jsonify({
            'Error': 'Salary values must be numeric.'
        }), 400)

    if min_salary < 0 or max_salary < 0:
        return make_response(jsonify({
            'Error': 'Salary values cannot be negative.'
        }), 400)

    if min_salary > max_salary:
        return make_response(jsonify({
            'Error': 'Minimum salary cannot exceed maximum salary.'
        }), 400)

    existing_role = roles.find_one({
        'role_id': role_id
    })

    if existing_role:
        return make_response(jsonify({
            'Error': 'This role ID is already registered.'
        }), 409)

    existing_name = roles.find_one({
        'name': name
    })

    if existing_name:
        return make_response(jsonify({
            'Error': 'This role name already exists.'
        }), 409)

    role = {
        'role_id': role_id,
        'name': name,
        'description': description,
        'min_salary': min_salary,
        'max_salary': max_salary
    }

    try:
        roles.insert_one(role)

    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'A role with these unique details already exists.'
        }), 409)

    new_role = roles.find_one({
        'role_id': role_id
    })

    new_role['_id'] = str(new_role['_id'])

    return make_response(jsonify({
        'Message': 'Role created successfully.',
        'Role': new_role
    }), 201)

# Route to update a role

@role_bp.route('/api/v1.0/roles/<string:role_id>', methods=['PUT'])
@jwt_required
@admin_required
def update_role(role_id):

    role = roles.find_one({
        'role_id': role_id
    })

    if role is None:
        return make_response(jsonify({
            'Error': 'Role not found.'
        }), 404)

    data = request.form.to_dict()

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    allowed_fields = [
        'name',
        'description',
        'min_salary',
        'max_salary'
    ]

    invalid_fields = [
        field for field in data
        if field not in allowed_fields
    ]

    if invalid_fields:
        return make_response(jsonify({
            'Error': 'One or more fields cannot be updated.',
            'Invalid fields': invalid_fields
        }), 400)

    for field, value in data.items():

        data[field] = value.strip()

        if not data[field]:
            return make_response(jsonify({
                'Error': f'{field} must not be empty.'
            }), 400)

    if 'name' in data:

        existing_name = roles.find_one({
            'name': data['name'],
            'role_id': {'$ne': role_id}
        })

        if existing_name:
            return make_response(jsonify({
                'Error': 'This role name already exists.'
            }), 409)

    for field in ['min_salary', 'max_salary']:

        if field in data:
            try:
                data[field] = float(data[field])

            except ValueError:
                return make_response(jsonify({
                    'Error': f'{field} must be numeric.'
                }), 400)

            if data[field] < 0:
                return make_response(jsonify({
                    'Error': 'Salary values cannot be negative.'
                }), 400)

    min_salary = data.get('min_salary', role['min_salary'])
    max_salary = data.get('max_salary', role['max_salary'])

    if min_salary > max_salary:
        return make_response(jsonify({
            'Error': 'Minimum salary cannot exceed maximum salary.'
        }), 400)

    try:
        roles.update_one(
            {'role_id': role_id},
            {'$set': data}
        )

    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'The update conflicts with existing role information.'
        }), 409)

    updated_role = roles.find_one({
        'role_id': role_id
    })

    updated_role['_id'] = str(updated_role['_id'])

    return make_response(jsonify({
        'Message': 'Role updated successfully.',
        'Role': updated_role
    }), 200)

# Route to delete a role

@role_bp.route('/api/v1.0/roles/<string:role_id>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_role(role_id):

    role = roles.find_one({
        'role_id': role_id
    })

    if role is None:
        return make_response(jsonify({
            'Error': 'Role not found.'
        }), 404)

    result = roles.delete_one({
        'role_id': role_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Role could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'Role deleted successfully.'
    }), 200)