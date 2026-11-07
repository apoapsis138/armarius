"""The saga's stories, in paraphrase: each a threat whose stages lay out
how it unfolds if the troupe ignores, stops or turns it (L23).

The book's frame is the Treaty of Baghdad under strain: the Crusade at
Damietta has the Crusader magi calling for war, the counter-Crusaders
fight them in secret, and the mediators try to hold the peace, with the
characters as go-betweens among the factions or between the Order and
the Muslims' rulers.

Under way in 1220: the Treaty's renewal vote, dated to the meeting of
1221 (world["threat_treaty"]), and Aedes Veritatis's secret war on
Foothold (world["threat_secret_war"]).

Dormant until the storyguide begins them: 'Umar's double loyalty
(world["threat_umar"]), Esther's trade (["threat_esther"]), Rufus's
hoard (["threat_rufus"]), Amber against her House (["threat_amber"]),
Aurora's health and the Embassy's succession (["threat_aurora"]), Fade
and Wraith (["threat_urbs_rubra"]), Heliobus's bloc
(["threat_heliobus"]), the Theban border (["threat_theban_border"]),
Arash (["threat_arash"]), the True Cross's call (["threat_true_cross"])
and the opening of the pyramids (["threat_pyramids"]).

The Fifth Crusade and the Mongol Conquest are east.py's shared threats
(world["fifth_crusade"], world["mongol_conquest"]), with the Levant's
stages already in them: they are not remade, and only the Fifth
Crusade's place is set here (world["damietta"]) when it has none.

`finish` puts each story at the place where it plays out, ties it to
the covenants, magi, creatures and places the other parts made (found
by key or by name, and skipped when missing), adds the book's 31 story
seeds as one line each under "Story seeds" in the summary or notes of
the record each hangs on (the region when that record is missing, or is
a shared one whose text is not this pack's to change), and closes the
Tribunal's summary with a word on the stories."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING, Any

from ...models import Covenant, Creature, as_secrets, secret_words
from ..builder import Builder, dormant, paragraphs

if TYPE_CHECKING:
    from . import Levant

S = Builder.stage
DATED = "Fixed dates"


def build(levant: Levant) -> None:
    _treaty(levant)
    _secret_war(levant)
    _umar(levant)
    _esther(levant)
    _rufus(levant)
    _amber(levant)
    _aurora(levant)
    _urbs_rubra(levant)
    _heliobus(levant)
    _theban_border(levant)
    _arash(levant)
    _true_cross(levant)
    _pyramids(levant)


# -- under way in 1220 --


def _treaty(levant: Levant) -> None:
    levant.world["threat_treaty"] = levant.b.threat(
        "The Renewal of the Treaty of Baghdad",
        summary=paragraphs(
            "Muslim law lets a truce stand for ten years at most, so the "
            "Treaty of Baghdad must be renewed every decade. It was renewed "
            "for 1203 and, by a whisker, for 1213; the meeting at Domus "
            "Pacis in 1221 must decide whether it runs again from 1223. "
            "The Crusade in Egypt has put it under more strain than ever. "
            "Foothold, Para Belli and the True Cross want it thrown out so "
            "that they can help their kin at Damietta; Aedes Veritatis "
            "backs it, since it shields the Muslims; the Hermetic Embassy "
            "and Domus Pacis argue that without it the Tribunal falls back "
            "into the chaos before 1193.",
            "Both sides are already counting heads. The aloof covenants "
            "have not made up their minds, and Heliobus of the Pyramids "
            "speaks for twelve magi. The Praeco and the presiding "
            "quaesitor do not vote. If the Treaty is kept little changes; "
            "if it falls, the Embassy must leave Baghdad at once, and "
            "Foothold is likely to be the first covenant to burn.",
        ),
        secrets=paragraphs(
            "The book's guess at the future: the Treaty fails, perhaps "
            "once the True Cross is lost at Damietta, and the Tribunal "
            "joins the war; or it holds until the Mongols, after which the "
            "Mamluks drive the Order off the mainland. If it is broken, "
            "the Crusader magi may plan a strike at the caliph's mages in "
            "Baghdad (see the Hermetic Embassy's story seeds), and "
            "openly pro-Muslim covenants such as Aedes Veritatis are the "
            "first to be Renounced.",
        ),
        antagonist="The Crusader covenants, led by Foothold",
        moves=DATED,
        stages=[
            S(
                "The scramble for votes",
                year=1220,
                clues=(
                    "Rufus de Clary speaks for Foothold in every covenant "
                    "that will hear him; envoys from the Embassy and Domus "
                    "Pacis follow on his heels. Redcaps of Venti Rosa carry "
                    "letters, promises and threats. Each side asks what "
                    "Heliobus wants, and how the covenants of Urania and "
                    "al-Arama, far from the war, mean to vote."
                ),
                ignored=(
                    "The Crusaders arrive with their votes in hand and the "
                    "mediators with hopes."
                ),
                stopped=(
                    "The undecided covenants are won for renewal before the meeting."
                ),
                turned=(
                    "The troupe becomes the broker both sides must court, "
                    "and names its price."
                ),
            ),
            S(
                "The meeting at Domus Pacis",
                year=1221,
                season="Summer",
                clues=(
                    "Tents rise outside the khan and the gate shuts on "
                    "all but magi. Scipio takes the chair; the motion to "
                    "renew is heard, the speakers chosen, and Foothold's "
                    "charge against 'Umar may be brought the same week to "
                    "cost the counter-Crusaders their leader."
                ),
                ignored=(
                    "The vote goes the way the Crusade's news from Egypt "
                    "blows that season."
                ),
                stopped=(
                    "The Treaty is renewed for ten years from 1223. Give "
                    "the ruling a term ending at the meeting of 1228, the "
                    "last before the next lapse."
                ),
                turned=(
                    "The renewal passes with terms the troupe wrote, or "
                    "the Treaty is remade to bind more than the Order."
                ),
            ),
            S(
                "The Treaty lapses",
                year=1223,
                clues=(
                    "Without a renewal the Treaty ends with its term. "
                    "Crusader magi ride for Egypt; Aedes Veritatis's "
                    "allies come into the open; the caliph's mages and the "
                    "Ayyubids' prepare for war."
                ),
                ignored=(
                    "The Tribunal slides back into open war with the "
                    "Muslims' mages and with itself; the Embassy flees "
                    "Baghdad and the quaesitores lose their grip."
                ),
                stopped=(
                    "A new treaty is patched together before the fighting spreads."
                ),
                turned=(
                    "The troupe treats with the caliph's court on its own "
                    "account, and becomes the Order's new voice there."
                ),
            ),
        ],
    )


def _secret_war(levant: Levant) -> None:
    levant.world["threat_secret_war"] = levant.b.threat(
        "The Secret War on Foothold",
        summary=paragraphs(
            "Foothold, two quarrelsome French magi on a hill above Acre, "
            "leads the Crusader covenants and calls loudest for war; the "
            "quaesitores mark it as a danger to the peace and suspect it "
            "of crusading still, though nothing has been proved. Aedes "
            "Veritatis, the counter-Crusaders' fortress outside Damascus, "
            "is its declared enemy, and the two trouble the Embassy with "
            "politics at every turn.",
            "Foothold's magi care more for conquest than for their own "
            "house: its woods are half cleared, its labs poorly kept, and "
            "its French grogs have begun to grumble. It may take a sharp "
            "blow to wake them.",
        ),
        secrets=paragraphs(
            "Since 1193 'Umar, his sodales and their allies, Hermetic and "
            "mundane, have waged a hidden war on the Crusader covenants, "
            "Foothold above all, and the quaesitores have not caught them. "
            "Aedes Veritatis has spies in Domus Pacis who learn "
            "everything said there, and Foothold has its own there who "
            "hear what is said in council. Mages in the Ayyubids' service "
            "have hidden scrying devices in Foothold to warn of any "
            "attack.",
        ),
        antagonist="Sharaf al-Din 'Umar and the counter-Crusaders",
        position=1,
        stages=[
            S(
                "Mishaps at Foothold",
                at=1,
                clues=(
                    "Foothold's fishing boats are lost, its merchant "
                    "robbed, its grogs fall out among themselves; things "
                    "said in its hall are known in Damascus within days."
                ),
                ignored="Foothold weakens without knowing why.",
                stopped=(
                    "Foothold's magi find the scrying devices and see the "
                    "hand behind their troubles."
                ),
                turned=(
                    "The troupe learns who is spying on whom, and can sell "
                    "or keep the knowledge."
                ),
            ),
            S(
                "The grogs on the edge",
                at=2,
                clues=(
                    "Open mutterings among Foothold's men-at-arms; a "
                    "stranger among them who stirs every quarrel; "
                    "Guillaume trains harder and listens less."
                ),
                ignored="The turb rises against its masters.",
                stopped="Guillaume and Rufus deal with the trouble in time.",
                turned=("The troupe wins the turb's trust, and a door into Foothold."),
            ),
            S(
                "A blow in the night",
                at=3,
                clues=(
                    "Foothold is struck directly by unseen hands: walls "
                    "breached, a lab burned, a magus nearly killed. Rufus "
                    "carries the outrage to the quaesitores and names Aedes "
                    "Veritatis."
                ),
                ignored=(
                    "Foothold and its allies answer in kind, and the "
                    "Treaty's enemies point to the war as proof it is dead."
                ),
                stopped=(
                    "The quaesitores trace the attack, and Aedes "
                    "Veritatis's magi face charges."
                ),
                turned=(
                    "The troupe proves who struck, or hides it, and both "
                    "covenants owe it a debt."
                ),
            ),
            S(
                "Open war",
                at=4,
                clues=(
                    "The secret war breaks into the open, or the Treaty "
                    "lapses and there is no longer any need for secrecy."
                ),
                ignored=(
                    "Foothold falls, the first casualty of the new war, or "
                    "Aedes Veritatis is Renounced and besieged."
                ),
                stopped="The quaesitores impose a peace on both covenants.",
                turned=(
                    "The troupe ends the feud on terms both sides can "
                    "stomach, and earns both their thanks and their "
                    "suspicion."
                ),
            ),
        ],
    )


# -- the dormant stories --


def _umar(levant: Levant) -> None:
    levant.world["threat_umar"] = dormant(
        levant.b.threat(
            "'Umar's Double Loyalty",
            summary=paragraphs(
                "Sharaf al-Din 'Umar, a Jerbiton elementalist and devout "
                "Sunni, has led Aedes Veritatis since Hattin, a careful "
                "leader now though the counter-Crusade still rules him. "
                "To the people of Damascus his fortress is the home of a "
                "reclusive emir, a part he plays when he must. Foothold "
                "has learnt that early in his career he killed a Crusader "
                "magus who attacked him, with no one to witness that it "
                "was self-defence, and means to see him Renounced.",
            ),
            secrets=paragraphs(
                "'Umar is sworn to the Ayyubid sultans as well as to the "
                "Order, and serves them in secret; not even his own "
                "sodales know. If the Order finds out he will almost "
                "certainly be Renounced, but he is powerful and would call "
                "on the Muslims' own mages to shelter him, so a "
                "Renunciation need not mean his death.",
            ),
            antagonist="The sultans' claim on 'Umar, and Foothold's hunt for it",
            stages=[
                S(
                    "Errands for the sultan",
                    at=1,
                    clues=(
                        "'Umar is away when no one expects it; Ayyubid "
                        "officers in Damascus treat the 'emir' with odd "
                        "respect; news of crusader plans reaches the "
                        "sultans' courts uncommonly fast."
                    ),
                    ignored="His service runs deeper with every season.",
                    stopped="'Umar keeps the two loyalties apart, for now.",
                    turned=(
                        "The troupe learns the secret, and holds it over him "
                        "or keeps it for him."
                    ),
                ),
                S(
                    "A shadow from the past",
                    at=2,
                    clues=(
                        "Foothold asks the troupe to help bring 'Umar before "
                        "the quaesitores for the old killing, perhaps on the "
                        "word of the dead magus's ghost."
                    ),
                    ignored="The charge reaches the meeting of 1221.",
                    stopped="The charge fails for want of a witness.",
                    turned=(
                        "The troupe finds the truth of the fight, and with "
                        "it a hold over Foothold or over 'Umar."
                    ),
                ),
                S(
                    "Discovery",
                    at=3,
                    clues=(
                        "A quaesitor, Felix perhaps, or Scipio, comes upon "
                        "proof that 'Umar serves the Ayyubids. Amber and "
                        "Wardat learn it with everyone else."
                    ),
                    ignored="The quaesitores move to Renounce him.",
                    stopped="The proof is lost or never believed.",
                    turned=(
                        "The troupe persuades 'Umar to give up one master "
                        "before the Order chooses for him."
                    ),
                ),
                S(
                    "Renounced",
                    at=4,
                    clues=(
                        "'Umar is Renounced and flees to the Muslims' mages, "
                        "who take him in; Aedes Veritatis must choose between "
                        "its leader and the Order."
                    ),
                    ignored=(
                        "The counter-Crusaders lose their head and the Order "
                        "gains a powerful enemy who knows its secrets."
                    ),
                    stopped="He is taken before he reaches his allies.",
                    turned=(
                        "'Umar becomes the troupe's link to the Muslims' "
                        "mages, an outlaw and a go-between at once."
                    ),
                ),
            ],
        )
    )


def _esther(levant: Levant) -> None:
    levant.world["threat_esther"] = dormant(
        levant.b.threat(
            "Esther's Trade",
            summary=paragraphs(
                "Esther of Verditius, an Englishwoman at Domus Pacis since "
                "1197, has made the covenant a channel for goods between "
                "the Levant and the Roman Tribunal and its trade its "
                "chief income. In doing so she broke al-Arama's long hold "
                "on that trade, and its magi curse her name and would "
                "help anyone against her if they thought they could get "
                "away with it. She is not above a little mind magic to "
                "win a bargain.",
            ),
            secrets=paragraphs(
                "She grows rich on her own account by selling potent "
                "enchanted devices to Muslim and Latin nobles, which the "
                "Peripheral Code forbids as meddling. If the quaesitores "
                "learn of it, her sodales at Domus Pacis, the Praeco and a "
                "quaesitor among them, will suffer with her. She also "
                "draws Terram vis from a source of her own that no one "
                "else knows.",
            ),
            antagonist="Esther of Verditius",
            stages=[
                S(
                    "A shipment to Rome",
                    at=1,
                    clues=(
                        "Esther offers the troupe a handsome fee to carry a "
                        "sealed shipment from Domus Pacis to a covenant of "
                        "the Roman Tribunal, and will not say what is in it."
                    ),
                    ignored="Her trade grows, and with it her risks.",
                    stopped="The troupe refuses, and she finds other carriers.",
                    turned="The troupe learns what she trades, and to whom.",
                ),
                S(
                    "Devices in the wrong hands",
                    at=2,
                    clues=(
                        "An emir's guard turns a blade that should have cut "
                        "him; a Latin lord's tower is warded against fire. "
                        "Al-Arama's magi start asking where such things come "
                        "from."
                    ),
                    ignored="Al-Arama gathers its evidence.",
                    stopped="The devices are recovered quietly.",
                    turned=(
                        "The troupe takes over the trade, or uses the proof "
                        "to bind Esther to it."
                    ),
                ),
                S(
                    "The charge",
                    at=3,
                    clues=(
                        "Al-Arama lays the evidence before the quaesitores. "
                        "Felix, under the same roof, must investigate his own "
                        "sodalis; the Praeco's covenant is shamed."
                    ),
                    ignored=(
                        "Esther is convicted, Domus Pacis loses its income "
                        "and its standing as a neutral house, and the "
                        "mediators lose votes."
                    ),
                    stopped="The charge cannot be made to stick.",
                    turned=(
                        "The troupe brokers a settlement that gives al-Arama "
                        "back part of the trade."
                    ),
                ),
            ],
        )
    )


def _rufus(levant: Levant) -> None:
    levant.world["threat_rufus"] = dormant(
        levant.b.threat(
            "Rufus's Hoard",
            summary=paragraphs(
                "Rufus de Clary of Tytalus speaks for Foothold at the "
                "Tribunal. Handsome, cunning and ready to spend others to "
                "get his way, he can work magic without words or gestures "
                "and read the lips of people across a room, and he has "
                "learnt a great many things other magi would rather keep "
                "hidden. Several of them fear what happens if he ever "
                "gets proof. In debate he says the Crusade must go on for "
                "the Order's good.",
            ),
            secrets=paragraphs(
                "Rufus's zeal is fear, not faith. His parents were "
                "diabolists who tormented him as a child until his master "
                "Gilles de Clary rescued him, and he believes demons still "
                "hunt his soul. He gathers magical power, and means to "
                "take his share of the East's riches when the Order "
                "conquers it, to protect himself. His own past is the one "
                "secret he would kill to keep.",
            ),
            antagonist="Rufus de Clary",
            stages=[
                S(
                    "Sins of the father",
                    at=1,
                    clues=(
                        "A character's parens comes asking for help: Rufus "
                        "has proof of something that could see the parens "
                        "executed under the Code, and has begun to hint at "
                        "a price."
                    ),
                    ignored="The parens pays, and Rufus gains a servant.",
                    stopped="The proof is stolen or destroyed.",
                    turned=(
                        "The troupe finds where Rufus keeps his proofs, and "
                        "who else is in them."
                    ),
                ),
                S(
                    "Votes for silence",
                    at=2,
                    clues=(
                        "Magi who owe Rufus their silence begin to speak "
                        "against the Treaty, or stay away from the meeting "
                        "of 1221."
                    ),
                    ignored="Blackmail tips the renewal vote.",
                    stopped="His victims band together against him.",
                    turned="The troupe frees his victims, who owe it instead.",
                ),
                S(
                    "The diabolist's son",
                    at=3,
                    clues=(
                        "Someone digs into Rufus's childhood, or a demon "
                        "that knew his parents comes looking for him."
                    ),
                    ignored=(
                        "His past comes out, and the Order wonders whether "
                        "the son learnt his parents' trade."
                    ),
                    stopped="Rufus buries the past again, at a price.",
                    turned=(
                        "The troupe holds Rufus's own secret, and with it "
                        "Foothold's voice."
                    ),
                ),
            ],
        )
    )


def _amber(levant: Levant) -> None:
    levant.world["threat_amber"] = dormant(
        levant.b.threat(
            "Amber against Her House",
            summary=paragraphs(
                "Amber the Golden of Tremere, gold of skin, hair and eye "
                "since a laboratory accident in her apprenticeship, "
                "joined Aedes Veritatis in 1188 because she would not "
                "accept her House's support for the Crusades. That put "
                "her in disgrace with her House's elders, and only her "
                "parens Catullus, a senior magus of Coeris who treats her "
                "as his protegée, has kept her from being disciplined.",
                "Catullus is drifting towards Final Twilight, and Amber "
                "will soon need other friends. She is fiercely "
                "independent, and her bond with her cat familiar Luigi is "
                "the only tie she has ever welcomed.",
            ),
            antagonist="The elders of House Tremere",
            stages=[
                S(
                    "Catullus fades",
                    at=1,
                    clues=(
                        "Letters from Coeris grow vague and then stop; "
                        "Catullus still holds Amber's sigil, and Tremere "
                        "magi in the Levant ask after her loyalties."
                    ),
                    ignored="Amber's protector is gone before she has another.",
                    stopped="Catullus's last act secures her standing.",
                    turned=(
                        "The troupe becomes the ally Amber needs, at a time "
                        "she can repay it."
                    ),
                ),
                S(
                    "The House remembers",
                    at=2,
                    clues=(
                        "Tremere magi of the Levant, the young David at "
                        "Damietta among them, are told to bring Amber to "
                        "heel; she is summoned to answer for her defiance."
                    ),
                    ignored="She is ordered to leave Aedes Veritatis.",
                    stopped="Her House is persuaded to let her be.",
                    turned=(
                        "The troupe argues her case within the House's own customs."
                    ),
                ),
                S(
                    "Discipline",
                    at=3,
                    clues=(
                        "The House moves against Amber, through its own "
                        "law or through the Tribunal, and 'Umar must decide "
                        "whether to stand by his friend."
                    ),
                    ignored=(
                        "Amber is broken or driven out, and the "
                        "counter-Crusaders lose a maga."
                    ),
                    stopped="Amber defies them and keeps her place.",
                    turned=(
                        "Amber leaves House Tremere, and the troupe helps her "
                        "find a new House or a new covenant."
                    ),
                ),
            ],
        )
    )


def _aurora(levant: Levant) -> None:
    levant.world["threat_aurora"] = dormant(
        levant.b.threat(
            "Aurora's Twilight",
            summary=paragraphs(
                "Archmaga Aurora Borealis of Jerbiton, quaesitor and maker "
                "of the Treaty, is 102 and failing. A severe Twilight not "
                "long ago damaged her command of Animal, and she can feel "
                "her hold on the world loosening. She fears for the Levant "
                "if she goes soon, for the Embassy's only other magus, "
                "Spiral of Criamon, is enthusiastic, wise in the Sufis' "
                "eyes and almost impossible to understand, and no "
                "diplomat. She is looking hard for an answer.",
            ),
            secrets=paragraphs(
                "When she was eight, lightning struck Aurora, wakening her "
                "Gift, and showed her how she would end: a second bolt "
                "carrying her into Final Twilight.",
                "If the Embassy is still in Baghdad when the Mongols take "
                "the city in 1258 it falls with it, and Aurora, old and "
                "weak, is taken by the Mongol shamans (see her story "
                "seeds).",
            ),
            antagonist="Time, and the Twilight that is claiming Aurora",
            stages=[
                S(
                    "Storm clouds",
                    at=1,
                    clues=(
                        "Aurora is absent from her duties for days at a "
                        "time; servants speak of her talking with no one; "
                        "she flinches at every thunderstorm."
                    ),
                    ignored="Her work falls more and more to Spiral.",
                    stopped=(
                        "Her Twilight is slowed, perhaps by rare lore or a "
                        "Criamon's help."
                    ),
                    turned=(
                        "The troupe earns her trust as she weighs who should "
                        "follow her."
                    ),
                ),
                S(
                    "The search for a successor",
                    at=2,
                    clues=(
                        "Aurora sounds out magi who might keep the Treaty "
                        "after her; Magvillus sends its own candidates; "
                        "Foothold and Aedes Veritatis each want a friendly "
                        "face in Baghdad."
                    ),
                    ignored="No successor is ready.",
                    stopped="A trusted diplomat joins the Embassy in time.",
                    turned="A player magus is chosen.",
                ),
                S(
                    "The second bolt",
                    at=3,
                    clues=(
                        "Lightning strikes Aurora and she passes into Final "
                        "Twilight, or very nearly."
                    ),
                    ignored=(
                        "Spiral is left to deal with the caliph's court "
                        "alone, the Treaty loses its architect, and the "
                        "border with Thebes loses its guarantor."
                    ),
                    stopped="Her successor takes over without a gap.",
                    turned=(
                        "The troupe keeps the caliph's trust through the "
                        "change, and the Treaty's future rests on it."
                    ),
                ),
            ],
        )
    )


def _urbs_rubra(levant: Levant) -> None:
    levant.world["threat_urbs_rubra"] = dormant(
        levant.b.threat(
            "Fade and Wraith",
            summary=paragraphs(
                "Fade and Wraith of Criamon, husband and wife at Urbs "
                "Rubra in Petra, are the Tribunal's eldest magi, so by "
                "right Wraith should be Praeco. A people of jinn living in "
                "great stone blocks in the gorge before the covenant serve "
                "and guard them, and have grown so protective that they "
                "let no visitor through; some are too powerful for any "
                "magus to pass. No one has seen the pair for years, and "
                "in 1207 the quaesitores gave up and ruled Tau the eldest. "
                "Most magi think the jinn killed them long ago and keep up "
                "the pretence for reasons of their own.",
            ),
            secrets=paragraphs(
                "They live: senile, close to Final Twilight and heedless of "
                "the Tribunal's business, while the jinn shut out a world "
                "their masters can no longer face.",
            ),
            antagonist="The jinn of Urbs Rubra",
            realm="Magic",
            stages=[
                S(
                    "Who is Praeco?",
                    at=1,
                    clues=(
                        "Someone at the Tribunal, for a motive of their own, "
                        "argues that Tau's office belongs to Wraith if she "
                        "lives, and that someone should find out."
                    ),
                    ignored="The question lingers over every ruling Tau makes.",
                    stopped="The Tribunal confirms the ruling of 1207.",
                    turned="The troupe is sent to Petra to learn the truth.",
                ),
                S(
                    "The gorge",
                    at=2,
                    clues=(
                        "The jinn of the stone blocks bar the way, with "
                        "bargains, illusions and, if pressed, force."
                    ),
                    ignored="Visitors are turned back, or not seen again.",
                    stopped="The jinn are persuaded or bested.",
                    turned=(
                        "The troupe wins the jinn's trust by showing it "
                        "means their masters no harm."
                    ),
                ),
                S(
                    "The Red City's heirs",
                    at=3,
                    clues=(
                        "Fade and Wraith are found, or their bodies are. "
                        "Either way the oldest covenant of the Tribunal, its "
                        "lore and its jinn want new masters."
                    ),
                    ignored=(
                        "The jinn keep Urbs Rubra for themselves, and its "
                        "secrets with it."
                    ),
                    stopped=(
                        "The pair are left in peace and the Praeco's office settled."
                    ),
                    turned=(
                        "The troupe becomes Urbs Rubra's heirs, or Wraith, "
                        "lucid for a day, claims the Praeco's chair."
                    ),
                ),
            ],
        )
    )


def _heliobus(levant: Levant) -> None:
    levant.world["threat_heliobus"] = dormant(
        levant.b.threat(
            "Heliobus's Bloc",
            summary=paragraphs(
                "Heliobus Magister of Bonisagus was drawn to the hidden "
                "temple of Thoth and Anubis at Giza in 1177, when one of "
                "its twelve priests died, and brought the priesthood into "
                "House Ex Miscellanea. Since then he has seemed to care "
                "only for studying the rites of his fellow priests. But "
                "with one vote to each magus he commands twelve at the "
                "Tribunal, and the more political covenants are uneasy at "
                "what he could do with them, and at what powerful magic "
                "the temple may keep.",
            ),
            antagonist="Heliobus Magister and his twelve votes",
            stages=[
                S(
                    "Courted",
                    at=1,
                    clues=(
                        "Envoys of the Crusaders and of the mediators find "
                        "their way to Giza with gifts; Heliobus receives "
                        "them politely and promises nothing."
                    ),
                    ignored="He keeps his own counsel until the vote.",
                    stopped="He promises to stay away from the meeting.",
                    turned="The troupe learns what he really wants.",
                ),
                S(
                    "The price",
                    at=2,
                    clues=(
                        "Heliobus names a price for his votes: lore, vis, a "
                        "ruling in the priests' favour, or the troupe's help "
                        "with something hidden in the temple."
                    ),
                    ignored="The side that pays most gets the bloc.",
                    stopped="Neither side will pay, and he abstains.",
                    turned="The troupe pays, and buys a friend.",
                ),
                S(
                    "A power at the Tribunal",
                    at=3,
                    clues=(
                        "Heliobus finds he enjoys being the kingmaker, and "
                        "brings motions of his own."
                    ),
                    ignored=(
                        "Every meeting turns on Giza's twelve votes, and "
                        "covenants begin to question whether the priests "
                        "are true magi at all."
                    ),
                    stopped=(
                        "A challenge to the priests' membership checks "
                        "him, at the cost of bitterness."
                    ),
                    turned="The troupe and Heliobus lead the Tribunal together.",
                ),
            ],
        )
    )


def _theban_border(levant: Levant) -> None:
    levant.world["threat_theban_border"] = dormant(
        levant.b.threat(
            "The Theban Border",
            summary=paragraphs(
                "After 1204 Theban magi fled east with the Greek refugees "
                "and their Tribunal claimed more of Asia Minor for them; "
                "Aurora and quaesitores of both Tribunals settled it, "
                "Nicaea going to Thebes and Trebizond to the Levant. "
                "Thebes says its magi, driven out by the Latins, deserve "
                "more room; the Levant says the Thebans' failure to defend "
                "themselves and the Latins' doings are no affair of its. "
                "Both have agreed to differ, and it would take very little "
                "to set them at each other's throats.",
            ),
            antagonist="The Theban magi who want more of Asia Minor",
            stages=[
                S(
                    "Newcomers",
                    at=1,
                    clues=(
                        "A Theban magus settles in Trebizond's lands, "
                        "harvests vis there, or claims a site a Levantine "
                        "covenant had marked."
                    ),
                    ignored="Others follow.",
                    stopped="The newcomer is warned back over the border.",
                    turned="The troupe makes the newcomer a friend.",
                ),
                S(
                    "Words at the border",
                    at=2,
                    clues=(
                        "Grogs come to blows over a vis source; each "
                        "Tribunal sends a Redcap with a protest; Aurora is "
                        "too ill to ride north."
                    ),
                    ignored="Wizard War is declared across the border.",
                    stopped="Quaesitores of both Tribunals meet and calm it.",
                    turned=(
                        "The troupe settles the dispute and becomes the "
                        "border's go-between."
                    ),
                ),
                S(
                    "Two Tribunals at odds",
                    at=3,
                    clues=(
                        "Each Tribunal votes to defend its claim; the "
                        "matter is talked of for the next Grand Tribunal."
                    ),
                    ignored=(
                        "The Levant fights a second war on its northern "
                        "border while the Crusade burns in the south."
                    ),
                    stopped="A new settlement is agreed and sworn.",
                    turned=(
                        "The border is redrawn in the Levant's favour, or the troupe's."
                    ),
                ),
            ],
        )
    )


def _arash(levant: Levant) -> None:
    levant.world["threat_arash"] = dormant(
        levant.b.threat(
            "Arash and the Oath",
            summary=paragraphs(
                "Arash, once apprenticed to Rachel of Criamon, refused the "
                "Oath of Hermes at his induction in 1213 and swore the "
                "Treaty of Barcelona instead, the peace between the Order "
                "and the Kabbalists. Magi threatened him, and House "
                "Criamon carried him off to Baghdad, where he studies the "
                "Kabbalah with the city's rabbis and struggles to make "
                "his Hermetic and Kabbalistic gifts agree. A Gifted man "
                "trained in the Arts who is outside the Order troubles "
                "magi who read the Code strictly.",
            ),
            antagonist="Magi who would treat Arash as an unsworn wizard",
            stages=[
                S(
                    "Found",
                    at=1,
                    clues=(
                        "Word reaches the Tribunal that Rachel's lost "
                        "apprentice lives in Baghdad's Jewish quarter, close "
                        "to the Embassy. Felix of Guernicus, who watches "
                        "Criamon's dealings with the Kabbalists, is asked "
                        "what he knows."
                    ),
                    ignored="The rumour spreads among the Crusader magi.",
                    stopped="House Criamon quietly moves him again.",
                    turned="The troupe reaches him first.",
                ),
                S(
                    "Join or die",
                    at=2,
                    clues=(
                        "Magi who threatened him in 1213 come to Baghdad, "
                        "and the rabbis who teach him close ranks. The "
                        "Treaty of Barcelona and the Embassy's peace are "
                        "both in the way."
                    ),
                    ignored=(
                        "Arash is killed or driven out, and the Kabbalists "
                        "ask whether the Order keeps its treaties."
                    ),
                    stopped=(
                        "The quaesitores rule that his oath under the "
                        "Treaty of Barcelona protects him."
                    ),
                    turned=(
                        "Arash finds a way to reconcile his two magics, and "
                        "the troupe gains his friendship and his insight."
                    ),
                ),
            ],
        )
    )


def _true_cross(levant: Levant) -> None:
    levant.world["threat_true_cross"] = dormant(
        levant.b.threat(
            "The True Cross's Call",
            summary=paragraphs(
                "Two young magi, David of Tremere and Xydas of Bonisagus, "
                "founded the True Cross in Damietta after the city fell to "
                "the crusaders in 1219. With a small turb and friends in "
                "the garrison they are stripping a Muslim sorcerer's estate "
                "of its magical relics and making the port a channel for "
                "the East's treasures to the magi of Europe. They have "
                "called on the Order for magi to join them, but few will "
                "come until Damietta is safer.",
            ),
            secrets=paragraphs(
                "If history runs its course the crusaders lose Damietta in "
                "1221, and the book suggests the loss of the True Cross may "
                "be what finally breaks the Treaty.",
            ),
            antagonist="The Muslim armies closing on Damietta",
            stages=[
                S(
                    "The call",
                    at=1,
                    clues=(
                        "A Redcap brings David's letter: magi wanted at "
                        "Damietta, rich pickings promised, the dead "
                        "sorcerer's house half searched."
                    ),
                    ignored="No one answers, and the two stay alone.",
                    stopped="The covenant is persuaded to leave while it can.",
                    turned=(
                        "The troupe answers, and has the first choice of the "
                        "sorcerer's treasures."
                    ),
                ),
                S(
                    "The sorcerer's estate",
                    at=2,
                    clues=(
                        "Something in the estate does not want to be "
                        "carried off, and the Muslim mages who knew its "
                        "master want it back."
                    ),
                    ignored="The relics, and their curses, reach Europe.",
                    stopped="The dangerous pieces are sealed away.",
                    turned="The troupe returns them, and wins Muslim friends.",
                ),
                S(
                    "Damietta falls again",
                    at=3,
                    clues=(
                        "The Crusade founders in the Nile flood, the truce "
                        "gives Damietta back, and the True Cross must flee "
                        "or be taken with the city."
                    ),
                    ignored=(
                        "The covenant is destroyed with its magi, and the "
                        "Crusaders cry for vengeance."
                    ),
                    stopped="The magi escape with what they can carry.",
                    turned=(
                        "The troupe gets them out quietly, before anyone "
                        "blames the Order or the Muslims."
                    ),
                ),
            ],
        )
    )


def _pyramids(levant: Levant) -> None:
    levant.world["threat_pyramids"] = dormant(
        levant.b.threat(
            "The Opening of the Pyramids",
            summary=paragraphs(
                "At Giza, Ruth of Bonisagus and Pariah of Criamon live "
                "only for the pyramids. They have bent the wandering "
                "spirits of the place to their will, set them to teach "
                "the monuments' history and to keep strangers off, and "
                "are working to read the hieroglyphs in the burial "
                "chamber of the greatest pyramid and to find a way into "
                "the others, hoping for the ancients' hidden wisdom and a "
                "way past the limits of Hermetic magic. Other magi find "
                "their single-mindedness disturbing; nobody knows how far "
                "they will go.",
            ),
            secrets=paragraphs(
                "No one knows what might come out if one of the sealed "
                "pyramids is opened; the storyguide decides.",
            ),
            antagonist="Ruth and Pariah",
            realm="Magic",
            stages=[
                S(
                    "Restless spirits",
                    at=1,
                    clues=(
                        "Travellers near the pyramids are driven off by "
                        "terrors; local guides refuse to go near; the two "
                        "magi buy every Egyptian text they can find."
                    ),
                    ignored="The work goes on unwatched.",
                    stopped="Others persuade them to go carefully.",
                    turned="The troupe joins the work, and shares the finds.",
                ),
                S(
                    "The inscription read",
                    at=2,
                    clues=(
                        "Ruth and Pariah decipher enough of the burial "
                        "chamber's writing to learn how a sealed pyramid "
                        "might be opened, and what was shut inside."
                    ),
                    ignored="They begin the opening.",
                    stopped="The knowledge is kept from them.",
                    turned=("The troupe understands the warning in the writing first."),
                ),
                S(
                    "A pyramid opened",
                    at=3,
                    clues=(
                        "A sealed pyramid is breached. The priests of the "
                        "hidden temple, if the storyguide uses them, stir "
                        "in alarm."
                    ),
                    ignored="Whatever was sealed inside walks free.",
                    stopped="The breach is closed again in time.",
                    turned=(
                        "The troupe claims the ancients' wisdom, and the "
                        "dangers that come with it."
                    ),
                ),
            ],
        )
    )


# -- tying the stories to the other parts' records --

#: A record to look for: its kind ("covenant", "magus", "creature",
#: "place" for places, "world" for the other neighbours, or "name" for a
#: neighbour by name only), its key in that dict, and names it may go by.
Target = tuple[str, ...]


def _key(name: str) -> str:
    """A name compared loosely: case, accents, hyphens, apostrophes and a
    leading 'The' set aside."""
    out = unicodedata.normalize("NFKD", name.casefold().strip())
    out = "".join(c for c in out if not unicodedata.combining(c))
    out = out.removeprefix("the ")
    for mark in ("-", "_", "'", "’", "‘"):
        out = out.replace(mark, " " if mark in "-_" else "")
    return " ".join(out.split())


def _named(records: list[Any], names: tuple[str, ...]) -> Any | None:
    """The first record whose name is one of `names`, or failing that
    whose name starts with one of them as a whole word ("Amirat al-Jabal"
    finds "Amirat al-Jabal, the Princess of the Mountain"), loosely
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


#: The records east.py shares with other packs: their text is never
#: changed here, so a seed that hangs on one goes to the region instead.
SHARED = frozenset(
    {
        "iraq",
        "georgia",
        "greater_armenia",
        "jinnistan",
        "qaf",
        "harut_and_marut",
        "order",
        "stone",
        "river",
        "jinn",
        "baghdad",
        "mosul",
        "caliph",
        "al_kamil",
        "al_aziz",
        "lord_of_mosul",
        "king_of_georgia",
        "nizaris",
        "imam",
        "sultan_of_rum",
        "emperor_of_trebizond",
        "fifth_crusade",
        "mongol_conquest",
        "al_khidr",
    }
)


def _lookup(levant: Levant, target: Target) -> Any | None:
    """The record a target names, or None when no part has made it."""
    kind, key, *names = target
    saga = levant.b.saga
    if kind == "covenant":
        return levant.covenants.get(key) or _named(saga.covenants, tuple(names))
    if kind == "magus":
        return levant.magi.get(key) or _named(saga.characters, tuple(names))
    if kind == "creature":
        return levant.creatures.get(key) or _named(saga.creatures, tuple(names))
    if kind == "place":
        found = levant.places.get(key)
    elif kind == "world":
        found = levant.world.get(key)
    else:
        found = None
    return found or _named(saga.neighbours, tuple(names))


def _shared_ids(levant: Levant) -> set[str]:
    """The ids of the shared records this pack holds."""
    return {found.id for key in SHARED if (found := levant.find(key)) is not None}


#: Each covenant's key with its name, as the covenant parts make them.
COVENANTS: dict[str, Target] = {
    "aedes_veritatis": ("covenant", "aedes_veritatis", "Aedes Veritatis"),
    "domus_pacis": ("covenant", "domus_pacis", "Domus Pacis"),
    "foothold": ("covenant", "foothold", "Foothold"),
    "embassy": ("covenant", "embassy", "The Hermetic Embassy"),
    "urbs_rubra": ("covenant", "urbs_rubra", "Urbs Rubra"),
    "urania": ("covenant", "urania", "Urania"),
    "para_belli": ("covenant", "para_belli", "Para Belli"),
    "al_arama": ("covenant", "al_arama", "Al-Arama"),
    "venti_rosa": ("covenant", "venti_rosa", "Venti Rosa"),
    "pyramids_i": ("covenant", "pyramids_i", "The Pyramids (I)"),
    "pyramids_ii": ("covenant", "pyramids_ii", "The Pyramids (II)"),
    "true_cross": ("covenant", "true_cross", "The True Cross"),
}


def _m(key: str, *names: str) -> Target:
    return ("magus", key, *names)


def _p(key: str, *names: str) -> Target:
    return ("place", key, *names)


def _w(key: str, *names: str) -> Target:
    return ("world", key, *names)


C = COVENANTS

#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target, note).
LINKS: tuple[tuple[str, str, Target, str], ...] = (
    ("threat_treaty", "covenants", C["embassy"], "Brings the renewal"),
    ("threat_treaty", "covenants", C["domus_pacis"], "Hosts the vote; for renewal"),
    ("threat_treaty", "covenants", C["aedes_veritatis"], "For renewal"),
    ("threat_treaty", "covenants", C["foothold"], "Leads the vote against"),
    ("threat_treaty", "covenants", C["para_belli"], "Against renewal"),
    ("threat_treaty", "covenants", C["true_cross"], "Against renewal"),
    ("threat_treaty", "covenants", C["pyramids_ii"], "Twelve votes"),
    ("threat_treaty", "characters", _m("aurora", "Aurora Borealis"), "Its maker"),
    ("threat_treaty", "characters", _m("scipio", "Scipio"), "In the chair"),
    ("threat_treaty", "characters", _m("tau", "Tau"), "The Praeco, the host"),
    ("threat_treaty", "characters", _m("rufus", "Rufus de Clary"), "Speaks against"),
    ("threat_treaty", "characters", _m("heliobus", "Heliobus"), "Holds twelve votes"),
    ("threat_treaty", "places", _w("caliph"), "The other party"),
    ("threat_treaty", "places", _w("fifth_crusade"), "Strains the peace"),
    ("threat_treaty", "places", _w("islamic_tradition"), "Suspected of meddling"),
    ("threat_secret_war", "covenants", C["aedes_veritatis"], "Wages it"),
    ("threat_secret_war", "covenants", C["foothold"], "Its target"),
    ("threat_secret_war", "covenants", C["domus_pacis"], "Full of both sides' spies"),
    ("threat_secret_war", "covenants", C["embassy"], "Troubled by both"),
    ("threat_secret_war", "characters", _m("umar", "Sharaf al-Din 'Umar"), "Leads it"),
    ("threat_secret_war", "characters", _m("amber", "Amber"), "Fights beside 'Umar"),
    ("threat_secret_war", "characters", _m("wardat", "Wardat al-Quds"), "Fights too"),
    ("threat_secret_war", "characters", _m("guillaume", "Guillaume"), "Its target"),
    ("threat_secret_war", "characters", _m("rufus", "Rufus"), "Its target"),
    ("threat_umar", "characters", _m("umar", "Sharaf al-Din 'Umar"), "The servant"),
    ("threat_umar", "characters", _m("amber", "Amber"), "His friend, unknowing"),
    ("threat_umar", "characters", _m("wardat", "Wardat al-Quds"), "His sodalis"),
    ("threat_umar", "characters", _m("felix", "Felix"), "A quaesitor who may find out"),
    ("threat_umar", "covenants", C["aedes_veritatis"], "His covenant"),
    ("threat_umar", "covenants", C["foothold"], "Wants him Renounced"),
    ("threat_umar", "places", _w("al_kamil"), "One of the sultans he serves"),
    ("threat_umar", "places", _w("al_muazzam"), "His sultan at Damascus"),
    ("threat_umar", "places", _w("damascus", "Damascus"), "Where he plays the emir"),
    ("threat_esther", "characters", _m("esther", "Esther"), "The trader"),
    ("threat_esther", "characters", _m("felix", "Felix"), "Quaesitor under her roof"),
    ("threat_esther", "characters", _m("tau", "Tau"), "Her covenant's head"),
    ("threat_esther", "characters", _m("hildegard", "Hildegard"), "Al-Arama's"),
    ("threat_esther", "covenants", C["domus_pacis"], "Her covenant"),
    ("threat_esther", "covenants", C["al_arama"], "Her rival in trade"),
    ("threat_rufus", "characters", _m("rufus", "Rufus de Clary"), "The blackmailer"),
    ("threat_rufus", "characters", _m("guillaume", "Guillaume"), "His sodalis"),
    ("threat_rufus", "covenants", C["foothold"], "His covenant"),
    ("threat_amber", "characters", _m("amber", "Amber"), "The rebel"),
    ("threat_amber", "characters", _m("umar", "Sharaf al-Din 'Umar"), "Her friend"),
    ("threat_amber", "characters", _m("david", "David"), "A Tremere of the Levant"),
    ("threat_amber", "characters", _m("xerxes", "Xerxes"), "A Tremere of the Levant"),
    ("threat_amber", "creatures", ("creature", "luigi", "Luigi"), "Her familiar"),
    ("threat_amber", "covenants", C["aedes_veritatis"], "Her covenant"),
    ("threat_aurora", "characters", _m("aurora", "Aurora Borealis"), "Failing"),
    ("threat_aurora", "characters", _m("spiral", "Spiral"), "Her unfit heir"),
    ("threat_aurora", "covenants", C["embassy"], "Her covenant"),
    ("threat_aurora", "covenants", C["domus_pacis"], "Her first covenant"),
    ("threat_aurora", "places", _w("caliph"), "Her counterpart"),
    ("threat_urbs_rubra", "characters", _m("fade", "Fade"), "The eldest"),
    ("threat_urbs_rubra", "characters", _m("wraith", "Wraith"), "Praeco by right"),
    ("threat_urbs_rubra", "characters", _m("tau", "Tau"), "Praeco by ruling"),
    ("threat_urbs_rubra", "covenants", C["urbs_rubra"], "Shut by its jinn"),
    ("threat_urbs_rubra", "places", _p("petra", "Petra"), "The Red City"),
    ("threat_heliobus", "characters", _m("heliobus", "Heliobus"), "The kingmaker"),
    ("threat_heliobus", "covenants", C["pyramids_ii"], "His twelve votes"),
    ("threat_heliobus", "places", _p("giza", "Giza"), "The hidden temple"),
    ("threat_theban_border", "characters", _m("aurora", "Aurora"), "Made the peace"),
    ("threat_theban_border", "places", _p("asia_minor", "Asia Minor"), "The border"),
    ("threat_theban_border", "places", _w("emperor_of_trebizond"), "The Levant's side"),
    ("threat_theban_border", "places", _w("sultan_of_rum"), "Rules between"),
    ("threat_arash", "characters", _m("arash", "Arash"), "Outside the Order"),
    ("threat_arash", "characters", _m("felix", "Felix"), "Watches the Kabbalists"),
    ("threat_arash", "covenants", C["embassy"], "His neighbour in Baghdad"),
    ("threat_arash", "places", _w("baghdad"), "Where he hides"),
    ("threat_true_cross", "characters", _m("david", "David"), "Sends the call"),
    ("threat_true_cross", "characters", _m("xydas", "Xydas"), "His sodalis"),
    ("threat_true_cross", "covenants", C["true_cross"], "The covenant"),
    ("threat_true_cross", "places", _w("fifth_crusade"), "Its fortunes"),
    ("threat_true_cross", "places", _w("damietta", "Damietta"), "Its city"),
    ("threat_pyramids", "characters", _m("ruth", "Ruth"), "Would open them"),
    ("threat_pyramids", "characters", _m("pariah", "Pariah"), "Would open them"),
    (
        "threat_pyramids",
        "characters",
        _m("heliobus", "Heliobus"),
        "Below, in the regio",
    ),
    ("threat_pyramids", "covenants", C["pyramids_i"], "The diggers"),
    ("threat_pyramids", "covenants", C["pyramids_ii"], "The hidden temple"),
    ("threat_pyramids", "places", _p("giza", "Giza"), "The pyramids"),
)

#: Each story's place: the first target found, a covenant giving its own
#: site.
PLACES: dict[str, tuple[Target, ...]] = {
    "threat_treaty": (C["domus_pacis"], _p("jerusalem_kingdom"), _p("levant")),
    "threat_secret_war": (C["foothold"], _p("jerusalem_kingdom"), _p("levant")),
    "threat_umar": (C["aedes_veritatis"], _w("damascus"), _p("syria")),
    "threat_esther": (C["domus_pacis"], _p("jerusalem_kingdom")),
    "threat_rufus": (C["foothold"], _p("jerusalem_kingdom")),
    "threat_amber": (C["aedes_veritatis"], _p("syria")),
    "threat_aurora": (C["embassy"], _w("baghdad")),
    "threat_urbs_rubra": (C["urbs_rubra"], _p("petra", "Petra")),
    "threat_heliobus": (C["pyramids_ii"], _p("giza", "Giza"), _p("egypt")),
    "threat_theban_border": (_p("asia_minor", "Asia Minor"), _p("levant")),
    "threat_arash": (_w("baghdad"), _p("iraq")),
    "threat_true_cross": (C["true_cross"], _w("damietta", "Damietta"), _p("egypt")),
    "threat_pyramids": (C["pyramids_i"], _p("giza", "Giza"), _p("egypt")),
}

#: The book's story seeds (L23): (the record it hangs on and fallbacks,
#: title, the seed, True if it belongs in the record's secrets). A seed
#: goes on the first target found that is not a shared record; the
#: region is the last fallback.
SEEDS: tuple[tuple[tuple[Target, ...], str, str, bool], ...] = (
    (
        (_p("levant"),),
        "Unusual Neighbours",
        "in some remote corner jinn and people may still share villages and "
        "markets as in Harun's day, and the characters find themselves with "
        "very strange neighbours, perhaps easier to live beside than the "
        "Latins and Muslims next door.",
        False,
    ),
    (
        (_p("egypt", "Egypt"), _p("levant")),
        "Berber Wizards",
        "a new leader rallies the Berber tribes and their wizards, whose "
        "unknown magic once won Egypt for the Fatimids, and marches east; "
        "if he comes as the Mongols do, the Levant's magi are caught "
        "between the two.",
        False,
    ),
    (
        (_w("islamic_tradition", "The Islamic Tradition"), _p("levant")),
        "A Muslim Hermetic Tradition?",
        "the characters meet a Muslim mage whose magic looks Hermetic and "
        "whose line runs back to Harun al-Rashid's court; do they bring "
        "him and his fellows into the Order, perhaps as a new House, learn "
        "what their magic has become, and face the Crusader magi's anger?",
        False,
    ),
    (
        (_w("antioch_city", "Antioch"), _p("antioch"), _p("levant")),
        "Quest for the Lance",
        "signs point the characters to where the Holy Lance, lost in Asia "
        "Minor in 1101, now rests; the search may take years and test "
        "whether they are worthy of it, within as much as without.",
        False,
    ),
    (
        (_w("acre", "Acre"), _p("jerusalem_kingdom")),
        "The Seedier Side of Acre",
        "a thief takes something from the covenant and sells it in Acre, "
        "and the characters must follow it from hand to hand through the "
        "city's underworld, where the Divine aura hampers their magic and "
        "the buyer may open a further story.",
        False,
    ),
    (
        (_p("cyprus", "Cyprus"),),
        "A Cypriot Covenant?",
        "if no Levantine magi have settled Cyprus yet, its growing trade "
        "makes it a fine site for a new covenant, Verditius and Jerbiton "
        "magi above all, provided they never alarm the wary Lusignans.",
        False,
    ),
    (
        (_p("lesser_armenia", "Lesser Armenia"), _p("levant")),
        "Illuminating Manuscripts",
        "illuminated books from Armenia glow in the dark, and their "
        "pictures turn out to be enchanted to some unknown end: the work "
        "of a powerful mage, or of an illuminator with the Gift who could "
        "be an apprentice?",
        False,
    ),
    (
        (_p("colchis", "Colchis"), _p("levant")),
        "In Jason's Footsteps",
        "rumour speaks of a new Golden Fleece in western Georgia, old "
        "Colchis; the Argonauts' own come home, or some other prize under "
        "that name? The way there may hold dangers like Jason's.",
        False,
    ),
    (
        (C["urania"], _p("alan_lands", "The Alan Lands")),
        "Fact-finding Mission",
        "when the Mongols overrun the Alan lands in 1238, their shamans "
        "destroy Urania without a survivor and hide what they did from "
        "scrying; the Tribunal sends the characters to slip in, learn what "
        "happened and slip out again.",
        False,
    ),
    (
        (_w("cairo", "Cairo"), _p("egypt")),
        "Under Pressure",
        "al-Kamil's agents ask the characters' help against the crusaders, "
        "or against al-Mu'azzam of Damascus; the Code forbids it, the "
        "sultan can reward or punish lavishly, and the other side may come "
        "asking too.",
        False,
    ),
    (
        (_w("damascus", "Damascus"), _p("syria")),
        "Scholarly Attention",
        "learned men of Damascus, fascinated by Hermetic magic and its "
        "classical roots, court an invitation to the covenant and, once "
        "there, will not stop asking questions; the characters must send "
        "them home without offending the city's scholars.",
        False,
    ),
    (
        (
            ("name", "", "The Tower of the Serpents", "Tower of the Serpents"),
            _w("aleppo", "Aleppo"),
            _p("syria"),
        ),
        "A Tempting Prize",
        "the talisman in Aleppo's Tower of the Serpents keeps every snake's "
        "venom from harming anyone in the city; it would grace a covenant, "
        "but it is hard to steal and harder to keep once word spreads, and "
        "it may not work anywhere else.",
        False,
    ),
    (
        (C["embassy"], _p("levant")),
        "A Strike at the Heart",
        "a meeting of the Tribunal throws out the Treaty and plans to "
        "cripple the caliph's mages by killing their leaders in Baghdad; "
        "the Crusader magi press the characters to take part and suspect "
        "any who hesitate, and pro-Muslim covenants such as Aedes Veritatis "
        "are among the first to be Renounced.",
        False,
    ),
    (
        (_w("konya", "Konya"), _p("asia_minor")),
        "Preventative Measures",
        "a Criamon seer who has foreseen that the Sufi Jalal al-Din Rumi "
        "will settle in Konya in 1226 and found the Mevlevi order sets out "
        "to shape it; the quaesitores send the characters, whose covenant "
        "lies nearest his road, to stop him before he sets the Order "
        "against men and perhaps God.",
        False,
    ),
    (
        (_p("levant"),),
        "Braving the Elements",
        "few covenants dare Greater Armenia's eight-month winters, so its "
        "magical riches lie waiting; the characters settle there and the "
        "weather itself seems to fight them, perhaps by nature, perhaps at "
        "the bidding of a powerful magus who resents newcomers.",
        False,
    ),
    (
        (C["foothold"], C["para_belli"], _p("levant")),
        "A Hermetic Military Order?",
        "zealous magi, chafing at the peace with the Muslims, mean to found "
        "a military order of their own in the hope that papal blessing "
        "will shield them from the quaesitores, and camp on the "
        "characters' doorstep demanding they join.",
        False,
    ),
    (
        (
            ("name", "", "The Knights Templar", "Knights Templar", "The Templars"),
            _p("jerusalem_kingdom"),
        ),
        "Templar Sorcerers?",
        "the troupe may make the Templars sorcerers or diabolists with real "
        "power, a rival to the Order across Europe and the Levant; if their "
        "strength is Infernal, Hermetic magic cannot see it, and companions "
        "and grogs must trace it by mundane means.",
        True,
    ),
    (
        (_p("egypt", "Egypt"), _p("levant")),
        "Fatimid Survivors?",
        "a Fatimid who escaped Salah al-Din's purge asks the characters to "
        "help him back to the caliph's throne, with powerful friends, rich "
        "rewards and perhaps an imam's powers, even the right to call the "
        "lesser jihad on those who refuse.",
        False,
    ),
    (
        (
            _w("syrian_nizaris", "The Syrian Nizaris"),
            _p("masyaf", "Masyaf"),
            _p("syria"),
        ),
        "Stolen Property",
        "the characters chance on a shipment of Assassins' daggers bound "
        "from Syria to Persia and only learn what they are in the lab; the "
        "Nizaris want them back, and others, the Order among them, want "
        "them too.",
        False,
    ),
    (
        (_p("levant"),),
        "Seeking Refuge",
        "a badly wounded jinni begs shelter at the covenant and offers his "
        "powers in return, not knowing that his enemies, perhaps magi or "
        "crusaders, are close behind.",
        False,
    ),
    (
        (("creature", "amirat_al_jabal", "Amirat al-Jabal"), _p("levant")),
        "Oops!",
        "the characters hurt one of the jinn under Amirat al-Jabal's "
        "protection by mistake; she hunts them for revenge or payment, and "
        "talking is far safer than fighting her.",
        False,
    ),
    (
        (("creature", "al_qatil", "Al-Qatil"), _p("levant")),
        "A Rogue Element",
        "al-Qatil takes the shape of a common soldier, joins the covenant's "
        "grogs and stirs them towards mutiny, and the magi must find the "
        "cause before it is too late.",
        False,
    ),
    (
        (("creature", "naddaha", "Naddaha", "The Naddaha"), _p("levant")),
        "Missing Persons",
        "a village qadi asks the covenant to find villagers who vanished at "
        "a riverside well; a naddaha has made it its home, and once it is "
        "dealt with the qadi wants the bodies it threw in the river, now "
        "far downstream.",
        False,
    ),
    (
        (_w("cairo", "Cairo"), _p("egypt")),
        "Recovery Mission",
        "the relic of the True Cross, lost at Hattin, must be won back: "
        "the characters must learn where the Ayyubids keep it, perhaps in the sultan's "
        "own palace, steal it from its guards and wards, and leave no trace "
        "that leads to the Order.",
        False,
    ),
    (
        (("creature", "abd_al_misbah", "'Abd al-Misbah", "Abd al-Misbah"),),
        "Set Me Free!",
        "the lamp of A'la al-Din comes to the characters, and 'Abd al-Misbah "
        "tells them the hard terms of his freedom; he would make a fine "
        "friend if they meet them, and a wretched servant until they do.",
        False,
    ),
    (
        (_m("umar", "Sharaf al-Din 'Umar"), C["aedes_veritatis"]),
        "A Shadow from the Past",
        "Foothold, having learnt of the Crusader magus 'Umar killed with "
        "no one to witness the self-defence, perhaps from the dead man's "
        "ghost, asks the characters to help bring him to trial and have "
        "him Renounced: the letter of the law, or a plain political move?",
        False,
    ),
    (
        (_m("esther", "Esther"), C["domus_pacis"]),
        "The Italian Job",
        "Esther offers the characters a rich reward to carry a shipment "
        "from Domus Pacis to a covenant of the Roman Tribunal, and will not "
        "say what is in it.",
        False,
    ),
    (
        (_m("rufus", "Rufus de Clary"), C["foothold"]),
        "Sins of the Father",
        "Rufus holds proof of a secret that could have a character's parens "
        "executed under the Code, and the parens asks for help: persuade "
        "him, steal the evidence, or something else?",
        False,
    ),
    (
        (_m("aurora", "Aurora Borealis"), C["embassy"]),
        "Rescue Mission",
        "if the Embassy is still in Baghdad when the Mongols take it in "
        "1258, Aurora is taken by their shamans; Magvillus, afraid of what "
        "she might reveal, sends the characters to free her, or kill her if "
        "they cannot, and to answer for it afterwards.",
        False,
    ),
    (
        (_m("aurora", "Aurora Borealis"), C["embassy"]),
        "The Archmage's Challenge",
        "Aurora won her title by answering a riddle set by Emerich of "
        "Criamon, archmage of the Rhine; any magus may now challenge her "
        "for it, and what she sets is the storyguide's choice, a story or "
        "the saga's leitmotif.",
        False,
    ),
    (
        (_w("jerusalem", "Jerusalem"), _p("jerusalem_kingdom")),
        "The Ghosts of Jerusalem",
        "a character caught out of doors on the night of 15 July, when the "
        "dead of 1099 fill the streets, is driven mad, and the ghosts will "
        "give back the wits they took only when they are laid to rest.",
        False,
    ),
)

STORIES = paragraphs(
    "Stories. The book frames the saga as the Treaty of Baghdad under "
    "strain: the Crusade at Damietta has the Crusader magi calling for "
    "war, the counter-Crusaders fight them in secret, and the mediators "
    "struggle to keep the peace. Under way in 1220 are the vote on "
    "renewing the Treaty at the meeting of 1221 and Aedes Veritatis's "
    "secret war on Foothold, with the Fifth Crusade and the Mongol "
    "Conquest beyond the Order. Others wait for the storyguide: 'Umar's "
    "double loyalty, Esther's trade, Rufus's hoard, Amber against her "
    "House, Aurora's Twilight and the Embassy's succession, Fade and "
    "Wraith, Heliobus's bloc, the Theban border, Arash, the True Cross's "
    "call and the opening of the pyramids. The book's smaller story seeds "
    "sit on the places, covenants, magi and creatures they use.",
)


def _add(record: Any, attr: str, more: str) -> None:
    if attr == "secrets":
        record.secrets = as_secrets(paragraphs(secret_words(record.secrets), more))
        return
    setattr(record, attr, paragraphs(getattr(record, attr) or "", more))


def finish(levant: Levant) -> None:
    world = levant.world
    for key, kind, target, note in LINKS:
        found = _lookup(levant, target)
        if found is not None:
            Builder.link(world[key], kind, found, note)
    for key, targets in PLACES.items():
        for target in targets:
            found = _lookup(levant, target)
            place_id = None
            if found is not None:
                place_id = found.place_id if target[0] == "covenant" else found.id
            if place_id:
                world[key].place_id = place_id
                break
    crusade, damietta = world.get("fifth_crusade"), world.get("damietta")
    if crusade is not None and damietta is not None and crusade.place_id is None:
        crusade.place_id = damietta.id
    _seeds(levant)
    if levant.tribunal is not None:
        _add(levant.tribunal, "summary", STORIES)


def _seeds(levant: Levant) -> None:
    """Each seed on the first of its targets that exists and is the
    pack's own, as one line under a "Story seeds" heading; a seed for
    the storyguide alone goes under the heading in the record's secrets."""
    region = levant.places.get("levant")
    shared = _shared_ids(levant)
    lines: dict[tuple[int, str], tuple[Any, list[str]]] = {}
    for targets, title, text, hidden in SEEDS:
        record = None
        for target in targets:
            found = _lookup(levant, target)
            if found is not None and found.id not in shared:
                record = found
                break
        record = record or region
        if record is None:
            continue
        if hidden:
            attr = "secrets"
        elif isinstance(record, (Covenant, Creature)):
            attr = "notes"
        else:
            attr = "summary"  # a neighbour or a character
        entry = lines.setdefault((id(record), attr), (record, []))
        entry[1].append(f"{title}: {text}")
    for (_, attr), (record, seeds) in lines.items():
        _add(record, attr, "Story seeds:\n" + "\n".join(seeds))
