# Ars Magica Manager

A GM-facing tool for tracking **Ars Magica 5th Edition** characters,
covenants, laboratories, and libraries, and the relationships between them
(who belongs to which covenant, who works in which lab, who's read which
book). See [DESIGN.md](DESIGN.md) for the full design and roadmap.

This is a companion to, but does not depend on,
[Ars-Magica-Solo](../Ars-Magica-Solo), which handles solo-play session
mechanics.

## Status

Phase 1 (core tracker) is underway: you can create and browse sagas,
covenants, characters, and laboratories, and add Virtues/Flaws to a
character or lab from the shared catalog. Book/Spell creation and the
Ability picker aren't wired up yet — see DESIGN.md §7 for the roadmap.

## Getting started

Requires Python 3.14+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py    # launches the Textual TUI
uv run pytest            # run tests
uv run ruff check .      # lint
```

## Layout

- `ars_magica_manager/models.py` — dataclasses for Saga, Covenant,
  Character, Laboratory, Library, Book, Spell, and the Virtue/Flaw and
  Ability catalog entry types.
- `ars_magica_manager/storage.py` — JSON load/save, one file per saga
  under `data/sagas/` (git-ignored — that's campaign data, not source).
- `ars_magica_manager/catalog.py` — loads the shared Virtue/Flaw catalog
  (`data/virtue_flaw_catalog.json`) and Ability catalog
  (`data/ability_catalog.json`).
- `ars_magica_manager/screens.py` — the Textual TUI's screens: saga/
  covenant/character/laboratory creation and browsing, and the shared
  Virtue/Flaw picker.
- `ars_magica_manager/app.py` — the Textual app entry point.
- `data/virtue_flaw_catalog.json`, `data/ability_catalog.json` — seed
  catalog entries (a starting point, not exhaustive — cross-check and
  expand against the rulebook as you need more).
