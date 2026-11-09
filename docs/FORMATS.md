# Data formats

Three json formats carry everything the art does not: where hands hold items (`hand-anchors/3`), where a travelling animation's frames stand (`frame-placement/1`), and how a skill's effect plays (`skill-fx/1`). All are independent of screen size, so any engine can read them.

## Files and names

For an animation `armored_hit_6frame` in `Animations/Warrior/hit/`:

| File | What |
|---|---|
| `armored_hit_6frame_strip.png` | The strip: N frames of 512 px side by side, transparent. The idle is `armored_idle_strip.png` (no frame count in the name). |
| `armored_hit_6frame_strip.hand-anchors.json` | The hand marks for this strip (`hand-anchors/3`, one animation). |
| `armored_hit_6frame_strip.placement.json` | The path (`frame-placement/1`), only for animations that travel. |
| `source/armored_hit_6frame_sheet.png` | The generated sheet the strip was cut from. |

A strip and its marks are matched **by name**: the strip name without `_strip.png` (`armored_hit_6frame`) must equal the `name` of the animation inside the hand-anchors file (the tool names animations after the strip file it was given; a trailing `_strip`, `_pack` or `_sheet` is dropped, case does not matter).

## `hand-anchors/3`

Written by `hand-anchor-tool.html` ("Save this animation" or "Save all"); read by the tool and by the test page.

```
{ "format": "hand-anchors/3", "note": "...",
  "characters": [ {
    "name": "Warrior", "fist": 0.09,
    "items": { "main": { "length": 0.42, "pivot": 0.81, "overlay": true },
               "off":  { "length": 0.42, "pivot": 0.81, "overlay": true } },
    "animations": [ {
      "name": "armored_idle", "frames": 6, "columns": 6, "fps": 10,
      "offItem": { "kind": "other", "length": 0.42, "pivot": 0.81, "overlay": true },
      "tracks": { "main": [ {x, y, a, front, hide, w} or null, ... one per frame ],
                  "off":  [ ... ] } } ] } ] }
```

- Two hands, called tracks: `main` is the character's left hand (the far arm), `off` is the right hand (the near arm). The character faces right.
- A mark: `x`, `y` are fractions of the frame from its top left (0 to 1); `a` is the angle in degrees, 0 = the item points straight up, clockwise is positive; `front` = the item is drawn in front of the body (false = behind); `hide` = no item on this frame; `w` = sideways squash (1 = normal). A `null` mark means nothing was marked for that frame (nothing is drawn).
- Item settings: `length` is the item's long side as a share of the frame WIDTH (512 px for every animation; before 2026-10-29 it was measured against the height, which made items 25% longer in 640-high frames), `pivot` is how far down the picture the grip is (0 = top, 1 = bottom; a sword is held near its pommel at 0.81), `overlay` = draw the hand over this item when it is in front.
- `fist` (per character) is the radius, as a share of the frame width, of the area searched around the mark for the hand.
- `picture` (in `items.main`, `items.off` and `offItem`): which item picture the arm holds: `sword`, `shield`, `staff`, `orb` or `book` (the mage's far arm holds either the orb or the spell book, never both: marks that say `orb` are shown as the spell book when the page's "Mage's far hand carries" choice is the book, with the book's own settings; a file that says `book` uses its own). The mage: `main` = `orb` floating above the open far hand, `offItem` kind `other` with `picture` `staff` in the fist. Files without `picture` mean the sword on the main arm and the shield or a second sword on the off arm (the mage is recognised by her name). A mark's position for a floating item is where its picture's grip point (`pivot`, 1.0 = the bottom of the picture) should sit.
- `offItem.kind`: `shield`, `other` (a second weapon or item) or `none` (the `off` track is all null). It is per animation and takes precedence over the character-level `items.off`. Exports from before it existed have no `offItem` and load as a shield.
- Draw order, per frame: items with `front = false` (main, then off), the body, items with `front = true` (main, then off), then the hand over each item in front whose `overlay` is true.
- The hand drawn over an item is the hand's own pixels from the body frame: the dominant skin colour (hue) within the `fist` circle around the mark, the connected area of that colour touching the mark, grown 2 px for the outline and closing knuckle lines. With no skin colour near the mark (gloves, armour) it is the whole disc. The same rule is in the tool and in the test page (`buildHand`); a game can run it once per frame at load time or bake the result into small sprites.
- Item pictures are not in the json: the game uses its own art for the sword, staff or shield, drawn as an image of height `length x 512 px` (squashed by `w`), hanging from the grip point, rotated about the grip by `a`.

## `frame-placement/1`

Where each frame of a travelling animation stands. Written by the test page ("Download .json"), read by it (loaded with the strip, or "Apply pasted path").

```
{ "format": "frame-placement/1", "animation": "attack", "file": "...strip.png", "frames": 8,
  "fps": 14, "hitFrame": 7, "smooth": true, "x": [ ...one per frame ], "y": [ ...one per frame ], "note": "..." }
```

- Frame i stands exactly at (x[i], y[i]) in the middle of its time slot. With `smooth: true` the position is linearly interpolated between frame middles (held at the first and last value before and after); with `smooth: false` it jumps from frame to frame.
- `y` is extra lift in character (= frame) widths, up positive, never below 0 (the ground line); it is added on top of the height already drawn in the frame. Everything clamps it at 0.
- **Attack** (`"animation": "attack"`): `x` = 0 is the fighter's home position, 1 is the strike point in front of the target (the target's centre minus 0.8 character widths); values past 1 or below 0 are allowed. `hitFrame` is the frame at which the hit lands (40% into it).
- **Dodge** (`"animation": "dodge"`): `"xUnit": "frame-widths"`: `x` is in character widths from the home position, positive toward the enemy, negative away from it (-0.2 = one fifth of a character back). `evadeFrame` is the frame on screen when the strike that is being dodged would have landed.
- Timing comes from the clock of the animation that was started: frame N is on screen at (N - 1) / fps. After the last frame the fighter slides back home in 280 ms.
- Only attack and dodge have paths. Hit and death play in place.

## `skill-fx/1`

Firebolt (`firebolt.skill-fx.json`, from the page's Firebolt panel) uses the same format for a projectile skill: `pack.hitFrame` = `pack.releaseFrame` is the cast's release frame, `palette` has an extra `deep` colour, and the timeline has `orb_charge`, `staff_tip_charge`, `release_flash`, `projectile` (with `spawn: staff_tip`, the path and speed) and `impact` at `arrival`; positions come from the hand marks (the top of the staff item: grip + pivot x length along its angle). Ice Shard (`ice-shard.skill-fx.json`, `element: ice`, palettes `ice` and `glacier`) uses the same shape with the timeline entries `orb_charge`, `staff_crystal_form`, `release_flash`, `projectile`, `ground_light` and `impact`; the page's skill select decides which skill the box (and the Download button) shows. Deep Freeze (`deep-freeze.skill-fx.json`, no projectile) has the timeline entries `orb_charge`, `release_flash`, `frost_crawl`, `aura`, `ice_block`, `seal`, `thaw` and `break`, and `params.look` ("code" or "painted", with `params.textures` listing the six `fz_*` pictures when painted), and a top-level `status` object: `{ "name": "frozen", "turns": 1, "chance": 1, "note": ... }`. Shatter Lance (`shatter-lance.skill-fx.json`) adds a `rules` list (`{if: "target is Frozen", damage: "+100%", removes: "frozen", applies: {status: "magic_def_down", amount: -0.25, turns: 2}}`, `{if: "target is Chilled and not Frozen", critical: "guaranteed"}`) and a `statuses` object that describes how Chilled and Magic Def reduced are drawn (the timeline has `impact_chilled` and `impact_frozen`). It plays in four beats on four frames of the cast (`params.fireFrame`, default 4; the beats are `fireFrame - 3` to `fireFrame`): `shard_appear` (50% visible), `shard_full`, `lance_form` and the projectile fired at once (`release_flash`, `projectile`). `params.chargeFrameMs` is how long each of the two charge frames (`fireFrame - 3` and `fireFrame - 2`) is held (the cast's other frames last 1000 / fps); the timeline has a `frost_charge` entry for the stronger frost on the orb and the staff's top and a `frost_aura` entry for the aura round the mage (the fire skills' jsons have the same entry named `fire_aura`, with their own levels) (the picture `frost_aura`, 30% / 60% / 100% on the three charge frames, turning; Ice Shard and Deep Freeze have a `frost_aura` entry too: 30% on frames 1 to 3, and 30% / 30% / 60% on frames 1 to 3); the lance's own slider defaults are `intensity` 1.2, `trail` 2, `impact` 1.2, `shake` 1.5. `form` = `{tail: [x, y], tip: [x, y]}` is the line marked on the stage for the first beat, in character widths from the orb's centre (x toward the target, mirrored when the mage faces left; y up); the shard fills it and the lance grows from its tail along it, and since the orb moves with the hand the whole thing follows it. The projectile is a perfectly straight line to the target in about 0.17 s with cold mist behind it (no wake picture). The game applies the status; the effect only draws it (the sealed block is the last frame, held until the game says the status ends, then `thaw`).


A skill's effect described as numbers plus a timeline, for porting the code-drawn effect to the game engine. Written by the test page (panel "Skill effect", "Download .json"). It does not contain frames; the effect is code.

```
{ "format": "skill-fx/1", "skill": "Thunderclap Guillotine", "element": "lightning", "description": "...",
  "pack": { "animation": "attack", "file": "...", "fps": 14, "hitFrame": 7 },
  "palette": { "name": "blue", "core": "255,255,255", "mid": "76,195,240", "glow": "122,92,255", "flash": "225,240,255" },
  "params": { "intensity": 1.5, "thickness": 0.6, "shake": 1.5, "impact": 0.8, "unit": "warrior (frame) width in px" },
  "timeline": [ { "frame": 2, "effect": "blade_crackle", "until": "impact", "note": "..." },
                { "frame": 5, "at": 0.1, "effect": "sky_strike", "duration_ms": 200, "note": "..." }, ... ],
  "bolt": { "method": "midpoint displacement", ... } }
```

- `frame` is 1-based, `at` is the fraction into that frame (the impact is at 0.4 of the hit frame). Times follow the animation's own clock, so a different fps or speed moves the whole effect.
- All sizes in the effect are shares of the warrior's width (the frame width on screen), so the effect scales with the character.
- The algorithms the `note` fields describe are in the test page: `boltPts`, `drawBolt`, `crackleDraw`, `glowDraw`, `skyDraw`, `trailDraw`, `impactFx`, `startSkill` (see `DEV_NOTES.md`).

## What is stored where (so nothing is lost by accident)

| Where | What |
|---|---|
| The hand tool, in the browser | Characters, animations, marks and images (autosave: localStorage `hand-anchors-v3`, images in IndexedDB). Save to a file to keep the work. |
| The test page, in the browser | A path you edited, per pack file name and frame count (localStorage `wvg-path:...`). The paths in the project folder are the real ones. |
| The test page file | The five built-in animations with their marks and the jump attack's path (filled in by `build.py`). |

Cinderburst (`cinderburst.skill-fx.json`, `element: fire`, palettes `fire` and `blue`) uses the Firebolt's shape (a projectile from the top of the staff; the timeline has `orb_charge`, `core_form`, `release_flash`, `projectile`, `ground_light`, `impact` and `burn_detonation`) with a `rules` list (`{if: "target is Burning", detonates: ..., removes: "burn"}`) and a `statuses.burn` object (`turns` 3, `maxStacks` 3, `damagePerStackPerTurn` 3, and how it is drawn); the game applies the damage over time, the page draws it.

Pyroclasm (`pyroclasm.skill-fx.json`, `element: fire`, palettes `fire` and `blue`) has no projectile: the timeline has `orb_charge`, `vortex_form`, `earth_glow`, `release_flash`, `vortex_drop`, `fissure`, `eruption` and `burn_applied`, `params.look` ("code" or "painted", with `params.textures` listing the six `pc_*` pictures when painted; `params.frame3Ms` is how long cast frame 3 lasts (350 ms in all), so the fire aura stays at 100% for it: every later time in the cast, release included, is later than on a plain strip) and a `rules` list (`{always: true, damage: "heavy magical damage (about 2x a normal cast)", applies: {status: "burn", stacks: 3, turns: 3}}`); the Burn status is described in the Cinderburst json (`statuses.burn`), the game applies its damage over time.

Barrier (`barrier.skill-fx.json`, `element: arcane`, `kind: "passive"`) is the mage's passive and has no pack, projectile or target: `params` has `enabled`, `visibility` (0.5 = half visible while combat is active), `size`, `castMs` (1000), `dropMs` (700), `rippleMs` (800), `palette` has `line`, `glow` and `core` ("r,g,b"), `hooks` lists when it acts (`combat_start` cast, `combat_active` hold, `mage_hit` ripple, `mage_defeated` break, `combat_end` drop) and `timeline` describes the form, flash, sphere, ground ring, sheen and ripple (entries keyed by `on` or `at` instead of `frame`). The engine draws it from code (the front half of a plain round glass circle, on the side the enemy is on: a soft edge glow, a rim line and highlights, with a half rune ring on the ground in front of her feet; the timeline entry is `half_circle`, it was `sphere` until 2026-11-03); nothing in it is a picture.
