"""The saga's stories, in paraphrase: each a threat whose stages lay out
how it unfolds if the troupe ignores, stops or turns it.

The book's frame is change coming to Hibernia: the English magi press
to remake the Tribunal while the Ordo Hiberniae holds to its customs,
and the characters may push the change, soften it or resist it.

Under way in 1220: Guillaume's push into Connacht, in the four stages
from hired raiders to war with the Coill Trí; the test of the Treaty of
Cnoc Maol Réidh, dated to the meeting at Tara in 1221; and the English
reform motions.

Dormant until the storyguide begins them: Maoilfhinnéin's plot against
Gráinne, Ballack's debts, Donn's army, the Gaileoin infernalists, the
giant under Qui Sonant, Áillen burning Tara, the Conspiracy of Mellifont
and the Pact of Oireadh's Parma.

`finish` puts each story inside the place where it plays out, ties it
to the covenants, magi, creatures and places the other parts made
(found by key or by name, and skipped when missing), puts the faction
behind it as the one it answers to, links the four private feuds
between their magi with a line in each one's notes, adds the book's
story seeds to the places and covenants they use, and closes the
Tribunal's summary with a word on the stories."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING, Any

from ...threats import DORMANT
from ..builder import Builder, paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Hibernia

S = Builder.stage
DATED = "Fixed dates"


def build(hibernia: Hibernia) -> None:
    _connacht(hibernia)
    _treaty_test(hibernia)
    _reform(hibernia)
    _grainne(hibernia)
    _ballack(hibernia)
    _donn(hibernia)
    _gaileoin(hibernia)
    _giant(hibernia)
    _aillen(hibernia)
    _mellifont(hibernia)
    _oireadh(hibernia)


def _dormant(threat: Neighbour) -> Neighbour:
    """Mark a threat as not yet begun: More, Begin This Story starts it."""
    threat.details[DORMANT] = True
    return threat


# -- under way in 1220 --


def _connacht(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_connacht"] = b.threat(
        "Guillaume and Connacht",
        summary=paragraphs(
            "Praesis fell to Ballack's siege, and its new masters now "
            "look west. For two seasons Guillaume Flambeau of Normandy "
            "has been telling the covenant's guests what his spies have "
            "found across the border: sites, auras and vis that the "
            "Treaty of Cnoc Maol Réidh keeps from the Order. Praesis "
            "plays host to a shifting company of foreign magi fresh to "
            "Hibernia, and their eyes are turning to Connacht.",
            "Guillaume has not yet crossed the Sionainne himself. He "
            "sends his turb of Bréifne mercenaries, who serve him for "
            "pay, food, wine and plunder, to find vis sources and strip "
            "them. The villages round Lough Ree have learned to fear "
            "Praesis and its men, the Coill Trí warns hedge wizards of "
            "the new danger, and Cacht of Criamon, who fought for "
            "Ballack only for the joy of overturning things, listens "
            "closely, sensing a fresh war.",
            "The Treaty forbids any covenant in Connacht and any magus "
            "more than three nights under its sky or roof, and no one "
            "person, druid or magus, can set a clause aside. One old "
            "clause gives the members of Praesis leave to enter "
            "Connacht in pursuit of Hermetic justice, at Manannán mac "
            "Lir's express request, or to seek bees for their hives, "
            "and its new masters may try to stretch it.",
        ),
        secrets=paragraphs(
            "Báetáin, who handed the Gáe Bulg to Ballack, now shares "
            "his tower with Guillaume, whose fire killed the people he "
            "knew; his regret is a lever for anyone who would turn "
            "Praesis from within.",
            "Maoilfhinnéin of Vigil is quietly steering the shards of "
            "Gráinne's broken first talisman into Guillaume's hands "
            "(see Maoilfhinnéin's Plot), which may draw Guillaume's "
            "attention east to Vigil before he finishes with Connacht.",
        ),
        antagonist="Guillaume Flambeau of Praesis and his Bréifne mercenaries",
        position=1,
        stages=[
            S(
                "Raids by hired men",
                at=1,
                clues=(
                    "Bréifne mercenaries cross the Sionainne by night, "
                    "guided by the spies' reports, and come back with vis. "
                    "Druids find their sources stripped; Connachta nobles, "
                    "who shelter their druids, blame the English; the Coill "
                    "Trí's ambassador starts gathering complaints for the "
                    "Sacred Council."
                ),
                ignored=(
                    "Connacht's sources are plundered one by one, and the "
                    "Coill Trí brings its anger to Tara in 1221."
                ),
                stopped=(
                    "The raiders are caught, and their paymaster named "
                    "before the Sacred Council."
                ),
                turned=(
                    "The troupe wins the trust of the druids who were "
                    "robbed, or quietly takes over the spies' knowledge."
                ),
            ),
            S(
                "A magus crosses the border",
                at=2,
                clues=(
                    "Guillaume, or one of the newcomers he has fired with "
                    "his reports, goes into Connacht in person, counting "
                    "the nights, or claiming Praesis's old leave to seek "
                    "bees or justice there."
                ),
                ignored=("Others follow, and a magus in Connacht becomes ordinary."),
                stopped=(
                    "The magus is brought back within three nights and "
                    "warned off by the Presiding Quaesitor."
                ),
                turned=(
                    "The troupe tests the Praesis clause in a way that "
                    "settles what it allows before the Tribunal."
                ),
            ),
            S(
                "The Treaty broken",
                at=3,
                clues=(
                    "A magus outstays his three nights, marks a Connacht "
                    "site as his own, or slays a hedge wizard without the "
                    "warning of Wizard War owed to the Order's allies. The "
                    "Coill Trí demands the justice the Treaty promises."
                ),
                ignored=(
                    "The Tribunal hesitates, and the druids conclude that "
                    "the Order will not keep its word."
                ),
                stopped=(
                    "The offender is tried, and Connacht is given redress "
                    "under the Treaty's terms."
                ),
                turned=(
                    "The breach forces the Tribunal to restate the Treaty, "
                    "perhaps with a new clause every ceannaire accepts."
                ),
            ),
            S(
                "War with the Coill Trí",
                at=4,
                clues=(
                    "The druids withhold the seven children and strike "
                    "back, the Connachta kings who guard their borders "
                    "hard ride with them, and Fir Bolg counsellors urge "
                    "old grudges. The Order must decide whether to march "
                    "on its own or let the war spread."
                ),
                ignored=(
                    "Connacht falls open to the English magi, and the Ordo "
                    "Hiberniae's fear of being driven back like the peoples "
                    "before it begins to come true."
                ),
                stopped="A peace is made at Qui Sonant, the neutral ground.",
                turned=(
                    "The troupe brokers the peace and becomes the go-between "
                    "the Treaty has always lacked."
                ),
            ),
        ],
    )


def _treaty_test(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_treaty"] = b.threat(
        "The Test of the Treaty",
        summary=paragraphs(
            "The Treaty of Cnoc Maol Réidh has bound every Hibernian "
            "Tribunal since 898, and every meeting speaks of it as "
            "binding, yet it has never been formally put to the vote: "
            "any attempt to question it is shouted down before "
            "debate can begin. That day is near. The English magi say "
            "no hedge wizard elsewhere in Mythic Europe has such "
            "rights, and that the Treaty mocks a Code written for "
            "Hermetic magi; some Irish magi have long coveted Connacht "
            "too; and younger magi in their macgnímartha, who are "
            "outside the Code and venture into Connacht for sport, "
            "have heard the English message.",
            "The Coill Trí is no happier. Its members resent the "
            "tithe of seven Gifted children at every meeting, a tithe "
            "that is sometimes rejected because a draoi misjudged the "
            "Gift, and some magi bully druids into service, knowing "
            "the druids dare not complain. Some churchmen in Connacht "
            "suspect the federation of heresy, even of worse.",
            "Open questions sharpen the debate. Bréifne lies on both "
            "sides of the Sionainne, and the Treaty does not say "
            "whether Connacht ends at the river or wherever the "
            "Connachta kings rule; the Coill Trí claims all of it. The "
            "Black Pig's Dyke, if restored, would ring Ulster and cut "
            "into Connacht, which is why the druids keep it broken. A "
            "magical marker along the Slieve Aughty, where magi seeking "
            "familiars stray across the border, would earn the thanks "
            "of both sides. A clause can be added only when the "
            "Tribunal wants it and every ceannaire agrees.",
        ),
        secrets="",
        antagonist="The Treaty's enemies, English and Irish alike",
        moves=DATED,
        stages=[
            S(
                "Voices against the Treaty",
                year=1220,
                clues=(
                    "The English Council and a few covetous Irish magi "
                    "count votes; Guillaume's reports on Connacht pass from "
                    "hand to hand; the Coill Trí's ambassador, distrusted "
                    "by both sides, collects witnesses and grievances."
                ),
                ignored=(
                    "The Treaty's enemies come to Tara with their case "
                    "prepared and its friends with none."
                ),
                stopped=(
                    "The would-be challengers are persuaded that the moment is wrong."
                ),
                turned=(
                    "The troupe becomes the one both sides consult before the meeting."
                ),
            ),
            S(
                "The Sacred Council",
                year=1221,
                clues=(
                    "Before the meeting proper, the Praeco and the "
                    "Presiding Quaesitor meet the embassies and confirm the "
                    "ambassadors. The Coill Trí hands over its seven "
                    "children, and brings its complaints: raids from "
                    "Praesis, magi who extort services, Faolán living in "
                    "Connacht."
                ),
                ignored=(
                    "Grievances go unanswered, and the druids come to the vote angry."
                ),
                stopped="The disputes are judged fairly and the tithe accepted.",
                turned=(
                    "A just settlement wins the Coill Trí's ambassador, and "
                    "perhaps a child of the tithe, for the troupe's side."
                ),
            ),
            S(
                "The challenge",
                year=1221,
                clues=(
                    "Someone at last asks the Tribunal to rule whether the "
                    "Treaty still binds. The ambassadors vote as equals, "
                    "which the English contest, and the Presiding Quaesitor "
                    "may veto only what plainly breaks the Oath or Code."
                ),
                ignored=(
                    "Whichever side loses takes matters into its own "
                    "hands: magi cross into Connacht, or the druids stop "
                    "paying the tithe."
                ),
                stopped=(
                    "The Treaty is affirmed, and the question is closed "
                    "for a generation."
                ),
                turned=(
                    "The Treaty is amended with a clause every ceannaire "
                    "accepts, settling Bréifne's border or marking the "
                    "Slieve Aughty."
                ),
            ),
        ],
    )


def _reform(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_reform"] = b.threat(
        "The English Reform Motions",
        summary=paragraphs(
            "Since England invaded Ireland, magi from across the Order, "
            "called the English after the first visitors from "
            "Stonehenge, have come to claim land and to bring the "
            "Tribunal into line with continental practice. House "
            "Tremere backed the first of them. They harvest vis when "
            "it is ready, ignore or intimidate the lesser traditions "
            "as suits them, and see Connacht as land waiting to be "
            "taken.",
            "At every meeting they press the same motions: that law "
            "made case by case in treaties, where a ruling in Munster "
            "in 1134 says nothing about the same dispute in 1220, is "
            "unworkable; that the ambassadors' votes are illegal and "
            "demeaning; and that the Peripheral Code should be "
            "rewritten on Stonehenge's model. Helles of Ashenrise leads "
            "the debate, a Tytalus trained in both academic and "
            "Tytalus disputation, and answers charges of high crimes "
            "against himself and his sodales at every meeting. The "
            "English Council meets at the start of each Tribunal to "
            "agree its line, but its members disagree, and it needs a "
            "leader who can see past the legacy of Praesis and the "
            "menace of Lámbaird.",
            "Against them stand Circulus Ruber, which will not change "
            "its time-honoured ways, and Cliffheart, which fights every "
            "English foundation by law; Milvia, the Praeco, keeps out "
            "of the quarrel. The Grand Tribunal of 1195 debated "
            "Hibernia's reform at length and left its Code alone, "
            "outraging Stonehenge when the parens of the apprentices "
            "who attacked Damisona were found guilty only of a Low "
            "Crime.",
        ),
        secrets=paragraphs(
            "Lugardis of Elk's Run, sent by Durenmar to judge the "
            "Order in Hibernia, has concluded that the Tribunal keeps "
            "the Code, if with an odd Peripheral Code, and has written "
            "home in its praise; an appeal abroad may find less "
            "sympathy than the reformers expect.",
            "Dorján and Konstanczia of Ashenrise are directed by the "
            "Transylvanian magi who hold their sigils to help Ashenrise "
            "bring the Tribunal up to date.",
        ),
        antagonist="The English Council and the reformers of Ashenrise",
        position=1,
        stages=[
            S(
                "The English Council",
                at=1,
                clues=(
                    "Before each meeting the foreign magi gather to agree a "
                    "common line, and quarrel. Elk's Run's beleaguered magi "
                    "lean on English nobles; Igneous Drake's killings and "
                    "Lámbaird's suspected raids give each side its "
                    "grievance."
                ),
                ignored=(
                    "The council speaks with many voices, and its motions "
                    "fail as before."
                ),
                stopped="The council breaks apart over Praesis.",
                turned=(
                    "A player magus takes the council's lead and decides "
                    "what it asks for."
                ),
            ),
            S(
                "Charges against Helles",
                at=2,
                clues=(
                    "The Ordo Hiberniae charges Helles and his sodales with "
                    "high crimes again; he defends himself with a summer's "
                    "worth of glosses on Hermetic law."
                ),
                ignored=(
                    "Helles is acquitted once more, and every acquittal "
                    "wins him sympathy among the newcomers."
                ),
                stopped="A charge sticks, and Ashenrise is silenced for a meeting.",
                turned=(
                    "The troupe wins a bargain: the charges dropped for a "
                    "motion withdrawn."
                ),
            ),
            S(
                "Against the ambassadors",
                at=3,
                clues=(
                    "The English move to strip the ambassadors of their "
                    "votes, and to make law by general rulings rather than "
                    "by treaty. Each new arrival from the continent adds a "
                    "vote."
                ),
                ignored=(
                    "The ambassadors keep their votes for now, but the "
                    "majority against them grows with every meeting."
                ),
                stopped="The ambassadors' votes are affirmed by a clear vote.",
                turned=(
                    "A compromise binds the ambassadors to the Code's "
                    "rulings in return for their seats."
                ),
            ),
            S(
                "A Code on Stonehenge's model",
                at=4,
                clues=(
                    "The reformers carry their case beyond Hibernia, to "
                    "Magvillus, to Durenmar, and to the next Grand Tribunal, "
                    "due in 1228 if it keeps its usual thirty-three years."
                ),
                ignored=(
                    "Hibernia's Code is rewritten from outside, and the "
                    "Ordo Hiberniae fears it will be pushed back to "
                    "Connacht like the druids before it."
                ),
                stopped="The Order upholds Hibernia's right to its own Code.",
                turned=(
                    "The troupe shapes a reformed Code both Irish and "
                    "English magi can live with."
                ),
            ),
        ],
    )


# -- the dormant stories --


def _grainne(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_grainne"] = _dormant(
        b.threat(
            "Maoilfhinnéin's Plot",
            summary=paragraphs(
                "Vigil, the Merinita covenant on Cionn Mhálanna, once "
                "stood watch over Ireland and now lives fat on its old "
                "glories. Gráinne inghean Uaitéar, its boisterous "
                "quartermaster, wastes vis without noticing, holds "
                "authority over vaults whose worth she does not guess, "
                "and has a long rivalry with Guillaume of Praesis, who "
                "would love to see her humbled. As a young maga she "
                "tired of her first talisman, a sword, broke it in a "
                "rite and threw the pieces from the cliffs.",
                "Maoilfhinnéin mac Lir, Vigil's Ambassador to the Sea, "
                "spends his days in faerie and magical courts and is "
                "married to a faerie princess of Inishtrahull, an island "
                "six miles out from the head.",
            ),
            secrets=paragraphs(
                "Maoilfhinnéin believes Ireland's old stories are bound "
                "to repeat, and that the Ordo Hiberniae will be driven "
                "back as the native wizards were; he sees the first "
                "signs already. Should Vigil be threatened, he has "
                "prepared to carry the tusks to Inishtrahull and found "
                "the covenant anew there.",
                "He has three schemes in hand. He supports Lámbaird's "
                "positions at Tribunal, to mend the harm Éinri's feud "
                "has done. He feeds Gráinne's overconfidence, seeing "
                "that a sacrifice may soon be needed. And his allies in "
                "the sea brought him the shards of her broken sword: he "
                "has fixed them as an Arcane Connection to her and is "
                "working them into the hands of Guillaume.",
            ),
            antagonist="Maoilfhinnéin mac Lir, Ambassador to the Sea",
            stages=[
                S(
                    "Old friends and sea-worn shards",
                    at=1,
                    clues=(
                        "Vigil's ambassador is unusually warm to Lámbaird; "
                        "Gráinne is goaded into ever bolder boasts; a "
                        "sea-worn blade fragment changes hands among "
                        "fishermen, then traders, heading south."
                    ),
                    ignored="The shards reach Praesis.",
                    stopped="The shards are found and returned to Gráinne.",
                    turned="The troupe learns who fixed the connection, and why.",
                ),
                S(
                    "Guillaume's weapon",
                    at=2,
                    clues=(
                        "Guillaume learns what the shards are. He declares "
                        "Wizard War on Gráinne in public, a month ahead as "
                        "the Code requires, or simply strikes from afar."
                    ),
                    ignored="His spells find her wherever she is.",
                    stopped=(
                        "Gráinne is warned and warded in time, and the "
                        "connection destroyed."
                    ),
                    turned="Guillaume is persuaded the shards are a trap.",
                ),
                S(
                    "The sacrifice",
                    at=3,
                    clues=(
                        "Gráinne is humbled or slain. The Two Dozen Men of "
                        "Mhálanna, loyal to her above all, cry for revenge, "
                        "and Vigil's halls fill with talk of war with "
                        "Praesis."
                    ),
                    ignored="Vigil and Praesis go to war.",
                    stopped="Gráinne survives, wiser and angry.",
                    turned=(
                        "Gráinne learns who betrayed her, and Vigil turns on "
                        "its ambassador."
                    ),
                ),
                S(
                    "Retreat to Inishtrahull",
                    at=4,
                    clues=(
                        "Declaring the covenant in danger, Maoilfhinnéin "
                        "carries the black pig's tusks out to sea and "
                        "refounds Vigil among his wife's people."
                    ),
                    ignored=(
                        "Vigil abandons the mainland, leaving Banbha's Crown "
                        "and the drowned vaults to whoever finds them."
                    ),
                    stopped="The tusks stay above the gate on Cionn Mhálanna.",
                    turned=(
                        "The troupe claims the abandoned vaults, or "
                        "Vigil's thanks for keeping it whole."
                    ),
                ),
            ],
        )
    )


def _ballack(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_ballack"] = _dormant(
        b.threat(
            "Ballack's Debts",
            summary=paragraphs(
                "Ballack of Tytalus came from the Rhine to avenge his "
                "filius Holzner, whom Praesis executed for stealing its "
                "cathach, and after a year's Wizard War he rules the "
                "covenant. He relishes turning Hibernia's traditions on "
                "the Irish, scorns their magi and courts the English "
                "covenants and new adventurers, and Holzner's head "
                "still hangs from the palisade where Meadhbh put it.",
                "The war cost him dearly. He owes vis and favours to "
                "many magi, and with his own resources spent he has "
                "borrowed more vis and casting tablets from distant "
                "benefactors. Until he pays them, he knows his prize is "
                "only on loan, yet he cannot be seen to give it up. "
                "Praesis must start paying for itself, and soon.",
            ),
            secrets="His benefactors are a powerful, secretive cult or society "
            "to which Ballack does not belong, though he took its aid; "
            "lately he has been forgetting what he owes it.",
            antagonist="Ballack's hidden creditors",
            stages=[
                S(
                    "A prize on loan",
                    at=1,
                    clues=(
                        "Ballack hunts for income: the vis Guillaume's men "
                        "bring out of Connacht, services sold to English "
                        "covenants, the sources around Lough Ree his siege "
                        "stripped bare."
                    ),
                    ignored="Praesis's greed falls on its neighbours.",
                    stopped="Praesis finds an honest income.",
                    turned="The troupe becomes Ballack's partner, on its own terms.",
                ),
                S(
                    "Remember who you work for",
                    at=2,
                    clues=(
                        "A player magus who has joined a cult or society is "
                        "sent to remind Ballack of his debt. He is no "
                        "member, and he is older and more dangerous than "
                        "the messenger."
                    ),
                    ignored="The creditors lose patience.",
                    stopped="Ballack pays what he can, and the reminder is heeded.",
                    turned=("The messenger gains a hold over the Lord of Praesis."),
                ),
                S(
                    "The debt called in",
                    at=3,
                    clues=(
                        "The benefactors collect in their own coin: service "
                        "in a quarrel that is not his, a share of Praesis's "
                        "sources, or his votes at Tara."
                    ),
                    ignored="Praesis becomes the creditors' tool.",
                    stopped="Ballack breaks free of them, at a price.",
                    turned=(
                        "The troupe learns who the creditors are, and what "
                        "they want in Hibernia."
                    ),
                ),
                S(
                    "The covenant changes hands",
                    at=4,
                    clues=(
                        "Weakened, Ballack's hold slips. Meadhbh's "
                        "supporters, whom Praesis watches for every week, "
                        "see their chance; so do his creditors."
                    ),
                    ignored="Praesis falls again, to Meadhbh or to the creditors.",
                    stopped="Ballack holds Praesis.",
                    turned="The troupe decides who keeps the Gáe Bulg.",
                ),
            ],
        )
    )


def _donn(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_donn"] = _dormant(
        b.threat(
            "Donn's Army",
            summary=paragraphs(
                "Donn, the Dark One, the death god of the Tuatha Dé "
                "(see the Bestiary), holds court where the dead gather, "
                "on Teach Duínn, a bare rock in the sea beyond "
                "Munster. He behaves like any king: he has sons, "
                "keeps cattle and raids his neighbours, and he is "
                "gathering a host, a warrior here and a warrior there. "
                "His favoured way is to slay a sleeper and let the spirit fly to his "
                "island, or to leave a perfect false corpse behind and "
                "carry the living man away. In war his three red-haired "
                "sons ride through the land, crying that the slain will "
                "rise at Teach Duínn to join him.",
                "In the Schism War Donn fought beside the Diedne of "
                "Salmon's Eye, and their forces destroyed Warbler's Way "
                "before the magi razed Salmon's Eye and drove him home. "
                "Cliffheart, founded by Warbler's Way's survivors, never "
                "learned why the Tuatha Dé sided with Diedne, and keeps "
                "watch. His great warded regio may hide a host, and "
                "magi wonder whether he means to invade again; "
                "Munster's endless wars may give him his chance, and "
                "anyone who makes war on the Order will find him a "
                "willing ally. The smith god Goibhniu hates him.",
                "In Ulster a faerie called Donn, the dark one of the "
                "endless war with bright Find, has caused children of "
                "faerie blood to be born, meant as the core of a new "
                "army. Find has not yet answered.",
            ),
            secrets="Whether Ulster's Donn and the lord of Teach Duínn are one "
            "being is left to the storyguide; if they are, the "
            "faerie-blooded children are the first sign of the host.",
            antagonist="Donn of Teach Duínn",
            realm="Faerie",
            stages=[
                S(
                    "Taken in sleep",
                    at=1,
                    clues=(
                        "Men die in their beds without a mark, or are buried "
                        "whole while their kin swear they saw them alive; a "
                        "grog's corpse is found that is not his."
                    ),
                    ignored="Donn's ranks swell quietly.",
                    stopped="The thefts are traced to Teach Duínn and warded against.",
                    turned="A captive is brought back alive, with news of the island.",
                ),
                S(
                    "The children of Donn",
                    at=2,
                    clues=(
                        "Children of faerie blood are born in Cuailnge and "
                        "beyond, and Find stirs against his old enemy."
                    ),
                    ignored="The children grow toward their father's war.",
                    stopped="The children are fostered beyond Donn's reach.",
                    turned=("The troupe claims a Gifted child, or Find's alliance."),
                ),
                S(
                    "Three red riders",
                    at=3,
                    clues=(
                        "Donn's sons ride through Munster in the wake of "
                        "Desmond's and Thomond's wars, spreading terror and "
                        "promising that the fallen will rise."
                    ),
                    ignored="The dead of every battle go to Donn.",
                    stopped="The sons are driven back to the sea.",
                    turned="Goibhniu's feud with Donn is turned against him.",
                ),
                S(
                    "The host of Teach Duínn",
                    at=4,
                    clues=(
                        "Donn's army marches out of its regio, perhaps "
                        "beside some enemy of the Order, as it once marched "
                        "with Diedne."
                    ),
                    ignored=(
                        "Munster's covenants face a second Schism War, "
                        "Cliffheart and Circulus Ruber first."
                    ),
                    stopped="The Tribunal unites and throws Donn back again.",
                    turned=(
                        "The troupe treats with Donn, and learns at last why "
                        "the Tuatha Dé fought for Diedne."
                    ),
                ),
            ],
        )
    )


def _gaileoin(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_gaileoin"] = _dormant(
        b.threat(
            "The Gaileoin Infernalists",
            summary=paragraphs(
                "The Gaileoin, the third tribe of the Fir Bolg, live on "
                "Árainn Thiar, smallest of the Aran Isles. They are "
                "Christian in name and hardly observant, their island "
                "has a single church, and they are lazier and quicker "
                "to small sins than their neighbours. The Fir Bolg are "
                "allies of the Order, with an ambassador who votes at "
                "Tara, and the isles lie in Connacht, where no magus "
                "may stay beyond three nights.",
            ),
            secrets=paragraphs(
                "Unknown to the other tribes, a cadre of infernalists "
                "rules the Gaileoin through their king. Their meddling "
                "has left the royal line feeble-minded, puppets who "
                "speak as they are told. The tribe as a whole has been "
                "slow to corrupt.",
                "Dealing with demons is the one crime for which the "
                "Code calls a Wizard's March without debate, which sets "
                "the Order's law against the Treaty's limits and the "
                "Fir Bolg alliance the moment the truth comes out.",
            ),
            antagonist="The infernalists behind the Gaileoin king",
            realm="Infernal",
            stages=[
                S(
                    "Idle islanders",
                    at=1,
                    clues=(
                        "Visitors to Árainn Thiar find the church empty, the "
                        "fields neglected and the people cheerfully sinful; "
                        "Fir Bolg monks of Árainn Mhór worry for their "
                        "cousins."
                    ),
                    ignored="The rot deepens.",
                    stopped="A preacher or saint stirs the Gaileoin to repent.",
                    turned="The troupe finds a Gaileoin who will talk.",
                ),
                S(
                    "The puppet king",
                    at=2,
                    clues=(
                        "An envoy to the Gaileoin court finds the king "
                        "vacant and his councillors answering for him."
                    ),
                    ignored="The cadre's hold is never questioned.",
                    stopped="The councillors are exposed before King Rudraige.",
                    turned="The troupe learns the cadre's names and masters.",
                ),
                S(
                    "Beyond the island",
                    at=3,
                    clues=(
                        "The cadre's reach grows: into the Fir Bolg's "
                        "counsel to the kings of Connacht, toward the "
                        "ambassador's vote, or across the water to the "
                        "mainland."
                    ),
                    ignored="The Order's ally becomes Hell's instrument.",
                    stopped="The cadre is kept to Árainn Thiar.",
                    turned="The Fir Bolg purge the cadre themselves, with help.",
                ),
                S(
                    "A March in Connacht",
                    at=4,
                    clues=(
                        "The truth comes out. The Code demands a March, the "
                        "Treaty limits magi to three nights in Connacht, and "
                        "the Fir Bolg are allies who must be warned like "
                        "magi."
                    ),
                    ignored=(
                        "The Order quarrels over the law while the "
                        "infernalists escape or dig in."
                    ),
                    stopped="The cadre is destroyed, and the Treaty survives.",
                    turned=(
                        "The troupe finds a way through the law that keeps "
                        "both the alliance and the Treaty."
                    ),
                ),
            ],
        )
    )


def _giant(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_giant"] = _dormant(
        b.threat(
            "The Giant under Qui Sonant",
            summary=paragraphs(
                "Legend says a giant sleeps beneath the Cuailnge "
                "ridge where Qui Sonant Pro Quieto stands, held asleep "
                "for as long as song is heard above him, and that if "
                "the songs end or he is disturbed he will rise and "
                "quit the island, and its magic will go with him. Day and "
                "night a choir of a dozen, magi and covenfolk, chants "
                "in the candlelit chantry where no magic is used, and "
                "every apprentice learns the songs by heart. The theory "
                "in fashion makes the giant a Fomóir, or Finn "
                "MacCumhaill himself.",
                "Cantarus, Master of the Songs for fifty years and now "
                "130, knows he has little time and no heir. Finn, his "
                "only filius still at the covenant, takes the office "
                "for granted and trades promises on it, but lacks the "
                "gift for leading; Cantarus would gladly name any magus "
                "willing to commit to Qui Sonant instead. Máel-ruanaid "
                "of Vigil, a master of Merinita story magic, believes "
                "the giant is held by the symbolic act of singing "
                "rather than by the songs, and wants to learn how.",
            ),
            secrets="No one knows what the giant truly is. If Máel-ruanaid is "
            "right, some other symbolic act could take the songs' "
            "place.",
            antagonist="Whatever silences the songs",
            realm="Magic",
            stages=[
                S(
                    "No heir for the songs",
                    at=1,
                    clues=(
                        "Cantarus looks among visitors for a successor; Finn "
                        "boasts of his coming office; Máel-ruanaid asks too "
                        "many questions about the chant."
                    ),
                    ignored="Finn inherits, and the covenant drifts.",
                    stopped="A worthy Master of the Songs is found.",
                    turned="A player magus is offered the office.",
                ),
                S(
                    "Silence falls",
                    at=2,
                    clues=(
                        "A sudden power silences Qui Sonant: no sound, "
                        "natural or magical, can be made or heard there. The "
                        "songs stop, and the ground begins to shake."
                    ),
                    ignored="The tremors grow with every silent day.",
                    stopped="Sound is restored before the giant stirs.",
                    turned="The troupe learns where the silence came from.",
                ),
                S(
                    "The bound daimon",
                    at=3,
                    clues=(
                        "The trail leads into the Magic realm, where a great "
                        "daimon has been trapped and stripped of its power "
                        "over sound on Earth. Its captor must be defeated "
                        "and the power returned."
                    ),
                    ignored="The daimon stays captive and the world stays silent.",
                    stopped="The captor is beaten and the daimon freed.",
                    turned="The freed daimon owes the troupe a favour.",
                ),
                S(
                    "The giant wakes",
                    at=4,
                    clues=(
                        "The hillside heaves, the tombs of the Order's dead "
                        "crack open, and something vast begins to rise."
                    ),
                    ignored=(
                        "The giant leaves Ireland and takes its magic, and "
                        "the Order's cemetery is broken."
                    ),
                    stopped="Song returns and the giant settles back to sleep.",
                    turned=(
                        "The troupe learns what the giant is, and what "
                        "would keep it asleep without the songs."
                    ),
                ),
            ],
        )
    )


def _aillen(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_aillen"] = _dormant(
        b.threat(
            "Áillen Burns Tara",
            summary=paragraphs(
                "The Hill of Tara lies neglected in 1220. Since Saint "
                "Ruadán's curse brought a burning beam down on King "
                "Diarmait in his own hall, no hall can be raised there, "
                "and faeries replay the old tales on the hill, among "
                "them Áillen mac Midgna setting the hall alight and "
                "Fionn mac Cumhaill driving him away.",
                "Áillen is a three-headed magician who lives in the "
                "north of Connacht. He has set Tara on fire again and "
                "again by spewing up burning rocks, and his attacks keep "
                "a regular pattern. Every seven years the hill holds "
                "the Tribunal, when Circulus Ruber raises a temporary "
                "settlement by magic and every covenant puts its "
                "cathach on show.",
            ),
            secrets="",
            antagonist="Áillen mac Midgna",
            realm="Faerie",
            stages=[
                S(
                    "Scorch marks on the hill",
                    at=1,
                    clues=(
                        "Burnt earth and blackened stones on Tara; a herder's "
                        "tale of a three-headed shape in the sky; old "
                        "records that, read together, show when Áillen comes."
                    ),
                    ignored="No one works out the pattern in time.",
                    stopped="The Tribunal is warned and wards are raised.",
                    turned="The troupe can tell the Praeco when he will strike.",
                ),
                S(
                    "Fire on Tara",
                    at=2,
                    clues=(
                        "Áillen comes while the Tribunal's camp stands, "
                        "raining burning stones on tents, hearths and the "
                        "cathaigh on display."
                    ),
                    ignored=(
                        "The camp burns, and a covenant that loses its "
                        "cathach loses its votes."
                    ),
                    stopped="The fire is beaten back before it spreads.",
                    turned="The troupe saves the cathaigh, and wins great credit.",
                ),
                S(
                    "A Fionn for Tara",
                    at=3,
                    clues=(
                        "The story needs its hero: a faerie playing Fionn, or "
                        "a character willing to take the part. Áillen flees "
                        "to Connacht, where magi may not stay three nights."
                    ),
                    ignored="Áillen returns on his next turn of the pattern.",
                    stopped="Áillen is driven off, as in the tale.",
                    turned=(
                        "A player character becomes Tara's Fionn, with the "
                        "reputation that goes with it."
                    ),
                ),
            ],
        )
    )


def _mellifont(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_mellifont"] = _dormant(
        b.threat(
            "The Conspiracy of Mellifont",
            summary=paragraphs(
                "Mellifont, near Drogheda, founded by Saint Malachy in "
                "1140, is the greatest Cistercian house in Ireland: a "
                "hundred monks and three hundred lay brothers, mother "
                "of Bective, Baltinglass and twenty-three more. Since "
                "the invasion its Irish and English monks have been at "
                "odds, and tales of corruption and debauchery reached "
                "Cîteaux. When a visitation came in 1216 to restore the "
                "Rule, the monks shut the gates against it. The general "
                "chapter deposed Abbot Thomas in 1217, but he still "
                "rules, backed by his monks and the daughter houses, "
                "and the Order means to send visitors who will put the "
                "house in order and remove the abbots at fault; the Pope may "
                "step in.",
                "Mellifont's nine granges now cover the Brú na Bóinne, "
                "built on high ground among the ancient sídhe and "
                "ráths, and the forty mounds stand clear of the "
                "undergrowth for the first time in ages. The newest "
                "grange, New Grange, lies beside the mound of Aonghus. "
                "Bective backs its mother house. At Baltinglass the "
                "abbot is for Mellifont while his monks stay loyal to "
                "Cîteaux, and they long to plant a great cross on the "
                "faerie mound above their valley. Jerpoint has joined "
                "the revolt.",
            ),
            secrets="Why the monks rebelled is the storyguide's choice: the "
            "quarrel of Irish and English, a lax life they will not "
            "give up, an Infernal corruption of the Cistercians, or "
            "some ancient magical secret the lay brothers turned up "
            "among the barrows of the Brú na Bóinne.",
            antagonist="Abbot Thomas and the rebel houses",
            stages=[
                S(
                    "The shut gates",
                    at=1,
                    clues=(
                        "Rumours of Mellifont's revolt pass from house to "
                        "house; Irish and English monks quarrel; the "
                        "granges' lay brothers see strange lights among the "
                        "mounds."
                    ),
                    ignored="The revolt hardens.",
                    stopped="Abbot Thomas quietly submits.",
                    turned="The troupe learns the revolt's true cause.",
                ),
                S(
                    "The haunting of New Grange",
                    at=2,
                    clues=(
                        "Trooping faeries ruin the crops at New Grange and "
                        "the lay brothers tell of terrors; then the steward "
                        "and his family vanish one summer evening, and Abbot "
                        "Thomas begs for help."
                    ),
                    ignored="Aonghus wakes, and the granges suffer his wrath.",
                    stopped="The steward's family is brought back from the mound.",
                    turned=(
                        "The troupe wins the abbot's gratitude, and a say in "
                        "where the granges may stand."
                    ),
                ),
                S(
                    "The deputation",
                    at=3,
                    clues=(
                        "Cîteaux's deputation arrives to expel the guilty "
                        "abbots. The daughter houses split, Baltinglass's "
                        "monks against their abbot."
                    ),
                    ignored="Gates are shut again, and the quarrel turns violent.",
                    stopped="Discipline is restored, and the rebels give way.",
                    turned="The troupe shapes which abbots stay and which go.",
                ),
                S(
                    "Rome",
                    at=4,
                    clues=(
                        "The Pope takes up the case, and a long, dark "
                        "struggle begins across the Irish Church."
                    ),
                    ignored=(
                        "The split between the Irish and Anglo-Irish churches "
                        "deepens into open enmity."
                    ),
                    stopped="Rome settles the matter.",
                    turned="A legate in the troupe's debt decides it.",
                ),
            ],
        )
    )


def _oireadh(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["threat_oireadh"] = _dormant(
        b.threat(
            "The Pact of Oireadh's Parma",
            summary=paragraphs(
                "Eight druids of mixed traditions, sworn to the Pact of "
                "Oireadh, meet every season in the village of Oireadh, "
                "no more than two days from any of them; living apart "
                "softens the strife their Gifts bring. They were once "
                "allies of Praesis, which was founded as a meeting "
                "place of magi and druids, but left Meadhbh when her "
                "demands grew too great, and began to ask what gave the "
                "Order its power and what kept it safe while lesser "
                "wizards fell. They have no love for the English.",
                "Ádhamh Brathair, a Gifted learned magician whose "
                "magic goes back to Bologna, conceived the Pact and "
                "leads its research: a theory of magic that embraces "
                "every Irish tradition and gives each the defences of "
                "all. He has made amulets that lend the folk witches' "
                "Second Sight, Dowsing and Cursing for a season, to "
                "learn how their magic differs from his. He is in minor "
                "orders, serves a wealthy noble of Cong, and lately lost "
                "a Gifted child of his to the Coill Trí's "
                "tithe. Among the others are Umor Ard Mac Adar, a "
                "four-armed Fir Domhnann healer in the hills above "
                "Lough Conn; Mór Greannach, a folk witch of Carrowmore "
                "with the widest acquaintance among hedge wizards; and "
                "Tuathal an Iarrainn, a goetic smith of Rosbeg.",
            ),
            secrets=paragraphs(
                "The Pact's true aim, hidden from the Order and the "
                "Coill Trí alike, is a Parma Magica of its own. Ádhamh "
                "needs 120 breakthrough points and has 15, and doubts "
                "he will live to finish; he keeps his notes for those "
                "who come after.",
                "Tuathal's arts are Infernal in origin, which Ádhamh has "
                "yet to discover.",
            ),
            antagonist="Ádhamh Brathair and the Pact of Oireadh",
            realm="Magic",
            stages=[
                S(
                    "Strange amulets",
                    at=1,
                    clues=(
                        "Druids appear with powers not of their tradition; "
                        "the Pact's messengers are busy on the roads; the "
                        "villagers of Oireadh grow wary of strangers and "
                        "send word ahead."
                    ),
                    ignored="The research goes on unseen.",
                    stopped="The Coill Trí learns of the work and forbids it.",
                    turned="The troupe befriends the Pact before anyone else knows.",
                ),
                S(
                    "The words of wisdom",
                    at=2,
                    clues=(
                        "A spirit born of Ádhamh's experiments flees on the "
                        "wind for fear of slavery and settles near the "
                        "player covenant. The villagers start speaking of "
                        "strange matters in a Latin none of them know. The "
                        "spirit is a store of magical knowledge with no "
                        "sense of how to use it, and it is fading."
                    ),
                    ignored="The spirit dies, and its knowledge with it.",
                    stopped="The spirit is guided back to its maker.",
                    turned="The troupe keeps what the spirit knows.",
                ),
                S(
                    "A true summoner",
                    at=3,
                    clues=(
                        "Learning that Tuathal's arts are Infernal, Ádhamh "
                        "looks beyond Connacht for a true magical summoner. "
                        "He writes to the apprentice the Coill Trí took from "
                        "him, asking her to tell him of any summoner her "
                        "covenant meets, and she is caught sending word."
                    ),
                    ignored="The girl keeps spying, and the Pact learns more.",
                    stopped="Her covenant cuts the link and questions her loyalty.",
                    turned=(
                        "Her covenant uncovers Ádhamh's research through her, "
                        "and chooses what to do with it."
                    ),
                ),
                S(
                    "A druid's Parma",
                    at=4,
                    clues=(
                        "Generations on, or sooner with help, the Pact's "
                        "breakthrough nears: Ireland's druids would gain a "
                        "defence like the Order's own."
                    ),
                    ignored=(
                        "The hedge wizards stand as the Order's equals, and "
                        "the balance the Treaty keeps is gone."
                    ),
                    stopped="The notes are destroyed or seized.",
                    turned=(
                        "The theory is brought into the Order, as the "
                        "Treaty's makers once hoped the old traditions might "
                        "be."
                    ),
                ),
            ],
        )
    )


# -- tying the stories to the other parts' records --


def _key(name: str) -> str:
    """A name compared loosely: case, accents, hyphens and a leading
    'The' set aside."""
    out = unicodedata.normalize("NFKD", name.casefold().strip())
    out = "".join(c for c in out if not unicodedata.combining(c))
    out = out.removeprefix("the ")
    return out.replace("-", " ").replace("_", " ").replace("’", "'")


def _find(records: list[Any], *names: str) -> Any | None:
    """The first record whose name is one of `names`, or failing that
    whose name starts with one of them as a whole word (so "Donn" finds
    "Donn, the Dark One"), loosely
    compared."""
    wanted = [_key(n) for n in names]
    for record in records:
        if _key(record.name) in wanted:
            return record
    for record in records:
        name = _key(record.name)
        if any(name.startswith((n + " ", n + ",")) for n in wanted):
            return record
    return None


def _add_to(record: Any, more: str, hidden: str = "", attr: str = "summary") -> None:
    """Add a paragraph to a record's summary (or notes), and `hidden` to
    its secrets."""
    setattr(record, attr, paragraphs(getattr(record, attr) or "", more))
    if hidden:
        record.secrets = paragraphs(record.secrets, hidden)


def _place(hibernia: Hibernia, places: list[Any], *keys: str) -> Any | None:
    """A place by one of the other parts' keys, or by one of its names."""
    for key in keys:
        found = hibernia.places.get(key)
        if found is not None:
            return found
    return _find(places, *keys)


def _character(hibernia: Hibernia, *names: str) -> Any | None:
    for name in names:
        found = hibernia.magi.get(name)
        if found is not None:
            return found
    return _find(hibernia.b.saga.characters, *names)


def _covenant(hibernia: Hibernia, *names: str) -> Any | None:
    for name in names:
        found = hibernia.covenants.get(name)
        if found is not None:
            return found
    return _find(hibernia.b.saga.covenants, *names)


#: Each covenant's key with the names it may go by.
COVENANTS: dict[str, tuple[str, ...]] = {
    "circulus_ruber": ("circulus_ruber", "Circulus Ruber"),
    "cliffheart": ("cliffheart", "Cliffheart"),
    "elks_run": ("elks_run", "Elk's Run"),
    "leth_moga": ("leth_moga", "Leth Moga", "The Mercer House of Leth Moga"),
    "ashenrise": ("ashenrise", "Ashenrise"),
    "lambaird": ("lambaird", "Lámbaird", "Na Lám Baird"),
    "paruchia": ("paruchia", "The Paruchia of Nerius", "Paruchia Nerius"),
    "praesis": ("praesis", "Praesis"),
    "leth_cuinn": ("leth_cuinn", "Leth Cuinn", "The Mercer House of Leth Cuinn"),
    "qui_sonant": ("qui_sonant", "Qui Sonant Pro Quieto", "Qui Sonant"),
    "vigil": ("vigil", "Vigil"),
}

#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target's possible keys or names, note).
LINKS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("threat_connacht", "characters", ("guillaume", "Guillaume"), "Leads the raids"),
    ("threat_connacht", "characters", ("ballack", "Ballack"), "Lord of Praesis"),
    ("threat_connacht", "characters", ("cacht", "Cacht"), "Waits for a new war"),
    (
        "threat_connacht",
        "characters",
        ("baetain", "Báetáin"),
        "Shares a tower with his friends' killer",
    ),
    ("threat_connacht", "characters", ("faolan", "Faolán"), "Already in Connacht"),
    ("threat_connacht", "covenants", COVENANTS["praesis"], "Where the raids begin"),
    ("threat_connacht", "covenants", COVENANTS["elks_run"], "On the Connacht border"),
    ("threat_connacht", "places", ("connacht", "Connacht"), "The land closed to magi"),
    ("threat_connacht", "places", ("lough_ree", "Lough Ree"), "Praesis's lake"),
    ("threat_connacht", "places", ("breifne", "Bréifne"), "Home of the mercenaries"),
    ("threat_treaty", "characters", ("milvia", "Milvia"), "The Praeco"),
    (
        "threat_treaty",
        "characters",
        ("visioturpis", "Visioturpis"),
        "The Presiding Quaesitor",
    ),
    ("threat_treaty", "characters", ("helles", "Helles"), "Leads the reformers"),
    ("threat_treaty", "covenants", COVENANTS["qui_sonant"], "A haven under the Treaty"),
    ("threat_treaty", "covenants", COVENANTS["vigil"], "Keeps the northern sea beasts"),
    ("threat_treaty", "covenants", COVENANTS["praesis"], "Holds leave to enter"),
    ("threat_treaty", "places", ("tara", "The Hill of Tara"), "Where it is tested"),
    ("threat_treaty", "places", ("connacht", "Connacht"), "The land it closes"),
    ("threat_treaty", "places", ("breifne", "Bréifne"), "Across the river"),
    (
        "threat_treaty",
        "places",
        ("black_pigs_dyke", "The Black Pig's Dyke"),
        "Kept broken by the druids",
    ),
    (
        "threat_treaty",
        "places",
        ("slieve_aughty", "Slieve Aughty"),
        "A border wanting a marker",
    ),
    ("threat_reform", "characters", ("helles", "Helles"), "Leads the debate"),
    (
        "threat_reform",
        "characters",
        ("pollices", "Pollices"),
        "Helles's fellow founder",
    ),
    ("threat_reform", "characters", ("konstanczia", "Konstanczia"), "Tremere backing"),
    ("threat_reform", "characters", ("dorjan", "Dorján"), "Tremere backing"),
    (
        "threat_reform",
        "characters",
        ("lugardis", "Lugardis"),
        "Writes in Hibernia's defence",
    ),
    ("threat_reform", "characters", ("igneous_drake", "Igneous Drake"), "A grievance"),
    ("threat_reform", "characters", ("milvia", "Milvia"), "Neutral"),
    ("threat_reform", "covenants", COVENANTS["ashenrise"], "The reformers' home"),
    ("threat_reform", "covenants", COVENANTS["elks_run"], "Leans on English nobles"),
    (
        "threat_reform",
        "covenants",
        COVENANTS["lambaird"],
        "The English Council's worry",
    ),
    ("threat_reform", "covenants", COVENANTS["circulus_ruber"], "Will not change"),
    (
        "threat_reform",
        "covenants",
        COVENANTS["cliffheart"],
        "Opposes English covenants",
    ),
    ("threat_reform", "places", ("tara", "The Hill of Tara"), "Where it is fought"),
    ("threat_grainne", "characters", ("maoilfhinnein", "Maoilfhinnéin"), "The plotter"),
    ("threat_grainne", "characters", ("grainne", "Gráinne"), "The sacrifice"),
    (
        "threat_grainne",
        "characters",
        ("guillaume", "Guillaume"),
        "The unwitting weapon",
    ),
    ("threat_grainne", "characters", ("einri", "Éinri"), "Vigil's leader"),
    (
        "threat_grainne",
        "characters",
        ("dalton", "Dalton"),
        "Courted by Vigil's ambassador",
    ),
    ("threat_grainne", "covenants", COVENANTS["vigil"], "The covenant at stake"),
    ("threat_grainne", "covenants", COVENANTS["lambaird"], "Courted"),
    ("threat_grainne", "covenants", COVENANTS["praesis"], "Where the shards are sent"),
    (
        "threat_grainne",
        "places",
        ("inishtrahull", "Inishtrahull"),
        "The refuge prepared",
    ),
    (
        "threat_grainne",
        "places",
        ("banbhas_crown", "Banbha's Crown"),
        "Left behind if Vigil goes",
    ),
    ("threat_ballack", "characters", ("ballack", "Ballack"), "The debtor"),
    (
        "threat_ballack",
        "characters",
        ("guillaume", "Guillaume"),
        "Brings in Connacht's vis",
    ),
    ("threat_ballack", "characters", ("baetain", "Báetáin"), "The traitor who stayed"),
    ("threat_ballack", "characters", ("meadhbh", "Meadhbh"), "Waits to return"),
    ("threat_ballack", "covenants", COVENANTS["praesis"], "The prize on loan"),
    ("threat_ballack", "covenants", COVENANTS["qui_sonant"], "Meadhbh's sanctuary"),
    ("threat_ballack", "places", ("lough_ree", "Lough Ree"), "Its stripped sources"),
    ("threat_donn", "creatures", ("Donn",), "The death god"),
    (
        "threat_donn",
        "characters",
        ("faisgia", "Faisgia"),
        "Hunts the Schism War's faeries",
    ),
    ("threat_donn", "covenants", COVENANTS["cliffheart"], "Watches Teach Duínn"),
    ("threat_donn", "covenants", COVENANTS["circulus_ruber"], "In the army's path"),
    (
        "threat_donn",
        "places",
        ("teach_duinn", "Teach Duínn", "Tech Duínn"),
        "His island",
    ),
    ("threat_donn", "places", ("salmons_eye", "Salmon's Eye"), "His old allies"),
    ("threat_donn", "places", ("warblers_way", "Warbler's Way"), "His old victims"),
    ("threat_donn", "places", ("cuailnge", "Cuailnge"), "The faerie-blooded children"),
    (
        "threat_gaileoin",
        "places",
        ("arainn_thiar", "Árainn Thiar", "aran_isles", "The Aran Isles", "aran"),
        "The Gaileoin's island",
    ),
    (
        "threat_gaileoin",
        "places",
        ("tempull_bheanain", "Tempull Bheanáin"),
        "The island's hidden holy place",
    ),
    ("threat_gaileoin", "places", ("connacht", "Connacht"), "Closed to magi"),
    ("threat_giant", "covenants", COVENANTS["qui_sonant"], "Sings the giant asleep"),
    ("threat_giant", "characters", ("cantarus", "Cantarus"), "Master of the Songs"),
    ("threat_giant", "characters", ("finn", "Finn"), "Would-be heir"),
    ("threat_giant", "characters", ("turlough", "Turlough"), "Keeper of the cemetery"),
    (
        "threat_giant",
        "characters",
        ("mael_ruanaid", "maelruanaid", "Máel-ruanaid"),
        "Studies the songs' magic",
    ),
    ("threat_giant", "places", ("cuailnge", "Cuailnge"), "The giant's ridge"),
    ("threat_aillen", "places", ("tara", "The Hill of Tara"), "What he burns"),
    (
        "threat_aillen",
        "places",
        ("mound_of_hostages", "The Mound of Hostages"),
        "The Tuatha Dé's mound on the hill",
    ),
    ("threat_aillen", "places", ("connacht", "Connacht"), "His lair, closed to magi"),
    (
        "threat_aillen",
        "covenants",
        COVENANTS["circulus_ruber"],
        "Builds the meeting's camp",
    ),
    (
        "threat_mellifont",
        "places",
        ("bru_na_boinne", "Brú na Bóinne", "The Brú na Bóinne"),
        "The granges",
    ),
    (
        "threat_mellifont",
        "places",
        ("new_grange", "New Grange", "Newgrange"),
        "Aonghus's mound",
    ),
    (
        "threat_mellifont",
        "creatures",
        ("Aonghus", "Aonghus mac Óg"),
        "Wakes if disturbed",
    ),
    ("threat_oireadh", "places", ("oireadh", "Oireadh"), "Where the Pact meets"),
    ("threat_oireadh", "places", ("lough_conn", "Lough Conn"), "Umor's hills"),
    ("threat_oireadh", "places", ("rosbeg", "Rosbeg"), "Tuathal's forge"),
    ("threat_oireadh", "places", ("cong", "Cong"), "Ádhamh's patron"),
    ("threat_oireadh", "covenants", COVENANTS["praesis"], "The Pact's old ally"),
    ("threat_oireadh", "characters", ("meadhbh", "Meadhbh"), "Whom the Pact deserted"),
)

#: Each story's place: covenants whose place to use, then place keys and
#: names to try, then the region's key as the fallback.
PLACES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "threat_connacht": (COVENANTS["praesis"], ("lough_ree", "Lough Ree"), "connacht"),
    "threat_treaty": ((), ("tara", "The Hill of Tara"), "meath"),
    "threat_reform": ((), ("tara", "The Hill of Tara"), "ireland"),
    "threat_grainne": (
        COVENANTS["vigil"],
        ("cionn_mhalanna", "Cionn Mhálanna"),
        "ulster",
    ),
    "threat_ballack": (COVENANTS["praesis"], ("lough_ree", "Lough Ree"), "connacht"),
    "threat_donn": ((), ("teach_duinn", "Teach Duínn", "Tech Duínn"), "munster"),
    "threat_gaileoin": (
        (),
        ("arainn_thiar", "Árainn Thiar", "aran_isles", "The Aran Isles", "aran"),
        "connacht",
    ),
    "threat_giant": (COVENANTS["qui_sonant"], ("cuailnge", "Cuailnge"), "ulster"),
    "threat_aillen": ((), ("tara", "The Hill of Tara"), "meath"),
    "threat_mellifont": (
        (),
        ("bru_na_boinne", "Brú na Bóinne", "The Brú na Bóinne"),
        "meath",
    ),
    "threat_oireadh": ((), ("oireadh", "Oireadh"), "connacht"),
}

#: Factions other parts may make that stand behind a story.
BEHIND: dict[str, tuple[str, ...]] = {
    "threat_reform": ("The English Council", "English Council"),
    "threat_oireadh": ("The Pact of Oireadh", "Pact of Oireadh"),
}

#: The private feuds: (one magus's keys or names, the other's, the line in
#: the first one's notes, the line in the other's). A rival no part made
#: gets no link, and only the first one's line.
FEUDS: tuple[tuple[tuple[str, ...], tuple[str, ...], str, str], ...] = (
    (
        ("einri", "Éinri"),
        ("dalton", "Dalton"),
        "Feud: Dalton Ballaugh of Lámbaird. They have fought certamen after "
        "certamen and their grogs clash often; it is not yet Wizard War, but "
        "they loathe each other, perhaps because they and their covenants "
        "are so alike.",
        "Feud: Éinri mac Cillíni of Vigil, who has learned the cost of "
        "Dalton's fire in years of certamen and skirmishes between their "
        "grogs, short of Wizard War so far.",
    ),
    (
        ("grainne", "Gráinne"),
        ("cu_chonnacht", "Cú Chonnacht"),
        "Feud: Cú Chonnacht Cluasach Mac Tire of Bjornaer. Their Wizard War "
        "has never ended, though they have met face to face many times; the "
        "Hibernian Code presumes a war goes on until death, surrender or "
        "treaty.",
        "Feud: Gráinne inghean Uaitéar of Vigil, in a Wizard War that has "
        "never been ended, however often they have met.",
    ),
    (
        ("guillaume", "Guillaume"),
        ("grainne", "Gráinne"),
        "Feud: Gráinne inghean Uaitéar of Vigil, who has slighted him many "
        "times; he wants nothing more than to see her humbled.",
        "Feud: Guillaume Flambeau of Praesis, an old rival who longs to see "
        "her humbled.",
    ),
    (
        ("lewis", "Lewis"),
        ("peter", "Peter"),
        "Feud: Peter of Verditius, once Qui Sonant's second stonemason, who "
        "left when the two quarrelled over Ingasia's claim to be "
        "Verditius's domus magna and Finn sided with Lewis. Peter, now an "
        "exile on the roads, is about to escalate the vendetta, and would "
        "gladly exploit Lewis's warning-off of rivals for a Gifted child of "
        "the tithe.",
        "Feud: Lewis of Verditius, the master stonemason of Qui Sonant, who "
        "drove him out over Ingasia's claim to be the House's domus magna.",
    ),
)

#: The book's story seeds, each added to the first of its places or
#: covenants that exists ("covenant:" before a covenant's key; a covenant
#: takes it in its notes), with the province or island as the last
#: fallback: (targets, the seed, what only the storyguide knows).
SEEDS: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (
        ("fionntans_grave", "Fionntan's Grave", "river_shannon", "The River Shannon"),
        "Story seed: Finding Fionntan. Ireland's first druid, Fionntan, who "
        "survived the Flood as a salmon, is said to be over four thousand "
        "years old and to live in a cave under the Shannon. Pagan once, he "
        "was converted by one Trefuilngid. Is he Divine, a man turned "
        "magical, or a faerie? The answer matters to any magus hunting the "
        "same long life.",
        "",
    ),
    (
        ("rath_cinn_eich", "Ráth Cinn-Eich", "widows_throat", "The Widow's Throat"),
        "Story seed: The Secret of Ráth Cinn-Eich. Nemed's royal fort on "
        "the slopes of Slieve Croob was dug by four Fomóir slave brothers; "
        "Diedne's covenant of the Widow's Throat later rose on its ruins and "
        "fell in the Schism War. Nobody has explored the deep Fomóir "
        "passages beneath, where treasure, Fomóir enchantments and Diedne "
        "lore may lie.",
        "",
    ),
    (
        ("ireland",),
        "Story seed: The High-King's Treasure. Many high-kings found faerie "
        "treasures, some of them true enchanted items made by the Tuatha "
        "Dé's Gifted craftsmen, and took them to the grave or lost them back "
        "to the Tuatha Dé, who hid them again. Since clans seldom move, a "
        "magus who wants such an item need only find its old owner's "
        "homestead and start opening barrows.",
        "",
    ),
    (
        ("ulster",),
        "Story seed: Recovering the First Christian Mission. An Ulster "
        "monastery's book says Palladius, hounded by worshippers of Crom "
        "Cruach, was destroyed by the god at the church of the Kindred of "
        "Cormac. His followers buried his books, with relics of Saints Peter "
        "and Paul, under a stone church that the cult pulled down; its "
        "successor may not stand on the spot, and the cult may live on.",
        "",
    ),
    (
        ("connacht",),
        "Story seed: The Lair of Lentinus. Lentinus of Flambeau sold "
        "protection to hedge wizards for vis, and those who refused his "
        "terms soon suffered a magical attack. He belonged to no covenant "
        "and died in a Wizard War, and his hoard of vis and books has never "
        "been found; magi still slip into Connacht to look for it.",
        "",
    ),
    (
        ("aran_isles", "The Aran Isles", "arainn_mhor", "Árainn Mhór", "connacht"),
        "Story seed: The Missing Mercere Envoy. When the Fomóir and the "
        "Tuatha Dé sided with Diedne, the Redcap Blakehalloc sailed to Aran "
        "to learn whether the Fir Bolg would join them, and never came back. "
        "Counted among the Schism War's dead, he was never sought, and his "
        "mission remains a mystery.",
        "",
    ),
    (
        ("covenant:qui_sonant", "covenant:cliffheart"),
        "Story seed: Three Diedne Bodies. No one knows what became of the "
        "three Diedne who fell at Clontarf. Cliffheart claims one as its "
        "cathach, though it fought nowhere near the battle; others say Qui "
        "Sonant buried each in the grave of a Hermetic rival, and none had "
        "Christian burial. Hibernia has no law against digging into its "
        "Diedne past, and a Seeker who wants to question a Diedne ghost may "
        "ask the characters' help.",
        "",
    ),
    (
        ("covenant:circulus_ruber",),
        "Story seed: Hermetic Hospitality. Circulus Ruber lodges a "
        "provincial king and two hundred followers overnight with "
        "magically made food and shelter, but conjured food does not "
        "nourish, and by morning the whole company is starving. The king "
        "demands two hundred cows, which the covenant will not pay, and the "
        "characters are asked to find another way to appease him.",
        "",
    ),
    (
        ("breifne", "Bréifne", "connacht"),
        "Story seed (Falling on Deaf Ears): in Bréifne, a farmer "
        "promises a seventh part of his harvest for seven years to whoever will free his "
        "son from a witch's enchantment; the witch is protected by an Uí "
        "Raghallaigh noble. Finding no druid, he comes east to the magi. "
        "Can they act themselves, or only through agents?",
        "",
    ),
    (
        ("diocese_of_mayo", "The Diocese of Mayo", "mayo", "Mayo", "connacht"),
        "Story seed: An Appeal. The clergy of Mayo ask a clerical companion "
        "to carry their case against the diocese's dissolution to Rome, "
        "hoping an outsider's voice adds weight. Menacing visitors, "
        "apparently sent by the Archbishop of Tuam, show that someone will "
        "go to supernatural lengths to keep Mayo under Tuam.",
        "The archbishop may be only a pawn in a larger game.",
    ),
    (
        ("tuam", "Tuam", "connacht"),
        "Story seed: The Devils of Tuam. With no cathedral and little "
        "leadership, Tuam's merchants govern themselves and grow rich while "
        "harvests fail and sickness spreads outside the walls. Desperate "
        "men turn to robbery and raiding, and hedge wizards, perhaps magi "
        "too, feel it. Do the characters punish the strays, or face what "
        "drove them?",
        "Demons are stirring both the greed and the hardship.",
    ),
    (
        ("athlone", "Athlone", "meath"),
        "Story seed: The Swords of the Fer Caille. Savage warriors put "
        "villages on the Meath bank of the Sionainne to the sword, and the "
        "Bishop of Athlone asks Leinster's magi for help. The raiders are "
        "Fer Caille, faeries seeking mortal heroes to fight, and Connachta "
        "men are following their lead against Meath's holdings. How do the "
        "magi arm their people, and what do they order done with the men "
        "of Connacht?",
        "",
    ),
    (
        ("athlone", "Athlone", "meath"),
        "Story seed: The Cry of the Banshee. A banshee wails, and the "
        "youngest of the family of Congal Mac an Fhailghigh sees her by "
        "their door. The boy runs into the night to find the characters and "
        "begs them to stop her or change his family's doom. Why, on this "
        "cold dark night, are so many English clergy and knights riding "
        "into town?",
        "",
    ),
    (
        ("rosbeg", "Rosbeg", "oireadh", "Oireadh", "connacht"),
        "Story seed: The Diabolist's Dying Wish. Tuathal an Iarrainn's "
        "goetic master has died in Dublin, leaving money and a large book in "
        "Latin and cipher to be sent to Tuathal at Rosbeg. Someone saw what "
        "the book was, and it has reached the player covenant through a "
        "companion. It is a book of Infernal Lore about particular demons. "
        "Keep it, deliver it, or look across the border for diabolism?",
        "",
    ),
    (
        ("lough_conn", "Lough Conn", "connacht"),
        "Story seed: An Evil Wind. An Infernal wind spreads a sickness the "
        "magi cannot cure, but a Fir Domhnann healer is said to live among "
        "men in Connacht. Barred from crossing, the magi send companions to "
        "find Umor Ard Mac Adar in the hills above Lough Conn and bring him "
        "back in time.",
        "Umor's three cousins have come into Connacht to kill him, and the "
        "companions must run their gauntlet.",
    ),
    (
        ("covenant:praesis",),
        "Story seed: Remember Who You Work For. A player character who has "
        "joined a cult or society is ordered to carry a message to Ballack, "
        "who has been forgetting what he owes certain powerful, mysterious "
        "benefactors (see Ballack's Debts). Can a younger magus bring the "
        "society's authority to bear on him?",
        "",
    ),
    (
        ("connacht",),
        "Story seed (The Broken Treaty): a magus named Faolán, whose "
        "parens was one of the true Ollamhain and whose grasp of the Arts is "
        "slight, fled into Connacht before Praesis fell and counts himself "
        "nearer the druids than the Order. His long stay is a plain breach "
        "of the Treaty. When the Tribunal learns where he is and that he has "
        "turned his back on the Order, the characters are sent to bring him "
        "back, with the Coill Trí's help or without it: a manhunt in hostile "
        "country.",
        "",
    ),
    (
        ("bannow", "Bannow", "leinster"),
        "Story seed: The Bay of Bannow. Bannow's harbour, where the English "
        "first landed, is silting up faster than anyone remembers, and "
        "other harbours round the coast have begun to follow. Some blame a "
        "cailleach's curse for letting the invaders land, others a "
        "fisherman who killed a seal maiden. The priest has seen in a vision "
        "that air, fire and water will finish what the mud began, and seeks "
        "learned help.",
        "",
    ),
    (
        ("ferns", "Ferns", "ferns_castle", "Ferns Castle", "leinster"),
        "Story seed: The Marshal's Curse. William Marshal the younger "
        "promised his father to keep his Irish lands whole and will not "
        "give back the two manors the Bishop of Ferns claims, yet he will "
        "not remarry and sire an heir until the bishop's curse on his line "
        "is lifted. Did the kiss of peace the Pope forced on them lift it? "
        "The bishop swore it would hold till the lands came back, so William "
        "may seek unusual help, even Hermetic.",
        "",
    ),
    (
        ("ferns", "Ferns", "ferns_castle", "Ferns Castle", "leinster"),
        "Story seed: Helen of Ireland. The tale of Derbforgaill feeds the "
        "faerie Aonghus, who stirs elopements and abductions to start wars "
        "and still does so gladly. The Bishop of Ferns has warned William "
        "the younger of him, which is why William's great new castle is "
        "meant to keep his young daughter safe from abduction as she grows "
        "up.",
        "",
    ),
    (
        ("glendalough", "Glendalough", "leinster"),
        "Story seed: Divine Vis. Saint Kevin's Fruit can be dried over a "
        "month by someone versed in Magic Theory, and then yields Divine "
        "vis: Corpus if dried in a Magic aura, Creo if dried in a Divine "
        "one.",
        "",
    ),
    (
        ("pool_of_the_puca", "The Pool of the Púca", "wicklow", "leinster"),
        "Story seed: The Púca Speaks? The Púca may not be the mindless beast "
        "it seems. It might give up its killings for favours or conditions, "
        "and might ask to be ridden to Tribunal to speak for itself there.",
        "It may instead be a powerful Infernal being, whose wishes will be "
        "neither pleasant nor easily met.",
    ),
    (
        ("kildare", "Kildare", "leinster"),
        "Story seed: Dousing the Fire. Archbishop Henry de Londres has "
        "sworn publicly to put out Saint Brigid's perpetual fire, and is "
        "worried: a failure would hearten the Ua Broin and Ua Túathal, whose "
        "outlaws will try to stop him. He rides to Kildare with knights and "
        "mercenaries, and is pragmatic enough to want magical help against "
        "what he takes for old druid magic, perhaps a maga, since a woman "
        "might pass where a man cannot.",
        "",
    ),
    (
        ("carbury", "Carbury", "naas", "Naas", "leinster"),
        "Story seed: Tales of Nuadha and Bóinn. Nuadha stands for the kings "
        "of Leinster: if an epic tale mended his silver arm so he could "
        "climb the dun of Naas, the kingship rites might return. Bóinn would "
        "rather her husband serve, and favours stories of power flowing into "
        "Meath, like the Boyne, the Boroimhe tribute, or the justiciarship "
        "passing from FitzHenry to de Lacy. Either may draw characters into "
        "a reenactment of an ancient tale, here or in Elysium, with dreadful "
        "results.",
        "",
    ),
    (
        ("kilkenny", "Kilkenny", "leinster"),
        "Story seed: The Witches of Kilkenny. Kilkenny blames a coven of "
        "dark witches for the accidents that dog its new cathedral. The "
        "witches are secretive, and resolving their quarrel will be hard.",
        "The accidents are only accidents: the witches belong to the Coill "
        "Trí and are busy with a long feud among themselves.",
    ),
    (
        (
            "new_grange",
            "New Grange",
            "Newgrange",
            "bru_na_boinne",
            "Brú na Bóinne",
            "meath",
        ),
        "Story seed: The Haunting of New Grange. Mellifont's lay brothers at "
        "New Grange tell of terrors and of trooping faeries wrecking the "
        "crops; then the steward and his family vanish one summer evening, "
        "and Abbot Thomas, troubled enough by his revolt, seeks help at "
        "once. Can the characters save the monks from Aonghus's anger (see "
        "The Conspiracy of Mellifont)?",
        "",
    ),
    (
        ("desmond", "Desmond", "munster"),
        "Story seed: Returning the King. The Red Book of Cloyne says Eoghan "
        "Mór did not die at Magh Léana: a faerie woman, Éadaoin, carried him "
        "into an invisible yew, healed him, and keeps him still, telling him "
        "he won and has been with her only days. The yew's reflection shows "
        "in the stream, but the regio has never been found, and failing "
        "Eoghanachta kings ask magi to bring him home.",
        "",
    ),
    (
        ("desmond", "Desmond", "munster"),
        "Story seed: The Midnight Builder. The Uí Mathghamhna's twelve "
        "coastal castles, all of stone, rose so fast that some magi suspect "
        "magic. Is a magus raising castles overnight for the túath? "
        "Cliffheart, known to favour the Irish, lies close by.",
        "",
    ),
    (
        ("magh_nala", "Magh nAla", "desmond", "munster"),
        "Story seed: Seeking the Plain of Swans. Mac Cárthaigh's hidden ráth "
        "is reached only by forest roads, and one is the road of the Coitse "
        "Bodhar, the Silent Wagon, whose faerie driver runs travellers down "
        "and throws them into a faerie forest to wander. The characters may "
        "be asked to find people who went looking for Magh nAla and never "
        "arrived.",
        "",
    ),
    (
        ("cork", "Cork", "munster"),
        "Story seed: The Siege of Shandon Castle. Shandon's squat tower is "
        "the keystone of Cork's defences, and Diarmait mac Cárthaigh has "
        "set his lightning-hurling hedge wizards to destroy it. If they "
        "succeed, the defeated may blame the Order, Ireland's best-known "
        "wizards. Should the magi stop them?",
        "",
    ),
    (
        ("thomond", "Thomond", "munster"),
        "Story seed: The Stealer of Secrets. Some Uí Briain warriors lie "
        "buried upright, weapon in hand, facing Connacht, in nearly a "
        "hundred mounds along Thomond's northern border. A hedge wizard has "
        "learned to speak with them and is plundering their memories for "
        "military secrets, and the robbed ghosts wail until the countryside "
        "cannot sleep. Stop the wizard, or at least lay the ghosts.",
        "",
    ),
    (
        ("river_shannon", "The River Shannon", "munster"),
        "Story seed: The Fish Wife. In a deep bend of the Shannon lives a "
        "bandraoi, a sea witch who takes any fish's shape or a lovely "
        "woman's. She lures fishermen to kiss her, becomes a great pike as "
        "they lean in, and drags them down by the face. Characters may be "
        "her victims or their rescuers.",
        "",
    ),
    (
        ("killaloe", "Killaloe", "thomond", "munster"),
        "Story seed: The King's Treasure. After the recent raid King "
        "Donnchadh buried his treasures, and when his most faithful warrior "
        "boasted he would guard them even in death, the king took him at his "
        "word and killed him. Now he has forgotten the spot and asks the "
        "characters to find it, without mentioning the ghost that waits "
        "there.",
        "",
    ),
    (
        (
            "church_of_st_flannan",
            "The Church of St Flannan",
            "killaloe",
            "Killaloe",
            "munster",
        ),
        "Story seed: The Faerie Saint Flannan. Saint Flannan foresaw only "
        "deaths, but the legend has grown until a social faerie has taken "
        "his part, visiting the cathedral's architect at night. The abbot "
        "notes that the building is going a little crooked and sprouting "
        "pagan images, and that the 'saint' calls only at the architect's "
        "house.",
        "",
    ),
    (
        ("cashel", "Cashel", "munster"),
        "Story seed: The Sacred Yew. The Eoghanachta once revered a yew at "
        "Cashel's heart, cut down in the Dál gCais raids. Their hedge "
        "wizards say the clan will not rise until a new one grows, and an "
        "Uí Cerbaill sorcerer can grow a yew from seed overnight. The monks "
        "keep felling his trees, and a Cashel envoy seeks a magus to stop "
        "him.",
        "",
    ),
    (
        ("waterford", "Waterford", "The Liberty of Waterford", "munster"),
        "Story seed: The Secret Army. Déise raiders strike English towns and "
        "castles in the Liberty of Waterford, and no one can find where "
        "their full-time leaders hide. Is the stronghold magically "
        "concealed in the inland woods? Ashenrise has taken an interest and "
        "is asking Redcaps what they know.",
        "",
    ),
    (
        ("waterford_city", "Waterford City", "waterford", "Waterford", "munster"),
        "Story seed: The Ruinous Toad. Before the English came, a toad, a "
        "creature unknown in Ireland, was found on a Waterford quay, and "
        "seers called it an evil omen. Toads have multiplied since, and a "
        "French merchant is said to have brought in a venomous snake. Have "
        "the English changed something in Ireland's supernatural fabric?",
        "",
    ),
    (
        ("covenant:leth_moga",),
        "Story seed: The Missing Book. Leth Moga is poorly defended, and one "
        "morning the Red Book is gone from the scriptorium. Diarmait "
        "assumes a youth in the macgnímartha took it, as they take cathaigh, "
        "and asks the characters to get it back; a trail leads to the woods "
        "around the Killarney lakes.",
        "The trail is false. The thief is an older magus who wants an "
        "inglorious episode cut from the annals, and hopes to slip the book "
        "back while the characters search the woods.",
    ),
    (
        ("leacht_abartaigh", "Leacht Ábartaigh", "ulster"),
        "Story seed: The Neamh-Mairbh. Ábhartach's forgotten grave is being "
        "cleared for farming. Felling a hawthorn over it, a workman cuts off "
        "his own hand, and his blood soaks into the ground; the earth "
        "rumbles, the men flee, and that night the evil dwarf magician rises "
        "again, perhaps a dark faerie, perhaps an infernal sorcerer, and "
        "begins to master the land once more.",
        "",
    ),
    (
        ("erenagh", "Erenagh", "iniscourcy", "Iniscourcy", "ulster"),
        "Story seed: Echoes at Erenagh. Survivors of the 1177 slaughter at "
        "Erenagh meet in its haunted ruins with monks recruited from "
        "Iniscourcy, plotting to drive out the English. An English friend "
        "of the characters is attacked without cause by an Irish monk who "
        "proves to have been possessed, and the trail leads back to the "
        "ruined monastery.",
        "The murdered monks' ghosts have been whispering compulsions to "
        "their living brothers, and the plot has turned to bloody revenge.",
    ),
    (
        ("sliabh_cruibe", "Sliabh Crúibe", "mountains_of_mourne", "ulster"),
        "Story seed: The Demon Kings of Sliabh Crúibe. On Cairn Sunday local "
        "people carry stones up the mountain to help bury twelve kings, and "
        "magi have found that some of the stones hold vis, gathered over "
        "many years.",
        "Eleven of the graves hold a demon bound in a dead tyrant's body. "
        "The Cailleacha Phiseogach know that if mortal hands uncover them "
        "they will rise, and that the world ends when a twelfth king joins "
        "them; unable to dig themselves, they make sure greedy magi hear of "
        "the vis.",
    ),
    (
        ("covenant:leth_cuinn", "ulster"),
        "Story seed: A Rival School. Some Redcaps resent that only Leth "
        "Cuinn teaches the clesa, and mean to quest into Arcadia for one or "
        "all of Scáthach's sons to found a rival school. Characters refused "
        "initiation may be recruited by them, or friends of the Mercer House "
        "asked to stop them.",
        "",
    ),
    (
        ("covenant:qui_sonant", "ulster"),
        "Story seed: The Body of a Ghost. Envoys of a covenant ask to speak "
        "with a member buried some fifty years ago, but the summoning fails: "
        "someone has destroyed the spirit. Did someone at Qui Sonant break "
        "that trust, and what are they hiding?",
        "",
    ),
    (
        ("the_bards", "The Bards", "bards", "ireland"),
        "Story seed: The Ollamhain Heresy. The Ollamhain, faerie wizards "
        "who use music to conjure glamour and borrow the title of ollamh "
        "without its burdens, are scorned by the bardic schools, and "
        "wordsmiths have tried to prosecute them at the Sacred Council. A "
        "rival covenant's bard may prove to be one; the schools' enmity "
        "could be turned against him, in a war of satire and rhymed slander.",
        "",
    ),
    (
        ("ireland",),
        "Story seed: Sometimes They Return. A child makes an abandoned "
        "faerie ráth his secret den, and after a month of play he vanishes. "
        "Its owner, a brutish swamp ogre, has come home. Was the boy eaten, "
        "flayed, or sold to another faerie? The magi must find out and save "
        "him.",
        "",
    ),
    (
        ("tuatha_de", "The Tuatha Dé", "The Tuatha Dé Danann", "ireland"),
        "Faerie story seeds. The Tuatha Dé repeat their tales and pull "
        "onlookers in. The Dagda makes villagers hollow out the ground "
        "and heap porridge into it, or bursts into a coast village with a Fomóir's wife, "
        "her husband's ship just offshore. A rebel steals one of Manannán's "
        "cloaks of invisibility to raid the English, and the faerie harries "
        "the village until it is returned. Thieves brew Goibhniu's ale of "
        "immortality and sell it, not knowing it turns to poison within a "
        "month. A covenfolk's old Irish sickness defies Hermetic healing "
        "and needs one of Dian Céacht's pools. Donn steals Goibhniu's cow "
        "and hides it in a king's ráth, and Goibhniu arms trooping faeries "
        "to raid it. Lugh raids the Fomóir isles again with young men, among "
        "them some in their macgnímartha. A physician sees Badhbh on his "
        "way to his king. Fionn and his fian burst into a wedding to take "
        "back an eloping Leinster bride. Faeries play saints and devils "
        "too: a false Saint Patrick, a devil cat who feeds on a priest's "
        "fears, a dicing devil who leaves a grog drained and sure he met "
        "Satan.",
        "",
    ),
)

STORIES = paragraphs(
    "Stories. The book frames the saga as change coming to Hibernia: the "
    "English magi mean to remake the Tribunal and the Ordo Hiberniae means "
    "to keep it, and the characters may drive the change, soften it or "
    "fight it. Under way in 1220 are Guillaume's push into Connacht from "
    "Praesis, the test of the Treaty of Cnoc Maol Réidh at Tara in 1221, "
    "and the English reform motions. Others wait for the storyguide to "
    "begin them: Maoilfhinnéin's plot against Gráinne, Ballack's debts, "
    "Donn's army, the Gaileoin infernalists, the giant under Qui Sonant, "
    "Áillen burning Tara, the Conspiracy of Mellifont and the Pact of "
    "Oireadh's Parma. Four private feuds run between magi, and the book's "
    "smaller story seeds sit on the places and covenants they use.",
)


def finish(hibernia: Hibernia) -> None:
    saga, world = hibernia.b.saga, hibernia.world
    places = [n for n in saga.neighbours if n.kind == "place"]
    factions = [n for n in saga.neighbours if n.kind == "faction"]
    for key, kind, names, note in LINKS:
        if kind == "characters":
            target = _character(hibernia, *names)
        elif kind == "covenants":
            target = _covenant(hibernia, *names)
        elif kind == "creatures":
            target = _find(saga.creatures, *names)
        else:
            target = _place(hibernia, places, *names)
        if target is not None:
            Builder.link(world[key], kind, target, note)
    for key, (covenants, names, region) in PLACES.items():
        place_id = None
        covenant = _covenant(hibernia, *covenants) if covenants else None
        if covenant is not None and covenant.place_id:
            place_id = covenant.place_id
        if place_id is None:
            place = _place(hibernia, places, *names) if names else None
            place = place or hibernia.places.get(region)
            place_id = place.id if place is not None else None
        if place_id is not None:
            world[key].place_id = place_id
    for key, names in BEHIND.items():
        faction = _find(factions, *names)
        if faction is not None:
            world[key].answers_to = faction.id
    _feuds(hibernia)
    _seeds(hibernia, places + factions)
    tribunal = hibernia.tribunal or next(iter(saga.tribunals), None)
    if tribunal is not None:
        _add_to(tribunal, STORIES)


def _feuds(hibernia: Hibernia) -> None:
    """Each feud as a link from one magus to the other, with a line in
    both their notes; a rival no part made gets only the other's line."""
    for one_names, other_names, one_line, other_line in FEUDS:
        one = _character(hibernia, *one_names)
        other = _character(hibernia, *other_names)
        if one is None:
            continue
        _add_to(one.description, one_line, attr="biography")
        if other is None:
            continue
        Builder.link(one, "characters", other, "Feud")
        _add_to(other.description, other_line, attr="biography")


def _seeds(hibernia: Hibernia, places: list[Any]) -> None:
    """Each seed on the first of its targets that exists; one with none
    found is left out."""
    for targets, text, hidden in SEEDS:
        for target in targets:
            if target.startswith("covenant:"):
                key = target.removeprefix("covenant:")
                covenant = _covenant(hibernia, *COVENANTS.get(key, (key,)))
                if covenant is not None:
                    _add_to(covenant, text, hidden, attr="notes")
                    break
                continue
            place = _place(hibernia, places, target)
            if place is not None:
                _add_to(place, text, hidden)
                break
