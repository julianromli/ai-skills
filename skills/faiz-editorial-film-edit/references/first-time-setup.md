# First-time setup

Do this section with the user the first time they use the skill on a machine (when `check_env.py` does not say
READY), and when they ask "what do I need?". Speak in the user's language. Ask before each install or download.

## Step 1. Run the check (read-only, installs nothing)

```bash
python3 $SKILL_DIR/engine/check_env.py
```

Show the user the MISSING lines and the size and source of each fix. Then run the setup, which asks before each
item:

```bash
sh $SKILL_DIR/engine/setup.sh
```

You cannot answer its questions yourself. Run it with `--yes` only after the user agrees to the full list below.

| Item | Size | Why | From |
|---|---|---|---|
| ffmpeg (with libx264) | ~100 MB | decode the footage, encode the delivery file, cut sound | Homebrew |
| Python venv `~/.editorial-raea/venv` (numpy, opencv, pillow, rembg, onnxruntime) | ~400 MB | grade media, masks, captions, SFX | PyPI |
| raea 0.1.0-canary.3 (`~/.raea`, `~/.local/bin/raea`) | ~150 MB | GPU compositing and render | raea.io (checksum verified); it also adds its own `raea` and `raea-bevy` skills to `~/.claude/skills` |
| BiRefNet-portrait model (`~/.editorial-raea/models`) | ~1 GB | person masks for text behind the presenter | rembg's model host, on first use |
| Fonts: Helvetica Neue, Didot, Menlo | — | the three type roles | macOS system fonts |

raea is a canary release that changes daily. The skill pins the tested version. Update it only after a still
test (see "Updating raea" below).

## Step 2. Accounts and keys (optional)

- **AssemblyAI** (word-level transcript): the user makes a key at assemblyai.com and saves it themselves:
  `printf %s KEY > ~/.editorial-raea/assemblyai.key && chmod 600 ~/.editorial-raea/assemblyai.key`.
  Never ask the user to paste the key into chat, and never print or store it in a project. Without a key, use a
  transcript the user already has (convert it to `transcript/words.json`: `{"words": [{"w", "t0", "t1"}]}`).
- **Higgsfield / Seedance** (generated illustration shots): optional. Only when it is connected in Claude and the
  user agrees to a credit budget. Show the price per shot before any generation.

## Step 2b. Person masks: local or fal (ask the user)

Text behind the presenter needs a person mask for each frame it covers (usually 100-300 frames per edit).
Ask the user which engine they want, and explain the choice:

| | **local** (default) | **fal** (cloud) |
|---|---|---|
| Where | this Mac's CPU (rembg, BiRefNet-portrait) | fal.ai, `fal-ai/birefnet/v2`, model "Portrait", 2048 px |
| Cost | free | $0.000575 per compute second (fal's price on 2026-11-09): a few cents per edit |
| Speed | ~15-20 s per modelled frame (measured on an M5; ~30 min for 8 s of behind-text), Mac stays busy | parallel requests, Mac stays free |
| Privacy | frames stay on the Mac | presenter crops (JPEG) are uploaded to fal |
| Setup | ~1 GB model (setup.sh) | a fal account, a payment method and an API key |

**fal setup guide (the user does these steps):**
1. Make an account at https://fal.ai and add a payment method or credits under Billing.
2. Open https://fal.ai/dashboard/keys, make a key (scope: API), and copy it.
3. Save it on the Mac, never in chat:
   `printf %s YOUR_FAL_KEY > ~/.editorial-raea/fal.key && chmod 600 ~/.editorial-raea/fal.key`
4. Test on one project first: `make_masks.py PROJECT --engine fal`. Then check the real cost in fal's billing page.
Frames that fail on fal are modelled locally when the local model is installed. The price can change: read it on
https://fal.ai/models/fal-ai/birefnet/v2 (logged in) before a big job.

## Step 3. What the user prepares for each project

Ask for these before you start. Tell the user why each is needed.

1. **The source video**, the final talk or recording. Its length, clip order, speech and format are kept.
   Ask where the file is (a path on this Mac).
2. **The topic and audience** in one or two sentences, and the **one message** viewers must remember.
3. **Correct spellings** of names, products, places and event titles (the transcript mishears them).
4. **Brand assets**, if any: logo files, official photos, a banner, the event URL. The user's own files are best.
   The user is responsible for the rights to the files they give.
5. **B-roll preferences**: public-domain archives only, generated shots, the user's photos, or a mix.
6. **Sound effects** (optional): links or files. Social-media links are downloaded only with the user's OK, and
   the user is responsible for the rights.
7. **Deadlines and outputs**: the target platform(s), the delivery format (default: same as the source), and
   whether captions must be burned in (default: yes) and/or supplied as SRT.

## Step 4. Tell the user how the work goes

Give the user this short picture before the first edit (in their language):

1. Transcript → the user approves the corrections.
2. A short plan of the edit (scenes, B-roll, titles) → the user approves.
3. Test stills of the hard moments → the user reviews.
4. Full render (raea renders about 30 frames per second at 1440p, so a 2-minute video takes about 4 minutes,
   plus the encode).
5. The user watches the export with sound and sends revision notes. Revisions are fast: change the data, render
   again.

## Updating raea

```bash
RAEA_VERSION=<new> sh <saved installer>   # see setup.sh
```

Then render the stills of an existing project (`deliver.py PROJECT --stills ...`) and compare them with the last
approved export before you use the new version for delivery. Known canary limits that edit.tsx works around:
CSS `url()` needs an absolute `file://` path; CSS `background-repeat` does not tile; an element with a CSS
`filter` draws over its later siblings.
