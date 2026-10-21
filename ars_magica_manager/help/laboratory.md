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
pawns of vis extracted in a season, and the most raw vis a season and the
largest shape and material bonus the owner's Magic Theory allows.

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

The Virtue's details, and its card, say whose Intelligence it is and what it
comes to: "Safety +2 (Kurt's Intelligence +3, halved, rounded up)". A Feature Virtue is usually added along with its Feature on the
Attributes tab.

### Flaws
<!-- help: section-lab-vf-flaws -->

The laboratory's Flaws, with the points they come to in the title. They work
like the Virtues: picked from the catalog, deleted rather than edited. A
laboratory may have only one Focus Flaw.

## Attributes tab
<!-- help: tab-lab-attributes -->

The laboratory's Specializations, its Features and its rooms.
<!-- gui -->
On the desktop they are in the laboratory's **Specializations** chapter.
<!-- /gui -->

**You type:** the Features and what their points go to, any Specialization
points from a source the app doesn't work out itself, and the rooms.

**The app works out:** each Specialization's score from all its sources, and
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
is fixed, how long it lasts if not, where it came from and a description.
Fixing one is a season of lab work planned on the Planning tab; when that
season is advanced, the connection is marked fixed.

### Enchanted Devices
<!-- help: section-lab-devices -->

The enchanted devices kept in the laboratory, each followed by its effects.
The app works out each device's figures, such as capacity, effect levels and
charges, from what you type (Ars Magica Definitive Edition, Chapter 8:
Laboratory).
<!-- tui -->
`e` and `d` act on the chosen device or effect. More (`m`) offers Instill
an Effect on a device that can take another effect, and Use a Charge on a
Charged Item.
<!-- /tui -->
<!-- gui -->
**Edit** and **Delete** act on the row last clicked, a device or one of its
effects. **Instill** adds an effect to a device that can take another, and
**Use Charge** uses up a charge of a Charged Item.
<!-- /gui -->

### Lab Texts
<!-- help: section-lab-texts -->

The laboratory's Lab Texts, as a table with each text's kind, Arts, level,
author and whether the owner can use it. A Lab Text is added like a book;
inventing a spell, instilling an effect and a Longevity Ritual each write one
here when the season is advanced.
<!-- tui -->
`/` filters the table by kind, Technique, Form, level, and to texts the
owner can read. Perform Ritual in More (`m`) performs a Longevity Ritual
again from its text at once: it takes vis but no season.
<!-- /tui -->
<!-- gui -->
The bar above the table narrows it by kind, Technique, Form and level, and
**Readable only** to texts the owner can read. **Texts Read**, beside Add,
Edit and Delete, sets whose texts the owner reads. **Perform Ritual**, a
button on the [Planning](help:tab-lab-planning) list in the Seasons chapter,
performs a Longevity Ritual again from its text at once: it takes vis but
no season.
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
from a Lab Text, extracting vis, fixing an Arcane Connection, a Longevity
Ritual, the enchantment activities (opening an item, instilling an effect, a
lesser enchantment, a charged item, attuning a talisman, investigating an
enchanted item), decoding another magus's Lab Texts, taming a magical beast,
stabilizing a Discovery, setting up, refining, taking over or moving the
laboratory, and binding or empowering a familiar.

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
the base level and the parameters; a Range, Duration or Target the app
doesn't list can be chosen as Other, with the magnitudes it adds typed in.

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
similar spell the magus knows, a Magical Focus (the lower Art counted again)
and a Magic Theory specialty, if the magus has them, days away from the
laboratory (up to 10 cost nothing, 11 to 20 lower the total, more rule lab
work out), and any other modifier the troupe allows.

### Experimenting
<!-- help: invent-spell-experiment -->

Work that can be done experimentally shows an Experiment box, a Risk modifier
and an optional research goal. Experimenting adds a simple die and the risk
to the Lab Total; the die is rolled when the season is advanced. With a
research goal, the experiment seeks a Discovery instead: the risk goes on the
Extraordinary Results roll, not the Lab Total (see the planning guide's
Experimenting section). A magus who is Averse to Risk can't experiment, and
one who is Prone to Chance must.

### Assistants
<!-- help: invent-spell-assistants -->

**Assistant** names a helper: anyone else with The Gift and Magic Theory.
Scheduling plans their season as Assist in a laboratory with this magus,
for each season the work is planned, and the Lab Total then includes their
Intelligence and Magic Theory, for as many helpers as the magus's
Leadership allows (at least one). If the helper already has a different
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
