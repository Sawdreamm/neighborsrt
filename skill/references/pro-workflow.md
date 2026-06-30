# Professional Subtitle Workflow

## Best Path For Real Clips

1. Transcribe the video or audio with `scripts/transcribe_media_to_srt.py`.
2. Validate the generated SRT with `scripts/validate_srt.py`.
3. If bilingual subtitles are needed, rewrite the timed SRT with the prompt in `bilingual-rewrite-prompt.md`.
4. Validate again.
5. Import the final `.srt` into CapCut, Premiere, DaVinci Resolve, or YouTube.
6. Optionally run `scripts/burn_subtitles.py` to create a hard-subtitled preview or final render.
7. Do a short manual timing pass only where the speaker talks unusually fast, pauses, laughs, or overlaps.

## Model Guidance

- `tiny` or `base`: fastest rough draft.
- `small`: recommended default for MacBook Pro M4 Pro 24GB.
- `medium`: better accuracy, slower.
- `large`: best accuracy, heavy; use only when needed.

## CapCut Settings

- Use one or two text lines per cue.
- Keep each line around 28-38 characters for mobile-first videos.
- Avoid four-line bilingual captions; split long thoughts into separate cues instead.
- Import `.srt` into CapCut, then apply visual style inside CapCut.

## Accuracy Notes

Whisper gives real segment timestamps from the audio, so it is much more accurate than distributing time from transcript length. Transcript-only generation is useful for draft timing or scripted voiceovers, but real media transcription is the professional path.
