# AnimeBook

把一本书（PDF）做成带动画、语音和互动练习的网页书。第一本是 *Pre-Algebra & Algebra*，68 章，网站在 `site/`。

完整制作流程、脚本、引擎与模板都在技能 `.claude/skills/animebook/`（英文，从 `SKILL.md` 读起）。本书的计划与进度见 `plan.md`，目录地图与约定见 `CLAUDE.md`。

常用命令（`SKILL=.claude/skills/animebook`）：

```sh
uv run --with pymupdf $SKILL/scripts/outline.py book.pdf                 # 看 PDF 书签，生成 sections.json
uv run --with pymupdf $SKILL/scripts/split_pages.py book.pdf             # 按章导出书页图片和 text.md
python3 -m http.server 8765 -d site                                       # 本地预览
uv run --with playwright tools/e2e_ch01.py                                # 某章端到端测试
```
