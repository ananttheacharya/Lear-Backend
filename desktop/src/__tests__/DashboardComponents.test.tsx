import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KPIStrip } from '../components/dashboard/index';

describe('dashboard presentation components', () => {
  it('renders live KPI values from props without fetching', () => {
    render(<KPIStrip healthScore={92} configuredConnectors={4} totalServices={7} watcherState="ACTIVE" activeWatches={2} environment="Production" />);
    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('7')).toBeInTheDocument();
    expect(screen.getByText('STREAMING')).toBeInTheDocument();
  });

  it('renders token-compatible skeletons while loading', () => {
    const { container } = render(<KPIStrip healthScore={0} configuredConnectors={0} totalServices={0} watcherState="IDLE" activeWatches={0} environment="Production" loading />);
    expect(container.querySelectorAll('.ui-skeleton')).toHaveLength(4);
  });
});
