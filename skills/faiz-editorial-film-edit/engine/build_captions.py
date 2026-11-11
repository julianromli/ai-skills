"""Word-timed caption chunks: transcript/words.json + captions_config.json -> captions.json + captions.srt.

    python build_captions.py PROJECT

captions_config.json (all keys optional):
  "fix":      {"heard,": ["right,"], "RAI,": ["era", "AI,"]}   one token -> one or more (time split evenly)
  "merge":    [["The", "Fest", "DevFest"]]                      two heard tokens -> one word
  "accent":   ["relasi,", "komunitas"]                          words drawn in the italic accent face
  "suppress": [[50.0, 54.2]]                                    seconds where a big title already says the words
  "max_words": 7, "max_chars": 38
Word times stay the transcript's, so captions stay locked to the speech. Only approved corrections go in "fix".
"""
import json, sys
from pathlib import Path

P = Path(sys.argv[1]).resolve()
words = json.load(open(P / "transcript/words.json"))["words"]
cfgp = P / "captions_config.json"
C = json.load(open(cfgp)) if cfgp.exists() else {}
FIX, MERGE = C.get("fix", {}), C.get("merge", [])
ACCENT, SUPPRESS = set(C.get("accent", [])), C.get("suppress", [])
MAXW, MAXC = C.get("max_words", 7), C.get("max_chars", 38)

out, i = [], 0
while i < len(words):
    w = words[i]
    m = next((m for m in MERGE if i + 1 < len(words) and w["w"] == m[0] and words[i + 1]["w"] == m[1]), None)
    if m:
        out.append({"w": m[2], "t0": w["t0"], "t1": words[i + 1]["t1"]}); i += 2; continue
    rep = FIX.get(w["w"], [w["w"]])
    for k, r in enumerate(rep):
        a = w["t0"] + (w["t1"] - w["t0"]) * k / len(rep)
        b = w["t0"] + (w["t1"] - w["t0"]) * (k + 1) / len(rep)
        out.append({"w": r, "t0": round(a, 3), "t1": round(b, 3)})
    i += 1


def is_sup(w):
    mid = (w["t0"] + w["t1"]) / 2
    return any(a <= mid <= b for a, b in SUPPRESS)


chunks, cur = [], []
for w in out:
    if cur:
        gap = w["t0"] - cur[-1]["t1"]
        text = " ".join(x["w"] for x in cur)
        if gap > 0.55 or len(cur) >= MAXW or len(text) + len(w["w"]) > MAXC or is_sup(w) != is_sup(cur[-1]) or \
           cur[-1]["w"][-1] in ".?!" or (cur[-1]["w"][-1] == "," and len(cur) >= 3):
            chunks.append(cur); cur = []
    cur.append(w)
if cur: chunks.append(cur)
merged = []        # one-word orphans join the previous chunk when it stays short
for c in chunks:
    if merged and len(c) == 1 and is_sup(c[0]) == is_sup(merged[-1][-1]) and \
       len(" ".join(x["w"] for x in merged[-1] + c)) <= MAXC + 10 and c[0]["t0"] - merged[-1][-1]["t1"] < 0.6:
        merged[-1].extend(c)
    else:
        merged.append(c)

data = []
for j, c in enumerate(merged):
    t0 = c[0]["t0"] - 0.06
    nxt = merged[j + 1][0]["t0"] - 0.06 if j + 1 < len(merged) else c[-1]["t1"] + 0.8
    data.append({"t0": round(t0, 3), "t1": round(min(nxt, c[-1]["t1"] + 0.7), 3),
                 "suppressed": sum(is_sup(x) for x in c) * 2 > len(c),
                 "words": [{"w": x["w"], "t0": x["t0"], "t1": x["t1"], "accent": x["w"] in ACCENT} for x in c]})
json.dump({"chunks": data}, open(P / "captions.json", "w"), ensure_ascii=False, indent=1)


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


with open(P / "captions.srt", "w") as f:
    for k, c in enumerate(data, 1):
        f.write(f"{k}\n{ts(c['t0'])} --> {ts(c['t1'])}\n{' '.join(w['w'] for w in c['words'])}\n\n")
print(len(data), "chunks -> captions.json, captions.srt")
for c in data:
    print(f"{c['t0']:7.2f}-{c['t1']:7.2f} {'S' if c['suppressed'] else ' '} " + " ".join(w["w"] for w in c["words"]))
