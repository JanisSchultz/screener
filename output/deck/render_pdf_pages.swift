import Foundation
import PDFKit
import AppKit

let pdfURL = URL(fileURLWithPath: "output/verify/deck_export.pdf")
guard let doc = PDFDocument(url: pdfURL) else {
    fputs("Failed to open PDF\n", stderr)
    exit(1)
}

print("PDF page count: \(doc.pageCount)")
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.0
    let w = Int(bounds.width * scale)
    let h = Int(bounds.height * scale)

    guard let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: w,
        pixelsHigh: h,
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    ) else {
        fputs("Failed bitmap rep on page \(i+1)\n", stderr)
        exit(1)
    }

    NSGraphicsContext.saveGraphicsState()
    guard let ctx = NSGraphicsContext(bitmapImageRep: rep) else { exit(1) }
    NSGraphicsContext.current = ctx
    let cg = ctx.cgContext
    cg.setFillColor(NSColor.white.cgColor)
    cg.fill(CGRect(x: 0, y: 0, width: w, height: h))
    cg.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: cg)
    NSGraphicsContext.restoreGraphicsState()

    guard let pngData = rep.representation(using: .png, properties: [:]) else { exit(1) }
    let outName = String(format: "output/verify/slide_%02d.png", i + 1)
    try pngData.write(to: URL(fileURLWithPath: outName))
    print("Wrote \(outName) (\(w)x\(h), \(pngData.count) bytes)")
}
