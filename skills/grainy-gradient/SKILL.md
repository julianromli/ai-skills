---
name: grainy-gradient
description: Use this when making soft, premium gradient backgrounds or covers (ElevenLabs / macOS wallpaper style) - blurred color blobs plus a fine grain noise layer, optional thin white line patterns, in HTML/CSS/Canvas with no images.
---

# Grainy gradient (ElevenLabs-style covers)

Source: @ianneo_ai breakdown of ElevenLabs blog covers (https://x.com/ianneo_ai/status/2113225499556381172).

## Why it looks premium
1. Color: 4-5 big color blobs overlap. Edges blur fully. No visible shapes.
2. Direction: top is light and cool. Bottom is dark and warm, like sky over ground.
3. Palette: use only neighbor hues on the color wheel (analogous). Example: blue-grey to sand-yellow to orange-red. Green goes only with blue and yellow.
4. Grain (the most important part): a 1-physical-pixel grey noise layer over everything. It shows in bright areas and almost disappears in dark areas. Grain breaks color banding and removes the plastic look, so the result feels like paper or out-of-focus film.
5. Optional pattern: thin white lines on top: rays, concentric contours, sound-wave lines, dot grid, lens shapes.

## Build recipe (HTML + CSS + Canvas, no images, no libraries)
1. Base: one top-to-bottom linear-gradient. Light and cool at the top, dark and warm at the bottom.
2. Blobs: stack 4 large radial-gradient layers that fade to transparent. Put them at the corners and edges, not the center.
3. Grain: draw a 128x128 random greyscale noise tile on a canvas. Tile it over the whole area with `mix-blend-mode: overlay` and `opacity: 0.4`. Size the canvas by `devicePixelRatio`, so 1 noise pixel = 1 physical pixel.
4. Pattern (optional): inline SVG of white lines. Stroke width 0.8px, opacity about 0.3. Use a radial `mask-image` so the center stays clear for text.
5. Text: white, centered, Inter 400, font size about 8% of card width, max 2 lines.
6. Card (for covers): radius 20px, inner 0.5px faint black border.
7. Motion (optional): blobs drift and scale a little over 20-28s with CSS animation. On hover, blobs move toward the cursor, the pattern moves a little the other way, and a soft light fades in at the cursor. Use a spring (stiffness 70, damping ratio 0.86) for smooth start and stop. Return to rest on leave.
8. Accessibility: turn off all motion under `prefers-reduced-motion`.

## Tuning that works (tested against the reference)
- Grain range: do not use full 0-255 noise. Keep values in about 128 +/- 70. Full range at overlay 0.4 is too heavy and speckles saturated colors.
- Blob placement: place each blob at the height of its color band. Cool colors go at the top corners. The brightest accent goes at mid-height on a side edge. The darkest warm color goes below the bottom edge. If you only follow "corners and edges", the warm color spreads too far up.
- Dark floor: keep the bottom 15-20% dark. Give the base gradient several stops (for example 0, 30, 55, 78, 100%), not only two colors.
- Blob size: about 90-100% of the card. Fade each radial-gradient to 0 alpha over several stops. Add a small blur of about 15-20px.
- Pattern mask: about `radial-gradient(ellipse 50% 46%, transparent 30%, #000 100%)`.
- Rays: start the ray origin well below the card, or the lines bunch into a busy point.
- Lenses: use 12 or more, spread around the edges.
- Hover distance: blobs move about 9% of the card. The pattern moves about 3% the other way. Run the spring on a wrapper element, not on the blobs, so it does not fight the CSS drift animation.
- Pattern order in the reference: card 2 rays, card 3 concentric contours, card 4 sound-wave lines, card 5 dot grid, card 6 lenses.
- Working example: `examples/index.html` in this skill folder.

## Palettes from the post (top to bottom)
- purple-pink to orange-gold
- grey-blue to deep brown
- mist-blue to deep sea blue
- mist-blue to ink green
- lavender to midnight purple
- sky-grey to rust red

## Copy-paste prompt (from the post, translated)
Build a 3x2 wall of square cover cards in HTML + CSS + Canvas. Each card has only two lines of white English text in the center. The background is a soft gradient with grain. Use no images.
1. Card radius 20px, inner 0.5px faint black border. Text Inter 400, size 8% of card width, centered.
2. Background: first a top-to-bottom linear gradient, light and cool at the top, dark and warm at the bottom. Then 4 large radial-gradient blobs with faded edges, at the corners and edges. Use only adjacent hues on the color wheel, one set per card: purple-pink to orange-gold, grey-blue to deep brown, mist-blue to deep sea blue, mist-blue to ink green, lavender to midnight purple, sky-grey to rust red.
3. Use canvas to generate 128x128 greyscale random noise, tile it over the card, mix-blend-mode overlay, opacity 0.4. Size by devicePixelRatio so one noise pixel = one physical pixel.
4. On cards 2-6, add a thin white SVG line pattern, in this order: rays, concentric contours, sound-wave lines, dot grid, lenses. Line width 0.8px, opacity about 0.3, radial mask to keep the center clear for text.
5. Blobs drift and scale slightly with CSS animation over 20-28s. On hover, blobs shift toward the cursor, the pattern shifts a little the other way, and a soft glow fades in at the cursor; return to rest on leave. Use a spring (stiffness 70, damping ratio 0.86) for smooth start and stop.
6. Turn off all motion when prefers-reduced-motion is on.
Output one single HTML file with no external libraries.

## Adapt it
- Change the palette to the brand, but keep the analogous-hue rule and the light-cool-top, dark-warm-bottom rule.
- For video or static export, keep the grain and render at the final pixel size so grain stays 1px.

## Check before delivery
- Zoom to 200%: grain must be fine and even, with no banding.
- No hard blob edges. Max 3 hue families per card.
- Text stays readable on the lightest area.
