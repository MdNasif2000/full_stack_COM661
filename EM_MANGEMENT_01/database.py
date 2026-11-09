from pymongo import MongoClient


# MongoDB connection
client = MongoClient("mongodb://localhost:27017")

# Database
db = client.em_management


# Collections
employees = db.employees
departments = db.departments
roles = db.roles
attendance = db.attendance
leave_requests = db.leave_requests
users = db.users
blacklist_token = db.blacklist_token