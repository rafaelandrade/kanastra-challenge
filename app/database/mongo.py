from pymongo import MongoClient
from app.config import config

MONGO_URL = config.get('MONGO_URL')
MONGO_DB = config.get('MONGO_DB')

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB]
