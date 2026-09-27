# U-04 — Component Library Foundation

**Owner:** Avi
**Priority:** P1
**Status:** ⬜ Not Started
**Estimated effort:** 2 days
**Depends on:** U-01 (design tokens must exist)
**Blocks:** Nothing (but every future UI task benefits from these primitives)

---

## Objective

Create a set of reusable primitive UI components: `Button`, `Card`, `Badge`, `Input`, `Modal`, `Dropdown`, `Tooltip`, `Skeleton`, `EmptyState`. Every future component builds on these primitives. Each has TypeScript types, dark-mode support, size variants, and loading states.

---

## Why This Matters

- **Currently:** Each component in the app defines its own button styles, card layouts, input fields, etc. There are at least 5 different button styles scattered across components with inconsistent colors, sizes, padding, and hover states.
- **After:** A single set of primitives that look and behave consistently everywhere. Building a new page means composing these primitives, not designing new UI elements from scratch.

---

## Components to Build

### 1. `Button`

```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}
```

**Requirements:**
- Primary: brand pink background, white text
- Secondary: transparent with border, neutral text
- Ghost: no background, no border, subtle hover
- Danger: red variant for destructive actions
- Disabled state with reduced opacity (not a new color)
- Loading state: spinner replaces text, button not clickable
- Hover: subtle brightness change + scale (1.02) with `--ease-spring`
- Press: scale down (0.98) with `--ease-out`
- Focus: visible ring using `--color-border-focus`

### 2. `Card`

```tsx
interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  clickable?: boolean;
  children: React.ReactNode;
}
```

Uses `glass-card` or `glass-panel` from existing CSS, extended with design tokens.

### 3. `Badge`

```tsx
interface BadgeProps {
  variant: 'default' | 'success' | 'warning' | 'error' | 'info' | 'brand';
  size?: 'sm' | 'md';
  dot?: boolean;           // Pulsing dot indicator
  children: React.ReactNode;
}
```

### 4. `Input`

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}
```

### 5. `Modal`

```tsx
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'full';
  children: React.ReactNode;
  footer?: React.ReactNode;
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
}
```

**Requirements:**
- Backdrop blur overlay
- Slide-up + fade-in animation on open
- Fade-out on close
- Focus trap (Tab stays within modal)
- ESC key closes by default
- Stacks correctly with z-index

### 6. `Dropdown`

```tsx
interface DropdownProps {
  trigger: React.ReactNode;
  items: DropdownItem[];
  align?: 'left' | 'right';
  width?: number | 'trigger';   // Match trigger width or fixed
}

interface DropdownItem {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  danger?: boolean;
  disabled?: boolean;
  divider?: boolean;           // Render as a divider line
}
```

### 7. `Tooltip`

```tsx
interface TooltipProps {
  content: string | React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  delay?: number;             // ms before showing (default 300)
  children: React.ReactNode;
}
```

### 8. `Skeleton`

```tsx
interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  lines?: number;            // For text variant: number of text lines
  animate?: boolean;         // Default true — shimmer animation
}
```

Uses a shimmer animation (gradient slide) for a polished loading feel.

### 9. `EmptyState`

```tsx
interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

---

## File Structure

```
desktop/src/components/ui/
  Button.tsx
  Card.tsx
  Badge.tsx
  Input.tsx
  Modal.tsx
  Dropdown.tsx
  Tooltip.tsx
  Skeleton.tsx
  EmptyState.tsx
  index.ts               — re-exports all components
  ui.css                  — shared styles for primitives (uses design tokens)
  _preview.tsx            — Storybook-like preview page for all components
```

### Preview Page

Create `_preview.tsx` — a component that renders every primitive in every variant/size/state. This serves as a living style guide:

```tsx
const ComponentPreview = () => (
  <div className="preview-grid">
    <section>
      <h2>Buttons</h2>
      <div className="preview-row">
        <Button variant="primary" size="sm">Small</Button>
        <Button variant="primary" size="md">Medium</Button>
        <Button variant="primary" size="lg">Large</Button>
        <Button variant="primary" size="md" loading>Loading</Button>
        <Button variant="primary" size="md" disabled>Disabled</Button>
      </div>
      {/* ... repeat for each variant */}
    </section>
    {/* ... repeat for each component */}
  </div>
);
```

Wire it to a route (e.g., `/preview`) accessible only in development.

---

## Checklist

### Components (one at a time)
- [ ] `Button` — all variants, sizes, loading, disabled, hover/press animations
- [ ] `Card` — all variants, hoverable, clickable, glass effect
- [ ] `Badge` — all variants, dot indicator with pulse animation
- [ ] `Input` — label, error state, hint text, icon, focus ring
- [ ] `Modal` — backdrop blur, animation, focus trap, ESC close
- [ ] `Dropdown` — positioning, item variants, keyboard nav
- [ ] `Tooltip` — positioning, delay, fade animation
- [ ] `Skeleton` — shimmer animation, text/circular/rectangular variants
- [ ] `EmptyState` — icon + title + description + action button

### Quality per component
- [ ] TypeScript props interface exported
- [ ] All design tokens used (zero hardcoded values)
- [ ] Dark mode works (this IS a dark mode app)
- [ ] Size variants work (sm, md, lg where applicable)
- [ ] Loading states work (where applicable)
- [ ] Focus states visible for keyboard users
- [ ] ARIA attributes where needed (modal focus trap, tooltip aria-describedby, etc.)

### Preview page
- [ ] `_preview.tsx` renders every component in every variant
- [ ] Accessible at `/preview` route in development
- [ ] Organized by component with clear section headers

### Integration
- [ ] `index.ts` re-exports all components
- [ ] At least one existing component refactored to use a primitive (proof of concept)

---

## Anti-Patterns to Avoid

> **🚫 DO NOT use third-party component libraries** (Radix, Headless UI, Chakra, etc.) unless explicitly approved. The goal is a custom design system that matches the Lear brand. Third-party components have their own opinions about styling and behavior.

> **🚫 DO NOT add props for every possible CSS property.** `<Button marginTop="8px">` is wrong. The consuming component controls layout. Primitives control their own internal styling.

> **🚫 DO NOT use `children` for everything.** Structured components like `Modal` should have explicit `title`, `footer`, and `children` (body) props. This makes the API predictable.

> **🚫 DO NOT skip focus management.** Modal must trap focus. Dropdown must close on outside click. Tooltip must be keyboard-accessible. These are not optional polish — they're usability requirements.

> **🚫 DO NOT create "God components."** Each primitive should do ONE thing well. If a component has 20+ props, it's doing too much — split it.

---

## Exit Criteria

- [ ] **`components/ui/` directory with all 9 primitives**
- [ ] **Each has TypeScript types** — exported `interface FooProps`
- [ ] **Dark-mode support** — all variants look correct on dark background
- [ ] **Size variants** — sm/md/lg where applicable
- [ ] **Loading states** — Button, Input, Card
- [ ] **Storybook-like preview page** — all components visible at `/preview` in dev
- [ ] **At least one existing component refactored** to use a primitive
