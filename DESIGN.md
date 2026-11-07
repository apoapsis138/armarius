# Armarius — Design

How the app is built and the decisions that shape it. What it does, by
feature and version, is in [CHANGELOG.md](CHANGELOG.md); how to install and
run it is in [README.md](README.md); the working rules for changing it are
in [CLAUDE.md](CLAUDE.md). Why each lasting choice was made is in
[docs/adr/](docs/adr/), one short record per decision.

## 1. What it is

A storyguide's tool for the paperwork of an *Ars Magica 5th Edition* saga:
characters, covenants, laboratories, familiars, books and spells and the
links between them; the seasons they spend; creating them by the book; and
the world around them (Tribunals, neighbours, places, threats, what lies
ahead). The storyguide can host it for the troupe: players open the same
saga in a browser or over SSH, from the storyguide's computer.

**Principles**

- **Sheet data first, then the rules on it.** Anything on a sheet is in
  scope; a rule is built when a sheet or a season needs its figure.
- **Store what is typed, work out the rest.** Scores come from xp, totals
  from modifiers, Economics and Loyalty from the covenant; none is saved.
- **The Definitive Edition wins.** A supplement's rule applies only while
  its book is in play for the saga, and a different version of a core rule
  is an optional rule, off by default. Every rule cites book and page.
- **Nothing changes unasked.** A season or a year proposes; the storyguide
  ticks what happens, and each change is a diary entry that can be undone.

## 2. Architecture: one core, two front-ends

```
          tui/  (Textual, Rich, textual-serve, asyncssh)
          gui/  (PySide6)
             |  draw sheets, forms, lists; bind keys, buttons, menus
             v
  core:  sheets/  forms/ + form_spec  actions + commands  grids/tables
             |
         rules/  seasons/  world_turns  catalogs  packs  tribunal_packages
             |
         models/  storage + merge  paths  settings
```

**Pattern: Ports and Adapters (hexagonal).** Everything outside `tui/` and
`gui/` is the core, and the core never imports a UI library. Each
front-end is an adapter that draws what the core describes: a sheet as
rows (`sheets/`), a form as fields (`form_spec`), a list as cells
(`grids`), what can be done where (`actions`). This is why the desktop
reached parity with the terminal without a second copy of the rules, and
why a third front-end would only draw. `tests/test_core_boundary.py`
enforces the line, including that neither front-end imports the other.

| Package | What lives there |
| --- | --- |
| `models/` | The dataclasses, one module per kind of record, and their load-time migrations |
| `rules/` | The Rules Engine: pure functions for the book's arithmetic, one module per area, each citing its sources |
| `seasons/` | Season plans and advancing the season |
| `sheets/` | What each sheet shows, as facts and rows |
| `forms/` | The forms and commands behind each sheet's buttons and keys |
| `book_packs/`, `packs.py` | The Tribunal and region books as importable packs |
| `tribunal_packages/` | Each Tribunal's customs |
| `help/` | The help, as Markdown pages keyed by widget id |
| `tui/` | The terminal app, its screens (`tui/screens/`), themes, and the hosting server |
| `gui/` | The desktop app, its pages, artwork and printing |
| `data/` | The shared catalogs (`*_catalog.json`) and the shipped packs (`packs/`) |
| `tools/` | Catalog and pack builders, the host launcher, the perf probe, the test slicer |

## 3. Design patterns in use

- **Strategy, as a registry: seasonal activities.** `rules/activities.ACTIVITIES`
  maps each activity's key to an `Activity` (who may plan it, its group, its
  book, whether it is lab work); `outcome()` looks the plan's activity up
  and works out what it gives. A new activity is a new entry, not a new
  branch in the season code. In Python a Strategy registry is just a dict
  of records and functions; no class hierarchy is needed.
- **Strategy, again: Tribunal customs.** `tribunal_packages.PACKAGES`
  registers each Tribunal's package (its book, notice period, roster
  columns, extra tabs and forms). A package's data sits under its own key
  in `Tribunal.package_data`, so switching package hides it and switching
  back finds it.
- **Declarative forms.** A form is a list of `form_spec.DialogField`s built
  by a `_*_fields` function; parsing and required-field rules live in
  `form_spec`. Each front-end's `FieldsDialog` draws the same list, so a
  form is written once and the contract tests drive it by its labels.
- **Command, as a chain of steps.** `commands.py` turns a button into steps
  the user answers: `Form`, `Choose`, `Confirm`, `ChooseFile`, or `Act`.
  Answering runs `apply`, which changes the saga and returns the next step
  (or notes, `Then`, `Go`, `Refuse`). A front-end only runs the steps,
  saves and redraws.
- **Dispatch table: section verbs.** `actions.SECTION_VERBS` says which of
  add / edit / delete each section supports, and `section_verbs.py` says
  what they do: a plain dict of builders keyed by the record's type (a
  Strategy; Python needs no class for it) gives, per record, each sheet
  section's id and its `SectionOps` (the three commands). Both front-ends
  read it, so a key or button does the same in the terminal and on the
  desktop. A key looks its section up instead of branching on it, which
  keeps "one verb per key" true everywhere; `tests/test_dispatch_matrix.py`
  is the golden record. A list whose rows count into what its sheet has
  chosen (Mystery Cults' cult, the Spells list's filters, a Tribunal's
  argument) is given by the sheet itself (`state_ops`), ahead of the table.
  Edit and Delete rows are the section's own list index, except Virtues and
  Flaws and Boons and Hooks, whose core rows count within a side or kind
  (`section_verbs.table_row`); `section_verbs.refreshed` says what else a
  change redraws.
- **Data-driven content: packs.** A Tribunal or region book is built in
  code once (`book_packs/<book>/`, with the shared `Builder`), written to
  `data/packs/*.amm.json`, and imported like any export. Importing matches
  records by name, so a pack can be imported again without doubling. The
  app has no code per book beyond its builder and its Tribunal package.
- **One effect model (Interpreter over data).** Catalog entries carry their
  effects as data; see section 5.
- **Facade: hosting.** `hosting.HOST` starts and stops the player server as
  a separate process, so neither front-end knows how the server is built.
- **Composite: the widget tree.** Sheets are tabs of collapsible sections
  of lists, each part drawn and focused the same way.

## 4. Data

- **One JSON file per saga**, human-readable, in `paths.data_dir()` (by
  default `Armarius` at the top of OneDrive), never in the repo. Records
  are flat lists linked by id (`covenant_id`, `owner_id`, `spell_id`),
  not nested; the dataclasses in `models/` are the field-by-field spec.
- **Migrations run on load**, so old saves, exports and packs keep
  working; a renamed or moved field needs one. A save from a newer version
  keeps the fields this one doesn't know.
- **Saving merges.** When the app is hosted, each player's copy saves
  through a three-way merge (`merge.py`) against the file, record by
  record, so two people changing different things both keep them.
- **Backups**: the saga is backed up just before a season is applied.
- **Exports and packs** are small sagas of the same format (`transfer.py`),
  so importing one runs the same migrations.
- **Catalogs** are shared reference data in `data/`, each entry citing its
  `source` book(s). A saga chooses its books in play
  (`Saga.books_in_play`) and may add its own entries and sources
  (`house_rules.py`).

Ownership at a glance:

```
Saga
 ├─ Tribunals ── member covenants, meetings, cases (package customs)
 ├─ Covenants ── laboratories, inhabitants, Boons & Hooks, diary
 ├─ Characters (magus | companion | Mythic Companion | grog)
 │     Virtues & Flaws, Abilities, Arts, spells, familiar, season plans
 ├─ Books (owned by a covenant, laboratory, character, or none)
 ├─ Spells, enchanted devices
 └─ World: neighbours, places, threats, Ahead, the world's turns
```

A Book has one owner, and there is no separate Library record: a
covenant's Library lists its books and those of its laboratories and
characters. Scores are derived from stored xp (`rules/xp.py`).

## 5. Effects: one modifier model (decided, don't re-open)

Every catalog that can change a number (character Virtues & Flaws,
laboratory Virtues & Flaws, covenant Boons & Hooks, user-made entries)
carries its effects as `Modifier`s: `applies_to`, `amount` or
`multiplier`, and optionally `target` and `activity`. `totals.py` is the
registry they are checked against at load, so a mistyped type fails
loudly. `rules.effects.collect()` gathers every modifier of a type from
every record involved (a magus, their laboratory, their covenant), each
attached instance counting once. Flat amounts add to the base first, then
multipliers multiply the sum; rounding is the owning rule's call.

Nothing looks an entry up by name to decide what it does. Rejected:
per-purpose flags with the rule in code, one-off key-to-number maps, and
per-entry code hooks, since each keeps effects out of the data. Catalogs
gain effects as the totals that need them are built.

## 6. Seasons and the year

- A character's season is a `SeasonPlan` the user locks in: magi on their
  laboratory's Planning tab, others on their sheet or the covenant's
  Seasons tab. Grogs get a yearly update instead.
- **Advancing works out every outcome from the saga as it stood, then
  applies them all**, so no result changes another that same season.
  Outcomes go to the Diaries; the year's aging comes with Winter.
- **The world turns** (`world_turns.py`): in Winter the app proposes what
  the year brought beyond the covenants (places, threats, fairs, loans,
  neighbours); only what the storyguide ticks is applied, as one entry
  that can be deleted to undo it.

## 7. Creation

A new covenant, laboratory or character starts **In Creation**; its
Creation Worksheet walks the book's steps with their budgets and checks,
and its buttons open the sheet's own forms, so it edits the real record.
Moving it **In Play** puts the values on its sheet. A book's "must" warns
(a saga setting makes it block); a "should" is only advice.

## 8. UI conventions

The standing decisions; terminal detail in
[reference/UI_Conventions.md](reference/UI_Conventions.md).

**No generative-AI art.** Every image, icon, symbol, texture or font the
app ships or draws, in either front-end, is drawn in code or taken from a
source under a free licence, with its licence beside it and a credit in
NOTICE.md. Never art from an image generator, nor its mockups.

**Both front-ends** (decided in the core, so they can't drift apart)

- **The same verbs in the same places.** Each section's Add / Edit /
  Delete come from `actions.SECTION_VERBS` and `section_verbs`, and the
  More and New menus from `actions.available`; Delete always confirms,
  and Edit and Delete act on the chosen row. Only how they are reached
  differs (below).
- **The same forms.** Every add/edit form is `form_spec` fields, drawn by
  each front-end's `FieldsDialog`.
- **In Creation / In Play** and the Creation Worksheet behave the same:
  the mode changes only when asked, and the worksheet's buttons open the
  record's own forms.
- **Colour comes only from the theme**: `$text-error` for problems and
  penalties, `$text-success` for met targets and bonuses, `$text-warning`,
  `$text-muted`. The desktop's palettes are the terminal themes' own, and
  `gui/markup_html.py` reads the same names; named and hex colours appear
  only in the theme modules (`tests/test_theme_colours.py`).
- **User text** goes through `markup.py` for escaping and emphasis.
- **Help** is the same Markdown in `help/`, a topic per tab, section and
  process dialog, opened on what has focus with `?` or F1. Text true of
  one front-end only is marked `tui` or `gui`; `tests/test_help.py` fails
  on a missing topic.
- **Global keys** (`hotkeys.py`): `?`/F1 Help, Esc cancels or goes back,
  `q` quits; a typed key never acts while a field is being filled in.

**Terminal only** (Textual)

- **One verb per key**: `a` add, `e` edit, `d` delete; rare actions in
  More (`m`), creation in New (`n`). Don't bind a new letter. A focused
  list always has a row chosen.
- Each tab has one details panel docked at the bottom, 12 rows; every
  collapsible section starts expanded; the sheet's summary sits above its
  tabs.
- Section titles carry the list's figure: `(n of m)` against a limit,
  `(X pts)` on a balance (in `$text-success` or `$text-error`), `(n)`
  otherwise.
- Sheets target 140x60 and are checked at 120x45; 80x24 is not a target.
- `refresh_bindings()` only when the keys on offer can change (the
  Footer recomposes each time).

**Desktop only** (PySide6)

- **One page at a time**, like a book: a trail across the top back to the
  pages above, a rail of chapters on a record's page, and an inspector in
  place of the details panel.
- **Buttons, not letters**: a section's Add / Edit / Delete are buttons
  (Edit and Delete greyed until a row is clicked), New and More are
  buttons and New cards where `menu_forms` places them, and a step opens
  in place of the section it belongs to.
- **Drawn, not printed**: laid paper, gilding and ornaments painted in
  code.
- **Motion and sound are few and short**: movements of 150 to 250 ms
  that never block a click, following Reduce motion; sounds only for
  moments that mean something, off in tests and probes
  (`ARMARIUS_MOTION`, `ARMARIUS_SOUNDS`).
- **Printing** adapts the page already drawn, so the PDF says what the
  screen does.

## 9. Phases

| Phase | What | Status |
| --- | --- | --- |
| 0–1 | Scaffolding; the core tracker and catalogs | 1.0.0 (Folio) |
| 2 | Rules Engine | done, grows with each rule |
| 3 | Seasons, aging, warping | done, grows with each activity |
| 4 | Creation by the book | 2.0.0 (Codex) |
| 5 | The Saga World, and the desktop at parity | 3.0.0 (Nomen Novum) |
| 6+ | Open-ended: more books, the desktop's polish, printing | in progress |

Open question (not blocking): a history of ownership changes, such as who
owned this laboratory in 1215.
