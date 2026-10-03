"""Register a ready chapter: add it to UNITS on the contents page, set the previous chapter's CHAPTER.next,
and mark its row in chapters.md.   python3 tools/math-notebook/register.py 2 8"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
n, minutes = int(sys.argv[1]), int(sys.argv[2])
sections = {s['folder']: s for s in json.loads((ROOT / 'books/math-notebook/sections.json').read_text())}
sec = sections[f'ch{n:02d}']
title = re.sub(r'^Chapter \d+: ', '', sec['title']).replace('Graphic Inequalities', 'Graphing Inequalities')
unit = re.sub(r'^UNIT \d+: ', '', sec['unit'])

# contents page: UNITS = [ [unit, [[title, minutes], ...]], ... ]
idx = ROOT / 'site/math-notebook/index.html'
s = idx.read_text()
m = re.search(r"const UNITS = \[[^\n]*\n(.*?)\n\];", s, re.S)
lines = m.group(1).split('\n')
units = [json.loads(l.strip().rstrip(',').replace("'", '"')) for l in lines]
done = sum(len(c) for _, c in units)
if done >= n:
    sys.exit(f'ch{n:02d} already listed')
if done != n - 1:
    sys.exit(f'contents has {done} chapters; register ch{done + 1:02d} first')
if units[-1][0] == unit:
    units[-1][1].append([title, minutes])
else:
    units.append([unit, [[title, minutes]]])
js = lambda v: json.dumps(v, ensure_ascii=False).replace('"', "'").replace("', '", "', '")
body = '\n'.join(f"  [{js(u)}, {js(c)}]," for u, c in units)
s = s[:m.start(1)] + body + s[m.end(1):]
idx.write_text(s)

# previous chapter's next link
if n > 1:
    prev = ROOT / f'site/math-notebook/ch{n - 1:02d}/index.html'
    p = prev.read_text()
    p2, k = re.subn(r"(const CHAPTER = \{[^}]*?)(, next: '[^']*')?( \};)", rf"\1, next: '../ch{n:02d}/'\3", p, count=1)
    if not k:
        sys.exit('CHAPTER line not found in previous chapter')
    prev.write_text(p2)

# chapters.md row
cm = ROOT / 'books/math-notebook/chapters.md'
c = cm.read_text()
c, k = re.subn(rf"^\| {n} \| (.*?) \| (\d+) \| [^|]* \| [^|]* \|$", rf"| {n} | \1 | \2 | {minutes} | ready |", c, count=1, flags=re.M)
cm.write_text(c)
print(f'registered ch{n:02d} "{title}" ({minutes} min, unit "{unit}"); chapters.md row updated: {bool(k)}')
