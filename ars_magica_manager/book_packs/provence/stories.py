"""The saga's stories, in paraphrase: each a threat whose stages lay out
how it unfolds if the troupe ignores, stops or turns it.

Under way in 1220: the Albigensian Crusade, by dated stages from the
south's recovery in 1220 to the Treaty of Paris in 1229 (the book tells
the war only up to 1219, so the later stages follow history in general
terms, each marked as what happens if history holds); The Serpent's
Venom, the Praeco Dama and her familiar Maju, in the book's two stages
(Sins of the Past, Schemes of the Present); the Six Deadly Spirits loose
since the English interdict; the followers of the Procrustean League;
Tolosa Paratge's war with itself; and the Coenobium's growing hegemony.
The Tribunal at Glanum in 1221 is a saga frame of dated stages, the
meeting's agenda in order.

Dormant until the storyguide begins them: the Adulteration of Flambeau,
sealed behind the Iron Door of Val-Negra (with the lost covenant as a
dungeon frame), and the Pyrenean covenants' secession at the Grand
Tribunal of 1228.

`finish` ties the stories to the covenants, magi, places and factions the
other parts made, found by name, and closes the Tribunal's summary with
the hooks too slight for a threat of their own (Fraxinetum Redux and the
Drac of Beaucaire under Secrets)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, Secrets, dormant, more_secrets, paragraphs, titled

if TYPE_CHECKING:
    from . import Provence

S = Builder.stage
DATED = "Fixed dates"


def build(provence: Provence) -> None:
    _crusade(provence)
    _serpent(provence)
    _spirits(provence)
    _procrustean(provence)
    _tolosa(provence)
    _coenobium(provence)
    _glanum(provence)
    _adulteration(provence)
    _secession(provence)


# -- the war --


def _crusade(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_crusade"] = b.threat(
        "The Albigensian Crusade",
        summary=paragraphs(
            "The war on the southern heretics has run for eleven years. "
            "The legate's murder by the Rhône in 1208 brought the crusade; "
            "Béziers was sacked and its people slaughtered in 1209, "
            "Carcassonne yielded and its viscount died a prisoner, and "
            "Simon de Montfort, a minor knight of the Île de France, took "
            "the Trencavel lands. Minerve, Termes and Lavaur followed; the "
            "massacre at Montgey in 1211 brought down the Tremere covenant "
            "of Lariander, and Mistridge fell to Tres's Wizard's War. At "
            "Muret in 1213 King Pedro of Aragon died and the southern host "
            "broke; Simon entered Toulouse in 1215.",
            "Then the tide turned. Count Raimond VI slipped back into "
            "Toulouse in 1217, Simon was killed by a stone from the walls "
            "in 1218 (some say from one of Tres's engines), and the royal "
            "expedition of 1219 butchered Marmande but failed before "
            "Toulouse. In 1220 the count is winning back his county. Amaury "
            "de Montfort claims his father's titles, with his mother Alice "
            "still a shrewd hand in the war, but his domain is crumbling. "
            "There are no borders: castles of either side stand within "
            "sight of one another and garrisons of both are scattered "
            "across the land.",
            "A saga frame as well as a threat: the crusade played as a "
            "war, in which characters of every faith and loyalty meet, "
            "change sides and betray one another. Who holds each town in "
            "1220 is in that place's notes.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The book tells the war only to 1219. The stages after 1221 "
                "follow history in broad strokes; a troupe that wants the south "
                "to win, or the war to end sooner, changes them.",
            ),
        ],
        antagonist=(
            "The crusaders: Amaury de Montfort, the papal legates, and in time "
            "the French crown"
        ),
        moves=DATED,
        stages=[
            S(
                "The count's recovery",
                year=1220,
                season="Summer",
                clues=(
                    "Southern lords take back castle after castle, and faidits, "
                    "the knights the crusade dispossessed, ride home to claim "
                    "their lands. Unpaid crusader garrisons hold on in "
                    "isolated towers. Routiers and camp followers rob the "
                    "roads; a Redcap died of their blows on the Via Domitia."
                ),
                ignored=(
                    "The patchwork war grinds on around any covenant in the "
                    "Toulousain, and both sides come asking for oaths, food "
                    "and shelter."
                ),
                stopped="The covenant stays hidden and the fighting passes it by.",
                turned=(
                    "A returning faidit, or a crusader captain, owes the "
                    "covenant his castle, and may pay in land or rights."
                ),
            ),
            S(
                "The old count's death",
                year=1222,
                season="Summer",
                clues=(
                    "If history holds, Raimond VI sickens and dies still under "
                    "the Church's ban, and the clergy will not bury him in "
                    "consecrated ground. His son Raimond VII, already the "
                    "south's best captain, takes up the war."
                ),
                ignored="The son carries on the reconquest with fresh energy.",
                stopped=(
                    "The old count is reconciled before he dies, and one "
                    "bitter grievance of the south is laid to rest."
                ),
                turned=(
                    "The covenant wins the young count's goodwill, through "
                    "healing or counsel, and must answer for it if the "
                    "Quaesitores hear."
                ),
            ),
            S(
                "The Montfort claim gives way",
                year=1224,
                season="Spring",
                clues=(
                    "If history holds, Amaury runs out of silver and men, "
                    "leaves Carcassonne, and hands his southern claims to the "
                    "King of France; the Trencavel heir comes home. Deserters "
                    "from his garrisons sell their swords on the roads."
                ),
                ignored=(
                    "The crusaders' domain falls apart, but its claim now "
                    "rests with a crowned king rather than a struggling heir."
                ),
                stopped=(
                    "Amaury finds money and allies, and the war stays a "
                    "southern affair a while longer."
                ),
                turned=(
                    "The covenant gains from the vacuum: a castle, a market or "
                    "a vis site on land that no lord now holds."
                ),
            ),
            S(
                "The king takes the cross",
                year=1226,
                season="Summer",
                clues=(
                    "If history holds, a council of the Church condemns the "
                    "young count again, the crusade is preached anew across "
                    "the north, and the French king leads it himself. Town "
                    "after town submits before his army arrives; Avignon on "
                    "the Rhône shuts its gates and is besieged all summer, "
                    "and the king dies on the road home in the autumn."
                ),
                ignored=(
                    "The royal host comes down the Rhône; Arelat, spared until "
                    "now, sees war, and the Coenobium's holdings at Avignon "
                    "lie under its siege lines."
                ),
                stopped=(
                    "The crusade is delayed or turned aside, and the south "
                    "gains years to make its peace."
                ),
                turned=(
                    "The covenant shelters a town or a lord through the siege, "
                    "or quietly helps the royal army, and is owed by whoever "
                    "wins."
                ),
            ),
            S(
                "The burning of the fields",
                year=1228,
                season="Summer",
                clues=(
                    "If history holds, the king's lieutenant wages a war of "
                    "attrition, burning crops and uprooting vineyards around "
                    "Toulouse season after season. The same year the Grand "
                    "Tribunal meets, and magi of the south carry their "
                    "quarrels there."
                ),
                ignored="Hunger, not battle, wears the south down.",
                stopped="The ravaging is checked and the harvest saved.",
                turned=(
                    "The covenant feeds the countryside, and wins its "
                    "loyalty, at the risk of a charge of interference."
                ),
            ),
            S(
                "The Treaty of Paris",
                year=1229,
                season="Spring",
                clues=(
                    "If history holds, the count submits in Paris: his "
                    "heiress is to marry the king's brother so the county "
                    "passes to the crown in time, Toulouse loses its walls, a "
                    "university is founded there to teach sound doctrine, and "
                    "a council of the Church sets about hunting heresy town "
                    "by town."
                ),
                ignored=(
                    "The south is bound to France. The Perfecti flee to "
                    "mountain refuges, the Hermetic faidits lose their cause, "
                    "and the Church's inquisitors begin asking questions."
                ),
                stopped=(
                    "The war goes on, or ends on terms that leave the south "
                    "its own lords."
                ),
                turned=(
                    "The covenant has placed itself well with the new order, "
                    "and gains from the peace."
                ),
            ),
        ],
    )


# -- the Praeco's secret --


def _serpent(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_serpent"] = b.threat(
        "The Serpent's Venom",
        summary=paragraphs(
            "A saga frame, the book's central one, and a threat. Dama of "
            "Merinita, the Praeco, is the Tribunal's oldest maga: "
            "respected, even by the Mercurians, and known to favour "
            "women. She founded the Matres and Matrones, a cult that "
            "advances women, draws on the Basque folk witches, the "
            "region's love of the female saints and its Black Madonnas, "
            "and the memory of Eleanor of Aquitaine. She lives apart from "
            "Castra Solis in a tower near Mimizan, an eerie and "
            "unwelcoming place that she says keeps crusaders away.",
            "Two Presiding Quaesitors have gone in ten years. Senex "
            "vanished in 1210 on some errand to a village, and Tibaut, "
            "who took his office, died in 1219. Tibaut's filia Beatrice "
            "holds the office until the Tribunal of 1221 confirms her, on "
            "Dama's suggestion.",
        ),
        secrets=[
            titled(
                "Who killed the Presiding Quaesitors",
                "Dama killed them both, Senex and Tibaut.",
            ),
            titled(
                "The death of Senex",
                "Senex had turned his eye on Dama's cult and slipped into "
                "Mimizan while she was away at an akelarre with the sorginak; "
                "she came back early and found him in her sanctum. Her Aegis, "
                "her spell Revoke the Protection of Bonisagus and Maju's venom "
                "killed him, and Maju, as a drake, ate the body.",
            ),
            titled(
                "Whether Senex's killing was lawful",
                "Senex had forfeited his immunity by entering Dama's sanctum, "
                "so the killing was lawful, but she hid it to keep the "
                "Quaesitores away from the cult.",
            ),
            titled(
                "Tibaut's inquiry",
                "Tibaut found the start of Senex's inquiry in his notes, came "
                "to believe him dead, told Beatrice so, and from 1217 looked "
                "into the Tribunal's cults.",
            ),
            titled(
                "Tibaut's letter",
                "Tibaut's sealed letter to Beatrice still lies in the satchel "
                "of a Redcap who died of a camp followers' ambush on the Via "
                "Domitia.",
            ),
            titled(
                "Luc's warning",
                "Luc of Ara Maxima Nova, after losing a certamen to Tibaut over "
                "his questions, told Dama which Arts he had used.",
            ),
            titled(
                "The death of Tibaut",
                "Dama lured Tibaut into an abandoned house near the road to "
                "Foix where Maju waited as a viper; he staggered out into the "
                "road, crusader knights carried him to the Abbey of Saint "
                "Hilaire thinking him a monk, and he died there of the poison.",
            ),
            titled(
                "Tibaut's belongings",
                "Tibaut's belongings sit in a locked chest in the abbot's "
                "office at the Abbey of Saint Hilaire; the crusaders, deciding "
                "he had been a Cathar, came back and raided the abbey.",
            ),
            titled(
                "What Tibaut may have told",
                "Dama does not know what Tibaut told the knights or the monks.",
            ),
            titled(
                "What Maju is",
                "Maju is the real enemy. The Gauls worshipped it as Teutates "
                "and drowned captives for it in the lake at Mimizan; among "
                "the Basques it wore the face of Sugaar, and Dama still calls "
                "it so before them.",
            ),
            titled(
                "Maju's hold on Dama",
                "Maju bound Dama's spirit as she bound it, and has turned each "
                "of her works a little: the cult's upper circle is a coven of "
                "tainted witches close to diabolism, and Dama drove her filia "
                "Marie away over it.",
            ),
            titled(
                "Maju becoming a demon",
                "Maju sets women against men and the Black Madonna against the "
                "God of the Dominion, and its sins are slowly making it a "
                "demon, which cloaks the Infernal aura at Mimizan as Magic or "
                "Faerie.",
            ),
            titled(
                "The Coenobium's support",
                "Dama bought the tacit backing of Alazais and the Coenobium "
                "with a secret Longevity Ritual for the Chief Redcap's "
                "mundane companion.",
            ),
            titled(
                "Dama's failing ritual",
                "Dama's own Longevity Ritual is failing; she must renew it "
                "before 1232.",
            ),
            titled(
                "Storyguide Notes",
                "Maju in its final form: a Duke of False Gods, Infernal Might 45.",
            ),
        ],
        antagonist=("Maju, the Praeco Dama's familiar: a faerie turning into a demon"),
        realm="Faerie",
        stages=[
            S(
                "Sins of the Past",
                at=1,
                clues=(
                    "At Beatrice's confirmation in 1221 there is talk that "
                    "Senex met foul play. A Redcap's remains lie by the Via "
                    "Domitia with a sealed letter. Tibaut's chest waits at "
                    "Saint Hilaire, and his lab notes in his sanctum. A "
                    "Quaesitor trained by Senex or Tibaut comes to find the "
                    "truth; Protendus of Tremere, hunting Tytalan intrigue, "
                    "stumbles on the Praeco instead and wants Tremere help, "
                    "for a price in sigils."
                ),
                ignored=(
                    "Beatrice is confirmed without knowing, and Dama invites "
                    "her into the cult before the letter reaches her, making "
                    "her complicit."
                ),
                stopped=(
                    "The truth comes out at Tribunal: Senex's death was "
                    "lawful, Tibaut's was murder, and the Praeco stands "
                    "accused."
                ),
                turned=(
                    "The characters keep what they know, and hold the most "
                    "powerful maga of the Tribunal in their debt or their "
                    "grip."
                ),
            ),
            S(
                "Schemes of the Present",
                at=2,
                clues=(
                    "Maju whispers that time is short: Dama's Longevity "
                    "Ritual is failing, Marie is estranged, Mimizan small "
                    "beside Oriande's court in the Médoc, and the cult too "
                    "small to outlive her. She recruits harder among the "
                    "sorginak and the coastal villages, tests would-be "
                    "initiates with odd questions, and seeks vis from "
                    "enchanted items, perhaps through a newly arrived "
                    "Verditius, which may betray her part in Senex's end."
                ),
                ignored=(
                    "Either the cult becomes a quiet Black Madonna devotion "
                    "that forgets its founder while Dama ages and grows "
                    "desperate, or she defeats those who pry, Maju becomes a "
                    "demon and carries her soul to Hell, the sorginak break "
                    "away from the Order, and the Tribunal suffers another "
                    "blow."
                ),
                stopped=(
                    "Shown the rot in her familiar and convinced that her "
                    "life has left a legacy after all, Dama is redeemed and "
                    "helps destroy Maju."
                ),
                turned=(
                    "If the investigation is bungled, Maju kills Dama and "
                    "takes the cult, or turns it on the characters in a "
                    "hidden war of witches; the characters who survive it "
                    "hold the cult's secrets."
                ),
            ),
        ],
    )


# -- the demons of the interdict --


def _spirits(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_spirits"] = b.threat(
        "The Six Deadly Spirits",
        summary="When the pope laid England and its lands under interdict in "
        "1208, Gascony's churches stood closed for six years, and in the "
        "wild country off the pilgrim roads a band of demons took root. "
        "Infernal auras are common there still, and in many villages the "
        "Dominion holds by day and the Infernal by night; no Divine aura "
        "below 7 is older than the interdict.",
        secrets=[
            titled(
                "How the spirits work",
                "Each of the Six Deadly Spirits descends on a community, "
                "possesses its leading folk and leads the rest into its own sin "
                "until the place lies under an Infernal aura; a host who dies "
                "unrepentant comes back as a lesser demon or a ghost.",
            ),
            titled(
                "Cenodoxus Superbia",
                "Cenodoxus Superbia, Lord of Pride and Envy, is still in "
                "Gascony, where he plays the muse to craftsmen and spreads envy "
                "through whole guilds.",
            ),
            titled(
                "Adrian, the Voice of Safety",
                "Adrian, the Voice of Safety, is still in Gascony: a troubadour "
                "preaching the sloth of standing aside from the war.",
            ),
            titled(
                "The Tempter of the Way of St. James",
                "Julian or Julia, the Tempter of the Way of St. James, is still "
                "in Gascony.",
            ),
            titled(
                "Greed at St. Thibery",
                "Greed has gone to the bridge of St. Thibery on the Via Domitia "
                "as the Old Man of the Bridge, who lures travellers into the "
                "river after a phantom treasure.",
            ),
            titled(
                "Gluttony and Wrath",
                "Gluttony and Wrath march with the crusaders in the Narbonnais "
                "and the Toulousain, feeding both armies' vices.",
            ),
            titled(
                "Storyguide Notes",
                "Cenodoxus Superbia: a Vessel of Iniquity, Infernal Might 40. "
                "Adrian: a Spirit of Deceit, 30. Julian or Julia: 15. The Old "
                "Man of the Bridge: 15.",
            ),
        ],
        antagonist="Six demons of the deadly sins, loose since the interdict",
        realm="Infernal",
        stages=[
            S(
                "A village gone wrong",
                at=1,
                clues=(
                    "A Gascon village near the covenant turns sour: its "
                    "reeve grows proud, its smith envious, its young men "
                    "idle, and at night the church feels cold. A handsome "
                    "stranger advises the best craftsman; a troubadour sings "
                    "that the war is no one's business."
                ),
                ignored=(
                    "The village falls under an Infernal aura, and its dead "
                    "do not rest."
                ),
                stopped="The possessed are freed and the demon driven off.",
                turned=(
                    "The covenant learns the demon's name and nature, a hold "
                    "over it, or a clue to the others."
                ),
            ),
            S(
                "The old man of the bridge",
                at=2,
                clues=(
                    "Travellers drown at the bridge of St. Thibery, each "
                    "last seen talking with an old peasant carrying a load "
                    "of firewood, who offered to mind their goods while they "
                    "dived for coins glinting in the river."
                ),
                ignored="The Via Domitia gains a deadly crossing.",
                stopped=(
                    "The Old Man is caught counting coins thrown at his feet, "
                    "his weakness, and banished."
                ),
                turned="The demon's purse holds three pawns of Vim vis.",
            ),
            S(
                "Gluttony and Wrath in the camps",
                at=3,
                clues=(
                    "Atrocities and drunken excess spread in both armies; a "
                    "garrison near the covenant runs riot, and the cruelty "
                    "spills onto the countryside."
                ),
                ignored=(
                    "The war grows crueller, and the Infernal takes root in "
                    "the places it scars."
                ),
                stopped="The two demons are found among the soldiers and cast out.",
                turned=(
                    "The covenant uses what it learns to sway a captain, at "
                    "the price of dealing with the Infernal."
                ),
            ),
            S(
                "The spirits notice the covenant",
                at=4,
                clues=(
                    "A companion is advised by a charming stranger; a grog "
                    "turns idle, another lustful; a magus's craft is praised "
                    "beyond reason by someone who knows too much of his work."
                ),
                ignored="One of the covenant is corrupted, or dies unrepentant.",
                stopped="The tempter is unmasked before it takes hold.",
                turned=(
                    "The covenant traps the demon, and learns the others' "
                    "plans from it."
                ),
            ),
            S(
                "All six descend",
                at=5,
                clues=(
                    "If one demon escapes the covenant, it brings the rest: "
                    "grogs and covenfolk possessed one after another, from "
                    "within the Aegis. Cenodoxus's Might is high enough to "
                    "pass many an Aegis."
                ),
                ignored="The covenant rots from within.",
                stopped=(
                    "The six are driven out or destroyed, and Gascony begins to heal."
                ),
                turned="The covenant earns the Church's gratitude, and its notice.",
            ),
        ],
    )


# -- Tolomae's heirs --


def _procrustean(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_procrustean"] = b.threat(
        "The Procrustean League",
        summary="A short-lived alliance led by Tolomae of Bellaquin, a Cathar "
        "sympathiser, that called for open war on the Church to save the "
        "Order's holdings in the south. At the Tribunal of 1214 he urged "
        "a joint Hermetic answer to the crusade, which would have meant "
        "open meddling in mundane and Church affairs; he was thrown out "
        "of the debate and swore revenge on the Mercurian conservatives "
        "and on the Coenobium, his old covenant. Aedes Mercurii and the "
        "Coenobium both renounced the League, Jerbiton declared him "
        "orbus in 1216, and he was Marched for repeated interference and "
        "slain early in 1218.",
        secrets=[
            titled(
                "Tolomae's flight",
                "Tolomae was suspected of the papal legate's murder and fled "
                "rather than answer the Quaesitor.",
            ),
            titled(
                "Tolomae's supporters",
                "Several of Tolomae's supporters went to other covenants or "
                "vanished in the war, and hide among the faidits; some magi "
                "fear the cause will return, sharpened by grief. No one knows "
                "who they are, which makes it an open case.",
            ),
        ],
        antagonist="Tolomae's surviving followers, hidden among the faidits",
        stages=[
            S(
                "Whispers among the faidits",
                at=1,
                clues=(
                    "Dispossessed knights speak of a wizard who promises "
                    "them their lands back; spells strike a crusader "
                    "garrison with no sigil the Redcaps know."
                ),
                ignored="The followers gather strength and allies unseen.",
                stopped="A follower is found out and brought to the Quaesitores.",
                turned=(
                    "The covenant finds them first, and decides what to do "
                    "with what it knows."
                ),
            ),
            S(
                "Tolomae's revenge",
                at=2,
                clues=(
                    "Attacks fall on the Mercurians of Aedes Mercurii and on "
                    "the Coenobium, the two Tolomae swore to punish; each "
                    "side suspects the other."
                ),
                ignored="The Tribunal's old rivals turn on each other.",
                stopped="The true culprits are exposed before blood is spilled.",
                turned="The covenant brokers a reckoning, and both sides owe it.",
            ),
            S(
                "War on the Church",
                at=3,
                clues=(
                    "The League's heirs strike openly at churchmen and "
                    "crusaders, as Tolomae wanted."
                ),
                ignored=(
                    "The Church sees wizards behind the heresy, and the whole "
                    "Order in the south pays."
                ),
                stopped="The followers are Marched, and the cause dies with them.",
                turned=(
                    "The covenant channels their anger into something the "
                    "Code allows, and gains desperate allies."
                ),
            ),
        ],
    )


# -- the covenant at war with itself --


def _tolosa(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_tolosa"] = b.threat(
        "Tolosa Paratge's Civil War",
        summary="The old covenant in the regio beside Toulouse is tearing itself "
        "apart over its Cathars. In 1218, sure the city would fall, its "
        "leader Augustus, a senior Quaesitor, asked the Gorgiastic Cathar "
        "magi to leave for their own safety. Marc, one of them, declared "
        "Wizard's War on him and, convinced he was under a demon's "
        "sway, killed him in a confused quarrel in the tower; a month "
        "later Carolus St. Tropez declared war on Marc, who did not "
        "resist, and killed him. Mariola, made leader, did nothing, and "
        "the covenant split: the Blacks, who shield the Cathars, hold "
        "the regio under Cyprian of Flambeau; the Whites, who would "
        "expel them, follow St. Tropez in the city and try to blockade "
        "it.",
        secrets=[
            titled(
                "A breach of the Code",
                "Both sides of Tolosa Paratge's war are plainly depriving each "
                "other of magical resources, which the Code forbids, but no one "
                "has brought a case and the Quaesitores have kept out of it, "
                "partly from respect. The rest of the Tribunal waits to see "
                "what survives.",
            ),
            titled(
                "The boom",
                "Adam Carpentiere's enchanted boom across the Garonne keeps "
                "Tolosa Paratge's weakening regio alive, and the Gorgiastics "
                "opposed it.",
            ),
            titled(
                "Raimond's death",
                "Raimond, a Gorgiastic Good Man, believes he will die by "
                "drowning in the Garonne and fears no other death.",
            ),
            titled(
                "St. Tropez's resolve",
                "St. Tropez would rather die striking at the Gorgiastics than "
                "wait for a Tribunal to convict him.",
            ),
        ],
        antagonist="The White and Black factions of Tolosa Paratge",
        stages=[
            S(
                "The blockade",
                at=1,
                clues=(
                    "Covenfolk of both factions brawl in the streets of "
                    "Toulouse. Half a dozen grogs and a dozen covenfolk are "
                    "trapped in the regio, and their friends in the city ask "
                    "outside magi, or send Redcaps, for help. A book lent to "
                    "the covenant before the quarrel must be fetched back."
                ),
                ignored="The siege tightens and the covenant sinks towards Winter.",
                stopped="A truce lets the trapped covenfolk out.",
                turned=(
                    "The covenant becomes a trusted go-between, welcome on "
                    "both sides of the lake."
                ),
            ),
            S(
                "Allies called in",
                at=2,
                clues=(
                    "The Blacks look to Castra Solis, which they think would "
                    "answer Cyprian, and to Renaud of Stella Durus, Cyprian's "
                    "filius; the Whites court Stella Durus through Mariola's "
                    "friendship with Jean Marie. Both seek the Coenobium's "
                    "weight. A covenant that backs the wrong side may face a "
                    "Wizard's War."
                ),
                ignored="The quarrel draws in covenants across the Tribunal.",
                stopped="The outsiders refuse to take sides.",
                turned="The covenant chooses a side and is rewarded if it wins.",
            ),
            S(
                "Tribunal or Wizard's War",
                at=3,
                clues=(
                    "The Whites must choose between a case at Glanum in 1221 "
                    "and a fresh Wizard's War to retake the regio."
                ),
                ignored="New Wizard's Wars are declared, and more magi die.",
                stopped=(
                    "A case is brought and the Quaesitores rule on both "
                    "factions' breaches."
                ),
                turned=(
                    "The covenant brings the case itself and shapes the settlement."
                ),
            ),
            S(
                "The lake closes",
                at=4,
                clues=(
                    "Open battle reaches the island; the boom on the Garonne "
                    "is threatened, and with it the regio."
                ),
                ignored=(
                    "Tolosa Paratge is destroyed or its regio lost, and "
                    "Toulouse loses the magi who guarded its spirit."
                ),
                stopped="The covenant is reconciled and rebuilt under a new leader.",
                turned=(
                    "One faction wins with the covenant's help, and the "
                    "ancient site and its lore are open to its friends."
                ),
            ),
        ],
    )


# -- the Coenobium's reach --


def _coenobium(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_coenobium"] = b.threat(
        "The Coenobium's Hegemony",
        summary="The Coenobium, a league of chapter houses along the Rhône and "
        "the coast run mostly by Jerbiton magi and the Tribunal's "
        "Redcaps, has long been praised as a model of cooperation. "
        "Since it destroyed Fraxinetum in 975 it has gathered most of "
        "the magical and mundane resources of the County of Provence, "
        "and it smothers any new covenant in its shadow that will not "
        "join it as a chapter: none has thrived in southern Provence for "
        "over a century. With several covenants lost to the crusade it "
        "has grown unopposed, and even old allies are uneasy. It offers "
        "help to any petitioner, and everyone knows the help implies "
        "annexation.",
        secrets=[
            titled(
                "The Coenobium's alliance",
                "The Coenobium allies with Castra Solis and knows the pair can "
                "carry most votes, but it also knows that isolating the small "
                "covenants risks a Tribunal too thin to be quorate.",
            ),
            titled(
                "Alazais and the cult",
                "The Coenobium's First Consul, Alazais, the Chief Redcap, is "
                "rumoured to belong to the Matres and Matrones.",
            ),
            titled(
                "The Praeco's bargain",
                "Dama's secret Longevity Ritual for Alazais's companion has "
                "bought the Coenobium's quiet support for burying a motion "
                "when the Praeco needs it.",
            ),
        ],
        antagonist="The Coenobium Rhodanien and its First Consul, Alazais",
        stages=[
            S(
                "A generous offer",
                at=1,
                clues=(
                    "A new covenant finds its suppliers slow, its Redcap "
                    "late and its neighbours unfriendly, until a consul of "
                    "the Coenobium calls with an offer of help."
                ),
                ignored="The covenant's efforts keep failing, and it grows dependent.",
                stopped="The covenant finds friends elsewhere and stands alone.",
                turned=(
                    "It becomes a chapter house on good terms, with a consul "
                    "as patron and a path to full membership, or to "
                    "independence later."
                ),
            ),
            S(
                "Chapters beyond Arelat",
                at=2,
                clues=(
                    "The Coenobium courts Stella Durus as a chapter, offers "
                    "to take the Exiles under its direction, and sponsors "
                    "magi to reclaim Barbegal or the Alpine sites of Portus "
                    "Cottiae."
                ),
                ignored=(
                    "Chapter houses spring up in the Narbonnais and the "
                    "Toulousain, and their votes are the Coenobium's."
                ),
                stopped="The western covenants refuse, and its reach stays in Arelat.",
                turned="The covenant founds a chapter on the Coenobium's silver.",
            ),
            S(
                "The bloc",
                at=3,
                clues=(
                    "At Tribunal the Coenobium and Castra Solis vote "
                    "together, and a motion against the Praeco is buried "
                    "without debate."
                ),
                ignored=(
                    "Little can stand against the pair; the smaller "
                    "covenants stop coming, and the Tribunal struggles for a "
                    "quorum."
                ),
                stopped=(
                    "A coalition of the small covenants, perhaps with Aedes "
                    "Mercurii, checks the bloc."
                ),
                turned=(
                    "The covenant learns what the Praeco paid, and uses it "
                    "against her or the Coenobium."
                ),
            ),
        ],
    )


# -- the frames --


def _glanum(provence: Provence) -> None:
    b = provence.b
    provence.world["frame_glanum"] = b.threat(
        "The Tribunal at Glanum",
        summary="A saga frame. The Tribunal meets in summer 1221 in the ruins of "
        "Glanum, a neutral ground agreed on after the bitter meeting of "
        "1214, which was driven from Toulouse to Castra Solis by de "
        "Montfort's army. Midius of Flambeau, the flamen, opens each day "
        "masked and robed in the old Mercurian rite, to the scorn of the "
        "pious at Castra Solis. The crusade and interference with "
        "mundanes will fill the agenda.",
        secrets=[
            titled(
                "Rumours at the confirmation",
                "Rumours at Beatrice's confirmation will hint that Senex was murdered.",
            ),
            titled(
                "If the Tribunal intervenes",
                "If the Tribunal votes to intervene against the crusade, the "
                "Pyrenean covenants may walk out for good.",
            ),
            titled(
                "Storyguide Notes",
                "See The Serpent's Venom and Pyrenean Secession.",
            ),
        ],
        antagonist="The Tribunal's factions",
        moves=DATED,
        stages=[
            S(
                "The Presiding Quaesitor",
                year=1221,
                season="Summer",
                clues=(
                    "The first business is Tibaut's successor. Beatrice of "
                    "Guernicus, his filia, is expected to be confirmed, but "
                    "she is young, lives in Arelat after quarrelling with "
                    "Primus Garus, and has no following of her own."
                ),
                ignored="Beatrice is confirmed, or a rival is chosen, without the covenant.",
                stopped="The appointment is contested and another Quaesitor named.",
                turned="The covenant's votes make Beatrice, and she remembers.",
            ),
            S(
                "The faidits' petition",
                year=1221,
                season="Summer",
                clues=(
                    "The Hermetic faidits and refugees of the fallen "
                    "covenants demand licence to defend themselves and win "
                    "back their power, and want Garus and the milites behind "
                    "them. The Mercurians, with Ara Maxima Nova, Stella "
                    "Durus and Miniata Sophia, argue for waiting the war "
                    "out. The Exiles also want their covenant recognised."
                ),
                ignored="The vote goes as the great covenants decide.",
                stopped="Non-interference is upheld and the Exiles are restrained.",
                turned=(
                    "The covenant shapes a ruling that lets magi defend their "
                    "own without making war on the Church."
                ),
            ),
            S(
                "The weight of the Coenobium",
                year=1221,
                season="Summer",
                clues=(
                    "Senior magi mutter about the Coenobium's growing power, "
                    "and watch how its votes and Castra Solis's fall together."
                ),
                ignored="The hegemony grows.",
                stopped="A motion curbs its expansion.",
                turned="The covenant trades its votes to the Coenobium for favours.",
            ),
            S(
                "Tolosa Paratge's case",
                year=1221,
                season="Summer",
                clues=(
                    "Someone may at last bring Tolosa Paratge's war before "
                    "the Tribunal, and both factions lobby every covenant."
                ),
                ignored="No case is brought, and the war goes on.",
                stopped="The Tribunal rules and the factions must obey.",
                turned="The covenant brings the case and frames the ruling.",
            ),
        ],
    )


def _adulteration(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_adulteration"] = dormant(
        b.threat(
            "The Adulteration of Flambeau",
            summary=paragraphs(
                "Val-Negra, Flambeau's own covenant and once the largest "
                "in the Order, fell as the Schism War was ending "
                "and never rose again. The Quaesitores ruled it must "
                "not, the domus magna moved to Castra Solis, and even "
                "its site in the far south is forgotten: a regio on "
                "Mount Perditu, where travellers go astray and return "
                "with no memory, if they return at all.",
                "A saga frame as well as a threat: an expedition into "
                "the lost covenant, its catacombs, ghosts and Aerie "
                "Clan, and perhaps a saga of restoring it against the "
                "ban.",
            ),
            secrets=[
                titled(
                    "The Iron Door",
                    "Deep in the mountain of Val-Negra a round chamber holds "
                    "the Iron Door, an iron disc carved as a wheel whose spokes "
                    "are seven swords, warded against all but the strongest "
                    "divinations. Since Apromor's time it has been forbidden "
                    "to touch it.",
                ),
                titled(
                    "What lies behind the door",
                    "Behind the Iron Door is the Adulteration of Flambeau: a "
                    "malignant spirit born of the Founder's Twilights, made of "
                    "his failings, wants and errors, which believes it is "
                    "Flambeau.",
                ),
                titled(
                    "The Adulteration's powers",
                    "The Adulteration is wrathful and proud, casts the "
                    "Founder's Pilum of Fire at will, flies on smoke, curses "
                    "magi, and when furious bursts into flame. Released, it "
                    "would lay the country waste in rage.",
                ),
                titled(
                    "The breach of 1012",
                    "When five Diedne archmagi stormed Val-Negra in 1012 "
                    "something got out and destroyed them.",
                ),
                titled(
                    "The failing ward",
                    "The two surviving defenders of Val-Negra put the "
                    "Adulteration back, but the old seal, made by a lost Rite "
                    "of Fenicil, was gone; their Hermetic ward holds only "
                    "while the Iron Door stays shut, and anyone can open it.",
                ),
                titled(
                    "The Quaesitores' silence",
                    "The Quaesitores hid the whole affair of the Iron Door.",
                ),
                titled(
                    "The door's watcher",
                    "Abaddon of Tytalus, one of the two surviving defenders, "
                    "keeps watch over the Iron Door as a Living Ghost.",
                ),
                titled(
                    "Storyguide Notes",
                    "The Adulteration: Magic Might 65 (Ignem). Its curses "
                    "give Deficient Ignem or Incompatible Arts.",
                ),
            ],
            antagonist="The Adulteration of Flambeau, the Founder's Twilight-born shadow",
            realm="Magic",
            stages=[
                S(
                    "The lost covenant",
                    at=1,
                    clues=(
                        "Someone seeks Val-Negra: Mercurians after "
                        "Priamitus's scroll of the great road ritual, "
                        "Flambeau eager to settle which covenant is the true "
                        "heir, or treasure hunters with an old Tribunal "
                        "record. Merinita bring back tales of faeries on "
                        "Mount Perditu."
                    ),
                    ignored="Another party finds the way in first.",
                    stopped=(
                        "The seekers are turned back, and the Quaesitores' ban holds."
                    ),
                    turned=(
                        "The troupe reaches Val-Negra and wins its guardian's "
                        "trust, and Casting Tokens for its Aegis."
                    ),
                ),
                S(
                    "The Iron Door",
                    at=2,
                    clues=(
                        "Intruders reach the round chamber beneath the "
                        "shrine. The Aerie raise the alarm and fight "
                        "anyone who goes on; carvings on the walls tell of "
                        "old wars."
                    ),
                    ignored="The door is opened, and the ward with it.",
                    stopped=(
                        "The intruders are stopped, and the ward renewed or "
                        "strengthened."
                    ),
                    turned=(
                        "The troupe restores a lasting seal, perhaps by "
                        "finding the lost Rite of Fenicil."
                    ),
                ),
                S(
                    "The Founder's shadow",
                    at=3,
                    clues=(
                        "Smoke and ash drift from Mount Perditu. A bald, "
                        "sun-darkened man in a brown robe walks the "
                        "foothills, smouldering when crossed, and calls "
                        "himself Flambeau."
                    ),
                    ignored=(
                        "The Adulteration burns its way across the "
                        "countryside, and the Quaesitores' secret is out."
                    ),
                    stopped=(
                        "It is subdued and shut away again, or destroyed at great cost."
                    ),
                    turned=(
                        "Its twisted memories of the Founder yield secrets "
                        "of House Flambeau before it is put down."
                    ),
                ),
            ],
        )
    )


def _secession(provence: Provence) -> None:
    b = provence.b
    provence.world["threat_secession"] = dormant(
        b.threat(
            "Pyrenean Secession",
            summary="The conservative covenants, led by the Mercurians of Aedes "
            "Mercurii with Ara Maxima Nova, Stella Durus and Miniata "
            "Sophia, want the Order to keep out of the crusade and trust "
            "to their isolation. If the Tribunal decides to act against "
            "the crusaders and the Church, they may refuse to take part "
            "any longer and ask the Grand Tribunal of 1228 to make them a "
            "Tribunal of their own: four covenants, the number a new "
            "Tribunal needs. Aedes Mercurii already threatened to walk "
            "out in 1214, which could have made the meeting invalid, "
            "until Tibaut and the Chief Redcap's threat to suspend the "
            "Redcaps stopped it.",
            secrets=[
                titled(
                    "Bellaquin's dream",
                    "Bellaquin, for its own reasons, dreams of a Catalan Tribunal.",
                ),
                titled(
                    "South of the mountains",
                    "Several of the Provençal Tribunal's places lie south of "
                    "the mountains where the Iberian Tribunal also looks.",
                ),
            ],
            antagonist="The Pyrenean conservatives, led by Aedes Mercurii",
            moves=DATED,
            stages=[
                S(
                    "Intervention at Glanum",
                    year=1221,
                    season="Summer",
                    clues=(
                        "The Tribunal votes to act against the crusaders; "
                        "the Mercurians leave the meeting in anger."
                    ),
                    ignored="The conservatives begin to talk of leaving.",
                    stopped="The vote fails, or a compromise keeps them in.",
                    turned=(
                        "The covenant brokers terms each side can live with, "
                        "and both remember it."
                    ),
                ),
                S(
                    "The boycott",
                    year=1227,
                    season="Summer",
                    clues=(
                        "The Pyrenean covenants refuse any further "
                        "discussion with the rest of the Tribunal, and their "
                        "Redcaps carry letters to the other Tribunals."
                    ),
                    ignored="The Tribunal is split in two in all but name.",
                    stopped="Concessions bring them back to the table.",
                    turned="The covenant sides with the bloc, and has its trust.",
                ),
                S(
                    "Petition at the Grand Tribunal",
                    year=1228,
                    season="Summer",
                    clues=(
                        "With four covenants behind them they ask the Grand "
                        "Tribunal for their own Tribunal; Bellaquin presses "
                        "its idea of a Catalan one."
                    ),
                    ignored="The Grand Tribunal decides without the covenant.",
                    stopped="The petition fails and the Pyrenees stay Provençal.",
                    turned=(
                        "A new Tribunal is made in the mountains, with a "
                        "Code the covenant helped to write."
                    ),
                ),
            ],
        )
    )


# -- tying the stories to the other parts' records --


def _key(name: str) -> str:
    """A name compared loosely: case, a leading 'The', and the spelling of
    'Saint' set aside."""
    out = name.casefold().strip()
    for article in ("the ", "la ", "le "):
        out = out.removeprefix(article)
    return out.replace("saint-", "st. ").replace("saint ", "st. ").replace("-", " ")


def _find(records: list[Any], *names: str) -> Any | None:
    """The first record whose name is one of `names`, or failing that
    whose name starts with one of them as a whole word, loosely
    compared."""
    wanted = [_key(n) for n in names]
    for record in records:
        if _key(record.name) in wanted:
            return record
    for record in records:
        name = _key(record.name)
        if any(name.startswith(n + " ") for n in wanted):
            return record
    return None


def _add_to(record: Any, more: str, hidden: Secrets = "") -> None:
    """Add a paragraph to a record's summary, and `hidden` to its
    secrets."""
    record.summary = paragraphs(record.summary, more)
    record.secrets = more_secrets(record.secrets, hidden)


#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target's possible names, note).
LINKS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("threat_crusade", "covenants", ("Ostal des Exiles",), "Hermetic faidits"),
    ("threat_crusade", "covenants", ("Tolosa Paratge",), "In the besieged city"),
    ("threat_crusade", "covenants", ("Castra Solis",), "Backs the crusade"),
    ("threat_crusade", "characters", ("Tres",), "His engines may have killed Simon"),
    ("threat_serpent", "characters", ("Dama",), "The Praeco, Maju's thrall"),
    ("threat_serpent", "characters", ("Beatrice",), "Tibaut's filia and heir"),
    ("threat_serpent", "characters", ("Protendus",), "The likely investigator"),
    ("threat_serpent", "characters", ("Luc",), "Told Dama of Tibaut's questions"),
    ("threat_serpent", "characters", ("Alazais",), "Bought with a Longevity Ritual"),
    ("threat_serpent", "characters", ("Marie",), "Dama's estranged filia"),
    ("threat_serpent", "characters", ("Rebecca",), "A sorgina of Dama's circle"),
    ("threat_serpent", "covenants", ("Castra Solis",), "Dama's covenant"),
    ("threat_procrustean", "covenants", ("Bellaquin",), "Tolomae's covenant"),
    ("threat_procrustean", "covenants", ("Aedes Mercurii",), "Tolomae swore revenge"),
    (
        "threat_procrustean",
        "covenants",
        ("Coenobium Rhodanien", "Coenobium"),
        "His old covenant, which renounced him",
    ),
    ("threat_procrustean", "covenants", ("Ostal des Exiles",), "Faidits shelter them"),
    ("threat_tolosa", "covenants", ("Tolosa Paratge",), "The divided covenant"),
    ("threat_tolosa", "characters", ("Mariola",), "Leader, paralysed"),
    (
        "threat_tolosa",
        "characters",
        ("Carolus St. Tropez", "Carolus"),
        "Leads the Whites",
    ),
    ("threat_tolosa", "characters", ("Cyprian",), "Leads the Blacks"),
    (
        "threat_tolosa",
        "characters",
        ("Adam Carpentiere", "Adam"),
        "White; built the boom",
    ),
    ("threat_tolosa", "characters", ("Raimond",), "Black; a Gorgiastic Good Man"),
    ("threat_tolosa", "characters", ("Renaud",), "Cyprian's filius"),
    ("threat_tolosa", "covenants", ("Stella Durus",), "Courted by both sides"),
    (
        "threat_coenobium",
        "covenants",
        ("Coenobium Rhodanien", "Coenobium"),
        "The hegemon",
    ),
    ("threat_coenobium", "characters", ("Alazais",), "First Consul"),
    ("threat_coenobium", "covenants", ("Castra Solis",), "Its ally"),
    ("threat_coenobium", "covenants", ("Stella Durus",), "Courted as a chapter"),
    ("threat_coenobium", "covenants", ("Ostal des Exiles",), "It would direct them"),
    ("frame_glanum", "characters", ("Beatrice",), "To be confirmed"),
    ("frame_glanum", "characters", ("Dama",), "The Praeco presides"),
    ("frame_glanum", "characters", ("Midius",), "The flamen"),
    ("frame_glanum", "characters", ("Garus",), "The faidits want his backing"),
    ("frame_glanum", "covenants", ("Ostal des Exiles",), "Seeks recognition"),
    ("frame_glanum", "covenants", ("Aedes Mercurii",), "Leads the conservatives"),
    ("threat_adulteration", "characters", ("Abaddon",), "Guards the Iron Door"),
    ("threat_adulteration", "covenants", ("Castra Solis",), "The domus magna now"),
    (
        "threat_adulteration",
        "covenants",
        ("Aedes Mercurii",),
        "Claims Val-Negra's legacy",
    ),
    ("threat_secession", "covenants", ("Aedes Mercurii",), "Leads the bloc"),
    ("threat_secession", "covenants", ("Ara Maxima Nova",), "Of the bloc"),
    ("threat_secession", "covenants", ("Stella Durus",), "Of the bloc"),
    ("threat_secession", "covenants", ("Miniata Sophia",), "Of the bloc"),
    ("threat_secession", "covenants", ("Bellaquin",), "Wants a Catalan Tribunal"),
)

#: Each story's place: the region part's key first, then names to try.
PLACES: dict[str, tuple[str, tuple[str, ...]]] = {
    "threat_crusade": ("toulousain", ("Toulouse",)),
    "threat_serpent": ("mimizan", ("Mimizan", "Dama's Tower", "The Tower at Mimizan")),
    "threat_spirits": ("gascony", ("Gascony",)),
    "threat_procrustean": ("toulousain", ("The Toulousain", "Toulouse")),
    "threat_tolosa": ("toulouse", ("Toulouse", "The Toulousain")),
    "threat_coenobium": ("arelat", ("Arelat",)),
    "frame_glanum": ("glanum", ("Glanum", "The Ruins of Glanum")),
    "threat_adulteration": ("val_negra", ("Val-Negra", "Val Negra", "Mount Perditu")),
    "threat_secession": ("pyrenees", ("The Pyrenees", "Pyrenees")),
}

#: Factions other parts may make that stand behind a story.
BEHIND: dict[str, tuple[str, ...]] = {
    "threat_serpent": ("Matres and Matrones", "Matres & Matrones"),
    "threat_procrustean": ("Procrustean League",),
    "threat_crusade": ("The Crusaders", "The Albigensian Crusaders", "Crusader Army"),
}


def finish(provence: Provence) -> None:
    saga, world = provence.b.saga, provence.world
    candidates: dict[str, list[Any]] = {
        "characters": saga.characters,
        "covenants": saga.covenants,
    }
    places = [n for n in saga.neighbours if n.kind == "place"]
    factions = [n for n in saga.neighbours if n.kind == "faction"]
    for key, kind, names, note in LINKS:
        target = _find(candidates[kind], *names)
        if target is not None:
            Builder.link(world[key], kind, target, note)
    tolosa = _find(saga.covenants, "Tolosa Paratge")
    for key, (slug, names) in PLACES.items():
        if key == "threat_tolosa" and tolosa is not None and tolosa.place_id:
            world[key].place_id = tolosa.place_id
            continue
        place = provence.places.get(slug) or _find(places, *names)
        if place is not None:
            world[key].place_id = place.id
    for key, names in BEHIND.items():
        faction = _find(factions, *names)
        if faction is not None:
            world[key].answers_to = faction.id
    tribunal = provence.tribunal or next(iter(saga.tribunals), None)
    if tribunal is not None:
        _add_to(tribunal, HOOKS, HIDDEN_HOOKS)


HOOKS = paragraphs(
    "Stories. The crusade is the background to everything: the Order is "
    "split over how to answer it, and the meeting at Glanum in 1221 will "
    "argue little else. Beside it run the Six Deadly Spirits in Gascony and "
    "the Narbonnais, the followers of the Procrustean League hiding among "
    "the faidits, Tolosa Paratge's war with itself and the Coenobium's "
    "growing reach. Two stories wait for the storyguide to begin them: the "
    "lost covenant of Val-Negra and what its Iron Door holds, and the "
    "Pyrenean covenants' threat to seek a Tribunal of their own at the Grand "
    "Tribunal of 1228. A smaller hook: Tres' Band, roving in the forests "
    "near Bazas, watches how each new covenant treats the common folk, and "
    "turns from indifference to hatred against magi who set themselves up "
    "as lords.",
)

HIDDEN_HOOKS = [
    titled(
        "Fraxinetum Redux",
        "Heirs of the raider covenant the Coenobium destroyed in 975, led by "
        "Ahmad ibn Nasr of Tytalus, keep a pirate base on the Hyères islands "
        "as Fraxinetum Redux, with two magi, a third aboard a ship, and still "
        "sponsor raids on the Provençal coast and on Catalan and Genoese "
        "shipping, steering clear of the Coenobium's fleet.",
    ),
    titled(
        "Fraxinetum Redux undeclared",
        "The magi of Fraxinetum Redux have never declared themselves for fear "
        "their ancestors' name would bring a Wizard's War; their three votes "
        "go unused.",
    ),
    titled(
        "What Fraxinetum Redux opposes",
        "Fraxinetum Redux opposes only a new maritime stronghold or an island "
        "covenant off the south coast.",
    ),
    titled(
        "The Drac of Beaucaire",
        "The monster said to have returned beneath the Rhône is a Tytalus "
        "eremite, Aucassin, who never comes to Tribunal and lives as the "
        "merchant Rene of Dragonianum, ruling the town council by subtle "
        "Mentem magic.",
    ),
    titled(
        "Aucassin's Drac blood",
        "Aucassin has learned he is heir to the Drac's blood and seeks a "
        "Mystery that would make him a true elder Drac.",
    ),
    titled(
        "Aucassin's kidnappings",
        "Aucassin has kidnapped children and servants to serve him.",
    ),
]
