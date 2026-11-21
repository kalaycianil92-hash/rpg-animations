"""Builds the Cleric's hit, death, dodge, run and BLOCK prompts (masters in Animations/Cleric/<anim>/source/ and the paste-ready kit folders in Cleric_animation_kit/). The Block (05_block) was added 2026-11-21 from the Warrior's Block prompt.

Written 2026-11-21 from the Rogue's four prompts (Animations/Rogue/<anim>/source/*_gemini_prompt.txt, all of which worked first time with ChatGPT) with the Cleric's armoured look.
The character paragraph is read from Animations/Cleric/source/cleric_description.txt (word for word, as the PLAYBOOK says), so a change of the look is one edit there and a rerun of this script.

    python Animations/Cleric/source/make_cleric_prompts.py

What differs from the Rogue's prompts, and why:
- HEAVY ARMOUR: the hit is a heavy shove and rock, not a flail; the dodge is a short heavy hop (peak 15% of his height instead of 20%); the armour stays on and rigid in every panel.
- His head is about 14% of his height (the Rogue's 19%), so the head sizes asked for are about 8% of the panel (the Rogue's 10 to 11%).
- ChatGPT drew the idle at 85% of the panel when 60% was asked, so the standing figure is asked at 50 to 55% (the cutters rescale; the room is for the recoil, the hop and the stride).
- No cloak or scarf: the front and back panels of the tabard (and the hair tips) are the secondary motion.
- His stance is a guard: the NEAR fist at the middle of the chest (66% of his height), the FAR fist at belt height out in front (57%), a wide stance (heel to toe 57% of his height), not the Rogue's low fists.
"""
import pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
CLERIC = HERE.parent                      # Animations/Cleric
ROOT = CLERIC.parent.parent               # the project root
KIT = ROOT / "Cleric_animation_kit"
REF = CLERIC / "reference_image.png"
DEATH_POSES = ROOT / "Animations" / "Warrior" / "death" / "source" / "old_character_death_pose_reference.png"
DESC = (HERE / "cleric_description.txt").read_text(encoding="utf-8").strip()
BAR = "=" * 78

OUT = "OUTPUT: exactly ONE static image, a PNG sprite sheet, and nothing else. Do NOT create a GIF, an animation, a video, a preview, extra images, alternate versions or a second attempt. No other files."
FINAL = "FINAL REMINDER: output ONE single static PNG image only. No GIF, no extra images."
GRID = "Create the sprite sheet: a grid of 3 columns x 2 rows, six equal square panels, read left to right, top row first, then the bottom row."
CHAR = ("CHARACTER: the exact same character as in the attached reference image: " + DESC + ". Keep the same painted game-sprite style, thick dark outlines, colors, proportions, face and "
        "three-quarter head angle. Do not redesign anything.")
STANCE = ("In the ready stance (as in the reference) the NEAR arm (the one closest to the viewer) is bent in front of his chest with its fist at the middle of his chest, close in front of his breastbone, "
          "and the FAR arm (the one farther from the viewer) is held lower and out in front of him with its fist at belt height, about one forearm length ahead of his belt.")
ARMS = ("ARMS: the near arm (the one closest to the viewer, the fist at his chest in the reference) always stays in front of the torso, and the far arm (the one farther from the viewer, the fist at belt height "
        "out in front of him in the reference) always stays on the far side of the torso. Never swap them between panels.")
ARMOUR = ("He is heavily armoured: the plate armour, the pauldrons, the vambraces, the knee plates, the greaves and the tabard stay on him in every panel, rigid and exactly as in the reference. "
          "No helmet, no gauntlets and no cape appear in any panel; his hands are bare.")
BG = ("BACKGROUND AND LAYOUT: one flat pure magenta (#FF00FF) background filling the whole image, identical in every pixel. No gradient, floor, ground line, cast shadow, glow or vignette. "
      "No grid lines or borders between panels. Leave about {margin}% empty margin around the figure in each panel; the whole character, with the tabard, the hands and the feet, must stay fully inside its own panel "
      "and never touch or cross a panel edge. No text, numbers, labels, dust{more} or any other effects. No magenta or pink on the character himself.")


def block(*parts):
    return "\n\n".join(p for p in parts if p) + "\n"


# --------------------------------------------------------------------------------------------- HIT
HIT_HEADER = """CLERIC HIT REACTION PROMPT (6 frames, 3 x 2). Written 2026-11-21 from the Rogue's hit prompt. Works with Gemini or ChatGPT (ChatGPT keeps sizes and spacing better).

HOW TO USE
- Attach ONE image: Animations/Cleric/reference_image.png (the armoured look). Ask for a 3:2 image (ChatGPT: 1536 x 1024). Paste everything between the two lines of equals signs.
- Generate several and keep the best. If only some frames are bad, ask again for those poses only and I join the good frames.
- Save the sheet in inbox/ as cleric_hit_sheet.png and tell me.
- What to look at: (1) the same man in all six panels (emerald hair, pointed ear, silver-steel plate with the big pauldrons, cream tabard with the gold cross, steel vambraces, no helmet, no cape); (2) panels 1 and 6 are the reference stance (the near fist at the middle of the chest, the far fist at belt height in front); (3) the rear boot stays on the same spot in every panel; (4) both hands are bare closed fists in every panel (no gauntlets); (5) the same size in every panel and nothing touches a panel edge (the idle came out at 85% of the panel when 60% was asked, so this prompt asks for 55%; the cutter rescales, but there must be margin); (6) the recoil is a heavy rock, not a flail, and the armour stays on; (7) one image only.
- Planned cut (default despill; green hair and steel are safe with it): `python source/tools/slice_keypose_sheet.py cleric_hit_sheet.png Animations/Cleric/hit/mailed_hit_6frame_strip.png --cols 3 --rows 2 --height 408 --scale-from median --modes heel --heel-x 174 --fit 1,6`. His idle: rear heel 173 to 174, front toe 411 to 412, middle of the feet 293, frame 1 407 px tall. Frames 1 and 6 must match it (check with `check_strip.py`); `--scale-mult` fixes panels drawn bigger or smaller (measure the face and the boots).
"""
HIT = block(
    OUT,
    GRID + " The six panels are the key poses of a \"hit reaction\": the character is struck from the front, rocks back, staggers and recovers.",
    CHAR,
    "VIEW: strict side view of the body and legs, he faces RIGHT in every panel, with the head turned a little toward the viewer in the same three-quarter view as in the reference (in the panels where he is struck, the head may turn with the blow). "
    "The attacker is off-screen to the right, so the blow comes from the front and shoves his head and upper body back toward the LEFT.",
    "NO ITEMS AND NO EFFECTS: no mace, no club, no wand, no sword, no shield, no orb, no book, no weapon of any kind, nothing in his hands. No glow, smoke, sparks, impact stars, blood, sweat drops, motion lines or effects of any kind.",
    ARMOUR + " The reaction is a heavy shove and rock, not a flail.",
    "HANDS (in every panel): both hands are bare, tight CLOSED FISTS with nothing in them, never open, never splayed, never gloved. " + STANCE,
    ARMS,
    "SAME SCALE AND FLOOR (very important): draw him at exactly the same size in all six panels, the same standing size as in the reference. Do not zoom in or out between panels, and do NOT make him bigger in the recoil frames. "
    "His head, from the top of the hair to the chin, is about 8% of the panel height, and the standing figure, from the top of the head to the soles of the boots, is only about 55% of the panel height, so that there is plenty of empty space all round him. "
    "The floor is at the same height in every panel, about 82% down the panel. The WHOLE body, from the top of the head to the soles of both boots, is visible in every panel, never cropped. "
    "The rear foot (the left foot) stays on the floor at the same spot in every panel, as if on an invisible floor line; only the body, head, arms and front foot move. He does not travel across the panel.",
    "THE SIX FRAMES:\n"
    "1. Impact. His ready stance exactly like the reference: knees slightly bent, the near fist at the middle of his chest, the far fist at belt height in front of him, both feet planted. The blow has just landed: eyes squeezed shut, teeth gritted, head just starting to snap back.\n"
    "2. Peak recoil. Head and upper body rocked far back to the left (the torso leaning back about 25 degrees), chin up, mouth open in a grunt of pain. The near arm is pushed out to the front and up, the far arm pushed out behind him, both fists clenched. The front foot is lifted slightly off the floor, the knees slightly bent. The front and back panels of the tabard swing forward past his legs.\n"
    "3. Stagger. Still leaning back but starting to recover, the rear leg braced hard, the front foot touching down again, one arm swinging forward for balance, wincing. The tabard panels swing back.\n"
    "4. Recover. The torso comes forward again, the head drops to face right, the knees bent, both fists coming back toward their places (the near fist at the chest, the far fist at belt height), grimacing.\n"
    "5. Settle. Nearly back in the stance, slightly hunched forward, the fists almost in place, eyes open and glaring at the enemy.\n"
    "6. Back to the stance. The same ready stance as the reference and as panel 1, the fists in their places, neutral determined face. The tabard hangs still.",
    BG.format(margin=12, more=""),
    FINAL)

# --------------------------------------------------------------------------------------------- DEATH
DEATH_HEADER = """CLERIC DEATH PROMPT (6 frames, 3 x 2, pose transfer from an older strip). Written 2026-11-21 from the Rogue's death prompt. Works with Gemini or ChatGPT.

HOW TO USE
- Attach TWO images, in this order: FIRST Animations/Warrior/death/source/old_character_death_pose_reference.png (a strip of six poses of a man being hit, falling backwards and lying; it is only a POSE reference, it is on a white background and wears bandages), SECOND Animations/Cleric/reference_image.png (the armoured elf). Ask for a 3:2 image (ChatGPT: 1536 x 1024). Paste everything between the two lines of equals signs.
- If the result copies the old outfit (bare chest, bandages, bare feet), reply: "Redo it. The character in all panels must be the elven man from the second image, wearing his silver-steel plate armour with the big pauldrons, his cream tabard with the gold cross, his dark-brown belt, trousers and boots with the steel knee plates and greaves. Do not copy any clothing from the first image."
- If only some frames are bad, ask again for those poses only; I join the good frames.
- Save the sheet in inbox/ as cleric_death_sheet.png and tell me.
- What to look at: (1) the same man and outfit in all six panels, also when he is falling and lying (emerald hair, pointed ear, plate armour, tabard, boots, no bandages, no helmet); (2) the poses follow the strip: 1 and 2 standing, 3 and 4 falling, 5 landing with the legs up, 6 lying flat; (3) the SAME SIZE in every panel: the lessons of the mage's and the Rogue's death sheets were that close-up faces in panels 1 and 2 come out too big and the falling panels too big; the prompt asks for the head size as a share of the panel and for the floor lower; measure the face and the boots in the cut (`--scale-mult`); (4) nothing is cropped and nothing touches a panel edge (the armoured body is wide when he lies); (5) no weapon, bare empty fists; (6) one image only.
- Planned cut: `python source/tools/slice_keypose_sheet.py cleric_death_sheet.png Animations/Cleric/death/mailed_death_6frame_strip.png --cols 3 --rows 2 --height 408 --scale-from panel1 --modes heel,heel,center,center,center,center --heel-x 174` plus `--scale-mult` from the measurements; use `--modes feet,feet,... --feet-x 293` for frames 1 and 2 if the stance came out wider than the idle's (as the Rogue's did). Frames 3 to 6 are centred with their lowest point on the ground line.
"""
DEATH = block(
    OUT,
    "You get two reference images.\nThe FIRST attached image is a strip of 6 key poses of a fighter being hit, falling backwards and lying on the ground. Use it ONLY as a pose reference.\nThe SECOND attached image shows the character I want.",
    "TASK: redraw the 6 poses of the first image with the character of the second image. Each panel must keep the exact pose of the same frame in the first image: the same body angle, head tilt, facing, arm and leg positions, expression and camera (strict side view). "
    "Only the character changes. Output them as ONE sprite sheet: a grid of 3 columns x 2 rows, six equal square panels, read left to right, top row first. Panels 1, 2, 3 are on the top row and panels 4, 5, 6 on the bottom row, in the same order as the frames of the first image.",
    "CHARACTER: the exact character of the second image: " + DESC + ". Keep the same painted game-sprite style, thick dark outlines, colors, proportions and face. "
    "Ignore the outfit of the first image: no bare chest, no bandage wraps, no bare feet, no white background. His plate armour, pauldrons, vambraces, tabard, belt, trousers, knee plates, greaves and boots must be worn in every panel, "
    "also when he is falling and lying down; when he lies down the tabard falls over his thighs and stays inside the panel. Both hands are empty closed fists, bare, never gauntlets. No weapon of any kind.",
    "DIRECTION: while standing he faces RIGHT, and the blow throws him backwards toward the LEFT, so his head ends up on the left and his feet on the right, exactly like the first image.",
    "THE SIX FRAMES:\n"
    "1. Stunned. His ready stance (feet wide apart and planted, knees bent), chin raised and head tilted back so he looks up, fists clenched in front of him: the near fist at the middle of his chest, the far fist at belt height.\n"
    "2. The hit. The same stance, face in a pained grimace, teeth gritted, eyes squeezed shut, chest pushed out, fists clenched.\n"
    "3. Falling backwards. Body tilted back about 40 degrees from vertical, head at the upper left, feet at the lower right just at the ground, legs together and slightly bent, the near arm trailing down behind him on the left, the far arm flung out to the upper right, looking up. The tabard panels fly up and forward.\n"
    "4. Falling further. Body tilted about 60 degrees from vertical, head far to the left, legs to the lower right, the near arm hanging down on the left, the far arm stretched out to the right, almost horizontal.\n"
    "5. Landing. Lying on his back on the left with his head on the ground, the torso on the ground, knees bent and both legs up in the air (one leg raised high, the other bent out to the right), the far arm raised with a fist up, the near fist near his chest.\n"
    "6. Lying still. Flat on his back, head on the left, body horizontal, legs stretched out to the right and slightly bent at the knees, arms resting loosely at his sides, eyes closed, limp.",
    "SCALE AND POSITION (very important, one single scale in all six panels): his head, from the top of the hair to the chin, is only about 8% of the panel height in EVERY panel, including panels 1 and 2: do NOT enlarge the face in the close-up poses. "
    "Standing, his whole body from the top of the head to the soles of the boots is only about 52% of the panel height. In the tilted and falling panels (3 and 4) the whole body is about 52 to 57% of the panel height. "
    "The lying figure in panel 6 is about 68% of the panel width long and fits inside the panel with a margin. The floor is lower than half way: in every panel the lowest point of the figure rests on the same floor height, about 78% down the panel. "
    "The WHOLE body, from the top of the head to the soles of both boots, is visible in every panel, nothing is cropped, and nothing is cut flat at the floor line. Keep each figure horizontally centred in its panel like the first image. "
    "Keep the near arm in front of the body and the far arm behind it in every panel.",
    BG.format(margin=10, more=", motion lines, impact stars, blood").replace("Leave about 10% empty margin around the figure in each panel; the whole", "The whole"),
    FINAL)

# --------------------------------------------------------------------------------------------- DODGE
DODGE_HEADER = """CLERIC DODGE PROMPT (6 frames, 3 x 2). Written 2026-11-21 from the Rogue's dodge prompt. Works with Gemini or ChatGPT.

HOW TO USE
- Attach ONE image: Animations/Cleric/reference_image.png. Ask for a 3:2 image (ChatGPT: 1536 x 1024). Paste everything between the two lines of equals signs.
- Generate several and keep the best. If only some frames are bad, ask again for those poses only; I join the good frames (the mage's dodge needed her idle's first frame pasted over a bad frame 1).
- Save the sheet in inbox/ as cleric_dodge_sheet.png and tell me.
- What to look at: (1) the same man in all six panels (emerald hair, pointed ear, plate armour, cream tabard, no helmet, no cape); (2) panels 1 and 6 are the reference stance; the fists stay in their guard places in every panel (the near fist at the chest, the far fist at belt height); (3) panels 3 and 4 are in the air: both boots off the floor, about 15% of his height in panel 3 and about 6% in panel 4 (he is heavily armoured, so it is a short heavy hop, lower than the Rogue's); (4) the same size in every panel, and room above his head for the hop (the idle came out at 85% of the panel when 60% was asked, so the prompt asks for only 52% and for 25% empty space above the head); (5) both hands bare closed fists; (6) nothing touches a panel edge; (7) one image only.
- This is the same dodge as the warrior's, the mage's and the Rogue's: a quick hop up and back, in place; the page slides him back along a path file (`.placement.json`, the same hop-back path as theirs with a smaller lift, the strike lands on frame 3).
- Planned cut (default despill): `python source/tools/slice_airborne_sheet.py cleric_dodge_sheet.png Animations/Cleric/dodge/mailed_dodge_6frame_strip.png --cols 3 --rows 2 --grounded 1,2,5,6 --standing 1,6 --ref-panel 1 --height 408 --align feet --feet-x 293 --fit 1,6`. His idle's feet middle is 293.
"""
DODGE = block(
    OUT,
    GRID + " The six panels are the key poses of a \"dodge\": the character reacts to an incoming attack by quickly hopping up and back, lands, and returns to his ready stance.",
    CHAR,
    "VIEW: strict side view of the body and legs, he faces RIGHT in every panel, with the head turned a little toward the viewer in the same three-quarter view as in the reference. The attacker is off-screen to the right, so the hop goes up and slightly back toward the LEFT.",
    "NO ITEMS AND NO EFFECTS: no mace, no club, no wand, no sword, no shield, no orb, no book, no weapon of any kind, nothing in his hands. No glow, smoke, sparks, dust, motion lines, speed lines, afterimages or effects of any kind.",
    ARMOUR + " The hop is short and heavy.",
    "HANDS (in every panel): both hands are bare, tight CLOSED FISTS with nothing in them, never gloved. The fists stay in their guard places the whole time: the near fist at the middle of his chest, the far fist at belt height out in front of him, as in the reference; they are never raised to his chin.",
    ARMS,
    "SAME SCALE AND FLOOR (very important): the character is drawn at exactly the same size in all six panels, the same standing size as in the reference. Do not zoom in or out between panels. "
    "His head, from the top of the hair to the chin, is about 7.5% of the panel height, and the standing figure, from the top of the head to the soles of the boots, is only about 52% of the panel height. "
    "The floor is at the same height in every panel, about 80% down the panel, so that in panel 1 there is at least 25% of the panel height empty above his head: that room is for the hop. "
    "The hop goes mostly UP; he stays at about the same horizontal position in every panel (the hips do not travel across the panel, at most a small lean and drift to the left at the peak). The WHOLE body is visible in every panel, never cropped.",
    "THE SIX FRAMES:\n"
    "1. React. His ready stance exactly like the reference: knees bent, fists in their guard places, both feet planted on the floor. Eyes wide and focused on the enemy, the weight just beginning to shift onto the rear leg. The tabard hangs still.\n"
    "2. Coil. Both feet still on the floor, the knees bent deeper, the torso leaning back about 10 degrees, the weight on the rear leg, the front foot only on its toes, the fists still in guard.\n"
    "3. Peak of the hop. BOTH FEET OFF THE FLOOR by about 15% of his height, the knees tucked slightly, the torso leaning back about 15 degrees, the head back, the fists in guard, the eyes on the enemy. The front and back panels of the tabard lift up and forward.\n"
    "4. Coming down. Still in the air, the feet about 6% of his height above the floor, the legs extending down with the toes pointing toward the floor, the torso leaning back about 10 degrees, the fists still in guard. The tabard is settling.\n"
    "5. Landing. Both feet back on the floor, the knees deeply bent to absorb the heavy impact, the torso leaning slightly forward, the fists in guard, looking at the enemy. The tabard catches up.\n"
    "6. Recover. The same ready stance as the reference and as panel 1: knees bent, fists in their places, neutral determined face. The tabard hangs still.",
    BG.format(margin=10, more=""),
    FINAL)

# --------------------------------------------------------------------------------------------- RUN
RUN_HEADER = """CLERIC RUN PROMPT (6 different poses of ONE running step, 3 x 2). Written 2026-11-21 from the Rogue's run prompt (which worked on the first sheet).

WHY THIS FORM (docs/PROMPTS.md, "Run in place"): image generators cannot draw the leg swap of a second step; they repeat the first step, or turn the torso away from the camera. What worked for the warrior and the Rogue is to ask for SIX DIFFERENT poses of ONE step with the position of the boot on the floor in percent of the height, so that it slides steadily backward from panel to panel, plus a wide diagonal arm swing in three of the panels. The Rogue's strip then used the six poses plus the early and mid stance again (1 2 3 4 5 6 2 3, the user's idea) at 11 to 12 fps.

HOW TO USE
- Attach ONE image: Animations/Cleric/reference_image.png. Ask for a 3:2 image (ChatGPT: 1536 x 1024). Paste everything between the two lines of equals signs.
- Generate two or three sheets and keep the best panels from each. If he keeps the standing boot at the same place in several panels, or turns his back to the camera, the fallback is pose transfer: attach `Animations/Rogue/run/cloaked_run_6frame_strip.png` (or the Warrior's `Animations/Warrior/run/armored_run_5frame_strip.png`) FIRST (poses only) and his reference SECOND, and say "redraw the poses of the first image with the elven man of the second image, keep the poses, ignore the outfit of the first image".
- Save the sheets in inbox/ as cleric_run_sheet_1.png (and _2, _3) and tell me which panels you like, or let me choose.
- What to look at: (1) six DIFFERENT poses, not one pose repeated; (2) the boot on the floor slides backward from panel 1 to 5 (about +22, +12, +2, -8, -25% of his height from the hips); (3) the torso faces the camera side-on in every panel (not turned away) and the near pauldron stays visible; (4) panels 1, 2 and 5 have the wide diagonal arm swing, one fist forward and up, the other back and down; (5) the same man and the same size in every panel (emerald hair, plate armour, cream tabard, no helmet, no cape), nothing cropped, nothing touching a panel edge; (6) bare closed fists (no gauntlets); (7) one image only.
- Building the strip (not run yet): `python source/tools/make_run_strip.py --sheet s1=inbox/cleric_run_sheet_1.png --cols 3 --native --scale s1=<head match> --anchor-x s1=<mean head x> --anchor-y s1=470 --head-x 297 --frames s1:1,s1:2,s1:3,s1:4,s1:5,s1:6 --out Animations/Cleric/run/mailed_run_6frame_strip.png` (his idle's head x is 297, the middle of his head columns 264 to 330 in frame 1; the head scale comes from a template match of his idle's head: a run is drawn with a bigger head and bent knees, so he ends up about 86 to 91% of the idle's height; the script's default despill is safe for him). File it, check it with `check_strip.py`, a `.placement.json` with only the fps (about 11), rebuild the page, then `BG_STEP.cleric` (now 12, a guess) is tuned by eye, and the hand marks are made later (the user: the mace behind, the shield in front, both visible while he runs).
"""
RUN = block(
    OUT,
    GRID + " The six panels are six DIFFERENT key poses of ONE running step of a character who runs on the spot, like on a treadmill, in strict side view facing RIGHT. The panels are in time order, and panel 6 flows straight on into panel 1 again. No two panels may look alike.",
    CHAR,
    "NO ITEMS AND NO EFFECTS: no mace, no club, no wand, no sword, no shield, no orb, no book, no weapon of any kind. Both hands are empty, tight closed fists (never open, never splayed, never gloved) in every panel. No glow, smoke, dust, sparks or effects of any kind.",
    ARMOUR + " In a run the armour stays rigid; only the front and back panels of the tabard swing and the tips of his hair flutter a little.",
    "RUNS ON THE SPOT: he does NOT travel across the panel. The hips stay over the same spot, the horizontal center of the panel, in all six panels; only the legs and arms reach forward and back. "
    "The boot that is on the floor slides steadily BACKWARD under the body from panel to panel while the other leg swings forward, like running on a treadmill.",
    "RUNNING POSTURE (the same in every panel): a brisk, powerful, determined run, heavy but fast. The torso leans forward about 12 degrees, the head is up and the eyes look forward to the right, a determined face with the mouth closed. "
    "Both legs are drawn in strict side view; where they overlap, the leg on the viewer's side is in front. The torso faces the camera side-on in every panel: never turned away, the back of the collar never shows, and the near pauldron stays visible on the viewer's side. "
    "The front panel of the tabard lifts and the back panel streams back behind his legs with a different ripple in every panel; the tips of his hair stream back too; the tabard always stays fully inside the panel.",
    "SAME SCALE AND FLOOR: draw him at exactly the same size in all six panels, about 55% of the panel height from the top of the head to the soles of the boots, with the head (from the top of the hair to the chin) about 8% of the panel height. "
    "The floor is an invisible line about 88% down the panel, and the whole body is visible in every panel, never cropped. The whole body moves up and down only a little (about 4% of the height in all): a smooth running stride, not jumping.",
    "HOW TO READ THE NUMBERS: H is his height from the top of the head to the soles of the boots. Distances are measured from the hips (the belt): + is forward (to the right), - is behind (to the left).",
    "THE BOOT THAT STAYS ON THE FLOOR MOVES STEADILY BACKWARD FROM PANEL TO PANEL: +22%, +12%, +2%, -8% and -25% of H in panels 1 to 5. This sliding is the most important thing of the sheet: do not draw the standing boot at the same place in two panels.",
    "THE ARMS SWING AS A WIDE DIAGONAL in panels 1, 2 and 5: one arm is swung forward and UP and the other arm back and DOWN, so that the line from the back fist through the shoulders to the front fist rises clearly from the lower left to the upper right. In panels 3, 4 and 6 the arms come close to the body.",
    "THE SIX FRAMES:\n"
    "1. Contact. The FRONT boot: 22% of H ahead of the hips, the heel just touching the floor, the knee almost straight. The BACK boot: 22% of H behind the hips, only its toe on the floor, the knee slightly bent. ARMS, a strong diagonal: the front arm swung forward and UP with the elbow bent about 80 degrees and the fist at chin height in front of the chest; the back arm swung back and DOWN with the elbow almost straight (about 160 degrees) and the fist behind the hip at belt level. Body at middle height. The back panel of the tabard streams back, low.\n"
    "2. Early stance. The FRONT boot FLAT on the floor 12% of H ahead of the hips, the knee bent about 25 degrees. The BACK leg is lifted: the knee bent about 90 degrees, the heel kicked up, the boot 15% of H behind the hips and 20% of H above the floor. ARMS, still a diagonal but a little smaller: the front fist at chest height, the back fist at hip level behind. The body is sinking.\n"
    "3. Mid stance, the lowest point of the body. The standing boot FLAT on the floor only 2% of H ahead of the hips, almost directly under them, the knee bent about 35 degrees. The other leg is tucked behind the standing one: the knee bent about 100 degrees, the boot 10% of H behind the hips and 18% of H above the floor, partly hidden behind the standing leg. ARMS close to the body: both fists near the belt, the elbows bent about 90 degrees. The tabard sags a little.\n"
    "4. Passing. The standing leg nearly straight, its boot FLAT on the floor 8% of H BEHIND the hips with the heel just starting to lift. The other leg swings through: the thigh forward and a little up, the knee bent about 80 degrees, its boot tucked just behind the standing knee, 15% of H above the floor, NOT touching it. ARMS at the waist, the fists crossing each other. The body is rising. The tabard lifts.\n"
    "5. Push-off and knee drive. The standing leg is straight and pushing off: only its toe on the floor, 25% of H behind the hips. The other knee is driven forward and up to about hip height, its boot hanging 12% of H above the floor and 14% of H ahead of the hips. ARMS, a strong diagonal again: one fist forward and UP at chin height in front of the chest, the other back and DOWN behind the hip with the elbow almost straight. The back panel of the tabard streams out straight behind him.\n"
    "6. Flight. BOTH boots are off the floor, but only a little: the soles about 5% of H above the floor line. One boot trails 24% of H behind the hips, low, toes pointing down; the other boot is 20% of H ahead of the hips with the knee lifted only about two thirds of the way up to hip height. ARMS in between: both elbows bent about 90 degrees, one fist at chest height in front, the other at the waist, about to swing wide again. The body is at its highest point, only about 4% of H higher than in panel 1.",
    "CHECK BEFORE YOU FINISH: the six panels show six different poses; the standing boot is at a different place in panels 1 to 5, moving steadily backward; panels 1, 2 and 5 show the wide diagonal of the arms; in panel 3 the standing boot is almost under the hips and in panel 4 it is behind them; the torso faces the camera side-on in every panel; the figures have the same size and the same floor line in all panels, stay over the same spot, and the tabard never touches a panel edge.",
    BG.format(margin=12, more=", motion lines, speed lines, afterimages"),
    FINAL)

# --------------------------------------------------------------------------------------------- BLOCK
BLOCK_HEADER = """CLERIC BLOCK PROMPT (6 frames, 3 x 2). Written 2026-11-21 from the Warrior's Block prompt (Animations/Warrior/block/source/block_prompt.txt: it came out right on the first try) and docs/BLOCK.md. Works with ChatGPT first (it keeps size and spacing, which Gemini drifts on), Gemini as a second try.

WHAT IT IS. A block is a REACTION, like the Dodge: when a hit lands it may be blocked, and this animation plays for about half a second INSTEAD of the Hit animation. The guard goes up BEFORE the blow lands (frame 3), the blow lands on frame 4 (the page puts the glass of the Mage's Barrier there, a short half circle in front of him, and cuts the damage by 20%, no critical hit), the guard eases (frame 5) and he is back in his guard stance (frame 6). He stays on the same spot: only the arms, the knees and the upper body move. The Cleric has +10 Block Rate as a class bonus, and the Templar is the shield-bearer, so his block is a SHIELD guard.

THE ITEMS ARE A LAYER (as in every sheet): his hands are drawn as empty, tight fists and the page draws the items afterwards on the hand marks the user makes in the hand tool (the SHIELD in the NEAR hand = the off hand, in front of the body; the MACE in the FAR hand = the main hand). So the fists must be where the items belong: in frames 3 and 4 the NEAR fist is raised in front of his face (the shield's grip; the shield will cover his face and chest) and the FAR fist is close beside it at chest height with a clear gap (the mace can stand up beside the shield). Nothing else is drawn in front of the fists.

HOW TO USE (the ready-to-use folder is Cleric_animation_kit/05_block)
- Attach ONE image: Animations/Cleric/reference_image.png (the armoured look; its stance is the guard stance of frames 1 and 6). Ask for a landscape 3:2 image (ChatGPT: 1536 x 1024). Paste everything between the two lines of equals signs.
- Generate several and keep the best. Save the sheet in inbox/ as cleric_block_sheet.png and tell me.
- What to look at: (1) frames 3 and 4: the near fist is raised in front of the FACE, the far fist beside it at chest height, both clenched, bare and empty, clear of each other by about one fist's width (room for the mace beside the shield); (2) frame 4 shows the blow: the upper body shoved back a little to the left (he is heavy: less than the Warrior), the rear foot on the same spot, the face gritted, the front foot sliding back a little; (3) frames 1 and 6 are the reference stance (same size, same feet); (4) the same man at the same size in all six panels, the same floor line, the bottom row NOT bigger than the top row; (5) the armour stays on in every panel, bare hands (no gauntlets), no helmet, no cape; (6) NO mace, NO shield, NO glass, NO impact stars, NO dust, NO motion lines; (7) nothing touches a panel edge (the raised arm and the pauldron make him wider); (8) no GIF and no extra images.
- Replies if it goes wrong (paste in the same chat). If it draws a mace, a sword or a shield: "Redo it. NO weapon and NO shield: both hands are empty, tight fists." If it draws an impact star, dust, a glow, a barrier or motion lines: "Redo it. NO effects of any kind: only the character, drawn crisp, on the flat magenta." If frames 3 and 4 look like frame 1: "Redo it. In frames 3 and 4 the NEAR fist must be raised in front of the FACE, level with the eyes, and the far fist beside it at chest height: the pose must be clearly different from the guard stance of frame 1." If the figure changes size or the bottom row is bigger: "Redo it. The character is exactly the same size in all six panels, the bottom row NOT bigger than the top row, the same floor line in every panel." If a foot slides across the panel: "Redo it. The REAR foot (the left foot) stays on the same spot in every panel; only the front foot may slide back a little in frame 4." If he changes outfit, gets a helmet or gauntlets: "Redo it. The character in all panels is the one in the attached image: the same armour, hair, face and proportions, bare hands, no helmet, nothing redesigned." If a part touches a panel edge: "Redo it. The whole character is at least 12% of the panel away from every panel edge." If the background is not flat magenta or the character has pink on it: "Redo it. One flat pure magenta (#FF00FF) background, nothing pink or magenta on the character." If it draws more or fewer panels: "Redo it. EXACTLY six panels, 3 columns by 2 rows."
- Planned cut (the Warrior's recipe, `Animations/Warrior/block/source/make_block_strip.py`): `python source/tools/slice_keypose_sheet.py cleric_block_sheet.png Animations/Cleric/block/mailed_block_6frame_strip.png --cols 3 --rows 2 --height 408 --scale-from median --modes heel --heel-x 174 --fit 1,6`; then frames 1 and 6 are REPLACED by the idle's frame 1 (so the pack starts and ends on the idle, no pop: the Cleric's hit sheet matched the idle at 0.84 only); `even_heads.py --char cleric` after the cut (his head tends to come out 3 to 10% bigger in action sheets); a `mailed_block_6frame_strip.placement.json` (fps 12, blockFrame 4: the frame on screen when the blow lands, like the dodge's evadeFrame). His idle: rear heel 173 to 174, front toe 411 to 412, feet middle 293. The page needs no new wiring: `build.py` maps the folder `block` to the slot `block`, and `charBlockSpec` plays the block pack of the hero slot; the glass comes from the Barrier's own drawing. The user then marks the shield and the mace on frames 2 to 5.
"""
BLOCK = block(
    OUT,
    GRID + " It is a \"block\" sequence: the character sees a blow coming, drops into a guard with his shield arm raised in front of his face, takes the blow on the guard (it shoves him back a little), holds, and returns to his guard stance. "
    "Six key poses of a sprite sheet, every panel one still pose, drawn crisp and clean; the motion is in the DIFFERENCE between the panels, never drawn inside one.",
    CHAR,
    "VIEW: strict side view of the body and legs, he faces RIGHT in every panel, with the head turned a little toward the viewer in the same three-quarter view as in the reference. The attacker is off-screen to the right, so the blow comes from the front and shoves his upper body back toward the LEFT.",
    "NO WEAPON, NO SHIELD: both hands are empty, tight clenched fists (never open, never gloved). No mace, no club, no wand, no sword, no shield, no orb, no book, no glass, no barrier, no light.",
    ARMOUR + " He is heavy: the blow moves him only a little.",
    "SAME SCALE AND FLOOR (very important): draw him at exactly the same size in all six panels, the same standing size as in the reference: the standing figure, from the top of the head to the soles of the boots, is only about 55% of the panel height, and his head, from the top of the hair to the chin, is about 8% of the panel height. "
    "The floor is at about 82% down the panel, the same in every panel, with at least 12% empty margin on every side (the raised arm and the pauldron make him wider in the guard). The bottom row must NOT be drawn bigger than the top row. Do not zoom in or out between panels. "
    "The REAR foot (the left foot, the one farther from the enemy) stays on the ground at the same spot in every panel, as if on an invisible floor line; the figure does not travel across the panel. Keep the figure horizontally centred like the reference. The WHOLE body is visible in every panel, never cropped.",
    ARMS,
    "THE SIX FRAMES:\n"
    "1. Ready. Exactly the guard stance of the reference image: both feet planted, the near fist at the middle of his chest, the far fist at belt height out in front of him, neutral determined face, eyes on the enemy.\n"
    "2. Brace. He has seen the blow coming. Knees bent, weight shifted onto the rear leg, torso leaning forward about 6 degrees, the NEAR fist rising from his chest to just in front of his chin and the near shoulder and pauldron lifting, the FAR fist drawn in to chest height just ahead of the torso. Eyes narrowed and locked on the enemy.\n"
    "3. Guard up. The guard is set. The NEAR forearm (in its steel vambrace) is raised almost vertical in front of his face and upper chest, the elbow plate forward and the near pauldron lifted beside his cheek, the NEAR fist at eye level about one head-width in front of his face; the FAR fist right beside it at chest height, about one fist's width away from the near fist (a clear gap between them, they do not touch or overlap); both elbows tucked in and bent. "
    "Knees bent about 25 degrees, torso leaning forward about 8 degrees, rear leg braced hard, front foot planted flat, head tucked down behind the raised arm so that only the eyes and the top of the face show above the near fist. Jaw set, eyes narrowed.\n"
    "4. THE BLOW. The same guard, but the blow has just landed on it: the whole upper body is shoved back toward the left (the shoulders about 5% of the panel width further left than in frame 3: he is heavy, so it is a small shove), the arms pressed in and braced against the force, the near forearm and the far fist still in the same raised guard with the same gap between them, "
    "knees bent deeply (about 35 degrees), the front foot sliding back a little along the floor, the rear foot unmoved, head ducked, teeth gritted, eyes squeezed narrow. The front and back panels of the tabard swing forward past his legs.\n"
    "5. Hold. The force is spent: he is pushing forward again, torso coming back up to the frame 3 lean, the guard still raised but starting to ease (the near fist a little lower, level with his nose), the front foot planted again, eyes open and glaring at the enemy. The tabard swings back.\n"
    "6. Back to guard. The same guard stance as the reference and as frame 1: the near fist at the middle of his chest, the far fist at belt height out in front, neutral determined face. This is the pose just before frame 1 and just before the idle. The tabard hangs still.",
    BG.format(margin=12, more=", motion lines, speed lines, impact stars, sparks, afterimages") + " NO GRID LINES, NO BORDERS and no lines between or around the panels. The game adds the impact later.",
    "FINAL REMINDER: ONE single static image only. Six equal panels, 3 columns by 2 rows. The same man at the same size in every panel, the rear foot on the same spot. Frames 3 and 4: the near fist raised in front of the FACE, the far fist beside it at chest height, a clear gap between the two fists; frame 4 shoved back a little to the left by the blow. "
    "Frames 1 and 6: the guard stance of the reference. Empty bare fists: NO weapon, NO shield, NO glass, NO effects. At least 12% margin on every side. Flat pure magenta background.")

ANIMS = [
    # folder, kit folder, header, body, attachments [(src, kit name)], sheet name in the inbox, what the kit's read-me says
    ("hit", "01_hit", HIT_HEADER, HIT, [(REF, "1_attach_this_image.png")], "cleric_hit_sheet.png"),
    ("death", "02_death", DEATH_HEADER, DEATH, [(DEATH_POSES, "1_attach_this_FIRST.png"), (REF, "2_attach_this_SECOND.png")], "cleric_death_sheet.png"),
    ("dodge", "03_dodge", DODGE_HEADER, DODGE, [(REF, "1_attach_this_image.png")], "cleric_dodge_sheet.png"),
    ("run", "04_run", RUN_HEADER, RUN, [(REF, "1_attach_this_image.png")], "cleric_run_sheet_1.png"),
    ("block", "05_block", BLOCK_HEADER, BLOCK, [(REF, "1_attach_this_image.png")], "cleric_block_sheet.png"),
]


def check_text(header):
    out = []
    for line in header.split("\n"):
        if line.startswith("- What to look at:") or line.startswith("- Replies if it goes wrong"):
            out.append(line[2:])
    return "\n\n".join(out)


def main():
    KIT.mkdir(exist_ok=True)
    for folder, kitname, header, body, attach, sheet in ANIMS:
        src_dir = CLERIC / folder / "source"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / f"{folder}_prompt.txt").write_text(header + "\n" + BAR + "\n" + body.rstrip("\n") + "\n" + BAR + "\n", encoding="utf-8", newline="\n")
        kd = KIT / kitname
        kd.mkdir(exist_ok=True)
        for src, name in attach:
            shutil.copy(src, kd / name)
        n_att = len(attach)
        (kd / f"{n_att + 1}_paste_this_prompt.txt").write_text(body, encoding="utf-8", newline="\n")
        steps = ["1. Start a NEW chat in Gemini or ChatGPT (ChatGPT usually keeps sizes better)."]
        if n_att == 1:
            steps.append("2. Attach 1_attach_this_image.png (the only image) and ask for a 3:2 image (a wide sheet, 3 columns x 2 rows).")
        else:
            steps.append("2. Attach 1_attach_this_FIRST.png (the pose strip: poses only) FIRST and 2_attach_this_SECOND.png (the Cleric) SECOND. The order matters. Ask for a 3:2 image.")
        steps += [f"3. Paste the whole text of {n_att + 1}_paste_this_prompt.txt.",
                  "4. Generate 2 or 3 and keep the best. If the generator says it is out of image capacity, wait; do not shorten the prompt.",
                  f"5. Save the sheet as inbox/{sheet} and tell me. I cut it into a strip, check it against his idle, and put it in the test page."]
        extra = ""
        if folder == "death":
            extra = ("\nIf the result copies the old outfit (bare chest, bandages, bare feet), reply in the same chat: \"Redo it. The character in all panels must be the elven man from the second image, wearing his silver-steel plate armour with the big pauldrons, "
                     "his cream tabard with the gold cross, his dark-brown belt, trousers and boots with the steel knee plates and greaves. Do not copy any clothing from the first image.\"\n")
        if folder == "run":
            extra = "\nFor the run, generate two or three sheets (save them as cleric_run_sheet_1.png, _2.png, _3.png): I pick the best panels from each, as for the Warrior.\n"
        (kd / f"{n_att + 2}_what_to_check.txt").write_text(
            f"CLERIC {folder.upper()}: what to do and what to check\n\n" + "\n".join(steps) + "\n\n" + check_text(header) + "\n" + extra +
            "\nIf ONE thing is wrong tell me which; I will give you a one-line fix, or I join the good frames of several sheets.\n", encoding="utf-8", newline="\n")
    (KIT / "0_read_me_first.txt").write_text(
        """CLERIC: HIT, DEATH, DODGE, RUN AND BLOCK PROMPTS (2026-11-21)

Five folders, one per animation. Each has the picture(s) to attach, the prompt to paste, and what to check. 01_hit, 02_death, 03_dodge and 04_run are DONE (the user's sheets were cut and are in the test page); 05_block is the new one. You can generate them in any order and one by one; tell me when a sheet is in the inbox.

The prompts are the Rogue's four prompts (they all worked first time with ChatGPT) with the Cleric's armoured look and these changes:
- HEAVY ARMOUR: the hit is a heavy rock, not a flail; the dodge is a short heavy hop; the armour stays on and rigid in every panel; no helmet, no gauntlets (his hands stay bare), no cape.
- His guard stance replaces her low fists: the near fist at the middle of his chest, the far fist at belt height out in front of him.
- The tabard's front and back panels (and the hair tips) are the secondary motion, in place of her cloak and scarf.
- BLOCK (05_block): a SHIELD guard (the Cleric has +10 Block Rate, the Templar is the shield-bearer): the near fist is raised in front of his face where the shield will be drawn, the far fist beside it at chest height for the mace; the blow shoves him back only a little (he is heavy); the guard goes up BEFORE the blow lands, the blow is frame 4, like the Warrior's.
- Sizes: his head is smaller next to the armour, so the head is asked at about 8% of the panel, and the standing figure at 52 to 55% (ChatGPT drew his idle at 85% when 60% was asked; the cutters rescale, but there must be room for the recoil, the hop and the stride).

Save the sheets as inbox/cleric_hit_sheet.png, cleric_death_sheet.png, cleric_dodge_sheet.png, cleric_run_sheet_1.png (more run sheets as _2, _3) and inbox/cleric_block_sheet.png. Each takes a new chat. The cut commands, his numbers and the planned strip names are in the header of each master prompt (Animations/Cleric/<animation>/source/<animation>_prompt.txt).
The sources: this folder is built by Animations/Cleric/source/make_cleric_prompts.py from the character paragraph Animations/Cleric/source/cleric_description.txt.
""", encoding="utf-8", newline="\n")
    print("done:", [a[0] for a in ANIMS])


if __name__ == "__main__":
    main()
