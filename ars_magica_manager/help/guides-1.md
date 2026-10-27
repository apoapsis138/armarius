# How to plan and run a season
<!-- help: guide-seasons -->

<!-- tui -->
This guide walks through one season of play: planning what everyone does, checking that nobody has been forgotten, advancing the saga with `t`, and reading what the season gave. Use it whenever the troupe finishes a season's stories and is ready to move the saga on.
<!-- /tui -->
<!-- gui -->
This guide walks through one season of play: planning what everyone does, checking that nobody has been forgotten, advancing the saga with **Advance Season**, and reading what the season gave. Use it whenever the troupe finishes a season's stories and is ready to move the saga on.
<!-- /gui -->

Nothing changes when you plan. Every plan waits until the season is advanced, and is applied then.

### Who is planned where
<!-- help: guide-seasons-who -->

Different people are planned in different places:

<!-- tui -->
- **A magus's laboratory work** (inventing a spell, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned on their laboratory's [Planning tab](help:tab-lab-planning).
- **A magus's other activities** (reading, practice, teaching, writing and so on), and **every season of a companion or Mythic Companion**, are planned on the character's [Planning tab](help:tab-planning) or on the covenant's [Seasons tab](help:tab-cov-seasons). Both open the same [Plan Season](help:plan-season) dialog.
<!-- /tui -->
<!-- gui -->
- **A magus's laboratory work** (inventing a spell, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned in the **Planning** section of their laboratory's **Seasons** chapter (see [Planning tab](help:tab-lab-planning)).
- **A magus's other activities** (reading, practice, teaching, writing and so on), and **every season of a companion or Mythic Companion**, are planned in the character's [Planning](help:tab-planning) chapter or the covenant's [Seasons](help:tab-cov-seasons) chapter. Both open the same [Plan Season](help:plan-season) form.
<!-- /gui -->
- **Grogs** aren't planned season by season. Each has a [yearly update](help:grog-year), applied when Winter is advanced.

Each magus, companion and Mythic Companion has one plan per season, wherever it was made.

### Planning a character's season
<!-- help: guide-seasons-plan -->

<!-- tui -->
1. In the tree, open the covenant, then **Characters**, and choose the character. Press Enter to move into their sheet.
2. Press `6` for the **Planning** tab. The **This Season** section names the season, or says "Nothing planned".
3. Press `e` (or `a`). The Plan Season dialog opens, titled with the character's name and the season.
<!-- /tui -->
<!-- gui -->
1. On the saga's page, click the covenant's card, then the character's card in the **People** chapter. Their sheet opens.
2. Choose **Planning** in the rail on the left. The **This Season** section names the season, or says "Nothing planned".
3. Click **Plan** (or **Edit**, once a plan is made). The Plan Season form opens in place of the section, titled with the character's name and the season.
<!-- /gui -->
4. Choose the **Activity**: it opens a list grouped by Type (Study, Writing & books, Work & trade and so on). Narrow it with **Type** or **Book**, or type part of the name, then choose one; the character's recent activities are at the top. See [Finding an activity](help:guide-seasons-find). The form then shows only the fields that activity needs, such as **Experience in**, a **Book**, a **Teacher / master** or a **Source Quality**. Leave **Stress die (blank: rolled)** empty to let the app roll when the season is applied.
5. Watch the line above Save: it shows what the season will give, or what is wrong with the plan. Save refuses a plan that breaks a rule until it is fixed.
6. Choose **Save**. This Season now shows the plan and its expected gains.

<!-- tui -->
To change a plan, press `e` again; to clear it, press `d` and confirm.
<!-- /tui -->
<!-- gui -->
To change a plan, click **Edit**; to clear it, click **Clear** and confirm.
<!-- /gui -->
To plan further ahead, use **Seasons Ahead** under This Season: it lists the next three seasons, a full year with this one.
<!-- tui -->
Highlight one and press `e` to plan it the same way (`a` plans the first free one, `d` clears one).
<!-- /tui -->
<!-- gui -->
Click one and **Edit** to plan it the same way (**Plan** plans the first free one, **Clear** clears one).
<!-- /gui -->
The form's **Season** field moves a plan to another season of the year. A season ahead's gains are worked out from the character as the seasons planned before it will leave them. See [Seasons Ahead](help:section-char-ahead).

To plan long work in one go, set the form's **For**. **Until it's done** plans reading a summa up to its Level, or writing, copying or translating a book, for every season it needs; **2 seasons** to **4 seasons** repeats any plan. When the season is advanced, Advance Season asks whether anything interrupted the work, and then works out again how many seasons it still needs. See [For several seasons](help:plan-season-repeat).

Teaching takes two plans, and the app makes the second one for you: saving **Be taught** plans the teacher's Teach for the same season, **Be trained** plans the master's season working at the Ability, and **Teach** with a **Student** plans the student's Be taught. Lab work naming an **Assistant** plans their **Assist in a laboratory**. Clearing either side clears both, after one question naming both people. See [Paired plans](help:plan-season-pairs).

### Finding an activity
<!-- help: guide-seasons-find -->

There are many activities, more with each sourcebook in play, so the Activity list can be narrowed:

<!-- tui -->
1. In the Plan Season form, press Enter on **Activity**. The list opens with the character's **Recent** activities first, then every activity under its Type.
2. Press F2 until the Type you want is shown above the list, for example **Study** or **Work & trade**; F2 past the last Type shows them all again. Or Tab to **Type** or **Book** and choose one.
3. Type part of the name, for example `read`, to narrow it further.
4. Use the arrow keys to highlight an activity: its summary and rule are shown under the list. Press Enter to choose it.
<!-- /tui -->
<!-- gui -->
1. In the Plan Season form, click **Activity**. The list opens with the character's **Recent** activities first, then every activity under its Type.
2. Choose a Type above the list, for example **Study** or **Work & trade**, or a **Book**.
3. Type part of the name, for example `read`, to narrow it further.
4. Click an activity: its summary and rule are shown beside the list. Double-click it, or click **Choose**.
<!-- /gui -->

The laboratory's **Lab work** list works the same way, with its own Types: Inventing, Enchanting, Familiar, Texts and vis, and The laboratory.

### Planning lab work
<!-- help: guide-seasons-lab -->

<!-- tui -->
1. In the tree, open the covenant's **Laboratories** group and choose the magus's laboratory. Its **Planning** tab (`1`) opens first.
2. The list shows the owner's seasons from the current one on, with "nothing planned" against a free season. Choose the season.
3. Press `e` to plan lab work for that season, or `a` to start inventing a new spell from a blank design. Either opens the [Invent Spell screen](help:invent-spell).
4. Choose the **Lab work** first, from its list grouped by Type (see [Finding an activity](help:guide-seasons-find)); the screen then asks only for what that work needs. The Lab Total and the When panel update as you type.
5. Press **Schedule**. For work that takes several seasons, the app also plans the following seasons it is projected to need.

`d` clears the chosen season's plan, and any later seasons scheduled to continue it, after asking. The laboratory needs a magus as its owner before anything can be planned.
<!-- /tui -->
<!-- gui -->
1. On the covenant's page, choose **Laboratories** in the rail and click the magus's laboratory.
2. Choose **Seasons** in the rail. Its **Planning** list shows the owner's seasons from the current one on, with "nothing planned" against a free season. Click the season.
3. Click **Plan** to plan lab work for that season, or **New Spell** to invent a spell: it first asks for a spell to start from (any spell, the magus's own known spells first), or "A new spell (a blank design)"; the form's **Start from** changes it later. Either opens the lab work form (see [Invent Spell screen](help:invent-spell)) in place of the list.
4. Choose the **Lab work** first, from its list grouped by Type (see [Finding an activity](help:guide-seasons-find)); the form then asks only for what that work needs. The line under the fields shows the Lab Total and when the work is done, updated as you type.
5. Click **Schedule**. For work that takes several seasons, the app also plans the following seasons it is projected to need.

**Clear** clears the clicked season's plan, and any later seasons scheduled to continue it, after asking. The laboratory needs a magus as its owner before anything can be planned.
<!-- /gui -->

### Setting up the grogs' year
<!-- help: guide-seasons-grogs -->

<!-- tui -->
1. Open the grog's sheet and press `6` for **Planning**, then `e`; or, on the covenant's Seasons tab, choose the grog in the **Grogs** list and press `e`.
<!-- /tui -->
<!-- gui -->
1. Open the grog's sheet, choose **Planning** in the rail and click **Yearly Update**; or, in the covenant's **Seasons** chapter, click the grog in the **Grogs** list and click **Plan**.
<!-- /gui -->
2. In the Yearly Update form, choose the **Vocational training** Ability and its xp, the **Practice (4 xp)** Ability, the two **Exposure (2 xp)** Abilities, and the **Story awards this year**.
3. Choose **Save**. The update can be changed any time before Winter is advanced.

### Checking that everyone has a plan
<!-- help: guide-seasons-check -->

<!-- tui -->
1. Choose the covenant in the tree and press `3` for the **Seasons** tab.
<!-- /tui -->
<!-- gui -->
1. Open the covenant's page and choose **Seasons** in the rail.
<!-- /gui -->
2. The **Magi** and **Companions** titles count how many are planned this season, for example "Magi (2 of 3 planned)". Each row is a person, with a column for this season and each of the three after it: the activity planned, or "nothing" (this season's in the warning colour). Companions also show **Worked**, their working seasons this year out of those they owe ("1 of 2"; Wealthy owes one, Poor three). Grogs show "yearly".
<!-- tui -->
3. Use Tab to move between the lists and the arrow keys to choose someone. The details panel shows their plan in full.
4. Press `e` (or `a`) on a magus or companion to plan their season here: the form opens on this season, and its **Season** field moves the plan to a season ahead to fill a gap on the board. `d` clears this season's plan. Lab work is still planned on the laboratory's Planning tab.

People marked departed on the Inhabitants tab are left out of this tab and aren't planned.
<!-- /tui -->
<!-- gui -->
3. Click someone. The inspector on the right shows their plan in full.
4. Click **Plan** to plan a magus's or companion's season here: the form opens on this season, and its **Season** field moves the plan to a season ahead to fill a gap on the board. **Clear** clears this season's plan. Lab work is still planned on the laboratory's Seasons chapter.

People marked departed in the Covenfolk chapter are left out of this chapter and aren't planned.
<!-- /gui -->

Anyone still left with nothing planned isn't lost: when the season is advanced, the saga's default for their kind applies (Edit Saga: Work / Exposure, or Nothing). Advance Season names the player characters with nothing planned and asks about each; non-player characters take the default quietly, unless **Be notified when and which non-player characters do not have seasonal activity** is ticked. See [Unplanned seasons](help:advance-unplanned).

### Advancing the season
<!-- help: guide-seasons-advance -->

<!-- tui -->
1. Press `t` from anywhere in the workspace. The **Advance Time** dialog asks whether to advance from this season to the next.
2. Read its summary: how many planned seasons will be applied, who has nothing planned (they gain nothing this season), and any plan that can't be carried out, with the reason. To fix anything, choose Cancel, change the plan and press `t` again.
<!-- /tui -->
<!-- gui -->
1. Click **Advance Season** at the top of the window, after the date (for example "Spring 1220 · Advance Season"). It can be clicked from any page of the saga. A question asks whether to advance from this season to the next.
2. Read its summary: how many planned seasons will be applied, who has nothing planned (they gain nothing this season), and any plan that can't be carried out, with the reason. To fix anything, choose Cancel, change the plan and click Advance Season again.
<!-- /gui -->
3. Choose **Advance**.
4. The app may then ask a few questions: which contested vis or income sources whose security has lapsed were secured this season, and, for an experiment seeking a Discovery, whether to use the risk to move the roll. In Winter it first asks about any covenant in deficit (see below).
5. Before anything is applied, the saga is backed up to `sagas/backups` in your data folder (Armarius in your OneDrive folder).

See [Advance Season](help:advance-season) for how the plans are applied.

### Reading the results
<!-- help: guide-seasons-results -->

<!-- tui -->
1. When anything happened, the [Season Summary](help:season-summary) ("The Season's Results") opens: one line per person, grouped by covenant, with the activity and what it gave. A plan that couldn't be carried out says why. Press Enter, Escape or Close to close it.
2. A message names the new date and whose seasons were applied. The date in the header moves on.
3. Each character's **Diary** tab (`7`) has an entry for the season, as does the laboratory's Diary tab (`6`) for lab work and the covenant's Diary tab (`9`) for vis harvests.
4. With Keep season records on (Edit Saga), the season is also kept under [Seasons](help:seasons) in the tree. Choose it and press Enter to browse past seasons, newest first.

The season's plans are removed once applied, so every This Season section starts empty again. Lab work that takes several seasons stays scheduled on the laboratory's Planning tab.
<!-- /tui -->
<!-- gui -->
1. When anything happened, the saga's [Seasons](help:seasons) page opens on its **Just played** chapter (the [Season Summary](help:season-summary)): one row per person, grouped by covenant, with the activity and what it gave. A plan that couldn't be carried out says why. When nothing happened, a message says so instead.
2. The date on the Advance Season button moves on.
3. Each character's **Diary** chapter has an entry for the season, as does the Diary in the laboratory's Seasons chapter for lab work and the covenant's Diary chapter for vis harvests.
4. With Keep season records on (Edit Saga), the season is also kept on the [Seasons](help:seasons) page. To browse past seasons later, open the saga's **Seasons** chapter and click **The Seasons Played**; the rail lists them newest first.

The season's plans are removed once applied, so every This Season section starts empty again. Lab work that takes several seasons stays scheduled in the laboratory's Planning list.
<!-- /gui -->

### Winter and the end of the year
<!-- help: guide-seasons-winter -->

Advancing Winter also closes the year:

<!-- tui -->
1. If any covenant spends more than it earns, the app asks whether to advance anyway. No leaves the date alone: balance the books on the covenant's [Economics tab](help:tab-cov-economics), then advance again. Advance anyway rolls the year over.
<!-- /tui -->
<!-- gui -->
1. If any covenant spends more than it earns, the app asks whether to advance anyway. No leaves the date alone: balance the books in the covenant's [Treasury](help:tab-cov-economics) chapter, then advance again. Advance anyway rolls the year over.
<!-- /gui -->
2. Each grog's yearly update is applied, yearly Warping Points are added where they are due, and aging rolls are made for those who need them. The updates and aging rolls appear in the Season Summary and in each Diary.
3. Each covenant's surplus is added to its Wealth, and a deficit Emergency Savings didn't cover is taken from it (DE p. 189; letting Wealth fall below 0, the covenant broke, is the app's house rule). Inflation grows a pound for every hundred pounds spent, unless spending fell (DE p. 193), and Emergency Savings start again at 0.

### Undoing a mistake
<!-- help: guide-seasons-undo -->

<!-- tui -->
- **The date only:** choose the saga (the top node of the tree), press `m` for More and choose **Set Date**. Set the season and year and press Set. This moves the date without undoing anything the season did, and Wealth added at a year end isn't taken back. See [More on the saga](help:saga-more).
<!-- /tui -->
<!-- gui -->
- **The date only:** on the saga's page, choose **Seasons** in the rail and click **Set Date** beside The Date. Set the season and year and choose Set. This moves the date without undoing anything the season did, and Wealth added at a year end isn't taken back.
<!-- /gui -->
- **The whole season:** the backup in `sagas/backups` (in Armarius in your OneDrive folder) holds the saga as it was just before the last season was applied. Quit the app, copy the backup over the saga's file of the same name in `sagas`, then reopen the saga. The four backups before it are kept too, as `<name>.1.json` (the season before) to `<name>.4.json`: to go further back, copy one of those over the saga's file and rename it to the saga's name. No backup is taken when nothing was planned.

### What the app does for you
<!-- help: guide-seasons-auto -->

**You type:** each plan's activity and details, the grogs' yearly updates, dice rolls made at the table (optional), and your answers when advancing.

**The app works out:** what each plan will give before you save it, who has nothing planned, the dice left blank, every result when the season is applied, the Diary entries and season record, vis harvests, and in Winter the grogs' updates, aging, Warping and each covenant's Wealth. Every plan is worked out from the saga as it stood before the season, so one result can't change another in the same season.

**See also:** [Plan Season](help:plan-season), [Grog's Yearly Update](help:grog-year), [Advance Season](help:advance-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [Invent Spell screen](help:invent-spell), [How to manage the covenant](help:guide-covenant)

# How to manage the covenant
<!-- help: guide-covenant -->

This guide is a tour of running a covenant over the years of a saga: its people, its resources, its money, its books, its Boons and Hooks, and its history. Use it once the covenant is In Play, to find where each part of covenant life is kept and what the app keeps up to date for you.

<!-- tui -->
Choose the covenant in the tree and press Enter to open the [Covenant sheet](help:covenant). The top panel stays in view; the number keys `1` to `8` open its tabs.
<!-- /tui -->
<!-- gui -->
Click the covenant's card on the saga's page to open the [Covenant sheet](help:covenant). The header stays in view; the rail on the left lists its chapters. Each list has **Add**, **Edit** and **Delete** buttons beside its title; Edit and Delete act on the row last clicked.
<!-- /gui -->

### People
<!-- help: guide-covenant-people -->

<!-- tui -->
The [Inhabitants tab](help:tab-cov-inhabitants) (`3`) lists who lives at the covenant.

1. **Magi and companions with a sheet** are listed automatically. To add one, choose the covenant in the tree, press `n` for New and choose **New Character**; the covenant is already chosen. Their row on the [Magi](help:section-inh-magus) or [Companions](help:section-inh-companion) list appears at once.
2. **People without a sheet** are added with `a` on the Magi or Companions list, typing their details yourself.
3. **Grogs** are made with New Character too (type grog). Then, on [Specialists](help:section-inh-specialist), [Craftspeople](help:section-inh-craftsperson) or [Turb](help:section-inh-turb), press `a`: the app offers the covenant's grogs not yet on a list, or "(New person -- not from a character sheet)".
4. **Everyone else** goes on [Other Covenfolk](help:section-inh-inhabitant), each with a Covenant Role and a Quantity; [Horses](help:section-inh-horse) and [Livestock](help:section-inh-livestock) have lists of their own.
5. When someone leaves, `d` on a listed magus or companion marks them departed rather than deleting them. More's **Restore** brings them back.

[Loyalty](help:section-inh-loyalty) is at the top of the tab. Press `e` there to choose the Equipment, Money, Pension and other modifiers; the app works out the rest from the magi's Gifts, Living Conditions, specialists' roles, known Reputations (bad ones cost, good local ones gain) and the Diary. The [Inhabitants](help:section-inh-population) section shows whether there are enough Teamsters and Servants.
<!-- /tui -->
<!-- gui -->
The **People** chapter shows the covenant's characters as cards; the [Covenfolk](help:tab-cov-inhabitants) chapter lists everyone who lives there.

1. **Magi and companions with a sheet** are listed automatically. To add one, click the **New Magus** or **New Companion** card at the end of its group in the People chapter; the covenant is already chosen. Their row on the [Magi](help:section-inh-magus) or [Companions](help:section-inh-companion) list in Covenfolk appears at once.
2. **People without a sheet** are added with **Add** on the Magi or Companions list in Covenfolk, typing their details yourself.
3. **Grogs** are made with the **New Grog** card in People. Then, on [Specialists](help:section-inh-specialist), [Craftspeople](help:section-inh-craftsperson) or [Turb](help:section-inh-turb), click **Add**: the app offers the covenant's grogs not yet on a list, or "(New person -- not from a character sheet)".
4. **Everyone else** goes on [Other Covenfolk](help:section-inh-inhabitant), each with a Covenant Role and a Quantity; [Horses](help:section-inh-horse) and [Livestock](help:section-inh-livestock) have lists of their own.
5. When someone leaves, **Delete** on a listed magus or companion marks them departed rather than deleting them. **Add** on the same list offers them again, marked "(taken off the list)", to bring them back.

[Loyalty](help:section-inh-loyalty) is at the top of the chapter. Click its **Edit** to choose the Equipment, Money, Pension and other modifiers; the app works out the rest from the magi's Gifts, Living Conditions, specialists' roles, known Reputations (bad ones cost, good local ones gain) and the Diary. [The Household](help:section-inh-population) shows whether there are enough Teamsters and Servants.
<!-- /gui -->

### Resources
<!-- help: guide-covenant-resources -->

<!-- tui -->
The [Possessions tab](help:tab-cov-possessions) (`5`) holds what the covenant owns. Each list adds with `a`, edits with `e` and deletes with `d`.
<!-- /tui -->
<!-- gui -->
The [Possessions](help:tab-cov-possessions) chapter holds what the covenant owns. Each list has **Add**, **Edit** and **Delete**.
<!-- /gui -->

<!-- tui -->
1. **Ships:** add each on [Ships](help:section-pos-ship) from the book's table of ships; her damage levels, crew and artillery are worked out, and Stress Check and Ship Combat roll for her.
2. **Property and items:** [Properties and Land](help:section-pos-property) and [Items](help:section-pos-item) are a record only. [Weapons](help:section-pos-weapon) and [Armor](help:section-pos-armor) can be chosen from the catalogue, and feed the Weapons cost on the Economics tab.
3. **Sanctums:** every laboratory of the covenant is listed under [Sanctums](help:section-pos-sanctum) automatically; set only its Usage here.
4. **Vis sources:** add each on [Vis Sources](help:section-pos-vis_source) with its Art, Season and pawns, and mark it Contested or Dwindling if it is. In its season each year, the harvest is added to the Raw Vis Stores and written in the Diary.
5. **Raw vis:** [Raw Vis Stores](help:section-pos-vis_store) lists the covenant's vis by Art. To hand vis to a laboratory, a magus or another covenant, choose the store, press `m` for More and choose **Give**. Type the **Pawns** and choose **To**, then press Give. Both Diaries record it.
6. **Enchanted devices:** [Enchanted Devices](help:section-cov-devices) has More's **Instill an Effect** and **Use a Charge**.
<!-- /tui -->
<!-- gui -->
1. **Ships:** add each on [Ships](help:section-pos-ship) from the book's table of ships; her damage levels, crew and artillery are worked out, and Stress Check and Ship Combat roll for her.
2. **Property and items:** [Properties and Land](help:section-pos-property) and [Items](help:section-pos-item) are a record only. [Weapons](help:section-pos-weapon) and [Armor](help:section-pos-armor) can be chosen from the catalogue, and feed the Weapons cost in the Treasury.
3. **Sanctums:** every laboratory of the covenant is listed under [Sanctums](help:section-pos-sanctum) automatically; set only its Usage here.
4. **Vis sources:** add each on [Vis Sources](help:section-pos-vis_source) with its Art, Season and pawns, and mark it Contested or Dwindling if it is. In its season each year, the harvest is added to the Raw Vis Stores and written in the Diary.
5. **Raw vis:** [Raw Vis Stores](help:section-pos-vis_store) lists the covenant's vis by Art. To hand vis to a laboratory, a magus or another covenant, click the store, then **Give** beside Add, Edit and Delete. Type the **Pawns** and choose **To**, then choose Give. Both Diaries record it.
6. **Enchanted devices:** [Enchanted Devices](help:section-cov-devices) has **Instill** and **Use Charge** buttons beside Add, Edit and Delete, for the row last clicked.
<!-- /gui -->

### Money
<!-- help: guide-covenant-money -->

<!-- tui -->
The [Economics tab](help:tab-cov-economics) (`6`) shows a year's finances. Most figures are worked out from the rest of the sheet.

1. On [Wealth](help:section-eco-wealth), press `e` to type the pounds in store. Its right-hand column shows Total Income, Total Expenditure and the Surplus/Deficit.
2. On [Sources of Income](help:section-eco-income), `a` adds an enterprise with its Type; leave Current Income blank to use the Type's usual income. To apply a year's Income Modification, choose the source, press `m` and choose **Improve Income**: pick the Annual Improvement Effect, check the Projected Income, and press Commit.
3. On [Yearly Expenditure](help:section-eco-expenditure), type Tithes, Inflation and Sundry with `e`. The other rows are worked out; `e` on them edits only their note.
4. On [Cost Savings](help:section-eco-savings), laborers' and craftspeople's savings come from the Inhabitants tab. Type Magic savings with `e`.
<!-- /tui -->
<!-- gui -->
The [Treasury](help:tab-cov-economics) chapter shows a year's finances: the year's income, expenditure and Surplus or Deficit at the top. Most figures are worked out from the rest of the sheet.

1. On [Wealth](help:section-eco-wealth), click **Edit** to type the pounds in store.
2. On [Sources of Income](help:section-eco-income), **Add** adds an enterprise with its Type; leave Current Income blank to use the Type's usual income. To apply a year's Income Modification, click the source and then **Improve**: pick the Annual Improvement Effect, check the Projected Income, and choose Commit.
3. On [Yearly Expenditure](help:section-eco-expenditure), click Tithes, Inflation or Sundry and then **Edit** to type it. The other rows are worked out; Edit on them edits only their note.
4. On [Cost Savings](help:section-eco-savings), laborers' and craftspeople's savings come from the Covenfolk chapter. Click Magic and then **Edit** to type its savings.
<!-- /gui -->

**At the end of each year,** when Winter is advanced, the surplus is added to Wealth and Emergency Savings start again at 0.

<!-- tui -->
**With a deficit,** the app asks before closing the year whether to advance anyway. To cover it from Wealth, choose **Emergency Savings** on Cost Savings and press `e`: the app offers to draw the deficit, or as much as Wealth holds, from Wealth. A covenant with no Wealth to draw is broke. Advancing anyway takes what is left of the deficit from Wealth.
<!-- /tui -->
<!-- gui -->
**With a deficit,** the app asks before closing the year whether to advance anyway. To cover it from Wealth, click **Emergency Savings** on Cost Savings and then **Edit**: the app offers to draw the deficit, or as much as Wealth holds, from Wealth. A covenant with no Wealth to draw is broke. Advancing anyway takes what is left of the deficit from Wealth.
<!-- /gui -->

### Books
<!-- help: guide-covenant-books -->

<!-- tui -->
The [Library tab](help:tab-cov-library) (`8`) lists every book at the covenant, including those owned by its laboratories and characters, with each one's Location.

1. On [Books](help:section-lib-books), press `a` to add a book; it belongs to the covenant. `e` edits the chosen book.
2. To bring in many at once, press `m` and choose **Import** to read books from a CSV file into this covenant's library. A preview shows what will be added first. See [Import Data](help:import-data).
3. To give several books a new owner, mark them with Space and press `e`. A book bound in a codex moves with its whole codex.
<!-- /tui -->
<!-- gui -->
The [Library](help:tab-cov-library) chapter shows every book at the covenant, including those owned by its laboratories and characters, on shelves by kind. Click a book's spine to see its details in the inspector.

1. In the **Library** section, click **Add** to add a book; it belongs to the covenant. **Edit** edits the book last clicked.
2. To bring in many at once, click **Import** on the Library to read books from a CSV file into this covenant's library. A preview shows what will be added first. See [Import Data](help:import-data).
3. To give several books a new owner, click **Change Owner**, choose the **New owner** and tick the books. A book bound in a codex moves with its whole codex.
<!-- /gui -->
4. To bind books together, choose a **Codex** in each one's form (or a new one); the codex can be a palimpsest, an encyclopedia, a florilegium or a folio. A tractatus can be a commentary on a summa, and any book can have a physical form, such as an exemplar.
<!-- tui -->
5. To say how well the library serves research, press `m` and choose **Set Up Research Library**: a level for each subject it has books on.

The [Summary](help:section-lib-summary) counts the books by type, the codices, and the subjects the library aids research on. A book's details show its value, a price guide and its subject's research bonuses.
<!-- /tui -->
<!-- gui -->
5. To say how well the library serves research, click **Set Up Research Library** on the Library: it walks through each subject the library has books on, and you choose a level for each.

A book's details show its value, a price guide and its subject's research bonuses.
<!-- /gui -->

### Boons and Hooks
<!-- help: guide-covenant-boons -->

<!-- tui -->
The [Attributes tab](help:tab-cov-attributes) (`1`) holds the covenant's description, [Reputations](help:section-cov-reputations), [Boons](help:section-cov-boons) and [Hooks](help:section-cov-hooks).

1. Press `a` on Boons or Hooks to choose one from the catalogue, then `e` to give its detail and description.
2. The titles show the points the Boons cost and the Hooks provide; the app warns above the lists about Boons and Hooks that can't be taken together.
3. Some Boons change figures elsewhere, such as the Aura in the top panel or the Buildings cost.
<!-- /tui -->
<!-- gui -->
The [Attributes](help:tab-cov-attributes) chapter holds the covenant's description, [Reputations](help:section-cov-reputations), [Boons](help:section-cov-boons) and [Hooks](help:section-cov-hooks).

1. Click **Add** on Boons or Hooks to choose one from the catalogue, then click its card and **Edit** to give its detail and description.
2. Under each title are the points the Boons cost and the Hooks provide; the app warns above them about Boons and Hooks that can't be taken together.
3. Some Boons change figures elsewhere, such as the Aura in the header or the Buildings cost.
<!-- /gui -->

### The covenant's Diary
<!-- help: guide-covenant-diary -->

<!-- tui -->
The [Diary tab](help:tab-cov-diary) (`9`) is the covenant's history.

1. Press `a` to add an entry with a Year, Season, Category and Name, and any pounds, vis or Loyalty points.
<!-- /tui -->
<!-- gui -->
The [Diary](help:tab-cov-diary) chapter is the covenant's history.

1. Click **Add** to add an entry with a Year, Season, Category and Name, and any pounds, vis or Loyalty points.
<!-- /gui -->
2. A Story Event also has a Status (Open or Resolved), a year to revisit it, and can be linked to a Hook to count the stories told against it.
3. Only the Loyalty points change the sheet, through Actions and events on the Loyalty block.

The app adds its own entries for vis harvests, vis moved in or out, and contested resources that went unsecured.

### The Seasons tab
<!-- help: guide-covenant-seasons -->

<!-- tui -->
The [Seasons tab](help:tab-cov-seasons) (`4`) is the covenant's planning board: every magus, companion and grog, with what each has planned this season. Plan anyone's season from here with `e`, and set up a grog's yearly update the same way. See [How to plan and run a season](help:guide-seasons).
<!-- /tui -->
<!-- gui -->
The [Seasons](help:tab-cov-seasons) chapter is the covenant's planning board: every magus, companion and grog, with what each has planned this season, over a timeline of their seasons. Click someone and then **Plan** to plan their season from here, and set up a grog's yearly update the same way. See [How to plan and run a season](help:guide-seasons).
<!-- /gui -->

### What the app does for you
<!-- help: guide-covenant-auto -->

**You type:** the people without a sheet, the Loyalty choices, each possession, Wealth and the income sources, the typed costs and savings, books, Boons and Hooks, and Diary entries.

**The app works out:** the magi, companions and sanctums listed from their own sheets, Loyalty, the points of inhabitants, laboratories and weapons and armour, every calculated cost and saving, the Surplus/Deficit, the yearly vis harvests and Wealth, and the Library's counts and Locations.

**See also:** [Covenant sheet](help:covenant), [Build tab](help:tab-cov-build), [Advance Season](help:advance-season), [How to plan and run a season](help:guide-seasons)
