# Test Documentation

## Running Tests

### Quick Test
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_missing_persons.py -v
pytest tests/test_sightings.py -v
pytest tests/test_feedback.py -v
```

### Run Specific Test
```bash
pytest tests/test_missing_persons.py::test_create_missing_person -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Integration Tests Only
```bash
pytest tests/test_integration.py -v
```

## Test Files

### conftest.py
- Provides pytest fixtures for:
  - FastAPI test client
  - Mock MongoDB
  - Sample data (missing persons, sightings, feedback)

### test_missing_persons.py
Tests for missing persons endpoints:
- Create missing person
- List missing persons
- Get specific missing person
- Update missing person
- Delete missing person
- Input validation

### test_sightings.py
Tests for sighting endpoints:
- Create sighting
- List sightings
- Get specific sighting
- Get matches
- Get alerts
- Input validation

### test_feedback.py
Tests for feedback endpoints:
- Submit feedback
- Retrieve feedback
- List feedback
- Validate correctness field

### test_models.py
Tests for data schema validation:
- MissingPersonCreate schema
- SightingCreate schema
- FeedbackCreate schema
- Field validation

### test_services.py
Tests for backend services:
- Similarity calculation
- Matching logic
- Service validation

### test_integration.py
End-to-end integration tests:
- Complete missing person workflow
- Multiple persons management
- Sighting and matching workflow
- Full feedback workflow

## Test Coverage

Current test coverage includes:
- ✓ All CRUD operations for missing persons
- ✓ All CRUD operations for sightings
- ✓ Feedback submission and retrieval
- ✓ Schema validation
- ✓ Service logic
- ✓ End-to-end workflows

## Installation

Install test dependencies:
```bash
pip install pytest pytest-asyncio mongomock httpx
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## CI/CD Integration

To run tests in CI/CD pipeline, use:
```bash
pytest tests/ --junit-xml=test-results.xml --cov=app --cov-report=xml
```
