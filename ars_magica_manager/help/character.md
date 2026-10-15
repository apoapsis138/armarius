# Character sheet
<!-- help: character -->

<!-- tui -->
The character sheet holds one character of the saga: a magus, companion or
grog. The top panel, with the character's name and Characteristics, stays
on screen above the tabs whichever tab is open. Below it are the numbered
tabs, opened with `1` to `7` (a character who is not a magus has no Hermetic
Magic tab, so the later tabs move up a number). On a tab with a list, the
details panel at the bottom shows the chosen row, including the rules text
of a Virtue, Flaw, Ability or spell.

A new character starts In Creation. The button beside Edit in the top panel
shows which mode the character is in; clicking it, or choosing In Creation /
In Play from More (`m`) while the top panel has focus, moves the character
between the two after asking first. While the character is In Creation, More
also offers the Creation Worksheet, which walks through the creation steps,
and the button beside the mode opens it too.
<!-- /tui -->
<!-- gui -->
The character sheet holds one character of the saga: a magus, companion or
grog. The header, with the character's name, Confidence, Warping,
Decrepitude and how they are faring, and the Characteristic cards under it
stay on the page whichever chapter is open. The rail on the left lists the
chapters: Description, Abilities, Virtues & Flaws, Hermetic Magic (a
character who is not a magus has none), Inventory, Planning, Diary and,
last, Manage. Clicking a row, card, Art or Casting Score shows it in the
inspector on the right, including the rules text of a Virtue, Flaw, Ability
or spell.

A new character starts In Creation. The header shows which mode the
character is in: In Creation (a quill) or In Play (a seal). Clicking it
moves the character between the two after asking first. While the
character is In Creation, the sheet is drawn on ruled drafting vellum and
**Worksheet** under the mode opens the Creation Worksheet, which walks
through the creation steps.
<!-- /gui -->

<!-- gui -->
The frame beside the name holds the character's portrait:
click it to choose a picture from anywhere on the computer. The app copies
the picture into the save folder's `portraits` folder, so moving or deleting
the original does not lose it, and clicking again changes or removes it.
While there is no portrait the frame shows the House symbol. A magus's
**Sanctum** button opens their laboratory below their sheet, so the trail
leads back to them; while they have no laboratory it reads **New Sanctum**
and creates one that is theirs.
<!-- /gui -->

**See also:** [How the app handles advancement](help:guide-advancement), [How to plan and run a season](help:guide-seasons), [How to create a character, covenant or laboratory](help:guide-creation)

### Character info
<!-- help: section-char-info -->

<!-- tui -->
The top panel names the character. You type the Setting, Covenant, Type,
Confidence Score and Confidence Points, and the Size, and for a magus the
Assigned Laboratory; the True Faith Score and Faith Points show only for a
character who can have them.
<!-- /tui -->
<!-- gui -->
The header names the character. Its **Edit** button edits the Setting,
Covenant, Type, Confidence Score and Confidence Points, and the Size, and
for a magus the Assigned Laboratory; the True Faith Score and Faith Points
show only for a character who can have them. The Age, Covenant, Laboratory,
Type and Size are listed under At a Glance at the top of the Description
chapter.
<!-- /gui -->
The app works out the Age from Year Born (in
Biographical Detail) and the saga's current year, and shows the current year
and season dimmed because they belong to the saga. Size includes any Virtue
that changes it (Ars Magica Definitive Edition, Chapter 3: Characters).
<!-- tui -->
With
the top panel focused, `d` deletes the character after saying what happens
to what they own, and More (`m`) offers Export, which writes the character
to a file another saga can import, and Update from a File, which reads such
a file back over them.
<!-- /tui -->
<!-- gui -->
The sheet's last chapter, **Manage**, offers **Export**, which writes the
character to a file another saga can import, **Update from a File**, which
reads such a file back over them, **Print to PDF** (see
[Printing a record](help:print-record)), and **Delete**, which deletes the
character after saying what happens to what they own.
<!-- /gui -->

### Characteristics
<!-- help: section-char-characteristics -->

<!-- tui -->
The eight Characteristics, typed in with `e`. They are always on screen
<!-- /tui -->
<!-- gui -->
The eight Characteristics, as cards under the header, typed in with the
**Edit** button at the end of the cards. They are always on the page
<!-- /gui -->
because so much of the sheet is worked out from them: Soak, Encumbrance,
Casting Scores and combat totals all use them.

## Description tab
<!-- help: tab-description -->

Who the character is, and how they are faring: background, personality,
reputation, age and health.
<!-- gui -->
At a Glance at the top lists the Age, Covenant, Laboratory, Type, Size and
any True Faith; a magus's familiar has its card here, which opens its page.
<!-- /gui -->

**You type:** the Hermetic Background (magi only), the Biographical Detail,
Personality Traits and Reputations, Decrepitude, Effects of Aging and
Warping, and the character's Wounds and Fatigue Level.

**The app works out:** Soak, Encumbrance, the Wound Penalty, the total
penalty and the Damage Table in Health, and when a season is applied, the
Winter aging roll and the year's Warping Points, which it writes into
Aging & Warping.

**See also:** [Abilities tab](help:tab-abilities),
[Virtues & Flaws tab](help:tab-vf), [Diary tab](help:tab-diary),
[Advancing a season](help:advance-season), [How the app handles advancement](help:guide-advancement)

### Hermetic Background
<!-- help: section-hermetic-background -->

<!-- tui -->
A magus's House, Domus Magna, Primus, Parens, Covenant of Apprenticeship,
Age of Apprenticeship and Wizard's Sigil, all typed in with `e`.
<!-- /tui -->
<!-- gui -->
A magus's House, Domus Magna, Primus, Parens, Covenant of Apprenticeship,
Age of Apprenticeship and Wizard's Sigil, all typed in with the section's
**Edit** button.
<!-- /gui -->
The House
decides which Virtue is the magus's free House Virtue, which then counts no
points on the [Virtues & Flaws tab](help:tab-vf). Reads Lab Texts of lists
the authors whose Lab Texts this magus can read;
<!-- tui -->
the Lab Texts Read
button, or Lab Texts Read in More (`m`), sets an author, the level the magus
reads them to (0 forgets the author) and whether the magus decoded them or
was taught.
<!-- /tui -->
<!-- gui -->
the **Texts Read** button
beside the section, also beside the Lab Texts of the magus's laboratory,
sets an author, the level the magus reads them to (0 forgets the author)
and whether the magus decoded them or was taught. While a magus has no
familiar, a blank **Bind Familiar** card stands under the section, where
the familiar would be.
<!-- /gui -->

### Biographical Detail
<!-- help: section-char-biographical -->

Player, Birth Name, Year Born, Race/Nationality, Place of Origin, Religion,
Title/Profession, Height, Weight, Hair, Eyes, Handedness, Physical
<!-- tui -->
Description and the free-text Biography in the second column. All of it is
typed in with `e`.
<!-- /tui -->
<!-- gui -->
Description and the free-text Biography, under Appearance and Biography.
All of it is typed in with the section's **Edit** button.
<!-- /gui -->
Year Born is what the app works the character's Age out
from.

### Personality Traits
<!-- help: section-personality-traits -->

The character's Personality Traits, each a name and a score that you type
(Ars Magica Definitive Edition, Chapter 3: Characters). Binding a familiar
adds a Loyal (Partner) +3 trait to the magus, which you can then change or
delete like any other.

### Reputations
<!-- help: section-reputations -->

The character's Reputations, each a name and a score that you type
(Ars Magica Definitive Edition, Chapter 3: Characters). A Reputation may also say its type (Hermetic, Local, Noble, Academic,
Ecclesiastical or Infernal) and how far it reaches, both shown in
brackets after its score.

### Aging & Warping
<!-- help: section-aging -->

<!-- tui -->
Decrepitude, the Effects of Aging and the Warping Score and Points, typed in
with `e`.
<!-- /tui -->
<!-- gui -->
Decrepitude, the Effects of Aging and the Warping Score and Points, typed in
with the **Edit** button of the Aging section; Warping and Decrepitude also
show as dials in the header.
<!-- /gui -->
The same form has Gain Warping Points now, for points gained from
one event; two or more at once take a magus to the edge of Wizard's
Twilight, which the app rolls straight away. When Winter is applied, the app
makes the yearly aging roll and adds the apparent age, Aging Points,
Decrepitude points and any Longevity Ritual here, and adds the year's
Warping Points from a Longevity Ritual or a strong aura of another realm
(Ars Magica Definitive Edition, Chapter 10: Long-Term Events).

### Health
<!-- help: section-char-health -->

<!-- tui -->
The left column shows Soak, Encumbrance and the Wound Penalty, worked out
from Stamina, armour, Virtues and the load of the character's Personal Gear,
then the wounds as typed.
<!-- /tui -->
<!-- gui -->
The wounds as typed, on the Damage Table for the character's Size, then the
Fatigue Level, then Soak, Encumbrance, the Wound Penalty and the total
penalty from wounds and fatigue. Soak, Encumbrance and the Wound Penalty are
worked out from Stamina, armour, Virtues and the load of the character's
Personal Gear.
<!-- /gui -->
Enduring Constitution makes the wound and fatigue
<!-- tui -->
penalties 1 better and Low Tolerance 1 worse. The right column shows the Fatigue Level, the
total penalty from wounds and fatigue, and the Damage Table for the
character's Size (Ars Magica Definitive Edition, Chapter 11: Obstacles).
`e` edits the wounds and a Soak adjustment; the Edit Fatigue button, or
Edit Fatigue in More (`m`), sets the Fatigue Level.
<!-- /tui -->
<!-- gui -->
penalties 1 better and Low Tolerance 1 worse (Ars Magica Definitive
Edition, Chapter 11: Obstacles). The **Wounds** button beside the section
edits the wounds and a Soak adjustment, and the **Fatigue** button sets the
Fatigue Level.
<!-- /gui -->

## Abilities tab
<!-- help: tab-abilities -->

Every Ability the character has, in one list grouped by category.

<!-- tui -->
**You type:** each Ability's total XP and its Specialty. `a` picks a new
Ability from the catalog; the picker shows the highlighted Ability's
description under the list.
<!-- /tui -->
<!-- gui -->
**You type:** each Ability's total XP and its Specialty. **Add** picks a
new Ability from the catalog; the list shows the chosen Ability's
description beside it.
<!-- /gui -->
Abilities from supplements (the Divine's Holy
Powers and Methods, Mythic Herbalism, Mechanica of Heron...) are listed only
while their book is in play. **Hedge Art** is the category for a hedge
tradition's Arts, such as the learned elementalists' Elementalist Fire: like
a Supernatural Ability, one is learned through the Virtue that grants it,
and it advances on the Ability XP table.

**The app works out:** the score from the XP, and the XP the next score
needs, shown as score and then XP over the next total (Ars Magica Definitive
Edition, Chapter 3: Characters, Advancement Table). When a Virtue or Flaw
gives a fixed bonus or penalty, such as Puissant, the score used follows in
brackets. While the XP is typed, the form shows the score it buys and the
total XP the next score needs ("Latin: Score 2 · Score 3 at 30 xp").

<!-- gui -->
Each Ability has a mark beside its name, cut like the
Art symbols: a dark block with a light figure, such as a quill for every
Dead Language or a shield for Parma Magica. The chosen Ability's mark is
shown larger, with its engraved lines, in the panel beside the list. An
Ability the app has no mark for shows its category's.
<!-- /gui -->

**See also:** [Virtues & Flaws tab](help:tab-vf),
[Planning tab](help:tab-planning), [How the app handles advancement](help:guide-advancement)

## Virtues & Flaws tab
<!-- help: tab-vf -->

<!-- tui -->
The character's Virtues and Flaws, side by side, with one details panel
below both that shows the chosen one's effects and rules text.
<!-- /tui -->
<!-- gui -->
The character's Virtues and Flaws, side by side, each a card; clicking one
shows its effects and rules text in the inspector.
<!-- /gui -->

**You type:** nothing; you pick each Virtue or Flaw from the catalog.

**The app works out:** the points each side comes to, in the section
titles, coloured by whether the two sides balance (Ars Magica Definitive
Edition, Chapter 4: Virtues and Flaws), and the effects of each one on the
rest of the sheet.

**See also:** [Abilities tab](help:tab-abilities),
[Hermetic Background](help:section-hermetic-background)

### Virtues
<!-- help: section-vf-virtues -->

The character's Virtues, each with its tier (Minor, Major or Free). Virtues
<!-- tui -->
can only be added and deleted, not edited: `a` opens the catalog on its
Virtues.
<!-- /tui -->
<!-- gui -->
can only be added and deleted, not edited: **Add** opens the catalog on
its Virtues.
<!-- /gui -->
A magus's House Virtue is marked Free and counts no points
(Ars Magica Definitive Edition, Chapter 3: Characters, Hermetic Houses).

### Flaws
<!-- help: section-vf-flaws -->

The character's Flaws, each with its tier. Like Virtues, Flaws can only be
<!-- tui -->
added and deleted, not edited: `a` opens the catalog on its Flaws.
<!-- /tui -->
<!-- gui -->
added and deleted, not edited: **Add** opens the catalog on its Flaws.
<!-- /gui -->
The
section title shows the points the Flaws come to.

## Hermetic Magic tab
<!-- help: tab-hermetic -->

A magus's Arts, what they can cast, their raw vis, the spells they know and
<!-- tui -->
their research. Only a magus has this tab. The line at the top names the
magus's Talisman, how far it is opened and its attunements.
<!-- /tui -->
<!-- gui -->
their research. Only a magus has this chapter.
<!-- /gui -->

**You type:** the XP in each Art, the raw vis the magus holds, the spells
they know and their Mastery, and their research goals.

**The app works out:** each Art's score from its XP, the Casting Score for
every Technique and Form, Magic Resistance, Penetration and the Certamen
totals.

**See also:** [Lab Totals tab](help:tab-lab-totals),
[Inventory tab](help:tab-inventory), [Planning tab](help:tab-planning), [How the app handles advancement](help:guide-advancement)

### Magical Arts
<!-- help: section-arts -->

<!-- tui -->
The five Techniques and ten Forms, each with its score and XP. `e` edits
every Art at once:
<!-- /tui -->
<!-- gui -->
The five Techniques and ten Forms, side by side, each with its symbol,
score and XP; clicking an Art shows it in the inspector. The section's
**Edit** button edits every Art at once:
<!-- /gui -->
you type the XP and the app works out the score (Ars
Magica Definitive Edition, Chapter 3: Characters, Advancement Table),
shown beside it as you type, with the total XP the next score needs
(Next at). A fixed bonus from a Virtue, such as Puissant, shows the
score used in brackets.

### Casting Scores
<!-- help: section-casting -->

Worked out, not typed: the Casting Score for every pair of Technique and
Form, from the Arts, Stamina and the aura of the magus's covenant,
<!-- tui -->
with the
lines below it giving Magic Resistance, Penetration and the Certamen totals
(Ars Magica Definitive Edition, Chapter 7: Hermetic Magic).
<!-- /tui -->
<!-- gui -->
drawn as
a grid with the Forms across and the Techniques down; clicking a cell shows
how its score is made up (Ars Magica Definitive Edition, Chapter 7:
Hermetic Magic).
<!-- /gui -->
It changes as
the Arts, Characteristics or covenant change. Virtues and Flaws that change
words and gestures (Mute, Quiet Magic, Deft Form), Magic Resistance (Flawed
Parma Magica), Penetration (Weak Magic) or the Fatigue a spell costs
(Enfeebled, Withstand Casting, Mythic Blood) are counted, and named where
they apply.

### Raw Vis
<!-- help: section-raw-vis-hermetic -->

The pawns of raw vis the magus holds, by Art. This is the same pool as the
Raw Vis section on the [Inventory tab](help:tab-inventory); a change in one
<!-- tui -->
shows in both. [Give](help:give) in More (`m`) gives vis to a covenant, laboratory or
another magus, and both sides' Diaries record it.
<!-- /tui -->
<!-- gui -->
shows in both. **Give**, beside Add, Edit and Delete, gives the chosen
Art's vis to a covenant, laboratory or another magus ([Give](help:give)),
and both sides' Diaries record it.
<!-- /gui -->

### Known Spells
<!-- help: section-known-spells -->

<!-- tui -->
The spells the magus knows, chosen with `a` from the spell catalog and the
saga's own spells. The picker shows the highlighted spell's details under the
list, description included, so you can compare spells before choosing. `e` edits the spell's Mastery, its score and XP and the
Mastery Abilities. The details panel shows the spell and what the magus
casts it at. Share Spell in More (`m`) makes a spell the magus invented
available to the whole saga.
<!-- /tui -->
<!-- gui -->
The spells the magus knows, chosen with **Add** from the spell catalog and
the saga's own spells. The list shows the chosen spell's details beside it,
description included, so you can compare spells before choosing. **Edit**
edits the spell's Mastery, its score and XP and the Mastery Abilities.
Clicking a spell shows it in the inspector, with what the magus casts it
at. The table sorts by any column you click, and the box above it filters
the spells by name. A spell the magus invented has a **Shared** tick in its
Edit form, which makes it available to the whole saga, and the list's
Shared column marks it (✓ once shared, "Not yet" before).
<!-- /gui -->
Once shared, a spell stays shared. The picker offers only spells from books in
<!-- tui -->
play (F3 shows the rest);
<!-- /tui -->
<!-- gui -->
play (**Show everything** lists the rest);
<!-- /gui -->
a spell already known from a book that goes out
of play stays, marked "(not in play)".

### Research Goals
<!-- help: section-research-goals -->

The Breakthroughs the magus is working towards: what it is, whether it is
Minor, Major or Hermetic, its target in points and what reaching it grants.
You type these; the app adds points to a goal when a season of research
towards it is applied (Houses of Hermes: True Lineages, Chapter 1: House
Bonisagus, Original Research).

## Inventory tab
<!-- help: tab-inventory -->

What the character carries and owns: raw vis (magi only), Personal Gear,
<!-- tui -->
Enchanted Devices and Books. The three lists below Raw Vis share one details
panel.
<!-- /tui -->
<!-- gui -->
Enchanted Devices and Books. Clicking a row shows it in the inspector.
<!-- /gui -->

**You type:** each item of gear, each enchanted device and its effects, and
each book.

**The app works out:** the combat totals of a chosen weapon, how a Lab Text
stands for this character, and the load that the Health section turns into
Encumbrance.

**See also:** [Hermetic Magic tab](help:tab-hermetic),
[Health](help:section-char-health)

### Raw Vis
<!-- help: section-raw-vis-inventory -->

The magus's raw vis, by Art: the same pool as Raw Vis on the
[Hermetic Magic tab](help:tab-hermetic), so a change in one shows in both.
<!-- tui -->
[Give](help:give) in More (`m`) gives vis to a covenant, laboratory or another magus.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, gives the chosen Art's vis to a
covenant, laboratory or another magus ([Give](help:give)).
<!-- /gui -->

### Personal Gear
<!-- help: section-inventory -->

<!-- tui -->
The character's Weapons, Armor and Other Items, in one list. `a` asks which
kind first.
<!-- /tui -->
<!-- gui -->
The character's Weapons, Armor and Other Items, each kind in its own table.
**Add** asks which kind first.
<!-- /gui -->
Choosing a weapon shows its Initiative, Attack, Defence and
Damage totals and the character's Soak, worked out from the weapon and the
character (Ars Magica Definitive Edition, Chapter 11: Obstacles). A weapon
typed in by hand rather than chosen from the catalog counts no Combat
Ability.

The title also shows the character's silver, in pounds, when they have
any; type it in the character's details (Silver).
<!-- tui -->
[Give](help:give) in More
hands the chosen gear to another character or the covenant, and **Give
Silver** gives pounds from the purse.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, hands the gear last clicked to
another character or the covenant ([Give](help:give)), and **Give Silver**
gives pounds from the purse.
<!-- /gui -->

### Enchanted Devices
<!-- help: section-char-devices -->

The enchanted devices the character holds, each followed by its effects;
<!-- tui -->
the magus's Talisman is one of them. More (`m`) offers Instill an Effect on
a device that can take another effect, and Use a Charge on a Charged Item.
<!-- /tui -->
<!-- gui -->
the magus's Talisman is one of them. Beside Add, Edit and Delete, the
**Instill** button instills an effect in the chosen device when it can
take another, and **Use Charge** uses a charge of a Charged Item.
<!-- /gui -->

### Books
<!-- help: section-books -->

The books the character owns. Choosing a Lab Text shows how it stands for
this character, for example whether they can read it.

## Planning tab
<!-- help: tab-planning -->

What the character does this season, and what it will give them, before the
season is applied.

**You type:** the season's activity and its details. Lab work is planned on
the laboratory's Planning tab instead.

**The app works out:** the XP and other gains the plan will give, from the
character as they stand now, with any problem with the plan shown in red
(Ars Magica Definitive Edition, Chapter 10: Long-Term Events).

A grog is not planned season by season: the tab sets up the grog's yearly
update instead, applied in Winter.

**See also:** [Planning a season](help:plan-season),
[Advancing a season](help:advance-season),
[A grog's year](help:grog-year), [Diary tab](help:tab-diary), [How to plan and run a season](help:guide-seasons)

### This Season
<!-- help: section-char-season -->

The plan for the current season, named in the title, and what it gives.
<!-- tui -->
`a` or `e` plans the season or changes the plan, and `d` clears the plan
after asking.
<!-- /tui -->
<!-- gui -->
**Plan** plans the season, **Edit** changes the plan, and **Clear** clears
it after asking.
<!-- /gui -->
Some results, such as a die roll, are only settled when the
season is applied. Below the plan it lists what the character carries
from season to season: Labor Points, works in progress, formulas and the
past Ordeals still lowering an Initiation's Target (see
[How to initiate a character into a Mystery](help:guide-initiation)). For
<!-- tui -->
a grog, `e` sets up the yearly update (Grogs, Chapter 5).
<!-- /tui -->
<!-- gui -->
a grog, **Yearly Update** sets up the yearly update (Grogs, Chapter 5).
<!-- /gui -->

## Diary tab
<!-- help: tab-diary -->

<!-- tui -->
A record of the character's seasons, in one list with a details panel.
<!-- /tui -->
<!-- gui -->
A record of the character's seasons. Seasons at the top is a calendar, a
row per year, of what the character did each season; clicking one shows it
in the inspector. The Diary below lists the entries.
<!-- /gui -->

**You type:** entries of your own, with a year, season, activity and notes;
you can also edit or delete any entry.

**The app works out:** an entry for each season applied, for aging and
Warping, and for vis moved, written as they happen.

**See also:** [Planning tab](help:tab-planning),
[Advancing a season](help:advance-season)
