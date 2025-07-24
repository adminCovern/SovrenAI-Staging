import React from 'react';
import { render, screen } from '@testing-library/react';
import SovrenScore from '../SovrenScore';
describe('SovrenScore', () => {
  it('renders SOVREN Score Analytics header', () => {
    render(<SovrenScore />);
    expect(screen.getByText(/SOVREN Score Analytics/i)).toBeInTheDocument();
  });
}); 