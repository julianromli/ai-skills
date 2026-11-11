---
name: faiz-editorial-film-edit
description: Edit a talking-head or presenter video into a soft archival editorial film (bright B&W archival B-roll, torn-paper collages, presenter splits, kinetic type with text behind the presenter, light grain and bloom, word-timed captions, transition sound effects), rendered on the GPU with raea. Use for new edits, revisions and variants of such a video, and when the user wants this look on their footage, even if they don't name the skill. Guides first-time users through setup first.
---

# Editorial edit (raea engine)

Turn the user's recording into a soft archival editorial film. The speech, clip order, length and format of the
source stay the same. Talk to the user in their language; write generation prompts in English.

Requirements: macOS on Apple Silicon (raea's renderer and the macOS system fonts Helvetica Neue, Didot, Menlo).

`SKILL_DIR` below means this skill's own folder (the base directory shown when the skill loads). Use that real
path in every command; do not assume `~/.claude/skills/...`.

The skill has three parts:
- **Style**: `references/style-guide.md` and the bundled reference photos, videos and frames.
- **Engine**: `engine/`. Python bakes the look (grade, bloom, torn paper, grain, person masks, captions, SFX),
  raea composites and renders every frame from `timeline.json`, and ffmpeg encodes and checks the delivery file.
- **Templates**: `templates/`. The default look (`style.json`) and an example of each scene type.

## 0. First time? Start here

Before any work, run the read-only check:

```bash
python3 $SKILL_DIR/engine/check_env.py
```

If it does not say READY, or this is the user's first edit with this skill, read
[references/first-time-setup.md](references/first-time-setup.md) and go through it with the user:
- What will be installed, how big it is and where it comes from. Ask before each install.
- Which keys they may want (AssemblyAI). The user saves the key themselves; never in chat.
- **What they must prepare**: the source video, the topic and one key message, correct spellings, brand assets,
  B-roll preferences, optional SFX links, and the target platform.
- How the work goes: transcript → plan → test stills → render → revisions.

Do not start editing until the check says READY, or the user accepts a named limit (for example, "no AssemblyAI
key: use my SRT").

## 0b. Project interview (every new project)

The user does not need to write a prompt. Start every new project with this interview. Ask only what the user's
message has not already answered, in the user's language, with the AskUserQuestion tool (at most 4 questions per
call, 2–4 options each; the user can always type "Other"). Make the questions specific: probe the footage first
(`ffprobe` and a contact sheet) so you can show what you found.

**Round 1: footage, platform, captions** (before anything else)
1. *Footage*: which file? If none was given, offer recent videos you can see (for example in ~/Downloads) or ask for
   the path. Probe it and confirm what you found: "81 s, 2880×2160, 25 fps, one presenter, no cuts. Correct?"
2. *Platform and formats* (multi-select): the source format (always made first, as the master) / 9:16 (Reels,
   TikTok, Shorts) / 4:5 (feed) / 5:4. Extra formats are made from the approved master (section 2b).
3. *Captions*: burned-in captions + SRT (default) / SRT only / none. Save the answer as `"captions": "burn" | "srt" |
   "none"` in timeline.json.

**Then start the project and transcribe** (`init_project.py`, then `transcribe.py`, about 1 minute). Tell the user in one line that you are reading the speech so
the next questions can be about their video. If there is no AssemblyAI key, ask for an SRT or skip the message
options and ask them as free text.

**Round 2: message, spellings, B-roll, assets** (from the transcript)
1. *Message*: 2–3 short summaries taken from the transcript; the user picks one or types their own.
2. *Spellings*: list the names, products and places the transcript heard, and the low-confidence words. "All
   correct" / "Fix some" (typed). Confirm each correction before it goes into `captions_config.json`.
3. *B-roll* (multi-select): public-domain archives (free) / generated shots (Higgsfield: say the price per shot,
   ask for a budget) / only my own images / type only.
4. *Own assets*: none / a folder (typed path). Copy them to `PROJECT/assets/brand/`, use `look: "color"` for logos
   and brand photos, and record them in CREDITS.md.

**Round 3: sound and masks**
1. *Sound effects*: the bundled library (24 clips, licence not verified) / my own SFX links or files / none.
2. *SFX density* (only if SFX): main elements (default) / every element / key moments only.
3. *SFX level* (only if SFX): subtle (~14 dB under the voice) / punchy (~8 dB under).
4. *Text behind the presenter*: masks made locally (free, private) / on fal (cloud, a few cents, needs a fal key).

Each round is one AskUserQuestion call with at most 4 questions. Leave out questions that are already answered
or do not apply (no SFX → no density/level), and do not move a question to a later round.

**Then confirm the brief.** Write it back in 5–8 short lines (footage, message, platform, B-roll, assets, SFX,
masks, corrections) and ask "Start with this brief?" as one question with "Yes, start" / "Change something".
Save it as `PROJECT/BRIEF.md`. Do not start the edit plan before the user says yes.

Later in the project, ask again only for real decisions (a generation budget, a variant to pick, deleting files).

## 1. Study the style (every new project)

1. Read [style-guide.md](references/style-guide.md). It covers composition, grain, bloom, B&W, fonts, motion,
   masks, splits and sound.
2. Read [reference-map.md](references/reference-map.md). Look at the 4 photos and 4 frame sheets. For motion,
   look at the reference MP4s in the given time windows; a still cannot show motion.
3. For revisions, also read [revision-checklist.md](references/revision-checklist.md).
4. [implementation-guide.md](references/implementation-guide.md) explains the layer logic of the original
   browser modules. It is background only: this skill's engine replaces those modules.

The references set the visual grammar, not the content. Do not reuse their people, text, timelines or music.
Pick archival objects and metaphors that fit the new topic.

## 2. Build the edit

Follow [references/pipeline.md](references/pipeline.md) for the commands and the data format. In short:

1. `init_project.py`: make the project from the source, then set `presenter_center_x` and `baked_cuts` by
   looking at frames.
2. `transcribe.py`: get a word-level transcript. Show the user the low-confidence words and the names. Put only
   the corrections they approve in `captions_config.json`. Then run `build_captions.py`.
3. Plan the edit from BRIEF.md: scenes, B-roll, titles, the 3 type roles, where text goes behind the presenter, and which
   splits are needed (splits only appear next to the presenter). Send the user a short plan. Ask only about
   blocking choices: B-roll sources, a generation budget, unclear words.
4. Collect B-roll with clear usage terms and record every source in `CREDITS.md` (public domain, CC with credit,
   or the user's own files). Pinterest alone does not establish rights. Generated shots need the user's budget
   OK and an on-screen AI-illustration label in the viewer's language (for example "ILUSTRASI · AI"); never present them as historical.
5. Write `timeline.json`. Run `make_masks.py` (only for `behind: true` text): ask the user once per project whether masks run **locally** (free, private) or on **fal** (cloud, a few cents, needs a fal key; setup guide in first-time-setup.md Step 2b). Then run `prep.py`.
6. Render **test stills** of the hard moments: light and dark B-roll, a split entering, text behind the presenter,
   a collage, a card on a photo, and the first and last frames. Look at them all, fix them all, then look again.
7. Optional SFX: a ready library of 24 cut clips is bundled in `$SKILL_DIR/sfx/` (whooshes, shutters, clicks, riser, impact; from 3 free-SFX reels, original sources unnamed: tell the user the licence is not verified). Or the user gives reels or files. Download links only with their OK. Then `sfx_cut.py` (check each
   clip's spectrogram for music or voice), `build_sfx.py`. Ask the user for density, level and mapping first.
8. `deliver.py`: raea renders the master, ffmpeg encodes the delivery file, and the script checks frames, size,
   decode, colour tags, audio sync and peak. Run it in the background for long videos.

## 2b. Other formats (9:16, 4:5, 5:4)

Only after the user approves the master edit. For each format the user asked for:

1. `make_format.py PROJECT --aspect 9:16` (or `4:5`, `5:4`) makes `PROJECT/formats/9x16/`, a normal project that shares
   the master's media, transcript and masks. It reframes the presenter with face tracking (YuNet, bundled; smoothed,
   never across the footage's own cuts), turns splits into full-frame cuts in 9:16 and 4:5, moves collage photos to
   the top, re-lays out and fits all text into the platform's safe area, and makes shorter captions.
2. This is a first pass: you are the editor now. Run `prep.py` and render stills at every scene change and every text
   layer. Fix in the format's own `timeline.json`: text over a face or on a busy/dark area (move it, `card: true`,
   or `color`/`shadow`), insert `focus` points that were chosen for a half-width panel, words behind the presenter
   that the bigger head hides, and the `reframe` keys (`[t, cx, cy, zoom]`) where the crop misses the presenter
   (e.g. two people, or a hand gesture cut off). Look again after each round.
3. Deliver each format with the master's audio: `deliver.py PROJECT/formats/9x16 -o ... --audio <master mix>` (or
   no `--audio` to copy the original sound). The timing is identical to the master.

## 3. Check the export itself

Look at contact sheets of the final MP4 around every cut, split, collage and title. Check grain and text motion,
both sides of each transition, mask edges, legibility at the target size, caption bounds, and that there are no
missing media, black or frozen frames, bars or stretching. You cannot watch in real time or listen: say so, and
ask the user to do one full playback with sound. Never report an unperformed check as passed.

## 4. Deliver

- The MP4 (a new version number each time; keep the older versions).
- The editable project as a zip (without `raea/media` and `cache/`, which can be regenerated), the SRT, the SFX
  stem if there is one, and `CREDITS.md`.
- A short note: what changed, what was checked, what was not checked, and any rights the user must confirm.

## Rules

- Keep the source's speech, timing, clip order, length, frame size and fps. Copy the original audio unless the
  user asks for a mix.
- Ask before: installs, downloads from links, spending credits, publishing or sending anything.
- Never put keys or the user's email into commands, files or requests to third parties.
- Do not edit the skill's own files during project work. Change the skill only when the user asks.
