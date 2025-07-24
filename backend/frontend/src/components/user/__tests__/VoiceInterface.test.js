import React from 'react';
import { render, screen } from '@testing-library/react';
import VoiceInterface from '../VoiceInterface';
describe('VoiceInterface', () => {
  it('renders voice interface header', () => {
    render(<VoiceInterface />);
    expect(screen.getByText(/Voice Interface/i)).toBeInTheDocument();
  });
}); 