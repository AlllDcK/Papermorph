# 按章节导出电子书图片

运行脚本，将本目录的 PDF 按章节拆成文件夹，每页保存为一张 PNG：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python split_book.py
```

输出在 `book_pages/`：

- `00_cover/`：封面、版权页、扉页（PDF 第 1–4 页）
- `01_preface/`：前言（第 5–6 页）
- `02_contents/`：目录和之后的空白页（第 7–13 页）
- `ch01/` 到 `ch68/`：各章正文、练习和答案；单元标题页归入该单元第一章
- `98_index/`：索引（第 632–640 页）
- `99_back_matter/`：末尾推荐页（第 641 页）

文件名如 `page_0014.png`，数字是从 1 开始的 **PDF 原始页序**，不是书页上印刷的页码。所有 641 页各导出一次，包含空白页。

`sections.json` 保存章节名称和页码范围，依据本书 PDF 书签生成并核对。调整分组时可编辑此文件；脚本会检查所有页码连续且不遗漏。`book_pages/manifest.json` 记录本次导出的分组和分辨率。

默认 150 DPI；提高到 200 DPI 会增加图片大小和导出时间：

```sh
.venv/bin/python split_book.py --list
.venv/bin/python split_book.py --dpi 200 --output book_pages_200dpi
```

目录里有多本 PDF 时可以显式传入文件路径。输出目录已有文件时脚本会停止；需要重新生成同名图片可加 `--overwrite`，它会覆盖图片，不会清理额外文件。
