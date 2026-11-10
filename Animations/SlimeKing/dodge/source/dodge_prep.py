"""The King's dodge sheet (ChatGPT, 2026-11-11) came with the generator's own text labels painted under each panel (REST POSE, CROUCH, TAKE-OFF, APEX, LANDING, SETTLE) although the prompt forbade text.
The labels are painted out with flat magenta before the cut (rectangles measured on the 2528 x 1696 sheet; none of them touches a creature)."""
from PIL import Image, ImageDraw
LABELS = [(190, 682, 616, 785), (1100, 696, 1426, 785), (1915, 704, 2312, 785),
          (305, 1604, 523, 1696), (1086, 1604, 1442, 1696), (1969, 1604, 2265, 1696)]


def clean(src, out):
    im = Image.open(src).convert("RGB"); d = ImageDraw.Draw(im)
    for r in LABELS: d.rectangle(r, fill=(255, 0, 255))
    im.save(out); return out
