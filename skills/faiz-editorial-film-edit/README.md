# faiz-editorial-film-edit

An agent skill (Claude Code) that turns a talking-head recording into a soft archival editorial film: bright B&W
archival B-roll, torn-paper collages, presenter splits, kinetic type that passes behind the presenter, light grain
and bloom, word-timed captions and transition sound effects. The speech, length, clip order and format of the
source stay the same.

## How it works

- **Python** bakes the look: B&W grade, bloom, torn paper, grain fields, person masks (BiRefNet), captions, SFX mix.
- **raea** (GPU, React/TypeScript) composites and renders every frame from a `timeline.json`.
- **ffmpeg** encodes the delivery MP4 and the scripts check frames, size, decode, colour tags, audio sync and peak.

A 105 s 1440p60 edit renders in about 1–4 minutes on an Apple M5, plus the x264 encode.

## Requirements

- macOS on Apple Silicon. raea renders on Apple Silicon; the type uses the macOS fonts Helvetica Neue, Didot, Menlo.
- ffmpeg, Python 3.10+, raea 0.1.0-canary.3 (pinned), ~1.5 GB for the Python environment and the mask model.
- Optional: an AssemblyAI key (transcripts), a fal.ai key (cloud masks), Higgsfield (generated B-roll).

## Install

Copy this folder to `~/.claude/skills/faiz-editorial-film-edit/` (or wherever your agent reads skills). Then ask the
agent to edit a video. On first use it runs `engine/check_env.py` (read-only) and walks you through
`engine/setup.sh`, which asks before every install.

## Folder

```
SKILL.md                 what the agent reads first
engine/                  check_env, setup, init_project, transcribe, build_captions, make_masks, prep,
                         edit.tsx (raea composition), sfx_cut, build_sfx, make_format, deliver
references/              style guide, reference map, pipeline and data format, first-time setup, revision checklist
templates/               default style.json and example timeline / captions / SFX configs
engine/models/           YuNet face detector (OpenCV zoo, MIT licence) for format reframes
sfx/                     24 cut sound-effect clips + library.json
```

## Third-party material: read before reuse

- `references/videos`, `references/frames` and `references/photos` are **style references only**. The videos are
  public Instagram reels by other creators (links in `references/media-manifest.json`); no reuse licence is granted
  or implied. The skill tells the agent never to put them into an edit.
- `sfx/` clips were cut from three public "SFX breakdown" reels whose creators say they collected free sounds online;
  the original sources and licences are **not verified**. Use them at your own risk, or replace them with your own
  library (`sfx_cut.py` + `sfx_config.json`).
- B-roll, logos, photos and footage you add to a project are your responsibility; the skill records every source in
  the project's `CREDITS.md`.

## Status

raea is a canary release; this skill pins the tested version. Formats: the source format plus 9:16, 4:5 and 5:4
versions made from the approved master (face-tracked reframe, re-laid-out text). Not supported: Linux and Windows. Tested end to end on a 1440p60 talk (105 s) and a 2160p25 talk (81 s).
