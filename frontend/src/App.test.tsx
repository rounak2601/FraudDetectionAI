import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

jest.mock('./api/client', () => ({
  getModelHealth: jest.fn().mockResolvedValue({
    data: { status: 'healthy', models_active: 3 },
  }),
}));

test('renders FraudVision navigation', async () => {
  render(<MemoryRouter><App /></MemoryRouter>);
  expect(screen.getByText('FraudVision')).toBeInTheDocument();
  expect(await screen.findByText('SYSTEM ONLINE')).toBeInTheDocument();
});
