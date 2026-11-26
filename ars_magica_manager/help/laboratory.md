# Laboratory sheet
<!-- help: laboratory -->

A laboratory sheet keeps one laboratory: what it's like, what it holds and
what has happened in it. A laboratory belongs to a covenant and has an
owner. The owner is a magus whose lab work is planned on this sheet and
whose Lab Totals it shows.

<!-- tui -->
The top panel, with the laboratory's identity and Characteristics, is always
on show above the tabs. Below it are six numbered tabs, opened with `1` to
`6`. On most tabs a details panel at the bottom shows more about the chosen
row, including the rules text of a Virtue, Flaw or Feature.

With focus on the top panel, More (`m`) offers Export and Update from a
File, and switches the laboratory between In Creation and In Play. While
it's In Creation, More also opens the Creation Worksheet. `d` on the top
panel deletes the laboratory, after asking.
<!-- /tui -->
<!-- gui -->
The header names the laboratory and whose sanctum it is, with the room its
Virtues leave and its aura as a seal. **Edit** beside it changes the
[Identity](help:section-lab-identity). The eight
[Characteristics](help:section-lab-characteristics) sit under the header.
The rail on the left holds the chapters:

- **Lab Totals**
- **Virtues & Flaws**
- **Specializations**, with the Features and rooms (see
  [Attributes](help:tab-lab-attributes))
- **Stores**, what [Inventory](help:tab-lab-inventory) lists
- **Seasons**, the [Planning](help:tab-lab-planning) list and the
  [Diary](help:tab-lab-diary)
- **Manage**

Clicking a card or row shows more about it in the inspector on the right,
including the rules text of a Virtue, Flaw or Feature.

The button in the header showing **In Creation** or **In Play** switches
the laboratory between them, after asking. While it's In Creation,
**Worksheet** beside it opens the Creation Worksheet. The **Manage**
chapter offers Export, Update from a File and Delete, which asks first.
<!-- /gui -->

The Creation Worksheet walks through setting the laboratory up. It covers
its owner, Size and Refinement, its Virtues, and whether it's one of its
covenant's starting laboratories, paid for from the covenant's Build
Points.

<!-- gui -->
The owner's name is a button in the header that opens
their sheet below the laboratory, so the trail leads back to it.
<!-- /gui -->

**See also:** [How lab planning works](help:guide-lab-planning), [How to create a character, covenant or laboratory](help:guide-creation)

### Identity
<!-- help: section-lab-identity -->

<!-- tui -->
The panel is titled with the laboratory's name, and `e` edits it.
<!-- /tui -->
<!-- gui -->
The laboratory's header, edited with **Edit** beside it.
<!-- /gui -->

**You type:** its name, location, aura modifier, whether its sanctum is
marked, its covenant and its owner, chosen from the saga's magi.

**The app works out:** the aura: the covenant's aura, with any Boons that
raise it, plus the modifier, shown with the covenant's realm.
<!-- tui -->
Also the Build Points: Size x 20, plus 10 for each Minor Virtue and 20 for
each Major one (DE Chapter 8: Laboratory).
<!-- /tui -->
<!-- gui -->
It's a seal in the realm's colour. Beside it are the Occupied Size, Free
Virtues and Base Safety from the
[Characteristics](help:section-lab-characteristics).
<!-- /gui -->

### Characteristics
<!-- help: section-lab-characteristics -->

The eight Characteristics are Size, Refinement, General Quality, Upkeep,
Safety, Warping, Health and Aesthetics. Each shows three figures: the value
you type, what the laboratory's Virtues and Flaws add, and the total.
<!-- tui -->
`e` edits only the typed values.
<!-- /tui -->
<!-- gui -->
They're drawn as a compass rose beside a card for each. **Edit** changes
only the typed values. Clicking a card shows where its total comes from,
naming each Virtue and Flaw's part (a Servant's with whose Intelligence it
is).
<!-- /gui -->

The app also works out these, following Covenants Chapter 9:

- **Occupied Size**: Virtue points less Flaw points less Refinement.
- **Free Virtues**: Size plus Refinement less the Virtue points net of
  Flaws.
- **Base Safety**: Refinement less any positive Occupied Size.

The laboratory's rolls use its Base Safety plus the Safety total, and its
Warping total. See [Safety and Warping](help:guide-lab-safety-warping).

Aesthetics is halved, after everything else, when the laboratory is
Invisible or Shrouded. It's at most -1 when the laboratory is Lightless (DE
p. 296; Covenants pp. 118-119). Each point of Aesthetics, good or bad, is
worth 5 xp in a fitting Reputation for its owner, perhaps over time (DE p.
290). Add it to the owner's Reputations as it comes.

A covenant that closes the year broke can't pay its laboratories' Upkeep.
The season record names each of them, and the troupe gives each a Flaw, or
takes a Virtue away, that lowers its Upkeep (DE p. 288).

## Planning
<!-- help: tab-lab-planning -->

Where the owner's lab work is planned, season by season. The list shows the
owner's seasons from the current one on:

- each planned activity, with the seasons it spans and how far it will
  have got
- any free seasons in between
- the first free season after the last plan

A season planned on the owner's own sheet, such as study, shows here too,
marked as such.

<!-- tui -->
**You type:** nothing here directly.

- `e` plans lab work for the chosen season on the [Invent Spell
  screen](help:invent-spell), or reopens the plan already there.
- `a` starts inventing a new spell from a blank design in the chosen
  season.
- `d` clears the chosen season's plan, with any later seasons scheduled to
  continue it, after asking.

**The app works out:** whether each plan can be done, its Lab Total line by
line in the details panel, and the progress of work that takes several
seasons. A row that can't be done says so in red, and the details panel
says why.
<!-- /tui -->
<!-- gui -->
On the desktop this list is **Planning**, at the top of the laboratory's
**Seasons** chapter, above the calendar of its seasons and the Diary.

**You type:** nothing here directly.

- **Plan** plans lab work for the season last clicked on the [lab work
  form](help:invent-spell), or reopens the plan already there.
- **New Spell** starts inventing a spell in that season, or the current
  one. It first asks for a spell to start from (any spell, the magus's own
  known spells first) or a blank design.
- **Clear** clears the season's plan, with any later seasons scheduled to
  continue it, after asking.

Below, in **A Season's Work**, **Bind Familiar** is there while the owner
has no familiar. **Perform Ritual** is there while the laboratory has a
Longevity Ritual's Lab Text (see [Lab Texts](help:section-lab-texts)). Each
has a line beside it saying what it does.

**The app works out:** whether each plan can be done, its Lab Total line by
line in the inspector, and the progress of work that takes several seasons.
A row that can't be done says so in red, and the inspector says why when
it's clicked.
<!-- /gui -->

A season ahead is worked out from the magus and laboratory as the seasons
planned before it will leave them. An Art raised by an earlier season's
study raises a later Lab Total, and an invention's points carry on. So an
item can be opened in Spring and an effect instilled in it in Summer,
planned together. The laboratory needs a magus as its owner before anything
can be planned.

**See also:** [Invent Spell screen](help:invent-spell),
[Lab Totals](help:tab-lab-totals),
[Advancing a season](help:advance-season), [How to plan and run a season](help:guide-seasons), [How lab planning works](help:guide-lab-planning)

## Research
<!-- help: tab-lab-research -->

The research the laboratory's owner has under way, while they have any:
their goals begun and not yet reached, and the seasons spent on them. It's
the magus's own [Research](help:tab-research), shown here to plan the
laboratory's seasons by, and the goals are added and changed there.
<!-- tui -->
Choosing a goal or a season of the log shows it as there.
<!-- /tui -->
<!-- gui -->
Clicking a goal or a season of the log shows it as there, the roll drawn
on the chart below the log.
<!-- /gui -->

### Research under way
<!-- help: section-lab-research-goals -->

The owner's goals begun and not yet reached, each with its points and
what waits on it: a Discovery to stabilize, or insights to invent.

### Research Log
<!-- help: section-lab-research-log -->

Every season spent on those goals, newest first, as on the magus's
[Research Log](help:section-research-log).

## Lab Totals
<!-- help: tab-lab-totals -->

What the owner's Lab Totals are when working in this laboratory, and what
goes into them.

**You type:** nothing. The figures come from the owner's sheet and from this
laboratory's aura, Characteristics, Specializations and Virtues and Flaws.

**The app works out:** the Lab Total for every Technique and Form, the Base
Lab Total they all share, and what each kind of lab activity adds (DE
Chapter 8: Laboratory). With no owner, or an owner who isn't a magus, the
page says so instead.

**See also:** [Planning](help:tab-lab-planning),
[Attributes](help:tab-lab-attributes),
[Invent Spell screen](help:invent-spell), [How lab planning works](help:guide-lab-planning)

### The totals
<!-- help: section-lab-totals-grid -->

A grid of the owner's Lab Total for each Technique (rows) and Form
(columns) in this laboratory. Each is the Technique plus the Form plus the
Base Lab Total below, with any Art Specialization of the laboratory
included where it applies.
<!-- gui -->
Each square is shaded by its total. Clicking one shows that Lab Total line
by line in the inspector.
<!-- /gui -->

### Base Lab Total
<!-- help: section-lab-totals-base -->

The terms every Lab Total shares:

- the owner's Intelligence and Magic Theory
- the aura's modifier for Hermetic magic in the laboratory's realm
- General Quality
- any Virtue or Flaw that adds to every total

Below them are the Art Specializations, each added only to totals using
that Art, and the Activity Specializations, each added only to its own
activity. Any multiplier from a Virtue is shown too, and is already in the
grid.

### By Activity
<!-- help: section-lab-totals-activity -->

What each kind of lab work adds on top of the grid: inventing spells,
enchanting items, working from a Lab Text, binding a familiar, Longevity
Rituals, extracting vis and experimenting. Below that are the results the
app works out from them:

- the Longevity Ritual's modifier to aging rolls
- the pawns of vis extracted in a season, a pawn for every 10 points,
  rounded up. Vis is extracted only in a Magic aura (DE p. 250).
- the most raw vis a season, and the largest shape and material bonus, the
  owner's Magic Theory allows

## Virtues & Flaws
<!-- help: tab-lab-vf -->

The laboratory's own Virtues and Flaws, from Covenants Chapter 9, side by
side.

**You type:** which Virtues and Flaws the laboratory has, chosen from the
catalog.

**The app works out:** the points each side comes to and what they add to
the Characteristics, Specializations and Lab Totals.

A warning line above the lists says when the laboratory has:

- more Virtues, net of Flaws, than Size plus Refinement allow
- more than one Focus
- a Virtue whose Specialization hasn't been chosen
- a Servant, Greater Guardian or Greater Horde with no Intelligence entered
- a Servant whose grog is no longer in the saga

**The Burning City's laboratory customizations** (Hermetic Projects pp.
26-27) are in the catalog:

- the Features Fumes (Pe, Au, Ig), Pool of Lava (Ig, Te), Thermal Spring
  (Cr, Aq, Ig) and Volcanic Rock (Mu, Ig, Te), each as a Greater or Lesser
  Feature
- Dormant Volcano, Active Volcano, Mineral Bath, Volcanic Spirit Forge and
  Hell Portal
- Volcanic Minerals, a Free Outfitting a Stone Harvester supplies to up to
  five laboratories: -1 Upkeep, +1 Te (p. 19)
- the Volcano Shape and Material bonus, +5 volcanoes

Experimenting on such work may bring the book's volcanic side effects (pp.
27-28). The troupe picks or invents them. Examples are lava tears, a
sulphurous stench, footprints that scorch, toxic fumes, humors thrown out
of balance (an Aging modifier of -1 or +1 for good), a crust of skin (+3
Soak for Sun), and a warm glow that keeps off hunger and thirst.

**See also:** [Characteristics](help:section-lab-characteristics),
[Features](help:section-lab-features),
[Lab Totals](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Virtues
<!-- help: section-lab-vf-virtues -->

The laboratory's Virtues, with the points they come to in the title. Adding
one picks it from the catalog, which shows each entry's rules, effects and
book as you go through it. A Virtue that grants a Specialization of the
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

A few Virtues add Safety worked out from an Intelligence (DE Chapter 8):

- **Servant** asks for the servant. That's one of the saga's grogs (those
  of the laboratory's covenant first) or, with none chosen, the servant's
  Intelligence typed in. It adds half that Intelligence, rounded up, to
  Safety. A chosen grog's Intelligence is read from their sheet each time,
  so it follows aging or any change to it.
- **Greater Guardian** and **Greater Horde** ask for the creature's
  Intelligence and add all of it to Safety.

**Natural Environment**, **Greater Guardian**, **Greater Horde** and the
Flaw **Sacrifices** put their Specialization points (3, 3, 2 and 2) in the
Art chosen. To split them among several, type the others under
Specializations: Other.

The Virtue's details, and its card, say whose Intelligence it is and what
it comes to, such as "Safety +2 (Kurt's Intelligence +3, halved, rounded
up)". A Feature Virtue is usually added along with its Feature, under
[Features](help:section-lab-features).

A Virtue a magic item grants reads "(Minor, from Wand)", and the Magic Item
and Enchantment Virtues name their item (see
[Magic Items](help:section-lab-magic-items)). Deleting a Virtue an item
grants, or the item's own Virtue, says what the laboratory loses with it.

### Flaws
<!-- help: section-lab-vf-flaws -->

The laboratory's Flaws, with the points they come to in the title. They work
like the Virtues. They're picked from the catalog, and Edit changes only
what one names, never which Flaw it is. A
laboratory may have only one Focus Flaw, and a Hidden Defect may be had
more than once.

Some Flaws ask a question when added:

- **Empty**: whether it costs +1 Upkeep or -1 Health.
- **Cramped**: the one activity it doesn't hamper, which takes a
  Specialization point.
- **Lesser** and **Greater Illusion**: which of the laboratory's Virtues is
  only an illusion. That Virtue then has no effect at all (DE p. 296).
- **Missing Ingredients**: an Art (and a second Form), whose Lab Totals it
  halves.
- **Missing Equipment**: one or two kinds of activity the laboratory can't
  be used for.
- **Elementary**: the one kind it can be used for, such as Spells, Items,
  Familiar, Texts or Experimentation.
- **Restriction**: the activity it forbids.

Lab work these last four rule out is refused when it's planned, with a
message naming the Flaw, and Missing Ingredients' halving shows in the Lab
Total (DE pp. 295-296).

### Personality Traits
<!-- help: section-lab-personality-traits -->

A laboratory with a Warping score has Personality Traits whose scores add
up to it, such as Whimsical +1 from faerie ingredients (DE p. 289). They
colour the experience of its owner and anyone living there, and suggest the
Warping its work and its inhabitants suffer. The storyguide may add one to
a Lab Total for an effect that matches it, or take it off for an opposite
one.
<!-- tui -->
`a` adds one, `e` edits the chosen one and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the trait last clicked.
<!-- /gui -->
The warning line above the lists says when they don't add up to the
laboratory's Warping.

## Attributes
<!-- help: tab-lab-attributes -->

The laboratory's Specializations, its Features, its magic items and its
rooms, then its [Connections](help:section-connections), its covenant and
where it is.
<!-- gui -->
On the desktop they're in the laboratory's **Specializations** chapter.
<!-- /gui -->

**You type:** the Features and where their points go, what each magic item
gives, Specialization points from other sources, and the rooms.

**The app works out:** each Specialization's score from all its sources and
how many count against the caps, and whether each item's points fit its
effect's level (Covenants Chapter 9).

**See also:** [Virtues & Flaws](help:tab-lab-vf),
[Lab Totals](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Specializations
<!-- help: section-lab-specializations -->

<!-- tui -->
A grid of every Specialization the laboratory has points in, grouped into
Activity and Art. Each group's title says how many count against its cap:
two Activities, and four Arts, no more than two of them Techniques.
<!-- /tui -->
<!-- gui -->
Every Specialization the laboratory has points in, as bars in two
sections, Activity Specializations and Art Specializations. Two Activities
and four Arts count, no more than two of them Techniques. Clicking one
shows where its points come from.
<!-- /gui -->
The scores are worked out from the Features, their Focus, the Virtues and
Flaws and the sources typed below.
<!-- tui -->
`Space` turns the chosen Specialization off or back on.
<!-- /tui -->
<!-- gui -->
**Turn Off/On** turns the one last clicked off or back on.
<!-- /gui -->
The app refuses to turn one on that would break a cap, and a newly gained
one that would break a cap arrives turned off.

Two Activity Specializations also count outside Lab Totals, when the
season is spent in the owner's laboratory (DE p. 291):

- **Teaching** adds its points, at most +3, to the Source Quality of
  teaching and training, and of teaching a Hermetic Virtue.
- **Texts** adds a point for every full 3 to Profession: Scribe when
  copying books and Lab Texts. It adds the same to the language when
  writing summae or rewriting Lab Texts.

A season of teaching, training, writing or copying has **In the
laboratory** ticked unless you untick it, for teaching away from the lab or
writing abroad. Unticked, neither counts. Teaching a spell is a Lab Total,
so the Spells Specialization helps it instead. Texts also adds to the Lab
Total of working from or decoding a Lab Text.

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
You type which Specialization, how many points (negative for a penalty) and
where they come from. The Specializations add them in.

### Features
<!-- help: section-lab-features -->

The laboratory's Features, each built on one of its Lesser or Greater
Feature Virtues. The title counts the Features against those Virtues.

Adding one takes two steps:

1. **Choose the kind and the Virtue.** Pick the kind of Feature from the
   catalog, or Custom, and the Virtue it's built on. With no free Feature
   Virtue, it offers to add one.
2. **Fill in the Feature.** Give its name, where its points go, and whether
   it's the laboratory's Focus.

Deleting a Feature keeps its Feature Virtue, free for another.

### Magic Items
<!-- help: section-lab-magic-items -->

What the enchanted devices kept in the laboratory give it, one row for each
effect, its title counting them (DE Chapter 8, Laboratory, and Covenants
Chapter 9, Magic Items for Laboratories). An item is installed as a Free
**Magic Item** Virtue, Minor when it's very large, or as an **Enchantment**
of the laboratory itself. The app adds that Virtue for you.

Each of its effects then gives the laboratory one of two things:

- **A Virtue or Flaw it duplicates.** The laboratory gains it at once, with
  no space cost and no Build Points at creation, and its modifications
  apply as usual. Virtues & Flaws shows it as "from" the item.
- **Points bought by its level.** One Specialization point for every 10
  levels of the effect, or one Characteristic point for every 20. The app
  refuses to save more points than the level buys.

Adding one takes two steps:

1. **Choose the effect.** Pick it from the devices kept here, then how the
   item is installed and which kind of benefit it gives.
2. **Choose the benefit.** Pick the Virtue it grants, or the points and
   where they go.

With no enchanted device kept in the laboratory there's nothing to choose.
Add one under [Enchanted Devices](help:section-lab-devices) first.

Deleting a row removes what that effect gives, and the Magic Item Virtue
once nothing else uses it. The device itself stays. Deleting the device, or
its effect, removes what it gave.

An item gives the laboratory nothing while its device is kept elsewhere.
Its points and the Virtue it grants stop counting, and its row says so,
until the device is back.

An effect must be new to the laboratory. The row warns when it grants a
Virtue the laboratory has already, or when its points need a higher level
than the effect has.

An item made into a Feature isn't entered here. Add it under Features, and
its Feature Virtue is paid for as usual.

**See also:** [Enchanted Devices](help:section-lab-devices),
[How to install a magic item in a laboratory](help:guide-lab-magic-item)

### Rooms
<!-- help: section-lab-rooms -->

The laboratory's rooms, each a name and a description you type. The app
works nothing out from them.

## Inventory
<!-- help: tab-lab-inventory -->

What the laboratory holds: raw vis, equipment, Arcane Connections, enchanted
devices, Lab Texts and other books.
<!-- gui -->
On the desktop this is the laboratory's **Stores** chapter.
<!-- /gui -->

**You type:** each entry, in its own section.

**The app works out:** the state of each Arcane Connection, each device's
figures, and how each Lab Text stands for the owner. Lab work changes these
lists when a season is advanced, such as vis paid or extracted, a
connection fixed or a Lab Text written.

**See also:** [Planning](help:tab-lab-planning),
[Diary](help:tab-lab-diary)

### Raw Vis
<!-- help: section-lab-raw-vis -->

The pawns of raw vis kept in the laboratory, one row per Art. You type the
Art and the pawns. Lab work that pays with the laboratory's vis takes it
from here when the season is advanced, and extracted vis can be sent here.
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

The Arcane Connections kept here. You type:

- what each connects to, and whether it's fixed
- if not fixed, its last active season and year, and any notes on how long
  it lasts
- where it came from, and a description

Fixing one is a season of lab work planned on
[Planning](help:tab-lab-planning). It must still be active as the season
starts (DE p. 250), so the app refuses one whose last season has passed.
When that season is advanced, the connection is marked fixed.

### Enchanted Devices
<!-- help: section-lab-devices -->

The enchanted devices kept in the laboratory, each followed by its effects.
The app works out each device's figures from what you type, such as
capacity, effect levels and charges (DE Chapter 8: Laboratory).
<!-- tui -->
`e` and `d` act on the chosen device or effect. More (`m`) offers:

- Instill an Effect, on a device that can take another effect
- Use a Charge, on a Charged Item
- Use an Effect, on a finished effect of an invested device or lesser
  enchantment
<!-- /tui -->
<!-- gui -->
**Edit** and **Delete** act on the row last clicked, a device or one of its
effects.

- **Instill** adds an effect to a device that can take another.
- **Use Charge** uses up a charge of a Charged Item.
- **Use** uses a finished effect of an invested device or lesser
  enchantment once.
<!-- /gui -->

What a device's effects give the laboratory itself, a Virtue or
Specialization and Characteristic points, is set under
[Magic Items](help:section-lab-magic-items).

**Using an effect** shows what it does at the table (DE p. 259).

- It goes off at Initiative Quickness + a stress die, +3 with a Fast
  Trigger (p. 257). The Quickness is the holder's, when a character holds
  it.
- Its Penetration is 0 unless levels were added for it, and no Fatigue is
  rolled.
- Each use counts against its uses per day, shown as "Today" in its
  details. When they're all spent, it asks whether a new day has begun. Yes
  gives every device's effects their uses again and counts this as the
  first.
- Advancing the season gives them all their uses again too.
- A Charged Item's effect is used a charge at a time instead.

**Weak Magic** gives only half the benefit of Penetration put into an item.
An effect its enchanter instils buys Penetration a level a point, not two
(DE p. 152). **Infernal vis** doubles botch dice in casting and needs a
roll on the experimental results for an enchanted item (DE p. 422). The
app doesn't mark vis by its realm, so add these at the table.

**Vis Transfer** isn't tracked, so it's noted here (DE p. 250). Moving raw
vis into another object takes a day in a laboratory, alongside other work.
It goes up to the object's Material and Size capacity and doesn't change
the vis's Art. An item opened for enchantment can't also hold raw vis. The
app keeps raw vis as pawns of each Art, not what holds them, so a transfer
changes nothing on the Raw Vis list.

**A very large item.** An item larger than huge (DE p. 255) has a size
multiplier one higher for each tenfold step past huge. A castle keep, a
hundred times a small room, is x7. It must be inside the laboratory to be
opened. Type its capacity in **Capacity**.

A Charged Item warns when more charges are recorded than its Lab Total
gives. That's the excess, or a fifth of the whole Lab Total when it was
made from a Lab Text.

**Arithmetic magic.** An invested device's **Arithmetic magic** field marks
a Numerologist's Book or a Hermetic Architecture component (The Mysteries
Revised Edition pp. 91-98).

- A lesser book (its parchment opened with 8 pawns, Magic Theory 4) gives
  its maker a book bonus of +4.
- A greater one (the whole book, 16 pawns, Magic Theory 8) gives +8.
- The bonus is never more than the maker's Artes Liberales, and counts only
  when they have Hermetic Numerology and hold the book.
- It adds to their Rote Lab Totals. For a magus with Hermetic Architecture
  it also adds to the Lab Totals for instilling effects in a component,
  shown as its own line.

**Talismans.** A talisman's details say what its magus's Talisman Mysteries
allow (The Mysteries Revised Edition pp. 89-90).

- **Great Talisman**: an attunement each season merely by using it, without
  working on it, still one a season. New components are crafted in
  whenever the magus reopens it, with no Craft roll, up to their Magic
  Theory in all.
- **Consummate Talisman**: its Personal Muto Vim effects work on the
  magus's Formulaic spells, listed as "On their Formulaic spells". Its Names
  of Power work on any spell they cast, spoken aloud, their bonus at most
  Magic Theory.
- Inscription on the Soul alone attunes no bonus without work on the
  talisman (the errata to TMRE p. 70).

**Verditius devices** (Houses of Hermes: Mystery Cults pp. 127-135). A
device whose Verditius maker crafted it in its first season has
**Verditius Runes** ticked. **Crafted with** names the Craft Ability used,
or is blank when the maker shaped it by magic. With Verditius Runes
ticked, an invested device shows three more fields for the House's Inner
Mysteries.

- **Elder rune (Technique)** and **Elder rune (Form)** are the elder runes
  inscribed when it was opened (p. 127).
  - It has at most one of each, and only for the twelve Arts that have
    runes. There are none for Muto, Imaginem or Terram.
  - Opening it then takes a pawn of each rune's Art besides its Vim, and
    the magus must know Verditius Elder Runes.
  - Each rune adds 5 to the level of every effect instilled in it, and its
    pawn counts toward what the device holds.
- **Verditius item** marks an attuned item or an automaton. Making either
  needs its Mystery.
  - Item Attunement (p. 135): the item holds its maker's highest Technique
    + highest Form + Philosophiae + the Craft they made it with, whatever
    its material and size.
  - Automata (pp. 129-130): type its Magic Might, 10 + Size + the
    material's base points, as its **Capacity**. It can't be a talisman,
    and its powers can't maintain concentration.

**House price.** A device crafted by a Verditius shows the House's price
(Houses of Hermes: Mystery Cults pp. 114-115). The line also gives the
Hubris experience selling it brings.

- To another magus, it's twice the vis it took, besides that vis. The vis
  it took is its opening, less its maker's Craft, and every effect's,
  elder runes included.
- To a mundane buyer, it's 15 Mythic Pounds for each pawn of that vis, the
  Primus's fixed price. An automaton's construction is charged on top.
- A charged item takes no vis. Its price to a magus is twice the vis its
  maker could have extracted in the seasons it took, worked out from their
  Vim extraction Lab Total. To a mundane buyer it's 15 Mythic Pounds a pawn
  of that vis.
- Prices bind only the House. Other magi charge what they like.

A forge-companion is an unGifted craftsman with the Virtue. They add +1 per
5 points of the Craft their master is using to the master's Lab Total, and
a Verditius may have as many as their Leadership (pp. 113-114). Add it to
the Lab Total by hand for now.

**Mercere's Portals** (Houses of Hermes: True Lineages pp. 100-101). An
effect named Mercere's Portal is instilled only by a magus who has learned
the method, by a season studying a Portal or its Lab Texts. Record it as a
reached research goal named Mercere's Portal on their Research.

- Each of the two archways is an invested device instilling Rego Terram 65
  (Base 35, +4 Arcane Connection, +10 unlimited uses). Each holds an Arcane
  Connection to the other.
- The season's notes add that a connecting ceremony, like Hermes' Portal
  and with no roll, is held at both at once. The Portals work only once
  joined, and moving one then destroys it.
- An effect whose level working names Boosted, Harnessed or Tethered is
  invested only by a magus with Mutantum Magic (p. 101).

### Lab Texts
<!-- help: section-lab-texts -->

The laboratory's Lab Texts, as a table with each text's kind, Arts, level,
author and whether the owner can use it. A Lab Text is added like a book.
Inventing a spell, instilling an effect and a Longevity Ritual each write
one here when the season is advanced.
<!-- tui -->
`/` filters the table by kind, Technique, Form, level, and to texts the
owner can read.

Perform Ritual in More (`m`) performs a Longevity Ritual again from its
text at once. It takes vis but no season.
<!-- /tui -->
<!-- gui -->
The bar above the table narrows it by kind, Technique, Form and level, and
**Readable only** to texts the owner can read. **Texts Read**, beside Add,
Edit and Delete, sets whose texts the owner reads.

**Perform Ritual**, a button on the [Planning](help:tab-lab-planning) list
in the Seasons chapter, performs a Longevity Ritual again from its text at
once. It takes vis but no season.
<!-- /gui -->
As for casting a ritual spell, the vis of each Art is at most the magus's
score in that Art, which may make it impossible (DE p. 261; The Mysteries
Revised Edition p. 42).

### Books
<!-- help: section-lab-books -->

<!-- tui -->
The laboratory's other books (everything kept here that isn't a Lab Text),
the same as in any other book list. `Space` marks several books. With books
marked, `e` gives them all a new owner and `d` deletes them all, after
asking.
<!-- /tui -->
<!-- gui -->
The laboratory's other books (everything kept here that isn't a Lab Text),
as cards at the foot of the Stores chapter. Clicking one shows it in the
inspector. On the desktop they can't be added, edited or deleted here yet,
so use the terminal version.
<!-- /gui -->

## Diary
<!-- help: tab-lab-diary -->

A record of what has happened in the laboratory, by season.
<!-- gui -->
On the desktop the Diary is at the foot of the laboratory's **Seasons**
chapter, newest first, with Add, Edit and Delete.
<!-- /gui -->

**You type:** entries of your own, each a year, season, activity type, name
and details.

**The app works out:** nothing, but it adds entries itself. It does so when
lab work is applied as a season is advanced, when vis is moved in or out,
and when a Longevity Ritual is performed again from its text.

**See also:** [Planning](help:tab-lab-planning),
[Advancing a season](help:advance-season)

# Invent Spell screen
<!-- help: invent-spell -->

<!-- tui -->
The screen where a season of the laboratory owner's lab work is planned,
opened from the [Planning tab](help:tab-lab-planning).
<!-- /tui -->
<!-- gui -->
The form where a season of the laboratory owner's lab work is planned. It
opens in a window of its own, from the [Planning](help:tab-lab-planning)
list's **Plan** or **New Spell**.
<!-- /gui -->
Despite its name it plans every kind of lab work:

- inventing a spell from a design or from a Lab Text, or learning spells
  from a teacher
- extracting vis, fixing an Arcane Connection, a Longevity Ritual
- the enchantment activities: opening an item, instilling an effect, a
  lesser enchantment, a charged item, attuning a talisman, investigating
  an enchanted item
- decoding another magus's Lab Texts, taming a magical beast, stabilizing a
  Discovery
- setting up, refining, taking over or moving the laboratory
- binding or empowering a familiar

A season ahead is checked as the seasons planned before it leave things
(see [Planning](help:tab-lab-planning)).

Its title names the work, the magus, the laboratory and the season. As you
type, it shows the Lab Total and when the work will be done, worked out
under DE Chapter 8: Laboratory.

**See also:** [Planning](help:tab-lab-planning),
[Lab Totals](help:tab-lab-totals),
[Advancing a season](help:advance-season), [How lab planning works](help:guide-lab-planning)

### Lab work
<!-- help: invent-spell-activity -->

The first field chooses the lab work.
<!-- tui -->
Press Enter on **Lab work** to open the list of lab work, grouped by Type:
Inventing, Enchanting, Familiar, Texts and vis, and The laboratory. Type to
search, or choose a **Type** or **Book** above the list to narrow it (F2
steps through the Types). Press Enter on the work wanted.
<!-- /tui -->
<!-- gui -->
Click **Lab work** to open the list of lab work, grouped by Type:
Inventing, Enchanting, Familiar, Texts and vis, and The laboratory. Type to
search, or choose a **Type** or **Book** above the list to narrow it, then
choose the work wanted.
<!-- /gui -->
The magus's most recent seasons are listed first, under Recent, until the
list is narrowed.

Then only the fields that work needs are shown, such as a spell design for
inventing a spell, a device and effect to enchant, or a subject and vis for
a Longevity Ritual. Where the work pays or gains vis, you choose whose: the
laboratory's raw vis, the magus's own, or the covenant's vis stores.

- **Vis of** and **Pawns of the other Art** (instilling an effect, a
  lesser enchantment, binding or empowering a familiar). Each pawn may be
  of the work's Technique or its Form, in any mix (DE pp. 258, 266-268).
  **Vis of** names one, and **Pawns of the other Art** says how many are of
  the other. The rest are of the one named. Each Art's pawns must be in the
  store chosen.
- **Attune a Talisman** refuses an item another magus prepared, whether its
  Maker is typed as a name or is another character. It also refuses one
  with an effect another magus instilled. The app records who instilled
  each effect when the season is applied, and an assistant's help doesn't
  count against it. A magus has one talisman at a time (DE p. 259), and
  gains one new attunement a season (DE p. 260), which the device warns
  about.
- **Attune the talisman to** appears on a season opening the magus's
  talisman or instilling an effect in it. It chooses the one attunement it
  gains that season from its Shape & Material bonuses not yet attuned (DE
  p. 259). When the season is applied it joins the talisman's attunements,
  dated.
- **More Lab Texts** (inventing from a Lab Text) adds further texts to learn
  the same season.
  - Every spell must be of the first one's Technique and Form, and their
    levels together must be within the lowest of their Lab Totals (DE pp.
    262, 264).
  - The book allows several activities of any one type and Technique and
    Form in a season, such as inventing several spells or instilling
    several effects. The app offers it only for Lab Texts, so plan the
    others one at a time.
- **A General spell's Lab Text** teaches the level it records, since a
  General spell is known at the level of the version learned (DE p. 313).
  Set the text's **Level** in the library first; a text with none can't
  be used. Each magus who learns from it gets a version of their own at
  that level, even from the same text (DE p. 226), named "Lab Text: ..."
  as its source, and the Lab Text they write teaches that version. A
  teacher who knows a General spell at no recorded level can't teach it.
- **Learn spells from a teacher** asks for the **Teacher**, any other magus
  who knows spells, and the **Spells taught**, of any Techniques and Forms.
  Scheduling plans the teacher's season as Teach. Every spell is learned in
  the one season.
  - The levels taught are at most the teacher's highest Lab Total among
    them.
  - Those of one Technique and Form are at most the teacher's Lab Total
    there.
  - No spell can be above the student's own Lab Total for it. The Spells
    Specialization counts for the student (DE p. 251).

### Spell design
<!-- help: invent-spell-design -->

<!-- tui -->
For inventing a spell, Start from picks any spell as a template (see
[Starting from a spell](help:invent-spell-start)), and New spell clears the
design.
<!-- /tui -->
<!-- gui -->
For inventing a spell, **Start from** picks any spell as a template (see
[Starting from a spell](help:invent-spell-start)). **New Spell** asks for it
first, and **Clear** beside it starts a blank design.
<!-- /gui -->

You type the name, the effect, the Technique and Form, any requisites, the
base level, whether it's a Ritual, the Range, Duration and Target, any size
or extra magnitudes and the guideline used. The app works out the spell's
level from the base level and the parameters.

For a Creo spell, tick **Creates something lasting** when what it makes is
meant to stay once a Momentary Duration ends, such as a wall or food. Such
a spell must be a Ritual, and the form says so until it is one (DE p. 311).
A flame or bolt that's gone at once, as Pilum of Fire, isn't lasting (DE
p. 344).

The **Guideline** field fills the base level from a catalog of supplement
guidelines. See [Basing a spell on a guideline](help:invent-spell-guideline).

### Which Ranges, Durations and Targets
<!-- help: invent-spell-parameters -->

The Range, Duration and Target lists offer the standard ones. Beyond them
they offer only those open to the magus, each with the standard one it
costs as. The line under the list says what opened each:

- **A Virtue or Mystery** that grants it, such as Hermetic Geometry's Line
  and Arcane Circle, Spell Timing's Held, Canaanite Magic's Veil of Death
  (as Sight), Fertility Ritual Magic's Unborn Child (as Individual), and
  Hermetic Rune Magic's Rune (as Moon) and Inscription (as Individual).
- **A breakthrough they reached** whose research goal grants a new Range,
  Duration or Target (see [Research Goals](help:section-research-goals)).
  - Ancient Magic's Event, a Ritual: +1 magnitude over the Duration of what
    it does when triggered.
  - Unlimited, a Ritual: Arcane Connection + 2 magnitudes.
  - 19 Years, a Ritual: Year + 1.
  - One of the troupe's own, such as Range: Horizon (as Sight).
- **A spell they know** that uses a breakthrough's parameter. A Minor
  Breakthrough is learned with the Lab Text of a spell that uses it.

The Mysteries open these (DE pp. 236-240; Houses of Hermes: Mystery Cults
p. 28; The Mysteries Revised Edition p. 116):

- **Faerie Magic** (DE pp. 237-238)
  - Range **Road** (as Voice).
  - Duration **Bargain**: the Duration of what it does once the bargain is
    broken, + 3 magnitudes, for at most a Year. It's listed as Bargain (Mom)
    to Bargain (Year).
  - Duration **Fire** (as Moon). It's cast on a fire, so the spell must be
    Ignem or Imaginem, and the level line warns otherwise.
  - Durations **Until (Condition)** and **Year + 1** (as Year), both
    Rituals.
  - Target **Bloodline** (as Structure).
- **Spell Timing** (DE pp. 239-240)
  - Held and While (Condition) (as Concentration).
  - Midday/Midnight and Not (Condition) (as Sun).
  - Season (as Moon, a Ritual).
  - **If (Condition)**: the Duration of what it does when triggered + 4
    magnitudes, always a Ritual, listed as If (Mom) to If (Year).
- **Sensory Magic** (HoH:MC p. 28): Targets Flavor, Texture, Scent, Sound
  and **Spectacle**, as Individual, Part, Group, Structure and Boundary.
  Spectacle isn't said to need a Ritual, so it doesn't here.
- **Road Magic** (TMRE p. 116): Range and Target Road and Road Network.
  - A magus with Mercurian Magic has them once they've learned Road Magic,
    a season's teaching with no further Virtue. Tick **Has learned Road
    Magic** in their Hermetic Background.
  - A starting magus whose parens has Mercurian Magic may have it, and
    every Mercurian magus of an older save has it ticked.
  - Any other magus needs the Road Magic Virtue, Initiated.
- **Symbolic Magic** (Houses of Hermes: Mystery Cults p. 99): Range,
  Duration and Target **Symbol** (as Arcane Connection, Year and Boundary),
  each a Ritual. Each needs a symbol of three charms, so Faerie Magic 3 for
  one, 9 for all three.

Only a magus with Faerie Magic, Spell Timing, Sensory Magic or Symbolic
Magic may learn a spell with that Mystery's parameters. Inventing it,
learning it from a Lab Text or being taught it says so and stops (DE pp.
236, 239; HoH:MC pp. 28, 99).

**Mutantum spells** (Houses of Hermes: True Lineages p. 101). Some spells
have a level working that ends in "; Boosted", "; Harnessed" or
"; Tethered", as House Mercere's Mutantum spells in the catalog do, or a
description that says "Requires ... Magic or Mutantum Magic".

- Such a spell is learned from a Lab Text or a teacher only by a magus with
  the Virtue for each of its qualities (Boosted, Harnessed or Tethered
  Magic) or Mutantum Magic.
- Tamed Magic counts as Harnessed and Tethered Magic.
- Inventing one needs Mutantum Magic itself (p. 107).
- A saga's own spell takes a quality the same way, typed at the end of its
  level working.

**Size / extra magnitudes** holds the magnitudes added for size and for
requisites that add an effect. Under the level, a line says what the Target
reaches if they're all spent on size. Each multiplies it by ten, from the
Form's base Individual, such as a pony-sized animal for Animal or a cubic
pace of stone for Terram. Size doesn't matter to Intellego spells, a
Circle, or a Mentem or Vim Individual (DE pp. 310-311, 546).

**Recurs each** makes the spell recur, for a magus with Spell Timing only.

- Each minute is +5 magnitudes, each day +4, each month +3, each year +2,
  each decade +1.
- Pick the row at or more often than the spell really recurs. Every ten
  minutes is +5.
- A recurring spell must be a Ritual. A spell that needs a Ritual for what
  it does, not for its level or parameters, can't recur (DE p. 240).

A spell started from one with a parameter the magus can't use takes the
standard one it costs as. With the optional rule **Any spell parameter** in
the saga's settings, the lists also offer **Other...**. That's any Range,
Duration or Target, with the magnitudes it adds typed in.

### Starting from a spell
<!-- help: invent-spell-start -->

A new spell can start from any spell there is, as a template: the
catalog's, the saga's own, or any magus's invented spells. Its name,
effect, Arts, requisites, base level, Range, Duration, Target and extra
magnitudes are copied into the design, and you change whatever you like.

The list opens with "A new spell (a blank design)". Then come the spells
the magus already knows, under **Known to (name)**, for inventing a variant
of one of their own, then **Every other spell**. **From** above the list
shows one group only, and typing searches the names and Arts (e.g. CrIg).
<!-- tui -->
F3 also lists the spells of sourcebooks not in play.
<!-- /tui -->
<!-- gui -->
**Show everything** also lists the spells of sourcebooks not in play.
<!-- /gui -->

A spell the magus knows has to be changed before it can be invented, such
as a different level, Range or name. Planning it unchanged is refused,
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
For a spell it uses the lower of each Art and the requisites of the same
kind, and adds the laboratory's terms from [Lab Totals](help:tab-lab-totals).

The Lab work fields below the design add their own terms:

- **Similar spell known**: the magnitude of the highest similar spell the
  magus knows, when inventing, instilling an effect, making a lesser
  enchantment or charged item, or empowering a familiar's bond (DE pp.
  258, 260, 267)
- a Magical Focus and a Magic Theory specialty, if the magus has them
- days away from the laboratory. Up to 10 cost nothing, 11 to 20 lower the
  total, and more rule lab work out.
- any other modifier the troupe allows

A **Magical Focus** counts the lower Art again (DE p. 94).

- When the focus records the Arts it spans, on the Virtue's **The Arts it
  spans**, it applies **By its Arts** unless you choose otherwise. Choose
  otherwise for a focus narrower than its Arts, such as birds within
  Animal.
- A requisite counts. A Creo Auram spell with an Ignem requisite falls in a
  fire focus, and the lower Art counted again may be a requisite's.

**Recreating a flawed creation** is offered to Invent a spell, the
enchanting work and a Longevity Ritual. It's there when the magus has a
creation of that kind an experiment changed, in an earlier season. Choose
it, and the Magic Theory they experimented with is added again (DE p.
274). Each is listed with its chart results, and whether it's flawed is
yours to judge. Where the record doesn't keep the score, **Magic Theory
then** asks for it (see [How to recreate a flawed
creation](help:guide-lab-planning-recreate)).

**Spent on a project's stage** is offered when the magus's covenant has a
staged Hermetic Project, such as a Burning City, an Intangible Assassin or
a Living Corpse. Choose the stage the season's work belongs to. When the
season is played, it's kept with that stage's works on the covenant's
Projects.

The total is built in a fixed order. First come the Arts and the
laboratory's terms, then the options and anyone helping, and last of all
any halving, such as a lab Flaw, Environmental Magic Condition or
Short-Ranged Magic. So a halving halves everything, once, rounded down.

**Enchanting** adds its own terms:

- **Shape & material**, capped by Magic Theory (DE p. 258). Choosing the
  effect to instil fills it with the device's Shape & Material bonuses
  whose "applies to" shares a word with the effect's name, description,
  Technique or Form. Change it when the troupe reads them otherwise.
- +5 in the magus's own talisman
- +1 for each effect already in the device sharing its Technique or Form
- for a device with Verditius Runes, the Philosophiae of its maker, or of a
  later Verditius enchanter with more, added to the Shape & material bonus,
  still capped. For the maker only, it also adds their current Craft score
  (Verditius Magic, DE pp. 240-241).

The runes add Philosophiae to each existing Shape and Material bonus. The
app adds it once, so when two bonuses apply, add the second Philosophiae to
Shape & material yourself. They count for enchanting only, and a
talisman's casting bonuses use the plain bonus. Empowering a familiar's
bond adds +5 when it shares the binding's Technique or Form, +10 when it
shares both.

**Verditius Elder Runes** (Houses of Hermes: Mystery Cults pp. 127-128).

- Each rune on the device of the effect's Technique or Form adds that Art
  again. That doubles it, as a Magical Focus does, and with a Focus as well
  it triples.
- A rune on a device of its own tree's wood adds +2. The app looks for the
  word in the device's name, description or components. The woods are
  birch for Creo, yew Intellego, pine Perdo, alder Rego, elder Animal,
  willow Aquam, ash Auram, holly Corpus, apple Herbam, juniper Ignem, oak
  Mentem and hawthorn Vim.
- The maker of an attuned item or an automaton adds their **Hubris** to
  every Lab Total for enchanting it (pp. 129, 135; DE p. 241).

**Sensory Magic** (Houses of Hermes: Mystery Cults p. 28). A Bjornaer with
the Mystery adds their Heartbeast to the Lab Total for inventing a spell
with a Flavor, Texture, Scent, Sound or Spectacle Target. The same goes for
an Intellego spell granting a magical sense: Taste, Touch, Smell, Hearing
or Vision.

**Faerie Magic** (DE p. 238). Experimenting, or inventing a spell with the
Mystery's own parameters, uses its score in place of Magic Theory when it's
the higher. The Lab Total shows the difference.

- It rolls that many more botch dice. Two of their botches make one, each
  0 is a Warping Point, and they never call for a Twilight check.
- With faerie vis only, a season may use (Magic Theory + Faerie Magic) x 2
  pawns. The app can't tell faerie vis from other vis, so the vis-limit
  message gives that figure for you to judge.

Some laboratory [Flaws](help:section-lab-vf-flaws) stop work or halve it,
with a message saying which Flaw does it.

Some Virtues and Flaws add a field of their own, shown only to a magus who
has them:

- **Potent Magic**: tick it when the work is in the Virtue's field. It's +3,
  or +6 for the Major Virtue, and only the best one counts.
- **Cyclic Magic: in its time** (+3, when the good part of the cycle covers
  the whole season) and **Cyclic Magic: its bad time** (-3, when the bad
  part touches any of it).
- **Environmental Magic Condition**: tick it when the condition holds. The
  Lab Total is halved.
- **Laboratory Horoscope (+0 to +5)**: the bonus sought, from Planetary
  Magic for enchanting a device or Celestial Magic for any lab work.
  - It needs a stress die + Intelligence + Artes Liberales of three times
    the bonus. With Celestial Magic, Astronomy counts when the magus has
    it, and Academic Concentration counts it as astronomy.
  - Type the die in **Horoscope die**, or leave it blank for the app to
    roll it when the season is applied. A botch wastes the season.
- **Vis extracted** (Hermetic Alchemy, or an Extractor of a Form's Vis):
  extract a Form's vis instead of Vim.
  - The Creo Vim total takes the Form as a requisite, and the lower of the
    two counts.
  - Hermetic Alchemy gives a pawn for every 20 points, the Form's Extractor
    a pawn for every 10.
  - With Hermetic Alchemy, **Shape & material** adds the vessel's bonuses,
    up to Magic Theory.
- **Dark or sinister (Chthonic Magic)**. Tick it for such work.
  The magus's Chthonic Magic then stands in for Magic Theory (Realms of
  Power: The Infernal p. 123).

Others apply by themselves:

- **Short-Ranged Magic** halves the total when the spell or effect designed
  has a Range beyond Touch.
- **Disjointed Magic** gets nothing from a similar spell known, or from
  effects already in a device sharing its Technique or Form.
- **Hubris** adds its Personality score to instilling the magus's own
  talisman and to binding a familiar.
- **Waster of Vis** needs a third more pawns, a quarter of those used being
  wasted. They count toward the season's limit.
- **Magical Memory** lets the magus work from their own Lab Texts wherever
  they're kept.
- **Holy Magic**: a holy magus halves their Lab Total when working from
  another's Lab Text, a Hermetic source (Realms of Power: The Divine p.
  67). The halving shows in the total.
- **Vulgar Alchemy** (The Mysteries Revised Edition pp. 32-35) adds Magic
  Lore to the Lab Total when experimenting while enchanting. Use it for
  charged or lesser devices only. The plan notes how to test the
  components: up to Magic Theory of them, each a simple die + Perception +
  Magic Lore against 3 + 3 x the bonus proposed.

### Experimenting
<!-- help: invent-spell-experiment -->

Work that can be done experimentally shows an Experiment box, a Risk
modifier and an optional research goal. Experimenting adds a simple die and
the risk to the Lab Total, and the die is rolled when the season is
advanced.

- With a research goal, the experiment seeks a Discovery instead. The risk
  goes on the Extraordinary Results roll, not the Lab Total (see the
  planning guide's Experimenting section).
- A magus who's Averse to Risk can't experiment, and one who's Prone to
  Chance must.
- Work whose Lab Total is too low can still be planned experimentally. The
  season goes ahead and the chart is rolled, and any vis paid is lost if
  the die doesn't lift it.

What the chart gives is settled in Advance Season's [Experiment
Results](help:advance-experiment-results) step, and kept with the creation
(see [Living with an experiment](help:guide-lab-planning-living)).

### Assistants
<!-- help: invent-spell-assistants -->

**Assistant** names a helper, anyone else with The Gift and Magic Theory,
or one of the magus's own apprentices without them, marked "(servant)".
Scheduling plans their season as Assist in a laboratory with this magus,
for each season the work is planned.

- A servant adds nothing to the Lab Total from Intelligence and Magic
  Theory. Instead, for that season, the laboratory counts a Servant
  Virtue: half the servant's Intelligence (rounded up) in Safety, +1
  Aesthetics and +1 to a Mentem Specialization (Apprentices p. 34,
  Covenants p. 116). A child with negative Intelligence lowers Safety.
- A servant isn't counted against Leadership, and doesn't learn to read
  the Lab Texts written that season. They gain Exposure in Magic Theory.

- The Lab Total then includes their Intelligence and Magic Theory, for as
  many helpers as the magus's Leadership allows, at least one.
- Each helper's own Virtues and Flaws count too, as the magus's do. An
  assistant's Inventive Genius adds its +3 (DE p. 264).
- A familiar bound to the magus with Magic Theory helps the same way,
  except with binding or empowering itself.
- If the helper already has a different plan for the season, Schedule
  refuses and says so.
- More helpers are planned on their own sheets, with Assist in a laboratory
  for the same season.

Clearing the lab work clears the assistant's season too. Clearing the
assistant's season takes them off the lab work.

### When
<!-- help: invent-spell-when -->

<!-- tui -->
Beside the Lab Total, the When panel says what the season will achieve.
<!-- /tui -->
<!-- gui -->
After the Lab Total, the same line says what the season will achieve.
<!-- /gui -->
For inventing a spell, the Lab Total must be above the spell's level, and
each season adds the Lab Total less the level in points. It shows the
points so far and the season the spell is projected to be invented. Other
work says what it will produce this season, such as pawns extracted or the
aging-roll modifier. Every lab season also gives 2 experience points of
Exposure in Magic Theory.

- **Effect Expiry**: an effect that lasts 1, 7 or 70 years from its first
  use gains 10, 5 or 2 times the season's excess. It still needs a Lab
  Total above its level (DE p. 257).
- **A charged item from a Lab Text** gets a charge for every 5 points of
  the whole Lab Total, rounded up (DE p. 262), and the device keeps that
  number.
- **Vis**: everything a season uses must be within twice the magus's Magic
  Theory (DE p. 250). That includes an experiment's or a stabilization's
  vis and Waster of Vis's waste.
  - With Verditius Elder Runes, enchanting a device uses Magic Theory x
    Philosophiae in its place, even when that's less, as smelting does
    (Houses of Hermes: Mystery Cults pp. 126, 128).
  - A Verditius who crafted the item opens it for their Craft score fewer
    pawns, or their Finesse when they shaped it by magic. It's at least
    one, and it still counts as opened in full.

### Scheduling
<!-- help: invent-spell-schedule -->

Schedule locks in the plan, replacing anything already planned for that
season. If the work can't be done, it refuses and says why. For work that
takes several seasons, the app also plans each following season the work
is projected to need, stopping at a season that already has a plan.
<!-- tui -->
Reset puts back the plan as it was when the screen opened, and Cancel
leaves without changing anything.
<!-- /tui -->
<!-- gui -->
Cancel leaves without changing anything.
<!-- /gui -->

Nothing happens to the magus or the laboratory until the season is
advanced. Then the work is applied, so a finished spell joins the magus's
spells, its Lab Text goes into the laboratory, and the laboratory's Diary
records the season. An unfinished invention keeps its points and carries on
into the next free season. See [Advancing a season](help:advance-season).

## Basing a spell on a guideline
<!-- help: invent-spell-guideline -->

**Guideline** offers the Hermetic spell guidelines the supplements add,
listed under their Form. Filter them by Form or Technique.

- Choosing one sets the Technique, Form and base level, and writes the
  guideline into Base effect. For one that needs a Target, such as Magi of
  Hermes's inhuman body parts (Part), it sets that too.
- You can still change any of them.
- A General guideline, shown as Gen, sets the Arts and Base effect but
  leaves the base level for you to type.
- Clear it and the figures stay as they are.

The guidelines are these:

- **Houses of Hermes: Societates**, Perception and Deception (pp. 61-70)
  - anamorphs, base 1 for one sense, +1 magnitude for each further sense
    (pp. 65-66, and Magi of Hermes p. 93). They're Muto Imaginem when the
    spell changes an existing image, such as a face, and Creo Imaginem when
    it stands on its own.
  - synaesthesia (MuIm 2, p. 65)
  - emotions aimed at someone (CrMe 4), or undirected or aimed at a whole
    class (CrMe 5, p. 66)
  - diminishing a mental capability (PeMe 4, pp. 66-67). Pain,
    proprioception and balance count (p. 63).
  - other states of consciousness (ReMe 4, p. 67)
  - inscribed memories (CrMe 5, p. 69)
  - a memory or emotion made solid (MuMe 5, p. 70)
  - inclinations to belief or indifference (ReMe 5, p. 70)
- **Societates' Rego craft table** (p. 61): an item made from bone,
  gemstone, glass, leather, metal, stone, timber, wood or wool, each at its
  level. It's Personal Range, Momentary, Individual. The Errata (p. 59)
  corrects the book's Touch to Personal.
- **Societates' other guidelines**
  - ice in a natural shape (CrAq 3, p. 34)
  - harmful gases causing a Light or Medium Wound (MuAu 4 and 5, p. 36)
  - destroying one aspect of dirt (PeTe 5, p. 37)
  - stone projectiles doing +5, +10 or +15 damage (ReTe 5 / 10 / 15, p. 38)
  - improving all wounds (CrCo 25, p. 100)
  - sustaining or suppressing another's magic of one type (ReVi General,
    p. 129, as the Errata pp. 12 and 60 reword it)
- **Magi of Hermes**
  - repairing a crafted item (CrTe 15, p. 31)
  - inhuman body parts (MuCo 5, Target Part, p. 49)
  - instant transport (ReTe 4, p. 92)
  - preserving an Arcane Connection one, two or three steps (CrVi 5 / 10 /
    15, p. 113)
  - restoring a wooden item (CrHe 15, p. 139)

The Definitive Edition prints most of these among its own guidelines, with
the same levels, so they're offered whichever books are in play. The rest
are offered only while Houses of Hermes: Societates is in play. Those are
the anamorphs, the two level 5 emotions and the craft table. For the
Definitive Edition's other guidelines, type the base level.

# Retire Flawed Spells
<!-- help: advance-retire-flawed -->

When a magus finishes recreating a flawed spell this season, Advance
Season asks, before the season is played, whether to retire the flawed
one. Both versions stay known unless you tick **Retire the flawed
(spell)?**, since a magus may know many usable versions of the same spell
(DE p. 279). Retiring it only takes it off Known Spells, once the new spell
is invented. Its record and Lab Text are kept. A season the experiment
wastes doesn't ask. See [How to recreate a flawed
creation](help:guide-lab-planning-recreate).
