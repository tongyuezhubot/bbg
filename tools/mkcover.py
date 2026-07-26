#!/usr/bin/env python3
"""生成分享卡片 og.png（1200×630）与站点图标。

像素场景先画在低分辨率画布上，再用最近邻整数倍放大，保持硬边像素风；
标题文字在最终分辨率上用 Georgia / 黑体绘制，跟站内 h1 排版一致。

用法：python3 tools/mkcover.py
输出：og.png, icon-512.png, icon-192.png, favicon.png（仓库根目录）
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 调色板（对齐 index.html 的 CSS 变量）────────────────────────
WALL      = (48, 37, 27)
WALL_LIT  = (66, 51, 36)
WAINSCOT  = (61, 39, 22)
FLOOR     = (99, 63, 36)
FLOOR_DK  = (84, 52, 29)
FRAME     = (107, 66, 38)
FRAME_DK  = (72, 44, 25)
CREAM     = (222, 214, 198)
INK       = (35, 32, 26)
AMBER     = (181, 118, 28)
AMBER_LIT = (232, 163, 61)
RULE      = (58, 52, 43)

BOX_HUES = [(168, 74, 62), (78, 106, 96), (196, 148, 66),
            (92, 88, 128), (170, 112, 74), (108, 124, 78)]

SW, SH, SCALE = 200, 105, 6          # 200×105 ×6 = 1200×630


def rect(d, x0, y0, x1, y1, c):
    """闭区间矩形，按像素格算。"""
    d.rectangle([x0, y0, x1, y1], fill=c)


# ── 场景 ────────────────────────────────────────────────────
def draw_scene():
    img = Image.new("RGB", (SW, SH), WALL)
    d = ImageDraw.Draw(img)

    HORIZON = 58
    rect(d, 0, 0, SW - 1, HORIZON - 1, WALL)
    rect(d, 0, HORIZON - 8, SW - 1, HORIZON - 1, WAINSCOT)     # 墙裙
    rect(d, 0, HORIZON - 9, SW - 1, HORIZON - 9, FRAME)
    rect(d, 0, HORIZON, SW - 1, SH - 1, FLOOR)                 # 地板
    rect(d, 0, HORIZON, SW - 1, HORIZON + 1, (58, 36, 21))     # 踢脚线
    for y in range(HORIZON + 4, SH, 7):                        # 地板缝
        rect(d, 0, y, SW - 1, y, FLOOR_DK)

    def shelf(x0, x1, y0, y1):
        rect(d, x0, y0, x1, y1, FRAME_DK)
        rect(d, x0 + 2, y0 + 2, x1 - 2, y1 - 2, WALL_LIT)
        rows = 3
        h = (y1 - y0 - 4) // rows
        for r in range(rows):
            sy = y0 + 2 + r * h
            rect(d, x0 + 2, sy + h - 1, x1 - 2, sy + h - 1, FRAME)
            # 一排竖着的游戏盒
            bx = x0 + 4
            i = r * 3
            while bx < x1 - 5:
                w = 2 + (i % 3)
                hue = BOX_HUES[i % len(BOX_HUES)]
                rect(d, bx, sy + 2, bx + w - 1, sy + h - 2, hue)
                rect(d, bx, sy + 2, bx, sy + h - 2,
                     tuple(min(255, v + 26) for v in hue))       # 盒脊高光
                bx += w + 1
                i += 1

    # 内容全部靠右，左半边留给标题文字
    shelf(112, 160, 8, 44)
    shelf(166, 196, 8, 44)

    # 墙上的小黑板菜单
    rect(d, 86, 12, 106, 32, FRAME_DK)
    rect(d, 88, 14, 104, 30, (34, 44, 40))
    for i, w in enumerate((12, 8, 13)):
        rect(d, 91, 17 + i * 5, 91 + w, 17 + i * 5, (120, 132, 122))

    # ── 吊灯 + 光晕 ────────────────────────────────────────
    glow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for cx in (128, 180):
        rect(d, cx, 0, cx, 11, FRAME_DK)                        # 灯线
        rect(d, cx - 5, 12, cx + 5, 12, AMBER)                  # 灯罩
        rect(d, cx - 4, 13, cx + 4, 14, AMBER_LIT)
        rect(d, cx - 2, 15, cx + 2, 16, (255, 236, 190))
        for r, a in ((26, 30), (18, 34), (11, 46), (6, 70)):
            gd.ellipse([cx - r, 14 - r, cx + r, 14 + r],
                       fill=(255, 198, 110, a))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)

    # ── 人物：头 6×6、身 8×7，眼睛 1×2 扁眼（bbg 全员统一）──
    def person(x, y, shirt, hair, skin=(226, 190, 158), flip=False):
        rect(d, x, y + 6, x + 7, y + 12, shirt)                 # 身体
        rect(d, x, y + 6, x, y + 12, tuple(max(0, v - 24) for v in shirt))
        rect(d, x + 1, y, x + 6, y + 5, skin)                   # 头
        rect(d, x, y, x + 7, y + 1, hair)                       # 头发
        rect(d, x, y, x + 1, y + 3, hair)
        rect(d, x + 6, y, x + 7, y + 3, hair)
        ex = x + 2 if not flip else x + 3
        rect(d, ex, y + 3, ex, y + 4, INK)                      # 眼 1×2
        rect(d, ex + 3, y + 3, ex + 3, y + 4, INK)

    # ── 主桌：两人对坐开局 ──────────────────────────────
    TX0, TX1, TY = 112, 164, 78
    person(118, TY - 14, (168, 74, 62), (48, 34, 26))
    person(150, TY - 14, (78, 106, 96), (32, 28, 24), flip=True)

    rect(d, TX0, TY, TX1, TY + 9, FRAME)                        # 桌面
    rect(d, TX0, TY, TX1, TY + 1, (132, 84, 50))
    rect(d, TX0 + 3, TY + 10, TX0 + 5, TY + 18, FRAME_DK)       # 桌腿
    rect(d, TX1 - 5, TY + 10, TX1 - 3, TY + 18, FRAME_DK)

    bx0, by0 = TX0 + 14, TY + 2                                 # 桌上棋盘
    for r in range(3):
        for c in range(8):
            col = (206, 196, 172) if (r + c) % 2 == 0 else (120, 104, 82)
            rect(d, bx0 + c * 3, by0 + r * 2, bx0 + c * 3 + 2, by0 + r * 2 + 1, col)
    rect(d, TX0 + 5, TY + 3, TX0 + 7, TY + 5, CREAM)            # 骰子
    rect(d, TX0 + 6, TY + 4, TX0 + 6, TY + 4, INK)
    rect(d, TX1 - 8, TY + 3, TX1 - 5, TY + 6, (196, 148, 66))   # 卡堆

    # ── 右侧小桌 ──────────────────────────────────────────
    person(178, 60, (196, 148, 66), (60, 40, 28))
    rect(d, 168, 74, 196, 81, FRAME)
    rect(d, 168, 74, 196, 75, (132, 84, 50))
    rect(d, 180, 82, 183, 90, FRAME_DK)
    rect(d, 172, 76, 175, 78, (168, 74, 62))

    # ── 左侧沙发区：在压暗层下面，只作纵深，不抢文字 ──────
    rect(d, 10, 86, 76, 101, (86, 66, 55))                      # 地毯
    rect(d, 13, 88, 73, 99, (104, 80, 66))
    rect(d, 16, 68, 60, 82, (78, 88, 100))                      # 沙发
    rect(d, 16, 66, 60, 69, (94, 106, 118))
    rect(d, 16, 68, 19, 82, (64, 74, 86))
    rect(d, 57, 68, 60, 82, (64, 74, 86))
    person(32, 54, (168, 132, 96), (44, 32, 26))

    return img


# ── 字体 ────────────────────────────────────────────────────
SUP = "/System/Library/Fonts/Supplemental/"


def font(path, size):
    return ImageFont.truetype(path, size)


def cjk(size, weight="Medium"):
    return ImageFont.truetype(f"/System/Library/Fonts/STHeiti {weight}.ttc", size)


def make_og():
    scene = draw_scene().resize((SW * SCALE, SH * SCALE), Image.NEAREST)

    # 左侧压暗成近实色文字区，560px 后快速淡出，让右边场景露出来
    scrim = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    W, H = scene.size
    SOLID, FADE = 540, 760
    for x in range(W):
        t = 1.0 if x < SOLID else max(0.0, (FADE - x) / (FADE - SOLID))
        sd.line([(x, 0), (x, H)], fill=(20, 15, 11, int(242 * t ** 0.85)))
    img = Image.alpha_composite(scene.convert("RGBA"), scrim).convert("RGB")
    d = ImageDraw.Draw(img)

    L = 76
    d.text((L, 132), "Welcome to", font=font(SUP + "Georgia Italic.ttf", 42),
           fill=(146, 136, 118))
    d.text((L - 4, 178), "BBG", font=font(SUP + "Georgia Bold.ttf", 104), fill=CREAM)
    d.text((L - 4, 292), "Boardgame",
           font=font(SUP + "Georgia Bold Italic.ttf", 92), fill=AMBER_LIT)

    d.text((L, 424), "桌游店 · 平面图", font=cjk(36), fill=(180, 170, 150))
    d.text((L, 470), "营业中的一天", font=cjk(36), fill=(180, 170, 150))

    # Open 小灯
    ly = 536
    d.ellipse([L + 1, ly + 1, L + 17, ly + 17], fill=AMBER_LIT)
    d.ellipse([L - 5, ly - 5, L + 23, ly + 23], outline=(122, 86, 34), width=2)
    d.text((L + 38, ly - 5), "O P E N", font=font(SUP + "Georgia.ttf", 28),
           fill=(198, 152, 94))

    img.save(os.path.join(ROOT, "og.png"), optimize=True)
    # 落地页背景用同一张场景，但不烤字、不压暗
    scene.save(os.path.join(ROOT, "door.png"), optimize=True)
    return img.size


# ── 图标：32×32 底稿，整数倍放大 ─────────────────────────────
def draw_icon():
    N = 32
    img = Image.new("RGB", (N, N), (30, 24, 18))
    d = ImageDraw.Draw(img)

    # 暖光底盘（去掉吊灯，32px 下少一个元素更好认）
    for r, c in ((15, (44, 33, 22)), (12, (60, 43, 26)), (8, (84, 58, 30)),
                 (4, (116, 78, 34))):
        d.ellipse([16 - r, 15 - r, 16 + r, 15 + r], fill=c)

    # 棋子（meeple）：逐行描出剪影，四周留边不顶到画布
    for y0, y1, x0, x1 in (
            (4, 4, 13, 18), (5, 9, 12, 19), (10, 10, 13, 18),   # 头
            (11, 12, 15, 16),                                   # 脖子
            (13, 17, 6, 25), (18, 18, 8, 23),                   # 平举双臂
            (19, 23, 11, 20),                                   # 躯干
            (24, 28, 10, 14), (24, 28, 17, 21)):                # 双腿
        rect(d, x0, y0, x1, y1, CREAM)
    SHADE = (176, 168, 150)                                     # 左侧暗面
    for y0, y1, x in ((5, 9, 12), (13, 17, 6), (19, 23, 11), (24, 28, 10)):
        rect(d, x, y0, x, y1, SHADE)

    rect(d, 0, 23, 4, 28, (196, 148, 66))                       # 骰子
    rect(d, 0, 23, 4, 23, (226, 184, 106))
    rect(d, 1, 25, 1, 25, INK)
    rect(d, 3, 27, 3, 27, INK)
    rect(d, 27, 24, 31, 28, (168, 74, 62))                      # 卡堆
    rect(d, 27, 24, 31, 24, (200, 108, 92))
    return img


def make_icons():
    base = draw_icon()
    out = []
    for size, name in ((512, "icon-512.png"), (192, "icon-192.png"), (32, "favicon.png")):
        base.resize((size, size), Image.NEAREST).save(
            os.path.join(ROOT, name), optimize=True)
        out.append(name)
    return out


if __name__ == "__main__":
    print("og.png", make_og())
    print("icons", make_icons())
