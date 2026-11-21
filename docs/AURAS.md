# Auras: every character gets its own SHAPE, the element keeps its COLOUR (design, 2026-11-22)

The user, 2026-11-22: the elemental auras (the user's `Elemental auras.png`: fire, lightning, dark, holy) are liked as they are, but using them exactly the same for every character is low effort; they were designed for the Mage's stance and skills. Design distinct auras for the other characters and keep the element colours the same for consistency.

## The rule

- **COLOUR = the element, the same for every character** (so a fire skill reads as fire whoever casts it): fire = orange-red, ice/frost = ice blue, lightning = blue-white with violet edges, dark = violet (the dark slime's `DKC`: core 235,205,255, bright 175,74,255, mid 105,20,255, deep 60,10,170), holy = gold (`HOLY_PAL`: 255,253,240 / 255,232,150 / 255,196,84), and the Cleric's crimson (the Covenant's pact, gold cores).
- **SHAPE = the character** (how that character stands, moves and fights): the aura is built from layers that suit the body and the skills, not from the Mage's turning cylinder.

## The shapes

| Character | Fights like | Aura shape | State |
|---|---|---|---|
| **Mage** | a caster who stands and channels | the **vortex**: ribbons wrapped round her like a turning cylinder (`auraLayer`, the user's pictures) | built, KEEPS it (it was designed for her) |
| **Cleric** | a grounded, armoured warrior-priest | **built from layers on the ground and behind him** (below) | built 2026-11-22 |
| **Warrior** | a heavy two-sword melee fighter | **the element lives on the blades and in the ground**: a sleeve of the element along each blade (heat, frost, crackle), a shockwave and dust ring at his feet when he plants, sparks or embers rising from the floor, never a cylinder | partly there (the blades, the lightning crackle); the ground layer to design |
| **Rogue / Assassin** | a fast, stealthy duelist | **a ring at the waist and trailing wisps**: a thin band of the element spinning round her hips (the Rogue's Winter's Kiss frost ring and Static Stiletto lightning ring are this), wisps and afterimages trailing off her cloak and daggers, a low mist rolling along the floor | the rings exist for ice and lightning; dark (Umbral Shroud) still uses the Mage's cylinder |
| **Spellblade** | a duelist who fights with a sword and magic | **a rune disc floating behind him** (a vertical magic circle) and the element running along the blade like a sheath | not designed in code yet |

## The Cleric's three auras (built)

Made in the page from the TAILORED pieces of the Cleric's sheets (`hj_*`, `dd_*`, `cp_*`, 2026-11-22; the older generic `hl_*`, `dk_*` are the fallback), by `pcAura` / `clAura` (`pcAura(A, steps, tEnd, fadeMs, tex)` keeps the old call: `holy_aura` -> holy, `dark_aura` -> dark, `cov_aura` -> crimson). They build up with the frames (30%, 60%, 100%) and fade after the blow; there is a back layer (behind him) and a front layer (over him).

- **HOLY = CONSECRATION** (Radiant Smite, Sanctified Judgment, Aegis of Retribution): an ornate seal on the ground under his feet, a nimbus (a radiant disc turning slowly) behind his head and shoulders, two WINGS of light behind him, feathers rising. Grounded and upright: he is blessing the ground he stands on.
- **DARK = SHADOW CREEPING FROM THE GROUND** (Dark Penance, Unholy Siphon): a dark seal on the floor, a faint column of smoke behind him, claws rising from the ground at his feet, two ribbons of smoke at his sides, motes. Low and creeping: the dark rises from below.
- **PACT = A HEARTBEAT** (Spiteful Covenant, crimson, its own cp_* pieces): a crimson ring on the ground that PULSES like a heart, small flames at his feet, rising embers (the contract seal, the rain of embers, the breaking chains and the shield of its own belong to the skill itself); on top of it the Covenant's own pay and roar effects (`covenantPaint`: the big flames are drawn behind him so the figure stays readable).

The Mage's cylinder code (`auraLayer`, `auraDraw`) is untouched except for one optional hook (`L.cxf`, a function that gives the centre) that nothing uses any more.

## How to design the next character's auras (the process)

1. Decide the shape from how the character fights (the table above is the proposal; the user can change it).
2. Build it first from the pieces that exist (additive pieces, tinted in code when the colour is another element's), per element the character uses.
3. If the pieces are not enough, write a tailored sheet (like `Cleric_vfx_kit/`: 9 pieces, pure black, ChatGPT 1:1) with the aura's pieces among them; the pieces that stand upright have their base at the bottom, the ones on the floor are flat wide ovals.
4. The user judges it in motion; every piece has its size and alpha in one place (the `clAura` function for the Cleric).

## Next (nothing done yet)

- The **Warrior** (his lightning, fire and ice skills already put the element on the blades: add the ground layer), then the **Rogue/Assassin** dark aura (the Umbral Shroud still uses the Mage's cylinder), then the **Spellblade**'s rune disc. Which one first is the user's call.
- The Cleric's tailored sheets are in (2026-11-22, `docs/CLERIC_VFX.md`): waiting for the user's verdict (final or adjustments).
