#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从源 PNG 生成网站多尺寸图标：
- 生成 favicon.ico（含 16/32/48/64/128/256 多尺寸）
- 生成多尺寸 PNG：favicon-16x16.png、favicon-32x32.png、...、favicon-256x256.png
- 生成 Apple Touch Icon：apple-touch-icon.png（180x180）

用法：
python scripts/image_tools/generate_favicons.py --src frontend/public/dataverse_logo.png --out frontend/public
"""
import argparse
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops

SIZES_ICO = [16, 32, 48, 64, 128, 256]
SIZES_PNG = [16, 32, 48, 64, 128, 192, 256]
APPLE_TOUCH_SIZE = 180


def trim_to_content(img: Image.Image, alpha_threshold: int = 10, pad: int = 0) -> Image.Image:
    """裁剪掉透明边缘，使主体尽量充满画布。"""
    a = img.split()[3]
    mask = a.point(lambda p: 255 if p > alpha_threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img.width, x1 + pad)
    y1 = min(img.height, y1 + pad)
    return img.crop((x0, y0, x1, y1))


def compose_square(content: Image.Image, size: int, fill_ratio: float = 0.92, bg=(0, 0, 0, 0)) -> Image.Image:
    """将内容图像按给定填充比例放入正方形透明画布。fill_ratio 越大，主体看起来越大。"""
    canvas = Image.new('RGBA', (size, size), bg)
    target = int(size * fill_ratio)
    # 依比例缩放以适配 target 尺寸
    w, h = content.size
    if w >= h:
        new_w = target
        new_h = max(1, round(h * target / w))
    else:
        new_h = target
        new_w = max(1, round(w * target / h))
    resized = content.resize((new_w, new_h), Image.LANCZOS)
    x = (size - new_w) // 2
    y = (size - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    return canvas


def generate_all(src: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert('RGBA')
    # 先裁掉多余透明边，使主体更“顶格”
    trimmed = trim_to_content(img, alpha_threshold=10, pad=2)

    def add_outline(img: Image.Image, color=(0, 0, 0, 255), width=1) -> Image.Image:
        """对非透明区域添加外描边，提升小图标可读性"""
        # 使用 alpha 通道做膨胀
        a = img.split()[3]
        # 膨胀：MaxFilter 近似形态学膨胀
        dilated = a.filter(ImageFilter.MaxFilter(size=width * 2 + 1))
        # 描边区域 = 膨胀 - 原 alpha
        outline_mask = Image.eval(dilated, lambda px: px)  # 复制
        outline_mask = ImageChops.subtract(outline_mask, a)
        # 生成纯色描边层
        stroke_layer = Image.new('RGBA', img.size, color)
        # 底为原图，上叠描边（以描边mask控制）
        base = img.copy()
        base.paste(stroke_layer, (0, 0), outline_mask)
        return base

    # 生成 PNG 多尺寸（小尺寸使用更高填充比例，使视觉更大）
    for size in SIZES_PNG:
        if size <= 32:
            fill = 0.98
        elif size <= 48:
            fill = 0.96
        else:
            fill = 0.92
        composed = compose_square(trimmed, size, fill_ratio=fill)
        if size <= 48:
            stroke_w = 2 if size <= 32 else 2
            composed = add_outline(composed, color=(0, 0, 0, 180), width=stroke_w)
        (out_dir / f"favicon-{size}x{size}.png").write_bytes(b"")  # 预创建避免权限问题
        composed.save(out_dir / f"favicon-{size}x{size}.png", format='PNG')

    # 生成 Apple Touch Icon
    apple = compose_square(trimmed, APPLE_TOUCH_SIZE, fill_ratio=0.92)
    apple.save(out_dir / 'apple-touch-icon.png', format='PNG')

    # 生成 ICO（多尺寸）
    ico_sizes = [(s, s) for s in SIZES_ICO]
    # ICO 使用最大尺寸作为基底，浏览器通常也会优先选用 PNG 链接的小尺寸
    base = compose_square(trimmed, max(SIZES_ICO), fill_ratio=0.92)
    base.save(out_dir / 'favicon.ico', sizes=ico_sizes)


def main():
    p = argparse.ArgumentParser(description='生成网站多尺寸图标')
    p.add_argument('--src', required=True, help='源 PNG 路径，例如 frontend/public/dataverse_logo.png')
    p.add_argument('--out', required=True, help='输出目录，例如 frontend/public')
    args = p.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out)

    if not src.exists():
        raise SystemExit(f'[ERROR] 源文件不存在: {src}')

    generate_all(src, out_dir)
    print('[DONE] 已生成 favicon.ico / 各尺寸 PNG / apple-touch-icon.png')


if __name__ == '__main__':
    main()
