# Playbook: making animations and characters

How the warrior was made, written so it can be repeated for the next character. The prompts are in `PROMPTS.md`, the file formats in `FORMATS.md`, the test page internals in `DEV_NOTES.md`.

## The loop for one animation

1. **Plan it.** Frames, grid, fps, and whether it is grounded, airborne or lying (this picks the cut command). Hit, death and idle stay in place; attack and dodge may travel and get a path.
2. **Prompt Gemini** (`PROMPTS.md`). Attach the character reference, ask for a 3:2 sheet (6 frames) or the matching grid, flat magenta background. Generate several and keep the best.
3. **Drop the sheet into `inbox/`**, cut it into a strip (below), and check it with `check_strip.py`.
4. **File it:** strip to `Animations/<Character>/<animation>/armored_<name>_<N>frame_strip.png` (idle: `armored_idle_strip.png`), the sheet it came from to that folder's `source/`.
5. **Mark the hands** in `hand-anchor-tool.html` and drop the exported json in `inbox/`; file it as `<strip name>.hand-anchors.json` next to the strip.
6. **Path (only if it travels):** set it in the test page, "Download .json", file it as `<strip name>.placement.json`.
7. **Rebuild the test page** (`python source/tools/build.py`, copy `source/dist/warrior-vs-goblin-test.html` over the one in the project folder) and look at it moving.
8. **Skill effect (only if it is a skill):** built in code in the test page, tuned by eye (`DEV_NOTES.md`).

## Generating with Gemini: what works

Image generators draw the animation as a grid of panels on a flat magenta (#FF00FF) background. They ignore requested pixel sizes (only the aspect ratio is respected), so the scripts do the scaling and alignment. A grid gives more pixels per frame than one long row.

What worked well:
- Attach a clean character reference first (the idle strip). Describe the character in words too, and say "do not redesign anything".
- 3 columns x 2 rows for 6 frames (ask for 3:2), 4 x 2 for 8 frames. Square panels, order left to right then top row first.
- Say what must be identical in every panel: the same size, the floor at the same height, the rear foot planted (for in-place moves), the near arm in front of the body and the far arm behind it.
- Pose lists per frame, with the first and last frame of a reaction equal to the idle guard stance (so it joins the idle cleanly).
- Ask for margin around the figure and "never touches a panel edge": the cutter keeps the largest blob in each panel and cuts at equal panel boundaries.
- For an animation that already exists on another character, attach the old strip as a pose reference (first image) and the new character as the second image, and say "use the first image only for poses" (this is how the death was made).
- No weapon in the hands, no effects, no shadows, no text, no motion lines, no blood.

What it cannot do (plan around it):
- Keep the near and far arm identity between frames. The hand tool's per-frame front or behind mark absorbs this.
- Hold exact pixel sizes or a consistent ground line between the two rows of a grid: the figure size drifts by 2 to 4 percent. The cutters shrink or grow each frame (`--fit`, `--scale-from`) and find each row's ground from the grounded frames.
- Draw outlines without a faint purple glow from the magenta. The cutters' despill options remove it.
- Follow exact horizontal positions inside a panel. In-place moves are re-centred by the cutter (`--align feet` or `heel`).

After each generation check: the same character in every panel, no weapon, first and last frame upright where they should be, floor contact, nobody crossing a panel edge. Regenerate rather than repair.

## Cutting a sheet into a strip

Needs `pip install pillow numpy scipy`. Run from `source/tools/`. Both scripts print what they did (`clipped pixels` should be 0). First measure the idle (below) so you know the numbers to use.

**Numbers from the idle.** `python check_strip.py <idle strip>` prints, per frame, the height, the rear heel x, the front toe x and the middle of the feet. The warrior's are heel 160, toe 426, feet middle 293, height 408. A new character should use the same ground line (42 px above the bottom) and a similar standing height, and gets its own heel, toe and feet-middle numbers from its idle. In the commands below, replace 160 / 426 / 293 with the idle's own numbers.

| Animation | Script and command | Why these options |
|---|---|---|
| **Idle** (grounded loop) | `python slice_keypose_sheet.py idle_sheet.png idle_strip.png --cols 3 --rows 2 --height 408 --scale-from median --modes heel --heel-x 160` | Feet planted by the rear heel; the shared scale is the median figure height |
| **Hit** (grounded, ends in the idle stance) | `python slice_keypose_sheet.py hit_sheet.png hit_strip.png --cols 3 --rows 2 --height 408 --scale-from median --modes heel --heel-x 160 --fit 1,6 --despill-band 10 --despill-thr 4` | `--fit 1,6` scales the two guide-stance frames to exactly 408 px so the hit joins the idle without a size jump |
| **Death** (stands, falls, lies) | `python slice_keypose_sheet.py death_sheet.png death_strip.png --cols 3 --rows 2 --height 408 --scale-from panel1 --modes heel,heel,center,center,center,center --heel-x 160 --despill-band 10 --despill-thr 4` | The scale comes from frame 1 only (the lying frames are much shorter than the standing ones); frames 3 to 6 are centred with their lowest point on the ground line |
| **Ground attack** (front foot planted) | `python slice_keypose_sheet.py attack_sheet.png attack_strip.png --cols 4 --rows 2 --height 408 --modes toe --toe-x 426` | The front foot stays where the idle's front toe is |
| **Jump attack** (feet leave the ground) | `python slice_airborne_sheet.py jump_sheet.png jump_strip.png --cols 4 --rows 2 --grounded 1,2,3,7,8 --standing 1,8 --ref-panel 1 --height 408 --toe-x 426` | `--grounded` lists the frames with feet on the floor (each row's ground is found from them); airborne frames keep their real height. The warrior's jump was cut with `--toe-x 336` by mistake, see the README's known issues |
| **Dodge or hop in place** | `python slice_airborne_sheet.py dodge_sheet.png dodge_strip.png --cols 3 --rows 2 --grounded 1,2,5,6 --standing 1,6 --ref-panel 1 --height 408 --align feet --feet-x 293 --despill-band 10 --despill-thr 4` | `--align feet` puts the middle of each grounded frame's feet on the idle's and lets airborne frames follow smoothly, which removes the generator's sideways wobble |

Options worth knowing: `--despill-band N --despill-thr T` (how far from the outline and how strictly leftover magenta is pulled out; the defaults 3 and 12 are enough for most sheets, 10 and 4 clean a purple glow), `--fit` (panels scaled individually to `--height`), `--scale-from panel1|median`, `--scale-mult 1,1,1.17,0.82,...` (per-panel size correction for the keypose cutter: Gemini sometimes draws some panels of a sheet bigger or smaller than the rest, most often the emotional close-ups and the lying poses; measure the face and the boots in a first cut, compare with the idle's, and give the inverse ratios. The mage's death needed 1.17 for frame 3 and 0.8 for frames 4 and 5), `--fit 1,6` and `--scale-mult` (the airborne cutter has both too: `--fit` scales the standing frames individually to exactly `--height`, so a hop joins the idle without a size jump; if a sheet's first frame is drawn differently from the idle, paste the idle's frame 1 over it, the ground lines match), `--lift-scale` (bakes extra jump height into the art; prefer a path, which keeps the art as pure poses). The output height of the airborne script grows to fit the highest frame (512 or 640 so far). Monsters with loose crisp effects (a slime's embers and smoke), added 2026-11-07, defaults unchanged: `--keep-near 0.25` keeps detached pieces within that share of the body's height (the old cutter kept only the biggest piece and dropped them; `--min-piece` ignores dust), `--base-width 350` sizes the shared scale by the WIDTH OF THE BASE (the widest row in the lowest `--base-band` 22% of the body) instead of the figure's height, so flames and smoke of different heights cannot resize the body, and prints every panel's base width (`--fit-base` scales chosen panels one by one). Tested on a synthetic six-panel sheet (one panel with its flames cut off kept the same base width and body size). `slice_airborne_sheet.py` has no such options yet: add them when the slime's dodge hop is cut.

**Too much movement?** An idle that bobs or sways more than you like can be calmed down without a new generation: `python damp_motion.py in_strip.png out_strip.png --keep 0.5` measures how far each part moved against frame 1 (optical flow) and warps each frame back so only that share is left (0.5 = half; `--ref` picks the rest frame). Nothing is blended, so lines stay sharp; the feet and ground line stay put. It prints the movement before and after per frame; run `check_strip.py` after it. The mage's idle was cut with it: her sheet bobbed the whole upper body 10 px (head 7 px up to 3 px down), and `--keep 0.5` gave a range of about 5 px. Keep the strip before damping, so another value can be tried.

**Check it:** `python check_strip.py <strip> --out check.png` prints the measures per frame and writes a picture of the strip under the idle with guide lines (red heel 160, yellow feet middle, green toe, blue ground). Good: ground line 42 px from the bottom, standing frames about 408 px tall, the frames that should match the idle (first and last of a hit or dodge) with the same heel and toe, "fringe" in the low hundreds or less, and no WARNING lines.

## Marking the hands (`hand-anchor-tool.html`)

The weapon is not in the art; each frame says where each hand holds an item. The tool keeps its work in the browser (so closing it is safe).

**Draft marks without clicking:** when the hands are bare skin (no gloves), `python source/tools/make_mage_marks.py` finds both hands in every frame (skin colour, the face is the biggest region) and writes draft marks into each animation's `source/` folder, and `preview_marks.py` draws the items on the frames to check them. It is written for the mage (an orb floating above the far hand, a staff in the near fist): copy it for another character and change the item settings and the angle table. A picture for a new item comes from `cut_item.py` (it removes the flat grey background of a generated item picture, keeps what is inside the outline, `--rotate 180` when the picture points down, items must point up). Then load the json in the tool and fix what looks off.

1. Name the character after its folder ("Warrior"). Pick the item of the far arm (the main hand: Sword, Shield, Staff or Orb) next to the name. In step 2 pick what the near arm (the off hand) carries for new animations (the same items or Nothing; the mage: Orb on the far arm, Staff on the near arm), then "Add animations from images" with the strips (the frame count is read from the width).
2. In step 3, pick the Far arm (the main hand, the character's left; the button shows its item) or the Near arm (the off hand, the right). Click the hand on the frame, drag toward where the item's top should point. New marks follow the house rule: main-hand item behind the body, off-hand item in front. Keys: arrows (frames), Q E (turn 3 degrees, Shift 1), W A S D (nudge), T (switch hand), F (front or behind), H (hide on this frame), Z X (narrower or wider), C (copy the previous frame), 1 to 9 (jump to an animation).
3. Mark the key frames (every 2 to 4 frames) and press "Fill unmarked frames in between"; fix the odd ones.
4. The item box beside the picture holds Length (a share of the frame width, so the item is the same size in every animation), Grip point, "Draw the hand over this item when it is in front" and Hand size. The hand drawn over the grip is the hand's own skin-coloured pixels near the mark, so keep the mark on or next to the fist.
5. Export with "Save this animation" (one animation, `<character>_<animation>.json`) and drop it in `inbox/`. Rename it to `<strip name>.hand-anchors.json` when filing.

The sample pictures in the tool are a sword and a shield. "Other picture" swaps the picture for the current session only (it is not saved). For a character with another weapon (a staff) the real fix is per-character item pictures in the tool and the page (`DEV_NOTES.md`).

## Paths and timing (only for animations that travel)

In the test page, the section "Frame positions" right under the stage controls (since 2026-11-13; it used to be folded away in the developer tools; the Thunderclap Guillotine's skill panel has a button that opens it), panel "Frame paths": pick "Attack pack" or "Dodge pack" under "Path for", tick "Edit on stage", pick a frame with the numbers, drag it (arrow keys nudge 1 px, with Shift 10 px; `,` and `.` change frame) or type X and Lift. "Fill line" and "Fill arc" fill a range. "Download .json" saves `<strip name>.placement.json`. The attack's x is a share of the distance to the target, the dodge's x is in character widths (format in `FORMATS.md`). The hit frame (attack) and the evade frame (dodge) mark the moment of impact.

## A run animation (in place, one stride of two steps)

Prompt and the lessons in `PROMPTS.md` ("Run in place"): Gemini repeats one step instead of drawing the swapped second step, so ask for one clean step (contact, down, passing, push-off with the knee drive, optionally a flight frame), keep the frames whose torso still faces the camera, and put them in the order of where the planted boot is (it must slide steadily backward). Build the strip with `source/tools/make_run_strip.py` (its docstring has the command; it cuts each panel with the project's keying and despill, `--despill-band 10 --despill-thr 4`), which scales by the HEAD (template-match the idle's head: the generator draws a run with a bigger head and bent knees, so the figure ends up about 86% of the idle's height), map the panel's floor to the cell's ground line (470) and the head to the idle's head x (288), file it as `Animations/<Character>/run/<prefix>_run_<N>frame_strip.png` and check it with `check_strip.py`. No path, no `.placement.json`; the fps (8) is the page's Run fps box. Draft hand marks: add the animation to `make_mage_marks.py` (`ANIMS`, `OVERRIDE_FAR` for forward fists the colour rule misses) and run it, preview with `preview_marks.py`, then refine in the tool.

## A cast animation for a mage (one for all her skills)

Prompt in `PROMPTS.md`. Cut it like the hit (`slice_keypose_sheet.py --cols 4 --rows 2 --height 406 --scale-from median --modes heel --heel-x 230 --fit 1,8 ...`), check the sizes (`--scale-mult`), file it as `Animations/Mage/cast/robed_cast_8frame_strip.png`, mark both hands in the hand tool (the staff pointing at the enemy on the release frame, the orb above the open hand), and give it a `.placement.json` with all x and y 0, fps 12 and hitFrame 5. Projectile skills are code: the page's skill panel is the model (Firebolt and Ice Shard share the cast, the sliders and the select; `docs/DEV_NOTES.md` says what a third skill needs).

## Troubleshooting

| What you see | What to do |
|---|---|
| Purple or pink edge on the character | Cut again with `--despill-band 10 --despill-thr 4` |
| Hair, scarf or trim of a RED character (burgundy, crimson) turns black or dark at the outline | The strict despill (`--despill-band 10 --despill-thr 4`) reads that red as magenta and darkens it (the Rogue's bob went half black). Cut with the DEFAULT despill (leave both options out; `make_run_strip.py` has the strict values as ITS defaults, so give it `--despill-band 3 --despill-thr 12`), then look at the frame on white and on a dark background. `check_strip.py`'s "fringe" number counts red pixels too, so it is useless for such a character (hers is 22000): judge the edge by eye |
| The figure changes size between frames | Use `--fit` for the standing frames, or `--scale-from median` / `panel1` as in the table |
| An in-place move wobbles sideways | Cut with `--align feet` (airborne script) or `--modes heel` / `feet` (keypose) |
| The character slides or jumps when the animation changes | Compare heel and toe with the idle using `check_strip.py` and cut again with the idle's numbers |
| A frame is cut off | The figure touched its panel edge in the sheet. Regenerate asking for more margin; check `clipped pixels` |
| A weapon appears in the art | Regenerate; hands must be empty fists |
| The weapon is the wrong size in tall frames | Item length is a share of the frame width; set Length once per character |
| Left and right arms swap between frames | Use the front or behind mark per frame in the hand tool |
| The hand drawn over a grip covers too much or nothing | Keep the mark on the fist; lower Hand size; gloves fall back to a disc |
| The browser pane cannot be screenshotted | See `DEV_NOTES.md`, "Testing in the browser pane" |

## Starting a new character (for example the mage)

1. **Look first.** Generate and settle the design (full body, side view facing right, neutral pose, plain background). Write the character paragraph once (outfit, hair, colours, proportions) and reuse it word for word in every prompt. Keep one clean reference image to attach each time.
2. **Idle first** (6 frames, 3 x 2), then `check_strip.py` on it: note its heel, toe, feet middle and height. Every other animation lines up with these. Decide whether the figure is the same height as the warrior (408 px) so the two can stand side by side.
3. **Folders:** `Animations/<Character>/<animation>/`, with the same file naming. `build.py` and the test page only know the warrior's folder and slots today; `DEV_NOTES.md` lists what to generalize.
4. **Weapon:** make the staff (or orb, book) a transparent PNG, tip up, and decide per animation whether it is held (closed fists as if gripping) or hidden (open hands for casting; mark the item hidden). The off hand can be Nothing or Other item.
5. **Animations to make:** idle, hit, death, dodge, then the attack and cast animations that carry the skills. Each skill gets a procedural effect (projectiles, auras, bursts) built in code, with its own `skill-fx/1` description.
6. **PvP:** once two characters exist, the test page needs to host two real fighters (`DEV_NOTES.md`).
