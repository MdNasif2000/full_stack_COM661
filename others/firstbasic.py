name = input("Whats is your name ? \n")
age = int(input("How old are you ? \n"))

if  32 > age >= 18 :
    print(f"Hello {name} ! Welcome Aboard \n You are an Adult !")

elif age < 18:
    print(f"Hello {name} ! Welcome Aboard \n You are Teenager !")
else:
    print(f"Hello {name} ! Welcome Aboard \n You are Old enough now !")
    
    
for _ in name:
    print( _ , end="_")
    
def future_age(years: int):
    print(f"\nAfter {years} year/years you will be {years + age} year's old. You grew up !!!")

future_age(20)
future_age(30)

























# Route to update employee information (Admin only)
@app.route('/api/v1.0/admin/employees/<string:employee_id>', methods=['PUT'])
def admin_update_employee(employee_id):

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

    if 'date_of_birth' in data:
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