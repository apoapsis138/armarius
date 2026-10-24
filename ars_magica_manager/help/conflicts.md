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
  - **Mounted**: Ride, at most +3, adds to its Attack and Defence (DE p. 397). A character's Ride comes from the sheet; a typed fighter's is typed. A Gifted rider (not the Gentle Gift) is warned that a horse throws them without magic (DE pp. 82, 205).
  - **Defending** another on its side, as a shield grog defends a magus: while a defender stands, nobody may strike the one it defends, and only a defender's botched Defence lets a blow through to them (DE p. 397).
  - Given a **Magic Resistance** (a creature's Might), against spells and devices; a magus's comes from Parma and Form.

  The panel at the foot of the form, **The Fighter**, shows the fighter as the fight will see it.
- **Edit Fight** also sets the **Range increments** between the sides (0: hand to hand) and the **Magic aura** where they fight. At range only missiles strike, at -3 for each increment past the first (DE p. 395); the aura adds to every Casting Total.
- **Form a Group** joins one to six fighters of a side, with a vanguard. A trained group (one that spent a season improving combat skills together) also has a leader. The group fights with the vanguard's figures. A trained group's other members add their Combat Abilities, at most three times the leader's Leadership, to its Attack or its Defence. A note says when the members' totals run more than five points apart, which a group's shouldn't when it forms (DE pp. 395-396).
- **Next Blow** plays the turn of whoever acts now. The first Next Blow rolls everyone's Initiative (Init + stress die, once for the whole fight); then each acts in order, highest first. Choose the action and who it strikes. Only the actions the fighter can take are offered, and the panel at the foot of the form, **The Blow to Come**, says what the action does and the totals it rolls (riding, range, group bonus and Form Bonus included), or why it can't be done:
  - **Attack**: Attack + stress die against Defence + stress die. A hit adds the Attack Advantage to Damage; what passes Soak is read on the Damage Table for the defender's Size. Against a missile weapon only a shield's Defence counts.
  - **Attack with Exertion**: spends a Fatigue level (each member's, in a group) for +the Combat Ability.
  - **Scuffle**: knocks out rather than kills. The wound becomes Fatigue by the Scuffle Effects table, at -3 to Attack and without the weapon's Damage when fighting with a real weapon.
  - **Disarm, Trip, Grab worn item, Take the weapon your opponent is using**: succeed with an Attack Advantage of 9, 3, 6 or 12, and deal no damage.
  - **Grapple**: with bare hands and Brawl. Any Attack Advantage above 0 takes hold, and becomes (or adds to) the Grapple Strength; the card says who holds whom (DE p. 398).
  - **Break free**: offered to one held, who may otherwise only cast, use a device or wait. An attack on the one holding them: its Advantage comes off the Grapple Strength, and at 0 they are free and the holder takes a Light Wound. A grip lets go when either falls.
  - **Split the group**: against an enemy group while another unit of your side presses it. An Advantage of 0 or more splits it rather than wounding it: in half, or in thirds when three or more press it and a second split succeeds that round; a part of one fights alone (DE p. 398).
  - **Cast a spell**: a magus casts one of the spells they know, or spontaneous magic (its Arts and level, fatiguing or not), at their place in the order. Formulaic: Casting Score + stress die, cast if no more than 10 short of the level (a Fatigue level when short). Spontaneous: (score + stress die) / 2 for a Fatigue level, or score / 5. Then Penetration (Casting Total - level + Penetration) against the target's Magic Resistance, and any damage: stress die + X against Soak (with the Form's Bonus) + stress die (DE pp. 214-215, 394, 397).
  - **Use a device**: one effect of a device the character holds, with no Fatigue; its Penetration is what it was enchanted with (0 unless more), against Magic Resistance, and any damage as for a spell (DE p. 259).
  - **Disengage**: a Defence Total against every attacker of the last round, +3 for each try after the first. Unattacked since its last turn, a fighter leaves freely.
  - **Wait**: passes the turn.
- A group's hit lands once for each of its fighters, spread over the defending group with its vanguard taking the most. When a group's vanguard or leader falls, the group splits into individuals.
- A magus's **Form Bonus** (the Form / 5, rounded up) adds to Soak against harm of its Form: Animal against teeth and claws, Corpus against bare hands, Herbam against wooden weapons, Terram against metal and stone ones, and against a spell, its own Form (DE pp. 206-209).
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
x 4 for a castle of Size +9 or more. A wall at 0 no longer gives its
Defense Bonus.

**Next Siege Event** plays one event, then moves the siege on by the
castle's interval:

- **Undermine a wall** (the besiegers need miners): their sapper's Intelligence + Profession: Sapper + stress die against the castle's counter-miner + the Defense Bonus (a step higher behind a moat) + stress die. A success takes the Defenses a step down, two on a botched defence. A botched attack loses a unit of miners.
- **Bombard a wall** (mangonels or trebuchets): the engines attack in groups of up to five, each group Intelligence + Siege Weapon + the engine's Attack + stress die against the castle's engineer (Intelligence + Profession: Siege Engineer) + the Defense Bonus + stress die. A hit costs the wall a damage level for each engine in the group.
- **Escalade**: play a battlefield event as in [Battles](help:section-nb-battles), then say who won. The garrison's Weight of Numbers and the Defense Bonus stand in for numbers and ground. Each besiegers' win takes the Garrison a step down, and a win at a Shoddy or broken wall breaches the castle.
- **The garrison sallies out**: a battlefield event at Battle Ease Factor 9, against the miners, a group of engines or a group of soldiers. A garrison's win removes them.
- **Keep the stockade**: nothing but time passes.

A castle with besiegers at three walls or more is in stockade. Each time
its Supplies interval passes it makes a supplies roll: the Siege
Conditions Bonus + stress die against 3 + the Garrison's Weight of
Numbers + the years under siege. A failure drops the Supplies a step,
and a failure at Shoddy means the castle surrenders. A botch (1 + the
full seasons besieged, in botch dice) means disease breaks out.

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
the set the saga chooses (Edit Saga, Season medallions): stained glass,
an illuminated letter's adornment, a wax seal, Limoges enamel, a Book of
Hours roundel, or pen and wash. Its gauges are bound in cord and read
off the book's own steps: the Garrison's 10, 20 and 40 groups, the four
qualities of Defenses and Supplies, and each wall's damage levels.
<!-- /gui -->

**See also:** [How to run a siege](help:guide-sieges), [Conflicts](help:conflicts)
