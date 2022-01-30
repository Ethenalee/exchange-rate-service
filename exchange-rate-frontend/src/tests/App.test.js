import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders App loading table component', () => {
  render(<App />);
  const paperElement = screen.getByTestId('exchange-rate-paper');
  const headerElement = screen.getByTestId('exchange-rate-header');
  expect(paperElement).toBeInTheDocument();
  expect(headerElement).toBeInTheDocument();
});
