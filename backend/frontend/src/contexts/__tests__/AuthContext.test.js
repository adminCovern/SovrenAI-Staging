import React from 'react';
import { render } from '@testing-library/react';
import { AuthProvider } from '../AuthContext';

describe('AuthContext', () => {
  it('renders AuthProvider without crashing', () => {
    render(<AuthProvider>test</AuthProvider>);
  });
  // Add more tests for login, logout, and user state as needed
}); 