# Ars Magica Manager — Design Document

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
- Stay a single-user, GM-facing tool (no auth, no sharing/sync).

**Non-Goals (for now)**
- Combat resolution (initiative, attack/damage rolls, wound tracking as a
  live subsystem).
- Bestiary content/management.
- Realm mechanics (Divine/Faerie/Infernal/Magical auras, Twilight *content*
  generation, supernatural interactions) beyond a character or lab simply
  recording an aura rating or a realm-related Virtue/Flaw.
- Story/Saga narrative tooling (that's Solo's domain).
- Multi-user/troupe sharing.

**Scoping principle:** if it's a field on a Character, Covenant, or
Laboratory sheet, it's in scope, even if we don't yet compute anything from
it. Subsystems that aren't really "sheet data" (combat resolution, bestiary,
realm lore) are deferred until there's a reason to pull them in.

## 3. Tech Stack

- **Python 3.14+**, managed with `uv` (mirrors Ars-Magica-Solo).
- **Textual** for the TUI. Consistent with Solo, keyboard-driven, no web
  server needed.
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
     ├─ Character (n)   [magus | companion | grog]
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
  [specific Art]").

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
splits them into formats the Totals Engine would have to reconcile.

**Staged migration.** Rather than converting everything at once, each catalog
moves to the shared shape when a real calculation needs it:
- Character Virtues & Flaws: already in this shape (effects not yet filled in).
- Covenant Boons & Hooks: **converted** -- `covenant_aura` (the Aura Boon / Weak
  Aura Hook) and `covenant_expense` / `buildings` (the Buildings surcharge),
  collected by `models.covenant_modifiers()`.
- Laboratory Virtues & Flaws: still the older `characteristic_modifiers` map
  (`{"safety": 1}`); convert when the Totals Engine starts, since that's when lab
  Characteristics feed Lab Totals (board: STORY-804).
- Still to settle then: how flat amounts and multipliers combine when both apply.

**Known exceptions in the code today** (predating this decision; each should
move onto its catalog entry when its calculation is next touched):
`inhabitants.py` picks the Gentle/Blatant Gift Loyalty modifier by the ids
`vf_gentle_gift`/`vf_blatant_gift`; `models.GOVERNANCE_STYLE_IDS` lists the
governance Boons/Hooks by id; binding a Familiar grants `vf_true_friend` by id
(`familiars.bind_familiar`); and `totals.describe_modifier` words `covenant_expense`
specially.

## 6. Data Shape (illustrative)

The actual field-by-field shape lives in the dataclasses in
[`ars_magica_manager/models.py`](ars_magica_manager/models.py) — that's the
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

**Phase 2 — Totals engine**
- Implement Lab Total, Casting Total, Spontaneous Total, Study Total
  formulas that consume Phase-1 modifier data. Display computed totals on
  sheets.

**Phase 3 — Seasonal activity execution**
- Run a season: Study (from a book, a teacher, or practice), Lab Activities
  (invent spells, enchant items, extract vis, longevity ritual). Apply
  results (XP, aging, new items/spells) back onto character/lab/covenant
  state. Season log, similar in spirit to Solo's.

**Phase 4 — Long-Term Events**
- Aging rolls, warping, decrepitude, longevity ritual effects over time.

**Phase 5+ — Polish / open-ended**
- Character sheet export/printing, multi-saga management UI, possible
  data-bridge with Ars-Magica-Solo, house-rule/customization hooks
  (mirroring Solo's `config.json` + CSV table pattern).

## 8. Open Questions (deferred, not blocking)

- History/audit trail for lab ownership changes, character covenant moves,
  etc. — not needed until someone actually asks "who owned this lab in
  1215?"

Settled since first written: combat stats are sheet data (Soak and
per-weapon Init/Attack/Defense/Damage are recorded, combat isn't resolved);
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
  across the Covenant and Character sheets; the Laboratory sheet's lists
  still use an older picker style (STORY-303).
- Every collapsible sheet section starts **expanded**; a sheet's
  always-visible summary sits above its tabs and stays visible across tabs.
- Add/edit dialogs are a config-driven `FieldsDialog` (one row per field,
  validated on Save, fits 80×24) rather than bespoke screens per dialog.
- Anything derivable from the rest of a sheet (covenant Economics, Loyalty,
  book costs) is **calculated on demand and never stored** — only what the
  user actually types is saved.
- User-written text goes through shared escaping/emphasis helpers
  (`ars_magica_manager/markup.py`) rather than each screen handling it
  separately, so bracketed names and `**bold**`-style emphasis are safe and
  consistent everywhere.

