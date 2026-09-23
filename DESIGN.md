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
     └─ Library tab: every Book kept in the covenant (see below)

Book (n per saga)
 ├─ type: Art Summa | Ability Summa | Tractatus | Lab Text | Casting Tablet | Other
 └─ owner: the Covenant, a Laboratory, a Character -- or none (files under the saga)

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
- A Book has a single owner (`owner_kind` + `owner_id`): a covenant, a
  laboratory or a character, or none. There is no separate Library record:
  a covenant's Library tab lists the books it owns plus those owned by its
  laboratories and characters; a laboratory's Inventory and a character's
  sheet list their own; books with no owner (or one that no longer exists)
  appear under "Unassigned Books" in the saga tree. A Summa or Tractatus is
  on an Art or an Ability; a Lab Text or Casting Tablet records a spell by
  name and level (spells aren't linked yet). See 9.5 for costs.
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

## 6. Data Shape (illustrative)

```json
{
  "saga": { "id": "saga_dammerstein", "name": "Dammerstein", "current_year": 1220, "current_season": "Spring" },
  "covenants": [
    { "id": "cov_1", "saga_id": "saga_dammerstein", "name": "...", "vis_stock": {} }
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
  "books": [
    { "id": "book_1", "name": "...", "type": "Ability Summa", "ability": "Magic Theory",
      "level": 8, "quality": 6, "language": "Latin", "author": "...",
      "owner_kind": "covenant", "owner_id": "cov_1", "year_published": null, "description": "" }
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

When fields depend on each other while the form is open, `FieldsDialog` stays
the tool: a field's `show_if` hides it until the other values call for it
(hidden fields are neither checked nor returned), and the dialog's `live`
callback fills a line above the error with something computed from the current
values. The book form uses both: the Type picks which of Art/Ability/Spell,
Level and Quality appear, and the live line shows the Build Point cost and any
covenant-creation limit warning before saving.

### 9.4 Calculated figures (covenant Economics and Loyalty)

Anything that can be worked out from the rest of the sheet is **calculated on
demand and never stored**; only what the user types is saved
(`Covenant.economics`: income sources, Wealth, Tithes / Inflation / Sundry,
Magic and Emergency Savings, and Notes; `Covenant.loyalty`: Governance (unless
a Boon provides it), Equipment/Money *choices* (not their points), Pension,
Familiarity, Actions and Events, Magical Influence). The rules live in
`ars_magica_manager/economics.py` and `ars_magica_manager/inhabitants.py` (no
UI) and follow `reference/Economics.md` / `reference/Loyalty.md`. Every screen
that shows a figure re-derives it after an edit anywhere on the covenant
sheet, keeping the chosen row chosen. Every computed money/points figure is a
whole number, rounded **away from zero** (`models.round_away_from_zero`: 2.4
→ 3, -2.4 → -3 -- plain `ceil` would soften a negative figure instead of
rounding it up). The one exception the rules call out explicitly: a common
craftsperson's `1 + Ability // 2` keeps its floor division.

**The "inhabitant" kind is the Other Covenfolk list** (`KIND_TITLES["inhabitant"]`;
the paper sheet's Dependents/Servants/Teamsters/Laborers, all in one list, each
entry tagged with a required Covenant Role -- `OTHER_COVENFOLK_ROLES` in
models.py: Laborer, Servant, Teamster, Dependent, distinct from `COVENANT_ROLES`
which is Companions'/Specialists' admin roles). `inhabitants.other_covenfolk_count(
saga, covenant, role)` sums the quantities tagged with a role -- what the
Inhabitants summary's Teamsters/Servants/Laborers counts are read from (no
longer typed fields on `Population`; only `other_people` still is, since it has
no list of its own behind it). An entry's row shows its Role unless the Role is
redundant with the Name (e.g. a "Servants" entry tagged Servant), and only shows
Year Born when Quantity is 1 (a group has no one shared birth year).
**Livestock are tracked but never counted** -- not in `total_inhabitants`, and
already 0 points in `INHABITANT_POINTS`; the book doesn't consider them
inhabitants at all.

**Points and Yearly Expenditure** (`economics.py`, `inhabitant_points` lives
in `inhabitants.py` since the Inhabitants tab's own minimums need it too --
see below):
- **Points of Inhabitants**: each list's headcount times its kind's points (Magus
  5/10, Companion 3/5, Specialist and Craftsperson 2/3, Turb and Other Covenfolk
  1/2, Horse 1, Livestock 0 and never counted; the covenant's Covenant Season
  picks Spring/Winter or Summer/Autumn), plus Other People at 1/2 (the one
  figure with no list behind it).
- **Points of Laboratories**: for each sanctum, its laboratory's Upkeep total (a
  manual sanctum: the Upkeep typed on it) through the book's Upkeep-to-points table
  (beyond +5: 5 x n x (n + 1)), times its Usage (Light 0.5, Standard 1, Heavy 1.5).
- **Points of Weapons and Armor**: each weapon or armor entry's Type and Quality from
  the book's table, times its Quantity.
- **Minimum Servants / Teamsters** (shown as the second number of the
  Inhabitants tab's "actual / needed" pairs, coloured green when met, red
  otherwise): 2 Servants per 10 points of inhabitants excluding Other Covenfolk
  tagged Servant, Laborer or Teamster; 1 Teamster per 10 points excluding
  Laborer/Teamster-tagged entries, minus 2 per Laborer.
- **Yearly Expenditure**: Buildings 1 per 10 points of inhabitants, plus 2 / 5 per
  Minor / Major Boon that adds to the size, magnificence or quantity of the
  covenant's buildings or fortifications (Artillery, Curtain Walls and Mural Towers,
  Edifice, Important Building, Shell Keep, Tower Keep; each instance counts, and the
  amounts live on the Boons as `covenant_expense`/`buildings` modifiers, see 5.1);
  Consumables 2,
  Provisions 5, Wages 2 times the salary multiplier (Loyalty > Money: none 0, half
  0.5, standard 1, generous 1.5, lavish 2), Laboratories 1 per 10 lab points, Weapons
  1 per 320, Writing Materials 1 per magus and Books craftsperson; Tithes, Inflation
  and Sundry are typed (Sundry defaults to, and should stay at, at least 1). Total
  Expenditure is the total before savings minus all savings.
- **Cost Savings** -- the book's actual four categories, no more: Laborers 1 each
  (at most half of Provisions); Craftspeople 1 + Ability/2 each (rare: the Ability),
  where each *craft* (same linked Ability, else same Responsibility, else each person
  alone) saves at most 50% or 20% of its category, and a category never saves more
  than it costs; Magic Savings is a typed pounds-saved number (items give 1/magnitude
  and Rituals ~5/magnitude, so the user works out the total by hand and enters it).
- **Wealth, deficits and Emergency Savings** -- an operation, not a formula.
  Wealth is typed by the user and also grows at the **end of the year**: advancing
  Winter to Spring adds each covenant's surplus to its Wealth and starts the new
  year's Emergency Savings at 0 (a deficit takes nothing from Wealth by itself). With
  a deficit, the Emergency Savings row shows in red "Covenant operating at a
  deficit", or "Covenant is broke - see rulebook for narrative and mechanical
  consequences" when Wealth can't cover it. Editing that row then first asks "Do you
  wish to draw from Wealth to cover the deficit?": Yes moves the deficit (or all the
  Wealth there is, if less) from Wealth into Emergency Savings -- *added* to any
  Emergency Savings already there, so what leaves Wealth always equals what arrives;
  No opens the ordinary form, where the figure can still be typed. A deficit is never
  taken from Wealth automatically: covering it is the user's choice (other ways, such
  as cutting pay or equipment, will affect Loyalty). Advancing Winter to Spring with
  any covenant in deficit first asks "The Covenant is currently in a deficit - do you
  wish to attempt to resolve this?": Yes (focused; also Escape) keeps the date so the
  books can be balanced, No advances regardless. Broke has no further consequences
  yet.
- Not modelled yet: income scaling by magus count (see "Saga-level options" below).

**Improving a source of income** (`economics.py`: `income_multiplier_text`,
`projected_income`, `improvement_note`; `screens.ImproveIncomeScreen`, key `i`
on the Sources of Income section) is a manual stand-in for the book's yearly
automated advancement, which isn't built. It applies one year's Income
Modification at a time: pick an Effect (Slump x0.5, Contraction x0.8,
Stagnation x0.95, Status Quo x1, Growth x1.05, Expansion x1.2, Boom x1.5 --
`INCOME_EFFECTS`/`INCOME_EFFECT_MULTIPLIERS` in models.py), see the resulting
Multiplier and Projected Income (Current Income x Multiplier, rounded) update
live as the Effect changes, then Commit asks to confirm before setting
`IncomeSource.income` to the projected value (permanent, like the book
describes) and replacing `IncomeSource.note` with a generated sentence naming
the year, source, effect and the income change (a distinct wording for Status
Quo, since nothing changed). The Note is shown at the end of the source's row
and before its Description in the details panel.

**Loyalty** (`inhabitants.py`): Base Loyalty is the average, across the
covenant's magi, of each one's Gift modifier (Gentle Gift or no Gift: 0; The
Gift: -30; Blatant Gift: -105) -- read from a sheet-linked magus's
Virtues/Flaws (`vf_gentle_gift`/`vf_blatant_gift`; anything else assumes The
Gift), or from a manual magus's own Gift choice (blank also assumes The
Gift). Total Modifiers sums: Living Conditions (10 x the covenant's Living
Conditions (Mundane) -- covenfolk are mundane, so Living Conditions (Magi)
doesn't apply here), Equipment and Money (fixed point tables keyed by their
selects, Money +10 more with Pension on), Specialists (every Companion/
Specialist holding Steward/Chamberlain/Turb Captain/Autocrat earns Presence +
a role-specific Ability -- Leadership for Turb Captain, Profession: Steward /
Profession: Chamberlain for the others, Autocrat gets both -- read from a
linked character sheet, or typed manually with no sheet), Familiarity,
Reputation (-5 per point of every *known* bad covenant Reputation --
Reputations can be marked "known by the covenant" or not), Actions and
Events, and Magical Influence. Current Loyalty Points = Base + Total
Modifiers; Prevailing Loyalty Score comes from a fixed cumulative table (the
same shape as Ability Advancement, symmetric for a negative total, clamped
beyond ±105/±6 since the reference doesn't extend it further). **Individual
inhabitants do not have a Loyalty score** -- only the covenant does; an
earlier per-`Inhabitant` `loyalty` field was removed because nothing read it
and it has no basis in the rules.

**Saga-level options** (not built): Economics.md scales a Typical/Lesser
income source's usual annual income by how many magi the covenant has
(±15/±6 pounds per magus over/under 6), which is a real rule but the first
one that's really a *per-saga house-rule toggle* rather than something always
true. Rather than hard-code it, this is a placeholder for a future "saga-level
options" concept -- settings decided once per saga (not per covenant) that
individual formulas would consult, the same way `covenant_season` already
picks a column of a table. Revisit when a second such toggle shows up.

### 9.5 Books and the Library tab

A book's Build Point cost (for creating a covenant) is calculated, never
stored: Art Summa Level + Quality; Ability Summa Quality + 3 x Level; Tractatus
Quality; Lab Text 1 per 5 levels of its spell and Casting Tablet 2 per 5, both
rounded up with the same rule as 9.4; Other books cost nothing. The
covenant-creation limits (Art Summa level 20 and quality 11 + (20 - level),
Ability Summa level 8 and quality 11 + 3 x (8 - level), both capped at 22;
Tractatus quality 11) only **warn**, since books found in play may exceed them.
Lab Text and Casting Tablet level limits aren't checked yet (their power-level
table hasn't been provided).

The Library tab has a read-only Summary section in two columns (left: Summae
and Tractatus, each with its Ability/Art split; right: Lab Texts, Casting
Tablets, Other, Total Books and Total Cost) above one list of every book in the
covenant, which stretches down to two rows above the details panel (its Subject
column -- the Art, Ability or spell -- widens to use spare room, 17 to 40
characters), (Name, Type, Art/Ability/Spell, Level, Quality,
Location: "Covenant Library", "Lab: <name>" or the owning character), and a
details panel listing every field and the cost. The same list widget
(`BookListView`) is used, inline, for a laboratory's and a character's Books
section, and for the saga's Unassigned Books node. A new book starts owned by
wherever it's added from.

**Importing books from CSV.** `I` on the saga opens *Import Data* (Characters,
Covenants and Laboratories are listed greyed out for later; only Books works),
then a small file explorer that starts in the folder the app runs in. `I` on a
covenant's Library tab goes straight to the explorer. The file needs a header
row with at least `name` and `type`; the other columns read are `language`,
`author`, `year_published`, `description`, `art`, `ability`, `level`, `quality`,
`tractatus_type` and `spell` (any case or order). Types may be plural ("Art
Summae"), Arts may be abbreviated ("Ig"). A preview confirms before anything is
added: the count, rows that will be skipped and why, duplicate names, unknown
abilities and books over the creation limits. Then each book whose name is
already taken (in the saga, or earlier in the same file) asks **Duplicate /
Duplicate All / Skip / Skip All** (Skip is focused; Escape skips). The file's
`owner` and `cost` columns are not used: a saga import leaves every book
unassigned, a Library import gives them all to that covenant, and cost is
always calculated.

**Unknown abilities.** An Ability summa or tractatus whose Ability isn't in the
ability catalog (matched regardless of case; a templated family like "Area Lore:
Rhine" counts as known) is kept as typed, but its row shows in red and its panel
leads with "Unknown ability: ...", prompting the user to pick a real one. Study
from books will rely on it.

**Several books at once.** Book lists are multi-select: Space (or Ctrl+click)
puts a green check on a row, and the section title counts the marked ones.
With books marked, `A` deletes them all after "Are you sure you want to delete N
books?", and `e` changes only their owner (a one-field form, then "Changing
ownership of N books to ..."). With nothing marked, `e`/`A` act on the chosen
book as usual. `SelectableList(multi=True)` provides this; other lists are
unchanged.

Text helpers shared by the UI and pure-logic modules (`escape`,
`markdown_inline`) live in `ars_magica_manager/markup.py`; logic that needs no UI
(what each Inhabitants list shows, headcounts, totals, row and panel text, all of
Loyalty and the shared Inhabitant-points math) lives in
`ars_magica_manager/inhabitants.py` so it can be tested without a terminal.

### 9.6 Spells

**Where spells live.** One `Spell` shape, three homes, one id namespace:
- the shared, read-only **catalog** (`data/spell_catalog.json`): the published
  spells, built from Project: Redcap's Grand Grimoire by
  `tools/build_spell_catalog.py` -- the core rules plus five supplements, each spell
  tagged with its `source` (for a future "sources allowed" saga option);
- the saga's **own spells** (`Saga.spells`): added by hand or imported;
- a magus's **invented spells** (`Character.invented_spells`): they stay with the
  magus, not the catalog (making one available to the saga is a backlog story).
`spells.find_spell()` resolves an id from any of them, in that order, so a known
spell or a Lab Text can point at any spell. (A Lab Text is what a magus produces
when inventing a spell, which is why it must be able to link an invented one.)

**The record.** Name, Technique, Form, `level` (None for a **General** spell, cast
at any level: the Aegis of the Hearth, the Wards), requisites (Techniques or
Forms), Range / Duration / Target (the standard values, or a supplement's own,
kept as written), Ritual, base level, description, source, and `details_missing`
for catalog entries the page lists without details. Magnitude (level / 5, rounded
up, at least 1), the shorthand ("CrIg 20", "Mu(Re)Te 15": a requisite follows the
Art it qualifies), a Ritual's vis (a pawn per magnitude) and casting time (15
minutes per magnitude) are worked out, never stored. Spell Mastery belongs to the
magus's known-spell record, not the spell (with the Character screen rework).

**The Spells view.** A **Spells (n)** node under the saga lists the catalog and the
saga's own spells (Name, Arts, Level, Range/Duration/Target, Ritual, Source) over a
details panel, the two sharing the height 2:1. A filter bar narrows it as you type:
a search over name and description (every word must match, any case), Technique
and Form (either also matches a requisite), Ritual, Source (a book, or "the saga's
own"), and a level range (General spells pass any range); the section title reads
"Spells (n of N)". `a`/`e`/`A` add, edit and delete the saga's own spells;
catalog spells are read-only. The spell form's Range/Duration/Target offer the
standard values plus "Other..." for a supplement's own, and a live line shows the
shorthand, magnitude and, for a Ritual, its vis and casting time.

**Building the catalog.** The page's index is the authority for a spell's level: it
matches the Base + magnitudes arithmetic for 371 spells, while an entry's own
"Level N" line almost never does (it belongs to a variant it describes). Index
links and headings are matched by anchor, then name, then close spelling; entries
with no section are kept as details-missing; a heading missing from the index gets
its level from its Base line. The script prints what it couldn't place.

## 10. Backlog (not scheduled)

Wanted, but not pressing; pick up when convenient.

- **Tidy up where things can be created.** Too many screens offer to create
  records: `c` (New Character) and `l` (New Laboratory) work from every screen of
  the workspace -- any tree node, any sheet, any tab -- because `check_action`
  allows them everywhere. Decide the few sensible places to create each kind of
  record (e.g. a character from the saga, its covenant, or a Characters group;
  a laboratory from Laboratories groups) and remove the rest, keeping creation
  easy to find.
- **User-made catalog entries, per saga.** Let the user create their own Boons,
  Hooks, laboratory Virtues & Flaws and character Virtues & Flaws at saga level
  (house rules, entries from other books), alongside the shared catalogs. They'd
  carry effects in the same `Modifier` shape as everything else (5.1).
