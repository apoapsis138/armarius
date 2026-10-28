# Changelog

What changed in Armarius (called Ars Magica Manager before 2.52.0), by
feature. Each feature has a name that stays; each finished round of work
on it is an edition of that feature, numbered as a book's editions are
(Peregrinatio I, II, III...), and work not yet finished is its next
edition, in progress. The Chronicle lists every version, newest first,
under the name of its major version, and the end of the page says where
the names and numbers come from.

The names come from the books and crafts of a medieval scriptorium and a
Hermetic covenant: a *pagina* is a page; the *computus* was the
reckoning of dates; a Book of Hours follows the labours of the seasons;
a *florilegium* gathers extracts from many books; the Gauntlet makes an
apprentice a magus; a *scriptorium* is where books are written; a
*glossa* is a note in the margin; *fundamenta* are foundations;
*sodales* are fellow magi of the Order, as the troupe's players are to
the storyguide; an *illuminatio* is the painted and gilded copy of a
manuscript; the *orbis* is the world; a *concilium* is a council;
*insignia* are marks of honour; and a *peregrinatio* is a journey into
other lands. Each major version has a name of its own: an *incipit* is
the opening words of a manuscript, a *folio* a sheet folded into leaves,
a *codex* the bound book, and a *nomen novum* a new name.

Versions are `MAJOR.MINOR.PATCH`: MAJOR marks a finished phase of the
plan (1.0.0: Phase 1, the core tracker; 2.0.0: Phase 4, creation by the
book; 3.0.0: Phase 5, the Saga World), a new or changed feature bumps MINOR, and a bug fix or
behind-the-scenes improvement bumps PATCH. The version is shown in the
app's title bar and on the saga picker, recorded in every saga file that
version saves, and tagged in git (`v0.2.0`, ...).

## Features

| Feature | What it is |
| --- | --- |
| Pagina | The sheets for characters, covenants, laboratories and familiars |
| Computus | The rules engine: scores, totals and the book's arithmetic |
| Book of Hours | Seasons planned and played out: study, lab work, books and gifts |
| Florilegium | The catalogs and what a saga offers from them |
| Gauntlet | Creating covenants, laboratories and characters by the book |
| Scriptorum | The terminal version: its keys, colours and readability |
| Glossa | Help, its guides and this page |
| Fundamenta | Your data, packaging, and the app's upkeep and checks |
| Sodales | Sharing a saga with the troupe |
| Illuminatio | The desktop version, drawn rather than printed |
| Orbis | The saga's world: its region, people, places, threats and what lies ahead |
| Concilium | Tribunals, their customs and their meetings |
| Insignia | Heraldry and the app's artwork |
| Peregrinatio | The Tribunal packs: each Tribunal book, ready to import |
| Hedge Magic | The non-Hermetic traditions: their Arts, chapters and rules |

## Editions

| Edition | Title | Finished in | What it brought |
| --- | --- | --- | --- |
| Pagina I | The core tracker | 1.0.0 | Characters, covenants, laboratories and familiars kept in full, with enchanted devices |
| Computus I | The rules engine | 1.2.0 | Scores from experience, casting and lab totals, and the Virtues and Flaws that change them |
| Book of Hours I | The seasons | 1.8.0 | Seasons planned and played out: study, teaching, lab work, books, aging and apprentices |
| Book of Hours II | The library | 2.39.0 | Codices, palimpsests, commentaries, correspondence, casting tablets and library research |
| Book of Hours III | Gifts | 2.60.0 | Give vis, books, devices, gear and silver from one record to another |
| Book of Hours IV | The Labours of the Months | 2.122.0 | Seasons planned a year ahead and laid out on a calendar: paired plans, repeating work, defaults for empty seasons, and previews that count the seasons before them |
| Florilegium I | Checked against the books | 0.10.0 | The reference catalogs, checked entry by entry against the books |
| Florilegium II | The Definitive Edition | 2.30.0 | The spell catalog rebuilt from the Definitive Edition, and every picker showing its entry's rules |
| Florilegium III | Saga Content | 2.41.0 | What a saga offers, gathered in one place, with sources and catalogs it can switch off |
| Florilegium IV | Renamed choices | 2.100.0 | Edit changes what a Virtue, Flaw, Boon or Hook names, without taking it again |
| Gauntlet I | Creation by the book | 2.4.0 | Phase 4: creating covenants, laboratories and characters by the book, step by step |
| Gauntlet II | Exemplar | 2.6.0 | Character templates that fill in a whole sheet |
| Gauntlet III | The covenant worksheet | 2.34.0 | A covenant built from its Baseline, Resources and Build Points, with its checks |
| Scriptorum I | Highlights | 0.4.0 | Highlights in the theme's own colours |
| Scriptorum II | Verbum | 2.5.0 | The keyboard rework: one key per verb |
| Scriptorum III | Readability | 2.9.0 | The readability pass: fields, headings, warnings and columns |
| Glossa I | Help for what has focus | 2.8.0 | Help for whatever has focus |
| Glossa II | Summa | 2.13.0 | How-to guides in Help, and this page |
| Glossa III | Help for each version | 2.62.0 | Help written for the terminal or the desktop, whichever you use |
| Glossa IV | Each pack's assumptions | 2.102.0 | A page for each Tribunal pack saying what it assumed where its book is silent |
| Fundamenta I | Foundations | 2.11.0 | Your data in its own folder, safe saves, packaging and automatic checks |
| Fundamenta II | Your own folder | 2.43.0 | Choose where your sagas, backups, exports and settings are kept |
| Sodales I | The troupe | 2.18.0 | The saga hosted for players' browsers and SSH, with sign-in and safe saves |
| Illuminatio I | The desktop | 2.51.0 | The desktop version, with a page for every record and everything editable |
| Illuminatio II | The title page | 2.61.0 | The title page, the window's own title bar, chapters, gifts and printing to PDF |
| Illuminatio III | Gilt | 2.92.0 | Gilt initials, ruled ledgers, manuscript drop-downs and sounds |
| Illuminatio IV | Keys | 2.96.0 | The terminal's keys on the desktop |
| Orbis I | Lines and sketches | 2.65.0 | Characters and covenants kept as a line or a sketch, with attitudes and favours |
| Orbis II | The Region | 2.73.0 | The Region and its neighbours: lords, towns, churches, universities and factions |
| Orbis III | The world turns | 2.78.0 | Threats, places and regiones, triggers, Ahead, and the world turning each winter |
| Orbis IV | Ruins | 2.93.0 | Ruined covenants, and new covenants founded on them |
| Concilium I | Tribunals | 2.70.0 | Tribunals as records of their own, with each region's customs |
| Concilium II | Hold Tribunal | 2.83.0 | Tribunal meetings held step by step: debate, the vote, rulings and the Acta |
| Insignia I | Arms | 2.86.0 | Coats of arms for covenants, lords, towns and factions, and proxy sigils |
| Insignia II | New heraldry | 2.95.0 | New charges, furs and divisions, a proper lion, and clean artwork |
| Peregrinatio I | Guardians of the Forests | 2.88.0 | Content packs, and the Rhine Tribunal as the first, every magus statted |
| Peregrinatio II | The Lion and the Lily | 2.94.0 | The Normandy Tribunal pack |
| Peregrinatio III | Faith & Flame | 2.95.0 | The Provence Tribunal pack |
| Peregrinatio IV | The Sundered Eagle | 2.99.0 | The Bestiary in the packs, and the Theban Tribunal pack |
| Peregrinatio V | Against the Dark | 2.102.0 | The Transylvanian Tribunal pack, with its oppida and five legal covenants |

## Major versions

| Major | Name | What it marked |
| --- | --- | --- |
| 0 | Incipit | the first sheets, catalogs and checks |
| 1 | Folio | Phase 1 finished: the core tracker, the rules and the seasons |
| 2 | Codex | Phase 4, creation by the book, and the app that became Armarius |
| 3 | Nomen Novum | Phase 5, the Saga World, and the desktop at parity with the terminal |

## Milestones

| Milestone | Version | What it marked |
| --- | --- | --- |
| Armarius | 2.52.0 | the app's new name |

## 3.35.0 — 2026-10-28

### Pagina

- A magus can stay as a guest at another covenant of the saga: Stay as
  Guest, beside Current Location, says where, since when and until when,
  the yearly fee (pawns of vis, pounds of silver, seasons of service or
  none), whether he may use its library and has a laboratory there, and
  the conditions of his hospitality. Arriving and leaving are written in
  his Diary and the host's.
- A host of a Rhine Tribunal fills in its Peripheral Code's terms: three
  to seven years, three pawns of vis a year, no laboratory owed.
- The host lists its guests (on Inhabitants, or a sketch covenant's
  Overview while it has any), with whether this year's fee is due; Pay
  the Fee hands the vis or silver over as Give does, or records the
  service, in both Diaries.
- While he stays, his casting counts the host's aura, and, with the use
  of its library, its books are his to study and copy. Deleting the host
  ends the stay, and importing him finds his host by name.

### Glossa

- Help for Stay as Guest (with House Jerbiton's code of hospitality) and
  the Guests list, and a how-to: How to stay at another covenant.

## 3.34.1 — 2026-10-28

### Fundamenta

- Importing a covenant, a pack or a saga export keeps its Charter of
  Covenant's seals when its magi are given new ids: each seal follows its
  magus. A seal whose magus isn't brought in and isn't already in the
  saga is left off, as the import's preview already says that magus is
  missing.

## 3.34.0 — 2026-10-28

### Orbis

- Threats have clocks: a row of squares filled as each stage comes (a
  dated threat) or as it moves along its track, on the threat's page,
  its card on the Region, the Region's Threats list (now with each
  threat's next stage) and Ahead.
- A place's trigger can move a threat along its track. When the
  trigger's season is played, Advance Season asks whether the troupe
  failed it (the threat moves on, and you're told which stage it
  reaches) or kept it, and writes the answer in the threat's and the
  place's Diary. Outside Winter this is its own short review, *The
  World This Season*, undone by deleting its entry like the yearly one.
- Delay or Hasten, in a threat's More, pushes it later or brings it
  sooner: a dated threat's stages still to come all move by the seasons
  you give, without retyping their dates, and a track's position moves
  back or on. The reason goes in the threat's new Diary tab.
- Open stories: a covenant's Story Event can say what it concerns (a
  character, a laboratory, the covenant or the Region). An experiment's
  story event names the magus, and a Disaster's covenant story the
  covenant. The Region lists every open story of the troupe's covenants
  under Open Stories, and a character's or laboratory's Connections
  names its own.
- Grow into a Threat makes an open story a threat of the Region, from
  its words, and marks the story Grown into a threat.

### Glossa

- Help for threat clocks, Delay or Hasten, Open Stories and Grow into a
  Threat, and two new how-tos: setting up a threat's clock, and
  following a story from its start to a threat.

## 3.33.0 — 2026-10-28

### Illuminatio

- The desktop's pages move a little, never in the way: the Inspector's
  new item inks in on its gilt leaf as a sheen crosses it, a chosen
  row's gold wash spreads from the left with its leaf after it, a
  chapter fades in with a small slide, and an experience line that has
  moved since you last saw it grows to its new length.
- A wax seal is pressed on the page for a moment when the season
  advances, and when a character, covenant or laboratory is moved to
  In Play.
- Reduce motion, the sparkle beside the speaker, stills every movement
  (the title page, the opening card and the dials too). Until you
  choose, it follows Windows' Animation effects setting.

### Glossa

- Help says what moves and how to reduce motion.

## 3.32.0 — 2026-10-28

### Pagina

- A Muslim's Faith section offers Invoke Baraka: a holy forbear's
  blessing, asked as a saint is invoked, at his shrine (the Qur'an
  anywhere), with the book's Muslim modifiers and its eight forbears,
  their Might, shrines and powers. A forbear is never threatened.
- The Hajj gives a Muslim Pious +3 and 3 Faith Points; made again, it
  restores them, never raising Pious above +3.

### Glossa

- Help pages for Invoke Baraka and the Hajj, and the faith how-to says
  what a Muslim may do.

## 3.31.0 — 2026-10-28

### Pagina

- A character's Church chapter is now the Religion chapter, right after
  Virtues & Flaws, in both versions. It opens with Faith: his religion,
  patron saint, Devotions, mystic path and the saints who have refused
  him, with Edit Religion.
- The saints, the mystic paths, God's aid and holy influence left the
  Personality Traits heading for Faith, and each is offered only to
  those the books allow: Threaten a Saint only after a saint has
  refused him, Devotion Points only with a Devotion or a positive Pious
  trait, Mystic Path only when Pious and tied to the Divine, God's aid
  not to a grog or one with Low Self-Esteem unless he has True Faith.
- Patron Saint is its own action, open to any Christian.
- A Christian has Petitions and the Canon Court; Holy Orders and
  Ordinations show only for one with a clerical Social Status or a
  grade, Perform an Exorcism only for a clergyman, and only a Christian
  may plan an Ordination season. Petition the Church, Add Canon Case and
  Holy Orders left More: Add on each list and Edit Holy Orders do them.
- Religion is chosen from a list (Christian, Muslim, Jewish, Mazdean,
  Pagan, Other); a blank one counts as Christian, and religions typed
  before are read into the list. A Jew or a Muslim is offered God's aid
  and holy influence, a Mazdean the yazata.

### Insignia

- The Religion chapter's icon is his faith's: a church, a Star of David,
  a crescent and star, a fire altar or a sacred tree, the last four
  drawn by the app in the manner of its other icons.

### Glossa

- A help topic for the Religion tab and its Faith section, Edit Religion
  and Patron Saint, and a how-to: "Which faith actions can he take?"

## 3.30.0 — 2026-10-28

### Illuminatio

- Gain or Lose in Play has its own "During the Saga" strip under the
  Virtues and Flaws, above Powers, so the two columns' headings match.
  Each change it saves is still kept in the Diary.
- Hermetic Magic opens with a Current Location section: where the
  character is and the aura their casting counts.
- Craft by Magic, Certamen, Cast in a Lacuna and the Mystery buttons
  moved from the Known Spells heading to a new "Magic Outside the Lab"
  section under Raw Vis, and each opens in its own window.

## 3.29.2 — 2026-10-28

### Concilium

- War's End is offered only with a case chosen on the docket.

### Book of Hours

- Hermetic Sacrifice saves with "Not now (pay it by hand)" chosen.

### Fundamenta

- The goldens regenerated for the walkthrough rounds' new commands, and
  the tests brought up to date with them.

## 3.29.1 — 2026-10-27

### Illuminatio

- The desktop's Reputations, Health and Aging show their own buttons
  again: House Acclaim, Reputation Roll, Melee Event, Tournament, Take
  Harm, Recovery Roll and the Aging actions.

## 3.29.0 — 2026-10-27

### Gauntlet

- A season searching for an apprentice that finds a Gifted child adds
  him as a companion of seven, in creation. A Bonisagus who takes one by
  right takes another magus's apprentice, whom the storyguide names.
- Opening the Arts makes the child the master's apprentice, and converts
  each Supernatural Ability into one of the master's Hermetic Virtues of
  its own size (DE p. 271).
- Educated can name its school, and the school caps the subjects it
  teaches (Art & Academe p. 79). A municipal school is chosen for
  Medicine or for Civil Law.
- Ticking a tradition in play brings the Virtues its members need; a
  Gifted member's Gift is still Opened by a master's season.
- A new grog joins the covenant's Turb.

### Pagina

- A magus's sheet shows his lineage.
- The desktop gains the buttons for Reputations, Health, Aging and
  Covers, and End of Session.
- Where He Is sets where a character is, and casting counts that aura.
- A deep cover's Disguise roll is Intelligence + Guile against 9 and its
  modifiers, and talking in disguise Presence + Guile against
  Intelligence + Folk Ken (HoH: Societates p. 87).
- The Silver Cord adds to trait rolls and offers its rescue; the Golden
  Cord lowers a hedge power's botch dice.
- Certamen plays a whole duel between two magi; a botch stops it for the
  storyguide.
- A vampire's precautions, limitations and death are on its form.

### Book of Hours

- Grogs earn Story Experience, and can plan seasons copying books and Lab
  Texts. Each award or copying season takes a season of the Grogs year
  in its order (Grogs p. 67).
- Lab work can recreate a flawed experiment, spend its season on a
  Hermetic Project's stage, attune a talisman, and fill a device's Shape
  and Material bonuses.
- A Magical Focus records the Arts it spans and applies by them,
  requisites included (DE p. 94).
- Quests performed are recorded, and a repeated Quest gives the Script
  nothing (TMRE p. 16). A vis sacrifice the initiate can't pay refuses
  the Initiation.
- An Invigorated Stirps breeds in its season, spring for animals and
  autumn for plants, up to its magus's Viresculture score (LoH p. 75).
- Hermetic Sacrifice pays its vis, a theriac takes the apothecary's
  Labor Points, and divination fills its ceremonial bonus from the
  question.

### Computus

- Base Loyalty rounds to the nearest, and a companion or specialist with
  a full council vote counts 0 in it (Covenants p. 38).
- Income that relies on the covenfolk is halved at Loyalty -6.
- Take Harm offers a volcano's hazards with Hermetic Projects in play.
- The Spirit and Rally rules, battle magic's Concentration and the
  mounted charge are played in battles and fights.

### Orbis

- Hermetic Projects: the Hermetic Shipyard's Build a Ship, a menagerie's
  Reputation Award, and the Burning City, the Intangible Assassin and the
  Living Corpse followed stage by stage, with their Warning Bell, Gather
  a Connection, Lower an Aegis and Death Roll.
- A covenant's Hooks suggest stories; the world turn suggests attitude
  changes from the year's favours; Cross the Threshold counts its points.
- Battles: a leader's groups, life on campaign and chevauchee. Sieges:
  the garrison's engines targeting the besiegers' one by one, several
  walls, outworks, who is inside (a season under siege counts), and an
  escalade breaching only at a Shoddy wall.
- Melee Events, a lord's coin for a manor, and the siege's dates fixed.

### Concilium

- The Grand Tribunal: a Tribunal with its delegates, quorate as any legal
  Tribunal, its Praeco and Presiding Quaesitor the Primi of Bonisagus and
  Guernicus.
- War's End records a Wizard's War's outcome and Flambeau's Acclaim; a
  war no meeting hears says so.
- A saga's Mystery Cults have agendas and attitudes, and lean at meetings.

### Glossa

- Help for all of it, a how-to for a staged Hermetic Project, and the
  Rhine's notice period corrected.

## 3.28.0 — 2026-10-27

### Gauntlet

- Edit type on the Creation Worksheet offers magus, companion, Mythic
  Companion and grog while the character is in creation.
- A Magic Theory specialty in inventing spells, or in the spell's
  Technique or Form, raises the creation spell cap by 1 (DE pp. 50, 168).
- A folk witch's apprenticeship years (from about ten, for ten years) are
  left out of Later Life, as are the sorginak's, the bouda's and the
  settuten's; Penetration is open to anyone with a tradition's Opening,
  and a Gifted witch's Opened powers need no Virtues (Hedge Magic RE p.
  34).
- A new Equipment step before Finishing Touches, and reminders of blank
  specialties on each experience step.
- The baseline's grogs and covenfolk go in as Inhabitants when a covenant
  goes into play (DE p. 179).

### Book of Hours

- Be taught counts its student once; varying a Script shows its new total
  before the season is played.
- With the Large Library rule, Read can study the library's whole holding
  of a subject (Transforming Mythic Europe p. 105).
- An Initiation's Sacrifice is chosen on the plan and made when the rite is
  carried out: a device, talisman, item, book, the familiar, an apprentice,
  mundane wealth, vis, or a season serving the cult.
- Binding a familiar can wait for its season to give True Friend and
  Loyal; the Suggested Familiars show once both Arts are chosen.

### Computus

- Debates choose each round's tactics by lot among a speaker's best
  Abilities, so equal speakers no longer stall at 0 to 0.
- Similar spells count when instilling an effect and empowering a bond.
- Living Conditions follow the covenant's season when left blank, and a
  noble uses the magi's (DE p. 190).
- Deep covers and personae (Houses of Hermes: Societates pp. 87-90): a
  Covers section, each cover's Reputation kept up at Advance, and a
  persona's Reputation growing with Persona.

### Pagina

- Resolve Twilight applies the storyguide's choice of effects, and
  Twilight Scars have their own field.
- Cast a Power rolls a hedge tradition's casting; Boost a Spell works out
  a boost's pawns and botch dice.
- A character's Marriages and a covenant's Land Works are shown on their
  sheets.
- A ship can be marked Sunk or Taken, and a taken one moves to its
  captor's Possessions.
- Placeholder names read "Affinity with (Art)" until chosen, and lists
  name only what a name doesn't show.

### Orbis

- Muster and Aftermath on a battle: Raise Allies, Hire Mercenaries or take
  a War Loan, the Deployment Total, and the End of the Day with its
  Confidence Points and Reputation (Lords of Men pp. 102-109).
- Each side's groups are kept by kind, and an event's losses fall on the
  kind its Enemy names; attacking the baggage earns a bad Reputation.
- A fight can take a standard combat group, and Combat Options works out a
  charge, a horse's gait, cover, crowding, interrupting and the saddle
  (Lords of Men ch. 9; Errata p. 75).
- Siege Actions: deployments with undefended walls, blockades, reliefs,
  Conjuration of Bread and Raise the Siege, running the stockade, and the
  castle taken (Lords of Men pp. 112-116).
- Marking a threat's stage writes its own text in the Diaries.

### Concilium

- A Rhine covenant leans with a party its members' gild shares (Guardians
  of the Forests pp. 27-28).
- Sentences no longer double "the" before a Tribunal's name.

### Florilegium

- Export a Cult, and Import's A Mystery Cult, move a saga's own Mystery
  Cult between sagas.

## 3.27.0 — 2026-10-27

### Concilium

- **Polemic** (Transforming Mythic Europe pp. 28-35): an Arguments tab on
  a Tribunal, with each case's polemic, diatribes and apologia written on
  any knowledge Ability, their circulation and Reputations, and one
  Argument Total for each side of a debate.
- **Charter Strength** (TME p. 36), a saga option: a charter's strength
  for its lord and his subjects, Draft the Charter and Seek a Loophole, by
  Civil and Canon Law, or Common Law in England.

### Pagina

- **The Menagerie** (Hermetic Projects pp. 122-142): a second kind of
  project, with its beasts, their animal and breed, taming, breeding by
  the book's optional rules, the young's Might, what the staff can tend,
  acclimation, upkeep and Realia.

### Orbis

- **Battles at sea** (Lords of Men pp. 105-106; Tales of Power pp.
  106-110): a battle fought by ships from a covenant's Possessions, with
  pilots, the Weight of Numbers by ships, and events at sea.
- **Marriages** (Lords of Men pp. 10-11, 81; City & Guild p. 113): a
  Marriages tab on a lord, with noble and merchant dowries and their
  terms by custom, and End a Marriage leading to Settle an Inheritance.
- A widow keeps the profit of a third of her husband's land until she
  remarries, and the daughters' inheritance gives both customs (DE pp.
  512-513).

### Computus

- **House Criamon's Enigma** (HoH: Mystery Cults pp. 50-73): The Enigma
  chapter for a Criamon magus, with his path, its stations and stigmata;
  Follow an Avenue and Change Path, with the House's guide at Presence +
  Lore 6, each station's Virtues and Ordeals, and the Path of the Mirror
  for the Primus.

## 3.26.0 — 2026-10-27

### Sodales

- **A cleric's career** (The Church pp. 25-38, 46-48): a Church tab for a
  character with a grade, a petition or a canon case: his Holy Orders and
  the ladder of grades, Ordinations with their examinations, Petitions to
  the Church and the Canon Court; an Ordination season that swaps his
  Social Status for the clergy's; Perform an Exorcism.
- **Virtues and Flaws gained and lost in play** (Grogs pp. 61-64), with
  temporary magical grants that end.

### Pagina

- **Ships** in a covenant's Possessions (Hermetic Projects pp. 53-62; City
  & Guild pp. 77, 86-87): their crew, cargo, quality and damage, stress
  checks and ship combat.
- **Hermetic Projects** (pp. 26-44, 78-95): a Projects tab once a project
  is begun, the Great Tower with its master mason, works and craft
  devices, Conjure Levels and the stress check, a Build the Great Tower
  season; Open a Tunnel; the Burning City's volcanic lab Features and
  Virtues.
- **Shape the Land** (Transforming Mythic Europe pp. 53-77): an island
  raised by Ritual, its wall, fill, acres and manors.

### Orbis

- **Egyptian tombs** (Lands of the Nile pp. 32-46): a Tomb tab on a place,
  with its curses, talismans and wards, traps and Overcome It.

### Concilium

- **The Great Library** of Durenmar (Guardians of the Forests pp. 55-58):
  credit, searches by the book's rolls, and books lent only while credit
  is paid.

### Florilegium

- **A saga's own Supernatural Abilities** in House Rules (HoH: Societates
  pp. 103-106), with their Virtue.
- **A saga's own Mystery Cults**, with degrees, Scripts and experiments
  (The Mysteries Revised pp. 13-19), in a tab of their own.
- **The spell-guideline catalog**: Societates' and Magi of Hermes'
  guidelines, offered on Invent Spell.

### Computus

- **House magic**: Mercere's Portals and Mutantum spells (HoH: True
  Lineages pp. 99-108); Tytalus disguises and personae (HoH: Societates
  pp. 86-91); Adaptive Casting on any similar spell (Errata p. 46).
- **Books by magic** and the covenant's savings by magic (Transforming
  Mythic Europe pp. 98-122), capped at half the Provisions.
- **Mythic Locations**' Mercurian rituals (pp. 96-101), with its other set
  pieces as help.

## 3.25.0 — 2026-10-27

### Computus

- **Philosophic Alchemy and the Elixirs** (The Mysteries Revised pp.
  39-46): a vis extraction left to digest beside other work, its spaces
  ready-opened or extra room; the Lesser Elixir off an alchemist's aging
  rolls; the Great Elixir's test, after which a magus is a being of Magic
  with a Might, no longer aging or gaining Warping. A Longevity Ritual's
  vis is capped per Art by the magus's score (DE p. 261).
- **Hermetic divination and astrology** (pp. 47-63): casual and
  ceremonial Divination Totals, horoscopes, Astrological Durations, the
  favourable hour, and Celestial Magic's discount on opening a device.
- **Spirit magic and theurgy** (pp. 64-88); **Dream Magic** and **Hermetic
  Sacrifice** (pp. 102-117); **Hermetic Numerology, Geometry and
  Architecture** (pp. 91-101).
- **The Magic Realm and the Faerie Threshold** (RoP: Magic pp. 20-28; RoP:
  Faerie pp. 16-24): a boundary's bonus and its botch dice on casting and
  lab work, travel and the Twilight Void; a Threshold's points.
- **Lunar**, Dies Irae's fifth realm, in every realm-interaction total
  while Dies Irae is in play (pp. 36-38).
- **House Bjornaer's Mysteries** (HoH: Mystery Cults pp. 18-33):
  temperaments and heartbeasts, changing form against magic, the
  Epitome, inner heartbeasts and refinements; Sensory Magic on the Lab
  Total.
- **House Merinita's Inner Mysteries** (pp. 82-106), with Symbolic
  Magic's Symbol Range, Duration and Target in spell design.
- **Learned magic** (RoP: The Divine pp. 97-100, 141-144): the Ars
  Notoria's Rings and its relief from a Divine aura when casting; Jewish
  mysticism's golems, Merkavah and Shinnui Shem; the Solomonic
  integrations (The Cradle & the Crescent pp. 44-45).
- **Vampires** of Against the Dark, and the kukudhi as a player character;
  a crowned king's free Shapeshifter (pp. 108-122).
- **House Acclaim** for Bonisagus and Flambeau, Flambeau's tournaments,
  and Jerbiton's league (HoH: True Lineages pp. 21-23; HoH: Societates pp.
  20-22, 31-32, 53-55).
- **Mythic Africa**: the Cult of Dedun and Corpse Magic, Ethiopia's
  calendar and church forests, the Aithiopian tribes and the Plinian races
  (Lands of the Nile pp. 95-126; Between Sand and Sea pp. 119-124).

### Book of Hours

- The Initiation season knows Houses Bjornaer's and Merinita's rules,
  reading each House's Lore by the books' names too.
- New seasons: Reinvent the Lesser Elixir, Make an armillary sphere,
  Invent Rotes, Bind an enchanted structure.

### Pagina

- More offers **Philosophic Alchemy**, **Test the Great Elixir**,
  **Divination**, **Astrology**, **Spirits and Names**, **Dream
  Working**, **Hermetic Sacrifice**, **House Acclaim** and **Reputation
  Roll**, each with an inspector.
- A place or regio level can lie in the Magic or Faerie Realm, or be
  Lunar; its facts show the Threshold and what the realm does.
- A vampire's sheet shows what its design lacks; a talisman says what
  Great or Consummate Talisman allows; a device can be a Numerologist's
  Book or an architecture component.

### Gauntlet

- New Character offers the dragon-born and varcolac templates (Against the
  Dark pp. 108, 122).

### Hedge Magic

- **The Debterah** of Ethiopia, a holy societas of amulet makers (Lands of
  the Nile p. 114), with its symbol; the Cult of Dedun's Corpse Magic.

### Florilegium

- The House Bjornaer and House Merinita Mystery Cults and their Scripts;
  the Divination Ability (and its mark); four Solomonic Virtues and the
  Story Flaw Miles; the Aithiopian tribes' Virtues and Flaws.

## 3.24.0 — 2026-10-26

### Computus

- **Christian mysticism** (The Church pp. 19-24): the contemplative and
  monistic paths, who may follow them, and their Divine Ascent (the
  Divine Form at 2 Warping Points, the Divine Gloom at 1); the Divine
  Form's Magic Resistance and Soak on the sheet; a contemplative's
  Spiritual Path to a Revelation, its quests reaching the Path Total; a
  monist's Revelations.
- **Invoking God's aid** (RoP: The Divine pp. 41-42); Font of Knowledge
  (DE p. 165); a Commanding Aura withdrawn until penance (DE pp. 74, 420),
  and the other faiths' leaders among the offices (RoP: The Divine p. 43).
- **Magic in a fight**: a mastered spell's Mastery in the Casting Score and
  Penetration, and doubled resistance (DE pp. 225-226); Arcane
  Connections and sympathies multiplying Penetration (DE pp. 219-220);
  indirect spells aimed instead of resisted, each of the 18 with its
  limits (DE p. 223; HoH: Societates p. 30); invisible fighters, located
  before they can be struck, kept out by Magic Resistance unless they
  picked up a weapon after turning invisible (pp. 32-33).
- **Breakthroughs**: a fertile Longevity Ritual and Hermetic Metamorphosis
  (Magi of Hermes pp. 20, 82-84), Hermetic Viresculture and its Lesser
  Enchantment Vis (Legends of Hermes pp. 72-76); a Longevity Ritual says
  whether it leaves its subject sterile.
- House Verditius's prices to magi and to mundanes (HoH: Mystery Cults
  pp. 114-115), forge-companions and vendettas.

### Hedge Magic

- **Folk witches**: Brew Potency, doses and the vis limit; two new
  kitchen seasons, extracting vis and fixing an Arcane Connection; the
  Witch Moon, potions, familiars and covens (Hedge Magic Revised pp.
  33-54).
- **Nightwalkers**: spirit travel's Ease Factors, leading a spirit
  astray, changing form, seeking a foe and questioning the dead (pp.
  103-119).
- **The clesrada**, the Ulster heroes' feats of arms, a new tradition with
  its eighteen feats and symbol (The Contested Isle pp. 101-105).
- Vitkir can hold the nine **Saxon runes**, with their guidelines and
  marks (Thrice-Told Tales pp. 139-143).

### Book of Hours

- An Initiation's **Script** can be written out as its components, its
  bonus worked out with the Ordeal's (The Mysteries Revised pp. 15-16).
- House Verditius's **Hubris** grows on the sheet with each Inner Mystery.
- New seasons: the Spiritual Path's service, devotion, preaching and
  mission (The Church p. 22); **Vitalize** and **Invigorate a Stirps**
  (Legends of Hermes pp. 72-75), several at once.

### Pagina

- More offers **Hubris** on a Verditius, and **Mystic Path**, **Spiritual
  Path**, **Monistic Revelation**, **Invoke God's Aid**, **Font of
  Knowledge** and **Commanding Aura** on a person, each with an
  inspector.
- A device made by a Verditius shows the House's prices; a fighter can be
  invisible; Cast a Spell asks for an Arcane Connection and whether the
  spell is indirect.

### Concilium

- A charge between two magi can be decided by **binding certamen**, or one
  point of it settled by certamen; a false or flawed thesis starts behind;
  a motion the Tribunal opposes is debated by the whole hall; a motion can
  go to the next Grand Tribunal (HoH: Societates pp. 91-93; DE p. 230).

### Peregrinatio

- **Normandy's Library** at each meeting: leases returned, books given for
  a lease, and the Tourney's book prizes by prize pawns (The Lion and the
  Lily pp. 22-23, 33).
- **Provence's roll of residents** (Faith and Flame p. 22).

### Florilegium

- The Hermetic Metamorphosis Virtue; the House Verditius Scripts'
  components; Thrice-Told Tales among the sourcebooks.

## 3.23.0 — 2026-10-26

### Computus

- **Dealing with faeries** (RoP: Faerie pp. 25-29, 102-103, 131-134): the
  Ars Fabulosa's totals (Summoning, Bonding, Captivating, Dismissing), the
  Might the Sympathy Traits reach, Penetration with the best Trait, and
  what each power does; Sympathy Traits gain and lose experience from
  bargains and from a 1 or a botch; an offer to the Faerie Realm with a
  fable point.
- **Devotion and the saints**: invoking a saint with every modifier the
  books give, and threatening one who refused (RoP: The Divine pp. 85-91);
  Devotions and Devotion Points (The Church pp. 12-15); a relic of the
  saint invoked adds +2 for each of its Faith Points with The Church in
  play, another saint's relic +1 (The Church p. 13); indulgences, vigils
  and fasts (pp. 11-12); the Mazdean yazdan (The Cradle and the Crescent
  p. 85).
- **Armour worn as pieces** (Lords of Men pp. 139-143): Protection and Load
  add together, rounded up at the end, wherever Soak, Load and harm are
  worked out; complex armour design is in the rules engine.
- **Lacunae** (HoH: Societates pp. 57-60): searching a city records it and
  the small lacunae known there; Mystical Choreography's reminder follows
  the DE (p. 99).
- **Angels** are checked against their Choir (RoP: The Divine pp. 16-26);
  a holy tradition's effects and an infernalist's maleficia work their
  levels out from the books' guidelines, with the Errata's corrections
  (RoP: The Divine pp. 46-56; RoP: The Infernal pp. 102-113).

### Concilium

- **Hermetic law**: a Tribunal's docket takes a declaration of **Wizard's
  War**, with its full moon and how it was served, and a **Wizard's
  March** a Quaesitor called (DE pp. 18-21; HoH: Societates pp. 22-25;
  HoH: True Lineages pp. 45-60). The Rulings ask whether a conviction
  Marched the accused; a case's details give the estate's shares (victim,
  prosecutor, heir) with the slayer's convention beside them, the
  Peripheral Code's low crimes, a spell trace's fading and the Acute
  Sense roll (p. 71), and an Intrigue roll with The Gift's penalty where
  Parma doesn't cover both sides (pp. 24-25).

### Pagina

- More offers **Cast in a Lacuna**, **Pilgrimage** (The Church pp.
  15-19), **Ars Fabulosa**, **A Faerie Bargain**, **An Offer to Faerie**,
  **Invoke a Saint**, **Threaten a Saint**, **Devotion Points**,
  **Indulgence, Vigil or Fast** and **Holy Influence**, each with an
  inspector, written to the Diary.
- A magus's Hermetic Background records a renunciation and any Wizard's
  War he is fighting.
- The armour form has a "Worn as" field with Lords of Men in play; a
  church's Relics show what each adds to invoking its saint; the Planning
  tab lists a patron saint and Devotions.

### Book of Hours

- A season of personal devotion at a saint's shrine earns 5 Devotion
  Points (The Church p. 14).

### Florilegium

- Lords of Men's weapons and armour pieces join the catalog with the book
  in play, with a Crossbow Ability (and its mark).
- The saints of RoP: The Divine, The Sundered Eagle and The Contested
  Isle, with their Might, feasts and powers.
- The holy Powers' and the maleficia's guidelines join the holy and
  infernal traditions.

### Fundamenta

- The Code of Hermes's crimes moved into the rules engine, beside
  Hermetic law.

## 3.22.0 — 2026-10-26

### Gauntlet

- **The Gauntlet**, from More on an apprentice: a story's verdict, a pass
  for one who has served his fifteen years, or the book's roll; three
  failures bring the Quaesitores, and an apprentice kept over 20 years is
  told of the low crime and the rook of vis a year past 15. Passing makes
  him a magus (Apprentices pp. 59-61).
- **Lose the Gift**: an apprentice's Gift lost for good (Failed Apprentice
  replaces Apprentice) or suppressed (pp. 58-59).
- An apprentice's Parma Magica gives no Magic Resistance until he has
  passed his Gauntlet and been given its final key (DE p. 169).

### Computus

- **Turbulence** (Apprentices pp. 12, 22-24): a Gifted character's Gift
  lashing out after a botched magical roll: the incurring roll against the
  storyguide's die and the character's age, the control roll, its
  magnitude and Penetration, rolled from More.
- New saga option, **Learning cantations** (Apprentices p. 46), off by
  default: a spontaneous spell cast as often as its level may be learned
  as a formulaic one for that many adventure xp, by apprentices and magi.
- **Faerie Sympathy Traits** (RoP: Faerie pp. 102-105): a Personality
  Trait can be a Sympathy Trait, or a temporary one; a character shows his
  Faerie Rank, the botch dice a negative Trait adds and how far experience
  may raise them, and a Faerie Calling says whether his Rank makes it a
  good one.
- **Faerie rites** are built by the book: the ollamhain, volkhvy and wise
  folk have their Powers' guidelines and the Faerie Ranges, Durations and
  Targets, so a rite's level is worked out, with the Sympathy it needs
  (pp. 121-131).
- **Ancient Magic**: a Grigori Secret's extra breakthrough point each
  season of research; the Secrets' vis and requisites; Heron's mechanica,
  animae, and Mutable and Awakened Devices; Adamic's Penetration bonus;
  Ptolemy's stellar observation (Ancient Magic pp. 10-11, 65-91).
- **The noble hunt** from Lords of Men: the quest with lymers, the
  assembly, the chase hour by hour with its relay and Terrain Bonus, and
  hawking with the book's flight table, hawks and prey (pp. 48-60); Area
  Lore's Ease Factors (City & Guild pp. 82-83).
- Translating needs Artes Liberales, loses the culture point only without
  the source culture's Area Lore 3 and never for a magus's Hermetic text,
  and loses less Quality with both languages at 6 (A&A p. 87).
- Good and Bad Academic Reputations are kept apart, each with its own
  score (A&A p. 103).

### Book of Hours

- **Create a work of art** works out its Aesthetic Quality with every
  bonus Art & Academe gives, and its time from the kind of piece,
  assistants and haste; it earns Artist Reputation experience, rolls its
  experiment, and lets a maestro instill magic as he works (pp. 123-135).
- New seasons: **Edit a lecture commentary**, **Seek a teaching or
  clerkly post** (A&A pp. 84, 89, 102) and **Learn to measure the fixed
  stars** (Ancient Magic p. 90).
- Recording a teacher's lectures gives him Academic Reputation experience
  for every second commentary (A&A p. 103).
- An apprentice assisting in a stressful laboratory season can check for a
  Turbulence midway through it: uncontrolled, his aid is halved
  (Apprentices p. 56).

### Pagina

- More offers **An Artist's Career** (a sponsor, trying conditions, a
  Reputation's deeds) and **A Scholar's Career** (a place at a school, an
  Academic Reputation's deeds) (A&A pp. 79-89, 103, 125-131).
- More offers **The Hunt** and **Area Lore** on a manor, and beside
  Travel on Ahead for a journey, each with an inspector; the outcome goes
  to the Diaries, with the chase's Long-Term Fatigue.
- A faerie creature notes its role in its stories and the story it wants
  (RoP: Faerie pp. 40, 140-142).
- A research goal's details name where its Insight is found; the Casting
  Scores notes remind of Adamic and the Grigori Secrets.
- A Reputation can be marked bad.

### Concilium

- A Transylvanian Tribunal's meeting holds **the Praeco's purse**: the
  Tribunal's projects for her, a levy on each oppidum the law obliges, her
  reserved vis source, the stipends and her promissory notes; and appoints
  **the Curantis** and his Notary, paid from the treasury, never two terms
  running (Against the Dark pp. 19, 97). The treasury shows levies unpaid
  and notes outstanding.

### Florilegium

- Ancient Magic's lost magics are catalog data, with two more integration
  choices on Add Research Goal (Awakened Device after Mutable Device;
  Mutable Device without the Virtue); errata to the fixed-stars spell and
  Azael's Secret.
- A Faerie God's blood can name its Olympian, and lists that god's
  Sympathy Traits (The Sundered Eagle p. 127).

## 3.21.0 — 2026-10-26

### Gauntlet

- Young characters, with Apprentices in play: the worksheet shows the Aging
  Chart's Characteristic Modifier and the Size a child should have for his
  age, with Grows Quickly, Late Bloomer and Deft (Characteristic) moving
  them (Apprentices pp. 7-12).
- Child Virtues and Flaws are checked against the character's age (20 and
  younger), Inherited ones are for magi and companions and must have
  manifested by 21, Virtues that grant xp are barred under 14, and
  Turbulence Prone needs The Gift (pp. 10-12; Errata p. 82).
- A young character may learn his parent's vocation from 6 to 14, but only
  to half the parent's score (p. 14).

### Computus

- New saga option, **Standard apprenticeship model** (Apprentices p. 14),
  off by default: an apprentice part way through has 19 xp a year for
  twelve years, then 6 xp and 40 spell levels a year, either spendable on
  the other, instead of the full 240 xp and 120 levels.
- **Aura kinds**: a Magic aura may be aligned, adding the aura again to
  the Casting Scores and Lab Totals of its Art, or half of it to Recovery
  Totals for Healing (RoP: Magic pp. 13-16); a Faerie aura may be tinted
  (RoP: Faerie p. 104); a Divine aura is the Dominion or Empyreal, both 1
  weaker at night and 1 stronger on Sundays and holy days (RoP: The
  Divine pp. 7-12). True Understanding and Insight of the Realms work on
  foreign auras and Rituals (Legends of Hermes pp. 14-16).
- **Sin**: Personality Traits and Personality Flaws are read against the
  seven deadly sins and their virtues; Confidence through sin, infernal
  influence, tarnish and what redemption costs (RoP: The Infernal pp.
  17-24, 89, 124).
- **The Goetic Arts'** own totals and targets: Summoning, Scouring,
  Ablating, Binding and Commanding, with Hierarchy on both sides against
  demons (pp. 114-119); the demon-hunter's spells show what they do at
  their level, with Apotropaic and Goetic Mastery (pp. 120-124, with the
  Errata's corrections).
- **The Theban customs** (The Sundered Eagle): the Hermetic letter's
  composing and reading rolls, the Oath Invocation roll with its
  maledictions, Greek Fire's dangerous batch, painting (by ordained clergy)
  and venerating icons, and a mother's curse (pp. 44-48, 133-136).
- **House Verditius's Inner Mysteries** in the laboratory: elder runes
  double their Art, raise each effect's level, take their pawn of vis and
  make the season's vis limit Magic Theory x Philosophiae; an attuned
  item's capacity; Hubris on an attuned item's and an automaton's Lab
  Totals; the rules for Items of Quality, reforging, automata and binding
  creatures and curses, ready for the season notes (HoH: Mystery Cults pp.
  123-135).
- **Art & Academe's apothecary**: medicinal degrees and simple poisons,
  the store's drains, searching for and preserving ingredients, formula
  levels and Lab Totals, ligatures and nativities (A&A pp. 63-78; Errata
  p. 61).
- **The Greek Fire siphon** joins the weapons, with The Sundered Eagle in
  play: used with Profession: Naffatun, and a shield's Defense goes to
  Soak against it in a fight (p. 47).

### Book of Hours

- At the year's end, a character turning 8, 15 or 21 is told of his
  transition of maturation, and what must change at 21.
- Initiations into House Verditius's Mysteries follow the House's rules:
  Cult Lore 3 for a Minor Inner Mystery and 5 for a Major, Hubris as the
  first one's Ordeal, the Hubris experience each earns, and each of the
  House's Ordeals suffered once (HoH: Mystery Cults pp. 116-121).
- Researching a philosophy formula records its kind and level, and its
  experience goes into the formula only; producing reagents, theriacs or
  inceptions works the season out, from a first concoction's points to
  doses by the Lab Total in his Personal Gear; a store pays 3 Labor Points
  a year for each physician whose regimens it supplies.

### Pagina

- A place's and a regio level's Edit asks for its aura's kind by its
  realm, and its facts say what each does.
- More on Personality Traits offers **Confidence through Sin** and
  **Infernal Influence**; More offers **Ars Goetia**, a calculator and roll
  of a Goetic Art.
- More offers the Byzantine customs (Hermetic Letter, Invoke a Broken
  Oath, Make Greek Fire, Paint an Icon, Venerate an Icon, A Mother's
  Curse), **Make a Ligature** and, on This Season, **Apothecary's Store**.
- Delusion, Obsessed, Compulsion and Weak-Willed take a detail naming the
  sin they lean to.
- An invested device a Verditius crafted records its elder runes and
  whether it is an attuned item or an automaton.
- The Plan Season form asks for a formula's level and Philosophic
  Bonuses; the Planning tab lists each formula with its kind, level and
  Laboratory Text.
- On the desktop, a chapter's buttons wrap by width, so none scrolls
  sideways.

### Florilegium

- Legends of Hermes's three realm-insight Virtues; RoP: Magic's Fine Aura
  and Favorable Aura Boons and Troublesome Aura Hook; Mythic Blood
  (Gigantes), The Sundered Eagle's six maledictions and a mother's curse;
  the House Verditius Mystery Cult and its sample Scripts.

### Orbis

- A church's Relics can hold its icons: an eikon's Aesthetic Quality and
  what venerating it adds to invoking its saint.

### Hedge Magic

- The five Goetic traditions list their Arts' effects as guidelines, and
  their Goetic Art notes give each Art's target correctly.

## 3.20.0 — 2026-10-26

### Pagina

- A covenant has a true **Charter** chapter (tab 2 in the terminal): its
  Charter of Covenant with its name, preamble, when sworn and whether a
  Quaesitor ratified it, the members' wax seals, and its clauses grouped
  by the charter's sections; **Break a Clause** strikes one through with
  when and how (Covenants pp. 31-36). The old Charter chapter is now
  **Attributes**, and the Chartered Town Boon's charter lords and terms
  move to the new chapter.
- **Resolve the Task** rolls an agent's own total against the task's Ease
  Factor, with the risk's botch dice, and writes it in the Diary (Lords of
  Men p. 24); long notice titles wrap; "1 pound", not "1 pounds".
- **Sell Finished Goods** on a craftsman's This Season: Presence + Bargain
  against 9, or opposed against an important customer (City & Guild pp.
  74-76).
- A character's complexion, under the Art & Academe medicine option (A&A
  pp. 37-41), and a Tremere's school of certamen and sigil challenge.

### Computus

- **Warping by realm**: Warping Points are counted by the realm that gave
  them, and the main source sets what a Warping Score brings (DE p. 391;
  the Realms of Power). Two or more points at once bring Wizard's
  Twilight, the **Divine Ascent**, **Vituperation** or **Faerie Calling**,
  by what the character is; leaving Faerie and instant travel have their
  own Warping (RoP: Faerie pp. 29-30, 118-120; The Divine pp. 62-65; The
  Infernal pp. 17, 95, 124; TME pp. 108-115).
- **Certamen styles**: the fifteen schools of True Lineages (pp. 135-139)
  and Tremere Promotion by Force (pp. 123-125).
- **Magic beings** are checked against Realms of Power: Magic:
  advancement, Beasts of Virtue, transformed animals, awakened trees and
  elementals (pp. 51-66, 78-80, 128-139; DE pp. 449-451).
- **Vis kinds**: dedicated, extraordinary and faerie vis, Herbs and
  Objects of Virtue, vis storage, and a creature's Might recovery in an
  aura (RoP: Magic pp. 30, 119-128; RoP: Faerie pp. 16-19).
- An Incapacitating wound may leave a lasting Flaw (A&A p. 43); the Great
  Pestilence's miasmas, from which Magic Resistance protects (Dies Irae
  pp. 86-98).
- Siege fixes: a mounted lance fights as a Single Weapon; supplies rolls
  no longer backdate after Supplies drop; walls keep the damage levels
  they began with when mines lower the Defenses; Seal the Breach is
  capped at a wall's whole (Lords of Men pp. 111-116, 126).
- Workshop exertion's results, its Aging roll, a craftsman's Reputation
  (both points for a wondrous item), and a laborer's Labor Total (C&G pp.
  73-76).

### Hedge Magic

- The **Hyperborean Hymns**: the seven hymns' guidelines and Powers, a
  Power's level cost and Ease Factor, infusion, relics, choirs and
  Illumination (Ancient Magic pp. 103-120).

### Concilium

- The Theban meeting's **Apprentice Presentation** (token bids and the
  Bonisagus claim), the conduct of archai, common vis, and **Lend Vis** /
  **Repay a Loan**; Byzantine coins on the treasury (The Sundered Eagle
  pp. 28-35, 44-45, 77).
- The Rhine's **Mark of Approval**, the **Archmage's Challenge**, the
  apprentice limit, and the opening step's new magi and sigils by proxy
  (Guardians of the Forests pp. 22-27).

### Florilegium

- The Book of Mundane Beasts' beasts cite their pages, with the charger
  and palfrey added (RoP: Magic pp. 140-144); Herbalism and Siege Weapon
  join the Abilities, and five Church characters the templates.

### Fundamenta

- Season work from the supplements is now a registry, one module per
  book.

## 3.19.0 — 2026-10-26

### Computus

- A character's income band comes from their Social Status, and This
  Season shows what their Labor Points are worth in money: 9 Labor Points
  are a quarter of a year's income (City & Guild pp. 37-40, errata p. 56).
- A covenant's income can be improved by magic, with a warning past the
  Tribunals' limit of 2 pounds of silver a magus a year (Covenants pp.
  57-58).
- Craft magic's Finesse Ease Factors and roll (Definitive Edition pp.
  306-308), shown on the Hermetic Magic tab's casting notes.
- A year of improved or reduced rations changes a grog's Living
  Conditions on that year's aging roll (Grogs pp. 23-25).

### Pagina

- **Labor Points from a Story** (More on This Season) awards a craftsman
  or merchant the book's Labor Points for a story, by kind of merchant
  (C&G pp. 39, 111-130). **Invest Time or Money** puts money into a
  business, or makes a merchant's investments (charity, speculation,
  introductions, marriage brokering, legal action, a boom foreseen,
  smuggling, a lavish party...), whose returns come in each Winter (C&G
  pp. 40, 110-130).
- **Reward or Punish** on a grog: improved rations, Pay and a Half,
  equipment and promotion; castigation through flogging, whipping,
  dismissal and the fustuarium, with what each does to him and to the
  covenant's Loyalty (Grogs pp. 23-25; Covenants pp. 38-39). **Pension**
  retires a grog on half Wages, or pays a widow (Grogs p. 26; DE p. 186).
- **Craft by Magic** on a magus's Known Spells works out the Ease Factor
  and roll for crafting with Rego or Creo.

## 3.18.0 — 2026-10-25

### Florilegium

- A **Goods** catalog: every good in City & Guild's Prices of Goods table,
  with its class, how it is sold, its four prices as printed (none to be
  had, priced by purity, blank where the book is blank), where it is bought
  in bulk and the book's notes; and the Price List of common goods, each
  quality's price worked out (C&G pp. 134-144). Silver keeps the book's
  2,420 a ton, with the errata's 2,240-pound ton noted; goods priced by
  purity price a lesser purity by its metal content; gemstones and pearls
  show their price an ounce. A saga can switch it off or hide single goods.

### Pagina

- A **Goods** tab in Saga Content: the goods by class, the chosen good's
  details, Add, Edit and Hide, and Add a Purity.

### Orbis

- A town has three new tabs. **Charter**: its lords (noble, Church, faerie
  or demon, holding it alone, shared by paragium, as a rival claim or as a
  secret parallel charter), its terms and privileges, what it gives (the
  walls' Divine aura: a town's or city's 3, one higher under the Church,
  1 under a faerie lord; a demon's Might and services; the pawn of vis in
  the charter), its citizens after a year and a day, and its size,
  occupations and officials (C&G pp. 8-24; DE p. 418). **Guilds**: its
  guilds, now with their kind, Craft, hall and officials, and the saga's
  characters in them by rank (C&G pp. 41-50). **Court**: its cases,
  verdicts and sentences, and a Court Roll with a live inspector (C&G pp.
  28-30).
- A covenant with the Chartered Town Boon shows its own charter; one with
  the Charter Lord Hook lists the towns it charters (C&G p. 11).
- A lord and a covenant have a **Manors** tab: manors with their land,
  peasants, flock, crops, customary mill or bakery (inside its 20 pounds)
  and manor-court dues as ticks and notes; kennels, mews and stables with
  the book's capacity, upkeep, staff and the Winter Roll; household,
  heirs and hunting rights; Buy a Manor, Assart and Settle an Inheritance
  (Lords of Men pp. 9-12, 48, 58-61, 71-87; errata p. 74). Unpaid
  establishments fall a class and lose 15% of their animals a season.
- A lord's Fief counts his manors from the Manors tab and shows his
  surplus (LoM pp. 31-32). A covenant's manors are shown beside its
  Agriculture (and Livestock) income as a check, never added to it.
- **Travel**, on Ahead: a journey's days (from the distance as the crow
  flies or along the route, or between named ports), what passage costs
  and the Long-Term Fatigue of travelling quickly, with the Definitive
  Edition's rough guide (C&G pp. 80-90, errata p. 57; DE pp. 404, 408).
  Close leaves it a what-if; Set Out writes it in each traveller's Diary,
  takes the forced march's Fatigue and puts the arrival on Ahead.

## 3.17.0 — 2026-10-25

### Illuminatio

- The season medallions now mark the seasons across the desktop, in the
  saga's chosen set: the present season at the centre of the band under
  the title bar, the Seasons page's title and each past season's heading,
  each season in Ahead, the title of a covenant's Seasons chapter, a
  character's This Season, and the column heads of a character's and a
  laboratory's calendar. The present season glows.
- A covenant's header shows its own Covenant Season as a medallion beside
  its Magic Aura and Loyalty, with no words, and Edit Covenant is now the
  header's Edit button.

### Pagina

- Every character has an Agents tab, after Inventory: the people they
  control through personal bonds (Lords of Men pp. 22-25). It shows how
  many agents they can keep (twice Presence plus the higher of Intrigue or
  Leadership, less the Gift's penalty, at least one), counting only those
  won, with those still being won and the unspent Agency experience beside
  it.
- Each agent shows his social status, Bond, resistance ("agent" once won)
  and what he brings; choosing one shows how his resistance was set and,
  for an agent, the Tasks for Agents table. An agent held by coercion is
  marked.
- New actions on an agent: Impress, Spend Agency Experience (wearing his
  resistance down, or raising his Bond with experience or with money at 5
  points a pound) and Set a Task (choose Charm, Intrigue or Leadership; the
  form shows the Ease Factor, persuasion total and botch dice).

### Book of Hours

- An Adventure season also gives as much Agency experience as the
  Adventure experience it gave.

## 3.16.0 — 2026-10-25

### Computus

- **Holy Magic** halves the Lab Total from a Hermetic Lab Text, and a season
  reading a Hermetic book on an Art or an Arcane Ability; a book can be
  marked **Holy (not Hermetic)**, and a holy magus's own texts are holy
  (Realms of Power: The Divine p. 67). Chthonic Magic stands in for Magic
  Theory on a dark or sinister lab plan.
- A Raw Vis Store can be marked Infernal, and a Ritual shows what its vis
  would do; a Hermetic rite may take the Faerie column for its aura.
- The Arma Magica folds, Parmulae and realm-aligned spells say what they
  give; Lab Mastery adds the similar spell's Mastery; Fenicil's rituals,
  Vulgar Alchemy, Performance Magic and Spell Binding are worked out or
  noted.
- Covenants' extended book Quality follows the errata (a tractatus author
  gives Communication + 3; no +3 for mundane subjects).
- A realia and an expert correspondence add one to a library's research
  between them, unless the new **Research aids stack** rule option is on
  (Covenants pp. 90, 102).
- Useful correspondence's and a folio's 1 xp are set points.
- A demon-blooded character is warned against Virtues of another realm (a
  Supernatural Virtue that names none is Magic, Hex Infernal; DE pp. 64,
  85).

### Book of Hours

- Hedge Initiations follow a tradition's own Script: its Ease Factor,
  Characteristic, Lore and bonus, +3 or +9 when the Mystagogue doesn't know
  the power, the Initiate's required scores (the elementalists' minimums,
  the learned magicians' tests), and a gruagach's harder Ease when he
  initiates himself (Hedge Magic RE pp. 13-14, 30-31, 61, 88-89).
- UnGifted Initiates must suffer an Ordeal and gain nothing from past ones;
  a failed Initiation spends no step of a past Ordeal's help.
- Experimental Initiation Scripts roll the Extraordinary Results chart and
  the rite's validity; an overlapping Script's component can be replaced
  (Ease 15).
- Magi can spend a season on Good Works (The Church).
- A realia **exhibit** of hundreds of objects counts as an Art's presence
  for Study Requirement and Study Bonus; a smaller collection doesn't
  (Against the Dark p. 61). Studying another artist's work gives half its
  Aesthetic Quality, once per work.
- A wondrous item takes the aura where the craftsman works and its one
  assistant's help; Touched by (Realm) and Mythic Farrier must name their
  realm (City & Guild pp. 71-72; Grogs p. 76).
- A regimen raises its patients' Inhabitant points; eucrasia is lost to
  convalescence, travel, disease or Twilight.

### Hedge Magic

- A tradition's effects can be built on its book's guideline table, with
  its own Ranges, Durations and Targets: the gruagachan, the learned
  magicians and imhergi, the vitkir, the folk witches, the Amazons, the
  Augustans, the Muspelli, Soqotra, the Solomonic arts, the Ex Miscellanea
  traditions, the hunters and the Nemthengacha.
- Hedge castings show their botch dice; the Opening Ease Factor counts
  Hermetic Arts; a folk witches' sabbat Opening asks the Magic aura at its
  site, which caps its helpers.
- Elementalist Refining shows what its total makes, rounding down where the
  book gives no rounding.
- The lector priests' transitory items, the hunters' Foe Arts, the
  gruagach's flexible casting and the Muspelli etin-mod follow their books.
- The Franciscans and four Mystery Cults join the traditions; an infernal
  tradition's Vituperation is worked out, with the local aura.

### Florilegium

- Spells, Virtues and labs corrected by Atlas Games' errata (Sight of the
  Lazy Parens keeps its invented-spell clause); Replenishing the Fount of
  the Magus added.
- Demons, magic spirits, ghosts and jinni are checked against their books.

### Pagina

- A Faerie Blood's details give its variety, Legacy and Sympathies; the
  charm Flaws, the Ríastradh and the hero's light explain themselves.
- Faith won in play is written in the Diary and brings True Faith.
- A Reputation can replace a bad one, its deeds counted the book's way, and
  editing it keeps its deeds; the Grogs Aging Chart is offered to
  companions.
- **Tournament** (More on Reputations) counts a season on the tourney
  circuit toward Prudhomme, which starts at 1 only as his first Noble
  Reputation (Lords of Men pp. 25, 64-69).

### Orbis

- A lord's Gratitude can be redeemed for a reward; his Fief shows his
  Affinity (a baron +2 unless chosen higher; Lords of Men p. 21) and his
  Mercenary Budget.
- Regio levels can be terrestrial, celestial, Tartaran or Abyssal; a relic's
  Faith raises its church's Dominion; with Auras change on, a faerie aura
  follows its faerie's glamour.
- Battles ask whether each army fights at home, and the losing commander's
  Morale; a vampire's Sap the Life is a disease.

### Concilium

- Charges say whether they are high crimes; new ruling templates for the
  Code's penalties; Theban contrition, Transylvanian Decorations, the
  Normandy Tourney's points and seven-day Hibernian meetings.

### Peregrinatio

- The packs take the errata (the Rhine's forest spirits' Might, stat block
  spell levels, smaller fixes in Normandy, the Cradle, Thebes and
  Transylvania); Lycaneon's oppidum is at aura 5 below the mountain's 9,
  and Hedyosmos's aura follows the Aura Boon (DE p. 184).

## 3.15.0 — 2026-10-25

### Computus

- Merinita's **Faerie Magic** opens its own Range, Durations and Target when
  inventing a spell: Road, Bargain, Fire, Until (Condition), Year + 1 and
  Bloodline; **Spell Timing** adds If (Condition) and recurring spells (a
  new "Recurs each" choice, +1 to +5 magnitudes and a Ritual); Sensory
  Magic adds Spectacle (DE pp. 236-240; HoH:MC p. 28).
- A spell with a Mystery's own Range, Duration or Target is learned only by
  a magus with that Mystery. A Mercurian magus has Road and Road Network
  once he has learned Road Magic (**Has learned Road Magic** in his
  Hermetic Background; every Mercurian of an older save has it) (TMRE p.
  116).
- Casting reminders for Faerie Magic, Spell Timing and Secret Name; against
  a magus with Secret Name, sympathetic connections add nothing to
  Penetration (DE p. 235).
- A related language reads at the books' penalty: Classical Greek through
  Romaic Greek at -2, and the other Tribunal books' tables.

### Book of Hours

- Faerie Magic stands in for Magic Theory when experimenting or inventing a
  faerie-parameter spell (DE p. 238).
- The **free House Virtue**: ten seasons of one-to-one work with the parens
  give an apprentice his House Virtue (DE p. 272).
- Initiation checks: Secret Name fails for a magus with a talisman or a
  familiar; Faerie Magic needs one touched by the fay.
- With the Art & Academe medicine option, an injury heals with **first aid**
  and **palliative care**, half a chirurgeon's Chirurgy each (together at
  most the nurse's); Recovery Roll gives first aid, operates on a disease
  (nine procedures, each leaving its wound), and can have a chirurgeon try
  a **surgical intervention** when a wound's roll fails, with its lasting
  cost (Art & Academe pp. 59-62).

### Pagina

- **Tremere voting sigils**: the Hermetic Background says who holds a
  Tremere magus's sigil, and "Holds own voting sigil" records winning it
  (DE p. 16).
- Prevailing **Loyalty** follows the advancement table past 6; an Autocrat
  adds the points of both roles; only one person counts for each of the
  three tasks; at -6 the laborers' and craftspeople's savings are halved
  (DE pp. 185-186; Covenants pp. 36-38).
- Scribes kept as specialists count for Writing Materials (DE p. 190).
- Covenant **Reputations** have no cap: a Major Prestige Boon's is 9 (DE
  pp. 28, 184).

### Gauntlet

- Bought specialists are held to the age cap, and a bought teacher can't
  be Gifted or teach a Hermetic Art; the Unknown Hook can't be counted
  twice; a Prestige Boon asks for its Reputation; "Starting income by
  number of magi" adjusts the main source once, 15 a magus (DE pp.
  179-189).

### Florilegium

- The **Nemthengacha** join House Ex Miscellanea's traditions, with a
  symbol of their own (DE p. 244).

### Concilium

- A Theban meeting executes its sentences (shards and tokens), gives a
  shard to one who refused the sortition, places the new archai on the
  Boards and the Treasury Council and draws the tamias, and closes with the
  Ceremony of Propitiation; the Tokens list gains Neutralize and the
  Tribunal's yearly Longevity Ritual (The Sundered Eagle pp. 27-35).
- Transylvania checks offices against privileges, and the roster's
  Oppidum column says whether each oppidum keeps the Tribunal's rulings
  (Against the Dark pp. 15-18).
- Rhine gilds are factions of magi, with leaders and an agenda; a Tremere
  whose sigil his exarch casts no longer votes twice (Guardians of the
  Forests pp. 22-29, 84, 109).

### Peregrinatio

- The Theban pack gives its magi the book's apparent ages, its covenants
  their Boons and Hooks and patrons, and two shared laboratories; the
  Transylvania pack's Chronicle is an encyclopedia of eighteen tractatus,
  and Tablinum's laboratories and the zenodochium's items are records; the
  Rhine pack seats its gilds' magi, fills in its rulings, and (Gild)
  Trained gives 30 + 60 xp as two pools.

## 3.14.0 — 2026-10-25

### Florilegium

- **Start from the book** in New Creature: the Definitive Edition's 62
  creatures (DE pp. 428-492), from the bear and the wolf to the
  elementals, the faerie knight, Baal-Peor and the angel Gabriel, each
  copied whole into the saga to change as you like.

### Book of Hours

- A **Master of (Form) Creatures** tames with Magic Lore in place of
  Intelligence, and a taming season with points enough for one says how
  many more of the same kind they would tame (DE pp. 384-385).
- A tamed animal is **trained** by someone with Animal Handling; an
  Ability new to it asks a Loyalty test against 6 at the season's end
  (DE p. 385).

### Pagina

- **Command the Beast**, in More on a tamed animal's Personality Traits:
  Presence + Animal Handling (Ride, Magic Lore) + stress die against the
  task's Ease Factor, with the Loyalty tests a feared or suicidal task
  asks (DE p. 386).
- A faerie built by Realms of Power: Faerie shows a **Faerie design**
  fact: the Might its Virtues give it, the choices every faerie makes
  that it lacks, and what a faerie can't have (RoP: Faerie pp. 45-64).

### Orbis

- In a fight, a group of tamed animals is led by its leader's **Animal
  Handling**, not his Leadership (DE p. 385).

## 3.13.0 — 2026-10-25

### Book of Hours

- A season working from a **Lab Text** counts the Spells Specialization and
  a similar spell known, as inventing does; anyone who assisted, and a
  Longevity Ritual's subject, can read the texts the season writes (DE pp.
  262-263).
- The laboratory's **Teaching Specialization** adds up to +3 to teaching and
  training, and its **Texts Specialization** a point for every 3 to copying
  and writing, when the season is spent in the laboratory: **In the
  laboratory** on the season, ticked unless you untick it (DE p. 291).
- **Refining** a laboratory reminds you of the familiarity it needs, and a
  magus with a Tidy trait rolls for Spotless; a Hidden Defect can be found
  one at a time, or gained again; a take-over that lowers Refinement says
  when the Virtues no longer fit (DE pp. 287-288; Covenants p. 118).
- A covenant that ends the year broke gets an **Upkeep unpaid** line for
  each of its laboratories, to give each a Flaw that lowers it (DE p. 288).
- An Arcane Connection keeps its **last active season**, and fixing one
  that has lapsed is refused (DE p. 250).
- **Practice** can be split between up to three Abilities at the lowest of
  their qualities, and a language practised among native speakers is worth
  8 only below a score of 5 (DE p. 377).
- Books can be written on a **spell's Mastery** and read into it (DE pp.
  378-379).
- **Blood of the Nephilim** slows every season's learning by age / 10 once
  Decrepitude starts, never below 1 (DE p. 72).
- An aging roll's points **in any Characteristic** are the player's to
  place, one choice a point (Place Aging Points), with the highest offered
  first; the Crisis rolls with the Decrepitude they bring (DE p. 392).
- A Crisis that can't kill doesn't harm the **Unaging**, and a **leper**
  takes a Heavy Wound with each one (DE pp. 114, 135).

### Pagina

- **Constant Effects**, a new section under Aging: the spells and items on
  a character all the time, each giving its Warping every Winter (1 a
  year, and 1 a season for a powerful one not made for them), with **The
  Effect** at the foot of its form (DE pp. 390-391).
- A laboratory's **Personality Traits**, under its Virtues and Flaws, with
  a warning when they don't add up to its Warping (DE p. 289).
- The Aging section warns at **Decrepitude 4 and 5** (DE p. 392).

### Computus

- The lab Virtues and Flaws that lacked them now have their modifiers:
  Cramped's and Empty's choices, the Specialization points of Natural
  Environment, Greater Guardian, Greater Horde and Sacrifices, Faerie
  Ingredients' lower Upkeep, Lightless, Invisible and Shrouded on
  Aesthetics, and an Illusion's balancing Virtue having no effect (DE pp.
  293-296; Covenants pp. 118-119).
- Under a new spell's level, a line says how far its **Target** reaches
  with its extra magnitudes, from the Form's base Individual (DE pp.
  310-311, 546).

### Orbis

- **Cast a Spell** in a fight asks for casting requisites, and the lowest
  Technique and Form among them count (DE p. 312).

## 3.12.0 — 2026-10-25

### Pagina

- **Powers**, a new section under the Virtues and Flaws: the powers
  Greater, Lesser, Personal, Ritual and Focus Power grant, each with its
  Initiative, Fatigue and Penetration, and each Virtue's levels used
  against those it gives; **The Power** at the foot of its form works them
  out as you type (DE pp. 81-106).
- A device can say it is **had by a Virtue**: Minor Enchantments (25
  levels a Virtue, no power over 30), a Masterpiece (one lesser
  enchantment) or a Redcap's 50 levels (DE pp. 97-98, 105).
- **Magic Resistance** from a Church office or crown (with a fifth of it
  to Soak), the relic relied on (added to the office's), Strong Angelic
  Heritage's Divine Might and a Guardian Angel (added to True Faith's);
  the sheet says where it comes from (DE pp. 84, 109, 419-420).
- Device uses come back each season as well as each new day.

### Computus

- The casting Virtues and Flaws the Casting Score can't hold get a
  reminder each with its page (DE pp. 70-145); Clumsy and Inconstant Magic
  take 3 off aiming; Incompatible Arts forbids a spell using its pair.
- Susceptibility to Faerie or Infernal Power halves Magic Resistance
  against that realm; a creature's Magic Resistance and Penetration take
  the aura's modifier for its realm (DE pp. 146, 412).
- Weak Magic buys an item's Penetration a level a point (DE p. 152).
- Susceptibility to Warping gives a point for each realm that gave
  Warping that year: a Virtue counts as its own realm, an event as the
  realm recorded with it (Gain Warping Points asks it) (DE pp. 64, 146).

### Orbis

- In a fight, Cast a Spell applies Incompatible Arts, Painful Magic's
  pain and Life-Linked Spontaneous Magic's Fatigue; a spontaneous spell
  short of its level fails.

### Gauntlet

- Creation follows more Virtues and Flaws: Feral, Sheltered and Foreign
  Upbringing, Savantism's halved xp and caps, Student of (Realm)'s one
  Lore, a Redcap's 300 xp, Warped by Magic's Magic Lore, a Devil Child's
  three free points; the review advises Warped by Magic's Warping, a
  written language for Academic Abilities, Mastered Spells' 50 xp, the
  Nephilim's Great Characteristics, and the Gifted non-magus's Hermetic
  Virtues of intrinsic ability only (DE pp. 56-158).

### Book of Hours

- Fluctuating Fortune alternates Wealthy and Poor years, the troupe
  choosing which years are the Wealthy ones (DE p. 130).

## 3.11.0 — 2026-10-24

### Orbis

- **Fights in full** (Definitive Edition pp. 394-398). A fighter can be
  **mounted** (Ride, at most +3, on Attack and Defence) or **defend**
  another, as shield grogs defend a magus: nobody may strike the one
  defended while a defender stands, and only a defender's botch lets a
  blow through. Edit Fight sets the **range** between the sides (only
  missiles strike at range, -3 an increment past the first) and the
  **Magic aura** where they fight.
- New actions on Next Blow: **Grapple** (the Advantage becomes the Grapple
  Strength), **Break free**, **Split the group** (in half, or thirds),
  **Cast a spell** (a known spell or spontaneous magic: Casting Total,
  Penetration against Magic Resistance, and damage) and **Use a device**.
  Only the actions a fighter can take are offered.
- A magus's **Form Bonus** adds to Soak against harm of its Form: teeth
  and claws, bare hands, wooden or metal weapons, and spells.

### Illuminatio

- **The Blow to Come**: Next Blow, Add and Edit Combatant show an
  inspector at their foot, boxed like a gloss, saying what the choice will
  do and the totals it rolls, or why it can't be done. The terminal shows
  it in a bordered box.
- The fight page reads as a book: the order of blows is a row of
  medallions in the saga's set, each carrying its Initiative, and the
  fighters are entries ruled off on the page. Titles gild only their
  capitalised words.

### Book of Hours

- **The Gift** costs a season of teaching or training 3 (6 for the
  Blatant Gift) when the other side isn't protected by a Parma Magica and
  isn't one of the magus's own covenfolk (DE pp. 169, 186, 204); two
  unprotected Gifted characters both pay.
- Vis for instilling an effect, binding or empowering a familiar can be
  paid in either the Technique or the Form (DE pp. 258, 266-268).
- Bond powers can work out their modified level from uses a day,
  Penetration and the other modifications (DE pp. 267-268).

### Pagina

- **Use an Effect** uses a device's finished effect: its Initiative,
  Penetration and how many of its uses a day are spent (DE pp. 257, 259).
- Attuning a talisman is refused when another magus made the item or
  instilled one of its effects (DE pp. 259-260).
- **Take Harm** asks what the harm comes from (fire, claws, a weapon of
  wood or metal, a poison's kind, drowning) and adds the highest Form
  Bonus that resists it (DE pp. 206-209).

## 3.10.1 — 2026-10-24

### Computus

The closing audit's small fixes, each checked against the Definitive
Edition:

- **Casting.** Fast Caster adds +3 to fast-casting speed; Wound and
  Fatigue penalties apply to fast casting, Concentration (three times the
  Wound Penalty) and aiming; Afflicted Tongue takes 2 off a spell cast
  with words; Susceptibility to Divine Power doubles a Divine aura's
  penalty and botch dice; Twilight Prone risks Twilight on a single botch.
  The sheet reminds you of Heartbeast's -15 and Verditius casting tools,
  and its Casting Score names the Fatigue it costs.
- **Character creation.** Weak Characteristics takes 3 points off the
  budget; eight Virtues and Flaws open the Lore they name; a Supernatural
  Ability from a Virtue lets the character take Penetration; Magic Theory
  3 is advised at Gauntlet; Church Upbringing's 25 xp is checked; missing
  Loyal and Brave are advice, not warnings.
- **Covenants.** Winter Ruins takes the right monster Hook, and a
  covenant has at most seven Aura Boons and an aura of at most 10.
- **The laboratory.** Penetration levels in a device round up; vis
  extraction gives no free pawn and needs a Magic aura; a device's
  capacity counts only effects begun; a companion whose Arts are opened
  gets a full Longevity Ritual; a Momentary Creo spell that isn't a
  Ritual gets a note; a Bjornaer can't bind a familiar, and strengthening
  a bond uses the Arts it was made with.
- **Seasons.** Months lost cut a summa's writing, copying or translating;
  magi can plan Worship; Good Teacher's +5 applies to training; copying a
  Parma Magica or Supernatural Ability book needs the matching score; a
  botched apprentice search leaves the magus duped; the Crisis text says
  what a physician adds.
- **Fights and sieges.** A botched roll keeps its negative total.
- Two spells carry their printed names.

### Concilium

- **The Redcap vote.** An unGifted Redcap has no vote at any Tribunal,
  while a Gifted one votes (DE p. 15); a Redcap carrying a magus's sigil
  casts that magus's vote. Tribunals whose customs give Redcaps no vote
  keep them silent.

## 3.10.0 — 2026-10-24

### Orbis

- **Conflicts**, a new place in the saga beside Seasons and the Bestiary:
  its battles, fights and sieges.
- **Battles between two armies.** A battle is kept once, between two
  armies: each a lord, town or other power of the Region, a covenant, or
  just a name. It shows on the Fief tab of each lord it names, so lords
  can fight one another. A lord's combat groups fill in from his title's
  army, Battle Event asks which army its character fights for, and each
  event is written in both armies' Diaries. Older saves' battles move
  into Conflicts by themselves.
- **Fights, blow by blow** (Definitive Edition pp. 394-398): two sides
  of characters (with their weapons, their wounds going onto their
  sheets), Bestiary creatures (as many as you like) or typed fighters, in
  combat groups with a vanguard and a leader. Initiative is rolled once;
  Next Blow plays each turn (attack, Exertion, a scuffle, disarm or trip,
  disengage), Next Round the rest of the round. A fight's end is written
  in its fighters' Diaries.
- **Sieges, event by event** (Lords of Men pp. 111-116): a castle's
  Garrison, Defenses, Supplies and four walls against the besiegers'
  miners, engines and soldiers. Next Siege Event undermines, bombards,
  scales a wall or sends the garrison sallying out, at the castle's own
  pace, and the stockade's supplies rolls come due by themselves. A
  siege can link the lords on each side, whose armies fill in its
  numbers, and it shows on both their Fief tabs.
- **A lord's Diary**, as places and factions have, after his Standing.

### Illuminatio

- The fight and siege pages drawn as manuscript leaves: the order of
  blows on a red ribbon, each side under its arms, the blow worked out;
  the castle's plan, cord-bound gauges and the seasons the siege has run
  as medallions.
- **Season medallions**, six sets to choose from on Edit Saga: stained
  glass, an illuminated letter's adornment, a wax seal, Limoges enamel, a
  Book of Hours roundel, and pen and wash.

### Glossa

- Help for Conflicts, a fight and a siege, and how-tos for running each.

## 3.9.0 — 2026-10-24

### Computus

- **The rules checked against the books.** Every system was read again
  in the Definitive Edition and its supplements, with the printed pages
  cited in the code; where they disagree, the Definitive Edition wins.
- **Laboratory.** Verditius Runes add Philosophiae to a Shape and
  Material bonus; learning a spell from a teacher has the book's caps;
  Opening the Arts loses, keeps or converts a student's Abilities by the
  book; Mystery Cults' Alexandrite, Hickory Wood and Platinum join the
  Shape and Material tables.
- **Casting.** The Casting Scores now show fast casting, ceremonial
  casting, Concentration, aiming and a talisman's attunements. Mastery
  abilities count by name; the Golden Cord lowers spellcasting botch
  dice. A Spontaneous grid appears beside the Formulaic one whenever its
  levels differ: for Method Caster, Poor Formulaic Magic, a Deficiency,
  Diedne Magic, Weak, Difficult or Ceremonial Spontaneous Magic, or
  Unstructured Caster. A Ritual's Fatigue past unconsciousness becomes
  wounds, and a casting botch can bring Warping and Twilight.
- **Warping, Twilight and aging.** A botched comprehension can reach
  Final Twilight; Age Quickly takes the year it began; Demonic Blood ages
  twice as fast without losing Characteristics; time spent in the aura
  where a character lives sets their Warping from it; the Blood Virtues
  that give Might, and Faerie Virtues in a Faerie aura, protect from
  Warping.
- **Combat and equipment.** Any one-handed weapon is fought with the best
  shield carried; only a shield's Defence counts against missiles; the
  mounted Attack bonus is for melee; weapons' damage levels and types
  come from Lords of Men; Grogs' equipment bonuses and four-footed beasts'
  burdens follow that book.
- **Reputations.** A Reputation is good or bad by its score's sign;
  covenant Loyalty, university exams and disputatio read them as the
  books say. **End of Session**, on More on Reputations, gives the
  session's Confidence Points and counts noteworthy deeds toward a
  Reputation.
- **Medicine**, Art & Academe's, as a saga option: diseases as records
  of their own, with stages, Crises, prognoses and the covenant's
  physician. A Crisis survived asks where its Aging Point goes before
  the next season is played (Place Aging Points, on More on Aging).
- **Creatures.** A creature's build is checked against the rules the
  Definitive Edition states, with its Quality points counted; a power can
  take its cost and Initiative from the Quality that gives it.

### Book of Hours

- **Teaching and books.** Reading and writing need their language and
  Artes Liberales; a teacher can take several students; copies don't use
  up the tractatus allowance; wounds slow or stop study; a Supernatural
  Ability's first season follows the book.
- **Mysteries.** Ordeals lower later Initiations by the Definitive
  Edition's table; varying a Script is rolled, and a failure fails the
  Initiation; distractions cost the Initiation Total; a Gift a hedge
  tradition opened needs 30 more to open the Arts.
- **The covenant's year.** A deficit comes out of Wealth; inflation,
  Familiarity, pensions and soldiers' pay follow the books; excellent and
  wondrous items, moving up a social class and pushed travel are worked
  out; a vis source's yield is hinted from the saga's vis level.

### Concilium

- **Thebes.** Redcaps don't vote, the archon does, and a defamation
  decree names only a magus who is present. The Rhine skips its Grand
  Tribunal year. Each is a Tribunal custom, so other Tribunals keep the
  core rules.

### Peregrinatio

- **The Sundered Eagle, Against the Dark and Guardians of the Forests**
  read page by page against their packs, and the mistakes found fixed.

### Glossa

- Help and the how-to guides follow every change above.

## 3.8.0 — 2026-10-24

### Computus

- **Wounds that heal.** Each wound now remembers where it came from (an
  injury, which heals with Chirurgy, or a disease, poison or deprivation,
  which heal with Medicine) and the +3 its stable Recovery rolls have
  built up. The Recovery Total (Definitive Edition p. 405) is Stamina +
  the best Chirurgy or Medicine among the character's covenant-mates,
  named, + those +3s + magical aid (a Zenodochium's +9) + the
  laboratory's Health + a familiar's Bronze Cord + Rapid Convalescence or
  Fragile Constitution, less an Infernal aura where they live, in which a
  disease can't improve. Health shows it under the wounds.
- **Take Harm**, in More on Health: an injury from heat and corrosion (by
  how much of the body it covers), a fall or an impact, read on the Damage
  Table against Soak; a poison or a disease from the books' tables, a
  Stamina check against its Ease Factor; deprivation of air, water or food,
  costing Fatigue (long-term for food and water) and then wounds. **Recovery
  Roll** rolls the wounds now, during a story. Both are kept only when you
  choose Keep.
- **Long-term Fatigue.** The Fatigue Level shows how many of its levels
  are long-term.
- **Bruises**, a Lords of Men rule option: a non-lethal blow gives a
  bruise, whose penalty counts as a wound's; it heals within hours and a
  Heavy or worse one leaves a residual wound.
- **Penalties everywhere.** Wound and Fatigue penalties now come off the
  Casting Score and certamen totals too.
- **Animal grogs' natural Protection** (at least 1, Grogs p. 137) is
  added to their Soak and can be set on their animal form.

### Book of Hours

- **A season of healing.** When a season is advanced, every wounded
  character makes its Recovery rolls: a Light wound weekly, a Medium one
  monthly, a Heavy one once, an Incapacitating one twice a day until it
  becomes Heavy or kills; bruises leave their residual wounds; everyone's
  Fatigue is rested away. The rolls go into the Diary.

## 3.7.0 — 2026-10-24

### Computus

- **Faerie Magic.** House Merinita's magi, and anyone else with Faerie
  Magic, are attuned to Faerie auras as to Magic ones (Definitive Edition
  p. 236): a Faerie aura adds its full score to their casting, Lab Totals
  and Magic Resistance, neither aura adds botch dice to their magic, and
  neither gives them Warping. Finishing Touches checks that a Merinita
  with no faerie Virtue or Flaw starts with the Warping Point his parens
  gave him.
- **At home in an aura.** Nobody gains Warping from living in an aura of
  the realm their supernatural powers come from (p. 390): a hedge wizard
  in his tradition's realm, anyone with a supernatural Ability in a Magic
  aura (a Divine one for Sense Holiness and Unholiness), as well as magi.
- **Regiones and botch dice.** A foreign aura's extra botch dice double
  when the covenant stands on a regio level, in casting and in vis study.
  Vis study now takes the aura of the student's laboratory, and the
  Twilight from a laboratory mishap or research is rolled against the
  laboratory's aura.
- **The senses.** Magic Sensitivity, Second Sight and Sense Holiness and
  Unholiness list the Ease Factors of what each senses (pp. 168-170), and
  Magic Sensitivity's score comes off Magic Resistance.
- **Dominion Magic Resistance** now takes effect: with the option on, a
  Christian, Jew or Muslim (or anyone whose religion is blank) living in a
  Dominion aura shows Magic Resistance of 5 x that aura on their sheet.

### Orbis

- **Seeing into a regio.** Regio Levels has a See column: the Ease Factor
  to see into each level from the one below, the level's own roll when it
  has one, else the Definitive Edition's (p. 421).
- **Auras that change, by the books.** With the Auras change option, a
  Magic aura follows Realms of Power: Magic: its tethers (scored in the
  place's Tethers) give a base aura, and each winter its yearly modifier
  (the base, auras impinging on it, the covenant's magic, vis study and
  extraction there, this year's botches) may roll it on the Strengthening
  or Weakening table, with botch dice that build up. An Infernal aura
  inside a stronger one erodes as Realms of Power: The Infernal says,
  unless a demon or an enchantment keeps it, and shows its corruption
  roll's Ease Factors. Any Infernal place may now be tarnished with a sin
  and corrupted.

## 3.6.0 — 2026-10-24

### Book of Hours

- **A laboratory's Safety and Warping matter.** Safety now takes dice off
  the botch roll of all lab work, experiments included, and Cautious
  Sorcerer's reduction comes first. A lab with negative Safety risks an
  accident each season: a simple die at or under its Safety means a botch
  roll on the Disaster table. A lab with positive Warping may warp what is
  made in it: a simple die at or under its Warping gives the season's
  product a side effect on an odd die or a modified effect on an even one,
  which you describe in Experiment Results. A season that was not an
  experiment shows these rolls there too, and writes a Laboratory Mishap
  entry in the lab's Diary. These are core rules (Definitive Edition pp.
  288-289), so they apply whether or not Covenants is in play.
- **Experiments follow the book more closely.** Botch dice count the
  laboratory's own aura, as its Lab Total does, and the research odds use
  the same count. A wasted experiment spends its vis. No Benefit drops only
  the experiment's die and risk, so Inventive Genius and an
  Experimentation Specialization still count; and if what is left is too
  low, the project is abandoned with its progress. Stabilizing a discovery
  can botch on a 12+'s extra rolls, two-dice Virtues get their second die
  there, and a run of 12+ is no longer cut off at three. An item being
  investigated resists harmful side effects when its protection holds, and
  a Disaster's Twilight comes to anyone opened to the Hermetic Arts, not
  only magi.

## 3.5.0 — 2026-10-23

### Glossa

- **Go there.** Help can now take you to what it describes. On a topic
  about a tab or section of a sheet, press `g` in the terminal's Help, or
  click **Go there** under the desktop's topic list: Help closes and that
  tab (on the desktop, that chapter) opens on the record you were looking
  at, with the section focused. Steps in the guides for familiars,
  creatures, a covenant's library, a Mystery's Lore and lab planning end
  with a **Go there** link that does the same. When the record you were
  looking at has no such tab, Help stays open and says which sheet it is
  on.

## 3.4.1 — 2026-10-23

### Fundamenta

- **A faster, leaner test suite.** Behind the scenes: the app's checks
  run about a tenth faster, and there are about 570 fewer of them, with
  nothing left unchecked. The check that each sheet shows what it should
  and the check that the key bar stays quick now share one pass through
  the sheets. The check of every key on every section no longer waits a
  second after each key that does nothing. A few form tests that the
  per-form checks already covered are gone, and what only they checked
  has moved into those per-form checks.

## 3.4.0 — 2026-10-23

### Pagina

- **Magic items in a laboratory.** A laboratory's Attributes (on the
  desktop, its Specializations chapter) gain a **Magic Items** list: an
  enchanted device kept in the lab is installed as a Free Magic Item
  Virtue (Minor when very large) or an Enchantment of the lab, and each
  of its effects either grants the lab Virtue or Flaw it duplicates, with
  no space or Build Point cost, or buys points by its level (a
  Specialization point for every 10 levels, a Characteristic point for
  every 20). The form refuses more points than the level buys. An item
  gives nothing while it is kept elsewhere, and its row says so. Deleting
  the device or its effect takes away what it gave.

### Gauntlet

- **Install a magic item while setting up a laboratory.** The Setting Up
  step makes a new device kept in the lab, then its effect, then asks
  what the effect gives; or it installs a device already there. A
  starting laboratory's devices are paid for from the covenant's Build
  Points and listed on its Resources step.

### Glossa

- **How to install a magic item in a laboratory**, a new guide, and help
  for the Magic Items list.

## 3.3.1 — 2026-10-23

### Orbis

- **Undoing a world turn.** Deleting a world turn's entry puts back what
  that year changed more reliably.

### Fundamenta

- **A code-health pass.** Behind the scenes: each shared helper is
  written once (the season order, an Ability's level, the Tribunal
  packs' helpers), the rules no longer reach up into the parts of the
  app built on them (a test now keeps it so), the lists a neighbour
  keeps (castles, guilds, fairs, a threat's stages, a place's levels and
  the rest) and other saved records are type-checked, data read from a
  file is checked with a message rather than a crash, the Tribunal packs
  are read once per form, and code nothing used is gone. The app works
  as before.

## 3.3.0 — 2026-10-23

### Computus

- **Virtues and Flaws in study.** Linguist, Savantism, Flawless Magic
  and Loose Magic change what a season's study gives; Study Bonus and
  Study Requirement ask whether the Art is present; Ability Block and
  Restricted Learning refuse what they forbid; Secondary Insight
  (with a grid to tick the Arts that gain), Elemental Magic, Hermetic
  Sorcery and Magian Lineage share the experience; Master of None
  loses a second raise in a year; Waster of Vis wastes vis studied.
- **Virtues and Flaws in the laboratory.** The lab plan offers only the
  magus's own options (Potent Magic, Cyclic Magic, Environmental Magic
  Condition, a Laboratory Horoscope, extracting Form vis), and counts
  Short-Ranged and Disjointed Magic, Hubris, Waster of Vis, Magical
  Memory and Hermetic Alchemy by themselves.
- **Casting.** The Casting Scores list the Virtues that count only
  sometimes, with a Spontaneous line for Diedne Magic; a Ritual's vis
  counts Mercurian Magic and Waster of Vis.
- **Working seasons and the year.** Wealthy, Poor and License of Absence
  change the working seasons; Perfect Eye for Commodity and Bigamist
  change the business year; Necessary Realm Aura and Independent
  Craftsman change workshop seasons; Academic Concentration and
  Aristotelian Training adjust Artes Liberales by subject; Raised from
  the Dead, Immortality of the Forest and Susceptibility to Warping add
  the year's Warping.
- **Combat.** A specialty naming the weapon adds 1 to Attack and
  Defence, and the combat Flaws (Lame, Missing Eye, Hobbled, Poor
  Eyesight, Slow Reflexes, Primitive Equipment) and natural weapons'
  Qualities and Inferiorities count, each named on a Counted line. A
  character with Ride gets a Mounted line: Ride (at most +3) to Attack
  and Defence, and a charge.
- **Battles (Lords of Men).** A lord's Fief tab lists his battles, and
  More > Battle Event plays each one's next event: the Event Total
  against the stage's Ease Factor, and the losing side's losses.
- **Disputatio (Art & Academe).** More > Disputatio stages a schoolmen's
  debate between two characters, with the Virtues and Flaws that change
  it, and keeps it in both Diaries.
- **A physician's regimen (Art & Academe).** The Aging form takes a
  physician's regimen, which raises Living Conditions for aging once
  lived under for a year.

### Glossa

- Help for each of these, and a guide, How to fight a battle.

## 3.2.1 — 2026-10-23

### Peregrinatio

- **King Fir's Might.** The Rhine pack gives the King of the Black
  Mountain Faerie Might 60, as the book's errata corrects (it prints 90),
  on his Bestiary entry and in the Black Forest and Feldberg places. His
  notes say why it differs from the printed page.

## 3.2.0 — 2026-10-22

### Pagina

- **Connections.** A character's, covenant's and laboratory's sheet has
  a Connections section listing every record tied to it, each name a
  link: its covenant, where it is (and each place around it), the Rhine
  gilds a covenant belongs to, the factions whose links include it
  (**Member of**, with the note on the link), the neighbours it rules,
  and anything else that links to it. On the desktop click a name to
  open it (Back returns); in the terminal click it, or press `m` for Go
  To. Nothing new is stored: each connection is worked out from the
  record that makes it, so changing that record changes both sides.

### Orbis

- **Linked from, clickable.** A place's and a creature's page lists what
  links to it among its facts, on the desktop too, each name opening its
  record; the unclickable rows under Links are gone.
- **A faction's Diary.** A faction has a Diary tab, as a place has, for
  what it does season by season.

### Glossa

- Help on Connections and a faction's Diary, and the faction how-to now
  follows a member back to the faction and keeps its history.

## 3.1.0 — 2026-10-22

### Orbis

- **Names that open their records.** A neighbour's page draws the
  records it names as links: its ruler or leader, the neighbour it
  answers to, the place it is in, and a place's claimant and what is
  found there. On the desktop click one to open its page, and Back
  returns; in the terminal (and a player's browser) click it, or use
  **Go To** in More to choose from them all by keyboard. A Links row
  has an **Open** button on the desktop.
- **Ruler or leader is a record.** Choose a character, another
  neighbour or a creature from the Bestiary (a faerie queen can lead her
  court), or type a name for one the saga has no record of. A typed name
  opens the one record that has it, so packs' rulers link as soon as
  their records are there; deleting the ruler keeps their name, and
  importing keeps the link.
- **Who answers to it, and what it rules.** A neighbour's page lists
  under **Answer to it** every neighbour whose Answers to names it (a
  lord's vassals, a faction's members), and a creature's page lists the
  neighbours it rules.

### Glossa

- **How to set up a faction's leader and members**, a new how-to, and
  help on following a record's links, Go To and the Ruler or Leader
  chooser.

## 3.0.0 — 2026-10-22

### Peregrinatio

- **The Cradle and the Crescent region pack.** Arabia, Mesopotamia,
  Persia and the Silk Road ship as a content pack that sits outside any
  Tribunal: thirteen houses of wisdom kept as covenants, each with an
  aura; the sahirs as companions, 'Arkhaman with the stats the book
  prints and the jinni Kharrat bound to him; the region's cities, holy
  and magical places, peoples and powers; the jinn and other creatures in
  the Bestiary; the Zoroastrians; and the book's history and stories. Its
  assumptions page in Help lists the judgement calls, and the guide to
  starting a saga from a sourcebook names the traditions to turn on.
- **Shared with the Levant pack.** The Order of Suleiman, the jinn, the
  caliph and the other records both books describe are built the same
  way, so a saga can import both packs; the first pack imported keeps its
  version of a record they share.
- **New catalog entries.** The Jinni Virtue and Theology: Zoroastrian,
  which has its own mark on the desktop: a sacred fire on its altar.
- **Leaving out a pack's history** now also leaves out its covenants'
  diary entries.

## 2.127.2 — 2026-10-22

### Illuminatio

- **A long form in Saga Management scrolls.** Export Pack's list of
  Tribunals, covenants and neighbours to tick ran off the bottom of the
  window on the desktop, with no way to reach the last ticks or the
  Export button. A form opened from a chapter with no sections, such as
  Saga Management, now opens in the chapter in place of its buttons and
  scrolls with it, as forms in a section always have.

## 2.127.1 — 2026-10-22

### Illuminatio

- **The desktop remembers its theme.** Whether you last chose Scriptorum
  or Scriptorum Dark, the desktop now opens in it next time, instead of
  always opening in Scriptorum. The choice is kept in this computer's
  settings, beside your bookmarks and the sounds setting.

## 2.127.0 — 2026-10-22

### Peregrinatio

- **The Levant Tribunal pack.** Blood and Sand, with its web companion
  Secrets in Sand, ships as a content pack: the Levant Tribunal of 1220
  with its Code and the Treaty of Baghdad up for renewal in 1221; its
  twelve covenants, four of them rebuilt in full; 49 magi, the eight the
  books print converted from Fourth Edition and Wardat a Hermetic Sahir;
  the crusader states, the Muslim powers, the military orders and the
  region's churches and faiths; its holy and magical places, Bestiary,
  history and stories. Its assumptions page in Help says the stats follow
  the Definitive Edition's conversion guide where it applies, and lists
  every judgement call made for the rest.
- **Shared records for the Middle East.** The Order of Suleiman, the jinn,
  the Nizaris, the Ayyubid sultans and the other powers the Levant shares
  with its neighbours are built the same way in every pack that has them,
  so importing two such packs updates them rather than making copies.

### Concilium

- **The Levant's customs.** A Tribunal can keep the Levant's customs: the
  Treaty of Baghdad, renewed every ten years, shown on its Peripheral
  Code tab.

### Florilegium

- **Secrets in Sand in the catalog.** Its four Virtues and Flaws for magi
  of the Islamic Tradition, and the book itself among the saga's sources.

## 2.126.0 — 2026-10-22

### Sodales

- **Host for Players from inside the app.** The saga page's Saga
  Management on the desktop, and More on the saga in the terminal, now
  have **Host for Players**: choose your address on the private network
  (a Tailscale one is marked), the browser port and, if you like, SSH,
  and the players can open the saga in their browsers. Saga Management
  then says where they reach it, and **Stop Hosting** ends it and closes
  every player's copy; closing the app stops it too. The form remembers
  what you chose, and refuses an address the computer doesn't have or a
  port another program is using. `tools/serve.py` still hosts from a
  terminal as before.
- The hosting guide now walks through starting and stopping from either
  version.

## 2.125.3 — 2026-10-22

### Illuminatio

- **One New Character at a time.** On the desktop, New Magus, New
  Companion and New Grog in a covenant's People chapter could each open
  another New Character form while one was already open, so several
  could pile up. Now, while any form is open on a page, clicking a New
  card takes you back to the open form (scrolled to, with the cursor in
  its first field) instead of opening another.

## 2.125.2 — 2026-10-22

### Book of Hours

- **Taking over a laboratory with no owner.** A laboratory left with no
  owner couldn't be taken over: the season was only offered on the
  laboratory's own Planning tab, which plans for its owner. A magus now
  plans Take over the laboratory on their own Planning tab (under
  Order & covenant), choosing the laboratory; when the season is
  played the laboratory becomes theirs, its Refinement drops to at
  most their Magic Theory - 3, and the Predecessor may linger. Any
  laboratory they had is left with no owner.

## 2.125.1 — 2026-10-22

### Illuminatio

- **A neighbour's lists fill the Inspector.** Clicking a row in a
  neighbour's lists on the desktop now shows it in full in the
  Inspector, as other pages' tables do. A threat's stage shows when it
  comes, what became of it, its clues, and what happens if it is
  ignored, stopped or turned; a lord's castles, a town's guilds and the
  rest show each of their columns.

## 2.125.0 — 2026-10-22

### Book of Hours

- **Experiment Results in Advance Season.** Each experiment whose
  Extraordinary Results need the storyguide's word gets one form: which
  of two rolls stands (Exciting Experimentation, Creative Block), what
  each side or modified effect is, where a Discovery's experience goes,
  what a special result becomes, a Disaster of 5 or more, and whether to
  take a Discovery the risk can reach.
- **Experimental effects stay with the creation,** warts and all: on
  spells (and the copies learned from them), instilled effects and their
  Lab Texts, bond powers, the familiar's bond and Longevity Rituals, each
  with the season it came from and a fatal flaw marked. They can be
  described or changed later from a known spell's Mastery, an item's
  effect or a bond power; a new Range, Duration or Target changes the
  creation, never its level.
- **Potency is worked out.** One step is 5 points of the Lab Total, or 1
  point of a Longevity Ritual's modifier, so a weakened ritual protects
  less on every aging roll. Help names this as the app's assumption.
- **Special results are carried out:** a story event goes into the
  laboratory's and covenant's Diaries as an open Story Event, a spell
  created as well is learned with its Lab Text, and extra vis is paid
  (or the season is a Complete Failure).
- **Experimenting follows the Definitive Edition more closely:** a 12+'s
  further rolls are stress dice that can botch; a Disaster of 5 or more
  is a story for the covenant or the laboratory destroyed; work whose Lab
  Total is too low still rolls the chart and loses its vis; and
  investigating an item by experiment can destroy it unless one of its
  own effects protects it.
- **Original research is now Arcane Discovery,** the Definitive Edition's
  name, and its Research log keeps what each season left on the work.

### Illuminatio

- **The Troupe.** The saga page opens on a new first chapter gathering
  the player characters (by covenant), the covenants the troupe plays
  and any page you bookmark, each a click from its sheet.
- **Bookmarks.** A ribbon at the right of a record's header bookmarks it
  onto The Troupe; bookmarks are kept on this computer, saga by saga.
- **A page reopens on the chapter you left it at,** until the app is
  closed.

## 2.124.0 — 2026-10-21

### Book of Hours

- **Breakthroughs unlock spell parameters.** Inventing a spell offers
  the standard Ranges, Durations and Targets, and beyond them only those
  open to the magus: from a Virtue (Canaanite Magic's Veil of Death,
  Fertility Ritual Magic's Unborn Child, Hermetic Rune Magic's Rune and
  Inscription, and the rest), from a breakthrough they reached, or from a
  spell they know that uses a breakthrough's parameter. The line under
  each list says what opened it.
- **Ancient Magic's new parameters.** Event (a Ritual held until its
  trigger), Unlimited Range and the 19 Years Duration, each costed as the
  book gives it.
- **A goal can grant a Range, Duration or Target of the troupe's own,**
  written as "Range: Horizon (as Sight)"; reaching it puts it on the
  magus's lists.
- **True Lineages' discoveries** join the ready-made research goals: the
  six Parma Magica folds, Parmulae, Figurine Magic, and Realm-aligned
  spells and mastery.

### Computus

- **Other... is now an optional rule.** Any spell parameter (Edit Saga,
  off by default) lets a spell have any Range, Duration or Target with
  its magnitudes typed in.

## 2.123.0 — 2026-10-21

### Pagina

- **A Research tab for every magus.** Their research goals and a Research
  Log of every season spent on them: the die, the risk, any move and what
  came of it. A goal's details show where it stands, step by step (Goal
  agreed, Seek, Discovery, Stabilize, Breakthrough, Spread), and the odds
  of its next season; a season's show its roll on the Extraordinary
  Results chart. Research Goals moved here from Hermetic Magic.
- **Secret targets.** A goal can keep its target secret: the sheet shows
  only the points gained until it is reached.
- **A laboratory shows its owner's research** on a Research tab of its
  own while any is under way.

### Book of Hours

- **Research is chosen, not typed.** Planning lab work or an insight
  season picks the goal from the magus's own; Risk + names the chance of
  a Discovery at each risk, and the line above Schedule gives the
  season's odds as you change it (for stabilizing, the chance it holds).
- **A roll card when a Discovery is in reach.** Advance Season shows the
  roll, the chart with its band marked, and the chance a stabilization
  would then succeed, before asking whether to take the move.

### Illuminatio

- **A Research chapter, set like a book.** Each goal is a card with the
  road of its research drawn in gilt roundels; the log is a ruled ledger,
  and the chosen season's roll is drawn on a ribbon of the chart.

### Scriptorum

- **A tenth tab opens with 0**, as the number keys run along the keyboard.

## 2.122.1 — 2026-10-21

### Book of Hours

- **Original research follows the Definitive Edition.** Taking the move
  onto 10 now gives a Discovery as well as the roll's own result (a side
  effect or modified effect still stands), and a season the roll wastes
  gives none. A Discovery toward a research goal no longer gives the
  Discovery table's experience, nor does one rolled while stabilizing.
- **Stabilizing repeats the Discovery exactly.** It uses the Discovery's
  own risk and moves the roll as before; a failed attempt must be tried
  again the very next season, and a goal's details say when.
- **One Discovery per spell.** A spell or enchantment that has given a
  Discovery toward a goal can't be used to seek another, and the goal's
  details list them.
- **Smaller fixes.** Inventive Genius adds 3 to Seek an insight; a
  Discovery's experience roll of 9 brings the Art to its next score, and
  10 or more rolls twice more; Stabilize a Discovery and Seek an insight
  no longer need Houses of Hermes: True Lineages in play.

## 2.122.0 — 2026-10-21

### Book of Hours

- **The covenant's Seasons board.** A covenant's Seasons tab is now a
  board for the year: each person down the side, this season and the
  three after it across, with what each has planned or "nothing", and
  each companion's working seasons this year ("1 of 2"). The details
  panel lists the chosen person's seasons ahead.

## 2.121.0 — 2026-10-21

### Book of Hours

- **Seasons ahead count the seasons before them.** A season ahead is
  now worked out from the character as the seasons planned before it
  will leave them: a summa read in Spring counts in Summer's Lab Total,
  and a second season on the same book starts where the first leaves
  off. A season whose die isn't rolled yet counts as nothing gained, and
  the seasons after it say so.
- **A calendar of each character's seasons.** Each character has a
  calendar of their seasons, a year a line: in the terminal a new
  Calendar section on the Planning tab, on the desktop the Diary's
  Seasons calendar. Each planned season shows what it's expected to
  give, such as "Ignem 7 (+15 xp)".

## 2.120.0 — 2026-10-21

### Gauntlet

- **Animal grogs.** A grog can be a horse, a hound, a hawk or any other
  beast that serves the covenant (Grogs, Horses & Hounds). The Animal
  Form on the worksheet sets its kind (Clawed Beast, Hoofed Beast, Bird,
  or Fish or Serpent), species, animal Language, lifespan and Size, and
  the worksheet follows the book: Restricted Learning, No Hands and Mute
  at no cost, an animal's Social Status, a Pre-adult Life step of 120 xp
  in place of Early Childhood, its Language fixed at 2, no training
  packages, Strength and Quickness moved by Size, and its kind's
  penalties with humans on the sheet, where Intelligence reads Cunning.
- **Animal templates.** New Character offers the book's sample Dog (1
  or 4 years old), Horse (3 or 10) and Hawk (8), marked "(Grogs, an
  animal)", through the same choices as the human grog templates.
- **The Grogs Aging Chart.** An older grog's worksheet can take its
  pre-play aging from the chart of expected Aging Points a decade, mild,
  average or harsh, instead of rolling every year; harsh aging may raise
  the Ability cap by 1 and mild lower it by 1, and the chart's crises
  are optional.

### Book of Hours

- **Animals age by their kind.** An animal grog ages from its kind's
  age, with its own roll bonus and number of rolls a year (five for a
  clawed beast, spread over the seasons, two for a hoofed beast), when
  the seasons are advanced.

### Pagina

- **Hounds.** The covenant's Covenfolk tab has a Hounds list beside
  Horses, with a quantity for each. An animal grog can be put on either
  list; hounds count no inhabitant points.

## 2.119.0 — 2026-10-21

### Gauntlet

- **Quick and Easy Virtues and Flaws.** New Character offers the
  Definitive Edition's quick recipes, marked "(DE quick)": one for a
  grog, four for a companion (martial, learned, social and magical) and
  one for a magus. Each asks only for its few choices (the Ability its
  Puissant and Affinity name, the Flaw, the Social Status) and makes the
  character In Creation with just those Virtues and Flaws, to finish on
  the worksheet.
- **Mythic Companion templates.** A Mythic Companion's Template list
  has one for each kind the books describe: the Definitive Edition's
  Devil Child, Faerie Doctor, Nephilim and Spirit Votary, and the Zahid,
  Perfectus, Kabbalist, Diabolist, Summoner, Blood of Heroes and Maestro
  of the supplements. Each gives the Virtues and Flaws that kind must
  take, lets you swap a Flaw where the book allows a substitute, offers
  more Virtues and Flaws of your own, and can put the book's minimum
  Abilities on the worksheet. Realms of Power: The Divine's Mythic
  Companion Perfectus is now a Virtue of its own, beside the Definitive
  Edition's Perfectus Social Status.
- **The supplements' companions.** A companion's list has 24 ready-made
  companions from Realms of Power: The Divine, The Church, Art &
  Academe, City & Guild, Covenants, Apprentices, Magi of Hermes, Hedge
  Magic and Mythic Africa, such as the Byzantine Priest and the Mystic
  Nun. Each brings the book's age, Characteristics, Virtues and Flaws
  (untick any to leave it out), Abilities and specialties, and starts
  In Creation so the worksheet checks it.
- **A Grogs template as a companion.** With Grogs in play, each of its
  grog templates can be played as a companion, held to a companion's
  limits once a Story Flaw is added, as Grogs says.
- **A Gifted companion.** The worksheet now gives the Definitive
  Edition's advice when a companion takes The Gift: allowed, but it
  should be extremely unusual.

## 2.118.0 — 2026-10-21

### Gauntlet

- **The Grogs templates.** With the Grogs book in play, New Character
  offers the 19 grog templates of Grogs' Chapter 7, from the Advisor to
  the Time-Lost Witness. Choosing one first asks its choices: the
  version (Christian, Islamic or Jewish Confessor, say), the age, the
  Social Status, the book's Virtues and Flaws (untick any to leave it
  out), its suggestions, any other Minor Virtue or Flaw, its
  Characteristics and its Personality Traits. A grog's limits hold: no
  Major or Hermetic Virtues or Flaws, at most three Minor Flaws, and no
  more Virtue points than Flaw points. The grog then starts In Creation
  with the book's Abilities for that age, its traits (with Loyal, and
  Brave for a warrior), and a biography noting where the app differs
  from the book.
- The Creation Worksheet no longer warns a grog off Inoffensive or
  Offensive to (Being) as if they were Hermetic.

## 2.117.0 — 2026-10-21

### Gauntlet

- **Training packages show their years.** A grog's Later Life line now
  names the years a training package takes, so a grog of 31 with a
  5-year package reads "26 years: 5 in training packages, 21 years at
  15 xp = 315 xp" instead of seeming to have lost five years.
- **The Grogs childhoods.** With the Grogs book in play, Covenant
  Upbringing offers the Covenant-bred childhood (which may also buy
  Latin and Order of Hermes Lore), and Feral Upbringing the Feral one:
  a feral child has no Language and 120 childhood xp instead of 75 + 45.
- **More training packages.** Failed Apprentice (which needs that
  Virtue), Student (monastic school) and Student (private tutor or
  university), and Natural Philosopher's formulae in its name.

### Florilegium

- **Three Grogs Virtues and Flaws.** Mythic Farrier, Pack Mentality and
  Worthless Abilities join the catalog; the rest of Grogs' Chapter 6 was
  already there under its Definitive Edition names.

## 2.116.0 — 2026-10-21

### Book of Hours

- **Paired plans.** Planning Be taught or Be trained now plans the
  teacher's or master's season too; planning Teach with a student plans
  the student's Be taught; and lab work can name an assistant, whose
  Assist is planned for them. If the other person already has a
  different plan, Save says so. Clearing either side clears both, after
  one question.
- **A default for unplanned seasons.** When you advance the season,
  anyone with nothing planned gets the saga's default, set in Edit Saga
  for Magi, Companions and Grogs: Work / Exposure in their Profession,
  else Magic Theory for a magus, else their highest Ability that isn't a
  language; for Grogs, 2 xp a season in their best Ability. Their Diary
  marks it "(default)". Each can be set to Nothing instead.
- **Who has nothing planned.** Advance Season names the player
  characters with nothing planned (and, with a new saga setting, the
  non-player characters too). For each you can choose the default,
  nothing, or planning their season there and then. A plan that can't
  be carried out can be planned again from the same step.

## 2.115.0 — 2026-10-21

### Pagina

- **Formatting in what you write.** The longer text you write yourself,
  such as a Biography, a covenant's Description, a record's Secrets, a
  book's Description or a diary entry's Details, shows `**bold**`,
  `*italic*` and `~~struck through~~` text, lines starting `- ` as
  bullets and lines starting `1. ` as numbered items (two spaces in
  front nests an item). The hint under each such box lists the marks.
- The same text is formatted wherever it's shown, in the terminal and
  the desktop version alike: a Biography, Physical Description and
  Effects of Aging, summaries and a Tribunal's History, a creature's
  Appearance and Notes, spell descriptions and a season plan's Notes
  now take it too.

### Illuminatio

- The desktop sheets show that formatting in the text itself, not only
  in the details pane: the hint promised bold and italic where the
  sheets showed the asterisks. A bulleted or numbered item that wraps
  lines up under its words, not under its bullet.

### Glossa

- A guide, How to format your notes, with every mark and an example.

## 2.114.0 — 2026-10-21

### Book of Hours

- **Plan long work in one go.** The Plan Season form's new For field
  plans a season for this season only, for 2 to 4 seasons, or until the
  work is done: reading a summa up to its Level, or writing, copying or
  translating a book, for as many seasons as it needs. A number of
  seasons repeats any plan.
- **Plans that keep up.** After each season of work planned until it's
  done, the seasons it still needs are worked out again: an interrupted
  or weak season adds one at the end, and finishing early clears the
  seasons no longer needed.
- **Interruptions.** When work runs until it's done, Advance Season
  first asks whether anything interrupted it: days away from the
  laboratory, months lost to distractions, or the whole season lost.
- **Clearing a longer plan.** Clearing the first season of a plan that
  runs for several seasons asks whether to clear the later seasons too.

## 2.113.0 — 2026-10-21

### Pagina

- **Every record keeps its secrets apart.** Covenants, characters,
  Tribunals, neighbours and creatures have a Secrets tab of their own,
  the last on the sheet: what only the storyguide should know, written
  and edited there instead of under a heading at the end of the notes.
- Older saves move what they kept under a "Secrets" heading in a
  record's notes or summary into its Secrets when they load.

### Sodales

- A player signed in to a hosted copy doesn't see a record's Secrets,
  and a web export a player makes leaves them out.

### Peregrinatio

- The Tribunal packs put their secrets on covenants, characters,
  Tribunals, neighbours and creatures in the new Secrets tab. Places,
  cases, diary events and book descriptions keep theirs under a Secrets
  heading as before.
- Aedes Mercurii's founding is no longer hidden among its secrets.

### Illuminatio

- The desktop sheets have a Secrets chapter, marked with a keyhole.

### Glossa

- A help page for the Secrets tab, and a guide to keeping secrets from
  the players.

## 2.112.0 — 2026-10-21

### Book of Hours

- **Plan a full year ahead.** A character's Planning tab now lists the
  Seasons Ahead under This Season: the next three seasons, a full year
  with this one. Each can be planned, changed or cleared there.
- **Move a plan within the year.** The Plan Season form has a Season
  field, so a plan can be moved to another season of the year. A season
  that already has a plan can't be chosen for another one.

## 2.111.0 — 2026-10-20

### Book of Hours

- **Find an activity fast.** Choosing a season's activity, or a lab's
  work, opens a list grouped by Type (Study, Writing & books, Order &
  covenant and so on) that you can narrow by Type, by Book or by typing
  part of a name, with the character's recent activities at the top.
  The list shows just each activity's name; its sourcebook, Type and rule
  are shown beside it.
- **Set up a new laboratory from the character sheet.** "Set up a new
  laboratory", under Order & covenant, needs no lab yet: applying it
  makes the lab in the magus's covenant with the Basic Flaw, and Advance
  Season then offers to have the magus finish it next season, which you
  can decline.
- **Invent from any spell.** A new spell can start from any spell as a
  template, the magus's own known spells listed first, from New Spell
  or the form's Start from. A spell the magus already knows has to be
  changed before it can be invented.

## 2.110.0 — 2026-10-20

### Concilium

- **Hold Tribunal is clearer.** Each step's form says which step it is
  (Step 3 of 9), which step comes next, what the app works out for you
  and what your entries change. Saving a step opens the next one
  straight away, and Cancel stops with the meeting waiting where you
  left it. The Meeting tab shows the step in hand, the step after it and
  the same guidance.
- **The roll call comes first.** Tick who is present, covenant by
  covenant (or the whole covenant at once), count a sketch covenant's
  unnamed magi, and record the proxies. The meeting shows whether it is
  quorate: twelve magi in person from four covenants, and a Quaesitor.
  The Praeco and the Presiding Quaesitor no longer vote, as the rules
  say, though the Praeco breaks a tie.
- **Speakers come from drop-downs.** The prosecution and defence (or a
  motion's speakers) are chosen from the magi present, a Guernicus
  advocate for an accused who stayed away, the Presiding Quaesitor for a
  high crime, or the Tribunal itself against a motion. A speaker with no
  scores debates as Middling, Able or Formidable.
- **A case can be settled in private** at the private hearing, with no
  debate and no vote.
- **The vote says why** each covenant leans as it does, and a tie asks
  how the Praeco casts the deciding vote.
- **Rulings from templates.** A ruling can be written from a template
  with blanks to fill ("Keep holds the ford for 7 years, until it is
  debated again"). Edit Saga keeps the saga's own templates.
- **Terms come due.** A ruling made for a term warns you the season
  before it ends and again when it ends, puts the matter back on the
  Tribunal's docket, and shows in Ahead.
- A new guide, How to hold a Tribunal, walks through a whole meeting.

### Scriptorum

- Notes at the top of a form now wrap instead of being cut off.

### Illuminatio

- Notes at the top of a form now wrap instead of being cut off.

## 2.109.1 — 2026-10-20

### Peregrinatio

- **Slips in the Rhine pack fixed.** Tabanus and Felicia, the two
  wandering magi of the Tribunal chapter, now have the book's own stat
  blocks (Tabanus is 38, not an assumed 50, and Felicia has a record of
  her own). Stentorius no longer leads the Oak Gild: Murion does, and
  only her raven thinks otherwise. Roznov has seven magi, so five are
  unnamed. The Diary gives the book's other date for Rethra, Oakdell
  and Grand Silesia.
- **Slips in the Normandy pack fixed.** Barnabé the cursor has the
  book's stat block, as a grog you can place at your covenant, and
  Skuld's record notes that the book has her at Atramentum before it
  was founded.
- **Slips in the Theban pack fixed.** Monorchis keeps Latin as his
  Hermetic language, like the rest of Gigas, and Alexandria has
  thirteen unnamed Redcaps, which matches the book's fifteen.
- **Slips in the Provence pack fixed.** The Diary no longer dates the
  Coenobium's founding to 975, which matches its 970 founding year.
  Aedes Mercurii has seven unnamed magi. The eight magi whose age is
  only the default of 50 now say so on their sheets.
- Each pack's Assumptions page in Help says what changed.

## 2.109.0 — 2026-10-20

### Insignia

- **A symbol for every tradition.** The other 75 traditions in the
  catalogue (faerie, holy, infernal, Ex Miscellanea and the regional
  traditions) each have their own symbol, so every hedge wizard shows
  their tradition's symbol in place of the figure of a person.
- **A mark for every Ability.** The 114 Abilities from the other hedge
  books that borrowed a related Ability's mark now have their own: the
  faerie rites and Ars Fabulosa, the Holy Methods and Powers, the
  maleficia and Goetic Arts, the settut powers, the Solomonic arts, the
  Amazons' Vowels and Consonants, the Augustan Schools, the Muspelli
  powers, the Soqotran tribes, the Hyperborean hymns and the Hunters'
  Arts.

## 2.108.0 — 2026-10-20

### Insignia

- **Tradition symbols.** The six Hedge Magic traditions (Elementalists,
  Folk Witches, Gruagachan, Learned Magicians, Nightwalkers and Vitkir)
  each have a symbol cut like the House symbols. A hedge wizard shows
  their tradition's symbol wherever a magus shows their House: on their
  person card, beside their portrait and over their laboratory.
- **Clearer leaves.** The leaves on the Folk Witch Magic Theory and
  Salutem marks are drawn at their proper size.

## 2.107.0 — 2026-10-20

### Hedge Magic

- **Creating a tradition member.** A hedge wizard is created by the
  book: the tradition's free Virtues, its apprenticeship (the vitkir's
  290 xp, the gruagach's years of training) and its Gift and score
  rules are checked on the worksheet's Training step.
- **Casting and Magical Defenses.** Each tradition's chapter shows its
  Casting Scores in the covenant's aura, with Penetration, and its
  Magical Defenses, as the book works them out.
- **A tradition's seasons.** A master can Open a student's Gift to his
  tradition, each tradition's own work is on the Activity list for its
  members, and initiation into a tradition's Mysteries uses its Scripts.
  Each chapter gains a Seasons section saying what its seasons give.
- **Effects and items.** Each chapter has an Effects and Items list:
  spells, charms, rune scripts, rites and powers, and the amulets,
  chartae, fetishes, potions, tattoos and wondrous items made with them,
  each with its Casting Score or Lab Total.
- **Bound beings, Warping and pools.** Familiars, fetches and other bound
  beings, with what they add; each tradition's Warping response in place
  of Twilight (the elementalists' worked out Trait by Trait); and the
  pools some traditions keep.
- **Every tradition in the books.** 81 traditions in all, from the
  Realms of Power books, the Houses of Hermes, the regional books, Rival
  Magic, Ancient Magic and Against the Dark, each switched on under
  Traditions Offered while its book is in play.
- **Hybrid magic.** A magus with Holy Magic uses it for Magic Theory in
  the lab and draws on Divine auras; Chthonic Magic draws on Infernal
  auras; neither gives Warping from its realm's auras. A Ritual adds
  Method + Power when that is better than Artes Liberales +
  Philosophiae, and a magus holding a Goetic Art may use Rego and Vim
  for it.
- **Magi in traditions.** A magus of House Ex Miscellanea can join his
  House's traditions, whose Virtues become his free House Virtues, and
  any magus can join the holy societies; a magus keeps Twilight.
- **Integration breakthroughs.** Add Research Goal offers the books'
  integrations (Ancient Magic's nineteen, Subtle Opening and Quick
  Charged Items) ready-made, with their points and what they grant.

### Florilegium

- **The traditions' Arts, Virtues and Flaws.** 118 more Abilities
  (Sihr, the Goetic Arts, the Holy, Unholy and Faerie Methods and
  Powers, Fertility Lore...) and 121 more Virtues and Flaws, among them
  the six Hermetic Virtues the integrations grant.

### Peregrinatio

- **The packs' hedge wizards.** A faction can name the tradition its
  members are played from. The six packs' hedge factions are linked, and
  Thietmar and Tibor of Transylvania are tradition members with real
  Art scores.

### Insignia

- **Marks for the new Abilities.** Each new Ability shows the mark of a
  kindred one on the desktop sheet until it has its own.

## 2.106.0 — 2026-10-20

### Hedge Magic

- **Hedge traditions.** The six traditions of Hedge Magic, Revised
  Edition (elementalists, folk witches, gruagachan, learned magicians,
  nightwalkers and vitkir) are in the app. Each has its own switch under
  Traditions Offered on the Books tab, off until you turn it on, and is
  offered only while its book is in play.
- **A chapter per tradition.** A character joins a tradition from More,
  Traditions (on the desktop, the Traditions button in the Abilities
  chapter). It then gets a tab or chapter named after the tradition's
  magic, such as Rune Magic, listing its Arts and Abilities grouped as
  Techniques, Forms, Runes and so on. Those leave the Abilities chapter.
- **Hedge Arts score as the book says.** Most hedge Arts and the vitkir's
  runes advance on the Art table, as Hermetic Arts do; Difficult Arts
  (the elementalist Forms, the gruagach's Give and Take, the learned
  magicians' Techniques) advance as Abilities. Study, teaching and the
  seasons use the same table.
- **A guide.** Help has a new how-to, How to play a hedge wizard.

### Florilegium

- **Hedge Magic's Arts, Virtues and Flaws.** 54 hedge Arts and Abilities
  and 110 Virtues and Flaws, checked against the printed book and Atlas
  Games' errata. Short-Lived Runes is a Major Flaw, as its own entry
  says; the book's sidebar lists it as Minor.
- **One Divining Art for the elementalists.** The book gives each
  elementalist Technique one score shared by its medicinal,
  philosophical and theurgical kinds, so Medicinal Divining is now
  Elementalist Divining. A saved Medicinal Divining loads as Elementalist
  Divining, at the same score.

### Insignia

- **Marks for the hedge Arts.** Every new hedge Art and Ability has its
  own mark on the desktop sheet, drawn in code like the rest.

## 2.105.0 — 2026-10-20

### Peregrinatio

- **The Hibernian Tribunal pack.** The Contested Isle ships as a content
  pack: the Tribunal of 1220 with its Code, docket, ambassadors,
  treaties and the Coill Trí's túatha; its eleven covenants with their
  cathaigh, magi and Redcaps; the five provinces' lords, churches, towns
  and faerie places; the High Roads; its stories, history and Bestiary.
  Its assumptions page in Help lists what the pack inferred and the
  judgement calls it made where the book is silent.

### Florilegium

- **A spell's name corrected.** "It Will Be Health To Your Flesh, And
  Strength To Your Bones" now has its full name in the spell catalog.

## 2.104.0 — 2026-10-19

### Glossa

- **What's New by feature and edition.** What's New now shows what changed
  feature by feature: Latest at the top, then each feature with its
  numbered editions (the newest in full, earlier ones a line per change),
  then the Chronicle, every version newest first under its major version
  and its day. The page is about half as long as before, so the desktop
  lays it out fully at any window size.
- **Names for the major versions.** The title page shows the major
  version's name rather than a feature's: Incipit for 0.x, Folio for 1.x
  and Codex for 2.x. The sheets feature is now called Pagina.

## 2.103.0 — 2026-10-19

### Concilium

- **Hibernia's cathaigh.** A covenant of a Tribunal that keeps Hibernia's
  customs has a cathach, the treasure it shows to be heard at the
  meeting. The covenant's form records which it is and who holds it if
  it was taken; a covenant that can't show its cathach is marked so at
  Attendance, and its votes don't count.
- **No vassals in Hibernia.** A covenant there can't swear itself to
  another covenant of the same Tribunal: the form says why.
- **Ambassadors and treaties.** The Tribunal's new Ambassadors tab lists
  the ambassadors who speak for the túatha and other peoples, and the
  treaties they have sworn. A confirmed ambassador takes a seat in the
  hall and casts a vote of their own.
- **The Sacred Council and the tithe.** Holding a Hibernian meeting opens
  with the Sacred Council, which confirms the ambassadors and notes any
  disputes, and closes with the tithe of Gifted children. The children
  are generated, each with a name, an age, the kind of Gift and signs of
  what they may become; the storyguide gives them out by hand or lets the
  covenants bid for them, and each winner pays in vis and gains an
  apprentice.

## 2.102.1 — 2026-10-19

### Illuminatio

- **The Armarius icon on the Windows taskbar.** The desktop version now
  tells Windows it is its own app, so the taskbar shows the Armarius
  sigil rather than Python's icon on every computer, whatever its
  taskbar settings.

## 2.102.0 — 2026-10-19

### Peregrinatio

- **The Transylvania pack.** Against the Dark: the Transylvanian Tribunal
  ships as a content pack. It holds the ten oppida the book writes up,
  with the zenodochia and Leviathan as sketches, and the forty-two named
  magi, each with their privilege in the five legal covenants and each
  oppidum's aediles. Monica Ierne comes as the book prints her and the
  rest have generated stats. Albertus is the Praeco and Benilda the
  Presiding Quaesitor. It also brings Hungary, Bulgaria, the Slav lands
  and Transylvania's border peoples with their places, regiones, auras
  and vis, Tablinum's ten regio levels, the Teutonic Knights and the
  kings and churches around them, and the hedge traditions as factions.
  The Peripheral Code, the docket for the Tribunal of 1221 at the Shipka
  Pass and the Tribunal's history are there too, with the book's
  creatures in the Bestiary and the Dragon War as the main story.

### Florilegium

- **Storm wizards, black hawthorn and the Zenodochium.** The storm
  wizards' Storm Calling, Storm Fighting and Storm Riding join the
  Abilities, each with its own mark. Black hawthorn joins the shapes and
  materials, and the Zenodochium joins the covenant Hooks.

### Glossa

- **What each pack assumed.** Help has a page for each Tribunal pack,
  "Assumptions made for" its book. Each page lists the values the pack
  inferred from the book's words, the ones it chose where the book is
  silent (an aura it never numbers, a season, a placement), and where it
  corrects the book. Importing a pack now says so and names the page.

## 2.101.0 — 2026-10-19

### Peregrinatio

- **Transylvania's oppida and five covenants.** In a Tribunal following
  Transylvania's customs, the places where magi live are oppida: the
  roster is headed Oppida, and an oppidum's sheet and its magi's sheets
  say so. Each magus belongs to one of the five legal covenants
  (Coeris, Domostron, Asclepius, Diodorus, Pannonia), whose privilege
  says what they may do. A new Five Covenants tab lists every magus with
  their oppidum, privilege and offices, grouped by legal covenant, and a
  magus's sheet shows their privilege. Each oppidum's aediles are chosen
  from its own magi on its Edit form, and the roster's Aediles column
  shows them. The old per-covenant Class column is gone: a saga that
  gave an oppidum a class gives it to each of that oppidum's magi.

## 2.100.0 — 2026-10-19

### Florilegium

- **Change what a Virtue or Flaw names.** Edit on a Virtue or Flaw now
  changes what it names, such as Puissant Magic Theory to Puissant
  Finesse, Affinity with Creo to Affinity with Rego, or a laboratory
  Virtue's Specialization, without deleting it and taking it again. It
  keeps its place in the list. The choices and refusals are the same as
  when it was taken, and changing a Great or Poor Characteristic moves
  both scores, which the form shows before you save. This works for
  characters, familiars, creatures and laboratories, on the terminal
  and the desktop.
- **Boons and Hooks can name choices too.** A Boon or Hook may now ask
  for something when it is taken, such as a Form picked from a list, and
  Edit changes it later. The House Rules form has a new *Asks for* field,
  so your saga's own Virtues, Flaws, Boons and Hooks can ask for their
  own choices ("Vis Source ({form})" shows as "Vis Source (Aquam)").

## 2.99.1 — 2026-10-19

### Fundamenta

- **Tidier code, nothing new to see.** A code health pass: the longest
  functions and forms are broken into smaller parts, the questions each
  kind of season work answers are looked up in tables instead of long
  chains of checks, the workspace screen's actions are grouped by what
  they act on, the forms and sheets each live in their own folder, and
  three functions nothing used are gone. The app works exactly as it
  did.

## 2.99.0 — 2026-10-18

### Peregrinatio

- **The Theban pack.** New Saga and Import offer *The Sundered Eagle*:
  the Theban Tribunal of 1220 in the book's own words, with its thirteen
  covenants, each in its phyle and with its patron, and about sixty
  magi, polites and metoikos, with their tokens and shards. Its Council
  of Magistrates sits as the book has it (the archon Aiakia is Praeco).
  The Greek mainland, the islands and Delos, Constantinople and Anatolia
  come with their auras, vis, towns, lords and churches. There are the
  ruined covenants (Wilusa a regio of Ilion), the leagues, cults and
  hedge traditions, the Bestiary's creatures, the Peripheral Code and
  the cases for the Tribunal of 1221 on Delos, its history, and An Enemy
  Within with the other stories. Magi trained in the Tribunal learn
  their Art in Classical Greek; incomers keep Latin. The text is a
  paraphrase of the book, credited to it. Elysian Ecstasy and Olympian
  Pact join the Virtues.
- **Pack magi know their own Tribunal.** Generated magi in the Normandy
  and Provence packs had Rhine lore; their lore now names their own
  Tribunal.

## 2.98.1 — 2026-10-18

### Illuminatio

- **A saga opens quickly again on the desktop.** Opening a saga drew a
  card for every neighbour in The Region, and a Tribunal pack brings
  hundreds, so a saga started from a pack took many seconds to open, and
  as long again to come back to from a covenant. The Region and The
  Bestiary are now drawn the first time you open them, and each group of
  neighbours shows its first twelve cards with a **Show more** card that
  draws the rest. A saga started from the Normandy pack opens about ten
  times faster.

## 2.98.0 — 2026-10-18

### Peregrinatio

- **The Theban Tribunal in its own words.** The Theban customs now use
  The Sundered Eagle's terms. Each magus is a polites (citizen) or a
  metoikos (resident foreigner), and every magus present votes once, by
  voting sigil, so Your votes counts as for any other Tribunal; tokens
  are civic merit, not votes. A metoikos holds no tokens or shards.
  Liturgies are now Services (older saves are read the same way). Each
  covenant belongs to a phyle, Ionian, Aegean, Kretan or Propontian, set
  on the covenant's form or the roster, and shown in the roster's Phyle
  column. The tab is The Polity and its office list The Council of
  Magistrates.

### Concilium

- **The Theban meeting.** Holding a Theban Tribunal follows the book's
  phases. On the first day the Hermetic Assembly sets the principal
  phyle in turn and hears decrees of citizenship, contrition and
  defamation, then holds the ostrakismos: the shard-holders are read and
  the one chosen is ostracised for seven years. The Law Council and the
  People's Court are the meeting's motions and cases. On the last day
  the Council of Archai pays the outgoing magistrates their tokens (2
  for an arche, 3 for the archon, 5 for the polemarch), draws four new
  archai by lot from each phyle (one may be set aside for the next
  drawn), and elects the archon, who becomes Praeco, and the polemarch.
  Each step writes its minutes, and the new offices go into the Acta.

## 2.97.1 — 2026-10-18

### Concilium

- **A shorter Tribunal page.** A long In the Saga, such as the Normandy
  and Provence packs write, no longer pushes the covenants off the
  Roster: only its first paragraph shows under the Tribunal's name, and
  the rest opens the History tab, above the history.

## 2.97.0 — 2026-10-18

### Orbis

- **The Bestiary.** The saga now keeps its creatures: beasts, spirits,
  faeries, demons and angels, each with its stat block as the books
  print one. The Bestiary has its own place in the navigation, after The
  Region (on the desktop, a chapter of creature cards on the saga's
  page), and each creature has its own sheet: its Might and Realm,
  Characteristics (Cunning in place of Intelligence for an animal mind),
  Size, Age and Confidence, Virtues, Flaws and Qualities, Personality
  Traits, Reputations and Abilities; its natural weapons, Soak, Fatigue
  levels and Encumbrance, with its Wound Penalties worked out from its
  Size; its powers, each with its Might cost and its Penetration worked
  out as the Definitive Edition gives it (Might, less five per Might
  Point, plus its Penetration Ability); the vis in its body; and its
  appearance and notes. A demon also has its Order, Hierarchy and
  Weakness. A creature can be found at a place in the Region, and any
  neighbour can link to it. New Creature is in the New menu.

### Peregrinatio

- **Creatures in the packs.** The Rhine, Normandy and Provence packs
  bring every creature their books give a stat block, each at the place
  it haunts and linked to the threat or court it belongs to.

### Glossa

- **Help** has pages for the Bestiary and a creature's sheet, and a new
  how-to: How to add a creature from a book.

## 2.96.0 — 2026-10-17

### Illuminatio

- **Keys on the desktop.** The desktop version now answers the same
  page-wide keys as the terminal: `?` (or F1) opens Help on the page
  you're on, `Esc` cancels a form or question that's open (or, with none
  open, goes back a page, and from Help back to the page you came from),
  and `q` quits. While you're typing in a box, `?` and `q` just type, and
  they do nothing while a form is open, so they never act by accident.
  Help's Keys page lists them.

## 2.95.0 — 2026-10-16

### Peregrinatio

- **The Provence pack.** New Saga and Import offer *Faith & Flame*: the
  Provençal Tribunal of 1220, with its eleven covenants and their votes,
  about sixty magi (the Praeco Dama and Rebecca as the book prints
  them), Toulouse, Gascony, the Pyrenees, the Narbonnais and the Arelat
  with their auras, vis, towns, lords and churches, thirty ruined
  covenants and Val-Negra's regio, the Albigensian Crusade, its
  Peripheral Code and the cases for the Tribunal of 1221 at Glanum, its
  history, and the Praeco's secret as a story. The text is a paraphrase
  of the book, credited to it. The Virtues, Flaws and spells it names
  that the catalogs lacked are added.

### Insignia

- **Clean artwork.** Two of the app's drawings carried a hidden
  content-credential tag that a file sync had added; it is removed, and
  a check keeps any shipped file from carrying one.

## 2.94.1 — 2026-10-16

### Computus

- **A lab Servant adds its Safety.** The Servant Virtue now gives the
  laboratory Safety equal to half the servant's Intelligence, rounded up,
  as the book says. Adding it asks for the servant: one of the saga's
  grogs, whose Intelligence is then read from their sheet and follows any
  change to it, or, with no grog chosen, the servant's Intelligence typed
  in. Greater Guardian and Greater Horde likewise ask for the creature's
  Intelligence and add it to Safety. The Virtue's card and details say
  whose Intelligence it is, the desktop's Characteristic cards list what
  each Virtue and Flaw adds, and a warning appears when nothing has been
  entered or the servant has left the saga. The desktop's Virtues & Flaws
  chapter now shows the laboratory's warnings too.

## 2.94.0 — 2026-10-16

### Peregrinatio

- **The Normandy pack.** New Saga and Import offer *The Lion and the
  Lily*: the Normandy Tribunal of 1220, with its fifteen covenants and
  their magi, the places, towns, lords and churches of each region, the
  ruins of its fallen covenants, its Peripheral Code and open cases, its
  history, the vis held under the Perthean Compact, and the lines of
  fealty between covenants. The text is a paraphrase of the book,
  credited to it. The Rhine pack now also brings its wandering magi.

### Orbis

- **Vassals and oaths.** A covenant can be sworn as the vassal of
  another in its Tribunal, with the oath's duties written down and, if
  you like, the Boons and Hooks the oath brings to each side. The
  covenant's page shows "Vassal of" or its vassals.
- **Dormant stories.** A pack's threats can be brought in asleep: a tick
  per story on import or New Saga says which begin at once. A dormant
  story stays out of What's Ahead and the season's turn until you choose
  Begin This Story on its page, which sets its stages from next season.

### Concilium

- **Normandy's meetings.** A Normandy Tribunal meeting now settles the
  Praeco's succession (the eldest magus, unless set aside) and draws
  the next host by lot. Founding a covenant there reminds you of the
  vis its Code asks for.

### Insignia

- **New heraldry.** The eagle, fleur-de-lis, tower, cross, crescent,
  star and tree are now proper heraldic drawings from Wikimedia Commons,
  in any tincture, and there is a new charge: a lion with its tail
  knotted (queue-nowed).

## 2.93.0 — 2026-10-16

### Orbis

- **Ruined covenants.** A place can be marked a ruined covenant: it
  shows a broken tower instead of its usual picture, and "Ruin" in the
  lists. The Rhine's Rethra, Treverorum and Rudiaria's old site are
  marked.
- **Found a covenant on a ruin.** Found a Covenant Here (More in the
  terminal, Manage on the desktop) raises a new covenant on a ruin, as
  the Winter Ruins situation does: named for the ruin, sited there and
  taking its aura, with Winter Ruins's Boons and Hooks if you like. On a
  ruin with a regio you choose its site, the surface or a regio level,
  and the Regio Boon or Hook that goes with it.

## 2.92.0 — 2026-10-16

### Illuminatio

- **Spin boxes to match the drop-downs.** On the desktop the level
  filters are the same inked blank: their number in italic on a dotted
  line, solid purple while in use, with two small purple steps for the
  arrows, faint at the end of the range.

## 2.91.0 — 2026-10-16

### Insignia

- **New arms: ermine, a bend, bendy and checky.** Ermine joins the
  tinctures as a fur (argent with black tails), free of the rule of
  tincture. A shield can bear a bend across it, or be divided bendy or
  checky. They are available in every saga.
- **A proper lion.** The lion rampant is now drawn from a public-domain
  heraldic lion from Wikimedia Commons, in place of the old one that
  looked like a bear. It takes any tincture with black line work (silver
  on a black lion), and its claws and tongue are red (blue on a red lion
  or a red field).

## 2.90.0 — 2026-10-16

### Illuminatio

- **A gilt title page.** The name Armarius on the title page is drawn
  letter by letter with a gilt edge, as a record's initial is, and the
  page's frame is burnished gold; its buttons take the gold wash under
  the pointer.
- **Drop-downs as a blank in a manuscript.** On the desktop each
  drop-down shows its choice in italic on a dotted line, with a purple
  silk bookmark at its right; the line turns solid purple while it has
  focus. Its open list is a slip ruled in ink, a purple margin rule down
  its side, the chosen line washed in purple.

## 2.89.0 — 2026-10-16

### Illuminatio

- **Tables as a ruled ledger.** On the desktop, tables lose their boxes,
  fills and stripes: a small-caps serif heading over a gilt double rule,
  a hairline under each row, and the chosen row a gold wash that fades to
  the right, with a leaf in the margin. XP is an ink line ending in a
  lozenge. No selection anywhere turns the system's blue.
- **A gilt leaf and gilt rods.** The inspector is a leaf of paper in a
  burnished frame with flourishes in its corners, its text in the serif;
  every scroll bar is a gilt rod with a bead at each end.
- **Gilt initials.** A character's, covenant's or place's name opens with
  its first letter in rubric red, a gold edge catching the light along its
  left side.
- **Sounds.** A page turns for a chapter, a longer one for another record;
  a quill marks a saved form, coins a save in the Treasury, a chest the
  Inventory, a wax seal Advance Season, and a dull knock a refused entry.
  The speaker button in the top bar turns them off. Windows only; the
  sounds are CC0, credited in NOTICE.md.

## 2.88.1 — 2026-10-16

### Peregrinatio

- **Create a New Saga fits its window.** Start from a pack now names the
  Tribunal and what it brings ("Rhine Tribunal: 10 covenants, 74
  characters, 319 places and neighbours") instead of the pack's long
  title. On the desktop a long choice no longer stretches a form past its
  window, so forms never scroll sideways, and forms open a little wider.

### Insignia

- **The motto leads a coat of arms.** On the desktop the motto is set
  large above the blazon, which sits smaller beneath it, on a covenant's
  and a neighbour's Arms. The terminal's covenant and neighbour sheets and
  the Region's details now show the motto too, above the arms, and the
  arms form's preview puts it first.

## 2.88.0 — 2026-10-16

### Peregrinatio

- **Every Rhine magus statted.** The 61 magi Guardians of the Forests
  describes but prints no stat block for now have full sheets:
  Characteristics, Virtues and Flaws, Arts, Abilities, spells, aging and
  Warping, inferred from what the book says of each by the creation
  rules. They are not an official write-up, and each one's Biography
  says so; where the book gives no age, the one assumed is noted too.
- **Full stats or the book's sketches.** Importing a content pack asks
  "Generated stats for magi": untick it to bring those magi in as the
  book's sketches. The magi the book does print stat blocks for come in
  full either way.

### Orbis

- **The Region's filter on its heading's line.** On the desktop, the
  Show drop-downs sit at the right of the first list's heading instead of
  on a line of their own.
- **Open the threat that is due.** On the desktop, a small leaf beside
  the Region's Threat due opens that threat's page.

## 2.87.0 — 2026-10-15

### Concilium

- **A covenant's gilds on its own form.** In a Tribunal that follows the
  Rhine's customs, Edit Covenant, New Covenant and a sketch covenant's
  form each have a tick for every gild; ticking one makes the covenant a
  member, just as the Gilds tab does.
- **A Tribunal's history.** A Tribunal has a History of its own, written
  on its form and shown in a History chapter (a tab in the terminal), so
  In the Saga stays a short summary. The Rhine pack's eras of history
  have moved there.

### Orbis

- **The troupe's covenants stand out.** Every list of covenants puts the
  ones the troupe plays first, marked with ✦. The Tribunal's roster and
  the desktop's World page set the rest under an "Other covenants"
  divider, and the troupe's cards there have gold corners.
- **Filter the Region's neighbours.** The Region's lists can be narrowed
  to one region (everything inside it, however deep) and one kind, and
  each list's title says how many it shows of how many. On the desktop
  it is two quiet drop-downs under the facts; in the terminal, press `/`
  on any of the lists.

### Insignia

- **The Rhine's gild symbols.** Each of the six gilds bears its tree (an
  oak leaf, a thorn, an ash spearhead, an elder sprig, a linden leaf, an
  apple), cut like the Arts' woodblocks: small beside its name on the
  Gilds tab, large in the inspector.

## 2.86.3 — 2026-10-15

### Concilium

- **The Rhine's notice of cases.** Notice of a case is now due a season
  before a Rhine meeting, as under the core rules: Guardians of the
  Forests sets no other period, and the pack no longer lists a ruling
  saying otherwise.
- **The Rhine's gild dues.** The book sets no dues, so each gild in the
  Rhine pack now says: "None: a member owes the gild their vote and
  reasonable aid."

### Glossa

- **The docket explained.** The Cases help now says what each field of a
  case records, among them Sought: what the case asks the Tribunal to do
  if it succeeds. The case form gives Sought a hint too. The help also
  says where the Peripheral Code's Case column comes from, and which
  treasury entries a meeting adds by itself.

## 2.86.2 — 2026-10-15

### Fundamenta

Steadier tests. Screen tests that sometimes failed when the computer was busy now wait for a section to keep its focus, and for a form or confirmation to actually open, before they go on.

## 2.86.1 — 2026-10-15

### Fundamenta

Faster tests. The desktop tests now close the windows they open, so later
tests no longer slow down, and the full suite takes about half as long
(about 10 minutes instead of 21 on a 4-core machine). Work in progress now
runs a quick tier of tests after each step, and the full suite runs once
per story.

## 2.86.0 — 2026-10-15

### Peregrinatio

The first book pack: the Rhine Tribunal.

- **The Rhine pack.** Start from a pack (and Import, A Content Pack) now
  lists the packs that ship with the app first, and the first is
  Guardians of the Forests: the Rhine Tribunal as of spring 1220. It
  brings the Tribunal with its six gilds, Peripheral Code and open cases;
  ten covenants with 74 magi and others and their libraries; the forests,
  regions and regiones; the lords, towns, churches and factions of the
  mundane world with their arms; the Curse of the Rhine Gorge as a threat
  with its stages; and the Tribunal's history in its Diary. Secrets sit
  under a Secrets heading. Importing a pack puts its book in play.
  Help: a new guide, How to start a saga from a Tribunal book.
- **Full characters from the book.** Philippus Niger, Imanitos Mendax,
  Falke and Ioannes Acer, and six people of the Rhine Gorge story, come
  with their full stats.

### Insignia

- **Proxy sigils.** The pack's covenants carry the Rhine's proxies to
  the meeting of 1221: one for each master, two for each archmage, and
  the Tremere sigils their exarchs hold.

### Florilegium

- **Forest Lore.** A new Arcane Ability from Guardians of the Forests.

### Concilium

- **Fixed: the Tribunal's inspector.** On the desktop, choosing a ruling
  of the Peripheral Code, a Diary entry or a gild now shows it in the
  inspector, instead of leaving the last thing chosen there.

## 2.85.0 — 2026-10-15

### Peregrinatio

Groundwork for the book packs, one content pack per Tribunal book.

- **Choose what a pack imports.** Import, A Content Pack now asks what to
  bring in before the preview. The pack's Tribunals and covenants always
  come; five ticks, all on to begin with, cover their people, places and
  regiones, the mundane world, the Peripheral Code with its cases and
  fines, and the history. A part the pack holds nothing of isn't asked
  about, and a line under the ticks says what the pack brings as you
  change them. What a left-out part held is matched by name to the
  saga's own or its links are dropped, and the preview lists which.
  Starting a new saga from a pack still brings everything. Help: a new
  Import a Content Pack page.

### Insignia

- **More arms.** Four new charges: an eagle, a lion, a wheel and a
  fleur-de-lis. The Arms form asks How many of the charge (one, two side
  by side, or three as two and one, as heralds place them) and the
  blazon says so ("Gules, three crowns or"). Churches bear arms too, so a
  bishop's see can carry its own. A wheel keeps its spokes: a hole in a
  charge now cuts only the shapes drawn before it.

## 2.84.0 — 2026-10-15

### Peregrinatio

- Content packs: **Export Pack** in Saga Management writes chosen
  Tribunals, covenants, places and neighbours to one file, with their
  characters and calendar if you like. A Tribunal takes everything in it:
  its covenants, the places they sit in and whoever is there, and the
  neighbours that deal with them.
- Import, **A Content Pack**, previews what a pack adds, what the saga
  already has of the same name (kept, with the pack's links pointing to
  it) and what is skipped; importing the same pack twice adds nothing
  the second time.
- Create a New Saga can start from a pack in the exports folder.
- Importing a whole saga now brings its places, neighbours, calendar and
  Tribunals' records too, and an imported covenant keeps its place and
  links where the saga has them.

## 2.83.0 — 2026-10-15

### Concilium

- The desktop's Meeting tab opens on the Grand Hall: the Tribunal drawn
  as a hemicycle with a seat for every vote, each covenant's seats
  together under its pennant, every seat marked with its magus's House
  and coloured by the side its vote went. The debate's speakers stand at
  the centre and a pair of scales weighs the tally.
- **Call the Vote** calls the covenants one at a time, their seats filling
  as the Praeco calls each one.
- Opening a meeting on the desktop shows an opening card first: the year
  in Roman numerals, the Tribunal and where it meets, the arms of its
  covenants hung one by one, and the meeting's numbers.

## 2.82.0 — 2026-10-15

### Insignia

- **Arms.** A covenant, and a lord, town or faction, can bear arms: choose
  the field's tincture, how it is divided (plain, per pale, per fess, per
  bend, quarterly or per chevron) and its second tincture, a charge (a
  tower, a book, a key, a star, a sword, a crown, a cross, a crescent, a
  tree or a chalice) and its tincture, and a motto. The blazon is written
  for you as you choose ("Per bend azure and argent, a tower or"), and a
  charge that breaks the rule of tincture (a colour on a colour, a metal
  on a metal) is warned of but allowed.
- On the desktop the shield is painted in the Arms section of a
  covenant's Charter or Sketch and of a neighbour's Standing, and in the
  form as you choose; a covenant's Charter also shows the arms of the
  other covenants of its Tribunal. In the terminal, More's Arms draws the
  shield in half-blocks beside the blazon, and the blazon shows in the
  record's panel and in the Region.

## 2.81.0 — 2026-10-15

### Concilium

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

### Concilium

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

### Concilium

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

### Orbis

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

### Orbis

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

### Orbis

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

### Orbis

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

### Orbis

- Threats and their stages. A threat has an antagonist, a way of moving
  (by fixed dates, along a track, or by an omen count) and an ordered
  list of stages, each with when it comes, its clues, and what happens
  if it is ignored, stopped or turned. Its Stages tab shows the stage it
  has reached and the next to come, worked out from the saga's date (or
  its position on the track); a stage can be marked as happened, stopped
  or turned. The Region's top panel names the threat due soonest.

## 2.73.0 — 2026-10-15

### Orbis

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

### Orbis

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

### Orbis

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

### Concilium

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

### Concilium

- The Theban Tribunal's customs (The Sundered Eagle): a Tokens and Archai
  tab with each magus's tokens, shards and liturgies served and their
  standing (an office, or ostracised and until when), and the archai who
  hold its offices, with their terms and duties. Its Your votes counts the
  troupe's tokens. Holding a Theban meeting will add its elections.

## 2.68.0 — 2026-10-15

### Concilium

- A Tribunal follows the core rules or one region's customs, chosen as
  Customs in Edit Tribunal; a region's customs are offered while its
  sourcebook is in play, and are never mixed. The top panel names them.
- The Rhine's customs: its covenants' gilds, each with its members and
  dues, on a Gilds tab, and a Gild column on the roster. Notice of a case
  is due a year before a Rhine meeting, a season under the core rules.
- Switching a Tribunal's customs keeps what the old ones recorded,
  hidden; switching back shows it again.

## 2.67.0 — 2026-10-15

### Concilium

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

### Concilium

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

### Orbis

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

### Orbis

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

### Orbis

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

### Pagina

- A Reputation can now say its type (Hermetic, Local, Noble, Academic,
  Ecclesiastical or Infernal) and how far it reaches. Both show in
  brackets on its row.

## 2.62.1 — 2026-10-14

### Fundamenta

- Opening a saga that a newer version of Armarius saved no longer loses
  what this version doesn't know about. Whatever the newer version added
  is kept through every save and backup, even though you can't see or
  change it here, and the saga stays marked as the newer version's.
- Opening such a saga now says which version saved it and which one you
  are using, so you know to update the app.

## 2.62.0 — 2026-10-14

### Glossa

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

### Illuminatio

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

### Book of Hours

- Give: vis, books and lab texts, enchanted devices (with their
  epitome), personal gear and silver can be handed from one character,
  covenant or laboratory to another, and both sides' Diaries record it.
  Gear can be split by how many, and gear and silver never go to a
  laboratory. Characters now carry pounds of silver, and Give Silver
  gives from a character's purse or a covenant's Wealth.
- Set Up Research Library walks the covenant's research subjects one at
  a time, showing which books back each bonus and the bonuses so far.

### Illuminatio

- On the desktop, a magus's Sanctum button opens their laboratory (or
  makes one), and the laboratory's owner is a button back to them.
- Print to PDF, in every record's Manage chapter on the desktop, lays
  the sheet out on parchment-coloured A4.
- Every ability on the desktop has a drawn woodcut-style mark in its
  row, larger in the details panel. An ability with no mark of its own
  shows its category's.
- The desktop has no New or More buttons. Every action they held now
  sits on the section or page it acts on.
- Section buttons are quieter, sitting on the section title's line at
  the far right, flat with a soft shadow line. Every button in the app
  takes the same look, and a button with nothing to act on is hidden.
- The message after a step is drawn on the app's paper, with no system
  title bar.
- Windows Snap, Win+arrow keys and maximising work again with the
  desktop's own title bar.

### Pagina

- A character can have a portrait in a gilt frame beside their name.
  The picture you choose is copied into the saves folder, and the House
  symbol shows while there is none.
- The Treasury reads Annual Income and Annual Expense, and every Raw Vis
  and vis store shows its Art's symbol.

### Gauntlet

- The creation worksheet shows each stage's budgets as bars (gold, red
  when over), every stage's experience in each Ability and Art with its
  total and score, and a red line naming any broken creation rule.

### Fundamenta

- Export Saga writes the whole saga in one file, and Import reads it
  back as A Whole Saga.

## 2.59.0 — 2026-10-14

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

- The desktop window draws its own title bar on the paper, in place of
  the system's: minimise, maximise and close as small glyphs at the right
  of the top bar, and the app's name in the middle. Drag the bar to move
  the window and double-click it to maximise; drag an edge or corner to
  resize it. The title page has the same buttons.

## 2.54.0 — 2026-10-13

### Illuminatio

- On the desktop, the lists that were lines of fixed-width text are now
  real tables in the app's own fonts: Enchanted Devices, Research Goals,
  Personal Gear (a table for each kind), Books, Raw Vis, the Diary, the
  covenant's season lists, Lab Texts, a laboratory's Planning, the
  Creation Worksheet's lists and the Seasons records. Long names show in
  full, headings run across the table, and problems keep their colours.
- The Creation Worksheet's budget lines up its figures in a grid.

## 2.53.0 — 2026-10-13

### Illuminatio

- The app now opens on a title page: an illuminated initial A in gold
  and knotwork, the name Armarius and its tagline, and the version.
  From it you can open the saga you had open last, choose or begin
  another saga, or read Help. Enter takes the first of these.
- The terminal version opens on a matching title card in front of the
  saga picker. Players joining a hosted saga skip it.
- The app remembers the saga you opened last.

## 2.52.0 — 2026-10-13

### Fundamenta

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

### Illuminatio

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

## 2.45.0 — 2026-10-13

### Illuminatio

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

### Illuminatio

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

### Illuminatio

- Behind the scenes, preparing for the desktop version: the fifteen Arts
  and the Houses now have their symbols, traced from the artwork Atlas
  Games has released under its open licence (Guernicus shows the
  Quaesitor's), along with a set of everyday icons, the Order of Hermes
  sigil as the app icon, and the EB Garamond and Uncial Antiqua fonts.
  Help's About page credits them all. The terminal version doesn't show
  them, so nothing in the app itself changed.

## 2.43.4 — 2026-10-12

### Illuminatio

- Behind the scenes, preparing for the desktop version: the terminal
  screens now sit in a package of their own beside an empty one for the
  desktop window, and the desktop's libraries are an optional install
  (`uv sync --group gui`) so the terminal install stays as it is. The app
  starts and works exactly as before.

## 2.43.3 — 2026-10-12

### Illuminatio

- Behind the scenes, preparing for the desktop version: an automatic check
  now makes sure the shared rules, saga and form code never depends on the
  terminal screens, so a second front-end can use it unchanged. Nothing in
  the app itself changed.

## 2.43.2 — 2026-10-12

### Fundamenta

- The automatic checks run about a quarter faster (from about 32 to about
  24 minutes when run one at a time), with the same coverage: screen tests
  open only the sheet and tab they look at, the key-routing check notes
  which form a key opens without drawing it, and the list and sheet-text
  checks share one app session where they repeated it. Nothing in the app
  itself changed.

## 2.43.1 — 2026-10-12

### Illuminatio

- Behind the scenes, first step toward a desktop version: what each form
  asks for and how its entries are checked, and what can be done in each
  part of a sheet (add, edit, delete, and the More and New menus), now
  live outside the terminal screens, so a second front-end can share
  them. Nothing in the app looks or behaves differently.

## 2.43.0 — 2026-10-12

### Fundamenta

- You can choose where your sagas, backups, exports and settings are
  kept: More (`m`) on the saga picker has Change save folder. It checks
  the folder can be written to (some system settings, or a synced or
  read-only folder, may not allow it), offers to move your files there
  without overwriting anything, and remembers the choice. The saga
  picker always shows which folder it is reading and why.

### Computus

- Many more Virtues and Flaws now change the numbers they should:
  Student of (Realm) and the Faerie Blood heritages' Ability bonuses,
  Characteristic bonuses taken at creation, Soak and Protection, Wound
  and Fatigue penalties, aging rolls, Magic Resistance and Penetration,
  casting totals, and creation experience. The blood kinds from Realms
  of Power: Faerie are in the catalog, and spontaneous casting text names
  its Fatigue cost.

### Gauntlet

- On the covenant creation worksheet, each Lab Text and Casting Tablet
  has its own row under the Lab Texts pool, so you can edit (`e`) or
  delete (`d`) one there; the pool's levels and Build Points update.

## 2.42.0 — 2026-10-09

### Book of Hours

- Planning an Initiation now says what its Ordeal costs: the Initiate
  gains a Flaw, loses one of their Minor or Major Virtues, or has one of
  their Minor Flaws raised to a related Major Flaw. The Ordeal's size
  follows from that (a raised Flaw is a Medium Ordeal), so the separate
  Ordeal size choice is gone. A successful Initiation takes the lost
  Virtue away (with its point, for a Great Characteristic) or replaces
  the raised Flaw; a failed one changes nothing. Plans made before keep
  their Ordeal Flaw.

## 2.41.0 — 2026-10-09

### Florilegium

- The Spells tab lists only the spells whose book is in play, plus the
  saga's own. The Source filter's new "Not in play" choice shows the
  rest, and choosing a book shows its spells whether it is in play or
  not. A spell out of play, or hidden in this saga, is marked "(not in
  play)" there and in a character's Known Spells, and its details say
  why; a magus who knows it keeps it.

### Book of Hours

- Planning an Initiation: Virtue initiated and Ordeal Flaw open the
  Virtues & Flaws picker, which asks for anything the entry names (an
  Affinity's Art), and the Virtue is added with it. Picking the Flaw sets
  the Ordeal size, and a size that doesn't fit the Flaw is refused.
  Leaving the Mystagogue blank plans a self-initiation, which the form
  couldn't before. The Mystagogue must know the Lore, and the Initiate
  needs it at 1 unless it is their own House's.
- Undergo an Initiation is offered without The Mysteries in play: its
  rules are in the Definitive Edition.
- Fixed: only the latest Ordeal was remembered, so a smaller Ordeal after
  a bigger one lost the bigger one's help. Every Ordeal now counts down
  on its own, and an Initiation's Target takes the largest reduction.

### Scriptorum

- In any form, Delete clears a chosen value that may be left empty.

### Glossa

- A new how-to guide, How to initiate a character into a Mystery.

## 2.40.0 — 2026-10-09

### Florilegium

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

### Book of Hours

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

### Book of Hours

- A Casting Tablet's details show each magus of its covenant casting
  from it: Stamina + Technique + Form + Aura before the stress die, and
  what each die gives by the Definitive Edition's table, from one Fatigue
  level down to not casting it, with Warping Points and a Twilight check.
  Reading a tablet needs Artes Liberales 1 and Latin 4.
- Write Casting Tablets, a magus's season: tablets of a spell they have
  mastered, as many as Latin x 20 levels holds. Copy Lab Texts copies
  Casting Tablets too.

## 2.37.0 — 2026-10-09

### Book of Hours

- Library research shows its roll: Intelligence + the Ability + the
  better of the covenant library's research bonus for it and its best
  encyclopedia's, against the storyguide's Ease Factor.
- "Read a commentary, florilegium or glossed book" is no longer offered:
  Read a book adds those bonuses itself. An older plan using it says to
  plan Read a book instead.

## 2.36.0 — 2026-10-08

### Book of Hours

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

### Book of Hours

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

### Book of Hours

- Fixed: on a shorter screen (120x45) a covenant's Library tab had room
  for one book row, or none once a book was chosen. Book rows no longer
  wrap onto a second line (a long one is cut short), the Library Summary
  takes four rows instead of seven, and the details panel gives up rows,
  its text scrolling, so the book list always keeps five.

## 2.34.2 — 2026-10-08

### Fundamenta

- Behind the scenes: the data model is split into one module per kind of
  record (characters, covenants, laboratories, books and so on) instead of
  one very long file. Nothing about saving or loading a saga changes.
- Behind the scenes: importing a covenant, laboratory or character, and
  the book form, are each built from smaller pieces. Both work exactly as
  before.

## 2.34.1 — 2026-10-08

### Fundamenta

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

### Gauntlet

- On a new covenant's Resources step, a can buy one of the saga's own
  books (Unassigned Books, such as an imported book list): the picker
  lists only those a new covenant may buy, with their Build Points, and
  F3 shows the rest marked with why. The covenant gets its own copy; the
  saga's book stays where it is.

## 2.33.0 — 2026-10-08

### Gauntlet

- An Illusory Resources Hook's 250 Build Points can be tracked in play,
  the same way as Hidden Resources: a Diary Story Event linked to one has
  a Build Points found illusory field, counted once the event is
  Resolved and never past the Hook's 250. The Hook's row shows how much
  has been found out ("60/250 BP"), its details list the Story Events
  that revealed it, and the Build tab shows the pool, what's found
  illusory and what's still believed real, apart from its totals.

## 2.32.0 — 2026-10-08

### Gauntlet

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

### Book of Hours

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

### Book of Hours

- Fixed: the delete confirmation and the duplicate-book question during an
  import are drawn in a framed box again, like every other dialog, instead
  of as bare text over the dimmed screen.

## 2.30.0 — 2026-10-07

### Florilegium

- The ability catalog gains the supplement abilities the ArM5 books index
  uses: the Divine's Adjuration, Blessing, Holy Music, Kabbalah and
  Merkavah, Mechanica of Heron, Mythic Herbalism and Theology: Pagan. Each
  is offered only while its book is in play.
- A new Hedge Art category holds a hedge tradition's Arts: Elementalist
  Air, Earth, Fire and Water, and Medicinal Divining. Like a Supernatural
  Ability, one is bought at creation through the Virtue that grants it.

## 2.29.0 — 2026-10-07

### Book of Hours

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

### Book of Hours

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

### Gauntlet

- The covenant worksheet's Review step says how many grogs and other
  covenfolk the creation baseline gives for free (about one grog and two
  others per magus), to add on the Inhabitants tab once the covenant is
  In Play.

## 2.26.0 — 2026-10-07

### Gauntlet

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

### Gauntlet

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

### Gauntlet

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

### Gauntlet

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

### Pagina

- The live score while editing XP now shows the total the next score
  needs, like the XP field beside it, rather than the xp still to gain:
  "Latin: Score 2 · Score 3 at 30 xp", with the Ability's name first.
  Edit Arts shows it in Score and Next at columns. The Affinity note
  is gone from these forms, which hold totals.

## 2.22.0 — 2026-10-07

### Pagina

- Editing an Ability's or Art's XP shows, as you type, the score it buys
  and the xp still needed for the next, e.g. "Score 3 (5) · 13 xp to
  next". This replaces the table of scores under the Ability's XP, and
  works when adding an Ability, for a familiar's Abilities and beside
  every Art in Edit Arts. A fixed bonus such as Puissant shows the score
  used in brackets; with an Affinity it also says how much xp gained
  before the Affinity's half again reaches the next score ("9 with
  Affinity").

## 2.21.0 — 2026-10-07

### Pagina

- A familiar can be removed on its own: press `d` on it in the tree or
  on its Familiar Info panel. The confirmation says what goes with it:
  the bond is broken, the magus loses the True Friend Virtue and Loyal
  (Partner) Trait the bond gave them, and any planned seasons of binding
  or empowering it are deleted. The magus's sheet is shown afterwards.

## 2.20.0 — 2026-10-07

### Florilegium

- The Boons and Hooks, Laboratory Virtues and Flaws, and Abilities
  pickers now show the highlighted entry's details under the list, as
  the spell picker does: its rules text, tier and points, what it
  requires or rules out, its effects and the book it comes from.
- Pickers name an entry's books in full ("Ars Magica Definitive
  Edition; Covenants"), core book first.

## 2.19.3 — 2026-10-07

### Fundamenta

- Behind the scenes: the Plan Season form and the Invent Spell screen are
  now built from short named parts instead of two very long functions,
  and a code check now stops new over-long functions from creeping in.
  Nothing you see changes.

## 2.19.2 — 2026-10-07

### Fundamenta

- Behind the scenes: the app's screen tests, which were all in one very
  long file, are now in one file per area, with the helpers they share
  in a file of their own. Nothing you see changes.

## 2.19.1 — 2026-10-07

### Fundamenta

- Behind the scenes: the code that plans and advances the seasons, which
  was all in one very long file, is now organised into one file per part
  (plans, what a season does to a character, the covenant, lab work and
  advancing). Nothing you see changes.

## 2.19.0 — 2026-10-07

### Florilegium

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

### Fundamenta

- Behind the scenes: the app's forms, which were all in one very long
  file, are now organised into one file per area (characters, covenants,
  laboratories, books, spells, seasons, enchanted devices and so on).
  Nothing you see changes.

## 2.18.2 — 2026-10-06

### Computus

- Great (Characteristic) now raises the Characteristic it names by 1, and
  can only be taken when that Characteristic is at +3 (or +4, for the
  second copy, which takes it to +5). The Virtue picker offers only the
  Characteristics that qualify. Removing it takes the point off again.
  Poor (Characteristic) works the same way from -3.

## 2.18.1 — 2026-10-06

### Fundamenta

- Tidier code notes: the program's comments now state each rule plainly,
  without internal ticket numbers, and the rules note on covenant
  finances no longer shows one either. The README now describes what
  the app does today: the rules, seasons, creation and hosting a saga.

## 2.18.0 — 2026-10-06

### Sodales

- Players can also reach a hosted saga over SSH: start hosting with
  `--ssh-port 2222` and they connect with `ssh -p 2222 player@ADDRESS`
  from Windows Terminal, macOS or Linux, to the same saga list and
  sign-in as in a browser. No accounts on your computer are involved.
  Export isn't offered over SSH, since the file could only land on the
  host. Help's hosting guide says how.
- Sodales (2.12.0 to 2.18.0) is the troupe release: the storyguide hosts
  the saga and players sign in from their own computers.

### Scriptorum

- Every form now opens with its first field ready to type into. Before,
  the first letters typed went nowhere until you pressed Tab or clicked
  a field.

## 2.17.1 — 2026-10-06

### Glossa

- Help gains "How to host a saga for your troupe": what to set up, how
  to start and stop hosting, Tailscale and ZeroTier recipes, and what
  players see. A character's Biographical Detail now shows who it is
  Played by when the saga has players.

## 2.17.0 — 2026-10-06

### Sodales

- When several people have a hosted saga open, each one sees the others'
  changes within a couple of seconds: the sheet on show updates where it
  is, with a note such as "Ana changed Corvinus; reloaded". If two people
  open the same character, both are told. A saga with no players works
  exactly as before.

## 2.16.0 — 2026-10-06

### Sodales

- Players signed in to a hosted saga now change only what is theirs: the
  characters they play, with those characters' familiars, laboratories
  and books. Choose who plays a character with **Played by** in its
  Biographical Detail, and tick **May change covenants** on a player to
  let them change the covenants too. Making new records, the season and
  date, importing, moving vis and sharing spells stay with the storyguide.
  Elsewhere a player can look and Export, and in a browser an export
  downloads to their own computer.

## 2.15.0 — 2026-10-06

### Sodales

- When the saga is hosted and several people have it open, saving no
  longer wipes out what the others saved meanwhile: each save keeps
  everyone else's changes and writes only its own, down to the single
  field. If two people change the same thing, the later save wins.

## 2.14.0 — 2026-10-06

### Sodales

- Players who open a hosted saga in a browser now sign in first, with
  their name and a passcode. You add them on the saga's new **Players**
  node (only the storyguide sees it), each as a Player or a Storyguide.
  Passcodes are kept only scrambled. In a browser the saga list no longer
  offers New or Delete Saga, and the header shows who is signed in.
  For now everyone signed in can still change everything.

## 2.13.0 — 2026-10-06

### Glossa

- Help has a What's New page, under REFERENCE after About this App: every
  version's changes, newest first. It shows its start at once and fills
  in the rest as you read.
- The big releases now have names, after the books and crafts of a
  medieval scriptorium and a Hermetic covenant (Incipit, Florilegium,
  Codex, Computus, Book of Hours, Gauntlet and more): each named
  version's heading carries its name, and a Release names table near the
  top of What's New says what each one brought.

## 2.12.1 — 2026-10-06

### Computus

- Fixes an experiment's Extraordinary Result of 11 (a modified effect):
  one die is now rolled for the whole Modified Effect table, as the book
  says, instead of a new die for each row checked, which skewed the odds
  of each kind of change.

## 2.12.0 — 2026-10-06

### Sodales

- First step towards players and the storyguide sharing a saga: the app
  can now be opened in a web browser from another computer, with
  `uv run python tools/serve.py --host <address>`. Each browser tab gets
  its own copy of the app. This is an early test: there is no sign-in
  yet, so only use it on a private network (your home network,
  Tailscale or ZeroTier), and two people editing at once can still
  overwrite each other's changes.

## 2.11.3 — 2026-10-05

### Gauntlet

- Fixes a covenant's starting laboratories taking 50 Build Points off for
  every magus whose laboratory wasn't entered (Dammerstein's Build tab
  showed -200 for Laboratories). Every magus has a free standard
  laboratory whether or not it is entered; only the magi you say go
  without one refund 50, set on the Power Level step as **Magi without a
  laboratory**. To recount a covenant already in play, move it back to
  In Creation and then to In Play again.

## 2.11.2 — 2026-10-05

### Fundamenta

Behind the scenes: the rules for each kind of seasonal activity are now
grouped into one place per family, the order in which a season's end is
played out is tested on its own, and more of the season rules are covered
by tests. Nothing changes in what the app shows or does.

## 2.11.1 — 2026-10-05

### Fundamenta

- Fixes 2.11.0 failing to start when Windows' Controlled folder access
  (ransomware protection) blocks writing to Documents. Your data now lives
  in **Ars Magica Manager** at the top of your OneDrive folder (or the app
  data folder without OneDrive). If the app can't write there, it keeps
  using wherever your saves already are and says why, instead of stopping.
- Behind the scenes: the covenant sheet now updates its tabs the same way
  the other sheets do, and the automatic GitHub checks run only on request.

## 2.11.0 — 2026-10-05

### Fundamenta

Your data now has a home of its own: sagas, their backups, exports and the
app's settings are kept in **Ars Magica Manager** in your Documents folder
(found wherever Windows keeps it, OneDrive included), where they are easy to
find and back up. The first time this version starts it moves your existing
saves there from the app's own folder, never overwriting anything, and says
what it moved. Another folder can be chosen (see the README). The project
also gained its package details and automatic checks on GitHub for every
change pushed.

## 2.10.2 — 2026-10-05

### Computus

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

### Fundamenta

Safer saving. A saga, the settings and an export are now written in full
before they replace the old file, so a crash or a full disk mid-save can no
longer leave a half-written saga. The app now keeps the last five backups
of a saga (taken before each season with plans is applied) instead of only
one. A damaged settings file no longer stops the app starting, and a saga
saved by an older version with a since-removed field in any record now
opens instead of failing.

## 2.10.0 — 2026-10-05

### Glossa

How-to guides in Help: eight step-by-step walk-throughs, listed under
HOW-TO GUIDES when you press ?: planning and running a season, managing
the covenant, how advancement works, lab planning, getting started,
creating characters, covenants and laboratories, familiars, and
importing and exporting. The help pages they cover link to them.

Two out-of-date hints are fixed: the Advance Time dialog now says Set
Date is in More on the saga, and the Export dialog says to import with
More's Import.

## 2.9.0 — 2026-10-05

### Scriptorum

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

## 2.8.0 — 2026-10-04

### Glossa

Help: press ? anywhere (F1 while typing in a dialog) for help on the part of
the screen you're in: the section, its tab and the sheet, with the keys that
work there. Every sheet, tab and section has a page saying what it's for and
what you type versus what the app works out, and the processes (planning and
advancing a season, inventing a spell, the Creation Worksheet, importing) have
their own. Topics can be filtered with /. About this App now lives in Help.

## 2.7.1 — 2026-10-04

### Pagina

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

### Scriptorum

The details panel at the bottom of a sheet's tab fits what it shows.

- It is as tall as its text, from 3 rows up to 12; longer text still
  scrolls inside it. With nothing chosen it shrinks to 3 rows, and the
  list above it gets the rows it gives back.
- Three laboratory hints are shorter so they fit on one line: Attributes,
  Inventory and Planning.

## 2.6.0 — 2026-10-03

### Gauntlet

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

## 2.5.0 — 2026-10-01

### Scriptorum

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

## 2.4.0 — 2026-10-01

### Gauntlet

Lab Texts, House Rules, and moving records between sagas.

- A laboratory's Inventory tab has a Lab Texts list of its own, apart from
  its other Books: each text's kind (Spell, Enchantment, Longevity Ritual
  or Other), Arts, level, author and Sigil, whether the laboratory's owner
  can read it, and what a copy costs a scribe. `F` filters it by kind,
  Art, level and readable only.

### Book of Hours

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

### Florilegium

- House Rules: a new node under the saga keeps the saga's own Virtues,
  Flaws, Boons and Hooks (name, type, tier, category, description). Every
  picker offers them alongside the catalog's. They are text only: no
  effects are applied.

### Fundamenta

- `x` on a covenant, laboratory or character exports it to a file with
  what travels with it (a character's familiar, devices, books and Diary;
  a laboratory's books; optionally a covenant's laboratories and
  characters). `I` on a saga imports one: Characters, Covenants and
  Laboratories now work in the Import list. A preview shows what is added
  and which links are kept or dropped before anything changes.

## 2.3.0 — 2026-10-01

### Book of Hours

Moving raw vis, paying from the covenant's vis, and live Characteristic
points.

- Raw vis can be moved: `m` (Move Vis) on a magus's Raw Vis, a laboratory's
  Raw Vis or a covenant's Raw Vis Stores asks how many pawns and who gets
  them: any other covenant, laboratory or magus in the saga. A covenant
  takes it into its store of that Art (a new one if it has none), and both
  sides' Diaries record the move.
- Season work can pay from the covenant's vis: "Vis from" on vis study and
  on every lab activity has a third choice, the covenant's vis stores.
  Spending takes from the stores of that Art in list order, vis extracted
  that way goes into the covenant's store, and the covenant's Diary
  records each change.

### Pagina

- A covenant's Raw Vis Store says where it is kept: the covenant, one of
  its laboratories or one of its characters. Location text in older saves
  that names a laboratory or character becomes that link; anything else is
  kept at the covenant, with the text left in Location as a note on where
  exactly.

### Gauntlet

- While a character is In Creation, the Edit Characteristics form shows the
  points spent and left, and each score's cost, as each number is typed:
  red when over the budget, green when it is spent exactly.

## 2.2.0 — 2026-10-01

### Gauntlet

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

### Pagina

- A magus can make an invented spell available to the whole saga: `s`
  (Share Spell) on Known Spells moves it to the saga's Spells, after
  asking. The magus still knows it and its Lab Texts still link to it.

## 2.1.0 — 2026-10-01

### Gauntlet

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

## 2.0.0 — 2026-10-01

### Gauntlet

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

### Florilegium

- The Grogs book is now in the list of sourcebooks.

## 1.9.2 — 2026-09-30

### Pagina

A fix to the covenant's Economics tab.

- Deleting the chosen source of income no longer leaves the next source
  chosen in its place, so pressing Delete again can't remove a second
  source by mistake. Like every other list, nothing is chosen after a
  delete; editing something elsewhere on the tab still keeps your choice.

## 1.9.1 — 2026-09-30

### Fundamenta

The performance plan is saved with the project. Nothing in the app changes.

- PERFORMANCE_PLAN.md records where the app spends its time (the screen,
  not the save file), why a database isn't needed at this size, and the
  fixes planned from it.

## 1.9.0 — 2026-09-30

### Pagina

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

### Computus

- Botch dice count the Virtues and Flaws that change them for spellcasting
  and experimenting: Cautious Sorcerer, Careless Sorcerer, Weird Magic,
  Afflicted Tongue, Deaf and Palsied Hands.

### Fundamenta

- A test that failed now and then under load is steady.

## 1.8.0 — 2026-09-30

### Book of Hours

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

### Fundamenta

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

### Fundamenta

A leaner test suite, first part. Nothing in the app changes.

- Removed UI tests that only repeated what the shared form, list, sheet and
  key checks already cover, and ran the shared trait-list checks on fewer
  of the lists that share one handler.
- A few rules that were only checked through the screens (the Boons & Hooks
  titles and details panel, which Abilities the picker offers, the Known
  Spells rows) are now plain functions with fast tests of their own.

## 1.7.0 — 2026-09-30

### Book of Hours

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

## 1.6.0 — 2026-09-29

### Book of Hours

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

### Fundamenta

- Behind the scenes: the code now passes its type check with no errors,
  and that is the standard from here on. Nothing changes in the app.

## 1.5.0 — 2026-09-29

### Book of Hours

- After a season with plans is played out (t), a summary shows what each
  person did and what it gave, by covenant, and who had nothing planned.
- A new Seasons entry in the tree lists past seasons, newest first; choose
  one to read its record again.
- Edit Saga has "Keep season records" (on by default). Off, the summary
  still shows after each season, but it isn't saved; the characters'
  Diaries keep their entries either way.

## 1.4.0 — 2026-09-29

### Book of Hours

- Each covenant has a new Seasons tab, after Inhabitants: its magi,
  companions and grogs, each with what they have planned for the season
  (or "nothing planned"), and a count of who has planned in each list.
  Choose someone to see their plan and what it will give; e plans their
  season and A clears it.

## 1.3.0 — 2026-09-29

### Book of Hours

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

### Fundamenta

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

### Fundamenta

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

### Computus

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

### Computus

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

### Pagina

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

### Pagina

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
- True Faith: the character sheet shows a True Faith Score and Faith
  Points for a character with the True Faith Virtue (or any points), and
  the Edit form warns if a Score doesn't fit the rules.
- New Covenant, New Character, New Laboratory and Bind Familiar are offered
  only on the saga and next to their own kind of record, so a sheet's key
  bar shows what belongs there.

### Florilegium

- Choose which sourcebooks are in play for each saga, from Edit Saga. The
  core book is always in play and every book is by default. Catalog pickers
  hide entries from books not in play; F3 shows them anyway.
- The laboratory Virtue/Flaw catalog now has all 128 entries from
  Covenants (it had 53).
- Corrected two House descriptions (Bonisagus, Tytalus) and the chapter
  the laboratory Virtues and Flaws are cited from.

## 0.11.1 — 2026-09-28

### Scriptorum

- Add and edit dialogs are now checked to fit a 120x45 terminal (the
  smallest size the app is checked at) rather than 80x24, which is no
  longer a target. Nothing you see in the app changes.

## 0.11.0 — 2026-09-28

### Florilegium

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

### Florilegium

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

### Scriptorum

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

### Florilegium

- Unknown Hooks: a Minor Hook the book says "may be Unknown" (35 of them)
  can be marked Unknown in its add or Edit form. It then counts 3 points in
  the Hooks total, as a Major Hook, and says so in its row ("Favors
  (Unknown, 3 pts)") and details panel. The picker notes which Hooks may be
  Unknown.

### Fundamenta

- Ars Magica Manager is now licensed under the GNU GPL v3 (LICENSE). The
  Ars Magica rules text in its catalogs is credited to Atlas Games under
  CC BY-SA 4.0: every catalog carries the attribution line, and NOTICE.md
  lists the sources, changes made and trademark notices.

### Glossa

- The saga picker has an About dialog (`?`) showing the version and the
  licences and credits.

## 0.7.0 — 2026-09-27

### Florilegium

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

### Florilegium

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

### Pagina

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

### Scriptorum

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

### Scriptorum

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

### Scriptorum

- A saved choice that a list no longer offers is kept when you save a form
  without touching it, instead of being cleared: a House missing from the
  House list shows as "… (not in the list)", and a laboratory owner who is no
  longer a magus shows by name.
- Multi-line fields (Biography, descriptions) keep an indented first line,
  such as a Markdown list; only trailing spaces and blank lines are dropped.

### Fundamenta

- Behind the scenes: the standard form's code is simpler and better checked,
  and the tests are sturdier.

## 0.2.0 — 2026-09-27

### Fundamenta

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

## 0.1.0 — 2026-09-17

### Pagina

Everything before versioning began, from the first sheets on 17 September 2026.
