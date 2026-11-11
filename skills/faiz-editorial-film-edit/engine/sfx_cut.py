"""Cut single sound effects out of the 3 Instagram SFX reels (assets/sfx/source/*.mp4).

Each clip gets a 3 ms fade-in and a short fade-out and is peak-normalised to -1 dBFS.
library.json keeps the loudest 50 ms RMS ("rms_db"); build_sfx.py uses it to set the level per event.
Writes assets/sfx/<name>.wav (44.1 kHz stereo, float) and assets/sfx/library.json.
Run: python sfx_cut.py PROJECT   (reels and cut points: PROJECT/sfx_config.json "reels", "cuts")
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(sys.argv[1]).resolve()
SRC = ROOT / "assets/sfx/source"
OUT = ROOT / "assets/sfx"
CFG = json.load(open(ROOT / "sfx_config.json"))
SR = 44100
REELS = CFG["reels"]      # letter -> downloaded file stem in assets/sfx/source
# name: (reel, start s, end s, label shown in the reel)
CUTS = {k: tuple(v) for k, v in CFG["cuts"].items()}   # name -> [reel, start s, end s, label]

def load(reel):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC / f"{REELS[reel]}.mp4"), "-vn",
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def env50(x):
    h = int(SR * 0.05)
    m = (x ** 2).mean(1)
    c = np.convolve(m, np.ones(h) / h, "same")
    return np.sqrt(c)

def main():
    audio = {k: load(k) for k in REELS}
    lib = {}
    for name, (reel, a, b, label) in CUTS.items():
        x = audio[reel][int(a * SR):int(b * SR)].copy()
        fi, fo = int(0.003 * SR), min(int(0.04 * SR), len(x) // 3)
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
        x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        x *= 10 ** (-1 / 20) / max(np.abs(x).max(), 1e-6)
        # first 20 ms window that reaches -6 dB of the loudest window = the "hit" point
        e = env50(x)
        hit = int(np.argmax(e > e.max() * 0.5))
        import wave
        with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        lib[name] = {"reel": REELS[reel], "from": a, "to": b, "label": label,
                     "dur": round(len(x) / SR, 3), "hit": round(hit / SR, 3),
                     "rms_db": round(float(20 * np.log10(e.max() + 1e-9)), 1)}
        print(f"{name:20} {lib[name]['dur']:5.2f}s hit {lib[name]['hit']:.2f}s rms50 {lib[name]['rms_db']:6.1f} dB  ({label})")
    json.dump(lib, open(OUT / "library.json", "w"), indent=1)

if __name__ == "__main__":
    main()
