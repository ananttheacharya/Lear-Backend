import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge, Button, Card, Dropdown, EmptyState, Input, Modal, Skeleton, Tooltip } from '../components/ui';

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
  it('closes dropdown items after an action', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();
    const action = () => undefined;
    render(<Dropdown trigger={<span>Open menu</span>} items={[{ label: 'Run check', onClick: action }]} />);
    await user.click(screen.getByRole('button', { name: 'Open menu' }));
    expect(screen.getByRole('menuitem', { name: 'Run check' })).toBeInTheDocument();
    await user.click(screen.getByRole('menuitem', { name: 'Run check' }));
    expect(screen.queryByRole('menuitem', { name: 'Run check' })).not.toBeInTheDocument();
  });
  it('renders an accessible empty state action', () => {
    render(<EmptyState icon={<span>!</span>} title="No watches" description="Connect a service to begin." action={{ label: 'Connect service', onClick: () => undefined }} />);
    expect(screen.getByRole('heading', { name: 'No watches' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Connect service' })).toBeInTheDocument();
  });
  it('opens a modal with dialog semantics', () => {
    render(<Modal open onClose={() => undefined} title="Confirm action">Secure operation</Modal>);
    expect(screen.getByRole('dialog', { name: 'Confirm action' })).toBeInTheDocument();
    expect(screen.getByText('Secure operation')).toBeInTheDocument();
  });
  it('exposes tooltip content on focus', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();
    render(<Tooltip content="Live status"><button>Indicator</button></Tooltip>);
    await user.hover(screen.getByRole('button', { name: 'Indicator' }));
    await new Promise(resolve => setTimeout(resolve, 320));
    expect(screen.getByRole('tooltip')).toHaveTextContent('Live status');
  });
  it('renders a loading skeleton with the requested shape', () => {
    const { container } = render(<Skeleton variant="circular" width="2rem" height="2rem" />);
    expect(container.querySelector('.ui-skeleton--circular')).toHaveStyle({ width: '2rem', height: '2rem' });
  });
});
