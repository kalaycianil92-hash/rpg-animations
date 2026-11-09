"""(Lightning slime copy of ice_cut.py, 2026-11-09: uses light_panels; shared=True gives every panel the scale of panel 1.)"""
"""The common cut of the ice slime's airborne / irregular sheets (2026-11-08), on top of ice_panels.py.

build_strip(...): one scale per row (the top row from panel 1 = base 350 px, the bottom row from its LAST panel, a rest-like pose, rest_mul times 350 px), every GROUNDED panel on its own floor (the lowest point of its
body on y 470), an airborne panel at its real height above its row's floor (the median of the row's grounded panels; raised if it would hang below y 478), the grounded bases centred on x 256 (the ice idle's base centre) and
the airborne ones in between; a part below the cell's bottom fades out instead of being cut. Writes the strip, a check picture (white and forest green, the floor line drawn) and the placement json.
"""
import json, os
import numpy as np
from PIL import Image, ImageDraw
import light_panels as ip


def build_strip(SRC, OUT, CHECK, PLACE, row_counts, grounded, animation, fps, hit_frame=None, last_rest=True, rest_mul=(1.0, 1.0), extra=None, shared=False, mul=None):
    BASE_W, GROUND_Y, BASE_X, FRAME = 350, 470, 259, 512
    data = ip.load_panels(SRC, row_counts); P = data["panels"]; N = len(P); ROWS = len(row_counts)
    bws = [q["bw"] for q in P]
    first_of_row, last_of_row = {}, {}
    for k, q in enumerate(P):
        first_of_row.setdefault(q["row"], k); last_of_row[q["row"]] = k
    sk = []
    for k, q in enumerate(P):
        if shared: sk.append(BASE_W / float(bws[0]))                                  # ONE scale from panel 1 (a body that collapses cannot be sized by its own base)
        elif q["row"] == 0: sk.append(BASE_W * rest_mul[0] / float(bws[0]))
        else: sk.append(BASE_W * rest_mul[1] / float(bws[last_of_row[1]]) if last_rest else BASE_W / float(bws[first_of_row[1]]))
    for kk, mm in (mul or {}).items(): sk[kk] *= mm                                      # per-panel size corrections (0-based panel: factor), for a panel whose burst would not fit the cell or a shrink the generator under-delivered
    ground = {rr: float(np.median([P[k]["low"] for k in grounded if P[k]["row"] == rr])) for rr in range(ROWS)}
    sh = {k: BASE_X - ip.base_mid(P[k]) * sk[k] for k in grounded}
    shifts = {}
    for k in range(N):
        before = [q for q in grounded if q <= k]; after = [q for q in grounded if q >= k]
        if k in sh: shifts[k] = sh[k]
        else: shifts[k] = sh[before[-1]] + (sh[after[0]] - sh[before[-1]]) * (k - before[-1]) / float(after[0] - before[-1])
    out = Image.new("RGBA", (FRAME * N, FRAME), (0, 0, 0, 0))
    info = []
    print("tips repaired: %d; scales %s; base widths in the sheet %s; floors %s" % (data["tips"], sorted(set(round(x, 4) for x in sk)), bws, {r: int(v) for r, v in ground.items()}))
    print("panel | lift of the body above the floor (px, in the 512 cell) | base width (px) | figure top y | figure bottom y | clipped | faded | x range")
    for k, q in enumerate(P):
        rr = q["row"]; ox = int(round(shifts[k]))
        if k in grounded:
            oy = int(round(GROUND_Y - q["low"] * sk[k])); lift = 0.0
        else:
            oy = int(round(GROUND_Y - ground[rr] * sk[k])); lift = (ground[rr] - q["low"]) * sk[k]
            low_y = oy + q["low"] * sk[k]
            if low_y > GROUND_Y + 8: oy -= int(round(low_y - (GROUND_Y + 8)))            # a pointed bottom hanging below the floor line: raised
        fr, clipped, faded = ip.place(q, sk[k], ox, oy)
        a = np.array(fr)[..., 3] > 128; ys, xs = np.where(a)
        print("  %d   |   %6.1f | %5.1f | %3d | %3d | %d | %d | %d..%d" % (k + 1, lift, q["bw"] * sk[k], ys.min(), ys.max(), clipped, faded, xs.min(), xs.max()))
        out.alpha_composite(fr, (FRAME * k, 0))
        info.append({"lift": round(float(lift), 1), "top": int(ys.min()), "bottom": int(ys.max()), "baseW": round(float(q["bw"] * sk[k]), 1), "sizeAgainstIdle": round(float(q["bw"] * sk[k] / BASE_W), 3)})
    out.save(OUT)
    pl = {"format": "frame-placement/1", "animation": animation, "file": os.path.basename(OUT), "frames": N, "fps": fps, "frameInfo": info}
    if hit_frame: pl["hitFrame"] = hit_frame
    if extra: pl.update(extra)
    json.dump(pl, open(PLACE, "w"), indent=1)
    W, H = out.size
    pic = Image.new("RGB", (W, H * 2), (255, 255, 255))
    for i, bg in enumerate([(255, 255, 255, 255), (38, 84, 52, 255)]):
        c = Image.new("RGBA", (W, H), bg); c.alpha_composite(out); pic.paste(c.convert("RGB"), (0, i * H))
    d = ImageDraw.Draw(pic)
    for i in range(2): d.line([(0, i * H + GROUND_Y), (W, i * H + GROUND_Y)], fill=(0, 0, 0) if i == 0 else (255, 255, 255), width=1)
    pic.resize((W // 2, H), Image.LANCZOS).save(CHECK)
    print("strip", os.path.abspath(OUT))
    return info
