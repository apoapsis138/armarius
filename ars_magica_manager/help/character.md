# Character sheet
<!-- help: character -->

<!-- tui -->
The character sheet holds one character of the saga: a magus, companion or
grog. The top panel, with the name and Characteristics, stays on screen
above the tabs. Below it are the numbered tabs, opened with `1` to `8`. A
character who isn't a magus has no Hermetic Magic tab, so the later tabs
move up a number. The last tab, Secrets, is the storyguide's alone. On a
tab with a list, the details panel at the bottom shows the chosen row,
including the rules text of a Virtue, Flaw, Ability or spell.

A new character starts In Creation. The button beside Edit in the top
panel shows which mode the character is in. Clicking it, or choosing In
Creation / In Play from More (`m`) with the top panel focused, moves the
character between the two after asking. While the character is In
Creation, More also offers the Creation Worksheet, which walks through the
creation steps. The button beside the mode opens it too.
<!-- /tui -->
<!-- gui -->
The character sheet holds one character of the saga: a magus, companion or
grog. The header shows the name, Confidence, Warping, Decrepitude and how
the character is faring. It and the Characteristic cards under it stay on
the page whichever chapter is open. The rail on the left lists the
chapters:

- Description
- Abilities
- Virtues & Flaws
- Hermetic Magic, for a magus only
- Inventory
- Planning
- Diary
- [Secrets](help:tab-secrets)
- Manage, last

Clicking a row, card, Art or Casting Score shows it in the inspector on the
right, including the rules text of a Virtue, Flaw, Ability or spell.

A new character starts In Creation. The header shows the mode: In Creation
(a quill) or In Play (a seal). Clicking it moves the character between the
two after asking. While the character is In Creation, the sheet is drawn
on ruled drafting vellum, and **Worksheet** under the mode opens the
Creation Worksheet, which walks through the creation steps.
<!-- /gui -->

<!-- gui -->
The frame beside the name holds the character's portrait. Click it to
choose a picture from anywhere on the computer, and click again to change
or remove it. The app keeps a copy in the save folder's `portraits`
folder, so moving or deleting the original doesn't lose it.

With no portrait, the frame shows the House symbol. A hedge wizard has
their tradition's symbol instead, the first of their traditions if they
belong to several, and anyone else a figure of a person. The same picture,
the portrait first, marks the character wherever they appear:

- their card on The Troupe
- a covenant's People, and the Unassigned Characters
- the button naming a laboratory's owner

A magus's **Sanctum** button opens their laboratory below their sheet, so
the trail leads back to them. While they have no laboratory it reads **New
Sanctum** and creates one that's theirs.
<!-- /gui -->

**See also:** [How the app handles advancement](help:guide-advancement), [How to plan and run a season](help:guide-seasons), [How to create a character, covenant or laboratory](help:guide-creation)

### Character info
<!-- help: section-char-info -->

<!-- tui -->
The top panel names the character. You type the Setting, Covenant, Type,
Confidence Score and Confidence Points, the Size, and for a magus the
Assigned Laboratory. The True Faith Score and Faith Points show only for a
character who can have them.
<!-- /tui -->
<!-- gui -->
The header names the character. Its **Edit** button edits the Setting,
Covenant, Type, Confidence Score and Confidence Points, the Size, and for a
magus the Assigned Laboratory. The True Faith Score and Faith Points show
only for a character who can have them. At a Glance shows most of these
(see [Description](help:tab-description)).

**Office, crown and relic.** Edit also sets the Church office or crown the
Divine protects, and the Faith of the one relic the character relies on.
Each office gives Magic Resistance:

- Pope 25
- a cardinal or legatus a latere 20
- a legatus missus 15
- an archbishop, a crowned king or his queen 10

The relic adds 10 x its Faith to the office's. The office also gives a
fifth of it to Soak (DE pp. 419-420). Resistances from other sources don't
add. The character has the highest of True Faith's, the office and
relic's, and Strong Angelic Heritage's Divine Might (age / 20, DE p. 109),
and the sheet says which it is.

Realms of Power: The Divine p. 43 lists the leaders of other faiths too:

- a Greek patriarch 20, the head of another eastern church 25
- a caliph or Shi'i imam 25, a chief qadi or mufti 20, a senior qadi or
  mufti 10, an invested sultan 10
- the exilarch 25, a chief rabbi 20, a senior rabbi 10

Metropolitans count as Archbishop, and crowned kings of any faith as King
(crowned).
<!-- /gui -->

The app works out the Age from Year Born, in Biographical Detail, and the
saga's current year. It shows the current year and season dimmed, because
they belong to the saga. Size includes any Virtue that changes it (DE,
Chapter 3: Characters).

Only a character with the True Faith Virtue has a True Faith Score. One
made with a Score of 2 or more is a Mythic Companion, and the form warns
about it only while the character is In Creation (Realms of Power: The
Divine p. 57). Faith can also be won in play, as the climax of a quest, a
pilgrimage or a test of faith (p. 58). Raise the Score or the Faith Points
on Edit while the character is In Play. The app writes "Faith won in play"
in the Diary, and adds the True Faith Virtue if the character had none.
Miracles aren't worked out.

<!-- tui -->
With the top panel focused, `d` deletes the character after saying what
happens to what they own. More (`m`) offers Export, which writes the
character to a file another saga can import, and Update from a File, which
reads such a file back over them.
<!-- /tui -->

How much of a character is written down is their detail level:

- **Line**: a name and who they are.
- **Sketch**: the statblock play needs, as the books print their NPCs.
- **Full**: the whole sheet.

Only a Full character is played. A Line or Sketch character is left out of
season plans, ageing and creation budgets. **Promote** writes one more
level down, and **Demote** keeps one less. Nothing is deleted, and the
parts a level doesn't show keep what they hold. Promoting a Sketch to Full
moves them In Creation and opens the Creation Worksheet on what the sketch
already has.

<!-- tui -->
Both are in More (`m`) on the top panel.
<!-- /tui -->
<!-- gui -->
Both are in the **Manage** chapter.
<!-- /gui -->
<!-- gui -->
**Manage**, the sheet's last chapter, offers:

- **Export**, which writes the character to a file another saga can import
- **Update from a File**, which reads such a file back over them
- **Print to PDF** (see [Printing a record](help:print-record))
- **Delete**, which deletes the character after saying what happens to
  what they own
<!-- /gui -->

### Characteristics
<!-- help: section-char-characteristics -->

<!-- tui -->
The eight Characteristics, typed in with `e`. They're always on screen.
<!-- /tui -->
<!-- gui -->
The eight Characteristics, as cards under the header, typed in with the
**Edit** button at the end of the cards. They're always on the page.
<!-- /gui -->

So much of the sheet is worked out from them: Soak, Encumbrance, Casting
Scores and combat totals all use them.

## Statblock
<!-- help: tab-statblock -->

A Line or Sketch character opens here. It shows who they are ("In the
Saga"), and for a Sketch their Characteristics, the Arts and Abilities that
matter, their Virtues and Flaws, signature spells, Personality and
Reputations. **Abilities not listed count as 0.**

<!-- tui -->
Each part is edited where it lives: "In the Saga" with the character's
Edit, the rest on its own tab.
<!-- /tui -->
<!-- gui -->
Each part is edited where it lives: "In the Saga" with the character's
Edit, the rest in its own chapter.
<!-- /gui -->

A Line or Sketch character has no Inventory or Planning, since they aren't
played season by season. A Line character has no Abilities, Virtues and
Flaws or Hermetic Magic either.

### The statblock
<!-- help: section-char-statblock; tui -->

The statblock as one block, redrawn whenever one of its parts changes on
another tab.

## Description
<!-- help: tab-description -->

Who the character is and how they're faring: background, personality,
reputation, the records they're connected to (see
[Connections](help:section-connections)), age and health.

<!-- gui -->
At a Glance, at the top, lists the Age, Covenant, Laboratory, Type, Size
and any True Faith. A magus's familiar has its card here, which opens its
page.
<!-- /gui -->

**You type:** each section's entries, as below.

**The app works out:** Health's totals, and when a season is applied, the
Winter aging roll and the year's Warping Points.

**See also:** [Abilities](help:tab-abilities),
[Virtues & Flaws](help:tab-vf), [Diary](help:tab-diary),
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

The House decides which Virtue is the magus's free House Virtue, which then
counts no points on [Virtues & Flaws](help:tab-vf). Reads Lab Texts of
lists the authors whose Lab Texts this magus can read.

<!-- tui -->
The Lab Texts Read button, or Lab Texts Read in More (`m`), sets an
author, the level the magus reads them to (0 forgets the author) and
whether the magus decoded them or was taught.
<!-- /tui -->
<!-- gui -->
The **Texts Read** button sets an author, the level the magus reads them
to (0 forgets the author) and whether the magus decoded them or was
taught. It's beside the section, and beside the Lab Texts of the magus's
laboratory. While a magus has no familiar, a blank **Bind Familiar** card
stands under the section, where the familiar would be.
<!-- /gui -->

For a magus of House Tremere, **Holds own voting sigil** records that
they've beaten their parens in certamen for their sigil. Until then the
sheet says who holds it: the parens, or the first magus up the line of
parentes who does when the parens doesn't hold their own. A parens of the
saga's who has died no longer holds it (DE p. 16).

For a Tremere whose parens still holds the sigil, **Has challenged for his
sigil** records that they've made their one challenge for it, at a time of
their choosing. After that they may challenge only at the House's
Decennials, every ten years (1218, 1228...), and the sheet says when the
next falls. Winning the certamen gives them their own sigil (Houses of
Hermes: True Lineages p. 123).

**School of certamen** records the style they were trained in, or joined by
a season's study with a member of the school (True Lineages p. 135). The
Casting Totals section then names it and what its followers can do.

For a magus with Mercurian Magic, **Has learned Road Magic** opens the Road
and Road Network Ranges and Targets for their spells. It takes a season's
teaching by one who knows it, with no further Virtue. A starting magus
whose parens has Mercurian Magic may be assumed to have learned it (TMRE
p. 116).

**Renounced (year)** and **Renounced by** record a magus cast out of the
Order by a Wizard's March. Closing a Tribunal meeting that Marched them
sets both. The section then says they're renounced. Any magus may slay
them, and by tradition what they have goes to whoever does (DE p. 18).

Their parens is expected to strike first, a social expectation rather than
a legal duty (DE p. 21), so nothing charges an heir who fails to. Houses of
Hermes: True Lineages p. 53 makes it the heir's duty, and lets the slayer
settle for the heir's inheritance. The Tribunal's case shows that
convention. A Wizard's War they're fighting, or about to fight, shows here
too, with its months (see the Tribunal's
[Cases](help:section-trib-cases)).

### Biographical Detail
<!-- help: section-char-biographical -->

Who the character is on paper:

- Player, Birth Name, Year Born
- Race/Nationality, Place of Origin, Religion, Title/Profession
- Height, Weight, Hair, Eyes, Handedness, Physical Description
- the free-text Biography

<!-- tui -->
The Biography is in the second column. All of it is typed in with `e`.
<!-- /tui -->
<!-- gui -->
Physical Description and the Biography sit under Appearance and Biography.
All of it is typed in with the section's **Edit** button.
<!-- /gui -->

The app works out the character's Age from Year Born.

Below Personality Traits and Reputations, a character who doesn't live at
a covenant the troupe plays has an [Attitude](help:section-attitudes)
toward each player covenant, as a neighbour has. Think of a lord's
steward, a hedge witch or a faerie knight. They also have the
[Favours](help:section-favours) owed between them and the troupe. Then
come the character's [Connections](help:section-connections): their
covenant, the factions they're a member of, what they rule, and any other
record that links to them.

With Art & Academe's medicine on, Edit Biographical Detail also asks for
the character's **complexion**, the blend of the four humours (A&A pp.
40-41):

- **sanguine**: blood, hot and moist, waxing in spring
- **choleric**: choler, hot and dry, summer
- **melancholic**: melancholy, cold and dry, autumn
- **phlegmatic**: phlegm, cold and moist, winter

Most people show two, the principal one first, and sometimes a touch of a
third. The hot or cold quality never features twice, so sanguine never
mixes with choleric, nor melancholic with phlegmatic. The sheet shows the
blend, its qualities, the season it waxes in, the traits it suggests, and
the foods of the opposite qualities that keep it in balance (p. 41).
Complexion changes no roll. It's the troupe's guide to personality and to
which diseases threaten.

### Notes & Goals
<!-- help: section-char-notes -->

The player's own page in the character's sheet. It holds their **Private
notes** (plans, suspicions, what the character really thinks of the
princeps) and the **goals** they set the character. It's in Description.

**Who reads it:** the character's players, all of them for a character
several play, its Steward, and its storyguide. With a
[storyguide for each story](help:assign-storyguide), only its own
storyguide reads it. No other player sees the notes, or that there are
any. A Remote seat and an export leave them out. A goal ticked **Share
with the troupe** is read by anyone who reads the character, and the rest
are private.

The list's first row is the notes, then each goal, with the score it aims
at and who reads it. Everything is written out in full below the list.

<!-- tui -->
`a` adds a goal, `e` edits the notes or the goal chosen and `d` deletes a
goal after asking. On a goal with a score to reach, More (`m`) offers
**Plan the Study Path**.
<!-- /tui -->
<!-- gui -->
**Add** adds a goal, **Edit** edits the notes or the goal chosen and
**Delete** deletes a goal after asking. On a goal with a score to reach,
**Plan** opens Plan the Study Path.
<!-- /gui -->

**You type:** for a goal, its words and whether to share it. For a score
to reach, also the **Art or Ability**, the **Score** and the year to reach
it **By the end of** ("Creo 15 by 1230"). [Study Path](help:study-path)
then opens filled in from it. The notes support **bold** and *italic*.

### Personality Traits
<!-- help: section-personality-traits -->

The character's Personality Traits, each a name and a score that you type
(DE, Chapter 3: Characters). Binding a familiar adds a Loyal (Partner) +3
trait to the magus, which you can change or delete like any other.

A trait roll is a stress die + the trait alone, against:

- 3 for what average people usually do
- 6 for what they do half the time
- 9 for what they usually don't
- 12 for what even people known for the trait rarely manage

A player changes the scores only between sessions, after striking rolls or
events (DE p. 28).

<!-- tui -->
On a grog who serves a covenant, More (`m`) here offers
[Reward or Punish](help:grog-discipline) and [Pension](help:grog-pension).
<!-- /tui -->
<!-- gui -->
On a grog who serves a covenant, **Reward or Punish** and **Pension** are
in the [Deeds chapter](help:tab-deeds), under Covenfolk.
<!-- /gui -->

A grog's Loyal to Covenant begins within 3 of the covenant's Prevailing
Loyalty (DE p. 185).

<!-- tui -->
More (`m`) here offers
[Confidence through Sin](help:confidence-through-sin) on a character with
a sinful trait. It offers [Infernal Influence](help:infernal-influence) on
a sinner, or one who knows Infernal Lore. It offers
[Holy Influence](help:holy-influence) on one of holy standing.
<!-- /tui -->
<!-- gui -->
**Confidence through Sin** and **Infernal Influence** are in the
[Deeds chapter](help:tab-deeds) under The Infernal, for a sinner or one
who knows Infernal Lore. **Holy Influence**, for one of holy standing, is
in the Religion chapter.
<!-- /gui -->

**Sympathy Traits.** A Personality Trait can be a faerie **Sympathy
Trait**. Tick *Faerie Sympathy Trait?* on its form, and the list shows it
as "Winter: +3 (Sympathy)". It's a bond with a narrow class of things
through the Faerie realm, such as Winter, Iron or Hounds, never a whole
Form.

- **As a specialty.** Where it fits, it can stand as a non-Supernatural
  Ability's specialty, adding its score in place of the +1. The roll
  becomes a stress roll, and a botch Warps. Only the best fitting Trait
  counts.
- **Negative Traits.** A negative Trait comes off every Ability it fits,
  and the worst one adds its size in botch dice (Realms of Power: Faerie
  p. 102).
- **Experience.** Experience raises a Trait as an Ability, to no more than
  the Warping Score, at 5 xp a season of practice. A negative one rises
  only while the Warping Score is above its size. It takes 10 xp from -1
  to 0, 15 from -2 and 20 from -3, and may go on through 0 (p. 103;
  Errata p. 68).
- **Temporary Traits.** Traits gained by sympathetic influence or granted
  by a Grant rite are temporary Sympathy Traits. Tick *Temporary Sympathy
  Trait?* as well, and the list shows "Oak: +2 (Sympathy, temporary)".
  They work as Sympathy Traits for a specialty, a folk charm, a rite's
  limit and botch dice. But experience doesn't raise them, the Warping
  Score doesn't limit them, and they don't count toward the Faerie Rank
  (pp. 103-105, 127).

The Traits a tinted aura gives everyone in it are plain Personality Traits
(p. 104).


### Reputations
<!-- help: section-reputations -->

The character's Reputations, each a name and a score that you type (DE,
Chapter 3: Characters). A Reputation may also give its type and how far it
reaches, both shown in brackets after its score. The types are Hermetic,
Local, Noble, Academic, Ecclesiastical and Infernal.

A **Noble** Reputation is known among the landed class, meaning everyone
who holds land or a great lord's office, or may inherit them (Lords of Men
p. 25). Entering feudal life, by birth or by becoming a vassal, starts one
at 1. Each season of great deeds noted by other nobles is an experience
point in it, such as hosting a tournament, making war or leading pilgrims.
A knight's prize Reputation is **Prudhomme**, which tournaments read.

Some events give more (p. 26):

- a season at war in a distant land, 1 more
- knighting a squire they trained, 1
- gaining a noble liege 3, a royal liege 6
- study under a supernatural creature, its Might / 5

Whether someone has heard of the character is a
[Reputation Roll](help:reputation-roll).

A noteworthy deed before witnesses who talk starts a Reputation at 1. Each
later one is an experience point in it, as for an Ability, so ten deeds
take it from 1 to 2 (DE p. 386). Type the new score when it rises.

Whether a Reputation is good or bad is yours to say, by its sign. Type a
bad one with a negative score (Drunkard -2) and a good one with a positive
score.

Academic Reputations are kept apart instead (Art & Academe p. 103). A Good
and a Bad one are separate entries, each with its own positive score that
builds like an Ability. A scholar may hold both at once, such as Good
Logician and Bad Argumentative. Tick **Bad Reputation?** on a bad one, and
any Reputation may be marked so. A roll adds the highest Good Academic
Reputation and takes off the highest Bad one (pp. 89, 100). A bad Academic
Reputation saved below 0 is read as a Bad one of that score.

A university exam adds the Good Academic Reputations and takes off the Bad
ones. Only academic ones count. It needs a net 1 for the baccalaureus
after 3 years at university, 2 for the magister after 8, and 3 for the
doctor after 10, counting the exam season (Art & Academe p. 100). The
doctor exam needs the Magister in Artibus Virtue already (DE p. 76) and
uses the faculty's Ability. Disputatio and debate count the highest good
one.

A bad Reputation can be **replaced** (DE pp. 386-387). Start the new one at
1 with a deed spectacular enough to begin a Reputation, and choose the bad
one it **Replaces** on its form. End of Session then asks for the deeds
that support the new one, which count toward it alone, and the other
noteworthy deeds. Those still count toward the old one until the new one's
score passes it, and toward the new one after. Once it's ahead, each time
it gathers the experience to rise you may lower the old one by a point
instead, ticked by default. An old Reputation lowered to 0 is gone. The
Reputations list marks a new one "replacing" the old.

<!-- tui -->
More (`m`) here offers **House Acclaim** to magi of Bonisagus and
Flambeau, and **Reputation Roll** to anyone with a Reputation.
<!-- /tui -->
<!-- gui -->
**House Acclaim**, for magi of Bonisagus and Flambeau, and **Reputation
Roll**, for anyone with a Reputation, are in the
[Deeds chapter](help:tab-deeds) under Session & Reputation.
<!-- /gui -->


### Lineage
<!-- help: section-char-lineage -->

A magus's line, read from each character's **Parens** in Hermetic
Background. It runs up through their parens, theirs and so on, as far back
as the saga names them. A parens who isn't a character of the saga ends
the line. Below the magus come their filii and theirs, an apprentice
marked so. It shows for a character with a parens, or with filii in the
saga. Change it by editing the Parens in Hermetic Background.

### Marriages
<!-- help: section-char-marriages -->

Shown once a marriage names the character as bride or groom. Each shows the
spouse, when, the dowry, whether it's a betrothal, a marriage or ended,
and how it ended. Marriages are arranged and ended under Marriages on
either family's lord (Lords of Men pp. 10-11, 81; City & Guild p. 113).
This is the same record, shown here too.

### Aging & Warping
<!-- help: section-aging -->

<!-- tui -->
Decrepitude, the Effects of Aging and the Warping Score and Points, typed
in with `e`.
<!-- /tui -->
<!-- gui -->
Decrepitude, the Effects of Aging and the Warping Score and Points, typed
in with the **Edit** button of the Aging section. Warping and Decrepitude
also show as dials in the header.
<!-- /gui -->

The same form has Gain Warping Points now, for points gained from one
event. Two or more at once take a magus to the edge of Wizard's Twilight,
which the app rolls straight away against the **Aura where it happened**.
Left blank, that's the aura where the character lives. **Enter Twilight
willingly** skips the roll to avoid it (DE p. 228). A botched spell gives a
Warping Point for each zero on the botch dice (DE p. 227), so type them
there as one event. The form also keeps the **Twilight Scars**, one a
line, and [Resolve Twilight](help:resolve-twilight) applies what a
Twilight left.

When Winter is applied, the app makes the yearly aging roll. It adds the
apparent age, Aging Points, Decrepitude points and any Longevity Ritual
here. It also adds the year's Warping Points from a Longevity Ritual or a
strong aura of another realm (DE, Chapter 10: Long-Term Events).

**Time in their home aura** sets how much of that they gain, by DE p.
390's table:

- **always**: living, working and sleeping there
- **half the time**: sleeping there but working elsewhere, or two weeks in
  and two out
- **frequent visits**: about a quarter of their time
- **living elsewhere**

A level 9 aura gives 4 points a year always, 2 half the time and 1 on
frequent visits. One point every second year comes in even years.

A botched Twilight comprehension adds a step on the time table for each
zero. The steps can reach the table's row 10, Final Twilight, so a magus at
Warping 8 who botches with two zeros is lost (DE p. 228).

A magus with the Lesser Elixir in force shows "Lesser Elixir: -N more".
That's its Level, taken off their aging rolls with the Longevity Ritual's
modifier (The Mysteries Revised Edition p. 42; see Reinvent the Lesser
Elixir). A magus the Great Elixir made a being of Magic shows "A being of
Magic". They make no more aging rolls and gain no Warping, and their Magic
Might shows beside their Size (p. 44; see
[Test the Great Elixir](help:great-elixir)).

**What gave them** says where the points came from. One event, such as a
powerful effect or a botch, is the usual.

- **Taken leaving Faerie** asks for the **Days spent in Faerie** and the
  **Final fable score**, and writes in the Diary how long passed in the
  mundane world. Each day there lasts an hour at fable score 0, 12 hours
  at 1, a day at 2, three days at 3, a week at 4, a month at 5, a season
  at 6 and a year from 7. Each Warping Point taken lowers the score by 1.
  A group leaving together takes the lowest, the others taking points to
  match (Realms of Power: Faerie p. 30).
- **Instant transport** is a point a transit. A spell or device of level
  30 or more that carries someone gives a Warping Point each time, unless
  they cast it or it was made for them. A Hermes' or Mercere's Portal
  gives none (Transforming Mythic Europe pp. 112, 114).

Neither brings Twilight, however many points. Faerie's never do, and each
transit is its own event.

The app counts the Warping Points from each realm as they come, from an
event's **Its realm**, an aura's or a place's realm, or a Longevity
Ritual's Magic. The section shows the count and the main source, the realm
with the most. A tie, or nothing counted yet, goes to the aura where they
live. A non-magus's Warping effects follow the main source:

- **Magic**: the Definitive Edition's own (DE p. 391).
- **Faerie**: a glamour of their own may take the first Flaw's place. It's
  a Reputation that rises with each Score and brings Sympathy Traits
  later, with Faerie Antipathy or Lesser Malediction at 3 (Realms of
  Power: Faerie p. 119).
- **Divine**: Flaws that punish sin or push piety to extremes (Realms of
  Power: The Divine p. 62).
- **Infernal**: a sinful Personality Flaw at 1, Offensive to Animals or
  Tainted with Evil at 3, an Infernal Virtue at 5, and Age Quickly,
  Enfeebled or Plagued by a Demon from 6 (Realms of Power: The Infernal
  p. 17). The Errata names Aptitude for (Sin) among the Virtues at 5.

The Virtue at Score 5 stops Warping only from auras of the main source's
realm (DE p. 391).

With Art & Academe in play, the form also takes a physician's
**Regimen**. That's its bonus to the Living Conditions the aging roll
uses, the physician (a character with Medicine) and the year it began. It
helps once the character has lived under it a year:

- +1 from a physician with Medicine 1, who can keep up to five times
  their Medicine in clients on it
- +2 from Medicine 4, for up to their Medicine in clients
- +3 from Medicine 7, for one client

A physician keeps a single regimen. Its level is their first client's, in
the saga's order, and it takes only as many clients as it allows, the
first ones. It needs bloodletting from someone with Chirurgy 3, either the
physician or someone at their covenant. The section says when the
physician's Medicine is too low for the bonus chosen, or why the regimen
gives nothing. A covenant drawing on Emergency Savings can keep no
regimen, so its bonus stops (Art & Academe p. 58).

Eucrasia is lost, and the regimen starts its year again, when the patient
plays a season convalescing or travelling, catches a disease, or enters
Wizard's Twilight (p. 59). The Diary says so. For the other causes, such
as a month away, a neglected diet, broken sleep or a day under a Corpus
spell, retype the year the regimen began on Edit.

**Faerie Rank.** A character with Sympathy Traits shows their **Faerie
Rank** under Warping. It's their best positive Sympathy Trait plus their
worst negative one, so Winter +4 and Summer -2 make +2, and Dancing +1 and
Stone -5 make -4. Temporary Traits are left out and listed after it. The
section also shows the botch dice the worst negative Trait adds, and how
far experience may raise their Traits (Realms of Power: Faerie p. 103).
Faeries like a high Rank and dislike a negative one. A Faerie Calling,
when a faerie wizard takes Warping, now says whether their Rank makes it a
good Calling or a bad one (p. 120).

Sympathetic influence is for the storyguide. It's either of these
(pp. 103-104):

- a ceremony of about ten minutes, led by someone with Faerie Lore 1.
  Everyone taking part spends a Confidence Point, and it lasts a week at
  most.
- a season of free time spent with the subject, lasting up to a year

Then roll a simple die + Presence + Leadership. 9 gives a Trait of 1 (or
-1), 15 of 2, and 24 of 3, the most. The subject needs a fitting
Personality Trait or Flaw. A fitting Sympathy Trait may be Leadership's
specialty, on a stress die.

### Health
<!-- help: section-char-health -->

<!-- tui -->
The left column shows Soak, Encumbrance and the Wound Penalty, worked out
from Stamina, armour, Virtues and the load of the character's Personal
Gear. Below them it shows:

- how far the character moves in a combat round: 10 + Quickness -
  Encumbrance paces at a walk, twice that hurrying, four times running
  (DE p. 395)
- what they can carry, lift and drag: a Burden of Strength + 5, + 7 and +
  12. A Load point is about 7 pounds. A clawed or hoofed four-footed
  beast's Strength counts half again, not a bird's or fish's (Grogs pp.
  47-48).
- how far they can push themselves in a day on good roads: 15 + 2 x
  Athletics miles on foot, with Encumbrance taken off Athletics. Riding,
  it's 30 + 2 x Ride, or 20 without Ride. It costs two Long-Term Fatigue
  levels (Grogs pp. 51-52).
- the wounds as typed
<!-- /tui -->
<!-- gui -->
The wounds as typed, on the Damage Table for the character's Size, then
the Fatigue Level, then Soak, Encumbrance, the Wound Penalty and the total
penalty from wounds and fatigue. Soak, Encumbrance and the Wound Penalty
are worked out from Stamina, armour, Virtues and the load of the
character's Personal Gear.
<!-- /gui -->

Enduring Constitution makes the wound and fatigue penalties 1 better, and
Low Tolerance 1 worse (DE, Chapter 11: Obstacles).

<!-- tui -->
The right column shows the Fatigue Level, the total penalty from wounds
and fatigue, and the Damage Table for the character's Size. `e` edits the
wounds and a Soak adjustment. The Edit Fatigue button, or Edit Fatigue in
More (`m`), sets the Fatigue Level.
<!-- /tui -->
<!-- gui -->
The **Wounds** button beside the section edits the wounds and a Soak
adjustment, and the **Fatigue** button sets the Fatigue Level.
<!-- /gui -->

Wounds and Fatigue take their penalty from every roll and total, the
Casting Score and certamen included, but not from Soak or Recovery rolls.
Listed under the wounds are any wound that isn't an injury (a disease,
poison or deprivation), any wound with stable rolls behind it, bruises and
the Recovery Total.

**Recovery** adds up these (DE pp. 289, 267, 405; Realms of Power: The
Infernal p. 12):

- Stamina
- the medic's Chirurgy for an injury, or Medicine for the rest. It's the
  best among the character's covenant-mates, named.
- the stable rolls' +3s, and magical aid
- the laboratory's Health, for those who live in one
- a familiar's Bronze Cord
- Rapid Convalescence or Fragile Constitution
- less an Infernal aura where they live

Each season the wounds heal on their own (see
[Recovery](help:recovery-roll)). The Fatigue Level shows how many of its
levels are long-term. Those come back a night's rest each, and the rest in
minutes. A season clears both.

With the **Art & Academe medicine** rule option, an injury's Recovery
counts **first aid** and **palliative care** in place of the medic's whole
Chirurgy:

- First aid given within a day of the wounds adds half the first-aider's
  Chirurgy, rounded up.
- Palliative care, the nursing afterwards, adds half the Chirurgy of the
  covenant-mate who nurses best. A palliative care specialty counts.

The two together never come to more than the nurse's Chirurgy, so a
medicus with Chirurgy 5 who gives both gives +5, not +6 (Art & Academe pp.
61-62). A wound that has had first aid is marked "first aid" in the list.
A disease, poison or deprivation still takes the physician's Medicine.

**Activities while injured** (DE p. 405):

- **-1 or -2**: travel and study, but nothing strenuous, such as spells
  that cost Fatigue.
- **-3 to -5**: travel is halved, and so is study for a month or more of
  it. No lab or craft work.
- **-6 or worse**: only talking, eating and moving short distances with
  help.

Doing more than that means a [Recovery Roll](help:recovery-roll) for the
worst wound, which can only hold or worsen. After a battle, -6 or worse
can't travel and -3 or worse can't keep pace with an army (Lords of Men p.
108).

**First aid** (Grogs p. 59) is Dexterity + Chirurgy + stress die, within a
day, against the Improvement Ease Factor of the worst wound. Success lets
the wounded act one category better for a day, still taking the Wound
Penalty, and a botch means an immediate Recovery roll. With Art &
Academe's medicine, first aid is rolled from
[Recovery Roll](help:recovery-roll), which gives its rules.

<!-- tui -->
More (`m`) on Health offers [Take Harm](help:take-harm) and a
[Recovery Roll](help:recovery-roll).
<!-- /tui -->
<!-- gui -->
**Take Harm** and **Recovery Roll**, beside Health's Edit buttons, harm the
character or roll for their wounds now.
<!-- /gui -->

## Boost a Spell
<!-- help: boost-spell -->

<!-- tui -->
More (`m`) on Known Spells offers it, for a magus who may boost one of
them.
<!-- /tui -->
<!-- gui -->
**Boost a Spell** is on Known Spells, for a magus who may boost one of
them.
<!-- /gui -->

Boosted Magic boosts any Formulaic spell (DE p. 72). A Boosted spell needs
Boosted or Mutantum Magic, and Boosted Casting comes with Mastery (Houses
of Hermes: True Lineages pp. 99-103).

Choose the **Spell**, then the **Range**, **Duration** and **Target** it's
raised to, and how much **Larger by**. The inspector gives the pawns of
vis it takes, one a magnitude, and the botch dice they add, one a pawn. It
also says what stops it. Nothing is lowered, and Year or Boundary is
reached only by a Ritual. It's a calculator that changes nothing, and the
spell is cast at the table at its own level.

## Resolve Twilight
<!-- help: resolve-twilight -->

<!-- tui -->
More (`m`) on [Aging & Warping](help:section-aging) offers it.
<!-- /tui -->
<!-- gui -->
It's in the Aging section of [Aging & Warping](help:section-aging).
<!-- /gui -->

After a Twilight the app has rolled, this applies the storyguide's choice
(DE pp. 229-230). The Twilight's Diary line says how many points it gave
and what they buy. Tick **Comprehended** if it was, type the **Warping
Points gained** in all, and choose the **Effect**:

- **Experience**: twice the points in an Art, Magic Theory or Enigmatic
  Wisdom. It's gained if comprehended, and lost if not, never below 0.
- **A Virtue or Flaw**: from 7 points. Comprehended, it's a Hermetic or
  Supernatural Virtue, Minor to 10 points and Major from 11. Not
  comprehended, it's a Flaw, Major from 10. One that names something, such
  as an Art or an Ability, is added from Virtues & Flaws instead.
- **A spell**: learned, of as many magnitudes as the points, or lost. A
  Twilight that takes several spells is resolved once for each.

Type the **Twilight Scar** it left. It joins the scars in Aging & Warping,
and the whole goes in the Diary.

## Take Harm
<!-- help: take-harm -->

Harm from more than weapons, rolled, then kept in the Diary when you choose
Keep.

- **An injury**: a damage bonus + stress die against Soak + stress die,
  read on the Damage Table for the character's Size. The bonus comes from
  the Heat and Corrosion or Impact tables, or is typed. Falling is +1 per
  two feet, doubled on a hard surface and halved on a soft one. Heat and
  corrosion multiply their bonus by how much of the body they cover, from
  a hand x1, a limb x2 and half the body x3 to all of it x4. Untick
  **Armour protects** for boiling water and the like (Definitive Edition
  p. 407).
  - With Hermetic Projects in play, the tables add a volcano's hazards
    (pp. 13-14). Lava is +15 each round, x2 a limb, x3 half the body and x4
    immersed. Armour counts against it only while it covers less than half
    the body. Boiling mud is +3, the heat within 30 yards of lava +3 a
    Diameter, and falling rocks in an eruption +5 at its edge to +20 at its
    heart. Its fumes are a poison, a Stamina check against 6 each Diameter
    or a Medium Wound, beside an air Deprivation check every 30 seconds.
- **A poison** or **a disease**: a Stamina check (stress die) against its
  Ease Factor. That comes from the Poison table (p. 406), City & Guild's
  urban diseases (pp. 27-28), or is typed. Failing it gives the wound
  named, which heals with Medicine. A disease spirit's attack must first
  pass Magic Resistance.
  - With the **Art & Academe medicine** rule option, a disease is its own
    record instead (see [Art & Academe's diseases](help:aa-diseases)).
    Choose one of the book's (pp. 47-51), or make one from its stage,
    Interval and Ease Factors. The Disease Avoidance roll is Stamina +
    Living Conditions + Corpus / 5 for a magus + the Wound Penalty +
    stress die. It must reach the Stable Ease Factor, by the Definitive
    Edition's equals-or-exceeds (DE p. 7). Art & Academe's "exceed" on p.
    46 disagrees with its own other rolls. A botch catches it a stage
    worse.
- **Deprivation** of air, water or food, for a number of periods of 30
  seconds, a day or three days. Each period is a Stamina check against 3,
  1 more each period. Each failure is a Fatigue level, long-term for water
  and food. Once unconscious, a failure is a Light Wound, then each a level
  worse (p. 407).
- **A bruise**, with the Bruises rule option (Lords of Men pp. 131-132): a
  non-lethal blow read on the Damage Table as a bruise. Its penalty works
  as a wound's. It heals within hours, and a Heavy, Incapacitating or
  Fatal one leaves a Light, Medium or Incapacitating wound.

With Art & Academe's medicine, an **injury** asks where it struck: the
head, the torso or a limb. An Incapacitating wound it deals calls at once
for a Stamina roll against 6 (Lasting Consequences of Serious Damage, A&A
p. 43). A failure leaves a lasting complication, a Minor Flaw fitting the
place, from the Surgical Intervention lists (p. 62):

- **the head**: Disfigured, Missing Eye or Missing Ear
- **the torso**: Disfigured or Fragile Constitution
- **a limb**: Disfigured, Lame, Missing Hand or Palsied Hands

The storyguide picks it, and the Diary keeps the roll.

Each of the book's **diseases** is an excess of a humour (pp. 47-51). A disease
of the character's own principal humour is ill-suited to the temperament,
and the result says so. As with a place that breeds the disease, that's
worth a roll or two in the first season there (p. 46).

The disease list also holds Dies Irae's **Great Pestilence** (pp. 86-98).
It's a Critical phlegmatic disease of Severity 21, Stable 12, Improve 18,
rolled every day once its Crisis passes.

- *The Great (Form) Pestilence* is a magic being's. It calls for a Disease
  Avoidance roll at the Form's new moon, and each week it stays in a Magic
  aura (pp. 87-88).
- *The Great Corpus Pestilence (Corpus miasma)* is what a Corpus miasma's
  Corpus Blight gives every human it touches. There's no Disease
  Avoidance, but its Penetration is 0, so magi and all others with Magic
  Resistance are immune (pp. 88, 94). That means a magus's Corpus and
  Parma, or True Faith, a Church office and relic, or Angelic Might.

A magus's **Form Bonus**, the Form's score / 5 rounded up, adds to Soak or
to the roll resisting harm of its Form (Definitive Edition pp. 206-209).
For an injury or a bruise, choose **What it comes from**:

- fire or heat, or cold or ice: Ignem
- an animal's claws, teeth or horns: Animal
- a human's unarmed blow: Corpus
- a wooden weapon or timber: Herbam
- a metal or stone weapon, or stone: Terram
- a jet or wave of water: Aquam
- lightning or other weather: Auram
- one's own spell-casting gone wrong: Vim

The tables' entries choose their own unless you choose otherwise, and
corrosion and the jug have none. For a poison, choose the **Kind of
poison**. An animal's venom is Animal, a herbal poison Herbam and a
mineral one Terram. The Poison table's entries choose theirs. A disease's
Stamina check adds Corpus, never to aging. Deprivation of air adds Auram,
of water Aquam and of food Herbam. Tick **Drowning** for air lost under
water, where Auram or Aquam counts. The bonuses never stack. Where two
apply only the higher counts, and the result names the one used. Vim's
bonus to avoiding Twilight is part of the Twilight roll.

## Recovery Roll
<!-- help: recovery-roll -->

Wounds heal season by season, when the season is advanced. Each rolls
against its two Ease Factors:

- **Light**: weekly, against 4 and 10
- **Medium**: monthly, against 6 and 12
- **Heavy**: once a season, against 9 and 15

At or over the higher, the wound improves a level. At or over the lower,
it holds and gains +3 to its later rolls. Below, it worsens. An
Incapacitating wound rolls twice a day. 0 or less dies, 9 or more makes it
Heavy, and anything else is worse, with -1 to later rolls (Definitive
Edition p. 405). The rolls go into the Diary.

**Recovery Roll** rolls once for each wound now, or for the worst one
only. That's the roll for doing more than the wounds allow, which can only
hold or worsen. It also sets the **magical aid** every Recovery roll adds,
such as a Zenodochium's +9 (Against the Dark p. 98) or a Purification of
the Festering Wound. It rolls each disease once too. Keep applies the
rolls.

With the **Art & Academe medicine** rule option, Recovery Roll also
offers:

- **first aid**: a chirurgeon tends the injuries. That's anyone in the saga
  with Chirurgy, the patient too. Each injury without first aid keeps half
  the chirurgeon's Chirurgy, rounded up, as a bonus to its Recovery rolls.
  The First Aid roll says whether the patient may act a category less
  injured for a day. It's Dexterity + Chirurgy + Recovery Modifiers +
  magical aid + stress die, against the worst wound's Improvement Ease
  Factor. A botch gives no bonus and makes an immediate Recovery roll,
  which can only hold or worsen (Art & Academe p. 61). Use it within a day
  of the wounds.
- **surgery** on a disease: choose the disease and the procedure. The
  Surgery roll is Dexterity + Chirurgy + Recovery Modifiers + stress die,
  against the procedure's Ease Factor.
  - phlebotomy 3, cautery or cupping 4. Each costs a Fatigue level, and
    is only for a disease of Severity 5 or less.
  - a rotten tooth 6, quinsy or a cataract 9, trepanation 12. Each gives a
    Light Wound.
  - a gall stone or fistula 9, a cold or hot tumor 12, a consumptive tumor
    15. Each gives a Medium Wound.

  The wound comes whatever the roll. A botch makes it a step worse and
  leaves the disease be. A success returns the disease to the stage it
  began at and gives +3 to its next Recovery roll (Art & Academe p. 61).
  Whether surgery can help a disease at all is in its description.
- **Surgical intervention when a roll fails**: tick it, choose the
  chirurgeon and where the wounds are (the head, the torso, a limb), then
  roll. Each Recovery roll that fails gets a Surgery roll against 9.
  - Success holds the wound as a stable result, with its +3.
  - Failure lets it worsen.
  - A botch worsens it two steps, so a Light wound becomes Heavy, a Medium
    Incapacitating, and anything worse is death.

  Whatever the roll, the patient keeps a consequence by the wound's
  severity (Art & Academe p. 62):
  - **Light**: an immediate Aging roll, made when you Keep, in the Diary.
  - **Medium**: two Aging Points in a Characteristic of that place, placed
    with Place Aging Points. The head's are Intelligence, Perception,
    Communication or Presence, the torso's Stamina or Strength, and a
    limb's Dexterity or Quickness.
  - **Heavy**: a Minor Flaw of that place, from the lists in
    [Take Harm](help:take-harm).
  - **Incapacitating**: a Major Flaw of that place. The head's are Blind,
    Deaf or Mute, the torso's Crippled or Enfeebled, and a limb's Crippled
    or No Hands.

  You add the Flaw on Virtues & Flaws. The season's own healing rolls never
  intervene.

## End of Session
<!-- help: end-of-session -->

<!-- tui -->
More (`m`) on [Reputations](help:section-reputations) offers **End of
Session**, for what a session of play gave the character.
<!-- /tui -->
<!-- gui -->
**End of Session**, in the [Deeds chapter](help:tab-deeds) under Session &
Reputation, opens a form for what a session of play gave the character.
<!-- /gui -->

If they were played for a good part of it and contributed, each award
ticked is a Confidence Point:

- achieving a personal goal
- contributing to a group goal
- success in a difficult task, once a session
- entertaining roleplaying
- a bonus the storyguide thinks deserved, once a session

Two or three a session is typical. The Confidence Score itself rises only
after years-long events, so type that by hand (DE p. 29).

Each Reputation has a box for the noteworthy deeds done before witnesses
who'll talk, each an experience point in it, good or bad. A new one starts
with Add on Reputations. For one that **Replaces** another, the form asks
for the deeds that support it and the other noteworthy deeds apart. See
[Reputations](help:section-reputations) for both rules. The Diary records
the session.

<!-- tui -->
**Tournament** (More, `m`, on Reputations, while Lords of Men is in play)
counts a season on the tourney circuit (Lords of Men pp. 64-69). Choose
the knight's Prudhomme Reputation, or start one. It's a
[Noble Reputation](help:section-reputations), at 1 when it's their first,
else at 0.

Tick what they did as a knight. Only the highest counts (p. 68):

- 1 experience point each: riding at the head of a company, ransoming a
  well-matched opponent, a feat of daring or of unquestionable honour
- 2: ransoming a stronger opponent, or winning a prize

As patron, hosting one or more tournaments that season is 1 point, a
lavish one 2, and an artist's record of aesthetic quality at least their
Prudhomme 1 more. Patrons hosting together share the points equally,
rounded down (p. 69). Each ransom they didn't pay is an experience point
toward a fitting bad Reputation (p. 67). Add that Reputation first, then
choose it.

The result says:

- what a tournament they host should cost, 10 pounds a point of their
  Prudhomme
- what a prize for them is worth, a pound a point
- the Labor Points a season on the circuit makes them, from their
  Dexterity + Single or Great Weapon x their Wealth Multiplier
- how many seasons a year keep an errant knight, at 36 Labor Points a year
  (p. 69)

It's written in their Diary.
<!-- /tui -->

## Melee Event
<!-- help: melee-event -->

<!-- tui -->
More (`m`) on Reputations offers **Melee Event**.
<!-- /tui -->
<!-- gui -->
**Melee Event** is in the Deeds chapter, under Knightly.
<!-- /gui -->

It rolls the Melee Events Table for a tournament's grand charge (Lords of
Men p. 68). The roll is a stress die + the knight's Prudhomme Reputation +
any Confidence spent, either way. Each event they've already rolled in
this melee adds a botch die. The result names:

- the knight or company that presents itself
- the ransom fair from them. From a Wealthy knight it's their horse and
  armor, an average one their horse or armor, a Poor one perhaps their
  weapons, and little from a young one. It's never service or an oath
  (p. 67).
- the Light Wounds the opponents already carry, one for each event past
  the first

A botch is an accident. Tick **With a company** for a company's single
roll. Each roll is written in the Diary. The fight itself, and taking the
ransom, are played out. Ransoms taken or left unpaid count on Tournament.

Melee Event and Tournament are offered only while Lords of Men is among the
saga's books in play, as is every action a supplement brings.

<!-- gui -->
Tournament is in A Season's Work, under This Season on the Planning
chapter.
<!-- /gui -->

## Labor Points from a Story
<!-- help: labor-from-story -->

<!-- tui -->
More (`m`) on [This Season](help:section-char-season) offers **Labor
Points from a Story**.
<!-- /tui -->
<!-- gui -->
**Labor Points from a Story** is in A Season's Work, under This Season on
the Planning chapter.
<!-- /gui -->

It records the Labor Points a story gives a craftsman or merchant when its
central issue is resolved (City & Guild p. 39). Choose the award, from the
book's guide or one of the story seeds' own. The guide gives, in seasons'
worth:

- half, for a subplot of a story the magi deal with
- one, for severe danger or hardship
- one and a half, when their part is pivotal to the end
- two, when they're the central character
- two and a half, when failing would bring severe repercussions on their
  city or covenant

A trader sees the stories for every merchant (pp. 111-115), and those of
their kind and the poorer kinds:

- local carrier (pp. 116-118)
- merchant adventurer (pp. 119-121)
- factor (pp. 122-128)
- capo (pp. 129-130)

"Invested" awards are the smaller ones for a story left unplayed as an
investment of time (p. 40). Change the seasons' worth where the story says
so, such as antique sailing instructions' ½ to 1½.

A season's worth is what a season's work earns: (Characteristic + the
Craft or Profession chosen) x the Wealth Multiplier. That's 2 Poor, 3
average and 6 Wealthy, and a fraction rounds down. The Labor Points are
added and the Diary records the story. A story is the only way to earn
Labor Points and experience other than Exposure in the same season, so
plan the season as usual.

Some awards do more, which the result says and you apply by hand. A new
product found in every fair promotes them to Wealthy, or a Wealthy one to
the next Social Status. With the Heir Virtue, a benefactor's murder may
raise their Social Status at once.

## Sell Finished Goods
<!-- help: sell-finished-goods -->

<!-- tui -->
More (`m`) on a craftsman's This Season offers **Sell Finished Goods**.
<!-- /tui -->
<!-- gui -->
**Sell Finished Goods** is in A Season's Work, under This Season on the
Planning chapter.
<!-- /gui -->

It settles a sale the story calls for with a roll, rather than leaving it
off-stage (City & Guild pp. 75-76). Give the goods, the guild's standard
price for them in pence, and the customer.

- **A typical customer**: Presence + Bargain + a simple die against 9.
  Making it sells for 10% over the standard price, and each point over 9
  another 10%, at most 50% over. Missing it sells at the standard price.
- **An important character or another player**: Presence + Bargain + a
  stress die against their Communication + Bargain + a stress die. Type
  their roll. Each point you win by is 10% more, and each you lose by 10%
  less, at most 50% either way. A botch sells for next to nothing.

Leave the Die blank and the app rolls it, or type it to use the table's.
Superior and excellent goods aren't priced by the guild, so give a higher
standard price for them. The sale is written in the Diary, and the purse
on Personal Gear isn't changed. This is apart from the Goods catalog's
commodity prices.

## Make a Ligature
<!-- help: ligature -->

A ligature is a small charm that helps one roll. It's a sack of parchment,
stones or herbs with an Arcane or Sympathetic Connection to its target
(Art & Academe pp. 68-69). Anyone with Artes Liberales, Philosophiae or
Medicine can make one, tied to an Ability they have at 1 or more. It takes
a few hours, and helps within a six-hour window on the day it's made for,
up to a year ahead.

- **The roll**: Intelligence + the Ability + a stress die. 9 gives +1, 15
  +2, and 24 +3, the most.
- **A botch** works against the action, with -2 and two more botch dice,
  and the maker doesn't know it.
- One ligature at a time helps a person. None helps a season's work, such
  as study or a Lab Total, and a medical one helps no Recovery roll.
- Each takes 1 Labor Point from an apothecary's store. Tick "From his own
  store" when it's the maker's own, and the point comes off their Labor
  Points.

The roll and its result go in the maker's Diary.

## Apothecary's Store
<!-- help: apothecary-store -->

An apothecary (Profession: Apothecary) keeps a store of medicinals (Art &
Academe pp. 63-66). A season keeping it ("Keep an apothecary's store")
earns (Intelligence + Profession: Apothecary) x the Wealth Multiplier
Labor Points. Each Winter the business loses 36, and 3 more for each
physician whose regimens it supplies. A physician who keeps their own
store supplies themselves, and otherwise the best apothecary at their
covenant does. Each theriac or reagent made from it costs 1 Labor Point
per 5 levels, the level times the doses, and each ligature 1.

<!-- tui -->
More (`m`) on This Season offers **Apothecary's Store**, which rolls one
of two things.
<!-- /tui -->
<!-- gui -->
**Apothecary's Store**, in A Season's Work under This Season on the
Planning chapter, rolls one of two things.
<!-- /gui -->

Each is written in the apothecary's Diary.

- **Search for an ingredient**, instead of drawing on the store:
  Perception + Profession + a stress die against 9, a month's search.
  - Area Lore where they search lowers the Ease Factor, and so does each
    assistant. They may have no more assistants than their Leadership,
    each with Profession: Apothecary 1 or Area Lore 2.
  - Inhospitable ground is +1, barren +3 and winter +2.
  - A finding spell such as Hunt for the Wild Herb is -3.

  Success finds a Labor Point's worth, and each point over another, or
  halves the time. A botch finds nothing. What's found pays for that need
  only, and never adds to the store's Labor Points.
- **Preserve an ingredient**: Dexterity + Profession + a simple die,
  against how long it must keep. Weeks are 3, months 6, seasons 9, years
  12, decades 15 and indefinitely 18. A plant or animal Arcane Connection
  kept longer than it lasts lasts a category longer.

Medicinals come in four degrees, and the fourth destroys tissue and is a
poison. Only a simple poison, a Light Wound resisted at 6 or less, is made
without its formula. Stronger ones are theriacs (below).

Magic can help. A Ritual Creo spell adds 1 Labor Point for each variety it
creates. A Rego Craft spell prepares a week's ingredients at Intelligence
+ Finesse against the Ease Factor + 6.

## Philosophic Alchemy
<!-- help: philosophic-alchemy -->

A magus with Philosophic Alchemy, which builds on Hermetic Alchemy, settles
an alchemical vis extraction to digest by itself while they do other work
(The Mysteries Revised Edition pp. 40-41).

<!-- tui -->
More (`m`) on This Season offers **Philosophic Alchemy**, which settles
one starting this season.
<!-- /tui -->
<!-- gui -->
**Philosophic Alchemy**, in A Season's Work under This Season on the
Planning chapter, settles one starting this season.
<!-- /gui -->

- **It makes**: Vim vis, a Form's vis, or **open spaces in a device**. A
  Form's vis is Hermetic Alchemy's twentieth of the Lab Total, or a tenth
  with that Form's Extractor Virtue. The device is an invested one on the
  magus's or their laboratory's Inventory, not yet opened.
- **Vessel's Shape and Material bonus**: what the object the vis settles
  in gives, up to their Magic Theory (Hermetic Alchemy, pp. 39-40).
- **The pawns go to**: their own raw vis, or their laboratory's or
  covenant's stores.
- **The spaces count as**, for open spaces: **pawns already opened**, so
  opening the device costs that many pawns fewer. Or **extra room on top
  of its capacity**, so the device holds that many spaces more, already
  open, and opening the rest costs its normal capacity (p. 41 offers
  both).

Each season it runs, its Lab Total is their alchemical Creo Vim total in
their laboratory's Magic aura, less their days away from the laboratory. A
Form's vis takes the Form as a requisite, and spaces are always Creo Vim.
The Minor Virtue's digestion takes four seasons and yields by the lowest of
the four. The Major's takes one season. Vis goes to the pool chosen.

Spaces counted as pawns already opened make the device ready for
enchantment, and opening it normally costs that many pawns fewer. Eight
spaces in a 24-pawn coral leave 16 (p. 41). Spaces counted as extra room
raise its capacity instead. The coral holds 32, 8 of them open, and
opening the rest still takes 24. Its Inventory shows them as extra room.

While it digests:

- Their other lab work that season loses the seven days they tend it,
  added to their days away. Nothing is lost until the two pass ten days,
  shown as "Tending the digestion" in its Lab Total. No other lab work is
  possible past twenty.
- They can't extract vis any other way, or work in another laboratory.
- Reading or studying vis beside it is fine. A month lost to distractions,
  a season out of the laboratory such as an adventure or travel, or
  experimenting spoils it. It's then abandoned and gives nothing.

With one running, the same command shows it and can abandon it. Each
season of it is written in the magus's and the laboratory's Diaries, and
in the season's record.

## Test the Great Elixir
<!-- help: great-elixir -->

A magus with the Great Elixir drinks the potion they've enchanted and tests
it (The Mysteries Revised Edition pp. 43-44). The Virtue needs Unaging and
the Lesser Elixir.

<!-- tui -->
More (`m`) on Aging & Warping offers **Test the Great Elixir**.
<!-- /tui -->
<!-- gui -->
**Test the Great Elixir** is in the Aging section.
<!-- /gui -->

It asks for:

- **Grant Might's level**: the level of the Grant Might effect invested in
  this potion. It gives Magic Might of half (level - 20), so a level 80
  effect gives 30.
- **Die**: a simple die, or blank for the app to roll it.

The roll is the die + Stamina + their Lesser Elixir Level + 1 for each
earlier attempt, at most their Magic Theory. The Ease Factor is their age
/ 10, rounded up. The inspector shows the bonus, the Ease Factor and the
Might as you type.

On a success they become an immortal being of the Magic realm with that
Magic Might, shown on their record beside their Size. From then on they
make no aging rolls and gain no Warping. A failure means this potion's
effects didn't work for them. A new dose of the Lesser Elixir and new
effects make the next potion, which adds 1 more to the roll.

Once immortal, they may test a better potion to raise their Might. The
Ease Factor stays at the age they transformed, the earlier attempts count
afresh, and a failure only wastes the potion. Every test is written in
their Diary.

## Dream Working
<!-- help: dream-working -->

A magus with Dream Magic sends their spirit into a dream while their body
lies in a trance (The Mysteries Revised Edition pp. 102-107).

<!-- tui -->
**Dream Working**, in More (`m`) on their record or Known Spells, rolls one
of five things and writes it in their Diary.
<!-- /tui -->
<!-- gui -->
**Dream Working**, in Magic Outside the Lab under Raw Vis, rolls one of
five things and writes it in their Diary.
<!-- /gui -->

- **A spell in the dream.** Every spell is Imaginem there. They cast with
  their Technique and Imaginem whatever the effect's Form, using that
  Form's guidelines (p. 103). The aura is the dream setting's, not the
  body's, so a dream cathedral is Divine. Their real wounds, Fatigue and
  gear stay with the body. Only dream wounds take from their totals, and a
  spirit loses no Fatigue (p. 106). Their Magic Resistance there is
  Imaginem + 5 x Parma Magica + the aura, or 3 less with Parma stretched
  over body and spirit as two (p. 103). A botch gains real Warping Points,
  and Twilight is real, timed in the waking world (p. 106).
- **The dreamer notices travelers**: Perception + Awareness + a stress die
  against 9 (p. 105). This roll and the next are the dreamer's, whoever's
  dream it is. So the form asks for the **Dreamer**, usually someone else.
  It's the magus only in their own dream.
- **The dreamer reshapes the dream**: Intelligence + a stress die against
  9, plus these. It's +3 for a magus, counted for a magus dreamer and
  ticked for one of similar power. It's +3 for Dream Magic, +3 for
  Hermetic Dream Interpreter, and +1 for each other power of illusion or
  dreams, at most +3. The total is the change's magnitude (p. 105).
- **A wound in the dream**: Stamina + a stress die + the earlier dream
  wounds' penalty, against the total Wound Penalty, or 9 for an
  Incapacitating wound. Add +3 for Strong-Willed, +3 for Enduring
  Constitution, -3 for Low Tolerance, and any other modifier. Failing, the
  magus wakes (p. 106).
- **The entranced body is disturbed**: Stamina + Concentration + a stress
  die, with the body's Wound Penalty counted three times. It's against the
  Definitive Edition's distraction less 3, so jostled or a sudden noise is
  6, knocked down 9 and hurt 12 (p. 102; DE p. 215).

Spells may use Dream Duration, as Concentration, and Dream Target, as
Individual. Dream Target works only on a spell with Mentem as its Form or a
requisite, as the Greater Dream Grimoire's Rego Corpus and Rego Terram
spells have it (pp. 103-104, 109). A spell without one is refused. Only a
magus with Dream Magic may learn them.

## Hermetic Sacrifice
<!-- help: hermetic-sacrifice -->

Hermetic Sacrifice (The Mysteries Revised Edition p. 117) lets a pure,
unblemished beast sacrificed on a pagan deity's altar stand in for some of
the vis of a Ritual that summons that deity, cast via the altar. A lamb
stands for 1 pawn, up to a lion for 6. A beast created or altered by magic
is never acceptable. The deity must cooperate, since forcing the spirit
with Hermetic Synthemata spoils the altar (Errata p. 51).

<!-- tui -->
**Hermetic Sacrifice**, in More (`m`) on their record or Known Spells,
takes one of the magus's known Rituals, or a level typed.
<!-- /tui -->
<!-- gui -->
**Hermetic Sacrifice**, in Magic Outside the Lab under Raw Vis, takes one
of the magus's known Rituals, or a level typed.
<!-- /gui -->

It shows the vis still needed: a pawn a magnitude, halved with Mercurian
Magic and a third more with Waster of Vis, less the sacrifice, never below
0. **Pay the vis still needed from** takes the rest from their own raw vis
(the default), or their laboratory's or the covenant's stores. It's of the
Ritual's Technique unless **Of** names another Art. Save is refused when
there isn't enough. Choose **Not now** to pay it by hand. Saving writes it
in their Diary.

## An Artist's Career
<!-- help: artist-career -->

An artist's Artist Reputation is named for their Craft or Profession, such
as a painter's "Painting". It rises as an Ability does, by its own
experience only (Art & Academe pp. 126-127).

The app keeps one Reputation per trade. An artist's Artist Reputation and
a craftsman's (Craft) Reputation (City & Guild p. 74) are the same score,
and both books' experience feeds it:

- Art & Academe's: a piece over three times the Reputation, a patron, a
  muse
- City & Guild's: a Workshop Total 6 over the Craft Level, a wondrous
  item, shoddy goods

Neither book says they're one Reputation. Merging them is the app's
reading, and it lets workshop seasons raise a score that Art & Academe
raises by an artist's own deeds only.

<!-- tui -->
More (`m`) offers **An Artist's Career**, which rolls or records what
happens between the artist's seasons.
<!-- /tui -->
<!-- gui -->
**An Artist's Career**, in A Season's Work under This Season on the
Planning chapter, rolls or records what happens between the artist's
seasons.
<!-- /gui -->

Each is written in the artist's Diary.

- **Seek a sponsor**, a season's work: Communication + Bargain + Artist
  Reputation + a stress die against 12 (p. 131).
  - The Ease Factor is -3 for a benefactor's single piece, +3 for their
    second, +6 past two, and +9 to make them a patron.
  - It's +3 or +6 for the sponsor's Minor or Major Social Virtue, and +
    their highest business or social Reputation.
  - Asking the same sponsor again adds +3. Picking them first with
    Perception + Folk Ken against 12 adds +3, and a botch there picks the
    wrong one.

  A new benefactor is 3 xp in the Reputation, a patron 6. At Reputation 4
  the artist needs a sponsor of Reputation 2. At 6 the sponsor also needs
  a Minor Social Status Virtue, or Wealthy, or a Major one. From 8 only a
  patron with a Major Social Status Virtue and Wealthy, or a Reputation of
  4, will do. A character sponsoring the artist pays at least a Mythic
  Pound per point of their Reputation for a season's piece.
- **Perform in trying conditions**, such as before a king or in the rain:
  Communication or Dexterity + Profession + a stress die, against the
  piece's Aesthetic Quality / 2 (p. 125).
- **Keep a sponsor** after a season off the piece: on a simple die of 6 or
  more the sponsor leaves (p. 131).
- **A deed**: the gains and losses of p. 126, such as a patron lost -12,
  barred from a society -15, or signing without Reputation 8 -10. From
  Reputation 10 the artist loses none.

The inspector shows what their Reputation brings (pp. 126-129):

- from 6, +1 per point over 5 to social rolls their renown sways
- at 7 a minor muse watches them, and at 9 a major one
- at 8 they sign their work and gain a Confidence point
- at 10 every piece gains +3 and no xp is lost
- at 11 their muse takes them, a legendary artist of Might twice their
  best Craft or Profession

A muse's bond gives 1 Warping Point a year, or 3 for a major muse.

## A Scholar's Career
<!-- help: scholar-career -->

<!-- tui -->
More (`m`) offers **A Scholar's Career**, which rolls or records a
scholar's steps between their seasons.
<!-- /tui -->
<!-- gui -->
**A Scholar's Career**, in A Season's Work under This Season on the
Planning chapter, rolls or records a scholar's steps between their
seasons.
<!-- /gui -->

Each is written in the scholar's Diary.

- **Seek a place at a school**: the parent's or the scholar's own Presence
  + Bargain, Charm or Guile + a stress die, against the school's Ease
  Factor (Art & Academe pp. 81-87).
  - 6 for a rural parish school
  - 9 for an urban parish or monastic school, or a citizen's urban school
  - 12 for a cathedral school or a foreigner's urban school

  Intrigue serves too, except for a parish school. Those other schools
  take off the scholar's highest Bad Reputation. A wealthy family's gift
  adds +1 to +3. A failure may try again next year, and a botch never with
  that teacher. The inspector shows what the school teaches and to what
  score (the Limits of Education, p. 79), and a year's fees. Acceptance is
  1 xp toward their Good Academic Reputation.
- **A deed for the Academic Reputation** (p. 103):
  - **Good, 1 xp each**: a summa at half their score, a tractatus, two
    lecture commentaries, a translation into Latin, raising Artes
    Liberales, Philosophiae, Theology or Law, a gloss of a text a school
    teaches, acceptance as a student, or a teaching or church post.
  - **Bad, 5 xp**: being forced out of a post, no summa in five years, a
    benefice lost, or immoral deeds.
  - **Bad, 10 xp**: a clerical position lost.
  - **Bad, 1 xp**: no tractatus or commentary in two years, or a year with
    no Good xp.

  Against another faith, the xp is doubled (p. 88). Name the Reputation,
  or the xp goes to their highest of that side, a new one if they have
  none (see [Reputations](help:section-reputations)). Hermetic Arts earn
  none.

## Byzantine Customs
<!-- help: theban-customs -->

<!-- tui -->
With The Sundered Eagle in play, More (`m`) on a person's record offers the
Theban Tribunal's customs.
<!-- /tui -->
<!-- gui -->
With The Sundered Eagle in play, the Theban Tribunal's customs are spread
by what they are. Hermetic Letter and Invoke a Broken Oath are in the
[Deeds chapter](help:tab-deeds) under Tribunal & Order. Make Greek Fire,
which takes a season, is in A Season's Work on the Planning chapter. Paint
an Icon, Venerate an Icon and A Mother's Curse are in the Religion
chapter's Faith.
<!-- /gui -->

- **Hermetic Letter**: a letter in the Theban magi's rhetorical style, a
  far-fetched tale of the writer's patron standing for their covenant and
  the letter's purpose (The Sundered Eagle p. 44). Composing one takes a
  day, with Communication + a Lore + a simple die against 6 for a plain
  message, more for a subtler one. Reading its purpose is Intelligence + a
  Lore against the same. Nothing is kept.
- **Invoke a Broken Oath**: made by the injured party, back where the oath
  was sworn (p. 48). It's Communication + Charm + a simple die, +6 if Styx
  was named in the oath, against 15 + a simple die. Heard, the spirit that
  witnessed the oath punishes the oath-breaker with a Flaw. It's a Minor
  one, or a Major one from an entity of Might 40 or more. Choose the
  oath-breaker and a malediction, and a heard oath lays it on their sheet.
  Leave it blank and the storyguide decides. The book's maledictions are
  in the catalog:
  - **Lesser**: Ashen Food, Mephitic Odor and Rotting Clothes
  - **Greater**: Toad of Lies, Opening Wounds and Breaking Tools

  Both Diaries record it.
- **Make Greek Fire**: a season making Greek Fire, an alchemical reagent of
  level 15 (p. 47; Art & Academe p. 76). A stress die matters only if it
  botches. It has a botch die for each dose being made, less the
  laboratory's Safety, prefilled from the maker's own laboratory. A botch
  is an explosion. The form shows the hand-held siphon's figures, and the
  Diary records the batch.
- **Paint an Icon**: someone in Holy Orders with Theology: Christian 3 or
  more paints an eikon (pp. 133-134). Holy Orders means Priest, Eastern
  Priest, Brother Chaplain or Senior Clergy. They're the ordained male
  clergy, sub-deacon and up (DE pp. 74, 500), so a monk counts only when
  he's also a priest, and a nun never. The Aesthetic Quality is Dexterity
  + Craft: Painting, plus these (Art & Academe p. 124):
  - +1 for each season of Standard gilding or bejewelling, +3 for each
    Excellent result
  - the painter's Pious trait, if the saint is their patron
  - other bonuses

  The icon goes on the chosen church's Relics, and in the painter's Diary.
  Plan the painting itself as a season's Create a work of art.
- **Venerate an Icon**: an eikon venerated adds its Aesthetic Quality / 5,
  rounded up, to invoking its saint (see [Devotion](help:devotion)), or
  God's aid for an icon of Christ (pp. 133-134). Veneration takes an hour of
  contemplation. In an
  emergency it takes a Fatigue level and Presence + Concentration + a
  stress die against 15. The saint's miracle comes when the saint decides.
- **A Mother's Curse**: any Mediterranean mother may curse her child, for
  a good reason (p. 136). It's the Lesser Malediction: A Mother's Curse, -3
  to every roll in one military, academic or professional area of the
  child's expertise. The Diary records her and the task that lifts it.
  Only that task done, or divine intervention, lifts it, so remove the Flaw
  then.

## Devotion and the Saints
<!-- help: devotion -->

<!-- tui -->
More (`m`) in the Faith section of a Christian's
[Religion tab](help:tab-religion) offers invoking the saints, and with The
Church in play, Devotions and acts of piety:
<!-- /tui -->
<!-- gui -->
The Faith section of a Christian's [Religion chapter](help:tab-religion)
offers invoking the saints, and with The Church in play, Devotions and
acts of piety:
<!-- /gui -->

- **Invoke a Saint**, with Realms of Power: The Divine, The Church, The
  Sundered Eagle, The Contested Isle or The Cradle and the Crescent in
  play. It's a heartfelt request for a miracle, once a day (RoP: The
  Divine p. 87). Roll Communication + Charm + the modifiers + a simple die,
  against 15 + the storyguide's simple die.
  - **Modifiers**: at the saint's tomb +1, a Divine aura its level, the
    feast day +3, a pilgrimage in the saint's honour within the year +2, a
    donation now +1 to +3 or none within a year -3, imminent peril +2, True
    Faith +1 a point of Score. Unchristian acts this month are -1 to -3, a
    miracle this month -20, and a saint who isn't their patron -15.
  - **No -15** for their patron saint, a saint they have a Devotion Point
    toward, or the Blessed Virgin, whom anyone may ask. Nor for a saint
    whose concern is the matter at hand or a sacramental's (The Church p.
    13), or while holding the saint's own relic (The Church p. 13). Nor for
    one of Irish birth asking Saints Patrick, Brigid and Columba (The
    Contested Isle p. 134).
  - **With The Church in play**, their Devotion score to the saint is
    added, and a season's fast +1 (The Church p. 12).
  - **A relic**: choose one of the churches' Relics, or their own, the
    relic they rely on (on Biographical Detail). With The Church in play,
    the saint's own relic adds +2 for each Faith Point, once a day. That's
    for the one who tends or carries it, or after a day's veneration at its
    shrine with the custodians' leave (The Church p. 13). Another saint's
    relic, or any relic without The Church, adds +1 for touching it (RoP:
    The Divine p. 87). The relic counts once.
  - **With The Sundered Eagle**, an eikon of the saint they venerated adds
    its Aesthetic Quality / 5 (p. 133).

  The inspector shows the chance, the saint's Might, feast and powers as
  the books give them, and the miracle asked. Heard, the saint works a
  miracle. Refused, they may ask again tomorrow. The Diary records it.
  With The Cradle and the Crescent, a Mazdean yazata is invoked the same
  way, by one ritually pure through the Nahn rite (p. 85).
- **Threaten a Saint** (RoP: The Divine pp. 87-88): the humiliation of a
  saint who has refused an invocation. It's offered only while a saint who
  refused them is on record, from an invocation the saint didn't answer.
  The Faith section lists those under **Refused him**, and only such a
  saint may be chosen. A threat, or a later miracle from the saint, takes
  them off the list.
  - **The roll**: Presence + Leadership + the threats + a stress die,
    against 9 + a fifth of the saint's Divine Might.
  - **Threats**: exposing the bones +1, defiling the relics +2, berating
    the saint before others +1, barring others from the saint +3, imminent
    peril +1. A miracle this month is -20, and an unfamiliar saint -15.
  - **Might**: Mary 100, greater saints 75, area saints 50, local saints
    25 (p. 89). The book's Mights are all multiples of 5. A custom one that
    isn't is rounded down, which is the app's choice, not the book's.

  Confidence may be spent at +3 each, but Faith Points may not. Succeed,
  and the miracle comes at once. Fail, and the saint hears none of the
  petitioner's prayers for a month. Fail by 10 or more, and it's a minor
  curse and nothing for a season. Botch, and it's the saint's curse. A
  yazata is never threatened.
- **Patron Saint**: the saint they call on as their own, without the -15
  for an unfamiliar saint. It's often their church's, home's or trade's,
  or one they're devoted to. Anyone may have one, Pious or not, and
  **(none)** clears it (The Church p. 13; RoP: The Divine p. 87). The
  Diary records the change.
- **Devotion Points** (The Church): offered only to one who holds a
  Devotion, or has a positive Pious trait or the Pious Flaw to begin one.
  A Devotion is a reverence for a saint or the Virgin. It rises as an
  Ability does, on Devotion Points alone, never experience, and has no
  Specialty (p. 12).
  - **At creation**, a character with a positive Pious trait has as many
    Devotion Points, among as many saints. The Pious Flaw counts 3, and its
    Major form 6. Later changes to Pious change nothing (p. 13).
  - **In play**, Devotion Points come from these (pp. 14-15):
    - a season of personal devotion at a shrine, 5
    - endowing a church to the saint, 5 to 50
    - joining the saint's guild 3, and rising in it 2 each
    - visiting the tomb, a relic or a site of the saint's miracles, 1 to
      10
    - sponsoring art of the saint, its Aesthetic Quality
    - a hagiography, its Quality / 2, or 1 for a general one
    - furthering the saint's cultus, the Petitioning Ease Factor
    - witnessing the saint's miracle, 5 to 10
    - the feast's procession, 1 to 5
    - a pilgrimage in the saint's honour, or a vision from the saint, 1

  Neglecting the feast day loses at least 3 (p. 14). Planning and the
  Faith section of Religion list their patron and their Devotions.
- **Indulgence, Vigil or Fast** (The Church pp. 11-12):
  - An indulgence shortens a penance but doesn't forgive. It costs about 6
    pennies a season for the poor, a pound or more for the wealthy. After
    a season of charitable works it gives as many experience points in
    Reputation: Piety as the seasons, and a temporary Faith Point.
  - A vigil, the night before an important event in prayer, costs a
    Fatigue level until a full night's sleep. It gives a Confidence Point
    to spend the next day on the task named.
  - A season's fast gives +1 to invoking a saint that season, and Invoke a
    Saint ticks it. It costs a Fatigue level all season.

## Confidence through Sin
<!-- help: confidence-through-sin -->

Sin feeds the sinner's resolve (Realms of Power: The Infernal, Gaining
Confidence through Sin, p. 24). Choose a Personality Trait or Personality
Flaw with a penchant for one of the seven deadly sins, and how they sin:

- **A season indulging it** at every chance, alongside their other work,
  gives a Confidence Point at the season's end.
- **A short ceremony** of a ritualized sin gives a Confidence Point and an
  Infernal Warping Point.

**Save** adds the point, and a ceremony's Warping Point counted as
Infernal, and writes it in the Diary.

A trait counts toward a sin by the table on p. 21. Each sin has its
opposing virtue and five traits on either side (Proud/Loyal,
Wrathful/Calm, Envious/Kind, Slothful/Brave, Lustful/Wise, Greedy/Strong,
Avaricious/Just). Name the sin in brackets to say which a trait serves, as
in "Cruel (Envious)". "Dedicated (Loyal)" counts as Proud at minus its
score.

A Minor Personality Flaw counts as a +3 trait, and a Major one as +6
(p. 24), when its name is on the table or among p. 17's sinful Flaws.
Hatred counts as Wrathful. Delusion, Obsessed, Compulsion and Weak-Willed
count only when the detail typed for the Flaw names a sin or its trait,
alone or in brackets, as in "Gold (Greedy)". Which sin those Flaws serve
is the app's reading, since p. 17 names them without one. A trait of +3 or
less is fed by venial sins. Above that the act must usually be a mortal
sin.

One with no Confidence Score still gains the points. They may spend them
on influence or tarnish, or with the storyguide's leave for +1 a point on a
fitting roll, no more on one roll than the trait's score.

The inspector also says what redemption would cost. Repentance removes the
mark of sin at any time, by confession and penance or a fast of atonement
(p. 22). But absolution takes a False Power Flaw with the Virtue it
changes (p. 89). It also takes the False Gift, with every Supernatural
Ability learned through it, the Hermetic Arts included (p. 124).

## Infernal Influence
<!-- help: infernal-influence -->

Leading others into temptation, or tarnishing an Infernal aura (Realms of
Power: The Infernal, Infernal Influence and Tarnish, pp. 23-24).

- **A person** who follows the character's lead: a simple die + Presence +
  Leadership. 9 gives the new trait +1, 12 +2, 15 +3, 18 +4, 21 +5 and 24
  +6. Only the willing are touched. Strangers are touched only by one with
  Inspirational, or within their Temporal Influence. A trait from personal
  influence lingers up to a year, and from a ceremony about a week.
- **An Infernal aura**: the same total on a stress die gives the aura a
  tarnish. It's added to similar traits of everyone inside, taken from
  opposing ones, and gained as a trait by anyone with neither. Only the
  strongest tarnish counts. A ceremonial one falls by 1 each morning, and a
  personal one at each season's end. A botch brings Warping Points or
  Fatigue.

**Personal** influence is a season in company. **Ceremonial** is a short
ceremony that needs Infernal Lore 1 and spends a Confidence Point.
**Roll** rolls it, spends a ceremony's point and writes the result in the
Diary.

## Mystic Paths
<!-- help: mystic-path -->

<!-- tui -->
More (`m`) in the Faith section of a Christian's
[Religion tab](help:tab-religion) offers, with The Church in play, their
**Mystic Path**. It's there once they're Pious and tied to the Divine, or
already on a path. On that path it also offers **Spiritual Path** or
**Monistic Revelation**.
<!-- /tui -->
<!-- gui -->
The Faith section of a Christian's [Religion chapter](help:tab-religion)
offers, with The Church in play, their **Mystic Path**. It's there once
they're Pious and tied to the Divine, or already on a path. On that path
it also offers **Spiritual Path** or **Monistic Revelation**.
<!-- /gui -->

- **Mystic Path** (The Church pp. 19-24): contemplative mysticism, the
  imitation of Christ, or monistic mysticism, the self lost in God. Only
  one at a time.
  - **Who may.** Both need a positive Pious trait and a tie to the Divine
    (p. 21). The tie is True Faith, a Divine Supernatural Ability, or
    Warping from a Divine source. A Divine Ability is Sense Holiness and
    Unholiness, a Holy Method or Power, or another of Realms of Power: The
    Divine's. A contemplative has no sinful trait (Realms of Power: The
    Divine p. 40). A monist has Visions or True Faith (p. 23).
  - **Warping.** A mystic's Warping is always the Divine Ascent, magus or
    not (pp. 21, 23). A contemplative's comes at 2 Warping Points from one
    event, its form the Divine Form. A monist's comes at a single point,
    its form the Divine Gloom. After the first Ascent the path can't be
    left, and its form stays for life.
  - **The Divine Form** adds the Warping Score to True Faith's Magic
    Resistance. It gives Soak of that Resistance / 5, or of the Warping
    Score / 5 without True Faith, both on the sheet. The inspector shows
    its Penetration, Warping Score + 5 x True Faith, and the botch dice an
    impious act adds, 3 x Warping Score.
  - **The Divine Gloom** makes each Warping Point gained an experience
    point among Dominion Lore and the mystic's Holy Abilities. It also
    takes one from mundane Abilities, never Concentration, and the Diary
    says so. A monist's season practising a Holy Ability is worth their
    Concentration, so type it as the season's Source Quality.
  - **True Faith** brings more, which the inspector shows (p. 23). At 2,
    Premonitions and a Faith Point to dispel any illusion or glamour. At 3,
    double Magic Resistance against Mentem and +6 for each Faith Point
    spent. At 5, an Empyreal aura to Voice range.
- **Spiritual Path** (a contemplative's, p. 22): begin a path to a
  Revelation, which is a Virtue, never True Faith. A Minor Holy Method,
  Power or Supernatural Ability has a Path Total of 15, another Minor
  Virtue 18, a Major Holy one 27 and another Major Virtue 30. Quest
  Components must reach the Path Total itself, and their Pious isn't taken
  off it.
  - **Seasons** are planned on This Season. Service is +1, and devotion +1
    with a Devotion Point toward the saint in the plan's details or their
    patron. Preaching is +3 once on a path, and a mission to heretics or
    infidels +9.
  - **The rest** are kept here. A minor pilgrimage for nothing else is +6,
    as is a Vow, which adds the Minor Flaw, or a quest. Error or
    corruption revealed and put right is +9. So is their wealth given as
    alms, which takes away Wealthy or gives Poor, or a year on crusade,
    with its temporary Faith Point (p. 19).

  Once it's reached, claim the Revelation. The Virtue is theirs, its
  Supernatural Ability at 1, with no penalty for their other Abilities or
  Arts.
- **Monistic Revelation** (a monist's, after an Ascent, p. 24):
  Intelligence + Concentration + stress die against their Warping Score +
  stress die, with no botch. The inspector shows the chance. Failing, the
  Gloom comes as usual. Succeeding, they also choose one of these:
  - no mundane experience lost to this Gloom
  - a Minor Virtue (3 or more Warping Points) or a Major one (5 or more),
    the first always Second Sight
  - at 7 or more, Dominion Lore in place of Magic or Faerie Lore, a realm
    each time
  - after both, Infernal Lore

## Spiritual Path
<!-- help: spiritual-path -->

A contemplative mystic's path to a Revelation (The Church p. 22). Begin
one, count a Quest Component done in a story, or claim the Revelation once
the Path Total is reached. A season's components are planned on This
Season. The rules are in [Mystic Paths](help:mystic-path).

## Monistic Revelation
<!-- help: monistic-revelation -->

After a Divine Ascent, a monist may try to integrate a Revelation (The
Church p. 24). Type the Warping Points the Ascent brought, those that set
it off and its margin, and what the Revelation brings. The Diary records
it. The roll and what each Revelation needs are in
[Mystic Paths](help:mystic-path).

## Holy Influence
<!-- help: holy-influence -->

Leading others to virtue, or tempering a Divine aura (Realms of Power: The
Divine, Holy Influence and Tempers, pp. 38-41). It's offered to a
Christian, Jew or Muslim of holy standing,
<!-- tui -->
in More on the character's sheet.
<!-- /tui -->
<!-- gui -->
in the Faith section of [Religion](help:tab-religion).
<!-- /gui -->
Holy standing is clergy, a monk, True Faith, Temporal Influence,
Inspirational, or Dominion Lore. A rabbi has it over their community
(p. 125).

- **Those in their care**: a simple die + Presence + Leadership. 9 gives
  the new trait +1, 15 +2, and 24 +3, the most. The one leading needs
  spiritual authority over them, such as a priest's parish, a parent's
  child, a teacher's pupil or a host's guests. Those led must be willing.
  - Temporal Influence serves only personal influence, on those under
    their temporal authority.
  - Inspirational lets them influence anyone willing, by a ceremony.
  - A trait from personal influence lasts up to a year, and from a
    ceremony rarely a week.
  - One set against a Personality Flaw never becomes lasting. A Minor
    Flaw counts as +3, a Major as +6.
- **A Divine aura**: the same total on a stress die gives the aura a
  temper. The tempers are Loyal against Pride, Calm against Wrath, Kind
  against Envy, Brave against Sloth, Wise against Lust, Strong against
  Greed and Just against Avarice.
  It's added to every roll in the aura that suits it, and taken from every
  roll against it. It falls by 1 each day if ceremonial, or each season if
  personal. One leader holds one temper at a time, and a new one replaces
  their last. Two leaders' tempers in one aura are schism, where an action
  may take both a bonus and a penalty (p. 41). A botch brings Warping,
  Fatigue or a bad name.

**Personal** influence is a season among them. **Ceremonial** is a short
ceremony that spends a Faith Point (with True Faith) or a Confidence
Point, which adds nothing to the roll. A group praying with the leader
adds its modifier. That's everyone's Ceremony less their number, and each
one's Presence + Leadership (p. 36). **Roll** rolls it, spends a
ceremony's point and writes the result in the Diary.

## Invoking God's Aid
<!-- help: gods-aid -->

With Realms of Power: The Divine in play, the Faith section of a
Christian's, Jew's or Muslim's [Religion](help:tab-religion) offers Invoke
God's Aid (pp. 41-42). It takes a short prayer and a Confidence Point, or
a Faith Point with True Faith. A grog can't invoke it, nor can one with
Low Self-Esteem, unless they have True Faith (p. 41).

The roll is a stress die + Communication + Dominion Lore. 9 gives +1, 15
+2, and 24 +3, to every roll in the scene clearly made toward the aim
named, spellcasting too. It lasts until one fails or the scene ends. A 0
rolls three botch dice, and a botch is divine disfavour: struck dumb,
blind or clumsy until penance.

Tick **For his followers too** to ask it for those in the character's
spiritual care, and they and the one praying gain the bonus. With the
Ceremony Ability the one praying leads them, adding it and each one's
Communication + Dominion Lore.

**In battle**, God's aid is asked only against infidels or heretics, as
the one praying sees them, or a supernatural menace not of the Divine. A
Trained Group adds a member's bonus to its combat bonus beyond the usual
limit. Only the highest counts, and it's lost when the group fails a roll
or splits (p. 42). The inspector shows each bonus's chance, and the Diary
records the prayer.

## Font of Knowledge
<!-- help: font-of-knowledge -->

<!-- tui -->
More (`m`) offers it on one with Font of Knowledge (DE p. 165; Antagonists
p. 109).
<!-- /tui -->
<!-- gui -->
It's in the [Deeds chapter](help:tab-deeds) under Insight, for one with
Font of Knowledge (DE p. 165; Antagonists p. 109).
<!-- /gui -->

The roll is Intelligence + Font of Knowledge + stress die, against 6 + 3
for each time they've drawn on it today, failures counted. Succeeding,
they attempt a task with the Ability they lack as if they had it at 2.
Name the Ability, and how often they've drawn on it today. The inspector
shows the chance, and the Diary the roll.

## Commanding Aura
<!-- help: commanding-aura -->

<!-- tui -->
More (`m`) offers **Commanding Aura** on one with a Church office or crown
(Biographical Detail), or the Commanding Aura Virtue.
<!-- /tui -->
<!-- gui -->
**Commanding Aura** is beside Health's buttons, for one with a Church
office or crown, or the Commanding Aura Virtue.
<!-- /gui -->

It shows the office's Magic Resistance, its Soak (a fifth of it), and an
Aura of Rightful Authority to Voice range, Penetration 0 (DE pp. 74, 420).
Tick **Withdrawn until penance** for a legatus missus who delays or strays
from their mission, or one God's will excommunicates. The office then
gives no Magic Resistance or Soak until it's unticked. A legatus missus
loses the aura for good when the mission is done (DE p. 74; Antagonists
p. 38).

## Ars Goetia
<!-- help: ars-goetia -->

The total of a Goetic Art against a spirit's Might (Realms of Power: The
Infernal, Chapter Eleven: Ars Goetia, pp. 114-119). **Close** keeps
nothing. **Roll** rolls it once and says what it did, also keeping
nothing, so apply what it gives by hand.

Every total is a stress die + a Characteristic + the Art + the Lore of the
spirit's realm + the aura + Penetration x its multiplier, so it's its own
Penetration. A demon's True Name is an indefinite Arcane Connection.
Against a demon, the sorcerer adds their own Hierarchy x 5, their highest
Infernal Reputation, to the total. The target adds the demon's Hierarchy x
5 (p. 114). A sacrifice adds +2 to +10.

- **Summoning** (Presence): twice the spirit's Might holds it in the
  circle until dismissed, or the next midday or midnight. Its Might alone
  calls it only while the summoner concentrates. It always costs a Fatigue
  level.
- **Scouring** (Summoning at large): Area Lore, with Penetration not
  multiplied. Whatever answers has about half the total's Might.
- **Ablating** (Stamina): must exceed the spirit's Might, or twice it
  outside a circle. The margin comes off its Might, no more than all of it.
  A fifth, rounded down, are Ablation Points for Confidence,
  Characteristics, healing, a Longevity bonus, insight, experience,
  Infernal Might, a Power or Infernal vis. The sorcerer also gains as much
  Infernal Reputation experience, and a Warping Point.
- **Binding** (Intelligence) and **Commanding** (Communication): exceed
  its Might in a circle, or twice it outside one. A spirit that agrees
  needs only no botch, or outside a circle only its Might exceeded. A bound
  spirit lends its Might as Magic Resistance and holds Might x 5 spell
  levels. A command lasts until midday or midnight.

A magus who holds a Goetic Art may use Rego for it and Vim for the Lore
(p. 124), and the total uses whichever is higher. Summoning may work as a
Magic or Faerie Power for the aura. The other Arts are always Infernal.

## Spirits and Names
<!-- help: spirits-and-names -->

The figures of a Mystery of spirit magic or theurgy (The Mysteries Revised
Edition, Chapters Eight and Nine, pp. 64-88). Pick the **Working**, and the
inspector says what it comes to. The spirit's Might and the other figures
are the storyguide's, and the sheet never knows them. **Close** keeps
nothing. **Roll** rolls where the book asks for a die, such as intuiting or
researching synthemata or the ascending hierarch's Stamina. Otherwise it
repeats the figures. Nothing is kept, so apply what it gives by hand.

- **Invoke the Spirit of (spell)** (Hermetic Theurgy, pp. 78-80): the
  spirit's Might must at least equal the power's level, and is the Invoke
  spell's base level. Levels added for Penetration give +2 each. The
  spirit casts at its Might + the aura, with no die, and succeeds at the
  level less 10. That's a magnitude more or less when the magus varies
  Range, Duration or Target. Its Penetration is that total less the level,
  plus the Invoke spell's bonus.
- **Invoke the Spirit of (Form)** (p. 80): the spirit casts as Spontaneous
  magic at (Might + aura) / 2, rounded up.
- **Invoke the Pact of (Daimon)** (pp. 80-81): each casting that
  penetrates gathers its level less the Daimon's Might. The Aspect comes
  when they reach its Might, or at once at twice its Might, the only way
  without Hermetic Theurgy. The Ritual's vis is also the Daimon Points the
  Daimon gains (p. 85).
- **Invent a theurgic spell** (p. 79): Technique + Form + Intelligence +
  Magic Theory + aura + Realm Lore + Names of Power.
- **Names of Power** (pp. 76-78): each is a Muto Vim spell of level 5 x its
  bonus. Together they never add more than Magic Theory (Errata p. 50).
- **Research Hermetic Synthemata** (pp. 86-87): Muto + Vim + Intelligence
  + Realm Lore + aura + an Arcane Connection's multiplier. Each season adds
  the Lab Total less the level and the name hiding, about Might / 2. The
  spell is at least the being's Might, 5 more for the Lasting version. It
  adds its level to Penetration against the being, or the Lasting
  version's level less 5.
- **Intuit Synthemata** and **Research Synthemata by fasting** (Synthemata
  Magia, pp. 87-88): Perception + Realm Lore + the magus's aura, against
  the being's Might + its aura + name hiding. The season's research adds an
  Arcane Connection's multiplier and ignores the being's aura.
- **Power Ritual effects** (Hermetic Empowerment, pp. 64-66): each use
  drains the Ritual's level / 5, rounded up, from the bound spirit's Might
  Score for good. The Might x 2 must reach the level (Errata p. 50). The
  Empowering Prison's base level is at least twice the spirit's Might.
- **Bond a spirit familiar** (pp. 66-69, 81-82): Technique + Form +
  Intelligence + Magic Theory + the worse of the magus's and the spirit's
  aura, against Might + 25. It takes a pawn of vis per 5 of the Lab Total.
  Might / 5 points buy its Intelligence, Perception and Communication. A
  Daimon first takes Might / 5 pawns, and may scorn a bond of Technique +
  Form under twice its Might.
- **Blending with Substance** (Inscription on the Soul, p. 70): the item's
  best bonus plus half the rest, x 5, is the effect's level. It costs a
  Warping Point, or two at level 30 or more.
- **The Living Ghost** (pp. 70-74): the magus's transformation limit is
  their best Technique + Form, and a Magical Focus doubles the lower. Bind
  the Living Ghost is level 30 + the Haunt's Size levels. The
  Transformation is at least the limit, and the magus's Might is its level
  less the Haunt's levels.
- **Ascendancy to the Hall of Heroes** (pp. 82-86): the Ascendant Form is
  at least their best Technique + Form, and 40. Its level / 2 is their
  Might. Each Transformation that penetrates gives its level less the
  Form's, against the Form's level + 3 x their negative Characteristics'
  cost + 5 x Decrepitude + 5 x their Flaw points if they outweigh their
  Virtues'. They roll Stamina against 9 or pass out.

## Ars Fabulosa
<!-- help: ars-fabulosa -->

A summoner's bargaining powers (Realms of Power: Faerie pp. 131-134). They're offered to anyone who holds (Faerie) Summoning, Bonding, Captivating or Dismissing, on their record or with their tradition's magic.

- **The total** is the power + its Characteristic + Faerie Rank + the aura (a Faerie power) + a stress die, and costs a Fatigue level. Summoning uses Presence, Bonding Communication, Captivating Perception and Dismissing Intelligence.
- **Sympathy Traits.** Tick the ones that fit the faerie. Together, negatives counted by their size, they set the most Might the power can touch, or for Dismissing the effect level. That's 5 for each point of all of them added together. Only the single highest adds to Penetration. The book says "highest" without saying how a negative Trait ranks, so the app takes it by its size. That's the app's reading, not a printed rule.
- **Summoning** holds the faerie only when the total equals or beats its Might, even a random faerie called at large. The faerie must then listen, and can't harm the summoner. Only a faerie the summoner has an Arcane Connection to must also be penetrated (p. 132). One called at large needn't be (p. 133). A botch brings a faerie all the same, hostile or unbound.
- **Bonding and Captivating** must exceed the faerie's Might and penetrate its Magic Resistance, which is its Might. A faerie held by the summoner's Summoning counts as level 0 for Penetration.
- **Dismissing** cancels an effect, ends one on a being, or frees a being from an agreement. Several in a round take 6 off each beyond the first. Deflecting a power first needs Quickness + Finesse against its Initiative.
- **Experience.** A 1 on the die gives each ticked Trait an experience point, and each botch die's 0 takes one, beyond the Warping limit. A negative Trait works the other way round, a botch deepening the penalty and a 1 lessening it (p. 103). Raising a negative Trait costs 10 xp from -1 to 0, 15 from -2, 20 from -3. Losing a point with none banked lowers the Trait a step. The book doesn't say, so that's the app's assumption. The roll goes into the Diary.

## A Faerie Bargain
<!-- help: faerie-bargain -->

How a bargain made in a summoning ended (RoP: Faerie pp. 132-133).

- A bargain struck gives the fitting Sympathy Trait an experience point, and none struck takes one away. The bargain binds the faerie whatever the summoner does.
- A deadlock may be settled by a contested roll. The summoner rolls Communication + Bargain + Faerie Rank against the faerie's, and may use a fitting Trait as Bargain's specialty. The book gives no rule for a tie, so the app's assumption is that a tie strikes no bargain.
- Working out first what an unknown faerie wants is Intelligence + Faerie Lore against 12 or more, on a simple die.
- A Sympathy Trait used as a specialty on either roll makes it a stress die that may botch. A botch gives Warping Points, and the die's 1 or its botch moves the Trait's experience (pp. 102-103).
- A summoner who breaks a bargain made in a summoning gains a -3 Sympathy Trait fitting the faerie, and may lose Faerie Rank. Dismissing can free the faerie instead (p. 134). It's kept in the Diary.

## An Offer to Faerie
<!-- help: faerie-offer -->

In the Faerie Realm, a character with an unspent fable point may bargain with the Realm itself to change one element of the story (RoP: Faerie pp. 25-29).

- **Fable.** The first fable point makes a fable score of 1, and raising it costs the score + 1 points. A point spent adds the score to one roll. It's all lost on leaving Faerie, so the form takes the score as it stands.
- **Offer Total.** Communication + Charm, a Profession, a Craft or Music, + the goods or a Virtue, + the promise (-6 to +3), + the change (+3 to -6), + a stress die. Only the highest of the goods or Virtue counts: Free Expression +3, a Puissant Ability, or goods +1 to +3.
- **Ease Factor.** It's the threat the change overcomes. Trivial 6, Minor 9, Serious 12, Major 15, Overwhelming 18. Elysium takes 6 off the roll, unless the offer puts its story back on track (Ease Factor 3 less).
- With Art & Academe, artistic Reputation adds 1 for each 3 or part, and a Faerie Patron's Might 1 for each 5 or part.
- It costs a fable point and a Long-Term Fatigue level whether or not it's accepted. It's kept in the Diary.

## Invest Time or Money
<!-- help: merchant-investment -->

<!-- tui -->
**Invest Time or Money**, in More (`m`) on [This Season](help:section-char-season), records what a character does with surplus Labor Points or money (City & Guild Chapter Seven).
<!-- /tui -->
<!-- gui -->
**Invest Time or Money**, in A Season's Work under This Season on the Planning chapter, opens a form for what a character does with surplus Labor Points or money (City & Guild Chapter Seven).
<!-- /gui -->

Anyone who works for Labor Points can **put money into the business**. The pounds come from the silver on Personal Gear, and buy Labor Points at the money table read the other way, 9 for a quarter of the year's income (p. 40; Errata p. 56). A trader can also invest (pp. 110-114). That's anyone with the Merchant, Merchant Adventurer, Factor, Capo, Partner or Redcap Virtue.

- **Charity.** The Labor Points given are lost. Each season's worth given, over the years, is an experience point in the Reputation you name. Having given at least 1 x the Wealth Multiplier in the past year, the trader can call a crowd of the people it helps. It's (Communication + Leadership) x that Reputation x 1 for an urban merchant, 2 for a local carrier, 3 for a merchant adventurer, 4 for a factor and 5 for a capo. A week's notice brings twice as many. This Season shows the crowd.
- **Commodity speculation.** At least 10 Labor Points are stored as goods and kept. They pay 1 a year for every 10, each Winter from the next year, with a guard for each half season's worth invested. **End an investment** takes them back, or loses them to the story events that burned the warehouse.
- **Drawings.** A sumptuous item of hand-tool size or smaller for each 1 x the Wealth Multiplier.
- **Introduction agent.** Two seasons' worth put in, three back in Winter two years on. The junior merchant owes the trader a Favor until then. Spend the season introducing them.
- **Marriage broker.** Two seasons' worth are lost. In return come an experience point in the Reputation named, Social Contacts in the couple's class for three years (unless the trader arranges another), and Favors from the couple or their parents.
- **Legal action** (p. 114). Half a season's worth a suit. Type the representative's Intelligence + Civil or Canon Law + die, and the opponent's. A true suit adds 3, a false one takes 3, an outlandish one 6. Winning, add or take 1 from one of the loser's Reputations. Losing may bring a poor Reputation, and either result may bring the Enemy Flaw.
- **Foreseeing a boom** (pp. 111-112), when the troupe's boom comes. Type Intelligence + Area Lore + the die. 18 or more gives back two seasons' Labor Points for each set aside, 15 to 17 one and a half, and 7 to 14 nothing gained. 6 or less loses 2 of every 10, and a botch destroys the business.

Each kind of merchant has investments of its own, also open to the richer kinds:

- A local carrier's **season smuggling**, (Intelligence + Intrigue) x the Wealth Multiplier (p. 117), or **sponsoring smugglers**, a season's worth each Winter beside their own work.
- A factor's **change of government**, (Communication + Intrigue) x the Wealth Multiplier and a minor political figure's Favor (p. 122). Or **young talent**, (Communication + Leadership) x the Wealth Multiplier and a Favor for each 10, rounded up (p. 128).
- A capo's **lavish party**, die + a Characteristic + the theme's Ability + a point a pound spent, at most their Intrigue. It gives a Favor for each 5, rounded up (p. 129), and the pounds come from their silver.

Investments that are time, not points, take a season, so plan it as a Merchant venture. Each is written in the Diary. An investment costing more than the character's Labor Points is refused.

## Command the Beast
<!-- help: command-beast -->

<!-- tui -->
On a tamed animal's sheet, **Command the Beast** in More (`m`) on its Personality Traits rolls a command.
<!-- /tui -->
<!-- gui -->
On a tamed animal's sheet, **Command the Beast** beside its Personality Traits rolls a command.
<!-- /gui -->
Choose who gives it, with Animal Handling (Ride for a mount, Magic Lore for a tamed elemental), and the task. The roll is Presence + that Ability + a stress die against the task's Ease Factor:

- none for something it has done many times
- 6 for an unusual or stressful task
- 9 for a long or new one
- 12 for one it fears
- 15 for a suicidal one.

A feared task also asks a Loyalty test, its Loyal trait + a stress die, against 6 when it has no Confidence Score. A suicidal one always asks one, against 9. A botch may make it flee, do the wrong thing or turn on its master (DE p. 386).

A tamed animal played season by season learns Abilities from anyone with Animal Handling, through **Be trained**. An animal grog has its yearly update instead. One it doesn't have yet asks a Loyalty test against 6 at the season's end, or the season is wasted (DE p. 385). In a fight, a group of tamed animals is led by its leader's Animal Handling, not their Leadership (DE p. 385).

## Reward or Punish
<!-- help: grog-discipline -->

Rewards and punishments for one of the covenfolk, as Grogs sets them out (pp. 23-25). The inspector, **What It Does**, says what a choice will do before you choose **Give**. The grog's Diary keeps it, and a punishment also goes in the covenant's Diary.

Rewards are usually set by the turb captain, steward or chamberlain, and announced before the turb.

- **Improved rations**, for a day to a year. A whole year of them is +1 to the grog's Living Conditions for that year's aging roll.
- **Pay and a Half**, for a season or more, or for good. Half the grog's Wages again go on the covenant's Wages while it lasts.
- **Improved equipment**, the grog's for good, but surrendered on demotion. Record the item on their Personal Gear.
- **Promotion in rank**: grog, custos, sergeant, then captain, chamberlain or steward. Type the rank they hold now.

Punishments, in order of severity:

1. **Castigation**: a single blow with the rod.
2. **Relegation to inferior duties**, done in the grog's free time.
3. **Reduction of rations.** A season or two of the year on them is -1 to Living Conditions for aging, three or four -2. A month counts for nothing.
4. **Flogging**: 1, 5 or 10 blows, giving 1, 2 or 3 Light Wounds and 1, 3 or 5 Long-Term Fatigue levels.
5. **Reduction in rank**, for good. The grog surrenders the equipment they were given.
6. **Whipping.** 10 lashes give a Light Wound, 30 a Medium, 50 a Heavy, and the short whip two of each. It takes a week to recover, or a day for ten lashes or fewer. Pay is docked for longer.
7. **Dismissal.** Tick **He leaves the covenant** to take the grog off its lists.
8. **Fustuarium**: beaten to death by the blindfolded turb. Few covenants have the right to order it.

What it costs in Loyalty (Covenants pp. 38-39). A fitting punishment from the turb captain, steward or chamberlain costs nothing. One a magus orders costs Loyalty points by what it counts as:

- a minor humiliation -1
- a public humiliation -3
- restraint -6
- infliction of pain -9
- a brutal punishment -12
- a brutal one the magus clearly enjoys -15.

With a positive Prevailing Loyalty, only an unjust one costs anything. **Counts as** starts at the usual row for the punishment. A blow is minor, the shaming ones public, reduced rations restraint, and a flogging, whipping or fustuarium brutal. The victim's **Reputation** among the covenfolk adds to the penalty if they're loved, and takes from it if they're disliked. A wound the magus deals in person costs its own points too (light -3, medium -6, heavy -9, death -15), one step worse by magic. The points go into the covenant Diary as a Loyalty Event, which Actions and Events adds up.

**His Loyal changes by** moves the grog's Loyal to Covenant (or Loyal) trait. The books leave it to the troupe (Grogs p. 24).

Free time, lodging and families (Grogs pp. 23, 25). A grog who doesn't sleep in their free time loses a Long-Term Fatigue level until they sleep two watches straight. Punishment duties are done in free time. Married covenfolk often have a room of their own, and covenants encourage matches among their covenfolk.

## Pension
<!-- help: grog-pension -->

A grog retires on a pension, or pays rent for their lodging instead and is fed free (Grogs p. 26). They still count as one of the covenant for its finances. On a pension their Wages are halved, and paying rent they draw none. Grogs gives a pension of half to three-quarters of pay. The Definitive Edition sets half Wages until death (p. 186), which the app uses. **Grants pensions** is the covenant's Loyalty Money modifier: +10 Loyalty points for granting pensions to all its retirees.

On a grog who has died, Pension gives the widow the pension the grog would have had. The widow becomes one more of the covenant's pensioners, at half Wages a year.

## Covers
<!-- help: section-char-covers -->

A character's other identities (Houses of Hermes: Societates pp. 87-90). The section shows for a magus of House Tytalus, a character with the Persona Ability, or anyone with one recorded. Add, edit or delete one.

- **A deep cover** is a name and role built in a community, with a Reputation there that rises as an Ability does.
  - It starts at 1 with a noteworthy act before witnesses.
  - Each season it's kept up, Advance adds 2 xp for living there or 1 for regular visits. A brief visit each season is 2 a year, so choose away and add them by hand.
  - Each staged event or tie to the community adds 1 more. More than 2 a season arouses suspicion.
  - Questioned, its Disguise roll's Ease Factor falls by the Reputation. With those it sees regularly, The Gift's penalty falls by as much.
  - A role needing a Minor Social Status Virtue costs a Minor Story Flaw's obligations. A Major one costs a Major Story Flaw's and doesn't last. One needing other Virtues can't be built.
  - Unused, it keeps its Reputation as many years as its score, then loses a point a year.
- **A persona** is a whole different person of the Persona Ability, one for each point of it.
  - Changing into one is a round's concentration and Stamina + Persona against 9.
  - Each persona has a Reputation of 1 when it's made. Every xp put into Persona after that goes to every persona's Reputation too (p. 90).

**Disguise Roll**, in More beside Covers, rolls a deep cover's Disguise roll, or a talk with someone in disguise ([Disguise Roll](help:disguise-roll)). A cover is defended when, say, a suspicious priest questions it or it covers a comrade's slip. Untick **Convincing someone of it** for the roll that first establishes it (HoH:S p. 88). The result is shown, not kept.

## Disguise Roll
<!-- help: disguise-roll -->

A deep cover's two rolls (Houses of Hermes: Societates pp. 87-88). The Definitive Edition's own disguise is an opposed roll instead, Guile against the other's Perception + Awareness (DE p. 165).

- **The Disguise roll** is Intelligence + Guile + stress die against an Ease Factor of 9 + the modifiers that apply. While the cover is defended rather than established, its Reputation comes off the Ease Factor. The modifiers are a change of social status +3, a minor alteration in appearance +1 or a major one +3, a change of sex +6, and minimal preparation +3 or none +6.
- **Talking with someone** in disguise is Presence + Guile + stress die against their Intelligence + Folk Ken + stress die. It's a social roll, so The Gift's penalty counts.

Leave a die blank to roll it. Nothing is changed, and the form shows whether the cover holds.

## Constant Effects
<!-- help: section-char-constant-effects -->

The supernatural effects the character is under all the time, or at least half of it, such as a spell kept up on them or an enchanted ring that lets them fly. Each gives a Warping Point a year, whatever its power or caster. A powerful one (sixth magnitude or more) neither cast by them nor designed for them gives one more each season, and one when it begins. Adding such an effect adds that first point at once. The app adds the year's points each Winter with the rest of their Warping, each counting as its realm for Susceptibility to Warping (DE pp. 390-391).

Don't list these here:

- a Longevity Ritual, which the app counts already
- Parma Magica, the Aegis of the Hearth or a familiar's bond, which don't warp
- an effect on something they live in rather than on them, such as a flying castle.

<!-- tui -->
`a` adds one, `e` edits the chosen one and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the row last clicked.
<!-- /gui -->
**The Effect** at the foot of its form says what it will give.

## Place Aging Points
<!-- help: aging-due -->

An aging roll of 10-12 gives an Aging Point in any Characteristic. A 13 or 22+ gives enough to reach the next Decrepitude, in any Characteristics. The player chooses where they go (DE p. 392).

- Their Decrepitude counts at once, and the Crisis is rolled with the Decrepitude they bring, whichever Characteristics take them.
- Each point is offered first in the Characteristic the roll suggests, the highest, with a choice for each point. So they can be spread over several Characteristics.
- Place them before the survival roll, since one in Stamina may lower it.
- A character who survives a disease's Crisis gains an Aging Point in a fitting Characteristic, the storyguide's choice (Art & Academe p. 47).

Until they're placed, the Aging section lists them. Advance Season asks for each one before it plays the next season, and Cancel leaves the date where it is.
<!-- tui -->
**Place Aging Points** is also in More (`m`) on the Aging section.
<!-- /tui -->
<!-- gui -->
**Place Aging Points** is also on the Aging section, beside its Edit.
<!-- /gui -->
Each point counts toward Decrepitude. Once a Characteristic's Aging Points pass its score, it falls by one, as for an aging roll.

An Aging Crisis takes the following season to recover from. An Unaging character isn't harmed by a Crisis that can't kill (DE p. 114). A leper also takes a Heavy Wound with every Crisis (DE p. 135). The Aging section warns at two points (DE p. 392):

- **Decrepitude 4**, extremely frail. A long journey, a fight or other stressful activity means a roll on the Crisis Table. This isn't for the Unaging.
- **Decrepitude 5**, bedridden and dying.

## Art & Academe's diseases
<!-- help: aa-diseases -->

With the **Art & Academe medicine** rule option (Saga Settings, with Art & Academe in play), a disease isn't a wound but its own record. It's listed under the wounds in Health with its stage, Severity, penalty, Interval and Ease Factors (Art & Academe pp. 45-51).

- **Stages.** Minor, Serious, Major and Critical give -1, -3, -5 and no action at all. A disease that gives Flaws instead has no penalty, such as the falling evil, phthisis, suffusio or worms. The penalty adds to the Wound Penalty everywhere but the disease's own rolls. Each stage moves its Severity 3.
- **Recovery** comes at the end of each Interval, played out when the season is advanced. The roll is Stamina + the physician's Medicine + Corpus / 5 (a magus) + the Wound Penalty + Recovery Modifiers + magical aid + the +3s of stable rolls + stress die.
  - Below the Stable Ease Factor, the disease worsens a stage.
  - At or over it, the next roll gets +3.
  - At or over the Improvement Ease Factor, it improves a stage, and a Minor one is cured.
  - A lifelong one never changes.
- **Surgery** (Recovery Roll, surgery) can return a disease to the stage it began at, with +3 to its next Recovery roll, at the cost of a wound (Art & Academe p. 61).
- **Crisis.** A Critical disease rolls twice a day. 0 or less dies, at or over the Stable Ease Factor it eases to Major, and anything else is -1 to later rolls (p. 47). The survivor gains an Aging Point in a Characteristic the storyguide chooses. It waits on the Aging section until placed (see [Place Aging Points](help:aging-due)).
- **Special diseases** carry their effects as notes, and the Flaws and choices they bring are yours to add. The notes cover:
  - the falling evil's convulsions and gangrene's wound that can't heal
  - the consumptive tumor's new tumors and suffusio's blindness
  - leprosy's Flaw, phthisis' Enfeebled and pneumonia's Winded
  - quinsy's Afflicted Tongue and Mute, and scrofula's Disfigured
  - worms, smallpox, phimosis and Saint Anthony's fire.
- **Sap the Life** is in the disease list. It's a vampire's power (Against the Dark p. 115) that inflicts a Serious disease of Severity 15, rolled weekly against 12 and 18. It allows no Disease Avoidance roll, since its Penetration decides, and costs two long-term Fatigue levels that come back only when it abates. Faerie Lore may treat it as Medicine does, but the app's Prognosis counts only Medicine.
- **The physician** is the covenant-mate with the most Medicine. Their Medicine counts only when their Prognosis Total is over the Severity (p. 58). That total is Intelligence + Medicine + the patient's Living Conditions + an apothecary's Profession: Apothecary and a chirurgeon's Chirurgy, at most 3 each.
- **Recovery Modifiers** are ticked on Edit Wounds. They're poor or wealthy living, a peasant's or a noble's diet, being routinely active, and no medicinal herbs (-3, less an apothecary's Profession: Apothecary). Each one also adds a botch die, to wound rolls too, and a disease's penalty slows a wound's healing (p. 54). Edit Wounds also clears a disease cured by magic, a saint or a surgeon.

## Abilities
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
**Divination** (Supernatural) is given at 1 by Divination & Augury or Hermetic Dream Interpreter. A magus with either may buy it at creation (The Mysteries Revised Edition pp. 59, 62).

Abilities from supplements are listed only while their book is in play, such as the Divine's Holy Powers and Methods, Mythic Herbalism or Mechanica of Heron. **Hedge Art** is the category for a hedge tradition's Arts, such as the learned elementalists' Elementalist Fire. Like a Supernatural Ability, one is learned through the Virtue that grants it.

Most hedge Arts, and Accelerated Abilities such as the vitkir's runes, advance on the Art XP table, so a score of 1 costs 1 XP. A Difficult Art, such as Elementalist Fire or the gruagach's Give, advances on the Ability XP table (Hedge Magic Revised Edition, Chapter 1: Difficult Arts, Accelerated Abilities). A character who belongs to a tradition sees its Arts and Abilities with the tradition's own magic, not here.

**The app works out:** the score from the XP, and the XP the next score needs, shown as score and then XP over the next total (Ars Magica Definitive Edition, Chapter 3: Characters, Advancement Table). When a Virtue or Flaw gives a fixed bonus or penalty, such as Puissant, the score used follows in brackets.

While the XP is typed, the form shows the score it buys and the total XP the next score needs ("Latin: Score 2 · Score 3 at 30 xp").

Some Abilities' details give their rules:

- **Magic Sensitivity**, **Second Sight** and **Sense Holiness and Unholiness** list the Ease Factors of what each senses (Definitive Edition pp. 168-170). Magic Sensitivity's score comes off the magus's Magic Resistance.
- **Guile** gives the Disguise roll and talking in disguise (see [Disguise Roll](help:disguise-roll)).
- **Persona** counts its identities, one a point, with the roll to take one or return and each persona's Reputation (see [Covers](help:section-char-covers)). It also says how the change shows to magic. That's a Muto Corpus 10 effect, a magnitude less each sunrise or sunset, and level 5 x Persona to other magic (DE p. 169; Societates pp. 89-90).

<!-- gui -->
Each Ability has a mark beside its name, cut like the Art symbols: a dark block with a light figure, such as a quill for every Dead Language or a shield for Parma Magica. The chosen Ability's mark is shown larger, with its engraved lines, in the panel beside the list.

The hedge traditions' Arts and Abilities have marks of their own. Each rune of the Vitkir is its Elder Futhark letter, all cut at one size, and the gruagachan's are taken from the Pictish symbol stones. The other hedge books' powers, Methods and Arts have theirs too, from the faerie rites and Goetic Arts to the Amazons' Vowels and the Hunters' Arts. An Ability the app has no mark for shows its category's.

The way to the next score is drawn as a gold line along a dotted rule, ending in a red lozenge as far as the XP reaches, with the XP over the next total after it.
<!-- /gui -->

With Art & Academe in play, a character can dispute with another
(see [Disputatio](help:disputatio)).

<!-- tui -->
On one who holds a Goetic Art, More (`m`) offers [Ars Goetia](help:ars-goetia)
from their record or their tradition's tab.
<!-- /tui -->
<!-- gui -->
**Ars Goetia**, in the [Deeds chapter](help:tab-deeds) under The Infernal, works out a
Goetic Art's total for one who holds one.
<!-- /gui -->

<!-- tui -->
On a magus with a Mystery of spirit magic or theurgy, More (`m`) offers
[Spirits and Names](help:spirits-and-names) from their record or Known Spells.
<!-- /tui -->
<!-- gui -->
**Spirits and Names**, in **Magic Outside the Lab** under Raw Vis on the Hermetic Magic chapter, works out the
figures of a Mystery of spirit magic or theurgy.
<!-- /gui -->

<!-- tui -->
With Apprentices in play, on a Gifted character More (`m`) offers
[Turbulence](help:turbulence). On an apprentice it also offers
[The Gauntlet](help:gauntlet) and [Lose the Gift](help:lose-the-gift).
<!-- /tui -->
<!-- gui -->
With Apprentices in play, **Turbulence** is in the [Deeds chapter](help:tab-deeds) under
Apprenticeship for a Gifted character, and in A Season's Work on the Planning chapter.
**The Gauntlet** and **Lose the Gift** are beside it for an apprentice.
<!-- /gui -->

**See also:** [Virtues & Flaws](help:tab-vf),
[Planning](help:tab-planning), [How the app handles advancement](help:guide-advancement)

## Disputatio
<!-- help: disputatio -->

<!-- tui -->
More (`m`) > **Disputatio**, on a character's sheet with Art & Academe in
play, stages a schoolmen's debate with another character.
<!-- /tui -->
<!-- gui -->
**Disputatio**, in the [Deeds chapter](help:tab-deeds) under Scholarly with Art & Academe
in play, stages a schoolmen's debate with another character.
<!-- /gui -->
Choose these:

- who they dispute with
- whether they're the **Opponent**, who states first, or the **Respondent**
- the **Subject**, one of Artes Liberales, Philosophiae, Theology or Civil and Canon Law. Each side uses its score in it.
- the **Kind**
- the number of the judge's **Questions**, usually 7, 9 or 12
- any Ease Factor the judge sets for the statements, such as 6 among students, 9 for baccalaureates or 12 for a candidate's examination.

The line above Dispute shows each side's totals before the die:

- **Attack**: Communication + the subject's Ability.
- **Defence**: Perception + the Ability.
- **Weakening**: Intelligence + how far the Attack beat the Defence.
- **Resistance**: Presence + the highest Academic Reputation.

Each question is an exchange. The opponent states and the respondent replies, then the respondent states and the opponent replies. A statement that beats the reply costs the other side a symbolic Fatigue level for every 5 points, or part of 5, by which its Weakening beats their Resistance, with the usual penalties. Five lose the disputatio. Otherwise the side that lost fewer wins when the questions run out. **Dispute** rolls it all and shows each exchange, and **Keep** writes it in both characters' Diaries.

Afterwards each rolls Stamina + a stress die against the number of questions. A failure costs a real Long-Term Fatigue level, and a botch one more for each 0. Keep takes these off their Fatigue.

The winner of an epideictic or deliberative disputatio gains an experience point toward a Good Academic Reputation, or gives the loser one toward a Bad one, once a season at most. The Diary notes it for you to add. The winner of a forensic one proves the case.

Virtues and Flaws count:

- Afflicted Tongue -2 and Incomprehensible -6 to Attack
- Good Teacher +3 in a deliberative disputatio, and Inspirational +3 in an epideictic one
- Short Attention Span -3 to Defence
- Piercing Gaze +3 to Weakening
- Strong-Willed +3 to Resistance
- Aristotelian Training +1 to every total
- Poor Disputer -3 to each roll
- Clear Thinker eases the Fatigue penalties by one
- Enfeebled -1 a question after the first.

**Before a crowd** takes 3 from each roll of a Gifted disputer, unless theirs is a Gentle Gift. Academic Concentration and Aristotelian Training count for Artes Liberales as logic and rhetoric (Art & Academe, Chapter Eight: Universities).

## Cast a Power
<!-- help: hedge-cast -->

More beside a hedge wizard's Abilities rolls one casting by the tradition's own rule, as its [chapter](help:tradition-chapter) lists it. Choose the **Way of casting** and the **Arts or Ability used**. Type the effect's **Level or Ease Factor**, the **Aura** where it's cast (the covenant's, to start with) and any **Pawns of vis**, then choose Cast.

The app works out the Casting Score and rolls the rule's die, or uses one typed in **Die**. It divides as the rule says and says whether the casting works. A rule that may fall short at a Fatigue level says so. A botch's zeroes give a Warping Point each (DE pp. 227, 389; Hedge Magic RE pp. 37, 96), which can bring on the character's answer to Warping as any other event does. The casting goes in the Diary.

## Conjure a Spirit
<!-- help: galdor-conjure -->

More beside a galdraman's Abilities. A song calls a spirit to work one effect (*Land of Fire & Ice* pp. 46-48).

- Choose the **Song Talent**.
- Type the **Effect level**. The Hermetic guidelines set it, and the storyguide has the last word. Its magnitude can't be more than the Song.
- Choose the **Duration**, Momentary or Concentration.
- Tick **A ritual effect** where a magus would need a ritual. The song then takes 15 minutes a magnitude in place of one, and the spirit takes a pawn of vis a magnitude.
- Tick **Touching the ground** if the galdraman isn't on a platform, a chair or a table. It halves the total.

The total is Com + Music + Galdor Wisdom + the Song + the aura + a stress die, and it must be greater than the level. Landvaettir count as Faerie in every aura but a Magic one, so a Dominion hurts as a faerie would feel it. The spirit's Might is the total, and Penetration is reckoned as the Definitive Edition does.

With **Hours he holds the song**, the app rolls Sta + Music for each hour, against 6 + the hours. Up to 3 short costs a Fatigue level, and worse ends the song. A total of twice the level leaves a Concentration effect working on for a die of hours. No vis boosts a song. It goes in the Diary, and a botch's zeroes give Warping Points.

## Bargain with a Lord
<!-- help: galdor-bargain -->

More beside a galdraman's Abilities. Anything longer than Concentration comes from a lord of the landvaettir, in the wilds, and the lord has to agree (*Land of Fire & Ice* p. 48). Write **The lord** and **The service**, the **Vis a year** it tithes if it lasts over a year, and any **Favour owed**. The book's price is about double the magnitude, reckoned at Sun Duration, and a skilled galdraman asks less.

Usually the lord agrees or refuses in play, so say which. A deal the lord agrees to goes in Bound Beings under Galdor, where you can change it.

To leave it to the dice, choose **Roll the Bargain** (*Houses of Hermes: Societates* p. 136). It's Com + Bargain + a stress die, against 18 with its modifiers for these:

- the terms
- how long the service lasts
- any duty the galdraman takes on
- the vis offered, +2 a pawn under the standard and -2 over.

The galdraman summoned nothing, so no Summoning Strength adds. Failure is no deal. A botch gives them Supernatural Nuisance from a weak lord, or Plagued by Supernatural Entity from a stronger one, for at least a month.

A missed tithe or service breaks a deal and may bring reprisals.

## Bind an Item
<!-- help: galdor-bind -->

More beside a galdraman's Abilities, once a deal with a lord is on their sheet (*Land of Fire & Ice* p. 49). The galdraman needs no laboratory, only the tools to make the item, and the spirit is bound as they make it.

- **For his lifetime**, the total must reach double the level plus the Effect Frequency Table's levels. The Duration is Momentary or Concentration, and Constant Use adds 5 to a Concentration effect's level.
- **A single service** needs only the level, and lasts a year and a day.

The total is Com + Music + Galdor Wisdom + the Song + the item's bonuses + the aura + a stress die. Galdor Wisdom and the Song each count no higher than the **Craft used**. Craft: Runes, the book's Scribe Runes, may stand as the Craft and inscribes a ready-made item, but adds nothing. The Song must be at least the magnitude. The spirit takes about the vis a magus would spend, first. The item goes on the tradition's Effects and Items.

## A tradition's chapter
<!-- help: tradition-chapter -->

<!-- tui -->
A character who belongs to a non-Hermetic tradition, such as the folk witches or the vitkir, has a tab named after the tradition's magic, such as Folk Witch Magic or Rune Magic, as a magus has Hermetic Magic.
<!-- /tui -->
<!-- gui -->
A character who belongs to a non-Hermetic tradition, such as the folk witches or the vitkir, has a chapter named after the tradition's magic, such as Folk Witch Magic or Rune Magic, as a magus has Hermetic Magic.
<!-- /gui -->
It lists the tradition's Arts and Abilities the character has, grouped by the part they play: Techniques, Forms, Runes, then the tradition's other Abilities. These leave the character's Abilities while they belong to the tradition.

A sahir's Sihr is usually of the Magic realm, and versions of the other realms exist (The Cradle and the Crescent, p. 47). One with the Sihr Ability chooses its realm on the **Traditions** form. Their summoning then reads the aura by that realm, for the total and the botch dice, and the Summoning rule says what that version changes in the bargain. The Solomonic arts stay Magic, since the book aligns only Sihr.

A sahir may have another summoning art in place of Sihr: (Faerie) Summoning, as most yatus do, the Goetic Summoning or Elementalist Summoning. The Summoning rule lists each one they have, read by that art's realm. With **Yatu Magic**, all their magic counts as Magic or Faerie, whichever suits the aura best, for its total and its botch dice. An aligned Sihr may use its own realm too. They gain no Warping from living in Magic or Faerie auras (The Cradle and the Crescent, pp. 30-31).

<!-- tui -->
**You type:** `a` adds one of the tradition's Arts or Abilities, `e` sets
its XP and Specialty, and `d` deletes it. More's **Traditions** (`m`, `t`)
on the character chooses the traditions they belong to. Only those the
saga offers are listed (see [Traditions Offered](help:section-traditions)).
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one of the tradition's Arts or Abilities,
**Edit** sets its XP and Specialty, and **Delete** deletes it. The
**Traditions** button in the Abilities chapter chooses the traditions the
character belongs to. Only those the saga offers are listed (see
[Traditions Offered](help:section-traditions)).
<!-- /gui -->

Ticking a tradition the character didn't belong to joins it. The Virtues and Social Status its members need are added, and a note says what was added. Leaving a tradition takes nothing away, and its Arts and Abilities move back among the character's Abilities.

Joining doesn't Open a Gifted member's Gift. A Gifted master of the tradition does that, usually at the start of an apprenticeship (Hedge Magic Revised p. 7). Plan **Open a student's Gift to a tradition** for the master. It brings the Opening's Arts and Abilities at 0 and its free Virtues.

A magus may belong to a tradition too. A Hermetic society, such as Sol Invictus or the Priory of Saint Nerius, is open to any magus. A tradition of House Ex Miscellanea, such as the Tempestaria or the Rustic Magi, is open to the House's magi. Their free House Virtues are then the tradition's own: its Major non-Hermetic Virtue, its Minor Hermetic Virtue and its Major Hermetic Flaw (Houses of Hermes: Societates, Chapter 5: House Ex Miscellanea). The tradition shows beside Hermetic Magic.

**Nemthengacha** (DE p. 244) are Celtic and Scandinavian magi Ex Miscellanea whose Embitterment turns a listener against a friend, kinsman or lord. The roll is Communication + Embitterment + stress die against 6 to 18, by how close the victim and their friend are, +3 for hatred and +6 for murderous loathing. Their package is Embitterment, Subtle Magic, and Deficient Technique in Rego (DE pp. 244-245).

**The app works out:** each score from its XP, on the Art table or the Ability table as the tradition's book says (see [Abilities](help:tab-abilities)). It also works out the [Casting](help:tradition-casting) totals, the [Magical Defenses](help:tradition-defenses), the character's [Effects and Items](help:tradition-effects) and their [Bound Beings](help:tradition-bonds). Last come the tradition's [Warping](help:tradition-warping), [Pools](help:tradition-pools) and [Seasons](help:tradition-seasons).

The Goetic traditions (Witch-Hammers, Dread Host, Mulhidun, Witches of Thessaly, Ba'al Ov) list their Arts' effects as General guidelines. These cover the summoning, scouring, ablating, binding and commanding targets, the uses of Ablation Points and the common commands (RoP: The Infernal pp. 114-118). An effect built on one keeps the level you type.

## A tradition's Effects and Items
<!-- help: tradition-effects -->

The spells, charms, rune scripts, rites and powers the character knows of the tradition, and the items they've made (amulets, chartae, fetishes, potions, tattoos, wondrous items). Each names the way of casting it uses, one of the tradition's in [Casting](help:tradition-casting). It also names its Arts, Ability or runes, its level and its Range, Duration and Target.

<!-- tui -->
**You type:** `a` adds one, `e` edits the chosen one, and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one, **Edit** edits the chosen one, and
**Delete** deletes it.
<!-- /gui -->
An item also keeps its charges or doses left, which you count down.

**The app works out:** each one's Casting Score in the covenant's aura, and the die it needs so that (Casting Score + die) / divisor reaches its level. Where the tradition casts up to 10 short, it also gives the die for a Fatigue level. A power whose magnitude is its Ability, such as a folk witch's, needs no die for a level. Cast against an Ease Factor, it shows the die that Ease Factor needs and the level the power counts as, 5 x the Ability (Hedge Magic RE p. 36). A stressed casting shows its botch dice. An item made by a Lab Total shows that Lab Total.

**Built from a guideline.** When the tradition has a guideline table (see [Casting](help:tradition-casting)), choose the effect's **Guideline**, its **Range**, **Duration** and **Target**, and any **Further magnitudes**, such as size, complexity or hatred for an Embitterment. The level is worked out for you instead of typed, as a Hermetic spell's is.

- Each magnitude adds 5 levels, or 1 below level 5. The traditions whose levels or Ease Factors step by 3 add 3 instead. These are Soqotran spells (Rival Magic p. 124), Augustan rites (p. 57), a Muspelli utiseta (p. 90) and an Embitterment (Tales of Mythic Europe p. 35).
- The Ranges, Durations and Targets offered are the tradition's own, or the Hermetic ones for a tradition that lists none. A gruagach has Conversation, Geas and Limit (HMRE pp. 60-63), and an Amazon Sister, Cousin, Exchange and Hour (Rival Magic p. 23). A learned magician's charms and amulets each have their own (HMRE pp. 85-86).
- Some cost by the Art used. A gruagach's Conversation is free for Blessing and Curse but a magnitude for Shape and Vision. An Amazon Consonant has a base Range and Duration, each step from it either way a magnitude (Rival Magic pp. 23-25). A utiseta counts only the steps from its Ability's own base (Rival Magic p. 95).
- A vitki's rune, a Columban ward or a folk witch's curse is its guideline's level as printed.
- A General guideline, or no guideline, keeps the level you type.

The Hyperborean hymns' guidelines are General, so a Power uses the Hermetic guidelines within its hymn's principles. The list offers each hymn's principles, the book's sample Powers with their level costs and Ease Factors (as corrected by the errata), and Numina of Apollo. That's a Vim Power any hymn can hold, giving Magic Resistance of the level - 5 against its principles (Ancient Magic p. 110). The level you type is the Power's level cost, with its uses a day and Penetration added as for an enchanted device (DE pp. 256-258; Ancient Magic pp. 107-118).

**Not yet:** a season of work making the item or inventing the effect for you, and the catalogs of each book's printed spells and charms. Add an effect here when its season is done.

**Faerie rites** (the ollamhain, the volkhvy and the wise folk). A rite is built on the guidelines of one of the tradition's Faerie Powers, with any Method. The ollamhain have Beguile, Dream and Portage, the volkhvy Conjure and Grant, and the wise folk Ware, Weal and Woe.

A rite may take the Hermetic Ranges, Durations and Targets, and House Merinita's Faerie Magic ones: Road, Fire, Until (Condition), Year + 1 and Bloodline (DE pp. 237-238). It can't take Bargain, which Realms of Power: Faerie doesn't give rites. It may also take the Faerie ones (Realms of Power: Faerie pp. 122-123):

- **Ranges**: Crossroads, Presence, Prop, Symbol. Presence reaches as far as the caster's Presence. That's 100 paces at +4, 50 at +2, 15 at -1 to +1, 5 at -3, and the caster alone at -4.
- **Durations**: Held, Focus, While (Condition), Geas (Condition), Hour + 1, Midday/Midnight, Not (Condition), Season, Aura, Faerie, Hidden, If (Condition), Symbol.
- **Targets**: Medium, Passion, Symbol.

Geas and If add the triggered effect's Duration, so type its magnitudes as further magnitudes. A Geas is Sun plus the trigger's Duration. If is the trigger's Duration plus four, and a ritual.

Each rite's row says these:

- **The Sympathy points it needs**, a fifth of its level. A rite reaches at most 5 x the Sympathy Traits that apply to its target, negatives counted by their size, and a Conjure change counts the Traits of both states (pp. 121, 125). The book's limit is firm, but the app can't tell which Traits apply. So it only warns when the rite needs more than all the character's Sympathy Traits together, temporary ones included.
- **The 3 points each Symbol needs.**
- **The parameters that make it a ritual**, which takes fifteen minutes a magnitude and no vis.
- **What its Method asks** (pp. 121-124; Errata p. 68). Evocation takes a Warping or Confidence Point, and vis at +2 a pawn up to Evocation + the Power. Enchantment needs a performance against 3 x the magnitude first. Empathy costs a Fatigue level and an hour's trance, each further Fatigue level adding the limit again.

**Holy Powers and maleficia.** A holy tradition's effects, such as the Ascetics', Cantores' or Sufis', are built on the holy Powers' guidelines (Realms of Power: The Divine pp. 48-56). An infernal tradition's are built on the maleficia's (Realms of Power: The Infernal pp. 105-112). Both serve the Powers among the tradition's favored Abilities. Each guideline names the Method it's for, such as "Strike dead (Purity)". The Ranges, Durations and Targets are the Hermetic ones.

- **A holy effect.** Year and Boundary cost 4 magnitudes more, as anything a Hermetic ritual would need does. Type other ritual cases, such as an Arcane Connection summons, as 4 further magnitudes. A holy connection stands in for an Arcane Connection (p. 48).
- **A maleficium's parameters.** It may also take Crossroads (as Voice), Cursed (Condition) (as Sun, with the triggered effect's Duration typed as further magnitudes), and Passion (as Group). It may take Forsaken (as Year), which repentance ends and which can't be dispelled (p. 103).
- **Method warnings.** An effect's row warns when its Power doesn't work with its Method, or its guideline is for the other Method. Adjuration and Cursing take Invocation or Purity, and Blessing Invocation or Meditation. Intervention and Transcendence take Meditation or Purity, Understanding Meditation alone, and Wonders Invocation alone.
- **Falling short, holy.** A holy effect's row says that falling short is a tragedy of hubris. It's Minor 1-10 short, Major 11-20, Ultimate 21 or more, with True Faith x 10 standing in for the total (p. 46).
- **Falling short, infernal.** A maleficium's row says its Method's cost. Debauchery costs a long-term Fatigue level or a Light Wound. Incantation costs a Confidence Point or a Warping Point for a fitting sin, and vis +2 a pawn up to Incantation + the Power. Each 10 levels short is a botch and a Warping Point (Vituperation at 2), with Hierarchy x 10 standing in for the total. A true botch owes Hell a soul within a season (pp. 102-104).

## A tradition's Casting
<!-- help: tradition-casting -->

How the tradition's members work magic, each way as its book gives it, with the character's Casting Score for everything they can cast in their covenant's aura.

- A tradition that pairs a Technique with a Form, such as the gruagachan, the learned magicians or the elementalists, shows a grid, Techniques down and Forms across.
- One whose powers are Abilities, such as the folk witches, lists each with its Characteristic.
- The vitkir list each rune.

Below each come what the total adds and what it must reach, the Fatigue, how much vis it can use, and the Penetration.

**The app works out:** each Casting Score as the Arts or Ability + the Characteristic + any Ability the book adds + the aura's modifier for the tradition's realm. A Magic tradition loses three times a Divine aura. The total is (score + die) / divisor. A gruagach's spontaneous spell halves it, and so does a learned magician's known charm, while one cast from a text divides it by five. Some traditions cast up to 10 short for a Fatigue level. An Ability's effect must reach its Ease Factor, and counts as a spell of 5 x its score. Penetration is the total + the Penetration bonus - the level, as for a magus. A Lab Total, such as Refining or a vitki's, adds no die. The dispellings a tradition knows and its group castings, such as the folk witches' sabbats, are listed below.

**Botch dice.** A stressed casting botches as a Hermetic magus's does (Definitive Edition p. 227). That's one die, one more a pawn of vis, and one a point of another realm's aura, twice that in a regio. A Divine power takes none for the aura. The books give this for the gruagachan, the learned magicians and the vitkir (HMRE pp. 71, 85, 126) and the rival traditions (Rival Magic pp. 25, 65, 115). An Amazon rite rolls its magnitude + the aura (Rival Magic p. 25). A Lab Total, a simple die or a rule with no die rolls none.

A tradition's own extra botch dice are noted under its rule:

- Wildfire's two (Rival Magic p. 104)
- a vitki's Mastered Rune taking three off (HMRE p. 121)
- the learned magicians' dice for each realm entreated and for a weak Language (HMRE pp. 85, 88)
- a sahir's extra summoning time (The Cradle and the Crescent p. 46).

**Guidelines.** A tradition with a guideline table lists how many it has and from which pages. Choose one on an effect in [Effects and Items](help:tradition-effects) and its level is worked out. The tables are these:

- the gruagachan (HMRE pp. 66-70)
- the learned magicians and the imhergi who cast with their Arts (HMRE pp. 89-94)
- the vitkir's runes (HMRE pp. 128-139) and the Saxon runes (Thrice-Told Tales pp. 139-143)
- the folk witches' Ease Factors (HMRE pp. 37-42)
- the Amazons (Rival Magic pp. 32-43)
- the Augustan schools and the Sortes Virgilianae (Rival Magic pp. 53-60)
- the Muspelli's Abilities and their utiseta bases (Rival Magic pp. 95-105)
- the Soqotran incenses (Rival Magic pp. 127-132)
- the five Solomonic arts (The Cradle and the Crescent pp. 48-58)
- the Columbae's wards and the other Ex Miscellanea Ease Factor tables (Houses of Hermes: Societates pp. 105-128)
- a hunter's Scry (Against the Dark p. 134)
- the Nemthengacha's Embitterment (Tales of Mythic Europe p. 35)
- the clesrada's feats (The Contested Isle pp. 102-105)
- the Debterah's Holy Methods and amulets (Lands of the Nile p. 114, with Realms of Power: The Divine)
- Corpse Magic for the Cult of Dedun (Lands of the Nile p. 102).

Corpse Magic is Communication + Corpse Magic + aura + stress die. It's against 9 to speak with a corpse, 12 to compel the truth or protect it, 15 to animate it and 18 to command it out of sight. Its Penetration must beat the corpse's Might, usually 9, to raise it from the grave.

**Hunters.** Any Foe Art pairs with any Practice Art (Against the Dark p. 132). The grid shows every Foe Art the character holds, the ones listed or another the troupe names.

**Folk witches.** A flying witch adds their Flight score to Attack and Defense against a foe who can't fly. Life-Linked Folk Witch Magic adds 5 a Fatigue level spent (HMRE pp. 35, 38). A potion casts at its Brew Potency + a stress die, with no aura and no Penetration bonus, and must penetrate the drinker. One that grants a power gives it at Brew Potency / 5, rounded up, for Brew Potency days (pp. 40-41).

**Nightwalkers'** rolls (HMRE pp. 107-111):

- Spirit travel is Stamina + Athletics against 3 (places seen daily) to 15 (never visited), +3 for each object carried.
- Leading a willing spirit along is Stamina + Leadership against 3 more.
- Changing form in combat is Stamina + Concentration against 15.
- Seeking a foe in battle is Perception + Awareness against 9.
- Intimidating a ghost is Presence + Leadership against 6 + its Brave.
- Questioning one is Presence + Charm against 3, 6 or 9 by the answer's length.
- Straying costs a Long-Term Fatigue level for any time up to an hour, however short, and two for a whole night. Talking with people at its end costs one more (HMRE pp. 106, 108).

**The clesrada.** Each feat of arms is a power on the Feat roll of its Characteristic, its guideline giving its Ease Factor. The roll is Characteristic + its Ability + a stress die, + the aura's modifier for a Faerie power, and a botch always costs a Fatigue level. A feat counts as a 15th-level spell with Penetration 0 + the Penetration bonus against magic that affects spells. But it acts on its user and need not penetrate a foe. Feats of one Ability chain into one action until one fails (The Contested Isle pp. 101-105).

**Saxon runes.** Ac, Æsc, Yr, Ear, Gar, Calc, Cweorth, Stan and Ior are vitkar runes with their own guidelines (Thrice-Told Tales pp. 139-143). Only Damhan-Allaidh knows them, by a minor Initiation for a vitki who knows all 24 Elder runes. Ac has no printed guidelines.

**Not yet:** rolling a casting, and the summoning chart. Each charm, spell or script the character knows is in [Effects and Items](help:tradition-effects).

## A tradition's Magical Defenses
<!-- help: tradition-defenses -->

The Magical Defenses the character's training gives: one for each of the tradition's Arts or Abilities they have, against its own kind of effect. Hedge wizards have no Magic Resistance, so these only lessen magic.

**The app works out:** the bonus, a hedge Art's score / 5 (rounded up) or a Supernatural Ability's score, doubled by Greater Magical Defenses. The No Magical Defenses Flaw takes them all. Defenses never add up. Only the best one against an effect applies, and none works against an effect of Personal range. The vitkir and elementalists have none.

## A tradition's Seasons
<!-- help: tradition-seasons -->

What the tradition does with its seasons, with the character's own totals.

- **Opening** gives the character's Opening Total as the master, and what it's set against.
- **Initiation** lists the tradition's printed Scripts, with the character's Initiation Total as Mystagogue against each one's Ease Factor, what it gives and its Ordeal.
- **Advancement** says whether the tradition's Arts may be practised or studied from vis.
- **Seasons of work** lists the tradition's own seasons, with the character's best Lab Total for each.

**The app works out:** the Opening Total, the Initiation Totals and the Lab Totals. Most Opening Totals are a Lab Total of Intelligence + an Ability + Arts + the aura. The elementalists' uses their highest Technique and lowest Form, and a vitki's their lowest rune. An Initiation Total is Presence + the tradition's Lore + the Script's bonus, or an elementalist's best Organization Lore.

The seasons themselves are planned on This Season (see [Activities offered](help:plan-season-activities)). A hedge Initiation is an **Undergo an Initiation** season with the **Hedge Script** chosen, which brings its bonus. See [How to initiate a character into a Mystery](help:guide-initiation).

The **Opening Ease Factor** is twice the student's Supernatural Ability and Art scores, their Hermetic Arts with experience among them. It's +12 if their Gift was Opened before, by another tradition or as a magus, which means any Hermetic Art with experience, or being a magus (HMRE p. 8).

At a folk witches' sabbat, helping Gifted witches add +1 each to the Opening Total. No more of them help than the Magic aura at the sabbat's site, so another realm's aura lets none help (HMRE pp. 45-46). Enter them as **Sabbat helpers** on the Open a Student's Gift season, with the **Sabbat aura (Magic)** where it's held. For a sabbat Initiation, add the helpers to the **Script bonus** yourself, with the same cap (p. 46).

**A folk witch's kitchen** (HMRE pp. 35, 39-41, 45; DE p. 219):

- A brew's Brew Potency is its power's Lab Total, or the power twice with Expert Potion Brewer. Add 1 for each sister helping at a sabbat, up to the Magic aura there.
- It makes Folk Witch Magic Theory doses, + a Lab Text's level, at a pawn each + the effect's own vis.
- A season may use twice the witch's Folk Witch Magic Theory in vis, or four times with Concentrated Potions.
- Extracting vis gives a tenth of the witch's Lab Total with no power in it, rounded up, in Vim.
- Fixing an Arcane Connection makes it last that Lab Total in its next unit up, along hours, days, weeks, months, years and decades. One lasting decades can't step further, and indefinite connections are the laboratory's.

The brewing season's notes say what it makes.

An elementalist's **Refining** season shows what its Refining Total makes (HMRE pp. 26-27):

- a longevity potion of Total / 5, for age / 5 pawns
- by the elementalist's Refining types, a Characteristic potion (Total / 5, to at most half the Form), vis from an aura (Total / 10), vis moved (Total / 5 pawns), or a being's Might restored or drained by the Total less its Might.

The divisions round down, as the book's do when it says nothing (DE p. 6). Only the potion's vis, age / 5, rounds up.

A Hyperborean hymnist's **Infuse a Power** season shows how many Power levels their recitation total reaches (Ancient Magic pp. 106-108).

- The total is Communication + the Hymn + Dead Language: Hyperborean + the aura. Hyperborean Descent's +2 or +4 is added in the note.
- The Ease Factor is the levels / 3, rounded up, so a total reaches three times its value in levels.
- The note also lists each hymn's levels. That's 15 for each point of its score (Puissant doesn't count), those already infused, and those left.
- Yours to add (p. 107) are devotion before the season (+3 a season, at most +9), days without reciting (-1 a day, at most -20), and Personality Flaws Apollo favours or dislikes (+1/+3, -1/-3).

An **Enchant a relic** season uses Intelligence in place of Communication, with no devotional bonus. Its note gives the most levels one Power can have, and the Warping it costs. That's 2 Warping Points for every pawn of vis Hermetic enchanting would need, plus 2 a pawn of the item's opening the first time (pp. 116-117).

A hedge Script may need scores of the Initiate, and the season says when the Initiate falls short:

- every Ikhwan as-Safa' Script fails without Artes Liberales, Philosophiae and Theology (Islam) 4 and Arabic 5
- the Tulab Ibn Sina's fail without Medicine and Chirurgy 3, 4 or 5 by Script (HMRE pp. 30-31)
- a learned magician's master tests an Ability at 2 (pp. 88-89).

A gruagach initiating themselves uses their own scores and the harder Ease Factor, 18 or 30 (p. 61).

The **lector priests** have a season to make a transitory item or statue (Lands of the Nile pp. 51-54). It's a temporary amulet, a seal or a potion poured over a cippus statue, each holding one Until effect for one use, or a faerie persuaded into a statue. The book gives no total for them. A new statue's consecration is Com + Folk Ken + a die against 18 (p. 53).

**Franciscans** (The Church pp. 137-139) are a Holy Tradition in the traditions list, open only to a friar or a Poor Sister, since Monastic Vows is required. They have four Scripts, each needing a Mystagogue who knows the Virtue (Target 21):

- Meditation (+15, Driven)
- Understanding (+7, Visions)
- Intervention (+9)
- Purity (+9, Fragile Constitution).

The book prints each Script's total after Meditation's Major Ordeal, so Understanding's Target is 12, Intervention's 15 and Purity's 18. The app takes those past-Ordeal reductions off by itself.

**Hermetic Mystery Cults** are in the traditions list as societates any magus may join:

- **The Cult of Mercury** (Faith & Flame p. 28). The Consecration of Priamitus, Target 21, +18, gives Mercurian Magic and the Pagan Story Flaw.
- **The Legion of Mithras** (The Mysteries Revised Edition p. 121). The Raven's Strong-Willed Script, Target 15, +5.
- **The Knights of the Green Stone** (p. 132). The Page's Free Expression Script, Target 15, +7, Dutybound.
- **The Matres et Matrones** (Faith & Flame p. 30). They have no printed Scripts. Their three levels and what each needs are in the cult's notes.

Add a member with Traditions, then plan Undergo an Initiation with the cult's Script chosen in Hedge Script. Each cult's Lore is "Mystery Cult Lore: (cult)". The Matres' is "Organization Lore: Matres and Matrones", as the book names it. The Green Stone's Page Script says its own Ordeal lowers that Initiation's Target to 12. The Definitive Edition lowers only the next three Initiations (DE p. 388), so the app keeps it at 15.

**Not yet:** what a season of work makes, such as a potion, a charm or a script, isn't added for you. Add it to [Effects and Items](help:tradition-effects) when the season is done.

## A tradition's Bound Beings
<!-- help: tradition-bonds -->

The beings bound to the character by the tradition, such as a folk witch's familiar, a gruagach's fetch, or any spirit, statue or beast the troupe binds. Each names the kind of bond, as the tradition's book gives it, and the Bestiary creature it is, if the saga has one. It also names the bonus its bond adds to the character's totals.

<!-- tui -->
**You type:** `a` adds one, `e` edits the chosen one, and `d` deletes it.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** adds one, **Edit** edits the chosen one, and
**Delete** deletes it.
<!-- /gui -->
The bonus is typed in. A folk witch's familiar adds its Intelligence + its Folk Witch Magic Theory to the witch's Lab Totals.

**The app works out:** the bonus, added to the tradition's casting totals or its Lab Totals, whichever the bond applies to. It shows in [Casting](help:tradition-casting), [Effects and Items](help:tradition-effects) and [Seasons](help:tradition-seasons). Below the list is each bond the tradition's book describes, with how it's made and what it gives.

**Not yet:** the season of binding itself. Plan it as the tradition's own work, then add the being here.

## A tradition's Warping
<!-- help: tradition-warping -->

What the tradition's Gifted members suffer from Warping. No hedge tradition goes into Wizard's Twilight, and none gains Warping Points from living in a strong magic aura. Each has its own response:

- the elementalists' Elemental Warping
- the folk witches' Witch Moon
- the gruagachan's Transformation
- the learned magicians' Intervention and Abduction
- the vitkir's Nátt-thel.

The section gives what sets it off and the rolls it calls for, with the character's Warping Score from the [Aging](help:section-aging) section.

**The Witch Moon.** Each month, Stamina - Warping Score + a stress die against 6 ends it. More months than the witch's Warping Score make it a bad experience, 2 xp lost a Warping Point gained. Otherwise it's a good one, 5 xp a month. Harsh Moon makes the fever a Heavy Wound, Painless Moon none (HMRE pp. 35, 42-43). A magus, and every member of an Ex Miscellanea tradition, is a Hermetic magus, with Warping and Twilight as for any magus.

**The app works out:** an elementalist's Personality Traits, one for each Elementalist Form they hold, at the Warping Score + the Form / 5 (rounded up). From +3 a Trait acts as a Minor Personality Flaw, from +6 a Major one, and at +10 the storyguide takes over.

An infernalist's **Vituperation** is worked out on their tradition's Warping (Realms of Power: The Infernal pp. 94-96). On 2 or more Warping Points at once, it's Stamina + Concentration + Confidence against Warping Score + the points + Hierarchy + the aura. Hierarchy is the infernalist's highest Infernal Reputation. Sacrifice adds +2 (an effigy) to +10 (an innocent) to an effect. Profaning a holy thing makes a pawn of Infernal vis for a Confidence Point.

Two or more Warping Points at once roll the tradition's answer straight away, as Twilight is rolled for a magus, and write it in the Diary.

- **Divine Ascent**, for a holy tradition's member or anyone with a holy Method or Power (Realms of Power: The Divine pp. 63-65). The roll is Presence + Concentration (or Meditation) + stress die against Warping Score + the points + True Faith + the aura + stress die. Only the character's own die can botch. Failing, they gain the margin in Warping Points more. They ascend for Warping Score + every point gained - True Faith days, at least 1, or months from Warping Score 6. The Diary gives what each of the three forms brings: Gloom, Form and Unity.
- **Vituperation**, for an infernalist (Realms of Power: The Infernal p. 95). Failing, they're torn away as long as Twilight's table gives their Warping Score. The app writes the Aging roll they must make, adding their Warping Score. They gain a Confidence Point a Warping Point at once, unless they botched the avoidance roll. Once the ordeal is over, their Confidence Score rises by 1 if it's below their Warping Score or their Decrepitude. When it's already below the Warping Score, the Diary says so outright. Otherwise it says it depends on the Aging roll's Decrepitude, for you to change on the Character Info form.
- **Faerie Calling**, for a Faerie tradition's member (Realms of Power: Faerie p. 120). It gives the Ease Factor to act while dazed, the roll that resolves it (a stress die that can botch), and the Faerie Rank from which it's a good Calling. The character's own Faerie Rank shows under [Aging & Warping](help:section-aging).

**Enter Twilight willingly** skips the roll for an Ascent or a Vituperation too.

A Hermetic magus goes into Twilight, True Faith or not, unless something takes its place:

- The False Gift, or an infernal tradition, brings Vituperation (Realms of Power: The Infernal p. 124).
- A homunculus wizard has a Faerie Calling (Realms of Power: Faerie p. 118).
- A magus who also has Miraculous Abilities has only one form of Warping for life, chosen by the troupe. Tick **Seeks Divine Ascent instead of Twilight** on their Aging & Warping form for the Ascent (Realms of Power: The Divine p. 63).

The Divine and Infernal answers come before Faerie's.

A Gifted Hyperborean hymnist whose first tradition is the hymns has **Illumination** in place of Twilight (Ancient Magic pp. 105-106). The section gives these:

- their Apollonian Personality Trait, which is their Warping Score
- their control total, Stamina + Concentration + their highest Hymn
- the Ease Factor's modifiers, -2 or -4 for Hyperborean Descent and +1 for every 30 levels of Powers they've infused
- the Bright Lightening, failing the roll on purpose. It gives as many more Warping Points, and xp in hymns, as their Warping Score after the points just gained + the aura + the modifiers. The number shown is for three points gained (Ancient Magic p. 106).

The +1 a 30 levels counts the Powers of all their hymns together, not those in relics. An unGifted hymnist, or a magus, Warps as usual.

## A tradition's Pools
<!-- help: tradition-pools -->

The points the character keeps in each of the tradition's pools, for a tradition whose members store power. Its book says what fills the pool, what spends it and its cap, which are shown here. A tradition with no pools has no such section.

A Hyperborean hymnist's **Power levels** pool lists each hymn they hold. It shows the levels its score holds (15 a point), the levels their infused Powers already use, and the levels left. Their infused Powers are their effects on the Infuse a Power rule. The points you type are kept apart from these, for the extra levels bought with vis, a level a pawn (Ancient Magic p. 109).

<!-- tui -->
**You type:** `e` sets the points in each pool.
<!-- /tui -->
<!-- gui -->
**You type:** **Edit** sets the points in each pool.
<!-- /gui -->

**Not yet:** filling or spending a pool for you. Set the points by hand.

## Ars Notoria
<!-- help: learned-magic -->

Ars Notoria (Realms of Power: The Divine pp. 97-100). Only a Gifted Christian may learn it, and only from the Book of Solomon. A season's search is Intelligence + Divine Lore + a stress die against 21. Reading it needs 4 in Latin, Greek, Hebrew and Chaldean, and Artes Liberales 4. It's a tractatus of Quality 20, learned as a first Supernatural Ability, so a season giving under 5 xp is wasted.

**Reciting a Ring** is Intelligence + Ars Notoria + the season's modifiers + a stress die. It's against 6 + 3 x the Ring's level + 1 a season it's to last, or 3 in place of 6 once the Ring is known. The modifiers are these:

- fasting +1 a season, and chastity +1
- Personality Flaws +/-1 or 3
- a venial sin -3, and a mortal sin -9
- minus each non-Divine Supernatural Ability
- plus True Faith.

The first recitation takes a season, and later ones 10 days less Ars Notoria, at least one. Rings are learned in order and don't stack. The xp go when the Ring ends.

- **I.** Philosophiae +100 xp and Communication +3 (to +5). Spring or Autumn.
- **II.** Theology +100 xp and Intelligence +3 (to +5). Winter.
- **III.** Medicine +100 xp and Greater Purifying Touch.
- **IV.** The Patron Angel, a teacher.
- **V.** Sense a being's realm, by Perception + Ars Notoria + stress die against 6 + its Magic Resistance / 5, with no Penetration (Errata p. 49). Summer.
- **VI.** Divination. Spring.
- **VII.** No botches.

Each point of Ars Notoria takes 3 off a Divine aura's penalty to casting the character's other magic. It shows on the Casting Score's aura line as "Ars Notoria". Lab Totals and Penetration take the whole penalty. While a Ring is in effect, a Divine aura gives no Warping (p. 100).

## Jewish Mysticism
<!-- help: jewish-mysticism -->

- **Shinnui Shem** (RoP:D p. 141). Once a life, a season's renaming severs every Arcane Connection. It gives (simple die + Intelligence + Gematria + Understanding + book Quality + Dominion aura) / 5 to Aging Rolls until the next Aging Point.
- **A golem** (pp. 142-143). A season shapes the clay. Then seasons of Intelligence + Kabbalah + Wonders + Ceremony bonus + Dominion aura against 30 bank the excess. Its Divine Might is the points + a stress die, at most 5 x the leader's Kabbalah. Its powers bank the same way against their level, up to its Might in magnitudes.
- **Merkavah** (p. 144). Stamina + Merkavah + Adjuration + Ceremony + aura against the being's Might banks until the points exceed it. That wins its True Name, for +5 Penetration.

## Solomonic Integration
<!-- help: solomonic-integration -->

The Cradle and the Crescent pp. 44-45.

- **Magi** may research Hermetic True Names, Scientates Suleimanis and Hermetic Realm Initiation, all on the breakthrough goal list. Hermetic True Names is Minor, giving a spell with a built-in Arcane Connection. The other two are Hermetic Breakthroughs giving Major Hermetic Virtues.
- **Sahirs** may reach Solomonic Devices, Spontaneous Solomonic Spells and Independent Solomonic Magic. Spontaneous spells are total / 2 with a Fatigue level, or / 5 without the die. Independent magic needs no spirit and no Summoning Strength, and uses its own Penetration.

## Virtues & Flaws
<!-- help: tab-vf -->

<!-- tui -->
The character's Virtues and Flaws, side by side, with one details panel
below both that shows the chosen one's effects and rules text.
<!-- /tui -->
<!-- gui -->
The character's Virtues and Flaws, side by side, each a card. Clicking one
shows its effects and rules text in the inspector.
<!-- /gui -->

**You type:** nothing. You pick each Virtue or Flaw from the catalog, and choose what it names from a list, such as Puissant's Ability, Affinity's Art or a Great Characteristic's Characteristic.

**The app works out:** the points each side comes to, in the section titles, coloured by whether the two sides balance (Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws). It also works out each one's effects on the rest of the sheet.

**See also:** [Abilities](help:tab-abilities),
[Hermetic Background](help:section-hermetic-background)

### Virtues
<!-- help: section-vf-virtues -->

The character's Virtues, each with its tier: Minor, Major or Free.
<!-- tui -->
`a` opens the catalog on its Virtues. `e` changes what the chosen one
names, such as Puissant Magic Theory to Puissant Finesse, and it keeps its
place in the list.
<!-- /tui -->
<!-- gui -->
**Add** opens the catalog on its Virtues. **Edit** changes what the chosen
one names, such as Puissant Magic Theory to Puissant Finesse, and it keeps its
place in the list.
<!-- /gui -->
<!-- tui -->
**Gain or Lose in Play**, in More, records a Virtue or Flaw that comes or
goes during the saga, with how, in the Diary ([help](help:vf-change)).
<!-- /tui -->
<!-- gui -->
**Gain or Lose in Play**, on the During the Saga strip under the Virtues
and Flaws, records a Virtue or Flaw that comes or goes during the saga, with
how, in the Diary ([help](help:vf-change)).
<!-- /gui -->
The choices are the ones Add offers. So a second Puissant Magic Theory is still refused, and a Great Characteristic can only move to a Characteristic at +3. Changing a Great or Poor Characteristic moves both scores. Great Intelligence to Great Stamina takes Intelligence down a point and Stamina up one, and the form says so before you save. A new choice counts from now on, and xp already earned stays where it is. To take a different Virtue, delete this one and add the other. A Virtue that names nothing has nothing to change.

A magus's House Virtue is marked Free and counts no points (Ars Magica Definitive Edition, Chapter 3: Characters, Hermetic Houses).

The catalog lists a supplement's Virtues and Flaws only while its book is in play (Saga Content's Books in Play). Some supplements print a Virtue or Flaw the Definitive Edition also prints, such as Art & Academe's Failed Student or The Church's Brother-Priest (the DE's Brother Chaplain). The catalog then has the Definitive Edition's alone, with its name, tier and text, whichever books are in play.

A character with a Might score from a Virtue (Demonic Blood) takes no Virtue of another realm. That rules out The Gift, True Faith, Faerie Blood and the Blood of the Nephilim (Realms of Power: The Infernal p. 84), and any Supernatural Virtue of another realm. One whose description names no realm is Magic (DE p. 64). Hex is taken as Infernal, the realm the book says it's most often tied to (DE p. 85). The Ríastradh needs the Fury or the Major Wrathful Flaw (The Contested Isle p. 120).

A Faerie Blood's details say what its variety gives, the stronger Legacy benefit with Faerie Legacy, and its Sympathies. The varieties are these:

- bloodcap, brownie, dwarf, ettin, faerie god, ghul, goblin, huldra, nymph, padfoot, satyr, selkie, sidhe and undine (Realms of Power: Faerie pp. 106-110)
- the jinni bloods 'afrit, ghula and jann (The Cradle and the Crescent pp. 77-78).

A Lesser or Greater Charm's details give the charm rules (Realms of Power: Faerie p. 104). The Ríastradh's and the Lúan láith's say how they work in play (The Contested Isle pp. 120-121).

A Faerie God's blood may name its Olympian. Choose "Faerie God: Zeus", or Hera, Poseidon, Demeter, Apollon, Artemis, Athene, Ares, Aphrodite, Hephaistos, Hermes, Dionysos or Hestia. The Virtue's details then list that god's Sympathy Traits to choose from (The Sundered Eagle p. 127). Zeus, for one, has Thunder & Lightning, Kings and Sky, with Fidelity negative.

### Flaws
<!-- help: section-vf-flaws -->

The character's Flaws, each with its tier. The section title shows the points they come to.
<!-- tui -->
Like Virtues, Flaws can be added, changed and deleted. `a` opens the catalog
on its Flaws, and `e` changes what the chosen one names, such as Poor
Perception to Poor Dexterity.
<!-- /tui -->
<!-- gui -->
Like Virtues, Flaws can be added, changed and deleted. **Add** opens the
catalog on its Flaws, and **Edit** changes what the chosen one names, such
as Poor Perception to Poor Dexterity.
<!-- /gui -->

### Powers
<!-- help: section-char-powers -->

The supernatural powers the character's Virtues grant, under the Virtues and Flaws. Each is like a Hermetic spell of its level, with Penetration bought level for level (DE pp. 81-106).

- **Greater Power** (Major). 50 levels a Virtue, one power each. Initiative is Quickness - magnitude / 2. It costs a Fatigue level up to level 50, two to 100.
- **Lesser Power** (Minor). 25 levels a Virtue, shared among powers. Initiative is Quickness - 2 x magnitude, and it costs a Fatigue level for each 25 levels.
- **Personal Power** (Minor). 25 levels a Virtue, for a power of Range Personal or a constant one. Initiative is as for a Greater Power.
- **Ritual Power** (Major). 25 levels a Virtue. Initiative and Fatigue are as for a Lesser Power, and it costs a Confidence Point a magnitude.
- **Focus Power** (Major). 25 points a Virtue, for any effect in its narrow field. It costs 2 a level of its greatest effect and 1 a point of Penetration. Initiative is Quickness - that magnitude, and it costs a Fatigue level for each 25 levels.

Each row shows the power's Initiative, Fatigue and Penetration. Under the list are each Virtue's levels used of those it gives. Shown in red is what breaks its rules:

- levels beyond them
- a power with no Virtue for it
- more Greater Powers than Greater Power Virtues
- a Personal Power neither Personal nor constant.

Adding or editing a power, **The Power** at the foot of the form says what it costs and what its Virtue has left.
<!-- tui -->
`a` adds a power, `e` edits the chosen one and `d` deletes it. Choosing
one shows it in the panel below.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the powers. Click one to read it
in full.
<!-- /gui -->

Conciatta's breakthroughs (Legends of Hermes pp. 14-16) are Hermetic Virtues gained by research or integration.

- **True Understanding of the Realms** (Major). An aura of another realm counts less by the magus's score in its Lore (Dominion, Faerie or Infernal Lore), never below 0, for its penalty and its extra botch dice. It shows on the Casting Score's and Lab Total's aura line. A bonus the aura gives, such as a Faerie aura's +half, is kept whole.
- **Insight of the Realms** (Minor). In a Ritual or ceremonial casting in an aura, that realm's Lore stands in for the lower of Artes Liberales and Philosophiae when it's higher, shown in the working. It also sees through that realm's regio boundaries in place of Second Sight.
- **Confluence of the Realms** (Minor). A lab text's realm may be changed when used again, and vis may be extracted in an aura of any realm.

## Hermetic Magic
<!-- help: tab-hermetic -->

<!-- tui -->
A magus's Arts, what they can cast, their raw vis and the spells they know,
with their research goals on the [Research tab](help:tab-research). Only a
magus has this tab. The line at the top names the magus's Talisman, how far
it's opened and its attunements.
<!-- /tui -->
<!-- gui -->
A magus's Arts, what they can cast, their raw vis, the spells they know and
their research. Only a magus has this chapter.

**Current Location**, at the top of the chapter, says where the magus is now
and the aura their casting counts there. Its button sets it
([Current Location](help:whereabouts)). **Magic Outside the Lab**, under
Raw Vis, holds the rest of what they can do with their magic. That's Craft by
Magic and Certamen, and Cast in a Lacuna, Spirits and Names, Dream Working,
Hermetic Sacrifice and Open a Tunnel when they can use them.
<!-- /gui -->

**You type:** the Arts' XP, the raw vis and each spell's Mastery.

**The app works out:** the Art scores, Casting Scores, Magic Resistance,
Penetration and Certamen totals.
<!-- gui -->
The Certamen totals are under the Casting Scores.
<!-- /gui -->

<!-- tui -->
**Certamen**, in More on Known Spells, plays a duel with another magus of
the saga (see [Certamen](help:certamen-duel)).
<!-- /tui -->
<!-- gui -->
**Certamen**, in Magic Outside the Lab, plays a duel with another magus of
the saga (see [Certamen](help:certamen-duel)).
<!-- /gui -->

The casting notes end with **craft magic**. Rego craft, shaping raw materials, is Perception + Finesse. Creo craft, making the thing, is Intelligence + Finesse. Each adds a stress die, against the Ease Factors for Creating and Crafting Objects (DE pp. 306-308).

**See also:** [Lab Totals](help:tab-lab-totals),
[Inventory](help:tab-inventory), [Planning](help:tab-planning), [How the app handles advancement](help:guide-advancement)

### Magical Arts
<!-- help: section-arts -->

<!-- tui -->
The five Techniques and ten Forms, each with its score and XP. `e` edits
every Art at once.
<!-- /tui -->
<!-- gui -->
The five Techniques and ten Forms, side by side, each with its symbol,
score and XP. Clicking an Art shows it in the inspector. The section's
**Edit** button edits every Art at once.
<!-- /gui -->
You type the XP and the app works out the score (Ars Magica Definitive Edition, Chapter 3: Characters, Advancement Table). It's shown beside the XP as you type, with the total XP the next score needs (Next at). A fixed bonus from a Virtue, such as Puissant, shows the score used in brackets.

### Casting Scores
<!-- help: section-casting -->

The Casting Score for every pair of Technique and Form is worked out, not typed, from the Arts, Stamina and the aura of the magus's covenant (Ars Magica Definitive Edition, Chapter 7: Hermetic Magic).
<!-- tui -->
The lines below it give Magic Resistance, Penetration and the Certamen totals.
<!-- /tui -->
<!-- gui -->
It's drawn as a grid with the Forms across and the Techniques down. Clicking
a cell shows how its score is made up.
<!-- /gui -->
It changes as the Arts, Characteristics or covenant change. The Virtues and Flaws that change it are counted, and named where they apply:

- words and gestures, such as Mute, Quiet Magic, Deft Form, and Afflicted Tongue's -2 to a spell spoken aloud
- a Divine aura, whose penalty and botch dice Susceptibility to Divine Power doubles
- Magic Resistance, by Flawed Parma Magica
- Penetration, by Weak Magic
- the Fatigue a spell costs, by Enfeebled, Withstand Casting or Mythic Blood.

**Virtues that count only sometimes.** The app works out the scores but doesn't play a cast out. So a Virtue or Flaw that counts only in its circumstance is named in a "When they apply" line under the scores:

- Special Circumstances (+3)
- Potent Magic (+3, or +6 Major, in its field)
- Hermetic Geometry (+3 for a circle or line)
- Cyclic Magic (+3 or -3 in its time)
- Corrupted Arts and Spells (+3 selfish, -3 selfless)
- Blood Haze (-10 to Formulaic magic in a fight)
- Environmental Magic Condition and Short-Ranged Magic (the total halved)
- Life Boost (+5 a Fatigue level spent)
- Spell Improvisation (a similar spell's magnitude).

Diedne Magic's Spontaneous casting gets a line of its own. A Ritual's vis on the Known Spells lines counts Mercurian Magic (half, at least one pawn) and Waster of Vis (a third more). With Rigid Magic it says no Ritual can be cast (Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws). Magical Focus, Deleterious Circumstances and Mystical Choreography are named there too. So are a Heartbeast's -15 in animal form, and Verditius Magic's reminder that Formulaic and Ritual spells need the magus's casting tools (DE p. 241).

Hermetic Numerology lists the Rotes the magus knows. A Rote is cast with no die and no Fatigue, quietly and still. Its Casting Total is half of Stamina + Technique + Form + Artes Liberales + aura, rounded up. The Numerologist's book bonus adds too when they take a round to consult it (TMRE p. 92). Hermetic Geometry adds +3 for a spell tracing a circle or line, and +3 more cast ceremonially in a regular figure (TMRE p. 94). Hermetic Architecture reminds how high Bind the Mystical Structure must be (TMRE p. 98).

Faerie Magic, Spell Timing and Secret Name add reminders (DE pp. 235, 237, 239-240):

- A Bargain spell's Penetration Total is doubled, and it takes effect when the bargain is broken.
- A held or If (Condition) spell is worked out, Penetration too, when it's released or triggered. An If spell lapses after a year.
- No sympathetic connection works against a magus with Secret Name. One who knows the secret name doesn't subtract the spell's level from their Penetration Total.

Hermetic Metamorphosis reminds its holder of the surgery of Harmonic Metamorphosis of the Beast (Magi of Hermes p. 83).

A Bjornaer's reminders give these:

- Stamina + Heartbeast against 3 + the magnitude, to change form despite a shapechange or an Aegis (DE p. 234)
- the heartbeast's temperament, when the Heartbeast specialty names one of the book's beasts (pp. 19-21)
- Theriomorphy's roll against 9 (p. 27)
- with an inner heartbeast, the roll against 9 to take it, and the Magic Might of the Great Beast they would become at Final Twilight, 5 x Heartbeast (pp. 24, 32).

The other casting Virtues and Flaws get a line each there too, with their page (DE pp. 70-145):

- Boosted Magic and Flexible Formulaic Magic
- Atlantean Magic's Water-way, Storm and Body-of-water
- Enduring and Short-Lived Magic's durations
- Exotic Casting
- Faerie-Raised Magic, which includes Spell Improvisation
- Harnessed and Tethered Magic
- Life-Linked Spontaneous Magic
- Imbued with the Spirit of (Form)
- Painful Magic and Slow Caster.

Clumsy Magic and Inconstant Magic each take 3 off the Aiming line's Finesse. With Incompatible Arts, typed as "Intellego Herbam, InAn", a known spell using a pair it rules out, even as a requisite, says it can't be cast. In a fight, Cast a Spell applies Incompatible Arts, Painful Magic's level of pain and Life-Linked Spontaneous Magic's extra Fatigue.

**Spontaneous levels.** A Spontaneous spell uses its own Casting Score, without the Virtues that count only for Formulaic spells (Method Caster's +3, Poor Formulaic Magic's -5). A Deficiency halves the total. When that makes the levels differ from the grid's score / 5, a second grid gives the level each pair reaches without Fatigue (DE pp. 98, 125, 141, 214). Method Caster's +3 is lost with anything but firm words and bold gestures, and a Deficiency counts when its Art is a requisite (DE pp. 98, 312).

These change it too, and the second grid's heading says how:

- **Ceremonial Spontaneous Magic** casts Spontaneous spells only ceremonially, adding Artes Liberales + Philosophiae, a magnitude a quarter of an hour (p. 122).
- **Unstructured Caster** casts Formulaic spells as Rituals, with Artes Liberales + Philosophiae and their vis (p. 149).
- **Weak Spontaneous Magic** always divides by 5 and can't exert (p. 153).
- **Difficult Spontaneous Magic** only exerts, dividing by 2 for a Fatigue level, so the grid shows a dash (p. 126). The two together allow no Spontaneous magic.
- **Diedne Magic** may divide by 2 with a stress die without Fatigue, or exert with the lowest Art doubled (p. 76).

Spell Improvisation depends on the spell, so it stays a reminder.

**Casting options** (DE pp. 215-218, 223, 260), each a line under the scores with the magus's own figures:

- **Fast casting.** Speed is Quickness + Finesse + stress die against the foe's Initiative, +3 with Fast Caster, -6 for each spell after the first. The score is -10, with +2 botch dice and no vis. Knowing an attacking spell's Form takes Perception + Awareness + die against 15 - its magnitude.
- **Ceremonial casting.** It adds Artes Liberales + Philosophiae, and props +1 to +5, instead of words and gestures. It takes 15 minutes a magnitude, 3 in a laboratory, and needs experience in one of the two.
- **Concentration.** Stamina + Concentration, with three times the Wound Penalty and the Fatigue penalty. A failure ends the spell and adds a botch die.
- **Aiming.** Perception + Finesse, less the Wound and Fatigue penalties, +6 for each size step past a basic Individual.
- **A talisman's attunements**, best first. The best that applies adds to the score while the magus touches it.

**A known spell's lines** count the Golden Cord of the magus's bound familiar, which takes its score off the botch dice but never below one (DE pp. 227, 267). They say that a mastered spell has no botch dice when calm. Extra pawns of vis on a Ritual still add +2 each, and each Art's pawns are limited to its score (DE p. 216). A Ritual's Fatigue past unconsciousness becomes a wound. One level more is Light, two Medium, three Heavy, four Incapacitating (DE p. 213).

The spell's **Mastery** special abilities, typed on its Mastery, are counted (DE pp. 225-226). Quiet and Still Casting count in the score, and the rest in a Mastery line. They are these:

- Quiet Casting and Still Casting
- Fast Casting and Ceremonial Casting
- Penetration and Magic Resistance
- Imperturbable Casting and Multiple Casting
- Obfuscated Casting, Precise Casting and Quick Casting.

House Mercere's masteries are read too, each on the spell's casting lines (Houses of Hermes: True Lineages pp. 99-100):

- Adaptive Casting
- Boosted, Disguised, Harnessed, Stalwart and Tethered Casting, not for a Ritual
- Lab Mastery and Learn From Mistakes.

Adaptive Casting follows the Errata (p. 46). The mastery serves on any spell similar to the mastered one, not only General spells. A similar spell has the same Technique and Form, and either the same base level at another Range, Duration or Target, or the same Range, Duration and Target (DE, Similar Spells, p. 260; the troupe has the last word). Each similar spell's casting lines name the masteries it may borrow. When two or more apply, only one serves a casting, its score with its own special abilities, never added together. Lab Mastery on the similar spell a lab plan names adds its Mastery score to the Lab Total, on top of the similar spell's bonus. Societates (p. 33) reprints these, and its Fast Trigger for items is the DE's (p. 257), already on the device forms.

**Mutantum spells** (True Lineages pp. 101-102; Errata p. 46). A known spell that is Boosted, Harnessed or Tethered says what each does on its casting lines:

- **Boosting** spends vis to raise its Range, Duration, Target or size (see [Boost a Spell](help:boost-spell)). It's cast, tires and penetrates at its own level.
- **A harnessed spell** is ended at will by concentrating.
- **A tethered spell's** control passes to another, or to an object that casts it on a fit target.

A magus without the Virtue for a quality is told they can't cast it. The reminders give Mutantum Magic and Tamed Magic. The Cult of Heroes' **(Characteristic) of the Followers** rituals raise a Characteristic by one to no more than 0, and **of the Heroes** to no more than +5. Mercury's Blessing is a Mercurian Ritual (p. 103).

**Fenicil's rituals** (True Lineages pp. 76-77). A magus who has one of the rituals as an Ability sees its Ease Factor, the Wizard's Communion it needs, its vis and casting time. The rituals are Wisdom of Athena, Sight of Alatheia, Veil All Eyes, The Oath of Truth and The Will of Alatheia, and the greater Curse of Thoth, Curse of Mars and Call for Justice. The leader rolls Stamina + everyone's score in the ritual + aura + die. The excess over the Ease Factor is its Penetration, and there's no botch unless it's stressed. An Unstructured Caster can't cast them. Performance Magic (DE p. 101) and Spell Binding (The Mysteries Revised Edition pp. 27-28) are noted when a magus has them.

**Certamen.** A Tremere's Minor Magical Focus in certamen doubles the lower of the two Arts (DE p. 233). A Deficient Art halves the total it's in.

**Schools of certamen.** At the start of a duel each magus fights either as a follower of their school, or in the style of various schools (True Lineages p. 135). A follower has the school's strongest techniques but can't change school. Fighting in various styles gives weaker imitations, which may be swapped at the start of each round. The Gladiator school is the basic rules.

Most other schools trade one total for another, up to a multiple of Finesse (pp. 136-138):

- the Andabatus, Attack for Defence
- the Hoplomachus, Defence for Attack, and more Defence in a round the duelist doesn't attack
- the Provocator, Resistance for Initiative
- the Retiarius, Initiative for later Attack Advantage
- the Saggitarius, Attack for Defence, with a hit costing one Fatigue level at most
- the Laquerius, Defence for a noose.

Others act when the duelist lands a blow and declines to do damage:

- the Essedarius frightens
- the Gladiatrix reads the foe
- the Pumilius amuses
- the Velitus wears down Resistance
- the Scissor's hit after a skipped attack cuts deeper.

The Bestiarius, for Bjornaer only, uses Heartbeast in place of Finesse in a Muto duel, and adds twice it to Resistance in Muto Corpus or Muto Animal. A Bjornaer fighting in its style adds their Heartbeast to Resistance in any duel (True Lineages p. 136). Charon and Bone-biting are tricks with no followers today.

**Hybrid magic.** A magus whose magic is also non-Hermetic has it counted too, and a line for each kind closes the section:

- **Holy Magic** (the Ability, or the Virtue that gives it). It stands in for Magic Theory in every Lab Total and in the vis the magus may use. A Divine or Magic aura adds its full score, a Faerie aura half, and an Infernal aura takes nothing away. Living in a Magic or Divine aura gives no Warping (Realms of Power: The Divine, Holy Magic).
- **Chthonic Magic.** A Magic or an Infernal aura adds its full score, and living in either gives no Warping (Realms of Power: The Infernal, Chthonic Magic).
- **Faerie Magic** (House Merinita's Virtue, or its Ability). A Faerie aura adds its full score as a Magic one does, neither adds botch dice, and living in either gives no Warping (Definitive Edition p. 236). Finishing Touches checks that a Merinita with no faerie Virtue or Flaw starts with the Warping Point their parens gave them.
- **Hermetic rites** (a Faerie Method and Power) are rituals from the faerie rite guidelines (Realms of Power: Faerie, Hermetic Rites). The magus may count a Ritual's aura from the Faerie column of the realm table when it's better than the Magic one (p. 121).
- A Ritual adds the magus's best **Method + Power** of the style's realm instead of Artes Liberales + Philosophiae, when that's more.
- **Goetic Arts.** In a Goetic Art's total, a magus may use Rego for the Art and Vim for the Realm Lore, when they're higher (Realms of Power: The Infernal, Goetic Magic).

A lab plan counts two of these (see [Lab Total](help:invent-spell-total)):

- Holy Magic halves the Lab Total from a Hermetic Lab Text, and halves reading from a Hermetic book on an Art or an Arcane Ability. A text by a holy magus, or one ticked Holy on its form, isn't halved.
- Chthonic Magic stands in for Magic Theory on a dark or sinister effect.

What can't be worked out, such as Chthonic Magic's sinful acts and the faerie rite parameters, is written in that closing line as the books word it.

A character with **Dead Language: Adamic** has a note (Ancient Magic pp. 10-11). Any Adamic adds +1 to the Penetration multiplier against a target named within Voice range, with an Arcane Connection to it. Fluent (5 or more), the named target is always a lasting connection (+4), so +5 in all. A mundane thing whose name they know counts as an Hours connection.

A holder of a **Secret of the Grigori** has a note of its three Arts. Their vis may stand for one another, and requisites among them are ignored. Held as the Supernatural Virtue, not a Legacy, vis used so in a Divine or Infernal aura rolls double the botch dice (p. 67).

### Raw Vis
<!-- help: section-raw-vis-hermetic -->

The pawns of raw vis the magus holds, by Art. It's the same pool as the Raw Vis section in [Inventory](help:section-raw-vis-inventory).
<!-- tui -->
[Give](help:give) in More (`m`) gives vis to a covenant, laboratory or
another magus, and both sides' Diaries record it.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, gives the chosen Art's vis to a
covenant, laboratory or another magus ([Give](help:give)). Both sides'
Diaries record it.
<!-- /gui -->

### Known Spells
<!-- help: section-known-spells -->

<!-- tui -->
The spells the magus knows, chosen with `a` from the spell catalog and the
saga's own spells. The picker shows the highlighted spell's details under
the list, description included, so you can compare spells before choosing.
`e` edits the spell's Mastery score and XP, its Mastery Abilities and
**Favourite** (shown on the [cast at a glance](help:cast-glance)). The
details panel shows the spell and what the magus casts it at. Share Spell
in More (`m`) makes a spell the magus invented available to the whole saga.
<!-- /tui -->
<!-- gui -->
The spells the magus knows, chosen with **Add** from the spell catalog and
the saga's own spells. The list shows the chosen spell's details beside it,
description included, so you can compare spells before choosing. **Edit**
edits the spell's Mastery score and XP, its Mastery Abilities and
**Favourite** (shown on the [cast at a glance](help:cast-glance)).
Clicking a spell shows it in the inspector, with what the magus casts it
at. The table sorts by any column you click, and the box above it filters
the spells by name. A spell the magus invented has a **Shared** tick in its
Edit form, which makes it available to the whole saga. The list's Shared
column marks it, with ✓ once shared and "Not yet" before.
<!-- /gui -->
Once shared, a spell stays shared.
<!-- tui -->
The picker offers only spells from books in play, and F3 shows the rest.
<!-- /tui -->
<!-- gui -->
The picker offers only spells from books in play, and **Show everything**
lists the rest.
<!-- /gui -->
A spell already known from a book that goes out of play stays, marked "(not in play)".

A demon-hunter's spells say what they do at their level (Realms of Power: The Infernal pp. 121-122, with the Errata's levels):

- Demon's Eternal Oblivion
- Fanning the Infernal Flames
- The Wicked Jar
- Bind the Devil's Hands
- Early Punishment for the Sinful Witch
- Exorcise the Filthy Spirit
- Lash of the Chastened Servant
- Adjuration of the Hell-Sworn Spirit
- Cleanse the Verminous Vis
- Command the Vile Spirit.

Two Mastery abilities are read by name:

- **Apotropaic Mastery** adds Mastery Score x Hierarchy to the level of effect of a spell on Infernal Might (pp. 122-123).
- **Goetic Mastery** adds the fitting Goetic Art to a spirit spell's Casting Total, and Hierarchy x 5 to its Penetration against a demon (p. 124).

<!-- tui -->
More (`m`) here offers [Craft by Magic](help:craft-magic).
<!-- /tui -->
<!-- gui -->
**Craft by Magic**, in **Magic Outside the Lab** under Raw Vis, works out a craft
spell's Finesse roll ([Craft by Magic](help:craft-magic)).
<!-- /gui -->

<!-- tui -->
With Houses of Hermes: Societates in play, More (`m`) here also offers
[Cast in a Lacuna](help:cast-in-lacuna).
<!-- /tui -->
<!-- gui -->
**Cast in a Lacuna**, in **Magic Outside the Lab** under Raw Vis (with
Houses of Hermes: Societates in play), works out a spell cast in a city
([Cast in a Lacuna](help:cast-in-lacuna)).
<!-- /gui -->

<!-- tui -->
With the saga option Learning cantations in play, More (`m`) here offers
[Learn a Cantation](help:learn-cantation).
<!-- /tui -->
<!-- gui -->
With the saga option Learning cantations in play, a button beside Known
Spells offers [Learn a Cantation](help:learn-cantation).
<!-- /gui -->

## Current Location
<!-- help: whereabouts -->

A character's Casting Scores and Penetration, and their tradition's and
Mysteries' totals, count the aura where they are. At home, that's their
covenant's.

<!-- tui -->
**Current Location**, in More on Casting Scores, sets where they are now
when away.
<!-- /tui -->
<!-- gui -->
**Current Location**, the button at the top of the Hermetic Magic chapter
under the line saying where they are, sets where they are now when away.
<!-- /gui -->
Choose a place of the saga, whose aura and its kind are used, or somewhere
else, with its aura and realm typed. A foreign realm's aura then counts as
the realms' interactions say (DE pp. 410-411). A Magic magus's casting is
lowered in a Divine or Infernal aura, for example. The Casting Scores say
they're away.

Their seasons, laboratory work, aging and warping stay at home. Set them
back **At home** when they return. While they're a guest at another
covenant ([Stay as Guest](help:guest-stay)), **Where he is a guest** takes
the place of At home and counts that covenant's aura.

## Stay as Guest
<!-- help: guest-stay -->

Magi are expected to take in visiting magi, even unannounced (DE p. 518).
A magus copying from a library that isn't their own enjoys *scribal
hospitality*, usually for a payment or a service (DE p. 381). Guests count
their stays in seasons, and are charged for their quills, vellum and ink
(Covenants pp. 96-98).

<!-- tui -->
**Stay as Guest**, in More on Casting Scores, makes the magus a guest of
another covenant of the saga.
<!-- /tui -->
<!-- gui -->
**Stay as Guest**, a button under Current Location at the top of the
Hermetic Magic chapter, makes the magus a guest of another covenant of the
saga.
<!-- /gui -->

- **Staying at**: the host, any covenant but their own. **Not a guest
  anywhere** ends the stay.
- **Since** and **Until the end of**: when the stay began, and its last
  year. Leave the last year blank for an open-ended stay.
- **Fee**: pawns of vis, pounds of silver or seasons of service a year, or
  no fee, and **How many**.
- **May study and copy from its library** and **Has a laboratory there**,
  and the **Conditions of hospitality** in words.

Choosing a host of the Rhine Tribunal fills in its Peripheral Code's terms
(Guardians of the Forests p. 20):

- a stay of at least three years and at most seven. A stay outside those
  years isn't saved.
- three pawns of vis a year, for which a season's service may stand in
- no laboratory owed.

Elsewhere the books set no terms, and the troupe agrees them.

While the magus stays, their casting counts the host's aura, unless
Current Location says they're elsewhere. The Casting Scores say so. With
the use of the library, its books join those they may study and copy in
their season's plan. Their seasons, laboratory, aging and warping stay
with their own records. Starting and ending a stay are written in their
Diary and the host's. The host lists them under
[Guests](help:section-cov-guests), where **Pay the Fee** takes each
year's.

House Jerbiton keeps a code of courtesy between guest and host (Houses of
Hermes: Societates p. 51). Breaking it insults only Jerbiton magi.

- The guest announces themselves, their business and when they'll leave.
  They bring a small gift, are good company, help if trouble comes and
  leave when asked.
- The host says plainly whether they offer hospitality. They give counsel
  on the region's dangers, food, wine and a bed, protection, and a gift in
  return. An uneven exchange is a debt of honour.

The app keeps no rules for it. Give the gifts with [Give](help:give), and
write the rest in the Diaries.

**See also:** [How to stay at another covenant](help:guide-guest-stay)

## Certamen
<!-- help: certamen-duel -->

**Certamen** plays a duel between two magi of the saga (DE pp. 231-233).
Choose the rival, the Technique, the Form and the stakes. By custom the
challenger picks the Technique and the challenged the Form.

Each side has a plan for the whole duel:

- the Art they attack with: the Technique, the Form, or whichever is
  better for them
- the pawns of vis of the Art used they spend a round, on attack and on
  defense. Each pawn is +2, at most their score in it.
- when they concede: at -1, -3 or -5 of Fatigue, or never.

Initiative (Quickness + Finesse + a stress die) is rolled once. Each round
the winner attacks first, then the other. The attack is Presence + the
attacking Art + a stress die, against Perception + the other Art + a
stress die, and a tie goes to the defender. What the attack wins by is
added to Intelligence + Penetration, less Stamina + Parma Magica. Every
five points or fraction costs a Fatigue level, whose penalty then counts.
A Tremere's Focus counts the lower Art double.

The duel ends when one magus falls unconscious or concedes. The victor may
cast a spell of the duel's Arts at an unconscious loser, whose Parma is
circumvented. One who concedes keeps their Parma.

The panel shows both duelists' totals, and the result shows every round.
**Take the Fatigue they lose** puts it on their sheets. The vis spent
comes off their raw vis, and both Diaries record it.

A magus who'd change plan mid-duel, or a duel broken by a lost
Concentration roll, is played at the table. A magus can botch (DE p. 231),
but the book doesn't say what that does. So a botch stops the duel there.
The storyguide says what comes of it, and the rest is played at the table.

## Craft by Magic
<!-- help: craft-magic -->

The Finesse roll a craft spell needs (DE pp. 306-308, Magical Craft).
**Close** keeps nothing. **Roll** rolls it once and says how it went,
keeping nothing either.

- **Rego** shapes raw materials as a craftsman would. Roll Perception +
  Finesse against the Ease Factor of the hardest task the spell covers.
- **Creo** makes a working example of the thing with no roll, as a work of
  craft of Ease Factor 6. Its details fall as chance has them. To fix
  details, roll Intelligence + Finesse against:
  - 0 for one basic property
  - 3 for two or three, or for one precisely
  - Rego's Ease Factor for an elaborate specification or a better-quality
    item.

The Ease Factors for Creating and Crafting Objects already hold the +3 for
magic and a day's work:

- Trivial 3, Simple 6, Easy 9
- Average 12, Hard 15, Very Hard 18
- Impressive 21, Remarkable 24, Almost Impossible 27.

More work adds +3 for a month (or thirty craftsmen for a day), +6 for a
season and +9 for a year. Given a mundane craftsman's Ease Factor or a
City & Guild Workshop Total, the app adds the +3.

The roll takes the Wound and Fatigue penalties, -3 for each of Clumsy and
Inconstant Magic, and the spell's Precise Casting. A failed Rego roll
still rearranges the materials, into nothing useful. A Rego botch looks
right but has a hidden, fatal flaw. A failed Creo roll still makes the
thing, without the details. A Creo botch makes something that hinders the
caster.

## Open a Tunnel
<!-- help: open-tunnel -->

<!-- tui -->
**Open a Tunnel**, in More on a magus's Known Spells, is offered once they
know a tunnel spell.
<!-- /tui -->
<!-- gui -->
**Open a Tunnel**, in Magic Outside the Lab under Raw Vis, is offered once
the magus knows a tunnel spell.
<!-- /gui -->
It works out a Wizard's War tunnel (Hermetic Projects pp. 78-81; DE pp.
219, 372). Choose:

- the tunnel, and the level it's cast at
- the Arcane Connection and how long it lasts. It may be one of their
  covenant's laboratories', or one held otherwise.
- the sympathetic connections they hold, such as a signature, name,
  horoscope or symbolic representation, at most +2 each
- the target: a magus of the saga, whose own Magic Resistance against each
  Form counts, or a Parma Magica typed, and any Aegis they shelter in.

The inspector gives the Penetration multiplier, 1 + the connection + the
sympathies (DE p. 219). It gives the tunnel's Penetration against the
target's Vim, then each spell the caster knows that fits through. A spell
fits at Touch range or more, and no higher than the tunnel allows:

- Opening the Intangible Tunnel and The Minute of Reckoning, their own
  level
- The Cursèd Day, a magnitude less
- Wizard's Siege, two less
- The Evil Eye and The Master's Message, a magnitude more.

The same multiplier applies to each, since the caster holds an Arcane
Connection to the target. Inside an Aegis every spell must also Penetrate
it, unless its caster holds the Aegis's token (p. 79). Break the Siege
suppresses a tunnel of less than its level + 2 magnitudes (errata p. 81).
**Cast** rolls the tunnel once, and nothing is kept.

## Cast in a Lacuna
<!-- help: cast-in-lacuna -->

A spell cast in a city, from a lacuna or in the Dominion (Houses of Hermes:
Societates pp. 57-58; DE pp. 217-218). **Close** keeps nothing. **Roll**
rolls the casting once and says how it went, keeping nothing either.

A lacuna is a small patch inside a city where the Dominion doesn't hold.
Most have no aura at all, and some have a Magic, Faerie or Infernal one.
Cast from one, a spell meets the lacuna's aura instead of the city's
Dominion. If its target is itself within the Dominion, the Dominion's
penalty stands. Most cities have a Dominion of 3, which is -9 to a
Hermetic Casting Score (p. 58). Subtle gestures and quiet words (-7), or
neither (-15), keep witnesses from seeing a magus at work.

Cast ceremonially, a spell adds Artes Liberales + Philosophiae and its
props' +1 to +5, in place of words and gestures. That needs a Spontaneous
spell, or a Formulaic one with the Ceremonial Casting Mastery ability, and
a magus with Artes Liberales or Philosophiae. The ceremony takes, per
magnitude (DE p. 218):

- 15 minutes, or 12 in a temporary space
- 9 in a space naturally suited, 6 in one carefully designed
- 3 in the magus's laboratory, 1 in a room built for it.

With Mystical Choreography it takes 5, or 1 in any prepared space (DE p.
99). A spell is no greater than the magnitudes the time spent allows.

The inspector shows the Casting Score in the lacuna and outside it, what
the die must reach, the ceremony's time, the botch dice, and the cities
whose lacunae the magus has found.

## Hubris
<!-- help: verditius-hubris -->

More on a Verditius's Personality Traits, shown once they have the Flaw
Hubris or the trait. It records what raised or lowered their pride between
seasons (DE p. 242; Houses of Hermes: Mystery Cults pp. 115, 120). Each is
kept in the Diary.

- **Experience**, for:
  - selling, or making for pay, a charged item or an item of quality, 1
  - repairing or reforging an item for pay, 1
  - a lesser enchanted device 1, a greater one 3, an attuned item 6
  - an automaton, 1 a magnitude of its Might
  - winning the Contest's apprentices' category 1, journeymen's 3 or
    masters' 6
  - declaring a vendetta 1, and winning one 3.

  Learning an Inner Mystery is added by the Initiation season. A magus
  with no Hubris trait yet starts at their first Inner Mystery's score.
- **Refusing a vendetta** (type the magus refused) gives the House
  Reputation Dishonorable 4. It lowers the Hubris score a full point, to
  the experience of the score below, as an Ability would (pp. 115, 119).
  The refusal is kept. They lose the Reputation only once they've regained
  the score they had and waged a vendetta on the magus they refused (p.
  115).
- **Wages the vendetta on a magus he refused**, offered once they've
  refused one, marks it waged. The inspector says what each refusal still
  needs. When the Hubris score is back too, the Reputation goes.
- **Resisting a vendetta**: a Personality Trait that works against Hubris
  (Intelligence without one) + a stress die, against Hubris + the
  challenger's (p. 120). Resisting a temptation to sell is left to the
  troupe, as an opposed Personality roll or a Confidence Point spent to
  walk away.

**See also:** [Personality Traits](help:section-personality-traits),
[Script components](help:guide-initiation-scripts)

## Divination
<!-- help: tmre-divination -->

<!-- tui -->
More on a Hermetic diviner's record (Divination & Augury, or Hermetic
Dream Interpreter).
<!-- /tui -->
<!-- gui -->
In the Deeds chapter under Insight, for a Hermetic diviner (Divination &
Augury, or Hermetic Dream Interpreter).
<!-- /gui -->
A divination answers one question as a Momentary Intellego spell of any
Form would. Its Ease Factor is that spell's level (The Mysteries Revised
Edition pp. 59-60). It makes the Ease Factor or fails, since it isn't
open-ended (p. 62).

- **Casual** (a round): stress die + Perception + Divination + aura + the
  storyguide's bonus for apt omens, +0 to +3 and rarely +5.
- **Ceremonial** (15 minutes a magnitude): stress die + Intelligence +
  Divination + aura, plus:
  - the method's ceremonial bonus, +1 to +5, from the Ceremonial Augury
    Phenomena table (p. 61)
  - the sympathetic bonus, the multiplier of the Arcane Connection and of
    each sympathetic connection (DE p. 220). Horoscopes count only when
    divining by Astrology.
  - a Scrying Device's bonus, its effect's level over 10, rounded up.

  The Errata (p. 50) keeps these bonuses out of a casual divination. **The
  question is about** offers the method's uses from the table, such as
  Aeromancy's weather (+5), and fills in the Ceremonial bonus. Choose
  Something else to type it. A diviner whose Virtue names no method is
  offered the whole table.
- **Penetration**: the total + the Penetration bonus - the Ease Factor.
- With Hermetic Dream Interpreter (pp. 62-63):
  - a **symbolic reading**: stress die + Intelligence + Divination, no
    aura. It's 9 for the dreamer's state, 12-15 for the dream's reasons
    and 18+ for its causes and consequences.
  - **Dream Calling**: stress die + Presence + Divination + aura, against
    6.

The live box shows the total, the chance and the botch dice, one more per
point of a non-Magic aura. **Roll** rolls it and keeps it in the Diary.

## Astrology
<!-- help: tmre-astrology -->

<!-- tui -->
More on the record of a magus with Planetary or Celestial Magic, a
Periapt, or the Astrology method of divination.
<!-- /tui -->
<!-- gui -->
In the Deeds chapter under Insight, for a magus with Planetary or
Celestial Magic, a Periapt, or the Astrology method of divination.
<!-- /gui -->
Each reckoning is a roll of Intelligence + Artes Liberales (Astronomy),
kept in the Diary.

- **Daily Horoscope** (an hour) and **Nativity Horoscope** (a day),
  against 9. They give +1 and +2 sympathetic connections (DE p. 220). The
  astrologer knows of a failure, but not of a botch.
- **Periapt Horoscope** (Periapt, p. 48): against 9 on an equinox or
  solstice. A sound one serves as a one-use Lab Text, with the Lab Total /
  5 charges and an effect up to 5 x Astronomy. A botch wastes the season.
- **Astrological Duration** (Celestial Magic, pp. 49-50): 6 + the units
  wanted (Minutes, Hours, Days, Signs, a year at most). Then -3 with a
  Daily Horoscope, -3 with the exact time measured and +3 for a precise
  end, all halved by a magical armillary sphere. With the time measured
  and a horoscope or sphere, checked over a Diameter, it's a simple die. A
  miss leaves the spell out by up to the shortfall, and a botch botches
  the spell.
- **Favorable Hour** (p. 50): against three times the bonus, +1 to +5. A
  botch makes the bonus a penalty for that hour. The storyguide's quick
  hour is rolled with it.
- **Set a magical armillary sphere** to another place: against 9, a single
  round (p. 54).

The season **Make an armillary sphere** (Work & trade) has two rolls (p.
52):

- design: Int + Astronomy against 12
- build: Dex + Craft: Mechanisms or Clocks against 12, or Blacksmith at -3
  with three more botch dice.

Opening the sphere costs 15 pawns in base metal, 18 in silver or 30 in
gold. Then come Know the Heavens (InVi 29) and Track the Heavens (ReTe
28), p. 53.

Celestial Magic's Laboratory Horoscope, when its die is typed on the plan,
takes its bonus off the pawns of vis that open an invested device. At
least one pawn is still paid (p. 49).

## House Acclaim
<!-- help: house-acclaim -->

<!-- tui -->
More on a magus's Reputations.
<!-- /tui -->
<!-- gui -->
In the Deeds chapter, under Session & Reputation.
<!-- /gui -->
It's shown for a magus of House Bonisagus or House Flambeau, or anyone who
already holds House Acclaim. It keeps the House's own Reputation, House
Acclaim, which grows like an Ability: 5, 15, 30 and 50 points reach 1 to
4. The first award starts it. Each award or roll is kept in the Diary.

**Research made public** (Bonisagus) earns from the Research and Acclaim
Points table (Houses of Hermes: True Lineages p. 21):

- an Art tractatus its Quality/2, a summa its Level/2
- an original spell 1 a magnitude, or 2 by experimentation
- a Talisman 2, a familiar its Magic Might/5, an apprentice trained 3
- each project assisting a magus of higher rank 1
- a stabilized breakthrough 3 a magnitude, a minor breakthrough 15, a
  major one 30
- twice the points for a tractatus or Lab Text taken into a folio
- rediscovering one of Conciatta's Minor Virtues 15, or her True
  Understanding of the Realms 30 (Legends of Hermes p. 45).

The scores are the ranks: boukoloi 1, daduchos 2, cannophori 3,
dendrophori 4, with the Primus above them (TL p. 22). The word takes a
year a point to spread.

**What it does** (Bonisagus, TL p. 22). Its score is added to social rolls
with magi of House Bonisagus, any roll with Presence as a rule of thumb.
It's added to Intrigue or Guile resisting a maga Trianomae, but never to
Presence in certamen. A season searching for an apprentice adds it to the
usual roll, Perception + a stress die against 9 (DE p. 269; TL repeats the
older 12).

- Less still finds one, taken from another magus by right.
- Failing by 5 or more antagonizes that magus, who must be compensated.
- A botch makes them the Major Story Flaw Enemies.

Only a child found is added as a new character. One taken by right is
already that magus's apprentice (DE p. 270), whom the storyguide names.

**An argument over a folio** (Bonisagus, TL p. 23): Presence + Leadership,
or Communication + Artes Liberales, + House Acclaim + a stress die. It's
against the other magus's total, and the higher wins.

**Trianoma's cipher** (TL p. 21): a day's work, Intelligence + Latin +
stress die. It decodes when higher than 6 + the author's Communication +
Intrigue, with +3 for one decoded before.

**A deed** (Flambeau, Houses of Hermes: Societates p. 31) earns a Hermetic
Reputation, known in the whole Order. Deeds before credible witnesses
give experience:

- an exceptional Gauntlet 2 to 5, a Wizard's March 1
- a certamen won 1, or 2 against a senior magus
- a tournament 1 to compete, 3 as a finalist, 5 as champion. A dismal
  showing is -3, still 1 for competing, so -2 in all.
- fighting bravely in a Wizard's War 1 to 3, and winning one twice the
  foe's highest Reputation
- slaying a renounced magus three times their Reputation, a supernatural
  beast its Might/5
- a Primus's order fulfilled, or another glorious deed, as the storyguide
  says.

Losses take experience away:

- a year without a gain -1
- a certamen lost -1, or -2 against a junior magus
- each incident of dishonesty or cowardice -1 or more.

Certamen counts only when it settles a real dispute. House Acclaim never
falls below 0. An ignoble act at 0 starts the bad Reputation you name, at
1 (DE p. 386). Famous may be put in it, starting it at 4, and the Flaw
Miles gives 5 experience points in it.

The inspector shows the points, the score they bring House Acclaim to and,
once it's held, what it does.

**See also:** [Reputations](help:section-reputations),
[Reputation Roll](help:reputation-roll)

## Reputation Roll
<!-- help: reputation-roll -->

<!-- tui -->
More on a character's Reputations.
<!-- /tui -->
<!-- gui -->
In the Deeds chapter, under Session & Reputation.
<!-- /gui -->
Has someone heard of one of the character's Reputations? A stress die +
the Reputation's score (a bad one's size) must equal or beat the Ease
Factor for where the listener is (DE pp. 28-29). The Reputation's type says
which column counts:

- 0 in the same village, parish or covenant
- 6 in the same town, diocese or Tribunal
- 9 in the same county, province or the whole Order
- 12 in the same country or the whole Church.

The more it beats the Ease Factor by, the more the listener has heard.
Between two magi of the same Jerbiton league, every Reputation counts 3
higher (Houses of Hermes: Societates p. 53). The roll is kept in the
Diary.

**See also:** [House Acclaim](help:house-acclaim)

## Gain or Lose in Play
<!-- help: vf-change -->

<!-- tui -->
More on a character's Virtues or Flaws: a Virtue or Flaw that comes or
goes during the saga, kept in the Diary with what happened.
<!-- /tui -->
<!-- gui -->
The button on the During the Saga strip under a character's Virtues and
Flaws, above Powers: a Virtue or Flaw that comes or goes during the saga.
<!-- /gui -->
Saving adds a Diary entry for the season. It says what changed, how it
came about, the story you gave it and the rules it follows.

- **Gain a Flaw**, by:
  - mishap, such as an injury, an amputation or a disease. A lost hand is
    always Missing Hand.
  - the character's own actions, such as a feud, a debt, an animal
    companion or offending a faerie
  - magic, such as a curse. A hedge wizard's usually wears off, and a
    creature that spends Might lays a lasting one.
  - Warping.

  A changed circumstance is a Flaw only if it affects the game, seeds
  stories or changes how the character is played (Grogs p. 62).
- **Gain a Virtue**, by:
  - magic. Most grants are temporary, and a lasting one comes from a
    supernatural being or the Goetic Arts.
  - Initiation, which first needs a score in the cult's or tradition's
    Organization Lore
  - the character's own actions, such as Social Contacts for an agent
    recruited, or Protection for a powerful friend
  - severe Warping.

  A Virtue that changes how experience is gained doesn't change what was
  gained before (Grogs pp. 62-63).
- **Lose a Flaw**, mostly by the ways a Virtue is gained, though not every
  way suits every Flaw. Initiation won't grow back a lost hand (Grogs p.
  63).
- **A temporary Virtue or Flaw ends**: one gained by magic for a while is
  taken off the sheet, and any Characteristic it moved is put back.
  - Most Virtues granted by magic are temporary, such as a gruagach's
    spells, an Object of Virtue or faerie wizardry. Hedge curses that lay
    Flaws are usually limited in duration too (Grogs pp. 62-63).
  - So a Virtue or Flaw gained by magic is ticked **Temporary** unless you
    clear it, with the season and year it ends if they're known. A year
    alone ends at its Winter. The sheet marks it "temporary, until Winter
    1225".
  - When its last season is advanced past, the character's Diary and the
    season record say it has ended. It stays on the sheet until you take
    it off here, since a story may renew it.
- **A change of Social Status** replaces the old status with the new. A
  status whose description allows it may be kept beside it (Grogs p. 61).
- **Exchange one chosen wrongly**, with the troupe's approval. An
  established character exchanges only a Minor for a Minor and a Major for
  a Major on the same side, never one that changes Characteristics. Tick
  New to the saga for larger changes (Grogs p. 61).

The inspector warns where the books advise against a change:

- a grog gaining a Story Flaw or a Major Virtue, unless they're becoming a
  companion
- a second Story Flaw
- more Personality Flaws than the guideline allows (DE p. 63).

A second Major Personality Flaw is refused (DE p. 63). Warping says what
the character's Warping Score has brought them (DE p. 391). A magus's
comes through Twilight (DE pp. 229-230).

**See also:** [Aging & Warping](help:section-aging)

## Pilgrimage
<!-- help: pilgrimage-more -->

A pilgrimage's road (The Church pp. 15-19), each step written in the
Diary. Its aim sets its Target Level:

- **18**, a minor pilgrimage of a single season and story. It may gain a
  Minor Virtue, lose a Minor Flaw or Virtue, remove a negative Personality
  Trait or meet a penance. It may also gain a Minor Supernatural Ability
  of the Divine.
- **30**, a major pilgrimage of several seasons. It may gain a Major
  Virtue, lose a Major Flaw, ask for a miracle, self-initiate in Holy
  Magic (with True Faith) or meet a penance. It may also gain a Major
  Supernatural Ability or Divine Methods and Powers.

No pilgrimage grants or removes Hermetic Virtues and Flaws, or background
ones such as Privileged Upbringing and Educated (p. 16). The app treats
every Virtue that gives experience at creation as background. A Divine
Supernatural Ability gained is added at 1, without the Gift's penalty.
Every aim needs the troupe to agree it suits the pilgrim.

- **Begin a pilgrimage**: its name and Target Level. Grogs may go too.
- **An Oppositional Element overcome**: its value goes toward the Target
  Level (p. 17).
  - +3 natural hazards, a temptation the pilgrim is prone to, another
    trial
  - +6 bandits, religious or political enemies, storms
  - +9 a supernatural encounter, a shipwreck, distractions to abandon it
  - +12 direct demonic opposition.

  Travel counts once, only the higher: +3 in a Christian land outside the
  pilgrim's homeland, or +6 through non-Christian or heretic lands. Each
  season on the road (the Pilgrimage season activity) is +3.
- **An Oppositional Element failed**: the aim fails unless a later element
  overcome remedies it.
- **Claim the pilgrimage's aim**, once the Target Level is reached and no
  failure is left unremedied. The Virtue is added, the Flaw or Trait taken
  away, or Holy Magic added. A penance met or a miracle asked is written
  in the Diary for the troupe. The pilgrim must have avoided mortal sin on
  the road and confessed their venial sins on arrival (p. 18).
  - The traits offered for removal are those with a negative score or
    leaning to a sin, such as Cruel +3, which is Kind -3 (The Church p.
    20). The book doesn't say what "negative" means.
  - Removing any other trait is for the troupe to agree and do by hand.

At a saint's shrine, a pilgrim with a Devotion to the saint gains 10
Devotion Points, +5 for each further site of the saint's life, and up to 5
for relics seen (p. 19).

## The Enigma
<!-- help: tab-criamon -->

A Criamon magus's path toward the Enigma. It shows the path they walk, its
five stations and what the next avenue needs, and their stigmata (Houses
of Hermes: Mystery Cults pp. 50-51, 58-73). It's there only for a magus of
House Criamon, or one Initiated into the Enigma.

**You type:** the path (or let their stations show it), their guide, and
their stigmata.

**The app works out:** which stations they hold, from their Virtues, and
what the next avenue needs: their House Criamon Lore, and its Target
against the guide and the Script. When an Initiation season follows an
avenue, it works out the station's Virtue, its Ordeal's Flaws and the
season it was reached.

**See also:** [Hermetic Magic](help:tab-hermetic),
[Planning](help:tab-planning)

### The path
<!-- help: section-char-criamon-path -->

The path the magus walks: of the Body, of Seeming, of Strife, of Walking
Backwards, or the Path of the Mirror. Only the Primus follows the Mirror,
and its stations aren't printed (pp. 57, 59). Change Path offers it only
to a magus whose Hermetic background names them as the House's Primus.
Unless Change Path names one, the path is the one most of their stations
are on. With none, they walk the Winding Path (p. 58).

**Station:** how far along it they are.

**Enigmatic Wisdom** and **House Criamon Lore**. A station needs the Lore
at its place on the path + 1, so the fifth needs 6 (p. 60). The Lore is
the sheet's Mystery Cult Lore: Criamon, and House Criamon Lore under that
name counts too.

**Flaws of the path:** the Flaws the stations' Ordeals have given them.
Every follower of a path ends Disfigured, with Vow or Pious (p. 60).

**Guide:** the guide's Presence + House Criamon Lore. The book's Scripts
assume 6, and the House always provides such a guide. So with none named,
the magus has the House's (Presence + Lore 6). A ghostly Primus at the
Cave of Twisting Shadows sometimes guides, with Lore 9 and the Presence
they had in life (p. 60). Any character who knows House Criamon Lore can
guide (DE p. 387). The app shows a guide not of the House as a warning,
its own reading: the books don't call it unusual.

**Next:** the next avenue, its station, and the Target against the guide +
the Script. The Target is 21 for a Major Virtue, less their best past
Ordeal's reduction (DE p. 388). A head bound in infancy, or castration,
broken bones or severed joints, gives an aptitude for one path, set on
Change Path. It's +3 to that path's first station only (p. 51).

One path at a time. A magus who steps onto another keeps only their
Enigmatic Wisdom of the old path's stations, which are listed as set
aside. Rejoining, they regain them. Only the Primus keeps theirs on the
Path of the Mirror (p. 58).

<!-- tui -->
e changes the path, the guide, a ghostly Primus's Presence and the path
their head binding suits. m (More) offers Follow an Avenue.
<!-- /tui -->
<!-- gui -->
Change Path and Follow an Avenue sit beside the title.
<!-- /gui -->

### Stations
<!-- help: section-char-criamon-stations -->

The path's five stations, each a Major Mystery Virtue. Each shows its
name, what it gives, its Script against the Target the book prints, and
when the magus reached it. The printed Target already counts the Ordeals
of the stations before it. When it was reached is the season, kept when an
Initiation season reached it, or "reached" for one held before.

The next is marked "next", or "needs Lore n" when their House Criamon Lore
is short. Choosing one shows its avenue in full (pp. 61-71; Errata p. 55
for the Path of Strife's fourth, Target 18). The Path of Walking
Backwards' fifth shows its reduction as the book prints it, -6 for its
second Initiation since a Major Ordeal (p. 71). The app's Ordeal sizes are
the Definitive Edition's Minor, Medium and Major (DE p. 388).

### Stigmata
<!-- help: section-char-stigmata -->

A Criamon magus's marks: where, the mark, what it marks and when. A new
one appears, or older ones move, for:

- a station reached, or a rise in Enigmatic Wisdom
- an Inner Mystery learned
- an apprentice begun or finished
- a familiar sought or bound
- a great work of the Art.

The first usually comes with the Riddle of the Magus, and loops on the
wrists after Twilight (p. 50). They have no mechanical cause and can't be
removed, even by magic. Another Criamon magus reads what one marks with
Intelligence + Enigmatic Wisdom against 6 (p. 60). A tattoo that is an
enchanted device is an ordinary device on the character, not a stigma (p.
51).

## Research
<!-- help: tab-research -->

A magus's Arcane Discovery, which Houses of Hermes: True Lineages calls
original research. It holds the goals they're working towards and every
season spent on them (DE Chapter 8, Experimentation and Arcane
Discovery).
<!-- tui -->
Only a magus has this tab. Choosing a goal shows where it stands and the
odds of its next season. Choosing a season of the log shows its roll on
the Extraordinary Results chart.
<!-- /tui -->
<!-- gui -->
Only a magus has this chapter. Each goal is a card with the road of its
research drawn under it. The steps behind it are filled in green, and the
one it's on is ringed in red. Clicking a goal shows it in the inspector
with the odds of its next season. Choosing a season of the log draws its
roll on the Extraordinary Results chart below the log, with the band it
landed in filled in.
<!-- /gui -->

**You type:** the research goals, and the points the storyguide sets for
a secret target.

**The app works out:** each season's roll, any move of it toward a
Discovery, the points a stabilized Discovery adds, and the chances of the
next season.

**See also:** [Hermetic Magic](help:tab-hermetic),
[Experimenting](help:guide-lab-planning-experiment)

### Research Goals
<!-- help: section-research-goals -->

The Breakthroughs the magus is working towards. Each shows what it is,
whether it's Minor, Major or Hermetic, its target in points and what
reaching it grants. When the storyguide keeps the target secret, it shows
only the points gained. You type these. The app adds points to a goal when
a season of research towards it is applied (DE Chapter 8, Arcane
Discovery; Houses of Hermes: True Lineages, Chapter 1: House Bonisagus,
Original Research).

A goal's details also show:

- when a failed stabilization must be tried again
- which spells and enchantments have already given it a Discovery. Each
  gives one at most.
- where the goal stands, step by step: Goal agreed, Seek, Discovery,
  Stabilize, Breakthrough, Spread
- the odds of its next season. That's the chance of a Discovery at each
  risk the magus's Magic Theory allows or, with a Discovery waiting, the
  chance that stabilizing it succeeds.

A new goal may start from an **Integration**. Choosing one fills in its
name, kind, points and what it grants, which you can still change (Ancient
Magic, Introduction, The Breakthrough). The Integrations are:

- the breakthroughs Ancient Magic names for folding a lost tradition into
  Hermetic magic, such as Canaanite Magic, Hermetic Rune Magic, Mutable
  and Awakened Devices, the Grigori Legacies, the Limit of Vis, the Event
  Duration and Unlimited Range
- Hedge Magic's Subtle Opening and Quick Charged Items
- True Lineages' discoveries of House Bonisagus: the six Parma Magica
  folds of the Arma Magica, Parmulae, Figurine Magic and Realm-aligned
  spells.

The books' magi have reached four more breakthroughs, and the Integration
picker fills in each. Their books give no points, so each takes its kind's
usual target.

- **Fertile Longevity Ritual** (Minor, 30; Magi of Hermes p. 20). A
  Longevity Ritual leaves its subject permanently sterile (DE p. 261).
  Once a magus has reached this, the rituals they make leave their subject
  fertile.
  - Like any Minor Breakthrough, any Hermetic magus with a Lab Text for an
    effect using it, or trained by its discoverer, can use it too (DE p.
    281).
  - The app can't tell which Longevity Lab Text uses it. So a Longevity
    Ritual's plan has a Fertile (Lab Text) tick for a magus who hasn't
    reached it, naming the Longevity Lab Texts they have at hand. The
    ritual's season says which it does.
- **Hermetic Metamorphosis** (Major, 45; Magi of Hermes pp. 82-83). It
  gives the Minor Hermetic Virtue of that name. Its holder grafts organs
  onto an animal by Harmonic Metamorphosis of the Beast, which only they
  can cast. The surgery is Dexterity + Chirurgy against 9, +3 for an organ
  added rather than swapped, and +3 more to give a Virtue. On a failure
  the animal dies soon after, and a botch makes a monster. A human
  recipient needs a further breakthrough.
- **Hermetic Viresculture** (Major, 45; Legends of Hermes pp. 72-75). It
  gives the Supernatural Ability of that name, its points as experience
  (DE p. 281). Only those Opened to the Hermetic Arts can use it.
- **Viresculture of Lesser Enchantment Vis** (Minor, 30; Legends of Hermes
  p. 73). Living Lesser Enchantment Vis may be made a Stirps, its effect's
  level standing for Magic Might. It builds on Hermetic Viresculture.

Ancient Magic's chapters add what their integrations need. A goal named
for one (the Grigori Legacy, the Limit of Vis, Mutable Device, Awakened
Device, the vis-less devices) shows in its details the Arts and kind of
effect its Insights produce. It also lists the texts, relics and teachers
that give Insight:

- for the Grigori, the second book of The Enigma of the Sons of God, the
  Stelae of the Watchers on Mount Hermon and Shamsiel on Mount Ararat
  (Ancient Magic pp. 69-73). The Stelae are also a Magic Theory summa,
  Level 8, Quality 6.
- for Heron, his uncorrupted Greek texts, a working mechanica and an
  anima (pp. 76, 79).

A magus who holds a Secret of the Grigori gains one extra breakthrough
point each season of research toward the Grigori Legacy. One who holds a
Secret or a Legacy gains one each season toward the Limit of Vis (p. 67).
The app adds it when the season is applied and notes it in the Diary.

Two more choices follow Mutable Device (p. 79; DE p. 281):

- **Awakened Device, after Mutable Device**: a Minor Breakthrough of 30
  points, once Mutable Device is reached
- **Mutable Device without the Virtue**: the second Major Breakthrough
  (45), which lets any magus with a Lab Text make them.

House Bonisagus's example discoveries (True Lineages pp. 30-34) say what
they give once reached: the six Parma Magica folds, Parmulae and
realm-aligned spells. A magus counts as knowing one when one of their
research goals of that name is reached, whether they made it or were
taught it. Record a taught fold as a reached goal. A magus may know as
many folds as their Parma Magica score. The notes under their
[Casting Scores](help:section-casting) then give:

- each fold's resistance:
  - Ablativa doubles Parma, worn down by each Penetration it stops.
  - Absorbea, Repercussa and Condensa against other Forms halve it,
    rounded up.
  - Condensa doubles it against its chosen Form.
  - Custodia gives no Parma resistance but adds twice Parma to Defense.
  - Restricta is Parma - 3.
- the Parmula, a level 44 lesser device giving Magic Resistance 30 for a
  year, for 5 pawns and a Rego Vim Lab Total of 88
- the realm-aligned table (p. 34).

Figurine Magic's Ease Factors show for anyone with the Virtue.

**Aetheric Magic** is a Hermetic breakthrough of 100 points, at least 20
of them from each Technique's projects. It gives the Major Hermetic Virtue
Aetheric Magic and the Art Aether at 13 (Dies Irae pp. 38-39). The Virtue
and the Art aren't in the catalogs yet, so reaching it grants nothing on
the sheet. The 20-a-Technique minimum is the troupe's to check.

A goal that grants **a new Range, Duration or Target** names it like
"Range: Horizon (as Sight)". That's its kind, its name, and the standard
one it costs as. Add +n inside the brackets for more magnitudes. One the
app already knows, such as Duration: 19 Years, needs only its name. Once
the goal is reached, Invent Spell offers it to the magus (see
[Which Ranges, Durations and Targets](help:invent-spell-parameters)).

### Research Log
<!-- help: section-research-log -->

Every season spent on any goal, newest first: seeking a Discovery,
stabilizing one, or studying a source for an insight. Each row shows the
season, the goal, the work, the stress die, the roll (the die plus the
risk), any move of it, and what came of it. The app writes these when a
season is applied, so there's nothing to type. Choosing a row shows the
chart with the roll's band marked, the botch dice a 0 rolled, and the
points and Warping it gave.

## Inventory
<!-- help: tab-inventory -->

What the character carries and owns: raw vis (magi only), Personal Gear,
<!-- tui -->
Enchanted Devices and Books. The three lists below Raw Vis share one
details panel.
<!-- /tui -->
<!-- gui -->
Enchanted Devices and Books. Clicking a row shows it in the inspector.
<!-- /gui -->

**You type:** each item of gear, each enchanted device and its effects,
and each book.

**The app works out:** the combat totals of a chosen weapon, how a Lab
Text stands for this character, and the load that the Health section
turns into Encumbrance.

**See also:** [Hermetic Magic](help:tab-hermetic),
[Health](help:section-char-health)

### Raw Vis
<!-- help: section-raw-vis-inventory -->

The magus's raw vis, by Art. It's the same pool as Raw Vis on
[Hermetic Magic](help:section-raw-vis-hermetic), so a change in one shows
in both, and it's given away the same way.
<!-- tui -->
[Give](help:give) is in More (`m`).
<!-- /tui -->
<!-- gui -->
**Give** is beside Add, Edit and Delete.
<!-- /gui -->

### Personal Gear
<!-- help: section-inventory -->

<!-- tui -->
The character's Weapons, Armor and Other Items, in one list. `a` asks
which kind first.
<!-- /tui -->
<!-- gui -->
The character's Weapons, Armor and Other Items, each kind in its own
table. **Add** asks which kind first.
<!-- /gui -->
Choosing a weapon shows its Initiative, Attack, Defence and Damage totals
and the character's Soak, worked out from the weapon and the character (DE
Chapter 11: Obstacles). A weapon typed in by hand rather than chosen from
the catalog counts no Combat Ability.

**Shields.** A one-handed weapon is fought with the best shield the
character carries, and the two add together (DE p. 393). The totals name
the shield. Every weapon takes one but a Great Weapon (two-handed) and a
bow, which needs both hands. That's the app's reading, since the book
doesn't list them. The weapon's and the shield's minimum Strength are
checked separately (DE p. 400). **Defence against missiles** counts the
Combat Ability and the carried shield only, not the weapon (DE p. 395).

**Flags and limits.** On foot a lance's totals are a Long Spear's, with
Great Weapon (DE pp. 400-401). A weapon or shield whose minimum Strength
is above the character's is flagged (DE p. 400). A weapon whose Combat
Ability the character lacks is used untrained, with three more botch
dice. A crossbow's Damage adds no Strength (Lords of Men p. 138).

**Greek Fire Siphon.** With The Sundered Eagle in play, the catalog also
has this hand-held missile weapon. It's fought with Profession: Naffatun
instead of a Martial Ability, and the character needs that Ability by
that name. A shield doesn't defend against its fire. In a fight, its
Defence adds to the target's Soak instead. One dose of Greek Fire is good
for 10 sprays, which the app doesn't count (The Sundered Eagle p. 47).

**Breaking.** When a botch or an odd use may break the weapon, the totals
give its stress check. It's a stress die + its Combat Ability and how well
it's made (-1 Shoddy, +1 Superior, +3 Excellent), against 15 (City &
Guild p. 77). The optional Clash of Weapons, when an Attack Total exactly
equals a Defence Total, is a lower check. It's a stress die + the Combat
Ability against 9, or 15 for an improvised weapon (Lords of Men p. 138).

The totals also give the weapon's damage types (crushing, piercing,
slashing) and damage levels, from Lords of Men's tables (pp. 137-138):

- 2 for most weapons
- 1 for the bludgeon, club, spear, lance, round shield, whip, farm
  implement, long spear and sling
- one fewer for Shoddy, and one or two more for Superior or Excellent, as
  City & Guild's base levels move.

Each failure costs a level, and a botch one more per botch. With none
left, it's broken. A standard item is mended in a season. A Superior or
Excellent one is mended by a craftsman with Craft twice its bonus, for a
Labor Point a level (City & Guild pp. 77-79).

**Lords of Men's weapons.** With Lords of Men in play, the Weapon list adds
(Lords of Men pp. 137-139):

- the falchion, net, infantry shield, trident, whip and halberd
- the bastard sword, one-handed and two-handed. Its Load is 2 (Errata p.
  76).
- the sharpened rock, and composite and horse bows
- the crossbow, the arbalest and the heavy arbalest.

Rows the book reprints from Ancient Magic or Guardians of the Forests come
with either book. Crossbows use the Crossbow Ability, and Strength doesn't
add to their Damage (p. 138). Where Lords of Men's tables differ from the
Definitive Edition's, the Definitive Edition's figures are used. That's
the throwing axe, the short bow's Load and the warhammer's cost.

**Armour pieces (Lords of Men).** With Lords of Men in play, the armour
form's Material also lists the book's pieces (Lords of Men p. 140):

- body armour: a cuirass or jerkin, haubergeon, hauberk or full armour of
  eight materials
- a surcoat: gambeson, coat of plates
- greaves or jambes
- helmets.

The coat of plates uses the Surcoats table's +2 and Load 2 (p. 140). The
book's Glossary (p. 141) says to use a metal scale cuirass's figures
instead (+3, Load 3). The book conflicts, and the app follows the table.

"Worn as" says where a piece goes. A character wears one piece of each
place, the best one. Their Protection and Load are added together, with
fractions kept to the end and then rounded up. So a mail cuirass (+3, Load
1.5) and a coif (+0.5) give Soak +4 and Load 2. Full body armour already
includes greaves. If the character also has a whole suit, the Definitive
Edition's partial or full armour, whichever protects better is worn. A
Superior or Excellent piece adds its bonus. A helmet's counts only against
blows to the head (Lords of Men p. 136). A helmet's Perception penalty is
shown in its book line.

**Made**, on a weapon or armour (City & Guild pp. 67-69, as Lords of Men
p. 136 sums them up):

- A Shoddy item is destroyed the first time it fails a stress check.
- A Superior weapon has +1 Attack, a Superior shield +1 Defence and
  Superior armour +1 Protection.
- An Excellent item has its **Excellent bonus**, +2 or more. On a weapon
  it goes to Attack and Defence both.

**Carried.** A weapon not **Carried** is kept elsewhere. Its Load doesn't
count, and a shield left behind isn't fought with. Only the armour worn
counts toward Load. An Other Item can name an Ability it **Helps** and how
much. Minor help takes 1 off the Ease Factor and major help 3, one item a
roll (Grogs p. 47).

**Specialties, Virtues and Flaws.** A specialty in the Combat Ability that
names the weapon adds 1 to Attack and Defence. It may name it as "pole
axe" for a Pole Axe, by the weapon's own name or by its catalog name.
Virtues and Flaws count too, and a **Counted** line names each:

- Lame: -1 to Initiative, Attack and Defence, -3 Dodging
- Missing Eye: -1 to a melee Attack, -3 with a missile
- Hobbled: -6
- Poor Eyesight: -3 Attack and Defence
- Slow Reflexes: -3 Initiative
- Primitive Equipment: -1 Attack and Defence with a weapon that isn't
  Inexpensive, and -1 Initiative and Protection in such armour.

A natural weapon's Qualities and Inferiorities (Improved or Reduced
Attack, Defense, Damage, Initiative) count for the weapon named when
they're taken. Improved Damage takes the bonus nominated for the fight.

**Mounted.** A character with Ride also gets a **Mounted** line. On a
trained warhorse, Ride (at most +3) adds to Attack and Defence with a
melee weapon, and to Defence alone with a missile weapon. That's DE p.
397, which Lords of Men pp. 126-127 expands: the Attack bonus is for melee
only.

- Shooting from a moving horse costs -1 at a walk or trot, -3 at a canter
  and -6 at a gallop. An untrained mount gives no bonus at all. These are
  the storyguide's to apply.
- A charge with a melee weapon adds the Combat Ability to the Attack
  again, at the cost of a Fatigue level the horse spends.
- A lance says that it breaks on a charge that hits.

The title also shows the character's silver, in pounds, when they have
any. Type it in the character's details (Silver).
<!-- tui -->
[Give](help:give) in More hands the chosen gear to another character or
the covenant, and **Give Silver** gives pounds from the purse.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, hands the gear last clicked to
another character or the covenant ([Give](help:give)). **Give Silver**
gives pounds from the purse.
<!-- /gui -->

### Enchanted Devices
<!-- help: section-char-devices -->

The enchanted devices the character holds, each followed by its effects.
<!-- tui -->
The magus's Talisman is one of them. More (`m`) offers Instill an Effect
on a device that can take another effect, Use a Charge on a Charged Item,
and Use an Effect on a finished effect of an invested device or lesser
enchantment.
<!-- /tui -->
<!-- gui -->
The magus's Talisman is one of them. Beside Add, Edit and Delete, the
**Instill** button instills an effect in the chosen device when it can
take another. **Use Charge** uses a charge of a Charged Item, and **Use**
uses a finished effect once.
<!-- /gui -->
The device form's **Holder** may be "(none - unassigned)". The device then
leaves this list and waits, held by nobody, in
[the Custodia Mirabilium](help:custodia).

Using an effect shows its Initiative (Quickness + stress die, +3 with a
Fast Trigger), its Penetration and how many of its uses a day are spent
(DE pp. 257, 259). Penetration is 0 unless the effect was enchanted with
more. In a fight, Next Blow's **Use a device** plays it.

A device the character has by a Virtue says so in its **Had by a Virtue**
(DE pp. 97-98, 105):

- Minor Enchantments: 25 levels a Virtue, no power over level 30
- a magus's Masterpiece: one lesser enchantment, made within their Lab
  Totals, its vis their parens's
- a Redcap's devices: 50 levels at Gauntlet, uses a day included.

The Powers section and the creation review say in red when they go past
these.

### Books
<!-- help: section-books -->

The books the character owns. Choosing a Lab Text shows how it stands for
this character, such as whether they can read it.

## Agents
<!-- help: tab-agents -->

The people the character controls through personal bonds, Lords of Men's
agents (Chapter Two: Politics, pp. 22-25). Every character has it, after
Inventory.

**You type:** each agent or would-be agent: their Social Status, what
makes them harder to win, what they bring you, whether they're impressed,
and their Bond once they're yours.

**The app works out:** how many agents you can keep, each one's resistance
from the Agent Recruitment Table, the Agency experience it takes to win
them, and the rolls to impress them and to set them a task.

**See also:** [Inventory](help:tab-inventory),
[Planning](help:tab-planning)

### The agents
<!-- help: section-char-agents -->

**The limit.** A character can keep 2 x (Presence + the higher of Intrigue
or Leadership - the Gift's social penalty) agents, at least 1 (p. 22).
Only recruited agents count against it, their resistance worn to nothing.
The people still being won show as a separate number beside it. The count
turns red past the limit. Beside it is the **Agency experience** not yet
spent, its own pool apart from any Ability's.

**Who isn't an agent** (p. 22). Leave these off the list:

- Hermetic magi
- people with no political role
- an agent's own people
- hirelings, who serve for pay and change sides when the odds are poor
- other players' characters.

**The list** shows each one's name, their Social Status Virtue or Flaw,
their Bond, their resistance and their resources. The Bond is the
Personality Trait that ties them to you, with its score. The resistance is
a number, "impressed" once the first roll is made, and "agent" once
they're yours.
<!-- tui -->
The details panel shows the chosen one in full.
<!-- /tui -->
<!-- gui -->
Clicking a row shows the chosen one in full in the inspector.
<!-- /gui -->
It lists the Agent Recruitment Table lines that set their starting
resistance (p. 23):

- their Social Status: a Major Social Virtue 3, a Minor 1, a Free one 0, a
  Minor Social Flaw -1, a Major -3
- less 3 or 1 for a Flaw that would trouble you, and 6 for one you use to
  dominate them
- plus each resource they'll use in your service, 6 more for over three
  resources and 9 for over six.

It's never below 1. Then it shows what winning them needs. For an agent,
it shows their Bond, their persuasion total and the **Tasks for Agents**
table (p. 24), with the Ease Factor of each task and the die they need.

**Coerced.** An agent who thinks you their social inferior is held only by
coercion. You have Difficult Underlings for them, and they have a Story
Flaw such as Blackmail or Dark Secret (pp. 22-23). One you dominate
through a Flaw hates you, with the same Difficult Underlings (p. 23). The
form and the panel say so.

**Winning them.** First you **impress** them: a stress die + Presence +
Leadership - the Gift's penalty, against 6 (p. 24). A failure waits for
another story. Then each point of resistance falls for as many Agency
experience points as it now stands at. So a resistance of 3 takes 3 + 2 +
1 = 6 (p. 24). At 0 they're your agent, with a Bond of 0.

**Agency experience** comes from adventuring. When an **Adventure** season
is applied, the character gains as much Agency experience as the season's
Adventure experience (pp. 24-25). Exposure, Practice and teaching bring
none.

**Their Bond** rises as an Ability does (5 x the new score), from Agency
experience or from money at 5 points a pound. Money fails for an agent
already prosperous, or one who thinks taking money for service a crime or
sin (p. 25). Paying comes out of the silver the character carries.

**Setting a task** needs an agent with a Bond of +1 or more. Roll a stress
die + Communication + Charm, Intrigue or Leadership as suits the request,
+ Bond - the Gift's penalty. The Ease Factor is:

- 3, 6 or 9 for the task
- +1 for within a few days, or +3 for within a day
- +1, +3 or +6 for the risk to the agent, with 1, 3 or 5 botch dice. With
  no risk, it's a simple die.

Gathering news they hear anyway needs no roll (p. 24).

**Resolving the task.** Once the agent takes it on, they make their own
roll (see [Resolve the Task](help:agent-task-resolve)).

<!-- tui -->
`a` adds an agent, `e` edits the chosen one and `d` deletes them. More
(`m`) offers:

- **Impress**, only for one not yet impressed
- **Spend Agency Experience**, for an impressed one while there's
  experience to spend, or an agent's Bond
- **Set a Task**, only for an agent with a Bond of +1
- **Resolve the Task**, for any agent.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the agents. These act on the
chosen one, and are greyed out where they can't:

- **Impress**, only for one not yet impressed
- **Spend Agency Experience**, for an impressed one while there's
  experience to spend, or an agent's Bond
- **Set a Task**, only for an agent with a Bond of +1
- **Resolve the Task**, for any agent.
<!-- /gui -->
The agent form's **The Agent** shows the resistance your choices give
them. Set a Task's **The Task** shows the Ease Factor, the persuasion
total and the botch dice before you roll.

## Resolve the Task
<!-- help: agent-task-resolve -->

The agent's own roll, once they've agreed to a task (Lords of Men, Using
Agents, p. 24). It's a die + their Characteristic + Ability, against the
task's Ease Factor. **Roll** rolls it once and says how it went. It writes
it in the character's Diary under the agent's name and the task.

- **With** and **Characteristic + Ability**: the scores the agent uses,
  added by hand. An agent's resources are free text, so the app can't look
  them up. Their resources are shown above.
- **Task**: the band the persuasion was for, which sets the **Ease
  Factor** to its highest (Easy 6, Hard 12, Impressive 18). Lower it for
  an easier deed within the band. One above the band is warned of, since
  the agent's agreement didn't cover it.
- **Risk to him**: none rolls a simple die. Embarrassment or reputation is
  a stress die with 1 botch die, injury or imprisonment 3, death 5.

**His Roll** shows the total, the Ease Factor and the die the agent needs
before you roll.

## Religion
<!-- help: tab-religion -->

A character's faith, what it lets them do, and their career in the Church.
It comes after Virtues & Flaws. It's there for a person (not an animal)
while a book that gives the faiths their rites is in play. It's also there
for anyone with a grade, an ordination, a petition or a canon case on
record. The books are:

- Realms of Power: The Divine
- The Church
- The Sundered Eagle
- The Contested Isle
- The Cradle and the Crescent.

Its icon is the character's faith's: a church for a Christian, a crescent
and star for a Muslim, a Star of David for a Jew, a fire altar for a
Mazdean, a tree for a pagan.

**Faith** comes first, with their religion and what it gives them. For a
Christian with The Church in play, the Church's sections follow (The
Church pp. 33-38, 46-48):

- **Holy Orders** and **Ordinations**, for one who may hold orders. That's
  a clerical Social Status (Clerk, Priest, Religious, Senior Clergy or
  Mendicant Friar), or a grade or ordination on record.
- **Petitions** and the **Canon Court**, for any Christian.

A layman begins in orders with an Ordination season on Planning, or by
taking a clerical Social Status on Virtues & Flaws.

**You type:** their religion, their birth diocese, standing and benefice,
each petition and each case.

**The app works out:** what their faith offers them and whether they may
take it, each examination's total and result, what an ordination brings,
what still stands between them and the priesthood, and each petition's
total, who may grant it and whether it's granted.

A character with no use for it can leave it off (see
[Interests](help:interests)).

**See also:** [Which faith actions a character can take](help:guide-religion),
[Virtues & Flaws](help:tab-vf), [Planning](help:tab-planning)

### Faith
<!-- help: section-char-faith -->

Their religion, where blank counts as Christian, as most of Mythic Europe
is. For a Christian, also their patron saint, their Devotions, their
mystic path and the saints who have refused their invocations. Then their
Pious trait, and a line on what their faith gives them.

<!-- tui -->
`e` edits their religion. `m` (More) offers what their faith lets them do:
<!-- /tui -->
<!-- gui -->
Edit Religion sits beside the title, with what their faith lets them do:
<!-- /gui -->

- **A Christian:**
  - [Invoke a Saint](help:devotion), and Threaten a Saint once a saint has
    refused them
  - Patron Saint
  - Devotion Points, with a Devotion or Pious enough to begin one
  - Indulgence, Vigil or Fast, with The Church
  - [Mystic Path](help:mystic-path), for one Pious and tied to the
    Divine, and its Spiritual Path or Monistic Revelation
  - [Invoke God's Aid](help:gods-aid) and
    [Holy Influence](help:holy-influence).
- **A Muslim:** [Invoke Baraka](help:baraka) and [The Hajj](help:hajj),
  Invoke God's Aid, and Holy Influence for one with spiritual authority.
- **A Jew:** Invoke God's Aid, and Holy Influence for one with spiritual
  authority, such as a rabbi over their community.
- **A Mazdean:** invoking a yazata, as a Christian invokes a saint. That's
  Invoke a Saint, with The Cradle and the Crescent.
- **A pagan:** the books give pagans no rite like the saints'. Their faith
  is in a magic spirit (a Spirit Votary, DE p. 58) or in faerie (Realms of
  Power: Faerie p. 134).

<!-- tui -->
A pagan's dealings with them are in More on their record: Ars Fabulosa, A
Faerie Bargain and An Offer to Faerie.
<!-- /tui -->
<!-- gui -->
A pagan's dealings with them are in the Deeds chapter under Dealings with
Faerie: Ars Fabulosa, A Faerie Bargain and An Offer to Faerie.
<!-- /gui -->

## Invoke Baraka
<!-- help: baraka -->

A Muslim seeks a holy forbear's blessing, the forbear's baraka, as a
Christian invokes a saint (Realms of Power: The Divine pp. 103-105). The
roll is as for [a saint](help:devotion), with the modifiers below, and
the storyguide's die is rolled in secret. The petitioner must be at
the forbear's shrine, usually their tomb (tick **At his shrine**). The
Qur'an itself may be invoked anywhere. A forbear is never threatened.

**The forbears** are the book's, each with where their baraka is sought
and their powers:

- the Qur'an, Might 100
- Muhammad, 100
- Abraham, David and al-Husayn, 75. The book lists no powers for David.
- Rabi'a al-'Adawiyya, 50
- al-Shafi'i and Nur al-Din, 25.

**The modifiers** (p. 103):

- the petitioner's highest Muslim Personality Trait, + its value. The book
  doesn't say which traits are Muslim ones, so you choose, and Pious is
  offered first.
- a Divine aura, +1 a level. The ritual prayer, a Muslim holiday and
  Ramadan each raise a Muslim Dominion aura by 1 (pp. 107-108).
- the forbear's feast day, normally their birthday, +3
- a pilgrimage made to their tomb or shrine +2
- touching their relic +1, owning it +2
- a donation +1 to +3
- imminent peril +2
- a recent sinful act -1 to -3
- no zakat paid within a year -3
- a miracle received within a month -5
- an unfamiliar forbear -10
- choosing a specific miracle of theirs, rather than general aid, -5.

**The Baraka** shows the total, the chance and the forbear's powers.
**Pray** rolls it, and the Diary records it.

## The Hajj
<!-- help: hajj -->

The pilgrimage to Mecca every Muslim who is able makes once, in the first
half of Dhu'l-Hijja (Realms of Power: The Divine p. 108). **Complete the
Hajj** gives Pious +3 and 3 Faith Points. Made again, it restores both,
but never raises Pious above +3. A Pious already higher stays as it is.
The Diary records it, with any notes. Play out the journey itself as a
story, or plan its seasons as travel.

## Edit Religion
<!-- help: religion -->

The character's religion, from the list: Christian, Muslim, Jewish,
Mazdean, Pagan or Other. Left blank, they count as Christian. It decides
what [Religion](help:tab-religion) offers them. Biographical Detail edits
the same field.

### Holy Orders
<!-- help: section-char-orders -->

The character's grade, Social Status, birth diocese and standing, and
which law they're under. The minor orders are doorkeeper, lector, exorcist
and acolyte. The major orders are sub-deacon, deacon, priest and bishop.
It also shows the Faith Points their ordinations brought, one each, even
for several grades at once (p. 34). A cleric of any grade is under canon
law, not secular law (pp. 34-35).

**The ladder** shows the grades held, the next one, and its examination.
That's Intelligence + Church Lore or Civil and Canon Law + a stress die,
against the grade's Ease Factor:

- Doorkeeper 3 and Lector 6, in Church Lore
- Exorcist 3 and Acolyte 6, in Civil and Canon Law
- Sub-deacon 9, Church Lore
- Deacon 9, Civil and Canon Law
- Priest 12, Church Lore
- a bishop is elected (p. 33).

Church Lore is the sheet's Organization Lore: Church.

**Toward Priest** (p. 35). A priest must be 25, freeborn, legitimate,
sound of body and mind and educated for their office. They need a
benefice, chaplaincy or curacy free. Each one the character fails is
flagged, and needs a dispensation, a petition at Ease Factor 9:

- "sound of body", by a Dwarf, Lame, Blind or similar Flaw
- legitimacy, by Bastard
- freeborn, by Slave.

The app warns, but never stops the ordination.

**Standing:**

- In good standing.
- Irregular: a cleric who has shed blood or committed a grossly immoral
  crime. They can't use Faith Points until they confess. No trial is
  needed (p. 37).
- Excommunicated: shown while a guilty verdict of excommunication stands
  against them in the Canon Court.

<!-- tui -->
`e` edits Holy Orders. `m` (More) performs an exorcism, for a clergyman.
<!-- /tui -->
<!-- gui -->
Edit Holy Orders sits beside the title, and Perform an Exorcism for a
clergyman.
<!-- /gui -->
A clergyman is one in orders, or a Clerk, Priest, Senior Clergy or
Mendicant Friar. A monk or nun who is Religious only isn't (p. 34).

### Ordinations
<!-- help: section-char-ordinations -->

One entry per examination: the grade, the season, the total against the
Ease Factor, and the result (p. 34).

- More than double the Ease Factor: ordained, with a Reputation of 1 for
  knowing the Ability, or a Reputation experience point toward it.
- Equal to it, or above it by no more than double: ordained.
- Missing it by 6 or less: they still pass, with a Reputation of 1 for
  ignorance, or a point toward it. Missing by exactly 6 is a judgement
  call. The book covers "less than 6" and "more than 6", and the app lets
  it pass.
- Missing it by 7 or more: not ordained. They may appeal, with a petition
  at Ease Factor 9, or sit it again another season.
- A botch: not ordained. They may sit it again only once a petition lets
  them, and Holy Orders shows them barred.

Being ordained brings the grade's Social Status (pp. 25-26, 34), which
replaces the character's own. A character holds two Social Statuses only
where both say they're compatible, and the clergy's don't (DE p. 63). So
they never keep both.

- The first grade gives Clerk in place of any lay status, such as
  Covenfolk or Craftsman (DE p. 74).
- Priest replaces Clerk, Religious for a monk, a Mendicant Friar's or a
  lay status (DE pp. 104, 106; The Church p. 26).
- A bishop's Senior Clergy is a Major Virtue (DE p. 107), so the app says
  to swap it on Virtues & Flaws rather than doing it.
- Wealthy and Poor aren't Social Statuses and are never touched.

The Ordination season offers the swap with **Swap his Social Status for
the clergy's**, ticked by default. Untick it to leave their status for the
troupe to change on Virtues & Flaws. A major order means celibacy from
then on (p. 35).

An Ordination season (Plan a Season) examines the character for the next
grade. Add records an ordination from before play, which doesn't change
their grade. Edit Holy Orders does that.

### Petitions
<!-- help: section-char-petitions -->

A petition to the Church: what was asked, by letter or in an audience, the
season, its Petition Total against the Ease Factor, and the result. No die
is rolled (p. 48).

### Canon Court
<!-- help: section-char-canon -->

Cases in the Church's courts, with the character accused or accusing. Each
shows the charge, the court, the verdict and the punishment. The kinds of
case are on pp. 37-38. The court may be:

- the archdeacon's, at their visitation
- a rural dean's or parish priest's
- the bishop's, on appeal
- the papal curia.

The judge decides, with no jury and no roll. About a dozen oath-helpers
swearing to the accused's good character acquit them, which is
compurgation. Canon courts shed no blood, and no one need attend one more
than two days' travel from their diocese (pp. 35-37). A clergyman a
secular court finds guilty is tried again in the bishop's court (p. 35).

## Petition the Church
<!-- help: petition-church -->

Anyone may petition the Church, whether clergy, peasants, nobles or magi
(The Church pp. 46-48). Add, on Petitions under Religion, makes one.
Choose the book's example it's most like, or type the Ease Factor (p. 47):

- 3, a marriage blessing
- 6, a parish crypt or library
- 9, the cathedral library, an appeal of an ordination exam, or a
  dispensation
- 12, renting land to a Hermetic covenant
- 15, excommunicating a nobleman
- 18, a monastery
- 21, a new diocese
- 24, changing canon law
- 30, declaring a saint
- 42, a crusade.

**Petition Total** (p. 46). A letter is Communication + Church Lore. A
scribe's Communication + Church Lore may stand in (type their name and
total), and The Gift doesn't apply. An audience is Presence + Church Lore,
and The Gift's penalty applies. Then add:

- many testify +1, magical evidence +1, a holy vision +3, miracles +6
- the highest clergy support, once: +1 a priest or deacon, +3 a senior
  clergyman, +6 an archbishop or higher
- the highest lay support, once: +1 a knight, +3 a nobleman, +6 a king,
  duke, earl or emperor
- a donation +1 to +3
- each argument, by Civil and Canon Law, Artes Liberales (Logic) or
  Intrigue, +1 to +3. It counts only if Intelligence + the Ability + a
  stress die reaches 9, rolled when the petition is made. A botch makes
  its bonus a penalty.
- the petitioner's Reputation with the Church
- spells cast on those deciding.

**Who decides** (p. 48). A priest may grant up to 6, a bishop up to 15,
and the papal curia the rest. One petition a season is usual. It takes no
season unless the petitioner travels.

**An appeal** against another's granted petition overturns it at that
petition's total + 3. Above its total - 3, it wins a compromise. It's -3
if it isn't made in the same season (p. 48).

Untick **Made now** to keep a petition planned, with no total yet.

## Add Canon Case
<!-- help: canon-case -->

The storyguide's record of a case:

- the charge, whom it's about, and whether the character is accused or
  accuses
- the court and the season
- whether oath-helpers swore for the accused. Compurgation acquits, and
  the form asks when it's set beside a Guilty verdict.
- the verdict and the punishment (The Church p. 37).

The punishments are a monition (an official warning), public penance, a
fine when penance isn't done, imprisonment in a monastery, the benefice
suspended, or excommunication. Excommunication means no sacrament but
penance and no consecrated burial, and a clergyman loses their shield from
secular justice. It's lifted by confession and penance, and shows on Holy
Orders as their standing.

## Perform an Exorcism
<!-- help: perform-exorcism -->

Any clergyman may exorcise (The Church p. 34). They spend at least one
Confidence or Faith Point, +3 each. The Exorcism Total is a stress die +
the Points, plus:

- +1 if they've been ordained exorcist. Every grade from exorcist up has
  been.
- +1 for holy water, and +1 for a crucifix.

Exorcism is a Divine power. A Divine aura adds its strength, and other
realms' auras don't hinder it (DE p. 411). It must reach the Might the
demon invested in the energumen, and Penetrate their Magic Resistance if
they have any. **Roll** rolls it. Mark the Points spent on the sheet. An
Irregular cleric can't use Faith Points (p. 37), and the calculator warns.

## Edit Holy Orders
<!-- help: edit-holy-orders -->

- The character's grade, for one held before play. An Ordination season
  examines them for the next.
- Their birth diocese, where they're ordained. Elsewhere needs its
  bishop's leave (p. 33).
- Their standing, and their benefice or office.
- Whether a botched examination bars them until a petition succeeds.

## Deeds
<!-- help: tab-deeds; gui -->

What the character can do in play that the saga's books bring, gathered in
one chapter instead of as buttons on the sections they touch. Each action
sits under the interest it belongs to, beside a line saying what it does:

- **Session & Reputation**: End of Session, Reputation Roll, House
  Acclaim.
- **Knightly**: Melee Event.
- **Scholarly**: Disputatio, Make a Ligature.
- **Insight**: Font of Knowledge, Divination, Astrology.
- **Mystery Cults**: Experiment on a Script, for a Mystagogue.
- **Tribunal & Order**: Hermetic Letter, Invoke a Broken Oath.
- **Dealings with Faerie**: Ars Fabulosa, A Faerie Bargain, An Offer to
  Faerie.
- **The Infernal**: Confidence through Sin, Infernal Influence, Ars
  Goetia.
- **Apprenticeship**: Turbulence, The Gauntlet, Lose the Gift.
- **Covenfolk**: Reward or Punish, Pension.

An action shows only while its book is in play and it fits the character.
Disputatio needs someone to dispute with, and The Gauntlet an apprentice.
A header with nothing to offer is left out.

What takes a season, such as a career or Greek Fire, is in the Planning
chapter's A Season's Work instead. The faith's actions are in the
Religion chapter. While the character is In Creation, the chapter only
says its deeds wait until the character is In Play. A character kept as a
statblock has no Deeds chapter.

A whole interest can be left off the sheet for a character who will never
take it up. Untick it in [Interests](help:interests) on the Manage
chapter.

**See also:** [Planning](help:tab-planning),
[Interests](help:interests), [How to find an action](help:guide-find-action)

## Interests
<!-- help: interests -->

<!-- tui -->
More (`m`) on a person's record offers **Interests**: a tick for each kind
of deed the saga's books bring, with a line on what it is.
<!-- /tui -->
<!-- gui -->
**Interests**, in a person's Manage chapter, opens a window of cards, one
for each kind of deed.
<!-- /gui -->
The kinds are Knightly, Scholarly, Insight, Religion, Agents, Research,
Hermetic Mysteries, Mystery Cults, Craft & Trade, Tribunal & Order,
Dealings with Faerie, The Infernal, Apprenticeship and Covenfolk.
<!-- gui -->
A card says what the interest is and how many actions it adds in this
saga, counting those whose book is in play. So one may read "2 actions, 4
more with other books". Click a card to see it in the Inspector. It shows
who the interest is for, and each action with a line on what it does. It
also says whether that action is on the Deeds chapter or on Planning in A
Season's Work, and which book the others wait for.

Each card's switch, and the Inspector's, turns the interest off or on, and
a card turned off fades. Save keeps your choices. Leaving with changes
unsaved, by Cancel, the close button or Esc, asks first. Discard Changes
leaves things as they were, and Keep Editing goes back to the window.

A card whose books aren't in play is faded and its switch is locked. The
character's choice is kept, so the interest comes back as you left it when
a book arrives.
<!-- /gui -->

Turn off the ones the character won't take up, such as a magus's Knightly
or a blacksmith's Scholarly, and their actions leave the sheet.
<!-- tui -->
More no longer offers them.
<!-- /tui -->
<!-- gui -->
They leave the Deeds chapter's heading, A Season's Work and More alike.
<!-- /gui -->
Session & Reputation (End of Session and the Reputation rolls) is every
character's and is always on.

Turning off **Religion** takes [Religion](help:tab-religion) off the
sheet, with Pilgrimage on Planning, for a character whose faith will never
come up. Their religion stays on their Biography. Its count goes by the
character's faith as well as the books, as in "15 actions for a
Christian", and the Inspector lists those of other faiths. A Church career
keeps it on: orders, a clerical Social Status, a petition or a canon case.
The switch then gives way to "On for a Church career". If a character
with Religion off takes up a career, Religion comes back.

**Agents** and **Research** work the same way, each hiding its own part of
the sheet. An agent on record, or research under way, keeps it on.
Research and Hermetic Mysteries are for magi, so other characters don't
see them.

<!-- tui -->
**A covenant has Interests too**, in More on its record.
<!-- /tui -->
<!-- gui -->
**A covenant has Interests too**, on its own Manage chapter.
<!-- /gui -->
Its Creation Worksheet has a Review Interests step for them. **Manors**
hides the covenant's Manors and **Ships** the Ships list on Possessions,
for a covenant that will never take them up. A manor or a ship on record
keeps them on. Hermetic Projects need no card, since they wait until a
project begins.

Everything starts ticked, so nothing goes missing until you say so. A new
character's Creation Worksheet has a Review Interests step for it. Ticking
an interest doesn't offer what the rules don't. An Artist's Career still
needs a Craft or Profession, and every action still needs its book in
play.

## Planning
<!-- help: tab-planning -->

What the character does this season and the three after it, a full year,
and what each will give them before the season is applied.

**You type:** the season's activity and its details. Lab work is planned
on the laboratory's Planning instead.

**The app works out:** the XP and other gains the plan will give, with any
problem with the plan shown in red (DE Chapter 10: Long-Term Events). This
season is worked out from the character as they stand now. A season ahead
is worked out from the character as the seasons planned before it will
leave them (see [Seasons Ahead](help:section-char-ahead)).

A grog isn't planned season by season. Planning sets up the grog's yearly
update instead, applied in Winter.

**See also:** [Planning a season](help:plan-season),
[Advancing a season](help:advance-season),
[A grog's year](help:grog-year), [Diary](help:tab-diary),
[How to plan and run a season](help:guide-seasons)

### A Season's Work
<!-- help: section-char-season-work; gui -->

Below This Season on the Planning chapter: the season-long work the saga's
books bring, each button beside a line saying what it does. These show
while their book is in play and they fit the character:

- a season on the tourney circuit
- Labor Points from a story, investing time or money, selling finished
  goods
- an apothecary's store, Greek Fire
- an artist's or a scholar's career
- Turbulence, a grog's story experience, a pilgrimage
- Philosophic Alchemy.

This Season's own buttons keep to planning the season: Plan, Edit, Clear
and copying. The terminal offers the same in More on This Season.

**See also:** [Deeds](help:tab-deeds), [Planning](help:tab-planning)

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
Some results, such as a die roll, are only settled when the season is
applied. Below the plan it lists what the character carries from season
to season:

- Labor Points, and what the Improve wealth or status season costs to move
  up a step: 120 from Poor, 360 from average, 1,080 from Wealthy (City &
  Guild p. 38)
- works in progress and formulas
- the past Ordeals still lowering an Initiation's Target (see
  [How to initiate a character into a Mystery](help:guide-initiation)).

<!-- tui -->
For a grog, `e` sets up the yearly update (Grogs, Chapter 5).
<!-- /tui -->
<!-- gui -->
For a grog, **Yearly Update** sets up the yearly update (Grogs, Chapter
5).
<!-- /gui -->

Below the Labor Points line it says what they're worth in money to the
business. 9 Labor Points are about a quarter of a year's income (City &
Guild p. 40, as the Errata p. 56 corrects it). Rounded to the nearest
pound, they're worth:

- about 2½ pounds to a Trivial income (10 pounds a year)
- about 10 to a Lesser one (40)
- about 63 to a Greater one (250).

The income source is the band the Social Status Virtue buys (p. 37):

- Trivial: Laborer, Journeyman and Craftsman
- Minor: Merchant, Guild Master and an expensive Craftsman
- Lesser: Senior Master
- Typical: Merchant Adventurer, Factor and Guild Dean
- Greater: Capo.

Where a Virtue buys either of two, the poorer is assumed until you choose
the other in either form below. A merchant's open investments are listed
too:

- a speculation, and what it pays a year
- an introduction, and when it pays back
- a brokered marriage's Social Contacts
- a charity, and the crowd it can call.

<!-- tui -->
More (`m`) here offers **Labor Points from a Story** and, for a trader or
anyone with Labor Points, **Invest Time or Money**.
<!-- /tui -->
<!-- gui -->
**Labor Points from a Story** and **Invest Time or Money** sit beside
Plan, Edit and Clear.
<!-- /gui -->

[Turbulence](help:turbulence) is offered here too, for an apprentice
assisting in a stressful laboratory season.

The seasons of The Mysteries Revised Edition's Hermetic Mysteries:

- **Invent Rotes (Hermetic Numerology)** (TMRE pp. 92-93). Choose the
  Rotes' Technique and Form, and type the Rotes as "Name: level". Add
  "(text)" after one invented from a Lab Text.
  - The Rote Lab Total is the laboratory's Lab Total plus Artes Liberales
    (at most Magic Theory) and the book bonus.
  - No Rote may be above a fifth of it, rounded up. Each costs twice its
    level, or its level from a Lab Text, all within the total.
  - The Rotes invented are kept as finished Rote records and shown with
    the Casting Scores.
- **Bind an enchanted structure (Hermetic Architecture)** (TMRE pp.
  97-99). Name the structure and type its highest component effect's
  level. Choose its Size multiplier: 5 a small room, 6 a Room, 7 a
  Structure, 8 a Boundary, 9 and 10 larger. Then give the days
  recomputing the components' places takes after a miss, from 1 for posts
  in a field to 30 for niches in a building. Blank means a month.
  - The season places the components, Intelligence + Artes Liberales
    against 6 + Size. Each failure costs those days, and the magus tries
    again while the season lasts. Its notes give the misses and the day
    the components were placed. A botch is a disaster.
  - Then the magus casts Bind the Mystical Structure, a Rego Vim Ritual of
    at least the effect's level + 5. It's a magnitude more for a Structure
    and two for a Boundary, paying a pawn of Vim a magnitude from the vis
    chosen.

A book is one reader's at a time. A plan to read or copy a book another
character has planned for the same season is refused, saying who holds it
and until when. Being taught by another Player's character becomes an ask
of that Player instead of a plan (see
[Teaching Requests](help:teaching-requests)). A character's **Steward**
plans their seasons here too.

**Study Path** (More) plans the way to a score (see
[Study Path](help:study-path)).

### Study Path
<!-- help: study-path -->

How a character reaches a score in an Art or Ability by a year, season by
season, with what's to hand.

**You type:** the Art or Ability, the score wanted, and the year to reach
it by. **Find** shows the path, and **Plan These Seasons** plans it.

**The app works out:** each season not yet planned, from now to the end of
that year, takes whichever source gives the most experience then:

- a book they may read, their covenant's or their own. A summa counts only
  to its Level and a tractatus once, never one another character holds
  that season.
- vis study for an Art, for a magus with the pawns to hand. Its Source
  Quality is counted at 6 plus the aura, a stress die's usual worth.
- practice for an Ability
- a teacher of their covenant with a higher score, only up to the
  teacher's own score.

It says whether the goal is reached, and otherwise with what score.
Seasons already planned stay as they are. A season with a teacher whose
Player isn't yours becomes an ask (see
[Teaching Requests](help:teaching-requests)). A storyguide, or the Player
of both, plans both seasons at once.

### Teaching Requests
<!-- help: teaching-requests -->

Asks for another Player's character to teach. A student's plan to be
taught by a character their Player doesn't play or steward becomes an
ask. The student's This Season says "Waiting for Bruno to teach Latin",
and storyguides see it on [Needs You](help:section-attention).
<!-- tui -->
The teacher's Player sees it in the teacher's **Teaching Requests**, in
More on This Season.
<!-- /tui -->
<!-- gui -->
The teacher's Player sees it on The Troupe, and in the teacher's
**Teaching Requests** on This Season.
<!-- /gui -->

**You type:** on the teacher, choose the ask, then **Accept** or
**Decline**. Accept plans both seasons, so the student is taught and the
teacher teaches. Decline takes a note the student sees. On the student,
choosing their own ask clears it.

### Seasons Ahead
<!-- help: section-char-ahead -->

The three seasons after this one, named in the title, each with what's
planned for it or "nothing planned". With This Season above it, a
character can be planned a full year ahead. When the season is advanced,
the next one becomes This Season and another joins the list.
<!-- tui -->
Highlight a season to see its plan and what it will give under the list.
`e` plans it or changes its plan, `a` plans the first season with nothing
planned, and `d` clears the highlighted season's plan after asking.
<!-- /tui -->
<!-- gui -->
Click a season to see its plan and what it will give under the list.
**Edit** plans it or changes its plan, **Plan** plans the first season
with nothing planned, and **Clear** clears the chosen season's plan after
asking.
<!-- /gui -->
What a season ahead will give is worked out from the character as the
seasons planned before it will leave them. The xp, books read, vis spent
and lab work of the earlier seasons all count, and the details say so
under the plan.

- A season whose die isn't rolled yet, such as study from vis or an
  experiment, counts as gaining nothing. The seasons after it say "Counts
  nothing gained from ...".
- The year's end (aging, a grog's year, the covenant's harvests) and the
  seasons nobody planned aren't counted.

Lab work in a season ahead is planned on the laboratory's Planning, as for
this season. A grog has no Seasons Ahead, since their yearly update covers
the year.

### Calendar
<!-- help: section-char-calendar; tui -->

The character's seasons as a calendar: a line per year, newest first, from
three years ago to the last season planned, with Spring, Summer, Autumn
and Winter across. A season already played shows its Diary entry's
activity. A planned one is in italics, with what it's expected to give on
the line under it, worked out as the Seasons Ahead are. That's the score
it leaves ("Ignem 7 (+15 xp)"), "8/15 points" or "die not rolled". The
current season is in bold. The calendar only shows. Plan or change a
season in This Season or Seasons Ahead above it.

## Diary
<!-- help: tab-diary -->

<!-- tui -->
A record of the character's seasons, in one list with a details panel.
<!-- /tui -->
<!-- gui -->
A record of the character's seasons. Seasons at the top is a calendar, a
row per year, of what the character did each season and plans to do. A
planned season has a dashed outline, and also says what it's expected to
give, worked out as for the [Seasons Ahead](help:section-char-ahead).
Clicking one shows it in the inspector. The Diary below lists the
entries.
<!-- /gui -->

**You type:** entries of your own, with a year, season, activity and
notes. You can also edit or delete any entry.

**The app works out:** an entry for each season applied, for aging and
Warping, and for vis moved, written as they happen.

**See also:** [Planning](help:tab-planning),
[Advancing a season](help:advance-season)

## Turbulence
<!-- help: turbulence -->

A Gifted child's untrained Gift lashing out (Apprentices pp. 22-24).
Choose why it's checked:

- **A botched stressful roll that includes magic.** How loosely "includes
  magic" is read is the troupe's call (p. 22).
- **A potential botch on magic**, for a character with Turbulence Prone
  (p. 12). It's checked whether or not they botched, and they can't
  control it.
- **Forced**: a Confidence Point spent to call one up at will (p. 24).
- **Midway through a stressful laboratory season**, offered while they're
  planned to Assist and not yet checked this season (p. 56). The parens
  experimenting, more than 10 pawns of vis, odd hours or a Lab Total
  barely enough make a season stressful.

**Incurring it.** The roll is Intelligence + stress die + the aura's
modifier for a Magic power, less half the level of an Aegis of the Hearth
they had no part in. It must beat both the storyguide's stress die and the
child's age. Only the storyguide's die there is no-botch (p. 22). The
player's die, and both dice of the control roll, are ordinary stress dice
that can botch. A botched die counts 0, and the inspector and the Diary
say which die botched. What else the botch brings is the troupe's call. A
child's Characteristics are used as the sheet has them, with the Aging
Chart's modifier already in them, since it counts once (p. 23).

**Controlling it.** Stamina + stress die against Warping Score + stress
die (Errata p. 83). Half the difference is the effect's magnitude, in any
Technique and Form. An Affinity or Puissant Art is a good choice. The book
gives no rounding for an odd difference, so the app rounds down.
Controlled, the player chooses the effect. Uncontrolled, the storyguide
does. It has no Penetration unless they have the Ability, and then it's
its score x (1 + a sympathetic multiplier). More Confidence may be spent
on either roll, +3 a point, at most their Confidence Score on one roll.

In the laboratory, an uncontrolled Turbulence halves their aid to the Lab
Total. For a storyguide character, tick the box to roll for losing the
Gift as well. On a 0, they roll a botch die for every 10 of the parens'
Lab Total, and any 0 loses it (p. 59). Then use Lose the Gift.

**Roll** rolls it and writes it in the Diary.

## The Gauntlet
<!-- help: gauntlet -->

The parens' test of their apprentice (Apprentices pp. 59-61), for a
character with the Apprentice Social Status. Choose how it's decided:

- **Played as a story**: the parens says whether the apprentice passed.
- **Passed without a story**, once they've served their 15 years.
- **Rolled**: Intelligence + an Ability fitting their House + stress die,
  against 9. A botch means something dire happened.

Failed, they spend another year as an apprentice. After three failures the
Quaesitores set their Gauntlet. An apprentice kept more than 20 years is a
low crime in many Tribunals. Convicted, the parens forgoes the Gauntlet
and pays a rook of vis (10 pawns) for each year past 15.

Passed, Hermetic Magus replaces Apprentice, and the character becomes a
magus. After the Oath they have Parma Magica's final key. Until then their
Parma Magica gives no Magic Resistance (DE p. 169). **Record** writes the
result in the Diary.

## Lose the Gift
<!-- help: lose-the-gift -->

Failing an apprentice (Apprentices pp. 58-59). It's always the player's
choice.

- **Lost for good**: The Gift, and a Gentle or Blatant Gift, is taken
  away. They cast no spells and work no magic, and their Supernatural
  Virtues and Abilities stop working. Failed Apprentice replaces
  Apprentice, and a magus's record becomes a companion's.
- **Suppressed**: they gain the Major Hermetic Flaw Suppressed Gift. Their
  existing Supernatural Virtues and Abilities still work, but they gain no
  new Supernatural or Hermetic Virtues while it lasts. How it returns is
  the troupe's story.

**Save** makes the change and writes the cause in the Diary.

## Learn a Cantation
<!-- help: learn-cantation -->

An optional rule (Apprentices p. 46), for a saga with the option Learning
cantations on. A spontaneous spell cast in play at least as many times as
its level may be bought as a formulaic spell with that adventure's
experience, one point a level.

Choose the spell and how often the magus cast it. It can be any formulaic
spell they don't know, since the book sets no level cap, only the times
cast. It's never a Ritual spell, whose effects spontaneous magic can never
replicate (DE p. 311). **Learn** adds it to their Known Spells. Give that
much less of the adventure's experience to their Abilities and Arts.

The rule is for adult magi as well as apprentices (p. 46), so it's offered
on any character's Known Spells.
