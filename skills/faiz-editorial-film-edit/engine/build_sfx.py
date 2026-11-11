"""Place sound effects on the element transitions of timeline.json and mix them under the speech.

Step 1 (default): timeline.json -> sfx.json (one event per transition; edit this file by hand if needed).
Step 2: sfx.json + original audio -> PROJECT/out/audio_sfx.wav (speech unchanged, SFX added) + out/sfx_only.wav.
  python build_sfx.py PROJECT             # make sfx.json, then mix
  python build_sfx.py PROJECT --mix-only  # mix from the existing (hand-edited) sfx.json
Needs PROJECT/assets/sfx/library.json (sfx_cut.py). Title cards: "titles" in PROJECT/sfx_config.json maps a text id
to "impact", "riser+impact" or "glacial". Cuts already in the footage: timeline.json source.baked_cuts.

Default rules (change LEVEL / VARIANTS below, or per project in sfx_config.json "level" / "variants"):
  split slide in / out          -> whoosh
  cut to photo / full / montage -> camera shutter
  collage build                 -> designed camera sequence
  cut back to the presenter     -> soft camera shutter
  stop-motion text (step)       -> shutter clicks
  other big text / each word    -> click, tap, button switch
  title cards                   -> riser into impact, cinematic whoosh
  Not used: photo credits, captions, text exits.
Level: "punchy", about 8 dB under the speech peaks. Each sound's "hit" lands on its frame.
"""
import json, subprocess, sys, wave
from pathlib import Path
import numpy as np

ROOT = Path(sys.argv[1]).resolve()
def _source_rate():
    T = json.load(open(ROOT / "timeline.json"))
    src = (ROOT / T["source"]["path"]).resolve()
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate",
                          "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else 48000
SR = _source_rate()          # mix at the source's own rate: the speech is never resampled
LIB = json.load(open(ROOT / "assets/sfx/library.json"))
CFG = json.load(open(ROOT / "sfx_config.json")) if (ROOT / "sfx_config.json").exists() else {}
SOURCE_CUTS = CFG.get("source_cuts", json.load(open(ROOT / "timeline.json"))["source"].get("baked_cuts", []))
OUT_GAIN_DB = -1.2                  # whole mix: headroom so the AAC encode stays under 0 dBFS true peak          # cuts that are in the original footage

# target loudest-50ms RMS in dBFS per role (speech words reach about -10 dBFS)
LEVEL = {**{"split": -17, "split_out": -20, "cut": -16, "cut_soft": -21, "collage": -19,
         "step": -20, "text": -18, "word": -20, "riser": -19, "impact": -15, "glacial": -16}, **CFG.get("level", {})}
VARIANTS = {**{
    "split": ["whoosh_gentle", "cinematic_woosh"],
    "split_out": ["woosh", "swoosh"],
    "cut": ["shutter_a", "shutter_c", "shutter_b", "shutter_d"],
    "cut_soft": ["shutter_swoosh", "shutter_swoosh_b"],
    "full": ["shutter_swoosh_b", "shutter_swoosh"],
    "collage": ["camera_seq03"],
    "step": ["shutter_clicks_v2", "shutter_clicks_v1", "shutter_clicks_v1b"],
    "text": ["button_switch", "click", "click_b", "pop"],
    "word": ["click", "click_b", "button_switch"],
}, **CFG.get("variants", {})}
PRIORITY = {"impact": 9, "glacial": 8, "riser": 8, "split": 7, "split_out": 6, "collage": 6,
            "cut": 5, "full": 5, "step": 4, "text": 3, "cut_soft": 3, "word": 2}
TITLES = CFG.get("titles", {})

_rot = {}
def pick(kind):
    v = VARIANTS[kind]; i = _rot.get(kind, 0); _rot[kind] = i + 1
    return v[i % len(v)]

def make_events():
    T = json.load(open(ROOT / "timeline.json"))
    ev = []
    def add(t, kind, why, sound=None, level=None, align="hit"):
        ev.append({"t": round(t, 3), "sound": sound or pick(kind), "role": kind,
                   "level_db": level if level is not None else LEVEL.get(kind, LEVEL["cut"]),
                   "align": align, "why": why})
    pres = [s for s in T["scenes"] if s["type"] == "presenter"]
    for t in SOURCE_CUTS:
        if not any(s["t0"] < t < s["t1"] for s in pres): continue      # a cut under an insert isn't seen
        add(t, "cut_soft", "cut in the original footage", sound="shutter_b", level=LEVEL["cut_soft"])
    scenes = T["scenes"]
    for i, s in enumerate(scenes):
        prev = scenes[i - 1] if i else None
        t0, typ = s["t0"], s["type"]
        if i == 0 or s["id"] == "s22_end":
            pass                                   # start of film / end card: the title sounds cover it
        elif typ == "split" and s.get("entry", True):
            add(t0 + 0.21, "split", f"{s['id']}: split slides in")
        elif typ == "split":
            add(t0, "cut", f"{s['id']}: new picture in the split panel")
        elif typ == "full":
            add(t0, "full", f"{s['id']}: cut to full-frame picture", level=LEVEL["cut"])
        elif typ == "collage":
            add(t0, "collage", f"{s['id']}: collage builds")
        elif typ == "montage":
            add(t0, "cut", f"{s['id']}: montage starts")
        elif typ == "presenter" and prev and not (prev["type"] == "split" and prev.get("exit", True)):
            add(t0, "cut_soft", f"{s['id']}: cut back to the presenter")
        if typ == "split" and s.get("exit", True):
            add(s["t1"] - 0.18, "split_out", f"{s['id']}: split slides out")
        for k in ("inserts", "items"):
            for it in (s.get(k) or [])[1:]:
                if it.get("t0") is not None:
                    add(it["t0"], "cut", f"{s['id']}: next picture ({it.get('media')})")
        for sh in (s.get("shots") or [])[1:]:
            add(sh["t0"], "cut", f"{s['id']}: montage shot {sh['media']}")
    for x in T["text"]:
        if "credit" in x["id"]:
            continue
        words = x.get("words") or [x["t0"]]
        label = x["text"].replace("*", "")
        title = TITLES.get(x["id"])
        if title:
            if "riser" in title:
                add(words[0], "riser", f"{x['id']}: build-up into the title", sound="riser", align="end")
            if "impact" in title:
                add(words[0], "impact", f"{x['id']}: title lands", sound="impact")
            if title == "glacial":
                add(words[0], "glacial", f"{x['id']}: title sweeps in", sound="whoosh_glacial")
            for w in words[1:]:
                add(w, "step", f"{x['id']}: next title word")
            continue
        kind = "step" if x.get("step") else "text"
        add(words[0], kind, f"{x['id']}: '{label}' appears")
        for w in words[1:]:
            add(w, "word", f"{x['id']}: next word of '{label}'")
    # one sound per moment: inside 0.12 s keep the stronger role
    ev.sort(key=lambda e: e["t"])
    out = []
    for e in ev:
        if e["role"] != "riser" and out:
            clash = [o for o in out if o["role"] != "riser" and abs(o["t"] - e["t"]) < 0.12]
            if clash:
                o = clash[0]
                if PRIORITY[e["role"]] > PRIORITY[o["role"]]:
                    out[out.index(o)] = e
                continue
        out.append(e)
    return out

def load_wav(p):
    w = wave.open(str(p))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    r = w.getframerate()
    if r != SR:   # library clips are 44.1 kHz: resample to the mix rate
        n = int(round(len(x) * SR / r))
        t = np.linspace(0, len(x) - 1, n)
        x = np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(2)], 1).astype(np.float32)
    return x

def mix(events):
    src = (ROOT / json.load(open(ROOT / "timeline.json"))["source"]["path"]).resolve()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn", "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    speech = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    fx = np.zeros_like(speech)
    for e in events:
        meta = LIB[e["sound"]]
        clip = load_wav(ROOT / f"assets/sfx/{e['sound']}.wav")
        clip = clip * 10 ** ((e["level_db"] - meta["rms_db"]) / 20)
        anchor = meta["dur"] if e["align"] == "end" else meta["hit"]
        a = int(round((e["t"] - anchor) * SR))
        if a < 0:
            clip, a = clip[-a:], 0
        b = min(a + len(clip), len(fx))
        fx[a:b] += clip[:b - a]
    # keep the speech untouched: where speech + sfx would pass -1 dBFS, turn the sfx down locally
    lim = 10 ** (-1 / 20)
    room = np.clip(lim - np.abs(speech), 0, None)
    need = np.where(np.abs(fx) > room, room / np.maximum(np.abs(fx), 1e-9), 1.0).min(1)
    win = int(0.01 * SR)
    g = np.minimum.reduceat(need, np.arange(0, len(need), win))
    g = np.repeat(g, win)[:len(need)]
    g = np.convolve(np.pad(g, (win, win), mode="edge"), np.ones(win) / win, "same")[win:-win]
    g = np.minimum(g, need)
    fx *= g[:, None]
    out = (speech + fx) * 10 ** (OUT_GAIN_DB / 20)
    print(f"{len(events)} events; sfx turned down on {np.mean(g < 0.999) * 100:.2f}% of samples; "
          f"peak {20 * np.log10(np.abs(out).max()):.2f} dBFS")
    (ROOT / "out").mkdir(exist_ok=True)
    dst = ROOT / "out/audio_sfx.wav"
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).round().astype("<i2").tobytes())
    with wave.open(str(ROOT / "out/sfx_only.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(fx, -1, 1) * 32767).round().astype("<i2").tobytes())
    print("wrote", dst.resolve())

if __name__ == "__main__":
    if "--mix-only" not in sys.argv:
        events = make_events()
        json.dump({"_note": "t = programme seconds where the sound's hit lands (align 'end': where it ends). "
                            "level_db = loudest-50ms RMS in dBFS. Edit, then run build_sfx.py --mix-only.",
                   "events": events}, open(ROOT / "sfx.json", "w"), indent=1, ensure_ascii=False)
        for e in events:
            print(f"{e['t']:7.2f}  {e['role']:9} {e['sound']:18} {e['why']}")
    mix(json.load(open(ROOT / "sfx.json"))["events"])
