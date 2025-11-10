from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

from pymongo import MongoClient, errors
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from bson.objectid import ObjectId

try:
    # Optional: load vars from .env if present
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional; continue without it if not installed
    pass


# Configuration

MONGODB_URI = os.getenv("MONGODB_URI", "7")
DB_NAME = os.getenv("DB_NAME", "book")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "cats")


# --------------------------- Database Helpers ---------------------------

def get_collection() -> Collection:
    """Create a Mongo client and return the target collection."""
    try:
        client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
        db = client[DB_NAME]
        coll = db[COLLECTION_NAME]
        # Ensure unique names for cats to simplify lookups & updates
        coll.create_index("name", unique=True)
        return coll
    except errors.ConfigurationError as e:
        sys.exit(f"[CONFIG ERROR] {e}")
    except errors.ConnectionFailure as e:
        sys.exit(f"[CONNECTION ERROR] {e}")
    except Exception as e:
        sys.exit(f"[UNEXPECTED ERROR] {e}")


# CRUD Operations

def list_all_cats(coll: Collection) -> List[Dict[str, Any]]:
    """List and return all cat documents in the collection."""
    try:
        return list(coll.find({}))
    except errors.PyMongoError as e:
        print(f"[READ ERROR] {e}")
        return []


def find_cat_by_name(coll: Collection, name: str) -> Optional[Dict[str, Any]]:
    """Find and return one cat document by name."""
    try:
        return coll.find_one({"name": name})
    except errors.PyMongoError as e:
        print(f"[READ ERROR] {e}")
        return None


def update_age_by_name(coll: Collection, name: str, new_age: int) -> bool:
    """ Update the age of a cat by name. Returns True if a document was modified."""
    try:
        res = coll.update_one({"name": name}, {"$set": {"age": new_age}})
        return res.modified_count == 1
    except errors.PyMongoError as e:
        print(f"[UPDATE ERROR] {e}")
        return False


def add_feature_by_name(coll: Collection, name: str, feature: str) -> bool:
    """ Add a feature to the features array of a cat by name. Returns True if a document was modified."""
    try:
        res = coll.update_one({"name": name}, {"$addToSet": {"features": feature}})
        return res.modified_count == 1
    except errors.PyMongoError as e:
        print(f"[UPDATE ERROR] {e}")
        return False


def delete_cat_by_name(coll: Collection, name: str) -> bool:
    """Delete one document by name. Returns True if a document was deleted."""
    try:
        res = coll.delete_one({"name": name})
        return res.deleted_count == 1
    except errors.PyMongoError as e:
        print(f"[DELETE ERROR] {e}")
        return False


def delete_all_cats(coll: Collection) -> int:
    """Delete all documents in the collection. Returns the number deleted."""
    try:
        res = coll.delete_many({})
        return res.deleted_count
    except errors.PyMongoError as e:
        print(f"[DELETE ERROR] {e}")
        return 0


# Utilities

def seed_sample_data(coll: Collection) -> None:
    """Insert sample documents if the collection is empty."""
    try:
        if coll.estimated_document_count() > 0:
            return
        sample_docs = [
            {
                "name": "barsik",
                "age": 3,
                "features": ["ходить в капці", "дає себе гладити", "рудий"],
            },
            {
                "name": "Lama",
                "age": 2,
                "features": ["ходить в лоток", "не дає себе гладити", "сірий"],
            },
            {
                "name": "Liza",
                "age": 4,
                "features": ["ходить в лоток", "дає себе гладити", "білий"],
            },
        ]
        coll.insert_many(sample_docs, ordered=False)
    except errors.BulkWriteError:
        # Ignore duplicate key errors if index exists
        pass
    except errors.PyMongoError as e:
        print(f"[SEED ERROR] {e}")


def pretty(doc: Dict[str, Any]) -> str:
    """Return a compact human-readable string for a cat document."""
    if not doc:
        return "<empty>"
    _id = str(doc.get("_id"))
    name = doc.get("name")
    age = doc.get("age")
    features = ", ".join(doc.get("features", []))
    return f"{name} (age={age}) — features: [{features}] — _id={_id}"


def print_all(coll: Collection) -> None:
    docs = list_all_cats(coll)
    if not docs:
        print("No cats found.")
        return
    for d in docs:
        print("•", pretty(d))


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


# CLI Menu

def menu() -> None:
    coll = get_collection()
    seed_sample_data(coll)

    actions = {
        "1": "List all cats",
        "2": "Find cat by name",
        "3": "Update cat age by name",
        "4": "Add feature to cat by name",
        "5": "Delete cat by name",
        "6": "Delete ALL cats",
        "7": "Exit",
    }

    while True:
        print("\n=== Mongo Cats CRUD ===")
        for k, v in actions.items():
            print(f"{k}. {v}")
        choice = ask("Select action [1-7]: ")

        if choice == "1":
            print_all(coll)

        elif choice == "2":
            name = ask("Enter cat name: ")
            doc = find_cat_by_name(coll, name)
            if doc:
                print(pretty(doc))
            else:
                print("Cat not found.")

        elif choice == "3":
            name = ask("Enter cat name: ")
            age_s = ask("Enter new age (int): ")
            try:
                age = int(age_s)
            except ValueError:
                print("Age must be an integer.")
                continue
            ok = update_age_by_name(coll, name, age)
            print("Updated." if ok else "Nothing updated (check name).")

        elif choice == "4":
            name = ask("Enter cat name: ")
            feature = ask("Enter feature to add: ")
            ok = add_feature_by_name(coll, name, feature)
            print("Feature added." if ok else "Nothing updated (check name).")

        elif choice == "5":
            name = ask("Enter cat name to delete: ")
            ok = delete_cat_by_name(coll, name)
            print("Deleted." if ok else "Nothing deleted (check name).")

        elif choice == "6":
            confirm = ask("Type 'YES' to delete ALL documents: ")
            if confirm == "YES":
                deleted = delete_all_cats(coll)
                print(f"Deleted {deleted} document(s).")
            else:
                print("Cancelled.")

        elif choice == "7":
            print("Bye!")
            break

        else:
            print("Unknown choice, try again.")


if __name__ == "__main__":
    menu()
