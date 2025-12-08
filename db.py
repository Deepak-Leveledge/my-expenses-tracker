# import os
# from motor.motor_asyncio import AsyncIOMotorClient
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URL = os.getenv("MONGO_DB_URL")
# DB_NAME = os.getenv("DB_NAME", "knowledge_assistant")

# if not MONGO_URL:
#     raise Exception("ERROR: MONGO_URL is missing in .env file")

# client = AsyncIOMotorClient(MONGO_URL)
# db = client[DB_NAME]

# expenses_collection = db["expenses"]

# print(f"Connected to MongoDB database: {DB_NAME}")



import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME", "knowledge_assistant")

if not MONGO_URL:
    raise Exception("ERROR: MONGO_URL is missing in .env file")

# Global variables for lazy initialization
_client = None
_db = None
_expenses_collection = None


def get_client():
    """Lazy initialization of MongoDB client"""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client


def get_db():
    """Get database instance"""
    global _db
    if _db is None:
        client = get_client()
        _db = client[DB_NAME]
    return _db


def get_expenses_collection():
    """Get expenses collection"""
    global _expenses_collection
    if _expenses_collection is None:
        db = get_db()
        _expenses_collection = db["expenses"]
    return _expenses_collection


# Proxy class that delays initialization until first use
class CollectionProxy:
    """Proxy that forwards all attribute access to the real collection"""
    def __getattr__(self, name):
        collection = get_expenses_collection()
        return getattr(collection, name)


# Export the proxy - it won't create the client until actually used
expenses_collection = CollectionProxy()