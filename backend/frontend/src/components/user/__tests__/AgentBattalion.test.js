import React from 'react';
import { render, screen } from '@testing-library/react';
import AgentBattalion from '../AgentBattalion';
describe('AgentBattalion', () => {
  it('renders Agent Battalion header', () => {
    render(<AgentBattalion />);
    expect(screen.getByText(/Agent Battalion/i)).toBeInTheDocument();
  });
}); 