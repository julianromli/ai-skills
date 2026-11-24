"""Add manual zooms (global recording times) to a Cap config and shift the camera.
usage: cap_zooms_camera.py <config in> <segments.json> <zooms.json> <camera shift s> <config out>
zooms.json: [[globalStart, globalEnd, x, y, label], ...]  x/y 0..1 from the top-left of the screen."""
import json, sys

cfg_in, segs_path, zooms_path, shift, out = sys.argv[1:]
cfg, segs = json.load(open(cfg_in)), json.load(open(segs_path))
seg_start = {s["index"]: s["start"] for s in segs}
clips = [(seg_start[c["recordingSegment"]] + c["start"], seg_start[c["recordingSegment"]] + c["end"], c.get("timescale", 1.0))
         for c in cfg["timeline"]["segments"]]


def tl(g):
    acc = 0.0
    for a, b, ts in clips:
        if g < a: return acc
        if g <= b: return acc + (g - a) / ts
        acc += (b - a) / ts
    return acc


zs = []
for a, b, x, y, label in json.load(open(zooms_path)):
    s, e = tl(a), tl(b)
    zs.append({"start": round(s, 3), "end": round(e, 3), "amount": 1.5, "mode": {"manual": {"x": x, "y": y}},
               "glideDirection": "none", "glideSpeed": 0.5, "instantAnimation": False, "edgeSnapRatio": 0.25})
    print(f"{int(s // 60):02d}:{s % 60:04.1f}-{int(e // 60):02d}:{e % 60:04.1f} ({e - s:4.1f}s) {label}")
cfg["timeline"]["zoomSegments"] = zs
for c in cfg.get("clips") or []:
    c["offsets"]["camera"] = round(c["offsets"].get("camera", 0.0) + float(shift), 6)
    c["offsetsAutoCalculated"] = False
json.dump(cfg, open(out, "w"), indent=2)
print("camera offsets:", sorted({c["offsets"]["camera"] for c in cfg.get("clips") or []}))
