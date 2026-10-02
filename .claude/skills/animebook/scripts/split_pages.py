#!/usr/bin/env python3
"""Render every PDF page to PNG, one folder per section of sections.json.

    uv run --with pymupdf split_pages.py book.pdf --sections sections.json --out book_pages
    uv run --with pymupdf split_pages.py book.pdf --list            # check the map only
    uv run --with pymupdf split_pages.py book.pdf --only ch05       # one section
    uv run --with pymupdf split_pages.py book.pdf --text-only        # text layer only, no images

Each section folder also gets text.md: the PDF's own text layer, page by page. Read that
first; open a page image only for diagrams, layout or text the layer gets wrong (it is far
cheaper than an image). Scanned books have no text layer, so text.md comes out empty.

Files are named page_NNNN.png by PDF page order (from 1), never by printed page numbers.
The script refuses a map with gaps or overlaps, and refuses to overwrite existing images
unless --overwrite is given. The pages are a private reference for the author; they are
never published with the site.
"""
import argparse
import json
from pathlib import Path

import pymupdf


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--sections", type=Path, default=Path("sections.json"))
    ap.add_argument("--out", type=Path, default=Path("book_pages"))
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--list", action="store_true", help="print the map and stop")
    ap.add_argument("--only", nargs="*", help="render only these section folders")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--text-only", action="store_true", help="write text.md files, skip the images")
    a = ap.parse_args()
    sections = json.loads(a.sections.read_text(encoding="utf-8"))
    with pymupdf.open(a.pdf) as doc:
        nxt, seen = 1, set()
        for s in sections:
            f, st, en = s["folder"], s["start"], s["end"]
            if not f or "/" in f or "\\" in f or f in (".", "..") or f in seen:
                ap.error(f"bad or repeated folder name: {f!r}")
            if st != nxt or en < st or en > len(doc):
                ap.error(f"pages must run on without gaps or overlaps: {f} ({st}-{en}), expected start {nxt}")
            seen.add(f)
            nxt = en + 1
        if nxt != len(doc) + 1:
            ap.error(f"the map ends at page {nxt - 1}; the PDF has {len(doc)} pages")
        print(f"{len(doc)} pages, {len(sections)} sections, {a.dpi} dpi")
        if a.list:
            for s in sections:
                print(f'{s["folder"]}: {s["start"]}-{s["end"]}  {s["title"]}')
            return
        todo = [s for s in sections if not a.only or s["folder"] in a.only]
        for s in todo:
            d = a.out / s["folder"]
            d.mkdir(parents=True, exist_ok=True)
            text = [f"## page {p}\n\n{doc[p - 1].get_text().strip()}\n" for p in range(s["start"], s["end"] + 1)]
            (d / "text.md").write_text(f"# {s['title']}\n\n" + "\n".join(text), encoding="utf-8")
            if a.text_only:
                continue
            for p in range(s["start"], s["end"] + 1):
                target = d / f"page_{p:04d}.png"
                if target.exists() and not a.overwrite:
                    continue
                tmp = target.with_suffix(".tmp")     # never leave half an image behind
                tmp.write_bytes(doc[p - 1].get_pixmap(dpi=a.dpi, colorspace=pymupdf.csRGB, alpha=False).tobytes("png"))
                tmp.replace(target)
            print(f'{s["folder"]}: {s["start"]}-{s["end"]} done', flush=True)
        manifest = {"source": a.pdf.name, "page_count": len(doc), "dpi": a.dpi,
                    "page_numbering": "PDF page order from 1, not printed page numbers",
                    "filename_pattern": "page_{pdf_page:04d}.png", "sections": sections}
        (a.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
