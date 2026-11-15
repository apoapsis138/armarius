# Working on Armarius

The working rules for changing the code. [DESIGN.md](DESIGN.md) has the
architecture and the lasting decisions, and [docs/adr/](docs/adr/) why each
was made. Before building a desktop button or window, read DESIGN.md's "How
a desktop page runs a command".

## Checks

Tests run in two tiers.

- **While working:** `uv run python tools/story_check.py` runs the tests
  for what you changed, import sorting, `ruff format`, `ruff check` and
  `pyright` in one call. `tools/slice_tests.py --dry-run` lists which tests
  it picks: the fast tier (every test file that isn't a screen test) plus
  the screen tests matching the files changed since the last commit.
- **Before handing a change over:** `uv run python tools/story_check.py
  --full` runs the whole suite in parallel (`python -m pytest -q -n auto
  --dist worksteal`, one worker per core; more workers than cores make the
  Pilot tests time out). Both modes rerun each failure once alone and
  report it flaky or real (flaky ones are logged in
  `.pytest_cache/flaky_tests.txt`).
- **pyright must report 0 errors.** It checks `ars_magica_manager/`,
  `tools/` and `main.py` in basic mode. Every parameter is annotated
  (`self`/`cls` aside); `reportMissingParameterType` is on.
- Then boot the app (`uv run python main.py`, `uv run python gui.py`), and
  for a UI change look at what it really draws (see "Seeing the screen").

Tests are isolated per test (a temporary saga folder and settings path, and
conftest closes every Qt window a test leaves open), so parallel runs are
safe. Screen tests (Pilot or Qt; `tools/tiers.py` says which) are marked
`ui`, so `-m "not ui"` runs the fast tier alone. When a new source file's
name doesn't say which screen tests check it, add it to
`tools/slice_tests.py`'s `AREA_TESTS`.

Nearly all the suite's time is the screen tests building sheets and
dialogs; the rules and data tests take seconds. Keep a screen test to what
it checks: `screen_helpers._select*` open only the sheet asked for, on its
first tab (a test that reaches into a tab it never shows calls
`support.build_all_tabs`); a new list goes into `test_list_flows.py`'s
one-session-per-list cases. A check that scans every module or file is one
test whose message names each offender, not a parametrized case per file.

### Golden tests

- `tests/test_dispatch_matrix.py` records every sheet section x a / e / d /
  More / Filter: it fails if key routing changes.
- `tests/test_sheet_text.py` records every tab's rendered text at 140x70
  and 120x45, checks that refreshing every section changes nothing, and
  runs the Footer rebuild guard (`tests/footer_guard.py`).

After an *intended* change to either, regenerate both once, when the UI is
settled, with `uv run python tools/story_check.py --goldens` (it takes
about ten minutes), and review the diff of `tests/golden/`.

## Structure

**The core never imports a UI library.** Only the front-end packages may:
`tui/` (Textual, Rich, textual-serve, asyncssh) and `gui/` (PySide6, from
the `gui` dependency group). Everything else in `ars_magica_manager/` is the
shared core both use. `tests/test_core_boundary.py` fails if a core module
imports a UI library or a front-end module, or one front-end imports the
other, even inside a function. Logic a screen needs that isn't about
drawing belongs in the core (as with `form_spec.py` and `actions.py`). A new
core module goes in `LAYERS` in `tests/test_core_boundary.py`, in the
lowest layer whose modules are all it imports.

**The look lives in the app.** The palettes and bundled fonts are in
`style/`, with no UI library. The Textual themes and CSS are `tui/style.py`;
the desktop's ornaments, paper, gilding, window frame and page pieces are
`gui/style/`. A widget that knows Armarius's records stays in `gui/` proper.

**Forms and lists.** A new form is a `commands.Form` built in the core
`forms/` package (one module per kind of record or process), its fields
`form_spec.DialogField`s. A list's Add, Edit and Delete are a
`commands.SectionOps` registered in `section_verbs.py`. Both front-ends draw
them. The `tests/test_dialog_contracts_<area>.py` files drive each form by
its field labels (fits 120x45, prefill, cancel, each invalid entry, save,
and what the sheet shows after saving): add an entry there (and an opener
in `tests/dialog_openers.py`) for a new form, and a `test_list_flows.py`
case for a new list.

**Help.** A new sheet tab or section needs a help topic (its widget id) in
`ars_magica_manager/help/*.md`, and a new process dialog a `help_id` and a
page; `tests/test_help.py` fails otherwise. Help true of only one front-end
is marked for it (`; tui` or `; gui` after a topic's id, or lines between
`<!-- tui -->` and `<!-- /tui -->`); `help_text.py`'s docstring has the
rules. A change to how something works updates its help in the same change.

**Keys: one verb per key** (`a` add, `e` edit, `d` delete with a
confirmation; rare actions in More `m`, creation in New `n`). A new section
gets them from its entry in `actions.SECTION_VERBS` plus its handlers in
`_section_ops` (`tests/test_menu_items.py` checks the two agree); a new rare
action is a `MenuItem` in `actions.MORE_MENU` plus an `actions.available`
clause. Don't bind a new letter.

## Code rules

**No import inside a function to get round a cycle.** Move the shared code
down into the lower module, or pass it in as an argument. An import inside
a function is kept only to speed up start-up, with a comment saying so.

**Catch only the error you expect.** Name the narrowest exception the code
can really raise for a known reason (`OSError` reading a file, `ValueError`
parsing, `LookupError` for a record that's gone). Never catch
`AttributeError` or `TypeError` to mean "the data changed".
`tests/test_broad_catches.py` fails on either. Use `assert` only for values
the code made itself. Data coming in (a file, a pack, another computer)
goes through `shapes.py`, which refuses the wrong shape with a ValueError
naming the field: build a saga with `storage.saga_from_data`, a plain
record file with `shapes.build`, and a loosely typed number with
`shapes.whole` / `shapes.real`.

**A saved dict gets a type.** A record kept as a dict gets a `TypedDict`
describing its keys. Values are converted and checked once, when a saga is
loaded or a pack imported, with a message naming the record.

**Renaming or moving a saved field breaks existing saves.** Add a load-time
migration, or use `models.known_fields()` to filter a stale dict to the
dataclass's current fields.

**Look for an existing helper before writing one** (a season as a number,
an Ability's score by name, finding a record by id or name). Helpers shared
by the Tribunal packs go in `book_packs/builder.py`.

**User data** (sagas, backups, exports, settings) lives in
`paths.data_dir()`. Tests and probe scripts must never touch it: the
conftest fixtures point it at the test's temporary folder. Ask
`paths.data_dir()` each time; never cache a path from it in a module
constant.

**Comments** state the rule or design choice plainly. Story and bug
numbers belong in commit messages and the CHANGELOG, not in code.

**No generative-AI art.** Every image, icon, symbol, texture or font the
app ships or draws is either drawn in code or taken from a source under a
free licence, with its licence file beside it and a credit in
[NOTICE.md](NOTICE.md).

## Rules and the books

A rule or game system is built from the books: the *Ars Magica Definitive
Edition* first, then the supplements that extend it, with the Definitive
Edition winning wherever they disagree, and the official errata over both.
Cite book and printed page in the module's `SOURCE` and the commit message.
Summarize a rule with its page; don't copy the books' text. Packs hold only
what the books print: never invent lists or figures to fill a gap.

## Performance rules

- Call `refresh_bindings()` only when the available keys can actually
  change, never from handlers that fire constantly (focus, row highlight,
  every tab activation).
- Guard with counts, not timings: the guard tests count Footer recomposes
  per action and widgets mounted per sheet. Raise a budget only
  deliberately.
- For a change that adds a sheet, tab or list, run
  `uv run python tools/perf_probe.py` (add `--scale 10` for list-heavy
  screens) before and after.
- Read a file once per flow, and pass the data along.

## Branches

- Branch from `dev`, and open pull requests into `dev`.
- Never commit to `main`. It is the default branch and always the latest
  release, and it changes only through a release pull request from `dev`,
  when the maintainer calls a release.
- The Checks workflow (`.github/workflows/checks.yml`) runs on Windows and
  Linux for every push and pull request to `dev` and `main`: formatting,
  lint and pyright once per system, and the full suite split into four
  shards per system that run side by side (`pytest --shard=k/4`). Its last
  job, `checks`, passes only when every other job did; it is the one status
  to require in branch protection.
- The shards are balanced by each test file's running time, from
  `tools/test_durations.json`; a file not in it counts as a typical file of
  its tier. When the suite has changed a lot, measure it again (the steps
  are in `tools/shards.py`'s docstring) and commit the new file.

## Changelog and versioning

**With each change** add its lines under `## Unreleased` at the top of
CHANGELOG.md (above the newest version; start the section if it isn't
there), in plain English for the user, each entry under a `### Feature`
heading naming one of the Features table's features. Don't change the
version. `tests/test_changelog.py` holds the Unreleased section to the
same rules as a version's, and fails if it isn't the first section above
the newest version. What's New shows it as Unreleased (in development).

**The version** is `MAJOR.MINOR.PATCH`, set only in `pyproject.toml`, and
goes up once per release, by the largest change in it: a change that adds
or changes what the app does is MINOR; a fix, code-health, test or docs
change is PATCH. MAJOR marks a finished phase of the plan, when the maintainer says.

**A release**, in order:

1. On `dev`, one commit: rename `## Unreleased` to
   `## X.Y.Z — YYYY-MM-DD`, set the version in `pyproject.toml`, and run
   `uv lock`. `tests/test_version.py` checks that the newest version
   heading is the one `pyproject.toml` names.
2. Open a pull request from `dev` into `main`, and merge it once the
   checks pass.
3. Tag the merge on `main`: `git tag -a vX.Y.Z -m "..."` and push the tag.
   The Release workflow (`.github/workflows/release.yml`) checks that the
   tag matches `pyproject.toml` and is on `main`, then publishes the GitHub
   Release with that version's section of CHANGELOG.md as its notes
   (`tools/release_notes.py`).

An urgent fix is just a small PATCH release made the same way: fix it on
`dev`, then release.

## Seeing the screen

Passing tests don't prove a layout is right. For a layout change, look at
it:

- **Text dump:** a throwaway probe script starts with `import probe_kit`
  (`tools/probe_kit.py`; its docstring has the API and a demo). It keeps
  the probe silent and on a throwaway copy of a saga, and writes the screen
  as text. Check 140x60 and 120x45.
- **SVG:** run the screen with `App.run_test(size=(140, 70))` and
  `app.save_screenshot(...)` for colour and pixel questions.

## Textual and Pilot gotchas

- A bare `Horizontal()`/`Vertical()` with no explicit size defaults to
  `1fr`, which breaks an ancestor's `width: auto`/`height: auto`. Give
  layout-bearing containers explicit `width: auto; height: auto;`.
- `Input` is three lines high by default; budget for it in dense dialogs.
- `ListView.clear()`/`append()`/`extend()` and `remove_children()` must be
  awaited before mounting same-id replacements, or you get `DuplicateIds`.
- `Collapsible.can_focus` is False; only `CollapsibleTitle` focuses. Use
  `widgets.section_of(app.focused)` to find the section and
  `section.focus_section()` to focus one, also in tests.
- A view whose first tab is a flat tab (no Collapsible inside) leaves the
  top panel's Collapsibles focused across a plain tab switch. Pass an
  `initial` flag through a `_focus_first_section()`-style helper: on first
  display fall back to the top panel; on a real switch focus the tab's
  first stop, or `self.screen.set_focus(None)` when it has none.
- `pilot.click(selector)` needs the target on screen. Prefer
  `widget.press()` or setting `.index` directly.
- Under load a bare `pilot.pause()` can be not quite enough, and a fixed
  extra delay only makes the failure rarer. Poll for the real condition
  (a `_wait_until(pilot, condition)` helper) at the lowest shared call site.
