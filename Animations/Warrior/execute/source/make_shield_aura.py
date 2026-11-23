#!/usr/bin/env python3
"""Makes the pictures for the Warrior's fire aura round his SHIELD in the Execute (2026-11-23), into source/assets/fx:

  ex_shield_fire.png   the Cleric's crimson pact SHIELD (cp_shield: panel 5 of the user's crimson_pact_vfx_sheet.png, a barrier in the shape of a pointed shield with a flame emblem) RECOLOURED to the Execute's
                       forged-fire colours (the page's FORGE palette: deep red-orange, orange, gold, a warm white core). The cut piece keeps the sheet's red in its colour channels with the brightness as alpha, so the
                       recolour reads the G channel (the cores of the lines are whiter, so G is higher there) as how hot a pixel is and maps it onto a fire ramp. Its own proportions are kept (it is not stretched to the shield).

The user chose this one (version A of five: the others, an outline-only version and two halos that follow the shield's exact silhouette, were tried and removed 2026-11-23; the comparison pictures are in
docs/previews/execute_shield_aura_versions_*.jpg).

  python make_shield_aura.py
"""
import pathlib
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FX = ROOT / "source" / "assets" / "fx"
RAMP = [(0.0, (150, 36, 12)), (0.25, (232, 98, 28)), (0.6, (255, 190, 92)), (1.0, (255, 250, 232))]     # the page's FORGE: deep, glow, mid, core


def ramp(t):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for (t0, c0), (t1, c1) in zip(RAMP[:-1], RAMP[1:]):
        m = (t >= t0) & (t <= t1)
        k = ((t - t0) / (t1 - t0))[m][:, None]
        out[m] = np.array(c0) * (1 - k) + np.array(c1) * k
    return out


def recolour(path):
    im = np.array(Image.open(path).convert("RGBA")).astype(float)
    t = np.clip((im[..., 1] - 40) / 215, 0, 1) ** 0.8                                                       # how hot: the G channel of the red picture
    rgb = ramp(t)
    return rgb, im[..., 3]


def save(rgb, a, name):
    out = np.dstack([rgb, a]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(FX / name)
    print("wrote", name, out.shape[1], "x", out.shape[0])


def main():
    rgb, a = recolour(FX / "cp_shield.png")
    save(rgb, a, "ex_shield_fire.png")


if __name__ == "__main__":
    main()
