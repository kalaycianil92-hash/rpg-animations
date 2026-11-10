#!/usr/bin/env python3
"""Cuts the Slime King's sheets (the user's ChatGPT PNG/JPGs, magenta key, 2026-11-11) into 512 px strips, with the Elite's machinery (Animations/EliteSlime/source/elite_panels.py: the body is the biggest piece of a
panel, the floating glove with its staff is a detached piece that goes to the nearest body, the magenta is keyed with `1 - clip((min(r, b) - g - 70) / 110, 0, 1)` and the soft edges are despilled).

  python Animations/SlimeKing/source/cut_king.py [idle] [hit] [death] [dodge]        (default: all)

Every panel is placed so that its floor row (the body's lowest row, measured through a morphological opening) is on y 470 and its base centre on x 259, at ONE scale for the whole sheet:
  idle   the median of the panels' opened base widths -> base 350 px (the generator kept the base within 2%)
  hit, death, dodge   an explicit `scale` (2026-11-11): the three sheets are 2528 x 1696 and the creature is drawn at 0.57 to 0.585 of its idle-strip size; the scale is where the RIGID parts (the crown and the staff:
                      their gold pixel area against the idle strip's, gold_king.py in the scratchpad) and the first panel's base agree: the dodge 0.585 (both agree), the death 0.585, the hit 0.57 (the hit sheet drew the
                      crown and staff 3% bigger against the base: halfway between the two readings).
JOBS options (as in the Elite's cut_pack.py): rows, order (the sheet panels used, in strip order; "idle" = the idle strip's frame 1, the REST pose), airborne (SOURCE panels the generator lifted off the floor: placed at
their real height above the floor line of their row, times `liftMul`), prep (a module in <folder>/source with clean(src, out): the dodge's text labels painted out), drop (the King's death: the glove or the staff the
generator drew BELOW the floor line would be cut by the 512 cell: the piece is moved up, only as far as needed). Output per animation: <folder>/king_<name>_<N>frame_strip.png + .placement.json + a check picture.
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
IDLE = os.path.join(KING, "idle", "king_idle_strip.png")
JOBS = {
    "idle": dict(file="slime_king_idle_sheet.png", folder="idle", rows=[3, 3], fps=5, name="idle", extra={}),
    # HIT: the generator drew the six panels in another order than asked. Panel 3 (a neutral face, the staff dropped and cut by the sheet's right edge) is NOT used; panel 6 (a grimace, the glove holding the staff)
    # is the third frame, then panel 5 and 4 (the smile coming back) and the idle's rest frame for the last (the generator's own 'rest' panels have a grimace or a different pose).
    "hit": dict(file="slime_king_hit_sheet.jpg", folder="hit", rows=[3, 3], fps=12, name="hit", scale=0.57, order=[0, 1, 5, 4, 3, "idle"], extra={}),
    # DEATH: shared scale; the glove or staff lying lower than the puddle must fit in the 512 cell (drop)
    "death": dict(file="slime_king_death_sheet.jpg", folder="death", rows=[3, 3], fps=8, name="death", scale=0.585, order=[0, 1, 2, 3, 4, 5], drop=True, slide="pieces",
                  extra={"holds": [1, 1.2, 1.3, 1.3, 1.5, 3]}),
    # DODGE: the dodge sheet came with the generator's text labels (dodge_prep.py paints them out); panel 4 (the apex) is lifted 198 sheet px off the floor (23% of the panel's height, the prompt asked 6%):
    # drawn at liftMul 0.5 here (a heavy King hops, it does not leap); the first and the last panels (grimaces, not the idle's smile) are replaced by the idle's rest frame
    "dodge": dict(file="slime_king_dodge_sheet.jpg", folder="dodge", rows=[3, 3], fps=12, name="dodge", scale=0.585, order=["idle", 1, 2, 3, 4, "idle"], airborne=[3], liftMul=0.5, drop=True, prep="dodge_prep",
                  extra={"evadeFrame": 4, "smooth": True, "xUnit": "character-widths", "x": [0, -0.02, -0.06, -0.1, -0.06, -0.02], "y": [0, 0, 0, 0, 0, 0]}),
}


def fit_pieces(q, sc, ox, oy):
    """The detached pieces of a panel (glove, staff, a fallen crown) that stick out of the 512 cell: the overflowing ones and every piece within 40 sheet px of them move as ONE group, left and/or up by the overflow
    (the body stays where it is). Returns dict(frame, clipped, dx, dy) or None."""
    f = q["fist"]; pa = q["p"]; lab, n = ndi.label(f); ext = {}
    for i in range(1, n + 1):
        ys_, xs_ = np.where(lab == i)
        ext[i] = (ox + xs_.min() * sc, ox + (xs_.max() + 1) * sc, oy + ys_.min() * sc, oy + (ys_.max() + 1) * sc)
    bad = [i for i, e in ext.items() if e[1] > FRAME - 3 or e[3] > FRAME - 3 or e[0] < 3]
    if not bad: return None
    dist = ndi.distance_transform_edt(~np.isin(lab, bad))
    group = [i for i in ext if i in bad or dist[lab == i].min() < 40]
    gx1 = max(ext[i][1] for i in group); gy1 = max(ext[i][3] for i in group); gx0 = min(ext[i][0] for i in group)
    dx = -int(np.ceil(max(0, gx1 - (FRAME - 3)))); dy = -int(np.ceil(max(0, gy1 - (FRAME - 3))))
    if gx0 + dx < 3: dx = int(np.ceil(3 - gx0))
    gm = ndi.binary_dilation(np.isin(lab, group), iterations=4) & (pa[..., 3] > 0) & ~q["main"]
    rest = pa.copy(); rest[..., 3] = np.where(gm, 0, pa[..., 3]); grp = pa.copy(); grp[..., 3] = np.where(gm, pa[..., 3], 0)
    qr = dict(q); qr["p"] = rest; fr, c0 = ep.place(qr, sc, ox, oy)
    qg = dict(q); qg["p"] = grp; f2, c2 = ep.place(qg, sc, ox + dx, oy + dy); fr.alpha_composite(f2)
    return {"frame": fr, "clipped": c0 + c2, "dx": dx, "dy": dy}


def cut(name):
    j = JOBS[name]
    d = os.path.join(KING, j["folder"]); os.makedirs(os.path.join(d, "source"), exist_ok=True)
    src = os.path.join(d, "source", j["folder"] + "_sheet" + os.path.splitext(j["file"])[1])
    if not os.path.isfile(src):
        for cand in (os.path.join(ROOT, "inbox", j["file"]), os.path.join(ROOT, "inbox", "Slime_king", j["file"])):
            if os.path.isfile(cand): shutil.copyfile(cand, src); break
    if j.get("prep"):
        sys.path.insert(0, os.path.join(d, "source")); mod = __import__(j["prep"]); clean = os.path.join(d, "source", j["folder"] + "_sheet_clean.png"); src = mod.clean(src, clean)
    rows = j["rows"]; NS = sum(rows)
    P = ep.load_panels(src, rows)["panels"]
    c = P[0]["bw"] / float(P[0]["bw_open"])
    bws = [q["bw_open"] * c for q in P]
    sc = j["scale"] if "scale" in j else BASE_W / float(np.median(bws))
    order = j.get("order", list(range(NS))); N = len(order)
    air = j.get("airborne", []); lmul = j.get("liftMul", 1.0)
    floor = {}                                                                          # the floor of a row (sheet y): the median floor of its grounded panels
    for r in range(len(rows)):
        ys = [P[k]["origin"][1] + P[k]["low_open"] for k in range(NS) if P[k]["row"] == r and k not in air]
        floor[r] = float(np.median(ys))
    print("== %s | opening factor %.3f | base widths (opened) %s | scale %.3f%s" % (name, c, [int(b) for b in bws], sc, "" if "scale" not in j else " (explicit)"))
    print("  strip | sheet | x range | y range | lift | clipped px")
    idle1 = Image.open(IDLE).convert("RGBA").crop((0, 0, FRAME, FRAME))
    out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0)); info = []
    for k, s in enumerate(order):
        if s == "idle":
            fr = idle1.copy(); a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
            out.alpha_composite(fr, (FRAME * k, 0))
            info.append({"top": int(ys.min()), "bottom": int(ys.max()), "replacedByIdleRest": True})
            print("  %d | idle rest | x %3d..%3d | y %3d..%3d" % (k + 1, xs.min(), xs.max(), ys.min(), ys.max())); continue
        q = P[s]; wx0, wy0 = q["origin"]
        lift = (floor[q["row"]] - (wy0 + q["low_open"])) * sc * lmul if s in air else 0.0
        ox = int(round(BASE_X - q["mid_open"] * sc)); oy = int(round(GROUND_Y - q["low_open"] * sc - lift))
        bx0, by0, bx1, by1 = q["box"]; slide = 0
        if j.get("slide", "frame") == "frame":                                              # the staff or glove the generator flung out sideways would be cut by the cell's edge: the WHOLE frame (body and pieces)
            if ox + (bx1 + 1) * sc > FRAME - 3: slide = int(np.ceil(ox + (bx1 + 1) * sc - (FRAME - 3))); ox -= slide   # slides left by the overflow (a recoil), so nothing is cut and nothing overlaps
            if ox + bx0 * sc < 3: ox += int(np.ceil(3 - (ox + bx0 * sc)))
        fr, clipped = ep.place(q, sc, ox, oy)
        moved = None
        if clipped and j.get("drop"):                                                       # a detached piece (the glove and the staff lying on the floor) is cut by the cell: it and the pieces next to it move left / up as a group, only as far as needed
            moved = fit_pieces(q, sc, ox, oy)
            if moved:
                fr = moved["frame"]; clipped = moved["clipped"]
        a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
        out.alpha_composite(fr, (FRAME * k, 0))
        info.append({"sheetPanel": s + 1, "lift": round(lift, 1), **({"slideLeft": slide} if slide else {}), "top": int(ys.min()), "bottom": int(ys.max()), "left": int(xs.min()), "right": int(xs.max()), **({"detachedPiecesMoved": {"dx": moved["dx"], "dy": moved["dy"]}} if moved else {})})
        print("  %d | %d | x %3d..%3d | y %3d..%3d | lift %5.1f | clipped %d%s%s" % (k + 1, s + 1, xs.min(), xs.max(), ys.min(), ys.max(), lift, clipped, ("  pieces moved dx %d dy %d" % (moved["dx"], moved["dy"])) if moved else "", ("  slid left %d" % slide) if slide else ""))
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
