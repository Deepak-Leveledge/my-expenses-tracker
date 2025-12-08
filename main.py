from mcp.server.fastmcp import FastMCP
from db import expenses_collection   # ← new MongoDB file
from bson import ObjectId
import datetime


import asyncio
import threading
import os
from dateutil import parser
from typing import Optional
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "category.json")




mcp = FastMCP("Expenses-tracker-mcp-server")


from dateutil import parser

def convert_date(date_str: str):
    """
    Convert ANY date format into ISO format YYYY-MM-DD.
    Auto-detects formats like:
    1-12-25, 01/12/2025, 2025-12-01, Dec 1 2025, etc.
    """
    try:
        # auto detect the date format
        dt = parser.parse(date_str, dayfirst=True)  
        return dt.strftime("%Y-%m-%d")  # return ISO format
    except Exception:
        raise ValueError(f"Invalid date format: {date_str}")


# ------------------------- ADD EXPENSE -------------------------
@mcp.tool()
async def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
    payment_method: str = "cash"  # NEW FIELD
):
    """Add a new expense entry to MongoDB."""
    try:
        expense = {
            "date": convert_date(date),
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "note": note,
            "payment_method": payment_method,
            "created_at": datetime.datetime.now()
        }

        result = await expenses_collection.insert_one(expense)

        return {
            "status": "success",
            "id": str(result.inserted_id),
            "message": "Expense added successfully"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ------------------------- GET ALL -------------------------
@mcp.tool()
async def get_all_expenses():
    """Retrieve all expenses."""
    try:
        cursor = expenses_collection.find().sort("date", 1)
        data = await cursor.to_list(None)

        # Convert ObjectId to str
        for d in data:
            d["id"] = str(d["_id"])
            del d["_id"]

        return data

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ------------------------- DATE RANGE -------------------------
@mcp.tool()
async def list_expenses_by_date(start_date: str, end_date: str):
    """List expenses between dates."""



    try:

        start = convert_date(start_date)
        end = convert_date(end_date)


        cursor = expenses_collection.find({
            "date": {"$gte": start, "$lte": end}
        }).sort("date", 1)

        data = await cursor.to_list(None)

        for d in data:
            d["id"] = str(d["_id"])
            del d["_id"]

        return data

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ------------------------- SUMMARY -------------------------
@mcp.tool()
async def summarize(start_date: str, end_date: str, category: Optional[str] = None):
    """Summarize expenses by category."""


    start = convert_date(start_date)
    end = convert_date(end_date)

    match_stage = {
        "date": {"$gte": start, "$lte": end}
    }

    if category in (None,"","null"):
        category = None

    if category:
        match_stage["category"] = category

    pipeline = [
        {"$match": match_stage},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"_id": 1}}
    ]

    try:
        results = await expenses_collection.aggregate(pipeline).to_list(None)

        return [
            {"category": r["_id"], "total_amount": r["total"]}
            for r in results
        ]

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ------------------------- DELETE BY ID -------------------------
# @mcp.tool()
# async def delete_expense_by_id(expense_id: str):
#     """Delete an expense by its ID (MongoDB ObjectId)."""
#     try:
#         result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})

#         if result.deleted_count == 0:
#             return {"status": "error", "message": "No expense found."}

#         return {"status": "success", "message": "Expense deleted."}

#     except Exception as e:
#         return {"status": "error", "message": str(e)}

# ------------------------- UPDATE -------------------------

# Helper function to build filter query for update_expense_smart and easy
def filter_the_expenses(date=None, amount=None, category=None, subcategory=None, note=None, payment_method=None):
    f = {}

    if date: f["date"] = convert_date(date)
    if amount: f["amount"] = amount
    if category: f["category"] = category
    if subcategory: f["subcategory"] = subcategory
    if note: f["note"] = note
    if payment_method: f["payment_method"] = payment_method

    return f


@mcp.tool()
async def update_expense(
    date: Optional[str] = None,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    note: Optional[str] = None,
    payment_method: Optional[str] = None,

    new_date: Optional[str] = None,
    new_amount: Optional[float] = None,
    new_category: Optional[str] = None,
    new_subcategory: Optional[str] = None,
    new_note: Optional[str] = None,
    new_payment_method: Optional[str] = None
):
    """
    Update an expense WITHOUT requiring the ID.
    Finds matching expense(s) based on fields provided.
    """
 # Normalize null/empty inputs
    def normalize(v):
        return None if v in (None, "", "null", "None") else v

    date = normalize(date)
    category = normalize(category)
    subcategory = normalize(subcategory)
    note = normalize(note)
    payment_method = normalize(payment_method)

    new_date = normalize(new_date)
    new_category = normalize(new_category)
    new_subcategory = normalize(new_subcategory)
    new_note = normalize(new_note)
    new_payment_method = normalize(new_payment_method)

    # Build filter
    filter_query = {}

    if date:
        filter_query["date"] = convert_date(date)
    if amount is not None:
        filter_query["amount"] = amount
    if category:
        filter_query["category"] = category
    if subcategory:
        filter_query["subcategory"] = subcategory
    if note:
        filter_query["note"] = note
    if payment_method:
        filter_query["payment_method"] = payment_method

    if not filter_query:
        return {"status": "error", "message": "No fields provided to identify the expense."}

    # Find matching expenses
    matches = await expenses_collection.find(filter_query).to_list(None)

    if len(matches) == 0:
        return {"status": "error", "message": "No matching expenses found."}

    if len(matches) > 1:
        return {
            "status": "multiple",
            "message": "Multiple expenses match your filters.",
            "options": [
                {
                    "index": i,
                    "id": str(m["_id"]),
                    "date": m["date"],
                    "amount": m["amount"],
                    "category": m["category"],
                    "subcategory": m.get("subcategory", ""),
                    "note": m.get("note", ""),
                    "payment_method": m.get("payment_method", "")
                }
                for i, m in enumerate(matches)
            ]
        }

    # Only one match — safe to update
    target_id = matches[0]["_id"]

    update_fields = {}

    if new_date:
        update_fields["date"] = convert_date(new_date)
    if new_amount is not None:
        update_fields["amount"] = new_amount
    if new_category:
        update_fields["category"] = new_category
    if new_subcategory:
        update_fields["subcategory"] = new_subcategory
    if new_note:
        update_fields["note"] = new_note
    if new_payment_method:
        update_fields["payment_method"] = new_payment_method

    if not update_fields:
        return {"status": "error", "message": "No update fields provided."}

    await expenses_collection.update_one(
        {"_id": target_id},
        {"$set": update_fields}
    )

    return {"status": "success", "message": "Expense updated successfully"}


@mcp.prompt()
def welcome():
    return "You are an expert personal finance assistant. Help users track and manage their expenses effectively."

@mcp.prompt(title="Add Expense")
def add_expense_prompt()-> str:
    return (
        "To add a new expense, please provide the following details:\n"
        "- Date (YYYY-MM-DD)\n"
        "- Amount (e.g., 12.34)\n"
        "- Category (e.g., Food & Dining)\n"
        "- Subcategory (optional)\n"
        "- Note (optional)\n"
        "- Payment Method (e.g., cash, credit card, gpay)\n\n"
        "Example: 'Add an expense of 15.50 for Food & Dining on 2023-10-01 with note Lunch at cafe.'"
    )


@mcp.resource("expense:///categories", mime_type="application/json")  # Changed: expense:// → expense:///
def categories():
    try:
        # Provide default categories if file doesn't exist
        default_categories = {
            "categories": [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Bills & Utilities",
                "Healthcare",
                "Travel",
                "Education",
                "Business",
                "Other"
            ]
        }
        
        try:
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            import json
            return json.dumps(default_categories, indent=2)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    


if __name__ == "__main__":
    # Avoid nested asyncio.run errors when an event loop is already running
    import asyncio
    import threading

    def _run_server():
        mcp.run(transport="http", host="0.0.0.0", port=5000)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's an active loop (e.g., running inside an async environment),
            # start the server in a separate thread so asyncio.run can be used safely
            t = threading.Thread(target=_run_server, daemon=True)
            t.start()
            t.join()
        else:
            _run_server()
    except RuntimeError:
        # No running loop available, just run the server normally
        _run_server()