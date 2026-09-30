#!/usr/bin/env python3
"""按 sections.json 的 PDF 页码分组，将每页渲染为 PNG。"""

import argparse
import json
from pathlib import Path

try:
    import pymupdf
except ImportError:
    raise SystemExit("请先安装依赖：.venv/bin/python -m pip install -r requirements.txt")


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, help="省略时使用脚本目录内唯一的 PDF")
    parser.add_argument("--sections", type=Path, default=ROOT / "sections.json")
    parser.add_argument("--output", type=Path, default=ROOT / "book_pages")
    parser.add_argument("--dpi", type=int, default=150, help="图片分辨率，默认 150")
    parser.add_argument("--list", action="store_true", help="只查看分组，不导出图片")
    parser.add_argument("--overwrite", action="store_true", help="允许重新渲染并覆盖同名图片")
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error("DPI 必须大于 0")
    if args.pdf is None:
        pdfs = sorted(p for p in ROOT.iterdir() if p.suffix.lower() == ".pdf")
        if len(pdfs) != 1:
            parser.error("请指定 PDF 路径；自动查找需要目录内恰好有一本 PDF")
        args.pdf = pdfs[0]

    sections = json.loads(args.sections.read_text(encoding="utf-8"))
    with pymupdf.open(args.pdf) as doc:
        # 页码从 1 开始，以 PDF 文件的实际页序为准。
        next_page = 1
        folders = set()
        for section in sections:
            folder = section["folder"]
            start, end = section["start"], section["end"]
            if not folder or folder in {".", ".."} or "/" in folder or "\\" in folder:
                parser.error(f"无效文件夹名：{folder!r}")
            if folder in folders:
                parser.error(f"重复文件夹名：{folder}")
            if not isinstance(start, int) or not isinstance(end, int):
                parser.error(f"页码必须为整数：{folder}")
            if start != next_page or end < start or end > len(doc):
                parser.error(f"页码不连续、重叠或越界：{folder} ({start}-{end})")
            folders.add(folder)
            next_page = end + 1
        if next_page != len(doc) + 1:
            parser.error("分组必须覆盖整本 PDF 的每一页")

        print(f"共 {len(doc)} 页，{len(sections)} 个文件夹，{args.dpi} DPI", flush=True)
        if args.list:
            for s in sections:
                print(f'{s["folder"]}: {s["start"]}-{s["end"]}  {s["title"]}')
            return
        if args.output.exists() and any(args.output.iterdir()) and not args.overwrite:
            parser.error("输出目录已有文件；请换 --output 路径，或使用 --overwrite 重新导出")

        args.output.mkdir(parents=True, exist_ok=True)
        manifest = {
            "source": args.pdf.resolve().name,
            "page_count": len(doc),
            "dpi": args.dpi,
            "format": "png",
            "page_numbering": "PDF 页序，从 1 开始；不是书页印刷页码",
            "filename_pattern": "page_{pdf_page:04d}.png",
            "sections": sections,
        }
        for s in sections:
            directory = args.output / s["folder"]
            directory.mkdir(parents=True, exist_ok=True)
            for page_number in range(s["start"], s["end"] + 1):
                page = doc[page_number - 1]
                pixmap = page.get_pixmap(dpi=args.dpi, colorspace=pymupdf.csRGB, alpha=False)
                target = directory / f"page_{page_number:04d}.png"
                # 先写临时文件，避免中断时留下半张图片。
                temporary = target.with_suffix(".tmp")
                temporary.write_bytes(pixmap.tobytes("png"))
                temporary.replace(target)
            print(f'{s["folder"]}: {s["start"]}-{s["end"]} 已完成', flush=True)

        (args.output / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"完成：{args.output.resolve()}", flush=True)


if __name__ == "__main__":
    main()
