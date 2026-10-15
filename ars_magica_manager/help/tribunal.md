# Tribunal sheet
<!-- help: tribunal -->

A Tribunal is the council of the magi of a region, meeting every seven
years (Ars Magica Definitive Edition, Chapter 2: The Order of Hermes).
Its sheet holds what belongs to the Tribunal itself: its name, how often
and where it next meets, its Praeco and Presiding Quaesitor, and how big
it really is. Everything else is worked out from the covenants that
belong to it.

A Tribunal follows either the core rules or one region's customs, from
that region's sourcebook, never a mix: choose them as **Customs** in Edit
Tribunal (a region's customs are offered while its book is in play).
The customs can add lists of their own to the sheet, a column to the
roster, and change when notice of a case is due. Switching customs keeps
what the old ones recorded, hidden, and switching back shows it again.

- **Core rules**: the Definitive Edition's Tribunal; notice of a case is
  due a season before the meeting.
- **Rhine: Gilds** (Guardians of the Forests): the Rhine's covenants band
  together in gilds, each with its dues; the sheet gains a Gilds list and
  the roster a Gild column. Notice is due a season before the meeting,
  as under the core rules.
  The book's Tribunal of 1220 ships as a content pack: see [How to start a
  saga from a Tribunal book](help:guide-book-packs).
- **Theban: Tokens** (The Sundered Eagle): its magi vote with
  tokens and ostracise with shards, and it elects its archai at each
  meeting; the sheet gains a Tokens and Archai tab, and Your votes counts
  the troupe's tokens.
- **Normandy: Vis tenure** (The Lion and the Lily): every vis source is
  held on a tenure of the Perthean Compact, and the covenants' teams
  contest the Hermetic Tourney after each meeting; the sheet gains Tenure
  and Tourney tabs.
- **Transylvania: Privileges** (Against the Dark): each covenant holds
  one of five privilege classes; the roster gains a Class column, entered
  with the roster's Edit beside its proxies.
- **Provence: Open founding** (Faith & Flame): any magus may found a
  covenant without the Tribunal's leave. A rule, not a list: it shows as
  a note on the Peripheral Code tab.
- **Hibernia: Notes** (The Contested Isle): the core rules, with its
  customs noted on the Peripheral Code tab.

Older sagas typed a covenant's Tribunal as a name. Each name became a
Tribunal of its own when the saga was first opened by this version, and
covenants that typed the same name share it.

<!-- tui -->
Add a Tribunal with **New Tribunal** in New (`n`). To delete one, press
`d` on its tree node or its top panel: its covenants belong to no
Tribunal afterwards, and nothing else about them changes.
<!-- /tui -->
<!-- gui -->
Add a Tribunal with the **New Tribunal** card under Tribunals in the
saga's World chapter. To delete one, use **Delete** in its page's
**Manage** chapter: its covenants belong to no Tribunal afterwards, and
nothing else about them changes.
<!-- /gui -->

**See also:** [Covenant sheet](help:covenant), [Sketch covenants](help:tab-cov-overview)

## The Tribunal
<!-- help: section-trib-info -->

The facts under the Tribunal's name:

- **Customs**: the core rules, or the region's customs it follows.
- **Meets every**: how many years between its meetings (seven, unless
  its customs say otherwise).
- **Next meeting** and **Meeting place**: when and where it next meets.
- **Praeco** and **Presiding Quaesitor**: chosen from the saga's
  characters, at any detail.
- **Covenants** and **Magi**: how many are recorded here, and of how many
  in all when you have said (most are never written down).
- **Your votes**: the troupe's covenants' votes, proxies included, of
  every vote in the hall.
- **Cases**: how many are on the docket, and how many are against the
  troupe's covenants or their magi.

<!-- tui -->
Press `e` (or Edit) to change them, and to write what the Tribunal is
like in the saga.
<!-- /tui -->
<!-- gui -->
**Edit Tribunal** changes them, and what the Tribunal is like in the saga.
<!-- /gui -->

## Roster tab
<!-- help: tab-trib-roster -->

Every covenant that belongs to the Tribunal, the troupe's first, and the
magi worth keeping an eye on.

### Covenants
<!-- help: section-trib-roster -->

Each covenant of the Tribunal: how much of it is written down, its magi
(named or not), its votes at the next meeting and the proxies it holds,
and its attitude toward the troupe's covenant. The troupe's covenants
come first, marked ✦, above an "Other covenants" line. When the Tribunal's size
says there are more covenants than are recorded, a last row counts them
and the magi they hold.

A covenant has one vote for each of its magi, and one for each proxy it
carries: the sigil of an absent magus, given for one meeting. Proxies
change at every meeting, so they are kept here rather than on the
covenant.

<!-- tui -->
Press `e` on a covenant to set the proxies it holds. Choose a covenant's
Tribunal in its Edit Covenant to add it here.
<!-- /tui -->
<!-- gui -->
Choose a covenant to read about it beside the list, and **Edit** to set
the proxies it holds. Choose a covenant's Tribunal in its Edit Covenant
to add it here.
<!-- /gui -->

### Magi of Note
<!-- help: section-trib-magi -->

The Tribunal's Praeco and Presiding Quaesitor, the magi of its covenants
the troupe doesn't play, and anyone prosecuting or defending a case on
its docket, with their House, covenant and part in the Tribunal. Edit a
magus on their covenant's sheet or their own.

## History tab
<!-- help: tab-trib-history -->

How the Tribunal came to be, era by era, kept apart from In the Saga
(what it is like now) so that stays short. Write it in the History field
of the Tribunal's own form; a Tribunal book fills it in.

## Docket tab
<!-- help: tab-trib-docket -->

The cases the Tribunal will hear at its next meeting, and those heard or
withdrawn before.

### Cases
<!-- help: section-trib-cases -->

Each charge, motion or appeal for the next meeting: when it was filed,
when notice of it is due, and what is sought. Under the core rules,
notice is due a season before the meeting; a case whose notice hasn't
been given is flagged, and a case against one of the troupe's covenants
or magi is drawn in red.

What a case records:

- **Case**: its name, as the docket lists it.
- **Kind**: a *charge* accuses someone of breaking the Code; a *motion*
  asks the Tribunal to decide or declare something (a new ruling, a
  boundary, recognising a covenant); an *appeal* asks it to reverse an
  earlier ruling.
- **Brought by** and **Against**: who brings it and who it is against,
  as names. A covenant or magus of the troupe's named in Against is
  flagged.
- **Charge**: what is alleged or proposed, in a sentence or two.
- **Filed**: the year and season it was filed.
- **Notice given**: whether the parties have been told of it in time.
  Notice is due a season before the meeting; the Notice due column says
  when.
- **Sought**: what the one bringing it asks the Tribunal to do if it
  succeeds: the penalty for a charge (a fine of vis or silver, the loss
  of a right, a Wizard's March) or the ruling a motion or appeal wants.
  Leave it empty while nobody has said.
- **Evidence**: what each side can show, one piece a line.
- **Prosecutor** and **Defender**: who speaks for each side at the
  meeting.
- **Status** and **Outcome** (when editing): open, decided or withdrawn,
  and what was decided. A decided or withdrawn case moves to the Rulings
  of Past Tribunals.

<!-- tui -->
`a` adds a case, `e` edits the chosen one and `d` deletes it. More (`m`)
offers **Withdraw**, which takes it off the docket and keeps it among
the past rulings. Choose a case to read all of it under the lists.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** change the cases; **Withdraw** takes
the chosen one off the docket and keeps it among the past rulings.
Choose a case to read all of it beside the list.
<!-- /gui -->

### Rulings of Past Tribunals
<!-- help: section-trib-past -->

The cases past meetings decided, with their outcome, and those
withdrawn. Edit one to correct it, or set its Status back to open to
return it to the docket.

## Meeting tab
<!-- help: tab-trib-meeting -->

Holding the Tribunal: the meeting being held, or (before it opens) the
order of business the next one would hold. Each step is saved as it
is held, so you can leave the meeting at any point and come back to it
later at the step in hand. See [Hold Tribunal](help:hold-tribunal).

<!-- gui -->
At the top of the tab is **The Hall**: the meeting drawn as a
hemicycle, one seat for each vote, the seats of a covenant together
under its pennant (its arms, if it bears any). Each seat shows its
magus's House and is coloured by the side its vote went on the case in
hand, with the magi who spoke in the debate at the centre and a pair of
scales weighing the tally. **Call the Vote** calls the covenants one by
one in the order of the roll, filling their seats as the Praeco calls
them. When **Hold** opens a meeting, a card announces it: the year,
the Tribunal and where it meets, the arms of its covenants, and its
numbers; a key or a click enters the hall.
<!-- /gui -->

### Order of Business
<!-- help: section-meeting-business -->

The meeting's steps, day by day: the Opening and Attendance on the
first day, each case and motion on the day the Opening set for it, and
the rulings, the treasury and the Closing on the last. A step held is
marked ✓, and the step in hand ▶.

<!-- tui -->
`e` holds the chosen step (again, if it was held already); before the
meeting opens, it opens it. `d` abandons the meeting, keeping whatever
its steps changed. Choose a step to read what was entered at it under
the lists.
<!-- /tui -->
<!-- gui -->
**Hold** holds the chosen step (again, if it was held already); before
the meeting opens, it opens it. **Abandon** gives up the meeting,
keeping whatever its steps changed. Choose a step to read what was
entered at it beside the list.
<!-- /gui -->

### The Vote
<!-- help: section-meeting-vote -->

The vote on the case in hand (or the last voted on): each covenant as
the Praeco calls it, in the order of the roll, with its votes for,
against and undecided, and how many of them the debate swayed; then the
tally, with a bar for the hall.

Each covenant starts from its leaning: a party votes its own side, and
any other leans by its attitude toward a troupe covenant that is a
party (Warm or better with it, Wary or worse against it), otherwise
undecided. The winner of the debate then wins a share of the undecided
votes, and from a Triumphant Victory a share of the other side's, taken
from the first covenants called. See [Hold Tribunal](help:hold-tribunal).

<!-- tui -->
`e` holds the vote, where you can change each covenant's leaning.
<!-- /tui -->
<!-- gui -->
**Edit** holds the vote, where you can change each covenant's leaning.
<!-- /gui -->

### Attendance
<!-- help: section-meeting-attendance -->

Each covenant's magi, how many are absent, the proxies it carries and
its votes in the hall: its magi present, and its proxies if the
Presiding Quaesitor allowed them. Proxies set aside are shown but not
counted.

<!-- tui -->
`e` holds Attendance and proxies again.
<!-- /tui -->
<!-- gui -->
**Edit** holds Attendance and proxies again.
<!-- /gui -->

## Peripheral Code tab
<!-- help: tab-trib-code -->

The rulings of this Tribunal's own Peripheral Code: what each says, the
year it was made, and the case it came from.

### Peripheral Code
<!-- help: section-trib-code -->

Add a ruling, edit it or delete it. A ruling can name one of the
Tribunal's cases as where it came from: the Case column shows it. When a
meeting decides a case and its ruling is written into the Code, the new
ruling names that case by itself. Older rulings, such as those a
content pack brings, name none.

## Treasury tab
<!-- help: tab-trib-treasury -->

What the Tribunal holds in common, and what is owed to it.

### Treasury
<!-- help: section-trib-treasury -->

Each entry is vis, silver, a loan or a fine; Add asks which first. Vis
and silver are taken in (a positive amount) or paid out (a negative
one). A loan is silver or vis lent out of the treasury: it leaves the
treasury until it is marked repaid. A fine, from a case, comes in once it
is marked paid.

Most entries are typed in by the storyguide. A meeting adds one by
itself: when a case is decided with a fine, the fine owed is entered,
naming who owes it and the case. A new Tribunal, or one from a content
pack, starts with an empty treasury, since the books give no figures.

The balance above the list adds them up: the silver and vis in hand,
the loans still out and the fines still unpaid.

## Gilds tab
<!-- help: tab-trib-gilds -->

A Rhine Tribunal's gilds: the bands its covenants join, each with its
dues. Only a Tribunal following the Rhine's customs has this tab.

A covenant's own form shows the same choice from its side: while its
Tribunal follows the Rhine's customs, Edit Covenant and New Covenant
have a tick for each gild, and ticking one makes the covenant a member.
Choose another Tribunal and the ticks disappear.

### Gilds
<!-- help: section-trib-gilds -->

Each gild with its member covenants and its dues. Add a gild, edit it
(its name, its dues, and a tick for each covenant of the Tribunal that
belongs to it) or delete it. The roster's Gild column shows the gilds
each covenant belongs to.
<!-- gui -->

A gild named for one of the Rhine's six trees (Oak, Hawthorn, Ash,
Elder, Linden, Apple) bears its symbol, cut like the Arts' woodblocks:
small beside its name in the list, and large in the inspector when it is
chosen.
<!-- /gui -->

## Tokens and Archai tab
<!-- help: tab-trib-tokens -->

A Theban Tribunal's own records: each magus's tokens and shards, and the
archai who hold its offices. Only a Tribunal following the Theban
customs has this tab.

### Tokens and Shards
<!-- help: section-trib-tokens -->

Each magus of note's tokens (the Theban Tribunal's votes, earned by
serving liturgies and passed between magi), the shards cast against
them, the liturgies they have served, and their standing: an office they
hold, or that they are ostracised and until when (they may not attend or
vote until then). Add a magus, edit their counts or delete the entry.

### The Archai
<!-- help: section-trib-archai -->

The Tribunal's offices: who holds each (or that it is vacant), when
their term ends, and its duties. The archai are elected at each meeting.

## Tenure tab
<!-- help: tab-trib-tenure -->

A Normandy Tribunal's record of who holds each vis source under the
Perthean Compact. Only a Tribunal following the Normandy customs has
this tab.

### Vis Tenure
<!-- help: section-trib-tenure -->

Each vis source, who holds it (a covenant of the Tribunal, or the
Tribunal itself), its tenure and when that runs out, in warning colour
once the year has come:

- **Seisin**: within a day's return march of the covenant's council
  chamber, held while it qualifies.
- **Legacy**: granted by vote for seven years; renewing it needs another
  vote, and a failed renewal makes it a tropaeum.
- **Tropaeum**: the Tribunal's, leased for seven years as a Tourney prize.
- **Luctatio**: the Tribunal's, harvested by any magus who dares; winning
  it gives no right to it afterwards.
- **Interim lease**: reported by its finders, who may harvest it until
  the next meeting.

Add a source, edit it or delete it.

## Tourney tab
<!-- help: tab-trib-tourney -->

A Normandy Tribunal's Hermetic Tourney, held after each meeting. Only a
Tribunal following the Normandy customs has this tab.

### The Tourney
<!-- help: section-trib-tourney -->

Each team's result at each Tourney, the latest first. Enter a team's
points (its starting tally and every event's); its rank, its prize pawns
and any named rank (the Sieges of Normandy, Valor, Notatus, Shame and
Alms, each a Hermetic Reputation of 2 for seven years) are worked out.
Teams level on points keep the order they were entered, since the book
breaks ties by seniority: enter the senior first. The 21st team keeps
6 pawns and gives 6 to the teams below it.

## Diary tab
<!-- help: tab-trib-diary -->

The Tribunal's own record of what happened: the minutes of each meeting
and anything else worth writing down.

### Diary
<!-- help: section-trib-diary -->

Entries newest first, each with its year and season, the numbers set in
its margin and the first line of its details. Add one, edit it or delete
it. A meeting writes its minutes here a step at a time, and its Acta
when it closes (see [Hold Tribunal](help:hold-tribunal)).
<!-- gui -->
Print prints the chosen Acta to a PDF.
<!-- /gui -->
