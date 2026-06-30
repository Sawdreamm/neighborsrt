#!/usr/bin/env python3
"""Validate SRT structure, timing, and basic readability limits."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TIMECODE_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp874"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_timestamp(value: str) -> int:
    hh, mm, rest = value.split(":")
    ss, ms = rest.split(",")
    return ((int(hh) * 60 + int(mm)) * 60 + int(ss)) * 1000 + int(ms)


def validate(path: Path, max_chars: int, max_lines: int) -> list[str]:
    content = read_text(path).replace("\r\n", "\n").replace("\r", "\n").strip()
    if not content:
        return ["file is empty"]

    errors: list[str] = []
    previous_end = -1
    expected_index = 1

    for block_no, block in enumerate(re.split(r"\n{2,}", content), start=1):
        lines = [line.rstrip() for line in block.split("\n") if line.strip()]
        if len(lines) < 3:
            errors.append(f"block {block_no}: expected index, timecode, and text")
            continue

        if not lines[0].isdigit():
            errors.append(f"block {block_no}: index is not numeric")
        elif int(lines[0]) != expected_index:
            errors.append(f"block {block_no}: expected index {expected_index}, got {lines[0]}")

        match = TIMECODE_RE.fullmatch(lines[1].strip())
        if not match:
            errors.append(f"block {block_no}: invalid timecode")
        else:
            start = parse_timestamp(match.group("start"))
            end = parse_timestamp(match.group("end"))
            if end <= start:
                errors.append(f"block {block_no}: end time is not after start time")
            if start < previous_end:
                errors.append(f"block {block_no}: overlaps previous cue")
            previous_end = end

        text_lines = lines[2:]
        if len(text_lines) > max_lines:
            errors.append(f"block {block_no}: has {len(text_lines)} text lines, max is {max_lines}")
        for line_no, text in enumerate(text_lines, start=1):
            if len(text) > max_chars:
                errors.append(f"block {block_no} line {line_no}: {len(text)} chars, max is {max_chars}")

        expected_index += 1

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SRT structure and readability.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--max-chars", type=int, default=42)
    parser.add_argument("--max-lines", type=int, default=2)
    args = parser.parse_args()

    errors = validate(args.input, args.max_chars, args.max_lines)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {args.input}")


if __name__ == "__main__":
    main()
