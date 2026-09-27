# T-03 — Frontend Test Infrastructure

**Owner:** Anant
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** Nothing
**Blocks:** Nothing

---

## Objective

Set up `vitest` properly with React Testing Library. Add tests for the 5 most critical components: `Dashboard`, `Chatbot`, `Integrations`, `ServiceWidget`, `Sidebar`. Each component should have 3+ test cases.

---

## Why This Matters

- **Currently:** The desktop app has only 2 test files (`ConnectorForm.test.tsx` and `Integrations.test.tsx`) in `desktop/src/__tests__/`. There's no systematic test infrastructure — no shared test utilities, no mock providers, no consistent patterns.
- **After:** A solid testing foundation with shared utilities (API mocking, provider wrappers, common fixtures). The 5 most critical components have verified behavior. New components have a clear testing pattern to follow.

---

## Current State

**Existing test infrastructure:**
- `vitest` v5.0.0 installed
- `@testing-library/react` v16.3.3 installed
- `@testing-library/jest-dom` v7.0.1 installed
- `@testing-library/user-event` v14.6.7 installed
- `npm test` → `cross-env NODE_ENV=test vitest run`
- 2 existing test files in `desktop/src/__tests__/`

**Missing:**
- No test setup file (global mocks, providers)
- No shared test utilities (render with providers, mock API)
- No tests for Dashboard, Chatbot, ServiceWidget, or Sidebar
- No mock data fixtures
- No API response mocking infrastructure

---

## Implementation Plan

### Step 1: Create test setup and utilities

**`desktop/src/test/setup.ts`** — global test setup:

```typescript
import '@testing-library/jest-dom';

// Mock window.matchMedia (used by responsive components)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock fetch globally
global.fetch = vi.fn();

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  send: vi.fn(),
  close: vi.fn(),
  readyState: 1,
})) as any;
```

**`desktop/src/test/utils.tsx`** — shared render wrapper:

```typescript
import { render, RenderOptions } from '@testing-library/react';
import { ReactElement } from 'react';

// If the app uses context providers, wrap them here
const AllProviders = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

export const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react';
export { renderWithProviders as render };
```

**`desktop/src/test/mocks.ts`** — mock API responses:

```typescript
export const mockConnectors = [
  {
    id: 'github',
    name: 'GitHub',
    category: 'Source Control',
    configured: true,
    status: 'healthy',
    color: '#333',
  },
  {
    id: 'datadog',
    name: 'Datadog',
    category: 'Monitoring',
    configured: false,
    status: 'unconfigured',
    color: '#632CA6',
  },
  // ... add more as needed
];

export const mockDashboardSummary = {
  health_score: 85,
  connectors_up: 5,
  connectors_total: 8,
  active_watchers: 3,
  recent_activity: [
    { id: '1', type: 'watcher_alert', message: 'Pod crash detected', timestamp: Date.now() },
    { id: '2', type: 'fix_applied', message: 'Auto-fix applied', timestamp: Date.now() - 60000 },
  ],
};

export function mockFetch(responses: Record<string, any>) {
  return vi.fn().mockImplementation((url: string) => {
    const path = new URL(url, 'http://localhost').pathname;
    const data = responses[path];
    if (data) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(data),
        text: () => Promise.resolve(JSON.stringify(data)),
      });
    }
    return Promise.resolve({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: 'not found' }),
    });
  });
}
```

### Step 2: Update vitest config

```typescript
// vitest.config.ts (or in vite.config.ts)
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.test.{ts,tsx}', 'src/**/*.d.ts', 'src/test/**'],
    },
  },
});
```

### Step 3: Write tests for each component

#### Dashboard tests (`__tests__/Dashboard.test.tsx`)

```typescript
import { render, screen, waitFor } from '../test/utils';
import { mockFetch, mockDashboardSummary } from '../test/mocks';
import Dashboard from '../components/Dashboard';

describe('Dashboard', () => {
  beforeEach(() => {
    global.fetch = mockFetch({
      '/api/dashboard/summary': mockDashboardSummary,
      '/api/connectors': [],
      '/api/activity': [],
    });
  });

  it('renders health score from API data', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/85/)).toBeInTheDocument();
    });
  });

  it('shows loading skeleton before data arrives', () => {
    render(<Dashboard />);
    // Skeleton elements should be present before data loads
    expect(document.querySelector('[class*="skeleton"]')).toBeInTheDocument();
  });

  it('displays connector count correctly', async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/5/)).toBeInTheDocument(); // connectors_up
    });
  });
});
```

#### Chatbot tests (`__tests__/Chatbot.test.tsx`)

```typescript
describe('Chatbot', () => {
  it('renders message input field', () => { ... });
  it('sends message on submit', async () => { ... });
  it('displays received messages', async () => { ... });
  it('shows typing indicator during streaming', async () => { ... });
});
```

#### Integrations tests (`__tests__/Integrations.test.tsx`)

Already exists — verify it has 3+ tests, add if missing.

#### ServiceWidget tests (`__tests__/ServiceWidget.test.tsx`)

```typescript
describe('ServiceWidget', () => {
  it('renders widget with connector data', () => { ... });
  it('shows unavailable state when connector is down', () => { ... });
  it('displays metrics from API response', async () => { ... });
});
```

#### Sidebar tests (`__tests__/Sidebar.test.tsx`)

```typescript
describe('Sidebar', () => {
  it('renders all navigation items', () => { ... });
  it('highlights active page', () => { ... });
  it('navigates on item click', async () => { ... });
});
```

---

## Checklist

### Infrastructure
- [ ] Create `desktop/src/test/setup.ts` with global mocks
- [ ] Create `desktop/src/test/utils.tsx` with render wrapper
- [ ] Create `desktop/src/test/mocks.ts` with mock data and `mockFetch`
- [ ] Update `vitest.config.ts` with proper jsdom environment and setup file
- [ ] Verify `npm test` runs correctly with the new setup
- [ ] Verify existing 2 test files still pass

### Component Tests (3+ test cases each)
- [ ] `__tests__/Dashboard.test.tsx` — renders health, shows skeleton, displays counts
- [ ] `__tests__/Chatbot.test.tsx` — renders input, sends message, displays messages
- [ ] `__tests__/Integrations.test.tsx` — verify existing, add missing cases
- [ ] `__tests__/ServiceWidget.test.tsx` — renders data, unavailable state, metrics
- [ ] `__tests__/Sidebar.test.tsx` — renders items, active state, navigation

### CI
- [ ] `npm test` runs all test files in CI
- [ ] Test output is visible in CI logs
- [ ] Failures block the build

---

## Anti-Patterns to Avoid

> **🚫 DO NOT test implementation details.** Test what the user sees and does, not internal component state. Use `screen.getByText()`, `screen.getByRole()` — not accessing component internals.

> **🚫 DO NOT mock too deep.** Mock the `fetch` API, not every internal function. The tests should exercise the component's real logic, just with fake network responses.

> **🚫 DO NOT write snapshot tests.** Snapshots are brittle — any UI change breaks them, and reviewers tend to blindly approve snapshot updates. Write behavioral tests instead.

> **🚫 DO NOT skip Tauri-specific APIs.** If components use Tauri's `invoke()` or window APIs, mock them in `setup.ts`. Don't let tests crash because Tauri isn't available in the test environment.

> **🚫 DO NOT write tests that depend on timing.** Use `waitFor()` and `findByText()` from Testing Library, not `setTimeout()` or `sleep()`.

---

## Exit Criteria

- [ ] **5 component test files** — Dashboard, Chatbot, Integrations, ServiceWidget, Sidebar
- [ ] **Each with 3+ test cases** — meaningful behavior tests, not trivial "it renders"
- [ ] **`npm test` in CI runs them** — all pass, failures block the build
- [ ] **Test infrastructure established** — setup file, utilities, mock data
- [ ] **Existing 2 test files still pass** — no regressions
