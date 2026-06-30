# NeighborSRT

NeighborSRT is a local web app and Codex skill for turning Thai clinic videos into CapCut-ready `.srt` subtitles.

It is tuned for Neighbor Clinic-style content: facial design, skin work, Ultraformer, Botox, Bone Loss, fillers, lasers, and Thai ASR post-editing.

## Quick Start

Clone the repo, run the installer, then start the local web app.

### macOS

```bash
git clone https://github.com/Sawdreamm/neighborsrt.git
cd neighborsrt
./install_all_macos.command
./start.command
```

### Windows

```powershell
git clone https://github.com/Sawdreamm/neighborsrt.git
cd neighborsrt
install_all_windows.bat
start_windows.bat
```

Open:

```text
http://127.0.0.1:8765
```

Then drag a video or audio file into the browser page and download the generated `.srt`.

## What The Installer Does

The full installer attempts to install:

- Python 3
- ffmpeg
- `openai-whisper`
- `pythainlp`
- the included Codex skill at `~/.codex/skills/neighborsrt` or `%USERPROFILE%\.codex\skills\neighborsrt`
- optionally Whisper `large-v3`

The Whisper model is not committed to GitHub because it is several GB. The installer can download it on first setup, or Whisper will download it on first use.

## Use With Codex

After cloning, you can ask Codex:

```text
Read this repository and install the NeighborSRT skill and all local-web dependencies on this machine.
```

Or install manually:

```bash
mkdir -p ~/.codex/skills
cp -R skill ~/.codex/skills/neighborsrt
```

Windows:

```powershell
install_skill_windows.bat
```

## Main Files

```text
neighborsrt/
├── index.html
├── app/server.py
├── install_all_macos.command
├── install_all_windows.bat
├── start.command
├── start_windows.bat
└── skill/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── scripts/
    └── references/
```

## Notes

- The local web UI runs on `127.0.0.1:8765`.
- Raw Whisper output still needs AI or human post-editing for publish-ready Thai clinic subtitles.
- The skill includes Neighbor-specific glossary and ambiguous-term handling, especially for devices and brand names.
- Hard-sub burning depends on ffmpeg build support for subtitle filters. Soft subtitle export is safer across machines.
