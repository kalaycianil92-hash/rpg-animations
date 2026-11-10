#!/usr/bin/env python3
"""Cuts the Slime King's sheets (the user's ChatGPT PNGs, magenta key, 2026-11-11) into 512 px strips, with the Elite's machinery (Animations/EliteSlime/source/elite_panels.py: the body is the biggest piece of a
panel, the floating glove with its staff is a detached piece that goes to the nearest body, the magenta is keyed with `1 - clip((min(r, b) - g - 70) / 110, 0, 1)` and the soft edges are despilled).

  python Animations/SlimeKing/source/cut_king.py [idle]

Every panel is placed so that its base is 350 px wide (the slimes' standard), its floor row on y 470 and its base centre on x 259, at ONE scale for the whole sheet (the median of the panels' base widths: the generator
kept the base within 2%). The King is drawn bigger on screen by the page (its Monster size), not in the strip. Output per animation: <folder>/king_<name>_<N>frame_strip.png + .placement.json + a check picture.
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
KING = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(KING, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "Animations", "EliteSlime", "source"))
import elite_panels as ep

BASE_W, GROUND_Y, BASE_X, FRAME = 350.0, 470, 259, 512
JOBS = {
    "idle": dict(file="slime_king_idle_sheet.png", folder="idle", rows=[3, 3], fps=8, name="idle", extra={}),
}


def cut(name):
    j = JOBS[name]
    d = os.path.join(KING, j["folder"]); os.makedirs(os.path.join(d, "source"), exist_ok=True)
    src = os.path.join(d, "source", j["folder"] + "_sheet" + os.path.splitext(j["file"])[1])
    if not os.path.isfile(src): shutil.copyfile(os.path.join(ROOT, "inbox", j["file"]), src)
    rows = j["rows"]; N = sum(rows)
    P = ep.load_panels(src, rows)["panels"]
    c = P[0]["bw"] / float(P[0]["bw_open"])
    bws = [q["bw_open"] * c for q in P]
    sc = BASE_W / float(np.median(bws))
    print("== %s | opening factor %.3f | base widths (opened) %s | shared scale %.3f" % (name, c, [int(b) for b in bws], sc))
    out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0)); info = []
    for k, q in enumerate(P):
        ox = int(round(BASE_X - q["mid_open"] * sc)); oy = int(round(GROUND_Y - q["low_open"] * sc))
        fr, clipped = ep.place(q, sc, ox, oy)
        a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
        out.alpha_composite(fr, (FRAME * k, 0))
        info.append({"top": int(ys.min()), "bottom": int(ys.max()), "left": int(xs.min()), "right": int(xs.max()), "baseW": round(bws[k] * sc, 1)})
        print("  %d | x %3d..%3d | y %3d..%3d | base %.0f | clipped px %d" % (k + 1, xs.min(), xs.max(), ys.min(), ys.max(), bws[k] * sc, clipped))
    stem = "king_%s_%dframe_strip" % (j["name"], N)
    if j["name"] == "idle": stem = "king_idle_strip"
    path = os.path.join(d, stem + ".png"); out.save(path)
    pl = {"format": "frame-placement/1", "animation": j["name"], "file": stem + ".png", "frames": N, "fps": j["fps"]}; pl.update(j["extra"]); pl["frameInfo"] = info
    json.dump(pl, open(path.replace(".png", ".placement.json"), "w"), indent=1)
    W, H = out.size; pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
    for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
        cc = Image.new("RGBA", (W, H), bg); cc.alpha_composite(out); pic.paste(cc.convert("RGB"), (0, i * H))
    dr = ImageDraw.Draw(pic)
    for i in range(2):
        dr.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
        for k in range(1, N): dr.line([(k * FRAME, i * H), (k * FRAME, (i + 1) * H)], fill=(200, 0, 0), width=1)
    pic.resize((W // 2, H * 2 // 2), Image.LANCZOS).save(path.replace("_strip.png", "_check.png"))
    print("strip", os.path.relpath(path, KING))


for nm in (sys.argv[1:] or list(JOBS)):
    cut(nm)
