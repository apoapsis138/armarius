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

**Office, crown and relic.** Edit also sets the Church office or crown the
Divine protects (Pope 25, a cardinal or legatus a latere 20, a legatus
missus 15, an archbishop, a crowned king or his queen 10) and the Faith of
the one relic the character relies on (10 x its Faith). They give Magic
Resistance, the relic's added to the office's, and the office a fifth of
it to Soak (DE pp. 419-420). Resistances from other sources don't add: the
character has the highest of True Faith's, the office and relic's, and
Strong Angelic Heritage's Divine Might (age / 20, DE p. 109). The sheet
says which it is.
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
reputation, the records they are connected to (see
[Connections](help:section-connections)), age and health.
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

Below Personality Traits and Reputations come the character's
[Connections](help:section-connections): their covenant, the factions they are a member of, what they rule, and any
other record that links to them.

### Personality Traits
<!-- help: section-personality-traits -->

The character's Personality Traits, each a name and a score that you type
(Ars Magica Definitive Edition, Chapter 3: Characters). Binding a familiar
adds a Loyal (Partner) +3 trait to the magus, which you can then change or
delete like any other.

When a trait is rolled, it is a stress die + the trait alone: against 3 for
what average people usually do, 6 for what they do half the time, 9 for
what they usually don't, and 12 for what even people known for the trait
rarely manage. A player changes the scores only between sessions, after
striking rolls or events (DE p. 28).

### Reputations
<!-- help: section-reputations -->

The character's Reputations, each a name and a score that you type
(Ars Magica Definitive Edition, Chapter 3: Characters). A Reputation may also say its type (Hermetic, Local, Noble, Academic,
Ecclesiastical or Infernal) and how far it reaches, both shown in
brackets after its score.

Someone has heard of the character when a stress die + the score reaches
0 in the same village, parish or covenant, 6 in the same town, diocese or
Tribunal, 9 in the county, province or whole Order, and 12 in the country
or the whole Church (DE pp. 28-29). A noteworthy deed before witnesses who
talk starts a Reputation at 1, and each later one is an experience point
in it, as for an Ability: ten deeds take it from 1 to 2 (DE p. 386). Type
the new score when it rises.

Whether a Reputation is good or bad is yours to say, by its sign: type a
bad one with a negative score (Drunkard -2) and a good one with a
positive score. A university exam adds the Good Academic Reputations and
takes off the Bad ones (only academic ones count), and needs a net 1, 2
or 3 for the baccalaureus, magister or doctor, after 3 years, 8 and 10 at
university, counting the exam season (Art & Academe p. 100). The doctor
exam needs the Magister in Artibus Virtue already (DE p. 76) and uses the
faculty's Ability. Disputatio and debate count the highest good one.

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
Twilight, which the app rolls straight away, against the **Aura where it
happened** (blank: where the character lives). **Enter Twilight
willingly** skips the roll to avoid it (DE p. 228). When Winter is applied, the app
makes the yearly aging roll and adds the apparent age, Aging Points,
Decrepitude points and any Longevity Ritual here, and adds the year's
Warping Points from a Longevity Ritual or a strong aura of another realm
(Ars Magica Definitive Edition, Chapter 10: Long-Term Events). **Time in
their home aura** sets how much of it they gain: always (living, working
and sleeping there), half the time (sleeping there but working elsewhere,
or two weeks in and two out), frequent visits (about a quarter of their
time), or living elsewhere, by DE p. 390's table: a level 9 aura gives 4
points a year always, 2 half the time and 1 on frequent visits; one point
every second year comes in even years. A botched Twilight comprehension
adds a step on the time table for each zero, and the steps can reach the
table's row 10, Final Twilight: a magus at Warping 8 who botches with two
zeros is lost (DE p. 228).

With Art & Academe in play, the form also takes a physician's
**Regimen**: its bonus to the Living Conditions the aging roll uses, the
physician (a character with Medicine) and the year it began. It helps
once the character has lived under it a year: +1 from a physician with
Medicine 1, who can keep up to five times his Medicine in clients on it;
+2 from Medicine 4, for up to his Medicine in clients; +3 from Medicine
7, for one client. A physician keeps a single regimen (its level is his
first client's, in the saga's order), only as many clients as it allows
(the first ones), and it needs bloodletting from someone with Chirurgy 3:
the physician, or someone at his covenant. The section says when the
physician's Medicine is too low for the bonus chosen, or why the regimen
gives nothing. A month away, a neglected diet, broken sleep, a disease or
a Twilight loses it: set the year it began again (Art & Academe p. 59).

### Health
<!-- help: section-char-health -->

<!-- tui -->
The left column shows Soak, Encumbrance and the Wound Penalty, worked out
from Stamina, armour, Virtues and the load of the character's Personal Gear,
how far the character moves in a combat round (10 + Quickness -
Encumbrance paces at a walk, twice that hurrying, four times running, DE
p. 395) and what they can carry, lift and drag (a Burden of Strength + 5,
+ 7 and + 12; a Load point is about 7 pounds; a four-footed beast's (clawed or hoofed, not a bird or fish)
Strength counts half again, Grogs pp. 47-48) and how far they can push
themselves in a day on good roads (15 + 2 x Athletics miles on foot, with
Encumbrance taken off Athletics; 30 + 2 x Ride riding, or 20 without
Ride; it costs two Long-Term Fatigue levels, Grogs pp. 51-52), then the
wounds as typed.
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

Wounds and Fatigue take their penalty from every roll and total, the
Casting Score and certamen included, though not from Soak or Recovery
rolls. A wound that isn't an injury (a disease, poison or deprivation), a
wound with stable rolls behind it, bruises and the Recovery Total are
listed under the wounds: **Recovery** is Stamina + the medic's Chirurgy
for an injury or Medicine for the rest (the best among the character's
covenant-mates, named) + the stable rolls' +3s + magical aid + the
laboratory's Health for those who live in one + a familiar's Bronze Cord +
Rapid Convalescence or Fragile Constitution, less an Infernal aura where
they live (Definitive Edition pp. 289, 267, 405; Realms of Power: The
Infernal p. 12). Each season the wounds heal on their own (see
[Recovery](help:recovery-roll)). The Fatigue Level shows how many of its
levels are long-term: those come back a night's rest each, the rest in
minutes; a season clears both.

**Activities while injured** (DE p. 405): a Wound Penalty of -1 or -2
allows travel and study but nothing strenuous, such as spells that cost
Fatigue; -3 to -5 halves travel and halves study for a month or more of
it, and forbids lab and craft work; -6 or worse allows only talking,
eating and moving short distances with help. Doing more than that means a
[Recovery Roll](help:recovery-roll) for the worst wound, which can only
hold or worsen. After a battle, -6 or worse can't travel and -3 or worse
can't keep pace with an army (Lords of Men p. 108). **First aid** (Grogs
p. 59): within a day, Dexterity + Chirurgy + stress die against the
Improvement Ease Factor of the worst wound lets the wounded act one
category better for a day; a botch means an immediate Recovery roll.

<!-- tui -->
More (`m`) on Health offers [Take Harm](help:take-harm) and a
[Recovery Roll](help:recovery-roll).
<!-- /tui -->
<!-- gui -->
**Take Harm** and **Recovery Roll**, beside Health's Edit buttons, harm the
character or roll for their wounds now.
<!-- /gui -->

## Take Harm
<!-- help: take-harm -->

Harm from more than weapons, rolled and then kept in the Diary when you
choose Keep:

- **An injury**: a damage bonus (from the Heat and Corrosion or Impact
  tables, or typed; falling is +1 per two feet, doubled on a hard surface,
  halved on a soft one) + stress die against Soak + stress die, read on
  the Damage Table for the character's Size. Heat and corrosion multiply
  their bonus by how much of the body they cover (a hand x1, a limb x2,
  half the body x3, all of it x4); untick **Armour protects** for boiling
  water and the like (Definitive Edition p. 407).
- **A poison** or **a disease**: a Stamina check (stress die) against its
  Ease Factor, from the Poison table (p. 406), City & Guild's urban
  diseases (pp. 27-28), or typed. Failing it gives the wound named, which
  heals with Medicine. A disease spirit's attack must first pass Magic
  Resistance. With the **Art & Academe medicine** rule option a disease is
  instead its own record (see [Art & Academe's diseases](help:aa-diseases)):
  choose one of the book's (pp. 47-51) or make one from its stage,
  Interval and Ease Factors, and the Disease Avoidance roll (Stamina +
  Living Conditions + Corpus / 5 for a magus + the Wound Penalty + stress
  die) must reach its Stable Ease Factor (the Definitive Edition's
  equals-or-exceeds, DE p. 7: Art & Academe's "exceed" on p. 46 disagrees
  with its own other rolls); a botch catches it a stage worse.
- **Deprivation** of air, water or food for a number of periods (30
  seconds, a day, three days): a Stamina check each period against 3, 1
  more each period; each failure a Fatigue level (long-term for water and
  food), and once unconscious a Light Wound, then each a level worse
  (p. 407).
- **A bruise**, with the Bruises rule option (Lords of Men pp. 131-132): a
  non-lethal blow read on the Damage Table as a bruise. Its penalty works
  as a wound's; it heals within hours, and a Heavy, Incapacitating or
  Fatal one leaves a Light, Medium or Incapacitating wound.

A magus's **Form Bonus** (the Form's score / 5, rounded up) adds to Soak
or to the roll resisting harm of its Form (Definitive Edition pp.
206-209). For an injury or a bruise, choose **What it comes from**: fire
or heat and cold or ice (Ignem), an animal's claws, teeth or horns
(Animal), a human's unarmed blow (Corpus), a wooden weapon or timber
(Herbam), a metal or stone weapon or stone (Terram), a jet or wave of
water (Aquam), lightning or other weather (Auram), or one's own
spell-casting gone wrong (Vim); the tables' entries choose their own
unless you choose otherwise (corrosion and the jug have none). For a
poison, the **Kind of poison**: an animal's venom (Animal), a herbal
poison (Herbam) or a mineral one (Terram); the Poison table's choose
theirs. A disease's Stamina check adds Corpus (never to aging),
deprivation of air Auram, of water Aquam and of food Herbam; tick
**Drowning** for air lost under water, where Auram or Aquam counts. The
bonuses never stack: where two apply, only the higher counts, and the
result names the one used. Vim's bonus to avoiding Twilight is part of
the Twilight roll.

## Recovery Roll
<!-- help: recovery-roll -->

Wounds heal season by season, when the season is advanced: a Light wound
rolls weekly, a Medium one monthly, a Heavy one once a season, each
against its Ease Factors (Light 4 and 10, Medium 6 and 12, Heavy 9 and
15). At or over the higher, the wound improves a level; at or over the
lower, it holds and gains +3 to its later rolls; below, it worsens. An
Incapacitating wound rolls twice a day: 0 or less dies, 9 or more makes
it Heavy, anything else worse, -1 to later rolls (Definitive Edition
p. 405). The rolls go into the Diary.

**Recovery Roll** rolls once for each wound now, or for the worst one only
(the roll for doing more than the wounds allow, which can only hold or
worsen), and sets the **magical aid** every Recovery roll adds: a
Zenodochium's +9 (Against the Dark p. 98) or a Purification of the
Festering Wound. It rolls each disease once too. Keep applies the rolls.

## End of Session
<!-- help: end-of-session -->

<!-- tui -->
More (`m`) on [Reputations](help:section-reputations) offers **End of
Session**:
<!-- /tui -->
<!-- gui -->
**End of Session**, beside Reputations' buttons, opens a form for
<!-- /gui -->
what a session of play gave the character. If they were played for a good
part of it and contributed, each award ticked is a Confidence Point:
achieving a personal goal, contributing to a group goal, success in a
difficult task (once a session), entertaining roleplaying, and a bonus the
storyguide thinks deserved (once a session). Two or three a session is
typical. The Confidence Score itself rises only after years-long events,
so type that by hand (DE p. 29).

Each Reputation has a box for the noteworthy deeds done before witnesses
who will talk. Each deed is an experience point in it, as for an Ability:
ten deeds take a Reputation from 1 to 2, and a bad one grows in the same
way. A new Reputation starts at 1 with Add on Reputations. A bad
Reputation is replaced only by starting a new one (DE p. 386). The Diary
records the session.

## Command the Beast
<!-- help: command-beast -->

On a tamed animal's sheet,
<!-- tui -->
More (`m`) on its Personality Traits
<!-- /tui -->
<!-- gui -->
**Command the Beast** beside its Personality Traits
<!-- /gui -->
rolls a command: who gives it, with Animal Handling (Ride for a mount,
Magic Lore for a tamed elemental), and the task. The roll is Presence +
that Ability + a stress die against the task's Ease Factor: none for
something it has done many times, 6 for an unusual or stressful one, 9
for a long or new one, 12 for one it fears, 15 for a suicidal one. A
feared task also asks a Loyalty test (its Loyal trait + a stress die)
against 6 when it has no Confidence Score, and a suicidal one against 9
always. A botch may make it flee, do the wrong thing or turn on its
master (DE p. 386).

A tamed animal played season by season (an animal grog has its yearly
update instead) learns Abilities from anyone with Animal Handling, by Be
trained: one it doesn't have yet asks a Loyalty test against 6 at the
season's end, or the season is wasted (DE p. 385). In a fight, a group of
tamed animals is led by its leader's Animal Handling, not his Leadership
(DE p. 385).

## Constant Effects
<!-- help: section-char-constant-effects -->

The supernatural effects the character is under all the time, or at least
half of it: a spell kept up on them, an enchanted ring that lets them fly.
Each gives a Warping Point a year, whatever its power or caster, and a
powerful one (sixth magnitude or more) neither cast by them nor designed
for them gives one more each season, and one when it begins: adding such
an effect adds that first point at once. The app adds the year's points
each Winter with the rest of their Warping, each counting as its realm for
Susceptibility to Warping (DE pp. 390-391).

Don't list a Longevity Ritual (the app counts it already), Parma Magica,
the Aegis of the Hearth or a familiar's bond (they don't warp), or an
effect on something they live in rather than on them, such as a flying
castle.
<!-- tui -->
`a` adds one, `e` edits the chosen one and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the row last clicked.
<!-- /gui -->
**The Effect** at the foot of its form says what it will give.

## Place Aging Points
<!-- help: aging-due -->

An aging roll of 10-12 gives an Aging Point in any Characteristic, and
13 or 22+ enough to reach the next Decrepitude in any Characteristics: the
player chooses where they go (DE p. 392). Their Decrepitude counts at once
(the Crisis is rolled with it), and each is offered first in the
Characteristic the roll suggests, the highest, with a choice for each
point, so several can be spread over different Characteristics. A Crisis
is rolled with the Decrepitude the points bring, whichever Characteristics
take them; place them before the survival roll, since one in Stamina may
lower it. A character who survives a
disease's Crisis gains an Aging Point in a fitting Characteristic, the
storyguide's choice (Art & Academe p. 47).
Until they are placed, the Aging section lists them. Advance Season asks for
each one before it plays the next season (Cancel leaves the date where it
is). It is also on the Aging section:
<!-- tui -->
More (`m`), **Place Aging Points**.
<!-- /tui -->
<!-- gui -->
**Place Aging Points** beside its Edit.
<!-- /gui -->
Each point counts toward Decrepitude, and once a Characteristic's Aging
Points pass its score it falls by one, as for an aging roll.

An Aging Crisis takes the following season to recover from, except for an
Unaging character, whom a Crisis that can't kill doesn't harm (DE p. 114);
a leper also takes a Heavy Wound with every Crisis (DE p. 135). The Aging
section warns at Decrepitude 4 (extremely frail: a long journey, a fight
or other stressful activity means a roll on the Crisis Table; not for the
Unaging) and 5 (bedridden and dying, DE p. 392).

## Art & Academe's diseases
<!-- help: aa-diseases -->

With the **Art & Academe medicine** rule option (Saga Settings, with Art
& Academe in play) a disease is not a wound but its own record, listed
under the wounds in Health with its stage, Severity, penalty, Interval and
Ease Factors (Art & Academe pp. 45-51):

- **Stages** Minor, Serious, Major and Critical give -1, -3, -5 and no
  action at all; a disease that gives Flaws instead (the falling evil,
  phthisis, suffusio, worms) has no penalty. The penalty adds to the Wound
  Penalty everywhere but the disease's own rolls. Each stage moves its
  Severity 3.
- **Recovery** at the end of each Interval, played out when the season is
  advanced: Stamina + the physician's Medicine + Corpus / 5 (a magus) +
  the Wound Penalty + Recovery Modifiers + magical aid + the +3s of stable
  rolls + stress die. Below the Stable Ease Factor it worsens a stage; at
  or over it, +3 to the next roll; at or over the Improvement Ease Factor
  it improves a stage, and a Minor one is cured. A lifelong one never
  changes.
- **Crisis**: a Critical disease rolls twice a day; 0 or less dies, at or
  over the Stable Ease Factor it eases to Major, anything else -1 to later
  rolls (p. 47). The survivor gains an Aging Point in a Characteristic the
  storyguide chooses: it waits on the Aging section until placed (see
  [Place Aging Points](help:aging-due)).
- **Special diseases** carry their effects as notes (the falling evil's
  convulsions, gangrene's wound that can't heal, the consumptive tumor's new
  tumors, suffusio's blindness, leprosy's Flaw, phthisis' Enfeebled,
  pneumonia's Winded, quinsy's Afflicted Tongue and Mute, scrofula's
  Disfigured, worms, smallpox, phimosis and Saint Anthony's fire): the
  Flaws and choices they bring are yours to add.
- **The physician** is the covenant-mate with the most Medicine. His
  Medicine counts only when his Prognosis Total (Intelligence + Medicine +
  the patient's Living Conditions + an apothecary's Profession:
  Apothecary and a chirurgeon's Chirurgy, at most 3 each) is over the
  Severity (p. 58).
- **Recovery Modifiers** are ticked on Edit Wounds: poor or wealthy
  living, a peasant's or a noble's diet, being routinely active, and no
  medicinal herbs (-3, less an apothecary's Profession: Apothecary). Each
  one also adds a botch die, to wound rolls too, and a disease's penalty
  slows a wound's healing (p. 54). Edit Wounds also clears a disease cured
  by magic, a saint or a surgeon.

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
The details of **Magic Sensitivity**, **Second Sight** and **Sense
Holiness and Unholiness** list the Ease Factors of what each senses
(Definitive Edition pp. 168-170), and Magic Sensitivity's score comes off
the magus's Magic Resistance.

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

With Art & Academe in play, a character can dispute with another
(see [Disputatio](help:disputatio)).

**See also:** [Virtues & Flaws tab](help:tab-vf),
[Planning tab](help:tab-planning), [How the app handles advancement](help:guide-advancement)

## Disputatio
<!-- help: disputatio -->

<!-- tui -->
More (`m`) > **Disputatio**, on a character's sheet with Art & Academe in
play, stages a schoolmen's debate with another character.
<!-- /tui -->
<!-- gui -->
**Disputatio**, in the Abilities chapter of a character's page with Art &
Academe in play, stages a schoolmen's debate with another character.
<!-- /gui -->
Choose who they dispute with, whether they are the **Opponent** (who
states first) or the **Respondent**, the **Subject** (Artes Liberales,
Philosophiae, Theology or Civil and Canon Law: each side uses its score in
it), the **Kind**, the number of the judge's **Questions** (usually 7, 9
or 12) and any Ease Factor the judge sets for the statements (6 among
students, 9 for baccalaureates, 12 for a candidate's examination). The
line above Dispute shows each side's totals before the die:

- **Attack**: Communication + the subject's Ability.
- **Defence**: Perception + the Ability.
- **Weakening**: Intelligence + how far the Attack beat the Defence.
- **Resistance**: Presence + the highest Academic Reputation.

Each question is an exchange: the opponent states and the respondent
replies, then the respondent states and the opponent replies. A statement
that beats the reply costs the other side a symbolic Fatigue level for
every 5 points (or part of 5) its Weakening beats their Resistance, with
the usual penalties; five lose the disputatio, and otherwise the side that
lost fewer wins when the questions run out. **Dispute** rolls it all and
shows each exchange; **Keep** writes it in both characters' Diaries.
Afterwards each rolls Stamina + a stress die against the number of
questions: a failure costs a real Long-Term Fatigue level, and a botch
one more for each 0, which Keep takes off their Fatigue.

The winner of an epideictic or deliberative disputatio gains an
experience point toward a Good Academic Reputation, or gives the loser
one toward a Bad one (once a season at most), which the Diary notes for
you to add. The winner of a forensic one proves the case.

Virtues and Flaws count: Afflicted Tongue -2 and Incomprehensible -6 to
Attack, Good Teacher +3 in a deliberative disputatio and Inspirational +3
in an epideictic one, Short Attention Span -3 to Defence, Piercing Gaze
+3 to Weakening, Strong-Willed +3 to Resistance, Aristotelian Training +1
to every total, Poor Disputer -3 to each roll, Clear Thinker easing the
Fatigue penalties by one, and Enfeebled -1 a question after the first.
Before a crowd, **Before a crowd** takes 3 from each roll of a Gifted
disputer (not a Gentle Gift). Academic Concentration and Aristotelian
Training count for Artes Liberales as logic and rhetoric (Art & Academe,
Chapter Eight: Universities).

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

### Powers
<!-- help: section-char-powers -->

The supernatural powers the character's Virtues grant, under the Virtues
and Flaws. Each is like a Hermetic spell of its level, with Penetration
bought level for level (DE pp. 81-106):

- **Greater Power** (Major): 50 levels a Virtue, one power each;
  Initiative Quickness - magnitude / 2; a Fatigue level up to level 50,
  two to 100.
- **Lesser Power** (Minor): 25 levels a Virtue, shared among powers;
  Initiative Quickness - 2 x magnitude; a Fatigue level for each 25
  levels.
- **Personal Power** (Minor): 25 levels a Virtue, for a power of Range
  Personal or a constant one; Initiative as a Greater Power.
- **Ritual Power** (Major): 25 levels a Virtue; Initiative as a Lesser
  Power, its Fatigue too, and a Confidence Point a magnitude.
- **Focus Power** (Major): 25 points a Virtue, 2 a level of its greatest
  effect and 1 a point of Penetration, for any effect in its narrow field;
  Initiative Quickness - that magnitude; a Fatigue level for each 25
  levels.

Each row shows the power's Initiative, Fatigue and Penetration. Under the
list, each Virtue's levels used of those it gives, and in red what breaks
its rules: levels beyond them, a power with no Virtue for it, more Greater
Powers than Greater Power Virtues, a Personal Power neither Personal nor
constant. Adding or editing a power, **The Power** at the foot of the
form says what it costs and what its Virtue has left.
<!-- tui -->
`a` adds a power, `e` edits the chosen one and `d` deletes it; choosing
one shows it in the panel below.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the powers; click one to read it
in full.
<!-- /gui -->

## Hermetic Magic tab
<!-- help: tab-hermetic -->

A magus's Arts, what they can cast, their raw vis, the spells they know and
<!-- tui -->
their research goals on the [Research tab](help:tab-research). Only a magus has this tab. The line at the top names the
magus's Talisman, how far it is opened and its attunements.
<!-- /tui -->
<!-- gui -->
their research. Only a magus has this chapter.
<!-- /gui -->

**You type:** the XP in each Art, the raw vis the magus holds, and the
spells they know and their Mastery.

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
words and gestures (Mute, Quiet Magic, Deft Form, Afflicted Tongue's -2 to
a spell spoken aloud), a Divine aura (Susceptibility to Divine Power
doubles its penalty and its botch dice), Magic Resistance (Flawed
Parma Magica), Penetration (Weak Magic) or the Fatigue a spell costs
(Enfeebled, Withstand Casting, Mythic Blood) are counted, and named where
they apply.

**Virtues that count only sometimes.** The app works out the scores but
doesn't play a cast out, so a Virtue or Flaw that counts only in its
circumstance is named in a "When they apply" line under the scores:
Special Circumstances (+3), Potent Magic (+3, or +6 Major, in its field),
Hermetic Geometry (+3 for a circle or line), Cyclic Magic (+3 or -3 in its
time), Corrupted Arts and Spells (+3 selfish, -3 selfless), Blood Haze (-10
to Formulaic magic in a fight), Environmental Magic Condition and
Short-Ranged Magic (the total halved), Life Boost (+5 a Fatigue level spent)
and Spell Improvisation (a similar spell's magnitude). Diedne Magic's
Spontaneous casting gets a line of its own. A Ritual's vis on the Known
Spells lines counts Mercurian Magic (half, at least one pawn) and Waster of
Vis (a third more); with Rigid Magic it says no Ritual can be cast (Ars
Magica Definitive Edition, Chapter Four: Virtues and Flaws). Magical
Focus, Deleterious Circumstances and Mystical Choreography are named there
too, as are a Heartbeast's -15 in animal form and Verditius Magic's casting
tools.

The other casting Virtues and Flaws get a line each there too, with their
page (DE pp. 70-145): Boosted Magic, Flexible Formulaic Magic, Atlantean
Magic's Water-way, Storm and Body-of-water, Enduring and Short-Lived Magic's
durations, Exotic Casting, Faerie-Raised Magic (which includes Spell
Improvisation), Harnessed and Tethered Magic, Life-Linked Spontaneous Magic,
Imbued with the Spirit of (Form), Painful Magic and Slow Caster. Clumsy
Magic and Inconstant Magic each take 3 off the Aiming line's Finesse; and
with Incompatible Arts (its Arts typed as "Intellego Herbam, InAn"), a
known spell using a pair it rules out, even as a requisite, says it can't
be cast. In a fight, Cast a Spell applies Incompatible Arts, Painful
Magic's level of pain and Life-Linked Spontaneous Magic's extra Fatigue.

**Spontaneous levels.** A Spontaneous spell uses its own Casting Score,
without the Virtues that count only for Formulaic spells (Method Caster's
+3, Poor Formulaic Magic's -5), and a Deficiency halves the total. When
that makes the levels differ from the grid's score / 5, a second grid gives
the level each pair reaches without Fatigue (DE pp. 98, 125, 141, 214).
Method Caster's +3 is lost with anything but firm words and bold gestures,
and a Deficiency counts when its Art is a requisite (DE pp. 98, 312).
These change it too, and the second grid's heading says how:
**Ceremonial Spontaneous Magic** casts Spontaneous spells only
ceremonially, adding Artes Liberales + Philosophiae, a magnitude a quarter
of an hour (p. 122); **Unstructured Caster** casts Formulaic spells as
Rituals, with Artes Liberales + Philosophiae and their vis (p. 149);
**Weak Spontaneous Magic** always divides by 5 and can't exert (p. 153);
**Difficult Spontaneous Magic** only exerts, dividing by 2 for a Fatigue
level, so the grid shows a dash (p. 126), and the two together allow no
Spontaneous magic; **Diedne Magic** may divide by 2 with a stress die
without Fatigue, or exert with the lowest Art doubled (p. 76). Spell
Improvisation depends on the spell, so it stays a reminder.

**Casting options** (DE pp. 215-218, 223, 260), each a line under the
scores with the magus's own figures: fast casting (speed Quickness +
Finesse + stress die against the foe's Initiative, +3 with Fast Caster,
-6 for each spell after the first; the score -10, +2 botch dice, no vis;
knowing an attacking spell's Form takes Perception + Awareness + die
against 15 - its magnitude); ceremonial casting (+
Artes Liberales + Philosophiae and props +1 to +5 instead of words and
gestures, 15 minutes a magnitude, 3 in a laboratory; it needs experience in
one of the two); Concentration (Stamina + Concentration, with three times
the Wound Penalty and the Fatigue penalty; a failure ends the spell and adds
a botch die); aiming (Perception + Finesse, less the Wound and Fatigue
penalties, +6 for each size step past a basic Individual); and a talisman's attunements, best first,
of which the best that applies adds to the score while he touches it.

**A known spell's lines** count the Golden Cord of the magus's bound
familiar, which takes its score off the botch dice but never below one
(DE pp. 227, 267), and say that a mastered spell has no botch dice when
calm. Extra pawns of vis on a Ritual still add +2 each, and each Art's
pawns are limited to its score (DE p. 216). A Ritual's Fatigue past
unconsciousness becomes a wound: one level more is Light, two Medium, three
Heavy, four Incapacitating (DE p. 213). The spell's **Mastery** special
abilities, typed on its Mastery as Quiet Casting, Still Casting, Fast
Casting, Ceremonial Casting, Penetration, Magic Resistance, Imperturbable
Casting, Multiple Casting, Precise Casting or Quick Casting, are counted:
Quiet and Still Casting in the score, the rest in a Mastery line (DE pp.
225-226).

**Certamen.** A Tremere's Minor Magical Focus in certamen doubles the
lower of the two Arts (DE p. 233), and a Deficient Art halves the total it
is in.

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
- **Faerie Magic** (House Merinita's Virtue, or its Ability): a Faerie
  aura adds its full score as a Magic one does, neither adds botch dice,
  and living in either gives him no Warping (Definitive Edition p. 236).
  Finishing Touches checks that a Merinita with no faerie Virtue or Flaw
  starts with the Warping Point his parens gave him.
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

## Research tab
<!-- help: tab-research -->

A magus's Arcane Discovery (what Houses of Hermes: True Lineages calls
original research): the goals they are working towards and every season
spent on them (Ars Magica Definitive Edition, Chapter 8,
Experimentation and Arcane Discovery).
<!-- tui -->
Only a magus has this tab. Choosing a goal shows where it stands and the
odds of its next season; choosing a season of the log shows its roll on
the Extraordinary Results chart.
<!-- /tui -->
<!-- gui -->
Only a magus has this chapter. Each goal is a card with the road of its
research drawn under it: the steps behind it filled in green, the one it
is on ringed in red. Clicking a goal shows it in the inspector with the
odds of its next season. Choosing a season of the log draws its roll on
the Extraordinary Results chart below the log, the band it landed in
filled in.
<!-- /gui -->

**You type:** the research goals, and, for a secret target, the points the
storyguide sets.

**The app works out:** each season's roll, any move of it toward a
Discovery, the points a stabilized Discovery adds, and the chances of the
next season.

**See also:** [Hermetic Magic tab](help:tab-hermetic),
[Experimenting](help:guide-lab-planning-experiment)

### Research Goals
<!-- help: section-research-goals -->

The Breakthroughs the magus is working towards: what it is, whether it is
Minor, Major or Hermetic, its target in points (or only the points gained,
when the storyguide keeps the target secret) and what reaching it grants.
You type these; the app adds points to a goal when a season of research
towards it is applied (Ars Magica Definitive Edition, Chapter 8, Arcane
Discovery; Houses of Hermes: True Lineages, Chapter 1: House Bonisagus,
Original Research). A goal's details also say when a failed stabilization
must be tried again, and which spells and enchantments have already given
it a Discovery (each gives one at most). They also show where the goal
stands, step by step (Goal agreed, Seek, Discovery, Stabilize,
Breakthrough, Spread), and the odds of its next season: the chance of a
Discovery at each risk the magus's Magic Theory allows, or, with a
Discovery waiting, the chance that stabilizing it succeeds.

A new goal may start from an **Integration**: the breakthroughs Ancient
Magic names for folding a lost tradition into Hermetic magic (Canaanite
Magic, Hermetic Rune Magic, Mutable and Awakened Devices, the Grigori
Legacies, the Limit of Vis, the Event Duration and Unlimited Range...),
Hedge Magic's Subtle Opening and Quick Charged Items, and True Lineages'
discoveries of House Bonisagus (the six Parma Magica folds of the Arma
Magica, Parmulae, Figurine Magic and Realm-aligned spells). Choosing one
fills in its name, kind, points and what it grants, which you can still
change (Ancient Magic, Introduction, The Breakthrough).

A goal that grants **a new Range, Duration or Target** names it as
"Range: Horizon (as Sight)": its kind, its name, and the standard one it
costs as (add +n inside the brackets for more magnitudes); one the app
already knows, such as Duration: 19 Years, needs only its name. Once the
goal is reached, Invent Spell offers it to the magus (see
[Which Ranges, Durations and Targets](help:invent-spell-parameters)).

### Research Log
<!-- help: section-research-log -->

Every season spent on any goal, newest first: seeking a Discovery,
stabilizing one, or studying a source for an insight. Each row shows the
season, the goal, the work, the stress die, the roll (the die plus the
risk), any move of it, and what came of it. The app writes these when a
season is applied; there is nothing to type. Choosing a row shows the
chart with the roll's band marked, the botch dice a 0 rolled, and the
points and Warping it gave.

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

A one-handed weapon is fought with the best shield the character
carries, and the two add together (DE p. 393); the totals name the
shield. Every weapon takes one but a Great Weapon (two-handed) and a bow
(it needs both hands), which is the app's reading: the book doesn't list
them. The weapon's and the shield's minimum Strength are checked
separately (DE p. 400). **Defence against missiles** counts the Combat Ability and the
carried shield only, not the weapon (DE p. 395). On foot a lance's totals
are a Long Spear's, with Great Weapon (DE pp. 400-401). A weapon or shield
whose minimum Strength is above the character's is flagged (DE p. 400), a
weapon whose Combat Ability the character lacks is used untrained with
three more botch dice, and a crossbow's Damage adds no Strength (Lords of
Men p. 138). When a botch or an odd use may break the weapon, the totals
give its stress check: a stress die + its Combat Ability and how well it
is made (-1 Shoddy, +1 Superior, +3 Excellent) against 15 (City & Guild p.
77). The optional Clash of Weapons, when an Attack Total exactly equals a
Defence Total, is a lower check: stress die + the Combat Ability against 9,
or 15 for an improvised weapon (Lords of Men p. 138). The totals also give
the weapon's damage types (crushing, piercing, slashing) and damage levels
from Lords of Men's tables (pp. 137-138): 2 for most, 1 for the bludgeon,
club, spear, lance, round shield, whip, farm implement, long spear and
sling, one fewer for Shoddy and one or two more for Superior or Excellent,
as City & Guild's base levels move. Each failure costs a level, a botch one
more per botch, and with none left it is broken; a standard item is mended in a season, a Superior
or Excellent one by a craftsman with Craft twice its bonus, for a Labor
Point a level (City & Guild pp. 77-79).

**Made** on a weapon or armour: a Shoddy item is destroyed the first time
it fails a stress check; a Superior weapon has +1 Attack, a Superior shield
+1 Defence and Superior armour +1 Protection; an Excellent item has its
**Excellent bonus** (+2 or more), on a weapon to Attack and Defence both
(City & Guild pp. 67-69, as Lords of Men p. 136 sums them up). A weapon not
**Carried** is kept elsewhere: its Load doesn't count and a shield left
behind isn't fought with. Only the armour worn counts toward Load. An
Other Item can name an Ability it **Helps** and how much: minor help takes
1 off the Ease Factor, major help 3, one item a roll (Grogs p. 47).

A specialty in the Combat Ability that names the weapon ("pole axe" for a
Pole Axe, the weapon's own name or its catalog name) adds 1 to Attack and
Defence. Virtues and Flaws count too, and a **Counted** line names each:
Lame (-1 to Initiative, Attack and Defence, -3 Dodging), Missing Eye (-1
to a melee Attack, -3 with a missile), Hobbled (-6), Poor Eyesight (-3
Attack and Defence), Slow Reflexes (-3 Initiative) and Primitive Equipment
(-1 Attack and Defence with a weapon that isn't Inexpensive; -1 Initiative
and Protection in such armour). A natural weapon's Qualities and
Inferiorities (Improved or Reduced Attack, Defense, Damage, Initiative)
count for the weapon named when they are taken; Improved Damage takes the
bonus nominated for the fight.

A character with Ride also gets a **Mounted** line: on a trained
warhorse, Ride (at most +3) adds to Attack and Defence with a melee
weapon, and to Defence alone with a missile weapon (DE p. 397, which
Lords of Men pp. 126-127 expands: the Attack bonus is for melee only).
Shooting from a moving horse costs -1 at a walk or trot, -3 at a canter
and -6 at a gallop, and an untrained mount gives no bonus at all; those
are the storyguide's to apply. A charge
with a melee weapon adds the Combat Ability to the Attack again, at the
cost of a Fatigue level the horse spends. A lance says that it breaks
on a charge that hits.

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
a device that can take another effect, Use a Charge on a Charged Item, and
Use an Effect on a finished effect of an invested device or lesser
enchantment.
<!-- /tui -->
<!-- gui -->
the magus's Talisman is one of them. Beside Add, Edit and Delete, the
**Instill** button instills an effect in the chosen device when it can
take another, **Use Charge** uses a charge of a Charged Item, and **Use**
uses a finished effect once.
<!-- /gui -->
Using an effect shows its Initiative (Quickness + stress die, +3 with a
Fast Trigger), its Penetration (0 unless enchanted with more) and how many
of its uses a day are spent (DE pp. 257, 259); in a fight, Next Blow's **Use
a device** plays it.

A device the character has by a Virtue says so in its **Had by a Virtue**:
Minor Enchantments (25 levels a Virtue, no power over level 30), a
magus's Masterpiece (one lesser enchantment, made within his Lab Totals,
its vis his parens's) or a Redcap's devices (50 levels at Gauntlet,
uses a day included) (DE pp. 97-98, 105). The Powers section and the
creation review say in red when they go past these.

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
from season to season: Labor Points (and what the Improve wealth or status
season costs to move up a step: 120 from Poor, 360 from average, 1,080 from
Wealthy, City & Guild p. 38), works in progress, formulas and the
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
