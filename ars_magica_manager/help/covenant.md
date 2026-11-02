# Covenant sheet
<!-- help: covenant -->

The covenant sheet holds everything that belongs to the covenant as a
whole: its attributes, its people, what it owns, its money, its library and
its history.
<!-- tui -->
It opens when you choose a covenant in the tree. Under the
covenant's node, the tree lists its **Characters** and **Laboratories**,
each of which has a sheet of its own.
<!-- /tui -->
<!-- gui -->
It opens when you choose the covenant's card on the saga's page. Its
characters and laboratories have pages of their own: their cards are in
the **People** and **Laboratories** chapters, and clicking one opens it.
<!-- /gui -->

<!-- tui -->
The top panel, with the covenant's name, stays in view above the tabs
whichever tab is open. The tabs are numbered, and the number keys `1` to `9`
open them; the last, Secrets, is the storyguide's alone. Most tabs have a details panel docked at the bottom: choose a row
and it shows that row's figures and, where there is one, its rules text and
where in the books it comes from.

More (`m`) on the top panel offers **In Creation / In Play**, which switches
the covenant between being built and being played, and, while it is In
Creation, the **Creation Worksheet**, which walks through building a
covenant step by step. The same switch and worksheet are the buttons beside
**Edit (e)** in the top panel. Export and Update from a File are in More
there too. A familiar is bound on its magus or in their laboratory.
<!-- /tui -->
<!-- gui -->
The header, with the covenant's name, its Tribunal and season, the Aegis,
the Living Conditions, and the Aura, Loyalty and Covenant Season as
medallions in the saga's set, stays in view above the chapters. The
aura's medallion is in its realm's colour, and Loyalty's is teal above
zero and rose below, whatever the season. The rail on the left lists the
chapters: **Overview**,
**Charter**, **People**, **Covenfolk**, **Laboratories**, **Possessions**,
**Treasury**, **Manors**, **Library**, **Seasons**, **Diary**, **History**, **Build**,
[**Secrets**](help:tab-secrets) and **Manage**. The help
below names two of them as the terminal's tabs: Covenfolk is the
Inhabitants tab and Treasury the Economics tab. Click a row or card and
the inspector on the right shows its figures and, where there is one, its
rules text and where in the books it comes from.

In the header, **In Creation** or **In Play** switches the covenant between
being built and being played, and, while it is In Creation, **Worksheet**
beside it opens the **Creation Worksheet**, which walks through building a
covenant step by step. The **Manage** chapter holds Export, Update from a
File and Delete. Each group of the People chapter (Magi, Companions, Grogs)
ends in a blank card, New Magus, New Companion or New Grog, and the
Laboratories chapter ends in New Laboratory; what they make belongs to the
covenant. A familiar is bound on its magus or in their laboratory.
<!-- /gui -->

How much of a covenant is written down is its detail level: a **Line** (a
name, its Tribunal and who they are), a **Sketch** (its magi, what matters
to it and its attitude to each player covenant) or **Full** (the whole
sheet). Only a full covenant is played: a Line or Sketch covenant is left
out of upkeep, income, Loyalty and the seasons, though its magi still count
toward its Tribunal's votes. **Promote** and **Demote** move it one level;
nothing is deleted. Promoting a sketch to Full moves it In Creation and
opens the Creation Worksheet on what the sketch already has.

A covenant may be the vassal of another, sworn to it by an oath: choose
its liege in **Vassal of** in the covenant's Edit, and write the oath's
duties beside it. The sheet then says **Vassal of** its liege, and the
liege's sheet lists its **Vassals**, while both are in the same Tribunal.
Ticking **Add the oath's Boons and Hooks** adds Beholden and Powerful Ally
to the vassal and Favors Owed and Protector to its liege, each naming the
other covenant; ones already taken aren't added twice. A Tribunal following
Hibernia's customs recognises no vassal covenants, so Edit refuses a liege
in the same Hibernian Tribunal.
<!-- tui -->
Both are in More (`m`) on the top panel.
<!-- /tui -->
<!-- gui -->
Both are in the **Manage** chapter.
<!-- /gui -->

A covenant is a **player covenant** when the troupe plays it ("Played by the
troupe" in its Edit): other records' attitudes point at the player
covenants. A covenant you make is played; a sketch covenant usually isn't.
Every list of covenants puts the player covenants first, each marked
with ✦, above the others.
<!-- gui -->
On The Covenants their cards carry gold corners, and a divider stands
before the rest.
<!-- /gui -->

**See also:** [Saga](help:saga), [Keys](help:keys),
[Advancing a season](help:advance-season), [How to manage the covenant](help:guide-covenant).

### The covenant panel
<!-- help: section-cov-info -->

<!-- tui -->
The panel at the top of the sheet. Saga, Storyguide, Current Season and
Current Year come from the saga and are shown dimmed: change them on the
saga, not here. Everything else is typed with `e` (Edit Covenant): the name,
<!-- /tui -->
<!-- gui -->
On the desktop this is the header at the top of the page and **The
Covenant** section at the start of the Charter chapter. The season shown comes from the saga:
change it on the saga, not here. **Edit Covenant** beside The Covenant
types the rest: the name,
<!-- /gui -->
Tribunal, Year Founded, Aegis of the Hearth and its Penetration, the two
Living Conditions, the base Aura, Aura Realm and Covenant Season. The app
works out the Aura shown, adding any Boon that raises it to the base you
typed, and that total is the aura every laboratory of the covenant starts
from. Leave a Living Conditions blank and it follows the Covenant Season:
+1 for magi and nobles in Spring or Winter and +2 in Summer or Autumn,
0 for everyone else in Spring or Winter and +1 in Summer or Autumn (DE p.
190); the sheet then shows the season beside it. Type a number to set it
instead. Living Conditions (Mundane) feeds Loyalty, both Living Conditions are
used in the aging rolls at the end of the year (the Magi one for magi and
for nobles: a Landed Noble, Knight or Gentleman/woman), and Covenant Season decides
how many points each inhabitant is worth on the Economics tab. While the
covenant is In Creation, the
<!-- tui -->
panel
<!-- /tui -->
<!-- gui -->
header
<!-- /gui -->
also shows the Build Points spent.

## Sketch tab
<!-- help: tab-cov-sketch -->

A Line or Sketch covenant opens here, beside its Diary: who it is in the
saga (typed in its Edit), its magi and their votes, What Matters, its
attitude to each player covenant, the favours owed and its links.
A Line covenant has only its attitude, favours and links.

**You type:** its magi (a line or a sketch each), how many more are
unnamed, What Matters, and each reason its attitude moved.

**The app works out:** its votes, one for each magus named or not, and
each attitude from where it started and every reason since.

### Magi
<!-- help: section-cov-magi -->

The magi whose covenant this is, at any detail, with their House and
votes, then how many more are unnamed (set in the covenant's Edit). Add
writes a new magus in as a line or a sketch; Edit changes their name,
House, detail and part in the saga; Delete removes them from the saga,
saying first what goes with them. Proxies are carried at each Tribunal
meeting, not here.
<!-- tui -->
To promote a magus to a full character, open them in the tree.
<!-- /tui -->
<!-- gui -->
Click a magus to see their statblock in the inspector.
<!-- /gui -->

### What Matters
<!-- help: section-cov-what-matters -->

Short entries, one a line, about what the covenant cares for: its vis, its
library, its Boons and Hooks. Start a line with a word and a colon ("Vis:
Vim 6 a year") to head it.

### Attitude
<!-- help: section-attitudes -->

How the record feels toward each player covenant, from −3 (Hostile) to +3
(Allied). Each starts somewhere (the "Started" row; Edit it to change it),
and every reason written down moves it: +1, −1 or more. The score is
worked out from those, never typed, and kept within −3 to +3. Add a reason
for what happened and when; delete one and the score moves back.

### Favours
<!-- help: section-favours -->

Favours owed: what for, who owes whom, and since when. A favour stays open
until a season it was repaid in is set, then shows dimmed.

### Links
<!-- help: section-links -->

Links to other records of the saga (a character, covenant, book,
possession, familiar, place or creature), each with a short note. The
record linked to lists this one in its own
[Connections](help:section-connections) (or, on a place's or creature's
page, under **Linked from**), so a link is made once and shows from both
ends.
<!-- gui -->
**Open** opens the record the chosen link points at (a book or a
possession has no page of its own to open).
<!-- /gui -->
<!-- tui -->
**Go To**, in More (`m`), lists the records the links point at, to open
one.
<!-- /tui -->

### Connections
<!-- help: section-connections -->

The records that point at this one, or that it sits in, worked out from
theirs, so nothing is entered here:

- **Covenant**: a character's or laboratory's covenant.
- **Located in**: a covenant's or laboratory's place (a laboratory with
  none of its own is where its covenant is), then each place around it.
- **Gilds**: the Rhine gilds a covenant belongs to, and the Tribunal they
  are in.
- **Member of**: each faction whose Links include this record, with the
  note on its link.
- **Rules**: each neighbour whose Ruler or leader this is.
- **Linked from**: any other record whose Links include this one.
- **Open stories**: a character's or laboratory's open Story Events,
  and the covenant whose Diary keeps them.

A connection is changed where it is made: on the faction's Links, the
neighbour's Ruler or leader, the covenant's or laboratory's place, the
Tribunal's gilds, or the Story Event's Concerns in the covenant's
Diary.
<!-- gui -->
Click an underlined name to open its record; **Back** returns here.
<!-- /gui -->
<!-- tui -->
Click a name to open its record, or press `m` (**Go To**) for a list of
them all to choose from.
<!-- /tui -->

**See also:** [Following a record's links](help:record-links),
[Links](help:section-links)

## Overview tab
<!-- help: tab-cov-overview -->

What the covenant is like: its description, its
[Connections](help:section-connections), its Reputations, and its Boons
and Hooks. The covenant's own charter, and the town charter of a
Chartered Town Boon, are on the [Charter tab](help:tab-cov-charter).

**You type:** the description, each Reputation and its score, and the
detail of each Boon or Hook you take from the catalogue.

**The app works out:** the points the Boons cost and the Hooks provide, and
warns, above the two lists, about Boons and Hooks that cannot be taken
together and about income that a Poverty Hook does not allow. Boons and
Hooks follow Ars Magica Definitive Edition, Chapter 6: Covenants.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants) (Loyalty),
[Economics tab](help:tab-cov-economics),
[Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Description
<!-- help: section-cov-description -->

Free text about the covenant: where it is, what it looks like, its history.
<!-- tui -->
`e` opens it for editing.
<!-- /tui -->
<!-- gui -->
**Edit Description** beside The Covenant opens it for editing.
<!-- /gui -->
Nothing on the sheet is worked out from it.

### Reputations
<!-- help: section-cov-reputations -->

The covenant's Reputations, each with a score (no cap: a Major Prestige
Boon's is 9, DE p. 184). Each one also
records whether the covenant knows about it: an unknown one is marked
"(not known by the covenant)" on its row. Every point of a bad Reputation
(a negative score) the covenant knows about costs 5 Loyalty points on the
Inhabitants tab, and every point of a good local one (Local, or no type)
gains 5; unknown ones count for nothing (Covenants p. 40). A Reputation may also say its type (Hermetic, Local, Noble, Academic,
Ecclesiastical or Infernal) and how far it reaches, both shown in
brackets after its score.

### Boons
<!-- help: section-cov-boons -->

<!-- tui -->
The covenant's Boons, chosen from the catalogue with `a` and edited with `e`
to give their detail and description, and to change what they name. The
picker shows the highlighted Boon's rules, requirements and book under the
list. The title shows the points they cost.
<!-- /tui -->
<!-- gui -->
The covenant's Boons, chosen from the catalogue with **Add** and edited
with **Edit** to give their detail and description, and to change what
they name. The points they cost
are under the title.
<!-- /gui -->
That total and the Hooks' total share one colour: plain while there are
points still to spend, the success colour when they match, and the error
colour when the Boons cost more than the Hooks provide. Some Boons change
figures elsewhere: an Aura Boon raises the covenant's Aura (at most seven
of them, for an Aura of at most 10, DE p. 183), a Style of
Governance Boon fills in the Type of Governance under Loyalty, and a
Boon that enlarges the buildings adds to the Buildings cost on the
Economics tab. A Hidden Resources Boon holds 250 Build Points the magi can't
use yet: its row shows how many are unlocked ("120/250 BP"), and
its details list the Story Events that unlocked them (see the
[Diary tab](help:tab-cov-diary)). Its description is the place to note
what the resources are, decided ahead or later.

A Prestige Boon gives the covenant a Reputation among the group it names:
3 for the Minor Boon, 9 for the Major (DE pp. 183-184). Add it under
Reputations; the checks advise while a Prestige Boon has none.

### Hooks
<!-- help: section-cov-hooks -->

<!-- tui -->
The covenant's Hooks, chosen from the catalogue with `a` and edited with
`e`. The title shows the points they provide, coloured together with the
Boons' total.
<!-- /tui -->
<!-- gui -->
The covenant's Hooks, chosen from the catalogue with **Add** and edited
with **Edit**. The points they provide are under the title, coloured
together with the Boons' total.
<!-- /gui -->
A Hook the catalogue allows to be unknown can be marked so,
and then counts a fixed number of points shown on its row. A Story Event in
the Diary can be linked to a Hook, and its details then say how many
stories have been told against that Hook so far. An Illusory Resources Hook
stands for 250 Build Points of improvements that don't really exist: its
row shows how many have been found out ("60/250 BP"), and its details list
the Story Events that revealed them.

An Unknown Hook is a Minor Hook a player chooses and keeps secret, counted
as Major for balancing Boons (DE p. 182). Take it either as the Unknown
entry or by marking a Minor Hook Unknown, not both: with both, the checks
say it is counted twice.

### Suggest a Story
<!-- help: hook-story -->

Hooks are the troupe's story ideas (DE p. 181).
<!-- tui -->
More's **Suggest a Story** (`m`, `y`) on the Hooks
<!-- /tui -->
<!-- gui -->
**Suggest a Story**, on the line under the Hooks' title,
<!-- /gui -->
takes one of the covenant's Hooks and proposes a story from it: its title
is drawn from the Hook's name and the detail typed on it, and the panel
shows what the Hook says (its description as typed, or the catalogue's).
Change the title as you like, and choose the season it is set for (the
next by default). **Accept** makes it an open Story Event in the
covenant's Diary, linked to the Hook, and an entry on Ahead in that
season; Cancel leaves nothing. The app writes no story of its own.

## Charter tab
<!-- help: tab-cov-charter -->

The covenant's Charter of Covenant: the written oath its magi swear and
the bylaws that say what a member is entitled to, what he owes and what
happens if he fails (Covenants p. 32). Its clauses are listed under the
charter, and the chosen one shows in full
<!-- tui -->
in the details panel.
<!-- /tui -->
<!-- gui -->
in the inspector.
<!-- /gui -->
A sketch covenant has this tab too, after its Overview, for the clauses
that matter in play. Below the charter come the town charter of a
Chartered Town Boon and the towns the covenant charters as a Charter Lord.

**You type:** the charter's name, preamble and when it was sworn, its
Official Seal (whether a Quaesitor notarized it, who and when), its
probation, who has sealed it, when and in what standing, each clause,
and each censure.

**The app works out:** how many clauses are in force and how many broken,
the members still to seal it, the grouping of the clauses by the
charter's sections, whether a breach can be charged as a Low Crime (from
the Official Seal and the Tribunal's customs), whether a charter drawn
from the Charter of Arae Flaviae still stands unaltered, when a
probation ends, and which expelled magi are still of the covenant.

See [How to draw up and keep a charter](help:guide-charter).

### The charter
<!-- help: section-cov-charter -->

The charter's name, when it was sworn, its Official Seal, the members'
seals, its preamble (the oath, or what the charter is for), and what the
law makes of it.
<!-- tui -->
`e` opens **Edit Charter**. More (`m`) here offers **Seal the Charter**
(a tick, season, year and standing for each of the covenant's magi),
**Use a Template**, **Save as Template**, **Forget a Template** (while
the saga keeps one) and **End Membership** (while a magus expelled under
it is still of the covenant). The **Sealed by** line lists those who
have sealed it, when, and any standing other than full member; the
covenant's other magi are listed as not yet sworn, and the expelled
struck through.
<!-- /tui -->
<!-- gui -->
**Edit Charter** changes its name, preamble, when it was sworn, its
probation and its Official Seal. **Seal the Charter** sets which of the
covenant's magi have sealed it, when and in what standing: each seal is
pressed in red wax with the magus's House symbol, his name and year
beneath (or his standing, when it isn't full member), an expelled
magus's seal is struck through, and a magus who hasn't sworn yet shows
as an empty dashed ring. **Use a Template**, **Save as Template**,
**Forget a Template** and **End Membership** are its other buttons.
<!-- /gui -->

**Membership.** The charter lists its members, whose seals or signatures
are affixed to show they agree to it. There may be full and associate
members, and a period of servitude before or after admittance without
full privileges (Covenants p. 33); the Charter of Arae Flaviae has
probationary members for seven seasons, and Protected Guests (pp.
126-128). A seal's standing is one of full, associate or probationary
member, Protected Guest, or expelled. A probationary seal ends when the
charter's **Probation** says (any number of seasons, or none), or when
you set it; once it has run, the charter says so, and Seal the Charter
makes him a full member or extends it. A new magus also lowers
Prevailing Loyalty: the app counts every magus of the covenant in Base
Loyalty, sealed or not, since the covenfolk feel his Gift whether or not
he has sworn (Covenants pp. 36-37).

**The Official Seal.** A charter a Quaesitor notarized is enforceable
under the Tribunal's Peripheral Code, and breaking it can be charged as
a Low Crime (Covenants pp. 32, 36). No Quaesitor can dictate what it
says unless it breaks the Code. The Charter of Arae Flaviae, used
unaltered, is ratified at once (p. 33), so a charter drawn from it shows
as notarized until a clause is amended or broken, or its preamble or
clauses change. A Tribunal's customs may say more:
- **Provence:** a charter once accepted and sworn is a legal obligation,
  and breaking it can be prosecuted as a Low Crime (Through the Aegis p.
  54). A Quaesitor must still notarize it, though some covenants put that
  off, and founding needs no leave of the Tribunal (Faith & Flame p. 21).
- **Thebes:** a new covenant declares its purpose, has a willing patron
  and draws up a suitable charter; the Conciliatory Board reviews it,
  then the Tribunal votes on a decree of founding, usually a formality
  (The Sundered Eagle p. 31). Edit Charter adds **Reviewed by the
  Conciliatory Board**.
- **The Rhine** formed one covenant's charter itself and votes on
  whether a group needs its permission to form (Guardians of the Forests
  pp. 18, 66, 142); **Normandy** asks permission to found near the
  Tribunal's own vis sources (The Lion and the Lily p. 21). Neither sets
  a rule the app applies.

**Templates.** **Use a Template** draws the charter from one: its
preamble and clauses replace the charter's, with the covenant's name,
its Tribunal's and the year filled in; its seals and Official Seal stay.
The book's is the Charter of Arae Flaviae (Covenants pp. 125-128), split
under the charter's sections. **Save as Template** keeps this charter
with the saga to start others from, for any Tribunal or one Tribunal's
customs (a covenant of that Tribunal sees it first); the covenant's and
its Tribunal's names become blanks again. **Forget a Template** drops one
the saga keeps; charters drawn from it keep their clauses.

**Governance.** How the council meets and votes, and how the charter may
be altered, is the covenant's own (Covenants pp. 32-35): write it as
clauses under Method of Governance.

### Clauses
<!-- help: section-cov-clauses -->

The charter's clauses, each with its number or a title, its words, when
it was agreed and its status: **In force**, **Amended** (with a note of
what changed and when; the earlier wording isn't kept) or **Broken**
(struck through and dimmed, with when and how it was broken, and its
censure).
<!-- tui -->
`a` adds a clause, `e` edits the chosen one and `d` deletes it after
asking. More (`m`) on a clause not yet broken opens **Break a Clause**:
the season, the year and how it was broken; its inspector shows the
clause struck through as it will read. On a broken clause, More offers
**Censure**, and **Charge at Tribunal** where the charter binds under
the Peripheral Code.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the chosen clause. **Break a
Clause**, on a clause not yet broken, asks the season, the year and how
it was broken; its inspector shows the clause struck through as it will
read. On a broken clause, **Censure** and (where the charter binds under
the Peripheral Code) **Charge at Tribunal**.
<!-- /gui -->
A clause broken by mistake is mended with Edit: set its status back.

A clause may name the section of the charter it belongs to: Oath of
Covenant, Membership, Method of Governance, Covenant Resources, Member
Rights, Member Obligations or Censure (Covenants pp. 33-35). Once any
clause has one, the list groups the clauses under small headings in that
order, with those that name none under **Other**.

**Censure.** Only breaking the charter is censured (Covenants p. 35).
**Censure** asks whom, and the penalty:
- **Privileges withheld**, which ones and until when (blank: until he
  makes amends). A covenant can withhold only what it holds in common,
  usually the library and shares of vis and money; most Tribunals take a
  magus's laboratory for his own, and withholding what is his deprives
  him of his magical power, against the Oath of Hermes, so the form warns
  you when you tick the laboratory or food, drink and shelter (p. 36).
- **Standing lowered**: a full member to probation, any other member to
  Protected Guest, as the Charter of Arae Flaviae's censure does (p.
  128).
- **Expelled**: his seal is struck through and stays on the charter.
  The app then asks whether to take him off the covenant's lists now;
  choose No to do your own bookkeeping first. While he is still of the
  covenant the charter says so, End Membership removes him, and each
  time a season is played Advance Season asks again.

**Charge at Tribunal.** On a broken clause of a charter that binds (see
the Official Seal above), this puts a charge of a Low Crime on the
covenant's Tribunal's [docket](help:section-trib-cases), brought by the
covenant, with the clause's words and how it was broken as its charge
and evidence. A member the covenant wronged under its charter has the
Tribunal as his remedy too.

**Amending.** The charter says how it may be altered (Covenants p. 33).
Several Tribunals hold that a charter may not change a member's
obligation without his agreement, and that doing so is a High Crime (p.
35).

### Charter lords
<!-- help: section-cov-charter-lords -->

Shown on the Charter tab while the covenant has the Chartered Town Boon
(City & Guild p. 11): the covenant is itself a town, chartered by its lord, and free of
feudal duties except what the charter asks; the charter can't make the
magi serve him. Its lords, as a town's [Lords](help:section-nb-charter-lords)
are kept. Add, edit or delete a lord.

With the saga's Charter Strength option on (Transforming Mythic Europe
p. 36), each lord's charter has two scores, the lord's (the superior
signatory's) and the town's or covenant's (the subordinate's). They show
in the lord's details and can be typed on his form, with **In England**
for an English charter (its notaries use Common Law, not Civil and Canon
Law); More's Draft the Charter rolls one and Seek a Loophole looks for
grounds against one.

### Charter terms
<!-- help: section-cov-charter-terms -->

The covenant's charter's family, year and privileges, as a town's
[Terms](help:section-nb-charter-terms). Edit Terms changes them.

### Towns it charters
<!-- help: section-cov-chartered-towns -->

Shown while the covenant has the Charter Lord Hook (City & Guild p.
11): the towns that list the covenant, by its name, among their charter
lords, and how it holds each. Granting charters is interference in the
mundane: neighbouring lords, petitions and revolts, and the Quaesitores
follow.

## Inhabitants tab
<!-- help: tab-cov-inhabitants -->

Who lives at the covenant, and how loyal they are.
<!-- gui -->
On the desktop this is the **Covenfolk** chapter. Loyalty shows four
figures in a row (Base Loyalty, Modifiers, Loyalty Points and the Prevailing
score), a line on what the score means and how many points the next one
needs (Covenants p. 37), and the situational modifiers as a ledger.
Household follows, with two ledgers: **Staffing** (the Teamsters and
Servants the covenant has against what it needs, read as Met, Shortfall of
2 or Excess of 1, then its Laborers and the devices doing servants' and
teamsters' work) and **Inhabitants** (each group's people, points and
what they cost a year, closed by the total). Click any figure or line and
the Inspector shows its working and its rule: Money, for instance, lists
each salary with its Loyalty points and what it does to Wages.
<!-- /gui -->

**You type:** the Loyalty choices (Equipment, Money, Pension, Familiarity,
Actions and events, Magical Influence, and the Type of Governance when no
Boon sets it), Other People, the Miscellaneous figures, and each inhabitant
you add.

**The app works out:** the magi and companions, listed from their own
character sheets; each list's headcount; the Teamsters and Servants the
covenant needs; Total Inhabitants; and all of Loyalty, from the magi's
Gifts, the Living Conditions, the salary, the specialists' roles, known bad
Reputations and the Diary. The Loyalty rules come from the Covenants
supplement.

**See also:** [Seasons tab](help:tab-cov-seasons),
[Economics tab](help:tab-cov-economics), [Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Loyalty
<!-- help: section-inh-loyalty -->

The covenfolk's Prevailing Loyalty. Base Loyalty Points is the average of
the council's Gifts (an ordinary Gift is -30, a Blatant Gift -105, a Gentle
Gift or none 0): the magi, and each companion or specialist ticked **On the
council, with a full vote** on their entry, who counts 0 (Covenants p. 38).
A token seat doesn't count. The average rounds to the nearest whole number,
as the book's example does (-225 over seven is -32). Total modifiers adds up the column on the right: Living
Conditions (10 for each point of Living Conditions (Mundane)), Equipment and
Money from the choices you make with
<!-- tui -->
`e`
<!-- /tui -->
<!-- gui -->
**Edit** beside Loyalty
<!-- /gui -->
(a Pension adds to Money, and its **Pensioners** each cost half Wages),
Specialists (below), Familiarity (worked out: 2 points for every year
since the covenant's Year Founded, at most what the magi's Gift takes off,
DE p. 186; newcomers dilute it by their share of the covenfolk and grow
used to the Gift at the same 2 a year from when they arrived, so it climbs
back to its most, Covenants pp. 37, 40; the **Familiarity adjustment** you
type changes it further), Reputation, Actions and events (the
Diary's Loyalty points plus any you type), and Magical Influence.

Specialists: the Presence and Ability of the covenant's Turb Captain,
Steward and Chamberlain. An Autocrat does a Steward's and a Chamberlain's
job and adds the points of both roles, so Presence counts twice. At most
one person counts for each of the three tasks, so at most three
specialists (DE p. 186; Covenants p. 37); when more hold a task, the ones
covering the most tasks with the highest total count, and the row says how
many are left out. Current Loyalty Points is the sum, and the Prevailing
Loyalty Score comes from it by the Ability Advancement Table, negative
points giving a negative score; the table goes on past 6 (7 at 140
points, 8 at 180).

### Inhabitants
<!-- help: section-inh-population -->

A summary of the population. The numbers of Teamsters, Servants and
Laborers are counted from the Other Covenfolk list, by each entry's
Covenant Role; the number needed is worked out from the points of everyone
else, and each pair shows in the success colour when met and the error
colour when not. Other People, typed with
<!-- tui -->
`e`,
<!-- /tui -->
<!-- gui -->
**Edit Inhabitants** beside The Household,
<!-- /gui -->
is for anyone you do not want to list one by one. Total Inhabitants adds Other People to every
list's headcount except Livestock.

### Miscellaneous
<!-- help: section-inh-misc -->

Aging for Magi and for Mundane, and the numbers of Magic Laborers, Servants,
Teamsters and Turbula, all typed with
<!-- tui -->
`e`.
<!-- /tui -->
<!-- gui -->
**Edit Miscellaneous** beside The Household.
<!-- /gui -->
Magic Servants and Magic Teamsters lower the Servants and Teamsters needed,
one each: a device doing that work stands in for a person (DE p. 195;
Covenants p. 68). The others are kept as a record.

### Magi
<!-- help: section-inh-magus -->

Every magus whose character sheet belongs to this covenant is listed
automatically, with their House, year of birth and Gift taken from the
sheet. You can also add a magus who has no sheet, typing those details
yourself.
<!-- tui -->
`e` on a listed magus edits only the covenant's own notes about
them. `d` on a listed magus does not delete anyone: it marks them as
departed, so they stop counting as an inhabitant (and leave the Seasons
tab) while staying in the covenant on their sheet. `a` offers every
magus of the saga who isn't on the list: one taken off earlier counts
again, and one from another covenant moves here (it asks first). More's
**Restore** also brings a departed magus back.
<!-- /tui -->
<!-- gui -->
**Edit** on a listed magus edits only the covenant's own notes about
them. **Delete** on a listed magus does not delete anyone: it marks them as
departed, so they stop counting as an inhabitant (and leave the Seasons
chapter's lists) while staying in the covenant on their page. **Add** offers
every magus of the saga who isn't on the list: one taken off earlier counts
again, and one from another covenant moves here (it asks first).
<!-- /gui -->

### Companions
<!-- help: section-inh-companion -->

Companions (and Mythic Companions) whose sheets belong to this covenant are
listed automatically; companions without a sheet can be added by hand. Each
can have a Responsibility and a Covenant Role. A Steward, Chamberlain, Turb
Captain or Autocrat earns the covenant a Loyalty bonus of Presence plus the
role's Ability, read from the character sheet. As with magi,
<!-- tui -->
`d` marks a listed companion as departed, and `a` (or More's
**Restore**) brings them back.
<!-- /tui -->
<!-- gui -->
**Delete** marks a listed companion as departed, and **Add** brings them
back.
<!-- /gui -->

### Specialists
<!-- help: section-inh-specialist -->

Covenfolk with a particular job.
<!-- tui -->
`a`
<!-- /tui -->
<!-- gui -->
**Add**
<!-- /gui -->
first offers the covenant's grogs that
are not yet on any list, or a new person who has no sheet. A specialist can
hold one of the Covenant Roles that earn a Loyalty bonus, as companions can;
for one without a sheet you type the Presence and Ability the bonus comes
from. Every specialist counts towards the points of inhabitants.

### Craftspeople
<!-- help: section-inh-craftsperson -->

Craftspeople, added from the covenant's unassigned grogs or as new people.
You give each one a crafting skill (or link it to an Ability on their
sheet), a Field of Work, whether they are rare, and a Quantity. Their Field
of Work decides which cost they save on the Economics tab: a common
craftsperson saves 1 plus half their skill a year, a rare one their skill.
A craftsperson working on Books saves nothing but adds to Writing
Materials.

Specialists, craftspeople, the turb and other covenfolk are counted as
here since the covenant's founding until someone joins them.
<!-- gui -->
**Recruit**, beside a list's Add, Edit and Delete, adds people to the line
clicked: how many and the year they came. **Depart** takes people away:
you choose which arrival they belong to (those here since the founding,
or those who joined in a given year), how many, and why. Both write the
covenant's Diary under Inhabitants, and a line everyone has left is
removed. To re-date people already on a line, **Edit** it: it has a year
for each group, blank for those here since the founding. Change a year to
re-date that group; groups given the same year merge.

Someone added to a list in play arrives in the saga's current year: the
add form shows it as **Year arrived**, which you can change, or clear for
someone who has been here since the founding. While a covenant is being
created its people start as here since the founding.

Every list of people, magi and companions too, has a **Year Arrived**
column (a magus's or companion's is set with Edit: blank for here since the
founding). A line whose people came in different years shows **Varies**,
with an indented row under it for each group: how many and when; clicking
one chooses its line. A year in italics is newcomers still growing used to
the Gift. Click a
line to see in the Inspector when each group arrived and how used to the
Gift they are yet.
<!-- /gui -->
Newcomers dilute Familiarity until they grow used to the Gift (see
Loyalty). Saves shows what each one saves a year; "(cap)" means the
craft's cap on its cost, a share of that cost rounded down (Covenants p.
68), cuts it.

### Turb
<!-- help: section-inh-turb -->

The covenant's soldiers, added from its unassigned grogs or as new people,
with a Responsibility and a Quantity. They count towards the points of
inhabitants, and so towards the yearly costs on the Economics tab.

### Other Covenfolk
<!-- help: section-inh-inhabitant -->

Everyone else who lives at the covenant, in one list. Each entry needs a
Covenant Role (Laborer, Servant, Teamster or Dependent) and can stand for
several people through its Quantity. The Inhabitants summary counts the
Laborers, Servants and Teamsters from here, and each Laborer saves on
Provisions on the Economics tab.

### Horses
<!-- help: section-inh-horse -->

The covenant's horses, with a Quantity. Each counts as one point of
inhabitants, whatever the Covenant Season. Adding one offers the
covenant's animal grogs (Grogs, Chapter 7: Horses & Hounds) not yet on a
list, so a named horse can be one of the covenant's horses.

### Hounds
<!-- help: section-inh-hound -->

The covenant's dogs, hawks and other working animals, with a Quantity.
Adding one offers the covenant's animal grogs not yet on a list, or an
animal with no character sheet. Covenants counts only horses among the
inhabitants, so hounds count towards neither Total Inhabitants nor the
points of inhabitants, as livestock don't.

### Livestock
<!-- help: section-inh-livestock -->

The covenant's animals, kept here for convenience. Livestock are not
inhabitants: they count towards neither Total Inhabitants nor the points of
inhabitants.

### Whereabouts
<!-- help: section-cov-whereabouts -->

Where a covenant on the move is now, and where it has been. It shows on the
Overview of a covenant with a stop, a route, or a Mobile Hook (Constantly
Mobile, Erratically Mobile, Covenants pp. 9-10); those Hooks have no rules of
their own, so this is what makes them count. **Add a Stop** is offered for
every covenant.
<!-- tui -->
More (`m`) on a covenant offers **Add a Stop**. On Whereabouts, `a`, `e` and
`d` add, edit and delete a stop, and More offers **Plan Route**.
<!-- /tui -->
<!-- gui -->
**Add a Stop** sits beside The Covenant's Edit Description, and on a sketch
beside What Matters, until Whereabouts shows. Whereabouts has Add, Edit, Delete
and **Plan Route**.
<!-- /gui -->

A stop is a date and a Place of The Region with its level; open water is a sea
Place with no aura. The latest stop not after the saga's date is where the
covenant is, so a stop dated later waits for the date. The covenant's own
Place stays its home, and **With no stops nothing changes**.

**What follows the covenant.** Its aura is the aura of the stop, so casting,
laboratories, vis study, aging and Warping all follow it. A Place set to
**Travels with** the covenant (its own aura or regio, as the Favonius ships
have) goes inside each stop's Place. On its surface the stronger of the two
auras holds sway, with its realm (DE p. 410), and a tie keeps its own; inside
its regio only the regio counts. A Dominion port of 3 beats a ship's Magic 2.
This is a ruling for travelling Places: a fixed Place inside another keeps its
own aura. If a covenant with a typed aura and no Place logs its first stop, tick
**Its aura travels with it** to make that aura such a Place; otherwise the aura
stays behind.

**What stays behind.** The Aegis of the Hearth: a Boundary effect isn't mobile
(Legends of Hermes p. 123). When Add a Stop or Advance Season moves the covenant
its Aegis drops to 0, and the Diary says so under Defence & Magic. Editing or
deleting a stop corrects the log and changes nothing else. Vis sources stay too:
**Vis this season** names those harvested now and where they lie, so that the
route can be planned round them. Whether the covenant got there is not checked.
Neighbours, Tribunal and possessions don't change.

**Ships.** On a covenant with a ship afloat, the stop form lists Places marked
with **Waters** first, and warns of an unmarked Place without refusing it. The
book packs mark their ports, anchorages, seas and working rivers. A port town
has a harbour Place beside it, which the town links to, since a stop must be a
Place. A harbour holds its own aura and inherits none: Divine 3 for a town or
city, Divine 2 for a village (Definitive Edition p. 418), unless the book prints
another figure. So a ship's magi stop inside the Dominion, and a ship with its
own aura gives way to a stronger port on the surface. A
ship covenant holds an Aegis only docked at a Port for the whole season, not at
an Anchorage: Edit Covenant refuses a higher Aegis anywhere else, and one still
held away from a Port is lost when Advance Season keeps it there. That is this
saga's ruling; the book only has its magi work at anchor (Through the Aegis
p. 23).

**Plan Route** lists the legs in order, with the seasons to stay at each, and
**Circuit** goes back to the first after the last (Traveling Covenant, Covenants
p. 27). A route is a plan: [Advance Season](help:advance-season) offers its next
leg, and what really happened is logged as a stop.

**See also:** [How to keep a covenant on the move](help:guide-mobile-covenant)

### Guests
<!-- help: section-cov-guests -->

The magi staying at the covenant as its guests ([Stay as
Guest](help:guest-stay)), each with when he came, the last year of his
stay, his yearly fee and **This Year**: *Due* while this year's fee is
owed, *Paid* once it is. A sketch covenant lists them on its Overview,
while it has any.
<!-- tui -->
`e` edits the chosen guest's stay. More (`m`) on a guest who owes this
year's fee opens **Pay the Fee**.
<!-- /tui -->
<!-- gui -->
**Edit** opens the chosen guest's stay. **Pay the Fee**, on a guest who
owes this year's fee, takes it.
<!-- /gui -->

**Pay the Fee** takes the year's vis from the guest's own (choose which
Art) or his silver, and gives it to the covenant as Give does, both
Diaries saying so; a fee in service asks what he did, and writes that in
both Diaries. Either marks the year paid. A guest who holds too little
is refused: give him what he needs first, or note it in the stay's
conditions.

## Seasons tab
<!-- help: tab-cov-seasons -->

The covenant's planning board: everyone at the covenant down the side, and
the year that can be planned across it (this season and the three after
it), each cell the activity planned for that season or "nothing" (this
season's in the warning colour, so a gap that matters now stands out).
Companions also have **Worked**: their working seasons this year, those in
their Diary and those planned for the rest of it, out of the two a
companion owes (Ars Magica Definitive Edition, Chapter 10: Assigning
Seasons). Each title counts how many are planned this season, and the
<!-- tui -->
details panel
<!-- /tui -->
<!-- gui -->
inspector
<!-- /gui -->
shows the chosen person's plan in full, then each season ahead.
People marked departed on the Inhabitants tab are left out.
<!-- gui -->
On the desktop, the Seasons chapter also draws a timeline of everyone's
seasons below the lists; click a season on it to read it in the inspector.
<!-- /gui -->

**You type:** each magus's and companion's plan for the season, and each
grog's yearly update.

**The app works out:** nothing on this tab itself. When you
<!-- tui -->
press `t` to advance the season,
<!-- /tui -->
<!-- gui -->
advance the season with **Advance Season** in the top bar,
<!-- /gui -->
every plan is worked out and applied, and someone with
nothing planned gains nothing that season. At the end of Winter the year
closes: before the date moves on, if any covenant spends more than it earns
the app asks whether to stop and balance the books first; then each
covenant's surplus is added to its Wealth, any deficit Emergency Savings
didn't cover is taken from it (DE p. 189; letting Wealth go below 0, the
covenant broke, is the app's house rule), Inflation grows a pound for every hundred pounds the
year spent unless spending fell (DE p. 193), and Emergency Savings start
again at 0.

**See also:** [Planning a season](help:plan-season),
[A grog's year](help:grog-year), [Advancing a season](help:advance-season),
[Economics tab](help:tab-cov-economics), [How to plan and run a season](help:guide-seasons).

### Magi
<!-- help: section-cov-seasons-magus -->

The covenant's magi, each with what they have planned for each season of
the year ahead, or "nothing".
<!-- tui -->
`a` or `e` opens the chosen magus's season plan, the same
dialog as on their own sheet, for this season: its **Season** field plans
one of the seasons ahead instead. `d` clears this season's plan after
asking first.
<!-- /tui -->
<!-- gui -->
**Plan** opens the season plan of the magus last clicked, the same form as
on their own page, for this season: its **Season** field plans one of the
seasons ahead instead. **Clear** clears this season's plan after asking
first.
<!-- /gui -->

### Companions
<!-- help: section-cov-seasons-companion -->

The covenant's companions and Mythic Companions, planned the same way as
the magi, with **Worked** counting their working seasons this year ("1 of
2"):
<!-- tui -->
`a` or `e` plans the chosen companion's season and `d` clears the
plan.
<!-- /tui -->
<!-- gui -->
**Plan** plans the chosen companion's season and **Clear** clears the
plan.
<!-- /gui -->

### Grogs
<!-- help: section-cov-seasons-grog -->

The covenant's grogs. They are not planned season by season: the board
shows "yearly" for their yearly update.
<!-- tui -->
`a` or `e`
<!-- /tui -->
<!-- gui -->
**Plan**
<!-- /gui -->
sets up the chosen grog's yearly update, whose training,
practice and exposure experience is applied at the end of Winter.


## Ahead for the covenant
<!-- help: section-cov-ahead -->

What is coming that concerns the covenant, season by season: its fairs'
income rolls, its people's aging and returns from Twilight, its
Tribunal's meetings, the region's threats and places, and your calendar
entries for it or for the whole saga. It looks as far ahead as the
saga's [Looking Ahead](help:section-ahead).

**You type:** your own calendar entries: Add one (it is for this
covenant), and Edit or Delete it. A row worked out from another record
is changed on that record.

## Possessions tab
<!-- help: tab-cov-possessions -->
<!-- gui -->

On the desktop this is the **Inventory** chapter.
<!-- /gui -->

What the covenant owns: land, sanctums, arms and armour, vis, other items
and enchanted devices.

**You type:** each possession and its details.

**The app works out:** the sanctums of the covenant's laboratories, listed
automatically; the book figures of a weapon or armour chosen from the
catalogue; and, from all of these, the points of laboratories and of
weapons and armour that drive costs on the Economics tab.

**See also:** [Economics tab](help:tab-cov-economics),
[Build tab](help:tab-cov-build), [Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Ships
<!-- help: section-pos-ship -->

The covenant's ships. Add one and choose **Like** to fill her size, cargo and crew from Hermetic Projects' table of ships (p. 54): a river ferry, a lighter, a river barge, a coastal buss (or knarr or small cog), a medium cog, a large merchant cog, and the Mediterranean grain barges. Change any figure afterwards. A lateen-rigged ship needs half as many crew again; a galley can ram and shear oars.

Her **damage levels** are her quality's (Shoddy 1, Standard 2, Superior 3, Excellent 4, Supernatural 5) times her size's (2 up to size +5, 3 for +6 to +8, 4 for +9; HP p. 54, City & Guild p. 77). She sails on until every level is lost; then she is wrecked, and any enchantment in her is gone (HP p. 65). Fewer levels lost than before marks her repaired.

Cargo space can carry fighting men instead: 8 a ton on a long voyage, or 16 a quarter ton raiding close to home (City & Guild p. 87). Each ballista or light catapult takes a quarter ton, and a ship carries at most one per 20 tons (p. 86). A Superior ship gives +1 to navigation and ship-handling rolls, an Excellent one her bonus there and to Lab Totals enchanting her (HP p. 63); enchanting a Standard ship costs -1, a Shoddy one -3 (City & Guild p. 70).

<!-- tui -->
Choose a ship and press `m` for More:
<!-- /tui -->
<!-- gui -->
Choose a ship, then the buttons beside Add, Edit and Delete:
<!-- /gui -->

- **Stress Check** (a storm, fire, naval combat or a magical attack, HP p. 53): a stress die + her captain's Profession + her quality (-1 Shoddy, +1 Superior, +3 Excellent, +5 Supernatural) + the magnitude of the total levels invested in her (all her effects' levels added together), -1 in poor weather or -3 in severe, -1 if repaired before, against 15 (City & Guild p. 77). Failing costs a damage level; a botch one, and one more for every botch die that shows a 0. The Diary records it.
- **Ship Combat** (City & Guild pp. 86-87): choose their ship (another ship of the saga's, or one typed in) and what you mean to do. Each captain rolls a stress die + Intelligence + Profession + up to 3 for an experienced crew, + what favours his side (a faster ship, fog). The winner boards or slips away; a galley may ram (the rammed ship founders in 5 x a simple die minutes; a sailing ship that rams stays entangled) or shear oars (2 x a simple die rowers out of action). Artillery shoots as the ships close: a ballista kills a crewman a hit within 600 yards, a light catapult puts a simple die / 2 out of action within 200; each reloads in ten rounds. A boarding sets up a Fight in Conflicts for the two crews to fight as groups; the taller ship's men have +3 Attack and Defense until they are boarded. The Diary records it.
- **Detach**: she sails on her own for a while, still of the covenant, since a covenant rests on its charter and not on being together (Guardians of the Forests p. 70; Through the Aegis pp. 11, 25). Say where she goes, and whether each magus of the laboratory aboard goes with her (ticked unless you say otherwise). Her laboratory and those who go take their aura from her stops, with no Current Location to set. Her entry on Possessions says she is apart, where she is and who is aboard. Advance Season asks about her each season.
- **Rejoin**: she comes back to the fleet, and her stops end. The Diary records both.
- **Sunk or Taken**: what became of her after a fight or a storm. Sunk, or Taken (by whom), she shows so on the list and counts in no fleet battle; one taken by another covenant of the saga moves to its Possessions, afloat, and both Diaries say so. Choose Still afloat to undo it. The books give no rule for this (Tales of Power pp. 109-110 has a victor claim the ships he boards), so it is a record.

**Laboratory aboard** names the lab she carries, so that it can leave with her.

The captain's Profession is the best of his seafaring Professions (Sailor, Mariner, Captain, Ship, Navigator, Pilot). Sailing speed is City & Guild's 60 to 80 miles a day (about 30 by the Definitive Edition, p. 408).

### Build a Ship
<!-- help: build-ship -->

**Build a Ship** makes a new ship for the covenant three ways (Hermetic Projects pp. 62-65):

- **A shipwright and his team**: the master's Workshop Total (Intelligence + Profession: Shipwright + the workshop's Innovation and Raw Materials) sets her quality against the Craft Levels (3 Shoddy, 6 Standard, 12 Superior, 15 Excellent, a point higher in a supernatural aura); an Excellent ship's bonus is +1 for every 3 over, at most his score / 3 (City & Guild pp. 67-69). At Profession: Shipwright 5 she takes two seasons, at 10 one, in between to the nearest nice fraction (City & Guild p. 68); the Conscientious Carpenter adds 1 to his score for the time. She is on Ahead in the season she is finished.
- **Rego craft magic**: Perception + Finesse + a stress die against her Ease Factor (a river barge 15, a coastal buss 21, a large cog 27, a grain barge 30; HP p. 63). For another ship type **Craft magic Ease Factor**: a shipwright's Ease Factor + 6 for a season's work or + 9 for a year's (Covenants p. 49). Success makes her as good as the caster's Workshop Total makes her: his Intelligence + Profession: Shipwright + the workshop's Innovation and Raw Materials, as a shipwright's build (HP p. 63).
- **A Creo ritual**: Intelligence + Finesse + a stress die against 9; she is a copy of the ritual's template, of the template's quality.

The panel also says what opening her for enchantment takes (pp. 66-67): her hull alone (10 pawns of Vim for a small ship up to 18 for a huge one), or as a compound device with the parts ticked (a mast 8, rigging 10, sails 5, a rudder 8, a castle 8, an anchor 20), the costliest part's pawns or all of them, and the Magic Theory to handle that in a season. The Diary records how she was built.

### Properties and Land
<!-- help: section-pos-property -->

Land and buildings the covenant holds, each with a Location, Dimensions,
who lives there and a description. These are a record: nothing is worked
out from them.

### Sanctums
<!-- help: section-pos-sanctum -->

Every laboratory of the covenant is listed here automatically, with its
owner, Quality and Upkeep taken from the laboratory, and cannot be deleted
here (move a laboratory to another covenant from the laboratory itself). For a
listed laboratory you set only its Usage (light, standard or heavy). You
can also add sanctums by hand, typing their Quality and Upkeep. Each
sanctum's Upkeep and Usage give its points of laboratories, which set the
Laboratories cost on the Economics tab.

### Weapons
<!-- help: section-pos-weapon -->

The covenant's armoury. Choose a weapon from the catalogue and its book
figures are filled in, or leave it custom and type them. Its Type and
Quality, times the Quantity, give its points of weapons and armour, which
set the Weapons cost on the Economics tab.

### Armor
<!-- help: section-pos-armor -->

The covenant's armour, chosen from the catalogue by Material or typed as
custom, with its Type (partial or full), Quality, Quantity, Protection and
Load. Like weapons, its points feed the Weapons cost on the Economics tab.

### Vis Sources
<!-- help: section-pos-vis_source -->

Places that yield raw vis, each with its Art, the Season it is harvested
and the pawns it gives. When that season is advanced, the pawns are added to
the covenant's Raw Vis Stores and the Diary records the harvest. A source
can be marked as a Contested Resource (advancing then asks whether it was
secured once its security lapses, and an unsecured one gives nothing) or as
a Dwindling Resource, which loses a tenth of the pawns it gave when it
began dwindling at the end of each year, so it is gone after ten years.
<!-- gui -->
An unsettled source shows as contested income does in the Treasury: a red
**!**, its Pawns struck through beside a 0, and its Standing. **Settle**
records the story that secures it for five years.
<!-- /gui -->
How many pawns to give one is the troupe's choice: a low-yield source gives
1, 2 or 4 a year in a low-, moderate- or high-vis saga, a moderate one 2,
4 or 8, a high-yield one (about a magus's year of vis) 4, 8 or 16
(Covenants p. 72).

A source can have a **Kind of vis** too (see Raw Vis Stores): its harvest
goes into a store of that kind, and on the Build tab a dedicated source
costs 7.5 Build Points a pawn a year, a lesser enchantment one 5 + 1 a
magnitude of its power and a spell-like one 5 + 2 a magnitude (the middle
of the book's ranges), with a stock of such vis a fifth of that for every
5 pawns (Realms of Power: Magic p. 124).

### Raw Vis Stores
<!-- help: section-pos-vis_store -->

The covenant's raw vis, by Art, with where it is kept: the covenant itself,
one of its laboratories or one of its characters. Harvests from the Vis
Sources land here.
<!-- tui -->
More's [Give](help:give) sends pawns from the chosen store to
another covenant, laboratory or magus, and both sides' Diaries record it.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, sends the pawns of the store last
clicked to another covenant, laboratory or magus ([Give](help:give)), and
both sides' Diaries record it.
<!-- /gui -->

Tick **Infernal vis** on a store that Hell has tainted (from a demon's
corpse or an Infernal aura). A Ritual drawing on vis of its Arts then
shows what Infernal vis would do: twice the botch dice (DE p. 422), or
with the **Harsher Infernal vis** option +5 a pawn to the Casting Total,
3 more botch dice a pawn, and never fewer botch dice than pawns, whatever
Mastery or a Virtue takes off (Realms of Power: The Infernal p. 19). A
chthonic magus uses Infernal vis without its peril (p. 123). Moving vis
to another store doesn't carry the mark.

**Kind of vis** marks vis that is more than ordinary. With Realms of Power:
Magic in play: *extraordinary* vis carries a power of the place that made
it, either like a lesser enchantment that isn't used up or like a spell
that is used up when its trigger comes (give **Level of its power**: such
an object usually holds a pawn for every 10 levels); *dedicated* vis is
one Technique and one Form together (**Dedicated with** names the other
Art): for that pair it gives +4 a pawn in casting, each pawn counts as two
toward a Ritual's or an enchantment's pawns and for botch dice, and it
doubles its form's Shape and Material bonus; *Herbs* and *Objects of
Virtue* (formed stones are Objects) hold 1 or 2 pawns and, Enriched by
someone with Magic Lore (a season, Intelligence + Magic Lore + aura of 9),
give their bearer a Virtue instead of being vis; **Thing of Virtue** picks
one of the book's (Realms of Power: Magic pp. 119-128). With Realms of
Power: Faerie in play: *encased*, *anchor* (harvesting it destroys its
faerie), *accrued*, *sleeping* and *abstract* faerie vis; abstract vis
holds no real vis, so it can't be spent (pp. 18-19).

The details say what the kind does and, for dedicated or extraordinary
vis, what a pawn is worth in trade (its Build Points / 5 ordinary pawns,
p. 124). Season work pays from ordinary stores first, then the special
ones, never from abstract vis; vis added, harvested or given joins only a
store of the same kind (and Infernal mark). A Ritual drawing on a special
store of its Arts says what spending it does. When a rook or more of one
Art is kept in one place, the details also say what so much vis may do at
the storyguide's option: spontaneous spells of its Art within Voice range,
a magnitude for each rook in a low-vis saga (each queen in a high-vis
one), or a harmless effect of the Art (pp. 123-124).

### Items
<!-- help: section-pos-item -->

Anything else the covenant owns, with a Quantity and a description. These
are a record only.

### Enchanted Devices
<!-- help: section-cov-devices -->

The enchanted devices the covenant holds, each with its instilled effects
listed beneath it. The app works out a device's capacity, each effect's
level and vis, and a Charged Item's charges, and warns when something does
not add up, following Ars Magica Definitive Edition, Chapter 8: Laboratory.
<!-- tui -->
More's **Instill an Effect** adds an effect to the chosen device (an
invested device takes any number, others only one), and **Use a Charge**
takes a charge off the chosen Charged Item, and **Use an Effect** uses the
chosen effect of an invested device or lesser enchantment once (see
[Enchanted Devices](help:section-lab-devices) for what it shows).
<!-- /tui -->
<!-- gui -->
**Instill**, beside the section's title, adds an effect to the device last
clicked (an invested device takes any number, others only one), **Use
Charge** takes a charge off the Charged Item last clicked, and **Use** uses
the effect last clicked once (see
[Enchanted Devices](help:section-lab-devices) for what it shows).
<!-- /gui -->

## Projects tab
<!-- help: tab-cov-projects -->

A covenant's great works (Hermetic Projects): a Great Tower (pp. 36-41), a Menagerie (pp. 119-142), or one followed stage by stage, a Burning City, an Intangible Assassin or a Living Corpse (pp. 9-28, 77-118). The tab shows once a project is begun: Begin Project, in Undertakings on the Seasons chapter (More on the covenant in the terminal). Deleting the last project hides it again.

**See also:** [Possessions tab](help:tab-cov-possessions), [Economics tab](help:tab-cov-economics)

### Hermetic Projects
<!-- help: section-cov-projects -->

Each project: its name, kind, when it was begun, its height and its weakest work. Add, Edit and Delete as anywhere; the form names its master mason, its place (whose aura its rituals' tethers feed) and the building operation's Innovation and Raw Materials, 0 to 3 each: the whole operation is the master mason's workshop (HP p. 37). More's Show Project puts the chosen project's tower, works and devices on the tab.

### The tower
<!-- help: section-cov-tower -->

Its height (20 feet a level), quality, damage levels, the tethers its rituals made and the failed Finesse rolls so far; then the master mason.

- **Rate** (HP pp. 36-37): an effective Craft: Mason of 5 builds a level a season, 10 two, 15 three. Craft devices add +1 each to that score for the rate alone, each kind of device counted once, never more than his Craft: Mason (p. 39). HP calls this generous and lets troupes slow it; the app keeps it as printed.
- **Workshop Total** (p. 37): Intelligence + Craft: Mason + Innovation + Raw Materials, against 3 shoddy, 6 standard, 12 superior, 15 excellent. De Architectura (the covenant's or the mason's copy) gives +1 Innovation, the Water Wheel +1; Innovation never passes +3 (pp. 37, 41). City & Guild leaves the Characteristic to the troupe (p. 67), so the tower's Intelligence doesn't change its workshops'.
- **Damage levels** (p. 38, after City & Guild p. 77): 1, 2, 3 or 4 by quality, x4 for a tower of size 10 or more: 4, 8, 12 or 16. The weakest work in the tower sets them, so they can fall as well as rise. A ritual whose Finesse roll succeeds builds standard work, a failed one shoddy (p. 39). A season's rebuilding makes a shoddy section standard; a season's repair restores one damage level, with no other building that season (p. 38).

**Stress Check** (More): the storyguide's event (severe storm, fire, earthquake or subsidence, assault: nothing else calls for one), stress die + Craft: Mason, -1 previously repaired, -1 shoddy, +1 superior, +3 excellent, +1 a Flying Buttress (as many as his Craft: Mason, p. 41), and the event's severity, against 15. A failure loses a damage level, a botch one more for each botch die (City & Guild p. 77): a partial collapse and a story. Roll keeps it in the works.

**Conjure Levels** (More): Conjuring the Great Tower (CrTe 55) raises the foundations and two levels; Heights of the Great Tower (CrTe 50) four more, a magnitude larger 40, two larger 400. Int + Finesse + stress die against 12 (+3 a magnitude): standard if it reaches, shoddy if not. Heights' botch dice are 1 + one for each earlier level built on a failed roll, whoever cast it (a failed Conjuring leaves 2 shoddy levels, a failed Heights 4), and +3 a magnitude; a botch is a story, and a botched Conjuring leaves foundations that need a stress check every year (pp. 39-40). Each casting gives the project's place a preternatural tether of 1 (Conjuring the Great Tower makes a Magic aura of 1 where there was none; Heights adds +1 to the year's aura modifier), which the place's aura rules read (Realms of Power: Magic pp. 8-11). Cast keeps it in the works.

### Works
<!-- help: section-cov-tower-works -->

The tower's ledger: rituals (their levels, Finesse roll and quality), the master mason's seasons, repairs, rebuildings and stress checks. Stress Check, Conjure Levels and the mason's seasons write here themselves; Add keeps anything done at the table.

### Craft Devices
<!-- help: section-cov-tower-devices -->

The enchanted devices that speed the building (HP pp. 39-41): each adds +1 to the mason's Craft: Mason for the rate (The Arms of Hercules, True Falsework, The Stonemason's Art, The Laborer's Rest; each kind once); a Flying Buttress adds +1 to stress checks instead, as many as his Craft: Mason; the Water Wheel adds +1 Innovation, to +3.

### The Menagerie
<!-- help: section-cov-menagerie -->

A Menagerie of magical beasts is the second kind of Hermetic Project (Hermetic Projects pp. 119-142). With one shown (Show Project on the projects list), the tab shows the menagerie, its beasts and its breedings in place of a tower's sections. Edit Project names its site (the place whose aura the beasts live in; the covenant's own aura without one), up to three handlers, the lead handler first, its owner and the name of his Reputation.

- **Site**: the place and its aura. A beast that always lives in a Magic aura weaker than its Might / 5 (rounded up) suffers Acclimation and is named in a warning (Realms of Power: Magic p. 53; HP p. 119). An enchanted brand that is always working may help (HP p. 130).
- **Can tend** (HP p. 136): each handler tends 10 domesticated herbivores per point of Animal Handling, half as many carnivores, a fifth as many wild beasts; "holding" counts the beasts the same way, and a warning shows when they are more than the staff can tend.
- **Upkeep** (HP p. 123): a beast costs Inhabitants points as a horse (Size +3) costs 1, each Size smaller doubling how many cost a point and each Size larger doubling the points; a carnivore costs double; the total is rounded up. It counts in the covenant's points of inhabitants.
- **Reputation** (HP p. 138): the owner's Reputation of that name, from his sheet. The storyguide awards its experience points: HP suggests 1 for every 10 visitors, 1 per magnitude of a captured beast's Might, 1 for every year past the first, 1 for each beast sold. **Reputation Award** on the Beasts list works the year's award out from those suggestions (the visitors, the beasts captured this year, whether it is past its first year, the beasts sold) and adds it to his Reputation, as a Reputation rises with experience; his Diary records it. Award anything else by hand (Reputation Award, below).
- **As realia** (HP p. 123): studied, the menagerie counts as a tractatus of Quality equal to its magical breeds, usually in Magic Lore; its collector can't study it.

### Reputation Award
<!-- help: menagerie-reputation -->

More's **Reputation Award** on a menagerie's Beasts works out the year's experience toward its owner's Reputation from Hermetic Projects' suggestions (p. 138): a point for every ten visitors, a point per magnitude of the Might of each beast captured this year (ticked), a point for a year past the menagerie's first, and a point for each beast sold to another magus. The storyguide may change any of them, so the figures are typed. Saving adds the experience to the owner's Reputation (it rises as an Ability does) and writes it in his Diary. The owner and the Reputation's name come from Edit Project.

### Beasts
<!-- help: section-cov-menagerie-beasts -->

The menagerie's beasts, one beast or several alike to a row. Each is a Beast of Virtue, a Beast of Legend or a Transformed Animal (no Might, never breeds true; HP p. 124), of an animal, its kind (lions, horses), and a breed of it (a destrier, a jennet; HP p. 131; a realia counts breeds), with its Might when grown and its Form, its Size, sex, diet, and whether it has Cunning. "In the Bestiary" ties it to a creature of the saga's Bestiary: choosing one fills its Might, Form, Size and Cunning. A beast born in the menagerie has the year it was born: until it is grown (five years for most) its Might is its grown Might divided by its years to grow, rounded down, at least 1 (HP p. 134). Ferocity is an aggressive beast's, taken off its Breeding Roll. Brands are listed one a line: a brand is an enchanted device of material 2, x2 for a palm's size, x3 a haunch, x4 the whole back (HP p. 130).

Its state: Tamed (ticked, or its taming finished), Taming (its tamer's points so far), Young or Wild.

**Tame a Beast** (More; the desktop's button): plans the chosen beast's taming. Choose who tames it. A magus's season is a Rego (its Form) lab season in his laboratory, his Lab Total (with Animal Handling and Animal Ken) less the beast's Might; anyone else's is Intelligence (Magic Lore for a Master of Creatures) + Animal Handling + Animal Ken - its Might, less the Gift's penalty (DE pp. 384-385). Plan saves a magus's or companion's season, worked out when the season is played; a grog plans no seasons, so his season is kept at once. Points last only over consecutive seasons and stay with their tamer; the beast is tamed when they reach its Might. A young beast is tamed at its smaller Might (HP p. 134). Only a beast with Cunning can be tamed; an Intelligent one must be befriended (HP p. 135).

### Breedings
<!-- help: section-cov-menagerie-breedings -->

Each season's breeding of a pair, as rolled. Add is **Breed a Pair**, HP's optional rules (pp. 140-142): choose the male and the female, what the breeding aims at (just young, for the best of a breed, or for the beast, a new line), the diet and environment, similar animals near, the pair the only ones of their kind (ticked when no other beast of their animal, of any breed, is kept; HP pp. 131, 141), a Hermetic spell's magnitudes, a ligature (Art & Academe p. 68) and the lead handler.

- **Breeding Roll**: stress die + adequate diet +1 (inadequate -2) + agreeable environment +1 (unsatisfactory -2) + a spell +1 per 2 magnitudes + herbivore +1 (carnivore -1) + the lead handler's Animal Handling / 5 and Magic Lore / 5 (each rounded up) - a magical beast's Might in magnitudes - 3 for the only pair of its kind (its animal, any breed) + 1 for similar animals near + 3 if both are tamed - an aggressive beast's Ferocity, against 9. A botch: one escapes (one botch), is sterile (two), is hurt mating (three or more).
- **The young**: as many as suit the kind; each is male on an even simple die. For the best or for the beast, each rolls a stress die + diet, environment, a spell +1 a magnitude, a ligature +1 to +3 (and +3 for a crossbred dam like her own dam): for the best a botch gives a Major Supernatural Flaw or Inferiority, 0 a Minor one, 1-3 weak (Stamina -1), 4-12 like its parents, 13-15 hardy (Stamina +1), 16-17 a Minor Virtue or Quality, 18+ a Major one; for the beast a botch dies days after birth, 0 weaker than its sire, 1-12 like its sire, 13 like its dam, 14 its sire's with a Minor Virtue or Quality of its dam's, 15+ a Major one.
- **Birth** is played out: the dam rolls as for a Medium Wound every two hours (doubled for each Size above 0), a handler adding his Animal Handling; a hatchling rolls Stamina + Survival + stress die against 9 (HP p. 134; Art & Academe p. 62).

Roll keeps the breeding and, with "Add the young to Beasts" ticked, adds each young that lives to the beasts: of its sire's kind, animal and breed (its dam's on a 13 for the beast), born this year, with the result in its note. A young of one magical parent is magical only exceptionally (HP p. 134), so it is added with no Might. Edit corrects a breeding as kept.

### The staged project
<!-- help: section-cov-staged -->

A Burning City (a covenant in the heart of a volcano, HP pp. 9-28), an Intangible Assassin (the tunnel spells and their kin, for Wizard's War, pp. 77-95) or a Living Corpse (a ghost bound to an animated corpse, pp. 96-118) is followed stage by stage. Most of each chapter is its spells and devices, which the magi invent as lab work, so the app keeps the stages and the work spent on each, and the chapter's own rules. With one shown (Show Project), the tab shows the project, its stages and its works in place of a tower's sections. Its facts: what it is, when begun, the stages done, the stage now (with its pages) and the seasons spent.

- **A Burning City**: a volcano's hazards are on Take Harm (a character's Health), with Hermetic Projects in play: lava +15 a round, multiplied by how much it covers, armour no help once it covers half the body; boiling mud +3; the heat within 30 yards of lava +3 a Diameter; falling rocks in an eruption +5 to +20; the fumes a Stamina check against 6 a Diameter (a Medium Wound), with an air Deprivation check every 30 seconds (pp. 13-14). Its laboratories' Virtues, Flaws and Features (Volcanic Minerals, Dormant and Active Volcano, Mineral Bath, Volcanic Spirit Forge, Hell Portal; Fumes, Pool of Lava, Thermal Spring, Volcanic Rock) are in the lab's lists (pp. 19, 26-27). **Warning Bell** (More) rolls Vulcan's Warning Bell when the volcano stirs: a stress die of days' warning; on a 0 the botch die's face is the hours, and a botch gives none (pp. 16-17). It goes in the covenant's Diary.
- **An Intangible Assassin**: its tunnels are Open a Tunnel's, on a magus's Known Spells. **Gather a Connection** (More) keeps an Arcane Connection to the quarry in one of the covenant's laboratories, lasting as the way it was gathered does: his spilled blood, or the weapon that drew it, years; a book or Lab Text he wrote lately, weeks; his breath, hours (pp. 86-91); it adds a work to Gathering connections. **Lower an Aegis** (More) works out the Aegis problem (pp. 94-95): Guttering of the Home-Fires suppresses an Aegis of less than half its level + 15, for a Diameter; Removing the Hearth's Keystone dispels one of less than its level + 15 + a stress die, which Roll throws. Each must Penetrate the Aegis too. A magus casting from inside a hostile Aegis loses half its level from his Casting Total (p. 79).
- **A Living Corpse**: **Death Roll** (More) is a magus's death, when he means to become one: the troupe's option, the chart's simple die (1 no spirit, 2 a ghost of another realm, 3 mindless, 4-5 an animating spirit, 6-7 a specter, 8 a shade, 9-10 an apparition) or the contest of his stress die + aura + Magic Lore + Vim Form Bonus against the storyguide's stress die (no botch) + all his Personality Traits + his highest Dominion, Infernal or Faerie Lore (equal or higher a magic ghost, 3 higher a specter, 6 a shade, 9 an apparition; lower, a ghost of that Lore's realm; a botch, none). An unGifted character's magic ghost is only ever a specter. Then the ghost's starting Might by the saga's power, its Season and the experience to buy back his Abilities (Spring 120, Summer 360, Autumn 720, Winter 1200), its vis (a pawn for each 5 of Might), its Virtues (Magic Spirit, Transformed (Being), Magical Air: none for the Gentle Gift, Blatant for the Blatant) and his one Personality Trait, his highest doubled; and a corpse animated days after death loses 1 from each Physical Characteristic a day, to -5, which lasts a year (pp. 107-111). It is written in his Diary and on The transformation stage. His sheet isn't rebuilt: his Qualities, Abilities and Powers are bought again by hand, as a magic creature's (Realms of Power: Magic). A living corpse doesn't age, Warp or fall into Final Twilight, can't be Incapacitated and does no lab work (p. 114).

### Stages
<!-- help: section-cov-staged-stages -->

The project's stages, in the chapter's order, each with its pages, the works spent on it, their seasons and whether it is done. A new project starts with its chapter's: a Burning City finds a volcano, raises or wakes one, protects its people, controls it, builds and lives in the crater, deals with its inhabitants and fits out its laboratories; an Intangible Assassin learns its tunnel spells, manipulates and defends against tunnels, its effects to cast through them, gathers connections, raises its Casting Total and faces the Aegis; a Living Corpse binds a ghost to a vessel, animates the corpse, passes control to the ghost, enchants its devices and goes through the transformation. Add, Edit and Delete as anywhere; Edit ticks a stage done. A magus's lab season is spent on a stage by choosing it on his lab work ("Spent on a project's stage"); when the season is played it is kept with the stage's works.

### Works on the stages
<!-- help: section-cov-staged-works -->

What has been done on the project: each lab season spent on a stage (written when the season is played), each connection gathered and each death roll, and anything Added by hand (a story's work takes 0 seasons). Each names its stage, when, who and the seasons spent.

## Economics tab
<!-- help: tab-cov-economics -->

The covenant's yearly finances: what it earns, what it spends, what it
saves, and what it has in store.
<!-- gui -->
On the desktop this is the **Treasury** chapter: the year's income,
expenditure and balance at the top, then Wealth and the tables. A line
under them says what settling any unsettled income would bring. When Wealth
can't cover a deficit, **Covering the Deficit** lists the book's ways out,
with this covenant's figures (DE pp. 195-196): miserly wages and what they
do to Loyalty, the magi giving up their comforts, letting covenfolk go, or
neglecting a whole category.
<!-- /gui -->

**You type:** Wealth, the sources of income, Tithes, Inflation and Sundry,
Magic savings, Emergency Savings, and a note on any row.

**The app works out:** everything else, from the rest of the sheet: the
points of inhabitants, laboratories and weapons and armour, every
calculated cost, the savings from laborers and craftspeople, Total Income,
Total Expenditure and the Surplus/Deficit. Every figure is a whole number,
and changes anywhere on the sheet show here at once. The finance rules come
from the Covenants supplement.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants),
[Possessions tab](help:tab-cov-possessions),
[Seasons tab](help:tab-cov-seasons) (the end of the year), [How to manage the covenant](help:guide-covenant).

### Wealth
<!-- help: section-eco-wealth -->

The totals. On the left, the points of inhabitants, laboratories and
weapons and armour that the costs are worked out from (characters under
a physician's regimen cost more points of inhabitants: theirs are
multiplied for each step the regimen raises their Living Conditions to,
to +1 x1.5, to +2 x2, to +3 or more x2.5, rounded up, so two companions
raised from 0 to +2 cost 18, not 6; Art & Academe p. 58), and Wealth, the
pounds in store, which you type with
<!-- tui -->
`e`. **Give Silver** (More, `m`) gives pounds to a character or another
covenant ([Give](help:give)).
<!-- /tui -->
<!-- gui -->
**Edit** beside Wealth. **Give Silver**, beside it, gives pounds to a
character or another covenant ([Give](help:give)).
<!-- /gui -->
On the right, Total Income, the
expenditure before and after cost savings, and the Surplus/Deficit. At the
end of each year the surplus is added to Wealth, and a deficit that
Emergency Savings didn't cover is taken from it (see Cost Savings).

<!-- gui -->
On the desktop, Wealth also shows **Can Afford**, the rule of thumb that a
covenant can afford about a point of inhabitants for each pound of income
(DE p. 191), and what next year's Inflation will rise by. The points sit
under their own heading, **What the Year Is Reckoned On**, since they aren't
money.
<!-- /gui -->

### Land Works
<!-- help: section-eco-land -->

The covenant's works of shaping the land (Transforming Mythic Europe pp.
53-77), as More's Shape the Land on Sources of Income plans them: each
project with its Rituals in order, ticked (✔) once a magus's Shape the
Land season has cast it, and the manors settled on its new land. On the
desktop the section shows once a project is planned.

### Sources of Income
<!-- help: section-eco-income -->

Each enterprise the covenant lives on, with its Type (Lesser, Typical,
Greater or Legendary). Leave Current Income blank to use the Type's usual
income. A source can be marked as a Contested Resource, which gives nothing
until it is secured, or a Dwindling Resource, which loses a tenth of the
income it gave when it began dwindling at the end of each year (gone after
ten years). One story secures a contested resource for five years (DE p.
181).
<!-- gui -->

An unsettled source carries a red **!**, its Income struck through with the
0 it gives beside it, and Standing says what contests it. **Settle**, beside
the section's title, records the story that ended it: the year, and what
settled it. Income comes back at once, Standing says when it is secured
through, and the Diary records it. When that year passes, the mark returns.
<!-- /gui -->
<!-- tui -->
More's **Improve Income** applies one year's Income Modification to the
chosen source:
<!-- /tui -->
<!-- gui -->
**Improve**, beside the section's title, applies one year's Income
Modification to the source last clicked:
<!-- /gui -->
pick an effect, see the
projected income, and confirm to set the new income and record a note.

Tick **Improved by magic** when the year's change is the magi's doing
(Covenants pp. 57-58: the storyguide picks the Effect a magical improvement
merits; City & Guild p. 130 lists ways magic makes a profit, from gathering
commodities to ships handled by magic). The form then shows the wealth the
magic makes a year (the income it adds, unless you type it) against the
limit several Tribunals have passed: at most 2 pounds of silver, or its
like, a magus a year (Covenants p. 57, citing Houses of Hermes: True
Lineages p. 87). Going over it is allowed, since not every Tribunal has the
rule, but the form warns that Redcaps notice and the Quaesitores, or irate
merchants and nobles, follow. The note records that the change was by magic.
Spending such wealth feeds the covenant's Inflation (Covenants p. 65).

### Yearly Expenditure
<!-- help: section-eco-expenditure -->

What the covenant spends each year, by category. Buildings, Consumables,
Laboratories, Provisions, Wages, Weapons and Writing Materials are worked
out from the points of inhabitants, laboratories and weapons and armour
(Wages also follows the salary chosen under Loyalty, adds a pound for each
penny a day paid to professional soldiers, typed on the Wages row, and half
Wages for each pensioner; building Boons add to Buildings);
<!-- tui -->
`e` on those rows edits only their note. Tithes, Inflation
and Sundry are typed with `e` (Sundry is at least 1 pound a year). The
details panel shows how the chosen row was worked out.
<!-- /tui -->
<!-- gui -->
**Edit** on those rows edits only their note. Tithes, Inflation and Sundry
are typed with **Edit** (Sundry is at least 1 pound a year, before the
year's purchases). The table gives each row's cap per craft, what it costs
after savings, and how it is reckoned; the inspector has the rule.
<!-- /gui -->

Writing Materials cost a pound a year for every magus, scribe, bookbinder
and illuminator (DE p. 194): magi, craftspeople working on Books, and
specialists whose Ability or responsibility names a scribe, bookbinder,
illuminator or copyist (a scribe is a specialist, DE p. 190).

### The Year's Purchases
<!-- help: section-eco-purchases; gui -->

What the covenant has bought this year. **Buy from Goods** picks a priced
good from the Goods catalog, then its quality and how much; **Add** enters
anything else, with its kind and pounds (Covenants p. 71 has the Price
List). The last line is the Pound of Enumerus, the pound of petty costs
nobody can account for (Covenants p. 70), which **Edit** on Sundry changes.

All of it goes onto Sundry. When the year closes, each purchase is written
in the Diary under Purchases & Sales and the list starts again. A purchase
doesn't yet put what was bought anywhere: add a weapon to Inventory, or land
to a manor, yourself.

### Cost Savings
<!-- help: section-eco-savings -->

What the covenant saves. Laborers save on Provisions and craftspeople on
the category of their Field of Work, each up to the limit shown in its
details; both are worked out from the Inhabitants tab. Magic is worked out from what the row's form holds (Covenants p. 67; Transforming
Mythic Europe pp. 120-121): a pound a year for each magnitude of the effects of each of
the covenant's enchanted devices ticked as doing covenfolk's work (The Elfin Baker in
an oven, level 20, saves 4; The Instant Harvest, level 45 by the Errata, 9), five
pounds for each magnitude of Ritual spells cast for the covenant this year (back to 0
when the year closes); magic doing covenfolk's work counts as laborers (Covenants
p. 67), so the devices and Rituals together save at most half the Provisions, less
what the laborers already save, and the row's details show the cut; and a store of
grain made by magic: while it holds a year's
bread (24 bushels a point of inhabitants), the covenant saves 5 shillings a point of
inhabitants a year when half its provisions is bread, 7½ when three quarters, no more
than the Provisions it still buys. At each year's end the covenant eats a year's grain
and the store loses a twentieth (protected well), a tenth (protected) or a fifth
(covered only) of what it held (p. 121). Fill the Capacious Silo makes 20,000 bushels:
a covenant of 50 points keeping it covered eats bread from it for six years, saving
112½ pounds (p. 121). Any other saving, a craft spell cast over and over or a Ritual
the storyguide rates differently, is typed. The row's details show the working.
Replacing the covenant's purchases with magic leaves farmers, millers and carters
without their trade (pp. 121-122): a source of stories.
Emergency Savings is money drawn from Wealth to cover a deficit. While the
covenant runs at a deficit the row says so (or that the covenant is broke
when Wealth cannot cover it), and
<!-- tui -->
`e`
<!-- /tui -->
<!-- gui -->
**Edit**
<!-- /gui -->
on it first offers to draw the
deficit, or as much as Wealth holds, from Wealth. Emergency Savings start
again at 0 each year.

At a Prevailing Loyalty of -6 the covenfolk's productivity is halved (DE
p. 185): the Laborers' and Craftspeople's savings are halved, and their
rows say why. Income that relies on covenfolk is halved too: tick
**Relies on the covenfolk's work** on each such source of income, and the
year's Income counts it at half. At +6 productivity
rises, but the book gives no figure, so the rows only note it.

## Manors tab
<!-- help: tab-cov-manors -->

A covenant that holds land keeps the same Manors tab as a lord: its
[manors](help:section-manors) and its [kennels, mews and
stables](help:section-establishments), with Buy a Manor and Assart; each
troupe may farm its land any way it likes (Lords of Men p. 73), and the
oldest covenants hold allods (p. 85).

### Beside the Income
<!-- help: section-manor-check -->

A covenant's income is its sources' (Covenants pp. 56-58): each source is
the surplus left after its operating costs, so its manors are not added
to it. Here the manors' 20 pounds each (LoM p. 72) are shown beside the
source they describe, as a check against the source's income this year,
after its Income Modification (x0.5 in a slump to x1.5 in a boom,
Covenants p. 57): its farmed manors beside its Agriculture source, and
manors turned over to sheep beside its Livestock source, a separate
source (p. 60). A Typical source (100 pounds) is about five manors.
Choose the Sources picks them.

## Library tab
<!-- help: tab-cov-library -->

Every book at the covenant: the ones it owns, and the ones owned by its
laboratories and its characters.

**You type:** each book and its details.

**The app works out:** the counts in the
<!-- tui -->
Summary,
<!-- /tui -->
<!-- gui -->
shelf headings,
<!-- /gui -->
where each book is kept, and
each book's Build Point cost, shown in its details. Lab Texts and
Casting Tablets are bought as a pool (1 and 2 Build Points per 5 levels of
the library's total), so their details show the pool, with any levels
bought but not yet used.

**See also:** [Books](help:section-books),
[a laboratory's Inventory tab](help:tab-lab-inventory),
[Build tab](help:tab-cov-build), [How to manage the covenant](help:guide-covenant).

### Summary
<!-- help: section-lib-summary -->

<!-- tui -->
How many books the library holds, by type: Summae and Tractatus, each split
into Ability and Art, then Lab Texts, Casting Tablets, Other and the total.
It is worked out from the list below and cannot be edited, but `a` here
adds a book and More's **Import** reads books from a CSV file, as on the
Books list.

**Research** counts the subjects the library aids research on, when a
magus looks up a fact (Covenants, Use: Research: an Intelligence + Ability
roll with the library's bonus); a book's details panel gives its subject's
bonuses. More's **Set Up Research Library** sets the library's bonus for
<!-- /tui -->
<!-- gui -->
On the desktop the Library chapter has no summary of its own: the books
stand on shelves by type, each shelf headed with how many it holds.

The library aids research when a magus looks up a fact (Covenants, Use:
Research: an Intelligence + Ability roll with the library's bonus); a
book's details in the inspector give its subject's bonuses. **Set Up
Research Library**, a button on the Library beside Import, sets the
library's bonus for
<!-- /gui -->
each subject it has a book on, from None to +5 (a few books, a respectable
collection, a broad and deep one, specialized, peerless); under each, what
the library holds on it is a guide.
<!-- gui -->
It walks through the subjects one at a time: each step lists the books on
that subject that back its bonus, and its encyclopedias, with the bonus
the level you choose comes to and the bonuses chosen so far. Nothing is
saved until the last step's Finish.
<!-- /gui -->
**Pictorial works** on a subject raise
it one level (10 Build Points at creation, a row of the Build tab), as does
an expert correspondence on it; the bonus stops at +5. An **encyclopedia** aids research like a
library of its own: +1 for each of its tractatus on the subject (Art &
Academe, Encyclopedias), worked out and shown beside the library's bonus;
a magus uses whichever is better.

### Books
<!-- help: section-lib-books -->

<!-- tui -->
One list of every book at the covenant, with its Type, Subject, Level,
Quality and Location ("Covenant Library", the laboratory, or the character
who owns it).
<!-- /tui -->
<!-- gui -->
On the desktop every book at the covenant stands on the Library chapter's
shelves (Summae, Tractatus, Laboratory Texts, Casting Tablets, Other
Books), a summa as tall as its level; click a book to see its figures and
its Owner (the covenant, a laboratory, or a character) in the inspector.
<!-- /gui -->

With the Large Library rule on (the saga's settings), a summa's or tractatus's
details also give the library's Level and Quality in its subject, worked
out from every summa and tractatus the covenant holds on it, as Read's
"the whole library" uses them (Transforming Mythic Europe p. 105).
A book added here belongs to the covenant.
<!-- tui -->
Space (or
Ctrl+click) marks several books: with books marked, `d` deletes them all and
`e` changes only their owner. More's **Import** reads books from a CSV file
into this covenant's library, showing a preview before anything is added.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** beside the Library's title act on one
book, the one last clicked on the shelves. With more than one
book, **Change Owner** there gives the books you tick one new owner;
deleting several books at once isn't offered on the desktop yet: use the
terminal version. **Import**, a button on the Library, reads books from a CSV file
into this covenant's library, showing a preview before anything is added.
<!-- /gui -->

A book on a spell's Mastery is an Ability summa or tractatus whose Ability
is **Mastery: {spell}**, the spell's name typed in the detail: it is read
into that spell's Mastery (DE pp. 378-379).

A **codex** is one tome binding several books together, such as a summa and
a tractatus on related subjects. Choose it in a book's **Codex** field (or a
new one).
<!-- tui -->
The books of a codex are listed together, each name starting with a bar.
<!-- /tui -->
Each book in it is still studied on its own, but only one reader can
use the codex in a season, and its books are always kept together: changing
one book's owner moves the whole codex. A **palimpsest** is a codex written
over a scraped text: each text in it is read, and priced, at -3 Quality.
A codex marked **Encyclopedia** is a series of tractatus that also aids
research (see Summary). A codex can also be a **Collection**: a
**Florilegium** binds tractatus on one topic, each read on its own at +1
Quality (+2 when edited by an authority from a peerless collection); a
**Folio** binds a society's best Lab Texts and tractatus, and reading one
of its books also gives 1 xp in Order of Hermes Lore.

A folio's details give its size: its Lab Texts' magnitudes and its
tractatus' Qualities added up. Its Colentes' Magic Theory scores, summed,
must be at least that. A scribe copies a whole folio the way a summa is
copied: carefully at 6 + Profession: Scribe points a season, or quickly at
18 + 3 x Profession: Scribe (its tractatus then 1 Quality lower, and
reading them no longer teaches Order of Hermes Lore), until the points
reach the Colentes' Magic Theory (Houses of Hermes: True Lineages pp.
22-23). Copying a folio is still planned book by book in the app.

A tractatus can be a **Realia**: a collection of objects studied as a
tractatus (Covenants p. 102). Its Quality comes from its unique pieces: 1
for one, and 1 more each time they double (2 for two, 3 for four ... 6 for
32, as Atlas Games' errata count it). It costs the Art column of the
Advancement Table at covenant creation (1, 3, 6, 10, 15 and 21 Build
Points). Each reader may study it as many times as its Quality, and
several readers may share it in one season at a lower Quality: -1 for two,
-2 for up to four, -3 for up to eight (Against the Dark p. 59). A realia
ticked **An exhibit (hundreds of objects)** on an Art counts as the Art's
presence for Study Requirement and Study Bonus until the reader's score in
it reaches 15 (Against the Dark p. 61); a smaller collection doesn't, since
the objects needed grow with the Art (DE p. 145). It adds
up to 1 to its library's research bonus on its subject (Covenants p.
102), and a long expert correspondence, 120 letters or more from each of
two experts, raises it one level (p. 90). The book doesn't say whether the
two stack: together they add one, unless the troupe turns on **Research
aids stack** among the saga's rule options.

When a magus of the saga practises Holy Magic, the form has **Holy (not
Hermetic)**: a holy magus's season reading a Hermetic book on an Art or an
Arcane Ability is halved, as his Lab Total is from a Hermetic Lab Text
(Realms of Power: The Divine p. 67). A book or text is holy when it is
ticked, or when its author is a holy magus of the saga; one holy magus
learns from another's at the full total.

A summa or tractatus can be **Glossed** (+1 Quality, once): annotated
by a reader at least half as skilled as its Level with better
Communication than its author -- tick it, or plan a Read season with
**Gloss it**, which checks the reader. A tractatus's **Opus** can be **Correspondence**: letters bound in order
(at least 24 from each writer), read as a tractatus whose Quality is the
two writers' Communication added -- type it as the Quality; an **Expert
correspondence** (120 or more letters from each of two experts) also raises
its library's research on the subject one level. A **Lecture commentary**
is a teacher's lectures recorded by a scribe (the Record a teacher's
lectures season makes one), which doesn't count against the tractatus the
teacher may write. Or it can be
**Commentary**: a book about a summa,
chosen in **Commentary on**. It is read only after a season studying that
summa (the plan notes it when no such season is on record: the app records
summae studied from now on) and is read at +1 Quality, which its Build
Point cost leaves out (Covenants, Other Opus Types). Any book's **Physical
form** says how the copy was made: an **Exemplar** (-3 Quality), a
**Flap-bound** book (-1), **Juvenilia** (-3), and others that change
nothing by a set amount, such as an edition de luxe or a damaged book,
whose Quality you enter as it is. A **Congregational** book is a huge
codex several magi can study in the same season.

A book can be an **Epitome**: the book itself enchanted as an item
(Covenants, Secondary Functions). Choose an existing enchanted device, or
**(enchant it: a new invested device)** to make one: material level 2 and
size x4 (8 pawns of capacity), held where the book is kept, and moving with
it. The **Book** shape (in the shape and material list) gives +6 to
changing thoughts or images within the book, +4 numerology and +3
divination; only the epitome's own resonant materials help its
enchantment. Its effects are instilled like any device's. The Quality in a book's
details shows what it is read at and why ("10 (written 9; commentary +1)"), and its **Kind**
line names the opus and form.

With the optional rule **Extended book Quality** (the saga's settings), a book's
Quality is built from parts (Covenants, Extended Suggestions on the Quality
of Books): the author gives Communication + 3 instead of + 6 (a season of
writing makes the book that way), and the book form gains its
craftsmanship -- a skilled scribe, binder and illuminator (+1 each, for a
Profession score of 6 or more), resonant materials (+1 bought, +2 from a
story) and clarified (+1). Each counts toward its Build Point
cost. A book's details warn of what can't go together (a gloss with
resonance, a florilegium with resonance or clarification, resonance on
juvenilia...) and of an Art book over what it effectively reaches (35 -
Level for a summa, 17 for a tractatus).

A summa or tractatus shows its **Value**: Excellent, Sound, Vain or
Discarded, from its Quality against its Level (Covenants, Categories of
Value: a summa's Quality + Level, an Ability summa's Level counting three
times; about 32 and up is Excellent, 26 to 31 Sound, 19 to 25 Vain; a
tractatus about 13 and up, 9 to 12, 4 to 8). After it, a guide to its price:
in vis for a book on an Art, an Arcane Ability or a supernatural power (a
sound summa about its Level in pawns, a vain one half that, a sound
tractatus 2 or 3 pawns, an excellent book only given as a gift), and about
a pound from a stationer for any other book. The book gives its value
bands for summae only as "Quality around (31 - Level)" and so on, for a
summa on an Art (Covenants p. 94). Counting an Ability summa's Level
three times, as its Build Point cost does, and the exact boundaries
between the bands, are this app's reading.

## Diary tab
<!-- help: tab-cov-diary -->

A dated record of what happens to the covenant, in date order. Each entry
has a Year, Season, Category and Name, and can carry pounds, vis and
Loyalty points. Only the Loyalty points change the sheet: they are added
into Actions and events under Loyalty. Pounds and vis are a record.
A Story Event also has a Status (Open, Resolved, or Grown into a
threat), what it **Concerns** (the covenant, the Region, or one of the
covenant's characters or laboratories), a year to revisit it and,
optionally, a link to one of the covenant's Boons or Hooks. Every open
Story Event of the troupe's covenants is listed together on the
Region's [Open Stories](help:section-region-stories), and one that
concerns a character or laboratory shows on its
[Connections](help:section-connections). The app adds entries of its
own too: vis harvests, vis moved in or out, contested resources that
went unsecured, and an open Story Event for an experiment's story event
(concerning the magus) or a Disaster's covenant story (concerning the
covenant).

A Story Event linked to a Hidden Resources Boon also has **Build Points
unlocked**: the points of that Boon's 250 that the story opened up. They
count once the event is Resolved, and the form refuses more than the Boon
has left. Only the points are recorded: add what was found (vis, books,
items) on its own tab as usual.

A Story Event linked to an Illusory Resources Hook has **Build Points found
illusory** instead: the points of that Hook's 250 the story showed don't
really exist. They count the same way; take what vanished off its own tab.

**You type:** each entry, with
<!-- tui -->
`a`, `e` and `d` on the list.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** beside the Diary's title (Edit and Delete
act on the entry last clicked).
<!-- /gui -->

**The app works out:** the order of the entries, for a Story Event
linked to a Hook, how many stories have been told against it, and for one
linked to Hidden Resources or Illusory Resources, how many of its points
have come to light.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants) (Loyalty),
[Possessions tab](help:tab-cov-possessions) (vis),
[Advancing a season](help:advance-season), [How to manage the covenant](help:guide-covenant).

## History tab
<!-- help: tab-cov-history -->

Everything dated that is written about the covenant, in one timeline,
oldest first: its own [Diary](help:tab-cov-diary), the diaries of its
place, of the places inside it and of the records placed there (a faction
of its founders, say), and the saga's calendar entries for it that come
once. Nothing is copied: each row names the record that keeps it, and
changes there show here.

**You type:** the eras, and what to leave out. Everything else is written
on its own record.

**The app works out:** the order, the era each entry falls in, and which
entries are the same (the same date and words, kept by two records: one
row naming both). Entries from the current season on are listed last,
under Now and ahead.

**See also:** [Diary tab](help:tab-cov-diary),
[How to tell the covenant's history](help:guide-covenant-history).

### History
<!-- help: section-cov-history -->

<!-- tui -->
`a` writes a new entry in the covenant's Diary. `e` changes the chosen
entry where it is written (in the Diary, a place's diary or Ahead's
calendar). `d` leaves it out of the history; it stays where it is written.
<!-- /tui -->
<!-- gui -->
**Add** writes a new entry in the covenant's Diary. **Edit** changes the
chosen entry where it is written (in the Diary, a place's diary or
Ahead's calendar). **Delete** leaves it out of the history; it stays where
it is written.
<!-- /gui -->
An entry left out is known by its date and words, so if its words are
changed later it comes back.
<!-- gui -->
The chips above the list, one for each record the history reads from,
hide or show that record's entries: click one to read only the Founders'
story, say. An entry another shown record keeps too still shows.
<!-- /gui -->

### What It Shows
<!-- help: section-cov-history-view -->

How many entries are left out of the history, and whose entries it isn't
showing. Left-out entries are hidden until **Show what's left out** is
ticked in this block's Edit; then they are listed at the history's foot,
and Delete on one puts it back. The same Edit has a tick for each record
the history reads from (on the desktop, the chips above the list do
the same):
untick one to hide its entries. Both are kept with the covenant.

### Eras
<!-- help: section-cov-eras -->

The stretches of years the history is told in: each a name and the year
it begins, running to the year before the next one begins. No two begin
in the same year. With none, the history is told in two, before the
covenant's founding and after it (and in one, with no year of founding).
Entries before the first era are listed as Earlier.

## Build tab
<!-- help: tab-cov-build -->

What the covenant's Build Points went on. Build Points are spent when a
covenant is created and do not matter in play, so this tab is the one place
they show once the covenant is In Play. The pricing follows Ars Magica
Definitive Edition, Chapter 6: Covenants, and Chapter 8: Laboratory for the
starting laboratories.

**You type:** nothing here. The Power Level and the storyguide's Build
Points are set on the Creation Worksheet.

**The app works out:** the Build Points of everything the covenant owns,
from its library, vis, enchanted items, laboratories, specialists and
money. Below them, for a covenant with Hidden Resources, the pool those
Boons hold, how much of it Story Events have unlocked and how much is
still hidden; and the same for Illusory Resources (found illusory, still
believed real). Both are kept out of the totals.

**See also:** [Library tab](help:tab-cov-library),
[Possessions tab](help:tab-cov-possessions),
[Inhabitants tab](help:tab-cov-inhabitants), [How to create a character, covenant or laboratory](help:guide-creation).

### Build Points
<!-- help: section-cov-build -->

A row for each kind of resource, with its Initial and Current Build Points,
and the total in the title. While the covenant is In Creation the two
columns are the same, and the title shows the total against the
storyguide's Build Points. Moving to In Play keeps the Initial figures,
while Current goes on following what the covenant owns, counting every
laboratory rather than only its starting ones. A covenant that was already
in play before Build Points were tracked shows no Initial figures. To
recount the Initial figures, move the covenant back to In Creation and then
to In Play again.

Each magus has one standard laboratory free, whether or not it is entered;
starting laboratories beyond those cost 50 each. Only the magi the Power
Level step says go without a laboratory refund 50 each.

### What's Counted
<!-- help: section-cov-build-items -->

Every resource that has a Build Point price, under the row it counts
towards, with its points: each book, vis source and stock, enchanted item,
laboratory and specialist.

## Shape the Land
<!-- help: land-shaping -->

More's Shape the Land, on a covenant's Income, plans an island raised from
the sea by magic, the way Transforming Mythic Europe's Island of the
Magicians is made (TME pp. 54-77), and settles manors on it once it stands.

A project is its shape (an open cylinder, a square prism or a solid stone
cylinder), its size in miles, its wall (30 paces high and 2 thick in the
book; 240 for a tall cylinder in deep water), what the wall is made of, its
ornaments, its fill, its surface life and its wards. The form lists each
Ritual it needs, in the order they are cast:

- The wall: a Creo Terram Ritual, Touch, Momentary, Individual. Level 20
  makes 10,000 cubic paces of stone, each magnitude ten times as much (DE
  pp. 310, 359; TME p. 55). Base metal is two magnitudes harder and a cubic
  foot an Individual; precious metal three magnitudes more (TME p. 58). Wood
  and animal bone are as hard as stone, human bone as base metal (pp.
  58-59). Crenellations, machicolations, a sea gate and artistic statuary
  add a magnitude each; a fire step and hoardings add none (pp. 56-57); an
  unnatural wall needs a Muto requisite (+1). The troupe may cap complexity
  at three magnitudes (p. 56).
- The ablative slope: earth as much as the wall, three magnitudes below its
  spell (p. 56).
- The fill: soil or clay to the wall's height; stone is three magnitudes
  harder, +1 for several kinds (pp. 59-60).
- Grassland over the island and a forest of so many trees (p. 62). The
  app works their levels out from TME's own designs, whose printed levels
  are slips: the forest's (Base 1, +8 magnitudes) comes to level 25, not
  40, and the grassland's (Base 1, +4) to level 5, raised to 20 because
  every Ritual is at least level 20 (DE p. 311), not 10.
- An Aegis of the Hearth and the book's island-wide Boundary spells (pp.
  71-77), raised for the island's size: a Boundary's area is ten times
  larger each magnitude (DE p. 310), so a 3-mile island adds 4. A ward is
  its level + 35 for Touch, Sun and Boundary, plus those (TME p. 71).

Each Ritual takes 15 minutes and a pawn of vis per magnitude (DE p. 213). A
30-mile island of stone and soil is a level 35 wall and a level 40 fill: 15
pawns, under four hours (TME p. 59).

The land: a manor is 600 acres (400 if highly fertile) and 20 pounds a year
before expenses, with 5 to 60 peasant families (TME p. 62). A Ritual of
level 50 or more leaves a preternatural tether for an aura, (level - 40) /
10 (RoP: Magic p. 10); otherwise an aura needs natural beauty, ancient
structures (1 a century) or magical beings (TME pp. 64-67).

The Rituals are cast in a season of **Shape the land**. A Ritual cast on a
total of its level or more costs one long-term Fatigue level; it still
works down to 10 below its level, for two or three (DE p. 213). Once the wall and
fill are cast, Shape the Land offers **Settle** for the project: so many
manors of new land, held as allods, added to the covenant's Manors.

# Arms
<!-- help: arms -->

A covenant's shield, or a lord's, town's, church's or faction's. Six
choices make it: the **Field**'s tincture, how it is divided
(**Division**: plain, per pale, per fess, per bend, quarterly, per
chevron, bendy or checky) and the **Second tincture** of a divided
field, a **Charge** laid on it (a tower, a book, a key, a star, a sword,
a crown, a cross, a crescent, a tree, a chalice, an eagle, a lion, a
lion with its tail knotted (queue-nowed), a wheel, a fleur-de-lis, or a
bend, the band from the top left corner to
the bottom right, which is borne once), **How many** of it (one, two
side by side, or three as two and one, as heralds place them) and the
**Charge tincture**. A **Motto**, the bearer's own words, leads above
the blazon. Leave the Field blank for no arms. The historical arms of Mythic
Europe's lords, towns and sees are mostly within reach: the Emperor's
eagle, the wheel of Mainz, the cross of Trier, the three crowns of
Cologne, the lion of Flanders, the bendy of Burgundy, the checky of
Dreux.

The tinctures are the two metals, Or (gold) and Argent (silver), the
colours Gules (red), Azure (blue), Vert (green), Sable (black) and
Purpure (purple), and the fur Ermine (argent strewn with black tails).
A fur is neither metal nor colour, so it may lie on either. The blazon, the arms in heralds' words ("Per bend
azure and argent, a tower or"; "Gules, three crowns or"), is written
for you as you choose, and
the shield is drawn beside it. Heralds' rule of tincture says a colour
never lies on a colour, nor a metal on a metal: the form warns of a
charge that breaks it, which is allowed, and of one in the same tincture
as its field, which can't be seen.

<!-- tui -->
Open it with More (m) and Arms on the covenant or neighbour itself. Its
blazon shows in the record's panel and on its card in the Region.
<!-- /tui -->
<!-- gui -->
Edit Arms in the Arms section (on a covenant's Charter or Sketch, on a
neighbour's Standing) opens it. A covenant's Charter also shows the arms
of the other covenants of its Tribunal.
<!-- /gui -->

**See also:** [Covenant sheet](help:covenant)
