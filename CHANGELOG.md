# Changelog

What changed in each version of Ars Magica Manager, newest first.

Versions are `MAJOR.MINOR.PATCH`: MAJOR marks a finished phase of the
plan (1.0.0: Phase 1, the core tracker; 2.0.0: Phase 4, creation by the
book), a new or changed feature bumps
MINOR, a bug fix or behind-the-scenes improvement bumps PATCH. The version is set in
`pyproject.toml`, shown in the app's title bar and on the saga picker, and
recorded in every saga file that version saves. Each version is tagged in
git (`v0.2.0`, ...).

## Release names

The big releases have names, after the books and crafts of a medieval
scriptorium and a Hermetic covenant. Bug fixes and small polish releases
are not named; each named version's heading carries its name.

| Name | Versions | What it brought |
| --- | --- | --- |
| Sodales | 2.12.0 to 2.18.0 | The troupe shares a saga: hosted for players' browsers and SSH, with sign-in and safe saves |
| Foundations | 2.11.0 | Your data in its own folder, packaging, automatic checks |
| Summa | 2.10.0 | How-to guides in Help |
| Scriptorum II | 2.9.0 | The readability pass |
| Glossa | 2.8.0 | Help for whatever has focus |
| Exemplar | 2.6.0 | Character templates |
| Verbum | 2.5.0 | The keyboard rework: one key per verb |
| Gauntlet | 2.0.0 to 2.4.0 | Phase 4: creating covenants, laboratories and characters by the book |
| Book of Hours | 1.3.0 to 1.8.0 | Seasons planned and played out, study and lab work |
| Computus | 1.1.0 to 1.2.0 | Phase 2: the Rules Engine |
| Codex | 1.0.0 | Phase 1: the core tracker |
| Florilegium | 0.6.0 to 0.10.0 | The reference catalogs, checked against the books |
| Scriptorum | 0.4.0 | Highlights in the theme's own colours |
| Incipit | 0.2.0 | The first tracked version |

An *incipit* opens a manuscript; a *florilegium* gathers extracts from
many books; the *computus* was the reckoning of dates; a Book of Hours
follows the labours of the seasons; the Gauntlet makes an apprentice a
magus; the Hermetic Techniques are verbs (*verbum*); an *exemplar* was the
copy scribes worked from; a *glossa* is a note in the margin; a *summa*
teaches a whole subject; *sodales* are fellow magi of the Order, as
the troupe's players are to the storyguide.

## 2.21.0 — 2026-10-07

- A familiar can be removed on its own: press `d` on it in the tree or
  on its Familiar Info panel. The confirmation says what goes with it:
  the bond is broken, the magus loses the True Friend Virtue and Loyal
  (Partner) Trait the bond gave them, and any planned seasons of binding
  or empowering it are deleted. The magus's sheet is shown afterwards.

## 2.20.0 — 2026-10-07

- The Boons and Hooks, Laboratory Virtues and Flaws, and Abilities
  pickers now show the highlighted entry's details under the list, as
  the spell picker does: its rules text, tier and points, what it
  requires or rules out, its effects and the book it comes from.
- Pickers name an entry's books in full ("Ars Magica Definitive
  Edition; Covenants"), core book first.

## 2.19.3 — 2026-10-07

- Behind the scenes: the Plan Season form and the Invent Spell screen are
  now built from short named parts instead of two very long functions,
  and a code check now stops new over-long functions from creeping in.
  Nothing you see changes.

## 2.19.2 — 2026-10-07

- Behind the scenes: the app's screen tests, which were all in one very
  long file, are now in one file per area, with the helpers they share
  in a file of their own. Nothing you see changes.

## 2.19.1 — 2026-10-07

- Behind the scenes: the code that plans and advances the seasons, which
  was all in one very long file, is now organised into one file per part
  (plans, what a season does to a character, the covenant, lab work and
  advancing). Nothing you see changes.

## 2.19.0 — 2026-10-07

- The spell catalog is rebuilt from the Definitive Edition's spell chapter
  and the Grand Grimoire of Hermetic Spells: 1,313 spells from the
  Definitive Edition and every supplement the Grimoire covers, each with
  its full description, book and page. Where the two disagree, the
  Definitive Edition's version is kept. Spells from a book not in play
  stay hidden in the pickers until F3 shows them. Known spells whose old
  catalog entry is gone show as "Unknown spell".
- The catalog pickers (spells, Virtues and Flaws, Abilities, Boons and
  Hooks, laboratory Virtues and Flaws, Shape and Material bonuses) open
  and search far faster: with every book in play the spell picker opens
  in about a quarter of a second instead of four and a half.
- Every spell picker now shows the highlighted spell's details under the
  list, description included, so you can compare spells before choosing.

## 2.18.3 — 2026-10-07

- Behind the scenes: the app's forms, which were all in one very long
  file, are now organised into one file per area (characters, covenants,
  laboratories, books, spells, seasons, enchanted devices and so on).
  Nothing you see changes.

## 2.18.2 — 2026-10-06

- Great (Characteristic) now raises the Characteristic it names by 1, and
  can only be taken when that Characteristic is at +3 (or +4, for the
  second copy, which takes it to +5). The Virtue picker offers only the
  Characteristics that qualify. Removing it takes the point off again.
  Poor (Characteristic) works the same way from -3.

## 2.18.1 — 2026-10-06

- Tidier code notes: the program's comments now state each rule plainly,
  without internal ticket numbers, and the rules note on covenant
  finances no longer shows one either. The README now describes what
  the app does today: the rules, seasons, creation and hosting a saga.

## 2.18.0 — 2026-10-06 — Sodales

- Players can also reach a hosted saga over SSH: start hosting with
  `--ssh-port 2222` and they connect with `ssh -p 2222 player@ADDRESS`
  from Windows Terminal, macOS or Linux, to the same saga list and
  sign-in as in a browser. No accounts on your computer are involved.
  Export isn't offered over SSH, since the file could only land on the
  host. Help's hosting guide says how.
- Every form now opens with its first field ready to type into. Before,
  the first letters typed went nowhere until you pressed Tab or clicked
  a field.
- Sodales (2.12.0 to 2.18.0) is the troupe release: the storyguide hosts
  the saga and players sign in from their own computers.

## 2.17.1 — 2026-10-06

- Help gains "How to host a saga for your troupe": what to set up, how
  to start and stop hosting, Tailscale and ZeroTier recipes, and what
  players see. A character's Biographical Detail now shows who it is
  Played by when the saga has players.

## 2.17.0 — 2026-10-06

- When several people have a hosted saga open, each one sees the others'
  changes within a couple of seconds: the sheet on show updates where it
  is, with a note such as "Ana changed Corvinus; reloaded". If two people
  open the same character, both are told. A saga with no players works
  exactly as before.

## 2.16.0 — 2026-10-06

- Players signed in to a hosted saga now change only what is theirs: the
  characters they play, with those characters' familiars, laboratories
  and books. Choose who plays a character with **Played by** in its
  Biographical Detail, and tick **May change covenants** on a player to
  let them change the covenants too. Making new records, the season and
  date, importing, moving vis and sharing spells stay with the storyguide.
  Elsewhere a player can look and Export, and in a browser an export
  downloads to their own computer.

## 2.15.0 — 2026-10-06

- When the saga is hosted and several people have it open, saving no
  longer wipes out what the others saved meanwhile: each save keeps
  everyone else's changes and writes only its own, down to the single
  field. If two people change the same thing, the later save wins.

## 2.14.0 — 2026-10-06

- Players who open a hosted saga in a browser now sign in first, with
  their name and a passcode. You add them on the saga's new **Players**
  node (only the storyguide sees it), each as a Player or a Storyguide.
  Passcodes are kept only scrambled. In a browser the saga list no longer
  offers New or Delete Saga, and the header shows who is signed in.
  For now everyone signed in can still change everything.

## 2.13.0 — 2026-10-06

- Help has a What's New page, under REFERENCE after About this App: every
  version's changes, newest first. It shows its start at once and fills
  in the rest as you read.
- The big releases now have names, after the books and crafts of a
  medieval scriptorium and a Hermetic covenant (Incipit, Florilegium,
  Codex, Computus, Book of Hours, Gauntlet and more): each named
  version's heading carries its name, and a Release names table near the
  top of What's New says what each one brought.

## 2.12.1 — 2026-10-06

- Fixes an experiment's Extraordinary Result of 11 (a modified effect):
  one die is now rolled for the whole Modified Effect table, as the book
  says, instead of a new die for each row checked, which skewed the odds
  of each kind of change.

## 2.12.0 — 2026-10-06

- First step towards players and the storyguide sharing a saga: the app
  can now be opened in a web browser from another computer, with
  `uv run python tools/serve.py --host <address>`. Each browser tab gets
  its own copy of the app. This is an early test: there is no sign-in
  yet, so only use it on a private network (your home network,
  Tailscale or ZeroTier), and two people editing at once can still
  overwrite each other's changes.

## 2.11.3 — 2026-10-05

- Fixes a covenant's starting laboratories taking 50 Build Points off for
  every magus whose laboratory wasn't entered (Dammerstein's Build tab
  showed -200 for Laboratories). Every magus has a free standard
  laboratory whether or not it is entered; only the magi you say go
  without one refund 50, set on the Power Level step as **Magi without a
  laboratory**. To recount a covenant already in play, move it back to
  In Creation and then to In Play again.

## 2.11.2 — 2026-10-05

Behind the scenes: the rules for each kind of seasonal activity are now
grouped into one place per family, the order in which a season's end is
played out is tested on its own, and more of the season rules are covered
by tests. Nothing changes in what the app shows or does.

## 2.11.1 — 2026-10-05

- Fixes 2.11.0 failing to start when Windows' Controlled folder access
  (ransomware protection) blocks writing to Documents. Your data now lives
  in **Ars Magica Manager** at the top of your OneDrive folder (or the app
  data folder without OneDrive). If the app can't write there, it keeps
  using wherever your saves already are and says why, instead of stopping.
- Behind the scenes: the covenant sheet now updates its tabs the same way
  the other sheets do, and the automatic GitHub checks run only on request.

## 2.11.0 — 2026-10-05 — Foundations

Your data now has a home of its own: sagas, their backups, exports and the
app's settings are kept in **Ars Magica Manager** in your Documents folder
(found wherever Windows keeps it, OneDrive included), where they are easy to
find and back up. The first time this version starts it moves your existing
saves there from the app's own folder, never overwriting anything, and says
what it moved. Another folder can be chosen (see the README). The project
also gained its package details and automatic checks on GitHub for every
change pushed.

## 2.10.2 — 2026-10-05

Rules corrections.

- Lab Texts and Casting Tablets are bought as a pool, as the book says:
  the levels of all a covenant's Lab Texts are added up and cost 1 Build
  Point per 5 levels (Casting Tablets 2), and the Build tab and a text's
  details show the levels bought but not yet used.
- The season plan offers a supplement's activities only while that book is
  in play (a plan already made keeps its activity).
- The minimum number of servants follows the book: 2 for every 10 points
  of inhabitants or part of 10.
- A Dwindling Resource loses a tenth of its original value each year and is
  gone after ten years.
- Where a rule doesn't say how to round, the app rounds down (recorded
  lectures now do).

## 2.10.1 — 2026-10-05

Safer saving. A saga, the settings and an export are now written in full
before they replace the old file, so a crash or a full disk mid-save can no
longer leave a half-written saga. The app now keeps the last five backups
of a saga (taken before each season with plans is applied) instead of only
one. A damaged settings file no longer stops the app starting, and a saga
saved by an older version with a since-removed field in any record now
opens instead of failing.

## 2.10.0 — 2026-10-05 — Summa

How-to guides in Help: eight step-by-step walk-throughs, listed under
HOW-TO GUIDES when you press ?: planning and running a season, managing
the covenant, how advancement works, lab planning, getting started,
creating characters, covenants and laboratories, familiars, and
importing and exporting. The help pages they cover link to them.

Two out-of-date hints are fixed: the Advance Time dialog now says Set
Date is in More on the saga, and the Export dialog says to import with
More's Import.

## 2.9.0 — 2026-10-05 — Scriptorum II

Easier to read, with a clearer order of importance on every screen.

- Text fields have a background of their own, a shade deeper than the
  page, so it's clear where to type; the field you're typing in lights
  up. Number fields are short, so long forms no longer read as one block.
- Names and dialog titles are headings, every section title is bold, and
  the tab you're on stands out. Labels are quieter than their values,
  values that come from the saga are in italics, and each details panel
  has an accent edge.
- Warnings have their own colour instead of the accent's gold, placeholder
  text in fields is readable, and every text colour now meets the
  standard readability contrast in both Scriptorum themes. A focused
  character name no longer disappears into its highlight.
- Abilities line up in Score and XP columns.
- Problems start with ✘ and things still to do with ☞ (the pointing hand
  scribes drew in margins), so they stand out by shape as well as colour.

## 2.8.0 — 2026-10-04 — Glossa

Help: press ? anywhere (F1 while typing in a dialog) for help on the part of
the screen you're in: the section, its tab and the sheet, with the keys that
work there. Every sheet, tab and section has a page saying what it's for and
what you type versus what the app works out, and the processes (planning and
advancing a season, inventing a spell, the Creation Worksheet, importing) have
their own. Topics can be filtered with /. About this App now lives in Help.

## 2.7.1 — 2026-10-04

A magus's free House Virtue no longer counts toward Virtue points.

- On the character sheet, the Virtue the House gives free (Hermetic
  Houses Summary, Definitive Edition Chapter Three) is left out of the
  Virtues points and marked Free in its row, so a balanced magus no
  longer shows one point too many in the error colour. For Ex
  Miscellanea, its two free Virtues and its compulsory Hermetic Flaw are
  left out of the points.
- The sheet and the Creation Worksheet now agree on which Virtue is the
  free one.
- The Virtues & Flaws lists update straight away after the House or the
  character type is changed.

## 2.7.0 — 2026-10-03

The details panel at the bottom of a sheet's tab fits what it shows.

- It is as tall as its text, from 3 rows up to 12; longer text still
  scrolls inside it. With nothing chosen it shrinks to 3 rows, and the
  list above it gets the rows it gives back.
- Three laboratory hints are shorter so they fit on one line: Attributes,
  Inventory and Planning.

## 2.6.0 — 2026-10-03 — Exemplar

Character templates: start a new character from one of the book's
ready-to-play characters.

- New Character has a Template choice under Type. It starts at None and
  offers only that type's templates from the Definitive Edition: six grogs,
  five companions and a magus for each of the twelve Houses (the book has
  none for Mythic Companions). The form describes the chosen template as
  you pick it.
- A template fills in the whole sheet: Characteristics, age, Virtues and
  Flaws, Abilities with their specialties, Arts, spells, weapons, armor and
  gear, Personality Traits, Reputations and the House. The character
  starts In Play, and its Biography notes the template and the book's
  advice on customizing it.
- It asks for the area and native language the template leaves to you;
  cancelling there creates no character.
- Two spells the templates know but the spell list lacks (Piercing the
  Magical Veil, Unravelling the Fabric of Imaginem) are added to the
  saga's own spells the first time they are needed.

## 2.5.0 — 2026-10-01 — Verbum

The keyboard rework: one key per verb, everywhere.

- `a` adds, `e` edits and `d` deletes whatever has focus: the highlighted
  row, the section, or the record itself (on its tree node or top panel).
  Delete always asks first; the `Delete` key works too. Nothing asks
  "which one?" any more: a focused list always has a row chosen.
- `m` (More) holds the rare actions for where you are: Move Vis, Share
  Spell, Perform Ritual, Improve Income, Instill an Effect, Use a Charge,
  Restore, Export, Import, Set Date, In Creation / In Play and the Creation
  Worksheet. With one action it runs at once and the footer names it; with
  several it opens a menu, a letter each.
- `n` (New) makes a Covenant, Character, Laboratory or Familiar. `/`
  filters: the Lab Texts filter, or the search box on Spells.
- `Tab` and `Shift+Tab` stop once per section instead of on every button
  and title. `1` to `9` open the numbered tabs. `Esc` steps out: sheet,
  then tree, then the saga picker. `c` collapses or expands the focused
  section; Enter on a title no longer does.
- Mouse: a click on a section that isn't focused only focuses it. A click
  on the focused section's title collapses or expands it. A click on a
  sheet button leaves focus on its section.
- The footer shows the focused section's keys on the left and the fixed
  ones on the right, and the row above it says where you are.
- After a delete the next row is chosen (a second `d` still asks).
- Gone: `A`, `v`, `V`, `Ctrl+D`, `r`, `i`, `u`, `s`, `I`, `x`, `T`, `F`,
  and `c` / `l` / `f` as create keys.
- Fixed: editing an existing Vis Source crashed.

## 2.4.0 — 2026-10-01 — Gauntlet

Lab Texts, House Rules, and moving records between sagas.

- A laboratory's Inventory tab has a Lab Texts list of its own, apart from
  its other Books: each text's kind (Spell, Enchantment, Longevity Ritual
  or Other), Arts, level, author and Sigil, whether the laboratory's owner
  can read it, and what a copy costs a scribe. `F` filters it by kind,
  Art, level and readable only.
- Instilling an effect in a device and performing a Longevity Ritual each
  leave a raw Lab Text in the laboratory. Taming and Discovery texts
  record their Arts, so another magus can decode them.
- Enchanting can be planned "From Lab Text": one season if the Lab Total is
  at least the level (a lesser enchantment no longer needs twice it, and a
  charged item gets a charge per 5 of the whole Lab Total). `u` on the Lab
  Texts list performs a Longevity Ritual again from its text: no season,
  only the vis, including any extra vis it was first made with.
- A magus's Hermetic Background lists whose Lab Texts they can read, with
  a "Lab Texts Read" button to set it. Renaming an author no longer loses
  what was decoded. The Invent and Copy pickers show texts that still need
  decoding instead of hiding them.
- House Rules: a new node under the saga keeps the saga's own Virtues,
  Flaws, Boons and Hooks (name, type, tier, category, description). Every
  picker offers them alongside the catalog's. They are text only: no
  effects are applied.
- `x` on a covenant, laboratory or character exports it to a file with
  what travels with it (a character's familiar, devices, books and Diary;
  a laboratory's books; optionally a covenant's laboratories and
  characters). `I` on a saga imports one: Characters, Covenants and
  Laboratories now work in the Import list. A preview shows what is added
  and which links are kept or dropped before anything changes.

## 2.3.0 — 2026-10-01 — Gauntlet

Moving raw vis, paying from the covenant's vis, and live Characteristic
points.

- Raw vis can be moved: `m` (Move Vis) on a magus's Raw Vis, a laboratory's
  Raw Vis or a covenant's Raw Vis Stores asks how many pawns and who gets
  them: any other covenant, laboratory or magus in the saga. A covenant
  takes it into its store of that Art (a new one if it has none), and both
  sides' Diaries record the move.
- A covenant's Raw Vis Store says where it is kept: the covenant, one of
  its laboratories or one of its characters. Location text in older saves
  that names a laboratory or character becomes that link; anything else is
  kept at the covenant, with the text left in Location as a note on where
  exactly.
- Season work can pay from the covenant's vis: "Vis from" on vis study and
  on every lab activity has a third choice, the covenant's vis stores.
  Spending takes from the stores of that Art in list order, vis extracted
  that way goes into the covenant's store, and the covenant's Diary
  records each change.
- While a character is In Creation, the Edit Characteristics form shows the
  points spent and left, and each score's cost, as each number is typed:
  red when over the budget, green when it is spent exactly.

## 2.2.0 — 2026-10-01 — Gauntlet

Covenant Situations, Poverty warnings, and sharing an invented spell.

- A covenant's Creation Worksheet can add a Covenant Situation: one of the
  books' ready-made sets of Boons and Hooks (the core book's six, and
  Covenants' eighteen when that book is in play), on top of what the
  covenant already has. Where Covenants' own lists disagree with its
  catalog, the preset says so before it is added.
- Boons and Hooks that don't go together are warned about above the Boons
  and Hooks lists and on the worksheet: the Minor Poverty Hook with Wealth
  or Secondary Income, and income that Poverty doesn't allow (one Lesser
  source for Minor Poverty, none for Major). Nothing is blocked.
- On the worksheet, Boons may cost less than the Hooks give (advice); only
  costing more breaks the rule.
- A magus can make an invented spell available to the whole saga: `s`
  (Share Spell) on Known Spells moves it to the saga's Spells, after
  asking. The magus still knows it and its Lab Texts still link to it.

## 2.1.0 — 2026-10-01 — Gauntlet

Build Points have one home: a Build tab on the covenant sheet.

- The covenant sheet has a Build tab: a row for each kind of resource
  (summae, tractatus, Lab Texts, Casting Tablets, vis sources and stocks,
  enchanted items, laboratories, specialists, money) with what was spent
  when the covenant started (Initial) and what it is worth now (Current),
  a total, and a list of everything counted. Initial is recorded when the
  covenant moves to In Play; a covenant already in play shows "-" there.
- Books no longer show their Build Point cost once the covenant is in
  play: the cost and the covenant-creation limit warnings appear only
  while the covenant is In Creation, and the Library summary has no Total
  Cost.
- A laboratory's Build Points are worked out (Size x 20, plus 10 for each
  Minor Virtue and 20 for each Major one) instead of typed.
- While a covenant is In Creation its top panel shows the Build Points
  spent against the storyguide's figure.

## 2.0.0 — 2026-10-01 — Gauntlet

Phase 4: creating covenants, laboratories and characters by the book.

- Every covenant, laboratory and character is now either In Creation or In
  Play. New ones start In Creation; everything you already had is In Play.
  A button beside Edit on each sheet shows the mode and switches it (it
  asks first), and records still being created are marked in the tree.
- While a record is In Creation its sheet offers a Creation Worksheet: the
  book's steps down the left, each marked as passing, breaking a rule, or
  carrying advice, with the chosen step's budget, checks and buttons on
  the right. The worksheet edits the real record, and "Move to In Play" on
  the last step reviews what is still open.
- Characters: concept (type, House, age), Virtue and Flaw limits by
  character type, the 7 Characteristic points, Early Childhood (with the
  sample childhoods), Later Life xp (only Abilities the character may
  learn, Virtue xp, the Ability cap by age), Grogs training packages, a
  magus's apprenticeship (240 xp, 120 spell levels, each spell capped by
  the magus's Lab Total) and years past Gauntlet, pre-play aging rolls,
  and Personality Traits, Reputations and Confidence.
- Each House gives its free Virtue: a magus's Virtues balance exactly, with
  the House's Virtue free, and the worksheet offers to add it.
- Covenants: pick a Power Level and the Build Points the storyguide gives;
  the library, vis, enchanted items, starting laboratories and bought
  specialists are totalled against them, and Boons must balance Hooks.
- Laboratories: a starting lab's Build Points go to its covenant, its
  builder needs Magic Theory 3, and its Virtues must fit.
- Rules the book says a record must follow are warnings; its "should"s are
  advice. A new saga option, "Enforce creation rules strictly", stops a
  record with a broken rule moving to In Play.
- The Grogs book is now in the list of sourcebooks.

## 1.9.2 — 2026-09-30

A fix to the covenant's Economics tab.

- Deleting the chosen source of income no longer leaves the next source
  chosen in its place, so pressing Delete again can't remove a second
  source by mistake. Like every other list, nothing is chosen after a
  delete; editing something elsewhere on the tab still keeps your choice.

## 1.9.1 — 2026-09-30

The performance plan is saved with the project. Nothing in the app changes.

- PERFORMANCE_PLAN.md records where the app spends its time (the screen,
  not the save file), why a database isn't needed at this size, and the
  fixes planned from it.

## 1.9.0 — 2026-09-30

Polish across the sheets.

- Magical Arts on the Hermetic Magic tab collapses like the other sections.
- A score raised or lowered by a Virtue or Flaw shows both numbers in the
  Abilities and Arts lists: "Magic Theory 5 (7)".
- A Virtue or Flaw that names a Characteristic, Ability, Art, Technique or
  Form is chosen from a list instead of typed, leaving out the ones already
  taken as often as the book allows.
- The laboratory's Lab Totals tab is easier to read: the grid, the Base Lab
  Total and what each activity adds are now separate sections, one term per
  line, with bonuses in green and penalties in red.
- Botch dice count the Virtues and Flaws that change them for spellcasting
  and experimenting: Cautious Sorcerer, Careless Sorcerer, Weird Magic,
  Afflicted Tongue, Deaf and Palsied Hands.
- A test that failed now and then under load is steady.

## 1.8.0 — 2026-09-30 — Book of Hours

The rest of the seasonal activities: almost everything a character can do
with a season now plays out when you advance it.

- **Laboratory work:** opening items, instilling effects, lesser and
  charged enchantments, attuning talismans, investigating items, binding
  and empowering familiars, decoding Lab Texts, taming magical beasts,
  assisting in a lab, and setting up, refining, taking over and moving a
  laboratory.
- **Books:** writing summae and tractatus, copying and translating books,
  and rewriting, copying and teaching the abbreviations of Lab Texts.
- **Aging and Warping:** yearly aging rolls with Longevity Rituals,
  Decrepitude and crises; Warping from magic and experiments, with
  Twilight when a score rises.
- **Experimentation and original research:** experimenting on any lab work
  that allows it, with the Extraordinary Results chart played for you
  (including Cautious Sorcerer and the two-dice Flaws). A Research Goals
  list on the Hermetic Magic tab tracks Breakthroughs; the season advance
  asks before moving a roll onto a Discovery, stabilizing repeats the
  experiment, and a reached goal grants its Ability or Virtue. Side effects
  stay with what was made, and an invented spell passes them on to anyone
  who learns it.
- **Apprentices:** searching for one, opening their Arts, teaching a
  Hermetic Virtue.
- **Covenant and grogs:** covenant seasons, contested resources (lost for
  the year if not settled, noted in the covenant Diary), and each grog's
  yearly update.
- **Other activities:** crafts and livelihoods, scholars, physicians and
  artists, religious seasons, Mysteries and House activities, animals,
  travel and more study sources.

## 1.7.2 — 2026-09-30

A leaner test suite, finished. Nothing in the app changes.

- Every form's checks (it fits the screen, starts with the current values,
  Cancel saves nothing, bad entries are refused, Save stores the change and
  the sheet shows it) now run in one go per form, and 36 more forms are
  covered this way.
- More of the sheet lists are checked the same way, including deleting the
  chosen entry; the older one-off tests they replace are gone.
- The data catalogs, and saving and loading a saga, are each checked by a
  few broad tests instead of many narrow ones.
- The full test run is about 3 minutes shorter (19 to 16 minutes).

## 1.7.1 — 2026-09-30

A leaner test suite, first part. Nothing in the app changes.

- Removed UI tests that only repeated what the shared form, list, sheet and
  key checks already cover, and ran the shared trait-list checks on fewer
  of the lists that share one handler.
- A few rules that were only checked through the screens (the Boons & Hooks
  titles and details panel, which Abilities the picker offers, the Known
  Spells rows) are now plain functions with fast tests of their own.

## 1.7.0 — 2026-09-30 — Book of Hours

Lab work, planned from the laboratory.

- The laboratory's Planning tab lists the owner's scheduled activities and
  the seasons each spans, with the chosen one's Lab Total line by line.
  e plans or changes lab work, a starts a new spell, A clears a plan (and
  every season it spans).
- Inventing a spell has its own screen: start from any spell or a blank
  one and change anything -- name, effect, Arts, requisites, base level,
  Range, Duration, Target, Ritual. The level is worked out as you edit;
  Virtues and Mysteries that grant extra Ranges, Durations or Targets add
  them to the lists, and "Other..." takes any with its magnitudes. Lab
  options: a similar spell, Magical Focus, Magic Theory Specialty, days
  away and any other modifier. It shows when the spell will be invented,
  and scheduling fills every season needed. Reset clears the form.
- Inventing from a Lab Text, too. A finished spell is known, a Lab Text is
  written for the lab, and the lab's Diary records it; every lab season
  gives 2 xp Exposure in Magic Theory.
- More lab work: extract Vim vis (Magic aura only), fix an Arcane
  Connection (1 pawn of Vim) and Longevity Rituals, your own or someone
  else's. The ritual's aging modifier is kept on its subject, whose season
  is planned with the magus's.
- Arcane Connections are kept on the laboratory's Inventory tab: what each
  connects to, and whether it is fixed or how long it lasts.
- The lab work screen opens with no activity chosen until you pick one.

## 1.6.0 — 2026-09-29 — Book of Hours

Study seasons.

- New activities to plan: Read a book, Be taught, Teach, Be trained and
  (magi) Study from vis. A summa gives its Quality up to its Level; a
  tractatus gives its Quality once to each reader; a teacher needs to plan
  Teach for the same season; vis study rolls its die when the season is
  played out (or use the roll you made at the table) and spends the vis.
- Who can read a book: everyone in the covenant can read its library's
  books; a book a character keeps (or keeps in their laboratory) is theirs
  alone. A book's details list only those who may read it.

## 1.5.1 — 2026-09-29

- Behind the scenes: the code now passes its type check with no errors,
  and that is the standard from here on. Nothing changes in the app.

## 1.5.0 — 2026-09-29 — Book of Hours

- After a season with plans is played out (t), a summary shows what each
  person did and what it gave, by covenant, and who had nothing planned.
- A new Seasons entry in the tree lists past seasons, newest first; choose
  one to read its record again.
- Edit Saga has "Keep season records" (on by default). Off, the summary
  still shows after each season, but it isn't saved; the characters'
  Diaries keep their entries either way.

## 1.4.0 — 2026-09-29 — Book of Hours

- Each covenant has a new Seasons tab, after Inhabitants: its magi,
  companions and grogs, each with what they have planned for the season
  (or "nothing planned"), and a count of who has planned in each list.
  Choose someone to see their plan and what it will give; e plans their
  season and A clears it.

## 1.3.0 — 2026-09-29 — Book of Hours

Seasons can be planned and played out (the start of Phase 3).

- Each character sheet has a new Planning tab, just before the Diary. Plan
  the season there: Work / Exposure, Practice (including a spell's
  Mastery), Adventure, or Other for anything else. While you fill it in,
  the plan shows what the season will give and the rule behind it.
- Advancing the season (t) warns about magi and companions with nothing
  planned, works out every plan from where things stood before the season
  (one character's results can't change another's that season), backs the
  saga up to data/sagas/backups, then adds the experience and writes each
  character's Diary.
- Characters have a Diary, like laboratories: an entry for every season
  played out, and entries you add yourself.
- A magus's Lab Totals moved from the character sheet to a new Lab Totals
  tab on their laboratory's sheet. The laboratory's Planning tab shows
  what its owner has planned for the season.

## 1.2.2 — 2026-09-29

The app is quicker to use.

- Switching tabs, moving between sections and arrowing through lists take
  about half the time or less: the key hints at the bottom used to be
  rebuilt several times for every keypress, and now only change when the
  keys do.
- Sheets open two to three times faster (a covenant in about a third of
  the time): a sheet now builds only the tab you see, and builds each other
  tab the first time you open it.
- The rulebook catalogs (Virtues and Flaws, Abilities, Houses and so on)
  are read once when the app starts instead of being checked on disk every
  time a total is worked out; Lab Totals come out over ten times faster. A
  rebuilt catalog is picked up the next time the app starts.

## 1.2.1 — 2026-09-29

Behind the scenes: a way to measure how fast the app is.

- A timing script (`tools/perf_probe.py`) that works on a copy of a saga
  and times loading, saving, the reference catalogs, and opening every
  sheet, switching every tab and redrawing after an edit. It can also try
  a saga made several times bigger, and profile where the time goes.
- What it found: saving and loading take under a millisecond (under 40 ms
  even for a saga 100 times bigger), so the saga file isn't what makes the
  app feel slow. The time goes on the screen: the key hints at the bottom
  are rebuilt several times for every keypress, and a sheet builds all of
  its tabs when it opens. Fixing those is planned next.

## 1.2.0 — 2026-09-29 — Computus

The Rules Engine (Phase 2) works out the book's totals from what's on the
sheets. Every figure shows where it comes from.

- Laboratories: the Planning tab (and the magus's Laboratory tab) shows the
  owner's Lab Total for every Technique and Form, with what each activity
  adds: inventing, enchanting, working from a Lab Text, binding a familiar,
  a Longevity Ritual's aging modifier and the vis a season's extraction
  gives. Laboratory Virtues and Flaws now grant their Specializations
  themselves; when the book lets you choose which, you're asked as the
  Virtue is added.
- Casting: the Hermetic Magic tab shows Casting Scores for every Technique
  and Form in your covenant's aura, Magic Resistance per Form, the
  Penetration bonus and certamen figures. A known spell's details give its
  Casting Score and the die it needs, with Fatigue and botch dice.
- Covenants have an Aura Realm; a Divine, Faerie or Infernal aura changes
  Hermetic casting and lab work as the book says.
- Characters: Soak (the old typed Soak becomes an adjustment on top),
  Encumbrance, the Wound and Fatigue penalties, the Damage Table for the
  character's Size, and a weapon's Initiative, Attack, Defence and Damage.
  Puissant shows as a bonus on the score (5+2). True Faith shows its Magic
  Resistance.
- Spells show their design ("Base 5, +2 Voice, +2 Sun, +2 Group = 35"), and
  the spell form fills in Level from its base and Range, Duration and
  Target.
- Books show what a season's reading gives each magus and companion of the
  covenant.
- Optional rules on Edit Saga, all off until you turn them on: simple dice
  only, Dominion Magic Resistance, harsher Infernal vis.
- Many Virtues and Flaws now change the totals they affect (Affinity,
  Puissant, Book Learner, Inventive Genius, Tough, Large, Deficient Arts and
  more).

## 1.1.0 — 2026-09-29 — Computus

The first piece of Phase 2, the Rules Engine.

- Art and Ability scores now come from experience: you enter each one's
  total XP and the score follows, from the Definitive Edition's
  Advancement Table (an Ability's score 5 costs 75 xp, an Art's 15). The
  XP is always the running total and never resets when a score is reached.
- An Ability reads like "Magic Theory 5 75/105" (score 5, 75 xp, score 6
  at 105), and its details show the score and XP. The Arts grid has a
  Score column; Edit Arts takes each Art's XP and shows its score beside
  it as you type.
- Older saves, which kept a typed score beside the XP, are converted when
  loaded: XP that already buys the score is kept; a smaller figure is read
  as XP toward the next score and added on; a pair that fits neither keeps
  the typed score.

## 1.0.0 — 2026-09-29 — Codex

Phase 1, the core tracker, is complete.

- Enchanted devices and talismans: a record for each enchanted item in the
  saga -- Invested Devices (a magus's Talisman is one), Lesser
  Enchantments and Charged Items -- shown in a new Enchanted Devices
  section on its holder's sheet: the laboratory's and character's
  Inventory tab, or the covenant's Possessions tab. Each device lists its
  effects under it; a magus's talisman is listed first and named on the
  Hermetic Magic tab.
- The app works out the item side of the Definitive Edition's enchantment
  rules: capacity from Material and Size (or a talisman's from its magus's
  Arts), each effect's modified level with its breakdown, its vis, pawns
  used, Effect Expiry, and a Charged Item's charges from its Lab Total.
  Any figure can be typed over. Warnings flag what doesn't add up (effects
  using more pawns than were opened, a second talisman, two attunements in
  one season, too many charges...) without stopping you.
- Shape & Material bonuses and talisman attunements can be picked from the
  Definitive Edition's table (all 241 shapes and materials) or typed in.
- Keys in an Enchanted Devices section: a adds a device, i instils an
  effect in the chosen device, e edits, A removes, u uses a charge of the
  chosen Charged Item. i and u only show in the footer where they can act.
- Deleting a character or laboratory passes the devices it holds to its
  covenant (or deletes them, with no covenant); deleting a covenant
  deletes the devices it holds. The confirmation says which.
- T (Set Date) still works everywhere but is no longer listed in the
  footer, to keep it on one line.

## 0.12.0 — 2026-09-28

- Covenants, characters and laboratories can be deleted: select one in the
  tree and press Ctrl+D. The confirmation says what else happens. Books,
  and a covenant's characters and laboratories, become unassigned rather
  than deleted; a laboratory loses its owner; a magus's Familiar goes with
  them; a magus's invented spells that anyone else still uses move to the
  saga's own spells.
- The covenant Diary tab is built: a dated record of what happens to the
  covenant, in 15 categories (Improvements, Purchases & Sales, Vis,
  Library, Story Events and more), with optional pounds, vis and Loyalty
  points. Its Loyalty points add into the Loyalty block's Actions and
  Events. A Story Event can be Open or Resolved and linked to one of the
  covenant's Boons or Hooks, counting the stories played against a Hook.
- Choose which sourcebooks are in play for each saga, from Edit Saga. The
  core book is always in play and every book is by default. Catalog pickers
  hide entries from books not in play; F3 shows them anyway.
- The laboratory Virtue/Flaw catalog now has all 128 entries from
  Covenants (it had 53).
- True Faith: the character sheet shows a True Faith Score and Faith
  Points for a character with the True Faith Virtue (or any points), and
  the Edit form warns if a Score doesn't fit the rules.
- New Covenant, New Character, New Laboratory and Bind Familiar are offered
  only on the saga and next to their own kind of record, so a sheet's key
  bar shows what belongs there.
- Corrected two House descriptions (Bonisagus, Tytalus) and the chapter
  the laboratory Virtues and Flaws are cited from.

## 0.11.1 — 2026-09-28

- Add and edit dialogs are now checked to fit a 120x45 terminal (the
  smallest size the app is checked at) rather than 80x24, which is no
  longer a target. Nothing you see in the app changes.

## 0.11.0 — 2026-09-28

- Adding a Virtue or Flaw now opens on the side you added it from: the
  Virtues section lists Virtues, the Flaws section lists Flaws. F2 switches
  to the other side or to both.
- The picker has Type and Tier filters beside the search box, and the
  search also matches each entry's one-line summary (names that match come
  first). The chosen entry's summary and source book show under the list.
- The picker hides what the character can't take: Hermetic Virtues and
  Flaws without The Gift (a magus counts as having it); for grogs, Major
  entries, Hermetic ones and The Gift; and entries meant for faeries,
  magic beings, corrupted beasts or animals. F3 (or "Show ineligible")
  lists them anyway, each marked with the reason, and they can still be
  taken if the troupe allows it.
- New character type: Mythic Companion. Only Mythic Companions are offered
  the Mythic Companion Virtues (Blood of Heroes, Nephilim, Spirit Votary,
  Zahid...); otherwise they count as companions, including on the
  covenant's Inhabitants tab. A companion's Edit form can switch it between
  Companion and Mythic Companion.
- A familiar's picker offers the animal and magic-being Qualities and
  Inferiorities as well as the ordinary Virtues and Flaws.

## 0.10.0 — 2026-09-28 — Florilegium

- The character Virtues & Flaws catalog has been checked entry by entry
  against the Definitive Edition and the open supplements: missing entries
  added, wrong ones fixed, bogus ones removed (1,100 entries, up from 625).
  Each entry names its source book. Where the book offers a Virtue or Flaw
  as "Major or Minor", both versions are in the list; the non-human
  Qualities and Inferiorities are there too, marked with who they're for.
- Virtues and Flaws the book lets a character take more than once (Affinity
  with Art, Puissant Ability, Great Characteristic...) are offered again
  after the first, up to the book's limit, and refused past it, or when the
  same choice (the same Art, the same Ability) is taken too often. The
  details panel says "May be taken more than once" or "up to N times".
  Familiars follow the same rule.
- A Virtue or Flaw whose choice isn't part of its name shows it in brackets:
  "Deficient Technique (Creo)".
- Weapons and armor can be chosen from the book's tables (melee weapons and
  shields, missile weapons, armor, and a familiar's natural weapons).
  Choosing one fills in its Init, Attack, Defense and Damage (or armor's
  Protection), its Load, its Quality from the book's cost, and its name if
  you haven't typed one. Everything stays editable, and the form shows the
  book's description as you choose.
- Weapons now record Load, and armor records Protection and Load, shown as
  list columns. Combat figures show signed as the book prints them (+2,
  +0), and a figure the book gives as n/a (a Dodge's Attack) can be left
  blank. A full suit of a material that only comes as partial armor is
  refused.
- A weapon's or armor's details name the book entry it came from, with its
  Ability, minimum Strength and range.
- A character's Personal Gear shows column titles on its Weapons, Armor and
  Other Items rows, and a familiar's Natural Weapons list has them too.

## 0.9.0 — 2026-09-28 — Florilegium

- Every details panel now works the same way on every sheet and list: one
  per tab, at the bottom of the tab below the part that scrolls, always 12
  rows tall. Longer text scrolls inside the panel, and it starts at the top
  whenever you choose another row. The character's Inventory tab shares one
  panel between Personal Gear and Books, like the laboratory's.
- Section titles show the list's figure: "(1 of 2)" where there's a limit
  (Features against the lab's Feature Virtues, as Specializations already
  did), the points on each side of a balance, and a plain count elsewhere
  ("Rooms (2)"). A character's Virtues and Flaws show their points in green
  when they balance and red when they don't; a laboratory's and a
  familiar's show their points uncoloured. Book lists no longer show Build
  Points in their titles.
- Side-by-side lists are the same distance apart on every sheet, and so are
  side-by-side blocks of text.
- Every details panel's prompt now reads "Select a ... to see its details."

## 0.8.0 — 2026-09-27 — Florilegium

- Unknown Hooks: a Minor Hook the book says "may be Unknown" (35 of them)
  can be marked Unknown in its add or Edit form. It then counts 3 points in
  the Hooks total, as a Major Hook, and says so in its row ("Favors
  (Unknown, 3 pts)") and details panel. The picker notes which Hooks may be
  Unknown.
- Ars Magica Manager is now licensed under the GNU GPL v3 (LICENSE). The
  Ars Magica rules text in its catalogs is credited to Atlas Games under
  CC BY-SA 4.0: every catalog carries the attribution line, and NOTICE.md
  lists the sources, changes made and trademark notices.
- The saga picker has an About dialog (`?`) showing the version and the
  licences and credits.

## 0.7.0 — 2026-09-27 — Florilegium

- The covenant Boons & Hooks catalog has been checked against Covenants
  and ArM5 and now has 216 entries: Writ of Crenellation, Haunted,
  Non-magical Regio, the Monster in the Surroundings and the Free Choice
  keeps and moat (Hall Keep, Courtyard Castle, Gatehouse Keep, Chemise,
  Barbican and Moat) were added, and a bogus "Historical" Boon removed.
- Corrected requirements and exclusions (e.g. the castle Boons and Hooks
  now need a Castle; Vis Grant and Vis Salary exclude each other), which
  Boons and Hooks can be taken more than once, and the Buildings cost of
  Bedrock, Vast and Labyrinthine, Natural Fortress, Magical Fortress and
  Superior Engineering.
- The details panel and picker show when a Boon or Hook needs one of
  several others, how many times it can be taken, and which book it comes
  from.

## 0.6.0 — 2026-09-27 — Florilegium

- Laboratory Features: each Feature (Altar, Cauldron, Window... all 36, or a
  custom one) is built on one of the lab's Lesser or Greater Feature
  Virtues and puts its 1 or 3 points into the Specializations it offers.
  Adding a Feature can add the Feature Virtue it needs (after asking), and
  deleting a Feature Virtue takes its Feature with it.
- A Feature can be the lab's Focus when the lab has the matching Focus
  Flaw, for 2 or 4 more points; deleting the Focus Flaw clears it.
- Feature and Focus points count in the Specializations list, labelled with
  the Feature's name. Old free-text Features are converted (e.g. "Large
  Brass Cauldron" becomes a Cauldron on the lab's first Lesser Feature).
- The Specializations list shows how many count against each limit in its
  headings ("Activity (2 of 2)", "Art (3 of 4)"); the other sources are
  nested inside it as "Specializations: Other". Specializations and Features
  no longer collapse.
- Whether the sanctum is marked now shows in the laboratory's Identity
  ("Sanctum?: Yes") and is set in its Edit form.
- The laboratory's Attributes and Inventory tabs each have one details panel
  at the bottom of the tab, as on the covenant's tabs, showing whichever row
  was last chosen.

## 0.5.0 — 2026-09-27

- The laboratory's Virtues and Flaws are two lists side by side, with a
  panel showing the chosen one's category, tier, points, effect on the
  Characteristics and rules. A warning appears above them when the lab is
  over capacity or has more than one Focus.
- Rooms, Raw Vis, Equipment & Stores (formerly Items) and the Diary are
  selectable lists: edit and delete act on the chosen row, every delete asks
  first, and Rooms, Equipment & Stores and Diary entries show their text in
  a details panel. Descriptions and Diary details can run to several lines.
- Diary entries have an Activity Type (Invent Spell, Extract Vis, Study...).
- Changing the lab's Virtues and Flaws now updates the Characteristics
  straight away.
- A new Specializations list on the Attributes tab adds up each Activity and
  Art Specialization from every source and shows where the points come
  from. At most 2 Activity and 4 Art Specializations (no more than 2
  Techniques) count: Space turns one off or back on, one that would go over
  a limit arrives turned off, and turned-off ones are dimmed and struck
  through.
- Specialization points from other sources (a Virtue such as Subterranean,
  a Flaw such as Undecorated) are entered by hand under Other Specialization
  Sources. Old free-text Specialties are converted, e.g. "Terram +1".
- The Attributes tab records whether the sanctum is marked.

## 0.4.0 — 2026-09-27 — Scriptorum

- Every highlight in the app now uses the current theme's own colours
  instead of fixed red, green and cyan, so it stays legible whichever theme
  you pick: problems, deficits and unmet minimums in the theme's error
  colour; balanced Boons/Hooks and met minimums in its success colour. A
  covenant surplus or break-even, and Boons that cost less than the Hooks
  provide, are now shown plain.
- Book problems, CSV rows that will be skipped, "can't be read" sagas and
  unknown spells are highlighted in the theme's error colour; the check mark
  on multi-selected books uses its success colour.

## 0.3.0 — 2026-09-27

- The laboratory sheet's top panel is more compact: Identity is titled with
  the lab's name, with Covenant/Owner and Location/Points side by side and
  the Aura below; the Characteristics sit in three columns (the derived
  figures, then the eight Characteristics four and four) instead of one long
  table. On a narrow terminal the columns stack one above the other.
- Characteristic numbers are coloured with the current theme's own colours
  (bonuses in its success colour, penalties in its error colour, zeros
  plain), so they stay legible whichever theme you pick.
- The wizard's sigil is entered in a multi-line box.

## 0.2.1 — 2026-09-27

- A saved choice that a list no longer offers is kept when you save a form
  without touching it, instead of being cleared: a House missing from the
  House list shows as "… (not in the list)", and a laboratory owner who is no
  longer a magus shows by name.
- Multi-line fields (Biography, descriptions) keep an indented first line,
  such as a Markdown list; only trailing spaces and blank lines are dropped.
- Behind the scenes: the standard form's code is simpler and better checked,
  and the tests are sturdier.

## 0.2.0 — 2026-09-27 — Incipit

The first tracked version. Includes everything since 0.1.0:

- **Versions.** The app now has a version number, shown in the title bar and
  on the saga picker and saved into each saga file, and this changelog.
- **Code health.** The screen code, one file of about 14,000 lines, is now
  organised into smaller pieces. Most add/edit dialogs are one standard
  form: they look and behave alike and fit an 80×24 terminal. Many more
  tests, and the full test run is much faster in parallel.
- **Bug fixes.**
  - A damaged saga file no longer stops the app from starting: it's listed
    as unreadable and can be deleted.
  - Names containing square brackets show correctly everywhere.
  - Every delete now asks first (familiar traits, reputations and Virtues &
    Flaws, laboratory Virtues & Flaws, Mastery Abilities).
  - Bind Familiar suggests a magus only when a magus is on show.
  - Clicking an Art row no longer stops the arrow keys working.
  - An old save with a field the app no longer uses still loads.
  - Changing the theme no longer wipes other settings.
  - Renaming a character or laboratory updates its book list straight away.
  - Importing spells asks about duplicate names whatever their case.
  - Reputation scores all show as "+2".
  - Smaller fixes: the familiar sheet's details panels are shaded like
    every other sheet's, the Hermetic Magic details panel keeps its hint,
    placeholder tabs read properly, and a few rare display races are gone.

## 0.1.0

Everything before versioning began.
