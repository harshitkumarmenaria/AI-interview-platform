from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "ai_interview_platform"

try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    print("✅ MongoDB connected successfully")
except ConnectionFailure:
    raise Exception("❌ Failed to connect to MongoDB")

db = client[DB_NAME]

users_col = db["users"]
resume_results_col = db["resume_results"]
interview_results_col = db["interview_results"]

# Ensure email uniqueness
users_col.create_index("email", unique=True)
