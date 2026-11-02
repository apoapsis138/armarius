# Conflicts
<!-- help: conflicts -->

Conflicts holds the saga's battles, fights and sieges. A battle between
two armies is played as Lords of Men's few battlefield events (Lords of
Men pp. 102-109). A fight is played blow by blow with the Definitive
Edition's combat rules (DE pp. 394-398). A siege is played event by
event with Lords of Men's siegecraft (pp. 111-116). They belong to the
whole saga, not to a covenant; a battle or siege that names a lord
shows on his Fief tab too, so lords can fight and besiege one another.

<!-- tui -->
In the navigation tree Conflicts sits after the Bestiary. Selecting it
shows its facts, then the Battles, Fights and Sieges lists, each over
the chosen row in full. In either list, `a` adds one, `e` edits the chosen
one and `d` deletes it. More (`m`) holds what plays them.
<!-- /tui -->
<!-- gui -->
On the saga's page, the Conflicts chapter lists the battles, the fights
and the sieges. A battle is acted on from its card. Each opens its own page, drawn as a manuscript leaf: a fight with
its order of blows and the two sides under their arms, a siege with its
castle's plan, the season medallions and both armies.
<!-- /gui -->

**See also:** [How to run a fight](help:guide-fights), [How to run a siege](help:guide-sieges)

## Conflicts' facts
<!-- help: section-conflicts-info -->

How many battles, fights and sieges the saga has, and how many fights
and sieges are still going on.

## Conflicts tab
<!-- help: tab-conflicts -->

The Battles, Fights and Sieges lists, over the chosen one in full.

### Battles
<!-- help: section-conflict-battles -->

Every battle in the saga, between two armies: each a lord, town or
other power of the Region, a covenant, or just a name. The columns and
the form are those of a lord's [Battles](help:section-nb-battles); More's
**Battle Event** plays the chosen battle's next event (see
[Battle Event](help:battle-event)).

### Fights
<!-- help: section-fights -->

Each fight's name, when and where, its two sides, the fighters still
standing on each, and whether it has begun, its round, or how it ended.
The panel below shows the chosen fight in full: the order of blows (the
one acting now marked), each side's fighters with their figures and
wounds, the last blow worked out line by line, and the chronicle.

<!-- tui -->
More on a fight: **Add Combatant**, **Edit Combatant**, **Remove
Combatant**, **Form a Group**, **Break up a Group**, **Next Blow**,
**Next Round** and **Restart the Fight**.
<!-- /tui -->

### Sieges
<!-- help: section-sieges -->

Each siege's name, its castle and besieger, the Garrison in combat
groups, the Defenses and Supplies, and how long it has run (or how it
ended). The panel below shows the chosen siege in full: the castle's
figures and the interval its events come at, each wall's damage levels,
the besiegers' miners, engines and soldiers, and the chronicle.

<!-- tui -->
More on a siege: **Next Siege Event**.
<!-- /tui -->

# A fight
<!-- help: fights -->

A fight has two sides. Each side has combatants, and some of them may
fight together in combat groups.

The app keeps no map: the Definitive Edition's combat has no positions,
only who acts when and whom they strike. Where the fight happens is the
fight's Where, and getting the fighters there is the story's; each blow
names its target, and Disengage is how a fighter leaves.

- **Add Combatant** adds one of the following to a side:
  - A character with one of the weapons they carry. Their figures, wounds and Fatigue come from their sheet, and wounds they take are written onto it.
  - A creature of the Bestiary with one of its attacks. Its figures are copied, and you can add several at once (Wolf 1, Wolf 2...), each with its own wounds.
  - A fighter with figures typed in, such as Init, Attack, Defence, Damage, Soak, Size, Combat Ability and Leadership.

  A character with no weapon fights with the book's Fist. Any of them may also be:
  - **Mounted**: Ride, at most +3, adds to its Attack and Defence (DE p. 397). A character's Ride comes from the sheet; a typed fighter's is typed. A Gifted rider (not the Gentle Gift) is warned that a horse throws them without magic (DE pp. 82, 205). A mounted character's lance fights as a Single Weapon; on foot it is a long spear, fought with Great Weapon (DE pp. 400-401; Lords of Men p. 126).
  - **Defending** another on its side, as a shield grog defends a magus: while a defender stands, nobody may strike the one it defends, and only a defender's botched Defence lets a blow through to them (DE p. 397).
  - Given a **Magic Resistance** (a creature's Might), against spells and devices; a magus's comes from Parma and Form.
  - **Invisible**, with how clear the signs that betray it are: Obvious (a visible sword, mud, wading), Clear (a shadow in sunlight, footprints in sand), Indistinct (a shadow on a cloudy day, packed earth), Faint (a shadow in moonlight, cobblestones) or No signs. They give it +1, +3, +3, +6 or +9 to a melee Attack, +3, +3, +6, +9 or +9 to Defence, and +3, +3, +6, +9 or +12 to Stealth. A foe must locate it before striking, shooting or casting at it, unless the two are engaged hand to hand; Obvious signs need no search, and No signs can be found by sound alone. An invisible fighter nobody has found acts first in the first round and adds +3 to its Attack against a foe who hasn't located it. Its weapon and its touch are magical too, so a target with Magic Resistance keeps them out, whatever its signs; tick **Weapon picked up after turning invisible** for a non-magical weapon taken up once invisible, which stays visible and gets through (never bare hands: a scuffle or grapple is still kept out). Obvious signs set the bonuses and let foes find it without a search; they don't make its blow non-magical. It can't fight in a trained group, an untrained group rolls a botch die more for each invisible member, and nobody can defend it (Houses of Hermes: Societates pp. 32-33; Errata p. 58; DE p. 223).

  The panel at the foot of the form, **The Fighter**, shows the fighter as the fight will see it.
- **Edit Fight** also sets the **Range increments** between the sides (0: hand to hand) and the **Magic aura** where they fight. At range only missiles strike, at -3 for each increment past the first (DE p. 395); the aura adds to every Casting Total.
- **Form a Group** joins one to six fighters of a side, with a vanguard. A trained group (one that spent a season improving combat skills together) also has a leader. The group fights with the vanguard's figures. A trained group's other members add their Combat Abilities, at most three times the leader's Leadership, to its Attack or its Defence. A note says when the members' totals run more than five points apart, which a group's shouldn't when it forms (DE pp. 395-396).
- **Next Blow** plays the turn of whoever acts now. The first Next Blow rolls everyone's Initiative (Init + stress die, once for the whole fight); then each acts in order, highest first. Choose the action and who it strikes. Only the actions the fighter can take are offered, and the panel at the foot of the form, **The Blow to Come**, says what the action does and the totals it rolls (riding, range, group bonus and Form Bonus included), or why it can't be done:
  - **Attack**: Attack + stress die against Defence + stress die. A hit adds the Attack Advantage to Damage; what passes Soak is read on the Damage Table for the defender's Size. Against a missile weapon only a shield's Defence counts. Against a hand-held Greek Fire siphon not even that: the fire splashes round the shield, and its Defence adds to the defender's Soak instead (The Sundered Eagle p. 47).
  - **Attack with Exertion**: spends a Fatigue level (each member's, in a group) for +the Combat Ability.
  - **Charge**: moves and attacks for +the Combat Ability, a Fatigue level spent (on foot the charger's; mounted the horse's, which the app doesn't track), never across difficult ground. A mounted charge that hits a target smaller than **The horse's Size** tests its shock: the target's Dexterity + Ride + saddle (**The target's saddle**: cantled +3, no stirrups -3) if mounted, or Strength + Size + Combat Ability on foot, + a stress die, against the Damage Total before Soak + the horse's Size; failing, it is unhorsed or knocked down, prone (Lords of Men pp. 123, 126-127). Combat Options works the other mounted rules out.
  - **Scuffle**: knocks out rather than kills. The wound becomes Fatigue by the Scuffle Effects table, at -3 to Attack and without the weapon's Damage when fighting with a real weapon.
  - **Disarm, Trip, Grab worn item, Take the weapon your opponent is using**: succeed with an Attack Advantage of 9, 3, 6 or 12, and deal no damage.
  - **Grapple**: with bare hands and Brawl. Any Attack Advantage above 0 takes hold, and becomes (or adds to) the Grapple Strength; the card says who holds whom (DE p. 398).
  - **Break free**: offered to one held, who may otherwise only cast, use a device or wait. An attack on the one holding them: its Advantage comes off the Grapple Strength, and at 0 they are free and the holder takes a Light Wound. A grip lets go when either falls.
  - **Split the group**: against an enemy group while another unit of your side presses it. An Advantage of 0 or more splits it rather than wounding it: in half, or in thirds when three or more press it and a second split succeeds that round; a part of one fights alone (DE p. 398).
  - **Locate the unseen**: offered while an invisible foe hasn't been found. A round spent searching: Perception + Awareness + stress die against its Dexterity + Stealth - Encumbrance + its Stealth bonus + stress die. Beating it locates the foe, who may then be struck, shot and targeted (Houses of Hermes: Societates p. 32). A typed fighter searches and hides with 0 besides the bonus.
  - **Amid a battle**: in a battle event's fight, or one marked **Part of a battle** on Edit Fight, a magus must first pass a Concentration roll to cast: Stamina + Concentration + a stress die against 12, or 9 with **Standing off, not engaged** ticked; failing it, the spell is lost (Lords of Men p. 109; DE p. 215). A Group target rarely fits a battle's mass of troops: a unit separated from the army is reached with one magnitude more (100 people), and a Boundary a magnitude more covers about 300 paces.
  - **Cast a spell**: a magus casts one of the spells they know, or spontaneous magic (its Arts and level, fatiguing or not), at their place in the order. Formulaic: Casting Score + stress die, cast if no more than 10 short of the level (a Fatigue level when short). Spontaneous: (score + stress die) / 2 for a Fatigue level, or score / 5, and the spell fails if that falls short of the level asked for, unless Life-Linked Spontaneous Magic pays a Fatigue level more for each 5 short. Incompatible Arts forbid a spell, and Painful Magic brings a level of pain with each. **Casting requisite** (a Technique, a Form, or both) adds the Arts what it is used on this time needs: the lowest Technique and Form among the spell's Arts, its own requisites and these are the ones cast with (DE p. 312). Then Penetration (Casting Total - level + Penetration) against the target's Magic Resistance, and any damage: stress die + X against Soak (with the Form's Bonus) + stress die (DE pp. 214-215, 394, 397). A mastered spell adds its Mastery score to the Casting Score and takes that many botch dice off, to none; with the Penetration Mastery ability it adds to Penetration too, and a target who mastered the same spell with Magic Resistance has his resistance doubled against it (DE pp. 225-226). **Arcane Connection** multiplies Penetration by how long it lasts (+1 hours or days, +2 weeks or months, +3 years or decades, +4 indefinitely), and with one, **Knows the target's name** adds +1 and **Symbolic representation** +2 (DE pp. 219-220; Houses of Hermes: Societates p. 27). **Indirect (aimed)**: a spell that moves or makes something mundane that then strikes isn't stopped by Magic Resistance but must be aimed: Perception + Finesse + stress die, +6 for each **Size step** past a basic Individual, +1 for each Precise Casting, against the target's Defence as against a missile + stress die; a hit does the damage with no Attack Advantage (DE pp. 223, 226; Houses of Hermes: Societates pp. 30, 32). The 18 spells Houses of Hermes: Societates p. 30 lists (Pit of the Gaping Earth, End of the Mighty Castle...), and the Invisible Sling of Vilano of its new spells (p. 38), are indirect without asking. Several are only partly so, and the panel says how: the corpse spells (Awaken the Slumbering Corpse, Strings of the Unwilling Marionette, The Walking Corpse) get through only with a non-magical weapon the corpse wields; The Earth Split Asunder's fall isn't resisted but its crush when it closes is; the waves capsize a boat or wash out a bridge rather than harm directly; the moving flames still burn. Weaver's Trap of Webs, Footsteps of Slippery Oil, Trap of the Entwining Vines and Coils of the Entangling Plants hold or trap and do no harm themselves, so a Damage typed for them is refused. An invisible foe nobody has found can be reached only by an area spell (Group, Room, Structure, Boundary) or one cast through an Arcane Connection, and Eye range works neither on nor by an invisible fighter (Houses of Hermes: Societates p. 32). The panel also says which of House Flambeau's schools of magical combat the magus's Virtues suit (Houses of Hermes: Societates pp. 25-30).
  - **Use a device**: one effect of a device the character holds, with no Fatigue; its Penetration is what it was enchanted with (0 unless more), against Magic Resistance, and any damage as for a spell (DE p. 259). Marked **Indirect (aimed)**, it isn't resisted but is aimed with the wielder's Perception + Finesse, as a spell is (DE p. 223).
  - **Disengage**: a Defence Total against every attacker of the last round, +3 for each try after the first. Unattacked since its last turn, a fighter leaves freely.
  - **Wait**: passes the turn.
- A group's hit lands once for each of its fighters, spread over the defending group with its vanguard taking the most. When a group's vanguard or leader falls, the group splits into individuals.
- A magus's **Form Bonus** (the Form / 5, rounded up) adds to Soak against harm of its Form: Animal against teeth and claws, Corpus against bare hands, Herbam against wooden weapons, Terram against metal and stone ones, and against a spell, its own Form (DE pp. 206-209).
- **Schools of magical combat.** House Flambeau names six ways of fighting with magic, each with the Virtue that suits it: the Founder (fire; Puissant Ignem), Apromor (direct Perdo; Puissant Perdo), Boreas (cold; Puissant Ignem or Perdo), Ramius (mundane weapons with magical defences; Warrior), Sebastian (direct attacks with another Form; a Magical Focus) and Vilano (indirect spells; Puissant Finesse or Cautious with Finesse). The Cast a spell panel says which the magus's Virtues suit (Houses of Hermes: Societates pp. 25-30). Under the Variant House Benefits option a Flambeau may take the Ramius, Sebastian or Vilano Virtue as his House Virtue instead (p. 27).
- **Next Round** plays every turn left in the round, each fighter striking whoever attacked it last, or the first enemy in the order it may strike (a held fighter tries to break free).
- **Restart the Fight** clears the order and the chronicle. Wounds already written onto sheets stay.

A side with nobody standing loses. The fight then ends and its line says
who won, and a line saying so is written in the Diary of every character
who fought and of each side's covenant (the arms it fights under). A botch says so in the chronicle; the storyguide says what goes
wrong.

**See also:** [How to run a fight](help:guide-fights), [Conflicts](help:conflicts)

# A siege
<!-- help: sieges -->

A siege's castle has a Garrison (combat groups), Defenses and Supplies,
each with an interval. Its events come at the shortest of the three: a
day, a week, a month or a season (Lords of Men pp. 111-112). Each of the
castle's four walls has damage levels equal to its Defense Bonus x 3, or
x 4 for a castle of Size +9 or more (p. 112). That measure is fixed
when the siege's first event is played: a mine that lowers the
Defenses lowers the Defense Bonus at every wall (p. 114), not the walls'
damage levels, so a wall's gauge always reads against the whole it had
when the siege began. A wall at 0 stays at 0 and no longer gives its
Defense Bonus.

**Next Siege Event** plays one event, then moves the siege on by the
castle's interval:

- **Undermine a wall** (the besiegers need miners): their sapper's Intelligence + Profession: Sapper + stress die against the castle's counter-miner + the Defense Bonus (a step higher behind a moat) + stress die. A success takes the Defenses a step down, two on a botched defence. A botched attack loses a unit of miners.
- **Bombard a wall** (mangonels or trebuchets): the engines attack in groups of up to five, each group Intelligence + Siege Weapon + the engine's Attack + stress die against the castle's engineer (Intelligence + Profession: Siege Engineer) + the Defense Bonus + stress die. A hit costs the wall a damage level for each engine in the group.
- **Escalade**: play a battlefield event as in [Battles](help:section-nb-battles), then say who won. The garrison's Weight of Numbers and the Defense Bonus stand in for numbers and ground. Each besiegers' win takes the Garrison a step down, and a win at a Shoddy wall breaches the castle (p. 115). A wall battered to 0 no longer gives its Defense Bonus (p. 114), but that alone isn't a breach.
- **The garrison sallies out**: a battlefield event at Battle Ease Factor 9, against the miners, a group of engines or a group of soldiers. A garrison's win removes them.
- **The magi seal a breach**: the ritual Seal the Breach (CrTe 20, Lords of Men p. 116; its level from the errata) knits a wall back together, restoring up to five damage levels, never more than the wall had when the siege began.
- **Keep the stockade**: nothing but time passes.

A castle with besiegers at three walls or more is in stockade. Each time
its Supplies interval passes it makes a supplies roll: the Siege
Conditions Bonus + stress die against 3 + the Garrison's Weight of
Numbers + the years under siege (p. 112). A failure drops the Supplies a step,
and a failure at Shoddy means the castle surrenders. A botch (1 + the
full seasons besieged, in botch dice) means disease breaks out. The next
roll comes one interval after the last, at the Supplies as they then stand:
a failed roll at Standard brings the next a week later, not rolls for the
weeks already past. An interval that ends with no stockade passes with no
roll to make up later.

When a siege ends (a surrender or a breach, or Ended set by editing it),
a line saying how is written in the Diaries of the records it is linked
to: the covenant it concerns, the castle as a lord, town or place of the
Region, and the besieging lord.

Edit a siege to change anything the story changes: a relief force, a
spell that repairs a wall, the experts' totals, how it ended. Living
under siege costs -2 Living Conditions for each year with a season of
it.

<!-- gui -->
The siege's page shows the seasons it has run as medallions, drawn in
the set the saga chooses (the saga's settings, Medallion style): stained glass,
an illuminated letter's adornment, a wax seal, Limoges enamel, a Book of
Hours roundel, or pen and wash. Its gauges are bound in cord and read
off the book's own steps: the Garrison's 10, 20 and 40 groups, the four
qualities of Defenses and Supplies, and each wall's damage levels.
<!-- /gui -->

**See also:** [How to run a siege](help:guide-sieges), [Conflicts](help:conflicts)

# Siege Actions
<!-- help: siege-actions -->

More (or the button) on a siege, for what happens besides its events
(Lords of Men pp. 112-116):

- **Change Deployments** (p. 113): the units at each wall. Three walls
  held make a stockade; a wall the besiegers hold and the garrison leaves
  empty is named, since they may escalade it unopposed.
- **A Supplies Story or Spell**: a blockade drops the Supplies a step, a
  relief raises them (p. 112); Conjuration of Bread adds +7 to the next
  season's supplies rolls; Raise the Siege has the commander roll
  Intelligence + Leadership + a simple die against 12 to resist it. The
  spell (ReMe 30, Duration Sun) only makes him take a pessimistic view
  until sunset, so failing doesn't end the siege; if he gives it up,
  set the siege's Ended on Edit (p. 116). Seal the Breach is a Next Siege Event.
- **Run the Stockade**: the castle's intervals waited, as many as asked,
  each with the supplies rolls it brings, until the siege ends (p. 112's
  batch rolls). A failed roll reminds you that those inside make
  deprivation checks (ArM5 p. 180).
- **The Castle Taken** (p. 116): it is the besieger's now, with its
  governor and its fate, written in the Diaries.

A sally against the soldiers takes as many groups as you say (p. 115).

## Discipline, Morale and rallying
<!-- help: group-morale -->

With **Morale and Discipline for combat groups** on (the saga's settings;
Lords of Men pp. 134-135), a fight's groups have a spirit as well as
wounds. **Discipline or Morale** (More on a fight) rolls the group
leader's Presence + Leadership + a stress die, + the lowest Loyal
(Discipline) or Brave (Morale) when every member has a positive one,
against the cause's Ease Factor: Discipline when the group is tempted to
break formation (difficult ground 3, running 6, the enemy disengaging 6,
changing between melee and missiles 6, the enemy routing 9, disengaging
9), Morale when bad things happen (missiles with none to answer 6, a
charge by an equal force 6, by a superior one 9, an ambush 9, every
member at -3 or worse 9, its leader or vanguard down 9). A group with no
leader standing fails.

Failing either disorders the group. A trained group disordered fights as
an untrained one (no group bonus); failing a second Discipline check it
fights as a disordered untrained group, only half its attacks hitting
(rounded up), as an untrained group disordered does at once. Only a
failed Morale check routs a disordered group: a routed group won't
attack, and tries to disengage and flee. The fight's chronicle names the
Morale check a blow brings on (its leader or vanguard down, or every
member at -3 or worse). **Rally a Group** rolls the leader's Presence +
Leadership + a stress die against its situation (not engaged 3, under
missile fire 6, in melee 9, routed and hotly pursued 12), +1 with
casualties or +3 at half or more: a routed group becomes disordered, a
disordered one steady.

A battle's army disordered or routed (a failed rally after an event)
carries into the fight its next event is played as: each of its groups
starts disordered or routed (Lords of Men p. 106).

## More on a siege
<!-- help: siege-more -->

**From a lord's castle.** A new siege can start **From a lord's castle**:
one on a lord's Castles list (its Kind, Garrison groups, Supplies quality
and moat set there), filling the castle's name, Garrison, Supplies and
moat, and its Defenses by its kind: a free choice Standard, a minor
castle Superior, a great castle Excellent (Lords of Men p. 111).

**Experts as characters.** Each expert (the besiegers' sapper and engine
master, the castle's counter-miner and engineer) may be a character:
Intelligence + Profession: Sapper, Siege Weapon or Profession: Siege
Engineer from his sheet, in place of the total typed. Profession: Sapper
can't be used untrained; a character with Profession: Miner may run a
mine with three botch dice (p. 114).

**The garrison's engines.** Type the garrison's mangonels and trebuchets
and its engine master's Intelligence + Siege Weapon on Edit Siege; the
event **The garrison's engines fire back** fires each group once at the
besiegers' engine it picks (each group's own choice: the book targets
engines one by one, p. 116): + the engine's Attack + a stress die
against 6, each hit destroying the engine it strikes. The book gives the
counter-battery no Ease Factor, so 6, an engine's own Defense (p. 113),
is the app's. Ballistae don't destroy engines, so they take no part.

**Several walls.** Bombarding, each group of up to five engines is set
at its own wall, and each makes its attack against the castle's defence
there (p. 114).

**Outworks.** Up to three outworks on Edit Siege, each with its Defense
Quality (Superior, a minor castle's, unless you say): while one stands,
mines, engines and escalades strike it before the castle; an escalade won
there, or its walls battered to nothing, takes it (p. 114, optional). Its
damage levels use the castle's Size.

**An escalade as one battle.** Tick **Take the castle in one battle** on
an escalade: a battle on Conflicts between the troops at that wall, the
garrison's side taking its Garrison row's Weight of Numbers and the
Defense Bonus there in place of the usual ones (against the besiegers,
so subtracted from their Event Totals). The besiegers can't strike the
baggage; each event they win takes the Garrison a step down; and a day
they win at a Shoddy wall breaches the castle, after which Siege Actions
offers only The Castle Taken (pp. 114-115).

**Life inside.** Tick who is inside the castle (everyone of a besieged
covenant by default; a castle sends its children, sick and elderly away,
so untick them): each takes -2 Living Conditions for a year in which at least a season, 91 days, of the siege falls, counted from its start and the days it has run (p. 112).
**Raise the Veronese Flag** (Siege Actions, CrIm 30) shows illusory
men-at-arms on every wall until sunset, so no wall looks undefended
(p. 116).
