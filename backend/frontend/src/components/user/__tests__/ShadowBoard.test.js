import React from 'react';
import { render, screen } from '@testing-library/react';
import ShadowBoard from '../ShadowBoard';
describe('ShadowBoard', () => {
  it('renders Shadow Board header', () => {
    render(<ShadowBoard />);
    expect(screen.getByText(/Shadow Board/i)).toBeInTheDocument();
  });
}); 