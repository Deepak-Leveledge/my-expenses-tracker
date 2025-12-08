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

# Load environment variables
MONGO_URL = os.getenv("MONGO_DB_URL")
DB_NAME = os.getenv("DB_NAME", "knowledge_assistant")

if not MONGO_URL:
    # For local development, try loading from .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        MONGO_URL = os.getenv("MONGO_DB_URL")
        if not MONGO_URL:
            raise Exception("ERROR: MONGO_DB_URL is missing in environment variables")
    except ImportError:
        raise Exception("ERROR: MONGO_DB_URL is missing in environment variables")

# DON'T create client at module level!
# Create it inside async functions instead


async def get_expenses_collection():
    """
    Get MongoDB collection.
    Creates a new client each time - this is fine for serverless.
    """
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    return db["expenses"]


# Proxy class that creates connection on each access
class AsyncCollectionProxy:
    """
    Proxy that creates a fresh Motor client for each operation.
    This avoids the 'already running asyncio' error in Lambda.
    """
    
    async def _get_collection(self):
        return await get_expenses_collection()
    
    # Proxy common collection methods
    async def insert_one(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.insert_one(*args, **kwargs)
    
    def find(self, *args, **kwargs):
        """
        find() returns a cursor immediately (synchronous),
        but the cursor operations are async
        """
        class FindProxy:
            def __init__(self, filter_query, *args, **kwargs):
                self.filter_query = filter_query
                self.args = args
                self.kwargs = kwargs
                self._sort_spec = None
            
            def sort(self, *args, **kwargs):
                self._sort_spec = (args, kwargs)
                return self
            
            async def to_list(self, length):
                col = await get_expenses_collection()
                cursor = col.find(self.filter_query, *self.args, **self.kwargs)
                if self._sort_spec:
                    cursor = cursor.sort(*self._sort_spec[0], **self._sort_spec[1])
                return await cursor.to_list(length)
        
        return FindProxy(*args, **kwargs)
    
    async def find_one(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.find_one(*args, **kwargs)
    
    async def update_one(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.update_one(*args, **kwargs)
    
    async def update_many(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.update_many(*args, **kwargs)
    
    async def delete_one(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.delete_one(*args, **kwargs)
    
    async def delete_many(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.delete_many(*args, **kwargs)
    
    async def count_documents(self, *args, **kwargs):
        col = await self._get_collection()
        return await col.count_documents(*args, **kwargs)
    
    def aggregate(self, *args, **kwargs):
        """Aggregate returns a cursor"""
        class AggregateCursor:
            def __init__(self, pipeline, *args, **kwargs):
                self.pipeline = pipeline
                self.args = args
                self.kwargs = kwargs
            
            async def to_list(self, length):
                col = await get_expenses_collection()
                cursor = col.aggregate(self.pipeline, *self.args, **self.kwargs)
                return await cursor.to_list(length)
        
        return AggregateCursor(*args, **kwargs)


# Export the proxy
expenses_collection = AsyncCollectionProxy()