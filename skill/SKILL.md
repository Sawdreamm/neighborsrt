---
name: neighborsrt
description: Create professional Neighbor Clinic-aware subtitles from audio, video, scripts, transcripts, or translated Thai/English caption text. Use when Codex needs to transcribe media with Whisper, generate timed .srt captions, post-edit Thai ASR with beauty clinic and Neighbor Clinic context, format bilingual Thai+English subtitles, validate SRT timing and readability, control subtitle line length, or prepare import-ready captions for CapCut, Premiere, DaVinci Resolve, or YouTube.
---

# NeighborSRT

## Overview

Use this skill to produce professional `.srt` subtitles for short-form and long-form video. Prefer real media transcription with Whisper when audio or video is available; use transcript + duration generation only when no media file or word timestamps are available.

## Workflow Decision

- **Audio/video file available**: run `scripts/transcribe_media_to_srt.py` to get real Whisper timestamps.
- **Only transcript + duration available**: run `scripts/transcript_to_srt.py` to create draft timing from text length.
- **Bilingual Thai+English requested**: generate or transcribe the source language first, then use `references/bilingual-rewrite-prompt.md` to create Thai+English caption text while preserving timestamps.
- **Thai ASR words are wrong**: read `references/thai-asr-postedit.md`, post-edit the full SRT with context and glossary, then validate again.
- **Existing SRT needs QA**: run `scripts/validate_srt.py`, then repair readability issues.

For the full professional workflow, read `references/pro-workflow.md`.

## Quick Commands

Transcribe a video/audio file with Whisper:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/transcribe_media_to_srt.py video.mp4 --language th --model small
```

Transcribe and also save a plain transcript:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/transcribe_media_to_srt.py video.mp4 --language th --model small --transcript-out video.txt
```

Translate non-English speech into English SRT with Whisper:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/transcribe_media_to_srt.py video.mp4 --task translate --model small
```

Generate a draft SRT from transcript and clip duration:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/transcript_to_srt.py transcript.txt --duration 01:30
```

Generate bilingual SRT from paired lines:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/transcript_to_srt.py transcript.txt --duration 90 --bilingual --max-chars 32 --max-lines 2
```

Validate before importing:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/validate_srt.py captions.srt --max-chars 42 --max-lines 2
```

Burn subtitles into a video for preview or final export:

```bash
python3 /Users/dream/.codex/skills/neighborsrt/scripts/burn_subtitles.py video.mp4 captions.srt -o video.subtitled.mp4
```

## Input Patterns

Plain transcript:

```text
วันนี้เราจะมาทำซับให้เร็วขึ้นมาก
โดยไม่ต้องนั่งจับเวลาทีละประโยค
```

Bilingual transcript using `||`:

```text
วันนี้เราจะมาทำซับให้เร็วขึ้นมาก || Today we'll make subtitles much faster.
โดยไม่ต้องนั่งจับเวลาทีละประโยค || Without timing every sentence manually.
```

Speaker labels are allowed:

```text
Dream: วันนี้เราจะลอง workflow ใหม่ || Dream: Today we'll try a new workflow.
```

## Professional Rules

- Preserve exact timestamps when working from an existing SRT or Whisper output.
- Keep one or two lines per cue.
- Use 28-38 characters per line for mobile-first captions; validate at 42 max unless the user asks otherwise.
- For bilingual subtitles, prefer Thai on line 1 and English on line 2.
- Avoid four-line bilingual cues; split long thoughts instead.
- Preserve names, numbers, brand terms, handles, URLs, hashtags, and speaker labels.
- Tell the user clearly when timing is estimated rather than audio-derived.
- Use an LLM or human review for Thai ASR correction when words are semantically wrong; deterministic scripts can format captions but cannot reliably infer misheard domain terms from audio context.

## Resources

- `scripts/transcribe_media_to_srt.py`: transcribe audio/video with Whisper and export timed SRT.
- `scripts/transcript_to_srt.py`: generate draft SRT from transcript plus duration.
- `scripts/validate_srt.py`: check SRT structure, overlaps, line count, and line length.
- `scripts/burn_subtitles.py`: optional ffmpeg burn-in for preview or hard-subtitled exports.
- `references/caption-style.md`: caption and bilingual formatting rules.
- `references/bilingual-rewrite-prompt.md`: prompt for creating bilingual SRT while preserving timestamps.
- `references/thai-asr-postedit.md`: Thai ASR correction workflow and prompt for context-aware word repair.
- `references/pro-workflow.md`: practical end-to-end workflow and model guidance.
