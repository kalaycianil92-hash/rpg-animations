#!/usr/bin/env python3
"""Recolours the Permafrost Execution's X (pf_cross, pf_cross_ice) from its glacier teal into Winter's Kiss's periwinkle frost (2026-11-25, the user: "Permafrost execution and Winter's kiss have
different ice effects, it should be the same color at least. Let's use Winter's kiss style for both").

The teal originals are in teal_fx_originals/ next to this script (with the crowns, the burst and the streak, which the page no longer uses: Winter's Kiss's own pictures stand in for them). Both sheets keep
the blue channel full and differ in the other two: teal brightens from (0, 190, 255) to white, the Kiss frost from (20, 45, 255) through (155, 172, 255) to white. So every pixel keeps its alpha and its
brightness, and takes the colour the Kiss frost has at that brightness (measured on the five rf_*.png pictures, averaged per brightness step).

  python Animations/Rogue/permafrost_execution/source/make_pf_kiss_colours.py      (writes source/assets/fx/pf_cross.png and pf_cross_ice.png)
"""
import pathlib
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FX = ROOT / "source" / "assets" / "fx"


def lum(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


# the Kiss frost's colour at each brightness: the mean colour of the rf pictures' visible pixels per brightness step of 8
edges = np.arange(0, 264, 8)
acc = np.zeros((len(edges) - 1, 3)); cnt = np.zeros(len(edges) - 1)
for n in ("rf_burst", "rf_ground", "rf_band", "rf_trail", "rf_blade"):
    a = np.array(Image.open(FX / (n + ".png")).convert("RGBA")).astype(np.float64)
    m = a[..., 3] > 40
    L = lum(a[..., :3])[m]; c = a[..., :3][m]
    idx = np.clip(np.digitize(L, edges) - 1, 0, len(edges) - 2)
    np.add.at(acc, idx, c); np.add.at(cnt, idx, 1)
ok = cnt > 30
mids = ((edges[:-1] + edges[1:]) / 2)[ok]
ramp = acc[ok] / cnt[ok][:, None]
print("Kiss ramp:", [(int(m), tuple(int(v) for v in r)) for m, r in zip(mids[::4], ramp[::4])])

for n in ("pf_cross", "pf_cross_ice"):
    a = np.array(Image.open(HERE / "teal_fx_originals" / (n + ".png")).convert("RGBA")).astype(np.float64)
    L = lum(a[..., :3])
    out = a.copy()
    for ch in range(3):
        out[..., ch] = np.interp(L, mids, ramp[:, ch])
    Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), "RGBA").save(FX / (n + ".png"))
    print("wrote", FX / (n + ".png"))
