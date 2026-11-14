#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把配图压到指定体积（默认 10KB）以内，尽量保住画质与尺寸。

为什么需要它：真美/公众号用的封面图如果太大，加载慢、也占空间。
WebP 在极小体积下画质明显优于 JPEG/PNG，所以默认输出 WebP（真美媒体接口支持 WebP）。

策略（两步二分，不暴力降质）：
  1. 先按 --max-width 限制长边；
  2. 在当前尺寸下，按画质阶梯（82→15）找**第一个**能压进目标的画质 → 命中即停（保住最大尺寸 + 最高画质）；
  3. 若最低画质仍超标，则逐级缩小宽度（×0.85）重试，直到 --min-width 为止；
  4. 始终报告实测结果；达不到目标时**如实说达不到**，不假装成功。

⚠️ 必须用带 Pillow 的解释器运行：
   /Users/cresjq/.workbuddy/binaries/python/envs/default/bin/python3

用法：
    python3 shrink_image.py in.png --target-kb 10 --crop-bottom-pct 8
    python3 shrink_image.py in.png --target-kb 10 --max-width 900 --out cover.webp
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("❌ 需要 Pillow。请用 /Users/cresjq/.workbuddy/binaries/python/envs/default/bin/python3 运行本脚本。", file=sys.stderr)
    raise SystemExit(3)

QUALITY_LADDER = [82, 72, 62, 52, 44, 36, 30, 25, 20, 15]


def fit_quality(img: "Image.Image", fmt: str, target: int, ceiling: int = 88) -> tuple[int, int] | None:
    """二分找出「能压进 target 的最高画质」。返回 (bytes, quality) 或 None。"""
    lo, hi = 1, ceiling
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        n = len(encode(img, fmt, mid))
        if n <= target:
            best = (n, mid)
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def encode(img: "Image.Image", fmt: str, quality: int) -> bytes:
    buf = io.BytesIO()
    if fmt == "webp":
        img.save(buf, "WEBP", quality=quality, method=6)
    elif fmt == "jpeg":
        img.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    else:
        raise ValueError(fmt)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description="压缩配图到指定体积以内（默认 10KB）")
    ap.add_argument("src", help="输入图片路径")
    ap.add_argument("--out", default=None, help="输出路径（默认 <同名>.min.webp）")
    ap.add_argument("--target-kb", type=float, default=10.0, help="目标体积上限，单位 KB（默认 10）")
    ap.add_argument("--max-width", type=int, default=1200, help="长边上限（默认 1200）")
    ap.add_argument("--min-width", type=int, default=400, help="缩小时宽度下限（默认 400）")
    ap.add_argument("--quality-floor", type=int, default=45,
                    help="画质下限（默认 45）。宁可缩尺寸也不把画质压到这条线以下，保证观感。")
    ap.add_argument("--crop-bottom-pct", type=float, default=0.0, help="裁掉底部百分比（去 AI 水印用，如 8）")
    ap.add_argument("--format", choices=["webp", "jpeg"], default="webp", help="输出格式（默认 webp，同体积画质更好）")
    ap.add_argument("--json", action="store_true", help="只输出 JSON 结果")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.is_file():
        print(f"❌ 找不到输入图片：{src}", file=sys.stderr)
        return 2

    img = Image.open(src)
    orig_size = img.size
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    if args.crop_bottom_pct > 0:
        w, h = img.size
        keep = int(h * (1 - args.crop_bottom_pct / 100.0))
        img = img.crop((0, 0, w, keep))

    w, h = img.size
    if w > args.max_width:
        h = round(h * args.max_width / w)
        w = args.max_width
        img = img.resize((w, h), Image.LANCZOS)

    target_bytes = int(args.target_kb * 1024)
    # 策略：**优先保画质，不够再缩尺寸**。
    # 在当前尺寸下二分求「能压进目标的最高画质」；只要它不低于 quality-floor 就采用；
    # 否则缩尺寸（×0.85）重试；降到 min-width 仍不行，才允许突破 floor 兜底。
    chosen = None
    while True:
        r = fit_quality(img, args.format, target_bytes)
        if r and r[1] >= args.quality_floor:
            chosen = (r[0], img.copy(), r[1])
            break
        nw = round(img.size[0] * 0.85)
        if nw < args.min_width:
            if r:
                chosen = (r[0], img.copy(), r[1])
            break
        nh = round(img.size[1] * nw / img.size[0])
        img = img.resize((nw, nh), Image.LANCZOS)

    if chosen is None:
        r = fit_quality(img, args.format, target_bytes)
        if r is None:  # 连 q=1 都压不进：取当前编码结果兜底
            data = encode(img, args.format, 1)
            chosen = (len(data), img.copy(), 1)
        else:
            chosen = (r[0], img.copy(), r[1])

    size, out_img, quality = chosen
    out = Path(args.out) if args.out else src.with_suffix("").with_name(
        src.stem + ".min." + ("webp" if args.format == "webp" else "jpg"))
    data = encode(out_img, args.format, quality)
    size = len(data)
    out.write_bytes(data)

    ok = size <= target_bytes
    report = {
        "ok": ok,
        "path": str(out),
        "bytes": size,
        "kb": round(size / 1024, 2),
        "target_kb": args.target_kb,
        "width": out_img.size[0],
        "height": out_img.size[1],
        "format": args.format,
        "quality": quality,
        "original_size": list(orig_size),
        "original_kb": round(src.stat().st_size / 1024, 2),
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        flag = "✅" if ok else "⚠️"
        print(f"{flag} {out}")
        print(f"   {report['original_kb']}KB {tuple(orig_size)} → {report['kb']}KB {report['width']}×{report['height']} "
              f"({args.format}, q={quality})")
        if not ok:
            print(f"   ⚠️ 未达到 {args.target_kb}KB 目标（最低止损：宽度 {args.min_width}px、画质 15）。"
                  f"如需更小可调低 --min-width，但会明显损画质。")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
