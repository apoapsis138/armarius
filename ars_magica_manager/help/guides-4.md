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
3. In the Export dialog, check the **File**. It starts in the app's exports folder (`exports`, in Ars Magica Manager in your OneDrive folder) with a name made from the record's name; `.amm.json` is added if you give no `.json` ending. The line above Export warns when the file exists and will be replaced.
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

Each saga is saved as one file, the saga's id followed by `.json`, in the `sagas` folder of Ars Magica Manager in your OneDrive folder (see the README to keep it elsewhere). The app saves every change as you make it.

- Before a season with plans is applied, the app copies the saga to `sagas/backups`, keeping the last five (the newest has the saga's own file name; older ones end `.1.json` to `.4.json`). To undo that season, copy the backup over the saga's file with the app closed.
- That is the only backup the app keeps, so for anything older, copy the saga's file yourself from time to time.
- To keep a single character, laboratory or covenant safe before a big change, export it as above.

**See also:** [Import Data](help:import-data), [Import Spells](help:import-spells), [Unassigned Books](help:unassigned-books), [Library tab](help:tab-cov-library), [House Rules](help:house-rules), [The saga](help:saga), [Advancing a season](help:advance-season)

# How to host a saga for your troupe
<!-- help: guide-hosting -->

The storyguide can let the players open the saga in a web browser on their own computers, while it stays on the storyguide's. The app and the saga file never leave your computer; each player who opens the page gets their own copy of the app, running on your machine.

You need a private network that you and the players share. The app doesn't come with one: use your home network, **Tailscale** or **ZeroTier** (recipes below). Never host on an address the whole internet can reach.

### Before the first session
<!-- help: guide-hosting-setup -->

1. Open the saga and select its [Players](help:players) node. Add each player with `a`: a name, the Role *Player*, and a passcode you give them yourself. Add a *Storyguide* there too if another storyguide will sign in from a browser.
2. For each player's characters, open the character, edit its Biographical Detail and choose who it's **Played by**. Tick **May change covenants** on a player who should keep the covenant's books.
3. Set up the private network (Tailscale or ZeroTier below) and note your computer's address on it.

### Starting and stopping
<!-- help: guide-hosting-start -->

1. In a terminal in the app's folder, run `uv run python tools/serve.py --host ADDRESS`, with your address on the private network (add `--port 8001` if 8000 is taken). The first time, Windows asks whether to let it through the firewall: allow it on **private** networks.
2. Players open `http://ADDRESS:8000` in their browser, choose the saga and sign in.
3. Keep your computer awake while people play: nobody can reach the saga while it sleeps.
4. To stop, press Ctrl+C in that terminal. Your own window of the app is separate: open it as usual.

If you give an address the computer doesn't have, the command says so and lists the ones it does.

### Tailscale
<!-- help: guide-hosting-tailscale -->

Everyone, you and each player, installs Tailscale and signs in with an existing Google, Microsoft, GitHub or Apple account.

1. On your computer, Tailscale shows its address (it starts with `100.`). That is the ADDRESS to host on.
2. In Tailscale's admin page, share your computer with each player by their email. They accept the invite, and can then reach only your computer.
3. Players open `http://ADDRESS:8000`.

### ZeroTier
<!-- help: guide-hosting-zerotier -->

Only you need a ZeroTier account; players just install the ZeroTier app.

1. On ZeroTier's website, create a network and copy its 16-character Network ID. Keep it Private.
2. On your computer, join that network from the ZeroTier icon, then on the website tick **Auth** for your computer and note its Managed IP: that is the ADDRESS to host on.
3. Windows often marks the ZeroTier connection as a Public network; set it to Private in Windows' network settings, or the firewall keeps players out.
4. Each player installs ZeroTier, joins with the Network ID, and you tick **Auth** for their device.
5. On a ZeroTier network every device can reach every other one. To let players reach only the app on your computer, set the network's Flow Rules along these lines (with your address), then check a player can still connect:

```
accept ethertype arp;
accept ipdest ADDRESS/32 and ipprotocol tcp and dport 8000;
accept ipsrc ADDRESS/32 and ipprotocol tcp and sport 8000;
drop;
```

### Over SSH instead of a browser
<!-- help: guide-hosting-ssh -->

A player who prefers a terminal can connect with SSH instead. Add `--ssh-port 2222` when you start hosting (`uv run python tools/serve.py --host ADDRESS --ssh-port 2222`); the browser page keeps working alongside. The SSH server is the app's own: no Windows accounts are involved, and any user name is accepted, because who the player is comes from the same sign-in as in a browser. The first time, the app makes a host key (`ssh_host_key` in your data folder); players' SSH clients ask once whether to trust it.

Players connect with `ssh -p 2222 player@ADDRESS` from Windows Terminal (Windows 10 and 11 include `ssh`), macOS Terminal or any Linux terminal, and get the same saga list and sign-in. Their terminal should be at least 120 columns by 45 rows and support true colour and Unicode: Windows Terminal, iTerm2, macOS Terminal and the usual Linux terminals do; the old Windows console does not. Over SSH, Export isn't offered, since the file could only land on your computer.

### What players see
<!-- help: guide-hosting-players -->

- The app fills the browser window. It is laid out for at least 120 columns by 45 rows: on a 1080p screen, add `?fontsize=12` to the address (`http://ADDRESS:8000/?fontsize=12`) or zoom the browser out.
- The browser keeps some keys for itself (Ctrl+W, Ctrl+T, F5), so don't use them in the app.
- A player changes only the characters they play and what belongs to them; everything else they can look at and Export, which downloads in their browser. See [Players](help:players).
- Everyone's changes reach the others within a few seconds. See [Signing in](help:sign-in).

**See also:** [Players](help:players), [Signing in](help:sign-in), [Saga picker](help:saga-picker)
