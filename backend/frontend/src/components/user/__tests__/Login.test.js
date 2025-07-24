import React from 'react';
import { render, screen } from '@testing-library/react';
import Login from '../Login';
describe('Login', () => {
  it('renders login form', () => {
    render(<Login />);
    expect(screen.getByText(/SOVREN AI/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });
}); 