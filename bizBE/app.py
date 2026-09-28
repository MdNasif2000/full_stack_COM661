from flask import Flask, make_response,jsonify, request
app = Flask(__name__)

businesses =[
    {
        "id" : 1,
        "name" : "Costa",
        "town" : "London",
        "rating" : 4,
        "reviews" :[]
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
#     return make_response(jsonify(data_to_return[0]),200)

@app.route("/api/v1.0/businesses", methods =["POST"])
def add_business():
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
    
if __name__ == "__main__":
    app.run(debug=True)