# Write a transcript that matches the edited video: drops words that were cut, remaps word times
# onto the edited timeline, and writes .srt subtitles + a readable .txt with timestamped paragraphs.
# usage: python export_transcript.py <transcript.json> <project-config.json> <out_basename> [--segments segments.json]
#        -> <out_basename>.srt, <out_basename>.txt
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from segmap import cfg_ranges, load_segments

args = sys.argv[1:]
seg_path = None
if "--segments" in args:
    i = args.index("--segments"); seg_path = args[i + 1]; del args[i:i + 2]
tr_path, cfg_path, base = args[:3]
tr = json.load(open(tr_path, encoding="utf-8"))
cfg = json.load(open(cfg_path, encoding="utf-8-sig"))
keep = cfg_ranges(cfg, load_segments(seg_path))
offs, acc = [], 0.0
for k0, k1, ts_ in keep:
    offs.append(acc); acc += (k1 - k0) / ts_

def edited(i, x):
    k0, k1, ts_ = keep[i]
    return offs[i] + (min(max(x, k0), k1) - k0) / ts_

# A word is kept when enough of it is audible in the edit. Whisper word times are approximate
# (often starting inside the preceding pause), so a strict midpoint test drops audible words.
words = []
for s in tr["segments"]:
    for w in s["words"]:
        a, b = w["start"], max(w["end"], w["start"] + 0.05)
        hits = [i for i, (k0, k1, _) in enumerate(keep) if k0 < b and k1 > a]
        overlap = sum(min(b, keep[i][1]) - max(a, keep[i][0]) for i in hits)
        if not hits or overlap < min(0.08, 0.3 * (b - a)): continue
        words.append({"t0": edited(hits[0], a), "t1": edited(hits[-1], b), "src0": a, "src1": b,
                      "w": w["word"].strip()})

def join(ws):
    out = ""
    for x in ws:
        t = x["w"]
        # whisper splits "ide-ide", "20-25", "bit.ly", "100%" into separate tokens
        out += t if (not out or re.match(r"^[-.,%:;!?)]", t) or out.endswith(("-", "("))) else " " + t
    return out.strip()

def ts(t, sep=","):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    ms = int(round((s % 1) * 1000))
    if ms == 1000: ms = 999
    return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{ms:03d}"

# subtitle cues: max 5 words / ~42 chars / 5 s, break on pauses >= 0.6 s in the edit
cues, cur = [], []
for w in words:
    if cur and (w["t0"] - cur[-1]["t1"] >= 0.6 or len(cur) >= 5 or len(join(cur + [w])) > 42 or w["t1"] - cur[0]["t0"] > 5.0):
        cues.append(cur); cur = []
    cur.append(w)
if cur: cues.append(cur)
with open(base + ".srt", "w", encoding="utf-8") as f:
    for i, c in enumerate(cues, 1):
        end = max(c[-1]["t1"], c[0]["t0"] + 0.8)
        if i < len(cues): end = min(end, cues[i][0]["t0"] - 0.01)
        f.write(f"{i}\n{ts(c[0]['t0'])} --> {ts(end)}\n{join(c)}\n\n")

# readable text: paragraphs break where the speaker paused >= 2.5 s in the original recording
# (pauses are gone from the edit, so they can't be measured there), capped at ~120 words
paras, cur = [], []
for w in words:
    if cur and (w["src0"] - cur[-1]["src1"] >= 2.5 or len(cur) >= 120):
        paras.append(cur); cur = []
    cur.append(w)
if cur: paras.append(cur)
with open(base + ".txt", "w", encoding="utf-8") as f:
    for p in paras:
        f.write(f"[{ts(p[0]['t0'], '.')[:8]}] {join(p)}\n\n")

print(f"{len(words)} words, {len(cues)} subtitle cues, {len(paras)} paragraphs -> {base}.srt / .txt")
