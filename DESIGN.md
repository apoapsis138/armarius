# Ars Magica Manager — Design Document

## 1. Overview

A GM-facing desktop tool for tracking the structural, "paperwork" side of an
*Ars Magica 5th Edition* saga: characters, covenants, laboratories, and
libraries, and the relationships between them (who lives where, who works in
which lab, who's read which book). It complements — but does not depend on —
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
     │    └─ assigned Laboratory   (0 or 1, magi only)
     ├─ Laboratory (n)
     │    ├─ owner: Character (0 or 1)
     │    └─ Virtue/Flaw instances (lab-specific, from catalog)
     └─ Library (0 or 1, or n if you split by building)
          └─ Book (n)
               ├─ type: Summa | Tractatus | Lab Text
               └─ if Lab Text: embodies a Spell

VirtueFlaw catalog (shared reference data, not per-saga)
Spell catalog / instances (a Spell can be "known" by a character and/or
  "embodied" in a Lab Text book)
```

Key relationship notes:
- A Character's `covenant_id` is nullable (not every character is attached
  to a covenant at all times).
- A Laboratory belongs to exactly one Covenant, and has at most one resident
  owner Character at a time, but ownership can change over time (track
  history later if needed — not v1).
- A Book's `subject` is either an Ability or an Art (matching what it
  teaches); a Lab Text additionally references a specific Spell.
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
tags**, not just flat descriptive text:

```json
{
  "id": "vf_affinity_with_art",
  "name": "Affinity with (Art)",
  "type": "Virtue",
  "category": "Hermetic",
  "cost": 1,
  "parameters": ["art"],
  "modifiers": [
    { "applies_to": "art_xp_gain", "target": "{art}", "multiplier": 1.5 }
  ]
},
{
  "id": "vf_superior_lab_equipment",
  "name": "Superior Lab Equipment",
  "type": "Virtue",
  "category": "General",
  "cost": 1,
  "modifiers": [
    { "applies_to": "lab_total", "amount": 3 }
  ]
}
```

- `applies_to` names a **Total** (`lab_total`, `casting_total`,
  `spontaneous_total`, `study_total`, `soak`, `aging_roll`, …) or a
  resource flow (`art_xp_gain`, `vis_extraction`, …).
- Modifiers on a Character instance and on that Character's assigned
  Laboratory instance both feed the same Total calculation.
- v1 stores and displays these tags but does **not** need every Total
  formula implemented — the schema just has to make "sum all modifiers
  tagged `lab_total` for this character + their lab" a trivial query once
  we build that engine, instead of a schema migration.

## 6. Data Shape (illustrative)

```json
{
  "saga": { "id": "saga_dammerstein", "name": "Dammerstein", "current_year": 1220, "current_season": "Spring" },
  "covenants": [
    { "id": "cov_1", "saga_id": "saga_dammerstein", "name": "...", "vis_stock": {}, "library_id": "lib_1" }
  ],
  "characters": [
    {
      "id": "char_1", "name": "Leandro", "type": "magus", "covenant_id": "cov_1",
      "characteristics": { "int": 3, "per": 1, "str": 0, "sta": 2, "pre": 0, "com": 1, "dex": 0, "qik": 0 },
      "arts": { "creo": 10, "intellego": 5, "... ": 0 },
      "abilities": [ { "name": "Magic Theory", "score": 5, "specialty": "Lab Totals" } ],
      "virtues_flaws": [ { "vf_id": "vf_affinity_with_art", "params": { "art": "creo" } } ],
      "spells_known": ["spell_1"],
      "assigned_lab_id": "lab_1"
    }
  ],
  "laboratories": [
    {
      "id": "lab_1", "covenant_id": "cov_1", "owner_id": "char_1", "size": 0,
      "aura": 3, "features": ["Superior Equipment"],
      "virtues_flaws": [ { "vf_id": "vf_superior_lab_equipment" } ]
    }
  ],
  "libraries": [ { "id": "lib_1", "covenant_id": "cov_1", "books": ["book_1"] } ],
  "books": [
    { "id": "book_1", "type": "Summa", "subject": "Magic Theory", "level": 8, "quality": 6, "author": "..." }
  ],
  "spells": [
    { "id": "spell_1", "name": "...", "technique": "Creo", "form": "Ignem", "level": 10 }
  ],
  "virtue_flaw_catalog": [ /* shared reference data, see §5 */ ]
}
```

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

- Do we ever need combat *stats* (Soak, weapon damage) recorded on a
  character sheet even without resolving combat? Likely yes eventually
  (it's sheet data) — revisit when Phase 1 character sheet fields are
  finalized.
- Covenant "build points"/resource-generation rules (boons/hooks, income)
  — model loosely now (free-form resources) or adopt the full Covenants
  chapter point-buy system? Leaning loose-now, revisit in a covenant-focused
  phase.
- Familiars: full familiar bond mechanics (Cord, Golden Cord virtues, etc.)
  or just "familiar: yes/no + notes" for v1?
- History/audit trail for lab ownership changes, character covenant moves,
  etc. — not needed until someone actually asks "who owned this lab in
  1215?"
