from flask import Flask,jsonify, make_response,jsonify, request
from pymongo import MongoClient
from bson import ObjectId
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
    return make_response("<h1>Welcome to Employee Management </h1>", 200)

#route to get all the json data
# @app.route("/api/employees", methods = ["GET"])
# def show_all_employees():
#     page_num , page_size = 1, 10
#     if request.args.get('pn'):
#         page_num = int(request.args.get('pn'))

#     if request.args.get('ps'):
#         page_size = int(request.args.get('ps'))
        
#     page_start = (page_size* (page_num - 1))
    
#     data_to_return = []
    
#     for employee in employees.find().skip(page_start).limit(page_size):
#             employee['_id'] = str(employee['_id'])
#             for review in employee['reviews']:
#                 review['id'] = str(review['id'])
                
#             data_to_return.append(employee)
#     return make_response(jsonify(data_to_return),200)


@app.route('/employees/<employee_id>/profile', methods=['GET'])
def get_employee_profile(employee_id):

    employee = employees.find_one({
        'employee_id': employee_id
    })

    if employee is None:
        return jsonify({
            'error': 'Employee not found'
        }), 404

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

    employee['_id'] = str(employee['_id'])

    if department:
        department['_id'] = str(department['_id'])

    if role:
        role['_id'] = str(role['_id'])

    for record in attendance_records:
        record['_id'] = str(record['_id'])

    for record in leave_records:
        record['_id'] = str(record['_id'])

    return jsonify({
        'employee': employee,
        'department': department,
        'job_role': role,
        'attendance': attendance_records,
        'leave_requests': leave_records
    }), 200



if __name__ == "__main__":
    app.run(debug=True)