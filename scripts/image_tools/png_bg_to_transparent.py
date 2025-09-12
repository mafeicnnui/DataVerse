#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将指定目录下的 PNG 图片背景色替换为透明：
- 通过四角像素推断背景主色（也可通过 --bg 手动指定）
- 支持阈值相似度判断（--threshold，默认 245，越小越严格）
- 会在同级创建 _backup_png/ 目录保存原图备份

使用示例：
python scripts/image_tools/png_bg_to_transparent.py frontend/public --threshold 245
python scripts/image_tools/png_bg_to_transparent.py frontend/public --bg 255,255,255
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    print("[ERROR] 需要 Pillow 库，请先安装：pip install Pillow", file=sys.stderr)
    raise


def parse_color(s: str):
    try:
        parts = [int(x) for x in s.split(',')]
        if len(parts) != 3:
            raise ValueError
        for v in parts:
            if not (0 <= v <= 255):
                raise ValueError
        return tuple(parts)
    except Exception:
        raise argparse.ArgumentTypeError("颜色应为R,G,B，范围0-255，例如：255,255,255")


def color_distance(c1, c2):
    # 简单曼哈顿距离，足够用于背景近似判断
    return abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2]-c2[2])


def guess_bg_color(img: Image.Image):
    w, h = img.size
    pixels = img.convert('RGB').load()
    corners = [
        pixels[0, 0],
        pixels[w-1, 0],
        pixels[0, h-1],
        pixels[w-1, h-1],
    ]
    # 取出现次数最多的角作为背景色
    from collections import Counter
    return Counter(corners).most_common(1)[0][0]


def make_transparent(img_path: Path, backup_dir: Path, threshold: int, bg_color=None):
    img = Image.open(img_path).convert('RGBA')

    if bg_color is None:
        bg_color = guess_bg_color(img)

    # 备份原图
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / img_path.name
    if not backup_path.exists():
        img.save(backup_path)

    datas = img.getdata()
    new_data = []

    for item in datas:
        r, g, b, a = item
        if color_distance((r, g, b), bg_color) <= (3 * (255 - threshold)):
            # 与背景色近似 -> 透明
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    # 覆盖保存
    img.save(img_path)
    return bg_color


def main():
    parser = argparse.ArgumentParser(description='将 PNG 背景色置为透明')
    parser.add_argument('directory', help='目标目录，例如 frontend/public')
    parser.add_argument('--threshold', type=int, default=245,
                        help='背景相似度阈值(0-255，越大越宽松，默认245)')
    parser.add_argument('--bg', type=parse_color, default=None,
                        help='手动指定背景色 R,G,B，例如 255,255,255')
    args = parser.parse_args()

    target_dir = Path(args.directory)
    if not target_dir.exists():
        print(f"[ERROR] 目录不存在: {target_dir}")
        sys.exit(1)

    pngs = list(target_dir.rglob('*.png'))
    if not pngs:
        print(f"[INFO] 未找到 PNG：{target_dir}")
        return

    backup_dir = target_dir / '_backup_png'
    count = 0
    for p in pngs:
        try:
            bgc = make_transparent(p, backup_dir, args.threshold, args.bg)
            print(f"[OK] {p} 背景≈{bgc} -> 透明")
            count += 1
        except Exception as e:
            print(f"[FAIL] {p}: {e}")

    print(f"[DONE] 处理完成，共 {count} 个 PNG。备份目录：{backup_dir}")


if __name__ == '__main__':
    main()
