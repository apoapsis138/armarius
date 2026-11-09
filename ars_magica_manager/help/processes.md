# Plan Season
<!-- help: plan-season -->

Plans what a magus, companion or Mythic Companion does with a season: the current one, or one up to a year ahead. Nothing changes when you save: the plan is applied when the saga is advanced
<!-- tui -->
with `t`.
<!-- /tui -->
<!-- gui -->
with **Advance Season**, under the chapters on the left.
<!-- /gui -->
Grogs aren't planned season by season; they have a [yearly update](help:grog-year) instead.

**You type:** the **Season** (the one it was opened for; choose another of the year ahead to move the plan there), the Activity, chosen from a list you can filter by Type and Book (see [Choosing the activity](help:plan-season-activity)), then the fields that activity needs (what the experience goes into, a book, a teacher, a Source Quality, a die roll), months lost to distractions, Notes, and **For**: this season only, until the work is done, or a number of seasons (see [For several seasons](help:plan-season-repeat)).

**The app works out:** what the season will give, from the character and the saga as they stand now, shown on the line above Save as you fill the form in. For a season ahead it is worked out from the character as the seasons planned before it will leave them, as the [Seasons Ahead](help:section-char-ahead) are, with a die not rolled yet counted as nothing gained. A season that already has a plan can't be chosen for another one: change that plan, or clear it first.

### For several seasons
<!-- help: plan-season-repeat -->

**For** plans the same activity for the seasons after this one too, straight after it, stopping at the first season that already has a plan:

- **This season**: only this one. Changing one season of a longer plan this way keeps the seasons planned after it.
- **Until it's done**: as many seasons as the work needs, as things stand now: reading a summa until the reader's score reaches its Level, writing a summa, or copying or translating a book until it is finished (lab work that takes several seasons is always planned this way, from the laboratory's Planning tab). The line above Save says how many seasons that is. Each season of it is worked out again after it is played: one interrupted, or one that gave less than expected, adds a season at the end; one that finishes the work early clears the seasons no longer needed. If the season after the last is already planned, the last season says the work needs more, and Seasons Ahead shows "(needs more seasons)". At most ten years are planned at once.
- **2 seasons** to **4 seasons**: the plan repeated that many times, for any activity (practice, exposure, a companion's working seasons). These aren't worked out again.

Choosing For again on a season of a longer plan replaces the seasons planned after it. Clearing the first season asks whether to clear the later ones too.

What each later season gives is worked out from the character as the seasons before it will leave them, as for any season ahead. See [Interruptions](help:advance-interrupted) for how a season is marked interrupted.

### Paired plans
<!-- help: plan-season-pairs -->

Some seasons take another person's season too, and saving one plans the other for the same season:

- **Be taught** plans the teacher's **Teach** (Exposure in Teaching). A teacher already teaching that season is left as they are, so two students can share one.
- **Be trained** plans the master's season working at the Ability (Exposure in it, with "Training (name)" in its Notes). A master who already has a plan keeps it: training doesn't need the master's season.
- **Teach** with a **Student** and **Teaching them** plans the student's **Be taught** from the teacher.
- Lab work naming an **Assistant** plans the helper's **Assist in a laboratory**, for each season of the work.

If the other person already has a different plan that season, Save is refused with the reason, so nothing is replaced without asking: change or clear that plan first. The line above Save says whose season will be planned too. Changing the plan to another activity clears the season it made.

Clearing either side clears both, after one question that names both people. A Teach another student still needs stays, and clearing an assistant's season only takes them off the lab work.

### Where it's opened from
<!-- help: plan-season-where -->

<!-- tui -->
- A character's **Planning** tab: the This Season section. `a` or `e` plans the season (or changes the plan), and `d` clears it after a confirmation.
- The same tab's [Seasons Ahead](help:section-char-ahead): highlight a season and press `e` to plan it (or change its plan), `a` to plan the first free one, or `d` to clear one.
- A covenant's **Seasons** tab: highlight someone in the Magi or Companions list and press `a` or `e` to plan, or `d` to clear the plan.
<!-- /tui -->
<!-- gui -->
- A character's **Planning** chapter: the This Season section. **Plan** plans the season; once it is planned, **Edit** changes the plan and **Clear** clears it after a confirmation.
- The same chapter's [Seasons Ahead](help:section-char-ahead): click a season, then **Edit** to plan it (or change its plan) or **Clear** to clear it; **Plan** plans the first free one.
- A covenant's **Seasons** chapter: click someone in the Magi or Companions list, then **Plan** to plan their season (or change the plan), or **Clear** to clear it.
<!-- /gui -->

A magus's laboratory work (inventing spells, enchanting, extracting vis, a Longevity Ritual, binding a familiar, setting up or refining a laboratory) is planned on the laboratory's [Planning list](help:tab-lab-planning), not here. See also [inventing a spell](help:invent-spell). A character's This Season names the laboratory when their season is lab work.

### Choosing the activity
<!-- help: plan-season-activity -->

<!-- tui -->
Press Enter on **Activity** to open the list of activities this character may plan. It is grouped by Type, what the season is for:
<!-- /tui -->
<!-- gui -->
Click **Activity** to open the list of activities this character may plan. It is grouped by Type, what the season is for:
<!-- /gui -->
Study; Writing & books; Work & trade; Teaching & apprentices; Faith; Order & covenant; Mysteries; Adventure & travel; Rest & other; and Tradition, a hedge tradition's own seasons, shown to its members only.

- **Type** above the list shows one group only.
<!-- tui -->
  F2 steps through the Types, and back to all of them.
<!-- /tui -->
- **Book** shows the activities of one sourcebook, or of the core rules.
- **Search**: type any part of an activity's name or summary.
- **Recent**: the character's last three activities, from their plans and Diary, head the list until a Type or Book is chosen or a search typed.
<!-- tui -->
- F3 also lists the activities of sourcebooks not in play in this saga, marked; they can't be planned until the book is in play (Saga Content).
<!-- /tui -->
<!-- gui -->
- **Show everything** also lists the activities of sourcebooks not in play in this saga, marked; they can't be planned until the book is in play (Saga Content).
<!-- /gui -->

The highlighted activity's summary, Type, sourcebook and rule are shown beside the list; the list itself shows only names. Choosing one closes the list and the form shows the fields it needs.

### Activities offered
<!-- help: plan-season-activities -->

The Activity list offers what this character may do. Activities marked "magi" are offered to magi only.

- **Study and experience:** Work / Exposure, Practice, Read a book, Be taught, Teach, Be trained, Study from vis (magi) and Adventure.
- **Books:** Write a summa, Write a tractatus (on an Art, an Ability or a spell's Mastery, DE p. 379; at most half the Ability or a fifth of the Art, rounded up, of the author's own originals: copies and translations of them don't count), Copy a book (a book on the Arts or Parma Magica needs Magic Theory 1, one on a Supernatural Ability that Ability or a Realm Lore at 1, or the copy is corrupt, DE p. 381), Translate a book, Copy Lab Texts (or Casting Tablets), Edit a florilegium (binds the tractatus on one subject you can get at, as many as you could write on it, from a collection twice that size: +1 Quality each, +2 for an authority -- Ability 10 or Art 35 -- from one five times the size; Ability 6 or Art 20 to edit at all), Write Casting Tablets (magi: of a spell they have mastered, Latin x 20 levels a season, as many tablets as that holds), Rewrite Lab Texts for general use (magi) and Teach Lab Text abbreviations (magi).
- **Apprentices and research (magi):** Search for an apprentice, Open an apprentice's Arts, Teach a Hermetic Virtue (with the teacher's teaching Virtues, such as Good Teacher; **With a Hermetic Flaw** of his own adds +3 for a Minor Flaw or +9 for a Major, and the student gains the Flaw too, DE p. 271) and Seek an insight. Opening the Arts of a child with Supernatural Abilities needs the master's Intellego Vim Lab Total, in his laboratory, to reach 5 x each Ability (at least 10 for a Minor Virtue's, 30 for a Major's; 10 or 30 for a power with no Ability), all added together. Reaching it, the Abilities and their Virtues are lost when the season is applied. Only at double it or more may the master choose to keep them (**Keep Supernatural Abilities**) or convert them (**Or convert them into**, and up to two more: one of his own Hermetic Virtues for each Ability, of its own size, Major for a Major and Minor for a Minor, checked when the season is played; those not converted are lost; a similar Virtue he lacks is the troupe's call, added by hand) (DE p. 271). When the season is applied the magus claims the child as his apprentice (DE p. 270): the Apprentice Social Status is added, and his Parens and House are set to the master's, so The Gauntlet can follow. A successful **Search for an apprentice** adds the Gifted child to the saga as a character at the magus's covenant, seven years old and In Creation, for you to name and build (DE p. 269). An inborn Ex Miscellanea tradition Virtue needs no Lab Total (DE p. 270): leave it out of the child's Virtues until the Arts are open.
- **The free House Virtue** (DE p. 272): in Houses Bonisagus, Guernicus, Mercere, Tremere, Flambeau, Jerbiton and Tytalus an apprentice takes on his parens's House Virtue after 10 seasons of one-to-one work with him. An apprentice is a character not yet a magus whose Parens (Hermetic Background) names a magus of the saga. Each season counts once when it is applied: being taught an Art or an Arcane Ability by the parens, learning spells from him, assisting in his laboratory, or the parens opening his Arts or teaching him a Hermetic Virtue. At the tenth the Virtue is added, when the parens has just one of the House's, with a Diary entry; when he has both of a House's choices (Puissant Perdo and Ignem), or for Jerbiton, the Diary says to add the one he chooses on the Virtues tab. The Mystery Cult Houses Initiate their Virtue instead, and an Ex Miscellanea apprentice's package is the troupe's to decide.
- **Assist in a laboratory:** helping a magus with the lab work they have planned.
- **Set up a new laboratory (magi):** for a magus with no laboratory yet, under Order & covenant. **Laboratory's name** names it (blank: "(name)'s laboratory"). It needs Magic Theory 3 and a covenant: when the season is applied the laboratory is made in the magus's covenant, theirs, with the Basic Flaw (-3 General Quality), and Advance Season asks whether they would like to spend the next season finishing it (see [A new laboratory](help:advance-new-lab)). Exposure in Magic Theory.
- **Take over the laboratory (magi; Covenants):** under Order & covenant, for a laboratory with no owner, chosen in **Laboratory** (those in the magus's covenant first). It is lab work in that laboratory, rolled like refining: when the season is applied the laboratory becomes the magus's (any laboratory they had is left without an owner), its Refinement drops to at most their Magic Theory - 3, and a Perception + Magic Theory roll against 3 x the old Refinement decides whether the Predecessor's arrangements remain (Covenants, Chapter Nine: Laboratories, Taking Over a Laboratory). A laboratory with an owner can't be chosen. Exposure in Magic Theory.
- **A hedge tradition's seasons (its members only):** Open a student's Gift to a tradition, and the tradition's own work (Refining, brewing a potion or making a fetish, binding a familiar, inventing a gruagach spell or enchanting a tattoo, inventing a charm or making an amulet, inventing rune scripts). Opening needs a Gifted master Opened to the tradition and a Gifted **Student**: the master's Opening Total is set against twice the student's Supernatural Abilities and Arts (+12 if his Gift was Opened before); with none it always works, up to twice that the student is Opened but loses his old powers (noted in the Diary, for you to remove), and beyond it he keeps them (Hedge Magic Revised Edition p. 8). An Amazon needs twice the Ease Factor to Open her apprentice and four times to keep her powers, and the Arts of any other tradition are always lost (Rival Magic p. 30); between twice and four times the app has her powers lost, as Rival Magic's own band reads, not the general rule's "more than twice keeps". Opening a Hermetic apprentice's Arts when a non-Hermetic tradition already Opened the Gift needs 30 more on the Intellego Vim Lab Total (Rival Magic p. 6). A hedge Initiation's Ease Factor rises by 3 for a Minor Virtue, 9 for a Major, when the Mystagogue doesn't have the power (Hedge Magic Revised Edition p. 13). Plan it as Undergo an Initiation with the Hedge Script chosen; tick Mystagogue knows the power when he has it as an Ability rather than a Virtue. An unGifted Initiate needs an Ordeal and gains nothing from past Ordeals, and an unGifted Mystagogue must know the power (p. 14). When the season is applied the student joins the tradition with its Arts at 0, the Virtues the Opening gives, and, where the master is below 2 in one of its Arts, the tradition's Flaw for it (the vitkir's Minor Magical Deficiency; for the others the Diary names the Arts and the troupe picks the Flaws). A tradition's own work gives Exposure in the Art or Ability chosen in **Experience in**, and the Diary notes its Lab Total; it counts as a companion's working season. The tradition's Arts can't be practised where its book says so (the gruagachan, learned magicians, elementalists and vitkir). See [A tradition's Seasons](help:tradition-seasons).
- **Undergo an Initiation:** the Initiate's season of a Mystery Initiation. **Teacher / master** is the Mystagogue (none for a self-initiation); give the Mystagogue's Lore and the Script bonus (every component, the Ordeal's +3, +6 or +9 included), and any variation of the Script. **Virtue initiated** opens
<!-- tui -->
the Virtues & Flaws picker, which asks for anything the entry names (an Affinity's Art); Delete clears a choice.
<!-- /tui -->
<!-- gui -->
a list of Virtues to choose from, which asks for anything the entry names (an Affinity's Art); **Clear** beside it clears a choice.
<!-- /gui -->
**Ordeal** says what the Ordeal costs, if anything: a Flaw gained (chosen in the picker), one of the Initiate's Minor or Major Virtues lost, or one of their Minor Flaws raised to a related Major Flaw. Its size follows: a Minor Flaw or Virtue is a Minor Ordeal, a Major one a Major Ordeal, a raised Flaw a Medium one. The Initiation succeeds when the Mystagogue's Presence + Lore + Script bonus reaches 15 for a Minor Virtue or 21 for a Major (18 or 30 when the Mystagogue lacks it), less the largest reduction among the Initiate's past Ordeals; the Initiate needs the Lore at 1 unless it is their own House's. A Mystery Cult of the saga's own (Saga Content's [Mystery Cults tab](help:tab-content-cults)) offers its degrees' Scripts here too. The Mystagogue must have its Lore (at 1 or more), and the Initiate needs its Lore at 1; a second or later Initiation (counted by the cult's Virtues he holds) typically needs 3, and the season warns when he has less, but lets the troupe go ahead (TMRE pp. 11, 13). See [How to initiate a character into a Mystery](help:guide-initiation).
- **Hermetic Viresculture (Legends of Hermes pp. 72-76):** in Work & trade, for a magus with the Ability. **Vitalize a Stirps**: name the creature or plant and type its Magic Might (for Lesser Enchantment Vis, its effect's level). The Vitalization Total is Intelligence + Creo + Vim + Hermetic Viresculture + the aura: the magus's laboratory's Creo Vim Lab Total with Viresculture in place of Magic Theory. Each season adds what the Total exceeds the Might by, until the points reach the Might; it costs a pawn of Vim vis per ten levels (or fraction), paid with its first season from the raw vis **Vis from** names (the magus's own, the laboratory's or the covenant's stores; the season won't plan without it, nor with more than twice Magic Theory). **Other Stirpes** ("Name: Might; Name: Might") works on several in the one season, under Multiple Laboratory Activities (DE p. 264; Legends of Hermes p. 75): Vitalizing, the Total is set against their Levels together and must finish them all that season (at least twice the sum), each paying its own Vim; Invigorating, they share the Invigoration Total, rounded up (43 for two roosters gives each 22), and are all of the one Form. A Might of 0 is allowed. Until it is Invigorated a Stirps' young are ordinary, and its vis may be transferred out without harm, though it is then no longer a Stirps. **Invigorate a Stirps**: also choose its Form. The Invigoration Total is Intelligence + Creo + the Form + Viresculture + the aura, Vim being the Form's requisite (the lower of the two counts, DE p. 312). It gives a breeding season per ten points or fraction, each yielding a fifth of the Might (rounded up) in pawns of the Form, one in ten of them a new, uninvigorated Stirps. An Invigorated Stirps with breeding seasons left breeds once a year (as it does without magic), in its breeding season: the spring for animals, the autumn for plants (Herbam) (Legends of Hermes p. 75). A magus oversees no more Stirpes than his Viresculture score; those past it don't breed, and the Diary says so. Its pawns go into the magus's own raw vis, the new Stirpes among them are rolled and said, and a Diary entry and the season's record note it. Its care is taken as given; take a pawn off by hand for care short or months unattended. The magus tends at most his Viresculture score in Stirpes; each needs 12 Labor Points a year, and the yield is a pawn less for every 6 Labor Points short and for each month left unattended. With the Aura Variation rules, a year's harvest takes a fifth of its pawns (rounded up) off the aura's yearly modifier.
- **The Lesser Elixir (The Mysteries Revised Edition pp. 42-43):** in Mysteries, for a magus with the Virtue (it needs Hermetic Alchemy). **Reinvent the Lesser Elixir** names the special ingredient added and its Shape and Material bonus; tick **He devised it himself** for one found by Vulgar Alchemy (its points are doubled). No ingredient counts above Magic Theory. The Elixir Points of all his ingredients give the Elixir Level as an Art's experience gives its score (1, 3, 6, 10, 15...), at most his Magic Theory as he devises it. The season prepares a dose of his own Longevity Ritual from its Lab Text (at hand, and readable), a pawn of **The dose's vis** (Creo, Corpus or Vim) for every five years of his age, from the raw vis **Vis from** names, and no more of it than his score in that Art, as a dose rebrewed from the Lab Text (DE p. 261; p. 42); he needs a Longevity Ritual in force. From then on his aging rolls subtract the Elixir Level as well as the ritual's modifier, until an Aging Crisis ends the ritual. Performing his own ritual again from its Lab Text, or making a new one himself, adds the ingredients again; a ritual someone else makes for him leaves the Elixir out.
- **Copy books by magic (Transforming Mythic Europe pp. 98-103):** in Writing & books, for a magus, while Transforming Mythic Europe is in play. He casts The First Furrow Guides the Second and The Copyist's Puissant Quill page after page through the season (he must know both), copying the **Book copied** (a summa, tractatus or Lab Text he can get at) as many **Copies** as the plan says (TME gives no rate for casting them page by page). Or choose a **Copying device** he, his covenant or one of its laboratories holds with The First Furrow Guides the Second instilled (as the Superb Scrinium, pp. 101-103): he then needs not the spells, but each text takes a use of that effect (and of the device's Binding the Mundane Codex, if it binds them), so its uses a day cap the copies: 3 a day is 3 books a day, 273 in a season (p. 102). His Finesse Total still sets the Quality. Magic neither reads nor understands, so he needs no language, Magic Theory or Realm Lore to copy it uncorrupted (p. 98). His Finesse Total (Perception + Finesse, with the Wound, Fatigue and Clumsy or Inconstant Magic penalties; TME says Intelligence, but the Definitive Edition's Rego craft roll is Perception, p. 307) is read on the book's table (p. 100): + 3 for a book of Quality 6 or less (the Quill's Ease Factor 9), - 3 for Quality 10 or more (15); 11 or more keeps the Quality, 9 loses 2, 7 loses 4, 5 loses 6, and less makes no readable book, which stops the plan. The Diary also says how long a mundane scribe would take: four pages a day, and as long again to tidy and illuminate them (p. 101). A copy made by magic loses the original's resonant materials and clarification (p. 101) and is loose sheets (**Unbound**) unless he ticks **Bind them with Binding the Mundane Codex**: he needs that spell (or the device's own) and a Finesse Total of 6, and a book so bound has the sound binding's +1 under the extended Quality rule (p. 103). A Lab Text is copied exactly, in its author's code if raw; it must be copied flawlessly: a Finesse Total of 11 copies up to 120 levels (a month's scribing), 14 up to 360 (a season's), 17 up to 1,440 (a year's: the Definitive Edition's +3 from a season's work to a year's, p. 307) (p. 103). Past 1,440 levels no book gives a figure, and the Diary says the troupe decides. Below that, the Diary warns that a botched page may have corrupted a copy, found only when it is used. The season gives Exposure, 2 xp, in the Ability chosen.
- **Shape the land (Transforming Mythic Europe pp. 54-77):** a magus casts the Rituals of one of his covenant's land projects, in order, as far as the vis goes: each takes a pawn a magnitude, of its Form first and then its Technique, at most his score in each Art (DE p. 213), from his own vis, his laboratory's or the covenant's. Each is rolled as a Ritual (Casting Score + Artes Liberales + Philosophiae + stress die, in the covenant's aura); the long-term Fatigue comes back with a night's sleep, so the season goes on to the next. A botch or a failure spends that Ritual's vis and ends the season's casting. Each Ritual cast is a point of the magus's progress toward the project. Exposure 2 xp. See [Shape the Land](help:land-shaping).
- **Activities from the supplements**, such as Study a significato, Library research or Act as Mystagogue. Library research shows the roll's total before the die: Intelligence + the Ability + the better of the covenant library's research bonus for it and its best encyclopedia's.
- **Learn to measure the fixed stars** (Ancient Magic, a magus): a season learning Ptolemy's measure of the array of fixed stars, the first stage of his coordinates; no experience. The app records it and won't plan it twice. The second stage, calibrating the system at its origin on the Zero Longitude in the Purple Islands, is a journey for the troupe; after both, a stellar observation (Intelligence + Artes Liberales against 15, four hours of clear stars, two with a supernaturally accurate timepiece, plus the calculations) gives the coordinates of where the magus stands, an Arcane Connection that never fades (Ancient Magic pp. 89-91; Errata p. 58).
- **Faith:** Good Works, Follow a preacher, Pilgrimage and Visitation, petition or penance are open to magi as well as companions. Good Works is for any Christian (a cleric's may be a working season; The Church p. 27), following a preacher is any character's free season (p. 130), and anyone may go on pilgrimage or do penance (pp. 12, 16; grogs may make a pilgrimage too, but the app plans no seasons for grogs); More's [Pilgrimage](help:pilgrimage-more) on This Season records a pilgrimage's Oppositional Elements, a grog's too, and claims its aim. Care of Souls stays a priest's (p. 28). Personal devotion is a season of prayer and meditation at a saint's shrine: name the saint, and it earns 5 Devotion Points toward him, beginning a Devotion if he has none, with only exposure experience, in Church Lore or Dominion Lore (The Church p. 14). A contemplative mystic's Spiritual path seasons each count toward the Revelation the plan names (begun with More's Spiritual Path): service to the poor or the Church +1; devotion +1, with a Devotion Point toward the saint the plan's details name, or his patron, and exposure only in Dominion Lore; preaching the Gospel +3, once on a path; a mission to heretics, pagans or infidels at the risk of martyrdom +9 (The Church p. 22). Ordination is a season's examination for the next grade of holy orders (The Church p. 33): Source Quality 2 in Church Lore or Civil and Canon Law (choose which); choose the grade sought, who examines him, whether he is ordained outside his birth diocese, whether he swaps his Social Status for the grade's (ticked: one status only, The Church pp. 25, 34; DE p. 63), and the die if it is rolled at the table. The plan shows the examination and what each result brings; the season ordains him, or not, on the [Religion tab](help:tab-religion). A barred cleric (a botched examination) can't plan one until a petition lets him.
- **Build the Great Tower** (Hermetic Projects pp. 36-38): a master mason's season on the project he is master mason of. Build new levels (his effective Craft: Mason / 5 a season, of his Workshop Total's quality), repair a damage level, or rebuild a shoddy section as standard. Kept in the project's Works on the [Projects tab](help:tab-cov-projects); Exposure in Craft: Mason. A grog mason, who has no season plans, has his seasons added by hand on Works.
- **Search for a lacuna:** Intelligence + the chosen Area Lore + a stress die against 9 (Houses of Hermes: Societates p. 57). The first success finds the city's obvious lacunae, recorded as 'Lacunae of <city>'; he then knows three small lacunae per level of that Area Lore, which the player names with the troupe. Seasons searching there after it are Area Lore practice, and the Area Lore's specialty may become lacunae. A character raised in the area by a magus knows them already and needs no search. A lacuna that gives more than a place to cast, not bought at creation nor won in a story, carries a limitation (unavailable by day, inhabitants to placate, overuse risking exposure, an Infernal aura). [Cast in a Lacuna](help:cast-in-lacuna) works out a spell cast from one.
- **Set points:** Useful correspondence's 1 xp, and the 1 xp in Organization Lore: Order of Hermes for each book read from a folio, are set points (Covenants p. 90; Houses of Hermes: True Lineages p. 23): no Affinity, Savantism or wound halves or multiplies them, and Master of None and Secondary Insight ignore them. **Study a realia collection** is for one outside the library, such as an exhibit at Tablinum; one the covenant owns is a book of the Realia kind (see [Books](help:section-lib-books)). **Study another artist's work**: Source Quality is half the work's Aesthetic Quality, and each work is studied once, like a tractatus (Art & Academe p. 126, with Atlas Games' errata).

**Create a work of art** (Art & Academe pp. 123-135). Its Aesthetic
Quality is Dexterity + Craft (Communication + Profession for a
performance, or Craft: Poetry), + Puissant, + 3 for Free Expression and
3 for Inspirational, + the season form's choices: twice the time +1;
overtime +1 and an Aging roll when it is done; a liberal art used, +
Artes Liberales / 3; a muse's sacrificed Might, +1 per 5; Life-Linked
Art's wound, +1, +3 or +6; a maestro or legendary artist in an aura of
the realm his nature is aligned with, + aura / 5 rounded up (never the
aura itself, and nothing for any other artist: Grifo's mural in his
church's Divine aura 3 comes to 19, where the book's example on p. 134
leaves the +1 out); Hermetic Inclination's Form Bonus; Artist Reputation 10, +3; half
the time, the Quality halved. The kind of piece sets its base time (a
season, two small pieces in a season, a year, a castle or church a year
per Size point, a cathedral ten years per Size point), times the
Quality / 10 rounded up; assistants, no more than his Leadership, take
3.5 days, a week or a month off each, to no less than half; Prolific
Artist takes a quarter off and allows no assistants. Each season whose
piece is over three times his Artist Reputation is 1 xp in it.
Experimenting adds a simple die / 2 (rounded up) to the Aesthetic
Quality and then at once rolls a stress die on the Artist
Experimentation Results (p. 124): the two are rolled together, in the
season the piece is finished. The book gives no season for a piece of
several; rolling them in the finishing one is the app's choice, since a
plan keeps nothing from one season to the next. A disaster or a ruined
piece loses the work (and a whole Reputation point, or Reputation xp
equal to the piece's presumed Aesthetic Quality, p. 126), a disparaged one loses a Quality point and a whole
Reputation point, a praised piece gives xp equal to its Quality, a
praised artist a whole Reputation level. A finished piece is an Arcane
Connection to him for half the time it took, a week less for each
assistant (none for a castle, church or cathedral). A maestro with
Hermetic Inclination may instill a Personal, constant effect of his
Form as he works: Dexterity + Craft + the Form + the aura's realm
interaction, the points over the effect's level each season, until they
reach it, and a Fatigue level per 10 levels lost while he works.

**Edit a lecture commentary** (p. 102): a season rewriting a commentary
of his own lectures adds 1 Quality and his writing Virtues (Good
Teacher), once. Every second commentary of a teacher's lectures earns
him an Academic Reputation xp (p. 103).

**Seek a teaching or clerkly post** (p. 89): a season looking, then
Presence + the post's Ability + his highest Good Academic Reputation -
his highest Bad one + 1 for a Minor Social Status Virtue or Educated,
Privileged Upbringing, Famous or Wealthy (3 for a Major Social Status
Virtue) + a stress die: 12 a secular jurist or copyist, 15 a municipal,
royal court or monastic teacher (a monk), 18 a cathedral school teacher
or a magister's or doctor's chair (the licence). A failure wastes the
season; a botch also costs a Medium Wound or a Bad Reputation. A post
won is an Academic Reputation xp; a cathedral teacher's students are a
simple die for each point of his Presence + Good Academic Reputation,
and he teaches five times his Teaching.

**Translating** (p. 87) now needs Artes Liberales 2 (1 between
languages of one alphabet), and a translator with both languages at 6
loses one Quality point less.

- **Research a formula** (Art & Academe p. 70): A formula is a recipe for an
  astrological inception (Artes Liberales), an alchemical reagent
  (Philosophiae) or a pharmaceutical theriac (Medicine): choose that Ability
  as the subject. Five xp make it, and a season's research gives five; they go
  into the formula, not the Ability. Type its level if you know it: its
  guideline's base raised by magnitudes as a spell's (5 levels each, 1 below
  5) for its Detail (an inception: Binary to Thorough, +1 for the past or the
  far future, +2 the near future), its Alteration (a reagent: Slight to Major,
  + size) or its Potency (a theriac: Weak to Mighty).
- **Produce reagents, theriacs or inceptions** (pp. 70-71): Choose a formula
  he knows. His Lab Total is Intelligence + its Ability (+1 for a matching
  specialty) + Philosophic Bonuses (Shape and Material, an experiment's Risk
  Modifier, the laboratory's), the bonuses no more than the Ability. It must
  reach the formula's level. The first time, each season gathers Lab Total -
  level points; at points equal to the level it is done, a dose is made and
  its Laboratory Text written (twice the level does it in a season). With the
  Laboratory Text, a season makes Lab Total / 5 doses (rounded up; fewer if
  Doses says so). The doses go into his Personal Gear. A reagent's or
  theriac's ingredients cost 1 Labor Point per 5 levels times the doses: from
  his own store if he has Profession: Apothecary, otherwise from the store
  of the best apothecary at his covenant, whose Labor Points they come off
  when the season is applied (with no apothecary there, take them off by
  hand). An inception costs none.
- To use an inception, cast the target's nativity once (a day: Intelligence +
  Artes Liberales + a die against 9), then a minute per level gives the
  answer.

- **Make a wondrous item:** the Workshop Total adds the aura's modifier: the aura where the craftsman works (enter it, and its realm, in **Aura where he works**; blank counts none), by the Realm Interaction table for the realm his Touched by (Realm) names (Faerie in a Magic aura adds half, Divine nothing; City & Guild p. 72, DE pp. 410-411). The Virtue must name Magic, Faerie, Divine or Infernal (p. 71), or the season says so. Choose the one assistant in the Teacher / master field: half their Craft is added (City & Guild p. 72); count no other help in Other. A Mythic Farrier (Grogs p. 76) makes wondrous horseshoes the same way, with Intelligence or Dexterity + Craft: Farrier, in one Form, their power on the horse or the ground it treads; name his realm on the Virtue (most likely Magic or Faerie, Infernal possible).
- **Exertion, a (Craft) Reputation and a laborer's working season** (City & Guild pp. 73-76), in a workshop production, excellent item or wondrous item season. **Exertion** adds a simple die to the Workshop Total, rolls a stress die on the exertion table, and makes an Aging roll whatever his age; under 35 the Aging roll takes a simple die for its stress die and a 13 brings no Crisis (DE p. 392). The table: a botch is a disaster; 4-5 disappointing ramifications; 6-7 no benefit (the simple die isn't added); 8 a story event; 9 invention, a simple die of Labor Points put toward Innovation (shown on This Season and spent by the next Innovation raised); 10-11 a simple die of experience in his (Craft) Reputation; 12+ a simple die of experience in the Craft. A **(Craft) Reputation** (p. 74) is named for the trade (Craft: Smith's is "Smith"), starts at 0 and rises as an Ability: a season whose Workshop Total is 6 or more over the standard goods' Craft Level (6) earns 1 experience, a wondrous item's season included, and the season a wondrous item is finished earns 1 more on top; a season of shoddy goods straight after another takes 1 off, and below 0 he gains a Reputation as a bad craftsman ("Shoddy Smith"), scored like any Reputation, the "bad" being in its name (DE p. 386). A **laborer's working season** (p. 76) with a Profession sets his Labor Total, his primary Characteristic + Profession, against the Profession Level: the Characteristic is the one the season names, Strength if it names none (p. 67), while his Labor Points stay Communication + Profession (p. 38). The Profession Level is 6, raised by 1 where he lives in an Infernal, Faerie or Magic aura, as a Craft Level is (p. 69; not a Divine one). It gives shoddy, standard (at the level) or superior (6 over it) service, never excellent, and his (Profession) Reputation follows the same rules.
- **Other:** anything else. It is written in the Diary with your notes, and no experience is worked out for it; say in Notes what the season is spent on.

The rules are those of Ars Magica Definitive Edition, Chapter 10: Long-Term Events (Exposure, Practice, Adventure, Books, Teaching, Training, Vis and Distractions); each activity's rule is cited under the plan in the character's This Season.

### Where the experience goes
<!-- help: plan-season-experience -->

**Experience in** chooses the Ability, Art or spell Mastery the season's experience goes into. For Teach, it is Teaching or the language used. Some activities split it:

- **Work / Exposure** can give 1 xp in each of two subjects instead of 2 in one.
- **Adventure** can split the storyguide's Source Quality (5 to 10) among up to three subjects, at most 5 to each; give each one's share in Source Quality to (n).

**Source Quality** is asked for Practice (leave it blank for 4, or 5 for a spell's Mastery), Adventure and some supplement activities. **Book** offers the covenant's library and the character's own books. **Teacher / master** lists the other characters: saving Be taught or Be trained plans their season too (see [Paired plans](help:plan-season-pairs)).

**The Art is present** (Read a book, Study from vis; a character with Study Bonus or Study Requirement): the Art is studied beside its substance, a fire for Ignem or a pond for Aquam. **Secondary Insight** (Read a book, Be taught, Study from vis; a character with the Virtue): choose the Book or **Experience in** first, then open it to tick the Arts that gain 1 xp: up to 4 Forms when the season studies a Technique, up to 2 Techniques when it studies a Form, each shown with its score. With none ticked (or Clear), the lowest-scored are chosen. See [Virtues and Flaws the app applies](help:guide-advancement-virtues).

**Stress die (blank: rolled)**: for activities that roll, leave it blank and the app rolls the die when the season is applied, or type a roll made at the table. **Months lost (0-3)**: each full month lost to distractions cuts the total by a third.

### The line above Save
<!-- help: plan-season-preview -->

As you fill the form in, the line above Save shows what the season will give: for each subject, the Advancement Total, the xp gained and how the score and xp change, for example "Latin: Advancement Total 4, +4 xp (score 3, 34 -> 38 xp)". For book work it shows the progress or the book made.

If the plan breaks a rule (a book the character can't read, a teacher whose score is too low), the line shows the problem and Save refuses the plan until it is fixed. Experience a Virtue shares with another subject says so, for example "Auram: +1 xp from Secondary Insight". For a companion, it also reminds you when the plan leaves too few seasons that year for their working seasons (two, one with Wealthy, three if Poor); this is a reminder, not a block.

**See also:** [Advance Season](help:advance-season), [Grog's Yearly Update](help:grog-year), [Laboratory Planning tab](help:tab-lab-planning), [How to plan and run a season](help:guide-seasons), [How the app handles advancement](help:guide-advancement)

# Grog's Yearly Update
<!-- help: grog-year -->

Grogs aren't planned season by season. Instead the app gives each grog a yearly update, applied when Winter is advanced, following Grogs, Chapter 5: Updating Grogs. This dialog sets up that update.

<!-- tui -->
Open it from the grog's **Planning** tab (`e`), or from the Grogs list on a covenant's **Seasons** tab.
<!-- /tui -->
<!-- gui -->
Open it with **Yearly Update** in the grog's **Planning** chapter, or by clicking the grog in the Grogs list of a covenant's **Seasons** chapter and choosing **Plan**.
<!-- /gui -->

**You type:**

- **Vocational training**: the Ability trained, usually Single Weapon from the drill sergeant, and **Vocational xp** (7, or the teacher's Source Quality if you know it).
- **Practice (4 xp)**: one Ability practised.
- **Exposure (2 xp)** and a second **Exposure (2 xp)**.
- **Story awards this year**: how many stories the grog took part in. [Story Experience](help:grog-story-xp) counts each one for you; change the number here only to correct it.

**The app works out:** the xp each Ability gains. Each story award takes one season of the year, in this order: the first exposure, the vocational training, the practice, then the second exposure. The grog's This Season shows what the update will give.

A grog may also plan a season of copying: see [Plan Copying](help:grog-copying).

In Winter the xp is added, a "Yearly update" entry is written in the grog's Diary and in the season's record, and the story awards go back to 0 for the next year. A grog with no Ability chosen here gets the saga's default instead (2 xp of Exposure a season in their highest Ability), less a season of the Grogs year for each story award, in Grogs p. 67's order: the first exposure's 2 xp, then the vocational 7, the practice 4 and the second exposure 2.

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

**You type:** the story's name, and up to three Abilities the story used with the experience each gains.

**The app checks:** a story gives 5 to 10 experience in all, at most 5 to one Ability (an Adventure's award, DE p. 376).

**The app does:** adds the experience to the Abilities now (an Ability the grog lacks is added), writes a "Story experience" entry in the Diary, and adds one to the year's **Story awards**. In Winter each award takes a season of the update: the first exposure, then the vocational training, the practice and the second exposure.

**See also:** [Grog's Yearly Update](help:grog-year), [Diary tab](help:tab-diary)

# Plan Copying
<!-- help: grog-copying -->

A covenant's scribe is often a grog. Grogs aren't planned season by season, but a season of copying is (DE p. 380): **Plan Copying** plans one for the grog, on the same form as anyone's season, offering only Copy a book and Copy Lab Texts.

<!-- tui -->
Open it from a grog's **Planning** tab: More (`m`), then **Plan Copying** (`c`). Once a season is planned, **Clear Copying** (`x`) drops it.
<!-- /tui -->
<!-- gui -->
Open it with **Plan Copying** in a grog's **Planning** chapter. Once a season is planned, **Clear Copying** drops it.
<!-- /gui -->

The season is played when it is advanced, as anyone's is, and the grog's This Season shows it below the yearly update. Each season spent copying takes a season of the yearly update in Winter, as a story award does: the first exposure, then the vocational training, the practice and the second exposure.

**See also:** [Grog's Yearly Update](help:grog-year), [Plan Season](help:plan-season)

# Advance Season
<!-- help: advance-season -->

<!-- tui -->
`t` moves the saga on by one season and applies every plan made for the season that is ending. It works from anywhere in the workspace.
<!-- /tui -->
<!-- gui -->
**Advance Season**, the card with the present season's medallion at the foot of the chapters on the left, moves the saga on by one season and applies every plan made for the season that is ending: click anywhere on the card. It is there on every page of a saga that has chapters, so the last thing you do in a season can be the last thing before it ends; a Creation Worksheet, a Fight and a Siege have none, as a record is finished or left first. Once you say Advance, a dial of the four seasons turns in the middle of the window to bring the new season to the top, then shows its medallion with its name and year, and fades; click or press a key to skip it. With **Reduce motion** on, the new season simply follows.
<!-- /gui -->

**You type:** only your answers to the questions it asks.

**The app works out:** each plan's result, the end-of-year events in Winter, the covenants' vis harvests, and the new date.

### The confirmation
<!-- help: advance-season-confirm -->

The Advance Time dialog asks whether to advance from this season to the next, and summarises the plans:

- how many planned seasons will be applied;
- who has nothing planned (they gain nothing this season);
- any plan that can't be carried out, and why.

When the year is about to end it also says that each covenant's surplus will be added to its Wealth and that Emergency Savings start again at 0. If you advance by mistake,
<!-- tui -->
More's Set Date on the saga
<!-- /tui -->
<!-- gui -->
**Set Date** in the saga page's Seasons chapter
<!-- /gui -->
puts the date back, but it doesn't undo what the season did.

### Questions along the way
<!-- help: advance-season-questions -->

After you choose Advance, the app may ask:

- For work that runs until it's done, whether anything interrupted it this season (see [Interruptions](help:advance-interrupted)).
- For the player characters with nothing planned, and any plan that can't be carried out, what to do with the season (see [Unplanned seasons](help:advance-unplanned)).
- In Winter, if a covenant is in deficit, whether to advance anyway. Advance anyway rolls the year over; No (or Escape) leaves the date alone so the books can be balanced first.
- Which contested vis or income sources whose security has lapsed were secured this season, one tick each. A ticked one is secure for five years; one left unticked gives nothing until it is.
- For each experiment whose Extraordinary Results need the storyguide's word, what they are: which of two rolls stands, what each side or modified effect is, what a Discovery teaches, what a special result becomes, and whether to take a Discovery the risk can reach (see [Experiment Results](help:advance-experiment-results)).
- For a magus finishing a recreation of a flawed spell, whether to retire the flawed one (see [Retire Flawed Spells](help:advance-retire-flawed)).
- For a magus setting up a new laboratory, whether they would like to finish it next season (see [A new laboratory](help:advance-new-lab)).
- For each player covenant on the move, and each of its ships apart from the fleet: move on to the route's next leg, stay, or go somewhere else (see [Whereabouts](help:section-cov-whereabouts)). The answer is logged as a stop in the new season, and a move costs the covenant its Aegis.

Cancelling any of these leaves the date and the saga as they were.

### A new laboratory
<!-- help: advance-new-lab -->

When a magus has planned **Set up a new laboratory**, Advance Season asks, for each one, "Would you like (name) to finish it next season?". The laboratory works after this first season, but with the Basic Flaw (-3 General Quality) until a second season's work in it removes the Flaw (Ars Magica Definitive Edition, Chapter 8: Laboratory, Setting Up a Laboratory).

- Leave it ticked and **Continue**: the magus's next season is planned as **Set up the laboratory**, lab work in the new laboratory, unless something is already planned for it. It shows on the laboratory's Planning tab, where it can be changed or cleared like any lab work.
- Untick it to decline: the laboratory keeps the Basic Flaw until you plan **Set up the laboratory** on its Planning tab yourself.

### Experiment Results
<!-- help: advance-experiment-results -->

When a magus experimented this season (Ars Magica Definitive Edition, Chapter 8: Laboratory, Experimentation), the Extraordinary Results chart has already been rolled when the season is advanced. Lab work in an unsafe or a Warping laboratory comes here too, experiment or not, when the laboratory warped it (see [Safety and Warping](help:guide-lab-safety-warping)). Before anything is applied, Advance Season asks the storyguide about each experiment whose results need a decision, one form per experiment, titled **Experiment Results** with the magus's name. Nothing on it is applied until the season is played, and cancelling leaves the saga as it was.

- **Which roll stands**: a magus with Exciting Experimentation or Creative Block rolls the chart twice. Both rolls are shown, and the storyguide picks the one that stands (the more amusing, says the Virtue). Only the chosen roll's questions are shown. While seeking an Arcane Discovery, both rolls already have the risk modifier's move applied.
- **Side effect** and **Modified effect**: what the sub-table gave, with **Which stands** when two dice gave different results, and **What it is**, the storyguide's description. It may be left blank and filled in later on the creation's experimental effects. A modified effect can also change the creation's **Range**, **Duration** or **Target**, or its **Potency** in steps. The level never changes and no requisite is added. A fatal flaw is marked on the creation.
- **Discovery**: the Ability (15 xp) or Art the experience goes to.
- **A special result or story event** (a 9): **A story event** is written in the laboratory's and the covenant's Diaries as an open story; **The creation changed** is described and kept with the creation's experimental effects; **Extra vis** asks for the effect's magnitude plus the risk modifier in pawns of the project's Technique or Form vis, and without them (or more than the magus can handle in a season) the season is a Complete Failure; **A spell as well** opens a spell form next, for a spell of the same Technique and Form up to half the Lab Total, which the magus learns with a Lab Text.
- **The Disaster** with 5 or more zeroes: the laboratory destroyed (Deformed and Unstable, and the magus Incapacitated), or a story threatening the whole covenant.
- **Take the Discovery**: when seeking an Arcane Discovery and the risk modifier could move the roll onto 10, a roll card shows the die and the risk, where the roll landed on the chart, and the chance a stabilization would then succeed, since it repeats the same move. The roll's own result stands either way.

Every chart roll of 0 rolls botch dice: 1, plus the risk modifier, plus the laboratory's aura (the one its Lab Total uses), less Cautious Sorcerer's, less the laboratory's Safety (a negative Safety adds dice). On a 12 or more, each further roll is a stress die plus the risk modifier, with the same botch dice, stabilizing too; after ten 12s in a row the storyguide rolls the rest.

**The app's assumption about Potency.** The rules say a modified effect can be more or less potent but give no size. The app takes one step as 5 points of the Lab Total behind the creation, which for a Longevity Ritual is 1 point of its modifier (so a ritual reduced by a step protects one point less on every aging roll). Where nothing is worked out from the Lab Total, the change is only described and recorded.

### Unplanned seasons
<!-- help: advance-unplanned -->

A season left with nothing planned takes the saga's default for that kind of character, set in the saga's settings:

- **Magi** and **Companions with nothing planned**: **Work / Exposure** (the default) gives 2 xp of Exposure in their profession (an Ability named Profession: ...), else a magus's Magic Theory (if they have a score in it), else their highest Ability that isn't a language. The Diary entry is marked "(default)". **Nothing** leaves the season empty.
- **Grogs with nothing planned**: a grog with no [yearly update](help:grog-year) gains 2 xp of Exposure a season in their highest Ability, 8 when Winter is advanced, marked "Yearly update (default)". **Nothing** gives them nothing.

Advance Season's **Unplanned Seasons** step names each player character (one with a Player) who has nothing planned, with a choice: **Default** (what the saga's default gives them), **Nothing this season**, or **Plan it now**, which opens [Plan Season](help:plan-season) for them and then carries on with the season. A plan that can't be carried out is listed too, with the reason: **Leave it** skips it, as before, or **Plan it again now** opens it to change. Cancelling any of these leaves the date and the saga as they were, apart from plans already saved.

Non-player characters with nothing planned aren't named: they take the default. Tick **Name Idle Non-Player Characters** (on the terminal, Be notified when and which non-player characters do not have seasonal activity) in the saga's settings to have them named and asked about too.

### Interruptions
<!-- help: advance-interrupted -->

When a season has work planned until it's done (reading a summa to its Level, writing, copying or translating a book, or lab work over several seasons such as inventing a spell), Advance Season first asks whether anything interrupted it. Each piece of work is listed with its character, the work, and the last season planned for it:

- **Days away from the laboratory** (lab work): up to 10 cost nothing, 11 to 20 lower the Lab Total, and more rule out lab work this season.
- **Months lost** (reading and other study, and a season writing, copying or translating a summa): each full month lost to distractions cuts the season's total by a third (0 to 3).
- **The whole season lost**: nothing is done on the work this season, and no Diary entry is written for it.

Leave them as they are and **Continue** if nothing interrupted it. Once the season is played, the seasons the work still needs are worked out again from where it stands: a season is added at the end when it fell behind (or a note says the season after is planned for something else), and seasons no longer needed are cleared when it finished early. The message after the season says what changed.

### How the season is applied
<!-- help: advance-season-apply -->

Every plan's outcome is worked out first, from the saga as it stood before the season, and only then are they all applied. So one character's results can't change another's, or their own, in the same season: raising Magic Theory this season doesn't raise this season's Lab Total. Dice left blank on a plan are rolled now.

Before anything is applied the saga is backed up to `sagas/backups` in your data folder (the last five are kept), so the season can be undone by copying the backup over the saga's file.

Then, for each plan:

- the experience is added, and lab work, book work and the like are carried out;
- an entry is written in the character's Diary (and the laboratory's or covenant's, where the work touches them);
- a plan that can't be carried out is skipped, and the record says why.

The season's plans are then removed.

### Winter: the end of the year
<!-- help: advance-season-winter -->

When Winter is advanced, the year ends:

- each grog's [yearly update](help:grog-year) is applied;
- a character running a business pays its yearly upkeep in Labor Points (City & Guild), with Perfect Eye for Commodity's gain and Bigamist's second household;
- yearly Warping Points are added, for a Longevity Ritual, for living in a strong aura of another realm, and for Raised from the Dead, Immortality of the Forest (which makes no aging roll) and Susceptibility to Warping;
- every character aged 35 or more (50 with Strong Faerie Blood or Dhampir), or with a Longevity Ritual, makes an aging roll (Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Aging), written in their Diary; a magus the Great Elixir made a being of Magic makes none and gains no Warping (The Mysteries Revised Edition p. 44);
- Dwindling Resources lose a tenth of their value when they began dwindling (gone after ten years), and a contested resource still not secured gives nothing that year;
- each covenant's surplus is added to its Wealth.

- Transitions of maturation (Apprentices pp. 14-15). At the end of a year, each character turning 8, 15 or 21 next year has a line and a Diary entry: in the first season of that year Virtues and Flaws may be exchanged, Minor for Minor and Major for Major; Child ones must be exchanged by 21 and Inherited ones have manifested.


Every season, each covenant's vis sources for that season are harvested into its vis stores and written in its Diary, and every wounded character makes the season's [Recovery rolls](help:recovery-roll) (bruises first leave their residual wounds), written in their Diary; everyone's Fatigue is rested away.

### Afterwards
<!-- help: advance-season-after -->

<!-- tui -->
The date moves on, a message names the new date and whose seasons were applied, and, when anything happened, the [Season Summary](help:season-summary) shows the results. With Keep season records on, the season is also kept under [Seasons](help:seasons) in the tree.
<!-- /tui -->
<!-- gui -->
The date moves on. When anything happened, the [Seasons](help:seasons) page opens on **Just played**, the [Season Summary](help:season-summary), which names the new date and whose seasons were applied; otherwise a message says so. With Keep season records on, the season stays on the Seasons page, opened from **The Seasons Played** in the saga page's Seasons chapter.
<!-- /gui -->

**See also:** [Plan Season](help:plan-season), [Season Summary](help:season-summary), [Seasons](help:seasons), [The saga](help:saga), [How to plan and run a season](help:guide-seasons)

# Hold Tribunal
<!-- help: hold-tribunal -->

A Tribunal's meeting, held a step at a time from its **Meeting**
tab. Each step is a short form: you make the decisions and enter the
rolls, and the app works out the rest. Every form opens by saying which
step it is ("Step 3 of 12"), what comes next, **what the app works out
for you** at that step and **what each thing you enter changes**; the
details panel says the same when you choose a step. Saving a step holds
it and opens the next straight away, so a meeting can be run from roll
call to Closing in one go; Cancel stops, and the meeting waits at the
step in hand. The meeting is saved after every step, so leaving it
simply leaves it; holding it again resumes at the step in hand. For a
meeting walked through from start to finish, see [How to hold a
Tribunal](help:guide-tribunal).

The rules are Ars Magica Definitive Edition's (Chapter 2, Tribunals: a
quorum of twelve magi in person from four covenants and a Quaesitor;
the Praeco and the Presiding Quaesitor don't vote, the Praeco breaking
a tie), with Houses of Hermes: True Lineages (House Guernicus, Tribunal
Procedures) for how a case is heard and Houses of Hermes: Societates
(House Tytalus, The Fine Arts of Debate) for the debate.

The steps run in a fixed order:

- **The roll call and proxies**: each covenant's magi, ticked present
  one by one or all at once with **all present**; how many of a sketch
  covenant's unnamed magi came; the proxies each carries, and whether
  the Presiding Quaesitor allows them or sets them aside. Under
  Hibernia's customs, also whether it shows its cathach: one that
  doesn't has no votes. Its votes in the hall are worked out (the
  Praeco and the Presiding Quaesitor are present but don't vote), the
  quorum is checked, and the proxies are kept on the roster. Only the
  magi ticked present can speak at a hearing: a proxy carries a vote,
  never a voice. Saving it opens the meeting; cancelling holds none.
- **Opening and the oaths**: where it is held, how many days it lasts
  and the day each case and motion is heard. A meeting lasts as many
  days as its Tribunal's customs give: Hibernia's seven (The Contested
  Isle p. 32), three elsewhere; **Days** on the Opening changes it.
- **The new magi and the sigils by proxy**, under the Rhine's customs, the first business
  after the Opening: every magus of its covenants who passed his Gauntlet since the last
  meeting is introduced (tick each, or name others not in the saga), then the rite confers a
  retired magus's sigil on each master and archmage made since (by the Mark of Approval or
  the Archmage's Challenge). Name whose sigil it is: typically his master's, if retired. Each
  sigil adds a proxy to his covenant's votes, at this meeting and the next. Holding the step
  again confers afresh, never twice (Guardians of the Forests pp. 24, 26-27).
- **The Hermetic Assembly**, on the first day under the Theban customs,
  in two steps. **The Assembly's decrees**: the principal phyle governing the meeting
  (the next in turn, Ionian, Aegean, Kretan, Propontian, unless you
  choose another); a decree of citizenship for each metoikos, making
  them a polites; a decree of contrition for each polites with a shard,
  taking one away (it asks the reparation: what the magus offers, and
  its vis in pawns of an Art, which leave his own vis for the Tribunal's
  treasury, as many as he has, when the decree is accepted; The Sundered
  Eagle p. 33; holding the step again gives them back first, and the
  minutes name each reparation); and a decree of defamation against a polites, which
  if upheld gives the accused a shard and if rejected gives the one who
  brought it a shard. **The ostrakismos**: the logothete reads every
  polites holding a shard, and the one on the most sherds (or no one)
  is ostracised: they become a metoikos, lose their tokens and shards,
  and may not return for seven years. The Theban Law Council and
  People's Court are the meeting's motions and cases, below.
- **The Apprentice Presentation**, under the Theban customs, between the Assembly's decrees
  and the ostrakismos: the Gifted children the Treasury Council found, interviewed for two
  days before the meeting. Enter each child the troupe's magi interviewed (up to five), her
  age, who delivered her to the Council (a polites who did earns a token, The Sundered Eagle
  p. 28) and the tokens each magus gave her (up to three magi). Only a polites with no shard
  may give tokens, or any Bonisagus even with one, since the Code trumps local custom, and
  no magus may give more tokens than he holds (p. 32). A child given tokens by one magus is
  his apprentice; one given tokens by several chooses, usually the one who gave the most (the
  app picks him, the first entered on a tie, unless you choose another of them); a child given
  none may be claimed by any magus, even one with a shard (pp. 33-34). Any Bonisagus may
  claim any child outright by the rights the Oath gives his House, whether or not he gave her
  tokens and whatever his shards: name him under **Claimed by** (shown only when the Tribunal
  has a Bonisagus), and her choice doesn't override him. By tradition he still gives her a
  token or two; enter them as his bid and she keeps them (p. 32). Her master's tokens leave him and stay with her,
  to spend once she is a maga; the others' go back to them. Each child given becomes a
  Sketch character at her master's covenant, with her master as parens and the tokens she
  keeps in her summary. Once given, holding the step again changes only its note.
- **Each case and motion**, on its day: the debate between the
  prosecutor and defender (for a motion, one who speaks for it and one
  against), each chosen from a drop-down of the magi present (shown with
  their covenant). The prosecution may instead be the Presiding
  Quaesitor, who prosecutes a high crime no one else will; the defence
  a Guernicus advocate, who defends an accused who didn't come; and a
  motion's opponent the Tribunal itself, since a proposer debates the
  whole hall. The case's own speakers, or the magus (or a magus of the
  covenant) it names, are chosen to start with, and an accused who is
  absent is given the advocate. A charge or appeal can instead be
  settled at the private hearing (tick **Settled in private**), when
  both sides accept the
  Presiding Quaesitor's ruling: it then has no debate and no vote, and
  its ruling starts as "Settled at the private hearing". Enter each
  side's debate Fatigue levels
  lost, or leave both blank and the debate is rolled round by round by
  the rules of Houses of Hermes: Societates (The Fine Arts of Debate):
  Communication + Folk Ken, Intrigue or Artes Liberales (as logic and
  rhetoric, for Academic Concentration and Aristotelian Training) against
  Intelligence + Charm, Guile or Leadership, each debater using what
  they are best at (by lot each round among Abilities of the same score:
  the app's stand-in for each debater's choice of tactic, Houses of
  Hermes: Societates pp. 90-91). A hit costs debate Fatigue only
  when Presence and the margin beat the defender's Resistance, their
  best positive Reputation + Confidence (+3 Strong Willed), so a weak
  speaker's hits on a well-known magus can cost nothing (p. 90). A speaker with none of those scores written down (an
  advocate, the Tribunal, a sketch magus) debates at the skill you give:
  **Middling** (an ordinary magus: Characteristics 0, those Abilities
  2), **Able** (Characteristics +1, Abilities 4) or **Formidable**
  (Characteristics +2, Abilities 6, a Reputation of 3); the rules give
  no figures for them, so these are the app's. The case's Evidence is the prosecution's testimony
  and the Defence testimony the defence's, each used once: a peer's +3,
  an apprentice's or familiar's +2, any other +1, and +3 more if a
  Quaesitor examined it. The side that lost fewer levels wins, and the
  difference is its Argument Strength (less 1 for a motion that adds to
  the Code, 3 for one that alters it).
  **Heard by** (a charge or appeal): Debate, as above; Certamen in its
  place, which binds the case however persuasive the loser: say who won,
  and the case goes to its ruling with no vote; or Certamen on one point
  of it, where the Fatigue levels each side actually lost stand in for
  the debate's levels lost, and its winner doesn't win the vote by it
  (Houses of Hermes: Societates p. 92). Certamen in its place is offered
  only for a personal charge one magus brings against another whose
  charge names no violation of the Code: it can't over-rule a Tribunal,
  so an appeal against a ruling is debated, and it can't require a
  violation of the Code or a magus to overlook one, so a charge naming a
  high or low crime is too (DE p. 230). The Heard by hint says why when
  it isn't offered.
  **Argues** (each side): In good faith; Knowing it false, when the
  speaker's Truthful Personality Trait comes off each of his Defence
  Totals (a deceitful Trait gives nothing); or a flawed, despised or
  preposterous thesis, which starts the debate 1, 2 or 3 levels down
  (The Power of Truth, p. 91). A motion opposed by "The Tribunal" is
  debated by the whole hall: each round a different magus present (its
  proposer aside) questions the proposer, at the skill you give the
  Tribunal if he has no scores written down, and the levels lost are all
  the Tribunal's (p. 92). **Changes** (a motion): the Peripheral Code;
  the Peripheral Code, and recommended to the next Grand Tribunal (a
  regional Tribunal can change only its own Code); or heard at the Grand
  Tribunal, which costs the proposal 1 more Argument Strength on top of
  an Addition's 1 or an Alteration's 3 (p. 93).
- **The vote** on each case: each covenant's leaning, which you can
  change, with why it leans that way under it (it brings the case, the
  case is against it, or its attitude toward a troupe covenant that is
  a party), and the votes the debate won: an Edge wins 10% of the
  undecided votes, up to a Landslide's 60%, and from a Triumphant
  Victory 10% to 30% of the other side's too. The covenants are called
  one by one and the tally kept; what is left undecided abstains. On a
  tie the Praeco casts the deciding vote: choose for or against (on a
  call for a Wizard's March a tie defeats it).
- **The Sacred Council**, on the first day under Hibernia's customs:
  tick each faction's ambassador confirmed for this meeting (from the
  Ambassadors tab), and write the disputes heard. Each confirmed
  ambassador votes as a magus does: they are called after the
  covenants, undecided unless named as a party, and you can change
  their leaning like a covenant's.
- **The Praeco's succession**, on the first day under Normandy's
  customs: with no Praeco, the eldest magus of the Tribunal (by Year
  Born) is offered; set them aside by choosing the next eldest. The one
  named becomes Praeco, and the minutes say who was passed over.
- **The Library of the Tribunal**, under Normandy's customs (The Lion and
  the Lily pp. 22-23). The books the Tribunal owns in common are kept at
  Confluensis and read only by those who win them at the Tourney, on a
  seven-year lease, back before the next meeting. At the meeting's
  Library step: tick each lease that is up as returned (one left
  unticked is noted as still held); record a book a magus of the
  Tribunal wrote and gave to the Library (it goes to Confluensis), and
  the giver's prize, a Library book worth no more Build Points than his
  gift (one lease for each book given, as many as there are to give);
  and each book won at the Tourney, with the covenant that won it, as
  many as the Library has free. A team buys its books with the prize
  pawns its rank won at this year's Tourney (record its points on the
  Tourney tab first): a book costs a pawn per 5 Build Points, a fraction
  counting as a pawn, and the step refuses a team's books costing more
  than its pawns. At the Tourney each team takes one tropaeum or lump of
  vis and one book or item a round, in rank order, then picks again
  while pawns remain (The Lion and the Lily p. 33); the pawns it spends
  on tropaea and vis aren't counted here. A leased book stays the
  Tribunal's, kept at Confluensis: the lessee has seven years' exclusive
  access. Two prizes can't name one book: when two contributors want the
  same book, certamen settles it.
- **Residency**, under Provence's customs (Faith & Flame p. 22). A magus
  is a resident of the Provençal Tribunal who attended one of its last
  three meetings, or was granted residency by vote at his first, or
  registered on arriving (with the Redcaps and the Praeco, or his
  nearest neighbour). One Gauntleted in the Tribunal is a resident until
  three meetings pass without him. The meeting's roll of residents
  records the magi present, lets you grant residency to a newcomer
  present, and records a resident's departure, registered or not (voting
  at another Tribunal without registering his departure breaks the
  Peripheral Code). Until three meetings are recorded, every magus of
  the Tribunal is presumed a resident. A magus's sheet shows his
  residency and why.
- **The execution of sentences**, on the last day under the Theban
  customs, before the outgoing magistrates are paid: each charge the
  People's Court heard, its verdict taken from how its vote went
  (carried: convicted; failed: exonerated; settled or not voted: no
  verdict). A conviction gives the guilty three shards for a High Crime
  or one for a Low Crime, beside its punishment, and the magus who
  brought the case a token, three if the guilty was Marched; a case the
  Court defeated gives its bringer a shard. Choose the accused and the
  accuser from the Tribunal's magi (the step guesses them from the
  case's names). A metoikos is given no tokens or shards. No March is
  held on Delos (The Sundered Eagle pp. 28, 35).
- **The conduct of archai**, under the Theban customs, after the sentences: any polites may
  ask that the conduct of an arche (the archon among them, as he is elected from the archai),
  or of the polemarch, be examined, naming the fault (a case poorly
  defended or prosecuted, a bribe, indolence) and proposing a fine of one to seven shards.
  Up to three complaints: for each, the magistrate, who brought it, the fault, the fine and
  how the votes went. A complaint upheld with its fine gives the magistrate the shards; one
  rejected, or whose fine is voted down, gives none. Failing to win or stop a conviction is
  no fault unless the neglect was willful (The Sundered Eagle p. 35). The logothete isn't offered: the book names only an arche or the polemarch (The Sundered
  Eagle p. 35). Holding the step again
  undoes the first holding first.
- **The common vis sources**, under the Theban customs, before the outgoing magistrates'
  tokens: the vis sources the Peripheral Code holds in common, gathered for the Tribunal by
  magi the Treasury Council names. For each source, its Art, its gatherer and the pawns
  brought into the coffers: each gatherer earns a token for the period (one token for each source he
  gathers: the book's 'one per Tribunal period' could also mean one per magus however many he
  gathers, so this is the app's reading; give back the extra by editing his tokens if your
  troupe reads it the other way), and the pawns go
  into the treasury as vis; a gatherer who forgot to harvest it (tick **Neglected**) is
  given a shard and brings in nothing (The Sundered Eagle pp. 28-29). The sources and their
  gatherers are kept, so the next meeting's form starts with them. The whole Tribunal
  gathers some 50 pawns a year, Creo and Vim the most, about half of it spent on the yearly
  Longevity Ritual (pp. 29-30).
- **The Council of Archai**, on the last day under the Theban customs,
  in three steps. **The outgoing magistrates' tokens**: each outgoing magistrate is
  paid in tokens, 2 for an arche, 3 for the archon and 5 for the
  polemarch (untick one to pay nothing). **The sortition**: four archai
  are drawn by lot from each phyle, the principal phyle first, from its
  politai who are not archai now (Redcaps are not drawn); the draw is
  kept, so holding the step again draws no one new, and one magus drawn
  may be set aside for the next drawn from the same phyle. A phyle with
  fewer than four politai leaves its other seats for the logothete to
  fill with Redcaps. A drawn magus set aside because he refused to
  stand is given a shard (choose "Refused to stand"); one set aside for
  any other cause is not (The Sundered Eagle p. 32). The new archai are then placed on the
  boards: those who have been archai before first, each on a board he
  has not sat on, by lot where he has a choice; then the rest by lot
  until each of the Judicial, Legislative and Conciliatory Boards has
  three; the others form the Treasury Council, where one is drawn
  tamias, four gather vis and Gifted children (one from each phyle where
  they can) and the rest are tutors. A board no arche can fill is left
  to the logothete's Redcaps, and the minutes say how many seats. Each
  arche's Duties say where he sits, the Tamias office takes the one
  drawn, and the Tribunal remembers who has sat on which board (pp.
  27-28, 35). The new archai serve until the next meeting.
  **Archon and polemarch**: the new archai elect the archon from among
  themselves (the eldest is offered) and the polemarch from every
  polites; the archon becomes the Tribunal's Praeco.
- **Rulings and fines**: the ruling on each case, starting from how its
  vote went, **written out** or from a **ruling template**; any fine,
  in pawns of an Art or (with no Art) pounds of silver, and who pays it;
  whether the ruling goes into the Peripheral Code (a motion's does
  unless you say otherwise); **term**, the years after
  which the matter comes back; and, for a case between a troupe covenant
  and another, how the other's attitude toward the troupe's moves (a
  party that lost takes it ill, -1). A template's blanks are asked
  next, one form a case, with the finished sentence shown under it as
  you fill them: "{party} holds {what} for {years} years, until it is
  debated again" becomes "Keep holds the Rhine ford's vis for 7 years,
  until it is debated again". A {years} blank sets the term. The
  templates are the saga's own, kept in the saga's settings ([the
  saga](help:saga), Ruling templates), where you can add, change and remove them; a blank
  is any word in braces. They include the Code's penalties (Houses of
  Hermes: True Lineages pp. 59-61): Damages, a fine shared a third to
  the prosecutor and two thirds to the Tribunal's coffers, Seasons of
  service, Investing items, Loss of an apprentice, Banished, Loss of a
  familiar, Death of a familiar, and Cast out (the estate a quarter to
  the victim, a quarter to the prosecutor, a half to one who is both, the
  rest to the heir: Houses of Hermes: True Lineages p. 59). A case's
  details show beside it the established convention that whoever slays
  the outcast takes the heir's half once the others are paid (p. 53).
  A case that may March the accused asks **Marched**: a conviction for a
  high crime when the prosecution called for a March and a simple
  majority carried it (a tie defeats it), or a Quaesitor's March the
  Tribunal ratified (Houses of Hermes: True Lineages pp. 58, 63). A charge
  also asks how many times the convicted magus **refused** a lesser
  penalty: at three he is Marched whatever the crime (p. 59). Closing the
  meeting writes the March on the outcast's Hermetic Background (when the
  case's Against names a character): the year and the Tribunal that
  renounced him. He is safe until the Tribunal closes, then outside the
  Code (DE p. 18; p. 60). A declaration of Wizard's War is not heard
  unless its service is disputed. The hunt itself is not worked out.
- **Treasury and vis**: the treasury as it stands and the loans that
  fall due this year.
- **The next host, by lot**, under Normandy's customs: a covenant of
  the Tribunal is drawn, and may be drawn again once (the second draw
  stands); it becomes the Tribunal's meeting place, and the minutes say
  where it meets next.
- **The tithe of Gifted children**, under Hibernia's customs: the Coill
  Trí bring a Gifted child from each of their seven túatha (as the
  Tribunal records them, else unnamed). Each túath offers three, made
  once and kept: the first is brought unless you choose another, which
  is a reroll. Each child has a name, an age from 5 to 12, a Gift
  (ordinary, Gentle or Blatant), a sign or two of what they may become,
  and where they come from. Now and then a child has no true Gift, which
  only this examination shows: they are turned away. Then give them
  out **By hand**, choosing a magus of a represented covenant for each
  (or none), or **By bidding**: each represented covenant with a magus
  who has no apprentice bids vis, a roll of a ten-sided die, 2 pawns
  for each such magus and a tenth of its vis, more for a Gentle Gift and
  less for a Blatant, never more than it holds; the highest bid wins
  the child for its first such magus, and the price is taken from its
  Raw Vis Stores, the fullest first, each in its Diary. The outcome
  shows under the form before you give them. Each child given becomes a
  Sketch character at their master's covenant, with their master as
  parens, and the minutes list where every child went. Once given,
  holding this step again changes only its note. A magus has an
  apprentice when someone not yet a magus names them as parens. The book
  says only that the Coill Trí owe seven Gifted children and that a
  child offered is sometimes turned away (The Contested Isle pp.
  113-114): the three each túath offers, the odds of each Gift (14, 3
  and 3 in twenty, one in twenty no true Gift) and the bidding are this
  app's own.
- **The Ceremony of Propitiation**, under the Theban customs, before
  the closing: the archon casts the ancient Ritual from its Casting
  Tablet at eight pawns of Creo or Vim, taken from the treasury; then
  each covenant offers to its patron. Enter the pawns each covenant
  offers and its patron's Might (remembered for next time); each patron
  gains 25 xp less its Might, the Might cut by two for every pawn
  offered, so a Might 25 patron offered 10 pawns gains 20 xp. The League
  Against Idolatry boycotts the rite (The Sundered Eagle p. 31). The
  pawns offered are not yet taken from the covenants' own stores.
- **Closing**: each case with a ruling is decided and what its ruling
  says is written: the fine, owed to the Tribunal's treasury; the
  ruling, into the Peripheral Code; the attitude's move, as a reason
  on the covenant's attitude; and a term's end, on the case. The Acta, the meeting's acts set out as a
  charter, goes into the Tribunal's Diary, and the next meeting is set
  for when the Tribunal next meets.

Any step can be held again to change it; saving it then goes on to the
step in hand. Every step has a Note for anything said or decided in
your own words.

**Terms that come due.** A ruling made for a term comes back. [Ahead](help:section-ahead)
lists the season before its term ends and the season it ends;
advancing into the season before says it ends next season, and
advancing into the season it ends says so and puts the matter back on
its Tribunal's docket as a new case ("Fengheld v. Keep (debated
again)"), with the old ruling in its charge, for the next meeting. The
case's details on the Docket show when its term ends.

Each step held writes its minutes into the Tribunal's Diary, an entry
headed with its day ("¶ The First Day: The roll call and proxies"), its
numbers in the margin (the votes in the hall, a vote's tally, a fine)
and its Note after its own words. Holding a step again rewrites its
entry rather than adding another. The Acta, like any Diary entry, can be
reworded by editing it.
<!-- gui -->
On the desktop, choose the Acta in the Diary and press Print to print it
to a PDF.
<!-- /gui -->

**Transylvania's meeting.** Two steps come before the rulings.

*The Praeco's purse* (Against the Dark p. 19). The Tribunal gives the
Praeco the projects she is to fund until the next meeting, and with them
the levies she may raise: write the projects, then a levy on each oppidum
(in pawns of an Art, or in pounds with the Art left blank). The book has
the legal covenants of the cives, socii and coloniae, and some of the
foederati, owe the projects reasonable aid, by their status, not each magus
for himself; the hospites' covenant is not named, so an oppidum of hospites
can't be levied. The app lays each levy on an oppidum, and its hint says
which of the oppidum's magi belong to a covenant that owes aid. Each levy goes on the treasury, owed until it is marked
paid. The pawns from the large vis source set aside for her come into the
treasury. She collects the Redcaps' and Quaesitores' stipends and Redcaps
deliver them, so they only go into the minutes. She may redeem promissory
notes (their pawns leave the treasury) and issue a new one: what it
borrows comes into the treasury now.

*The Curantis and his Notary* (p. 97). The Curantis keeps the zenodochia,
the Tribunal's safehouses for travelling magi. He is appointed at every
meeting for a term to the next, usually unopposed, and no one serves two
terms running. Say whether the outgoing Curantis built a new zenodochium
in his term, as he is expected to; choose the new one, the Notary the
outgoing Curantis selected (often a Redcap, or a magus fresh from his
Gauntlet), and his salary, which leaves the treasury now. Both then show
as offices on the Five Covenants list. A colona may not be Curantis.

**See also:** [How to hold a Tribunal](help:guide-tribunal), [Tribunal sheet](help:tribunal), [Meeting tab](help:tab-trib-meeting)

# The World Turns
<!-- help: world-turns -->

The yearly step. When Winter is played, Advance Season asks one more
question before the season is played out: what the year brought beyond
the covenants. Each line has a tick box, and only the ticked lines are
applied.

- **Threat clocks**: a place's trigger tied to a threat comes up in the
  season it comes, Winter or not. Answer **Failed** (the threat moves on
  its steps, and the line says which stage that reaches), **Kept** (it
  stays) or **Leave it unanswered** (nothing is written). Failed and
  Kept are written in the threat's Diary and the place's. In a season
  other than Winter these are the only questions, titled *The World This
  Season*, and they go into an entry of their own.

- **Places**: each place's triggers that came this year (written into
  the place's Diary), and, with the Auras change rule option, each
  aura's year: a Magic aura's yearly modifier and its roll on the
  Strengthening or Weakening table, or an Infernal aura's erosion
  (already rolled: what you see is what is applied).
- **Threats**: a dated stage whose season has come is marked as having
  happened.
- **Neighbours**: each fair a covenant trades at rolls its income for
  the year.
- **Tribunal treasury**: a loan due this year; tick it if it was repaid
  (it starts unticked).
- **Attitudes**: the year's events with each neighbour (favours begun or
  repaid, a covenant's Diary entries naming it). Where the year's
  favours make it plain, the change is suggested, with its reason filled
  in: +1 for each favour the covenant did the neighbour or repaid it this
  year, at most +3. Accept it by saving, or change it; a Diary entry
  alone suggests nothing, since the app can't tell how it went. A change
  needs its reason.

**You type:** the ticks, each threat clock's answer, and each
attitude's change and reason.

**The app works out:** everything applied goes into one entry, *The
world turns, Winter 1220*, under The World Turned on Seasons. Delete
that entry to undo all of it; a value changed by hand since is left as
it is, and you are told.

Cancel stops Advance Season: the date stays.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons)

# Season Summary
<!-- help: season-summary -->

<!-- tui -->
Shown after a season has been advanced, when anything happened: what the season gave everyone, grouped by covenant.

**You type:** nothing. Enter, Escape or Close closes it.
<!-- /tui -->
<!-- gui -->
Shown after a season has been advanced, when anything happened: the **Just played** chapter of the [Seasons](help:seasons) page, first in its rail, says what the season gave everyone, grouped by covenant.

**You type:** nothing.
<!-- /gui -->

**The app works out:** one line per person: the activity, what it was on and its result (for example the xp gained). A plan that couldn't be carried out shows why; a magus or companion with nothing planned is shown as "nothing planned". In Winter it also lists aging rolls, grogs' yearly updates and business upkeep, and in any season the covenants' vis harvests.

The note at the bottom says whether the season is kept
<!-- tui -->
under Seasons in the tree.
<!-- /tui -->
<!-- gui -->
on the Seasons page.
<!-- /gui -->
If season records are off (the saga's settings), each character's Diary still has their entry.

**See also:** [Advance Season](help:advance-season), [Seasons](help:seasons), [How to plan and run a season](help:guide-seasons)

# Creation Worksheet
<!-- help: creation-worksheet -->

Walks a covenant, laboratory or character that is In Creation through the book's steps, showing each step's budget, what was spent or taken there, and its checks.
<!-- tui -->
It fills the screen, and opens by itself when you make a new covenant, laboratory or character.

**You type:** nothing in the worksheet itself. Its keys and buttons open the same dialogs as the sheet, and they edit the real record; everything is saved as you go.
<!-- /tui -->
<!-- gui -->
It is a page of its own, below the record's in the trail, and opens by itself when you make a new covenant, laboratory or character.

**You type:** nothing in the worksheet itself. Its buttons open the same forms as the record's page, and they edit the real record; everything is saved as you go.
<!-- /gui -->

**The app works out:** each step's budget and what is spent, and the creation checks, worked out again whenever a dialog closes.

### In Creation and In Play
<!-- help: creation-worksheet-modes -->

<!-- tui -->
A new covenant, laboratory or character starts **In Creation**, with its tree node marked "(creating)".
<!-- /tui -->
<!-- gui -->
A new covenant, laboratory or character starts **In Creation**, shown in its page's header.
<!-- /gui -->
A character made from a template starts **In Play**, since the book's templates are fully made.

<!-- tui -->
The record's top panel has a button showing the mode; clicking it, or More's **In Creation / In Play**, switches between them after a confirmation.
<!-- /tui -->
<!-- gui -->
The record's header has a button showing the mode; clicking it switches between them after a confirmation, and the page changes its colours to match.
<!-- /gui -->
Creation checks only run while a record is In Creation, and come back if it is moved back. When a covenant moves to In Play, the app keeps what its Build Points were spent on.

<!-- tui -->
Open the worksheet from the top panel's **Creation Worksheet** button, or from More's **Creation Worksheet** on the record's tree node or top panel. Both are only there while the record is In Creation.
<!-- /tui -->
<!-- gui -->
Open the worksheet with **Worksheet** beside the mode button. It is only there while the record is In Creation.
<!-- /gui -->

### Steps and their marks
<!-- help: creation-worksheet-steps -->

<!-- tui -->
The left column lists the steps:
<!-- /tui -->
<!-- gui -->
The rail on the left lists the steps:
<!-- /gui -->

- a character: Concept, Virtues and Flaws, Characteristics, Early Childhood (Pre-adult Life for an [animal grog](help:animal-grogs)), Later Life, Tradition Training (a hedge tradition's member), Apprenticeship and Years past Gauntlet (magi only), Equipment and Review Interests (not an animal), and Finishing Touches;
- a covenant: Baseline, Resources, Boons & Hooks, Review Interests, and Review;
- a laboratory: Setting Up, and Review.

Each step is marked by how its checks stand:

- **✔** every check passes;
- **✘** a rule the book says must be followed is broken (a warning);
- **☞** advice: something the book says should be done isn't, such as too many or too few of something;
- **○** the step has no checks.

A companion may take The Gift (it is free) and then Hermetic Virtues and Flaws. The Definitive Edition says this should be extremely unusual, mainly to play through a magus's apprenticeship, since without magical training The Gift is almost entirely a Flaw (Chapter 3, page 45), so Virtues and Flaws gives that as advice. A Mythic Companion has no Gift, and a grog never has it.

<!-- tui -->
Below the list the app counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Up and Down choose a step; Tab moves to the step's list, then its buttons; Escape closes the worksheet. On the right, the step shows its budget and what is left, its list, its checks (each with what the record has), and buttons for its other edits, for example Edit Characteristics, Learn a spell or Buy a specialist. The chosen row's details show at the bottom: a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

The step's list works like every list on the sheets: **a** adds (Add a Virtue on Virtues and Flaws, where F2 in the picker turns to Flaws; Spend xp on the xp steps), **e** changes the chosen row and **d** takes it back after asking.
<!-- /tui -->
<!-- gui -->
The page's header counts how many steps pass and sums up the checks ("2 warnings, 1 advice", or "all checks pass").

Click a step in the rail to show it. The step shows its budget and what is left, its list, its Creation Checks (each with what the record has), and under **This Step** buttons for its other edits, for example Edit Characteristics, Learn a spell or Buy a specialist. Clicking a row of the list shows its details in the inspector on the right: a Virtue's or Flaw's rules, or an Ability's or Art's score, any Affinity, its creation cap, every worksheet spend on it and what it covers.

The step's list has its own buttons: one that adds (**Add a Virtue** on Virtues and Flaws, with **Add a Flaw** under This Step; **Spend xp** on the xp steps), and, for the row last clicked, **Change its xp** and **Take it back** (or **Remove**), which asks first.
<!-- /gui -->
On an xp step each row shows the pool xp spent and the xp it gained, which is half again with an Affinity, rounded up on the whole spend. The Spend xp dialog shows, as you type, what the pool xp gains, the score that buys and the pool xp the next score needs, and warns past the creation cap; an Ability's Specialty can be given there too. Taking xp back always gives back the pool xp spent and takes off exactly what it gained. On the Later Life step, taking back a training package's row drops the whole package.

<!-- gui -->
Each budget is also a bar that fills as it is spent: gold while some is left, red once it is over, with the sums beside it. Every xp step (Early Childhood, Later Life, Tradition Training, Apprenticeship, Years past Gauntlet) adds **Experience So Far**: each Ability and Art the worksheet has put xp into, with what each step gave it (this step's column first, in bold), the total and the score it buys, so a step shows what the others already gave. Above the steps, **Rules broken** names each step with a rule that must hold and doesn't, and how many; click one to go to that step (its rules are in the line's tooltip).
<!-- /gui -->

The Ability cap at creation goes by age (5 under 30); an Affinity with the Ability raises it by 2 for that Ability, and Mentored by Demons lifts it. An Ability that advances as an Art (a hedge Art, a vitki's runes) has no age cap, only its tradition's (a vitki's runes, 10).

**Schools** (Art & Academe p. 79). Educated may name where the character studied: a rural or urban parish school, a cathedral or monastic school, a municipal school (Italy) for Medicine or for Civil Law (its one major subject besides the basics, the student's choice: the other isn't taught), an imperial school (Spain), a private tutor or a royal court. Its masters' knowledge then caps the subjects it teaches: its major subjects at the school's limit (a cathedral school's 6), its minor ones at half of it, rounded up, and a subject it doesn't teach at 0 (a cathedral school teaches no Medicine). The subjects are Artes Liberales, Latin, Greek, Hebrew, Theology, Civil and Canon Law, Philosophiae and Medicine; other Academic Abilities keep only the age cap. Leave the school blank for no school's limits (a university education, for one). An Ability's details show when its cap is the school's.

On Later Life, (Gild) Trained gives two pools: 30 xp on Order of Hermes Lore, Intrigue and Durenmar Lore, and 60 more on General or Arcane Abilities and the Arts suited to the gild (Guardians of the Forests p. 20). The book lets the 60 buy spells too, a point a level; the worksheet doesn't spend pooled xp on spells yet, so give those levels by hand.

Specialists bought with Build Points are checked too. Each one's score in the Ability they serve with, and a teacher's Teaching, may be no higher than a new character of their age could have: 5 under 30, 6 to 35, 7 to 40, 8 to 45, 9 after that (DE pp. 180-181, p. 48). One with no Year Born is taken as under 30. A bought teacher can't have The Gift, so can't teach a Hermetic Art; they teach as the magi direct two seasons a year (DE p. 180). The form for buying a teacher says so.

**Characteristics:** Young characters (Apprentices, when it is in play). Below 14 the Aging Chart gives every Characteristic a modifier and a smaller Size: under a year -10 and Size -3, down to 12-13 at -1 and Size -1 (Apprentices p. 7). Grows Quickly reads Size one age category higher, Late Bloomer both one lower, and Deft (Characteristic) halves that Characteristic's modifier (pp. 11-12). Size Virtues and Flaws count from the first birthday, and a child is never smaller than Size -3 (p. 10). The worksheet shows the modifier and says what base Size to set; the modifier itself isn't added to the scores.

**Virtues and Flaws:** With Apprentices in play: Child Virtues and Flaws are for characters of 20 and younger (p. 11, Errata p. 82); Inherited ones only for magi and companions, and they must have manifested by 21 (pp. 10-11); no Virtue that grants experience points (Warrior, Educated...) for a character made younger than 14 (p. 10); Turbulence Prone only with The Gift (p. 12).

**Later Life:** Parent's vocation (Apprentices p. 14). From 6 to 14 a child may put xp in the Ability his same-sex parent earns a living by (a Craft or Profession, or a knight's Ride and Single Weapon), even one of a type he couldn't otherwise learn, but his score stays at most half the parent's until 14. "Parent's vocation" on this step names the Ability and the parent's score.

**Apprenticeship:** Standard apprenticeship model (a saga option, with Apprentices in play). A magus still in apprenticeship has, for each year so far, 19 xp for the first 12 years and then 6 xp and 40 spell levels a year for the last 3; xp may buy spell levels and spell levels xp, one for one. A Skilled Parens gives 5 xp and 10 levels a year more, a Weak Parens as much less (Apprentices pp. 10, 14). Parma Magica, Magic Theory and Latin are only advice until Gauntlet. A magus past Gauntlet keeps the Definitive Edition's 240 xp and 120 levels.

A hedge wizard picks their tradition on Concept with **Choose tradition** (once the saga offers one: see [How to play a hedge wizard](help:guide-hedge-magic)), which also adds the Virtues the tradition requires. A magus may choose a Hermetic society there, and a magus of House Ex Miscellanea one of the House's traditions, whose Virtues become his free House Virtues. The tradition's free Virtues, such as a learned magician's Entreat the Powers or a vitki's Minor Virtue from the master, are outside the Virtue and Flaw balance, as a House's are. A crowned king (Church office "King (crowned)") whose race or nationality is Slavic, Magyar or Vlach holds Shapeshifter free, outside the balance, with the forms of a wolf, a lion and a dragon (Against the Dark p. 122); his Magic Resistance 10 is the crown's (DE p. 420). **Tradition Training** then spends the apprenticeship the book gives (a vitki's 290 xp counting the minimums, a folk witch's 200 (her ten years of it, from about age ten, are left out of Later Life), a gruagach's 160, or 64 unGifted), changed by Well-Trained and Poorly Trained; **Open the Arts** gives a Gifted member the tradition's Arts and Abilities at 0; and its checks ask for the minimum scores and any share the Arts must have. The spell levels it gives are shown but not yet learned there. Puissant never counts, since it adds only when the Ability is used. While a character is In Creation, the sheet's Edit Ability and Edit Arts say how much xp came from the worksheet: take that back on the worksheet, not by lowering the total. The checks follow Ars Magica Definitive Edition, Chapter 3: Characters, Detailed Character Creation Summary, for characters, and Ars Magica Definitive Edition, Chapter 6: Covenants, for covenants.

### The Grogs Aging Chart
<!-- help: creation-worksheet-aging-chart -->

A character older than 35 makes an aging roll for each year from 35 before play: **Roll pre-play aging** makes them all, each written in the Diary. While the Grogs book is in play, a grog can instead **Use the Grogs Aging Chart** (a companion too, and a grog promoted from a Line or Sketch, not only a new grog; Grogs p. 65), on the Finishing Touches step: the expected Aging Points for each decade, from the chart in Grogs, Chapter 5 (Aging, the Easy Way, pp. 65-66).

**You type:** the kind of aging, Mild, Average or Harsh (a grog with Mild Aging can only take mild aging, one with Poor Living Conditions only harsh); whether to take the chart's crises (off at first: the book suggests ignoring them for a new character); and, for harsh or mild aging, whether it moves the Ability cap. The line under the form shows each decade and the total as you choose.

**The app works out:**

- the decades: ten years each from the first roll still to make, the last one shorter. Each takes the highest Aging Score of its years: age / 10 (rounded up), less the covenant's Living Conditions (with Mild Aging +1 or Poor Living Conditions -1) and any Longevity Ritual, plus the Virtues that change aging rolls. A score above 10 reads the chart's last row, below 1 its first. A shorter decade takes its share of the chart's points and crises, rounded up;
- with crises: the Decrepitude score rises by one for each crisis, with the points that score needs, and the chart's points are divided by one more than the crises, rounded up (Paul, 45, average aging at Aging Score 5: 5 points, or 5 + 3 = 8 with his crisis). No Crisis is rolled;
- where the points go: a crisis's are spread over the Characteristics highest first; of the chart's, 45% go to the highest Characteristic, then of the rest about half to Quickness or Stamina, 30% to Perception or Presence, 15% to Strength or Dexterity and the remainder to Intelligence or Communication. A Characteristic with more Aging Points than its score (ignoring any minus sign) falls by 1, as with the yearly roll;
- the apparent age: a simple die for each decade, which ages it the whole decade if it is no more than the decade's Aging Points, otherwise by the die;
- the Ability cap: 1 higher after harsh aging, 1 lower after mild, when you chose to move it. The Later Life step's cap and checks use it, and Finishing Touches notes the chart's use.

It is written in the Diary as one entry and can't be undone.

### Moving to In Play
<!-- help: creation-worksheet-play -->

The last step has **Move to In Play**. It lists every check that doesn't pass and asks before moving the record. A covenant with Build Points left over is told how many: moving it to In Play turns them into Mythic Pounds in its Wealth, 10 pounds for each Build Point (the rate money is bought at). The books don't say what becomes of unspent Build Points (without bought money a covenant starts with no significant cash, Covenants p. 56), so turning them into money is the app's own rule, at the rate Covenants gives for buying a starting reserve. To keep the covenant poor, go back and spend them first.

Checks never stop an edit. If the saga has **Enforce creation rules strictly** turned on (the saga's settings), a record that breaks a rule it must follow stays In Creation until that is fixed. Advice never stops it.

**See also:** [Characters group](help:character-group), [The saga](help:saga), [How to create a character, covenant or laboratory](help:guide-creation)

# Import Data
<!-- help: import-data -->

<!-- tui -->
Brings records into the saga from files. Open it from More's **Import** on the saga node.

**You choose:** what to import, then the file: the terminal lists the folders and files of that kind.
<!-- /tui -->
<!-- gui -->
Brings records into the saga from files. Open it from **Import** in the saga page's **Saga Management** chapter.

**You choose:** what to import, then the file, in the desktop's Open window.
<!-- /gui -->

**The app works out:** a preview of what the file adds, shown before anything is added.

### What can be imported
<!-- help: import-data-kinds -->

- **Characters**, **Covenants** and **Laboratories**: a file exported from another saga with Export. The file must hold the kind you chose. The file picker starts in the exports folder.
- **A Whole Saga**: a file written by **Export Saga**. Every covenant, laboratory, character and familiar in it is added beside this saga's own, with their books and devices and the saga's own spells and house rules, as importing each record would; so are its places, neighbours and calendar entries, and its Tribunals, joined to this saga's own of the same name.
- **A Content Pack**: a file written by **Export Pack**. Its Tribunals, covenants, characters, places, neighbours and calendar entries are added, except those this saga already has one of the same name of: those are kept as they are, and the pack's links to them go to this saga's own. See [Content packs](help:export-pack).
- **A Mystery Cult**: a file written by **Export a Cult**. The cult, its Lore, degrees, Scripts and components, joins this saga's own cults on Saga Content; one of a name this saga has already is marked "(imported)", and its founder, a character of the other saga, isn't kept.
- **Books**: a CSV file with a header row. Columns, in any order and any case: name, type, language, author, year_published, description, art, ability, level, quality, tractatus_type, spell, codex, encyclopedia, opus and physical_form; name and type are needed. Rows with the same codex are bound together in one new codex of that name, an encyclopedia when its rows' encyclopedia column says yes. A tractatus's opus can be commentary or correspondence; physical_form is one of exemplar, flap-bound, juvenilia, edition de luxe, treasure-bound, ex libris, holographic, huge codex, unbound or damaged. A level or quality of "var" means the figure is to be set later: the book is imported, highlighted until you edit it to give its numbers, and can't be studied until then. Books imported here go to Unassigned Books.
<!-- tui -->
From a covenant's **Library** tab, More's Import puts them straight into that covenant's library instead.
<!-- /tui -->
<!-- gui -->
**Import**, a button on a covenant's Library, imports books straight into that covenant's library instead.
<!-- /gui -->
An owner or cost column is ignored: the cost is always worked out.
- **Spells**: a CSV file, through the [Import Spells](help:import-spells) helper.

A row that can't be read is skipped, and the preview says why. When a book or spell has the name of one already in the saga, the app asks: Skip, Skip All, Duplicate or Duplicate All. Nothing is added until every question is answered, and cancelling a question imports nothing.

### Importing an exported record
<!-- help: import-data-records -->

What travels with the record comes too, and everything imported gets new ids. Links to records that aren't in the file (a character's covenant, a laboratory's owner, a book's author) are matched by name to the one record of that kind and name in this saga, or dropped; the preview lists which. A character's or laboratory's covenant is the exception when this saga has no covenant of that name: the file carries its name, aura and realm, and the import adds a covenant with just those, so the aura comes too. The preview lists it under Adds as having only its name and aura; fill in the rest on its sheet. A record with the same name as one already here is added beside it. Nothing already in the saga is changed, except that a laboratory with no owner, or a magus with no laboratory, can be linked to the imported partner the file names.

### Exporting
<!-- help: import-data-export -->

<!-- tui -->
More's **Export**, on a covenant's, laboratory's or character's tree node or top panel, writes that record to a file another saga can import.
<!-- /tui -->
<!-- gui -->
**Export**, in a covenant's, laboratory's or character's **Manage** chapter (the last one on its page, with Update from a File and Delete), writes that record to a file another saga can import.
<!-- /gui -->

**You type:** the File to write (it starts in the exports folder, and `.amm.json` is added if you give no `.json` ending), and for a covenant whether to include its laboratories and characters. The line above Export warns when the file exists and will be replaced.

What goes with it:

- a character: their familiar, the enchanted devices they hold, their books and their Diary;
- a laboratory: its books and the devices kept in it;
- a covenant: its books and devices, and optionally its laboratories and characters with their own things;
- the saga's own spells and house rules that these use.

Season plans, season records and lab projects under way stay behind.

**Pictures go too.** An export whose records have pictures on this computer (a character's portrait; with Export Saga or a pack, a Tribunal's maps) is written as a zip, `.amm.zip`, holding the same file and its pictures, so they reach the other computer. Import reads a `.amm.zip` as it reads a `.amm.json`, copying its maps into the maps folder (one already there is kept: a map is named by its picture's bytes) and each portrait under its character's new name. A file sent to a browser is the JSON alone, without its pictures.

<!-- tui -->
**Export Saga**, in More on the saga node, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. In a browser copy, the file downloads instead. Only the storyguide can use it. **Export a Cult** beside it writes one of the saga's own Mystery Cults to a file, for Import's **A Mystery Cult**.
<!-- /tui -->
<!-- gui -->
**Export Saga**, a button in the saga page's **Saga Management**, beside Import, writes the whole saga to one file in the same shape: every record and what it holds. Import it into another saga with Import, **A Whole Saga**. **Export a Cult** there writes one of the saga's own Mystery Cults to a file, for Import's **A Mystery Cult**.
<!-- /gui -->

### Content packs
<!-- help: export-pack -->

A content pack is part of a saga's world written to one file, to fill
another saga with it or start a new saga from it: Tribunals, covenants,
characters, places, neighbours and calendar entries, with their links to
one another.

<!-- tui -->
**Export Pack**, in More on the saga node, writes one. Only the storyguide
can use it; in a browser copy the file downloads instead.
<!-- /tui -->
<!-- gui -->
**Export Pack**, a button in the saga page's **Saga Management**, writes
one.
<!-- /gui -->

**You choose:** the pack's name and file, an optional **Introduction**
(a few paragraphs on what the pack sets up, a blank line between
paragraphs, shown under the pack in Start from a pack), and a tick for each Tribunal,
covenant, place and neighbour it holds. A Tribunal takes everything in
it: its covenants, the places they sit in (and the places round and
inside those), whoever is in those places, and the neighbours that hold
an attitude toward or a link to its covenants. A covenant of a ticked
Tribunal is not asked about. **With their characters** adds the
covenants' characters and laboratories and each Tribunal's Praeco and
Presiding Quaesitor; **With the calendar** the covenants' calendar
entries and the saga's own. The line above Export says what the pack
holds. In **Start from a pack** a pack is listed by its Tribunal
("Rhine Tribunal: 10 covenants, …"), or, when its name doesn't name
the Tribunal, by its name first ("Dammërstein (Rhine Tribunal): 1
covenant, …"), so give a pack a name of its own. The book packs come
first, then the saga starters: ready-made covenants and sagas shipped
with the app, such as Dammërstein. A starter is a pack exported like
any other and put in the app's `data/saga_starters` folder; every pack
there is listed. A starter may name the shipped book pack it is
built on (its `base`, such as `rhine`): Start from a pack brings that in
first, and a starter whose book pack the app doesn't have isn't offered.
A pack whose Tribunals have maps with pictures is written as a
zip, `.amm.zip`, with the maps in it (see Exporting, above).

A Tribunal's meeting under way stays behind, and its Diary comes without
what its entries changed.

**Importing a pack** (Import, **A Content Pack**) asks first what to bring
in, then shows what it adds, what this saga already has of the same name (kept as it is, with
the pack's links pointing to it, and the books, devices and familiars of
those records skipped), what else is skipped (a calendar entry already in
the calendar, or one for a covenant that isn't here), and the links kept
and dropped. Importing the same pack twice adds nothing the second time.

A pack carries its Tribunals' maps and the pins of the records it holds.
Importing it adds them as the pack's: a pin goes in only where the saga
has none of that record on that map, so a pin you moved stays where you
put it and one you took off stays off. A map of a Tribunal the saga
already has joins it, or is matched to its map of the same name.

**Starting a saga from a pack:** the Create a New Saga form offers **Start
from a pack**, listing the packs shipped with the app (one per Tribunal
sourcebook; see [How to start a saga from a sourcebook](help:guide-book-packs))
and then any pack in the exports folder; the new saga begins with
everything in it. A pack built from a sourcebook puts that book in play
when it is imported.

### Printing a record
<!-- help: print-record; gui -->

On the desktop, a covenant's, laboratory's, character's or familiar's
**Manage** chapter has **Print to PDF**. It first asks a few options, then
where to save the file (it starts in the exports folder, named after the
record). The options you choose are kept for next time.

- **Paper size:** US Letter, or A4 outside North America.
- **Spells in the Grimoire** (characters only): **Short**, just each
  spell's Arts and level, Range, Duration and Target, Casting Total and
  Mastery; or **Full description**, which adds each spell's text.
- **Background** (characters only): **Textured parchment**, or **Plain
  white** to save ink.

A character prints as a sheet laid out for paper, not a picture of the
screen. Their name is set in the title lettering, with a bound edge down
the left of each page. Nothing is cut by the page edge: a table that fits
on a page is never split, and a heading always stays with what it heads.
A magus's Hermetic Arts, Grimoire, and Biography & Story each start a new
page; companions and grogs have no magic pages. Each Art and Ability has
its symbol beside it. The Grimoire lists the spells by Form. A Virtue or
Flaw taken more than once is printed once with its count, as **Great
Intelligence × 2**; the screens still show each one. Combat & Condition
follows the published character sheet. It has a box for each Fatigue
level and five for each Light, Medium and Heavy Wound, with the current
ones ticked. It also has blank lines to pencil in weapons, armor and
equipment, with the character's own already filled in. Empty sections
are left off.

Covenants, laboratories and familiars still print their page as it looks
on screen: the header, then each chapter under its name, in the
Scriptorum parchment colours, with the buttons left off. Manage, Planning
and Seasons are left off, since they are for the screen.

The PDF can be printed or sent like any other.

### Giving to another record
<!-- help: give -->

**Give** hands what one record holds to another record of the saga: the
chosen row of a Raw Vis list, a books list (a laboratory's Lab Texts too),
Enchanted Devices, a character's Personal Gear or a covenant's Weapons,
Armor or Items.
<!-- tui -->
It is in More (`m`) on those lists.
<!-- /tui -->
<!-- gui -->
It is a Give button beside the list's Add, Edit and Delete, acting on the row last clicked.
<!-- /gui -->
It asks who gets it and, for vis
and gear, how many. A book changes owner and a device changes holder (a
device's epitome goes with it); gear given in part is split, so both keep
some. Vis goes to a covenant, a laboratory or a magus; a laboratory takes
no gear or silver.

**Give Silver** gives pounds of silver from a character's purse (on
Personal Gear) or a covenant's Wealth to another character or covenant,
so someone leaving a covenant can take silver with them. Both sides'
Diaries record every gift; a covenant files it under Library for a book,
else Purchases & Sales, with the pounds for silver. Only the storyguide
can give.

### Updating a record from a file
<!-- help: import-data-update -->

<!-- tui -->
More's **Update from a File**, on a covenant's, laboratory's or character's tree node or top panel,
<!-- /tui -->
<!-- gui -->
**Update from a File**, in a covenant's, laboratory's or character's **Manage** chapter,
<!-- /gui -->
reads an export of that same record over it: for example after working on a character on another computer. Only the storyguide can use it.

**You choose:** the exported file. It must hold the same kind of record.

**The app works out:** what would change, field by field ("Abilities: 1 added, 2 changed", "Name: Old → New"), and the links in the file it can't match here. Nothing changes until you choose **Update**; a file that changes nothing says so.

What it replaces: the record's own contents, and what travels with it in an export (a character's familiar, devices and books; a laboratory's or covenant's books and devices). What it keeps: the record itself, so everything that points at it still does, and where it sits in this saga (a character's covenant and laboratory, a laboratory's covenant and owner). A covenant's file made with its laboratories and characters updates the covenant only; update each of them from its own export.

**See also:** [Import Spells](help:import-spells), [Unassigned Books](help:unassigned-books), [The saga](help:saga), [How to import and export](help:guide-import-export)

# Import a Content Pack
<!-- help: import-pack -->

The form shown after choosing a pack's file in Import Data, **A Content Pack**: which of its parts to bring in.

A pack's Tribunals and covenants always come in: they are what the rest
hangs on (a region book's pack has covenants and no Tribunal). The rest is a tick each, all ticked to begin with, and a part
the pack holds nothing of isn't asked about:

- **Their people**: the covenants' characters, laboratories and
  familiars, and each Tribunal's Praeco and Presiding Quaesitor.
- **Generated stats for magi**: asked only while their people are
  ticked. A book pack gives full stats to the magi its book describes
  but prints no stat block for. Those stats are not an official
  write-up: they are inferred from the book's description by the
  creation rules, and each such magus's Biography says so. Untick it to
  bring those magi in as the book's sketches; the magi the book does
  print stat blocks for come in full either way.
- **Places and regiones**: the places the covenants sit in, the places
  round and inside those, and their regio levels.
- **The mundane world**: lords, towns, the Church, universities, factions
  and threats.
- **Code, cases and fines**: each Tribunal's Peripheral Code,
  docket and fines.
- **The history**: each Tribunal's Diary, each covenant's Diary (where a
  pack with no Tribunal keeps its history), and the calendar entries.

Then each of the pack's stories (its threats) that this saga doesn't
already have is a **Begin** tick, shown while the mundane world is
ticked. A story left unticked comes in **dormant**: listed among the
Region's Threats as Dormant, it reaches no stage and nothing of it
comes due until **Begin This Story** in its More starts it.

If the saga already has one of the pack's stories, told differently, as
the Fifth Crusade is in the Cradle and Nile packs, a **Use this book's**
tick asks which to keep. Left unticked, the saga keeps its own.

The line under the ticks says what the pack brings with the ticks as they
are. **Preview** then shows the import as above. What a left-out part
held is matched by name to this saga's own (a covenant's place, a
Tribunal's Praeco) or the link is dropped, and the preview lists which;
a covenant whose place is left out sits nowhere until you place it.
Starting a saga from a pack brings everything, and asks which of its
stories to begin in the same way.

A place, threat, faction or lord this saga already has is kept as it
is, with one exception: the pack's roll tables on it that the saga's
has none of the same name of (in any case) are added to it, and the
preview says so ("1 roll table to The valley of Durenmar"). So a saga
starter can bring "Rumours about Dammërstein" to a Rhine Tribunal place.
A table the saga has is never overwritten, and importing the pack again
adds nothing.

A saga starter built on a book pack, imported into a saga without that
book's Tribunal (Dammërstein into a Transylvanian saga), first asks
**First bring in the Rhine Tribunal**, ticked, with the book pack's own
choices under it, so it can come in lightly. The preview shows the book
pack's import, then the starter's over it. Untick it and the starter
comes in alone, and the preview says that its tables for the Tribunal's
records come in on records of their own. A saga that has the Tribunal
is not asked.

Importing a pack again, or a newer copy of it, leaves every record the
saga already has as it is and adds the rest: see [Adding a book to a saga
you already have](help:guide-book-packs-add).

**See also:** [Content packs](help:export-pack), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

# Import Spells
<!-- help: import-spells -->

Explains what a spell CSV file looks like before you choose one. Tick **Save an example CSV instead** to save one to start from, rather than choosing a file. The spells imported become the saga's own spells, which you can edit on [Spells](help:tab-content-spells).

<!-- tui -->
Open it from More's Import on the saga node, then Spells.
<!-- /tui -->
<!-- gui -->
Open it from **Import** in the saga page's Saga Management chapter, then Spells.
<!-- /gui -->

**You type:** a CSV file with a header row. Columns, in any order and any case:

- **name**, **technique** and **form** (required). A Technique or Form can be written in full or abbreviated (Cr, Ig...).
- **level**: a number, or Gen (or blank) for a General spell.
- **requisites**: extra Arts, for example Rego, Corpus.
- **range**, **duration** and **target**, in full or abbreviated (Per, Mom...).
- **ritual**: yes or no (blank is no).
- **base_level**: the guideline level before Range, Duration and Target (optional).
- **description** and **source**.

**The app works out:** a preview of the spells found, the rows skipped and why, and any columns it didn't use. Names already in the saga are compared in any case, and the app asks about each one (Duplicate, Duplicate All, Skip or Skip All).

### The buttons
<!-- help: import-spells-buttons -->

- **Choose CSV File** goes on to pick the file.
- With **Save an example CSV instead** ticked, it writes `spells_example.csv` (numbered if it exists) to the folder the app was started from, with two example spells, instead. Edit it, then choose it to import.
- **Cancel** closes the helper.

**See also:** [Spells](help:tab-content-spells), [Import Data](help:import-data), [How to import and export](help:guide-import-export)

## Follow an Avenue
<!-- help: follow-avenue -->

Plans the Initiation season that follows an avenue to its station
(Houses of Hermes: Mystery Cults pp. 59-60). Choose the avenue (the next
on his path, or the next on another path, which steps onto it), the guide
(the guide the House provides, at Presence + House Criamon Lore 6 as the
printed Scripts assume; a character of the saga with House Criamon Lore,
one not of the House shown as unusual; or a ghostly Primus at the Cave of
Twisting Shadows, Lore 9, p. 60), whether the Path of Seeming's third
avenue gives up his talisman in place of the special time and place (the
same +3, not an added one, p. 64) and the season. A head bound in infancy
for the path, set on Change Path, adds +3 to its first station only
(p. 51).

The Avenue shows the guide's Presence + Lore + the Script against the
Target (21, less his past Ordeal's reduction), whether his House Criamon
Lore is enough (the station's place + 1), the avenue's story (a
psychodrama: failing, he may try again; utter failure may bring a
Twilight check, p. 59) and what success brings. Plan puts an Undergo an
Initiation season on Planning (it replaces a plan for that season); when
it is played, the season adds the station's Virtue and its Ordeal's
Flaws (a Major Pious replacing his Vow, say), and the Virtues some
stations bring with them: Clear Thinker, Common Sense and Keen Vision
(Differentiation of Seeming; trade Keen Vision for another sense by hand,
p. 64), the Gentle Gift, or the Blatant Gift lifted to an ordinary Gift
(Service to Harmony, p. 70), and Free Expression and Inspirational
(Expression, p. 71), none twice. It keeps the season on
Stations, and reminds you to add the new stigma. A Flaw the book only
describes (Incompatible Arts, "the equivalent of a Supernatural
Nuisance") is noted for you to add by hand.

## Change Path
<!-- help: change-path -->

The path he walks (or "as his stations show"), his guide, a ghostly
Primus's Presence (the one he had in life; his House Criamon Lore is 9,
p. 60), and the path a head bound in infancy (or a like modification)
suits, +3 to its first station only (a cone suits Seeming, a
double-lobed skull the Body, p. 51), with notes. Changing path sets aside
his stations on the old one (p. 58). The Path of the Mirror is offered
only to the Primus (pp. 57, 59): a magus whose Hermetic background names
himself as the House's Primus.

## Draft the Charter
<!-- help: draft-charter -->

A season's work by one side's notaries (Transforming Mythic Europe
p. 36): the principal notary's Intelligence + Civil and Canon Law + a
stress die is that side's Charter Strength. Tick **In England** for an
English charter: its notaries use Common Law instead, and only it; the
tick is kept on the lord (his form has it too). There are 3 botch dice,
one fewer for each notary beyond the first; a botch leaves the strength
at 0, no legal defence.

## Seek a Loophole
<!-- help: seek-loophole -->

A season examining the charter and its legal texts, then Intelligence +
Civil and Canon Law (Common Law, and only it, for a charter in England)
+ a stress die against the other side's Charter Strength (Transforming
Mythic Europe p. 36). Higher finds a loophole: legal grounds to break
one or more of its provisions, noted on the lord. The other side's
strength must be drafted (or typed) first.

The book gives the search no botch dice; the app rolls one. A botch is
a total of 0 and something goes wrong (DE p. 7), as the storyguide
decides: a false loophole the searcher believes in, say, or the other
side learning of the search.

# Delay or Hasten
<!-- help: threat-delay -->

Something the troupe did (or failed to do) pushes a threat later or
brings it sooner, without editing each stage.

- **A threat moving by fixed dates**: give the seasons later (below 0,
  sooner). Every stage still to come moves by that much; the dates you
  typed stay as they are, and the threat's Edit shows the delay so far
  in Delayed by. A stage already marked Happened, Stopped or Turned
  doesn't move.
- **A threat moving along a track or an omen count**: give the steps
  back (below 0, on). Its position can't go below 0.

**You type:** how far, and why.

**The app works out:** the new dates or position, and a line in the
threat's [Diary](help:tab-nb-threat-diary) saying what moved it and why.
To undo it, Delay or Hasten again the other way, or Edit the threat.

**See also:** [A threat](help:tab-nb-threat), [How to set up a threat's clock](help:guide-threat-clock)

# Take Up the Tale
<!-- help: take-up-tale -->

The troupe picks a story up again: a chapter of what it did, met or
avoided, dated by season, so the Diary keeps a record of each time.

- **On an open story** (a covenant's Diary, the Region's
  [Open Stories](help:section-region-stories), or
  [Needs You](help:section-attention)): the chapter is an entry of its
  own in the same covenant's Diary, of the category Chapter, naming its
  story. A story grown into a threat is taken up on the threat instead.
- **On a threat** (its page's More, or a threat's row on Needs You):
  the chapter goes in the threat's [Diary](help:tab-nb-threat-diary)
  and each troupe covenant's.
- **How the Tale Ended**: marking an open story Resolved asks for its
  last chapter, the same form; Cancel leaves it resolved with none.

**You type:** the year and season (this one, unless you change it) and
what the troupe did.

**The app works out:** the chapter's Diary entry; the story's (or the
threat's) details then list its chapters, oldest first, a grown story's
going on into its threat's.

**See also:** [How to follow a story from its start to a threat](help:guide-story-hook), [Diary tab](help:tab-cov-diary)

# Grow into a Threat
<!-- help: grow-story -->

An open story the troupe left alone becomes a threat of the Region:
a story that grows on its own (see [A threat](help:tab-nb-threat)).

**You type:** the threat's name (the story's, unless you change it),
its antagonist, how it moves (by fixed dates, a track or an omen
count), and whether it begins now or waits, dormant, until Begin This
Story.

**The app works out:** the threat, its summary the story's words and a
link to the covenant whose Diary kept the story; the story is marked
**Grown into a threat**, so it leaves Open Stories; and the threat's
Diary says where it came from. Add its stages on its page.

**See also:** [Open Stories](help:section-region-stories), [How to follow a story from its start to a threat](help:guide-story-hook)

# Host for Players
<!-- help: host-for-players-window; gui -->

Open it from **Host for Players** in the saga page's **Saga Management**
chapter. It is the one place you host the saga and manage who joins, and
it stays open beside the game: you can keep playing while it is open.

At the top, choose how **players join**:

- **Armarius on their own computers, over the internet (Remote seats).**
  Each player runs the app; it connects through a tunnel you set up
  yourself, such as Cloudflare Tunnel.
- **A browser or terminal, on your private network.** The older way, over
  Tailscale or ZeroTier: see [How to host a saga](help:guide-hosting).

Under it, the window says whether the saga is hosted, with **Host** or
**Stop Hosting**. To switch the way players join, stop hosting first.
Closing the app while the saga is hosted asks first, as it ends every
player's connection.

For Remote seats it also shows the host's **six words**, which you read
aloud on your group's call, and four pages, chosen on the rail at the
left: Players, Requests, Seats and Log. The window looks for new requests
every few seconds; the title, and Requests on the rail, count those
waiting.

### Players
<!-- help: remote-seats-players; gui -->

Everyone who may sign in to the saga, with their role, the characters
they play, and whether they can sign in from a Remote seat (**✓ Ready**,
or why not). **Add**, **Edit** and **Delete** work as on Saga Content's
[Players](help:tab-content-players): a player's form has a **Plays** tick
for each of the troupe's characters (several players may tick the same
one). A passcode needs at least 14 characters: a few words they'll
remember, such as "grey owl over the mill", are easiest. Choose a player
and **Issue Invite** to invite them.

While the saga has players, your own window picks up what they save every
few seconds: the page is drawn again, with a note at its foot such as
"Anna changed Leandro; reloaded." It waits while you have a form or
question open, so nothing you are typing is touched. A player's change
reaches only what is theirs to change (their characters, those
characters' labs, familiars and season plans, and the covenants if you
gave them covenant rights), and it never removes anything hidden from
them, such as a Secret. Where you and a player changed the same thing,
the later save is kept.

### Host for Remote Seats
<!-- help: host-remote-seats; gui -->

**Host**, with Remote seats chosen, asks:

- **Tunnel address:** the https address your tunnel gives you, such as
  `https://saga.example.com`, with nothing after the name.
- **Tunnel:** Cloudflare Tunnel, or another (ngrok, Tailscale Funnel...).
  It tells the app where the tunnel says each player's own address is, so
  the limits on connections count each player apart.
- **Port:** the port on this computer the tunnel points at (8790 unless
  another program has it).

The line under the fields says what to point the tunnel at
(`http://localhost:PORT`) and the address the Invites will carry. The app
listens on this computer alone; only the tunnel reaches it. The choices are
kept for the saga, outside the saga file.

### Issue Invite
<!-- help: issue-invite; gui -->

On **Players** (with the player chosen) or **Requests**, **Issue Invite**
asks which Player to invite. Only Players whose passcode has at least 14
characters, set since this rule began, are offered; the others are listed
with the reason. A storyguide's sign-in is not offered.

The window then shows the line to send the player by chat or email, with a
**Copy** button, and the host's six words to read them on the call. The
line works once, on one device, for 24 hours. It is shown only then: the
app keeps no copy of the code, so if you close it unsent, issue another.

### Requests
<!-- help: remote-seats-requests; gui -->

When a player's app uses an Invite, their device waits here: the player,
the device's name, its **three words** and when it asked. Ask the player to
read you the three words their screen shows; **Approve** asks whether they
match before it gives the device a seat. **Reject** turns it away; its
Invite is spent. A request not decided within an hour lapses.

### Seats
<!-- help: remote-seats-list; gui -->

Each device given a seat: the player, the device, its words, when it was
last used, and when it expires if unused (or when it ended).

- **Revoke** ends the chosen seat. Its connection is cut within a second,
  and the device needs a new Invite to come back.
- **Idle Expiry** sets how many days a seat may go unused before it stops
  working (90 unless changed), for this saga.
- **Rotate Host Key** gives the host a new key. Every Invite, waiting
  request and seat ends at once, and each player needs a new Invite and
  hears the new six words. If the saga is hosted, it starts again with the
  new key.

### Log
<!-- help: remote-seats-log; gui -->

What happened to Remote seats, newest first: Invites issued and redeemed,
requests approved or rejected, sign-ins, wrong passcodes and lock-outs,
reads of the saga, each record a player changed (and each change refused),
revoked and expired seats, and new host keys. **Show** narrows it to one
player. The log records who and when, never a passcode or a code, and keeps
a year. It is kept outside the saga file, so players never receive it.

**See also:** [How to host a saga](help:guide-hosting), [Players](help:tab-content-players)

# Join a Saga
<!-- help: join-game; gui -->

Join a saga your storyguide hosts on their own computer, from your own
copy of Armarius, over the internet. Click **Join a Saga** on the title
page or the Sagas shelf. The first time takes a few steps; after that you sign in with your
passcode.

### The first time
<!-- help: join-game-first; gui -->

1. **Paste the invite** your storyguide sent you (a line that begins
   `ARM1`). It works once, on one computer, for a day.
2. **Check the six words.** Your storyguide reads six words out on your
   call. If they match the six on your screen, click **They match**. If
   they don't, click **They don't match**: the invite may have been
   changed on its way to you, so nothing is sent, and you should ask for
   a new one, by another way if you can.
3. **Name this computer** (its own name to start with), so your
   storyguide knows which device is asking, then **Ask for a Seat**.
4. **Read your three words** to your storyguide. When they match what
   their screen shows, they let you in; the window moves on by itself.
5. **Your passcode**, the one your storyguide gave you (at least 14
   characters). The saga opens.

The saga then stays on your shelf, marked **Hosted elsewhere**.

### Coming back, and leaving
<!-- help: join-game-again; gui -->

Click the saga on the shelf and type your passcode. If the connection
drops while you play, the app connects again by itself; changes you made
meanwhile are sent once it's back (closing the app before then asks
first). If your seat has ended (your storyguide revoked it, you didn't use
it for a long while, or they gave their host a new key), the app says so:
ask for a new invite. **Leave Saga** on the saga's card forgets this
computer's seat; to come back you'll need a new invite.

While you play, your pages show what you may see, and you change only
what's yours (your characters, their laboratories, familiars and season
plans, and the covenants if your storyguide gave you covenant rights).
Every few seconds your pages pick up what others saved, with a note at
the window's foot. When your storyguide advances the season, your
window turns the season's dial too. If someone else has the record you're
on open, their name shows beside the trail ("◉ Bruno is here too"), so
you can agree who changes what.

### What a host can and can't see or do
<!-- help: what-a-host-sees; gui -->

- **Your saga, as you may see it, is all you receive.** Secrets you
  haven't been told, places and people you don't know of, and other
  things your storyguide keeps to themselves never leave their computer.
- **Nothing is stored on your computer** but this device's seat, kept in
  your computer's own keychain (Windows Credential Manager, macOS
  Keychain or a Linux Secret Service). The saga stays in memory while
  it's open and is gone when you close it.
- **Your passcode never crosses the internet**, not even scrambled: your
  app proves it knows it, in a way that is useless to anyone who
  overhears, and to anyone pretending to be the host.
- **The six words are your check that you reached your storyguide**, not
  someone in the middle. Compare them on your call each time you join
  from a new invite.
- **What your storyguide's computer sees:** your internet address (as any
  website does), when you play, and the changes you make, each recorded
  in their log by which record it touched (never what you typed). Their
  tunnel company sees that you connected, not what passed.
- **What it can't do:** reach anything on your computer. The app takes
  only saga records from it and runs nothing it sends. Every record is
  checked against the form the app's records have before it is used:
  anything else is refused, and the app names the field it couldn't read.

**See also:** [How to host a saga](help:guide-hosting)
