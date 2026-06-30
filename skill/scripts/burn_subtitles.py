#!/usr/bin/env python3
"""Burn SRT subtitles into a video with ffmpeg for preview or final export."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_STYLE = "FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=54"


def quote_filter_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", r"\'")
    return f"'{escaped}'"


def default_output_path(video: Path) -> Path:
    return video.with_name(f"{video.stem}.subtitled{video.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Burn SRT subtitles into a video with ffmpeg.")
    parser.add_argument("video", type=Path)
    parser.add_argument("srt", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--style", default=DEFAULT_STYLE, help="force_style string for ffmpeg subtitles filter")
    parser.add_argument("--crf", default="18", help="H.264 quality, lower is better")
    parser.add_argument("--preset", default="medium")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is required")

    output = args.output or default_output_path(args.video)
    with tempfile.TemporaryDirectory() as tmp:
        temp_srt = Path(tmp) / "captions.srt"
        shutil.copyfile(args.srt, temp_srt)
        subtitle_filter = f"subtitles=filename={quote_filter_value(str(temp_srt))}:force_style={quote_filter_value(args.style)}"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(args.video),
            "-vf",
            subtitle_filter,
            "-c:v",
            "libx264",
            "-crf",
            args.crf,
            "-preset",
            args.preset,
            "-c:a",
            "copy",
            str(output),
        ]
        subprocess.run(cmd, check=True)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
