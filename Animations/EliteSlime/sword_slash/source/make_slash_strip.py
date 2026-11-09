#!/usr/bin/env python3
"""Cuts the Elite slime's SWORD SLASH sheet (the user's Gemini JPG inbox/elite_slime_sword_slash.jpg, 2752 x 1536, eight panels, 4 x 2, 2026-11-10) into the 8-frame strip.

  python Animations/EliteSlime/sword_slash/source/make_slash_strip.py

Three things the sheet needed that the idle sheet did not (see docs/MONSTERS.md):
  1. PANELS 6 AND 7 ARE ONE PIECE: the strike's blade (panel 6) was drawn ACROSS the border into panel 7's left skirt lump (its tip lies on it), so the two bodies were joined by the blade. elite_panels.load_panels(carves=...)
     takes the blade's lower part out of the picture before the pieces are found (polygon CARVE_REMOVE, from row 1325 down) and gives it to panel 6 (polygon CARVE_ASSIGN: the same plus the blade's dark outline on its right,
     which panel 7's lump keeps: its edge where the blade lay is then the blade's dark outline).
  2. THE BLADES LIE ACROSS THEIR OWN SKIRT (panels 6 and 7), so the body cannot be measured from the biggest piece alone: the base width, the floor row and the base centre come from the body seen through a
     morphological opening (open_measure: a thin blade vanishes, the skirt stays). The opening shaves the pebbly rim a little, so every width is multiplied by the factor measured on panel 1 (no sword over the skirt).
  3. THE GENERATOR DREW THE CREATURE BIGGER THAN ASKED (base 94% of a panel instead of 46%) and the strike's blade tip leaves the cell on the right: those panels get a size factor (MUL) and a shift (DX).
Every panel is scaled so that its BASE is BASE_W px wide (350, the idle's), the floor row y 470, the base centre x 259; MUL / DX are per-panel corrections printed in the report.
Output: ../elite_sword_slash_8frame_strip.png (+ .placement.json: fps 12, hitFrame 6), ../elite_sword_slash_8frame_check.png and a report.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "source"))
import elite_panels as ep

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "sword_slash_sheet.jpg")
OUT = os.path.join(HERE, "..", "elite_sword_slash_8frame_strip.png")
BASE_W, GROUND_Y, BASE_X, FRAME = 350.0, 470, 259, 512
MUL = {}            # panel index (0-based) -> extra size factor
DX = {5: -9}          # panel index (0-based) -> shift of the base centre in the cell (px): the strike (panel 6) blade tip would leave the cell by 6 px, the body shifts left 9 px (the page moves the whole sprite toward the target anyway)

# the strike's blade (panel 6, 0-based 5), read from a 4x gridded crop of the sheet (sheet coordinates)
R_EDGE = [(1352, 1262), (1390, 1300), (1412, 1335), (1452, 1382), (1472, 1400), (1490, 1420), (1505, 1462), (1511, 1474)]     # the blade's light face, upper right edge (white), tip last
L_EDGE = [(1330, 1287), (1370, 1337), (1392, 1365), (1430, 1402), (1460, 1435), (1490, 1457), (1511, 1474)]                      # the blade's lower left edge, tip last
off = lambda pts, dx, dy: [(x + dx, y + dy) for x, y in pts]
CARVE_ASSIGN = off(R_EDGE, 4, -3) + [(1514, 1477)] + off(L_EDGE[::-1], -5, 4)[1:]          # the blade with its outline on both sides
CARVE_REMOVE = off(R_EDGE, 3, -2) + off(L_EDGE[::-1], -5, 4)[0:]                                         # the same without the outline on the right: that thin dark line stays with panel 7's skirt lump
# rows 1318 to 1352: the blade WITH its right outline goes (the outline strip would otherwise join panel 6's blade above to panel 7's skirt lump below); from row 1352 down the right outline stays with the lump
CARVES = [{"remove": CARVE_ASSIGN, "assign": CARVE_ASSIGN, "to": 5, "y_min": 1318, "y_max": 1352},
          {"remove": CARVE_REMOVE, "assign": CARVE_ASSIGN, "to": 5, "y_min": 1353}]

if not os.path.isfile(SRC):
    import shutil; shutil.copyfile(os.path.join(ROOT, "inbox", "elite_slime_sword_slash.jpg"), SRC)
LUMP = (1395, 1395, 6)            # panel 7's left skirt lump (1618 px, 1374..1438 x 1368..1419): the blade of panel 6 lay across it and cut it off its skirt; it belongs to panel 7 (the distance rule gave it to panel 6)
data = ep.load_panels(SRC, [4, 4], carves=CARVES, force_owner=[LUMP]); P = data["panels"]


def fill_blade_gap(q, band_poly, r=30):
    """Panel 7: the blade of panel 6 lay over its left skirt lump and hid the stone behind it. After the carve the lump floats apart from the skirt; the gap (inside the blade's footprint, `band_poly`
    in sheet coordinates) is closed where stone lies on both sides (a morphological closing, disc r), painted from the stone around it (cv2.inpaint) and given the sheet's thin dark outline on its new rim."""
    import cv2
    p = q["p"].copy(); wx0, wy0 = q["origin"]; H, W = p.shape[:2]
    pad = 40
    al = np.pad(p[..., 3] > 128, pad)
    band = ep.poly_mask([(x - wx0 + pad, y - wy0 + pad) for x, y in band_poly], al.shape)
    band = ndi.binary_dilation(band, iterations=3)
    rgb0 = np.pad(p[..., :3], ((pad, pad), (pad, pad), (0, 0))).astype(int)
    steel = al & ndi.binary_dilation(band, iterations=5) & (rgb0.min(axis=2) > 140)                 # the blade's white edge and light face left along the cut: pale, stone is darker
    al = al & ~steel
    C = cv2.morphologyEx(al.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0
    F = C & ~al & band
    rgb = np.pad(p[..., :3], ((pad, pad), (pad, pad), (0, 0)))
    known = al; print("  steel pixels taken out of panel 7:", int(steel.sum()))
    stone = known & (rgb0.max(axis=2) > 70)                                                          # the fill is painted from STONE pixels only (not from the blade's dark outline lines)
    out = cv2.inpaint(np.ascontiguousarray(rgb), ((~stone) * 255).astype(np.uint8), 5, cv2.INPAINT_TELEA)
    ring = ndi.binary_dilation(F, iterations=3) & ~al & ~F & ndi.binary_dilation(band, iterations=8)
    full = np.dstack([np.where(F[..., None], out, rgb), np.where(F, 255, np.where(al, np.pad(p[..., 3], pad), 0))]).astype(np.uint8)
    full[ring & ~(full[..., 3] > 128)] = [36, 32, 40, 255]
    q["p"] = full[pad:-pad, pad:-pad]
    q["fill_px"] = int(F.sum())
    return q


P[6] = fill_blade_gap(P[6], CARVE_ASSIGN)
print("panel 7: gap filled, %d px" % P[6]["fill_px"])
m7 = P[6]["p"][..., 3] > 128                      # panel 7 measured on everything it now has (the lump is back): the opening removes the thin blades
P[6]["bw_open"], P[6]["low_open"], P[6]["mid_open"] = ep.open_measure(m7)

c = P[0]["bw"] / float(P[0]["bw_open"])           # the opening's shave, measured where there is nothing to remove
print("opening factor (panel 1: raw base width / opened base width): %.3f" % c)
out = Image.new("RGBA", (FRAME * 8, FRAME), (0, 0, 0, 0))
info = []
print("panel | base w raw / opened | scale | eyes above ground | base w | figure x range | top y | bottom y | clipped px | right edge before clipping")
for k, q in enumerate(P):
    bw = q["bw_open"] * c
    sc = BASE_W / bw * MUL.get(k, 1.0)
    ox = int(round(BASE_X + DX.get(k, 0) - q["mid_open"] * sc)); oy = int(round(GROUND_Y - q["low_open"] * sc))
    fr, clipped = ep.place(q, sc, ox, oy)
    arr = np.array(fr); a = arr[..., 3] > 128; ys, xs = np.where(a)
    R, G, B = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    amber = ndi.binary_opening(a & (R > 200) & (G > 110) & (G < 215) & (B < 110), structure=np.ones((3, 3)))
    lab, n = ndi.label(amber); ey = float("nan")
    if n:
        sz = ndi.sum(amber, lab, range(1, n + 1)); top2 = np.argsort(sz)[::-1][:2]
        ey = GROUND_Y - float(np.mean([ndi.center_of_mass(lab == (i + 1))[0] for i in top2]))
    out.alpha_composite(fr, (FRAME * k, 0))
    unclipped_right = ox + (q["box"][2] + 1) * sc
    info.append({"lift": 0.0, "top": int(ys.min()), "bottom": int(ys.max()), "baseW": round(bw * sc, 1), "sizeAgainstIdle": round(sc * bw / BASE_W, 3)})
    print("  %d   | %4d / %4d | %.3f |  %5.1f  | %.0f | %3d..%3d | %3d | %3d | %d | %.0f" % (k + 1, q["bw"], q["bw_open"], sc, ey, bw * sc, xs.min(), xs.max(), ys.min(), ys.max(), clipped, unclipped_right))
out.save(OUT)
# where the blade's tip is on the frames the page needs (cell coordinates of the 512 cell, before the page mirrors the sprite): frame 5 (the chop begins: the sword is up and back, the tip is the highest point)
# and frame 6 (the strike: the tip is the right-most point). The page lands the strike's tip on the target and draws the slash's trail between the two.
tips = {}
for fi, how in ((5, "top"), (6, "right")):
    a = np.array(out.crop(((fi - 1) * FRAME, 0, fi * FRAME, FRAME)))[..., 3] > 128; ys, xs = np.where(a)
    j = int(np.argmin(ys)) if how == "top" else int(np.argmax(xs))
    tips[str(fi)] = {"x": int(xs[j]), "y": int(ys[j])}
print("blade tips:", tips)
json.dump({"format": "frame-placement/1", "animation": "sword_slash", "file": os.path.basename(OUT), "frames": 8, "fps": 12, "hitFrame": 6, "tips": tips, "frameInfo": info},
          open(OUT.replace(".png", ".placement.json"), "w"), indent=1)
W, H = out.size
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    cc = Image.new("RGBA", (W, H), bg); cc.alpha_composite(out); pic.paste(cc.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2):
    d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
    for k in range(1, 8): d.line([(k * FRAME, i * H), (k * FRAME, (i + 1) * H)], fill=(200, 0, 0), width=1)
pic.resize((W // 2, H * 2 // 2), Image.LANCZOS).save(os.path.join(HERE, "..", "elite_sword_slash_8frame_check.png"))
print("strip", os.path.abspath(OUT))
