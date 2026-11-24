"""Fix ASR name spellings in .srt / .txt files, also across cue boundaries.
usage: fix_names.py <file>...   (writes <file>, keeps <name>.asr<ext> once)"""
import re, sys, shutil, os, collections

EDGE = ".,?!…:;\"'"
# (token sequence, normalized lowercase) -> replacement; "*" token suffix "nya" allowed on last token
RULES = [
    ("kedokter ek", "ke Dr. Eggbot"), ("dr. eggbot", "Dr. Eggbot"), ("dr eggbot", "Dr. Eggbot"),
    ("dokter eggbot", "Dr. Eggbot"), ("dokter eggbrot", "Dr. Eggbot"), ("dokter grokbot", "Dr. Eggbot"),
    ("dr grogbot", "Dr. Eggbot"), ("dr egg", "Dr. Eggbot"), ("ekbot", "Dr. Eggbot"), ("eggbot", "Dr. Eggbot"),
    ("geruk bot", "Grok Bot"), ("mid grok bot", "mid Grok Bot"), ("grok bot", "Grok Bot"), ("grokbots", "Grok Bot"),
    ("grokbot", "Grok Bot"), ("grokpot", "Grok Bot"), ("grogbot", "Grok Bot"), ("growbot", "Grok Bot"),
    ("glockbot", "Grok Bot"), ("clockpot", "Grok Bot"), ("grokbo", "Grok Bot"), ("sigrok", "si Grok"),
    ("cloud code cli", "Claude Code CLI"), ("cloud code dash", "Claude Code"), ("cloud code", "Claude Code"),
    ("cloud desktop", "Claude desktop"), ("di cloud ke kalian", "di Claude Code kalian"), ("di cloud ini selama", "di Claude ini selama"), ("buka cloud kalian", "buka Claude kalian"), ("opencloud", "OpenClaw"), ("open cloud", "OpenClaw"), ("cloud design", "Claude Design"), ("cloud motion", "Claude Motion"),
    ("cloud startup", "Claude for Startups"), ("cloud atau codecs", "Claude atau Codex"), ("pake cloud mcp", "pake claude mcp"),
    ("codecs", "Codex"), ("kodex", "Codex"), ("codex", "Codex"),
    ("pendrift", "Pen.dev"), ("pendrive", "Pen.dev"),
    ("mobien", "Mobbin"), ("mobin", "Mobbin"), ("mobi", "Mobbin"),
    ("vapcoding", "vibe coding"), ("vapcuring", "vibe coding"),
    ("wounder", "Wonder"), ("wanderer", "Wonder"), ("hounder", "Wonder"), ("di owner ini", "di Wonder ini"),
    ("haikyu", "Haiku"), ("quiver row", "Quiver Arrow"), ("raw punya quiver", "Arrow punya Quiver"),
    ("thresh", "Threads"), ("trades", "Threads"),
    ("jacob.kr", "jakub.kr"), ("jacob rehall", "Jakub Krehel"), ("jacob punya", "Jakub punya"), ("jago pro helm", "Jakub Krehel"),
    ("konteks 7", "Context7"), ("anthrofic", "Anthropic"), ("xfield", "Higgsfield"), ("eleven labs", "ElevenLabs"),
    ("daya browser", "Dia browser"), ("egoled", "ego-lite"), ("keya", "QA"), ("key a", "QA"), ("cke", "QA"),
    ("dialkit.tiff", "dialkit.dev"), ("measurer.tiff", "measurer.dev"), ("mesurer.dev", "measurer.dev"),
    ("mesurer dev", "measurer.dev"), ("measure depth", "measurer.dev"), ("agitation", "Agentation"),
    ("emdash", "em dash"), ("n8n", "n8n"), ("nanoband", "Nano Banana"), ("anti graffiti", "Antigravity"),
    ("anti-gravity", "Antigravity"), ("code rabbit", "CodeRabbit"), ("kubik.dev", "cubic.dev"),
    ("link.id", "lynk.id"), ("link id", "lynk.id"), ("fvp hunter", "FYP Hunter"), ("fyp hunter", "FYP Hunter"),
    ("x.aipricing", "x.ai/pricing"), ("firecrawl", "Firecrawl"),
    # minimax-code video
    ("ga bakal pake cloud", "ga bakal pake Claude"), ("minimax code", "MiniMax Code"), ("minimax kode", "MiniMax Code"),
    ("minimax agent", "MiniMax Agent"), ("minimax", "MiniMax"), ("wondermcp", "Wonder MCP"), ("wonder mcp", "Wonder MCP"),
    ("wonder", "Wonder"), ("wander", "Wonder"), ("interfere", "Interfere"), ("interfare", "Interfere"),
    ("front tire", "frontier"), ("jacob.kr/.skills", "jakub.kr/skills"), ("skills jacob.kr/.skills", "skills jakub.kr/skills"),
    ("emil skowalski", "Emil Kowalski"), ("matt pokoch", "Matt Pocock"), ("grillme", "grill-me"), ("grill me", "grill-me"),
    ("trope", "Troupe"), ("trove", "Troupe"), ("thermal app", "Termul app"), ("shade cn", "shadcn"), ("shadecn", "shadcn"),
    ("versal react", "Vercel React"), ("boon run dev", "bun run dev"), ("ermine", "Ermine"),
    ("desain amd", "DESIGN.md"), ("design amd", "DESIGN.md"), ("desain md", "DESIGN.md"), ("design md", "DESIGN.md"),
    ("desain .md", "DESIGN.md"), ("kontekstu gmcp", "Context7 MCP"), ("ibelik", "ibelick"),
    ("create-strip-design-strip-md", "create-design-md"), ("fight aja", "Vite aja"), ("dhp", "di HP"),
    ("refill animation", "reveal animation"), ("ai stock", "AI stack"), ("webcoding", "vibe coding"),
    ("agents mdk", "AGENTS.md"), ("agents md", "AGENTS.md"), ("transitions .dev", "transitions.dev"),
    # higgsfield-mcp video
    ("hexfield.ai", "higgsfield.ai"), ("xfield", "Higgsfield"), ("higgs field", "Higgsfield"), ("higgsville", "Higgsfield"),
    ("higgsfield mcp", "Higgsfield MCP"), ("higgsfield mcps", "Higgsfield MCP"), ("higgsfield mcb", "Higgsfield MCP"),
    ("higgsfield mcp", "Higgsfield MCP"), ("hvlm cp", "Higgsfield MCP"), ("hvlm", "Higgsfield"), ("xlm zip", "Higgsfield MCP"),
    ("xvil katana", "Higgsfield Katana"), ("waveline", "Higgsfield"), ("mcb", "MCP"),
    ("smle-ai", "AssemblyAI"), ("smlei", "AssemblyAI"), ("sml ai", "AssemblyAI"), ("assemble ai", "AssemblyAI"),
    ("assembly ai", "AssemblyAI"), ("sydens 2.5", "Seedance 2.5"), ("dense 2.5", "Seedance 2.5"), ("sedans 2.5", "Seedance 2.5"),
    ("the fest bandung", "DevFest Bandung"), ("the vest", "DevFest"), ("devface", "DevFest"), ("dvs", "DevFest"),
    ("lhotel", "eL Hotel"), ("el hotel", "eL Hotel"), ("l hotel", "eL Hotel"), ("r.a.i.a", "raea"),
    ("hiq", "Haiku"), ("jgpt", "ChatGPT"), ("11 labs", "ElevenLabs"), ("cia-nya", "AI-nya"),
    ("kelawakan, tanggut", "kelabakan, takut"), ("kelemahkan", "kelabakan"), ("langgaran", "langganan"),
    ("editor film edit", "editorial-film-edit"), ("remotion", "Remotion"), ("sikaye", "si Kye"),
]
RULES = sorted(((r.split(), v) for r, v in RULES), key=lambda x: -len(x[0]))
CASE_RULES = [(["KE"], "QA")]  # uppercase only: "ngelakuin KE"; lowercase "ke" = "to"

def norm(t): return t.strip(EDGE).lower()

def fix_tokens(toks, counts):
    """toks: list of [cue_index, word]. Replaces in place; merged words go to the first word's cue."""
    out, i = [], 0
    while i < len(toks):
        done = False
        for pat, rep in CASE_RULES:
            if toks[i][1].strip(EDGE) == pat[0]:
                w = toks[i][1]; core = w.strip(EDGE); out.append([toks[i][0], w.replace(core, rep)])
                counts[f"{core} -> {rep}"] += 1; i += 1; done = True; break
        if done: continue
        for pat, rep in RULES:
            n = len(pat)
            if i + n > len(toks): continue
            ws = [norm(t[1]) for t in toks[i:i + n]]
            if ws[:-1] != pat[:-1]: continue
            m = re.fullmatch(re.escape(pat[-1]) + r"(-?nya)?", ws[-1])
            if not m: continue
            last = toks[i + n - 1][1]
            core_end = len(last.rstrip(EDGE)); tail = last[core_end:]
            lead = toks[i][1][:len(toks[i][1]) - len(toks[i][1].lstrip(EDGE))]
            suf = "-nya" if m.group(1) else ""
            new = lead + rep + suf + tail
            counts[f"{' '.join(t[1] for t in toks[i:i + n])} -> {rep}{suf}"] += 1
            # keep words of later cues as empty so cue timing stays; text moves to first cue
            out.append([toks[i][0], new])
            i += n; done = True; break
        if not done:
            out.append(toks[i]); i += 1
    return out

def process(path):
    ext = os.path.splitext(path)[1]
    bak = path[:-len(ext)] + ".asr" + ext
    if not os.path.exists(bak): shutil.copy(path, bak)
    src = open(bak, encoding="utf-8").read()
    counts = collections.Counter()
    if ext == ".srt":
        blocks = [b.split("\n") for b in src.strip().split("\n\n")]
        texts = [" ".join(b[2:]) for b in blocks]
    else:
        paras = [p for p in src.strip().split("\n\n")]
        heads = [re.match(r"(\[[^\]]*\]\s*)?", p).group(0) for p in paras]
        texts = [p[len(h):] for p, h in zip(paras, heads)]
    toks = [[ci, w] for ci, t in enumerate(texts) for w in t.split()]
    new = fix_tokens(toks, counts)
    per = [[] for _ in texts]
    for ci, w in new: per[ci].append(w)
    if ext == ".srt":
        res = []
        for b, ws in zip(blocks, per):
            res.append("\n".join(b[:2] + [" ".join(ws) if ws else "..."]))
        open(path, "w", encoding="utf-8").write("\n\n".join(res) + "\n")
    else:
        open(path, "w", encoding="utf-8").write("\n\n".join(h + " ".join(ws) for h, ws in zip(heads, per)) + "\n")
    print(f"== {os.path.basename(path)}: {sum(counts.values())} fixes")
    for k, v in counts.most_common(): print(f"   {v:3d}  {k}")

for p in sys.argv[1:]: process(p)
