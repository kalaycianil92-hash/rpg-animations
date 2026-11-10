#!/usr/bin/env python3
"""Cuts the Elite slime's HIT, DEATH and DODGE sheets (the user's Gemini JPGs, 2752 x 1536, 3 x 2, inbox/Elite_slime_animations/, 2026-11-10) into 512 px strips.

  python Animations/EliteSlime/source/cut_pack.py [hit] [death] [dodge]        (default: all three)

The same machinery as the Sword Slash (make_slash_strip.py): elite_panels.load_panels (the body is the biggest piece, the floating fist and sword go to the body they are nearest to), the base width, the floor row and the
base centre measured through a morphological opening (a blade lying across the skirt vanishes) times the factor measured on panel 1 (where nothing lies on the skirt), every panel placed so that its base is 350 px wide
(the idle's), its floor row on y 470 and its base centre on x 259. What differs per animation (JOBS below):
  mode "base"   every panel scaled to the same base width (NOT used: the generator draws the base itself at different widths, e.g. the hit's panel 4 has a base 14% narrower than panel 1's but a shield only 4% smaller,
                so base-width scaling made that frame 16% too big; checked by matching the shield, a rigid part, panel against panel)
  mode "shared" one scale for all panels, panel 1's (hit, dodge, death: the creature is the same size in every frame within the generator's +-5%; in the death the pile is wider and lower because it collapsed)
  airborne      panels the generator lifted off the floor (the dodge's hop): placed at their real height above the floor line of their row (the median floor of the grounded panels of that row)
  swap          panels replaced by the idle's frame 1 (the REST pose): the generator drew the 'rest' panels with the sword tilted back (11 o'clock) instead of the idle's 12:30, which would pop at the pack's start and end
Output per animation: <folder>/elite_<name>_6frame_strip.png + .placement.json + a check picture (white and green, the floor line drawn) and a report.
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elite_panels as ep

EL = os.path.abspath(os.path.join(HERE, ".."))
INBOX = os.path.abspath(os.path.join(EL, "..", "..", "inbox", "Elite_slime_animations"))
IDLE = os.path.join(EL, "idle", "elite_idle_strip.png")
BASE_W, GROUND_Y, BASE_X, FRAME = 350.0, 470, 259, 512

JOBS = {
    "hit": dict(file="elite_slime_hit.jpg", folder="hit", mode="shared", airborne=[], swap=[5], fps=12, mul={}, dx={}, extra={}),
    "death": dict(file="elite_slime_death.jpg", folder="death", mode="shared", airborne=[], swap=[], fps=8, mul={}, dx={},
                  extra={"holds": [1, 1.2, 1.3, 1.3, 1.5, 3]}),
    "dodge": dict(file="elite_slime_dodge.jpg", folder="dodge", mode="shared", airborne=[2], swap=[0, 5], fps=14, mul={}, dx={},
                  extra={"evadeFrame": 3, "smooth": True, "xUnit": "character-widths", "x": [0, -0.02, -0.07, -0.1, -0.06, -0.02], "y": [0, 0, 0, 0, 0, 0]}),
    # the Shield Bash (2026-11-10): the user generated it twice; Gemini's (elite_slime_shield_bash_gemini.jpg: skirts of the bottom row touching, an arm on the fist in panel 3, three near-identical panels) was not usable;
    # ChatGPT's (1774 x 887, 4 x 2: the same size in every panel, base 72% of the panel as asked, the fist floating in all eight) is the one cut here. front: the body's right-most point on the strike frame (the page lands it on the target)
    "shield_bash": dict(file="elite_slime_shield_bash_chatgpt.png", folder="shield_bash", mode="shared", rows=[4, 4], airborne=[], swap=[], fps=12, mul={}, dx={}, front=6,
                        extra={"hitFrame": 6}),
}


def cut(name):
    j = JOBS[name]
    d = os.path.join(EL, j["folder"]); os.makedirs(os.path.join(d, "source"), exist_ok=True)
    src = os.path.join(d, "source", j["folder"] + "_sheet" + os.path.splitext(j["file"])[1])
    if not os.path.isfile(src): shutil.copyfile(os.path.join(INBOX, j["file"]), src)
    stem = "elite_%s_%dframe_strip" % (name, sum(j.get("rows", [3, 3])))
    rows = j.get("rows", [3, 3]); N = sum(rows)
    P = ep.load_panels(src, rows)["panels"]
    c = P[0]["bw"] / float(P[0]["bw_open"])
    print("==", name, "| opening factor %.3f" % c)
    # the floor of a row (sheet y): the median floor of its grounded panels
    floor = {}
    for r in range(len(rows)):
        ys = [P[k]["origin"][1] + P[k]["low_open"] for k in range(N) if P[k]["row"] == r and k not in j["airborne"]]
        floor[r] = float(np.median(ys))
    out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0)); info = []
    idle1 = Image.open(IDLE).convert("RGBA").crop((0, 0, FRAME, FRAME))
    print("panel | base w raw / opened | scale | lift | x range | top | bottom | clipped px")
    sc0 = BASE_W / (P[0]["bw_open"] * c)
    for k, q in enumerate(P):
        bw = q["bw_open"] * c
        sc = (BASE_W / bw if j["mode"] == "base" else sc0) * j["mul"].get(k, 1.0)
        wx0, wy0 = q["origin"]
        floor_local = (floor[q["row"]] - wy0) if k in j["airborne"] else q["low_open"]
        lift = (floor[q["row"]] - (wy0 + q["low_open"])) * sc if k in j["airborne"] else 0.0
        ox = int(round(BASE_X + j["dx"].get(k, 0) - q["mid_open"] * sc)); oy = int(round(GROUND_Y - floor_local * sc))
        fr, clipped = ep.place(q, sc, ox, oy)
        if k in j["swap"]: fr = idle1.copy()
        a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
        out.alpha_composite(fr, (FRAME * k, 0))
        if j.get("front") == k + 1:                                            # the body's right-most point on this frame (the strike): where the page lands it on the target
            my, mx = np.where(q["main"]); jf = int(np.argmax(mx)); j["extra"]["front"] = {"x": int(round(ox + mx[jf] * sc)), "y": int(round(oy + my[jf] * sc))}
        info.append({"lift": round(lift, 1), "top": int(ys.min()), "bottom": int(ys.max()), "baseW": round(bw * sc, 1), "sizeAgainstIdle": round(sc * bw / BASE_W, 3), **({"replacedByIdleRest": True} if k in j["swap"] else {})})
        print("  %d   | %4d / %4d | %.3f | %5.1f | %3d..%3d | %3d | %3d | %d%s" % (k + 1, q["bw"], q["bw_open"], sc, lift, xs.min(), xs.max(), ys.min(), ys.max(), clipped, "  (idle rest frame)" if k in j["swap"] else ""))
    path = os.path.join(d, stem + ".png"); out.save(path)
    pl = {"format": "frame-placement/1", "animation": name, "file": stem + ".png", "frames": N, "fps": j["fps"]}; pl.update(j["extra"]); pl["frameInfo"] = info
    json.dump(pl, open(path.replace(".png", ".placement.json"), "w"), indent=1)
    W, H = out.size; pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
    for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
        cc = Image.new("RGBA", (W, H), bg); cc.alpha_composite(out); pic.paste(cc.convert("RGB"), (0, i * H))
    dr = ImageDraw.Draw(pic)
    for i in range(2):
        dr.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
        for k in range(1, N): dr.line([(k * FRAME, i * H), (k * FRAME, (i + 1) * H)], fill=(200, 0, 0), width=1)
    pic.resize((W // 2, H * 2 // 2), Image.LANCZOS).save(path.replace("_strip.png", "_check.png"))
    print("strip", os.path.relpath(path, EL))


for nm in (sys.argv[1:] or list(JOBS)):
    cut(nm)
