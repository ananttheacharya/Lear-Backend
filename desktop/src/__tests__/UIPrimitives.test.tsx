import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge, Button, Card, Input, Skeleton } from '../components/ui';

describe('Lear UI primitives', () => {
  it('supports semantic button variants and loading state', () => {
    const { rerender } = render(<Button variant="success">Confirm action</Button>);
    expect(screen.getByRole('button', { name: 'Confirm action' })).toBeInTheDocument();
    rerender(<Button loading>Confirm action</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
  it('renders status badges and card variants accessibly', () => {
    render(<Card variant="glass" aria-label="Telemetry card"><Badge variant="success" dot>Healthy</Badge></Card>);
    expect(screen.getByText('Healthy')).toBeInTheDocument();
    expect(screen.getByLabelText('Telemetry card')).toHaveClass('ui-card--glass');
  });
  it('connects input labels and exposes validation errors', () => {
    render(<Input label="Connector token" error="Token is required" />);
    expect(screen.getByLabelText('Connector token')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByText('Token is required')).toBeInTheDocument();
  });
  it('renders a loading skeleton with the requested shape', () => {
    const { container } = render(<Skeleton variant="circular" width="2rem" height="2rem" />);
    expect(container.querySelector('.ui-skeleton--circular')).toHaveStyle({ width: '2rem', height: '2rem' });
  });
});
