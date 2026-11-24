# Screen-recorder project formats (verified on this Mac, Nov 2026)

All zoom anchors are 0..1 from the **top-left** of the recorded screen. Verified for all three apps.

## Cap (`*.cap`, in `~/Library/Application Support/so.cap.desktop/recordings/`)
- Use cap-course-edit's pipeline and `references/cap-project-notes.md` there. CLI:
  `/Applications/Cap.app/Contents/MacOS/cap-cli` (validate, config get, export-preview, export).
- One `content/segments/segment-N/` per pause/resume. Mic: `audio-input.ogg|m4a` per segment, so
  `prep_audio.py` joins them. A word can be split across two recording segments; that is a pause in
  the recording, not a bad cut.
- Manual zoom: `"mode": {"manual": {"x": 0.7, "y": 0.2}}` (`auto` and `manual` are the only variants).
- Camera lag: `clips[i].offsets.camera` (+ = camera earlier), set `offsetsAutoCalculated: false`.
  Ask the user for the value and let them check the export. The automatic lip-motion vs voice
  correlation gave no clear result (hand and mic move in the face area), so do not trust it.
- `cap-cli export-preview <proj> --frame-time T --settings-json '{"fps":30,"resolution_base":{"x":1920,"y":1080},"compression_bpp":0.3}' --json`
  returns one rendered frame (`jpeg_base64`). Use it on an APFS clone (`cp -cR`) to check a zoom
  before you write the real project.
- Export: `cap-cli export <proj> -o out.mp4 --resolution 2560x1440 --fps 60 --quality maximum --json`.
- Volume: `audio.micVolumeDb` exists, but the mic peaks near -4.5 dB at -32 LUFS, so +17 dB clips.
  Raise loudness at merge time instead.

## Shotbase (`*.shotbase`, in `~/Shotbase Captures/`)
- Use cap-course-edit's `shotbase.py` (prep, apply, check, write) and `references/shotbase-notes.md`.
- Manual zoom (`motionEffectSegments`): `zoomMode: "manual"`, `zoom: 150`, `zoomAnchorX/Y`.
  `scripts/add_zooms.py` writes these into the Cap-like `NEW.json` before `shotbase.py apply`.
- Mic is a separate `microphone.m4a`: raise it in place with `scripts/loudmic.py`
  (keep `microphone.original.m4a`). The 0.044 s AAC start offset is encoder priming: never add a delay for it.
- `motionEffectsDisabled: true` turns off all zooms; the user may set it on purpose.
- Some projects have no `title` key; read it with `.get()`.

## CleanShot X (`*.cleanshotvideo`, usually in `~/Movies/`)
- `document.json`: `clips[] {startTime (source s), duration, id}` play in order; `zooms[]
  {startTimestamp, endTimestamp (edited-timeline s), zoomValue, position [x,y], mode, id}`.
  `mode 0` = follow cursor (CleanShot auto zooms), `mode 1` = manual at `position`.
- `scripts/cleanshot.py to_cap | apply` converts to and from a Cap-like config.
- `files/video.mov` holds the screen **and** the mic: stream 1 = mic, stream 2 = system audio
  (check which one has signal with `ebur128`). Extract the mic yourself; there is no prep script.
- Projects are huge: video.mov is recorded at 250-500 Mbps (about 17 GB per project). Exports are
  H.264 at 67-107 Mbps. Check free disk before every export or merge.
- No CLI and no validation. The first edit of a new CleanShot version goes to a clone that the user
  opens and checks (length, two cut points, first zoom).
- The app keeps its document in memory: tell the user to close the project window without saving
  and open it again after you write.
