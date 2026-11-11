"""First-time check: is this machine ready for an editorial edit? Prints OK / MISSING with the fix for each item.

    python3 check_env.py [--venv PATH] [--models PATH]

Read-only: it installs nothing. setup.sh does the installs after the user agrees.
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

HOME = Path.home()
CFG = HOME / ".editorial-raea"            # venv, models and API key live here, shared by all projects
FONTS = {
    "Helvetica Neue": "/System/Library/Fonts/HelveticaNeue.ttc",
    "Didot": "/System/Library/Fonts/Supplemental/Didot.ttc",
    "Menlo": "/System/Library/Fonts/Menlo.ttc",
}
PY_PKGS = ["numpy", "cv2", "PIL", "rembg", "onnxruntime"]


def row(ok, name, detail="", fix=""):
    print(f"{'OK     ' if ok else 'MISSING'}  {name}{('  -  ' + detail) if detail else ''}")
    if not ok and fix:
        print(f"         fix: {fix}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venv", default=str(CFG / "venv"))
    ap.add_argument("--models", default=str(CFG / "models"))
    a = ap.parse_args()
    venv_py = Path(a.venv) / "bin/python"
    need = []

    print("== machine")
    mac = sys.platform == "darwin" and os.uname().machine == "arm64"
    row(mac, "macOS on Apple Silicon", os.uname().machine,
        "raea renders on Apple Silicon macOS (or Linux x86_64); fonts below assume macOS")
    free = shutil.disk_usage(HOME).free / 1e9
    row(free > 20, "free disk", f"{free:.0f} GB", "keep 20 GB free: masters at 1440p are ~1 GB per minute") or need.append("disk")

    print("== tools")
    ff = shutil.which("ffmpeg")
    if row(bool(ff), "ffmpeg", ff or "", "brew install ffmpeg"):
        enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        row("libx264" in enc, "ffmpeg libx264", "", "brew reinstall ffmpeg (needs libx264)") or need.append("libx264")
    else:
        need.append("ffmpeg")
    row(bool(shutil.which("ffprobe")), "ffprobe", "", "comes with ffmpeg") or need.append("ffprobe")
    raea = HOME / ".local/bin/raea"
    if row(raea.exists(), "raea", "", "setup.sh installs it (curl https://raea.io/install, checksum verified)"):
        v = subprocess.run([str(raea), "--version"], capture_output=True, text=True).stdout.strip()
        print(f"         version {v} (canary: a newer one can break; setup.sh pins the tested version)")
    else:
        need.append("raea")
    row(bool(shutil.which("python3")), "python3", shutil.which("python3") or "", "brew install python@3.11") or need.append("python3")

    print("== python environment")
    if row(venv_py.exists(), "venv", str(a.venv), "setup.sh creates it"):
        r = subprocess.run([str(venv_py), "-c", "import importlib,sys\n"
                            f"bad=[m for m in {PY_PKGS!r} if importlib.util.find_spec(m) is None]\nprint(','.join(bad))"],
                           capture_output=True, text=True)
        bad = r.stdout.strip()
        row(not bad, "python packages", "numpy opencv pillow rembg onnxruntime" if not bad else f"missing: {bad}",
            "setup.sh installs them") or need.append("packages")
    else:
        need.append("venv")
    found = list(Path(a.models).rglob("birefnet-portrait*.onnx")) if Path(a.models).exists() else []
    model = found[0] if found else Path(a.models) / "birefnet-portrait.onnx"
    row(bool(found), "person-mask model (BiRefNet-portrait, ~1 GB)", str(model),
        "setup.sh downloads it on first use; only needed for text behind the presenter") or need.append("model")

    print("== fonts (the three type roles)")
    for name, p in FONTS.items():
        row(Path(p).exists(), name, p, "macOS system font; on another OS set css_fonts and fonts in style.json") or need.append(name)

    print("== services (optional)")
    key = CFG / "assemblyai.key"
    row(key.exists() or bool(os.environ.get("ASSEMBLYAI_API_KEY")), "AssemblyAI API key", str(key),
        f"create a key at assemblyai.com, then save it: echo KEY > {key}; chmod 600 {key}  (or use a transcript you have)")
    fk = HOME / ".editorial-raea/fal.key"
    row(fk.exists() or bool(os.environ.get("FAL_KEY")), "fal API key (only for cloud masks)", str(fk),
        "optional: see first-time-setup.md Step 2b; local masks need no key")
    print("         Higgsfield (generated B-roll) is optional: connect it in Claude only if you want generated shots.")

    print()
    print("READY" if not need else f"NOT READY: {', '.join(need)}  ->  run setup.sh (asks before each install)")
    sys.exit(0 if not need else 1)


if __name__ == "__main__":
    main()
