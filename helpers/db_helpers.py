import os
from pymongo import MongoClient

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['extremeAccountability']  
config_collection = db['creds']
recipients_collection = db['recipients']

ENV=os.getenv("ENV")

def get_creds_from_db():
    doc = config_collection.find_one({"user": "jordan"})
    return doc


def update_strava_tokens_in_db(new_access_token, new_refresh_token, expires_at):
    config_collection.update_one(
        {"user": "jordan"},
        {"$set": {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "access_token_expires_at": expires_at
        }},
        upsert=True
    )


def get_refresh_token_from_db():
    doc = config_collection.find_one({"user": "jordan"})
    if doc and 'refresh_token' in doc:
        return doc['refresh_token']
    raise Exception("No refresh token found in MongoDB.")


def save_refresh_token_to_db(new_token):
    config_collection.update_one(
        {"user": "jordan"},
        {"$set": {"refresh_token": new_token}},
        upsert=True
    )


def get_email_recipients_from_db():
    if ENV == "dev":
        return list(
            recipients_collection.find(
                {"user": "jordan", "dev": True}, 
                {"_id": 0, "email": 1, "first_name": 1}
            )
        )
    
    return list(
        recipients_collection.find(
            {"user": "jordan"}, 
            {"_id": 0, "email": 1, "first_name": 1}
        )
    )
  
