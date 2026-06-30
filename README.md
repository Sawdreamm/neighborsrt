# NeighborSRT

NeighborSRT is a Codex skill for creating professional Thai subtitles for Neighbor Clinic-style videos.

It helps Codex transcribe media with Whisper, generate timed `.srt` captions, post-edit Thai ASR with clinic context, and validate subtitles for CapCut, Premiere, DaVinci Resolve, or YouTube.

## Install

Clone the repo and run the installer for your OS.

### macOS

```bash
git clone https://github.com/Sawdreamm/neighborsrt.git
cd neighborsrt
./install_all_macos.command
```

### Windows

```powershell
git clone https://github.com/Sawdreamm/neighborsrt.git
cd neighborsrt
install_all_windows.bat
```

The installer attempts to install:

- Python 3
- ffmpeg
- `openai-whisper`
- `pythainlp`
- the Codex skill at `~/.codex/skills/neighborsrt` or `%USERPROFILE%\.codex\skills\neighborsrt`
- optionally Whisper `large-v3`

The Whisper model is not committed because it is several GB. The installer can download it, or Whisper will download it on first use.

## Use In Codex

After install, open Codex and ask:

```text
Use $neighborsrt to transcribe this video, polish Thai clinic terms, and create a CapCut-ready SRT.
```

Or:

```text
ใช้ NeighborSRT กับไฟล์นี้ แล้วช่วย post-edit คำไทยสายคลินิกให้ด้วย
```

## Install Manually

macOS/Linux:

```bash
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/neighborsrt
cp -R skill ~/.codex/skills/neighborsrt
python3 -m pip install -U openai-whisper pythainlp
```

Windows PowerShell:

```powershell
mkdir $env:USERPROFILE\.codex\skills -Force
Remove-Item $env:USERPROFILE\.codex\skills\neighborsrt -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item skill $env:USERPROFILE\.codex\skills\neighborsrt -Recurse
py -3 -m pip install -U openai-whisper pythainlp
```

## Repository Layout

```text
neighborsrt/
├── README.md
├── install_all_macos.command
├── install_all_windows.bat
├── requirements.txt
└── skill/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── scripts/
    └── references/
```

## Notes

- This repo intentionally does not include a local web app. It is meant to be used through Codex.
- Raw Whisper output still needs AI or human post-editing for publish-ready Thai clinic subtitles.
- The skill includes Neighbor-specific glossary and ambiguous-term handling for beauty clinic device and treatment names.
