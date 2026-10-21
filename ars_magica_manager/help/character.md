# Character sheet
<!-- help: character -->

<!-- tui -->
The character sheet holds one character of the saga: a magus, companion or
grog. The top panel, with the character's name and Characteristics, stays
on screen above the tabs whichever tab is open. Below it are the numbered
tabs, opened with `1` to `8` (a character who is not a magus has no Hermetic
Magic tab, so the later tabs move up a number); the last, Secrets, is the
storyguide's alone. On a tab with a list, the
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
character who is not a magus has none), Inventory, Planning, Diary,
[Secrets](help:tab-secrets) and, last, Manage. Clicking a row, card, Art or Casting Score shows it in the
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
While there is no portrait the frame shows the House symbol, or for a
hedge wizard their tradition's symbol (the first of their traditions, if
they belong to several); anyone else has a figure of a person. A magus's
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

How much of a character is written down is their detail level: a **Line**
(a name and who they are), a **Sketch** (the statblock play needs, as the
books print their NPCs) or **Full** (the whole sheet). Only a full
character is played: a Line or Sketch character is left out of season
plans, ageing and creation budgets. **Promote** writes one more level down,
and **Demote** keeps one less; nothing is deleted, and the parts a level
doesn't show keep what they hold. Promoting a sketch to Full moves them In
Creation and opens the Creation Worksheet on what the sketch already has.
<!-- tui -->
Both are in More (`m`) on the top panel.
<!-- /tui -->
<!-- gui -->
Both are in the **Manage** chapter.
<!-- /gui -->
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

## Statblock tab
<!-- help: tab-statblock -->

A Line or Sketch character opens here: who they are ("In the Saga"), and
for a sketch their Characteristics, the Arts and Abilities that matter,
their Virtues and Flaws, signature spells, Personality and Reputations.
**Abilities not listed count as 0.** Each part is edited where it lives:
"In the Saga" with the character's Edit, the rest on its own
<!-- tui -->
tab.
<!-- /tui -->
<!-- gui -->
chapter.
<!-- /gui -->
A Line or Sketch character's sheet has no Inventory or Planning, since
they are not played season by season; a Line character has no Abilities,
Virtues and Flaws or Hermetic Magic either.

### Statblock
<!-- help: section-char-statblock; tui -->

The statblock as one block, redrawn whenever one of its parts changes on
another tab.

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
a Supernatural Ability, one is learned through the Virtue that grants it.
Most hedge Arts, and Accelerated Abilities such as the vitkir's runes,
advance on the Art XP table (1 XP for a score of 1); a Difficult Art, such
as Elementalist Fire or the gruagach's Give, advances on the Ability XP
table (Hedge Magic Revised Edition, Chapter 1: Difficult Arts, Accelerated
Abilities). A character who belongs to a tradition sees its Arts and
Abilities in the tradition's own chapter, not here.

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
shown larger, with its engraved lines, in the panel beside the list. The
hedge traditions' Arts and Abilities have marks of their own: each rune
of the Vitkir is its Elder Futhark letter, all cut at one size, and the
gruagachan's are taken from the Pictish symbol stones. So do the
powers, Methods and Arts of the other hedge books, from the faerie rites
and Goetic Arts to the Amazons' Vowels and the Hunters' Arts. An Ability the
app has no mark for shows its category's. The way to the next
score is drawn as a gold line along a dotted rule, ending in a red
lozenge as far as the XP reaches, with the XP over the next total after
it.
<!-- /gui -->

**See also:** [Virtues & Flaws tab](help:tab-vf),
[Planning tab](help:tab-planning), [How the app handles advancement](help:guide-advancement)

## A tradition's chapter
<!-- help: tradition-chapter -->

A character who belongs to a non-Hermetic tradition, such as the folk
witches or the vitkir, has a chapter named after the tradition's magic
(Folk Witch Magic, Rune Magic...), as a magus has Hermetic Magic. It lists
the tradition's Arts and Abilities the character has, grouped by the part
they play: Techniques, Forms, Runes, then the tradition's other Abilities.
These leave the Abilities chapter while the character belongs to the
tradition.

<!-- tui -->
**You type:** `a` adds one of the tradition's Arts or Abilities, `e` sets
its XP and Specialty, and `d` deletes it. More's **Traditions** (`m`, `t`)
on the character chooses the traditions they belong to: only those the
saga offers are listed (see [Traditions Offered](help:section-traditions)).
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one of the tradition's Arts or Abilities,
**Edit** sets its XP and Specialty, and **Delete** deletes it. The
**Traditions** button in the Abilities chapter chooses the traditions the
character belongs to: only those the saga offers are listed (see
[Traditions Offered](help:section-traditions)).
<!-- /gui -->

A magus may belong to a tradition too. A Hermetic society, such as Sol
Invictus or the Priory of Saint Nerius, is open to any magus; a tradition
of House Ex Miscellanea, such as the Tempestaria or the Rustic Magi, to the
House's magi, whose free House Virtues are then the tradition's own: its
Major non-Hermetic Virtue, its Minor Hermetic Virtue and its Major
Hermetic Flaw (Houses of Hermes: Societates, Chapter 5: House Ex
Miscellanea). Its chapter shows beside Hermetic Magic.

Leaving a tradition keeps its Arts and Abilities: they move back to the
Abilities chapter. **The app works out:** each score from its XP, on the
Art table or the Ability table as the tradition's book says (see the
[Abilities tab](help:tab-abilities)), the [Casting](help:tradition-casting)
totals, the [Magical Defenses](help:tradition-defenses), the character's
[Effects and Items](help:tradition-effects), their
[Bound Beings](help:tradition-bonds), the tradition's
[Warping](help:tradition-warping) and [Pools](help:tradition-pools), and
its [Seasons](help:tradition-seasons).

## A tradition's Effects and Items
<!-- help: tradition-effects -->

The spells, charms, rune scripts, rites and powers the character knows of
the tradition, and the items they have made (amulets, chartae, fetishes,
potions, tattoos, wondrous items). Each names the way of casting it uses
(one of the tradition's, in [Casting](help:tradition-casting)), the Arts,
Ability or runes, its level and its Range, Duration and Target.

<!-- tui -->
**You type:** `a` adds one, `e` edits the chosen one, and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one, **Edit** edits the chosen one, and
**Delete** deletes it.
<!-- /gui -->
An item also keeps its charges or doses left, which you count down.

**The app works out:** each one's Casting Score in the covenant's aura and
the die it needs to reach its level ((Casting Score + die) / divisor at
least the level), and the die for a Fatigue level where the tradition
casts up to 10 short; a power whose magnitude is its Ability needs no die;
an item made by a Lab Total shows that Lab Total.

**Not yet:** a season of work making the item or inventing the effect
for you (add it here when the season is done), and the catalogs of each
book's printed spells and charms.

## A tradition's Casting
<!-- help: tradition-casting -->

How the tradition's members work magic, each way as its book gives it,
with the character's Casting Score for everything they can cast in their
covenant's aura. A tradition that pairs a Technique with a Form (the
gruagachan, the learned magicians, the elementalists) shows a grid,
Techniques down and Forms across; one whose powers are Abilities (the folk
witches) lists each with its Characteristic; the vitkir list each rune.
Below each come what the total adds and what it must reach, the Fatigue,
how much vis it can use, and the Penetration.

**The app works out:** each Casting Score as the Arts or Ability + the
Characteristic + any Ability the book adds + the aura's modifier for the
tradition's realm (a Magic tradition loses three times a Divine aura). The
total is (score + die) / divisor: a gruagach's spontaneous spell halves
it, a learned magician's known charm halves it and one cast from a text
divides it by five. Some traditions cast up to 10 short for a Fatigue
level; an Ability's effect must reach its Ease Factor, and counts as a
spell of 5 x its score. Penetration is the total + the Penetration bonus
- the level, as for a magus. A Lab Total (Refining, a vitki's) adds no
die. The dispellings a tradition knows and its group castings (the folk
witches' sabbats) are listed below.

**Not yet:** rolling a casting and the summoning chart. Each charm,
spell or script the character knows is in
[Effects and Items](help:tradition-effects).

## A tradition's Magical Defenses
<!-- help: tradition-defenses -->

The Magical Defenses the character's training gives: one for each of the
tradition's Arts or Abilities they have, against its own kind of effect.
Hedge wizards have no Magic Resistance; these only lessen magic.

**The app works out:** the bonus, a hedge Art's score / 5 (rounded up) or
a Supernatural Ability's score, doubled by Greater Magical Defenses; the
No Magical Defenses Flaw takes them all. Defenses never add up: only the
best one against an effect applies, and none works against an effect of
Personal range. The vitkir and elementalists have none.

## A tradition's Seasons
<!-- help: tradition-seasons -->

What the tradition does with its seasons, with the character's own totals.
**Opening** gives the character's Opening Total as the master, and what it
is set against; **Initiation** lists the tradition's printed Scripts with
the character's Initiation Total as Mystagogue against each one's Ease
Factor, what it gives and its Ordeal; **Advancement** says whether the
tradition's Arts may be practised or studied from vis; and **Seasons of
work** lists the tradition's own seasons with the character's best Lab
Total for each.

**The app works out:** the Opening Total (most are a Lab Total:
Intelligence + an Ability + Arts + the aura; the elementalists' uses their
highest Technique and lowest Form, a vitki's his lowest rune), the
Initiation Totals (Presence + the tradition's Lore + the Script's bonus;
an elementalist's best Organization Lore), and the Lab Totals. The seasons
themselves are planned on This Season (see [Activities
offered](help:plan-season-activities)); an initiation uses Undergo an
Initiation with the Script's bonus.

**Not yet:** what a season of work makes (a potion, a charm, a script)
isn't added for you: add it to [Effects and Items](help:tradition-effects)
when the season is done.

## A tradition's Bound Beings
<!-- help: tradition-bonds -->

The beings bound to the character by the tradition: a folk witch's
familiar, a gruagach's fetch, and any spirit, statue or beast the troupe
binds. Each names the kind of bond (the tradition's, as its book gives
it), the Bestiary creature it is, if the saga has one, and the bonus its
bond adds to the character's totals.

<!-- tui -->
**You type:** `a` adds one, `e` edits the chosen one, and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one, **Edit** edits the chosen one, and
**Delete** deletes it.
<!-- /gui -->
The bonus is typed in: a folk witch's familiar adds its Intelligence + its
Folk Witch Magic Theory to her Lab Totals.

**The app works out:** the bonus, added to the tradition's casting totals
or its Lab Totals (whichever the bond applies to) in
[Casting](help:tradition-casting), [Effects and Items](help:tradition-effects)
and [Seasons](help:tradition-seasons). Below the list, each bond the
tradition's book describes: how it is made and what it gives.

**Not yet:** the season of binding itself (plan it as the tradition's own
work, then add the being here).

## A tradition's Warping
<!-- help: tradition-warping -->

What the tradition's Gifted members suffer from Warping. No hedge
tradition goes into Wizard's Twilight, and none gains Warping Points from
living in a strong magic aura; each has its own response: the
elementalists' Elemental Warping, the folk witches' Witch Moon, the
gruagachan's Transformation, the learned magicians' Intervention and
Abduction, and the vitkir's Nátt-thel. The section gives what sets it off
and the rolls it calls for, with the character's Warping Score (from the
[Aging](help:section-aging) section). A magus, and every member of an Ex
Miscellanea tradition, is a Hermetic magus: Warping and Twilight as for
any magus.

**The app works out:** an elementalist's Personality Traits, one for each
Elementalist Form he holds: the Warping Score + the Form / 5 (rounded up).
From +3 a Trait acts as a Minor Personality Flaw, from +6 a Major one, and
at +10 the storyguide takes over.

**Not yet:** rolling the avoidance and its effects.

## A tradition's Pools
<!-- help: tradition-pools -->

The points the character keeps in each of the tradition's pools, for a
tradition whose members store power (its book says what fills the pool,
what spends it and its cap, shown here). A tradition with no pools has no
such section.

<!-- tui -->
**You type:** `e` sets the points in each pool.
<!-- /tui -->
<!-- gui -->
**You type:** **Edit** sets the points in each pool.
<!-- /gui -->

**Not yet:** filling or spending a pool for you: set the points by hand.

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

**You type:** nothing; you pick each Virtue or Flaw from the catalog, and
choose what it names (Puissant's Ability, Affinity's Art, a Great
Characteristic's Characteristic) from a list.

**The app works out:** the points each side comes to, in the section
titles, coloured by whether the two sides balance (Ars Magica Definitive
Edition, Chapter 4: Virtues and Flaws), and the effects of each one on the
rest of the sheet.

**See also:** [Abilities tab](help:tab-abilities),
[Hermetic Background](help:section-hermetic-background)

### Virtues
<!-- help: section-vf-virtues -->

The character's Virtues, each with its tier (Minor, Major or Free).
<!-- tui -->
`a` opens the catalog on its Virtues. `e` changes what the chosen one
names, such as Puissant Magic Theory to Puissant Finesse; it keeps its
place in the list.
<!-- /tui -->
<!-- gui -->
**Add** opens the catalog on its Virtues. **Edit** changes what the chosen
one names, such as Puissant Magic Theory to Puissant Finesse; it keeps its
place in the list.
<!-- /gui -->
The choices are the ones Add offers, so a second Puissant Magic Theory is
still refused, and a Great Characteristic can only move to a
Characteristic at +3. Changing a Great or Poor Characteristic moves both
scores: Great Intelligence to Great Stamina takes Intelligence down a point
and Stamina up one, and the form says so before you save. A new choice
counts from now on; xp already earned stays where it is. To take a
different Virtue, delete this one and add the other. A Virtue that names
nothing has nothing to change.

A magus's House Virtue is marked Free and counts no points
(Ars Magica Definitive Edition, Chapter 3: Characters, Hermetic Houses).

### Flaws
<!-- help: section-vf-flaws -->

The character's Flaws, each with its tier. Like Virtues, Flaws can be
<!-- tui -->
added, changed and deleted: `a` opens the catalog on its Flaws, and `e`
changes what the chosen one names (Poor Perception to Poor Dexterity).
<!-- /tui -->
<!-- gui -->
added, changed and deleted: **Add** opens the catalog on its Flaws, and
**Edit** changes what the chosen one names (Poor Perception to Poor
Dexterity).
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

**Hybrid magic.** A magus whose magic is also non-Hermetic has it counted
too, and a line for each kind closes the section:

- **Holy Magic** (the Ability, or the Virtue that gives it): Holy Magic
  stands in for Magic Theory in every Lab Total and in the vis he may use;
  a Divine or Magic aura adds its full score, a Faerie aura half, and an
  Infernal aura takes nothing away; living in a Magic or Divine aura gives
  him no Warping (Realms of Power: The Divine, Holy Magic).
- **Chthonic Magic**: a Magic or an Infernal aura adds its full score, and
  living in either gives him no Warping (Realms of Power: The Infernal,
  Chthonic Magic).
- **Hermetic rites** (a Faerie Method and Power): rituals from the faerie
  rite guidelines (Realms of Power: Faerie, Hermetic Rites).
- A Ritual adds his best **Method + Power** of the style's realm instead of
  Artes Liberales + Philosophiae, when that is more.
- **Goetic Arts**: in a Goetic Art's total a magus may use Rego for the Art
  and Vim for the Realm Lore, when they are higher (Realms of Power: The
  Infernal, Goetic Magic).

What can't be worked out (Holy Magic's halved totals from Hermetic texts,
Chthonic Magic's sinful acts, the faerie rite parameters) is written in
that closing line as the books word it.

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
towards it is applied (Ars Magica Definitive Edition, Chapter 8, Arcane
Discovery; Houses of Hermes: True Lineages, Chapter 1: House Bonisagus,
Original Research). A goal's details also say when a failed stabilization
must be tried again, and which spells and enchantments have already given
it a Discovery (each gives one at most).

A new goal may start from an **Integration**: the breakthroughs Ancient
Magic names for folding a lost tradition into Hermetic magic (Canaanite
Magic, Hermetic Rune Magic, Mutable and Awakened Devices, the Grigori
Legacies, the Limit of Vis...), and Hedge Magic's Subtle Opening and Quick
Charged Items. Choosing one fills in its name, kind, points and what it
grants, which you can still change (Ancient Magic, Introduction, The
Breakthrough).

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

What the character does this season and the three after it, a full year,
and what each will give them, before the season is applied.

**You type:** the season's activity and its details. Lab work is planned on
the laboratory's Planning tab instead.

**The app works out:** the XP and other gains the plan will give, with any
problem with the plan shown in red (Ars Magica Definitive Edition, Chapter
10: Long-Term Events). This season is worked out from the character as they
stand now; a season ahead from the character as the seasons planned before
it will leave them (see [Seasons Ahead](help:section-char-ahead)).

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

### Seasons Ahead
<!-- help: section-char-ahead -->

The three seasons after this one, named in the title, each with what is
planned for it or "nothing planned". With This Season above it, a
character can be planned a full year ahead; when the season is advanced,
the next one becomes This Season and another joins the list.
<!-- tui -->
Highlight a season to see its plan and what it will give under the list.
`e` plans it or changes its plan, `a` plans the first season with nothing
planned, and `d` clears the highlighted season's plan after asking.
<!-- /tui -->
<!-- gui -->
Click a season to see its plan and what it will give under the list.
**Edit** plans it or changes its plan, **Plan** plans the first season with
nothing planned, and **Clear** clears the chosen season's plan after asking.
<!-- /gui -->
What a season ahead will give is worked out from the character as the
seasons planned before it will leave them: the app plays the planned
seasons forward on a copy of the saga, so the xp, books read, vis spent
and lab work of the earlier seasons count, and the copy is thrown away.
The details say so under the plan. A season whose die isn't rolled yet
(study from vis, an experiment) counts as gaining nothing, and the seasons
after it say "Counts nothing gained from ...". The year's end (aging, a
grog's year, the covenant's harvests) and the seasons nobody planned are
not counted. Lab work in a season ahead is planned on the laboratory's
Planning tab, as for this season. A grog has no Seasons Ahead: their
yearly update covers the year.

### Calendar
<!-- help: section-char-calendar; tui -->

The character's seasons as a calendar: a line per year, newest first, from
three years ago to the last season planned, with Spring, Summer, Autumn
and Winter across. A season already played shows its Diary entry's
activity; a planned one is in italics, with what it is expected to give
on the line under it ("Ignem 7 (+15 xp)": the score it leaves, "8/15
points", "die not rolled"), worked out as the Seasons Ahead are. The current season is
in bold. The calendar only shows: plan or change a season in This Season
or Seasons Ahead above it.

## Diary tab
<!-- help: tab-diary -->

<!-- tui -->
A record of the character's seasons, in one list with a details panel.
<!-- /tui -->
<!-- gui -->
A record of the character's seasons. Seasons at the top is a calendar, a
row per year, of what the character did each season and plans to do: a
planned season (a dashed outline) also says what it is expected to give,
worked out from the seasons planned before it as for the
[Seasons Ahead](help:section-char-ahead). Clicking one shows it in the
inspector. The Diary below lists the entries.
<!-- /gui -->

**You type:** entries of your own, with a year, season, activity and notes;
you can also edit or delete any entry.

**The app works out:** an entry for each season applied, for aging and
Warping, and for vis moved, written as they happen.

**See also:** [Planning tab](help:tab-planning),
[Advancing a season](help:advance-season)
