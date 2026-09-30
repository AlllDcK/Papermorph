# 角色素材

本目录包含十个表情和主形象的透明 PNG，以及同名的 SVG 封装。原图和白背景裁切版保留在上级目录。

- `png/`：透明 PNG，保留原画纹理。外围白色或米白色背景已去除，内部眼白、纸张及道具保留。
- `svg/`：把透明 PNG 内嵌进 SVG，无外部图片依赖。**不是矢量路径**，不支持无限放大或直接操作角色的手、眼睛等部件。
- `manifest.json`：名称、来源、尺寸、原图裁切范围和 PNG／SVG 路径。
- `preview.html`：打开即可查看全部素材，可以切换背景检查透明边缘。

图案下方的编号和中文介绍已去除；黑板及图案内部的原有文字和数学符号保留。

| 名称 | 表情 |
| --- | --- |
| `01_default` | 默认头像 |
| `02_explaining` | 开心讲题 |
| `03_thinking` | 思考 |
| `04_confused` | 疑惑 |
| `05_angry` | 生气 |
| `06_anxious` | 害怕／紧张 |
| `07_teasing` | 友好调侃 |
| `08_speechless` | 无语 |
| `09_praising` | 自信／表扬 |
| `10_inspired` | 灵机一动 |
| `main` | 主形象 |

网页中直接使用，例如：

```html
<img src="img/mascot/svg/03_thinking.svg" alt="思考中的小伙伴">
```

路径相对于使用它的页面位置调整；通常按图片原始比例显示。PNG 与 SVG 包含相同的角色像素，PNG 文件更小，按实际需要选用。

从项目根目录重新生成（需要 macOS 自带的 Swift）：

```sh
swift -module-cache-path /private/tmp/animebook-swift-cache scripts/prepare_mascot.swift
```

脚本通过识别与画布边缘连通的近背景色区域生成透明度，并处理淡色边缘；不会重新生成角色。重新运行会覆盖本目录的派生图片、清单和预览，不会改动原图。
