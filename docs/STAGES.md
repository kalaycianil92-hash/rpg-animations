# The stage looks: the Forest Kingdom

The user's design (2026-11-01): every stage of the game has a forest theme, and the PvE stages 1 to 100 are the **Forest Kingdom** category, in **five acts of 20 stages**, each act with its own monsters and its own look. Besides them there are the arena (see "The arena") and the dungeon (see "The dungeon"), both designed on 2026-11-03. The misty forest made first (pictures `far` and `ground`, see `docs/PROMPTS.md`, "Forest background") is the look of act 2. This file is the design; the names are suggestions and the pictures of acts 1 and 3 to 5 do not exist yet.

**Status (2026-11-01):** the scene mechanism and the props layer are built in the test page (see "Stage looks" in `docs/DEV_NOTES.md`). The pictures: all five acts (Glimmerwood, Mistwood Hollow, Moonshade Woods, Ashfall Reach and Warhorn Fields: far, ground and props each) are the user's, in the page since 2026-11-01 (act 2's were generated twice, act 5's floor and props after a rewrite of the prompts); no stand-ins are left (`source/tools/dev/make_standin_scenes.py`). Prompts are written for all five acts (`docs/PROMPTS.md`; act 2's props prompt was added later).

## The five acts

| Act | Stages | Monsters | Name (suggested) | Look |
|---|---|---|---|---|
| 1 | 1 to 20 | Slimes | **Glimmerwood** | the brightest and most colourful: a sunlit magical forest, fresh greens and aqua, soft beams, glowing mushrooms; still mid-value on the floor so the effects read |
| 2 | 21 to 40 | Goblins | **Mistwood Hollow** | the forest we have: teal mist, mossy trunks, golden shafts, a bare earthy floor (done) |
| 3 | 41 to 60 | Wolves (dark and holy) | **Moonshade Woods** | the same forest at night: deep blue-green dark, a moon, cold light on the floor in patches; holy light (pale gold) and dark light (violet) as accents |
| 4 | 61 to 80 | Ogres | **Ashfall Reach** | barren land: bare dead trees, grey ash soil, a destroyed village, a dull smoky sky |
| 5 | 81 to 100 | Orcs | **Warhorn Fields** | the barren land turned into an orc battlefield: smoky dusk, mud, banners, tents, barricades |

The names tell one story, a forest kingdom that is lit, then clouded, then dark, then burned, then invaded. Other names, if you prefer: Dewlight Glade, Greymist Thicket, Nightfall Grove, The Withered Reach, Bloodbanner Moor. The time of day and the light also move along: bright day, misty day, night, ash and dusk, smoke and dusk.

## The artifacts layer ("props")

Agreed and recommended: one more picture per act, the objects that finish the theme. How it works:

- **File:** `props.png`, on flat magenta like `ground` and `mid`, keyed and made seamless by `make_bg_layer.py` (the same camera: horizon at 62%).
- **Where it is drawn:** between the floor and the fighters, objects standing on the far half of the floor (between 62% and about 84% of the height, the fighters' feet are at 88%). So nothing covers the fighters, and a prop never stands where a fighter stands.
- **Speed:** a little slower than the floor (about 85%), because it stands further back: the parallax gets one more step.
- **Sparse and varied:** about six to ten objects across one picture, no two the same, none taller than about a third of the stage, nothing as big as a landmark. To avoid a visible repeat the layer should be longer than the others: generate two or three pictures per act and let the tool join them (it already joins several pictures into one ring).
- **Low contrast like everything else:** props are details, not the stars; glow only in the objects that are meant to glow, thin and small.
- **Later, in code:** flicker for fires and lanterns, a pulse for glowing runes, shrines and mushrooms, drifting spores and smoke. That needs a small list of where the lights are in each picture (like the hand marks); not part of the first version.
- **Not now:** a strip in front of the fighters (grass, branches along the bottom edge), which would add depth but also covers the feet. Possible later.

Suggested artifacts for each act (each picture gets four to six kinds):

| Act | Artifacts |
|---|---|
| 1 Glimmerwood | glowing mushroom clusters, rune stones with a soft blue-green glow, aqua crystal clusters, giant flowers and lilies, slime puddles and trails, a fairy ring of toadstools |
| 2 Mistwood Hollow | goblin totems (a skull on a pole), crude stake fences and rope snares, stolen loot sacks and a broken crate, a cooking pot over dead embers, a rusty trap, a lantern on a post |
| 3 Moonshade Woods | holy shrine stones (pale gold glow, for the holy wolves), dark altar stones (violet glow, for the dark wolves), moonlit boulders, a fallen log, wolf bones, paw prints pressed in the ground |
| 4 Ashfall Reach | burnt hut frames, a toppled wagon and broken cart wheels, fence posts, ash piles and scorched patches, a scarecrow, a ruined well |
| 5 Warhorn Fields | tattered war banners on tall poles, orc hide tents, spiked barricades, weapon racks and broken weapons stuck in the ground, war drums and skull totems, a bonfire pit, siege remains |

## Rules every look follows (what the forest taught)

- **One camera.** The horizon is at 62% of every picture's height, the floor fills the bottom 38%, the fighters stand at about 88% of the base stage height. Nothing needs tuning when a look is swapped.
- **Layers.** `far` (opaque, wide, 3:1 or wider, with the big near elements in it), `ground` (the floor band on magenta), `props` (new, above), `mid` only if a look needs it (the forest did not). Made seamless by `source/tools/make_bg_layer.py`.
- **Low contrast and mid-dark behind the fighters.** The skill effects are additive glows (lightning, fire, ice, and the holy and dark auras): they read best on calm, mid-dark, desaturated areas. No white and no big saturated patches behind the fighters. Act 1 is the one to watch: bright must mean colourful and lit, not pale; keep the floor and the area behind the fighters mid-value.
- **Keep the characters readable.** The warrior is dark steel and skin, the mage a blue robe with blonde hair: no mid-blue floors or walls behind her, no near-black behind the warrior's armour. In act 3 the dark wolves must not vanish into the night: the floor stays mid-dark and moonlit in patches.
- **Nothing unique.** The far picture repeats sideways as the world scrolls: a repeating motif (trunks, bare trees, tents), no landmark.
- **Evenly spread small details on the floor** (a stone, a leaf, a crack every 8 to 12% of the width): they make the run's speed visible.
- **Big monsters.** Ogres (act 4) and orcs (act 5) are bigger than slimes, goblins and wolves: this needs the planned size per monster, and the stage must not look small around them.
- **Generate big:** at least 2K; the tool takes `--height 1100` or more (see "Phone screen" in `docs/DEV_NOTES.md`).

## How the stage changes (proposal)

- **Scenes are folders:** `source/assets/bg/<scene>/` with `far.jpg`, `ground.png`, `props.png`; one folder per act (`glimmerwood`, `mistwood`, `moonshade`, `ashfall`, `warhorn`); the old `forest` folder is now `mistwood`. The test page embeds them (it is one file, 30 MB now); the game should load them as files.
- **Stage to act:** act = (stage - 1) div 20 + 1, so the look changes at stages 21, 41, 61 and 81. A table in the page (`STAGE_LOOKS`) holds it, and the test page gets a Scene select and a Stage box to jump (for example to 20, then a win shows the change to 21).
- **Chapter change:** when the next stage is in another act, the stage change gets one more beat: while the run slows, the old scene cross-fades into the new one (far first, then the floor and the props), and the caption gets a second line, for example "Stage 21" with "Mistwood Hollow" under it. A look that has no pictures yet falls back to the nearest one that has.
- **Monsters per act:** slimes, goblins, wolves, ogres and orcs: the planned size per monster, and monster art, are needed for each act (only the goblin placeholder exists).

## The arena: Oakcrown Colosseum (design, 2026-11-03)

The user's brief: an arena stage with three layers again; no change between stages, because a fight starts and ends in the same stage; a Colosseum theme with flags and war props. Decisions (mine, to be changed if they disagree):

- **A mode, not an act.** The arena is chosen by the kind of fight (PvP: two player characters face each other), not by a stage number. Suggested name: **Oakcrown Colosseum** (the forest kingdom's arena).
- **Fixed view.** No scroll, no run across the world, no "Stage N" caption, no cross-fade, no new monster riding in. After a fight (Victory or Defeat) the stage stays as it is until Reset. In the page it is the **Arena** choice of the Look select (it is never picked by the stage number).
- **Same three layers, same camera, same tool.** `far`, `ground` and `props` in `source/assets/bg/arena/`, horizon at 62%, cut into repeating strips by `make_bg_layer.py`, drawn by the same code, only standing still. Why strips and not one composed picture: a colosseum wall IS a repeating arcade; a strip fits every stage width (a phone shows about 45% of a 16:9 picture, a desktop about 75%, and a strip needs no tuning for either); the prompts, the tool and the checks stay the ones we know. A composed view with a central gate or royal box would need its own non-repeating pipeline; it can be added later as one more layer if wanted. The page shows the strips from their left edge.
- **Look.** The one clear, sunlit, festive place: warm late-afternoon light, pale weathered sandstone and limestone with a little moss and ivy and a few treetops over the rim (the light tie to the Forest Kingdom). `far`: a row of flagpoles with flags on the rim, rising tiers with a soft crowd (colour dabs, never readable people), an arcade with big hanging banners, and a heavy lower wall of gateways whose base meets the sand at 62%. `ground`: tan arena sand, raked and scuffed, with boot prints, drag lines, grit and a few dropped arms. `props`: a fixed set of five, in this order: cold fire basket, armour stand (empty, with shields), bronze gong, armour stand, cold fire basket (equal gaps, the gong at the exact centre of the floor).
- **Colours.** Everything mid-value (pale is the trap: sand and sandstone turn cream and the effects vanish on white; the blue-robed mage and the dark warrior must read on it). Banners: forest green with gold, brick red with cream (leaning orange, never crimson or pink: the keyed layers would drop it). No blue, no violet. No open flames (fire baskets are cold; the effects are glows).
- **Later, in code (not part of the first version):** flags and banners that sway (they would have to be separate pieces, with a list of where they hang, like the hand marks), the fire baskets lit when a fight starts, a soft crowd murmur of light. A phone landscape layout is covered by the phone notes in `docs/DEV_NOTES.md`.
- **Prompts:** `docs/PROMPTS.md`, "Arena: Oakcrown Colosseum" (three pictures: far, ground, props).
- **Pictures: made by the user and in the page since 2026-11-03** (first-result notes in `docs/PROMPTS.md`). The far wall's base is at 75.8% of its height instead of 62%, so the arena folder has a `horizon.txt` (`0.758`) and the page scales that far picture to put the line on the ground line. The props came as one row of nine; the user chose a fixed set of five instead (cold fire basket, armour stand, gong, armour stand, cold fire basket; equal gaps; the gong at the exact centre), drawn once and centred (`centered.txt`); no banner standards.

## The dungeon: Rootdeep Crypt (design, 2026-11-03)

The user's brief: four stage designs for the dungeon: (1) the **entrance**, where a party of four stands and, when "Enter" is chosen, moves toward the entrance gate; (2) the **regular stages**; (3) a **rest area**; (4) a **boss room**. Decisions (mine, to be changed if they disagree):

- **One place, four looks.** This settles the old open question (forest theme or its own look): the dungeon is **Rootdeep Crypt**, the burial crypt of a forgotten forest kingdom under the oldest oak: old grey-brown stone, roots forcing through walls and ceilings, moss. The roots are the tie to the Forest Kingdom and the thing that makes it recognisable; a plain stone catacomb (my first draft) would look like every dungeon. Suggested names: **Rootgate** (entrance), **Crypt Halls** (regular), **Vigil Hall** (rest), **Throne of Roots** (boss).
- **Colour and light (the rules the other looks taught, plus the crypt's own).** Mid-DARK, never black (the dark-armoured warrior must read, the effects want a calm mid-dark ground); warm grey-brown stone and NOT blue-grey (the mage's blue robe and the frost effects would vanish); olive moss, tan roots, rusty iron, bone ivory; the floor clearly lighter than the walls. The only glow is a soft yellow-green on a few moss patches (and, in the rest hall only, small warm lantern glows and one pale-gold shrine stone). No flames anywhere (torches, braziers, candles and the fire pit are cold; their flicker is drawn in code later), no blue, violet or pink.
- **The four looks:**

| Look | Mode | Pictures | What it shows |
|---|---|---|---|
| **A. Crypt Halls** | scrolls like the acts (run, Stage N, the next monster rides in); one look for all regular dungeon stages | far, ground, props: repeating strips | a long vaulted hall: round pillars and arches, niches with sarcophagi and iron-barred openings, roots hanging from the ceiling, flagstone floor; props: sarcophagi, urns, broken pillars, cold braziers, chests, rusty arms, root tangles, bones |
| **B. Rootgate** | fixed, one composed picture per layer | far, ground, props (cut-outs) | dusk at the foot of the oak: the open gate (doors open on a dark passage) at 72% of the width with roots curling over it, the open forecourt on the left 55% where the party of four stands; props: a cold brazier, a fallen pillar, a mossy shrine, a root-wrapped boulder |
| **C. Vigil Hall** | fixed, composed, no fighting | far, ground, props (cut-outs) | a quiet vaulted alcove, symmetrical, three lanterns, three niches with a small shrine and a pale-gold stone in the middle one; swept floor; props: fire pit with a hanging pot, two bedrolls, crates and a barrel, stool and table, a lantern post |
| **D. Throne of Roots** | fixed, composed | far, ground, props (cut-outs) | a vast, tall, round hall, symmetrical: a colossal root-wrapped stone throne at the centre of the far wall, two root-wrapped columns, roots hanging like curtains; a wide cracked dais with no circles or symbols; props: two brazier columns, a heap of bones and rusted armour, a pillar stump with chains, a tilted sarcophagus |

- **The entrance's movement.** The party of four stands in the open forecourt on the left; the gate is at 72% of the width. On "Enter" they run to the gate: the characters move across the stage in code while their run frames play, the picture stays still; they go through the threshold and the stage fades to the first hall. (A camera pan with scrolling layers was the alternative; it needs long non-repeating pictures and was left out.) **A one-character preview is in the page (2026-11-03):** with the Rootgate chosen, the button "Enter the dungeon (preview)" runs the warrior or the mage from their place to the gate (the gate's place is `gate.txt`, 0.745 of the far picture's width), in through the door (up into the passage, smaller, fading), and the stage cross-fades into the Crypt Halls.
- **Composed looks are not strips.** B, C and D are single pictures, drawn once and centred like the arena's props. They are asked for as 16:9, not wider: the stage is about 1.5 times as wide as it is high, so a 16:9 picture scaled to the stage's height shows its middle (about 75% of the width on a desktop, 45% on a phone). Everything important stays in the middle 70%. Their props are cut-outs in a row with big gaps and a script lays them out (equal gaps, symmetrical sets), as in the arena.
- **Pictures and page (done 2026-11-03):** the user's twelve pictures (the halls: far, floor and one props; Rootgate, Vigil Hall and Throne of Roots: far, floor, props each) are in the page as the four dungeon entries at the end of the Look select. The hall scrolls and changes stages but keeps its look; the other three stand still, drawn once and centred, with their far picture's wall base and their floor's far edge in `horizon.txt` and the cut-outs laid out by `source/tools/dev/compose_dungeon_props.py`. Details and what was measured: the first-result notes in `docs/PROMPTS.md` and "Stage looks" in `docs/DEV_NOTES.md`.
- **Not built yet:** the party of four (the page has two fighters; the entrance walk is previewed with one character, the whole party's walk, the rest hall's camp and the party's places in a fight come with the party), a boss that is bigger than the stage's headroom (the planned size per monster; the throne room may need more headroom), the fire pit's flicker and the rest hall's healing glow.
- **Prompts:** `docs/PROMPTS.md`, "Dungeon: Rootdeep Crypt" (thirteen pictures). Suggested order: **A** (the halls, the most played), then **B**, **D** and **C**.

## Order of work

1. Agree the names, the acts and the props layer (this file).
2. Add the scene mechanism and the props layer to the page, and test them with the misty forest plus stand-in pictures (done).
3. Act 1's three prompts (far, ground, props) are written (`docs/PROMPTS.md`, "Act 1: Glimmerwood"); the pictures are the user's to generate. Per act: prompts (the forest's three-prompt pattern with the act's theme, plus one for props), generate at 2K or more, run `make_bg_layer.py`, look at it with the fighters and the effects on it. Suggested order: act 1 (the brightest, the first thing a player sees), then 3, 4 and 5.
