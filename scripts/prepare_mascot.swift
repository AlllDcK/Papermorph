// macOS: swift -module-cache-path /private/tmp/animebook-swift-cache scripts/prepare_mascot.swift
// 从边缘识别背景，保留封闭区域中的眼白、纸张等细节；不重绘角色。
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let output = root.appendingPathComponent("img/mascot")
let fm = FileManager.default
for dir in ["png", "svg"] {
    try fm.createDirectory(at: output.appendingPathComponent(dir), withIntermediateDirectories: true)
}

let expressions: [(String, String)] = [
    ("01_default", "默认头像"), ("02_explaining", "开心讲题"),
    ("03_thinking", "思考"), ("04_confused", "疑惑"),
    ("05_angry", "生气"), ("06_anxious", "害怕／紧张"),
    ("07_teasing", "友好调侃"), ("08_speechless", "无语"),
    ("09_praising", "自信／表扬"), ("10_inspired", "灵机一动")
]
let inputs = expressions.map { ($0.0, $0.1, "img/expressions/\($0.0).png") }
    + [("main", "主形象", "img/doge main.png")]
var records: [[String: Any]] = []

for (name, label, path) in inputs {
    let sourceURL = root.appendingPathComponent(path)
    guard let source = CGImageSourceCreateWithURL(sourceURL as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        fatalError("无法读取：\(path)")
    }
    let w = image.width, h = image.height, count = w * h
    let colorSpace = CGColorSpace(name: CGColorSpace.sRGB)!
    let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue
    var pixels = [UInt8](repeating: 0, count: count * 4)
    pixels.withUnsafeMutableBytes { bytes in
        let context = CGContext(data: bytes.baseAddress, width: w, height: h,
                                bitsPerComponent: 8, bytesPerRow: w * 4,
                                space: colorSpace, bitmapInfo: bitmapInfo)!
        context.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
    }

    // 估计白色或米白色背景；只删除从画布边缘连通的近背景色区域。
    let corners = [0, w - 1, (h - 1) * w, count - 1]
    let background = (0..<3).map { channel in
        corners.reduce(0.0) { $0 + Double(pixels[$1 * 4 + channel]) } / 4.0
    }
    let whiteBackground = background.min()! >= 244
    let backgroundTolerance: Double = 17
    let fringeDistance: Double = whiteBackground ? 110 : 45
    func distance(_ i: Int) -> Double {
        (0..<3).map { abs(Double(pixels[i * 4 + $0]) - background[$0]) }.max()!
    }
    var removed = [Bool](repeating: false, count: count)
    var queue = [Int]()
    queue.reserveCapacity(count)
    func enqueue(_ i: Int) {
        if !removed[i] && distance(i) <= backgroundTolerance {
            removed[i] = true
            queue.append(i)
        }
    }
    for x in 0..<w { enqueue(x); enqueue((h - 1) * w + x) }
    for y in 0..<h { enqueue(y * w); enqueue(y * w + w - 1) }
    var cursor = 0
    while cursor < queue.count {
        let i = queue[cursor]; cursor += 1
        let x = i % w, y = i / w
        if x > 0 { enqueue(i - 1) }
        if x + 1 < w { enqueue(i + 1) }
        if y > 0 { enqueue(i - w) }
        if y + 1 < h { enqueue(i + w) }
    }
    guard !queue.isEmpty && queue.count < count else { fatalError("背景识别失败：\(name)") }

    var rgba = pixels
    for i in 0..<count {
        if removed[i] {
            for channel in 0..<4 { rgba[i * 4 + channel] = 0 }
            continue
        }
        let x = i % w, y = i / w
        let onEdge = (x > 0 && removed[i - 1]) || (x + 1 < w && removed[i + 1])
            || (y > 0 && removed[i - w]) || (y + 1 < h && removed[i + w])
        // 处理紧邻背景的淡色抗锯齿边缘，减轻白色轮廓；内部色彩保持不变。
        let d = distance(i)
        if onEdge && d < fringeDistance {
            let alpha = max(0, min(1, d / fringeDistance))
            for channel in 0..<3 {
                let premultiplied = Double(pixels[i * 4 + channel]) - background[channel] * (1 - alpha)
                rgba[i * 4 + channel] = UInt8(max(0, min(255 * alpha, premultiplied.rounded())))
            }
            rgba[i * 4 + 3] = UInt8((255 * alpha).rounded())
        }
    }

    var minX = w, minY = h, maxX = 0, maxY = 0
    for i in 0..<count where rgba[i * 4 + 3] > 0 {
        minX = min(minX, i % w); maxX = max(maxX, i % w)
        minY = min(minY, i / w); maxY = max(maxY, i / w)
    }
    minX = max(0, minX - 2); minY = max(0, minY - 2)
    maxX = min(w - 1, maxX + 2); maxY = min(h - 1, maxY + 2)
    let outW = maxX - minX + 1, outH = maxY - minY + 1
    var cropped = [UInt8]()
    cropped.reserveCapacity(outW * outH * 4)
    for y in minY...maxY {
        cropped.append(contentsOf: rgba[((y * w + minX) * 4)..<((y * w + maxX + 1) * 4)])
    }
    let provider = CGDataProvider(data: Data(cropped) as CFData)!
    let result = CGImage(width: outW, height: outH, bitsPerComponent: 8,
                         bitsPerPixel: 32, bytesPerRow: outW * 4, space: colorSpace,
                         bitmapInfo: CGBitmapInfo(rawValue: bitmapInfo), provider: provider,
                         decode: nil, shouldInterpolate: true, intent: .defaultIntent)!
    let pngURL = output.appendingPathComponent("png/\(name).png")
    let destination = CGImageDestinationCreateWithURL(pngURL as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(destination, result, nil)
    guard CGImageDestinationFinalize(destination) else { fatalError("PNG 保存失败：\(name)") }
    let pngData = try Data(contentsOf: pngURL)
    let svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="\(outW)" height="\(outH)" viewBox="0 0 \(outW) \(outH)" role="img" aria-labelledby="title">
      <title id="title">\(label)</title>
      <desc>透明 PNG 的自包含 SVG 封装；图像内容为位图，不是矢量路径。</desc>
      <image width="\(outW)" height="\(outH)" href="data:image/png;base64,\(pngData.base64EncodedString())"/>
    </svg>
    """
    try svg.write(to: output.appendingPathComponent("svg/\(name).svg"), atomically: true, encoding: .utf8)
    records.append(["id": name, "label": label, "source": path,
                    "png": "png/\(name).png", "svg": "svg/\(name).svg",
                    "width": outW, "height": outH,
                    "source_crop": [minX, minY, outW, outH],
                    "background_pixels_removed": queue.count])
    print("\(name)：\(outW) × \(outH)，背景已透明")
}

let manifest: [String: Any] = [
    "svg_type": "embedded-transparent-png", "true_vector": false,
    "originals_preserved": true, "assets": records
]
try JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys])
    .write(to: output.appendingPathComponent("manifest.json"))

let cards = records.map { record in
    let name = record["id"] as! String, label = record["label"] as! String
    return """
    <article><div class="art"><img src="svg/\(name).svg" alt="\(label)"></div>
    <h2>\(label)</h2><p>\(name)</p><a href="png/\(name).png">PNG</a> · <a href="svg/\(name).svg">SVG</a></article>
    """
}.joined(separator: "\n")
let preview = """
<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>角色素材预览</title><style>
body{margin:24px;font:16px system-ui;background:#f4f3ee;color:#222}h1{font-size:24px}h2{font-size:17px;margin:12px 0 4px}p{margin:6px 0}
nav{display:flex;gap:12px;margin:20px 0;flex-wrap:wrap}button{padding:8px 16px;cursor:pointer;border:1px solid #aaa;border-radius:8px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}article{padding:14px;background:white;border-radius:12px}
.art{height:280px;display:flex;align-items:center;justify-content:center;background-color:#fff;background-image:conic-gradient(#ddd 25%,transparent 0 50%,#ddd 0 75%,transparent 0);background-size:24px 24px;border-radius:6px}
.art img{max-width:100%;max-height:100%;object-fit:contain}body[data-bg="dark"] .art{background:#263749}body[data-bg="paper"] .art{background:#fff4d8}body[data-bg="white"] .art{background:#fff}
</style><body><h1>角色素材预览</h1><p>10 个表情 + 主形象。SVG 内嵌透明 PNG，保留原画风格，不是矢量路径。</p>
<nav><button data-bg="check">透明棋盘</button><button data-bg="dark">深色背景</button><button data-bg="paper">纸色背景</button><button data-bg="white">白色背景</button></nav>
<main>\(cards)</main><script>document.querySelectorAll('button').forEach(button=>button.onclick=()=>document.body.dataset.bg=button.dataset.bg);</script></body></html>
"""
try preview.write(to: output.appendingPathComponent("preview.html"), atomically: true, encoding: .utf8)
