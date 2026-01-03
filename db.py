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
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME", "knowledge_assistant")

if not MONGO_URL:
    logger.error("ERROR: MONGO_DB_URL is missing in environment variables")
    logger.info("Please set MONGO_DB_URL environment variable")
    raise Exception("ERROR: MONGO_DB_URL is missing")

try:
    # Initialize MongoDB client
    client = AsyncIOMotorClient(
        MONGO_URL,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    
    db = client[DB_NAME]
    expenses_collection = db["expenses"]
    
    logger.info(f"MongoDB client initialized for database: {DB_NAME}")
    logger.info("Connection will be established on first query")
    
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise