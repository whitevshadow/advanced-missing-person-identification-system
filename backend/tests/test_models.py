import pytest
from datetime import datetime
from app.schemas import (
    MissingPersonCreate,
    SightingCreate,
    FeedbackCreate,
)


def test_missing_person_schema(sample_missing_person):
    """Test MissingPersonCreate schema validation."""
    person = MissingPersonCreate(**sample_missing_person)
    assert person.name == sample_missing_person["name"]
    assert person.age == sample_missing_person["age"]
    assert person.city == sample_missing_person["city"]


def test_sighting_schema(sample_sighting):
    """Test SightingCreate schema validation."""
    sighting = SightingCreate(**sample_sighting)
    assert sighting.location == sample_sighting["location"]
    assert sighting.reporter_name == sample_sighting["reporter_name"]


def test_feedback_schema(sample_feedback):
    """Test FeedbackCreate schema validation."""
    feedback = FeedbackCreate(**sample_feedback)
    assert feedback.is_correct == sample_feedback["is_correct"]
    assert feedback.missing_person_id == sample_feedback["missing_person_id"]


def test_missing_person_invalid_age():
    """Test that invalid age is rejected."""
    with pytest.raises(Exception):  # Should raise validation error
        MissingPersonCreate(
            name="John",
            age=-5,  # Invalid negative age
            gender="Male",
            city="New York",
            description="Test",
            phone="555-1234",
            email="test@example.com",
            photos=[],
            date_reported=datetime.now().isoformat(),
        )


def test_sighting_required_fields():
    """Test that sighting requires all necessary fields."""
    incomplete_sighting = {
        "location": "Somewhere",
        # Missing required fields
    }
    with pytest.raises(Exception):  # Should raise validation error
        SightingCreate(**incomplete_sighting)


def test_feedback_boolean_validation():
    """Test feedback is_correct must be boolean."""
    valid_feedback = {
        "match_id": "507f1f77bcf86cd799439012",
        "missing_person_id": "507f1f77bcf86cd799439011",
        "sighting_id": "507f1f77bcf86cd799439013",
        "is_correct": True,
        "comments": "Test",
    }
    feedback = FeedbackCreate(**valid_feedback)
    assert isinstance(feedback.is_correct, bool)
