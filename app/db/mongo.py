# app/db/mongo.py
from pymongo import MongoClient
from config import Config

def get_mongo_db():
    """Returns the MongoDB database object."""
    client = MongoClient(Config.MONGO_URI)
    return client[Config.MONGO_DB]