import pytest
from bson import ObjectId


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_missing_person(client, sample_missing_person):
    """Test creating a missing person."""
    response = client.post("/api/missing-persons", json=sample_missing_person)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_missing_person["name"]
    assert data["age"] == sample_missing_person["age"]
    assert data["city"] == sample_missing_person["city"]
    assert "id" in data or "_id" in data


def test_list_missing_persons(client, sample_missing_person):
    """Test listing missing persons."""
    # Create a person first
    client.post("/api/missing-persons", json=sample_missing_person)
    
    # List them
    response = client.get("/api/missing-persons")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_missing_person(client, sample_missing_person):
    """Test getting a specific missing person."""
    # Create a person
    create_response = client.post("/api/missing-persons", json=sample_missing_person)
    person_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # Retrieve it
    response = client.get(f"/api/missing-persons/{person_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_missing_person["name"]


def test_update_missing_person(client, sample_missing_person):
    """Test updating a missing person."""
    # Create a person
    create_response = client.post("/api/missing-persons", json=sample_missing_person)
    person_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # Update it
    updated_data = sample_missing_person.copy()
    updated_data["age"] = 31
    response = client.put(f"/api/missing-persons/{person_id}", json=updated_data)
    assert response.status_code == 200


def test_delete_missing_person(client, sample_missing_person):
    """Test deleting a missing person."""
    # Create a person
    create_response = client.post("/api/missing-persons", json=sample_missing_person)
    person_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # Delete it
    response = client.delete(f"/api/missing-persons/{person_id}")
    assert response.status_code in [200, 204]


def test_invalid_missing_person_data(client):
    """Test creating missing person with invalid data."""
    invalid_data = {
        "name": "John Doe",
        # Missing required fields
    }
    response = client.post("/api/missing-persons", json=invalid_data)
    assert response.status_code in [400, 422]  # Validation errors
