# The Region
<!-- help: region -->

<!-- tui -->
The Region is the saga's world beyond the troupe's covenants. It holds
the Tribunals, the covenants the troupe doesn't play, and the
neighbours around them, such as lords, towns, the Church and threats.
Each neighbour has its attitude toward the troupe.

In the navigation tree, The Region sits under the troupe's covenants.
Each Tribunal is listed there with the covenants the troupe doesn't
play under it. A covenant with no Tribunal sits directly under The
Region. Then comes a node for each group of neighbours, with the
neighbours in it. Selecting The Region, or a group, shows the Region
sheet: its Neighbours tab of lists and its
[By Place](help:tab-region-by-place) tab. Selecting a neighbour shows
its own sheet.

Press `n` (New) here, or on the saga, and choose **New Tribunal** or
**New Neighbour**. A covenant joins a Tribunal through the Tribunal
choice in Edit Covenant.
<!-- /tui -->
<!-- gui -->
The Region is the saga's world beyond the troupe's covenants. It holds
the Tribunals and the neighbours around them, such as lords, towns, the
Church and threats. Each neighbour has its attitude toward the troupe.

On the saga's page, The Region chapter opens with the Tribunals as
cards, each opening its own page, and a New card that adds one. Under
them come the Region's facts, then each group's neighbours as cards with
their own New card, or the Region [by place](help:tab-region-by-place).
The covenants are in The Covenants, whether the troupe plays them or
not.

A group with more than a dozen neighbours shows its first twelve and a
**Show more** card that draws the rest. A Tribunal book brings hundreds,
and a card for each would make the saga slow to open, so use the filter
below to narrow them.
<!-- /gui -->

**See also:** [A neighbour](help:neighbour), [Tribunal sheet](help:tribunal),
[Covenant sheet](help:covenant)

## The Region's facts
<!-- help: section-region-info -->

- **The troupe's covenant**, the first it plays when it plays several.
  The attitudes in the lists are toward it.
- Its Tribunal, that Tribunal's customs, and when the Tribunal next
  meets.
- How many neighbours there are, and how many are warm or wary toward
  it.
- How many other covenants there are.
- **Threat due** names the threat whose next stage comes soonest.
<!-- gui -->
  The leaf after it (❧) opens that threat's page.
<!-- /gui -->

## Merge Doubled Records
<!-- help: merge-doubles -->

Before a character or a creature could hold an attitude, someone the
troupe dealt with was often entered twice. A faerie knight or a hedge
witch became a faction, to carry the attitude, and a character or
Bestiary creature, for the stat block. **Merge Doubled Records** finds
each faction whose name exactly one character or creature has. It makes
the pair one record, the character's or creature's.

The form lists each pair, ticked, with what merging brings. Untick any
that are two records on purpose, then choose **Merge**. For each pair
ticked:

- Its attitudes, favours and links move to the character or creature.
  Where the record already has an attitude toward that covenant, the
  record's is kept.
- Its summary, rules, wants, offers and diary are added to the
  character's summary or the creature's notes. Its Secrets join theirs.
- The factions it was a member of, and the neighbours it ruled, now name
  the character or creature.
- A creature takes its place and its map pins. A character's pins are
  left off, since the Atlas shows a character at their covenant's pin.
- The faction itself is deleted.

Only factions are offered. A lord, a threat or a place named for its
person keeps rules of its own and stays a record apart, such as the Ash
of Nortorf, the story and the spirit.
<!-- tui -->
It's in More (`m`) on the saga or The Region while there is a pair to
merge.
<!-- /tui -->
<!-- gui -->
It's a button beside the Neighbours heading of The Region while there
is a pair to merge.
<!-- /gui -->

## Neighbours
<!-- help: tab-region-neighbours -->

The other covenants, then a list for each group of neighbours, over the
details of the one chosen. The details give its kind and detail, its
attitude toward each player covenant and how it was reached, the first
line of its summary and the favours still open. A group is listed when
it has a neighbour, or when the book one of its kinds needs is in play.

A Tribunal book brings a great many neighbours, so the lists can be
narrowed:

- **Region**: a place that sits inside no other, such as the Black
  Forest. It shows the region and everything inside it at any depth.
- **Kind**: lords, towns, places and so on.
- **Tribunal's lands**, once a place names one: whatever lies in them,
  member of that Tribunal or not. See [A place](help:tab-nb-place).

Each list's title then says how many it shows of how many. The filter
stays while the app is open.

<!-- tui -->
The Region's facts say what the lists are narrowed to ("Showing").
Press `/` (Filter) on any of the lists and choose a Tribunal's lands, a
region, a kind, or any of them. Blank them all to show everything again.
<!-- /tui -->
<!-- gui -->
Choose them in the quiet drop-downs at the right of the first list's
heading ("Show: Every Tribunal, Every region, Every kind"). The Tribunal
one shows once a place names a Tribunal's lands. Set them back to Every
to show everything again.
<!-- /gui -->

### Other Covenants
<!-- help: section-region-covenants -->

The covenants the troupe doesn't play, with their Tribunal, their
votes, their attitude toward the troupe's covenant and their detail.
Open one from the tree to change it.

### Lords and Towns
<!-- help: section-region-lords -->

The lords (Lords of Men) and towns (City & Guild) of the region. Add
one, choosing a lord or a town. Edit changes the chosen one's common
fields, and Delete removes it.

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

The gilds, hedge covens, families and other factions of the region
(the core rules). Add, edit or delete one.

### Threats
<!-- help: section-region-threats -->

The stories that grow if left alone (the core rules). Each shows its
[Clock](help:tab-nb-threat), its next stage and when, and its attitude.
Add, edit or delete one. A story not yet begun shows as **Dormant**.
Open it and choose **Begin This Story** in More to start it.

### Open Stories
<!-- help: section-region-stories -->

Every open Story Event of the troupe's covenants, oldest first. Each
shows what it concerns, the covenant whose Diary keeps it, and the
season it arose.

- An experiment's story event, a Disaster's covenant story and Suggest
  a Story each write one. You can also add one by hand in a covenant's
  Diary, as a Story Event.
- Edit opens its Diary entry. Mark it **Resolved** once it's told, and
  it leaves the list. Resolving asks for its last chapter.
- **Take Up the Tale** writes a chapter of what the troupe did. A
  story's chapters show under its words.
- The Seasons page's [Needs You](help:section-attention) lists them
  too, those whose Revisit year has come first.
<!-- tui -->
- More (`m`) > **Grow into a Threat** makes the chosen story a threat
  of the Region (see [Grow into a Threat](help:grow-story)).
<!-- /tui -->
<!-- gui -->
- **Grow into a Threat** on a story's card makes it a threat of the
  Region (see [Grow into a Threat](help:grow-story)).
<!-- /gui -->

### Places
<!-- help: section-region-places -->

The forests, ruins, crags and regiones of the region. Each shows where
it is, its aura, how many regio levels it has and how far the troupe
has got with it. Add, edit or delete one; see [A place](help:tab-nb-place).

A place's form also has:

- **Waters** (Open water, Anchorage or Port), which a ship's stops use.
  The book packs mark theirs, and a port town has a harbour Place
  beside it.
- **Travels with**, for a place that moves with a covenant, as a ship
  does. See **How to keep a covenant on the move**.

## By Place
<!-- help: tab-region-by-place -->

The Region as the land rather than as lists. It starts with each place
that sits inside no other, such as the Black Forest or the Rhine
Valley. Under each comes what rests on it and the places inside it,
each indented under the one it sits in, however deep. What rests on a
place includes its lords, towns, churches, factions and threats, the
covenants there now and the creatures found there.

Each line says what the record is, such as a place's aura or a
neighbour's kind and attitude. What is placed nowhere comes last. Click
a name to open its record.

<!-- tui -->
It's the Region's **By Place** tab, beside Neighbours.
<!-- /tui -->
<!-- gui -->
Choose **By place** in the chips under the Neighbours heading of The
Region. **By kind** brings back the lists. The choice stays while the
app is open.
<!-- /gui -->

These are the same records in another order, and nothing is moved. A
place's **Inside** (Edit) is what puts it under another.

### The land
<!-- help: section-region-by-place -->

Each place, what rests on it and the places inside it. Every name is a
link that opens its record (see [By Place](help:tab-region-by-place)).

### Customs and Lore
<!-- help: section-region-customs -->

How the land lives, as a book's background describes it. That covers
its honour and kin, its tongues and manners, its law and its things,
its trade and
roads, a treaty or a legend. Each says where it belongs and the first
line of the rules it brings, such as hof and ohof among the Icelanders,
or the Baqt between Egypt and Nubia. Add, edit or delete one; see [A custom](help:tab-nb-custom).

# A custom
<!-- help: tab-nb-custom -->

A custom is the land's lore rather than a company: what the people of a
place do and believe, and how they trade, judge, speak and travel. New
Custom and Edit record:

- **Its rules**: what it means in play, with the book's page. It might
  favour a Virtue, change a roll or set a law the troupe must keep.
- **Wants** and **Offers**: what those who keep it ask of the troupe,
  and what it gives them, when the book says.
- **Ruler or leader**, shown as **Kept by**: a person who keeps or
  presides over it, as Viscountess Ermengarde does her Courts of Love.
- **Place**: where it holds, so the Region
  [by place](help:tab-region-by-place) lists it under that land.

Like a place, it has no attitude, detail or liege. Its **Found Here**
shows the favours and links that name it.

**See also:** [A neighbour](help:neighbour)

# A neighbour
<!-- help: neighbour -->

A neighbour is a lord, a town, a church, a university, a faction, a
threat, a place or a custom of the saga's region. Only its name is
needed. The rest can be filled in later, or never.

**New Neighbour** asks for its kind first, offering the kinds whose
book is in play. Show everything lists the others, with the book each
needs. Then comes a plain form:

- **Name**: the only field required.
- **What its kind adds**:
  - a lord's title, wealth, manors and seat (see [A lord](help:tab-nb-fief))
  - a town's charter, council and population (see [A town](help:tab-nb-town))
  - a church's kind and order (see [A church](help:tab-nb-church))
  - a university's kind and fees (see [A university](help:tab-nb-studium))
  - a faction's kind, how it decides, its members, rules, wants and
    offers (see [A faction](help:tab-nb-faction))
  - a threat's antagonist and how it moves (see [A threat](help:tab-nb-threat))
  - a place's aura, tethers and gazetteer (see [A place](help:tab-nb-place))
  - a custom's rules (see [A custom](help:tab-nb-custom))
- **Summary**: a paragraph on who they are and what they want.
- **Detail**: a line, a sketch, or written in full.
- **Ruler or leader**: one of the saga's characters, its other
  neighbours or the Bestiary's creatures. Or type a name for one the
  saga has no record of (see [Ruler or Leader](help:neighbour-ruler)).
- **Answers to**: its liege, bishop or master among the neighbours.
  Deleting a neighbour leaves those that answered to it answering to no
  one.
- **Realm**: Divine, Faerie, Infernal or Magic, or none.
- **Place**: the place it is in, or one of that place's regio levels.

Edit can also change its kind.
<!-- gui -->
**Edit** sits beside the neighbour's name at the top of its page.

Click a row in any of its lists, such as a lord's castles or a town's
guilds, to read it in full in the Inspector.
<!-- /gui -->

**See also:** [The Region](help:region)

## The neighbour
<!-- help: section-nb-info -->

Its kind, detail, ruler or leader, who it answers to, its realm and the
book its kind comes from, with its summary. Under **Answer to it** come
the neighbours whose Answers to names this one, such as a lord's
vassals or a faction's members. Edit changes them. Each name is a link
(see [Following a record's links](help:record-links)).

## Standing
<!-- help: tab-nb-standing -->

Its attitude toward each player covenant with the reasons it moved,
the favours owed between it and the troupe, and its links to other
records. It works as on a sketch covenant. See
[Attitude](help:section-attitudes), [Favours](help:section-favours) and
[Links](help:section-links). A place or a custom holds no attitude, so
this is called **Found Here** and shows only its favours and links.

### Following a record's links
<!-- help: record-links -->

A page that names another record of the saga names it as a link. That
includes:

- a neighbour's ruler or leader, who it answers to, where it is and who
  answers to it
- a place's claimant and what is found there
- a creature's place and the neighbours it rules
- what links to a place or creature (**Linked from**)
- a character's, covenant's or laboratory's
  [Connections](help:section-connections)
<!-- gui -->

Click an underlined name to open its record's page. **Back** returns to
the page you came from. In Standing, **Open** in Links opens the record
the chosen link points at.
<!-- /gui -->
<!-- tui -->

Click a name with the mouse to open its record. It's chosen in the tree
and its sheet shown. From the keyboard, **Go To** in More (`m`) lists
every record the page names, its links' too. Each is listed under what
it's named as, such as Ruler or leader, Answers to or Links. Choose one
to open it.
<!-- /tui -->

**See also:** [A neighbour](help:neighbour), [Links](help:section-links)

### Go To
<!-- help: go-to; tui -->

The records the page on show names, each under what it's named as.
Choose one to open its sheet. The filter at the top narrows the list to
one kind of name. See [Following a record's links](help:record-links).

### Ruler or Leader
<!-- help: neighbour-ruler -->

Who rules or leads the neighbour, chosen from the saga's records:

- **Characters**: a lord, an abbess, a hedge wizard, at any detail.
- **Neighbours**: another neighbour, such as the faction a puppet lord
  really serves.
- **Bestiary**: a creature, such as the faerie who rules a court.
- **Type a name...**: a name only, for a ruler the saga has no record
  of yet. It opens the record of that name if exactly one character,
  neighbour or creature has it. So a pack's rulers link as soon as
  their records are there.

The ruler shows on the neighbour's page as a link to their record. A
ruling creature's or neighbour's page lists what it rules under
**Rules**. Deleting the ruler's record keeps their name on the
neighbours they ruled.

# A lord
<!-- help: tab-nb-fief -->

A lord (Lords of Men) has a title, a wealth, a number of manors and a
seat, entered on New Lord or Edit. The title is landed noble, baron,
count or earl, or duke. The wealth is poor, average or wealthy. The
lord's **Fief** works out the rest:

- **Income**: 20 pounds a year for each manor (LoM p. 72), counted as
  [Manors](help:tab-nb-manors) says.
- **Mercenary budget**: what the lord may spend on mercenaries a year,
  once the household and knights are paid (Lords of Men p. 103).
  - 0 if poor.
  - A landed noble 2, or 5 if wealthy.
  - A baron 40, or 100 if wealthy.
  - A count 100, or 250 if wealthy.
  - A duke 250, or 500 or more if wealthy.
  - It isn't the 10 or 20 pounds a landed noble has for largesse and
    war together (p. 31).
- **Free time**: a landed noble's free seasons a year, as Lords of Men
  gives them. That's 1 if poor, 2, or 3 if wealthy (p. 31). The
  Definitive Edition's Landed Noble has no free time beyond the usual,
  and a poor one none (DE p. 89).
- **Army**: the knights, serjeants, infantry and levies the title
  raises.
- **Owes** and **Aids**: what the lord owes the neighbour they answer
  to, if any.
  - A knight's service for 40 days for each manor, or 2 pounds scutage
    a knight.
  - Aids of a pound a manor.
  - The heir's relief: a year's income, but at most 5 pounds a manor
    (100 for a baron or greater).

Where Lords of Men gives two figures for the same thing, the lower is
used. That covers a landed noble's spending money, and a duke's knights
and scutage.

**Affinity** is the lord's bonus to social rolls among the region's
nobles, land-holding churchmen and the councils of towns without a
royal charter. It helps in mustering the local knights, settling their
disputes, swaying their advice or refereeing a tournament (Lords of Men
pp. 21-22).

- +1 for a landholding noble of banneret stature.
- +2 for an officer or baron of a minor lord.
- +3 for an officer or minor baron of the king.
- +4 for a greater baron.
- +5 for the senior noble under the king in the region.
- Half that, rounded down, where two warring affinities divide the
  lord's country.

Left blank on the lord's form, it follows the title. A landed noble of
five manors or more gets +1, a count or duke +5. A baron gets +2, the
lowest of the barons' standings, since the title doesn't say whose
baron they are. Choose a standing to set it, and tick **divided** to
halve it. A lord who neglects their affinity loses some of it, so lower
the standing.

Surplus is Chapter Three's own figure, not income less costs:

- A landed noble none, or 10 or 20 pounds a year by wealth (p. 31).
- A baron none, 40 or 100.
- A count 100 or 250 (p. 32).
- The book gives none for a poor count or for a duke.

A greater baron's expenses are 400 pounds or more a year, about 20
manors (p. 32).

**See also:** [A neighbour](help:neighbour)

## Manors
<!-- help: tab-nb-manors -->

A lord's manors, kennels, mews and stables, and household (Lords of Men,
Chapter Six, pp. 71-87; Chapter Five, pp. 58-61; Chapter Two, pp.
9-12). The lord's **Fief** counts the manors listed here, 20 pounds a
year each. The count on the form is used only while none is listed.
<!-- tui -->
Choose a manor or an establishment to see it in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a manor or an establishment to see it in full in the inspector.
<!-- /gui -->

### The manors
<!-- help: section-manors -->

Each manor's row records:

- **Acres**: about 600, a third more or less without being unusual
  (LoM p. 72).
- **How it's farmed**: large fields, turned over to sheep, or another
  way (pp. 72-73).
- **Land by use**: demesne, rented, villeins, glebe and waste (p. 75).
- **Allod**: held with no lord above it (p. 85).

A mill or bakery a manor holds by custom is already inside its 20
pounds, so its tick adds nothing (p. 85).

The panel shows:

- **Peasant land** (p. 72).
  - Hides: 120-144 acres, 4 pounds to the lord.
  - Virgates: 24-32 acres, a family worth about a pound a year.
  - Bovates: half a virgate.
  - Cottars: ten acres or less.
  - The usual spread is 20% virgaters, 30% bovaters and 50% cottars.
- **Demesne flock**: 600 sheep, over 1,000 on marshland and 300 in
  wooded land. That's two-thirds of the manor's sheep. The swineherd's
  pigs are a quarter of the flock.
- **Crops**: a winter crop sown at 2 bushels an acre reaps 8, a spring
  crop 4 reaps 16 (p. 76).

The manor court's fines and dues are ticks and a line of notes (pp.
79-82). They are entry fine, heriot, mortuary, tallage, merchet,
leywrite, childwrite, and fines for celibacy and for being fined
elsewhere. The book gives no sums, and tallage may be as high as the
lord wishes. Add, edit or delete a manor.
<!-- tui -->
More (`m`) on the Manors list:
<!-- /tui -->
<!-- gui -->
The Manors list's own buttons:
<!-- /gui -->

- **Buy a Manor** adds one at its price, 30 to 50 times its 20 pounds a
  year: 600 to 1,000 pounds (p. 85).
  - It's less if the seller keeps some of its rights or you take on its
    dues, and better for coin in hand.
  - It's more when the seller's lord takes a cut.
  - A covenant may pay from its Wealth. A lord pays from **Coin in
    hand** (on Edit Lord), or else by installments from the yearly
    surplus, which the result counts in years.
- **Assart** clears the chosen manor's waste. A strong laborer with
  proper tools clears an acre of lightly wooded land a month doing
  nothing else (p. 84, errata p. 74). Villeins clearing between their
  duties are much slower. Land cleared by magic overnight alarms the
  neighbouring lords. Type the acres cleared for either.

**The Hunt** (More, on the chosen manor) rolls a day's hunt there.

- *Hunting with hounds* (Lords of Men pp. 51-53).
  - Before dawn each huntsman quests with a lymer. Perception + the
    lower of their own and the lymer's Hunt against 9 tracks a fit
    beast. Presence + Animal Handling against 9 keeps the lymer quiet.
    Intelligence + Hunt against 9 judges its age and condition.
  - At the assembly the hunters read the droppings (Perception + Hunt
    against 12).
  - The book calls none of these stress rolls, so all take a simple
    die. It names a stress die wherever it wants one.
  - Then the chase, an hour a round. The pack's Pursuit Total is the
    best dog's Perception + Hunt + its +2 to Hunt rolls + a stress die,
    less the pack's Fatigue. The quarry's Evasion Total is Dexterity +
    Athletics + the Terrain Bonus + a stress die, less its Fatigue.
  - Four rounds won by either side, not necessarily in a row, corner
    the quarry or lose it. A tie counts for neither. Nightfall ends the
    chase with the quarry escaping.
  - The book counts Fatigue only as a penalty to each total. So a
    quarry or pack spent past its last Fatigue level, cornered or giving
    up, is the app's gap-fill, and the Diary says so.
  - The hounds and the quarry each lose a Fatigue level an hour unless
    Stamina + Athletics + a simple die makes 12.
  - Each hunter rolls Dexterity + Ride + a stress die against 6 an hour
    or falls behind. They roll Stamina + Ride + a simple die against 9
    every three hours or lose a Long-Term Fatigue level (p. 52).
- *The Terrain Bonus* (p. 53) starts at +6 for a beast on its own
  ground.
  - The relay's huntsmen roll Intelligence + Hunt + 6 + a stress die
    against the Evasion Total for fresh dogs. Then Intelligence + Area
    Lore + a stress die takes 1 off it.
  - Each hunter still with the pack rolls Perception + Area Lore + a
    stress die to take 1 more off.
- *The quarry* (p. 54), by the Definitive Edition's stat blocks:
  - the hart (spring and summer)
  - the boar (summer and autumn)
  - the bear (any season but spring)
  - the wolf
  - the hare (p. 58)
  - any beast of the saga's Bestiary
  - A dangerous beast's kill is fought out as a melee.
- *Hawking* (pp. 57-59). The hawker rolls Presence + Animal Handling +
  a simple die on the book's table. The Gift's penalty applies.
  - On 7 or more the bird strikes at the prey (p. 58's table), with a
    bonus as the roll rises.
  - On 0 or less, a Loyalty check (a simple die against 6), or the bird
    is gone for good.
  - At 21 or more it goes on attacking after the first strike, hit or
    miss. The book sets no limit. The app stops it on a kill, and after
    five strikes by its own limit, not the book's.
  - A goshawk or merlin won't stoop at prey too large unless trained to
    it (p. 59).
- The inspector shows the holding's kennels or mews and a lord's hunting
  rights. A hunt needs a dozen running dogs and a lymer (p. 60).
- Hunt writes the day in the Diary of each hunter and huntsman named and
  of the lord or covenant. It takes the Long-Term Fatigue it cost.

**Area Lore** (More, on the chosen manor) rolls Intelligence + Area Lore
+ a simple die against a line of City & Guild's Area Lore Ease Factors
(p. 83). They run from a hunting spot or a major inn at 6 to smugglers
and faerie trods at 18.

- One who lives in a town subtracts 3 seeking in the hinterland, and
  one who lives in the country 3 in the city (p. 82).
- Success means they know where it is or whom to ask. Charm or Bargain
  win it.
- It's written in the seeker's Diary.

### Establishments
<!-- help: section-establishments -->

Kennels, mews and stables (LoM pp. 58-61).

- **Each quality** has its capacity, maintenance, staff and Living
  Conditions for the animals (p. 60). The Excellent stables follow the
  errata's moved row: 40 horses, 3 pounds a horse, 12 staff, +2 (errata
  p. 74).
- **Young and breeding stock** may add up to a third again of the
  capacity (p. 58).
- **Cost.** A stable that befits its owner costs nothing: a knight's
  Standard, an earl's Excellent. The app takes a landed noble's to be
  Superior, and a baron's, count's or duke's Excellent. A covenant pays
  for anything better than Standard. Kennels and mews always pay
  (p. 59).
- **Staff.** Superior and better need a specialist: a marshal, falconer
  or master of kennels. A positive Living Conditions needs one with the
  Profession at twice it. Or someone with Animal Handling at three times
  it can give the establishment a season a year (pp. 59-60).
- **Unpaid upkeep.** Marking a year's upkeep unpaid drops the
  establishment a class at once. Each season it stays unpaid, it loses
  15% of its animals, rounded up, as the season ends (p. 59).
- A covenant's upkeep isn't counted in its Treasury. Enter it with the
  covenant's expenditure if it pays it.

<!-- tui -->
More (`m`) > **Winter Roll**
<!-- /tui -->
<!-- gui -->
**Winter Roll**
<!-- /gui -->
on the chosen establishment, once a year in winter, rolls a stress die
+ Intelligence + Animal Handling against 9. Profession: Marshal,
Falconer or Master of Kennels may stand in for Animal Handling.

- A failure drops it a class until a success in a later year brings it
  back one. Its maintenance stays as it was.
- A botch is a catastrophe, such as a fire, disease among the animals,
  theft, or a story to resolve (pp. 60-61).

Add, edit or delete an establishment.

### Household
<!-- help: section-household -->

The lord's household (LoM pp. 9-12). Edit Household changes it.

- **Size**: loosely, a lord of the manor about 10, a landed knight 16, a
  banneret 24, a baron 40, an earl 140. The mesnie's knights are counted
  in it.
- **Mesnie**: the household knights. A wealthy lord keeps eight to ten.
- **Heirs**.
- **Custom** the lands pass by.
  - To the heir the lord names, or the eldest, or the strongest the
    liege chooses. Or divided between the sons.
  - With no son, where the eldest takes all, local custom decides. A
    daughter takes the land intact, or it's divided between the sisters
    or their husbands.
  - Where land is split between all the siblings, daughters inherit
    alongside their brothers (DE p. 512; LoM p. 10 agrees).
- **Relief** the heir owes the liege.
- **Hunting rights**. Warrens, chases and parks are the lord's alone,
  forests the king's (pp. 48, 79).

<!-- tui -->
More (`m`) > **Settle an Inheritance**
<!-- /tui -->
<!-- gui -->
**Settle an Inheritance**
<!-- /gui -->
passes the lands to the heir.

- The heir becomes the record's ruler.
- The relief owed the liege is noted.
- Divided lands are shared out among the heirs. Give each heir's manors
  a record of their own.
- A widow keeps her third (see [The Terms](help:section-nb-marriage)).
  It's ticked already when the lord's last marriage in **Marriages**
  stands, or ended with the lord's death.
- The lord's Diary keeps it.

## Marriages
<!-- help: tab-nb-marriages -->

A lord's family's marriages and betrothals, and the terms of the one
that stands, with what follows from it (Lords of Men pp. 10-11). A
marriage is kept once and shown on the page of each house it joins,
the bride's and the groom's. A lord who marries shows it on their own.
<!-- tui -->
Choose a marriage to see it in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a marriage to see it in full in the inspector.
<!-- /gui -->

### The marriages
<!-- help: section-nb-marriages -->

The marriages joining the house, the lord's own family's spouses first.
Each shows when, the dowry, and where it stands: betrothed, married,
ended by a death, or separated. Arrange a Marriage adds one. Edit or
delete one.
<!-- tui -->
More (`m`) > **End a Marriage**
<!-- /tui -->
<!-- gui -->
**End a Marriage**
<!-- /gui -->
records how the chosen one ends.

### The Terms
<!-- help: section-nb-marriage -->

The marriage that stands, or the last one, named for the couple. It
shows:

- the bride and groom, with their ages from their sheets
- the custom that governs the dowry
- the dowry, or a dower for an heiress
- the consents
- what the Church asks. That's only a spoken intent and a dowry, though
  it prefers a priest and two witnesses (LoM p. 10).

**What follows:**

- An heiress keeps her own fief while married, except in England, where
  her rights become her husband's (DE p. 512).
- Her dowry is managed, kept or taken by her husband as the custom says
  (LoM p. 11).
- A widow keeps the profit, not the income, of a third of her late
  husband's land until she remarries (DE p. 513). That wins over Lords
  of Men's third of the estate (p. 11).
- If they part, a dowry goes back to her family.

A warning shows:

- when her father withholds consent. In many places that stops it,
  though no Christian father may choose her husband (LoM p. 10).
- when she hasn't consented. Then there is no sacrament.
- for close kin or bigamy.

Edit Terms edits it.

## Arrange a Marriage
<!-- help: arrange-marriage -->

Who marries whom, the houses whose pages show it, when, and whether
they are betrothed or married. Each spouse is a character of the saga,
a lord of the Region, or a name typed in. Then choose the bride's
family, which sets her dowry:

- **Noble** (LoM p. 11): an equal share of her parents' land between
  their children.
  - In the French sphere the eldest son and the patrimony both come out
    of the division. Enter the patrimony and count all her parents'
    children, and the eldest son is left out of the sharing.
  - The book then lists what makes a dowry larger or smaller, and gives
    no figures. Tick the statements true of her. Each ticked makes it
    larger, each not smaller. The statements are:
    - her groom's family is wealthier
    - she is one of many acceptable brides
    - she is not a virgin
    - she is less than ten years younger than the groom
    - she will receive nothing after
    - she has fewer siblings than most, mostly brothers
    - she will find it hard to get money from the heir
    - she is paid in other rights rather than land or money
  - The Contract works out the share and counts them. The troupe settles
    the figure and types it as the dowry agreed.
  - An heiress brings no dowry. The groom's family may pay her father a
    dower instead.
- **Merchant** (City & Guild p. 113, as the errata p. 57 corrects it).
  - When her father's Social Status is the same as the groom's, or one
    level higher, the dowry is 10 times the father's yearly profit
    divided by the father's children, married daughters left out. It's in Mythic
    Pounds.
  - The same statements make it larger or smaller. But hers is larger
    paid in assets (land or goods) rather than money. Two more count:
    paid in instalments, and her parents would seem richer than they
    are.
  - Two levels higher, the father raises the groom instead. The groom
    becomes a Poor member of the status just below the father's, and
    the groom's surplus Labor Points are lost.
  - A daughter who will inherit the business likely brings no dowry.
- **Peasant**: no figure in the books. Serfs of different lords need
  their lord's leave, bought with merchet. It costs more for a large
  dowry, or when she moves to her husband's lord's manor (LoM p. 81).
  The manor court keeps it.

The custom for the dowry is each marriage's own (LoM p. 11):

- **Italy, or much of France.** The husband manages it but may not
  spend it, may be sued for mismanaging it, and gives it back if they
  separate. Only Italy's sends it to her children or her parents if she
  dies first. For France the books are silent, so the troupe decides.
- **Parts of France.** The husband may keep much of it.
- **England.** Everything she has becomes her husband's.
- **Another** the troupe sets.

Her consent is needed for the sacrament, and her father's where custom
asks it. Marriage between close kin and bigamy are canon crimes (The
Church p. 37; LoM p. 82). Since 1215, close kin are those sharing a
great-great-grandparent. A marriage blessing is a petition at Ease
Factor 3 (The Church p. 47). **The Contract** says all this as you fill
the form in.

## End a Marriage
<!-- help: end-marriage -->

How the chosen marriage ends, and when.

- **He dies first.** She keeps her widow's third (see
  [The Terms](help:section-nb-marriage)). If she was landed at her
  marriage, with no adult sons, she likely keeps her own lands outright
  (DE p. 513). When the husband is a lord of the Region, Settle an
  Inheritance follows with the widow ticked.
- **She dies first.** Her dowry goes by its custom (see
  [Arrange a Marriage](help:arrange-marriage)). Her own fief goes to her
  eldest son where the eldest takes all, or to one of her sons where
  land is divided (DE p. 512).
- **They separate**, or it's annulled. Separation, not divorce, is
  allowed in many places for infidelity. Her dowry goes back to her
  family, in part or whole, and among nobles this can start a feud (DE
  p. 148; LoM p. 11). Annulling a marriage of common folk is a petition
  at Ease Factor 9 (The Church p. 47).

Both families' Diaries, and the spouses' own, note it.

## Castles
<!-- help: section-nb-castles -->

The lord's castles, each with its garrison, defences and supplies. Add,
edit or delete one.

## Gratitude
<!-- help: section-nb-gratitude -->

The Gratitude the lord owes each character who has served them. A
story that serves the lord's interest earns 1 point, or 2 if it was the
story's aim. A renowned feat earns 5. Each line says which of the
rewards below its points are enough for. Add, edit or delete one.

<!-- tui -->
**Redeem Gratitude** (More, `m`, on the chosen debt)
<!-- /tui -->
<!-- gui -->
**Redeem Gratitude** (the row's Redeem Gratitude button)
<!-- /gui -->
spends the points the lord owes for a reward from Lords of Men's
Advancement Requirements Table (p. 8):

- **5 points**: serf to freeman, warrior to knight, knight to bacheler,
  or bacheler to carissimus.
- **10 points**: a manor, added manors, banneret to baron of a minor
  lord, appointment as baron, or an officer's post under a greater
  baron.
- **20 points**: minor baron to baron of the king.
- **Money and goods** for whatever the troupe agrees.

Most steps also ask a story event, a Reputation for loyalty or an
office's Abilities. The form names them but leaves them to the troupe.
The points come off the debt, and the reward is written in the lord's
Diary and the character's. A step that brings a Social Status Virtue
says so, such as Knight or Landed Noble. Add it to the character's
Virtues yourself (Lords of Men p. 7).

## Battles
<!-- help: section-nb-battles -->

The battles the lord fights, on either side, played as Lords of Men
plays them. That means a few heroic events, each with a player
character at its heart, rather than every blow. A battle is kept once,
in the saga's [Conflicts](help:conflicts), between two armies. Each
army is a lord, town or other power of the Region, a covenant, or just
a name. So a battle between two lords shows in both lords' **Fief**.

Each line shows:

- the two armies, in combat groups of five men
- the first army's **Ground** (Territorial Advantage), its commander's
  [Deployment Total](help:battle-muster) less the other's
- the first army's **Numbers** (Weight of Numbers): +1 with half as many
  groups again as the other, +2 for twice as many, +3 for three times,
  +4 for four times or more, and as much below 0 when outnumbered
- the events it has won and lost so far

Add, edit or delete one. Added here, a battle's first army is this
lord.

- An army's groups left blank are filled in from a lord's title: the
  knights, serjeants, infantry and levies, in groups of five. You add
  the allies and mercenaries.
- Blank baggage is as much as the army needs.
- The form asks whether each army fights on its home ground. Only then
  does a lord's title raise the levies (Lords of Men pp. 31, 102).

**At sea: a fleet battle.** Set *Fought* to *At sea* and the battle is
fought between fleets (Tales of Power p. 106).

- Each army ticks its ships. When an army is a covenant, every ship on
  its
<!-- tui -->
  Possessions
<!-- /tui -->
<!-- gui -->
  Inventory
<!-- /gui -->
  is listed, all ticked at first. A wrecked one is left out of the
  count.
- *Other ships* counts those kept on no covenant's list, such as a
  pirate fleet or ships hired.
- Weight of Numbers counts ships, not combat groups. 3 ships against 2
  is +1 (Lords of Men p. 105's ratios).
- Combat groups left blank are the picked ships' crews and fighting
  men, in groups of five.
- The *pilot*, anyone with a seafaring Profession, replaces Area Lore in
  the Deployment Total. That's Intelligence + the pilot's Profession +
  stress die (ToP p. 106). The inspector shows the sum to roll against.
- *Bearded* ships, with iron plates on the bow, are appreciably slower.
  But the plates are armour, so the ship is more resistant to damage,
  and it rams and takes collisions better. The book gives no figure, so
  the storyguide sets the bonus in an event (ToP pp. 106, 110).
- Boarding is fought much as on land.

## Sieges
<!-- help: section-nb-sieges -->

The sieges the lord lays, or holds out in, kept in the saga's
[Conflicts](help:conflicts). Each is a siege whose besieging lord, or
whose castle in the Region, is this lord. Each line shows the castle and
its besieger, the Garrison, Defenses and Supplies, and how long it has
run.

Add, edit or delete one. Added here, this lord is the besieger. Link the
castle to the lord, town or place being besieged. A garrison or
besiegers' soldiers left blank are filled in from the linked lords'
armies. Play it from Conflicts with Next Siege Event; see
[A siege](help:sieges).

## Combat Options
<!-- help: combat-options -->

More (or the button) on a fight works out Lords of Men's optional combat
rules (Chapter Nine) for one of its characters, to play at the table. It
changes nothing in the fight. Choose the **Option**:

- **A charge, and its shock** (on foot p. 123, mounted pp. 126-127). It
  gives the Combat Ability added to the Attack and the Fatigue it costs,
  the horse's when mounted. It also gives what the one charged rolls to
  resist its shock.
- **A horse's gait** (p. 127, with the Errata's corrected table, p. 75).
  It gives the missile penalty, falling damage, extended-action Ease
  Factor and optional Defense bonus.
- **Cover, concealment and higher ground** (pp. 130-131).
- **How many may attack one man** (p. 131).
- **Interrupting** (p. 119): Quickness + the Ability - Encumbrance.
- **Into and out of the saddle** (pp. 127-128).

Add Combatant also offers **A standard combat group** (p. 108). That's
five knights, serjeants, infantry, archers, levies or baggage with the
book's figures, formed into a group as they're added. Knights, serjeants
and infantry are trained, the rest untrained.

## Muster and Aftermath
<!-- help: battle-muster -->

More (or the button) on a battle, for what comes before and after its
battlefield events (Lords of Men, Chapter Eight):

- **A crusade** (p. 104). Tick it on Raise Allies for a churchman with
  Senior Clergy. The Affinity is the most prominent noble's of the
  churchman's diocese, rolled on the Allied Troops Table. The book names
  an Army Size Table that doesn't exist, and Holy Influence (Realms of
  Power: The Divine p. 38) has no Affinity in it, so this is the app's
  reading.
- **Raise Allies** (pp. 102-103).
  - Give who calls them, their Affinity score and their core vassal
    groups. The lord's title gives the groups, levies only on home
    ground.
  - Tick the Allied Troops Table's modifiers that apply.
  - Roll Presence + Leadership + Affinity + a simple die. 6 adds half
    the core force, 12 as much again, 18 double, 24 treble.
  - The allies join the side.
- **Hire Mercenaries** (pp. 103-104). Groups of knights, serjeants,
  infantry, archers and levies cost 15, 5, 2, 2 and 1 pounds, up to the
  lord's Mercenary Budget.
- **A War Loan** steps the lord's wealth down for five times the budget
  given up.
  - An Average lord becoming Poor borrows five times their budget.
  - A Wealthy one becoming Average gains five times the difference of
    the two, or becoming Poor five times the Wealthy budget.
  - A Poor lord can't borrow.
  - The loan and the new wealth's budget are what the lord may spend.
    The book doesn't say, but its "five times the difference" points
    that way. It also makes the two routes to Poor come out the same.
    For a baron, Wealthy to Average is 300 + 40 = 340 pounds.
  - The lord needs a banker able to lend that much and to collect on a
    default. The loan may take weeks, so it doesn't suit a lightning
    war.
  - The loan is repaid from spoils or stories. The book leaves to you
    whether it lowers next year's budget, and when the lord regains the
    old wealth. The app doesn't restore it.
- **Roll a Deployment Total** (pp. 104-105). Intelligence + Area Lore +
  a stress die for the one who chooses the ground, the commander or a
  lieutenant, plus the highest magnitude of a spell that shapes it in
  the commander's favour.
- **End of the Day** (pp. 108-109). A side wins, or a truce holds at
  nightfall.
  - The victors who led events gain a Confidence Point for each event
    their side won.
  - Their commander gains an experience point toward a Reputation.
  - No more events follow.

A side keeps the groups it raised or hired by kind. So an event's
losses come first from the kind its Enemy names (p. 106):

- levies for Inexpensive
- infantry and archers for Standard
- knights and serjeants for Expensive

Leading an attack on the baggage gives 1 xp toward a bad Reputation. A
magus casting in a battle makes a Concentration roll against 12, or 9
if not yet engaged (p. 109). Roll it at the table.

## Battle Event
<!-- help: battle-event -->

<!-- tui -->
More (`m`) > **Battle Event** plays the chosen battle's next event.
<!-- /tui -->
<!-- gui -->
**Battle Event** plays the chosen battle's next event.
<!-- /gui -->
Choose the character **Leading the event** and the army they are
**Fighting for**. Then choose:

- **Maneuver**: Defend +0, Attack +1, Run the Gauntlet +2, Take +3, a
  Heroic Gesture +4.
- **Enemy**: Inexpensive troops such as levies +0, Standard +1,
  Expensive such as knights +2, Special +3, the Baggage +4.
- **Size**: Lesser +0, Even +1, Outnumbered +2, Overwhelmed +3, I Stand
  Alone +4.

The line above Record shows the Event Total. It's the character's
Stamina + Leadership + their army's Ground and Numbers + those three,
+1 for giving up the initiative. It must reach the stage's Ease Factor
to be won at all:

- 9 for the first event (Engaged)
- 12 for the second (Advantage or Setback)
- 15 for the third and any after (Imminent Victory or Defeat)

**Play it out as a fight.** Tick it to have the event made into a fight
on Conflicts (Lords of Men pp. 105-108).

- The leader and their own group fight. The group, **His group** on the
  form, comes from the Standard Combat Groups table (p. 108).
- They face the groups the Size sets. Lesser is one about half theirs,
  Even one, Outnumbered two, Overwhelmed three. I Stand Alone is the
  leader alone against a full group.
- The foes are the troops the Enemy names (**Their troops**): levies,
  infantry or archers, knights or serjeants, or the Baggage guarded by
  levies. A Special enemy is the storyguide's to add with Add Combatant.
- Weight of Numbers adds as many men to each group of the side it
  favours.
- Knights, serjeants and infantry fight as trained groups.
- The leader fights with the first weapon they carry. Edit Combatant
  changes it.
- Play it, five rounds unless the event says otherwise. Then open Battle
  Event again. It's filled in as you left it, and the line above Record
  says what the fight showed.

**How it went.** Say it by the Maneuver's own condition (pp. 106-108):

- A Defend is won by beating the attackers or holding for the rounds
  set.
- An Attack is won by defeating or routing them.
- Run the Gauntlet is won by reaching its objective.
- A Take is won by taking it and holding it against the counter-attack.
- A Heroic Gesture is won if its leader dies, or survives meeting the
  storyguide's conditions. It's lost if another player character is
  killed.

**Record.**

- The side that lost loses the groups the fight cost it. When the
  winner has the greater army, it loses as many more as the event's
  Size times the winner's Numbers.
- The next event's Numbers are worked out from what is left.
- After an event, type the losing commander's **Morale** roll: Presence
  + Leadership + a stress die, against 6. If it fails, type their
  **rally** at the next event, against 9.
- A failed rally disorders the army. A second, while it's still
  disordered, routs it and ends the battle (Lords of Men p. 106).
- While an army is disordered, the next Battle Event offers **A rally
  by** a player character who takes command. Type their roll (Presence
  + Leadership + a stress die against 9, p. 135), or a story event
  played for it, won or lost. A rally lifts the army a step, routed to
  disordered, disordered to steady.
- With Morale and Discipline on, a disordered or routed army's groups
  start its event's fight that way (see [Discipline, Morale and
  rallying](help:group-morale)).
- Each event recorded is written as a line in the Diary of each army's
  lord or covenant (see [A lord's Diary](help:tab-nb-lord-diary)) and of
  the leading character.

Allies and mercenaries are raised before the battle (see
[Muster and Aftermath](help:battle-muster)). Every ten groups need a
group of baggage, and each one short is -1 to the Event Totals.

**An event at sea.** In a fleet battle the event is told at sea, such as
cutting off part of their fleet, boarding their flagship, or bringing
down the mast that flies their signals. Intercepting them with swift
ships, or another, also serves.

- Tick the ships *engaged* in it, and how many of each army's other
  ships. At first that's every ship, later the ones engaged last time.
- Only the engaged ships count for this event's Weight of Numbers, so
  beating part of their fleet alone pays (ToP p. 106). The losses it
  causes use that figure.
- *They throw naptha bombs*: +5 damage, and the ship is set alight.
  Water won't put it out, but a great deal of sand will (ToP p. 110).

## Draft the Charter
<!-- help: draft-charter -->

A season's work by one side's notaries (Transforming Mythic Europe p. 36). The principal notary's Intelligence + Civil and Canon Law + a stress die is that side's Charter Strength. Tick **In England** for an English charter: its notaries use Common Law instead, and only it. The tick is kept on the lord, whose form has it too. There are 3 botch dice, one fewer for each notary beyond the first. A botch leaves the strength at 0, no legal defence.

## Seek a Loophole
<!-- help: seek-loophole -->

A season examining the charter and its legal texts, then Intelligence + Civil and Canon Law + a stress die against the other side's Charter Strength (Transforming Mythic Europe p. 36). For a charter in England it's Common Law, and only it. Higher finds a loophole: legal grounds to break one or more of its provisions, noted on the lord. The other side's strength must be drafted, or typed, first.

The book gives the search no botch dice, so the app rolls one. A botch is a total of 0, and something goes wrong as the storyguide decides (DE p. 7). It might be a false loophole the searcher believes in, or the other side learning of the search.

# A town
<!-- help: tab-nb-town -->

A town (City & Guild) has a charter, a council and a population,
entered on New Town or Edit. The charter is granted by a noble lord or
the Church, held by its townsmen as a commune, or a faerie's or a
demon's.

Its **Town** shows them with its [size](help:section-nb-town-people),
its fairs and markets, and how many
[guilds](help:section-nb-guilds) a town its size has. Its
charter in full, its guilds and its court have pages of their own:
[Charter](help:tab-nb-charter), [Guilds](help:tab-nb-guilds) and
[Court](help:tab-nb-court).

**See also:** [A neighbour](help:neighbour)

## Charter
<!-- help: tab-nb-charter -->

The town's charter (City & Guild, Town Charters, pp. 8-14). It shows
who granted it and how they hold it, its terms, what it gives, the
saga's characters who are its citizens, and the town's size and people.
<!-- tui -->
Choose a lord or a citizen to see them in full in the details panel.
<!-- /tui -->
<!-- gui -->
Choose a lord or a citizen to see them in full in the inspector.
<!-- /gui -->

### Lords
<!-- help: section-nb-charter-lords -->

Each lord of the charter: a noble, the Church, a faerie or a demon. It
shows how the lord holds it, their share of the revenue in words, and
since when.

- **Sole**: the lord holds it alone.
- **Shared (paragium)**: lords granting in partnership. They split the
  revenue by an agreement older than the charter (p. 10).
- **Rival**: a contested claim, or a faerie lord's rival charter (pp.
  9-10).
- **Parallel**: a secret demonic charter beside a mundane one (p. 11).

A demon's entry also ticks the services it offers. Add, edit or delete
a lord.

With the saga's Charter Strength option on, each lord's charter has two
scores, worked as a covenant's are (see
[Charter lords](help:section-cov-charter-lords)).

### Terms
<!-- help: section-nb-charter-terms -->

The charter's family, the year it was granted, the burgesses, and its
privileges. The family is the law it shares with other towns, such as
Lorris, Breteuil, Freiburg, Lübeck or Cuenca. Each privilege is held or
not, some with a word on what exactly:

- the annual tax (40 pounds for a town of several hundred burgesses, p.
  12)
- its own courts
- ordeal and combat limited
- a cap on fines (Breteuil's is 12 pence)
- monopolies and toll exemptions
- a market or fair
- salvage
- choosing its officials
- selling land (pp. 12-13)
- militia duty (p. 10)

Edit Terms changes them.

### What it gives
<!-- help: section-nb-charter-gives -->

- **The Divine aura** within the walls.
  - A town's or city's normal 3 (Definitive Edition p. 418, which wins
    over Realms of Power: The Divine's town 2).
  - One higher, 4, under a charter the Church holds (C&G p. 10: "one
    higher than would be normally expected").
  - 1 under a faerie charter, which a stronger Faerie aura may swamp (p.
    11).
  - A shared charter keeps the normal aura unless **The Church holds the
    charter** is ticked. A rival claim or a secret parallel charter
    changes nothing.
  - Churches inside keep their own aura.
- **A demon's charter** has its Infernal Might 15 (Mentem) and the
  services it gives (p. 11):
  - relief from disease (+2 Living Conditions)
  - help for merchants (+3 to Bargain and Profession: Merchant)
  - dangerous labor
- **The pawn.** The signed charter holds a pawn of Rego vis tainted by
  the Divine, more for very large towns. Taking it destroys the
  charter's sympathetic connections (p. 9).

Edit changes the Church's tick, the pawns and whether the vis was
taken.

### Citizens
<!-- help: section-nb-citizens -->

The saga's characters who live in the town, from the season they came.
A year and a day of residence makes a townsman (p. 9), shown as the
season a year later.

- A citizen has a sympathetic connection to everyone under the same
  charter, its family's other towns too. That's +1 to the Penetration
  multiplier of a spell against them, until the charter's vis is taken.
- Becoming a citizen of another town ends the old connection. So adding
  a citizen here takes them off any other town's list, and the form says
  so first.
- Clerics are rarely citizens (pp. 9-10), and the panel warns.

Add, edit or delete a citizen.

### Size and people
<!-- help: section-nb-town-people -->

The population and its size, the burgesses, the council and the
magistrates. The size is a small, medium or large town, or a city. A
city is one by right, or one of 20,000 or more. An average town has up
to six magistrates (p. 29).

Occupations share the people by size (p. 24):

- a small town: half farmers, half craftsmen
- a medium town: 10% farmers, 50% craftsmen, 30% in service, 10%
  traders
- a large town or a city: 10%, 30%, 30%, 30%

The officials are a line each, Title: who (pp. 13-14). The titles are
aldermen, bailiffs, consuls, coroners, councilors, magistrates, mayors,
ministerials, portmen, rectors and reeves. Edit changes them.

## Guilds
<!-- help: tab-nb-guilds -->

The town's guilds and the saga's characters in them (City & Guild,
Chapter III, pp. 41-50).

### The guilds
<!-- help: section-nb-guilds -->

Each guild shows:

- its trade and kind: craft, service or merchant (p. 41)
- the Craft its members practise
- its hall and its dean
- its officials. Most guilds have six, chosen from the senior masters
  for six months (pp. 49-50).
- its members by rank: senior masters, masters, journeymen, apprentices

The line above the list says how many guilds a town its size has in the
saga's year (p. 54). Choosing a guild shows its ranks, the saga's
characters in it, and how members rise:

- an apprentice piece after seven years: a stress die + a
  Characteristic + Craft against 9 (p. 45)
- 12 to join another town's guild (p. 47)
- a master pays about a year's income and needs the senior masters'
  vote (p. 47)

Renaming a guild keeps its members. Deleting it takes them out.

### Members from the saga
<!-- help: section-nb-guild-members -->

The saga's characters in the town's guilds, each with their guild and
rank. The list shows their Craft and Guild Lore, and whether they have
what the rank needs (pp. 43-50). The Craft is the guild's, as Craft: or
Profession:.

- **Guild Lore**: 1 a journeyman, 2 a master, 3 a senior master or
  dean.
- **Craft**: 5 a journeyman or master, 7 a senior master.
- **Leadership** half the Craft score, and **Artes Liberales**, for a
  master or above.
- **The rank's Social Status Virtue**: Guild Apprentice, Journeyman,
  Guild Master, Senior Master, Guild Dean.

Choosing one shows the rough guide for their rank by age (p. 42) and
what they lack. Add one once the guild is listed.

## Court
<!-- help: tab-nb-court -->

The cases before the town's courts and the sentences they pass (City &
Guild, Crime, pp. 28-30).

### Cases
<!-- help: section-nb-court-cases -->

Each case shows:

- the accused and the charge
- the accuser. A kinsman accuses for the dead.
- the court. Churchmen, commercial law and heresy go to the Church's
  courts (p. 29).
- the verdict and, if guilty, the sentence and its detail. A fine left
  unpaid makes the accused an outlaw (p. 30).

<!-- tui -->
More (`m`) > **Court Roll** decides the chosen case.
<!-- /tui -->
<!-- gui -->
**Court Roll** decides the chosen case.
<!-- /gui -->
It rolls a stress die + Communication + Civil and Canon Law against 6,
for the defendant or their proxy. In England it's Common Law. Success
finds the defendant innocent (p. 29).

- It's a social roll, so the arguer's Gift counts: 3, or 6 for a
  Blatant Gift. An unGifted proxy avoids it (DE p. 204).
- Enter any other social Virtues and Flaws as a + or -.
- The Ease Factor is 3 lower if the defendant truly is innocent. It's 3
  higher for a bad name in that court, and 3 higher if most credible
  witnesses say guilty.
- Under Civil Law, Artes Liberales (logic) can shake a witness's
  credit. The inspector shows the arguer's score. Untick the witnesses
  if the storyguide allows it.

The inspector, The Verdict, shows the total and the die needed as you
choose. Roll keeps the verdict and the roll on the case, then Edit
passes sentence. Add, edit or delete a case.

### Sentences
<!-- help: section-nb-sentences -->

What the guilty face (p. 30):

- **Death** for thievery, robbery, house-breaking, arson, premeditated
  murder and treason.
- **A fine**, a few pence to 50-60 pounds, for murder, accidental death,
  rape, assault, petty thievery and failing the charter's duties.
  Unpaid, it makes the guilty an outlaw.
- **Mutilation** (an eye, ear or hand) or **branding**, instead of a
  fine or beside it.
- **Shaming** in the stocks or pillory for minor crimes.

A defendant who insists they're innocent may choose a trial by ordeal,
which many charters limit or ban.

## Fairs and markets
<!-- help: section-nb-fairs -->

The town's fairs and markets, each with its season. A fair a covenant
trades at is a source of income to it, by its size, or the income
entered:

- a town's yearly fair: 40 pounds a year
- a county fair: 100
- a fair that draws traders from across Europe: 250

<!-- tui -->
More (`m`) > **Roll Income** rolls the chosen fair's year.
<!-- /tui -->
<!-- gui -->
**Roll Income** rolls the chosen fair's year.
<!-- /gui -->
A stress die picks the Income Modification:

- a botch: a Slump, x0.5
- 0: a Contraction, x0.8
- 2: Stagnation, x0.95
- 3 to 8: Status Quo
- 9: Growth, x1.05
- 10 to 19: Expansion, x1.2
- 20 or more: a Boom, x1.5

Keep records the new income and the roll. Add, edit or delete a fair or
market.

# A church
<!-- help: tab-nb-church -->

A church (The Church) has a kind and an order, entered on New Church or
Edit. The kind is a chapel, a parish church, a large urban church, a
monastery or nunnery, or a bishop's or an archbishop's cathedral. Its
**Church** shows its Dominion aura: a chapel's 3, a parish church's 4,
any greater church's 5.

With Realms of Power: The Divine in play, a church also records the
year worship began there, and the year it was abandoned.

- With the **Dominion growth** Rule Option on (Saga Content), its aura
  grows with the years of worship instead. It's 3 when consecrated, 4
  after a year, 5 after a decade, never above its kind's. Once worship
  stops, it fades to nothing over as long as the site was in use.
- Otherwise a church's aura comes from its kind (DE p. 419).
- Either way, a relic with a Faith score above 5 raises the church's
  Dominion by 1 for each point above 5 (Realms of Power: The Divine p.
  12).

With The Sundered Eagle in play, a church's Relics also hold its icons
(The Sundered Eagle pp. 133-135). Choose the Kind.

- **An eikon** has no Faith or Might. Give its Aesthetic Quality. The
  Invoking column shows what venerating it adds to invoking its saint:
  Aesthetic Quality / 5, rounded up.
- **An acheiropoieton**, an icon not made by hand, is a powerful relic
  with a Faith score like any other.
- A character's More, Paint an Icon, adds an eikon here.

**See also:** [A neighbour](help:neighbour)

## Relics
<!-- help: section-nb-relics -->

The church's relics, each with its saint and its Faith score. A relic's
Faith score gives it as many Faith Points and a Divine Might of 10 times
it. Whoever bears it gains as much Magic Resistance.

The Invoking column is what the relic adds to invoking its saint:

- With The Church in play, +2 for each Faith Point, once a day (The
  Church p. 13). That's for the one who tends or carries it, or who
  venerates it a day at its shrine with the custodians' leave.
- With only Realms of Power: The Divine, +1 for touching it (p. 87).

A character's More, Invoke a Saint, chooses it. Add, edit or delete
one.

# A university
<!-- help: tab-nb-studium -->

A university or school (Art & Academe) has a kind and its fees, entered
on New University or Edit. The kind is a university, or a cathedral,
monastic, urban or parish school. Its **Studium** shows:

- **The fees**, blank for its kind's: 4 pounds a year at a university,
  with books, 1 at a cathedral school.
- **The highest an Academic Ability can be taught there**: no limit at a
  university, 6 at a cathedral school, 2 at a rural parish school.
- For a university, **the degrees its faculties grant**.

**See also:** [A neighbour](help:neighbour)

## Faculties
<!-- help: section-nb-faculties -->

The university's faculties (Arts, Medicine, Law, Theology). Each shows
its rector, its endowed chairs (six to twelve) and how many of the
masters listed teach in it. A Faculty of Arts grants the Baccalaureus
and the Magister in Artibus, and each higher faculty its Doctorate.
Add, edit or delete one.

## Masters
<!-- help: section-nb-masters -->

Its masters, each named or chosen from the saga's characters, with
their licence and faculty. A licence starts its holder's Good Academic
Reputation:

- 1 for a Baccalaureus
- 2 for a Magister in Artibus or a cathedral school master
- 3 for a Doctor

Add, edit or delete one.

# A faction
<!-- help: tab-nb-faction -->

A faction (the core rules) is any company with a will of its own. Its
**Faction** says which kind:

- a hedge coven, a magicians' tradition too
- a faerie court
- a gild
- a family or dynasty
- a Hermetic group: a lineage, societas, league, cabal or a House's
  faction
- a people or tribe
- spirits and beings, a host or race of them. One being is a Bestiary
  creature.
- a faith or sect
- a council or assembly
- a military order
- brigands and mercenaries
- a religious community
- an estate or rank
- Other

The books name no list of kinds. These sort what the Tribunal books
describe.

New Faction and Edit record what kind it is, how it decides, how many
members it has, its rules, what it wants and what it offers. It decides
by its leader, a council, or a vote of all. Its **Faction** shows them.

- A hedge coven can also name the hedge tradition its members follow,
  from the traditions the app knows (see
  [A tradition's chapter](help:tradition-chapter)). Then the troupe
  knows which record a member is played from.
- Its named members are listed under
  [Members](help:section-nb-members), and its **Faction** counts them.

Its leader is its [Ruler or leader](help:neighbour-ruler). Its **Answers to** is its
liege or master, not its membership. See
[How to set up a faction's leader and members](help:guide-faction).

### Members
<!-- help: section-nb-members -->

The faction's members, each with their **Role** in it, such as "knight
of the court" or "elder". A member is a character, a covenant, a
Bestiary creature or another neighbour, such as a courtier or a branch
of the gild.

- Add one by choosing their record. Filter the list by Kind, or type to
  search.
- Edit their role, or take them off the roster. Their own record stays.
- A record can belong to several factions, and each one lists it. The
  record's page shows every faction under **Member of**, a character's
  in its [Connections](help:section-connections).
- A member whose record has since been deleted shows as no longer in
  the saga.

Older saves made a faction that belonged to another answer to it, such
as a court's courtiers. It's moved to the other's roster when the saga
is opened. A faction's links stay links, under **Linked from** on the
record they point at. Add a member here to say they belong to it.

**See also:** [A neighbour](help:neighbour)

## Diary
<!-- help: tab-nb-faction-diary -->

What the faction has done, season by season, such as its schemes, its
quarrels, and who joined or left. A faction's Diary is written by hand,
or by a roll on its [Roll Tables](help:tab-nb-tables) for what its
agents are up to this season. It works as a place's
[Diary](help:section-nb-place-diary) does. Add, edit or delete an entry.

# A lord's Diary
<!-- help: tab-nb-lord-diary -->

What befell the lord and their lands, season by season:

- each Battle Event the lord's army fights
- a siege the lord is linked to, as the castle or the besieger, when it
  ends
- a roll on the lord's [Roll Tables](help:tab-nb-tables)
- anything the storyguide writes

It works as a place's [Diary](help:section-nb-place-diary) does. Add,
edit or delete an entry.

# A threat
<!-- help: tab-nb-threat -->

A threat is a story that grows if the troupe leaves it alone, such as a
faerie king gathering a court, a plague or a heresy. New Threat and Edit
record its antagonist and how it moves:

- by **fixed dates**, each stage with its season and year
- along **a track** or **an omen count**, each stage at a number. Edit
  moves the threat's position.

Its **Stages** shows the stage it has reached and the next to come,
worked out from the saga's date or its position. The Region's facts
name the threat whose next stage is due soonest.

Its **Clock** shows how far it has come, as filled squares (■■■□□ 3 of
5). A dated threat has one for each stage, filled as each comes. A
track has one for each step up to its last stage, filled to its
position. The threat's page, its card on the Region and its lines on
Ahead show it.

A threat moving along a track can be moved by a place's
[trigger](help:section-nb-triggers). Each time the trigger comes, its
season asks whether the troupe **failed** it, and the threat moves on,
or **kept** it, and it stays. See
[How to set up a threat's clock](help:guide-threat-clock).

**Take Up the Tale**
<!-- tui -->
(in the threat's More)
<!-- /tui -->
<!-- gui -->
(a button on the threat's page)
<!-- /gui -->
writes a chapter of what the troupe did, met or avoided. It goes in the
threat's [Diary](help:tab-nb-threat-diary) and each troupe covenant's.
A threat grown from a story names it under **Grew from**, a link to the
covenant whose Diary keeps it. See [Take Up the Tale](help:take-up-tale).

**Delay or Hasten**, in the threat's More, pushes it later or brings it
sooner when something the troupe did changes it.

- A dated threat's stages still to come all move by the seasons you
  give. The dates typed stay as they are, and Edit shows the delay so
  far.
- A track's position moves back or on.
- The reason goes in its [Diary](help:tab-nb-threat-diary).

A threat can be **dormant**, a story the storyguide hasn't begun, such
as one left unticked when its pack was imported. It reaches no stage,
nothing of it comes due, and the Tribunal sheet counts it under
**Stories**. **Begin This Story**, in the threat's More, starts it.

- Dated stages move later together, so the first still to come is due
  next season at the soonest.
- A track or omen count starts where it stands.

Its [Roll Tables](help:tab-nb-tables) say how the stage it has reached
shows itself this season. A row rolled is written in its Diary with the
stage it colours. A roll never moves the threat. Its clock moves only by
date, by a tied trigger, by Delay or Hasten, or by Edit.

**See also:** [A neighbour](help:neighbour)

## Stages
<!-- help: section-nb-stages -->

The threat's stages in order. Each has when it comes, the clues that
warn of it, and what happens if it's ignored, stopped or turned.

- A pending stage comes when its date, or its place on the track, is
  reached.
- Mark one **Happened** to say it came anyway, or **Stopped** or
  **Turned** to say the troupe kept it from coming.
- Marking it writes what the stage says follows, its If ignored, If
  stopped or If turned. It goes in the threat's Diary and each troupe
  covenant's, so the troupe sees what comes of it.
- The stage reached is in bold.
- **What the troupe did**, on the stage's form, is optional. Anything
  typed there is written as a chapter of the threat's tale, in its Diary
  and the troupe's covenants'. It isn't kept on the stage.

Add, edit or delete one.
<!-- gui -->
Click a stage to read it in full in the Inspector: when it comes, what
became of it, its clues, and what happens if it's ignored, stopped or
turned.
<!-- /gui -->

## Diary
<!-- help: tab-nb-threat-diary -->

What moved the threat, season by season:

- each answer to a trigger tied to it, failed or kept
- each Delay or Hasten and its reason
- what came of a stage marked Happened, Stopped or Turned
- its chapters, marked "Chapter:": what the troupe did when it took up
  the tale
- each roll on its Roll Tables, with the stage it coloured

A threat grown from a story shows that story and its chapters above the
list. It works as a place's [Diary](help:section-nb-place-diary) does.
Add, edit or delete an entry.

# A place
<!-- help: tab-nb-place -->

A place is somewhere the saga's records can be, such as a forest, a
ruin, a crag or a regio. It's a kind of neighbour without an attitude
or a ruler, listed under Places in the Region. New Place and Edit
record:

- **Ruined covenant**: the place is a fallen covenant's site. It shows a
  broken tower in place of the place's own picture, and "Ruin" in the
  lists.
- **Aura**: the aura of its surface, its mundane level. The Realm field
  says whose.
- **Tethers**: the monuments, creatures or vis sources that anchor it.
- **Status** and **Known**: how far the troupe has got with it
  (rumoured, known, visited, claimed) and how widely it's known.
- **Claimed by**: the covenant that claims it.
- **Tribunal's lands**, once the saga has a Tribunal: the Tribunal whose
  lands the place is.
  - Set it on a region, such as the Black Forest, and everything inside
    takes it, unless a place nearer in names another.
  - This is geography, not membership. A covenant's own **Tribunal**
    (Edit Covenant) is the council it belongs to. So a covenant in the
    Rhine's lands that is petitioning to join lies in the Rhine and is
    no member yet. Its Connections say both.
- **Inside**: the place it's part of, so a regio can sit inside a forest
  inside a county. A place can't be put inside itself or inside a place
  within it.

A covenant, a laboratory or another neighbour names its place with
**Place** in its own Edit form. It chooses the place or one of its regio
levels.

- A covenant placed somewhere takes its aura from there, or from the
  level it's in.
- The aura typed on the covenant is kept, and comes back if it's moved
  out. So its Edit form doesn't ask for an aura while it's placed.
- A laboratory placed in a regio of its own takes that level's aura
  instead of its covenant's.

The place's pages show:

- **Regio**: what is worked out for it, its regio levels, its effects
  and its triggers. What's worked out includes its next trigger, and how
  its aura changes with the Auras change option.
- **Roll Tables** and **Diary**: its tables and what has happened there.
- **Found Here**: its favours and links, such as the vis sources, books
  and creatures found there.

Deleting a place leaves what was in it placed nowhere.

**Found a Covenant Here** (More, on a ruined covenant's site) raises a
new covenant on the ruin, as the Definitive Edition's Winter Ruins
Situation does.

- New Covenant's form opens, named for the ruin and in its aura's realm.
  **Take Winter Ruins** adds that Situation's Boons and Hooks.
- The covenant starts In Creation, sited on the place so it takes its
  aura.
- The place is then claimed by it and no longer a ruin.

A ruin with a regio asks for the covenant's **Site**: its surface or one
of its regio levels, whose aura the covenant takes.

- In a level it takes the **Regio Boon**. It's Minor when entered in
  several ways, Major when entered only with a native guide.
- On the surface, the regio on its site is the **Regio Hook**. It's
  Minor, or Major when its folk come out and make trouble. The
  Non-magical Regio Hook comes too when the regio isn't Magical.

With the **Auras change** Rule Option on (Realms of Power: Magic and The
Infernal, in Saga Content), auras move each winter as those books say:

- **A Magic aura** has a base aura from its **Tethers** (RoP: Magic p.
  8).
  - End each one in the place's Tethers with "(natural 1)" or "(natural
    2)", or "(preternatural 1)" to "(preternatural 5)".
  - A magical being gives its Might / 10, a monument a point a century
    of use, a vis source its yearly pawns / 3.
  - Each winter its yearly modifier adds up:
    - +3 for every point the aura is below its base, -3 for every point
      above it
    - the stronger auras that impinge on it, which Edit asks: Magic +2,
      Faerie +1, Divine -6, Infernal -2
    - +1 to +3 for the magic its covenant works, by the covenant's
      season
    - +1 for each season of vis study there using 3 or more pawns, and
      -1 for each season of vis extraction, both counted from the season
      records
    - **This year's botches and other magic**, which you type
  - From -3 to +3 nothing happens. At +4 or more the year's turn rolls
    on the Strengthening table, and at -4 or less on the Weakening table.
  - The roll takes the **Aura roll botch dice** the place has built up.
    It gains one after every roll of 9 or more, and loses one after a
    year with no roll.
  - A permanent rise or fall changes the aura, or a regio's top level.
    The rest go into the place's Diary.
- **An Infernal aura** inside a **Stronger aura around it** loses 1
  after as many years as its strength. Edit asks the stronger aura's
  score and realm.
  - It doesn't erode when **Kept by a demon or an Infernal
    enchantment**.
  - A corruption roll that keeps it starts its clock again (**Eroding
    since**).
  - Its **Regio** shows the corruption roll's Ease Factors. To keep it
    is 3 + the strongest aura there, and to raise it 6 + that aura.
- **A Faerie aura** follows the glamour of the faerie that claims it
  (Realms of Power: Faerie pp. 14-16).
  - It's the presiding faerie's Might / 5.
  - While another faerie contests it, it's 2 + the higher Might / 5, at
    most 9.
  - While the presiding faerie is away, it's a steward's Might / 5.
  - Each season the magi extract vis there without a bargain with the
    faerie lowers it by 1, until the faerie has had redress. Then set
    **Aura lost to vis taken** back to 0.
  - A faerie that travels takes its aura with it.

Any Infernal place's Edit asks two more things (Realms of Power: The
Infernal pp. 13-15):

- **Tarnished with**: a sinful Personality Trait. Everyone in the aura
  acts as if moved by its strength.
- **Corrupted**: Debauched, Malevolent or Perfidious. Only an aura of 3
  or more can be, with its features written in its Notes.

An aura may have a kind of its own. Edit asks it by the place's realm,
and Add or edit asks it of each regio level by the level's realm:

- **Alignment**, for a Magic aura (Realms of Power: Magic pp. 15-16).
  An aura has at most one.
  - Aligned with an **Art**, its strength counts again in the Casting
    Score of any spell using that Art, as its Technique, Form or a
    requisite. It counts again in a Lab Total of that Art too. Both show
    as "Aura aligned with ..." in the working.
  - With an Art, a creature whose Might is of that Form pays a Might
    Point less for any power that costs one. The opposed Art takes no
    penalty.
  - **Healing** adds half the aura, rounded up, to the Recovery Totals
    of those who live there.
  - **Luck** gives +1, +2 from 5 to 8 and +3 above, to rolls where luck
    matters, for everyone.
  - **Distracting** calls for Concentration rolls more often, their Ease
    Factors 3 higher from aura 5.
  - Any other word is a feeling, such as Aggressive, Carefree,
    Communicative, Respectful or Fearful. After a few minutes there, those without The Gift or
    another Magic power take it as a temporary Personality Trait. It's
    +1 at aura 1-3, +2 at 4-6 or +3 at 7-10, never changing an Essential
    Trait.
  - An aligned aura above 5 slowly warps those who live in it without a
    Magic power.
  - Intellego Vim at level 4 discerns an alignment. A covenant may take
    it as a Boon, Fine Aura if Major or Favorable Aura if Minor, or as
    the Troublesome Aura Hook (p. 16).
- **Tints**, for a Faerie aura (Realms of Power: Faerie p. 104), written
  "Drawn to Children +3; Light +2".
  - Everyone in the aura takes each as a temporary Personality Trait
    while they stay, no stronger than the aura.
  - Tinting takes a ceremony, where the tint fades a point a day, or a
    season's influence, a point a season.
  - The roll is stress die + Presence + Concentration against 3 times
    the Trait's value, never above the tinter's Sympathy Trait.
  - Several tints pull people several ways at once. Some auras are
    tinted for good.
- **Divine aura**, for a Divine aura: the **Dominion** or an
  **Empyreal** aura.
  - Both are one weaker at night and one stronger on Sundays and holy
    days (Realms of Power: The Divine pp. 7, 10; DE p. 418). Both hold
    sway over another realm's aura of the same strength (p. 11).
  - The Dominion comes from worship. An Empyreal aura comes from no
    congregation (pp. 12-13). It comes from a person or relic of 5 or
    more Faith Points, or from a miracle. A miracle gives 1 at level 50,
    and a point more each five levels above, while its effect lasts. A
    holy creature's home gains a point each season it dwells there, up
    to its Might / 10.
  - In play the two are the same, and the realm table applies to both
    (p. 12). Mundane folk are moved alike, the pious to love and awe,
    the sinful to guilt and fear. The Gifted feel their Gift falter (pp.
    8-9).

The place's facts say what its aura's kind does ("Aura kind"), and each
level's ("Within").

**Conciatta's guidelines for auras** (Legends of Hermes p. 17) may be
used by any magus who has studied one of her unpublished works.

- Intellego Vim detects:
  - a supernatural tether of strength 5 or more at level 1
  - one of 4 or more, and a subsumed aura, at level 2. A subsumed aura
    is one a stronger aura overpowers.
  - one of 3 or more at level 3
  - a natural or supernatural tether of 2 or more at level 4
  - any tether at level 5
- A Rego Vim Ritual suppresses an aura no stronger than its magnitude
  for its duration. It works only on the mundane level, and breaks if
  the aura grows past it.
- Dominance Over the Infernal holds an Infernal aura of (magnitude - 9)
  at bay for a year.
- Her words for auras (p. 15):
  - diffuse (no fixed source) or tethered
  - stable, waning or waxing
  - existential (Faerie and Magic) or moral (Divine and Infernal)
  - apparent (the strongest present) or subsumed

**Lies in.** A place, or a regio level, may lie in the Magic Realm or
the Faerie Realm instead of the mundane world. Set it with Lies in, on
the place's form and on each regio level's. Its aura then is the
realm's own, whatever the Aura field says:

- **The Magic Realm** (Realms of Power: Magic pp. 20-28).
  - Magic 10 throughout, plus the realm boundary the place lies in
    (Boundary, 0-10). A boundary of 4 makes the aura 14 for magic.
  - The boundary is aligned with a Form, kept in Alignment. That Form's
    effects add the boundary again, so Corpus 4 gives +18 to Corpus
    effects.
  - Powers of other realms take no bonus from it.
  - Each roll the aura helps takes as many extra botch dice as the
    boundary. Casting botch dice and the laboratory's count them.
  - Each season, (aura / 10, rounded up) pawns of the boundary's Form
    of vis appear there, and fade if not taken (p. 22).
  - No one gains experience there. A season's experience comes as pawns
    of vis of one Art instead (p. 20). No one makes Aging rolls.
  - Diameter, Sun and Moon last to the season's end, and Year as long as
    the target stays.
  - Travelling on through a boundary or vestige takes Magic Might,
    Second Sight or Magic Sensitivity. Roll stress die + Perception + an
    Ability + the Form / 5 against (10 - its level) x 3, less the best
    Familiarity. Familiarity is knows of it 1, seen it 3, visited it 6,
    an Arcane Connection 15, or Enigmatic Wisdom, Magic Lore or Area
    Lore x 3.
  - By how much it passes is the Speed Level of the journey through the
    Twilight Void (p. 23). 0 is seven years and more, 9 a season, 15 a
    day, 24 two minutes, 30 a moment. Each botch is a step (3) slower.
    Below 0, the traveller is stranded.
  - Straying from the path in the Void is a Twilight Comprehension roll
    (p. 24). It's Int + Enigmatic Wisdom + stress die against Warping
    Score (or Might / 5) + stress die.
  - The vis gathered there can transform a character without Might, one
    change a season (p. 26). 5 pawns give a Minor Virtue and Flaw, 10 a
    Minor Virtue, 15 a Major Virtue and Flaw, 30 a Major Virtue.
- **The Faerie Realm** (Realms of Power: Faerie p. 24).
  - Faerie 10 throughout. Hermetic magic gets +5, with ten botch dice
    rolled apart, whose botches are strange rather than dangerous.
  - An entrance to Faerieland from a faerie regio is a regio level of
    aura 10 (p. 16). Set its level to lie in the Faerie Realm.

**Threshold.** A place with a Faerie aura shows the Threshold's
strength. That's the Threshold points needed to cross into the Faerie
Realm from there, (13 - the aura's modifier on a Faerie power) x 3.
Faerie 3 needs 30. A Faerie regio level adds the surface's Faerie aura
to its own, but any other surface aura doesn't count (Realms of Power:
Faerie p. 21).

Points come from (pp. 21-23):

- the border crossed: 3, 6, 9 or 12, +3 if lost. A trod is at least 9.
- the time: new moon 1, full moon or a pagan holiday 3, solstice 6,
  equinox 9
- the traveller: faerie Virtues 3, or 9 if Major, faerie Flaws 3, only
  the best of these. An extreme emotion gives 3 + its Trait, a life
  change 9 to 18.
- a work of art about Faerie: its Aesthetic Quality
- a faerie's Spirit Away
- the Arcadian Travel charm

A set of circumstances is tried once. Changed, it's tried again at the
next moonrise. The Guardian of the Threshold then offers the choice, and
Int + Faerie Lore against 6 gives hints (p. 24). Once a faerie regio's
entrance is found, finding the action that opens its level is Int +
Faerie Lore against 15. It's 3 when the story narrows it to a choice
(p. 16).

**Lunar aura** (with Dies Irae in play). Lunar is a fifth supernatural
realm (Dies Irae p. 36). Where the fallen lunar sphere's matter lies, a
place, a regio level or a covenant's aura may have a Lunar aura, its
Realm set to Lunar. The realm is offered only while Dies Irae is in
play.

- By the New Realm Interaction Table (p. 37), a Lunar aura gives
  Hermetic and Faerie powers -5 x the aura and Infernal ones -aura. It
  leaves Divine powers untouched.
- Lunar powers lose the aura in Magic, Faerie and Infernal auras, and 3
  x it in a Divine one.
- Casting Scores, Lab Totals and the rest take it like any other aura,
  with a botch die a point for the foreign aura.
- A season's clearing lowers it by 1. The matter carried off makes 1 of
  Lunar aura wherever it's taken.
- Since the fall, Diameter, Sun, Moon and Year Durations fail
  everywhere, and Parma Magica and the Aegis of the Hearth with them.
  Each replacement duration is a Minor Breakthrough of 30 points (p.
  37).

**See also:** [A neighbour](help:neighbour)

### Cross the Threshold
<!-- help: cross-threshold -->

<!-- tui -->
**Cross the Threshold**, in More on the place's sheet,
<!-- /tui -->
<!-- gui -->
**Cross the Threshold**, in the place's Regio chapter,
<!-- /gui -->
counts the points a set of circumstances gathers. Choose:

- the level they start from
- who leads the crossing. Their faerie Virtues and Flaws come from their
  sheet.
- the border and the time
- the leader's emotion and life change
- a work of art, Spirit Away, an Arcadian Travel charm's total and a
  cognizant faerie's Might

The panel sets the total against the Threshold's strength. Try writes
the attempt in the place's Diary. It says whether the Threshold comes,
with the Guardian's least Might, or that these circumstances can't open
it again before the next moonrise.

## Regio Levels
<!-- help: section-nb-levels -->

The regio's levels, deepest first, over its surface. Each has a name, a
realm and an aura, how to see it and how to enter it, and notes.

- Write the roll to see or to enter it as "Per + Awareness against 9",
  a Characteristic, an Ability and the number to reach. The list then
  shows which of the player covenants' characters reach it with their
  scores alone, best first.
- Anything else is kept as a sentence ("walk the path backwards at
  dusk").
- Add puts a new level above the deepest. Edit or delete one.

**See** is the Ease Factor to see into the level from the one below.
It's the level's own roll when it names one. Otherwise it's the
Definitive Edition's, marked DE (p. 421):

- 5 + 2 x the difference in aura
- 5 + 2 x the two auras added, when the level below is of another realm

Second Sight or Magic Sensitivity sees into any level. Sense Holiness
and Unholiness sees into a Divine or Infernal one.

A regio level may have a kind:

- **A Divine regio** is terrestrial, tied to a place on earth, or
  celestial, an angels' home reached by invitation (Realms of Power:
  The Divine pp. 13-15). In a celestial level:
  - A mortal acts normally only on Stamina + Dominion Lore, or Parma if
    better, against 3 times its rating. Otherwise they take as much from
    every roll.
  - After Stamina + Parma + 3 hours, they lose a Fatigue level an hour,
    then gain Warping.
- **Every Infernal regio** suspends Divine powers (Realms of Power: The
  Infernal pp. 16-17). There's no invoking God, Intercession or Holy
  Influence. Holy Powers and Holy Magic are at minus its aura.
  - A Tartaran one makes all Fatigue long-term and burns with hell-fire.
  - An Abyssal one lowers every Characteristic by its aura, and asks a
    daily Intelligence roll against the madness Flaws.

The place's facts say what each level does ("Within").

Each level may also have its aura's own kind, such as an alignment,
tints, or Dominion or Empyreal. It's asked by the level's realm, as the
place's is.

## Vis Sources
<!-- help: section-nb-vis-sites -->

The vis sources gathered at this place. A vis source is a place where a
certain number of pawns can be taken each year (Definitive Edition p.
422). Each shows its Art, pawns, season, who holds it, and its level.
When the aura there isn't Magic's, it shows its taint too ("Faerie
vis"). Divine vis risks the Church's anger, and Infernal vis corrupts.

- A source a covenant holds is listed from its covenant's
  [Vis Sources](help:section-pos-vis_source), where it's edited. Its
  Place names this one.
- A source no covenant holds yet, one waiting to be found, is added and
  edited here. Choose a covenant in **Claimed by** and it becomes that
  covenant's source, still gathered here.

The place's **Vis** says what its sources give a year, by Art. It adds
what the places inside it give, however deep, so a region shows the vis
in all its lands. The Region [by place](help:tab-region-by-place) lists
each source under its place.

## Effects
<!-- help: section-nb-effects -->

What the place does to those in it, at every level, one level, or a
level and those above it:

- **Lab totals**: added to the Lab Totals of the laboratories there, for
  the Art named, or every Art.
- **Aging rolls** and **Living Conditions**: added to the aging rolls of
  the characters who live there, whose covenant is there.
- **Warping**: Warping Points a season for those who live there, added
  each year with the rest of their Warping.
- **The aura**: replaces the aura of the levels it covers, in the realm
  named.

Add, edit or delete one.

## Triggers
<!-- help: section-nb-triggers -->

What comes at the place, and when:

- **once**: a season and year
- **each year**: a season
- **every N years**: a season, and a year it comes
- **whenever** something happens: say what in What happens

The dated ones show their next date, and the soonest is the place's
Next. Add, edit or delete one.

A dated trigger can **move a threat** that moves along a track or an
omen count. Choose it in **Moves a threat**, and say how many steps
failing it moves the threat, 1 if left blank. Each time the trigger
comes, the season it comes in asks how it went (see
[The World Turns](help:world-turns)).

## Roll Tables
<!-- help: tab-nb-tables -->

The roll tables of a place, a threat, a faction or a lord:

- what the troupe might meet at a place, or what a night in the regio
  brings
- how a threat's stage shows itself
- what a faction or a lord is up to this season

A lord's Roll Tables come after Standing, beside the lord's Diary. No
book prints a rule for these tables. They're the storyguide's own.

Only the storyguide sees them and rolls. A player signed in to a hosted
copy doesn't see them, as with Secrets (see
[Keeping secrets from players](help:guide-hosting-secrets)). Played
solo, the one player is the storyguide and sees everything.

### Writing and rolling a table
<!-- help: section-nb-tables -->

Each table names its die, such as a simple die, a stress die, a d6 or
a d10.
Its rows go one a line, such as "1-3: Nothing stirs", "4: A hare" and
"9+: The Hall opens". For a stress die, add "botch: The mist closes".

A row may end with a note for the storyguide, written "(SG: ...)":
"3: The letters on the walls curse whoever reads them. (SG: False: they
honour Abnoba.)".

- The roll shows the note. The line written in the Diary leaves it out,
  so players reading the Diary see only what happened.
- Any row can take one, a botch row too. A row without one works as
  before.
- "(SG:" anywhere but the row's end is part of its text.

<!-- tui -->
More (`m`) > **Roll** rolls the chosen table and shows the row it lands
on. **Write** puts it in the record's Diary.
<!-- /tui -->
<!-- gui -->
**Roll** rolls the chosen table and shows the row it lands on. **Write**
puts it in the record's Diary.
<!-- /gui -->

Add, edit or delete one.

## Tomb
<!-- help: tab-nb-tomb -->

A place marked **A tomb**, on its form with Lands of the Nile in play,
gets a **Tomb** page. It's the tomb designed like a covenant, with its
curses, its talismans and wards, and its traps (Lands of the Nile pp.
32-46). The rules suit any tomb, not only Egypt's and Nubia's.

## The Tomb
<!-- help: section-nb-tomb -->

What the tomb's kind gives (Lands of the Nile p. 40):

- a major monarch's tomb: a base Magic aura of 5 and 500 Build Points
- a royal consort's or minor monarch's: 4 and 250
- a lesser royal's or high priest's: 3 and 100
- a non-royal dignitary's: 3 and 50

Decay lowers the aura. A burial ground in use for a century is a
preternatural tether of 1, up to 5 for five centuries. The place keeps
its own aura. So with the aura change option on, name the tether in the
place's Tethers, as "(preternatural 5)". A tomb has up to 10 points of
Hooks to buy Boons.

The Build Points spent are those of:

- the curses
- the talismans and wards
- the traps
- the other resources, which cost what a covenant's do (pp. 42, 44).
  Inscriptions count as a library, and guardians and ghosts as
  specialists. Vis counts too.

More than the tomb has are shown in red. **Edit Tomb** sets them.

## Curses
<!-- help: section-nb-tomb-curses -->

A curse is a condition and its excoriation (Lands of the Nile pp. 34,
40-41).

- It strikes when its condition is broken or its text is defaced.
- Once it has struck as many times as its uses a day, the text can be
  destroyed safely.
- It costs 2 Build Points for every 5 levels. One written without force
  (**Hollow**) costs nothing.
- One beyond Hermetic magic is a **Lesser** (base level 10) or
  **Greater Malediction** (base 30). It has Special Duration, until
  dispelled, and it Warps its victims.

Add, edit or delete one.

The book's Tomb of Cleopatra prints 6 Build Points for her fear curse.
But the curse is a CrMe 25 effect, which the rule prices at 10. The 6
fits a level-15 effect, so it's a misprint, and her tomb's curses come
to 42 Build Points, not 38 (Lands of the Nile pp. 41, 46). The app
prices curses by the rule.

## Talismans and Wards
<!-- help: section-nb-tomb-wards -->

A **talisman** harms or imprisons, and is overcome without magic
against 6 + its magnitude. A **ward** repels or hides, against 9 + its
magnitude (Lands of the Nile pp. 35, 42).

- Anyone whose Magic Resistance is at least its Penetration passes
  untouched.
- Each costs 2 Build Points for every 5 levels.
- A talisman is usually made inert until sunset by a particular spell
  effect, and a ward by a deed at a place and time.
- A third kind, **No obstacle**, neither harms nor repels, and has no
  Ease Factor, such as the Face of Lost Companions (p. 42).
- **Ease Factor, if another** keeps one the book prints apart from the
  rule.
- **Overcome It** works on a talisman or ward as on a trap.

Add, edit or delete one.

## Traps
<!-- help: section-nb-tomb-traps -->

A trap costs Build Points for its harm, plus more for its Ease Factor
to avoid (Lands of the Nile p. 44):

- **Harm**: 3 to delay or scare, 6 for a minor injury or imprisonment,
  9 for a serious injury, 12 if often fatal.
- **Ease Factor to avoid** of 3, 6, 9, 12 or 15: 0, 1, 3, 6 or 9 more.
- A trap treated as several pays for each harm once. Put what the
  others cost under **Further harms' Build Points**, as the book's
  covered pit does with a serious and a minor injury (p. 46).
- **The roll to avoid it** and **Ease Factor to spot it** keep what the
  book gives, where it gives them.
- Most mechanical traps are reset by hand, and some work only once.

<!-- tui -->
More (`m`) > **Overcome It** walks the party through the chosen trap when
it springs.
<!-- /tui -->
<!-- gui -->
**Overcome It** walks the party through the chosen trap when it springs.
<!-- /gui -->

Add, edit or delete one. A puzzle is a trap and lock in one. Keep it in
the trap's words, for the troupe to play (p. 33).

### Egyptian craftwork
<!-- help: tomb-craftwork -->

Egyptian curses, talismans, wards and amulets are designed as Hermetic
enchanted items. A troupe with Hedge Magic may use Learned Magic
instead, whose protection, assistance and harm match the Egyptians'
amulets, talismans and curses (Lands of the Nile p. 55). The Egyptians
had very high casting and laboratory totals, no Difficult Arts and no
limits on Range, Duration and Target.

An amulet's colour is flavour (pp. 55-56):

- black for magic
- green to draw faeries
- blue for the gods
- yellow, orange and some reds for fire
- red for curses, and for Apep and Seth

## Overcome It
<!-- help: overcome-trap -->

A tomb is fixed once built, so only the rolls vary. Overcome It takes
one step at a time (Lands of the Nile pp. 32-33, 44), and cancelling
any step writes nothing. It works on a trap, and on a talisman or ward,
which the same rules resolve (pp. 35, 42).

1. **Who is there.** Choose who is in danger and tick who is with them.
2. **Look for it.** Ticking **They look for it first** rolls Per +
   Awareness for each of them against the Ease Factor to spot it. It's
   3 less in perfect light, 3 more by a single flame, 6 more in near
   darkness.
3. **If someone sees it.** They have combat rounds to deal with it, and
   magi time for formulaic or ritual magic. Say whether they deal with
   it, leave it be, or it springs all the same.
4. **Each character acts.** The one in danger goes first, the rest by
   Quickness, each seeing how those before did. Each says one thing
   they do. The troupe agrees **His roll**, a Characteristic + Ability,
   `- Encumbrance` if it counts, or blank if the action needs none. The
   storyguide moves the Ease Factor by 3, 6 or more for that action.
5. **A magus casts.** A magus answers with **a Fast-Cast spell**, judged
   on its own. Cast it from their sheet, and tick **The spell worked**
   if it did, which clears them of the trap. Magic Resistance passes a
   talisman or ward as [its rule](help:section-nb-tomb-wards) says.
6. **Settle a clash.** If two actions clash, the troupe settles it by an
   Action Priority Roll: Qik + an Ability, or Finesse for a
   fast-caster.
7. **It acts last.** Tick anyone another character helped, or who was
   out of its reach. The rest suffer it. The app says what the record
   says of the harm, and the storyguide rolls any damage.
8. **Write it.** Say what came of it, and whether the trap stays sprung
   or is reset. **Write** puts it all in the place's diary.

A trap left sprung can't spring again. Overcome It offers to reset it
first, unless it works only once. With Lords of Men's Evasion, a trap's
Attack is a stress die + its setter's Int + Profession, + a like
weapon's Attack (p. 44).

## Diary
<!-- help: tab-nb-place-diary -->

What has happened at the place.

### The entries
<!-- help: section-nb-place-diary -->

What has happened at the place, or what the faction has done, a line
each, with the season it happened. For a place, that's the rolls on its
tables and the aura rising. For either, it's anything the storyguide
writes. Add, edit or delete an entry.
