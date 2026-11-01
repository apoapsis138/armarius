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
Realms of Power: The Divine p. 43's leaders of other faiths are listed too:
a Greek patriarch 20, the head of another eastern church 25, a caliph or
Shi'i imam 25, a chief qadi or mufti 20, a senior qadi or mufti 10, an
invested sultan 10, the exilarch 25, a chief rabbi 20, a senior rabbi 10;
metropolitans are Archbishop, crowned kings of any faith King (crowned).
<!-- /gui -->
The app works out the Age from Year Born (in
Biographical Detail) and the saga's current year, and shows the current year
and season dimmed because they belong to the saga. Size includes any Virtue
that changes it (Ars Magica Definitive Edition, Chapter 3: Characters).

Only a character with the True Faith Virtue has a True Faith Score. A
character made with a Score of 2 or more is a Mythic Companion, and the form
warns only while the character is In Creation (Realms of Power: The Divine
p. 57). Faith can also be won in play, as the climax of a quest, a
pilgrimage or a test of faith (p. 58): raise the Score or the Faith Points
on Edit while the character is In Play, and the app writes "Faith won in
play" in the Diary, adding the True Faith Virtue if the character had none.
Miracles are not worked out.
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

For a magus of House Tremere, **Holds own voting sigil** records that he
has beaten his parens in certamen for his sigil. Until then the sheet says
who holds it: his parens, or, when the parens doesn't hold his own, the
first magus up the line of parentes who does; a parens of the saga's who
has died no longer holds it (DE p. 16).

For a Tremere whose parens still holds his sigil, **Has challenged for his
sigil** records that he has made his one challenge for it at a time of his
choosing. After that he may challenge only at the House's Decennials, every
ten years (1218, 1228...), and the sheet says when the next falls. Winning
the certamen gives him his own sigil (Houses of Hermes: True Lineages p. 123).

**School of certamen** records the style he was trained in, or joined by a
season's study with a member of the school (True Lineages p. 135). The
Casting Totals section then names it and what its followers can do.

For a magus with Mercurian Magic, **Has learned Road Magic** opens the Road
and Road Network Ranges and Targets for his spells: a season's teaching by
one who knows it, with no further Virtue; a starting magus whose parens has
Mercurian Magic may be assumed to have learned it (TMRE p. 116).

**Renounced (year)** and **Renounced by** record a magus cast out of the
Order by a Wizard's March; closing a Tribunal meeting that Marched him
sets them. The section then says he is renounced: any magus may slay
him, and by tradition what he has goes to whoever does (Ars Magica
Definitive Edition p. 18). His parens is expected to strike first, a
social expectation rather than a legal duty (DE p. 21), so nothing charges
an heir who fails to; Houses of Hermes: True Lineages p. 53 makes it the
heir's duty and lets the slayer settle for the heir's inheritance, a
convention the Tribunal's case shows. A Wizard's War
he is fighting, or about to, shows here too, with its months (see the
Tribunal's [Cases](help:section-trib-cases)).

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

With Art & Academe's medicine on, Edit Biographical Detail also asks for the
character's **complexion**, the blend of the four humours (A&A pp. 40-41):
sanguine (blood: hot and moist, waxing in spring), choleric (choler: hot and
dry, summer), melancholic (melancholy: cold and dry, autumn) or phlegmatic
(phlegm: cold and moist, winter). Most people show two, the principal one
first, and sometimes a touch of a third; the hot or cold quality never
features twice, so sanguine never mixes with choleric, nor melancholic with
phlegmatic. The sheet shows the blend, its qualities, the season it waxes
in, the traits it suggests and the foods that keep it in balance (those of
the opposite qualities, p. 41). Complexion changes no roll: it is the
troupe's guide to personality and to which diseases threaten.

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
On a character with a sinful trait, More (`m`) here offers
[Confidence through Sin](help:confidence-through-sin); on a sinner or one
who knows Infernal Lore, [Infernal Influence](help:infernal-influence); on
one of holy standing (clergy, a monk, True Faith, Temporal Influence,
Inspirational, or Dominion Lore), [Holy Influence](help:holy-influence).
<!-- /tui -->
<!-- gui -->
**Confidence through Sin** and **Infernal Influence**, in the [Deeds chapter](help:tab-deeds)
under The Infernal, are there for a sinner (or one who knows Infernal
Lore). **Holy Influence**, for one of holy standing, is in the Religion
chapter.
<!-- /gui -->

**Sympathy Traits.** A Personality Trait can be a faerie **Sympathy Trait**: tick *Faerie
Sympathy Trait?* on its form, and the list shows it as "Winter: +3 (Sympathy)". A Sympathy
Trait is a bond with a narrow class of things through the Faerie realm (Winter, Iron, Hounds,
never a whole Form). Where it fits, it can stand as a non-Supernatural Ability's specialty,
adding its score in place of the +1, but the roll becomes a stress roll and a botch Warps;
only the best fitting Trait counts. A negative Trait comes off every Ability it fits, and the
worst one adds its size in botch dice (Realms of Power: Faerie p. 102). Experience raises a
Trait as an Ability, to no more than the Warping Score, 5 xp a season of practice; a negative
one rises only while the Warping Score is above its size, 10 xp from -1 to 0, 15 from -2, 20
from -3, and may go on through 0 (p. 103; Errata p. 68). Traits gained by sympathetic
influence or granted by a Grant rite are temporary Sympathy Traits: tick *Temporary Sympathy
Trait?* as well, and the list shows "Oak: +2 (Sympathy, temporary)". They work as Sympathy
Traits (a specialty, a folk charm, a rite's limit, botch dice), but experience doesn't raise
them, the Warping Score doesn't limit them, and they don't count toward the Faerie Rank
(pp. 103-105, 127). The Traits a tinted aura gives everyone in it are plain Personality
Traits (p. 104).


### Reputations
<!-- help: section-reputations -->

The character's Reputations, each a name and a score that you type
(Ars Magica Definitive Edition, Chapter 3: Characters). A Reputation may also say its type (Hermetic, Local, Noble, Academic,
Ecclesiastical or Infernal) and how far it reaches, both shown in
brackets after its score.

A **Noble** Reputation is known among the landed class: everyone who holds
land or a great lord's office, or may inherit them (Lords of Men p. 25).
Entering feudal life, by birth or by becoming a vassal, starts one at 1;
each season of great deeds noted by other nobles is an experience point in
it (hosting a tournament, making war, leading pilgrims), and some events
give more: a season at war in a distant land 1 more, knighting a squire he
trained 1, gaining a noble liege 3, a royal liege 6, study under a
supernatural creature its Might / 5 (p. 26). A knight's prize Reputation is
**Prudhomme**: tournaments read it.

Someone has heard of the character when a stress die + the score reaches
0 in the same village, parish or covenant, 6 in the same town, diocese or
Tribunal, 9 in the county, province or whole Order, and 12 in the country
or the whole Church (DE pp. 28-29). A noteworthy deed before witnesses who
talk starts a Reputation at 1, and each later one is an experience point
in it, as for an Ability: ten deeds take it from 1 to 2 (DE p. 386). Type
the new score when it rises.

Whether a Reputation is good or bad is yours to say, by its sign: type a
bad one with a negative score (Drunkard -2) and a good one with a
positive score. Academic Reputations are kept apart instead (Art &
Academe p. 103): a Good and a Bad one are separate entries, each with its
own positive score that builds like an Ability, and a scholar may hold
both at once (Good Logician and Bad Argumentative). Tick **Bad
Reputation?** on a bad one; any Reputation may be marked so. A roll adds
the highest Good Academic Reputation and takes off the highest Bad one
(pp. 89, 100). A save that typed a bad Academic Reputation below 0 is
read as a bad one of that score. A university exam adds the Good Academic Reputations and
takes off the Bad ones (only academic ones count), and needs a net 1, 2
or 3 for the baccalaureus, magister or doctor, after 3 years, 8 and 10 at
university, counting the exam season (Art & Academe p. 100). The doctor
exam needs the Magister in Artibus Virtue already (DE p. 76) and uses the
faculty's Ability. Disputatio and debate count the highest good one.

A bad Reputation can be **replaced** (DE pp. 386-387). Start the new one,
at 1, with a deed spectacular enough to begin a Reputation, and on its form
choose the bad one it **Replaces**. End of Session then asks, for the new
one, the deeds that support it (they count toward it alone) and the other
noteworthy deeds, which still count toward the old one until the new one's
score passes it, and toward the new one after. Once it is ahead, each time
it gathers the experience to rise you may lower the old one by a point
instead (ticked by default). An old Reputation lowered to 0 is gone. The
Reputations list marks a new one "replacing" the old.

More offers **House Acclaim** to magi of Bonisagus and Flambeau, and
**Reputation Roll** to anyone with a Reputation.


### Lineage
<!-- help: section-char-lineage -->

A magus's line, read from each character's **Parens** (Hermetic
Background): his parens, theirs and so on back as far as the saga names
them (a parens who isn't a character of the saga ends the line), and below
him his filii and theirs, an apprentice marked so. It shows for a
character with a parens, or with filii in the saga. Change it by editing
the Parens on the Hermetic Background.

### Marriages
<!-- help: section-char-marriages -->

Shown once a marriage names the character as bride or groom: each with
the spouse, when, the dowry and whether it is a betrothal, a marriage or
ended, and how it ended. Marriages are arranged and ended on the
Marriages tab of either family's lord (Lords of Men pp. 10-11, 81; City &
Guild p. 113), which lists the same record: nothing is copied here.

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
willingly** skips the roll to avoid it (DE p. 228). A botched spell gives a
Warping Point for each zero on the botch dice (DE p. 227): type them there as
one event. The form also keeps the **Twilight Scars**, one a line, and More's
[Resolve Twilight](help:resolve-twilight) applies what a Twilight left. When Winter is applied, the app
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

A magus with the Lesser Elixir in force shows "Lesser Elixir: -N more":
its Level, taken off his aging rolls with the Longevity Ritual's modifier
(The Mysteries Revised Edition p. 42; see Reinvent the Lesser Elixir).
A magus the Great Elixir made a being of Magic shows "A being of Magic":
he makes no more aging rolls and gains no Warping, and his Magic Might
shows beside his Size (p. 44; see [Test the Great Elixir](help:great-elixir)).

**What gave them** says where the points came from. One event (a
powerful effect, a botch) is the usual; **Taken leaving Faerie** asks for
the **Days spent in Faerie** and the **Final fable score**, and writes
into the Diary how long passed in the mundane world: each day there
lasts an hour at fable score 0, 12 hours at 1, a day at 2, three days at
3, a week at 4, a month at 5, a season at 6 and a year from 7, and each
Warping Point taken lowers the score by 1 (a group leaving together
takes the lowest, the others taking points to match; Realms of Power:
Faerie p. 30). **Instant transport** is a point a transit: a spell or
device of level 30 or more that carries someone gives a Warping Point
each time unless they cast it or it was made for them, and a Hermes' or
Mercere's Portal gives none (Transforming Mythic Europe pp. 112, 114).
Neither brings Twilight, however many points: Faerie's never do, and
each transit is its own event.

The app counts the Warping Points from each realm as they come (an
event's **Its realm**, an aura's or a place's realm, a Longevity
Ritual's Magic) and the section shows the count and the main source,
the realm with the most (a tie, or nothing counted yet, goes to the
aura where they live). A non-magus's Warping effects follow it: the
Definitive Edition's own for Magic (DE p. 391); for Faerie a glamour of
their own may take the first Flaw's place, a Reputation that rises with
each Score and brings Sympathy Traits later, with Faerie Antipathy or
Lesser Malediction at 3 (Realms of Power: Faerie p. 119); for the
Divine, Flaws that punish sin or push piety to extremes (Realms of
Power: The Divine p. 62); for the Infernal, a sinful Personality Flaw
at 1, Offensive to Animals or Tainted with Evil at 3, an Infernal Virtue
at 5 and Age Quickly, Enfeebled or Plagued by a Demon from 6 (Realms of
Power: The Infernal p. 17, with the Errata naming Aptitude for (Sin)).
The Virtue at Score 5 stops Warping only from auras of the main
source's realm (DE p. 391).

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
gives nothing. A covenant drawing on Emergency Savings can keep no
regimen: its bonus stops (Art & Academe p. 58). Eucrasia is lost, and the
regimen starts its year again, when the patient plays a season
convalescing or travelling, catches a disease, or enters Wizard's
Twilight (p. 59); the Diary says so. For the other causes (a month away,
a neglected diet, broken sleep, a day under a Corpus spell) retype the
regimen's year it began on Edit.

**Faerie Rank.** A character with Sympathy Traits shows his **Faerie Rank** under his Warping:
his best positive Sympathy Trait plus his worst negative one (Winter +4 and Summer -2 make
+2; Dancing +1 and Stone -5 make -4), temporary Traits apart (listed after it), the botch dice his worst negative Trait adds, and how far
experience may raise his Traits (Realms of Power: Faerie p. 103). Faeries like a high Rank and
dislike a negative one. A Faerie Calling (when a faerie wizard takes Warping) now says whether
his Rank makes it a good Calling or a bad one (p. 120).

Sympathetic influence, for the storyguide: a ceremony of about ten minutes, led by someone with
Faerie Lore 1, costing everyone taking part a Confidence Point and lasting a week at most; or
a season of free time spent with the subject, lasting up to a year. Then a simple die +
Presence + Leadership: 9 gives a Trait of 1 (or -1), 15 of 2, 24 of 3, the most. The subject
needs a fitting Personality Trait or Flaw; a fitting Sympathy Trait may be Leadership's
specialty, on a stress die (pp. 103-104).

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

With the **Art & Academe medicine** rule option, an injury's Recovery
counts **first aid** and **palliative care** in place of the medic's whole
Chirurgy: first aid given within a day of the wounds adds half the
first-aider's Chirurgy, rounded up, and palliative care, the nursing
afterwards, adds half the Chirurgy of the covenant-mate who nurses best
(a palliative care specialty counts). The two together never come to more
than the nurse's Chirurgy: a medicus with Chirurgy 5 who gives both gives
+5, not +6 (Art & Academe pp. 61-62). A wound that has had first aid is
marked "first aid" in the list. A disease, poison or deprivation still
takes the physician's Medicine.

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
With Art & Academe's medicine, first aid is rolled from
[Recovery Roll](help:recovery-roll): Dexterity + Chirurgy + Recovery
Modifiers + magical aid + stress die against the Improvement Ease Factor
of the worst wound; success lets the wounded act a category less injured
for a day (still taking the Wound Penalty), and a botch gives no first-aid
bonus and an immediate Recovery roll for the worst wound (Art & Academe
p. 61).

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

More on Known Spells, for a magus who may boost one of them: Boosted
Magic boosts any Formulaic spell (DE p. 72), a Boosted spell needs
Boosted or Mutantum Magic, and Boosted Casting comes with Mastery
(Houses of Hermes: True Lineages pp. 99-103). Choose the **Spell**, then
the **Range**, **Duration** and **Target** it is raised to and how much
**Larger by**. The inspector gives the pawns of vis it takes (one a
magnitude), the botch dice they add (one a pawn), and what stops it:
nothing is lowered, and Year or Boundary is reached only by a Ritual. It
is a calculator: it changes nothing, and the spell is cast at the table
at its own level.

## Resolve Twilight
<!-- help: resolve-twilight -->

More on [Aging & Warping](help:section-aging). After a Twilight the app has
rolled (its Diary line says how many points it gave and what they buy), this
applies the storyguide's choice (DE pp. 229-230). Tick **Comprehended** if it
was, type the **Warping Points gained** in all, and choose the **Effect**:

- **Experience**: twice the points in an Art, Magic Theory or Enigmatic
  Wisdom, gained if comprehended, lost if not (never below 0).
- **A Virtue or Flaw**: from 7 points, a Hermetic or Supernatural Virtue if
  comprehended (Minor to 10 points, Major from 11) or a Flaw if not (Major
  from 10). One that names something (an Art, an Ability) is added from
  Virtues & Flaws instead.
- **A spell**: learned, of as many magnitudes as the points, or lost; a
  Twilight that takes several spells is resolved once for each.

Type the **Twilight Scar** it left: it joins the Aging & Warping section's
scars, and the whole goes in the Diary.

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
  With Hermetic Projects in play the tables add a volcano's hazards (pp.
  13-14): lava +15 each round (x2 a limb, x3 half the body, x4 immersed;
  armour counts only while it covers less than half the body), boiling
  mud +3, the heat within 30 yards of lava +3 a Diameter, and falling
  rocks in an eruption +5 at its edge to +20 at its heart. Its fumes are a
  poison, a Stamina check against 6 each Diameter or a Medium Wound,
  beside an air Deprivation check every 30 seconds.
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

With Art & Academe's medicine, an **injury** asks where it struck (the head,
the torso or a limb). An Incapacitating wound it deals calls at once for a
Stamina roll against 6 (Lasting Consequences of Serious Damage, A&A p. 43);
a failure leaves a lasting complication, a Minor Flaw fitting the place,
from those Surgical Intervention lists (p. 62): the head Disfigured, Missing
Eye or Missing Ear; the torso Disfigured or Fragile Constitution; a limb
Disfigured, Lame, Missing Hand or Palsied Hands. The storyguide picks it; the
Diary keeps the roll.

Each of the book's **diseases** is an excess of a humour (pp. 47-51). One of
the character's own principal humour is ill-suited to the temperament: the
result says so, as a place that breeds it is worth a roll or two in the first
season there (p. 46).

The disease list also holds Dies Irae's **Great Pestilence** (pp. 86-98): a
Critical phlegmatic disease of Severity 21, Stable 12, Improve 18, rolled
every day once its Crisis passes. *The Great (Form) Pestilence* is a magic
being's: a Disease Avoidance roll at the Form's new moon and each week it
stays in a Magic aura (pp. 87-88). *The Great Corpus Pestilence (Corpus
miasma)* is what a Corpus miasma's Corpus Blight gives every human it
touches: no Disease Avoidance, but its Penetration is 0, so magi and all others with Magic
Resistance are immune (pp. 88, 94): a magus's Corpus and Parma, or True Faith, a Church
office and relic, or Angelic Might.

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

With the **Art & Academe medicine** rule option, Recovery Roll also
offers:

- **first aid**: a chirurgeon (anyone in the saga with Chirurgy, the
  patient too) tends the injuries. Each injury without first aid keeps
  half his Chirurgy, rounded up, as a bonus to its Recovery rolls, and the
  First Aid roll (Dexterity + Chirurgy + Recovery Modifiers + magical aid
  + stress die against the worst wound's Improvement Ease Factor) says
  whether the patient may act a category less injured for a day. A botch
  gives no bonus and makes an immediate Recovery roll, which can only hold
  or worsen (Art & Academe p. 61). Use it within a day of the wounds.
- **surgery** on a disease: choose the disease and the procedure. The
  Surgery roll is Dexterity + Chirurgy + Recovery Modifiers + stress die
  against the procedure's Ease Factor: phlebotomy 3 and cautery or
  cupping 4 (both a Fatigue level, and only for a disease of Severity 5 or
  less), a rotten tooth 6, quinsy or a cataract 9, trepanation 12 (each a
  Light Wound), a gall stone or fistula 9, a cold or hot tumor 12, a
  consumptive tumor 15 (each a Medium Wound). The wound comes whatever the
  roll; a botch makes it a step worse and leaves the disease be. A success
  returns the disease to the stage it began at and gives +3 to its next
  Recovery roll (Art & Academe p. 61). Whether surgery can help a disease
  at all is in its description.
- **Surgical intervention when a roll fails**: tick it, choose the
  chirurgeon and where the wounds are (the head, the torso, a limb), then
  roll. Each Recovery roll that fails gets a Surgery roll against 9: a
  success holds the wound as a stable result, with its +3; a failure lets
  it worsen; a botch worsens it two steps (a Light wound to Heavy, a Medium
  to Incapacitating, anything worse to death). Whatever the roll, the
  patient keeps a consequence by the wound's severity: a Light wound an
  immediate Aging roll (made when you Keep, in the Diary), a Medium two
  Aging Points in a Characteristic of that place (Intelligence,
  Perception, Communication or Presence for the head; Stamina or Strength
  for the torso; Dexterity or Quickness for a limb), placed with Place
  Aging Points, a Heavy a Minor Flaw and an Incapacitating a Major Flaw of
  that place (Blind, Deaf or Mute; Disfigured, Missing Eye or Missing Ear
  for the head; Crippled or Enfeebled, Disfigured or Fragile Constitution
  for the torso; Crippled or No Hands, Disfigured, Lame, Missing Hand or
  Palsied Hands for a limb), which you add on Virtues & Flaws (Art &
  Academe p. 62). The season's own healing rolls never intervene.

## End of Session
<!-- help: end-of-session -->

<!-- tui -->
More (`m`) on [Reputations](help:section-reputations) offers **End of
Session**:
<!-- /tui -->
<!-- gui -->
**End of Session**, in the [Deeds chapter](help:tab-deeds) under Session & Reputation, opens a
form for
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
Reputation is replaced only by starting a new one (DE p. 386): for one
that **Replaces** another, the form asks the deeds that support it and
the other noteworthy deeds apart (see
[Reputations](help:section-reputations)). The Diary records the session.

<!-- tui -->
**Tournament** (More, `m`, on Reputations, while Lords of Men is in play)
counts a season on the tourney circuit (Lords of Men pp. 64-69). Choose his Prudhomme Reputation (or start
one: a Noble Reputation, at 1 when it is his first, the 1 a man gains
entering feudal life, Lords of Men p. 25, else at 0) and tick what he did as a knight: riding at
the head of a company, ransoming a well-matched opponent, a feat of daring
or of unquestionable honour are 1 experience point each, ransoming a
stronger opponent or winning a prize 2; only the highest counts (p. 68).
As patron, hosting one or more tournaments that season is 1 point, a lavish
one 2, and an artist's record of aesthetic quality at least his Prudhomme 1
more; patrons hosting together share the points equally, rounded down
(p. 69). Each ransom he didn't pay is an experience point toward a fitting
bad Reputation (p. 67): add that Reputation first, then choose it. The
result says what a tournament he hosts should cost (10 pounds a point of
his Prudhomme), what a prize for him is worth (a pound a point), and, from
his Dexterity + Single or Great Weapon x his Wealth Multiplier, the Labor
Points a season on the circuit makes him and how many seasons a year keep
an errant knight (36 Labor Points a year, p. 69). It is written in his
Diary.
<!-- /tui -->

## Melee Event
<!-- help: melee-event -->

**Melee Event** (More on Reputations; on the desktop, in the Deeds chapter
under Knightly) rolls the Melee Events Table for a
tournament's grand charge (Lords of Men p. 68): a stress die + his
Prudhomme Reputation + any Confidence spent (either way), with a botch die
more for each event he has already rolled in this melee. The result names
the knight or company that presents itself, the ransom fair from him (from
a Wealthy knight his horse and armor, an average one his horse or armor, a
Poor one perhaps his weapons, little from a young one; never service or
an oath, p. 67), and the Light Wounds his opponents already carry (one for
each event past the first). A botch is an accident. Tick **With a
company** for a company's single roll. Each roll is written in his Diary;
the fight itself, and taking the ransom, are played out. Ransoms he takes
or leaves unpaid count on Tournament.

Melee Event and Tournament are offered only while Lords of Men is among
the saga's books in play, as is every action a supplement brings. On the
desktop, Tournament is in A Season's Work, under This Season on the Planning chapter.

## Labor Points from a Story
<!-- help: labor-from-story -->

<!-- tui -->
More (`m`) on [This Season](help:section-char-season) offers **Labor Points
from a Story**:
<!-- /tui -->
<!-- gui -->
**Labor Points from a Story**, in A Season's Work, under This Season on the Planning chapter,
opens a form
for
<!-- /gui -->
the Labor Points a story gives a craftsman or merchant when its central
issue is resolved (City & Guild p. 39). Choose the award: the book's guide
(half a season's worth for a subplot of a story the magi deal with, one for
severe danger or hardship, one and a half when his part is pivotal to the
end, two when he is the central character, two and a half when failing
would bring severe repercussions on his city or covenant), or one of the
story seeds' own awards. A trader sees the stories for every merchant (pp.
111-115) and those of his kind and the poorer kinds: local carrier (pp.
116-118), merchant adventurer (pp. 119-121), factor (pp. 122-128) and capo
(pp. 129-130); "invested" awards are the smaller ones for a story left
unplayed as an investment of time (p. 40). Change the seasons' worth where
the story says so (antique sailing instructions give ½ to 1½). A season's
worth is what a season's work earns: (Characteristic + the Craft or
Profession chosen) x the Wealth Multiplier (2 Poor, 3 average, 6 Wealthy); a
fraction rounds down. The Labor Points are added and the Diary records the
story. A story is the only way to earn Labor Points and experience other
than Exposure in the same season, so plan the season as usual. Some awards
do more, which the result says and you apply by hand: a new product found
in every fair promotes him to Wealthy (or, Wealthy, to the next Social
Status), and with the Heir Virtue a benefactor's murder may raise his Social
Status at once.

## Sell Finished Goods
<!-- help: sell-finished-goods -->

More's Sell Finished Goods, on a craftsman's This Season, settles a sale
the story calls for with a roll, rather than leaving it off-stage (City &
Guild pp. 75-76). Give the goods, the guild's standard price for them in
pence, and the customer.

- A typical customer: Presence + Bargain + a simple die against 9. Making
  it sells for 10% over the standard price, and each point over 9 another
  10%, at most 50% over. Missing it sells at the standard price.
- An important character or another player: Presence + Bargain + a
  stress die against his Communication + Bargain + a stress die (type
  his roll). Each point you win by is 10% more, each you lose by 10%
  less, at most 50% either way. A botch sells for next to nothing.

Leave the Die blank and the app rolls it; type it to use the table's.
Superior and excellent goods aren't priced by the guild: give a higher
standard price for them. The sale is written in the Diary; the purse on
Personal Gear is not changed. This is apart from the Goods catalog's
commodity prices.

## Make a Ligature
<!-- help: ligature -->

A ligature is a small charm, a sack of parchment, stones or herbs with
an Arcane or Sympathetic Connection to its target, that helps one roll
(Art & Academe pp. 68-69). Anyone with Artes Liberales, Philosophiae or
Medicine can make one, tied to an Ability he has at 1 or more; it takes
a few hours and helps within a six-hour window on the day it is made
for, up to a year ahead.

- The roll: Intelligence + the Ability + a stress die. 9 gives +1, 15
  +2, 24 +3 (the most).
- A botch works against the action: -2 and two more botch dice, and the
  maker doesn't know it.
- One ligature at a time helps a person. None helps a season's work
  (study, a Lab Total), and a medical one no Recovery roll.
- Each takes 1 Labor Point from an apothecary's store: tick "From his
  own store" when it is his, and the point comes off his Labor Points.

The roll and its result go in his Diary.

## Apothecary's Store
<!-- help: apothecary-store -->

An apothecary (Profession: Apothecary) keeps a store of medicinals
(Art & Academe pp. 63-66). A season keeping it ("Keep an apothecary's
store") earns (Intelligence + Profession: Apothecary) x the Wealth
Multiplier Labor Points; each Winter the business loses 36, and 3 more
for each physician whose regimens it supplies (a physician who keeps
his own store supplies himself; otherwise the best apothecary at his
covenant does). Each theriac or reagent made from it costs 1 Labor
Point per 5 levels (the level times the doses), and each ligature 1.

More's Apothecary's Store rolls one of two things, written in his Diary:

- **Search for an ingredient**, instead of drawing on the store:
  Perception + Profession + a stress die against 9, a month's search.
  Area Lore where he searches lowers it, and so does each assistant (no
  more than his Leadership, each with Profession: Apothecary 1 or Area
  Lore 2); inhospitable ground +1, barren +3, winter +2, a finding spell
  such as Hunt for the Wild Herb -3. Success finds a Labor Point's
  worth, each point over another (or halves the time); a botch finds
  nothing. What is found pays for that need only: it never adds to the
  store's Labor Points.
- **Preserve an ingredient**: Dexterity + Profession + a simple die
  against how long it must keep: weeks 3, months 6, seasons 9, years
  12, decades 15, indefinitely 18. A plant or animal Arcane Connection
  kept longer than it lasts lasts a category longer.

Medicinals come in four degrees; the fourth destroys tissue and is a
poison. Only a simple poison (a Light Wound, resisted at 6 or less) is
made without its formula; stronger ones are theriacs (below).

Magic can help: a Ritual Creo spell adds 1 Labor Point for each variety
it creates; a Rego Craft spell prepares a week's ingredients at
Intelligence + Finesse against the Ease Factor + 6.

## Philosophic Alchemy
<!-- help: philosophic-alchemy -->

A magus with Philosophic Alchemy (The Mysteries Revised Edition pp.
40-41; it builds on Hermetic Alchemy) settles an alchemical vis
extraction to digest by itself while he does other work. More's
**Philosophic Alchemy** on This Season settles one, starting this
season:

- **It makes**: Vim vis, a Form's vis (Hermetic Alchemy's twentieth of
  the Lab Total, a tenth with that Form's Extractor Virtue), or **open
  spaces in a device**: an invested device on his or his laboratory's
  Inventory, not yet opened.
- **Vessel's Shape and Material bonus**: what the object the vis settles
  in gives, up to his Magic Theory (Hermetic Alchemy, pp. 39-40).
- **The pawns go to**: his own raw vis, his laboratory's or his
  covenant's stores.
- **The spaces count as** (for open spaces): **pawns already opened**,
  so opening the device costs that many pawns fewer, or **extra room on
  top of its capacity**, so the device holds that many spaces more,
  already open, and opening the rest costs its normal capacity (p. 41
  offers both).

Each season it runs, its Lab Total is his alchemical Creo Vim total in
his laboratory's Magic aura (the Form as a requisite for a Form's vis;
spaces are always Creo Vim), less his days away from the laboratory.
The Minor Virtue's digestion takes four seasons and yields by the lowest
of the four; the Major's one season. Vis goes to the pool chosen. Spaces
counted as pawns already opened make the device ready for enchantment,
and opening it normally costs that many pawns fewer (p. 41: eight spaces
in a 24-pawn coral leave 16). Spaces counted as extra room raise its
capacity instead (the coral holds 32, 8 of them open, and opening the
rest still takes 24); its Inventory shows them as extra room.

While it digests:

- His other lab work that season loses the seven days he tends it, added
  to his days away: nothing until the two pass ten days (a line
  "Tending the digestion" in its Lab Total), and no other lab work at
  all past twenty.
- He can't extract vis any other way, nor work in another laboratory.
- Reading or studying vis beside it is fine; a month lost to
  distractions, a season out of the laboratory (an adventure, travel), or
  experimenting, spoils it: it is abandoned and gives nothing.

With one running, the same More command shows it and can abandon it.
Each season of it is written in his and the laboratory's Diaries and in
the season's record.

## Test the Great Elixir
<!-- help: great-elixir -->

A magus with the Great Elixir (The Mysteries Revised Edition pp. 43-44;
it needs Unaging and the Lesser Elixir) drinks the potion he has
enchanted and tests it. More's **Test the Great Elixir** on Aging &
Warping asks:

- **Grant Might's level**: the level of the Grant Might effect invested
  in this potion. It gives Magic Might of half (level - 20): a level 80
  effect gives 30.
- **Die**: a simple die, or blank for the app to roll it.

The roll is the die + Stamina + his Lesser Elixir Level + 1 for each
earlier attempt (at most his Magic Theory), against an Ease Factor of his
age / 10, rounded up. The inspector shows the bonus, the Ease Factor and
the Might as you type.

On a success he becomes an immortal being of the Magic realm with that
Magic Might, shown on his record beside his Size. From then on he makes
no aging rolls and gains no Warping. A failure means this potion's
effects did not work for him: a new dose of the Lesser Elixir and new
effects make the next potion, which adds 1 more to the roll.

Once immortal, he may test a better potion to raise his Might: the Ease
Factor stays at the age he transformed, the earlier attempts count
afresh, and a failure only wastes the potion. Every test is written in
his Diary.

## Dream Working
<!-- help: dream-working -->

A magus with Dream Magic (The Mysteries Revised Edition pp. 102-107)
sends his spirit into a dream; his body lies in a trance. Dream
Working (More on his record or Known Spells; on the desktop, in
Magic Outside the Lab under Raw Vis) rolls one of five things and
writes it in his Diary:

- **A spell in the dream.** Every spell is Imaginem there: he casts with
  his Technique and Imaginem whatever the effect's Form, using that
  Form's guidelines (p. 103). The aura is the dream setting's (a dream
  cathedral is Divine), not his body's. His real wounds, Fatigue and
  gear stay with the body; only dream wounds take from his totals, and a
  spirit loses no Fatigue (p. 106). His Magic Resistance there is
  Imaginem + 5 x Parma Magica + the aura; Parma stretched over body and
  spirit as two is 3 less (p. 103). A botch gains real Warping Points,
  and Twilight is real, timed in the waking world (p. 106).
- **The dreamer notices travelers:** Perception + Awareness + a stress
  die against 9 (p. 105).
- **The dreamer reshapes the dream:** Intelligence + a stress die, +3
  for a magus (or similar power), +3 for Dream Magic, +3 for Hermetic
  Dream Interpreter and +1 for each other power of illusion or dreams
  (at most +3), against 9. The total is the change's magnitude (p. 105).
- **A wound in the dream:** Stamina + a stress die + the earlier dream
  wounds' penalty (+3 Strong-Willed, +3 Enduring Constitution, -3 Low
  Tolerance, and any other modifier) against the total Wound Penalty,
  9 for an Incapacitating wound; failing, he wakes (p. 106).
- **The entranced body is disturbed:** Stamina + Concentration (the
  body's Wound Penalty three times) + a stress die against the
  Definitive Edition's distraction less 3: jostled or a sudden noise 6,
  knocked down 9, hurt 12 (p. 102; DE p. 215).

Spells may use Dream Duration (as Concentration) and Dream Target (as
Individual); Dream Target only on a spell with Mentem as its Form or a
requisite, as the Greater Dream Grimoire's Rego Corpus and Rego Terram
spells have it (pp. 103-104, 109), and a spell without one is refused.
Only a magus with Dream Magic may learn them.

## Hermetic Sacrifice
<!-- help: hermetic-sacrifice -->
Hermetic Sacrifice (The Mysteries Revised Edition p. 117) lets a pure,
unblemished beast sacrificed on a pagan deity's altar stand in for 1
(a lamb) to 6 (a lion) pawns of the vis of a Ritual that summons that
deity, cast via the altar. A beast created or altered by magic is never
acceptable. The deity must cooperate: forcing the spirit with Hermetic
Synthemata spoils the altar (Errata p. 51).

Hermetic Sacrifice (More on his record or Known Spells; on the desktop,
in Magic Outside the Lab under Raw Vis) takes one of
his known Rituals (or a level typed) and shows the vis it still needs: a
pawn a magnitude, halved with Mercurian Magic and a third more with
Waster of Vis, less the sacrifice, never below 0. **Pay the vis still
needed from** takes the rest from his own raw vis (the default), his
laboratory's or the covenant's stores, of the Ritual's Technique unless
**Of** names another Art; Save is refused when there isn't enough. Choose
**Not now** to pay it by hand. Saving writes it in his Diary.

## An Artist's Career
<!-- help: artist-career -->

An artist's Artist Reputation is named for his Craft or Profession (a
painter's "Painting") and rises as an Ability does, by its own
experience only (Art & Academe pp. 126-127). The app keeps one
Reputation per trade: an artist's Artist Reputation and a craftsman's
(Craft) Reputation (City & Guild p. 74) are the same score, and both
books' experience feeds it (a piece over three times the Reputation, a
patron, a muse; a Workshop Total 6 over the Craft Level, a wondrous
item, shoddy goods). Neither book says they are one Reputation: merging
them is the app's reading, and it lets workshop seasons raise a score
that Art & Academe raises by an artist's own deeds only. More's An Artist's Career rolls, or
records, what happens between his seasons, each written in his Diary:

- **Seek a sponsor** (a season): Communication + Bargain + Artist
  Reputation + a stress die against 12, -3 for a benefactor's single
  piece, +3 for his second, +6 past two, +9 to make him a patron; +3 or
  +6 for the sponsor's Minor or Major Social Virtue, and + his highest
  business or social Reputation (p. 131). Asking the same man again adds
  +3; picking him first with Perception + Folk Ken against 12 adds +3,
  and a botch there picks the wrong man. A new benefactor is 3 xp in the
  Reputation, a patron 6. At Reputation 4 he needs a sponsor of
  Reputation 2; at 6 a Minor Social Status Virtue too (or Wealthy, or a
  Major one); from 8 only a patron with a Major Social Status Virtue and
  Wealthy or a Reputation of 4. A character sponsoring him pays at least
  a Mythic Pound per point of his Reputation for a season's piece.
- **Perform in trying conditions** (before a king, in the rain):
  Communication or Dexterity + Profession + a stress die against the
  piece's Aesthetic Quality / 2 (p. 125).
- **Keep a sponsor** after a season off the piece: a simple die of 6 or
  more and the sponsor leaves him (p. 131).
- **A deed**: the gains and losses of p. 126 (a patron lost -12, barred
  from a society -15, signing without Reputation 8 -10...). From
  Reputation 10 he loses none.

The inspector shows what his Reputation brings (pp. 126-129): from 6, +1
per point over 5 to social rolls his renown sways; at 7 a minor muse
watches him, at 9 a major one; at 8 he signs his work and gains a
Confidence point; at 10 every piece gains +3 and no xp is lost; at 11 his
muse takes him, a legendary artist of Might twice his best Craft or
Profession. A muse's bond gives 1 Warping Point a year (3 a major muse).

## A Scholar's Career
<!-- help: scholar-career -->

More's A Scholar's Career rolls, or records, a scholar's steps between
his seasons, each written in his Diary:

- **Seek a place at a school**: the parent's (or his own) Presence +
  Bargain, Charm or Guile + a stress die, against 6 for a rural parish
  school, 9 an urban parish or monastic school or a citizen's urban
  school, 12 a cathedral school or a foreigner's urban school; Intrigue
  serves too but for a parish school, and those last ones take off his
  highest Bad Reputation. A wealthy family's gift adds +1 to +3. A
  failure may try again next year; a botch, never with that teacher
  (Art & Academe pp. 81-87). The inspector shows what the school teaches
  and to what score (the Limits of Education, p. 79), and a year's fees.
  Acceptance is 1 xp toward his Good Academic Reputation.
- **A deed for the Academic Reputation** (p. 103): each of these earns a
  Good Academic Reputation 1 xp: a summa at half his score, a tractatus,
  two lecture commentaries, a translation into Latin, raising Artes
  Liberales, Philosophiae, Theology or Law, a gloss of a text a school
  teaches, acceptance as a student, a teaching or church post. A Bad one
  gains 5 for being forced out of a post, no summa in five years, a
  benefice lost or immoral deeds, 10 for a clerical position lost, 1 for
  no tractatus or commentary in two years or a year with no Good xp.
  Against another faith, the xp is doubled (p. 88). Name the Reputation,
  or the xp goes to his highest of that side (a new one if he has none);
  a Good and a Bad one are separate entries, each with its own positive
  score.
  Hermetic Arts earn none.

## Byzantine Customs
<!-- help: theban-customs -->

<!-- tui -->
With The Sundered Eagle in play, More (`m`) on a person's record offers the
Theban Tribunal's customs:
<!-- /tui -->
<!-- gui -->
With The Sundered Eagle in play, the Theban Tribunal's customs are spread
by what they are: Hermetic Letter and Invoke a Broken Oath in the
[Deeds chapter](help:tab-deeds) under Tribunal & Order, Make Greek Fire in A
Season's Work on the Planning chapter (it takes a season), and Paint an Icon, Venerate an Icon
and A Mother's Curse in the Religion chapter's Faith:
<!-- /gui -->

- **Hermetic Letter**: a letter in the Theban magi's rhetorical style, a
  far-fetched tale of the writer's patron standing for his covenant and
  the letter's purpose (The Sundered Eagle p. 44). Composing one takes a
  day: Communication + a Lore + a simple die against 6 for a plain
  message, more for a subtler one. Reading its purpose is Intelligence +
  a Lore against the same. Nothing is kept.
- **Invoke a Broken Oath**: made by the injured party, back where the oath
  was sworn (p. 48): Communication + Charm + a simple die, +6 if Styx was
  named in the oath, against 15 + a simple die. Heard, the spirit that
  witnessed the oath punishes the oath-breaker with a Flaw: a Minor one,
  or a Major one from an entity of Might 40 or more. Choose the
  oath-breaker and a malediction, and a heard oath lays it on his sheet;
  leave it blank and the storyguide decides. The book's maledictions are
  in the catalog: Ashen Food, Mephitic Odor and Rotting Clothes (Lesser),
  Toad of Lies, Opening Wounds and Breaking Tools (Greater). Both Diaries
  record it.
- **Make Greek Fire**: a season making Greek Fire, an alchemical reagent
  of level 15 (p. 47; Art & Academe p. 76). A stress die that matters only
  if it botches, with a botch die for each dose being made, less the
  laboratory's Safety (prefilled from his own laboratory); a botch is an
  explosion. The form shows the hand-held siphon's figures. The Diary
  records the batch.
- **Paint an Icon**: someone in Holy Orders (Priest, Eastern Priest,
  Brother Chaplain or Senior Clergy) with Theology: Christian 3 or more
  paints an eikon (pp. 133-134). Holy Orders are the ordained male clergy,
  sub-deacon and up (DE pp. 74, 500), so a monk counts only when he is
  also a priest, and a nun never. Its Aesthetic Quality is
  Dexterity + Craft: Painting, +1 for each season of Standard gilding or
  bejewelling, +3 for each Excellent result, + his Pious trait if the
  saint is his patron, + other bonuses (Art & Academe p. 124). It goes on
  the chosen church's Relics, and the painter's Diary. Plan the painting
  itself as a season's Create a work of art.
- **Venerate an Icon**: an eikon venerated adds its Aesthetic Quality / 5
  (rounded up) to invoking its saint (Communication + Charm + modifiers +
  a simple die against 15 + a simple die, p. 136), or God's aid for an
  icon of Christ. It takes an hour of contemplation, or in an emergency a
  Fatigue level and Presence + Concentration + a stress die against 15.
  The saint's miracle comes when the saint decides.
- **A Mother's Curse**: any Mediterranean mother may curse her child, for
  a good reason (p. 136): the Lesser Malediction: A Mother's Curse, -3 to
  every roll in one area of his expertise (military, academic or
  professional). The Diary records her and the task that lifts it; only
  that task done, or divine intervention, lifts it, so remove the Flaw
  then.

## Devotion and the Saints
<!-- help: devotion -->

<!-- tui -->
More (`m`) in the Faith section of a Christian's [Religion tab](help:tab-religion)
offers invoking the saints, and with The Church in play, Devotions and
acts of piety:
<!-- /tui -->
<!-- gui -->
The Faith section of a Christian's [Religion chapter](help:tab-religion)
offers invoking the saints, and with The Church in play, Devotions and
acts of piety:
<!-- /gui -->

- **Invoke a Saint** (with Realms of Power: The Divine, The Church, The
  Sundered Eagle, The Contested Isle or The Cradle and the Crescent in
  play): once a day, a heartfelt request for a miracle (RoP: The Divine
  p. 87). Communication + Charm + the modifiers + a simple die, against
  15 + the storyguide's simple die. The modifiers: at the saint's tomb
  +1, a Divine aura its level, his feast day +3, a pilgrimage in his
  honour within the year +2, a donation now +1 to +3 (none within a year
  -3), imminent peril +2, True Faith +1 a point of Score, unchristian
  acts this month -1 to -3, a miracle this month -20, and -15 for a saint
  who is not his patron. There is no -15 for his patron saint, a saint
  he has a Devotion Point toward, the Blessed Virgin (anyone may ask
  her), a saint whose concern is the matter at hand or a sacramental's
  (The Church p. 13), the saint's own relic held (The Church p. 13), or
  for one of Irish birth, Saints Patrick, Brigid and Columba (The
  Contested Isle p. 134). With The Church in play, his Devotion score to
  the saint is added, and a season's fast +1 (The Church p. 12).
  Choose a relic: one of the churches' Relics, or his own (the relic he
  relies on, on Biographical Detail). With The Church in play, the
  saint's own relic adds +2 for each Faith Point, once a day, for the one
  who tends or carries it, or a day's veneration at its shrine with the
  custodians' leave (The Church p. 13); another saint's relic, or any
  relic without The Church, +1 for touching it (RoP: The Divine p. 87).
  The relic counts once. With The Sundered Eagle, an eikon of the saint
  he venerated adds its Aesthetic Quality / 5 (p. 133). The inspector
  shows the chance, the saint's Might, feast and powers as the books give
  them, and the miracle asked. Heard, the saint works a miracle;
  refused, he may ask again tomorrow. The Diary records it.
  With The Cradle and the Crescent, a Mazdean yazata is invoked the same
  way, by one ritually pure through the Nahn rite (p. 85).
- **Threaten a Saint** (RoP: The Divine): after a saint has refused an
  invocation, the humiliation of a saint (pp. 87-88). It is offered only
  while a saint who refused him is on record (an invocation he didn't
  answer; the Faith section lists them under **Refused him**), and only
  such a saint may be chosen. A threat, or a later miracle from him,
  takes him off the list. Presence +
  Leadership + the threats (exposing his bones +1, defiling his relics
  +2, berating him before others +1, barring others from him +3,
  imminent peril +1; a miracle this month -20; -15 for an unfamiliar
  saint) + a stress die, against 9 + a fifth of his Divine Might (Mary
  100, greater saints 75, area saints 50, local saints 25, p. 89). The
  book's Mights are all multiples of 5; a custom one that isn't is
  rounded down, which is the app's choice, not the book's.
  Confidence may be spent (+3 each), Faith Points not. Succeed, and the
  miracle comes at once; fail, and he hears none of the petitioner's
  prayers for a month; fail by 10 or more, a minor curse and nothing for
  a season; botch, the saint's curse. A yazata is never threatened.
- **Patron Saint**: the saint he calls on as his own, without the -15
  for an unfamiliar saint: often his church's, his home's or his
  trade's, or one he is devoted to. Anyone may have one, Pious or not,
  and **(none)** clears it (The Church p. 13; RoP: The Divine p. 87). The
  Diary records the change.
- **Devotion Points** (The Church): offered only to one who holds a
  Devotion, or has a positive Pious trait (or the Pious Flaw) to begin
  one. A Devotion is a reverence for a saint
  (or the Virgin) that rises as an Ability does, on Devotion Points
  alone, never experience, and has no Specialty (p. 12). At creation a
  character with a positive Pious trait has as many Devotion Points (the
  Pious Flaw counts 3, its Major form 6), among as many saints; later
  changes to Pious change nothing (p. 13). In play, Devotion Points come
  from a season of personal devotion at a shrine (5), endowing a church
  to the saint (5 to 50), joining his guild (3) and rising in it (2
  each), visiting his tomb, relic or a site of his miracles (1 to 10),
  sponsoring art of him (its Aesthetic Quality), a hagiography (Quality /
  2, a general one 1), furthering his cultus (the Petitioning Ease
  Factor), witnessing his miracle (5 to 10), his feast's procession (1 to
  5), a pilgrimage in his honour, or a vision from him (1) (pp. 14-15).
  Neglecting his feast day loses at least 3 (p. 14). The Planning tab
  and the Religion tab's Faith list his patron and his Devotions.
- **Indulgence, Vigil or Fast** (The Church pp. 11-12): an indulgence
  shortens a penance, it does not forgive: about 6 pennies a season for
  the poor, a pound or more for the wealthy; after a season of
  charitable works, as many experience points in Reputation: Piety as
  the seasons, and a temporary Faith Point. A vigil, the night before an
  important event in prayer, costs a Fatigue level until a full night's
  sleep and gives a Confidence Point to spend the next day on the task
  named. A season's fast gives +1 to invoking a saint that season (Invoke
  a Saint ticks it) and a Fatigue level all season.

## Confidence through Sin
<!-- help: confidence-through-sin -->

Sin feeds the sinner's resolve (Realms of Power: The Infernal, Gaining
Confidence through Sin, p. 24). Choose a Personality Trait or Personality
Flaw with a penchant for one of the seven deadly sins, and how he sins:

- **A season indulging it** at every chance, alongside his other work: a
  Confidence Point at the season's end.
- **A short ceremony** of a ritualized sin: a Confidence Point and an
  Infernal Warping Point.

**Save** adds the point (and a ceremony's Warping Point, counted as
Infernal) and writes it in the Diary.

A trait counts toward a sin by the table on p. 21: each sin, its opposing
virtue, and five traits on either side (Proud/Loyal, Wrathful/Calm,
Envious/Kind, Slothful/Brave, Lustful/Wise, Greedy/Strong,
Avaricious/Just). Name the sin in brackets to say which a trait serves:
"Cruel (Envious)", or "Dedicated (Loyal)", which counts as Proud at minus
its score. A Minor Personality Flaw counts as a +3 trait, a Major one as
+6 (p. 24), when its name is on the table or among p. 17's sinful Flaws:
Hatred counts as Wrathful, and Delusion, Obsessed, Compulsion and
Weak-Willed count only when the detail typed for the Flaw names a sin or
its trait, alone or in brackets ("Gold (Greedy)"). Which sin those
Flaws serve is the app's reading: p. 17 names them without one. A trait of +3 or less is fed by venial sins; above that the
act must usually be a mortal sin.

One with no Confidence Score still gains the points: he may spend them on
influence or tarnish, or with the storyguide's leave +1 a point on a
fitting roll, no more on one roll than the trait's score.

The inspector also says what redemption would cost him: repentance removes
the mark of sin at any time (confession and penance, or a fast of
atonement, p. 22), but absolution takes a False Power Flaw with the Virtue
it changes (p. 89), and the False Gift with every Supernatural Ability
learned through it, the Hermetic Arts included (p. 124).

## Infernal Influence
<!-- help: infernal-influence -->

Leading others into temptation, or tarnishing an Infernal aura (Realms of
Power: The Infernal, Infernal Influence and Tarnish, pp. 23-24).

- **A person** who follows his lead: a simple die + Presence + Leadership.
  9 gives the new trait +1, 12 +2, 15 +3, 18 +4, 21 +5, 24 +6. Only the
  willing are touched; strangers only by one with Inspirational (or within
  his Temporal Influence). A trait from personal influence lingers up to a
  year, from a ceremony about a week.
- **An Infernal aura**: the same total on a stress die gives the aura a
  tarnish. It is added to similar traits of everyone inside, taken from
  opposing ones, and gained as a trait by anyone with neither. Only the
  strongest tarnish counts; a ceremonial one falls by 1 each morning, a
  personal one at each season's end. A botch brings Warping Points or
  Fatigue.

**Personal** influence is a season in company; **ceremonial** is a short
ceremony that needs Infernal Lore 1 and spends a Confidence Point. **Roll**
rolls it, spends a ceremony's point and writes the result in the Diary.

## Mystic Paths
<!-- help: mystic-path -->

<!-- tui -->
More (`m`) in the Faith section of a Christian's [Religion tab](help:tab-religion)
offers, with The Church in play, his **Mystic Path** (once he is Pious
and tied to the Divine, or already on a path), and on that path
**Spiritual Path** or **Monistic Revelation**:
<!-- /tui -->
<!-- gui -->
The Faith section of a Christian's [Religion chapter](help:tab-religion)
offers, with The Church in play, his **Mystic Path** (once he is Pious
and tied to the Divine, or already on a path), and on that path
**Spiritual Path** or **Monistic Revelation**:
<!-- /gui -->

- **Mystic Path** (The Church pp. 19-24): contemplative mysticism, the
  imitation of Christ, or monistic mysticism, the self lost in God; one at
  a time. Both need a positive Pious trait and a tie to the Divine: True
  Faith, a Divine Supernatural Ability (Sense Holiness and Unholiness, a
  Holy Method or Power, or another of Realms of Power: The Divine's), or
  Warping from a Divine source (p. 21). A contemplative has no sinful
  trait (Realms of Power: The Divine p. 40); a monist has Visions or True
  Faith (p. 23). A mystic's Warping is always the Divine Ascent, magus or
  not: a contemplative's at 2 Warping Points from one event, its form the
  Divine Form; a monist's at a single point, its form the Divine Gloom
  (pp. 21, 23). After his first Ascent the path can't be left, its form
  staying for life. The Divine Form adds his Warping Score to True Faith's
  Magic Resistance and gives Soak of that Resistance / 5 (his Warping Score
  / 5 without True Faith), both on the sheet; the inspector shows its
  Penetration (Warping Score + 5 x True Faith) and the botch dice an
  impious act adds (3 x Warping Score). In the Divine Gloom each Warping
  Point gained is an experience point among Dominion Lore and his Holy
  Abilities and one lost from mundane Abilities, never Concentration (the
  Diary says so). A monist's season practising a Holy Ability is worth his
  Concentration: type it as the season's Source Quality. The inspector
  also shows what his True Faith brings (p. 23): at 2 Premonitions and a
  Faith Point to dispel any illusion or glamour; at 3 double Magic
  Resistance against Mentem and +6 for each Faith Point spent; at 5 an
  Empyreal aura to Voice range.
- **Spiritual Path** (a contemplative's, p. 22): begin a path to a
  Revelation, a Virtue: a Minor Holy Method, Power or Supernatural Ability
  (Path Total 15), another Minor Virtue (18), a Major Holy one (27) or
  another Major Virtue (30), never True Faith. Quest Components must
  reach the Path Total itself; his Pious isn't taken off it: the seasons are
  planned on This Season (Spiritual path: service +1, devotion +1 with a
  Devotion Point toward the saint in the plan's details or his patron,
  preaching +3 once on a path, mission to heretics or infidels +9); the
  rest are kept here (+6 a minor pilgrimage for nothing else, a Vow, which
  adds the Minor Flaw, or a quest; +9 error or corruption revealed and put
  right, his wealth given as alms, which takes away Wealthy or gives Poor,
  or a year on crusade, with its temporary Faith Point, p. 19). Reached,
  claim the Revelation: the Virtue is his, its Supernatural Ability at 1
  with no penalty for his other Abilities or Arts.
- **Monistic Revelation** (a monist's, after an Ascent, p. 24):
  Intelligence + Concentration + stress die against his Warping Score +
  stress die (no botch); the inspector shows the chance. Failing, the
  Gloom comes as usual; succeeding, he also chooses: no mundane experience
  lost to this Gloom; a Minor Virtue (3 or more Warping Points) or a Major
  one (5 or more), the first always Second Sight; at 7 or more, Dominion
  Lore in place of Magic or Faerie Lore, a realm each time; after both,
  Infernal Lore.

## Spiritual Path
<!-- help: spiritual-path -->

A contemplative mystic's path to a Revelation (The Church p. 22): begin
one, count a Quest Component done in a story, or claim the Revelation once
the Path Total is reached (his Pious isn't taken off it). A season's
components are planned on This Season. See Mystic Paths.

## Monistic Revelation
<!-- help: monistic-revelation -->

After a Divine Ascent, a monist may try to integrate a Revelation (The
Church p. 24): Intelligence + Concentration + stress die against his
Warping Score + stress die. Type the Warping Points the Ascent brought
(those that set it off and its margin) and what the Revelation brings; a
Virtue needs 3 points (Minor) or 5 (Major), the first always Second Sight;
Dominion Lore in place of Magic or Faerie Lore 7, Infernal Lore after
both. The Diary records it. See Mystic Paths.

## Holy Influence
<!-- help: holy-influence -->

Leading others to virtue, or tempering a Divine aura (Realms of Power: The
Divine, Holy Influence and Tempers, pp. 38-41). The Faith section of the
[Religion chapter](help:tab-religion) offers it to a Christian, Jew or
Muslim of holy standing (clergy, a monk, True Faith, Temporal Influence,
Inspirational, or Dominion Lore); a rabbi has it over his community (p.
125).

- **Those in his care**: a simple die + Presence + Leadership. 9 gives the
  new trait +1, 15 +2, 24 +3, the most. He needs spiritual authority over
  them (a priest's parish, a parent's child, a teacher's pupil, a host's
  guests), and they must be willing. Temporal Influence serves only
  personal influence on those under his temporal authority;
  Inspirational lets him influence anyone willing, by a ceremony. A trait
  from personal influence lasts up to a year, from a ceremony rarely a
  week; one set against a Personality Flaw (a Minor counts as +3, a Major
  as +6) never becomes lasting.
- **A Divine aura**: the same total on a stress die gives the aura a
  temper: Loyal (against Pride), Calm (Wrath), Kind (Envy), Brave
  (Sloth), Wise (Lust), Strong (Greed) or Just (Avarice). It is added to
  every roll in the aura that suits it and taken from every roll against
  it, and falls by 1 each day (ceremonial) or each season (personal). He
  holds one temper at a time; a new one replaces his last. Two leaders'
  tempers in one aura are schism: an action may take both a bonus and a
  penalty (p. 41). A botch brings Warping, Fatigue or a bad name.

**Personal** influence is a season among them; **ceremonial** is a short
ceremony that spends a Faith Point (with True Faith) or a Confidence
Point, which adds nothing to the roll. A group praying with him adds its
modifier: everyone's Ceremony less their number, and each one's Presence +
Leadership (p. 36). **Roll** rolls it, spends a ceremony's point and
writes the result in the Diary.

## Invoking God's Aid
<!-- help: gods-aid -->

With Realms of Power: The Divine in play, the Faith section of a
Christian's, Jew's or Muslim's [Religion chapter](help:tab-religion)
offers Invoke God's Aid (pp. 41-42): a short prayer and a Confidence Point (a Faith
Point with True Faith; never a grog's, nor one with Low Self-Esteem). A
stress die + Communication + Dominion Lore: 9 gives +1, 15 +2, 24 +3, to
every roll in the scene clearly made toward the aim named, spellcasting
too, until one fails or the scene ends. A 0 rolls three botch dice:
divine disfavour, struck dumb, blind or clumsy until penance. Tick **For
his followers too** to ask it for those in his spiritual care (they and he
gain the bonus); with the Ceremony Ability he leads them, adding it and
each one's Communication + Dominion Lore. **In battle**, God's aid is
asked only against infidels or heretics, as his faith sees them, or a
supernatural menace not of the Divine; a Trained Group adds a member's
bonus to its combat bonus beyond the usual limit, only the highest
counting, lost when the group fails a roll or splits (p. 42). The
inspector shows each bonus's chance; the Diary records the prayer.

## Font of Knowledge
<!-- help: font-of-knowledge -->

<!-- tui -->
More on one with Font of Knowledge offers it (DE p. 165; Antagonists p.
109):
<!-- /tui -->
<!-- gui -->
In the [Deeds chapter](help:tab-deeds) under Insight, for one with Font of
Knowledge (DE p. 165; Antagonists p. 109):
<!-- /gui -->
Intelligence + Font of Knowledge + stress die against 6 + 3 for each time
he has drawn on it today, failures counted. Succeeding, he attempts a task
with the Ability he lacks as if he had it at 2. Name the Ability and how
often he has drawn on it today; the inspector shows the chance, the Diary
the roll.

## Commanding Aura
<!-- help: commanding-aura -->

<!-- tui -->
More on one with a Church office or crown (Biographical Detail), or the
Commanding Aura Virtue, offers Commanding Aura:
<!-- /tui -->
<!-- gui -->
Beside Health's buttons, for one with a Church office or crown, or the
Commanding Aura Virtue:
<!-- /gui -->
the office's Magic Resistance, its Soak (a fifth of it) and an Aura of
Rightful Authority to Voice range, Penetration 0 (DE pp. 74, 420). Tick
**Withdrawn until penance** for a legatus missus who delays or strays from
his mission, or one God's will excommunicates: the office then gives no
Magic Resistance or Soak until it is unticked. A legatus missus loses the
aura for good when his mission is done (DE p. 74; Antagonists p. 38).

## Ars Goetia
<!-- help: ars-goetia -->

The total of a Goetic Art against a spirit's Might (Realms of Power: The
Infernal, Chapter Eleven: Ars Goetia, pp. 114-119). **Close** keeps
nothing; **Roll** rolls it once and says what it did, keeping nothing
either: apply what it gives by hand.

Every total is a stress die + a Characteristic + the Art + the Lore of the
spirit's realm + the aura + Penetration x its multiplier (a demon's True
Name is an indefinite Arcane Connection), so it is its own Penetration.
Against a demon he adds his own Hierarchy x 5 (his highest Infernal
Reputation) to the total, and the target adds the demon's Hierarchy x 5
(p. 114). A sacrifice adds +2 to +10.

- **Summoning** (Presence): twice the spirit's Might holds it in his
  circle until he dismisses it, or the next midday or midnight; its Might
  alone calls it only while he concentrates. Always a Fatigue level.
- **Scouring** (Summoning at large): Area Lore, Penetration not
  multiplied; whatever answers has about half the total's Might.
- **Ablating** (Stamina): must exceed the spirit's Might (twice outside a
  circle). The margin comes off its Might, no more than all of it; a
  fifth, rounded down, are Ablation Points for Confidence, Characteristics,
  healing, a Longevity bonus, insight, experience, Infernal Might, a Power
  or Infernal vis. He also gains as much Infernal Reputation experience and
  a Warping Point.
- **Binding** (Intelligence) and **Commanding** (Communication): exceed
  its Might in a circle, twice outside one; a spirit that agrees needs only
  no botch (outside a circle, only its Might exceeded). A bound spirit
  lends its Might as Magic Resistance and holds Might x 5 spell levels; a
  command lasts until midday or midnight.

A magus who holds a Goetic Art may use Rego for it and Vim for the Lore
(p. 124); the total uses whichever is higher. Summoning may work as a
Magic or Faerie Power for the aura; the other Arts are always Infernal.

## Spirits and Names
<!-- help: spirits-and-names -->

The figures of a Mystery of spirit magic or theurgy (The Mysteries Revised
Edition, Chapters Eight and Nine, pp. 64-88). Pick the **Working**; the
inspector says what it comes to. The spirit's Might and the other figures
are the storyguide's: the sheet never knows them. **Close** keeps nothing;
**Roll** rolls where the book asks for a die (intuiting or researching
synthemata, the ascending hierarch's Stamina) and otherwise repeats the
figures. Nothing is kept: apply what it gives by hand.

- **Invoke the Spirit of (spell)** (Hermetic Theurgy, pp. 78-80): the
  spirit's Might must at least equal the power's level and is the Invoke
  spell's base level; levels added for Penetration give +2 each. The
  spirit casts at its Might + the aura, no die, and succeeds at the level
  less 10 (a magnitude more or less when he varies Range, Duration or
  Target); its Penetration is that total less the level, plus the Invoke
  spell's bonus.
- **Invoke the Spirit of (Form)** (p. 80): the spirit casts as Spontaneous
  magic at (Might + aura) / 2, rounded up.
- **Invoke the Pact of (Daimon)** (pp. 80-81): each casting that
  penetrates gathers its level less the Daimon's Might; the Aspect comes
  when they reach its Might, at once at twice its Might (the only way
  without Hermetic Theurgy). The Ritual's vis is also the Daimon Points the
  Daimon gains (p. 85).
- **Invent a theurgic spell** (p. 79): Technique + Form + Intelligence +
  Magic Theory + aura + Realm Lore + Names of Power.
- **Names of Power** (pp. 76-78): each is a Muto Vim spell of level 5 x
  its bonus; together they never add more than Magic Theory (Errata p. 50).
- **Research Hermetic Synthemata** (pp. 86-87): Muto + Vim + Intelligence
  + Realm Lore + aura + an Arcane Connection's multiplier; each season adds
  the Lab Total less the level and the name hiding (about Might / 2). The
  spell is at least the being's Might (5 more for the Lasting version) and
  adds its level (the Lasting version's level less 5) to Penetration
  against it.
- **Intuit Synthemata** and **Research Synthemata by fasting** (Synthemata
  Magia, pp. 87-88): Perception + Realm Lore + his aura against the
  being's Might + its aura + name hiding; the season's research adds an
  Arcane Connection's multiplier and ignores the being's aura.
- **Power Ritual effects** (Hermetic Empowerment, pp. 64-66): each use
  drains the Ritual's level / 5 (rounded up) from the bound spirit's Might
  Score for good; the Might x 2 must reach the level (Errata p. 50). The
  Empowering Prison's base level is at least twice the spirit's Might.
- **Bond a spirit familiar** (pp. 66-69, 81-82): Technique + Form +
  Intelligence + Magic Theory + the worse of the magus's and the spirit's
  aura, against Might + 25; a pawn of vis per 5 of the Lab Total. Might / 5
  points buy its Intelligence, Perception and Communication. A Daimon
  first takes Might / 5 pawns, and may scorn a bond of Technique + Form
  under twice its Might.
- **Blending with Substance** (Inscription on the Soul, p. 70): the
  item's best bonus plus half the rest, x 5, is the effect's level; a
  Warping Point, two at level 30 or more.
- **The Living Ghost** (pp. 70-74): his transformation limit is his best
  Technique + Form (a Magical Focus doubles the lower). Bind the Living
  Ghost is level 30 + the Haunt's Size levels; the Transformation is at
  least the limit, and his Might is its level less the Haunt's levels.
- **Ascendancy to the Hall of Heroes** (pp. 82-86): the Ascendant Form is
  at least his best Technique + Form, and 40; its level / 2 is his Might.
  Each Transformation that penetrates gives its level less the Form's,
  against the Form's level + 3 x his negative Characteristics' cost + 5 x
  Decrepitude + 5 x his Flaw points if they outweigh his Virtues'. He rolls
  Stamina against 9 or passes out.

## Ars Fabulosa
<!-- help: ars-fabulosa -->

The bargaining powers of a summoner (Realms of Power: Faerie pp. 131-134),
offered on the record, or a tradition's chapter, of anyone who holds
(Faerie) Summoning, Bonding, Captivating or Dismissing.

- Each total is the power + its Characteristic (Summoning Presence,
  Bonding Communication, Captivating Perception, Dismissing Intelligence)
  + Faerie Rank + the aura (a Faerie power) + a stress die, and costs a
  Fatigue level.
- Tick the Sympathy Traits that fit the faerie: together, negatives by
  their size, they set the most Might (or, for Dismissing, effect level)
  the power can touch, 5 for each point of all of them added together.
  Only the single highest adds to Penetration: the book says "highest"
  without saying how a negative Trait ranks, so the app takes it by its
  size (its reading, not a printed rule).
- Summoning holds the faerie only when the total equals or beats its
  Might, a random faerie called at large too: it must listen, and can't
  harm him. Only a faerie he has an Arcane Connection to must also be
  penetrated (p. 132); one called at large needn't be (p. 133). A botch
  brings a faerie all the same, hostile or unbound.
- Bonding and Captivating must exceed the faerie's Might and penetrate its
  Magic Resistance (its Might); a faerie held by his Summoning counts as
  level 0 for Penetration.
- Dismissing cancels an effect, ends one on a being, or frees a being from
  an agreement; several in a round take 6 off each beyond the first, and
  deflecting a power first needs Quickness + Finesse against its
  Initiative.
- A 1 on the die gives each ticked Trait an experience point, each botch
  die's 0 takes one, beyond the Warping limit; for a negative Trait it is
  reversed, a botch deepening the penalty and a 1 lessening it (p. 103).
  Raising a negative Trait costs 10 xp from -1 to 0, 15 from -2, 20 from
  -3. Losing a point with none banked lowers the Trait a step: the book
  doesn't say, so that is the app's assumption. The roll goes into the
  Diary.

## A Faerie Bargain
<!-- help: faerie-bargain -->

How a bargain made in a summoning ended (RoP: Faerie pp. 132-133).

- A bargain struck gives the fitting Sympathy Trait an experience point,
  none struck takes one away; the bargain binds the faerie whatever he
  does.
- A deadlock may be settled by a contested roll: his Communication +
  Bargain + Faerie Rank, a fitting Trait as Bargain's specialty if he
  chooses, against the faerie's. The book gives no rule for a tie: the
  app's assumption is that a tie strikes no bargain.
- Working out what an unknown faerie wants first: Intelligence + Faerie
  Lore against 12 or more, on a simple die.
- A Sympathy Trait used as a specialty on either roll makes it a stress
  die that may botch, a botch giving Warping Points, and its 1 or its
  botch moves the Trait's experience (pp. 102-103).
- A summoner who breaks a bargain made in a summoning gains a -3 Sympathy
  Trait fitting the faerie, and may lose Faerie Rank; Dismissing can free
  the faerie instead (p. 134). Kept in the Diary.

## An Offer to Faerie
<!-- help: faerie-offer -->

In the Faerie Realm a character with an unspent fable point may bargain
with the Realm itself to change one element of the story (RoP: Faerie
pp. 25-29).

- Fable: the first fable point makes a fable score of 1; raising it costs
  the score + 1 points; a point spent adds the score to one roll. All of
  it is lost on leaving Faerie, so the form takes the score as it stands.
- Offer Total: Communication + Charm, a Profession, a Craft or Music + the
  goods or a Virtue (only the highest: Free Expression +3, a Puissant
  Ability, goods +1 to +3) + the promise (-6 to +3) + the change (+3 to
  -6) + a stress die.
- The Ease Factor is the threat the change overcomes: Trivial 6, Minor 9,
  Serious 12, Major 15, Overwhelming 18. Elysium takes 6 off the roll,
  unless the offer puts its story back on track (Ease Factor 3 less).
- With Art & Academe, artistic Reputation adds 1 a 3 (or part), a Faerie
  Patron's Might 1 a 5 (or part).
- It costs a fable point and a Long-Term Fatigue level whether or not it
  is accepted. Kept in the Diary.

## Invest Time or Money
<!-- help: merchant-investment -->

<!-- tui -->
More (`m`) on [This Season](help:section-char-season) offers **Invest Time
or Money**:
<!-- /tui -->
<!-- gui -->
**Invest Time or Money**, in A Season's Work, under This Season on the Planning chapter, opens a
form for
<!-- /gui -->
what a character does with surplus Labor Points or money (City & Guild
Chapter Seven). Anyone who works for Labor Points can **put money into the
business**: the pounds come from the silver on Personal Gear and buy Labor
Points at the money table read the other way (9 for a quarter of the year's
income, p. 40; Errata p. 56). A trader (the Merchant, Merchant Adventurer,
Factor, Capo, Partner or Redcap Virtue) can also invest (pp. 110-114):

- **Charity**: the Labor Points given are lost; each season's worth given,
  over the years, is an experience point in the Reputation you name. Having
  given at least 1 x the Wealth Multiplier in the past year, he can call a
  crowd of the people it helps: (Communication + Leadership) x that
  Reputation x 1 for an urban merchant, 2 a local carrier, 3 a merchant
  adventurer, 4 a factor, 5 a capo; twice as many with a week's notice. This
  Season shows the crowd.
- **Commodity speculation**: at least 10 Labor Points stored as goods, kept,
  and paying 1 a year for every 10, each Winter from the next year, with a
  guard for each half season's worth invested. **End an investment** takes
  them back, or loses them to the story events that burned the warehouse.
- **Drawings**: a sumptuous item of hand-tool size or smaller for each 1 x
  the Wealth Multiplier.
- **Introduction agent**: two seasons' worth put in, three back in Winter
  two years on; the junior merchant owes him a Favor until then. Spend the
  season introducing them.
- **Marriage broker**: two seasons' worth lost; an experience point in the
  Reputation named, Social Contacts in the couple's class for three years
  (unless he arranges another), and Favors from the couple or their
  parents.
- **Legal action** (p. 114): half a season's worth a suit. Type his
  representative's Intelligence + Civil or Canon Law + die and the
  opponent's; a true suit adds 3, a false one takes 3, an outlandish one 6.
  Winning, add or take 1 from one of the loser's Reputations; losing may
  bring a poor Reputation, and either may bring the Enemy Flaw.
- **Foreseeing a boom** (pp. 111-112), when the troupe's boom comes:
  Intelligence + Area Lore + the die typed. 18 or more gives back two
  seasons' Labor Points for each set aside, 15 to 17 one and a half, 7 to 14
  nothing gained, 6 or less loses 2 of every 10; a botch destroys the
  business.

By kind of merchant, each also open to the richer kinds: a local carrier's
**season smuggling** ((Intelligence + Intrigue) x the Wealth Multiplier, p.
117) or **sponsoring smugglers** (a season's worth each Winter beside his
own work); a factor's **change of government** ((Communication + Intrigue)
x the Wealth Multiplier and a minor political figure's Favor, p. 122) and
**young talent** ((Communication + Leadership) x the Wealth Multiplier and a
Favor for each 10, rounded up, p. 128); a capo's **lavish party** (die + a
Characteristic + the theme's Ability + a point a pound spent, at most his
Intrigue: a Favor for each 5, rounded up, p. 129; the pounds come from his
silver). Investments that are time, not points, take a season: plan it as a
Merchant venture. Each is written in the Diary; an investment costing more
than his Labor Points is refused.

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

## Reward or Punish
<!-- help: grog-discipline -->

Rewards and punishments for one of the covenfolk, as Grogs sets them out
(pp. 23-25). The inspector, **What It Does**, says what the choice will do
before you choose **Give**; the grog's Diary keeps it, and a punishment
also goes in the covenant's Diary.

Rewards, usually set by the turb captain, steward or chamberlain and
announced before the turb:

- **Improved rations**, for a day to a year: a whole year of them is +1 to
  his Living Conditions for that year's aging roll.
- **Pay and a Half**, for a season or more, or for good: half his Wages
  again on the covenant's Wages while it lasts.
- **Improved equipment**: his for good, but surrendered if he is demoted.
  Record the item on his Personal Gear.
- **Promotion in rank** (grog, custos, sergeant, then captain, chamberlain
  or steward): type the rank he holds now.

Punishments, in order of severity:

1. **Castigation**: a single blow with the rod.
2. **Relegation to inferior duties**, done in his free time.
3. **Reduction of rations**: a season or two of the year on them is -1 to
   his Living Conditions for aging, three or four -2. A month counts for
   nothing.
4. **Flogging**: 1, 5 or 10 blows, 1, 2 or 3 Light Wounds and 1, 3 or 5
   Long-Term Fatigue levels.
5. **Reduction in rank**, for good; he surrenders the equipment he was
   given.
6. **Whipping**: 10 lashes a Light Wound, 30 a Medium, 50 a Heavy; the
   short whip two of each. A week to recover (a day for ten lashes or
   fewer); his pay is docked for longer.
7. **Dismissal**: tick **He leaves the covenant** to take him off its
   lists.
8. **Fustuarium**: beaten to death by the blindfolded turb. Few covenants
   have the right to order it.

What it costs in Loyalty (Covenants pp. 38-39): a fitting punishment from
the turb captain, steward or chamberlain costs nothing. One a magus orders
costs Loyalty points by what it counts as: a minor humiliation -1, a
public humiliation -3, restraint -6, infliction of pain -9, a brutal
punishment -12, a brutal one the magus clearly enjoys -15. With a positive
Prevailing Loyalty only an unjust one costs anything. **Counts as** starts
at the usual row for the punishment (a blow minor, the shaming ones
public, reduced rations restraint, a flogging, whipping or fustuarium
brutal). The victim's **Reputation** among the covenfolk adds to the
penalty if he is loved and takes from it if he is disliked. A wound the
magus deals himself costs its own points too (light -3, medium -6, heavy
-9, death -15), one step worse by magic. The points go into the covenant
Diary as a Loyalty Event, which Actions and Events adds up.

**His Loyal changes by** moves his Loyal to Covenant (or Loyal) trait; the
books leave it to the troupe (Grogs p. 24).

Free time, lodging and families (Grogs pp. 23, 25): a grog who doesn't
sleep in his free time loses a Long-Term Fatigue level until he sleeps two
watches straight; punishment duties are done in free time. Married
covenfolk often have a room of their own, and covenants encourage matches
among their covenfolk.

## Pension
<!-- help: grog-pension -->

A grog retires on a pension, or pays rent for his lodging instead and is
fed free (Grogs p. 26). He still counts as one of the covenant for its
finances; his Wages are halved (his pension) or, paying rent, he draws
none. Grogs gives a pension of half to three-quarters of his pay; the
Definitive Edition sets half Wages until death (p. 186), which the app
uses. **Grants pensions** is the covenant's Loyalty Money modifier: +10
Loyalty points for granting pensions to all its retirees.

On a grog who has died, Pension gives his widow the pension he would have
had: one more of the covenant's pensioners, at half Wages a year.

## Covers
<!-- help: section-char-covers -->

A character's other identities (Houses of Hermes: Societates pp. 87-90),
shown for a magus of House Tytalus, a character with the Persona Ability,
or anyone with one recorded. Add, edit or delete one:

- **A deep cover**: a name and role built in a community, with a
  Reputation there that rises as an Ability does. It starts at 1 with a
  noteworthy act before witnesses; each season it is kept up, Advance adds
  2 xp for living there or 1 for regular visits (a brief visit each season
  is 2 a year: choose away and add them by hand), and each staged event or
  tie to the community 1 more. More than 2 a season arouses suspicion.
  Questioned, its Disguise roll's Ease Factor falls by the Reputation, and
  with those it sees regularly The Gift's penalty falls by as much. A role
  needing a Minor Social Status Virtue costs a Minor Story Flaw's
  obligations, a Major one a Major Story Flaw's and doesn't last; one
  needing other Virtues can't be built. Unused, it keeps its Reputation
  as many years as its score, then loses a point a year.
- **A persona**: a whole different person of the Persona Ability, one for
  each point of it; changing into one is a round's concentration and
  Stamina + Persona against 9. Each persona has a Reputation of 1 when it
  is made, and every xp put into Persona after that goes to every
  persona's Reputation too (p. 90).

**Disguise Roll** (More, beside Covers) rolls a deep cover's Disguise:
the Characteristic you choose (Communication by default, as for a lie)
+ Guile + a stress die, against the questioner's Perception + Awareness
+ a stress die (DE p. 165). When the cover is being defended (questioned
by a suspicious priest, covering a comrade's slip) the cover's
Reputation comes off their total; untick **Convincing someone of it**
for the roll that first establishes it (HoH:S p. 88). The result is
shown, not kept.

## Disguise Roll
<!-- help: disguise-roll -->

A deep cover's two rolls (Houses of Hermes: Societates pp. 87-88). **The
Disguise roll** is Intelligence + Guile + stress die against an Ease Factor
of 9 + the modifiers that apply (a change of social status +3, a minor
alteration in appearance +1, a major one +3, a change of sex +6, minimal
preparation +3, none +6), less the cover's Reputation while it is defended
rather than established. **Talking with someone** in disguise is Presence +
Guile + stress die against their Intelligence + Folk Ken + stress die; it is
a social roll, so The Gift's penalty counts. Leave a die blank to roll it.
Nothing is changed: the form shows whether the cover holds.

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
- **Surgery** (Recovery Roll, surgery) can return a disease to the stage
  it began at, with +3 to its next Recovery roll, at the cost of a wound
  (Art & Academe p. 61).
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
- **Sap the Life** is in the disease list: a vampire's power (Against the
  Dark p. 115) that inflicts a Serious disease of Severity 15, rolled
  weekly against 12 and 18, with no Disease Avoidance roll (its
  Penetration decides) and two long-term Fatigue levels that come back
  only when it abates. Faerie Lore may treat it as Medicine does: the
  app's Prognosis counts only Medicine.
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
**Divination** (Supernatural): given at 1 by Divination & Augury or Hermetic Dream Interpreter; a magus with either may buy it at creation (The Mysteries Revised Edition pp. 59, 62).

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

The details of **Guile** give the Disguise roll: Intelligence + Guile +
stress die against 9, +3 for a change of social status, +1 or +3 for a minor
or major change of appearance, +6 for a change of sex, +3 or +6 for minimal
or no preparation; then Presence + Guile against the other's Intelligence +
Folk Ken to talk with someone (Houses of Hermes: Societates p. 87). The
details of **Persona** count its identities (one a point) and give the roll
to take one or return (Stamina + Persona against 9), each persona's
Reputation (from 1, gaining the xp put into Persona), and how the change
shows to magic: a Muto Corpus 10 effect, a magnitude less each sunrise or
sunset, level 5 x Persona to other magic (DE p. 169; Societates pp. 89-90).

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

<!-- tui -->
On one who holds a Goetic Art, More (`m`) offers [Ars Goetia](help:ars-goetia)
from his record or his tradition's chapter.
<!-- /tui -->
<!-- gui -->
**Ars Goetia**, in the [Deeds chapter](help:tab-deeds) under The Infernal, works out a
Goetic Art's total for one who holds one.
<!-- /gui -->

<!-- tui -->
On a magus with a Mystery of spirit magic or theurgy, More (`m`) offers
[Spirits and Names](help:spirits-and-names) from his record or Known Spells.
<!-- /tui -->
<!-- gui -->
**Spirits and Names**, in **Magic Outside the Lab**, under Raw Vis on the Hermetic Magic chapter, works out the
figures of a Mystery of spirit magic or theurgy.
<!-- /gui -->

<!-- tui -->
With Apprentices in play, on a Gifted character More (`m`) offers
[Turbulence](help:turbulence); on an apprentice, also
[The Gauntlet](help:gauntlet) and [Lose the Gift](help:lose-the-gift).
<!-- /tui -->
<!-- gui -->
With Apprentices in play, **Turbulence** is in the [Deeds chapter](help:tab-deeds) under
Apprenticeship (and in A Season's Work on the Planning chapter) for a
Gifted character,
and **The Gauntlet** and **Lose the Gift** beside it for an apprentice.
<!-- /gui -->


**See also:** [Virtues & Flaws tab](help:tab-vf),
[Planning tab](help:tab-planning), [How the app handles advancement](help:guide-advancement)

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


## Cast a Power
<!-- help: hedge-cast -->

More beside a hedge wizard's Abilities: one casting rolled by the
tradition's own rule, as its [chapter](help:tradition-chapter) lists it.
Choose the **Way of casting** and the **Arts or Ability used**, type the
effect's **Level or Ease Factor**, the **Aura** where it is cast (the
covenant's, to start with) and any **Pawns of vis**, and choose Cast. The
app works out the Casting Score, rolls the rule's die (or uses one typed
in **Die**), divides as the rule says and says whether it works; a rule
that may fall short at a Fatigue level says so. A botch's zeroes give a
Warping Point each (DE pp. 227, 389; Hedge Magic RE pp. 37, 96), which can bring on the character's answer
to Warping as any other event does. The casting goes in the Diary.

## Conjure a Spirit
<!-- help: galdor-conjure -->

More beside a galdraman's Abilities: a song calls a spirit to work one
effect (*Land of Fire & Ice* pp. 46-48). Choose the **Song Talent**, type
the **Effect level**, which the Hermetic guidelines set and the storyguide
has the last word on, and the **Duration**, Momentary or Concentration. The
level's magnitude can't be more than the Song. Tick **A ritual effect**
where a magus would need a ritual: the song takes 15 minutes a magnitude in
place of one, and the spirit takes a pawn of vis a magnitude. Tick
**Touching the ground** if he isn't on a platform, a chair or a table: it
halves the total.

The total is Com + Music + Galdor Wisdom + the Song + the aura + a stress
die, and it must be greater than the level. Landvaettir count as Faerie
in every aura but a Magic one, so a Dominion hurts as a faerie would feel
it. The spirit's Might is the total, and Penetration is reckoned as the
Definitive Edition does. With **Hours he holds the song**, the app rolls
Sta + Music for each hour, against 6 + the hours: up to 3 short costs a
Fatigue level, and worse ends the song. A total of twice the level leaves a
Concentration effect working on for a die of hours. No vis boosts a song.
It goes in the Diary, and a botch's zeroes give Warping Points.

## Bargain with a Lord
<!-- help: galdor-bargain -->

More beside a galdraman's Abilities. Anything longer than Concentration
comes from a lord of the landvaettir, in the wilds, and he has to agree
(*Land of Fire & Ice* p. 48). Write **The lord** and **The service**, the
**Vis a year** it tithes if it lasts over a year, and any **Favour owed**.
The book's price is about double the magnitude, reckoned at Sun Duration,
and a skilled galdraman asks less.

Usually the lord agrees or refuses in play: say which. A deal he agrees to
goes in the Galdor chapter's Bound Beings, where you can change it. To
leave it to the dice, choose **Roll the Bargain**, *Houses of Hermes:
Societates* p. 136: Com + Bargain + a stress die, against 18 with its
modifiers for the terms, how long the service lasts, any duty he takes on,
and the vis offered, +2 a pawn under the standard and -2 over. He summoned
nothing, so no Summoning Strength adds. Failure is no deal. A botch gives
him Supernatural Nuisance from a weak lord and Plagued by Supernatural
Entity from a stronger one, for at least a month.

A missed tithe or service breaks a deal and may bring reprisals.

## Bind an Item
<!-- help: galdor-bind -->

More beside a galdraman's Abilities, once a deal with a lord is on his
sheet (*Land of Fire & Ice* p. 49). He needs no laboratory, only the tools
to make the item, and the spirit is bound as he makes it. **For his
lifetime** the total must reach double the level plus the Effect Frequency
Table's levels, and the Duration is Momentary or Concentration; Constant
Use adds 5 to a Concentration effect's level. **A single service** needs
only the level, and lasts a year and a day.

The total is Com + Music + Galdor Wisdom + the Song + the item's bonuses +
the aura + a stress die, with Galdor Wisdom and the Song each no higher
than the **Craft used**. Craft: Runes, the book's Scribe Runes, may stand as
the Craft and inscribes a ready-made item, but adds nothing. The Song must
be at least the magnitude. The spirit takes about the vis a magus would
spend, first. The item goes on the chapter's Effects and Items.

## A tradition's chapter
<!-- help: tradition-chapter -->

A character who belongs to a non-Hermetic tradition, such as the folk
witches or the vitkir, has a chapter named after the tradition's magic
(Folk Witch Magic, Rune Magic...), as a magus has Hermetic Magic. It lists
the tradition's Arts and Abilities the character has, grouped by the part
they play: Techniques, Forms, Runes, then the tradition's other Abilities.
These leave the Abilities chapter while the character belongs to the
tradition.

A sahir's Sihr is usually of the Magic realm, and versions of the other
realms exist (The Cradle and the Crescent, p. 47). One with the Sihr
Ability chooses its realm on the **Traditions** form. Their summoning then
reads the aura by that realm, for the total and the botch dice, and the
Summoning rule says what that version changes in the bargain. The
Solomonic arts stay Magic: the book aligns only Sihr.

A sahir may have another summoning art in place of Sihr: (Faerie) Summoning,
as most yatus do, the Goetic Summoning or Elementalist Summoning. The
Summoning rule lists each one they have, read by that art's realm. With
**Yatu Magic**, all their magic counts as Magic or Faerie, whichever suits
the aura best, for its total and its botch dice, and an aligned Sihr may
use its own realm too; they gain no Warping from living in Magic or Faerie
auras (The Cradle and the Crescent, pp. 30-31).

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

Ticking a tradition the character didn't belong to joins it: the Virtues
and Social Status its members need are added, and a note says what was
added. Leaving a tradition takes nothing away. Joining doesn't Open a
Gifted member's Gift: a Gifted master of the tradition does that, usually
at the start of an apprenticeship (Hedge Magic Revised p. 7). Plan **Open a
student's Gift to a tradition** for the master: it brings the Opening's
Arts and Abilities at 0 and its free Virtues.

A magus may belong to a tradition too. A Hermetic society, such as Sol
Invictus or the Priory of Saint Nerius, is open to any magus; a tradition
of House Ex Miscellanea, such as the Tempestaria or the Rustic Magi, to the
House's magi, whose free House Virtues are then the tradition's own: its
Major non-Hermetic Virtue, its Minor Hermetic Virtue and its Major
Hermetic Flaw (Houses of Hermes: Societates, Chapter 5: House Ex
Miscellanea). Its chapter shows beside Hermetic Magic.

**Nemthengacha** (DE p. 244): Celtic and Scandinavian magi Ex Miscellanea
whose Embitterment (Communication + Embitterment + stress die against 6 to
18 by how close the victim and his friend are, +3 for hatred, +6 for
murderous loathing) turns a listener against a friend, kinsman or lord.
Their package: Embitterment, Subtle Magic, and Deficient Technique in Rego
(DE pp. 244-245).

Leaving a tradition keeps its Arts and Abilities: they move back to the
Abilities chapter. **The app works out:** each score from its XP, on the
Art table or the Ability table as the tradition's book says (see the
[Abilities tab](help:tab-abilities)), the [Casting](help:tradition-casting)
totals, the [Magical Defenses](help:tradition-defenses), the character's
[Effects and Items](help:tradition-effects), their
[Bound Beings](help:tradition-bonds), the tradition's
[Warping](help:tradition-warping) and [Pools](help:tradition-pools), and
its [Seasons](help:tradition-seasons).

The Goetic traditions (Witch-Hammers, Dread Host, Mulhidun, Witches of
Thessaly, Ba'al Ov) list their Arts' effects as General guidelines: the
summoning, scouring, ablating, binding and commanding targets, the uses
of Ablation Points and the common commands (RoP: The Infernal pp. 114-118).
An effect built on one keeps the level you type.

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
casts up to 10 short. A power whose magnitude is its Ability (a folk
witch's) needs no die for a level, but cast against an Ease Factor it
shows the die that Ease Factor needs and the level the power counts as
(5 x the Ability; Hedge Magic RE p. 36). A stressed casting shows its
botch dice. An item made by a Lab Total shows that Lab Total.

**Built from a guideline:** when the tradition has a guideline table
(see [Casting](help:tradition-casting)), choose the effect's **Guideline**
and its **Range**, **Duration** and **Target**, and any **Further
magnitudes** (size, complexity, hatred for an Embitterment): the level is
worked out for you instead of typed, as a Hermetic spell's is. Each
magnitude adds 5 levels (1 below level 5), or 3 for the traditions whose
levels or Ease Factors step by 3 (Soqotran spells, Rival Magic p. 124;
Augustan rites, p. 57; a Muspelli utiseta, p. 90; an Embitterment, Tales
of Mythic Europe p. 35). The Ranges, Durations and Targets offered are the
tradition's own (a gruagach's Conversation, Geas and Limit, HMRE pp. 60-63;
an Amazon's Sister, Cousin, Exchange and Hour, Rival Magic p. 23; a learned
magician's charms and amulets each their own, HMRE pp. 85-86), or the
Hermetic ones for a tradition that lists none. Some cost by the Art used:
a gruagach's Conversation is free for Blessing and Curse but a magnitude
for Shape and Vision; an Amazon Consonant has a base Range and Duration,
each step from it either way a magnitude (Rival Magic pp. 23-25); a
utiseta counts only the steps from its Ability's own base (Rival Magic
p. 95). A vitki's rune, a Columban ward or a folk witch's curse is its
guideline's level as printed. A General guideline, or no guideline, keeps
the level you type. The Hyperborean hymns' guidelines are General: a
Power uses the Hermetic guidelines within its hymn's principles. Each
hymn's principles, the book's sample Powers with their level costs and
Ease Factors (as corrected by the errata), and Numina of Apollo, a Vim
Power any hymn can hold (Magic Resistance of the level - 5 against its
principles; Ancient Magic p. 110) are listed to choose from. The level you
type is the Power's level cost, with its uses a day and Penetration added
as for an enchanted device (DE pp. 256-258; Ancient Magic pp. 107-118).

**Not yet:** a season of work making the item or inventing the effect
for you (add it here when the season is done), and the catalogs of each
book's printed spells and charms.

**Faerie rites** (the ollamhain, the volkhvy and the wise folk). A rite is built on one of the
tradition's Faerie Powers' guidelines (Beguile, Dream and Portage for the ollamhain; Conjure
and Grant for the volkhvy; Ware, Weal and Woe for the wise folk) with any Method, and may take
the Hermetic Ranges, Durations and Targets, House Merinita's Faerie Magic ones (Road, Fire,
Until (Condition), Year + 1, Bloodline; DE pp. 237-238; not Bargain, which Realms of Power:
Faerie doesn't give rites) and the Faerie ones: Crossroads,
Presence (as far as the caster's Presence reaches: 100 paces at +4, 50 at +2, 15 at -1 to +1,
5 at -3, himself alone at -4), Prop, Symbol; Held, Focus, While (Condition), Geas (Condition),
Hour + 1, Midday/Midnight, Not (Condition), Season, Aura, Faerie, Hidden, If (Condition),
Symbol; Medium, Passion, Symbol (Realms of Power: Faerie pp. 122-123). Geas and If add the
triggered effect's Duration: type its magnitudes as further magnitudes (a Geas is Sun plus the
trigger's Duration; If is the trigger's Duration plus four, and a ritual). Each rite's row says
the Sympathy points it needs (a fifth of its level: a rite reaches at most 5 x the Sympathy
Traits that apply to its target, negatives counted by their size, and a Conjure change counts
the Traits of both states; pp. 121, 125). The book's limit is firm, but the app can't tell
which Traits apply, so it only warns when the rite needs more than all the character's
Sympathy Traits together, temporary ones included; the 3 points each Symbol needs; the parameters that make it a
ritual (fifteen minutes a magnitude, no vis); and what its Method asks: Evocation a Warping or
Confidence Point and vis at +2 a pawn up to Evocation + the Power, Enchantment a performance
against 3 x the magnitude first, Empathy a Fatigue level and an hour's trance, each further
Fatigue level adding the limit again (pp. 121-124; Errata p. 68).

**Holy Powers and maleficia.** A holy tradition's effects (the Ascetics, Cantores, Sufis and
the rest) are built on the holy Powers' guidelines (Realms of Power: The Divine pp. 48-56), an
infernal tradition's on the maleficia's (Realms of Power: The Infernal pp. 105-112), for the
Powers among the tradition's favored Abilities. Each guideline names the Method it is for:
"Strike dead (Purity)". The Ranges, Durations and Targets are the Hermetic ones. For a holy
effect, Year and Boundary cost 4 magnitudes more, as anything a Hermetic ritual would need does
(type other ritual cases, such as an Arcane Connection summons, as 4 further magnitudes); a holy
connection stands in for an Arcane Connection (p. 48). A maleficium may also take Crossroads (as
Voice), Cursed (Condition) (as Sun, with the triggered effect's Duration typed as further
magnitudes), Forsaken (as Year; repentance ends it, and it can't be dispelled) and Passion (as
Group) (p. 103). An effect's row warns when its Power doesn't work with its Method (Adjuration and
Cursing take Invocation or Purity, Blessing Invocation or Meditation, Intervention and
Transcendence Meditation or Purity, Understanding Meditation alone, Wonders Invocation alone),
or its guideline is for the other Method. A holy effect's row says that falling short is a
tragedy of hubris (Minor 1-10 short, Major 11-20, Ultimate 21 or more), with True Faith x 10
standing in for the total (p. 46). A maleficium's says its Method's cost (Debauchery: a long-term
Fatigue level or a Light Wound; Incantation: a Confidence Point or a Warping Point for a fitting
sin, and vis +2 a pawn up to Incantation + the Power), and that each 10 levels short is a botch and
a Warping Point (Vituperation at 2), with Hierarchy x 10 standing in for the total; a true botch
owes Hell a soul within a season (pp. 102-104).

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

**Botch dice:** a stressed casting botches as a Hermetic magus's does
(Definitive Edition p. 227): one die, one more a pawn of vis, and one a
point of another realm's aura (twice that in a regio); a Divine power
takes none for the aura. The books give this for the gruagachan, the
learned magicians and the vitkir (HMRE pp. 71, 85, 126) and the rival
traditions (Rival Magic pp. 25, 65, 115). An Amazon rite rolls its
magnitude + the aura (Rival Magic p. 25). A tradition's own extras are
noted under its rule: Wildfire's two (Rival Magic p. 104), a vitki's
Mastered Rune taking three off (HMRE p. 121), the learned magicians' dice
for each realm entreated and for a weak Language (HMRE pp. 85, 88), a
sahir's extra summoning time (The Cradle and the Crescent p. 46). A Lab
Total, a simple die or a rule with no die rolls none.

**Guidelines:** a tradition with a guideline table lists how many it has
and from which pages: the gruagachan (HMRE pp. 66-70), the learned
magicians and the imhergi who cast with their Arts (pp. 89-94), the
vitkir's runes (pp. 128-139) and the Saxon runes (Thrice-Told Tales
pp. 139-143), the folk witches' Ease Factors (pp. 37-42),
the Amazons (Rival Magic pp. 32-43), the Augustan schools and the Sortes
Virgilianae (pp. 53-60), the Muspelli's Abilities and their utiseta bases
(pp. 95-105), the Soqotran incenses (pp. 127-132), the five Solomonic arts
(The Cradle and the Crescent pp. 48-58), the Columbae's wards and the other
Ex Miscellanea Ease Factor tables (Houses of Hermes: Societates
pp. 105-128), a hunter's Scry (Against the Dark p. 134) and the
Nemthengacha's Embitterment (Tales of Mythic Europe p. 35) the
clesrada's feats (The Contested Isle pp. 102-105), the Debterah's Holy
Methods and amulets (Lands of the Nile p. 114, with Realms of Power: The
Divine) and Corpse Magic for the Cult of Dedun (Lands of the Nile p. 102:
Communication + Corpse Magic + aura + stress die against 9 to speak with a
corpse, 12 to compel the truth or protect it, 15 to animate it and 18 to
command it out of sight; its Penetration must beat the corpse's Might,
usually 9, to raise it from the grave). Choose one on
an effect in [Effects and Items](help:tradition-effects) and its level is
worked out.

**Hunters:** any Foe Art pairs with any Practice Art (Against the Dark
p. 132): the grid shows every Foe Art the character holds, the ones
listed or another the troupe names.

**Folk witches:** a flying witch adds her Flight score to Attack and
Defense against a foe who can't fly, and Life-Linked Folk Witch Magic
adds 5 a Fatigue level spent (HMRE pp. 35, 38). A potion casts at its
Brew Potency + a stress die, with no aura and no Penetration bonus, and
must penetrate the drinker; one that grants a power gives it at Brew
Potency / 5, rounded up, for Brew Potency days (p. 40-41).

**Nightwalkers:** spirit travel is Stamina + Athletics against 3 (places
seen daily) to 15 (never visited), +3 for each object carried; leading a
willing spirit along is Stamina + Leadership against 3 more; changing
form in combat is Stamina + Concentration against 15; seeking a foe in
battle Perception + Awareness against 9; intimidating a ghost Presence +
Leadership against 6 + its Brave; questioning one Presence + Charm
against 3, 6 or 9 by the answer's length (HMRE pp. 107-111). Straying
costs a Long-Term Fatigue level for any time up to an hour, however
short, two for a whole night, and one more for talking with people at
its end (HMRE pp. 106, 108).

**The clesrada:** each feat of arms is a power on the Feat roll of its
Characteristic, its guideline giving its Ease Factor: Characteristic +
its Ability + a stress die, + the aura's modifier for a Faerie power; a
botch always costs a Fatigue level. A feat counts as a 15th-level spell
with Penetration 0 + the Penetration bonus against magic that affects
spells, but acts on its user and need not penetrate a foe; feats of one
Ability chain into one action until one fails (The Contested Isle
pp. 101-105).

**Saxon runes:** Ac, Æsc, Yr, Ear, Gar, Calc, Cweorth, Stan and Ior are
vitkar runes with their own guidelines (Thrice-Told Tales pp. 139-143);
only Damhan-Allaidh knows them, by a minor Initiation for a vitki who
knows all 24 Elder runes. Ac has no printed guidelines.

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
Initiation with the Script's bonus. A hedge Initiation is planned as an
**Undergo an Initiation** season with the **Hedge Script** chosen; see
[How to initiate a character into a Mystery](help:guide-initiation).

The **Opening Ease Factor** is twice the student's Supernatural Ability
and Art scores, his Hermetic Arts with experience among them, + 12 if his
Gift was Opened before, by another tradition or as a magus (any Hermetic
Art with experience, or a magus; HMRE p. 8). At a folk witches' sabbat,
helping Gifted witches add +1 each to the Opening Total, but no more of
them than the Magic aura at the sabbat's site, so another realm's aura
lets none help (HMRE pp. 45-46): enter them as **Sabbat helpers** on the
Open a Student's Gift season, with the **Sabbat aura (Magic)** where it
is held. For a sabbat Initiation, add the helpers to the
**Script bonus** yourself, with the same cap (p. 46).

**A folk witch's kitchen:** a brew's Brew Potency is its power's Lab
Total (the power twice with Expert Potion Brewer), + 1 for each sister
helping at a sabbat, up to the Magic aura there; it makes Folk Witch
Magic Theory doses (+ a Lab Text's level), a pawn each + the effect's
own vis, and a season may use twice her Folk Witch Magic Theory in vis
(four times with Concentrated Potions). Extracting vis gives a tenth of
her Lab Total with no power in it, rounded up, in Vim; fixing an Arcane
Connection makes it last that Lab Total in its next unit up, along
hours, days, weeks, months, years and decades (one lasting decades
can't step further; indefinite connections are the laboratory's) (HMRE
pp. 35, 39-41, 45; DE p. 219). The brewing season's notes say what it makes.

An elementalist's
**Refining** season shows what its Refining Total makes (HMRE pp. 26-27):
a longevity potion of Total / 5 for age / 5 pawns, and by his Refining
types a Characteristic potion (Total / 5, to at most half the Form), vis
from an aura (Total / 10) or vis moved (Total / 5 pawns), or a being's
Might restored or drained by the Total less its Might. The divisions
round down, as the book's do when it says nothing (DE p. 6); only the
potion's vis, age / 5, rounds up.

A Hyperborean hymnist's **Infuse a Power** season shows how many Power
levels his recitation total reaches. The total is Communication + the
Hymn + Dead Language: Hyperborean + the aura, and Hyperborean Descent's
+2 or +4 is added in the note. The Ease Factor is the levels / 3, rounded
up, so a total reaches three times its value in levels (Ancient Magic
pp. 106-108). The note also lists each hymn's levels: 15 for each point
of its score (Puissant doesn't count), those already infused, and those
left. Devotion before the season (+3 a season, at most +9), days without
reciting (-1 a day, at most -20) and Personality Flaws Apollo favours or
dislikes (+1/+3, -1/-3) are yours to add (p. 107). An **Enchant a relic**
season uses Intelligence in place of Communication, with no devotional
bonus. Its note gives the most levels one Power can have, and the Warping
it costs: 2 Warping Points for every pawn of vis Hermetic enchanting
would need, plus 2 a pawn of the item's opening the first time
(pp. 116-117).

A hedge Script may need scores of the Initiate: every Ikhwan as-Safa'
Script fails without Artes Liberales, Philosophiae and Theology (Islam)
4 and Arabic 5, the Tulab Ibn Sina's without Medicine and Chirurgy 3, 4
or 5 by Script (HMRE pp. 30-31), and a learned magician's master tests
an Ability at 2 (pp. 88-89); the season says when the Initiate falls
short. A gruagach initiating himself uses his own scores and the harder
Ease Factor, 18 or 30 (p. 61).

The **lector priests** have a season to make a transitory item or
statue: a temporary amulet, a seal or a potion poured over a cippus
statue, each holding one Until effect for one use, or a faerie persuaded
into a statue (Lands of the Nile pp. 51-54). The book gives no total for
them; a new statue's consecration is Com + Folk Ken + a die against 18
(p. 53).

**Franciscans** (The Church pp. 137-139) are a Holy Tradition in the
traditions list, open only to a friar or a Poor Sister (Monastic Vows is
required). Their four Scripts, each needing a Mystagogue who knows the
Virtue (Target 21): Meditation (+15, Driven), Understanding (+7, Visions),
Intervention (+9) and Purity (+9, Fragile Constitution). The book prints
each Script's total after Meditation's Major Ordeal (Understanding's
Target 12, Intervention's 15, Purity's 18); the app takes those
past-Ordeal reductions off by itself.

**Hermetic Mystery Cults** are in the traditions list as societates any
magus may join: the Cult of Mercury (Faith & Flame p. 28: the
Consecration of Priamitus, Target 21, +18, gives Mercurian Magic and the
Pagan Story Flaw), the Legion of Mithras (The Mysteries Revised Edition
p. 121: the Raven's Strong-Willed Script, Target 15, +5), the Knights of
the Green Stone (p. 132: the Page's Free Expression Script, Target 15, +7,
Dutybound) and the Matres et Matrones (Faith & Flame p. 30: no printed
Scripts; their three levels and what each needs are in the cult's notes).
Add a member with Traditions, then plan Undergo an Initiation with the
cult's Script chosen in Hedge Script. Each cult's Lore is "Mystery Cult
Lore: (cult)" (the Matres' is "Organization Lore: Matres and Matrones",
as the book names it). The Green Stone's Page Script says its own Ordeal
lowers that Initiation's Target to 12; the Definitive Edition lowers only
the next three Initiations (DE p. 388), so the app keeps it at 15.

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
[Aging](help:section-aging) section).

**The Witch Moon:** each month Stamina - Warping Score + a stress die
against 6 ends it; more months than her Warping Score make it a bad
experience (2 xp lost a Warping Point gained), otherwise a good one (5 xp
a month). Harsh Moon makes the fever a Heavy Wound, Painless Moon none
(HMRE pp. 35, 42-43). A magus, and every member of an Ex
Miscellanea tradition, is a Hermetic magus: Warping and Twilight as for
any magus.

**The app works out:** an elementalist's Personality Traits, one for each
Elementalist Form he holds: the Warping Score + the Form / 5 (rounded up).
From +3 a Trait acts as a Minor Personality Flaw, from +6 a Major one, and
at +10 the storyguide takes over.

An infernalist's **Vituperation** is worked out on his tradition's
Warping: on 2 or more Warping Points at once, Stamina + Concentration +
Confidence against Warping Score + the points + Hierarchy + the aura; his
Hierarchy is his highest Infernal Reputation. Sacrifice adds +2 (an
effigy) to +10 (an innocent) to an effect, and profaning a holy thing
makes a pawn of Infernal vis for a Confidence Point (Realms of Power: The
Infernal pp. 94-96).

Two or more Warping Points at once now roll the tradition's answer
straight away, as Twilight is rolled for a magus, and write it in the
Diary. **Divine Ascent**, for a holy tradition's member or anyone with a
holy Method or Power: Presence + Concentration (or Meditation) + stress
die against Warping Score + the points + True Faith + the aura + stress
die (only his own die can botch); failing, he gains the margin in
Warping Points more and ascends for Warping Score + every point gained -
True Faith days (at least 1; months from Warping Score 6), and the Diary
gives what each of the three forms (Gloom, Form, Unity) brings (Realms
of Power: The Divine pp. 63-65). **Vituperation**, for an infernalist:
failing, he is torn away as long as Twilight's table gives his Warping
Score, and the app writes the Aging roll he must make, adding his
Warping Score. He gains a Confidence Point a Warping Point at once,
unless he botched the avoidance roll. Once the ordeal is over his
Confidence Score rises by 1 if it is below his Warping Score or his
Decrepitude: the Diary says so outright when it is already below his
Warping Score, and otherwise that it depends on the Aging roll's
Decrepitude, for you to change on the Character Info form (Realms of
Power: The Infernal p. 95). **Faerie Calling**, for a
Faerie tradition's member: the Ease Factor to act while dazed, and the
roll that resolves it (a stress die that can botch), with the Faerie
Rank from which it is a good Calling (the app keeps no Faerie Rank;
Realms of Power: Faerie p. 120). **Enter Twilight willingly** skips the
roll for an Ascent or a Vituperation too.

A Hermetic magus goes into Twilight, True Faith or not, unless something
takes its place: the False Gift, or an infernal tradition, brings
Vituperation (Realms of Power: The Infernal p. 124); a homunculus wizard
has a Faerie Calling (Realms of Power: Faerie p. 118); and a magus who
also has Miraculous Abilities has only one form of Warping for life,
chosen by the troupe: tick **Seeks Divine Ascent instead of Twilight**
on his Aging & Warping form for the Ascent (Realms of Power: The Divine
p. 63). The Divine and Infernal answers come before Faerie's.

A Gifted Hyperborean hymnist whose first tradition is the hymns has
**Illumination** in place of Twilight (Ancient Magic pp. 105-106). The
section gives his Apollonian Personality Trait (his Warping Score), his
control total (Stamina + Concentration + his highest Hymn), and the Ease
Factor's modifiers: -2 or -4 for Hyperborean Descent, and +1 for every
30 levels of Powers he has infused. It also shows the Bright Lightening,
failing the roll on purpose: as many more Warping Points, and xp in
hymns, as his Warping Score after the points just gained + the aura +
the modifiers, with the number for three points gained (Ancient Magic p.
106). The +1 a 30 levels counts the Powers of all his hymns together,
not those in relics. An unGifted hymnist, or a magus, Warps as usual.

Gain Warping Points rolls the response when 2 or more points come at once, as described above.

## A tradition's Pools
<!-- help: tradition-pools -->

The points the character keeps in each of the tradition's pools, for a
tradition whose members store power (its book says what fills the pool,
what spends it and its cap, shown here). A tradition with no pools has no
such section.

A Hyperborean hymnist's **Power levels** pool lists each hymn he holds:
the levels its score holds (15 a point), the levels his infused Powers
(his effects on the Infuse a Power rule) already use, and the levels
left. The points you type are kept apart from these, for the extra
levels bought with vis (a level a pawn; Ancient Magic p. 109).

<!-- tui -->
**You type:** `e` sets the points in each pool.
<!-- /tui -->
<!-- gui -->
**You type:** **Edit** sets the points in each pool.
<!-- /gui -->

**Not yet:** filling or spending a pool for you: set the points by hand.

## Ars Notoria
<!-- help: learned-magic -->


Ars Notoria (Realms of Power: The Divine pp. 97-100). Only a Gifted
Christian may learn it, and only from the Book of Solomon: a season's
search is Intelligence + Divine Lore + a stress die against 21. Reading
it needs 4 in Latin, Greek, Hebrew and Chaldean, and Artes Liberales 4.
It is a tractatus of Quality 20, learned as a first Supernatural
Ability (a season giving under 5 xp is wasted).

Reciting a Ring: Intelligence + Ars Notoria + the season's modifiers
(fasting +1 a season, chastity +1, Personality Flaws +/-1 or 3, a venial
sin -3, a mortal sin -9, minus each non-Divine Supernatural Ability,
plus True Faith) + a stress die, against 6 + 3 x the Ring's level + 1 a
season it is to last (3 + ... once the Ring is known). The first
recitation takes a season; later ones 10 days less Ars Notoria, at
least one. Rings are learned in order and don't stack.

I Philosophiae +100 xp, Communication +3 (to +5), Spring or Autumn.
II Theology +100 xp, Intelligence +3 (to +5), Winter. III Medicine +100
xp and Greater Purifying Touch. IV the Patron Angel, a teacher. V sense a
being's realm: Perception + Ars Notoria + stress die against 6 + its
Magic Resistance / 5, no Penetration (Errata p. 49), Summer. VI
divination, Spring. VII no botches. The xp go when the Ring ends.

Each point of Ars Notoria takes 3 off a Divine aura's penalty to
casting your other magic (shown on the Casting Score's aura line as "Ars
Notoria"); Lab Totals and Penetration take the whole penalty. While a
Ring is in effect a Divine aura gives no Warping (p. 100).


## Jewish Mysticism
<!-- help: jewish-mysticism -->


Shinnui Shem (RoP:D p. 141): once a life, a season's renaming severs
every Arcane Connection and gives (simple die + Intelligence + Gematria
+ Understanding + book Quality + Dominion aura) / 5 to Aging Rolls until
the next Aging Point. A golem (pp. 142-143): a season shaping the clay,
then seasons of Intelligence + Kabbalah + Wonders + Ceremony bonus +
Dominion aura against 30, banking the excess; its Divine Might is the
points + a stress die, at most 5 x the leader's Kabbalah. Its powers
bank the same way against their level, up to its Might in magnitudes.
Merkavah (p. 144): Stamina + Merkavah + Adjuration + Ceremony + aura
against the being's Might, banking until the points exceed it: its True
Name, +5 Penetration.


## Solomonic Integration
<!-- help: solomonic-integration -->


The Cradle and the Crescent pp. 44-45. Magi may research Hermetic True
Names (Minor: a spell with a built-in Arcane Connection), Scientates
Suleimanis and Hermetic Realm Initiation (Hermetic Breakthroughs giving
Major Hermetic Virtues); they are on the breakthrough goal list. Sahirs
may reach Solomonic Devices, Spontaneous Solomonic Spells (total / 2 with
a Fatigue level, / 5 without the die) and Independent Solomonic Magic
(no spirit, no Summoning Strength, own Penetration).


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
<!-- tui -->
**Gain or Lose in Play** (in More) records a Virtue or Flaw that comes or
goes during the saga, with how, in the Diary ([help](help:vf-change)).
<!-- /tui -->
<!-- gui -->
**Gain or Lose in Play**, on the During the Saga strip under the Virtues
and Flaws, records a Virtue or Flaw that comes or goes during the saga, with
how, in the Diary ([help](help:vf-change)).
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

The catalog lists a supplement's Virtues and Flaws only while its book is
in play (Saga Content's Books in Play). Where a supplement prints a Virtue
or Flaw the Definitive Edition also prints, such as Art & Academe's Failed
Student or The Church's Brother-Priest (the DE's Brother Chaplain), the
catalog has the Definitive Edition's alone, with its name, tier and text,
and it is there whichever books are in play.

A character with a Might score from a Virtue (Demonic Blood) takes no
Virtue of another realm: not The Gift, True Faith, Faerie Blood or the
Blood of the Nephilim (Realms of Power: The Infernal p. 84), nor a
Supernatural Virtue of another realm. One whose description names no realm
is Magic (DE p. 64); Hex is taken as Infernal, the realm the book says it
is most often tied to (DE p. 85). The Ríastradh
needs the Fury or the Major Wrathful Flaw (The Contested Isle p. 120).

A Faerie Blood's details say what its variety gives, the stronger Legacy
benefit with Faerie Legacy, and its Sympathies: bloodcap, brownie, dwarf,
ettin, faerie god, ghul, goblin, huldra, nymph, padfoot, satyr, selkie,
sidhe and undine (Realms of Power: Faerie pp. 106-110), and the jinni
bloods 'afrit, ghula and jann (The Cradle and the Crescent pp. 77-78). A
Lesser or Greater Charm's details give the charm rules (Realms of Power:
Faerie p. 104); the Ríastradh's and the Lúan láith's say how they work in
play (The Contested Isle pp. 120-121).

A Faerie God's blood may name its Olympian: choose "Faerie God: Zeus" (or Hera, Poseidon,
Demeter, Apollon, Artemis, Athene, Ares, Aphrodite, Hephaistos, Hermes, Dionysos, Hestia), and
the Virtue's details list that god's Sympathy Traits to choose from (The Sundered Eagle
p. 127): Zeus, for one, Thunder & Lightning, Kings and Sky, with Fidelity negative.

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

Conciatta's breakthroughs (Legends of Hermes pp. 14-16) are Hermetic
Virtues gained by research or integration. **True Understanding of the
Realms** (Major): an aura of another realm counts less by the magus's
score in its Lore (Dominion, Faerie or Infernal Lore), never below 0, for
its penalty and its extra botch dice, shown on the Casting Score's and
Lab Total's aura line; a bonus it gives (a Faerie aura's +half) is kept
whole. **Insight of the Realms** (Minor): in a Ritual or ceremonial
casting in an aura, that realm's Lore stands in for the lower of Artes
Liberales and Philosophiae when it is higher, shown in the working; and
it sees through that realm's regio boundaries in place of Second Sight.
**Confluence of the Realms** (Minor): a lab text's realm may be changed
when used again, and vis may be extracted in an aura of any realm.

## Hermetic Magic tab
<!-- help: tab-hermetic -->

A magus's Arts, what they can cast, their raw vis, the spells they know and
<!-- tui -->
their research goals on the [Research tab](help:tab-research). Only a magus has this tab. The line at the top names the
magus's Talisman, how far it is opened and its attunements.
<!-- /tui -->
<!-- gui -->
their research. Only a magus has this chapter.

**Current Location**, at the top of the chapter, says where the magus is now
and the aura his casting counts there; its button sets it
([Current Location](help:whereabouts)). **Magic Outside the Lab**, under
Raw Vis, holds the rest of what he can do with his magic: Craft by
Magic, Certamen, and Cast in a Lacuna, Spirits and Names, Dream
Working, Hermetic Sacrifice and Open a Tunnel when he can use them.
<!-- /gui -->

**You type:** the XP in each Art, the raw vis the magus holds, and the
spells they know and their Mastery.

**The app works out:** each Art's score from its XP, the Casting Score for
every Technique and Form, Magic Resistance, Penetration and the Certamen
totals (on the desktop, under the Casting Scores).

**Certamen** (More on Known Spells; on the desktop, in Magic Outside
the Lab; see [Certamen](help:certamen-duel))
plays a duel with another magus of the saga.

The casting notes end with **craft magic**: Rego craft (shaping raw
materials) is Perception + Finesse, Creo craft (making the thing) is
Intelligence + Finesse, each + a stress die, against the Ease Factors for
Creating and Crafting Objects (DE pp. 306-308).

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
too, as are a Heartbeast's -15 in animal form and Verditius Magic's
reminder that Formulaic and Ritual spells need his casting tools (DE
p. 241).

Hermetic Numerology lists the Rotes the magus knows: a Rote is cast with no
die and no Fatigue, quietly and still, its Casting Total half of Stamina +
Technique + Form + Artes Liberales + aura (rounded up), with the
Numerologist's book bonus too when he takes a round to consult it (TMRE
p. 92). Hermetic Geometry adds +3 for a spell tracing a circle or line and
+3 more cast ceremonially in a regular figure (TMRE p. 94); Hermetic
Architecture reminds how high Bind the Mystical Structure must be (TMRE p.
98).

Faerie Magic, Spell Timing and Secret Name add reminders: a Bargain spell's
Penetration Total is doubled and takes effect when the bargain is broken;
a held or If (Condition) spell is worked out, Penetration too, when it is
released or triggered, and an If spell lapses after a year; no sympathetic
connection works against a magus with Secret Name, and one who knows the
secret name doesn't subtract the spell's level from his Penetration Total
(DE pp. 235, 237, 239-240).
Hermetic Metamorphosis reminds its holder of the surgery of Harmonic
Metamorphosis of the Beast (Magi of Hermes p. 83).

A Bjornaer's reminders give his Stamina + Heartbeast against 3 + the
magnitude to change form despite a shapechange or an Aegis (DE p. 234), his
heartbeast's temperament when the Heartbeast specialty names one of the
book's beasts (pp. 19-21), Theriomorphy's roll against 9 (p. 27), and with
an inner heartbeast the roll against 9 to take it and the Magic Might of the
Great Beast he would become at Final Twilight, 5 x Heartbeast (pp. 24, 32).

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
Casting, Multiple Casting, Obfuscated Casting, Precise Casting or Quick
Casting, are counted: Quiet and Still Casting in the score, the rest in a
Mastery line (DE pp. 225-226). House Mercere's are read too (Houses of
Hermes: True Lineages pp. 99-100): Adaptive Casting,
Boosted, Disguised, Harnessed, Stalwart and Tethered Casting (not for a
Ritual), Lab Mastery and Learn From Mistakes, each on the spell's casting
lines. Adaptive Casting follows the Errata (p. 46): the mastery serves on
any spell similar to the mastered one, not only General spells. A similar
spell is one of the same Technique and Form with the same base level at
another Range, Duration or Target, or with the same Range, Duration and
Target (DE, Similar Spells, p. 260; the troupe has the last word). Each
similar spell's casting lines name the masteries it may borrow; when two
or more apply, only one serves a casting, its score with its own special
abilities, never added together. Lab Mastery on the similar spell a lab plan names adds its Mastery
score to the Lab Total, on top of the similar spell's bonus. Societates
(p. 33) reprints these, and its Fast Trigger for items is the DE's
(p. 257), already on the device forms.

**Mutantum spells** (True Lineages pp. 101-102; Errata p. 46): a known spell
that is Boosted, Harnessed or Tethered says what each does on its casting
lines: boosting spends a pawn of vis a magnitude to raise its Range,
Duration, Target or size, a botch die more each, cast, tiring and
penetrating at its own level, and past Formulaic limits (Year, Boundary)
only for a Ritual; a harnessed spell is ended at will by concentrating; a
tethered one's control passes to another, or to an object that casts it on
a fit target. A magus without the Virtue for a quality is told he can't cast
it. The reminders give Mutantum Magic and Tamed Magic. The Cult of Heroes'
**(Characteristic) of the Followers** rituals raise a Characteristic by one
to no more than 0, **of the Heroes** to no more than +5, and Mercury's
Blessing is a Mercurian Ritual (p. 103).

**Fenicil's rituals** (True Lineages pp. 76-77): a magus who has one of
the rituals as an Ability (Wisdom of Athena, Sight of Alatheia, Veil All
Eyes, The Oath of Truth, The Will of Alatheia, or the greater Curse of
Thoth, Curse of Mars, Call for Justice) sees its Ease Factor, the Wizard's
Communion it needs, its vis and casting time. The leader rolls Stamina +
everyone's score in the ritual + aura + die; the excess over the Ease
Factor is its Penetration; no botch unless stressed. An Unstructured
Caster can't cast them. Performance Magic (DE p. 101) and Spell Binding
(The Mysteries Revised Edition pp. 27-28) are noted when a magus has
them.

**Certamen.** A Tremere's Minor Magical Focus in certamen doubles the
lower of the two Arts (DE p. 233), and a Deficient Art halves the total it
is in.

**Schools of certamen.** At the start of a duel each magus fights either as
a follower of his school, with its strongest techniques but no change of
school, or in the style of various schools, with weaker imitations he may
swap at the start of each round (True Lineages p. 135). The Gladiator
school is the basic rules. Most other schools trade one total for another,
up to a multiple of Finesse: the Andabatus Attack for Defence, the
Hoplomachus Defence for Attack (and more Defence in a round he doesn't
attack), the Provocator Resistance for Initiative, the Retiarius Initiative
for later Attack Advantage, the Saggitarius Attack for Defence with a hit
costing one Fatigue level at most, and the Laquerius Defence for a noose
(pp. 136-138). Others act when the duelist lands a blow and declines to do
damage: the Essedarius frightens, the Gladiatrix reads the foe, the
Pumilius amuses, the Velitus wears down Resistance, and the Scissor's hit
after a skipped attack cuts deeper. The Bestiarius, for Bjornaer only, uses Heartbeast in place of Finesse in
a Muto duel and adds twice it to Resistance in Muto Corpus or Muto
Animal; a Bjornaer fighting in its style adds his Heartbeast to
Resistance in any duel (True Lineages p. 136). Charon and Bone-biting are tricks with no
followers today.

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
  rite guidelines (Realms of Power: Faerie, Hermetic Rites). He may count
  a Ritual's aura from the Faerie column of the realm table when it is
  better than the Magic one (p. 121).
- A Ritual adds his best **Method + Power** of the style's realm instead of
  Artes Liberales + Philosophiae, when that is more.
- **Goetic Arts**: in a Goetic Art's total a magus may use Rego for the Art
  and Vim for the Realm Lore, when they are higher (Realms of Power: The
  Infernal, Goetic Magic).

Holy Magic's halved Lab Total from a Hermetic Lab Text (and halved
reading from a Hermetic book on an Art or an Arcane Ability: a text by a
holy magus, or one ticked Holy on its form, isn't halved), and Chthonic
Magic standing in for Magic Theory on a dark or sinister effect, are
counted on a lab plan (see [Lab Total](help:invent-spell-total)). What
can't be worked out (Chthonic Magic's sinful acts, the faerie rite
parameters) is written in
that closing line as the books word it.

A character with **Dead Language: Adamic** has a note: any Adamic adds +1
to the Penetration multiplier against a target named within Voice range,
with an Arcane Connection to it; fluent (5 or more), the named target is
always a lasting connection (+4), so +5 in all, and a mundane thing whose
name he knows counts as an Hours connection (Ancient Magic pp. 10-11). A
holder of a **Secret of the Grigori** has a note of its three Arts: their
vis may stand for one another and requisites among them are ignored; held
as the Supernatural Virtue (not a Legacy), vis used so in a Divine or
Infernal aura rolls double the botch dice (p. 67).

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

A demon-hunter's spells say what they do at their level: Demon's Eternal
Oblivion, Fanning the Infernal Flames, The Wicked Jar, Bind the Devil's
Hands, Early Punishment for the Sinful Witch, Exorcise the Filthy Spirit,
Lash of the Chastened Servant, Adjuration of the Hell-Sworn Spirit,
Cleanse the Verminous Vis and Command the Vile Spirit (Realms of Power:
The Infernal pp. 121-122, with the Errata's levels). Two Mastery abilities
are read by name: **Apotropaic Mastery** adds Mastery Score x Hierarchy
to the level of effect of a spell on Infernal Might (pp. 122-123), and
**Goetic Mastery** adds the fitting Goetic Art to a spirit spell's Casting
Total and Hierarchy x 5 to its Penetration against a demon (p. 124).

<!-- tui -->
More (`m`) here offers [Craft by Magic](help:craft-magic).
<!-- /tui -->
<!-- gui -->
**Craft by Magic**, in **Magic Outside the Lab**, under Raw Vis on the Hermetic Magic chapter, works out a craft
spell's Finesse roll ([Craft by Magic](help:craft-magic)).
<!-- /gui -->

<!-- tui -->
With Houses of Hermes: Societates in play, More (`m`) here also offers
[Cast in a Lacuna](help:cast-in-lacuna).
<!-- /tui -->
<!-- gui -->
**Cast in a Lacuna**, in **Magic Outside the Lab**, under Raw Vis on the Hermetic Magic chapter (with
Houses of Hermes: Societates in play), works out a spell cast in a city
([Cast in a Lacuna](help:cast-in-lacuna)).
<!-- /gui -->

With the saga option Learning cantations in play, More (`m`) here (on the desktop, a button beside Known Spells) offers [Learn a Cantation](help:learn-cantation).

## Current Location
<!-- help: whereabouts -->

A character's Casting Scores, Penetration, and his tradition's and his
Mysteries' totals count the aura where he is. At home that is his
covenant's. **Current Location** (More on Casting Scores; on the desktop, the
button at the top of the Hermetic Magic chapter, under the line saying
where he is) sets where he is now, when away: a place of the saga, whose
aura (and its kind) is used, or somewhere else, its aura and realm typed.
A foreign realm's aura then counts as the realms' interactions say
(DE pp. 410-411): a Magic magus's casting is lowered in a Divine or
Infernal aura, and so on. The Casting Scores say he is away. His seasons,
laboratory work, aging and warping stay at home. Set him back **At home**
when he returns. While he is a guest at another covenant
([Stay as Guest](help:guest-stay)), **Where he is a guest** takes the
place of At home, and counts that covenant's aura.

## Stay as Guest
<!-- help: guest-stay -->

Magi are expected to take in visiting magi, even unannounced (DE p.
518), and a magus copying from a library that isn't his own enjoys
*scribal hospitality*, usually for a payment or a service (DE p. 381);
guests count their stays in seasons, and are charged for their quills,
vellum and ink (Covenants pp. 96-98). **Stay as Guest** (More on Casting
Scores; on the desktop, a button under Current Location, at the top of
the Hermetic Magic chapter) makes the magus a guest of another covenant
of the saga:

- **Staying at**: the host (any covenant but his own), or **Not a guest
  anywhere** to end the stay.
- **Since** and **Until the end of**: when the stay began, and the last
  year of it (blank for open-ended).
- **Fee**: pawns of vis, pounds of silver or seasons of service a year,
  or no fee, and **How many**.
- **May study and copy from its library** and **Has a laboratory
  there**, and the **Conditions of hospitality** in words.

A host of a Rhine Tribunal fills in its Peripheral Code's terms when it
is chosen: at least three years and at most seven, three pawns of vis a
year (a season's service may stand in for it), and no laboratory owed
(Guardians of the Forests p. 20); a stay outside those years isn't
saved. Elsewhere the books set no terms, and the troupe agrees them.

While he stays, his casting counts the host's aura (unless Current
Location says he is elsewhere), the Casting Scores say so, and, with the
use of the library, its books join those he may study and copy in his
season's plan. His seasons, laboratory, aging and warping stay with his
own records. Starting and ending a stay are written in his Diary and the
host's. The host lists him under [Guests](help:section-cov-guests),
where **Pay the Fee** takes each year's.

House Jerbiton keeps a code of courtesy between guest and host (Houses
of Hermes: Societates p. 51): the guest announces himself, his business
and when he will leave, brings a small gift, is good company, helps if
trouble comes and leaves when asked; the host says plainly whether he
offers hospitality, gives counsel on the region's dangers, food, wine
and a bed, a gift in return (an uneven exchange is a debt of honour) and
protection. Breaking it insults only Jerbiton magi. The app keeps no
rules for it: give the gifts with [Give](help:give), and write the rest
in the Diaries.

**See also:** [How to stay at another covenant](help:guide-guest-stay)

## Certamen
<!-- help: certamen-duel -->

**Certamen** plays a duel between two magi of the saga (DE pp. 231-233).
Choose the rival, the Technique (by custom the challenger's) and the Form
(the challenged's), and the stakes. Each side has a plan for the whole
duel: which Art he attacks with (the Technique, the Form, or whichever is
better for him), the pawns of vis he spends a round on attack and on
defense (of the Art used, +2 a pawn, at most his score in it), and when
he concedes (at -1, -3 or -5 of Fatigue, or never).

Initiative (Quickness + Finesse + a stress die) is rolled once. Each round
the winner attacks first, then the other: Presence + the attacking Art +
a stress die against Perception + the other Art + a stress die, a tie
going to the defender. What the attack wins by adds to Intelligence +
Penetration; less Stamina + Parma Magica, every five points or fraction
cost a Fatigue level, whose penalty then counts. A Tremere's Focus counts
the lower Art double. It ends when one falls unconscious (the victor may
cast a spell of the duel's Arts at him, his Parma circumvented) or
concedes (his Parma stands). The panel shows both duelists' totals; the
result shows every round. **Take the Fatigue they lose** puts it on their
sheets; the vis spent comes off their raw vis, and both Diaries record it.
A magus who would change plan mid-duel, or a duel broken by a lost
Concentration roll, is played at the table. A magus can botch (DE p. 231),
and the book doesn't say what that does, so a botch stops the duel there:
the storyguide says what comes of it, and the rest is played at the table.

## Craft by Magic
<!-- help: craft-magic -->

The Finesse roll a craft spell needs (Definitive Edition, Magical Craft,
pp. 306-308). **Close** keeps nothing; **Roll** rolls it once and says how
it went, keeping nothing either.

- **Rego** shapes raw materials as a craftsman would: Perception + Finesse
  against the Ease Factor of the hardest task the spell covers.
- **Creo** makes a working example of the thing with no roll (as a work of
  craft of Ease Factor 6), its details as chance falls. To fix details:
  Intelligence + Finesse, one basic property 0, two or three (or one
  precisely) 3, an elaborate specification or a better-quality item as
  Rego.

The Ease Factors for Creating and Crafting Objects already hold the +3 for
magic and a day's work: Trivial 3, Simple 6, Easy 9, Average 12, Hard 15,
Very Hard 18, Impressive 21, Remarkable 24, Almost Impossible 27. More work
adds: a month's +3 (or thirty craftsmen for a day), a season's +6, a
year's +9. With a mundane craftsman's Ease Factor or a City & Guild
Workshop Total, the app adds the +3.

The roll takes the Wound and Fatigue penalties, -3 for each of Clumsy and
Inconstant Magic, and the spell's Precise Casting. A failed Rego roll
still rearranges the materials, into nothing useful; a botch looks right
but has a hidden, fatal flaw. A failed Creo roll still makes the thing
without the details; a botch makes something that hinders the caster.


## Open a Tunnel
<!-- help: open-tunnel -->

Open a Tunnel (More on a magus's Known Spells; on the desktop, in Magic Outside the Lab under Raw Vis), offered once he knows a tunnel spell, works out a Wizard's War tunnel (Hermetic Projects pp. 78-81; DE pp. 219, 372). Choose the tunnel and the level he casts it at, the Arcane Connection (one of his covenant's laboratories', or one held otherwise) and how long it lasts, the sympathetic connections he holds (signature, name, horoscopes, a symbolic representation: no more than +2 each), and the target: a magus of the saga (his own Magic Resistance against each Form), or a Parma Magica typed, and any Aegis he shelters in.

The inspector gives the Penetration multiplier (1 + the connection + the sympathies, DE p. 219), the tunnel's Penetration against his Vim, then each spell he knows that fits through: Touch range or more, and no higher than the tunnel allows (Opening the Intangible Tunnel and The Minute of Reckoning their own level, The Cursèd Day a magnitude less, Wizard's Siege two less, The Evil Eye and The Master's Message a magnitude more). The same multiplier applies to each, since he holds an Arcane Connection to the target. Inside an Aegis every spell must also Penetrate it, unless its caster holds the Aegis's token (p. 79). Break the Siege suppresses a tunnel of less than its level + 2 magnitudes (errata p. 81). Cast rolls the tunnel once; nothing is kept.

## Cast in a Lacuna
<!-- help: cast-in-lacuna -->

A spell cast in a city, from a lacuna or in the Dominion (Houses of Hermes:
Societates pp. 57-58; Definitive Edition pp. 217-218). **Close** keeps
nothing; **Roll** rolls the casting once and says how it went, keeping
nothing either.

A lacuna is a small patch inside a city where the Dominion doesn't hold:
most have no aura at all, some a Magic, Faerie or Infernal one. Cast from
one, a spell meets the lacuna's aura instead of the city's Dominion --
unless its target is itself within the Dominion, when the Dominion's
penalty stands. Most cities have a Dominion of 3: -9 to a Hermetic
Casting Score (p. 58). Subtle gestures and quiet words (-7), or neither
(-15), keep witnesses from seeing a magus at work.

Cast ceremonially (a Spontaneous spell, or a Formulaic one with the
Ceremonial Casting Mastery ability, by a magus with Artes Liberales or
Philosophiae), a spell adds Artes Liberales + Philosophiae and its props'
+1 to +5, in place of words and gestures. The ceremony takes 15 minutes a
magnitude, 12 in a temporary space, 9 in one naturally suited, 6 in one
carefully designed, 3 in his laboratory, 1 in a room built for it (DE p.
218); with Mystical Choreography, 5, or 1 in any prepared space (DE p. 99).
A spell is no greater than the magnitudes the time spent allows.

The inspector shows the Casting Score in the lacuna and outside it, what
the die must reach, the ceremony's time, the botch dice, and the cities
whose lacunae he has found.

## Hubris
<!-- help: verditius-hubris -->

More on a Verditius's Personality Traits, shown once he has the Flaw Hubris
or the trait. What raised or lowered his pride between seasons (DE p. 242;
Houses of Hermes: Mystery Cults pp. 115, 120). Each is kept in the Diary.

- **Experience** for selling or making for pay a charged item or an item of
  quality (1), repairing or reforging an item for pay (1), a lesser enchanted
  device (1), a greater one (3), an attuned item (6), an automaton (1 a
  magnitude of its Might), winning the Contest's apprentices' (1),
  journeymen's (3) or masters' (6) category, declaring a vendetta (1) and
  winning one (3). Learning an Inner Mystery is added by the Initiation
  season. A magus with no Hubris trait yet starts at his first Inner
  Mystery's score.
- **Refusing a vendetta** (type the magus refused) gives the House
  Reputation Dishonorable 4 and lowers the Hubris score a full point: it
  falls to the experience of the score below, as an Ability would (pp. 115,
  119). The refusal is kept: he loses the Reputation only once he has
  regained the score he had and waged a vendetta on the magus he refused
  (p. 115).
- **Wages the vendetta on a magus he refused** (offered once he has refused
  one) marks it waged; the inspector says what each refusal still needs.
  When the Hubris score is back too, the Reputation goes.
- **Resisting a vendetta**: a Personality Trait that works against Hubris
  (her Intelligence without one) + a stress die against her Hubris + the
  challenger's (p. 120). Resisting a temptation to sell is an opposed
  Personality roll, or a Confidence Point spent to walk away: the troupe's.

**See also:** [Personality Traits](help:section-personality-traits),
[Script components](help:guide-initiation-plan)

## Divination
<!-- help: tmre-divination -->

More on a Hermetic diviner's record (Divination & Augury, or Hermetic Dream
Interpreter); on the desktop, in the Deeds chapter under Insight. A divination answers one
question as a Momentary Intellego spell of any Form would; its Ease Factor is
that spell's level (The Mysteries Revised Edition pp. 59-60). It makes the Ease
Factor or fails: it is not open-ended (p. 62).

- **Casual** (a round): stress die + Perception + Divination + aura + the
  storyguide's bonus for apt omens (+0 to +3, rarely +5).
- **Ceremonial** (15 minutes a magnitude): stress die + Intelligence +
  Divination + aura + the method's ceremonial bonus (+1 to +5, the Ceremonial
  Augury Phenomena table, p. 61) + the sympathetic bonus (the Arcane
  Connection's and each sympathetic connection's multiplier, DE p. 220) + a
  Scrying Device's bonus (its effect's level over 10, rounded up). The
  horoscopes count only divining by Astrology. The Errata (p. 50) keeps these
  bonuses out of a casual divination. **The question is about** offers the
  method's uses from the table (Aeromancy's weather, +5), which fill the
  Ceremonial bonus in; choose Something else to type it. A diviner whose
  Virtue names no method is offered the whole table.
- **Penetration**: the total + the Penetration bonus - the Ease Factor.
- With Hermetic Dream Interpreter: a **symbolic reading** (stress die +
  Intelligence + Divination, no aura; 9 the dreamer's state, 12-15 the dream's
  reasons, 18+ its causes and consequences) and **Dream Calling** (stress die +
  Presence + Divination + aura against 6), pp. 62-63.

The live box shows the total, the chance and the botch dice (one more per
point of a non-Magic aura); Roll rolls it and keeps it in the Diary.

## Astrology
<!-- help: tmre-astrology -->

More on the record (on the desktop, in the Deeds chapter under Insight) of a
magus with Planetary or Celestial Magic, a Periapt, or the Astrology method of
divination. Each reckoning is a roll of Intelligence +
Artes Liberales (Astronomy), kept in the Diary.

- **Daily Horoscope** (an hour) and **Nativity Horoscope** (a day), against 9:
  +1 and +2 sympathetic connections (DE p. 220). A failure he knows of; a
  botch he doesn't.
- **Periapt Horoscope** (Periapt, p. 48): against 9 on the equinox or
  solstice; sound, it serves as a one-use Lab Text: the Lab Total / 5 charges,
  an effect up to 5 x Astronomy. A botch wastes the season.
- **Astrological Duration** (Celestial Magic, pp. 49-50): 6 + the units
  wanted (Minutes, Hours, Days, Signs; a year at most), -3 with a Daily
  Horoscope, -3 with the exact time measured, +3 for a precise end, then
  halved by a magical armillary sphere. With the time measured and a horoscope
  or sphere, checked over a Diameter, a simple die. A miss leaves the spell out
  by up to the shortfall; a botch botches the spell.
- **Favorable Hour** (p. 50): against three times the bonus (+1 to +5); a
  botch is the bonus as a penalty for that hour. The storyguide's quick hour
  is rolled with it.
- **Set a magical armillary sphere** to another place: against 9, a single
  round (p. 54).

The season **Make an armillary sphere** (Work & trade) designs it (Int +
Astronomy against 12) and builds it (Dex + Craft: Mechanisms or Clocks against
12; Blacksmith at -3 with three more botch dice), p. 52. Opening the sphere
costs 15 pawns in base metal, 18 in silver, 30 in gold, then Know the Heavens
(InVi 29) and Track the Heavens (ReTe 28), p. 53.

Celestial Magic's Laboratory Horoscope, when its die is typed on the plan,
takes its bonus off the pawns of vis that open an invested device, at least
one still paid (p. 49).

## House Acclaim
<!-- help: house-acclaim -->

More on a magus's Reputations (on the desktop, in the Deeds chapter under
Session & Reputation), shown for a magus of House Bonisagus or
House Flambeau, or anyone who already holds House Acclaim. It keeps the
House's own Reputation, House Acclaim, which grows like an Ability: 5,
15, 30 and 50 points reach 1 to 4. The first award starts it. Each award
or roll is kept in the Diary.

- **Research made public** (Bonisagus): the Research and Acclaim Points
  table (Houses of Hermes: True Lineages p. 21): an Art tractatus is its
  Quality/2, a summa its Level/2, an original spell 1 a magnitude (2 by
  experimentation), a Talisman 2, a familiar its Magic Might/5, an
  apprentice trained 3, each project assisting a magus of higher rank 1,
  a stabilized breakthrough 3 a magnitude, a minor breakthrough 15, a
  major one 30. A tractatus or Lab Text taken into a folio earns twice.
  Rediscovering one of Conciatta's Minor Virtues is 15, her True
  Understanding of the Realms 30 (Legends of Hermes p. 45). The scores
  are the ranks: boukoloi 1, daduchos 2, cannophori 3, dendrophori 4; the
  Primus is above them (TL p. 22). The word takes a year a point to
  spread.
- **What it does** (Bonisagus, TL p. 22): its score is added to social
  rolls with magi of House Bonisagus (any roll with Presence, as a rule
  of thumb), and to Intrigue or Guile resisting a maga Trianomae, never
  to Presence in certamen. A season searching for an apprentice adds it
  to the usual roll, Perception + a stress die against 9 (DE p. 269; TL
  repeats the older 12): less still finds one, taken from another magus
  by right; failing by 5 or more antagonizes him, who must be
  compensated; a botch makes him the Major Story Flaw Enemies. Only a
  child found is added as a new character: one taken by right is that
  magus's apprentice already (DE p. 270), whom the storyguide names.
- **An argument over a folio** (Bonisagus, TL p. 23): Presence +
  Leadership, or Communication + Artes Liberales, + House Acclaim + a
  stress die, against the other magus's total; the higher wins.
- **Trianoma's cipher** (TL p. 21): a day's work, Intelligence + Latin +
  stress die, decoding when higher than 6 + the author's Communication +
  Intrigue; +3 for one decoded before.
- **A deed** (Flambeau, Houses of Hermes: Societates p. 31): a Hermetic
  Reputation, known in the whole Order. Experience for deeds before
  credible witnesses: an exceptional Gauntlet 2 to 5, a Wizard's March 1,
  a certamen won 1 (2 against a senior magus), a tournament 1 to compete,
  3 as a finalist, 5 as champion, -3 for a dismal showing (still 1 for
  competing, so -2 in all), fighting
  bravely in a Wizard's War 1 to 3, winning one twice the foe's highest
  Reputation, slaying a renounced magus three times his, a supernatural
  beast its Might/5, a Primus's order fulfilled or another glorious deed
  as the storyguide says. Losses take experience away: a year without a
  gain -1, a certamen lost -1 (-2 against a junior magus), each incident
  of dishonesty or cowardice -1 or more. Certamen counts only when it
  settles a real dispute. House Acclaim never falls below 0: an ignoble
  act at 0 starts the bad Reputation you name, at 1 (DE p. 386). Famous
  may be put in it (it starts at 4), and the Flaw Miles gives 5
  experience points in it.

The inspector shows the points, the score they bring House Acclaim to
and, once it is held, what it does.

**See also:** [Reputations](help:section-reputations),
[Reputation Roll](help:reputation-roll)

## Reputation Roll
<!-- help: reputation-roll -->

More on a character's Reputations (on the desktop, in the Deeds chapter
under Session & Reputation): has someone heard of one? A stress die
+ the Reputation's score (a bad one's size) equals or beats the Ease
Factor for where the listener is: 0 in the same village, parish or
covenant; 6 in the same town, diocese or Tribunal; 9 in the same county,
province or the whole Order; 12 in the same country or the whole Church.
The Reputation's type says which column counts. The more it beats the
Ease by, the more he has heard (DE p. 28). Between two magi of the same
Jerbiton league every Reputation counts 3 higher (Houses of Hermes:
Societates p. 53). The roll is kept in the Diary.

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
Saving adds a Diary entry for the season: what changed, how it came
about, the story you gave it and the rules it follows.

- **Gain a Flaw**, by mishap (an injury, an amputation, a disease: a lost
  hand is always Missing Hand), by their own actions (a feud, a debt, an
  animal companion, offending a faerie), by magic (a curse: a hedge
  wizard's usually wears off, a creature that spends Might lays a lasting
  one) or by Warping. A changed circumstance is a Flaw only if it affects
  the game, seeds stories or changes how the character is played
  (Grogs p. 62).
- **Gain a Virtue**, by magic (most grants are temporary; a lasting one
  comes from a supernatural being or the Goetic Arts), by Initiation
  (which needs a score in the cult's or tradition's Organization Lore
  first), by their own actions (Social Contacts for an agent recruited,
  Protection for a powerful friend) or by severe Warping. A Virtue that
  changes how experience is gained doesn't change what was gained before
  (Grogs pp. 62-63).
- **Lose a Flaw**, mostly by the ways a Virtue is gained, though not
  every way suits every Flaw: Initiation won't grow back a lost hand
  (Grogs p. 63).
- **A temporary Virtue or Flaw ends**: one gained by magic for a while is
  taken off the sheet, any Characteristic it moved put back. Most Virtues
  granted by magic are temporary (a gruagach's spells, an Object of
  Virtue, faerie wizardry), and hedge curses that lay Flaws are usually
  limited in duration too (Grogs pp. 62-63), so a Virtue or Flaw gained
  by magic is ticked **Temporary** unless you clear it, with the season
  and year it ends if they are known (a year alone ends at its Winter).
  The sheet marks it "temporary, until Winter 1225". When its last
  season is advanced past, the character's Diary and the season record
  say it has ended; it stays on the sheet until you take it off here,
  since a story may renew it.
- **A change of Social Status** replaces the old status with the new; a
  status whose description allows it may be kept beside it (Grogs p. 61).
- **Exchange one chosen wrongly**, with the troupe's approval: an
  established character exchanges only a Minor for a Minor and a Major
  for a Major on the same side, never one that changes Characteristics;
  tick New to the saga for larger changes (Grogs p. 61).

The inspector warns where the books advise against a change: a grog
gaining a Story Flaw or a Major Virtue (unless he is becoming a
companion), a second Story Flaw, more Personality Flaws than the
guideline allows (DE p. 63). A second Major Personality Flaw is refused
(DE p. 63). Warping says what the character's Warping Score has brought
them (DE p. 391); a magus's comes through Twilight (DE pp. 229-230).

**See also:** [Aging & Warping](help:section-aging)

## Pilgrimage
<!-- help: pilgrimage-more -->

A pilgrimage's road (The Church pp. 15-19), each step written in the
Diary. Its aim sets its Target Level: 18 for a minor pilgrimage (a
single season and story) to gain a Minor Virtue, lose a Minor Flaw (or
Virtue), remove a negative Personality Trait or meet a penance; 30 for a
major one (several seasons) to gain a Major Virtue, lose a Major Flaw,
ask for a miracle, self-initiate in Holy Magic (with True Faith) or meet
a penance. The 30 may also gain a Major Supernatural Ability or Divine
Methods and Powers; the 18 a Minor Supernatural Ability of the Divine.
No pilgrimage grants or removes Hermetic Virtues and Flaws, or
background ones such as Privileged Upbringing and Educated (p. 16): the
app treats every Virtue that gives experience at creation as background.
A Divine Supernatural Ability gained is added at 1, without the Gift's
penalty. Every aim needs the troupe to agree it suits the pilgrim.

- **Begin a pilgrimage**: its name and Target Level. Grogs may go too.
- **An Oppositional Element overcome**: its value goes toward the Target
  Level -- +3 natural hazards, a temptation he is prone to, another
  trial; +6 bandits, religious or political enemies, storms; +9 a
  supernatural encounter, a shipwreck, distractions to abandon it; +12
  direct demonic opposition (p. 17). Travel in a Christian land outside
  his homeland (+3) or through non-Christian or heretic lands (+6) counts
  once, only the higher. Each season on the road (the Pilgrimage season
  activity) is +3.
- **An Oppositional Element failed**: the aim fails unless a later element
  he overcomes remedies it.
- **Claim the pilgrimage's aim**, once the Target Level is reached and no
  failure is left unremedied: the Virtue is added, the Flaw or Trait
  taken away, Holy Magic added. The traits offered for removal are those
  with a negative score or leaning to a sin (Cruel +3 is Kind -3; The
  Church p. 20), the book not saying what "negative" means; removing any
  other is for the troupe to agree and do by hand; a penance met or a miracle asked is
  written in the Diary for the troupe. He must have avoided mortal sin on
  the road and confessed his venial sins on arrival (p. 18).

At a saint's shrine, one with a Devotion to the saint gains 10 Devotion
Points, +5 for each further site of the saint's life, and up to 5 for
relics seen (p. 19).
## The Enigma tab
<!-- help: tab-criamon -->

A Criamon magus's path toward the Enigma: the path he walks, its five
stations and what the next avenue needs, and his stigmata (Houses of
Hermes: Mystery Cults pp. 50-51, 58-73). The tab is there only for a magus
of House Criamon (or one Initiated into the Enigma).

**You type:** the path (or let his stations show it), his guide, and his
stigmata.

**The app works out:** which stations he holds (from his Virtues), what
the next avenue needs (his House Criamon Lore, its Target against the
guide and the Script), and, when an Initiation season follows an avenue,
the station's Virtue, its Ordeal's Flaws and the season it was reached.

**See also:** [Hermetic Magic tab](help:tab-hermetic),
[Planning tab](help:tab-planning)

### The path
<!-- help: section-char-criamon-path -->

The path he walks: of the Body, of Seeming, of Strife, of Walking
Backwards, or the Path of the Mirror, which only the Primus follows
(pp. 57, 59; its stations aren't printed): Change Path offers it only to
a magus whose Hermetic background names him as the House's Primus.
Unless Change Path names one, it is the path most of his
stations are on; with none, he walks the Winding Path (p. 58).

**Station:** how far along it he is. **Enigmatic Wisdom** and **House
Criamon Lore** (the sheet's Mystery Cult Lore: Criamon; House Criamon Lore
under that name counts too): a station needs the Lore at its place on the
path + 1, so the fifth needs 6 (p. 60). **Flaws of the path:** the Flaws
the stations' Ordeals have given him; every follower of a path ends
Disfigured, with Vow or Pious (p. 60). **Guide:** his Presence + House
Criamon Lore. The book's Scripts assume 6, and the House always provides
such a guide, so with none named he has the House's (Presence + Lore 6).
A ghostly Primus at the Cave of Twisting Shadows sometimes guides: Lore 9
and the Presence he had in life (p. 60). Any character who knows House
Criamon Lore can guide; one not of the House is unusual, and shown as a
warning (p. 59; DE p. 387).

**Next:** the next avenue, its station, and the Target (21 for a Major
Virtue, less his best past Ordeal's reduction, DE p. 388) against the
guide + the Script. A head bound in infancy (or castration, broken bones,
severed joints) gives an aptitude for one path, set on Change Path: +3 to
that path's first station only (p. 51).

One path at a time: a magus who steps onto another keeps only his
Enigmatic Wisdom of the old path's stations, which the tab lists as set
aside; rejoining, he regains them. Only the Primus keeps his on the Path
of the Mirror (p. 58).

<!-- tui -->
e changes the path, the guide, a ghostly Primus's Presence and the path
his head binding suits; m (More) offers Follow an Avenue.
<!-- /tui -->
<!-- gui -->
Change Path and Follow an Avenue sit beside the title.
<!-- /gui -->

### Stations
<!-- help: section-char-criamon-stations -->

The path's five stations, each a Major Mystery Virtue: its name, what it
gives, its Script against the Target the book prints (which already
counts the Ordeals of the stations before it) and when he reached it: the
season, kept when an Initiation season reached it, or "reached" for one
held before. The next is marked "next", or "needs Lore n" when his House
Criamon Lore is short. Choosing one shows its avenue in full (pp. 61-71;
Errata p. 55 for the Path of Strife's fourth, Target 18). The Path of
Walking Backwards' fifth shows its reduction as the book prints it (its
second Initiation since a Major Ordeal, −6, p. 71); the app's Ordeal sizes
are the Definitive Edition's Minor, Medium and Major (DE p. 388).

### Stigmata
<!-- help: section-char-stigmata -->

A Criamon magus's marks: where, the mark, what it marks and when. A new
one appears, or older ones move, for a station reached, a rise in
Enigmatic Wisdom, an Inner Mystery learned, an apprentice begun or
finished, a familiar sought or bound, or a great work of the Art; the
first usually with the Riddle of the Magus, and loops on the wrists after
Twilight (p. 50). They have no mechanical cause and can't be removed, even
by magic. Another Criamon magus reads what one marks with Intelligence +
Enigmatic Wisdom against 6 (p. 60). A tattoo that is an enchanted device
is an ordinary device on the character, not a stigma (p. 51).

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

The books' magi have reached four more breakthroughs, each a goal the
Integration picker fills in (their books give no points, so each takes its
kind's usual target):

- Fertile Longevity Ritual (Minor, 30; Magi of Hermes p. 20). A Longevity
  Ritual leaves its subject permanently sterile (DE p. 261); once a magus
  has reached this, the rituals he makes leave their subject fertile. Like
  any Minor Breakthrough, any Hermetic magus with a Lab Text for an effect
  using it, or trained by its discoverer, can use it too (DE p. 281): the
  app can't tell which Longevity Lab Text uses it, so a Longevity Ritual's
  plan has a Fertile (Lab Text) tick for a magus who hasn't reached it,
  naming the Longevity Lab Texts he has at hand. The ritual's season says
  which it does.
- Hermetic Metamorphosis (Major, 45; Magi of Hermes pp. 82-83). Gives the
  Minor Hermetic Virtue of that name: organs grafted onto an animal by
  Harmonic Metamorphosis of the Beast, which only its holder can cast. The
  surgery is Dexterity + Chirurgy against 9, +3 for an organ added rather
  than swapped, +3 more to give a Virtue; failing, the animal dies soon
  after, and a botch makes a monster. A human recipient needs a further
  breakthrough.
- Hermetic Viresculture (Major, 45; Legends of Hermes pp. 72-75). Gives
  the Supernatural Ability of that name, its points as experience
  (DE p. 281). Only those Opened to the Hermetic Arts can use it.
- Viresculture of Lesser Enchantment Vis (Minor, 30; Legends of Hermes
  p. 73). Living Lesser Enchantment Vis may be made a Stirps, its
  effect's level standing for Magic Might; builds on Hermetic
  Viresculture.

Ancient Magic's chapters add what their integrations need. A goal named
for one (the Grigori Legacy, the Limit of Vis, Mutable Device, Awakened
Device, the vis-less devices) shows in its details the Arts and kind of
effect its Insights produce and the texts, relics and teachers that give
Insight: for the Grigori, the second book of The Enigma of the Sons of
God, the Stelae of the Watchers on Mount Hermon (also a Magic Theory
summa, Level 8, Quality 6) and Shamsiel on Mount Ararat (Ancient Magic
pp. 69-73); for Heron, his uncorrupted Greek texts, a working mechanica
and an anima (pp. 76, 79). A magus who holds a Secret of the Grigori gains
one extra breakthrough point each season of research toward the Grigori
Legacy, and a Secret or a Legacy each season toward the Limit of Vis
(p. 67); the app adds it when the season is applied and notes it in the
Diary. Two more choices follow Mutable Device: **Awakened Device, after
Mutable Device**, a Minor Breakthrough of 30 points once Mutable Device is
reached, and **Mutable Device without the Virtue**, the second Major
Breakthrough (45) that lets any magus with a Lab Text make them (p. 79;
Ars Magica Definitive Edition p. 281).

House Bonisagus's example discoveries (True Lineages pp. 30-34) say what
they give once reached: the six Parma Magica folds, Parmulae and
realm-aligned spells. A magus counts as knowing one when one of his
research goals of that name is reached, whether he made it or was taught
it; record a taught fold as a reached goal. He may know as many folds as
his Parma Magica score. The notes under his
[Casting Scores](help:section-casting) then give each fold's
resistance (Ablativa doubles Parma, worn down by each Penetration it
stops; Absorbea, Repercussa and Condensa against other Forms halve it,
rounded up; Condensa doubles it against its chosen Form; Custodia gives
no Parma resistance but adds twice Parma to Defense; Restricta is Parma -
3), the Parmula (a level 44 lesser device giving Magic Resistance 30 for
a year, 5 pawns, Rego Vim Lab Total 88), and the realm-aligned table
(p. 34). Figurine Magic's Ease Factors show for anyone with the Virtue.

**Aetheric Magic** is a Hermetic breakthrough of 100 points, at least 20
of them from each Technique's projects; it gives the Major Hermetic
Virtue Aetheric Magic and the Art Aether at 13 (Dies Irae pp. 38-39).
The Virtue and the Art aren't in the catalogs yet, so reaching it grants
nothing for you; the 20-a-Technique minimum is the troupe's to check.

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
Men p. 138). With The Sundered Eagle in play the catalog also has the
hand-held **Greek Fire Siphon**, a missile weapon fought with Profession:
Naffatun instead of a Martial Ability (a character needs that Ability by
that name). A shield doesn't defend against its fire: in a fight its
Defence adds to the target's Soak instead. One dose of Greek Fire is good
for 10 sprays, which the app doesn't count (The Sundered Eagle p. 47).
When a botch or an odd use may break the weapon, the totals
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

Lords of Men's weapons. With Lords of Men in play the Weapon list adds the
falchion, net, infantry shield, trident, whip, halberd, the bastard sword
(one-handed and two-handed), the sharpened rock, composite and horse bows,
the crossbow, the arbalest and the heavy arbalest (Lords of Men pp. 137-139;
the bastard sword's Load is 2, Errata p. 76). Rows the book reprints from
Ancient Magic or Guardians of the Forests come with either book. Crossbows
use the Crossbow Ability, and Strength doesn't add to their Damage (p. 138).
Where Lords of Men's tables differ from the Definitive Edition's (the
throwing axe, the short bow's Load, the warhammer's cost) the Definitive
Edition's figures are used.

Armour pieces (Lords of Men). With Lords of Men in play, the armour form's
Material also lists the book's pieces (Lords of Men p. 140): body armour (a
cuirass or jerkin, haubergeon, hauberk or full armour of eight materials), a
surcoat (gambeson, coat of plates), greaves or jambes, and helmets. The coat
of plates uses the Surcoats table's +2 and Load 2 (p. 140); the book's
Glossary (p. 141) says to use a metal scale cuirass's figures instead (+3,
Load 3), a conflict in the book, and the app follows the table. "Worn as"
says where a piece goes. A character wears one piece of each place, the best
one; their Protection and Load are added together, fractions kept to the end
and then rounded up, so a mail cuirass (+3, Load 1.5) and a coif (+0.5) give
Soak +4 and Load 2. Full body armour already includes greaves. If the
character also has a whole suit (the Definitive Edition's partial or full
armour), whichever protects better is the one worn. A Superior or Excellent
piece adds its bonus, except a helmet's, which counts only against blows to
the head (Lords of Men p. 136). A helmet's Perception penalty is shown in its
book line.

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

## Agents tab
<!-- help: tab-agents -->

The people the character controls through personal bonds: Lords of Men's
agents (Chapter Two: Politics, pp. 22-25). Every character has the tab,
after Inventory.

**You type:** each agent or would-be agent: his Social Status, what makes
him harder to win, what he brings you, whether he is impressed, and once he
is yours his Bond.

**The app works out:** how many agents you can keep, each one's resistance
from the Agent Recruitment Table, the Agency experience it takes to win
him, and the rolls to impress him and to set him a task.

**See also:** [Inventory tab](help:tab-inventory),
[Planning tab](help:tab-planning)

### Agents
<!-- help: section-char-agents -->

**The limit.** A character can keep 2 x (Presence + the higher of
Intrigue or Leadership - the Gift's social penalty) agents, at least 1
(p. 22). Only recruited agents count against it (their resistance is worn
to nothing); the people still being won show as a separate number beside
it. The count turns red past the limit. Beside it is the **Agency
experience** not yet spent: its own pool, apart from any Ability's.

**Who is not an agent** (p. 22): Hermetic magi, people with no political
role, an agent's own people, hirelings (who serve for pay and change
sides when the odds are poor), and other players' characters. Leave them
off the list.

**The list** shows each one's name, his Social Status Virtue or Flaw, his
Bond (the Personality Trait that ties him to you, and its score), his
resistance (a number, "impressed" once the first roll is made, and
"agent" once he is yours), and his resources.
<!-- tui -->
The details panel shows the chosen one in full.
<!-- /tui -->
<!-- gui -->
Clicking a row shows the chosen one in full in the inspector.
<!-- /gui -->
It lists the Agent Recruitment Table lines that set his starting
resistance (p. 23): his Social Status (a Major Social Virtue 3, a Minor 1,
a Free one 0, a Minor Social Flaw -1, a Major -3), less 3 or 1 for a Flaw
that would trouble you and 6 for one you use to dominate him, plus each
resource he will use in your service, 6 more for over three resources and
9 for over six; never below 1. Then what winning him needs, and for an
agent his Bond, his persuasion total and the **Tasks for Agents** table
(p. 24): the Ease Factor of each task and the die he needs.

**Coerced.** An agent who thinks you his social inferior is held only by
coercion: you have Difficult Underlings for him, and he has a Story Flaw
such as Blackmail or Dark Secret (pp. 22-23). One you dominate through a
Flaw hates you, with the same Difficult Underlings (p. 23). The form
and the panel say so.

**Winning him.** First you **impress** him: a stress die + Presence +
Leadership - the Gift's penalty against 6 (p. 24); a failure waits for
another story. Then each point of resistance falls for as many Agency
experience points as it now stands at, so a resistance of 3 takes 3 + 2 +
1 = 6 (p. 24). At 0 he is your agent, with a Bond of 0.

**Agency experience** comes from adventuring: when an **Adventure**
season is applied, the character gains as much Agency experience as the
season's Adventure experience (pp. 24-25). Exposure, Practice and teaching
bring none.

**His Bond** rises as an Ability does (5 x the new score), from Agency
experience, or from money at 5 points a pound, which fails for an agent
already prosperous or one who thinks taking money for service a crime or
sin (p. 25). Paying comes out of the silver the character carries.

**Setting a task** needs an agent with a Bond of +1 or more: a stress die
+ Communication + Charm, Intrigue or Leadership, as suits the request, +
Bond - the Gift's penalty, against the task's Ease Factor: 3, 6 or 9,
with +1 for within a few days and +3 for within a day, and +1, +3 or +6
for the risk to him (1, 3 or 5 botch dice; with no risk, a simple die).
Gathering news he hears anyway needs no roll (p. 24).

**Resolving the task**: once he takes it on, he rolls with his own
Characteristic + Ability against the task's Ease Factor (p. 24). **Resolve
the Task** rolls it and writes the outcome in the character's Diary.

<!-- tui -->
`a` adds an agent, `e` edits the chosen one and `d` deletes him. More
(`m`) offers **Impress** (only for one not yet impressed), **Spend Agency
Experience** (for an impressed one while there is experience to spend, or
an agent's Bond), **Set a Task** (only for an agent with a Bond of +1)
and **Resolve the Task** (for any agent).
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the agents. **Impress**, **Spend
Agency Experience**, **Set a Task** and **Resolve the Task** act on the
chosen one, and are greyed out where they can't: Impress only for one not
yet impressed, Spend for an impressed one while there is experience to
spend (or an agent's Bond), Set a Task only for an agent with a Bond of
+1, Resolve the Task for any agent.
<!-- /gui -->
The agent form's **The Agent** shows the resistance your choices give
him, and Set a Task's **The Task** the Ease Factor, the persuasion total
and the botch dice before you roll.

## Resolve the Task
<!-- help: agent-task-resolve -->

The agent's own roll, once he has agreed to a task (Lords of Men, Using
Agents, p. 24): a die + his Characteristic + Ability against the task's
Ease Factor. **Roll** rolls it once, says how it went and writes it in
the character's Diary under the agent's name and the task.

- **With** and **Characteristic + Ability**: the scores he uses, added
  by hand (an agent's resources are free text, so the app can't look
  them up). His resources are shown above them.
- **Task**: the band the persuasion was for, which sets the **Ease
  Factor** to its highest (Easy 6, Hard 12, Impressive 18). Lower it for
  an easier deed within the band; one above the band is warned of, as
  his agreement didn't cover it.
- **Risk to him**: none rolls a simple die; embarrassment or reputation
  a stress die with 1 botch die, injury or imprisonment 3, death 5.

**His Roll** shows the total, the Ease Factor and the die he needs before
you roll.

## Religion tab
<!-- help: tab-religion -->

A character's faith and what it lets him do, and his career in the Church. The tab follows Virtues & Flaws. It is there for a person (not an animal) while a book that gives the faiths their rites is in play (Realms of Power: The Divine, The Church, The Sundered Eagle, The Contested Isle, The Cradle and the Crescent), or for anyone with a grade, an ordination, a petition or a canon case on record. Its icon is his faith's: a church for a Christian, a crescent and star for a Muslim, a Star of David for a Jew, a fire altar for a Mazdean, a tree for a pagan.

**Faith** comes first: his religion and what it gives him. For a Christian with The Church in play, the Church's sections follow: **Holy Orders** and **Ordinations** for one who may hold orders (a clerical Social Status: Clerk, Priest, Religious, Senior Clergy or Mendicant Friar, or a grade or ordination on record), then **Petitions** and the **Canon Court** for any Christian (The Church pp. 33-38, 46-48). A layman begins in orders with an Ordination season on Planning, or by taking a clerical Social Status on Virtues & Flaws.

**You type:** his religion, his birth diocese, standing and benefice, each petition and each case.

**The app works out:** what his faith offers him and whether he may take it, each examination's total and result, what an ordination brings (the grade, a Faith Point, the Social Status and a Reputation), what still stands between him and the priesthood, and each petition's total, who may grant it and whether it is granted.

A character with no use for it can leave this chapter off: see [Interests](help:interests).

**See also:** [Which faith actions can he take?](help:guide-religion), [Virtues & Flaws tab](help:tab-vf), [Planning tab](help:tab-planning)

### Faith
<!-- help: section-char-faith -->

His religion (blank counts as Christian, as most of Mythic Europe is), and for a Christian his patron saint, his Devotions, his mystic path and the saints who have refused his invocations; then his Pious trait and a line on what his faith gives him.

<!-- tui -->
`e` edits his religion. `m` (More) offers what his faith lets him do:
<!-- /tui -->
<!-- gui -->
Edit Religion sits beside the title, with what his faith lets him do:
<!-- /gui -->

- **A Christian:** [Invoke a Saint](help:devotion), Threaten a Saint (only after a saint has refused him), Patron Saint, Devotion Points (with a Devotion, or Pious enough to begin one) and Indulgence, Vigil or Fast (with The Church), [Mystic Path](help:mystic-path) (Pious and tied to the Divine) and its Spiritual Path or Monistic Revelation, [Invoke God's Aid](help:gods-aid) and [Holy Influence](help:holy-influence).
- **A Muslim:** [Invoke Baraka](help:baraka) and [The Hajj](help:hajj), Invoke God's Aid, and Holy Influence for one with spiritual authority.
- **A Jew:** Invoke God's Aid, and Holy Influence for one with spiritual authority (a rabbi over his community).
- **A Mazdean:** invoking a yazata, as a Christian invokes a saint (Invoke a Saint, with The Cradle and the Crescent).
- **A pagan:** the books give pagans no rite like the saints'. His faith is in a magic spirit (a Spirit Votary, DE p. 58) or in faerie (Realms of Power: Faerie p. 134), and his dealings with them are in the Deeds chapter under Dealings with Faerie on the desktop (Ars Fabulosa, A Faerie Bargain, An Offer to Faerie), or More on his record in the terminal.

God's aid is never a grog's, nor one's with Low Self-Esteem, unless he has True Faith (RoP: The Divine p. 41).

## Invoke Baraka
<!-- help: baraka -->

A Muslim seeks a holy forbear's blessing, his baraka, as a Christian invokes a saint (Realms of Power: The Divine pp. 103-105): Communication + Charm + the modifiers + a simple die, against 15 + the storyguide's simple die, rolled in secret. He must be at the forbear's shrine, usually his tomb (tick **At his shrine**); the Qur'an itself may be invoked anywhere. A forbear is never threatened.

**The forbears** are the book's: the Qur'an (Might 100), Muhammad (100), Abraham (75), David (75; the book lists no powers for him), al-Husayn (75), Rabi'a al-'Adawiyya (50), al-Shafi'i (25) and Nur al-Din (25), each with where his baraka is sought and his powers.

**The modifiers** (p. 103): his highest Muslim Personality Trait, + its value (the book doesn't say which traits are Muslim ones, so you choose; Pious is offered first); a Divine aura, +1 a level (the ritual prayer, a Muslim holiday and Ramadan each raise a Muslim Dominion aura by 1, pp. 107-108); his feast day, normally his birthday, +3; a pilgrimage made to his tomb or shrine +2; touching his relic +1, owning it +2; a donation +1 to +3; imminent peril +2; a recent sinful act -1 to -3; no zakat paid within a year -3; a miracle received within a month -5; an unfamiliar forbear -10; and choosing a specific miracle of his, rather than general aid, -5.

**The Baraka** shows the total, the chance and the forbear's powers. **Pray** rolls it; the Diary records it.

## The Hajj
<!-- help: hajj -->

The pilgrimage to Mecca every Muslim who is able makes once, in the first half of Dhu'l-Hijja (Realms of Power: The Divine p. 108). **Complete the Hajj** gives him Pious +3 and 3 Faith Points. Made again, it restores both, but never raises Pious above +3; a Pious already higher stays as it is. The Diary records it, with any notes. Play out the journey itself as a story (or plan its seasons as travel).

## Edit Religion
<!-- help: religion -->

His religion, from the list: Christian, Muslim, Jewish, Mazdean, Pagan or Other. Left blank, he counts as Christian. It decides what the [Religion tab](help:tab-religion) offers him. Biographical Detail edits the same field.

### Holy Orders
<!-- help: section-char-orders -->

His grade (minor orders: doorkeeper, lector, exorcist, acolyte; major orders: sub-deacon, deacon, priest, bishop), his Social Status, birth diocese, the Faith Points his ordinations brought (one each, even for several grades at once, p. 34), his standing and which law he is under: a cleric of any grade is under canon law, not secular law (pp. 34-35).

**The ladder** shows the grades held, the next one, and its examination: Intelligence + Church Lore or Civil and Canon Law + a stress die against the grade's Ease Factor (Doorkeeper 3 and Lector 6 in Church Lore; Exorcist 3 and Acolyte 6 in Civil and Canon Law; Sub-deacon 9, Church Lore; Deacon 9, Civil and Canon Law; Priest 12, Church Lore; a bishop is elected, p. 33). Church Lore is the sheet's Organization Lore: Church.

**Toward Priest** (p. 35): a priest must be 25, freeborn, legitimate, sound of body and mind and educated for his office, and needs a benefice, chaplaincy or curacy free. Each one he fails is flagged (a Dwarf, Lame, Blind or similar Flaw for "sound of body"; Bastard for legitimacy; Slave for freeborn) and needs a dispensation, a petition at Ease Factor 9. The app warns; it never stops the ordination.

**Standing:** In good standing, Irregular (a cleric who has shed blood or committed a grossly immoral crime: he can't use Faith Points until he confesses; no trial needed, p. 37) or Excommunicated (shown while a guilty verdict of excommunication stands against him in the Canon Court).

<!-- tui -->
`e` edits Holy Orders; `m` (More) performs an exorcism, for a clergyman: one in orders, or a Clerk, Priest, Senior Clergy or Mendicant Friar (a monk or nun who is Religious only is not; p. 34).
<!-- /tui -->
<!-- gui -->
Edit Holy Orders sits beside the title, and Perform an Exorcism for a clergyman: one in orders, or a Clerk, Priest, Senior Clergy or Mendicant Friar (a monk or nun who is Religious only is not; p. 34).
<!-- /gui -->

### Ordinations
<!-- help: section-char-ordinations -->

One entry per examination: the grade, the season, the total against the Ease Factor, and the result (p. 34):

- more than double the Ease Factor: ordained, and a Reputation of 1 for knowing the Ability (or a Reputation experience point toward it);
- equal to it, or above it by no more than double: ordained;
- missing it by 6 or less: he still passes, with a Reputation of 1 for ignorance (or a point toward it). Missing by exactly 6 is a judgement call: the book covers "less than 6" and "more than 6", and the app lets it pass;
- missing it by 7 or more: not ordained; he may appeal (a petition, Ease Factor 9) or sit it again another season;
- a botch: not ordained, and he may sit it again only once a petition lets him (Holy Orders shows him barred).

Being ordained brings the grade's Social Status (pp. 25-26, 34), and it replaces his own: a character holds two Social Statuses only where both say they are compatible, and the clergy's don't (DE p. 63), so he never keeps both. The first grade gives Clerk in place of any lay status (Covenfolk, Craftsman...; DE p. 74); Priest replaces Clerk, Religious for a monk, a Mendicant Friar's or a lay status (DE pp. 104, 106; The Church p. 26). The Ordination season offers the swap with **Swap his Social Status for the clergy's**, ticked by default; untick it to leave his status for the troupe to change on Virtues & Flaws. A bishop's Senior Clergy is a Major Virtue (DE p. 107), so the app says to swap it there rather than doing it. Wealthy and Poor aren't Social Statuses and are never touched. A major order means celibacy from then on (p. 35).

An Ordination season (Plan a Season) examines him for the next grade; Add is for recording an ordination from before play, which doesn't change his grade (Edit Holy Orders does).

### Petitions
<!-- help: section-char-petitions -->

A petition to the Church: what was asked, by letter or in an audience, the season, its Petition Total against the Ease Factor, and the result. No die is rolled (p. 48).

### Canon Court
<!-- help: section-char-canon -->

Cases in the Church's courts, the character accused or accusing: the charge (the kinds of case, pp. 37-38), the court (the archdeacon's at his visitation, a rural dean's or parish priest's, the bishop's on appeal, the papal curia), the verdict and the punishment. The judge decides: there is no jury and no roll; about a dozen oath-helpers swearing to the accused's good character acquit him (compurgation). Canon courts shed no blood, and no one need attend one more than two days' travel from his diocese (pp. 35-37). A clergyman a secular court finds guilty is tried again in the bishop's court (p. 35).

## Petition the Church
<!-- help: petition-church -->

Anyone may petition the Church: clergy, peasants, nobles, magi (The Church pp. 46-48). Add on the Religion tab's Petitions makes one. Choose the book's example it is most like (p. 47: 3 a marriage blessing, 6 a parish crypt or library, 9 the cathedral library, an appeal of an ordination exam or a dispensation, 12 rent land to a Hermetic covenant, 15 excommunicate a nobleman, 18 a monastery, 21 a new diocese, 24 change canon law, 30 declare a saint, 42 a crusade), or type the Ease Factor.

**Petition Total:** Communication + Church Lore for a letter (a scribe's Communication + Church Lore may stand in: type his name and total; The Gift doesn't apply), or Presence + Church Lore in an audience (The Gift's penalty applies), plus: many testify +1; magical evidence +1; a holy vision +3; miracles +6; the highest clergy support (+1 a priest or deacon, +3 a senior clergyman, +6 an archbishop or higher) and the highest lay support (+1 a knight, +3 a nobleman, +6 a king, duke, earl or emperor), once each; a donation +1 to +3; each argument, by Civil and Canon Law, Artes Liberales (Logic) or Intrigue, +1 to +3, which counts only if Intelligence + the Ability + a stress die reaches 9 (rolled when the petition is made; a botch makes its bonus a penalty); his Reputation with the Church; spells cast on those deciding (p. 46).

**Who decides** (p. 48): a priest may grant up to 6, a bishop up to 15, the papal curia the rest. One petition a season, usually; it takes no season unless he travels.

**An appeal** against another's granted petition overturns it at that petition's total + 3, and above its total - 3 wins a compromise; -3 if it isn't made in the same season (p. 48).

Untick Made now to keep a petition planned (no total yet).

## Add Canon Case
<!-- help: canon-case -->

The storyguide's record of a case: the charge, whom it is about, whether the character is accused or accuses, the court, the season, whether oath-helpers swore for the accused (compurgation acquits; the form asks when it is set beside a Guilty verdict), the verdict and the punishment (The Church p. 37): a monition (an official warning), public penance, a fine (when penance isn't done), imprisonment in a monastery, the benefice suspended, or excommunication (no sacrament but penance, no consecrated burial, and a clergyman loses his shield from secular justice; lifted by confession and penance), which shows on Holy Orders as his standing. There is no roll: the judge decides.

## Perform an Exorcism
<!-- help: perform-exorcism -->

Any clergyman may exorcise (The Church p. 34). He spends at least one Confidence or Faith Point (+3 each); the Exorcism Total is a stress die + the Points, +1 if he has been ordained exorcist (every grade from exorcist up has been), +1 for holy water and +1 for a crucifix. Exorcism is a Divine power: a Divine aura adds its strength and other realms' auras don't hinder it (DE p. 411). It must reach the Might the demon invested in the energumen, and Penetrate his Magic Resistance if he has any. Roll rolls it; mark the Points spent on the sheet. An Irregular cleric can't use Faith Points (p. 37): the calculator warns.

## Edit Holy Orders
<!-- help: edit-holy-orders -->

His grade (for one held before play; an Ordination season examines him for the next), birth diocese (where he is ordained; elsewhere needs its bishop's leave, p. 33), standing, benefice or office, and whether a botched examination bars him until a petition succeeds.

## Deeds tab
<!-- help: tab-deeds; gui -->

What the character can do in play that the saga's books bring, gathered in
one chapter instead of as buttons on the sections they touch. Each action
sits under the interest it belongs to, beside a line saying what it does:

- **Session & Reputation**: End of Session, Reputation Roll, House Acclaim.
- **Knightly**: Melee Event.
- **Scholarly**: Disputatio, Make a Ligature.
- **Insight**: Font of Knowledge, Divination, Astrology.
- **Mystery Cults**: Experiment on a Script, for a Mystagogue.
- **Tribunal & Order**: Hermetic Letter, Invoke a Broken Oath.
- **Dealings with Faerie**: Ars Fabulosa, A Faerie Bargain, An Offer to
  Faerie.
- **The Infernal**: Confidence through Sin, Infernal Influence, Ars Goetia.
- **Apprenticeship**: Turbulence, The Gauntlet, Lose the Gift.
- **Covenfolk**: Reward or Punish, Pension.

An action shows only while its book is in play and it fits the character
(Disputatio needs someone to dispute with; The Gauntlet, an apprentice), so
a header with nothing to offer is left out. What takes a season (a career,
a season on the tourney circuit, Greek Fire, an apothecary's store) is
in the Planning chapter's A Season's Work instead; the faith's
actions are in the Religion chapter. While the character is In Creation the
chapter only says its deeds wait until the character is In Play. A
character kept as a statblock has no Deeds chapter.

A whole interest can be left off the sheet for a character who will never
take it up: untick it in [Interests](help:interests) on the Manage chapter.

**See also:** [Planning tab](help:tab-planning),
[Interests](help:interests), [How to find an action](help:guide-find-action)

## Interests
<!-- help: interests -->

<!-- tui -->
More (`m`) on a person's record offers **Interests**:
a tick for each kind of deed the saga's books bring, with a line on what
it is: Knightly, Scholarly, Insight, Religion, Agents, Research, Hermetic
Mysteries, Mystery Cults, Craft & Trade, Tribunal & Order, Dealings with Faerie, The Infernal, Apprenticeship and Covenfolk.
<!-- /tui -->
<!-- gui -->
**Interests**, in a person's Manage chapter, opens a window of cards, one
for each kind of deed: Knightly, Scholarly, Insight, Religion, Agents,
Research, Hermetic Mysteries, Mystery Cults, Craft & Trade, Tribunal & Order, Dealings with Faerie, The Infernal, Apprenticeship
and Covenfolk. A card says what the interest is and how many actions it
adds in this saga, counting those whose book is in play, so one may read
"2 actions, 4 more with other books". Click a card to see it in the
Inspector: who it is for, each action with a line on what it does, whether
that action is on the Deeds chapter or on Planning in A Season's Work, and
which book the others wait for. Each card's switch, and the Inspector's,
turns the interest off or on, and a card turned off fades. Save keeps
your choices. Leaving with changes unsaved, by Cancel, the close button or
Esc, asks first: Discard Changes leaves things as they were, and Keep
Editing goes back to the window.

A card whose books aren't in play is faded and its switch is locked. The
character's choice is kept, so the interest comes back as you left it when
a book arrives.
<!-- /gui -->

Turn off the ones the character won't take up, a magus's Knightly or a
blacksmith's Scholarly, and their actions leave the sheet: the Deeds
chapter's heading, A Season's Work and More alike. Session & Reputation
(End of Session and the Reputation rolls) is every character's and is
always on.

Turning off **Religion** takes the whole [Religion chapter](help:tab-religion)
off the sheet, with Pilgrimage on Planning, for a character whose faith
will never come up; their religion stays on their Biography. Its count goes
by the character's faith as well as the books, as in "15 actions for a
Christian", and the Inspector lists those of other faiths. A Church career
(orders, a clerical Social Status, a petition or a canon case) keeps it on:
the switch gives way to "On for a Church career", and if a character with
Religion off takes up a career, the chapter comes back.

**Agents** and **Research** work the same way, each hiding its chapter: an
agent on record, or research under way, keeps it on. Research and Hermetic
Mysteries are for magi, so other characters don't see them.

**A covenant has Interests too**, on its own Manage chapter (More on its
record in the terminal), and its Creation Worksheet has a Review Interests
step for them. **Manors** hides the Manors chapter and **Ships** the Ships
list on Possessions, for a covenant that will never take them up; a manor
or a ship on record keeps them on. Hermetic Projects need no card: their
chapter waits until a project begins.

Everything starts ticked, so nothing goes missing until you say so; a new
character's Creation Worksheet has a Review Interests step for it. Ticking
an interest doesn't offer what the rules don't: An Artist's Career still
needs a Craft or Profession, and every action still needs its book in play.

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

### A Season's Work
<!-- help: section-char-season-work; gui -->

Below This Season on the Planning chapter: the season-long work the saga's
books bring, each button beside a line saying what it does. A season on
the tourney circuit, Labor Points from a story, investing time or money,
selling finished goods, an apothecary's store, Greek Fire, an artist's or
a scholar's career, Turbulence, a grog's story experience, a pilgrimage
and Philosophic Alchemy show here while their book is in play and they
fit the character. This Season's own buttons keep to planning the season
(Plan, Edit, Clear, and copying). The terminal offers the same in More on
This Season.

**See also:** [Deeds tab](help:tab-deeds), [Planning tab](help:tab-planning)

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

Below the Labor Points line it says what they are worth in money to the
business: 9 Labor Points are about a quarter of a year's income (City & Guild
p. 40, as the Errata p. 56 corrects it), so to a Trivial income (10 pounds a
year) they are worth about 2½ pounds, to a Lesser one (40) about 10, to a
Greater one (250) about 63, rounded to the nearest pound. The income source
is the band the Social Status Virtue buys (p. 37: Laborer, Journeyman and
Craftsman Trivial; Merchant, Guild Master and an expensive Craftsman Minor;
Senior Master Lesser; Merchant Adventurer, Factor and Guild Dean Typical;
Capo Greater); where a Virtue buys either of two, the poorer is assumed
until you choose the other in either form below. A merchant's open
investments are listed too: a speculation and what it pays a year, an
introduction and when it pays back, a brokered marriage's Social Contacts, a
charity and the crowd it can call.
<!-- tui -->
More (`m`) here offers **Labor Points from a Story** and, for a trader or
anyone with Labor Points, **Invest Time or Money**.
<!-- /tui -->
<!-- gui -->
**Labor Points from a Story** and **Invest Time or Money** sit beside Plan,
Edit and Clear.
<!-- /gui -->

Turbulence is offered here too: an apprentice assisting in a stressful laboratory season checks for one midway through it (Apprentices p. 56).

The seasons of The Mysteries Revised Edition's Hermetic Mysteries:

- **Invent Rotes (Hermetic Numerology)** (TMRE pp. 92-93): choose the
  Rotes' Technique and Form and type the Rotes, "Name: level", with
  "(text)" after one invented from a Lab Text. The Rote Lab Total is the
  laboratory's Lab Total plus Artes Liberales (at most Magic Theory) and the
  book bonus; no Rote may be above a fifth of it (rounded up), and each
  costs twice its level (its level from a Lab Text), all within the total.
  The Rotes invented are kept as finished Rote records and shown with the
  Casting Scores.
- **Bind an enchanted structure (Hermetic Architecture)** (TMRE pp. 97-99):
  name the structure, type its highest component effect's level and choose
  its Size multiplier (5 a small room, 6 a Room, 7 a Structure, 8 a
  Boundary, 9 and 10 larger), and the days recomputing the components'
  places takes after a miss (1 for posts in a field to 30 for niches in
  a building; blank is a month). The season places the components,
  Intelligence + Artes Liberales against 6 + Size; each failure costs
  those days, and he tries again while the season lasts, its notes giving
  the misses and the day the components were placed (a botch is a
  disaster). Then he
  casts Bind the Mystical Structure, a Rego Vim Ritual of at least the
  effect's level + 5, a magnitude more for a Structure and two for a
  Boundary, paying a pawn of Vim a magnitude from the vis chosen.

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

## Turbulence
<!-- help: turbulence -->

A Gifted child's untrained Gift lashing out (Apprentices pp. 22-24). Choose
why it is checked:

- **A botched stressful roll that includes magic** (how loosely "includes
  magic" is read is the troupe's call, p. 22).
- **A potential botch on magic**, for a character with Turbulence Prone
  (p. 12): checked whether or not he botched, and he can't control it.
- **Forced**: a Confidence Point spent to call one up at will (p. 24).
- **Midway through a stressful laboratory season**, offered while he is
  planned to Assist and not yet checked this season (p. 56): the parens
  experimenting, more than 10 pawns of vis, odd hours or a Lab Total barely
  enough make a season stressful.

The incurring roll is Intelligence + stress die + the aura's modifier for a
Magic power, less half the level of an Aegis of the Hearth he had no part
in; it must beat both the storyguide's stress die and his age. Only the
storyguide's die there is no-botch (p. 22): the player's die, and both
dice of the control roll, are ordinary stress dice that can botch. A
botched die counts 0, the inspector and the Diary say which die botched,
and what else the botch brings is the troupe's call. A child's
Characteristics are used as the sheet has them, the Aging Chart's
modifier already in them (it counts once, p. 23). Controlling it is Stamina +
stress die against Warping Score + stress die (Errata p. 83); half the
difference is the effect's magnitude (the book gives no rounding for an
odd difference: the app rounds down, its own gap-fill), any Technique and Form (an Affinity or
Puissant Art a good choice). Controlled, the player chooses the effect;
uncontrolled, the storyguide. It has no Penetration unless he has the
Ability: its score x (1 + a sympathetic multiplier). More Confidence may be
spent on either roll, +3 a point, at most his Confidence Score on one roll.

In the laboratory an uncontrolled Turbulence halves his aid to the Lab
Total; for a storyguide character, tick the box to roll for losing the
Gift as well: on a 0, a botch die for every 10 of the parens' Lab Total, and
any 0 loses it (p. 59; then use Lose the Gift).

**Roll** rolls it and writes it in the Diary.

## The Gauntlet
<!-- help: gauntlet -->

The parens' test of his apprentice (Apprentices pp. 59-61), for a character
with the Apprentice Social Status. Choose how it is decided:

- **Played as a story**: the parens says whether he passed.
- **Passed without a story**, once he has served his 15 years.
- **Rolled**: Intelligence + an Ability fitting his House + stress die
  against 9; a botch means something dire happened.

Failed, he spends another year as an apprentice; after three failures the
Quaesitores set his Gauntlet. Kept more than 20 years is a low crime in many
Tribunals: convicted, the parens forgoes the Gauntlet and pays a rook of vis
(10 pawns) for each year past 15. Passed, Hermetic Magus replaces
Apprentice, the character becomes a magus, and after the Oath he has Parma
Magica's final key: until then his Parma Magica gives no Magic Resistance
(DE p. 169). **Record** writes the result in the Diary.

## Lose the Gift
<!-- help: lose-the-gift -->

Failing an apprentice (Apprentices pp. 58-59): always the player's choice.

- **Lost for good**: The Gift (and a Gentle or Blatant Gift) is taken away;
  he casts no spells and works no magic, and his Supernatural Virtues and
  Abilities stop working. Failed Apprentice replaces Apprentice, and a
  magus's record becomes a companion's.
- **Suppressed**: he gains the Major Hermetic Flaw Suppressed Gift; his
  existing Supernatural Virtues and Abilities still work, but he gains no new
  Supernatural or Hermetic Virtues while it lasts. How it returns is the
  troupe's story.

**Save** makes the change and writes the cause in the Diary.

## Learn a Cantation
<!-- help: learn-cantation -->

An optional rule (Apprentices p. 46), with the saga option Learning
cantations in play on: a spontaneous spell cast in play at least as many
times as its level may be bought as a formulaic spell with that adventure's
experience, one point a level. Choose the spell (any formulaic spell he
doesn't know: the book sets no level cap, only the times cast; never a
Ritual spell, whose effects spontaneous magic can never replicate, DE p.
311) and how often he cast it; **Learn** adds it to his Known Spells. Give
that much less of the adventure's experience to his Abilities and Arts.
The rule is for adult magi as well as apprentices (p. 46), so it is
offered on any character's Known Spells.
