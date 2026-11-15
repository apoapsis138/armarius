# Conflicts
<!-- help: conflicts -->

Conflicts holds the saga's battles, fights and sieges.

- **A battle** between two armies is played as Lords of Men's few
  battlefield events (Lords of Men pp. 102-109).
- **A fight** is played blow by blow with the Definitive Edition's combat
  rules (DE pp. 394-398).
- **A siege** is played event by event with Lords of Men's siegecraft
  (pp. 111-116).

They belong to the whole saga, not to a covenant. A battle or siege that
names a lord shows in that lord's Fief too, so lords can fight and
besiege one another.

<!-- tui -->
In the navigation tree Conflicts sits after the Bestiary. Selecting it
shows its facts, then the Battles, Fights and Sieges lists, each over the
chosen row in full. In each list, `a` adds one, `e` edits the chosen one
and `d` deletes it. More (`m`) holds what plays them.
<!-- /tui -->
<!-- gui -->
On the saga's page, the Conflicts chapter lists the battles, the fights
and the sieges. A battle is acted on from its card. A fight or siege opens
its own page, drawn as a manuscript leaf. A fight's shows its order of
blows and the two sides under their arms. A siege's shows its castle's
plan, the season medallions and both armies.
<!-- /gui -->

**See also:** [How to run a fight](help:guide-fights), [How to run a siege](help:guide-sieges)

## Conflicts' facts
<!-- help: section-conflicts-info -->

How many battles, fights and sieges the saga has, and how many fights and
sieges are still going on.

## Conflicts
<!-- help: tab-conflicts -->

The Battles, Fights and Sieges lists, over the chosen one in full.

### Battles
<!-- help: section-conflict-battles -->

Every battle in the saga. The armies, columns and form are those of a
lord's [Battles](help:section-nb-battles). More's
**Battle Event** plays the chosen battle's next event (see [Battle
Event](help:battle-event)).

### Fights
<!-- help: section-fights -->

Each fight's name, when and where, its two sides, and the fighters still
standing on each. It also says whether the fight has begun, its round, or
how it ended. The panel below shows the chosen fight in full:

- the order of blows, the one acting now marked
- each side's fighters, with their figures and wounds
- the last blow, worked out line by line
- the chronicle

<!-- tui -->
More on a fight: **Add Combatant**, **Edit Combatant**, **Remove
Combatant**, **Form a Group**, **Break up a Group**, **Next Blow**,
**Next Round** and **Restart the Fight**.
<!-- /tui -->

### Sieges
<!-- help: section-sieges -->

Each siege's name, its castle and besieger, the Garrison in combat groups,
the Defenses and Supplies, and how long it has run or how it ended. The
panel below shows the chosen siege in full:

- the castle's figures and the interval its events come at
- each wall's damage levels
- the besiegers' miners, engines and soldiers
- the chronicle

<!-- tui -->
More on a siege: **Next Siege Event**.
<!-- /tui -->

# A fight
<!-- help: fights -->

A fight has two sides. Each side has combatants, and some of them may
fight together in combat groups.

The app keeps no map, since the Definitive Edition's combat has no
positions, only who acts when and whom they strike. Where the fight
happens is the fight's Where, and getting the fighters there is the
story's. Each blow names its target, and Disengage is how a fighter
leaves.

- **Add Combatant** adds one of these to a side:
  - A character with one of the weapons they carry. Their figures, wounds and Fatigue come from their sheet, and wounds they take are written onto it.
  - A creature of the Bestiary with one of its attacks. Its figures are copied. You can add several at once (Wolf 1, Wolf 2...), each with its own wounds.
  - A fighter with figures typed in, such as Init, Attack, Defence, Damage, Soak, Size, Combat Ability and Leadership.

  A character with no weapon fights with the book's Fist. Any of them may also be:
  - **Mounted**. Ride, at most +3, adds to its Attack and Defence (DE p. 397). A character's Ride comes from the sheet, and a typed fighter's is typed. A Gifted rider without the Gentle Gift is warned that a horse throws them without magic (DE pp. 82, 205). A mounted character's lance fights as a Single Weapon. On foot it's a long spear, fought with Great Weapon (DE pp. 400-401; Lords of Men p. 126).
  - **Defending** another on its side, as a shield grog defends a magus. While a defender stands, nobody may strike the one it defends. Only a defender's botched Defence lets a blow through to them (DE p. 397).
  - Given a **Magic Resistance**, such as a creature's Might, against spells and devices. A magus's comes from Parma and Form.
  - **Invisible**, with how clear the signs that betray it are. See **Invisible fighters** below.

  The panel at the foot of the form, **The Fighter**, shows the fighter as the fight will see it.
- **Edit Fight** also sets the **Range increments** between the sides (0
  is hand to hand) and the **Magic aura** where they fight. At range only
  missiles strike, at -3 for each increment past the first (DE p. 395).
  The aura adds to every Casting Total.
- **Form a Group** joins one to six fighters of a side, with a vanguard
  (DE pp. 395-396).
  - A trained group, one that spent a season improving combat skills
    together, also has a leader.
  - The group fights with the vanguard's figures.
  - A trained group's other members add their Combat Abilities to its
    Attack or its Defence, at most three times the leader's Leadership.
  - A note says when the members' totals run more than five points apart,
    which a group's shouldn't when it forms.
- **Next Blow** plays the turn of whoever acts now. The first Next Blow
  rolls everyone's Initiative (Init + stress die, once for the whole
  fight). Then each acts in order, highest first. Choose the action and
  who it strikes. Only the actions the fighter can take are offered. The
  panel at the foot of the form, **The Blow to Come**, says what the
  action does and the totals it rolls, or why it can't be done. Riding,
  range, the group bonus and the Form Bonus are all included. The actions
  are listed below, under **The actions**.
- A group's hit lands once for each of its fighters, spread over the
  defending group with its vanguard taking the most. When a group's
  vanguard or leader falls, the group splits into individuals.
- A magus's **Form Bonus** (the Form / 5, rounded up) adds to Soak against
  harm of its Form (DE pp. 206-209):
  - Animal against teeth and claws
  - Corpus against bare hands
  - Herbam against wooden weapons
  - Terram against metal and stone ones
  - against a spell, its own Form
- **Schools of magical combat.** House Flambeau names six ways of fighting
  with magic, each with the Virtue that suits it (Houses of Hermes:
  Societates pp. 25-30). The Cast a spell panel says which the magus's
  Virtues suit.
  - the Founder: fire, with Puissant Ignem
  - Apromor: direct Perdo, with Puissant Perdo
  - Boreas: cold, with Puissant Ignem or Perdo
  - Ramius: mundane weapons with magical defences, with Warrior
  - Sebastian: direct attacks with another Form, with a Magical Focus
  - Vilano: indirect spells, with Puissant Finesse or Cautious with
    Finesse

  Under the Variant House Benefits option a Flambeau may take the Ramius, Sebastian or Vilano Virtue as their House Virtue instead (p. 27).
- **Next Round** plays every turn left in the round. Each fighter strikes
  whoever attacked it last, or the first enemy in the order it may strike.
  A held fighter tries to break free.
- **Restart the Fight** clears the order and the chronicle. Wounds already
  written onto sheets stay.

**Invisible fighters.** The signs that betray one are, clearest first:

- **Obvious**, such as a visible sword, mud or wading
- **Clear**, such as a shadow in sunlight or footprints in sand
- **Indistinct**, such as a shadow on a cloudy day or packed earth
- **Faint**, such as a shadow in moonlight or cobblestones
- **No signs**

In that order, they give the invisible fighter:

- +1, +3, +3, +6 or +9 to a melee Attack
- +3, +3, +6, +9 or +9 to Defence
- +3, +3, +6, +9 or +12 to Stealth

A foe must locate an invisible fighter before striking, shooting or
casting at it, unless the two are engaged hand to hand. Obvious signs need
no search, and No signs can be found by sound alone. An invisible fighter
nobody has found acts first in the first round, and adds +3 to its Attack
against a foe who hasn't located it.

Its weapon and its touch are magical too, so a target with Magic
Resistance keeps them out, whatever its signs. Tick **Weapon picked up
after turning invisible** for a non-magical weapon taken up once
invisible, which stays visible and gets through. Bare hands never do, so a
scuffle or grapple is still kept out. Obvious signs set the bonuses and
let foes find it without a search. They don't make its blow non-magical.

An invisible fighter can't fight in a trained group. An untrained group
rolls a botch die more for each invisible member, and nobody can defend
it (Houses of Hermes: Societates pp. 32-33; Errata p. 58; DE p. 223).

**The actions.** Next Blow offers these:

- **Attack**: Attack + stress die against Defence + stress die. A hit adds
  the Attack Advantage to Damage, and what passes Soak is read on the
  Damage Table for the defender's Size. Against a missile weapon only a
  shield's Defence counts. Against a hand-held Greek Fire siphon not even
  that counts. The fire splashes round the shield, and its Defence adds to
  the defender's Soak instead (The Sundered Eagle p. 47).
- **Attack with Exertion**: spends a Fatigue level, each member's in a
  group, for + the Combat Ability.
- **Charge**: moves and attacks for + the Combat Ability, never across
  difficult ground. It spends a Fatigue level: the charger's on foot, or
  mounted the horse's, which the app doesn't track. A mounted charge that
  hits a target smaller than **The horse's Size** tests its shock (Lords
  of Men pp. 123, 126-127).
  - The target rolls Dexterity + Ride + saddle if mounted, or Strength +
    Size + Combat Ability on foot, + a stress die. **The target's saddle**
    is +3 for cantled, -3 for no stirrups.
  - That's against the Damage Total before Soak + the horse's Size.
  - Failing, the target is unhorsed or knocked down, prone.

  Combat Options works the other mounted rules out.
- **Scuffle**: knocks out rather than kills. The wound becomes Fatigue by
  the Scuffle Effects table. With a real weapon it's at -3 to Attack and
  without the weapon's Damage.
- **Disarm, Trip, Grab worn item, Take the weapon your opponent is
  using**: succeed with an Attack Advantage of 9, 3, 6 or 12, and deal no
  damage.
- **Grapple**: with bare hands and Brawl. Any Attack Advantage above 0
  takes hold, and becomes or adds to the Grapple Strength. The card says
  who holds whom (DE p. 398).
- **Break free**: offered to one held, who may otherwise only cast, use a
  device or wait. It's an attack on the one holding them, and its
  Advantage comes off the Grapple Strength. At 0 they're free and the
  holder takes a Light Wound. A grip lets go when either falls.
- **Split the group**: against an enemy group while another unit of your
  side presses it. An Advantage of 0 or more splits it rather than
  wounding it. It splits in half, or in thirds when three or more press it
  and a second split succeeds that round. A part of one fights alone (DE
  p. 398).
- **Locate the unseen**: offered while an invisible foe hasn't been found.
  A round spent searching rolls Perception + Awareness + stress die against its
  Dexterity + Stealth - Encumbrance + its Stealth bonus + stress die.
  Beating it locates the foe, who may then be struck, shot and targeted
  (Houses of Hermes: Societates p. 32). A typed fighter searches and hides
  with 0 besides the bonus.
- **Amid a battle**: in a battle event's fight, or one marked **Part of a
  battle** on Edit Fight, a magus must first pass a Concentration roll to
  cast (Lords of Men p. 109; DE p. 215). It's Stamina + Concentration + a
  stress die against 12, or 9 with **Standing off, not engaged** ticked.
  Failing it, the spell is lost. A Group target rarely fits a battle's mass
  of troops. A unit separated from the army is reached with one magnitude
  more (100 people), and a Boundary a magnitude more covers about 300
  paces.
- **Cast a spell**: a magus casts one of the spells they know, or
  spontaneous magic (its Arts and level, fatiguing or not), at their place
  in the order (DE pp. 214-215, 394, 397).
  - Formulaic: Casting Score + stress die, cast if no more than 10 short of
    the level. Falling short costs a Fatigue level.
  - Spontaneous: (score + stress die) / 2 for a Fatigue level, or score / 5.
    The spell fails if that falls short of the level asked for, unless
    Life-Linked Spontaneous Magic pays a Fatigue level more for each 5
    short.
  - Incompatible Arts forbid a spell, and Painful Magic brings a level of
    pain with each.
  - **Casting requisite** (a Technique, a Form, or both) adds the Arts this
    use of the spell needs. The spell is cast with the lowest Technique and
    Form among its Arts, its own requisites and these (DE p. 312).
  - Then Penetration (Casting Total - level + Penetration) against the
    target's Magic Resistance. Any damage is stress die + X against Soak,
    with the Form's Bonus, + stress die.
  - A mastered spell adds its Mastery score to the Casting Score, and takes
    that many botch dice off, to none. With the Penetration Mastery ability
    it adds to Penetration too. A target who mastered the same spell has
    their Magic Resistance doubled against it (DE pp. 225-226).
  - **Arcane Connection** multiplies Penetration by how long it lasts, +1
    for hours or days, +2 weeks or months, +3 years or decades, +4
    indefinitely. With one, **Knows the target's name** adds +1 and
    **Symbolic representation** +2 (DE pp. 219-220; Houses of Hermes:
    Societates p. 27).
  - **Indirect (aimed)**: a spell that moves or makes something mundane
    that then strikes isn't stopped by Magic Resistance, but must be aimed.
    The roll is Perception + Finesse + stress die, +6 for each **Size
    step** past a basic Individual, +1 for each Precise Casting. It's
    against the target's Defence as against a missile + stress die. A hit
    does the damage with no Attack Advantage (DE pp. 223, 226; Houses of
    Hermes: Societates pp. 30, 32).
  - The 18 spells Houses of Hermes: Societates p. 30 lists, such as Pit of
    the Gaping Earth and End of the Mighty Castle, are indirect without
    asking. So is the Invisible Sling of Vilano, one of its new spells
    (p. 38).
  - Several are only partly indirect, and the panel says how. The corpse
    spells (Awaken the Slumbering Corpse, Strings of the Unwilling
    Marionette, The Walking Corpse) get through only with a non-magical
    weapon the corpse wields. The Earth Split Asunder's fall isn't
    resisted, but its crush when it closes is. The waves capsize a boat or
    wash out a bridge rather than harm directly. The moving flames still
    burn.
  - Weaver's Trap of Webs, Footsteps of Slippery Oil, Trap of the
    Entwining Vines and Coils of the Entangling Plants hold or trap and do
    no harm themselves. A Damage typed for them is refused.
  - An invisible foe nobody has found can be reached only by an area spell
    (Group, Room, Structure, Boundary) or one cast through an Arcane
    Connection. Eye range works neither on nor by an invisible fighter
    (Houses of Hermes: Societates p. 32).
  - The panel also names the magus's school of magical combat (see
    **Schools of magical combat** above).
- **Use a device**: one effect of a device the character holds, with no
  Fatigue. Its Penetration is what it was enchanted with, 0 unless more,
  against Magic Resistance. Any damage is as for a spell (DE p. 259).
  Marked **Indirect (aimed)**, it isn't resisted but is aimed with the
  wielder's Perception + Finesse, as a spell is (DE p. 223).
- **Disengage**: a Defence Total against every attacker of the last round,
  +3 for each try after the first. A fighter unattacked since its last
  turn leaves freely.
- **Wait**: passes the turn.

A side with nobody standing loses. The fight then ends and its line says
who won. A line saying so is written in the Diary of every character who
fought, and of each side's covenant (the arms it fights under). A botch
says so in the chronicle, and the storyguide says what goes wrong.

**See also:** [How to run a fight](help:guide-fights), [Conflicts](help:conflicts)

# A siege
<!-- help: sieges -->

A siege's castle has a Garrison (combat groups), Defenses and Supplies,
each with an interval. Its events come at the shortest of the three: a
day, a week, a month or a season (Lords of Men pp. 111-112).

Each of the castle's four walls has damage levels equal to its Defense
Bonus x 3, or x 4 for a castle of Size +9 or more (p. 112). That measure
is fixed when the siege's first event is played. A mine that lowers the
Defenses lowers the Defense Bonus at every wall (p. 114), not the walls'
damage levels. So a wall's gauge always reads against the whole it had
when the siege began. A wall at 0 stays at 0 and no longer gives its
Defense Bonus.

**Next Siege Event** plays one event, then moves the siege on by the
castle's interval:

- **Undermine a wall**, if the besiegers have miners. Their sapper's
  Intelligence + Profession: Sapper + stress die is against the castle's
  counter-miner + the Defense Bonus + stress die. The Defense Bonus counts
  a step higher behind a moat. A success takes the Defenses a step down,
  two on a botched defence. A botched attack loses a unit of miners.
- **Bombard a wall**, with mangonels or trebuchets. The engines attack in
  groups of up to five. Each group rolls Intelligence + Siege Weapon + the
  engine's Attack + stress die. That's against the castle's engineer
  (Intelligence + Profession: Siege Engineer) + the Defense Bonus + stress
  die. A hit costs the wall a damage level for each engine in the group.
- **Escalade**: play a battlefield event as in
  [Battles](help:section-nb-battles), then say who won. The garrison's
  Weight of Numbers and the Defense Bonus stand in for numbers and ground.
  Each besiegers' win takes the Garrison a step down, and a win at a
  Shoddy wall breaches the castle (p. 115). A wall battered to 0 isn't by
  itself a breach (p. 114).
- **The garrison sallies out**: a battlefield event at Battle Ease Factor
  9, against the miners, a group of engines or a group of soldiers. A
  garrison's win removes them.
- **The magi seal a breach**: the ritual Seal the Breach (CrTe 20, Lords
  of Men p. 116, its level from the errata) knits a wall back together. It
  restores up to five damage levels, never more than the wall had when the
  siege began.
- **Keep the stockade**: nothing but time passes.

A castle with besiegers at three walls or more is in stockade. Each time
its Supplies interval passes it makes a supplies roll: the Siege
Conditions Bonus + stress die against 3 + the Garrison's Weight of Numbers
+ the years under siege (p. 112).

- A failure drops the Supplies a step. A failure at Shoddy means the
  castle surrenders.
- A botch means disease breaks out. It rolls 1 + the full seasons
  besieged in botch dice.
- The next roll comes one interval after the last, at the Supplies as they
  then stand. A failed roll at Standard brings the next a week later, not
  rolls for the weeks already past.
- An interval that ends with no stockade passes with no roll to make up
  later.

When a siege ends, by a surrender, a breach or Ended set by editing it, a
line saying how is written in the Diaries of the records it's linked to.
Those are the covenant it concerns, the castle as a lord, town or place of
the Region, and the besieging lord.

Edit a siege to change anything the story changes, such as a relief
force, a spell that repairs a wall, the experts' totals, or how it ended.
Living under siege costs Living Conditions (see **Life inside** under
[More on a siege](help:siege-more)).

<!-- gui -->
The siege's page shows the seasons it has run as medallions, drawn in the
set the saga chooses (the saga's settings, Medallion style). The sets are
stained glass, an illuminated letter's adornment, a wax seal, Limoges
enamel, a Book of Hours roundel, or pen and wash. Its gauges are bound in
cord and read off the book's own steps: the Garrison's 10, 20 and 40
groups, the four qualities of Defenses and Supplies, and each wall's
damage levels.
<!-- /gui -->

**See also:** [How to run a siege](help:guide-sieges), [Conflicts](help:conflicts)

# Siege Actions
<!-- help: siege-actions -->

More (or the button) on a siege, for what happens besides its events
(Lords of Men pp. 112-116):

- **Change Deployments** (p. 113): the units at each wall. A wall the besiegers hold and the garrison leaves
  empty is named, since they may escalade it unopposed.
- **A Supplies Story or Spell**:
  - A blockade drops the Supplies a step, and a relief raises them
    (p. 112).
  - Conjuration of Bread adds +7 to the next season's supplies rolls.
  - Raise the Siege has the commander roll Intelligence + Leadership + a
    simple die against 12 to resist it. The spell (ReMe 30, Duration Sun)
    only makes them take a pessimistic view until sunset, so failing
    doesn't end the siege. If the commander gives it up, set the siege's
    Ended on Edit (p. 116).
  - Seal the Breach is a Next Siege Event.
- **Run the Stockade**: the castle's intervals waited, as many as asked,
  each with the supplies rolls it brings, until the siege ends. These are
  p. 112's batch rolls. A failed roll reminds you that those inside make
  deprivation checks (ArM5 p. 180).
- **The Castle Taken** (p. 116): it's the besieger's now, with its
  governor and its fate, written in the Diaries.

A sally against the soldiers takes as many groups as you say (p. 115).

## Discipline, Morale and rallying
<!-- help: group-morale -->

With **Morale and Discipline for combat groups** on in the saga's
settings, a fight's groups have a spirit as well as wounds (Lords of Men
pp. 134-135). **Discipline or Morale**, in More on a fight, rolls the
group leader's Presence + Leadership + a stress die. It adds the lowest
Loyal (Discipline) or Brave (Morale) when every member has a positive one.
The roll is against the cause's Ease Factor:

- **Discipline**, when the group is tempted to break formation: difficult
  ground 3, running 6, the enemy disengaging 6, changing between melee and
  missiles 6, the enemy routing 9, disengaging 9.
- **Morale**, when bad things happen: missiles with none to answer 6, a
  charge by an equal force 6, by a superior one 9, an ambush 9, every
  member at -3 or worse 9, its leader or vanguard down 9.

A group with no leader standing fails.

Failing either disorders the group.

- A trained group disordered fights as an untrained one, with no group
  bonus.
- Failing a second Discipline check, it fights as a disordered untrained
  group, only half its attacks hitting (rounded up). An untrained group
  disordered does so at once.
- Only a failed Morale check routs a disordered group. A routed group
  won't attack, and tries to disengage and flee.

The fight's chronicle names the Morale check a blow brings on, when its
leader or vanguard is down or every member is at -3 or worse.

**Rally a Group** rolls the leader's Presence + Leadership + a stress die
against the group's situation: not engaged 3, under missile fire 6, in
melee 9, routed and hotly pursued 12. It's +1 with casualties, or +3 at
half or more. A routed group becomes disordered, and a disordered one
steady.

A battle's army disordered or routed, by a failed rally after an event,
carries that into the fight its next event is played as. Each of its
groups starts disordered or routed (Lords of Men p. 106).

## More on a siege
<!-- help: siege-more -->

**From a lord's castle.** A new siege can start **From a lord's castle**,
one on a lord's Castles list, where its Kind, Garrison groups, Supplies
quality and moat are set. It fills in the castle's name, Garrison,
Supplies and moat, and its Defenses by its kind (Lords of Men p. 111):

- a free choice: Standard
- a minor castle: Superior
- a great castle: Excellent

**Experts as characters.** Each expert may be a character, whether the
besiegers' sapper and engine master or the castle's counter-miner and
engineer. The
sheet's Intelligence + Profession: Sapper, Siege Weapon or Profession:
Siege Engineer is used in place of the total typed. Profession: Sapper
can't be used untrained. A character with Profession: Miner may run a mine
with three botch dice (p. 114).

**The garrison's engines.** Type the garrison's mangonels and trebuchets,
and its engine master's Intelligence + Siege Weapon, on Edit Siege. The
event **The garrison's engines fire back** fires each group once at the
besiegers' engine it picks. Each group chooses its own, as the book
targets engines one by one (p. 116). The roll adds the engine's Attack and
a stress die, against 6, and each hit destroys the engine it strikes. The
book gives the counter-battery no Ease Factor, so 6, an engine's own
Defense (p. 113), is the app's. Ballistae don't destroy engines, so they
take no part.

**Several walls.** Bombarding, each group of up to five engines is set at
its own wall. Each makes its attack against the castle's defence there
(p. 114).

**Outworks.** Up to three outworks on Edit Siege, each with its Defense
Quality. That's Superior, a minor castle's, unless you say. While one
stands, mines, engines and escalades strike it before the castle. An
escalade won there, or its walls battered to nothing, takes it (p. 114,
optional). Its damage levels use the castle's Size.

**An escalade as one battle.** Tick **Take the castle in one battle** on
an escalade. It's a battle on Conflicts between the troops at that wall.
The garrison's side takes its Garrison row's Weight of Numbers and the
Defense Bonus there in place of the usual ones. Both count against the
besiegers, so they're subtracted from their Event Totals (pp. 114-115).

- The besiegers can't strike the baggage.
- Their wins step the Garrison down and breach a Shoddy wall, as an
  ordinary escalade's do. After a breach, Siege Actions offers only The
  Castle Taken.

**Life inside.** Tick who is inside the castle. Everyone of a besieged
covenant is ticked by default. A castle sends its children, sick and
elderly away, so untick them. Each takes -2 Living Conditions for a year
in which at least a season, 91 days, of the siege falls. That's counted
from its start and the days it has run (p. 112).

**Raise the Veronese Flag** (Siege Actions, CrIm 30) shows illusory
men-at-arms on every wall until sunset, so no wall looks undefended
(p. 116).
