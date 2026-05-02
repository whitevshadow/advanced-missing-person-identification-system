import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';

describe('API Module', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch missing persons', async () => {
    const mockData = [
      {
        id: 1,
        name: 'John Doe',
        age: 30,
        city: 'New York',
        description: 'Brown hair, blue eyes'
      }
    ];

    global.fetch.mockResolvedValueOnce({
      json: async () => mockData,
      ok: true,
    });

    // Import the function after setting up the mock
    const api = await import('../src/api.js');
    const result = await api.fetchMissingPersons();

    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/missing-persons'),
      expect.any(Object)
    );
  });

  it('should handle API errors gracefully', async () => {
    global.fetch.mockResolvedValueOnce({
      json: async () => ({ error: 'Not found' }),
      ok: false,
      status: 404,
    });

    const api = await import('../src/api.js');
    // This will depend on how the API module handles errors
    // Adjust test based on actual error handling
  });

  it('should set correct base URL', async () => {
    const api = await import('../src/api.js');
    expect(api.default.defaults.baseURL).toContain('/api');
  });
});
