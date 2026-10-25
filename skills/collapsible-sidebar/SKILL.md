---
name: collapsible-sidebar
description: Use this when building a sidebar that collapses to an icon rail, or any element that toggles between shown and hidden. Labels fade out before display:none and fade in on show, using CSS transition-behavior allow-discrete plus @starting-style, with no JS animation library.
---

# Collapsible sidebar (allow-discrete fade)

Source: @nonzeroexitcode (Daniel Petho) on Threads, https://www.threads.com/@nonzeroexitcode/post/De4xkSrE0Ze. Working demo: `examples/index.html` (normal vs allow-discrete, side by side).

## The problem
`display` is a discrete property. It has no in-between value. When a label goes to `display: none`, it disappears in the first frame, and any opacity transition on it never shows.

`transition-behavior: allow-discrete` makes the browser hold the old `display` value until the transition ends. Then `display: none` applies. `@starting-style` gives the entry a start value, so the element fades in when it comes back.

## Recipe
1. Sidebar width: transition `width` between the open and collapsed sizes. Use 200ms with a strong ease-out, `cubic-bezier(0.23, 1, 0.32, 1)`. Set `overflow: hidden` on the sidebar.
2. Label: put the text in its own element (`<span class="label">`). Keep the icon outside it. Icons never move or fade.
3. Label transition:
   ```css
   .label {
     opacity: 1;
     transition: opacity 150ms ease-out, display 150ms allow-discrete;
   }
   .sidebar[data-collapsed] .label {
     opacity: 0;
     display: none;
   }
   @starting-style {
     .label { opacity: 0; }
   }
   ```
4. Keep the `display` duration the same as the `opacity` duration. If the display duration is shorter, the fade is cut off.
5. Put the `@starting-style` block after the base rule. It needs equal or higher specificity than the rule it starts.
6. Rows: fixed height (32px desktop, 44px touch), `white-space: nowrap`, so the text never wraps while the width animates.

## Tailwind v4
- `transition-discrete` sets `transition-behavior: allow-discrete`.
- The `starting:` variant writes `@starting-style`, for example `starting:opacity-0`.
- Example label: `transition-[opacity,display] duration-150 ease-out transition-discrete starting:opacity-0 group-data-collapsed:hidden group-data-collapsed:opacity-0`.

## Accessibility
1. The toggle is a `<button>` with `aria-expanded` and `aria-controls` that points to the sidebar id. Its label changes with the state ("Collapse sidebar" / "Expand sidebar").
2. A label under `display: none` gives no accessible name. Put `aria-label` on each link, plus `title` (or a real tooltip) for mouse users on the collapsed rail.
3. Keep a visible `:focus-visible` ring on every link and on the toggle.
4. Under `prefers-reduced-motion: reduce`, set `transition: none` on the width and the label. The state still changes at once.
5. Hover styles go inside `@media (hover: hover)`, so touch taps do not leave a stuck hover.

## When it does not apply
- `allow-discrete` works only on an element that stays in the DOM and changes `display` (or `content-visibility`, or `overlay` for `<dialog>` and `[popover]`). It does not help an element that React or another framework unmounts. For an unmounted element, keep it mounted and hide it with CSS, or render a short-lived inert exit copy, or use an animation library with exit support.
- Do not animate `width` on a large, content-heavy layout where relayout is costly. Then animate `transform` on an overlay sidebar instead.

## Browser support
Baseline 2024: Chrome 117, Safari 17.4, Firefox 129. A browser without support hides and shows the label at once, with no fade. That is a safe fallback; no polyfill is needed.

## Verify
1. Open the page in Chromium. Collapse. Sample the label's computed `display` and `opacity` every frame for 200ms. Expected: `display` stays visible while opacity goes 1 to 0, then `display: none` at about 150ms.
2. Expand. Expected: opacity starts at 0 and rises to 1.
3. With reduced motion on: no transition, the state changes in one frame.
4. Tab through the collapsed rail: every link has a name and a visible focus ring.
