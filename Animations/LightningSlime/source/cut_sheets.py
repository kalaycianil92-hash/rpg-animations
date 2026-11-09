#!/usr/bin/env python3
"""Cuts the lightning slime's generated sheets (the user's Gemini JPGs in inbox/Lightning_Slime_Animations, 2026-11-09) into 512 px strips with the lightning loader (light_panels.py: the body is measured from its
warm colours only; the dark magenta shadow ellipses the generator drew are keyed out) and the ice slime's piece-based cutter (light_cut.py: row scales from panel 1 / the last panel, grounded panels on y 470,
base centres on x 259, airborne panels at their real height).

  python Animations/LightningSlime/source/cut_sheets.py [names...]      (names: hit death dodge spark_spit skybolt_bounce; default all)

Output per animation: <folder>/lightning_<name>_<n>frame_strip.png + .placement.json + a check picture; the spit also gets .mouth.json (where the page starts the spit).
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
LS = os.path.abspath(os.path.join(HERE, ".."))
INBOX = os.path.abspath(os.path.join(LS, "..", "..", "inbox", "Lightning_Slime_Animations"))
sys.path.insert(0, HERE)
import light_cut as lc

JOBS = {
    # name: (inbox file, folder, strip name, row_counts, grounded panels (0-based), fps, hit frame, options)
    "hit": ("Gemini_slime_lightning_hit_sheet.jpg", "hit", "lightning_hit_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 12, None, {}),
    "death": ("Gemini_slime_lightning_death_sheet.jpg", "death", "lightning_death_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 8, None, {"shared": True}),
    "dodge": ("Gemini_slime_lightning_dodge_sheet.jpg", "dodge", "lightning_dodge_6frame_strip", [3, 3], [0, 1, 4, 5], 14, None, {}),
    "spark_spit": ("Gemini_slime_lightning_spark_spit_sheet.jpg", "spark_spit", "lightning_spark_spit_8frame_strip", [4, 4], [0, 1, 2, 3, 4, 5, 6, 7], 12, 5, {}),
    "thunder_slam": ("Gemini_slime_lightning_thunder_slam_sheet.jpg", "thunder_slam", "lightning_thunder_slam_8frame_strip", [4, 4], [0, 1, 6, 7], 12, 7, {"shared": True, "mul": {6: 0.78}}),
    "voltaic_eruption": ("Gemini_slime_lightning_voltaic_eruption_sheet.jpg", "voltaic_eruption", "lightning_voltaic_eruption_6frame_strip", [3, 3], [0, 1, 2, 3, 4, 5], 12, None, {"rest_mul": (1.0, 0.95), "mul": {1: 0.86, 2: 0.86, 3: 0.55, 4: 0.62}}),
    "skybolt_bounce": ("Gemini_slime_lightning_skybolt_bounce_sheet.jpg", "skybolt_bounce", "lightning_skybolt_bounce_8frame_strip", [4, 4], [0, 1, 4, 6, 7], 12, 5, {}),
}


def mouth_marks(strip_path, json_path, check_path):
    st = np.array(Image.open(strip_path).convert("RGBA")).astype(int)
    marks = {}
    for k in (3, 4, 5):
        f = st[:, k * 512:(k + 1) * 512]
        box = np.zeros(f.shape[:2], bool); box[240:440, 240:512] = True
        r, g, b, a = f[..., 0], f[..., 1], f[..., 2], f[..., 3]
        if k < 5: m = box & (a > 128) & (r < 235) & (g > 225) & (b > 240); need = 120                      # the bright cyan-white spark ball
        else: m = box & (a > 128) & (0.3 * r + 0.59 * g + 0.11 * b < 130) & (r > g); need = 400            # the dark red mouth opening
        m = ndi.binary_opening(m, structure=np.ones((3, 3)))
        lab, n = ndi.label(m); cands = []
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) > need: cands.append((len(ys), float(xs.mean()), float(ys.mean()), int(xs.max() - xs.min()), int(ys.max() - ys.min())))
        print("  frame", k + 1, "candidates (area, x, y, w, h):", [(c[0], round(c[1]), round(c[2]), c[3], c[4]) for c in sorted(cands, reverse=True)[:4]])
        if cands:
            if k < 5: best = max(cands, key=lambda c: (c[2] > 300, c[0]))                                    # below the eyes
            else: best = max(cands, key=lambda c: c[0])
            marks[k + 1] = {"area": best[0], "x": round(best[1], 1), "y": round(best[2], 1), "w": best[3], "h": best[4]}
    json.dump({"note": "the spark ball in the mouth on frames 4 and 5 and the open mouth on frame 6 (centre and size in the 512 cell, before the page mirrors the sprite): the spit leaves the mouth at the release frame 5",
               "mouth": marks}, open(json_path, "w"), indent=1)
    print("  mouth marks:", marks)
    W, H = st.shape[1], st.shape[0]
    pic = Image.new("RGB", (W, H), (38, 84, 52)); pic.paste(Image.fromarray(st.astype(np.uint8)).convert("RGB"), (0, 0), Image.fromarray(st.astype(np.uint8)).split()[3])
    d = ImageDraw.Draw(pic)
    for k, mk in marks.items():
        d.ellipse([(k - 1) * 512 + mk["x"] - 6, mk["y"] - 6, (k - 1) * 512 + mk["x"] + 6, mk["y"] + 6], outline=(255, 0, 0), width=2)
    pic.resize((W // 2, H // 2), Image.LANCZOS).save(check_path)


names = sys.argv[1:] or list(JOBS)
for nm in names:
    fn, folder, stem, rows, grounded, fps, hitf, opts = JOBS[nm]
    d = os.path.join(LS, folder); os.makedirs(os.path.join(d, "source"), exist_ok=True)
    src = os.path.join(d, "source", folder + "_sheet.jpg")
    shutil.copyfile(os.path.join(INBOX, fn), src)
    print("==", nm)
    lc.build_strip(src, os.path.join(d, stem + ".png"), os.path.join(d, stem.replace("_strip", "_check") + ".png"), os.path.join(d, stem + ".placement.json"),
                   rows, grounded, nm, fps, hitf, **opts)
    if nm == "thunder_slam":                                                     # the generator drew the slam's panel 1 as a PAIN pose (eyes shut, mouth open), not the rest pose: the idle's frame 1 stands in for it
        from PIL import Image as _I
        st = _I.open(os.path.join(d, stem + ".png")).convert("RGBA"); idle = _I.open(os.path.join(LS, "idle", "lightning_idle_strip.png")).convert("RGBA")
        st.paste(_I.new("RGBA", (512, 512), (0, 0, 0, 0)), (0, 0)); st.alpha_composite(idle.crop((0, 0, 512, 512)), (0, 0)); st.save(os.path.join(d, stem + ".png"))
        print("  frame 1 replaced by the idle's rest frame")
    if nm == "spark_spit":
        mouth_marks(os.path.join(d, stem + ".png"), os.path.join(d, stem + ".mouth.json"), os.path.join(d, "lightning_spark_spit_mouth_check.png"))
