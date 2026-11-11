"""Person masks (BiRefNet-portrait) for frames where a text layer has "behind": true in a presenter scene.

    python make_masks.py PROJECT [--engine local|fal] [--crop 0.18 0.82] [--workers 6]

Engines (ask the user which one; see references/first-time-setup.md):
  local  rembg on this Mac's CPU. Free, private, ~15-20 s per modelled frame on an M5 (every 2nd frame is modelled,
         so ~8 s of behind-text at 25 fps ~ 30 min). Needs the ~1 GB model.
  fal    fal.ai "fal-ai/birefnet/v2", model "Portrait", 2048x2048, mask only. $0.000575 per compute second
         (fal's price on 2026-11-09; a typical edit of ~250 frames is a few cents). Needs a fal API key in
         FAL_KEY or ~/.editorial-raea/fal.key. Frames (presenter crop, JPEG) are uploaded to fal. Frames that
         fail on fal are modelled locally when rembg and the model are installed.

Every 2nd frame is modelled; frames between are the mean of their neighbours. Masks are tied to the source's
exact frame index and full-frame geometry. Output: PROJECT/cache/masks/NNNNN.png. Existing files are kept, so
run it again after adding a behind-text layer.
"""
import argparse, base64, io, json, os, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np, cv2
from PIL import Image

os.environ.setdefault("U2NET_HOME", str(Path.home() / ".editorial-raea/models"))
FAL_URL = "https://fal.run/fal-ai/birefnet/v2"

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--engine", choices=["local", "fal"], default="local")
ap.add_argument("--crop", nargs=2, type=float, default=[0.18, 0.82], help="x range around the presenter, fractions of the width")
ap.add_argument("--workers", type=int, default=6, help="parallel fal requests")
a = ap.parse_args()
P = Path(a.project).resolve()
TL = json.load(open(P / "timeline.json"))
S = TL["source"]; W, H, FPS = S["width"], S["height"], S["fps"]
src = (P / S["path"]).resolve()
out = P / "cache/masks"; out.mkdir(parents=True, exist_ok=True)
X0, X1 = int(a.crop[0] * W), int(a.crop[1] * W)

pres = [s for s in TL["scenes"] if s["type"] == "presenter"]
allneed = sorted({n for te in TL["text"] if te.get("behind")
                  for n in range(int(np.floor(te["t0"] * FPS)), int(np.ceil(te["t1"] * FPS)) + 1)
                  if any(s["t0"] <= n / FPS < s["t1"] for s in pres)})
ends = {n for i, n in enumerate(allneed) if i == 0 or allneed[i - 1] != n - 1 or i == len(allneed) - 1 or allneed[i + 1] != n + 1}
need = [n for n in allneed if (n % 2 == 0 or n in ends) and not (out / f"{n:05d}.png").exists()]
print(f"{len(need)} masks to model ({a.engine}), {len(allneed)} frames in all", flush=True)


def frames(nums):
    """Yield (n, presenter crop RGB) for the frame numbers, decoding each consecutive run once."""
    runs, cur = [], []
    for n in nums:
        if cur and n != cur[-1] + 1: runs.append(cur); cur = []
        cur.append(n)
    if cur: runs.append(cur)
    for run in runs:
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{run[0] / FPS:.6f}", "-i", str(src), "-frames:v", str(len(run)),
                              "-vf", "scale=in_color_matrix=bt709:out_color_matrix=bt709,format=rgb24", "-f", "rawvideo", "-"],
                             stdout=subprocess.PIPE)
        for n in run:
            fr = np.frombuffer(p.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
            yield n, np.ascontiguousarray(fr[:, X0:X1])
        p.wait()


def save(n, m):
    full = np.zeros((H, W), np.uint8)
    full[:, X0:X1] = cv2.resize(m, (X1 - X0, H), interpolation=cv2.INTER_LINEAR) if m.shape != (H, X1 - X0) else m
    cv2.imwrite(str(out / f"{n:05d}.png"), full)


def run_local(nums):
    if not nums: return
    from rembg import new_session, remove
    sess = new_session("birefnet-portrait", providers=["CPUExecutionProvider"])   # CoreML hangs
    for n, crop in frames(nums):
        h, w = crop.shape[:2]
        s = min(1.0, 1440 / h)          # larger frames only cost decode/resize time, not mask quality
        im = Image.fromarray(crop if s == 1.0 else cv2.resize(crop, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA))
        save(n, np.asarray(remove(im, session=sess, only_mask=True), np.uint8))
        print("mask", n, flush=True)


def fal_key():
    k = os.environ.get("FAL_KEY")
    f = Path.home() / ".editorial-raea/fal.key"
    if not k and f.exists(): k = f.read_text().strip()
    if not k: sys.exit("no fal key: set FAL_KEY or save it to ~/.editorial-raea/fal.key (see first-time-setup.md)")
    return k


def fal_one(key, n, crop):
    buf = io.BytesIO(); Image.fromarray(crop).save(buf, "JPEG", quality=93)
    body = {"image_url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
            "model": "Portrait", "operating_resolution": "2048x2048", "mask_only": True,
            "output_format": "png", "sync_mode": True}
    req = urllib.request.Request(FAL_URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Key {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        url = json.loads(r.read())["image"]["url"]
    data = base64.b64decode(url.split(",", 1)[1]) if url.startswith("data:") else urllib.request.urlopen(url, timeout=120).read()
    im = Image.open(io.BytesIO(data))
    m = np.asarray(im.getchannel("A") if im.mode in ("RGBA", "LA") else im.convert("L"), np.uint8)
    save(n, m)
    return n


def run_fal(nums):
    key = fal_key(); failed = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(fal_one, key, n, crop): n for n, crop in frames(nums)}
        for f, n in futs.items():
            try:
                f.result(); print("mask", n, "(fal)", flush=True)
            except Exception as e:
                failed.append(n); print("fal failed", n, type(e).__name__, str(e)[:120], flush=True)
    if failed:
        try:
            import rembg  # noqa: F401
            print(f"{len(failed)} frames failed on fal: modelling them locally", flush=True)
            run_local(failed)
        except ImportError:
            sys.exit(f"{len(failed)} frames failed on fal and rembg is not installed: run again later")


(run_fal if a.engine == "fal" else run_local)(need)
for n in allneed:
    f = out / f"{n:05d}.png"
    if f.exists(): continue
    x, y = cv2.imread(str(out / f"{n - 1:05d}.png"), 0), cv2.imread(str(out / f"{n + 1:05d}.png"), 0)
    m = ((x.astype(np.uint16) + y) // 2).astype(np.uint8) if x is not None and y is not None else (x if x is not None else y)
    if m is not None: cv2.imwrite(str(f), m)
print("masks ready:", out)
