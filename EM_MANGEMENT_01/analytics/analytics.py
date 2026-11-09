from flask import Blueprint, request, jsonify, make_response

from datetime import datetime

from database import (
    employees,
    departments,
    attendance,
    leave_requests
)

from decorators import jwt_required, admin_required


analytics_bp = Blueprint('analytics', __name__)


#route for employee analytics

@analytics_bp.route('/api/v1.0/analytics/employee-count', methods=['GET'])
@jwt_required
@admin_required
def get_employee_count():
    total_employees = employees.count_documents({})

    active_employees = employees.count_documents({
        'status': 'Active'
    })

    inactive_employees = employees.count_documents({
        'status': 'Inactive'
    })

    return make_response(jsonify({
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees
    }), 200)

#route for employees in department

@analytics_bp.route('/api/v1.0/analytics/department-summary', methods=['GET'])
@jwt_required
@admin_required
def get_department_summary():
    pipeline = [
        {
            '$lookup': {
                'from': 'employees',
                'localField': 'department_id',
                'foreignField': 'department_id',
                'as': 'department_employees'
            }
        },
        {
            '$project': {
                '_id': 0,
                'department_id': 1,
                'name': 1,
                'employee_count': {
                    '$size': '$department_employees'
                }
            }
        },
        {
            '$sort': {
                'employee_count': -1
            }
        }
    ]

    summary = list(departments.aggregate(pipeline))

    return make_response(jsonify(summary), 200)


#route for attendance analytics

@analytics_bp.route('/api/v1.0/analytics/attendance-summary', methods=['GET'])
@jwt_required
@admin_required
def get_attendance_summary():
    query = {}

    if request.args.get('date'):
        attendance_date = request.args.get('date').strip()

        try:
            datetime.strptime(attendance_date, '%Y-%m-%d')
        except ValueError:
            return make_response(jsonify({
                'Error': 'Date must use YYYY-MM-DD format.'
            }), 400)

        query['date'] = attendance_date

    total_records = attendance.count_documents(query)

    pipeline = [
        {
            '$match': query
        },
        {
            '$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    status_counts = {}

    for result in attendance.aggregate(pipeline):
        status_counts[result['_id']] = result['count']

    return make_response(jsonify({
        'date': query.get('date', 'All dates'),
        'total_attendance_records': total_records,
        'status_summary': status_counts
    }), 200)

#route for leave request analytics

@analytics_bp.route('/api/v1.0/analytics/leave-summary', methods=['GET'])
@jwt_required
@admin_required
def get_leave_summary():
    query = {}

    if request.args.get('employee_id'):
        query['employee_id'] = request.args.get('employee_id').strip()

    total_requests = leave_requests.count_documents(query)

    status_pipeline = [
        {
            '$match': query
        },
        {
            '$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }
        }
    ]

    status_summary = {}

    for result in leave_requests.aggregate(status_pipeline):
        status_summary[result['_id']] = result['count']

    type_pipeline = [
        {
            '$match': query
        },
        {
            '$group': {
                '_id': '$leave_type',
                'count': {'$sum': 1}
            }
        }
    ]

    type_summary = {}

    for result in leave_requests.aggregate(type_pipeline):
        type_summary[result['_id']] = result['count']

    return make_response(jsonify({
        'employee_id': query.get('employee_id', 'All employees'),
        'total_leave_requests': total_requests,
        'status_summary': status_summary,
        'leave_type_summary': type_summary
    }), 200)