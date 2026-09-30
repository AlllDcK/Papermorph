# 课程引擎速查（以 site/ch01/index.html 为准）

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
| `mathEl(parts, size)` | HTML 行内数学（小 SVG），基线与正文对齐 |
| `rich([...])` | HTML 富文本：字符串、DOM 节点、`$m(...parts)` 行内数学 |

第一章专用：数轴（`X(v)`、`Y0`、`tick`、`dot`）、家族列表 `row`、右侧面板 `panel/header`、集合图（`RINGS`、`CHAIN`、`buildVenn`、`regionAt`）。新章节需要的新场景（坐标系、方程两边等）按同样方式写一组小函数。

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
- 新题型的 `build(body, api)` 需返回 `{ reveal, check?, lock?, key?(e), hint? }`，判完调用 `api.grade(是否正确, 说明, {right, total})`。`key` 处理本题快捷键，返回 true 表示已处理；`hint` 显示在题干下方。
- 答题动画使用独立时钟，函数有 `fx`、`fxp`、`pulseFx`、`shakeFx`、`glowFx`、`popDotFx`、`floatText`、`hopsFx`。离开本步时会自动收尾，不必自己清理。

## 播放器

`seek(i, play)` 重建并快进到第 i 步；`start(i, play)` 从当前画面开始第 i 步。`P.keys` 是当前题目的按键处理器，由 `quiz` 设置，由 `clearCards` 清除。字幕数据来自 `TIMINGS[id].cues`。
