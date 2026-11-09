from flask import Flask, make_response

from auth.auth import auth_bp
from employees.employees import employee_bp
from departments.departments import department_bp
from roles.roles import role_bp
from attendance.attendance import attendance_bp
from leaves.leaves import leave_bp
from admin.admin import admin_bp
from analytics.analytics import analytics_bp


app = Flask(__name__)


# Register all Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(department_bp)
app.register_blueprint(role_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(leave_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(analytics_bp)


# Welcome route
@app.route("/", methods=["GET"])
def index():

    return make_response(
        "<h1>Welcome to Employee Management</h1>",
        200
    )


if __name__ == "__main__":
    app.run(debug=True)
