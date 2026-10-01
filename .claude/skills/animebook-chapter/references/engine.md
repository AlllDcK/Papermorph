# 课程引擎速查（以 site/lib/engine.js 为准）

写步骤代码或新题型前先读本文件。函数名如与代码不一致，以代码为准，并顺手更新本文件。

## 舞台与状态

- 舞台为 SVG，`viewBox 0 0 1600 900`，所有动画元素画在 `#scene` 中。HTML 卡片放在 `#ui`，坐标系与舞台相同。
- 每个动画元素带一个状态对象，由 `render()` 写回 DOM：`x y`（平移）、`s`（缩放）、`r`（旋转，度）、`o`（不透明度）、`d`（描边绘制进度 0–1）、`a_<属性>`（数值属性，如 `'a_stroke-width'`）、`c_<属性>`（十六进制颜色）。补间用到的键要先在创建时赋初值。
- 缩放、旋转都绕元素自身原点。所以把内容画在 (0,0) 周围，再用 `x/y` 摆放位置。
- `S` 保存本章跨步骤共用的对象（`S.line`、`S.dots`、`S.ring`、`S.panel`……）。`reset()` 会清空它，需要跨步使用的对象都要登记在 `S` 上。

## 绘图

| 函数 | 用途 |
| --- | --- |
| `G(parent, {x,y,s,r,o})` | 分组 |
| `path(parent, d, attrs, {d:0})` | 路径；传 `d:0` 表示之后用 `draw()` 逐步画出 |
| `T(parent, str, {x,y,size,fill,font,weight,anchor,o})` | 文字（默认 UI 字体） |
| `M(parent, parts, {x,y,size,fill,anchor,o,s})` | 数学式，基线在 y；`parts` 由字符串、`F(n,d)` 分数、`R(x)` 根号组成；返回的元素带 `_w` 宽度 |
| `chip(parent, parts, color, {x,y,size})` | 胶囊形数字卡片，中心在 (x,y) |
| `tokens(parent, items, {x,y,size,anchor})` | 一行算式拆成可单独移动的记号；项可以是字符串、parts 数组或 `{t, fill}`；返回数组，带 `.w`、`.y`、`.size` |
| `mathEl(parts, size)` | HTML 行内数学（小 SVG），基线与正文对齐 |
| `rich([...])` | HTML 富文本：字符串、DOM 节点、`$m(...parts)` 行内数学 |

数学字符串里 1–2 个字母的小写片段（a、x、ab）自动排成斜体变量；更长的单词保持正体。

数轴：`X(v)`、`Y0`、`tick`、`dot`；章节可改 `AXIS.o`（0 的横坐标）和 `AXIS.u`（每单位像素）。`panel(t0)` 淡出上一个场景组并新建一个，`header()` 写小标题。第一章专用：家族列表 `row`（在 ch01 页面里）、集合图（`RINGS`、`CHAIN`、`buildVenn`、`regionAt`）。新章节需要的新场景（坐标系、方程两边等）按同样方式写一组小函数。

## 按主题的现成画法（第 2–10 章加入引擎）

| 函数 | 用途 |
| --- | --- |
| `collapse(row, i, j, parts, t0, {color, live})` | 框住 tokens 行里第 i..j 个记号，缩成一个结果并合拢空隙；返回新行。`live: true` 用于答题动画 |
| `numberLine(t0, lo, hi)`、`move(p, a, b, y, t0)`、`landDot(p, v, t0, color)`、`brace(p, a, b, y, label, color, t0)` | 整数数轴、带箭头的移动、落点、区间括号；`POS`/`NEG` 为正负颜色 |
| `tile / tiles / popAll / cancelPairs` | 正负方块与成对抵消 |
| `vAxis(p, {x, Yf, lo, hi, step})`、`thermometer(p, {...}).set(v, t0, run)` | 竖直数轴、温度计 |
| `fracRow(p, items, {x, y, size})`、`reduce(row, k, 'num'/'den', value, color, t0)` | 分数行，可逐个划掉分子分母写约分结果 |
| `rect(p, x, y, w, h, fill, o, stroke)`、`bracketH(p, x1, x2, y, label, color, t0)` | 面积模型用的矩形和水平括号 |

| `pointRow(p, digits, x, y, places)` + `.hop(from, to, t0)` | 小数点在数字间跳动（ch10、ch20） |
| `balance(p, {x, y, L})` + `.load(side, parts, color, t0)`、`.tilt(deg, t0)` | 天平（ch24、ch25） |
| `atile(p, kind, x, y, neg)`、`tileRow`、`cancel`、`popIn` | 代数方块 x²、x、y、1 及正负抵消（ch23、ch25） |
| `eqLine(p, L, R, y, t0, {xEq, sym, note})` | 等号（或不等号）对齐的一行推导，右侧可带注释 |
| `ray(p, v, closed, dir, t0)`、`segment(p, a, b, ca, cb, t0)` | 数轴上的射线与线段解集（ch26、ch27） |
| `E(exp)` | `M()` 中的上标指数 |
| `plane(p, {cx, cy, u, x0, x1, y0, y1, t0})` | 坐标系（ch30 起）。返回 `P`：`PX/PY` 换算、`dot(x, y, color, t0, {label, dx, dy, anchor, into, run})`、`walk`（从原点沿 x 再沿 y 走到点）、`line(xa, ya, xb, yb, color, t0)`（延长到网格边）、`arrow(xa, ya, xb, yb, color, t0, {label})`、`stair(x, y, rise, run, t0, {labels})`（先竖后横的斜率台阶）、`half(a, b, c, color, t0)`（给 a·x + b·y ≥ c 的半平面着色，裁在网格内）；`line` 传 `dash` 时淡入而不是描出。每步设 `P.layer = panel(0)`，点和线画进本步面板，换步自动淡出；答题动画传 `{run: fx, into: 层}` |

题型补充：`pickPoint(P, [x, y], 答对说明, (x, y) => 错因, 答对动画?, test?)`（`test(x, y)` 给出时接受任何满足的点，`[x, y]` 只用于 Show answer；答对说明也可以是 `(x, y) => 文本`） 在坐标系上选格点，方向键移动光标、Enter 选定或直接点击；同一 quiz 连续两题时，前一题的答对动画要画进本步面板（qlayer 会在下一题清空）。`tapEls(row, idx, right, yes, no, onRight)` 点选画面里算式的某个记号（如“先算哪一步”）；`blanks` 的格子接受分数与带分数，`{box: '3/4', lowest: true}` 要求最简形式。

## 步骤（BEATS）

```js
['sqrt2', '标题', (m, D) => {
  const p = panel(0);                       // 面板：先淡出上一个，再新建
  draw(path(S.line, '…', {…}, { d: 0 }), m('sq'), 1.1);
  show(T(p, '…', { o: 0 }), m('dec', 3.6));  // 该 mark 的词开始后 3.6 秒出现
}, { ask: done => quiz(BAND, [问题…], done) }],   // 可选：本步是小测
```

- `m(name, 偏移)` 返回讲稿里 `[[name]]` 后第一个词开始的秒数；拼错名字会直接报错。`D` 是本段语音时长。
- 补间函数：`tw(e, to, t0, dur, ease)`、`prog(q => …, t0, dur)`（自定义进度，例如滚动圆、弧线运动）、`show/hide/draw/pop/pulse`、`glow/glowRun`（集合圈描边闪亮）、`stream`（数字逐位出现）。缓动有 `io`、`out`、`back`、`lin`。
- 普通步骤播完自动进入下一步；带 `ask` 的步骤播完旁白后等待学生答完再继续。

## 小测与练习

```js
quiz(位置, [{ id: 'c-xxx', prompt: [...rich], build: 题型(...) }, …], done, 'Quick check')
```

- 位置：`BAND`（数轴下方横条）、`TOPR`（数轴场景右上）、`RIGHT`（集合图右栏）、`SCREEN`（全屏）、`SORT_SCREEN`（全屏集合图分类）。
- `id` 前缀：`c-` 表示讲解中途的小测，`p-` 表示整章练习；结束页按前缀汇总首次作答成绩。
- 题型：
  - `choice(选项, 正确序号, 答对说明, 各选项错因[], 答对动画?)`：单选，数字键作答。
  - `tap(数值[], 正确值, 答对说明, v => 错因, 答对动画?)`：点数轴上的点，←/→ 移动，Enter 选定。
  - `grid(行[{parts, ans:[键], why, fx?}], 列[[键, 名称, 颜色?, 快捷键?]], {multi, text})`：表格勾选，↑/↓ 换行，数字键或字母键选择。
  - `sorter(卡片[[parts, 最小圈, 错因]], i => [x, y])`：拖进集合图，←/→ 挑卡片，1–6 放入圈。
  - `blanks(行[{parts: [..., {box: '21'}, ...], why, hint?, fx?}])`：在算式里填数字，Tab 切换格子，Enter 检查；接受 “−5”“-5”；答错显示 hint，答对显示 why。
- 新题型的 `build(body, api)` 需返回 `{ reveal, check?, lock?, key?(e), hint? }`，判完调用 `api.grade(是否正确, 说明, {right, total})`。`key` 处理本题快捷键，返回 true 表示已处理；`hint` 显示在题干下方。
- 答题动画使用独立时钟，函数有 `fx`、`fxp`、`pulseFx`、`shakeFx`、`glowFx`、`popDotFx`、`floatText`、`hopsFx`。离开本步时会自动收尾，不必自己清理。

## 播放器

`seek(i, play)` 重建并快进到第 i 步；`start(i, play)` 从当前画面开始第 i 步。`P.keys` 是当前题目的按键处理器，由 `quiz` 设置，由 `clearCards` 清除。字幕数据来自 `TIMINGS[id].cues`。
