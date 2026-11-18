# Plan Season
<!-- help: plan-season -->

Plans what a magus, companion or Mythic Companion does with a season: the current one, or one up to a year ahead. Nothing changes when you save. The plan is applied when the saga is advanced
<!-- tui -->
with `t`.
<!-- /tui -->
<!-- gui -->
with **Advance Season**, under the chapters on the left.
<!-- /gui -->
Grogs aren't planned season by season. They have a [yearly update](help:grog-year) instead.

**You type:**

- **Season**: the one it was opened for. Choose another of the year ahead to move the plan there.
- **Activity**, from a list you can filter by Type and Book (see [Choosing the activity](help:plan-season-activity)).
- The fields that activity needs, such as what the experience goes into, a book, a teacher, a Source Quality or a die roll.
- Months lost to distractions, and Notes.
- **For**: this season only, until the work is done, or a number of seasons (see [For several seasons](help:plan-season-repeat)).

**The app works out:** what the season will give, on [the line above Save](help:plan-season-preview), from the character and the saga as they stand now. A season ahead is worked out from the character as the seasons planned before it will leave them, as the [Seasons Ahead](help:section-char-ahead) are, with a die not rolled yet counted as nothing gained. A season that already has a plan can't be chosen for another one. Change that plan, or clear it first.

### For several seasons
<!-- help: plan-season-repeat -->

**For** plans the same activity for the seasons straight after this one too. It stops at the first season that already has a plan.

- **This season**: only this one. Changing one season of a longer plan this way keeps the seasons planned after it.
- **Until it's done**: as many seasons as the work needs, as things stand now. That's reading a summa until the reader's score reaches its Level, writing a summa, or copying or translating a book until it's finished. Lab work over several seasons is always planned this way, from the laboratory's **Planning**. The line above Save says how many seasons that is.
  - Each season of it is worked out again after it's played. One interrupted, or one that gave less than expected, adds a season at the end. One that finishes the work early clears the seasons no longer needed.
  - If the season after the last is already planned, the last season says the work needs more, and Seasons Ahead shows "(needs more seasons)".
  - At most ten years are planned at once.
- **2 seasons** to **4 seasons**: the plan repeated that many times, for any activity, such as practice, exposure or a companion's working seasons. These aren't worked out again.

Choosing For again on a season of a longer plan replaces the seasons planned after it. Clearing the first season asks whether to clear the later ones too.

See [Interruptions](help:advance-interrupted) for how a season is marked interrupted.

### Paired plans
<!-- help: plan-season-pairs -->

Some seasons take another person's season too. Saving one plans the other for the same season:

- **Be taught** plans the teacher's **Teach** (Exposure in Teaching). A teacher already teaching that season is left as they are, so two students can share one.
- **Be trained** plans the master's season working at the Ability, as Exposure in it with "Training (name)" in its Notes. A master who already has a plan keeps it, since training doesn't need the master's season.
- **Teach** with a **Student** and **Teaching them** plans the student's **Be taught** from the teacher.
- Lab work naming an **Assistant** plans the helper's **Assist in a laboratory** for each season of the work.

If the other person already has a different plan that season, Save is refused with the reason, so nothing is replaced without asking. Change or clear that plan first. The line above Save says whose season will be planned too. Changing the plan to another activity clears the season it made.

Clearing either side clears both, after one question that names both people. A Teach another student still needs stays. Clearing an assistant's season only takes them off the lab work.

### Where it's opened from
<!-- help: plan-season-where -->

<!-- tui -->
- A character's **Planning** tab, in the This Season section. `a` or `e` plans the season or changes the plan, and `d` clears it after a confirmation.
- The same tab's [Seasons Ahead](help:section-char-ahead). Highlight a season and press `e` to plan it or change its plan, `a` to plan the first free one, or `d` to clear one.
- A covenant's **Seasons** tab. Highlight someone in the Magi or Companions list and press `a` or `e` to plan, or `d` to clear the plan.
<!-- /tui -->
<!-- gui -->
- A character's **Planning** chapter, in the This Season section. **Plan** plans the season. Once it's planned, **Edit** changes the plan and **Clear** clears it after a confirmation.
- The same chapter's [Seasons Ahead](help:section-char-ahead). Click a season, then **Edit** to plan it or change its plan, or **Clear** to clear it. **Plan** plans the first free one.
- A covenant's **Seasons** chapter. Click someone in the Magi or Companions list, then **Plan** to plan their season or change the plan, or **Clear** to clear it.
<!-- /gui -->

A magus's laboratory work is planned on the laboratory's [Planning list](help:tab-lab-planning), not here. That covers inventing spells, enchanting, extracting vis, a Longevity Ritual, binding a familiar, and setting up or refining a laboratory. See also [inventing a spell](help:invent-spell). A character's This Season names the laboratory when their season is lab work.

### Choosing the activity
<!-- help: plan-season-activity -->

<!-- tui -->
Press Enter on **Activity** to open the list of activities this character may plan.
<!-- /tui -->
<!-- gui -->
Click **Activity** to open the list of activities this character may plan.
<!-- /gui -->
It's grouped by Type, what the season is for:

- Study
- Writing & books
- Work & trade
- Teaching & apprentices
- Faith
- Order & covenant
- Mysteries
- Adventure & travel
- Rest & other
- Tradition, a hedge tradition's own seasons, shown to its members only.

To narrow the list:

- **Type** above the list shows one group only.
<!-- tui -->
  F2 steps through the Types, and back to all of them.
<!-- /tui -->
- **Book** shows the activities of one sourcebook, or of the core rules.
- **Search**: type any part of an activity's name or summary.
- **Recent**: the character's last three activities, from their plans and Diary, head the list until a Type or Book is chosen or a search typed.
<!-- tui -->
- F3 also lists the activities of sourcebooks not in play in this saga, marked. They can't be planned until the book is in play (Saga Content).
<!-- /tui -->
<!-- gui -->
- **Show everything** also lists the activities of sourcebooks not in play in this saga, marked. They can't be planned until the book is in play (Saga Content).
<!-- /gui -->

The highlighted activity's summary, Type, sourcebook and rule are shown beside the list. The list itself shows only names. Choosing one closes the list, and the form shows the fields it needs.

### Activities offered
<!-- help: plan-season-activities -->

The Activity list offers what this character may do. Activities marked "magi" are offered to magi only.

- **Study and experience:** Work / Exposure, Practice, Read a book, Be taught, Teach, Be trained, Study from vis (magi) and Adventure.
- **Books:**
  - Write a summa.
  - Write a tractatus on an Art, an Ability or a spell's Mastery (DE p. 379). An author writes at most half their Ability score, or a fifth of their Art score, rounded up, in tractatus on it. Only their originals count toward that, not copies or translations of them.
  - Copy a book. A book on the Arts or Parma Magica needs Magic Theory 1, and one on a Supernatural Ability needs that Ability or a Realm Lore at 1. Otherwise the copy is corrupt (DE p. 381).
  - Translate a book.
  - Copy Lab Texts, or Casting Tablets.
  - Edit a florilegium. It binds the tractatus on one subject you can get at, as many as you could write on it, from a collection twice that size. Each adds +1 Quality, or +2 for an authority (Ability 10 or Art 35) from a collection five times the size. Editing at all needs Ability 6 or Art 20.
  - Write Casting Tablets (magi) of a spell they've mastered. A season writes Latin x 20 levels, as many tablets as that holds.
  - Rewrite Lab Texts for general use (magi).
  - Teach Lab Text abbreviations (magi).
- **Apprentices and research (magi):** Search for an apprentice, Open an apprentice's Arts, Teach a Hermetic Virtue and Seek an insight.
  - **Teach a Hermetic Virtue** adds the teacher's teaching Virtues, such as Good Teacher. **With a Hermetic Flaw** of the teacher's own adds +3 for a Minor Flaw or +9 for a Major, and the student gains the Flaw too (DE p. 271).
  - **Opening the Arts** of a child with Supernatural Abilities needs the master's Intellego Vim Lab Total, in their laboratory, to reach 5 x each Ability, all added together. Each counts at least 10 for a Minor Virtue's Ability and 30 for a Major's, or 10 or 30 for a power with no Ability.
  - Reaching it, the Abilities and their Virtues are lost when the season is applied. Only at double it or more may the master choose to keep them, with **Keep Supernatural Abilities**, or convert them, with **Or convert them into** and up to two more (DE p. 271).
  - Converting gives one of the master's own Hermetic Virtues for each Ability, of its own size: Major for a Major, Minor for a Minor. It's checked when the season is played. Those not converted are lost. A similar Virtue the master lacks is the troupe's call, added by hand.
  - When the season is applied, the magus claims the child as their apprentice (DE p. 270). The Apprentice Social Status is added, and the child's Parens and House are set to the master's, so The Gauntlet can follow.
  - A successful **Search for an apprentice** adds the Gifted child to the saga as a character at the magus's covenant, seven years old and In Creation, for you to name and build (DE p. 269).
  - An inborn Ex Miscellanea tradition Virtue needs no Lab Total (DE p. 270). Leave it out of the child's Virtues until the Arts are open.
- **The free House Virtue** (DE p. 272): in Houses Bonisagus, Guernicus, Mercere, Tremere, Flambeau, Jerbiton and Tytalus, an apprentice takes on their parens's House Virtue after 10 seasons of one-to-one work with them.
  - An apprentice is a character not yet a magus whose Parens (Hermetic Background) names a magus of the saga.
  - Each season counts once, when it's applied: being taught an Art or an Arcane Ability by the parens, learning spells from them, assisting in their laboratory, or the parens opening the apprentice's Arts or teaching them a Hermetic Virtue.
  - At the tenth, when the parens has just one of the House's Virtues, it's added, with a Diary entry. When the parens has both of a House's choices (Puissant Perdo and Ignem), or for Jerbiton, the Diary says to add the one they choose among the apprentice's Virtues.
  - The Mystery Cult Houses Initiate their Virtue instead, and an Ex Miscellanea apprentice's package is the troupe's to decide.
- **Assist in a laboratory:** helping a magus with the lab work they've planned.
- **Set up a new laboratory (magi):** under Order & covenant, for a magus with no laboratory yet. **Laboratory's name** names it, or "(name)'s laboratory" if left blank. It needs Magic Theory 3 and a covenant. When the season is applied, the laboratory is made in the magus's covenant, as theirs, with the Basic Flaw until a second season finishes it (see [A new laboratory](help:advance-new-lab)). Exposure in Magic Theory.
- **Take over the laboratory (magi; Covenants):** under Order & covenant, for a laboratory with no owner, chosen in **Laboratory**, those in the magus's covenant first. A laboratory with an owner can't be chosen. It's lab work in that laboratory, rolled like refining, with Exposure in Magic Theory. When the season is applied:
  - The laboratory becomes the magus's, and any laboratory they had is left without an owner.
  - Its Refinement drops to at most their Magic Theory - 3.
  - A Perception + Magic Theory roll against 3 x the old Refinement decides whether the Predecessor's arrangements remain (Covenants, Chapter Nine: Laboratories, Taking Over a Laboratory).
- **A hedge tradition's seasons (its members only):** Open a student's Gift to a tradition, and the tradition's own work. That's Refining, brewing a potion or making a fetish, binding a familiar, inventing a gruagach spell or enchanting a tattoo, inventing a charm or making an amulet, and inventing rune scripts.
  - **Opening** needs a Gifted master Opened to the tradition and a Gifted **Student**. The master's Opening Total is set against twice the student's Supernatural Abilities and Arts, +12 if the student's Gift was Opened before. With none it always works. Up to twice that, the student is Opened but loses their old powers, noted in the Diary for you to remove. Beyond it they keep them (Hedge Magic Revised Edition p. 8).
  - An Amazon needs twice the Ease Factor to Open her apprentice, and four times to keep her powers. The Arts of any other tradition are always lost (Rival Magic p. 30). Between twice and four times, the app has her powers lost, as Rival Magic's own band reads, not the general rule's "more than twice keeps".
  - Opening a Hermetic apprentice's Arts when a non-Hermetic tradition already Opened the Gift needs 30 more on the Intellego Vim Lab Total (Rival Magic p. 6).
  - A hedge Initiation's Ease Factor rises by 3 for a Minor Virtue, 9 for a Major, when the Mystagogue doesn't have the power (Hedge Magic Revised Edition p. 13). Plan it as Undergo an Initiation with the Hedge Script chosen. Tick **Mystagogue knows the power** when they have it as an Ability rather than a Virtue. An unGifted Initiate needs an Ordeal and gains nothing from past Ordeals, and an unGifted Mystagogue must know the power (p. 14).
  - When the season is applied, the student joins the tradition with its Arts at 0 and the Virtues the Opening gives. Where the master is below 2 in one of its Arts, the student also takes the tradition's Flaw for it. For the vitkir that's their Minor Magical Deficiency. For the other traditions the Diary names the Arts and the troupe picks the Flaws.
  - A tradition's own work gives Exposure in the Art or Ability chosen in **Experience in**, and the Diary notes its Lab Total. It counts as a companion's working season.
  - The tradition's Arts can't be practised where its book says so: the gruagachan, learned magicians, elementalists and vitkir. See [A tradition's Seasons](help:tradition-seasons).
- **Undergo an Initiation:** the Initiate's season of a Mystery Initiation.
  - **Teacher / master** is the Mystagogue, or none for a self-initiation.
  - Give the Mystagogue's Lore, the Script bonus and any variation of the Script. The bonus counts every component, the Ordeal's +3, +6 or +9 included. The exception is a Verditius's first Inner Mystery's Hubris Ordeal, whose +3 the app adds itself.
<!-- tui -->
  - **Virtue initiated** opens the Virtues & Flaws picker, which asks for anything the entry names, such as an Affinity's Art. Delete clears a choice.
<!-- /tui -->
<!-- gui -->
  - **Virtue initiated** opens a list of Virtues to choose from, which asks for anything the entry names, such as an Affinity's Art. **Clear** beside it clears a choice.
<!-- /gui -->
  - **Ordeal** says what the Ordeal costs, if anything. That's a Flaw gained (chosen in the picker), one of the Initiate's Minor or Major Virtues lost, or one of their Minor Flaws raised to a related Major Flaw. A Minor Flaw or Virtue makes a Minor Ordeal, and a Major one a Major Ordeal. A raised Flaw makes a Medium one.
  - The Initiation succeeds when the Mystagogue's Presence + Lore + Script bonus reaches 15 for a Minor Virtue or 21 for a Major. It's 18 or 30 when the Mystagogue lacks the Virtue. Take off the largest reduction among the Initiate's past Ordeals. The Initiate needs the Lore at 1 unless it's their own House's.
  - A Mystery Cult of the saga's own, on Saga Content's [Mystery Cults](help:tab-content-cults), offers its degrees' Scripts here too. The Mystagogue must have its Lore at 1 or more, and the Initiate needs its Lore at 1. A second or later Initiation, counted by the cult's Virtues the Initiate holds, typically needs 3. The season warns when they have less, but lets the troupe go ahead (TMRE pp. 11, 13). See [How to initiate a character into a Mystery](help:guide-initiation).
- **Hermetic Viresculture (Legends of Hermes pp. 72-76):** in Work & trade, for a magus with the Ability.
  - **Vitalize a Stirps**: name the creature or plant and type its Magic Might, or its effect's level for Lesser Enchantment Vis. The Vitalization Total is Intelligence + Creo + Vim + Hermetic Viresculture + the aura. That's the magus's laboratory's Creo Vim Lab Total with Viresculture in place of Magic Theory.
  - Each season adds what the Total exceeds the Might by, until the points reach the Might. A Might of 0 is allowed.
  - It costs a pawn of Vim vis per ten levels or fraction, paid with its first season from the raw vis **Vis from** names. That's the magus's own, the laboratory's or the covenant's stores. The season won't plan without it, nor with more than twice Magic Theory.
  - **Other Stirpes** (`Name: Might; Name: Might`) works on several in the one season, under Multiple Laboratory Activities (DE p. 264; Legends of Hermes p. 75). Vitalizing, the Total is set against their Levels together and must finish them all that season, at least twice the sum. Each pays its own Vim. Invigorating, they share the Invigoration Total, rounded up (43 for two roosters gives each 22), and are all of the one Form.
  - Until it's Invigorated, a Stirps' young are ordinary. Its vis may be transferred out without harm, though it's then no longer a Stirps.
  - **Invigorate a Stirps**: also choose its Form. The Invigoration Total is Intelligence + Creo + the Form + Viresculture + the aura, Vim being the Form's requisite (the lower of the two counts, DE p. 312). It gives a breeding season per ten points or fraction. Each yields a fifth of the Might, rounded up, in pawns of the Form, one in ten of them a new, uninvigorated Stirps.
  - An Invigorated Stirps with breeding seasons left breeds once a year, as it does without magic, in its breeding season. That's the spring for animals and the autumn for plants, Herbam (Legends of Hermes p. 75).
  - Its pawns go into the magus's own raw vis. The new Stirpes among them are rolled and named, and a Diary entry and the season's record note it.
  - A magus tends no more Stirpes than their Viresculture score. Those past it don't breed, and the Diary says so. Each needs 12 Labor Points a year, and the yield is a pawn less for every 6 Labor Points short and for each month left unattended. The app takes its care as given, so take a pawn off by hand for care short or months unattended.
  - With the Aura Variation rules, a year's harvest takes a fifth of its pawns, rounded up, off the aura's yearly modifier.
- **The Lesser Elixir (The Mysteries Revised Edition pp. 42-43):** in Mysteries, for a magus with the Virtue, which needs Hermetic Alchemy.
  - **Reinvent the Lesser Elixir** names the special ingredient added and its Shape and Material bonus. Tick **He devised it himself** for one found by Vulgar Alchemy, and its points are doubled. No ingredient counts above Magic Theory.
  - The Elixir Points of all the magus's ingredients give the Elixir Level as an Art's experience gives its score (1, 3, 6, 10, 15...). It's at most their Magic Theory as they devise it.
  - The season prepares a dose of their own Longevity Ritual from its Lab Text, which must be at hand and readable. They need a Longevity Ritual in force. The dose takes a pawn of **The dose's vis** (Creo, Corpus or Vim) for every five years of their age, from the raw vis **Vis from** names. They use no more of it than their score in that Art, as for a dose rebrewed from the Lab Text (DE p. 261; p. 42).
  - From then on their aging rolls subtract the Elixir Level as well as the ritual's modifier, until an Aging Crisis ends the ritual. Performing their own ritual again from its Lab Text, or making a new one themselves, adds the ingredients again. A ritual someone else makes for them leaves the Elixir out.
- **Copy books by magic (Transforming Mythic Europe pp. 98-103):** in Writing & books, for a magus, while Transforming Mythic Europe is in play.
  - They cast The First Furrow Guides the Second and The Copyist's Puissant Quill page after page through the season, and must know both. They copy the **Book copied**, a summa, tractatus or Lab Text they can get at, as many **Copies** as the plan says. TME gives no rate for casting them page by page.
  - Or choose a **Copying device** held by the magus, their covenant or one of its laboratories, with The First Furrow Guides the Second instilled, as the Superb Scrinium has (pp. 101-103). They then needn't know the spells, but each text takes a use of that effect, and of the device's Binding the Mundane Codex if it binds them. So its uses a day cap the copies. 3 a day is 3 books a day, 273 in a season (p. 102). Their Finesse Total still sets the Quality.
  - Magic neither reads nor understands, so they need no language, Magic Theory or Realm Lore to copy it uncorrupted (p. 98).
  - Their Finesse Total is Perception + Finesse, with the Wound, Fatigue and Clumsy or Inconstant Magic penalties. TME says Intelligence, but the Definitive Edition's Rego craft roll is Perception (p. 307).
  - It's read on the book's table (p. 100), +3 for a book of Quality 6 or less (the Quill's Ease Factor 9), -3 for Quality 10 or more (15). 11 or more keeps the Quality, 9 loses 2, 7 loses 4 and 5 loses 6. Less makes no readable book, which stops the plan.
  - The Diary also says how long a mundane scribe would take: four pages a day, and as long again to tidy and illuminate them (p. 101).
  - A copy made by magic loses the original's resonant materials and clarification (p. 101). It's loose sheets (**Unbound**) unless they tick **Bind them with Binding the Mundane Codex**. That needs the spell, or the device's own, and a Finesse Total of 6. A book so bound has the sound binding's +1 under the extended Quality rule (p. 103).
  - A Lab Text is copied exactly, in its author's code if raw, and must be copied flawlessly (p. 103). A Finesse Total of 11 copies up to 120 levels, a month's scribing. 14 copies up to 360, a season's. 17 copies up to 1,440, a year's, by the Definitive Edition's +3 from a season's work to a year's (p. 307).
  - Past 1,440 levels no book gives a figure, and the Diary says the troupe decides. Below that, the Diary warns that a botched page may have corrupted a copy, found only when it's used.
  - The season gives Exposure, 2 xp, in the Ability chosen.
- **Shape the land (Transforming Mythic Europe pp. 54-77):** a magus casts the Rituals of one of their covenant's land projects, in order, as far as the vis goes.
  - Each takes a pawn a magnitude, of its Form first and then its Technique, at most their score in each Art (DE p. 213). The vis comes from their own, their laboratory's or the covenant's.
  - Each is rolled as a Ritual: Casting Score + Artes Liberales + Philosophiae + stress die, in the covenant's aura. The long-term Fatigue comes back with a night's sleep, so the season goes on to the next.
  - A botch or a failure spends that Ritual's vis and ends the season's casting.
  - Each Ritual cast is a point of the magus's progress toward the project. Exposure 2 xp. See [Shape the Land](help:land-shaping).
- **Activities from the supplements**, such as Study a significato, Library research or Act as Mystagogue. Library research shows the roll's total before the die: Intelligence + the Ability + the better of the covenant library's research bonus for it and its best encyclopedia's.
- **Learn to measure the fixed stars** (Ancient Magic, a magus): a season learning Ptolemy's measure of the array of fixed stars, the first stage of the magus's coordinates. It gives no experience. The app records it and won't plan it twice.
  - The second stage, calibrating the system at its origin on the Zero Longitude in the Purple Islands, is a journey for the troupe.
  - After both, a stellar observation gives the coordinates of where the magus stands, an Arcane Connection that never fades (Ancient Magic pp. 89-91; Errata p. 58). It's Intelligence + Artes Liberales against 15, with four hours of clear stars, or two with a supernaturally accurate timepiece, plus the calculations.
- **Faith:** Good Works, Follow a preacher, Pilgrimage and Visitation, petition or penance are open to magi as well as companions.
  - Good Works is for any Christian, and a cleric's may be a working season (The Church p. 27). Following a preacher is any character's free season (p. 130). Anyone may go on pilgrimage or do penance (pp. 12, 16).
  - Grogs may make a pilgrimage too, but the app plans no seasons for grogs. More's [Pilgrimage](help:pilgrimage-more) on This Season records a pilgrimage's Oppositional Elements, a grog's too, and claims its aim.
  - Care of Souls stays a priest's (p. 28).
  - **Personal devotion** is a season of prayer and meditation at a saint's shrine. Name the saint, and it earns 5 Devotion Points toward them, beginning a Devotion if the character has none. It gives only exposure experience, in Church Lore or Dominion Lore (The Church p. 14).
  - A contemplative mystic's **Spiritual path** seasons each count toward the Revelation the plan names, begun with More's Spiritual Path (The Church p. 22). Service to the poor or the Church counts +1. Devotion counts +1, with a Devotion Point toward the saint the plan's details name, or the mystic's patron, and exposure only in Dominion Lore. Preaching the Gospel counts +3, once on a path. A mission to heretics, pagans or infidels at the risk of martyrdom counts +9.
  - **Ordination** is a season's examination for the next grade of holy orders (The Church p. 33), Source Quality 2 in Church Lore or Civil and Canon Law. Choose which, the grade sought, who examines the candidate, and whether they're ordained outside their birth diocese. Choose too whether they swap their Social Status for the grade's. Ticked, they keep one status only (The Church pp. 25, 34; DE p. 63). Give the die if it's rolled at the table.
  - The plan shows the examination and what each result brings. The season ordains them, or not, on [Religion](help:tab-religion). A barred cleric, after a botched examination, can't plan one until a petition lets them.
- **Build the Great Tower** (Hermetic Projects pp. 36-38) is a master mason's season on the project they're master mason of.
  - They build new levels, at their effective Craft: Mason / 5 a season and of their Workshop Total's quality, repair a damage level, or rebuild a shoddy section as standard.
  - It's kept in the project's Works on [Projects](help:tab-cov-projects), with Exposure in Craft: Mason. A grog mason has no season plans, so their seasons are added by hand on Works.
- **Search for a lacuna:** Intelligence + the chosen Area Lore + a stress die against 9 (Houses of Hermes: Societates p. 57).
  - The first success finds the city's obvious lacunae, recorded as 'Lacunae of <city>'. The searcher then knows three small lacunae per level of that Area Lore, which the player names with the troupe.
  - Later seasons searching there are Area Lore practice, and the Area Lore's specialty may become lacunae.
  - A character raised in the area by a magus knows them already and needs no search.
  - A lacuna that gives more than a place to cast, not bought at creation nor won in a story, carries a limitation. It might be unavailable by day, have inhabitants to placate, risk exposure with overuse, or have an Infernal aura.
  - [Cast in a Lacuna](help:cast-in-lacuna) works out a spell cast from one.
- **Set points:** Useful correspondence's 1 xp, and the 1 xp in Organization Lore: Order of Hermes for each book read from a folio, are set points (Covenants p. 90; Houses of Hermes: True Lineages p. 23). No Affinity, Savantism or wound halves or multiplies them, and Master of None and Secondary Insight ignore them.
- **Study a realia collection** is for one outside the library, such as an exhibit at Tablinum. One the covenant owns is a book of the Realia kind (see [Books](help:section-lib-books)).
- **Study another artist's work**: Source Quality is half the work's Aesthetic Quality, and each work is studied once, like a tractatus (Art & Academe p. 126, with Atlas Games' errata).

**Create a work of art** (Art & Academe pp. 123-135). Its Aesthetic Quality is Dexterity + Craft (Communication + Profession for a performance, or Craft: Poetry), + Puissant, +3 for Free Expression and +3 for Inspirational.

Then the season form's choices change it:

- **Twice the time**: +1.
- **Overtime**: +1, and an Aging roll when it's done.
- **A liberal art used**: + Artes Liberales / 3.
- **A muse's sacrificed Might**: +1 per 5.
- **Life-Linked Art's wound**: +1, +3 or +6.
- **A maestro or legendary artist** in an aura of the realm their nature is aligned with: + aura / 5, rounded up. It's never the aura itself, and nothing for any other artist. Grifo's mural in his church's Divine aura 3 comes to 19, where the book's example on p. 134 leaves the +1 out.
- **Hermetic Inclination**: its Form Bonus.
- **Artist Reputation 10**: +3.
- **Half the time**: the Quality halved.

The kind of piece sets its base time: a season, two small pieces in a season, a year, a castle or church a year per Size point, or a cathedral ten years per Size point. That's multiplied by the Quality / 10, rounded up. Assistants, no more than the artist's Leadership, take 3.5 days, a week or a month off each, to no less than half. Prolific Artist takes a quarter off and allows no assistants. Each season whose piece is over three times the artist's Artist Reputation is 1 xp in it.

Experimenting adds a simple die / 2, rounded up, to the Aesthetic Quality, and at once rolls a stress die on the Artist Experimentation Results (p. 124). The two are rolled together, in the season the piece is finished. The book gives no season for a piece of several. Rolling them in the finishing one is the app's choice, since a plan keeps nothing from one season to the next.

- A disaster or a ruined piece loses the work, and a whole Reputation point or Reputation xp equal to the piece's presumed Aesthetic Quality (p. 126).
- A disparaged piece loses a Quality point and a whole Reputation point.
- A praised piece gives xp equal to its Quality.
- A praised artist gains a whole Reputation level.

A finished piece is an Arcane Connection to the artist for half the time it took, a week less for each assistant. A castle, church or cathedral is none. A maestro with Hermetic Inclination may instill a Personal, constant effect of their Form as they work. Each season adds the points of Dexterity + Craft + the Form + the aura's realm interaction over the effect's level, until they reach it. They lose a Fatigue level per 10 levels while they work.

**Edit a lecture commentary** (p. 102): a season rewriting a commentary of the teacher's own lectures adds 1 Quality and their writing Virtues, such as Good Teacher, once. Every second commentary of a teacher's lectures earns them an Academic Reputation xp (p. 103).

**Seek a teaching or clerkly post** (p. 89): a season looking, then a roll. It's Presence + the post's Ability + the highest Good Academic Reputation - the highest Bad one + a bonus + a stress die. The bonus is +1 for a Minor Social Status Virtue or Educated, Privileged Upbringing, Famous or Wealthy, or +3 for a Major Social Status Virtue.

- 12 for a secular jurist or copyist.
- 15 for a municipal, royal court or monastic teacher (a monk).
- 18 for a cathedral school teacher, or a magister's or doctor's chair (the licence).

A failure wastes the season, and a botch also costs a Medium Wound or a Bad Reputation. A post won is an Academic Reputation xp. A cathedral teacher's students are a simple die for each point of their Presence + Good Academic Reputation, and they teach five times their Teaching.

**Translating** (p. 87) now needs Artes Liberales 2, or 1 between languages of one alphabet. A translator with both languages at 6 loses one Quality point less.

- **Research a formula** (Art & Academe p. 70). A formula is a recipe for an astrological inception, an alchemical reagent or a pharmaceutical theriac. Their Abilities are Artes Liberales, Philosophiae and Medicine: choose that Ability as the subject. Five xp make it, and a season's research gives five. They go into the formula, not the Ability.
  - Type its level if you know it. It's its guideline's base raised by magnitudes as a spell's is (5 levels each, 1 below 5).
  - An inception rises for its Detail, Binary to Thorough, +1 for the past or the far future, +2 for the near future.
  - A reagent rises for its Alteration, Slight to Major, + size.
  - A theriac rises for its Potency, Weak to Mighty.
- **Produce reagents, theriacs or inceptions** (pp. 70-71). Choose a formula the character knows.
  - Their Lab Total is Intelligence + its Ability (+1 for a matching specialty) + Philosophic Bonuses, the bonuses no more than the Ability. Those are Shape and Material, an experiment's Risk Modifier and the laboratory's. It must reach the formula's level.
  - The first time, each season gathers Lab Total - level points. At points equal to the level it's done: a dose is made and its Laboratory Text written. Twice the level does it in a season.
  - With the Laboratory Text, a season makes Lab Total / 5 doses, rounded up, or fewer if Doses says so. The doses go into the character's Personal Gear.
  - A reagent's or theriac's ingredients cost 1 Labor Point per 5 levels times the doses. They come from the character's own store if they have Profession: Apothecary. Otherwise they come from the store of the best apothecary at their covenant, off whose Labor Points they're taken when the season is applied. With no apothecary there, take them off by hand. An inception costs none.
- To use an inception, cast the target's nativity once, a day's work of Intelligence + Artes Liberales + a die against 9. Then a minute per level gives the answer.

- **Make a wondrous item:** the Workshop Total adds the aura's modifier.
  - Enter the aura where the craftsman works, and its realm, in **Aura where he works**. Blank counts none. It's read on the Realm Interaction table for the realm the craftsman's Touched by (Realm) names. Faerie in a Magic aura adds half, Divine nothing (City & Guild p. 72, DE pp. 410-411).
  - The Virtue must name Magic, Faerie, Divine or Infernal (p. 71), or the season says so.
  - Choose the one assistant in the Teacher / master field. Half their Craft is added (City & Guild p. 72). Count no other help in Other.
  - A Mythic Farrier (Grogs p. 76) makes wondrous horseshoes the same way, with Intelligence or Dexterity + Craft: Farrier, in one Form. Their power works on the horse or the ground it treads. Name the farrier's realm on the Virtue, most likely Magic or Faerie, Infernal possible.
- **Exertion, a (Craft) Reputation and a laborer's working season** (City & Guild pp. 73-76), in a workshop production, excellent item or wondrous item season.
  - **Exertion** adds a simple die to the Workshop Total, rolls a stress die on the exertion table, and makes an Aging roll whatever the character's age. Under 35 the Aging roll takes a simple die for its stress die, and a 13 brings no Crisis (DE p. 392).
  - **The exertion table**: a botch is a disaster, 4-5 disappointing ramifications, 6-7 no benefit (the simple die isn't added) and 8 a story event. A 9 is invention, a simple die of Labor Points put toward Innovation, shown on This Season and spent by the next Innovation raised. A 10-11 is a simple die of experience in their (Craft) Reputation, and 12+ a simple die of experience in the Craft.
  - A **(Craft) Reputation** (p. 74) is named for the trade, so Craft: Smith's is "Smith". It starts at 0 and rises as an Ability. A season whose Workshop Total is 6 or more over the standard goods' Craft Level (6) earns 1 experience, a wondrous item's season included. The season a wondrous item is finished earns 1 more on top.
  - A season of shoddy goods straight after another takes 1 off. Below 0 the character gains a Reputation as a bad craftsman ("Shoddy Smith"), scored like any Reputation, the "bad" being in its name (DE p. 386).
  - A **laborer's working season** (p. 76) with a Profession sets their Labor Total, their primary Characteristic + Profession, against the Profession Level. The Characteristic is the one the season names, or Strength if it names none (p. 67). Their Labor Points stay Communication + Profession (p. 38).
  - The Profession Level is 6, raised by 1 where they live in an Infernal, Faerie or Magic aura, as a Craft Level is (p. 69). A Divine aura doesn't raise it. The season gives shoddy, standard (at the level) or superior (6 over it) service, never excellent. Their (Profession) Reputation follows the same rules.
- **Other:** anything else. It's written in the Diary with your notes, and no experience is worked out for it. Say in Notes what the season is spent on.

The rules are those of Ars Magica Definitive Edition, Chapter 10: Long-Term Events (Exposure, Practice, Adventure, Books, Teaching, Training, Vis and Distractions). Each activity's rule is cited under the plan in the character's This Season.

### Where the experience goes
<!-- help: plan-season-experience -->

**Experience in** chooses the Ability, Art or spell Mastery the season's experience goes into. For Teach, it's Teaching or the language used. Some activities split it:

- **Work / Exposure** can give 1 xp in each of two subjects instead of 2 in one.
- **Adventure** can split the storyguide's Source Quality (5 to 10) among up to three subjects, at most 5 to each. Give each one's share in **Source Quality to (n)**.

**Source Quality** is asked for Practice, Adventure and some supplement activities. For Practice, leave it blank for 4, or 5 for a spell's Mastery. **Book** offers the covenant's library and the character's own books. **Teacher / master** lists the other characters. Saving Be taught or Be trained plans their season too (see [Paired plans](help:plan-season-pairs)).

**The Art is present** (Read a book, Study from vis) is for a character with Study Bonus or Study Requirement. The Art is studied beside its substance, such as a fire for Ignem or a pond for Aquam.

**Secondary Insight** (Read a book, Be taught, Study from vis) is for a character with the Virtue. Choose the Book or **Experience in** first, then open it to tick the Arts that gain 1 xp, each shown with its score. That's up to 4 Forms when the season studies a Technique, or up to 2 Techniques when it studies a Form. With none ticked, or after Clear, the lowest-scored are chosen. See [Virtues and Flaws the app applies](help:guide-advancement-virtues).

**Stress die (blank: rolled)**: for activities that roll, leave it blank and the app rolls the die when the season is applied. Or type a roll made at the table.

**Months lost (0-3)**: each full month lost to distractions cuts the total by a third.

### The line above Save
<!-- help: plan-season-preview -->

As you fill the form in, the line above Save shows what the season will give. For each subject it shows the Advancement Total, the xp gained and how the score and xp change, for example "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)". For book work it shows the progress or the book made.

If the plan breaks a rule, such as a book the character can't read or a teacher whose score is too low, the line shows the problem. Save refuses the plan until it's fixed. Experience a Virtue shares with another subject says so, for example "Auram: +1 xp from Secondary Insight".

For a companion, the line also reminds you when the plan leaves too few seasons that year for their working seasons. That's two, one with Wealthy, or three if Poor. It's a reminder, not a block.

**See also:** [Advance Season](help:advance-season), [Grog's Yearly Update](help:grog-year), [Laboratory Planning tab](help:tab-lab-planning), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Grog's Yearly Update
<!-- help: grog-year -->

Grogs aren't planned season by season. Instead each grog gets a yearly update, applied when Winter is advanced, following Grogs, Chapter 5: Updating Grogs. This dialog sets up that update.

<!-- tui -->
Open it from the grog's **Planning** tab (`e`), or from the Grogs list on a covenant's **Seasons** tab.
<!-- /tui -->
<!-- gui -->
Open it with **Yearly Update** in the grog's **Planning** chapter, or by clicking the grog in the Grogs list of a covenant's **Seasons** chapter and choosing **Plan**.
<!-- /gui -->

**You type:**

- **Vocational training**: the Ability trained, usually Single Weapon from the drill sergeant, and **Vocational xp**. That's 7, or the teacher's Source Quality if you know it.
- **Practice (4 xp)**: one Ability practised.
- **Exposure (2 xp)** and a second **Exposure (2 xp)**.
- **Story awards this year**: how many stories the grog took part in. [Story Experience](help:grog-story-xp) counts each one for you. Change the number here only to correct it.

**The app works out:** the xp each Ability gains, shown on the grog's This Season. Each story award, and each season of [copying](help:grog-copying), takes one season of the year, in Grogs p. 67's order: the first exposure, the vocational training, the practice, then the second exposure.

In Winter the xp is added, and a "Yearly update" entry is written in the grog's Diary and in the season's record. The story awards go back to 0 for the next year.

A grog with no Ability chosen here gets the saga's [default](help:advance-unplanned) instead. Each story award still takes a season off it, in the same order: 2 xp, then 7, 4 and 2.

**See also:** [Story Experience](help:grog-story-xp), [Advance Season](help:advance-season), [Plan Season](help:plan-season), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Story Experience
<!-- help: grog-story-xp -->

A grog who takes part in a story gains its experience at once, and the yearly update in Winter loses a season for each award (Grogs p. 67). This form gives the experience and counts the award.

<!-- tui -->
Open it from a grog's **Planning** tab: More (`m`), then **Story Experience** (`s`).
<!-- /tui -->
<!-- gui -->
Open it with **Story Experience** in a grog's **Planning** chapter.
<!-- /gui -->

**You type:** the story's name, and up to three Abilities the story used, with the experience each gains.

**The app checks:** a story gives 5 to 10 experience in all, at most 5 to one Ability (an Adventure's award, DE p. 376).

**The app does:** it adds the experience to the Abilities now, adding any Ability the grog lacks. It writes a "Story experience" entry in the Diary, and adds one to the year's **Story awards**.

**See also:** [Grog's Yearly Update](help:grog-year), [Diary tab](help:tab-diary)

# Plan Copying
<!-- help: grog-copying -->

A covenant's scribe is often a grog. Grogs aren't planned season by season, but a season of copying is (DE p. 380). **Plan Copying** plans one for the grog on the same form as anyone's season, offering only Copy a book and Copy Lab Texts.

<!-- tui -->
Open it from a grog's **Planning** tab: More (`m`), then **Plan Copying** (`c`). Once a season is planned, **Clear Copying** (`x`) drops it.
<!-- /tui -->
<!-- gui -->
Open it with **Plan Copying** in a grog's **Planning** chapter. Once a season is planned, **Clear Copying** drops it.
<!-- /gui -->

The season is played when it's advanced, as anyone's is, and the grog's This Season shows it below the yearly update. Each season spent copying takes a season of the [yearly update](help:grog-year) in Winter, as a story award does.

**See also:** [Grog's Yearly Update](help:grog-year), [Plan Season](help:plan-season)

# Advance Season
<!-- help: advance-season -->

<!-- tui -->
`t` moves the saga on by one season and applies every plan made for the season that's ending. It works from anywhere in the workspace.
<!-- /tui -->
<!-- gui -->
**Advance Season** moves the saga on by one season and applies every plan made for the season that's ending. It's the card with the present season's medallion at the foot of the chapters on the left: click anywhere on it. It's on every page of a saga that has chapters, so the last thing you do in a season can be the last thing before it ends. A Creation Worksheet, a Fight and a Siege have none, as a record is finished or left first.

Once you say Advance, a dial of the four seasons turns in the middle of the window to bring the new season to the top. It then shows its medallion with its name and year, and fades. Click or press a key to skip it. With **Reduce motion** on, the new season simply follows.
<!-- /gui -->

**You type:** only your answers to [its questions](help:advance-season-questions).

**The app works out:** everything else, as below. Each season's result ends with [the dice it rolled](help:dice-line): the Lab Total's die, the experimentation chart's stress die with its doublings and botch dice, and any further roll on the chart.

### The confirmation
<!-- help: advance-season-confirm -->

The Advance Time dialog asks whether to advance from this season to the next, and sums up the plans:

- how many planned seasons will be applied
- who has nothing planned, since they gain nothing this season
- any plan that can't be carried out, and why.

When the year is about to end, it also says that each covenant's surplus will be added to its Wealth, and that Emergency Savings start again at 0.

<!-- tui -->
If you advance by mistake, More's **Set Date** on the saga puts the date back, but it doesn't undo what the season did. **Undo Last Season**, beside it, does (see [Undoing a mistake](help:guide-seasons-undo)).
<!-- /tui -->
<!-- gui -->
If you advance by mistake, **Set Date** in the saga page's Seasons chapter puts the date back, but it doesn't undo what the season did. **Undo Last Season**, beside it, does (see [Undoing a mistake](help:guide-seasons-undo)).
<!-- /gui -->

### Questions along the way
<!-- help: advance-season-questions -->

After you choose Advance, the app may ask:

- For work that runs until it's done, whether anything interrupted it this season (see [Interruptions](help:advance-interrupted)).
- For the player characters with nothing planned, and any plan that can't be carried out, what to do with the season (see [Unplanned seasons](help:advance-unplanned)).
- In Winter, if a covenant is in deficit, whether to advance anyway. **Advance anyway** rolls the year over. **No**, or Escape, leaves the date alone so the books can be balanced first.
- Which contested vis or income sources whose security has lapsed were secured this season, one tick each. A ticked one is secure for five years. One left unticked gives nothing until it is.
- For each experiment whose Extraordinary Results need the storyguide's word, what they are (see [Experiment Results](help:advance-experiment-results)). That may be which of two rolls stands, what each side or modified effect is, what a Discovery teaches, what a special result becomes, or whether to take a Discovery the risk can reach.
- For a magus finishing a recreation of a flawed spell, whether to retire the flawed one (see [Retire Flawed Spells](help:advance-retire-flawed)).
- For a magus setting up a new laboratory, whether they'd like to finish it next season (see [A new laboratory](help:advance-new-lab)).
- For each player covenant on the move, and each of its ships apart from the fleet: move on to the route's next leg, stay, or go somewhere else (see [Whereabouts](help:section-cov-whereabouts)). The answer is logged as a stop in the new season, and a move costs the covenant its Aegis.

Cancelling any of these leaves the date and the saga as they were.

### Run Downtime
<!-- help: downtime-run -->

Runs several seasons at once, for a pulsed saga that plays a burst of stories and then lets years of downtime pass (DE p. 528).
<!-- tui -->
Open it from More on the saga, **Run Downtime**.
<!-- /tui -->
<!-- gui -->
Open it with **Run Downtime** in the saga page's Seasons chapter.
<!-- /gui -->
It's only on the host's own copy. A storyguide at a Remote seat advances season by season.

**You type:** where the run stops. **A season I choose** stops when the saga reaches that season, before playing it. **The next Tribunal** stops at the meeting of a troupe covenant's Tribunal, so you can hold it. A run of more than ten years asks first.

**The app works out:** one backup first, then each season as Advance Season plays it, with the plans repeating. Each season is kept (saved) before the next.

- Any question Advance Season would ask (see [Questions along the way](help:advance-season-questions)) stops the run at its season for your answer. The run goes on after it.
- Each Winter's World Turns review is the exception. It's rolled in its year and kept, and every one is asked at the end, oldest first, each dated its own Winter.
- A player character whose plans have run out stops the run with their Plan Season form. The run goes on once it's saved.
- Anyone else with nothing planned takes the saga's default, and the end says who.
- The end also says, for each player character, what changed over the whole run.
- Cancelling a question stops the run there. The seasons already played stay played.

### A new laboratory
<!-- help: advance-new-lab -->

When a magus has planned **Set up a new laboratory**, Advance Season asks, for each one, "Would you like (name) to finish it next season?". The laboratory works after this first season, but with the Basic Flaw (-3 General Quality) until a second season's work in it removes the Flaw (Ars Magica Definitive Edition, Chapter 8: Laboratory, Setting Up a Laboratory).

- Leave it ticked and **Continue**, and the magus's next season is planned as **Set up the laboratory**, lab work in the new laboratory, unless something is already planned for it. It shows on the laboratory's **Planning**, where it can be changed or cleared like any lab work.
- Untick it to decline. The laboratory keeps the Basic Flaw until you plan **Set up the laboratory** on its **Planning** yourself.

### Experiment Results
<!-- help: advance-experiment-results -->

When a magus experimented this season (Ars Magica Definitive Edition, Chapter 8: Laboratory, Experimentation), the Extraordinary Results chart has already been rolled when the season is advanced. Lab work in an unsafe or a Warping laboratory comes here too, experiment or not, when the laboratory warped it (see [Safety and Warping](help:guide-lab-safety-warping)).

Before anything is applied, Advance Season asks the storyguide about each experiment whose results need a decision. There's one form per experiment, titled **Experiment Results** with the magus's name. Nothing on it is applied until the season is played, and cancelling leaves the saga as it was.

- **Which roll stands**: a magus with Exciting Experimentation or Creative Block rolls the chart twice. Both rolls are shown, and the storyguide picks the one that stands, the more amusing, says the Virtue. Only the chosen roll's questions are shown. While seeking an Arcane Discovery, both rolls already have the risk modifier's move applied.
- **Side effect** and **Modified effect** show what the sub-table gave. **Which stands** appears when two dice gave different results. **What it is** is the storyguide's description, which may be left blank and filled in later on the creation's experimental effects.
- A modified effect can also change the creation's **Range**, **Duration** or **Target**, or its **Potency** in steps. The level never changes and no requisite is added. A fatal flaw is marked on the creation.
- **Discovery**: the Ability (15 xp) or Art the experience goes to.
- **A special result or story event** (a 9):
  - **A story event** is written in the laboratory's and the covenant's Diaries as an open story.
  - **The creation changed** is described and kept with the creation's experimental effects.
  - **Extra vis** asks for the effect's magnitude plus the risk modifier in pawns of the project's Technique or Form vis. Without them, or with more than the magus can handle in a season, the season is a Complete Failure.
  - **A spell as well** opens a spell form next, for a spell of the same Technique and Form up to half the Lab Total, which the magus learns with a Lab Text.
- **The Disaster** with 5 or more zeroes: the laboratory destroyed (Deformed and Unstable, and the magus Incapacitated), or a story threatening the whole covenant.
- **Take the Discovery**: when seeking an Arcane Discovery, the risk modifier could move the roll onto 10. A roll card then shows the die and the risk, where the roll landed on the chart, and the chance a stabilization would then succeed, since it repeats the same move. The roll's own result stands either way.

Every chart roll of 0 rolls botch dice: 1, plus the risk modifier, plus the laboratory's aura (the one its Lab Total uses), less Cautious Sorcerer's, less the laboratory's Safety. A negative Safety adds dice. On a 12 or more, each further roll is a stress die plus the risk modifier, with the same botch dice, stabilizing too. After ten 12s in a row the storyguide rolls the rest.

**The app's assumption about Potency.** The rules say a modified effect can be more or less potent but give no size. The app takes one step as 5 points of the Lab Total behind the creation. For a Longevity Ritual that's 1 point of its modifier, so a ritual reduced by a step protects one point less on every aging roll. Where nothing is worked out from the Lab Total, the change is only described and recorded.

### Unplanned seasons
<!-- help: advance-unplanned -->

A season left with nothing planned takes the saga's default for that kind of character, set in the saga's settings:

- **Magi** and **Companions with nothing planned**: **Work / Exposure**, the default, gives 2 xp of Exposure in their profession, an Ability whose name starts with Profession. Failing that it's a magus's Magic Theory, if they have a score in it, else their highest Ability that isn't a language. The Diary entry is marked "(default)". **Nothing** leaves the season empty.
- **Grogs with nothing planned**: a grog with no [yearly update](help:grog-year) gains 2 xp of Exposure a season in their highest Ability, 8 when Winter is advanced, marked "Yearly update (default)". **Nothing** gives them nothing.

Advance Season's **Unplanned Seasons** step names each player character (one with a Player) who has nothing planned. Each gets a choice:

- **Default**: what the saga's default gives them.
- **Nothing this season**.
- **Plan it now** opens [Plan Season](help:plan-season) for them, then carries on with the season.

A plan that can't be carried out is listed too, with the reason. **Leave it** skips it, as before, and **Plan it again now** opens it to change. Cancelling keeps only the plans already saved.

Non-player characters with nothing planned aren't named: they take the default.
<!-- tui -->
Tick **Be notified when and which non-player characters do not have seasonal activity** in the saga's settings to have them named and asked about too.
<!-- /tui -->
<!-- gui -->
Tick **Name Idle Non-Player Characters** in the saga's settings to have them named and asked about too.
<!-- /gui -->

### Interruptions
<!-- help: advance-interrupted -->

When a season has work planned [until it's done](help:plan-season-repeat), Advance Season first asks whether anything interrupted it. Each piece of work is listed with its character, the work, and the last season planned for it:

- **Days away from the laboratory** (lab work): up to 10 cost nothing, 11 to 20 lower the Lab Total, and more rule out lab work this season.
- **Months lost** (0 to 3), for reading and other study, and a season writing, copying or translating a summa, as on [the plan](help:plan-season-experience).
- **The whole season lost**: nothing is done on the work this season, and no Diary entry is written for it.

If nothing interrupted it, leave them as they are and **Continue**. Once the season is played, the seasons the work still needs are worked out again, as [For several seasons](help:plan-season-repeat) says. The message after the season says what changed.

### How the season is applied
<!-- help: advance-season-apply -->

Every plan's outcome is worked out first, from the saga as it stood before the season, and only then are they all applied. So one character's results can't change another's, or their own, in the same season. Raising Magic Theory this season doesn't raise this season's Lab Total. Dice left blank on a plan are rolled now.

Before anything is applied, the saga is backed up to `sagas/backups` in your [save folder](help:saga-picker), where the last five are kept. So the season can be undone with **Undo Last Season** (see [Undoing a mistake](help:guide-seasons-undo)).

Then, for each plan:

- the experience is added, and lab work, book work and the like are carried out
- an entry is written in the character's Diary, and in the laboratory's or covenant's where the work touches them
- a plan that can't be carried out is skipped, and the record says why.

The season's plans are then removed.

### Winter: the end of the year
<!-- help: advance-season-winter -->

When Winter is advanced, the year ends:

- Each grog's [yearly update](help:grog-year) is applied.
- A character running a business pays its yearly upkeep in Labor Points (City & Guild), with Perfect Eye for Commodity's gain and Bigamist's second household.
- Yearly Warping Points are added for a Longevity Ritual, for living in a strong aura of another realm, and for Raised from the Dead, Immortality of the Forest (which makes no aging roll) and Susceptibility to Warping.
- Every character aged 35 or more makes an aging roll, or 50 or more with Strong Faerie Blood or Dhampir, as does anyone with a Longevity Ritual. It's written in their Diary with [the dice it rolled](help:dice-line) (Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Aging). A magus the Great Elixir made a being of Magic makes none and gains no Warping (The Mysteries Revised Edition p. 44).
- Dwindling Resources lose a tenth of the value they had when they began dwindling, so they're gone after ten years. A contested resource still not secured gives nothing that year.
- Each covenant's surplus is added to its Wealth.
- Transitions of maturation (Apprentices pp. 14-15). Each character turning 8, 15 or 21 next year gets a line and a Diary entry. In the first season of that year their Virtues and Flaws may be exchanged, Minor for Minor and Major for Major. Child ones must be exchanged by 21, and Inherited ones have manifested.

Every season, each covenant's vis sources for that season are harvested into its vis stores and written in its Diary. Every wounded character makes the season's [Recovery rolls](help:recovery-roll), written in their Diary, with bruises first leaving their residual wounds. Everyone's Fatigue is rested away.

### Afterwards
<!-- help: advance-season-after -->

<!-- tui -->
The date moves on, and a message names the new date and whose seasons were applied. When anything happened, the [Season Summary](help:season-summary) shows the results. With Keep season records on, the season is also kept under [Seasons](help:seasons) in the tree.
<!-- /tui -->
<!-- gui -->
The date moves on. When anything happened, the [Seasons](help:seasons) page opens on **Just played**, the [Season Summary](help:season-summary), which names the new date and whose seasons were applied. Otherwise a message says so. With Keep season records on, the season stays on the Seasons page, opened from **The Seasons Played** in the saga page's Seasons chapter.
<!-- /gui -->

**See also:** [Plan Season](help:plan-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [The saga](help:saga), [How to plan and run a season](help:guide-seasons)

# Hold Tribunal
<!-- help: hold-tribunal -->

A Tribunal's meeting, held a step at a time from the Tribunal's **Meeting**. Each step is a short form: you make the decisions and enter the rolls, and the app works out the rest.

Every form says which step it is ("Step 3 of 12"), what comes next, **what the app works out for you** and **what each thing you enter changes**. The details panel says the same when you choose a step.

Saving a step holds it and opens the next, so a meeting can run from roll call to Closing in one go. Cancel stops, and the meeting waits at the step in hand. It's saved after every step, so you can leave it, and holding it again resumes there. For a meeting walked through from start to finish, see [How to hold a Tribunal](help:guide-tribunal).

The rules are Ars Magica Definitive Edition's (Chapter 2, Tribunals). A quorum is twelve magi in person from four covenants and a Quaesitor. The Praeco and the Presiding Quaesitor don't vote, and the Praeco breaks a tie.

How a case is heard follows Houses of Hermes: True Lineages (House Guernicus, Tribunal Procedures). The debate follows Houses of Hermes: Societates (House Tytalus, The Fine Arts of Debate).

The steps run in a fixed order:

- **The roll call and proxies.**
  - Tick each covenant's magi present one by one, or all at once with **all present**. Give how many of a sketch covenant's unnamed magi came.
  - Give the proxies each carries, and whether the Presiding Quaesitor allows them or sets them aside.
  - Under Hibernia's customs, also say whether each covenant shows its cathach. One that doesn't has no votes.
  - The votes in the hall are worked out (the Praeco and the Presiding Quaesitor are present but don't vote), the quorum is checked, and the proxies are kept on the roster.
  - Only the magi ticked present can speak at a hearing. A proxy carries a vote, never a voice.
  - Saving it opens the meeting, and cancelling holds none.
- **Opening and the oaths**: where it's held, how many days it lasts, and the day each case and motion is heard. A meeting lasts as many days as its Tribunal's customs give: Hibernia's seven (The Contested Isle p. 32), three elsewhere. **Days** on the Opening changes it.
- **The new magi and the sigils by proxy**, under the Rhine's customs, the first business after the Opening (Guardians of the Forests pp. 24, 26-27).
  - Every magus of its covenants who passed their Gauntlet since the last meeting is introduced. Tick each, or name others not in the saga.
  - Then the rite confers a retired magus's sigil on each master and archmage made since, by the Mark of Approval or the Archmage's Challenge. Name whose sigil it is, typically their master's, if retired.
  - Each sigil adds a proxy to the magus's covenant's votes, at this meeting and the next. Holding the step again confers afresh, never twice.
- **The Hermetic Assembly**, on the first day under the Theban customs, in two steps. The Theban Law Council and People's Court are the meeting's motions and cases, below.
  - **The Assembly's decrees** name the principal phyle governing the meeting. It's the next in turn (Ionian, Aegean, Kretan, Propontian), unless you choose another.
  - A decree of citizenship for each metoikos makes them a polites.
  - A decree of contrition for each polites with a shard takes one away. It asks the reparation: what the magus offers, and its vis in pawns of an Art. When the decree is accepted, those pawns leave the magus's own vis for the Tribunal's treasury, as many as they have (The Sundered Eagle p. 33). Holding the step again gives them back first, and the minutes name each reparation.
  - A decree of defamation against a polites, if upheld, gives the accused a shard. If rejected, it gives the one who brought it a shard.
  - **The ostrakismos**: the logothete reads every polites holding a shard, and the one on the most sherds, or no one, is ostracised. They become a metoikos, lose their tokens and shards, and may not return for seven years.
- **The Apprentice Presentation**, under the Theban customs, between the Assembly's decrees and the ostrakismos. These are the Gifted children the Treasury Council found, interviewed for two days before the meeting.
  - Enter each child the troupe's magi interviewed, up to five, with their age. Give who delivered them to the Council, since a polites who did earns a token (The Sundered Eagle p. 28). Give the tokens each magus gave them, up to three magi.
  - Only a polites with no shard may give tokens, or any Bonisagus even with one, since the Code trumps local custom. No magus may give more tokens than they hold (p. 32).
  - A child given tokens by one magus is that magus's apprentice. One given tokens by several chooses, usually the one who gave the most. The app picks that one, the first entered on a tie, unless you choose another of them. A child given none may be claimed by any magus, even one with a shard (pp. 33-34).
  - Any Bonisagus may claim any child outright by the rights the Oath gives their House, whether or not they gave tokens, and whatever their shards. Name them under **Claimed by**, shown only when the Tribunal has a Bonisagus. The child's choice doesn't override them. By tradition the Bonisagus still gives a token or two. Enter them as their bid, and the child keeps them (p. 32).
  - The master's tokens leave the master and stay with the child, to spend once they're a magus. The others' go back to them.
  - Each child given becomes a Sketch character at their master's covenant, with the master as parens and the tokens they keep in their summary. Once given, holding the step again changes only its note.
- **Each case and motion**, on its day, is a debate between the prosecutor and the defender. For a motion, it's one who speaks for it and one against.
  - Each is chosen from a drop-down of the magi present, shown with their covenant. The prosecution may instead be the Presiding Quaesitor, who prosecutes a high crime no one else will. The defence may be a Guernicus advocate, who defends an accused who didn't come. A motion's opponent may be the Tribunal itself, since a proposer debates the whole hall.
  - The case's own speakers are chosen to start with, or the magus it names, or a magus of the covenant it names. An accused who is absent is given the advocate.
  - A charge or appeal can instead be settled at the private hearing, when both sides accept the Presiding Quaesitor's ruling. Tick **Settled in private**. It then has no debate and no vote, and its ruling starts as "Settled at the private hearing".
  - Enter each side's debate Fatigue levels lost, or leave both blank and the debate is rolled round by round. That follows Houses of Hermes: Societates (The Fine Arts of Debate).
  - Each round, Communication + Folk Ken, Intrigue or Artes Liberales is rolled against Intelligence + Charm, Guile or Leadership. Artes Liberales counts as logic and rhetoric, for Academic Concentration and Aristotelian Training. Each debater uses what they're best at, by lot each round among Abilities of the same score, the app's stand-in for their choice of tactic (Houses of Hermes: Societates pp. 90-91).
  - A hit costs debate Fatigue only when Presence and the margin beat the defender's Resistance, their best positive Reputation + Confidence (+3 Strong Willed). So a weak speaker's hits on a well-known magus can cost nothing (p. 90).
  - A speaker with none of those scores written down, such as an advocate, the Tribunal or a sketch magus, debates at the skill you give. The rules give no figures for them, so these are the app's. **Middling** is an ordinary magus, Characteristics 0 and those Abilities 2. **Able** is Characteristics +1 and Abilities 4. **Formidable** is Characteristics +2, Abilities 6 and a Reputation of 3.
  - The case's Evidence is the prosecution's testimony, and the Defence testimony the defence's, each used once. A peer's is +3, an apprentice's or familiar's +2, any other +1, and +3 more if a Quaesitor examined it.
  - The side that lost fewer levels wins, and the difference is its Argument Strength. A motion that adds to the Code takes 1 off it, and one that alters it 3.
  - **Heard by** (a charge or appeal) is Debate, as above, or certamen. **Certamen in its place** binds the case however persuasive the loser. Say who won, and the case goes to its ruling with no vote.
  - With **Certamen on one point** of it, the Fatigue levels each side actually lost stand in for the debate's levels lost, and its winner doesn't win the vote by it (Houses of Hermes: Societates p. 92).
  - Certamen in its place is offered only for a personal charge one magus brings against another, when the charge names no violation of the Code. It can't over-rule a Tribunal, so an appeal against a ruling is debated. It can't require a violation of the Code or a magus to overlook one, so a charge naming a high or low crime is debated too (DE p. 230). The Heard by hint says why when it isn't offered.
  - **Argues**, for each side, is In good faith or Knowing it false. Knowing it false takes the speaker's Truthful Personality Trait off each of their Defence Totals, and a deceitful Trait gives nothing. A flawed, despised or preposterous thesis starts the debate 1, 2 or 3 levels down (The Power of Truth, p. 91).
  - A motion opposed by "The Tribunal" is debated by the whole hall. Each round a different magus present, the proposer aside, questions the proposer, at the skill you give the Tribunal if that magus has no scores written down. The levels lost are all the Tribunal's (p. 92).
  - **Changes** (a motion) is the Peripheral Code, or the Peripheral Code and recommended to the next Grand Tribunal, since a regional Tribunal can change only its own Code. Or it's heard at the Grand Tribunal, which costs the proposal 1 more Argument Strength on top of an Addition's 1 or an Alteration's 3 (p. 93).
- **The vote** on each case.
  - Each covenant's leaning, which you can change, shows with why it leans that way under it. It brings the case, the case is against it, or it has an attitude toward a troupe covenant that's a party.
  - The debate wins votes. An Edge wins 10% of the undecided votes, up to a Landslide's 60%. A Triumphant Victory wins 10% to 30% of the other side's too.
  - The covenants are called one by one and the tally kept. What's left undecided abstains.
  - On a tie the Praeco casts the deciding vote: choose for or against. On a call for a Wizard's March a tie defeats it.
- **The Sacred Council**, on the first day under Hibernia's customs. Tick each faction's ambassador confirmed for this meeting, from the Tribunal's **Ambassadors**, and write the disputes heard. Each confirmed ambassador votes as a magus does. They're called after the covenants, undecided unless named as a party, and you can change their leaning like a covenant's.
- **The Praeco's succession**, on the first day under Normandy's customs. With no Praeco, the eldest magus of the Tribunal, by Year Born, is offered. Set them aside by choosing the next eldest. The one named becomes Praeco, and the minutes say who was passed over.
- **The Library of the Tribunal**, under Normandy's customs (The Lion and the Lily pp. 22-23). The books the Tribunal owns in common are kept at Confluensis, read only by those who win them at the Tourney. Each goes out on a seven-year lease, back before the next meeting. At the Library step:
  - Tick each lease that's up as returned. One left unticked is noted as still held.
  - Record a book a magus of the Tribunal wrote and gave to the Library, which goes to Confluensis. Record too the giver's prize, a Library book worth no more Build Points than the gift. There's one lease for each book given, as many as there are to give.
  - Record each book won at the Tourney, with the covenant that won it, as many as the Library has free.
  - A team buys its books with the prize pawns its rank won at this year's Tourney. Record its points on the Tribunal's **Tourney** first. A book costs a pawn per 5 Build Points, a fraction counting as a pawn, and the step refuses a team's books costing more than its pawns.
  - At the Tourney each team takes one tropaeum or lump of vis and one book or item a round, in rank order, then picks again while pawns remain (The Lion and the Lily p. 33). The pawns it spends on tropaea and vis aren't counted here.
  - A leased book stays the Tribunal's, kept at Confluensis, and the lessee has seven years' exclusive access. Two prizes can't name one book. When two contributors want the same book, certamen settles it.
- **Residency**, under Provence's customs (Faith & Flame p. 22).
  - A magus is a resident of the Provençal Tribunal who attended one of its last three meetings, or was granted residency by vote at their first, or registered on arriving. They register with the Redcaps and the Praeco, or their nearest neighbour.
  - One Gauntleted in the Tribunal is a resident until three meetings pass without them.
  - The meeting's roll of residents records the magi present, lets you grant residency to a newcomer present, and records a resident's departure, registered or not. Voting at another Tribunal without registering a departure breaks the Peripheral Code.
  - Until three meetings are recorded, every magus of the Tribunal is presumed a resident. A magus's sheet shows their residency and why.
- **The execution of sentences**, on the last day under the Theban customs, before the outgoing magistrates are paid (The Sundered Eagle pp. 28, 35).
  - Each charge the People's Court heard takes its verdict from how its vote went. Carried is convicted, failed is exonerated, and settled or not voted is no verdict.
  - A conviction gives the guilty three shards for a High Crime or one for a Low Crime, beside its punishment. The magus who brought the case gets a token, or three if the guilty was Marched. A case the Court defeated gives its bringer a shard.
  - Choose the accused and the accuser from the Tribunal's magi. The step guesses them from the case's names.
  - A metoikos is given no tokens or shards. No March is held on Delos.
- **The conduct of archai**, under the Theban customs, after the sentences (The Sundered Eagle p. 35).
  - Any polites may ask that the conduct of an arche, or of the polemarch, be examined, naming the fault and proposing a fine of one to seven shards. The archon counts as an arche, since the archon is elected from the archai. A fault may be a case poorly defended or prosecuted, a bribe, or indolence.
  - There may be up to three complaints. For each, give the magistrate, who brought it, the fault, the fine and how the votes went.
  - A complaint upheld with its fine gives the magistrate the shards. One rejected, or whose fine is voted down, gives none.
  - Failing to win or stop a conviction is no fault unless the neglect was willful.
  - The logothete isn't offered, since the book names only an arche or the polemarch. Holding the step again undoes the first holding first.
- **The common vis sources**, under the Theban customs, before the outgoing magistrates' tokens (The Sundered Eagle pp. 28-29). These are the vis sources the Peripheral Code holds in common, gathered for the Tribunal by magi the Treasury Council names.
  - For each source, give its Art, its gatherer and the pawns brought into the coffers. The pawns go into the treasury as vis.
  - Each gatherer earns a token for the period, one for each source they gather. The book's "one per Tribunal period" could also mean one per magus however many they gather, so this is the app's reading. If your troupe reads it the other way, give back the extra by editing the gatherer's tokens.
  - A gatherer who forgot to harvest (tick **Neglected**) is given a shard and brings in nothing.
  - The sources and their gatherers are kept, so the next meeting's form starts with them.
  - The whole Tribunal gathers some 50 pawns a year, Creo and Vim the most, about half of it spent on the yearly Longevity Ritual (pp. 29-30).
- **The Council of Archai**, on the last day under the Theban customs, in three steps.
  - **The outgoing magistrates' tokens**: each outgoing magistrate is paid in tokens, 2 for an arche, 3 for the archon and 5 for the polemarch. Untick one to pay nothing.
  - **The sortition**: four archai are drawn by lot from each phyle, the principal phyle first, from its politai who aren't archai now. Redcaps aren't drawn. The draw is kept, so holding the step again draws no one new. One magus drawn may be set aside for the next drawn from the same phyle.
  - A phyle with fewer than four politai leaves its other seats for the logothete to fill with Redcaps.
  - A drawn magus set aside because they refused to stand is given a shard (choose "Refused to stand"). One set aside for any other cause isn't (The Sundered Eagle p. 32).
  - The new archai are then placed on the boards. Those who've been archai before go first, each on a board they haven't sat on, by lot where they have a choice. Then the rest go by lot until each of the Judicial, Legislative and Conciliatory Boards has three.
  - The others form the Treasury Council. One is drawn tamias, four gather vis and Gifted children (one from each phyle where they can), and the rest are tutors.
  - A board no arche can fill is left to the logothete's Redcaps, and the minutes say how many seats.
  - Each arche's Duties say where they sit, and the Tamias office takes the one drawn. The Tribunal remembers who has sat on which board (pp. 27-28, 35). The new archai serve until the next meeting.
  - **Archon and polemarch**: the new archai elect the archon from among themselves, the eldest offered first, and the polemarch from every polites. The archon becomes the Tribunal's Praeco.
- **Rulings and fines**: the ruling on each case, starting from how its vote went.
  - The ruling is **written out**, or made from a **ruling template** (see below).
  - Give any fine, in pawns of an Art or, with no Art, pounds of silver, and who pays it.
  - Say whether the ruling goes into the Peripheral Code. A motion's does unless you say otherwise.
  - **Term** is the years after which the matter comes back.
  - For a case between a troupe covenant and another, say how the other's attitude toward the troupe moves. A party that lost takes it ill, -1.
  - A case that may March the accused asks **Marched**. That's a conviction for a high crime when the prosecution called for a March and a simple majority carried it (a tie defeats it), or a Quaesitor's March the Tribunal ratified (Houses of Hermes: True Lineages pp. 58, 63).
  - A charge also asks how many times the convicted magus **refused** a lesser penalty. At three they're Marched whatever the crime (p. 59).
  - Closing the meeting writes the March on the outcast's Hermetic Background, with the year and the Tribunal that renounced them, when the case's Against names a character. They're safe until the Tribunal closes, then outside the Code (DE p. 18; p. 60).
  - A declaration of Wizard's War isn't heard unless its service is disputed. The hunt itself isn't worked out.
- **Treasury and vis**: the treasury as it stands and the loans that fall due this year.
- **The next host, by lot**, under Normandy's customs. A covenant of the Tribunal is drawn, and may be drawn again once, the second draw standing. It becomes the Tribunal's meeting place, and the minutes say where it meets next.
- **The tithe of Gifted children**, under Hibernia's customs. The Coill Trí bring a Gifted child from each of their seven túatha, as the Tribunal records them, else unnamed.
  - Each túath offers three, made once and kept. The first is brought unless you choose another, which is a reroll.
  - Each child has a name, an age from 5 to 12, a Gift (ordinary, Gentle or Blatant), a sign or two of what they may become, and where they come from.
  - Now and then a child has no true Gift, which only this examination shows. They're turned away.
  - Then give them out **By hand**, choosing a magus of a represented covenant for each, or none. Or give them out **By bidding**. Each represented covenant with a magus who has no apprentice bids vis: a roll of a ten-sided die, 2 pawns for each such magus and a tenth of its vis. It bids more for a Gentle Gift and less for a Blatant, never more than it holds.
  - The highest bid wins the child for its first such magus. The price is taken from its Raw Vis Stores, the fullest first, each in its Diary.
  - The outcome shows under the form before you give them. Each child given becomes a Sketch character at their master's covenant, with their master as parens, and the minutes list where every child went. Once given, holding this step again changes only its note.
  - A magus has an apprentice when someone not yet a magus names them as parens.
  - The book says only that the Coill Trí owe seven Gifted children and that a child offered is sometimes turned away (The Contested Isle pp. 113-114). The three each túath offers, the odds of each Gift (14, 3 and 3 in twenty, one in twenty no true Gift) and the bidding are the app's own.
- **The Ceremony of Propitiation**, under the Theban customs, before the closing.
  - The archon casts the ancient Ritual from its Casting Tablet at eight pawns of Creo or Vim, taken from the treasury. Then each covenant offers to its patron.
  - Enter the pawns each covenant offers and its patron's Might, which is remembered for next time. Each patron gains 25 xp less its Might, the Might cut by two for every pawn offered. So a Might 25 patron offered 10 pawns gains 20 xp.
  - The League Against Idolatry boycotts the rite (The Sundered Eagle p. 31). The pawns offered aren't yet taken from the covenants' own stores.
- **Closing**: each case with a ruling is decided, and what its ruling says is written.
  - The fine is owed to the Tribunal's treasury.
  - The ruling goes into the Peripheral Code.
  - The attitude's move becomes a reason on the covenant's attitude.
  - A term's end goes on the case.
  - The Acta, the meeting's acts set out as a charter, goes into the Tribunal's Diary, and the next meeting is set for when the Tribunal next meets.

**Ruling templates.** A template's blanks are asked after the Rulings step, one form a case, with the finished sentence shown under it as you fill them. "{party} holds {what} for {years} years, until it is debated again" becomes "Keep holds the Rhine ford's vis for 7 years, until it is debated again". A {years} blank sets the term. A blank is any word in braces. The templates are the saga's own, kept in the saga's settings ([the saga](help:saga), Ruling templates), where you can add, change and remove them.

They include the Code's penalties (Houses of Hermes: True Lineages pp. 59-61):

- **Damages**: a fine shared a third to the prosecutor and two thirds to the Tribunal's coffers.
- Seasons of service.
- Investing items.
- Loss of an apprentice.
- Banished.
- Loss of a familiar.
- Death of a familiar.
- **Cast out**: the estate goes a quarter to the victim, a quarter to the prosecutor, a half to one who is both, and the rest to the heir (Houses of Hermes: True Lineages p. 59). A case's details show beside it the established convention that whoever slays the outcast takes the heir's half once the others are paid (p. 53).

Any step can be held again to change it. Saving it then goes on to the step in hand. Every step has a Note for anything said or decided in your own words.

**Terms that come due.** A ruling made for a term comes back. [Ahead](help:section-ahead) lists the season before its term ends and the season it ends. Advancing into the season before says it ends next season. Advancing into the season it ends says so, and puts the matter back on its Tribunal's docket as a new case for the next meeting, such as "Fengheld v. Keep (debated again)", with the old ruling in its charge. The case's details on the Docket show when its term ends.

**The minutes.** Each step held writes its minutes into the Tribunal's Diary. The entry is headed with its day ("¶ The First Day: The roll call and proxies"), with its numbers in the margin, such as the votes in the hall, a vote's tally or a fine, and its Note after its own words. Holding a step again rewrites its entry rather than adding another. The Acta, like any Diary entry, can be reworded by editing it.
<!-- gui -->
On the desktop, choose the Acta in the Diary and press Print to print it to a PDF.
<!-- /gui -->

**Transylvania's meeting.** Two steps come before the rulings.

*The Praeco's purse* (Against the Dark p. 19). The Tribunal gives the Praeco the projects they're to fund until the next meeting, and with them the levies they may raise.

- Write the projects, then a levy on each oppidum, in pawns of an Art, or in pounds with the Art left blank.
- The book has the legal covenants of the cives, socii and coloniae, and some of the foederati, owe the projects reasonable aid. They owe it by their status, not each magus for themselves. The hospites' covenant isn't named, so an oppidum of hospites can't be levied.
- The app lays each levy on an oppidum, and its hint says which of the oppidum's magi belong to a covenant that owes aid. Each levy goes on the treasury, owed until it's marked paid.
- The pawns from the large vis source set aside for the Praeco come into the treasury.
- The Praeco collects the Redcaps' and Quaesitores' stipends and Redcaps deliver them, so they only go into the minutes.
- The Praeco may redeem promissory notes, whose pawns leave the treasury, and issue a new one. What it borrows comes into the treasury now.

*The Curantis and his Notary* (p. 97). The Curantis keeps the zenodochia, the Tribunal's safehouses for travelling magi. They're appointed at every meeting for a term to the next, usually unopposed, and no one serves two terms running.

- Say whether the outgoing Curantis built a new zenodochium in their term, as they're expected to.
- Choose the new Curantis and the Notary the outgoing Curantis selected, often a Redcap or a magus fresh from their Gauntlet. Give the Curantis's salary, which leaves the treasury now.
- Both then show as offices on the Five Covenants list. A colona may not be Curantis.

**See also:** [How to hold a Tribunal](help:guide-tribunal), [Tribunal sheet](help:tribunal), [Meeting tab](help:tab-trib-meeting)

# The World Turns
<!-- help: world-turns -->

The yearly step. When Winter is played, Advance Season asks one more question before the season is played out: what the year brought beyond the covenants. Each line has a tick box, and only the ticked lines are applied.

- **Threat clocks**: a place's trigger tied to a threat comes up in the season it comes, Winter or not. Answer **Failed**, **Kept** or **Leave it unanswered**. Failed moves the threat on its steps, and the line says which stage that reaches. Kept leaves it where it is, and Leave it unanswered writes nothing. Failed and Kept are written in the threat's Diary and the place's.
- In a season other than Winter, the threat clocks are the only questions. They're titled *The World This Season*, and they go into an entry of their own.
- **Places**: each place's triggers that came this year, written into the place's Diary. With the Auras change rule option, each aura's year comes too. That's a Magic aura's yearly modifier and its roll on the Strengthening or Weakening table, or an Infernal aura's erosion. They're already rolled, so what you see is what's applied.
- **Threats**: a dated stage whose season has come is marked as having happened.
- **Neighbours**: each fair a covenant trades at rolls its income for the year.
- **Tribunal treasury**: a loan due this year. Tick it if it was repaid. It starts unticked.
- **Attitudes**: the year's events with each neighbour, such as favours begun or repaid, or a covenant's Diary entries naming it.
  - Where the year's favours make it plain, the change is suggested, with its reason filled in. That's +1 for each favour the covenant did the neighbour or repaid it this year, at most +3. Accept it by saving, or change it.
  - A Diary entry alone suggests nothing, since the app can't tell how it went. A change needs its reason.

**You type:** the ticks and answers above.

**The app works out:** everything applied goes into one entry, *The world turns, Winter 1220*, under The World Turned on Seasons. Delete that entry to undo all of it. A value changed by hand since is left as it is, and you're told.

Cancel stops Advance Season, and the date stays.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons)

# Season Summary
<!-- help: season-summary -->

Shown after a season has been advanced, when anything happened. It says what the season gave everyone, grouped by covenant.
<!-- gui -->
It's the **Just played** chapter of the [Seasons](help:seasons) page, first in its rail.
<!-- /gui -->

**You type:** nothing.
<!-- tui -->
Enter, Escape or Close closes it.
<!-- /tui -->

**The app works out:** one line per person, with the activity, what it was on and its result, such as the xp gained. A plan that couldn't be carried out shows why. A magus or companion with nothing planned is shown as "nothing planned". In Winter it also lists aging rolls, grogs' yearly updates and business upkeep, and in any season the covenants' vis harvests.

**What changed** comes next, for each player character the season changed.
<!-- tui -->
It's folded shut under the results: open it with Enter on its title.
<!-- /tui -->
<!-- gui -->
It's its own chapter after Just played.
<!-- /gui -->
It shows:

- their Arts and Abilities as new scores ("Creo 12 to 13")
- spells learned, and Virtues and Flaws gained or lost
- Warping, Decrepitude, wounds and Fatigue
- Confidence, Personality Traits and Reputations
- raw vis and silver
- books and enchanted items gained or given up.

The xp itself is in the lines above. To see what changed since the last evening of play, use **What Changed Since the Last Session** in a character's More (see [Sessions](help:tab-content-sessions)).

<!-- tui -->
The note at the bottom says whether the season is kept under Seasons in the tree.
<!-- /tui -->
<!-- gui -->
The note at the bottom says whether the season is kept on the Seasons page.
<!-- /gui -->
If season records are off in the saga's settings, each character's Diary still has their entry.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons), [How to plan and run a season](help:guide-seasons)

# Creation Worksheet
<!-- help: creation-worksheet -->

Walks a covenant, laboratory or character that's In Creation through the book's steps. It shows each step's budget, what was spent or taken there, and its checks. It opens by itself when you make a new covenant, laboratory or character.
<!-- tui -->
It fills the screen.
<!-- /tui -->
<!-- gui -->
It's a page of its own, below the record's in the trail.
<!-- /gui -->

**You type:** nothing in the worksheet itself. It opens the record's own forms, which edit the real record, and everything is saved as you go.

**The app works out:** the budgets and checks again whenever a form closes.

### In Creation and In Play
<!-- help: creation-worksheet-modes -->

<!-- tui -->
A new covenant, laboratory or character starts **In Creation**, with its tree node marked "(creating)".
<!-- /tui -->
<!-- gui -->
A new covenant, laboratory or character starts **In Creation**, shown in its page's header.
<!-- /gui -->
A character made from one of the Definitive Edition's templates starts **In Play**, since those are fully made. One made from a Grogs, quick, Mythic Companion, supplement or animal template starts In Creation, to finish on its worksheet.

<!-- tui -->
The record's top panel has a button showing the mode. Clicking it, or More's **In Creation / In Play**, switches between them after a confirmation.
<!-- /tui -->
<!-- gui -->
The record's header has a button showing the mode. Clicking it switches between them after a confirmation, and the page changes its colours to match.
<!-- /gui -->
Creation checks only run while a record is In Creation, and come back if it's moved back. When a covenant moves to In Play, the app keeps what its Build Points were spent on.

<!-- tui -->
Open the worksheet from the top panel's **Creation Worksheet** button, or from More's **Creation Worksheet** on the record's tree node or top panel. Both are only there while the record is In Creation.
<!-- /tui -->
<!-- gui -->
Open the worksheet with **Worksheet** beside the mode button. It's only there while the record is In Creation.
<!-- /gui -->

### Steps and their marks
<!-- help: creation-worksheet-steps -->

<!-- tui -->
The left column lists the steps:
<!-- /tui -->
<!-- gui -->
The rail on the left lists the steps:
<!-- /gui -->

- **A character**:
  - Concept
  - Virtues and Flaws
  - Characteristics
  - Early Childhood, or Pre-adult Life for an [animal grog](help:animal-grogs)
  - Later Life
  - Tradition Training, for a hedge tradition's member
  - Apprenticeship and Years past Gauntlet, for magi only
  - Equipment and Review Interests, not for an animal
  - Finishing Touches
- **A covenant**: Baseline, Resources, Boons & Hooks, Review Interests, and Review.
- **A laboratory**: Setting Up, and Review.

Each step is marked by how its checks stand:

- **✔** every check passes.
- **✘** a rule the book says must be followed is broken (a warning).
- **☞** advice: something the book says should be done isn't, such as too many or too few of something.
- **○** the step has no checks.

A companion may take The Gift, which is free, and then Hermetic Virtues and Flaws. The Definitive Edition says this should be extremely unusual, mainly to play through a magus's apprenticeship, since without magical training The Gift is almost entirely a Flaw (Chapter 3, page 45). So Virtues and Flaws gives that as advice. A Mythic Companion has no Gift, and a grog never has it.

Each step shows its budget and what's left, its list, its checks (each with what the record has), and buttons for its other edits, such as Edit Characteristics, Learn a spell or Buy a specialist. A row's details give a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

<!-- tui -->
Below the list the app counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Up and Down choose a step, shown on the right. Tab moves to the step's list and then its buttons, and Escape closes the worksheet. The chosen row's details show at the bottom.

The step's list works like every list on the sheets. **a** adds, as Add a Virtue on Virtues and Flaws, where F2 in the picker turns to Flaws, or Spend xp on the xp steps. **e** changes the chosen row, and **d** takes it back after asking.
<!-- /tui -->
<!-- gui -->
The page's header counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Click a step in the rail to show it. Its checks are under **Creation Checks**, and its other edits under **This Step**. Clicking a row of the list shows its details in the inspector on the right.

The step's list has its own buttons. One adds: **Add a Virtue** on Virtues and Flaws, with **Add a Flaw** under This Step, or **Spend xp** on the xp steps. For the row last clicked, **Change its xp** and **Take it back** (or **Remove**) act on it, asking first.
<!-- /gui -->
On an xp step each row shows the pool xp spent and the xp it gained. That's half again with an Affinity, rounded up on the whole spend. As you type, the Spend xp dialog shows what the pool xp gains, the score that buys and the pool xp the next score needs. It warns past the creation cap, and an Ability's Specialty can be given there too. Taking xp back always gives back the pool xp spent and takes off exactly what it gained. On the Later Life step, taking back a training package's row drops the whole package.

<!-- gui -->
Each budget is also a bar that fills as it's spent: gold while some is left, red once it's over, with the sums beside it.

Every xp step (Early Childhood, Later Life, Tradition Training, Apprenticeship, Years past Gauntlet) adds **Experience So Far**. It lists each Ability and Art the worksheet has put xp into, with what each step gave it, the total and the score it buys. This step's column comes first, in bold, so a step shows what the others already gave.

Above the steps, **Rules broken** names each step with a rule that must hold and doesn't, and how many. Click one to go to that step. Its rules are in the line's tooltip.
<!-- /gui -->

The Ability cap at creation goes by age, 5 under 30. An Affinity with the Ability raises it by 2 for that Ability, and Mentored by Demons lifts it. An Ability that advances as an Art, such as a hedge Art or a vitki's runes, has no age cap, only its tradition's (a vitki's runes, 10).

**Schools** (Art & Academe p. 79). Educated may name where the character studied:

- a rural or urban parish school
- a cathedral or monastic school
- a municipal school (Italy) for Medicine or for Civil Law. Its one major subject besides the basics is the student's choice, and the other isn't taught.
- an imperial school (Spain)
- a private tutor
- a royal court.

The school's masters' knowledge then caps the subjects it teaches. Its major subjects are capped at the school's limit (a cathedral school's is 6), its minor ones at half of it, rounded up, and a subject it doesn't teach at 0. A cathedral school teaches no Medicine, for one. The subjects are Artes Liberales, Latin, Greek, Hebrew, Theology, Civil and Canon Law, Philosophiae and Medicine. Other Academic Abilities keep only the age cap. Leave the school blank for no school's limits, for a university education, say. An Ability's details show when its cap is the school's.

On Later Life, (Gild) Trained gives two pools (Guardians of the Forests p. 20). One is 30 xp on Order of Hermes Lore, Intrigue and Durenmar Lore. The other is 60 more on General or Arcane Abilities and the Arts suited to the gild. The book lets the 60 buy spells too, a point a level. The worksheet doesn't spend pooled xp on spells yet, so give those levels by hand.

Specialists bought with Build Points are checked too. Each one's score in the Ability they serve with, and a teacher's Teaching, may be no higher than a new character of their age could have: 5 under 30, 6 to 35, 7 to 40, 8 to 45, 9 after that (DE pp. 180-181, p. 48). One with no Year Born is taken as under 30. A bought teacher can't have The Gift, so can't teach a Hermetic Art. They teach as the magi direct, two seasons a year (DE p. 180). The form for buying a teacher says so.

**Characteristics: young characters** (Apprentices, when it's in play). Below 14 the Aging Chart gives every Characteristic a modifier and a smaller Size, from -10 and Size -3 under a year to -1 and Size -1 at 12-13 (Apprentices p. 7). Grows Quickly reads Size one age category higher, Late Bloomer both one lower, and Deft (Characteristic) halves that Characteristic's modifier (pp. 11-12). Size Virtues and Flaws count from the first birthday, and a child is never smaller than Size -3 (p. 10). The worksheet shows the modifier and says what base Size to set. The modifier itself isn't added to the scores.

**Virtues and Flaws, with Apprentices in play:**

- Child Virtues and Flaws are for characters of 20 and younger (p. 11, Errata p. 82).
- Inherited ones are only for magi and companions, and must have manifested by 21 (pp. 10-11).
- No Virtue that grants experience points, such as Warrior or Educated, for a character made younger than 14 (p. 10).
- Turbulence Prone only with The Gift (p. 12).

**Later Life: parent's vocation** (Apprentices p. 14). From 6 to 14 a child may put xp in the Ability their same-sex parent earns a living by: a Craft or Profession, or a knight's Ride and Single Weapon. That holds even for an Ability of a type they couldn't otherwise learn, but their score stays at most half the parent's until 14. "Parent's vocation" on this step names the Ability and the parent's score.

**Apprenticeship: standard apprenticeship model** (a saga option, with Apprentices in play). A magus still in apprenticeship has, for each year so far, 19 xp for the first 12 years, then 6 xp and 40 spell levels a year for the last 3. Xp may buy spell levels, and spell levels xp, one for one. A Skilled Parens gives 5 xp and 10 levels a year more, a Weak Parens as much less (Apprentices pp. 10, 14). Parma Magica, Magic Theory and Latin are only advice until Gauntlet. A magus past Gauntlet keeps the Definitive Edition's 240 xp and 120 levels.

**Traditions and societies.** A hedge wizard picks their tradition on Concept with **Choose tradition**, once the saga offers one (see [How to play a hedge wizard](help:guide-hedge-magic)). It also adds the Virtues the tradition requires. A magus may choose a Hermetic society there, and a magus of House Ex Miscellanea one of the House's traditions, whose Virtues become their free House Virtues. The tradition's free Virtues, such as a learned magician's Entreat the Powers or a vitki's Minor Virtue from the master, are outside the Virtue and Flaw balance, as a House's are.

A crowned king, with the Church office "King (crowned)", whose race or nationality is Slavic, Magyar or Vlach holds Shapeshifter free, outside the balance. Its forms are a wolf, a lion and a dragon (Against the Dark p. 122). The king's Magic Resistance 10 is the crown's (DE p. 420).

**Tradition Training** then spends the apprenticeship the book gives, changed by Well-Trained and Poorly Trained:

- a vitki's 290 xp, counting the minimums
- a folk witch's 200. Her ten years of it, from about age ten, are left out of Later Life.
- a gruagach's 160, or 64 unGifted.

**Open the Arts** gives a Gifted member the tradition's Arts and Abilities at 0. The step's checks ask for the minimum scores and any share the Arts must have. The spell levels it gives are shown but not yet learned there. Puissant never counts, since it adds only when the Ability is used.

While a character is In Creation, the sheet's Edit Ability and Edit Arts say how much xp came from the worksheet. Take that back on the worksheet, not by lowering the total.

The checks follow Ars Magica Definitive Edition, Chapter 3: Characters, Detailed Character Creation Summary, for characters. For covenants they follow Ars Magica Definitive Edition, Chapter 6: Covenants.

**A covenant's Baseline.** The storyguide's Build Points must lie within the Power Level's range, and each magus who goes without a laboratory refunds 50 of them. **Set starting income** makes the covenant's sources of income by the rules. That's one Typical source (100 pounds a year) or two Lesser (40 each), or what a Poverty Hook or Wealth Boon allows.

With the optional rule Starting income by number of magi, the income gains or loses 15 pounds a year for each magus over or under six, made once, to its main source. A covenant whose one source is Lesser gains or loses only 6 a magus (DE p. 189). A Secondary Income source isn't adjusted, and two Lesser sources share the 15 between them. The book doesn't say, so this is the app's reading.

Choosing another Covenant Situation warns first, then removes the Boons and Hooks the earlier one brought and adds the new ones.

The book's three base covenants are:

- Weak: 200 Build Points, Low.
- Medium: 800, Medium.
- Powerful: 2000, High.

A base covenant's books and vis come as placeholders, each with its level, quality or pawns but no subject or Art yet. **Edit** on its Resources row chooses them, and the name can be changed there too. Its Lab Text and enchanted item levels are an allowance the Resources step counts against what you add. Choosing another base covenant warns first and removes the placeholders the first one left unfilled.

**A covenant's Resources.** A new covenant may buy:

- Art summae up to level 20 and Ability summae up to level 8, each with its quality cap
- tractatus up to quality 11
- Lab Texts and Casting Tablets up to the Power Level's highest level.

Buying from the saga's books lists only the books within those limits, each with its Build Points. The checks list any of the covenant's books, a new one included, that go over them (DE p. 179). A book with no level or Quality yet is listed under Not priced yet. Lab Texts and Casting Tablets are bought as a pool of levels. So their category shows one row with the levels and Build Points, and each text is listed below it with its level.

A specialist's Ability comes from the Ability picker, and it says where they belong among the covenant's inhabitants. A Craft makes a craftsperson, common or rare, with what it saves money on. A Martial Ability makes a member of the turb, and a teacher or anyone else is a specialist. The Build Points rules call them all specialists, and the covenant's finances count them apart.

**A covenant's Boons & Hooks.** The checks ask that the Boon and Hook points balance, and that an aura realm other than Magic comes with its Hook. A Contested, Indiscreet or Dwindling Resource Hook says it needs its source until Edit chooses one.

**A covenant's Review.** It advises when the covenant has fewer servants or teamsters than its inhabitants need (Other Covenfolk among its inhabitants), since they cost no Build Points. It also says how many grogs and other covenfolk the baseline gives for free, about one grog and two others per magus. **Add the baseline's people** puts them among the covenant's inhabitants as a row of grogs and a row of servants and craftsmen, whose numbers you can change there (DE p. 179).

**A character's Characteristics.** A free point from a heritage Virtue costs nothing and shows beside the budget:

- a Sidhe Faerie Blood's Presence (DE p. 79), or Bloodcap's Strength (Houses of Hermes: True Lineages p. 104). Either goes up to +3, or +4 with Faerie Legacy (Realms of Power: Faerie pp. 106, 109, 112).
- Giant Blood's Strength and Stamina, up to +6 (DE p. 83).

Uninspirational can't be taken while Presence or Communication is above 0. **Fill from an array** spends the 7 points in one go: choose an array, then place each of its scores on a Characteristic. The arrays come from Grogs p. 65, but are open to every character, whatever books are in play. The highest value starts on the Characteristic that's highest now, and Save refuses a value used twice or left out. With Improved or Weak Characteristics the budget isn't 7, so the arrays aren't offered and the step says why.

**A character's Early Childhood.** With the Grogs book in play, Covenant Upbringing's Covenant-bred childhood may also buy Latin and Order of Hermes Lore. A Feral Upbringing's child has no Language, and 120 childhood xp instead of 75 + 45 (DE p. 130). They're spent only on (Area) Lore, Animal Handling, Athletics, Awareness, Brawl, Hunt, Stealth, Survival and Swim.

**A character's Later Life.** A training package takes its years out of Later Life, and the step's line says so. A grog of 31 with a 5-year package reads "26 years: 5 in training packages, 21 years at 15 xp = 315 xp". The Failed Apprentice package needs that Virtue, as the Academic, Arcane and Martial packages need a Virtue opening those Abilities. A Jurist needs no Virtue opening Academic Abilities for the Advocate package (Grogs p. 68).

**A magus's Apprenticeship.** Skilled Parens gives 60 xp and 30 spell levels more, and Weak Parens as much less. Each spell learned is capped at its Lab Total, with an aura of 3, the Virtues that change a Lab Total, and +1 for a Magic Theory specialty in inventing spells or in one of its Arts (DE pp. 50, 168).

**Finishing Touches.** The review expects Confidence 1 with 3 points, or 2 with 5 for Self-Confident or Heroic Personality, and none for Low Self-Esteem.

**Specialties.** Each step that spends xp on Abilities advises (☞) giving every Ability a specialization, Spell Mastery aside (DE p. 157). Spend xp's Specialty box sets it, and the check names any left blank.

**Virtues and Flaws that change creation** (Definitive Edition, Chapters Three to Five):

- Savantism halves the creation xp and caps every Ability at 3 but its favoured one, at 6 (p. 143).
- Foreign Upbringing halves the caps of Languages, Area and Organization Lores and the social Abilities (p. 131).
- Sheltered Upbringing rules out Bargain, Charm, Etiquette, Folk Ken, Guile, Intrigue and Leadership (p. 144).
- A Redcap's first fifteen Later Life years give 300 xp, the book's fifteen years of apprenticeship (p. 105).
- Student of (Realm) opens its own realm's Lore, and Warped by Magic opens Magic Lore (pp. 110, 151).
- A Devil Child takes three Virtue points free (p. 56).

The review also advises:

- Warped by Magic's five Warping Points.
- A written language at 3 for Academic Abilities, Latin, Greek, Hebrew or Arabic (p. 158).
- Mastered Spells' 50 xp of Mastery (p. 96).
- Savantism's favoured Ability.
- The Nephilim's Great Stamina and Strength (p. 58).
- That a Gifted companion take only Hermetic Virtues of intrinsic ability, not of background or training (p. 64). The review counts these as training:
  - Skilled and Weak Parens
  - Mastered Spells
  - Infamous and Tormenting Master
  - Hermetic Prestige
  - a House's Outer Mystery or membership: Heartbeast, The Enigma, Faerie Magic, Verditius Magic, Clan Ilfetu, Guest of House Criamon
  - Diedne and Mercurian Magic
  - Flawed and Stockade Parma Magica

### The Grogs Aging Chart
<!-- help: creation-worksheet-aging-chart -->

A character older than 35 makes an aging roll for each year from 35 before play. **Roll pre-play aging** makes them all, each written in the Diary.

While the Grogs book is in play, a grog can instead **Use the Grogs Aging Chart**, on the Finishing Touches step. So can a companion, and a grog promoted from a Line or Sketch, not only a new grog (Grogs p. 65). It gives the expected Aging Points for each decade, from the chart in Grogs, Chapter 5 (Aging, the Easy Way, pp. 65-66).

**You type:**

- The kind of aging, Mild, Average or Harsh. A grog with Mild Aging can only take mild aging, and one with Poor Living Conditions only harsh.
- Whether to take the chart's crises. It's off at first, as the book suggests ignoring them for a new character.
- For harsh or mild aging, whether it moves the Ability cap.

The line under the form shows each decade and the total as you choose.

**The app works out:**

- **The decades**: ten years each from the first roll still to make, the last one shorter. Each takes the highest Aging Score of its years. That's age / 10 (rounded up), less the covenant's Living Conditions (with Mild Aging +1 or Poor Living Conditions -1) and any Longevity Ritual, plus the Virtues that change aging rolls. A score above 10 reads the chart's last row, below 1 its first. A shorter decade takes its share of the chart's points and crises, rounded up.
- **With crises**: the Decrepitude score rises by one for each crisis, with the points that score needs. The chart's points are divided by one more than the crises, rounded up. Paul, 45, with average aging at Aging Score 5, takes 5 points, or 5 + 3 = 8 with his crisis. No Crisis is rolled.
- **Where the points go**: a crisis's are spread over the Characteristics, highest first. Of the chart's, 45% go to the highest Characteristic. Of the rest, about half go to Quickness or Stamina, 30% to Perception or Presence, 15% to Strength or Dexterity and the remainder to Intelligence or Communication. A Characteristic with more Aging Points than its score, ignoring any minus sign, falls by 1, as with the yearly roll.
- **The apparent age**: a simple die for each decade. The decade ages it fully if the die is no more than the decade's Aging Points, otherwise by the die.
- **The Ability cap**: 1 higher after harsh aging, 1 lower after mild, when you chose to move it. The Later Life step's cap and checks use it, and Finishing Touches notes the chart's use.

It's written in the Diary as one entry and can't be undone.

### Moving to In Play
<!-- help: creation-worksheet-play -->

The last step has **Move to In Play**. It lists every check that doesn't pass and asks before moving the record.

A covenant with Build Points left over is told how many. Moving it to In Play turns them into Mythic Pounds in its Wealth, 10 pounds for each Build Point, the rate money is bought at. The books don't say what becomes of unspent Build Points. Without bought money a covenant starts with no significant cash (Covenants p. 56). So turning them into money is the app's own rule, at the rate Covenants gives for buying a starting reserve. To keep the covenant poor, go back and spend them first.

Checks never stop an edit. If the saga has **Enforce creation rules strictly** turned on in its settings, a record that breaks a rule it must follow stays In Creation until that's fixed. Advice never stops it.

**See also:** [Characters group](help:character-group), [The saga](help:saga), [How to create a character, covenant or laboratory](help:guide-creation)

# Import Data
<!-- help: import-data -->

<!-- tui -->
Brings records into the saga from files. Open it from More's **Import** on the saga node.

**You choose:** what to import, then the file. The terminal lists the folders and files of that kind.

In a browser or over SSH, as a storyguide signed in to a hosted saga, the list shows only the host's exports folder and the folders in it, named from there (`exports/...`). Up stops at it, and a path typed outside it is refused. Copy a file into that folder on the host's computer to import it from there.
<!-- /tui -->
<!-- gui -->
Brings records into the saga from files. Open it from **Import** in the saga page's **Saga Management** chapter.

**You choose:** what to import, then the file, in the desktop's Open window.
<!-- /gui -->

**The app works out:** a preview of what the file adds, shown before anything is added.

### What can be imported
<!-- help: import-data-kinds -->

- **Characters**, **Covenants** and **Laboratories**: a file exported from another saga with Export. The file must hold the kind you chose. The file picker starts in the exports folder.
- **A Whole Saga**: a file written by **Export Saga**. Every covenant, laboratory, character and familiar in it is added beside this saga's own, as importing each record would. Their books and devices come too, with the saga's own spells and house rules. So do its places, neighbours and calendar entries, and its Tribunals, joined to this saga's own of the same name.
- **A Content Pack**: a file written by **Export Pack** (see [Content packs](help:export-pack)), brought in as [Import a Content Pack](help:import-pack) says. A supplement that adds to a Tribunal pack is checked as it's read: it may change only the Tribunals, covenants, characters, neighbours and creatures it names, and only their fields, never an id. Anything else refuses it before any of it is applied.
- **A Mystery Cult**: a file written by **Export a Cult**. The cult, with its Lore, degrees, Scripts and components, joins this saga's own cults on Saga Content. One with a name this saga already has is marked "(imported)", and its founder, a character of the other saga, isn't kept. The file is checked as it's read, and one of the wrong shape is refused, naming what is wrong.
- **Books**: a CSV file with a header row. Its columns, in any order and any case, are name, type, language, author, year_published, description, art, ability, level, quality, tractatus_type, spell, codex, encyclopedia, opus and physical_form. Name and type are needed.
  - Rows with the same codex are bound together in one new codex of that name, an encyclopedia when its rows' encyclopedia column says yes.
  - A tractatus's opus can be commentary or correspondence.
  - physical_form is one of exemplar, flap-bound, juvenilia, edition de luxe, treasure-bound, ex libris, holographic, huge codex, unbound or damaged.
  - A level or quality of "var" means the figure is to be set later. The book is imported, highlighted until you edit it to give its numbers, and can't be studied until then.
  - Books imported here go to [the Armarium](help:armarium), unassigned.
<!-- tui -->
  - From a covenant's **Library** tab, More's Import puts them straight into that covenant's library instead.
<!-- /tui -->
<!-- gui -->
  - **Import**, a button on a covenant's Library, imports books straight into that covenant's library instead.
<!-- /gui -->
  - An owner or cost column is ignored, since the cost is always worked out.
- **Spells**: a CSV file, through the [Import Spells](help:import-spells) helper.

A saga, export, content pack or Mystery Cult file larger than 50 MB, or nested too deeply to read, is refused before anything is added; a picture larger than 5 MB inside an export is left out, as a missing one is. A row that can't be read is skipped, and the preview says why. When a book or spell has the name of one already in the saga, the app asks: Skip, Skip All, Duplicate or Duplicate All. Nothing is added until every question is answered, and cancelling a question imports nothing.

### Importing an exported record
<!-- help: import-data-records -->

What travels with the record comes too, and everything imported gets new ids. Ids are plain names (lowercase letters, digits, `_` and `-`): a record whose id isn't one gets a fresh one, its links following. A file with an id that isn't plain inside a record is refused, naming it, and so is a saga file with one when it is opened. Links to records that aren't in the file, such as a character's covenant, a laboratory's owner or a book's author, are matched by name to the one record of that kind and name in this saga, or dropped. The preview lists which.

A character's or laboratory's covenant is the exception when this saga has no covenant of that name. The file carries its name, aura and realm, and the import adds a covenant with just those, so the aura comes too. The preview lists it under Adds as having only its name and aura. Fill in the rest on its sheet.

A record with the same name as one already here is added beside it. Nothing already in the saga is changed, except that a laboratory with no owner, or a magus with no laboratory, can be linked to the imported partner the file names.

### Exporting
<!-- help: import-data-export -->

<!-- tui -->
More's **Export**, on a covenant's, laboratory's or character's tree node or top panel, writes that record to a file another saga can import.
<!-- /tui -->
<!-- gui -->
**Export**, in a covenant's, laboratory's or character's **Manage** chapter, writes that record to a file another saga can import. Manage is the last chapter on its page, with Update from a File and Delete.
<!-- /gui -->

**You type:** the File to write, and for a covenant whether to include its laboratories and characters. The file starts in the exports folder, and `.amm.json` is added if you give no `.json` ending. The line above Export warns when the file exists and will be replaced.

What goes with it:

- a character: their familiar, the enchanted devices they hold, their books and their Diary
- a laboratory: its books and the devices kept in it
- a covenant: its books and devices, and optionally its laboratories and characters with their own things
- the saga's own spells and house rules that these use.

Season plans, season records and lab projects under way stay behind.

**Pictures go too.** An export whose records have pictures on this computer is written as a zip, `.amm.zip`, holding the same file and its pictures, so they reach the other computer. That's a character's portrait, and with Export Saga or a pack, a Tribunal's maps.

Import reads a `.amm.zip` as it reads a `.amm.json`. It copies the maps into the maps folder, keeping one already there, since a map is named by its picture's bytes. Each portrait goes under its character's new name. Only pictures are copied (PNG, JPEG, WebP, BMP or GIF), under plain file names. A picture whose name has a folder or drive in it, or a file that isn't a picture, is left behind, and its record comes in without it. A file sent to a browser is the JSON alone, without its pictures.

<!-- tui -->
**Export Saga**, in More on the saga node, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. In a browser copy the file downloads instead. Only the storyguide can use it. **Export a Cult** beside it writes one of the saga's own Mystery Cults to a file, for Import's **A Mystery Cult**.
<!-- /tui -->
<!-- gui -->
**Export Saga**, a button in the saga page's **Saga Management**, beside Import, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. **Export a Cult** there writes one of the saga's own Mystery Cults to a file, for Import's **A Mystery Cult**.
<!-- /gui -->

### Content packs
<!-- help: export-pack -->

A content pack is part of a saga's world written to one file, to fill another saga with it or start a new saga from it. It holds Tribunals, covenants, characters, places, neighbours and calendar entries, with their links to one another.

<!-- tui -->
**Export Pack**, in More on the saga node, writes one. Only the storyguide can use it. In a browser copy the file downloads instead.
<!-- /tui -->
<!-- gui -->
**Export Pack**, a button in the saga page's **Saga Management**, writes one.
<!-- /gui -->

**You choose:**

- the pack's name and file
- an optional **Introduction**: a few paragraphs on what the pack sets up, a blank line between paragraphs, shown under the pack in Start from a pack
- a tick for each Tribunal, covenant, place and neighbour it holds.

A Tribunal takes everything in it: its covenants, the places they sit in and the places round and inside those, whoever is in those places, and the neighbours that hold an attitude toward or a link to its covenants. A covenant of a ticked Tribunal isn't asked about. **With their characters** adds the covenants' characters and laboratories and each Tribunal's Praeco and Presiding Quaesitor. **With the calendar** adds the covenants' calendar entries and the saga's own. The line above Export says what the pack holds.

In **Start from a pack** a pack is listed by its Tribunal ("Rhine Tribunal: 10 covenants, …").

When its name doesn't name the Tribunal, its name comes first, as in "Dammërstein (Rhine Tribunal): 1 covenant, …". So give a pack a name of its own.

The book packs come first, then the saga starters: ready-made covenants and sagas shipped with the app, such as Dammërstein. A starter is a pack exported like any other and put in the app's `data/saga_starters` folder. Every pack there is listed. A starter may name the shipped book pack it's built on (its `base`, such as `rhine`). Start from a pack brings that in first, and a starter whose book pack the app doesn't have isn't offered. A pack's maps go in a zip, as [Exporting](help:import-data-export) says.

A Tribunal's meeting under way stays behind, and its Diary comes without what its entries changed.

**Importing a pack** (Import, **A Content Pack**) is [Import a Content Pack](help:import-pack). A pack carries its Tribunals' maps and the pins of the records it holds. Importing it adds them as the pack's. A pin goes in only where the saga has none of that record on that map, so a pin you moved stays where you put it, and one you took off stays off. A map of a Tribunal the saga already has joins it, or is matched to its map of the same name.

**Starting a saga from a pack:** the Create a New Saga form offers **Start from a pack**. It lists the packs shipped with the app, one per Tribunal sourcebook (see [How to start a saga from a sourcebook](help:guide-book-packs)), then any pack in the exports folder. The new saga begins with everything in it. A pack built from a sourcebook puts that book in play when it's imported.

### Printing a record
<!-- help: print-record; gui -->

On the desktop, a covenant's, laboratory's, character's or familiar's **Manage** chapter has **Print to PDF**. It asks a few options first, then where to save the file. It starts in the exports folder, named after the record. The options you choose are kept for next time, all but the copy.

- **Copy** (asked only of someone who reads the whole saga, the host or a storyguide): **Player copy**, what the players may read, or **Storyguide copy**, everything, Secrets too. It starts at the Player copy every time, so nothing secret goes out by accident. Anyone else, a player signed in included, always gets the Player copy and isn't asked. A Player copy leaves off each Secret not yet revealed (a Storyguide Notes secret too) and anything the players don't know of. A player printing their own character still gets their own notes and goals.
- **Sheet** (characters only): **Play sheet**, a page or two to play from, or **Full record**, everything.
- **Paper size:** US Letter, or A4 outside North America.
- **Theme:** **Each in its House's colours** (a magus, their laboratory and familiar in their House's theme; covenants, companions and grogs in Scriptorum), or any theme by name, for everything you print. The page takes the theme's colours, its paper and its House's mark beside the title and in the running head, with the mark large and faint behind the first page's title (the Order's sigil in Scriptorum).
- **Background:** **The theme's paper**, or **Plain white** to save ink. A dark theme's paper takes a lot of ink. On plain white a dark theme prints in its light colours (Scriptorum Dark as Scriptorum; a dark House theme in Scriptorum's colours with its own mark, until it has a light version), so there is never pale ink on white. The faint mark is left off plain white.

A character prints as a sheet laid out for paper, not a picture of the screen. Their name is set in the title lettering, with a bound edge down the left of each page. Whatever the theme, nothing on the page carries meaning by colour alone.

The **play sheet** is about a page for a companion or grog and two for a magus. The first page has the Characteristics, the Virtues and Flaws by name, Personality Traits and Reputations, the Abilities and Combat & Condition. A magus's second has the Arts, Casting Scores, Raw Vis and the spells, a line each with their Arts and level, Range, Duration and Target, and Casting Total. It leaves off the description, biography, books and diary.

The **full record** has everything, in this order:

1. The Characteristics, Personality Traits and Reputations, the Abilities and Combat & Condition.
2. Whatever of Combat & Condition didn't fit, then the Virtues and Flaws, each with what it does, in two columns that end level.
3. For a magus, the Hermetic Background and Wizard's Sigil, then the Arts, Casting Scores, Raw Vis and research goals. This follows on from the Virtues and Flaws, and starts a page of its own when little of the page is left.
4. From a new page, the description and biography, the familiar in short (its own sheet prints from its own page), books, diary, the player's notes and goals, and the Secrets the copy may hold, each marked revealed or not.
5. Last, from a new page, the Grimoire: the spells by Form, each with its full description. A spell is never split between pages: one that won't fit starts the next page, and only a spell longer than a whole page runs on, its name marked continued.

Nothing else is cut by the page edge:

- A section runs on to the next page where the page ends: a table between its rows, with its header again.
- A heading always stays with what it heads, and the Combat box with Weapons and Equipment.
- Companions and grogs have no magic pages.
- The Abilities are set in two columns by category, and the Arts in three, the Techniques beside the Forms. Each Art and Ability has its symbol beside it.
- Anything taken more than once (a Virtue, Flaw, Boon or Hook) is printed once with its count, as **Great Intelligence × 2**. The screens still show each one.
- Combat & Condition follows the published character sheet. It has a box for each Fatigue level and five for each Light, Medium and Heavy Wound, with the current ones ticked. It also has blank lines to pencil in weapons, armor and equipment, with the character's own already filled in.
- Empty sections are left off, except Raw Vis, which keeps lines to pencil in what is gathered in play.

Covenants, laboratories and familiars print the same way, as a full record laid out for paper, real text you can search and copy:

- **A covenant:** its aura and Charter figures, then the Overview (its description, Reputations, and the Boons beside the Hooks), the Charter and its clauses (a broken one marked Broken), People and Covenfolk, the Laboratories a line each, the Library shelf by shelf, the Treasury, the Inventory (vis sources, stores, every other possession and the enchanted devices), the Diary and the History, every entry of each. A Line or Sketch covenant prints what it is to the saga, its magi, What Matters, its Charter and Diary.
- **A laboratory:** its Characteristics, its owner's Lab Totals, its Virtues and Flaws, Specializations, Features, magic items and rooms, its stores (raw vis with lines to pencil in, equipment, Arcane Connections, Lab Texts and books) and its Diary.
- **A familiar:** its master, species, Characteristics and Might, the Cords and the binding, Bond Powers, Combat & Condition, natural weapons, Abilities, Virtues and Flaws and Personality Traits.

Seasons, Planning, Build and Manage are left off, since they're for the screen, and so are empty sections. A record's Secrets go at the end, as the copy may hold them. Nothing on paper carries meaning by colour alone: the Lab Totals are plain numbers with the five best in bold, a Specialization's bar is its points (struck through when it is turned off), a contested source keeps its ! mark and its standing in words, and income it doesn't give this year is struck through beside what it does.

**Print the Troupe**, on the saga page's The Troupe chapter, prints every player character into one PDF, in the order The Troupe lists them. Each starts on a fresh page, and the PDF has a bookmark for each, so a reader's side panel lists them by name. It asks the same options, with **Sheet** choosing play sheets or full records for all of them, and **Theme** each magus in their House's colours (companions and grogs in Scriptorum) or everyone in one theme: Scriptorum, Scriptorum Dark, or a House's, for a saga of one House. A player printing the troupe always gets Player copies.

The PDF can be printed or sent like any other.

### Exporting a sheet as Markdown
<!-- help: export-markdown -->

**Export as Markdown** writes a character's, covenant's, laboratory's or
familiar's sheet as a Markdown file (`.md`), plain text that any editor,
wiki or notes app shows with its headings and tables: for your own notes,
an Obsidian vault, or a message to the troupe.
<!-- tui -->
It is in More (`m`) on the record, beside Export. In a browser copy the
file downloads to your own computer.
<!-- /tui -->
<!-- gui -->
It is in the record's **Manage** chapter, beside Print to PDF.
<!-- /gui -->

It asks the same **Copy** as printing (only the host or a storyguide is
asked; anyone else gets the Player copy) and, for a character, **Sheet**:
a play sheet or the full record. Then the file, in the exports folder,
named after the record.

The file holds what the printed sheet does, laid out for text: the
Characteristics and facts as short tables, each list as a table, Fatigue
and Wounds as a small table each with the current Fatigue level marked
◀ now, and the Grimoire's spells under their Form. What only paper needs
is left off: the Art and Ability symbols, and the blank lines and boxes
left to pencil in. See [How to export a sheet as Markdown](help:guide-export-markdown).

### How to export a sheet as Markdown
<!-- help: guide-export-markdown -->

1. Open the record: a character, covenant, laboratory or familiar.
<!-- tui -->
2. Press `m` for More, then **Export as Markdown**.
<!-- /tui -->
<!-- gui -->
2. Open its **Manage** chapter and click **Export as Markdown**.
<!-- /gui -->
3. Choose the **Copy** (if you are asked): **Player copy** to share it,
   **Storyguide copy** for your own notes. For a character choose the
   **Sheet**: a play sheet, or the full record.
4. Check the **File**: it starts in the exports folder, named after the
   record. Click **Export**.
5. Open the `.md` file in any text editor, or drop it into a wiki or a
   notes app such as Obsidian, which shows its tables.

### Giving to another record
<!-- help: give -->

**Give** hands what one record holds to another record of the saga. It acts on the chosen row of:

- a Raw Vis list
- a books list, a laboratory's Lab Texts too
- Enchanted Devices
- a character's Personal Gear
- a covenant's Weapons, Armor or Items.

<!-- tui -->
It's in More (`m`) on those lists.
<!-- /tui -->
<!-- gui -->
It's a Give button beside the list's Add, Edit and Delete, acting on the row last clicked.
<!-- /gui -->

It asks who gets it and, for vis and gear, how many. A book changes owner, and a device changes holder, its epitome going with it. Gear given in part is split, so both keep some. Vis goes to a covenant, a laboratory or a magus. A laboratory takes no gear or silver. A book bound in a codex takes its whole codex, and the form says so.

In [the Armarium](help:armarium) and [the Custodia Mirabilium](help:custodia), Give hands any book or device on. That's one already held, as above, or one nobody holds (Unassigned) to its first holder, with only the receiver's Diary recording it.

**Give Silver** gives pounds of silver from a character's purse, on Personal Gear, or a covenant's Wealth to another character or covenant. So someone leaving a covenant can take silver with them. Both sides' Diaries record every gift. A covenant files it under Library for a book, else Purchases & Sales, with the pounds for silver. Only the storyguide can give.

### Updating a record from a file
<!-- help: import-data-update -->

<!-- tui -->
More's **Update from a File**, on a covenant's, laboratory's or character's tree node or top panel, reads an export of that same record over it, for example after working on a character on another computer. Only the storyguide can use it.
<!-- /tui -->
<!-- gui -->
**Update from a File**, in a covenant's, laboratory's or character's **Manage** chapter, reads an export of that same record over it, for example after working on a character on another computer. Only the storyguide can use it.
<!-- /gui -->

**You choose:** the exported file. It must hold the same kind of record.

**The app works out:** what would change, field by field, such as "Abilities: 1 added, 2 changed" or "Name: Old → New". It also lists the links in the file it can't match here. Nothing changes until you choose **Update**, and a file that changes nothing says so.

It replaces the record's own contents and what travels with it in an export. For a character that's their familiar, devices and books, and for a laboratory or covenant its books and devices.

It keeps the record itself, so everything that points at it still does. It also keeps where the record sits in this saga, such as a character's covenant and laboratory, or a laboratory's covenant and owner. A covenant's file made with its laboratories and characters updates the covenant only. Update each of them from its own export.

**See also:** [Import Spells](help:import-spells), [The Armarium](help:armarium), [The saga](help:saga), [How to import and export](help:guide-import-export)

# Import a Content Pack
<!-- help: import-pack -->

The form shown after choosing a pack's file in Import Data, **A Content Pack**, asks which of its parts to bring in.

A pack's Tribunals and covenants always come in, since they're what the rest hangs on. A region book's pack has covenants and no Tribunal. The rest is a tick each, all ticked to begin with, and a part the pack holds nothing of isn't asked about:

- **Their people**: the covenants' characters, laboratories and familiars, and each Tribunal's Praeco and Presiding Quaesitor.
- **Generated stats for magi**: asked only while their people are ticked. A book pack gives full stats to the magi its book describes but prints no stat block for. Those stats aren't an official write-up. They're inferred from the book's description by the creation rules, and each such magus's Biography says so. Untick it to bring those magi in as the book's sketches. The magi the book does print stat blocks for come in full either way.
- **Places and regiones**: the places the covenants sit in, the places round and inside those, and their regio levels.
- **The mundane world**: lords, towns, the Church, universities, factions and threats.
- **Code, cases and fines**: each Tribunal's Peripheral Code, docket and fines.
- **The history**: each Tribunal's Diary, each covenant's Diary (where a pack with no Tribunal keeps its history), and the calendar entries.

Then each of the pack's stories (its threats) that this saga doesn't already have is a **Begin** tick, shown while the mundane world is ticked. A story left unticked comes in **dormant**. It's listed among the Region's Threats as Dormant, reaches no stage, and nothing of it comes due until **Begin This Story** in its More starts it.

If the saga already has one of the pack's stories, told differently, as the Fifth Crusade is in the Cradle and Nile packs, a **Use this book's** tick asks which to keep. Left unticked, the saga keeps its own.

The line under the ticks says what the pack brings with the ticks as they are. **Preview** then shows:

- what it adds
- what this saga already has of the same name, kept as it is, with the pack's links pointing to it and the books, devices and familiars of those records skipped
- what else is skipped, such as a calendar entry already in the calendar, or one for a covenant that isn't here
- the links kept and dropped.

What a left-out part held is matched by name to this saga's own, such as a covenant's place or a Tribunal's Praeco, or the link is dropped, and the preview lists which. A covenant whose place is left out sits nowhere until you place it. Starting a saga from a pack brings everything, and asks which of its stories to begin in the same way.

A place, threat, faction or lord this saga already has is kept as it is, with one exception. The pack's roll tables on it are added when the saga's has none of the same name, in any case. The preview says so ("1 roll table to The valley of Durenmar"). So a saga starter can bring "Rumours about Dammërstein" to a Rhine Tribunal place. A table the saga has is never overwritten, and importing the pack again adds nothing.

A saga starter built on a book pack, imported into a saga without that book's Tribunal (Dammërstein into a Transylvanian saga), first asks **First bring in the Rhine Tribunal**. It's ticked, with the book pack's own choices under it, so it can come in lightly. The preview shows the book pack's import, then the starter's over it. Untick it and the starter comes in alone, and the preview says its tables for the Tribunal's records come in on records of their own. A saga that has the Tribunal isn't asked.

Importing a pack again, or a newer copy of it, leaves every record the saga already has as it is and adds the rest (see [Adding a book to a saga you already have](help:guide-book-packs-add)).

**See also:** [Content packs](help:export-pack), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Import Spells
<!-- help: import-spells -->

Explains what a spell CSV file looks like before you choose one, or saves an example to start from (see [The buttons](help:import-spells-buttons)). The spells imported become the saga's own spells, which you can edit on [Spells](help:tab-content-spells).

<!-- tui -->
Open it from More's Import on the saga node, then Spells. In a browser or over SSH, the example is saved in the host's exports folder, the one folder the file list there shows.
<!-- /tui -->
<!-- gui -->
Open it from **Import** in the saga page's Saga Management chapter, then Spells.
<!-- /gui -->

**You type:** a CSV file with a header row. Columns, in any order and any case:

- **name**, **technique** and **form** (required). A Technique or Form can be written in full or abbreviated (Cr, Ig...).
- **level**: a number, or Gen (or blank) for a General spell.
- **requisites**: extra Arts, for example Rego, Corpus.
- **range**, **duration** and **target**, in full or abbreviated (Per, Mom...).
- **ritual**: yes or no. Blank is no.
- **base_level**: the guideline level before Range, Duration and Target (optional).
- **description** and **source**.

**The app works out:** a preview of the spells found, the rows skipped and why, and any columns it didn't use. Names already in the saga are compared in any case, and the app asks about each one: Duplicate, Duplicate All, Skip or Skip All.

### The buttons
<!-- help: import-spells-buttons -->

- **Choose CSV File** goes on to pick the file.
- With **Save an example CSV instead** ticked, it writes `spells_example.csv` instead, numbered if it exists, to the folder the app was started from. It holds two example spells. Edit it, then choose it to import.
- **Cancel** closes the helper.

**See also:** [Spells](help:tab-content-spells), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Delay or Hasten
<!-- help: threat-delay -->

Something the troupe did, or failed to do, pushes a threat later or brings it sooner, without editing each stage.

- **A threat moving by fixed dates**: give the seasons later, or below 0 for sooner. Every stage still to come moves by that much. The dates you typed stay as they are, and the threat's Edit shows the delay so far in Delayed by. A stage already marked Happened, Stopped or Turned doesn't move.
- **A threat moving along a track or an omen count**: give the steps back, or below 0 to move it on. Its position can't go below 0.

**You type:** how far, and why.

**The app works out:** the new dates or position, and a line in the threat's [Diary](help:tab-nb-threat-diary) saying what moved it and why. To undo it, Delay or Hasten again the other way, or Edit the threat.

**See also:** [A threat](help:tab-nb-threat), [How to set up a threat's clock](help:guide-threat-clock)

# Take Up the Tale
<!-- help: take-up-tale -->

The troupe picks a story up again. Each chapter records what the troupe did, met or avoided, dated by season, so the Diary keeps a record of each time.

- **On an open story**, from a covenant's Diary, the Region's [Open Stories](help:section-region-stories) or [Needs You](help:section-attention). The chapter is an entry of its own in the same covenant's Diary, of the category Chapter, naming its story. A story grown into a threat is taken up on the threat instead.
- **On a threat**, from its page's More or a threat's row on Needs You. The chapter goes in the threat's [Diary](help:tab-nb-threat-diary) and each troupe covenant's.
- **How the Tale Ended**: marking an open story Resolved asks for its last chapter, on the same form. Cancel leaves it resolved with none.

**You type:** the year and season, this one unless you change it, and what the troupe did. On a story, also give who **Went** and the **Days it took**. Who went is ticked for you from who played whom at the [Session](help:tab-content-sessions) at hand. A threat's chapter asks for neither.

**The app works out:** the chapter's Diary entry. The story's or threat's details then list its chapters, oldest first, with who went each time, and a grown story's chapters go on into its threat's. A chapter with a cast goes on to its aftermath, [Close the Chapter](help:close-chapter). Cancel there leaves it open, to close later from Needs You.

**See also:** [How to follow a story from its start to a threat](help:guide-story-hook), [Diary tab](help:tab-cov-diary), [Close the Chapter](help:close-chapter)

# Close the Chapter
<!-- help: close-chapter -->

What a chapter of a story gave the characters who went (DE pp. 376-377, Adventure; p. 265; Grogs p. 67). It's asked once for the whole cast after Take Up the Tale or How the Tale Ended, or later from the chapter's **Close** row on [Needs You](help:section-attention).

**You type:**

- First the Adventure's **Source Quality**, 5 to 10, as the storyguide judges how much the story taught. There's one for the season, however many adventures it held.
- For each of the cast, whether they take it. A magus who plans seasons chooses between the Adventure and keeping their laboratory work with the chapter's days away. Anyone else takes it or not.
- Then, for each who takes it, up to four **Subjects** from their Arts and Abilities and the **Points** each gets. That's at most 5 to one, and no more than the Source Quality in all. An Art counts only if it was used on stage, which the app leaves to you.

**The app works out:**

- An Adventure plan for the chapter's season for each character who plans seasons, checked like one made by hand. A second chapter in the same season updates that plan, raising its Source Quality and adding subjects, and never doubles it.
- A magus keeping their work has the days added to their plan's days away.
- A grog gets the experience at once, as Story Experience gives it, counted against the year's update.

Confidence and noteworthy deeds stay with each character's End of Session. Marking a Session Played reminds you of its chapters not yet closed.

**See also:** [Take Up the Tale](help:take-up-tale), [Sessions](help:tab-content-sessions)

# Grow into a Threat
<!-- help: grow-story -->

An open story the troupe left alone becomes a threat of the Region, a story that grows on its own (see [A threat](help:tab-nb-threat)).

**You type:** the threat's name (the story's, unless you change it), its antagonist, and how it moves, by fixed dates, a track or an omen count. Say too whether it begins now or waits, dormant, until Begin This Story.

**The app works out:** the threat, with the story's words as its summary and a link to the covenant whose Diary kept the story. The story is marked **Grown into a threat**, so it leaves Open Stories, and the threat's Diary says where it came from. Add its stages on its page.

**See also:** [Open Stories](help:section-region-stories), [How to follow a story from its start to a threat](help:guide-story-hook)

# Host for Players
<!-- help: host-for-players-window; gui -->

Open it from **Host for Players** in the saga page's **Saga Management** chapter. It's the one place you host the saga and manage who joins. It stays open beside the game, so you can keep playing while it's open.

At the top, choose how **players join**:

- **Remote seats** (Their own Armarius, over the internet). Each player
  runs the app, which connects through a tunnel you set up yourself, such
  as Cloudflare Tunnel. See [How to host for Remote seats](help:guide-hosting-internet).
- **Browser or terminal** (On your private network). The older way, over
  Tailscale or ZeroTier. See [How to host for browsers and SSH](help:guide-hosting-local). An
  address the internet can reach is refused unless you tick **I know this
  is reachable from the internet**.

Under it, the window says whether the saga is hosted, with **Host** or **Stop Hosting**. To switch the way players join, stop hosting first. Closing the app while the saga is hosted asks first, as it ends every player's connection.

For Remote seats it also shows the host's **six words**, which you read aloud on your group's call. It has three pages, chosen on the rail at the left: Requests, Seats and Log. The window looks for new requests every few seconds. The title, and Requests on the rail, count those waiting.

### Players
<!-- help: remote-seats-players; gui -->

Who may sign in is on the saga page's **Saga Management**, beside the Host for Players button. The [Players](help:section-players) list shows each player's role, the characters they play, and whether they can sign in from a Remote seat (**✓ Ready**, or why not).

A player's form has a **Plays** tick for each of the troupe's characters, and several players may tick the same one. A passcode needs at least 14 characters (see [Changing or forgetting your passcode](help:join-game-passcode)). Choose a player there and **Issue Invite** to invite them, and this window opens with the Invite.

**Storyguides in troupe-style play.** Give a player the role **Storyguide** to let them run the saga from their own seat. They see everything, such as Secrets, unknown records, Roll Tables and threats' stages to come. They can change any record, advance the season and change Saga Settings. What stays yours, on this computer only, is who may join and as what: the Players and their roles, this window, and deleting the saga.

Making someone a storyguide whose devices already have seats asks first, naming those devices. The change reaches their seat within seconds, and the Log notes it. Storyguides are marked "(storyguide)" in these lists, in the Log, and beside the trail when they're viewing a record.

To play a character yourself for a while, use **Play as** in the title bar. Hosting goes on, and its menu keeps **Host for Players** one click away until you choose **Storyguide** again.

When a storyguide advances the season from their seat, this computer backs the saga up first. Then it takes the saga in as it takes any save, keeping a player's change made meanwhile unless it touched the same thing. If two storyguides advance at once, the first wins. The second is told who advanced, and nothing of theirs is changed.

While the saga has players, your own window picks up what they save every few seconds. The page is drawn again, with a note at its foot such as "Anna changed Leandro; reloaded." It waits while you have a form or question open, so nothing you're typing is touched.

A player's change reaches only what's theirs to change: their characters, those characters' labs, familiars and season plans, and the covenants if you gave them covenant rights. It never removes anything hidden from them, such as a Secret. Where you and a player changed the same thing, the later save is kept.

A player needn't play a character to join. Once in, they can make their own with **New Character** (see [Joining with no character yet](help:join-game-new-character)). It arrives here named as theirs, with a note like any change, and the Log notes it too. Change or delete it as you would any character.

### Host for Remote Seats
<!-- help: host-remote-seats; gui -->

**Host**, with Remote seats chosen, asks:

- **Tunnel address:** the https address your tunnel gives you, such as `https://saga.example.com`, with nothing after the name.
- **Tunnel:** Cloudflare Tunnel, or another, such as ngrok or Tailscale Funnel. It tells the app where the tunnel says each player's own address is, so the limits on connections count each player apart.
- **Port:** the port on this computer the tunnel points at, 8790 unless another program has it.

The line under the fields says what to point the tunnel at (`http://localhost:PORT`) and the address the Invites will carry. The app listens on this computer alone, and only the tunnel reaches it. The choices are kept for the saga, outside the saga file.

### The Chronicle at a Remote seat
<!-- help: chronicle-seats; gui -->

Preview: turn on Virtual Tabletop in Settings.

The preview is turned on in the host's Settings, on the computer the storyguide hosts from. A headless host serves Remote seats as before, without it. A seat needs nothing turned on: while the host's Session is under way, the seat is sent its [Chronicle](help:chronicle), shown in the [Chronicle pane](help:chronicle-pane).

- The seat opens a second connection, used only for the Chronicle, beside the one it reads and saves the saga on. Each entry comes down it within about a second.
- The host sends a seat only what its player may see. A Private roll of someone else's, or a Blind roll's number, never leaves the host's computer for that seat. It isn't sent and hidden; it isn't sent at all.
- A seat keeps the Chronicle in memory only. Nothing of it is written on the player's computer. Reconnecting, or starting the app again, it's sent again from the last entry it holds, or from the start.
- A roll from a seat says what to roll, never the number. The host rolls it, for a character the player plays tonight, at most 30 a minute.
- A [Table roll](help:table-rolls) made from a form at a seat draws each die from the host, one at a time, at most 50 dice a minute. The host keeps the faces and writes the roll; the seat sends back only the form's result. A seat that drops mid-roll leaves the dice it drew, as drawn, then cancelled.
- An entry of a kind this version doesn't know shows as "Something this version can't show; update Armarius."
- A seat on a version of Armarius from before Table rolls can't join until it's updated, and an updated seat can't join a host that hasn't been.

**See also:** [The Chronicle](help:chronicle), [Host for Remote Seats](help:host-remote-seats)

### Issue Invite
<!-- help: issue-invite; gui -->

On **Players**, with the player chosen, or on **Requests**, **Issue Invite** asks which Player to invite. Players and storyguides are both offered, storyguides marked. Only those whose passcode has at least 14 characters, set since this rule began, are offered. The others are listed with the reason. A storyguide's device will see everything in the saga, and approving it says so.

The window then shows the line to send the player by chat or email, with a **Copy** button, and the host's six words to read them on the call. The line works once, on one device, for 24 hours. It's shown only this once and can't be shown again, so if you close it unsent, issue another.

### Requests
<!-- help: remote-seats-requests; gui -->

When a player's app uses an Invite, their device waits here, with the player, the device's name, its **three words** and when it asked. Ask the player to read you the three words their screen shows. **Approve** asks whether they match before it gives the device a seat. **Reject** turns it away, and its Invite is spent. A request not decided within an hour lapses.

A player who has forgotten their passcode asks here too, from a device that already has a seat. **Asks for** says *A new passcode*. Check it's really them, on your call say. Then **Set New Passcode** opens their player form: type a new passcode and tell it to them. Setting one, here or on Players, answers the ask, and their device keeps its seat. **Reject** turns the ask down, and they keep the passcode they have.

Players can also change their own passcode from their seat. The Log notes it, never the passcode.

### Seats
<!-- help: remote-seats-list; gui -->

Each device given a seat, with the player, the device, its words, when it was last used, and when it expires if unused, or when it ended.

- **Revoke** ends the chosen seat. Its connection is cut within a second, and the device needs a new Invite to come back.
- **Idle Expiry** sets how many days a seat may go unused before it stops working, for this saga. It's 90 unless changed.
- **Rotate Host Key** gives the host a new key. Every Invite, waiting request and seat ends at once, and each player needs a new Invite and hears the new six words. If the saga is hosted, it starts again with the new key.

### Log
<!-- help: remote-seats-log; gui -->

What happened to Remote seats, newest first:

- Invites issued and redeemed
- requests approved or rejected
- sign-ins, wrong passcodes and lock-outs
- reads of the saga
- each record a player changed, and each change refused
- revoked and expired seats, and new host keys.

**Show** narrows it to one player. The log records who and when, never a passcode or a code, and keeps a year. It's kept outside the saga file, so players never receive it.

**See also:** [How to host a saga](help:guide-hosting), [Players](help:tab-content-players)

# Join a Saga
<!-- help: join-game; gui -->

Join a saga your storyguide hosts on their own computer, from your own copy of Armarius, over the internet. Click **Join a Saga** on the title page or the Sagas shelf. The first time takes a few steps. After that you sign in with your passcode.

### The first time
<!-- help: join-game-first; gui -->

1. **Paste the invite** your storyguide sent you, a line that begins `ARM1`. It works once, on one computer, for a day.
2. **Check the six words.** Your storyguide reads six words out on your call. Compare every one with the six on your screen, since the first two or three alone are far easier to fake. If all six match, click **They match**.
3. **Stop if they differ.** If they don't match, click **They don't match**. The invite may have been changed on its way to you, so nothing is sent. Ask for a new one, by another way if you can.
4. **Name this computer**, its own name to start with, so your storyguide knows which device is asking. Then click **Ask for a Seat**.
5. **Read your three words** to your storyguide. When they match what their screen shows, they let you in, and the window moves on by itself.
6. **Type your passcode**, the one your storyguide gave you (at least 14 characters). The saga opens.

The saga then stays on your shelf, marked **Hosted elsewhere**.

### When your version and the host's differ
<!-- help: join-game-versions; gui -->

Joining compares your Armarius with your storyguide's, from the host's
greeting (nothing is asked of GitHub).

- **Another major version** (the first number differs) stops you joining.
  If yours is the older, it says the host runs Armarius X and you run Y, so
  update to the host's major version, and **Update** opens the app's
  Releases page. If the host's is the older, it says "Your storyguide's
  Armarius is older (X). Ask them to update.", with no button.
- **Another minor version** (only the second or third number differs) lets
  you play. In the joined saga, the settings gear wears its "!" seal and
  the Settings window's Update row says "Your host runs Armarius A, and you
  run B. You can play, but these versions haven't been tested together, so
  some things may behave oddly." It offers **Update** when yours is the
  older.

On the storyguide's side, the Players list in Saga Management notes a
player who last joined on another version, as "4.13.1, not tested with
yours". Nothing is ever blocked by it.

### Coming back, and leaving
<!-- help: join-game-again; gui -->

When the saga you played last is a joined one, **Open Saga** on the title page opens it, as it does a saga of your own. Otherwise click the saga on the shelf and type your passcode. You stay signed in until you close the app, leave the saga, or your seat ends. Going back to the Sagas shelf and opening it again doesn't ask for the passcode.

If the connection drops while you play, the app connects again by itself. Changes you made meanwhile are sent once it's back, and closing the app before then asks first.

If your seat has ended, the app says so, and you'll need to ask for a new invite. A seat ends when your storyguide revokes it, when you don't use it for a long while, or when they give their host a new key. **Leave Saga** on the saga's card forgets this computer's seat. To come back you'll need a new invite.

### Changing or forgetting your passcode
<!-- help: join-game-passcode; gui -->

**Change Passcode** on the saga's card changes it. Type the passcode you have now, then the new one twice. It needs at least 14 characters, and a few words you'll remember, such as "grey owl over the mill", are easiest. A wrong current passcode counts toward the lock-out, as signing in does. You stay signed in, and from then on you use the new one on every computer you join from.

Forgotten it? Click the saga on the shelf, then **I've forgotten my passcode** under the passcode. Your storyguide is asked. They check it's really you, on your call say, and give you a new passcode, which you type there. This computer keeps its seat, so you need no new invite. Only a computer that already has a seat can ask.

While you play, your pages show what you may see, and you change only what's yours:

- your characters, their laboratories, familiars and season plans
- the season plans of characters you're Steward of
- your teaching asks and answers
- the covenants, if your storyguide gave you covenant rights.

### Joining with no character yet
<!-- help: join-game-new-character; gui -->

You can join before you have a character. **Your Characters** on The Troupe then says "None yet", with a **New Character** card. Click it to make your own, a magus or a companion. You can make a grog too if your storyguide gave you covenant rights, since a grog joins the covenant's household. It's yours from the start, named as played by you, and opens on its Creation Worksheet so you can carry on building it. Your storyguide sees it at once and can change or delete it like any other. You can't make one for someone else or for the whole troupe, since who plays a character is the storyguide's to say.

Every few seconds your pages pick up what others saved, with a note at the window's foot. When your storyguide advances the season, your window turns the season's dial too. If someone else has the record you're on open, their name shows beside the trail, such as "◉ Bruno is also viewing", so you can agree who changes what. A storyguide is marked as "Bruno (storyguide)".

If the host made you a **storyguide**, you see the whole saga and may do all a [storyguide in troupe-style play](help:remote-seats-players) may, Advance Season included. If another storyguide advanced first, your window shows the saga as it now is, so look before advancing again. Who may join, and as what, stays the host's, and Saga Management says so. When the host changes your role, your window follows within seconds and says so.

### What a host can and can't see or do
<!-- help: what-a-host-sees; gui -->

- **Your saga, as you may see it, is all you receive.** Secrets you haven't been told, places and people you don't know of, and other things your storyguide keeps to themselves never leave their computer.
- **Nothing is stored on your computer** but this device's seat, kept in your computer's own keychain: Windows Credential Manager, macOS Keychain or a Linux Secret Service. The saga stays in memory while it's open and is gone when you close it.
- **Your passcode never crosses the internet.** Signing in, your app proves it knows it in a way that's useless to anyone who overhears, and to anyone pretending to be the host. When you change it, only the new one's scrambled form is sent, inside the encrypted connection. That's the form the host keeps, from which the passcode can't be read back.
- **The six words are your check that you reached your storyguide**, not someone in the middle. Compare all six on your call each time you join from a new invite.
- **What your storyguide's computer sees:** your internet address, as any website does, when you play, and the changes you make. Each change is recorded in their log by which record it touched, never what you typed. Their tunnel company sees that you connected, not what passed.
- **What it can't do:** reach anything on your computer. The app takes only saga records from it and runs nothing it sends. Every record is checked against the form the app's records have before it's used. Anything else is refused, and the app names the field it couldn't read.

### What keeps you safe
<!-- help: join-game-safety; gui -->

In plain words, what happens when you join and play:

- **The handshake.** Before anything else, your app and your storyguide's set up a private, encrypted connection of their own, inside the one the tunnel carries. Nobody on the way, such as your network, the internet or the tunnel company, can read it or change a word of it unnoticed. A changed message ends the connection. Each connection has fresh keys, so a recording of an old one is no use later.
- **The pin.** Your Invite carries a fingerprint of your storyguide's computer, its pin. Your app checks the host it reaches against that pin before it sends anything at all, and stops if they differ. The six words are the same pin, made easy to read aloud. Matching them on the call proves nobody swapped the Invite on its way to you.
- **Your device's seat.** Once your storyguide approves your device, it gets a key of its own, kept in your computer's keychain. It works only with your passcode, only for this saga, and your storyguide can end it at any time. Leave Saga ends it from your side.
- **The limits.** A wrong passcode slows your device down, so nobody can guess it quickly. Three tries are free, then the waits grow, and nobody else's device can lock you out. Your storyguide's computer closes a connection that floods it or sends what it doesn't understand, and turns away too many connections at once.
- **If something looks wrong**, such as six words that don't match, a passcode you know being refused, or a seat ended that you didn't leave, stop. Ask your storyguide on your call before trying again.

**See also:** [How to host a saga](help:guide-hosting)
