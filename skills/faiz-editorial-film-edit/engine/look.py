"""The editorial look as pixel functions (B&W grade, bloom, torn paper edge, paper, grain fields).
Used by prep.py to bake media and textures that raea then composites. Values come from style.json."""
import numpy as np
import cv2


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def bw_grade(rgb, st, lohi=None):
    """Bright archival B&W: percentile normalise, gamma, soft S-curve, shoulder, black/white points."""
    g = st["bw"]
    L = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    lo, hi = lohi if lohi else (np.percentile(L, 0.5), np.percentile(L, 99.6))
    L = np.clip((L - lo) / max(hi - lo, 1e-3), 0, 1) ** g["gamma"]
    L = L + g["soft_s"] * (L * L * (3 - 2 * L) - L)
    sh = g["shoulder"]
    L = np.where(L > sh, sh + (1 - sh) * np.tanh((L - sh) / (1 - sh)), L)
    L = g["black"] + (g["white"] - g["black"]) * L
    return np.repeat(L.astype(np.float32)[..., None], 3, 2), (lo, hi)


def bloom(img, st):
    """Soft bloom on highlights (inserts only)."""
    b = st["bloom"]
    h, w = img.shape[:2]
    m = smooth(b["threshold"] - b["knee"], b["threshold"] + b["knee"], img.mean(2))
    small = cv2.resize(img * m[..., None], (max(w // 4, 1), max(h // 4, 1)), interpolation=cv2.INTER_AREA)
    acc = 0.6 * cv2.GaussianBlur(small, (0, 0), b["sigmas"][0] / 4) + 0.4 * cv2.GaussianBlur(small, (0, 0), b["sigmas"][1] / 4)
    out = img + b["amount"] * cv2.resize(acc, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.where(out > 0.92, 0.92 + 0.08 * np.tanh((out - 0.92) / 0.08), out).astype(np.float32)


def torn_mask(w, h, seed):
    """Torn paper edge mask (1 inside), w x h."""
    rng = np.random.default_rng(seed)
    m = np.zeros((h, w), np.float32)

    def edge(n):
        x = np.linspace(0, 1, n)
        e = np.zeros(n)
        for f, a in ((3, 2.2), (11, 1.3), (37, 0.8), (97, 0.5)):
            e += a * np.sin(2 * np.pi * (f * x + rng.random()))
        return e

    top, bot, lef, rig = edge(w), edge(w), edge(h), edge(h)
    yy, xx = np.mgrid[0:h, 0:w]
    inside = (yy > 4 + top[xx]) & (yy < h - 5 - bot[xx]) & (xx > 4 + lef[yy]) & (xx < w - 5 - rig[yy])
    m[inside] = 1
    return cv2.GaussianBlur(m, (0, 0), 0.8)


def shadow_from_mask(m, pad=60, dx=12, dy=7, sigma=16, alpha=0.32):
    """Soft drop shadow (alpha only) for a torn card, padded by `pad` px on each side."""
    h, w = m.shape
    big = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    big[pad:pad + h, pad:pad + w] = m
    return np.clip(cv2.GaussianBlur(np.roll(big, (dy, dx), (0, 1)), (0, 0), sigma) * alpha, 0, 1)


def make_paper(w, h, st, seed=7):
    """Warm paper ground with low-frequency mottling and fibres."""
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(st["colors"]["paper"], np.float32)
    low = cv2.GaussianBlur(rng.standard_normal((h // 8, w // 8)).astype(np.float32), (0, 0), 14)
    low = cv2.resize(low / low.std(), (w, h), interpolation=cv2.INTER_CUBIC)
    fib = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), sigmaX=3.0, sigmaY=0.6)
    fib /= fib.std()
    return np.clip(base + (0.006 * low + 0.007 * fib)[..., None], 0, 1)


def grain_field(w, h, st, seed):
    """One grain field as a mid-grey PNG value (0.5 + png_scale * noise) for an overlay blend in raea."""
    g = st["grain"]
    rng = np.random.default_rng(seed)
    k = h / st.get("ref_height", 1440)
    f = cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 0.5 * g["size"] * k)
    f /= f.std()
    return np.clip(0.5 + g.get("png_scale", 0.3) * f, 0, 1)


def to8(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def write_rgb(path, img):
    cv2.imwrite(str(path), cv2.cvtColor(to8(img), cv2.COLOR_RGB2BGR))


def write_alpha(path, alpha, rgb=(1.0, 1.0, 1.0)):
    h, w = alpha.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = (np.array(rgb[::-1]) * 255).astype(np.uint8)
    out[..., 3] = to8(alpha)
    cv2.imwrite(str(path), out)
