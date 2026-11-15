# How to download and run the app
<!-- help: guide-download -->

You want Armarius on a new computer, or a friend at the table wants to try it. You don't need Python: each Release on the app's GitHub page, under **Releases**, has a download for Windows and one for Linux.

Each is a zip named like `Armarius-X.Y.Z-windows.zip`, where X.Y.Z is the version. It holds the whole app, with its books' catalogs, the Tribunal packs and the tutorials. Your sagas are never inside it. They're kept in your [save folder](help:saga-picker), so a newer download finds them.

### Windows
<!-- help: guide-download-windows -->

1. **Unzip it.** Download the Windows zip, right-click it and choose **Extract All**. Put the folder it makes, `Armarius-X.Y.Z`, wherever you keep programs, such as your Documents.
2. **Start it.** Open the folder and double-click **Armarius** for the desktop app. **armarius-terminal**, in the same folder, starts the terminal version.
3. **Let Windows run it.** The first time, Windows may say "Windows protected your PC", because the app isn't signed with a paid certificate. Click **More info**, then **Run anyway**. It asks only once for each version.
4. **Pin it.** Right-click **Armarius** and choose **Pin to Start**, or **Send to**, then **Desktop (create shortcut)**.

### Linux
<!-- help: guide-download-linux -->

1. **Unzip it.** Download the Linux zip and run `unzip Armarius-X.Y.Z-linux.zip`.
2. **Start it.** Run `./Armarius-X.Y.Z/Armarius` for the desktop app, or `./Armarius-X.Y.Z/armarius-terminal` in a terminal for the terminal version.

It runs on Ubuntu 22.04 and other systems of that age or newer. The desktop app needs the usual desktop libraries. If it won't start, run it from a terminal to see which one is missing.

On GNOME the desktop app draws its windows through X11. If you'd rather use Wayland, start it with `QT_QPA_PLATFORM=wayland ./Armarius`.

### A newer version
<!-- help: guide-download-update -->

1. **Unzip the new one.** Download the newer zip and unzip it beside the old folder.
2. **Start the new one.** Your sagas and settings carry over, since they aren't in the app's folder.
3. **Delete the old folder** once the new one works.

An older version still opens a saga the newer one saved, but says so, and can't show what only the newer one knows. If your troupe shares a saga, move to the new version together.

### Hosting from a download
<!-- help: guide-download-hosting -->

Hosting works from a download just as it does from the source (see [How to host a saga for your troupe](help:guide-hosting)). The first time you host, Windows asks whether to let **armarius-terminal** through the firewall, as it asks about Python when you run from the source. Allow it on **private** networks.

Players who join with Remote seats need the same major version of Armarius as you, the first number of the version (the 4 in 4.13.0).

**See also:** [Saga picker](help:saga-picker), [Getting started](help:guide-getting-started), [How to host a saga for your troupe](help:guide-hosting)

# Getting started
<!-- help: guide-getting-started -->

Your troupe is ready to begin a saga, and you want its books, its covenant, its characters and their laboratories in place before the first story. Here's the way from the start screen to a saga you can play, and how to find your way around once you're there.

### Create and open a saga
<!-- help: guide-getting-started-saga -->

<!-- tui -->
1. **Choose New Saga.** The app opens on its [title page](help:title-page). New Saga goes to the [saga picker](help:saga-picker), which lists the sagas saved on this computer ("No sagas yet" the first time), and opens its New Saga form. On the saga picker itself, `n` opens the same form.
2. **Fill in the form.** Create a New Saga asks for a Name and a Storyguide, both required, a Start Year and Start Season, and an optional one-line Description. Choose Create.
3. **Open it.** The new saga appears in the list. Highlight it with the arrow keys and press Enter to open it in the [workspace](help:workspace).
<!-- /tui -->
<!-- gui -->
1. **Choose New Saga.** The app opens on its [title page](help:title-page). New Saga goes to the [Sagas page](help:saga-picker), which shows the sagas saved on this computer as cards ("No sagas yet" the first time), and opens its New Saga form. On the Sagas page itself, **New Saga** above the cards opens the same form.
2. **Fill in the form.** Create a New Saga asks for a Name and a Storyguide, both required, a Start Year and Start Season, and an optional one-line Description. Choose Create.
3. **Start playing.** The new saga opens at once, on [its page](help:saga). Next time, click its card on the Sagas page, or choose **Open Saga** on the title page to go back to the saga you had open last.
<!-- /gui -->

To begin with a Tribunal and its covenants already written, choose a pack in **Start from a pack** on the New Saga form. It offers the sourcebooks' packs shipped with the app (see [How to start a saga from a sourcebook](help:guide-book-packs)), then the saga starters, ready-made covenants or sagas such as Dammërstein. It also lists any pack in your exports folder (see [Content packs](help:export-pack)). A pack imported into a saga that already exists can leave parts out, such as the mundane world or the history (see [Choosing what a pack imports](help:import-pack)).

The saga is saved in your [save folder](help:saga-picker) as soon as it's made, and every change after that is saved as you make it. There's no Save command to remember.

### Choose the books and optional rules
<!-- help: guide-getting-started-rules -->

<!-- tui -->
1. **Look at the saga.** The workspace opens with the navigation tree on the left. Its top node is [the saga](help:saga). With it chosen, the pane on the right shows the current date, the books in play and the optional rules.
2. **Choose the books.** Choose **Saga Content** in the tree, press Enter, and press `e` on Books in Play. Tick the books your troupe uses. Pickers then hide entries from books not in play, such as Virtues and spells, and whatever a supplement adds switches off with it. See [Saga Content](help:saga-content).
3. **Open the saga's settings.** Back on the saga node, press `e` (the footer calls it Edit Saga).
<!-- /tui -->
<!-- gui -->
1. **Find the chapters.** [The saga's page](help:saga) lists its chapters in the rail on the left, such as The Troupe, The Covenants, Seasons and Saga Settings.
2. **Choose the books.** In **Saga Settings**, click the **Saga Content** card under Content in Play. On its **Books** chapter, click **Edit** on Books in Play and tick the books your troupe uses, or click one card's **In play** chip to switch just that book. Pickers then hide entries from books not in play (see [Saga Content](help:saga-content)).
3. **Go back to the settings.** Click the saga's name in the trail to return to its page's **Saga Settings** chapter. A card's switch changes it at once, and clicking the card explains it in the Inspector.
<!-- /gui -->
4. **Turn on the optional rules you want.** Each is off until you turn it on, such as Simple dice only, Enforce creation rules strictly and Extended book Quality. A supplement's rules show only while its book is in play, and the line under each says what it does.
5. **Keep season records.** **Keep season records** keeps a record of each season under Seasons. Leave it on unless you only want the characters' Diaries to keep them.
6. **Choose the medallions.** **Medallion style** chooses how the desktop draws the seasons as medallions, on the band at the top of every page, the Seasons page, the calendars and a siege's page. Stained glass is the default, and the others include a wax seal and Limoges enamel.
7. **Say what an unplanned season gives.** **Magi / Companions / Grogs with nothing planned** set what a season left unplanned gives when it's advanced, Work / Exposure (the default) or Nothing. See [Unplanned seasons](help:advance-unplanned).
<!-- tui -->
8. **Name idle characters, if you like.** **Be notified when and which non-player characters do not have seasonal activity**, off by default, makes Advance Season name non-player characters with nothing planned too.
9. **Set the Story Flaw spotlight.** **Story Flaw spotlight (years)**, 3 by default and 0 for off, is how long a player character's Story or Major Personality Flaw may go without a told story before [Needs You](help:section-attention) names them.
10. **Save.** The saga's summary now lists your books and the optional rules turned on.
<!-- /tui -->
<!-- gui -->
8. **Name idle characters, if you like.** **Name Idle Non-Player Characters**, off by default, makes Advance Season name non-player characters with nothing planned too.
9. **Set the Story Flaw spotlight.** **Story Flaw Spotlight**, 3 years by default and 0 for off, is how long a player character's Story or Major Personality Flaw may go without a told story before [Needs You](help:section-attention) names them.
<!-- /gui -->

You can come back to these settings at any time.

### Make the first covenant
<!-- help: guide-getting-started-covenant -->

<!-- tui -->
1. **Choose New Covenant.** With the saga node chosen, press `n` (New). A menu offers New Covenant, New Character and New Laboratory. Press `v` for New Covenant.
<!-- /tui -->
<!-- gui -->
1. **Choose New Covenant.** On the saga's page, open **The Covenants** and click the **New Covenant** card at the end of the Covenants.
<!-- /gui -->
2. **Name it.** Type a Name and, if you like, a one-line note under Notes.
3. **Choose its Season and aura.** The Season, Spring unless you change it, sets what each inhabitant counts for. The Aura realm starts at Magic, since the creation rules assume a Magic aura, and a Faerie aura is a Hook. Choose Create. The covenant starts at the creation baseline's aura of 3.
<!-- tui -->
4. **Find it in the tree.** The covenant appears in the tree, marked "(creating)", with two groups under it, **Characters** and **Laboratories**. Its [covenant sheet](help:covenant) opens on the right.
5. **Build it by the book.** The covenant starts In Creation, and its Creation Worksheet opens. To build it step by step (Baseline, Resources, Boons & Hooks), see [How to create a character, covenant or laboratory](help:guide-creation).
6. **Or fill it in by hand.** Press Enter to move into the sheet, and use `e` on its top panel and `a` in its sections.
<!-- /tui -->
<!-- gui -->
4. **Build it by the book.** The covenant starts In Creation, so its Creation Worksheet opens. To build it step by step (Baseline, Resources, Boons & Hooks), see [How to create a character, covenant or laboratory](help:guide-creation).
5. **Or fill it in by hand.** Click the covenant's name in the trail. Its [page](help:covenant) is drawn on drafting vellum while it's In Creation. Use the **Edit** and **Add** buttons on its header and in its chapters.
<!-- /gui -->

### Add characters and laboratories
<!-- help: guide-getting-started-people -->

<!-- tui -->
1. **Choose New Character.** In the tree, choose the covenant or its Characters group and press `n`, then `c` for New Character. The new character starts in the covenant on show.
<!-- /tui -->
<!-- gui -->
1. **Choose the kind of character.** On the covenant's page, open its **People** chapter. Each group ends in a New card, **New Magus**, **New Companion** or **New Grog**. Click the one you want. The new character starts in the covenant on show.
<!-- /gui -->
2. **Fill in the form.** Give a Name, a Type and the Covenant, and a Template, or None to build the character step by step (see [New Character](help:character-group-new)).
<!-- tui -->
3. **Create.** Choose Create. The character's [sheet](help:character) opens, and their node appears under Characters.
4. **Add a laboratory.** Choose the covenant or its Laboratories group, press `n`, then `l` for New Laboratory. The form asks for a Name, a Size, the Covenant, and whether it's **One of the covenant's starting labs**, ticked for you while the covenant is In Creation. See [Laboratories group](help:laboratory-group).
<!-- /tui -->
<!-- gui -->
3. **Create.** Choose Create. A character built step by step opens on their Creation Worksheet, and one made from a template opens on their [sheet](help:character). Either way, their card joins the covenant's People.
4. **Add a laboratory.** Open the covenant's **Laboratories** chapter and click the **New Laboratory** card. The form asks for a Name, a Size, the Covenant, and whether it's **One of the covenant's starting labs**, ticked for you while the covenant is In Creation. See [Laboratories group](help:laboratory-group).
<!-- /gui -->

### Give a magus their laboratory
<!-- help: guide-getting-started-lab -->

A laboratory's owner is the magus whose lab work is planned on it and whose Lab Totals it shows. You can set it from either side, and the app keeps the two in step.

<!-- tui -->
1. **From the laboratory.** Choose it in the tree, press Enter, and with its top panel focused press `e`. Choose the magus as **Owner** in the [Identity](help:section-lab-identity) panel and save.
2. **Or from the magus.** On their sheet, with the top panel focused, press `e` and choose the **Assigned Laboratory** in [Character info](help:section-char-info).
<!-- /tui -->
<!-- gui -->
1. **From the laboratory.** Open its page and click **Edit** in its header. Choose the magus as **Owner** in the [Identity](help:section-lab-identity) form and save.
2. **Or from the magus.** On their sheet, click **Edit** in the header and choose the **Assigned Laboratory** in [Character info](help:section-char-info).
<!-- /gui -->

A laboratory has only one owner at a time. Giving a laboratory to a magus who already had one frees their old laboratory.

### Find your way around
<!-- help: guide-getting-started-moving -->

<!-- tui -->
1. **The tree.** The arrow keys move along it, and the sheet on the right follows. Enter moves focus into the sheet. Esc steps back out, from the sheet to the tree and from the tree to the saga picker. See [the navigation tree](help:workspace-tree).
2. **Sections.** A sheet is made of sections. Tab and Shift+Tab move from one section to the next, and the arrow keys move within a list. `c` collapses or expands the focused section.
3. **Tabs.** The number keys open a sheet's tabs, and each tab shows its number.
4. **The keys that act.** `a` adds to the focused list, `e` edits the highlighted row or the focused section, and `d` deletes the highlighted row after asking first. `m` More holds the rarer actions for where you are, and `n` New makes a covenant, character, laboratory or familiar bond. See [Keys](help:keys) and [What the keys act on](help:workspace-keys).
5. **The footer.** Its left end shows the keys that work where focus is, labelled with what they'll do, and its right end the keys that always work.
6. **Where you are.** The row above the footer names where focus is.
7. **The details panel.** A list that holds records shows the chosen row in full below it, with the rules text of a Virtue, Flaw or spell. See [Where you are, the details panel and the theme](help:workspace-status).
<!-- /tui -->
<!-- gui -->
1. **The trail.** The top left of the window names the pages above the one on show. Click one to go back to it, or a card to open the page of what it shows. See [The trail and the pages](help:workspace-tree).
2. **Chapters.** A page is a book of chapters, listed in the rail on its left. Click one to show it.
3. **The buttons that act.** A section's **Add** adds to it, and **Edit** and **Delete** act on the row or card last clicked in it. Forms open in a window of their own. See [What the buttons act on](help:workspace-keys).
4. **Making and managing.** A **New** card at the end of a page's cards makes one more, such as New Covenant or New Laboratory. The rarer actions are buttons in the chapter or section they act on. A record's own **Manage** chapter holds actions such as Export, Print to PDF and Delete.
5. **The top bar.** **Find** opens any record of the saga by its name, and **Help**, beside it, opens help on the page on show. Past a thin rule, the **gear** opens the Settings window, to choose the theme, turn the sounds on or off, and reduce motion (see [How to choose a theme](help:guide-themes)).
6. **Advance Season.** The card at the foot of the chapters, with the present season's medallion, is the **Advance Season** button. Click it, or press Space or Enter on it (see [Advance Season](help:advance-season)).
7. **The Inspector.** The right of a page shows whatever you last clicked in full, with the rules text of a Virtue, Flaw or spell. See [The Inspector and the theme](help:workspace-status).
8. **Your troupe, close at hand.** Fill in each player character's **Player** in their Biographical Detail, in their Description chapter. They then gather on the saga's first chapter, **The Troupe**, a click from their sheets. See [The Troupe](help:saga-troupe).
9. **Bookmarks.** For any other page you keep going back to, such as a rival magus, a Tribunal or a neighbour, open it and click the ribbon at the right of its header. It joins The Troupe too.
<!-- /gui -->

### Help
<!-- help: guide-getting-started-help -->

<!-- tui -->
Press `?` anywhere for help on the part of the screen that has focus, or F1 in a dialog where you're typing. The Help screen lists THIS SCREEN first, then the REFERENCE pages, the HOW-TO GUIDES and ALL PAGES. The reference pages include About this App, Keys, and What's New, which shows any changes not yet in a release, then what changed by feature and edition, then every version in its Chronicle. Filtering finds About and What's New by their titles too.

The arrow keys choose a topic, `/` filters the topics, Tab moves between the list and the page, and Esc closes Help.

On a topic about a tab or section of a sheet, `g` (Go there) closes Help and opens that tab on the record you were looking at, with the section focused. Some steps in the guides end with a **Go there** link that does the same when clicked. If the record on show has no such tab, such as Lab Totals while you look at a covenant, Help stays open and says which sheet it's on.
<!-- /tui -->
<!-- gui -->
Click **Help** in the top bar, or press `?` or F1, for help on the page and chapter on show. Help lists THIS SCREEN first, then the REFERENCE pages, the HOW-TO GUIDES and ALL PAGES. The reference pages include About this App, and What's New, which shows any changes not yet in a release, then what changed by feature and edition, then every version in its Chronicle.

The box above the list filters the topics, and finds About and What's New by their titles too. Click a topic to read it, and a link to follow it. Esc, or the trail, leads back to the page you came from, and `q` quits the app.

On a topic about a chapter of the page you came from, **Go there** under the topic list goes back to that page, open at that chapter. Some steps in the guides end with a **Go there** link that does the same. If the page you came from has no such chapter, Help stays open and says which page it's on.
<!-- /gui -->

The desktop's help and its guides are also on the [Armarius website](https://apoapsis138.github.io/armarius/), with how to install the app and answers to common setup questions. It's handy on another screen, or before you install.

### Where to go next
<!-- help: guide-getting-started-next -->

- [How to create a character, covenant or laboratory](help:guide-creation): building by the book with the Creation Worksheet.
- [How to plan and run a season](help:guide-seasons): planning everyone's season and advancing the saga.
- [How to manage the covenant](help:guide-covenant): its people, possessions and money.
- [How the app handles advancement](help:guide-advancement): study, books and teaching.
- [How lab planning works](help:guide-lab-planning): inventing spells, enchanting and other lab projects.
- [How to bind and keep a familiar](help:guide-familiars).
- [How to import and export](help:guide-import-export): moving records between sagas.
- [How to start a saga from a sourcebook](help:guide-book-packs): the shipped content packs.
<!-- gui -->
- [How to add a map and place its records](help:guide-atlas): the saga's Atlas.
- [How to fit the window to your screen](help:guide-window-size): high-resolution screens and display scale.
- [Jump to your sheet and back](help:guide-my-sheet): your character's sheet from any page while you are Playing.
<!-- /gui -->

**See also:** [Saga picker](help:saga-picker), [The workspace](help:workspace), [The saga](help:saga), [Keys](help:keys)

# How to create a character, covenant or laboratory
<!-- help: guide-creation -->

Your troupe is founding a new saga's covenant and its magi, or a new character is about to join play. The Creation Worksheet walks each one through the book's steps, with its budget and checks beside you.

### In Creation and In Play
<!-- help: guide-creation-modes -->

<!-- tui -->
Every new covenant, laboratory and character starts **In Creation**, and its tree node is marked "(creating)". While a record is In Creation the app runs its creation checks. Once it's **In Play** the checks stop. See [In Creation and In Play](help:creation-worksheet-modes).

The top panel of the record's sheet has a button that shows its mode, beside Edit (e). While it's In Creation, a **Creation Worksheet** button sits beside that.
<!-- /tui -->
<!-- gui -->
Every new covenant, laboratory and character starts **In Creation**, and its page is drawn on drafting vellum. While a record is In Creation the app runs its creation checks. Once it's **In Play** the checks stop. See [In Creation and In Play](help:creation-worksheet-modes).

The header of the record's page has a button that shows its mode, **In Creation** or **In Play**. While it's In Creation, a **Worksheet** button sits under it.
<!-- /gui -->

The exception is a character made from one of the Definitive Edition's templates. Those are finished characters, so they start In Play. The other templates, such as a Grogs template or a quick recipe, start In Creation, built from the choices you made.

### Choose the order
<!-- help: guide-creation-order -->

The three kinds of record depend on each other, so this order saves going back:

1. **The covenant first.** Its Power Level sets the Build Points the storyguide gives it, and those Build Points pay for its starting laboratories.
2. **Then the magi.** A covenant gets one standard laboratory free for each of its magi, so the Build Points come out right once the magi are in it. A laboratory's builder also needs Magic Theory 3, which a magus gains in their Apprenticeship.
3. **Then the laboratories**, each given to its magus, and the companions and grogs whenever you like.
4. **Last, review the covenant** and move everything to In Play.

You can move freely between records and steps. Nothing is locked in by the order.

### Start a character, with or without a template
<!-- help: guide-creation-character-new -->

<!-- tui -->
1. **Choose New Character.** Choose the covenant or its Characters group in the tree, press `n`, then `c` for New Character.
<!-- /tui -->
<!-- gui -->
1. **Choose New Character.** On the covenant's page, open its **People** chapter and click the New card at the end of a group, **New Magus**, **New Companion** or **New Grog**.
<!-- /gui -->
2. **Give a Name and a Type.** A Mythic Companion's templates are its kinds, such as Faerie Doctor (DE) or Zahid (RoP:D).
3. **Choose a template, or None.** Leave Template at None to build the character yourself, and the line above Create says the character starts In Creation. See [New Character](help:character-group-new) for the templates.
4. **Choose Create.** Some templates ask for their choices next, then make a character In Creation for you to finish on its worksheet: [A Grogs template](help:grog-templates), [Animal grogs](help:animal-grogs), [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws), [A Mythic Companion template](help:mythic-companion-templates), [A supplement's character](help:companion-sample-templates) and [A Grogs template as a companion](help:grog-template-companion).

### Open the worksheet
<!-- help: guide-creation-open; tui -->

A new covenant, laboratory or character opens its worksheet by itself. To open it again later:

1. **Focus the record.** Choose the record in the tree and press Enter to focus its top panel.
2. **Open the worksheet.** Choose the **Creation Worksheet** button, or press `m` More and choose Creation Worksheet.
3. **Find your way in it.** The [Creation Worksheet](help:creation-worksheet) fills the screen, with the steps on the left (see [Steps and their marks](help:creation-worksheet-steps)). In a step's list, `a` adds, `e` changes and `d` takes back.

The keys and buttons open the sheet's own dialogs and change the real record, so everything is saved as you go. When a dialog closes, the worksheet works out the budget and checks again.

### Open the worksheet
<!-- help: guide-creation-open; gui -->

A new covenant, laboratory or character opens its worksheet by itself. To open it again later:

1. **Open the record's page.**
2. **Click Worksheet.** It's under the In Creation button in the page's header, and only there while the record is In Creation.
3. **Find your way in it.** The [Creation Worksheet](help:creation-worksheet) opens as a page of its own. The rail on the left lists the steps. The chapter shows the chosen step's budget, its list and its buttons, its Creation Checks, and the step's own buttons under This Step. The Inspector on the right shows the row clicked.
4. **Move around.** Click a step in the rail to show it. The trail leads back to the record's page.

The buttons open the sheet's own forms and change the real record, so everything is saved as you go. When a form closes, the worksheet works out the budget and checks again.

### Build a covenant
<!-- help: guide-creation-covenant -->

<!-- tui -->
On each step, `a` adds to the step's list, `e` edits the highlighted row and `d` deletes or removes it. The key line under the step names what each does there, such as "a: Buy something", and the steps below use those names.
<!-- /tui -->
<!-- gui -->
Each step's list has an add button named for what it adds, such as **Buy something**, and **Edit** and **Delete** (or **Remove**) for the row last clicked.
<!-- /gui -->

The rules each step checks, with their book pages, are in [Steps and their marks](help:creation-worksheet-steps).

1. **Baseline: choose the Power Level.** Choose Power Level asks for the Power Level, the storyguide's Build Points, how many magi go without a laboratory and the Year Founded. The step shows the season and aura, which Edit covenant (season, aura) changes, what every covenant has free, and the highest level of text or enchanted effect allowed.
2. **Baseline: set the income.** Set starting income makes the covenant's sources of income by the rules. The step lists them. Add a source of income adds one, Edit edits and Delete deletes.
3. **Use a Covenant Situation, if you like.** It takes one of the books' ready-made sets of Boons and Hooks, and the step shows which. Choosing another Situation warns first, then swaps the earlier one's Boons and Hooks for the new ones. The ones you added yourself stay.
4. **Or start from a base covenant.** Use a base covenant starts from one of the book's three base covenants. It sets the Power Level and Build Points, and adds its books and vis as placeholders. Edit on a placeholder's Resources row chooses its subject or Art.
5. **Resources: buy what the covenant owns.** Buy something asks what to buy, such as a new book, a vis source, an enchanted item or a specialist. Enchanted items kept in the starting laboratories are bought here too. The step shows the Build Points spent and left, and lists each purchase under its category.
<!-- tui -->
6. **Buy a book the saga already has.** A book from the saga's books picks from the unassigned books in [the Armarium](help:armarium) that a new covenant may buy. F3 also shows the others, marked with why. The covenant gets its own copy, and the saga's book stays in the Armarium.
<!-- /tui -->
<!-- gui -->
6. **Buy a book the saga already has.** A book from the saga's books picks from the unassigned books in [the Armarium](help:armarium) that a new covenant may buy. Ticking **Show everything** also lists the others, marked with why. The covenant gets its own copy, and the saga's book stays in the Armarium.
<!-- /gui -->
7. **Change or remove a purchase.** Edit and Delete act on the chosen row. Lab Texts and Casting Tablets are bought as a pool of levels, so editing or deleting a text changes the pool's levels and Build Points to match. A laboratory is set up on its own worksheet.
8. **Boons & Hooks: balance them.** Add a Boon adds a Boon and Add a Hook adds a Hook. Edit edits the chosen one and Remove removes it. The step shows the chosen one's rules, and the Boon and Hook points, which should balance.
9. **Tie a resource Hook to its source.** A Contested, Indiscreet or Dwindling Resource Hook is about one of the covenant's vis or income sources. Edit on it chooses which, and that source is then marked Contested or Dwindling. That can wait until the source exists.
10. **Review Interests.** Edit Interests turns off what the covenant will never take up, such as its Manors or its Ships, leaving them off the sheet. Everything starts on, and you can change them at any time as its interests grow (see [Interests](help:interests)).
11. **Review.** It lists every step that still has a check open, and the Build Points tally. **Add the baseline's people** puts the grogs and other covenfolk the baseline gives for free among the covenant's inhabitants (DE p. 179).

<!-- tui -->
The covenant's [Build tab](help:tab-cov-build) shows the same Build Points.
<!-- /tui -->
<!-- gui -->
The covenant's [Build chapter](help:tab-cov-build) shows the same Build Points.
<!-- /gui -->

### Set up a laboratory
<!-- help: guide-creation-lab -->

A laboratory's worksheet has two steps, Setting Up and Review.

1. **Choose the owner.** On Setting Up, Edit identity (owner) chooses the magus who builds it.
2. **Set its Size and Refinement.** Edit Characteristics sets them.
3. **Add its Virtues and Flaws.** The step lists them with the chosen one's rules. Add a Virtue or Flaw adds one and Remove removes it.
4. **Say whether it's a starting lab.** Starting lab: yes/no says whether the covenant's Build Points pay for it. For a starting lab the step shows its Build Points.
5. **Install magic items, if any.** Install a magic item installs an enchanted device in it, making the device first if need be (see [How to install a magic item in a laboratory](help:guide-lab-magic-item)). The step shows what each one gives.
6. **Review.** It lists any check still open, such as an owner without Magic Theory 3, or Virtues that don't fit in Size plus Refinement.

See the [Laboratory sheet](help:laboratory).

### Build a character
<!-- help: guide-creation-character -->

The steps follow the book's order, and each one's buttons are named for what they do. The rules each step checks, with their book pages, are in [Steps and their marks](help:creation-worksheet-steps).

<!-- tui -->
On a step with a list, `a` adds to it, `e` changes the highlighted row and `d` takes it back. The key line under the step names what each does there, such as "a: Spend xp", and the steps below use those names.
<!-- /tui -->
<!-- gui -->
On a step with a list, its add button is named for what it adds, such as **Spend xp**, and the buttons for the row last clicked for what they do, such as **Change its xp** and **Take it back**.
<!-- /gui -->

1. **Concept.** Edit type (any type, while the character is In Creation) and Edit Year Born. A magus also has Edit House, a button to add The Gift and Hermetic Magus if they're missing, and Add the House Virtue. A Mythic Companion chooses their status Virtue.
<!-- tui -->
2. **Virtues and Flaws.** The step shows the Virtue points spent against those allowed, and the Flaw points and Minor Flaws against their limits. `a` adds a Virtue (F2 in the picker for Flaws), the Add a Flaw button opens the picker on Flaws, and `d` removes the chosen one. Its rules show below the list.
<!-- /tui -->
<!-- gui -->
2. **Virtues and Flaws.** The step shows the Virtue points spent against those allowed, and the Flaw points and Minor Flaws against their limits. Add a Virtue adds a Virtue, the Add a Flaw button adds a Flaw, and Remove removes the chosen one. Its rules show in the Inspector.
<!-- /gui -->
3. **Characteristics.** Edit Characteristics, or Fill from an array. To fill from one, choose one of the pre-bought arrays, then place its scores, one select per Characteristic. The step shows each score, what it cost and the points spent of the budget.
4. **Early Childhood.** Set the Native Language, then Spend xp on the childhood Abilities, or Use a sample childhood. With the Grogs book in play, Covenant Upbringing and Feral Upbringing offer those childhoods. An animal grog has **Pre-adult Life** instead (see [Animal grogs](help:animal-grogs)).
5. **Later Life.** Spend xp, use the button for any Virtue that gives its own xp, or Take a training package where one is offered. The step shows the years, the xp a year, what's spent and left, and the Ability cap at this age.
6. **Apprenticeship** (magi only). Spend xp spends xp on Arts and Abilities, and Learn a spell adds a spell. The spells list under the xp, each capped at its Lab Total. Choose one to see its details, or Take it back to forget it.
7. **Years past Gauntlet** (magi only). Years and conditions sets the years and working conditions. Spend points on xp spends them, and Learn a spell learns spells from the points those years give. An older character can Roll pre-play aging here.
8. **Equipment.** Add an item adds the weapons, armor and tools the character starts with (DE p. 44, the summary's step 11). They're kept in their Inventory. The step is advice (☞) until something is recorded.
9. **Review Interests** (not an animal). Edit Interests turns off the kinds of deed the character won't take up, such as Knightly for a scholar or Scholarly for a blacksmith, leaving those actions off the sheet. Everything starts ticked, and you can change them at any time (see [Interests](help:interests)).
10. **Finishing Touches.** Add a Personality Trait, Add a Reputation and Edit Confidence, then read the review of every step. A character other than a magus older than 35 can Roll pre-play aging here. With the Grogs book in play, a grog can Use the Grogs Aging Chart instead (see [The Grogs Aging Chart](help:creation-worksheet-aging-chart)).

Once xp is spent at a step, it's a row of the step's list, showing the pool xp spent and the xp gained (more with an Affinity). Change its xp changes it and Take it back takes it back. Spend xp's Specialty box gives the Ability its specialization.

### Marks, warnings and advice
<!-- help: guide-creation-marks -->

<!-- tui -->
Each step in the left column is marked ✔, ✘ (a warning), ☞ (advice) or ○ by how its checks stand, and below the list the app sums them up, for example "2 warnings, 1 advice". See [Steps and their marks](help:creation-worksheet-steps).
<!-- /tui -->
<!-- gui -->
Each step in the rail is marked ✔, ✘ (a warning), ☞ (advice) or ○ by how its checks stand, and the worksheet's header sums them up, for example "2 warnings, 1 advice". See [Steps and their marks](help:creation-worksheet-steps).
<!-- /gui -->

Checks never stop an edit. They only matter when you move the record to In Play.

### Move to In Play
<!-- help: guide-creation-play -->

1. **Choose Move to In Play.** It's on the worksheet's last step. The confirmation lists every check that doesn't pass, and for a covenant the Build Points left, which become Mythic Pounds. Choose Move to In Play to go ahead.
<!-- tui -->
2. **Or use the mode button.** From the sheet, choose the mode button on the top panel, or More's **In Creation / In Play**.
<!-- /tui -->
<!-- gui -->
2. **Or use the mode button.** From the record's page, click the **In Creation** button in its header.
<!-- /gui -->
3. **Fix any warnings, if the saga is strict.** If **Enforce creation rules strictly** is turned on in the saga's settings, a record with a warning stays In Creation, and a message says how many rules it breaks. Advice never stops it.
<!-- tui -->
4. **See it in play.** The "(creating)" mark leaves the tree node. A covenant keeps what its Build Points were spent on, shown in the Initial column of its Build tab.
<!-- /tui -->
<!-- gui -->
4. **See it in play.** The page is no longer drawn on drafting vellum, and its header says In Play. A covenant keeps what its Build Points were spent on, shown in the Initial column of its Build chapter.
<!-- /gui -->

You can move a record back to In Creation the same way, and its checks return until it moves to In Play again. See [Moving to In Play](help:creation-worksheet-play).

**See also:** [Creation Worksheet](help:creation-worksheet), [Characters group](help:character-group), [Laboratories group](help:laboratory-group), [Covenant sheet](help:covenant), [Character sheet](help:character), [The saga](help:saga), [Getting started](help:guide-getting-started)