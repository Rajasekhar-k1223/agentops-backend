# db_mongo.py

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.agentops

def insert_log(task_id, data):
    db.task_logs.insert_one({"task_id": task_id, **data})

def get_logs_by_task(task_id):
    return list(db.task_logs.find({"task_id": task_id}))
