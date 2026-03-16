import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from typing import Dict, Any

# Get MongoDB URI from environment or use a local default fallback
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "hematology_db"
COLLECTION_NAME = "scan_reports"

class Database:
    client: AsyncIOMotorClient = None
    db = None
    collection = None

    @classmethod
    def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            cls.db = cls.client[DATABASE_NAME]
            cls.collection = cls.db[COLLECTION_NAME]
            print(f"Connected to MongoDB at {MONGO_URI}")
        except Exception as e:
            print(f"Warning: Could not connect to MongoDB: {e}. Scan history will be disabled.")

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed.")

    @classmethod
    async def save_report(cls, report_data: Dict[str, Any]):
        if cls.collection is not None:
            try:
                # Add timestamp
                report_data["timestamp"] = datetime.now(timezone.utc)
                result = await cls.collection.insert_one(report_data)
                return str(result.inserted_id)
            except Exception as e:
                print(f"Error saving report to MongoDB: {e}")
                return None
        return None

    @classmethod
    async def get_all_reports(cls):
        if cls.collection is not None:
            try:
                reports = []
                async for document in cls.collection.find().sort("timestamp", -1):
                    document["_id"] = str(document["_id"]) # convert ObjectId to string
                    reports.append(document)
                return reports
            except Exception as e:
                print(f"Error fetching reports from MongoDB: {e}")
                return []
        return []
