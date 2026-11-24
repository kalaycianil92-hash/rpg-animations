#!/usr/bin/env python3
"""Makes rf_ground_ring.png: Winter's Kiss's frost on the ground (rf_ground.png, the user's painted sheet) with a much WIDER empty middle, so the frost forms round the character's feet instead of under them
(2026-11-25, the user: "extend the frost effect beneath the feet for those 3 characters ... it should form outside their feet, the empty area should be bigger so it does not look like they are stepping on it").

The picture's own empty oval is 141 px wide in a 490 px picture (drawn about 0.95 character widths wide: about 0.29 widths), while the Rogue's, the Assassin's and the Spellblade's feet span about 0.49 widths
in Winter's Kiss and in Permafrost Execution's focus. Scaling the picture up would make the crystals chunky, a polar warp would smear them round the inner edge, so the picture is pulled APART instead:
its left half stays, its right half moves GAP px to the right, and the gap between them is filled with the picture's middle strip MIRRORED (the frost in front of and behind the hole, so the ring stays
closed at the front and at the back; mirrored, so it does not read as a repeat). The three pieces cross-fade over FEATHER px at the seams, and the new hole (an ellipse round the middle, HOLE_B px high)
is cleared with a soft edge. The page draws the far half (above the hole's middle row) behind the character and the near half in front of her, the middle row on her ground line (see kissGroundDraw).

  python Animations/Rogue/dagger_throw/source/make_kiss_ground_ring.py      (writes source/assets/fx/rf_ground_ring.png; prints the numbers the page uses)
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[4]
FX = ROOT / "source" / "assets" / "fx"
GAP = 240                  # px the right half moves (the hole gets this much wider)
FEATHER = 36               # px of cross-fade at each seam
HOLE_B = 24                # half-height of the cleared hole (px)
EDGE = 10                  # px of soft edge round the cleared hole

src = np.array(Image.open(FX / "rf_ground.png").convert("RGBA")).astype(np.float64)
H, W = src.shape[:2]
a = src[..., 3] / 255.0
pm = np.dstack([src[..., :3] * a[..., None], a])                                      # premultiplied, so the cross-fades do not darken the edges

# the picture's own hole: the empty region round the middle
empty = ndi.gaussian_filter(a, 3) < 0.06
lab, _ = ndi.label(empty)
hy, hx = np.where(lab == lab[H // 2 - 10, W // 2])
cx, cy = (hx.min() + hx.max()) / 2.0, (hy.min() + hy.max()) / 2.0
half_w = (hx.max() - hx.min()) / 2.0
print("own hole: x %d-%d, y %d-%d, middle (%.1f, %.1f)" % (hx.min(), hx.max(), hy.min(), hy.max(), cx, cy))

W2 = W + GAP
c = int(round(cx)); D = GAP // 2
xo = np.arange(W2)


def take(xsrc):                                                                        # columns of the source (clamped), as a full-height layer
    return pm[:, np.clip(xsrc, 0, W - 1), :] * ((xsrc >= 0) & (xsrc < W))[None, :, None]


left = take(xo)                                                                        # x' = x
mid = take(c + D - (xo - c))                                                          # the middle strip, mirrored: output c..c+GAP shows source c+D .. c-D
right = take(xo - GAP)                                                                 # x' = x + GAP


def ramp(x0):                                                                          # 0 before x0 - FEATHER/2, 1 after x0 + FEATHER/2
    return np.clip((xo - (x0 - FEATHER / 2.0)) / FEATHER, 0, 1)


wl = 1 - ramp(c)
wr = ramp(c + GAP)
wm = 1 - wl - wr
out = left * wl[None, :, None] + mid * wm[None, :, None] + right * wr[None, :, None]

# clear the new hole: an ellipse round the new middle, as wide as the old hole plus the gap
ncx = cx + D
A = half_w + D
yy, xx = np.mgrid[0:H, 0:W2]
r = np.sqrt(((xx - ncx) / A) ** 2 + ((yy - cy) / HOLE_B) ** 2)
keep = np.clip((r - 1) * min(A, HOLE_B) / EDGE, 0, 1)                                 # 0 inside the hole, 1 past its soft edge
out *= keep[..., None]

alpha = np.clip(out[..., 3], 0, 1)
rgb = np.where(alpha[..., None] > 1e-4, out[..., :3] / np.maximum(alpha, 1e-4)[..., None], 0)
img = np.dstack([np.clip(rgb, 0, 255), alpha * 255])
Image.fromarray((img + 0.5).astype(np.uint8), "RGBA").save(FX / "rf_ground_ring.png")
print("wrote rf_ground_ring.png %d x %d; hole middle x %.1f (%.3f of the width), row %.1f (%.3f of the height), hole %.0f px wide (%.3f of the width); width factor vs rf_ground %.4f"
      % (W2, H, ncx, ncx / W2, cy, cy / H, 2 * A, 2 * A / W2, W2 / W))
