# Browser implementation reference
> The browser modules named below (`engine.js`, `picture.js`, …) belonged to the original browser-based package and are **not bundled** here. This skill's raea engine (`engine/edit.tsx`, `engine/look.py`) replaces them; read this file only for the layer logic.

These small modules preserve useful implementation techniques for temporal film grain, highlight bloom, soft type, selective stepped timing, and presenter splits. They are **building blocks, not a complete renderer or an existing project to run**. Create a new composition, source/asset manifest, transcript and timestamps, stage, media loader, masking system, frame capture, audio assembly, and encoder for each video. An implementation in another available renderer is acceptable if the visual result follows the skill.

## Included modules and dependencies

Paths below are relative to this document. Keep the JavaScript files together so their relative imports resolve.

| File | Purpose | Required support |
|---|---|---|
| `engine.js` | Easing, absolute-time key sampling, crop geometry, selective `posterT()` | No imports; caller supplies current project dimensions and tracking |
| `picture.js` | `Picture`: 2D composition input followed by WebGL grain/bloom/grade | Browser DOM, 2D canvas, functioning WebGL, decoded same-origin or CORS-safe media |
| `split-layout.js` | Shared picture/type/effect-region geometry for presenter split entry | `engine.js`; caller implements drawing and clipping |
| `typeLayers.js` | DOM emphasis text driven by programme time | `engine.js`, font tokens and corresponding CSS |
| `fonts.js` | Three font-role stacks; `applyFontTokens()` | Available fonts verified on the actual machine |
| `captions.js` | Word-timed DOM captions | `engine.js`, `fonts.js`, matching CSS, a new transcript and timings |
| `reel.css` | Historical CSS examples for the included text classes | Adapt selectors, stage size and desired styles for the new project |

Version numbers in source comments are historical provenance, not target dimensions, scene IDs, validation rules or editorial instructions. The reference includes older optional looks and transitions; use only the modes permitted by the current skill. In particular, legacy neon, hard B&W, thermal, halftone, spring, bounce and flash options are not style defaults.

## New-project setup and render order

1. Read the actual source metadata and requested delivery format. Set `width`, `height`, `fps` and duration from this project. Do not reuse an old timeline, crop track, media path, cache or audio mix.
2. Create an explicitly sized stage and canvas. Override the historical `#stage { width: 1920px; height: 1440px; }` rule. CSS pixels must match master-frame pixels before any preview-only scaling. Size the output canvas before constructing `Picture`; its composition canvas and bloom buffers are allocated in the constructor and do not resize automatically.
3. Choose one verified installed or properly loaded font per role, update `FONT`/CSS consistently, call `applyFontTokens()`, and wait for `document.fonts.ready` **before** constructing `Captions`, which measures glyph widths immediately. Rebuild caption measurements after changing fonts, font size or stage geometry.
4. Build scene, type and caption data from the new material. All times below are seconds on the new programme timeline. Decode/seek media to the correct source times before rendering each frame.
5. For frame index `n`, calculate `t = n / fps`. Determine current/outgoing scene geometry; use the same split result for picture placement, clipping, effect regions and panel text. Draw the picture into `picture.ctx`, then call `picture.post(t, explicitEffects, fps)`.
6. Update emphasis text with `type.update(t, split?.typeMotion ?? null)` and captions with `captions.update(t)`. These DOM layers are separate from the WebGL canvas. A canvas-only export will omit them. Capture the whole composed stage or composite text through an equivalent rendering path.
7. For occluded text, use the actual layer order `background → text → exact foreground cutout`, with new tracked masks for the current source, crop and timestamp. The six included modules do not generate masks or provide a ready occlusion compositor. Text that must stay clean belongs above the grain pass; a foreground cutout used above it must match the underlying picture treatment.
8. Capture every completed frame after media and fonts are ready; mux the new project’s audio and encode an actual video. The snippets do not provide frame capture, media loading, audio mixing or MP4 export. Verify the final encoded video, not just the browser preview.

## Picture API and safe starting values

```js
const picture = new Picture(outputCanvas);
// The caller clears and draws the complete picture here for every frame:
const ctx = picture.ctx;
ctx.clearRect(0, 0, outputCanvas.width, outputCanvas.height);
// ...draw decoded, cropped footage and inserts...
picture.post(t, {
  grade: 'clean', exposure: 1,
  grainIns: 0.018, grainOut: 0,
  grainSize: 1.15, grainColor: 0,
  grainRect: [0, 0, 1, 1],
  bloom: 0.12, bloomThr: 0.68,
  film: 0, age: 0, dust: 0, halation: 0, vignette: 0,
  blurX: 0, rgb: 0, flash: 0, sweep: 1
}, fps);
```

These are conservative **test values**, not a guaranteed final look. Inspect light and dark real footage, export compression, and the intended viewing size; adjust the grain/bloom strength and size accordingly. `grainIns`/`grainOut` are additive grain amplitudes inside/outside the normalized rectangle `[left, top, right, bottom]`. `grainSize` is measured against the actual output pixels. `post()` hashes the absolute frame index for fresh per-frame grain. Do not pass posterized time to `post()`.

Important behavior to account for:

- `Picture` assumes WebGL exists; its constructor does not supply a graceful non-WebGL fallback. Check support, shader compilation, available codecs and actual media decoding before choosing this path. The shader is computationally expensive at high resolutions.
- `grainRect` confines grain selection, bloom, `film` and `age`, **not** the general grade, exposure, vignette, RGB shift or blur. For a B&W insert beside a clean presenter, grade the insert before composition or implement a correctly masked grade. Setting `grade: 'bw'` on the final split would make the presenter B&W too.
- The bright-pass blur samples the full composition before bloom is restricted to `grainRect`. At a split boundary it can pick up light from the neighboring panel. For strict isolation, process bloom on the insert before composition or mask the bright-pass source as well; inspect the moving seam.
- Defaults include `halation: 1` and `vignette: 0.35`. Always specify them explicitly. `film > 0` automatically adds weave, softness, exposure flicker, print falloff and potentially colored halation. `age: 0` does **not** disable all that flicker. Keep `film: 0` when using clean temporal grain and restrained bloom without aging; add needed source softness separately.
- The B&W grade is `grade: 'bw'`; `bw_hard` is a legacy hard-contrast option. General `film` grade and the separate `film` amount are different controls. Do not infer one from the other.
- A resized canvas requires recreated internal buffers. The output context uses `preserveDrawingBuffer: false`; capture through a render path verified to read the frame at the right moment, not through an arbitrary delayed canvas readback.

## Presenter split schema

```js
const spec = {
  t0: sceneStart, t1: sceneEnd,
  split: {
    dir: 'h', at: 0.5,
    entry: { duration: 0.4 },
    a: { kind: 'presenter' },
    b: { kind: 'insert' }
  }
};
const layout = splitLayout(spec, t, { x: 0, y: 0, w: width, h: height });
// layout.a / layout.b are the current picture rectangles.
// layout.grainRect is normalized; layout.typeMotion describes panel text motion.
```

`dir: 'h'` means left/right panels. The animation runs only when exactly one panel has `kind: 'presenter'`, and `entry !== false`. With the presenter in `a`, the right insert slides from the right; with the presenter in `b`, the left insert slides from the left. The function calculates geometry only; the caller must keep the insert’s final crop, clip off-stage pixels, and reframe the presenter without stretching. Set `at` explicitly. Avoid automatic direction based on frame shape.

The included vertical path and its effect rectangle are historical logic, not a generalized animated top/bottom splitter. Do not use it for a new transition without adapting and inspecting it. `TypeLayers` identifies panel membership heuristically from layer X and lifetime; a text bridge extending outside the split’s lifetime will not move with the panel. Prefer explicit new-project ownership metadata if the layout needs more complex cases.

## Emphasis text schema

```js
const layers = [{
  id: 'new-title', style: 'display_sans', text: 'A meaningful phrase',
  t0: 2.0, t1: 4.0,
  x: width * 0.5, y: height * 0.66, size: height * 0.075,
  align: 'center', w: width * 0.8, color: '#f2efe8',
  enter: 'soft', enterDur: 0.32, exit: 'drift', exitDur: 0.25,
  motion: { drift: [0, -0.015] },
  posterize: { fps: 12.5, from: 2.0, to: 2.4 }
}];
const type = new TypeLayers(typeRoot, layers, [width, height], {});
```

Coordinates, widths and `size` are master-frame pixels; motion drift is in em per second. `words: [{w, t, it?}, ...]` supplies absolute per-word reveal times. Use `wordMotion: 'soft'` when needed. Inline `*italic words*` in `text` selects the serif accent. Common style roles are `display_sans`, `display_serif`, `credit`, `number` and `typewriter`; use only those that serve the content. `number` also supports `sub`, `qual` and `src`.

`posterize` may be a frequency number, a `{fps, from, to}` window, or a list of windows. It affects this layer’s animation clock, not the picture. At a 25 fps master, 12.5 fps creates regular two-frame steps. Choose a compatible cadence for another master rate. Keep visibility and meaningful reading holds intact. A title bridging a cut must be one persistent layer with a continuous clock, not separate restarted copies.

The included CSS contains historical fixed values, legacy effects and `white-space` behavior. Do not assume setting `w` will automatically wrap a title. Author line breaks or a measured layout, and inspect all actual glyph bounds. The module has no automatic subject-avoidance or safe-area layout engine.

## Caption schema

```js
const data = {
  size: height * 0.032,
  chunks: [{
    t0: 2.0, t1: 3.2, x: width * 0.5, y: height * 0.82,
    maxW: width * 0.8,
    lines: [[0, 1]],
    words: [
      { w: 'Meaningful', t0: 2.0, t1: 2.55, accent: false },
      { w: 'words', t0: 2.55, t1: 3.2, accent: true }
    ]
  }]
};
const captions = new Captions(captionRoot, data, width, height);
```

`lines` lists indices into that chunk’s `words`; do not reuse an old transcript. Optional chunk fields include `ink`, `suppressed` and `posterize`. A chunk position is cached at its first visible time so it stays stable through a picture cut. Font measurements and cached positions require rebuilding after relevant layout changes. Captions do not receive split-panel motion automatically. Integrate them deliberately rather than assuming the emphasis-text split behavior also applies.

## Font verification and scope of checking

The historical stacks prefer Helvetica Neue, Didot and Menlo, which may be absent on another machine. Choose one working family per role, load it where necessary and check glyph coverage, visual identity and measured widths. `familyOf()` checks the CSS stack’s first name; it does **not** prove that the intended font rendered. Neither a successful import nor a successful shader compile establishes good visual quality or a valid finished MP4.

Create fresh project-specific validation: actual frame count and aspect, complete decodability, source-time mapping, audio synchronization, legibility, temporal grain, split seams and mask stability. No historical validation report, opening-frame cache, prebuilt audio or scene allowlist is part of these building blocks.
