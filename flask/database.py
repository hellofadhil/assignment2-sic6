import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set! Please check your .env file.")

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client["mydatabase"]  # Adjust this to your actual database name

# Ensure db is available for import
__all__ = ["db"]
