from flask import Blueprint, make_response,jsonify, request
from bson import ObjectId
from functools import wraps
from decorators.decorators import jwt_required, admin_required
import globals

business_bp = Blueprint('business_bp', __name__)
businesses = globals.db.biz
#Route for welcoming 
@business_bp.route("/", methods = ["GET"])
def index():
    return make_response("<h1>Welcome to Flask </h1>", 200)

#route to get the json data
@app.route("/api/v1.0/businesses", methods = ["GET"])
@jwt_required
def show_all_businesses():
    page_num , page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))

    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
        
    page_start = (page_size* (page_num - 1))
    
    data_to_return = []
    
    for business in businesses.find().skip(page_start).limit(page_size):
            business['_id'] = str(business['_id'])
            for review in business['reviews']:
                review['id'] = str(review['id'])
                
            data_to_return.append(business)
    return make_response(jsonify(data_to_return),200)

#fetch data by ID
@app.route("/api/v1.0/businesses/<string:biz_id>", methods = ["GET"])
def show_one_business(biz_id):
    # data_to_return = [
    #     business for business in businesses
    #         if business["id"] == biz_id ]
    # return make_response(jsonify(data_to_return[0]),200)
    
    business = businesses.find_one({'_id':ObjectId(biz_id)})
    
    if business is not None:
        business['_id'] = str(business['_id'])
        
        # for review in business['reviews']:
        #     review['_id'] = str(review['_id'])
            
        return make_response(jsonify(business),200)
    else:
        return make_response(jsonify({"Error" : "Invalid business ID"}),404)
    
    
    
# @app.route("/api/v1.0/businesses/<int:biz_id>", methods = ["GET"])
# def show_one_business(biz_id):
#     data_to_return = [
#         business = for business in businesses
#             if business["id"] = biz_id ]
#       
#     return make_response(jsonify(data_to_return[0]),200

#adding new business by POST
@app.route("/api/v1.0/businesses", methods =["POST"])
def add_business():
    
    if "name" in request.form and \
        "town" in request.form and "rating" in request.form:
        new_business= {
            "name" : request.form["name"],
            "town" : request.form["town"],
            "rating" : request.form["rating"],
            "reviews" : [],
        }
        
        new_business_id = businesses.insert_one(new_business)
        
        new_business_link = "http://127.0.0.1:5000/api/v1.0/businesses/"\
            + str(new_business_id.inserted_id)
            
        return make_response(jsonify({"url" : new_business_link}),201)
    
    else:
        return make_response(jsonify({"url" : "Missing form data"}),404)
    
    # if len(businesses) ==0:
    #     next_id = 1
        
    # else:
    #     next_id = businesses[-1]["id"] + 1
    
    # new_business= {
    #     "id" : next_id,
    #     "name" : request.form["name"],
    #     "town" : request.form["town"],
    #     "rating" : request.form["rating"],
    #     "reviews" : [],
    # }
    
    # businesses.append(new_business)
    
    # return make_response(jsonify(new_business),201)

#editing business by id by PUT
@app.route("/api/v1.0/businesses/<string:biz_id>",methods =["PUT"])
def edit_business(biz_id):
    # for business in businesses:
    #     if business['id'] == biz_id:
    #         business['name'] = request.form['name']
    #         business['town'] = request.form['town']
    #         business['rating'] = request.form['rating']
    #         break
    # return make_response(jsonify(business),200)
    
    if "name" in request.form and "town" in request.form and "rating" in request.form:
        results = businesses.update_one(
            {"_id" : ObjectId(biz_id)},{
                "$set" : {
                    "name" : request.form["name"],
                    "town" : request.form["town"],
                    "rating" : request.form["rating"],
                }
            }
        )
        if results.matched_count == 1:
            edited_link = "http://127.0.0.1:5000/api/v1.0/businesses/" + biz_id
            
            return make_response(jsonify({"url": edited_link}),200)
        
        else:
            return make_response(jsonify({"Error" : "Invalid Business ID"}),404)
    else:
        return make_response(jsonify({"Error" : "Missing Form Data"}),404)

#delete an instance by id by DELETE
@app.route("/api/v1.0/businesses/<int:biz_id>",methods =["DELETE"])
def delete_business(biz_id):
    # for business in businesses:
    #     if business['id'] == biz_id:
    #         businesses.remove(business)
    #         break
    # return make_response(jsonify({"Message":"Business Deleted Successfully !"}),200)
    
    
    result = businesses.delete_one({"_id" : ObjectId(biz_id)})
    
    if result.deleted_count ==1:
        return make_response(jsonify({"Message" : "Business Deleted Successfully !"}),200)
    else:
        return make_response(jsonify({"Error" : "Invalid Business ID"}), 404)