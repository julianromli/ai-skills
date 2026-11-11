"""Start a new editorial project from a source video.

    python init_project.py PROJECT_DIR --source /path/to/footage.mp4

Creates the folders, links the footage, reads its size/fps/frame count, and writes a starting timeline.json
(one presenter scene over the whole video), style.json (the skill's look), captions_config.json, sfx_config.json
and CREDITS.md. Existing files are never overwritten.
"""
import argparse, json, shutil, subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("project"); ap.add_argument("--source", required=True)
a = ap.parse_args()
P = Path(a.project).resolve(); src = Path(a.source).resolve()
for d in ("footage", "assets/archive", "assets/generated", "assets/brand", "assets/sfx/source", "transcript", "cache/masks", "out", "stills"):
    (P / d).mkdir(parents=True, exist_ok=True)
link = P / "footage" / src.name
if not link.exists():
    link.symlink_to(src)

d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
    "stream=width,height,r_frame_rate,nb_read_packets,codec_name,pix_fmt,color_transfer:format=duration",
    "-of", "json", str(src)], capture_output=True, text=True, check=True).stdout)
s = d["streams"][0]; n, dd = s["r_frame_rate"].split("/"); fps = round(float(n) / float(dd), 3)
dur = float(d["format"]["duration"]); frames = int(s["nb_read_packets"])
au = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name,sample_rate,channels",
                     "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip()


def write(name, obj):
    f = P / name
    if f.exists():
        print("kept", name); return
    (json.dump(obj, open(f, "w"), indent=1, ensure_ascii=False) if not isinstance(obj, str) else f.write_text(obj))
    print("wrote", name)


write("timeline.json", {
    "source": {"path": f"footage/{src.name}", "width": int(s["width"]), "height": int(s["height"]), "fps": fps,
               "frames": frames, "presenter_center_x": 0.5, "baked_cuts": []},
    "output": {"path": "out/edit_v1.mp4"},
    "captions": "burn",
    "media": {},
    "scenes": [{"id": "s01", "type": "presenter", "t0": 0.0, "t1": round(frames / fps, 3)}],
    "text": []})
if not (P / "style.json").exists():
    shutil.copy2(SKILL / "templates/style.json", P / "style.json"); print("wrote style.json")
write("captions_config.json", {"fix": {}, "merge": [], "accent": [], "suppress": []})
write("sfx_config.json", {"reels": {}, "cuts": {}, "titles": {}, "level": {}, "variants": {}})
write("CREDITS.md", "# Sources and credits\n\n## Source footage\n- footage/" + src.name +
      " (the user's recording)\n\n## B-roll\n| File | Source | Licence / credit |\n|---|---|---|\n\n## Sound effects\n\n## Fonts\n")
print(f"\nsource: {s['width']}x{s['height']} {fps} fps, {frames} frames, {dur:.2f} s, {s['codec_name']} {s.get('pix_fmt')}"
      f" {s.get('color_transfer', '')}; audio: {au or 'none'}")
print("next: set presenter_center_x and baked_cuts in timeline.json (look at frames), then transcribe.py")
