NeighborSRT Local Web

One-command install:
  macOS:   open install_all_macos.command
  Windows: double-click install_all_windows.bat

The full installer installs ffmpeg, Python packages, the Codex skill, and can optionally download Whisper large-v3.

Open start.command on macOS.
Open start_windows.bat on Windows.

Then drag a video/audio file into the browser page and click "ถอดเสียงเป็น SRT".

Requirements:
- python3
- ffmpeg
- openai-whisper
- pythainlp

Install:
  brew install ffmpeg
  python3 -m pip install -U openai-whisper pythainlp

Windows install:
  winget install Python.Python.3.12
  winget install Gyan.FFmpeg
  py -3 -m pip install -U openai-whisper pythainlp

Outputs are saved in:
  outputs/
