#!/usr/bin/env python3
"""Makes the pictures for the Warrior's elemental aura round his SHIELD (2026-11-23), into source/assets/fx:

  wsa_fire.png   the Cleric's crimson pact SHIELD (cp_shield: panel 5 of the user's crimson_pact_vfx_sheet.png, a barrier in the shape of a pointed shield with a flame emblem) RECOLOURED to the Execute's
                 forged-fire colours (the page's FORGE palette: deep red-orange, orange, gold, a warm white core). The cut piece keeps the sheet's red in its colour channels with the brightness as alpha, so the
                 recolour reads the G channel (the cores of the lines are whiter, so G is higher there) as how hot a pixel is and maps it onto a ramp. Its own proportions are kept (it is not stretched to the
                 shield). It keeps the FLAME EMBLEM in the middle (Execute, Molten Cleave).
  wsa_ice.png    the same shield in the ice colours (the page's IPALS.ice: deep blue, blue, pale blue, a white core) WITHOUT the emblem (the user: the fire symbol has to go for the other elements): Glacial Blade.
  wsa_bolt.png   the same in the game's one lightning blue (LTC: deep blue, electric blue, periwinkle, a white-blue core), no emblem: Thunderclap Guillotine, Static Bash.

The emblem is removed by flattening the inside of the shield to the typical level of its faint haze (smoothly, so the outline keeps its glow and nothing shows a seam).
The user chose the shape from five versions on 2026-11-23 (the comparison pictures are in docs/previews/execute_shield_aura_versions_*.jpg).

  python make_shield_aura.py
"""
import pathlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FX = ROOT / "source" / "assets" / "fx"
RAMPS = {
    "fire": [(0.0, (150, 36, 12)), (0.25, (232, 98, 28)), (0.6, (255, 190, 92)), (1.0, (255, 250, 232))],     # the page's FORGE: deep, glow, mid, core
    "ice": [(0.0, (34, 78, 176)), (0.25, (74, 150, 238)), (0.6, (150, 214, 255)), (1.0, (244, 252, 255))],      # IPALS.ice: deep, glow, mid, core
    "bolt": [(0.0, (35, 55, 215)), (0.25, (60, 95, 255)), (0.6, (125, 148, 255)), (1.0, (240, 244, 255))],      # LTC: deep, mid, bright, core
}


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= t0) & (t <= t1)
        k = ((t - t0) / (t1 - t0))[m][:, None]
        out[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return out


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def save(rgb, a, name):
    out = np.dstack([rgb, a]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(FX / name)
    print("wrote", name, out.shape[1], "x", out.shape[0])


def main():
    im = np.array(Image.open(FX / "cp_shield.png").convert("RGBA")).astype(float)
    a = im[..., 3]
    t = np.clip((im[..., 1] - 40) / 215, 0, 1) ** 0.8                                                       # how hot: the G channel of the red picture
    save(ramp(t, RAMPS["fire"]), a, "wsa_fire.png")
    # without the emblem: the inside is flattened to the haze's typical level
    solid = ndi.binary_fill_holes(a > 30)
    d = ndi.distance_transform_edt(solid)
    size = max(a.shape)
    inner = solid & (d > 0.075 * size)
    haze = float(np.median(a[inner & (a < 90)])) * 0.8
    flat_a = ndi.gaussian_filter(np.minimum(a, haze), 3)
    flat_t = np.where(inner, float(np.median(t[inner & (a < 90)])), t)
    w = smooth((d - 0.055 * size) / (0.04 * size))                                                           # 0 on the outline, 1 inside
    a2 = a * (1 - w) + flat_a * w
    t2 = t * (1 - w) + flat_t * w
    save(ramp(t2, RAMPS["ice"]), a2, "wsa_ice.png")
    save(ramp(t2, RAMPS["bolt"]), a2, "wsa_bolt.png")


if __name__ == "__main__":
    main()
