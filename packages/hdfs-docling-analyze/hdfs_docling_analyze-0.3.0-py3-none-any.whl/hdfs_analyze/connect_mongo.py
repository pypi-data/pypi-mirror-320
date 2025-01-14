from pymongo import MongoClient
from pymongo.server_api import ServerApi

def connect_to_mongo(mongo_url: str, db_name: str, collection_name: str):
    uri = mongo_url
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        return False