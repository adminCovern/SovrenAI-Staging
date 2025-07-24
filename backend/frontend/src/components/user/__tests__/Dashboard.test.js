import React from 'react';
import { render, screen } from '@testing-library/react';
import Dashboard from '../Dashboard';
describe('Dashboard', () => {
  it('renders dashboard header', () => {
    render(<Dashboard />);
    expect(screen.getByText(/SOVREN AI/i)).toBeInTheDocument();
  });
}); 