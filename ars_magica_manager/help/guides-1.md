# How to plan and run a season
<!-- help: guide-seasons -->

This guide walks through one season of play: planning what everyone does, checking that nobody has been forgotten, advancing the saga with `t`, and reading what the season gave. Use it whenever the troupe finishes a season's stories and is ready to move the saga on.

Nothing changes when you plan. Every plan waits until the season is advanced, and is applied then.

### Who is planned where
<!-- help: guide-seasons-who -->

Different people are planned in different places:

- **A magus's laboratory work** (inventing a spell, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned on their laboratory's [Planning tab](help:tab-lab-planning).
- **A magus's other activities** (reading, practice, teaching, writing and so on), and **every season of a companion or Mythic Companion**, are planned on the character's [Planning tab](help:tab-planning) or on the covenant's [Seasons tab](help:tab-cov-seasons). Both open the same [Plan Season](help:plan-season) dialog.
- **Grogs** aren't planned season by season. Each has a [yearly update](help:grog-year), applied when Winter is advanced.

Each magus, companion and Mythic Companion has one plan per season, wherever it was made.

### Planning a character's season
<!-- help: guide-seasons-plan -->

1. In the tree, open the covenant, then **Characters**, and choose the character. Press Enter to move into their sheet.
2. Press `6` for the **Planning** tab. The **This Season** section names the season, or says "Nothing planned".
3. Press `e` (or `a`). The Plan Season dialog opens, titled with the character's name and the season.
4. Choose the **Activity**. The dialog then shows only the fields that activity needs, such as **Experience in**, a **Book**, a **Teacher / master** or a **Source Quality**. Leave **Stress die (blank: rolled)** empty to let the app roll when the season is applied.
5. Watch the line above Save: it shows what the season will give, or what is wrong with the plan. Save refuses a plan that breaks a rule until it is fixed.
6. Press Save. This Season now shows the plan and its expected gains.

To change a plan, press `e` again; to clear it, press `d` and confirm. Teaching takes two plans: the teacher plans Teach and the student plans Be taught, for the same season. A helper in a laboratory plans **Assist in a laboratory** on their own sheet.

### Planning lab work
<!-- help: guide-seasons-lab -->

1. In the tree, open the covenant's **Laboratories** group and choose the magus's laboratory. Its **Planning** tab (`1`) opens first.
2. The list shows the owner's seasons from the current one on, with "nothing planned" against a free season. Choose the season.
3. Press `e` to plan lab work for that season, or `a` to start inventing a new spell from a blank design. Either opens the [Invent Spell screen](help:invent-spell).
4. Choose the **Lab work** first; the screen then asks only for what that work needs. The Lab Total and the When panel update as you type.
5. Press **Schedule**. For work that takes several seasons, the app also plans the following seasons it is projected to need.

`d` clears the chosen season's plan, and any later seasons scheduled to continue it, after asking. The laboratory needs a magus as its owner before anything can be planned.

### Setting up the grogs' year
<!-- help: guide-seasons-grogs -->

1. Open the grog's sheet and press `6` for **Planning**, then `e`; or, on the covenant's Seasons tab, choose the grog in the **Grogs** list and press `e`.
2. In the Yearly Update dialog, choose the **Vocational training** Ability and its xp, the **Practice (4 xp)** Ability, the two **Exposure (2 xp)** Abilities, and the **Story awards this year**.
3. Press Save. The update can be changed any time before Winter is advanced.

### Checking that everyone has a plan
<!-- help: guide-seasons-check -->

1. Choose the covenant in the tree and press `3` for the **Seasons** tab.
2. The **Magi** and **Companions** titles count how many are planned, for example "Magi (2 of 3 planned)". Each row shows what the person has planned, or "nothing planned"; grogs show "updated yearly".
3. Use Tab to move between the lists and the arrow keys to choose someone. The details panel shows their plan in full.
4. Press `e` (or `a`) on a magus or companion to plan their season here, or `d` to clear it. Lab work is still planned on the laboratory's Planning tab.

People marked departed on the Inhabitants tab are left out of this tab and aren't planned.

### Advancing the season
<!-- help: guide-seasons-advance -->

1. Press `t` from anywhere in the workspace. The **Advance Time** dialog asks whether to advance from this season to the next.
2. Read its summary: how many planned seasons will be applied, who has nothing planned (they gain nothing this season), and any plan that can't be carried out, with the reason. To fix anything, choose Cancel, change the plan and press `t` again.
3. Choose **Advance**.
4. The app may then ask questions, one at a time: whether each contested vis or income source whose security has lapsed was secured this season, and, for an experiment seeking a Discovery, whether to use the risk to move the roll. In Winter it first asks about any covenant in deficit (see below).
5. Before anything is applied, the saga is backed up to `sagas/backups` in your data folder (Ars Magica Manager in your OneDrive folder).

See [Advance Season](help:advance-season) for how the plans are applied.

### Reading the results
<!-- help: guide-seasons-results -->

1. When anything happened, the [Season Summary](help:season-summary) ("The Season's Results") opens: one line per person, grouped by covenant, with the activity and what it gave. A plan that couldn't be carried out says why. Press Enter, Escape or Close to close it.
2. A message names the new date and whose seasons were applied. The date in the header moves on.
3. Each character's **Diary** tab (`7`) has an entry for the season, as does the laboratory's Diary tab (`6`) for lab work and the covenant's Diary tab (`7`) for vis harvests.
4. With Keep season records on (Edit Saga), the season is also kept under [Seasons](help:seasons) in the tree. Choose it and press Enter to browse past seasons, newest first.

The season's plans are removed once applied, so every This Season section starts empty again. Lab work that takes several seasons stays scheduled on the laboratory's Planning tab.

### Winter and the end of the year
<!-- help: guide-seasons-winter -->

Advancing Winter also closes the year:

1. If any covenant spends more than it earns, the app asks whether to resolve the deficit first. Yes leaves the date alone: balance the books on the covenant's [Economics tab](help:tab-cov-economics), then press `t` again. No advances anyway.
2. Each grog's yearly update is applied, yearly Warping Points are added where they are due, and aging rolls are made for those who need them. The updates and aging rolls appear in the Season Summary and in each Diary.
3. Each covenant's surplus is added to its Wealth, and its Emergency Savings start again at 0. A deficit is never taken from Wealth by itself.

### Undoing a mistake
<!-- help: guide-seasons-undo -->

- **The date only:** choose the saga (the top node of the tree), press `m` for More and choose **Set Date**. Set the season and year and press Set. This moves the date without undoing anything the season did, and Wealth added at a year end isn't taken back. See [More on the saga](help:saga-more).
- **The whole season:** the backup in `sagas/backups` (in Ars Magica Manager in your OneDrive folder) holds the saga as it was just before the last season was applied. Quit the app, copy the backup over the saga's file of the same name in `sagas`, then reopen the saga. The four backups before it are kept too, as `<name>.1.json` (the season before) to `<name>.4.json`: to go further back, copy one of those over the saga's file and rename it to the saga's name. No backup is taken when nothing was planned.

### What the app does for you
<!-- help: guide-seasons-auto -->

**You type:** each plan's activity and details, the grogs' yearly updates, dice rolls made at the table (optional), and your answers when advancing.

**The app works out:** what each plan will give before you save it, who has nothing planned, the dice left blank, every result when the season is applied, the Diary entries and season record, vis harvests, and in Winter the grogs' updates, aging, Warping and each covenant's Wealth. Every plan is worked out from the saga as it stood before the season, so one result can't change another in the same season.

**See also:** [Plan Season](help:plan-season), [Grog's Yearly Update](help:grog-year), [Advance Season](help:advance-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [Invent Spell screen](help:invent-spell), [How to manage the covenant](help:guide-covenant)

# How to manage the covenant
<!-- help: guide-covenant -->

This guide is a tour of running a covenant over the years of a saga: its people, its resources, its money, its books, its Boons and Hooks, and its history. Use it once the covenant is In Play, to find where each part of covenant life is kept and what the app keeps up to date for you.

Choose the covenant in the tree and press Enter to open the [Covenant sheet](help:covenant). The top panel stays in view; the number keys `1` to `8` open its tabs.

### People
<!-- help: guide-covenant-people -->

The [Inhabitants tab](help:tab-cov-inhabitants) (`2`) lists who lives at the covenant.

1. **Magi and companions with a sheet** are listed automatically. To add one, choose the covenant in the tree, press `n` for New and choose **New Character**; the covenant is already chosen. Their row on the [Magi](help:section-inh-magus) or [Companions](help:section-inh-companion) list appears at once.
2. **People without a sheet** are added with `a` on the Magi or Companions list, typing their details yourself.
3. **Grogs** are made with New Character too (type grog). Then, on [Specialists](help:section-inh-specialist), [Craftspeople](help:section-inh-craftsperson) or [Turb](help:section-inh-turb), press `a`: the app offers the covenant's grogs not yet on a list, or "(New person -- not from a character sheet)".
4. **Everyone else** goes on [Other Covenfolk](help:section-inh-inhabitant), each with a Covenant Role and a Quantity; [Horses](help:section-inh-horse) and [Livestock](help:section-inh-livestock) have lists of their own.
5. When someone leaves, `d` on a listed magus or companion marks them departed rather than deleting them. More's **Restore** brings them back.

[Loyalty](help:section-inh-loyalty) is at the top of the tab. Press `e` there to choose the Equipment, Money, Pension and other modifiers; the app works out the rest from the magi's Gifts, Living Conditions, specialists' roles, known bad Reputations and the Diary. The [Inhabitants](help:section-inh-population) section shows whether there are enough Teamsters and Servants.

### Resources
<!-- help: guide-covenant-resources -->

The [Possessions tab](help:tab-cov-possessions) (`4`) holds what the covenant owns. Each list adds with `a`, edits with `e` and deletes with `d`.

1. **Property and items:** [Properties and Land](help:section-pos-property) and [Items](help:section-pos-item) are a record only. [Weapons](help:section-pos-weapon) and [Armor](help:section-pos-armor) can be chosen from the catalogue, and feed the Weapons cost on the Economics tab.
2. **Sanctums:** every laboratory of the covenant is listed under [Sanctums](help:section-pos-sanctum) automatically; set only its Usage here.
3. **Vis sources:** add each on [Vis Sources](help:section-pos-vis_source) with its Art, Season and pawns, and mark it Contested or Dwindling if it is. In its season each year, the harvest is added to the Raw Vis Stores and written in the Diary.
4. **Raw vis:** [Raw Vis Stores](help:section-pos-vis_store) lists the covenant's vis by Art. To hand vis to a laboratory, a magus or another covenant, choose the store, press `m` for More and choose **Move Vis**. In the Move Raw Vis dialog, give the **Pawns** and choose **To**, then press Move. Both Diaries record it.
5. **Enchanted devices:** [Enchanted Devices](help:section-cov-devices) has More's **Instill an Effect** and **Use a Charge**.

### Money
<!-- help: guide-covenant-money -->

The [Economics tab](help:tab-cov-economics) (`5`) shows a year's finances. Most figures are worked out from the rest of the sheet.

1. On [Wealth](help:section-eco-wealth), press `e` to type the pounds in store. Its right-hand column shows Total Income, Total Expenditure and the Surplus/Deficit.
2. On [Sources of Income](help:section-eco-income), `a` adds an enterprise with its Type; leave Current Income blank to use the Type's usual income. To apply a year's Income Modification, choose the source, press `m` and choose **Improve Income**: pick the Annual Improvement Effect, check the Projected Income, and press Commit.
3. On [Yearly Expenditure](help:section-eco-expenditure), type Tithes, Inflation and Sundry with `e`. The other rows are worked out; `e` on them edits only their note.
4. On [Cost Savings](help:section-eco-savings), laborers' and craftspeople's savings come from the Inhabitants tab. Type Magic savings with `e`.

**At the end of each year,** when Winter is advanced, the surplus is added to Wealth and Emergency Savings start again at 0.

**With a deficit,** the app asks before closing the year whether you want to resolve it. To cover it from Wealth, choose **Emergency Savings** on Cost Savings and press `e`: the app offers to draw the deficit, or as much as Wealth holds, from Wealth. A covenant with no Wealth to draw is broke. A deficit is never taken from Wealth unless you choose to.

### Books
<!-- help: guide-covenant-books -->

The [Library tab](help:tab-cov-library) (`6`) lists every book at the covenant, including those owned by its laboratories and characters, with each one's Location.

1. On [Books](help:section-lib-books), press `a` to add a book; it belongs to the covenant. `e` edits the chosen book.
2. To bring in many at once, press `m` and choose **Import** to read books from a CSV file into this covenant's library. A preview shows what will be added first. See [Import Data](help:import-data).
3. To give several books a new owner, mark them with Space and press `e`. A book bound in a codex moves with its whole codex.
4. To bind books together, choose a **Codex** in each one's form (or a new one); the codex can be a palimpsest, an encyclopedia, a florilegium or a folio. A tractatus can be a commentary on a summa, and any book can have a physical form, such as an exemplar.
5. To say how well the library serves research, press `m` and choose **Research Bonuses**: a level for each subject it has books on.

The [Summary](help:section-lib-summary) counts the books by type, the codices, and the subjects the library aids research on. A book's details show its value, a price guide and its subject's research bonuses.

### Boons and Hooks
<!-- help: guide-covenant-boons -->

The [Attributes tab](help:tab-cov-attributes) (`1`) holds the covenant's description, [Reputations](help:section-cov-reputations), [Boons](help:section-cov-boons) and [Hooks](help:section-cov-hooks).

1. Press `a` on Boons or Hooks to choose one from the catalogue, then `e` to give its detail and description.
2. The titles show the points the Boons cost and the Hooks provide; the app warns above the lists about Boons and Hooks that can't be taken together.
3. Some Boons change figures elsewhere, such as the Aura in the top panel or the Buildings cost.

### The covenant's Diary
<!-- help: guide-covenant-diary -->

The [Diary tab](help:tab-cov-diary) (`7`) is the covenant's history.

1. Press `a` to add an entry with a Year, Season, Category and Name, and any pounds, vis or Loyalty points.
2. A Story Event also has a Status (Open or Resolved), a year to revisit it, and can be linked to a Hook to count the stories told against it.
3. Only the Loyalty points change the sheet, through Actions and events on the Loyalty block.

The app adds its own entries for vis harvests, vis moved in or out, and contested resources that went unsecured.

### The Seasons tab
<!-- help: guide-covenant-seasons -->

The [Seasons tab](help:tab-cov-seasons) (`3`) is the covenant's planning board: every magus, companion and grog, with what each has planned this season. Plan anyone's season from here with `e`, and set up a grog's yearly update the same way. See [How to plan and run a season](help:guide-seasons).

### What the app does for you
<!-- help: guide-covenant-auto -->

**You type:** the people without a sheet, the Loyalty choices, each possession, Wealth and the income sources, the typed costs and savings, books, Boons and Hooks, and Diary entries.

**The app works out:** the magi, companions and sanctums listed from their own sheets, Loyalty, the points of inhabitants, laboratories and weapons and armour, every calculated cost and saving, the Surplus/Deficit, the yearly vis harvests and Wealth, and the Library's counts and Locations.

**See also:** [Covenant sheet](help:covenant), [Build tab](help:tab-cov-build), [Advance Season](help:advance-season), [How to plan and run a season](help:guide-seasons)
