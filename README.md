# AnimeBook

把一本书（PDF）做成带动画、语音和互动练习的网页书。网站在 `site/`，首页书架目前收录：

- *Pre-Algebra & Algebra*：68 章，保留原有 `site/chNN/` 路径。
- *Ace Math & the Big Fat Notebook*：已完成前三章，入口在 `site/math-notebook/`；全书规划为 63 章，后续制作因 API 成本暂停。

完整制作流程、脚本、引擎与模板都在技能 `.claude/skills/animebook/`（英文，从 `SKILL.md` 读起）。本书的计划与进度见 `plan.md`，目录地图与约定见 `CLAUDE.md`。

第二本书从 Book2 合并，使用独立引擎和学习进度；约定与进度见 `books/math-notebook/BOOK.md` 和 `chapters.md`，讲稿在 `content/math-notebook/`，检查脚本在 `tools/math-notebook/`。原始 PDF 和提取书页仅供本地制作，不进入 Git 或部署目录。

常用命令（`SKILL=.claude/skills/animebook`）：

```sh
uv run --with pymupdf $SKILL/scripts/outline.py book.pdf                 # 看 PDF 书签，生成 sections.json
uv run --with pymupdf $SKILL/scripts/split_pages.py book.pdf             # 按章导出书页图片和 text.md
python3 -m http.server 8765 -d site                                       # 本地预览
uv run --with playwright tools/e2e_ch01.py                                # 某章端到端测试
uv run --with playwright tools/math-notebook/smoke_ch01.py                # 第二本书；另有 ch02、ch03
```
