"""Recheck a rough cut: flag clip edges that cut through sound or through a word.
usage: check_edges.py <workdir> <cap-like config.json>
workdir must hold segments.json, transcript.json and mic.flac (global times).
A flag is a lead, not a verdict: a word that the ASR stretched to ~3 s, or a recording-segment
boundary (pause/resume), shows up here too. Look at the printed words and levels before changing anything."""
import json, subprocess, sys
import numpy as np

W, C = sys.argv[1:]
segs = json.load(open(W + "/segments.json")); st = {s["index"]: s["start"] for s in segs}
cfg = json.load(open(C))
cl = [(st[c.get("recordingSegment", 0)] + c["start"], st[c.get("recordingSegment", 0)] + c["end"]) for c in cfg["timeline"]["segments"]]
ws = [w for s in json.load(open(W + "/transcript.json"))["segments"] for w in s.get("words", [])]
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", W + "/mic.flac", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)


def db(t):
    s = x[int(max(t, 0) * 16000):int((t + 0.05) * 16000)]
    return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9) if len(s) else -99


def ctx(t0, t1): return " ".join(w["word"].strip() for w in ws if t0 <= w["start"] < t1)


acc, n = 0.0, 0
for i, (a, b) in enumerate(cl):
    tag = []
    if max(db(a), db(a + 0.05)) > -38: tag.append("START on sound")
    if max(db(b - 0.1), db(b - 0.05)) > -38: tag.append("END on sound")
    if any(w["start"] < a - 0.03 < w["end"] - 0.05 for w in ws): tag.append("START inside a word")
    if any(w["start"] + 0.05 < b < w["end"] - 0.03 for w in ws): tag.append("END inside a word")
    if tag:
        n += 1
        print(f"#{i} edited {int(acc // 60):02d}:{acc % 60:04.1f} source {a:.2f}-{b:.2f} {tag}\n"
              f"   start: [{ctx(a - 3, a)}] | [{ctx(a, a + 3)}]\n   end:   [{ctx(b - 3, b)}] | [{ctx(b, b + 3)}]")
    acc += b - a
print(f"{len(cl)} clips, {n} flagged")
