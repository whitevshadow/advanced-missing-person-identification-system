import '@testing-library/jest-dom';

// Mock environment
process.env.VITE_API_BASE_URL = 'http://localhost:1050/api';

// Mock fetch if needed
global.fetch = jest.fn();
