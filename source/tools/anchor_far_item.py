#!/usr/bin/env python3
"""Anchors the mage's far-hand item (the orb or the spell book) to her open hand in every frame, so nobody has to place it frame by frame.

The far hand (the "main" track of hand-anchors/3) is found in each frame by its skin colour: the skin blobs of the frame minus the face (the
biggest blob, and the ears and neck next to it) and minus the near fist (the blob at the "off" track's mark, the staff hand you marked), small
pieces of one hand joined together. The item's mark is then put at the same place relative to that hand in every frame: DX px to the side of the
hand's middle and DY px above its top (in a 512 px wide frame), copied from the idle's marks. The page shows the orb or the spell book on that mark
(the book with its own size and grip, see BOOK_CFG in the page), so both follow the hand.

Only the main track's x and y change; the angle is set upright (0) and "hide" and "w" are kept, as is the whole off track (the staff) and
every item setting. "front" is kept too, except on a frame where the body would hide most of the orb or the book (she lies on her far hand at the
end of the death): there the item is drawn in front, because every item stays visible in every animation. A frame where no far hand is found keeps its old mark (listed in the output). The old file is kept in the animation's source/
folder as <strip>.hand-anchors.before-anchor.json the first time.

  python anchor_far_item.py                 all the mage's animations
  python anchor_far_item.py hit dodge       only these
  python anchor_far_item.py --dry-run       print and draw a check sheet, write nothing (scratch: anchor_check.png next to this script's output)

Needs pillow, numpy and scipy.
"""
import json
import pathlib
import shutil
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAGE = ROOT / "Animations" / "Mage"
FACE_R = 45          # px: skin within this distance of the face's middle is the face (ears, neck)
FIST_R = 40          # px: the blob within this distance of the staff mark is the near fist
JOIN_R = 30          # px: pieces of skin this close together are one hand
MIN_AREA = 40        # px: smaller specks are not a hand
NEAR_R = 70          # px: how far the hand may be from where the marks had it
BOOK = (0.14, 0.85)  # the spell book's length and grip, as BOOK_CFG in the page (the orb's come from the marks file)
# A frame where the colour rule finds the wrong blob or nothing: (animation, frame) -> the far hand's (middle x, top y) in px of the 512 px frame.
OVERRIDE = {}


def skin_blobs(frame):
    r, g, b = [frame[..., i] / 255.0 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    skin = (frame[..., 3] > 200) & (h > 6) & (h < 24) & (s > 0.2) & (s < 0.55) & (mx > 0.72)
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=1))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= MIN_AREA // 2:
            out.append({"area": len(ys), "xs": xs, "ys": ys, "cx": float(xs.mean()), "cy": float(ys.mean())})
    return out


def far_hand(frame, fist, near=None):
    """The open far hand: (middle x, top y) in px, or None. near: where the hand was (middle x, top y) by the marks already in the file: the
    hand closest to it is taken (within NEAR_R px), so a face that the art shades into several small patches is never mistaken for the hand
    (the redrawn run, 2026-11-25); without it, or when nothing is that close, the biggest remaining patch is the hand."""
    bl = sorted(skin_blobs(frame), key=lambda c: -c["area"])
    if not bl:
        return None
    face = bl[0]
    if near is not None:                                              # the face is the biggest patch that is not where the hand was (a fist can be bigger than a face split by shading)
        far_from_hand = [c for c in bl if np.hypot(c["cx"] - near[0], c["ys"].min() - near[1]) > NEAR_R]
        face = far_from_hand[0] if far_from_hand else bl[0]
    rest = [c for c in bl if c is not face and np.hypot(c["cx"] - face["cx"], c["cy"] - face["cy"]) > FACE_R and np.hypot(c["cx"] - fist[0], c["cy"] - fist[1]) > FIST_R]
    groups = []                                                       # join the pieces of one hand
    for c in rest:
        for gr in groups:
            if min(np.hypot(c["cx"] - o["cx"], c["cy"] - o["cy"]) for o in gr) < JOIN_R:
                gr.append(c); break
        else:
            groups.append([c])
    groups = [gr for gr in groups if sum(c["area"] for c in gr) >= MIN_AREA]
    if not groups:
        return None
    def mid_top(g):
        xs = np.concatenate([c["xs"] for c in g]); ys = np.concatenate([c["ys"] for c in g])
        return float(xs.mean()), float(ys.min())
    gr = max(groups, key=lambda g: sum(c["area"] for c in g))
    if near is not None:
        d, g = min(((np.hypot(mid_top(g)[0] - near[0], mid_top(g)[1] - near[1]), g) for g in groups), key=lambda t: t[0])
        if d < NEAR_R:
            gr = g
    xs = np.concatenate([c["xs"] for c in gr]); ys = np.concatenate([c["ys"] for c in gr])
    return float(xs.mean()), float(ys.min())


def hidden_share(frame, im, length, pivot, x, y):
    """How much of the item picture (drawn behind the body at the mark) the body covers, 0..1."""
    h = length * 512; w = im.width * h / im.height
    t = np.array(im.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS))[..., 3] > 128
    x0, y0 = round(x - w / 2), round(y - pivot * h)
    body = np.zeros(t.shape, bool)
    ys0, xs0 = max(0, y0), max(0, x0)
    ys1, xs1 = min(frame.shape[0], y0 + t.shape[0]), min(frame.shape[1], x0 + t.shape[1])
    if ys1 > ys0 and xs1 > xs0:
        body[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] = frame[ys0:ys1, xs0:xs1, 3] > 128
    return (t & body).sum() / max(1, t.sum())


def strips(names):
    for folder in sorted(p for p in MAGE.iterdir() if p.is_dir()):
        if names and folder.name not in names:
            continue
        for js in folder.glob("*.hand-anchors.json"):
            png = folder / js.name.replace(".hand-anchors.json", ".png")
            if png.exists():
                yield folder.name, png, js


def offset_from_idle():
    """Where the item sits relative to the open hand in the idle's marks (the user's own): the median of (mark - (hand middle, hand top))."""
    _, png, js = next(strips(["idle"]))
    im = np.array(Image.open(png).convert("RGBA")).astype(int)
    tr = json.load(open(js, encoding="utf-8"))["characters"][0]["animations"][0]["tracks"]
    dx, dy = [], []
    for k in range(im.shape[1] // 512):
        m, o = tr["main"][k], tr["off"][k]
        if not m or not o:
            continue
        fh = far_hand(im[:, 512 * k:512 * (k + 1)], (o["x"] * 512, o["y"] * im.shape[0]))
        if fh:
            dx.append(m["x"] * 512 - fh[0]); dy.append(m["y"] * im.shape[0] - fh[1])
    return float(np.median(dx)), float(np.median(dy))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    DX, DY = offset_from_idle()
    print("the item sits %+.0f px to the side of the hand's middle and %+.0f px from its top (from the idle's marks)" % (DX, DY))
    sheet = []
    pics = [(Image.open(ROOT / "source" / "assets" / "orb.png").convert("RGBA"), None), (Image.open(ROOT / "source" / "assets" / "book.png").convert("RGBA"), BOOK)]
    for name, png, js in strips(args):
        im = np.array(Image.open(png).convert("RGBA")).astype(int)
        H = im.shape[0]
        doc = json.load(open(js, encoding="utf-8"))
        tr = doc["characters"][0]["animations"][0]["tracks"]
        orb_set = doc["characters"][0]["items"]["main"]
        for k in range(im.shape[1] // 512):
            m, o = tr["main"][k], tr["off"][k]
            if not m or not o:
                print(" ", name, k + 1, "no marks: left as it is"); continue
            near = None if m.get("hide") else (m["x"] * 512 - DX, m["y"] * H - DY)
            fh = OVERRIDE.get((name, k + 1)) or far_hand(im[:, 512 * k:512 * (k + 1)], (o["x"] * 512, o["y"] * H), near)
            old = (m["x"] * 512, m["y"] * H)
            if not fh:
                print(" ", name, k + 1, "far hand not found: old mark kept"); new = old
            else:
                new = (fh[0] + DX, fh[1] + DY)
                m["x"], m["y"], m["a"] = round(new[0] / 512, 3), round(new[1] / H, 3), 0
                print(" ", name, k + 1, "hand (%.0f, %.0f) -> mark (%.0f, %.0f), moved %.0f px" % (fh[0], fh[1], new[0], new[1], np.hypot(new[0] - old[0], new[1] - old[1])))
                if not m.get("front"):
                    fr = im[:, 512 * k:512 * (k + 1)]
                    hid = max(hidden_share(fr, pic, *(size or (orb_set["length"], orb_set["pivot"])), *new) for pic, size in pics)
                    if hid > 0.5:
                        m["front"] = True
                        print("    the body would hide %.0f%% of the item: drawn in front on this frame" % (100 * hid))
            sheet.append((name, k + 1, im[:, 512 * k:512 * (k + 1)], fh, old, new))
        if not dry:
            keep = png.parent / "source" / (png.name[:-4] + ".hand-anchors.before-anchor.json")
            keep.parent.mkdir(exist_ok=True)
            if not keep.exists():
                shutil.copyfile(js, keep)
            raw = open(js, encoding="utf-8").read()
            indent = 1 if raw.lstrip().startswith("{\n") or "\n " in raw[:40] else None
            open(js, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=indent, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))
            print("wrote", js.relative_to(ROOT))
    if dry:                                                          # a check sheet: each frame with the hand (green), the old mark (red) and the new one (cyan)
        cw, chh, cols = 200, 250, 8
        out = Image.new("RGB", (cw * cols, chh * ((len(sheet) + cols - 1) // cols)), (40, 40, 52))
        for i, (name, k, fr, fh, old, new) in enumerate(sheet):
            t = Image.new("RGB", (512, fr.shape[0]), (70, 90, 80)); t.paste(Image.fromarray(fr.astype(np.uint8), "RGBA"), mask=Image.fromarray(fr[..., 3].astype(np.uint8)))
            d = ImageDraw.Draw(t)
            if fh: d.ellipse((fh[0] - 6, fh[1] - 6, fh[0] + 6, fh[1] + 6), outline=(0, 255, 0), width=3)
            d.ellipse((old[0] - 7, old[1] - 7, old[0] + 7, old[1] + 7), outline=(255, 60, 60), width=3)
            d.ellipse((new[0] - 7, new[1] - 7, new[0] + 7, new[1] + 7), outline=(0, 230, 255), width=3)
            t.thumbnail((cw, chh)); out.paste(t, ((i % cols) * cw, (i // cols) * chh))
            ImageDraw.Draw(out).text(((i % cols) * cw + 4, (i // cols) * chh + 4), "%s %d" % (name, k), fill=(255, 255, 255))
        p = pathlib.Path(sys.argv[0]).resolve().parent / "anchor_check.png" if "--sheet-here" in sys.argv else pathlib.Path.cwd() / "anchor_check.png"
        out.save(p); print("check sheet", p)


main()
