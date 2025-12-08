import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME", "knowledge_assistant")

if not MONGO_URL:
    raise Exception("ERROR: MONGO_URL is missing in .env file")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

expenses_collection = db["expenses"]

# print(f"Connected to MongoDB database: {DB_NAME}")
