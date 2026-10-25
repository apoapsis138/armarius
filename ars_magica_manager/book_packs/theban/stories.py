"""The saga's stories, in paraphrase: each a threat whose stages lay out
how it unfolds if the troupe ignores, stops or turns it.

Under way in 1220: An Enemy Within, the book's suggested main enemy,
Proximios of Alexandria, in the five stages from the League of the
Vigilant's recruiting to Celaenea set against Lucian; Epiros's war on
the Kingdom of Thessaloniki; and Nicaea's war on the Latins, from the
landing at Holkos in 1220 to the peace of 1221 (the book stops there,
so the later stages follow history in broad strokes, each marked as
what happens if history holds). The Tribunal of 1221 on Delos is a saga
frame of dated stages, its agenda in the meeting's own order.

Dormant until the storyguide begins them: Akgah's war, Lucian's pacts
and the risk of a False God, Kampe's Lovers and the titans, Klymene's
prison, the Estate of Hades, the Tremere appeal of 1228, the Verditius
Contest of 1234, Talos, the Duke of Naxos, the lost hagka, the
Christians of Serapis, Zeno, Thermakopolis refounded, and Wilusa.

`finish` puts each story inside the place where it plays out, ties it
to the covenants, magi, creatures and factions the other parts made,
found by key or by name, and closes the Tribunal's summary with the
book's smaller story seeds, too slight for a threat of their own."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, dormant, paragraphs

if TYPE_CHECKING:
    from . import Theban

S = Builder.stage
DATED = "Fixed dates"
HISTORY = "If history holds, "


def build(theban: Theban) -> None:
    _enemy_within(theban)
    _tribunal_1221(theban)
    _epiros(theban)
    _nicaea(theban)
    _akgah(theban)
    _lucian(theban)
    _kampe(theban)
    _klymene(theban)
    _hades(theban)
    _tremere_appeal(theban)
    _verditius_contest(theban)
    _talos(theban)
    _naxos(theban)
    _hagka(theban)
    _serapis(theban)
    _zeno(theban)
    _thermakopolis(theban)
    _wilusa(theban)


# -- the hidden enemy --


def _enemy_within(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_enemy_within"] = b.threat(
        "An Enemy Within",
        summary=paragraphs(
            "Most magi know that demons marched with both armies when "
            "Constantinople fell, and many fear the Order caught the "
            "same rot. Hydatius of Ingasia and Proximios of Alexandria "
            "have answered by founding the League of the Vigilant: "
            "Hydatius is its general, Proximios its paymaster and "
            "quartermaster. They want recruits from outside the "
            "Tribunal, fresh eyes to find what is foul, and they keep "
            "every other member's name secret. Since Hermetic magic "
            "cannot reveal a demon, the league watches its sodales and "
            "waits for one to give himself away.",
            "The Tribunal accepts the league as it accepts any, though "
            "its quieter magi remember how hunts for witches grow "
            "beyond anyone's control; the two founders' good names "
            "silence most critics. Proximios, the Redcap whose idea it "
            "was to make the logothete's post permanent, is the "
            "Redcaps' choice to follow Leontius in 1221. He neither "
            "seeks the post nor refuses it, and most magi call that "
            "humility.",
            "A saga frame as well as a threat, and the book's own "
            "choice for a saga's chief enemy. Let it build over years: "
            "at full strength it would overwhelm young magi before the "
            "saga had found its feet.",
        ),
        secrets=paragraphs(
            "Proximios is an infernalist. He has mastered the Unholy "
            "Method of Incantation and the Unholy Power of Diablerie "
            "and holds a long list of demons' True Names; the Tempters "
            "and Evil Spirits he calls up spy for him, bait his traps "
            "and urge his sodales into sin. He wants the whole Order "
            "brought low, beginning with Thebes, and works slowly and "
            "covertly because the Tribunal is full of magi who would "
            "spot a clumsy Infernal plot. The letters that pass "
            "through Alexandria show him where each covenant is weak.",
            "He set Hydatius at the league's head so that its mistakes "
            "would be someone else's. He will steer it toward magi who "
            "look like diabolists and are not, send its members out to "
            "investigate without going himself, and once they are in "
            "the field a demon wearing Hydatius's face will order the "
            "attack. Other infernalists have told "
            "him that an infernalist planted among Lucian's Children "
            "of Olympos would probably raise a False God for them to "
            "bind instead of a faerie; finding such a magus is the "
            "hard part.",
            "In 1220 all this is still taking shape in his mind. He "
            "will take the logothete's post, making a show of "
            "reluctance so that no blame sticks to him when his plans "
            "come apart, and as keeper of the register of tokens and "
            "shards he can favour those who help him. He has no "
            "Hermetic accomplices yet, but has noted a few magi he "
            "thinks could be tempted. Each scheme is built to look "
            "like another's work; as he gains ground he will use the "
            "Vigilant more openly, as shock troops for a Tribunal "
            "remade to suit him.",
        ),
        antagonist="Proximios of House Mercere, a Redcap secretly in league with Hell",
        realm="Infernal",
        stages=[
            S(
                "The Vigilant recruit",
                at=1,
                clues=(
                    "Through 1220 Hydatius and Proximios sound out magi new "
                    "to the Tribunal: Frankish incomers, metoikoi, the "
                    "newly Gauntleted. A recruit is asked to keep an eye on "
                    "a sodalis and report anything strange. Proximios "
                    "supplies vis and equipment but never leads anyone in "
                    "person."
                ),
                ignored=(
                    "The league grows unseen, its members strangers to one "
                    "another, and becomes Proximios's tool."
                ),
                stopped=(
                    "The troupe declines to join, or learns who the members "
                    "are and makes the league's methods known before it "
                    "acts."
                ),
                turned=(
                    "Player magi join and watch the league from within, "
                    "where in time they may notice that not every order "
                    "really comes from Hydatius."
                ),
            ),
            S(
                "The new logothete",
                at=2,
                clues=(
                    "On Delos in 1221 Leontius steps down and the Redcaps "
                    "put Proximios forward. He accepts with every sign of "
                    "unwillingness, and takes charge of the register of "
                    "tokens and shards and of where every Redcap is sent."
                ),
                ignored=(
                    "The Tribunal's records, messengers and letters are all "
                    "in his hands."
                ),
                stopped=(
                    "Another Redcap is chosen, or a later vote of no "
                    "confidence among the Redcaps removes him."
                ),
                turned=(
                    "The troupe backs him and finds its tally of tokens "
                    "kindly kept, at the price of owing him."
                ),
            ),
            S(
                "False accusations",
                at=3,
                clues=(
                    "League members are sent to look into three suspects: "
                    "Caterina da Vigonovo of Polyaigos, a Venetian newcomer; "
                    "the young magi of Erebos, whose witchcraft looks "
                    "sinister; and Delfini of Aegaea, whose questions are "
                    "taken for prying. In the field, a demon in Hydatius's "
                    "shape tells them to strike."
                ),
                ignored=(
                    "Innocent magi are attacked, or charged with diabolism "
                    "before the Judicial Board, and their accusers are "
                    "rewarded with tokens."
                ),
                stopped=(
                    "The troupe proves the accused innocent, or exposes the "
                    "false Hydatius."
                ),
                turned=(
                    "Clearing one of the accused earns lasting gratitude, "
                    "and the first real hint that someone is steering the "
                    "league."
                ),
            ),
            S(
                "Hedyosmos turned on Gigas",
                at=4,
                clues=(
                    "Hints reach Aiakia that the Tremere of Gigas had a hand "
                    "in Constantinople's fall and mean to strike at "
                    "Hedyosmos next; Boustaphan will never let her read "
                    "Gigas's records. Tisiphon, easier to lead, is told the "
                    "Tremere slipped past the justice they deserved."
                ),
                ignored=(
                    "Aiakia moves against Gigas and the volatile Tisiphon "
                    "declares Wizard's Wars, waking the old enmity of the "
                    "Sundering."
                ),
                stopped="Someone shows the evidence to be forged before blood is spilled.",
                turned=(
                    "The troupe arranges an exchange of records or oaths, "
                    "and wins the trust of both covenants."
                ),
            ),
            S(
                "Celaenea set against Lucian",
                at=5,
                clues=(
                    "Celaenea of Hedyosmos, whose love of Hermes borders on "
                    "obsession, hears from a well-wisher that Lucian of "
                    "Aegaea means to raise the forgotten gods. Meanwhile "
                    "Proximios hunts for an infernalist to slip into the "
                    "Children of Olympos."
                ),
                ignored=(
                    "Celaenea turns on Lucian and his league; if Proximios "
                    "places his man, the god they summon and bind is a "
                    "False God (see Lucian's Pacts)."
                ),
                stopped=(
                    "Celaenea and Lucian compare what they were told and "
                    "see that a third hand set them at odds."
                ),
                turned=(
                    "The trail of whispers leads back to the logothete "
                    "himself, and the troupe holds the proof."
                ),
            ),
        ],
    )


# -- the frames --


def _tribunal_1221(theban: Theban) -> None:
    b = theban.b
    theban.world["frame_1221"] = b.threat(
        "The Tribunal of 1221",
        summary=paragraphs(
            "A saga frame. The Tribunal meets on Delos in 1221, seven "
            "years after the last meeting; the book names no season, "
            "and Summer is assumed. Its business runs in fixed order: "
            "the phylai's candidate dinners and two days of apprentice "
            "interviews, then the four phases (Hermetic Assembly, Law "
            "Council, People's Court, Council of Archai), and last the "
            "Rite of Dismissal and the Ceremony of Propitiation at the "
            "sacred lake. Which phyle is principal this time is left to "
            "the storyguide. Aiakia of Hedyosmos presides as archon.",
            "Sixteen years after the fall of Constantinople, Frankish "
            "magi who have settled in Thebes mean to change its ways, "
            "and Gigas campaigns for Latin over Greek. Cases that "
            "might reach the People's Court include Formosos's charge "
            "that Passara serves the Latin emperor, and the riddle of "
            "the mysterious knight who saved the Nicene emperor in "
            "1211.",
        ),
        secrets="The logothete's election is the second stage of An Enemy "
        "Within. Gemma and Bobila of Ingasia have quietly sold Nicaea "
        "more enchanted items than the Code's five a year allow; if "
        "that comes out, Ingasia's neutrality is in question.",
        antagonist="The Tribunal's factions and leagues",
        moves=DATED,
        stages=[
            S(
                "Pancratius's Gauntlet",
                year=1221,
                season="Summer",
                clues=(
                    "Syagricus's apprentice Pancratius hopes to pass his "
                    "Gauntlet at the meeting and join Moero's Garden. "
                    "Trasaric and Helladius count on his voice to commit the "
                    "covenant to the Nicene emperor's cause."
                ),
                ignored=(
                    "He becomes a full member and the covenant leans toward "
                    "the League of Constantine."
                ),
                stopped="His Gauntlet is delayed, and the covenant stays split.",
                turned=(
                    "The troupe befriends the new magus, a polites from his first day."
                ),
            ),
            S(
                "Caterina's citizenship",
                year=1221,
                season="Summer",
                clues=(
                    "In the Hermetic Assembly Caterina da Vigonovo of "
                    "Polyaigos, a metoikos, may seek a decree of "
                    "citizenship: without it she can earn no tokens, and "
                    "without tokens the Tribunal will never sponsor the "
                    "Longevity Ritual her waning vigour now demands. She "
                    "needs evidence of service to the polity, a home at an "
                    "established covenant (she has one) and an arche to "
                    "sponsor her. Many Jerbiton magi distrust her as a "
                    "Venetian."
                ),
                ignored=(
                    "No arche will sponsor her, and she looks for a ritual "
                    "elsewhere, perhaps through her dealings with the Duke "
                    "of Naxos."
                ),
                stopped="The Assembly votes the decree down.",
                turned=(
                    "An arche of the troupe sponsors her, and she becomes a "
                    "polites in its debt."
                ),
            ),
            S(
                "Nanno and Ampelius",
                year=1221,
                season="Summer",
                clues=(
                    "Ziper of Moero's Garden wants two of the covenant's "
                    "craftsmen admitted to House Jerbiton: Nanno, who makes "
                    "wondrous cosmetics, and the painter Ampelius, whose "
                    "murals carry small enchantments. Neither has the Gift. "
                    "Proximios supports the idea, pointing to his own House "
                    "of unGifted members. The rest of the covenant, Syagricus "
                    "apart, is appalled, less at the missing Gift than at "
                    "the thought of artisans as sodales. The pair threaten "
                    "to sail to Delos and put their case to the whole "
                    "Tribunal."
                ),
                ignored=(
                    "The petition embarrasses Moero's Garden in public, "
                    "whichever way it goes."
                ),
                stopped="The craftsmen are talked out of it, or the Assembly refuses.",
                turned=(
                    "The troupe finds them a place that keeps everyone's "
                    "dignity, and wins two grateful artisans."
                ),
            ),
            S(
                "The petition against the Propitiation",
                year=1221,
                season="Summer",
                clues=(
                    "Before the Law Council the League Against Idolatry, "
                    "the magae of Oikos tou Eleous and the magi of Gigas "
                    "with lukewarm help from Artoud of Xylinites, asks that "
                    "the Ceremony of Propitiation be banned as worship of "
                    "false gods. The Legislative Board demands an "
                    "alternative ruling, and two archai are drawn by lot to "
                    "argue for and against. Kristophoros of Bonisagus may "
                    "lend his tongue to the petitioners."
                ),
                ignored=(
                    "The ceremony goes on as ever, and the quarrel grows angrier."
                ),
                stopped="The petition is defeated and the rite stands.",
                turned=(
                    "A new ruling draws the line between veneration and "
                    "worship in words both sides can accept."
                ),
            ),
            S(
                "The logothete",
                year=1221,
                season="Summer",
                clues=(
                    "Leontius, who escaped ostracism by a whisker in 1214 "
                    "after records went missing and the register of tokens "
                    "and shards was found faulty, resigns. The post falls "
                    "vacant for the first time since it was made permanent, "
                    "and the Redcaps propose Proximios."
                ),
                ignored="Proximios becomes logothete (An Enemy Within).",
                stopped="Another Redcap is chosen.",
                turned=(
                    "The troupe puts the faulty register right before it "
                    "changes hands, and learns whose tallies were wrong."
                ),
            ),
            S(
                "The sortition",
                year=1221,
                season="Summer",
                clues=(
                    "In the Council of Archai the outgoing archai are "
                    "thanked and paid two tokens each; Maria Laskarina, "
                    "polemarch since 1207, takes five and Aiakia three. "
                    "Each phyle's Redcap reads out its candidates, starting "
                    "with the principal phyle, and the logothete draws four "
                    "names from the jar for each. The sixteen new archai "
                    "choose an archon, then a polemarch, most likely Maria "
                    "once more."
                ),
                ignored="The lot falls where it falls.",
                stopped=("A polites refuses candidacy, and takes a shard for it."),
                turned=(
                    "A player magus is drawn as an arche, and the troupe "
                    "has a seat on a board for seven years."
                ),
            ),
        ],
    )


# -- the wars of the successor states --


def _epiros(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_epiros"] = b.threat(
        "Epiros against Thessaloniki",
        summary=paragraphs(
            "Theodore Komnenos Doukas, who rules Epiros from Arta, "
            "is carving up the Kingdom of Thessaloniki. He has taken "
            "most of Thessaly, Ohrid and Pelagonia, and in 1217 "
            "captured the Latin emperor Peter on the Via Egnatia, who "
            "has not been seen since. His army is largely Frankish "
            "mercenaries; King Demetrios, fifteen years old, defends "
            "his Frankish kingdom with a largely Greek one, and the "
            "fighting is heavy and constant. Count Oberto of Biandrate "
            "still works for the claim of William of Montferrat, and "
            "the new Latin emperor, Robert, will not reach "
            "Constantinople before 1221. Few think the city can hold "
            "much longer.",
            "Thessaloniki's patron, Saint Demetrios, has risen to save "
            "his city before, most recently against Tsar Kaloyan in "
            "1207, but only when its cause is just. The magae of Oikos "
            "tou Eleous are sworn to the young king's protection and "
            "to the city's survival, which may draw them over the line "
            "into mundane affairs. Erebos's valley already lies in "
            "Epirote Thessaly, and the Frankish covenant of "
            "Novocastrum died resisting Epiros in 1212.",
        ),
        secrets="The book tells the war only to 1220. The later stages follow "
        "history in broad strokes; a troupe whose saga takes another "
        "road changes them.",
        antagonist="Theodore Komnenos Doukas, ruler of Epiros",
        moves=DATED,
        stages=[
            S(
                "The noose tightens",
                year=1220,
                season="Summer",
                clues=(
                    "Epirote columns close on Thessaloniki from the north "
                    "and the west. Refugees crowd the roads; Frankish lords "
                    "weigh which side will leave them their estates."
                ),
                ignored=("Town after town of the kingdom goes over to Epiros."),
                stopped=(
                    "The kingdom finds allies, or the new emperor sends help in time."
                ),
                turned=(
                    "A covenant that shelters refugees or a threatened "
                    "monastery is owed by whoever wins."
                ),
            ),
            S(
                "Serres and the hinterland",
                year=1221,
                season="Summer",
                clues=(
                    HISTORY + "Theodore takes Serres and most of the "
                    "kingdom's remaining towns, and the city is left almost "
                    "alone behind its walls."
                ),
                ignored="Thessaloniki is cut off by land.",
                stopped="The Epirote advance stalls before the city's hinterland.",
                turned=(
                    "The troupe profits from the shifting borders: a "
                    "vis site or a road that no lord now watches."
                ),
            ),
            S(
                "The king looks west",
                year=1222,
                season="Spring",
                clues=(
                    HISTORY + "Demetrios leaves for Italy to plead for help "
                    "from the pope and the western emperor, and his "
                    "regents hold the city in his name."
                ),
                ignored=("Help is promised from the west but comes slowly, if at all."),
                stopped="The king stays, and the city rallies around him.",
                turned=(
                    "Oikos tou Eleous, or the troupe, finds the king friends "
                    "abroad, at the risk of a charge of interference."
                ),
            ),
            S(
                "The fall of Thessaloniki",
                year=1224,
                season="Autumn",
                clues=(
                    HISTORY + "the city yields to Theodore after a long "
                    "siege, and the Latin kingdom of Thessaloniki ends. "
                    "Whether Saint Demetrios rises depends on whose cause "
                    "is just."
                ),
                ignored=(
                    "Epiros holds the empire's second city, and Oikos tou "
                    "Eleous lives under a new and harsh lord."
                ),
                stopped=(
                    "The saint, a relief army or the city's own stubbornness "
                    "keeps Theodore out."
                ),
                turned=(
                    "The covenant eases the surrender, sparing the city a "
                    "sack like 1185, and is remembered by its people."
                ),
            ),
            S(
                "An emperor at Thessaloniki",
                year=1227,
                season="Spring",
                clues=(
                    HISTORY + "Theodore has himself crowned emperor at "
                    "Thessaloniki, a rival to Nicaea in the race for "
                    "Constantinople."
                ),
                ignored=(
                    "Two Greek emperors now claim the Queen of Cities, and "
                    "the successor states turn on each other."
                ),
                stopped="The crowning is delayed or denied by the churchmen.",
                turned=(
                    "The troupe's friends at court shape what the new "
                    "emperor wants from the magi, and from the Church."
                ),
            ),
        ],
    )


def _nicaea(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_nicaea"] = b.threat(
        "Nicaea against the Latins",
        summary=paragraphs(
            "Theodore Laskaris, who fled Constantinople in 1204 and was "
            "crowned emperor at Nicaea in 1208, has sworn to win the "
            "city back. His peace with the Latins, sealed in 1219 by "
            "his marriage to a niece of Emperor Henry, has broken: in "
            "1220 the two empires are at war again. Many of the Latin knights who "
            "held the Troad are away fighting the Bulgarians, and "
            "Theodore has gathered his forces to take Holkos on the "
            "Hellespont as a second naval base against Venetian "
            "shipping. Bithynia's coastal castles, which have changed "
            "hands many times, wait to see who comes next.",
            "Theodore is also ready to put the Eastern Church under "
            "Rome for a while if it buys him the city, and has called "
            "churchmen together to end the schism. A small Nicene "
            "garrison, sent to guard Smyrna against the Turks, has "
            "taken over Alexandria's ruined citadel and shut the "
            "covenfolk out, knowing nothing of the regiones within. "
            "At Moero's Garden, members of the League of Constantine "
            "want the covenant to back the emperor.",
        ),
        secrets="The book calls him Theodore II; history has Theodore I "
        "Laskaris. It says the invasion succeeded and the Latins, "
        "harried from the north, sued for peace in 1221. The later "
        "stages follow history in broad strokes.",
        antagonist="Theodore I Laskaris, Emperor of Nicaea",
        moves=DATED,
        stages=[
            S(
                "The landing at Holkos",
                year=1220,
                season="Summer",
                clues=(
                    "Troops mass along the Bithynian border, and a Nicene "
                    "fleet gathers. The army crosses into the Troad and "
                    "falls on Holkos while its Latin lords are away."
                ),
                ignored="Holkos falls and the Nicene navy has a base on the Straits.",
                stopped="The Latins return in time and the attack fails.",
                turned=(
                    "The covenant helps one side through a crossing or a "
                    "siege, and must hope the Tribunal never hears of it."
                ),
            ),
            S(
                "The council of union",
                year=1220,
                season="Autumn",
                clues=(
                    "Bishops and papal envoys argue at Nicaea over the "
                    "Holy Spirit's procession, leavened bread and the "
                    "pope's primacy. The patriarch and the Anatolian sees "
                    "must be won over."
                ),
                ignored="The talks founder, as such talks always have.",
                stopped="The bishops reject union outright.",
                turned=(
                    "A covenant with friends among the clergy learns which "
                    "churchmen can be moved, and why."
                ),
            ),
            S(
                "The Latins sue for peace",
                year=1221,
                season="Spring",
                clues=(
                    "Pressed from the north and leaderless until Robert of "
                    "Courtenay arrives, the Latin regency asks for terms."
                ),
                ignored=(
                    "Nicaea keeps its gains, and the Latin empire shrinks "
                    "toward its capital."
                ),
                stopped="The war drags on without a peace.",
                turned=(
                    "The peace talks need go-betweens, and magi with the "
                    "Gentle Gift are in demand."
                ),
            ),
            S(
                "A new emperor at Nicaea",
                year=1221,
                season="Winter",
                clues=(
                    HISTORY + "Theodore dies and his son-in-law John Doukas "
                    "Vatatzes takes the throne. Theodore's brothers, passed "
                    "over, flee to the Latins and bring the war back."
                ),
                ignored="The succession is fought over in the field.",
                stopped="The brothers are reconciled and the peace holds.",
                turned=(
                    "The covenant earns the new emperor's goodwill, and "
                    "the Tribunal's watchful eye."
                ),
            ),
            S(
                "Poimanenon",
                year=1224,
                season="Spring",
                clues=(
                    HISTORY + "John beats the Latin army at Poimanenon and "
                    "takes almost all their lands in Asia; the Latin "
                    "empire is left with little beyond the city."
                ),
                ignored=(
                    "Nicaea becomes the strongest of the Greek states, and "
                    "the League of Constantine's hopes rise."
                ),
                stopped="The Latins hold their Anatolian lands.",
                turned=(
                    "The covenant gains land, rights or a vis site on the new border."
                ),
            ),
        ],
    )


# -- the dormant stories --


def _akgah(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_akgah"] = dormant(
        b.threat(
            "Akgah's War",
            summary="The magi of Thebes know that the Infernal had a hand in "
            "the Fourth Crusade, though not whose: demons stood behind "
            "Andronikos Komnenos's massacre of the Latins in 1182, "
            "behind the sack of Zara and the crusaders' "
            "excommunication, and in the hordes that came over the "
            "walls in 1204. Since then the successor states have "
            "fought one another without pause.",
            secrets=paragraphs(
                "It was the design of Akgah, a prince of Hell with an "
                "Infernal Might of 50 and the Hagka's enemy and mirror: "
                "a two-headed winged leopard the size of an elephant, "
                "a mockery of the lion of Venice, gold and black with "
                "golden wings and a sweet smell, whose company fills "
                "men with greed, lust and battle-madness (see the "
                "Bestiary). In 1204 it fought the Hagka in the "
                "Hippodrome, wrecking part of the arena, and drove it "
                "off wounded; crusaders who saw it thought they had "
                "seen Venice's lion triumph by God's will.",
                "Its success has raised it high among the princes of "
                "Hell. Now it keeps the old empire's heirs at war and "
                "feeds their distrust and greed. Its lair lies about a "
                "dozen miles outside Constantinople, an Infernal regio "
                "like a ruined battlefield, where it gorges on heaps of "
                "corpses among looted treasure and defiled relics, "
                "with hundreds of bodies hung on pikes around it.",
            ),
            antagonist="Akgah, the demon of the Fourth Crusade",
            realm="Infernal",
            stages=[
                S(
                    "Treaties broken",
                    at=1,
                    clues=(
                        "Envoys are murdered on the road, a truce breaks "
                        "over a petty slight, and each court blames the "
                        "other's treachery."
                    ),
                    ignored="The successor states bleed one another white.",
                    stopped=(
                        "The troupe shows a broken treaty to be the work of "
                        "a third hand."
                    ),
                    turned="Both courts owe the covenant for keeping a peace.",
                ),
                S(
                    "The lion's visions",
                    at=2,
                    clues=(
                        "Soldiers of one army or another see a winged "
                        "beast in the sky before battle and fight like "
                        "madmen; the plunder afterwards is savage."
                    ),
                    ignored=(
                        "Infernal auras spread across the battlefields of "
                        "Thrace and Bithynia."
                    ),
                    stopped="The visions are exposed as the demon's work.",
                    turned=(
                        "The troupe learns the beast's true name, and the "
                        "way to its lair."
                    ),
                ),
                S(
                    "The blasted field",
                    at=3,
                    clues=(
                        "Searchers for the relics lost in 1204 trace some "
                        "to a regio outside the city, where the stench of "
                        "corpses carries for miles."
                    ),
                    ignored=(
                        "Akgah grows mightier, and its war spreads to the "
                        "Order's covenants."
                    ),
                    stopped=(
                        "Akgah is driven from its lair, perhaps with the "
                        "Hagka's help, and the relics are recovered."
                    ),
                    turned=(
                        "Recovered relics win the Church's gratitude and "
                        "some holy power for the covenant."
                    ),
                ),
            ],
        )
    )


def _lucian(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_lucian"] = dormant(
        b.threat(
            "Lucian's Pacts",
            summary=paragraphs(
                "The Children of Olympos, a small and eccentric league "
                "led by Lucian the Scholar of Aegaea, want the old "
                "Greek gods as the covenants' patrons. Lucian argues "
                "that the Divine and the Infernal have used the Order "
                "badly, that Magic's creatures care nothing for men, "
                "and that the gods, faeries who live on the hearts of "
                "men, have outlasted every rival. Its members are "
                "mostly Merinita; it has sympathisers, and few "
                "members.",
                "Lucian believes stories feed the power of Faerie, and "
                "that the old myths must be lived, not just retold. He "
                "has cast many of the Tribunal's magi and covenants in "
                "parts of his great reenactment and nudges them toward "
                "their roles, which explains the sudden turns in his "
                "politics that others take for treachery. Lucian and "
                "his league prize the Great Altar at Pergamos, which "
                "powers rituals without vis.",
            ),
            secrets=paragraphs(
                "Lucian has devised two Mysteries, Elysian Ecstasy and "
                "the Olympian Pact, by which a person channels a god "
                "who possesses him; in the end the god may overwhelm "
                "the channeller and walk the earth in his body. He has "
                "initiated every member who knows the first, and holds "
                "the only Olympian Pact himself. Beneath his plan lies "
                "a hope he does not voice: that Faerie auras will "
                "replace the Magic ones of most covenants, and the old "
                "worship return.",
                "He thinks he channels the gods themselves, but they "
                "may be pretenders, faerie or Infernal; his Twilight "
                "Scars make him forget who he is when a god rides him. "
                "No channelled god has yet agreed to be a patron. "
                "Proximios knows of the plan and wants an infernalist "
                "among the initiates, so that what the league binds is "
                "a False God (An Enemy Within).",
            ),
            antagonist="Lucian the Scholar and the gods he channels",
            realm="Faerie",
            stages=[
                S(
                    "A part in the story",
                    at=1,
                    clues=(
                        "Lucian suddenly backs the troupe at Tribunal, or "
                        "turns against it, and greets a player magus by the "
                        "name of a hero from myth."
                    ),
                    ignored=(
                        "The covenant is steered, unknowing, toward the "
                        "fate of its part."
                    ),
                    stopped="The troupe sees through the casting and refuses it.",
                    turned="The troupe plays its part well, and Lucian's favour follows.",
                ),
                S(
                    "Twelve boons",
                    at=2,
                    clues=(
                        "An initiate travels the Tribunal asking boons of "
                        "twelve mighty beings, each standing for one "
                        "Olympian; a player magus or the covenant's patron "
                        "may be one of them."
                    ),
                    ignored="The league gains another initiate.",
                    stopped="The troupe refuses the boon, and the initiation fails.",
                    turned=(
                        "The troupe learns the Mystery's script, and may "
                        "seek initiation itself."
                    ),
                ),
                S(
                    "A god for a patron",
                    at=3,
                    clues=(
                        "A channelled god agrees to become a covenant's "
                        "patron; the covenant's Magic aura begins to take "
                        "on a faerie glamour."
                    ),
                    ignored=(
                        "Faerie spreads through the covenants, and the "
                        "Propitiation becomes worship in earnest."
                    ),
                    stopped="The pact is broken before the god takes hold.",
                    turned=(
                        "The covenant gains a mighty patron on terms it can live with."
                    ),
                ),
                S(
                    "A False God",
                    at=4,
                    clues=(
                        "The god that answers the league is colder and "
                        "hungrier than the myths, and its initiates' sins "
                        "grow."
                    ),
                    ignored=(
                        "A demon sits on a covenant's plinth at Delos, fed "
                        "with vis at every Propitiation."
                    ),
                    stopped=(
                        "The deceiver is unmasked and banished, and the "
                        "infernalist among the initiates exposed."
                    ),
                    turned="The trail leads the troupe to Proximios.",
                ),
            ],
        )
    )


def _kampe(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_kampe"] = dormant(
        b.threat(
            "Kampe's Lovers and the Titans",
            summary=paragraphs(
                "Three loose factions study the imprisoned titans, all "
                "named in mockery by Lucian four Tribunals ago: the "
                "Seekers of the Fallen, who would restore them to "
                "usher in a new age of magic (Evantia of Moero's "
                "Garden is their most respected member); the Legion "
                "of Atlas around Kristophoros of Bonisagus, who would "
                "bring down the faerie gods; and Kampe's Lovers, named "
                "for the she-dragon who keeps the gates of Tartaros, "
                "who draw on the titans' power and want a closer bond "
                "with them. Tisiphon of Hedyosmos, a Tytalan Quaesitor "
                "of the Titanoi, is the best known of these.",
                "Hedyosmos sits over a gate to the Underworld guarded "
                "by its patron, the nymph Minthe, and the Terram aura "
                "of the labyrinth beneath it strengthens the deeper "
                "one goes. Rumour has always tied the covenant to the "
                "Sundering of 848, when Typhon is said to have been "
                "loosed on Dorostolon and then bound again.",
            ),
            secrets="In Thebes the threskeia geine of Hedyosmos is the heart "
            "of Kampe's Lovers: it has taken over Hades's old offices "
            "without honouring him, and quietly works to loosen his "
            "grip on the titans' prison, hoping to bring them back "
            "and begin a golden age of magic. Minthe's gate is the "
            "key to that plan. Since 1204 many ancient bindings across "
            "the Tribunal have failed, and no living magus could mend "
            "the greatest of them.",
            antagonist="The threskeia geine of Hedyosmos and Kampe's Lovers",
            realm="Magic",
            stages=[
                S(
                    "Deeper in the labyrinth",
                    at=1,
                    clues=(
                        "Earth elementals wander up from the lower passages "
                        "of Hedyosmos, the ground shakes in Elis, and the "
                        "covenant's grogs are forbidden levels they used "
                        "to patrol."
                    ),
                    ignored="The cult's work below goes on unseen.",
                    stopped=(
                        "The Tribunal learns of the cult's aim and the "
                        "Judicial Board takes an interest."
                    ),
                    turned=(
                        "The troupe trades help for a share of the cult's Terram lore."
                    ),
                ),
                S(
                    "A binding fails",
                    at=2,
                    clues=(
                        "One of the giants buried under a mountain or an "
                        "island stirs; Nicomedia's century of quiet ends "
                        "early; the Legion of Atlas and the Seekers both "
                        "rush to the spot."
                    ),
                    ignored="A titan's child walks free, and the land suffers.",
                    stopped="The binding is renewed, at great cost in vis.",
                    turned=(
                        "The troupe learns a fragment of the lost "
                        "epanankoi, the binding magic of the ancients."
                    ),
                ),
                S(
                    "The gate of Tartaros",
                    at=3,
                    clues=(
                        "Minthe grows strange and distant; the aura at the "
                        "bottom of the labyrinth rises past anything known."
                    ),
                    ignored=(
                        "The gate opens, the titans' power floods into the "
                        "world, and the gods, and every faerie patron, are "
                        "shaken."
                    ),
                    stopped="The gate is sealed and the cult's leaders brought to account.",
                    turned=(
                        "The troupe passes the gate into the Magic Realm, "
                        "and returns changed."
                    ),
                ),
            ],
        )
    )


def _klymene(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_klymene"] = dormant(
        b.threat(
            "Klymene's Prison",
            summary="On the acropolis of Pergamos stands the Great Altar, its "
            "friezes showing the gods' war with the titans; Christians "
            "shun it as Satan's throne. It has a Faerie aura of 4, and "
            "any Hermetic ritual cast from its top needs no vis, though "
            "a botch is tainted as if with faerie vis and even a good "
            "casting can go oddly. The locals have driven magi off "
            "before, taking them for devil-worshippers, and with vis "
            "so plentiful few bother. Lucian's league is drawn to it.",
            secrets="The altar is the lock on the prison of Klymene, titaness "
            "of fame, a Kosmokrator Spirit of Magic Might 50 (see the "
            "Bestiary), one of the titanesses who stayed out of the "
            "war and was bound somewhere kinder than Tartaros. The "
            "free rituals draw on her. Her bonds have a strength of "
            "50, renewed every year, and each ritual cast there wears "
            "them down by the pawns it would have cost; if they reach "
            "nothing within one year, the altar splits in two and she "
            "goes free. She thought her cell a mercy shared with her "
            "sisters, and freed she has nowhere to go.",
            antagonist="Klymene, the titaness of fame",
            realm="Magic",
            stages=[
                S(
                    "Rituals for nothing",
                    at=1,
                    clues=(
                        "Word spreads that rituals at Pergamos cost no vis; "
                        "the Children of Olympos and thrifty magi come to "
                        "cast them, and the townsfolk grow angry."
                    ),
                    ignored="The altar is used more each year.",
                    stopped="The Tribunal discourages its use.",
                    turned=(
                        "The troupe learns what powers the altar, and can "
                        "use it wisely or warn others."
                    ),
                ),
                S(
                    "The altar cracks",
                    at=2,
                    clues=(
                        "After a year of heavy use, fissures run through "
                        "the friezes and the altar hums at night."
                    ),
                    ignored="The altar splits and Klymene is released.",
                    stopped="The rituals stop in time and the bonds renew.",
                    turned=(
                        "The troupe parleys with the waking titaness "
                        "before she is free."
                    ),
                ),
                S(
                    "Klymene unbound",
                    at=3,
                    clues=(
                        "A great presence settles on a mountaintop, or "
                        "roams the Tribunal seeking her imprisoned sisters."
                    ),
                    ignored=(
                        "She frees other titanesses, overturning the land "
                        "and its people."
                    ),
                    stopped="She returns to the Magic Realm, leaving a ruined altar.",
                    turned="She becomes a mighty, unpredictable friend.",
                ),
            ],
        )
    )


def _hades(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_hades"] = dormant(
        b.threat(
            "The Estate of Hades",
            summary="Hedyosmos stands on the ruins of an oracle of the dead, "
            "once one of the few places where Hades was worshipped. "
            "Its magi honour the nymph Minthe, never the god.",
            secrets="Vrakos, the covenant's cook, beneath the magi's notice, "
            "has been won over by Askalaphos, a faerie servant of "
            "Hades whom Demeter cursed into a screech owl for "
            "betraying that Persephone ate the pomegranate seeds. "
            "Vrakos now holds secret rites in the covenant's depths as "
            "a priest of Hades, asks for milk, honey and the blood of "
            "a black ram, and is cautiously recruiting among the "
            "servants. Askalaphos means in time to take the covenant "
            "back as a temple of his lord and be rid of the magi. The "
            "Aegis of the Hearth bars him, and he is looking for a way "
            "to be invited into its ritual.",
            antagonist="Askalaphos, the owl of Hades, and his priest Vrakos",
            realm="Faerie",
            stages=[
                S(
                    "Offerings in the dark",
                    at=1,
                    clues=(
                        "Milk and honey go missing from the stores, a black "
                        "ram is bought and never eaten, and a screech owl "
                        "calls near the ruined oracle."
                    ),
                    ignored="The cult grows among the covenfolk.",
                    stopped="Vrakos is found out and the owl driven away.",
                    turned=(
                        "The troupe turns the cook, and learns what Askalaphos wants."
                    ),
                ),
                S(
                    "Within the Aegis",
                    at=2,
                    clues=(
                        "A servant of the cult asks to bring a bird into "
                        "the covenant, or a token is slipped among the "
                        "Aegis's ritual offerings."
                    ),
                    ignored="Askalaphos is invited within the Aegis.",
                    stopped="The Aegis is cast clean, and the faerie stays out.",
                    turned="The troupe sets a trap for the faerie at the ritual.",
                ),
                S(
                    "The temple reclaimed",
                    at=3,
                    clues=(
                        "Lamps fail in the forbidden passages, covenfolk "
                        "refuse orders, and the magi's sancta are "
                        "tampered with."
                    ),
                    ignored=(
                        "Hedyosmos's people rise for Hades, and the "
                        "covenant must fight its own household."
                    ),
                    stopped="The cult is broken and its faerie patron banished.",
                    turned=(
                        "A bargain with Hades's servant gives the covenant "
                        "a new and dangerous ally below."
                    ),
                ),
            ],
        )
    )


def _tremere_appeal(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_tremere_appeal"] = dormant(
        b.threat(
            "The Tremere Appeal of 1228",
            summary="The League of Advisors, Greek magi who after 1185 lived "
            "at the emperor's court and claimed they only advised, "
            "lost many members with Thermakopolis in 1204 and broke up "
            "under charges of meddling with mundanes. The Tribunal "
            "failed to convict its survivors. House Tremere, which "
            "Thebes has distrusted since the Sundering and which "
            "blames Theban magi for the empire's war on Bulgaria in "
            "1014, has appealed to the Grand Tribunal of 1228 to try "
            "the two surviving members again.",
            secrets="If the appeal succeeds, a Grand Tribunal will have "
            "overturned a Tribunal's own verdict, which bears on every "
            "Tribunal's independence and on the Theban polity most of "
            "all. Boustaphan of Gigas, Tremere's voice in Thebes, "
            "holds proxies from the House's younger magi.",
            antagonist="House Tremere, through Gigas",
            moves=DATED,
            stages=[
                S(
                    "Lobbying on Delos",
                    year=1221,
                    season="Summer",
                    clues=(
                        "Allectores of Gigas courts magi at the meeting, "
                        "and Gigas presses its case for the Order's common "
                        "ways over Theban custom."
                    ),
                    ignored="The Tremere gather friends for the appeal.",
                    stopped="The Tribunal resolves to defend its verdict as one.",
                    turned="The troupe trades its support to Gigas for favours.",
                ),
                S(
                    "Witnesses sought",
                    year=1226,
                    season="Spring",
                    clues=(
                        "Tremere agents search for anyone who saw the "
                        "Advisors at court, and for letters from the "
                        "fallen palace."
                    ),
                    ignored="The appeal arrives at the Grand Tribunal with new evidence.",
                    stopped="The witnesses are found first, or their tales discredited.",
                    turned="The troupe holds the evidence that decides the case.",
                ),
                S(
                    "The Grand Tribunal",
                    year=1228,
                    season="Summer",
                    clues=(
                        "The Grand Tribunal hears the appeal; Theban magi "
                        "who travel there earn a token for the service."
                    ),
                    ignored=(
                        "The verdict is overturned, and Thebes's right to "
                        "judge its own is in doubt."
                    ),
                    stopped="The appeal fails and the polity's verdict stands.",
                    turned=(
                        "The troupe's advocacy wins a ruling that guards "
                        "every Tribunal's independence."
                    ),
                ),
            ],
        )
    )


def _verditius_contest(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_verditius"] = dormant(
        b.threat(
            "The Verditius Contest of 1234",
            summary="Stouritus of Ingasia, newly primus of House Verditius, has "
            "chosen to stay on Lemnos rather than move to Verdi, which "
            "makes Ingasia the domus magna in all but name. Ingasia's "
            "magi say their forge, Hephaistos's own, is older than "
            "Verdi. Stouritus wants the next Contest, due in 1234, "
            "held there: he has plans drawn for grander buildings "
            "above ground and more laboratories below, Egyptian marble "
            "and Trebizond oak on order, and masons hired from the "
            "villages, and he has opened Ingasia to new Verditius "
            "members to show the Order a welcoming house beside a "
            "quarrelsome Verdi. The House is split between the two "
            "covenants' partisans.",
            secrets="Ingasia's neutrality, and so its trade, would suffer if "
            "Gemma and Bobila's secret sales to Nicaea came out.",
            antagonist="The rivalry of Verdi and Ingasia",
            stages=[
                S(
                    "Death of an Artificer",
                    at=1,
                    clues=(
                        "Simon of Newmarket, a Verditius bound for Ingasia "
                        "to discuss the Contest, is found hacked apart in a "
                        "disused well in Constantinople's back streets. "
                        "Each faction suspects the other; the characters "
                        "may be suspects, archai or foreign Quaesitores."
                    ),
                    ignored="The House's quarrel turns murderous in rumour.",
                    stopped=(
                        "The truth comes out: a frightened mob killed him "
                        "for the runes on his brooch, his Gift and his open "
                        "spellcasting, and no magus was to blame."
                    ),
                    turned=(
                        "The troupe's finding calms the House, and both "
                        "factions owe it."
                    ),
                ),
                S(
                    "Building on Mosychlos",
                    at=2,
                    clues=(
                        "Shiploads of marble and oak arrive on Lemnos and "
                        "gangs of workmen dig into the volcano's slopes, "
                        "stirring its ill-tempered spirit."
                    ),
                    ignored=(
                        "Mosychlos rumbles, tunnels collapse and lava "
                        "creeps into the labyrinth."
                    ),
                    stopped="The work is scaled back to keep the patron calm.",
                    turned="The troupe helps shore up the works, and is welcome at the Contest.",
                ),
                S(
                    "The Contest",
                    at=3,
                    clues=(
                        "The House decides where the Contest of 1234 will "
                        "be held, and Verditius magi from across the Order "
                        "look to Lemnos or to Verdi."
                    ),
                    ignored="The choice is made without the Tribunal's say.",
                    stopped="The Contest stays at Verdi, and Ingasia's pride is hurt.",
                    turned=(
                        "The Contest comes to Thebes, and with it rare "
                        "trade and a gathering of the Order's finest "
                        "craftsmen."
                    ),
                ),
            ],
        )
    )


def _talos(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_talos"] = dormant(
        b.threat(
            "Talos of Candia",
            summary="Talos, the bronze bull-headed giant that Hephaistos made "
            "for King Minos, guards Candia again. Medea once drained "
            "the ichor from his single vein by pulling the nail in "
            "his ankle, and a local alchemist later brewed him new "
            "blood. Byzantine magicians bound him for centuries in a "
            "cellar of the ruined Labyrinth of Knossos, but the spell "
            "failed lately. He runs round the island three times a "
            "day, stones any hostile ship, and seizes landing "
            "parties in a red-hot grip (see the Bestiary).",
            secrets="The Venetians who now rule Candia have put a fat price on "
            "the head of this demon, as they call him. House Verditius "
            "would give a great deal to learn how he was made, and he "
            "might serve a new covenant on Candia as its patron. His "
            "ichor holds 7 pawns of Ignem vis.",
            antagonist="Talos, the bronze guardian of Candia",
            realm="Magic",
            stages=[
                S(
                    "Ships lost off Candia",
                    at=1,
                    clues=(
                        "Venetian galleys come home holed by boulders or not "
                        "at all, and sailors tell of a bronze giant striding "
                        "the shore."
                    ),
                    ignored="Candia's trade withers.",
                    stopped="Ships learn to keep clear, and Talos's war cools.",
                    turned="The troupe finds a way to pass his watch unharmed.",
                ),
                S(
                    "The Venetian bounty",
                    at=2,
                    clues=(
                        "The duke of Candia's reward draws hunters, "
                        "adventurers and at least one magus who sees "
                        "seven pawns of Ignem walking the beaches."
                    ),
                    ignored="Talos is slain or captured, and his secrets are lost.",
                    stopped="The hunters fail, or are warned off by the Tribunal.",
                    turned=(
                        "The troupe takes Talos alive, for study or as an "
                        "ally, and must answer for it to the Venetians."
                    ),
                ),
                S(
                    "A guardian for a covenant",
                    at=3,
                    clues=(
                        "Magi talk of founding a covenant on Candia with "
                        "Talos as its patron."
                    ),
                    ignored="Another group founds it first.",
                    stopped="The bronze man refuses every pact.",
                    turned=(
                        "The troupe's new covenant has the mightiest of "
                        "guardians, and the Venetians as neighbours."
                    ),
                ),
            ],
        )
    )


def _naxos(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_naxos"] = dormant(
        b.threat(
            "The Duke of Naxos",
            summary="Marco Sanudo, nephew of the doge Enrico Dandolo, took the "
            "Cyclades between 1207 and 1212 and rules them as Duke of "
            "Naxos, a vassal of the Latin emperor in name and a friend "
            "of Venice in fact. Polyaigos lies within his duchy, and "
            "he has heard tales of the riches behind its famous "
            "school and envies them. Caterina da Vigonovo, who runs "
            "the covenant's mines and trade, has met him in the guise "
            "of a wealthy noblewoman and begun to arrange a quiet "
            "understanding.",
            secrets="Polyaigos's wealth comes from its quarry on Argentiera "
            "and from the old gold and silver mines of Sifnos, which "
            "it has reopened in secret. Satabus, the Verditius maga "
            "who has just joined Polyaigos from Ingasia, is the duke's "
            "younger brother Pietro, an odd and scholarly boy whom "
            "Dandolo placed somewhere before he died. Marco still "
            "wonders what became of him. Satabus knows of his "
            "brother's rise, still loves his family, and has not "
            "written.",
            antagonist="Marco Sanudo, Duke of Naxos",
            stages=[
                S(
                    "The duke's envy",
                    at=1,
                    clues=(
                        "Ducal officers ask who works the mines of Sifnos, "
                        "and a new tax falls on the goods Polyaigos buys on "
                        "Melos."
                    ),
                    ignored="The duke presses harder for a share.",
                    stopped="The officers are put off with gifts and answers.",
                    turned="The troupe wins the duke as a trading partner.",
                ),
                S(
                    "Caterina's arrangement",
                    at=2,
                    clues=(
                        "Caterina's dealings with the duke deepen; a rival "
                        "at Tribunal wonders aloud whether a Venetian maga "
                        "meddles in a Venetian lord's affairs."
                    ),
                    ignored=(
                        "The arrangement holds until someone brings it "
                        "before the Judicial Board."
                    ),
                    stopped="Caterina ends it before it becomes a crime.",
                    turned="The troupe shapes a deal the Code allows.",
                ),
                S(
                    "A brother found",
                    at=3,
                    clues=(
                        "Satabus writes to the duke at last, or the duke's "
                        "agents trace Pietro to the island of many goats."
                    ),
                    ignored=(
                        "The duke has a brother inside the covenant, and "
                        "the covenant a hostage to the duke's affection."
                    ),
                    stopped="Satabus keeps his secret.",
                    turned=(
                        "The reunion makes the duke Polyaigos's friend, if "
                        "the magi can keep it within the Code."
                    ),
                ),
            ],
        )
    )


def _hagka(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_hagka"] = dormant(
        b.threat(
            "The Lost Hagka",
            summary=paragraphs(
                "Three things stand for the emperor's God-given "
                "authority: his battle standard, his crown and the "
                "hagka, a bronze two-headed eagle on a long lance with "
                "an icon of the Virgin hung from it. Together they are "
                "a great Divine power. In 1220 they are scattered: the "
                "standard was last seen when Isaac Angelos's army fled "
                "the Bulgarians in 1190, the crowns are the "
                "conquerors' loot, and the hagka has vanished. Alexios "
                "V lost it, with his crown, to a band of French knights "
                "outside Philia in 1204. Many say the empire will not "
                "mend until one emperor holds all three.",
                "The League of Constantine, Jerbiton magi centred on "
                "Moero's Garden with martial apprentices near their "
                "Gauntlets, wants a Greek emperor back on the throne. "
                "It has learned that demons brought the city down, and "
                "is searching Bulgarian lands for the standard in "
                "hope of a clue to the hagka.",
            ),
            secrets="The league is right: the city suffers for losing God's "
            "favour, and the hagka, restored to a truly devout "
            "emperor, would give him Solomon's wisdom, David's "
            "strength and Paul's mercy, though not necessarily a "
            "Greek throne. But the demons hid themselves from the "
            "league's spells, and it cannot tell friend from foe. The "
            "icon may be whole or broken, in a crusader's treasury, a "
            "Greek monastery, the burned Venetian quarter or the bed "
            "of the Bosporus. The living Hagka, a Divine eagle of "
            "Might 40 wounded by Akgah, guards Nicaea from the "
            "wilderness of Asia Minor.",
            antagonist="The demons who hid the empire's fall, and time",
            realm="Divine",
            stages=[
                S(
                    "The standard in Bulgaria",
                    at=1,
                    clues=(
                        "League magi travel the Bulgarian lands asking about "
                        "the battle of 1190 and a golden eagle on a bronze "
                        "staff."
                    ),
                    ignored="The league's search draws the tsar's suspicion.",
                    stopped="The standard proves to be lost for good.",
                    turned="The troupe finds the standard, and its holder's price.",
                ),
                S(
                    "Where the eagle fell",
                    at=2,
                    clues=(
                        "A lead points to Philia, to a Latin lord's "
                        "treasury, a monastery's crypt or the waters of the "
                        "Bosporus; others, not all of them human, hunt the "
                        "same trail."
                    ),
                    ignored="Someone else finds the hagka first.",
                    stopped="The trail goes cold.",
                    turned="The hagka, whole or in part, is in the troupe's hands.",
                ),
                S(
                    "Three in one hand",
                    at=3,
                    clues=(
                        "Standard, crown and hagka are brought together for "
                        "one emperor; which one is the question."
                    ),
                    ignored=(
                        "Whoever holds them gains holy strength, and the "
                        "magi who helped are suspected of meddling."
                    ),
                    stopped="The relics stay apart and the empire stays broken.",
                    turned=(
                        "A devout emperor is made whole, and the Hagka's "
                        "wounds begin to heal."
                    ),
                ),
            ],
        )
    )


def _serapis(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_serapis"] = dormant(
        b.threat(
            "The Christians of Serapis",
            summary="Sinope, a Seljuk port on the Black Sea, is known for its "
            "tolerance: Christians, Muslims and Jews worship as they "
            "please under its Greek governor, Etoumes, a vassal of the "
            "sultan but no Muslim.",
            secrets="Hidden beneath the city is a heretical sect that worships "
            "Serapis in God's place. Alexander brought the idol to "
            "Anatolia; Ptolemy took it to Egypt and blended it with "
            "Egyptian gods; under Hadrian some Egyptian Christians "
            "took it up. Everyone believed the sect wiped out some "
            "nine hundred years ago, yet its idol was saved and "
            "carried in secret to Sinope. Serapis is a False God, a demon. About 200 "
            "follow him, led by a dozen priests who dress and serve "
            "like Orthodox clergy and convert quietly; few know what "
            "they worship, and Shroud the Stench of the Pit hides the "
            "Infernal taint of the powers he gives them. Etoumes has "
            "just taken one of the priests as his confessor, to the "
            "demon's delight.",
            antagonist="Serapis, a False God",
            realm="Infernal",
            stages=[
                S(
                    "A new confessor",
                    at=1,
                    clues=(
                        "Etoumes's household grows strangely devout; a "
                        "priest no bishop ordained is seen at his side."
                    ),
                    ignored="The governor falls under the priest's sway.",
                    stopped="The priest is exposed to the governor.",
                    turned="The troupe finds the sect's hiding place.",
                ),
                S(
                    "Converts in the port",
                    at=2,
                    clues=(
                        "Sailors and merchants speak of a church where the "
                        "liturgy is almost right; small miracles follow its "
                        "faithful."
                    ),
                    ignored=(
                        "The sect spreads along the trade routes of the Black Sea."
                    ),
                    stopped="The cult statue is found and destroyed.",
                    turned=(
                        "The troupe turns a priest, and learns the demon's "
                        "nature and weakness."
                    ),
                ),
                S(
                    "Sinope under the idol",
                    at=3,
                    clues=(
                        "The governor's edicts begin to favour the sect, "
                        "and its enemies disappear."
                    ),
                    ignored=(
                        "A city falls to a False God, and its tolerance "
                        "becomes its ruin."
                    ),
                    stopped="Serapis is cast down and the city's faiths freed.",
                    turned=(
                        "The covenant earns the thanks of three faiths, and "
                        "a demon's enmity."
                    ),
                ),
            ],
        )
    )


def _zeno(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_zeno"] = dormant(
        b.threat(
            "The Return of Zeno",
            summary="The Church of the Holy Apostles, once the resting place "
            "of emperors and patriarchs, was stripped by looters in "
            "1204 and keeps only a weak Divine aura. Magi of the city "
            "once hid occult books in its crypts, trusting the ghosts "
            "of dead emperors to guard them, and necromancers called "
            "up those emperors' unquiet souls there. Hermetic legend "
            "says many of both never came back up.",
            secrets="Beneath it lies Zeno, the Isaurian chieftain Tarasicodissa "
            "who ruled as emperor from 474 to 491 and was buried "
            "alive by his enemies. He did not die. Demon-blooded and "
            "proof against hunger and age, he lies in his open "
            "sarcophagus by day, while the church's Dominion holds an "
            "Infernal aura of 3 in check, and at night, when the "
            "Dominion weakens to 3 and the Infernal rises to 4, he "
            "climbs out to roam the church, killing and eating anyone "
            "he catches. Outside an Infernal aura he cannot live, so "
            "he cannot leave. Whatever lies in the crypts, he guards.",
            antagonist="Zeno, the buried emperor",
            realm="Infernal",
            stages=[
                S(
                    "Night in the church",
                    at=1,
                    clues=(
                        "A sacristan or a thief is found half-eaten among "
                        "the empty tombs; the priests lock the doors at "
                        "dusk."
                    ),
                    ignored="The deaths go on, and the church empties.",
                    stopped="The church is reconsecrated and its aura grows.",
                    turned="The troupe learns what lurks below, and when.",
                ),
                S(
                    "Treasures of the crypt",
                    at=2,
                    clues=(
                        "An old Hermetic letter names a tome hidden beneath "
                        "the Holy Apostles; rival magi want it too."
                    ),
                    ignored="Others go down after it, and do not return.",
                    stopped="The crypt is sealed for good.",
                    turned="The troupe overcomes Zeno and carries off the prize.",
                ),
                S(
                    "Zeno abroad",
                    at=3,
                    clues=(
                        "As the Infernal grows in the city, the dark aura "
                        "creeps out from the church into the streets."
                    ),
                    ignored=("Zeno can walk wherever the city's corruption reaches."),
                    stopped="He is destroyed in his tomb.",
                    turned="The troupe uses his hunger against a worse enemy.",
                ),
            ],
        )
    )


def _thermakopolis(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_thermakopolis"] = dormant(
        b.threat(
            "Thermakopolis Refounded",
            summary="Thermakopolis, the great Jerbiton covenant of "
            "Constantinople, swore to protect the city and promised "
            "the Tribunal all was well until the Latins were at the "
            "walls. Its Mentem magic could not sway crusade leaders "
            "who bore protections won from demons, and its magi's "
            "spells on the walls frightened the defenders more than "
            "the enemy. Four of the five died, and Michael with them; "
            "Mathieus fled west. It is still House Jerbiton's deepest "
            "shame.",
            secrets="Many Jerbiton magi, above all the apprentices close to "
            "their Gauntlets, long to plant a covenant in the city "
            "again; Michael's Tabula already holds the city's defence "
            "as its cause. The Tribunal cannot decide whether to "
            "encourage it, and most would wait and see. A founding "
            "needs a declared purpose, a willing patron living on the "
            "site, a charter and the Conciliatory Board's review, "
            "then a decree. The old site is the obvious ground.",
            antagonist="The Latin city, and the demons who still haunt it",
            stages=[
                S(
                    "A charter drafted",
                    at=1,
                    clues=(
                        "Young Jerbiton magi, Trasaric and Helladius among "
                        "them, seek sodales and a patron for a new covenant "
                        "in the city, and ask the troupe to join."
                    ),
                    ignored="The plan waits for another Tribunal.",
                    stopped="The Conciliatory Board finds the charter wanting.",
                    turned="The troupe becomes part of the founding.",
                ),
                S(
                    "A patron in the ruins",
                    at=2,
                    clues=(
                        "Among the burned ruins of the old covenant, a "
                        "spirit of the city stirs; so do things less "
                        "friendly."
                    ),
                    ignored="The ruin's Infernal taint deepens.",
                    stopped="No willing patron is found, and the founding fails.",
                    turned="A worthy patron swears to the new covenant.",
                ),
                S(
                    "A covenant in the Queen of Cities",
                    at=3,
                    clues=(
                        "The decree of founding is put to the Assembly; the "
                        "Latin authorities, and Akgah, take notice."
                    ),
                    ignored=(
                        "The new covenant's zeal drags it toward the "
                        "meddling that damned the old one."
                    ),
                    stopped="The Assembly votes the decree down.",
                    turned=(
                        "Thebes has a covenant in Constantinople again, "
                        "wiser for its predecessor's fall."
                    ),
                ),
            ],
        )
    )


def _wilusa(theban: Theban) -> None:
    b = theban.b
    theban.world["threat_wilusa"] = dormant(
        b.threat(
            "In Search of Wilusa",
            summary="In 1109 the Tribunal let Droserius of Merinita and four "
            "others found Wilusa at Ilion, where he said the spirit of "
            "the Scamander had promised to be their patron. By the "
            "next meeting covenant and magi were gone without trace, "
            "and since then the Tribunal has easily refused every "
            "proposal for a second covenant there. The plain of Troy "
            "is a tangle of overlapping Faerie regiones, each "
            "replaying a scene of the war, and its faeries snatch any "
            "visitor for their tales.",
            secrets="Wilusa was raised by magic in a Faerie regio of aura 4, "
            "but not the one holding the Scamander's spirit: a faerie "
            "who calls himself Odysseus tricked Droserius, sealed the "
            "regio and made the covenant look like Troy. Ever since he "
            "has put it through the war's last assault, and the magi "
            "defend it by reflex. He has bent time so that more than "
            "a century has passed outside while the magi think it a "
            "few months. Odysseus is very aware, and hopes to gather "
            "vitality enough to change his own story. Other regiones "
            "copy the fall of Troy too, so the troupe may beat the "
            "Greeks and find it is the wrong city. Rescued, Droserius "
            "and his sodales will not want to leave, until they learn "
            "how long they have been gone.",
            antagonist="The faerie Odysseus",
            realm="Faerie",
            stages=[
                S(
                    "Tales of a lost covenant",
                    at=1,
                    clues=(
                        "A Merinita brings back word of a Troy where men in "
                        "Hermetic robes defend the walls."
                    ),
                    ignored="The tale is forgotten for another century.",
                    stopped="The Tribunal forbids any search.",
                    turned="The troupe takes up the search.",
                ),
                S(
                    "The wrong Troy",
                    at=2,
                    clues=(
                        "Faeries of Ilion lead searchers into their own "
                        "stories; a Hektor or an Akhilles claims the "
                        "troupe for his tale."
                    ),
                    ignored="A searcher is lost in a regio.",
                    stopped="The troupe escapes the faeries' stories.",
                    turned="Deep Faerie Lore points to the true regio.",
                ),
                S(
                    "The siege that never ends",
                    at=3,
                    clues=(
                        "Inside Odysseus's regio the final assault begins "
                        "again, and the defenders take the troupe for "
                        "Greeks."
                    ),
                    ignored="The troupe becomes part of the siege.",
                    stopped=(
                        "Odysseus is outwitted, the regio opened, and "
                        "Wilusa's magi come home a hundred years late."
                    ),
                    turned=(
                        "The troupe gives Odysseus a new tale to tell, and "
                        "wins a strange faerie friend."
                    ),
                ),
            ],
        )
    )


# -- tying the stories to the other parts' records --


def _key(name: str) -> str:
    """A name compared loosely: case and a leading 'The' set aside."""
    out = name.casefold().strip()
    out = out.removeprefix("the ")
    return out.replace("-", " ").replace("’", "'")


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


def _slug(name: str) -> str:
    return _key(name).replace("'", "").replace(" ", "_")


def _add_to(record: Any, more: str, hidden: str = "") -> None:
    """Add a paragraph to a record's summary, and `hidden` to its
    secrets."""
    record.summary = paragraphs(record.summary, more)
    record.secrets = paragraphs(record.secrets, hidden)


#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target's possible keys or names, note).
LINKS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("threat_enemy_within", "characters", ("Proximios",), "The hidden infernalist"),
    (
        "threat_enemy_within",
        "characters",
        ("Hydatius",),
        "The Vigilant's general, his dupe",
    ),
    (
        "threat_enemy_within",
        "characters",
        ("Leontius",),
        "The logothete he will succeed",
    ),
    ("threat_enemy_within", "characters", ("Caterina",), "A target of false charges"),
    ("threat_enemy_within", "characters", ("Delfini",), "A target of false charges"),
    ("threat_enemy_within", "characters", ("Aiakia",), "To be turned on Gigas"),
    ("threat_enemy_within", "characters", ("Tisiphon",), "To be turned on Gigas"),
    (
        "threat_enemy_within",
        "characters",
        ("Boustaphan",),
        "Will not open Gigas's records",
    ),
    ("threat_enemy_within", "characters", ("Celaenea",), "To be set against Lucian"),
    ("threat_enemy_within", "characters", ("Lucian",), "Celaenea's intended target"),
    ("threat_enemy_within", "covenants", ("Alexandria",), "Proximios's covenant"),
    ("threat_enemy_within", "covenants", ("Ingasia",), "Hydatius's covenant"),
    ("threat_enemy_within", "covenants", ("Erebos",), "Its young magi to be accused"),
    ("threat_enemy_within", "covenants", ("Hedyosmos",), "To be turned on Gigas"),
    ("threat_enemy_within", "covenants", ("Gigas",), "The intended victim"),
    ("frame_1221", "places", ("delos", "Delos"), "Where the Tribunal meets"),
    ("frame_1221", "characters", ("Aiakia",), "The archon presides"),
    ("frame_1221", "characters", ("Maria Laskarina",), "The polemarch"),
    ("frame_1221", "characters", ("Leontius",), "Resigns as logothete"),
    ("frame_1221", "characters", ("Proximios",), "Proposed as logothete"),
    ("frame_1221", "characters", ("Caterina",), "Seeks citizenship"),
    ("frame_1221", "characters", ("Ziper",), "Proposes Nanno and Ampelius"),
    ("frame_1221", "characters", ("Syagricus",), "Pancratius's master"),
    ("frame_1221", "characters", ("Nanno",), "Asks to join House Jerbiton"),
    ("frame_1221", "characters", ("Ampelius",), "Asks to join House Jerbiton"),
    ("frame_1221", "characters", ("Pancratius",), "Due his Gauntlet"),
    ("frame_1221", "characters", ("Artoud",), "Half-hearted against the Propitiation"),
    ("frame_1221", "characters", ("Kristophoros",), "May speak against idolatry"),
    ("frame_1221", "characters", ("Formosos",), "Accuses Passara"),
    ("frame_1221", "characters", ("Passara",), "Accused of serving the emperor"),
    (
        "frame_1221",
        "covenants",
        ("Oikos tou Eleous",),
        "Petitions against the Propitiation",
    ),
    ("frame_1221", "covenants", ("Gigas",), "Petitions against the Propitiation"),
    ("frame_1221", "covenants", ("Moero's Garden",), "Pancratius and the craftsmen"),
    ("threat_epiros", "covenants", ("Oikos tou Eleous",), "Sworn to the boy-king"),
    ("threat_epiros", "covenants", ("Erebos",), "In Epirote Thessaly"),
    ("threat_epiros", "places", ("thessaloniki", "Thessaloniki"), "The besieged city"),
    ("threat_epiros", "places", ("arta", "Arta"), "Theodore's capital"),
    ("threat_nicaea", "covenants", ("Moero's Garden",), "The League of Constantine"),
    ("threat_nicaea", "covenants", ("Alexandria",), "A Nicene garrison in its citadel"),
    ("threat_nicaea", "places", ("nicaea", "Nicaea"), "The emperor's capital"),
    (
        "threat_nicaea",
        "places",
        ("holkos", "hellespont", "Holkos", "The Hellespont"),
        "The landing",
    ),
    ("threat_akgah", "creatures", ("Akgah",), "The demon itself"),
    (
        "threat_akgah",
        "places",
        ("hippodrome", "The Hippodrome"),
        "Where it beat the Hagka",
    ),
    ("threat_lucian", "characters", ("Lucian",), "The league's leader"),
    ("threat_lucian", "characters", ("Leukothea",), "Cast as Amphitrite"),
    ("threat_lucian", "characters", ("Celaenea",), "Jealous for Hermes"),
    ("threat_lucian", "characters", ("Proximios",), "Would plant an infernalist"),
    ("threat_lucian", "covenants", ("Aegaea",), "Lucian's covenant"),
    (
        "threat_lucian",
        "places",
        ("great_altar", "The Great Altar"),
        "The league's altar",
    ),
    ("threat_kampe", "characters", ("Tisiphon",), "The faction's best known member"),
    ("threat_kampe", "characters", ("Ausculator",), "Head of the threskeia geine"),
    ("threat_kampe", "characters", ("Aiakia",), "Keeper of the cult's rites"),
    ("threat_kampe", "characters", ("Kristophoros",), "The Legion of Atlas"),
    ("threat_kampe", "characters", ("Evantia",), "The Seekers of the Fallen"),
    ("threat_kampe", "covenants", ("Hedyosmos",), "Over the gate of Tartaros"),
    ("threat_klymene", "creatures", ("Klymene",), "The prisoner"),
    ("threat_klymene", "characters", ("Lucian",), "His league uses the altar"),
    (
        "threat_klymene",
        "places",
        ("great_altar", "pergamos", "The Great Altar", "Pergamos"),
        "The lock",
    ),
    ("threat_hades", "covenants", ("Hedyosmos",), "The temple Askalaphos wants back"),
    ("threat_hades", "characters", ("Vrakos",), "The cook turned priest"),
    ("threat_tremere_appeal", "covenants", ("Gigas",), "Tremere's covenant in Thebes"),
    ("threat_tremere_appeal", "characters", ("Boustaphan",), "Tremere's tribune"),
    ("threat_tremere_appeal", "characters", ("Allectores",), "Gigas's envoy"),
    (
        "threat_tremere_appeal",
        "places",
        ("thermakopolis", "Thermakopolis"),
        "The Advisors' fall",
    ),
    ("threat_verditius", "covenants", ("Ingasia",), "Would host the Contest"),
    ("threat_verditius", "characters", ("Stouritus",), "The primus"),
    ("threat_verditius", "characters", ("Gemma",), "Over-quota sales"),
    ("threat_verditius", "characters", ("Bobila",), "Over-quota sales"),
    ("threat_talos", "creatures", ("Talos",), "The bronze guardian"),
    ("threat_naxos", "covenants", ("Polyaigos",), "The duke envies its wealth"),
    ("threat_naxos", "characters", ("Caterina",), "Arranging terms with him"),
    ("threat_naxos", "characters", ("Satabus",), "The duke's lost brother"),
    (
        "threat_hagka",
        "covenants",
        ("Moero's Garden",),
        "The League of Constantine's seat",
    ),
    ("threat_hagka", "covenants", ("Michael's Tabula",), "Sworn to the city"),
    ("threat_serapis", "places", ("sinope", "Sinope"), "The sect's city"),
    (
        "threat_zeno",
        "places",
        ("holy_apostles", "The Church of the Holy Apostles"),
        "His crypt",
    ),
    (
        "threat_thermakopolis",
        "covenants",
        ("Michael's Tabula",),
        "Already sworn to the city",
    ),
    (
        "threat_thermakopolis",
        "covenants",
        ("Moero's Garden",),
        "Its young magi want it",
    ),
    ("threat_thermakopolis", "characters", ("Petros",), "Bears the old shame"),
    (
        "threat_thermakopolis",
        "places",
        ("thermakopolis", "Thermakopolis"),
        "The old site",
    ),
    ("threat_wilusa", "places", ("wilusa", "Wilusa"), "The lost covenant"),
)

#: Each story's place: covenants whose place to use, then place keys and
#: names to try, then the region's key as the fallback.
PLACES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "threat_enemy_within": (("Alexandria",), ("smyrna", "Smyrna"), "anatolia"),
    "frame_1221": ((), ("delos", "Delos"), "islands"),
    "threat_epiros": ((), ("thessaloniki", "Thessaloniki"), "greece"),
    "threat_nicaea": (
        (),
        ("holkos", "hellespont", "troad", "bithynia", "Holkos", "The Hellespont"),
        "anatolia",
    ),
    "threat_akgah": ((), ("akgah_lair", "Akgah's Lair"), "constantinople"),
    "threat_lucian": (("Aegaea",), ("aegaea",), "islands"),
    "threat_kampe": (("Hedyosmos",), ("hedyosmos", "mount_minthe"), "greece"),
    "threat_klymene": (
        (),
        ("great_altar", "pergamos", "The Great Altar", "Pergamos"),
        "anatolia",
    ),
    "threat_hades": (("Hedyosmos",), ("hedyosmos", "mount_minthe"), "greece"),
    "threat_tremere_appeal": (("Gigas",), ("gigas",), "greece"),
    "threat_verditius": (("Ingasia",), ("lemnos", "Lemnos"), "islands"),
    "threat_talos": (
        (),
        ("knossos", "candia", "The Labyrinth of Knossos", "Candia"),
        "islands",
    ),
    "threat_naxos": ((), ("naxos", "Naxos"), "islands"),
    "threat_hagka": ((), (), "constantinople"),
    "threat_serapis": ((), ("sinope", "Sinope"), "anatolia"),
    "threat_zeno": (
        (),
        ("holy_apostles", "The Church of the Holy Apostles", "Holy Apostles"),
        "constantinople",
    ),
    "threat_thermakopolis": ((), ("thermakopolis", "Thermakopolis"), "constantinople"),
    "threat_wilusa": ((), ("wilusa", "ilion", "Wilusa", "Ilion"), "anatolia"),
}

#: Factions other parts may make that stand behind a story.
BEHIND: dict[str, tuple[str, ...]] = {
    "threat_enemy_within": ("League of the Vigilant",),
    "threat_lucian": ("Children of Olympos", "Children of Olympus"),
    "threat_kampe": ("Kampe's Lovers",),
    "threat_serapis": ("Christians of Serapis",),
    "threat_hagka": ("League of Constantine",),
}


def _place(theban: Theban, places: list[Any], *keys: str) -> Any | None:
    """A place by one of the region parts' keys, or by one of its names."""
    for key in keys:
        if key in theban.places:
            return theban.places[key]
    return _find(places, *keys)


def _character(theban: Theban, *names: str) -> Any | None:
    for name in names:
        found = theban.magi.get(_slug(name))
        if found is not None:
            return found
    return _find(theban.b.saga.characters, *names)


def finish(theban: Theban) -> None:
    saga, world = theban.b.saga, theban.world
    places = [n for n in saga.neighbours if n.kind == "place"]
    factions = [n for n in saga.neighbours if n.kind == "faction"]
    for key, kind, names, note in LINKS:
        if kind == "characters":
            target = _character(theban, *names)
        elif kind == "covenants":
            target = _find(saga.covenants, *names)
        elif kind == "creatures":
            target = _find(saga.creatures, *names)
        else:
            target = _place(theban, places, *names)
        if target is not None:
            Builder.link(world[key], kind, target, note)
    for key, (covenants, names, region) in PLACES.items():
        place_id = None
        for name in covenants:
            covenant = _find(saga.covenants, name)
            if covenant is not None and covenant.place_id:
                place_id = covenant.place_id
                break
        if place_id is None:
            place = _place(theban, places, *names) or theban.places.get(region)
            place_id = place.id if place is not None else None
        if place_id is not None:
            world[key].place_id = place_id
    for key, names in BEHIND.items():
        faction = _find(factions, *names)
        if faction is not None:
            world[key].answers_to = faction.id
    tribunal = theban.tribunal or next(iter(saga.tribunals), None)
    if tribunal is not None:
        _add_to(tribunal, HOOKS, HIDDEN_HOOKS)


HOOKS = paragraphs(
    "Stories. Four are under way in 1220: the League of the Vigilant's "
    "first recruiting (An Enemy Within), the meeting on Delos in 1221, "
    "Epiros's war on Thessaloniki and Nicaea's on the Latins. Others wait "
    "for the storyguide to begin them, from Klymene's prison at Pergamos "
    "and the lost covenant of Wilusa to the Tremere appeal of 1228 and "
    "the Verditius Contest of 1234.",
    "Smaller seeds. Young magi lending their Parma Magica to the Gifted "
    "children before the Apprentice Presentation, who whisper that "
    "unchosen children vanish; a Gifted boy who bonded with the arche "
    "lodging him, then fled his new Tytalus master with stolen enchanted "
    "items to rule a band of robbers. A god seen near Olympos who looks "
    "like a magus lost to Final Twilight; a girl at Delphi who says Pythia "
    "is gone and repeats a prophecy of her rescue; the Prince of Achaea "
    "fallen ill, his wife begging Epidauros for a cure that either way "
    "looks like meddling. The despot of Rodos, who has seized every book "
    "on his island and listens to a sinister hedge wizard; the scattered "
    "Julian Library, hunted by every Seeker; Formosos's crusade to prove "
    "Passara a court wizard; and the mysterious French knight who killed "
    "the Sultan of Rum in 1211 and saved the Nicene emperor, perhaps a "
    "magus in disguise, whom a senior magus wants unmasked before the "
    "meeting. In Constantinople the Latin clergy may suppress the "
    "procession of icons on the Feast of Orthodoxy, and riot will follow. "
    "Nearer home: a merchant ruined by swarms of flies, a Persian wizard "
    "hunting his ancestor's amulet, a triton lord at war with a "
    "covenant's fishermen, a family house-snake that follows its magus "
    "to a new covenant, a tree spirit freed when its fruit is all taken, "
    "and a guardian owl-spirit a covenant might court as its patron.",
)

HIDDEN_HOOKS = paragraphs(
    "Behind the seeds: one of the children at the interviews is a faerie "
    "changeling who means to lead the others away to safety. The flies "
    "are a nasu bound in a relic of the Persian Wars, and the rival who "
    "found it commands them. The despot's adviser is close to the "
    "Infernal, writes the island's only books, among them a corrupt "
    "Bible, and hoards its vis while his demon watches. The senior magus "
    "asking after the mysterious knight may be the knight himself, "
    "testing how easily he could be found out.",
)
