import os
from pymongo import MongoClient
from dotenv import load_dotenv
from modules_data import MODULES

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

added, updated = 0, 0
for m in MODULES:
    # find by id , if not found -- add
    result = db.modules.update_one({"id": m["id"]}, {"$set": m}, upsert=True)
    if result.upserted_id:
        added += 1
    else:
        updated += 1

print(f"Modules: {added} added, {updated} updated. Total in DB: {db.modules.count_documents({})}")