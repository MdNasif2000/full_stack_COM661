from flask import Flask, make_response,jsonify, request
app = Flask(__name__)

businesses =[
    {
        "id" : 1,
        "name" : "Costa",
        "town" : "London",
        "rating" : 4,
        "reviews" :[
            {
                "id": 1 ,
                "username" :"Nasif",
                "comment" : "Not Bad!",
                "stars": 4,
            }
        ]
    },
    {
        "id" : 2,
        "name" : "Black-Sheep",
        "town" : "London",
        "rating" : 4,
        "reviews" :[]
    },
    {
        "id" : 3,
        "name" : "Nero",
        "town" : "London",
        "rating" : 4,
        "reviews" :[]
    },
    {
        "id" : 3,
        "name" : "Nero",
        "town" : "London",
        "rating" : 4,
        "reviews" :[]
    },
    
]

#Route for welcoming 
@app.route("/", methods = ["GET"])
def index():
    return make_response("<h1>Welcome to Flask </h1>", 200)

#route to get the json data
@app.route("/api/v1.0/businesses", methods = ["GET"])
def show_all_businesses():
    return make_response(jsonify(businesses),200)

#fetch data by ID
@app.route("/api/v1.0/businesses/<int:biz_id>", methods = ["GET"])
def show_one_business(biz_id):
    data_to_return = [
        business for business in businesses
            if business["id"] == biz_id ]
    return make_response(jsonify(data_to_return[0]),200)
    
    
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
    if len(businesses) ==0:
        next_id = 1
        
    else:
        next_id = businesses[-1]["id"] + 1
    
    new_business= {
        "id" : next_id,
        "name" : request.form["name"],
        "town" : request.form["town"],
        "rating" : request.form["rating"],
        "reviews" : [],
    }
    
    businesses.append(new_business)
    
    return make_response(jsonify(new_business),201)

#editing business by id by PUT
@app.route("/api/v1.0/businesses/<int:biz_id>",methods =["PUT"])
def edit_business(biz_id):
    for business in businesses:
        if business['id'] == biz_id:
            business['name'] = request.form['name']
            business['town'] = request.form['town']
            business['rating'] = request.form['rating']
            break
    return make_response(jsonify(business),200)

#delete an instance by id by DELETE
@app.route("/api/v1.0/businesses/<int:biz_id>",methods =["DELETE"])
def delete_business(biz_id):
    for business in businesses:
        if business['id'] == biz_id:
            businesses.remove(business)
            break
    return make_response(jsonify({"Message":"Business Deleted Successfully !"}),200)

#=========REVIEWS==============

#getting the review by id by ID by GET
@app.route("/api/v1.0/businesses/<int:biz_id>/reviews",methods=['GET'])
def get_review(biz_id):
    for business in businesses:
        if business['id'] == biz_id:
            
            break
        
    return make_response(jsonify(business["reviews"]),200)

#creating the new review by POST
@app.route("/api/v1.0/businesses/<int:biz_id>/reviews", methods=['POST'])
def add_new_review(biz_id):
    for business in businesses:
        if business['id'] == biz_id:
            if len(business["reviews"]) == 0:
                new_review_id =1
                
            else:
                new_review_id = business["reviews"][-1]["id"] + 1
                
            new_review = {
                "id" : new_review_id,
                "username" : request.form['username'],
                "comment": request.form['comment'],
                "stars": request.form['stars'],
            }
            business["reviews"].append(new_review)
            break
        
    return make_response(jsonify(new_review),200)
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
    
if __name__ == "__main__":
    app.run(debug=True)
    
