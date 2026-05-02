import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient

from app.main import app
from app.database import db, missing_persons_collection, sightings_collection, matches_collection, alerts_collection, feedback_collection


@pytest.fixture
def client():
    """Provide test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_mongo():
    """Provide mock MongoDB client for testing."""
    mock_client = MongoClient()
    mock_db = mock_client["test_missing_persons_db"]
    
    # Return collections
    return {
        "db": mock_db,
        "missing_persons": mock_db["missing_persons"],
        "sightings": mock_db["sightings"],
        "matches": mock_db["matches"],
        "alerts": mock_db["alerts"],
        "feedback": mock_db["feedback"],
    }


@pytest.fixture
def sample_missing_person():
    """Provide sample missing person data."""
    return {
        "name": "John Doe",
        "age": 30,
        "gender": "Male",
        "city": "New York",
        "description": "Brown hair, blue eyes, 5'10\"",
        "phone": "555-1234",
        "email": "contact@example.com",
        "photos": ["photo1.jpg", "photo2.jpg"],
        "date_reported": "2026-05-01T00:00:00Z",
    }


@pytest.fixture
def sample_sighting():
    """Provide sample sighting data."""
    return {
        "missing_person_id": "507f1f77bcf86cd799439011",
        "location": "Central Park, New York",
        "description": "Saw someone matching the description",
        "sighting_date": "2026-05-02T10:30:00Z",
        "photo": "sighting_photo.jpg",
        "reporter_name": "Jane Smith",
        "reporter_phone": "555-5678",
        "reporter_email": "jane@example.com",
    }


@pytest.fixture
def sample_feedback():
    """Provide sample feedback data."""
    return {
        "match_id": "507f1f77bcf86cd799439012",
        "missing_person_id": "507f1f77bcf86cd799439011",
        "sighting_id": "507f1f77bcf86cd799439013",
        "is_correct": True,
        "comments": "Correct match, person found!",
    }
