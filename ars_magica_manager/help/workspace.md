# Title page
<!-- help: title-page -->

The page the app opens on: the illuminated A and the name Armarius, the tagline, the version and the name of its major version (see What's New), and the ways on.

- **Open Saga** opens the saga you had open last (or the only saga, if there is one). It isn't offered when there is no saga to open.
- **All Sagas** goes to the [saga picker](help:saga-picker), to choose a saga, start a new one or delete one.
- **New Saga** goes to the saga picker and opens its New Saga form at once; the new saga opens when you save it. Cancel the form and you stay on the picker.
- **Help** opens Help.

<!-- tui -->
Enter takes the first of them. Choose with the arrow keys and Enter, and `q` quits. A player's copy of a hosted saga skips the title page and opens on the saga picker, where they sign in.
<!-- /tui -->
<!-- gui -->
Click one; Enter takes the first of them, as the line under the buttons says. The window's own buttons, at its top right, minimise, maximise and close it.

The same illuminated A is the app's icon, on the Windows taskbar and in Alt-Tab. `run-gui.bat` opens the app with no console window behind it.
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
The line under the page's title names the folder the sagas are read from. If the app ever closes itself without a word, `crash.log` in that folder records where it was; the file stays empty until then.
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
- **Seasons**: the record of each season applied.
- **Saga Content**: the books in play, the catalogs the saga hides, its House Rules, its own spells and (for the storyguide) its players.
- **The Armarium** and **The Custodia Mirabilium** (the storyguide's only): every book, and every enchanted device, in the saga, held or [unassigned](help:armarium).

A character's node shows its type, for example "Leandro (magus)". A covenant, laboratory or character still being made is marked "(creating)".

### Moving around
<!-- help: workspace-moving -->

- Arrow keys move along the tree. **Enter** shows the chosen node and moves focus into it: into a sheet's first section, or into a list (Seasons).
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
- **Ctrl+F** opens Find, to open any record by its name. See [Find](help:find).
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
- A saga's page opens on **The Troupe**: the player characters, the covenants the troupe plays and the pages you have bookmarked, each a click from its page (see [The Troupe](help:saga-troupe)). **The Covenants** shows its covenants as cards, then the characters and laboratories that belong to no covenant. **The Region** holds its Tribunals and neighbours and **The Bestiary** its creatures. **Seasons** sets the date and opens the seasons played; **Rules and Content** opens Saga Content; **Saga Settings** holds its details, seasons, optional rules and ruling templates; **Saga Management** holds Import, Export Saga, Export Pack and Host for Players.
- A covenant's page lists its people, laboratories and possessions; click a person or a laboratory to open their page. A magus's familiar opens from the magus's page.

A covenant, laboratory or character still being made is In Creation: its page is drawn on drafting vellum, and its header has the In Creation / In Play switch and the Creation Worksheet.

### Moving around
<!-- help: workspace-moving; gui -->

- A record's page is a book of chapters: the rail on the left lists them, and a click shows one. The chapter scrolls if it is longer than the window. Come back to a page and it opens on the chapter you left it at, until the app is closed.
- The player characters are on the saga's first chapter, [The Troupe](help:saga-troupe), and so is any page you bookmark.
- Cards and rows are chosen with a click; a card that opens a page (a covenant, a person, a laboratory, a familiar) opens it on a click.
- The trail goes back up. Leaving a page cancels a form left open on it.
- The window can be moved by dragging the app's name in the middle of the top bar (a double-click maximises it), and resized from its edges and corners.

### What the buttons act on
<!-- help: workspace-keys; gui -->

- A section's **Add**, **Edit** and **Delete** buttons act on that section. Edit and Delete act on the row or card last clicked in it (or the only one there is), and stay greyed out until there is one. Delete asks first.
- A form, a list to choose from and a question (such as Delete's) open in a window of their own over the page, one after another when a button asks several things, and the page waits until the window is closed. Each has the app's title bar: drag it to move the window, and use its close button, or its maximise button on a form or list (double-clicking the bar does the same, and a form's edges resize it). Choosing a file or folder uses the system's own window. A window is sized to what it holds, grows when a choice shows more fields (as Lab Work's does), and past the height of the screen its fields scroll inside it, above its buttons, so a long form such as Export Pack's list of ticks can be read to its end. The form's Save keeps what you typed, and Cancel leaves things as they were; if you have changed anything, Cancel, the close button and Esc ask first, so a slip doesn't lose your work. A form that only works something out, with Close in place of Cancel, doesn't ask. Every change is saved to the saga file at once. One form is open at a time: while one is open, the page's other buttons wait, and clicking a New card (such as **New Magus** while a New Character form is open) takes you back to the form already open instead of opening another.
- Buttons in a page's header or chapter heading, such as **Edit Covenant**, act on the record itself.
- What the terminal keeps in its New and More menus is on the page itself: a New card at the end of the cards it adds to (**New Covenant**, **New Character**, **New Laboratory**), or a button in the chapter or section it acts on, such as **Give** beside a list's Add, Edit and Delete, **Set Up Research Library** on a covenant's Library or **Set Date** in the saga's Seasons chapter.
- A record's **Manage** chapter holds what acts on the record as a whole: Export, Update from a File, Print to PDF, Show on Map (on the desktop, for a covenant, laboratory, neighbour or creature on one of the saga's maps: see [The Atlas](help:saga-atlas)) and Delete.
- **Advance Season**, the card at the foot of the chapters on the left, shows the present season's medallion and date; click anywhere on it to advance the saga by one season, after asking first. It is on every page of a saga with chapters, but not on a Creation Worksheet, a Fight or a Siege. See [Advance Season](help:advance-season).
- The **gear** at the right of the top bar, past a thin rule after Help, holds the app's own settings: switch the theme, turn the sounds on or off, and Reduce motion. A tick shows which are on.
- The **bookmark**, a ribbon at the right of the header of a character, covenant, laboratory, familiar, Tribunal, neighbour or creature, keeps that page on the saga's [The Troupe](help:saga-troupe) chapter; it fills in when the page is bookmarked, and a second click takes the bookmark out.
- **Find**, just left of Help, or `Ctrl+F`, drops a box to type a name in and open that record, wherever it is in the saga. See [Find](help:find).
- **Help**, or `?` or `F1`, opens Help on the page and chapter on show. `Esc` goes back a page (or cancels a form that is open), and `q` quits. See [Keys](help:keys).

### The Inspector and the theme
<!-- help: workspace-status; gui -->

The Inspector, on the right of a record's page, shows whatever you last clicked on the page in full: a row, a card, a book, a spell.

**Switch to**, in the gear's menu at the right of the top bar, switches between the two themes, Scriptorum (aged parchment and iron gall ink) and Scriptorum Dark (vellum by candlelight); it names the one it switches to. The desktop remembers your choice on this computer and opens in it next time.

While a saga is open, the headpiece band under the top bar carries the present season's medallion at its centre, drawn in the set the saga chooses (the saga's settings, Medallion style). The same medallions mark the seasons elsewhere: the Seasons page's title and each past season's heading, each season's column in Ahead (on the Seasons page and a covenant's Seasons chapter), a covenant's header (its own Covenant Season, beside its Magic Aura and Loyalty, with no words), the title of a covenant's Seasons chapter, a character's This Season, the column heads of a character's and a laboratory's calendar, and a siege's track. The present season's medallion glows. A figure drawn as a medallion, such as an aura or a Loyalty, takes the same set in its own colour. They change with the season when it is advanced, and with the set when the saga's settings change it.

**Sounds**, in the gear's menu, turns the sounds on or off, and the app remembers which. Sounds are kept for moments that mean something: a page turning when you open a chapter (a longer one for a record or page), a quill when a form is saved, coins in a Treasury, a chest for the Inventory, a wax seal when the new season comes to the top of its dial, and a dull knock when an entry is refused. Plain button presses stay silent. While the sounds are on and Armarius is the active window, it keeps the audio device awake with silence, so Bluetooth speakers and headphones don't lose the start of each sound. The sounds play on Windows only.

The pages move a little, never in your way: the Inspector's new item inks in on its gilt leaf as a sheen of light crosses it, a chosen row's gold wash spreads from the left with its leaf after it, a chapter fades in with a small slide, and an experience line that has moved since you last saw it (after Advance Season, or an edit) grows to its new length. When the season advances, a dial of the four seasons turns in the middle of the window to bring the new one to the top, then shows its medallion large with its name and year (a click or a key skips it); a wax seal is pressed on the page for a moment when a record is moved to In Play (its initial). **Reduce motion**, in the gear's menu, stills them: the pages change at once, with no dial and no seal; it shows ticked while it is on, and the app remembers your choice. Until you choose, it follows Windows' own Animation effects setting.

**See also:** [The saga](help:saga), [Saga Content](help:saga-content), [Seasons](help:seasons), [Getting started](help:guide-getting-started)

# Find
<!-- help: find -->

Find opens any record in the saga by its name, without going through the
pages above it.

<!-- tui -->
**Ctrl+F** (`^f Find` in the footer), anywhere in the workspace, opens
Find: a box to type in over
the list of matches. Each letter typed narrows the list. **Down** moves
into the list and **Enter** opens the match chosen (Enter in the box opens
the first); the tree moves to the record and its sheet shows. **Esc**
closes Find and leaves you where you were.
<!-- /tui -->
<!-- gui -->
**Find**, in the top bar just left of Help, or **Ctrl+F** on any page of a saga,
drops a box under the button with the matches below it. Each letter typed
narrows the list. **Up** and **Down** choose a match and **Enter** opens
it, or click one; it opens below the page on show, so the trail leads
back. **Esc**, or a click anywhere else, closes Find. It lists sixty
matches at most, and says how many more there are.
<!-- /gui -->

Each match shows its name, what it is and where it is: "Gottfried of
Arnsberg · Lord · The Drachenfels".

- **What it finds:** characters, covenants, laboratories, familiars,
  Tribunals, neighbours of every kind (lords, towns, the Church,
  universities, factions, threats, places, customs and lore), creatures,
  books, spells and enchanted devices.
- **By name first,** in any case and with or without accents
  ("dammerstein" finds Dammërstein): names that start with what you
  typed (a leading "The" or "A" passed over), then names with a word
  that does, then names that hold it anywhere. Within each, a name
  that is exactly what you typed comes first, the kind it ends with
  aside: "rhine" lists The Rhine Tribunal before The Rhine Gorge.
- **Then by what it is tied to,** with the reason shown beside the
  match: a faction by its members ("member Gottfried of Arnsberg"), a
  record by the place it is at, and by the Tribunal whose lands it lies
  in ("in the lands of Rhine", set on a place: see
  [The Place tab](help:tab-nb-place)).
- **Books, spells and enchanted devices** have no page of their own. A
  spell opens the page of the magus who knows it, at Known Spells with
  its row chosen; a spell nobody knows is not listed. For the
  storyguide, every book opens [the Armarium](help:armarium) and every
  device [the Custodia Mirabilium](help:custodia), at its row (a filter
  hiding it is cleared), held or unassigned. For a player, a book or
  device opens the page of whoever holds it, at its row (a covenant's
  book in its Library, a device among its holder's Enchanted Devices),
  and one nobody holds is not listed.
- **Secrets, for the storyguide:** your Find also looks in each record's
  [Secrets](help:tab-secrets), last, a match there marked "secret" with
  the words around it. A player's Find never does, and in
  [Player view](help:player-view) yours doesn't either.
- **What the players don't know of** is never listed for a player or in
  Player view, nor named as where another record is.
- **Not searched:** notes and descriptions, the seasons played and the
  calendar.

**See also:** [How to find a record](help:guide-find-record)

# The saga
<!-- help: saga -->

<!-- tui -->
The top node of the tree. It shows the saga's own details and what it holds.
<!-- /tui -->
<!-- gui -->
The saga's page, opened from its card on the Sagas page. It has ten chapters, and opens on the first. **The Troupe** gathers the player characters, the covenants the troupe plays and the pages you have bookmarked (see [The Troupe](help:saga-troupe)). **The Covenants** shows its
Covenants, Unassigned Characters and Unassigned Laboratories as cards, each
heading ending in a blank card (New Covenant, New Character, New
Laboratory) that makes one more. A covenant's card shows its aura with its Boons and
Hooks counted (each Aura Boon adds 1, Definitive Edition p. 183), the same total its
page shows. **The Region** holds its Tribunals, each a card with a New Tribunal card after them, and its neighbours; **The Atlas** its maps, with a pin for each covenant, place and neighbour on them (see [The Atlas](help:saga-atlas)); and **The Bestiary** its creatures (see [The Region](help:region) and [The Bestiary](help:bestiary)). **Conflicts** lists its fights and sieges (see [Conflicts](help:conflicts)). **Seasons** sets the date (Set Date) and
opens the seasons played; **Rules and Content** opens Saga Content; **Saga Settings** holds its details, its seasons, its optional rules and its ruling templates (see [Saga Settings](help:saga-settings)); and
**Saga Management** holds Import, Export Saga, Export Pack and Host for Players. A familiar is bound on its
magus or in their laboratory.
<!-- /gui -->

<!-- tui -->
**You type:** with `e` (the saga's settings): the Name, Storyguide and Description; whether to Keep season records; the optional rules of the books in play, each off until you turn it on; and the **Ruling templates** a Tribunal's rulings are written from (see [Hold Tribunal](help:hold-tribunal)): `Enter` opens the list, where each can be added, changed or removed. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /tui -->
<!-- gui -->
**You type:** the Name, Storyguide and Description, with **Edit Saga** on [Saga Settings](help:saga-settings), where everything else about the saga is set too. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /gui -->

**The app works out:** the counts of covenants, characters, laboratories, books and spells, and a summary of the books in play and the optional rules turned on ("none (the book's standard rules)" when none is).

### What the saga shows
<!-- help: saga-summary -->

<!-- tui -->
- **Current date**: the season and year the saga is in. It is also shown in the header on every screen of the workspace.
<!-- /tui -->
<!-- gui -->
- **Current date**: the season and year the saga is in, under its name. It is also shown under the chapters, beside Advance Season, on every page with chapters.
<!-- /gui -->
- **Books in play**: the sourcebooks the troupe uses, and how many of the saga's own sources are in play. They are chosen on [Saga Content](help:section-books-in-play), which says what a book out of play switches off.
- **Optional rules**: Simple dice only, Dominion Magic Resistance, Harsher Infernal vis, Starting income by number of magi, Enforce creation rules strictly, Extended book Quality, Bruises, Dominion growth and Auras change. Each one's effect is described on its card in the saga's settings; Harsher Infernal vis (Realms of Power: The Infernal), Extended book Quality (Covenants), Dominion growth (Realms of Power: The Divine) and Auras change (Realms of Power: Magic) are offered only while their book is in play. With Dominion Magic Resistance on, a Christian, Jew or Muslim (or anyone whose religion is left blank) living in a Dominion aura shows Magic Resistance of 5 x that aura on their sheet. Simple dice only and Dominion Magic Resistance are house rules the Definitive Edition offers as examples (Chapter 16: Sagas, Rules Questions, p. 524), not rules of the game; Extended book Quality comes from Covenants' Library chapter. Standard apprenticeship model (Apprentices) is offered only while that book is in play, off by default: see the Apprenticeship step of [the Creation Worksheet](help:creation-worksheet-steps). Learning cantations in play (Apprentices) is offered only while that book is in play, off by default: see [Learn a Cantation](help:learn-cantation). Hazardous Laboratory Texts and No magical copying of Lab Texts (Transforming Mythic Europe pp. 103-104) are offered only while that book is in play. With the first, a Lab Text copied by magic below the Finesse Total that copies it flawlessly isn't useless: each use of it makes an extra Experimentation roll, its risk modifier half the pages spoiled in ten (the season's Diary entry gives it). With the second, Copy books by magic refuses Lab Texts: each is written by hand. Charter Strength (Transforming Mythic Europe p. 36) is offered only while that book is in play: a charter between a lord and a town or covenant has two scores; More's Draft the Charter and Seek a Loophole on its lords.
<!-- tui -->
- **Keep season records**: when on, each season applied is kept under Seasons in the tree. When off, only the characters' Diaries keep them.
<!-- /tui -->
<!-- gui -->
- **Keep season records**: when on, each season applied is kept on the Seasons page. When off, only the characters' Diaries keep them.

On the desktop, the books in play are counted on the Saga Content card in Rules and Content, and the optional rules turned on are shown on [Saga Settings](help:saga-settings).
<!-- /gui -->

### Saga Settings
<!-- help: saga-settings; gui -->

Everything about the saga that can be set, on one chapter of its page, as cards under their sections' headings: **Saga Details**, **Seasons**, **Optional Rules** and **Tribunal**.

- **Saga Details** shows the Name, Storyguide and Description; **Edit Saga** changes them.
- A card's first line names the setting, and the line under it says briefly what it does. Click the card to read it in full in the Inspector, with its source for an optional rule.
- A **switch** at a card's upper right turns the setting on or off at once, as a book's chip does on Books in Play; there is no Save. The Inspector has the same switch.
- A **chip** at the upper right shows a setting chosen from a list (what idle magi, companions and grogs do, the set of Medallion Style, or the Ruling Templates): click it to change it.
- Clicking **Medallion Style** shows an example of every set in the Inspector, with the one in use marked. The set draws every medallion on the desktop: the seasons', and the figures', such as an aura or a covenant's Loyalty.
- **Ruling Templates** opens as a ledger, each template's name in red beside its words. A row too long for the window ends in dots: hover over it, or maximise the window, to read it all.
- **Optional Rules** are sorted by what they touch, each naming its book. All are off until you turn them on. A rule whose book is out of play is greyed out and can't be switched; it counts as off, and your choice is kept for when the book comes back. Books are chosen on [Saga Content](help:section-books-in-play).

### The Troupe
<!-- help: saga-troupe; gui -->

The saga page's first chapter, so the characters you play are a click away rather than inside their covenant's People.

- **Next Session**: the next evening of play, with its storyguide, who is coming and who is Away, and who plays whom; then the other planned [Sessions](help:tab-content-sessions) and the three played most recently. Saga Management's Sessions adds and changes them.
- **Player Characters**: every character whose Biographical Detail, in their Description chapter, names their **Player** (or who is **Played by** one of the saga's [players](help:players-access)), by covenant: the troupe's covenants first, then the others, then those who belong to none. Click one to open their sheet.
- **Stewards**: each Player's stewarded characters (a [Steward](help:players-access) keeps a character with no Player of its own between Sessions), and whether each has a plan for the current season. Not shown while the saga has no players.
- **Troupe Covenants**: the covenants the troupe plays, marked ✦ as on The Covenants.
- **Bookmarked**: anything else you bookmarked, by kind: characters, covenants, laboratories, familiars, Tribunals, neighbours and creatures. A bookmarked page that is a player character or a troupe covenant is shown once, above.

To bookmark a page, open it and click the ribbon at the right of its header, below its buttons: a faint outline becomes a filled ribbon. Click it again to take the bookmark out. Bookmarks belong to whoever reads the saga, so they are kept on this computer, saga by saga, and are not saved in the saga file: another computer, or someone who opens the same saga, has their own. A bookmarked record that is deleted drops off the chapter.

**The app works out:** who is a player character, from their Player; the cards' figures, as on The Covenants.

### More on the saga
<!-- help: saga-more -->

- **Set Date** moves the saga to any season and year without applying anything; it does not undo what a season did.
- **Undo Last Season** puts the whole saga back as it was before the last advance (see [Undoing a mistake](help:guide-seasons-undo)).
- **Import** opens the Import Data dialog: characters, covenants or laboratories exported from another saga, books from a CSV file, or spells from a CSV file. See [Import Data](help:import-data).
- **Host for Players** lets the players open the app in a web browser on their own computers, and **Stop Hosting** ends it. Only the storyguide's own window offers them. See [How to host a saga](help:guide-hosting).

<!-- tui -->
New (`n`) on the saga offers New Covenant, New Character, New Laboratory and, while a magus has no familiar, Bind Familiar.
<!-- /tui -->
<!-- gui -->
Set Date is in the Seasons chapter, and Import, Export Saga and Host for Players in Saga Management. The New cards on The Covenants make a covenant, character or laboratory, and those on The Region a Tribunal or neighbour.
<!-- /gui -->

**See also:** [The workspace](help:workspace), [Advance Season](help:advance-season), [Import Data](help:import-data), [Creation Worksheet](help:creation-worksheet), [Getting started](help:guide-getting-started)

# Characters group
<!-- help: character-group -->

<!-- tui -->
The Characters node under a covenant, or Unassigned Characters under the saga. It lists the characters in the tree below it; select one there to open their sheet.

**You type:** nothing here. `n` (New) offers New Character, with this covenant already chosen, and Bind Familiar while a magus has no familiar.
<!-- /tui -->
<!-- gui -->
A covenant's People chapter, or Unassigned Characters in the saga's The Covenants chapter, shows the characters as cards; click one to open their sheet.

**You type:** nothing here. The **New Character** card at the end of the cards makes one, with this covenant already chosen. A familiar is bound on its magus's page (or in their laboratory).
<!-- /gui -->

**The app works out:** the count in the node's label.

### New Character
<!-- help: character-group-new -->

The Create a New Character form asks for a Name, a Type (magus, companion, Mythic Companion or grog) and a covenant. For a type the book has templates for, it also offers a **Template**:

- **None**: the character starts In Creation, to be built step by step with the [Creation Worksheet](help:creation-worksheet).
- **A template**: one of the book's ready-to-play characters (Ars Magica Definitive Edition, Chapter 3: Characters, Character Templates). It fills the new sheet and the character starts In Play. If the template leaves a name to the player, such as an Area Lore's area, the app asks for it before the character is made; cancelling that cancels the new character.
- **A Grogs template** (a grog, while Grogs is in play; marked "(Grogs)"): one of the nineteen kinds of grog in Grogs, Chapter 7, such as The Advisor or The Street Thug. These are guidance rather than finished characters, so the app asks for the template's choices next (see [A Grogs template](help:grog-templates)) and the grog starts In Creation.
- **A quick recipe** (marked "(DE quick)"): the Definitive Edition's Quick and Easy Virtues and Flaws, for a grog, a martial, learned, social or magical companion, or a magus. The app asks for the recipe's choices next (see [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws)) and the character starts In Creation with those Virtues and Flaws.
- **A Mythic Companion template** (a Mythic Companion; marked with its book, such as "(DE)" or "(RoP:D)"): one kind of Mythic Companion, such as the Faerie Doctor or the Zahid, with the Virtues and Flaws its book requires and its minimum Abilities. See [A Mythic Companion template](help:mythic-companion-templates).
- **A supplement's character** (a companion, grog or Mythic Companion; marked with its book, such as "(RoP:D)"): a ready-made character from a supplement, such as the Byzantine Priest or The Church's Anchoress. See [A supplement's character](help:companion-sample-templates).
- **A Grogs template as a companion** (a companion, while Grogs is in play): see [A Grogs template as a companion](help:grog-template-companion).
- **An animal template** (a grog, while Grogs is in play; marked "(Grogs, an animal)"): the book's sample Dog, Horse and Hawk (Grogs, Chapter 7: Horses & Hounds, page 137). See [Animal grogs](help:animal-grogs).

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

### Quick and Easy Virtues and Flaws
<!-- help: quick-virtues-flaws -->

The Definitive Edition's Quick and Easy Virtues and Flaws (Chapter 3, page 47) are a fast way to choose a character's Virtues and Flaws. Each type's Template list has its recipes, marked "(DE quick)":

- **Grog**: a Minor Personality Flaw for how you want to play the grog, Covenfolk, and one Minor Virtue: Warrior for a grog who fights, Educated for one who is educated, Arcane Lore for one who knows about the supernatural, or Puissant in the grog's specialty for anyone else (typed in, such as Craft: Blacksmith).
- **Companions**: a Major Personality or Story Flaw, which says what stories they are in, Covenfolk, and three points of Virtues from one of four recipes:
  - **Martial companion**: Warrior, with Puissant and Affinity in one Martial Ability.
  - **Learned companion**: Educated, with either Puissant in two Academic Abilities, or Puissant and Affinity in one.
  - **Social companion**: one of Gossip, Piercing Gaze, Social Contacts, Well-Traveled or Venus' Blessing, with Puissant in two Social Abilities. The book doesn't say which Abilities are Social; the app offers Bargain, Carouse, Charm, Etiquette, Folk Ken, Guile, Intrigue and Leadership.
  - **Magical companion**: one Minor Supernatural Virtue that grants an Ability, such as Second Sight, with Puissant and Affinity in that Ability.
- **Magus**: a Major Personality or Story Flaw, The Gift and the Hermetic Magus Social Status, Deficient Form in a Form you are not interested in, a Minor Magical Focus that doesn't rely on that Form (typed in, such as Fire), Puissant and Affinity in one Technique that overlaps the Focus, and Puissant in one Form that overlaps it. The House's free Virtue is chosen on the worksheet.

**Templar companion (The Church).** The Social Status is the character's rank
in the Knights Templar: Brother Knight, Brother Sergeant, Brother Chaplain,
Templar Administrator, Templar Specialist, Templar Commander, or an associate
(Confrere or Consoeur) or servant (The Church pp. 123-125; the Definitive
Edition reprints them, pp. 73 and 111-112). "Renowned among the brothers"
adds Templar Prestige (Reputation 4 among the Templars). An office (Templar
Office Holder) is a second Social Status, taken on the sheet. A commander
already has the brother-knight's standing and Temporal Influence free.

**You choose:** where the recipe gives several ways (the grog's Virtue, the Learned companion's), which one; the Abilities, Arts or Virtue each part names; the **Flaw**, from the books in play; and the **Social Status** (Covenfolk to start with; a magus's is Hermetic Magus).

**The app works out:** the line under the form gives the Virtue and Flaw points so far. Use refuses a choice that breaks the type's limits. A grog's are those of [A Grogs template](help:grog-templates). A companion's and a magus's: nothing Hermetic without The Gift, at most one Major Hermetic Virtue, at most ten points of Flaws and five Minor Flaws, no more Virtue points than Flaw points, exactly one Social Status, and the same Ability or Art named twice by the same Virtue. A Social Status that costs a point is refused here, since it leaves the Virtues a point over: take it on the worksheet with another Flaw. Cancelling makes no character.

**What the character starts with:** those Virtues and Flaws, and nothing else: the recipe is only the Virtues and Flaws. The character starts **In Creation**, so you finish on the [Creation Worksheet](help:creation-worksheet): Characteristics, a childhood, Later Life, training packages, and a magus's House, apprenticeship and spells. You can change the Virtues and Flaws there too.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [How to start a character](help:guide-creation-character-new)

### A Mythic Companion template
<!-- help: mythic-companion-templates -->

A Mythic Companion's Template list has one template for each kind of Mythic Companion the books in play describe, marked with its book: the Definitive Edition's Devil Child, Faerie Doctor, Nephilim and Spirit Votary (Chapter 3, pages 56 to 58), Realms of Power: The Divine's Zahid, Perfectus and Kabbalist, Realms of Power: The Infernal's Diabolist and Summoner, Houses of Hermes: True Lineages' Blood of Heroes, and Art & Academe's Maestro, and Against the Dark's Dragon-born and Varcolac.

**Dragon-born** (Against the Dark p. 108). A zmaj's human child, one of
the Magic Kin (Realms of Power: Magic p. 89): Greater Immunity (fire), a
Personal Power mirroring one of the dragon father's (Lungs of the Fish,
Hands of the Fiery Beast, or one of your own), Self-Confident, and the
Common Flaw, greed for gold (Avaricious) or for women (Lecherous). Second
Sight sees a snake's pupils and a sheen of scales.

**Varcolac** (Against the Dark p. 122). A man who takes a wolf's shape:
born to it (Shapeshifter), born to it and a Lycanthrope, taught
(Skinchanger), or a kudlak, a nightwalker of the kudlaki (Nightwalker,
Versatile Phantasticum). Good or evil, he becomes a bestial vampire when
he dies.

**The template gives:** the Mythic Companion Virtue and every Virtue and Flaw the book says that kind must take, such as a Faerie Doctor's Dowsing, Curse-Throwing and Wise One.

**You choose:**

- where the book gives a choice, which one: a Devil Child's Demonic Might or Demonic Powers, a Spirit Votary's one Major or three Minor Supernatural Virtues, a Kabbalist's Holy Method and two Holy Powers, the free Minor Virtue of a Diabolist, Summoner or Maestro;
- each Flaw the book allows "or a suitable substitute" for, the book's own chosen to start with;
- anything the Virtues name, such as the spirit of a Spirit Votary's Spiritual Pact;
- **Another Virtue** and **Another Flaw**: more of the player's own, from the books in play. Each point of Flaws allows two points of Virtues, plus the free Minor Virtue, so a Nephilim, Zahid or Kabbalist needs about five points of Flaws to pay for what the book requires;
- **The book's minimum Abilities**, ticked: the scores the book says the character should start with (90 xp for a Zahid), put on the [Creation Worksheet](help:creation-worksheet) as xp. Untick it to spend the xp yourself. Where they leave a name to you, such as a Spirit Votary's local Area Lore, the form asks for it;
- the **Social Status**, where the book doesn't fix it.

**The app works out:** the line under the form gives the Virtue points so far against what the Flaws allow, and the Flaw points. Use refuses a choice that breaks a Mythic Companion's limits: exactly one Mythic Companion Virtue, no Gift and nothing Hermetic, at most ten points of Flaws and five Minor Flaws, no more Virtue points than twice the Flaw points plus one, and nothing taken more often than the book allows. The Biography notes the template, its book's advice and where the app differs from the book (the Hebrew of a Nephilim or Kabbalist is taken as Dead Language: Hebrew, a Perfectus's Church Lore as Organization Lore: Church).

The Definitive Edition's Perfectus is a Minor Social Status for an ordinary companion; the Perfectus template is Realms of Power: The Divine's Mythic Companion, a separate Virtue. The character starts **In Creation**, and the worksheet does the rest.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws)

### A supplement's character
<!-- help: companion-sample-templates -->

The Template list also has the ready-made characters the supplements in play print, marked with their book. A named one is listed by its role, then its name, so you can tell what it is for: Bachelor of Arts at Paris - Gilpatrick (A&A), Guild Master Clothier - Doolin (C&G), Hound of God - Rothiger (HMRE). One the book leaves unnamed is listed by its role alone, such as Mystic Nun (TC). Unlike the Definitive Edition's templates, which start In Play, these start **In Creation**, so the worksheet checks them against the rules.

- **Companions**: Art & Academe's Leonardo Fibonacci, Gilles de Corbeil, Brogo the Dwarf, Brother Julian and Gilpatrick; City & Guild's Julian, Obano, Doolin and Banco; The Church's Mystic Nun, Anne, the Imposter, a Templar Commander and Templar Brother-Priest (pp. 126-127), and the first Franciscans Francis of Assisi, Brother Elias and Clare of Assisi; and the companions of Realms of Power: The Divine and other books.
- **Grogs**: The Church's grog templates, the Anchoress, the Beguine and the Priest's Wife (pp. 83-84), and a Franciscan Nun and Friar (p. 142), are on a grog's list and held to a grog's limits.
- **For the storyguide**: a saint or an antagonist the book prints for the storyguide, such as Francis and Clare of Assisi, or The Church's diabolist abbot Father Tino of Gradara (p. 97, a Mythic Companion), is marked "for the storyguide". It is taken as the book prints it, so Use doesn't hold it to its type's limits.

**You choose:**

- **The book's Virtues and Flaws**, ticked: untick one to leave it out.
- **Another Virtue** and **Another Flaw**: more of your own, from the books in play.
- **The book's Characteristics**, ticked: untick them to buy your own on the worksheet.
- **The book's Abilities**, ticked: the character's Abilities and specialties, put on the worksheet as xp (Native Language, a Virtue's own xp, Early Childhood, then Later Life). Where the book leaves a name to you, such as an Area Lore's area or a language, the form asks for it.
- the **Social Status**, from the book's.

**The app works out:** the line under the form gives the Virtue and Flaw points, and the xp a character has at the book's age against what its Abilities come to. Use refuses a choice that breaks its type's limits (a companion's, a grog's or a Mythic Companion's), except for a storyguide's character (as for [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws)); fewer Virtue points than Flaw points is allowed, since some books leave a companion a few points short for the player to fill. The character's age sets the year born, and its Personality Traits and Reputations come with it. The Biography notes the book's advice and where the app differs from the page, such as an older edition's Ability (Church Lore taken as Organization Lore: Church).

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [A Grogs template as a companion](help:grog-template-companion)

### A Grogs template as a companion
<!-- help: grog-template-companion -->

Grogs says any of its grog templates can be played as a companion simply by adding a Story Flaw (Chapter 7, page 95, and the "as Companion" notes of many templates). While Grogs is in play, a companion's Template list has each one, marked "(Grogs, as a companion)".

It asks for the same choices as [A Grogs template](help:grog-templates), with two differences: the choices are held to a companion's limits rather than a grog's (Major Virtues and Flaws and up to ten points of Flaws are allowed), and Next refuses until a **Story Flaw** is among them: choose one under **Another Flaw**, such as Dark Secret or Visions. The character is made a companion, without the Loyal +1 a grog gets, and the Biography notes it.

**See also:** [A Grogs template](help:grog-templates), [A supplement's character](help:companion-sample-templates), [New Character](help:character-group-new)

### Animal grogs
<!-- help: animal-grogs -->

A grog can be an animal: a horse, a hound, a hawk or any other beast that serves the covenant (Grogs, Chapter 7: Grog Templates, Horses & Hounds, pages 133-137). Make one from an animal template on the New Character form, or make a grog with no template and choose **Animal form** on its worksheet's Concept step.

**You choose (Animal Form):**

- **Kind**: a person, or a Clawed Beast, a Hoofed Beast, a Bird, or a Fish or Serpent. Each kind has its own penalties with humans (Presence and Communication: Clawed Beast -2/-5, Hoofed Beast -4/-5, Bird -1/-2, Fish or Serpent -5/-6) and its own aging.
- **Species**, such as Dog or Horse, and its **Language**, the animal language it speaks (its species', unless you name another).
- **Lifespan**: blank for the kind's own, or a species' own lifespan in years.
- **Size**, from -3 to +2. Strength gets +2 for each point of Size and Quickness loses one, added after the Characteristic points are spent.

From an animal template you also choose its age (Dog 1 or 4, Horse 3 or 10, Hawk 8), its Social Status and its Virtues and Flaws, from the book's suggested ones, as for [A Grogs template](help:grog-templates).

**The rules the worksheet checks:**

- An animal takes **Restricted Learning**; **No Hands** and **Mute** are part of its form and cost nothing. Its Social Status is Domestic Animal, Wanderer or Companion Animal (a Companion Animal starts with Loyal to Master +1). A Major Personality Flaw counts as Minor, and nothing about human society (a Craft, Educated, a noble's status and the like) can be taken.
- **No Early Childhood and no Native Language.** The **Pre-adult Life** step takes its place: its animal Language at score 2, and 120 xp spent up to the age it is grown, then 15 xp a year in Later Life. Restricted Learning puts the xp on at most five Abilities, and the animal Language is never raised.
- **A human Language** is learnt with a Source Quality of 4 + Cunning (lower for a negative Cunning), and Animal Ken never above its animal Language. On its sheet, Intelligence reads Cunning.
- **No training packages**, and the Ability cap is that of a person of the same share of a human life (advice, since the book says it "might" apply).
- **Aging**: a clawed beast is grown at 1, ages from 6 and makes five aging rolls a year (one each season and two in Winter), +1 to the roll every 2 years; a hoofed beast is grown at 3, ages from 20, two rolls (Summer and Winter), +1 every 5 years; a bird is grown at 8, ages from 55, a roll every second year, +1 every 15 years; a fish or serpent is grown at 24, ages from 170, a roll every fifth year, +1 every 50 years. A different lifespan scales the figures by 50 / lifespan. The rolls are made as the seasons pass.

An animal grog can be put on the covenant's Horses or Hounds list (Covenfolk tab).

**See also:** [A Grogs template](help:grog-templates), [Creation Worksheet](help:creation-worksheet), [Hounds](help:section-inh-hound)

**See also:** [Laboratories group](help:laboratory-group), [Creation Worksheet](help:creation-worksheet), [The workspace](help:workspace), [How to create a character, covenant or laboratory](help:guide-creation)

# Laboratories group
<!-- help: laboratory-group -->

<!-- tui -->
The Laboratories node under a covenant, or Unassigned Laboratories under the saga. It lists the laboratories in the tree below it; select one there to open its sheet.

**You type:** nothing here. `n` (New) offers New Laboratory, with this covenant already chosen.
<!-- /tui -->
<!-- gui -->
A covenant's Laboratories chapter, or Unassigned Laboratories in the saga's The Covenants chapter, shows the laboratories as cards; click one to open its page. A card's Aura is the one its Lab Totals use: its covenant's (Boons and Hooks counted), or its own place's, with the lab's own modifier.

**You type:** nothing here. The **New Laboratory** card at the end of the cards makes one, with this covenant already chosen.
<!-- /gui -->
The form asks for a Name, a Size and the covenant, and whether it is one of the covenant's starting labs (paid for from the covenant's Build Points, one free per magus).

**The app works out:** the count in the node's label. A new laboratory starts In Creation.

**See also:** [Characters group](help:character-group), [Creation Worksheet](help:creation-worksheet), [How to create a character, covenant or laboratory](help:guide-creation)

# The Armarium
<!-- help: armarium -->

Every book in the saga in one list: each covenant's library, each laboratory's and each character's books, and the books nobody holds, **Unassigned**. Lab texts, casting tablets and the volumes of a codex are each a row of their own; a volume's row names its codex. An armarius is a locked book closet (Covenants p. 92): this is the saga's.

Only the storyguide sees it, since the unassigned books are often ones the players haven't found yet.

<!-- tui -->
It is the **The Armarium** node in the tree, beside Saga Content.
<!-- /tui -->
<!-- gui -->
Open it from its card in the saga page's **Rules and Content** chapter, beside Saga Content.
<!-- /gui -->

**See also:** [The Custodia Mirabilium](help:custodia), [How to make a book or device for the players to find](help:guide-store-find), [Find](help:find)

### Books tab
<!-- help: tab-armarium -->

The Armarium's one list, [Books](help:section-armarium), its filter above it and the chosen book's details below.

### Books
<!-- help: section-armarium -->

Each row is a book: its Name, Type, Subject (the Art, Ability or spell it is on) and Holder, the covenant, laboratory or character that has it, or Unassigned.

**Filter:** choose a **Holder** (one record, or **Unassigned** for the books nobody has) and a **Type**; the list's title counts what it shows ("Books (3 of 59)").

<!-- tui -->
**You type:** `a` adds a book with no owner, `e` edits the chosen one and `d` deletes it, in the same form as a library's. More's **Give** hands the chosen book to a covenant, laboratory or character.

Mark books with Space (or Ctrl+click) to act on them together: with books marked, `e` gives them all one new owner and `d` deletes them all, each after a confirmation.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** makes a book with no owner, **Edit** and **Delete** act on the chosen row, in the same form as a library's, and **Give** hands the chosen book to a covenant, laboratory or character. **Change Owner** gives several of the books listed one new owner at once.
<!-- /gui -->

Give on an unassigned book writes only the receiver's Diary ("Received ..."); on a held book it is the usual Give, both Diaries. To take a book away from its holder, edit its Owner to "(none - unassigned)": nothing is written in a Diary. A book bound in a codex takes its whole codex with it, and the form says so. Deleting a held book names its holder first.

Books imported from a CSV file on the saga land here, unassigned.

**The app works out:** the count, who holds each book, and the chosen book's details, its holder a link that opens it.

**See also:** [Library tab](help:tab-cov-library), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# The Custodia Mirabilium
<!-- help: custodia -->

"The keeping of wonders": every enchanted device in the saga in one list, each held by a covenant, a laboratory or a character, or by nobody, **Unassigned**. Only the storyguide sees it.

<!-- tui -->
It is the **The Custodia Mirabilium** node in the tree, beside Saga Content.
<!-- /tui -->
<!-- gui -->
Open it from its card in the saga page's **Rules and Content** chapter, beside Saga Content.
<!-- /gui -->

**See also:** [The Armarium](help:armarium), [How to make a book or device for the players to find](help:guide-store-find), [Find](help:find)

### Enchanted Devices tab
<!-- help: tab-custodia -->

The Custodia's one list, [Enchanted Devices](help:section-custodia), its filter above it and the chosen device's details below.

### Enchanted Devices
<!-- help: section-custodia -->

Each row is a device: its Name, Type (Invested, Lesser, Charged, or Talisman), its first Effect and how many more ("+2 more"), and its Holder, or Unassigned. The details list every effect.

**Filter:** choose a **Holder** (one record, or **Unassigned**) and a **Type**.

<!-- tui -->
**You type:** `a` adds a device with no holder, `e` edits the chosen one and `d` deletes it, in the same form as on a holder's sheet. More's **Give** hands the chosen device to a covenant, laboratory or character.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** makes a device with no holder, **Edit** and **Delete** act on the chosen row, in the same form as on a holder's page, and **Give** hands the chosen device to a covenant, laboratory or character.
<!-- /gui -->

Effects are instilled, used and charged on the holder's page. Give on an unassigned device writes only the receiver's Diary; on a held one it is the usual Give. To take a device away, edit its Holder to "(none - unassigned)". Deleting a held device names its holder first.

A talisman given away or set down keeps its Talisman mark. The rules say only the magus who prepared an item can attune it, and that he always keeps an Arcane Connection to his talisman, which makes it dangerous in an enemy's hands (DE p. 259); whether it is still his talisman in other hands, and whether it can be attuned again, is the troupe's call.

**The app works out:** the count, who holds each device, and the chosen device's details and effects, its holder a link that opens it.

**See also:** [Enchanted Devices](help:section-char-devices), [Give](help:give)

# Seasons
<!-- help: seasons -->

The saga's record of past seasons: what everyone did each season and what it gave them. A record is added each time a season is applied with [Advance Season](help:advance-season), as long as Keep season records is on in the saga's settings.

**You type:** nothing; the records are written by the app.

<!-- tui -->
**The app works out:** what is waiting on you ([Needs You](help:section-attention)) and what is coming ([Looking Ahead](help:section-ahead)), then one row per season recorded, newest first ("Spring 1220 (3 people)"), and below the list the chosen season's record, grouped by covenant.
<!-- /tui -->
<!-- gui -->
**The app works out:** the Seasons page, opened from the saga's Seasons chapter (The Seasons Played), starts with what is coming ([Ahead](help:section-ahead)) and what is waiting on you ([Needs You](help:section-attention)), then lists the seasons in its rail, newest first, and shows the chosen season's record, grouped by covenant, a row a person. Just after Advance Season, the season just played out is first. The page's title carries the present season's medallion, and each season's heading its own, in the saga's set of medallions.
<!-- /gui -->
Each person's line gives the activity, what it was on and its result. A plan that could not be carried out says why, and a magus or companion with nothing planned is shown as "nothing planned". Winter's lines also include aging rolls, grogs' yearly updates, business upkeep and vis harvests.

When season records are off, the page says so and no new seasons are added; each character's Diary still has their own entry.

**See also:** [Advance Season](help:advance-season), [Season Summary](help:season-summary), [How to plan and run a season](help:guide-seasons)

## The Seasons panel
<!-- help: section-seasons-info -->

The date, how far Ahead looks, the next Tribunal's meeting, how many
things come this season, and how many are waiting on you (Needs you).

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

What is waiting on you and what is coming, season by season, over the
seasons already recorded.

## Needs You
<!-- help: section-attention -->

What in the saga is waiting on the storyguide, gathered from every part
of it. Nothing here is kept as a list: each part of the saga is asked
when the list is shown, so a row goes as soon as you deal with it.

- **Revisit**: an open story whose Revisit year has come (marked).
- **Open story**: every other open Story Event of the troupe's
  covenants, oldest first (see [Open Stories](help:section-region-stories)).
- **Describe**: a creation an experiment changed whose experimental
  effects you haven't described yet: a side effect or a special result
  with no words, or a modified effect that changes nothing the app works
  out. A spell is opened through a magus who knows it (its Mastery form
  holds its effects), an enchanted item's effect through its holder, a
  bond power through its familiar.
- **Overdue**: a dated stage of a threat still Pending after its season
  has passed (marked): record what became of it on the threat's Stages,
  or [Delay or Hasten](help:threat-delay) the threat.
- **Spotlight**: a player character with a Story Flaw or a Major
  Personality Flaw that no told (Resolved) story has concerned for the
  saga's **Story Flaw spotlight** span, 3 years unless changed in the
  saga's settings (0 turns it off). Such a Flaw is a promise of stories
  (DE p. 66): any story about the character counts, whichever Flaw it
  drew on. A character no told story has concerned yet is counted from
  the first season the saga recorded.
- **Teach?**: a student's open ask for another Player's character to
  teach them (see [Teaching Requests](help:teaching-requests)).
- **Close**: a chapter with a cast whose aftermath hasn't been asked;
  its Take Up step opens [Close the Chapter](help:close-chapter).
- **Away**: an open story about a character none of whose Players is
  coming to the next planned [Session](help:tab-content-sessions). It is
  only advice: keep the story for another evening, or play the
  character another way. A character everyone in the troupe plays is
  never named, and nothing shows until the Session says who is coming.

**You type:** nothing here. Choose a row to read what it needs and
where;
<!-- tui -->
Edit (`e`) opens the record it is dealt with on.
<!-- /tui -->
<!-- gui -->
**Open** goes to the record it is dealt with on.
<!-- /gui -->

**See also:** [How to clear what needs you](help:guide-needs-you)

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

More (`m`) > **Travel** (on the desktop, the **Travel** button) works out
a journey's days, cost and Fatigue, and can set the travellers out: see
[Travel](help:travel).

## Undertakings
<!-- help: section-undertakings; gui -->

Below Ahead on the Seasons page and on a covenant's Seasons chapter: what
the troupe sets out to do besides the seasons' plans, each button beside a
line saying what it does. [Travel](help:travel) works out a journey, and
The Hunt and Area Lore hunt and seek along the road. On a covenant,
**Begin Project** starts one of its great works of Hermetic Projects (see
[Hermetic Projects](help:tab-cov-projects)).

## Travel
<!-- help: travel -->

<!-- tui -->
On Ahead (the Seasons page's or a covenant's), More (`m`) > **Travel**
works out a journey.
<!-- /tui -->
<!-- gui -->
In Undertakings, below Ahead on the Seasons page and a covenant's Seasons
chapter, **Travel** works out a journey.
<!-- /gui -->
Choose **From** and **To** (the saga's covenants, towns and places),
then how the distance is **Measured**. When From and To are both on a
map of the saga's Atlas that has a scale (the Atlas is the desktop's),
choosing them fills in the **Miles**, as the crow flies, and sets
Measured to Direct distance: the divisors below then allow for the
winding way. Otherwise type the miles as measured on the troupe's map.
<!-- gui -->
See [Scale and distance](help:atlas-scale).
<!-- /gui -->

- **Direct distance, as the crow flies**, as you would measure it on a
  map: road travel takes the miles / 12 days, a barge / 8 with the
  current and / 6 against it, a ship / 60 (City & Guild p. 89, the river
  figures as the errata corrects them, p. 57). These already allow 20%
  for winding roads and rivers. A route that is mostly road or mostly
  river counts as all one; otherwise work out each leg on its own and add
  them. On foot or on your own horses the 20% is added to the miles first.
- **Route length, along the road or river**, at each way's miles a day
  (City & Guild p. 85): barges 8 to 10 (10 with the current, 8 against),
  carts 15 to 25, packhorses about 24, coaches 18 to 24, a courier about
  30, a rider with remounts up to 90. City & Guild gives no walking
  speed: on foot is the Definitive Edition's 20 miles a day (p. 408).
- **Between named ports**: the Naval Trade Tables (City & Guild
  pp. 89-90) give the days directly, through the junctions between
  Europe's regions, inland travel to the named city included.

Name **Who goes** (the saga's characters); **Travellers** counts them and
any others you add to it. Add the **Cargo, in tons**, tick **A known magus
travels** and, on land, **Travel quickly**.

**The Journey** shows the days, how they were worked out, City & Guild's
words for the way you travel and the Definitive Edition's figure as a
rough guide (p. 408: ships about 30 miles a day, good ones three or four
times that; a cart 20; a courier 30, 50 if urgent). Where the two books
differ the days are City & Guild's.

The cost is passage with a merchant or a captain (City & Guild
pp. 85-86): a pound a fortnight by sea for a party of eight in about a
ton of space with their food (half a ton hugging the coast), counted by
the day, with the cargo's own tons; river travel twice that, road travel
8 to 20 times. A known magus pays double aboard a ship or barge, if a
captain will take him at all (p. 85). On foot or on your own horses the
book has no figure: food, tools and lodging have no rate (p. 86).

Travelling quickly costs one Long-Term Fatigue level for each day on the
road (Definitive Edition p. 408); delays for terrain and weather still
cost it, waiting on toll collectors doesn't. A forced march of five days
leaves the travellers Unconscious. The app's reading: the nights of the
march restore nothing, and each night's rest without hurrying afterwards
restores one level (p. 404). A courier who hurries rides at the urgent
50 miles a day; a rider with remounts is always hurrying.

**Close** leaves it as a what-if: nothing is recorded. **Set Out** makes
the journey in one click: a Travel line in each traveller's Diary (from,
to, how, the days and the cost), the forced march's Long-Term Fatigue on
each of them if Travel quickly is ticked, and their arrival in the saga's
calendar, so it shows on Ahead (a season is taken as 13 weeks: a journey
of 91 days or more arrives a season later). Set Out needs someone named
in Who goes and a journey it can work out.

**The Hunt** and **Area Lore** sit beside Travel (on the desktop, in
Undertakings), for the road.
A hunt on the road first needs a hunting spot: the party's best
Intelligence + Area Lore against 6 (City & Guild p. 83). With no
huntsman named, the hunters quest and lay the relay themselves. Game
in a lord's chase, warren or forest is poached, and fiercely punished
(Lords of Men pp. 48-49). Otherwise both work as on a manor (see
Manors): Area Lore finds roads, fords, inns, hazards and people along
the route by the book's Ease Factors.

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
Every sourcebook as a card, with whether it is in play. The core book comes first, then the supplements under the book lines they belong to (The Order, with Houses of Hermes first and then The Order at Large; Realms of Power; Tribunals; Mythic Europe; The Lands Beyond; Non-Hermetic Magic; Scenarios; Transforming Mythic Europe), then the saga's own sources. A book line's books that the app doesn't have yet are left out until it does.

Each card says what its book brings: how many Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, spells, Shapes & Materials and Goods it adds to the catalogs, and how many optional rules, season activities, kinds of book and traditions; a saga source counts the saga's own entries that cite it. A book the app has nothing from yet says so. A book out of play is drawn faded.

Click a supplement's **In play** or **Not in play** chip to put it in play or take it out; the chapter's count changes with it and the saga is saved. The core book's **Always** chip can't be clicked: it is always in play. **Edit** opens the picker of books, to tick many at once. 
Click a card itself to see the book in the inspector.
<!-- /gui -->

A book's details give a short overview of it, how much it holds, and its special rules: its optional rules by name, and for a supplement its season activities, kinds of book and traditions. A saga source's give what it holds and what cites it.

While a book is out of play, everything it adds is switched off: the pickers leave out its Virtues, Flaws, spells and other entries; the season plan leaves out its activities (a plan already made keeps its activity); its optional rules are greyed out on Saga Settings (the terminal's Edit Saga leaves them off) and count as off (the choice is kept for when the book comes back); and the library's book form leaves out its kinds of books and their fields (a book already using one keeps it). The Library tab's research bonuses need Covenants.

### Saga Sources
<!-- help: section-saga-sources -->

<!-- tui -->
Sources of the saga's own, such as a house-rules list or a fan supplement, that its House Rules, spells, goods and Mystery Cults can cite, so that a whole set of homebrew goes in or out of play at once (see [How to keep homebrew in a source](help:guide-homebrew-source)). `a` adds one: an Abbreviation (short, like a book's, and not one a sourcebook already uses) and a Title. A new source starts in play, and it is put in or out of play with the books above.
<!-- /tui -->
<!-- gui -->
Sources of the saga's own, such as a house-rules list or a fan supplement, that its House Rules, spells, goods and Mystery Cults can cite, so that a whole set of homebrew goes in or out of play at once (see [How to keep homebrew in a source](help:guide-homebrew-source)). **Add** adds one: an Abbreviation (short, like a book's, and not one a sourcebook already uses) and a Title. A new source starts in play, and it is put in or out of play with the books above.
<!-- /gui -->

<!-- tui -->
`e` edits a source; a new abbreviation is carried to everything that cites it. `d` won't delete a source anything still cites (a House Rule, a spell, a good or a cult): the message names them. Its Entries column counts them all, and its card under Books in Play says what it brings.
<!-- /tui -->
<!-- gui -->
**Edit** edits the source last clicked; a new abbreviation is carried to everything that cites it. **Delete** won't delete a source anything still cites (a House Rule, a spell, a good or a cult): the message names them. Its Entries column counts them all, and its card under Books in Play says what it brings.
<!-- /gui -->

### Traditions Offered
<!-- help: section-traditions -->

The non-Hermetic magical traditions (Hedge Magic Revised Edition's six, and those of the Realms of Power, Societates, the Tribunal and regional books, Rival Magic and Ancient Magic), listed by book in the order of Books in Play, and whether the saga offers each. Every tradition of a book in play is offered until you turn it off, so a book put in play brings its traditions with it; turn off the ones your saga doesn't use. A tradition citing two books is listed under the first of them in play. A character can join a tradition the saga offers, which gives them [a chapter](help:tradition-chapter) for its Arts and Abilities.

<!-- tui -->
Each tradition's row says whether it is offered; one whose book is out of play is dimmed, marked "(book not in play)". `e` opens a tick for each tradition of the books in play: untick the ones the saga doesn't offer.
<!-- /tui -->
<!-- gui -->
The **Traditions** chapter has a heading for each book, saying whether the saga offers All, Some or None of its traditions, with a switch: flip it to offer them all, or, when all are offered, none. Under it each tradition is a card of two lines: its name and switch, then what kind of tradition it is. Flip the switch to offer that one or stop; click the card to see in the Inspector what it is and what it adds, with a switch at the top right. A book out of play has its cards greyed out and their switches off: put the book in play on Books in Play to offer them.
<!-- /gui -->

A tradition's kind is one of Hedge Tradition, Ex Miscellanea Tradition, Mystery Cult, Faerie Tradition, Holy Tradition, Infernal Tradition, Rival Tradition or Ancient Tradition. Its realm follows only when that is new information: a Holy Tradition is Divine and most others are Magic, so "Ancient Tradition · Faerie" names a realm and "Hedge Tradition" doesn't. A tradition whose magic can belong to several realms lists them: a sahir's Sihr is usually Magic, and a character's own version is chosen on their **Traditions** form (see [A tradition's chapter](help:tradition-chapter)).

Turning a tradition off, or taking its book out of play, stops it being offered; characters who already belong to it keep their chapter, and the choice is kept for when the book comes back. A saga from before traditions were offered by default offers every tradition of its books in play, as a new one does.

## Catalogs tab
<!-- help: tab-content-catalogs -->

The shared catalogs the pickers draw on, and what this saga leaves out of them.

**You type:** whether each catalog is offered, and the single entries to hide.

**The app works out:** each catalog's number of entries and of hidden ones.

### Catalogs
<!-- help: section-catalogs -->

<!-- tui -->
The Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, Spells, Shapes & Materials and Goods catalogs. `e` offers a whole catalog or not. A catalog not offered leaves its pickers with only the saga's own entries (its House Rules or own spells).
<!-- /tui -->
<!-- gui -->
The Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, Spells, Shapes & Materials and Goods catalogs. **Edit** offers a whole catalog or not. A catalog not offered leaves its pickers with only the saga's own entries (its House Rules or own spells).
<!-- /gui -->

### Hidden Entries
<!-- help: section-hidden-entries -->

<!-- tui -->
Single entries this saga's pickers leave out, as if their book were out of play. `a` asks which catalog, then which entry to hide; `d` offers the chosen one again, after a confirmation.
<!-- /tui -->
<!-- gui -->
Single entries this saga's pickers leave out, as if their book were out of play. **Add** asks which catalog, then which entry to hide; **Delete** offers the entry last clicked again, after a confirmation.
<!-- /gui -->

## Goods tab
<!-- help: tab-content-goods -->

What goods cost in Mythic Europe: every row of City & Guild's Prices of Goods table (pp. 141-142) and its Price List of common goods (p. 144), and any goods of the saga's own.

**You type:** goods of the saga's own, and purities of the goods priced by purity.

**The app works out:** a common good's price at each quality, a purity's price from its metal content, and what a gemstone or pearl costs an ounce.

### Goods
<!-- help: section-content-goods -->

The commodities come first, by class: bulk, manufactured and luxury goods (C&G p. 134). Their four prices, Shoddy, Standard, Superior and Expensive, are Mythic pounds a tun or ton, as the book prints them: `#` none to be had at that quality, `*` priced by purity, `250*` one purity's price, `n/a` as printed, and a blank where the book has none (Dye's Superior). There is no Excellent column. Goods the book doesn't sell by the ton are still priced by the ton for comparison; Sold by says how they are sold (wine by the tun, gemstones and pearls by the ounce, gold by the pound, silk by the roll, horses and slaves by the head).

The common goods follow, at their standard price each (C&G p. 144). Their details give the other qualities by the book's multipliers: Shoddy x0.5, Superior x2, Excellent x5, Wondrous x5 or more. The book means these prices for story flavour, not for merchants' or crafters' incomes (p. 143); selling finished items is a separate roll (Presence + Bargain, Chapter IV).

A good's details show its class and page, its prices, how it is sold, its purities, where it is bought in bulk (the commercial sources, pp. 138-140) and the book's note on it. The weights are 16 ounces to the pound and 2,240 pounds to the ton, as the errata corrects p. 140 (errata p. 57).

- **Silver** stays 2,420 a ton as printed: the table is built on it (gold's 24,200 is ten times silver, p. 141). Its 250*, 1,650* and 2,200* are prices at lesser purities: about 10%, 68% and 91% silver.
- **Priced by purity** (alum, copper, gold, iron, lead, saffron, salt, silver, tin): a lesser purity's price is the pure price times its metal content (p. 140). Alum's three prices are its three kinds instead, salt-adulterated, European and Asian, with no Expensive (p. 134).
- **Gemstones and pearls** show their price an ounce by column: the table's price over the 2,420-pound ton it is built on, which matches the book's 2 and 2 1/2 pounds an ounce for average and fine gems; pearls are 2 an ounce from rivers, 3 from the sea (p. 141).

<!-- tui -->
`a` adds a good of the saga's own: a commodity, priced a tun or ton by quality (its class, how it is sold, its four prices and, if it is priced by purity, its pure price), or a common good, priced each in pence (12 to the shilling, 240 to the pound, p. 143), with where it is bought and a description. `e` edits one of the saga's own goods; a catalog good is read-only. `d` deletes one of the saga's own goods, or hides a catalog good after a confirmation: the Catalogs tab's Hidden Entries offers it again, and Catalogs can switch the whole Goods catalog off. More's **Add a Purity** (`m`, then `p`, for a good priced by purity) adds a purity by its name and metal content, its price worked out as you type, and removes one the saga added.
<!-- /tui -->
<!-- gui -->
**Add** adds a good of the saga's own: a commodity, priced a tun or ton by quality (its class, how it is sold, its four prices and, if it is priced by purity, its pure price), or a common good, priced each in pence (12 to the shilling, 240 to the pound, p. 143), with where it is bought and a description. **Edit** edits one of the saga's own goods; a catalog good is read-only. **Hide** deletes one of the saga's own goods, or hides a catalog good after a confirmation: the Catalogs chapter's Hidden Entries offers it again, and Catalogs can switch the whole Goods catalog off. **Add a Purity** (for a good priced by purity) adds a purity by its name and metal content, its price worked out as you type, and removes one the saga added.
<!-- /gui -->

A good of the saga's own can cite one of the saga's sources (its **Source**, once the saga has one): while that source is out of play the good is marked "(not in play)".

## House Rules tab
<!-- help: tab-content-house-rules -->

The Virtues, Flaws, Boons and Hooks made for this saga, and its own Abilities: house rules, or entries from books the app's catalogs don't carry. They show in the pickers alongside the catalog's entries.

<!-- tui -->
**You type:** with `a` and `e`: what the entry is For (a Character Virtue or Flaw, a Laboratory Virtue or Flaw, a Covenant Boon or Hook, or an Ability; this is fixed once the entry is made), its Name, Type, Tier, Category, whether it can be taken more than once, what it Asks for, a Description and, once the saga has sources of its own, the Source it comes from.
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**: what the entry is For (a Character Virtue or Flaw, a Laboratory Virtue or Flaw, a Covenant Boon or Hook, or an Ability; this is fixed once the entry is made), its Name, Type, Tier, Category, whether it can be taken more than once, what it Asks for, a Description and, once the saga has sources of its own, the Source it comes from.
<!-- /gui -->

**Asks for** (a character's or covenant's entry only) lists what is chosen when the entry is taken, comma-separated, as the books' Puissant asks for an Ability: "Form" for a Vis Source Boon, say. Characteristic, Ability, Art, Technique, Form, Realm and Blood are chosen from a list; anything else is typed. Put a choice in the name in braces, "Vis Source ({form})", to have it shown there ("Vis Source (Aquam)"); otherwise it follows the name in brackets. What was chosen can be changed later with Edit on the Virtue, Flaw, Boon or Hook.

**An Ability** is one the saga adds beside the catalog's, most often a Supernatural Ability designed for a tradition of House Ex Miscellanea or a storyguide's character (Houses of Hermes: Societates pp. 103-106). You give its Name, Category (Supernatural unless you choose another), and for a Supernatural one its Realm (Magic, unless it belongs to another realm), the Characteristic it Rolls with (left blank, the storyguide chooses each time), whether it is Accelerated (on the Art table, for Ease Factors like Mights or spell levels; Puissant gives it +2 and it isn't studied from vis, Societates p. 104; Errata p. 60 adds that it isn't limited at creation), a Description, and, when adding, whether to Add its Virtue. A designed Ability is a Major Supernatural Virtue's (p. 104), and a Virtue of the Ability's name grants it, so Add its Virtue also makes that Supernatural Virtue among the saga's own (not when a Virtue of that name is already offered). **Its Virtue is** Major unless you choose Minor: the Definitive Edition has Minor Virtues that grant an Ability too, such as Second Sight (DE p. 106). Write in the Description what it does: by the book, three of its Range, Duration, Target and base effect are fixed, and the fourth grows with its score, or with the Ease Factor reached when it affects other beings.

**The app works out** for an Ability: its Casting Total (Characteristic + Ability + aura + die, against the storyguide's Ease Factor), its Penetration (Casting Total - Ease Factor + Penetration bonus), its level as a spell (5 x its score, or its Casting Total when Accelerated) and its vis limit (up to its score in pawns, +1 and a botch die each), all Houses of Hermes: Societates p. 104; and who holds it. Renaming an Ability renames it on every character, familiar and creature holding it, and renames its Virtue.

**The app works out** for a Virtue, Flaw, Boon or Hook: the points from its type and tier (Free 0, Minor 1, Major 3; Flaws and Hooks give points rather than cost them), and, in its details, who holds the entry. An entry citing one of the saga's sources is offered only while that source is in play; one citing none always is.

### House Rules
<!-- help: section-house-rules -->

<!-- tui -->
The list of the saga's own entries, with the details panel below it. Once the saga has a source of its own, More's **Move to Source** (`m`, then `s`) makes several entries cite one source, or none, at once: choose the source, then tick the entries (each listed with the source it cites now).
<!-- /tui -->
<!-- gui -->
The list of the saga's own entries; the Inspector shows the one last clicked in full. Once the saga has a source of its own, **Move to Source** makes several entries cite one source, or none, at once: choose the source, then tick the entries (each listed with the source it cites now).
<!-- /gui -->

### What house rules don't do
<!-- help: house-rules-limits -->

House rules are text only: the rules engine applies no effects for them. Two entries of the same kind can't share a name, type and tier. Delete won't delete an entry that a character, laboratory or covenant still holds; the message names them, so remove it there first.

An Ability has no type, tier or points, and two Abilities (the catalog's or the saga's) can't share a name. Delete won't delete an Ability someone holds; deleting one leaves its Virtue, which is deleted on its own. Whether an Ability is Accelerated can't change while someone holds it, since their score would change with it. On the desktop, its mark is its category's.

When a character, laboratory or covenant is exported, the house rules and saga Abilities it uses go with it.

**See also:** [Import Data](help:import-data), [How to import and export](help:guide-import-export)

## Mystery Cults tab
<!-- help: tab-content-cults -->

The saga's own Mystery Cults, as The Mysteries Revised Edition pp. 18-19 has the troupe invent one. Each cult has its own Lore and its degrees. Each degree teaches one Mystery Virtue, and its Initiation Script is written out as its components. The Initiation season offers the cults' Scripts beside the catalog's cults, under Hedge Script.

**You type:** the cult (its name, its Lore, its realm, the Characteristic its Initiations add, who may join, its founder and the year, what it is), its degrees and their Virtues, and each degree's Script.

**The app works out:** who belongs to the cult, each degree's Target, a Script's bonus from its components, a Mystagogue's Initiation Total against it, and an experiment for a degree with no Script, or with one that falls short.

**See also:** [House Rules tab](help:tab-content-house-rules), [How to initiate a character into a Mystery](help:guide-initiation)

### The Saga's Mystery Cults
<!-- help: section-content-cults -->

Each cult the saga has invented: its Lore, realm, founder and how many degrees it has. The storyguide creates the cult's Lore, and its founders may start with it at 0 (TMRE pp. 18-19). A Lore written as "Mystery Cult Lore: (cult)" is the catalog's own Ability. Any other name becomes a new Ability the saga adds, which characters can take like any other. Renaming the Lore renames it on every character who has it. Deleting a cult leaves its members their Lore and Virtues, and the Initiation season no longer offers its Scripts.

<!-- tui -->
`a` adds a cult, `e` edits the chosen one and `d` deletes it after asking. Choosing a cult shows its degrees and Scripts below.
<!-- /tui -->

Once the saga has a source of its own, a cult can cite one (its **Source**): while that source is out of play, no Initiation season can follow the cult's Scripts. Its members keep their Lore and Virtues.

### The chosen cult
<!-- help: section-content-cult -->

The cult's Lore, realm and founding. Initiation is the Mystagogue's Presence (or the Characteristic the cult chose) + the Lore + the Script's bonus, with no die. A probationer needs the Lore at 1 before his first Initiation, and the season holds every Initiate to that. The second and later Initiations typically need 3 (TMRE pp. 11, 13; DE p. 387): counted by the Initiations he has taken (the cult's Virtues he holds), not by the degree, so a cult whose path may start anywhere is not held to it. The season only warns when he falls short, and the troupe may go ahead. Members are worked out, not listed: one joins by gaining the cult's Lore, so a member is everyone who has it, at any score, and the founder, who may have it at 0 (TMRE pp. 11, 13, 19). One of its Virtues alone doesn't make a member, since most can be taken at creation. Each member is shown at the highest degree whose Virtue he holds. Someone with only the Lore is a probationer. If anyone may join, an unGifted Initiate needs an Ordeal in every Initiation, and his past Ordeals don't lower its Target (Hedge Magic Revised Edition p. 14).

**As a secret society.** A cult is a faction in the Order's politics too, as a Tribunal's factions are. On Add or Edit, **As a secret society: what it works for** gives its agenda, and **Its attitude toward** each of the troupe's covenants, from Hostile (-3) to Allied (+3), how it stands with them; the chosen cult's details show both. At a Tribunal meeting, a covenant with a member among its magi leans with its cult before the debate: with a covenant sharing the cult that brings the case or answers it, else by the cult's attitude toward a troupe covenant that does (Warm or better with it, Wary or worse against it). The Rhine's gilds lean first, then the cult. That the members vote as one is the app's reading, not a rule; the vote's leanings can be changed as ever.

### Degrees
<!-- help: section-content-cult-degrees -->

Each degree's name, the Mystery Virtue it teaches, its Script's bonus and its Target. Almost any Virtue may be Initiated, save those of birth or circumstance (TMRE p. 13). The saga's own Virtues are offered too. A Virtue that names something (an Art, an Ability) names it on the degree. The Target is 15 for a Minor Virtue and 21 for a Major one when a Mystagogue has the Virtue, and 18 and 30 when no one in the cult does (DE pp. 387-388). An Ordeal from an earlier Initiation lowers the next three Targets by 3/2/1, 6/4/2 or 9/6/3, never below 9.

**Experiment on a Script** is the Mystagogue's to make, so it is on her own sheet: in the Deeds chapter under Mystery Cults (More on her record in the terminal). It is there while she leads a cult with a degree that has no Script yet, or whose Script can't reach the Target for one of the cult's Mystagogues (TMRE p. 18); with several such cults it asks which first. It asks for the Virtue, the Mystagogue (her, unless you choose another with the Lore at 1 or more), the Initiate (the Mystagogue herself, or someone else, which is harder), the bonus the proposed rite's components would give, the Flaw of its Ordeal, if it has one, and a risk of 0 to +3. It refuses a degree whose Script already reaches the Target for that Mystagogue and Initiate. Roll throws a stress die + the risk on the Extraordinary Results chart, then the validity roll: a simple die + risk + Intelligence + Lore against 9 + the bonus, or 15 + it on another Initiate. The rite's Ordeal Flaw is suffered whatever follows, even when the rite fails. A Disaster ends it: a second form asks for the Major Flaw the Mystagogue and the Initiate each gain. If the rite still stands, a second form asks for the storyguide's sympathy (-5 to +5) and what the chart's results become: each side effect, minor flaw or minor benefit a Personality Trait with its score ("Devoted to the cult +1"), each major flaw an extra Ordeal Flaw with no bonus, each major benefit a Virtue, and a modified effect the different Virtue it Initiates in place of the degree's own. The Initiation Total is then the Characteristic + Lore + bonus + sympathy + risk against the Target, which the Initiate's past Ordeals lower, never below 9 (TMRE p. 14). If it succeeds, the degree gets its Script (the rite as proposed with its Ordeal, the sympathy, the extra Ordeal Flaws, Virtues and Personality Traits, without the risk), replacing a Script that fell short, and the Initiate gains the Virtue (or the one Initiated instead), the extra Virtues, the Personality Traits and the Ordeal Flaws; the largest of these is kept as his Ordeal. The Initiate's season isn't planned for him. A failed rite's Quests and Ordeals can't count again (TMRE p. 19).

<!-- tui -->
`a` adds a degree, `e` edits the chosen one and `d` deletes it (and its Script) after asking.
<!-- /tui -->

### The Script
<!-- help: section-content-cult-scripts -->

The chosen degree's Script, as its components with each one's bonus (TMRE pp. 15-16; DE p. 388): a special place at a special time +3 (once), a Quest +3 (+6 for a unique one), a Minor Ordeal +3, a Medium +6, a Major +9 (each with its Flaw), a Minor Virtue the Major one replaces +3, a sacrifice of goods +1 (once), a season serving the cult +1 (once), something of great value +3 to +6, the Mystagogue's time +3, and the rite's sympathy -5 to +5. The Script's bonus is their sum. A component that costs the Initiate nothing makes the whole Script void (TMRE p. 16).

**Edit Script** sets how many of each kind of component the Script has. It keeps the words of the ones it keeps. Its Ordeal is the Script's first Ordeal (an experiment's extra Ordeal Flaws, which give no bonus, are kept as they are, and so are the Virtue it Initiates instead, its extra Virtues and its Personality Traits, shown in the degree's details), and **Mystagogue** picks someone to test the Script against: the Rite shows that person's Initiation Total and Target. The Mystagogue isn't saved. An experiment's rite stays as one lump until its components are written out; then set it to 0.

<!-- tui -->
On a degree with no Script, `a` writes one. Otherwise `a` adds a component (its kind, its bonus when the troupe sizes it, its Flaw for an Ordeal, and what it is), `e` edits the whole Script, and `d` removes the chosen component after asking.
<!-- /tui -->

## Spells tab
<!-- help: tab-content-spells -->

Every spell the saga knows: the catalog's spells from the books in play, and the saga's own. Spells from books out of play, or hidden on the Catalogs tab, are left out until the Source filter asks for them, and so is a spell of the saga's own whose Source (one of the saga's own sources, chosen in its form once the saga has one) is out of play; they are marked "(not in play)", and a magus who already knows one keeps it, marked the same way on their Known Spells.
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

## Sessions
<!-- help: tab-content-sessions -->

The evenings of play at the table: planned ones first, the soonest at the top (those with no date yet after the dated ones), then the ones played, newest first. A Session need not sit in one season: a slow saga plays several in one season, a fast one a year or more in one (DE p. 528).

<!-- tui -->
In Saga Content's Sessions tab. Everyone can read them; only a storyguide adds, changes or deletes them.
<!-- /tui -->
<!-- gui -->
In the saga page's **Saga Management** chapter, the storyguide's; players see the next Session and the recent ones on The Troupe.
<!-- /gui -->

<!-- tui -->
**You type:** with `a` and `e`, in two steps. First the real Date (year-month-day, or blank), whether it was Played, the Game season and year it is set in (both optional), its Storyguide (any Player; blank is the saga's own) and, for each Player, whether they are Coming or Away. Then **Who Played Whom**: for each character, the Player playing them that evening, or no one. `d` deletes a Session after a confirmation.
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**, in two steps. First the real Date (year-month-day, or blank), whether it was Played, the Game season and year it is set in (both optional), its Storyguide (any Player; blank is the saga's own) and, for each Player, whether they are Coming or Away. Then **Who Played Whom**: for each character, the Player playing them that evening, or no one. **Delete** deletes a Session after a confirmation.
<!-- /gui -->

A character is played by one person at most each evening, though it may have several Players and a Player may play several characters. Who Played Whom comes filled in from who usually plays whom: a character goes to its Player when exactly one of its Players is coming, and is left for you to choose when two or more are (a shared character, or one everyone plays). The characters of the Players coming are listed first.

In a solo saga (no one in the Player role) no attendance or Who Played Whom is asked. A Session made then shows **Attendance not recorded** if the saga gains players later.

Marking a Session **Played** keeps a copy of each player character as they stand, so a character's More offers **What Changed Since the Last Session**: their scores, spells, Virtues and Flaws, Warping, wounds, Confidence, traits and what they hold, then and now. The latest two played Sessions keep their copies; untick Played to drop one.

**The app works out:** which Session is next; the names as written, so a played Session still reads right after a Player or character is deleted (deleting one takes them out of the planned Sessions only); and, on [Needs You](help:section-attention), an open story about a character none of whose Players is coming.

**See also:** [How to plan and record a Session](help:guide-sessions), [Players](help:tab-content-players)

### Previously On
<!-- help: previously-on -->

A page to read aloud before the next Session: what happened since the
last one. Its chapters (with who went), the seasons played since, what
the world did each year (The World Turns), the threats' stages that came,
were stopped or turned, and each player character's What changed. It runs
from the saga's date when the last Session was marked Played; with no
played Session, over the last four seasons.

<!-- tui -->
More on the saga, **Previously On**.
<!-- /tui -->
<!-- gui -->
**Previously On** in the saga page's Seasons chapter, or on Saga
Management's Sessions; **Print Previously On** there makes a PDF in the
Scriptorum style, read as the Player view.
<!-- /gui -->

Players see it too, as the [Player view](help:player-view): without what
the world did (its lines name neighbours they may not know of), unknown
threats, or non-player characters' seasons. A storyguide sees all of it;
switch to the Player view to read it aloud safely.

**See also:** [Sessions](help:tab-content-sessions)

### Cast at a Glance
<!-- help: cast-glance -->

One page of the figures the storyguide reaches for during play, for each
character playing at a Session (who played whom): Initiative, Attack and
Defence with their first weapon (bare hands if none), Soak, Magic
Resistance (a magus with Parma Magica, against his weakest Form), Wounds,
Fatigue and Confidence (score and points), then their Personality Traits
and chosen spells: those with a Mastery score, and those ticked
**Favourite** in their Known Spells' Mastery form.

<!-- tui -->
Choose a Session in the Sessions list and press `m` for More, then
**Cast at a Glance**.
<!-- /tui -->
<!-- gui -->
Choose a Session in Saga Management's Sessions and click **Cast at a
Glance**, or **Print the Cast** for a PDF in the Scriptorum style (the
paper first, then where to save it).
<!-- /gui -->

**See also:** [Sessions](help:tab-content-sessions)

### The Sessions list
<!-- help: section-sessions -->

<!-- tui -->
The list of Sessions, with the details panel below it: when, its game date, storyguide, who is coming and who is Away, and who played whom.
<!-- /tui -->
<!-- gui -->
The list of Sessions; the Inspector shows the one last clicked: when, its game date, storyguide, who is coming and who is Away, and who played whom.
<!-- /gui -->

## Players tab
<!-- help: tab-content-players -->

Who can sign in to this saga when you host it, so that players open it in a web browser from their own computers. Each player signs in with their name and the passcode you give them. Your own window, the app run on your computer, never asks.
<!-- gui -->

On the desktop the Players are in the saga page's **Saga Management**, beside **Host for Players** (see [How to host a saga](help:guide-hosting)) and the Sessions; the players you add there are the ones it lets in. To join from their own copy of Armarius over the internet (a Remote seat), a player's passcode needs at least 14 characters, set there; the list says whether each can (**✓ Ready**, or why not), and **Issue Invite** on the chosen player opens Host for Players with their Invite (see [Issue Invite](help:issue-invite)).
<!-- /gui -->

Only the storyguide sees it: your own window, or someone signed in with the Storyguide role (not a storyguide joined from a Remote seat: who may join is the host's).

Players stay in this saga: no export or pack carries them, nor which player plays a character (a character keeps the Player named on its sheet).

<!-- tui -->
**You type:** with `a` and `e`: the player's Name (what they type to sign in; no two players may share one), their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. When editing, leave New passcode blank to keep the one they have. `d` deletes a player after a confirmation; they can no longer sign in.
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**: the player's Name (what they type to sign in; no two players may share one), their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. When editing, leave New passcode blank to keep the one they have. **Delete** deletes a player after a confirmation; they can no longer sign in.
<!-- /gui -->

Leave the Passcode blank when adding someone who only sits at the table: a **table-only Player**, named on Sessions and as a Steward but never able to sign in. Give them a passcode later, by editing them, if they are to join from their own computer.

**The app works out:** in their details, the characters each plays, the characters each stewards, and what they may change. Passcodes are stored only scrambled (a salted hash), so the app can check one but no one can read it back from the saga file: if a player forgets theirs, give them a new one.

### Players
<!-- help: section-players -->

<!-- tui -->
The list of players, with the details panel below it.
<!-- /tui -->
<!-- gui -->
The list of players, in Saga Management, with whether each can sign in from a Remote seat; the Inspector shows the one last clicked. **Issue Invite** invites the chosen player.
<!-- /gui -->

### What a signed-in player can do
<!-- help: players-access -->

Choose who plays a character in the character's Biographical Detail (only the storyguide can): tick **Played by** each player who plays them (several, in troupe-style play), or **Played by everyone in the troupe** for a character the troupe shares, such as a grog. Any of a character's players may change it; if two change the same thing at once, the later save is kept and the other is told. A signed-in player can then:

- change the characters they play, with those characters' familiars, laboratories and books, and their season plans;
- plan the seasons of the characters they are **Steward** of, and change nothing else on those sheets. A Steward is chosen in the Biographical Detail of a character no Player is named on (a pooled grog, even one everyone in the troupe plays): they keep it between Sessions and decide its downtime;
- change the covenants too, if you ticked May change covenants for them;
- look at everything else but each record's [Secrets](help:tab-secrets), which they never see, and the records they don't know of (see [Player view](help:player-view)), and Export a character, laboratory or covenant (the file downloads in their browser, without its secrets or the records they don't know of).

Only the storyguide (your own window, or someone signed in as Storyguide) can make new records (New), advance or set the season, import, give things between records, share spells, or change the saga itself, its content and its players. Keys a player can't use there don't appear, and if a change slips through anyway, the app doesn't save it and says so.

<!-- gui -->
**On the desktop** a player's window opens on **Your Characters**, then the troupe's other characters, the troupe's covenants and the rest of what the players know. Their own characters show every button; any other record is read only, with no Add, Edit or Delete, and Advance Season and Player view are not there. To see it as a player does, click the **Play as** icon (two people) in the title bar, which appears once the saga has players, and pick a player; it then reads "Playing as" and their name. Pick **Storyguide** from it to come back.
<!-- /gui -->

**See also:** [Signing in](help:sign-in), [How to host a saga](help:guide-hosting), [The saga](help:saga)

# A record's Secrets
<!-- help: tab-secrets -->

What only the storyguide should know about a record: the covenant's
hidden debt, the magus's true master, where a missing founder really
went. Every covenant, character, Tribunal, neighbour and creature keeps
a list of them, apart from its summary and notes so those can be read
aloud or shown to the players as they are. Each secret is a short title
and its words, and says whether it has been revealed, and when.
<!-- tui -->
It is the record's last tab, **Secrets**.
<!-- /tui -->
<!-- gui -->
It is the record's last chapter before Manage, **Secrets**.
<!-- /gui -->

You see every secret, each marked "Not revealed" or "Revealed" with the
season and year. A player signed in to a hosted copy, and your own
window in [Player view](help:player-view), see only those revealed, in
the record's **Known** section instead; with none revealed the tab isn't
there for them. A record a player exports carries only its revealed
secrets. Your Find searches every secret, theirs none.

The content packs that come with the app, and the Dammërstein saga
starter, give each secret a title, each one thing the players could
learn on its own. A record's table notes (auras, rolls, where a stat
block is, the rules' names for a trait) are its last secret,
**Storyguide Notes**, which is for you and not meant to be revealed.

Older sagas and content packs kept a record's secrets as one piece of
writing (some at the end of a summary or notes under a **Secrets**
heading). Opening the saga makes that one untitled secret; **Split by
Paragraph** breaks it up. A pack exported from such a saga brings its
secrets the same way.

**See also:** [How to reveal a record to the players](help:guide-reveal), [What a signed-in player can do](help:players-access), [How to host a saga](help:guide-hosting)

### Secrets
<!-- help: section-secrets -->

The list of the record's secrets, each with its title (or, untitled,
its first words) and whether it is revealed; every secret is written in
full below the list.

<!-- tui -->
`a` adds a secret, `e` edits the one chosen and `d` deletes it after
asking. More (`m`) on a chosen secret offers **Reveal the Secret** (or
**Hide the Secret Again** once revealed) and, for a secret of several
paragraphs, **Split by Paragraph**.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the secret chosen, as do
**Reveal** (or **Hide Again** once revealed) and, for a secret of
several paragraphs, **Split**.
<!-- /gui -->

- **Reveal** marks it revealed this season and writes a dated line,
  "Revealed: the record: the secret", in each troupe covenant's Diary;
  the players see it in Known from then on. On a record the players
  don't know of yet, it shows once the record is revealed too. **Hide
  Again** takes it back, and its Diary line.
- **Split by Paragraph** shows the parts first, then makes one secret of
  each paragraph, each revealed as the whole was; the first keeps the
  title.

**You type:** a **Title** (a few words, optional) and the **Secret**
itself, as many paragraphs as you like. It supports **bold** and
*italic*.

### Known
<!-- help: known-secrets -->

What the players have been told of the record's secrets: each one the
storyguide revealed, with its title and the season it was revealed in.
It is what a player, or the storyguide's window in
[Player view](help:player-view), sees in place of Secrets.

# Player view
<!-- help: player-view -->

What the players may read, and the storyguide's own window shown as they
see it. Every page, list, search and export asks the same question, so a
player sees the same saga wherever they look.

<!-- tui -->
**Player View**, in More (`m`) on the saga at the top of the tree, turns
it on or off. While it is on, the header says "Player view".
<!-- /tui -->
<!-- gui -->
The **eye** in the title bar, beside Find, turns it on or off; while it
is on, the words "Player view" stand beside it. Use it on a screen your
players can see across the table.
<!-- /gui -->

The app remembers it for each saga on this computer. A player signed in
to a hosted copy always sees the saga this way. In a solo saga, with
nobody signing in, Player view is your guard against spoilers: it is off
until you turn it on.

- **Known to the players.** Every record of the world beyond the troupe
  (a neighbour or place, a creature, a covenant the troupe doesn't play,
  a character no player plays) is either known to the players or not.
  One they don't know of is left out of every list, of Find, of the
  Atlas and of Looking Ahead; a page that names it shows neither its
  name nor a link, and a line that names nothing else is left out. The
  troupe's own characters, covenants and laboratories are always known.
- **Reveal to the Players** tells them of a record: a dated line saying
  so goes in each troupe covenant's Diary. **Hide from the Players**
  takes it back, and takes that line out. Both are on the record's own
  page (More in the terminal, Manage on the desktop). Hide from the
  Players on the Region hides a whole list at once (see
  [Hide many records](help:mark-unknown)).
<!-- tui -->
- **The mark** after a record's name, at the top of its sheet, shows
  which it is: 👁 while the players know of it, 🚫 while it is hidden
  from them. The troupe's own records have none, and Player view shows
  none.
<!-- /tui -->
<!-- gui -->
- **The seal** under a record's bookmark ribbon shows which it is: an
  eye in a ring, struck through and inked red while the record is
  hidden from the players, plain once it is known. Hover over it to read
  Hidden or Known; click it to reveal or hide the record. The troupe's
  own records have none, and Player view shows none.
<!-- /gui -->
- **The storyguide's alone:** each record's [Secrets](help:tab-secrets),
  a place's or lord's [Roll Tables](help:tab-nb-tables), Needs You, Saga
  Management, Saga Settings and the Players list of Saga Content. The
  books in play, catalogs, House Rules and spells stay on show.
- **Threats:** a threat's stages show only once they have come or been
  marked; never its clock, its position or what is still to come.
- **Looking Ahead** shows only the dates anyone could know: Tribunal
  meetings and terms, fairs, aging rolls and your own calendar entries,
  never a threat's stage, a place's trigger or the world's yearly turn.
- **The Diary:** a line the app wrote about a record the players don't
  know of (a threat's stage, a roll on a place's table) is left out
  until it is revealed; lines you typed always show.
- **Exports** made in Player view, or by a player, leave out Secrets and
  the records the players don't know of. Yours otherwise are whole.
- **Actions** only the storyguide takes are left off while Player view is
  on: Roll on a table, Reveal and Hide, hosting, Import, Export Pack,
  Edit Saga, and beginning, growing, delaying or taking up a threat's
  story.

Sagas from before keep every record known; a pack brings its records
known, except any it marks secret.

**With a second storyguide** (a Player whose role is Storyguide), Player
view becomes **Playing**, and every storyguide's window opens in it,
yours too: your characters as a player sees them.
<!-- tui -->
Player View in More switches to your storyguide role and back.
<!-- /tui -->
<!-- gui -->
The eye then reads **Playing** or **Storyguide**; click it to switch.
<!-- /gui -->
Each switch is written in the host's Remote seats log. In your
storyguide role you read your own stories and those with no storyguide
whole; another storyguide's you read as a player would (see
[A storyguide for each story](help:assign-storyguide)).

**See also:** [How to reveal a record to the players](help:guide-reveal), [What a signed-in player can do](help:players-access), [A record's Secrets](help:tab-secrets), [How to run a saga with several storyguides](help:guide-troupe-storyguides)

# A storyguide for each story
<!-- help: assign-storyguide -->

In troupe-style play several of you take turns as storyguide, each
running their own stories (DE pp. 529-530, the alpha and beta
storyguides). Once the saga has a second storyguide (a Player whose role
is **Storyguide**), any record that keeps Secrets (a character, covenant,
place, lord, faction, threat, creature or Tribunal) can have its own
storyguide: you (the host) or one of them. A covenant's open story
events are its storyguide's; a laboratory or familiar is its
character's.

- **Its storyguide** reads it whole: its Secrets, Roll Tables, a
  threat's stages still to come and its clock.
- **Any other storyguide, the host included,** reads it as a player
  would, and can't change it. There is no storyguide who reads
  everything. Find, Looking Ahead, Needs You, the Atlas and exports
  follow the same rule.
- **No storyguide:** every storyguide reads it whole, as before.

<!-- tui -->
**Its Storyguide**, in More (`m`) on the record,
<!-- /tui -->
<!-- gui -->
**Its Storyguide**, in the record's Manage chapter,
<!-- /gui -->
sets it. Any storyguide takes a record with none for themselves; only
its own storyguide releases it (blank) or hands it on to another. Nobody
takes someone else's, so nobody can read another's Secrets by taking
them. The record's Connections (or its facts) say whose it is.

Deleting a storyguide, or making them a player again, leaves their
records with no storyguide, so every storyguide then reads their
Secrets; you are asked first, with the records named.

**What it is not:** a lock. The host's saga file holds everything, and
Armarius keeps the rule on screen and in what it sends. It keeps friends
from spoiling each other's stories; it doesn't stop someone who opens the
file.

**From a Remote seat**, while another storyguide runs some of the saga's
stories, Advance Season is left to the host's computer, which holds
every record whole; a seat holds another's records only as the players
have them.

**See also:** [Player view](help:player-view), [How to run a saga with several storyguides](help:guide-troupe-storyguides), [What a signed-in player can do](help:players-access)

### Hide many records
<!-- help: mark-unknown -->

Hide from the Players on the saga
<!-- tui -->
or the Region (More, `m`)
<!-- /tui -->
<!-- gui -->
page's The Region chapter
<!-- /gui -->
hides a whole list at once: a pack's every place, say, before the troupe
has travelled.

**You type:** **Which** list (Lords and Towns, the Church, Universities,
Factions, Threats, Places, Customs and Lore, Other covenants,
Non-player characters or the Bestiary), and **In the lands of** to take
only those in one Tribunal's lands (blank: wherever they are).

**The app works out:** how many records the players know of now would be
hidden, shown as you choose. Nothing is deleted; reveal each one as the
troupe learns of it.

# Saga Management
<!-- help: saga-management; gui -->

A chapter of the saga's page: Import, Export Saga, Export a Cult, Export
Pack and Host for Players, each with a line on what it does; then the
[Players](help:section-players) and the [Sessions](help:section-sessions).
Host for Players opens the [Host for Players](help:host-for-players-window)
window, where you host the saga and manage Remote seats; while the saga is
hosted, its line says how. It is the storyguide's alone: [Player view](help:player-view)
leaves it out, and a storyguide joined from a Remote seat sees no Players
(who may join is the host's).

**See also:** [Import Data](help:import-data), [How to host a saga](help:guide-hosting), [Host for Players](help:host-for-players-window)

# Signing in
<!-- help: sign-in -->

When the storyguide hosts the app, opening a saga in a browser (or over SSH) first asks who you are: type your Name and the Passcode the storyguide gave you, then Sign in. Name is not case-sensitive; the passcode is.

If the saga has no players yet, it can't be opened from a browser: the storyguide adds them on the [Players](help:tab-content-players) (Saga Content's Players tab in the terminal, the saga page's Saga Management on the desktop). Your name is shown in the header beside the saga's date while you're signed in. Going back to the saga list (Escape) signs you out.

While several people have the saga open, each one's saves keep everyone else's changes, and within a few seconds the others' screens show them: the sheet on show updates where it is (with a note such as "Ana changed Corvinus; reloaded"), and if two people open the same character, both are told ("Ana is also on Corvinus"; on the desktop, "◉ Ana is here too" beside the trail, for as long as she is), whether they're in a browser, the storyguide's own desktop or a Remote seat. If the record you have open is deleted elsewhere, the saga is shown instead.

**See also:** [Players](help:tab-content-players), [How to host a saga](help:guide-hosting), [Saga picker](help:saga-picker)
