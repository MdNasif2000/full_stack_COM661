from flask import Flask,jsonify, make_response, request
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime,date,timedelta,timezone
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client.em_management
employees = db.employees
departments = db.departments
attendance = db.attendance
roles = db.job_roles
leave_requests = db.leave_requests



#Route for welcoming 
@app.route("/", methods = ["GET"])
def index():
    return make_response("<h1> Welcome to Employee Management </h1>", 200)


#route to get a employee profile
@app.route('/api/v1.0/employees/<string:employee_id>/profile', methods=['GET'])
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
@app.route('/api/v1.0/employees', methods =["GET"])
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
@app.route('/api/v1.0/employees/<string:employee_id>', methods= ["GET"])
def get_one_employee(employee_id):
    
    employee = employees.find_one({
        "employee_id": employee_id
    })
    
    if employee is not None and '_id' in employee:
        employee['_id'] = str(employee['_id'])
        return make_response(jsonify(employee),200)    

    else:
        return make_response(jsonify({'Error': 'Invalid Employee ID !'}), 404)    

#route to add a new employee
@app.route('/api/v1.0/employees', methods =["POST"])
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

    department = db.departments.find_one({
        'department_id': data['department_id'].strip()
    })

    if department is None:
        return make_response(jsonify({
            'Error': 'The specified department does not exist.'
        }), 400)

    role = db.roles.find_one({
        'role_id': data['role_id'].strip()
    })

    if role is None:
        return make_response(jsonify({
            'Error': 'The specified job role does not exist.'
        }), 400)

    existing_employee = db.employees.find_one({
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
        'status': 'Active'
    }

    try:
        db.employees.insert_one(employee)
    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'An employee with these unique details already exists.'
        }), 409)

    return make_response(jsonify({
        'message': 'Employee created successfully.',
        'data': employee
    }), 201)

#route to updating employee
@app.route('/api/v1.0/employees/<string:employee_id>', methods=['PUT'])
def update_employee(employee_id):

    employee = db.employees.find_one({
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
        'hire_date',
        'department_id',
        'role_id',
        'status'
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

        existing_email = db.employees.find_one({
            'email': email,
            'employee_id': {'$ne': employee_id}
        })

        if existing_email:
            return make_response(jsonify({
                'Error': 'This email address is already registered.'
            }), 409)

    if 'hire_date' in data:
        try:
            date.fromisoformat(data['hire_date'])
        except ValueError:
            return make_response(jsonify({
                'Error': 'Hire date must use YYYY-MM-DD format.'
            }), 400)

    if data.get('date_of_birth') is not None:
        try:
            date.fromisoformat(data['date_of_birth'])
        except ValueError:
            return make_response(jsonify({
                'Error': 'Date of birth must use YYYY-MM-DD format.'
            }), 400)

    if 'department_id' in data:
        department = db.departments.find_one({
            'department_id': data['department_id']
        })

        if department is None:
            return make_response(jsonify({
                'Error': 'The specified department does not exist.'
            }), 400)

    if 'role_id' in data:
        role = db.roles.find_one({
            'role_id': data['role_id']
        })

        if role is None:
            return make_response(jsonify({
                'Error': 'The specified job role does not exist.'
            }), 400)

    if 'status' in data:
        if data['status'] not in ['Active', 'Inactive']:
            return make_response(jsonify({
                'Error': 'Status must be Active or Inactive.'
            }), 400)

    try:
        db.employees.update_one(
            {'employee_id': employee_id},
            {'$set': data}
        )

    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'The update conflicts with existing employee information.'
        }), 409)

    updated_employee = db.employees.find_one(
        {'employee_id': employee_id},
        {'_id': 0}
    )

    return make_response(jsonify({
        'Message': 'Employee information updated successfully.',
        'Employee': updated_employee
    }), 200)

#route to delete an employee
@app.route('/api/v1/employees/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):

    employee = db.employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'Error': 'Employee not found.'
        }), 404)

    result = db.employees.delete_one({
        'employee_id': employee_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Employee could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'Employee deleted successfully.'
    }), 200)


#route to get all departments

@app.route('/api/v1.0/departments', methods= ['GET'])
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

@app.route('/api/v1.0/departments/<string:department_id>', methods = ['GET'])
def get_one_department(department_id):
    
    department = departments.find_one({
        'department_id' : department_id
    })
    if department is not None:
        department['_id'] = str(department['_id'])

        return make_response(jsonify(department),200)
    
    return make_response(jsonify({'Error' : 'Department Id is not valid  !'}),404)    

#route to add a department

@app.route('/api/v1.0/departments', methods=["POST"])
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

@app.route('/api/v1.0/departments/<string:department_id>', methods = ['PUT'])
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
        'Message':'Department updated successfully \n',
        'Department':updated_department
    }),200)    
    

#route to delete a department 

@app.route('/api/v1.0/departments/<string:department_id>', methods = ['DELETE'])
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
        
# Route to get all roles

@app.route('/api/v1.0/roles', methods=['GET'])
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

@app.route('/api/v1.0/roles/<string:role_id>', methods=['GET'])
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

@app.route('/api/v1.0/roles', methods=['POST'])
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

@app.route('/api/v1.0/roles/<string:role_id>', methods=['PUT'])
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

@app.route('/api/v1.0/roles/<string:role_id>', methods=['DELETE'])
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
    
if __name__ == "__main__":
    app.run(debug=True)