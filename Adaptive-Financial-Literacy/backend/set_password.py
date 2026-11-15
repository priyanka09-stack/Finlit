import os
import re
import sys

from dotenv import load_dotenv
from pymongo import MongoClient

from auth import hash_password

load_dotenv()

if len(sys.argv) != 3:
    print("Usage: python set_password.py <email> <new_password>")
    sys.exit(1)

email, password = sys.argv[1].strip().lower(), sys.argv[2]
if len(password) < 6:
    print("Password must be at least 6 characters")
    sys.exit(1)

db = MongoClient(os.getenv("MONGO_URI"))[os.getenv("DB_NAME")]
pattern = {"$regex": f"^{re.escape(email)}$", "$options": "i"}
result = db.students.update_one(
    {"email": pattern},
    {"$set": {"password_hash": hash_password(password), "email": email}},
)
print("Password set." if result.matched_count else "No student found with that email.")