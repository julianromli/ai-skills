"""Word-level transcript with AssemblyAI (pre-recorded API) -> PROJECT/transcript/words.json.

    python transcribe.py PROJECT [--language id] [--keyterms "DevFest,GDG Bandung"]

Key: ASSEMBLYAI_API_KEY, or ~/.editorial-raea/assemblyai.key. The key is never printed or written to the project;
the raw response is saved without the upload URL. Models: ["universal-3-5-pro", "universal-2"] (3.5 Pro covers 18
languages and falls back to Universal-2 for the rest, e.g. Indonesian).
"""
import argparse, json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

API = "https://api.assemblyai.com/v2"


def key():
    k = os.environ.get("ASSEMBLYAI_API_KEY")
    f = Path.home() / ".editorial-raea/assemblyai.key"
    if not k and f.exists():
        k = f.read_text().strip()
    if not k:
        sys.exit("no AssemblyAI key: set ASSEMBLYAI_API_KEY or save it to ~/.editorial-raea/assemblyai.key")
    return k


def call(method, url, k, body=None, raw=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(url, data=data, method=method, headers={"authorization": k,
        "content-type": "application/octet-stream" if raw is not None else "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project"); ap.add_argument("--language", default=None, help="ISO code, e.g. id, en; omit to detect")
    ap.add_argument("--keyterms", default="", help="comma-separated names and terms to bias toward")
    a = ap.parse_args()
    P = Path(a.project).resolve()
    T = json.load(open(P / "timeline.json"))
    src = (P / T["source"]["path"]).resolve()
    k = key()
    with tempfile.TemporaryDirectory() as td:
        audio = Path(td) / "audio.m4a"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-c:a", "aac", "-b:a", "128k", str(audio)], check=True)
        up = call("POST", f"{API}/upload", k, raw=audio.read_bytes())["upload_url"]
    body = {"audio_url": up, "speech_models": ["universal-3-5-pro", "universal-2"], "punctuate": True, "format_text": True}
    if a.language: body["language_code"] = a.language
    else: body["language_detection"] = True
    terms = [t.strip() for t in a.keyterms.split(",") if t.strip()]
    if terms: body["keyterms_prompt"] = terms
    job = call("POST", f"{API}/transcript", k, body)
    print("transcribing", job["id"], flush=True)
    while job["status"] not in ("completed", "error"):
        time.sleep(4); job = call("GET", f"{API}/transcript/{job['id']}", k)
    if job["status"] == "error":
        sys.exit("AssemblyAI error: " + str(job.get("error")))
    out = P / "transcript"; out.mkdir(exist_ok=True)
    job.pop("audio_url", None)
    json.dump(job, open(out / "assemblyai_raw.json", "w"), ensure_ascii=False, indent=1)
    words = [{"w": w["text"], "t0": w["start"] / 1000, "t1": w["end"] / 1000, "conf": round(w.get("confidence", 1), 3)}
             for w in job["words"]]
    json.dump({"source": f"AssemblyAI {job.get('speech_model_used', '?')}, language {job.get('language_code', '?')}",
               "transcript_id": job["id"], "words": words}, open(out / "words.json", "w"), ensure_ascii=False, indent=1)
    low = [w for w in words if w["conf"] < 0.6]
    print(f"{len(words)} words -> transcript/words.json; {len(low)} low-confidence words to review with the user:")
    print(" ".join(f"{w['w']}@{w['t0']:.1f}" for w in low[:60]))


if __name__ == "__main__":
    main()
