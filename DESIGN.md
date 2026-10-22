# Armarius — Design Document

## 1. Overview

A GM-facing desktop tool for tracking the structural, "paperwork" side of an
*Ars Magica 5th Edition* saga: characters, covenants, laboratories,
libraries and spells, and the relationships between them (who lives where,
who works in which lab, who's read which book, who knows which spell). It
complements — but does not depend on —
[Ars-Magica-Solo](../Ars-Magica-Solo), which handles solo-play session
mechanics (Oracle, Chaos Factor, adventure/event generation).

Ruleset reference: [Ars Magica – Definitive Edition (Core Rules)](https://github.com/OriginalMadman/Ars-Magica-Open-License/blob/main/reviewed/Ars%20Magica%20-%20Definitive%20Edition%20(Core%20Rules).md)

## 2. Goals & Non-Goals

**Goals**
- Model every field that legitimately appears on a Character, Covenant,
  Laboratory, or Library/Book record, with real relationships between them
  (not flat text blobs).
- Start as a reliable data tracker — enter what's on paper, browse it,
  edit it — and grow toward actively *running* seasonal activities (Study,
  Lab Activities) on top of that data.
- Support multiple independent sagas/covenants in one tool.
- A GM-facing tool that the storyguide can also host for the troupe
  (FEAT-14, decided 2026-10-06): the storyguide's copy serves the saga to
  players' browsers (textual-serve, tools/serve.py) over a private network
  the storyguide picks; players sign in with a name and passcode kept in
  the saga. One computer, one set of saga files: no sync between copies.
  Plan: reference/feat-14-plan.md.

**Non-Goals (for now)**
- Combat resolution (initiative, attack/damage rolls, wound tracking as a
  live subsystem).
- Bestiary content/management.
- Realm mechanics (Divine/Faerie/Infernal/Magical auras, Twilight *content*
  generation, supernatural interactions) beyond a character or lab simply
  recording an aura rating or a realm-related Virtue/Flaw.
- Story/Saga narrative tooling (that's Solo's domain).
- Sharing by syncing saga files between computers, or a separate server
  (see FEAT-14: the storyguide hosts instead).

**Scoping principle:** if it's a field on a Character, Covenant, or
Laboratory sheet, it's in scope, even if we don't yet compute anything from
it. Subsystems that aren't really "sheet data" (combat resolution, bestiary,
realm lore) are deferred until there's a reason to pull them in.

## 3. Tech Stack

- **Python 3.14+**, managed with `uv` (mirrors Ars-Magica-Solo).
- **Textual** for the TUI. Consistent with Solo, keyboard-driven, no web
  server needed.
- **A shared core, front-ends on top.** The rules, models, seasons and
  storage never import a UI library; nor do `form_spec.py` (what a form
  asks for and how its entries are checked), `actions.py` (what can be done
  in each sheet section and the More / New menus, and where),
  `tables.py` (a list as columns and cells, which the desktop draws as a
  table while the terminal pads the same values into lines) and
  `sections.py` (the section ids both refer to). The front-ends are the
  two sub-packages around that core (Ports and Adapters): `tui/` is the
  Textual front-end (the app, its screens, themes and CSS, and the hosting
  that serves it to players), which draws those forms and binds those
  actions to keys; `gui/` is the desktop GUI (FEAT-16, PySide6), whose
  libraries come with the optional `gui` dependency group so the terminal
  install stays lean. `tests/test_core_boundary.py` enforces the line:
  outside `tui/` and `gui/`, no module may import Textual, Rich, PySide6
  or a front-end module, and neither front-end imports the other.
- **Plain JSON files** for persistence. One file per saga (or a small set of
  files per saga), human-readable and git-diffable. Relationships between
  entities are stored as IDs and resolved in code — no ORM/SQL.
- **`ruff`** for linting, matching Solo's config.
- Standalone repo. No code or runtime dependency on Ars-Magica-Solo. We
  avoid deliberately *incompatible* choices (e.g. wildly different ID/date
  conventions) so a future data bridge stays plausible, but we don't design
  for integration yet.

## 4. Entity Model

```
Saga
 └─ Covenant  (n per saga)
     ├─ Character (n)   [magus | companion | mythic companion | grog]
     │    ├─ Virtue/Flaw instances (from catalog)
     │    ├─ Ability scores
     │    ├─ Art scores            (magi only)
     │    ├─ Spells known          (magi only)
     │    ├─ assigned Laboratory   (0 or 1, magi only)
     │    └─ Familiar              (0 or 1, magi only)
     ├─ Laboratory (n)
     │    ├─ owner: Character (0 or 1)
     │    └─ Virtue/Flaw instances (lab-specific, from catalog)
     └─ Library tab: every Book kept in the covenant (see below)

Book (n per saga)
 ├─ type: Art Summa | Ability Summa | Tractatus | Lab Text | Casting Tablet | Other
 └─ owner: the Covenant, a Laboratory, a Character -- or none (files under the saga)

VirtueFlaw catalog (shared reference data, not per-saga)
Spell catalog / instances (a Spell can be "known" by a character and/or
  "embodied" in a Lab Text book; see reference/UI_Conventions.md §6)
```

The tree shows ownership, not storage: a saga file keeps flat lists of
covenants, characters, laboratories, familiars, books and spells, linked by
id (see §6).

Key relationship notes:
- An Art's or Ability's score is derived from the total xp spent on it
  (`rules/xp.py`, the Advancement Table); only the xp is stored. Saves
  from before this (STORY-806) typed a score beside the xp and are
  migrated on load.
- A Character's `covenant_id` is nullable (not every character is attached
  to a covenant at all times).
- A Laboratory belongs to exactly one Covenant, and has at most one resident
  owner Character at a time, but ownership can change over time (track
  history later if needed — not v1).
- A Book has a single owner (`owner_kind` + `owner_id`): a covenant, a
  laboratory or a character, or none. There is no separate Library record:
  a covenant's Library tab lists the books it owns plus those owned by its
  laboratories and characters; a laboratory's Inventory and a character's
  sheet list their own; books with no owner (or one that no longer exists)
  appear under "Unassigned Books" in the saga tree. A Summa or Tractatus is
  on an Art or an Ability; a Lab Text or Casting Tablet records a spell by
  name and level, linked to the spell record (see reference/UI_Conventions.md
  §6). See reference/UI_Conventions.md §5 for costs.
- Virtues and Flaws are catalog entries (name, category, cost, description)
  referenced by *instances* attached to a Character or a Laboratory, each
  instance carrying any per-case parameters (e.g. "Affinity with
  [specific Art]"). The character catalog (STORY-707) holds the Definitive
  Edition's entries plus those of the open-content supplements, each with
  its `source` book(s), a one-line `summary`, and an `audience` for the
  ones only non-human characters (or Mythic Companions) take; RoP:Magic /
  HoH:Mystery Cults Qualities and Inferiorities are entries too, listed
  with the Virtues and the Flaws respectively. A "Major or Minor" entry is
  two entries. An entry the book lets a character take more than once is
  `repeatable`, with an optional `max_count` and a `max_per_parameter` (how
  many copies may share the same parameters); each copy is its own
  instance. The field-by-field source is
  reference/virtues-and-flaws-reference.md.
- The character picker hides what a character can't take (STORY-710),
  structural rules only (catalog.VirtueFlawChooser): Hermetic entries
  without The Gift (a magus counts as Gifted); for grogs, Major and
  Hermetic entries and The Gift; entries whose `audience` the character
  isn't (a familiar is an animal and a magic being; a Mythic Companion,
  a character type that otherwise counts as a companion, gets its Free
  Mythic Companion Virtues); and, once STORY-711 lands, books not in play.
  A toggle lists them anyway, each marked with the reason. Prose
  prerequisites ("requires Demonic Blood") stay in the description.

## 5. The Virtue/Flaw Modifier System

This is the part of the schema we're deliberately over-building now, per
your call: there are enough Virtues/Flaws (on both characters *and* labs)
that affect Lab Total, Casting Total, Study/Aging rolls, etc. that bolting
a calculation layer on after the fact would mean reshaping the data model
later. Instead, every catalog Virtue/Flaw carries **structured modifier
tags**, not just flat descriptive text (illustrative entries: the shipped
catalog's character Virtues & Flaws don't carry their modifiers yet):

```json
{
  "id": "vf_affinity_with_art",
  "name": "Affinity with (Art)",
  "type": "Virtue",
  "category": "Hermetic",
  "tier": "Minor",
  "cost": 1,
  "parameters": ["art"],
  "modifiers": [
    { "applies_to": "art_xp_gain", "target": "{art}", "multiplier": 1.5 }
  ]
},
{
  "id": "vf_gifted_researcher",
  "name": "Gifted Researcher",
  "type": "Virtue",
  "category": "Hermetic",
  "tier": "Minor",
  "cost": 1,
  "modifiers": [
    { "applies_to": "lab_total", "activity": "original_research", "amount": 3 },
    { "applies_to": "lab_total", "activity": "invent_spells", "amount": 6 }
  ]
}
```

- `applies_to` names a **modifier type** (`lab_total`, `casting_total`,
  `spontaneous_total`, `study_total`, `soak`, `aging_roll`, …, or a resource
  flow like `art_xp_gain`, `vis_extraction`), validated against the
  registry in [`ars_magica_manager/totals.py`](ars_magica_manager/totals.py)
  — an unrecognized value fails loudly at load time rather than silently
  vanishing from a future calculation.
- `activity` optionally narrows `applies_to` to one specific activity within
  that type (see `totals.ACTIVITIES_BY_TYPE`) — e.g. Lab Total differs by
  whether you're Inventing Spells, Extracting Vis, doing a Longevity Ritual,
  etc. Since `modifiers` is a list, one Virtue/Flaw can carry several
  differently-scoped, differently-sized modifiers, as in the
  "Gifted Researcher" example above (+3 for Original Research, +6 for
  Inventing Spells) — this is also validated, so an activity that isn't
  valid for its `applies_to` type is rejected the same way.
- Modifiers on a Character instance and on that Character's assigned
  Laboratory instance both feed the same Total calculation.
- v1 stores, validates, and displays these tags but does **not** need every
  Total formula implemented — the schema just has to make "sum all
  `lab_total` modifiers for this character + their lab, filtered to this
  activity" a trivial query once we build that engine, instead of a schema
  migration.

### 5.1 Decision: one effect model for every catalog (2026-09-23)

**Decided -- don't re-open.** Every catalog that can change a number -- character
Virtues & Flaws, laboratory Virtues & Flaws, covenant Boons & Hooks, and any
user-made entries later -- carries its effects in the **same `Modifier` shape**
(`applies_to`, `amount`/`multiplier`, `target`, `activity`), checked at load time
against the one registry in `totals.py`. Nothing looks up a catalog entry by name
or id to decide what it does; the effect is data on the entry. Each total is then
worked out by the same kind of query: collect every modifier of a type (and
activity/target) from everything attached to the records involved -- a magus's
Virtues, their laboratory's, the covenant's Boons -- where each attached
*instance* counts, so a repeatable entry taken twice applies twice.

Considered and rejected: per-purpose flags with the rule in code (e.g. a
"buildings" tag and +2/+5 hard-coded in Economics), more one-off key -> number
maps, and per-entry code hooks. Each keeps effects out of the catalog data or
splits them into formats the Rules Engine would have to reconcile.

**Staged migration.** Rather than converting everything at once, each catalog
moves to the shared shape when a real calculation needs it:
- Character Virtues & Flaws: in this shape; effects are filled in by each
  Rules Engine story as its total needs them (Puissant Art/Ability first,
  STORY-804), with a closing audit (STORY-818).
- Covenant Boons & Hooks: **converted** -- `covenant_aura` (the Aura Boon / Weak
  Aura Hook) and `covenant_expense` / `buildings` (the Buildings surcharge).
- Laboratory Virtues & Flaws: **converted** (STORY-804) -- each effect on a
  Characteristic is a `lab_characteristic` modifier whose `target` names it.
  Specialization grants are `lab_specialization` modifiers (STORY-817): a
  fixed target, or "{specialization}" picked from the entry's `choices` as
  the Virtue is added; Undecorated is `lab_specialization_high`. Grants the
  book leaves to distribute stay typed-in Specialization sources.

All three are collected by one lookup, `rules.effects.collect()`, over any mix
of character, laboratory and covenant sources. **Stacking (settled,
STORY-804):** flat amounts are added to the base first, then multipliers
multiply that sum (several multiply together), as in the Definitive Edition's
advancement pipeline; rounding the result is the owning rule's call.

**Former exceptions, moved onto the catalog (STORY-815):** the Gentle and
Blatant Gift's Loyalty effect is a `gift_loyalty` modifier on those entries;
the Style of Governance Boons carry `governance: true`; binding a familiar
grants every entry whose `granted_by` lists `familiar_bond` (True Friend); and
`covenant_expense` is worded by the registry like any other type.

## 6. Data Shape (illustrative)

The actual field-by-field shape lives in the dataclasses in
[`ars_magica_manager/models/`](ars_magica_manager/models/) — that's the
source of truth; treat any example here as a sketch of the *relationships*,
not a spec. Roughly: a `Saga` holds `Covenant`, `Character`, `Laboratory`,
`Book` and `Spell` records plus the shared catalogs, cross-referenced by id
(`covenant_id`, `owner_id`, `spell_id`, ...) rather than nested — see §4 for
which entity owns which relationship.

## 7. Roadmap

**Phase 0 — Scaffolding**
- Repo structure, `pyproject.toml`, `uv` setup, dataclasses for all entities
  above, JSON load/save layer, empty Textual app shell.

**Phase 1 — Core tracker**
- CRUD + browsing for Saga → Covenant → Character/Laboratory/Library/Book,
  with all relationships navigable (e.g. from a Covenant, see its
  characters, labs, and library; from a Character, jump to their lab).
- Virtue/Flaw catalog with structured `modifiers` (stored, displayed, not
  yet computed against).
- Spells as data, linkable from a character's known-spells list or a
  Lab Text book.

**Phase 2 — Rules Engine**
- A rules engine that applies the ArM5 formulas consistently across the app,
  so Phase 3 can automate seasons, XP and lab work: Lab, Casting,
  Spontaneous and Study totals, scores from XP, dice, derived character
  values, aura and realm modifiers, Penetration and Magic Resistance, spell
  levels, combat, certamen and Mystery initiation totals. Formulas consume
  Phase-1 modifier data; computed totals are displayed on sheets. Optional
  rules are saga settings, off by default.
- Builds from the local rules reference `reference/rules-engine-reference.md`
  (compiled from the Ars Magica open content, organised by what the engine
  computes, every rule cited; not committed).

**Phase 3 — Seasonal activity execution and long-term events**
- Run a season: Study (from a book, a teacher, or practice), Lab Activities
  (invent spells, enchant items, extract vis, longevity ritual). Apply
  results (XP, aging, new items/spells) back onto character/lab/covenant
  state. Season log, similar in spirit to Solo's.
- Aging rolls, warping, decrepitude, longevity ritual effects over time
  (first planned as Phase 4; merged into Phase 3 on 2026-09-29, since the
  Winter aging roll runs in the same season step).
- Execution plan: `reference/phase-3-plan.md` (not committed), shaped by
  `reference/phase-3-goals.md`. Decided: each character's season is a
  `SeasonPlan` the user locks in (magi on the lab Planning tab, everyone
  else on the character sheet or the covenant Seasons tab); advancing
  works out every plan's outcome from the saga as it stood before the
  season, then applies them all, so a season's results never change that
  same season; outcomes are written to the character's (and lab's,
  covenant's) Diary; the saga file is backed up just before applying.
  Seasons are planned for magi, companions and Mythic Companions; grogs
  get a yearly update instead.

**Phase 4 — Creation workflows**
- Create covenants, laboratories and characters by the book. A new record
  starts In Creation (existing records are In Play); a Creation Worksheet
  walks through the book's steps with a progress widget and its budgets
  (Virtues and Flaws, Characteristics, childhood and later-life xp,
  apprenticeship, years past Gauntlet; a covenant's Build Points), and
  moving the record to In Play puts the values on its sheet.
- Rule breaks warn by default; a saga setting enforces them strictly. A
  book's "should" is advice, never blocking. 2.0.0 ships when this phase
  is done. Plan: `reference/feat-13-plan.md` (not committed).

**Phase 5 — The Saga World**
- The world outside the covenant: Tribunals and their meetings (Hold
  Tribunal, resumable, with its debate, vote, rulings, minutes and Acta),
  neighbours (lords, towns, the Church, universities, factions, threats)
  with an attitude toward each player covenant, places and regiones,
  sketch covenants and characters (a detail level on the existing
  records, never a separate type), what's coming (Ahead) and a yearly
  step that proposes changes for the storyguide to tick, and covenant
  arms. Both front-ends; forms are `form_spec` fields as everywhere else.
- Decided: each Tribunal's customs are a package of their own, never
  mixed; the Definitive Edition rule is the default and a supplement's
  version a Rule Option; nothing outside the covenant changes unless the
  storyguide ticks it, and every automatic change is a diary entry that
  can be deleted to undo it. One migration: a covenant's free-text
  Tribunal becomes a Tribunal record.
- Spec: the "Saga World: data and forms spec" Claude Doc; mockups in the
  project's shared files (`saga-modules/mockups/`). FEAT-17 in the
  kanban. 3.0.0 ships when this phase and the desktop's parity with
  the terminal are both done (decided 2026-10-14). Shipped 2026-10-22.

**Phase 6+ — Polish / open-ended**
- Character sheet export/printing, multi-saga management UI, possible
  data-bridge with Ars-Magica-Solo, house-rule/customization hooks
  (mirroring Solo's `config.json` + CSV table pattern).

## 8. Open Questions (deferred, not blocking)

- History/audit trail for lab ownership changes, character covenant moves,
  etc. — not needed until someone actually asks "who owned this lab in
  1215?"

Settled since first written: combat stats are sheet data (Soak,
per-weapon Init/Attack/Defense/Damage and Load, and armor Protection and
Load are recorded, combat isn't resolved; choosing a weapon or armor
Material from the book's tables fills its figures in, still editable);
covenants use the Covenants chapter's Boons & Hooks with points plus a
calculated Economics tab; familiars have the full bond mechanics (cords,
bond powers).

## 9. UI Conventions

Every sheet follows the same conventions so the app behaves the same wherever
a GM is looking. Full detail (behaviour, implementation notes, known
pitfalls, and the exact Economics/Loyalty/Books/Spells rules) lives in
[`reference/UI_Conventions.md`](reference/UI_Conventions.md); this section is
just the standing decisions.

- **Selectable lists with a details panel** are the standard way to show,
  edit and remove a sheet's list items (rows carry a chosen/unchosen marker,
  `a`/`e`/`A` add/edit/delete the chosen row, delete always confirms). Applied
  on every sheet. Each tab has **one** details panel (`DetailsPanel`), docked
  at the bottom below the part that scrolls, always 12 rows (longer text
  scrolls inside it); its hint reads "Select a … to see its details."
- **Section titles** carry the list's figure: `(n of m)` where there's a
  limit (Specializations, Features); `(X pts)` on the two sides of a
  balance -- a character's Virtues/Flaws in `$text-success` when they match
  and `$text-error` when they don't, Boons/Hooks the same except plain
  while the Boons cost less than the Hooks provide; plain `(X pts)` on a
  lab's or familiar's Virtues/Flaws (no balance rule: the lab's capacity
  has its own warning); a plain `(n)` count on other lists; nothing on
  Abilities, Raw Vis or calculated sections. Book titles don't show Build
  Points.
- **Build Points show in one place: the covenant's Build tab** (a row per
  kind of resource, Initial as the covenant started and Current as it
  stands). A book shows its cost only while its covenant is In Creation; a
  laboratory's Build Points are worked out (Size x 20 plus its Virtues),
  never typed.
- Side-by-side lists sit 2 columns apart and side-by-side blocks of text 4
  apart, set once in `TwoColumns`/`StackingColumns`; column headings above a
  list are a `TableHeader`. Sheets target a 140x60 terminal (checked at
  120x45); 80x24 is not a target for sheets.
- Every collapsible sheet section starts **expanded**; a sheet's
  always-visible summary sits above its tabs and stays visible across tabs.
- Add/edit dialogs are a config-driven `FieldsDialog` (one row per field,
  validated on Save, fits 120×45) rather than bespoke screens per dialog.
- **In Creation / In Play** (Phase 4): the top panel of every covenant,
  laboratory and character sheet has, beside Edit, a button labelled with
  the record's mode; it changes only when pressed (or from More) and asks
  first. While In Creation the panel also offers the **Creation
  Worksheet**, a dialog listing the book's steps (each marked ✔ / ✘ / ☞ /
  ○) with the chosen step's budget, checks and buttons; the buttons open
  the sheet's own dialogs, so the worksheet edits the real record. Checks
  are pass, warn (a book "must") or advice (a "should"); only the saga's
  strict-creation option lets a warning stop the move to In Play.
- Anything derivable from the rest of a sheet (covenant Economics, Loyalty,
  book costs) is **calculated on demand and never stored** — only what the
  user actually types is saved.
- User-written text goes through shared escaping/emphasis helpers
  (`ars_magica_manager/markup.py`) rather than each screen handling it
  separately, so bracketed names and `**bold**`-style emphasis are safe and
  consistent everywhere.
- **Help** (STORY-115): `?` (F1 while typing in a dialog) opens one Help
  screen on the help for what has focus: the section, its tab, the sheet or
  view, or a process dialog's own page. The text is Markdown in
  `ars_magica_manager/help/`, a page per tab with a paragraph per section,
  saying what it's for and what is typed versus worked out; the "keys
  here" line is generated from the footer. Every tab and section must have
  help (`tests/test_help.py`). Rules text stays in the details panel.
- **Colour comes only from the active theme.** Text that needs to stand out
  uses the theme's text variables in markup: `$text-error` for problems,
  deficits and penalties, `$text-success` for met targets and bonuses
  (`$text-warning` for caution, `$text-muted`/`[dim]` for secondary text).
  Each theme computes these to be legible on its own background, so they
  beat hand-picked `$error-lighten-1`-style shades. Zero or neutral values
  stay plain. Named (`[red]`) and hex colours appear only in `themes.py`;
  `tests/test_theme_colours.py` enforces it. Signed numbers keep their
  leading `+` (`+0`, `+2`).

