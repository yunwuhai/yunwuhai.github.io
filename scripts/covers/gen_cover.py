# -*- coding: utf-8 -*-
"""为每个分区与每篇文章生成 1200x630 的装饰性封面图。

用法（在仓库根目录）：
    python scripts/covers/gen_cover.py

扫描 content/posts：
  * 含 _index.md 的目录 → 分区封面（纯装饰）
  * 含 index.md 的 leaf bundle → 文章封面（纯装饰）
输出 <目录>/cover.jpg。

设计要点：
  封面**不写任何文字**。Stack 的列表卡与文章页都会在图片下方再渲染标题、
  分类与标签，图上再画文字就变成重复信息（同一标题在一张卡里出现两次）。
  所以这里只做渐变 + 几何纹理，靠 seed（crc32，可复现）让每篇图案不同。
"""
import os
import math
import zlib
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTS = os.path.join(ROOT, "content", "posts")
W, H = 1200, 630

# 顶层分区配色
TOP_COLORS = {
    "嵌入式": ("#1e3a5f", "#2d6a9f"),
    "算法": ("#3b2f63", "#6b4fa0"),
    "网络安全": ("#1f3d34", "#2f7a5e"),
    "工具与环境": ("#3a3f2a", "#6b7448"),
    "桌面端": ("#2f3640", "#57606f"),
    "杂谈": ("#3d3025", "#8a6a4a"),
}

# 子分区微调配色
SUB_COLORS = {
    "Arduino": ("#24547f", "#3a86c0"),
    "C_CPP": ("#1a3352", "#2a5f93"),
    "USB": ("#28587f", "#3f88b8"),
    "硬件设计": ("#234a70", "#3877a8"),
    "题目": ("#443670", "#7757ad"),
    "自制脚本语言": ("#33285a", "#5c4490"),
    "CSharp": ("#353d4a", "#647082"),
    "工具链": ("#274a5c", "#3f7d96"),
}
DEFAULT_COLOR = ("#333a45", "#5a6570")


def hex2rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(c1, c2):
    a, b = hex2rgb(c1), hex2rgb(c2)
    img = Image.new("RGB", (W, H), a)
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix(a, b, (y / (H - 1)) * 0.92))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(-H, W, 2):
        t = (i + H) / (W + H)
        od.line([(i, 0), (i + H, H)],
                fill=(255, 255, 255, int(30 * math.sin(t * math.pi))), width=2)
    ov = ov.filter(ImageFilter.GaussianBlur(2.0))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def pattern(img, seed):
    """按 seed 选一种几何纹理，让同一分区下的文章封面彼此可区分。"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    kind = seed % 4

    if kind == 0:                                    # 同心圆
        cx = 980 + (seed % 5) * 24
        cy = 120 + (seed % 7) * 14
        for r in range(80, 520, 54):
            d.ellipse([cx - r, cy - r, cx + r, cy + r],
                      outline=(255, 255, 255, 20), width=2)
    elif kind == 1:                                  # 斜条纹
        for x in range(-H, W, 64):
            d.line([(x, 0), (x + H, H)], fill=(255, 255, 255, 16), width=3)
    elif kind == 2:                                  # 点阵
        for gx in range(0, W + 40, 46):
            for gy in range(0, H + 40, 46):
                if (gx // 46 + gy // 46 + seed) % 3 == 0:
                    d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2],
                              fill=(255, 255, 255, 34))
    else:                                            # 波浪
        for k in range(4):
            base = 120 + k * 110 + (seed % 5) * 12
            for x in range(0, W, 8):
                y = base + math.sin(x / 190.0 + k + seed % 6) * 46
                d.ellipse([x, y, x + 9, y + 9], fill=(255, 255, 255, 22))

    lay = lay.filter(ImageFilter.GaussianBlur(0.7))
    return Image.alpha_composite(img, lay)


def blobs(img, seed):
    """两团柔和的亮色光斑，按 seed 摆放，制造纵深。"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    spots = [
        (60 + (seed * 37) % 380, H - 90 - (seed * 53) % 160, 300, 34),
        (W - 200 - (seed * 61) % 420, 40 + (seed * 29) % 240, 240, 26),
    ]
    for cx, cy, r, a in spots:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a))
    lay = lay.filter(ImageFilter.GaussianBlur(80))
    return Image.alpha_composite(img, lay)


def render(c1, c2, seed=0):
    img = gradient(c1, c2)
    img = blobs(img, seed)
    img = pattern(img, seed)

    # 左上一条细亮边，让卡片裁切后仍有层次
    bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(bar).rounded_rectangle([40, 46, 46, H - 46], radius=3,
                                          fill=(255, 255, 255, 90))
    img = Image.alpha_composite(img, bar)
    return img.convert("RGB")


def save(img, out, quality=88):
    img.save(out, "JPEG", quality=quality, optimize=True, progressive=True)


def colors_for(rel_dir):
    parts = rel_dir.split("/") if rel_dir else []
    top = parts[0] if parts else ""
    sub = parts[1] if len(parts) > 1 else ""
    if sub in SUB_COLORS:
        return SUB_COLORS[sub]
    return TOP_COLORS.get(top, DEFAULT_COLOR)


def main():
    made_a = made_s = 0
    for dirpath, dirnames, filenames in os.walk(POSTS):
        dirnames.sort()
        rel_dir = os.path.relpath(dirpath, POSTS).replace(os.sep, "/")
        if rel_dir == ".":
            rel_dir = ""
        c1, c2 = colors_for(rel_dir)
        seed = zlib.crc32(rel_dir.encode("utf-8")) % 97

        if "_index.md" in filenames:
            img = render(c1, c2, seed)
            save(img, os.path.join(dirpath, "cover.jpg"))
            made_s += 1

        if "index.md" in filenames:
            img = render(c1, c2, seed)
            save(img, os.path.join(dirpath, "cover.jpg"))
            made_a += 1

    print("sections:", made_s, "articles:", made_a)


if __name__ == "__main__":
    main()
