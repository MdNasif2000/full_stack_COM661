from flask import Blueprint, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError

from database import departments, employees

from decorators import jwt_required, admin_required


department_bp = Blueprint('departments', __name__)


#route to get all departments

@department_bp.route('/api/v1.0/departments', methods= ['GET'])
@jwt_required
@admin_required
def get_all_departments():
    
    query = {}

    if request.args.get('name'):
        query['name'] = {
            '$regex' :request.args.get('name').strip(),
            '$options' : 'i'
        }
            
    
    data_to_return = []
    for department in departments.find(query):
        department['_id'] = str(department['_id'])
        
        data_to_return.append(department)

    return make_response(jsonify(data_to_return),200)

#route to get one department

@department_bp.route('/api/v1.0/departments/<string:department_id>', methods = ['GET'])
@jwt_required
@admin_required
def get_one_department(department_id):
    
    department = departments.find_one({
        'department_id' : department_id
    })
    if department is not None:
        department['_id'] = str(department['_id'])

        return make_response(jsonify(department),200)
    
    return make_response(jsonify({'Error' : 'Department Id is not valid  !'}),404)    

#route to add a department

@department_bp.route('/api/v1.0/departments', methods=["POST"])
@jwt_required
@admin_required
def add_department():

    data = request.form

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    required_fields = [
        'department_id',
        'name'
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

    department_id = data['department_id'].strip()
    name = data['name'].strip()
    description = data.get('description', '').strip()
    manager_id = data.get('manager_id', '').strip()

    existing_department = departments.find_one({
        'department_id': department_id
    })

    if existing_department:
        return make_response(jsonify({
            'Error': 'This department ID is already registered.'
        }), 409)

    existing_name = departments.find_one({
        'name': name
    })

    if existing_name:
        return make_response(jsonify({
            'Error': 'This department name already exists.'
        }), 409)

    if manager_id:
        manager = employees.find_one({
            'employee_id': manager_id
        })

        if manager is None:
            return make_response(jsonify({
                'Error': 'The specified manager does not exist.'
            }), 400)

    department = {
        'department_id': department_id,
        'name': name,
        'description': description,
        'manager_id': manager_id if manager_id else None
    }

    try:
        departments.insert_one(department)

    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'A department with these unique details already exists.'
        }), 409)
    new_department = departments.find_one({
        'department_id': department_id
    })
    new_department['_id'] = str(new_department['_id'])
    return make_response(jsonify({
        'Message': 'Department created successfully.',
        'Department': new_department
    }), 201)

#route to update a department

@department_bp.route('/api/v1.0/departments/<string:department_id>', methods = ['PUT'])
@jwt_required
@admin_required
def update_department(department_id):
    
    department = departments.find_one({
        'department_id' : department_id
    })
    if department is None:
        return make_response(jsonify({
            'Error' : 'No department found !'
        }),404)
    
    data = request.form 
    
    if not data:
        return make_response(jsonify({
            'Error' : 'No form data was provided !'
        }), 400)
        
    required_field = [
        'manager_id'
    ]
    missing_field = [ 
        field for field in required_field if not data.get(field) or not data.get(field).strip()
    ]    
    
    if missing_field:
        return make_response(jsonify({
            'Error' : 'Required field value missing !',
            'Field' : missing_field
        }),400)
    
    departments.update_one(
        {'department_id' : department_id},
        { '$set' :{
            'manager_id' : data['manager_id'].strip()
            }
        }
    )    
    
    updated_department = departments.find_one({
        'department_id' : department_id
    })
    
    updated_department['_id'] = str(updated_department['_id'])
    return make_response(jsonify({
        'Message':'Department updated successfully ',
        'Department':updated_department
    }),200)    
    

#route to delete a department 

@department_bp.route('/api/v1.0/departments/<string:department_id>', methods = ['DELETE'])
@jwt_required
@admin_required
def delete_department(department_id):
    
    department = departments.find_one({
        'department_id': department_id
    })
    if department is None:
        return make_response(jsonify({'Error' : 'Department could not found'}),404)

    department['_id'] = str(department['_id'])

    result = departments.delete_one({
        'department_id' : department_id
    })
    
    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Department could not be deleted !'
        }),500)
    return make_response(jsonify({
        'Message': 'Department deleted successfully'
    }),200)