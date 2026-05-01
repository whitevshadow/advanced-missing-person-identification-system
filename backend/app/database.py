from pymongo import MongoClient

from .config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db]

missing_persons_collection = db["missing_persons"]
sightings_collection = db["sightings"]
matches_collection = db["matches"]
alerts_collection = db["alerts"]
feedback_collection = db["feedback"]
