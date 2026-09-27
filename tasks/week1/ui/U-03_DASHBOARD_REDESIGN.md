# U-03 — Dashboard Redesign

**Owner:** Avi
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 2–3 days
**Depends on:** U-01 (design tokens must exist)
**Blocks:** Nothing

---

## Objective

Decompose the bloated `Dashboard.tsx` (50 KB / ~1,400 lines) into composable sub-components: `HealthBar`, `KPIStrip`, `ActivityFeed`, `QuickActions`. Add micro-animations on data updates. The dashboard must load in under 500ms with skeleton loading states.

---

## Why This Matters

- **Currently:** `Dashboard.tsx` is a 50 KB monolith containing ALL dashboard logic — data fetching, health score calculation, KPI rendering, activity feed, quick actions, and connector status — in one file. It's untestable, unmaintainable, and slow to render.
- **After:** The dashboard is composed of focused, independently testable sub-components. Data updates animate smoothly. Loading shows skeletons, not blank space.

---

## Current State

`Dashboard.tsx` (50,605 bytes):
- Fetches from multiple API endpoints inline
- Health score calculation mixed with rendering
- Activity feed embedded in the same component
- Quick actions hardcoded inline
- No loading skeletons (shows old data or nothing)
- All styling inline or hardcoded

---

## Target Component Architecture

```
Dashboard.tsx (orchestrator, < 200 lines)
├── HealthBar.tsx         — Overall system health score with animated arc/bar
├── KPIStrip.tsx          — Key metrics row (connectors up, watchers active, etc.)
│   └── KPICard.tsx       — Individual metric card with label + value + trend
├── ActivityFeed.tsx      — Recent events/actions timeline
│   └── ActivityItem.tsx  — Single activity entry with icon + timestamp
├── QuickActions.tsx      — Common action buttons (run diagnosis, add watcher, etc.)
├── ConnectorOverview.tsx — Grid of connector status cards
│   └── ConnectorMini.tsx — Compact connector card with health indicator
└── DashboardSkeleton.tsx — Skeleton loading state matching the full layout
```

---

## Implementation Plan

### Step 1: Create sub-component directory

```
desktop/src/components/dashboard/
  HealthBar.tsx
  KPIStrip.tsx
  KPICard.tsx
  ActivityFeed.tsx
  ActivityItem.tsx
  QuickActions.tsx
  ConnectorOverview.tsx
  ConnectorMini.tsx
  DashboardSkeleton.tsx
  index.ts             — re-exports
```

### Step 2: Extract `HealthBar`

The health score should be a visual arc/gauge that animates when the value changes:

```tsx
interface HealthBarProps {
  score: number;       // 0-100
  label: string;       // "System Health"
  loading?: boolean;
}

const HealthBar: React.FC<HealthBarProps> = ({ score, label, loading }) => {
  const [displayScore, setDisplayScore] = useState(0);

  // Animate score changes
  useEffect(() => {
    const start = displayScore;
    const diff = score - start;
    const duration = 600; // ms
    const startTime = performance.now();

    const animate = (time: number) => {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(start + diff * eased));
      if (progress < 1) requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
  }, [score]);

  if (loading) return <HealthBarSkeleton />;

  return (
    <div className="health-bar">
      {/* Animated arc/gauge SVG */}
      <svg viewBox="0 0 120 120">
        {/* Background arc */}
        <circle cx="60" cy="60" r="50" fill="none"
          stroke="var(--color-neutral-800)" strokeWidth="8"
          strokeDasharray="251" strokeDashoffset="62" /* 75% arc */
          transform="rotate(135 60 60)"
        />
        {/* Value arc — animates via stroke-dashoffset */}
        <circle cx="60" cy="60" r="50" fill="none"
          stroke={getHealthColor(displayScore)}
          strokeWidth="8" strokeLinecap="round"
          strokeDasharray="251"
          strokeDashoffset={251 - (189 * displayScore / 100)}
          transform="rotate(135 60 60)"
          style={{ transition: 'stroke-dashoffset 600ms var(--ease-out)' }}
        />
      </svg>
      <span className="health-bar__score">{displayScore}%</span>
      <span className="health-bar__label">{label}</span>
    </div>
  );
};
```

### Step 3: Extract `KPIStrip` and `KPICard`

```tsx
interface KPICardProps {
  label: string;
  value: number | string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;   // e.g., "+5%" 
  icon: React.ReactNode;
  loading?: boolean;
}
```

Numbers should animate when they change (count up/down).

### Step 4: Extract `ActivityFeed`

Pull the activity feed into its own component that:
- Accepts an `activities` array
- Renders a scrollable timeline
- New items animate in from the top (slide + fade)
- Shows relative timestamps ("2m ago", "1h ago")

### Step 5: Create `DashboardSkeleton`

A skeleton that matches the exact layout shape of the loaded dashboard:

```tsx
const DashboardSkeleton = () => (
  <div className="dashboard">
    <div className="dashboard__header">
      <SkeletonBlock width="200px" height="32px" />
    </div>
    <div className="dashboard__health">
      <SkeletonCircle size="120px" />
    </div>
    <div className="dashboard__kpis">
      {[1, 2, 3, 4].map(i => (
        <SkeletonBlock key={i} width="100%" height="80px" />
      ))}
    </div>
    <div className="dashboard__activity">
      {[1, 2, 3, 4, 5].map(i => (
        <SkeletonBlock key={i} width="100%" height="48px" />
      ))}
    </div>
  </div>
);
```

### Step 6: Rewrite `Dashboard.tsx` as orchestrator

The new `Dashboard.tsx` should be under 200 lines — fetching data and composing sub-components:

```tsx
const Dashboard = () => {
  const { data, loading, error } = useDashboardData();

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="dashboard">
      <HealthBar score={data.healthScore} label="System Health" />
      <KPIStrip metrics={data.kpis} />
      <div className="dashboard__grid">
        <ActivityFeed activities={data.recentActivity} />
        <QuickActions />
      </div>
      <ConnectorOverview connectors={data.connectors} />
    </div>
  );
};
```

### Step 7: Add micro-animations

| Element | Animation | Trigger |
|---|---|---|
| Health score | Count up/down + arc fill | Data refresh |
| KPI numbers | Count animation | Data refresh |
| Activity feed items | Slide in from top | New item arrives |
| Connector status dots | Pulse briefly | Status change |
| Stale data | Fade to muted | Data older than 30s |

---

## Checklist

### Preparation
- [ ] Read all 1,400+ lines of `Dashboard.tsx`
- [ ] Map each section to its target sub-component
- [ ] Identify all data fetching calls and their dependencies
- [ ] Ensure U-01 design tokens are available

### Sub-component extraction
- [ ] Create `desktop/src/components/dashboard/` directory
- [ ] Extract `HealthBar.tsx` with animated score arc
- [ ] Extract `KPIStrip.tsx` and `KPICard.tsx` with animated numbers
- [ ] Extract `ActivityFeed.tsx` and `ActivityItem.tsx` with timeline
- [ ] Extract `QuickActions.tsx`
- [ ] Extract `ConnectorOverview.tsx` and `ConnectorMini.tsx`
- [ ] Create `DashboardSkeleton.tsx` matching the layout shape
- [ ] Rewrite `Dashboard.tsx` as thin orchestrator (under 200 lines)

### Animations
- [ ] Health score animates on change (number count + arc fill)
- [ ] KPI numbers animate on change (count up/down)
- [ ] New activity items slide in from top
- [ ] Stale data shows loading skeleton, not old numbers
- [ ] Connector status dots pulse on status change

### Quality
- [ ] All sub-components use design tokens (zero hardcoded values)
- [ ] Each sub-component has TypeScript prop types
- [ ] Dashboard loads in under 500ms (measure with DevTools)
- [ ] Skeleton → real data transition is smooth (no layout shift)
- [ ] Each sub-component is independently testable

---

## Anti-Patterns to Avoid

> **🚫 DO NOT fetch data in sub-components.** Data fetching happens in the orchestrator (`Dashboard.tsx`) or a custom hook (`useDashboardData`). Sub-components receive data as props — they're pure presentation.

> **🚫 DO NOT animate with JavaScript `setInterval`.** Use `requestAnimationFrame` for number counting and CSS transitions for visual properties. RAF is synced to the display refresh rate; setInterval is not.

> **🚫 DO NOT show old numbers while loading.** When data is refreshing, either show a subtle loading indicator over the current data, or show a skeleton. Never show stale data without indicating it's stale.

> **🚫 DO NOT make sub-components aware of the API.** `KPICard` takes `{ label, value, trend }` — it doesn't know about `/api/dashboard/summary`. This makes them reusable and testable.

> **🚫 DO NOT animate on initial render.** Animations should only trigger on DATA CHANGES, not on first mount. A dashboard that bounces and counts on every page load is annoying, not delightful.

---

## Exit Criteria

- [ ] **Dashboard loads in under 500ms** — measured with DevTools Performance
- [ ] **Each sub-component is independently testable** — accepts props, renders deterministically
- [ ] **Stale data shows loading skeleton, not old numbers**
- [ ] **Health score animates on change** — smooth arc fill + number count
- [ ] **`Dashboard.tsx` under 200 lines** — orchestrator only
- [ ] **All sub-components use design tokens** — zero hardcoded values
