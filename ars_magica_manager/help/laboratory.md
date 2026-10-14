# Laboratory sheet
<!-- help: laboratory -->

A laboratory sheet keeps one laboratory: what it is like, what it holds and
what has happened in it. A laboratory belongs to a covenant and has an owner,
a magus whose lab work is planned on this sheet and whose Lab Totals it
shows.

The top panel, with the laboratory's identity and Characteristics, is always
on show above the tabs. Below it are six numbered tabs, opened with `1` to
`6`. On most tabs a details panel at the bottom shows more about the chosen
row, including the rules text of a Virtue, Flaw or Feature.

With focus on the top panel, More (`m`) offers Export and Update from a
File (on the desktop, in the laboratory's **Manage** chapter), and switches the
laboratory between In Creation and In Play (In Creation / In Play). While it
is In Creation, More also opens the Creation Worksheet, which walks through
setting the laboratory up: its owner, Size and Refinement, its Virtues, and
whether it is one of its covenant's starting laboratories, paid for from the
covenant's Build Points. `d` on the top panel deletes the laboratory, after
asking.

**See also:** [How lab planning works](help:guide-lab-planning), [How to create a character, covenant or laboratory](help:guide-creation)

### Identity
<!-- help: section-lab-identity -->

The panel is titled with the laboratory's name. **You type** (with `e`) its
name, location, aura modifier, whether its sanctum is marked, its covenant
and its owner, chosen from the saga's magi. **The app works out** the aura,
the covenant's aura (with any Boons that raise it) plus the modifier, shown
with the covenant's realm, and the Build Points: Size x 20, plus 10 for each
Minor Virtue and 20 for each Major one (Ars Magica Definitive Edition,
Chapter 8: Laboratory).

### Characteristics
<!-- help: section-lab-characteristics -->

The eight Characteristics (Size, Refinement, General Quality, Upkeep, Safety,
Warping, Health and Aesthetics) each show three figures: the value you type,
what the laboratory's Virtues and Flaws add, and the total. `e` edits only
the typed values. The app also works out Occupied Size (Virtue points less
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

**You type:** nothing here directly. `e` plans lab work for the chosen
season on the [Invent Spell screen](help:invent-spell), or reopens the plan
already there; `a` starts inventing a new spell from a blank design in the
chosen season; `d` clears the chosen season's plan, with any later seasons
scheduled to continue it, after asking.

**The app works out:** whether each plan can be done (a row that can't says
so in red, and the details panel says why), the Lab Total of each plan line
by line in the details panel, and the progress of work that takes several
seasons. The laboratory needs a magus as its owner before anything can be
planned.

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

**The app works out:** the points each side comes to, what they add to the
Characteristics, Specializations and Lab Totals, and a warning line above
the lists when the laboratory has more Virtues (net of Flaws) than Size plus
Refinement allow, more than one Focus, or a Virtue whose Specialization
hasn't been chosen.

**See also:** [Characteristics](help:section-lab-characteristics),
[Features](help:section-lab-features),
[Lab Totals tab](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Virtues
<!-- help: section-lab-vf-virtues -->

The laboratory's Virtues, with the points they come to in the title. Adding
one picks it from the catalog, which shows the highlighted entry's
rules, effects and book under the list; a Virtue that grants a Specialization of the
owner's choice asks for it then. Virtues can't be edited, only deleted and
added again. A Feature Virtue is usually added along with its Feature on the
Attributes tab.

### Flaws
<!-- help: section-lab-vf-flaws -->

The laboratory's Flaws, with the points they come to in the title. They work
like the Virtues: picked from the catalog, deleted rather than edited. A
laboratory may have only one Focus Flaw.

## Attributes tab
<!-- help: tab-lab-attributes -->

The laboratory's Specializations, its Features and its rooms.

**You type:** the Features and what their points go to, any Specialization
points from a source the app doesn't work out itself, and the rooms.

**The app works out:** each Specialization's score from all its sources, and
how many count against the limits on Activity and Art Specializations
(Ars Magica Fifth Edition: Covenants, Chapter 9).

**See also:** [Virtues & Flaws tab](help:tab-lab-vf),
[Lab Totals tab](help:tab-lab-totals), [How lab planning works](help:guide-lab-planning)

### Specializations
<!-- help: section-lab-specializations -->

A grid of every Specialization the laboratory has points in, grouped into
Activity and Art, each group's title saying how many count against its cap
(two Activities, four Arts, no more than two of them Techniques). The scores
are worked out from the Features, their Focus, the Virtues and Flaws and the
sources typed below. `Space` turns the chosen Specialization off or back on;
the app refuses to turn one on that would break a cap, and a newly gained
one that would break a cap arrives turned off.

### Specializations: Other
<!-- help: section-lab-specialties -->

Specialization points from sources the app doesn't work out itself, nested
inside Specializations. You type which Specialization, how many points
(negative for a penalty) and where they come from; the grid above adds them
in.

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
here when the season is advanced, and extracted vis can be sent here. Move
Vis in More (`m`) moves pawns to another laboratory, covenant or magus, and
both Diaries record it.

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
Laboratory). `e` and `d` act on the chosen device or effect. More (`m`)
offers Instill an Effect on a device that can take another effect, and Use a
Charge on a Charged Item.

### Lab Texts
<!-- help: section-lab-texts -->

The laboratory's Lab Texts, as a table with each text's kind, Arts, level,
author and whether the owner can use it. A Lab Text is added like a book;
inventing a spell, instilling an effect and a Longevity Ritual each write one
here when the season is advanced. `/` filters the table by kind, Technique,
Form, level, and to texts the owner can read. Perform Ritual in More (`m`)
performs a Longevity Ritual again from its text at once: it takes vis but no
season. On the desktop, Perform Ritual is a button in the Seasons chapter,
beside Bind Familiar while the owner has no familiar, and **Texts Read**
beside the Lab Texts sets whose texts the owner reads.

### Books
<!-- help: section-lab-books -->

The laboratory's other books (everything kept here that isn't a Lab Text),
the same as in any other book list. `Space` marks several books; with books
marked, `e` gives them all a new owner and `d` deletes them all, after
asking.

## Diary tab
<!-- help: tab-lab-diary -->

A record of what has happened in the laboratory, by season.

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

Its title names the work, the magus, the laboratory and the season. As you
type, it shows the Lab Total and when the work will be done, worked out under
Ars Magica Definitive Edition, Chapter 8: Laboratory.

**See also:** [Planning tab](help:tab-lab-planning),
[Lab Totals tab](help:tab-lab-totals),
[Advancing a season](help:advance-season), [How lab planning works](help:guide-lab-planning)

### Lab work
<!-- help: invent-spell-activity -->

The first field chooses the lab work. The screen then shows only the fields
that work needs: a spell design for inventing a spell, a Lab Text to work
from, a connection to fix, a device and effect to enchant, a subject and vis
for a Longevity Ritual, and so on. Where the work pays or gains vis, you
choose whose: the laboratory's raw vis, the magus's own, or the covenant's
vis stores.

### Spell design
<!-- help: invent-spell-design -->

For inventing a spell, Start from picks an existing spell the magus doesn't
know as the starting point, and New spell clears the design. You type the
name, the effect, the Technique and Form, any requisites, the base level,
whether it is a Ritual, the Range, Duration and Target, any size or extra
magnitudes and the guideline used. The app works out the spell's level from
the base level and the parameters; a Range, Duration or Target the app
doesn't list can be chosen as Other, with the magnitudes it adds typed in.

### Lab Total
<!-- help: invent-spell-total -->

The Lab Total panel lists every term of the total and the result. For a
spell it uses the lower of each Art and the requisites of the same kind, and
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
to the Lab Total; the die is rolled when the season is advanced. A magus who
is Averse to Risk can't experiment, and one who is Prone to Chance must.

### Assistants
<!-- help: invent-spell-assistants -->

Assistants aren't chosen here. A character who will help is planned on their
own sheet, with Assist in a laboratory for the same season; the Lab Total
then includes their Intelligence and Magic Theory, for as many helpers as
the magus's Leadership allows (at least one).

### When
<!-- help: invent-spell-when -->

Beside the Lab Total, the When panel says what the season will achieve. For
inventing a spell, the Lab Total must be above the spell's level, each season
adds the Lab Total less the level in points, and the panel shows the points
so far and the season the spell is projected to be invented. Other work says
what it will produce this season, such as pawns extracted or the aging-roll
modifier. Every lab season also gives 2 experience points of Exposure in
Magic Theory.

### Scheduling
<!-- help: invent-spell-schedule -->

Schedule locks in the plan, replacing anything already planned for that
season; it refuses, and says why, if the work can't be done. For work that
takes several seasons, the app also plans each following season the work is
projected to need, stopping at a season that already has a plan. Reset puts
back the plan as it was when the screen opened, and Cancel leaves without
changing anything. Nothing happens to the magus or the laboratory until the
season is advanced: then the work is applied, so a finished spell joins the
magus's spells, its Lab Text goes into the laboratory, and the laboratory's
Diary records the season. An unfinished invention keeps its points and
carries on into the next free season. See
[Advancing a season](help:advance-season).
