from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://localhost:27017/")
db = client.bizDB
users = db.users

user_list = [
    {
    'name' : 'Homer Simpson',
    'username' : 'homer',
    'password' : 'homer_s',
    'email' : 'homersimpson@com661.com',
    'admin' : True
    },
    {
    'name' : 'Simpson',
    'username' : 'simpson',
    'password' : 'simpson_s',
    'email' : 'simpson@com661.com',
    'admin' : False
    },
    {
    'name' : 'Homo Sapiens',
    'username' : 'homo',
    'password' : 'homo_s',
    'email' : 'homosapeins@com661.com',
    'admin' : False
    },
             ]

for new_user in user_list:
    new_user['password'] = bcrypt.hashpw(
        new_user['password'].encode('utf-8'),bcrypt.gensalt()
    )
    
    users.insert_one(new_user)