# Covenant sheet
<!-- help: covenant -->

The covenant sheet holds everything that belongs to the covenant as a
whole: its attributes, its people, what it owns, its money, its library and
its history. It opens when you choose a covenant in the tree. Under the
covenant's node, the tree lists its **Characters** and **Laboratories**,
each of which has a sheet of its own.

The top panel, with the covenant's name, stays in view above the tabs
whichever tab is open. The tabs are numbered, and the number keys `1` to `8`
open them. Most tabs have a details panel docked at the bottom: choose a row
and it shows that row's figures and, where there is one, its rules text and
where in the books it comes from.

More (`m`) on the top panel offers **In Creation / In Play**, which switches
the covenant between being built and being played, and, while it is In
Creation, the **Creation Worksheet**, which walks through building a
covenant step by step. The same switch and worksheet are the buttons beside
**Edit (e)** in the top panel. Export is in More there too.

**See also:** [Saga](help:saga), [Keys](help:keys),
[Advancing a season](help:advance-season), [How to manage the covenant](help:guide-covenant).

### The covenant panel
<!-- help: section-cov-info -->

The panel at the top of the sheet. Saga, Storyguide, Current Season and
Current Year come from the saga and are shown dimmed: change them on the
saga, not here. Everything else is typed with `e` (Edit Covenant): the name,
Tribunal, Year Founded, Aegis of the Hearth and its Penetration, the two
Living Conditions, the base Aura, Aura Realm and Covenant Season. The app
works out the Aura shown, adding any Boon that raises it to the base you
typed, and that total is the aura every laboratory of the covenant starts
from. Living Conditions (Mundane) feeds Loyalty, both Living Conditions are
used in the aging rolls at the end of the year, and Covenant Season decides
how many points each inhabitant is worth on the Economics tab. While the
covenant is In Creation, the panel also shows the Build Points spent.

## Attributes tab
<!-- help: tab-cov-attributes -->

What the covenant is like: its description, its Reputations, and its Boons
and Hooks.

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
`e` opens it for editing. Nothing on the sheet is worked out from it.

### Reputations
<!-- help: section-cov-reputations -->

The covenant's Reputations, each with a score from -3 to +3. Each one also
records whether the covenant knows about it: an unknown one is marked
"(not known by the covenant)" on its row. Every point of a bad Reputation
the covenant knows about costs 5 Loyalty points on the Inhabitants tab; good
Reputations and unknown ones cost nothing.

### Boons
<!-- help: section-cov-boons -->

The covenant's Boons, chosen from the catalogue with `a` and edited with `e`
to give their detail and description. The picker shows the highlighted
Boon's rules, requirements and book under the list. The title shows the points they cost.
That total and the Hooks' total share one colour: plain while there are
points still to spend, the success colour when they match, and the error
colour when the Boons cost more than the Hooks provide. Some Boons change
figures elsewhere: an Aura Boon raises the Aura in the top panel, a Style of
Governance Boon fills in the Type of Governance on the Loyalty block, and a
Boon that enlarges the buildings adds to the Buildings cost on the
Economics tab. A Hidden Resources Boon holds 250 Build Points the magi can't
use yet: its row shows how many are unlocked ("120/250 BP"), and
its details panel lists the Story Events that unlocked them (see the
[Diary tab](help:tab-cov-diary)). Its description is the place to note
what the resources are, decided ahead or later.

### Hooks
<!-- help: section-cov-hooks -->

The covenant's Hooks, chosen from the catalogue with `a` and edited with
`e`. The title shows the points they provide, coloured together with the
Boons' total. A Hook the catalogue allows to be unknown can be marked so,
and then counts a fixed number of points shown on its row. A Story Event in
the Diary can be linked to a Hook, and its details then say how many
stories have been told against that Hook so far. An Illusory Resources Hook
stands for 250 Build Points of improvements that don't really exist: its
row shows how many have been found out ("60/250 BP"), and its details list
the Story Events that revealed them.

## Inhabitants tab
<!-- help: tab-cov-inhabitants -->

Who lives at the covenant, and how loyal they are.

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
Money from the choices you make with `e` (a Pension adds to Money),
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
colour when not. Other People, typed with `e`, is for anyone you do not
want to list one by one. Total Inhabitants adds Other People to every
list's headcount except Livestock.

### Miscellaneous
<!-- help: section-inh-misc -->

Aging for Magi and for Mundane, and the numbers of Magic Laborers, Servants,
Teamsters and Turbula, all typed with `e`. The app keeps them as a record
and does not work anything out from them.

### Magi
<!-- help: section-inh-magus -->

Every magus whose character sheet belongs to this covenant is listed
automatically, with their House, year of birth and Gift taken from the
sheet. You can also add a magus who has no sheet, typing those details
yourself. `e` on a listed magus edits only the covenant's own notes about
them. `d` on a listed magus does not delete anyone: it marks them as
departed, so they stop counting as an inhabitant (and leave the Seasons
tab) while staying in the covenant on their sheet. More's **Restore**
brings a departed magus back.

### Companions
<!-- help: section-inh-companion -->

Companions (and Mythic Companions) whose sheets belong to this covenant are
listed automatically; companions without a sheet can be added by hand. Each
can have a Responsibility and a Covenant Role. A Steward, Chamberlain, Turb
Captain or Autocrat earns the covenant a Loyalty bonus of Presence plus the
role's Ability, read from the character sheet. As with magi, `d` marks a
listed companion as departed and More's **Restore** brings them back.

### Specialists
<!-- help: section-inh-specialist -->

Covenfolk with a particular job. `a` first offers the covenant's grogs that
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
are planned, and the details panel shows the chosen person's plan in full.
People marked departed on the Inhabitants tab are left out.

**You type:** each magus's and companion's plan for the season, and each
grog's yearly update.

**The app works out:** nothing on this tab itself. When you press `t` to
advance the season, every plan is worked out and applied, and someone with
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
"nothing planned". `a` or `e` opens the chosen magus's season plan, the same
dialog as on their own sheet; `d` clears the plan after asking first.

### Companions
<!-- help: section-cov-seasons-companion -->

The covenant's companions and Mythic Companions, planned the same way as
the magi: `a` or `e` plans the chosen companion's season and `d` clears the
plan.

### Grogs
<!-- help: section-cov-seasons-grog -->

The covenant's grogs. They are not planned season by season but "updated
yearly": `a` or `e` sets up the chosen grog's yearly update, whose training,
practice and exposure experience is applied at the end of Winter.

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
here (move a laboratory to another covenant from its own sheet). For a
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
Sources land here. More's **Move Vis** sends pawns from the chosen store to
another covenant, laboratory or magus, and both sides' Diaries record it.

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
More's **Instill an Effect** adds an effect to the chosen device (an
invested device takes any number, others only one), and **Use a Charge**
takes a charge off the chosen Charged Item.

## Economics tab
<!-- help: tab-cov-economics -->

The covenant's yearly finances: what it earns, what it spends, what it
saves, and what it has in store.

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
pounds in store, which you type with `e`. On the right, Total Income, the
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
ten years). More's **Improve Income** applies one
year's Income Modification to the chosen source: pick an effect, see the
projected income, and confirm to set the new income and record a note.

### Yearly Expenditure
<!-- help: section-eco-expenditure -->

What the covenant spends each year, by category. Buildings, Consumables,
Laboratories, Provisions, Wages, Weapons and Writing Materials are worked
out from the points of inhabitants, laboratories and weapons and armour
(Wages also follows the salary chosen under Loyalty, and building Boons add
to Buildings); `e` on those rows edits only their note. Tithes, Inflation
and Sundry are typed with `e` (Sundry is at least 1 pound a year). The
details panel shows how the chosen row was worked out.

### Cost Savings
<!-- help: section-eco-savings -->

What the covenant saves. Laborers save on Provisions and craftspeople on
the category of their Field of Work, each up to the limit shown in the
details panel; both are worked out from the Inhabitants tab. Magic savings
is typed: work out what the covenant's magic saves and enter the total.
Emergency Savings is money drawn from Wealth to cover a deficit. While the
covenant runs at a deficit the row says so (or that the covenant is broke
when Wealth cannot cover it), and `e` on it first offers to draw the
deficit, or as much as Wealth holds, from Wealth. Emergency Savings start
again at 0 each year.

## Library tab
<!-- help: tab-cov-library -->

Every book at the covenant: the ones it owns, and the ones owned by its
laboratories and its characters.

**You type:** each book and its details.

**The app works out:** the counts in the Summary, each book's Location, and
each book's Build Point cost, shown in its details panel. Lab Texts and
Casting Tablets are bought as a pool (1 and 2 Build Points per 5 levels of
the library's total), so their details show the pool, with any levels
bought but not yet used.

**See also:** [Books](help:section-books),
[a laboratory's Inventory tab](help:tab-lab-inventory),
[Build tab](help:tab-cov-build), [How to manage the covenant](help:guide-covenant).

### Summary
<!-- help: section-lib-summary -->

How many books the library holds, by type: Summae and Tractatus, each split
into Ability and Art, then Lab Texts, Casting Tablets, Other and the total.
It is worked out from the list below and cannot be edited, but `a` here
adds a book and More's **Import** reads books from a CSV file, as on the
Books list.

**Research** counts the subjects the library aids research on, when a
magus looks up a fact (Covenants, Use: Research: an Intelligence + Ability
roll with the library's bonus); a book's details panel gives its subject's
bonuses. More's **Research Bonuses** sets the library's bonus for
each subject it has a book on, from None to +5 (a few books, a respectable
collection, a broad and deep one, specialized, peerless); under each, what
the library holds on it is a guide. An **encyclopedia** aids research like a
library of its own: +1 for each of its tractatus on the subject (Art &
Academe, Encyclopedias), worked out and shown beside the library's bonus;
a magus uses whichever is better.

### Books
<!-- help: section-lib-books -->

One list of every book at the covenant, with its Type, Subject, Level,
Quality and Location ("Covenant Library", the laboratory, or the character
who owns it). A book added here belongs to the covenant. Space (or
Ctrl+click) marks several books: with books marked, `d` deletes them all and
`e` changes only their owner. More's **Import** reads books from a CSV file
into this covenant's library, showing a preview before anything is added.

A **codex** is one tome binding several books together, such as a summa and
a tractatus on related subjects. Choose it in a book's **Codex** field (or a
new one); the books of a codex are listed together, each name starting with
a bar. Each book in it is still studied on its own, but only one reader can
use the codex in a season, and its books are always kept together: changing
one book's owner moves the whole codex. A **palimpsest** is a codex written
over a scraped text: each text in it is read, and priced, at -3 Quality.
A codex marked **Encyclopedia** is a series of tractatus that also aids
research (see Summary). A codex can also be a **Collection**: a
**Florilegium** binds tractatus on one topic, each read on its own at +1
Quality (+2 when edited by an authority from a peerless collection); a
**Folio** binds a society's best Lab Texts and tractatus, and reading one
of its books also gives 1 xp in Order of Hermes Lore.

A tractatus's **Opus** can be **Commentary**: a book about a summa,
chosen in **Commentary on**. It is read only after a season studying that
summa (the plan notes it when no such season is on record: the app records
summae studied from now on) and is read at +1 Quality, which its Build
Point cost leaves out (Covenants, Other Opus Types). Any book's **Physical
form** says how the copy was made: an **Exemplar** (-3 Quality), a
**Flap-bound** book (-1), **Juvenilia** (-3), and others that change
nothing by a set amount, such as an edition de luxe or a damaged book,
whose Quality you enter as it is. The details panel's Quality shows what a
book is read at and why ("10 (written 9; commentary +1)"), and its **Kind**
line names the opus and form.

With the optional rule **Extended book Quality** (Edit Saga), a book's
Quality is built from parts (Covenants, Extended Suggestions on the Quality
of Books): the author gives Communication + 3 instead of + 6 (a season of
writing makes the book that way), and the book form gains its
craftsmanship -- a skilled scribe, binder and illuminator (+1 each, for a
Profession score of 6 or more), resonant materials (+1 bought, +2 from a
story), clarified (+1) and glossed (+1). Each counts toward its Build Point
cost. The details panel warns of what can't go together (a gloss with
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
into Actions and events on the Loyalty block. Pounds and vis are a record.
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

**You type:** each entry, with `a`, `e` and `d` on the list.

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
