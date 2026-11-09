#!/usr/bin/env python3
"""Finds a character's HAIR in an animation strip and writes a hair mask (white = hair) that a game can use to recolour the hair at runtime.

Adapted (2026-11-05) from Claude_animation_adjuster/tools/hair_mask.py, which found only BLONDE hair inside the top 22% of the figure (it gave 0 pixels on all three of our characters:
the Mage's hair is joined to her face and dress, the Rogue's is burgundy, the Warrior's black). What changed:
  - every character has its own PROFILE (the hair's colour window, with hue wrapping through 0 for the Rogue's burgundy, and her skin colour);
  - the head is found in every frame by its FACE (the largest skin-coloured blob), not by "the top 22% of the figure", so lying, falling, diving and running poses work;
  - hair = the biggest blob of BRIGHT-ENOUGH hair colour that touches the face (the dark outlines and shading are left out first, so the Rogue's crimson scarf, the same colour as her hair, separates from it;
    the Mage's braid is joined to her hair, so it stays), then the dark shading and outline-side pixels of the same hair are grown back (a few px, never into the scarf or a trim line);
  - small gaps and holes are closed. For the Mage the hair must also reach the face's height along the body's up direction (her gold robe trim is lower).

  python source/tools/hair_mask.py <strip.png> <mask.png> --char rogue|mage|warrior|spellblade [--frame 512] [--preview preview.png]
  python source/tools/hair_mask.py --all [--char rogue|mage|warrior|spellblade]     (every strip of the character(s): writes <strip>.hair-mask.png next to it and a contact sheet source/hair_check/<char>_<animation>.png)

The mask is a grey PNG the size of the strip: 255 = hair. Needs:  pip install pillow numpy scipy
"""
import argparse
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]


def rogue_skin(r, g, b, h, s, v):                                  # her olive-tan skin
    return (r > 140) & (r < 245) & (g > 90) & (g < 180) & (b > 40) & (b < 135) & (r > g + 22) & (g > b + 10)


def spellblade_skin(r, g, b, h, s, v):                             # her honey-tan skin (hue about 28; her copper-scarlet hair is hue 8-20, her gold trim and cape lining 40 and up, the ivory suit has low saturation)
    return (h >= 22) & (h <= 38) & (s >= 0.28) & (s <= 0.78) & (v >= 0.5) & (r > g + 25)


def mage_skin(r, g, b, h, s, v):                                   # the elf's pale peach skin
    return (h >= 8) & (h <= 27) & (s >= 0.14) & (s <= 0.55) & (v >= 0.6)


def warrior_skin(r, g, b, h, s, v):                                # his tan-brown skin
    return (h >= 10) & (h <= 30) & (s >= 0.35) & (s <= 0.8) & (v >= 0.35)


# hue = windows in degrees (a window may wrap through 0: give (322, 360) and (0, 14)); sat / val = (min, max).
# "strict" finds the hair's body (bright enough that the dark outlines and shading, which would join the hair to look-alikes like a scarf, are not part of it; it is eroded by `erode` px so
# thin bridges break); "loose" is what may be added back round it (the dark shading and the outline-side pixels of the same hair, `grow` px at most, never through a neighbouring blob).
PROFILES = {
    "rogue": dict(hue=[(322, 360), (0, 14)], skin=rogue_skin, strict=dict(sat=0.38, val=0.28), loose=dict(sat=0.22, val=0.03), erode=1, grow=8, near=30, reach=None, block=350, chin=6, chain=0, chain_face=0, chain_thick=0),
    "spellblade": dict(hue=[(0, 26)], skin=spellblade_skin, strict=dict(sat=0.5, val=0.35), loose=dict(sat=0.3, val=0.08), erode=1, grow=8, near=30, reach=None, block=350, chin=6, chain=0, chain_face=0, chain_thick=0),
    "mage": dict(hue=[(26, 62), (19, 26, 0.45, 0.78)], skin=mage_skin, strict=dict(sat=0.28, val=0.35), loose=dict(sat=0.22, val=0.30), erode=0, grow=4, near=30, reach=-3, block=350, chin=None, chain=12, chain_face=260, chain_thick=4.5),
    "warrior": dict(hue=[(0, 360)], skin=warrior_skin, strict=dict(sat=0.0, val=0.11, smax=0.65, vmax=0.38), loose=dict(sat=0.0, val=0.05, smax=0.8, vmax=0.45), erode=1, grow=6, near=30, reach=-3, block=350, chin=None, chain=0, chain_face=0, chain_thick=0, head_top=0.3),
}


def hair_in_frame(rgba, P):
    """rgba: one frame (H x W x 4, uint8). Returns a boolean hair mask."""
    rgb = rgba[..., :3].astype(float)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    fg = (rgba[..., 3] > 128) & ~((np.minimum(r, b) - g) > 70)           # (a magenta background, if the sheet is not yet keyed, is not figure)
    empty = np.zeros(fg.shape, bool)
    if fg.sum() < 500:
        return empty
    hsv = np.array(Image.fromarray(rgba[..., :3]).convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    hue_ok = np.zeros(fg.shape, bool)
    for w in P["hue"]:                                                   # a window is (lo, hi) or (lo, hi, min sat, max val): the Mage's tan hair shading shares its hue with skin, but is more saturated and darker
        ok = (h >= w[0]) & (h <= w[1])
        if len(w) > 2:
            ok &= (s >= w[2]) & (v <= w[3])
        hue_ok |= ok
    sc = float(np.clip(fg.sum() / 30000.0, 0.25, 1.0))                   # (a frame where the figure is drawn small — a full-body frame in a strip of close-ups — gets proportionally smaller thresholds)
    S, Lo = P["strict"], P["loose"]
    strict = fg & hue_ok & (s >= S["sat"]) & (v >= S["val"]) & (s <= S.get("smax", 1.0)) & (v <= S.get("vmax", 1.0))
    loose = fg & hue_ok & (s >= Lo["sat"]) & (v >= Lo["val"]) & (s <= Lo.get("smax", 1.0)) & (v <= Lo.get("vmax", 1.0))
    if P["erode"]:
        strict = ndi.binary_erosion(strict, iterations=P["erode"])
    slab, sn = ndi.label(strict)                                         # (4-connected: a thin dark outline between hair and scarf keeps them apart)
    if sn == 0:
        return empty
    ssz = ndi.sum(strict, slab, range(1, sn + 1))
    # the face: a skin blob next to the biggest blob of hair colour (the hair frames the face; a hand or a pair of fists can be a bigger skin blob than the face, as in a dive or an outstretched arm)
    skin = fg & P["skin"](r, g, b, h, s, v) & ~loose
    lab, n = ndi.label(ndi.binary_closing(skin, iterations=1))
    if n == 0:
        return empty
    sizes = ndi.sum(skin, lab, range(1, n + 1))
    big = [i + 1 for i in range(n) if sizes[i] >= 150 * sc]
    if P.get("head_top"):                                                # (the Warrior: arms and chest are skin too, so the face must lie in the top part of the figure: his lying frames are not covered)
        fy0 = np.where(fg.any(1))[0]
        lim = fy0[0] + P["head_top"] * (fy0[-1] - fy0[0])
        big = [i for i in big if ndi.center_of_mass(lab == i)[0] <= lim]
    if not big:
        return empty
    hair0 = slab == (1 + int(np.argmax(ssz)))
    d0 = ndi.distance_transform_edt(~hair0)
    near = {i: d0[lab == i].min() for i in big}
    close = [i for i in big if near[i] <= 20]
    k = min(close, key=lambda i: (near[i] > 8, -sizes[i - 1])) if close else max(big, key=lambda i: sizes[i - 1])
    if P.get("head_top"):                                                # (the Warrior: his armour is as dark as his hair, so the biggest dark blob is a pauldron, not hair: the face is the highest of the skin blobs)
        k = min(big, key=lambda i: ndi.center_of_mass(lab == i)[0])
    face = lab == k
    fy, fx = np.where(face)
    Fx, Fy = fx.mean(), fy.mean()
    dist = ndi.distance_transform_edt(~face)
    # the hair: the biggest strict blob that touches the face (plus blobs of its own colour that lie right against it)
    order = [i for i in np.argsort(-ssz) + 1 if ssz[i - 1] >= 100 * sc and dist[slab == i].min() <= P["near"]]
    if not order:
        return empty
    if P["reach"] is not None:                                           # (the Mage: the hair must reach the face's height measured along the body's up direction; her robe's gold trim is lower)
        ys, xs = np.where(fg)
        up = np.array([Fx - xs.mean(), Fy - ys.mean()]); nu = np.hypot(*up); up = up / nu if nu > 8 else np.array([0.0, -1.0])
        yy, xx = np.mgrid[0:fg.shape[0], 0:fg.shape[1]]
        proj = (xx - Fx) * up[0] + (yy - Fy) * up[1]
        order = [i for i in order if proj[slab == i].max() >= P["reach"]]
        if not order:
            return empty
    if P.get("head_top"):                                                # (the Warrior: of the dark blobs next to the face, the hair is the one that lies mostly ABOVE the face's middle; his collar and chest armour lie below it)
        above = lambda i: int(((slab == i) & (np.arange(fg.shape[0])[:, None] < Fy)).sum())
        order.sort(key=lambda i: -above(i))
        if above(order[0]) < 60 * sc:
            return empty
    main = slab == order[0]
    near_main = ndi.distance_transform_edt(~main)
    core = main.copy()
    for i in order[1:]:
        m = slab == i
        if near_main[m].min() <= 3:
            core |= m
    if P["chain"]:                                                       # the Mage's braid and side locks are cut off from the top of her hair by outlines: take the blobs of hair colour that follow it, each within `chain` px of the hair so far and within `chain_face` px of the face (the robe's gold trim is farther)
        tlab, tn = ndi.label(strict)
        todo = [i for i in range(1, tn + 1) if (tlab == i).sum() >= 100 and not (core & (tlab == i)).any() and dist[tlab == i].min() <= P["chain_face"]
                and ndi.distance_transform_edt(tlab == i).max() >= P["chain_thick"]]   # (a trim line is thin: its widest point is a few px; a braid is thick)
        for _ in range(8):
            dc = ndi.distance_transform_edt(~core)
            add = [i for i in todo if dc[tlab == i].min() <= P["chain"]]
            if not add:
                break
            for i in add:
                core |= tlab == i
                todo.remove(i)
    others = (slab > 0) & ~core                                          # the scarf, trim lines ...: the hair may not grow into them (but small fragments, such as the dark strands of the far side of the head, may be absorbed)
    olab, on = ndi.label(others)
    if on:
        osz = ndi.sum(others, olab, range(1, on + 1))
        others = np.isin(olab, 1 + np.where(osz >= P["block"])[0])
    block = ndi.binary_dilation(others, iterations=2)
    hair = core.copy()
    for _ in range(P["grow"]):                                           # geodesic growth back into the dark shading of the same hair
        hair = ndi.binary_dilation(hair) & loose & ~block | hair
    hair = ndi.binary_opening(hair, iterations=1)
    hair = ndi.binary_closing(hair, iterations=2)
    hair = ndi.binary_fill_holes(hair) & fg & ~face
    if P["chin"] is not None:                                            # (an upright head: nothing of the hair colour below the chin is hair; the Rogue's scarf, which can touch her hair, lies there)
        ys, xs = np.where(fg)
        ax = np.array([Fx - xs.mean(), Fy - ys.mean()]); na = np.hypot(*ax)
        if na > 8 and -ax[1] / na >= np.cos(np.radians(40)):
            hair &= np.arange(fg.shape[0])[:, None] <= fy.max() + P["chin"]
    lab2, n2 = ndi.label(hair)
    if n2:
        sz = ndi.sum(hair, lab2, range(1, n2 + 1))
        hair = np.isin(lab2, 1 + np.where(sz >= 100)[0])
    return hair


def mask_for_strip(path, P, frame):
    im = Image.open(path).convert("RGBA")
    rgba = np.array(im)
    W = rgba.shape[1]
    step = frame or W
    mask = np.zeros(rgba.shape[:2], bool)
    counts = []
    for x in range(0, W, step):
        mask[:, x:x + step] = hair_in_frame(rgba[:, x:x + step], P)
        counts.append(int(mask[:, x:x + step].sum()))
    return rgba, mask, counts


def contact_sheet(rgba, mask, frame, out, thumb=170):
    """The frames side by side (at most 10 per row) with the mask painted green over a grey background."""
    W = rgba.shape[1]
    n = W // frame
    cols = min(n, 10)
    rows = (n + cols - 1) // cols
    H = rgba.shape[0]
    sc = thumb / max(frame, H)
    tw, th = int(frame * sc), int(H * sc)
    sheet = Image.new("RGB", (tw * cols, th * rows), (70, 70, 90))
    for i in range(n):
        f = rgba[:, i * frame:(i + 1) * frame].copy()
        mk = mask[:, i * frame:(i + 1) * frame]
        p = f.copy(); p[mk] = [0, 255, 0, 255]
        bg = Image.new("RGBA", (frame, H), (70, 70, 90, 255)); bg.alpha_composite(Image.fromarray(p))
        sheet.paste(bg.convert("RGB").resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--char", choices=sorted(PROFILES))
    ap.add_argument("--frame", type=int, default=512, help="frame (cell) width of the strip, 0 = the whole image is one frame")
    ap.add_argument("--preview", help="also write the strip with the mask painted green")
    ap.add_argument("--all", action="store_true", help="every strip of the character(s) in Animations/")
    a = ap.parse_args()
    if a.all:
        names = [a.char] if a.char else sorted(PROFILES)
        (ROOT / "source" / "hair_check").mkdir(exist_ok=True)
        for c in names:
            for strip in sorted((ROOT / "Animations" / c.capitalize()).glob("*/*_strip.png")):
                rgba, mask, counts = mask_for_strip(strip, PROFILES[c], a.frame)
                out = strip.with_name(strip.name[:-len(".png")] + ".hair-mask.png")
                Image.fromarray((mask * 255).astype(np.uint8)).save(out)
                contact_sheet(rgba, mask, a.frame, ROOT / "source" / "hair_check" / (c + "_" + strip.parent.name + ".png"))
                print(c, strip.parent.name, strip.name, "hair px per frame", counts)
        return
    if not (a.src and a.dst and a.char):
        ap.error("give <strip.png> <mask.png> --char rogue|mage|warrior|spellblade, or --all")
    rgba, mask, counts = mask_for_strip(a.src, PROFILES[a.char], a.frame)
    for i, c in enumerate(counts):
        print("frame", i + 1, "hair px", c)
    Image.fromarray((mask * 255).astype(np.uint8)).save(a.dst)
    if a.preview:
        p = rgba.copy(); p[mask] = [0, 255, 0, 255]
        Image.fromarray(p).save(a.preview)
    print("->", a.dst)


if __name__ == "__main__":
    main()
