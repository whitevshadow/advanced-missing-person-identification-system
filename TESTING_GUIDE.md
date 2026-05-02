# AMPIS Testing Suite

Complete testing framework for the Advanced Missing Person Identification System.

## Quick Start

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm install
npm test
```

## Backend Testing (Python/Pytest)

### Test Files
- `test_missing_persons.py` - Missing persons CRUD operations
- `test_sightings.py` - Sighting reports and alerts
- `test_feedback.py` - User feedback submission
- `test_models.py` - Data validation and schemas
- `test_services.py` - Service layer logic
- `test_integration.py` - End-to-end workflows

### Key Test Coverage
✓ All REST API endpoints
✓ Database operations
✓ Schema validation
✓ Service logic
✓ Error handling
✓ Integration workflows

### Running Tests

**All tests:**
```bash
pytest tests/ -v
```

**Specific test file:**
```bash
pytest tests/test_missing_persons.py -v
```

**Specific test:**
```bash
pytest tests/test_missing_persons.py::test_create_missing_person -v
```

**With coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
```

**Integration tests only:**
```bash
pytest tests/test_integration.py -v
```

## Frontend Testing (JavaScript/Jest)

### Test Files
- `api.test.js` - API module and fetch calls
- `App.test.jsx` - Component rendering and responsiveness

### Running Tests

**All tests:**
```bash
npm test
```

**Specific test file:**
```bash
npm test -- api.test.js
```

**Watch mode:**
```bash
npm test -- --watch
```

**Coverage report:**
```bash
npm test -- --coverage
```

## Test Data & Fixtures

### Backend Fixtures (conftest.py)
- `sample_missing_person` - Test missing person record
- `sample_sighting` - Test sighting report
- `sample_feedback` - Test feedback submission
- `mock_mongo` - Mock MongoDB database
- `client` - FastAPI test client

### Frontend Mocks (setupTests.js)
- `global.fetch` - Mocked HTTP requests
- Environment variables
- DOM testing library setup

## Test Workflows

### Backend Workflow Testing

1. **Missing Person Workflow**
   - Create → List → Get → Update → Delete

2. **Sighting & Matching Workflow**
   - Create person → Report sighting → Check matches → View alerts

3. **Feedback Workflow**
   - Submit feedback → Retrieve feedback → List all feedback

### Frontend Workflow Testing

1. **Component Rendering**
   - App mounts without errors
   - UI elements display correctly

2. **Responsive Design**
   - Mobile screen adaptation (375px)
   - Desktop screen adaptation (1920px)

3. **API Integration**
   - Fetch calls are correct
   - Error handling works
   - Base URL is configured

## Continuous Integration

### Running All Tests
```bash
# Backend
cd backend && pytest tests/ --junit-xml=test-results.xml --cov=app --cov-report=xml

# Frontend
cd frontend && npm test -- --coverage
```

### Test Artifacts
- JUnit XML reports for CI/CD
- Coverage reports (HTML and XML)
- Test execution logs

## Dependencies

### Backend
- pytest>=7.4.0
- pytest-asyncio>=0.21.0
- mongomock>=4.1.2
- httpx>=0.24.0

### Frontend
- @testing-library/react
- @testing-library/jest-dom
- jest
- babel-jest

## Adding New Tests

### Backend
1. Create test file in `backend/tests/test_*.py`
2. Use fixtures from `conftest.py`
3. Follow naming convention: `test_<feature>`
4. Run: `pytest tests/test_<file>.py -v`

### Frontend
1. Create test file in `frontend/src/__tests__/*.test.jsx`
2. Use testing-library utilities
3. Follow naming convention: `test_<feature>`
4. Run: `npm test -- <file>.test.js`

## Test Results

Run this to see test results:
```bash
cd backend
pytest tests/ -v --tb=short
```

Expected output:
```
test_missing_persons.py::test_create_missing_person PASSED
test_missing_persons.py::test_list_missing_persons PASSED
test_sightings.py::test_create_sighting PASSED
...
```

## Troubleshooting

### Backend Tests Fail
- Ensure MongoDB mock is available: `pip install mongomock`
- Check test data in conftest.py
- Verify all dependencies installed: `pip install -r requirements.txt`

### Frontend Tests Fail
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Jest configuration in jest.config.js
- Verify test setup in setupTests.js

## Documentation

- [Backend Testing Guide](backend/TESTING.md)
- [Frontend Testing Guide](frontend/TESTING.md)

---

**Last Updated:** 2026-05-02
**Version:** 1.0.0
