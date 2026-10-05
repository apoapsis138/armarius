# How to bind and keep a familiar
<!-- help: guide-familiars -->

This guide follows a familiar from the magus's first meeting with the creature to a bond strengthened with powers. Use it when a magus in your saga is ready to bind a familiar, or when you are adding a magus who already has one. The rules are in Ars Magica Definitive Edition, Chapter 8: Laboratory, Familiars.

### Finding the familiar
<!-- help: guide-familiars-finding -->

Finding a suitable creature and winning it over is a matter for your stories, not for the app. Play it out at the table; the app only comes in once the creature has agreed to the bond.

A magus can have one familiar at a time, so Bind Familiar is only offered while at least one magus in the saga has none.

### Making the familiar's record
<!-- help: guide-familiars-record -->

1. In the tree, select the magus's node (or the saga, a covenant or a Characters node).
2. Press `n` (New) and choose **Bind Familiar**.
3. In the Bind a New Familiar form, type the familiar's **Name** and choose its **Magus Partner**. When you started from the magus's own node, they are already chosen. Choose **Create**.
4. The familiar's sheet opens. In the tree, the magus's node now has the familiar beneath it, as "Familiar: " and its name; select it there to come back to the [Familiar sheet](help:familiar) later.

Making the record grants the bond at once: both the magus and the familiar gain the True Friend Virtue and a Loyal (Partner) +3 Personality Trait. You can see them on the magus's [Virtues & Flaws tab](help:tab-vf) (`3`) and the familiar's [Identity & Cords tab](help:tab-fam-identity) (`1`).

### Describing the creature
<!-- help: guide-familiars-creature -->

Type in the creature's statistics as the rules or your storyguide give them.

1. On the [Familiar Info](help:section-fam-info) panel at the top, press `e` and fill in its Species / Description, Magic Might Score, Current Might Pool, Size and Wound Multiplier. The binding below needs the Might and Size.
2. On the [Characteristics tab](help:tab-fam-characteristics) (`2`), press `e` to type the eight Characteristics, Base Soak and Magic Resistance.
3. On the [Combat & Health tab](help:tab-fam-combat) (`3`), add its natural weapons with `a` in [Natural Weapons & Attacks](help:section-fam-natural-weapons).
4. On the [Abilities tab](help:tab-fam-abilities) (`4`), add its Abilities with `a`. It shares its magus's Language scores, so there is no need to add those.
5. Back on the Identity & Cords tab, add its Virtues and Flaws with `a` in [Virtues](help:section-fam-vf-virtues) and [Flaws](help:section-fam-vf-flaws), and any [Personality Traits](help:section-fam-personality-traits) and [Reputations](help:section-fam-reputations).

### Binding it in the laboratory
<!-- help: guide-familiars-binding -->

Binding the familiar is a season of lab work, planned in the magus's laboratory. The laboratory must have the magus as its owner.

1. Select the laboratory in the tree and open its [Planning tab](help:tab-lab-planning) (`1`).
2. Choose the season and press `e`. The [Invent Spell screen](help:invent-spell) opens.
3. In **Lab work**, choose **Bind or strengthen a familiar**.
4. Choose the **Technique** and **Form** the bond is made with, and type the **Golden cord**, **Silver cord** and **Bronze cord** scores you want, each 0 to 5.
5. In **Vis from**, choose whose raw vis pays (the laboratory's, the magus's own or the covenant's stores), and in **Art** whether it is vis of the Technique or the Form.
6. Check the Lab Total panel. The binding needs a Lab Total of at least 25 + Might + 5 x Size, and the Lab Total also pays for the cords (0, 5, 15, 30, 50 and 75 points for scores 0 to 5). The vis is a fifth of the Lab Total, rounded up, and the magus can handle no more than twice their Magic Theory in a season. You can tick Experiment, as for other lab work.
7. Choose **Schedule**. If something is wrong, the screen says what.
8. Press `t` to [advance the season](help:advance-season) when the troupe is ready.

When the season is applied, the app fills in the [Binding & Cords](help:section-fam-binding) section: the Arts used, the Lab Total, the binding level, the vis spent and the three cords. It also sets the season and year bound if they were blank.

To strengthen the bond later, plan **Bind or strengthen a familiar** again with higher cords. The vis already spent on the bond is taken off what the new binding costs.

A familiar bound before play starts can skip the lab work: on the Identity & Cords tab, press `e` on Binding & Cords and type the details and cords in.

### Giving the bond powers
<!-- help: guide-familiars-powers -->

Bond powers are instilled much like an effect in an enchanted device, and can take several seasons.

1. On the familiar's [Bond Powers tab](help:tab-fam-powers) (`5`), press `a`. Type the Power Name, Level, Technique, Form and the rest, and set **Instilling (blank = finished)** to 0.
2. In the laboratory's Planning tab, choose a season and press `e`. In **Lab work**, choose **Empower the familiar's bond**, then choose the power in **Bond power** and the vis Art.
3. Choose **Schedule**. The Lab Total must be above the power's level. Each season adds the Lab Total less the level in points, and the vis (a tenth of the level, rounded up) is paid in the first season. The app plans the following seasons the work is projected to need.

When the power's points reach its level, the power is finished. A power the familiar already had can be added with Instilling left blank.

### What the app works out, and what it doesn't
<!-- help: guide-familiars-limits -->

The app works out the point cost of each cord, whether a binding or empowerment can be done, its Lab Total, its vis, and the progress of a power over several seasons. The Bronze Cord is taken off the magus's aging roll each Winter.

Most of the familiar's own figures are typed in: its Soak, Magic Resistance and Might, its wounds and penalties, and each bond power's figures. The Golden and Silver Cords are shown with what they do, but their bonuses are yours to apply in play, and the True Friend Virtue is recorded but has no effect the app applies.

Deleting the magus also deletes their familiar, and exporting the magus takes the familiar with them.

**See also:** [Familiar sheet](help:familiar), [Binding & Cords](help:section-fam-binding), [Bond Powers tab](help:tab-fam-powers), [Planning tab](help:tab-lab-planning), [Invent Spell screen](help:invent-spell), [Advancing a season](help:advance-season)

# How to import and export
<!-- help: guide-import-export -->

This guide covers moving records between sagas, bringing books and spells in from spreadsheet (CSV) files, and keeping copies of your saga safe. Use it when a player brings a character from another saga, when you want to type a long list of books or spells in a spreadsheet, or before you try something you might want to undo.

### Exporting a covenant, laboratory or character
<!-- help: guide-import-export-export -->

1. In the tree, select the covenant, laboratory or character you want to move. Leave focus on its tree node or on the panel at the top of its sheet.
2. Press `m` (More) and choose **Export**.
3. In the Export dialog, check the **File**. It starts in the app's exports folder (`data/exports`) with a name made from the record's name; `.amm.json` is added if you give no `.json` ending. The line above Export warns when the file exists and will be replaced.
4. For a covenant, tick **With its laboratories and characters** to take them too.
5. Choose **Export**.

What goes with the record, and what stays behind, is listed under [Exporting](help:import-data-export). In short: a character takes their familiar, their enchanted devices, their books and their Diary; a laboratory takes its books and devices; and the saga's own spells and [House Rules](help:house-rules) that these use go too. Season plans and lab work under way stay behind.

### Importing a record into another saga
<!-- help: guide-import-export-records -->

1. Open the saga that should receive the record, and select [the saga](help:saga) at the top of the tree.
2. Press `m` (More) and choose **Import**. The [Import Data](help:import-data) dialog opens.
3. Choose **Characters**, **Covenants** or **Laboratories**, matching what the file holds.
4. Choose the file. The file picker starts in the exports folder; Enter opens a folder or picks a file, and you can also type a path in the box at the top.
5. Read the preview and choose **Import**.

The preview lists what will be added, the links kept and the links dropped. [Importing an exported record](help:import-data-records) explains the rules:

- Everything imported gets new ids, so nothing in this saga is overwritten. A record with the same name as one already here is added beside it, and the preview says so.
- A link to a record that isn't in the file, such as a character's covenant or a laboratory's owner, is kept only if this saga has exactly one record of that kind with that name. Otherwise it is dropped, and you can set it again on the sheet.
- A saga-made spell is matched to one here with the same name, Technique, Form and level. A House Rule is matched to one with the same name, type and tier. Anything not matched is added.

### Importing books from a CSV file
<!-- help: guide-import-export-books -->

1. Make a CSV file with a header row. The columns are listed under [What can be imported](help:import-data-kinds); **name** and **type** are needed. The cost of each book is worked out by the app, so an owner or cost column is ignored.
2. To import books with no owner, select the saga, press `m` (More), choose **Import**, then **Books**. They land in [Unassigned Books](help:unassigned-books), where you can mark several and give them an owner with `e`.
3. To import books straight into a covenant's library, open the covenant's [Library tab](help:tab-cov-library) (`6`) instead, and press `m` (More) and choose **Import** there.
4. Choose the file. This picker starts in the folder the app was started from.
5. Read the preview, which lists the books found and any rows skipped with the reason, and choose **Import**.

### Importing spells from a CSV file
<!-- help: guide-import-export-spells -->

1. Select the saga, press `m` (More), choose **Import**, then **Spells**. The [Import Spells](help:import-spells) helper opens and lists the columns it reads; **name**, **technique** and **form** are needed.
2. If you have no file yet, choose **Save example CSV**. It writes `spells_example.csv` with two example spells to the folder the app was started from. Edit it in a spreadsheet and save it as CSV.
3. Choose **Choose CSV file...** and pick the file.
4. Read the preview and choose **Import**.

The spells become the saga's own spells, which you can edit on [Spells](help:spells).

### When a name is already taken
<!-- help: guide-import-export-duplicates -->

When an imported book or spell has the name of one already in the saga, the app asks about each one: **Duplicate** adds it anyway, **Skip** leaves it out, and **Duplicate All** and **Skip All** answer the same for the rest of that import. Spell names are compared in any case. Nothing is added until every question is answered.

### Keeping backups
<!-- help: guide-import-export-backups -->

Each saga is saved as one file, `data/sagas/` followed by the saga's id and `.json`, in the app's folder. The app saves every change as you make it.

- Before a season with plans is applied, the app copies the saga to `data/sagas/backups`, replacing the previous backup. To undo that season, copy the backup over the saga's file with the app closed.
- That is the only backup the app keeps, so for anything older, copy the saga's file yourself from time to time.
- To keep a single character, laboratory or covenant safe before a big change, export it as above.

**See also:** [Import Data](help:import-data), [Import Spells](help:import-spells), [Unassigned Books](help:unassigned-books), [Library tab](help:tab-cov-library), [House Rules](help:house-rules), [The saga](help:saga), [Advancing a season](help:advance-season)
