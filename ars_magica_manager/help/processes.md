# Plan Season
<!-- help: plan-season -->

Plans what a magus, companion or Mythic Companion does with the current season. Nothing changes when you save: the plan is applied when the saga is advanced
<!-- tui -->
with `t`.
<!-- /tui -->
<!-- gui -->
with **Advance Season** in the top bar.
<!-- /gui -->
Grogs aren't planned season by season; they have a [yearly update](help:grog-year) instead.

**You type:** the Activity, then the fields that activity needs (what the experience goes into, a book, a teacher, a Source Quality, a die roll), months lost to distractions, and Notes.

**The app works out:** what the season will give, from the character and the saga as they stand now, shown on the line above Save as you fill the form in.

### Where it's opened from
<!-- help: plan-season-where -->

<!-- tui -->
- A character's **Planning** tab: the This Season section. `a` or `e` plans the season (or changes the plan), and `d` clears it after a confirmation.
- A covenant's **Seasons** tab: highlight someone in the Magi or Companions list and press `a` or `e` to plan, or `d` to clear the plan.
<!-- /tui -->
<!-- gui -->
- A character's **Planning** chapter: the This Season section. **Plan** plans the season; once it is planned, **Edit** changes the plan and **Clear** clears it after a confirmation.
- A covenant's **Seasons** chapter: click someone in the Magi or Companions list, then **Plan** to plan their season (or change the plan), or **Clear** to clear it.
<!-- /gui -->

A magus's laboratory work (inventing spells, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned on the laboratory's [Planning list](help:tab-lab-planning), not here. See also [inventing a spell](help:invent-spell). A character's This Season names the laboratory when their season is lab work.

### Activities offered
<!-- help: plan-season-activities -->

The Activity list offers what this character may do. Activities marked "magi" are offered to magi only.

- **Study and experience:** Work / Exposure, Practice, Read a book, Be taught, Teach, Be trained, Study from vis (magi) and Adventure.
- **Books:** Write a summa, Write a tractatus, Copy a book, Translate a book, Copy Lab Texts (or Casting Tablets), Edit a florilegium (binds the tractatus on one subject you can get at, as many as you could write on it, from a collection twice that size: +1 Quality each, +2 for an authority -- Ability 10 or Art 35 -- from one five times the size; Ability 6 or Art 20 to edit at all), Write Casting Tablets (magi: of a spell they have mastered, Latin x 20 levels a season, as many tablets as that holds), Rewrite Lab Texts for general use (magi) and Teach Lab Text abbreviations (magi).
- **Apprentices and research (magi):** Search for an apprentice, Open an apprentice's Arts, Teach a Hermetic Virtue and Seek an insight.
- **Assist in a laboratory:** helping a magus with the lab work they have planned.
- **Undergo an Initiation:** the Initiate's season of a Mystery Initiation. **Teacher / master** is the Mystagogue (none for a self-initiation); give the Mystagogue's Lore and the Script bonus (every component, the Ordeal's +3, +6 or +9 included). **Virtue initiated** opens
<!-- tui -->
the Virtues & Flaws picker, which asks for anything the entry names (an Affinity's Art); Delete clears a choice.
<!-- /tui -->
<!-- gui -->
a list of Virtues to choose from, which asks for anything the entry names (an Affinity's Art); **Clear** beside it clears a choice.
<!-- /gui -->
**Ordeal** says what the Ordeal costs, if anything: a Flaw gained (chosen in the picker), one of the Initiate's Minor or Major Virtues lost, or one of their Minor Flaws raised to a related Major Flaw. Its size follows: a Minor Flaw or Virtue is a Minor Ordeal, a Major one a Major Ordeal, a raised Flaw a Medium one. The Initiation succeeds when the Mystagogue's Presence + Lore + Script bonus reaches 15 for a Minor Virtue or 21 for a Major (18 or 30 when the Mystagogue lacks it), less the largest reduction among the Initiate's past Ordeals; the Initiate needs the Lore at 1 unless it is their own House's. See [How to initiate a character into a Mystery](help:guide-initiation).
- **Activities from the supplements**, such as Study a significato, Library research or Act as Mystagogue. Library research shows the roll's total before the die: Intelligence + the Ability + the better of the covenant library's research bonus for it and its best encyclopedia's.
- **Other:** anything else. It is written in the Diary with your notes, and no experience is worked out for it; say in Notes what the season is spent on.

The rules are those of Ars Magica Definitive Edition, Chapter 10: Long-Term Events (Exposure, Practice, Adventure, Books, Teaching, Training, Vis and Distractions); each activity's rule is cited under the plan in the character's This Season.

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

<!-- tui -->
Open it from the grog's **Planning** tab (`e`), or from the Grogs list on a covenant's **Seasons** tab.
<!-- /tui -->
<!-- gui -->
Open it with **Yearly Update** in the grog's **Planning** chapter, or by clicking the grog in the Grogs list of a covenant's **Seasons** chapter and choosing **Plan**.
<!-- /gui -->

**You type:**

- **Vocational training**: the Ability trained, usually Single Weapon from the drill sergeant, and **Vocational xp** (7, or the teacher's Source Quality if you know it).
- **Practice (4 xp)**: one Ability practised.
- **Exposure (2 xp)** and a second **Exposure (2 xp)**.
- **Story awards this year**: how many stories the grog took part in.

**The app works out:** the xp each Ability gains. Each story award takes one season of the year, in this order: the first exposure, the vocational training, the practice, then the second exposure. The grog's This Season shows what the update will give.

In Winter the xp is added, a "Yearly update" entry is written in the grog's Diary and in the season's record, and the story awards go back to 0 for the next year.

**See also:** [Advance Season](help:advance-season), [Plan Season](help:plan-season), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Advance Season
<!-- help: advance-season -->

<!-- tui -->
`t` moves the saga on by one season and applies every plan made for the season that is ending. It works from anywhere in the workspace.
<!-- /tui -->
<!-- gui -->
**Advance Season**, in the top bar beside the date, moves the saga on by one season and applies every plan made for the season that is ending. It is there on every page while a saga is open.
<!-- /gui -->

**You type:** only your answers to the questions it asks.

**The app works out:** each plan's result, the end-of-year events in Winter, the covenants' vis harvests, and the new date.

### The confirmation
<!-- help: advance-season-confirm -->

The Advance Time dialog asks whether to advance from this season to the next, and summarises the plans:

- how many planned seasons will be applied;
- who has nothing planned (they gain nothing this season);
- any plan that can't be carried out, and why.

When the year is about to end it also says that each covenant's surplus will be added to its Wealth and that Emergency Savings start again at 0. If you advance by mistake,
<!-- tui -->
More's Set Date on the saga
<!-- /tui -->
<!-- gui -->
**Set Date** in the saga page's Seasons chapter
<!-- /gui -->
puts the date back, but it doesn't undo what the season did.

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

<!-- tui -->
The date moves on, a message names the new date and whose seasons were applied, and, when anything happened, the [Season Summary](help:season-summary) shows the results. With Keep season records on, the season is also kept under [Seasons](help:seasons) in the tree.
<!-- /tui -->
<!-- gui -->
The date moves on. When anything happened, the [Seasons](help:seasons) page opens on **Just played**, the [Season Summary](help:season-summary), which names the new date and whose seasons were applied; otherwise a message says so. With Keep season records on, the season stays on the Seasons page, opened from **The Seasons Played** in the saga page's Seasons chapter.
<!-- /gui -->

**See also:** [Plan Season](help:plan-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [The saga](help:saga), [How to plan and run a season](help:guide-seasons)

# Hold Tribunal
<!-- help: hold-tribunal -->

A Tribunal's meeting, held a step at a time from its **Meeting**
tab. Each step is a short form: you make the decisions and enter the
rolls, and the app works out the rest. The meeting is saved after
every step, so leaving it simply leaves it; holding it again resumes
at the step in hand.

The steps run in a fixed order:

- **Opening and the oaths**: where it is held, how many days it lasts
  (3 unless you say otherwise) and the day each case and motion is
  heard. Saving it opens the meeting; cancelling holds none.
- **Attendance and proxies**: for each covenant, how many of its magi
  are absent and the proxies it carries, and whether the Presiding
  Quaesitor allows them or sets them aside. Its votes in the hall are
  worked out, and the proxies are kept on the roster.
- **Each case and motion**, on its day: the debate between the
  prosecutor and defender (for a motion, one who speaks for it and one
  against), taken from the case. Enter each side's debate Fatigue levels
  lost, or leave both blank and the debate is rolled round by round by
  the rules of Houses of Hermes: Societates (The Fine Arts of Debate):
  Communication + Folk Ken, Intrigue or Artes Liberales against
  Intelligence + Charm, Guile or Leadership, each debater using what
  they are best at; a name that is no character in the saga debates as
  an ordinary magus. The case's Evidence is the prosecution's testimony
  and the Defence testimony the defence's, each used once: a peer's +3,
  an apprentice's or familiar's +2, any other +1, and +3 more if a
  Quaesitor examined it. The side that lost fewer levels wins, and the
  difference is its Argument Strength (less 1 for a motion that adds to
  the Code, 3 for one that alters it).
- **The vote** on each case: each covenant's leaning, which you can
  change, and the votes the debate won: an Edge wins 10% of the
  undecided votes, up to a Landslide's 60%, and from a Triumphant
  Victory 10% to 30% of the other side's too. The covenants are called
  one by one and the tally kept; what is left undecided abstains.
- **Elections**, when the Tribunal's customs have offices (the Theban
  archai): each office's holder and when the term ends.
- **Rulings and fines**: the ruling on each case, starting from how its
  vote went; any fine, in pawns of an Art or (with no Art) pounds of
  silver, and who pays it; whether the ruling goes into the Peripheral
  Code (a motion's does unless you say otherwise); and, for a case
  between a troupe covenant and another, how the other's attitude
  toward the troupe's moves (a party that lost takes it ill, -1).
- **Treasury and vis**: the treasury as it stands and the loans that
  fall due this year.
- **Closing**: each case with a ruling is decided and what its ruling
  says is written: the fine, owed to the Tribunal's treasury; the
  ruling, into the Peripheral Code; and the attitude's move, as a reason
  on the covenant's attitude. The Acta, the meeting's acts set out as a
  charter, goes into the Tribunal's Diary, and the next meeting is set
  for when the Tribunal next meets.

Any step can be held again to change it. Every step has a Note for
anything said or decided in your own words.

Each step held writes its minutes into the Tribunal's Diary, an entry
headed with its day ("¶ The First Day: Attendance and proxies"), its
numbers in the margin (the votes in the hall, a vote's tally, a fine)
and its Note after its own words. Holding a step again rewrites its
entry rather than adding another. The Acta, like any Diary entry, can be
reworded by editing it.
<!-- gui -->
On the desktop, choose the Acta in the Diary and press Print to print it
to a PDF.
<!-- /gui -->

**See also:** [Tribunal sheet](help:tribunal), [Meeting tab](help:tab-trib-meeting)

# The World Turns
<!-- help: world-turns -->

The yearly step. When Winter is played, Advance Season asks one more
question before the season is played out: what the year brought beyond
the covenants. Each line has a tick box, and only the ticked lines are
applied.

- **Places**: each place's triggers that came this year (written into
  the place's Diary), and, with the Auras change rule option, the roll
  to raise a Magic aura (already rolled: what you see is what is
  applied).
- **Threats**: a dated stage whose season has come is marked as having
  happened.
- **Neighbours**: each fair a covenant trades at rolls its income for
  the year.
- **Tribunal treasury**: a loan due this year; tick it if it was repaid
  (it starts unticked).
- **Attitudes**: the year's events with each neighbour (favours begun or
  repaid, a covenant's Diary entries naming it). Nothing moves unless
  you choose a change, and a change needs its reason: the app never
  guesses how a lord feels.

**You type:** the ticks, and each attitude's change and reason.

**The app works out:** everything applied goes into one entry, *The
world turns, Winter 1220*, under The World Turned on Seasons. Delete
that entry to undo all of it; a value changed by hand since is left as
it is, and you are told.

Cancel stops Advance Season: the date stays.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons)

# Season Summary
<!-- help: season-summary -->

<!-- tui -->
Shown after a season has been advanced, when anything happened: what the season gave everyone, grouped by covenant.

**You type:** nothing. Enter, Escape or Close closes it.
<!-- /tui -->
<!-- gui -->
Shown after a season has been advanced, when anything happened: the **Just played** chapter of the [Seasons](help:seasons) page, first in its rail, says what the season gave everyone, grouped by covenant.

**You type:** nothing.
<!-- /gui -->

**The app works out:** one line per person: the activity, what it was on and its result (for example the xp gained). A plan that couldn't be carried out shows why; a magus or companion with nothing planned is shown as "nothing planned". In Winter it also lists aging rolls, grogs' yearly updates and business upkeep, and in any season the covenants' vis harvests.

The note at the bottom says whether the season is kept
<!-- tui -->
under Seasons in the tree.
<!-- /tui -->
<!-- gui -->
on the Seasons page.
<!-- /gui -->
If season records are off (Edit Saga), each character's Diary still has their entry.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons), [How to plan and run a season](help:guide-seasons)

# Creation Worksheet
<!-- help: creation-worksheet -->

Walks a covenant, laboratory or character that is In Creation through the book's steps, showing each step's budget, what was spent or taken there, and its checks.
<!-- tui -->
It fills the screen, and opens by itself when you make a new covenant, laboratory or character.

**You type:** nothing in the worksheet itself. Its keys and buttons open the same dialogs as the sheet, and they edit the real record; everything is saved as you go.
<!-- /tui -->
<!-- gui -->
It is a page of its own, below the record's in the trail, and opens by itself when you make a new covenant, laboratory or character.

**You type:** nothing in the worksheet itself. Its buttons open the same forms as the record's page, and they edit the real record; everything is saved as you go.
<!-- /gui -->

**The app works out:** each step's budget and what is spent, and the creation checks, worked out again whenever a dialog closes.

### In Creation and In Play
<!-- help: creation-worksheet-modes -->

<!-- tui -->
A new covenant, laboratory or character starts **In Creation**, with its tree node marked "(creating)".
<!-- /tui -->
<!-- gui -->
A new covenant, laboratory or character starts **In Creation**, shown in its page's header.
<!-- /gui -->
A character made from a template starts **In Play**, since the book's templates are fully made.

<!-- tui -->
The record's top panel has a button showing the mode; clicking it, or More's **In Creation / In Play**, switches between them after a confirmation.
<!-- /tui -->
<!-- gui -->
The record's header has a button showing the mode; clicking it switches between them after a confirmation, and the page changes its colours to match.
<!-- /gui -->
Creation checks only run while a record is In Creation, and come back if it is moved back. When a covenant moves to In Play, the app keeps what its Build Points were spent on.

<!-- tui -->
Open the worksheet from the top panel's **Creation Worksheet** button, or from More's **Creation Worksheet** on the record's tree node or top panel. Both are only there while the record is In Creation.
<!-- /tui -->
<!-- gui -->
Open the worksheet with **Worksheet** beside the mode button. It is only there while the record is In Creation.
<!-- /gui -->

### Steps and their marks
<!-- help: creation-worksheet-steps -->

<!-- tui -->
The left column lists the steps:
<!-- /tui -->
<!-- gui -->
The rail on the left lists the steps:
<!-- /gui -->

- a character: Concept, Virtues and Flaws, Characteristics, Early Childhood, Later Life, Apprenticeship and Years past Gauntlet (magi only), and Finishing Touches;
- a covenant: Baseline, Resources, Boons & Hooks, and Review;
- a laboratory: Setting Up, and Review.

Each step is marked by how its checks stand:

- **✔** every check passes;
- **✘** a rule the book says must be followed is broken (a warning);
- **☞** advice: something the book says should be done isn't, such as too many or too few of something;
- **○** the step has no checks.

<!-- tui -->
Below the list the app counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Up and Down choose a step; Tab moves to the step's list, then its buttons; Escape closes the worksheet. On the right, the step shows its budget and what is left, its list, its checks (each with what the record has), and buttons for its other edits, for example Edit Characteristics, Learn a spell or Buy a specialist. The chosen row's details show at the bottom: a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

The step's list works like every list on the sheets: **a** adds (Add a Virtue on Virtues and Flaws, where F2 in the picker turns to Flaws; Spend xp on the xp steps), **e** changes the chosen row and **d** takes it back after asking.
<!-- /tui -->
<!-- gui -->
The page's header counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Click a step in the rail to show it. The step shows its budget and what is left, its list, its Creation Checks (each with what the record has), and under **This Step** buttons for its other edits, for example Edit Characteristics, Learn a spell or Buy a specialist. Clicking a row of the list shows its details in the inspector on the right: a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

The step's list has its own buttons: one that adds (**Add a Virtue** on Virtues and Flaws, with **Add a Flaw** under This Step; **Spend xp** on the xp steps), and, for the row last clicked, **Change its xp** and **Take it back** (or **Remove**), which asks first.
<!-- /gui -->
On an xp step each row shows the pool xp spent and the xp it gained, which is half again with an Affinity, rounded up on the whole spend. The Spend xp dialog shows, as you type, what the pool xp gains, the score that buys and the pool xp the next score needs, and warns past the creation cap; an Ability's Specialty can be given there too. Taking xp back always gives back the pool xp spent and takes off exactly what it gained. On the Later Life step, taking back a training package's row drops the whole package.

<!-- gui -->
Each budget is also a bar that fills as it is spent: gold while some is left, red once it is over, with the sums beside it. Every xp step (Early Childhood, Later Life, Apprenticeship, Years past Gauntlet) adds **Experience So Far**: each Ability and Art the worksheet has put xp into, with what each step gave it (this step's column first, in bold), the total and the score it buys, so a step shows what the others already gave. Above the steps, **Rules broken** names each step with a rule that must hold and doesn't, and how many; click one to go to that step (its rules are in the line's tooltip).
<!-- /gui -->

The Ability cap at creation goes by age (5 under 30); an Affinity with the Ability raises it by 2 for that Ability, and Mentored by Demons lifts it. Puissant never counts, since it adds only when the Ability is used. While a character is In Creation, the sheet's Edit Ability and Edit Arts say how much xp came from the worksheet: take that back on the worksheet, not by lowering the total. The checks follow Ars Magica Definitive Edition, Chapter 3: Characters, Detailed Character Creation Summary, for characters, and Ars Magica Definitive Edition, Chapter 6: Covenants, for covenants.

### Moving to In Play
<!-- help: creation-worksheet-play -->

The last step has **Move to In Play**. It lists every check that doesn't pass and asks before moving the record. A covenant with Build Points left over is told how many: moving it to In Play turns them into Mythic Pounds in its Wealth, 10 pounds for each Build Point (the rate money is bought at).

Checks never stop an edit. If the saga has **Enforce creation rules strictly** turned on (Edit Saga), a record that breaks a rule it must follow stays In Creation until that is fixed. Advice never stops it.

**See also:** [Characters group](help:character-group), [The saga](help:saga), [How to create a character, covenant or laboratory](help:guide-creation)

# Import Data
<!-- help: import-data -->

<!-- tui -->
Brings records into the saga from files. Open it from More's **Import** on the saga node.

**You choose:** what to import, then the file: the terminal lists the folders and files of that kind.
<!-- /tui -->
<!-- gui -->
Brings records into the saga from files. Open it from **Import** in the saga page's **Saga Management** chapter.

**You choose:** what to import, then the file, in the desktop's Open window.
<!-- /gui -->

**The app works out:** a preview of what the file adds, shown before anything is added.

### What can be imported
<!-- help: import-data-kinds -->

- **Characters**, **Covenants** and **Laboratories**: a file exported from another saga with Export. The file must hold the kind you chose. The file picker starts in the exports folder.
- **A Whole Saga**: a file written by **Export Saga**. Every covenant, laboratory, character and familiar in it is added beside this saga's own, with their books and devices and the saga's own spells and house rules, as importing each record would; so are its places, neighbours and calendar entries, and its Tribunals, joined to this saga's own of the same name.
- **A Content Pack**: a file written by **Export Pack**. Its Tribunals, covenants, characters, places, neighbours and calendar entries are added, except those this saga already has one of the same name of: those are kept as they are, and the pack's links to them go to this saga's own. See [Content packs](help:export-pack).
- **Books**: a CSV file with a header row. Columns, in any order and any case: name, type, language, author, year_published, description, art, ability, level, quality, tractatus_type, spell, codex, encyclopedia, opus and physical_form; name and type are needed. Rows with the same codex are bound together in one new codex of that name, an encyclopedia when its rows' encyclopedia column says yes. A tractatus's opus can be commentary or correspondence; physical_form is one of exemplar, flap-bound, juvenilia, edition de luxe, treasure-bound, ex libris, holographic, huge codex, unbound or damaged. A level or quality of "var" means the figure is to be set later: the book is imported, highlighted until you edit it to give its numbers, and can't be studied until then. Books imported here go to Unassigned Books.
<!-- tui -->
From a covenant's **Library** tab, More's Import puts them straight into that covenant's library instead.
<!-- /tui -->
<!-- gui -->
**Import**, a button on a covenant's Library, imports books straight into that covenant's library instead.
<!-- /gui -->
An owner or cost column is ignored: the cost is always worked out.
- **Spells**: a CSV file, through the [Import Spells](help:import-spells) helper.

A row that can't be read is skipped, and the preview says why. When a book or spell has the name of one already in the saga, the app asks: Skip, Skip All, Duplicate or Duplicate All. Nothing is added until every question is answered, and cancelling a question imports nothing.

### Importing an exported record
<!-- help: import-data-records -->

What travels with the record comes too, and everything imported gets new ids. Links to records that aren't in the file (a character's covenant, a laboratory's owner, a book's author) are matched by name to the one record of that kind and name in this saga, or dropped; the preview lists which. A record with the same name as one already here is added beside it. Nothing already in the saga is changed, except that a laboratory with no owner, or a magus with no laboratory, can be linked to the imported partner the file names.

### Exporting
<!-- help: import-data-export -->

<!-- tui -->
More's **Export**, on a covenant's, laboratory's or character's tree node or top panel, writes that record to a file another saga can import.
<!-- /tui -->
<!-- gui -->
**Export**, in a covenant's, laboratory's or character's **Manage** chapter (the last one on its page, with Update from a File and Delete), writes that record to a file another saga can import.
<!-- /gui -->

**You type:** the File to write (it starts in the exports folder, and `.amm.json` is added if you give no `.json` ending), and for a covenant whether to include its laboratories and characters. The line above Export warns when the file exists and will be replaced.

What goes with it:

- a character: their familiar, the enchanted devices they hold, their books and their Diary;
- a laboratory: its books and the devices kept in it;
- a covenant: its books and devices, and optionally its laboratories and characters with their own things;
- the saga's own spells and house rules that these use.

Season plans, season records and lab projects under way stay behind.

<!-- tui -->
**Export Saga**, in More on the saga node, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. In a browser copy, the file downloads instead. Only the storyguide can use it.
<!-- /tui -->
<!-- gui -->
**Export Saga**, a button in the saga page's **Saga Management**, beside Import, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**.
<!-- /gui -->

### Content packs
<!-- help: export-pack -->

A content pack is part of a saga's world written to one file, to fill
another saga with it or start a new saga from it: Tribunals, covenants,
characters, places, neighbours and calendar entries, with their links to
one another.

<!-- tui -->
**Export Pack**, in More on the saga node, writes one. Only the storyguide
can use it; in a browser copy the file downloads instead.
<!-- /tui -->
<!-- gui -->
**Export Pack**, a button in the saga page's **Saga Management**, writes
one.
<!-- /gui -->

**You choose:** the pack's name and file, and a tick for each Tribunal,
covenant, place and neighbour it holds. A Tribunal takes everything in
it: its covenants, the places they sit in (and the places round and
inside those), whoever is in those places, and the neighbours that hold
an attitude toward or a link to its covenants. A covenant of a ticked
Tribunal is not asked about. **With their characters** adds the
covenants' characters and laboratories and each Tribunal's Praeco and
Presiding Quaesitor; **With the calendar** the covenants' calendar
entries and the saga's own. The line above Export says what the pack
holds.

A Tribunal's meeting under way stays behind, and its Diary comes without
what its entries changed.

**Importing a pack** (Import, **A Content Pack**) asks first what to bring
in, then shows what it adds, what this saga already has of the same name (kept as it is, with
the pack's links pointing to it, and the books, devices and familiars of
those records skipped), what else is skipped (a calendar entry already in
the calendar, or one for a covenant that isn't here), and the links kept
and dropped. Importing the same pack twice adds nothing the second time.

**Starting a saga from a pack:** the Create a New Saga form offers **Start
from a pack**, listing the packs shipped with the app (one per Tribunal
sourcebook; see [How to start a saga from a Tribunal book](help:guide-book-packs))
and then any pack in the exports folder; the new saga begins with
everything in it. A pack built from a sourcebook puts that book in play
when it is imported.

### Printing a record
<!-- help: print-record; gui -->

On the desktop, a covenant's, laboratory's, character's or familiar's
**Manage** chapter has **Print to PDF**. It first asks a few options, then
where to save the file (it starts in the exports folder, named after the
record). The options you choose are kept for next time.

- **Paper size:** US Letter, or A4 outside North America.
- **Spells in the Grimoire** (characters only): **Short**, just each
  spell's Arts and level, Range, Duration and Target, Casting Total and
  Mastery; or **Full description**, which adds each spell's text.
- **Background** (characters only): **Textured parchment**, or **Plain
  white** to save ink.

A character prints as a sheet laid out for paper, not a picture of the
screen. Their name is set in the title lettering, with a bound edge down
the left of each page. Nothing is cut by the page edge: a table that fits
on a page is never split, and a heading always stays with what it heads.
A magus's Hermetic Arts, Grimoire, and Biography & Story each start a new
page; companions and grogs have no magic pages. Each Art and Ability has
its symbol beside it. The Grimoire lists the spells by Form. A Virtue or
Flaw taken more than once is printed once with its count, as **Great
Intelligence × 2**; the screens still show each one. Combat & Condition
follows the published character sheet. It has a box for each Fatigue
level and five for each Light, Medium and Heavy Wound, with the current
ones ticked. It also has blank lines to pencil in weapons, armor and
equipment, with the character's own already filled in. Empty sections
are left off.

Covenants, laboratories and familiars still print their page as it looks
on screen: the header, then each chapter under its name, in the
Scriptorum parchment colours, with the buttons left off. Manage, Planning
and Seasons are left off, since they are for the screen.

The PDF can be printed or sent like any other.

### Giving to another record
<!-- help: give -->

**Give** hands what one record holds to another record of the saga: the
chosen row of a Raw Vis list, a books list (a laboratory's Lab Texts too),
Enchanted Devices, a character's Personal Gear or a covenant's Weapons,
Armor or Items.
<!-- tui -->
It is in More (`m`) on those lists.
<!-- /tui -->
<!-- gui -->
It is a Give button beside the list's Add, Edit and Delete, acting on the row last clicked.
<!-- /gui -->
It asks who gets it and, for vis
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

<!-- tui -->
More's **Update from a File**, on a covenant's, laboratory's or character's tree node or top panel,
<!-- /tui -->
<!-- gui -->
**Update from a File**, in a covenant's, laboratory's or character's **Manage** chapter,
<!-- /gui -->
reads an export of that same record over it: for example after working on a character on another computer. Only the storyguide can use it.

**You choose:** the exported file. It must hold the same kind of record.

**The app works out:** what would change, field by field ("Abilities: 1 added, 2 changed", "Name: Old → New"), and the links in the file it can't match here. Nothing changes until you choose **Update**; a file that changes nothing says so.

What it replaces: the record's own contents, and what travels with it in an export (a character's familiar, devices and books; a laboratory's or covenant's books and devices). What it keeps: the record itself, so everything that points at it still does, and where it sits in this saga (a character's covenant and laboratory, a laboratory's covenant and owner). A covenant's file made with its laboratories and characters updates the covenant only; update each of them from its own export.

**See also:** [Import Spells](help:import-spells), [Unassigned Books](help:unassigned-books), [The saga](help:saga), [How to import and export](help:guide-import-export)

# Import a Content Pack
<!-- help: import-pack -->

The form shown after choosing a pack's file in Import Data, **A Content Pack**: which of its parts to bring in.

A pack's Tribunals and covenants always come in: they are what the rest
hangs on. The rest is a tick each, all ticked to begin with, and a part
the pack holds nothing of isn't asked about:

- **Their people**: the covenants' characters, laboratories and
  familiars, and each Tribunal's Praeco and Presiding Quaesitor.
- **Places and regiones**: the places the covenants sit in, the places
  round and inside those, and their regio levels.
- **The mundane world**: lords, towns, the Church, universities, factions
  and threats.
- **Code, cases and fines**: each Tribunal's Peripheral Code,
  docket and fines.
- **The history**: each Tribunal's Diary, and the calendar entries.

The line under the ticks says what the pack brings with the ticks as they
are. **Preview** then shows the import as above. What a left-out part
held is matched by name to this saga's own (a covenant's place, a
Tribunal's Praeco) or the link is dropped, and the preview lists which;
a covenant whose place is left out sits nowhere until you place it.
Starting a saga from a pack brings everything.

**See also:** [Content packs](help:export-pack), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Import Spells
<!-- help: import-spells -->

Explains what a spell CSV file looks like before you choose one. Tick **Save an example CSV instead** to save one to start from, rather than choosing a file. The spells imported become the saga's own spells, which you can edit on [Spells](help:tab-content-spells).

<!-- tui -->
Open it from More's Import on the saga node, then Spells.
<!-- /tui -->
<!-- gui -->
Open it from **Import** in the saga page's Saga Management chapter, then Spells.
<!-- /gui -->

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

- **Choose CSV File** goes on to pick the file.
- With **Save an example CSV instead** ticked, it writes `spells_example.csv` (numbered if it exists) to the folder the app was started from, with two example spells, instead. Edit it, then choose it to import.
- **Cancel** closes the helper.

**See also:** [Spells](help:tab-content-spells), [Import Data](help:import-data), [How to import and export](help:guide-import-export)
