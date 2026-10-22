# The Region
<!-- help: region -->

The Region is the saga's world beyond the troupe's covenants: the
covenants the troupe doesn't play, and the neighbours (the lords and
towns, the Church, the universities, the factions and the threats
around them), each with its attitude toward the troupe.

<!-- tui -->
In the navigation tree The Region sits under the troupe's covenants.
Each Tribunal is listed there, with the covenants the troupe doesn't
play under the Tribunal they belong to (a covenant with no Tribunal sits
directly under The Region), then a node for each group of neighbours
with the neighbours in it. Selecting The Region, or a group, shows the
Region sheet; selecting a neighbour shows its own sheet.

Press `n` (New) here, or on the saga, and choose **New Tribunal** or
**New Neighbour**. A covenant joins a Tribunal through the Tribunal
choice in Edit Covenant.
<!-- /tui -->
<!-- gui -->
On the saga's page, The Region chapter shows each group's neighbours as
cards, each opening its own page, and a New card that adds one. The
Tribunals and the covenants are in The World.

A group with more than a dozen neighbours shows its first twelve and a
**Show more** card that draws the rest; a Tribunal book brings hundreds,
and a card for each would make the saga slow to open. The filter below
narrows them instead.
<!-- /gui -->

**See also:** [A neighbour](help:neighbour), [Tribunal sheet](help:tribunal),
[Covenant sheet](help:covenant)

## The Region's facts
<!-- help: section-region-info -->

The troupe's covenant (the first it plays, when it plays several: the
attitudes in the lists are toward it), its Tribunal and that Tribunal's
customs, how many neighbours there are and how many are warm or wary
toward it, how many other covenants there are, and when the Tribunal
next meets.

**Threat due** names the threat whose next stage comes soonest.
<!-- gui -->
The leaf after it (❧) opens that threat's page.
<!-- /gui -->

## Neighbours tab
<!-- help: tab-region-neighbours -->

The other covenants, then a list for each group of neighbours, over the
details of the one chosen: its kind and detail, its attitude toward each
player covenant and how it was reached, the first line of its summary
and the favours still open. A group is listed when it has a neighbour,
or when the book one of its kinds needs is in play.

A Tribunal book brings a great many neighbours, so the lists can be
narrowed to one **region** (a place that sits inside no other, such as
the Black Forest: everything inside it at any depth, and the region
itself) and to one **kind** (lords, towns, places...). Each list's title
then says how many it shows of how many. The filter stays while the
app is open.

<!-- tui -->
The Region's facts say what the lists are narrowed to ("Showing"). Press `/` (Filter) on any of the lists and choose a region, a kind or
both; blank both to show everything again.
<!-- /tui -->
<!-- gui -->
Choose them in the two quiet drop-downs at the right of the first list's
heading ("Show: Every region, Every kind"); set both back to Every to
show everything again.
<!-- /gui -->

### Other Covenants
<!-- help: section-region-covenants -->

The covenants the troupe doesn't play: their Tribunal, their votes,
their attitude toward the troupe's covenant and their detail. Open one
from the tree to change it.

### Lords and Towns
<!-- help: section-region-lords -->

The lords (Lords of Men) and towns (City & Guild) of the region. Add
one (choosing a lord or a town), edit the chosen one's common fields,
or delete it.

### The Church
<!-- help: section-region-church -->

The bishops, abbeys and parishes of the region (The Church). Add, edit
or delete one.

### Universities
<!-- help: section-region-universities -->

The universities of the region (Art & Academe). Add, edit or delete
one.

### Factions
<!-- help: section-region-factions -->

The gilds, hedge covens, families and other factions of the region (the
core rules). Add, edit or delete one.

### Threats
<!-- help: section-region-threats -->

The stories that grow if left alone (the core rules). Add, edit or
delete one. A story not yet begun shows as **Dormant**: open it and
choose **Begin This Story** in More to start it.

### Places
<!-- help: section-region-places -->

The forests, ruins, crags and regiones of the region: where each is,
its aura, how many regio levels it has and how far the troupe has got
with it. Add, edit or delete one; see [A place](help:tab-nb-place).

# A neighbour
<!-- help: neighbour -->

A neighbour is a lord, a town, a church, a university, a faction or a
threat of the saga's region. Only its name is needed; the rest can be
filled in later, or never.

**New Neighbour** asks for its kind first, offering the kinds whose book
is in play (Show everything lists the others, with the book each
needs), then a plain form:

- **Name**: the only field required.
- What its kind adds: a lord's title, wealth, manors and seat (see
  [A lord](help:tab-nb-fief)); a town's charter, council and population
  (see [A town](help:tab-nb-town)); a church's kind and order (see
  [A church](help:tab-nb-church)); a university's kind and fees (see
  [A university](help:tab-nb-studium)); a faction's kind, how it
  decides, its members, rules, wants and offers (see
  [A faction](help:tab-nb-faction)); a threat's antagonist and how it
  moves (see [A threat](help:tab-nb-threat)); a place's aura, tethers
  and gazetteer (see [A place](help:tab-nb-place)).
- **Summary**: a paragraph on who they are and what they want.
- **Detail**: a line, a sketch, or written in full.
- **Ruler or leader**: chosen from the saga's characters, its other
  neighbours or the Bestiary's creatures, or a name typed for one the
  saga has no record of (see [Ruler or Leader](help:neighbour-ruler)).
- **Answers to**: its liege, bishop or master among the neighbours.
  Deleting a neighbour leaves those that answered to it answering to no
  one, and a neighbour it ruled keeps its name as a name typed.
- **Realm**: Divine, Faerie, Infernal or Magic, or none.
- **Place**: the place it is in, or one of that place's regio levels.

Edit can also change its kind.
<!-- gui -->
Click a row in any of its lists (a lord's castles, a town's guilds, a
threat's stages...) to read it in full in the Inspector.
<!-- /gui -->

**See also:** [The Region](help:region)

## The neighbour
<!-- help: section-nb-info -->

Its kind, detail, ruler or leader, who it answers to, its realm and the
book its kind comes from, with its summary; then, under **Answer to
it**, every neighbour whose Answers to names this one (a lord's
vassals, a faction's members). Edit changes them.

The ruler, the neighbour it answers to, the place it is in and each
name under Answer to it are links that open that record: see
[Following a record's links](help:record-links).

## Standing tab
<!-- help: tab-nb-standing -->

Its attitude toward each player covenant, with the reasons it moved,
the favours owed between it and the troupe, and its links to other
records, as on a sketch covenant: see
[Attitude](help:section-attitudes), [Favours](help:section-favours) and
[Links](help:section-links). A place holds no attitude: its tab is
called Found Here and shows only its favours and links.

### Following a record's links
<!-- help: record-links -->

A page that names another record of the saga names it as a link: a
neighbour's ruler or leader, who it answers to, where it is and who
answers to it; a place's claimant and what is found there; a creature's
place and the neighbours it rules; what links to a place or creature
(**Linked from**); and a character's, covenant's or laboratory's
[Connections](help:section-connections).
<!-- gui -->
Click an underlined name to open its record's page. **Back** returns to
the page you came from. On the Standing tab, **Open** in Links opens
the record the chosen link points at.
<!-- /gui -->
<!-- tui -->
Click a name with the mouse to open its record: it is chosen in the
tree and its sheet shown. From the keyboard, **Go To** in More (`m`)
lists every record the page names, its links' too, under what it is
named as (Ruler or leader, Answers to, Links...); choose one to open
it.
<!-- /tui -->

**See also:** [A neighbour](help:neighbour), [Links](help:section-links)

### Go To
<!-- help: go-to; tui -->

The records the page on show names, each under what it is named as.
Choose one to open its sheet; the filter at the top narrows the list to
one kind of name. See [Following a record's links](help:record-links).

### Ruler or Leader
<!-- help: neighbour-ruler -->

Who rules or leads the neighbour, chosen from the saga's records:

- **Characters**: a lord, an abbess, a hedge wizard, at any detail.
- **Neighbours**: another neighbour, such as the faction a puppet lord
  really serves.
- **Bestiary**: a creature, such as the faerie who rules a court.
- **Type a name...**: a name only, for a ruler the saga has no record
  of yet. A name typed opens the record of that name if exactly one
  character, neighbour or creature has it, so a pack's rulers link as
  soon as their records are there.

The ruler shows on the neighbour's page as a link to their record, and
a ruling creature's or neighbour's page lists what it rules under
**Rules**. Deleting the
ruler's record keeps their name on the neighbours they ruled.

# A lord
<!-- help: tab-nb-fief -->

A lord (Lords of Men) has a title (landed noble, baron, count or earl,
duke), a wealth (poor, average, wealthy), a number of manors and a
seat, entered on New Lord or Edit. His Fief tab works out the rest:

- **Income**: 20 pounds a year for each manor.
- **To spend**: what is left after his household and his knights: 0
  if poor; a landed noble 2 (5 if wealthy), a baron 40 (100), a count
  100 (250), a duke 250 (500).
- **Free time**: a landed noble's free seasons a year: 1 if poor, 2,
  or 3 if wealthy.
- **Army**: the knights, serjeants, infantry and levies his title
  raises.
- **Owes** and **Aids**: when he answers to another neighbour, what he
  owes it: a knight's service for 40 days for each manor, or 2 pounds
  scutage a knight; aids of a pound a manor; and his heir's relief, a
  year's income but at most 5 pounds a manor (100 for a baron or
  greater).

Where Lords of Men gives two figures for the same thing, the lower is
used: a landed noble's spending money, a duke's knights and scutage.

**See also:** [A neighbour](help:neighbour)

## Castles
<!-- help: section-nb-castles -->

His castles, each with its garrison, defences and supplies. Add, edit
or delete one.

## Gratitude
<!-- help: section-nb-gratitude -->

The Gratitude he owes each character who has served him: a story that
serves his interest earns 1 point (2 if it was the story's aim), a
renowned feat 5. Each line says what its points are enough for: 5 for
freedom or knighthood, 10 for a manor of one's own, 20 for a barony
held of the king. Add, edit or delete one.

# A town
<!-- help: tab-nb-town -->

A town (City & Guild) has a charter (granted by a noble lord, the
Church, or held by its townsmen as a commune; or a faerie's or a
demon's), a council and a population, entered on New Town or Edit. Its
Town tab shows them with its size (a small, medium or large town, or a
city) and how many guilds a town its size has in the saga's year.

**See also:** [A neighbour](help:neighbour)

## Guilds
<!-- help: section-nb-guilds -->

The town's guilds: each one's trade, its dean, and how many masters,
journeymen and apprentices it has. Add, edit or delete one.

## Fairs and markets
<!-- help: section-nb-fairs -->

The town's fairs and markets, each with its season. A fair a covenant
trades at is a source of income to it, by its size: a town's yearly
fair 40 pounds a year, a county fair 100, a fair that draws traders
from across Europe 250 (or the income entered).

<!-- tui -->
More (`m`) > **Roll Income** rolls the chosen fair's year:
<!-- /tui -->
<!-- gui -->
**Roll Income** rolls the chosen fair's year:
<!-- /gui -->
a stress die picks the Income Modification (a botch a Slump, x0.5; 0 a
Contraction, x0.8; 2 Stagnation, x0.95; 3 to 8 Status Quo; 9 Growth,
x1.05; 10 to 19 Expansion, x1.2; 20 or more a Boom, x1.5), and Keep
records the new income and the roll. Add, edit or delete a fair or
market.

# A church
<!-- help: tab-nb-church -->

A church (The Church) has a kind (a chapel, a parish church, a large
urban church, a monastery or nunnery, a bishop's or an archbishop's
cathedral) and an order, entered on New Church or Edit. Its Church tab
shows its Dominion aura: a chapel's 3, a parish church's 4, any greater
church's 5.

With Realms of Power: The Divine in play, a church also records the
year worship began there, and the year it was abandoned. With the
**Dominion growth** Rule Option on (Saga Content), its aura grows with
the years of worship instead: 3 when consecrated, 4 after a year, 5
after a decade, never above its kind's; once worship stops it fades to
nothing over as long as the site was in use; and its greatest relic
raises it by 1 for each Faith Point above 5.

**See also:** [A neighbour](help:neighbour)

## Relics
<!-- help: section-nb-relics -->

The church's relics, each with its saint and its Faith Points. A
relic's Divine Might is 10 for each Faith Point, and whoever bears it
gains as much Magic Resistance. With Realms of Power: The Divine in
play, touching a relic is worth +1 to an invocation of its saint (its
Touched column). Add, edit or delete one.

# A university
<!-- help: tab-nb-studium -->

A university or school (Art & Academe) has a kind (a university, or a
cathedral, monastic, urban or parish school) and its fees, entered on
New University or Edit. Its Studium tab shows the fees (blank for its
kind's: 4 pounds a year at a university, with books, 1 at a cathedral
school), the highest an Academic Ability can be taught there (a
university has no limit, a cathedral school 6, a rural parish school 2)
and, for a university, the degrees its faculties grant.

**See also:** [A neighbour](help:neighbour)

## Faculties
<!-- help: section-nb-faculties -->

The university's faculties (Arts, Medicine, Law, Theology), each with
its rector, its endowed chairs (six to twelve) and how many of the
masters listed teach in it. A Faculty of Arts grants the Baccalaureus
and the Magister in Artibus; each higher faculty its Doctorate. Add,
edit or delete one.

## Masters
<!-- help: section-nb-masters -->

Its masters, each named or chosen from the saga's characters, with
the licence he holds and his faculty. A licence starts its holder's
Good Academic Reputation: 1 for a Baccalaureus, 2 for a Magister in
Artibus or a cathedral school master, 3 for a Doctor. Add, edit or
delete one.

# A faction
<!-- help: tab-nb-faction -->

A faction (the core rules) is a hedge coven, a faerie court, a gild, a
family or any other company with a will of its own. New Faction and
Edit record what kind it is, how it decides (its leader, a council, or
a vote of all), how many members it has, its rules, what it wants and
what it offers; its Faction tab shows them. A hedge coven can also name
the hedge tradition its members follow, from the traditions the app
knows (see [A tradition's chapter](help:tradition-chapter)), so the troupe
knows which record a member is played from. Members who are characters
can be linked on its Standing tab, and the Faction tab counts them.

Its leader is its **Ruler or leader**: a character, another neighbour or
a creature from the Bestiary (see [Ruler or Leader](help:neighbour-ruler)).
A member that is itself a neighbour (a courtier, a branch of the gild)
names the faction in its own **Answers to**, and the faction's page
lists it under **Answer to it**. A member linked from the faction lists
it under **Member of** in their own
[Connections](help:section-connections). See
[How to set up a faction's leader and members](help:guide-faction).

**See also:** [A neighbour](help:neighbour)

## Diary tab
<!-- help: tab-nb-faction-diary -->

What the faction has done, season by season: its schemes, its quarrels,
who joined or left. A place's Diary works the same way (see
[Diary](help:section-nb-place-diary)); a faction's is written only by
hand. Add, edit or delete an entry.

# A threat
<!-- help: tab-nb-threat -->

A threat is a story that grows if the troupe leaves it alone: a
faerie king gathering a court, a plague, a heresy. New Threat and Edit
record its antagonist and how it moves: by **fixed dates** (each stage
has its season and year), or along **a track** or **an omen count**
(each stage comes at a number, and Edit moves the threat's position).
Its Stages tab shows the stage it has reached and the next to come,
worked out from the saga's date (or its position); the Region's top
panel names the threat whose next stage is due soonest.

A threat can be **dormant**: a story the storyguide hasn't begun, such
as one left unticked when its pack was imported. It reaches no stage,
nothing of it comes due, and the Tribunal sheet counts it under
**Stories**. **Begin This Story**, in the threat's More, starts it:
dated stages move later together so the first still to come is due next
season at the soonest; a track or omen count starts where it stands.

**See also:** [A neighbour](help:neighbour)

## Stages
<!-- help: section-nb-stages -->

The threat's stages in order, each with when it comes, the clues that
warn of it, and what happens if it is ignored, stopped or turned. A
pending stage comes when its date (or its place on the track) is
reached; mark one **Happened** to say it came anyway, or **Stopped** or
**Turned** to say the troupe kept it from coming. The stage reached is
in bold. Add, edit or delete one.
<!-- gui -->
Click a stage to read it in full in the Inspector: when it comes, what
became of it, its clues, and what happens if it is ignored, stopped or
turned.
<!-- /gui -->

# A place
<!-- help: tab-nb-place -->

A place is somewhere the saga's records can be: a forest, a ruin, a
crag, a regio. It is a kind of neighbour without an attitude or a
ruler, listed under Places in the Region. New Place and Edit record:

- **Ruined covenant**: the place is a fallen covenant's site. It shows a
  broken tower in place of the place's own picture, and "Ruin" in the
  lists.
- **Aura**: the aura of its surface (its mundane level); the Realm field
  says whose.
- **Tethers**: the monuments, creatures or vis sources that anchor it.
- **Status** and **Known**: how far the troupe has got with it
  (rumoured, known, visited, claimed) and how widely it is known.
- **Claimed by**: the covenant that claims it.
- **Inside**: the place it is part of, so a regio can sit inside a
  forest inside a county. A place can't be put inside itself or inside
  a place within it.

A covenant, a laboratory or another neighbour names its place with
**Place** in its own Edit form, choosing the place or one of its regio
levels. A covenant placed somewhere takes its aura from there (the
level's, if it is in one); the aura typed on the covenant is kept, and
comes back if it is moved out, so its Edit form doesn't ask for an aura
while it is placed. A laboratory placed in a regio of its own takes that
level's aura instead of its covenant's.

Its Regio tab shows what is worked out for it (its next trigger, and
how its aura changes with the Auras change option), its regio levels,
its effects and its triggers; its Roll Tables and Diary tabs its tables
and what has happened there; its Found Here tab its favours and links
(the vis sources, books and creatures found there). Deleting a place
leaves what was in it placed nowhere.

**Found a Covenant Here** (More, on a ruined covenant's site) raises a
new covenant on the ruin, as the Definitive Edition's Winter Ruins
Situation does: New Covenant's form, named for the ruin and in its
aura's realm, with **Take Winter Ruins** to add that Situation's Boons
and Hooks. The covenant starts In Creation, sited on the place so it
takes its aura, and the place is then claimed by it and no longer a
ruin.

A ruin with a regio asks for the covenant's **Site**: its surface or one
of its regio levels, whose aura the covenant takes. In a level it takes
the **Regio Boon** (Minor: entered in several ways; Major: entered only
with a native guide). On the surface, the regio on its site is the
**Regio Hook** (Minor, or Major when its folk come out and make trouble),
with the Non-magical Regio Hook too when the regio isn't Magical.

With the **Auras change** Rule Option on (Realms of Power: Magic, in
Saga Content), Edit also asks for **Magic worked there** (+1 to +3 for
lab work, spells and vis study) and, for an Infernal place, the year
its **Infernal focus** was removed. A Magic aura then rises by 1 on a
yearly stress die plus the magic worked there against 15, and an
Infernal aura whose focus is gone falls by 1 after as many years as its
strength, until it is gone.

**See also:** [A neighbour](help:neighbour)

## Regio Levels
<!-- help: section-nb-levels -->

The regio's levels, deepest first, over its surface. Each has a name, a
realm and an aura, how to see it and how to enter it, and notes. Write
the roll to see or to enter it as "Per + Awareness against 9" (a
Characteristic, an Ability and the number to reach): the list then
shows which of the player covenants' characters reach it with their
scores alone, best first. Anything else is kept as a sentence ("walk the
path backwards at dusk"). Add puts a new level above the deepest; edit
or delete one.

## Effects
<!-- help: section-nb-effects -->

What the place does to those in it, at every level, one level, or a
level and those above it:

- **Lab totals**: added to the Lab Totals of the laboratories there, for
  the Art named (or every Art).
- **Aging rolls** and **Living Conditions**: added to the aging rolls of
  the characters who live there (their covenant is there).
- **Warping**: Warping Points a season for those who live there, added
  each year with the rest of their Warping.
- **The aura**: replaces the aura of the levels it covers, in the realm
  named.

Add, edit or delete one.

## Triggers
<!-- help: section-nb-triggers -->

What comes at the place, and when: **once** (a season and year), **each
year** (a season), **every N years** (a season, and a year it comes),
or **whenever** something happens (say what in What happens). The
dated ones show their next date, and the soonest is the place's Next.
Add, edit or delete one.

## Roll Tables tab
<!-- help: tab-nb-tables -->

The place's roll tables: what the troupe might meet there, or what a
night in the regio brings.

## Roll Tables
<!-- help: section-nb-tables -->

Each table names its die (a simple die, a stress die, a d6 or a d10)
and its rows, one a line: "1-3: Nothing stirs", "4: A hare", "9+: The
Hall opens", and for a stress die "botch: The mist closes".

<!-- tui -->
More (`m`) > **Roll** rolls the chosen table and shows the row it lands
on; **Write** puts it in the place's diary.
<!-- /tui -->
<!-- gui -->
**Roll** rolls the chosen table and shows the row it lands on; **Write**
puts it in the place's diary.
<!-- /gui -->

Add, edit or delete one.

## Diary tab
<!-- help: tab-nb-place-diary -->

What has happened at the place.

## Diary
<!-- help: section-nb-place-diary -->

What has happened at the place, or what the faction has done, a line
each, with the season it happened: for a place, the rolls on its tables
and the aura rising; for either, anything the storyguide writes. Add,
edit or delete an entry.
