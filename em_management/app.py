from flask import Flask, make_response,jsonify, request
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client.employees
employees = db.employee


#Route for welcoming 
@app.route("/", methods = ["GET"])
def index():
    return make_response("<h1>Welcome to Employee Management </h1>", 200)

#route to get all the json data
@app.route("/api/employees", methods = ["GET"])
def show_all_employees():
    page_num , page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))

    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
        
    page_start = (page_size* (page_num - 1))
    
    data_to_return = []
    
    for employee in employees.find().skip(page_start).limit(page_size):
            employee['_id'] = str(employee['_id'])
            for review in employee['reviews']:
                review['id'] = str(review['id'])
                
            data_to_return.append(employee)
    return make_response(jsonify(data_to_return),200)




if __name__ == "__main__":
    app.run(debug=True)