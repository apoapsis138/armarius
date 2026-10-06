# Saga picker
<!-- help: saga-picker -->

The start screen. It lists every saga saved on this computer, so you can open one, start a new one or delete one you no longer want.

Each row shows the saga's name, its storyguide and its current date. A saga file that the app can't read is still listed, marked "can't be read", so that you can delete it.

**You type:** for a new saga, its Name and Storyguide (both required), the Start Year and Start Season, and an optional one-line Description.

**The app works out:** nothing here; the saga starts on the date you give and is saved at once.

### Opening, creating and deleting
<!-- help: saga-picker-actions -->

- Highlight a saga and press Enter to open it in the workspace.
- `n` opens the Create a New Saga form.
- `d` (or Delete) deletes the highlighted saga after a confirmation. This deletes the saga's file and everything in it (covenants, characters, laboratories, library) for good, so the confirmation says so and No is the safe answer.
- `q` quits the app.

In a browser opened on a hosted saga, the list only opens sagas: New and Delete are left to the storyguide's own window, and opening a saga first asks who you are. See [Signing in](help:sign-in).

The app's version is shown under the list. The About page in Help has the version, the licences and the credits.

**See also:** [The workspace](help:workspace), [The saga](help:saga), [Getting started](help:guide-getting-started)

# The workspace
<!-- help: workspace -->

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
- **Spells**: the catalog's spells and the saga's own.
- **House Rules**: the Virtues, Flaws, Boons and Hooks made for this saga.

A character's node shows its type, for example "Leandro (magus)". A covenant, laboratory or character still being made is marked "(creating)".

### Moving around
<!-- help: workspace-moving -->

- Arrow keys move along the tree. **Enter** shows the chosen node and moves focus into it: into a sheet's first section, or into a list (Spells, Seasons, House Rules, Unassigned Books).
- **Esc** steps out: from a sheet back to the tree, and from the tree back to the saga picker.
- **Tab** and **Shift+Tab** move from one section of a sheet to the next. Each section is one stop: its list if it has one, otherwise its title. Arrow keys move within a section.
- **1** to **9** open a sheet's tabs; the tabs show their numbers.
- **c** collapses or expands the section that has focus. Enter on a section's title does not.
- With the mouse, a click on a section that doesn't have focus focuses it; a click on the focused section's title collapses or expands it.

### What the keys act on
<!-- help: workspace-keys -->

**a**, **e** and **d** act on whatever has focus: the highlighted row of a list, a section, or the record itself. On a record's tree node, or the top panel that names it, **d** deletes the whole covenant, laboratory or character, and the confirmation lists what happens to what it owns. A focused list always has a row chosen; in a collapsed section, e and d say "Choose a row first." unless there is only one entry.

- **m** (More) holds the actions only a few places have, such as Import, Export, Set Date, Move Vis or the Creation Worksheet. It offers only what applies where focus is. With one thing to do it runs straight away, and the footer names it; with several it opens a menu with a letter for each.
- **n** (New) makes a covenant, character, laboratory or familiar bond, offering only what belongs at the selected tree node. A new character or laboratory starts in the covenant on show.
- **/** filters a list that can be filtered: on Spells it moves to the search box, and on a laboratory's Lab Texts it opens the filter.
- **t** advances the saga by one season. See [Advance Season](help:advance-season).
- **q** quits, and **Ctrl+P** opens Textual's command palette.
- **?** opens Help on the part of the screen that has focus (F1 does the same while you are typing in a dialog).

The footer shows the keys that work where focus is at its left, and the ones that always work (New, Advance Season, Help, Back, Quit) at its right.

### Where you are, the details panel and the theme
<!-- help: workspace-status -->

The row above the footer says where focus is: the tree node on show, then the tab, the section and the chosen row, separated by "›".

Lists that hold records (books, spells, House Rules, a sheet's lists) have a details panel below them that shows the chosen row in full.

At the right end of the same row the app names the theme in use. Change it from the command palette (Ctrl+P); the app remembers your choice for next time.

**See also:** [The saga](help:saga), [Characters group](help:character-group), [Laboratories group](help:laboratory-group), [Seasons](help:seasons), [Spells](help:spells), [House Rules](help:house-rules), [Players](help:players), [Getting started](help:guide-getting-started)

# The saga
<!-- help: saga -->

The top node of the tree. It shows the saga's own details and what it holds.

**You type:** with `e` (Edit Saga): the Name, Storyguide and Description; whether to Keep season records; the Books in play; and the optional rules, each off until you turn it on.

**The app works out:** the counts of covenants, characters, laboratories, books and spells, and a summary of the books in play and the optional rules turned on ("none (the book's standard rules)" when none is).

### What the saga shows
<!-- help: saga-summary -->

- **Current date**: the season and year the saga is in. It is also shown in the header on every screen of the workspace.
- **Books in play**: the sourcebooks the troupe uses. Catalog pickers hide entries from books not in play, the season plan offers a supplement's activities only while its book is in play (a plan already made keeps its activity), and a supplement's own rules apply when its book is in play.
- **Optional rules**: Simple dice only, Dominion Magic Resistance, Harsher Infernal vis and Enforce creation rules strictly. Each one's effect is described beside it in Edit Saga. These come from Ars Magica Definitive Edition, Chapter 16: Sagas, Rules Questions.
- **Keep season records**: when on, each season applied is kept under Seasons in the tree. When off, only the characters' Diaries keep them.

### More on the saga
<!-- help: saga-more -->

- **Set Date** moves the saga to any season and year without applying anything. Use it to put the date back after advancing by mistake; it does not undo what the season did (a backup is kept for that, see [Advance Season](help:advance-season)).
- **Import** opens the Import Data dialog: characters, covenants or laboratories exported from another saga, books from a CSV file, or spells from a CSV file. See [Import Data](help:import-data).

New (`n`) on the saga offers New Covenant, New Character, New Laboratory and, while a magus has no familiar, Bind Familiar.

**See also:** [The workspace](help:workspace), [Advance Season](help:advance-season), [Import Data](help:import-data), [Creation Worksheet](help:creation-worksheet), [Getting started](help:guide-getting-started)

# Characters group
<!-- help: character-group -->

The Characters node under a covenant, or Unassigned Characters under the saga. It lists the characters in the tree below it; select one there to open their sheet.

**You type:** nothing here. `n` (New) offers New Character, with this covenant already chosen, and Bind Familiar while a magus has no familiar.

**The app works out:** the count in the node's label.

### New Character
<!-- help: character-group-new -->

The Create a New Character form asks for a Name, a Type (magus, companion, Mythic Companion or grog) and a covenant. For a type the book has templates for, it also offers a **Template**:

- **None**: the character starts In Creation, to be built step by step with the [Creation Worksheet](help:creation-worksheet).
- **A template**: one of the book's ready-to-play characters (Ars Magica Definitive Edition, Chapter 3: Characters, Character Templates). It fills the new sheet and the character starts In Play. If the template leaves a name to the player, such as an Area Lore's area, the app asks for it before the character is made; cancelling that cancels the new character.

The line above Create describes the template you chose.

**See also:** [Laboratories group](help:laboratory-group), [Creation Worksheet](help:creation-worksheet), [The workspace](help:workspace), [How to create a character, covenant or laboratory](help:guide-creation)

# Laboratories group
<!-- help: laboratory-group -->

The Laboratories node under a covenant, or Unassigned Laboratories under the saga. It lists the laboratories in the tree below it; select one there to open its sheet.

**You type:** nothing here. `n` (New) offers New Laboratory, with this covenant already chosen. The form asks for a Name, a Size and the covenant, and whether it is one of the covenant's starting labs (paid for from the covenant's Build Points, one free per magus).

**The app works out:** the count in the node's label. A new laboratory starts In Creation.

**See also:** [Characters group](help:character-group), [Creation Worksheet](help:creation-worksheet), [How to create a character, covenant or laboratory](help:guide-creation)

# Unassigned Books
<!-- help: unassigned-books -->

The books in the saga that nobody owns: not a covenant's library, a laboratory or a character. The node only appears in the tree while there are some.

**You type:** a book's details with `a` and `e`, the same form as a library's. Give a book an owner and it moves off this list.

**The app works out:** the count, and the details panel for the chosen book.

### Acting on several books
<!-- help: unassigned-books-marked -->

Mark books with Space (or Ctrl+click) to act on them together. With books marked, `e` gives them all one new owner and `d` deletes them all, each after a confirmation. With none marked, e and d act on the highlighted book.

Books imported from a CSV file on the saga (More, Import, Books) land here.

**See also:** [Import Data](help:import-data), [The workspace](help:workspace), [How to import and export](help:guide-import-export)

# Seasons
<!-- help: seasons -->

The saga's record of past seasons: what everyone did each season and what it gave them. A record is added each time a season is applied with [Advance Season](help:advance-season), as long as Keep season records is on in Edit Saga.

**You type:** nothing; the records are written by the app.

**The app works out:** one row per season, newest first ("Spring 1220 (3 people)"), and below the list the chosen season's record, grouped by covenant. Each person's line gives the activity, what it was on and its result. A plan that could not be carried out says why, and a magus or companion with nothing planned is shown as "nothing planned". Winter's lines also include aging rolls, grogs' yearly updates, business upkeep and vis harvests.

When season records are off, the view says so and no new seasons are added; each character's Diary still has their own entry.

**See also:** [Advance Season](help:advance-season), [Season Summary](help:season-summary), [How to plan and run a season](help:guide-seasons)

# Spells
<!-- help: spells -->

Every spell the saga knows: the catalog's spells from the sourcebooks, and the saga's own. The list stretches down to a details panel that shows the chosen spell in full.

**You type:** the saga's own spells, with `a` (add) and `e` (edit). Catalog spells are read-only: to make your own version of one, add a spell with `a`. `d` deletes only the saga's own spells.

**The app works out:** each spell's Arts, level, Range, Duration and Target, and, in the details panel, its magnitude, vis cost and casting time. The section title shows how many spells are listed out of how many there are.

### Filtering
<!-- help: spells-filter -->

`/` moves to the search box. The filters apply as you change them:

- **Search** looks in spell names and descriptions; every word must match.
- **Source**: one sourcebook, or "The saga's own".
- **Technique** and **Form**: each also matches a spell that has it as a requisite.
- **Ritual**: Rituals or Formulaic.
- **Level** from and to. General spells pass any level range.

### Importing spells
<!-- help: spells-import -->

Spells can be added in bulk from a CSV file: on the saga node, More, Import, then Spells. They become the saga's own spells. See [Import Spells](help:import-spells).

**See also:** [Import Spells](help:import-spells), [House Rules](help:house-rules), [How to import and export](help:guide-import-export)

# House Rules
<!-- help: house-rules -->

The Virtues, Flaws, Boons and Hooks made for this saga: house rules, or entries from books the app's catalogs don't carry. They show in the pickers alongside the catalog's entries, and they count as always in play whatever books the saga uses.

**You type:** with `a` and `e`: what the entry is For (a Character Virtue or Flaw, a Laboratory Virtue or Flaw, or a Covenant Boon or Hook; this is fixed once the entry is made), its Name, Type, Tier, Category, whether it can be taken more than once, and a Description.

**The app works out:** the points from the type and tier (Free 0, Minor 1, Major 3; Flaws and Hooks give points rather than cost them), and, in the details panel, who holds the entry.

### What house rules don't do
<!-- help: house-rules-limits -->

House rules are text only: the rules engine applies no effects for them. Two entries of the same kind can't share a name, type and tier. `d` won't delete an entry that a character, laboratory or covenant still holds; the message names them, so remove it there first.

When a character, laboratory or covenant is exported, the house rules it uses go with it.

**See also:** [Spells](help:spells), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Players
<!-- help: players -->

Who can sign in to this saga when you host it, so that players open it in a web browser from their own computers. Each player signs in with their name and the passcode you give them. Your own window, the app run on your computer, never asks.

Only the storyguide sees this node: your own window, or someone signed in with the Storyguide role.

**You type:** with `a` and `e`: the player's Name (what they type to sign in; no two players may share one), their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. When editing, leave New passcode blank to keep the one they have. `d` deletes a player after a confirmation; they can no longer sign in.

**The app works out:** in the details panel, the characters each plays and what they may change. Passcodes are stored only scrambled (a salted hash), so the app can check one but no one can read it back from the saga file: if a player forgets theirs, give them a new one.

### What a signed-in player can do
<!-- help: players-access -->

Choose who plays a character with **Played by** in the character's Biographical Detail (only the storyguide can). A signed-in player can then:

- change the characters they play, with those characters' familiars, laboratories and books, and their season plans;
- change the covenants too, if you ticked May change covenants for them;
- look at everything else, and Export a character, laboratory or covenant (the file downloads in their browser).

Only the storyguide (your own window, or someone signed in as Storyguide) can make new records (New), advance or set the season, import, move vis, share spells, or change the saga itself, its house rules and its players. Keys a player can't use there don't appear, and if a change slips through anyway, the app doesn't save it and says so.

**See also:** [Signing in](help:sign-in), [How to host a saga](help:guide-hosting), [The saga](help:saga)

# Signing in
<!-- help: sign-in -->

When the storyguide hosts the app, opening a saga in a browser first asks who you are: type your Name and the Passcode the storyguide gave you, then Sign in. Name is not case-sensitive; the passcode is.

If the saga has no players yet, it can't be opened from a browser: the storyguide adds players on the saga's [Players](help:players) node. Your name is shown in the header beside the saga's date while you're signed in. Going back to the saga list (Escape) signs you out.

While several people have the saga open, each one's saves keep everyone else's changes, and within a few seconds the others' screens show them: the sheet on show updates where it is (with a note such as "Ana changed Corvinus; reloaded"), and if two people open the same character, both are told ("Ana is also on Corvinus"). If the record you have open is deleted elsewhere, the saga is shown instead.

**See also:** [Players](help:players), [How to host a saga](help:guide-hosting), [Saga picker](help:saga-picker)
