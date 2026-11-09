"""Colour MOCKUP of the lightning slime look the user asked for on 2026-11-08: the yellow body kept, the spikes ('tails') and the small bolts ('sparks') azure blue.
Not a generated picture: the user's inbox/lightning_slime_reference.jpg is split into the body and the parts outside it, and only the outside parts are re-coloured.
Usage: python azure_mockup.py <project root>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

root = sys.argv[1]
im = Image.open(root + '/inbox/lightning_slime_reference.jpg').convert('RGB')
hsv = np.array(im.convert('HSV')).astype(np.float32)
h = hsv[..., 0] * 360 / 255.0; s = hsv[..., 1] / 255.0; v = hsv[..., 2] / 255.0
bg = (h > 270) & (h < 340) & (s > 0.35)
bg = ndi.binary_dilation(bg, iterations=1) & (s > 0.2) | bg
outline = (v < 0.42) & ~bg
fg = ~bg & ~outline
lab, n = ndi.label(fg, structure=np.ones((3, 3)))
sizes = ndi.sum(fg, lab, range(1, n + 1))
dome_id = 1 + int(np.argmax(sizes))
dome = ndi.binary_fill_holes(lab == dome_id)
dome_near = ndi.binary_dilation(dome, iterations=14)
outside_ids = []
for i in range(1, n + 1):
    if i == dome_id: continue
    m = lab == i
    cnt = int(m.sum())
    if cnt < 30: continue
    inside = float((m & dome_near).sum()) / cnt
    if inside < 0.5: outside_ids.append(i)
print('components', n, 'dome', int(sizes[dome_id - 1]), 'outside parts', len(outside_ids))

# the outline pixels follow the nearest component, except along the body's own outline
outside = np.isin(lab, outside_ids)
lab2 = np.where(outside | (lab == dome_id), lab, 0)                   # only the real parts own outline pixels (not the specks)
dist, (iy, ix) = ndi.distance_transform_edt(lab2 == 0, return_indices=True)
near = lab2[iy, ix]
edge = ndi.binary_dilation(bg, iterations=4) & ~bg                    # the pixels between the outline and the flat magenta (dark red blends)
outside_o = (outline | edge) & ~outside & np.isin(near, outside_ids) & ~dome_near & (dist < 40)
# the dark outline between a spike and the body stays brown where it hugs the body; elsewhere it turns dark navy

TARGET = 208.0                       # azure
H = h.copy(); S = s.copy(); V = v.copy()
H[outside] = (H[outside] + (TARGET - 50.0)) % 360                 # yellow (about 50 deg) -> azure
S[outside] = np.clip(S[outside] * 1.05, 0, 1)
H[outside_o] = 222.0; S[outside_o] = np.maximum(S[outside_o], 0.7); V[outside_o] = np.minimum(V[outside_o], 0.40)   # navy outline
out = np.stack([H * 255 / 360.0, S * 255, V * 255], -1).clip(0, 255).astype(np.uint8)
res = Image.fromarray(out, 'HSV').convert('RGB')
res.save(root + '/inbox/lightning_slime_yellow_azure_mockup.png')

w = 1100; hgt = int(im.size[1] * w / im.size[0])
board = Image.new('RGB', (w * 2 + 20, hgt), (30, 30, 30))
board.paste(im.resize((w, hgt), Image.LANCZOS), (0, 0))
board.paste(res.resize((w, hgt), Image.LANCZOS), (w + 20, 0))
board.save(root + '/inbox/lightning_slime_azure_compare.png')
dbg = np.zeros(im.size[::-1] + (3,), np.uint8); dbg[dome] = (90, 90, 90); dbg[outside] = (0, 200, 255); dbg[outside_o] = (0, 90, 160)
Image.fromarray(dbg).resize((w // 2, hgt // 2)).save(root + '/inbox/_azure_mask_debug.png')
print('done')
