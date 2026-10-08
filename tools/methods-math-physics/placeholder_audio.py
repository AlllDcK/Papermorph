"""Silent placeholder narration with estimated timings, for when Edge TTS cannot be reached.

    python3 tools/methods-math-physics/placeholder_audio.py content/methods-math-physics/ch01/narration.ru.json site/methods-math-physics/ch01/audio/ru

Writes <beat>.mp3 (silence of the estimated speaking time) and timings.js in the same format as
the skill's tts.py (dur, marks, cues), so the page runs unchanged with captions. It never writes
tts.py's cache (narration.<lang>.timings.json), so a later real tts.py run synthesizes every beat
and replaces these files; [[marks]] keep the animation in step with the real voice.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MARK = re.compile(r"\[\[(\w+)\]\]")
CPS = 14.0                      # characters per second (letters and spaces) at rate −6 %
PAUSE = {",": .25, ";": .3, ":": .3, "—": .3, ".": .55, "?": .55, "!": .55}
LEAD, TAIL = .15, .35


def split_marks(raw):
    marks, clean, pos = {}, [], 0
    for i, part in enumerate(MARK.split(raw)):
        if i % 2:
            marks[part] = pos
        else:
            clean.append(part)
            pos += len(part)
    return "".join(clean), marks


def clock(clean):
    """Estimated start time of every character."""
    t, out = LEAD, []
    for ch in clean:
        out.append(t)
        t += 1 / CPS + PAUSE.get(ch, 0)
    return out, t + TAIL


def word_start(clean, pos):
    while pos < len(clean) and not clean[pos].isalnum():
        pos += 1
    return min(pos, len(clean) - 1)


def main(src, out_dir):
    spec = json.loads(Path(src).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    timings = {}
    for beat, raw in spec["beats"].items():
        clean, marks = split_marks(raw)
        at, total = clock(clean)
        mp3 = out / f"{beat}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", f"{total:.3f}",
                        "-c:a", "libmp3lame", "-b:a", "8k", str(mp3)], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                                   capture_output=True, text=True, check=True).stdout)
        cues, start = [], 0
        for m in list(re.finditer(r"[.?!]\s+", clean)) + [None]:
            end = m.end() if m else len(clean)
            text = clean[start:end].strip()
            if text:
                cues.append([round(at[word_start(clean, start)], 3), text])
            start = end
        timings[beat] = {"dur": round(dur, 3), "marks": {k: round(at[word_start(clean, p)], 3) for k, p in marks.items()}, "cues": cues}
        print(f"{beat}: {dur:.1f} s (placeholder)")
    # TIMINGS_PLACEHOLDER makes this book's engine show captions and a note; tts.py's timings.js has no such flag.
    (out / "timings.js").write_text("window.TIMINGS_PLACEHOLDER = true;\nwindow.TIMINGS = " + json.dumps(timings, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:3])
