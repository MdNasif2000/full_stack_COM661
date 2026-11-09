from flask import Blueprint, request, jsonify, make_response

from datetime import datetime

from database import attendance, employees

from decorators import jwt_required, admin_required


attendance_bp = Blueprint('attendance', __name__)

#route to get all attendances

@attendance_bp.route('/api/v1.0/attendances', methods=['GET'])
@jwt_required
@admin_required
def get_all_attendance():
    query = {}

    if request.args.get('employee_id'):
        query['employee_id'] = request.args.get('employee_id').strip()

    if request.args.get('date'):
        query['date'] = request.args.get('date').strip()

    if request.args.get('status'):
        status = request.args.get('status').strip()

        if status not in ['Present', 'Absent', 'Late']:
            return make_response(jsonify({
                'Error': 'Status must be Present, Absent or Late'
            }), 400)

        query['status'] = status

    data_to_return = []

    for record in attendance.find(query).sort('date', -1):
        record['_id'] = str(record['_id'])
        data_to_return.append(record)

    return make_response(jsonify(data_to_return), 200)

#route to get one attendance

@attendance_bp.route('/api/v1.0/attendances/<string:attendance_id>', methods=['GET'])
@jwt_required
@admin_required
def get_one_attendance(attendance_id):
    record = attendance.find_one({
        'attendance_id': attendance_id
    })

    if record is None:
        return make_response(jsonify({
            'Error': 'Attendance record not found.'
        }), 404)

    record['_id'] = str(record['_id'])

    return make_response(jsonify(record), 200)

#route to add a attendance

@attendance_bp.route('/api/v1.0/attendances', methods=['POST'])
@jwt_required
@admin_required
def add_attendance():
    data = request.form

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    required_fields = [
        'attendance_id',
        'employee_id',
        'date',
        'status'
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

    attendance_id = data['attendance_id'].strip()
    employee_id = data['employee_id'].strip()
    attendance_date = data['date'].strip()
    status = data['status'].strip()

    check_in = data.get('check_in', '').strip()
    check_out = data.get('check_out', '').strip()

    try:
        datetime.strptime(attendance_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'Date must use YYYY-MM-DD format.'
        }), 400)

    if check_in:
        try:
            datetime.strptime(check_in, '%H:%M')
        except ValueError:
            return make_response(jsonify({
                'Error': 'Check-in time must use HH:MM format.'
            }), 400)

    if check_out:
        try:
            datetime.strptime(check_out, '%H:%M').time()
        except ValueError:
            return make_response(jsonify({
                'Error': 'Check-out time must use HH:MM format.'
            }), 400)

    if check_out and not check_in:
        return make_response(jsonify({
            'Error': 'Check-in time is required to check-out .'
        }), 400)

    if check_in and check_out and check_out <= check_in:
        return make_response(jsonify({
            'Error': 'Check-out time must be later than check-in time.'
        }), 400)

    if status not in ['Present', 'Absent', 'Late']:
        return make_response(jsonify({
            'Error': 'Status must be Present, Absent or Late.'
        }), 400)

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'Error': 'Employee not found.'
        }), 404)

    if attendance.find_one({'attendance_id': attendance_id}):
        return make_response(jsonify({
            'Error': 'This attendance ID already exists.'
        }), 409)

    existing_record = attendance.find_one({
        'employee_id': employee_id,
        'date': attendance_date
    })

    if existing_record:
        return make_response(jsonify({
            'Error': 'Attendance for this employee on this date already exists.'
        }), 409)

    record = {
        'attendance_id': attendance_id,
        'employee_id': employee_id,
        'date': attendance_date,
        'check_in': check_in or None,
        'check_out': check_out or None,
        'status': status
    }

    attendance.insert_one(record)

    new_record = attendance.find_one({
        'attendance_id': attendance_id
    })

    new_record['_id'] = str(new_record['_id'])

    return make_response(jsonify({
        'Message': 'Attendance record created successfully.',
        'Attendance': new_record
    }), 201)

#route to update an attendance

@attendance_bp.route('/api/v1.0/attendances/<string:attendance_id>', methods=['PUT'])
@jwt_required
@admin_required
def update_attendance(attendance_id):
    record = attendance.find_one({
        'attendance_id': attendance_id
    })

    if record is None:
        return make_response(jsonify({
            'Error': 'Attendance record not found.'
        }), 404)

    data = request.form.to_dict()

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    allowed_fields = [
        'employee_id',
        'date',
        'check_in',
        'check_out',
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

    for field in data:
        data[field] = data[field].strip()

    employee_id = data.get('employee_id', record['employee_id'])

    if not employee_id:
        return make_response(jsonify({
            'Error': 'Employee ID cannot be empty.'
        }), 400)

    if 'employee_id' in data:
        employee = employees.find_one({
            'employee_id': employee_id
        })

        if employee is None:
            return make_response(jsonify({
                'Error': 'Employee not found.'
            }), 404)

    attendance_date = data.get('date', record['date'])

    if not attendance_date:
        return make_response(jsonify({
            'Error': 'Date cannot be empty.'
        }), 400)

    try:
        datetime.strptime(attendance_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'Date must use YYYY-MM-DD format.'
        }), 400)

    check_in = data.get('check_in', record.get('check_in'))

    if check_in:
        try:
            datetime.strptime(check_in, '%H:%M')
        except ValueError:
            return make_response(jsonify({
                'Error': 'Check-in time must use HH:MM format.'
            }), 400)

    check_out = data.get('check_out', record.get('check_out'))

    if check_out:
        try:
            datetime.strptime(check_out, '%H:%M')
        except ValueError:
            return make_response(jsonify({
                'Error': 'Check-out time must use HH:MM format.'
            }), 400)

    if check_out and not check_in:
        return make_response(jsonify({
            'Error': 'Check-in time is required when check-out time is provided.'
        }), 400)

    if check_in and check_out and check_out <= check_in:
        return make_response(jsonify({
            'Error': 'Check-out time must be later than check-in time.'
        }), 400)

    status = data.get('status', record['status'])

    if status not in ['Present', 'Absent', 'Late']:
        return make_response(jsonify({
            'Error': 'Status must be Present, Absent or Late.'
        }), 400)

    existing_record = attendance.find_one({
        'employee_id': employee_id,
        'date': attendance_date,
        'attendance_id': {'$ne': attendance_id}
    })

    if existing_record:
        return make_response(jsonify({
            'Error': 'Attendance for this employee on this date already exists.'
        }), 409)

    attendance.update_one(
        {'attendance_id': attendance_id},
        {'$set': data}
    )

    updated_record = attendance.find_one({
        'attendance_id': attendance_id
    })

    updated_record['_id'] = str(updated_record['_id'])

    return make_response(jsonify({
        'Message': 'Attendance record updated successfully.',
        'Attendance': updated_record
    }), 200)

#route to delete an attendance

@attendance_bp.route('/api/v1.0/attendances/<string:attendance_id>', methods=['DELETE'])
@jwt_required
@admin_required
def delete_attendance(attendance_id):
    record = attendance.find_one({
        'attendance_id': attendance_id
    })

    if record is None:
        return make_response(jsonify({
            'Error': 'Attendance record not found.'
        }), 404)

    result = attendance.delete_one({
        'attendance_id': attendance_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Attendance record could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'Attendance record deleted successfully.'
    }), 200)