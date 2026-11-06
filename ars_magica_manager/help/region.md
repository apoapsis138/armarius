# The Region
<!-- help: region -->

<!-- tui -->
The Region is the saga's world beyond the troupe's covenants: the
Tribunals, the covenants the troupe doesn't play, and the neighbours
(the lords and towns, the Church, the universities, the factions and
the threats around them), each with its attitude toward the troupe.

In the navigation tree The Region sits under the troupe's covenants.
Each Tribunal is listed there, with the covenants the troupe doesn't
play under the Tribunal they belong to (a covenant with no Tribunal sits
directly under The Region), then a node for each group of neighbours
with the neighbours in it. Selecting The Region, or a group, shows the
Region sheet (its Neighbours tab of lists, and its
[By Place](help:tab-region-by-place) tab); selecting a neighbour shows
its own sheet.

Press `n` (New) here, or on the saga, and choose **New Tribunal** or
**New Neighbour**. A covenant joins a Tribunal through the Tribunal
choice in Edit Covenant.
<!-- /tui -->
<!-- gui -->
The Region is the saga's world beyond the troupe's covenants: the
Tribunals and the neighbours (the lords and towns, the Church, the
universities, the factions and the threats around them), each with its
attitude toward the troupe.

On the saga's page, The Region chapter opens with the Tribunals as
cards, each opening its own page, and a New card that adds one. Under
them come the Region's facts, then each group's neighbours as cards,
with their own New card, or the Region [by place](help:tab-region-by-place). The covenants are in The Covenants, whether
the troupe plays them or not.

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

## Merge Doubled Records
<!-- help: merge-doubles -->

Before a character or a creature could hold an attitude, someone the
troupe dealt with (a faerie knight, a hedge witch) was often entered
twice: as a faction, to carry the attitude, and as a character or
Bestiary creature, for the stat block. **Merge Doubled Records** finds
each faction whose name exactly one character or creature has, and
makes the pair one record: the character's or creature's.

The form lists each pair, ticked, with what merging brings. Untick any
that are two records on purpose, then choose **Merge**. For each pair
ticked:

- Its attitudes, favours and links move to the character or creature
  (an attitude toward a covenant the record already has one toward is
  left as the record's).
- Its summary, and its rules, wants, offers and diary, are added to the
  character's summary or the creature's notes; its Secrets to theirs.
- The factions it was a member of, and the neighbours it ruled, now name
  the character or creature. A creature takes its place and its map
  pins; a character's pins are left off (the Atlas shows him at his
  covenant's).
- The faction itself is deleted.

Only factions are offered: a lord, a threat or a place named for its
person (the Ash of Nortorf, the story and the spirit) keeps rules of its
own and stays a record apart.
<!-- tui -->
It is in More (`m`) on the saga or The Region while there is a pair to
merge.
<!-- /tui -->
<!-- gui -->
It is a button beside the Neighbours heading of The Region while there
is a pair to merge.
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
itself), to one **kind** (lords, towns, places...) and, once a place
names one, to one **Tribunal's lands** (whatever lies in them, member of
that Tribunal or not; see [A place](help:tab-nb-place)). Each list's title
then says how many it shows of how many. The filter stays while the
app is open.

<!-- tui -->
The Region's facts say what the lists are narrowed to ("Showing"). Press `/` (Filter) on any of the lists and choose a Tribunal's lands, a
region, a kind, or any of them; blank them all to show everything again.
<!-- /tui -->
<!-- gui -->
Choose them in the quiet drop-downs at the right of the first list's
heading ("Show: Every Tribunal, Every region, Every kind"; the Tribunal
one shows once a place names a Tribunal's lands); set them back to Every
to show everything again.
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

The stories that grow if left alone (the core rules): each one's
**Clock** (how far it has come, a filled square for each stage come or
each step taken), its next stage and when, and its attitude. Add, edit or
delete one. A story not yet begun shows as **Dormant**: open it and
choose **Begin This Story** in More to start it.

### Open Stories
<!-- help: section-region-stories -->

Every open Story Event of the troupe's covenants, oldest first: what it
concerns, the covenant whose Diary keeps it, and the season it arose.
An experiment's story event, a Disaster's covenant story and Suggest a
Story write one, and you add them by hand in a covenant's Diary (as a
Story Event). Edit opens its Diary entry: mark it **Resolved** once it
is told, and it leaves the list (resolving asks for its last chapter).
**Take Up the Tale** writes a chapter of what the troupe did; a story's
chapters show under its words. The Seasons page's
[Needs You](help:section-attention) lists them too, those whose Revisit
year has come first.
<!-- tui -->
More (`m`) > **Grow into a Threat** makes the chosen story a threat of
the Region (see [Grow into a Threat](help:grow-story)).
<!-- /tui -->
<!-- gui -->
**Grow into a Threat** on a story's card makes it a threat of the
Region (see [Grow into a Threat](help:grow-story)).
<!-- /gui -->

### Places
<!-- help: section-region-places -->

The forests, ruins, crags and regiones of the region: where each is,
its aura, how many regio levels it has and how far the troupe has got
with it. Add, edit or delete one; see [A place](help:tab-nb-place).

A place's form also has **Waters** (Open water, Anchorage or Port), which a ship's stops use (the book packs mark theirs, and a port town has a harbour Place beside it), and **Travels with**, for a place that moves with a covenant, as a ship does. See **How to keep a covenant on the move**.

## By Place
<!-- help: tab-region-by-place -->

The Region as the land rather than as lists: each place that sits inside
no other (the Black Forest, the Rhine Valley), then what rests on it (its
lords, towns, churches, factions, threats, the covenants there now and
the creatures found there) and the places inside it, each indented under
the one it sits in, however deep. Each line says what the record is (a
place's aura, a neighbour's kind and attitude). What is placed nowhere
comes last. Click a name to open its record.

<!-- tui -->
It is the Region's **By Place** tab, beside Neighbours.
<!-- /tui -->
<!-- gui -->
Choose **By place** in the chips under the Neighbours heading of The
Region; **By kind** brings back the lists. The choice stays while the
app is open.
<!-- /gui -->

The same records, in another order: nothing is moved, and a place's
**Inside** (Edit) is what puts it under another.

### The land
<!-- help: section-region-by-place -->

Each place, what rests on it and the places inside it, every name a link
that opens its record (see [By Place](help:tab-region-by-place)).

### Customs and Lore
<!-- help: section-region-customs -->

How the land lives, as a book's background describes it: its honour and
kin, its tongues and manners, its law and its things, its trade and
roads, a treaty or a legend. Each says where it belongs and the first
line of the rules it brings (hof and ohof among the Icelanders, the
Baqt between Egypt and Nubia). A custom holds no attitude toward the
troupe. Add, edit or delete one; see [A custom](help:tab-nb-custom).

# A custom
<!-- help: tab-nb-custom -->

A custom is the land's lore rather than a company: what the people of a
place do and believe, how they trade, judge, speak and travel. New
Custom and Edit record:

- **Its rules**: what it means in play, with the book's page (a Virtue
  it favours, a roll it changes, a law the troupe must keep).
- **Wants** and **Offers**: what those who keep it ask of the troupe,
  and what it gives them, when the book says.
- **Ruler or leader**, shown as **Kept by**: a person who keeps or
  presides over it (Viscountess Ermengarde over her Courts of Love).
- **Place**: where it holds, so the Region [by place](help:tab-region-by-place)
  lists it under that land.

It has no attitude, detail or liege, as a place has none. Its Found Here
tab shows the favours and links that name it.

**See also:** [A neighbour](help:neighbour)

# A neighbour
<!-- help: neighbour -->

A neighbour is a lord, a town, a church, a university, a faction, a
threat, a place or a custom of the saga's region. Only its name is needed; the rest can be
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
  and gazetteer (see [A place](help:tab-nb-place)); a custom's rules
  (see [A custom](help:tab-nb-custom)).
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
On the desktop, **Edit** sits beside the neighbour's name at the top of
its page.

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
[Links](help:section-links). A place or a custom holds no attitude: its tab is
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
- **Mercenary budget**: what he may spend on mercenaries a year, once
  his household and his knights are paid (Lords of Men p. 103): 0 if
  poor; a landed noble 2 (5 if wealthy), a baron 40 (100), a count 100
  (250), a duke 250 (500 or more). It is not the 10 or 20 pounds a
  landed noble has for largesse and war together (p. 31).
- **Free time**: a landed noble's free seasons a year, as Lords of Men
  gives them: 1 if poor, 2, or 3 if wealthy (p. 31). The Definitive
  Edition's Landed Noble has no free time beyond the usual, and a poor
  one none (DE p. 89).
- **Army**: the knights, serjeants, infantry and levies his title
  raises.
- **Owes** and **Aids**: when he answers to another neighbour, what he
  owes it: a knight's service for 40 days for each manor, or 2 pounds
  scutage a knight; aids of a pound a manor; and his heir's relief, a
  year's income but at most 5 pounds a manor (100 for a baron or
  greater).

Where Lords of Men gives two figures for the same thing, the lower is
used: a landed noble's spending money, a duke's knights and scutage.

**Affinity** is the lord's bonus to social rolls among his region's nobles,
land-holding churchmen and the councils of towns without a royal charter:
mustering the local knights, settling their disputes, swaying their advice,
refereeing a tournament (Lords of Men pp. 21-22). It is +1 for a
landholding noble of banneret stature, +2 an officer or baron of a minor
lord, +3 an officer or minor baron of the king, +4 a greater baron, +5 the
senior noble under the king in the region, and half that, rounded down,
where two warring affinities divide his country. Left blank on the lord's
form it follows his title (a landed noble of five manors or more +1, a
baron +2, the lowest of the barons' standings, since the title doesn't say
whose baron he is; a count or duke +5); choose a standing to set it, and tick
**divided** to halve it. A lord who neglects his affinity loses some of
it: lower the standing.

His manors are the rows on his Manors tab, or, while it lists none, the
count on his form; his income is 20 pounds a manor (LoM p. 72). His
surplus is Chapter Three's own figure, not his income less his costs: a
landed noble none, 10 or 20 pounds a year by his wealth (p. 31); a baron
none, 40 or 100; a count 100 or 250 (p. 32); the book gives none for a
poor count or for a duke. A greater baron's expenses are 400 pounds or
more a year, about 20 manors (p. 32).

**See also:** [A neighbour](help:neighbour)

## Manors tab
<!-- help: tab-nb-manors -->

A lord's manors, his kennels, mews and stables, and his household (Lords
of Men, Chapter Six, pp. 71-87; Chapter Five, pp. 58-61; Chapter Two, pp.
9-12). His Fief tab counts the manors listed here, 20 pounds a year each;
the count on his form is used only while none is listed.
<!-- tui -->
Choose a manor or an establishment to see it in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a manor or an establishment to see it in full in the inspector.
<!-- /gui -->

### Manors
<!-- help: section-manors -->

Each manor: its acres (about 600, a third more or less without being
unusual, LoM p. 72), how it is farmed (large fields, turned over to
sheep, or another way, pp. 72-73), its land by use (demesne, rented,
villeins, glebe and waste, p. 75), and whether it is an allod, held with
no lord above it (p. 85). Every manor yields its lord 20 pounds a year; a
mill or bakery it holds by custom is already inside that figure, so its
tick adds nothing (p. 85). The panel shows its peasant land: hides
(120-144 acres, 4 pounds to the lord), virgates (24-32 acres, a family
worth about a pound a year), bovates (half a virgate) and cottars (ten
acres or less), with the usual spread of 20% virgaters, 30% bovaters and
50% cottars (p. 72); its demesne flock, 600 sheep, over 1,000 on
marshland and 300 in wooded land, two-thirds of the manor's sheep, and
the swineherd's pigs, a quarter of the flock; and its crops, a winter
crop sown at 2 bushels an acre reaping 8, a spring crop 4 reaping 16 (p.
76). The manor court's fines and dues (entry fine, heriot, mortuary,
tallage, merchet, leywrite, childwrite, fines for celibacy and for being
fined elsewhere, pp. 79-82) are ticks and a line of notes: the book gives
no sums, and tallage may be as high as the lord wishes. Add, edit or
delete a manor.
<!-- tui -->
More (`m`) on the Manors list:
<!-- /tui -->
<!-- gui -->
The Manors list's own buttons:
<!-- /gui -->
**Buy a Manor** adds one at its price: 30 to 50 times its 20 pounds a
year, 600 to 1,000 pounds, less if the seller keeps some of its rights or
you take on its dues, better for coin in hand, more when his lord takes a
cut (p. 85); a covenant may pay it from its Wealth, and a lord from his
**Coin in hand** (on Edit Lord), or else by installments from his yearly
surplus, which the result counts in years. **Assart** clears the
chosen manor's waste: a strong laborer with proper tools clears an acre
of lightly wooded land a month doing nothing else (p. 84, errata p. 74);
villeins clearing between their duties are much slower, and land cleared
by magic overnight alarms the neighbouring lords, so type the acres
cleared for either.

**The Hunt** (More, on the chosen manor) rolls a day's hunt there.

- *Hunting with hounds* (Lords of Men pp. 51-53). Before dawn each
  huntsman quests with a lymer: Perception + the lower of his and the
  lymer's Hunt against 9 to track a fit beast, Presence + Animal
  Handling against 9 to keep the lymer quiet, Intelligence + Hunt
  against 9 to judge its age and condition. At the assembly the hunters
  read the droppings (Perception + Hunt against 12). The book calls none
  of these stress rolls, so all take a simple die: it names a stress die
  wherever it wants one. Then the chase, an hour a round: the pack's
  Pursuit Total (the best dog's Perception + Hunt + its +2 to Hunt rolls
  + a stress die, less the pack's Fatigue) against the quarry's Evasion
  Total (Dexterity + Athletics + the Terrain Bonus + a stress die, less
  its Fatigue). Four rounds won by either side, not necessarily in a row,
  corner it or lose it; a tie counts for neither, and nightfall ends the
  chase with the quarry escaping. The book counts Fatigue only as a
  penalty to each total, so a quarry or pack spent past its last Fatigue
  level (cornered, or giving up) is the app's gap-fill, and the Diary
  says so. The hounds and the quarry each lose a Fatigue level an hour
  unless Stamina + Athletics + a simple die makes 12. Each hunter rolls
  Dexterity + Ride + a stress die against 6 an hour or falls behind, and
  Stamina + Ride + a simple die against 9 every three hours or loses a
  Long-Term Fatigue level (p. 52).
- *The Terrain Bonus* (p. 53) starts at +6 for a beast on its own ground.
  The relay's huntsmen roll Intelligence + Hunt + 6 + a stress die
  against the Evasion Total for fresh dogs, then Intelligence + Area Lore
  + a stress die to take 1 off it; each hunter still with the pack rolls
  Perception + Area Lore + a stress die to take 1 more off.
- *The quarry* (p. 54): the hart (spring and summer), the boar (summer and
  autumn), the bear (any season but spring) and the wolf, by the
  Definitive Edition's stat blocks; the hare (p. 58); and any beast of the
  saga's Bestiary. A dangerous beast's kill is fought out as a melee.
- *Hawking* (pp. 57-59): the hawker's Presence + Animal Handling + a
  simple die (the Gift's penalty applies) on the book's table; 7 or more
  and the bird strikes at the prey (p. 58's table), with a bonus as the
  roll rises; 0 or less and a Loyalty check (a simple die against 6), or
  the bird is gone for good. At 21 or more it goes on attacking after the
  first strike, hit or miss. The book sets no limit: the app stops it on
  a kill, and after five strikes by its own limit, not the book's. A goshawk
  or merlin won't stoop at prey too large unless trained to it (p. 59).
- The inspector shows the holding's kennels or mews (a hunt needs a dozen
  running dogs and a lymer, p. 60) and a lord's hunting rights. Hunt
  writes the day in the Diary of each hunter and huntsman named and of the
  lord or covenant, and takes the Long-Term Fatigue it cost.

**Area Lore** (More, on the chosen manor) rolls Intelligence + Area Lore
(a simple die) against a line of City & Guild's Area Lore Ease Factors
(p. 83): from a hunting spot or a major inn at 6 to smugglers and faerie
trods at 18. One who lives in a town subtracts 3 seeking in the
hinterland, one who lives in the country 3 in the city (p. 82). Success
means he knows where it is or whom to ask; Charm or Bargain win it. It is
written in his Diary.

### Establishments
<!-- help: section-establishments -->

Kennels, mews and stables (LoM pp. 58-61). Each quality has its capacity,
maintenance, staff and Living Conditions for the animals (p. 60; the
Excellent stables as the errata moves the row: 40 horses, 3 pounds a
horse, 12 staff, +2, errata p. 74), and up to a third again of the
capacity may be young and breeding stock (p. 58). A stable that befits
its owner costs nothing: a knight's Standard, an earl's Excellent; the
app takes a landed noble's to be Superior and a baron's, count's or
duke's Excellent, and a covenant pays for anything better than Standard.
Kennels and mews always pay (p. 59). Superior and better need a
specialist (a marshal, falconer or master of kennels), and a positive
Living Conditions needs one with the Profession at twice it, or someone
with Animal Handling three times it giving the establishment a season a
year (pp. 59-60). Marking a year's upkeep unpaid drops the establishment
a class at once, and each season it stays unpaid it loses 15% of its
animals, rounded up, as the season ends (p. 59). A covenant's upkeep is
not counted in its Treasury: enter it with the covenant's expenditure if
it pays it.
<!-- tui -->
More (`m`) > **Winter Roll**
<!-- /tui -->
<!-- gui -->
**Winter Roll**
<!-- /gui -->
on the chosen establishment, once a year in winter: a stress die +
Intelligence + Animal Handling, or + Profession: Marshal, Falconer or
Master of Kennels, against 9. A failure drops it a class until a success
in a later year brings it back one; its maintenance stays as it was. A
botch is a catastrophe: a fire, disease among the animals, theft, or a
story to resolve (pp. 60-61). Add, edit or delete an establishment.

### Household
<!-- help: section-household -->

His household (LoM pp. 9-12): its size (loosely, a lord of the manor
about 10, a landed knight 16, a banneret 24, a baron 40, an earl 140,
his mesnie's knights counted in it), his mesnie of household knights (a
wealthy lord keeps eight to ten), his heirs, the custom his lands pass by
(to the heir he names, or the eldest, or the strongest his liege
chooses; or divided between his sons; with no son, where the eldest
takes all, local custom decides whether a daughter takes the land intact
or it is divided between the sisters or their husbands, and where land
is split between all the siblings, daughters inherit alongside their
brothers, DE p. 512; LoM p. 10 agrees), the relief his heir owes his
liege, and his hunting rights:
warrens, chases and parks are his alone, forests the king's (pp. 48, 79).
Edit Household changes them.
<!-- tui -->
More (`m`) > **Settle an Inheritance**
<!-- /tui -->
<!-- gui -->
**Settle an Inheritance**
<!-- /gui -->
passes the lands to his heir: the heir becomes the record's ruler, the
relief owed his liege is noted, divided lands are shared out among the
heirs (give each heir's manors a record of their own), a widow keeps the profit (not the income) of a third of his land until
she remarries (DE p. 513, which wins over LoM p. 11's third of his
estate; ticked already when his last marriage on the Marriages tab
stands, or ended with his death), and his Diary keeps it.

## Marriages tab
<!-- help: tab-nb-marriages -->

A lord's family's marriages and betrothals, and the terms of the one that
stands, with what follows from it (Lords of Men pp. 10-11). A marriage is
kept once and shown on the page of each house it joins: the bride's and
the groom's, and a lord who marries shows it on his own.
<!-- tui -->
Choose a marriage to see it in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a marriage to see it in full in the inspector.
<!-- /gui -->

### Marriages
<!-- help: section-nb-marriages -->

The marriages joining his house: the spouses (his own family's first),
when, the dowry, and where it stands: betrothed, married, ended by his
death or hers, or separated. Arrange a Marriage adds one; edit or delete
one.
<!-- tui -->
More (`m`) > **End a Marriage**
<!-- /tui -->
<!-- gui -->
**End a Marriage**
<!-- /gui -->
records how the chosen one ends.

### The Terms
<!-- help: section-nb-marriage -->

The marriage that stands (or the last one), named for the couple: the
bride and groom (with their ages, from their sheets), the custom that
governs the dowry, the dowry (or a dower, for an heiress), the consents,
and what the Church asks: only a spoken intent and a dowry, though it
prefers a priest and two witnesses (LoM p. 10). **What follows:** an
heiress keeps her own fief while married, except in England, where her
rights become her husband's (DE p. 512); her dowry is managed, kept or
taken by her husband as the custom says (LoM p. 11); a widow keeps the
profit, not the income, of a third of his land until she remarries (DE
p. 513; Lords of Men's "a third of his estate" gives way to it); if they
part, a dowry goes back to her family. A warning shows when her father
withholds his consent (in many places that stops it, though no Christian
father may choose her husband, LoM p. 10), when she hasn't consented
(then there is no sacrament), and for close kin or bigamy. Edit Terms
edits it.

## Arrange a Marriage
<!-- help: arrange-marriage -->

Who marries whom (a character of the saga, a lord of the Region, or a
name typed in), the houses whose pages show it, when, and whether they
are betrothed or married. Then the bride's family, which sets her dowry:

- **Noble** (LoM p. 11): an equal share of her parents' land between
  their children; in the French sphere the eldest son and his patrimony
  both come out of the division: enter the patrimony, count all her
  parents' children, and the eldest son is left out of the sharing. The
  book then lists what makes a dowry larger or smaller and
  gives no figures: tick the statements true of her (her groom's family
  is wealthier, she is one of many acceptable brides, not a virgin, less
  than ten years younger than him, will receive nothing after, has fewer
  siblings than most, mostly brothers, will find it hard to get money from
  the heir, is paid in other rights rather than land or money); each
  ticked makes it larger, each not smaller. The Contract works out the
  share and counts them; the troupe settles the figure and types it as the
  dowry agreed. An heiress brings no dowry: the groom's family may pay her
  father a dower instead.
- **Merchant** (City & Guild p. 113, as the errata p. 57 corrects it):
  her father's Social Status the same as the groom's, or one level
  higher, pays 10 times his yearly profit divided by his children (married
  daughters left out), as Mythic Pounds, larger or smaller by the same
  statements, except that hers is larger paid in assets (land or goods)
  rather than money, and two more (paid in instalments; her parents would
  seem richer than they are). Two levels higher, he raises the groom instead: a
  Poor member of the status just below the father's, his surplus Labor
  Points lost. A daughter who will inherit the business likely brings no
  dowry.
- **Peasant**: no figure in the books. Serfs of different lords need
  their lord's leave, bought with merchet, more for a large dowry or when
  she moves to her husband's lord's manor (LoM p. 81); the manor court
  keeps it.

The custom for the dowry is each marriage's own: Italy, or much of
France (in both he manages it but may not spend it, may be sued for
mismanaging it, and gives it back if they separate; only Italy's sends it
to her children or her parents if she dies first, and for France the
books are silent, so the troupe decides), parts of France (he may keep
much of it),
England (everything she has becomes his), or another the troupe sets
(LoM p. 11). Her consent is needed for the sacrament; her father's where
custom asks it. Marriage between close kin (since 1215, those sharing a
great-great-grandparent) and bigamy are canon crimes (The Church p. 37;
LoM p. 82). A marriage blessing is a petition at Ease Factor 3 (The
Church p. 47). **The Contract** says all this as you fill the form in.

## End a Marriage
<!-- help: end-marriage -->

How the chosen marriage ends, and when. **He dies first:** she keeps the
profit (not the income) of a third of his land until she remarries, and,
landed at her marriage with no adult sons, likely her own lands outright
(DE p. 513); when he is a lord of the Region, Settle an Inheritance
follows with his widow ticked. **She dies first:** her dowry goes to her
children or back to her parents (Italy), or the troupe decides (much of
France: the books don't say), or he may keep much of it (parts of
France), or it is his already (England); her own fief goes to
her eldest son where the eldest takes all, or to one of her sons where
land is divided (DE p. 512). **They separate** (or it is annulled):
separation, not divorce, is allowed in many places for infidelity; her
dowry goes back to her family, in part or whole, and among nobles this
can start a feud (DE p. 148; LoM p. 11). Annulling a marriage of common
folk is a petition at Ease Factor 9 (The Church p. 47). Both families'
Diaries, and the spouses' own, note it.

## Castles
<!-- help: section-nb-castles -->

His castles, each with its garrison, defences and supplies. Add, edit
or delete one.

## Gratitude
<!-- help: section-nb-gratitude -->

The Gratitude he owes each character who has served him: a story that
serves his interest earns 1 point (2 if it was the story's aim), a
renowned feat 5. Each line says what its points are enough for: 5 for
freedom or knighthood, 10 for a manor of one's own, 20 to become a
baron of the king. Add, edit or delete one.

<!-- tui -->
**Redeem Gratitude** (More, `m`, on the chosen debt)
<!-- /tui -->
<!-- gui -->
**Redeem Gratitude** (the row's Redeem Gratitude button)
<!-- /gui -->
spends the points the lord owes for a reward
from Lords of Men's Advancement Requirements Table (p. 8): serf to freeman,
warrior to knight, knight to bacheler or bacheler to carissimus for 5;
a manor, added manors, banneret to baron of a minor lord, appointment as
baron, or an officer's post under a greater baron for 10; minor baron to
baron of the king for 20; or money and goods for whatever the troupe
agrees. Most steps also ask a story event, a Reputation for loyalty or an
office's Abilities, which the form names but leaves to the troupe. The
points come off the debt, the reward is written in the lord's Diary and
the character's, and a step that brings a Social Status Virtue (Knight,
Landed Noble, Great Noble, Temporal Influence) says so: add it to the
character's Virtues yourself (Lords of Men p. 7).

## Battles
<!-- help: section-nb-battles -->

The battles he fights, on either side, played as Lords of Men plays
them: a few heroic events, each with a player character at its heart,
rather than every blow. A battle is kept once, in the saga's
[Conflicts](help:conflicts), between two armies: each a lord, town or
other power of the Region, or a covenant, or just a name. So a battle
between two lords shows on both their Fief tabs.

Each line shows the two armies in combat groups of five men, the first
army's **Ground** (Territorial Advantage: its commander's Deployment
Total less the other's) and its **Numbers** (Weight of Numbers: +1 with
half as many groups again as the other, +2 for twice as many, +3 for
three times, +4 for four times or more; as much below 0 when
outnumbered), and the events it has won and lost so far. Add, edit or
delete one. Added here, a battle's first army is this lord. An army's
groups left blank are filled in from a lord's title (his knights,
serjeants, infantry and levies, in groups of five), to which you add
his allies and mercenaries; blank baggage is as much as the army
needs. The form asks whether each army fights on its home ground: only
then does a lord's title raise his levies (Lords of Men pp. 31, 102).

A Deployment Total is Intelligence + Area Lore + a stress die, the
commander's own or a lieutenant's, plus the magnitude of any spell that
shapes the field in his favour.

**At sea: a fleet battle.** Set *Fought* to *At sea* and the battle is
fought between fleets (Tales of Power p. 106). Each army then ticks its
ships: when an army is a covenant, every ship on its Inventory (Possessions in the terminal) is
listed (all ticked at first; a wrecked one is left out of the count), and
*other ships* counts those kept on no covenant's Inventory (a pirate
fleet, ships hired). Weight of Numbers counts ships, not combat groups: 3
ships against 2 is +1 (Lords of Men p. 105's ratios). Combat groups left
blank are the picked ships' crews and fighting men in groups of five.
The *pilot* (anyone with a seafaring Profession) replaces Area Lore in the
Deployment Total: Intelligence + his Profession + stress die (ToP p. 106);
the inspector shows the sum to roll against. *Bearded* ships (iron plates
on the bow) are appreciably slower, but the plates are armour: the ship
is more resistant to damage, and it rams and takes collisions better.
The book gives no figure, so the storyguide sets the bonus in an event
(ToP pp. 106, 110). Boarding
is fought much as on land.

## Sieges
<!-- help: section-nb-sieges -->

The sieges he lays, or holds out in, kept in the saga's
[Conflicts](help:conflicts): each a siege whose besieging lord, or whose
castle in the Region, is this lord. Each line shows the castle and its
besieger, the Garrison, Defenses and Supplies, and how long it has run.
Add, edit or delete one. Added here, he is the besieging lord: link the
castle to the lord, town or place he besieges. A garrison or besiegers'
soldiers left blank are filled in from the linked lords' armies. Play
it from Conflicts with Next Siege Event; see [A siege](help:sieges).

## Combat Options
<!-- help: combat-options -->

More (or the button) on a fight: Lords of Men's optional combat rules
(Chapter Nine) worked out for one of its characters, to play at the
table. It changes nothing in the fight. Choose the **Option**:

- **A charge, and its shock** (on foot p. 123, mounted pp. 126-127): the Combat Ability added to
  the Attack and the Fatigue it costs (the horse's, mounted), and what
  the one charged rolls to resist its shock.
- **A horse's gait** (p. 127, with the Errata's corrected table, p. 75):
  its missile penalty, falling damage, extended-action Ease Factor and
  optional Defense bonus.
- **Cover, concealment and higher ground** (pp. 130-131).
- **How many may attack one man** (p. 131).
- **Interrupting** (p. 119): Quickness + the Ability - Encumbrance.
- **Into and out of the saddle** (pp. 127-128).

Add Combatant also offers **A standard combat group** (p. 108): five
knights, serjeants, infantry, archers, levies or baggage with the book's
figures, formed into a group as they are added: trained for knights,
serjeants and infantry, untrained for the rest.

## Muster and Aftermath
<!-- help: battle-muster -->

More (or the button) on a battle, for what comes before and after its
battlefield events (Lords of Men, Chapter Eight):

- **A crusade** (p. 104): tick it on Raise Allies for a churchman with
  Senior Clergy: the Affinity is the most prominent noble's of his
  diocese, rolled on the Allied Troops Table. The book names an Army Size
  Table that doesn't exist, and Holy Influence (Realms of Power: The
  Divine p. 38) has no Affinity in it, so this is the app's reading.
- **Raise Allies** (pp. 102-103): who calls them, his Affinity score and
  his core vassal groups (his lord's title gives them, levies only on home
  ground), and the Allied Troops Table's modifiers that apply. Presence +
  Leadership + Affinity + a simple die: 6 adds half his core force, 12 as
  much again, 18 double, 24 treble. The allies join the side.
- **Hire Mercenaries** (pp. 103-104): groups of knights, serjeants,
  infantry, archers and levies at 15, 5, 2, 2 and 1 pounds, up to the
  lord's Mercenary Budget. **A War Loan** steps his wealth down for five
  times the budget he gives up: an Average lord becoming Poor borrows five
  times his budget; a Wealthy one becoming Average gains five times the
  difference of the two, or becoming Poor five times the Wealthy budget. A
  Poor lord can't borrow. The loan and his new wealth's budget are what he
  may spend: the book doesn't say, but its "five times the difference"
  points that way, and it makes the two routes to Poor come out the same
  (for a baron, Wealthy to Average is 300 + 40 = 340 pounds). He needs a
  banker able to lend that much and to collect if he defaults, and the
  loan may take weeks, so it doesn't suit a lightning war. The loan is
  repaid from spoils or stories; whether it lowers next year's budget,
  and when he regains his old wealth, the book leaves to you, and the app
  doesn't restore it.
- **Roll a Deployment Total** (pp. 104-105): Intelligence + Area Lore + a
  stress die for the one who chooses the ground, plus the highest
  magnitude of a spell that shapes it.
- **End of the Day** (pp. 108-109): a side wins, or a truce holds at
  nightfall. The victors who led events gain a Confidence Point for each
  event their side won, and their commander an experience point toward a
  Reputation. No more events follow.

A side keeps the groups it raised or hired by kind, so an event's losses
come first from the kind its Enemy names (levies for Inexpensive, infantry
and archers for Standard, knights and serjeants for Expensive, p. 106).
Leading an attack on the baggage gives 1 xp toward a bad Reputation. A
magus casting in a battle makes a Concentration roll against 12, or 9 if
not yet engaged (p. 109): roll it at the table.

## Battle Event
<!-- help: battle-event -->

<!-- tui -->
More (`m`) > **Battle Event** plays the chosen battle's next event.
<!-- /tui -->
<!-- gui -->
**Battle Event** plays the chosen battle's next event.
<!-- /gui -->
Choose the character **Leading the event** and the army they are
**Fighting for**, then its **Maneuver**
(Defend +0, Attack +1, Run the Gauntlet +2, Take +3, a Heroic Gesture
+4), its **Enemy** (Inexpensive troops such as levies +0, Standard +1,
Expensive such as knights +2, Special +3, the Baggage +4) and its
**Size** (Lesser +0, Even +1, Outnumbered +2, Overwhelmed +3, I Stand
Alone +4). The line above Record shows the Event Total: the character's
Stamina + Leadership + their army's Ground and Numbers + those three,
+1 for giving up the initiative. It must reach the stage's Ease Factor to be won at all:
9 for the first event (Engaged), 12 for the second (Advantage or
Setback), 15 for the third and any after (Imminent Victory or Defeat).

Tick **Play it out as a fight** to have the event made into a fight on
Conflicts (Lords of Men pp. 105-108): the leader and his own group (**His
group**, from the Standard Combat Groups table, p. 108) against the
groups the Size sets (Lesser: one about half his; Even: one;
Outnumbered: two; Overwhelmed: three; I Stand Alone: he alone against a
full group) of the troops its Enemy names (**Their troops**: levies,
infantry or archers, knights or serjeants, the Baggage guarded by
levies; a Special enemy is the storyguide's to add with Add Combatant).
Weight of Numbers adds as many men to each group of the side it favours;
knights, serjeants and infantry fight as trained groups. The leader
fights with the first weapon he carries (Edit Combatant changes it).
Play it, five rounds unless the event says otherwise, then open Battle
Event again: it is filled in as you left it, and the line above Record
says what the fight showed.

Then say **How it went** by the Maneuver's own condition (pp. 106-108):
a Defend is won by beating the attackers or holding for the rounds set;
an Attack by defeating or routing them; Run the Gauntlet by reaching its
objective; a Take by taking it and holding it against the counter-attack;
a Heroic Gesture is won if its leader dies (or survives meeting the
storyguide's conditions), and lost if another player character is
killed. **Record**. The side that lost loses the groups the fight cost
it, and as many more as the event's Size times the winner's Numbers,
when the winner has the greater army; the next event's Numbers are
worked out from what is left. After an event, type the losing
commander's **Morale** roll (Presence + Leadership + a stress die,
against 6) and, if it fails, his **rally** at the next event (against
9). A failed rally disorders his army; a second, while it is still
disordered, routs it and ends the battle (Lords of Men p. 106). While an
army is disordered, the next Battle Event offers **A rally by** a player
character who takes command: his roll (Presence + Leadership + a stress
die against 9, p. 135), or a story event played for it, won or lost. A
rally lifts the army a step, routed to disordered, disordered to steady.
With Morale and Discipline on, a disordered or routed army's groups start
its event's fight that way (see [Discipline, Morale and
rallying](help:group-morale)). Each event recorded is
written as a line in the Diary of each army's lord or covenant (see
[A lord's Diary](help:tab-nb-lord-diary)) and of the leading character.

When the lord raises his army, his allies add a share of his own forces
for a Presence + Leadership + Affinity roll (6 half, 12 as many again,
18 double, 24 treble), and mercenaries cost 15 pounds a group of
knights, 5 of serjeants, 2 of infantry or archers and 1 of levies. Every
ten groups need a group of baggage, and each one short is -1 to the
Event Totals.

**An event at sea.** In a fleet battle the event is told at sea: cutting
off part of their fleet, boarding their flagship, bringing down the mast
that flies their signals, intercepting them with swift ships, or another.
Tick the ships *engaged* in it (and how many of each army's other ships):
at first every ship, later the ones engaged last time. Only the engaged
ships count for this event's Weight of Numbers, so beating part of their
fleet alone pays (ToP p. 106); the losses it causes use that figure. *They
throw naptha bombs*: +5 damage, and the ship is set alight; water won't
put it out, a great deal of sand will (ToP p. 110).

# A town
<!-- help: tab-nb-town -->

A town (City & Guild) has a charter (granted by a noble lord, the
Church, or held by its townsmen as a commune; or a faerie's or a
demon's), a council and a population, entered on New Town or Edit. Its
Town tab shows them with its size (a small, medium or large town, or a
city) and how many guilds a town its size has in the saga's year (C&G
p. 54), then its fairs and markets. Its charter in full, its guilds and
its court have tabs of their own: [Charter](help:tab-nb-charter),
[Guilds](help:tab-nb-guilds) and [Court](help:tab-nb-court).

**See also:** [A neighbour](help:neighbour)

## Charter tab
<!-- help: tab-nb-charter -->

The town's charter (City & Guild, Town Charters, pp. 8-14): who granted
it and how they hold it, its terms, what it gives, the saga's characters
who are its citizens, and the town's size and people.
<!-- tui -->
Choose a lord or a citizen to see him in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a lord or a citizen to see him in full in the inspector.
<!-- /gui -->

### Lords
<!-- help: section-nb-charter-lords -->

Each lord of the charter: a noble, the Church, a faerie or a demon, how
he holds it, his share of the revenue (in words) and since when. **Sole**:
he holds it alone. **Shared (paragium)**: lords granting in partnership,
splitting the revenue by an agreement older than the charter (p. 10).
**Rival**: a contested claim, or a faerie lord's rival charter (pp. 9-10).
**Parallel**: a secret demonic charter beside a mundane one (p. 11). A
demon's entry also ticks the services it offers. Add, edit or delete a
lord.

With the saga's Charter Strength option on (Transforming Mythic Europe
p. 36), each lord's charter has two scores, the lord's (the superior
signatory's) and the town's or covenant's (the subordinate's). They show
in the lord's details and can be typed on his form, with **In England**
for an English charter (its notaries use Common Law, not Civil and Canon
Law); More's Draft the Charter rolls one and Seek a Loophole looks for
grounds against one.

### Terms
<!-- help: section-nb-charter-terms -->

The charter's family (the law it shares with other towns: Lorris,
Breteuil, Freiburg, Lübeck, Cuenca), the year it was granted, the
burgesses, and its privileges, each held or not, some with a word on
what exactly: the annual tax (40 pounds for a town of several hundred
burgesses, p. 12), its own courts, ordeal and combat limited, a cap on
fines (Breteuil's is 12 pence), monopolies, toll exemptions, a market or
fair, salvage, choosing its officials, selling land (pp. 12-13), and
militia duty (p. 10). Edit Terms changes them.

### What it gives
<!-- help: section-nb-charter-gives -->

The Divine aura within the walls: a town's or city's normal 3 (Definitive
Edition p. 418, which wins over Realms of Power: The Divine's town 2);
one higher, 4, under a charter the Church holds (C&G p. 10: "one higher
than would be normally expected"), 1 under a faerie one, which a stronger Faerie aura may swamp (p.
11). A shared charter keeps the normal aura unless **The Church holds the
charter** is ticked; a rival claim or a secret parallel charter changes
nothing. Churches inside keep their own aura. A demon's charter: its
Infernal Might 15 (Mentem) and the services it gives, relief from
disease (+2 Living Conditions), help for merchants (+3 to Bargain and
Profession: Merchant) and dangerous labor (p. 11). The signed charter
holds a pawn of Rego vis tainted by the Divine (very large towns more);
taking it destroys the charter's sympathetic connections (p. 9). Edit
changes the Church's tick, the pawns and whether the vis was taken.

### Citizens
<!-- help: section-nb-citizens -->

The saga's characters who live in the town, from the season they came.
A year and a day of residence makes a townsman (p. 9), shown as the
season a year later. A citizen has a sympathetic connection to everyone
under the same charter, its family's other towns too: +1 to the
Penetration multiplier of a spell against them, until the charter's vis
is taken. Becoming a citizen of another town ends the old connection, so
adding him here takes him off any other town's list (the form says so
first). Clerics are rarely citizens (pp. 9-10): the panel warns. Add,
edit or delete a citizen.

### Size and people
<!-- help: section-nb-town-people -->

The population and its size (a small, medium or large town, or a city:
a city by right, or one of 20,000 or more), the burgesses, the council
and the magistrates (an average town has up to six, p. 29). Occupations
share the people by size (p. 24): a small town half farmers, half
craftsmen; a medium town 10% farmers, 50% craftsmen, 30% in service, 10%
traders; a large town or a city 10%, 30%, 30%, 30%. The officials are a
line each, Title: who (aldermen, bailiffs, consuls, coroners,
councilors, magistrates, mayors, ministerials, portmen, rectors, reeves;
pp. 13-14). Edit changes them.

## Guilds tab
<!-- help: tab-nb-guilds -->

The town's guilds and the saga's characters in
them (City & Guild, Chapter III, pp. 41-50).

### Guilds
<!-- help: section-nb-guilds -->

Each guild: its trade, kind (craft,
service or merchant, p. 41), the Craft its members practise, its hall,
its dean, its officials (most guilds six, chosen from the senior masters
for six months, pp. 49-50) and its members by rank: senior masters,
masters, journeymen, apprentices. The line above the list says how many
guilds a town its size has in the saga's year (p. 54). Choosing a guild
shows its ranks, the saga's characters in it, and how members rise: an
apprentice piece after seven years, a stress die + a Characteristic +
Craft against 9 (p. 45); 12 to join another town's guild (p. 47); a
master pays about a year's income and needs the senior masters' vote
(p. 47). Renaming a guild keeps its members; deleting it takes them out.

### Members from the saga
<!-- help: section-nb-guild-members -->

The saga's characters in the town's guilds, each with his guild and
rank. The list shows his Craft (the guild's Craft, as Craft: or
Profession:) and Guild Lore, and whether he has what the rank needs
(pp. 43-50): Guild Lore 1 a journeyman, 2 a master, 3 a senior master or
dean; Craft 5 a journeyman or master, 7 a senior master; Leadership half
the Craft score and Artes Liberales for a master or above; and the
rank's Social Status Virtue (Guild Apprentice, Journeyman, Guild Master,
Senior Master, Guild Dean). Choosing one shows the rough guide for his
rank by age (p. 42) and what he lacks. Add one once the guild is listed.

## Court tab
<!-- help: tab-nb-court -->

The cases before the town's courts and the sentences they pass (City &
Guild, Crime, pp. 28-30).

### Cases
<!-- help: section-nb-court-cases -->

Each case: the accused, the charge, the accuser (a kinsman accuses for
the dead), the court (churchmen, commercial law and heresy go to the
Church's courts, p. 29), the verdict and, if guilty, the sentence and
its detail; a fine left unpaid makes him an outlaw (p. 30).
<!-- tui -->
More (`m`) > **Court Roll** decides the chosen case:
<!-- /tui -->
<!-- gui -->
**Court Roll** decides the chosen case:
<!-- /gui -->
a stress die + Communication + Civil and Canon Law (Common Law in
England) against 6, for the defendant or his proxy; success finds him
innocent (p. 29). It is a social roll, so the arguer's Gift counts (3, a
Blatant Gift 6; an unGifted proxy avoids it, DE p. 204), with any other
social Virtues and Flaws entered as a + or -. The Ease Factor is 3 lower
if he truly is innocent, 3 higher for a bad name in that court, 3 higher
if most credible witnesses call him guilty. Under Civil Law, Artes
Liberales (logic) can shake a witness's credit: the inspector shows the
arguer's score, and untick the witnesses if the storyguide allows it.
The inspector, The Verdict, shows the total and the die needed as you
choose; Roll keeps the verdict and the roll on the case, then Edit
passes sentence. Add, edit or delete a case.

### Sentences
<!-- help: section-nb-sentences -->

What a guilty man faces (p. 30): death for thievery, robbery,
house-breaking, arson, premeditated murder and treason; a fine, a few
pence to 50-60 pounds, for murder, accidental death, rape, assault,
petty thievery and failing the charter's duties, unpaid making him an
outlaw; mutilation (an eye, ear or hand) or branding instead of a fine
or beside it; shaming in the stocks or pillory for minor crimes. A
defendant who insists he is innocent may choose a trial by ordeal, which
many charters limit or ban.

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
nothing over as long as the site was in use. Otherwise a church's aura
comes from its kind (DE p. 419). Either way, with Realms of Power: The
Divine in play, a relic with a Faith score above 5 raises the church's
Dominion by 1 for each point above 5 (Realms of Power: The Divine p. 12).

With The Sundered Eagle in play, a church's Relics also hold its icons
(The Sundered Eagle pp. 133-135): choose the Kind. An eikon has no Faith
or Might; give its Aesthetic Quality, and the Invoking column shows what
venerating it adds to invoking its saint (Aesthetic Quality / 5, rounded
up). An acheiropoieton, an icon not made by hand, is a powerful relic
with a Faith score like any other. A character's More, Paint an Icon,
adds an eikon here.


**See also:** [A neighbour](help:neighbour)

## Relics
<!-- help: section-nb-relics -->

The church's relics, each with its saint and its Faith score. A relic's
Faith score gives it as many Faith Points and a Divine Might of 10 times
it, and whoever bears it
gains as much Magic Resistance. Its Invoking column is what the relic adds to invoking its saint: with The
Church in play, +2 for each Faith Point, once a day, for the one who tends
or carries it or venerates it a day at its shrine with the custodians'
leave (The Church p. 13); with only Realms of Power: The Divine, +1 for
touching it (p. 87). A character's More, Invoke a Saint, chooses it. Add,
edit or delete one.

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

A faction (the core rules) is any company with a will of its own. Its
**Faction** says which kind: a hedge coven (a magicians' tradition too),
a faerie court, a gild, a family or dynasty, a Hermetic group (a
lineage, societas, league, cabal or a House's faction), a people or
tribe, spirits and beings (a host or race of them, not one: one being
is a Bestiary creature), a faith or sect, a council or assembly, a
military order, brigands and mercenaries, a religious community or an
estate or rank; or Other. The books name no list of kinds: these sort
what the Tribunal books describe. New Faction and Edit record what kind
it is, how it decides (its leader, a council, or
a vote of all), how many members it has, its rules, what it wants and
what it offers; its Faction tab shows them. A hedge coven can also name
the hedge tradition its members follow, from the traditions the app
knows (see [A tradition's chapter](help:tradition-chapter)), so the troupe
knows which record a member is played from. Its named members are listed
under [Members](help:section-nb-members), and the Faction tab counts them.

Its leader is its **Ruler or leader**: a character, another neighbour or
a creature from the Bestiary (see [Ruler or Leader](help:neighbour-ruler)).
Its **Answers to** is its liege or master, not its membership. See
[How to set up a faction's leader and members](help:guide-faction).

### Members
<!-- help: section-nb-members -->

The faction's members, each a character, a covenant, a Bestiary
creature or another neighbour (a courtier, a branch of the gild), with their **Role** in it
("knight of the court", "elder"). Add one by choosing their record
(filter the list by Kind, or type to search), edit their role, or take
them off the roster; their own record stays. A record can belong to
several factions: each one lists it, and the record's page shows every
faction under **Member of** (a character's in its
[Connections](help:section-connections)). A member whose record has since
been deleted shows as no longer in the saga.

Older saves made a faction that belonged to another (a court's
courtiers) answer to it; it is moved to the other's roster when the saga
is opened. A faction's links stay links, under **Linked from** on the
record they point at: add a member here to say they belong to it.

**See also:** [A neighbour](help:neighbour)

## Diary tab
<!-- help: tab-nb-faction-diary -->

What the faction has done, season by season: its schemes, its quarrels,
who joined or left. A place's Diary works the same way (see
[Diary](help:section-nb-place-diary)); a faction's is written by hand,
or by a roll on its [Roll Tables](help:tab-nb-tables) (what its agents
are up to this season). Add, edit or delete an entry.

# A lord's Diary
<!-- help: tab-nb-lord-diary -->

What befell the lord and his lands, season by season: each Battle Event
his army fights, a siege he is linked to as the castle or the besieger
when it ends, a roll on his [Roll Tables](help:tab-nb-tables) (which
sit beside his Diary, after Standing), and anything the storyguide
writes. It works as a place's [Diary](help:section-nb-place-diary): add,
edit or delete an entry.

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

Its **Clock** shows how far it has come, as filled squares: one for each
stage of a dated threat, filled as each comes, or one for each step of
a track up to its last stage, filled to its position (■■■□□ 3 of 5). The
threat's page, its card on the Region and its lines on Ahead show it.

A threat moving along a track can be moved by a place's
[trigger](help:section-nb-triggers): each time the trigger comes, its
season asks whether the troupe **failed** it (the threat moves on) or
**kept** it (it stays). See
[How to set up a threat's clock](help:guide-threat-clock).

**Take Up the Tale**, in the threat's More (on the desktop, its button),
writes a chapter: what the troupe did, met or avoided, in the threat's
[Diary](help:tab-nb-threat-diary) and each troupe covenant's. A threat
grown from a story names it (**Grew from**, a link to the covenant whose
Diary keeps it), and its Diary shows that story's chapters first. See
[Take Up the Tale](help:take-up-tale).

**Delay or Hasten**, in the threat's More, pushes it later or brings it
sooner when something the troupe did changes it: a dated threat's stages
still to come all move by the seasons you give (the dates typed stay as
they are, and Edit shows the delay so far), a track's position moves
back or on. The reason goes in its [Diary](help:tab-nb-threat-diary).

A threat can be **dormant**: a story the storyguide hasn't begun, such
as one left unticked when its pack was imported. It reaches no stage,
nothing of it comes due, and the Tribunal sheet counts it under
**Stories**. **Begin This Story**, in the threat's More, starts it:
dated stages move later together so the first still to come is due next
season at the soonest; a track or omen count starts where it stands.

Its [Roll Tables](help:tab-nb-tables) say how the stage it has reached
shows itself this season: rolled, the row is written in its Diary with
the stage it colours. A roll never moves the threat: its clock moves
only by date, by a tied trigger, by Delay or Hasten, or by Edit.

**See also:** [A neighbour](help:neighbour)

## Stages
<!-- help: section-nb-stages -->

The threat's stages in order, each with when it comes, the clues that
warn of it, and what happens if it is ignored, stopped or turned. A
pending stage comes when its date (or its place on the track) is
reached; mark one **Happened** to say it came anyway, or **Stopped** or
**Turned** to say the troupe kept it from coming. Marking it so writes
what the stage says follows (its If ignored, If stopped or If turned) in
the threat's Diary and each troupe covenant's, so the troupe sees what
comes of it. The stage reached is in bold. Add, edit or delete one.
**What the troupe did**, on the stage's form, is optional: anything
typed there is written as a chapter of the threat's tale (in its Diary
and the troupe's covenants'), and not kept on the stage.
<!-- gui -->
Click a stage to read it in full in the Inspector: when it comes, what
became of it, its clues, and what happens if it is ignored, stopped or
turned.
<!-- /gui -->

## Diary tab
<!-- help: tab-nb-threat-diary -->

What moved the threat, season by season: each answer to a trigger tied
to it (failed or kept), each Delay or Hasten and its reason, and what
came of a stage marked Happened, Stopped or Turned, and its chapters
(marked "Chapter:"), what the troupe did when it took up the tale, and
each roll on its Roll Tables with the stage it coloured. A
threat grown from a story shows that story and its chapters above the
list. It works as a place's [Diary](help:section-nb-place-diary): add,
edit or delete an entry.

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
- **Tribunal's lands** (once the saga has a Tribunal): the Tribunal whose
  lands the place is. Set it on a region (the Black Forest) and
  everything inside takes it, unless a place nearer in names another.
  This is geography, not membership: a covenant's own **Tribunal** (Edit
  Covenant) is the council it belongs to, so a covenant in the Rhine's
  lands that is petitioning to join lies in the Rhine and is no member
  yet; its Connections say both.
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

With the **Auras change** Rule Option on (Realms of Power: Magic and The
Infernal, in Saga Content), auras move each winter as those books say:

- **A Magic aura** has a base aura from its **Tethers**: end each one in
  the place's Tethers with "(natural 1)" or "(natural 2)", or
  "(preternatural 1)" to "(preternatural 5)" (RoP: Magic p. 8; a magical
  being gives its Might / 10, a monument a point a century of use, a vis
  source its yearly pawns / 3). Each winter its yearly modifier adds up
  +3 for every point the aura is below its base (-3 above it), the
  stronger auras that impinge on it (Edit asks which: Magic +2, Faerie
  +1, Divine -6, Infernal -2), +1 to +3 for the magic its covenant works
  (by the covenant's season), +1 for each season of vis study there using
  3 or more pawns and -1 for each season of vis extraction (both counted
  from the season records), and **This year's botches and other magic**,
  which you type. From -3 to +3 nothing happens; at +4 or more the year's
  turn rolls on the Strengthening table, at -4 or less on the Weakening
  table, with the **Aura roll botch dice** the place has built up (one
  more after every roll of 9 or more, one fewer after a year with no
  roll). A permanent rise or fall changes the aura (a regio's top level);
  the rest go into the place's Diary.
- **An Infernal aura** sitting inside a **Stronger aura around it** (Edit
  asks its score and realm) loses 1 after as many years as its strength,
  unless it is **Kept by a demon or an Infernal enchantment**; a
  corruption roll that keeps it starts its clock again (**Eroding
  since**). Its Regio tab shows the corruption roll's Ease Factors: to
  keep it, 3 + the strongest aura there; to raise it, 6 + that aura.
- **A Faerie aura** follows the glamour of the faerie that claims it: the
  presiding faerie's Might / 5; 2 + the higher Might / 5 (at most 9)
  while another faerie contests it; a steward's Might / 5 while the
  presiding faerie is away. Each season the magi extract vis there
  without a bargain with the faerie lowers it by 1, until the faerie has
  had redress (set **Aura lost to vis taken** back to 0). A faerie that
  travels takes its aura with it (Realms of Power: Faerie pp. 14-16).

Any Infernal place's Edit asks what it is **Tarnished with** (a sinful
Personality Trait, which everyone in the aura acts as if moved by its
strength) and whether it is **Corrupted** (Debauched, Malevolent or
Perfidious; only an aura of 3 or more, with its features written in its
Notes) (Realms of Power: The Infernal pp. 13-15).

An aura may have a kind of its own, which Edit asks by the place's realm
(and Add or edit asks of each regio level by the level's):

- **Alignment**, for a Magic aura (Realms of Power: Magic pp. 15-16). An
  aura has at most one. Aligned with an **Art**, its strength counts again
  in the Casting Score of any spell using that Art (as its Technique, Form
  or a requisite) and in a Lab Total of that Art, both shown as "Aura
  aligned with ..." in the working; a creature whose Might is of that Form
  pays a Might Point less for any power that costs one; the opposed Art
  takes no penalty. **Healing** adds half the aura, rounded up, to the
  Recovery Totals of those who live there; **Luck** gives +1 (+2 from 5 to
  8, +3 above) to rolls where luck matters, for everyone; **Distracting**
  calls for Concentration rolls more often, their Ease Factors 3 higher
  from aura 5. Any other word is a feeling (Aggressive, Carefree,
  Communicative, Respectful, Fearful...): after a few minutes there,
  those without The Gift or another Magic power take it as a temporary
  Personality Trait of +1 (aura 1-3), +2 (4-6) or +3 (7-10), never
  changing an Essential Trait. An aligned aura above 5 slowly warps those
  who live in it without a Magic power. Intellego Vim at level 4 discerns
  an alignment; a covenant may take it as the Fine Aura (Major) or
  Favorable Aura (Minor) Boon, or the Troublesome Aura Hook (p. 16).
- **Tints**, for a Faerie aura (Realms of Power: Faerie p. 104), written
  "Drawn to Children +3; Light +2": everyone in the aura takes each as a
  temporary Personality Trait while they stay, no stronger than the aura.
  Tinting takes a ceremony (the tint fades a point a day) or a season's
  influence (a point a season): stress die + Presence + Concentration
  against 3 times the Trait's value, never above the tinter's Sympathy
  Trait. Several tints pull people several ways at once; some auras are
  tinted for good.
- **Divine aura**, for a Divine aura: the **Dominion** or an
  **Empyreal** aura. Both are one weaker at night and one stronger on
  Sundays and holy days (Realms of Power: The Divine pp. 7, 10; DE
  p. 418), and both hold sway over another realm's aura of the same
  strength (p. 11). The Dominion comes from worship; an Empyreal aura
  comes from no congregation: from a person or relic of 5 or more Faith
  Points, from a miracle (1 at level 50, a point more each five levels
  above, while its effect lasts), or from a holy creature's home (a point
  each season it dwells there, up to its Might / 10; pp. 12-13). In play
  the two are the same (p. 12): the realm table applies to both, and
  mundane folk are moved alike, the pious to love and awe, the sinful to
  guilt and fear, while the Gifted feel their Gift falter (pp. 8-9).

The place's facts say what its aura's kind does ("Aura kind"), and each
level's ("Within").

Conciatta's guidelines for auras (Legends of Hermes p. 17), which any
magus who has studied one of her unpublished works may use: Intellego Vim
detects a supernatural tether of strength 5 or more at level 1, 4 or more
(and a subsumed aura, one a stronger aura overpowers) at level 2, 3 or
more at level 3, a natural or supernatural tether of 2 or more at level
4, and any tether at level 5; a Rego Vim Ritual suppresses an aura no
stronger than its magnitude for its duration (only the mundane level;
broken if the aura grows past it), and Dominance Over the Infernal holds
an Infernal aura of (magnitude - 9) at bay for a year. Her words for
auras: diffuse (no fixed source) or tethered; stable, waning or waxing;
existential (Faerie and Magic) or moral (Divine and Infernal); apparent
(the strongest present) or subsumed (p. 15).

**See also:** [A neighbour](help:neighbour)

**Lies in.** A place, or a regio level, may lie in the Magic Realm or the
Faerie Realm instead of the mundane world (Lies in, on the place's form and
on each regio level's). Its aura then is the realm's own, whatever the Aura
field says:

- **The Magic Realm** (Realms of Power: Magic pp. 20-28): Magic 10
  throughout, plus the realm boundary the place lies in (Boundary, 0-10):
  a boundary of 4 makes the aura 14 for magic. The boundary is aligned with
  a Form, kept in Alignment: that Form's effects add the boundary again
  (Corpus 4: +18 to Corpus effects). Powers of other realms take no bonus
  from it. Each roll the aura helps takes as many extra botch dice as the
  boundary: casting botch dice and the laboratory's count them. Each season (aura / 10, rounded up) pawns of the boundary's
  Form of vis appear there and fade if not taken (p. 22). No one gains
  experience there: a season's experience comes as pawns of vis of one Art
  instead (p. 20), and no one makes Aging rolls; Diameter, Sun and Moon last
  to the season's end, Year as long as the target stays.
  Travelling on through a boundary or vestige takes Magic Might, Second
  Sight or Magic Sensitivity: stress die + Perception + an Ability + the
  Form / 5 against (10 - its level) x 3, less the best Familiarity (knows
  of it 1, seen it 3, visited it 6, an Arcane Connection 15, or Enigmatic
  Wisdom, Magic Lore, Area Lore x 3). By how much it passes is the Speed
  Level of the journey through the Twilight Void: 0 seven years and more, 9
  a season, 15 a day, 24 two minutes, 30 a moment; each botch a step (3)
  slower; below 0, stranded (p. 23). Straying from the path in the Void is
  a Twilight Comprehension roll, Int + Enigmatic Wisdom + stress die
  against Warping Score (or Might / 5) + stress die (p. 24). The vis
  gathered there can transform a character without Might: 5 pawns a Minor
  Virtue and Flaw, 10 a Minor Virtue, 15 a Major Virtue and Flaw, 30 a
  Major Virtue, one change a season (p. 26).
- **The Faerie Realm** (Realms of Power: Faerie p. 24): Faerie 10
  throughout: Hermetic magic +5, with ten botch dice rolled apart (their
  botches are strange rather than dangerous). An entrance to Faerieland
  from a faerie regio is a regio level of aura 10 (p. 16): set its level
  to lie in the Faerie Realm.

**Threshold.** A place with a Faerie aura shows the Threshold's strength:
the Threshold points needed to cross into the Faerie Realm from there,
(13 - the aura's modifier on a Faerie power) x 3; Faerie 3 needs 30. A
Faerie regio level adds the surface's Faerie aura to its own (any other
surface aura doesn't count) (Realms of Power: Faerie p. 21). Points come
from the border crossed (3, 6, 9 or 12, +3 if lost; a trod at least 9),
the time (new moon 1, full moon or a pagan holiday 3, solstice 6, equinox
9), the traveller (faerie Virtues 3, or 9 if Major; faerie Flaws 3; only
the best of these; an extreme emotion 3 + its Trait; a life change 9 to
18), a work of art about Faerie (its Aesthetic Quality), a faerie's Spirit
Away, and the Arcadian Travel charm (pp. 21-23). A set of circumstances is
tried once; changed, again at the next moonrise. The Guardian of the
Threshold then offers the choice; Int + Faerie Lore against 6 gives hints
(p. 24). Finding the action that opens a faerie regio's level, once its
entrance is found, is Int + Faerie Lore against 15, or 3 when the story
narrows it to a choice (p. 16).

**Lunar aura** (with Dies Irae in play). Lunar is a fifth supernatural
realm (Dies Irae p. 36): where the fallen lunar sphere's matter lies, a
place (or a regio level, or a covenant's aura) may have a Lunar aura, its
Realm set to Lunar. The realm is offered only while Dies Irae is in play.
By the New Realm Interaction Table (p. 37) a Lunar aura gives Hermetic
and Faerie powers -5 x the aura and Infernal ones -aura, and leaves
Divine powers untouched; Lunar powers lose the aura in Magic, Faerie and
Infernal auras and 3 x it in a Divine one. Casting Scores, Lab Totals
and the rest take it like any other aura, with a botch die a point for
the foreign aura. A season's clearing lowers it by 1, and the matter
carried off makes 1 of Lunar aura wherever it is taken. Since the fall
Diameter, Sun, Moon and Year Durations fail everywhere, and Parma Magica
and the Aegis of the Hearth with them; each replacement duration is a
Minor Breakthrough of 30 points (p. 37).

### Cross the Threshold
<!-- help: cross-threshold -->

**Cross the Threshold** (More on the place's record; on the desktop on the
Regio chapter) counts the points a set of circumstances gathers: choose
the level they start from, who leads the crossing (his faerie Virtues and
Flaws come from his sheet), the border, the time, his emotion and life
change, a work of art, Spirit Away, an Arcadian Travel charm's total and
a cognizant faerie's Might. The panel sets the total against the
Threshold's strength; Try writes the attempt in the place's Diary, and
says whether the Threshold comes (and the Guardian's least Might) or
that these circumstances can't open it again before the next moonrise.

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

**See** is the Ease Factor to see into the level from the one below:
its own roll's when it names one, else the Definitive Edition's (marked
DE): 5 + 2 x the difference in aura, or 5 + 2 x the two auras added when
the level below is of another realm (p. 421). Second Sight or Magic
Sensitivity sees into any level, Sense Holiness and Unholiness into a
Divine or Infernal one.

A regio level may have a kind. A Divine regio is terrestrial (tied to a
place on earth) or celestial (an angels' home, reached by invitation): in
a celestial level a mortal acts normally only on Stamina + Dominion Lore
(or Parma, if better) against 3 times its rating, else takes as much from
every roll, and after Stamina + Parma + 3 hours loses a Fatigue level an
hour, then gains Warping (Realms of Power: The Divine pp. 13-15). Every
Infernal regio suspends Divine powers (no invoking God, Intercession or
Holy Influence; Holy Powers and Holy Magic at minus its aura); a Tartaran
one makes all Fatigue long-term and burns with hell-fire, an Abyssal one
lowers every Characteristic by its aura and asks a daily Intelligence
roll against the madness Flaws (Realms of Power: The Infernal pp. 16-17).
The place's facts say what each level does ("Within").

Each level may also have its aura's own kind (an alignment, tints, or
Dominion or Empyreal), asked by the level's realm as the place's is.


## Vis Sources
<!-- help: section-nb-vis-sites -->

The vis sources gathered at this place (Definitive Edition p. 422: a
place where a certain number of pawns can be taken each year): each
one's Art, pawns, season, who holds it, its level, and its taint when
the aura there is not Magic's ("Faerie vis"; Divine vis risks the
Church's anger, Infernal vis corrupts).

- A source a covenant holds is listed from its covenant's
  [Vis Sources](help:section-pos-vis_source), where it is edited: its
  Place names this one.
- A source no covenant holds yet (one waiting to be found) is added and
  edited here. Choose a covenant in **Claimed by** and it becomes that
  covenant's source, still gathered here.

The place's **Vis** says what its sources give a year, by Art, and what
the places inside it give, however deep, so a region shows the vis in
all its lands. The Region [by place](help:tab-region-by-place) lists
each source under its place.

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

A dated trigger can **move a threat** that moves along a track or an
omen count: choose it in **Moves a threat**, and say how many steps
failing it moves the threat (1 if left blank). Each time the trigger
comes, the season it comes in asks how it went (see
[The World Turns](help:world-turns)).

## Roll Tables tab
<!-- help: tab-nb-tables -->

The roll tables of a place, a threat, a faction or a lord: what the
troupe might meet at a place, or what a night in the regio brings; how
a threat's stage shows itself; what a faction or a lord is up to this
season. A lord's tab comes after Standing, beside his Diary. No book
prints a rule for these tables: they are the storyguide's own.

Only the storyguide sees the tab and rolls: a player signed in to a
hosted copy doesn't see it, as with Secrets (see
[Keeping secrets from players](help:guide-hosting-secrets)). Played
solo, the one player is the storyguide and sees everything.

A roll on a threat's table colours the stage it has reached and never
moves its clock.

## Roll Tables
<!-- help: section-nb-tables -->

Each table names its die (a simple die, a stress die, a d6 or a d10)
and its rows, one a line: "1-3: Nothing stirs", "4: A hare", "9+: The
Hall opens", and for a stress die "botch: The mist closes".

A row may end with a note for the storyguide, written "(SG: ...)":
"3: The letters on the walls curse whoever reads them. (SG: False: they
honour Abnoba.)". The roll shows the note; the line written in the
Diary leaves it out, so players reading the Diary see only what
happened. Any row can take one, a botch row too; a row without one
works as before, and "(SG:" anywhere but the row's end is part of its
text.

<!-- tui -->
More (`m`) > **Roll** rolls the chosen table and shows the row it lands
on; **Write** puts it in the record's Diary.
<!-- /tui -->
<!-- gui -->
**Roll** rolls the chosen table and shows the row it lands on; **Write**
puts it in the record's Diary.
<!-- /gui -->

Add, edit or delete one.

## Tomb tab
<!-- help: tab-nb-tomb -->

A place marked **A tomb** (on its form, with Lands of the Nile in play)
has a Tomb tab: the tomb designed like a covenant, with its curses, its
talismans and wards, and its traps (Lands of the Nile pp. 32-46). The
rules suit any tomb, not only Egypt's and Nubia's.

## The Tomb
<!-- help: section-nb-tomb -->

What the tomb's kind gives (Lands of the Nile p. 40): a major monarch's
tomb has a base Magic aura of 5 and 500 Build Points; a royal consort's
or minor monarch's 4 and 250; a lesser royal's or high priest's 3 and
100; a non-royal dignitary's 3 and 50. Decay lowers the aura. A burial
ground in use for a century is a preternatural tether of 1, up to 5 for
five centuries; the place keeps its own aura, so with the aura change
option on, name the tether in the place's Tethers, as "(preternatural
5)". A tomb has up to 10 points of Hooks to buy Boons.

The Build Points spent are the curses', the talismans' and wards', the
traps', and the other resources' (inscriptions as a library, guardians
and ghosts as specialists, vis), which cost what a covenant's do (pp. 42,
44); more than the tomb has are shown in red. **Edit Tomb** sets them.

## Curses
<!-- help: section-nb-tomb-curses -->

A curse is a condition and its excoriation (Lands of the Nile pp. 34,
40-41). It strikes when its condition is broken or its text is defaced;
once it has struck as many times as its uses a day, the text can be
destroyed safely. It costs 2 Build Points for every 5 levels; one
written without force (**Hollow**) costs nothing. One beyond Hermetic
magic is a **Lesser** (base level 10) or **Greater Malediction** (base
30): Special Duration, until dispelled, and it Warps its victims. Add,
edit or delete one.

The book's Tomb of Cleopatra prints 6 Build Points for her fear curse,
but the curse is a CrMe 25 effect, which the rule prices at 10: the 6
fits a level-15 effect, so it is a misprint, and her tomb's curses come
to 42 Build Points, not 38 (Lands of the Nile pp. 41, 46). The app
prices curses by the rule.

## Talismans and Wards
<!-- help: section-nb-tomb-wards -->

A third kind, **No obstacle**, neither harms nor repels, and has no Ease
Factor (the Face of Lost Companions, p. 42). **Ease Factor, if another**
keeps one the book prints apart from the rule. **Overcome It** works on a
talisman or ward as on a trap.

A **talisman** harms or imprisons, and is overcome without magic
against 6 + its magnitude; a **ward** repels or hides, against 9 + its
magnitude (Lands of the Nile pp. 35, 42). Anyone whose Magic Resistance
is at least its Penetration passes untouched. Each costs 2 Build Points
for every 5 levels. A talisman is usually made inert until sunset by a
particular spell effect; a ward by a deed at a place and time. Add, edit
or delete one.

## Traps
<!-- help: section-nb-tomb-traps -->

A trap costs Build Points for its harm (3 to delay or scare, 6 for a
minor injury or imprisonment, 9 for a serious injury, 12 if often
fatal) plus 0, 1, 3, 6 or 9 for an Ease Factor to avoid of 3, 6, 9, 12
or 15 (Lands of the Nile p. 44). A trap treated as several pays for each
harm once: put what the others cost under **Further harms' Build
Points**, as the book's covered pit does (a serious and a minor injury,
p. 46). **The roll to avoid it** and **Ease Factor to spot it** keep what
the book gives, where it gives them. Most mechanical traps are reset by
hand, and some work only once.

<!-- tui -->
More (`m`) > **Overcome It** walks the party through the chosen trap when
it springs.
<!-- /tui -->
<!-- gui -->
**Overcome It** walks the party through the chosen trap when it springs.
<!-- /gui -->

Add, edit or delete one. A puzzle is a trap and lock in one: keep it in
the trap's words, for the troupe to play (p. 33).

### Egyptian craftwork
<!-- help: tomb-craftwork -->

Egyptian curses, talismans, wards and amulets are designed as Hermetic
enchanted items; a troupe with Hedge Magic may use Learned Magic instead,
whose protection, assistance and harm match the Egyptians' amulets,
talismans and curses (Lands of the Nile p. 55). The Egyptians had very
high casting and laboratory totals, no Difficult Arts and no limits on
Range, Duration and Target. An amulet's colour is flavour: black for
magic, green to draw faeries, blue for the gods, yellow, orange and some
reds for fire, red for curses and for Apep and Seth (pp. 55-56).

## Overcome It
<!-- help: overcome-trap -->

A tomb is fixed once built, so only the rolls vary. Overcome It takes
one step at a time (Lands of the Nile pp. 32-33, 44), and cancelling any
step writes nothing. It works on a trap, and on a talisman or ward, which
the same rules resolve (pp. 35, 42).

1. **Who is there.** Choose who is in danger and tick who is with him.
   Ticking **They look for it first** rolls Per + Awareness for each of
   them against the Ease Factor to spot it: 3 less in perfect light, 3
   more by a single flame, 6 more in near darkness. If someone sees it,
   they have combat rounds to deal with it, and magi time for formulaic
   or ritual magic: say whether they deal with it, leave it be, or it
   springs all the same.
2. **Each character acts**, the one in danger first, the rest by
   Quickness, and sees how those before him did. He says one thing he
   does; the troupe agrees **His roll** (a Characteristic + Ability,
   `- Encumbrance` if it counts; blank if the action needs none), and the
   storyguide moves the Ease Factor by 3, 6 or more for that action. A
   magus answers with **a Fast-Cast spell**, judged on its own: cast it
   from his sheet, and tick **The spell worked** if it did, which clears
   him of the trap. Against a talisman or ward, Magic Resistance of at
   least its Penetration passes it untouched. If two actions clash, the
   troupe settles it by an Action Priority Roll (Qik + an Ability,
   Finesse for a fast-caster).
3. **It acts last.** Tick anyone another character helped, or who was out
   of its reach: the rest suffer it. The app says what the record says of
   the harm; the storyguide rolls any damage. Say what came of it, and
   whether the trap stays sprung or is reset. **Write** puts it all in the
   place's diary.

A trap left sprung can't spring again: Overcome It offers to reset it
first, unless it works only once. With Lords of Men's Evasion, a trap's
Attack is a stress die + its setter's Int + Profession, + a like weapon's
Attack (p. 44).

## Diary tab
<!-- help: tab-nb-place-diary -->

What has happened at the place.

## Diary
<!-- help: section-nb-place-diary -->

What has happened at the place, or what the faction has done, a line
each, with the season it happened: for a place, the rolls on its tables
and the aura rising; for either, anything the storyguide writes. Add,
edit or delete an entry.
