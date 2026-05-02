import pytest


def test_end_to_end_missing_person_workflow(client, sample_missing_person):
    """Test complete workflow: create person, list, retrieve, update, delete."""
    # Create
    create_response = client.post("/api/missing-persons", json=sample_missing_person)
    assert create_response.status_code == 200
    person_id = create_response.json()["id"] if "id" in create_response.json() else create_response.json()["_id"]
    
    # List
    list_response = client.get("/api/missing-persons")
    assert list_response.status_code == 200
    assert any(p.get("id") == person_id or p.get("_id") == person_id for p in list_response.json())
    
    # Retrieve
    get_response = client.get(f"/api/missing-persons/{person_id}")
    assert get_response.status_code == 200
    
    # Update
    updated_data = sample_missing_person.copy()
    updated_data["age"] = 31
    update_response = client.put(f"/api/missing-persons/{person_id}", json=updated_data)
    assert update_response.status_code == 200
    
    # Delete
    delete_response = client.delete(f"/api/missing-persons/{person_id}")
    assert delete_response.status_code in [200, 204]


def test_multiple_missing_persons(client, sample_missing_person):
    """Test creating and managing multiple missing persons."""
    person1 = sample_missing_person.copy()
    person2 = sample_missing_person.copy()
    person2["name"] = "Jane Smith"
    person2["city"] = "Los Angeles"
    
    # Create both
    response1 = client.post("/api/missing-persons", json=person1)
    response2 = client.post("/api/missing-persons", json=person2)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # List and verify both exist
    list_response = client.get("/api/missing-persons")
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 2


def test_sighting_and_matching_workflow(client, sample_missing_person, sample_sighting):
    """Test workflow: create person, report sighting, check matches."""
    # Create a missing person
    person_response = client.post("/api/missing-persons", json=sample_missing_person)
    assert person_response.status_code == 200
    person_id = person_response.json()["id"] if "id" in person_response.json() else person_response.json()["_id"]
    
    # Update sighting with correct person ID
    sample_sighting["missing_person_id"] = person_id
    
    # Report a sighting
    sighting_response = client.post("/api/sightings", json=sample_sighting)
    assert sighting_response.status_code == 200
    
    # Check for matches
    matches_response = client.get("/api/sightings/matches")
    assert matches_response.status_code == 200
    assert isinstance(matches_response.json(), list)


def test_feedback_workflow(client, sample_missing_person, sample_sighting, sample_feedback):
    """Test complete feedback workflow."""
    # Create person and sighting first
    person_response = client.post("/api/missing-persons", json=sample_missing_person)
    person_id = person_response.json()["id"] if "id" in person_response.json() else person_response.json()["_id"]
    
    sample_sighting["missing_person_id"] = person_id
    sighting_response = client.post("/api/sightings", json=sample_sighting)
    sighting_id = sighting_response.json()["id"] if "id" in sighting_response.json() else sighting_response.json()["_id"]
    
    # Submit feedback
    sample_feedback["missing_person_id"] = person_id
    sample_feedback["sighting_id"] = sighting_id
    
    feedback_response = client.post("/api/feedback", json=sample_feedback)
    assert feedback_response.status_code == 200
    
    # Verify feedback was recorded
    list_response = client.get("/api/feedback")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)
