# Ars Magica Manager

A GM-facing tool for tracking **Ars Magica 5th Edition** characters,
covenants, laboratories, and libraries, and the relationships between them
(who belongs to which covenant, who works in which lab, who's read which
book). See [DESIGN.md](DESIGN.md) for the full design and roadmap.

This is a companion to, but does not depend on,
[Ars-Magica-Solo](../Ars-Magica-Solo), which handles solo-play session
mechanics.

## What it does

Phases 1 to 4 of DESIGN.md's roadmap are built; work now is ongoing
improvements. Per saga, the app keeps:

- **Covenants** — Boons & Hooks, Covenant Situations, Reputations,
  Inhabitants and Loyalty, Possessions, Economics (income, expenditure,
  savings, the yearly close), a Library, the seasons of its vis sources
  and income (Contested and Dwindling Resources included), a Diary, and
  where its Build Points went.
- **Characters** — the full sheet: Characteristics, Abilities, Virtues &
  Flaws, Arts, Raw Vis, spells with Mastery, inventory and combat figures,
  Soak, Confidence and True Faith, Personality Traits, Reputations, aging,
  Warping, wounds and fatigue, books and a Diary.
- **Laboratories** — Virtues & Flaws, Features and a Focus, the
  Specializations they add up to, Rooms, Raw Vis, Equipment & Stores, Lab
  Texts, enchanted devices, the owner's Lab Totals, and a Diary.
- **Familiars** — bond, cords and bond powers.
- **Books** and **spells** — the published spell catalog, the saga's own
  spells, CSV import, and which sourcebooks are in play.

The rules are worked out for you: Lab, Casting, Spontaneous and Study
totals, scores from xp, dice, derived values, auras, Penetration and Magic
Resistance, spell levels, combat, certamen and Mystery initiations, with
optional rules as saga settings.

**Seasons.** Each character's season is planned (study, teaching, lab
work, inventing spells, enchanting, Longevity Rituals, familiars, writing
and copying books, experimentation and original research, and the
supplements' activities), then the season is advanced: every plan's
result is worked out and applied, with Winter's aging rolls and Warping,
the grogs' yearly update and the covenant's seasons. The saga is backed up
first, and each season's results go into a record and the Diaries.

**Creation.** New covenants, laboratories and characters can be built by
the book: a Creation Worksheet walks through the steps and their budgets,
starting from a Character Template if you like, then moves the record
into play.

**Sharing a saga.** The storyguide can host a saga so players use it from
their own computers, in a browser or over SSH (`tools/serve.py`). Players
sign in, change only what is theirs, and see each other's changes as they
happen. Help (F1, or `?`) explains whatever has focus and has how-to guides,
including one on hosting.

Also: user-made catalog entries (house rules), export and import of
covenants, laboratories and characters, and light and dark Scriptorum
themes.

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
uv run python tools/serve.py --ssh-port 2222  # host the app for players
```

### Where your data is kept

Your sagas, their backups, exports and the app's settings are kept in your
**save folder**, which the saga picker shows under the list of sagas. To
use another one, press `m` (More) on the saga picker and choose **Change
save folder**: pick the folder, and the app can move your saves there
(it never overwrites a file already in the new folder). It remembers the
choice in `location.json` in the app's config folder.

Some folders may not allow saving: system settings (on Windows,
Controlled folder access protects Documents and the Desktop), a read-only
folder or a sync service can refuse. The app checks it can save in a
folder before using it, and if the save folder ever can't be used when the
app starts, it uses another and says so.

The `ARS_MAGICA_MANAGER_DATA` environment variable, if set, chooses the
folder instead (the saga picker says so). Saves kept in the repo's `data/`
folder by older versions are moved to the save folder the first time the
app starts.

## Layout

- `main.py`, `ars_magica_manager/app.py` — the Textual app entry point.
- `ars_magica_manager/screens/` — every screen and widget, one module per
  layer, each importing only from those before it: `widgets` (bottom bar,
  selectable list, sections), `fields` (the modal-dialog base and the
  config-driven `FieldsDialog` form), `prompts` (confirmations and short
  forms), `pickers` (catalog and row pickers), `forms` (the records' form
  builders and the few bespoke forms), the `sheets` package (one module
  each for the Character, Laboratory, Familiar and Covenant sheets, their
  shared base, and the Book and Spell lists), the
  `workspace` package (navigation tree + sheet pane, and every action on
  the records: a base class plus one mixin module of actions per kind of
  record) and
  `saga_picker` (the start screen, and its About dialog on `?`).
- `ars_magica_manager/models/` — the dataclasses (Saga, Covenant,
  Character, Laboratory, Familiar, Book, Spell, Possession, Inhabitant,
  Economics, catalog entry types, ...) and their load-time migrations, one
  module per kind of record, all re-exported from `models`;
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
- `data/spell_catalog.json` — the published Hermetic spells, built by
  `tools/build_spell_catalog.py` from the Definitive Edition's spell chapter
  and Atlas Games' Grand Grimoire of Hermetic Spells (two PDFs kept in the
  local `reference/` folder; rerun with `uv run --group catalog`, which
  needs tesseract for the chapter's headings). It writes a review list of
  anything that needs a look.
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
