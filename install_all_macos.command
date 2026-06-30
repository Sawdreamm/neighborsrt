#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "NeighborSRT full installer for macOS"
echo "===================================="

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Installing Python..."
  brew install python
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Installing ffmpeg..."
  brew install ffmpeg
fi

echo "Installing Python packages..."
python3 -m pip install -U openai-whisper pythainlp

echo "Installing Codex skill..."
DEST="${CODEX_HOME:-$HOME/.codex}/skills/neighborsrt"
mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R skill "$DEST"

echo "Preparing Whisper model cache..."
mkdir -p "$HOME/.cache/whisper"

read -r -p "Download Whisper large-v3 now? This is about 3GB. [y/N] " answer
case "$answer" in
  [yY][eE][sS]|[yY])
    python3 - <<'PY'
import whisper
print("Downloading/loading large-v3. This may take a while...")
whisper.load_model("large-v3")
print("large-v3 is ready.")
PY
    ;;
  *)
    echo "Skipped model download. It will download on first use."
    ;;
esac

echo ""
echo "Done."
echo "Start local web with:"
echo "  ./start.command"
