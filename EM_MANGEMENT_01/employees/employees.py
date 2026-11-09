from flask import Blueprint, jsonify, make_response, request

from datetime import date

from pymongo.errors import DuplicateKeyError

from database import employees, departments, roles, attendance, leave_requests

from decorators import jwt_required, admin_required


employee_bp = Blueprint('employee', __name__)



#route to get a employee complete profile

@employee_bp.route('/api/v1.0/employees/<string:employee_id>/profile', methods=['GET'])
@jwt_required
@admin_required
def get_employee_profile(employee_id):
    
    def convert_id(document):
        if document is not None and "_id" in document:
            document["_id"] = str(document["_id"])
            return document

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'error': 'Employee not found'
        }), 404)

    department = departments.find_one({
        'department_id': employee.get('department_id')
    })

    role = roles.find_one({
        'role_id': employee.get('role_id')
    })

    attendance_records = list(attendance.find({
        'employee_id': employee_id
    }))

    leave_records = list(leave_requests.find({
        'employee_id': employee_id
    }))
    employee = convert_id(employee)
    department = convert_id(department)
    role = convert_id(role)
    attendance_records = [ convert_id(record) for record in attendance_records]
    leave_records = [ convert_id(record) for record in leave_records]

    return make_response(jsonify({
        'employee': employee,
        'department': department,
        'job_role': role,
        'attendance': attendance_records,
        'leave_requests': leave_records
    }), 200 )


#route to get all employees

@employee_bp.route('/api/v1.0/employees', methods =["GET"])
@jwt_required
@admin_required
def get_all_employees():

    page_num = request.args.get('pn', default=1, type=int)
    page_size = request.args.get('ps', default=10, type=int)

    if page_num is None or page_num < 1:
        return make_response(jsonify({
            'Error': 'Page number must be a positive integer.'
        }), 400)

    if page_size is None or page_size < 1:
        return make_response(jsonify({
            'Error': 'Page size must be a positive integer.'
        }), 400)

    if page_size > 50:
        return make_response(jsonify({
            'Error': 'Page size cannot exceed 50.'
        }), 400)

    page_start = page_size * (page_num - 1)

    query = {}

    if request.args.get('department_id'):
        query['department_id'] = request.args.get('department_id').strip()

    if request.args.get('role_id'):
        query['role_id'] = request.args.get('role_id').strip()

    if request.args.get('status'):
        status = request.args.get('status').strip()

        if status not in ['Active', 'Inactive']:
            return make_response(jsonify({
                'Error': 'Status must be Active or Inactive.'
            }), 400)

        query['status'] = status

    if request.args.get('first_name'):
        query['first_name'] = {
            '$regex': request.args.get('first_name').strip(),
            '$options': 'i'
        }

    data_to_return = []

    for employee in employees.find(query).sort('employee_id', 1).skip(page_start).limit(page_size):

        employee['_id'] = str(employee['_id'])
        data_to_return.append(employee)

    return make_response(jsonify(data_to_return), 200)



#route to get one employee    

@employee_bp.route('/api/v1.0/employees/<string:employee_id>', methods= ["GET"])
@jwt_required
def get_one_employee(employee_id):
    
    employee = employees.find_one(
        {"employee_id": employee_id},
        {"_id": 0}
    )
    
    if employee is not None:
        return make_response(jsonify(employee),200)    

    else:
        return make_response(jsonify({'Error': 'Invalid Employee ID !'}), 404)    

#route to add a new employee

@employee_bp.route('/api/v1.0/employees', methods =["POST"])
@jwt_required
@admin_required
def add_employee():
        
    data = request.form

    required_fields = [
        'employee_id',
        'first_name',
        'last_name',
        'email',
        'hire_date',
        'department_id',
        'role_id'
    ]

    missing_fields = [
        field for field in required_fields
        if not data.get(field) or not data.get(field).strip()
    ]

    if missing_fields:
        return make_response(jsonify({
            'Error': 'Required fields are missing !',
            'fields': missing_fields
        }), 400)

    email = data['email'].strip()

    # Different validations
    if '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
        return make_response(jsonify({
            'Error': 'Please provide a valid email address.'
        }), 400)

    try:
        hire_date = date.fromisoformat(data['hire_date'].strip())
    except ValueError:
        return make_response(jsonify({
            'Error': 'INVALID date, date must use YYYY-MM-DD format.'
        }), 400)

    department = departments.find_one({
        'department_id': data['department_id'].strip()
    })

    if department is None:
        return make_response(jsonify({
            'Error': 'The specified department does not exist.'
        }), 400)

    role = roles.find_one({
        'role_id': data['role_id'].strip()
    })

    if role is None:
        return make_response(jsonify({
            'Error': 'The specified job role does not exist.'
        }), 400)

    existing_employee = employees.find_one({
        '$or': [
            {'employee_id': data['employee_id'].strip()},
            {'email': email}
        ]
    })

    if existing_employee:
        return make_response(jsonify({
            'Error': 'The employee ID or email is already registered.'
        }), 409)

    employee = {
        'employee_id': data['employee_id'].strip(),
        'first_name': data['first_name'].strip(),
        'last_name': data['last_name'].strip(),
        'email': email,
        'phone': data.get('phone') or None,
        'date_of_birth': data.get('date_of_birth') or None,
        'hire_date': hire_date.isoformat(),
        'department_id': data['department_id'].strip(),
        'role_id': data['role_id'].strip(),
        'status': 'Active',
        'employment_type': data.get('employment_type', "Permanent")
    }

    try:
        employees.insert_one(employee)
    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'An employee with these unique details already exists.'
        }), 409)
    
    new_employee = employees.find_one({
        'employee_id' : data['employee_id']
    })
    new_employee['_id'] = str(new_employee['_id'])
    
    return make_response(jsonify({
        'message': 'Employee created successfully.',
        'data': new_employee
    }), 201)

#route to update  employee

@employee_bp.route('/api/v1.0/employees/<string:employee_id>', methods=['PUT'])
@jwt_required
def update_employee(employee_id):

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'Error': 'Employee not found.'
        }), 404)

    data = request.form.to_dict()

    if not data:
        return make_response(jsonify({
            'Error': 'No data was provided.'
        }), 400)

    allowed_fields = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'date_of_birth',
        'street',
        'city',
        'postcode',
        'country'
        
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

    if 'email' in data:
        email = data['email']

        if '@' not in email or '.' not in email.rsplit('@', 1)[-1]:
            return make_response(jsonify({
                'Error': 'Please provide a valid email address.'
            }), 400)

        existing_email = employees.find_one({
            'email': email,
            'employee_id': {'$ne': employee_id}
        })

        if existing_email:
            return make_response(jsonify({
                'Error': 'This email address is already registered.'
            }), 409)



    if data.get('date_of_birth') is not None:
        try:
            date.fromisoformat(data['date_of_birth'])
        except ValueError:
            return make_response(jsonify({
                'Error': 'Date of birth must use YYYY-MM-DD format.'
            }), 400)


    try:
        employees.update_one(
            {'employee_id': employee_id},
            {'$set': data}
        )

    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'The update conflicts with existing employee information.'
        }), 409)

    updated_employee = employees.find_one(
        {'employee_id': employee_id},
        {'_id': 0}
    )

    return make_response(jsonify({
        'Message': 'Employee information updated successfully.',
        'Employee': updated_employee
    }), 200)

#route to delete an employee

@employee_bp.route('/api/v1.0/employees/<employee_id>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_employee(employee_id):

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'Error': 'Employee not found.'
        }), 404)

    result = employees.delete_one({
        'employee_id': employee_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Employee could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'Employee deleted successfully.'
    }), 200)