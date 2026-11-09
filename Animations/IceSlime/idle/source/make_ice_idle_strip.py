#!/usr/bin/env python3
"""Cuts the ice slime's idle sheet (the user's Gemini JPG, 2752 x 1536, six panels, 3 x 2) into the 6-frame strip (2026-11-08).

  python Animations/IceSlime/idle/source/make_ice_idle_strip.py

The fire slime's candidate cutter (Animations/Slime/idle/candidates/source/make_candidate_strip.py) for the ice slime:
  1. equalize_sheet.py re-lays the six creatures into equal cells (the wide ice slime nearly fills its 917 px panel, a crystal or snowflake must not go to the wrong panel);
  2. a first cut with ONE scale from panel 1's base width (350 px in the 512 cell, the monster standard);
  3. the face of each frame is measured by template matching (panel 1's own face is the template; the ice slime's face is at the same place as in the test cut of the reference: x 255..405, y 295..405
     of the 512 cell) and each panel gets the scale correction face(panel 1) / face(panel k);
  4. the final cut with those corrections, a check picture, and the squash data (per frame: the face's height above the ground and the base width against frame 1) the page's Squash and stretch slider uses.
Output: ../ice_idle_strip.png, ../ice_idle_strip.squash.json, ../ice_idle_check.png and a report.
"""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = os.path.join(HERE, "ice_idle_sheet.jpg")
EQ = os.path.join(HERE, "ice_equal_sheet.png")
OUT = os.path.join(HERE, "..", "ice_idle_strip.png")
TMP = os.path.join(HERE, "_tmp_first.png")
TOOLS = os.path.join(ROOT, "source", "tools")
py = sys.executable
FACE = (255, 295, 150, 110)                                    # x, y, w, h of the face in frame 1 of the first cut

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    return r.stdout

print(run([py, os.path.join(TOOLS, "equalize_sheet.py"), SRC, EQ]))
CUT = ["--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1", "--keep-near", "0.25", "--modes", "feet", "--feet-x", "256", "--despill-band", "10", "--despill-thr", "4"]
print(run([py, os.path.join(TOOLS, "slice_keypose_sheet.py"), EQ, TMP] + CUT))
strip = np.array(Image.open(TMP).convert("RGBA"))
frames = [strip[:, i * 512:(i + 1) * 512] for i in range(6)]

def gray(f):
    g = cv2.cvtColor(f[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32); g[f[..., 3] < 128] = 0; return g

def best_match(g, tmpl, lo, hi):
    best = (-1, 1.0, (0, 0))
    for s in np.arange(lo, hi, 0.01):
        ts = cv2.resize(tmpl, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        if ts.shape[0] >= g.shape[0] or ts.shape[1] >= g.shape[1]: continue
        r = cv2.matchTemplate(g, ts, cv2.TM_CCOEFF_NORMED); _, mv, _, loc = cv2.minMaxLoc(r)
        if mv > best[0]: best = (mv, s, loc)
    return best

fx, fy, fw, fh_ = FACE
g1 = gray(frames[0])
t_own = g1[fy:fy + fh_, fx:fx + fw]
scales, scores = [1.0], [1.0]
for k in range(1, 6):
    mv, s, loc_k = best_match(gray(frames[k]), t_own, 0.85, 1.2)
    scales.append(s); scores.append(mv)
mults = [round(1.0 / s, 3) for s in scales]
print("face scale of each frame against frame 1:", [round(s, 2) for s in scales], "match", [round(x, 2) for x in scores])
print("scale-mult:", ",".join(str(m) for m in mults))
if min(scores[1:]) < 0.5:
    print("WARNING: a weak match (%.2f): check that frame's size by eye" % min(scores[1:]))
print(run([py, os.path.join(TOOLS, "slice_keypose_sheet.py"), EQ, OUT] + CUT + ["--scale-mult", ",".join(str(m) for m in mults)]))
os.remove(TMP)

def match_aniso(g, tmpl):                                      # the face with separate x and y scales (a squashed face is flatter)
    best = (-1, 1.0, 1.0, (0, 0))
    reg = g[150:480, 100:500]
    for sy in np.arange(0.8, 1.2, 0.02):
        for sx in np.arange(0.85, 1.2, 0.02):
            ts = cv2.resize(tmpl, None, fx=sx, fy=sy, interpolation=cv2.INTER_AREA)
            if ts.shape[0] >= reg.shape[0] or ts.shape[1] >= reg.shape[1]: continue
            _, mv, _, loc = cv2.minMaxLoc(cv2.matchTemplate(reg, ts, cv2.TM_CCOEFF_NORMED))
            if mv > best[0]: best = (mv, sx, sy, (loc[0] + 100, loc[1] + 150, ts.shape[0], ts.shape[1]))
    return best
st = np.array(Image.open(OUT).convert("RGBA"))
g1c = gray(st[:, :512]); t_final = g1c[fy:fy + fh_, fx:fx + fw]
rows = []
for k in range(6):
    f = st[:, k * 512:(k + 1) * 512]; a = f[..., 3] > 128
    lab, n = ndi.label(a); sz = ndi.sum(a, lab, range(1, n + 1)); main = lab == 1 + int(np.argmax(sz))
    my, mx = np.where(main); y0, y1 = my.min(), my.max()
    bw = max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any())
    mv, sx, sy, (lx, ly, th_, tw_) = match_aniso(gray(f), t_final)
    ys, xs = np.where(a)
    rows.append((bw, 470 - (ly + th_ / 2), sy, mv, ys.min(), xs.min(), xs.max(), int(np.where(main[:, :].any(1))[0].min())))
print("frame | base w | face height above ground | face y scale | match | top y | bbox x | dome-less top")
for k, (bw, fh, sy, mv, top, x0, x1, mt) in enumerate(rows):
    print("  %d   |  %3d   |        %5.1f              |    %.3f     | %.2f  |  %3d  | %d..%d" % (k + 1, bw, fh, sy, mv, top, x0, x1))
R = [round(r[1] / rows[0][1], 3) for r in rows]
Q = [round(r[0] / rows[0][0], 3) for r in rows]
print("height ratio r:", R, "| base width ratio q:", Q)
SQ = os.path.join(os.path.dirname(OUT), "ice_idle_strip.squash.json")
json.dump({"note": "per-frame proportions of the drawn slime against frame 1: h = height of the face above the ground, w = width of the base; the page undoes a chosen share of the deformation",
           "h": R, "w": Q, "match": [round(r[3], 2) for r in rows]}, open(SQ, "w"), indent=1)
W, H = st.shape[1], st.shape[0]
img = Image.fromarray(st)
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(img); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(os.path.join(HERE, "..", "ice_idle_check.png"))
print("strip", os.path.abspath(OUT))
