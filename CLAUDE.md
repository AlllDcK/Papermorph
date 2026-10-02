# Agent 工作指南

项目根目录：`/Users/a1212/Projects/AnimeBook`。
先阅读 [`plan.md`](plan.md)，了解详细目标、已确认要求、候选编排和待定事项。本文件提供目录地图、素材说明和执行约定，避免重复维护完整计划。

## 当前方向

- 以参考书为基础重新创作数学动画练习册，先做第一章实验。
- 成品是尽量轻量、自包含的静态站点，无应用后端和数据库。
- 数学教学动画是核心。用户已验证纯 JS 动画的可行性，允许实现 agent 自行处理动画细节；技术栈尚未选定。
- 概念、公式和说明在动画主画面内逐步出现，并配合语音；不使用底部或侧边的独立字幕栏承担讲解。
- 所有操作都在屏幕上完成，不设纸笔任务：讲解中途在画面内插入小测，讲完后做全屏整章练习，均自动判题。
- 中英文切换显示。Edge TTS 计划用于制作阶段预生成语音，目前尚无语音资产。
- 课程角色是 agent 用 SVG 画的无穷符号 ∞（`index.html` 中的 `mascotEl`），不用狗狗素材，也不用 π。角色服务于教学，不遮挡或替代数学演示。

## 目录地图

```text
AnimeBook/
├── CLAUDE.md           # Agent 工作指南与目录地图
├── plan.md             # 详细项目计划
├── README.md           # PDF 按章节导出图片的使用说明
├── split_book.py       # PDF 每页导出为 PNG 的脚本
├── sections.json       # 分组名称、章节与单元信息、PDF 页码范围
├── requirements.txt    # PDF 导出脚本的 Python 依赖
├── Everything You Need to Ace Pre-Algebra and Algebra I in One Big Fat Notebook (Jason Wang) (z-library.sk, 1lib.sk, z-lib.sk).pdf
│                      # 原始参考书，641 页
├── book_pages/         # 原书书页图片；内部制作参考
│   ├── 00_cover/       # 封面、版权页、扉页
│   ├── 01_preface/     # 前言
│   ├── 02_contents/    # 目录及之后的空白页
│   ├── ch01/           # 第一章，含 Unit 1 标题页；首个实验的参考内容
│   ├── ch02/           # 第二章
│   ├── …              # 中间章节文件夹，按相同规则命名
│   ├── ch68/           # 第六十八章
│   ├── 98_index/       # 索引
│   ├── 99_back_matter/ # 末尾推荐页
│   └── manifest.json   # 导出来源、分辨率、命名规则和分组信息
├── img/                # 用户准备的美术素材
│   ├── 1.png           # 十个表情的大图，保留原文件
│   ├── doge main.png
│   ├── expressions/    # 从 1.png 裁出的独立表情，已排除底部编号及中文介绍
│   │   ├── 01_default.png     # 默认头像
│   │   ├── 02_explaining.png  # 开心讲题
│   │   ├── 03_thinking.png    # 思考
│   │   ├── 04_confused.png    # 疑惑
│   │   ├── 05_angry.png       # 生气
│   │   ├── 06_anxious.png     # 害怕／紧张
│   │   ├── 07_teasing.png     # 友好调侃
│   │   ├── 08_speechless.png  # 无语
│   │   ├── 09_praising.png    # 自信／表扬
│   │   └── 10_inspired.png    # 灵机一动
│   └── mascot/         # 可直接使用的透明素材
│       ├── png/        # 上述十个表情的透明版本，以及 main.png 主形象
│       ├── svg/        # 同名 SVG，内嵌透明 PNG，不是矢量路径
│       ├── manifest.json # 文件映射、尺寸、原图裁切范围
│       ├── preview.html  # 素材预览，可切换棋盘、深色、纸色、白色背景
│       └── README.md     # 使用方式与重新生成说明
├── scripts/
│   └── prepare_mascot.swift # 在 macOS 上生成透明 PNG 和 SVG 封装
├── content/chNN/       # 每章英文讲稿 narration.en.json（[[mark]] 标记动画触发词）及 tts 缓存
├── .claude/skills/animebook-chapter/  # 做章节的流程、已定约定、踩过的坑、引擎速查（新章节先读）
├── tools/
│   ├── tts.py          # Edge TTS 生成 MP3、词级时间点与逐句字幕
│   ├── e2e_chNN.py     # 各章浏览器端到端检查（Playwright）；改引擎后全部重跑
│   └── check_blank.py  # 检测开场留白：旁白已开始、画面仍为空的步骤
├── site/               # 可部署的静态站点（只部署此目录）
│   ├── index.html      # 书架、书封与章节目录（同一页，hash 切换；章节数据在 UNITS；localStorage 记进度）
│   ├── lib/            # 共用引擎 engine.js / engine.css；书架数据与样式 bookshelf.js / bookshelf.css；目录页单元小图 unit-art.js
│   └── chNN/           # ch01–ch68 每章一个目录：index.html（本章步骤与题目）、audio/en/（MP3 与 timings.js）
├── .venv/              # 现有 PDF 处理工具的 Python 虚拟环境
├── .git/               # 本地 Git 仓库，尚未配置远程
└── .DS_Store           # macOS 自动生成的目录信息
```

`book_pages/` 共 641 张 PNG。文件名如 `page_0015.png`，数字为从 1 开始的 PDF 原始页序，不是书上印刷的页码。

第一章位于 `book_pages/ch01/`：第 14 页是单元标题，第 15–19 页是正文，第 20 页是练习，第 21 页是答案。

`img/` 中的狗狗素材已决定不用于课程（2026-10-01），保留作参考。`img/expressions/` 是保留白背景的原像素裁切版，`img/mascot/` 是透明版本；图案内部的道具、文字和符号保留。处理版本裁去了外围空白，尺寸及来源见 `img/mascot/manifest.json`。

SVG 将 PNG 以 data URL 嵌入，单个文件自包含；仍然是位图，放大后不会获得矢量细节。角色可以作为整体在页面中移动、缩放或淡入淡出，但眼睛、手和身体不是独立可操作的 SVG 路径。

网站源码在 `site/`，无构建步骤。美术素材继续补充时，同步更新 `img/` 的目录说明。

## 素材使用

- 原始 PDF 和 `book_pages/` 仅供内部参考。成品重新编写讲解、绘制数学图形，不把原书截图、切图或整页排版作为课程界面。
- 对第一章先阅读 `book_pages/ch01/`，再进行教学编排。章节边界见 `sections.json`；不要把 PDF 页序与书页印刷页码混用。
- 原图 `img/1.png` 和 `img/doge main.png` 保留，处理版本放在独立目录，不覆盖原图。
- 表情素材包含黑板、数学符号和道具；这些装饰不代表当前课程的定义或题目答案。
- 部分角色图案内部仍带原有中文装饰文字，底下的编号和中文介绍已去除。双语课程的关键讲解使用页面文字，不依赖图片内文字。
- 根据教学情境选用角色表情，答错反馈以解释和鼓励为主，避免机械地用生气或调侃表情回应错误。
- 处理素材后核对透明背景、裁切边界、完整图案和实际文件格式，并更新本文件。SVG 若内嵌位图，要明确说明，不能称为真正的矢量路径。

## 执行约定

1. 以用户最新明确指示为准。`plan.md` 中标为候选或待定的方案不能当成已批准决定；确认新决定后同步修改相关段落。
2. 当前重点是完善计划与素材。后续按用户授权推进技术栈、首章分镜、代表性动画及完整首章，不根据计划自行扩展全书。
3. 优先完成可观看、可暂停、可操作、可判题的教学过程，再扩展导航、装饰和复用框架。
4. 普通暂停、教学暂停、重播及语言切换要保持语音、画面文字和数学对象的状态一致。画面不要简单叠加未对齐的音频。
5. 数学判题检查数学含义。第一章的自然数按从 1 开始的约定，whole numbers 包含 0；同一个数可以属于多个类别。
6. 数学公式与图形应保持准确。角色、颜色和动效不能遮挡标签或造成集合关系、数轴位置等歧义。
7. 站点运行时不依赖 Python、在线 TTS、后端或数据库。制作工具与发布资源分开，原书及开发环境不随站点部署。
8. Git 仅在本地使用。没有用户明确指示，不添加远程仓库、不 push、不发布站点；保留用户已有的修改。
9. audiobook 项目尚未查看。用户授权参考时再检查实际实现，不推测它的路径、接口或素材规格。

## 现有工具

查看章节分组：

```sh
.venv/bin/python split_book.py --list
```

重新导出书页到新的目录：

```sh
.venv/bin/python split_book.py --dpi 200 --output book_pages_200dpi
```

安装和其他导出参数见 `README.md`。已有图片通常可以直接使用，不必重复导出。`.venv/` 服务于现有 PDF 工具，不是已确定的网站开发环境。

本地预览（音频需要 HTTP，不能双击打开）：

```sh
python3 -m http.server 8765 -d site   # 打开 http://localhost:8765/
```

`?beat=N&t=秒` 直接停在某一步的某一时刻，便于截图审阅。改动播放或题目逻辑后运行各章的 `uv run --with playwright tools/e2e_chNN.py`（需先启动上面的预览服务器）。

修改讲稿后重新生成语音（只重做改动过的步骤，需联网）：

```sh
uv run --with edge-tts tools/tts.py content/chNN/narration.en.json site/chNN/audio/en
```

讲稿中的 `[[mark]]` 名称必须与 `index.html` 中该步使用的 `m('mark')` 一致。

在 macOS 上重新生成角色素材：

```sh
swift -module-cache-path /private/tmp/animebook-swift-cache scripts/prepare_mascot.swift
```

此命令覆盖 `img/mascot/` 中的派生 PNG、SVG、清单和预览页，保留原图与白背景裁切版。首次运行可能需要等待 Swift 编译。无需为部署网站安装 Swift。

## 验证与交接

- 文档修改核对路径、实际目录和既定需求是否一致。
- 素材修改检查角色轮廓、内部白色细节、透明边缘，以及是否残留底部编号和中文介绍。
- 后续开发实际播放完整教学流程；检查暂停恢复、小测、数学交互、双语及判题。必要的自动检查集中在核心逻辑。
- 静态产物通过本地 HTTP 预览验证，不只检查文件是否生成。
- 交接说明完成内容、文件位置、验证结果和仍待决定的问题；及时更新目录地图和 `plan.md`，不要把未完成事项写成已完成。
