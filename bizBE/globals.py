from pymongo import MongoClient


app.config['SECRET_KEY'] = 'mysecret'

#Mongo connection

client = MongoClient("mongodb://localhost:27017")
db = client.bizDB