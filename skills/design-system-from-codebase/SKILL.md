---
name: design-system-from-codebase
description: Use when the user wants a public design system site built from an existing app codebase (build mode), or wants an existing design system updated after the app changed (maintain mode). Audits the code, extracts tokens and components, and ships every change through one reviewed PR.
---

# Design system from codebase

Turn an existing app repo into a professional, public design-system site: tokens, foundations, components, copyable code and a shadcn registry. Then keep it in sync as the app grows.

## Pick the mode
- **Build:** no design system exists yet. Run steps 0 to 5.
- **Maintain:** a design system exists and the app changed. Skip to "Maintain mode".
- If unsure, look for an existing DS repo or folder and a CHANGELOG.md with a sync point.

## Hard rules
- The app code is the source of truth. A design file (Figma, Paper, Wonder) is secondary.
- Work on a branch. One PR per run. Never push to main and never merge without the user's explicit go. No force-push.
- Before anything goes public, scan the ported code for secrets, internal URLs, customer data and private API shapes. Remove them.
- Keep the app's brand. Copy only the structure and craft of a reference site, never its brand signature.

## 0. Intake (ask only what is missing)
- App repo and target: a new repo or a folder in the app repo.
- Optional design file.
- Brand assets: product icon, company logo or wordmark.
- Theme scope (light only, or light and dark). Public or private.
- Reference site for polish. Default: Palermo, https://palermo.tryprofound.com.

## 1. Audit the codebase (read-only)
- Stack: framework, styling (Tailwind version, CSS variables), component libraries (Base UI, Radix, shadcn), icon set, fonts.
- Tokens the app actually uses: colours with semantic roles, type scale, radius, spacing, shadows, motion durations and easings, z-index, breakpoints.
- Reusable components: variants, states, props, and how often each is used. Flag duplicates and one-offs.
- Large app: start with the most-used components. List the rest as a backlog.
- Design file present: diff it against the code. Code wins. Record the differences.
- Write audit.md with the stack, tokens, component inventory, gaps and top issues by impact.
- Send the user a short summary plus screenshots of the reference site. Confirm scope before you build.

## 2. Scaffold the site
- Default stack: Vite, React, TypeScript, TanStack Router (file-based routes), Tailwind v4, the app's own primitives, pnpm, GitHub Pages deploy on push to main, PR checks on every PR. If the app is not React, match its framework.
- Prefer one shared token source (a theme file or package) that the app and the site both import. If that is not possible yet, copy the tokens and note it as drift risk.
- Pages: Overview, Installation, Foundations (Colors, Typography, Radius, Elevation, Motion, Icons, Layout, others found), Components grouped by job (Actions, Forms, Overlays, Data, Navigation, Feedback).
- shadcn registry: r/theme.json plus r/<component>.json.
- Port components without business logic or API calls. Keep the app's exact values.
- Provenance (design-file names, code-only parts, design-vs-code diffs) goes in CONTRIBUTING.md, not on public pages.
- Create CHANGELOG.md with version 1.0.0 and the sync point: the app commit SHA you audited.

## 3. Public polish (defaults; the app's own tokens win)
- Top bar 56px: product icon, Search button with a Ctrl/Cmd+K command palette (dialog role, focus trap, arrow keys wrap, Enter opens, Esc closes, focus returns), GitHub link.
- Sidebar: sentence-case groups, active item marked by a thin left line, no pills or badges, a filter field.
- Page header: title 24/32 at weight 600, one lead line under 65ch, text-wrap balance, no overlines or jargon.
- Content column about 800px. Component pages about 880px.
- Specimen frame: one thin border, generous padding, no dot grid. Preview and Code text tabs inside the frame, Copy in the tab bar. Code in the app's mono at 13/20, line numbers hidden from screen readers.
- Foundations as large specimens (type stack, swatch cards with wrapping token names), not tables.
- Home: short intro, one primary CTA (install the theme), GitHub link, foundation tiles that show real tokens, compact component directory (2 columns on desktop, first-sentence descriptions, no truncation).
- Footer: product name and version, source link, company credit ("By <Company>" wordmark linked to the company site).
- Branding: product icon in the top bar, mobile drawer and favicons (32px PNG, 180px full-bleed apple-touch-icon). Optimise SVGs and strip generator comments. Use real logos in demos, never text placeholders.
- Mobile at 390px: drawer nav, search button, 44px tap targets, 16px inputs, no page-level sideways scroll. Variant grids switch to stacked lists when columns do not fit.
- Copy: plain English, short sentences, no internal jargon.
- Motion: respect prefers-reduced-motion. Keyboard-opened UI like the palette opens without animation.

## 4. Review before the PR
- Run a design review on the output: spacing, type, motion, accessibility, touch targets, AI-slop patterns. (If emil-* skills are available, use emil-ui-review, emil-unslop-design and emil-touch-and-accessibility.) Fix small issues. List larger ones.
- Typecheck, lint, tests (include an accessibility test for the palette) and build must pass. Registry output changes only when intended.
- Screenshots at 1440 and 390: home, one component page, typography, colors, the open palette. In maintain mode, before and after. Keep PR images on a separate assets branch so they never land in main.

## 5. Ship
- Open one PR: change list per step, deviations from the plan, remaining issues, screenshots.
- Iterate with new commits.
- On the user's go: update the README (live URL, search, brand asset paths, CONTRIBUTING link), merge, then verify the deployed site (title, favicon, credit, search, no console errors).

## Maintain mode (the app changed; the DS exists)
1. Read the last sync point from the DS CHANGELOG.md. Diff the app repo from that commit to now. No sync point: use the date of the last DS release and record a proper sync point this time.
2. Audit only the diff:
   - New or changed tokens. Hardcoded values that should be tokens.
   - New reusable components, new variants or props, removed or renamed components.
   - Duplicates: two components doing the same job. Propose one.
3. Classify each change: add, update, deprecate, or ignore (one-off). Ask the user only about unclear ones.
4. Update the DS on a branch: tokens, component pages, demos, registry entries, CONTRIBUTING provenance. Deprecate with a note and a planned removal version. Never delete in the same release.
5. Bump the version (new = minor, breaking = major, fixes = patch). Add a CHANGELOG entry with the new app commit SHA as the sync point.
6. Run steps 4 and 5. Nothing changed: report that and open no PR.
7. Suggest once, set up only on a yes:
   - A shared token package that the app and the DS both import.
   - DS demos that import the real components instead of copies.
   - An app CI check that warns on new components without docs and on hardcoded colours outside tokens.
   - A weekly scheduled run of maintain mode.

## Report
Short summary in the user's language: what changed, PR link, check, build and CI results, screenshots, open questions as a short list.
