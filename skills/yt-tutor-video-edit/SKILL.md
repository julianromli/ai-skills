---
name: yt-tutor-video-edit
description: >-
  Faiz's YouTube tutorial workflow, from a raw screen recording to an upload-ready video - edit the
  project in Shotbase, Cap or CleanShot X (cut "cut" markers, retakes, mutters, tighten pauses, zooms
  on prompts), then subtitles (SRT, max 5 words), YouTube chapters, -14 LUFS audio, merging parts and
  HEVC compression. Use whenever Faiz gives a .shotbase, .cap or .cleanshotvideo project (one or more
  parts) for a new video, asks to re-check a cut, to make or redo SRT/chapters, to merge exported
  parts, to make audio louder, or to compress a video, even if he only names the topic
  ("next konten: ...").
---

# YouTube tutorial video edit

Faiz records AI-tool tutorials (Indonesian, many English tool names) with Shotbase, Cap or CleanShot X,
sometimes in 2+ parts. He exports in the app himself, unless he asks you to. This skill fixes the
process; cap-course-edit supplies the engine (transcription, timeline build, Shotbase/Cap I/O).

Talk to him in Indonesian, in ASD-STE100 style: short sentences, one fact each.

## 0. Paths

```bash
CCE="$HOME/.claude/skills/cap-course-edit/scripts"; S="$HOME/.claude/skills/yt-tutor-video-edit/scripts"
ROOT="$HOME/Library/Application Support/cap-course-edit"; PY="$ROOT/venv/bin/python"; W="$ROOT/work/<project name>"
Y="/Users/faizintifada/content-creator/youtube/<video title>"     # all deliverables go here
```
Read `references/app-formats.md` for the app you meet. For Cap and Shotbase also follow
cap-course-edit's SKILL.md steps for prep, build and write.

## 1. Fixed defaults: never ask about these

| Topic | Default | Why |
|---|---|---|
| Pauses | tighten, not cut all silence: `build_timeline.py --transcript … --pad-head 0.35 --pad-tail 0.55 --style keep --zoom 0 --min-zoom 0.3` (no `--silence`) | full silence cuts make screen demos jump |
| Transcription | AssemblyAI, `--language id --model universal-2` | best Indonesian result so far |
| Cuts | always cut: "cut"/"cut cut" markers + the take before them, retakes, stutters, "test test", dictation while typing, lone mutters (≤ -6 dB, "oke", "gitu", "nah…"), noises from `review.sounds.json` | he says "cut" to mark retakes |
| Output folder | `$Y` = `content-creator/youtube/<title>/`; title = the topic he names, else the app's project title | he uploads from there |
| SRT | max 5 words per cue, names fixed (step 6) | long cues pile up on YouTube |
| Chapters | about 1 per 1.5 min, short titles that name the tool or step | he asked for fewer chapters |
| Audio | -14 LUFS, true peak ≤ -1.5 dB | his earlier videos were ~-28 LUFS |
| Compression | HEVC `hevc_videotoolbox`, 8 Mbps at ≤1440p, 12 Mbps above | 8-9× smaller, SSIM ≥ 0.99 |
| Backup | clone or copy the project before the first write; keep every replaced file | he reviews and may revert |

Ask only about: zoom policy for this video (default proposal: manual 1.5× zooms only where a prompt or
setup step is on screen, app auto-zooms removed), a camera offset if he reports lag, and who exports.

## 2. Confirm-first actions

Always get a clear yes before: writing into the project the first time for a new app format,
changing audio volume, deleting any file (also your own broken outputs: say which and why), and
merging when free disk < 1.2 × the sum of the parts. Before every write check the app:
Shotbase `pgrep -il shotbase` must be empty; Cap and CleanShot: ask him to close the editor window.
Before a later write, diff the live file against your last written copy; merge his edits, never overwrite them.

## 3. Edit (per part)

1. Back up (see table), prep audio (Shotbase/Cap: cap-course-edit; CleanShot: extract mic stream).
2. Transcribe all parts in parallel in the background, then `analyze.py`.
3. Read every line of every `review.tsv`. Write `cuts.json` with a reason per cut. Place cuts on word
   times, never on segment bounds.
4. **ASR merge trap.** AssemblyAI sometimes merges a retake into one long "fake word" (≥ 2.4 s,
   listed by analyze.py). When a fake word sits near a retake, a "cut", or loud bursts in the level
   bars, cut the 10-15 s around it out of `mic.flac` and transcribe that piece alone before you decide.
   (The MiniMax outro retake was hidden this way.)
5. **Part joins.** The end of part N and the start of part N+1 often repeat (he searches, then starts
   part N+1 clean). Cut the searching at the end of part N.
6. Build the timeline. Check it with `$S/check_edges.py "$W" <config>` and look at every flag.
   A clip that ends on a sound gets 0.2-0.3 s shorter; a recording-segment boundary is not a flaw.

## 4. Zooms (when he wants them)

Find prompt moments: transcript phrases (prompt/prom, ketik, slash commands, "install this", reading a
prompt aloud) plus a contact sheet of frames at those times (`ffmpeg … tile=4x5`). Read the anchor from
the frame: centre of the prompt bubble or the command block, 0..1 from top-left.
- Zoom only while the prompt is readable on screen; start at the first word about it.
- Never zoom on AI output, dashboards or pricing pages unless they are a setup step he follows.
- 1.5×, manual, one zoom per prompt. Split anything > 50 s.
Write: Shotbase `$S/add_zooms.py NEW.json zooms.json`; Cap `$S/cap_zooms_camera.py`;
CleanShot `zooms[]` with `mode 1` (see app-formats.md). Verify one zoom (Cap: export-preview on a clone;
others: ask him to check the first zoom).

## 5. Write, then report

Use the app's CLI for every step it supports (Cap: `cap-cli project config get|set`, `validate`,
`export-preview`, `export`); write files directly only for apps without a CLI (Shotbase via
`shotbase.py write`, CleanShot `document.json`). Faiz asked for this.

Report per part: before → after length, a table of cuts (recording time, edited time, what, why),
the boldest cut to check first, zooms with times, backups and how to restore.

## 6. Subtitles and chapters

```bash
PYTHONPATH="$CCE" "$PY" "$S/export_transcript_5w.py" "$W/transcript.json" <edited config> "$W/raw" --segments "$W/segments.json"
python3 -I "$S/build_srt.py" "$W/raw.srt" "$W/raw.txt" "$Y/<name>" [rules.json]
```
- `fix_names.py` holds the global name list (Claude Code, Grok Bot, Codex, …). Put names that only
  fit this video in a `rules.json` (`[[regex, replacement], …]`, see `references/rules-example.json`).
  Before you write rules, grep the txt for every product/tool name and for "cloud": in his videos
  "cloud" almost always means Claude, but check each case.
- Never guess a word you cannot confirm: list it in the report instead.
- Chapters: find each topic start in the transcript, map it with `where.py`, check the first words of
  the SRT at that time.
- Multi-part: one SRT per part plus `<title> (merged).srt`. The merged offset of part N+1 is the
  **exported** video duration of parts 1..N (`ffprobe` stream duration), not the config length.
  Redo the merged SRT after export.

## 7. Audio, merge, compress

- Shotbase: raise the mic in the project with `$S/loudmic.py` (sync check must print 0 ms).
- Cap and CleanShot: raise loudness while merging (mic is per segment or inside video.mov).
- `$S/merge_parts.py <out> <part1> <part2> …` - copy video when parts share codec/size/fps, else
  `--crop WxH` (a few pixels differ between exports) and/or `--hevc 8M`. It prints part durations,
  loudness and decode errors.
- Compress a big file separately: HEVC as in the table, keep audio (`-c:a copy`), then check
  duration, full decode and SSIM at 3 points. Keep the original until he deletes it.
- Disk: CleanShot projects are ~17 GB, exports 4-9 GB. On ENOSPC stop, delete only your own broken
  output (moov atom missing), and ask him to free space.
- Open the final file with `open` when he asks to see it.
