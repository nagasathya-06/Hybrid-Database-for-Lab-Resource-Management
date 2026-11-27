# config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY     = os.getenv("SECRET_KEY", "dev-secret-key")
    # PostgreSQL
    DB_HOST        = os.getenv("DB_HOST")
    DB_PORT        = os.getenv("DB_PORT")
    DB_NAME        = os.getenv("DB_NAME")
    DB_USER        = os.getenv("DB_USER")
    DB_PASSWORD    = os.getenv("DB_PASSWORD")
    # MongoDB
    MONGO_URI      = os.getenv("MONGO_URI")
    MONGO_DB       = os.getenv("MONGO_DB")