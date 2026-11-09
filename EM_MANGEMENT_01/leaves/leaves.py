from flask import Blueprint, request, jsonify, make_response
from pymongo.errors import DuplicateKeyError
from datetime import datetime

from database import leave_requests, employees
from decorators import jwt_required, admin_required


leave_bp = Blueprint('leaves', __name__)


#route to get all leave requests 

@leave_bp.route('/api/v1.0/leaves', methods=['GET'])
@jwt_required
@admin_required
def get_all_leaves():
    query = {}

    if request.args.get('employee_id'):
        query['employee_id'] = request.args.get('employee_id').strip()

    if request.args.get('leave_type'):
        leave_type = request.args.get('leave_type').strip()

        if leave_type not in [
            'Annual Leave',
            'Sick Leave',
            'Personal Leave',
            'Unpaid Leave'
        ]:
            return make_response(jsonify({
                'Error': 'Invalid leave type.'
            }), 400)

        query['leave_type'] = leave_type

    if request.args.get('status'):
        status = request.args.get('status').strip()

        if status not in ['Pending', 'Approved', 'Rejected']:
            return make_response(jsonify({
                'Error': 'Status must be Pending, Approved or Rejected.'
            }), 400)

        query['status'] = status

    if request.args.get('start_date'):
        start_date = request.args.get('start_date').strip()

        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return make_response(jsonify({
                'Error': 'Start date must use YYYY-MM-DD format.'
            }), 400)

        query['start_date'] = start_date

    data_to_return = []

    for leave in leave_requests.find(query).sort('requested_at', -1):
        leave['_id'] = str(leave['_id'])
        data_to_return.append(leave)

    return make_response(jsonify(data_to_return), 200)    

#route to get one leave request

@leave_bp.route('/api/v1.0/leaves/<string:leave_id>', methods=['GET'])
@jwt_required
@admin_required
def get_one_leave(leave_id):
    leave = leave_requests.find_one({
        'leave_id': leave_id
    })

    if leave is None:
        return make_response(jsonify({
            'Error': 'Leave request not found.'
        }), 404)

    leave['_id'] = str(leave['_id'])

    return make_response(jsonify(leave), 200)

#route to add a leave request


@leave_bp.route('/api/v1.0/leaves', methods=['POST'])
@jwt_required
def add_leave():
    data = request.form

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    required_fields = [
        'leave_id',
        'employee_id',
        'leave_type',
        'start_date',
        'end_date',
        'reason'
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

    leave_id = data['leave_id'].strip()
    employee_id = data['employee_id'].strip()
    leave_type = data['leave_type'].strip()
    start_date = data['start_date'].strip()
    end_date = data['end_date'].strip()
    reason = data['reason'].strip()

    if leave_type not in [
        'Annual Leave',
        'Sick Leave',
        'Personal Leave',
        'Unpaid Leave'
    ]:
        return make_response(jsonify({
            'Error': 'Invalid leave type.'
        }), 400)

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'Start date must use YYYY-MM-DD format.'
        }), 400)

    try:
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'End date must use YYYY-MM-DD format.'
        }), 400)

    if end_date <= start_date:
        return make_response(jsonify({
            'Error': 'End date cannot be earlier than start date.'
        }), 400)

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return make_response(jsonify({
            'Error': 'Employee not found.'
        }), 404)

    if leave_requests.find_one({'leave_id': leave_id}):
        return make_response(jsonify({
            'Error': 'This leave ID already exists.'
        }), 409)

    leave = {
        'leave_id': leave_id,
        'employee_id': employee_id,
        'leave_type': leave_type,
        'start_date': start_date,
        'end_date': end_date,
        'reason': reason,
        'status': 'Pending',
        'requested_at': datetime.now().isoformat(timespec='seconds')
    }

    try:
        leave_requests.insert_one(leave)
    except DuplicateKeyError:
        return make_response(jsonify({
            'Error': 'This leave ID already exists.'
        }), 409)

    new_leave = leave_requests.find_one({
        'leave_id': leave_id
    })

    new_leave['_id'] = str(new_leave['_id'])

    return make_response(jsonify({
        'Message': 'Leave request submitted successfully.',
        'Leave': new_leave
    }), 201)

#route to update a leave request 


@leave_bp.route('/api/v1.0/leaves/<string:leave_id>', methods=['PUT'])
@jwt_required
def update_leave(leave_id):
    leave = leave_requests.find_one({
        'leave_id': leave_id
    })

    if leave is None:
        return make_response(jsonify({
            'Error': 'Leave request not found.'
        }), 404)

    data = request.form.to_dict()

    if not data:
        return make_response(jsonify({
            'Error': 'No form data was provided.'
        }), 400)

    allowed_fields = [
        'employee_id',
        'leave_type',
        'start_date',
        'end_date',
        'reason',
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

        if not data[field]:
            return make_response(jsonify({
                'Error': f'{field} cannot be empty.'
            }), 400)

    employee_id = data.get('employee_id', leave['employee_id'])

    if 'employee_id' in data:
        employee = employees.find_one({
            'employee_id': employee_id
        })

        if employee is None:
            return make_response(jsonify({
                'Error': 'Employee not found.'
            }), 404)

    leave_type = data.get('leave_type', leave['leave_type'])

    if leave_type not in [
        'Annual Leave',
        'Sick Leave',
        'Personal Leave',
        'Unpaid Leave'
    ]:
        return make_response(jsonify({
            'Error': 'Invalid leave type.'
        }), 400)

    status = data.get('status', leave['status'])

    if status not in ['Pending', 'Approved', 'Rejected']:
        return make_response(jsonify({
            'Error': 'Status must be Pending, Approved or Rejected.'
        }), 400)

    start_date = data.get('start_date', leave['start_date'])

    try:
        datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'Start date must use YYYY-MM-DD format.'
        }), 400)

    end_date = data.get('end_date', leave['end_date'])

    try:
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return make_response(jsonify({
            'Error': 'End date must use YYYY-MM-DD format.'
        }), 400)

    if end_date < start_date:
        return make_response(jsonify({
            'Error': 'End date cannot be earlier than start date.'
        }), 400)

    leave_requests.update_one(
        {'leave_id': leave_id},
        {'$set': data}
    )

    updated_leave = leave_requests.find_one({
        'leave_id': leave_id
    })

    updated_leave['_id'] = str(updated_leave['_id'])

    return make_response(jsonify({
        'Message': 'Leave request updated successfully.',
        'Leave': updated_leave
    }), 200)

#route to delete a leave request


@leave_bp.route('/api/v1.0/leaves/<string:leave_id>', methods=['DELETE'])
@jwt_required
def delete_leave(leave_id):
    leave = leave_requests.find_one({
        'leave_id': leave_id
    })

    if leave is None:
        return make_response(jsonify({
            'Error': 'Leave request not found.'
        }), 404)

    result = leave_requests.delete_one({
        'leave_id': leave_id
    })

    if result.deleted_count == 0:
        return make_response(jsonify({
            'Error': 'Leave request could not be deleted.'
        }), 500)

    return make_response(jsonify({
        'Message': 'Leave request deleted successfully.'
    }), 200)