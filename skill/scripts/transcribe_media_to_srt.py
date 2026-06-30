#!/usr/bin/env python3
"""Transcribe audio/video with Whisper and export CapCut-ready SRT."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TRANSCRIPT_SCRIPT = SCRIPT_DIR / "transcript_to_srt.py"

spec = importlib.util.spec_from_file_location("transcript_to_srt", TRANSCRIPT_SCRIPT)
if spec is None or spec.loader is None:
    raise SystemExit(f"Cannot load {TRANSCRIPT_SCRIPT}")
transcript_to_srt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = transcript_to_srt
spec.loader.exec_module(transcript_to_srt)


def default_output_path(path: Path, task: str) -> Path:
    suffix = ".en.srt" if task == "translate" else ".srt"
    return path.with_name(f"{path.stem}{suffix}")


def captions_from_segments(segments: list[dict], max_chars: int, max_lines: int):
    cues = []
    for segment in segments:
        text = transcript_to_srt.clean_text(segment.get("text", ""))
        if not text:
            continue
        cues.extend(split_segment_into_cues(segment, text, max_chars, max_lines))
    return cues


def split_segment_into_cues(segment: dict, text: str, max_chars: int, max_lines: int):
    start = float(segment["start"])
    end = float(segment["end"])
    duration = max(0.1, end - start)
    lines = transcript_to_srt.wrap_line(text, max_chars=max_chars, max_lines=99)
    if not lines:
        return []

    groups = [lines[i : i + max_lines] for i in range(0, len(lines), max_lines)]
    if len(groups) == 1:
        return [(start, end, groups[0])]

    weights = [max(1, sum(len(line) for line in group)) for group in groups]
    total_weight = sum(weights)
    cues = []
    current = start
    for group, weight in zip(groups, weights):
        cue_duration = duration * weight / total_weight
        cue_end = min(end, current + cue_duration)
        cues.append((current, cue_end, group))
        current = cue_end
    cues[-1] = (cues[-1][0], end, cues[-1][2])
    return cues


def format_segment_srt(cues) -> str:
    blocks = []
    for index, (start, end, lines) in enumerate(cues, start=1):
        if end <= start:
            end = start + 0.75
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{transcript_to_srt.format_timestamp(start)} --> {transcript_to_srt.format_timestamp(end)}",
                    *lines,
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def write_transcript(path: Path, segments: list[dict]) -> None:
    text = "\n".join(transcript_to_srt.clean_text(segment.get("text", "")) for segment in segments)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe media with Whisper and write SRT.")
    parser.add_argument("input", type=Path, help="Audio/video file")
    parser.add_argument("-o", "--output", type=Path, help="Output .srt file")
    parser.add_argument("--model", default="small", help="Whisper model: tiny, base, small, medium, large")
    parser.add_argument("--language", help="Language code such as th or en. Omit for auto-detect.")
    parser.add_argument("--task", choices=["transcribe", "translate"], default="transcribe")
    parser.add_argument("--max-chars", type=int, default=34, help="Target max characters per subtitle line")
    parser.add_argument("--max-lines", type=int, default=2, help="Maximum lines per cue")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--prompt", help="Optional Whisper initial prompt for names, terms, or style")
    parser.add_argument("--transcript-out", type=Path, help="Also write plain transcript text")
    parser.add_argument("--device", help="Whisper device override, for example cpu")
    args = parser.parse_args()

    try:
        import whisper
    except ImportError as exc:
        raise SystemExit("Install openai-whisper first: pip install -U openai-whisper") from exc

    model_kwargs = {}
    if args.device:
        model_kwargs["device"] = args.device

    model = whisper.load_model(args.model, **model_kwargs)
    result = model.transcribe(
        str(args.input),
        language=args.language,
        task=args.task,
        temperature=args.temperature,
        initial_prompt=args.prompt,
        fp16=False,
    )

    segments = result.get("segments", [])
    if not segments:
        raise SystemExit("Whisper returned no segments")

    output = args.output or default_output_path(args.input, args.task)
    cues = captions_from_segments(segments, args.max_chars, args.max_lines)
    output.write_text(format_segment_srt(cues), encoding="utf-8")

    if args.transcript_out:
        write_transcript(args.transcript_out, segments)

    language = result.get("language", "unknown")
    print(f"Wrote {output} ({len(cues)} cues, language={language}, model={args.model})")


if __name__ == "__main__":
    main()
