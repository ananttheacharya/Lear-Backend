# U-01 — Design System Audit and Token Overhaul

**Owner:** Avi
**Priority:** P0
**Status:** ⬜ Not Started
**Estimated effort:** 2 days
**Depends on:** Nothing (start day 1)
**Blocks:** U-02, U-03, U-04 (all UI work depends on tokens existing)

---

## Objective

Audit the current `index.css` and define a comprehensive design token system covering: spacing scale, typography scale, color palette, elevation/shadow system, border-radius scale, and motion/easing tokens. Every component should reference tokens via CSS custom properties — no raw values.

---

## Why This Matters

- **Currently:** `index.css` (81 lines) has a minimal `@theme` block with 10 color variables and a few utility classes (`glass-panel`, `glass-card`, `pulse-radar`). Individual components use a mix of token references AND hardcoded values. There's no spacing scale, no typography scale, no shadow system, no motion tokens.
- **After:** A single `design-tokens.css` file defines ALL visual primitives. Components are consistent because they reference the same token set. Changing the brand color or spacing scale is a single-file edit.

---

## Current State

From `desktop/src/index.css`:

```css
@theme {
  --color-background: #080B11;
  --color-surface: #0E131F;
  --color-surface-elevated: #151C2C;
  --color-accent: #FF3A89;
  --color-accent-light: #FF66A5;
  --color-accent-glow: rgba(255, 58, 137, 0.25);
  --color-cyan: #06B6D4;
  --color-amber: #F59E0B;
  --color-rose: #F43F5E;
  --color-border-subtle: rgba(255, 255, 255, 0.08);
  --color-border-hover: rgba(255, 255, 255, 0.16);
}
```

**What's missing:**
- Spacing scale (no consistent spacing between elements)
- Typography scale (font sizes, weights, line heights)
- Full neutral color scale (only 3 background shades)
- Semantic colors (success, warning, error, info)
- Elevation/shadow system
- Border-radius scale
- Motion/easing tokens
- Font family tokens (currently using a fallback stack in `body`, not tokens)

---

## Implementation Plan

### Step 1: Audit all existing components

Scan all 25 component files for hardcoded values:

```bash
# Find all raw color values
grep -rn "#[0-9a-fA-F]\{3,8\}" desktop/src/components/ --include="*.tsx"

# Find all raw pixel values (spacing, font-size, etc.)
grep -rn "[0-9]\+px" desktop/src/components/ --include="*.tsx"

# Find all raw rgba values
grep -rn "rgba(" desktop/src/components/ --include="*.tsx"
```

Document every unique value found — these all need token equivalents.

### Step 2: Define the token system

Create `desktop/src/design-tokens.css`:

```css
/* ═══════════════════════════════════════════════════════════════
   LEAR DESIGN SYSTEM — Token Definitions
   Every visual primitive is defined here. Components reference
   these tokens — never raw values.
   ═══════════════════════════════════════════════════════════════ */

:root {
  /* ── Color: Brand ─────────────────────────────────────────── */
  --color-brand-primary: #FF3A89;
  --color-brand-primary-light: #FF66A5;
  --color-brand-primary-dark: #D42F73;
  --color-brand-primary-glow: rgba(255, 58, 137, 0.25);
  --color-brand-primary-muted: rgba(255, 58, 137, 0.12);

  /* ── Color: Neutrals (Dark Mode) ──────────────────────────── */
  --color-neutral-950: #050810;     /* Deepest background */
  --color-neutral-900: #080B11;     /* App background */
  --color-neutral-850: #0B0F18;     /* Subtle surface */
  --color-neutral-800: #0E131F;     /* Card surface */
  --color-neutral-750: #111827;     /* Elevated surface */
  --color-neutral-700: #151C2C;     /* Higher elevation */
  --color-neutral-600: #1E2A3D;     /* Borders, dividers */
  --color-neutral-500: #374151;     /* Muted elements */
  --color-neutral-400: #6B7280;     /* Placeholder text */
  --color-neutral-300: #9CA3AF;     /* Secondary text */
  --color-neutral-200: #D1D5DB;     /* Primary text */
  --color-neutral-100: #F3F4F6;     /* Bright text */
  --color-neutral-50:  #F9FAFB;     /* Maximum brightness */

  /* ── Color: Semantic ──────────────────────────────────────── */
  --color-success: #10B981;
  --color-success-light: #34D399;
  --color-success-muted: rgba(16, 185, 129, 0.12);
  --color-warning: #F59E0B;
  --color-warning-light: #FBBF24;
  --color-warning-muted: rgba(245, 158, 11, 0.12);
  --color-error: #EF4444;
  --color-error-light: #F87171;
  --color-error-muted: rgba(239, 68, 68, 0.12);
  --color-info: #06B6D4;
  --color-info-light: #22D3EE;
  --color-info-muted: rgba(6, 182, 212, 0.12);

  /* ── Color: Borders ───────────────────────────────────────── */
  --color-border-default: rgba(255, 255, 255, 0.08);
  --color-border-hover: rgba(255, 255, 255, 0.16);
  --color-border-focus: rgba(255, 58, 137, 0.5);
  --color-border-active: var(--color-brand-primary);

  /* ── Typography: Font Families ────────────────────────────── */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-display: 'Outfit', 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;

  /* ── Typography: Font Sizes ───────────────────────────────── */
  --text-xs:   0.75rem;     /* 12px */
  --text-sm:   0.875rem;    /* 14px */
  --text-base: 1rem;        /* 16px */
  --text-lg:   1.125rem;    /* 18px */
  --text-xl:   1.25rem;     /* 20px */
  --text-2xl:  1.5rem;      /* 24px */
  --text-3xl:  1.875rem;    /* 30px */
  --text-4xl:  2.25rem;     /* 36px */

  /* ── Typography: Font Weights ─────────────────────────────── */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* ── Typography: Line Heights ─────────────────────────────── */
  --leading-tight:  1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* ── Spacing Scale ────────────────────────────────────────── */
  --space-0:   0;
  --space-0.5: 0.125rem;   /* 2px  */
  --space-1:   0.25rem;    /* 4px  */
  --space-1.5: 0.375rem;   /* 6px  */
  --space-2:   0.5rem;     /* 8px  */
  --space-3:   0.75rem;    /* 12px */
  --space-4:   1rem;       /* 16px */
  --space-5:   1.25rem;    /* 20px */
  --space-6:   1.5rem;     /* 24px */
  --space-8:   2rem;       /* 32px */
  --space-10:  2.5rem;     /* 40px */
  --space-12:  3rem;       /* 48px */
  --space-16:  4rem;       /* 64px */
  --space-20:  5rem;       /* 80px */

  /* ── Border Radius ────────────────────────────────────────── */
  --radius-sm:   0.25rem;   /* 4px  */
  --radius-md:   0.375rem;  /* 6px  */
  --radius-lg:   0.5rem;    /* 8px  */
  --radius-xl:   0.75rem;   /* 12px */
  --radius-2xl:  1rem;      /* 16px */
  --radius-full: 9999px;    /* Pill shape */

  /* ── Elevation / Shadows ──────────────────────────────────── */
  --shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md:   0 4px 8px rgba(0, 0, 0, 0.4);
  --shadow-lg:   0 8px 24px rgba(0, 0, 0, 0.5);
  --shadow-xl:   0 16px 48px rgba(0, 0, 0, 0.6);
  --shadow-glow: 0 0 20px var(--color-brand-primary-glow);
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.3), 0 0 1px rgba(255, 255, 255, 0.06);

  /* ── Motion / Easing ──────────────────────────────────────── */
  --ease-out:     cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out:  cubic-bezier(0.45, 0, 0.55, 1);
  --ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-bounce:  cubic-bezier(0.68, -0.55, 0.27, 1.55);

  --duration-fast:    100ms;
  --duration-normal:  200ms;
  --duration-slow:    300ms;
  --duration-slower:  500ms;

  /* ── Z-Index Scale ────────────────────────────────────────── */
  --z-base:    0;
  --z-dropdown: 10;
  --z-sticky:  20;
  --z-overlay: 30;
  --z-modal:   40;
  --z-toast:   50;
  --z-tooltip: 60;
}
```

### Step 3: Import Google Fonts

Add to `desktop/index.html` (or via CSS `@import`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### Step 4: Update `index.css` to import tokens

```css
@import "./design-tokens.css";
@import "tailwindcss";

/* Override Tailwind's @theme with our tokens */
@theme {
  /* Map our tokens to Tailwind's expected shape */
  --color-background: var(--color-neutral-900);
  --color-surface: var(--color-neutral-800);
  /* ... etc */
}
```

### Step 5: Migrate components to use tokens

For each of the 25 components, replace hardcoded values with token references:

```tsx
// Before:
<div style={{ padding: '16px', borderRadius: '8px', background: '#0E131F' }}>

// After:
<div style={{ padding: 'var(--space-4)', borderRadius: 'var(--radius-lg)', background: 'var(--color-neutral-800)' }}>
```

Or via Tailwind classes that reference the tokens.

### Step 6: Take before/after screenshots

Before starting the migration, take screenshots of:
- Dashboard
- Sidebar
- Chat
- Settings
- Integrations

After applying tokens, take the same screenshots. The visual diff should be minimal (same appearance, different underlying tokens).

---

## Checklist

### Audit
- [ ] Scan all 25 components for hardcoded color values
- [ ] Scan all components for hardcoded spacing (px values)
- [ ] Scan all components for hardcoded font sizes
- [ ] Scan all components for hardcoded border-radius values
- [ ] Scan all components for hardcoded shadows
- [ ] Document all unique values found

### Token Definition
- [ ] Create `desktop/src/design-tokens.css`
- [ ] Define brand color palette (primary + variants)
- [ ] Define neutral color scale (10+ steps)
- [ ] Define semantic colors (success, warning, error, info)
- [ ] Define border colors
- [ ] Define font family tokens (Inter, Outfit, JetBrains Mono)
- [ ] Define font size scale
- [ ] Define font weight tokens
- [ ] Define line height tokens
- [ ] Define spacing scale
- [ ] Define border-radius scale
- [ ] Define elevation/shadow system
- [ ] Define motion/easing tokens
- [ ] Define z-index scale
- [ ] Import Google Fonts

### Migration
- [ ] Import `design-tokens.css` in `index.css`
- [ ] Update existing `@theme` block to reference tokens
- [ ] Take before screenshots (Dashboard, Sidebar, Chat, Settings, Integrations)
- [ ] Migrate hardcoded values in components to token references
- [ ] Take after screenshots — visual diff should be minimal
- [ ] Verify dark mode works with all tokens

---

## Anti-Patterns to Avoid

> **🚫 DO NOT define tokens in Tailwind config files.** Tokens should be vanilla CSS custom properties, not Tailwind-specific. This makes them usable in inline styles, CSS modules, and any CSS-in-JS solution.

> **🚫 DO NOT create too-specific tokens.** `--sidebar-background` is wrong. `--color-neutral-800` is right. Tokens should be reusable across components, not tied to one element. Semantic aliases (e.g., `--color-surface`) that map to the scale are fine.

> **🚫 DO NOT change the visual appearance during this task.** This is a structural migration — the app should look IDENTICAL before and after. If you want to improve the design, that's a separate task.

> **🚫 DO NOT use `rem` or `em` inconsistently.** The spacing scale uses `rem` (relative to root). Stick with `rem` everywhere for consistency.

> **🚫 DO NOT remove Tailwind utility classes yet.** The app uses TailwindCSS. Tokens and Tailwind can coexist — the tokens feed into Tailwind's `@theme`.

---

## Exit Criteria

- [ ] **`design-tokens.css` file exists** with all tokens as CSS custom properties
- [ ] **Every component references tokens, not raw values** — grep for hardcoded `#hex` values returns 0 hits in component files (excluding token definitions)
- [ ] **Visual diff: before/after screenshots** show no visible regression
- [ ] **Google Fonts loaded** — Inter, Outfit, JetBrains Mono
- [ ] **All 25 components use the token system**
