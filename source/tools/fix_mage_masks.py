#!/usr/bin/env python3
"""Cleans the mage's Recolour masks after hair_mask.py and skin_mask.py (char mage) have made them (2026-11-25).

The two tools leave three kinds of mistakes on her, which the user saw as colour where it does not belong:
  - the gold trim of her collar, from the neck down to the clasp, is in the hair mask on some frames and not on others, so in the idle the
    collar flickers in the hair colour as she breathes (also in the hit, dodge and cast); and in the redrawn run the lit leather of her boots
    is in the skin mask;
  - in the redrawn run the hair mask grew over her forehead down to the brows, down one cheek and onto the ears.
So, on the frames where she stands upright (the head above the body), in every strip:
  - hair: nothing below her chin in front of her neck (the braid hangs BEHIND her neck and stays);
  - skin: nothing below SKIN_FLOOR (her hands never go below the belt; the boots are far below it);
in the idle only (TRIM_RULES):
  - hair: not the gold lining of her collar. It has the hair's very colours, so it is told apart by its shape: a THIN gold line (it vanishes
    under a 5 x 5 opening; the braid does not) lying within 4 px of the blue cloth, from her chin down to TRIM_BELOW_CHIN below it (the top
    edge of the standing collar behind her neck, and the lining where it meets the braid);
and in the redrawn run only (FACE_RULES):
  - hair: below the chin nothing thinner than the braid (a trim line touching the braid);
  - hair: no skin-coloured pixel next to her face: skin is paler and less saturated than her blonde hair (hue under SKIN_HUE with
    saturation under SKIN_SAT, or hue under SKIN_HUE_PEACH with saturation under SKIN_SAT_PEACH); the hair's pale highlights are yellower
    and stay. Those pixels go to the skin mask instead.
Frames where she lies or is thrown back (the death's 3 to 6) are left as the tools made them.
The chin and the neck come from the skin mask: all the skin near the top of her head is the face (shading splits it into patches).

  python source/tools/fix_mage_masks.py              every mage strip that has masks
  python source/tools/fix_mage_masks.py idle run     only these
Run it after remaking the masks with the two tools, then rebuild the page. The masks are changed in place; the first time a strip is
cleaned, its masks as the tools made them are kept in the animation's source/ folder as *.hair-mask.raw.png and *.skin-mask.raw.png.
"""
import pathlib
import shutil
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAGE = ROOT / "Animations" / "Mage"
UPRIGHT = {"death": [1, 2]}  # frames (from 1) where she stands upright, for strips where not all of them are; every other strip: all frames
TRIM_RULES = {"idle"}        # strips that also get the collar-lining rule (the user, 2026-11-25: 'the golden lining around the top of the collar
                             # should be isolated from hair'; asked for the idle only)
TRIM_BELOW_CHIN = 22         # px: the lining rule works down to this far below her chin (the braid's edge further down is left alone)
FACE_RULES = {"run"}         # strips that also get the skin-colour rule and the thin-line rule (the redrawn run). Not the others: in them the
                             # shaded parts of her braid and the lock of hair beside her cheek have her forehead's colours and would be lost
SKIN_FLOOR = 320      # px of the 512 px frame: no skin below this line
NECK_BACK = 12        # px: the hair below the chin is kept only this far in front of the neck's middle, or further back
HEAD_DEPTH = 110      # px: the head's skin lies within this far below the top of the figure
HEAD_HALF = 55        # px: and within this far to either side of the top of her head (a fist raised to her chin is further out)
NEAR_FACE = 22        # px: the skin-coloured test is made only this close to her face's skin
SKIN_HUE, SKIN_SAT = 32, 0.40
SKIN_HUE_PEACH, SKIN_SAT_PEACH = 27, 0.56


def clean(strip, frames, face_rules, trim_rules=False):
    hair_p = strip.with_name(strip.name[:-4] + ".hair-mask.png"); skin_p = strip.with_name(strip.name[:-4] + ".skin-mask.png")
    for p, tag in ((hair_p, "hair"), (skin_p, "skin")):
        keep = strip.parent / "source" / (strip.name[:-4] + "." + tag + "-mask.raw.png")
        if not keep.exists():
            keep.parent.mkdir(exist_ok=True); shutil.copyfile(p, keep)
    rgba = np.array(Image.open(strip).convert("RGBA")).astype(float)
    alpha = rgba[..., 3] > 128
    r, g, b = [rgba[..., i] / 255 for i in range(3)]
    mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b); dd = mx - mn + 1e-9
    hue = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    sat = np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0)
    gold = alpha & (hue > 12) & (hue < 48) & (mx > 0.33) & (sat > 0.25)
    blue = alpha & (hue > 190) & (hue < 250) & (sat > 0.15) & (mx > 0.2)
    skin_col = ((hue < SKIN_HUE) & (sat < SKIN_SAT) | (hue < SKIN_HUE_PEACH) & (sat < SKIN_SAT_PEACH)) & (mx > 0.4) & alpha
    hair = np.array(Image.open(hair_p).convert("L")); skin = np.array(Image.open(skin_p).convert("L"))
    H = alpha.shape[0]; n = alpha.shape[1] // 512
    rows = np.arange(H)[:, None]; cols = np.arange(512)[None, :]
    for k in range(n):
        if frames and k + 1 not in frames:
            continue
        sl = slice(512 * k, 512 * (k + 1))
        a = alpha[:, sl]; top = np.where(a.any(axis=1))[0].min()
        floor = top + SKIN_FLOOR - 64                                  # (the 320 line of the run, where the top of her head is at about 64; 640 px frames keep it relative to her head)
        skin[floor:, sl] = 0
        head_x = np.where(a[top:top + 40])[1].mean()                   # the middle of the top of her head
        fs = skin[:, sl] > 128
        fs[top + HEAD_DEPTH:] = False; fs[:, :max(0, int(head_x - HEAD_HALF))] = False; fs[:, int(head_x + HEAD_HALF):] = False
        if not fs.any():
            print("  %s frame %d: no face found, left as it is" % (strip.name, k + 1)); continue
        face = np.where(fs)
        chin, neck_x = face[0].max(), face[1].mean()
        hk = hair[:, sl]
        hk[(rows > chin) & (cols > neck_x - NECK_BACK)] = 0
        if trim_rules:
            inmask = (hk > 64) & gold[:, sl]
            thick = ndi.binary_opening(inmask, structure=np.ones((5, 5)))
            lining = inmask & ~thick & ndi.binary_dilation(blue[:, sl], iterations=4) & (rows <= chin + TRIM_BELOW_CHIN)
            lining = ndi.binary_dilation(lining, iterations=1) & (hk > 64) & ~thick & (rows <= chin + TRIM_BELOW_CHIN)   # its soft edge too
            hk[lining] = 0
        if not face_rules:
            continue
        below = (hk > 0) & (rows > chin)
        hk[below & ~ndi.binary_opening(below, structure=np.ones((3, 3)), iterations=2)] = 0
        near = ndi.binary_dilation(fs, iterations=NEAR_FACE)
        on_face = near & skin_col[:, sl] & (hk > 0)
        on_face = ndi.binary_closing(on_face, iterations=1) & near & (hk > 0)
        hk[on_face] = 0
        sk = skin[:, sl]; sk[on_face] = np.maximum(sk[on_face], 230)
    Image.fromarray(hair).save(hair_p); Image.fromarray(skin).save(skin_p)
    print("cleaned", hair_p.relative_to(ROOT), "and its skin mask")


names = sys.argv[1:]
for folder in sorted(p for p in MAGE.iterdir() if p.is_dir()):
    if names and folder.name not in names:
        continue
    for strip in folder.glob("*_strip.png"):
        if strip.with_name(strip.name[:-4] + ".hair-mask.png").exists():
            clean(strip, UPRIGHT.get(folder.name), folder.name in FACE_RULES, folder.name in TRIM_RULES)
