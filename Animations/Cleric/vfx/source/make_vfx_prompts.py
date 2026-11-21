#!/usr/bin/env python3
"""Builds the prompts for the Cleric's THREE TAILORED VFX SHEETS (2026-11-22) into Cleric_vfx_kit/ (one folder per sheet) and the masters in Animations/Cleric/vfx/source/.

  python Animations/Cleric/vfx/source/make_vfx_prompts.py

Why (docs/CLERIC_VFX.md and docs/AURAS.md): the user liked the painted layer made from the existing glow sheets but asked for (a) more detailed pieces designed for the Cleric's skills and (b) auras of the CLERIC's own shape
(not the Mage's turning cylinder), in the same element colours. Each sheet is 9 pieces on PURE BLACK, drawn additively (black = nothing), like every earlier glow sheet: ChatGPT, 1:1, no attachment, cut by
source/tools/cut_fx_sheet.py (brightness becomes transparency). The pieces split into the skill pieces and the AURA pieces (the aura of this character is built from layers, not a cylinder).

  01_holy_judgment  : gold      : hj_sky, hj_beam, hj_pillar, hj_seal, hj_cross, hj_nimbus, hj_wing, hj_feathers, hj_shock
  02_dark_drain     : violet    : dd_rope, dd_claws, dd_fissure, dd_seal, dd_wisp, dd_implode, dd_smoke, dd_veil, dd_motes
  03_crimson_pact   : crimson   : cp_seal, cp_chains, cp_heart, cp_flames, cp_shield, cp_embers, cp_roar, cp_cracked, cp_rain

Lessons from the earlier glow prompts: no attachment; a colour family named in hex; the background pure black with no haze; every piece centred with margin; NOT lightning for the soft elements; a reply per usual failure;
GROUND pieces drawn as FLAT top-down ellipses (the page lays them on the floor at a low angle), UPRIGHT pieces with their base at the bottom of the panel.
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
KIT = ROOT / "Cleric_vfx_kit"
BAR = "=" * 78

OUT = "OUTPUT: exactly ONE static image, a PNG texture sheet, and nothing else. Do NOT create a GIF, an animation, a video, a preview, extra images, alternate versions or a second attempt. No other files."
BG = ("BACKGROUND (very important): the whole image is PURE BLACK (#000000), perfectly flat and identical in every pixel. The effects are added over a game scene, so black means transparent and everything that is not black adds light. "
      "No gradient, no vignette, no dark-blue, dark-brown or dark-purple haze, no outlines, no borders, no divider lines or frames between the panels. A soft glow is allowed but must fade to pure black well before the panel edge.")
LAYOUT = ("LAYOUT: each effect is centred in its own panel with at least 8% pure black margin all round and never touches or crosses the panel edge. The nine panels must clearly differ in shape. "
          "Pieces that stand UPRIGHT have their base at the bottom of the panel (centred horizontally) and their top near the top. Pieces that lie on the GROUND are drawn as FLAT TOP-DOWN ELLIPSES seen from a low angle (wide and short), never tilted, never seen from above as a full circle.")

SHEETS = []

# ------------------------------------------------------------------------------------------------ 1. HOLY: JUDGMENT + THE CONSECRATION AURA
HOLY_HEAD = """CLERIC VFX SHEET 1 OF 3: HOLY JUDGMENT AND THE CONSECRATION AURA (one sheet, 3 x 3, no reference image, ask for 1:1). Written 2026-11-22. Works with ChatGPT (Gemini as a second try).

WHY (the user, 2026-11-22: the Cleric's animations look great but the code effects look simple; the Mage's turning aura cylinder reused for every character looks low effort, each character should get auras of its own SHAPE in the same element colours): this is the tailored version of the holy glow sheet (inbox/SPELL VFX/holy_fx_glow_sheet.png, the Slime King's), made for the Cleric. The page draws every piece ADDITIVELY (black = transparent) on top of its code effects. Pieces 1 to 5 and 9 are for SANCTIFIED JUDGMENT (the sky opens, a beam is charged, the pillar falls, a seal burns on the ground, a cross-shaped flare, a shockwave); pieces 6 to 8 are the CONSECRATION AURA the Cleric wears while he casts a holy skill (a nimbus behind his head, a wing of light at each side, feathers drifting): a grounded warrior-priest's aura, NOT a vortex.

THE ONE COLOUR: holy light, warm radiant GOLD, the same family as the existing holy pieces: warm white core (#FFFDF0), pale gold (#FFE896), gold (#FFC454), a little deep amber (#C98A1C) only on the faintest edges. No orange-red, no pink, no blue, no cyan, no violet, no green. NOT fire (no flames, embers, smoke). NOT lightning (no jagged zig-zags). Calm and radiant: smooth flowing ribbons, straight clean rays, four-point glints, soft droplets of liquid light, fine feathers. Allowed this time, because they are the Cleric's own: one radiant CROSS shape (piece 5) and feathered WINGS of light (piece 7); still NO letters, NO readable runes, NO faces, NO figures, NO angels (no bodies).

HOW TO USE
- No attachment. Ask for a 1:1 image (ChatGPT: 1024 x 1024 or larger; bigger is better). Paste everything between the two lines of equals signs.
- Generate 2 or 3 and keep the best; if only some panels are good, ask again for those and I join them.
- Save the sheet as inbox/Cleric_VFX/holy_judgment_sheet.png and tell me.
- What to look at: (1) pure flat black everywhere; (2) every panel is ONE separate effect centred with black all round; (3) one gold colour family, calm and radiant, no fire, no lightning, no figures; (4) the ground pieces (4 and 9) are FLAT wide ovals, the upright pieces (1, 2, 3, 6, 7) have their base at the bottom; (5) panel 6 is a radiant DISC seen front-on (a halo with rays), panel 7 ONE wing of light standing upright; (6) nothing touches a panel edge; (7) the nine panels clearly differ in shape; (8) one image only.
- Cut: `python source/tools/cut_fx_sheet.py inbox/Cleric_VFX/holy_judgment_sheet.png source/assets/fx --cols 3 --rows 3 --min 40 --pad 12 "--names=hj_sky,hj_beam,hj_pillar,hj_seal,hj_cross,hj_nimbus,hj_wing,hj_feathers,hj_shock"`. The page then uses them in `judgmentPaint` and in the holy aura (`clAura`), the existing pieces stay as the fallback.
- Replies if it goes wrong. If it draws fire, flames, embers or smoke: "Redo it. NO fire, NO flames, NO embers, NO smoke: only calm golden LIGHT." If it draws lightning or jagged zig-zags: "Redo it. NO lightning, NO jagged zig-zags, NO hairline forks." If it draws an angel, a figure, a face, a body or letters: "Redo it. NO angels, NO figures, NO faces, NO letters: only abstract light, one cross shape and one wing made of light." If it is orange, red, pink, blue, violet or green: "Redo it. One colour family only: warm gold (#FFC454 and #FFE896) with a warm white core (#FFFDF0) and a little deep amber (#C98A1C) on the faintest edges." If the background is not pure black or has a haze: "Redo it. The whole image is pure flat black (#000000), identical in every pixel, no gradient, no vignette, no haze, no panel borders." If the ground pieces are circles or tilted: "Redo it. Panels 4 and 9 are FLAT WIDE OVALS (about three times wider than tall) seen from a low angle, lying on the ground." If effects touch the edges: "Redo it. Each effect is centred in its panel with at least 8% pure black margin on every side and fades to pure black before the edge."
"""

HOLY = f"""{OUT}

Create a texture sheet of HOLY LIGHT effects for a 2D fantasy RPG game: a grid of 3 columns x 3 rows, nine equal square panels (the whole image is 1:1), read left to right, top row first, then the bottom row. Each panel holds ONE separate effect, centred, to be added over a game scene with additive blending. Do not draw any creature, character, figure, face, weapon, ground, landscape or text.

{BG}

STYLE: holy light, painted: warm radiant gold that flows like liquid light and shines like sunlight through haze: smooth ribbons, round droplets of liquid light, straight thin tapering rays, small four-point glints, fine feathers, soft round glows. A hard bright warm-white core (#FFFDF0) where it is brightest, pale gold (#FFE896) and gold (#FFC454) over most of it, a little deep amber (#C98A1C) only on the faintest edges. Hand-painted, rich and warm, with hard bright cores and soft falloff. ONE colour family only: gold. NOT fire (no flames, embers, smoke), NOT lightning (no jagged zig-zags, no hairline forks). No letters, no readable symbols, no faces, no figures, no angels. No pink, no magenta, no orange-red, no blue, no cyan, no violet, no green.

THE NINE EFFECTS:
1. Sky. An opening in the heavens seen from below, drawn only as light: a wide crown of soft light and long straight rays fanning DOWN and outward from a bright pale-gold glow at the TOP centre, like sunlight breaking through a gap in the clouds (the clouds themselves are not drawn: only the light), a few motes falling. About 90% of the panel width and 70% of its height, the glow at the top, fading to black toward the bottom.
2. Beam. A THIN descending beam of holy light, standing upright: a narrow bright warm-white core line (about 6% of the panel width) with a soft golden glow about 14% wide, a few tiny motes beside it, the top thinning and fading out, the bottom ending in a small bright spot at the base. About 16% of the panel width and 92% of its height, centred, base at the bottom.
3. Pillar. A tall FULL column of holy light standing on the ground, seen from the side: a bright warm-white core stripe, a golden body about 40% of the panel width, fine vertical streaks and feathery ripples inside it, gently flaring at the bottom into a wide bright base, tiny motes rising along it, the top thinning and fading out. About 46% of the panel width and 92% of its height, centred, base at the bottom.
4. Seal. An ORNATE magic seal lying on the ground, a FLAT WIDE OVAL (about 92% of the panel width and 30% of its height), centred: three concentric oval rings of golden light, the outer one with many small ABSTRACT tick marks and four-point glints spaced round it, between the rings a band of fine abstract geometric patterns (small diamonds and arcs, NOT letters, NOT readable runes), four small bright cardinal marks at the left, right, front and back; the middle EMPTY black with a faint soft glow.
5. Cross. A radiant CROSS of holy light, front-on: a bright warm-white core, an upright cross whose vertical arm is longer than the horizontal one, made of straight clean light with tapering ends, soft golden rays fanning between its arms, a thin soft ring round the core, a few tiny four-point glints. Perfectly symmetric left to right, centred, about 88% of the panel.
6. Nimbus. A radiant DISC of light seen front-on, like a halo or a sun behind a head: a bright soft golden disc about 55% of the panel with a thin bright ring at its edge, 24 to 32 straight thin rays of alternating lengths radiating from the ring out to about 95% of the panel, a faint inner ring and a soft glow; the middle only about 35% bright (so a head standing in front of it stays visible). Perfectly round, centred.
7. Wing. ONE wing made of light, standing upright, its base at the bottom centre: about 14 to 18 long feather-shaped streaks of golden light fanning up and outward in a curved sweep like the folded-open wing of a bird, bright warm-white along the leading edge, softer toward the tips, a few loose feathers and tiny motes drifting off its tips. NOT an angel, no body. About 70% of the panel width and 92% of its height.
8. Feathers. A loose cloud of 14 to 20 small glowing FEATHERS of golden light of different sizes and angles, drifting, mixed with 25 to 35 tiny glowing motes and 6 to 8 small four-point glints, scattered in a roughly round area of about 75% of the panel, brighter near the middle, none touching the edge.
9. Shock. A flat expanding SHOCKWAVE RING on the ground, a FLAT WIDE OVAL (about 94% of the panel width and 26% of its height), centred: one thick ring of bright warm-white and gold light with a soft outer glow and a thinner faint second ring just inside it, a few thin bright rays splashing outward along the ground, tiny four-point glints on the outer ring; the middle EMPTY black.

{LAYOUT}

FINAL REMINDER: output ONE single static PNG image only. No GIF, no extra images. Warm golden holy light on pure flat black; ribbons, straight rays, feathers and four-point glints; one cross and one wing of light are allowed; no fire, no lightning, no figures, no faces, no letters, no pink or orange-red, no creatures.
"""
SHEETS.append(("01_holy_judgment", "holy_judgment", HOLY_HEAD, HOLY, "inbox/Cleric_VFX/holy_judgment_sheet.png"))

# ------------------------------------------------------------------------------------------------ 2. DARK: DRAIN + THE SHADOW AURA
DARK_HEAD = """CLERIC VFX SHEET 2 OF 3: DARK DRAIN AND THE SHADOW AURA (one sheet, 3 x 3, no reference image, ask for 1:1). Written 2026-11-22. Works with ChatGPT (Gemini as a second try).

WHY: the tailored dark pieces for Unholy Siphon (a rope of tendrils from his fist, the soul-life flying back) and Dark Penance (claws and cracks from the ground), and the SHADOW AURA the Cleric wears while he casts a dark skill: shadow creeping up from the GROUND (claws and smoke at his feet, a veil of smoke at his shoulders), not a vortex. The existing dark pieces (the dark slime's dk_* from inbox/SPELL VFX/dark_fx_glow_sheet.png) stay as the fallback. The page draws every piece ADDITIVELY (black = transparent).

IMPORTANT (the user, 2026-11-22, about the first dark hit: a BLACK CIRCLE appeared on the opponent and was unnecessary): NO black discs, NO dark filled shapes. Everything on this sheet is made of glowing violet LIGHT on pure black; the "void orb" of a dark effect is only a RING of violet light with an empty black middle.

THE ONE COLOUR: the dark element's violet, the same family as the dark slime's: pale pink-violet core (#EBCDFF), bright violet (#AF4AFF), electric violet (#6914FF), deep indigo (#3C0AAA) only on the faintest edges. One exception, piece 5 only: the soul-wisp is pale GREEN-WHITE (#E8FFF0 core, #96EBAA body): it is the life being drained. No cyan, no blue-white, no magenta-pink, no orange, no yellow. NOT lightning: no straight jagged zig-zags, no hairline forks. The dark effects are CURVED: flowing, curling, tendril-like and crescent-shaped.

HOW TO USE
- No attachment. Ask for a 1:1 image (ChatGPT: 1024 x 1024 or larger). Paste everything between the two lines of equals signs.
- Generate 2 or 3 and keep the best; if only some panels are good, ask again for those and I join them.
- Save the sheet as inbox/Cleric_VFX/dark_drain_sheet.png and tell me.
- What to look at: (1) pure flat black everywhere and NO dark filled discs or blobs; (2) every panel is ONE separate effect centred with black all round; (3) violet only (piece 5 green-white), curved shapes, no lightning; (4) the ground pieces (3 and 4) are FLAT WIDE OVALS, the upright pieces (2, 7, 8) have their base at the bottom; (5) panel 1 is a horizontal rope, panel 5 a horizontal ribbon with a bright head at the RIGHT; (6) nothing touches a panel edge; (7) the nine panels clearly differ; (8) one image only.
- Cut: `python source/tools/cut_fx_sheet.py inbox/Cleric_VFX/dark_drain_sheet.png source/assets/fx --cols 3 --rows 3 --min 40 --pad 12 "--names=dd_rope,dd_claws,dd_fissure,dd_seal,dd_wisp,dd_implode,dd_smoke,dd_veil,dd_motes"`.
- Replies if it goes wrong. If it draws lightning or jagged zig-zags: "Redo it. NO lightning, NO straight jagged zig-zags, NO hairline forks: only CURVED flowing shapes: curling tendrils, swirls, crescents and soft wisps." If it draws black discs, filled dark shapes or a dark blob: "Redo it. NO black or dark filled shapes: everything is glowing violet LIGHT on pure black; a ring has an empty black middle." If it is cyan, blue-white, magenta, pink or orange: "Redo it. One colour family only: violet (#AF4AFF and #6914FF) with a pale pink-violet core (#EBCDFF) and deep indigo edges (#3C0AAA); only panel 5 is pale green-white." If it draws skulls, faces, hands with fingers or creatures: "Redo it. NO skulls, NO faces, NO creatures: only abstract shapes; the claws are plain curved dark spikes of light." If the background is not pure black or has a haze: "Redo it. The whole image is pure flat black (#000000), identical in every pixel, no gradient, no vignette, no haze, no panel borders." If effects touch the edges: "Redo it. Each effect is centred in its panel with at least 8% pure black margin on every side and fades to pure black before the edge."
"""

DARK = f"""{OUT}

Create a texture sheet of DARK-MAGIC GLOW effects for a 2D fantasy RPG game: a grid of 3 columns x 3 rows, nine equal square panels (the whole image is 1:1), read left to right, top row first, then the bottom row. Each panel holds ONE separate effect, centred, to be added over a game scene with additive blending. Do not draw any creature, character, face, skull, weapon, ground, landscape or text.

{BG} Never draw a black or dark filled disc, blob or shape: every effect is made of glowing light.

STYLE: the dark element, painted: glowing violet energy that flows like ink in water and smoke in wind: CURVED tendrils, slow swirls, thin crescents, soft curling wisps, with a bright pale pink-violet (#EBCDFF) core where it is hottest, electric violet (#AF4AFF, #6914FF) over most of it and deep indigo (#3C0AAA) only on the faintest edges. Hand-painted, rich and moody, with hard bright cores and soft falloff. ONE colour family only: violet (except piece 5, pale green-white). NOT lightning: no straight zig-zag bolts, no hairline forks, no jagged branching. No cyan, no blue-white, no magenta-pink, no orange, no yellow. No skulls, no faces, no creatures.

THE NINE EFFECTS:
1. Rope. A thick rope of dark energy lying HORIZONTAL, seen from the side: one long writhing tendril made of 3 to 5 twisting strands of violet light braided together, bright pale pink-violet core line along its middle, a few small curling side wisps, thin at both ends (the left end a tapering tail, the right end a sharp bright point), tiny motes. About 94% of the panel width and 22% of its height, centred.
2. Claws. A cluster of GRASPING CLAWS rising from the ground, upright, base at the bottom centre: 6 to 9 curved pointed spikes of violet light of different lengths and angles, like the dark fingers of a hand reaching up and curling, glowing bright pale violet along their edges, thin tendrils of smoke curling between them, a bright violet glow at their base. Plain curved spikes (NOT hands with fingers, NOT skeletal). About 60% of the panel width and 85% of its height.
3. Fissure. A network of glowing cracks on the ground, a FLAT WIDE OVAL (about 92% of the panel width and 30% of its height), centred: 9 to 13 curved cracks radiating from an EMPTY black middle, glowing violet with a pale core line, thin curling tendrils of violet light rising from them, brightest near the middle and thinning toward the edge.
4. Seal. An ORNATE dark seal lying on the ground, a FLAT WIDE OVAL (about 92% of the panel width and 30% of its height), centred: three concentric oval rings of violet light with a pale pink-violet edge, the outer ring with many small ABSTRACT tick marks and crescent shapes spaced round it, between the rings a band of fine curling abstract patterns (NOT letters, NOT readable runes), four small bright cardinal marks; the middle EMPTY black with a faint violet glow.
5. Wisp. A stream of stolen life flying to the RIGHT, HORIZONTAL: a ribbon of PALE GREEN-WHITE light (#E8FFF0 core, #96EBAA body) with a bright round head at the RIGHT end and a long flowing tail of 3 to 4 thin ribbons and tiny round droplets of light trailing to the LEFT, fading to black. About 94% of the panel width and 24% of its height, centred. (This is the only piece that is not violet.)
6. Implode. A collapsing ring: a bright thin ring of violet light about 70% of the panel in diameter with 14 to 20 thin curved wisps of violet light spiralling INWARD toward the centre like water down a drain, brighter toward the centre, a small bright pale pink-violet spark at the very middle; the area between the ring and the centre only faintly glowing, NOT black-filled. Round, centred.
7. Smoke. A tall column of dark smoke made of light, rising from the ground, upright, base at the bottom centre: a wide glowing base about 45% of the panel width narrowing to a curling column about 22% wide, rising to the top and dissolving into curling wisps and a few crescents, violet light along the curls with a pale core where the curls are thickest, tiny motes rising. About 50% of the panel width and 92% of its height.
8. Veil. A pair of tall, narrow ribbons of dark smoke made of light, hanging and curling, upright: two long soft S-curved ribbons of violet light about 8% of the panel wide each, side by side, a little apart, rising from the bottom and curling over at the top like smoke from two candles, with small crescents drifting off them. About 40% of the panel width and 92% of its height, centred.
9. Motes. A loose cloud of 30 to 45 tiny glowing violet motes of different sizes, 6 to 8 small thin crescents and 4 to 6 small four-point glints, scattered in a roughly round area of about 75% of the panel, brighter near the middle, none touching the edge.

{LAYOUT}

FINAL REMINDER: output ONE single static PNG image only. No GIF, no extra images. Violet dark-magic light on pure flat black (only the wisp is pale green-white); curved tendrils, crescents, smoke, claws as plain curved spikes; NO black or dark filled shapes, no lightning, no skulls, no faces, no creatures, no cyan, no pink, no orange.
"""
SHEETS.append(("02_dark_drain", "dark_drain", DARK_HEAD, DARK, "inbox/Cleric_VFX/dark_drain_sheet.png"))

# ------------------------------------------------------------------------------------------------ 3. CRIMSON: THE PACT + THE HEARTBEAT AURA
CRIM_HEAD = """CLERIC VFX SHEET 3 OF 3: THE CRIMSON PACT AND THE HEARTBEAT AURA (one sheet, 3 x 3, no reference image, ask for 1:1). Written 2026-11-22. Works with ChatGPT (Gemini as a second try).

WHY: the Spiteful Covenant is the Cleric's costly, dramatic skill: he pays half of his HP and a bigger barrier erupts. Today its colour is the gold holy pieces TINTED crimson in code and its barrier is the Mage's blue glass tinted. This sheet gives it pieces of its own: a contract seal, chains that break, a heartbeat ring, crimson flames, a SHIELD-shaped barrier outline of its own, embers, a roar shockwave, a cracked shield, falling embers. The HEARTBEAT AURA (a pulsing ring on the ground, small flames at his feet, rising embers, a veil of heat) is built from pieces 3, 4, 6 and 9. The page draws every piece ADDITIVELY (black = transparent).

THE ONE COLOUR: crimson and gold, NOT orange fire: warm white-gold core (#FFF0D8), pale gold (#FFD98A) only in the brightest cores, bright crimson (#FF3A2E), deep crimson (#D4121F), dark crimson (#7A0A18) only on the faintest edges. It is a holy-and-blood pact: it must look related to the Cleric's gold (the cores are gold-white) but clearly RED. No orange, no yellow flames, no pink, no blue, no violet, no green. NO skulls, NO faces, NO figures, NO blood splatter, NO liquid blood (only light and embers). NOT lightning (no zig-zags).

HOW TO USE
- No attachment. Ask for a 1:1 image (ChatGPT: 1024 x 1024 or larger). Paste everything between the two lines of equals signs.
- Generate 2 or 3 and keep the best; if only some panels are good, ask again for those and I join them.
- Save the sheet as inbox/Cleric_VFX/crimson_pact_sheet.png and tell me.
- What to look at: (1) pure flat black everywhere; (2) every panel is ONE separate effect centred with black all round; (3) crimson with gold-white cores, NOT orange; no skulls, no blood splatter, no figures; (4) the ground pieces (1, 3 and 7) are FLAT WIDE OVALS, the upright pieces (4, 5, 8) have their base at the bottom; (5) panel 5 is a tall shield-shaped outline (pointed at the bottom, a rune at the centre) standing upright; (6) nothing touches a panel edge; (7) the nine panels clearly differ; (8) one image only.
- Cut: `python source/tools/cut_fx_sheet.py inbox/Cleric_VFX/crimson_pact_sheet.png source/assets/fx --cols 3 --rows 3 --min 40 --pad 12 "--names=cp_seal,cp_chains,cp_heart,cp_flames,cp_shield,cp_embers,cp_roar,cp_cracked,cp_rain"`.
- Replies if it goes wrong. If it is orange or yellow like a campfire: "Redo it. NOT orange fire: crimson red (#FF3A2E, #D4121F) with warm white-gold cores (#FFF0D8); no orange, no yellow." If it draws skulls, faces, figures, blood splatter or liquid blood: "Redo it. NO skulls, NO faces, NO figures, NO blood splatter: only glowing crimson light, embers and abstract shapes." If it draws lightning: "Redo it. NO lightning, NO jagged zig-zags." If it is pink, blue, violet or green: "Redo it. One colour family only: crimson with gold-white cores." If the background is not pure black or has a haze: "Redo it. The whole image is pure flat black (#000000), identical in every pixel, no gradient, no vignette, no haze, no panel borders." If the ground pieces are circles or tilted: "Redo it. Panels 1, 3 and 7 are FLAT WIDE OVALS (about three times wider than tall) seen from a low angle, lying on the ground." If the shield is not upright or not a shield: "Redo it. Panel 5 is a tall upright SHIELD-shaped outline: flat top with a slightly curved edge, sides curving down to a point at the bottom, a double rim of crimson light, an abstract rune in the middle, drawn only as light with an empty middle." If effects touch the edges: "Redo it. Each effect is centred in its panel with at least 8% pure black margin on every side and fades to pure black before the edge."
"""

CRIM = f"""{OUT}

Create a texture sheet of CRIMSON PACT-MAGIC effects for a 2D fantasy RPG game: a grid of 3 columns x 3 rows, nine equal square panels (the whole image is 1:1), read left to right, top row first, then the bottom row. Each panel holds ONE separate effect, centred, to be added over a game scene with additive blending. Do not draw any creature, character, figure, face, skull, weapon, ground, landscape or text.

{BG}

STYLE: a holy-and-blood pact, painted: glowing crimson energy, hot and heavy, with a bright warm white-gold core (#FFF0D8) where it is brightest, pale gold (#FFD98A) only in the tiniest cores, bright crimson (#FF3A2E) and deep crimson (#D4121F) over most of it and dark crimson (#7A0A18) only on the faintest edges. Hand-painted, rich and dramatic, with hard bright cores and soft falloff. NOT orange fire and NOT a campfire: no orange and no yellow flames. NOT lightning. No skulls, no faces, no figures, no blood splatter, no liquid blood: only light, embers and abstract shapes. No pink, no blue, no violet, no green.

THE NINE EFFECTS:
1. Seal. A CONTRACT SEAL lying on the ground, a FLAT WIDE OVAL (about 92% of the panel width and 30% of its height), centred: two concentric oval rings of crimson light with a gold-white edge, the outer ring with small ABSTRACT tick marks, between the rings a band of fine abstract patterns (NOT letters, NOT readable runes), a bold simple flame-shaped mark in the centre (a single teardrop flame outline, flat, as part of the seal); four small bright cardinal marks.
2. Chains. A burst of BREAKING CHAINS, front-on: 7 to 10 chain links of glowing crimson light with gold-white edges flying outward from a bright centre in all directions like a shattering chain, some links broken in two, a few spark trails, tiny embers, a soft crimson glow in the middle. Roughly round, centred, about 88% of the panel.
3. Heart. A HEARTBEAT RING lying on the ground, a FLAT WIDE OVAL (about 90% of the panel width and 30% of its height), centred: one thick soft ring of bright crimson light with a hot gold-white inner edge and a wide soft outer glow, a fainter second ring just outside it, a few tiny embers on the ring; the middle EMPTY black.
4. Flames. THREE tall tongues of crimson flame standing together, upright, base at the bottom centre: one tall in the middle, two shorter at its sides, each a smooth S-curved teardrop of crimson light with a bright gold-white core and soft crimson edges, tiny embers rising. Crimson, NOT orange. About 50% of the panel width and 92% of its height.
5. Shield. A SHIELD-SHAPED BARRIER OUTLINE of light, upright, front-on: a tall shield with a flat top and a slightly curved top edge, sides curving down to a point at the bottom, a double rim of bright crimson light with a gold-white edge, an abstract simple mark at the centre (a bold flame teardrop outline or a plain cross of light), the inside only a faint crimson glow (about 20% brightness) so something standing behind it stays visible, a few tiny motes at its rim. About 62% of the panel width and 92% of its height, centred.
6. Embers. A rising cloud of EMBERS: 40 to 60 small glowing crimson and gold-white embers and sparks of different sizes drifting upward, brighter and denser near the bottom and thinning toward the top, a few small curved trails. About 60% of the panel width and 92% of its height, centred, base at the bottom.
7. Roar. A ROAR SHOCKWAVE lying on the ground, a FLAT WIDE OVAL (about 94% of the panel width and 28% of its height), centred: one thick bright ring of crimson light with a gold-white edge, 16 to 22 sharp spikes of light radiating outward from the ring along the ground like a crown, tiny embers; the middle EMPTY black.
8. Cracked. A CRACKED SHIELD: the same tall shield shape as panel 5 but broken: 8 to 12 fragments of the crimson shield rim hanging in the air with dark gaps between them, glowing cracks of gold-white light running across it, a few fragments flying off, tiny embers. Upright, about 66% of the panel width and 92% of its height, centred.
9. Rain. A downward drift of FALLING EMBERS: 30 to 45 small teardrop-shaped drops of crimson light and tiny embers falling, each with a short bright trail above it, a few tiny gold-white sparks, brighter in the middle, spread over about 70% of the panel width and 92% of its height, none touching the edge.

{LAYOUT}

FINAL REMINDER: output ONE single static PNG image only. No GIF, no extra images. Crimson pact-magic light with gold-white cores on pure flat black, NOT orange fire; no skulls, no faces, no figures, no blood splatter, no lightning, no pink, no blue, no violet, no green, no creatures.
"""
SHEETS.append(("03_crimson_pact", "crimson_pact", CRIM_HEAD, CRIM, "inbox/Cleric_VFX/crimson_pact_sheet.png"))


def main():
    KIT.mkdir(exist_ok=True)
    for folder, name, head, body, saved in SHEETS:
        (HERE / f"{name}_prompt.txt").write_text(head + "\n" + BAR + "\n" + body.rstrip("\n") + "\n" + BAR + "\n", encoding="utf-8", newline="\n")
        kd = KIT / folder
        kd.mkdir(exist_ok=True)
        (kd / "1_paste_this_prompt.txt").write_text(body, encoding="utf-8", newline="\n")
        steps = ["1. Start a NEW chat in ChatGPT (Gemini as a second try). NO attachment: these are pure effect sheets.",
                 "2. Ask for a 1:1 square image, as large as it will give you (1024 x 1024 or more).",
                 "3. Paste the whole text of 1_paste_this_prompt.txt.",
                 "4. Generate 2 or 3 and keep the best. If it says it is out of image capacity, wait; do not shorten the prompt.",
                 f"5. Save the sheet as {saved} and tell me (or name the files after the panels you want from each). I cut it, wire the pieces into the Cleric's effects and the auras, and you judge it in motion."]
        look = [l[2:] for l in head.split("\n") if l.startswith("- What to look at:") or l.startswith("- Replies if it goes wrong")]
        (kd / "2_what_to_check.txt").write_text(f"CLERIC VFX SHEET: {name.upper().replace('_', ' ')}: what to do and what to check\n\n" + "\n".join(steps) + "\n\n" + "\n\n".join(look) +
                                                "\n\nIf ONE panel is wrong tell me which; I will give you a one-line fix or join the good panels of several sheets.\n", encoding="utf-8", newline="\n")
    (KIT / "0_read_me_first.txt").write_text(
        """CLERIC VFX: THE THREE TAILORED SHEETS (written 2026-11-22)

Order: 01_holy_judgment first (Sanctified Judgment is the skill that most needs more), then 02_dark_drain (Unholy Siphon, Dark Penance), then 03_crimson_pact (Spiteful Covenant).
Each folder: the prompt to paste (no attachment) and what to check with the replies. Save the sheets in inbox/Cleric_VFX/ (the exact name is in each check file).

What is new compared with the earlier glow sheets: the pieces are designed for the Cleric's skills and for the Cleric's OWN AURAS (docs/AURAS.md: each character gets auras of its own shape, in the same element colours; the Mage keeps her turning cylinder, the Cleric's holy aura is a consecration of a ground seal, a nimbus and wings, the dark one is shadow creeping from the ground, the crimson one is a heartbeat).
The existing pieces stay as the fallback underneath, so nothing already built is lost.
""", encoding="utf-8", newline="\n")
    print("done:", [s[0] for s in SHEETS])


if __name__ == "__main__":
    main()
