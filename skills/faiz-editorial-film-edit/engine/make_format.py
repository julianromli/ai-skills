"""Make a 9:16, 4:5 or 5:4 version of an approved master edit (any source shape, e.g. 16:9).

    python make_format.py MASTER --aspect 9:16 [--out MASTER/formats/9x16]

What it does (a first pass; the agent then checks stills and fixes what doesn't fit):
  1. Canvas: platform size (9:16 1080x1920, 4:5 1080x1350, 5:4 1350x1080). Same fps, frames and timing.
  2. Reframe: YuNet face tracking (engine/models) on the source (5 samples/s), gaps filled, smoothed per shot (never across the
     cuts in source.baked_cuts) -> timeline "reframe" track. The presenter's face stays centred.
  3. Scenes: in portrait formats (9:16, 4:5) a split becomes a full-frame cut to its picture(s) (one insert -> full,
     several -> montage); collage photos move to the top of the frame. 5:4 keeps splits and collages.
  4. Text: behind-the-presenter words stay at the head and are fitted to the width; other text is stacked in the
     lower safe zone in its original order; small mono credits go to the top-left. Every line is measured with the
     real fonts and shrunk to fit. Panel text loses its panel.
  5. Captions: shorter chunks (max_chars per format), bigger size and a y above the platform's bottom buttons.
The format folder is a normal project: prep.py, deliver.py (use the master's audio mix with --audio) and edits
to its own timeline.json work as usual. Media and masks are shared with the master (absolute paths / links).
"""
import argparse, copy, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import ImageFont

ENGINE = Path(__file__).resolve().parent
FORMATS = {   # canvas, caption y, caption ref size, caption max chars, text zone (top, bottom), safe left/right
    "9:16": dict(w=1080, h=1920, cap_y=0.755, cap_size=72, cap_chars=22, zone=(0.47, 0.705), left=0.08, right=0.87),
    "4:5": dict(w=1080, h=1350, cap_y=0.845, cap_size=64, cap_chars=26, zone=(0.50, 0.78), left=0.07, right=0.93),
    "5:4": dict(w=1350, h=1080, cap_y=0.885, cap_size=58, cap_chars=32, zone=None, left=0.05, right=0.95),
}


def face_track(src, fps_src, frames, baked, pcx, sample=5.0):
    """Per-sample face centre (cx, cy) in 0-1 source coords, smoothed within shots. Returns [[t, cx, cy, 1.0], ...]."""
    w = 640
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height", "-of", "json", str(src)], capture_output=True, text=True).stdout)
    sw, sh = info["streams"][0]["width"], info["streams"][0]["height"]
    h = int(round(sh * w / sw / 2) * 2)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"fps={sample},scale={w}:{h},format=bgr24",
                          "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    # YuNet (OpenCV zoo, MIT, bundled in engine/models): OpenCV 5 has no Haar cascades
    det = cv2.FaceDetectorYN.create(str(ENGINE / "models/face_detection_yunet_2023mar.onnx"), "", (w, h), 0.7, 0.3, 50)
    xs, ys, bottoms = [], [], []
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: break
        _, f = det.detect(np.frombuffer(buf, np.uint8).reshape(h, w, 3))
        if f is not None and len(f):
            x, y, fw, fh = max(f[:, :4], key=lambda r: r[2] * r[3])
            xs.append((x + fw / 2) / w); ys.append((y + fh / 2) / h); bottoms.append((y + fh) / h)
        else:
            xs.append(np.nan); ys.append(np.nan)
    p.wait()
    t = np.arange(len(xs)) / sample
    xs, ys = np.array(xs), np.array(ys)
    found = ~np.isnan(xs)
    print(f"face found in {found.mean() * 100:.0f}% of {len(xs)} samples", flush=True)
    if found.sum() < 2:
        return [[0.0, pcx, 0.5, 1.0]], 0.0, None
    xs = np.interp(t, t[found], xs[found]); ys = np.interp(t, t[found], ys[found])
    # smooth inside each shot: median (removes false detections), then a gaussian (~1 s): a slow virtual camera
    edges = [0.0] + sorted(c for c in baked if 0 < c < frames / fps_src) + [frames / fps_src + 1]
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (t >= a) & (t < b)
        if not m.any(): continue
        for arr in (xs, ys):
            seg = arr[m].copy()
            if len(seg) >= 5:
                pad = np.pad(seg, 2, mode="edge")
                seg = np.array([np.median(pad[i:i + 5]) for i in range(len(seg))])
                ker = cv2.getGaussianKernel(int(sample * 3) | 1, sample * 0.8).ravel()
                seg = np.convolve(np.pad(seg, len(ker) // 2, mode="edge"), ker, "valid")
            arr[m] = seg
        idx = np.nonzero(m)[0]
        keep = idx[::2].tolist() + [idx[-1]]
        if out and a > 0:      # hard cut: hold the old framing to the cut, jump on it
            out.append([round(a - 0.001, 3), out[-1][1], out[-1][2], 1.0])
        for i in sorted(set(keep)):
            out.append([round(max(t[i], a), 3), round(float(xs[i]), 4), round(float(ys[i]), 4), 1.0])
    # where the chin usually is (90th percentile of face-box bottoms; YuNet boxes end near the chin)
    chin = float(np.percentile(bottoms, 90)) if bottoms else None
    return out, float(found.mean()), chin


class Measure:
    def __init__(self, st):
        self.st, self.cache = st, {}

    def font(self, key, px):
        k = (key, int(px))
        if k not in self.cache:
            f = self.st["fonts"].get(key) or self.st["fonts"]["sans"]
            self.cache[k] = ImageFont.truetype(f["file"], max(int(px), 4), index=f["index"])
        return self.cache[k]

    def width(self, spec, px):
        """Width in px of a text layer at size px (rich *italic* runs, tracking)."""
        total, first = 0.0, True
        for pi, part in enumerate(str(spec["text"]).split("*")):
            it = pi % 2 == 1
            for wd in part.split(" "):
                if not wd: continue
                key = "serif_it" if it else spec.get("font", "sans")
                sz = px * (1.1 if it and str(spec.get("font", "sans")).startswith("sans") else 1.0)
                f = self.font(key, sz)
                tr = 0 if it else spec.get("tracking", 0.0) * px * max(len(wd) - 1, 0)
                total += (0 if first else f.getlength(" ")) + f.getlength(wd) + tr
                first = False
        return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("master"); ap.add_argument("--aspect", required=True, choices=list(FORMATS))
    ap.add_argument("--out")
    a = ap.parse_args()
    M = Path(a.master).resolve()
    F = FORMATS[a.aspect]
    out = Path(a.out).resolve() if a.out else M / "formats" / a.aspect.replace(":", "x")
    out.mkdir(parents=True, exist_ok=True)
    T = json.load(open(M / "timeline.json")); st = json.load(open(M / "style.json"))
    S = T["source"]; W, H = F["w"], F["h"]
    portrait = W < H
    K = min(W, H) / st.get("ref_height", 1440)
    meas = Measure(st)

    # ---- shared material: absolute media/source paths, linked transcript and masks
    T2 = copy.deepcopy(T)
    T2["source"]["path"] = str((M / S["path"]).resolve())
    for m in T2["media"].values():
        m["path"] = str((M / m["path"]).resolve())
    T2["output"] = {"width": W, "height": H, "path": f"out/edit_{a.aspect.replace(':', 'x')}_v1.mp4", "aspect": a.aspect}
    (out / "cache").mkdir(exist_ok=True)
    for name, target in (("transcript", M / "transcript"), ("cache/masks", M / "cache/masks")):
        l = out / name
        if not l.exists() and target.exists():
            l.symlink_to(target)

    # ---- 2. reframe
    T2["reframe"], hit, chin = face_track(Path(T2["source"]["path"]), S["fps"], S["frames"], S.get("baked_cuts", []),
                                    S.get("presenter_center_x", 0.5))

    # ---- 3. scenes
    split_ids = set()
    if portrait:
        for i, sc in enumerate(T2["scenes"]):
            if sc["type"] == "split":
                split_ids.add(sc["id"])
                ins = sc["inserts"]
                mv = lambda x: {"from": [x["focus"][0], x["focus"][1], x.get("push", [1, 1])[0]],
                                "to": [x["focus"][0], x["focus"][1], x.get("push", [1, 1])[1]]}
                base = {k: sc[k] for k in ("id", "t0", "t1") if k in sc}
                if len(ins) == 1:
                    T2["scenes"][i] = {**base, "type": "full", "media": ins[0]["media"], "src_t0": ins[0].get("src_t0", 0.0),
                                       "move": mv(ins[0]), "_was": "split"}
                else:
                    T2["scenes"][i] = {**base, "type": "montage", "_was": "split",
                                       "shots": [{"media": x["media"], "t0": x["t0"], "t1": x["t1"], "move": mv(x)} for x in ins]}
            elif sc["type"] == "collage":
                for it in sc.get("items", []):
                    x0, y0, x1, y1 = it["rect"]
                    it["rect"] = [0.06, round(0.12 + y0 * 0.36, 3), 0.94, round(0.12 + y1 * 0.36, 3)]
                if sc.get("lines"):
                    sc["_lines_removed"] = len(sc.pop("lines"))   # rules were placed for the 16:9 text layout

    # ---- 4. text
    scene_of = lambda t: next((s for s in T2["scenes"] if s["t0"] <= t < s["t1"]), T2["scenes"][-1])
    maxw = (F["right"] - F["left"]) * W
    for x in T2["text"]:
        x.pop("panel", None) if x.get("panel") in split_ids else None
    # landscape-ish (5:4): keep positions, fit widths
    if not portrait:
        for x in T2["text"]:
            if x.get("panel"): continue
            px = x["size"] * K; wpx = meas.width(x, px)
            anc = str(x.get("anchor", "ls"))[0]
            left = x["x"] * W - (wpx / 2 if anc == "m" else wpx if anc == "r" else 0)
            if left < F["left"] * W or left + wpx > F["right"] * W:
                if wpx > maxw:
                    x["size"] = round(x["size"] * maxw / wpx, 1); wpx = maxw
                if anc == "l": x["x"] = round(min(max(x["x"], F["left"]), F["right"] - wpx / W), 4)
                elif anc == "m": x["x"] = round(min(max(x["x"], F["left"] + wpx / W / 2), F["right"] - wpx / W / 2), 4)
                else: x["x"] = round(min(max(x["x"], F["left"] + wpx / W), F["right"]), 4)
    else:
        z0, z1 = F["zone"]
        z0_broll = 0.20                # B-roll scenes have no face: their text can start higher
        if chin is not None:          # presenter scenes: start below this presenter's chin (+ a little air)
            z0 = min(max(z0, chin + 0.06), z1 - 0.12)
            print(f"  text zone {z0:.2f}-{z1:.2f} over the presenter (chin at {chin:.2f}), {z0_broll:.2f}-{z1:.2f} over B-roll")
        texts = sorted(T2["text"], key=lambda x: x["t0"])
        placed = []                                   # (t0, t1, top, bottom) of stacked lines
        top_placed = []                               # the same for the small top-left lines
        review = []
        for x in texts:
            sc = scene_of((x["t0"] + x["t1"]) / 2)
            px = x["size"] * K * 1.2                  # a little larger on a phone
            if x.get("behind") and sc["type"] == "presenter":
                x["anchor"], x["x"] = "ms", 0.5
                wpx = meas.width(x, px)
                if wpx > 0.94 * W: px *= 0.94 * W / wpx
                x["size"] = round(px / K, 1)
                continue
            if x.get("font") == "mono" and x["size"] <= 40:   # credits and small info lines: top-left, stacked
                px = max(x["size"], 26) * K * 1.2
                wpx = meas.width(x, px)
                if wpx > maxw: px *= maxw / wpx
                busy = [b for (t0, t1, tp, b) in top_placed if t0 < x["t1"] and x["t0"] < t1]
                base_y = max([0.14 * H] + [b + 1.6 * px for b in busy])
                x.update(x=F["left"], y=round(base_y / H, 4), anchor="ls", size=round(px / K, 1))
                top_placed.append((x["t0"], x["t1"], base_y, base_y))
                continue
            wpx = meas.width(x, px)
            if wpx > maxw: px *= maxw / wpx
            # stack under any line that is on screen at the same time
            busy = [b for (t0, t1, tp, b) in placed if t0 < x["t1"] and x["t0"] < t1]
            zt = z0 if sc["type"] == "presenter" else z0_broll
            if sc["type"] == "collage" and sc.get("items"):   # under the photo cards
                zt = max(zt, max(it["rect"][3] for it in sc["items"]) + 0.04)
            top = max([zt * H] + [b + 0.2 * px for b in busy])
            base_y = top + 0.93 * px
            if base_y + 0.25 * px > z1 * H:           # zone full: shrink to what is left, but not below half size
                room = max(z1 * H - top, 0.5 * px * 1.2)
                px = min(px, room / 1.2); base_y = top + 0.93 * px
            x.update(x=F["left"], y=round(base_y / H, 4), anchor="ls", size=round(px / K, 1))
            if base_y + 0.27 * px > z1 * H + 2:      # no room left in the zone: the agent must re-lay this group
                x["_review"] = "no room in the text zone: overlaps the caption or another line"
                review.append(f"{x['id']} ({x['t0']:.1f}-{x['t1']:.1f} s)")
            if sc["type"] == "presenter" and x.get("color", "ink") == "ink" and not x.get("card"):
                x["card"] = True              # dark type over the presenter's body needs a paper label to be read
            placed.append((x["t0"], x["t1"], top, base_y + 0.27 * px + (0.12 * px if x.get("card") else 0)))
    review = locals().get("review", [])
    if review:
        print(f"  REVIEW {len(review)} text layers that did not fit (marked \"_review\" in the timeline): " + ", ".join(review))
    T2["_format_note"] = (f"Made by make_format.py from {M.name} ({a.aspect}). First pass: check stills of every text "
                          f"layer and scene; face found in {hit * 100:.0f}% of samples.")
    json.dump(T2, open(out / "timeline.json", "w"), indent=1, ensure_ascii=False)

    # ---- 5. style + captions
    st2 = copy.deepcopy(st)
    st2["captions"].update(y=F["cap_y"], size=F["cap_size"])
    json.dump(st2, open(out / "style.json", "w"), indent=1, ensure_ascii=False)
    cc = json.load(open(M / "captions_config.json")) if (M / "captions_config.json").exists() else {}
    cc.update(max_chars=F["cap_chars"], max_words=min(cc.get("max_words", 7), 5))
    json.dump(cc, open(out / "captions_config.json", "w"), indent=1, ensure_ascii=False)
    for f in ("CREDITS.md", "sfx_config.json"):
        if (M / f).exists() and not (out / f).exists(): shutil.copy2(M / f, out / f)
    if (out / "transcript/words.json").exists():
        subprocess.run([sys.executable, str(ENGINE / "build_captions.py"), str(out)], check=True, capture_output=True)
    elif (M / "captions.json").exists():
        shutil.copy2(M / "captions.json", out / "captions.json")
    n_split = len(split_ids)
    print(f"format {a.aspect}: {W}x{H} -> {out}")
    print(f"  reframe: {len(T2['reframe'])} keys; splits -> full-frame cuts: {n_split}; text layers: {len(T2['text'])}")
    print("  next: prep.py, stills of every scene and text layer (fix overlaps by hand in this timeline.json), then")
    print(f"        deliver.py {out} -o {out}/out/edit.mp4 --audio <master mix>   (or no --audio: original sound)")


if __name__ == "__main__":
    main()
