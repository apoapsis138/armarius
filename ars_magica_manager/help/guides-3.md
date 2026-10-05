# Getting started
<!-- help: guide-getting-started -->

This guide takes you from the start screen to a saga you can play: a saga with its books and optional rules chosen, a first covenant, its characters and their laboratories. It also shows how to find your way around the workspace and its keys. Read it the first time you use the app, or when you start a new saga.

### Create and open a saga
<!-- help: guide-getting-started-saga -->

1. The app opens on the [saga picker](help:saga-picker), which lists the sagas saved on this computer ("No sagas yet" the first time).
2. Press `n`. The Create a New Saga form asks for a Name and a Storyguide (both required), a Start Year and Start Season, and an optional one-line Description. Choose Create.
3. The new saga appears in the list. Highlight it with the arrow keys and press Enter to open it in the [workspace](help:workspace).

The saga is saved as soon as it is made, and every change after that is saved as you make it: there is no Save command to remember.

### Choose the books and optional rules
<!-- help: guide-getting-started-rules -->

1. The workspace opens with the navigation tree on the left. Its top node is [the saga](help:saga); with it chosen, the pane on the right shows the current date, the books in play and the optional rules.
2. With the saga node chosen, press `e` (the footer calls it Edit Saga).
3. **Books in play** opens a picker of the sourcebooks. Choose the ones your troupe uses: catalog pickers then hide Virtues, spells and other entries from books not in play, and a supplement's own rules apply only while its book is in play.
4. Below it are the optional rules, each off until you tick it: Simple dice only, Dominion Magic Resistance, Harsher Infernal vis and Enforce creation rules strictly. The line under each says what it does.
5. **Keep season records** keeps a record of each season under Seasons in the tree. Leave it on unless you only want the characters' Diaries to keep them.
6. Save. The saga's summary now lists your books and the optional rules turned on.

You can come back to Edit Saga at any time.

### Make the first covenant
<!-- help: guide-getting-started-covenant -->

1. With the saga node chosen, press `n` (New). A menu offers New Covenant, New Character and New Laboratory; press `v` for New Covenant.
2. Type a Name and, if you like, a one-line note under Notes, then choose Create.
3. The covenant appears in the tree, marked "(creating)", with two groups under it: **Characters** and **Laboratories**. Its [covenant sheet](help:covenant) opens on the right.
4. The covenant starts In Creation. To build it by the book (Power Level, Build Points, Boons and Hooks), see [How to create a character, covenant or laboratory](help:guide-creation). To fill it in by hand instead, press Enter to move into the sheet and use `e` on its top panel and `a` in its sections.

### Add characters and laboratories
<!-- help: guide-getting-started-people -->

1. In the tree, choose the covenant (or its Characters group) and press `n`, then `c` for New Character. The new character starts in the covenant on show.
2. The Create a New Character form asks for a Name, a Type (Magus, Companion, Mythic Companion or Grog), a Template and the Covenant. Leave Template at None to build the character step by step, or choose one of the book's ready-to-play characters; the line above Create describes the one you chose. See [Characters group](help:character-group).
3. Choose Create. The character's [sheet](help:character) opens, and their node appears under Characters.
4. For a laboratory, choose the covenant (or its Laboratories group), press `n`, then `l` for New Laboratory. The form asks for a Name, a Size, the Covenant, and whether it is **One of the covenant's starting labs** (ticked for you while the covenant is In Creation). See [Laboratories group](help:laboratory-group).

### Give a magus their laboratory
<!-- help: guide-getting-started-lab -->

A laboratory's owner is the magus whose lab work is planned on it and whose Lab Totals it shows. You can set it from either side; the app keeps the two in step.

1. From the laboratory: choose it in the tree, press Enter, and with its top panel focused press `e`. Choose the magus as **Owner** in the [Identity](help:section-lab-identity) panel and save.
2. Or from the magus: on their sheet, with the top panel focused, press `e` and choose the **Assigned Laboratory** in [Character info](help:section-char-info).

Giving a laboratory to a magus who already had one frees their old laboratory, and a laboratory can have only one owner at a time.

### Find your way around
<!-- help: guide-getting-started-moving -->

1. **The tree.** The arrow keys move along it, and the sheet on the right follows. Enter moves focus into the sheet; Esc steps back out, from the sheet to the tree and from the tree to the saga picker. See [the navigation tree](help:workspace-tree).
2. **Sections.** A sheet is made of sections. Tab and Shift+Tab move from one section to the next; the arrow keys move within a list. `c` collapses or expands the focused section.
3. **Tabs.** The number keys open a sheet's tabs, and each tab shows its number: `1` to `8` on a covenant, `1` to `7` on a magus, `1` to `6` on a laboratory.
4. **The keys that act.** `a` adds to the focused list, `e` edits the highlighted row or the focused section, and `d` deletes the highlighted row after asking first. `m` More holds the rarer actions for where you are, and `n` New makes a covenant, character, laboratory or familiar bond. See [Keys](help:keys) and [What the keys act on](help:workspace-keys).
5. **The footer.** Its left end shows the keys that work where focus is, with labels that say what they will do; its right end shows the keys that always work.
6. **Where you are.** The row above the footer names the tree node, the tab, the section and the chosen row, separated by "›".
7. **The details panel.** A list that holds records has a panel below it that shows the chosen row in full, with the rules text of a Virtue, Flaw or spell. See [Where you are, the details panel and the theme](help:workspace-status).

### Help
<!-- help: guide-getting-started-help -->

Press `?` anywhere for help on the part of the screen that has focus; in a dialog where you are typing, press F1. The Help screen lists THIS SCREEN first, then the HOW-TO GUIDES, the REFERENCE pages and ALL PAGES. The arrow keys choose a topic, `/` filters the topics, Tab moves between the list and the page, and Esc closes Help.

### Where to go next
<!-- help: guide-getting-started-next -->

- [How to create a character, covenant or laboratory](help:guide-creation): building by the book with the Creation Worksheet.
- [How to plan and run a season](help:guide-seasons): planning everyone's season and advancing the saga.
- [How to manage the covenant](help:guide-covenant): its people, possessions and money.
- [How the app handles advancement](help:guide-advancement): study, books and teaching.
- [How lab planning works](help:guide-lab-planning): inventing spells, enchanting and other lab projects.
- [How to bind and keep a familiar](help:guide-familiars).
- [How to import and export](help:guide-import-export): moving records between sagas.

**See also:** [Saga picker](help:saga-picker), [The workspace](help:workspace), [The saga](help:saga), [Keys](help:keys)

# How to create a character, covenant or laboratory
<!-- help: guide-creation -->

This guide builds a covenant, a laboratory or a character by the book, using the Creation Worksheet to walk through each step with its budget and checks. Use it when your troupe makes a new saga's covenant and characters, or when a new character joins play.

### In Creation and In Play
<!-- help: guide-creation-modes -->

Every new covenant, laboratory and character starts **In Creation**, and its tree node is marked "(creating)". While a record is In Creation the app runs its creation checks; once it is **In Play** the checks stop. See [In Creation and In Play](help:creation-worksheet-modes).

The top panel of the record's sheet has a button that shows its mode, beside Edit (e). While it is In Creation, a **Creation Worksheet** button sits beside that.

The one exception is a character made from a template: the book's templates are finished characters, so they start In Play.

### Choose the order
<!-- help: guide-creation-order -->

The three kinds of record depend on each other, so this order saves going back:

1. **The covenant first.** Its Power Level sets the Build Points the storyguide gives it, and those Build Points pay for its starting laboratories.
2. **Then the magi.** A covenant gets one standard laboratory free for each of its magi, so the Build Points come out right once the magi are in it. A laboratory's builder also needs Magic Theory 3, which a magus gains in their Apprenticeship.
3. **Then the laboratories**, each given to its magus, and the companions and grogs whenever you like.
4. **Last, review the covenant** and move everything to In Play.

You can move freely between records and steps; nothing is locked in by the order.

### Start a character, with or without a template
<!-- help: guide-creation-character-new -->

1. Choose the covenant or its Characters group in the tree, press `n`, then `c` for New Character.
2. Give a Name and a Type. For a Magus, Companion or Grog the form offers a **Template**: one of the book's ready-to-play characters, such as a magus of each House or The Knight. The Mythic Companion type has none.
3. Leave Template at None to build the character yourself; the line above Create says the character starts In Creation. Or choose a template and the line describes it.
4. Choose Create. If the template leaves a name to you, such as an Area Lore's area, the app asks for it first; cancelling there cancels the new character.

See [New Character](help:character-group-new).

### Open the worksheet
<!-- help: guide-creation-open -->

1. Choose the record in the tree and press Enter to focus its top panel.
2. Choose the **Creation Worksheet** button, or press `m` More and choose Creation Worksheet.
3. The [Creation Worksheet](help:creation-worksheet) opens over the sheet. The left column lists the steps; the right shows the chosen step's budget, its checks and its buttons.
4. Up and Down choose a step, Tab moves to the step's buttons, and Esc closes the worksheet.

The buttons open the sheet's own dialogs and change the real record, so everything is saved as you go. When a dialog closes, the worksheet works out the budget and checks again.

### Build a covenant
<!-- help: guide-creation-covenant -->

1. **Power Level.** Choose Power Level asks for the Power Level, the storyguide's Build Points (within that level's range) and the Year Founded. The step also lists what every covenant has free, and the highest level of text or enchanted effect the Power Level allows. Edit covenant opens the covenant's own details.
2. **Build Points.** The step shows the Build Points spent against the budget, line by line. They are priced from what the covenant owns: books in its Library, vis sources and stocks on its Possessions tab, enchanted devices, starting laboratories and specialists. Add those on the covenant sheet as usual; Buy a specialist is here.
3. **Boons and Hooks.** Add a Boon, Add a Hook, or Use a Covenant Situation to take one of the books' ready-made sets. The step shows the Boon and Hook points, which should balance.
4. **Review.** Lists every step that still has a check open.

The covenant's [Build tab](help:tab-cov-build) (`8`) shows the same Build Points.

### Set up a laboratory
<!-- help: guide-creation-lab -->

1. **Setting Up.** Edit identity (owner) chooses the magus who builds it; Edit Characteristics sets its Size and Refinement; Add a Virtue adds a laboratory Virtue or Flaw; Starting lab: yes/no says whether the covenant's Build Points pay for it. The step shows the owner, Size, Refinement and, for a starting lab, its Build Points.
2. **Review.** Lists any check still open, such as an owner without Magic Theory 3, or Virtues that don't fit in Size plus Refinement.

See the [Laboratory sheet](help:laboratory).

### Build a character
<!-- help: guide-creation-character -->

The steps follow the book's order. Each one's buttons are named for what they do.

1. **Concept.** Edit type and Edit Year Born. A magus also has Edit House, a button to add The Gift and Hermetic Magus if they are missing, and Add the House Virtue. A Mythic Companion chooses their status Virtue.
2. **Virtues and Flaws.** The Virtue points spent against those allowed, and the Flaw points and Minor Flaws against their limits. Add a Virtue, Add a Flaw, or Remove one.
3. **Characteristics.** Each Characteristic's score and what it cost, and the points spent of the budget. Edit Characteristics; with the Grogs book in play, a grog can also Fill from a Grogs array.
4. **Early Childhood.** Set the Native Language, then Spend xp on the childhood Abilities, or Use a sample childhood.
5. **Later Life.** The years and xp a year, and what is spent; Spend xp, plus a button for any Virtue that gives its own xp, Take a training package where one is offered, and the Ability cap at this age.
6. **Apprenticeship** (magi only). The xp for Arts and Abilities and the spell levels; Spend xp, Learn a spell, Spell details and Forget a spell. Each spell is capped at its Lab Total.
7. **Years past Gauntlet** (magi only). Years and conditions sets the years and working conditions; Spend points on xp and learn spells from the points those years give. An older character can Roll pre-play aging here.
8. **Finishing Touches.** Add a Personality Trait, Add a Reputation and Edit Confidence, followed by a review of every step.

Once xp is spent at a step, Change one and Take back one let you correct it.

### Marks, warnings and advice
<!-- help: guide-creation-marks -->

Each step in the left column is marked ✔ when every check passes, ✘ when a rule the book says must be followed is broken (a warning), ☞ when something the book says should be done isn't (advice), and ○ when the step has no checks. Below the list the app counts the steps that pass and sums up the checks, for example "2 warnings, 1 advice". See [Steps and their marks](help:creation-worksheet-steps).

Checks never stop an edit. They only matter when you move the record to In Play.

### Move to In Play
<!-- help: guide-creation-play -->

1. On the worksheet's last step, choose **Move to In Play**. The confirmation lists every check that doesn't pass; choose Move to In Play to go ahead.
2. Or, from the sheet, choose the mode button on the top panel, or More's **In Creation / In Play**.
3. If the saga has **Enforce creation rules strictly** turned on in Edit Saga, a record with a warning stays In Creation and a message says how many rules it breaks. Advice never stops it.
4. The "(creating)" mark leaves the tree node. A covenant keeps what its Build Points were spent on, shown in the Initial column of its Build tab.

You can move a record back to In Creation the same way; its checks return until it moves to In Play again. See [Moving to In Play](help:creation-worksheet-play).

**See also:** [Creation Worksheet](help:creation-worksheet), [Characters group](help:character-group), [Laboratories group](help:laboratory-group), [Covenant sheet](help:covenant), [Character sheet](help:character), [The saga](help:saga), [Getting started](help:guide-getting-started)
