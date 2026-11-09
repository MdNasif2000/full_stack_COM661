from flask import Flask
from blueprint.businesses.businesses import business_bp
from review.review import review_bp
from auth.auth import auth_bp

app = Flask(__name__)

app.register_blueprint(business_bp)
app.register_blueprint(review_bp)
app.register_blueprint(auth_bp)


businesses = db.biz
users = db.users
blacklist_token = db.blacklist_token





# businesses =[
#     {
#         "id" : 1,
#         "name" : "Costa",
#         "town" : "London",
#         "rating" : 4,
#         "reviews" :[
#             {
#                 "id": 1 ,
#                 "username" :"Nasif",
#                 "comment" : "Not Bad!",
#                 "stars": 4,
#             }
#         ]
#     },
# ]

    
if __name__ == "__main__":
    app.run(debug=True)
    
