"""Build the final SRT + TXT from a raw export: name fixes, extra regex fixes, cues of max 5 words.
usage: build_srt.py <raw.srt> <raw.txt> <out base path (no extension)> [extra-rules.json]
extra-rules.json: [[regex, replacement], ...] for this video, applied after the built-in rules."""
import os, re, sys, json, collections
sys.argv, args = sys.argv[:1], sys.argv[1:]
sys.path.insert(0, os.path.dirname(__file__))
from fix_names import fix_tokens  # noqa: E402

EXTRA = [(r"\bkalau [Cc]loud\b", "kalau Claude"), (r"\b[Cc]loud [Oo]pus\b", "Claude Opus"), (r"\bhajing face\b", "Hugging Face"),
         (r"\bhiding face\b", "Hugging Face"), (r"\b[Mm]3\.1 flash\b", "M3.1 Flash"), (r"\bgrokput\b", "Grok Bot"),
         (r"\b3GS\b", "Three.js"), (r"\b3gs\b", "Three.js"), (r"\bnpm rendev\b", "npm run dev"), (r"\b[Hh]udi\b", "hoodie"),
         (r"\bEGo\b", "Ego"), (r"\bharnasnya\b", "harness-nya"), (r"\bFaisal (Yudhivada|Intifada)\b", "Faiz Intifada"),
         (r"\bagent decoding\b", "agent coding"), (r"\bminimax kode\b", "MiniMax Code"), (r"\b[Mm]inimax\b", "MiniMax"),
         (r"\bcode\.MiniMax\.io\b", "code.minimax.io"), (r"\bfabel\b", "Fable"), (r"\bnetfall\b", "Nightfall"),
         (r"\bsemangsa\b", "semaksimal"), (r"\bstress-stress\b", "stress test"), (r"\btext tag-nya\b", "tech stack-nya")]
GLUE = {"Grok", "Claude", "MiniMax", "Hugging", "M3.1", "npm", "run", "Three.js", "AI", "Faiz", "Ego", "vibe"}


def t(s):
    h, m, r = s.split(":"); sec, ms = r.split(","); return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def ts(x):
    ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def fix_text(texts):
    toks = [[ci, w] for ci, s in enumerate(texts) for w in s.split()]
    per = [[] for _ in texts]
    for ci, w in fix_tokens(toks, collections.Counter()): per[ci].append(w)
    out = []
    for ws in per:
        s = " ".join(ws)
        for a, b in EXTRA: s = re.sub(a, b, s)
        out.append(s)
    return out


raw_srt, raw_txt, base = args[:3]
if len(args) > 3: EXTRA += [tuple(r) for r in json.load(open(args[3], encoding="utf-8"))]
blocks = [b.split("\n") for b in open(raw_srt, encoding="utf-8").read().strip().split("\n\n")]
texts = fix_text([" ".join(b[2:]) for b in blocks])
cues = []
for b, text in zip(blocks, texts):
    if not text.strip(): continue
    a, c = [t(v) for v in b[1].split(" --> ")]; w = text.split()
    if len(w) <= 5: cues.append((a, c, text)); continue
    k = (len(w) + 1) // 2
    while 0 < k < len(w) and w[k - 1].strip(".,") in GLUE: k += 1
    if k >= len(w): k = (len(w) + 1) // 2 - 1
    p1, p2 = " ".join(w[:k]), " ".join(w[k:]); m = a + (c - a) * len(p1) / (len(p1) + len(p2))
    cues += [(a, m - 0.01, p1), (m, c, p2)]
open(base + ".srt", "w", encoding="utf-8").write("".join(f"{i}\n{ts(a)} --> {ts(c)}\n{s}\n\n" for i, (a, c, s) in enumerate(cues, 1)))

paras = open(raw_txt, encoding="utf-8").read().strip().split("\n\n")
heads = [re.match(r"(\[[^\]]*\]\s*)?", p).group(0) for p in paras]
body = fix_text([p[len(h):] for p, h in zip(paras, heads)])
open(base + ".txt", "w", encoding="utf-8").write("\n\n".join(h + b for h, b in zip(heads, body)) + "\n")
bad = sum(1 for i, (a, c, s) in enumerate(cues) if len(s.split()) > 5 or c <= a or (i and a < cues[i - 1][1]))
print(f"{len(cues)} cues, problems {bad}, end {ts(cues[-1][1])}")
