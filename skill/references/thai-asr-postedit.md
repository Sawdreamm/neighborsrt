# Thai ASR Post-Edit

Use this reference when Whisper produces Thai subtitles with wrong words, broken Thai syllables, or domain-specific mistakes.

## Principle

ASR post-editing is a language task, not a deterministic formatting task. Use an LLM or a human editor to infer likely words from the full clip context, while preserving timestamps.

## Workflow

1. Read the full SRT before editing individual cues.
2. Identify domain and glossary candidates from repeated words, visual context, title, user notes, and nearby captions.
3. Correct ASR errors by meaning and context, not by sound alone.
4. Preserve every index and timestamp exactly.
5. Keep one or two lines per cue.
6. Validate the final SRT with `scripts/validate_srt.py`.
7. Mark uncertain terms for user review instead of pretending certainty.

## Beauty Clinic Glossary

- Neighbor Clinic / เนเบอร์
- ในงบนี้
- ทำอะไรที่ Neighbor ได้บ้าง
- โปรแกรมออกแบบรูปหน้า
- Facial Design
- คุณหมอไอซ์
- ปรับรูปหน้า
- งานสกิน
- ยกกระชับ
- กรอบหน้า
- เหนียง
- Ultraformer
- Ultraformer III
- Ultraformer MPT
- Ulthera
- Ulthera Prime
- Volnewmer
- Thermage FLX
- Thermage
- Botox / โบท็อกซ์
- ลดกราม
- ริ้วรอย
- ร่องลึก
- หน้าผาก
- หางตา
- หว่างคิ้ว
- เลเซอร์หน้าใส
- Dual Yellow
- Dual Pulse
- Pico Laser
- รอยแดงสิว
- รอยสิว
- หลุมสิว
- Skin Booster
- White Peptide
- วิตามินผิว
- ผิวหน้าเรียบเนียน

## Neighbor Clinic Notes

Use this section when the video is about Neighbor Clinic or says "Neighbor".

- Prefer "Neighbor" or "เนเบอร์" over ASR guesses such as "neighbor" inside Thai text, "ในงบเบอร์", or unrelated English words.
- The phrase "ทำอะไรที่ Neighbor ได้บ้าง" is plausible in intro hooks about budgets and should be considered before rewriting it as "ในงบนี้ทำอะไรได้บ้าง".
- Neighbor-related content often discusses facial design, face contouring, skin work, Ultraformer III, Volnewmer, Ulthera, Botox, and doctor-led planning.
- If an ASR output sounds like "ดัว...พัลส์/พัว/เยลโลว์", treat it as ambiguous between "Dual Pulse" and "Dual Yellow". Do not force one unless the audio or user-provided context confirms it.
- If the exact laser/device name is uncertain, prefer a safe caption such as "เลเซอร์หน้าใส" and add a note to review the brand name, rather than inventing a specific device.

## Ambiguous Term Handling

- Keep brand/device names only when confidence is high.
- Use user corrections as the highest-priority glossary for future passes.
- When confidence is medium, choose a generic but faithful term and list the uncertain candidate separately for review.
- Never let glossary matching override clear audio context; the glossary narrows guesses, it does not replace listening.

## Prompt

```text
You are a professional Thai subtitle editor.

Task:
- Correct Thai ASR errors in this SRT using the full context.
- Preserve every SRT index and timestamp exactly.
- Rewrite only subtitle text.
- Keep meaning faithful to the likely spoken audio.
- Keep one or two readable lines per cue.
- Fix broken Thai words, medical/aesthetic terms, numbers, and prices.
- Preserve uncertain brand names only when context strongly supports them.
- Return valid SRT only.

Context/glossary:
[Add domain, names, products, prices, and user notes here]

Uncertain terms to flag:
- [List any brand/device names that were inferred rather than confirmed]
```
