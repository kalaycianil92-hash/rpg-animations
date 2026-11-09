#!/usr/bin/env python3
"""Cuts the dark slime's generated sheets (the user's Gemini JPGs in inbox/Dark_Slime_animations, 2026-11-09, flat GREEN background) into 512 px strips with the green-key loader (dark_panels.py) and the
piece-based cutter (dark_cut.py: row scales from panel 1 / the last panel or ONE shared scale, grounded panels on y 470, base centres on x 259, airborne panels at their real height).

  python Animations/DarkSlime/source/cut_sheets.py [names...]      (names: hit death dodge gloom_spit abyssal_eruption; default all)

Output per animation: <folder>/dark_<name>_<n>frame_strip.png + .placement.json + a check picture; the spit also gets .mouth.json (where the page starts the spit).
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.abspath(os.path.join(HERE, ".."))
INBOX = os.path.abspath(os.path.join(DS, "..", "..", "inbox", "Dark_Slime_animations"))
sys.path.insert(0, HERE)
import dark_cut as dc

JOBS = {
    # name: (inbox file, folder, strip name, row_counts, grounded panels (0-based), fps, hit frame, options)
    "hit": ("dark_slime_hit_sheet.jpg", "hit", "dark_hit_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 12, None, {}),
    "death": ("dark_slime_death_sheet.jpg", "death", "dark_death_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 8, None, {"shared": True}),
    "dodge": ("dark_slime_dodge_sheet.jpg", "dodge", "dark_dodge_6frame_strip", [3, 3], [0, 1, 4, 5], 14, None, {}),
    "gloom_spit": ("dark_slime_gloom_spit_sheet.jpg", "gloom_spit", "dark_gloom_spit_8frame_strip", [4, 4], [0, 1, 2, 3, 4, 5, 6, 7], 12, 5, {}),
    "abyssal_eruption": ("dark_slime_abyssal_eruption_sheet.jpg", "abyssal_eruption", "dark_abyssal_eruption_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 12, None, {"shared": True}),
}


def mouth_marks(strip_path, json_path, check_path):
    st = np.array(Image.open(strip_path).convert("RGBA")).astype(int)
    marks = {}
    for k in (3, 4, 5):
        f = st[:, k * 512:(k + 1) * 512]
        box = np.zeros(f.shape[:2], bool); box[255:440, 240:512] = True
        r, g, b, a = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
        if k < 5: m = box & (a > 128) & (r > 215) & (b > 235) & (g > 130); need = 150                      # the bright violet-pink orb in the mouth
        else: m = box & (a > 128) & (0.3 * r + 0.59 * g + 0.11 * b < 38); need = 400                       # the dark open mouth
        m = ndi.binary_opening(m, structure=np.ones((3, 3)))
        lab, n = ndi.label(m); cands = []
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) > need: cands.append((len(ys), float(xs.mean()), float(ys.mean()), int(xs.max() - xs.min()), int(ys.max() - ys.min())))
        print("  frame", k + 1, "candidates (area, x, y, w, h):", [(c[0], round(c[1]), round(c[2]), c[3], c[4]) for c in sorted(cands, reverse=True)[:4]])
        if cands:
            if k < 5: best = max(cands, key=lambda c: (c[2] > 320, c[0]))                                    # below the eyes
            else: best = max(cands, key=lambda c: c[0])
            marks[k + 1] = {"area": best[0], "x": round(best[1], 1), "y": round(best[2], 1), "w": best[3], "h": best[4]}
    json.dump({"note": "the orb of dark energy in the mouth on frames 4 and 5 and the open mouth on frame 6 (centre and size in the 512 cell, before the page mirrors the sprite): the spit leaves the mouth at the release frame 5",
               "mouth": marks}, open(json_path, "w"), indent=1)
    print("  mouth marks:", marks)
    W, H = st.shape[1], st.shape[0]
    img = Image.fromarray(st.astype(np.uint8))
    pic = Image.new("RGB", (W, H), (38, 84, 52)); pic.paste(img.convert("RGB"), (0, 0), img.split()[3])
    d = ImageDraw.Draw(pic)
    for k, mk in marks.items():
        d.ellipse([(k - 1) * 512 + mk["x"] - 6, mk["y"] - 6, (k - 1) * 512 + mk["x"] + 6, mk["y"] + 6], outline=(255, 0, 0), width=2)
    pic.resize((W // 2, H // 2), Image.LANCZOS).save(check_path)


names = sys.argv[1:] or list(JOBS)
for nm in names:
    fn, folder, stem, rows, grounded, fps, hitf, opts = JOBS[nm]
    d = os.path.join(DS, folder); os.makedirs(os.path.join(d, "source"), exist_ok=True)
    src = os.path.join(d, "source", folder + "_sheet.jpg")
    shutil.copyfile(os.path.join(INBOX, fn), src)
    print("==", nm)
    dc.build_strip(src, os.path.join(d, stem + ".png"), os.path.join(d, stem.replace("_strip", "_check") + ".png"), os.path.join(d, stem + ".placement.json"),
                   rows, grounded, nm, fps, hitf, **opts)
    if nm == "gloom_spit":
        mouth_marks(os.path.join(d, stem + ".png"), os.path.join(d, stem + ".mouth.json"), os.path.join(d, "dark_gloom_spit_mouth_check.png"))
