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
- **One run at a time on a computer:** story_check's tests wait while
  another worktree's are running (it says whose), since runs sharing the
  cores stop at their time limit and flake. The lint and type checks
  don't wait. When several builders work at once (a spec's stories, see
  "Branches"), only single-test runs overlap (`uv run python -m pytest -p
  no:xdist tests/<file>.py::<test>`, which never waits); slice checks take
  turns through story_check; and the full suite runs once, on the
  integration branch, not per story. Run the suite only through
  story_check, never a bare `pytest -n auto`, which doesn't take the turn.
- **Before handing a change over:** `uv run python tools/story_check.py
  --full` runs the whole suite in parallel (`python -m pytest -q -n auto
  --dist worksteal`, one worker per core; more workers than cores make the
  Pilot tests time out). Both modes rerun each failure once alone, by its
  exact test id. One that fails again is real; one that passes alone is
  flaky, and **a flaky test fails the check too**: fix its waits (see
  "Textual and Pilot gotchas"). Flaky ones are named and added to
  `.pytest_cache/flaky_tests.txt`, the list still to fix.
- **pyright must report 0 errors.** It checks `ars_magica_manager/`,
  `tools/` and `main.py` in basic mode. Every parameter is annotated
  (`self`/`cls` aside); `reportMissingParameterType` is on.
- Then boot the app (`uv run python main.py`, `uv run python gui.py`), and
  for a UI change look at what it really draws (see "Seeing the screen").

**Every flake becomes a story the same day.** A flaky test is a bug in its
waits, not bad luck: the day one shows up, locally or in CI, it gets a
story of its own to find the cause and fix it. In CI
(`tools/ci_tests.py`) a failed test is run once more alone, sharing
story_check's rerun (`tools/rerun_once.py`): one that passes then keeps
the job green but is flagged as a "Flaky test" warning on the pull request
and in the job's summary, and one that fails again, or a collection or
setup error, fails the job.

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
action is one `MoreAction` entry in its area's module of `forms/more/`
(its letter and label, where it shows, when it's offered, its first step and
what it changes) plus its key in `registry.ORDER`. Don't bind a new letter.

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
numbers belong in commit messages and pull request titles or
descriptions, not in changelog fragments (they're for the user), code
comments or docstrings.

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

- `main` is the one long-lived branch, and it is always releasable.
  Branch from an up-to-date `main`, keep the branch short-lived (one
  change), and open a pull request into `main`. Never commit to `main`
  directly; it changes only through pull requests.
- **A spec's coupled stories share an integration branch.** When a spec's
  stories can't each merge into `main` alone and keep it green, the spec
  gets one short-lived integration branch from `main`, `spec-<topic>`,
  and one pull request into `main`; that branch counts as one change.
  Each of its stories is built on its own branch from the integration
  branch, `spec-<topic>-story-<n>`, in its own worktree, and merges back
  into it with a merge commit (never a rebase or a force push). Before the
  pull request opens, merge `main` into the integration branch and run the
  full suite there once (docs/adr/0033). A story outside such a spec keeps
  a branch and a pull request of its own. A story blocked by another waits
  until its blocker has merged: into `main`, or into the integration
  branch both share. Branches are never stacked.
- Whoever builds a change commits it, pushes its own branch and opens its
  pull request, once the checks above pass and both reviews are done (the
  bug review, and the Standards and Spec review against this file and the
  change's story and spec). Its description follows "Writing a pull
  request" below. Merging and releases stay with the maintainer. Never
  push to `main`, force-push, push a tag or delete a remote branch. (On
  the maintainer's computer a local guard hook, outside the repo, refuses
  those, and `reset --hard`, `clean -f` and `branch -D` too.)
- A release is a version tag on `main` (see "A release" and "Release
  rhythm" below). Its `release/X.Y.Z` branch is an ordinary short-lived
  one, gone once it merges; there is no long-lived release branch.
- The Checks workflow (`.github/workflows/checks.yml`) runs on Windows and
  Linux for every push and pull request to `main`: formatting, lint and
  pyright once per system, and the full suite split into four shards per
  system that run side by side (`pytest --shard=k/4`). Its last job,
  `checks`, passes only when every job that should run did; it is the one
  status to require in branch protection.
- A pull request that changes only docs (README.md, CONTRIBUTING.md,
  SECURITY.md, `docs/` outside `docs/screenshots/`,
  `.github/ISSUE_TEMPLATE/`, changelog fragments, `changelog.d/*.md`, and
  the walkthroughs PDF, `data/tutorials/*.pdf`; not the tutorial saves)
  gets lighter checks: formatting, lint and
  pyright as usual, and the fast tier (`-m "not ui"`) once per system in
  place of the sharded suite. NOTICE.md and the screenshots are left out
  because tests read NOTICE.md and the help site copies the screenshots.
  Pushes to `main` and runs by hand always run the full suite.
- The shards are balanced by each test file's running time, from
  `tools/test_durations.json`; a file not in it counts as a typical file of
  its tier. When the suite has changed a lot, measure it again (the steps
  are in `tools/shards.py`'s docstring) and commit the new file.

## Writing a pull request

Every pull request's description fills in
`.github/pull_request_template.md`, which GitHub puts in the box: Summary,
Evidence and Merge Danger, then an Armarius block of Story, Pattern, Rules,
Help, Changelog and Checks. Write "None" or "n/a" in a section that doesn't
apply; never leave one empty.

- **Summary**: what the change does, in a few sentences, with the smallest
  diagram that shows it (a mermaid flowchart, a before/after table), or
  none when words are enough.
- **Evidence**: before and after. What it did, what it does now, and how
  that was seen: a test, a probe's screen text, a screenshot.
- **Merge Danger**: is it a one-way door (a saved field renamed, a pack's
  ids changed: a revert won't undo it) or a two-way door (a revert puts
  everything back)? And its blast radius: which saves, screens, packs or
  seats it touches.
- **Story** (STORY-n), **Pattern** (the design pattern and why), **Rules**
  (book and printed page, errata too), **Help** (topics changed),
  **Changelog** (the fragment's file) and **Checks** (`story_check --full`'s
  count, and anything else run).

The description is about the change, not about who made it or how.
`tools/check_pr_body.py` checks it in the Checks workflow and again on
every edit (`.github/workflows/pr-description.yml`; branch protection
requires both `checks` and `pr-description`), and fails on:

- a missing heading or an empty section;
- first-person narration (I, I'm, I'd, me, my and the like);
- tool or agent names, outside code spans (the app's Agents are fine);
- attribution lines (Co-Authored-By and the like) anywhere: the repo's
  statement on AI use covers them;
- he, she and the like, as in screen text (quoted book text aside);
- a name in the repo's private `BLOCKED_NAMES` secret.

Run it before opening the pull request: `uv run python
tools/check_pr_body.py body.md`.

## Changelog and versioning

**With each change** add a fragment to `changelog.d/`, one file per
entry, and never edit CHANGELOG.md's versions by hand
(`changelog.d/README.md` has the details). Name it
`<slug>.<feature>.md`: a few lowercase words joined by hyphens, then the
feature's key from `[tool.towncrier]` in `pyproject.toml` (`glossa`,
`fundamenta`, `castellum`, ...), one per feature in CHANGELOG.md's
Features table. Write one paragraph in plain English for the user,
starting with a bold headline (`**A new guide.** ...`), at most 60 words,
with no bullet or heading: a release adds those. Don't change the
version. `tests/test_changelog.py` checks every fragment, and builds a
release from them to check that What's New, the release notes and the
site can read it. What's New shows released versions only. A security
fix is a fragment that starts with `**Security:**`: the app's App update
notice marks a Release with one as a security App update.

**The version** is `MAJOR.MINOR.PATCH`, set only in `pyproject.toml`, and
goes up once per release, by the largest change in it: a change that adds
or changes what the app does is MINOR; a fix, code-health, test or docs
change is PATCH. MAJOR marks a finished phase of the plan, when the maintainer says.

**A release**, in order (see "Release rhythm" for when):

1. From an up-to-date `main` (`git switch main`, `git pull`), run
   `uv run python tools/release.py X.Y.Z`. It refuses, changing nothing,
   unless the working tree is clean, HEAD is `origin/main`, the version is
   newer than `pyproject.toml`'s and `changelog.d/` has fragments. Then it
   makes the branch `release/X.Y.Z`, builds the fragments into CHANGELOG.md
   as `## X.Y.Z — YYYY-MM-DD` (`towncrier build`, which deletes them), sets
   the version in `pyproject.toml`, runs `uv lock` and the tests that hold
   the changelog and the version together (`tests/test_version.py`,
   `tests/test_changelog.py`, `tests/test_release_notes.py`). It never
   commits or pushes. (`uv run towncrier build --draft --version X.Y.Z`
   shows the section beforehand without writing it.)
2. Read the new section, then stage, commit and push as the script
   prints, and open the pull request into `main` from the link it gives.
   Merge it once the checks pass.
3. Tag the merge commit on `main` with the commands the script printed
   (`git tag -a vX.Y.Z -m "Armarius X.Y.Z"`, then push the tag). The tag
   builds the rest: the Release workflow (`.github/workflows/release.yml`)
   checks that the tag matches `pyproject.toml` and is on `main`, then
   publishes the GitHub Release with that version's section of
   CHANGELOG.md as its notes (`tools/release_notes.py`); the Image
   workflow publishes the container image; and the Pages workflow
   rebuilds the help site, so the site matches the latest release.

### Release rhythm

- **Weekly.** The maintainer releases on Sunday morning, US Eastern time.
  Whatever has merged into `main` by Saturday night ships in that release;
  a week with no fragments has no release.
- **Hotfixes any time.** An urgent fix ships as soon as it merges, as a
  PATCH release made the same way.
- **Every branch has a story** on the board, and the story moves to Done
  when its pull request merges.

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

### Settled and closed

Two moments in a screen's life decide when a test may act, and when the
app's own work must stop.

- **Settled.** Showing a tree node in the workspace builds its view, then
  gives it a first focus (a sheet does this when its first tab is
  announced), and that focus reaches the workspace a few message-loop turns
  later, rebuilding the Footer. Until then a key a test presses can go to
  the wrong section, and a focus the test sets can be taken back.
  The workspace's `detail_settled` turns true, and it posts
  `DetailSettled`, once that first focus has landed. In a test,
  `await settled(pilot, workspace)` (`tests/support.py`) waits for that and
  for the Footer to finish rebuilding: wait for it after choosing a node,
  before pressing keys, focusing a section or counting Footer rebuilds.
- **Closed.** A screen's async work (an awaiting `on_mount`, a worker, a
  `call_after_refresh`) can outlive the screen. Mark it `@while_open`
  (`tui/screens/closing.py`): a missing widget once the screen has closed
  ends the work quietly, and is still an error while it is open.
