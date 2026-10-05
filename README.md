# Ars Magica Manager

A GM-facing tool for tracking **Ars Magica 5th Edition** characters,
covenants, laboratories, and libraries, and the relationships between them
(who belongs to which covenant, who works in which lab, who's read which
book). See [DESIGN.md](DESIGN.md) for the full design and roadmap.

This is a companion to, but does not depend on,
[Ars-Magica-Solo](../Ars-Magica-Solo), which handles solo-play session
mechanics.

## Status

Phase 1 (core tracker) is mostly built. You can create and browse sagas
(with a saga calendar and an edit screen) and keep, per saga:

- **Covenants** — info panel, Boons & Hooks, Reputations, Inhabitants and
  Loyalty, Possessions, Economics (income, expenditure, savings, the yearly
  close) and a Library tab.
- **Characters** — the full sheet: identity, Characteristics, Abilities,
  Virtues & Flaws, Arts, Raw Vis, known spells with Mastery, inventory,
  combat figures (filled in from the book's weapon and armor tables) and
  Soak, Confidence, Personality Traits, Reputations,
  aging, wounds and fatigue, and books.
- **Laboratories** — Virtues & Flaws (with their effect on the lab's
  Characteristics), Features and a Focus, the Specializations they add up
  to, Rooms, Raw Vis, Equipment & Stores, books and a Diary.
- **Familiars** — bond mechanics, cords and bond powers.
- **Books** (owned by a covenant, lab or character, with CSV import) and
  **spells** (the published catalog, the saga's own spells and CSV import).

The app has light and dark Scriptorum themes; the one you pick is
remembered.

Not built yet: enchanted devices, the Rules Engine (Phase 2) and running
seasons (Phase 3) — see DESIGN.md §7.

The current version is in the title bar; [CHANGELOG.md](CHANGELOG.md) lists
what changed in each one.

## Getting started

Requires Python 3.14+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py                         # launches the Textual TUI
uv run pytest -q -n 16 --dist worksteal       # run tests in parallel (~1.5 min)
uv run ruff check . && uv run ruff format .   # lint and format
uv run pyright                                # type-check
```

### Where your data is kept

Your sagas, their backups, exports and the app's settings are kept in
**Ars Magica Manager** at the top of your OneDrive folder, wherever OneDrive
is on that computer (without OneDrive: in your app data folder, e.g.
`~/Library/Application Support/Ars Magica Manager` on a Mac). Saves kept in
the repo's `data/` folder by older versions are moved there the first time
the app starts.

To keep them somewhere else, either set the `ARS_MAGICA_MANAGER_DATA`
environment variable to a folder, or create `location.json` in the app's
config folder (`%LOCALAPPDATA%\Ars Magica Manager` on Windows) holding
`{"data_dir": "D:/Somewhere/Ars Magica"}`. Move the existing files there
yourself first: the app only moves them out of the repo.

If the folder can't be created or written to, the app keeps using the
repo's `data/` folder (or, with no saves there, its app data folder) and
says so when it starts. On Windows the usual cause is **Controlled folder
access** (Windows Security, Ransomware protection), which stops Python
from writing in protected folders such as Documents: choose a folder
outside them as above, or allow `python.exe` there.

## Layout

- `main.py`, `ars_magica_manager/app.py` — the Textual app entry point.
- `ars_magica_manager/screens/` — every screen and widget, one module per
  layer, each importing only from those before it: `widgets` (bottom bar,
  selectable list, sections), `fields` (the modal-dialog base and the
  config-driven `FieldsDialog` form), `prompts` (confirmations and short
  forms), `pickers` (catalog and row pickers), `forms` (the records' form
  builders and the few bespoke forms), `sheets` (the Character, Laboratory,
  Familiar and Covenant sheets and the Book and Spell lists), the
  `workspace` package (navigation tree + sheet pane, and every action on
  the records: a base class plus one mixin module of actions per kind of
  record) and
  `saga_picker` (the start screen, and its About dialog on `?`).
- `ars_magica_manager/models.py` — the dataclasses (Saga, Covenant,
  Character, Laboratory, Familiar, Book, Spell, Possession, Inhabitant,
  Economics, catalog entry types, ...) and their load-time migrations;
  `arts.py` — the fifteen Arts.
- Domain logic, one module per area, with no widgets in them:
  `books.py`, `spells.py` (where a spell id resolves, magnitude, the
  "CrIg 20" shorthand, R/D/T), `economics.py`, `inhabitants.py` (and
  Loyalty), `possessions.py`, `familiars.py`, `laboratories.py` and
  `covenants.py` (rules computed from a lab's or covenant's Virtues/
  Boons), `creation.py` (new sagas and records), `sheet_text.py` (text
  shared by the Character and Familiar sheets), `csv_import.py`.
- `ars_magica_manager/catalog.py` — loads the shared catalogs in `data/`
  (Virtues & Flaws, laboratory Virtues & Flaws, laboratory Features,
  Abilities, Houses, covenant Boons & Hooks, spells, weapons & armor);
  `totals.py` — the registry of modifier types the catalogs' effects are
  checked against.
- `ars_magica_manager/storage.py` — JSON load/save, one file per saga in
  the user's data folder (`paths.py`, see above), never in the repo;
  `settings.py` — app settings (the chosen theme).
- `ars_magica_manager/markup.py` — escaping and `**bold**`/`*italic*` for
  user-written text; `themes.py` — the Scriptorum light/dark themes.
- `data/spell_catalog.json` — the published Hermetic spells, built from
  Project: Redcap's [Grand Grimoire](https://www.redcap.org/page/The_Grand_Grimoire)
  by `tools/build_spell_catalog.py` (rerun it to refresh; it prints a report
  of anything that needs a look).
- `data/*_catalog.json` — the other catalogs (a starting point, not
  exhaustive — cross-check and expand against the rulebook as you need more).
  Each is `{"attribution": ..., "entries": [...]}` (spells and Features
  name their list), and the attribution must end with Atlas Games' line
  (see below).

## Licence and credits

Ars Magica Manager is free software under the GNU General Public License
v3.0 (see [LICENSE](LICENSE)). The Ars Magica rules text in its
catalogs (`data/`) and code is adapted from material licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/):

> Based on the material for Ars Magica, ©1993–2024, licensed by Trident,
> Inc. d/b/a Atlas Games®, under Creative Commons Attribution-ShareAlike 4.0
> International license 4.0 ("CC-BY-SA 4.0").

This is an unofficial fan project, not endorsed by Atlas Games or Paradox
Interactive. See [NOTICE.md](NOTICE.md) for sources, changes made and
trademark notices.
