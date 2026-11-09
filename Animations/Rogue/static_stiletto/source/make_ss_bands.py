#!/usr/bin/env python3
"""Makes ss_band_a.png, ss_band_b.png and ss_band_c.png, the pictures of the Static Stiletto's ORBITING lightning ring, from the three lightning cages (ss_halo_a/b/c.png, the user's ChatGPT electricity sheet).

The user (2026-11-06): "change the static circle to orbit around like in winter kiss animation". Winter's Kiss does it with make_kiss_band.py (its vertical frost cage unwrapped into a seamless strip that the page wraps round a
flat ring at waist height and spins, kissRingDraw). This is the same method, three times (the page changes between the three bands every few tens of ms, so the ring crackles as it turns):
for every angle round the oval cage and every distance from its middle line the picture is sampled (elliptical polar coordinates), giving a long strip: the cage stretched out along its length, the outer edge of the
arcs at the TOP and the inner edge at the BOTTOM.
The strip is seamless where it closes (the same picture point is sampled at angle 0 and at 360 degrees).

  python make_ss_bands.py        (writes source/assets/fx/ss_band_a.png ... and prints the numbers it measured; the cages stay in the page too: they still ring a Shocked target)
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[4]
FX = ROOT / "source" / "assets" / "fx"
W_OUT, H_OUT = 1200, 200
RHO0, RHO1 = 0.45, 1.55                  # inner and outer edge of the sampled band, as a multiple of the cage's middle-line radius


def unwrap(path):
    im = np.array(Image.open(path).convert("RGBA")).astype(np.float64)
    H, W = im.shape[:2]
    a = im[..., 3] / 255.0
    rgb = im[..., :3] * a[..., None]     # premultiplied, so sampling does not bleed black colour into the edges
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = (xs * a).sum() / a.sum(), (ys * a).sum() / a.sum()

    def mean_r(theta):
        rs = np.arange(0, max(W, H) / 2, 1.0)
        px, py = cx + rs * np.cos(theta), cy + rs * np.sin(theta)
        v = ndi.map_coordinates(a, [py, px], order=1, mode="constant")
        return (rs * v).sum() / max(v.sum(), 1e-6)
    ax = np.mean([mean_r(t) for t in np.linspace(-0.25, 0.25, 9)] + [mean_r(np.pi + t) for t in np.linspace(-0.25, 0.25, 9)])
    ay = np.mean([mean_r(np.pi / 2 + t) for t in np.linspace(-0.25, 0.25, 9)] + [mean_r(-np.pi / 2 + t) for t in np.linspace(-0.25, 0.25, 9)])
    print(path.name, W, "x", H, "centre", round(cx, 1), round(cy, 1), "middle-line radii", round(ax, 1), round(ay, 1))
    th = np.linspace(0, 2 * np.pi, W_OUT, endpoint=False)[None, :]
    rho = np.linspace(RHO1, RHO0, H_OUT)[:, None]
    px, py = cx + rho * ax * np.cos(th), cy + rho * ay * np.sin(th)
    chan = [ndi.map_coordinates(rgb[..., c], [py, px], order=1, mode="constant") for c in range(3)] + [ndi.map_coordinates(a, [py, px], order=1, mode="constant")]
    A = np.clip(chan[3], 0, 1)
    out = np.zeros((H_OUT, W_OUT, 4))
    nz = A > 1e-4
    for c in range(3):
        out[..., c] = np.where(nz, np.clip(chan[c] / np.maximum(A, 1e-4), 0, 255), 0)
    out[..., 3] = A * 255
    fade = np.minimum(1, np.minimum(np.arange(H_OUT), np.arange(H_OUT)[::-1]) / 8.0)[:, None]
    out[..., 3] *= fade
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), float(A.mean())


for k in "abc":
    img, am = unwrap(FX / ("ss_halo_%s.png" % k))
    img.save(FX / ("ss_band_%s.png" % k))
    print("wrote ss_band_%s.png" % k, img.size, "alpha mean %.3f" % am)
