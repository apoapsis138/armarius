# Laboratory sheet
<!-- help: laboratory -->

A laboratory sheet keeps one laboratory: what it is like, what it holds and
what has happened in it. A laboratory belongs to a covenant and has an owner,
a magus whose lab work is planned on this sheet and whose Lab Totals it
shows.

<!-- tui -->
The top panel, with the laboratory's identity and Characteristics, is always
on show above the tabs. Below it are six numbered tabs, opened with `1` to
`6`. On most tabs a details panel at the bottom shows more about the chosen
row, including the rules text of a Virtue, Flaw or Feature.

With focus on the top panel, More (`m`) offers Export and Update from a
File, and switches the laboratory between In Creation and In Play (In
Creation / In Play). While it is In Creation, More also opens the Creation
Worksheet. `d` on the top panel deletes the laboratory, after asking.
<!-- /tui -->
<!-- gui -->
The header names the laboratory and whose sanctum it is, with the room its
Virtues leave and its aura as a seal; **Edit** beside it changes the
[Identity](help:section-lab-identity). The eight
[Characteristics](help:section-lab-characteristics) sit under the header.
The rail on the left holds the chapters: **Lab Totals**, **Virtues &
Flaws**, **Specializations** (with the Features and rooms of the
[Attributes tab](help:tab-lab-attributes)), **Stores** (what the
[Inventory tab](help:tab-lab-inventory) lists), **Seasons** (the
[Planning](help:tab-lab-planning) list and the [Diary](help:tab-lab-diary))
and **Manage**. Clicking a card or row shows more about it in the inspector
on the right, including the rules text of a Virtue, Flaw or Feature.

The button in the header showing **In Creation** or **In Play** switches
the laboratory between them, after asking. While it is In Creation,
**Worksheet** beside it opens the Creation Worksheet. The **Manage**
chapter offers Export, Update from a File and Delete, which asks first.
<!-- /gui -->

The Creation Worksheet walks through setting the laboratory up: its owner,
Size and Refinement, its Virtues, and whether it is one of its covenant's
starting laboratories, paid for from the covenant's Build Points.

<!-- gui -->
The owner's name is a button in the header that opens
their sheet below the laboratory, so the trail leads back to it.
<!-- /gui -->

**See also:** [How lab planning works](help:guide-lab-planning), [How to create a character, covenant or laboratory](help:guide-creation)

### Identity
<!-- help: section-lab-identity -->

<!-- tui -->
The panel is titled with the laboratory's name. **You type** (with `e`) its
name, location, aura modifier, whether its sanctum is marked, its covenant
and its owner, chosen from the saga's magi. **The app works out** the aura,
the covenant's aura (with any Boons that raise it) plus the modifier, shown
with the covenant's realm, and the Build Points: Size x 20, plus 10 for each
Minor Virtue and 20 for each Major one (Ars Magica Definitive Edition,
Chapter 8: Laboratory).
<!-- /tui -->
<!-- gui -->
The laboratory's header. **You type** (with **Edit** beside it) its name,
location, aura modifier, whether its sanctum is marked, its covenant and its
owner, chosen from the saga's magi. **The app works out** the aura, the
covenant's aura (with any Boons that raise it) plus the modifier, shown as
a seal in the covenant's realm's colour, and, beside it, the Occupied Size,
Free Virtues and Base Safety from the
[Characteristics](help:section-lab-characteristics).
<!-- /gui -->

### Characteristics
<!-- help: section-lab-characteristics -->

The eight Characteristics (Size, Refinement, General Quality, Upkeep, Safety,
Warping, Health and Aesthetics) each show three figures: the value you type,
what the laboratory's Virtues and Flaws add, and the total.
<!-- tui -->
`e` edits only the typed values.
<!-- /tui -->
<!-- gui -->
They are drawn as a compass rose beside a card for each; **Edit** changes
only the typed values, and clicking a card shows where its total comes from,
naming each Virtue and Flaw's part (a Servant's with whose Intelligence it is).
<!-- /gui -->
The app also works out Occupied Size (Virtue points less
Flaw points less Refinement), Free Virtues (Size plus Refinement less the
Virtue points net of Flaws) and Base Safety (Refinement less any positive
Occupied Size), following Ars Magica Fifth Edition: Covenants, Chapter 9.
The laboratory's rolls use its Base Safety plus the Safety total, and its
Warping total: see [Safety and Warping](help:guide-lab-safety-warping).

Aesthetics is halved, after everything else, when the laboratory is
Invisible or Shrouded, and is at most -1 when it is Lightless (DE p. 296;
Covenants pp. 118-119). Each point of Aesthetics, good or bad, is worth 5 xp
in a fitting Reputation for its owner, perhaps over time (DE p. 290): add it
to the owner's Reputations as it comes.

A covenant that closes the year broke can't pay its laboratories' Upkeep:
the season record names each of them, and the troupe gives each a Flaw, or
takes a Virtue away, that lowers its Upkeep (DE p. 288).

## Planning tab
<!-- help: tab-lab-planning -->

Where the owner's lab work is planned, season by season. The list shows the
owner's seasons from the current one on: each planned activity with the
seasons it spans and how far it will have got, any free seasons in between,
and the first free season after the last plan. A season planned on the
owner's own sheet (study, say) shows here too, marked as such.

<!-- tui -->
**You type:** nothing here directly. `e` plans lab work for the chosen
season on the [Invent Spell screen](help:invent-spell), or reopens the plan
already there; `a` starts inventing a new spell from a blank design in the
chosen season; `d` clears the chosen season's plan, with any later seasons
scheduled to continue it, after asking.

**The app works out:** whether each plan can be done (a row that can't says
so in red, and the details panel says why), the Lab Total of each plan line
by line in the details panel, and the progress of work that takes several
seasons. A season ahead is worked out from the magus and laboratory as the
seasons planned before it will leave them: an Art raised by an earlier
season's study raises a later Lab Total, and an invention's points carry
on. The laboratory needs a magus as its owner before anything can be
planned.
<!-- /tui -->
<!-- gui -->
On the desktop this list is **Planning**, at the top of the laboratory's
**Seasons** chapter, above the calendar of its seasons and the Diary.

**You type:** nothing here directly. **Plan** plans lab work for the season
last clicked on the [lab work form](help:invent-spell), or reopens the plan
already there; **New Spell** starts inventing a spell in that season (or the
current one), first asking for a spell to start from (any spell, the
magus's own known spells first) or a blank design;
**Clear** clears the season's plan, with any later seasons scheduled to
continue it, after asking. Beside them, **Bind Familiar** is there while the
owner has no familiar, and **Perform Ritual** while the laboratory has a
Longevity Ritual's Lab Text (see [Lab Texts](help:section-lab-texts)).

**The app works out:** whether each plan can be done (a row that can't says
so in red, and the inspector says why when it is clicked), the Lab Total of
each plan line by line in the inspector, and the progress of work that
takes several seasons. A season ahead is worked out from the magus and
laboratory as the seasons planned before it will leave them: an Art raised
by an earlier season's study raises a later Lab Total, and an invention's
points carry on. The laboratory needs a magus as its owner before anything
can be planned.
<!-- /gui -->

**See also:** [Invent Spell screen](help:invent-spell),
[Lab Totals tab](help:tab-lab-totals),
[Advancing a season](help:advance-season), [How to plan and run a season](help:guide-seasons), [How lab planning works](help:guide-lab-planning)

## Research tab
<!-- help: tab-lab-research -->

The research the laboratory's owner has under way, while they have any:
their goals begun and not yet reached, and the seasons spent on them
(Ars Magica Definitive Edition, Chapter 8, Experimentation and Arcane
Discovery). It is the same research as on the magus's own
[Research tab](help:tab-research), shown here to plan the laboratory's
seasons by; the goals are added and changed on the magus's sheet.
<!-- tui -->
Choosing a goal shows where it stands and the odds of its next season;
choosing a season of the log shows its roll on the Extraordinary Results
chart.
<!-- /tui -->
<!-- gui -->
Clicking a goal shows it in the inspector with the odds of its next
season; choosing a season of the log draws its roll on the chart below
the log.
<!-- /gui -->

### Research under way
<!-- help: section-lab-research-goals -->

The owner's goals begun and not yet reached, each with its points and
what waits on it: a Discovery to stabilize, or insights to invent.

### Research Log
<!-- help: section-lab-research-log -->

Every season spent on those goals, newest first: the season, the goal,
the work, the stress die, the roll (the die plus the risk), any move of
it, and what came of it.

## Lab Totals tab
<!-- help: tab-lab-totals -->

What the owner's Lab Totals are when working in this laboratory, and what
goes into them.

**You type:** nothing. The figures come from the owner's sheet and from this
laboratory's aura, Characteristics, Specializations and Virtues and Flaws.

**The app works out:** the Lab Total for every Technique and Form, the Base
Lab Total every one of them shares, and what each kind of lab activity adds
(Ars Magica Definitive Edition, Chapter 8: Laboratory). With no owner, or an
owner who isn't a magus, the tab says so instead.

**See also:** [Planning tab](help:tab-lab-planning),
[Attributes tab](help:tab-lab-attributes),
[Invent Spell screen](help:invent-spell), [How lab planning works](help:guide-lab-planning)

### Lab Totals
<!-- help: section-lab-totals-grid -->

A grid of the owner's Lab Total for each Technique (rows) and Form
(columns) in this laboratory: the Technique plus the Form plus the Base Lab
Total below, with any Art Specialization of the laboratory included where
it applies. Nothing here is typed.
<!-- gui -->
Each square is shaded by its total; clicking one shows that Lab Total line
by line in the inspector.
<!-- /gui -->

### Base Lab Total
<!-- help: section-lab-totals-base -->

The terms every Lab Total shares: the owner's Intelligence and Magic Theory,
the aura's modifier for Hermetic magic in the laboratory's realm, General
Quality and any Virtue or Flaw that adds to every total. Below them are the
Art Specializations (each added only to totals using that Art), the Activity
Specializations (each added only to its own activity) and any multiplier
from a Virtue, which is already in the grid.

### By Activity
<!-- help: section-lab-totals-activity -->

What each kind of lab work adds on top of the grid: inventing spells,
enchanting items, working from a Lab Text, binding a familiar, Longevity
Rituals, extracting vis and experimenting. Below that are the results the
app works out from them: the Longevity Ritual's modifier to aging rolls, the
pawns of vis extracted in a season (a pawn for every 10 points, rounded
up; vis is extracted only in a Magic aura, DE p. 250), and the most raw
vis a season and the largest shape and material bonus the owner's Magic
Theory allows.

## Virtues & Flaws tab
<!-- help: tab-lab-vf -->

The laboratory's own Virtues and Flaws, from Ars Magica Fifth Edition:
Covenants, Chapter 9, side by side.

**You type:** which Virtues and Flaws the laboratory has, chosen from the
catalog.

**The app works out:** the points each side comes to and what they add to
the Characteristics, Specializations and Lab Totals.

A warning line above the lists says when the laboratory has more Virtues
(net of Flaws) than Size plus Refinement allow, more than one Focus, a
Virtue whose Specialization hasn't been chosen, a Servant, Greater Guardian
or Greater Horde with no Intelligence entered, or a Servant whose grog is no
longer in the saga.

The Burning City's laboratory customizations (Hermetic Projects pp. 26-27): the Features Fumes (Pe, Au, Ig), Pool of Lava (Ig, Te), Thermal Spring (Cr, Aq, Ig) and Volcanic Rock (Mu, Ig, Te), each as a Greater or Lesser Feature; Dormant Volcano, Active Volcano, Mineral Bath, Volcanic Spirit Forge and Hell Portal; and the Volcano Shape and Material bonus (+5 volcanoes). Experimenting on such work may bring the book's volcanic side effects (pp. 27-28): lava tears, a sulphurous stench, footprints that scorch, toxic fumes, humors thrown out of balance (an Aging modifier of -1 or +1 for good), a crust of skin (+3 Soak for Sun), a warm glow that keeps off hunger and thirst; the troupe picks or invents them.

**See also:** [Characteristics](help:section-lab-characteristics),
[Features](help:section-lab-features),
[Lab Totals tab](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Virtues
<!-- help: section-lab-vf-virtues -->

The laboratory's Virtues, with the points they come to in the title. Adding
one picks it from the catalog, which shows each entry's rules, effects and
book as you go through it; a Virtue that grants a Specialization of the
owner's choice asks for it then.
<!-- tui -->
`e` changes the chosen Virtue's Specialization, or a Servant's grog or
Intelligence,
<!-- /tui -->
<!-- gui -->
**Edit** changes the chosen Virtue's Specialization, or a Servant's grog
or Intelligence,
<!-- /gui -->
keeping the Virtue and any Feature built on it. To take a different
Virtue, delete this one and add the other.

A few Virtues add Safety worked out from an Intelligence (Ars Magica
Definitive Edition, Chapter 8):

- **Servant** asks for the servant: one of the saga's grogs (those of the
  laboratory's covenant first), or, with none chosen, the servant's
  Intelligence typed in. It adds half that Intelligence, rounded up, to
  Safety. A chosen grog's Intelligence is read from their sheet each time,
  so it follows aging or any change to it.
- **Greater Guardian** and **Greater Horde** ask for the creature's
  Intelligence and add all of it to Safety.

**Natural Environment**, **Greater Guardian**, **Greater Horde** and the
Flaw **Sacrifices** put their Specialization points (3, 3, 2 and 2) in the
Art chosen; to split them among several, type the others under
Specializations: Other.

The Virtue's details, and its card, say whose Intelligence it is and what it
comes to: "Safety +2 (Kurt's Intelligence +3, halved, rounded up)". A Feature Virtue is usually added along with its Feature on the
Attributes tab.

A Virtue a magic item grants reads "(Minor, from Wand)": it takes no space
and costs no Build Points. The Magic Item and Enchantment Virtues name
their item, and are added for you under
[Magic Items](help:section-lab-magic-items). Deleting a Virtue an item
grants, or the item's own Virtue, says what the laboratory loses with it.

### Flaws
<!-- help: section-lab-vf-flaws -->

The laboratory's Flaws, with the points they come to in the title. They work
like the Virtues: picked from the catalog, deleted rather than edited. A
laboratory may have only one Focus Flaw.

**Empty** asks whether it costs +1 Upkeep or -1 Health, and **Cramped** for
the one activity it doesn't hamper, which takes a Specialization point.
**Lesser** and **Greater Illusion** ask which of the laboratory's Virtues is
only an illusion: that Virtue then has no effect at all (DE p. 296). A
Hidden Defect may be had more than once.

A few Flaws ask what they apply to when added: **Missing Ingredients** an
Art (and a second Form), whose Lab Totals it halves; **Missing Equipment**
one or two kinds of activity the laboratory can't be used for;
**Elementary** the one kind it can be used for; **Restriction** the
activity it forbids (DE pp. 295-296). Lab work they rule out is refused
when it is planned.

### Personality Traits
<!-- help: section-lab-personality-traits -->

A laboratory with a Warping score has Personality Traits whose scores add
up to it, such as Whimsical +1 from faerie ingredients: they colour the
experience of its owner and anyone living there, suggest the Warping its
work and its inhabitants suffer, and the storyguide may add one to a Lab
Total for an effect that matches it, or take it off for an opposite one
(DE p. 289).
<!-- tui -->
`a` adds one, `e` edits the chosen one and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the trait last clicked.
<!-- /gui -->
The warning line above the lists says when they don't add up to the
laboratory's Warping.

## Attributes tab
<!-- help: tab-lab-attributes -->

The laboratory's Specializations, its Features, its magic items and its
rooms, then its
[Connections](help:section-connections): its covenant and where it is.
<!-- gui -->
On the desktop they are in the laboratory's **Specializations** chapter.
<!-- /gui -->

**You type:** the Features and what their points go to, what each magic
item's effects give the laboratory, any Specialization points from a source
the app doesn't work out itself, and the rooms.

**The app works out:** each Specialization's score from all its sources
(magic items included), whether each magic item's points fit its effect's
level, and
how many count against the limits on Activity and Art Specializations
(Ars Magica Fifth Edition: Covenants, Chapter 9).

**See also:** [Virtues & Flaws tab](help:tab-lab-vf),
[Lab Totals tab](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Specializations
<!-- help: section-lab-specializations -->

<!-- tui -->
A grid of every Specialization the laboratory has points in, grouped into
Activity and Art, each group's title saying how many count against its cap
(two Activities, four Arts, no more than two of them Techniques).
<!-- /tui -->
<!-- gui -->
Every Specialization the laboratory has points in, as bars in two sections,
Activity Specializations and Art Specializations (two Activities and four
Arts count, no more than two of them Techniques). Clicking one shows where
its points come from.
<!-- /gui -->
The scores are worked out from the Features, their Focus, the Virtues and
Flaws and the sources typed below.
<!-- tui -->
`Space` turns the chosen Specialization off or back on;
<!-- /tui -->
<!-- gui -->
**Turn Off/On** turns the one last clicked off or back on;
<!-- /gui -->
the app refuses to turn one on that would break a cap, and a newly gained
one that would break a cap arrives turned off.

Besides Lab Totals, two Activity Specializations count outside them when
the season is spent in the owner's laboratory (DE p. 291): **Teaching** adds
its points, at most +3, to the Source Quality of teaching and training, and
of teaching a Hermetic Virtue; **Texts** adds a point for every full 3 to
Profession: Scribe when copying books and Lab Texts, and to the language
when writing summae or rewriting Lab Texts. A season of teaching, training,
writing or copying has **In the laboratory** ticked unless you untick it
(taught away from the lab, or written abroad): then neither counts.
Teaching a spell is a Lab Total, so the Spells Specialization helps it
instead, and Texts adds to the Lab Total of working from or decoding a Lab
Text.

### Specializations: Other
<!-- help: section-lab-specialties -->

<!-- tui -->
Specialization points from sources the app doesn't work out itself, nested
inside Specializations.
<!-- /tui -->
<!-- gui -->
Specialization points from sources the app doesn't work out itself, in the
**Specialization sources** section under the Specializations.
<!-- /gui -->
You type which Specialization, how many points
(negative for a penalty) and where they come from; the Specializations
add them in.

### Features
<!-- help: section-lab-features -->

The laboratory's Features, each built on one of its Lesser or Greater
Feature Virtues; the title counts the Features against those Virtues. Adding
one takes two steps: the kind of Feature (from the catalog, or Custom) and
the Virtue it is built on, offering to add a new Feature Virtue if there is
no free one; then its name, where its points go and whether it is the
laboratory's Focus. Deleting a Feature keeps its Feature Virtue, free for
another.

### Magic Items
<!-- help: section-lab-magic-items -->

What the enchanted devices kept in the laboratory give it (Ars Magica
Definitive Edition, Chapter 8: Laboratory, and Covenants, Chapter 9: Magic
Items for Laboratories), one row for each effect, its title counting them.
An item is installed as a Free **Magic Item** Virtue (Minor when it is very
large) or as an **Enchantment** of the laboratory itself; the app adds that
Virtue for you. Each of its effects then gives the laboratory one of two
things:

- **A Virtue or Flaw it duplicates.** The laboratory gains it at once, with
  no space cost and no Build Points at creation, and its modifications
  apply as usual. The Virtues & Flaws tab shows it as "from" the item.
- **Points bought by its level:** one Specialization point for every 10
  levels of the effect, one Characteristic point for every 20. The app
  refuses to save more points than the level buys.

Adding one takes two steps: the effect (from the devices kept here), how
the item is installed and which kind of benefit it gives; then the Virtue
it grants, or the points and where they go. With no enchanted device kept
in the laboratory there is nothing to choose: add one under Enchanted
Devices on the Inventory tab first. Deleting a row removes what that effect
gives, and the Magic Item Virtue once nothing else uses it; the device
itself stays. Deleting the device, or its effect, removes what it gave.

An item gives the laboratory nothing while its device is kept elsewhere:
its points and the Virtue it grants stop counting, and its row says so,
until the device is back.

An effect must be new to the laboratory: the row warns when it grants a
Virtue the laboratory has already, or when its points need a higher level
than the effect has.

An item made into a Feature is not entered here: add it under Features, and
its Feature Virtue is paid for as usual.

**See also:** [Enchanted Devices](help:section-lab-devices),
[How to install a magic item in a laboratory](help:guide-lab-magic-item)

### Rooms
<!-- help: section-lab-rooms -->

The laboratory's rooms, each a name and a description you type. The app
works nothing out from them.

## Inventory tab
<!-- help: tab-lab-inventory -->

What the laboratory holds: raw vis, equipment, Arcane Connections, enchanted
devices, Lab Texts and other books.
<!-- gui -->
On the desktop this is the laboratory's **Stores** chapter.
<!-- /gui -->

**You type:** each entry, in its own section.

**The app works out:** the state of each Arcane Connection, each device's
figures, and how each Lab Text stands for the owner. Lab work changes these
lists when a season is advanced: vis paid or extracted, a connection fixed,
a Lab Text written.

**See also:** [Planning tab](help:tab-lab-planning),
[Diary tab](help:tab-lab-diary)

### Raw Vis
<!-- help: section-lab-raw-vis -->

The pawns of raw vis kept in the laboratory, one row per Art. You type the
Art and the pawns. Lab work that pays with the laboratory's vis takes it from
here when the season is advanced, and extracted vis can be sent here.
<!-- tui -->
[Give](help:give) in More (`m`) gives the chosen Art's pawns
<!-- /tui -->
<!-- gui -->
The **Give** button here gives the chosen Art's pawns
<!-- /gui -->
to another laboratory, covenant or magus, and both Diaries record it.

### Equipment & Stores
<!-- help: section-lab-items -->

The laboratory's equipment and stores, each a name and a description you
type. The app works nothing out from them.

### Arcane Connections
<!-- help: section-lab-connections -->

The Arcane Connections kept here. You type what each connects to, whether it
is fixed, and if not its last active season and year (and any notes on how
long it lasts), where it came from and a description. Fixing one is a
season of lab work planned on the Planning tab; it must still be active as
the season starts (DE p. 250), so the app refuses one whose last season has
passed. When that season is advanced, the connection is marked fixed.

### Enchanted Devices
<!-- help: section-lab-devices -->

The enchanted devices kept in the laboratory, each followed by its effects.
The app works out each device's figures, such as capacity, effect levels and
charges, from what you type (Ars Magica Definitive Edition, Chapter 8:
Laboratory).
<!-- tui -->
`e` and `d` act on the chosen device or effect. More (`m`) offers Instill
an Effect on a device that can take another effect, Use a Charge on a
Charged Item, and Use an Effect on a finished effect of an invested device
or lesser enchantment.
<!-- /tui -->
<!-- gui -->
**Edit** and **Delete** act on the row last clicked, a device or one of its
effects. **Instill** adds an effect to a device that can take another,
**Use Charge** uses up a charge of a Charged Item, and **Use** uses a
finished effect of an invested device or lesser enchantment once.
<!-- /gui -->
An invested device's **Arithmetic magic** field marks a Numerologist's Book
or a Hermetic Architecture component (The Mysteries Revised Edition pp.
91-98). A lesser book (its parchment opened with 8 pawns, Magic Theory 4)
gives its maker a book bonus of +4, a greater one (the whole book, 16
pawns, Magic Theory 8) +8, never more than his Artes Liberales, and only
when he has Hermetic Numerology and holds it. The bonus adds to his Rote
Lab Totals and, for a magus with Hermetic Architecture, to the Lab Totals
for instilling effects in a component, shown as its own line.
A talisman's details say what its magus's Talisman Mysteries allow
(The Mysteries Revised Edition pp. 89-90): with **Great Talisman**, an
attunement each season merely by using it, without working on it (still
one a season), and new components crafted in whenever he reopens it, no
Craft roll, up to his Magic Theory in all; with **Consummate Talisman**,
its Personal Muto Vim effects work on his Formulaic spells (listed as
"On his Formulaic spells") and its Names of Power on any spell he casts,
spoken aloud, their bonus at most Magic Theory. Inscription on the Soul
alone attunes no bonus without work on the talisman (the errata to TMRE
p. 70).

Using an effect shows what it does at the table (DE p. 259): it goes off
at Initiative Quickness (the holder's, when a character holds it) + a
stress die, +3 with a Fast Trigger (p. 257); its Penetration is 0 unless
levels were added for it; no Fatigue is rolled. Each use counts against its
uses per day, shown as "Today" in its details. When they are all spent, it
asks whether a new day has begun: yes gives every device's effects their
uses again and counts this as the first. Advancing the season gives them
all their uses again too. A Charged Item's effect is used a
charge at a time instead.

**Weak Magic** gives only half the benefit of Penetration put into an
item: an effect its enchanter instils buys Penetration a level a point,
not two (DE p. 152). **Infernal vis** doubles botch dice in casting and
needs a roll on the experimental results for an enchanted item (DE p.
422); the app doesn't mark vis by its realm, so add these at the table.

Not tracked, so noted here: moving raw vis into another object (Vis
Transfer, DE p. 250) takes a day in a laboratory, alongside other work, up
to the object's Material and Size capacity, and doesn't change the vis's
Art; an item opened for enchantment can't also hold raw vis. The app keeps
raw vis as pawns of each Art, not what holds them, so a transfer changes
nothing on the Raw Vis list. An item larger than huge (DE p.
255) has a size multiplier one higher for each tenfold step past huge (a
castle keep, a hundred times a small room, is x7) and must be inside the
laboratory to be opened: type its capacity in **Capacity**.
A device whose Verditius maker crafted it in its first season has
**Verditius Runes** ticked, and **Crafted with** names the Craft Ability
used (blank when he shaped it by magic).
With **Verditius Runes** ticked, an invested device shows three more fields for
the House's Inner Mysteries (Houses of Hermes: Mystery Cults pp. 127-135).
**Elder rune (Technique)** and **Elder rune (Form)** are the elder runes
inscribed when it was opened, at most one of each, and only for the twelve Arts
that have runes (none for Muto, Imaginem or Terram). Opening it then takes a
pawn of each rune's Art besides its Vim, and the magus must know Verditius
Elder Runes; each rune adds 5 to the level of every effect instilled in it, and
its pawn counts toward what the device holds (p. 127). **Verditius item** marks
an attuned item (Item Attunement: it holds its maker's highest Technique +
highest Form + Philosophiae + the Craft he made it with, whatever its material
and size, p. 135) or an automaton (Automata: type its Magic Might, 10 + Size +
the material's base points, as its **Capacity**; it can't be a talisman, and
its powers can't maintain concentration, pp. 129-130). Making either needs its
Mystery.
A device crafted by a Verditius shows the **House price** (Houses of Hermes: Mystery Cults
pp. 114-115): to another magus, twice the vis it took (its opening, less its maker's
Craft, and every effect's, elder runes included) besides that vis; to a mundane buyer
15 Mythic Pounds for each pawn of that vis, the Primus's fixed price (an automaton's
construction is charged on top). A charged item takes no vis: its price to a magus is
twice the vis its maker could have extracted in the seasons it took, which he works out
from his Vim extraction Lab Total, and to a mundane buyer 15 Mythic Pounds a pawn of
that vis. The line also
gives the Hubris experience selling it brings. Prices only bind the House; other magi
charge what they like. A forge-companion (an unGifted craftsman with the Virtue) adds +1
per 5 points of the Craft his master is using to the master's Lab Total, and a Verditius
may have as many as his Leadership (pp. 113-114): add it to the Lab Total by hand for now.
A Charged Item warns when more
charges are recorded than its Lab Total gives: by the excess, or a fifth of
the whole Lab Total when it was made from a Lab Text.
What a device's effects give the laboratory itself, a Virtue or
Specialization and Characteristic points, is set under
[Magic Items](help:section-lab-magic-items) on the Attributes tab.

**Mercere's Portals** (Houses of Hermes: True Lineages pp. 100-101): an
effect named Mercere's Portal is instilled only by a magus who has learned
the method, by a season studying a Portal or its Lab Texts: record it as a
reached research goal named Mercere's Portal on his Research. Each of the
two archways is an invested device instilling Rego Terram 65 (Base 35, +4
Arcane Connection, +10 unlimited uses), each holding an Arcane Connection
to the other; the season's notes add that a connecting ceremony, like
Hermes' Portal and with no roll, is held at both at once, that the Portals
work only once joined, and that moving one then destroys it. An effect
whose level working names Boosted, Harnessed or Tethered is invested only
by a magus with Mutantum Magic (p. 101).

### Lab Texts
<!-- help: section-lab-texts -->

The laboratory's Lab Texts, as a table with each text's kind, Arts, level,
author and whether the owner can use it. A Lab Text is added like a book;
inventing a spell, instilling an effect and a Longevity Ritual each write one
here when the season is advanced.
<!-- tui -->
`/` filters the table by kind, Technique, Form, level, and to texts the
owner can read. Perform Ritual in More (`m`) performs a Longevity Ritual
again from its text at once: it takes vis but no season. As for casting a
ritual spell, the vis of each Art is at most the magus's score in that
Art, which may make it impossible (DE p. 261; The Mysteries Revised
Edition p. 42).
<!-- /tui -->
<!-- gui -->
The bar above the table narrows it by kind, Technique, Form and level, and
**Readable only** to texts the owner can read. **Texts Read**, beside Add,
Edit and Delete, sets whose texts the owner reads. **Perform Ritual**, a
button on the [Planning](help:tab-lab-planning) list in the Seasons chapter,
performs a Longevity Ritual again from its text at once: it takes vis but
no season. As for casting a ritual spell, the vis of each Art is at most
the magus's score in that Art, which may make it impossible (DE p. 261;
The Mysteries Revised Edition p. 42).
<!-- /gui -->

### Books
<!-- help: section-lab-books -->

<!-- tui -->
The laboratory's other books (everything kept here that isn't a Lab Text),
the same as in any other book list. `Space` marks several books; with books
marked, `e` gives them all a new owner and `d` deletes them all, after
asking.
<!-- /tui -->
<!-- gui -->
The laboratory's other books (everything kept here that isn't a Lab Text),
as cards at the foot of the Stores chapter; clicking one shows it in the
inspector. On the desktop they can't be added, edited or deleted here yet:
use the terminal version.
<!-- /gui -->

## Diary tab
<!-- help: tab-lab-diary -->

A record of what has happened in the laboratory, by season.
<!-- gui -->
On the desktop the Diary is at the foot of the laboratory's **Seasons**
chapter, newest first, with Add, Edit and Delete.
<!-- /gui -->

**You type:** entries of your own: year, season, activity type, a name and
details.

**The app works out:** nothing, but it adds entries itself when lab work is
applied as a season is advanced, when vis is moved in or out, and when a
Longevity Ritual is performed again from its text.

**See also:** [Planning tab](help:tab-lab-planning),
[Advancing a season](help:advance-season)

# Invent Spell screen
<!-- help: invent-spell -->

The screen where a season of the laboratory owner's lab work is planned,
opened from the [Planning tab](help:tab-lab-planning). Despite its name it
plans every kind of lab work: inventing a spell from a design, inventing one
from a Lab Text, learning spells from a teacher, extracting vis, fixing an Arcane Connection, a Longevity
Ritual, the enchantment activities (opening an item, instilling an effect, a
lesser enchantment, a charged item, attuning a talisman, investigating an
enchanted item), decoding another magus's Lab Texts, taming a magical beast,
stabilizing a Discovery, setting up, refining, taking over or moving the
laboratory, and binding or empowering a familiar.

A season ahead is checked against the magus and laboratory as the seasons
planned before it leave them, so an item can be opened in Spring and an
effect instilled in it in Summer, planned together. **Similar spell known**
adds the magnitude of the highest similar spell the magus knows when
inventing, instilling an effect (lesser and charged enchantments too) and
empowering a familiar's bond (DE pp. 258, 260, 267). Choosing the effect
to instil fills in **Shape & material** with the device's Shape & Material
bonuses whose "applies to" shares a word with the effect's name,
description, Technique or Form, up to the magus's Magic Theory (DE p.
258); change it when the troupe reads the bonuses otherwise.

<!-- gui -->
On the desktop it is a form that opens in place of the Planning list, from
its **Plan** or **New Spell**.
<!-- /gui -->
Its title names the work, the magus, the laboratory and the season. As you
type, it shows the Lab Total and when the work will be done, worked out under
Ars Magica Definitive Edition, Chapter 8: Laboratory.

**See also:** [Planning tab](help:tab-lab-planning),
[Lab Totals tab](help:tab-lab-totals),
[Advancing a season](help:advance-season), [How lab planning works](help:guide-lab-planning)

### Lab work
<!-- help: invent-spell-activity -->

The first field chooses the lab work.
<!-- tui -->
Press Enter on **Lab work** to open the list of lab work, grouped by Type:
Inventing, Enchanting, Familiar, Texts and vis, and The laboratory. Type to
search, choose a **Type** or **Book** above the list to narrow it (F2 steps
through the Types), and press Enter on the work wanted.
<!-- /tui -->
<!-- gui -->
Click **Lab work** to open the list of lab work, grouped by Type:
Inventing, Enchanting, Familiar, Texts and vis, and The laboratory. Type to
search, or choose a **Type** or **Book** above the list to narrow it, then
choose the work wanted.
<!-- /gui -->
The magus's most recent seasons are listed first, under Recent, until the
list is narrowed. Then only the fields that work needs
are shown: a spell design for inventing a spell, a Lab Text to work
from, a connection to fix, a device and effect to enchant, a subject and vis
for a Longevity Ritual, and so on. Where the work pays or gains vis, you
choose whose: the laboratory's raw vis, the magus's own, or the covenant's
vis stores.

- **Vis of** and **Pawns of the other Art** (instilling an effect, a
  lesser enchantment, binding or empowering a familiar): each pawn may be
  of the work's Technique or its Form, in any mix (DE pp. 258, 266-268).
  **Vis of** names one; **Pawns of the other Art** says how many are of
  the other, and the rest are of the one named. Each Art's pawns must be
  in the store chosen.
- **Attune a Talisman** refuses an item another magus prepared (its Maker
  typed as a name, or another character), and one with an effect another
  magus instilled; the app records who instilled each effect when the
  season is applied (an assistant's help doesn't count against it). A
  magus has one talisman at a time (DE p. 259), and gains one new
  attunement a season (DE p. 260), which the device warns about.
- **More Lab Texts** (inventing from a Lab Text) adds further texts to learn
  the same season. Every spell must be of the first one's Technique and
  Form, and their levels together must be within the lowest of their Lab
  Totals (DE pp. 262, 264). The book allows several activities of any one
  type and Technique and Form in a season, such as inventing several
  spells or instilling several effects. The app offers it only for Lab
  Texts; plan the others one at a time.
- **Learn spells from a teacher** asks for the **Teacher**, any other magus
  who knows spells, and the **Spells taught**, of any Techniques and Forms.
  Scheduling plans the teacher's season as Teach. The levels taught are at
  most the teacher's highest Lab Total among them, those of one Technique
  and Form at most the teacher's Lab Total there, and no spell above the
  student's own Lab Total for it. The Spells Specialization counts for the
  student (DE p. 251). Every spell is learned in the one season.

### Spell design
<!-- help: invent-spell-design -->

<!-- tui -->
For inventing a spell, Start from picks any spell as a template (see
[Starting from a spell](help:invent-spell-start)), and New spell clears the
design.
<!-- /tui -->
<!-- gui -->
For inventing a spell, **Start from** picks any spell as a template (see
[Starting from a spell](help:invent-spell-start)); **New Spell** asks for it
first, and **Clear** beside it starts a blank design.
<!-- /gui -->
You type the
name, the effect, the Technique and Form, any requisites, the base level,
whether it is a Ritual, the Range, Duration and Target, any size or extra
magnitudes and the guideline used. The app works out the spell's level from
the base level and the parameters.

The **Guideline** field fills the base level from a catalog of supplement guidelines: see [Basing a spell on a guideline](help:invent-spell-guideline).

### Which Ranges, Durations and Targets
<!-- help: invent-spell-parameters -->

The Range, Duration and Target lists offer the standard ones, and beyond
them only those open to the magus, each with the standard one it costs as;
the line under the list says what opened each:

- **A Virtue or Mystery** that grants it: Hermetic Geometry's Line and
  Arcane Circle, Spell Timing's Held, Canaanite Magic's Veil of Death
  (as Sight), Fertility Ritual Magic's Unborn Child (as Individual),
  Hermetic Rune Magic's Rune (as Moon) and Inscription (as Individual), and
  the rest.
- **A breakthrough they reached** whose research goal grants a new Range,
  Duration or Target (see [Research Goals](help:section-research-goals)):
  Ancient Magic's Event (a Ritual: +1 magnitude over the Duration of what
  it does when triggered), Unlimited (a Ritual: Arcane Connection + 2
  magnitudes) and 19 Years (a Ritual: Year + 1), or one of the troupe's
  own, such as Range: Horizon (as Sight).
- **A spell they know** that uses a breakthrough's parameter: a Minor
  Breakthrough is learned with the Lab Text of a spell that uses it.

The Mysteries open these (Ars Magica Definitive Edition pp. 236-240; Houses
of Hermes: Mystery Cults p. 28; The Mysteries Revised Edition p. 116):

- **Faerie Magic**: Range **Road** (as Voice); Durations **Bargain** (the
  Duration of what it does once the bargain is broken, + 3 magnitudes, for at
  most a Year; listed as Bargain (Mom) to Bargain (Year)), **Fire** (as Moon;
  it is cast on a fire, so the spell must be Ignem or Imaginem, and the level
  line warns otherwise), **Until (Condition)** and **Year + 1** (as Year, both
  Rituals); Target **Bloodline** (as Structure). DE pp. 237-238.
- **Spell Timing**: Held and While (Condition) (as Concentration),
  Midday/Midnight and Not (Condition) (as Sun), Season (as Moon, a Ritual),
  and **If (Condition)**: the Duration of what it does when triggered + 4
  magnitudes, always a Ritual, listed as If (Mom) to If (Year). DE pp.
  239-240.
- **Sensory Magic**: Targets Flavor, Texture, Scent, Sound and **Spectacle**
  (as Individual, Part, Group, Structure and Boundary). Spectacle isn't said
  to need a Ritual, so it doesn't here. HoH:MC p. 28.
- **Road Magic**: Range and Target Road and Road Network. A magus with
  Mercurian Magic has them once he has learned Road Magic, a season's
  teaching with no further Virtue: tick **Has learned Road Magic** in his
  Hermetic Background (a starting magus whose parens has Mercurian Magic
  may have it; every Mercurian magus of an older save has it ticked). Any
  other magus needs the Road Magic Virtue, Initiated. TMRE p. 116.
- **Symbolic Magic**: Range, Duration and Target **Symbol** (as Arcane
  Connection, Year and Boundary), each a Ritual. Each needs a symbol of three
  charms, so Faerie Magic 3 for one, 9 for all three (Houses of Hermes:
  Mystery Cults p. 99).

Only a magus with Faerie Magic, Spell Timing, Sensory Magic or Symbolic
Magic may learn a spell with that Mystery's parameters: inventing it,
learning it from a Lab Text or being taught it says so and stops (DE pp.
236, 239; HoH:MC pp. 28, 99).

**Mutantum spells** (Houses of Hermes: True Lineages p. 101): a spell
whose level working ends in "; Boosted", "; Harnessed" or "; Tethered" (or
whose description says "Requires ... Magic or Mutantum Magic"), as House
Mercere's Mutantum spells in the catalog do, is learned from a Lab Text or
a teacher only by a magus with the Virtue for each of its qualities
(Boosted, Harnessed or Tethered Magic) or Mutantum Magic; Tamed Magic
counts as Harnessed and Tethered Magic. Inventing one needs Mutantum Magic
itself (p. 107). A saga's own spell takes a quality the same way, typed at
the end of its level working.

**Size / extra magnitudes** holds the magnitudes added for size and for
requisites that add an effect. Under the level, a line says what the Target
reaches if they are all spent on size: each multiplies it by ten, from the
Form's base Individual (a pony-sized animal for Animal, a cubic pace of
stone for Terram, and so on); size doesn't matter to Intellego spells, a
Circle, or a Mentem or Vim Individual (DE pp. 310-311, 546).

**Recurs each** (a magus with Spell Timing only) makes the spell recur:
each minute +5 magnitudes, each day +4, each month +3, each year +2, each
decade +1. Pick the row at or more often than the spell really recurs (every
ten minutes is +5). A recurring spell must be a Ritual, and a spell that
needs a Ritual for what it does (not for its level or parameters) can't
recur (DE p. 240).

A spell started from one with a parameter the magus can't use takes the
standard one it costs as. With the optional rule **Any spell parameter**
(Edit Saga), the lists also offer **Other...**: any Range, Duration or
Target, with the magnitudes it adds typed in.

### Starting from a spell
<!-- help: invent-spell-start -->

A new spell can start from any spell there is, as a template: the catalog's,
the saga's own, any magus's invented spells. Its name, effect, Arts,
requisites, base level, Range, Duration, Target and extra magnitudes are
copied into the design, and you change whatever you like.

The list opens with "A new spell (a blank design)", then the spells the
magus already knows, under **Known to (name)**, for inventing a variant of
one of their own, then **Every other spell**. **From** above the list shows
one group only, and typing searches the names and Arts (e.g. CrIg).
<!-- tui -->
F3 also lists the spells of sourcebooks not in play.
<!-- /tui -->
<!-- gui -->
**Show everything** also lists the spells of sourcebooks not in play.
<!-- /gui -->

A spell the magus knows has to be changed before it can be invented (a
different level, Range or name, say): planning it unchanged is refused,
since they know it already.

### Lab Total
<!-- help: invent-spell-total -->

<!-- tui -->
The Lab Total panel lists every term of the total and the result.
<!-- /tui -->
<!-- gui -->
The line under the fields gives the Lab Total, with every term of it in
brackets.
<!-- /gui -->
For a spell it uses the lower of each Art and the requisites of the same kind, and
adds the laboratory's terms from the [Lab Totals tab](help:tab-lab-totals).
The Lab work fields below the design add their own terms: the magnitude of a
similar spell the magus knows (when inventing, instilling an effect, making
a lesser enchantment or charged item, or empowering a familiar's bond), a
Magical Focus (the lower Art counted again)
and a Magic Theory specialty, if the magus has them, days away from the
laboratory (up to 10 cost nothing, 11 to 20 lower the total, more rule lab
work out), and any other modifier the troupe allows.

The total is built in a fixed order: the Arts and the laboratory's terms,
then the options and anyone helping, and last of all any halving (a lab
Flaw, Environmental Magic Condition, Short-Ranged Magic), so a halving
halves everything, once, rounded down.

Enchanting adds its own terms: **Shape & material** (capped by Magic
Theory), +5 in the magus's own talisman, +1 for each effect already in the
device sharing its Technique or Form, and for a device with Verditius
Runes, the Philosophiae of its maker (or of a later Verditius enchanter
with more) added to the Shape & material bonus, still capped, and for the
maker only, his current Craft score (Verditius Magic, DE pp. 240-241). The
runes add Philosophiae to each existing Shape and Material bonus. The app
adds it once, so when two bonuses apply, add the second Philosophiae to
Shape & material yourself. They count for enchanting only: a talisman's
casting bonuses use the plain bonus. Empowering a familiar's bond adds +5 when it shares the
binding's Technique or Form, +10 when it shares both.

With **Verditius Elder Runes**, each rune on the device of the effect's
Technique or Form adds that Art again (doubling it, as a Magical Focus does;
with a Focus as well it triples), and a rune on a device of its own tree's wood
(birch for Creo, yew Intellego, pine Perdo, alder Rego, elder Animal, willow
Aquam, ash Auram, holly Corpus, apple Herbam, juniper Ignem, oak Mentem,
hawthorn Vim; the app looks for the word in the device's name, description or
components) adds +2 (Houses of Hermes: Mystery Cults pp. 127-128). The maker
of an attuned item or an automaton adds his **Hubris** to every Lab Total for
enchanting it (pp. 129, 135; DE p. 241).

**Sensory Magic** (Houses of Hermes: Mystery Cults p. 28): a Bjornaer with
the Mystery adds his Heartbeast to the Lab Total inventing a spell with a
Flavor, Texture, Scent, Sound or Spectacle Target, or an Intellego spell
granting a magical sense (Taste, Touch, Smell, Hearing or Vision).

With **Faerie Magic**, experimenting or inventing a spell with the
Mystery's own parameters uses its score in place of Magic Theory when it
is the higher (the Lab Total shows the difference), and rolls that many
more botch dice: two of their botches make one, each 0 is a Warping Point,
and they never call for a Twilight check. With faerie vis only, a season may
use (Magic Theory + Faerie Magic) x 2 pawns; the app can't tell faerie vis
from other vis, so the vis-limit message gives that figure for you to judge
(DE p. 238).

Some laboratory Flaws stop work or halve it: **Missing Ingredients**
halves totals with its Art (and second Form); **Missing Equipment** and
**Restriction** refuse the activities they name, and **Elementary** all
but the one it names (Spells, Items, Familiar, Texts, Experimentation and
so on), with a message saying which Flaw does it.

Some Virtues and Flaws add a field of their own, shown only to a magus who
has them:

- **Potent Magic**: tick it when the work is in the Virtue's field (+3, or
  +6 for the Major Virtue; only the best one counts).
- **Cyclic Magic: in its time** (+3, when the good part of the cycle covers
  the whole season) and **Cyclic Magic: its bad time** (-3, when the bad
  part touches any of it).
- **Environmental Magic Condition**: tick it when the condition holds; the
  Lab Total is halved.
- **Laboratory Horoscope (+0 to +5)** (Planetary Magic, for enchanting a
  device; Celestial Magic, any lab work): the bonus sought. It needs a
  stress die + Intelligence + Artes Liberales (Astronomy, with Celestial
  Magic, when the magus has it; Academic Concentration counts it as
  astronomy) of three times the bonus. Type the die in
  **Horoscope die** or leave it blank for the app to roll it when the
  season is applied; a botch wastes the season.
- **Vis extracted** (Hermetic Alchemy, or an Extractor of a Form's Vis):
  extract a Form's vis instead of Vim. The Creo Vim total takes the Form
  as a requisite (the lower of the two counts); Hermetic Alchemy gives a
  pawn for every 20 points, the Form's Extractor a pawn for every 10. With
  Hermetic Alchemy, **Shape & material** adds the vessel's bonuses, up to
  Magic Theory.
- **A dark or sinister effect** (Chthonic Magic): tick it for such work;
  his Chthonic Magic then stands in for Magic Theory (Realms of Power: The
  Infernal p. 123).

Others apply by themselves: **Short-Ranged Magic** halves the total when
the spell or effect designed has a Range beyond Touch; **Disjointed Magic**
gets nothing from a similar spell known or from effects already in a device
sharing its Technique or Form; **Hubris** adds its Personality score to
instilling the magus's own talisman and to binding a familiar; **Waster of
Vis** needs a third more pawns (a quarter of those used is wasted), which
count toward the season's limit; **Magical Memory** lets the magus work from
their own Lab Texts wherever they are kept. A holy magus (**Holy Magic**)
halves his Lab Total when he works from another's Lab Text, a Hermetic
source (Realms of Power: The Divine p. 67); the halving shows in the
total. **Vulgar Alchemy** (The Mysteries Revised Edition pp. 32-35), when
experimenting while enchanting, adds Magic Lore to the Lab Total, and the
plan notes how to test the components (up to Magic Theory of them, simple
die + Perception + Magic Lore against 3 + 3 x the bonus proposed). Use it
for charged or lesser devices only.

### Experimenting
<!-- help: invent-spell-experiment -->

Work that can be done experimentally shows an Experiment box, a Risk modifier
and an optional research goal. Experimenting adds a simple die and the risk
to the Lab Total; the die is rolled when the season is advanced. With a
research goal, the experiment seeks a Discovery instead: the risk goes on the
Extraordinary Results roll, not the Lab Total (see the planning guide's
Experimenting section). A magus who is Averse to Risk can't experiment, and
one who is Prone to Chance must. Work whose Lab Total is too low can still be
planned experimentally: the season goes ahead, the chart is rolled and any
vis paid is lost if the die doesn't lift it. What the chart gives is settled
in Advance Season's [Experiment Results](help:advance-experiment-results)
step, and kept with the creation (see
[Living with an experiment](help:guide-lab-planning-living)).

### Assistants
<!-- help: invent-spell-assistants -->

**Assistant** names a helper: anyone else with The Gift and Magic Theory.
Scheduling plans their season as Assist in a laboratory with this magus,
for each season the work is planned, and the Lab Total then includes their
Intelligence and Magic Theory, for as many helpers as the magus's
Leadership allows (at least one). Each helper's own Virtues and Flaws count
too, as the magus's do: an assistant's Inventive Genius adds its +3 (DE p.
264). A familiar bound to the magus with Magic Theory helps the same way,
except with binding or empowering itself. If the helper already has a different
plan for the season, Schedule refuses and says so. More helpers are
planned on their own sheets, with Assist in a laboratory for the same
season. Clearing the lab work clears the assistant's season too; clearing
the assistant's season takes them off the lab work.

### When
<!-- help: invent-spell-when -->

<!-- tui -->
Beside the Lab Total, the When panel says what the season will achieve.
<!-- /tui -->
<!-- gui -->
After the Lab Total, the same line says what the season will achieve.
<!-- /gui -->
For
inventing a spell, the Lab Total must be above the spell's level, each season
adds the Lab Total less the level in points, and it shows the points
so far and the season the spell is projected to be invented. Other work says
what it will produce this season, such as pawns extracted or the aging-roll
modifier. Every lab season also gives 2 experience points of Exposure in
Magic Theory.

- **Effect Expiry**: an effect that lasts 1, 7 or 70 years from its first
  use gains 10, 5 or 2 times the season's excess, but still needs a Lab
  Total above its level (DE p. 257).
- **A charged item from a Lab Text** gets a charge for every 5 points of
  the whole Lab Total, rounded up (DE p. 262), and the device keeps that
  number.
- **Vis**: everything a season uses, an experiment's or a stabilization's
  vis and Waster of Vis's waste included, must be within twice the magus's
  Magic Theory (DE p. 250). With Verditius Elder Runes, enchanting a device
  uses Magic Theory x Philosophiae in its place, even when that is less, as
  smelting does (Houses of Hermes: Mystery Cults pp. 126, 128). A Verditius who crafted the item opens it for
  his Craft score fewer pawns (his Finesse when he shaped it by magic), at
  least one, and it still counts as opened in full.

### Scheduling
<!-- help: invent-spell-schedule -->

Schedule locks in the plan, replacing anything already planned for that
season; it refuses, and says why, if the work can't be done. For work that
takes several seasons, the app also plans each following season the work is
projected to need, stopping at a season that already has a plan.
<!-- tui -->
Reset puts back the plan as it was when the screen opened, and Cancel
leaves without changing anything.
<!-- /tui -->
<!-- gui -->
Cancel leaves without changing anything.
<!-- /gui -->
Nothing happens to the magus or the laboratory until the
season is advanced: then the work is applied, so a finished spell joins the
magus's spells, its Lab Text goes into the laboratory, and the laboratory's
Diary records the season. An unfinished invention keeps its points and
carries on into the next free season. See
[Advancing a season](help:advance-season).

## Basing a spell on a guideline
<!-- help: invent-spell-guideline -->

**Guideline** offers the Hermetic spell guidelines the supplements add,
listed under their Form (filter by Form or Technique). Choosing one sets
the Technique, Form and base level, writes the guideline into Base
effect, and for one that needs a Target (Magi of Hermes's inhuman body
parts: Part) sets that too; you can still change any of them. A General
guideline (shown as Gen) sets the Arts and Base effect but leaves the base
level for you to type. Clear it and the figures stay as they are.

- **Houses of Hermes: Societates**, Perception and Deception (pp.
  61-70): anamorphs, Muto Imaginem when the spell changes an existing
  image (a face) and Creo Imaginem when it stands on its own (base 1 for
  one sense, +1 magnitude for each further sense; pp. 65-66, and Magi of
  Hermes p. 93), synaesthesia (MuIm 2, p. 65),
  emotions aimed at someone (CrMe 4), undirected or aimed at a whole class
  (CrMe 5, p. 66), diminishing a mental capability (PeMe 4, pp. 66-67;
  pain, proprioception and balance count, p. 63), other states of
  consciousness (ReMe 4, p. 67), inscribed memories (CrMe 5, p. 69), a
  memory or emotion made solid (MuMe 5, p. 70) and inclinations to belief
  or indifference (ReMe 5, p. 70).
- **Societates' Rego craft table** (p. 61): an item made from bone,
  gemstone, glass, leather, metal, stone, timber, wood or wool, each at
  its level, at Personal Range (the Errata, p. 59, corrects the book's
  Touch), Momentary, Individual.
- **Societates' other guidelines**: ice in a natural shape (CrAq 3,
  p. 34), harmful gases causing a Light or Medium Wound (MuAu 4 and 5,
  p. 36), destroying one aspect of dirt (PeTe 5, p. 37), stone
  projectiles doing +5, +10 or +15 damage (ReTe 5 / 10 / 15, p. 38),
  improving all wounds (CrCo 25, p. 100) and sustaining or suppressing
  another's magic of one type (ReVi General, p. 129, as the Errata pp. 12
  and 60 reword it).
- **Magi of Hermes**: repairing a crafted item (CrTe 15, p. 31), inhuman
  body parts (MuCo 5, Target Part, p. 49), instant transport (ReTe 4,
  p. 92), preserving an Arcane Connection one, two or three steps (CrVi
  5 / 10 / 15, p. 113) and restoring a wooden item (CrHe 15, p. 139).

The Definitive Edition prints most of these among its own guidelines,
with the same levels, so they are offered whichever books are in play;
the rest (the anamorphs, the two level 5 emotions and the craft table)
only while Houses of Hermes: Societates is in play. For the Definitive Edition's
other guidelines, type the base level.

