# Changelog

What changed in each version of Ars Magica Manager, newest first.

Versions are `MAJOR.MINOR.PATCH`: MAJOR marks a finished phase of the
plan (1.0.0: Phase 1, the core tracker), a new or changed feature bumps
MINOR, a bug fix or behind-the-scenes improvement bumps PATCH. The version is set in
`pyproject.toml`, shown in the app's title bar and on the saga picker, and
recorded in every saga file that version saves. Each version is tagged in
git (`v0.2.0`, ...).

## 1.6.0 — 2026-09-29

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

## 1.5.0 — 2026-09-29

- After a season with plans is played out (t), a summary shows what each
  person did and what it gave, by covenant, and who had nothing planned.
- A new Seasons entry in the tree lists past seasons, newest first; choose
  one to read its record again.
- Edit Saga has "Keep season records" (on by default). Off, the summary
  still shows after each season, but it isn't saved; the characters'
  Diaries keep their entries either way.

## 1.4.0 — 2026-09-29

- Each covenant has a new Seasons tab, after Inhabitants: its magi,
  companions and grogs, each with what they have planned for the season
  (or "nothing planned"), and a count of who has planned in each list.
  Choose someone to see their plan and what it will give; e plans their
  season and A clears it.

## 1.3.0 — 2026-09-29

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

## 1.2.0 — 2026-09-29

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

## 1.1.0 — 2026-09-29

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

## 1.0.0 — 2026-09-29

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

## 0.10.0 — 2026-09-28

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

## 0.9.0 — 2026-09-28

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

## 0.8.0 — 2026-09-27

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

## 0.7.0 — 2026-09-27

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

## 0.6.0 — 2026-09-27

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

## 0.4.0 — 2026-09-27

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

## 0.2.0 — 2026-09-27

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
