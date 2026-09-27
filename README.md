# Ars Magica Manager

A GM-facing tool for tracking **Ars Magica 5th Edition** characters,
covenants, laboratories, and libraries, and the relationships between them
(who belongs to which covenant, who works in which lab, who's read which
book). See [DESIGN.md](DESIGN.md) for the full design and roadmap.

This is a companion to, but does not depend on,
[Ars-Magica-Solo](../Ars-Magica-Solo), which handles solo-play session
mechanics.

## Status

Phase 1 (core tracker) is mostly built. You can create and browse sagas and
keep, per saga:

- **Covenants** — info panel, Boons & Hooks, Reputations, Inhabitants and
  Loyalty, Possessions, Economics (income, expenditure, savings, the yearly
  close) and a Library tab.
- **Characters** — the full sheet: identity, Characteristics, Abilities,
  Virtues & Flaws, Arts, Raw Vis, known spells with Mastery, inventory,
  Personality Traits, Reputations, aging, wounds and fatigue, and books.
- **Laboratories** and **Familiars** (bond mechanics, cords, bond powers).
- **Books** (owned by a covenant, lab or character, with CSV import) and
  **spells** (the published catalog, the saga's own spells and CSV import).

Not built yet: deleting characters, labs and covenants, the covenant Diary,
the Totals engine (Phase 2) and running seasons (Phase 3) — see DESIGN.md §7.

## Getting started

Requires Python 3.14+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py                         # launches the Textual TUI
uv run pytest -q -n 16 --dist worksteal       # run tests in parallel (~1 min)
uv run ruff check . && uv run ruff format .   # lint and format
uv run pyright                                # type-check
```

## Layout

- `main.py`, `ars_magica_manager/app.py` — the Textual app entry point.
- `ars_magica_manager/screens/` — every screen and widget, one module per
  layer, each importing only from those before it: `widgets` (bottom bar,
  selectable list, sections), `fields` (the modal-dialog base and the
  config-driven `FieldsDialog` form), `prompts` (confirmations and short
  forms), `pickers` (catalog and row pickers), `forms` (the records' form
  builders and the few bespoke forms), `sheets` (the Character, Laboratory,
  Familiar and Covenant sheets and the Book and Spell lists), `workspace`
  (navigation tree + sheet pane, and every action on the records) and
  `saga_picker` (the start screen).
- `ars_magica_manager/models.py` — the dataclasses (Saga, Covenant,
  Character, Laboratory, Familiar, Book, Spell, Possession, Inhabitant,
  Economics, catalog entry types, ...) and their load-time migrations.
- Domain logic, one module per area, with no widgets in them:
  `books.py`, `spells.py` (where a spell id resolves, magnitude, the
  "CrIg 20" shorthand, R/D/T), `economics.py`, `inhabitants.py` (and
  Loyalty), `possessions.py`, `familiars.py`.
- `ars_magica_manager/catalog.py` — loads the shared catalogs in `data/`
  (Virtues & Flaws, laboratory Virtues & Flaws, Abilities, Houses, covenant
  Boons & Hooks, spells); `totals.py` — the registry of modifier types the
  catalogs' effects are checked against.
- `ars_magica_manager/storage.py` — JSON load/save, one file per saga under
  `data/sagas/` (git-ignored — that's campaign data, not source);
  `settings.py` — app settings (the chosen theme).
- `ars_magica_manager/markup.py` — escaping and `**bold**`/`*italic*` for
  user-written text; `themes.py` — the Scriptorum light/dark themes.
- `data/spell_catalog.json` — the published Hermetic spells, built from
  Project: Redcap's [Grand Grimoire](https://www.redcap.org/page/The_Grand_Grimoire)
  by `tools/build_spell_catalog.py` (rerun it to refresh; it prints a report
  of anything that needs a look).
- `data/*_catalog.json` — the other catalogs (a starting point, not
  exhaustive — cross-check and expand against the rulebook as you need more).
