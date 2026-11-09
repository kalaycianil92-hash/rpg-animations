#!/usr/bin/env python3
"""Makes POSE GUIDES from an existing animation strip, to attach to an image generator when a character is redrawn in a new look (see docs/RESKIN_PILOT_PLAN.md).

The generator gets flat grey SILHOUETTES of the poses, not the old character, so it cannot copy the old clothes, colours or face. Each guide shows:
  - the silhouette of the pose (smoothed: no folds, no details),
  - a thin ground line when the figure stands on the ground (none in the air),
  - two dots from the hand marks: RED = the 'main' mark (the Rogue: the front fist, the cutlass), BLUE = the 'off' mark (the Rogue: the rear fist, the dagger); none where an item is hidden.

Only the UNIQUE images are drawn (strips repeat frames for timing). With --share-with <strip> (repeatable) the images that also appear in another strip are left out of the guides: they come
from that strip's re-skin (the idle's first frame ends every skill, the Umbral Shroud's first two frames start the Abyssal Backstab, the Shadow Shiv's frames are the Static Stiletto's).

Writes, in --out (default reskin/<Character>_<animation>/):
  guide_sheet_1.png ...   the guides in 3 x 2 sheets (panel = one cell, read left to right, top row first), the order the generated sheet will be cut in
  guide_uidNN.png         every guide alone (for generating one image at a time)
  frame_map.json          which unique image sits at which position of the strip, which are shared, which panel is which (used by check_reskin.py and reskin_strip.py)
  prompt.txt              a ready prompt for the sheets (fill in the new character's description)

  python source/tools/make_pose_guides.py Animations/Rogue/permafrost_execution/cloaked_permafrost_execution_19frame_strip.png --share-with Animations/Rogue/idle/cloaked_idle_strip.png
"""
import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reskin_lib as L

ROOT = pathlib.Path(__file__).resolve().parents[2]
BG, FILL, LINE = (240, 240, 240), (96, 96, 108), (60, 60, 60)
RED, BLUE = (230, 40, 40), (40, 90, 230)

ap = argparse.ArgumentParser()
ap.add_argument("strip")
ap.add_argument("--out")
ap.add_argument("--cols", type=int, default=3)
ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--share-with", action="append", default=[], help="a strip whose frames this animation re-uses (their guides are not made)")
ap.add_argument("--marks", help="the hand marks (default: next to the strip)")
ap.add_argument("--no-marks", action="store_true")
ap.add_argument("--air", default="", help="unique-image ids (the uid numbers in frame_map.json, comma separated) that are IN THE AIR although the strip puts them on the ground line (a flight frame the page lifts with its path): drawn without a ground line and raised by --air-lift px, the dots with them")
ap.add_argument("--air-lift", type=int, default=150)
ap.add_argument("--color-refs", action="store_true", help="also write ref_uidNN.png: the ORIGINAL character's own frame, coloured, on flat magenta in a square picture (a second kind of pose reference: a silhouette cannot show perspective, which arm is nearer, where the head looks; a coloured example can, but the generator may copy the old look: the prompt must say it is a pose reference only)")
a = ap.parse_args()

strip = pathlib.Path(a.strip).resolve()
char, anim = L.char_and_anim(strip)
out = pathlib.Path(a.out) if a.out else ROOT / "reskin" / (char + "_" + anim)
out.mkdir(parents=True, exist_ok=True)
for old in list(out.glob("guide_sheet_*.png")) + list(out.glob("guide_uid*.png")) + list(out.glob("ref_uid*.png")):              # (guides of an earlier run, with other frames shared, must not stay behind)
    old.unlink()
frames, H = L.load_frames(strip)
first, pos, groups = L.uniques(frames)
marks = None if a.no_marks else L.load_marks(a.marks or L.default_marks_path(strip))

shared_keys = []                                                       # [(strip path, {frame key: frame index})]
for s in a.share_with:
    fr, _ = L.load_frames(s)
    shared_keys.append((str(pathlib.Path(s).resolve()), {L.frame_key(L.pad_to(f, H)): i for i, f in enumerate(fr)}))

uniq = []
for uid, p0 in enumerate(first):
    k = L.frame_key(frames[p0])
    sh = None
    for si, (sp, keys) in enumerate(shared_keys):
        if k in keys:
            sh = {"strip": si, "frame": keys[k]}
            break
    uniq.append({"id": uid, "positions": [g + 1 for g in groups[uid]], "shared": sh})
guided = [u["id"] for u in uniq if u["shared"] is None]
air_ids = {int(x) for x in a.air.split(",") if x.strip()}


def silhouette(uid):
    f = frames[first[uid]]
    m = L.mask(f)
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3))
    m = ndi.gaussian_filter(m.astype(float), 1.3) > 0.5
    lift = a.air_lift if uid in air_ids else 0
    if lift:                                                          # a flight frame: raised, so that it floats in the panel (no ground line below)
        m2 = np.zeros_like(m)
        m2[:H - lift] = m[lift:]
        m = m2
    arr = np.zeros((H, L.CW, 3), np.uint8)
    arr[:] = BG
    arr[m] = FILL
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    bb = L.bbox(m)
    gy = L.ground_y(H)
    if bb and bb[3] >= gy - 8 and not lift:                                         # standing on the ground: a thin line under the feet
        d.line([(30, gy), (L.CW - 30, gy)], fill=LINE, width=2)
    if marks:
        dist = ndi.distance_transform_edt(~m)
        for tr, x, y in L.marks_at(marks, first[uid]):
            cx, cy, r = x * L.CW, y * H - lift, 9
            if dist[min(H - 1, max(0, int(cy))), min(L.CW - 1, max(0, int(cx)))] > 14:   # a mark that lies outside the body (a hand under her, like the death's last frame): no dot, it would only confuse the generator
                continue
            d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=(255, 255, 255))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED if tr == "main" else BLUE)
    return img


sheets = []
per = a.cols * a.rows
for si in range(0, len(guided), per):
    chunk = guided[si:si + per]
    sheet = Image.new("RGB", (L.CW * a.cols, H * a.rows), BG)
    d = ImageDraw.Draw(sheet)
    for k, uid in enumerate(chunk):
        r, c = divmod(k, a.cols)
        sheet.paste(silhouette(uid), (c * L.CW, r * H))
    for c in range(1, a.cols):
        d.line([(c * L.CW, 0), (c * L.CW, H * a.rows)], fill=(205, 205, 205), width=2)
    for r in range(1, a.rows):
        d.line([(0, r * H), (L.CW * a.cols, r * H)], fill=(205, 205, 205), width=2)
    name = "guide_sheet_%d.png" % (len(sheets) + 1)
    sheet.save(out / name)
    sheets.append({"file": name, "uids": chunk, "cols": a.cols, "rows": a.rows})
for uid in guided:
    silhouette(uid).save(out / ("guide_uid%02d.png" % uid))

if a.color_refs:
    S = max(L.CW, H) * 2
    for uid in guided:
        f = Image.fromarray(frames[first[uid]]).resize((L.CW * 2, H * 2), Image.LANCZOS)
        cv = Image.new("RGBA", (S, S), (255, 0, 255, 255))
        cv.alpha_composite(f, ((S - f.width) // 2, S - f.height))
        cv.convert("RGB").save(out / ("ref_uid%02d.png" % uid))

doc = {"format": "reskin-map/1", "orig_strip": str(strip), "cell": [L.CW, H], "positions": len(frames), "uniques": uniq, "guided": guided, "sheets": sheets,
       "share_with": [s for s, _ in shared_keys], "marks": None if marks is None else str(L.default_marks_path(strip) if not a.marks else pathlib.Path(a.marks).resolve())}
(out / "frame_map.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")

from math import gcd
_w, _h = a.cols * L.CW, a.rows * H
_g = gcd(_w, _h)
RATIO = "%d:%d" % (_w // _g, _h // _g)                                    # 3:2 for 512 px cells, 1:1 for 512 x 768 cells (6 panels)
prompt = """RE-SKIN PROMPT (pose-guided sheet). Made by make_pose_guides.py for %s / %s. Works with Gemini or ChatGPT.

HOW TO USE
- Attach TWO images: (1) the reference picture of the character's NEW look, (2) one guide sheet from this folder (%s). Ask for a %s image. Paste everything between the two lines of equals signs and fill in the one bracket.
- The panels of the sheet you get back must be in the same order as the guide's (left to right, top row first): that order is how the pieces are cut and matched to the animation.
- Save the sheet in inbox/ and tell me. Then: cut it with source/tools/slice_keypose_sheet.py, check it with source/tools/check_reskin.py (--map %s), rebuild with source/tools/reskin_strip.py.

==============================================================================
OUTPUT: exactly ONE static image, a PNG sprite sheet, and nothing else. Do NOT create a GIF, an animation, a video, a preview, extra images, alternate versions or a second attempt. No other files.

Create a sprite sheet: a grid of %d columns x %d rows of equal panels, read left to right, top row first. In every panel draw the character of image 1 in EXACTLY the pose of the matching panel of image 2.

IMAGE 2 IS A POSE GUIDE ONLY. Its grey silhouettes show where the head, body, arms, legs and cloak must be in each panel: same pose, same size, same place in the panel, the feet where the silhouette's feet are (on the thin line where there is one, in the air where there is none), the head where the silhouette's head is. Do NOT copy its grey colour, its flat look or its outline: the character must be fully drawn in her or his own colours, clothes and face from image 1. The two dots mark the two hands: a RED dot and a BLUE dot; put one closed fist exactly on each dot. The dots are for positioning ONLY: do NOT draw any dot, circle, ring, spot or colour mark on the character (not on the fists, the nails, the boots or the clothes).

CHARACTER: the exact same character as in image 1: [PASTE THE NEW LOOK'S DESCRIPTION HERE]. Keep the same painted game-sprite style, thick dark outlines, colours, proportions, face and three-quarter head angle as image 1. Do not redesign anything. Her or his face looks the same in every panel.

VIEW: strict side view, facing the direction of the silhouette (right unless the guide shows otherwise), the head turned a little toward the viewer as in image 1. The camera angle is the same in every panel.

NO ITEMS AND NO EFFECTS: no weapon, no dagger, no sword, nothing in the hands: both hands are bare, tight CLOSED FISTS (the items are added later). No glow, smoke, sparks, speed lines, motion blur or effects of any kind.

SAME SCALE (very important): the character must have exactly the same height in every panel as the silhouette in the same panel. Do not zoom in or out between panels. The WHOLE body, with the cloak, both fists and both boots, is visible in every panel, never cropped, and nothing touches a panel edge.

BACKGROUND AND LAYOUT: one flat pure magenta (#FF00FF) background filling the whole image, identical in every pixel. No gradient, no ground line, no cast shadow, no grid lines or borders between panels, no text, no numbers, no labels. No magenta or pink on the character.

FINAL REMINDER: output ONE single static PNG image only. No GIF, no extra images.
==============================================================================
""" % (char, anim, sheets[0]["file"] if sheets else "guide_sheet_1.png", RATIO, "frame_map.json", a.cols, a.rows)
(out / "prompt.txt").write_text(prompt, encoding="utf-8")

print("strip", strip.name, ":", len(frames), "frames,", len(uniq), "unique,", len(guided), "to draw,", len(uniq) - len(guided), "shared")
for u in uniq:
    print("  unique %2d  positions %-22s %s" % (u["id"], u["positions"], "shared with strip %d frame %d" % (u["shared"]["strip"], u["shared"]["frame"] + 1) if u["shared"] else "guide"))
print("sheets:", [(s["file"], s["uids"]) for s in sheets])
print("->", out)
