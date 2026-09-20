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
  "id": "vf_gifted_researcher",
  "name": "Gifted Researcher",
  "type": "Virtue",
  "category": "Hermetic",
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

## 9. UI Conventions

Conventions that every sheet follows, so the app behaves the same wherever a
GM is looking.

### 9.1 Selectable lists with a details panel

The standard way to show, edit and remove the items of a list on a sheet
(covenant Boons, Hooks and Reputations first; other lists adopt it as their
screens are reworked). It replaces the older "static text plus a picker that
asks *which one?*" style.

**Behaviour**

1. **Rows are selectable.** Each row carries a selector: a dim `○`, or a blue
   bold `●` on the chosen row. At most one row is chosen at a time — including
   across two lists that sit side by side (choosing in one unchooses the
   other). Nothing is chosen when a sheet opens.
2. **A details panel sits under the list(s)** and fills in as a row is chosen.
   For catalog items it shows the name (with any user detail), its **Type**
   (the book's category, e.g. Site or Fortifications), its **Tier** (Minor Boon,
   Major Hook, Free Boon...), notes such as prerequisites and exclusions, the user's own **Description** if
   they wrote one, and then the official **Rules** text — the user's words
   always come before the rulebook's. The user's Description supports inline
   emphasis (`**bold**`, `*italic*`, `***both***`) so labels such as
   "Accessible Value:" can stand out; the official Rules text is shown as
   written. Until something is chosen it invites a
   choice. *The panel is for items with content beyond their label*: a list
   whose entries are only a name and a number (covenant Reputations) has no
   panel, because it would only repeat the row.
3. **`e` edits the chosen row and `A` deletes it.** Neither asks *which one?*
   when a row is chosen. Only a choice in the section being acted on counts:
   with nothing chosen there (or the choice is in the other list) the keys fall
   back to a picker, so they never silently do nothing.
4. **Deleting always confirms**: `Delete <name>?` with Yes / No. `y` and `n`
   answer directly, Escape means No, and No is focused by default so a stray
   Enter cannot delete anything.
5. **`a` adds.** Catalog-backed lists open a searchable picker (entries already
   taken are marked, never hidden or blocked — a covenant can have two
   Edifices — and prerequisites/exclusions are shown as notes only, consistent
   with the tracker-first principle). Picking an entry opens one dialog for its
   optional one-line **Detail** (shown in the list) and multi-line
   **Description** (shown in the panel), both blank by default. Freeform lists
   (Reputations) open their add dialog directly.
6. Section titles may carry totals or status, coloured by a rule the sheet
   states (Boons vs Hooks points: cyan while Boons < Hooks, red when
   Boons > Hooks, green when equal).

**Data.** The user's own text is stored with the attached entry, never in the
shared catalog: for covenant Boons/Hooks, `VirtueFlawInstance.params["detail"]`
and `params["description"]`, each present only when non-empty.

**Implementation.**

- `SelectableList` (an `OptionList`) owns the rows, the selector markers, the
  disabled "(none recorded)" placeholder, and the choice. A sheet gives it
  `(data index, label)` rows and reacts to its `Chosen` message. The data index
  is the entry's position in the sheet's own data list and is the row's id, so
  a filtered list still maps back to the true entry.
- Each sheet has one *entries* accessor per list that is the single source of
  truth for what the rows show, and one rebuild method that refreshes
  everything depending on the data (all lists, titles, the panel).
- `e`/`A` are dispatched through the section that contains the focused list
  (the generic `a`/`A`/`e` keys), with the selection
  read from the list; deletion goes through the reusable `ConfirmScreen`.
- All user text placed into markup (row labels, panel text, confirm messages)
  is escaped with `screens.escape()` — Textual's own `escape()` misses
  capitalised `[Tags]`.
- **Inline emphasis** in user-written descriptions goes through
  `screens.markdown_inline()`, which converts `**bold**`, `*italic*` and
  `***both***` (nesting works) to Textual markup and escapes everything else,
  so it is safe for any user text. Rules: an asterisk run opens emphasis only if
  the next character is not whitespace and closes only if the previous one is
  not (so `5 * 3` stays literal); unmatched runs and runs of four or more stay
  literal; `\*` is a literal asterisk; emphasis never spans a blank line. It is
  deliberately just emphasis — no headings, lists or links. Any dialog with a
  description field hints at the syntax ("Supports **bold** and *italic*."), and
  any new user-written description field should use the same function (it is
  applied to Boon/Hook Descriptions and the covenant Description).

**Pitfalls that shaped the implementation** (each was hit and fixed; keep them
fixed):

- `OptionList(*options)` highlights its first row on construction, so lists
  are built empty and filled with `add_options()`; nothing is chosen until the
  user chooses.
- The default OptionList highlight bar would hide the `●` and its `:focus`
  style re-adds a border, so `SelectableList` neutralises both (compact, no
  border, transparent bar, bold text for the chosen row).
- Use OptionList's synchronous `clear_options()`/`add_options()`; a `ListView`
  needs awaited clears and produced duplicate-id errors on refresh.
- Textual compares a label's *text* only, so changing just its colour does not
  repaint it (a Hooks total staying green after turning red). Titles whose
  colour can change without their text changing must be re-set explicitly.
- Dialogs: a bare `Horizontal` defaults to `1fr` and stretches an auto-height
  dialog to the whole window, so every dialog's button row gets an id and
  `height: auto`. Dialogs must also fit an 80×24 terminal.
- A dialog's result callback runs a moment *after* the screen switches back, so
  tests wait for the resulting state instead of assuming it.
- Refresh methods tolerate the sheet having just been replaced.

**Testing.** Drive the real key flow (open the sheet, focus the list, choose a
row, press `e`/`A`), and assert on rendered style and region, not only on
strings: marker moves and single choice; panel content and order; `e` opens the
edit dialog directly, pre-filled; `A` confirms (No/Escape keep, Yes deletes
exactly the chosen row, Enter on the default No is safe); the picker fallback;
blank optional fields store nothing; bracketed user text survives; emphasis
renders as bold/italic *spans* while literal asterisks and the official Rules
text do not; dialogs fit
80×24 *and* do not stretch on a tall terminal.

**Adoption.** Applied to covenant Boons, Hooks and Reputations, and to every list on
the covenant Inhabitants and Possessions tabs. Character
Abilities, Virtues & Flaws, Personality Traits, Reputations, Inventory, Raw
Vis and Spells, and the laboratory's lists (Virtues & Flaws, Specialties,
Features, Rooms, Raw Vis, Items, Diary), still use the older picker style and
remove without confirming; they move over as their screens are reworked.

### 9.2 Related sheet conventions

- Every collapsible sheet section starts **expanded** (`SheetSection`).
- A sheet's always-visible summary (laboratory Identity/Characteristics,
  covenant info panel) sits above its tabs in a non-collapsible
  `PinnedCollapsible`, and stays visible whichever tab is open.
- Rows that are *listed* from another sheet (Magi and Companions from character
  sheets, sanctums from laboratories) show that sheet's data live. Removing a
  listed person from the Inhabitants tab (`A`, with a confirmation that says so)
  marks a covenant-side record `departed`: they stop being listed and counted,
  but their character sheet still shows them as belonging to the covenant — so a
  magus who dies is still part of the covenant's history. A laboratory listed as
  a sanctum cannot be removed from the Possessions tab (move the laboratory to
  another covenant instead).
- New sheets are checked by rendering them (regions and a screenshot), not by
  tests alone, and at more than one terminal size.

### 9.3 Forms

Add/edit dialogs that are just a stack of fields use the config-driven
`FieldsDialog`: one compact row per `DialogField` (text, whole number, optional
number, dropdown, checkbox, multi-line area, or read-only info), validated on
Save. Its field list scrolls when the terminal is short but the title, error line
and Save/Cancel never leave the screen, so every form fits 80×24; it must also
not stretch on a tall terminal (test both). Read-only "info" rows show values that
come from elsewhere (a name taken from a character sheet, a governance type
provided by a Boon, a calculated total) so nothing that isn't editable *looks*
editable. Description fields in forms carry the emphasis hint (see 9.1).

Text helpers shared by the UI and pure-logic modules (`escape`,
`markdown_inline`) live in `ars_magica_manager/markup.py`; logic that needs no UI
(what each Inhabitants list shows, headcounts, totals, row and panel text) lives
in `ars_magica_manager/inhabitants.py` so it can be tested without a terminal.
