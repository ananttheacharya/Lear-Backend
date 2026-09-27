# U-02 — Sidebar and Navigation Redesign

**Owner:** Avi
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 1–2 days
**Depends on:** U-01 (design tokens must exist)
**Blocks:** Nothing

---

## Objective

Redesign `Sidebar.tsx` (16 KB / 694 lines) to support: smoother transitions, better active state indication, a collapsible mode for more workspace, and keyboard navigation. The sidebar should feel premium and responsive.

---

## Why This Matters

- **Currently:** `Sidebar.tsx` is 16 KB with hardcoded styles, basic active state highlighting, and no collapse/expand functionality. Navigation is mouse-only.
- **After:** A polished sidebar that collapses to icons-only mode, has smooth animated transitions, clear active state indication with the brand accent, and full keyboard navigation.

---

## Current State

`Sidebar.tsx` (16,694 bytes):
- Static width (no collapse/expand)
- Basic active state (color change, no animation)
- No keyboard navigation
- Hardcoded pixel values and colors throughout

---

## Implementation Plan

### Step 1: Add collapse/expand state

```tsx
const [collapsed, setCollapsed] = useState(false);

// Persist collapse state
useEffect(() => {
  const saved = localStorage.getItem('sidebar-collapsed');
  if (saved) setCollapsed(JSON.parse(saved));
}, []);

useEffect(() => {
  localStorage.setItem('sidebar-collapsed', JSON.stringify(collapsed));
}, [collapsed]);
```

### Step 2: Implement animated width transition

```css
.sidebar {
  width: var(--sidebar-width-expanded, 240px);
  transition: width var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.sidebar--collapsed {
  width: var(--sidebar-width-collapsed, 64px);
}
```

**Key requirement:** Width transition must be under 200ms (`--duration-normal`).

### Step 3: Redesign active state indication

Replace the current basic color change with a multi-cue active indicator:

```css
.nav-item {
  position: relative;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast) var(--ease-out);
  color: var(--color-neutral-400);
}

.nav-item:hover {
  background: var(--color-neutral-800);
  color: var(--color-neutral-200);
}

.nav-item--active {
  background: var(--color-brand-primary-muted);
  color: var(--color-brand-primary-light);
}

/* Active indicator bar */
.nav-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  border-radius: var(--radius-full);
  background: var(--color-brand-primary);
  transition: height var(--duration-normal) var(--ease-spring);
}
```

### Step 4: Add keyboard navigation

```tsx
// Handle arrow keys for navigation
const handleKeyDown = (e: React.KeyboardEvent) => {
  const items = document.querySelectorAll('.nav-item');
  const currentIndex = Array.from(items).findIndex(
    item => item === document.activeElement
  );

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      const next = items[Math.min(currentIndex + 1, items.length - 1)] as HTMLElement;
      next?.focus();
      break;
    case 'ArrowUp':
      e.preventDefault();
      const prev = items[Math.max(currentIndex - 1, 0)] as HTMLElement;
      prev?.focus();
      break;
    case 'Enter':
    case ' ':
      e.preventDefault();
      (document.activeElement as HTMLElement)?.click();
      break;
  }
};
```

Add `tabIndex={0}` and proper `role="navigation"` / `role="menuitem"` attributes.

### Step 5: Collapse toggle button

Add a toggle button at the bottom of the sidebar:

```tsx
<button
  className="collapse-toggle"
  onClick={() => setCollapsed(!collapsed)}
  aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
  title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
>
  {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
</button>
```

### Step 6: Collapsed state — icons only

When collapsed, show only the icon for each nav item. Add tooltips to show the label:

```tsx
{collapsed ? (
  <Tooltip content={item.label} side="right">
    <span className="nav-item__icon">{item.icon}</span>
  </Tooltip>
) : (
  <>
    <span className="nav-item__icon">{item.icon}</span>
    <span className="nav-item__label">{item.label}</span>
  </>
)}
```

The label should animate out (fade + slide) during collapse.

---

## Checklist

### Preparation
- [ ] Review current `Sidebar.tsx` (16 KB) and identify all hardcoded values
- [ ] List all navigation items and their icons
- [ ] Ensure U-01 tokens are available

### Implementation
- [ ] Add collapse/expand state with localStorage persistence
- [ ] Implement animated width transition (under 200ms)
- [ ] Replace all hardcoded colors/sizes with design tokens
- [ ] Redesign active state with accent bar + background highlight
- [ ] Add hover state with smooth transition
- [ ] Add keyboard navigation (arrow keys, Enter, Space)
- [ ] Add collapse toggle button with icon
- [ ] Collapsed state shows icons only with tooltips
- [ ] Label text animates out during collapse (fade + slide)
- [ ] Add proper ARIA attributes (`role="navigation"`, `role="menuitem"`, `aria-current="page"`)

### Testing
- [ ] Visual test: sidebar collapses/expands smoothly
- [ ] Timing test: width transition completes in under 200ms
- [ ] Keyboard test: Tab to sidebar, arrow keys navigate, Enter activates
- [ ] Persistence test: refresh page, collapse state is preserved
- [ ] Active state test: correct item highlighted on each page

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use `display: none` to hide labels on collapse.** This causes a jarring jump. Use `opacity`, `width`, and `overflow: hidden` for a smooth transition.

> **🚫 DO NOT break the layout of the main content area.** The main content must smoothly fill the space freed by the sidebar collapse. Use CSS Grid or Flexbox with the sidebar width as a column track.

> **🚫 DO NOT add a hamburger menu.** This is a desktop app, not mobile. The sidebar collapses to an icon strip, not a hidden menu.

> **🚫 DO NOT animate with JavaScript.** Use CSS transitions for width, opacity, and transform. They're GPU-accelerated and smoother than JS animations for layout properties.

> **🚫 DO NOT forget focus management.** When the sidebar collapses, focus should not be lost. If a nav item was focused, it stays focused in the collapsed state.

---

## Exit Criteria

- [ ] **Sidebar collapses/expands with animation** — smooth width transition
- [ ] **Active page highlighted with accent** — brand pink indicator bar + muted background
- [ ] **Keyboard nav works** — Tab into sidebar, Arrow keys move between items, Enter activates
- [ ] **Width transition under 200ms** — measure with DevTools Performance tab
- [ ] **Collapse state persisted** — survives page refresh
- [ ] **All design tokens used** — zero hardcoded colors or pixel values
