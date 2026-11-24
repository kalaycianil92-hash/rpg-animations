#!/usr/bin/env python3
"""Finds a character's SKIN in an animation strip and writes a skin mask (white = skin, grey = partly) that the test page uses to change the skin colour at runtime (2026-11-24).

Like hair_mask.py it needs a per-character PROFILE; only the Warrior has one so far. The Warrior's skin is a warm tan (hue 8 to 36 degrees, saturation 0.25 to 0.8) that is
bright (value 0.45 and up) on the face, the bare arms and the fists, and darker in its shading (down to 0.3). The things that share the hue but are NOT skin: the brown leather bracers
(value 0.2 to 0.4, wide areas), the copper trim of the armour (thin lines, 1 to 3 px) and the hair's warm shading. So:
  - the CORE is every bright warm pixel, opened with a 5 x 5 square so the trim lines vanish, and without blobs under 60 px;
  - the shading is grown back from the core, a few pixels at most and only over warm pixels that are not too dark (the bracers' darker brown stays out);
  - the mask is soft: 1.0 in the core, 0.85 in the grown shading, edges blurred a little, so the recolour fades into the dark outline instead of leaving a halo.

  python source/tools/skin_mask.py <strip.png> <mask.png> [--frame 512] [--preview preview.png]
  python source/tools/skin_mask.py --all [--char warrior]       (every strip of the character: writes <strip>.skin-mask.png next to it and a contact sheet source/skin_check/<char>_<animation>.png)

The mask is a grey PNG the size of the strip. Needs:  pip install pillow numpy scipy
"""
import argparse
import pathlib
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parents[2]

PROFILES = {
    # body_*: the loose growth everywhere (steps, saturation, value).
    # head_*: around the HAIR (the hair mask must exist) the rule is looser, because the ear, the temple and the neck under the hair lie in shadow (value 0.15 to 0.45):
    # head_r = how far from the hair (px) the loose rule is allowed, head_val / head_sat = what counts as warm there, head_open = the opening that drops thin copper lines, head_grow = growth steps, head_bridge / head_bridge_min = a loose blob (at least that many px) within that distance of the skin joins it even across a dark outline line
    "warrior": dict(hue=(0, 36), hue_wrap=348, head_wrap=345, sat=(0.25, 0.80), core_val=0.45, shade_val=0.28, shade_sat=0.28, open=5, min_blob=24, grow=3, grow_w=0.85, blur=0.6,
                    body_grow=8, body_sat=0.2, body_val=0.33, head_r=30, head_hue=(0, 40), head_sat=0.20, head_val=0.14, head_open=3, head_grow=14, head_w=0.9, head_bridge=4, head_bridge_min=14),
    # the other three (2026-11-25), first guesses from the colour windows of the hair tool (hair_mask.py); no_hair = whatever the hair mask covers is never skin (blonde hair and brows are warm too)
    "mage": dict(hue=(8, 28), sat=(0.14, 0.60), core_val=0.60, shade_val=0.45, shade_sat=0.15, open=3, min_blob=20, grow=3, grow_w=0.85, blur=0.6, no_hair=True,
                 body_grow=5, body_sat=0.14, body_val=0.50, head_r=30, head_hue=(0, 32), head_sat=0.14, head_val=0.40, head_open=3, head_grow=8, head_w=0.9, head_bridge=3, head_bridge_min=10),
    "rogue": dict(hue=(10, 34), sat=(0.28, 0.80), core_val=0.45, shade_val=0.28, shade_sat=0.28, open=3, min_blob=24, grow=3, grow_w=0.85, blur=0.6, no_hair=True, min_peak_val=0.65, hue_margin=2, ear_skin=dict(hue=(12, 36), sat=0.3, val=0.36, smin=6, smax=300, reach=14, w=0.95),
                  body_grow=6, body_sat=0.25, body_val=0.33, body_hue_min=6, body_hue_max=38, head_r=30, head_hue=(4, 40), head_sat=0.22, head_val=0.16, head_open=3, head_grow=12, head_w=0.9, head_bridge=4, head_bridge_min=12),
    "cleric": dict(hue=(16, 32), sat=(0.25, 0.75), core_val=0.55, shade_val=0.40, shade_sat=0.25, open=3, min_blob=24, grow=3, grow_w=0.85, blur=0.6, no_hair=True, min_peak_val=0.70, hue_margin=1, body_bridge=3, body_bridge_min=30, body_bridge_max=500, bridge_hue_max=36,
                   body_grow=5, body_sat=0.22, body_val=0.42, body_hue_min=14, body_hue_max=41, head_r=30, head_hue=(10, 43), head_sat=0.22, head_val=0.30, head_open=3, head_grow=10, head_w=0.9, head_bridge=5, head_bridge_min=12),
}


def skin_in_frame(rgba, P, hair=None):
    """rgba: one frame (H x W x 4, uint8); hair: that frame's hair mask (float 0..1) or None. Returns a float mask 0..1."""
    rgb = rgba[..., :3]
    fg = rgba[..., 3] > 128
    if fg.sum() < 500:
        return np.zeros(fg.shape, float)
    hsv = np.array(Image.fromarray(rgb).convert("HSV")).astype(float)
    h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    redder = (h >= P["hue_wrap"]) if P.get("hue_wrap") else False         # the far hand's shading is pinker (hue 350 to 360): skin too
    warm = fg & (((h >= P["hue"][0]) & (h <= P["hue"][1])) | redder) & (s >= P["sat"][0]) & (s <= P["sat"][1])
    core = warm & (v >= P["core_val"])
    if P["open"]:                                                        # opened with an `open` x `open` square: the copper trim and the armour's bright edge lines (up to 4 px wide) vanish, the face, the arms and the fists (15 px and more) stay
        core = ndi.binary_opening(core, structure=np.ones((P["open"], P["open"]), bool))
    lab, n = ndi.label(core)
    if n:
        sizes = ndi.sum(core, lab, range(1, n + 1))
        for i in range(n):
            if sizes[i] < P["min_blob"]:
                core[lab == i + 1] = False
    mg = P.get("hue_margin", 4)                                           # how far past the hue window the shading may reach (the Cleric's cream tabard is only 3 degrees past his skin: 0 there)
    shade_ok = fg & (((h >= P["hue"][0] - mg) & (h <= P["hue"][1] + mg)) | redder) & (s >= P["shade_sat"]) & (v >= P["shade_val"])
    grown = core.copy()
    for _ in range(P["grow"]):                                           # geodesic growth: only over shading pixels touching what is already skin
        grown = ndi.binary_dilation(grown, structure=np.ones((3, 3), bool)) & (shade_ok | core)
    if P.get("body_grow"):                                               # the far fist, shadowed arms: the darker skin between the bright patches (a loose rule, but not so dark that the leather bracers (value under 0.3) join in)
        cand = fg & (((h >= P.get("body_hue_min", 0)) & (h <= P.get("body_hue_max", P["hue"][1] + 4))) | redder) & (s >= P["body_sat"]) & (v >= P["body_val"])
        cand = ndi.binary_opening(cand, structure=np.ones((3, 3), bool)) | core
        g3 = grown.copy()
        for _ in range(P["body_grow"]):
            g3 = ndi.binary_dilation(g3, structure=np.ones((3, 3), bool)) & (cand | grown)
        if P.get("body_bridge"):                                         # a lit patch of a fist cut off from the rest by a dark knuckle line: a blob of that colour (body_bridge_min to body_bridge_max px, so never a whole tabard) within body_bridge px of the skin joins it
            bc = fg & (h >= P.get("body_hue_min", 0)) & (h <= P.get("bridge_hue_max", P["hue"][1] + 4)) & (s >= P["body_sat"]) & (v >= P["body_val"])
            bc = ndi.binary_opening(bc, structure=np.ones((3, 3), bool)) & ~g3
            lab3, n3 = ndi.label(bc, structure=np.ones((3, 3), bool))
            if n3:
                near3 = ndi.binary_dilation(g3, iterations=P["body_bridge"])
                sizes3 = ndi.sum(np.ones_like(lab3), lab3, range(1, n3 + 1))
                hit3 = ndi.sum(near3, lab3, range(1, n3 + 1))
                for i in range(n3):
                    if P["body_bridge_min"] <= sizes3[i] <= P["body_bridge_max"] and hit3[i] > 0:
                        g3 |= lab3 == i + 1
        grown = g3
    m = np.where(core, 1.0, np.where(grown, P["grow_w"], 0.0))
    if hair is not None and P.get("head_r") and (hair > 0.5).sum() > 50:
        zone = ndi.distance_transform_edt(~(hair > 0.5)) <= P["head_r"]      # near the hair: the ear, the temple, the shadowed neck
        loose = fg & zone & (hair < 0.3) & (s >= P["head_sat"]) & (v >= P["head_val"]) & (((h >= P["head_hue"][0]) & (h <= P["head_hue"][1])) | ((h >= P["head_wrap"]) if P.get("head_wrap") else False))
        if P["head_open"]:
            loose = ndi.binary_opening(loose, structure=np.ones((P["head_open"], P["head_open"]), bool)) | core
        g2 = grown.copy()
        for _ in range(P["head_grow"]):
            g2 = ndi.binary_dilation(g2, structure=np.ones((3, 3), bool)) & (loose | grown)
        if P.get("head_bridge"):                                         # skin parts cut off by a dark outline line (the lit brow ridge, the throat): a loose blob that lies within `head_bridge` px of the skin so far joins it
            lab2, n2 = ndi.label(loose & ~g2, structure=np.ones((3, 3), bool))
            if n2:
                near = ndi.binary_dilation(g2, iterations=P["head_bridge"])
                sizes2 = ndi.sum(np.ones_like(lab2), lab2, range(1, n2 + 1))
                hit = ndi.sum(near, lab2, range(1, n2 + 1))
                for i in range(n2):
                    if sizes2[i] >= P["head_bridge_min"] and hit[i] > 0:
                        g2 |= lab2 == i + 1
        grown = g2
        m = np.where(core, 1.0, np.where(grown & ~core, np.maximum(m, P["head_w"]), m))
    if P["blur"]:
        m = ndi.gaussian_filter(m, P["blur"]) * (ndi.binary_dilation(grown, iterations=1))
    if P.get("min_peak_val"):                                            # a piece of mask that is never bright is not skin (boot trim, a leather strap): its 90th-percentile value must reach min_peak_val
        lab4, n4 = ndi.label(m > 0.5, structure=np.ones((3, 3), bool))
        for i in range(1, n4 + 1):
            sel = lab4 == i
            if np.percentile(v[sel], 90) < P["min_peak_val"]:
                m[sel] = 0
    if P.get("ear_skin") and hair is not None and (hair > 0.5).any():   # the ear (2026-11-25): a small tan blob that lies against the hair, which the strict rules cannot find (it is thin and partly in shadow)
        E = P["ear_skin"]
        hmask = hair > 0.5
        dh = ndi.distance_transform_edt(~hmask)
        tan = fg & (h >= E["hue"][0]) & (h <= E["hue"][1]) & (s >= E["sat"]) & (v >= E["val"]) & ~hmask & (m < 0.5)
        elab, en = ndi.label(tan, structure=np.ones((3, 3), bool))
        ear = np.zeros(fg.shape, bool)
        for i in range(1, en + 1):
            em = elab == i
            if E["smin"] <= em.sum() <= E["smax"] and dh[em].max() <= E["reach"] and dh[em].min() <= 1.5:
                ear |= em
        if ear.any():
            m = np.maximum(m, ndi.gaussian_filter(ndi.binary_dilation(ear).astype(float), 0.5) * E["w"] * ndi.binary_dilation(ear, iterations=2))
    if P.get("no_hair") and hair is not None:                            # the hair (and the brows) it covers is never skin
        m = m * (1 - np.clip(hair * 1.5, 0, 1))
    return np.clip(m, 0, 1)


def skin_in_strip(strip, P, frame=512, hair=None):
    """strip: H x W x 4 uint8; hair: the strip's hair mask (H x W uint8) or None. Returns an H x W uint8 mask."""
    h, w = strip.shape[:2]
    out = np.zeros((h, w), np.uint8)
    n = w // frame
    for i in range(n):
        f = strip[:, i * frame:(i + 1) * frame]
        hf = None if hair is None else hair[:, i * frame:(i + 1) * frame].astype(float) / 255
        out[:, i * frame:(i + 1) * frame] = np.round(skin_in_frame(f, P, hf) * 255).astype(np.uint8)
    return out


def preview(strip, mask, frame=512, scale=0.5):
    """the strip on a grey ground with the skin painted cyan (strength = the mask)"""
    h, w = strip.shape[:2]
    bg = np.zeros((h, w, 3), float) + (70, 70, 90)
    a = strip[..., 3:4] / 255.0
    base = bg * (1 - a) + strip[..., :3] * a
    m = (mask / 255.0)[..., None]
    base = base * (1 - m) + np.array([0, 255, 255]) * m
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def run_one(strip_path, mask_path, P, preview_path=None, frame=512):
    strip = np.array(Image.open(strip_path).convert("RGBA"))
    hp = pathlib.Path(strip_path)
    hp = hp.with_name(hp.name[:-4] + ".hair-mask.png")
    hair = np.array(Image.open(hp).convert("L")) if hp.exists() else None      # the hair mask next to the strip (run hair_mask.py first)
    mask = skin_in_strip(strip, P, frame, hair)
    Image.fromarray(mask, "L").save(mask_path)
    per = [int((mask[:, i * frame:(i + 1) * frame] > 127).sum()) for i in range(strip.shape[1] // frame)]
    print(pathlib.Path(strip_path).name, "skin px per frame", per, "->", pathlib.Path(mask_path).name)
    if preview_path:
        pathlib.Path(preview_path).parent.mkdir(parents=True, exist_ok=True)
        preview(strip, mask, frame).save(preview_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strip", nargs="?")
    ap.add_argument("mask", nargs="?")
    ap.add_argument("--char", default="warrior")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--frame", type=int, default=512)
    ap.add_argument("--preview")
    a = ap.parse_args()
    P = PROFILES[a.char]
    if a.all:
        base = ROOT / "Animations" / a.char.capitalize()
        for folder in sorted(p for p in base.iterdir() if p.is_dir()):
            for strip in sorted(folder.glob("*_strip.png")):
                run_one(strip, strip.with_name(strip.name[:-4] + ".skin-mask.png"), P, ROOT / "source" / "skin_check" / (a.char + "_" + folder.name + ".png"), a.frame)
        return
    if not a.strip or not a.mask:
        ap.print_help()
        sys.exit(1)
    run_one(a.strip, a.mask, P, a.preview, a.frame)


if __name__ == "__main__":
    main()
