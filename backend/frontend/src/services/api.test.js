import api from './api';

describe('api service', () => {
  it('should instantiate axios instance', () => {
    expect(api).toBeDefined();
  });
  // Add more tests for interceptors, error handling, and auth as needed
}); 