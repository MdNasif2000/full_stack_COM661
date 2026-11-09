from flask import Blueprint, make_response,jsonify, request
from bson import ObjectId
from decorators.decorators import jwt_required, admin_required
import globals

review_bp = Blueprint('review_bp',__name__)


#=========REVIEWS==============

#getting the review by id by ID by GET
@review_bp.route("/api/v1.0/businesses/<string:biz_id>/reviews",methods=['GET'])
def get_review(biz_id):
    for business in businesses:
        if business['_id'] == biz_id:
            
            break
        
    return make_response(jsonify(business["reviews"]),200)

#creating the new review by POST
@app.route("/api/v1.0/businesses/<string:biz_id>/reviews", methods=['POST'])
def add_new_review(biz_id):
    # for business in businesses:
    #     if business['id'] == biz_id:
    #         if len(business["reviews"]) == 0:
    #             new_review_id =1
                
    #         else:
    #             new_review_id = business["reviews"][-1]["id"] + 1
                
    #         new_review = {
    #             "id" : new_review_id,
    #             "username" : request.form['username'],
    #             "comment": request.form['comment'],
    #             "stars": request.form['stars'],
    #         }
    #         business["reviews"].append(new_review)
    #         break
        
    # return make_response(jsonify(new_review),200)
    
    
    
    new_review = {
    "_id" : ObjectId(),
    "username" : request.form['username'],
    "comment": request.form['comment'],
    "stars": request.form['stars'],
    }
    
    businesses.update_one({"_id" : ObjectId(biz_id)},{"$push" : {"reviews": new_review}})
    
    new_review_link = "http://127.0.0.1:5000/api/v1.0/businesses/" + biz_id +"/reviews" + str(new_review["_id"])
    return make_response(jsonify({"url" : new_review_link}),201)
  
    
#getting the review by ID by GET method
@app.route("/api/v1.0/businesses/<int:biz_id>/reviews/<int:rev_id>",methods=['GET'])
def get_one_review(biz_id , rev_id):
    for business in businesses:
        if business['id'] == biz_id:
            for review in business["reviews"]:
                if review["id"] == rev_id :
                    break
            break
        
    return make_response(jsonify(review),200)

#route to update review by its ID
@app.route("/api/v1.0/businesses/<int:biz_id>/reviews/<int:rev_id>",methods=['PUT'])
def update_review(biz_id , rev_id):
    for business in businesses:
        if business['id'] == biz_id:
            for review in business["reviews"]:
                if review["id"] == rev_id :
                    review["username"] = request.form["username"]
                    review["comment"] = request.form["comment"]
                    review["stars"] = request.form["stars"]
                    break
            break
        
    return make_response(jsonify(review),200)
#route to delete the review by its ID
@app.route("/api/v1.0/businesses/<int:biz_id>/reviews/<int:rev_id>",methods=['DELETE'])
def delete_review(biz_id , rev_id):
    for business in businesses:
        if business['id'] == biz_id:
            for review in business["reviews"]:
                if review["id"] == rev_id :
                    business["reviews"].remove(review)
                    break
            break
        
    return make_response(jsonify({"Message":"Review deleted successfully !"}),200)