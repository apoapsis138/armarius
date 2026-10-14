# Plan Season
<!-- help: plan-season -->

Plans what a magus, companion or Mythic Companion does with the current season. Nothing changes when you save: the plan is applied when the saga is advanced with `t`. Grogs aren't planned season by season; they have a [yearly update](help:grog-year) instead.

**You type:** the Activity, then the fields that activity needs (what the experience goes into, a book, a teacher, a Source Quality, a die roll), months lost to distractions, and Notes.

**The app works out:** what the season will give, from the character and the saga as they stand now, shown on the line above Save as you fill the form in.

### Where it's opened from
<!-- help: plan-season-where -->

- A character's **Planning** tab: the This Season section. `a` or `e` plans the season (or changes the plan), and `d` clears it after a confirmation.
- A covenant's **Seasons** tab: highlight someone in the Magi or Companions list and press `a` or `e` to plan, or `d` to clear the plan.

A magus's laboratory work (inventing spells, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned on the laboratory's [Planning tab](help:tab-lab-planning), not here. See also [inventing a spell](help:invent-spell). A character's Planning tab names the laboratory when their season is lab work.

### Activities offered
<!-- help: plan-season-activities -->

The Activity list offers what this character may do. Activities marked "magi" are offered to magi only.

- **Study and experience:** Work / Exposure, Practice, Read a book, Be taught, Teach, Be trained, Study from vis (magi) and Adventure.
- **Books:** Write a summa, Write a tractatus, Copy a book, Translate a book, Copy Lab Texts (or Casting Tablets), Edit a florilegium (binds the tractatus on one subject you can get at, as many as you could write on it, from a collection twice that size: +1 Quality each, +2 for an authority -- Ability 10 or Art 35 -- from one five times the size; Ability 6 or Art 20 to edit at all), Write Casting Tablets (magi: of a spell they have mastered, Latin x 20 levels a season, as many tablets as that holds), Rewrite Lab Texts for general use (magi) and Teach Lab Text abbreviations (magi).
- **Apprentices and research (magi):** Search for an apprentice, Open an apprentice's Arts, Teach a Hermetic Virtue and Seek an insight.
- **Assist in a laboratory:** helping a magus with the lab work they have planned.
- **Undergo an Initiation:** the Initiate's season of a Mystery Initiation. **Teacher / master** is the Mystagogue (none for a self-initiation); give the Mystagogue's Lore and the Script bonus (every component, the Ordeal's +3, +6 or +9 included). **Virtue initiated** opens the Virtues & Flaws picker, which asks for anything the entry names (an Affinity's Art); Delete clears a choice. **Ordeal** says what the Ordeal costs, if anything: a Flaw gained (chosen in the picker), one of the Initiate's Minor or Major Virtues lost, or one of their Minor Flaws raised to a related Major Flaw. Its size follows: a Minor Flaw or Virtue is a Minor Ordeal, a Major one a Major Ordeal, a raised Flaw a Medium one. The Initiation succeeds when the Mystagogue's Presence + Lore + Script bonus reaches 15 for a Minor Virtue or 21 for a Major (18 or 30 when the Mystagogue lacks it), less the largest reduction among the Initiate's past Ordeals; the Initiate needs the Lore at 1 unless it is their own House's. See [How to initiate a character into a Mystery](help:guide-initiation).
- **Activities from the supplements**, such as Study a significato, Library research or Act as Mystagogue. Library research shows the roll's total before the die: Intelligence + the Ability + the better of the covenant library's research bonus for it and its best encyclopedia's.
- **Other:** anything else. It is written in the Diary with your notes, and no experience is worked out for it; say in Notes what the season is spent on.

The rules are those of Ars Magica Definitive Edition, Chapter 10: Long-Term Events (Exposure, Practice, Adventure, Books, Teaching, Training, Vis and Distractions); each activity's rule is cited under the plan on the character's Planning tab.

### Where the experience goes
<!-- help: plan-season-experience -->

**Experience in** chooses the Ability, Art or spell Mastery the season's experience goes into. For Teach, it is Teaching or the language used. Some activities split it:

- **Work / Exposure** can give 1 xp in each of two subjects instead of 2 in one.
- **Adventure** can split the storyguide's Source Quality (5 to 10) among up to three subjects, at most 5 to each; give each one's share in Source Quality to (n).

**Source Quality** is asked for Practice (leave it blank for 4, or 5 for a spell's Mastery), Adventure and some supplement activities. **Book** offers the covenant's library and the character's own books. **Teacher / master** lists the other characters: a teacher must plan Teach for the same season.

**Stress die (blank: rolled)**: for activities that roll, leave it blank and the app rolls the die when the season is applied, or type a roll made at the table. **Months lost (0-3)**: each full month lost to distractions cuts the total by a third.

### The line above Save
<!-- help: plan-season-preview -->

As you fill the form in, the line above Save shows what the season will give: for each subject, the Advancement Total, the xp gained and how the score and xp change, for example "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)". For book work it shows the progress or the book made.

If the plan breaks a rule (a book the character can't read, a teacher whose score is too low), the line shows the problem and Save refuses the plan until it is fixed. For a companion, it also reminds you when the plan leaves too few seasons that year for their two working seasons; this is a reminder, not a block.

**See also:** [Advance Season](help:advance-season), [Grog's Yearly Update](help:grog-year), [Laboratory Planning tab](help:tab-lab-planning), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Grog's Yearly Update
<!-- help: grog-year -->

Grogs aren't planned season by season. Instead the app gives each grog a yearly update, applied when Winter is advanced, following Grogs, Chapter 5: Updating Grogs. This dialog sets up that update.

Open it from the grog's **Planning** tab (`e`), or from the Grogs list on a covenant's **Seasons** tab.

**You type:**

- **Vocational training**: the Ability trained, usually Single Weapon from the drill sergeant, and **Vocational xp** (7, or the teacher's Source Quality if you know it).
- **Practice (4 xp)**: one Ability practised.
- **Exposure (2 xp)** and a second **Exposure (2 xp)**.
- **Story awards this year**: how many stories the grog took part in.

**The app works out:** the xp each Ability gains. Each story award takes one season of the year, in this order: the first exposure, the vocational training, the practice, then the second exposure. The grog's Planning tab shows what the update will give.

In Winter the xp is added, a "Yearly update" entry is written in the grog's Diary and in the season's record, and the story awards go back to 0 for the next year.

**See also:** [Advance Season](help:advance-season), [Plan Season](help:plan-season), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Advance Season
<!-- help: advance-season -->

`t` moves the saga on by one season and applies every plan made for the season that is ending. It works from anywhere in the workspace.

**You type:** only your answers to the questions it asks.

**The app works out:** each plan's result, the end-of-year events in Winter, the covenants' vis harvests, and the new date.

### The confirmation
<!-- help: advance-season-confirm -->

The Advance Time dialog asks whether to advance from this season to the next, and summarises the plans:

- how many planned seasons will be applied;
- who has nothing planned (they gain nothing this season);
- any plan that can't be carried out, and why.

When the year is about to end it also says that each covenant's surplus will be added to its Wealth and that Emergency Savings start again at 0. If you advance by mistake, More's Set Date on the saga puts the date back, but it doesn't undo what the season did.

### Questions along the way
<!-- help: advance-season-questions -->

After you choose Advance, the app may ask:

- In Winter, if a covenant is in deficit, whether to advance anyway. Advance anyway rolls the year over; No (or Escape) leaves the date alone so the books can be balanced first.
- Which contested vis or income sources whose security has lapsed were secured this season, one tick each. A ticked one is secure for five years; one left unticked gives nothing until it is.
- For an experiment seeking a Discovery, whether to take the Discovery by using the risk to move the roll, when it could (a tick each).

Cancelling any of these leaves the date and the saga as they were.

### How the season is applied
<!-- help: advance-season-apply -->

Every plan's outcome is worked out first, from the saga as it stood before the season, and only then are they all applied. So one character's results can't change another's, or their own, in the same season: raising Magic Theory this season doesn't raise this season's Lab Total. Dice left blank on a plan are rolled now.

Before anything is applied the saga is backed up to `sagas/backups` in your data folder (the last five are kept), so the season can be undone by copying the backup over the saga's file.

Then, for each plan:

- the experience is added, and lab work, book work and the like are carried out;
- an entry is written in the character's Diary (and the laboratory's or covenant's, where the work touches them);
- a plan that can't be carried out is skipped, and the record says why.

The season's plans are then removed.

### Winter: the end of the year
<!-- help: advance-season-winter -->

When Winter is advanced, the year ends:

- each grog's [yearly update](help:grog-year) is applied;
- a character running a business pays its yearly upkeep in Labor Points (City & Guild);
- yearly Warping Points are added, for a Longevity Ritual and for living in a strong aura of another realm;
- every character aged 35 or more (50 with Strong Faerie Blood or Dhampir), or with a Longevity Ritual, makes an aging roll (Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Aging), written in their Diary;
- Dwindling Resources lose a tenth of their value when they began dwindling (gone after ten years), and a contested resource still not secured gives nothing that year;
- each covenant's surplus is added to its Wealth.

Every season, each covenant's vis sources for that season are harvested into its vis stores and written in its Diary.

### Afterwards
<!-- help: advance-season-after -->

The date moves on, a message names the new date and whose seasons were applied, and, when anything happened, the [Season Summary](help:season-summary) shows the results. With Keep season records on, the season is also kept under [Seasons](help:seasons) in the tree.

**See also:** [Plan Season](help:plan-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [The saga](help:saga), [How to plan and run a season](help:guide-seasons)

# Season Summary
<!-- help: season-summary -->

Shown after a season has been advanced, when anything happened: what the season gave everyone, grouped by covenant.

**You type:** nothing. Enter, Escape or Close closes it.

**The app works out:** one line per person: the activity, what it was on and its result (for example the xp gained). A plan that couldn't be carried out shows why; a magus or companion with nothing planned is shown as "nothing planned". In Winter it also lists aging rolls, grogs' yearly updates and business upkeep, and in any season the covenants' vis harvests.

The note at the bottom says whether the season is kept under Seasons in the tree. If season records are off (Edit Saga), each character's Diary still has their entry.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons), [How to plan and run a season](help:guide-seasons)

# Creation Worksheet
<!-- help: creation-worksheet -->

Walks a covenant, laboratory or character that is In Creation through the book's steps, showing each step's budget, what was spent or taken there, and its checks. It fills the screen, and opens by itself when you make a new covenant, laboratory or character.

**You type:** nothing in the worksheet itself. Its keys and buttons open the same dialogs as the sheet, and they edit the real record; everything is saved as you go.

**The app works out:** each step's budget and what is spent, and the creation checks, worked out again whenever a dialog closes.

### In Creation and In Play
<!-- help: creation-worksheet-modes -->

A new covenant, laboratory or character starts **In Creation**, with its tree node marked "(creating)". A character made from a template starts **In Play**, since the book's templates are fully made.

The record's top panel has a button showing the mode; clicking it, or More's **In Creation / In Play**, switches between them after a confirmation. Creation checks only run while a record is In Creation, and come back if it is moved back. When a covenant moves to In Play, the app keeps what its Build Points were spent on.

Open the worksheet from the top panel's **Creation Worksheet** button, or from More's **Creation Worksheet** on the record's tree node or top panel. Both are only there while the record is In Creation.

### Steps and their marks
<!-- help: creation-worksheet-steps -->

The left column lists the steps:

- a character: Concept, Virtues and Flaws, Characteristics, Early Childhood, Later Life, Apprenticeship and Years past Gauntlet (magi only), and Finishing Touches;
- a covenant: Baseline, Resources, Boons & Hooks, and Review;
- a laboratory: Setting Up, and Review.

Each step is marked by how its checks stand:

- **✔** every check passes;
- **✘** a rule the book says must be followed is broken (a warning);
- **☞** advice: something the book says should be done isn't, such as too many or too few of something;
- **○** the step has no checks.

Below the list the app counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Up and Down choose a step; Tab moves to the step's list, then its buttons; Escape closes the worksheet. On the right, the step shows its budget and what is left, its list, its checks (each with what the record has), and buttons for its other edits, for example Edit Characteristics, Learn a spell or Buy a specialist. The chosen row's details show at the bottom: a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

The step's list works like every list on the sheets: **a** adds (Add a Virtue on Virtues and Flaws, where F2 in the picker turns to Flaws; Spend xp on the xp steps), **e** changes the chosen row and **d** takes it back after asking. On an xp step each row shows the pool xp spent and the xp it gained, which is half again with an Affinity, rounded up on the whole spend. The Spend xp dialog shows, as you type, what the pool xp gains, the score that buys and the pool xp the next score needs, and warns past the creation cap; an Ability's Specialty can be given there too. Taking xp back always gives back the pool xp spent and takes off exactly what it gained. On the Later Life step, d on a training package's row drops the whole package.

On the desktop, each budget is also a bar that fills as it is spent: gold while some is left, red once it is over, with the sums beside it. Every xp step (Early Childhood, Later Life, Apprenticeship, Years past Gauntlet) adds **Experience So Far**: each Ability and Art the worksheet has put xp into, with what each step gave it (this step's column first, in bold), the total and the score it buys, so a step shows what the others already gave. Above the steps, **Rules broken** names each step with a rule that must hold and doesn't, and how many; click one to go to that step (its rules are in the line's tooltip).

The Ability cap at creation goes by age (5 under 30); an Affinity with the Ability raises it by 2 for that Ability, and Mentored by Demons lifts it. Puissant never counts, since it adds only when the Ability is used. While a character is In Creation, the sheet's Edit Ability and Edit Arts say how much xp came from the worksheet: take that back on the worksheet, not by lowering the total. The checks follow Ars Magica Definitive Edition, Chapter 3: Characters, Detailed Character Creation Summary, for characters, and Ars Magica Definitive Edition, Chapter 6: Covenants, for covenants.

### Moving to In Play
<!-- help: creation-worksheet-play -->

The last step has **Move to In Play**. It lists every check that doesn't pass and asks before moving the record. A covenant with Build Points left over is told how many: moving it to In Play turns them into Mythic Pounds in its Wealth, 10 pounds for each Build Point (the rate money is bought at).

Checks never stop an edit. If the saga has **Enforce creation rules strictly** turned on (Edit Saga), a record that breaks a rule it must follow stays In Creation until that is fixed. Advice never stops it.

**See also:** [Characters group](help:character-group), [The saga](help:saga), [How to create a character, covenant or laboratory](help:guide-creation)

# Import Data
<!-- help: import-data -->

Brings records into the saga from files. Open it from More's **Import** on the saga node.

**You choose:** what to import, then the file: the terminal lists the folders and files of that kind, the desktop opens its Open window.

**The app works out:** a preview of what the file adds, shown before anything is added.

### What can be imported
<!-- help: import-data-kinds -->

- **Characters**, **Covenants** and **Laboratories**: a file exported from another saga with More's Export. The file must hold the kind you chose. The file picker starts in the exports folder.
- **A Whole Saga**: a file written by **Export Saga**. Every covenant, laboratory, character and familiar in it is added beside this saga's own, with their books and devices and the saga's own spells and house rules, as importing each record would.
- **Books**: a CSV file with a header row. Columns, in any order and any case: name, type, language, author, year_published, description, art, ability, level, quality, tractatus_type, spell, codex, encyclopedia, opus and physical_form; name and type are needed. Rows with the same codex are bound together in one new codex of that name, an encyclopedia when its rows' encyclopedia column says yes. A tractatus's opus can be commentary or correspondence; physical_form is one of exemplar, flap-bound, juvenilia, edition de luxe, treasure-bound, ex libris, holographic, huge codex, unbound or damaged. A level or quality of "var" means the figure is to be set later: the book is imported, highlighted until you edit it to give its numbers, and can't be studied until then. Books imported here go to Unassigned Books. From a covenant's **Library** tab, More's Import puts them straight into that covenant's library instead. An owner or cost column is ignored: the cost is always worked out.
- **Spells**: a CSV file, through the [Import Spells](help:import-spells) helper.

A row that can't be read is skipped, and the preview says why. When a book or spell has the name of one already in the saga, the app asks: Skip, Skip All, Duplicate or Duplicate All. Nothing is added until every question is answered, and cancelling a question imports nothing.

### Importing an exported record
<!-- help: import-data-records -->

What travels with the record comes too, and everything imported gets new ids. Links to records that aren't in the file (a character's covenant, a laboratory's owner, a book's author) are matched by name to the one record of that kind and name in this saga, or dropped; the preview lists which. A record with the same name as one already here is added beside it. Nothing already in the saga is changed, except that a laboratory with no owner, or a magus with no laboratory, can be linked to the imported partner the file names.

### Exporting
<!-- help: import-data-export -->

More's **Export**, on a covenant's, laboratory's or character's tree node or top panel, writes that record to a file another saga can import. On the desktop, Export is in the record's **Manage** chapter, the last one on its page, with Update from a File and Delete.

**You type:** the File to write (it starts in the exports folder, and `.amm.json` is added if you give no `.json` ending), and for a covenant whether to include its laboratories and characters. The line above Export warns when the file exists and will be replaced.

What goes with it:

- a character: their familiar, the enchanted devices they hold, their books and their Diary;
- a laboratory: its books and the devices kept in it;
- a covenant: its books and devices, and optionally its laboratories and characters with their own things;
- the saga's own spells and house rules that these use.

Season plans, season records and lab projects under way stay behind.

**Export Saga**, in More on the saga node (on the desktop, a button in the saga page's **Saga Management**, beside Import), writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. In a browser copy, the file downloads instead. Only the storyguide can use it.

### Printing a record
<!-- help: print-record -->

On the desktop, a covenant's, laboratory's, character's or familiar's
**Manage** chapter has **Print to PDF**. It asks where to save the file
(it starts in the exports folder, named after the record), then lays the
page out for paper: the header, then each chapter in turn under its name,
in the Scriptorum parchment colours whatever theme is on show, with the
buttons and the inspector left off. Pages break between sections where
they can, and a section's title is never left alone at the foot of a page.
Manage, Planning and Seasons are left off, since they are for the screen.
The PDF can be printed or sent like any other.

### Giving to another record
<!-- help: give -->

**Give** hands what one record holds to another record of the saga: the
chosen row of a Raw Vis list, a books list (a laboratory's Lab Texts too),
Enchanted Devices, a character's Personal Gear or a covenant's Weapons,
Armor or Items. In the terminal it is in More (`m`) on those lists; on the
desktop, a Give button beside the list. It asks who gets it and, for vis
and gear, how many. A book changes owner and a device changes holder (a
device's epitome goes with it); gear given in part is split, so both keep
some. Vis goes to a covenant, a laboratory or a magus; a laboratory takes
no gear or silver.

**Give Silver** gives pounds of silver from a character's purse (on
Personal Gear) or a covenant's Wealth to another character or covenant,
so someone leaving a covenant can take silver with them. Both sides'
Diaries record every gift; a covenant files it under Library for a book,
else Purchases & Sales, with the pounds for silver. Only the storyguide
can give.

### Updating a record from a file
<!-- help: import-data-update -->

More's **Update from a File**, on a covenant's, laboratory's or character's tree node or top panel (on the desktop, in its **Manage** chapter), reads an export of that same record over it: for example after working on a character on another computer. Only the storyguide can use it.

**You choose:** the exported file. It must hold the same kind of record.

**The app works out:** what would change, field by field ("Abilities: 1 added, 2 changed", "Name: Old → New"), and the links in the file it can't match here. Nothing changes until you choose **Update**; a file that changes nothing says so.

What it replaces: the record's own contents, and what travels with it in an export (a character's familiar, devices and books; a laboratory's or covenant's books and devices). What it keeps: the record itself, so everything that points at it still does, and where it sits in this saga (a character's covenant and laboratory, a laboratory's covenant and owner). A covenant's file made with its laboratories and characters updates the covenant only; update each of them from its own export.

**See also:** [Import Spells](help:import-spells), [Unassigned Books](help:unassigned-books), [The saga](help:saga), [How to import and export](help:guide-import-export)

# Import Spells
<!-- help: import-spells -->

Explains what a spell CSV file looks like before you choose one. Tick **Save an example CSV instead** to save one to start from, rather than choosing a file. The spells imported become the saga's own spells, which you can edit on [Spells](help:tab-content-spells).

Open it from More's Import on the saga node, then Spells.

**You type:** a CSV file with a header row. Columns, in any order and any case:

- **name**, **technique** and **form** (required). A Technique or Form can be written in full or abbreviated (Cr, Ig...).
- **level**: a number, or Gen (or blank) for a General spell.
- **requisites**: extra Arts, for example Rego, Corpus.
- **range**, **duration** and **target**, in full or abbreviated (Per, Mom...).
- **ritual**: yes or no (blank is no).
- **base_level**: the guideline level before Range, Duration and Target (optional).
- **description** and **source**.

**The app works out:** a preview of the spells found, the rows skipped and why, and any columns it didn't use. Names already in the saga are compared in any case, and the app asks about each one (Duplicate, Duplicate All, Skip or Skip All).

### The buttons
<!-- help: import-spells-buttons -->

- **Choose CSV file...** goes on to pick the file.
- **Save example CSV** writes `spells_example.csv` (numbered if it exists) to the folder the app was started from, with two example spells. Edit it, then choose it to import.
- **Cancel** closes the helper.

**See also:** [Spells](help:tab-content-spells), [Import Data](help:import-data), [How to import and export](help:guide-import-export)
