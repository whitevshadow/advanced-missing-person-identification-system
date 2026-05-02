import pytest
from bson import ObjectId


def test_create_sighting(client, sample_sighting):
    """Test creating a sighting report."""
    response = client.post("/api/sightings", json=sample_sighting)
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == sample_sighting["location"]
    assert "id" in data or "_id" in data


def test_list_sightings(client, sample_sighting):
    """Test listing sightings."""
    # Create a sighting
    client.post("/api/sightings", json=sample_sighting)
    
    # List them
    response = client.get("/api/sightings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_sighting(client, sample_sighting):
    """Test getting a specific sighting."""
    # Create a sighting
    create_response = client.post("/api/sightings", json=sample_sighting)
    sighting_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # Retrieve it
    response = client.get(f"/api/sightings/{sighting_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == sample_sighting["location"]


def test_get_matches(client):
    """Test getting matches between sightings and missing persons."""
    response = client.get("/api/sightings/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_alerts(client):
    """Test getting alerts for matches."""
    response = client.get("/api/sightings/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_invalid_sighting_data(client):
    """Test creating sighting with invalid data."""
    invalid_data = {
        "location": "Somewhere",
        # Missing other required fields
    }
    response = client.post("/api/sightings", json=invalid_data)
    assert response.status_code in [400, 422]
