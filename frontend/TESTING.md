# Frontend Testing Guide

## Test Files

### api.test.js
- Tests for API module
- Fetch calls validation
- Error handling
- Base URL configuration

### App.test.jsx
- Component rendering tests
- UI structure validation
- Responsive design tests

## Running Tests

### Install Dependencies
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom jest babel-jest identity-obj-proxy
```

### Run All Tests
```bash
npm test
```

### Run Specific Test
```bash
npm test -- api.test.js
npm test -- App.test.jsx
```

### Watch Mode
```bash
npm test -- --watch
```

### Coverage Report
```bash
npm test -- --coverage
```

## Test Structure

- `setupTests.js` - Jest configuration and global mocks
- `__tests__/` - Test directory containing all test files
- Each component/module has a corresponding `.test.js/jsx` file

## Mocking

- API calls are mocked using Jest
- Environment variables are set in setupTests.js
- Components can use testing-library utilities for DOM queries

## Best Practices

1. Test user behavior, not implementation details
2. Use semantic queries (getByRole, getByLabelText)
3. Always clean up after tests
4. Mock external dependencies (API calls, etc.)
5. Test error states and edge cases
