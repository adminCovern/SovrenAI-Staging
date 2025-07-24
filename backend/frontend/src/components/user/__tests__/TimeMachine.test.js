import React from 'react';
import { render, screen } from '@testing-library/react';
import TimeMachine from '../TimeMachine';
describe('TimeMachine', () => {
  it('renders Time Machine header', () => {
    render(<TimeMachine />);
    expect(screen.getByText(/Time Machine/i)).toBeInTheDocument();
  });
}); 