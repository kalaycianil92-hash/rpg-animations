#!/usr/bin/env python3
"""Makes rf_band.png, the picture of Winter's Kiss's spinning waist ring, from the user's frost sheet (rf_halo_b.png, the full vertical hoarfrost cage).

The user (2026-11-04): "I don't really like the halo design for rogue as the aura, is it possible to change it to horizontal halo which spins around rogue, centering the waist area?"
The vertical oval cage is UNWRAPPED: for every angle round the oval and every distance from its middle line, the picture is sampled (elliptical polar coordinates), giving a long
strip that is the cage stretched out along its length, the crystals of the outer edge at the TOP and those of the inner edge at the BOTTOM, seamless where it closes (angle 0 and 360).
The page wraps that strip round a flat ring at waist height and turns it (docs/DEV_NOTES.md, kissRingDraw).

  python make_kiss_band.py        (writes source/assets/fx/rf_band.png and prints the numbers it measured)
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[4]
SRC = ROOT / "Animations" / "Rogue" / "dagger_throw" / "source" / "frost_cut" / "rf_halo_b.png"      # cut from the user's frost sheet (not embedded in the page any more: only the band made from it is)
DST = ROOT / "source" / "assets" / "fx" / "rf_band.png"
W_OUT, H_OUT = 1200, 176
RHO0, RHO1 = 0.45, 1.50                  # inner and outer edge of the sampled band, as a multiple of the ring's middle-line radius

im = np.array(Image.open(SRC).convert("RGBA")).astype(np.float64)
H, W = im.shape[:2]
a = im[..., 3] / 255.0
rgb = im[..., :3] * a[..., None]         # premultiplied, so sampling does not bleed black colour into the edges
# the middle of the cage: the weighted centre of the picture's light
ys, xs = np.mgrid[0:H, 0:W]
cx, cy = (xs * a).sum() / a.sum(), (ys * a).sum() / a.sum()
# radii of the ring's middle line: along rays, the light-weighted mean distance
def mean_r(theta):
    rs = np.arange(0, max(W, H) / 2, 1.0)
    px, py = cx + rs * np.cos(theta), cy + rs * np.sin(theta)
    v = ndi.map_coordinates(a, [py, px], order=1, mode="constant")
    return (rs * v).sum() / max(v.sum(), 1e-6)
ax = np.mean([mean_r(t) for t in np.linspace(-0.25, 0.25, 9)] + [mean_r(np.pi + t) for t in np.linspace(-0.25, 0.25, 9)])
ay = np.mean([mean_r(np.pi / 2 + t) for t in np.linspace(-0.25, 0.25, 9)] + [mean_r(-np.pi / 2 + t) for t in np.linspace(-0.25, 0.25, 9)])
print("picture", W, "x", H, "centre", round(cx, 1), round(cy, 1), "middle-line radii", round(ax, 1), round(ay, 1))

th = np.linspace(0, 2 * np.pi, W_OUT, endpoint=False)[None, :]          # angle along the strip (x)
rho = np.linspace(RHO1, RHO0, H_OUT)[:, None]                           # distance across the strip (y): the OUTER edge at the top
px = cx + rho * ax * np.cos(th)
py = cy + rho * ay * np.sin(th)
chan = [ndi.map_coordinates(rgb[..., c], [py, px], order=1, mode="constant") for c in range(3)] + [ndi.map_coordinates(a, [py, px], order=1, mode="constant")]
A = np.clip(chan[3], 0, 1)
out = np.zeros((H_OUT, W_OUT, 4))
nz = A > 1e-4
for c in range(3):
    out[..., c] = np.where(nz, np.clip(chan[c] / np.maximum(A, 1e-4), 0, 255), 0)
# soft top and bottom so no crystal is cut off hard
fade = np.minimum(1, np.minimum(np.arange(H_OUT), np.arange(H_OUT)[::-1]) / 8.0)[:, None]
out[..., 3] = A * fade * 255
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").save(DST)
print("wrote", DST, (W_OUT, H_OUT), "alpha mean %.3f" % A.mean())
