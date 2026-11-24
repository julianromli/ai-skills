"""Merge exported parts into one video, audio at -14 LUFS (two-pass loudnorm), then verify.
usage: merge_parts.py <out.mp4> <part1.mp4> <part2.mp4> [...] [--hevc BITRATE] [--crop WxH]
  default: video stream copy (all parts must share codec, size and fps).
  --hevc 8M : re-encode with hevc_videotoolbox at this bitrate (use when the export is huge, or with --crop).
  --crop WxH: center-crop every part to WxH (parts differ by a few pixels) - implies re-encode.
Prints part durations (use part 1's for the merged SRT offset), loudness, full-decode errors."""
import json, re, subprocess, sys, tempfile, os

a = sys.argv[1:]
opt = {k: a[a.index(k) + 1] for k in ("--hevc", "--crop") if k in a}
files = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--hevc", "--crop"))]
if len(files) < 3: sys.exit(__doc__)
out, parts = files[0], files[1:]
if os.path.exists(out): sys.exit(f"exists: {out}")


def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                                         "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


for p in parts: print(f"{os.path.basename(p)}: video {dur(p):.3f} s")
inputs = sum((["-i", p] for p in parts), [])
n = len(parts)
if "--crop" in opt:
    w, h = opt["--crop"].split("x")
    vf = "".join(f"[{i}:v]crop={w}:{h},setsar=1[v{i}];" for i in range(n))
    cat = "".join(f"[v{i}][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    graph = vf + cat
else:
    graph = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
copy = "--hevc" not in opt and "--crop" not in opt
if copy:  # concat demuxer keeps the video bitstream
    lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    lst.write("".join(f"file '{p}'\n" for p in parts)); lst.close()
    src = ["-f", "concat", "-safe", "0", "-i", lst.name]
    amap = ["-map", "0:a"]
else:
    src = inputs + ["-filter_complex", graph]
    amap = ["-map", "[a]"]
measure = "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json"
if copy:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *src, *amap, "-af", measure, "-f", "null", "-"], capture_output=True, text=True)
else:  # measure on the concatenated audio
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *inputs, "-filter_complex",
                        "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1,{measure}[o]",
                        "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
m = json.loads(re.search(r"\{[^{}]*input_i[^{}]*\}", r.stderr).group(0))
print("measured", m["input_i"], "LUFS, true peak", m["input_tp"])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']},aresample=48000")
venc = ["-c:v", "copy"] if copy else ["-c:v", "hevc_videotoolbox", "-b:v", opt.get("--hevc", "8M"), "-tag:v", "hvc1", "-profile:v", "main",
                                      "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
if copy:
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", *src, "-map", "0:v", "-map", "0:a", *venc, "-af", ln]
else:
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", *inputs, "-filter_complex", graph.replace("[a]", "[a0]") + f";[a0]{ln}[a]",
           "-map", "[v]", "-map", "[a]", *venc]
subprocess.run(cmd + ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print(f"merged: {out} ({os.path.getsize(out) / 1e9:.2f} GB), video {dur(out):.3f} s")
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", out, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
print("output:", " | ".join(l.strip() for l in r.stderr.splitlines() if re.match(r"\s+(I|Peak):", l))[-60:])
err = subprocess.run(["ffmpeg", "-v", "error", "-i", out, "-map", "0:v", "-f", "null", "-"], capture_output=True, text=True).stderr.strip()
print("decode:", "OK" if not err else err[:300])
