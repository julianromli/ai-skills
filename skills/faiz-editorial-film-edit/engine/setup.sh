#!/bin/sh
# First-time setup for faiz-editorial-film-edit. Asks before each install; skips what is already there.
#   sh setup.sh            interactive
#   sh setup.sh --yes      no questions (only when the user has already agreed to all of it)
# Installs into ~/.editorial-raea (venv, models) and ~/.raea (raea). Nothing else on the system changes,
# except that the raea installer adds its own raea and raea-bevy skills to ~/.claude/skills.
set -eu
CFG="$HOME/.editorial-raea"
RAEA_PIN="0.1.0-canary.3"          # the raea version this skill was tested with
YES="${1:-}"
ask() { [ "$YES" = "--yes" ] && return 0; printf '%s [y/N] ' "$1"; read -r a; [ "$a" = "y" ] || [ "$a" = "Y" ]; }
say() { printf '%s\n' "setup: $*"; }
mkdir -p "$CFG"

command -v ffmpeg >/dev/null || {
  if command -v brew >/dev/null && ask "ffmpeg is missing. Install it with Homebrew (brew install ffmpeg)?"; then brew install ffmpeg
  else say "install ffmpeg yourself, then run this again"; exit 1; fi; }

# rembg needs Python 3.10+; macOS's own python3 is 3.9
PY=""
for v in python3.13 python3.12 python3.11 python3.10 python3; do
  c=$(command -v "$v" 2>/dev/null) || continue
  "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null && { PY="$c"; break; }
done
if [ -z "$PY" ]; then
  say "Python 3.10 or newer is needed (macOS's python3 is 3.9). Install one, e.g.:  brew install python@3.12  — then run this again"
  exit 1
fi
if [ ! -x "$CFG/venv/bin/python" ]; then
  if ask "Create a Python environment in $CFG/venv and install numpy, opencv, pillow, rembg, onnxruntime (~400 MB)?"; then
    "$PY" -m venv "$CFG/venv"
    "$CFG/venv/bin/pip" install -q --upgrade pip
    "$CFG/venv/bin/pip" install -q numpy opencv-python-headless pillow rembg onnxruntime
    say "python environment ready"
  fi
fi

if [ ! -x "$HOME/.local/bin/raea" ]; then
  if ask "Install raea $RAEA_PIN (GPU renderer, ~150 MB) from raea.io? It also adds raea's own skills to ~/.claude/skills."; then
    tmp=$(mktemp -d); curl -fsSL https://raea.io/install -o "$tmp/install.sh"
    say "installer saved to $tmp/install.sh (it verifies the download's checksum)"
    RAEA_VERSION="$RAEA_PIN" sh "$tmp/install.sh"
  fi
fi

if [ -z "$(find "$CFG/models" -name 'birefnet-portrait*.onnx' 2>/dev/null | head -n 1)" ] && [ -x "$CFG/venv/bin/python" ]; then
  if ask "Download the person-mask model BiRefNet-portrait (~1 GB, only for text behind the presenter)?"; then
    mkdir -p "$CFG/models"
    U2NET_HOME="$CFG/models" "$CFG/venv/bin/python" -c "from rembg import new_session; new_session('birefnet-portrait')"
    say "model ready"
  fi
fi

if [ ! -f "$CFG/assemblyai.key" ]; then
  say "optional: for transcription, save an AssemblyAI key:  printf %s YOUR_KEY > $CFG/assemblyai.key && chmod 600 $CFG/assemblyai.key"
fi
"${CFG}/venv/bin/python" "$(dirname "$0")/check_env.py" || true
