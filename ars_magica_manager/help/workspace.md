# Title page
<!-- help: title-page -->

The page the app opens on. It shows the illuminated A and the name Armarius, the tagline, the version and its major version's name (see What's New), and the ways on.

- **Open Saga** opens the saga you had open last, or the only saga if there's just one. It isn't offered when there's no saga to open.
- **All Sagas** goes to the [saga picker](help:saga-picker), to choose a saga, start a new one or delete one.
- **New Saga** goes to the saga picker and opens its New Saga form at once. The new saga opens when you save it. Cancel the form and you stay on the picker.
- **Learn** shows two more ways on in their place, with **Back** to return.
  - **Tutorials** goes to the saga picker and opens [Start a Tutorial](help:saga-picker-actions).
  - **General Help** opens Help. `?` (or F1 on the desktop) opens it from the title page too.
<!-- tui -->
- **Update**, last and in the accent colour, is there only while a newer version of Armarius is out, with "Armarius X.Y.Z is available" beside it (in the warning colour when it brings security fixes). It opens the [Update screen](help:update-screen). See [How to check for an App update](help:guide-app-update).
<!-- /tui -->

<!-- tui -->
Enter takes the first of them. Choose with the arrow keys and Enter, and `q` quits. A player's copy of a hosted saga skips the title page and opens on the saga picker, where they sign in.
<!-- /tui -->
<!-- gui -->
While a newer version of Armarius is out, "! Armarius X.Y.Z is available" shows beside the version line, after a small gilded seal, and glows softly once (not with Reduce motion on). It reads "…, with security fixes" in the theme's warning colour when the new version brings them. Click it to open the [Settings window](help:settings-window) at its Update row. See [How to check for an App update](help:guide-app-update).

Click one. Enter takes the first of them, as the line under the buttons says. The window's own buttons, at its top right, minimise, maximise and close it.

The window opens fitted to the screen and centred on it, as large as the app likes but never more than nine tenths of the screen's free space. If the screen is too small for even the window's smallest size, it opens maximised. On a small screen, or one set to a large display scale, the title page draws its initial, name and buttons smaller so they fit. Given room again, it draws them full size. See [How to fit the window to your screen](help:guide-window-size).

The same illuminated A is the app's icon, on the Windows taskbar and in Alt-Tab. `run-gui.bat` opens the app with no console window behind it.
<!-- /gui -->

**You type:** nothing here. You choose where to go.

**The app works out:** which saga you had open last. The settings remember it each time you open one.

**See also:** [Saga picker](help:saga-picker), [Getting started](help:guide-getting-started)

### The Update screen
<!-- help: update-screen; tui -->

Opened by **Update** on the title page, or by Ctrl+P and **Update**. It says whether a newer version of Armarius is out, and holds the setting that looks for one, since the terminal app has no Settings window (the desktop app shares the setting).

- **The notice**: "! Armarius X.Y.Z is available", with its date and the first lines of its notes. It is in the warning colour, "with security fixes", when the new version's notes mark a security fix (a line starting **Security:**). A new major version adds a line saying players who join by Remote seat must move to it too. A version you skipped is shown faintly.
- **What's new** shows the new version's whole notes. Esc closes them.
- **Download page** opens the Release's page in your browser. A copy run from the source says to pull `main` instead.
- **Skip this version** hides the notice until a newer Release. A security update can't be skipped.
- **Check for updates when Armarius starts**: the app asks GitHub at most once a day, sending only its version. Untick it to stop, and to hide the notice.
- **Check now** asks at once and says what it found, or "Couldn't reach GitHub" and why.

While a notice waits, the first saga you open shows its short line once at the foot of the screen, beside the theme's name. Esc closes the screen. See [How to check for an App update](help:guide-app-update).

# How to fit the window to your screen
<!-- help: guide-window-size; gui -->

You've opened the app on a high-resolution (4K) screen set to a large display scale, and the window is too big or too small for it.

1. **Open the app.** The window fits itself to the screen (see [Title page](help:title-page)), and every form opens inside the screen too.
2. **Fill the screen.** Double-click the strip along the top of the window, or click the maximise button at the top right. On the title page, that strip is the space beside the window's buttons. On a saga's page, it's the app's name in the middle of the top bar. Do the same again to restore it.
3. **Size it by hand.** Drag any edge or corner, down to the smallest size it allows.
4. **Change the display scale.** If everything looks too large or too small, open **Settings > System > Display** in Windows, then **Scale**. On Windows 10 it's under **Scale and layout**. Close and reopen the app after changing the scale.

On a 4K screen, 150% to 200% leaves the app plenty of room. At 300% the window and its pages still fit, but drawn small.

**See also:** [Title page](help:title-page), [Moving around](help:workspace-moving)

# How to jump to your sheet and back
<!-- help: guide-my-sheet; gui -->

The Tribunal is debating your magus's case, and you need their Intrigue score now, without losing your place in the Meeting.

1. **Jump.** Click your character's name on the **Playing** button at the top right of the window, or press `c`. Sitting as a player with Play as, click "Playing as" and the name.
2. **See where you are.** Your sheet opens below the page you were on, and the trail marks the jump with ↪, such as "… › Rhine Tribunal ↪ Aurelia of Bonisagus".
3. **Read.** The sheet opens at the chapter you last left it on. You can open your familiar or laboratory from there as usual, and My sheet then steps back up to your sheet.
4. **Go back.** Click the crumb before your name, press `Esc`, or press `c` again. The page you jumped from opens at the chapter you left it on.

The button opens the character you last opened from it, else your first. Those that name you come before those everyone plays, and its ▾ lists them all. `c` does nothing while you type in a box or a form is open, in your storyguide role, or in a saga with no players. With no character of your own, the button reads just "Playing".

**See also:** [The trail and the pages](help:workspace-tree), [The Troupe](help:saga-troupe), [Keys](help:keys)

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
A saga file the app can't read is still listed, marked "can't be read", so you can delete it.

Under the list, **Save folder** shows the folder the sagas are read from and what chose it. That's the default, a folder chosen in the app, the ARMARIUS_DATA environment variable (or the older ARS_MAGICA_MANAGER_DATA), or a folder the app fell back to because the chosen one couldn't be used.
<!-- /tui -->
<!-- gui -->
The line under the page's title names the folder the sagas are read from. If the app ever closes itself without a word, `crash.log` in that folder records where it was. The file stays empty until then.
<!-- /gui -->
The default is Armarius in your app data folder (C:\Users\you\AppData\Local\Armarius on Windows, ~/.local/share/Armarius on Linux). If an older version saved somewhere else by default (Armarius or Ars Magica Manager at the top of your OneDrive), Armarius keeps saving there, as a folder you chose; Change save folder moves it.

**You type:** for a new saga, its Name and Storyguide (both required), the Start Year and Start Season, and an optional one-line Description.

**The app works out:** nothing here. The saga starts on the date you give and is saved at once.

### Opening, creating and deleting
<!-- help: saga-picker-actions -->

<!-- tui -->
- Highlight a saga and press Enter to open it in the workspace.
- `n` opens the Create a New Saga form.
- `d` (or Delete) deletes the highlighted saga after a confirmation.
- More (`m`) offers **Start a tutorial**, a fresh copy of a walkthrough guide's saga, which opens once it's made (see [How to learn with the tutorials](help:guide-tutorials)).
- More (`m`) also offers **Change save folder**. Choose a folder with the folder browser, where Enter opens a folder, Up goes to the parent, or you type a path. Then choose whether to move the saves there.
<!-- /tui -->
<!-- gui -->
- Click a saga's card to open it on its own page.
- **New Saga** opens the Create a New Saga form.
- **Start a Tutorial** makes a fresh copy of a walkthrough guide's saga and opens it (see [How to learn with the tutorials](help:guide-tutorials)).
- **Delete**, on a saga's card, deletes that saga after a confirmation.
- **Change Save Folder** lets you choose a folder in the system's folder dialog, then whether to move the saves there.
<!-- /gui -->
  The sagas, their backups, exports and settings are moved, and a file already in the new folder is never overwritten. Some folders refuse saving: on Windows, Controlled folder access protects Documents and the Desktop, and a read-only or synced folder can refuse too. So the app checks it can save in a folder before using it. When ARMARIUS_DATA (or ARS_MAGICA_MANAGER_DATA) sets the folder, it can't be changed here.
<!-- tui -->
- `q` quits the app.

In a browser opened on a hosted saga, the list only opens sagas. New and Delete are left to the storyguide's own window, and opening a saga first asks who you are. See [Signing in](help:sign-in).

The app's version is shown under the list.
<!-- /tui -->

Deleting a saga deletes its file and everything in it (covenants, characters, laboratories, library) for good. The confirmation says so, and No is the safe answer.

The About page in Help has the version, the licences and the credits.

**See also:** [The workspace](help:workspace), [The saga](help:saga), [Getting started](help:guide-getting-started)

# The workspace
<!-- help: workspace; tui -->

The screen a saga opens in. The navigation tree on the left lists everything in the saga, and the pane on the right shows the sheet or list for the node you choose.

**You type:** nothing here. You choose where to go.

**The app works out:** the tree's counts, such as "Characters (3)", and the row above the footer that says where you are.

### The navigation tree
<!-- help: workspace-tree -->

The tree's top node is the saga itself. Under it:

- Each covenant, with **Characters** and **Laboratories** under it. A magus with a bound familiar has it under them ("Familiar: name").
- **Unassigned Characters** and **Unassigned Laboratories**, for those with no covenant. They appear only when there's something in them.
- **Seasons**, the record of each season applied.
- **Saga Content**: the books in play, the catalogs the saga hides, its House Rules, its own spells and, for the storyguide, its players.
- **The Armarium** and **The Custodia Mirabilium**, the storyguide's only. They hold every book and every enchanted device in the saga, held or [unassigned](help:armarium).

A character's node shows its type, such as "Leandro (magus)". A covenant, laboratory or character still being made is marked "(creating)".

### Moving around
<!-- help: workspace-moving -->

- Arrow keys move along the tree. **Enter** shows the chosen node and moves focus into it: into a sheet's first section, or into a list such as Seasons.
- **Esc** steps out, from a sheet back to the tree and from the tree back to the saga picker.
- **Tab** and **Shift+Tab** move from one section of a sheet to the next. Each section is one stop, its list if it has one and otherwise its title. Arrow keys move within a section.
- **1** to **9** open a sheet's tabs, which show their numbers.
- **c** collapses or expands the section that has focus. Enter on a section's title doesn't.
- With the mouse, a click on a section without focus focuses it. A click on the focused section's title collapses or expands it.

### What the keys act on
<!-- help: workspace-keys -->

**a**, **e** and **d** act on whatever has focus: a list's highlighted row, a section, or the record itself. On a record's tree node, or the top panel that names it, **d** deletes the whole covenant, laboratory, character or familiar. Its confirmation lists what happens to what it owns. A focused list always has a row chosen. In a collapsed section, e and d say "Choose a row first." unless there's only one entry.

- **m** (More) holds the actions only a few places have, such as Import, Export, Set Date, Give or the Creation Worksheet. It offers only what applies where focus is. With one thing to do it runs straight away, and the footer names it. With several it opens a menu with a letter for each.
- **n** (New) makes a covenant, character, laboratory or familiar bond, offering only what belongs at the chosen tree node. A new character or laboratory starts in the covenant on show.
- **/** filters a list that can be filtered. On the Saga Content Spells tab it moves to the search box, and on a laboratory's Lab Texts it opens the filter.
- **t** advances the saga by one season. See [Advance Season](help:advance-season).
- **Ctrl+F** opens Find, to open any record by its name. See [Find](help:find).
- **q** quits, and **Ctrl+P** opens Textual's command palette (see [the theme](help:workspace-status)).
- **?** opens Help on the part of the screen that has focus. F1 does the same while you're typing in a dialog.

The footer shows the keys that work where focus is at its left, and the ones that always work at its right: New, Advance Season, Help, Back and Quit.

### Where you are, the details panel and the theme
<!-- help: workspace-status -->

The row above the footer says where focus is: the tree node on show, then the tab, the section and the chosen row, separated by "›".

Lists that hold records, such as books, spells, House Rules and a sheet's lists, have a details panel below them that shows the chosen row in full.

At the right end of the same row the app names the theme in use. Change it from the command palette (Ctrl+P), and the app remembers your choice for next time. A copy opened in a browser or over SSH has no command palette, and keeps the storyguide's theme.

**See also:** [The saga](help:saga), [Characters group](help:character-group), [Laboratories group](help:laboratory-group), [Seasons](help:seasons), [Saga Content](help:saga-content), [Getting started](help:guide-getting-started)

# The window
<!-- help: workspace; gui -->

The desktop shows one page at a time, the way a book is read: the Sagas, a saga, one of its covenants, characters, laboratories or familiars, Saga Content, the Seasons, a Creation Worksheet or Help. The bar across the top of the window says where you are and holds what works on every page.

**You type:** nothing here. You choose where to go.

**The app works out:** what each page shows, and which actions it offers.

### The trail and the pages
<!-- help: workspace-tree; gui -->

The trail at the top left names the pages above the one on show, such as "Sagas › Matrix › Keep › Leandro". Click one to go back to it.

- **A jump.** My sheet (your name on the Playing button, or `c`, while you are Playing) opens your character's sheet below the page on show, wherever that is, and the trail marks the jump with ↪ in place of ›: "… › Rhine Tribunal ↪ Aurelia of Bonisagus". The crumb before it, `Esc` or `c` again takes you back to that page, at the chapter you left it on. If the trail already passes through your sheet (from your familiar or your laboratory), My sheet steps back up to it instead. See [Jump to your sheet and back](help:guide-my-sheet).
- **The switcher.** When the page on show is a character, a laboratory or a covenant, a ▾ follows its crumb. Click it for the others at the same level: a character's covenant's people by Magi, Companions and Grogs (those of no covenant, for one who belongs to none), the covenant's laboratories, or the saga's covenants, the troupe's first. The one on show is marked "on show". Click another, or choose it with Up and Down and press Enter, to open it in place of the last crumb; the crumbs above it stay. A person opens at the chapter on show if they have it, else where you last left them. A long list has a box at its top: type to narrow it. `Esc`, or a click outside, closes it. It lists only what you may read (in Player view, or a player's seat, what the players know).

- **Sagas** shows every saga as a card. Click one to open it.
- A saga's page opens on [The Troupe](help:saga-troupe), with the player characters, the troupe's covenants and the pages you've bookmarked. Its other chapters are listed under [The saga](help:saga).
- A covenant's page lists its people, laboratories and possessions. Click a person or a laboratory to open their page. A magus's familiar opens from the magus's page.

A covenant, laboratory or character still being made is In Creation. Its page is drawn on drafting vellum, and its header has the In Creation / In Play switch and the Creation Worksheet.

### Moving around
<!-- help: workspace-moving; gui -->

- A record's page is a book of chapters. The rail on the left lists them, and a click shows one. A chapter longer than the window scrolls. Come back to a page and it opens on the chapter you left it at, until the app is closed.
- Click a card or row to choose it. A card for a covenant, person, laboratory or familiar opens its page.
- The trail goes back up. Leaving a page cancels a form left open on it.
- Drag the app's name in the middle of the top bar to move the window, and double-click it to maximise. Resize it from its edges and corners. A form opens inside the screen, shrunk to fit if it must. See [How to fit the window to your screen](help:guide-window-size).

### What the buttons act on
<!-- help: workspace-keys; gui -->

- A section's **Add**, **Edit** and **Delete** buttons act on that section. Edit and Delete act on the row or card last clicked in it, or the only one there is, and stay greyed out until there is one. Delete asks first.
- A form, a list to choose from and a question such as Delete's open in a window of their own over the page. When a button asks several things they come one after another, and the page waits until the window is closed.
  - Each window has the app's title bar. Drag it to move the window, and use its close button. A form or list also has a maximise button, or double-click the bar, and a form's edges resize it.
  - Choosing a file or folder uses the system's own window.
  - A window is sized to what it holds, and grows when a choice shows more fields, as Lab Work's does. Past the height of the screen its fields scroll inside it, above its buttons, so a long form such as Export Pack's list of ticks can be read to its end.
  - **Save** keeps what you typed, and **Cancel** leaves things as they were. If you've changed anything, Cancel, the close button and Esc ask first, so a slip doesn't lose your work. A form that only works something out has Close in place of Cancel, and doesn't ask.
  - Every change is saved to the saga file at once. A saga holding something that couldn't be opened again isn't saved: a note names the field, and the file stays as it was. That is a fault in the app, worth reporting.
  - One form is open at a time, and while it's open the page's other buttons wait. Clicking a New card, such as **New Magus** while a New Character form is open, takes you back to the form already open instead of opening another.
- Buttons in a page's header or chapter heading, such as **Edit Covenant**, act on the record itself.
- What the terminal keeps in its New and More menus is on the page itself. A New card ends the cards it adds to (**New Covenant**, **New Character**, **New Laboratory**). Other actions are buttons in the chapter or section they act on, such as **Give** beside a list's Add, Edit and Delete, **Set Up Research Library** on a covenant's Library or **Set Date** in the saga's Seasons chapter.
- A record's **Manage** chapter holds what acts on the record as a whole: Export, Update from a File, Print to PDF, Show on Map and Delete. Show on Map is there for a covenant, laboratory, neighbour or creature on one of the saga's maps (see [The Atlas](help:saga-atlas)).
- **Advance Season**, the card at the foot of the chapters on the left, shows the present season's medallion and date. Click anywhere on it to advance the saga by one season, after it asks first. It's on every page of a saga with chapters, but not on a Creation Worksheet, a Fight or a Siege. See [Advance Season](help:advance-season).
- The **gear** at the right of the top bar, past a thin rule after Help, opens the [Settings window](help:settings-window), with the theme, the sounds and Reduce motion.
- The **bookmark**, a ribbon at the right of the header of a character, covenant, laboratory, familiar, Tribunal, neighbour or creature, keeps that page on [The Troupe](help:saga-troupe).
- **Find**, just left of Help, or `Ctrl+F`, opens [Find](help:find), to open any record by its name.
- **Help**, `?` or `F1` opens Help on the page and chapter on show. `Esc` goes back a page, or cancels a form that's open, and `q` quits. See [Keys](help:keys).

### The Inspector and the theme
<!-- help: workspace-status; gui -->

The Inspector, on the right of a record's page, shows in full whatever you last clicked on the page, such as a row, a card, a book or a spell.

The theme is the look the whole app is drawn in: Scriptorum (aged parchment and iron gall ink), Scriptorum Dark (vellum by candlelight), or a House's own. Choose it in the [Settings window](help:settings-window), from the gear at the right of the top bar. The desktop remembers your choice on this computer and opens in it next time.

While a saga is open, the headpiece band under the top bar carries the present season's medallion at its centre. It's drawn in the set the saga chooses, its Medallion style setting. The same medallions mark the seasons elsewhere:

- the Seasons page's title and each past season's heading
- each season's column in Ahead, on the Seasons page and a covenant's Seasons chapter
- a covenant's header, with no words, for its own Covenant Season beside its Magic Aura and Loyalty
- the title of a covenant's Seasons chapter
- a character's This Season
- the column heads of a character's and a laboratory's calendar
- a siege's track

The present season's medallion glows. A figure drawn as a medallion, such as an aura or a Loyalty, takes the same set in its own colour. They change with the season when it's advanced, and with the set when the saga's settings change it.

**Sounds**, in the Settings window, turns the sounds on or off, and the app remembers which. Sounds are kept for moments that mean something:

- a page turning when you open a chapter, and a longer one for a record or page
- a quill when a form is saved
- coins in a Treasury, and a chest for the Inventory
- a wax seal when the new season comes to the top of its dial
- a dull knock when an entry is refused

Plain button presses stay silent. While the sounds are on and Armarius is the active window, it keeps the audio device awake with silence, so Bluetooth speakers and headphones don't lose the start of each sound. The sounds play on Windows only.

The pages move a little, never in your way:

- The Inspector's new item inks in on its gilt leaf as a sheen of light crosses it.
- A chosen row's gold wash spreads from the left, with its leaf after it.
- A chapter fades in with a small slide.
- An experience line that has moved since you last saw it, after Advance Season or an edit, grows to its new length.
- When the season advances, the dial of the four seasons turns (see [Advance Season](help:advance-season)).
- When a record is moved to In Play, a wax seal with its initial is pressed on the page for a moment.

**Reduce motion**, in the Settings window, stills them. The pages change at once, with no dial and no seal. It shows ticked while it's on, and the app remembers your choice. Until you choose, it follows Windows' own Animation effects setting.

**See also:** [The saga](help:saga), [Saga Content](help:saga-content), [Seasons](help:seasons), [Getting started](help:guide-getting-started), [The Settings window](help:settings-window)

### The Settings window
<!-- help: settings-window; gui -->

The gear at the right of the top bar opens the Settings window. It stays open beside the page while you go on working. Close it with **Close** or its title bar's close button, and the gear brings it back. While a newer version of Armarius is out, the gear wears a small "!" seal.

- **Update**, at the top, says whether a newer version is out: "! Armarius X.Y.Z is available", with its date and the first lines of its notes (in the warning colour, "with security fixes", when its notes mark a security fix, a line starting **Security:**; faint once you've skipped it). **What's new** shows all its notes in Help, **Download page** opens its Release in your browser (a copy run from the source says to pull `main` instead), and **Skip this version** hides the notice until a newer one (not for security fixes). In a joined saga whose host runs another minor version, it says so instead, with **Update** when yours is the older. **Check for updates when Armarius starts** asks GitHub at most once a day, sending only the app's version; untick it to stop, and to hide the notice. **Check now** asks at once and says what it found, or "Couldn't reach GitHub" and why. See [How to check for an App update](help:guide-app-update).
- **Theme** is a drop-down showing the look the app is drawn in, as a small sample of its page with the House's mark, its name and a few words on it.
  - Open it for every look. Scriptorum and Scriptorum Dark come first, then the House themes under their House family (True Lineages, Mystery Cults, Societates). House Diedne comes last, on its own under Renounced.
  - Choose one and the whole app, the window included, is drawn in it at once. There's nothing to confirm.
  - With the drop-down chosen but closed, the up and down arrow keys step from theme to theme, past the family headings. Each is drawn as you reach it, to compare them quickly.
  - A record In Creation is drawn on the theme's own drafting page, cooler and ruled. Printed pages stay in Scriptorum.
- **Sounds** turns the app's sounds on or off.
- **Reduce motion** stills the pages' movements, the season dial and the seal.
- **Virtual Tabletop (Preview)**, under Preview, turns on the parts of the Virtual Tabletop built so far: Begin Session, End Session and a Session's [Chronicle](help:chronicle). It's off by default until the Virtual Tabletop is finished in 5.0. Remote seats work without it.

A House theme draws the window, its pages and its windows in its House family's form, with the House's own colours, paper and mark:

- **True Lineages** (Bonisagus, Guernicus, Mercere, Tremere): square-cut and Roman. A double rule runs round the page with square blocks at its corners, a key pattern runs through the band over the page, and headings are in inscriptional capitals.
- **Mystery Cults** (Bjornaer, Criamon, Merinita, Verditius): round and closed. A frame has rounded corners and a ring at each, with chains of rings, and headings are in uncials.
- **Societates** (Ex Miscellanea, Flambeau, Jerbiton, Tytalus): angular, with a frame whose corners are cut off, and chevrons. A row of swallow-tailed pennants in the House's colours hangs from a cord across the band over the page. Big titles, such as a sheet's name or a window's title, are in blackletter, and section headings are in small capitals in the House's heading colour.

The House's sign closes every chapter of a page, in the headings' ink between the family's rules, where Scriptorum has its three leaves. It also shows faintly at the foot of the Inspector, as a watermark shows in a sheet held to the light. Scriptorum and Scriptorum Dark belong to no House, so they show the Order of Hermes's sigil there instead. An illuminated initial takes the House's pigments. Text stays as easy to read as in Scriptorum, since a texture is drawn fainter behind text and whole in the margins. The colours that mean something keep their colours in every theme, such as a realm, a season's kind, Loyalty, an error or a warning, and so does a coat of arms.

The House themes:

- **Bonisagus** (True Lineages, light): clean vellum faintly ruled with compass-drawn circles, lapis ink and the crossed keys.
- **Guernicus** (True Lineages, light): a law tablet's cool marble, crossed by soft veins and lines of incised capitals. Iron-black ink, indigo headings, and the scales of justice on a sword in bronze, the House's metal.
- **Mercere** (True Lineages, light): road-dust parchment creased where letters were folded, with drops of sealing wax and a dotted road. Headings are in the Redcap's deep red, and frame and rules in the triangle's deep woad blue. The sign closing each chapter shows the mark in the book's own colours, with the red cap, the yellow coin and the blue triangle.
- **Tremere** (True Lineages, dark): iron by night, laid with the flagstones of a Roman road worn so low they only just show. Pale steel headings, rust for frame and rules, and Mars incised with a square. Cold and still where its rival Tytalus storms.
- **Bjornaer** (Mystery Cults, light): a pale hide, its grain pricked and softly creased, sewn along seams whose ochre thread has faded into it. Fur runs along the frame, and feathers hang from the corner rings and lie along the rules. Dark pine headings, a bear-brown ochre for frame and rules, and the cone closing each chapter.
- **Criamon** (Mystery Cults, dark): the violet dark of the Cave of Twisting Shadows. Its rock is marked with loops of the infinite, rings within rings and small spirals, worn half away into the dark. Bone-pale ink, lamp-amber headings and the Loop of the Infinite in the Eye of Time.
- **Merinita** (Mystery Cults, dark): a faerie wood at twilight, the faint shadows of oak leaves and acorns on a moss-dark page. Oak leaves lie along the frame from the corner rings and along the rules, and a vine of oak leaves runs through the band over the page. Moonlit green-silver headings and leaves, heather violet for frame and rules, and the oak in its circle closing each chapter.
- **Verditius** (Mystery Cults, dark): a forge by night, its soot-dark metal hammered with faint dents and catching the forge's light in a few soft glints. A cut stone is set in each corner's ring, and hammer and tongs cross in the band over the page. Headings in the gold of the House's rings, hot copper for frame and rules, and the hand with its five rings closing each chapter.
- **Ex Miscellanea** (Societates, light): many parts made one whole. A warm linen page carries a patchwork of pages from the traditions the House gathers, each ruled its own way and sewn to the next along stitched seams, with the mist of Cad Gadu's lake drifting over it. Lake-slate headings, a lichen ochre for frame and rules, the crooked staff closing each chapter, and pennants dyed one muted colour for each tradition.
- **Flambeau** (Societates, dark): a page that has been through the fire. It's ember-black, scorched in soft dark blots with the heat still glowing under them and a few live embers caught in the scorch, with a small flame at each corner and over the band. Flame headings, crimson for frame and rules, pennants in flame and crimson, and the hourglass closing each chapter. A name or a passage opens on an initial quartered crimson and flame, as a knight's shield is.
- **Jerbiton** (Societates, light): a Byzantine city's fine arts. Cream vellum has the faintest weave of a tapestry through it, purple threads and now and then a teal one, with a tessera at each corner. Imperial purple headings, a mosaic teal for frame and rules, and pennants in both. Over the band, the House's own pennant flies from its staff with mercury's sign, and the pennant on its tower closes each chapter.
- **Tytalus** (Societates, dark): Fudarus's storm-slate sky, with banks of sea mist rolling over it and rain driven slantwise through them. Headings and the spira closing each chapter are in Buliste's violet, a bright amethyst. Frame, rules and scroll bars are in Harpax's green, a deep, dark verdigris. The two claimants' colours are set against each other in lightness as well as hue, so they part even for red-green colourblind eyes. A name or a passage opens on a small illuminated initial, a burnished-gold letter on a ground quartered violet and green.
- **Diedne** (Renounced, dark): the pagan House the Order destroyed, drawn as a forbidden book read by a covered lamp.
  - Its page is a palimpsest. The ghost of older writing in an invented hand shows through where it was scraped off the vellum, faded where the knife went over it and almost gone behind the text. The skin is fine-scratched by the knife.
  - It belongs to no family, so it keeps Scriptorum's frame and ornaments, worn. Its frames, the Inspector's too, its rules and the band over the page are broken off in places, and two corner flourishes are gone.
  - Uncial headings in a pale ash-grey like faded chalk, oak-gall brown for frame and rules, and plain initials with no gilt.
  - Closing each chapter, in the dark of the Inspector's watermark, are the last traces of a sign gouged out of the page: a few ends of a triskelion's spirals. The books give Diedne no symbol, since its own was struck from the records, so this one is invented.

The app remembers each choice on this computer.

**See also:** [How to choose a theme](help:guide-themes), [The Inspector and the theme](help:workspace-status)

# Find
<!-- help: find -->

Find opens any record in the saga by its name, without going through the pages above it.

<!-- tui -->
**Ctrl+F** (`^f Find` in the footer), anywhere in the workspace, opens Find, a box to type in over the list of matches. Each letter typed narrows the list. **Down** moves into the list and **Enter** opens the chosen match, or the first one if you press it in the box. The tree moves to the record and its sheet shows. **Esc** closes Find and leaves you where you were.
<!-- /tui -->
<!-- gui -->
**Find**, in the top bar just left of Help, or **Ctrl+F** on any page of a saga, drops a box under the button with the matches below it. Each letter typed narrows the list. **Up** and **Down** choose a match and **Enter** opens it, or click one. It opens below the page on show, so the trail leads back. **Esc**, or a click anywhere else, closes Find. It lists sixty matches at most, and says how many more there are.
<!-- /gui -->

Each match shows its name, its kind and where it is: "Gottfried of Arnsberg · Lord · The Drachenfels".

- **What it finds:** characters, covenants, laboratories, familiars, Tribunals, neighbours of every kind, creatures, books, spells and enchanted devices. Neighbours include lords, towns, the Church, universities, factions, threats, places, customs and lore.
- **By name first**, in any case and with or without accents ("dammerstein" finds Dammërstein).
  - First come names that start with what you typed, passing over a leading "The" or "A". Then come names with a word that does, then names that hold it anywhere.
  - Within each, a name that's exactly what you typed comes first, the kind it ends with aside. So "rhine" lists The Rhine Tribunal before The Rhine Gorge.
- **Then by what it's tied to**, with the reason shown beside the match. A faction is found by its members ("member Gottfried of Arnsberg"). A record is found by the place it's at, and by the Tribunal whose lands it lies in ("in the lands of Rhine"), set on a place (see [Place](help:tab-nb-place)).
- **Books, spells and enchanted devices** have no page of their own.
  - A spell opens the page of the magus who knows it, at Known Spells with its row chosen. A spell nobody knows isn't listed.
  - For the storyguide, every book opens [the Armarium](help:armarium) and every device [the Custodia Mirabilium](help:custodia), at its row, held or unassigned. A filter hiding it is cleared.
  - For a player, a book or device opens the page of whoever holds it, at its row: a covenant's book in its Library, or a device among its holder's Enchanted Devices. One nobody holds isn't listed.
- **Secrets, for the storyguide:** your Find also looks in each record's [Secrets](help:tab-secrets), last. A match there is marked "secret", with the words around it. A player's Find never does, and in [Player view](help:player-view) yours doesn't either.
- **What the players don't know of** is never listed for a player or in Player view, nor named as where another record is.
- **Not searched:** notes and descriptions, the seasons played and the calendar.

**See also:** [How to find a record](help:guide-find-record)

# The saga
<!-- help: saga -->

<!-- tui -->
The top node of the tree. It shows the saga's own details and what it holds.
<!-- /tui -->
<!-- gui -->
The saga's page, opened from its card on the Sagas page. It has nine chapters, and opens on the first.

- **The Troupe** gathers the player characters, the covenants the troupe plays and the pages you've bookmarked (see [The Troupe](help:saga-troupe)).
- **The Covenants** shows its Covenants, Unassigned Characters and Unassigned Laboratories as cards. Each heading ends in a blank card that makes one more (New Covenant, New Character, New Laboratory). A covenant's card shows its aura with its Boons and Hooks counted, the same total its page shows. Each Aura Boon adds 1 (Definitive Edition p. 183).
- **The Region** holds its Tribunals, each a card with a New Tribunal card after them, and its neighbours (see [The Region](help:region)).
- **The Atlas** holds its maps, with a pin for each covenant, place and neighbour on them (see [The Atlas](help:saga-atlas)).
- **Compendium** holds the Armarium, the Custodia Mirabilium and the Bestiary's creatures (see [Compendium](help:saga-compendium)).
- **Conflicts** lists its fights and sieges (see [Conflicts](help:conflicts)).
- **Seasons** sets the date (Set Date) and opens the seasons played.
- **Saga Settings** holds its details, its seasons, the content in play (Saga Content's card), its optional rules and its ruling templates (see [Saga Settings](help:saga-settings)).
- **Saga Management** holds Import, Export Saga, Export Pack and Host for Players.

A familiar is bound on its magus or in their laboratory.
<!-- /gui -->

<!-- tui -->
**You type:** with `e`, the saga's settings. That's the Name, Storyguide and Description, and whether to Keep season records. It's also the optional rules of the books in play, each off until you turn it on, and the **Ruling templates** a Tribunal's rulings are written from (see [Hold Tribunal](help:hold-tribunal)). `Enter` opens the templates' list, where each can be added, changed or removed. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /tui -->
<!-- gui -->
**You type:** the Name, Storyguide and Description, with **Edit Saga** on [Saga Settings](help:saga-settings), where everything else about the saga is set too. The books in play are chosen on [Saga Content](help:section-books-in-play).
<!-- /gui -->

**The app works out:** the counts of covenants, characters, laboratories, books and spells, and a summary of the books in play and the optional rules turned on. With none on, it says "none (the book's standard rules)".

### What the saga shows
<!-- help: saga-summary -->

<!-- tui -->
- **Current date**: the season and year the saga is in. It's also shown in the header on every screen of the workspace.
<!-- /tui -->
<!-- gui -->
- **Current date**: the season and year the saga is in, under its name. It's also shown under the chapters, beside Advance Season, on every page with chapters.
<!-- /gui -->
- **Books in play**: the sourcebooks the troupe uses, and how many of the saga's own sources are in play. They're chosen on [Saga Content](help:section-books-in-play), which says what a book out of play switches off.
- **Optional rules**: Simple dice only, Dominion Magic Resistance, Harsher Infernal vis, Starting income by number of magi, Enforce creation rules strictly, Extended book Quality, Bruises, Dominion growth and Auras change. Each one's effect is described on its card in the saga's settings.
  - Four are offered only while their book is in play. They're Harsher Infernal vis from Realms of Power: The Infernal, Extended book Quality from Covenants' Library chapter, Dominion growth from Realms of Power: The Divine, and Auras change from Realms of Power: Magic.
  - Simple dice only and Dominion Magic Resistance are house rules the Definitive Edition offers as examples, not rules of the game (Chapter 16: Sagas, Rules Questions, p. 524).
  - With Dominion Magic Resistance on, a Christian, Jew or Muslim living in a Dominion aura shows Magic Resistance of 5 x that aura on their sheet. So does anyone whose religion is left blank.
  - **Standard apprenticeship model** (Apprentices) is offered only while that book is in play, and is off by default. See the Apprenticeship step of [the Creation Worksheet](help:creation-worksheet-steps).
  - **Learning cantations in play** (Apprentices) is offered only while that book is in play, and is off by default. See [Learn a Cantation](help:learn-cantation).
  - **Hazardous Laboratory Texts** and **No magical copying of Lab Texts** (Transforming Mythic Europe pp. 103-104) are offered only while that book is in play. With the first, a Lab Text copied by magic below the Finesse Total that copies it flawlessly isn't useless. Each use of it makes an extra Experimentation roll, its risk modifier half the pages spoiled in ten, and the season's Diary entry gives it. With the second, Copy books by magic refuses Lab Texts, so each is written by hand.
  - **Charter Strength** (Transforming Mythic Europe p. 36) is offered only while that book is in play. A charter between a lord and a town or covenant has two scores, and Draft the Charter and Seek a Loophole are offered on its lords.
<!-- tui -->
- **Keep season records**: when on, each season applied is kept under Seasons in the tree. When off, only the characters' Diaries keep them.
<!-- /tui -->
<!-- gui -->
- **Keep season records**: when on, each season applied is kept on the Seasons page. When off, only the characters' Diaries keep them.
<!-- /gui -->

### Saga Settings
<!-- help: saga-settings; gui -->

Everything about the saga that can be set, on one chapter of its page, as cards under their sections' headings: **Saga Details**, **Seasons**, **Content in Play**, **Optional Rules** and **Tribunal**.

- **Saga Details** shows the Name, Storyguide and Description, and **Edit Saga** changes them.
- **Content in Play** holds Saga Content's card, which counts the books in play, the catalogs, House Rules and spells. Click it to open [Saga Content](help:saga-content), where the books in play, catalogs, goods, House Rules, mystery cults, spells and Sessions are all set.
- A card's first line names the setting, and the line under it says briefly what it does. Click the card to read it in full in the Inspector, with its source for an optional rule.
- A **switch** at a card's upper right turns the setting on or off at once, as a book's chip does on Books in Play. There's no Save, and the Inspector has the same switch.
- A **chip** at the upper right shows a setting chosen from a list, such as what idle magi, companions and grogs do, the Medallion Style set, or the Ruling Templates. Click it to change it.
- Click **Medallion Style** to see an example of every set in the Inspector, with the one in use marked. The set draws every medallion on the desktop, the seasons' and the figures', such as an aura or a covenant's Loyalty.
- **Ruling Templates** opens as a ledger, each template's name in red beside its words. A row too long for the window ends in dots. Hover over it, or maximise the window, to read it all.
- **Optional Rules** are sorted by what they touch, each naming its book. All are off until you turn them on. A rule whose book is out of play is greyed out and can't be switched. It counts as off, and your choice is kept for when the book comes back. Books are chosen on [Saga Content](help:section-books-in-play).

### Compendium
<!-- help: saga-compendium; gui -->

The saga page's chapter of what the saga holds beyond its covenants and its region.

- **The Armarium** and **The Custodia Mirabilium** open as cards at the top. They hold every book and every enchanted device in the saga, each with its count and how many nobody holds (see [The Armarium](help:armarium) and [The Custodia Mirabilium](help:custodia)). Only the storyguide sees them.
- **Content in Play** takes their place for a player, and in [Player view](help:player-view). It's Saga Content's card, which opens [Saga Content](help:saga-content) to read the books in play, catalogs, House Rules and spells. The storyguide finds the same card on [Saga Settings](help:saga-settings), which players don't see.
- **The Bestiary** follows, with its facts, then every creature as a card that opens its page, and a New Creature card (see [The Bestiary](help:bestiary)).

The chapter is drawn the first time you open it, since a Tribunal pack can bring dozens of creatures.

### The Troupe
<!-- help: saga-troupe; gui -->

The saga page's first chapter, so the characters you play are a click away rather than inside their covenant's People.

- **Next Session**: the next evening of play, with its storyguide, who's coming and who's Away, and who plays whom. Then come the other planned [Sessions](help:tab-content-sessions) and the three played most recently. Saga Management's Sessions adds and changes them.
- **Your Characters**, while you're Playing or sit as a player: the characters you play, those that name you first, then those everyone plays. The Playing button, or `c`, opens the first of them, or the one you last opened from it (see [Jump to your sheet and back](help:guide-my-sheet)).
- **Player Characters**: every character whose Biographical Detail, in their Description chapter, names their **Player**, or who is **Played by** one of the saga's [players](help:players-access). They're grouped by covenant, the troupe's covenants first, then the others, then those who belong to none. Click one to open their sheet. **Print the Troupe**, under the heading, prints every one of them into one PDF, each from a fresh page with a bookmark of their name (see [Printing a record](help:print-record)).
- **Stewards**: each Player's stewarded characters, and whether each has a plan for the current season. A [Steward](help:players-access) keeps a character with no Player of its own between Sessions. This isn't shown while the saga has no players.
- **Troupe Covenants**: the covenants the troupe plays, marked ✦ as on The Covenants.
- **Bookmarked**: anything else you bookmarked, by kind (characters, covenants, laboratories, familiars, Tribunals, neighbours and creatures). A bookmarked page that's a player character or a troupe covenant is shown once, above.

To bookmark a page, open it and click the ribbon at the right of its header, below its buttons. A faint outline becomes a filled ribbon, and clicking it again takes the bookmark out. Bookmarks belong to whoever reads the saga. They're kept on this computer, saga by saga, and aren't saved in the saga file, so another computer, or someone else who opens the same saga, has their own. A bookmarked record that's deleted drops off the chapter.

**The app works out:** who is a player character, from their Player, and the cards' figures, as on The Covenants.

### More on the saga
<!-- help: saga-more -->

- **Set Date** moves the saga to any season and year without applying anything. It doesn't undo what a season did.
- **Undo Last Season** puts the whole saga back as it was before the last advance (see [Undoing a mistake](help:guide-seasons-undo)).
- **Import** opens the Import Data dialog, for characters, covenants or laboratories exported from another saga, or books or spells from a CSV file. See [Import Data](help:import-data).
- **Host for Players** lets the players open the app in a web browser on their own computers, and **Stop Hosting** ends it. Only the storyguide's own window offers them. See [How to host a saga](help:guide-hosting).

<!-- tui -->
New (`n`) on the saga offers New Covenant, New Character, New Laboratory and, while a magus has no familiar, Bind Familiar.
<!-- /tui -->
<!-- gui -->
Set Date is in the Seasons chapter, and Import and Host for Players are in Saga Management. The New cards on The Region make a Tribunal or neighbour.
<!-- /gui -->

**See also:** [The workspace](help:workspace), [Advance Season](help:advance-season), [Import Data](help:import-data), [Creation Worksheet](help:creation-worksheet), [Getting started](help:guide-getting-started)

# Characters group
<!-- help: character-group -->

<!-- tui -->
The Characters node under a covenant, or Unassigned Characters under the saga. It lists the characters in the tree below it. Choose one there to open their sheet.

**You type:** nothing here. `n` (New) offers New Character, with this covenant already chosen, and Bind Familiar while a magus has no familiar.
<!-- /tui -->
<!-- gui -->
A covenant's People chapter, or Unassigned Characters in the saga's The Covenants chapter, shows the characters as cards. Click one to open their sheet.

**You type:** nothing here. In a covenant's People, each group ends in a New card (**New Magus**, **New Companion** or **New Grog**) that makes one with this covenant already chosen. Unassigned Characters ends in **New Character**. A familiar is bound on its magus's page, or in their laboratory.
<!-- /gui -->

<!-- tui -->
**The app works out:** the count in the node's label.
<!-- /tui -->

**See also:** [Laboratories group](help:laboratory-group), [Creation Worksheet](help:creation-worksheet), [The workspace](help:workspace), [How to create a character, covenant or laboratory](help:guide-creation)

### New Character
<!-- help: character-group-new -->

The Create a New Character form asks for a Name, a Type (magus, companion, Mythic Companion or grog) and a covenant. For a type the books have templates for, it also offers a **Template**:

- **None**. The character starts In Creation, to be built step by step with the [Creation Worksheet](help:creation-worksheet).
- **A template**, one of the book's ready-to-play characters (Ars Magica Definitive Edition, Chapter 3, Character Templates). It fills the new sheet and the character starts In Play. If the template leaves a name to the player, such as an Area Lore's area, the app asks for it before the character is made. Cancelling that cancels the new character.
- **A Grogs template**, for a grog while Grogs is in play, marked "(Grogs)". It's one of the nineteen kinds of grog in Grogs, Chapter 7, such as The Advisor or The Street Thug. These are guidance rather than finished characters, so the app asks for the template's choices next (see [A Grogs template](help:grog-templates)). The grog starts In Creation.
- **A quick recipe**, marked "(DE quick)". It's the Definitive Edition's Quick and Easy Virtues and Flaws, for a grog, a martial, learned, social or magical companion, or a magus. The app asks for the recipe's choices next (see [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws)), and the character starts In Creation with those Virtues and Flaws.
- **A Mythic Companion template**, marked with its book, such as "(DE)" or "(RoP:D)". It's one kind of Mythic Companion, such as the Faerie Doctor or the Zahid, with the Virtues and Flaws its book requires and its minimum Abilities. See [A Mythic Companion template](help:mythic-companion-templates).
- **A supplement's character**, for a companion, grog or Mythic Companion, marked with its book. It's a ready-made character from a supplement, such as the Byzantine Priest or The Church's Anchoress. See [A supplement's character](help:companion-sample-templates).
- **A Grogs template as a companion**, for a companion while Grogs is in play. See [A Grogs template as a companion](help:grog-template-companion).
- **An animal template**, for a grog while Grogs is in play, marked "(Grogs, an animal)". It's the book's sample Dog, Horse or Hawk (Grogs, Chapter 7, Horses & Hounds, p. 137). See [Animal grogs](help:animal-grogs).

The line above Create describes the template you chose.

### A Grogs template
<!-- help: grog-templates -->

After Create, a Grogs template asks for its choices before anything is made. The templates are from Grogs, Chapter 7, Grog Templates, and the limits from the Definitive Edition, Chapter 3.

**You choose:**

- **Faith**, **Stage** or **Character**, where the book gives several versions. These are the Confessor's faith, the Craftsman's apprentice or journeyman, and the Animal Trainer's three sample characters.
- **Age**, one of the book's ages for the template. It sets the year born and which of the book's Ability lists the grog gets.
- **Social Status**, from the ones the book suggests.
- **The book's Virtues and Flaws**, ticked. Untick one to leave it out.
- **The book also suggests**: tick any of its other suggestions. Where the book says "this or that", pick one.
- **Another Virtue** and **Another Flaw**, for any other Minor Virtue or Flaw a grog may take, from the books in play. Where the book gives a Flaw a grog can't take, the hint under the first Another Flaw says what to choose instead.
- **The book's Characteristics**, for The Advisor only, the one template that gives figures, and a **Personality Trait** where the book gives a choice.

**The app works out:** the line under the form, with the template, the xp a grog has at that age against what the book's list comes to, and the Virtue and Flaw points so far. Next refuses a choice that breaks a grog's limits, which are:

- no Major Virtues or Flaws
- nothing Hermetic, and not The Gift
- at most three Minor Flaws
- no more Virtue points than Flaw points
- exactly one Social Status

Taking fewer Virtues than Flaws is allowed here. The worksheet then shows the points left to balance.

Then the app asks for any names the Ability list leaves to you, such as an Area Lore's area, the Native Language or a Craft. The covenant's own name is filled in for you. Then it makes the grog. Cancelling either form cancels the new character.

**What the grog starts with:** the age, the Social Status, Virtues and Flaws, the book's Personality Traits and any Reputation, and the book's Ability list for that age, with its specialties. If the book's traits lack them, the grog gets Loyal +1, and Brave +1 if it has a Martial Ability.

The Abilities go on the [Creation Worksheet](help:creation-worksheet) as xp, step by step:

- 75 xp of Native Language
- the free score of a Supernatural Ability its Virtue grants
- a Virtue's own xp (Educated, Warrior, Arcane Lore) on what it may buy
- the 45 xp of Early Childhood on what a child may learn
- the rest in Later Life

The grog starts **In Creation**, so the worksheet checks the result. Its checks say where the book's list spends more than the age gives, needs a Virtue the grog doesn't have (a Martial Ability without Warrior), or leaves xp unspent. The Biography notes the template, the book's details and its suggested training packages. It also notes where the app's version differs from the book and why, such as a Flaw the Definitive Edition makes Major, or an older edition's Ability.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [How to start a character](help:guide-creation-character-new)

### Quick and Easy Virtues and Flaws
<!-- help: quick-virtues-flaws -->

The Definitive Edition's Quick and Easy Virtues and Flaws (Chapter 3, p. 47) are a fast way to choose a character's Virtues and Flaws. Each type's Template list has its recipes, marked "(DE quick)":

- **Grog**: a Minor Personality Flaw for how you want to play the grog, Covenfolk, and one Minor Virtue. That's Warrior for a grog who fights, Educated for one who's educated, Arcane Lore for one who knows about the supernatural, or Puissant in the grog's specialty for anyone else, typed in, such as Craft: Blacksmith.
- **Companions**: a Major Personality or Story Flaw, which says what stories they're in, Covenfolk, and three points of Virtues from one of four recipes.
  - **Martial companion**: Warrior, with Puissant and Affinity in one Martial Ability.
  - **Learned companion**: Educated, with either Puissant in two Academic Abilities, or Puissant and Affinity in one.
  - **Social companion**: one of Gossip, Piercing Gaze, Social Contacts, Well-Traveled or Venus' Blessing, with Puissant in two Social Abilities. The book doesn't say which Abilities are Social. The app offers Bargain, Carouse, Charm, Etiquette, Folk Ken, Guile, Intrigue and Leadership.
  - **Magical companion**: one Minor Supernatural Virtue that grants an Ability, such as Second Sight, with Puissant and Affinity in that Ability.
- **Magus**, with the House's free Virtue chosen on the worksheet:
  - a Major Personality or Story Flaw
  - The Gift and the Hermetic Magus Social Status
  - Deficient Form in a Form you're not interested in
  - a Minor Magical Focus that doesn't rely on that Form, typed in, such as Fire
  - Puissant and Affinity in one Technique that overlaps the Focus
  - Puissant in one Form that overlaps it

**Templar companion (The Church).** The Social Status is the character's rank in the Knights Templar: Brother Knight, Brother Sergeant, Brother Chaplain, Templar Administrator, Templar Specialist, Templar Commander, or an associate (Confrere or Consoeur) or servant. The ranks are in The Church pp. 123-125, and the Definitive Edition reprints them (pp. 73 and 111-112). "Renowned among the brothers" adds Templar Prestige, a Reputation 4 among the Templars. An office (Templar Office Holder) is a second Social Status, taken on the sheet. A commander already has the brother-knight's standing and Temporal Influence free.

**You choose:** which one, where the recipe gives several ways, such as the grog's Virtue or the Learned companion's. Then the Abilities, Arts or Virtue each part names, the **Flaw** from the books in play, and the **Social Status**. That's Covenfolk to start with, and a magus's is Hermetic Magus.

**The app works out:** the line under the form gives the Virtue and Flaw points so far. Use refuses a choice that breaks the type's limits. A grog's are those of [A Grogs template](help:grog-templates). A companion's and a magus's are:

- nothing Hermetic without The Gift
- at most one Major Hermetic Virtue
- at most ten points of Flaws and five Minor Flaws
- no more Virtue points than Flaw points
- exactly one Social Status
- not the same Ability or Art named twice by the same Virtue

A Social Status that costs a point is refused here, since it leaves the Virtues a point over. Take it on the worksheet with another Flaw. Cancelling makes no character.

**What the character starts with:** those Virtues and Flaws, and nothing else, since the recipe is only the Virtues and Flaws. The character starts **In Creation**, so you finish the rest on the [Creation Worksheet](help:creation-worksheet), such as Characteristics, a childhood, Later Life, training packages, and a magus's House, apprenticeship and spells. You can change the Virtues and Flaws there too.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [How to start a character](help:guide-creation-character-new)

### A Mythic Companion template
<!-- help: mythic-companion-templates -->

A Mythic Companion's Template list has one template for each kind of Mythic Companion the books in play describe, marked with its book:

- the Definitive Edition's Devil Child, Faerie Doctor, Nephilim and Spirit Votary (Chapter 3, pp. 56-58)
- Realms of Power: The Divine's Zahid, Perfectus and Kabbalist
- Realms of Power: The Infernal's Diabolist and Summoner
- Houses of Hermes: True Lineages' Blood of Heroes
- Art & Academe's Maestro
- Against the Dark's Dragon-born and Varcolac

**Dragon-born** (Against the Dark p. 108). A zmaj's human child, one of the Magic Kin (Realms of Power: Magic p. 89). They have Greater Immunity to fire, Self-Confident, a Personal Power mirroring one of the dragon father's, and the Common Flaw. The Personal Power is Lungs of the Fish, Hands of the Fiery Beast, or one of your own. The Common Flaw is greed for gold, Avaricious, or for women, Lecherous. Second Sight sees a snake's pupils and a sheen of scales.

**Varcolac** (Against the Dark p. 122). A man who takes a wolf's shape, in one of four ways:

- born to it (Shapeshifter)
- born to it and a Lycanthrope
- taught (Skinchanger)
- a kudlak, a nightwalker of the kudlaki (Nightwalker, Versatile Phantasticum)

Good or evil, a varcolac becomes a bestial vampire on death.

**The template gives:** the Mythic Companion Virtue and every Virtue and Flaw the book says that kind must take, such as a Faerie Doctor's Dowsing, Curse-Throwing and Wise One.

**You choose:**

- which one, where the book gives a choice. Examples are a Devil Child's Demonic Might or Demonic Powers, a Spirit Votary's one Major or three Minor Supernatural Virtues, a Kabbalist's Holy Method and two Holy Powers, and the free Minor Virtue of a Diabolist, Summoner or Maestro.
- each Flaw the book allows "or a suitable substitute" for, starting with the book's own
- anything the Virtues name, such as the spirit of a Spirit Votary's Spiritual Pact
- **Another Virtue** and **Another Flaw**, more of the player's own, from the books in play. Each point of Flaws allows two points of Virtues, plus the free Minor Virtue. So a Nephilim, Zahid or Kabbalist needs about five points of Flaws to pay for what the book requires.
- **The book's minimum Abilities**, ticked. These are the scores the book says the character should start with (90 xp for a Zahid), put on the [Creation Worksheet](help:creation-worksheet) as xp. Untick it to spend the xp yourself. Where they leave a name to you, such as a Spirit Votary's local Area Lore, the form asks for it.
- the **Social Status**, where the book doesn't fix it

**The app works out:** the line under the form gives the Virtue points so far against what the Flaws allow, and the Flaw points. Use refuses a choice that breaks a Mythic Companion's limits:

- exactly one Mythic Companion Virtue
- no Gift and nothing Hermetic
- at most ten points of Flaws and five Minor Flaws
- no more Virtue points than twice the Flaw points plus one
- nothing taken more often than the book allows

The Biography notes the template, its book's advice and where the app differs from the book. The Hebrew of a Nephilim or Kabbalist is taken as Dead Language: Hebrew, and a Perfectus's Church Lore as Organization Lore: Church.

The Definitive Edition's Perfectus is a Minor Social Status for an ordinary companion. The Perfectus template is Realms of Power: The Divine's Mythic Companion, a separate Virtue. The character starts **In Creation**, and the worksheet does the rest.

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws)

### A supplement's character
<!-- help: companion-sample-templates -->

The Template list also has the ready-made characters the supplements in play print, marked with their book. A named one is listed by its role, then its name, so you can tell what it's for, such as Bachelor of Arts at Paris - Gilpatrick (A&A), Guild Master Clothier - Doolin (C&G) or Hound of God - Rothiger (HMRE). One the book leaves unnamed is listed by its role alone, such as Mystic Nun (TC). The Definitive Edition's templates start In Play, but these start **In Creation**, so the worksheet checks them against the rules.

- **Companions**, among them:
  - Art & Academe's Leonardo Fibonacci, Gilles de Corbeil, Brogo the Dwarf, Brother Julian and Gilpatrick
  - City & Guild's Julian, Obano, Doolin and Banco
  - The Church's Mystic Nun, Anne, the Imposter, a Templar Commander and Templar Brother-Priest (pp. 126-127), and the first Franciscans, Francis of Assisi, Brother Elias and Clare of Assisi
  - the companions of Realms of Power: The Divine and other books
- **Grogs**: The Church's grog templates, the Anchoress, the Beguine and the Priest's Wife (pp. 83-84), and a Franciscan Nun and Friar (p. 142). They're on a grog's list and held to a grog's limits.
- **For the storyguide**: a saint or an antagonist the book prints for the storyguide is marked "for the storyguide". Examples are Francis and Clare of Assisi, or The Church's diabolist abbot Father Tino of Gradara (p. 97), a Mythic Companion. It's taken as the book prints it, so Use doesn't hold it to its type's limits.

**You choose:**

- **The book's Virtues and Flaws**, ticked. Untick one to leave it out.
- **Another Virtue** and **Another Flaw**, more of your own, from the books in play.
- **The book's Characteristics**, ticked. Untick them to buy your own on the worksheet.
- **The book's Abilities**, ticked. These are the character's Abilities and specialties, put on the worksheet as xp (Native Language, a Virtue's own xp, Early Childhood, then Later Life). Where the book leaves a name to you, such as an Area Lore's area or a language, the form asks for it.
- the **Social Status**, from the book's

**The app works out:** the line under the form gives the Virtue and Flaw points, and the xp a character has at the book's age against what its Abilities come to. Use refuses a choice that breaks its type's limits, a companion's, a grog's or a Mythic Companion's, as for [Quick and Easy Virtues and Flaws](help:quick-virtues-flaws). A storyguide's character is the exception. Fewer Virtue points than Flaw points is allowed, since some books leave a companion a few points short for the player to fill. The character's age sets the year born, and its Personality Traits and Reputations come with it. The Biography notes the book's advice and where the app differs from the page, such as an older edition's Ability (Church Lore taken as Organization Lore: Church).

**See also:** [New Character](help:character-group-new), [Creation Worksheet](help:creation-worksheet), [A Grogs template as a companion](help:grog-template-companion)

### A Grogs template as a companion
<!-- help: grog-template-companion -->

Grogs says any of its grog templates can be played as a companion simply by adding a Story Flaw (Chapter 7, p. 95, and the "as Companion" notes of many templates). While Grogs is in play, a companion's Template list has each one, marked "(Grogs, as a companion)".

It asks for the same choices as [A Grogs template](help:grog-templates), with two differences:

- The choices are held to a companion's limits rather than a grog's, so Major Virtues and Flaws and up to ten points of Flaws are allowed.
- Next refuses until a **Story Flaw** is among them. Choose one under **Another Flaw**, such as Dark Secret or Visions.

The character is made a companion, without the Loyal +1 a grog gets, and the Biography notes it.

**See also:** [A Grogs template](help:grog-templates), [A supplement's character](help:companion-sample-templates), [New Character](help:character-group-new)

### Animal grogs
<!-- help: animal-grogs -->

A grog can be an animal: a horse, a hound, a hawk or any other beast that serves the covenant (Grogs, Chapter 7, Grog Templates, Horses & Hounds, pp. 133-137). Make one from an animal template on the New Character form, or make a grog with no template and choose **Animal form** on its worksheet's Concept step.

**You choose (Animal Form):**

- **Kind**: a person, or a Clawed Beast, a Hoofed Beast, a Bird, or a Fish or Serpent. Each kind has its own aging, and its own penalties with humans to Presence and Communication. They're Clawed Beast -2/-5, Hoofed Beast -4/-5, Bird -1/-2, and Fish or Serpent -5/-6.
- **Species**, such as Dog or Horse, and its **Language**, the animal language it speaks. That's its species' unless you name another.
- **Lifespan**: blank for the kind's own, or a species' own lifespan in years.
- **Size**, from -3 to +2. Strength gets +2 for each point of Size and Quickness loses one, added after the Characteristic points are spent.

From an animal template you also choose its age (Dog 1 or 4, Horse 3 or 10, Hawk 8), its Social Status and its Virtues and Flaws from the book's suggested ones, as for [A Grogs template](help:grog-templates).

**The rules the worksheet checks:**

- An animal takes **Restricted Learning**. **No Hands** and **Mute** are part of its form and cost nothing. Its Social Status is Domestic Animal, Wanderer or Companion Animal, and a Companion Animal starts with Loyal to Master +1. A Major Personality Flaw counts as Minor. Nothing about human society can be taken, such as a Craft, Educated or a noble's status.
- **No Early Childhood and no Native Language.** The **Pre-adult Life** step takes their place. It gives the animal Language at score 2, and 120 xp spent up to the age it's grown, then 15 xp a year in Later Life. Restricted Learning puts the xp on at most five Abilities, and the animal Language is never raised.
- **A human Language** is learnt with a Source Quality of 4 + Cunning, lower for a negative Cunning. Animal Ken is never above its animal Language. On its sheet, Intelligence reads Cunning.
- **No training packages.** The Ability cap is that of a person of the same share of a human life. That's advice, since the book says it "might" apply.
- **Aging**, by kind:
  - a clawed beast is grown at 1 and ages from 6. It makes five aging rolls a year, one each season and two in Winter, with +1 to the roll every 2 years.
  - a hoofed beast is grown at 3 and ages from 20, with two rolls a year (Summer and Winter) and +1 every 5 years.
  - a bird is grown at 8 and ages from 55, with a roll every second year and +1 every 15 years.
  - a fish or serpent is grown at 24 and ages from 170, with a roll every fifth year and +1 every 50 years.
  - a different lifespan scales the figures by 50 / lifespan. The rolls are made as the seasons pass.

An animal grog can be put on the covenant's Horses or Hounds list, in its Covenfolk.

**See also:** [A Grogs template](help:grog-templates), [Creation Worksheet](help:creation-worksheet), [Hounds](help:section-inh-hound)

# Laboratories group
<!-- help: laboratory-group -->

<!-- tui -->
The Laboratories node under a covenant, or Unassigned Laboratories under the saga. It lists the laboratories in the tree below it. Choose one there to open its sheet.

**You type:** nothing here. `n` (New) offers New Laboratory, with this covenant already chosen.
<!-- /tui -->
<!-- gui -->
A covenant's Laboratories chapter, or Unassigned Laboratories in the saga's The Covenants chapter, shows the laboratories as cards. Click one to open its page. A card's Aura is the one its Lab Totals use, with the lab's own modifier. That's its covenant's aura, with Boons and Hooks counted, or its own place's.

**You type:** nothing here. The **New Laboratory** card at the end of the cards makes one, with this covenant already chosen.
<!-- /gui -->
The form asks for a Name, a Size and the covenant, and whether it's one of the covenant's starting labs. A starting lab is paid for from the covenant's Build Points, one free per magus.

<!-- tui -->
**The app works out:** the count in the node's label. A new laboratory starts In Creation.
<!-- /tui -->
<!-- gui -->
**The app works out:** a new laboratory starts In Creation.
<!-- /gui -->

**See also:** [Characters group](help:character-group), [Creation Worksheet](help:creation-worksheet), [How to create a character, covenant or laboratory](help:guide-creation)

# The Armarium
<!-- help: armarium -->

Every book in the saga in one list. It holds each covenant's library, each laboratory's and each character's books, and the books nobody holds, **Unassigned**. Lab texts, casting tablets and the volumes of a codex are each a row of their own, and a volume's row names its codex. An armarius is a locked book closet (Covenants p. 92), and this is the saga's.

Only the storyguide sees it, since the unassigned books are often ones the players haven't found yet.

<!-- tui -->
It's the **The Armarium** node in the tree, beside Saga Content.
<!-- /tui -->
<!-- gui -->
Open it from its card at the top of the saga page's **Compendium** chapter, beside the Custodia Mirabilium's.
<!-- /gui -->

**See also:** [The Custodia Mirabilium](help:custodia), [How to make a book or device for the players to find](help:guide-store-find), [Find](help:find)

### Books
<!-- help: tab-armarium -->

The Armarium's one list, [Books](help:section-armarium), with its filter above it and the chosen book's details below.

### The books
<!-- help: section-armarium -->

Each row is a book: its Name, Type, Subject (the Art, Ability or spell it's on) and Holder. The Holder is the covenant, laboratory or character that has it, or Unassigned.

**Filter:** choose a **Holder**, one record or **Unassigned** for the books nobody has, and a **Type**. The list's title counts what it shows, such as "Books (3 of 59)".

<!-- tui -->
**You type:** `a` adds a book with no owner, and `e` and `d` edit and delete the chosen one, in the same form as a library's. More's **Give** hands the chosen book to a covenant, laboratory or character.

Mark books with Space or Ctrl+click to act on them together. With books marked, `e` gives them all one new owner and `d` deletes them all, each after a confirmation.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** makes a book with no owner, and **Edit** and **Delete** act on the chosen row, in the same form as a library's. **Give** hands the chosen book to a covenant, laboratory or character. **Change Owner** gives several of the books listed one new owner at once.
<!-- /gui -->

Give on an unassigned book writes only the receiver's Diary ("Received ..."). On a held book it's the usual Give, in both Diaries. To take a book away from its holder, edit its Owner to "(none - unassigned)", and nothing is written in a Diary. A book bound in a codex takes its whole codex with it, and the form says so. Deleting a held book names its holder first.

Books imported from a CSV file on the saga land here, unassigned.

**The app works out:** the count, who holds each book, and the chosen book's details, with its holder a link that opens it.

**See also:** [Library tab](help:tab-cov-library), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# The Custodia Mirabilium
<!-- help: custodia -->

"The keeping of wonders": every enchanted device in the saga in one list. Each is held by a covenant, a laboratory or a character, or by nobody, **Unassigned**. Only the storyguide sees it.

<!-- tui -->
It's the **The Custodia Mirabilium** node in the tree, beside Saga Content.
<!-- /tui -->
<!-- gui -->
Open it from its card at the top of the saga page's **Compendium** chapter, beside the Armarium's.
<!-- /gui -->

**See also:** [The Armarium](help:armarium), [How to make a book or device for the players to find](help:guide-store-find), [Find](help:find)

### Enchanted Devices
<!-- help: tab-custodia -->

The Custodia's one list, [Enchanted Devices](help:section-custodia), with its filter above it and the chosen device's details below.

### The devices
<!-- help: section-custodia -->

Each row is a device: its Name, Type (Invested, Lesser, Charged or Talisman), its first Effect and how many more ("+2 more"), and its Holder, or Unassigned. The details list every effect.

**Filter:** choose a **Holder**, one record or **Unassigned**, and a **Type**.

<!-- tui -->
**You type:** `a` adds a device with no holder, and `e` and `d` edit and delete the chosen one, in the same form as on a holder's sheet. More's **Give** hands the chosen device to a covenant, laboratory or character.
<!-- /tui -->
<!-- gui -->
**You type:** **Add** makes a device with no holder, and **Edit** and **Delete** act on the chosen row, in the same form as on a holder's page. **Give** hands the chosen device to a covenant, laboratory or character.
<!-- /gui -->

Effects are instilled, used and charged on the holder's page. Give, taking a device away (its Holder set to "(none - unassigned)") and Delete work as on [the Armarium's books](help:section-armarium).

A talisman given away or set down keeps its Talisman mark. The rules say only the magus who prepared an item can attune it, and that they always keep an Arcane Connection to their talisman, which makes it dangerous in an enemy's hands (DE p. 259). Whether it's still their talisman in other hands, and whether it can be attuned again, is the troupe's call.

**The app works out:** the count, who holds each device, and the chosen device's details and effects, with its holder a link that opens it.

**See also:** [Enchanted Devices](help:section-char-devices), [Give](help:give)

# Seasons
<!-- help: seasons -->

The saga's record of past seasons: what everyone did each season and what it gave them. A record is added each time a season is applied with [Advance Season](help:advance-season), as long as Keep season records is on in the saga's settings.

**You type:** nothing. The app writes the records.

<!-- tui -->
**The app works out:** what's waiting on you, in [Needs You](help:section-attention), and what's coming, in [Looking Ahead](help:section-ahead). Then one row per season recorded, newest first, such as "Spring 1220 (3 people)", and below the list the chosen season's record, grouped by covenant.
<!-- /tui -->
<!-- gui -->
**The app works out:** the Seasons page, opened from the saga's Seasons chapter (The Seasons Played). It starts with what's coming ([Ahead](help:section-ahead)) and what's waiting on you ([Needs You](help:section-attention)). Its rail lists the seasons, newest first, and it shows the chosen season's record grouped by covenant, a row a person. Just after Advance Season, the season just played out is first. The page's title carries the present season's medallion, and each season's heading its own, in the saga's set of medallions.
<!-- /gui -->
Each person's line gives the activity, what it was on and its result. A plan that couldn't be carried out says why, and a magus or companion with nothing planned shows "nothing planned". Winter's lines also include aging rolls, grogs' yearly updates, business upkeep and vis harvests.

When season records are off, the page says so and no new seasons are added. Each character's Diary still has their own entry.

**See also:** [Advance Season](help:advance-season), [Season Summary](help:season-summary), [How to plan and run a season](help:guide-seasons)

## The Seasons panel
<!-- help: section-seasons-info -->

The date, how far Ahead looks, the next Tribunal's meeting, how many things come this season, and how many are waiting on you (Needs you).

**You type:** how far to look ahead, a number of years or to the next Tribunal, and what to show, with
<!-- tui -->
Edit (`e`).
<!-- /tui -->
<!-- gui -->
**Looking ahead** on the Ahead section.
<!-- /gui -->
Both are kept with the saga. Looking ahead starts at 2 years.

## Seasons
<!-- help: tab-seasons -->

What's waiting on you and what's coming, season by season, over the seasons already recorded.

## Needs You
<!-- help: section-attention -->

What in the saga is waiting on the storyguide, gathered from every part of it. Nothing here is kept as a list. Each part of the saga is asked when the list is shown, so a row goes as soon as you deal with it.

- **Revisit**: an open story whose Revisit year has come (marked).
- **Open story**: every other open Story Event of the troupe's covenants, oldest first (see [Open Stories](help:section-region-stories)).
- **Describe**: a creation an experiment changed whose experimental effects you haven't described yet. That's a side effect or a special result with no words, or a modified effect that changes nothing the app works out.
  - A spell is opened through a magus who knows it, since its Mastery form holds its effects.
  - An enchanted item's effect is opened through its holder, and a bond power through its familiar.
- **Overdue**: a dated stage of a threat still Pending after its season has passed (marked). Record what became of it on the threat's Stages, or [Delay or Hasten](help:threat-delay) the threat.
- **Spotlight**: a player character with a Story Flaw or a Major Personality Flaw that no told (Resolved) story has concerned for the saga's **Story Flaw spotlight** span.
  - The span is 3 years unless changed in the saga's settings, and 0 turns it off.
  - Such a Flaw is a promise of stories (DE p. 66), so any story about the character counts, whichever Flaw it drew on.
  - A character no told story has concerned yet is counted from the first season the saga recorded.
- **Teach?**: a student's open ask for another Player's character to teach them (see [Teaching Requests](help:teaching-requests)).
- **Close**: a chapter with a cast whose aftermath hasn't been asked. Its Take Up step opens [Close the Chapter](help:close-chapter).
- **Away**: an open story about a character none of whose Players is coming to the next planned [Session](help:tab-content-sessions). It's only advice. Keep the story for another evening, or play the character another way. A character everyone in the troupe plays is never named, and nothing shows until the Session says who's coming.

**You type:** nothing here. Choose a row to read what it needs and where.
<!-- tui -->
Edit (`e`) opens the record it's dealt with on.
<!-- /tui -->
<!-- gui -->
**Open** goes to the record it's dealt with on.
<!-- /gui -->

**See also:** [How to clear what needs you](help:guide-needs-you)

## Looking Ahead
<!-- help: section-ahead -->

What's coming in the seasons ahead, from this one to the end of the span, a season at a time. Nothing here is kept as a list. Each part of the saga is asked what it has coming.

- **Tribunal**: each Tribunal's next meeting, and the season notice of its open cases is due.
- **Neighbours** and **Income**: each town's fairs and markets. A fair a covenant trades at is its income roll.
- **Places**: each place's dated triggers.
- **Threats**: a threat's dated stages still to come.
- **Characters**: the year a character's aging rolls begin, and the season one comes back from Twilight.
- **Every Winter**: the world turns, the yearly step.
- **Calendar**: your own entries, once, each year or every so many years, for the whole saga or one covenant.

**You type:** your own calendar entries. Add one, and Edit or Delete it. A row worked out from another record is changed on that record, and Edit and Delete say where.
<!-- tui -->
Show (Edit on the Seasons panel) narrows the list to one kind of entry.

More (`m`) > [Travel](help:travel) works out a journey.
<!-- /tui -->
<!-- gui -->
The chips under the title narrow the cards to one kind of entry. Click a card to read it in the Inspector. [Travel](help:travel) is in Undertakings, below.
<!-- /gui -->

## Undertakings
<!-- help: section-undertakings; gui -->

Below Ahead on the Seasons page and on a covenant's Seasons chapter: what the troupe sets out to do besides the seasons' plans. Each button sits beside a line saying what it does. [Travel](help:travel) works out a journey, and The Hunt and Area Lore hunt and seek along the road. On a covenant, **Begin Project** starts one of its great works of Hermetic Projects (see [Hermetic Projects](help:tab-cov-projects)).

## Travel
<!-- help: travel -->

<!-- tui -->
On Ahead, the Seasons page's or a covenant's, More (`m`) > **Travel** works out a journey.
<!-- /tui -->
<!-- gui -->
In [Undertakings](help:section-undertakings), **Travel** works out a journey.
<!-- /gui -->
Choose **From** and **To**, from the saga's covenants, towns and places, then how the distance is **Measured**. The Atlas is the desktop's. When From and To are both on one of its maps that has a scale, choosing them fills in the **Miles**, as the crow flies, and sets Measured to Direct distance. The divisors below then allow for the winding way. Otherwise type the miles as measured on the troupe's map.
<!-- gui -->
See [Scale and distance](help:atlas-scale).
<!-- /gui -->

- **Direct distance, as the crow flies**, as you'd measure it on a map. Road travel takes the miles / 12 days, a barge / 8 with the current and / 6 against it, and a ship / 60 (City & Guild p. 89, the river figures as the errata corrects them, p. 57).
  - These already allow 20% for winding roads and rivers.
  - A route that's mostly road or mostly river counts as all one. Otherwise work out each leg on its own and add them.
  - On foot or on your own horses, the 20% is added to the miles first.
- **Route length, along the road or river**, at each way's miles a day (City & Guild p. 85):
  - barges 8 to 10, 10 with the current and 8 against
  - carts 15 to 25
  - packhorses about 24
  - coaches 18 to 24
  - a courier about 30
  - a rider with remounts up to 90
  - on foot, the Definitive Edition's 20 miles a day (p. 408), since City & Guild gives no walking speed
- **Between named ports**, the Naval Trade Tables (City & Guild pp. 89-90) give the days directly. They go through the junctions between Europe's regions, inland travel to the named city included.

Name **Who goes**, from the saga's characters. **Travellers** counts them and any others you add to it. Add the **Cargo, in tons**, and tick **A known magus travels** and, on land, **Travel quickly**.

**The Journey** shows the days, how they were worked out, and City & Guild's words for the way you travel. It also gives the Definitive Edition's figure as a rough guide (p. 408): ships about 30 miles a day, good ones three or four times that, a cart 20, and a courier 30, or 50 if urgent. Where the two books differ, the days are City & Guild's.

The cost is passage with a merchant or a captain (City & Guild pp. 85-86). By sea it's a pound a fortnight for a party of eight in about a ton of space with their food, or half a ton hugging the coast. It's counted by the day, with the cargo's own tons. River travel costs twice that, and road travel 8 to 20 times. A known magus pays double aboard a ship or barge, if a captain will take them at all (p. 85). On foot or on your own horses the book has no figure, since food, tools and lodging have no rate (p. 86).

Travelling quickly costs one Long-Term Fatigue level for each day on the road (Definitive Edition p. 408). Delays for terrain and weather still cost it, but waiting on toll collectors doesn't. A forced march of five days leaves the travellers Unconscious. The app's reading: the nights of the march restore nothing, and each night's rest afterwards without hurrying restores one level (p. 404). A courier who hurries rides at the urgent 50 miles a day, and a rider with remounts is always hurrying.

**Close** leaves it as a what-if, and nothing is recorded. **Set Out** makes the journey in one click:

- a Travel line in each traveller's Diary, with from, to, how, the days and the cost
- the forced march's Long-Term Fatigue on each of them, if Travel quickly is ticked
- their arrival in the saga's calendar, so it shows on Ahead. A season is taken as 13 weeks, so a journey of 91 days or more arrives a season later.

Set Out needs someone named in Who goes and a journey it can work out.

<!-- tui -->
**The Hunt** and **Area Lore** sit beside Travel, for the road.
<!-- /tui -->
<!-- gui -->
**The Hunt** and **Area Lore** sit beside Travel in Undertakings, for the road.
<!-- /gui -->
A hunt on the road first needs a hunting spot, found with the party's best Intelligence + Area Lore against 6 (City & Guild p. 83). With no huntsman named, the hunters quest and lay the relay themselves. Game in a lord's chase, warren or forest is poached, and fiercely punished (Lords of Men pp. 48-49). Otherwise both work as on a manor (see Manors). Area Lore finds roads, fords, inns, hazards and people along the route by the book's Ease Factors.

## The World Turned
<!-- help: section-world-turns -->

Each Winter's yearly step, newest first: what was applied when the world turned ([The World Turns](help:world-turns)). Delete one to undo its changes. A value changed by hand since is left as it is.

## Seasons Recorded
<!-- help: section-seasons-recorded -->

The seasons applied so far, newest first. The chosen season's record is shown
<!-- tui -->
in the details panel.
<!-- /tui -->
<!-- gui -->
in its chapter.
<!-- /gui -->
See [Seasons](help:seasons).

# Saga Content
<!-- help: saga-content -->

One place for what this saga's pickers offer: the books in play and the saga's own sources, the shared catalogs and the single entries it hides, its House Rules, its own spells and, for the storyguide, its players.
<!-- tui -->
Choose **Saga Content** in the tree, under Seasons. The tabs open with `1` to `5`.
<!-- /tui -->
<!-- gui -->
Open it from its card under **Content in Play** on the saga page's [Saga Settings](help:saga-settings). A player, who has no Saga Settings, finds the card at the top of the [Compendium](help:saga-compendium). Its chapters, Books, Catalogs, House Rules, Spells and Players, are described below. Click a row or card to see it in full in the Inspector.
<!-- /gui -->

**You type:** what each part below describes. The catalog files the app ships with are never changed, so hiding something here affects only this saga.

<!-- tui -->
**The app works out:** what every picker in the saga offers. An entry from a book out of play, or one hidden here, is left out of the pickers, and `F3` in a picker shows it, marked. An entry already on a character, laboratory or covenant stays there.
<!-- /tui -->
<!-- gui -->
**The app works out:** what every picker in the saga offers. An entry from a book out of play, or one hidden here, is left out of the pickers, and **Show everything** in a picker lists it, marked. An entry already on a character, laboratory or covenant stays there.
<!-- /gui -->

**See also:** [The saga](help:saga), [The workspace](help:workspace), [Getting started](help:guide-getting-started)

## Books
<!-- help: tab-content-books -->

The sourcebooks the saga uses, and the saga's own sources.

**You type:** which books are in play, and the saga's own sources.

**The app works out:** what each book in or out of play switches on or off, and how many House Rules cite each source.

### Books in Play
<!-- help: section-books-in-play -->

<!-- tui -->
Every sourcebook, with whether it's in play. `e` opens the picker of books, where you tick the ones your troupe uses. The core book is always in play.
<!-- /tui -->
<!-- gui -->
Every sourcebook as a card, with whether it's in play. The core book comes first, then the supplements under the book lines they belong to, then the saga's own sources. The book lines are:

- The Order, with Houses of Hermes first and then The Order at Large
- Realms of Power
- Tribunals
- Mythic Europe
- The Lands Beyond
- Non-Hermetic Magic
- Scenarios
- Transforming Mythic Europe

A book line's books that the app doesn't have yet are left out until it does.

Each card says what its book brings. That's how many Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, spells, Shapes & Materials and Goods it adds to the catalogs, and how many optional rules, season activities, kinds of book and traditions. A saga source counts the saga's own entries that cite it. A book the app has nothing from yet says so. A book out of play is drawn faded.

Click a supplement's **In play** or **Not in play** chip to put it in play or take it out. The chapter's count changes with it and the saga is saved. The core book's **Always** chip can't be clicked, since it's always in play. **Edit** opens the picker of books, to tick many at once. Click a card itself to see the book in the Inspector.
<!-- /gui -->

A book's details give a short overview of it, how much it holds, and its special rules. Those are its optional rules by name, and for a supplement its season activities, kinds of book and traditions. A saga source's details give what it holds and what cites it.

While a book is out of play, everything it adds is switched off:

- The pickers leave out its Virtues, Flaws, spells and other entries.
- The season plan leaves out its activities. A plan already made keeps its activity.
<!-- tui -->
- Its optional rules are left off by Edit Saga and count as off. The choice is kept for when the book comes back.
<!-- /tui -->
<!-- gui -->
- Its optional rules are greyed out on Saga Settings and count as off. The choice is kept for when the book comes back.
<!-- /gui -->
- The library's book form leaves out its kinds of books and their fields. A book already using one keeps it.

A covenant Library's research bonuses need Covenants.

### Saga Sources
<!-- help: section-saga-sources -->

Sources of the saga's own, such as a house-rules list or a fan supplement, that its House Rules, spells, goods and Mystery Cults can cite. A whole set of homebrew then goes in or out of play at once (see [How to keep homebrew in a source](help:guide-homebrew-source)).
<!-- tui -->
`a` adds one, with an Abbreviation and a Title. The Abbreviation is short, like a book's, and not one a sourcebook already uses.
<!-- /tui -->
<!-- gui -->
**Add** adds one, with an Abbreviation and a Title. The Abbreviation is short, like a book's, and not one a sourcebook already uses.
<!-- /gui -->
A new source starts in play, and goes in or out of play with the books above.

<!-- tui -->
`e` edits a source, and a new abbreviation is carried to everything that cites it. `d` won't delete a source anything still cites (a House Rule, a spell, a good or a cult), and the message names them.
<!-- /tui -->
<!-- gui -->
**Edit** edits the source last clicked, and a new abbreviation is carried to everything that cites it. **Delete** won't delete a source anything still cites (a House Rule, a spell, a good or a cult), and the message names them.
<!-- /gui -->
Its Entries column counts them all, and its card under Books in Play says what it brings.

### Traditions Offered
<!-- help: section-traditions -->

The non-Hermetic magical traditions, listed by book in the order of Books in Play, and whether the saga offers each. They're Hedge Magic Revised Edition's six, and those of the Realms of Power, Societates, the Tribunal and regional books, Rival Magic and Ancient Magic.

Every tradition of a book in play is offered until you turn it off, so a book put in play brings its traditions with it. Turn off the ones your saga doesn't use. A tradition citing two books is listed under the first of them in play. A character can join a tradition the saga offers, which gives them [a place on their sheet](help:tradition-chapter) for its Arts and Abilities.

<!-- tui -->
Each tradition's row says whether it's offered. One whose book is out of play is dimmed and marked "(book not in play)". `e` opens a tick for each tradition of the books in play. Untick the ones the saga doesn't offer.
<!-- /tui -->
<!-- gui -->
The **Traditions** chapter has a heading for each book, saying whether the saga offers All, Some or None of its traditions. Its switch offers them all, or none when all are offered. Under it each tradition is a card of two lines, its name and switch, then its kind of tradition. Flip the switch to offer that one or stop. Click the card to see the tradition and what it adds in the Inspector, with a switch at the top right. A book out of play has its cards greyed out and their switches off. Put the book in play on Books in Play to offer them.
<!-- /gui -->

A tradition's kind is one of Hedge Tradition, Ex Miscellanea Tradition, Mystery Cult, Faerie Tradition, Holy Tradition, Infernal Tradition, Rival Tradition or Ancient Tradition. Its realm follows only when that's new information. A Holy Tradition is Divine and most others are Magic, so "Ancient Tradition · Faerie" names a realm and "Hedge Tradition" doesn't. A tradition whose magic can belong to several realms lists them. A sahir's Sihr is usually Magic, and a character's own version is chosen on their **Traditions** form (see [A tradition's chapter](help:tradition-chapter)).

Turning a tradition off, or taking its book out of play, stops it being offered. Characters who already belong to it keep it on their sheet, and the choice is kept for when the book comes back. A saga from before traditions were offered by default offers every tradition of its books in play, as a new one does.

## Catalogs
<!-- help: tab-content-catalogs -->

The shared catalogs the pickers draw on, and what this saga leaves out of them.

**You type:** whether each catalog is offered, and the single entries to hide.

**The app works out:** each catalog's number of entries and of hidden ones.

### The catalogs
<!-- help: section-catalogs -->

The Virtues & Flaws, Laboratory Virtues & Flaws, Boons & Hooks, Abilities, Spells, Shapes & Materials and Goods catalogs.
<!-- tui -->
`e` offers a whole catalog or not.
<!-- /tui -->
<!-- gui -->
**Edit** offers a whole catalog or not.
<!-- /gui -->
A catalog not offered leaves its pickers with only the saga's own entries, its House Rules or own spells.

### Hidden Entries
<!-- help: section-hidden-entries -->

Single entries this saga's pickers leave out, as if their book were out of play.
<!-- tui -->
`a` asks which catalog, then which entry to hide. `d` offers the chosen one again, after a confirmation.
<!-- /tui -->
<!-- gui -->
**Add** asks which catalog, then which entry to hide. **Delete** offers the entry last clicked again, after a confirmation.
<!-- /gui -->

## Goods
<!-- help: tab-content-goods -->

What goods cost in Mythic Europe. It holds every row of City & Guild's Prices of Goods table and its Price List of common goods (C&G pp. 141-142 and p. 144), and any goods of the saga's own.

**You type:** goods of the saga's own, and purities of the goods priced by purity.

**The app works out:** a common good's price at each quality, a purity's price from its metal content, and what a gemstone or pearl costs an ounce.

### The goods
<!-- help: section-content-goods -->

The commodities come first, by class: bulk, manufactured and luxury goods (C&G p. 134). Their four prices, Shoddy, Standard, Superior and Expensive, are Mythic pounds a tun or ton, as the book prints them. There's no Excellent column. The marks are:

- `#` means none to be had at that quality
- `*` means priced by purity
- `250*` is one purity's price
- `n/a` is as printed
- a blank is where the book has none (Dye's Superior)

Goods the book doesn't sell by the ton are still priced by the ton for comparison. Sold by says how they're sold, such as wine by the tun, gemstones and pearls by the ounce, gold by the pound, silk by the roll, and horses and slaves by the head.

The common goods follow, at their standard price each (C&G p. 144). Their details give the other qualities by the book's multipliers: Shoddy x0.5, Superior x2, Excellent x5, Wondrous x5 or more. The book means these prices for story flavour, not for merchants' or crafters' incomes (p. 143). Selling finished items is a separate roll (Presence + Bargain, Chapter IV).

A good's details show its class and page, its prices, how it's sold, its purities, where it's bought in bulk (the commercial sources, pp. 138-140) and the book's note on it. The weights are 16 ounces to the pound and 2,240 pounds to the ton, as the errata corrects p. 140 (errata p. 57).

- **Silver** stays 2,420 a ton as printed, since the table is built on it (gold's 24,200 is ten times silver, p. 141). Its 250*, 1,650* and 2,200* are prices at lesser purities, about 10%, 68% and 91% silver.
- **Priced by purity** are alum, copper, gold, iron, lead, saffron, salt, silver and tin. A lesser purity's price is the pure price times its metal content (p. 140). Alum's three prices are its three kinds instead, salt-adulterated, European and Asian, with no Expensive (p. 134).
- **Gemstones and pearls** show their price an ounce by column. That's the table's price over the 2,420-pound ton it's built on, which matches the book's 2 and 2 1/2 pounds an ounce for average and fine gems. Pearls are 2 an ounce from rivers and 3 from the sea (p. 141).

<!-- tui -->
`a` adds a good of the saga's own, of one of two kinds:
<!-- /tui -->
<!-- gui -->
**Add** adds a good of the saga's own, of one of two kinds:
<!-- /gui -->

- a commodity, priced a tun or ton by quality, with its class, how it's sold, its four prices and, if it's priced by purity, its pure price
- a common good, priced each in pence (12 to the shilling, 240 to the pound, p. 143), with where it's bought and a description

<!-- tui -->
`e` edits one of the saga's own goods, and a catalog good is read-only. `d` deletes one of the saga's own goods, or hides a catalog good after a confirmation. The Catalogs tab's Hidden Entries offers it again, and Catalogs can switch the whole Goods catalog off. More's **Add a Purity** (`m`, then `p`, for a good priced by purity) adds a purity by its name and metal content, with its price worked out as you type. It also removes one the saga added.
<!-- /tui -->
<!-- gui -->
**Edit** edits one of the saga's own goods, and a catalog good is read-only. **Hide** deletes one of the saga's own goods, or hides a catalog good after a confirmation. The Catalogs chapter's Hidden Entries offers it again, and Catalogs can switch the whole Goods catalog off. **Add a Purity**, for a good priced by purity, adds a purity by its name and metal content, with its price worked out as you type. It also removes one the saga added.
<!-- /gui -->

A good of the saga's own can cite one of the saga's sources, its **Source**, once the saga has one. While that source is out of play, the good is marked "(not in play)".

## House Rules
<!-- help: tab-content-house-rules -->

The Virtues, Flaws, Boons and Hooks made for this saga, and its own Abilities. They're house rules, or entries from books the app's catalogs don't carry, and they show in the pickers alongside the catalog's entries.

<!-- tui -->
**You type:** with `a` and `e`,
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**,
<!-- /gui -->
what the entry is For, which is fixed once the entry is made. That's a Character Virtue or Flaw, a Laboratory Virtue or Flaw, a Covenant Boon or Hook, or an Ability. Then its Name, Type, Tier, Category, whether it can be taken more than once, what it Asks for, a Description and, once the saga has sources of its own, the Source it comes from.

**Asks for**, on a character's or covenant's entry only, lists what's chosen when the entry is taken, comma-separated, as the books' Puissant asks for an Ability. For a Vis Source Boon, say, it's "Form". Characteristic, Ability, Art, Technique, Form, Realm and Blood are chosen from a list, and anything else is typed. Put a choice in the name in braces to show it there: "Vis Source ({form})" shows as "Vis Source (Aquam)". Otherwise it follows the name in brackets. What was chosen can be changed later with Edit on the Virtue, Flaw, Boon or Hook.

**An Ability** is one the saga adds beside the catalog's, most often a Supernatural Ability designed for a tradition of House Ex Miscellanea or a storyguide's character (Houses of Hermes: Societates pp. 103-106). You give:

- its Name
- its Category, Supernatural unless you choose another
- for a Supernatural one, its Realm, Magic unless it belongs to another realm
- the Characteristic it Rolls with, or blank for the storyguide to choose each time
- whether it's Accelerated, on the Art table, for Ease Factors like Mights or spell levels. Puissant gives it +2 and it isn't studied from vis (Societates p. 104). Errata p. 60 adds that it isn't limited at creation.
- a Description
- when adding, whether to Add its Virtue

A designed Ability is a Major Supernatural Virtue's (p. 104), and a Virtue of the Ability's name grants it. So Add its Virtue also makes that Supernatural Virtue among the saga's own, unless a Virtue of that name is already offered. **Its Virtue is** Major unless you choose Minor, since the Definitive Edition has Minor Virtues that grant an Ability too, such as Second Sight (DE p. 106). Write in the Description what it does. By the book, three of its Range, Duration, Target and base effect are fixed. The fourth grows with its score, or with the Ease Factor reached when it affects other beings.

**The app works out** for an Ability, all from Houses of Hermes: Societates p. 104:

- its Casting Total, Characteristic + Ability + aura + die, against the storyguide's Ease Factor
- its Penetration, Casting Total - Ease Factor + Penetration bonus
- its level as a spell, 5 x its score, or its Casting Total when Accelerated
- its vis limit, up to its score in pawns, each pawn +1 and a botch die
- who holds it

Renaming an Ability renames it on every character, familiar and creature holding it, and renames its Virtue.

**The app works out** for a Virtue, Flaw, Boon or Hook: the points from its type and tier (Free 0, Minor 1, Major 3), with Flaws and Hooks giving points rather than costing them. Its details say who holds the entry. An entry citing one of the saga's sources is offered only while that source is in play, and one citing none always is.

### The house rules
<!-- help: section-house-rules -->

<!-- tui -->
The list of the saga's own entries, with the details panel below it. Once the saga has a source of its own, More's **Move to Source** (`m`, then `s`) makes several entries cite one source, or none, at once. Choose the source, then tick the entries, each listed with the source it cites now.
<!-- /tui -->
<!-- gui -->
The list of the saga's own entries. The Inspector shows the one last clicked in full. Once the saga has a source of its own, **Move to Source** makes several entries cite one source, or none, at once. Choose the source, then tick the entries, each listed with the source it cites now.
<!-- /gui -->

### What house rules don't do
<!-- help: house-rules-limits -->

House rules are text only, and the rules engine applies no effects for them. Two entries of the same kind can't share a name, type and tier. Delete won't delete an entry that a character, laboratory or covenant still holds. The message names them, so remove it there first.

An Ability has no type, tier or points, and no two Abilities, the catalog's or the saga's, can share a name. Delete won't delete an Ability someone holds. Deleting one leaves its Virtue, which is deleted on its own. Whether an Ability is Accelerated can't change while someone holds it, since their score would change with it. On the desktop, its mark is its category's.

When a character, laboratory or covenant is exported, the house rules and saga Abilities it uses go with it.

**See also:** [Import Data](help:import-data), [How to import and export](help:guide-import-export)

## Mystery Cults
<!-- help: tab-content-cults -->

The saga's own Mystery Cults, invented by the troupe as The Mysteries Revised Edition pp. 18-19 has it. Each cult has its own Lore and its degrees. Each degree teaches one Mystery Virtue, and its Initiation Script is written out as its components. The Initiation season offers the cults' Scripts beside the catalog's cults, under Hedge Script.

**You type:** the cult, its degrees and their Virtues, and each degree's Script. For the cult, that's its name, its Lore, its realm, the Characteristic its Initiations add, who may join, its founder and the year, and what it is.

**The app works out:** who belongs to the cult, each degree's Target, a Script's bonus from its components, a Mystagogue's Initiation Total against it, and an experiment for a degree with no Script, or with one that falls short.

**See also:** [House Rules tab](help:tab-content-house-rules), [How to initiate a character into a Mystery](help:guide-initiation)

### The Saga's Mystery Cults
<!-- help: section-content-cults -->

Each cult the saga has invented, with its Lore, realm, founder and how many degrees it has. The storyguide creates the cult's Lore, and its founders may start with it at 0 (TMRE pp. 18-19). A Lore written as "Mystery Cult Lore: (cult)" is the catalog's own Ability. Any other name becomes a new Ability the saga adds, which characters can take like any other. Renaming the Lore renames it on every character who has it. Deleting a cult leaves its members their Lore and Virtues, and the Initiation season no longer offers its Scripts.

<!-- tui -->
`a` adds a cult, `e` edits the chosen one and `d` deletes it after asking. Choosing a cult shows its degrees and Scripts below.
<!-- /tui -->

Once the saga has a source of its own, a cult can cite one, its **Source**. While that source is out of play, no Initiation season can follow the cult's Scripts. Its members keep their Lore and Virtues.

### The chosen cult
<!-- help: section-content-cult -->

The cult's Lore, realm and founding.

- **Initiation** is the Mystagogue's Presence, or the Characteristic the cult chose, + the Lore + the Script's bonus, with no die.
- **The Lore it needs.** A probationer needs the Lore at 1 before their first Initiation, and the season holds every Initiate to that. The second and later Initiations typically need 3 (TMRE pp. 11, 13; DE p. 387). They're counted by the Initiations the character has taken, the cult's Virtues they hold, not by the degree. So a cult whose path may start anywhere isn't held to it. The season only warns when they fall short, and the troupe may go ahead.
- **Members** are worked out, not listed. One joins by gaining the cult's Lore, so a member is everyone who has it, at any score, and the founder, who may have it at 0 (TMRE pp. 11, 13, 19). One of its Virtues alone doesn't make a member, since most can be taken at creation. Each member is shown at the highest degree whose Virtue they hold. Someone with only the Lore is a probationer.
- **If anyone may join**, an unGifted Initiate needs an Ordeal in every Initiation, and their past Ordeals don't lower its Target (Hedge Magic Revised Edition p. 14).

**As a secret society.** A cult is a faction in the Order's politics too, as a Tribunal's factions are. On Add or Edit, **As a secret society: what it works for** gives its agenda. **Its attitude toward** each of the troupe's covenants, from Hostile (-3) to Allied (+3), says how it stands with them. The chosen cult's details show both.

At a Tribunal meeting, a covenant with a member among its magi leans with its cult before the debate:

- with a covenant sharing the cult that brings the case or answers it
- otherwise by the cult's attitude toward a troupe covenant that does, Warm or better with it and Wary or worse against it

The Rhine's gilds lean first, then the cult. That the members vote as one is the app's reading, not a rule, and the vote's leanings can be changed as ever.

### Degrees
<!-- help: section-content-cult-degrees -->

Each degree's name, the Mystery Virtue it teaches, its Script's bonus and its Target. Almost any Virtue may be Initiated, save those of birth or circumstance (TMRE p. 13). The saga's own Virtues are offered too. A Virtue that names something, such as an Art or an Ability, names it on the degree. The Target is 15 for a Minor Virtue and 21 for a Major one when a Mystagogue has the Virtue, and 18 and 30 when no one in the cult does (DE pp. 387-388). An Ordeal from an earlier Initiation lowers the next three Targets by 3/2/1, 6/4/2 or 9/6/3, never below 9 (TMRE p. 14).

<!-- tui -->
**Experiment on a Script** is the Mystagogue's to make, so it's in More on their own record.
<!-- /tui -->
<!-- gui -->
**Experiment on a Script** is the Mystagogue's to make, so it's on their own sheet, in the Deeds chapter under Mystery Cults.
<!-- /gui -->
It's there while they lead a cult with a degree that has no Script yet, or whose Script can't reach the Target for one of the cult's Mystagogues (TMRE p. 18). With several such cults it asks which first. It asks for:

- the Virtue
- the Mystagogue, who is them unless you choose another with the Lore at 1 or more
- the Initiate, the Mystagogue themselves or someone else, which is harder
- the bonus the proposed rite's components would give
- the Flaw of its Ordeal, if it has one
- a risk of 0 to +3

It refuses a degree whose Script already reaches the Target for that Mystagogue and Initiate.

**Roll** throws a stress die + the risk on the Extraordinary Results chart, then the validity roll. That's a simple die + risk + Intelligence + Lore against 9 + the bonus, or 15 + the bonus on another Initiate. The rite's Ordeal Flaw is suffered whatever follows, even when the rite fails. A Disaster ends it, and a second form asks for the Major Flaw the Mystagogue and the Initiate each gain.

If the rite still stands, a second form asks for the storyguide's sympathy (-5 to +5) and what the chart's results become:

- each side effect, minor flaw or minor benefit, a Personality Trait with its score ("Devoted to the cult +1")
- each major flaw, an extra Ordeal Flaw with no bonus
- each major benefit, a Virtue
- a modified effect, the different Virtue it Initiates in place of the degree's own

The Initiation Total is then the Characteristic + Lore + bonus + sympathy + risk, against the Target, lowered by the Initiate's past Ordeals as above.

If it succeeds, the degree gets its Script, replacing a Script that fell short. The Script is the rite as proposed with its Ordeal, the sympathy, the extra Ordeal Flaws, Virtues and Personality Traits, without the risk. The Initiate gains the Virtue, or the one Initiated instead, and the extra Virtues, the Personality Traits and the Ordeal Flaws. The largest of these is kept as their Ordeal. The Initiate's season isn't planned for them. A failed rite's Quests and Ordeals can't count again (TMRE p. 19).

<!-- tui -->
`a` adds a degree, `e` edits the chosen one and `d` deletes it, and its Script, after asking.
<!-- /tui -->

### The Script
<!-- help: section-content-cult-scripts -->

The chosen degree's Script, as its components with each one's bonus (TMRE pp. 15-16; DE p. 388):

- a special place at a special time, +3 (once)
- a Quest, +3, or +6 for a unique one
- a Minor Ordeal +3, a Medium +6, a Major +9, each with its Flaw
- a Minor Virtue the Major one replaces, +3
- a sacrifice of goods, +1 (once)
- a season serving the cult, +1 (once)
- something of great value, +3 to +6
- the Mystagogue's time, +3
- the rite's sympathy, -5 to +5

The Script's bonus is their sum. A component that costs the Initiate nothing makes the whole Script void (TMRE p. 16).

**Edit Script** sets how many of each kind of component the Script has, and keeps the words of the ones it keeps. Its Ordeal is the Script's first Ordeal. An experiment's extra Ordeal Flaws, which give no bonus, are kept as they are. So are the Virtue it Initiates instead, its extra Virtues and its Personality Traits, shown in the degree's details. **Mystagogue** picks someone to test the Script against, and the Rite shows that person's Initiation Total and Target. The Mystagogue isn't saved. An experiment's rite stays as one lump until its components are written out. Then set it to 0.

<!-- tui -->
On a degree with no Script, `a` writes one. Otherwise `a` adds a component, with its kind, its bonus when the troupe sizes it, its Flaw for an Ordeal, and what it is. `e` edits the whole Script, and `d` removes the chosen component after asking.
<!-- /tui -->

## Spells
<!-- help: tab-content-spells -->

Every spell the saga knows: the catalog's spells from the books in play, and the saga's own.

Some are left out until the Source filter asks for them, and are marked "(not in play)". These are spells from books out of play or hidden in Catalogs, and a spell of the saga's own whose Source is out of play. A Source is one of the saga's own sources, chosen in the spell's form once the saga has one. A magus who already knows such a spell keeps it, marked the same way on their Known Spells.
<!-- tui -->
The list stretches down to a details panel that shows the chosen spell in full.
<!-- /tui -->
<!-- gui -->
The Inspector shows the spell last clicked in full.
<!-- /gui -->

<!-- tui -->
**You type:** the saga's own spells, with `a` (add) and `e` (edit). Catalog spells are read-only, so to make your own version of one, add a spell with `a`. `d` deletes only the saga's own spells.
<!-- /tui -->
<!-- gui -->
**You type:** the saga's own spells, with **Add** and **Edit**. Catalog spells are read-only, so to make your own version of one, add a spell with Add. **Delete** deletes only the saga's own spells.
<!-- /gui -->

**The app works out:** each spell's Arts, level, Range, Duration and Target, and, in its details, its magnitude, vis cost and casting time. The section title shows how many spells are listed out of how many there are.

### The spells
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

- **Search** looks in spell names and descriptions. Every word must match.
- **Source** is one sourcebook (its spells, in play or not), "The saga's own", or "Not in play" for the catalog spells the saga leaves out.
- **Technique** and **Form** each also match a spell that has it as a requisite.
- **Ritual** is Rituals or Formulaic.
- **Level** runs from and to. General spells pass any level range.

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

The evenings of play at the table. Planned ones come first, the soonest at the top, with those that have no date yet after the dated ones. Then come the ones played, newest first. A Session need not sit in one season. A slow saga plays several in one season, and a fast one a year or more in one (DE p. 528).

<!-- tui -->
They're in Saga Content's Sessions tab. Everyone can read them, but only a storyguide adds, changes or deletes them.
<!-- /tui -->
<!-- gui -->
They're in the saga page's **Saga Management** chapter, the storyguide's. Players see the next Session and the recent ones on The Troupe.
<!-- /gui -->

<!-- tui -->
**You type:** with `a` and `e`, in two steps. First:
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**, in two steps. First:
<!-- /gui -->

- the real Date, year-month-day or blank
- whether it was Played
- the Game season and year it's set in, both optional
- its Storyguide, any Player, or blank for the saga's own
- for each Player, whether they're Coming or Away

Then **Who Played Whom**: for each character, the Player playing them that evening, or no one.
<!-- tui -->
`d` deletes a Session after a confirmation.
<!-- /tui -->
<!-- gui -->
**Delete** deletes a Session after a confirmation.
<!-- /gui -->

A character is played by one person at most each evening, though it may have several Players and a Player may play several characters. Who Played Whom comes filled in from who usually plays whom. A character goes to its Player when exactly one of its Players is coming. It's left for you to choose when two or more are, as with a shared character or one everyone plays. The characters of the Players coming are listed first.

In a solo saga, with no one in the Player role, no attendance or Who Played Whom is asked. A Session made then shows **Attendance not recorded** if the saga gains players later.

Marking a Session **Played** keeps a copy of each player character as they stand. A character's More then offers **What Changed Since the Last Session**, with their scores, spells, Virtues and Flaws, Warping, wounds, Confidence, traits and what they hold, then and now. The latest two played Sessions keep their copies. Untick Played to drop one.

**The app works out:** which Session is next, and the names as written, so a played Session still reads right after a Player or character is deleted. Deleting one takes them out of the planned Sessions only. On [Needs You](help:section-attention), it shows an open story about a character none of whose Players is coming.

**See also:** [How to plan and record a Session](help:guide-sessions), [Players](help:tab-content-players)

### Previously On
<!-- help: previously-on -->

A page to read aloud before the next Session, with what happened since the last one:

- its chapters, with who went
- the seasons played since
- what the world did each year (The World Turns)
- the threats' stages that came, were stopped or turned
- each player character's What changed

It runs from the saga's date when the last Session was marked Played. With no played Session, it covers the last four seasons.

<!-- tui -->
It's in More on the saga, **Previously On**.
<!-- /tui -->
<!-- gui -->
It's **Previously On** in the saga page's Seasons chapter, or on Saga Management's Sessions. **Print Previously On** there makes a PDF in the Scriptorum style, read as the Player view.
<!-- /gui -->

Players see it too, as the [Player view](help:player-view) shows it. That leaves out what the world did, since its lines name neighbours they may not know of, and unknown threats and non-player characters' seasons. A storyguide sees all of it. Switch to the Player view to read it aloud safely.

**See also:** [Sessions](help:tab-content-sessions)

### Cast at a Glance
<!-- help: cast-glance -->

One page of the figures the storyguide reaches for during play, for each character playing at a Session, by who played whom:

- Initiative, and Attack and Defence with their first weapon, or bare hands if none
- Soak
- Magic Resistance, for a magus with Parma Magica against their weakest Form
- Wounds, Fatigue and Confidence, score and points
- their Personality Traits
- chosen spells, those with a Mastery score and those ticked **Favourite** in their Known Spells' Mastery form

<!-- tui -->
Choose a Session in the Sessions list and press `m` for More, then **Cast at a Glance**.
<!-- /tui -->
<!-- gui -->
Choose a Session in Saga Management's Sessions and click **Cast at a Glance**. **Print the Cast** makes a PDF in the Scriptorum style, asking for the paper first and then where to save it.
<!-- /gui -->

**See also:** [Sessions](help:tab-content-sessions)

### The Chronicle
<!-- help: chronicle -->

Preview: turn on Virtual Tabletop in Settings.

A Session's record of everything rolled while it's under way. Each line has its number, its time and what happened. A roll shows every die face: each 1 that doubled, and the botch dice after a 0. Then come the modifier, the total and, when the roll had one, the Ease Factor and whether it succeeded and by how much (DE pp. 7-8). A [roll from the sheet](help:sheet-roll) shows how its modifier was made: the Characteristic, the Ability, a Specialty and any wound or Fatigue penalty. A [Table roll](help:table-rolls) made from one of the app's rolling forms shows the form, each die the host drew for it (a stress die with its doublings worked out and its botch dice, as in Stress die 1, 1, 5 → 5 × 4 = 20) and the form's own result. Each Remote seat is sent the entries its player may see, as they come, and rolls through the host.

<!-- gui -->
On the desktop, the [Chronicle pane](help:chronicle-pane) shows it as it happens, on the host's computer and at each seat, and makes [Free rolls](help:free-roll).
<!-- /gui -->

**Begin Session** puts a planned Session under way and opens its Chronicle. **End Session** marks it Played, as ticking Played does, and closes its Chronicle. The Chronicle is still read from the Session's row afterwards, but nothing more is added. Only the Session's storyguide begins or ends it, and only one Session of a saga is under way at a time. End Session isn't **End of Session** on a character's More, which gives Confidence Points for an evening of play.

Who sees each roll:

- **Public**: everyone at the Session.
- **Private**: the roller and the Session's storyguide.
- **Blind**: the number is the Session's storyguide's alone. The player of the character it was rolled for sees only that the storyguide rolled.

In troupe-style play, another storyguide at the Session counts as a player that evening. A roll that shouldn't count is **struck** by the Session's storyguide with a reason. It stays in the Chronicle, marked Struck, and no longer counts.

A **Roll request** is the storyguide's call for chosen characters to roll a Characteristic, with an Ability or none: its line names what and who, and each answer is a roll of its own beneath it. The storyguide may keep the Ease Factor to themselves: players then see their totals, and only the storyguide sees the Ease Factor and who succeeded. The storyguide may add what came of it, as one more line.

**Confidence** is spent after a roll, once you see how it fell: +3 a point, at most your Confidence Score on one roll, never on a botch (DE p. 29). Only someone who sees the roll's number and may roll for the character spends it, so a Blind roll takes none from its player. Each spend is a line of its own naming the roll and its new total. The points come off the character's sheet when the Session ends; until then the Chronicle counts what's left.

Every die is rolled on the host's computer, and the host's computer keeps the whole Chronicle in a file beside the saga, Private and Blind rolls included. The host's own window shows only what the host may see, but anyone at that computer could open the file. A saga's backups include its Chronicles. A headless host serves Remote seats as before, but the preview needs a host with the desktop app until 5.0.

<!-- tui -->
Choose a Session in the Sessions list and press `m` for More. **Begin Session**, **End Session** and **Chronicle** are there while the preview is on in the desktop app's Settings.
<!-- /tui -->
<!-- gui -->
Choose a Session in Saga Management's Sessions and click **Begin Session**, **End Session** or **Chronicle**. The preview is turned on in the [Settings window](help:settings-window).
<!-- /gui -->

**See also:** [Sessions](help:tab-content-sessions), [Table rolls](help:table-rolls)

### Table rolls
<!-- help: table-rolls -->

Preview: turn on Virtual Tabletop in Settings.

While a Session is under way, a form whose roll the story calls for in the moment, for a character acting in a scene, is a **Table roll**: the host rolls its dice, and the roll goes to the [Chronicle](help:chronicle). These are the Personality Trait roll, Take Harm, Invoke Baraka, a saint's or God's aid, the holy life's and Theban customs' rolls, Holy Influence, Sin, Command the Beast, craft magic, Lacunae, Cast a Power, Galdor, Ars Goetia, the spirits, divination and dreams of Mythic Europe, faerie dealings, Turbulence, Reputation and House Acclaim, a cover's disguise, an agent's risks, a ship's Stress Check and Ship Combat, Open a Tunnel, melee events, disputations and polemic, a Tribunal debate, Sell Finished Goods, the Hunt, a place's roll tables, a town court's case, Exorcism and Hubris.

- Each such form gains **Who sees the roll**: Public, Private, or Blind for the Session's storyguide alone. The storyguide's start at Blind, a player's at Public. A roll made without a form, such as a place's roll table or a Tribunal debate, is Blind for the storyguide and Public for a player.
- A form's die field ("Stress die", "Blank: rolled") is hidden: the host rolls.
- The form still works its rule and says what came of it as it always has. Its Chronicle line is the form's name, the character, each die the host drew in order (a stress die with its doublings and botch dice, a simple die, and any other dice the form drew), and the form's result, word for word. A roll whose result you're asked to keep, such as Take Harm or a Disputatio, shows that result too. A form rolled at a Remote seat shows its faces as drawn, without grouping them into dice.
- At a Remote seat, each die is drawn from the host as the form needs it. The seat can't choose its dice or roll again quietly.
- A form that fails after its dice are drawn, or a seat that drops mid-roll, leaves its dice in the Chronicle as drawn, then cancelled.
- The storyguide may Strike a Table roll as any other. Confidence isn't spent on them.

Rolls the season, the year or a project calls for (Advance Season, lab work, experimentation, aging, a covenant's or a manor's years) never post, even while a Session is under way, and outside a Session every form rolls as before. Fights, battles, sieges and certamen aren't Table rolls yet.

**See also:** [The Chronicle](help:chronicle)

### The Chronicle pane
<!-- help: chronicle-pane; gui -->

Preview: turn on Virtual Tabletop in Settings.

While a Session is under way, the [Chronicle](help:chronicle) is docked on the right of the saga window. It opens when you Begin Session. It sits on a gilt leaf in your theme's own frame. Each roll is a card:

- **Who** rolled: the character, in small capitals, and the player in smaller type.
- **What** it's for, in italic.
- **The dice**, drawn as ten-sided dice with their faces: the die's throws, then the botch dice. A 0 is drawn solid, its number in white, as well as in the warning colour, so it shows without telling colours apart. A 1 that exploded has a second rim inside its kite, with what the next die is multiplied by beside it (×2, ×4...), and the outcome says it once more: die 5 × 4 = 20. A form's Table roll draws each of its dice the same way, with the line of dice under them.
- **The outcome**, set largest: the total, then whether it beat the Ease Factor and by how much, or a botch and how many zeros.

You see only what you may: a Private roll of someone else's, or a Blind roll's number unless you run the Session, isn't shown. The Session's storyguide sees a Blind roll once, as the roll itself.

A roll from the sheet has a line under what it's for saying how its modifier was made: Dexterity +2, Athletics +3, Wounds −1.

**Striking a roll:** click **Strike** beside a roll's dice, or right-click the dice and choose **Strike this roll**. Only the Session's storyguide can. Say why, and the roll stays on its card, faded, with a fine line struck through its dice and its total, and "Struck" with the reason beneath. It no longer counts.

**Spending Confidence:** click **Confidence** beside your roll's dice, or right-click them and choose **Spend Confidence**. It's there only on a roll you may spend Confidence on (see [The Chronicle](help:chronicle)). Say how many points; the spend shows as a card of its own with the new total.

- **Free Roll**, at the foot, makes a [Free roll](help:free-roll).
- **Roll Request**, below it for the Session's storyguide on the host's computer, makes a [Roll request](help:roll-requests).
- **›** collapses the pane to a thin gilt strip on the right edge, its name running up it and the count of entries come since in a small seal at its head. Click the strip to open it again. **Chronicle** in the top bar opens or collapses it too.
- A Blind roll's number, for the Session's storyguide, or the line telling you one was rolled for your character pulses the strip once. Not with **Reduce motion** on. The pane never opens by itself.
- A roll landing plays a soft tock, with **Sounds** on.

Whether it's open or collapsed is remembered for the next time the app starts with a Session under way.

**At a Remote seat** the pane shows while your host's Session is under way, with only what the host sends you. **Free Roll**, Roll on a sheet and Confidence send what you ask to the host, which does it. Strike is the host's alone. On the host's computer, a seat's roll shows as soon as the listener writes it.

**See also:** [How to roll at the table](help:guide-rolling), [Sessions](help:tab-content-sessions)

### Free roll
<!-- help: free-roll; gui -->

Preview: turn on Virtual Tabletop in Settings.

A roll made from the Chronicle rather than from a sheet. You say what to roll, never the number: the host's computer rolls every die.

- **Die**: a stress die, or a simple die, on which a 0 counts as ten (DE p. 7).
- **Modifier**: the Characteristic, Ability and anything else, added up and typed in.
- **Botch dice**: for a stress die, one most of the time, more when disaster is likelier, 0 when a botch isn't possible (DE pp. 7-8). From 0 to 10.
- **Ease Factor**: blank for none. With one, the Chronicle says whether the roll succeeded and by how much.
- **For**: what the roll is for, shown on its card.
- **Character**: a player rolls only for the characters they play tonight. The Session's storyguide rolls for any character, or for no one.
- **Who sees it**: Public, Private or, for the Session's storyguide, Blind (see [The Chronicle](help:chronicle)).

**Roll** sends it. If it can't be rolled, the reason is shown and nothing is added. To roll a Characteristic and Ability without adding them up, [roll from the sheet](help:sheet-roll) instead.

**See also:** [The Chronicle](help:chronicle)

### Roll requests
<!-- help: roll-requests; gui -->

Preview: turn on Virtual Tabletop in Settings.

The storyguide's call for chosen characters to roll, answered with one click each. Click **Roll Request** at the foot of the [Chronicle pane](help:chronicle-pane):

- **The characters**: each character cast tonight, and each shared grog whose Steward is coming, with a tick. All are ticked to start with.
- **Characteristic** and **Ability**: what to roll. The host adds each character's own scores, Specialty and penalties, as for a [roll from the sheet](help:sheet-roll). A character with no score in the Ability rolls at 0 with three more botch dice.
- **Die** and **Ease Factor**: blank for none.
- **Hide Ease Factor**: players see their totals; only you see the Ease Factor and who succeeded.
- **For**: what it's for.
- **Who sees each roll**: Blind to start with, so the numbers are yours alone and each player sees only that they rolled; or Private, each roller and you; or Public.
- **Shared grogs rolled by**: a shared grog is rolled by its Steward unless you name another Player here. It's for this request only: the evening's casting doesn't change.

**Ask** puts the request in the Chronicle. Its card lists each character with **Roll** beside it for whoever rolls it (the character's player tonight, a shared grog's Steward, or you) and **Roll (climbing)** too when that character's Specialty may apply. Each answer fills its line as it comes: the total, with ✓ or ✗ against the Ease Factor, or "rolled" for a number you may not see. You can roll for anyone without a seat, such as a player at your table. **Outcome** notes what came of it.

**At a Remote seat**, a request for your character shows its Roll on its card, sent to the host to roll.

**See also:** [The Chronicle](help:chronicle), [How to roll at the table](help:guide-rolling)

### Roll from the sheet
<!-- help: sheet-roll -->

Preview: turn on Virtual Tabletop in Settings.

While a Session is under way, a character's **Abilities** and **Characteristics** offer **Roll**: to the player of a character cast to them tonight, and to the Session's storyguide for any character. You say what to roll; the host's computer reads the sheet and rolls the dice.

- **Characteristic**: any of the eight goes with any Ability, as the situation says (DE p. 157). The one last rolled with that Ability tonight is chosen for you.
- **Ability**: the character's own with their scores, or none for a Characteristic alone. Abilities the character has no score in are offered too, marked "no score": rolled at 0 with three more botch dice (DE p. 157). An Ability the book asterisks, such as Magic Theory, or any Supernatural one, can't be used without experience and isn't offered (DE p. 159).
- **Specialty applies**: +1 when the roll falls within the Ability's Specialty (DE p. 157). The roll names the Specialty.
- **Die**, **Ease Factor**, **For** and **Who sees it**: as a Free roll's. The storyguide's own rolls start as Blind.
- **Anything else**: a bonus or penalty beyond the sheet, such as an aura or the storyguide's call.

The host adds the wound penalty and the Fatigue penalty itself, as the character's Virtues and Flaws change them: Enduring Constitution eases each by one (DE pp. 403-404). A character who is Incapacitated or Unconscious takes no action, and Roll says so (DE p. 404). After the roll, you may spend Confidence on it (see [The Chronicle](help:chronicle)).

<!-- tui -->
Choose the Ability or Characteristic in its list and press `m` for More, then **Roll**: the card opens with it chosen. The roll shows in the Chronicle.
<!-- /tui -->
<!-- gui -->
Click **Roll** by the Abilities or Characteristics heading and choose what to roll on the card. The roll lands in the [Chronicle pane](help:chronicle-pane). See also [Free roll](help:free-roll).
<!-- /gui -->

**See also:** [The Chronicle](help:chronicle)

### The Sessions list
<!-- help: section-sessions -->

<!-- tui -->
The list of Sessions, with the details panel below it. The panel shows when, its game date, storyguide, who's coming and who's Away, and who played whom.
<!-- /tui -->
<!-- gui -->
The list of Sessions. The Inspector shows the one last clicked: when, its game date, storyguide, who's coming and who's Away, and who played whom.
<!-- /gui -->

## Players
<!-- help: tab-content-players -->

Who can sign in to this saga when you host it, so players open it in a web browser from their own computers. Each player signs in with their name and the passcode you give them. Your own window, the app run on your computer, never asks.
<!-- gui -->

On the desktop the Players are in the saga page's **Saga Management**, beside **Host for Players** (see [How to host a saga](help:guide-hosting)) and the Sessions. The players you add there are the ones it lets in. To join over the internet from their own copy of Armarius, a Remote seat, a player's passcode needs at least 14 characters, set there. The list says whether each can (**✓ Ready**, or why not). **Issue Invite** on the chosen player opens Host for Players with their Invite (see [Issue Invite](help:issue-invite)).
<!-- /gui -->

Only the storyguide sees it: your own window, or someone signed in with the Storyguide role. A storyguide joined from a Remote seat doesn't, since who may join is the host's.

Players stay in this saga. No export or pack carries them, nor which player plays a character, though a character keeps the Player named on its sheet.

<!-- tui -->
**You type:** with `a` and `e`,
<!-- /tui -->
<!-- gui -->
**You type:** with **Add** and **Edit**,
<!-- /gui -->
the player's Name, their Role (Player or Storyguide), for a player whether they May change covenants, and a Passcode. The Name is what they type to sign in, and no two players may share one. When editing, leave New passcode blank to keep the one they have. Deleting a player asks first, and they can no longer sign in.

Leave the Passcode blank when adding someone who only sits at the table. They're a **table-only Player**, named on Sessions and as a Steward but never able to sign in. Give them a passcode later, by editing them, if they're to join from their own computer.

**The app works out:** in their details, the characters each plays, the characters each stewards, and what they may change. Passcodes are stored only scrambled, as a salted hash, so the app can check one but no one can read it back from the saga file. If a player forgets theirs, give them a new one.

### The players
<!-- help: section-players -->

<!-- tui -->
The list of players, with the details panel below it.
<!-- /tui -->
<!-- gui -->
The list of players, in Saga Management. The Inspector shows the one last clicked. When a player last joined by Remote seat on another version of Armarius than yours, their Remote seat says so, as "4.13.1, not tested with yours". They can still play.
<!-- /gui -->

### What a signed-in player can do
<!-- help: players-access -->

Only the storyguide chooses who plays a character, in the character's Biographical Detail. Tick **Played by** for each player who plays them, several in troupe-style play, or **Played by everyone in the troupe** for a character the troupe shares, such as a grog. Any of a character's players may change the character. If two change the same thing at once, the later save is kept and the other is told.

A signed-in player can then:

- change the characters they play, with those characters' familiars, laboratories and books, and their season plans
- plan the seasons of the characters they're **Steward** of, and change nothing else on those sheets. A Steward is chosen in the Biographical Detail of a character no Player is named on, such as a pooled grog, even one everyone in the troupe plays. They keep it between Sessions and decide its downtime.
- make a character of their own with **New Character**, so a player can join before they have one. It can be a magus or companion, or a grog with covenant rights, since a new grog joins the covenant's household. It's theirs from the start, named in its Biographical Detail as played by them, and you can change or delete it like any other.
- change the covenants too, if you ticked May change covenants for them
- look at everything else, except each record's [Secrets](help:tab-secrets), which they never see, and the records they don't know of (see [Player view](help:player-view))
- Export a character, laboratory or covenant. The file downloads in their browser, without its secrets or the records they don't know of.

Only the storyguide, in your own window or signed in as Storyguide, can make any other new record (New), advance or set the season, import, give things between records, share spells, or change the saga itself, its content and its players. Keys a player can't use there don't appear. If a change slips through anyway, the app doesn't save it and says so.

<!-- gui -->
**On the desktop** a player's window opens on **Your Characters**, with a **New Character** card for one of their own. Then come the troupe's other characters, the troupe's covenants and the rest of what the players know. Their own characters show every button. Any other record is read only, with no Add, Edit or Delete, and Advance Season and Player view aren't there.

To see it as a player does, click the **Play as** icon (two people) in the title bar, which appears once the saga has players, and pick a player. It then reads "Playing as" and their name. Pick **Storyguide** from it to come back.

While the player you sit as has characters, the button is split. "Playing as" and the name opens their sheet (My sheet, or `c`), and its ▾ is the seat menu, with their characters at the top. A player's own desktop has the same button: their character's name, with a ▾ listing their characters (see [Jump to your sheet and back](help:guide-my-sheet)).
<!-- /gui -->

**See also:** [Signing in](help:sign-in), [How to host a saga](help:guide-hosting), [The saga](help:saga)

# A record's Secrets
<!-- help: tab-secrets -->

What only the storyguide should know about a record, such as the covenant's hidden debt, the magus's true master, or where a missing founder really went. Every covenant, character, Tribunal, neighbour and creature keeps a list of them. They're kept apart from its summary and notes, so those can be read aloud or shown to the players as they are. Each secret is a short title and its words, and says whether it's been revealed, and when.
<!-- tui -->
It's the record's last tab, **Secrets**.
<!-- /tui -->
<!-- gui -->
It's the record's last chapter before Manage, **Secrets**.
<!-- /gui -->

You see every secret, each marked "Not revealed" or "Revealed" with the season and year. A player signed in to a hosted copy, and your own window in [Player view](help:player-view), see only those revealed, in the record's **Known** section instead. With none revealed, Secrets isn't shown to them at all. A record a player exports carries only its revealed secrets, and [Find](help:find) searches secrets only for you.

The content packs that come with the app, and the Dammërstein saga starter, give each secret a title, each one thing the players could learn on its own. A record's table notes, such as auras, rolls, where a stat block is and the rules' names for a trait, are its last secret, **Storyguide Notes**. That one is for you, and isn't meant to be revealed.

Older sagas and content packs kept a record's secrets as one piece of writing, some at the end of a summary or notes under a **Secrets** heading. Opening the saga makes that one untitled secret, and **Split by Paragraph** breaks it up. A pack exported from such a saga brings its secrets the same way.

**See also:** [How to reveal a record to the players](help:guide-reveal), [What a signed-in player can do](help:players-access), [How to host a saga](help:guide-hosting)

### Secrets
<!-- help: section-secrets -->

The list of the record's secrets, each with its title, or its first words if it has none, and whether it's revealed. Every secret is written in full below the list.

<!-- tui -->
`a` adds a secret, `e` edits the one chosen and `d` deletes it after asking. More (`m`) on a chosen secret offers **Reveal the Secret**, or **Hide the Secret Again** once revealed. For a secret of several paragraphs it also offers **Split by Paragraph**.
<!-- /tui -->
<!-- gui -->
**Add**, **Edit** and **Delete** act on the secret chosen, as do **Reveal**, or **Hide Again** once revealed, and **Split** for a secret of several paragraphs.
<!-- /gui -->

- **Reveal** marks it revealed this season and writes a dated line in each troupe covenant's Diary, "Revealed: the record: the secret". The players see it in Known from then on. On a record the players don't know of yet, it shows once the record is revealed too. **Hide Again** takes it back, and its Diary line.
- **Split by Paragraph** shows the parts first, then makes one secret of each paragraph, each revealed as the whole was. The first keeps the title.

**You type:** a **Title**, a few words and optional, and the **Secret** itself, as many paragraphs as you like. It supports **bold** and *italic*.

### Known
<!-- help: known-secrets -->

What the players have been told of the record's secrets: each one the storyguide revealed, with its title and the season it was revealed in. A player, or the storyguide's window in [Player view](help:player-view), sees it in place of Secrets.

# Player view
<!-- help: player-view -->

What the players may read, and the storyguide's own window shown as they see it. Every page, list, search and export asks the same question, so a player sees the same saga wherever they look.

<!-- tui -->
**Player View**, in More (`m`) on the saga at the top of the tree, turns it on or off. While it's on, the header says "Player view".
<!-- /tui -->
<!-- gui -->
The **eye** in the title bar, beside Find, turns it on or off. While it's on, the words "Player view" stand beside it. Use it on a screen your players can see across the table.
<!-- /gui -->

The app remembers it for each saga on this computer. A player signed in to a hosted copy always sees the saga this way. In a solo saga, with nobody signing in, Player view is your guard against spoilers. It's off until you turn it on.

- **Known to the players.** Every record of the world beyond the troupe is either known to the players or not. That's a neighbour or place, a creature, a covenant the troupe doesn't play, or a character no player plays. One they don't know of is left out of every list, Find, the Atlas and Looking Ahead. A page that names it shows neither its name nor a link, and a line that names nothing else is left out. The troupe's own characters, covenants and laboratories are always known.
- **Reveal to the Players** tells them of a record, and a dated line saying so goes in each troupe covenant's Diary. **Hide from the Players** takes it back, and takes that line out. It can also [hide many records](help:mark-unknown) at once.
<!-- tui -->
  Both are in More on the record's own sheet.
- **The mark** after a record's name, at the top of its sheet, shows which it is. It's 👁 while the players know of it, and 🚫 while it's hidden from them. The troupe's own records have none, and Player view shows none.
<!-- /tui -->
<!-- gui -->
  Both are in the record's Manage chapter.
- **The seal** under a record's bookmark ribbon shows which it is. It's an eye in a ring, struck through and inked red while the record is hidden from the players, and plain once it's known. Hover over it to read Hidden or Known, and click it to reveal or hide the record. The troupe's own records have none, and Player view shows none.
<!-- /gui -->
- **The storyguide's alone:** each record's [Secrets](help:tab-secrets), a place's or lord's [Roll Tables](help:tab-nb-tables), Needs You, Saga Management, Saga Settings, the Armarium, the Custodia Mirabilium and the Players list of Saga Content. The books in play, catalogs, House Rules and spells stay on show.
<!-- gui -->
  With Saga Settings hidden, Saga Content's card moves to the top of the saga page's [Compendium](help:saga-compendium), under Content in Play.
<!-- /gui -->
- **Threats:** a threat's stages show only once they've come or been marked. Its clock, its position and what's still to come never show.
- **Looking Ahead** shows only the dates anyone could know: Tribunal meetings and terms, fairs, aging rolls and your own calendar entries. It never shows a threat's stage, a place's trigger or the world's yearly turn.
- **The Diary:** a line the app wrote about a record the players don't know of, such as a threat's stage or a roll on a place's table, is left out until it's revealed. Lines you typed always show.
- **Exports** made in Player view, or by a player, leave out Secrets and the records the players don't know of. Yours otherwise are whole.
- **Actions** only the storyguide takes are left off while Player view is on: Roll on a table, Reveal and Hide, hosting, Import, Export Pack, Edit Saga, and beginning, growing, delaying or taking up a threat's story.

Sagas from before keep every record known. A pack brings its records known, except any it marks secret.

**With a second storyguide**, a Player whose role is Storyguide, Player view becomes **Playing**. Every storyguide's window opens in it, yours too, with your characters as a player sees them.
<!-- tui -->
Player View in More switches to your storyguide role and back.
<!-- /tui -->
<!-- gui -->
The eye then reads **Playing** or **Storyguide**. Click it to switch.
<!-- /gui -->
Each switch is written in the host's Remote seats log. In your storyguide role you read your own stories, and those with no storyguide, whole. Another storyguide's you read as a player would (see [A storyguide for each story](help:assign-storyguide)).

**See also:** [How to reveal a record to the players](help:guide-reveal), [What a signed-in player can do](help:players-access), [A record's Secrets](help:tab-secrets), [How to run a saga with several storyguides](help:guide-troupe-storyguides)

# A storyguide for each story
<!-- help: assign-storyguide -->

In troupe-style play several of you take turns as storyguide, each running their own stories (DE pp. 529-530, the alpha and beta storyguides). Once the saga has a second storyguide, a Player whose role is **Storyguide**, any record that keeps Secrets can have its own storyguide. That's you, the host, or one of them. The records are characters, covenants, places, lords, factions, threats, creatures and Tribunals. A covenant's open story events are its storyguide's, and a laboratory or familiar is its character's.

- **Its storyguide** reads it whole: its Secrets, Roll Tables, and a threat's stages still to come and its clock.
- **Any other storyguide, the host included,** reads it as a player would, and can't change it. There's no storyguide who reads everything. Find, Looking Ahead, Needs You, the Atlas and exports follow the same rule.
- **No storyguide:** every storyguide reads it whole, as before.

<!-- tui -->
**Its Storyguide**, in More (`m`) on the record, sets it.
<!-- /tui -->
<!-- gui -->
**Its Storyguide**, in the record's Manage chapter, sets it.
<!-- /gui -->
Any storyguide takes a record with none for themselves. Only its own storyguide releases it, by leaving it blank, or hands it on to another. Nobody takes someone else's, so nobody can read another's Secrets by taking them. The record's Connections, or its facts, say whose it is.

Deleting a storyguide, or making them a player again, leaves their records with no storyguide, so every storyguide then reads their Secrets. You're asked first, with the records named.

**What it isn't:** a lock. The host's saga file holds everything, and Armarius keeps the rule on screen and in what it sends. It keeps friends from spoiling each other's stories, but doesn't stop someone who opens the file.

**From a Remote seat**, while another storyguide runs some of the saga's stories, Advance Season is left to the host's computer, which holds every record whole. A seat holds another's records only as the players have them.

**See also:** [Player view](help:player-view), [How to run a saga with several storyguides](help:guide-troupe-storyguides), [What a signed-in player can do](help:players-access)

### Hide many records
<!-- help: mark-unknown -->

<!-- tui -->
Hide from the Players on the saga or the Region (More, `m`) hides a whole list at once, such as a pack's every place before the troupe has travelled.
<!-- /tui -->
<!-- gui -->
Hide from the Players on the saga page's The Region chapter hides a whole list at once, such as a pack's every place before the troupe has travelled.
<!-- /gui -->

**You type:** **Which** list, and **In the lands of** to take only those in one Tribunal's lands, or blank for wherever they are. The lists are Lords and Towns, the Church, Universities, Factions, Threats, Places, Customs and Lore, Other covenants, Non-player characters and the Bestiary.

**The app works out:** how many records the players know of now would be hidden, shown as you choose. Nothing is deleted. Reveal each one as the troupe learns of it.

# Saga Management
<!-- help: saga-management; gui -->

A chapter of the saga's page. It holds Import, Export Saga, Export a Cult, Export Pack and Host for Players, each with a line on what it does, then the [Players](help:section-players) and the [Sessions](help:section-sessions). Host for Players opens the [Host for Players](help:host-for-players-window) window, where you host the saga and manage Remote seats. While the saga is hosted, its line says how. It's the storyguide's alone, and [Player view](help:player-view) leaves it out.

**See also:** [Import Data](help:import-data), [How to host a saga](help:guide-hosting), [Host for Players](help:host-for-players-window)

# Signing in
<!-- help: sign-in -->

When the storyguide hosts the app, opening a saga in a browser or over SSH first asks who you are. Type your Name and the Passcode the storyguide gave you, then Sign in. The Name isn't case-sensitive, but the passcode is.

Three wrong passcodes for a name are free. After that each try must wait, longer each time (30 seconds, then 2 minutes, 10 minutes, then an hour), and the dialog says how long. The wait holds for that name wherever it signs in. A right passcode starts the count again.

A passcode needs at least 14 characters. If yours is shorter, set before that rule, signing in asks you to **Choose a new passcode**. Type it twice and Save. **Not Now** lets you in this once. Next time, the short passcode is refused until you choose a new one here or the storyguide sets one. A new passcode you choose here also lets you join from a Remote seat.

<!-- tui -->
If the saga has no players yet, it can't be opened from a browser. The storyguide adds them on Saga Content's [Players](help:tab-content-players) tab.
<!-- /tui -->
<!-- gui -->
If the saga has no players yet, it can't be opened from a browser. The storyguide adds them as [Players](help:tab-content-players) in the saga page's Saga Management.
<!-- /gui -->
While you're signed in, your name is shown in the header beside the saga's date. Going back to the saga list (Escape) signs you out.

While several people have the saga open, each one's saves keep everyone else's changes, and within a few seconds the others' screens show them. The sheet on show updates where it is, with a note such as "Ana changed Corvinus; reloaded". If two people open the same character, both are told, whether they're in a browser, the storyguide's own desktop or a Remote seat. The note reads "Ana is also on Corvinus", or on the desktop "◉ Ana is here too" beside the trail, for as long as she is. If the record you have open is deleted elsewhere, the saga is shown instead.

**See also:** [Players](help:tab-content-players), [How to host a saga](help:guide-hosting), [Saga picker](help:saga-picker)
