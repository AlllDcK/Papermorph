"""Generate narration audio and word-mark timings with Edge TTS.

Usage (from the project root; SKILL is this skill's folder):
    uv run --with edge-tts $SKILL/scripts/tts.py content/ch01/narration.en.json site/ch01/audio/en

Needs network access and ffprobe (from ffmpeg) for clip durations.

Narration text may contain [[mark]] tags placed before a word. The output
timings.js records each clip's duration and the time (seconds) at which the
word after every mark starts, so page animations can wait for that word,
plus one caption cue per sentence. Only beats whose text or voice changed are
regenerated; spoken word times are cached, so caption and mark rules can change
without new audio.
"""

import asyncio
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts

MARK = re.compile(r"\[\[(\w+)\]\]")


async def synth(text, voice, rate, mp3_path):
    words = []  # (seconds, word)
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append((chunk["offset"] / 1e7, chunk["text"]))
    return words


def split_marks(raw):
    """Return clean text and {mark: char position in clean text}."""
    marks, clean, pos = {}, [], 0
    # MARK.split alternates text, name, text, name, ...
    for i, part in enumerate(MARK.split(raw)):
        if i % 2:
            marks[part] = pos
        else:
            clean.append(part)
            pos += len(part)
    return "".join(clean), marks


def time_at(clean, words):
    """Return f(pos): start time of the first spoken word at or after char pos."""
    cursor, located = 0, []
    for t, w in words:
        i = clean.find(w, cursor)
        if i < 0:
            continue
        located.append((i, t))
        cursor = i + len(w)
    return lambda pos: next((round(t, 3) for i, t in located if i >= pos), None)


def mark_times(clean, marks, words):
    at, out = time_at(clean, words), {}
    for name, pos in marks.items():
        out[name] = at(pos)
        if out[name] is None:
            raise SystemExit(f"mark {name!r} not matched to a spoken word")
    return out


def caption_cues(clean, words):
    """One cue per sentence: [start seconds, sentence]."""
    at, cues, start = time_at(clean, words), [], 0
    for m in list(re.finditer(r"[.?!]\s+", clean)) + [None]:
        end = m.end() if m else len(clean)
        text = clean[start:end].strip()
        if text:
            cues.append([at(start) or 0, text])
        start = end
    return cues


def duration(mp3):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
        capture_output=True, text=True, check=True)
    return round(float(r.stdout), 3)


async def main(src, out_dir):
    spec = json.loads(Path(src).read_text())
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_path = Path(src).with_suffix(".timings.json")  # build cache, kept out of the site
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    voice, rate = spec["voice"], spec["rate"]
    result = {}
    for beat, raw in spec["beats"].items():
        key = hashlib.sha1(f"{voice}|{rate}|{raw}".encode()).hexdigest()
        mp3 = out_dir / f"{beat}.mp3"
        old = cache.get(beat)
        clean, marks = split_marks(raw)
        if old and old.get("key") == key and "words" in old and mp3.exists():
            words = old["words"]
        else:
            words = await synth(clean, voice, rate, mp3)
            print(f"{beat}: synthesized")
        result[beat] = {"key": key, "dur": duration(mp3), "words": words,
                        "marks": mark_times(clean, marks, words), "cues": caption_cues(clean, words)}
    cache_path.write_text(json.dumps(result, indent=1))
    js = {b: {"dur": v["dur"], "marks": v["marks"], "cues": v["cues"]} for b, v in result.items()}
    (out_dir / "timings.js").write_text("window.TIMINGS = " + json.dumps(js, indent=1) + ";\n")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:3]))
