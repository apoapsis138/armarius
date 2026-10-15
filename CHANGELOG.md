# Changelog

What changed in each version of Armarius (called Ars Magica Manager
before 2.52.0), newest first.

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
| Nomen Novum | 2.52.0 | The app's new name: Armarius, a saga manager for Ars Magica |
| Illuminatio | 2.45.0 to ... | The desktop version, drawn rather than printed |
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
the troupe's players are to the storyguide; an *illuminatio* is the
painted and gilded copy of a manuscript; *nomen novum* is a new name,
and an *armarius* kept a monastery's books and records.

## 2.81.0 — 2026-10-15

- **The minutes.** Each step of a meeting, once held, writes its
  minutes into the Tribunal's Diary: an entry headed with its day, what
  was done in plain words, its numbers in the margin (the votes in the
  hall, a debate's levels lost, a vote's tally, a fine) and its Note.
  Holding a step again rewrites its entry. The Diary has a new Numbers
  column, and any entry's numbers can be edited.
- **Rulings that take effect.** The Rulings step now takes, for each
  case, any fine (pawns of an Art, or pounds of silver) and who pays it,
  whether the ruling goes into the Peripheral Code, and how the other
  party's attitude toward a troupe covenant moves. When the meeting
  closes, the fines are owed to the Tribunal's treasury, the rulings go
  into the Code and the attitudes move, each with its reason.
- **The Acta.** Closing a meeting writes its Acta into the Diary: the
  meeting's acts set out as a charter (who attended, each ruling and
  its fine, the offices filled, the witnesses), which you can reword
  like any entry. On the desktop, Print prints the chosen Acta to a PDF.
- A debater now loses no more than five levels, however hard the last
  blow.

## 2.80.0 — 2026-10-15

- **The debate.** Each case and motion at a meeting is now debated by
  the rules of Houses of Hermes: Societates (The Fine Arts of Debate).
  Enter each side's debate Fatigue levels lost, or leave them blank and
  the debate is rolled round by round from the debaters' own scores
  (Communication with Folk Ken, Intrigue or Artes Liberales against
  Intelligence with Charm, Guile or Leadership), with the case's
  evidence as the prosecution's testimony and any you add for the
  defence. Each round is written down, with who won and the Argument
  Strength; a motion that adds to or alters the Code is harder to carry.
- **Calling the vote.** After each debate comes its vote. Each covenant
  starts from its leaning (a party votes its own side; any other leans
  by its attitude to a troupe covenant in the case), which you can
  change; the debate's winner then sways a share of the undecided votes
  (and, from a Triumphant Victory, of the other side's). The Meeting tab
  shows the vote covenant by covenant as the Praeco calls it, with the
  tally and a bar for the hall, and the rulings start from how each vote
  went.

## 2.79.0 — 2026-10-15

- **Hold Tribunal.** Each Tribunal has a new Meeting tab (a chapter on
  the desktop): the order of business day by day, who is in the hall,
  and the step in hand. Hold any step to open the meeting: the Opening
  (where, how many days, and the day each case and motion is heard),
  Attendance and proxies (who is absent, the proxies each covenant
  carries and whether the Presiding Quaesitor allows them), each case
  and motion with its prosecutor and defender, the Theban elections,
  the rulings, the treasury, and the Closing, which decides the cases
  with a ruling, writes the meeting into the Diary and sets the next
  one.
- **Leave and come back.** The meeting is saved after every step, so
  you can leave it at any point; holding it again resumes at the step
  in hand. Any step can be held again to change it, or the meeting
  abandoned.

## 2.78.0 — 2026-10-15

- **The world turns.** When Winter is played, Advance Season now asks
  one more question before the season is played out: what the year
  brought beyond the covenants. A place's triggers that came this year
  (written into its Diary) and, with Auras change on, the roll to raise
  a Magic aura; a threat's dated stages that have come; each fair's
  income roll; a loan due to a Tribunal; and the year's events with
  each neighbour. Each line has a tick box, and only the ticked lines
  are applied.
- **Attitudes are never guessed.** A neighbour's attitude moves only by
  the change you choose, and a change needs its reason.
- **Undo by deleting.** Everything applied goes into one entry, "The
  world turns, Winter 1220", under The World Turned on Seasons. Delete
  it to undo the lot; anything changed by hand since is left alone, and
  you are told.

## 2.77.0 — 2026-10-15

- **Ahead: what's coming.** Seasons (the tree's Seasons in the terminal,
  the Seasons page on the desktop) now opens on Looking Ahead:
  everything coming in the seasons ahead, a season at a time, worked out
  from the saga itself. Each Tribunal's next meeting and when notice of
  its cases is due; the towns' fairs (a covenant's income roll among
  them); the places' triggers; the threats' dated stages; the year a
  character's aging rolls begin and the season one comes back from
  Twilight; and the world turning each Winter.
- **How far it looks** is kept with the saga: 2 years to start with, or
  1, 3 or 5, or to the next Tribunal. Show narrows the list to one kind
  of entry (chips on the desktop).
- **Your own calendar.** Add your own entries to Ahead: once, each year
  or every so many years, for the whole saga or one covenant. A row
  worked out from another record is changed on that record.
- **Ahead for a covenant.** A covenant's Seasons tab starts with what
  concerns it.

## 2.76.0 — 2026-10-15

- **Triggers.** A place's Regio tab lists its triggers: what comes once,
  each year, every few years, or whenever something happens. The dated
  ones show their next date, and the soonest is shown as the place's
  Next.
- **Roll tables.** A place has a Roll Tables tab: name the die and write
  the rows ("1-3: Nothing stirs", "9+: The Hall opens"), then More >
  Roll (or the Roll button on the desktop) rolls it and writes the
  result to the place's new Diary tab.
- **Auras change**, a new Rule Option with Realms of Power: Magic in
  play: a Magic aura can rise by 1 on a yearly stress die plus the magic
  worked there against 15, and an Infernal aura whose focus is gone
  fades by 1 after as many years as its strength.
- Who can see each regio level now shows among the place's facts, which
  leaves room for the level list at narrower windows.

## 2.75.0 — 2026-10-15

- **Places and regiones.** The Region has a list of Places: forests,
  ruins, crags and regiones. A place has an aura, its tethers, how far
  the troupe has got with it and how widely it is known, and the
  covenant that claims it, and can sit inside another place (a regio
  inside a forest inside a county).
- A covenant, a laboratory or a neighbour can name the place it is in,
  or one of its regio levels. A covenant placed somewhere takes its aura
  from there, and gets back the aura typed on it if it is moved out; a
  laboratory built in a regio takes that level's aura.
- A place's Regio tab lists its regio levels, deepest first, each with
  its realm and aura and how to see and enter it. Write a roll as "Per +
  Awareness against 9" and it shows which of the troupe's characters
  reach it with their scores alone.
- A place's effects work for real: a lab bonus reaches the Lab Totals of
  the laboratories there, an aging or Living Conditions change reaches
  the aging rolls of those who live there, Warping a season is added to
  their yearly Warping, and an aura effect replaces a level's aura.

## 2.74.0 — 2026-10-15

- Threats and their stages. A threat has an antagonist, a way of moving
  (by fixed dates, along a track, or by an omen count) and an ordered
  list of stages, each with when it comes, its clues, and what happens
  if it is ignored, stopped or turned. Its Stages tab shows the stage it
  has reached and the next to come, worked out from the saga's date (or
  its position on the track); a stage can be marked as happened, stopped
  or turned. The Region's top panel names the threat due soonest.

## 2.73.0 — 2026-10-15

- Churches in detail (The Church). A church has a kind (a chapel up to
  an archbishop's cathedral) and an order, and a Church tab showing its
  Dominion aura and its relics, each with its saint, Faith Points,
  Might and the Magic Resistance it gives its bearer. With Realms of
  Power: The Divine in play, touching a relic adds +1 to invoking its
  saint, and a new Rule Option, Dominion growth, grows a church's aura
  with the years of worship, fades it once worship stops, and raises it
  for a relic of more than 5 Faith Points.
- Universities in detail (Art & Academe). A university or school has a
  kind and fees, and a Studium tab showing the highest it can teach,
  the degrees its faculties grant, its faculties with their rectors and
  chairs, and its masters with the Academic Reputation their licences
  start.
- Factions in detail. A faction records what kind it is, how it
  decides, its members, its rules, what it wants and what it offers, on
  a Faction tab.

## 2.72.0 — 2026-10-15

- Lords in detail (Lords of Men). A lord has a title, a wealth, his
  manors and his seat, and a Fief tab that works out his income, what he
  has to spend, the knights, serjeants, infantry and levies his title
  raises, and what he owes the neighbour he answers to (knight service
  or scutage, aids and relief). Where the book gives two figures, the
  lower is used. The tab lists his castles and the Gratitude he owes
  each character, with what its points are enough for.
- Towns in detail (City & Guild). A town has a charter, a council and a
  population, and a Town tab showing its size and how many guilds a
  town its size has in the saga's year, then its guilds and its fairs
  and markets. A fair a covenant trades at is a source of income to it;
  Roll Income rolls its year's Income Modification on a stress die and
  keeps the new income.
- Changing a neighbour's kind shows its new kind's tab at once.

## 2.71.0 — 2026-10-15

- The Region and its neighbours. A saga keeps the lords, towns, churches,
  universities, factions and threats of its region, each with its
  summary, its detail, its ruler, who it answers to and its realm, and
  its attitude toward each player covenant, the favours owed and its
  links, as a sketch covenant has. New Neighbour asks for the kind first,
  offering those whose book is in play.
- The terminal's Region sheet shows the other covenants and a list per
  group of neighbours, with each one's attitude toward the troupe and the
  chosen one's details below; each neighbour has its own sheet, under its
  group in the tree. On the desktop, the saga's page gains a Region
  chapter of neighbour cards, each opening the neighbour's own page.

## 2.70.0 — 2026-10-15

- Four more Tribunals' customs. Normandy (The Lion and the Lily): a
  Tenure tab recording who holds each vis source under the Perthean
  Compact (seisin, legacy, tropaeum, luctatio or interim lease) and until
  when, and a Tourney tab where each team's points give its rank, prize
  pawns and any named Siege. Transylvania (Against the Dark): each
  covenant's privilege class, entered with the roster's Edit and shown in
  a Class column. Provence (Faith & Flame) and Hibernia (The Contested
  Isle) add no lists: their customs are a note on the Peripheral Code
  tab, as they now are for every region.

## 2.69.0 — 2026-10-15

- The Theban Tribunal's customs (The Sundered Eagle): a Tokens and Archai
  tab with each magus's tokens, shards and liturgies served and their
  standing (an office, or ostracised and until when), and the archai who
  hold its offices, with their terms and duties. Its Your votes counts the
  troupe's tokens. Holding a Theban meeting will add its elections.

## 2.68.0 — 2026-10-15

- A Tribunal follows the core rules or one region's customs, chosen as
  Customs in Edit Tribunal; a region's customs are offered while its
  sourcebook is in play, and are never mixed. The top panel names them.
- The Rhine's customs: its covenants' gilds, each with its members and
  dues, on a Gilds tab, and a Gild column on the roster. Notice of a case
  is due a year before a Rhine meeting, a season under the core rules.
- Switching a Tribunal's customs keeps what the old ones recorded,
  hidden; switching back shows it again.

## 2.67.0 — 2026-10-15

- A Tribunal's sheet has its lists. The Roster shows each covenant's
  detail, magi, votes, the proxies it holds for the next meeting and its
  attitude toward the troupe's covenant, then the covenants not written
  down, counted; under it, the Magi of Note: the Praeco, the Presiding
  Quaesitor, the magi of its other covenants and anyone pleading a case.
- The Docket lists the cases for the next meeting (charges, motions and
  appeals), with when notice is due and whether it has been given, and
  flags the ones against the troupe. Withdraw takes a case off the
  docket; decided and withdrawn cases are kept as the Rulings of Past
  Tribunals.
- The Peripheral Code holds the Tribunal's own rulings, the Treasury its
  vis, silver, loans and fines with the balance worked out, and the
  Diary its minutes. The top panel counts the cases pending and the
  troupe's votes, proxies included.

## 2.66.0 — 2026-10-15

- Tribunals are records of their own. A covenant chooses its Tribunal
  from the saga's in Edit Covenant, and New Tribunal adds one: its name,
  how often and where it next meets, its Praeco and Presiding Quaesitor,
  and how many covenants and magi it really has.
- A Tribunal's sheet shows those facts, the troupe's votes and its roster
  of covenants with their votes. Deleting a Tribunal says which
  covenants it leaves without one.
- In the terminal, The Region sits below the troupe's covenants in the
  tree, with each Tribunal and, under it, the covenants the troupe
  doesn't play. On the desktop, the saga's World chapter lists the
  Tribunals.
- Older sagas typed a covenant's Tribunal as a name: each name becomes a
  Tribunal the first time the saga is opened, shared by the covenants
  that typed it. An exported covenant brings its Tribunal's name, and
  joins the Tribunal of that name where it is imported.

## 2.65.0 — 2026-10-15

- Covenants can be kept as a line or a sketch too, for the other
  covenants of the Tribunal. A sketch opens on its Overview: its magi
  (named ones, at any detail, plus how many more go unnamed) and the
  votes they give it, What Matters to it, its Attitude toward each
  player covenant, the favours owed either way and its links. A line
  is only who they are and their relations.
- An Attitude starts somewhere between -3 and +3 and moves only with a
  reason: what happened, by how much and when.
- Favours (who owes whom, for what, and whether it has been repaid) and
  links to other characters and covenants, which show on both records.
- Promote and Demote work on covenants. A covenant not played by the
  troupe ("Played by the troupe" in Edit Covenant) is left out of the
  seasons, and a full covenant that isn't played shows its Attitude,
  Favours and Links too.
- Bind Familiar offers only magi kept in full.

## 2.64.0 — 2026-10-15

- Characters can be kept as a line or a sketch instead of in full, the
  way the books print their NPCs. A sketch opens on its Statblock: who
  they are in the saga, then their Characteristics, Arts, the Abilities
  they have (any not listed count as 0), Virtues and Flaws, signature
  spells, Personality and Reputations. A line is only who they are.
  Sketches leave out Inventory and Planning; a line leaves out
  Abilities, Virtues & Flaws and Hermetic Magic too.
- Promote and Demote (under More in the terminal, under Manage on the
  desktop) move a character one level up or down without losing
  anything written. Promoting a sketch to full starts its creation, so
  the Creation Worksheet can check it.

## 2.63.0 — 2026-10-15

- The groundwork for the Saga World. Characters and covenants can now be
  written down at three levels of detail: a line, a sketch or in full.
  Only full records are played: sketches are left out of season plans,
  ageing, the year's accounts and creation budgets. Your existing
  characters and covenants are all full, so nothing changes for them.
- A covenant can hold an attitude toward each player covenant, from
  Hostile to Allied, worked out from where it started and every reason
  since, along with the favours owed and links to other records. The
  forms for these arrive with the sketch covenants and neighbours that
  use them.
- A Reputation can now say its type (Hermetic, Local, Noble, Academic,
  Ecclesiastical or Infernal) and how far it reaches. Both show in
  brackets on its row.

## 2.62.1 — 2026-10-14

- Opening a saga that a newer version of Armarius saved no longer loses
  what this version doesn't know about. Whatever the newer version added
  is kept through every save and backup, even though you can't see or
  change it here, and the saga stays marked as the newer version's.
- Opening such a saga now says which version saved it and which one you
  are using, so you know to update the app.

## 2.62.0 — 2026-10-14

- Help now fits the version you are using. The desktop version's Help
  describes the desktop: its window, trail, chapters, Inspector and
  buttons, with a Keys page of its own. The terminal's Help keeps its
  tree, footer and keys. Pages, sheet sections and how-to guides that
  differ between the two say what to click on the desktop and what to
  press in the terminal, and neither shows the other's.
- Where something can't be done on the desktop yet, such as Unassigned
  Books or hosting a saga for players, the desktop's Help says so and
  points to the terminal version.
- Help opened from a desktop chapter named differently from the
  terminal's tab (Charter, People, Covenfolk, Treasury, Specializations,
  Stores, Seasons) opens on that chapter's help.

## 2.61.0 — 2026-10-14

- Print to PDF lays a character out as a sheet made for paper, not a
  picture of the screen. The name is set in the title lettering, with a
  gilt edge and a bound strip down each page, and the text is real text
  you can search and copy. Nothing is cut by a page edge: a table that
  fits on a page is never split, a heading stays with what it heads, and
  empty sections are left off.
- A magus's Hermetic Arts, Grimoire and Biography each start a page. The
  Grimoire lists the spells by Form, under each Form's symbol, and every
  Art and Ability has its symbol beside it.
- Combat & Condition follows the published character sheet: boxes for
  each Fatigue level and for five Light, Medium and Heavy Wounds, the
  current ones ticked, and blank lines to pencil in weapons, armor and
  equipment.
- A Virtue or Flaw taken more than once prints once with its count, as
  Great Intelligence × 2. The screens still show each one.
- Print to PDF first asks the paper size (US Letter or A4), and for a
  character short or full spells and a parchment or plain white page. It
  remembers your choices. Covenants, laboratories and familiars still
  print their page as it looks on screen, now on Letter or A4.

## 2.60.0 — 2026-10-14

- Give: vis, books and lab texts, enchanted devices (with their
  epitome), personal gear and silver can be handed from one character,
  covenant or laboratory to another, and both sides' Diaries record it.
  Gear can be split by how many, and gear and silver never go to a
  laboratory. Characters now carry pounds of silver, and Give Silver
  gives from a character's purse or a covenant's Wealth.
- On the desktop, a magus's Sanctum button opens their laboratory (or
  makes one), and the laboratory's owner is a button back to them.
- A character can have a portrait in a gilt frame beside their name.
  The picture you choose is copied into the saves folder, and the House
  symbol shows while there is none.
- The creation worksheet shows each stage's budgets as bars (gold, red
  when over), every stage's experience in each Ability and Art with its
  total and score, and a red line naming any broken creation rule.
- Set Up Research Library walks the covenant's research subjects one at
  a time, showing which books back each bonus and the bonuses so far.
- Print to PDF, in every record's Manage chapter on the desktop, lays
  the sheet out on parchment-coloured A4.
- Export Saga writes the whole saga in one file, and Import reads it
  back as A Whole Saga.
- Every ability on the desktop has a drawn woodcut-style mark in its
  row, larger in the details panel. An ability with no mark of its own
  shows its category's.
- The Treasury reads Annual Income and Annual Expense, and every Raw Vis
  and vis store shows its Art's symbol.
- The desktop has no New or More buttons. Every action they held now
  sits on the section or page it acts on.
- Section buttons are quieter, sitting on the section title's line at
  the far right, flat with a soft shadow line. Every button in the app
  takes the same look, and a button with nothing to act on is hidden.
- The message after a step is drawn on the app's paper, with no system
  title bar.
- Windows Snap, Win+arrow keys and maximising work again with the
  desktop's own title bar.

## 2.59.0 — 2026-10-14

- On the desktop, the saga's page is in chapters. The World shows its
  covenants, unassigned characters and unassigned laboratories, each list
  ending in a blank card that makes a new one. Seasons sets the date, Rules
  and Content opens Saga Content, and Saga Management holds Edit Saga and
  Import. The row of buttons under the saga's name is gone.
- A covenant's People chapter shows every group, each ending in a blank
  New Magus, New Companion or New Grog card, and its Laboratories end in a
  New Laboratory card shaped like the labs beside it.
- A magus with no familiar has a blank Bind Familiar card where the
  familiar would be; in the laboratory it is a button beside Planning.

## 2.58.0 — 2026-10-14

- On the desktop, the actions that were in More now sit on what they act
  on: Improve beside a covenant's Sources of Income, Texts Read beside a
  magus's Hermetic Background and their laboratory's Lab Texts, and
  Perform Ritual in the laboratory's Seasons chapter.
- A spell a magus invented has a Shared tick in its Edit form, and Known
  Spells marks it once it is shared. A shared spell stays shared.
- Bind Familiar is a button on a magus who has none, and in their
  laboratory's Seasons chapter.
- Add on a covenant's Magi and Companions offers every magus or companion
  in the saga who isn't on the list: someone taken off comes back, and
  someone from another covenant moves here after asking. This replaces
  Restore on the desktop; the terminal keeps Restore too.

## 2.57.0 — 2026-10-14

- The desktop's saga page sets out what it does as a row of buttons under
  its name: Edit Saga, Import, Set Date, New Covenant, New Character and
  New Laboratory. Each button is gilt-edged, and its first letter is an
  illuminated initial.
- A covenant's People chapter opens with New Character and its
  Laboratories chapter with New Laboratory. What they make belongs to
  that covenant.
- New and More keep only what has no place on the page: Bind Familiar is
  on a covenant or a magus, not the saga, and companions and grogs no
  longer offer New.

## 2.56.0 — 2026-10-14

- Every character, covenant, laboratory and familiar on the desktop ends
  with a Manage chapter: Export, Update from a File and Delete, each with
  a line on what it does. Delete is set apart in the warning colour.
- Update from a File (also in the terminal's More, for the storyguide)
  reads an export of a record back over it, for example after working on
  it on another computer. It shows what would change first and keeps the
  record's place in the saga: its covenant, laboratory or owner.
- The record's header shows its mode, a seal for In Play or a quill for
  In Creation; click it to switch. While a record is In Creation, its
  page fades to ruled drafting vellum and the Creation Worksheet is a
  click away beside the mode.
- The desktop's More menu no longer lists what the page now offers
  itself: Export, Delete, the mode and the worksheet.

## 2.55.0 — 2026-10-13

- The desktop window draws its own title bar on the paper, in place of
  the system's: minimise, maximise and close as small glyphs at the right
  of the top bar, and the app's name in the middle. Drag the bar to move
  the window and double-click it to maximise; drag an edge or corner to
  resize it. The title page has the same buttons.

## 2.54.0 — 2026-10-13

- On the desktop, the lists that were lines of fixed-width text are now
  real tables in the app's own fonts: Enchanted Devices, Research Goals,
  Personal Gear (a table for each kind), Books, Raw Vis, the Diary, the
  covenant's season lists, Lab Texts, a laboratory's Planning, the
  Creation Worksheet's lists and the Seasons records. Long names show in
  full, headings run across the table, and problems keep their colours.
- The Creation Worksheet's budget lines up its figures in a grid.

## 2.53.0 — 2026-10-13

- The app now opens on a title page: an illuminated initial A in gold
  and knotwork, the name Armarius and its tagline, and the version.
  From it you can open the saga you had open last, choose or begin
  another saga, or read Help. Enter takes the first of these.
- The terminal version opens on a matching title card in front of the
  saga picker. Players joining a hosted saga skip it.
- The app remembers the saga you opened last.

## 2.52.0 — 2026-10-13 — Nomen Novum

- The app is now called **Armarius**, a saga manager for Ars Magica.
  The title bar, the saga picker, Help's About page, the desktop
  window and the hosted browser tab say so.
- Your save folder's default is now `Armarius` at the top of your
  OneDrive. The first time the app starts, it renames the old `Ars
  Magica Manager` folder and says so. A folder you chose yourself stays
  where it is; if both folders exist, nothing is merged and `Armarius`
  is used.
- Everything set up under the old name still works: a save folder you
  chose, the `ARS_MAGICA_MANAGER_DATA` and
  `ARS_MAGICA_MANAGER_TRANSPORT` environment variables (now also
  `ARMARIUS_DATA` and `ARMARIUS_TRANSPORT`), and exports made before
  the rename, which still import.

## 2.51.0 — 2026-10-13

- Advance Season is on the desktop, as a button in the top bar. After a
  season with plans, a Seasons page shows what it did; the saga page
  opens the seasons kept.
- Advancing asks the same questions in both: at the year's end with a
  covenant in deficit, whether to advance anyway; each contested
  resource secured, and each Discovery taken, is a tick on one form.
- Help on the desktop: F1 (or Help in the top bar) opens the help pages
  on the page you're looking at, with the guides and a filter.
- The desktop's Sagas page has New Saga, Change Save Folder and a Delete
  on each saga.
- A laboratory's Lab Texts on the desktop can be filtered by kind, Arts,
  level and whether the owner can read them.
- Import chooses its file in the desktop's Open window. In the terminal,
  Books comes first in the Import list, a duplicate's question offers
  Skip first, cancelling it imports nothing, and the spell CSV help is a
  form with a tick to save an example.
- Invent a Spell refuses a number box that isn't a number, rather than
  reading it as 0.

## 2.50.0 — 2026-10-13

- The Creation Worksheet is on the desktop: a new character, covenant or
  laboratory opens on it, each step listed down the side with its
  budget, what's been spent, its checks and its buttons, ending with
  Move to In Play. The terminal and the desktop now share one worksheet,
  so both offer the same steps.
- Lists to choose from are searchable on the desktop, and a Show
  everything switch lists what isn't offered too, each marked with why
  (the terminal's F3). In the terminal, the sample childhoods, training
  packages, Covenant Situations and the saga's books a new covenant may
  buy are searchable lists too.
- Enchanted devices on the desktop: characters, laboratories and
  covenants show the devices they hold, with Instill an Effect and Use a
  Charge.
- A laboratory's Specializations can be turned off and on from the
  desktop, and several books can be given one new owner at once.
- On the worksheet's Virtues step, Add a Virtue and Add a Flaw are
  separate buttons.

## 2.49.0 — 2026-10-13

- The desktop version can now edit everything it shows. Every section of
  a character, familiar, laboratory, covenant and the Saga Content page
  has Add, Edit and Delete buttons, using the same forms and rules as
  the terminal, and a deletion always asks first.
- Forms, lists to choose from and delete questions open in place, inside
  the section they belong to, rather than in a separate window; the
  rest of the page waits until the step is saved or cancelled.
- Seasons can be planned on the desktop: a character's, a laboratory's
  and a covenant's season plans are added, changed and cleared there.
- Each desktop page has New and More menus with the terminal's rarer
  actions, including creating characters and deleting records.
- The books on the library shelves have larger spine titles that can
  run to two lines, so a long title makes a thicker book.
- Every desktop page fits a 1280-pixel-wide window without scrolling
  sideways.
- The message for a reputation score out of range now reads "between -3
  and +3".

## 2.48.0 — 2026-10-13

- The desktop version has a Saga Content page, opened from the saga's
  page under "The Saga's Books and Rules". It shows which books are in
  play, the saga's own sources, the catalogs and what is hidden from
  them, the House Rules as cards with their points, and every spell the
  saga can use, which can be searched, filtered and sorted as on the
  terminal, plus the players and who they play.
- Every desktop page is set with printer's ornaments: a headpiece band
  across the top, a hedera leaf opening each heading's rule, a tailpiece
  closing each chapter, and gilt flourishes in the corners of every card
  and the inspector.

## 2.47.0 — 2026-10-13

- The desktop version has a page for each covenant, with every chapter of
  the terminal's covenant sheet. The header shows the Tribunal, season and
  founding, the Aegis of the Hearth and living conditions, and the aura
  and Loyalty as seals. Its chapters: the charter (the description, Boons
  and Hooks as cards, Reputations), its people, covenfolk with Loyalty,
  laboratories, possessions, the treasury as a year's account, the
  library, its seasons, the Diary and the Build Points.
- The library stands its books on wooden shelves, bound in muted leather
  with gilt lettering: each spine carries its Art's symbol, its whole
  title and its level and quality. The shelves fill to the page's width.
- Every desktop page now lies on paper (vellum by candlelight in the dark
  theme), darker toward its edges; cards, seals and the inspector sit on
  it with soft shadows, and the bookcase has depth.
- A familiar has its own page, opened from its covenant's people or its
  magus's sheet: its Magic Might as a seal, its Characteristics, the
  binding, the three Cords as twisted cords of gold, silver and bronze
  with a knot for each point, its Virtues and Flaws, health and natural
  weapons, Abilities, and Bond Powers as cards.

## 2.46.0 — 2026-10-13

- The desktop version has a page for each laboratory, opened from its
  card on the covenant's page. The header shows whose sanctum it is, the
  Size its Virtues and Flaws take up, the free Virtues left, the Base
  Safety, and the aura as a seal in its realm's colour. The eight
  Characteristics are drawn as a compass rose, each point as long as its
  score (gilt when it adds, red when it takes away), beside a card each
  that shows what you typed and what the Virtues and Flaws add.
- Its chapters: the owner's Lab Total for every Technique and Form as a
  coloured grid (click one to see its terms), with the Base Lab Total and
  what each activity adds; the Virtues and Flaws as cards; Specializations
  as bars, with the Features and rooms; the stores (raw vis, equipment,
  Arcane Connections, books); and the lab's seasons as a calendar beside
  its diary.

## 2.45.0 — 2026-10-13 — Illuminatio

- The desktop Character sheet is laid out as a codex: a chapter list on the
  left, the chapter in the middle, and a panel on the right that shows
  whatever you click (an Art, a Virtue, a spell, a casting score). The
  header shows the House symbol, the name with a red initial,
  Confidence, and Warping and Decrepitude as dials: the arc and its notches
  fill with the points toward the next score, and wind up as the sheet
  opens. Characteristics are cards; the Arts are two tables, Techniques
  beside Forms, each with its score and a bar of experience toward the next,
  like the Abilities; every casting score is a coloured grid; the known
  spells sort and filter; Virtues and Flaws are cards.
- The Description chapter sets its facts in the book's type with unset
  fields dimmed, the Biography opens with a red initial, Personality Traits
  and Reputations are bars, wounds are a row of boxes and Fatigue a ladder.
- No more tree or saga drop-down: a trail across the top (Sagas, the saga,
  the covenant, the character) leads back up. A saga shows its covenants
  as cards; a covenant shows its people (Magi, Companions, Grogs) and
  laboratories as cards, and a timeline of everyone's seasons, coloured by
  kind of activity, with planned seasons dashed. A character's Diary opens
  with the same seasons as a calendar, a row per year.

## 2.44.0 — 2026-10-12

- A first look at the desktop version: `run-gui.bat` (or `uv run --group gui
  python gui.py`) opens a window with your saga's covenants and characters
  and a read-only Character sheet, with the same tabs and text as the
  terminal's, the Arts' symbols, the House symbol beside a magus's name and
  the Scriptorum light and dark themes. It never saves, so it is safe to
  open beside the terminal app. The terminal's Character sheet now reads
  its text from the same shared place, and shows exactly what it did.
- The desktop version's libraries now come with the developer install
  (`uv sync`), so the automatic checks cover it too.

## 2.43.5 — 2026-10-12

- Behind the scenes, preparing for the desktop version: the fifteen Arts
  and the Houses now have their symbols, traced from the artwork Atlas
  Games has released under its open licence (Guernicus shows the
  Quaesitor's), along with a set of everyday icons, the Order of Hermes
  sigil as the app icon, and the EB Garamond and Uncial Antiqua fonts.
  Help's About page credits them all. The terminal version doesn't show
  them, so nothing in the app itself changed.

## 2.43.4 — 2026-10-12

- Behind the scenes, preparing for the desktop version: the terminal
  screens now sit in a package of their own beside an empty one for the
  desktop window, and the desktop's libraries are an optional install
  (`uv sync --group gui`) so the terminal install stays as it is. The app
  starts and works exactly as before.

## 2.43.3 — 2026-10-12

- Behind the scenes, preparing for the desktop version: an automatic check
  now makes sure the shared rules, saga and form code never depends on the
  terminal screens, so a second front-end can use it unchanged. Nothing in
  the app itself changed.

## 2.43.2 — 2026-10-12

- The automatic checks run about a quarter faster (from about 32 to about
  24 minutes when run one at a time), with the same coverage: screen tests
  open only the sheet and tab they look at, the key-routing check notes
  which form a key opens without drawing it, and the list and sheet-text
  checks share one app session where they repeated it. Nothing in the app
  itself changed.

## 2.43.1 — 2026-10-12

- Behind the scenes, first step toward a desktop version: what each form
  asks for and how its entries are checked, and what can be done in each
  part of a sheet (add, edit, delete, and the More and New menus), now
  live outside the terminal screens, so a second front-end can share
  them. Nothing in the app looks or behaves differently.

## 2.43.0 — 2026-10-12

- You can choose where your sagas, backups, exports and settings are
  kept: More (`m`) on the saga picker has Change save folder. It checks
  the folder can be written to (some system settings, or a synced or
  read-only folder, may not allow it), offers to move your files there
  without overwriting anything, and remembers the choice. The saga
  picker always shows which folder it is reading and why.
- Many more Virtues and Flaws now change the numbers they should:
  Student of (Realm) and the Faerie Blood heritages' Ability bonuses,
  Characteristic bonuses taken at creation, Soak and Protection, Wound
  and Fatigue penalties, aging rolls, Magic Resistance and Penetration,
  casting totals, and creation experience. The blood kinds from Realms
  of Power: Faerie are in the catalog, and spontaneous casting text names
  its Fatigue cost.
- On the covenant creation worksheet, each Lab Text and Casting Tablet
  has its own row under the Lab Texts pool, so you can edit (`e`) or
  delete (`d`) one there; the pool's levels and Build Points update.

## 2.42.0 — 2026-10-09

- Planning an Initiation now says what its Ordeal costs: the Initiate
  gains a Flaw, loses one of their Minor or Major Virtues, or has one of
  their Minor Flaws raised to a related Major Flaw. The Ordeal's size
  follows from that (a raised Flaw is a Medium Ordeal), so the separate
  Ordeal size choice is gone. A successful Initiation takes the lost
  Virtue away (with its point, for a Great Characteristic) or replaces
  the raised Flaw; a failed one changes nothing. Plans made before keep
  their Ordeal Flaw.

## 2.41.0 — 2026-10-09

- The Spells tab lists only the spells whose book is in play, plus the
  saga's own. The Source filter's new "Not in play" choice shows the
  rest, and choosing a book shows its spells whether it is in play or
  not. A spell out of play, or hidden in this saga, is marked "(not in
  play)" there and in a character's Known Spells, and its details say
  why; a magus who knows it keeps it.
- Planning an Initiation: Virtue initiated and Ordeal Flaw open the
  Virtues & Flaws picker, which asks for anything the entry names (an
  Affinity's Art), and the Virtue is added with it. Picking the Flaw sets
  the Ordeal size, and a size that doesn't fit the Flaw is refused.
  Leaving the Mystagogue blank plans a self-initiation, which the form
  couldn't before. The Mystagogue must know the Lore, and the Initiate
  needs it at 1 unless it is their own House's.
- Undergo an Initiation is offered without The Mysteries in play: its
  rules are in the Definitive Edition.
- In any form, Delete clears a chosen value that may be left empty.
- A new how-to guide, How to initiate a character into a Mystery.
- Fixed: only the latest Ordeal was remembered, so a smaller Ordeal after
  a bigger one lost the bigger one's help. Every Ordeal now counts down
  on its own, and an Initiation's Target takes the largest reduction.

## 2.40.0 — 2026-10-09

- A new Saga Content node in the tree gathers what the saga's pickers
  offer, in tabs: Books, Catalogs, House Rules, Spells and (for the
  storyguide) Players. It replaces the separate Spells, House Rules and
  Players nodes, and the books in play move there from Edit Saga.
- Saga sources: the saga can have sources of its own (a house-rules
  list, a fan supplement) that House Rules entries cite. A source is put
  in or out of play like a book; renaming one carries over to the entries
  citing it, and one still cited can't be deleted.
- Catalogs: a saga can stop offering a whole catalog (Virtues & Flaws,
  Lab Virtues & Flaws, Boons & Hooks, Abilities, Spells, Shapes &
  Materials) or single entries in it. Pickers leave them out as if their
  book were out of play (F3 shows them); the saga's own entries are always
  offered, and the shared catalog files are never changed.
- Everything a supplement adds now switches off with its book: the
  season activities it brings, its optional rules (Harsher Infernal vis,
  Extended book Quality: hidden and off, the choice kept), the library's
  book kinds and fields (commentaries, florilegia, epitomes, palimpsests,
  encyclopedias and more), Gloss it while reading, and Research Bonuses.
  Anything already using one keeps it.

## 2.39.0 — 2026-10-09

- Correspondence: a tractatus can be a bound correspondence, read at the
  two writers' Communication added, or an expert correspondence (120 or
  more letters each), which also raises its library's research on the
  subject. Plan Season's Correspondence on adds 1 xp in a subject for a
  season of useful letters.
- A summa or tractatus can be glossed (+1 Quality, once) -- in the book
  form, or while reading it with Gloss it, which checks the reader. Edit a
  florilegium binds the tractatus on one subject into a florilegium (+1
  Quality each, +2 for an authority's).
- A congregational book can be read by several magi in one season.
  Pictorial works on a subject raise the library's research one level (10
  Build Points, a new Build tab row). Recorded lectures become lecture
  commentaries, which don't count against a teacher's tractatus and are
  limited by the teacher's score.
- A book can be an epitome: enchanted as an item (material level 2, size
  x4), held where the book is kept. The shape list has the Book shape's
  bonuses.

## 2.38.0 — 2026-10-09

- A Casting Tablet's details show each magus of its covenant casting
  from it: Stamina + Technique + Form + Aura before the stress die, and
  what each die gives by the Definitive Edition's table, from one Fatigue
  level down to not casting it, with Warping Points and a Twilight check.
  Reading a tablet needs Artes Liberales 1 and Latin 4.
- Write Casting Tablets, a magus's season: tablets of a spell they have
  mastered, as many as Latin x 20 levels holds. Copy Lab Texts copies
  Casting Tablets too.

## 2.37.0 — 2026-10-09

- Library research shows its roll: Intelligence + the Ability + the
  better of the covenant library's research bonus for it and its best
  encyclopedia's, against the storyguide's Ease Factor.
- "Read a commentary, florilegium or glossed book" is no longer offered:
  Read a book adds those bonuses itself. An older plan using it says to
  plan Read a book instead.

## 2.36.0 — 2026-10-08

- A new optional rule, Extended book Quality (Edit Saga), uses Covenants'
  extended rules: a book's Quality is built from parts. An author gives
  Communication + 3 instead of + 6, and the book form records a skilled
  scribe, binder and illuminator (+1 each), resonant materials (+1 bought,
  +2 from a story), clarification (+1) and a gloss (+1), all counted in
  its Build Point cost. A book's details warn of what can't go together
  and of an Art book over what it effectively reaches.
- The guides cover reading codices, commentaries, florilegia, folios and
  books still to be set, the library's research bonuses, and the bundled
  ArM5 book package.

## 2.35.0 — 2026-10-08

- A tractatus can be a commentary on a summa (the book form's Opus and
  Commentary on): read at +1 Quality, which its Build Point cost leaves
  out, and only after a season studying its summa -- the season plan notes
  it when no such season is on record. Summae studied are now recorded.
- A codex can be a florilegium (tractatus on one topic, each at +1
  Quality, or +2 when edited by an authority) or a folio (reading one of
  its books also gives 1 xp in Order of Hermes Lore).
- A book's physical form: an exemplar (-3 Quality), a flap-bound book
  (-1), juvenilia (-3), or one that changes nothing by a set amount, such
  as an edition de luxe or a damaged book.
- A book's details show what its Quality is read at and why, and a Kind
  line names its opus and form. A book import reads opus and
  physical_form columns.

## 2.34.3 — 2026-10-08

- Fixed: on a shorter screen (120x45) a covenant's Library tab had room
  for one book row, or none once a book was chosen. Book rows no longer
  wrap onto a second line (a long one is cut short), the Library Summary
  takes four rows instead of seven, and the details panel gives up rows,
  its text scrolling, so the book list always keeps five.

## 2.34.2 — 2026-10-08

- Behind the scenes: the data model is split into one module per kind of
  record (characters, covenants, laboratories, books and so on) instead of
  one very long file. Nothing about saving or loading a saga changes.
- Behind the scenes: importing a covenant, laboratory or character, and
  the book form, are each built from smaller pieces. Both work exactly as
  before.

## 2.34.1 — 2026-10-08

- Behind the scenes: three hand-built dialogs (a Familiar's Binding &
  Cords, Improve Income and Spell Mastery) are now ordinary forms like the
  rest. Each Cord's choices show their point cost, Improve Income still
  asks before changing the income, and a spell's Mastery Abilities are
  added, edited and deleted in a small list, like a device's components.
- Behind the scenes: choosing a tree node, working out a supplement
  season (Labor Points, workshops, initiation and the rest), and the
  enchanting and spell-lab seasons are split into small pieces, and the
  sheets' code is split into one file per sheet. Nothing else changes.

## 2.34.0 — 2026-10-08

- On a new covenant's Resources step, a can buy one of the saga's own
  books (Unassigned Books, such as an imported book list): the picker
  lists only those a new covenant may buy, with their Build Points, and
  F3 shows the rest marked with why. The covenant gets its own copy; the
  saga's book stays where it is.

## 2.33.0 — 2026-10-08

- An Illusory Resources Hook's 250 Build Points can be tracked in play,
  the same way as Hidden Resources: a Diary Story Event linked to one has
  a Build Points found illusory field, counted once the event is
  Resolved and never past the Hook's 250. The Hook's row shows how much
  has been found out ("60/250 BP"), its details list the Story Events
  that revealed it, and the Build tab shows the pool, what's found
  illusory and what's still believed real, apart from its totals.

## 2.32.0 — 2026-10-08

- A Hidden Resources Boon's 250 Build Points can be tracked in play. A
  Diary Story Event linked to one has a Build Points unlocked field; once
  the event is Resolved its points count against that Boon, and the form
  refuses more than the Boon has left. A Boon can be unlocked over
  several stories.
- The Boon's row shows how much is unlocked ("120/250 BP"), and its
  details list the Story Events that unlocked it. The Build tab shows the
  covenant's Hidden Resources pool, what's unlocked and what's still
  hidden, apart from its totals. Only the points are recorded: what was
  found (vis, books, items) is added on its own tab as usual.

## 2.31.0 — 2026-10-08

- A summa's or tractatus's details show its value -- Excellent, Sound,
  Vain or Discarded, from its Quality against its Level -- with a guide to
  its price: in vis for a book on an Art, an Arcane Ability or a
  supernatural power, about a pound for a mundane book.
- Research Bonuses (More, on a covenant's Library tab) sets how well the
  library serves research on each subject it has a book on, from None to
  +5 (a few books, a respectable collection, a broad and deep one,
  specialized, peerless), with what the library holds on each as a guide.
- A codex can be marked as an encyclopedia (or by a book import's new
  encyclopedia column): it aids research on its own, +1 for each of its
  tractatus on the subject. A book's details give its subject's research
  bonuses, and the Library Summary counts the subjects aided.

## 2.30.1 — 2026-10-08

- Fixed: the delete confirmation and the duplicate-book question during an
  import are drawn in a framed box again, like every other dialog, instead
  of as bare text over the dimmed screen.

## 2.30.0 — 2026-10-07

- The ability catalog gains the supplement abilities the ArM5 books index
  uses: the Divine's Adjuration, Blessing, Holy Music, Kabbalah and
  Merkavah, Mechanica of Heron, Mythic Herbalism and Theology: Pagan. Each
  is offered only while its book is in play.
- A new Hedge Art category holds a hedge tradition's Arts: Elementalist
  Air, Earth, Fire and Water, and Medicinal Divining. Like a Supernatural
  Ability, one is bought at creation through the Virtue that grants it.

## 2.29.0 — 2026-10-07

- A book can come in with its Level or Quality still to be set: "var"
  (or "variable") in a book import's level or quality column. The book is
  highlighted until you edit it to give its numbers, can't be studied
  until then, and its cost reads "to be set". A blank cell is still
  refused.
- A summa or tractatus missing its Level or Quality is highlighted the
  same way.
- Fixed: a highlighted book's warning mark no longer wraps onto the next
  line of the book list.

## 2.28.0 — 2026-10-07

- Books can be bound together in a codex: one tome holding several
  books, such as a tractatus and two summae on related subjects. Choose
  it in a book's new Codex field (or start a new one). A codex's books
  are listed together in the Library, and the details panel names the
  codex. Each book is still studied on its own, but only one reader can
  use the codex in a season, and moving one of its books moves them all.
- A palimpsest is a codex written over a scraped text: each text in it is
  read, and priced, at -3 Quality.
- Two characters can no longer both read the same book in one season.
- A book import's new codex column binds the rows that share a codex
  name; exporting a covenant or character takes its codices along.

## 2.27.0 — 2026-10-07

- The covenant worksheet's Review step says how many grogs and other
  covenfolk the creation baseline gives for free (about one grog and two
  others per magus), to add on the Inhabitants tab once the covenant is
  In Play.

## 2.26.0 — 2026-10-07

- Use a base covenant, on the covenant worksheet's Baseline step, starts
  from one of the book's Weak (200 Build Points), Medium (800) or Powerful
  (2000) covenants: it sets the Power Level and Build Points and adds the
  books and vis as placeholders whose subject or Art you choose. Its Lab
  Text and enchanted item levels are an allowance Resources counts
  against what you add. Choosing another replaces the placeholders the
  first one left unfilled.
- Moving a covenant to In Play with Build Points left says so, and turns
  them into Mythic Pounds in its Wealth (10 for each Build Point). They
  are only ever converted once.
- Review advises when a covenant has fewer servants or teamsters than its
  inhabitants need.
- Starting income counts each Secondary Income Boon as another Typical
  source.

## 2.25.0 — 2026-10-07

- New Covenant also asks for the covenant's Season and Aura realm (Magic
  unless you say otherwise), and a new covenant starts at the creation
  baseline's aura of 3.
- The covenant's Creation Worksheet has new steps: Baseline, Resources,
  Boons & Hooks and Review.
- Baseline: Power Level and Build Points, the season and aura, a Covenant
  Situation, and the starting income. Set starting income makes one
  Typical source (100 pounds a year) or two Lesser (40 each), or what a
  Poverty Hook or Wealth Boon allows. A new optional rule, Starting income
  by number of magi, adds or takes 15 pounds (6 for a Lesser source) for
  each magus over or under six.
- Choosing a second Covenant Situation warns first, then replaces the
  Boons and Hooks the first one brought; ones you added yourself stay.
- Resources: a tally of Build Points by category, then everything they
  bought, with a to buy a book, vis source, vis stock, enchanted item or
  specialist, and e and d on any row.
- Buy a Specialist picks the Ability from the Ability picker, and the
  Ability decides where they belong: a Craft makes a craftsperson, a
  Martial Ability a member of the turb, anyone else a specialist.
- A Contested, Indiscreet or Dwindling Resource Hook names the vis or
  income source it is about, which marks that source; until then it says
  it needs its source.
- New creation checks: a Faerie aura needs the Faerie Aura Hook, other
  realms are outside the creation rules, and the starting income should
  be one of the book's choices.

## 2.24.0 — 2026-10-07

- The covenant's Creation Worksheet shows what was added. Build Points
  lists every book in the Library with its points (one with no level or
  Quality yet shows 0, marked not priced), then vis, enchanted items,
  laboratories and specialists, with what is spent and left; a adds a
  book, e and d edit or delete one.
- Boons and Hooks lists each one with its points and rules: a adds a
  Boon, e edits the chosen one and d removes it.
- A laboratory's Setting Up step lists its Virtues and Flaws with their
  rules: a adds one, d removes one.

## 2.23.0 — 2026-10-07

- The Creation Worksheet opens by itself when you make a new covenant,
  laboratory or character, and fills the screen.
- Each step lists what was spent or taken there, with the chosen row's
  details below: a adds, e changes the chosen row and d takes it back,
  like every list on the sheets. The Change one, Take back one, Remove
  one, Drop a package, Spell details and Forget a spell buttons are gone.
- xp rows show the pool xp spent and the xp it gained (half again with an
  Affinity), the score and the Specialty. Taking xp back gives back the
  pool xp and takes off exactly what it gained.
- Spending xp shows, as you type, what it gains, the score that buys and
  the pool xp the next score needs, with what the Ability or Art covers;
  it warns past the creation cap, and an Ability's Specialty can be set
  there too.
- The Virtues and Flaws step shows the full rules of the chosen one, and
  the Virtue picker shows each entry's book text, not just a summary.
- An Affinity with an Ability raises its creation cap by 2, and Mentored
  by Demons lifts the cap.
- While a character is In Creation, Edit Ability and Edit Arts say how
  much xp came from the worksheet, to be taken back there.

## 2.22.1 — 2026-10-07

- The live score while editing XP now shows the total the next score
  needs, like the XP field beside it, rather than the xp still to gain:
  "Latin: Score 2 · Score 3 at 30 xp", with the Ability's name first.
  Edit Arts shows it in Score and Next at columns. The Affinity note
  is gone from these forms, which hold totals.

## 2.22.0 — 2026-10-07

- Editing an Ability's or Art's XP shows, as you type, the score it buys
  and the xp still needed for the next, e.g. "Score 3 (5) · 13 xp to
  next". This replaces the table of scores under the Ability's XP, and
  works when adding an Ability, for a familiar's Abilities and beside
  every Art in Edit Arts. A fixed bonus such as Puissant shows the score
  used in brackets; with an Affinity it also says how much xp gained
  before the Affinity's half again reaches the next score ("9 with
  Affinity").

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
