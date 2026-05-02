import pytest


def test_submit_feedback(client, sample_feedback):
    """Test submitting feedback on a match."""
    response = client.post("/api/feedback", json=sample_feedback)
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == sample_feedback["is_correct"]
    assert "id" in data or "_id" in data


def test_get_feedback(client, sample_feedback):
    """Test retrieving feedback."""
    # Submit feedback
    create_response = client.post("/api/feedback", json=sample_feedback)
    feedback_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # Retrieve it
    response = client.get(f"/api/feedback/{feedback_id}")
    assert response.status_code == 200


def test_list_feedback(client, sample_feedback):
    """Test listing all feedback."""
    # Submit feedback
    client.post("/api/feedback", json=sample_feedback)
    
    # List feedback
    response = client.get("/api/feedback")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_feedback_validation(client):
    """Test feedback validation."""
    invalid_feedback = {
        "match_id": "507f1f77bcf86cd799439012",
        # Missing required fields
    }
    response = client.post("/api/feedback", json=invalid_feedback)
    assert response.status_code in [400, 422]


def test_feedback_correctness_field(client, sample_feedback):
    """Test that is_correct field is properly validated."""
    feedback_positive = sample_feedback.copy()
    feedback_positive["is_correct"] = True
    response = client.post("/api/feedback", json=feedback_positive)
    assert response.status_code == 200
    assert response.json()["is_correct"] is True
    
    feedback_negative = sample_feedback.copy()
    feedback_negative["is_correct"] = False
    response = client.post("/api/feedback", json=feedback_negative)
    assert response.status_code == 200
    assert response.json()["is_correct"] is False
