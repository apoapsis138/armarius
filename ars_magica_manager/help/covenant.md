# Covenant sheet
<!-- help: covenant -->

The covenant sheet holds everything that belongs to the covenant as a
whole: its attributes, its people, what it owns, its money, its library and
its history.
<!-- tui -->
It opens when you choose a covenant in the tree. Under the
covenant's node, the tree lists its **Characters** and **Laboratories**,
each of which has a sheet of its own.
<!-- /tui -->
<!-- gui -->
It opens when you choose the covenant's card on the saga's page. Its
characters and laboratories have pages of their own: their cards are in
the **People** and **Laboratories** chapters, and clicking one opens it.
<!-- /gui -->

<!-- tui -->
The top panel, with the covenant's name, stays in view above the tabs
whichever tab is open. The tabs are numbered, and the number keys `1` to `9`
open them; the last, Secrets, is the storyguide's alone. Most tabs have a details panel docked at the bottom: choose a row
and it shows that row's figures and, where there is one, its rules text and
where in the books it comes from.

More (`m`) on the top panel offers **In Creation / In Play**, which switches
the covenant between being built and being played, and, while it is In
Creation, the **Creation Worksheet**, which walks through building a
covenant step by step. The same switch and worksheet are the buttons beside
**Edit (e)** in the top panel. Export and Update from a File are in More
there too. A familiar is bound on its magus or in their laboratory.
<!-- /tui -->
<!-- gui -->
The header, with the covenant's name, its Tribunal and season, the Aegis,
the Living Conditions, and the Aura and Loyalty as seals, stays in view
above the chapters. The rail on the left lists the chapters: **Charter**,
**People**, **Covenfolk**, **Laboratories**, **Possessions**, **Treasury**,
**Library**, **Seasons**, **Diary**, **Build**, [**Secrets**](help:tab-secrets)
and **Manage**. The help
below names three of them as the terminal's tabs: Charter is the Attributes
tab, Covenfolk the Inhabitants tab and Treasury the Economics tab. Click a row or card and
the inspector on the right shows its figures and, where there is one, its
rules text and where in the books it comes from.

In the header, **In Creation** or **In Play** switches the covenant between
being built and being played, and, while it is In Creation, **Worksheet**
beside it opens the **Creation Worksheet**, which walks through building a
covenant step by step. The **Manage** chapter holds Export, Update from a
File and Delete. Each group of the People chapter (Magi, Companions, Grogs)
ends in a blank card, New Magus, New Companion or New Grog, and the
Laboratories chapter ends in New Laboratory; what they make belongs to the
covenant. A familiar is bound on its magus or in their laboratory.
<!-- /gui -->

How much of a covenant is written down is its detail level: a **Line** (a
name, its Tribunal and who they are), a **Sketch** (its magi, what matters
to it and its attitude to each player covenant) or **Full** (the whole
sheet). Only a full covenant is played: a Line or Sketch covenant is left
out of upkeep, income, Loyalty and the seasons, though its magi still count
toward its Tribunal's votes. **Promote** and **Demote** move it one level;
nothing is deleted. Promoting a sketch to Full moves it In Creation and
opens the Creation Worksheet on what the sketch already has.

A covenant may be the vassal of another, sworn to it by an oath: choose
its liege in **Vassal of** in the covenant's Edit, and write the oath's
duties beside it. The sheet then says **Vassal of** its liege, and the
liege's sheet lists its **Vassals**, while both are in the same Tribunal.
Ticking **Add the oath's Boons and Hooks** adds Beholden and Powerful Ally
to the vassal and Favors Owed and Protector to its liege, each naming the
other covenant; ones already taken aren't added twice. A Tribunal following
Hibernia's customs recognises no vassal covenants, so Edit refuses a liege
in the same Hibernian Tribunal.
<!-- tui -->
Both are in More (`m`) on the top panel.
<!-- /tui -->
<!-- gui -->
Both are in the **Manage** chapter.
<!-- /gui -->

A covenant is a **player covenant** when the troupe plays it ("Played by the
troupe" in its Edit): other records' attitudes point at the player
covenants. A covenant you make is played; a sketch covenant usually isn't.
Every list of covenants puts the player covenants first, each marked
with ✦, above the others.
<!-- gui -->
On the World page their cards carry gold corners, and a divider stands
before the rest.
<!-- /gui -->

**See also:** [Saga](help:saga), [Keys](help:keys),
[Advancing a season](help:advance-season), [How to manage the covenant](help:guide-covenant).

### The covenant panel
<!-- help: section-cov-info -->

<!-- tui -->
The panel at the top of the sheet. Saga, Storyguide, Current Season and
Current Year come from the saga and are shown dimmed: change them on the
saga, not here. Everything else is typed with `e` (Edit Covenant): the name,
<!-- /tui -->
<!-- gui -->
On the desktop this is the header at the top of the page and **The
Covenant** section at the start of the Charter chapter. The season shown comes from the saga:
change it on the saga, not here. **Edit Covenant** beside The Covenant
types the rest: the name,
<!-- /gui -->
Tribunal, Year Founded, Aegis of the Hearth and its Penetration, the two
Living Conditions, the base Aura, Aura Realm and Covenant Season. The app
works out the Aura shown, adding any Boon that raises it to the base you
typed, and that total is the aura every laboratory of the covenant starts
from. Living Conditions (Mundane) feeds Loyalty, both Living Conditions are
used in the aging rolls at the end of the year, and Covenant Season decides
how many points each inhabitant is worth on the Economics tab. While the
covenant is In Creation, the
<!-- tui -->
panel
<!-- /tui -->
<!-- gui -->
header
<!-- /gui -->
also shows the Build Points spent.

## Overview tab
<!-- help: tab-cov-overview -->

A Line or Sketch covenant opens here, beside its Diary: who it is in the
saga (typed in its Edit), its magi and their votes, What Matters, its
attitude to each player covenant, the favours owed and its links.
<!-- gui -->
On the desktop this is the **Sketch** chapter.
<!-- /gui -->
A Line covenant has only its attitude, favours and links.

**You type:** its magi (a line or a sketch each), how many more are
unnamed, What Matters, and each reason its attitude moved.

**The app works out:** its votes, one for each magus named or not, and
each attitude from where it started and every reason since.

### Magi
<!-- help: section-cov-magi -->

The magi whose covenant this is, at any detail, with their House and
votes, then how many more are unnamed (set in the covenant's Edit). Add
writes a new magus in as a line or a sketch; Edit changes their name,
House, detail and part in the saga; Delete removes them from the saga,
saying first what goes with them. Proxies are carried at each Tribunal
meeting, not here.
<!-- tui -->
To promote a magus to a full character, open them in the tree.
<!-- /tui -->
<!-- gui -->
Click a magus to see their statblock in the inspector.
<!-- /gui -->

### What Matters
<!-- help: section-cov-what-matters -->

Short entries, one a line, about what the covenant cares for: its vis, its
library, its Boons and Hooks. Start a line with a word and a colon ("Vis:
Vim 6 a year") to head it.

### Attitude
<!-- help: section-attitudes -->

How the record feels toward each player covenant, from −3 (Hostile) to +3
(Allied). Each starts somewhere (the "Started" row; Edit it to change it),
and every reason written down moves it: +1, −1 or more. The score is
worked out from those, never typed, and kept within −3 to +3. Add a reason
for what happened and when; delete one and the score moves back.

### Favours
<!-- help: section-favours -->

Favours owed: what for, who owes whom, and since when. A favour stays open
until a season it was repaid in is set, then shows dimmed.

### Links
<!-- help: section-links -->

Links to other records of the saga (a character, covenant, book,
possession or familiar), each with a short note. Below them, unselectable,
are the records that link here.

## Attributes tab
<!-- help: tab-cov-attributes -->

What the covenant is like: its description, its Reputations, and its Boons
and Hooks.
<!-- gui -->
On the desktop this is the **Charter** chapter.
<!-- /gui -->

**You type:** the description, each Reputation and its score, and the
detail of each Boon or Hook you take from the catalogue.

**The app works out:** the points the Boons cost and the Hooks provide, and
warns, above the two lists, about Boons and Hooks that cannot be taken
together and about income that a Poverty Hook does not allow. Boons and
Hooks follow Ars Magica Definitive Edition, Chapter 6: Covenants.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants) (Loyalty),
[Economics tab](help:tab-cov-economics),
[Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Description
<!-- help: section-cov-description -->

Free text about the covenant: where it is, what it looks like, its history.
<!-- tui -->
`e` opens it for editing.
<!-- /tui -->
<!-- gui -->
**Edit Description** beside The Covenant opens it for editing.
<!-- /gui -->
Nothing on the sheet is worked out from it.

### Reputations
<!-- help: section-cov-reputations -->

The covenant's Reputations, each with a score from -3 to +3. Each one also
records whether the covenant knows about it: an unknown one is marked
"(not known by the covenant)" on its row. Every point of a bad Reputation
the covenant knows about costs 5 Loyalty points on the Inhabitants tab; good
Reputations and unknown ones cost nothing. A Reputation may also say its type (Hermetic, Local, Noble, Academic,
Ecclesiastical or Infernal) and how far it reaches, both shown in
brackets after its score.

### Boons
<!-- help: section-cov-boons -->

<!-- tui -->
The covenant's Boons, chosen from the catalogue with `a` and edited with `e`
to give their detail and description, and to change what they name. The
picker shows the highlighted Boon's rules, requirements and book under the
list. The title shows the points they cost.
<!-- /tui -->
<!-- gui -->
The covenant's Boons, chosen from the catalogue with **Add** and edited
with **Edit** to give their detail and description, and to change what
they name. The points they cost
are under the title.
<!-- /gui -->
That total and the Hooks' total share one colour: plain while there are
points still to spend, the success colour when they match, and the error
colour when the Boons cost more than the Hooks provide. Some Boons change
figures elsewhere: an Aura Boon raises the covenant's Aura, a Style of
Governance Boon fills in the Type of Governance under Loyalty, and a
Boon that enlarges the buildings adds to the Buildings cost on the
Economics tab. A Hidden Resources Boon holds 250 Build Points the magi can't
use yet: its row shows how many are unlocked ("120/250 BP"), and
its details list the Story Events that unlocked them (see the
[Diary tab](help:tab-cov-diary)). Its description is the place to note
what the resources are, decided ahead or later.

### Hooks
<!-- help: section-cov-hooks -->

<!-- tui -->
The covenant's Hooks, chosen from the catalogue with `a` and edited with
`e`. The title shows the points they provide, coloured together with the
Boons' total.
<!-- /tui -->
<!-- gui -->
The covenant's Hooks, chosen from the catalogue with **Add** and edited
with **Edit**. The points they provide are under the title, coloured
together with the Boons' total.
<!-- /gui -->
A Hook the catalogue allows to be unknown can be marked so,
and then counts a fixed number of points shown on its row. A Story Event in
the Diary can be linked to a Hook, and its details then say how many
stories have been told against that Hook so far. An Illusory Resources Hook
stands for 250 Build Points of improvements that don't really exist: its
row shows how many have been found out ("60/250 BP"), and its details list
the Story Events that revealed them.

## Inhabitants tab
<!-- help: tab-cov-inhabitants -->

Who lives at the covenant, and how loyal they are.
<!-- gui -->
On the desktop this is the **Covenfolk** chapter.
<!-- /gui -->

**You type:** the Loyalty choices (Equipment, Money, Pension, Familiarity,
Actions and events, Magical Influence, and the Type of Governance when no
Boon sets it), Other People, the Miscellaneous figures, and each inhabitant
you add.

**The app works out:** the magi and companions, listed from their own
character sheets; each list's headcount; the Teamsters and Servants the
covenant needs; Total Inhabitants; and all of Loyalty, from the magi's
Gifts, the Living Conditions, the salary, the specialists' roles, known bad
Reputations and the Diary. The Loyalty rules come from the Covenants
supplement.

**See also:** [Seasons tab](help:tab-cov-seasons),
[Economics tab](help:tab-cov-economics), [Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Loyalty
<!-- help: section-inh-loyalty -->

The covenfolk's Prevailing Loyalty. Base Loyalty Points is the average of
the magi's Gifts (an ordinary Gift is -30, a Blatant Gift -105, a Gentle
Gift or none 0). Total modifiers adds up the column on the right: Living
Conditions (10 for each point of Living Conditions (Mundane)), Equipment and
Money from the choices you make with
<!-- tui -->
`e`
<!-- /tui -->
<!-- gui -->
**Edit** beside Loyalty
<!-- /gui -->
(a Pension adds to Money),
Specialists (the Presence and Ability of any Steward, Chamberlain, Turb
Captain or Autocrat), Familiarity, Reputation, Actions and events (the
Diary's Loyalty points plus any you type), and Magical Influence. Current
Loyalty Points is the sum, and the Prevailing Loyalty Score comes from it
by the same table as Ability advancement.

### Inhabitants
<!-- help: section-inh-population -->

A summary of the population. The numbers of Teamsters, Servants and
Laborers are counted from the Other Covenfolk list, by each entry's
Covenant Role; the number needed is worked out from the points of everyone
else, and each pair shows in the success colour when met and the error
colour when not. Other People, typed with
<!-- tui -->
`e`,
<!-- /tui -->
<!-- gui -->
**Edit Inhabitants** beside The Household,
<!-- /gui -->
is for anyone you do not want to list one by one. Total Inhabitants adds Other People to every
list's headcount except Livestock.

### Miscellaneous
<!-- help: section-inh-misc -->

Aging for Magi and for Mundane, and the numbers of Magic Laborers, Servants,
Teamsters and Turbula, all typed with
<!-- tui -->
`e`.
<!-- /tui -->
<!-- gui -->
**Edit Miscellaneous** beside The Household.
<!-- /gui -->
The app keeps them as a record
and does not work anything out from them.

### Magi
<!-- help: section-inh-magus -->

Every magus whose character sheet belongs to this covenant is listed
automatically, with their House, year of birth and Gift taken from the
sheet. You can also add a magus who has no sheet, typing those details
yourself.
<!-- tui -->
`e` on a listed magus edits only the covenant's own notes about
them. `d` on a listed magus does not delete anyone: it marks them as
departed, so they stop counting as an inhabitant (and leave the Seasons
tab) while staying in the covenant on their sheet. `a` offers every
magus of the saga who isn't on the list: one taken off earlier counts
again, and one from another covenant moves here (it asks first). More's
**Restore** also brings a departed magus back.
<!-- /tui -->
<!-- gui -->
**Edit** on a listed magus edits only the covenant's own notes about
them. **Delete** on a listed magus does not delete anyone: it marks them as
departed, so they stop counting as an inhabitant (and leave the Seasons
chapter's lists) while staying in the covenant on their page. **Add** offers
every magus of the saga who isn't on the list: one taken off earlier counts
again, and one from another covenant moves here (it asks first).
<!-- /gui -->

### Companions
<!-- help: section-inh-companion -->

Companions (and Mythic Companions) whose sheets belong to this covenant are
listed automatically; companions without a sheet can be added by hand. Each
can have a Responsibility and a Covenant Role. A Steward, Chamberlain, Turb
Captain or Autocrat earns the covenant a Loyalty bonus of Presence plus the
role's Ability, read from the character sheet. As with magi,
<!-- tui -->
`d` marks a listed companion as departed, and `a` (or More's
**Restore**) brings them back.
<!-- /tui -->
<!-- gui -->
**Delete** marks a listed companion as departed, and **Add** brings them
back.
<!-- /gui -->

### Specialists
<!-- help: section-inh-specialist -->

Covenfolk with a particular job.
<!-- tui -->
`a`
<!-- /tui -->
<!-- gui -->
**Add**
<!-- /gui -->
first offers the covenant's grogs that
are not yet on any list, or a new person who has no sheet. A specialist can
hold one of the Covenant Roles that earn a Loyalty bonus, as companions can;
for one without a sheet you type the Presence and Ability the bonus comes
from. Every specialist counts towards the points of inhabitants.

### Craftspeople
<!-- help: section-inh-craftsperson -->

Craftspeople, added from the covenant's unassigned grogs or as new people.
You give each one a crafting skill (or link it to an Ability on their
sheet), a Field of Work, whether they are rare, and a Quantity. Their Field
of Work decides which cost they save on the Economics tab: a common
craftsperson saves 1 plus half their skill a year, a rare one their skill.
A craftsperson working on Books saves nothing but adds to Writing
Materials.

### Turb
<!-- help: section-inh-turb -->

The covenant's soldiers, added from its unassigned grogs or as new people,
with a Responsibility and a Quantity. They count towards the points of
inhabitants, and so towards the yearly costs on the Economics tab.

### Other Covenfolk
<!-- help: section-inh-inhabitant -->

Everyone else who lives at the covenant, in one list. Each entry needs a
Covenant Role (Laborer, Servant, Teamster or Dependent) and can stand for
several people through its Quantity. The Inhabitants summary counts the
Laborers, Servants and Teamsters from here, and each Laborer saves on
Provisions on the Economics tab.

### Horses
<!-- help: section-inh-horse -->

The covenant's horses, with a Quantity. Each counts as one point of
inhabitants, whatever the Covenant Season.

### Livestock
<!-- help: section-inh-livestock -->

The covenant's animals, kept here for convenience. Livestock are not
inhabitants: they count towards neither Total Inhabitants nor the points of
inhabitants.

## Seasons tab
<!-- help: tab-cov-seasons -->

The covenant's planning board: everyone at the covenant and what each has
planned for the current season, in one place. Each title counts how many
are planned, and the
<!-- tui -->
details panel
<!-- /tui -->
<!-- gui -->
inspector
<!-- /gui -->
shows the chosen person's plan in full.
People marked departed on the Inhabitants tab are left out.
<!-- gui -->
On the desktop, the Seasons chapter also draws a timeline of everyone's
seasons below the lists; click a season on it to read it in the inspector.
<!-- /gui -->

**You type:** each magus's and companion's plan for the season, and each
grog's yearly update.

**The app works out:** nothing on this tab itself. When you
<!-- tui -->
press `t` to advance the season,
<!-- /tui -->
<!-- gui -->
advance the season with **Advance Season** in the top bar,
<!-- /gui -->
every plan is worked out and applied, and someone with
nothing planned gains nothing that season. At the end of Winter the year
closes: before the date moves on, if any covenant spends more than it earns
the app asks whether to stop and balance the books first; then each
covenant's surplus is added to its Wealth and its Emergency Savings start
again at 0. A deficit is never taken from Wealth by itself.

**See also:** [Planning a season](help:plan-season),
[A grog's year](help:grog-year), [Advancing a season](help:advance-season),
[Economics tab](help:tab-cov-economics), [How to plan and run a season](help:guide-seasons).

### Magi
<!-- help: section-cov-seasons-magus -->

The covenant's magi, each with what they have planned this season or
"nothing planned".
<!-- tui -->
`a` or `e` opens the chosen magus's season plan, the same
dialog as on their own sheet; `d` clears the plan after asking first.
<!-- /tui -->
<!-- gui -->
**Plan** opens the season plan of the magus last clicked, the same form as
on their own page; **Clear** clears the plan after asking first.
<!-- /gui -->

### Companions
<!-- help: section-cov-seasons-companion -->

The covenant's companions and Mythic Companions, planned the same way as
the magi:
<!-- tui -->
`a` or `e` plans the chosen companion's season and `d` clears the
plan.
<!-- /tui -->
<!-- gui -->
**Plan** plans the chosen companion's season and **Clear** clears the
plan.
<!-- /gui -->

### Grogs
<!-- help: section-cov-seasons-grog -->

The covenant's grogs. They are not planned season by season but "updated
yearly":
<!-- tui -->
`a` or `e`
<!-- /tui -->
<!-- gui -->
**Plan**
<!-- /gui -->
sets up the chosen grog's yearly update, whose training,
practice and exposure experience is applied at the end of Winter.


## Ahead for the covenant
<!-- help: section-cov-ahead -->

What is coming that concerns the covenant, season by season: its fairs'
income rolls, its people's aging and returns from Twilight, its
Tribunal's meetings, the region's threats and places, and your calendar
entries for it or for the whole saga. It looks as far ahead as the
saga's [Looking Ahead](help:section-ahead).

**You type:** your own calendar entries: Add one (it is for this
covenant), and Edit or Delete it. A row worked out from another record
is changed on that record.

## Possessions tab
<!-- help: tab-cov-possessions -->

What the covenant owns: land, sanctums, arms and armour, vis, other items
and enchanted devices.

**You type:** each possession and its details.

**The app works out:** the sanctums of the covenant's laboratories, listed
automatically; the book figures of a weapon or armour chosen from the
catalogue; and, from all of these, the points of laboratories and of
weapons and armour that drive costs on the Economics tab.

**See also:** [Economics tab](help:tab-cov-economics),
[Build tab](help:tab-cov-build), [Diary tab](help:tab-cov-diary), [How to manage the covenant](help:guide-covenant).

### Properties and Land
<!-- help: section-pos-property -->

Land and buildings the covenant holds, each with a Location, Dimensions,
who lives there and a description. These are a record: nothing is worked
out from them.

### Sanctums
<!-- help: section-pos-sanctum -->

Every laboratory of the covenant is listed here automatically, with its
owner, Quality and Upkeep taken from the laboratory, and cannot be deleted
here (move a laboratory to another covenant from the laboratory itself). For a
listed laboratory you set only its Usage (light, standard or heavy). You
can also add sanctums by hand, typing their Quality and Upkeep. Each
sanctum's Upkeep and Usage give its points of laboratories, which set the
Laboratories cost on the Economics tab.

### Weapons
<!-- help: section-pos-weapon -->

The covenant's armoury. Choose a weapon from the catalogue and its book
figures are filled in, or leave it custom and type them. Its Type and
Quality, times the Quantity, give its points of weapons and armour, which
set the Weapons cost on the Economics tab.

### Armor
<!-- help: section-pos-armor -->

The covenant's armour, chosen from the catalogue by Material or typed as
custom, with its Type (partial or full), Quality, Quantity, Protection and
Load. Like weapons, its points feed the Weapons cost on the Economics tab.

### Vis Sources
<!-- help: section-pos-vis_source -->

Places that yield raw vis, each with its Art, the Season it is harvested
and the pawns it gives. When that season is advanced, the pawns are added to
the covenant's Raw Vis Stores and the Diary records the harvest. A source
can be marked as a Contested Resource (advancing then asks whether it was
secured once its security lapses, and an unsecured one gives nothing) or as
a Dwindling Resource, which loses a tenth of the pawns it gave when it
began dwindling at the end of each year, so it is gone after ten years.

### Raw Vis Stores
<!-- help: section-pos-vis_store -->

The covenant's raw vis, by Art, with where it is kept: the covenant itself,
one of its laboratories or one of its characters. Harvests from the Vis
Sources land here.
<!-- tui -->
More's [Give](help:give) sends pawns from the chosen store to
another covenant, laboratory or magus, and both sides' Diaries record it.
<!-- /tui -->
<!-- gui -->
**Give**, beside Add, Edit and Delete, sends the pawns of the store last
clicked to another covenant, laboratory or magus ([Give](help:give)), and
both sides' Diaries record it.
<!-- /gui -->

### Items
<!-- help: section-pos-item -->

Anything else the covenant owns, with a Quantity and a description. These
are a record only.

### Enchanted Devices
<!-- help: section-cov-devices -->

The enchanted devices the covenant holds, each with its instilled effects
listed beneath it. The app works out a device's capacity, each effect's
level and vis, and a Charged Item's charges, and warns when something does
not add up, following Ars Magica Definitive Edition, Chapter 8: Laboratory.
<!-- tui -->
More's **Instill an Effect** adds an effect to the chosen device (an
invested device takes any number, others only one), and **Use a Charge**
takes a charge off the chosen Charged Item.
<!-- /tui -->
<!-- gui -->
**Instill**, beside the section's title, adds an effect to the device last
clicked (an invested device takes any number, others only one), and **Use
Charge** takes a charge off the Charged Item last clicked.
<!-- /gui -->

## Economics tab
<!-- help: tab-cov-economics -->

The covenant's yearly finances: what it earns, what it spends, what it
saves, and what it has in store.
<!-- gui -->
On the desktop this is the **Treasury** chapter: the year's income,
expenditure and balance at the top, then Wealth and the tables.
<!-- /gui -->

**You type:** Wealth, the sources of income, Tithes, Inflation and Sundry,
Magic savings, Emergency Savings, and a note on any row.

**The app works out:** everything else, from the rest of the sheet: the
points of inhabitants, laboratories and weapons and armour, every
calculated cost, the savings from laborers and craftspeople, Total Income,
Total Expenditure and the Surplus/Deficit. Every figure is a whole number,
and changes anywhere on the sheet show here at once. The finance rules come
from the Covenants supplement.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants),
[Possessions tab](help:tab-cov-possessions),
[Seasons tab](help:tab-cov-seasons) (the end of the year), [How to manage the covenant](help:guide-covenant).

### Wealth
<!-- help: section-eco-wealth -->

The totals. On the left, the points of inhabitants, laboratories and
weapons and armour that the costs are worked out from, and Wealth, the
pounds in store, which you type with
<!-- tui -->
`e`. **Give Silver** (More, `m`) gives pounds to a character or another
covenant ([Give](help:give)).
<!-- /tui -->
<!-- gui -->
**Edit** beside Wealth. **Give Silver**, beside it, gives pounds to a
character or another covenant ([Give](help:give)).
<!-- /gui -->
On the right, Total Income, the
expenditure before and after cost savings, and the Surplus/Deficit. At the
end of each year the surplus is added to Wealth; a deficit is not taken
from it unless you choose to (see Cost Savings).

### Sources of Income
<!-- help: section-eco-income -->

Each enterprise the covenant lives on, with its Type (Lesser, Typical,
Greater or Legendary). Leave Current Income blank to use the Type's usual
income. A source can be marked as a Contested Resource, which gives nothing
until it is secured, or a Dwindling Resource, which loses a tenth of the
income it gave when it began dwindling at the end of each year (gone after
ten years).
<!-- tui -->
More's **Improve Income** applies one year's Income Modification to the
chosen source:
<!-- /tui -->
<!-- gui -->
**Improve**, beside the section's title, applies one year's Income
Modification to the source last clicked:
<!-- /gui -->
pick an effect, see the
projected income, and confirm to set the new income and record a note.

### Yearly Expenditure
<!-- help: section-eco-expenditure -->

What the covenant spends each year, by category. Buildings, Consumables,
Laboratories, Provisions, Wages, Weapons and Writing Materials are worked
out from the points of inhabitants, laboratories and weapons and armour
(Wages also follows the salary chosen under Loyalty, and building Boons add
to Buildings);
<!-- tui -->
`e` on those rows edits only their note. Tithes, Inflation
and Sundry are typed with `e` (Sundry is at least 1 pound a year). The
details panel shows how the chosen row was worked out.
<!-- /tui -->
<!-- gui -->
**Edit** on those rows edits only their note. Tithes, Inflation and Sundry
are typed with **Edit** (Sundry is at least 1 pound a year). The inspector
shows how the row clicked was worked out.
<!-- /gui -->

### Cost Savings
<!-- help: section-eco-savings -->

What the covenant saves. Laborers save on Provisions and craftspeople on
the category of their Field of Work, each up to the limit shown in its
details; both are worked out from the Inhabitants tab. Magic savings
is typed: work out what the covenant's magic saves and enter the total.
Emergency Savings is money drawn from Wealth to cover a deficit. While the
covenant runs at a deficit the row says so (or that the covenant is broke
when Wealth cannot cover it), and
<!-- tui -->
`e`
<!-- /tui -->
<!-- gui -->
**Edit**
<!-- /gui -->
on it first offers to draw the
deficit, or as much as Wealth holds, from Wealth. Emergency Savings start
again at 0 each year.

## Library tab
<!-- help: tab-cov-library -->

Every book at the covenant: the ones it owns, and the ones owned by its
laboratories and its characters.

**You type:** each book and its details.

**The app works out:** the counts in the
<!-- tui -->
Summary,
<!-- /tui -->
<!-- gui -->
shelf headings,
<!-- /gui -->
where each book is kept, and
each book's Build Point cost, shown in its details. Lab Texts and
Casting Tablets are bought as a pool (1 and 2 Build Points per 5 levels of
the library's total), so their details show the pool, with any levels
bought but not yet used.

**See also:** [Books](help:section-books),
[a laboratory's Inventory tab](help:tab-lab-inventory),
[Build tab](help:tab-cov-build), [How to manage the covenant](help:guide-covenant).

### Summary
<!-- help: section-lib-summary -->

<!-- tui -->
How many books the library holds, by type: Summae and Tractatus, each split
into Ability and Art, then Lab Texts, Casting Tablets, Other and the total.
It is worked out from the list below and cannot be edited, but `a` here
adds a book and More's **Import** reads books from a CSV file, as on the
Books list.

**Research** counts the subjects the library aids research on, when a
magus looks up a fact (Covenants, Use: Research: an Intelligence + Ability
roll with the library's bonus); a book's details panel gives its subject's
bonuses. More's **Set Up Research Library** sets the library's bonus for
<!-- /tui -->
<!-- gui -->
On the desktop the Library chapter has no summary of its own: the books
stand on shelves by type, each shelf headed with how many it holds.

The library aids research when a magus looks up a fact (Covenants, Use:
Research: an Intelligence + Ability roll with the library's bonus); a
book's details in the inspector give its subject's bonuses. **Set Up
Research Library**, a button on the Library beside Import, sets the
library's bonus for
<!-- /gui -->
each subject it has a book on, from None to +5 (a few books, a respectable
collection, a broad and deep one, specialized, peerless); under each, what
the library holds on it is a guide.
<!-- gui -->
It walks through the subjects one at a time: each step lists the books on
that subject that back its bonus, and its encyclopedias, with the bonus
the level you choose comes to and the bonuses chosen so far. Nothing is
saved until the last step's Finish.
<!-- /gui -->
**Pictorial works** on a subject raise
it one level (10 Build Points at creation, a row of the Build tab), as does
an expert correspondence on it; the bonus stops at +5. An **encyclopedia** aids research like a
library of its own: +1 for each of its tractatus on the subject (Art &
Academe, Encyclopedias), worked out and shown beside the library's bonus;
a magus uses whichever is better.

### Books
<!-- help: section-lib-books -->

<!-- tui -->
One list of every book at the covenant, with its Type, Subject, Level,
Quality and Location ("Covenant Library", the laboratory, or the character
who owns it).
<!-- /tui -->
<!-- gui -->
On the desktop every book at the covenant stands on the Library chapter's
shelves (Summae, Tractatus, Laboratory Texts, Casting Tablets, Other
Books), a summa as tall as its level; click a book to see its figures and
its Owner (the covenant, a laboratory, or a character) in the inspector.
<!-- /gui -->
A book added here belongs to the covenant.
<!-- tui -->
Space (or
Ctrl+click) marks several books: with books marked, `d` deletes them all and
`e` changes only their owner. More's **Import** reads books from a CSV file
into this covenant's library, showing a preview before anything is added.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** beside the Library's title act on one
book, the one last clicked on the shelves. With more than one
book, **Change Owner** there gives the books you tick one new owner;
deleting several books at once isn't offered on the desktop yet: use the
terminal version. **Import**, a button on the Library, reads books from a CSV file
into this covenant's library, showing a preview before anything is added.
<!-- /gui -->

A **codex** is one tome binding several books together, such as a summa and
a tractatus on related subjects. Choose it in a book's **Codex** field (or a
new one).
<!-- tui -->
The books of a codex are listed together, each name starting with a bar.
<!-- /tui -->
Each book in it is still studied on its own, but only one reader can
use the codex in a season, and its books are always kept together: changing
one book's owner moves the whole codex. A **palimpsest** is a codex written
over a scraped text: each text in it is read, and priced, at -3 Quality.
A codex marked **Encyclopedia** is a series of tractatus that also aids
research (see Summary). A codex can also be a **Collection**: a
**Florilegium** binds tractatus on one topic, each read on its own at +1
Quality (+2 when edited by an authority from a peerless collection); a
**Folio** binds a society's best Lab Texts and tractatus, and reading one
of its books also gives 1 xp in Order of Hermes Lore.

A summa or tractatus can be **Glossed** (+1 Quality, once): annotated
by a reader at least half as skilled as its Level with better
Communication than its author -- tick it, or plan a Read season with
**Gloss it**, which checks the reader. A tractatus's **Opus** can be **Correspondence**: letters bound in order
(at least 24 from each writer), read as a tractatus whose Quality is the
two writers' Communication added -- type it as the Quality; an **Expert
correspondence** (120 or more letters from each of two experts) also raises
its library's research on the subject one level. A **Lecture commentary**
is a teacher's lectures recorded by a scribe (the Record a teacher's
lectures season makes one), which doesn't count against the tractatus the
teacher may write. Or it can be
**Commentary**: a book about a summa,
chosen in **Commentary on**. It is read only after a season studying that
summa (the plan notes it when no such season is on record: the app records
summae studied from now on) and is read at +1 Quality, which its Build
Point cost leaves out (Covenants, Other Opus Types). Any book's **Physical
form** says how the copy was made: an **Exemplar** (-3 Quality), a
**Flap-bound** book (-1), **Juvenilia** (-3), and others that change
nothing by a set amount, such as an edition de luxe or a damaged book,
whose Quality you enter as it is. A **Congregational** book is a huge
codex several magi can study in the same season.

A book can be an **Epitome**: the book itself enchanted as an item
(Covenants, Secondary Functions). Choose an existing enchanted device, or
**(enchant it: a new invested device)** to make one: material level 2 and
size x4 (8 pawns of capacity), held where the book is kept, and moving with
it. The **Book** shape (in the shape and material list) gives +6 to
changing thoughts or images within the book, +4 numerology and +3
divination; only the epitome's own resonant materials help its
enchantment. Its effects are instilled like any device's. The Quality in a book's
details shows what it is read at and why ("10 (written 9; commentary +1)"), and its **Kind**
line names the opus and form.

With the optional rule **Extended book Quality** (Edit Saga), a book's
Quality is built from parts (Covenants, Extended Suggestions on the Quality
of Books): the author gives Communication + 3 instead of + 6 (a season of
writing makes the book that way), and the book form gains its
craftsmanship -- a skilled scribe, binder and illuminator (+1 each, for a
Profession score of 6 or more), resonant materials (+1 bought, +2 from a
story) and clarified (+1). Each counts toward its Build Point
cost. A book's details warn of what can't go together (a gloss with
resonance, a florilegium with resonance or clarification, resonance on
juvenilia...) and of an Art book over what it effectively reaches (35 -
Level for a summa, 17 for a tractatus).

A summa or tractatus shows its **Value**: Excellent, Sound, Vain or
Discarded, from its Quality against its Level (Covenants, Categories of
Value: a summa's Quality + Level, an Ability summa's Level counting three
times; about 32 and up is Excellent, 26 to 31 Sound, 19 to 25 Vain; a
tractatus about 13 and up, 9 to 12, 4 to 8). After it, a guide to its price:
in vis for a book on an Art, an Arcane Ability or a supernatural power (a
sound summa about its Level in pawns, a vain one half that, a sound
tractatus 2 or 3 pawns, an excellent book only given as a gift), and about
a pound from a stationer for any other book.

## Diary tab
<!-- help: tab-cov-diary -->

A dated record of what happens to the covenant, in date order. Each entry
has a Year, Season, Category and Name, and can carry pounds, vis and
Loyalty points. Only the Loyalty points change the sheet: they are added
into Actions and events under Loyalty. Pounds and vis are a record.
A Story Event also has a Status (Open or Resolved), a year to revisit it
and, optionally, a link to one of the covenant's Boons or Hooks. The app
adds entries of its own too: vis harvests, vis moved in or out, and
contested resources that went unsecured.

A Story Event linked to a Hidden Resources Boon also has **Build Points
unlocked**: the points of that Boon's 250 that the story opened up. They
count once the event is Resolved, and the form refuses more than the Boon
has left. Only the points are recorded: add what was found (vis, books,
items) on its own tab as usual.

A Story Event linked to an Illusory Resources Hook has **Build Points found
illusory** instead: the points of that Hook's 250 the story showed don't
really exist. They count the same way; take what vanished off its own tab.

**You type:** each entry, with
<!-- tui -->
`a`, `e` and `d` on the list.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** beside the Diary's title (Edit and Delete
act on the entry last clicked).
<!-- /gui -->

**The app works out:** the order of the entries, for a Story Event
linked to a Hook, how many stories have been told against it, and for one
linked to Hidden Resources or Illusory Resources, how many of its points
have come to light.

**See also:** [Inhabitants tab](help:tab-cov-inhabitants) (Loyalty),
[Possessions tab](help:tab-cov-possessions) (vis),
[Advancing a season](help:advance-season), [How to manage the covenant](help:guide-covenant).

## Build tab
<!-- help: tab-cov-build -->

What the covenant's Build Points went on. Build Points are spent when a
covenant is created and do not matter in play, so this tab is the one place
they show once the covenant is In Play. The pricing follows Ars Magica
Definitive Edition, Chapter 6: Covenants, and Chapter 8: Laboratory for the
starting laboratories.

**You type:** nothing here. The Power Level and the storyguide's Build
Points are set on the Creation Worksheet.

**The app works out:** the Build Points of everything the covenant owns,
from its library, vis, enchanted items, laboratories, specialists and
money. Below them, for a covenant with Hidden Resources, the pool those
Boons hold, how much of it Story Events have unlocked and how much is
still hidden; and the same for Illusory Resources (found illusory, still
believed real). Both are kept out of the totals.

**See also:** [Library tab](help:tab-cov-library),
[Possessions tab](help:tab-cov-possessions),
[Inhabitants tab](help:tab-cov-inhabitants), [How to create a character, covenant or laboratory](help:guide-creation).

### Build Points
<!-- help: section-cov-build -->

A row for each kind of resource, with its Initial and Current Build Points,
and the total in the title. While the covenant is In Creation the two
columns are the same, and the title shows the total against the
storyguide's Build Points. Moving to In Play keeps the Initial figures,
while Current goes on following what the covenant owns, counting every
laboratory rather than only its starting ones. A covenant that was already
in play before Build Points were tracked shows no Initial figures. To
recount the Initial figures, move the covenant back to In Creation and then
to In Play again.

Each magus has one standard laboratory free, whether or not it is entered;
starting laboratories beyond those cost 50 each. Only the magi the Power
Level step says go without a laboratory refund 50 each.

### What's Counted
<!-- help: section-cov-build-items -->

Every resource that has a Build Point price, under the row it counts
towards, with its points: each book, vis source and stock, enchanted item,
laboratory and specialist.

# Arms
<!-- help: arms -->

A covenant's shield, or a lord's, town's, church's or faction's. Six
choices make it: the **Field**'s tincture, how it is divided
(**Division**: plain, per pale, per fess, per bend, quarterly, per
chevron, bendy or checky) and the **Second tincture** of a divided
field, a **Charge** laid on it (a tower, a book, a key, a star, a sword,
a crown, a cross, a crescent, a tree, a chalice, an eagle, a lion, a
lion with its tail knotted (queue-nowed), a wheel, a fleur-de-lis, or a
bend, the band from the top left corner to
the bottom right, which is borne once), **How many** of it (one, two
side by side, or three as two and one, as heralds place them) and the
**Charge tincture**. A **Motto**, the bearer's own words, leads above
the blazon. Leave the Field blank for no arms. The historical arms of Mythic
Europe's lords, towns and sees are mostly within reach: the Emperor's
eagle, the wheel of Mainz, the cross of Trier, the three crowns of
Cologne, the lion of Flanders, the bendy of Burgundy, the checky of
Dreux.

The tinctures are the two metals, Or (gold) and Argent (silver), the
colours Gules (red), Azure (blue), Vert (green), Sable (black) and
Purpure (purple), and the fur Ermine (argent strewn with black tails).
A fur is neither metal nor colour, so it may lie on either. The blazon, the arms in heralds' words ("Per bend
azure and argent, a tower or"; "Gules, three crowns or"), is written
for you as you choose, and
the shield is drawn beside it. Heralds' rule of tincture says a colour
never lies on a colour, nor a metal on a metal: the form warns of a
charge that breaks it, which is allowed, and of one in the same tincture
as its field, which can't be seen.

<!-- tui -->
Open it with More (m) and Arms on the covenant or neighbour itself. Its
blazon shows in the record's panel and on its card in the Region.
<!-- /tui -->
<!-- gui -->
Edit Arms in the Arms section (on a covenant's Charter or Sketch, on a
neighbour's Standing) opens it. A covenant's Charter also shows the arms
of the other covenants of its Tribunal.
<!-- /gui -->

**See also:** [Covenant sheet](help:covenant)
