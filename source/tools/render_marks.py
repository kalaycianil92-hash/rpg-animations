#!/usr/bin/env python3
"""Draws a strip's frames with the weapons and the 'hand over the grip' layer exactly the way the test page does (a port of drawItemOn / buildHand / drawGearTo in warrior-vs-goblin-test.src.html),
so a hand size (the circle round each mark that decides which pixels count as the hand) can be judged at full resolution, offline (2026-11-07).

  python source/tools/render_marks.py <strip.png> <marks.json> --frames 1,5,10 --fist 3,2,1 --out sheet.png [--zoom 3] [--focus off] [--crop 0.14]

  --fist    hand sizes in percent of the frame width (the page's "Hand size"; radius = round(percent / 100 x frame width)); one row per size, one column per frame
  --crop    keep only this share of the frame around the two marks (default: the box round both marks, 0.35 of the frame wide minimum)
"""
import argparse
import json
import pathlib

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]
ASSETS = ROOT / "source" / "assets"
CROSS = ndi.generate_binary_structure(2, 1)


def load_item(name):
    return Image.open(ASSETS / (name + ".png")).convert("RGBA")


def draw_item(canvas, im, length, pivot, an, W, H):
    """canvas: RGBA PIL image the size of the frame; the item scaled to length x W high, its `pivot` point at the mark, rotated an['a'] degrees clockwise"""
    sc = length * W / im.height
    w, h = max(1, int(round(im.width * sc * (an.get("w") or 1)))), max(1, int(round(im.height * sc)))
    it = im.resize((w, h), Image.LANCZOS)
    big = int(2 * max(w, h)) + 8
    tmp = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    px, py = w / 2.0, pivot * h
    ox, oy = big // 2 - px, big // 2 - py
    tmp.alpha_composite(it, (int(round(ox)), int(round(oy))))
    tmp = tmp.rotate(-an["a"], resample=Image.BICUBIC, center=(big // 2, big // 2))
    paste_clipped(canvas, tmp, int(round(an["x"] * W - big // 2)), int(round(an["y"] * H - big // 2)))


def paste_clipped(canvas, tile, x, y):
    cw, ch = canvas.size
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cw, x + tile.width), min(ch, y + tile.height)
    if x1 <= x0 or y1 <= y0:
        return
    canvas.alpha_composite(tile.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def build_hand(frame, an, rad):
    """buildHand of the page: the dominant skin hue inside a circle of `rad` px round the mark, the pixels of that hue connected to the mark, grown 2 px for the outline. Returns (patch RGBA, x0, y0) or None"""
    fh, fw = frame.shape[:2]
    cx, cy = int(round(an["x"] * fw)), int(round(an["y"] * fh))
    pad = 3
    x0, y0 = max(0, cx - rad - pad), max(0, cy - rad - pad)
    x1, y1 = min(fw, cx + rad + pad + 1), min(fh, cy + rad + pad + 1)
    w, h = x1 - x0, y1 - y0
    if w < 3 or h < 3:
        return None
    d = frame[y0:y1, x0:x1].astype(np.int32).copy()
    ox, oy = cx - x0, cy - y0
    yy, xx = np.mgrid[0:h, 0:w]
    dd = (xx - ox) ** 2 + (yy - oy) ** 2
    r2 = rad * rad
    seed2 = r2 * 0.3
    R, G, B, A = d[..., 0], d[..., 1], d[..., 2], d[..., 3]
    mx = np.maximum(np.maximum(R, G), B)
    mn = np.minimum(np.minimum(R, G), B)
    dl = mx - mn
    ish = (dd <= r2) & (A >= 128) & (dl > 0) & (dl * 1.0 / np.maximum(mx, 1) >= 0.2) & (mx >= 90)
    dls = np.where(dl == 0, 1, dl)
    hue = np.where(mx == R, ((G - B) / dls) % 6, np.where(mx == G, (B - R) / dls + 2, (R - G) / dls + 4)) * 60.0
    hue = np.where(hue < 0, hue + 360, hue)
    seedpix = ish & (dd <= seed2) & (A >= 200)
    cnt = np.zeros(12)
    sins = np.zeros(12)
    coss = np.zeros(12)
    for b in range(12):
        sel = seedpix & (np.floor(hue / 30).astype(int) % 12 == b)
        cnt[b] = sel.sum()
        sins[b] = np.sin(np.radians(hue[sel])).sum()
        coss[b] = np.cos(np.radians(hue[sel])).sum()
    near = lambda j: [(j + 11) % 12, j, (j + 1) % 12]
    best, bs = -1, 0
    for b in range(12):
        sc = sum(cnt[j] for j in near(b))
        if sc > bs:
            bs, best = sc, b
    if best < 0 or bs < 8:
        return None
    ss = sum(sins[j] for j in near(best))
    cs = sum(coss[j] for j in near(best))
    ref = np.degrees(np.arctan2(ss, cs)) % 360
    df = np.abs(hue - ref)
    df = np.where(df > 180, 360 - df, df)
    ok = ish & (df <= 22)
    seeds = ok & (dd <= seed2)
    lab, n = ndi.label(ok, structure=np.ones((3, 3)))
    keep_ids = np.unique(lab[seeds])
    keep = np.isin(lab, keep_ids[keep_ids > 0])
    if not keep.any():
        return None
    m = ndi.binary_dilation(keep, structure=CROSS, iterations=3)
    m = ndi.binary_erosion(m, structure=CROSS, border_value=1)
    patch = d.copy()
    patch[..., 3] = np.where(m, patch[..., 3], 0)
    return Image.fromarray(patch.astype(np.uint8)), x0, y0


def render(frame_rgba, set_, i, fist_pct, W=512, H=512):
    body = Image.fromarray(frame_rgba)
    back = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    front = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rad = max(2, int(round(fist_pct / 100.0 * W)))
    marks = {}
    for tk in ("main", "off"):
        an = set_["tracks"][tk][i]
        cfg = set_["main"] if tk == "main" else set_["off"]
        if not an or an.get("hide"):
            continue
        marks[tk] = (an, cfg)
        draw_item(front if an.get("front") else back, load_item(cfg["picture"]), cfg["length"], cfg["pivot"], an, W, H)
    for tk, (an, cfg) in marks.items():
        if not an.get("front") or not cfg.get("overlay", True):
            continue
        hl = build_hand(frame_rgba, an, rad)
        if hl:
            front.alpha_composite(hl[0], (hl[1], hl[2]))
        else:
            yy, xx = np.mgrid[0:H, 0:W]
            disc = ((xx - an["x"] * W) ** 2 + (yy - an["y"] * H) ** 2 <= rad * rad)
            bd = frame_rgba.copy()
            bd[..., 3] = np.where(disc, bd[..., 3], 0)
            front.alpha_composite(Image.fromarray(bd))
    out = Image.new("RGBA", (W, H), (58, 62, 78, 255))
    out.alpha_composite(back)
    out.alpha_composite(body)
    out.alpha_composite(front)
    return out


def marks_set(path):
    j = json.load(open(path, encoding="utf-8"))
    c = j["characters"][0]
    a = c["animations"][0]
    off = a.get("offItem") or {}
    return {"tracks": a["tracks"],
            "main": {"picture": c["items"]["main"].get("picture", "cutlass"), "length": c["items"]["main"]["length"], "pivot": c["items"]["main"]["pivot"], "overlay": c["items"]["main"].get("overlay", True)},
            "off": {"picture": off.get("picture", "dagger"), "length": off.get("length", 0.33), "pivot": off.get("pivot", 0.73), "overlay": off.get("overlay", True)},
            "fist": c.get("fist", 0.09)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strip")
    ap.add_argument("marks")
    ap.add_argument("--frames", default="1")
    ap.add_argument("--fist", default="3")
    ap.add_argument("--out", required=True)
    ap.add_argument("--zoom", type=float, default=3.0)
    ap.add_argument("--focus", choices=["main", "off"], default="", help="crop round this one mark only (main = the cutlass hand, off = the dagger hand)")
    ap.add_argument("--crop", type=float, default=0.0, help="half-size of the crop box round the marks, as a share of the frame width (0 = fit both marks)")
    a = ap.parse_args()
    strip = np.array(Image.open(a.strip).convert("RGBA"))
    W = 512
    S = marks_set(a.marks)
    frames = [int(x) for x in a.frames.split(",")]
    fists = [float(x) for x in a.fist.split(",")]
    tiles = []
    for fr in frames:
        i = fr - 1
        f = strip[:, i * W:(i + 1) * W]
        marks_here = [S["tracks"][a.focus][i]] if a.focus else [S["tracks"]["main"][i], S["tracks"]["off"][i]]
        pts = [(m["x"] * W, m["y"] * f.shape[0]) for m in marks_here if m]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        half = a.crop * W if a.crop else max(60, (max(xs) - min(xs)) / 2 + 45, (max(ys) - min(ys)) / 2 + 45)
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        box = (int(max(0, cx - half)), int(max(0, cy - half)), int(min(W, cx + half)), int(min(f.shape[0], cy + half)))
        col = []
        for fp in fists:
            im = render(f, S, i, fp, W, f.shape[0]).crop(box)
            col.append(im.resize((int(im.width * a.zoom), int(im.height * a.zoom)), Image.LANCZOS))
        tiles.append(col)
    cw = max(t[0].width for t in tiles)
    ch = max(t.height for col in tiles for t in col)
    sheet = Image.new("RGB", (cw * len(tiles), ch * len(fists)), (30, 30, 40))
    from PIL import ImageDraw
    for c, col in enumerate(tiles):
        for r, im in enumerate(col):
            sheet.paste(im.convert("RGB"), (c * cw, r * ch))
            ImageDraw.Draw(sheet).text((c * cw + 4, r * ch + 3), "frame %d, hand %g%%" % (frames[c], fists[r]), fill=(255, 255, 0))
    sheet.save(a.out)
    print("->", a.out, sheet.size)


if __name__ == "__main__":
    main()
