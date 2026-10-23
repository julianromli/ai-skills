---
name: skeleton-dither
description: Use when building a loading skeleton or a content/image reveal that should feel ASCII or dithered - a shimmering glyph skeleton (░▒▓█) that decodes into the real text and images, for cards, profiles, dashboards and heroes. Based on ascii-reveal by Quan Hoang (MIT).
---

# skeleton-dither

An ASCII loading state in two parts. First, a **dither skeleton**: shaded glyph bars (`░▒▓█`) with a denser band sweeping across them. Then a **decode reveal**: when data lands, every character scrambles into place, and images resolve from coarse glyph cells into real pixels. Both move as one radial wave.

Source: [ascii-reveal](https://quanhoangindex.github.io/ascii-reveal/) by Quan Hoang, from the repo [quanhoangindex/ascii-reveal](https://github.com/quanhoangindex/ascii-reveal) (v0.3.0). It's **MIT licensed**, so copying or adapting it is allowed if you keep the copyright notice. You can also install the original with `npm i github:quanhoangindex/ascii-reveal`; it includes `ascii-reveal/core` for non-React use. The reference file `skeleton-dither.js` in this skill's folder is a clean, smaller rewrite. It credits the original in its header. The folder also has `demo/` (working demo plus `verify.py`) and `shots/` (demo vs original screenshots).

## When to use
- Skeleton or loading states for cards, profiles, dashboards and stats that should feel crafted, not gray.
- Revealing a hero, image or card on mount, on route change, or when it scrolls into view.
- Brands that are techy, editorial or terminal-like. Skip it for dense forms, for anything that needs a calm feel (medical, finance errors), and for content that has to be readable at 0 ms.

## How it works
1. **Skeleton: pure HTML and CSS, painted on the first frame, no JS at runtime.**
   - Each line is 3 stacked `white-space:pre` spans:
     - a faint **base** row (opacity .22),
     - two **wave** rows that use denser glyphs and alternate every 120 ms (`steps(1)` visibility flip), so the glyphs inside the band look like they scramble.
   - A `mask-image` gradient band (55% wide) sweeps from `-120%` to `220%` over 1.8 s with `cubic-bezier(.45,.05,.55,.95)`.
   - Each line is delayed 0.09 s more than the one above, so the sweep reads as one diagonal band.
   - Glyph rows come from a deterministic integer hash of (index, seed), so SSR and client output match.
2. **Reveal: one `<canvas>` overlay above the real DOM.**
   - The real content stays in the DOM at its real position. Nothing shifts, and screen readers read it the whole time.
   - Text is hidden with `-webkit-text-fill-color:transparent`, so `currentColor` icons stay visible.
   - Images, and fades marked with `[data-sd="fade"]`, are hidden through `opacity: var(--sd-o)`.
   - **The wave:**
     - Each target starts at `offset = min(distance(target centre, origin) / 3.2 px/ms, 220 ms)`.
     - The default origin is the centre. It can also be `top-left` or `{x,y}` in viewport px; pass `{x:e.clientX,y:e.clientY}` to start from the pointer.
   - **Text:**
     - Each grapheme is measured with a `Range`.
     - Character k starts at `s0 = k/n·spread·0.72 + rand·spread·0.28`, with `spread = min(200, 40 + 4n)` ms.
     - It scrambles for `90 + rand·110` ms.
     - For the first 70% of that time it **condenses through the ramp** (light to dense, ±1 jitter 35% of the time). After that it picks random glyphs from the scramble set. Glyphs change every `tick` ms and are drawn in the mono font at 50% alpha.
     - Then it **locks**: the real character is drawn in the element's own font. When everything has landed, the overlay is removed and the DOM text is unhidden.
     - Numeric text scrambles through digits only.
   - **Images (450 ms):**
     - The pixels are drawn to an offscreen canvas.
     - The image is split into grids of mono cells (cell width = 0.62 × height), stepping coarse to fine: `[24,16,11,8,6]` px for decode and `[20,14,10,7,5]` for dither. Cells scale down on images smaller than 230 px.
     - Each cell takes the strongest of 5 samples. Its ink is `|lum − backdropLum| / max(bgLum, 1−bgLum)`, and that picks the glyph from the ramp.
     - Each cell appears when `gate < q·2.3`, with `gate = 0.5·noise + 0.5·distance from origin`. This gives an organic radial fill.
     - On each tick, 16% of the cells flicker by ±0.175 ink.
     - The real image cross-fades in from q = 0.68 (easeInOutCubic) while the glyphs fade out from q = 0.74.
   - **Fades (220 ms):** easeOutCubic opacity on the wave.

## Tuned parameters (from the original)
| Preset | ramp | scramble | image color | cells | tick |
|---|---|---|---|---|---|
| decode | ` .:-=+*#%@` | `A–Z 0–9 #%&*+=?/` | text color | 24,16,11,8,6 | 60 ms |
| dither | ` ░▒▓█` | `░▒▓█` | source pixels | 20,14,10,7,5 | 85 ms |
| terminal | ` .-:=+*#` | `01<>/\{}[]\|_=+-;:` | text color, `█` cursor leads | 22,15,10,7,6 | 40 ms |
| blueprint | ` ·-+=x#` | `+-/\|x·` | accent | 26,18,13,9,7 | 95 ms |

| Timing | vel | maxWave | spread | per char | media | fade |
|---|---|---|---|---|---|---|
| fast (data, readable ~400 ms) | 3.2 px/ms | 220 ms | min(200, 40+4n) | 90+110·r | 450 | 220 |
| cinematic (hero) | 1.15 px/ms | ∞ | min(720, 90+13n) | 200+240·r | 1150 | 420 |

Skeleton variants:

| Variant | base | wave | base opacity | wave opacity | band | notes |
|---|---|---|---|---|---|---|
| **dither** | `░░░░▒` | `▒▓▓█▓▒` | .22 | .75 | 55% | `line-height:1`, `letter-spacing:-.02em` |
| scan | `··:·:-` | `+=*#%@&$` | .28 | .95 | 38% | 8% gaps |
| braille | `⠢⠔⠑…` | `⣿⣷⣯…` | .35 | 1 | 40% | |
| terminal | `01` | `01` | .16 | 1 | 35% | 1.5 s sweep, accent color |

Rows are 160 glyphs long and clipped by `overflow:hidden`. Block skeletons (images, avatars) get `rows` lines and a 6% `currentColor` tint background.

Fonts: Geist for UI and Geist Mono for glyphs (`--sd-font`). The demo page background is `#f6f6f7` and the text is `#141416`.

## Implementation steps
1. Copy `skeleton-dither.js` from this skill's folder (about 300 lines, no dependencies) into the project, then call `injectSkeletonCSS()` once.
2. While loading, render `skeletonHTML({ variant:'dither', lines:2, widths:['55%','40%'], seed })` per text block, and `skeletonHTML({ rows: 26 })` inside image boxes. Give the boxes fixed sizes so the skeleton reserves the layout. Use `circle:true` for avatars. Give neighbouring skeletons different `seed`s.
3. When data arrives, swap in the real markup, then `await createReveal(container, { preset:'decode', duration:'fast', origin:'center' }).reveal()`.
4. Mark buttons and chips `data-sd="fade"`. Use `data-sd="skip"` for UI that must stay usable.
5. Theme with `--sd-font`, `--sd-color` (skeleton glyphs) and `--sd-accent` (for the terminal and blueprint looks).

Skeleton markup produced, for SSR or any templating:
```html
<span class="sd sd-dither" data-sd-skeleton aria-hidden="true">
  <span class="sd-line" style="width:55%;--d:0s">
    <span class="sd-base">░░▒░░░…</span><span class="sd-wave">▓█▒▓…</span><span class="sd-wave">▒▓▓█…</span>
  </span>
</span>
```

Core reveal loop (simplified; the full version is in `skeleton-dither.js`):
```js
const t0 = performance.now() + 16;
function frame(now) {
  const local = now - t0, paint = now - lastPaint >= 30;    // glyphs ~30fps, opacity every frame
  if (paint) { lastPaint = now; ctx.clearRect(0, 0, W, H); }
  let done = true;
  for (const t of targets) {
    const lt = clamp(local - t.offset, 0, t.dur);           // offset = radial wave delay
    if (local - t.offset < t.dur) done = false;
    t.draw(lt, paint);                                      // text: ramp→scramble→real; media: glyph grid→pixels
  }
  done ? finish() : requestAnimationFrame(frame);           // finish: remove canvas, unhide DOM
}
```

## React wrapper
```tsx
function DitherReveal({ loading, children, preset = 'decode' }) {
  const ref = useRef<HTMLDivElement>(null);
  const was = useRef(loading);
  useLayoutEffect(() => {           // layout effect: hide before first paint, no flash
    if (was.current && !loading && ref.current) createReveal(ref.current, { preset }).reveal();
    was.current = loading;
  }, [loading]);
  return <div ref={ref} aria-busy={loading}>{children}</div>;
}
// <DitherReveal loading={!data}>{data ? <Profile/> : <Skeleton/>}</DitherReveal>
// Skeleton = <span dangerouslySetInnerHTML={{__html: skeletonHTML({lines:3})}}/>
```
- In Next.js, mark the wrapper `"use client"`.
- Don't animate content that was server-rendered on hydration. It's already readable.
- If you'd rather not maintain your own copy, use the original `ascii-reveal` package (`<AsciiReveal loading>` and `<AsciiSkeleton>`).

## Performance
- Use one canvas per reveal, sized to the animated area, with DPR capped at 2. Precompute each image grid once per cell step and sample pixels once (`willReadFrequently`, OffscreenCanvas).
- Repaint glyphs at about 30 fps, since glyphs only change every 40–95 ms. Opacity cross-fades still update every frame.
- Use one shared rAF loop. Stop the loop as soon as every target has landed, and remove the canvas.
- The original also does these:
  - It bakes landed text onto a second canvas.
  - It only measures the viewport plus 120 px. Sections below the fold are hidden instantly and decode when an IntersectionObserver sees them.
  - A **watchdog** watches frame times. After 8 frames over 45 ms, it finishes the reveal and uses fades for the next 10 s.
  - A **ResizeObserver** finishes the reveal if the root resizes mid-run.
- Wait for `document.fonts.ready` and image `decode()` (900 ms cap) before measuring. Cross-origin images without CORS fall back to a neutral noise texture.
- rAF pauses on hidden tabs automatically. For looping shimmers, also pause them when they're off screen (IntersectionObserver).

## Accessibility
- `prefers-reduced-motion: reduce`:
  - the skeleton sweep is removed (`.sd-wave{display:none}`),
  - the reveal becomes a 220 ms opacity fade,
  - hides are instant.
- The skeleton and the overlay are `aria-hidden="true"`. Put `aria-busy="true"` on the loading region and remove it when the reveal finishes.
- The real text stays in the DOM and in the accessibility tree the whole time. Never put the content only on the canvas.
- Status text such as "all ready in 1.6 s" goes in `aria-live="polite"`.

## Tuning tips
- **Data or UI:** use `fast`. Heroes and replays use `cinematic` or `speed: 0.6`.
- **Origin:** `center` for cards. `top-left` reads like a scan. Use `{x:e.clientX,y:e.clientY}` for click-to-replay.
- **Color images:** use `dither` (source colors). Use `decode` or `blueprint` for a mono or brand look.
- **On a brand color,** set `--sd-color` to a darker tint of the text color. Keep base opacity at .2–.3 so bars read as shapes, not noise.
- **If it looks noisy,** lower the flicker rate (16%) or raise `tick`. If it feels slow, cap `maxWave` lower. Content should be readable in about 400 ms.
- **Fonts:** glyph alignment needs a monospace font with full block and braille coverage (Geist Mono, JetBrains Mono, SF Mono).

## Demo and verification
- The demo is `demo/index.html`, with skeleton/preset toggles and Reload. Serve the skill folder (`python3 -m http.server 8811`) and open `/demo/`.
- `demo/verify.py` (Playwright) runs from `demo/`. It saves screenshots to `../shots/`, checks for console errors, checks that no `data-sd-*` attributes or overlays are left behind, and runs the reduced-motion path.
