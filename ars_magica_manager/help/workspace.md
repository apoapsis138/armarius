# Title page
<!-- help: title-page -->

The page the app opens on: the illuminated A and the name Armarius, the tagline, the version and the name of its major version (see What's New), and the ways on.

- **Open Saga** opens the saga you had open last (or the only saga, if there is one). It isn't offered when there is no saga to open.
- **All Sagas** goes to the [saga picker](help:saga-picker), to choose a saga, start a new one or delete one.
- **Help** opens Help.

<!-- tui -->
Enter takes the first of them. Choose with the arrow keys and Enter, and `q` quits. A player's copy of a hosted saga skips the title page and opens on the saga picker, where they sign in.
<!-- /tui -->
<!-- gui -->
Click one; Enter takes the first of them, as the line under the buttons says. The window's own buttons, at its top right, minimise, maximise and close it.
<!-- /gui -->

**You type:** nothing here; you choose where to go.

**The app works out:** which saga you had open last, which it remembers in the settings each time you open one.

**See also:** [Saga picker](help:saga-picker), [Getting started](help:guide-getting-started)

# Saga picker
<!-- help: saga-picker -->

<!-- tui -->
The start screen. It lists every saga saved on this computer, so you can open one, start a new one or delete one you no longer want.

Each row shows the saga's name, its storyguide and its current date.
<!-- /tui -->
<!-- gui -->
The Sagas page, the first place on the trail at the top of the window. It shows every saga saved on this computer as a card, so you can open one, start a new one or delete one you no longer want.

Each card shows the saga's name, its current date and how many covenants and characters it has. Click a card to open the saga.
<!-- /gui -->
<!-- tui -->
A saga file that the app can't read is still listed, marked "can't be read", so that you can delete it.

Under the list, **Save folder** shows the folder the sagas are read from and what chose it: the default, chosen in the app, set by the ARMARIUS_DATA environment variable (or the older ARS_MAGICA_MANAGER_DATA), or a folder the app fell back to because the chosen one couldn't be used.
<!-- /tui -->
<!-- gui -->
The line under the page's title names the folder the sagas are read from.
<!-- /gui -->
The default is Armarius at the top of your OneDrive. The app was called Ars Magica Manager before: the first time Armarius starts, it renames the default Ars Magica Manager folder to Armarius and says so (a folder you chose stays where it is, and when both folders exist nothing is merged and Armarius is used).

**You type:** for a new saga, its Name and Storyguide (both required), the Start Year and Start Season, and an optional one-line Description.

**The app works out:** nothing here; the saga starts on the date you give and is saved at once.

### Opening, creating and deleting
<!-- help: saga-picker-actions -->

<!-- tui -->
- Highlight a saga and press Enter to open it in the workspace.
- `n` opens the Create a New Saga form.
- `d` (or Delete) deletes the highlighted saga after a confirmation. This deletes the saga's file and everything in it (covenants, characters, laboratories, library) for good, so the confirmation says so and No is the safe answer.
- More (`m`) offers **Change save folder**: choose a folder with the folder browser (Enter opens a folder, Up goes to the parent, or type a path), and whether to move the saves there.
<!-- /tui -->
<!-- gui -->
- Click a saga's card to open it on its own page.
- **New Saga** opens the Create a New Saga form.
- **Delete**, on a saga's card, deletes that saga after a confirmation. This deletes the saga's file and everything in it (covenants, characters, laboratories, library) for good, so the confirmation says so and No is the safe answer.
- **Change Save Folder**: choose a folder in the system's folder dialog, then whether to move the saves there.
<!-- /gui -->
  The sagas, their backups, exports and settings are moved; a file already in the new folder is never overwritten. Some folders may not allow saving (on Windows, Controlled folder access protects Documents and the Desktop; a read-only or synced folder can refuse too), so the app checks it can save in the folder before using it. When ARMARIUS_DATA (or ARS_MAGICA_MANAGER_DATA) sets the folder, it can't be changed here.
<!-- tui -->
- `q` quits the app.

In a browser opened on a hosted saga, the list only opens sagas: New and Delete are left to the storyguide's own window, and opening a saga first asks who you are. See [Signing in](help:sign-in).

The app's version is shown under the list.
<!-- /tui -->

The About page in Help has the version, the licences and the credits.

**See also:** [The workspace](help:workspace), [The saga](help:saga), [Getting started](help:guide-getting-started)

# The workspace
<!-- help: workspace; tui -->

The screen a saga opens in. The navigation tree on the left lists everything in the saga; the pane on the right shows the sheet or list for the node you choose.

**You type:** nothing here; you choose where to go.

**The app works out:** the tree's counts (for example "Characters (3)") and the row above the footer that says where you are.

### The navigation tree
<!-- help: workspace-tree -->

The tree's top node is the saga itself. Under it:

- Each covenant, with two groups under it: **Characters** and **Laboratories**. A magus with a bound familiar has the familiar under them ("Familiar: name").
- **Unassigned Characters** and **Unassigned Laboratories**: those with no covenant. These groups only appear when there is something in them.
- **Unassigned Books**: books with no owner, only shown when there are some.
- **Seasons**: the record of each season applied.
- **Saga Content**: the books in play, the catalogs the saga hides, its House Rules, its own spells and (for the storyguide) its players.

A character's node shows its type, for example "Leandro (magus)". A covenant, laboratory or character still being made is marked "(creating)".

### Moving around
<!-- help: workspace-moving -->

- Arrow keys move along the tree. **Enter** shows the chosen node and moves focus into it: into a sheet's first section, or into a list (Seasons, Unassigned Books).
- **Esc** steps out: from a sheet back to the tree, and from the tree back to the saga picker.
- **Tab** and **Shift+Tab** move from one section of a sheet to the next. Each section is one stop: its list if it has one, otherwise its title. Arrow keys move within a section.
- **1** to **9** open a sheet's tabs; the tabs show their numbers.
- **c** collapses or expands the section that has focus. Enter on a section's title does not.
- With the mouse, a click on a section that doesn't have focus focuses it; a click on the focused section's title collapses or expands it.

### What the keys act on
<!-- help: workspace-keys -->

**a**, **e** and **d** act on whatever has focus: the highlighted row of a list, a section, or the record itself. On a record's tree node, or the top panel that names it, **d** deletes the whole covenant, laboratory, character or familiar, and the confirmation lists what happens to what it owns. A focused list always has a row chosen; in a collapsed section, e and d say "Choose a row first." unless there is only one entry.

- **m** (More) holds the actions only a few places have, such as Import, Export, Set Date, Give or the Creation Worksheet. It offers only what applies where focus is. With one thing to do it runs straight away, and the footer names it; with several it opens a menu with a letter for each.
- **n** (New) makes a covenant, character, laboratory or familiar bond, offering only what belongs at the selected tree node. A new character or laboratory starts in the covenant on show.
- **/** filters a list that can be filtered: on the Saga Content Spells tab it moves to the search box, and on a laboratory's Lab Texts it opens the filter.
- **t** advances the saga by one season. See [Advance Season](help:advance-season).
- **q** quits, and **Ctrl+P** opens Textual's command palette.
- **?** opens Help on the part of the screen that has focus (F1 does the same while you are typing in a dialog).

The footer shows the keys that work where focus is at its left, and the ones that always work (New, Advance Season, Help, Back, Quit) at its right.

### Where you are, the details panel and the theme
<!-- help: workspace-status -->

The row above the footer says where focus is: the tree node on show, then the tab, the section and the chosen row, separated by "›".

Lists that hold records (books, spells, House Rules, a sheet's lists) have a details panel below them that shows the chosen row in full.

At the right end of the same row the app names the theme in use. Change it from the command palette (Ctrl+P); the app remembers your choice for next time.

**See also:** [The saga](help:saga), [Characters group](help:character-group), [Laboratories group](help:laboratory-group), [Seasons](help:seasons), [Saga Content](help:saga-content), [Getting started](help:guide-getting-started)

# The window
<!-- help: workspace; gui -->

The desktop version shows one page at a time, the way a book is read: the Sagas, a saga, a covenant, a character, a laboratory, a familiar, Saga Content, the Seasons, a Creation Worksheet or Help. The bar across the top of the window says where you are and holds what works on every page.

**You type:** nothing here; you choose where to go.

**The app works out:** what each page shows, and which actions it offers.

### The trail and the pages
<!-- help: workspace-tree; gui -->

The trail at the top left names the pages above the one on show, for example "Sagas › Matrix › Keep › Leandro". Click one to go back to it.

- **Sagas** shows every saga as a card. Click one to open it.
- A saga's page has four chapters. **The World** shows its covenants as cards, then the characters and laboratories that belong to no covenant. **Seasons** sets the date and opens the seasons played; **Rules and Content** opens Saga Content; **Saga Management** holds Edit Saga, Import and Export Saga.
- A covenant's page lists its people, laboratories and possessions; click a person or a laboratory to open their page. A magus's familiar opens from the magus's page.

A covenant, laboratory or character still being made is In Creation: its page is drawn on drafting vellum, and its header has the In Creation / In Play switch and the Creation Worksheet.

### Moving around
<!-- help: workspace-moving; gui -->

- A record's page is a book of chapters: the rail on the left lists them, and a click shows one. The chapter scrolls if it is longer than the window.
- Cards and rows are chosen with a click; a card that opens a page (a covenant, a person, a laboratory, a familiar) opens it on a click.
- The trail goes back up. Leaving a page cancels a form left open on it.
- The window can be moved by dragging the app's name in the middle of the top bar (a double-click maximises it), and resized from its edges and corners.

### What the buttons act on
<!-- help: workspace-keys; gui -->

- A section's **Add**, **Edit** and **Delete** buttons act on that section. Edit and Delete act on the row or card last clicked in it (or the only one there is), and stay greyed out until there is one. Delete asks first.
- A form opens in place, under the section's title; a question (such as Delete's) opens above the section. The form's Save keeps what you typed, and Cancel leaves things as they were. Every change is saved to the saga file at once.
- Buttons in a page's header or chapter heading, such as **Edit Covenant**, act on the record itself.
- What the terminal keeps in its New and More menus is on the page itself: a New card at the end of the cards it adds to (**New Covenant**, **New Character**, **New Laboratory**), or a button in the chapter or section it acts on, such as **Give** beside a list's Add, Edit and Delete, **Set Up Research Library** on a covenant's Library or **Set Date** in the saga's Seasons chapter.
- A record's **Manage** chapter holds what acts on the record as a whole: Export, Update from a File, Print to PDF and Delete.
- **Advance Season**, in the top bar, shows the saga's date and advances it by one season. See [Advance Season](help:advance-season).
- **Help**, or `?` or `F1`, opens Help on the page and chapter on show. `Esc` goes back a page (or cancels a form that is open), and `q` quits. See [Keys](help:keys).

### The Inspector and the theme
<!-- help: workspace-status; gui -->

The Inspector, on the right of a record's page, shows whatever you last clicked on the page in full: a row, a card, a book, a spell.

The button beside Help switches between the two themes, Scriptorum (aged parchment and iron gall ink) and Scriptorum Dark (vellum by candlelight); it names the one it switches to. The desktop opens in Scriptorum each time.

The speaker beside the theme turns the sounds on or off, and the app remembers which. Sounds are kept for moments that mean something: a page turning when you open a chapter (a longer one for a record or page), a quill when a form is saved, coins in a Treasury, a chest for the Inventory, a wax seal when the season advances, and a dull knock when an entry is refused. Plain button presses stay silent. The sounds play on Windows only.

**See also:** [The saga](help:saga), [Saga Content](help:saga-content), [Seasons](help:seasons), [Getting started](help:guide-getting-started)

# The saga
<!-- help: saga -->

<!-- tui -->
The top node of the tree. It shows the saga's own details and what it holds.
<!-- /tui -->
<!-- gui -->
The saga's page, opened from its card on the Sagas page. It has four chapters. **The World** shows its
Covenants, Unassigned Characters and Unassigned Laboratories as cards, each
heading ending in a blank card (New Covenant, New Character, New
Laboratory) that makes one more. **Seasons** sets the date (Set Date) and
opens the seasons played; **Rules and Content** opens Saga Content; and
**Saga Management** holds Edit Saga, Import and Export Saga. A familiar is bound on its
magus or in their laboratory.
<!-- /gui -->

<!-- tui -->
**You type:** with `e` (Edit Saga): the Name, Storyguide and Description; whether to Keep season records; the optional rules of the books in play, each off until you turn it on; and the **Ruling templates** a Tribunal's rulings are written from (see [Hold Tribunal](help:hold-tribunal)): `Enter` opens the list, where each can be added, changed or removed. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /tui -->
<!-- gui -->
**You type:** with **Edit Saga**, in Saga Management: the Name, Storyguide and Description; whether to Keep season records; the optional rules of the books in play, each off until you turn it on; and the **Ruling templates** a Tribunal's rulings are written from (see [Hold Tribunal](help:hold-tribunal)): its button opens the list, where each can be added, changed or removed. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /gui -->

**The app works out:** the counts of covenants, characters, laboratories, books and spells, and a summary of the books in play and the optional rules turned on ("none (the book's standard rules)" when none is).

### What the saga shows
<!-- help: saga-summary -->

<!-- tui -->
- **Current date**: the season and year the saga is in. It is also shown in the header on every screen of the workspace.
<!-- /tui -->
<!-- gui -->
- **Current date**: the season and year the saga is in, under its name. It is also shown on Advance Season, in the top bar of every page.
<!-- /gui -->
- **Books in play**: the sourcebooks the troupe uses, and how many of the saga's own sources are in play. They are chosen on [Saga Content](help:section-books-in-play), which says what a book out of play switches off.
- **Optional rules**: Simple dice only, Dominion Magic Resistance, Harsher Infernal vis, Starting income by number of magi, Enforce creation rules strictly, Extended book Quality, Dominion growth and Auras change. Each one's effect is described beside it in Edit Saga; Harsher Infernal vis (Realms of Power: The Infernal), Extended book Quality (Covenants), Dominion growth (Realms of Power: The Divine) and Auras change (Realms of Power: Magic) are offered only while their book is in play. These come from Ars Magica Definitive Edition, Chapter 16: Sagas, Rules Questions, except Extended book Quality, from Covenants' Library chapter.
<!-- tui -->
- **Keep season records**: when on, each season applied is kept under Seasons in the tree. When off, only the characters' Diaries keep them.
<!-- /tui -->
<!-- gui -->
- **Keep season records**: when on, each season applied is kept on the Seasons page. When off, only the characters' Diaries keep them.

On the desktop, the books in play are counted on the Saga Content card in Rules and Content, and the optional rules turned on are shown in Edit Saga.
<!-- /gui -->

### More on the saga
<!-- help: saga-more -->

- **Set Date** moves the saga to any season and year without applying anything. Use it to put the date back after advancing by mistake; it does not undo what the season did (a backup is kept for that, see [Advance Season](help:advance-season)).
- **Import** opens the Import Data dialog: characters, covenants or laboratories exported from another saga, books from a CSV file, or spells from a CSV file. See [Import Data](help:import-data).

<!-- tui -->
New (`n`) on the saga offers New Covenant, New Character, New Laboratory and, while a magus has no familiar, Bind Familiar.
<!-- /tui -->
<!-- gui -->
Set Date is in the Seasons chapter, and Import and Export Saga in Saga Management. The New cards on The World make a covenant, character or laboratory.
<!-- /gui -->

**See also:** [The workspace](help:workspace), [Advance Season](help:advance-season), [Import Data](help:import-data), [Creation Worksheet](help:creation-worksheet), [Getting started](help:guide-getting-started)

# Characters group
<!-- help: character-group -->

<!-- tui -->
The Characters node under a covenant, or Unassigned Characters under the saga. It lists the characters in the tree below it; select one there to open their sheet.

**You type:** nothing here. `n` (New) offers New Character, with this covenant already chosen, and Bind Familiar while a magus has no familiar.
<!-- /tui -->
<!-- gui -->
A covenant's People chapter, or Unassigned Characters on the saga's The World, shows the characters as cards; click one to open their sheet.

**You type:** nothing here. The **New Character** card at the end of the cards makes one, with this covenant already chosen. A familiar is bound on its magus's page (or in their laboratory).
<!-- /gui -->

**The app works out:** the count in the node's label.

### New Character
<!-- help: character-group-new -->

The Create a New Character form asks for a Name, a Type (magus, companion, Mythic Companion or grog) and a covenant. For a type the book has templates for, it also offers a **Template**:

- **None**: the character starts In Creation, to be built step by step with the [Creation Worksheet](help:creation-worksheet).
- **A template**: one of the book's ready-to-play characters (Ars Magica Definitive Edition, Chapter 3: Characters, Character Templates). It fills the new sheet and the character starts In Play. If the template leaves a name to the player, such as an Area Lore's area, the app asks for it before the character is made; cancelling that cancels the new character.
- **A Grogs template** (a grog, while Grogs is in play; marked "(Grogs)"): one of the nineteen kinds of grog in Grogs, Chapter 7, such as The Advisor or The Street Thug. These are guidance rather than finished characters, so the app asks for the template's choices next (see [A Grogs template](help:grog-templates)) and the grog starts In Creation.

The line above Create describes the template you chose.

### A Grogs template
<!-- help: grog-templates -->

After Create, a Grogs template asks for its choices before anything is made (Grogs, Chapter 7: Grog Templates; the limits are the Definitive Edition's, Chapter 3).

**You choose:**

- **Faith**, **Stage** or **Character**, where the book gives several versions: the Confessor's faith, the Craftsman's apprentice or journeyman, and the Animal Trainer's three sample characters.
- **Age**: one of the book's ages for the template. It sets the year born and which of the book's Ability lists the grog gets.
- **Social Status**, from the ones the book suggests.
- **The book's Virtues and Flaws**, ticked: untick one to leave it out.
- **The book also suggests**: tick any of its other suggestions; where the book says "this or that", pick one.
- **Another Virtue** and **Another Flaw**: any other Minor Virtue or Flaw a grog may take, from the books in play. Where the book gives a Flaw a grog can't take, the hint under the first Another Flaw says what to choose instead.
- **The book's Characteristics** (The Advisor only, the one template that gives figures), and a **Personality Trait** where the book gives a choice.

**The app works out:** the line under the form gives the template, the xp a grog has at that age against what the book's list comes to, and the Virtue and Flaw points so far. Next refuses a choice that breaks a grog's limits: no Major Virtues or Flaws, nothing Hermetic and not The Gift, at most three Minor Flaws, no more Virtue points than Flaw points, and exactly one Social Status. Taking fewer Virtues than Flaws is allowed here; the worksheet then shows the points left to balance.

Then the app asks for any names the Ability list leaves to you, such as an Area Lore's area, the Native Language or a Craft (the covenant's own name is filled in for you), and makes the grog. Cancelling either form cancels the new character.

**What the grog starts with:** the age, the Social Status, Virtues and Flaws, the book's Personality Traits (with Loyal +1, and Brave +1 for one with a Martial Ability, if the book's lack them) and any Reputation, and the book's Ability list for that age, with its specialties. The Abilities go on the [Creation Worksheet](help:creation-worksheet) as xp, step by step: 75 xp of Native Language, the free score of a Supernatural Ability its Virtue grants, a Virtue's own xp (Educated, Warrior, Arcane Lore) on what it may buy, the 45 xp of Early Childhood on what a child may learn, and the rest in Later Life. The grog starts **In Creation**, so the worksheet checks the result: where the book's list spends more than the age gives, needs a Virtue the grog doesn't have (a Martial Ability without Warrior), or leaves xp unspent, its checks say so. The Biography notes the template, the book's details, its suggested training packages, and where the app's version differs from the book (a Flaw the Definitive Edition makes Major, an older edition's Ability) and why.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [How to start a character](help:guide-creation-character-new)

**See also:** [Laboratories group](help:laboratory-group), [Creation Worksheet](help:creation-worksheet), [The workspace](help:workspace), [How to create a character, covenant or laboratory](help:guide-creation)

# Laboratories group
<!-- help: laboratory-group -->

<!-- tui -->
The Laboratories node under a covenant, or Unassigned Laboratories under the saga. It lists the laboratories in the tree below it; select one there to open its sheet.

**You type:** nothing here. `n` (New) offers New Laboratory, with this covenant already chosen.
<!-- /tui -->
<!-- gui -->
A covenant's Laboratories chapter, or Unassigned Laboratories on the saga's The World, shows the laboratories as cards; click one to open its page.

**You type:** nothing here. The **New Laboratory** card at the end of the cards makes one, with this covenant already chosen.
<!-- /gui -->
The form asks for a Name, a Size and the covenant, and whether it is one of the covenant's starting labs (paid for from the covenant's Build Points, one free per magus).

**The app works out:** the count in the node's label. A new laboratory starts In Creation.

**See also:** [Characters group](help:character-group), [Creation Worksheet](help:creation-worksheet), [How to create a character, covenant or laboratory](help:guide-creation)

# Unassigned Books
<!-- help: unassigned-books; tui -->

The books in the saga that nobody owns: not a covenant's library, a laboratory or a character. The node only appears in the tree while there are some.

**You type:** a book's details with `a` and `e`, the same form as a library's. Give a book an owner and it moves off this list.

**The app works out:** the count, and the details panel for the chosen book.

### Acting on several books
<!-- help: unassigned-books-marked -->

Mark books with Space (or Ctrl+click) to act on them together. With books marked, `e` gives them all one new owner and `d` deletes them all, each after a confirmation. With none marked, e and d act on the highlighted book. A book bound in a codex takes its whole codex to the new owner.

Books imported from a CSV file on the saga (More, Import, Books) land here.

**See also:** [Import Data](help:import-data), [The workspace](help:workspace), [How to import and export](help:guide-import-export)

# Unassigned Books
<!-- help: unassigned-books; gui -->

The books in the saga that nobody owns: not a covenant's library, a laboratory or a character. Books imported from a CSV file on the saga (Import, in Saga Management) land here.

The desktop doesn't list them yet: open the saga in the terminal version to see them, give them an owner or delete them. Once a book has an owner it shows in that covenant's Library, laboratory or character's books.

**See also:** [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Seasons
<!-- help: seasons -->

The saga's record of past seasons: what everyone did each season and what it gave them. A record is added each time a season is applied with [Advance Season](help:advance-season), as long as Keep season records is on in Edit Saga.

**You type:** nothing; the records are written by the app.

<!-- tui -->
**The app works out:** what is coming ([Looking Ahead](help:section-ahead)), then one row per season recorded, newest first ("Spring 1220 (3 people)"), and below the list the chosen season's record, grouped by covenant.
<!-- /tui -->
<!-- gui -->
**The app works out:** the Seasons page, opened from the saga's Seasons chapter (The Seasons Played), starts with what is coming ([Ahead](help:section-ahead)), then lists the seasons in its rail, newest first, and shows the chosen season's record, grouped by covenant, a row a person. Just after Advance Season, the season just played out is first.
<!-- /gui -->
Each person's line gives the activity, what it was on and its result. A plan that could not be carried out says why, and a magus or companion with nothing planned is shown as "nothing planned". Winter's lines also include aging rolls, grogs' yearly updates, business upkeep and vis harvests.

When season records are off, the page says so and no new seasons are added; each character's Diary still has their own entry.

**See also:** [Advance Season](help:advance-season), [Season Summary](help:season-summary), [How to plan and run a season](help:guide-seasons)

## The Seasons panel
<!-- help: section-seasons-info -->

The date, how far Ahead looks, the next Tribunal's meeting and how many
things come this season.

**You type:** how far to look ahead (a number of years, or to the next
Tribunal) and what to show, with
<!-- tui -->
Edit (`e`).
<!-- /tui -->
<!-- gui -->
**Looking ahead** on the Ahead section.
<!-- /gui -->
Both are kept with the saga; looking ahead starts at 2 years.

## Seasons tab
<!-- help: tab-seasons -->

What is coming, season by season, over the seasons already recorded.

## Looking Ahead
<!-- help: section-ahead -->

What is coming in the seasons ahead, from this one to the end of the
span, a season at a time. Nothing here is kept as a list: each part of
the saga is asked what it has coming.

- **Tribunal**: each Tribunal's next meeting, and the season notice of
  its open cases is due.
- **Neighbours** and **Income**: each town's fairs and markets (a fair a
  covenant trades at is its income roll).
- **Places**: each place's dated triggers.
- **Threats**: a threat's dated stages still to come.
- **Characters**: the year a character's aging rolls begin, and the
  season one comes back from Twilight.
- **Every Winter**: the world turns (the yearly step).
- **Calendar**: your own entries, once, each year or every so many
  years, for the whole saga or one covenant.

**You type:** your own calendar entries: Add one, and Edit or Delete
it. A row worked out from another record is changed on that record:
Edit and Delete say where.
<!-- tui -->
Show (Edit on the Seasons panel) narrows the list to one kind of entry.
<!-- /tui -->
<!-- gui -->
The chips under the title narrow the cards to one kind of entry; click a
card to read it in the inspector.
<!-- /gui -->

## The World Turned
<!-- help: section-world-turns -->

Each Winter's yearly step: what was applied when the world turned
([The World Turns](help:world-turns)), newest first. Delete one to undo
its changes (a value changed by hand since is left as it is).

## Seasons Recorded
<!-- help: section-seasons-recorded -->

The seasons applied so far, newest first; the chosen season's record is
shown
<!-- tui -->
in the details panel.
<!-- /tui -->
<!-- gui -->
in its chapter.
<!-- /gui -->
See [Seasons](help:seasons).

# Saga Content
<!-- help: saga-content -->

One place for what this saga's pickers offer: the books in play and the saga's own sources, the shared catalogs and single entries it hides, its House Rules, its own spells and, for the storyguide, its players.
<!-- tui -->
Choose **Saga Content** in the tree, under Seasons. The tabs open with `1` to `5`.
<!-- /tui -->
<!-- gui -->
Open it from the saga page's **Rules and Content** chapter. Its chapters (Books, Catalogs, House Rules, Spells, Players) are the tabs described below; click a row or card to see it in full in the Inspector.
<!-- /gui -->

**You type:** what each tab below describes. The catalog files the app ships with are never changed: hiding something here affects only this saga.

<!-- tui -->
**The app works out:** what every picker in the saga offers. An entry from a book out of play, or one hidden here, is left out of the pickers (`F3` in a picker shows it, marked); an entry already on a character, laboratory or covenant stays there.
<!-- /tui -->
<!-- gui -->
**The app works out:** what every picker in the saga offers. An entry from a book out of play, or one hidden here, is left out of the pickers (**Show everything** in a picker lists it, marked); an entry already on a character, laboratory or covenant stays there.
<!-- /gui -->

**See also:** [The saga](help:saga), [The workspace](help:workspace), [Getting started](help:guide-getting-started)

## Books tab
<!-- help: tab-content-books -->

The sourcebooks the saga uses, and the saga's own sources.

**You type:** which books are in play, and the saga's own sources.

**The app works out:** what each book in or out of play switches on or off, and how many House Rules cite each source.

### Books in Play
<!-- help: section-books-in-play -->

<!-- tui -->
Every sourcebook, with whether it is in play. `e` opens the picker of books: tick the ones your troupe uses. The core book is always in play.
<!-- /tui -->
<!-- gui -->
Every sourcebook as a card, with whether it is in play. **Edit** opens the picker of books: tick the ones your troupe uses. The core book is always in play.
<!-- /gui -->

While a book is out of play, everything it adds is switched off: the pickers leave out its Virtues, Flaws, spells and other entries; the season plan leaves out its activities (a plan already made keeps its activity); its optional rules are left off Edit Saga and count as off (the choice is kept for when the book comes back); and the library's book form leaves out its kinds of books and their fields (a book already using one keeps it). The Library tab's research bonuses need Covenants.

### Saga Sources
<!-- help: section-saga-sources -->

<!-- tui -->
Sources of the saga's own, such as a house-rules list or a fan supplement, that its House Rules can cite. `a` adds one: an Abbreviation (short, like a book's, and not one a sourcebook already uses) and a Title. A new source starts in play, and it is put in or out of play with the books above.
<!-- /tui -->
<!-- gui -->
Sources of the saga's own, such as a house-rules list or a fan supplement, that its House Rules can cite. **Add** adds one: an Abbreviation (short, like a book's, and not one a sourcebook already uses) and a Title. A new source starts in play, and it is put in or out of play with the books above.
<!-- /gui -->

<!-- tui -->
`e` edits a source; a new abbreviation is carried to the House Rules that cite it. `d` won't delete a source a House Rule still cites: the message names them.
<!-- /tui -->
<!-- gui -->
**Edit** edits the source last clicked; a new abbreviation is carried to the House Rules that cite it. **Delete** won't delete a source a House Rule still cites: the message names them.
<!-- /gui -->

### Traditions Offered
<!-- help: section-traditions -->

The non-Hermetic magical traditions whose book is in play (Hedge Magic Revised Edition's six, and those of the Realms of Power, Societates, the Tribunal and regional books, Rival Magic and Ancient Magic), and whether the saga offers each. Every tradition starts off, so the lists stay short: turn on only the ones your saga uses. A character can join a tradition the saga offers, which gives them [a chapter](help:tradition-chapter) for its Arts and Abilities.

<!-- tui -->
`e` opens a tick for each tradition: tick the ones the saga offers.
<!-- /tui -->
<!-- gui -->
**Edit** opens a tick for each tradition: tick the ones the saga offers.
<!-- /gui -->

Turning a tradition off, or taking its book out of play, stops it being offered; characters who already belong to it keep their chapter, and the choice is kept for when the book comes back.

## Catalogs tab
<!-- help: tab-content-catalogs -->

The shared catalogs the pickers draw on, and what this saga leaves out of them.

**You type:** whether each catalog is offered, and the single entries to hide.

**The app works out:** each catalog's number of entries and of hidden ones.

### Catalogs
<!-- help: section-catalogs -->

<!-- tui -->
The Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, Spells, and Shapes & Materials catalogs. `e` offers a whole catalog or not. A catalog not offered leaves its pickers with only the saga's own entries (its House Rules or own spells).
<!-- /tui -->
<!-- gui -->
The Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, Spells, and Shapes & Materials catalogs. **Edit** offers a whole catalog or not. A catalog not offered leaves its pickers with only the saga's own entries (its House Rules or own spells).
<!-- /gui -->

### Hidden Entries
<!-- help: section-hidden-entries -->

<!-- tui -->
Single entries this saga's pickers leave out, as if their book were out of play. `a` asks which catalog, then which entry to hide; `d` offers the chosen one again, after a confirmation.
<!-- /tui -->
<!-- gui -->
Single entries this saga's pickers leave out, as if their book were out of play. **Add** asks which catalog, then which entry to hide; **Delete** offers the entry last clicked again, after a confirmation.
<!-- /gui -->

## House Rules tab
<!-- help: tab-content-house-rules -->

The Virtues, Flaws, Boons and Hooks made for this saga: house rules, or entries from books the app's catalogs don't carry. They show in the pickers alongside the catalog's entries.

<!-- tui -->
**You type:** with `a` and `e`: what the entry is For (a Character Virtue or Flaw, a Laboratory Virtue or Flaw, or a Covenant Boon or Hook; this is fixed once the entry is made), its Name, Type, Tier, Category, whether it can be taken more than once, what it Asks for, a Description and, once the saga has sources of its own, the Source it comes from.
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**: what the entry is For (a Character Virtue or Flaw, a Laboratory Virtue or Flaw, or a Covenant Boon or Hook; this is fixed once the entry is made), its Name, Type, Tier, Category, whether it can be taken more than once, what it Asks for, a Description and, once the saga has sources of its own, the Source it comes from.
<!-- /gui -->

**Asks for** (a character's or covenant's entry only) lists what is chosen when the entry is taken, comma-separated, as the books' Puissant asks for an Ability: "Form" for a Vis Source Boon, say. Characteristic, Ability, Art, Technique, Form, Realm and Blood are chosen from a list; anything else is typed. Put a choice in the name in braces, "Vis Source ({form})", to have it shown there ("Vis Source (Aquam)"); otherwise it follows the name in brackets. What was chosen can be changed later with Edit on the Virtue, Flaw, Boon or Hook.

**The app works out:** the points from the type and tier (Free 0, Minor 1, Major 3; Flaws and Hooks give points rather than cost them), and, in its details, who holds the entry. An entry citing one of the saga's sources is offered only while that source is in play; one citing none always is.

### House Rules
<!-- help: section-house-rules -->

<!-- tui -->
The list of the saga's own entries, with the details panel below it.
<!-- /tui -->
<!-- gui -->
The list of the saga's own entries; the Inspector shows the one last clicked in full.
<!-- /gui -->

### What house rules don't do
<!-- help: house-rules-limits -->

House rules are text only: the rules engine applies no effects for them. Two entries of the same kind can't share a name, type and tier. Delete won't delete an entry that a character, laboratory or covenant still holds; the message names them, so remove it there first.

When a character, laboratory or covenant is exported, the house rules it uses go with it.

**See also:** [Import Data](help:import-data), [How to import and export](help:guide-import-export)

## Spells tab
<!-- help: tab-content-spells -->

Every spell the saga knows: the catalog's spells from the books in play, and the saga's own. Spells from books out of play, or hidden on the Catalogs tab, are left out until the Source filter asks for them; they are marked "(not in play)", and a magus who already knows one keeps it, marked the same way on their Known Spells.
<!-- tui -->
The list stretches down to a details panel that shows the chosen spell in full.
<!-- /tui -->
<!-- gui -->
The Inspector shows the spell last clicked in full.
<!-- /gui -->

<!-- tui -->
**You type:** the saga's own spells, with `a` (add) and `e` (edit). Catalog spells are read-only: to make your own version of one, add a spell with `a`. `d` deletes only the saga's own spells.
<!-- /tui -->
<!-- gui -->
**You type:** the saga's own spells, with **Add** and **Edit**. Catalog spells are read-only: to make your own version of one, add a spell with Add. **Delete** deletes only the saga's own spells.
<!-- /gui -->

**The app works out:** each spell's Arts, level, Range, Duration and Target, and, in its details, its magnitude, vis cost and casting time. The section title shows how many spells are listed out of how many there are.

### Spells
<!-- help: section-spells -->

<!-- tui -->
The list of spells, with the filter bar above it and the details panel below.
<!-- /tui -->
<!-- gui -->
The list of spells, with the filter bar above it. Click a column's heading to sort by it.
<!-- /gui -->

### Filtering
<!-- help: spells-filter -->

<!-- tui -->
`/` moves to the search box. The filters apply as you change them:
<!-- /tui -->
<!-- gui -->
The filters apply as you change them:
<!-- /gui -->

- **Search** looks in spell names and descriptions; every word must match.
- **Source**: one sourcebook (its spells, in play or not), "The saga's own", or "Not in play" for the catalog spells the saga leaves out.
- **Technique** and **Form**: each also matches a spell that has it as a requisite.
- **Ritual**: Rituals or Formulaic.
- **Level** from and to. General spells pass any level range.

### Importing spells
<!-- help: spells-import -->

Spells can be added in bulk from a CSV file:
<!-- tui -->
on the saga node, More, Import, then Spells.
<!-- /tui -->
<!-- gui -->
on the saga page, Saga Management, Import, then Spells.
<!-- /gui -->
They become the saga's own spells. See [Import Spells](help:import-spells).

**See also:** [Import Spells](help:import-spells), [How to import and export](help:guide-import-export)

## Players tab
<!-- help: tab-content-players -->

Who can sign in to this saga when you host it, so that players open it in a web browser from their own computers. Each player signs in with their name and the passcode you give them. Your own window, the app run on your computer, never asks.
<!-- gui -->

The saga is hosted from the terminal version (see [How to host a saga](help:guide-hosting)); the players you add here are the ones it lets in.
<!-- /gui -->

Only the storyguide sees this tab: your own window, or someone signed in with the Storyguide role.

<!-- tui -->
**You type:** with `a` and `e`: the player's Name (what they type to sign in; no two players may share one), their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. When editing, leave New passcode blank to keep the one they have. `d` deletes a player after a confirmation; they can no longer sign in.
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**: the player's Name (what they type to sign in; no two players may share one), their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. When editing, leave New passcode blank to keep the one they have. **Delete** deletes a player after a confirmation; they can no longer sign in.
<!-- /gui -->

**The app works out:** in their details, the characters each plays and what they may change. Passcodes are stored only scrambled (a salted hash), so the app can check one but no one can read it back from the saga file: if a player forgets theirs, give them a new one.

### Players
<!-- help: section-players -->

<!-- tui -->
The list of players, with the details panel below it.
<!-- /tui -->
<!-- gui -->
The list of players; the Inspector shows the one last clicked.
<!-- /gui -->

### What a signed-in player can do
<!-- help: players-access -->

Choose who plays a character with **Played by** in the character's Biographical Detail (only the storyguide can). A signed-in player can then:

- change the characters they play, with those characters' familiars, laboratories and books, and their season plans;
- change the covenants too, if you ticked May change covenants for them;
- look at everything else but each record's [Secrets](help:tab-secrets), which they never see, and Export a character, laboratory or covenant (the file downloads in their browser, without its secrets).

Only the storyguide (your own window, or someone signed in as Storyguide) can make new records (New), advance or set the season, import, give things between records, share spells, or change the saga itself, its content and its players. Keys a player can't use there don't appear, and if a change slips through anyway, the app doesn't save it and says so.

**See also:** [Signing in](help:sign-in), [How to host a saga](help:guide-hosting), [The saga](help:saga)

# A record's Secrets
<!-- help: tab-secrets -->

What only the storyguide should know about a record: the covenant's
hidden debt, the magus's true master, where a missing founder really
went. Every covenant, character, Tribunal, neighbour and creature has
one, kept apart from its summary and notes so those can be read aloud
or shown to the players as they are.
<!-- tui -->
It is the record's last tab, **Secrets**.
<!-- /tui -->
<!-- gui -->
It is the record's last chapter before Manage, **Secrets**.
<!-- /gui -->

A player signed in to a hosted copy never sees it: the tab isn't there
for them, and a record they export downloads without its secrets. Your
own window, and anyone signed in as Storyguide, always sees it.

Older sagas and content packs kept secrets at the end of a summary or
notes under a **Secrets** heading. Opening the saga moves them here.

**See also:** [What a signed-in player can do](help:players-access), [How to host a saga](help:guide-hosting)

### Secrets
<!-- help: section-secrets -->

<!-- tui -->
**You type:** with `e`, the record's Secrets, as many paragraphs as you
like. It supports **bold** and *italic*.
<!-- /tui -->
<!-- gui -->
**You type:** with **Edit Secrets**, the record's Secrets, as many
paragraphs as you like. It supports **bold** and *italic*.
<!-- /gui -->

# Signing in
<!-- help: sign-in -->

When the storyguide hosts the app, opening a saga in a browser (or over SSH) first asks who you are: type your Name and the Passcode the storyguide gave you, then Sign in. Name is not case-sensitive; the passcode is.

If the saga has no players yet, it can't be opened from a browser: the storyguide adds players on the [Players tab](help:tab-content-players) of Saga Content. Your name is shown in the header beside the saga's date while you're signed in. Going back to the saga list (Escape) signs you out.

While several people have the saga open, each one's saves keep everyone else's changes, and within a few seconds the others' screens show them: the sheet on show updates where it is (with a note such as "Ana changed Corvinus; reloaded"), and if two people open the same character, both are told ("Ana is also on Corvinus"). If the record you have open is deleted elsewhere, the saga is shown instead.

**See also:** [Players](help:tab-content-players), [How to host a saga](help:guide-hosting), [Saga picker](help:saga-picker)
