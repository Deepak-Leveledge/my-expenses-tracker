# import asyncio
# from db import expenses_collection   # ← yahi file tumne banayi thi
# from bson import ObjectId


# async def test_mongodb():
#     print("---- TESTING MONGODB CONNECTION ----")

#     # 1. Insert test expense (new schema)
#     sample_expense = {
#         "date": "2025-02-01",
#         "amount": 250,
#         "category": "Food",
#         "subcategory": "Lunch",
#         "note": "Testing MongoDB entry",
#         "payment_method": "gpay",    # NEW FIELD
#     }

#     result = await expenses_collection.insert_one(sample_expense)
#     print("Inserted ID:", result.inserted_id)

#     # 2. Fetch the same entry
#     inserted_id = result.inserted_id
#     data = await expenses_collection.find_one({"_id": ObjectId(inserted_id)})

#     print("Fetched Document:")
#     print(data)

#     # # 3. Clean test record (optional)
#     # await expenses_collection.delete_one({"_id": ObjectId(inserted_id)})
#     # print("Test record deleted (cleanup).")

#     print("---- TEST SUCCESS ----")


# # Run the test
# asyncio.run(test_mongodb())
