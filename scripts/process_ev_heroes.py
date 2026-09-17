#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程石材製品型錄 — Hero 主圖去水印 + 雙格式落盤
=================================================
處理 ImageGen 生成的 PNG（右下角平台水印），裁切重採樣去水印，
亮度校正（適配站內 .product-hero-bg 的 filter:brightness(.5)），
輸出 jpg(quality 92) + webp(quality 88) 到 images/products/engineering-stone-varieties/。

用法：
  python3 scripts/process_ev_heroes.py          # 處理目錄內所有匹配 PNG
  python3 scripts/process_ev_heroes.py --keep    # 處理後保留 PNG（不移到備份）

映射：ImageGen 檔名唯一前綴 -> 目標 slug（landing 特殊）
"""
import os, glob, sys, shutil
import numpy as np
from PIL import Image

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "images/products/engineering-stone-varieties")
BACKUP = "/tmp/ev-png-backup"
KEEP = "--keep" in sys.argv

# (ImageGen 檔名前綴, 目標 slug；landing 用 "landing")
PREFIX_SLUG = [
    ("BollardBallHero",      "bollard-ball"),
    ("BollardPostHero",      "bollard-post"),
    ("BalustradeHero",       "stone-balustrade"),
    ("NameStoneHero",        "engraved-name-stone"),
    ("StonePierHero",        "carved-stone-pier"),
    ("FlamedPavingHero",     "flamed-paving"),
    ("BushHammeredHero",     "bushhammered-paving"),
    ("TactileHero",          "tactile-paving"),
    ("CobblestoneHero",      "cobblestone"),
    ("CrazyPavingHero",      "crazy-paving"),
    ("CurbStoneHero",        "curb-stone"),
    ("CurvedCurbHero",       "curved-curb"),
    ("TreePitHero",          "tree-pit-stone"),
    ("CopingStoneHero",      "coping-stone"),
    ("StepTreadHero",        "step-tread"),
    ("DrainGrateHero",       "stone-drain-grate"),
    ("CurtainWallHero",      "curtain-wall-panel"),
    ("MushroomStoneHero",    "mushroom-stone"),
    ("EngVarietyLandingHero","landing"),
]

# Hero 主圖：裁掉右下角水印區，放大回 1536×986
CROP = (0, 0, 1380, 886)
OUT_SIZE = (1536, 986)
TARGET_MEAN = 145.0   # 預濾鏡（CSS brightness .5 後約 72，落入 64–95 區間）


def correct_mean(im):
    """自適應亮度：將預濾鏡平均亮度拉到 ~TARGET_MEAN（只提亮不壓暗）。"""
    arr = np.asarray(im, dtype=np.float32)
    m = float(arr.mean())
    if m <= 1:
        return im
    if m >= TARGET_MEAN:
        return im  # 已夠亮，不動
    gamma = np.log(TARGET_MEAN / 255.0) / np.log(m / 255.0)
    if gamma > 1.0:
        gamma = 1.0
    lut = (np.arange(256, dtype=np.float32) / 255.0) ** gamma * 255.0
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return Image.fromarray(lut[arr.astype(np.uint8)])


def find_png(prefix):
    ps = sorted(glob.glob(os.path.join(DIR, prefix + "*.png")),
                key=lambda p: os.path.getmtime(p))
    return ps[-1] if ps else None


def process(prefix, slug):
    png = find_png(prefix)
    if not png:
        print("  ⚠️ 找不到 %s 的 PNG（前綴 %s）" % (slug, prefix))
        return False
    im = Image.open(png).convert("RGB")
    base = im.crop(CROP).resize(OUT_SIZE, Image.LANCZOS)
    before = float(np.asarray(base).mean())
    out = correct_mean(base)
    after = float(np.asarray(out).mean())
    jpg = os.path.join(DIR, slug + "-hero.jpg")
    webp = os.path.join(DIR, slug + "-hero.webp")
    out.save(jpg, "JPEG", quality=92, optimize=True, progressive=True)
    out.save(webp, "WEBP", quality=88, method=6)
    print("  ✅ %-22s mean %5.1f -> %5.1f | %s / %s" %
          (slug, before, after, os.path.basename(jpg), os.path.basename(webp)))
    if not KEEP:
        os.makedirs(BACKUP, exist_ok=True)
        shutil.move(png, os.path.join(BACKUP, os.path.basename(png)))
    return True


def main():
    os.makedirs(DIR, exist_ok=True)
    print("處理目錄：%s" % DIR)
    ok = 0
    for prefix, slug in PREFIX_SLUG:
        if process(prefix, slug):
            ok += 1
    print("完成 %d/%d" % (ok, len(PREFIX_SLUG)))


if __name__ == "__main__":
    main()
