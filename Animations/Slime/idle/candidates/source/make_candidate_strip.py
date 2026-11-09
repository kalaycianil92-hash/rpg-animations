#!/usr/bin/env python3
"""Cuts one candidate idle sheet of the re-looked fire slime into a 6-frame strip (2026-11-07).

  python Animations/Slime/idle/candidates/source/make_candidate_strip.py gpt
  python Animations/Slime/idle/candidates/source/make_candidate_strip.py gemini

Needs  <tag>_idle_sheet.(png|jpg)  in this folder (the user's sheet). Steps:
  1. equalize_sheet.py re-lays the six creatures into equal cells (so a flame or ember that crosses the middle line cannot
     go to the wrong panel) -> <tag>_equal_sheet.png
  2. a first cut with ONE scale from panel 1's base width (350 px in the 512 cell, the project's monster standard)
  3. the generators draw some panels bigger than others (the first sheet: the bottom row 7% bigger), so the face of each frame is
     measured by template matching (first the old slime's face finds panel 1's face, then panel 1's own face is the template),
     and each panel gets the scale correction  face(panel 1) / face(panel k)
  4. the final cut with those corrections -> ../<tag>_fire_idle_strip.png, a check picture and a report
"""
import glob, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

tag = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
SRC = glob.glob(os.path.join(HERE, tag + "_idle_sheet.*"))[0]
EQ = os.path.join(HERE, tag + "_equal_sheet.png")
OUT = os.path.join(HERE, "..", tag + "_fire_idle_strip.png")
TMP = os.path.join(HERE, "_tmp_" + tag + ".png")
TOOLS = os.path.join(ROOT, "source", "tools")
py = sys.executable

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    return r.stdout

print(run([py, os.path.join(TOOLS, "equalize_sheet.py"), SRC, EQ]))
CUT = [py, os.path.join(TOOLS, "slice_keypose_sheet.py"), EQ, None, "--cols", "3", "--rows", "2", "--base-width", "350",
       "--scale-from", "panel1", "--keep-near", "0.25", "--modes", "feet", "--feet-x", "256", "--despill-band", "10", "--despill-thr", "4"]
cmd = list(CUT); cmd[3 - 1 + 0] = cmd[2]; cmd[3] = EQ
cmd = [py, os.path.join(TOOLS, "slice_keypose_sheet.py"), EQ, TMP] + CUT[4:]
print(run(cmd))

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

old = np.array(Image.open(os.path.join(ROOT, "Animations", "Slime", "idle", "fire_idle_strip.png")).convert("RGBA"))[:, :512]
tx, ty, tw, th = 250, 300, 130, 80                              # the old slime's face in its cell (the same place in every look: the generators trace the reference)
t_old = gray(old)[ty:ty + th, tx:tx + tw]
g1 = gray(frames[0])
mv, s1, loc = best_match(g1, t_old, 0.7, 1.4)
print("stage 1: old face found in frame 1: match %.2f at scale %.2f, at %s" % (mv, s1, loc))
tw1, th1 = int(round(tw * s1)), int(round(th * s1))
t_own = g1[loc[1]:loc[1] + th1, loc[0]:loc[0] + tw1]            # frame 1's own face
scales, scores = [1.0], [1.0]
for k in range(1, 6):
    mv, s, loc_k = best_match(gray(frames[k]), t_own, 0.8, 1.25)
    scales.append(s); scores.append(mv)
mults = [round(1.0 / s, 3) for s in scales]
print("face scale of each frame against frame 1:", [round(s, 2) for s in scales], "match", [round(x, 2) for x in scores])
print("scale-mult:", ",".join(str(m) for m in mults))
if min(scores[1:]) < 0.5:
    print("WARNING: a weak match (%.2f): check that frame's size by eye" % min(scores[1:]))

print(run([py, os.path.join(TOOLS, "slice_keypose_sheet.py"), EQ, OUT, "--cols", "3", "--rows", "2", "--base-width", "350", "--scale-from", "panel1",
           "--scale-mult", ",".join(str(m) for m in mults), "--keep-near", "0.25", "--modes", "feet", "--feet-x", "256",
           "--despill-band", "10", "--despill-thr", "4"]))
os.remove(TMP)

# The report and the squash data (2026-11-07: the user found the squash and stretch frames too heavy and asked to tune them down). Per frame: the base width
# (the widest row in the lowest 22% of the figure), the height of the face above the ground line (frame 1's own face matched with separate x and y scales:
# a squashed face is flatter, so a uniform scale does not match it) and the top of the figure. The page's "Squash and stretch" slider takes a chosen share
# of the deformation out of each frame: it scales a frame about the soles and the base centre by (1 + a (r - 1)) / r in y and (1 + a (q - 1)) / q in x, where r is
# the frame's face height and q its base width, both against frame 1; a = 1 leaves the frame as drawn, 0 gives every frame the proportions of frame 1.
import json
def match_aniso(g, tmpl):
    best = (-1, 1.0, 1.0, (0, 0))
    reg = g[150:480, 100:480]
    for sy in np.arange(0.45, 1.25, 0.025):
        for sx in np.arange(0.85, 1.35, 0.025):
            ts = cv2.resize(tmpl, None, fx=sx, fy=sy, interpolation=cv2.INTER_AREA)
            if ts.shape[0] >= reg.shape[0] or ts.shape[1] >= reg.shape[1]: continue
            _, mv, _, loc = cv2.minMaxLoc(cv2.matchTemplate(reg, ts, cv2.TM_CCOEFF_NORMED))
            if mv > best[0]: best = (mv, sx, sy, (loc[0] + 100, loc[1] + 150, ts.shape[0], ts.shape[1]))
    return best
st = np.array(Image.open(OUT).convert("RGBA"))
rows = []
for k in range(6):
    f = st[:, k * 512:(k + 1) * 512]; a = f[..., 3] > 128
    lab, n = ndi.label(a); sz = ndi.sum(a, lab, range(1, n + 1)); main = lab == 1 + int(np.argmax(sz))
    my, mx = np.where(main); y0, y1 = my.min(), my.max()
    bw = max(mx[my == y].max() - mx[my == y].min() for y in range(int(y1 - 0.22 * (y1 - y0)), y1 + 1) if (my == y).any())
    mv, sx, sy, (lx, ly, th_, tw_) = match_aniso(gray(f), t_own)
    fh = 470 - (ly + th_ / 2)
    ys, xs = np.where(a)
    rows.append((bw, fh, sy, mv, ys.min(), xs.min(), xs.max()))
print("frame | base w | face height above ground | face y scale | match | top y | bbox x")
for k, (bw, fh, sy, mv, top, x0, x1) in enumerate(rows):
    print("  %d   |  %3d   |        %5.1f              |    %.3f     | %.2f  |  %3d  | %d..%d" % (k + 1, bw, fh, sy, mv, top, x0, x1))
R = [round(r[1] / rows[0][1], 3) for r in rows]
Q = [round(r[0] / rows[0][0], 3) for r in rows]
print("height ratio r:", R, "| base width ratio q:", Q)
SQ = os.path.join(os.path.dirname(OUT), tag + "_fire_idle_strip.squash.json")
json.dump({"note": "per-frame proportions of the drawn slime against frame 1: h = height of the face above the ground, w = width of the base; the page undoes a chosen share of the deformation",
           "h": R, "w": Q, "match": [round(r[3], 2) for r in rows]}, open(SQ, "w"), indent=1)
print("wrote", os.path.abspath(SQ))

# check picture on white and forest green
W, H = st.shape[1], st.shape[0]
img = Image.fromarray(st)
pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
    c = Image.new("RGBA", (W, H), bg); c.alpha_composite(img); pic.paste(c.convert("RGB"), (0, i * H))
d = ImageDraw.Draw(pic)
for i in range(2): d.line([(0, i * H + 470), (W, i * H + 470)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
pic.resize((W * 2 // 3, H * 2 * 2 // 3), Image.LANCZOS).save(os.path.join(HERE, "..", tag + "_fire_idle_check.png"))
print("strip", os.path.abspath(OUT))
