# The editorial-film-edit visual system

This document defines a transferable editing style. The content, topic, presenter, duration, format and assets belong to the current project. The bundled external photos and videos are sources of visual techniques; they are not ready-made inserts for every story. All work is based on the current project's source and the external references bundled locally.

## 1. Content and pacing

- By default, preserve the duration, clip order, speech, meaningful pauses and aspect ratio of the supplied pre-cut source. Shortening, rearranging lines and changing the format require a corresponding user request. Duration and aspect ratio are not fixed across all projects.
- Determine resolution and frame rate from the current source and publication format, without unnecessary upscaling. Cropping must not stretch people, objects or letters.
- First build a timeline around meaning: thought → visual argument or association → readable emphasis → next thought. B-roll supports a specific line rather than filling random gaps.
- Captions and emphasis words match the actual speech, names and numbers. Do not invent quotations, facts, product capabilities, interfaces or results. Do not silently correct the content of the presentation.
- For long videos, reduce the density of effects and inserts: preserve calm passages, reading time and time to examine details. The pace of a short reel does not automatically carry over to a long episode.
- If the presenter, speech or both are absent, adapt the style to the existing action, music and units of meaning. Do not add speech subtitles and presenter splits without a reason.
- Do not impose the same number of inserts, a fixed proportion of face screen time or a mandatory zoom on every project. An immediately readable opening hook is needed where the task calls for it; a soft entrance must not obscure its meaning.

## 2. External references: what to carry over

[reference-map.md](reference-map.md) contains the roles of the four videos and four photographs, local paths and animation time windows. Study them before assembly. Exact font families, grain algorithms and animation frequency cannot be reliably determined from appearance alone. The numerical settings below are working starting values for a new edit, not measured parameters used by the reference creators. Silent video copies are not audio-editing references.

## 3. Archival editorial aesthetic

The overall character is a contemporary, authored editorial edit with tactile archival materials: photographic fragments, physically convincing paper collages, soft light, cream and charcoal tones. Dusty ochre and muted oxide red are used as occasional accents. Avoid glossy CGI, neon, plastic surfaces, generic digital glitches and a collection of random stock footage.

Adapt the visual grammar to the current video's topic. Analogue instruments, film, CRTs, cables, old laboratories and computing equipment suit technology topics. For food, fashion, history, creativity or another topic, choose appropriate objects, photographs and archives. Old computers are not a required element in every video. Show a modern interface or product that is essential to the explanation accurately and legibly; stylization must not distort the demonstration.

All inserts belong to one visual system but differ in their main subject, scale and composition. A new crop, mirror flip or recolouring of one image does not replace selecting a complete new scene. Recurring paper, palette, lines and other connecting motifs are acceptable. Alternate suitable videos, details, photographs and collages, avoiding a monotonous slideshow.

The presenter stays in the original setting with natural skin unless the user has requested otherwise. Do not automatically “age” the face along with the inserts.

### Composition and collage

- Each frame has one main focal point: a face, object, word or number. Make secondary elements serve it.
- Leave space for text and safe margins, accounting for the actual aspect ratio and the publication platform's interface.
- In a collage, use a limited number of meaningful elements, differences in scale, convincing paper edges and delicate shadows. Materials should feel like layers, not randomly scattered PNGs.
- Technical labels, fine registration lines and red markings are appropriate only when connected to the topic. Do not generate pseudo-documentary details that could pass an illustration off as real evidence.
- Animate a photograph with a small movement in framing or layers. Preserve perspective; avoid excessive pseudo-3D and do not stretch body parts.
- The main transitions are cuts motivated by meaning. Adjacent images can be connected by a shared colour, composition or continuing phrase. A transition must not distract from the thought.

## 4. Grain and image treatment

### Lively fine grain

Grain is light, fine and predominantly monochrome. Its pattern updates on every master frame; a single stationary or moving noise image is unsuitable. For reproducible rendering, use a seed based on the integer output-frame index. Intensity depends on image brightness and decreases at tonal extremes. Avoid large blotches, chromatic dirt and flat additive overlays. If using slight film movement, coordinate it with the picture's coordinate system.

Animation alone does not correct the wrong grain size or tonal behaviour. First assess the texture already baked into the source: additional noise may amplify it excessively. Paper texture may remain stationary relative to the paper; it is a separate layer, not a substitute for temporal grain.

Apply treatment by scene and image region. In a split, the treatment belongs to the insert, regardless of which side it occupies. The treatment mask moves with the panel. By default, keep the presenter's skin, important interfaces and informational graphics clean. Dust, scratches, burns and noticeable flicker are off unless justified by a separate request.

Calibrate grain size and strength on actual light and dark frames, at full resolution and normal speed, then on the final encoded file. There is no universal numerical recipe for all renderers. Do not strengthen grain solely to make it survive every possible social media transcode.

### Light bloom and optics

Add a soft glow to bright areas of B-roll before the final grain: a gradual highlight threshold, soft blur at several scales, restrained intensity. Preserve the shape of lamps and other bright objects, highlight detail and thin lettering. Avoid a grey veil, duplicate light rings and murky fog across the whole frame.

Bloom, grain, aging, exposure and halation must have independent controls. Do not remove a coloured halo around letters by globally disabling all film treatment: reduce the relevant effect locally or protect the text. Pay particular attention to warm sources, white captions and neutral B&W. B&W must not contain accidental orange or red outlines.

Believable source materials, motion and optics matter more than a strong filter. Slight softness and smooth highlights are appropriate; film weave, vignette, chromatic effects and flicker are optional. Check both sides of every transition: the outgoing shot's treatment must remain correct until it disappears completely.

### Bright, soft B&W

Use a separate neutral monochrome treatment: open up midtones, preserve controlled blacks and smooth highlights. Lifted blacks alone do not make a dark scene bright. Preserve detail in faces, paper, metal and shadows; the result should be soft and bright without being flat.

Avoid coloured split toning in neutral B&W, multiple stacked darkening curves, and a strong dark overlay combined with a vignette. Adjust exposure and contrast separately for each source. Do not darken every insert with one strong setting just to accommodate white text—first solve its placement and hierarchy.

## 5. Typography

Authored typography is limited to three families, with shared tokens for titles, subtitles, collages, masked words and technical labels:

| Role | Preferred family | Purpose |
|---|---|---|
| Sans serif | Helvetica Neue | Main information, subtitles, strong words; bold remains a style within the same family. |
| Editorial serif | Didot, including italics | Selected words, expressive numerals and contrasting accents. |
| Monospace | Menlo | Compact sources, labels and technical details. |

If a family is unavailable, choose one available equivalent for that role, record the substitution and recheck sizes, line breaks and weights. A specified fallback does not prove which font actually rendered. Do not add a fourth family for a bold word, code or a decorative handwritten insert. Logos and lettering already present in a source photograph or interface do not count as additional authored typography.

Hierarchy: one key word or numeral large, a short explanation quieter, the source in small monospaced text. Sizes depend on the frame, word length and viewing conditions. Do not stretch letters along one axis or crop meaningful text at the edges. Full subtitles and emphasis words must not interfere with one another or duplicate each other in the same place. Keep thin serif type readable on a small screen. Create new lettering as separate layers; do not bake it into generated imagery.

### Soft, active animation

Each text element has a meaningful entrance, a readable hold and an exit. Use restrained rise or drift, changes in spacing and delicate blur with smooth acceleration and deceleration. Start tuning a short accent's entrance around 0.2–0.45 s and its exit around 0.15–0.25 s; reading time is determined by actual speech and phrase complexity. These are starting settings, not measurements of the references. Do not turn every word into a jump, jitter, spring or abrupt zoom.

A phrase may continue across a cut while the same thought continues. Preserve the element's identity, position and continuous animation clock as the background changes. First check the meaning and actual words of the presentation, then collisions with new text, the face and frame geometry. Non-overlapping rectangles alone do not justify keeping a completed line on screen. When the thought changes, the old text leaves; a meaningful in-place word replacement can remain a clean cut.

### Selective stepped motion

Some text transformations may have a light stop-motion / posterize-time character at approximately 10–15 updates per second. For a 25 fps master, a working example is to update the transformation every two output frames, or 12.5 fps. Quantize by integer frame index for reproducibility. Adjust the rate to the actual master if it differs.

This is a selective artistic device for entrances or individual details, not a global reduction in the film's frame rate. Video, sound, grain and tracked masks retain their full required temporal resolution. Combine stepped details with a soft overall trajectory; do not make all text constantly jerky.

## 6. Text behind a person or object

At several meaningful moments, create depth with the layer order: background → text → real foreground. The mask belongs to the exact source, time within the clip, and the same crop, scale, position and flip transformation. When replacing the source, the old mask cannot simply be reused.

Check hair, glasses, fingers, shoulder edges and temporal stability wherever they intersect letters. An arbitrary rectangle is not object segmentation. After replacement or reframing, check several consecutive frames, not just one successful still frame.

Preserve recognizable letterforms, contrast and reading time. If occlusion is excessive, move, shrink or retime the text; do not change the factual content of the speech for an effect. Do not show hidden letters translucently through a face or body. The numerical proportion of visible area is a supporting metric; it does not prove a word's legibility. If the mask is unstable, use a clean, readable composition without occlusion at that point.

## 7. Presenter split

The new side-entry motion applies only when a presenter and an insert are visible simultaneously. The panel enters calmly from the left or right, shifting and reframing the previous picture. The starting duration is 0.3–0.45 s with soft acceleration and deceleration. Choose the direction based on the composition and face position.

Preserve facial proportions, room at the edges, crop continuity and a stable final state. Text, clipping, grain and bloom belong to the panel and move in coordination with it. Avoid black gaps, stretching, flashes, spring motion, abrupt zooms or a jump on the animation's last frame.

Full-screen B-roll and splits made only of inserts do not automatically receive this entry motion. Preserve existing exceptions explicitly approved by the user. This technique is not required in a project without a presenter.

## 8. Selecting and generating assets

Use accessible materials with clear provenance and usage terms. Pinterest serves as a reference and a way to find the creator; a pin link does not confirm publication permission. Store the creator, original source, license and required attribution text alongside the asset; the on-screen credit applies to the scenes that use the corresponding source.

Generation is optional. If a needed shot is unavailable and user-approved Higgsfield with Seedance 2.5 is accessible, make a small number of precise generations. Do not silently change the model or incur costs without the corresponding authorization or an agreed limit. Having a style reference does not imply access to the service; without a generator, continue with suitable accessible materials.

Write the generation prompt in detail in English, directly in the current project: the specific main subject and its relationship to the topic, composition, physical materials, period or archival optics where needed, soft light, colour palette, camera character, one clear movement, appropriate frame proportions and free space for future captions. Do not generate readable lettering in place of separate text layers. Maintain a consistent style between shots and check the actual duration, frame rate and geometry of the result after downloading.

Photorealistic archival generation is treated as illustration, not evidence of a real historical event. Do not present a fictional product screen, a person at an event or a test result as documentary fact. Record the prompts and results actually used, without keys, private correspondence or unnecessary personal data. Bundled references are study material, not automatic permission to include their pixels in the final video.

## 9. Assembly, sound and quality control

Assemble from clean, independent layers: source video, inserts, text, masks, treatment and sound. Preserve the previous version when making revisions. A finished, flattened MP4 is suitable for comparison and an unchanged audio track, but does not provide clean layers for replacing grain or captions. A new project receives its own timeline, word timing, masks and format settings; IDs, dimensions, timecodes, caches and validation reports from other projects do not carry over.

Account for internal edit points already baked into the source. An insert or presenter segment must not show the end of an adjacent take for a few frames. Distinguish programme time from source time. After shifting the start of a scene, recalculate the text's relative timing so that its absolute alignment with speech is preserved. Check the duration of available B-roll, accounting for the chosen playback speed.

Preserve the original speech and do not add a new voiceover without a request. If music has not been supplied or agreed upon, do not delay the edit for it. If only the picture has changed and the timeline is identical, use the approved soundtrack without additional changes. For a new mix, check speech intelligibility, balance and synchronization; record actual listening and level measurements separately.

### Tests before the full render

Test a light and a dark insert, B&W, an interface, a title across a cut, a split and each mask type on real material. Assess the full frame, important details at actual size and viewing on a small screen. Synthetic test cards are useful for diagnosis but do not replace these tests.

To diagnose grain, compare identical frames and source times with exposure, bloom and colour held constant, changing only the grain. Ensure that “off” actually disables all its sources in the region being checked. Use consecutive frames and normal playback: source and text motion distort simple inter-frame difference statistics. An additional downscaled test encode is acceptable, but does not promise the outcome of the social network's current transcoding.

### Acceptance of the actual delivery file

1. Check the required resolution, aspect ratio, pixel aspect ratio, frame rate, frame count, duration and correct colour reproduction. H.264/AAC in MP4 is suitable for ordinary delivery unless the request requires another format. Do not copy settings from a previous project.
2. Fully decode the final file and check for corruption, missing media, accidental black frames and unintentional freezes. A still photograph held intentionally is not itself an error.
3. Watch the entire exported MP4 at normal speed and listen to it. Check synchronization, grain, bloom, exposure, text motion, mask edges, joins and legibility. Contact sheets and metrics supplement viewing; they do not replace it.
4. Separately check questionable transitions and all occlusions on consecutive frames, including the outgoing side of the transition. Ensure that no old phrase remains over a new thought.
5. Fix substantive defects and recheck the affected areas. The number of iterations is not proof of quality. Accept the result based on the actual fulfilment of the criteria.
6. In the report, distinguish viewing, listening and technical checks. State actions that were not actually completed and any limitations. Do not present an old report or a successful render launch as verification of the new final file.

Delivery includes the final MP4, a version without added music if music was used, an editable project, necessary assets or a clear list of external dependencies, sources, and a brief report of changes and checks. Paths must be portable, and the package must contain no secrets or unrelated data. Store universal style settings separately from the assets, exceptions and timecodes of a specific project.
