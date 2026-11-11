"""Bake everything raea composites: graded media, paper, grain fields, torn masks and shadows.

    python prep.py PROJECT            # PROJECT holds timeline.json, style.json, captions.json
    python prep.py PROJECT --force    # bake every file again (after a look change in style.json)

Writes PROJECT/raea/ :  edit.tsx (the engine, copied from the skill), manifest.json, media/ .
Media that are already baked and unchanged are skipped, so run it after every timeline edit.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import look as L

ENGINE = Path(__file__).resolve().parent
MAX_SIDE = 4096          # keeps GPU textures in range; larger photos gain nothing at 1440p
N_CARDS = 6              # generic torn masks for text cards (stretched to each card)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,r_frame_rate,nb_read_packets",
                          "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out); s = d["streams"][0]
    a, b = s["r_frame_rate"].split("/")
    return dict(w=int(s["width"]), h=int(s["height"]), fps=float(a) / float(b),
                frames=int(s.get("nb_read_packets", 0)), dur=float(d["format"]["duration"]))


def sig(*parts):
    h = hashlib.sha1()
    for p in parts:
        h.update(json.dumps(p, sort_keys=True).encode() if not isinstance(p, Path) else
                 f"{p}:{p.stat().st_mtime_ns}:{p.stat().st_size}".encode())
    return h.hexdigest()[:16]


def bake_image(src, dst, m, st):
    im = np.asarray(Image.open(src).convert("RGB"), np.float32) / 255
    if "trim" in m:  # [left, top, right, bottom] fractions: scan borders, printed captions
        l, t, r, b = m["trim"]; h, w = im.shape[:2]
        im = im[int(t * h):h - int(b * h), int(l * w):w - int(r * w)]
    h, w = im.shape[:2]
    if max(h, w) > MAX_SIDE:
        s = MAX_SIDE / max(h, w)
        im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    if m.get("look", "bw") != "color":
        im = L.bw_grade(im, st)[0]
    im = L.bloom(im, st)
    L.write_rgb(dst, im)
    return dict(w=im.shape[1], h=im.shape[0])


def bake_video(src, dst, m, st):
    info = probe(src)
    w, h = info["w"], info["h"]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-an", "-vf", "format=rgb24",
                            "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                            "-r", f"{info['fps']}", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)], stdin=subprocess.PIPE)
    lohi = None
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
        if m.get("look", "bw") != "color":
            f, got = L.bw_grade(f, st, lohi)
            lohi = lohi or got            # one exposure for the whole clip: no flicker
        enc.stdin.write(L.to8(L.bloom(f, st)).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    return dict(w=w, h=h, fps=info["fps"], dur=info["dur"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    P = Path(a.project).resolve()
    T = json.load(open(P / "timeline.json"))
    st = json.load(open(P / "style.json"))
    out = P / "raea"; media = out / "media"; media.mkdir(parents=True, exist_ok=True)
    old = json.load(open(out / "manifest.json")) if (out / "manifest.json").exists() and not a.force else {}
    out_ = T.get("output", {})
    W, H = out_.get("width", T["source"]["width"]), out_.get("height", T["source"]["height"])   # canvas size

    shutil.copy2(ENGINE / "edit.tsx", out / "edit.tsx")
    if not (P / "captions.json").exists():              # edit.tsx imports it, even with "captions": "none"
        json.dump({"chunks": []}, open(P / "captions.json", "w"))
    for name in ("timeline.json", "style.json", "captions.json"):   # raea bundles imports from its own folder
        if (P / name).exists():
            shutil.copy2(P / name, out / name)

    src = (P / T["source"]["path"]).resolve()
    link = media / "source.mp4"
    if link.is_symlink() or link.exists(): link.unlink()
    link.symlink_to(src)

    man = dict(media_dir=str(media), masks_dir=str((P / "cache/masks").resolve()), media={}, collage={},
               cards=N_CARDS, grain=st["grain"]["bank"])
    for mid, m in T["media"].items():
        srcp = (P / m["path"]).resolve()
        if not srcp.exists():
            sys.exit(f"missing media '{mid}': {srcp}")
        ext = ".mp4" if m["kind"] == "video" else ".png"
        dst = media / f"{mid}{ext}"
        key = sig(srcp, m, st["bw"], st["bloom"])
        prev = old.get("media", {}).get(mid)
        if prev and prev.get("sig") == key and dst.exists():
            man["media"][mid] = prev; continue
        print("bake", mid, flush=True)
        info = bake_video(srcp, dst, m, st) if m["kind"] == "video" else bake_image(srcp, dst, m, st)
        man["media"][mid] = dict(file=dst.name, kind=m["kind"], sig=key, **info)

    if a.force or not (media / "paper.png").exists():
        L.write_rgb(media / "paper.png", L.make_paper(W, H, st))
    for k in range(st["grain"]["bank"]):
        f = media / f"grain_{k}.png"
        if a.force or not f.exists():
            g = L.grain_field(W, H, st, 1234 + k)
            L.write_rgb(f, np.repeat(g[..., None], 3, 2))
    for k in range(N_CARDS):
        f, fs = media / f"card_{k}.png", media / f"card_{k}_sh.png"
        if a.force or not f.exists() or not fs.exists():
            m = L.torn_mask(1600, 400, 900 + k)
            L.write_alpha(f, m)
            L.write_alpha(fs, L.shadow_from_mask(m, pad=40, dx=0, dy=0, sigma=7, alpha=0.28), rgb=(0, 0, 0))

    for s in T["scenes"]:
        if s["type"] != "collage":
            continue
        items = []
        for k, it in enumerate(s["items"]):
            x0, y0, x1, y1 = it["rect"]
            rw, rh = int((x1 - x0) * W), int((y1 - y0) * H)
            seed = int(hashlib.md5(f"{s['id']}{k}".encode()).hexdigest()[:6], 16)
            mf, sf = media / f"torn_{s['id']}_{k}.png", media / f"shadow_{s['id']}_{k}.png"
            if a.force or not mf.exists() or not sf.exists() or Image.open(mf).size != (rw, rh):
                m = L.torn_mask(rw, rh, seed)
                L.write_alpha(mf, m)
                L.write_alpha(sf, L.shadow_from_mask(m), rgb=(0, 0, 0))
            items.append(dict(mask=mf.name, shadow=sf.name, w=rw, h=rh, pad=60))
        man["collage"][s["id"]] = items

    # frames that have a person mask (text behind the presenter), as [first, last] runs
    nums = sorted(int(p.stem) for p in (P / "cache/masks").glob("*.png")) if (P / "cache/masks").exists() else []
    runs = []
    for k in nums:
        if runs and k == runs[-1][1] + 1: runs[-1][1] = k
        else: runs.append([k, k])
    man["mask_frames"] = runs
    # text behind the presenter needs a mask on every frame it shows over a presenter scene
    fps = T["source"]["fps"]; have = set(nums)
    pres = [s for s in T["scenes"] if s["type"] == "presenter"]
    for te in T["text"]:
        if not te.get("behind"): continue
        want = [n for n in range(int(np.floor(te["t0"] * fps)), int(np.ceil(te["t1"] * fps)))
                if any(s["t0"] <= n / fps < s["t1"] for s in pres)]
        miss = [n for n in want if n not in have]
        if miss:
            print(f"WARNING: '{te['id']}' is behind the presenter but {len(miss)} of {len(want)} frames have no mask "
                  f"(first {miss[0]}): it draws OVER the presenter there. Run make_masks.py, then prep.py again.")

    json.dump(man, open(out / "manifest.json", "w"), indent=1)
    print("ready:", out / "edit.tsx")


if __name__ == "__main__":
    main()
