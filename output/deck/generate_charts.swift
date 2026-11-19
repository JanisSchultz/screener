import Foundation
import CoreGraphics
import CoreText
import ImageIO
import UniformTypeIdentifiers

// Helper: parse hex color "#RRGGBB"
func cgColor(_ hex: String, alpha: CGFloat = 1.0) -> CGColor {
    let clean = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
    var rgb: UInt64 = 0
    Scanner(string: clean).scanHexInt64(&rgb)
    let r = CGFloat((rgb >> 16) & 0xFF) / 255.0
    let g = CGFloat((rgb >> 8) & 0xFF) / 255.0
    let b = CGFloat(rgb & 0xFF) / 255.0
    return CGColor(colorSpace: CGColorSpaceCreateDeviceRGB(), components: [r, g, b, alpha])!
}

func makeContext(width: Int, height: Int, bgHex: String) -> CGContext {
    let ctx = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: width * 4,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    )!
    ctx.setAllowsAntialiasing(true)
    ctx.setShouldAntialias(true)
    ctx.setAllowsFontSmoothing(true)
    ctx.setShouldSmoothFonts(true)
    ctx.setFillColor(cgColor(bgHex))
    ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
    return ctx
}

func savePNG(_ ctx: CGContext, to path: String) {
    let url = URL(fileURLWithPath: path)
    guard let image = ctx.makeImage(),
          let dest = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
        fatalError("Failed to create image destination for \(path)")
    }
    CGImageDestinationAddImage(dest, image, nil)
    if !CGImageDestinationFinalize(dest) {
        fatalError("Failed to write PNG to \(path)")
    }
    print("Saved \(path)")
}

enum HAlign { case left, center, right }

func drawText(
    _ ctx: CGContext,
    _ text: String,
    x: CGFloat,
    yTop: CGFloat,
    heightCanvas: CGFloat,
    fontName: String = "HelveticaNeue",
    size: CGFloat,
    bold: Bool = false,
    colorHex: String,
    align: HAlign = .left
) {
    let actualFontName = bold ? (fontName == "HelveticaNeue" ? "HelveticaNeue-Bold" : fontName) : fontName
    let font = CTFontCreateWithName(actualFontName as CFString, size, nil)
    let attrs: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): font,
        NSAttributedString.Key(kCTForegroundColorAttributeName as String): cgColor(colorHex)
    ]
    let attrStr = NSAttributedString(string: text, attributes: attrs)
    let line = CTLineCreateWithAttributedString(attrStr)
    var ascent: CGFloat = 0
    var descent: CGFloat = 0
    var leading: CGFloat = 0
    let width = CGFloat(CTLineGetTypographicBounds(line, &ascent, &descent, &leading))

    var drawX = x
    if align == .center {
        drawX = x - width / 2.0
    } else if align == .right {
        drawX = x - width
    }
    let baselineY = heightCanvas - yTop - ascent
    ctx.saveGState()
    ctx.textMatrix = .identity
    ctx.textPosition = CGPoint(x: drawX, y: baselineY)
    CTLineDraw(line, ctx)
    ctx.restoreGState()
}

func fillRectTop(_ ctx: CGContext, x: CGFloat, yTop: CGFloat, w: CGFloat, h: CGFloat, heightCanvas: CGFloat, colorHex: String, alpha: CGFloat = 1.0, radius: CGFloat = 0) {
    let rect = CGRect(x: x, y: heightCanvas - yTop - h, width: w, height: h)
    ctx.saveGState()
    ctx.setFillColor(cgColor(colorHex, alpha: alpha))
    if radius > 0 {
        let path = CGPath(roundedRect: rect, cornerWidth: radius, cornerHeight: radius, transform: nil)
        ctx.addPath(path)
        ctx.fillPath()
    } else {
        ctx.fill(rect)
    }
    ctx.restoreGState()
}

func strokeRectTop(_ ctx: CGContext, x: CGFloat, yTop: CGFloat, w: CGFloat, h: CGFloat, heightCanvas: CGFloat, colorHex: String, lineWidth: CGFloat, radius: CGFloat = 0) {
    let rect = CGRect(x: x, y: heightCanvas - yTop - h, width: w, height: h)
    ctx.saveGState()
    ctx.setStrokeColor(cgColor(colorHex))
    ctx.setLineWidth(lineWidth)
    if radius > 0 {
        let path = CGPath(roundedRect: rect, cornerWidth: radius, cornerHeight: radius, transform: nil)
        ctx.addPath(path)
        ctx.strokePath()
    } else {
        ctx.stroke(rect)
    }
    ctx.restoreGState()
}

func drawLineTop(_ ctx: CGContext, x1: CGFloat, yTop1: CGFloat, x2: CGFloat, yTop2: CGFloat, heightCanvas: CGFloat, colorHex: String, alpha: CGFloat = 1.0, width: CGFloat, dash: [CGFloat]? = nil) {
    ctx.saveGState()
    ctx.setStrokeColor(cgColor(colorHex, alpha: alpha))
    ctx.setLineWidth(width)
    ctx.setLineCap(.round)
    if let dash = dash {
        ctx.setLineDash(phase: 0, lengths: dash)
    }
    ctx.move(to: CGPoint(x: x1, y: heightCanvas - yTop1))
    ctx.addLine(to: CGPoint(x: x2, y: heightCanvas - yTop2))
    ctx.strokePath()
    ctx.restoreGState()
}

func drawCircleTop(_ ctx: CGContext, cx: CGFloat, cyTop: CGFloat, r: CGFloat, heightCanvas: CGFloat, fillHex: String, strokeHex: String? = nil, strokeWidth: CGFloat = 2) {
    let rect = CGRect(x: cx - r, y: heightCanvas - cyTop - r, width: r * 2, height: r * 2)
    ctx.saveGState()
    ctx.setFillColor(cgColor(fillHex))
    ctx.fillEllipse(in: rect)
    if let s = strokeHex {
        ctx.setStrokeColor(cgColor(s))
        ctx.setLineWidth(strokeWidth)
        ctx.strokeEllipse(in: rect)
    }
    ctx.restoreGState()
}

// =========================================================================
// CHART 1: Global Funnel Attrition Waterfall (1395 x 756 px for 465 x 252 pt)
// =========================================================================
func generateFunnelWaterfall() {
    let W = 1395, H = 756
    let Hc = CGFloat(H)
    let ctx = makeContext(width: W, height: H, bgHex: "#1E2761")

    // Card frame
    fillRectTop(ctx, x: 4, yTop: 4, w: CGFloat(W - 8), h: CGFloat(H - 8), heightCanvas: Hc, colorHex: "#232F70", radius: 22)
    strokeRectTop(ctx, x: 4, yTop: 4, w: CGFloat(W - 8), h: CGFloat(H - 8), heightCanvas: Hc, colorHex: "#3949A6", lineWidth: 3, radius: 22)

    // Chart Header & Legend
    drawText(ctx, "GLOBAL SURVIVAL FUNNEL (v7.19)", x: 34, yTop: 26, heightCanvas: Hc, size: 30, bold: true, colorHex: "#FFFFFF")

    // Legend top-right
    let legY: CGFloat = 34
    fillRectTop(ctx, x: 750, yTop: legY, w: 22, h: 22, heightCanvas: Hc, colorHex: "#5B7CFA", radius: 4)
    drawText(ctx, "Remaining", x: 780, yTop: legY - 3, heightCanvas: Hc, size: 24, colorHex: "#CADCFC")

    fillRectTop(ctx, x: 925, yTop: legY, w: 22, h: 22, heightCanvas: Hc, colorHex: "#FB923C", radius: 4)
    drawText(ctx, "Cut", x: 955, yTop: legY - 3, heightCanvas: Hc, size: 24, colorHex: "#CADCFC")

    fillRectTop(ctx, x: 1020, yTop: legY, w: 22, h: 22, heightCanvas: Hc, colorHex: "#FBBF24", radius: 4)
    drawText(ctx, "G3 Choke", x: 1050, yTop: legY - 3, heightCanvas: Hc, size: 24, colorHex: "#FBBF24")

    fillRectTop(ctx, x: 1185, yTop: legY, w: 22, h: 22, heightCanvas: Hc, colorHex: "#2DD4BF", radius: 4)
    drawText(ctx, "Prime", x: 1215, yTop: legY - 3, heightCanvas: Hc, size: 24, colorHex: "#2DD4BF")

    drawLineTop(ctx, x1: 34, yTop1: 78, x2: 1361, yTop2: 78, heightCanvas: Hc, colorHex: "#3949A6", width: 2)

    struct FunnelRow {
        let label: String
        let rem: Int
        let cut: Int
        let pctCut: String
        let remColor: String
        let cutColor: String
        let note: String
    }

    let rows: [FunnelRow] = [
        FunnelRow(label: "Starting Universe", rem: 1175, cut: 0, pctCut: "", remColor: "#5B7CFA", cutColor: "#FB923C", note: "1,175  (100.0%)"),
        FunnelRow(label: "G1 · Simple Business", rem: 1145, cut: 30, pctCut: "−2.6%", remColor: "#5B7CFA", cutColor: "#FB923C", note: "1,145  |  −30 (−2.6%)"),
        FunnelRow(label: "G2 · Essential & Habits", rem: 989, cut: 156, pctCut: "−13.3%", remColor: "#5B7CFA", cutColor: "#FB923C", note: "989  |  −156 (−13.3%)"),
        FunnelRow(label: "G3 · Moat & Pricing", rem: 483, cut: 506, pctCut: "−43.1%", remColor: "#5B7CFA", cutColor: "#FBBF24", note: "483  |  −506 (−43.1%)"),
        FunnelRow(label: "G4 · Runway CAP ≥ 15Y", rem: 375, cut: 108, pctCut: "−9.2%", remColor: "#5B7CFA", cutColor: "#FB923C", note: "375  |  −108 (−9.2%)"),
        FunnelRow(label: "G5 · Stewardship ≥ 1", rem: 359, cut: 16, pctCut: "−1.4%", remColor: "#5B7CFA", cutColor: "#FB923C", note: "359  |  −16 (−1.4%)"),
        FunnelRow(label: "G6 · Cash & Fortress B/S", rem: 225, cut: 134, pctCut: "−11.4%", remColor: "#2DD4BF", cutColor: "#FB923C", note: "225 (19.1%) | −134 (−11.4%)")
    ]

    let barX: CGFloat = 345
    let maxBarW: CGFloat = 670
    let startY: CGFloat = 104
    let rowStep: CGFloat = 90
    let barH: CGFloat = 54
    let maxVal: CGFloat = 1175.0

    for (i, row) in rows.enumerated() {
        let y = startY + CGFloat(i) * rowStep

        // Subtle alternating row band
        if i % 2 == 1 {
            fillRectTop(ctx, x: 24, yTop: y - 10, w: CGFloat(W - 48), h: barH + 20, heightCanvas: Hc, colorHex: "#283582", alpha: 0.45, radius: 10)
        }

        // Row label
        let labelColor = (i == 6) ? "#2DD4BF" : (i == 3 ? "#FBBF24" : "#FFFFFF")
        drawText(ctx, row.label, x: 34, yTop: y + 11, heightCanvas: Hc, size: 26, bold: (i == 0 || i == 3 || i == 6), colorHex: labelColor)

        // Remaining bar
        let remW = CGFloat(row.rem) / maxVal * maxBarW
        fillRectTop(ctx, x: barX, yTop: y, w: remW, h: barH, heightCanvas: Hc, colorHex: row.remColor, radius: 8)

        // Dropped segment
        let cutW = CGFloat(row.cut) / maxVal * maxBarW
        if row.cut > 0 {
            let cutDisplayW = max(cutW, 8)
            fillRectTop(ctx, x: barX + remW + 3, yTop: y, w: cutDisplayW, h: barH, heightCanvas: Hc, colorHex: row.cutColor, radius: 6)
            // Dotted connector from previous row's remaining end
            drawLineTop(ctx, x1: barX + remW + 3 + cutW, yTop1: y - 14, x2: barX + remW + 3 + cutW, yTop2: y, heightCanvas: Hc, colorHex: "#A8BCE8", alpha: 0.55, width: 2, dash: [4, 4])
        }

        // Label inside or right of bar
        if i == 0 {
            drawText(ctx, "1,175 (100%)", x: barX + remW + 16, yTop: y + 11, heightCanvas: Hc, size: 26, bold: true, colorHex: "#FFFFFF")
        } else {
            let totalEnd = barX + remW + max(cutW, 8) + 16
            let noteColor = (i == 6) ? "#2DD4BF" : (i == 3 ? "#FBBF24" : "#CADCFC")
            drawText(ctx, row.note, x: totalEnd, yTop: y + 11, heightCanvas: Hc, size: 24, bold: (i == 3 || i == 6), colorHex: noteColor)
        }
    }

    savePNG(ctx, to: "output/charts/funnel_waterfall.png")
}

// =========================================================================
// CHART 2: Mauboussin Fade DCF (1095 x 756 px for 365 x 252 pt)
// =========================================================================
func generateMauboussinFade() {
    let W = 1095, H = 756
    let Hc = CGFloat(H)
    let ctx = makeContext(width: W, height: H, bgHex: "#283582")

    strokeRectTop(ctx, x: 4, yTop: 4, w: CGFloat(W - 8), h: CGFloat(H - 8), heightCanvas: Hc, colorHex: "#3949A6", lineWidth: 3, radius: 22)

    // Title
    drawText(ctx, "EXPLICIT N-YEAR FADE TRAJECTORY (N = 25Y)", x: 34, yTop: 26, heightCanvas: Hc, size: 29, bold: true, colorHex: "#FFFFFF")

    // Legend
    drawLineTop(ctx, x1: 36, yTop1: 86, x2: 86, yTop2: 86, heightCanvas: Hc, colorHex: "#FBBF24", width: 7)
    drawText(ctx, "RONIC_t (50% → 20%)", x: 96, yTop: 71, heightCanvas: Hc, size: 24, bold: true, colorHex: "#FBBF24")

    drawLineTop(ctx, x1: 400, yTop1: 86, x2: 450, yTop2: 86, heightCanvas: Hc, colorHex: "#2DD4BF", width: 7)
    drawText(ctx, "g_t (11.5% → 3.0%)", x: 460, yTop: 71, heightCanvas: Hc, size: 24, bold: true, colorHex: "#2DD4BF")

    drawLineTop(ctx, x1: 735, yTop1: 86, x2: 785, yTop2: 86, heightCanvas: Hc, colorHex: "#CADCFC", width: 4, dash: [8, 6])
    drawText(ctx, "r = 8.50%", x: 795, yTop: 71, heightCanvas: Hc, size: 24, bold: true, colorHex: "#CADCFC")

    // Plot area
    let plotX: CGFloat = 105
    let plotYTop: CGFloat = 132
    let plotW: CGFloat = 930
    let plotH: CGFloat = 510
    let plotBottom = plotYTop + plotH

    // Stage 1 and Stage 2 subtle background zones
    let xAt25 = plotX + (25.0 - 1.0) / 29.0 * plotW
    fillRectTop(ctx, x: plotX, yTop: plotYTop, w: xAt25 - plotX, h: plotH, heightCanvas: Hc, colorHex: "#1E2761", alpha: 0.45)
    fillRectTop(ctx, x: xAt25, yTop: plotYTop, w: plotX + plotW - xAt25, h: plotH, heightCanvas: Hc, colorHex: "#2DD4BF", alpha: 0.08)

    // Stage Labels
    drawText(ctx, "STAGE 1: EXPLICIT FADE (t = 1..N)", x: (plotX + xAt25) / 2, yTop: plotYTop + 14, heightCanvas: Hc, size: 22, bold: true, colorHex: "#A8BCE8", align: .center)
    drawText(ctx, "STAGE 2", x: (xAt25 + plotX + plotW) / 2, yTop: plotYTop + 14, heightCanvas: Hc, size: 22, bold: true, colorHex: "#2DD4BF", align: .center)
    drawText(ctx, "TERMINAL", x: (xAt25 + plotX + plotW) / 2, yTop: plotYTop + 42, heightCanvas: Hc, size: 20, bold: false, colorHex: "#2DD4BF", align: .center)

    func mapX(_ t: CGFloat) -> CGFloat { plotX + (t - 1.0) / 29.0 * plotW }
    func mapY(_ pct: CGFloat) -> CGFloat { plotBottom - (pct / 55.0) * plotH }

    // Grid lines
    for yTick in [0, 10, 20, 30, 40, 50] {
        let yy = mapY(CGFloat(yTick))
        drawLineTop(ctx, x1: plotX, yTop1: yy, x2: plotX + plotW, yTop2: yy, heightCanvas: Hc, colorHex: "#4658B8", alpha: 0.45, width: 2)
        drawText(ctx, "\(yTick)%", x: plotX - 14, yTop: yy - 13, heightCanvas: Hc, size: 23, colorHex: "#A8BCE8", align: .right)
    }

    // X-axis ticks
    for xTick in [1, 5, 10, 15, 20, 25, 30] {
        let xx = mapX(CGFloat(xTick))
        drawLineTop(ctx, x1: xx, yTop1: plotBottom, x2: xx, yTop2: plotBottom + 10, heightCanvas: Hc, colorHex: "#A8BCE8", width: 2)
        let lbl = (xTick == 25) ? "N=25" : "Y\(xTick)"
        drawText(ctx, lbl, x: xx, yTop: plotBottom + 16, heightCanvas: Hc, size: 23, bold: (xTick == 25), colorHex: (xTick == 25 ? "#FFFFFF" : "#A8BCE8"), align: .center)
    }

    // Axes
    drawLineTop(ctx, x1: plotX, yTop1: plotYTop, x2: plotX, yTop2: plotBottom, heightCanvas: Hc, colorHex: "#A8BCE8", width: 3)
    drawLineTop(ctx, x1: plotX, yTop1: plotBottom, x2: plotX + plotW, yTop2: plotBottom, heightCanvas: Hc, colorHex: "#A8BCE8", width: 3)

    // Vertical CAP boundary at t = 25
    drawLineTop(ctx, x1: xAt25, yTop1: plotYTop, x2: xAt25, yTop2: plotBottom, heightCanvas: Hc, colorHex: "#FFFFFF", alpha: 0.75, width: 3, dash: [10, 8])

    // Hurdle line r = 8.50%
    let yHurdle = mapY(8.5)
    drawLineTop(ctx, x1: plotX, yTop1: yHurdle, x2: plotX + plotW, yTop2: yHurdle, heightCanvas: Hc, colorHex: "#CADCFC", width: 4, dash: [12, 8])
    drawText(ctx, "r = 8.50%", x: plotX + plotW - 10, yTop: yHurdle - 34, heightCanvas: Hc, size: 22, bold: true, colorHex: "#CADCFC", align: .right)

    // Series B: RONIC_t (50% -> 20% linear t=1..25, then 20% dashed t=25..30)
    drawLineTop(ctx, x1: mapX(1), yTop1: mapY(50), x2: mapX(25), yTop2: mapY(20), heightCanvas: Hc, colorHex: "#FBBF24", width: 8)
    drawLineTop(ctx, x1: mapX(25), yTop1: mapY(20), x2: mapX(30), yTop2: mapY(20), heightCanvas: Hc, colorHex: "#FBBF24", width: 6, dash: [10, 8])
    drawCircleTop(ctx, cx: mapX(1), cyTop: mapY(50), r: 10, heightCanvas: Hc, fillHex: "#FBBF24", strokeHex: "#1E2761", strokeWidth: 3)
    drawCircleTop(ctx, cx: mapX(25), cyTop: mapY(20), r: 10, heightCanvas: Hc, fillHex: "#FBBF24", strokeHex: "#1E2761", strokeWidth: 3)

    // Series A: g_t (11.5% -> 3.0% linear t=1..25, then 3.0% dashed t=25..30)
    drawLineTop(ctx, x1: mapX(1), yTop1: mapY(11.5), x2: mapX(25), yTop2: mapY(3.0), heightCanvas: Hc, colorHex: "#2DD4BF", width: 8)
    drawLineTop(ctx, x1: mapX(25), yTop1: mapY(3.0), x2: mapX(30), yTop2: mapY(3.0), heightCanvas: Hc, colorHex: "#2DD4BF", width: 6, dash: [10, 8])
    drawCircleTop(ctx, cx: mapX(1), cyTop: mapY(11.5), r: 10, heightCanvas: Hc, fillHex: "#2DD4BF", strokeHex: "#1E2761", strokeWidth: 3)
    drawCircleTop(ctx, cx: mapX(25), cyTop: mapY(3.0), r: 10, heightCanvas: Hc, fillHex: "#2DD4BF", strokeHex: "#1E2761", strokeWidth: 3)

    // Direct point labels (clear of lines)
    drawText(ctx, "RONIC₀ = 50%", x: mapX(1) + 22, yTop: mapY(50) - 22, heightCanvas: Hc, size: 24, bold: true, colorHex: "#FBBF24")
    drawText(ctx, "20% cap", x: mapX(27.5), yTop: mapY(20) - 40, heightCanvas: Hc, size: 23, bold: true, colorHex: "#FBBF24", align: .center)
    drawText(ctx, "g₀ = 11.5%", x: mapX(1) + 18, yTop: mapY(11.5) - 38, heightCanvas: Hc, size: 24, bold: true, colorHex: "#2DD4BF")
    drawText(ctx, "3.0% g_term", x: mapX(27.5), yTop: mapY(3.0) - 36, heightCanvas: Hc, size: 22, bold: true, colorHex: "#2DD4BF", align: .center)

    // Bottom equation callout
    drawText(ctx, "FCF_t = E_t × (1 − g_t / RONIC_t)    |    Reinvestment Spread: RONIC_t > r", x: CGFloat(W) / 2, yTop: 702, heightCanvas: Hc, size: 24, bold: true, colorHex: "#CADCFC", align: .center)

    savePNG(ctx, to: "output/charts/mauboussin_fade_dcf.png")
}

// =========================================================================
// CHART 3: Case Study 5Y Expected IRR vs 8.50% Hurdle (780 x 756 px for 260 x 252 pt)
// =========================================================================
func generateCaseStudyIRR() {
    let W = 780, H = 756
    let Hc = CGFloat(H)
    let ctx = makeContext(width: W, height: H, bgHex: "#FFFFFF")

    strokeRectTop(ctx, x: 3, yTop: 3, w: CGFloat(W - 6), h: CGFloat(H - 6), heightCanvas: Hc, colorHex: "#D5DFED", lineWidth: 3, radius: 20)

    drawText(ctx, "5Y EXPECTED IRR VS. 8.5% HURDLE", x: 30, yTop: 26, heightCanvas: Hc, size: 28, bold: true, colorHex: "#1E2761")
    drawText(ctx, "Bellman 5Y IRR (price date 2026-11-17)", x: 30, yTop: 64, heightCanvas: Hc, size: 22, colorHex: "#4B5563")

    struct CaseBar {
        let ticker: String
        let irr: CGFloat
        let color: String
        let label: String
        let tag: String?
    }

    let cases: [CaseBar] = [
        CaseBar(ticker: "MSFT", irr: 10.3, color: "#0D9488", label: "+10.3%", tag: "✓ PASS"),
        CaseBar(ticker: "SPGI", irr: 3.5, color: "#64748B", label: "+3.5%", tag: nil),
        CaseBar(ticker: "ASML.NL", irr: -0.7, color: "#C2410C", label: "−0.7%", tag: nil),
        CaseBar(ticker: "COST", irr: -4.6, color: "#C2410C", label: "−4.6%", tag: nil),
        CaseBar(ticker: "WM", irr: -10.5, color: "#C2410C", label: "−10.5%", tag: nil),
        CaseBar(ticker: "CRM", irr: 4.7, color: "#D97706", label: "+4.7%", tag: "✗ G4 FAIL")
    ]

    let plotX: CGFloat = 148
    let plotW: CGFloat = 596
    let plotYTop: CGFloat = 128
    let plotH: CGFloat = 515
    let plotBottom = plotYTop + plotH
    let minIRR: CGFloat = -16.5
    let maxIRR: CGFloat = 20.5

    func mapX(_ val: CGFloat) -> CGFloat {
        return plotX + (val - minIRR) / (maxIRR - minIRR) * plotW
    }

    let xZero = mapX(0.0)
    let xHurdle = mapX(8.5)

    // Grid lines
    for v in [-15, -10, -5, 0, 5, 10, 15, 20] {
        let xx = mapX(CGFloat(v))
        drawLineTop(ctx, x1: xx, yTop1: plotYTop, x2: xx, yTop2: plotBottom, heightCanvas: Hc, colorHex: (v == 0 ? "#94A3B8" : "#E2E8F0"), width: (v == 0 ? 3 : 2))
        if v != -15 && v != 20 {
            drawText(ctx, "\(v)%", x: xx, yTop: plotBottom + 14, heightCanvas: Hc, size: 21, bold: (v == 0), colorHex: "#4B5563", align: .center)
        }
    }

    // 8.50% Hurdle vertical dashed line
    drawLineTop(ctx, x1: xHurdle, yTop1: plotYTop - 16, x2: xHurdle, yTop2: plotBottom, heightCanvas: Hc, colorHex: "#0F766E", width: 4, dash: [10, 7])
    drawText(ctx, "8.5% Hurdle", x: xHurdle, yTop: plotYTop - 42, heightCanvas: Hc, size: 21, bold: true, colorHex: "#0F766E", align: .center)

    let rowStep = plotH / CGFloat(cases.count)
    let barH: CGFloat = 48

    for (i, c) in cases.enumerated() {
        let rowTop = plotYTop + CGFloat(i) * rowStep
        let barTop = rowTop + (rowStep - barH) / 2.0

        // Divider before CRM
        if i == 5 {
            drawLineTop(ctx, x1: 24, yTop1: rowTop - 2, x2: CGFloat(W - 24), yTop2: rowTop - 2, heightCanvas: Hc, colorHex: "#D97706", alpha: 0.5, width: 2, dash: [6, 6])
        }

        // Ticker label on left
        drawText(ctx, c.ticker, x: 132, yTop: barTop + 11, heightCanvas: Hc, size: 23, bold: true, colorHex: (c.ticker == "CRM" ? "#B45309" : "#1E2761"), align: .right)

        let xVal = mapX(c.irr)
        let bx = min(xZero, xVal)
        let bw = max(abs(xVal - xZero), 6)

        if c.ticker == "CRM" {
            // Hollow/outlined amber warning bar
            fillRectTop(ctx, x: bx, yTop: barTop, w: bw, h: barH, heightCanvas: Hc, colorHex: "#FEF3C7", radius: 6)
            strokeRectTop(ctx, x: bx, yTop: barTop, w: bw, h: barH, heightCanvas: Hc, colorHex: "#D97706", lineWidth: 4, radius: 6)
            // +4.7% inside bar, ✗ G4 FAIL cleanly to the right of the hurdle line
            drawText(ctx, c.label, x: (bx + xVal) / 2, yTop: barTop + 12, heightCanvas: Hc, size: 19, bold: true, colorHex: "#92400E", align: .center)
            drawText(ctx, c.tag!, x: xHurdle + 12, yTop: barTop + 12, heightCanvas: Hc, size: 20, bold: true, colorHex: "#B45309", align: .left)
        } else {
            fillRectTop(ctx, x: bx, yTop: barTop, w: bw, h: barH, heightCanvas: Hc, colorHex: c.color, radius: 6)
            let lblText = (c.tag != nil) ? "\(c.label) \(c.tag!)" : c.label
            if c.irr >= 0 {
                drawText(ctx, lblText, x: xVal + 10, yTop: barTop + 12, heightCanvas: Hc, size: 20, bold: true, colorHex: c.color, align: .left)
            } else if c.irr > -3.0 {
                drawText(ctx, lblText, x: xZero + 10, yTop: barTop + 12, heightCanvas: Hc, size: 20, bold: true, colorHex: c.color, align: .left)
            } else {
                drawText(ctx, lblText, x: bx - 10, yTop: barTop + 12, heightCanvas: Hc, size: 20, bold: true, colorHex: c.color, align: .right)
            }
        }
    }

    drawText(ctx, "Only MSFT clears r = 8.50%; CRM blocked at Gate 4 (5Y CAP)", x: CGFloat(W) / 2, yTop: 702, heightCanvas: Hc, size: 20, bold: true, colorHex: "#4B5563", align: .center)

    savePNG(ctx, to: "output/charts/case_study_irr_pe.png")
}

generateFunnelWaterfall()
generateMauboussinFade()
generateCaseStudyIRR()
