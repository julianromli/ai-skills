"""Render the whole edit with raea, encode the delivery MP4 with the audio, and check it.

    python deliver.py PROJECT -o OUT.mp4                       # original audio from the source, copied bit-exact
    python deliver.py PROJECT -o OUT.mp4 --audio mix.wav       # a mixed track (build_sfx.py), AAC 256k
    python deliver.py PROJECT --stills 12.5,40.2 -o stills/    # PNG stills at programme seconds

Delivery: H.264 High, CRF 20, maxrate 50M, BT.709 tags, same size/fps/frame count as the source.
Checks: frame count and duration against the source, full decode, colour tags, audio sync (cross-correlation
against the source speech) and loudness. A failed check exits 1 and says which.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np

RAEA = os.path.expanduser("~/.local/bin/raea")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def decode_audio(path, sr=44100):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--audio"); ap.add_argument("--stills")
    ap.add_argument("--keep-master", action="store_true")
    ap.add_argument("--preset", default="slow", help="x264 preset: slow (final) or medium/fast (review copies, ~2-4x faster)")
    a = ap.parse_args()
    P = Path(a.project).resolve(); R = P / "raea"
    T = json.load(open(P / "timeline.json")); S = T["source"]
    src = (P / S["path"]).resolve()
    if not (R / "edit.tsx").exists():
        sys.exit("run prep.py first (PROJECT/raea/edit.tsx is missing)")

    if a.stills:
        frames = ",".join(str(round(float(x) * S["fps"])) for x in a.stills.split(","))
        r = run([RAEA, "render", str(R / "edit.tsx"), "--at", frames, "-o", str(Path(a.out).resolve()) + "/"])
        print("\n".join(l for l in (r.stdout + r.stderr).splitlines() if "APPLIED" in l or "REFUSED" in l))
        return

    out = Path(a.out).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
    master = out.with_suffix(".master.mp4")
    t0 = time.time()
    # raea's MP4 writer can't exceed 4 GB (u32 mdat): pick the highest bitrate that fits, at most 250 Mbit/s
    dur = S["frames"] / S["fps"]
    kbps = int(min(250_000, 0.85 * 4.29e9 * 8 / dur / 1000))
    print(f"raea master at {kbps // 1000} Mbit/s", flush=True)
    r = run([RAEA, "render", str(R / "edit.tsx"), "-o", str(master), "--kbps", str(kbps)])
    msg = [l for l in (r.stdout + r.stderr).splitlines() if "APPLIED" in l or "REFUSED" in l or "error" in l.lower()]
    print("\n".join(msg[-3:]), f"({time.time() - t0:.0f} s)")
    if r.returncode != 0 or not master.exists():
        sys.exit("raea render failed")

    audio_in = ["-i", a.audio] if a.audio else ["-i", str(src)]
    # AAC overshoots up to ~2.5 dB on sharp SFX transients: a -3 dBFS peak limiter (latency-compensated, so sync
    # stays exact) catches them; it only acts on those few peaks. The original audio is copied untouched.
    audio_codec = ["-af", "alimiter=limit=0.708:attack=1:release=40:level=disabled:latency=1",
                   "-c:a", "aac", "-b:a", "256k"] if a.audio else ["-c:a", "copy"]
    t1 = time.time()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), *audio_in, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", a.preset, "-crf", "20", "-maxrate", "50M", "-bufsize", "100M",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-x264-params", "keyint=120:min-keyint=60",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                    "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0",
                    *audio_codec, "-movflags", "+faststart", str(out)], check=True)
    print(f"encoded {out.name} ({time.time() - t1:.0f} s)")
    if not a.keep_master:
        master.unlink()

    fails = []
    info = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                           "stream=codec_type,nb_read_frames,width,height,color_primaries:format=duration", "-of", "json", str(out)]).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    if int(v["nb_read_frames"]) != S["frames"]: fails.append(f"frames {v['nb_read_frames']} != source {S['frames']}")
    OW, OH = T.get("output", {}).get("width", S["width"]), T.get("output", {}).get("height", S["height"])
    if (v["width"], v["height"]) != (OW, OH): fails.append(f"size {v['width']}x{v['height']} != canvas {OW}x{OH}")
    if v.get("color_primaries") != "bt709": fails.append("colour tags missing")
    if run(["ffmpeg", "-v", "error", "-i", str(out), "-f", "null", "-"]).stderr.strip(): fails.append("decode errors")
    x, y = decode_audio(src), decode_audio(out)
    offs = []
    for sec in np.linspace(5, max(6, len(x) / 44100 - 5), 4):
        i = int(sec * 44100); seg = x[i:i + 44100]
        if len(seg) < 44100 or np.abs(seg).max() < 1e-3: continue
        offs.append(max(range(-300, 301), key=lambda k: float(np.dot(seg, y[i + k:i + k + 44100]))))
    if any(abs(o) > 2 for o in offs): fails.append(f"audio offset {offs} samples")
    lufs = run(["ffmpeg", "-nostats", "-i", str(out), "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    I = [l.split()[1] for l in lufs.splitlines() if l.strip().startswith("I:")]
    pk = [l.split()[1] for l in lufs.splitlines() if l.strip().startswith("Peak:")]
    print(f"check: {v['nb_read_frames']} frames, {float(info['format']['duration']):.2f} s, sync offsets {offs}, "
          f"{I[-1] if I else '?'} LUFS, true peak {pk[-1] if pk else '?'} dBFS")
    if pk and float(pk[-1]) > 0: fails.append(f"true peak {pk[-1]} dBFS > 0")
    mode = T.get("captions", "burn")
    if mode in ("burn", "srt") and (P / "captions.srt").exists():
        import shutil
        shutil.copy2(P / "captions.srt", out.with_suffix(".srt"))
        print(f"captions: {mode} ->", out.with_suffix(".srt").name)
    if fails:
        sys.exit("CHECK FAILED: " + "; ".join(fails))
    print("all checks passed:", out)


if __name__ == "__main__":
    main()
