#!/usr/bin/env python3
"""Writes the Slime King's TREASURE prompts, second try (2026-11-12): three variations A, B and C of a hoard that stands BEHIND the King, who guards it facing left, mixing gold with SPOILS OF WAR.

  python Animations/SlimeKing/source/write_treasure_prompts.py

The user (2026-11-12): the first pile (gold only, 1.25 of his width, centred) made him look like he sat on it, the small version (0.48) was too small, and 'the look I have in mind is the Slime King guarding the treasures, the
treasures behind him, facing left'. The game's treasures feature will later unlock things like 'elite slime core', 'goblin warrior shield', 'gloom wolf dark pelt' (spoils of war), so the hoard should mix gold with
such trophies ('should we mix them up?': YES, and the three variations are three mixes: A mostly gold with three trophies, B half and half with one trophy per act, C a trophy wall with little gold).
Output: Animations/SlimeKing/treasure_pile/source/treasure_v2_<A|B|C>_prompt.txt (the user pastes the text between the two lines of equals signs into ChatGPT or Gemini with Animations/SlimeKing/reference_image.png
attached as a style reference only). The user saves the pictures as inbox/slime_king_treasure_A.png (B, C); cut_treasure.py <file> <A|B|C> cuts each into source/assets/fx/treasure_pile_<tag>.png.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

STYLE = """STYLE: the same matte hand-painted style as the attached reference image (the Slime King's golden crown and golden jewelled staff): warm gold with cream highlights and brown shadows (gold #E8B83A, shadows #8A5A14, highlights #FFF2A8), a thin dark warm-brown outline round every object, soft painted shading, no gloss spots, NO glow. The light comes from the upper left, so the left sides of the objects are lighter and the right sides darker. The attached image is ONLY a style and colour reference: do NOT draw the King or any creature."""

BEHIND = """THE PLACE OF THE PICTURE (very important): in the game this picture stands BEHIND a big ivory slime king who stands in FRONT of it, facing LEFT toward the hero and guarding the hoard (the King is NOT in this picture). So draw the hoard as a BACKDROP: a wide heap seen from the front, slightly from above, that is TALLER at the RIGHT and in the BACK and slopes DOWN toward the LEFT (the hero's side); its front edge is a clean, fairly flat base line on the floor. The King's body will cover the lower middle of the heap, so put the important, recognisable objects on the TOP, on the LEFT slope and on the RIGHT side, and keep the lower middle simple (coins). Everything that has a front (a shield's painted face, a pelt's head, a chest's opening, an axe blade) is turned to FACE LEFT, toward the hero."""

SPOILS = """THE SPOILS OF WAR (trophies taken from defeated monsters; the game's treasure feature will later unlock items like these, so they must be easy to recognise at a glance, big, bold and chunky, with a strong silhouette; at game size the whole picture is only about 250 pixels wide, so draw few, large objects, not many tiny ones):
- ELITE SLIME CORE: a fist-sized rounded lump of cracked matte GREY STONE with pale mineral flecks and a warm amber-orange crystal heart showing through the crack (painted flat amber, no glow).
- GOBLIN WARRIOR SHIELD: a round, dented wooden shield with a rough iron rim and iron studs, a leather strap, and a crude cartoon goblin face painted on it in green (two angry eyes, a jagged-tooth grin), facing left.
- GLOOM WOLF DARK PELT: a thick shaggy fur pelt in charcoal black with a cold blue-grey sheen on the fur tips (NOT violet, NOT purple), draped over the heap, a wolf head with closed eyes and small fangs at one end turned to the left, paws hanging.
- OGRE CLUB: a heavy studded club of dark knotted wood with iron spikes.
- ORC WAR AXE: a crude notched iron axe with a red cloth wrapped round its handle.
- SLIME CORES: small round gem-like cores of the four element slimes: fire (red-orange), ice (pale blue), lightning (bright yellow), dark (near-black deep blue with a pale blue rim).
(Colour safety: nothing on the pile is pink, magenta or purple.)"""

COMMON_NO = """NOTHING ELSE: no King or slime, no character, no floor, no ground line, no shadow on the floor, no cave, no wall, no background objects, no text, no letters, no numbers, no lettering on coins, shields or banners.

NO SOFT EFFECTS: no glow, no halo, no light rays, no sparkles, no star glints, no bloom, no blur, no smoke, no dust, no motes, no see-through anything, no gradient fade-outs, no light spilling onto the background. Every object has a hard, clean, opaque edge (the game adds all the glimmer and light)."""

BACKGROUND = """BACKGROUND AND LAYOUT: one flat pure MAGENTA (#FF00FF) background filling the whole image, identical in every pixel. No gradient, floor, ground line, shadow, glow or vignette. No grid lines, no borders. No text, numbers or labels. No pink, magenta or purple on the treasure itself (the jewels are red, blue and green)."""

REPLIES = """- Replies if it goes wrong. If it draws a floor, a shadow, a cave, a wall or any background: "Redo it. Only the hoard on flat magenta: no floor, no ground shadow, no cave, no wall, no background of any kind." If the King or a slime appears: "Redo it. No King, no slime, no creature: only the objects." If it glows or sparkles: "Redo it. NO glow, NO sparkles, NO light rays: only crisp solid painted objects with thin outlines." If it is symmetric or the same height everywhere: "Redo it. The heap is TALLEST at the right and in the back and slopes down to the LEFT; its front edge is flat on the floor." If the trophies are tiny or unreadable: "Redo it. Fewer, BIGGER trophies: each one clearly recognisable on its own at a glance (the grey stone core with the amber heart, the round goblin shield with the green face, the black fur pelt with the wolf head)." If the shield, pelt or chests face right: "Redo it. Everything with a front faces LEFT." If anything is pink, magenta or purple: "Redo it. Nothing on the pile is pink, magenta or purple: the pelt is charcoal black with a blue-grey sheen, the dark core is near-black blue." If it draws text or letters: "Redo it. No text, no letters, no numbers anywhere." If the background is not flat magenta: "Redo it. One flat pure magenta (#FF00FF) background, identical in every pixel." If the heap is cut by an edge or too small: "Redo it. The heap fills about 88% of the picture's width, its base about 92% of the way down, with a clear border of flat magenta all round." """

VARIANTS = {
    "A": dict(
        title="A: THE HOARD (mostly gold, three trophies)", ratio="about 2.2 : 1",
        what="""A rich heap of gold with three spoils of war on it. About three quarters of the pile is gold, gems and royal treasure, one quarter is trophies.""",
        body="""THE HEAP: ONE wide heap, about 2.2 times as wide as it is tall. Mostly loose GOLD COINS (round, thick, with a rim, many tilted or on edge), with ingots, a few jewels (ruby red, sapphire blue, emerald green), one golden crown on the top, two jewelled goblets and one small open wooden chest with gold bands on the LEFT slope spilling coins and facing left.
THE THREE TROPHIES (big and bold, placed where the King will not hide them): the ELITE SLIME CORE sitting on the TOP of the heap (a little right of the middle), the GOBLIN WARRIOR SHIELD leaning against the LEFT slope at the front, its green face turned to the left, and the GLOOM WOLF DARK PELT draped over the RIGHT shoulder of the heap with its wolf head turned left. Also four small SLIME CORES (fire, ice, lightning, dark) lying among the coins instead of ordinary gems.""",
        final="ONE wide heap (about 2.2 : 1), tallest at the right and in the back, sloping down to the left, mostly gold coins with a golden crown, a small open chest facing left, ingots and jewels, and three big bold trophies (the grey stone Elite Slime core with its amber heart on top, the round goblin shield with the green face leaning on the left slope, the black wolf pelt draped over the right shoulder)"),
    "B": dict(
        title="B: THE SPOILS OF WAR (half gold, five trophies: one per act)", ratio="about 1.9 : 1",
        what="""A balanced hoard: half gold, half spoils of war, with one trophy from each of the game's five acts (slimes, goblins, wolves, ogres, orcs).""",
        body="""THE HEAP: ONE heap, about 1.9 times as wide as it is tall, rising in steps toward the back right like a rocky hill: a base layer of gold coins and ingots, a middle layer of trophies, a top layer at the back right. Gold is about half of what you see: coins, ingots, one open wooden chest with gold bands facing left on the left slope, a golden goblet, and a few jewels (ruby red, sapphire blue, emerald green).
THE FIVE TROPHIES, one per act, all big and clearly visible: the ELITE SLIME CORE on the front of the heap near the middle-left, the GOBLIN WARRIOR SHIELD leaning against the left slope facing left, the GLOOM WOLF DARK PELT draped over the top with its head turned left, the OGRE CLUB leaning against the back right with its spiked head up, and the ORC WAR AXE stuck blade-first into the top of the heap, its red cloth hanging. Two or three small SLIME CORES (fire, ice, lightning) lie among the coins.""",
        final="ONE heap (about 1.9 : 1), rising in steps toward the back right and sloping down to the left, half gold coins, ingots and an open chest facing left, half spoils of war, five big bold trophies one per act (the grey stone Elite Slime core with its amber heart, the round goblin shield with the green face facing left, the black wolf pelt with the head turned left, the studded ogre club, the notched orc axe)"),
    "C": dict(
        title="C: THE TROPHY WALL (mostly spoils, little gold)", ratio="about 1.7 : 1",
        what="""A war-trophy corner: the monsters' spoils displayed on a crude wooden rack and crates behind a low mound of gold. About a quarter of what you see is gold, three quarters spoils of war.""",
        body="""THE ARRANGEMENT: ONE compact group, about 1.7 times as wide as it is tall: in FRONT a low mound of gold coins with ingots and one small open chest facing left (about a quarter of the picture); BEHIND and above it a crude WOODEN TROPHY RACK built from rough planks, posts and crates (it can be taller at the RIGHT, lower at the LEFT) on which the spoils are displayed: the GOBLIN WARRIOR SHIELD mounted on the front of a post facing left, the GLOOM WOLF DARK PELT hung over a beam with its wolf head turned left, the ELITE SLIME CORE on a small crate in the middle, the OGRE CLUB and the ORC WAR AXE crossed behind the rack at the back right, and a row of four small SLIME CORES (fire, ice, lightning, dark) on a plank shelf. The wood is rough, weathered brown with iron straps, in the same warm matte painted style.""",
        final="ONE compact group (about 1.7 : 1): a low mound of gold coins, ingots and a small open chest facing left in front, and behind it a crude wooden trophy rack taller at the right with the spoils of war displayed (the round goblin shield with the green face facing left, the black wolf pelt with its head turned left, the grey stone Elite Slime core with its amber heart, the studded ogre club and the notched orc axe crossed, a shelf of four small slime cores)"),
}


def build(tag, v):
    head = "SLIME KING: THE TREASURE, SECOND TRY, VARIATION %s. Written 2026-11-12.\n\n" % v["title"]
    why = """WHY (the user, 2026-11-12): the first pile was gold only, too big and centred under him (he looked like he sat on it); the small one was too small. 'The look I have in mind: the Slime King guarding the treasures, the treasures behind him, facing left. The treasures feature later unlocks things like elite slime core, goblin warrior shield, gloom wolf dark pelt: spoils of war. Should we mix them up?' YES: gold says 'treasure' at a glance and the spoils say what the game is about. This is variation %s of THREE (A mostly gold, B half and half, C a trophy wall): generate each in its own chat so they differ, then the user picks, or tests all three in the page. %s

""" % (tag, v["what"])
    how = """HOW TO USE
- ChatGPT first (it keeps the layout and the flat magenta), Gemini is the second try. Attach ONE image: Animations/SlimeKing/reference_image.png (a style and gold reference ONLY: the prompt says not to draw the King). Ask for a 3:2 landscape image, as large as it will give you. Paste everything between the two lines of equals signs.
- Generate a few and keep the best. Save it in inbox/ as inbox/slime_king_treasure_%s.png and tell me. I cut it with Animations/SlimeKing/source/cut_treasure.py <file> %s (the magenta keyed out, trimmed to the objects) into source/assets/fx/treasure_pile_%s.png and check it behind the King.
- What I check: (1) ONE group, about %s wide to high, taller at the RIGHT and in the back, sloping down to the LEFT, a flat base line; (2) the trophies are big, bold and recognisable at a glance: the grey stone core with the amber heart, the round goblin shield with the green face, the black fur pelt with the wolf head, and for B and C the studded club and the notched axe; (3) everything with a front faces LEFT; (4) the gold is the King's warm gold, thin dark warm-brown outlines, matte painted, light from the upper left; (5) crisp opaque, NO glow, NO sparkles; (6) NO floor, NO shadow, NO background, NO King, NO text; (7) flat magenta around it, nothing pink, magenta or purple on the pile; (8) the group fills about 88%% of the picture's width, base about 92%% down; (9) no GIF and no extra images.
""" % (tag, tag, tag, v["ratio"])
    prompt = """==============================================================================
OUTPUT: exactly ONE static image and nothing else. Do NOT create a GIF, an animation, a video, extra images, alternate versions or a second attempt. No other files.

Create one picture: a PROP for a fantasy RPG boss stage: a big treasure hoard mixed with spoils of war, seen from the front, slightly from above. VARIATION %s.

%s

%s

%s

%s

%s

SCALE AND PLACE: the group fills about 88%% of the picture's width and its lowest point (the base) is about 92%% of the way down the picture, centred, with a clear border of flat magenta on every side. Do not draw it bigger than that.

%s

FINAL REMINDER: output ONE single static image only. %s. Hand-painted in the warm gold of the King's crown, thin dark warm-brown outlines, crisp and opaque, the trophies big and bold, everything with a front facing LEFT, NO glow or sparkles, NO floor or shadow or background, NO King, NO text, on flat pure magenta, filling about 88%% of the width.
==============================================================================
""" % (v["title"], BEHIND, v["body"], SPOILS, STYLE, COMMON_NO, BACKGROUND, v["final"])
    return head + why + how + REPLIES + "\n\n" + prompt


if __name__ == "__main__":
    d = os.path.join(ROOT, "Animations", "SlimeKing", "treasure_pile", "source"); os.makedirs(d, exist_ok=True)
    for tag, v in VARIANTS.items():
        path = os.path.join(d, "treasure_v2_%s_prompt.txt" % tag)
        open(path, "w", encoding="utf-8").write(build(tag, v))
        print("wrote", os.path.relpath(path, ROOT), os.path.getsize(path), "bytes")
