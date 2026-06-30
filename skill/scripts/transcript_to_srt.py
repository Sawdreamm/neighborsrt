#!/usr/bin/env python3
"""Generate SRT subtitles from transcript text and total clip duration."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from pythainlp.tokenize import word_tokenize as thai_word_tokenize
except ImportError:
    thai_word_tokenize = None


SPACE_RE = re.compile(r"[ \t\u00a0\u200b\u200c\u200d]+")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")


@dataclass
class Caption:
    lines: list[str]
    weight: int


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp874"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    value = value.replace("\\N", " ")
    value = SPACE_RE.sub(" ", value)
    value = re.sub(r"\s+([,.;:!?%])", r"\1", value)
    value = re.sub(r"([,.;:!?])([^\s])", r"\1 \2", value)
    return value.strip()


def parse_duration(value: str) -> float:
    value = value.strip()
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)

    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError("Duration must be seconds, MM:SS, or HH:MM:SS")


def split_segments(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    raw_segments = [segment.strip() for segment in SENTENCE_SPLIT_RE.split(text) if segment.strip()]
    segments: list[str] = []
    for segment in raw_segments:
        if "||" in segment:
            segments.append(segment)
            continue
        segments.extend(split_long_plain_segment(segment, 90))
    return segments


def split_long_plain_segment(segment: str, max_chars: int) -> list[str]:
    if len(segment) <= max_chars:
        return [segment]

    tokens = segment.split()
    if len(tokens) <= 1:
        return [segment[i : i + max_chars] for i in range(0, len(segment), max_chars)]

    chunks: list[str] = []
    current = ""
    for token in tokens:
        candidate = f"{current} {token}".strip()
        if len(candidate) <= max_chars or not current:
            current = candidate
            continue
        chunks.append(current)
        current = token
    if current:
        chunks.append(current)
    return chunks


def wrap_line(text: str, max_chars: int, max_lines: int) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    tokens = expand_long_tokens(split_tokens(text), max_chars)
    lines: list[str] = []
    current = ""

    for token in tokens:
        separator = "" if not current or is_thai_join(current, token) else " "
        candidate = f"{current}{separator}{token}" if current else token
        if len(candidate) <= max_chars or not current:
            current = candidate
            continue
        lines.append(current)
        current = token

    if current:
        lines.append(current)

    if len(lines) <= max_lines:
        return lines
    return rebalance_lines(" ".join(lines), max_lines)


def split_tokens(text: str) -> list[str]:
    if thai_word_tokenize is not None and re.search(r"[\u0e00-\u0e7f]", text):
        tokens = [token.strip() for token in thai_word_tokenize(text, engine="newmm", keep_whitespace=False)]
        return [token for token in tokens if token] or [text]

    parts = re.split(r"(\s+|[，,。.!?;:]+)", text)
    tokens: list[str] = []
    buffer = ""

    for part in parts:
        if not part:
            continue
        if part.isspace():
            if buffer:
                tokens.append(buffer)
                buffer = ""
            continue
        if re.fullmatch(r"[，,。.!?;:]+", part):
            if buffer:
                buffer += part
                tokens.append(buffer)
                buffer = ""
            elif tokens:
                tokens[-1] += part
            continue
        if re.search(r"[A-Za-z0-9]", part):
            if buffer:
                tokens.append(buffer)
                buffer = ""
            tokens.append(part)
        else:
            buffer += part

    if buffer:
        tokens.append(buffer)
    return tokens or [text]


def is_thai_join(left: str, right: str) -> bool:
    return bool(re.search(r"[\u0e00-\u0e7f]$", left) and re.search(r"^[\u0e00-\u0e7f]", right))


def expand_long_tokens(tokens: list[str], max_chars: int) -> list[str]:
    expanded: list[str] = []
    for token in tokens:
        if len(token) <= max_chars:
            expanded.append(token)
        else:
            expanded.extend(token[i : i + max_chars] for i in range(0, len(token), max_chars))
    return expanded


def rebalance_lines(text: str, max_lines: int) -> list[str]:
    if max_lines <= 1:
        return [text]

    target = max(1, len(text) // max_lines)
    breakpoints = [m.end() for m in re.finditer(r"[ ,.!?;:]+", text)]
    lines: list[str] = []
    start = 0

    for _ in range(max_lines - 1):
        ideal = start + target
        candidates = [point for point in breakpoints if start < point < len(text)]
        if candidates:
            point = min(candidates, key=lambda p: abs(p - ideal))
        else:
            point = min(len(text), ideal)
        lines.append(text[start:point].strip())
        start = point

    tail = text[start:].strip()
    if tail:
        lines.append(tail)
    return [line for line in lines if line]


def make_captions(text: str, bilingual: bool, max_chars: int, max_lines: int) -> list[Caption]:
    captions: list[Caption] = []
    for segment in split_segments(text):
        if bilingual and "||" in segment:
            left, right = [part.strip() for part in segment.split("||", 1)]
            lines = []
            lines.extend(wrap_line(left, max_chars=max_chars, max_lines=1))
            lines.extend(wrap_line(right, max_chars=max_chars, max_lines=1))
        else:
            lines = wrap_line(segment, max_chars=max_chars, max_lines=max_lines)

        if not lines:
            continue
        weight = max(1, sum(len(line) for line in lines))
        captions.append(Caption(lines=lines, weight=weight))
    return captions


def distribute_times(captions: list[Caption], duration: float, min_seconds: float) -> list[tuple[float, float, Caption]]:
    if not captions:
        return []

    required = min_seconds * len(captions)
    if required >= duration:
        cue_duration = duration / len(captions)
        starts = [i * cue_duration for i in range(len(captions))]
        return [(start, min(duration, start + cue_duration), caption) for start, caption in zip(starts, captions)]

    flexible_duration = duration - required
    total_weight = sum(caption.weight for caption in captions)
    current = 0.0
    timed = []
    for caption in captions:
        extra = flexible_duration * caption.weight / total_weight
        end = current + min_seconds + extra
        timed.append((current, end, caption))
        current = end

    if timed:
        start, _, caption = timed[-1]
        timed[-1] = (start, duration, caption)
    return timed


def format_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def format_srt(captions: list[Caption], duration: float, min_seconds: float) -> str:
    blocks: list[str] = []
    for index, (start, end, caption) in enumerate(distribute_times(captions, duration, min_seconds), start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{format_timestamp(start)} --> {format_timestamp(end)}",
                    *caption.lines,
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def default_output_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.srt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SRT from transcript plus clip duration.")
    parser.add_argument("input", type=Path, help="Transcript .txt file")
    parser.add_argument("--duration", required=True, help="Clip duration in seconds, MM:SS, or HH:MM:SS")
    parser.add_argument("-o", "--output", type=Path, help="Output .srt file")
    parser.add_argument("--bilingual", action="store_true", help="Treat lines containing '||' as Thai || English pairs")
    parser.add_argument("--max-chars", type=int, default=34, help="Target max characters per subtitle line")
    parser.add_argument("--max-lines", type=int, default=2, help="Maximum lines per cue for monolingual captions")
    parser.add_argument("--min-seconds", type=float, default=1.1, help="Minimum seconds per cue when duration allows")
    args = parser.parse_args()

    duration = parse_duration(args.duration)
    if duration <= 0:
        raise SystemExit("Duration must be greater than zero")

    transcript = read_text(args.input)
    captions = make_captions(transcript, args.bilingual, args.max_chars, args.max_lines)
    if not captions:
        raise SystemExit(f"No caption text found in {args.input}")

    output = args.output or default_output_path(args.input)
    output.write_text(format_srt(captions, duration, args.min_seconds), encoding="utf-8")
    print(f"Wrote {output} ({len(captions)} cues, {duration:.3f}s)")


if __name__ == "__main__":
    main()
