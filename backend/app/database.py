import os
import sys

from pymongo import MongoClient

from .config import settings


# During pytest runs we prefer an in-memory mongomock client to avoid
# requiring a running MongoDB instance. Detect pytest via the environment
# or presence of the pytest module.
USE_MOCK = os.getenv("USE_MOCK_DB") == "1" or "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules
if USE_MOCK:
	try:
		import mongomock  # type: ignore

		client = mongomock.MongoClient()
	except Exception:
		# Fallback to real MongoClient if mongomock is not available.
		client = MongoClient(settings.mongo_uri)
else:
	client = MongoClient(settings.mongo_uri)

db = client[settings.mongo_db]

missing_persons_collection = db["missing_persons"]
sightings_collection = db["sightings"]
matches_collection = db["matches"]
alerts_collection = db["alerts"]
feedback_collection = db["feedback"]
