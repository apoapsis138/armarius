"""The Theban Tribunal itself: the record and its summary (the polity,
its phylai, the Council of Magistrates and the meeting on Delos), the
Peripheral Code and the Tribunal's customs, the docket for the meeting
of 1221, the twelve ruined or lost covenants as ruined places, and the
Redcaps described only with the polity (build); then the Praeco, the
Council of Magistrates, every covenant's phyle, the tokens and shards of
each named magus, each ruin's region and its ties to living covenants
(finish, once the parts that make the regions, covenants and magi have
built); and last the Redcaps' generated stats (stats)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...tribunal_packages import theban as package
from ...tribunal_packages.theban import THEBAN
from ..builder import Secrets, paragraphs, titled
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character, Covenant, Saga, Tribunal
    from . import Theban

NAME = "The Theban Tribunal"
MERCERE = "house_mercere"
GREEK = "Greek"

SUMMARY = paragraphs(
    "The Tribunal of the Greek-speaking lands that were the Roman Empire "
    "of the East until the crusaders took Constantinople in 1204: mainland "
    "Greece and the Morea, Macedonia and Thrace, the Aegean islands and "
    "Candia, and the western coasts of Asia Minor, with the half-ruined "
    "Queen of Cities at the crossing between the Aegean and the Black Sea. "
    "The sea binds it together more than in any other Tribunal: one "
    "covenant lives aboard ships, one under the waves, and most of the "
    "rest within a short sail of the coast. It holds about a hundred magi. "
    "Old gods and spirits crowd the land, and vis is so plentiful that "
    "its magi treat it as food, needful but not money; freed of the "
    "scramble for it, they have built a society of equals that prizes "
    "service to the common good.",
    "Its magi speak Romaic Greek and work the Art in Classical Greek, not "
    "Latin; incomers and some Houses keep to Latin, and Gigas campaigns for "
    "it. All politai are equal: titles such as Primus or Archmage carry no "
    "weight here, though callings such as Quaesitor, Redcap and hoplite "
    "are respected.",
    "The polity. Every decision belongs to the Hermetic Assembly, the magi "
    "themselves, voting once each by a show of voting sigils, politai and "
    "metoikoi alike. A polites (citizen) passed Gauntlet in the Tribunal "
    "and keeps his good standing; a metoikos is a guest from elsewhere or "
    "a polites who has lost his rights, and wears grey at meetings. Only "
    "politai hold tokens and shards or serve as magistrates. Each polites "
    "belongs to the phyle of the covenant where his sanctum lies: the "
    "Ionian (Erebos, Epidauros, Hedyosmos), the Aegean (Aegaea, Oikos tou "
    "Eleous, Ingasia), the Kretan (Alexandria, Favonius, Polyaigos) and the "
    "Propontian (Moero's Garden, Gigas, Xylinites, Michael's Tabula).",
    "The Council of Magistrates. Sixteen archai, four from each phyle, are "
    "drawn by lot at each meeting for seven years. They prepare and carry "
    "out the Assembly's business but decide nothing: three sit on each of "
    "the Judicial, Legislative and Conciliatory Boards, and the remaining "
    "seven form the Treasury Council (the apodektai), one of them drawn "
    "as tamias, four gathering vis and Gifted children, and two as tutors "
    "of the children. The book names none of the sixteen or of the board "
    "members, nor the present tamias. The archai elect the archon, who "
    "chairs the Council and is the Tribunal's Praeco: Aiakia of "
    "Hedyosmos since 1214. They also elect the polemarch, who carries out "
    "sentences and leads Wizard's Marches with the Tribunal's restraining "
    "devices: Maria Laskarina of Polyaigos, chosen in 1207 and again in "
    "1214. The logothete, the Chief Redcap, has held office for life "
    "since 1186 and keeps the register of tokens and shards: Leontius of "
    "Alexandria, who means to resign in 1221. There is no Presiding "
    "Quaesitor: the boards do the Quaesitors' work, and Theban Quaesitors "
    "vote like anyone else.",
    "Tokens and shards. A token, a bronze disc stamped with a gorgon's "
    "face, rewards a service to the community; a shard of pottery marks "
    "an act against the polity's unity, and anyone holding one may be "
    "ostracised. Tokens buy the sponsored Longevity Ritual and pay for "
    "neutralisation; they may be given away but never traded for vis. "
    "The logothete's register is known to be faulty, so the holdings "
    "entered here are only what the book implies, and the storyguide "
    "should treat the rest as in doubt.",
    "The meeting. The Tribunal meets every seven years on Delos, the "
    "floating island that wanders the Cyclades; the last meetings were in "
    "1207 and 1214 and the next is in 1221. The book gives no season, so "
    "summer is assumed. Each meeting is run by a principal phyle, in turn "
    "Ionian, Aegean, Kretan and Propontian; where the cycle stands now is "
    "left to the storyguide. Before it, each phyle dines in its own house "
    "on Delos to draw up its candidate list, and magi seeking apprentices "
    "interview the Gifted children. Then come four phases: the Hermetic "
    "Assembly (the Conciliatory Board's decrees, decrees of citizenship, "
    "defamation and contrition, news, the Apprentice Presentation and the "
    "ostracism vote), then the Law Council, then the People's Court, and "
    "last the Council of Archai (sentences, conduct reviews, the sortition of new archai and "
    "the election of archon and polemarch). The Rite of Dismissal closes "
    "it, and the magi go down to the sacred lake for the Ceremony of "
    "Propitiation, where each covenant honours its patron.",
    "The treasury. Under a leaden trapdoor on Delos, copied from the one "
    "at Durenmar and opened only by the archon's iron key, lie several "
    "hundred pawns of vis and many old items and texts. The polity "
    "gathers about fifty pawns a year from its common sources, Creo and "
    "Vim above all, and spends half of it on one sponsored Longevity "
    "Ritual a year; the rest pays for the Propitiation, magic for the "
    "archai and Redcaps, healing and emergencies.",
    "Questions for 1221: who follows Leontius as logothete (the Redcaps "
    "are likely to put forward Proximios); the League Against Idolatry's "
    "petition against the Ceremony of Propitiation; Frankish newcomers who "
    "chafe at the polity; and, further off, Tremere's appeal to the Grand "
    "Tribunal of 1228 to retry the last two magi of the League of "
    "Advisors.",
)

SECRET = [
    titled(
        "Whom Proximios serves",
        "Proximios, the likely next logothete, secretly serves the Infernal "
        "and founded the League of the Vigilant to turn the polity's own "
        "suspicions against the innocent.",
    ),
    titled(
        "Ingasia's trade with mundanes",
        "Gemma and Bobila of Ingasia are selling more enchanted items to "
        "mundanes than the Peripheral Code allows, mostly to Nicaea.",
    ),
    titled("Storyguide Notes", "See An Enemy Within."),
]


def build(theban: Theban) -> None:
    b = theban.b
    theban.tribunal = tribunal = b.tribunal(
        NAME,
        package=THEBAN.key,
        summary=SUMMARY,
        secrets=SECRET,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place="Delos",
        magi_total=100,
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _ruins(theban)
    _docket(theban)
    _redcaps(theban)


# -- the Peripheral Code and the Tribunal's customs --

#: The Peripheral Code: (year or None, title, what it says). The Theban
#: Code holds only deliberate law passed by the Law Council; cases set no
#: precedent.
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        865,
        "The polity",
        "When the Tribunal was made, its magi brought its government back "
        "toward the Typikon of Prokopios. The Hermetic Assembly, every magus "
        "present, decides all things by majority, one voting sigil each, "
        "politai and metoikoi alike; the magistrates chosen by lot prepare "
        "and carry out its business but have no vote or power of their own. "
        "The magistrates, not the parties, gather the evidence in a case, "
        "and the Assembly, not the Quaesitores, settles guilt and sentence. "
        "The Code is judged afresh in each case, without precedent.",
    ),
    (
        None,
        "Politai and metoikoi",
        "A polites passed Gauntlet in the Tribunal and stays in good "
        "standing. A metoikos is a magus from another Tribunal, or a "
        "polites who has lost his rights, and can hold neither tokens nor "
        "shards; he is punished by fines or ostracism instead. A metoikos "
        "may ask the Assembly for a decree of citizenship if he lives at an "
        "established covenant, can show he has served the polity, and has "
        "an arche to sponsor him; a new polites cannot be drawn as arche at "
        "the meeting that made him one.",
    ),
    (
        None,
        "The phylai and the sortition",
        "Every polites belongs to the phyle of the covenant where his "
        "sanctum is: Ionian, Aegean, Kretan or Propontian. Each phyle sends "
        "four archai, drawn by lot from its politai who are not serving and "
        "consent to stand; a magus who is eligible but refuses earns a "
        "shard. Archai serve seven years, never two terms running, and "
        "never on the same board twice. Redcaps belong to the phylai but "
        "are not drawn; they fill board seats no arche can.",
    ),
    (
        1186,
        "The officers",
        "The archai elect one of their number as archon, the Tribunal's "
        "Praeco and chair of the Council, who may serve more than once; by "
        "custom an arche with no preference votes for the eldest magus on "
        "the Council. They elect the polemarch from all the politai, and "
        "only a former polemarch may decline; the same magus is often "
        "chosen again and again. The polemarch may award tokens to the magi "
        "she names to help her carry out a Wizard's March, and has the use "
        "of the Tribunal's devices that bind a magus's body and Gift. The "
        "logothete, the Chief Redcap, was once "
        "chosen every seven years, but since 1186 holds office until death, "
        "Twilight, resignation or a vote of no confidence among the "
        "Redcaps, and earns no tokens for it.",
    ),
    (
        None,
        "The Judicial Board",
        "Prepares every charge of a High Crime and may take over any "
        "matter before the other boards that plainly breaks the Oath. A "
        "prosecution and a defence principal are drawn by lot from its "
        "members and must share what they find. In haste, as over the "
        "unlawful slaying of a magus or diabolism, it may call an interim "
        "Tribunal of at least twelve magi from four covenants, and the "
        "polemarch fetches the accused.",
    ),
    (
        None,
        "The Legislative Board",
        "Reviews the Peripheral Code. Any polites may ask for a change, but "
        "must offer a replacement: no ruling can simply be repealed. Two "
        "members drawn by lot argue for the old ruling and the new before "
        "the Law Council at the next meeting, where the Assembly votes. A "
        "polites who fears conviction may seek a review of the law first, "
        "at the risk of having no defence left if it fails.",
    ),
    (
        None,
        "The Conciliatory Board",
        "Hears quarrels between magi, over land, resources, or between "
        "master and apprentice, and investigates an apprentice's death. It "
        "solemnises binding agreements, such as shares of vis sources, the "
        "founding of covenants and new members' Oaths, and issues decrees "
        "of contrition. A settlement is binding only when the whole board "
        "agrees it was fair; its decrees are read to the Assembly, which may "
        "overturn them.",
    ),
    (
        None,
        "Convening a board",
        "No board can call itself together: a polites with a complaint "
        "applies through its Redcap, and the board must meet within six "
        "months, somewhere convenient or relevant. An arche who needs a "
        "board applies as a citizen, and may not sit when his own case is "
        "heard.",
    ),
    (
        None,
        "Tokens and shards",
        "Tokens are earned by service: two for a term as arche, three as "
        "archon, five as polemarch; one for gathering a common vis source "
        "in a Tribunal period; one for a requested service, a Longevity "
        "Ritual made for the treasurer (two at tenth magnitude or more), a "
        "Gifted child delivered, or seven and fourteen years of apprentice "
        "training without abuse; one for a prosecution that convicts and "
        "three if it ends in a March; and what the polemarch awards those "
        "who join a March at her call. Shards punish harm: three for a High "
        "Crime and one for a Low, one for a failed prosecution, losing or "
        "suffering a decree of defamation, refusing candidacy, neglect of "
        "an arche's duty or a promised task, or abusing an apprentice, and "
        "two for withholding a Gifted child. A token holder may ask a shard "
        "holder for a season's service; if he agrees before a Redcap, each "
        "surrenders one, but not within one covenant. A decree of "
        "contrition, with a reparation the magus chooses, also clears a "
        "shard. Tokens may be given, never exchanged for vis.",
    ),
    (
        None,
        "Ostracism",
        "Every polites holding a shard is named at the Assembly, and the "
        "magi vote which of them stand as candidates; then each writes a "
        "name, or 'no one', on a potsherd. The magus named most often loses "
        "his citizenship, must leave the Tribunal within a season, may not "
        "return for seven years, and comes back only as a metoikos.",
    ),
    (
        None,
        "Common vis sources",
        "Vis from the shrines of the old gods and certain mythic sites is "
        "held to belong to everyone, and the Code lists these sources. The "
        "Treasury Council assigns their gathering, which earns a token, "
        "and the vis goes to the Tribunal's coffers.",
    ),
    (
        None,
        "The sponsored Longevity Ritual",
        "Each year the Tribunal pays for one Longevity Ritual. Any polites "
        "with no shards and no working ritual may apply to the tamias by "
        "spring; the one with most tokens, the elder on a tie, wins and "
        "gives up all of them. Winners usually hold three or four. The "
        "rituals are customarily made at Epidauros.",
    ),
    (
        None,
        "Healing",
        "A capable magus asked to heal a sodalis is expected to, paying the "
        "vis himself; the healed customarily gives back about half of it, "
        "and the healer earns a token. The coffers pay only when neither "
        "can. A covenant bears the cost of healing its own members at home, "
        "and no token is given.",
    ),
    (
        None,
        "Gifted children",
        "Whoever finds a Gifted child must tell the Treasury Council, which "
        "houses and schools the children until the Apprentice Presentation "
        "before each meeting. Masters without a shard, and any Bonisagus, "
        "interview them and bid tokens; a child bid for by several chooses "
        "her master, and keeps his tokens. Under pressure from Tytalus, the "
        "Conciliatory Board holds that following the Book of Instruction is "
        "not abuse.",
    ),
    (
        None,
        "Covenant patrons",
        "Every covenant is bound by a pact of mutual protection to a "
        "patron, a spirit, god, genius loci, saint or faerie living within "
        "it, and honours it at the Ceremony of Propitiation. A patron known "
        "to be Infernal would not be tolerated. A covenant whose patron "
        "dies must find another quickly, or is held to have died with it.",
    ),
    (
        None,
        "Founding a covenant",
        "A new covenant must declare its purpose, secure a willing patron "
        "at its site and draw up a charter. The Conciliatory Board checks "
        "all three, and the Assembly then votes a decree of founding, "
        "usually a formality once the board approves.",
    ),
    (
        None,
        "The peace of Delos",
        "No one may be killed or born on Delos: the magi still keep the old "
        "ban for fear of Zeus. No pregnant women or beasts, and no predatory "
        "animals, familiars included, are allowed there during a meeting, "
        "and executions are carried out at sea or on another island.",
    ),
    (
        None,
        "Certamen",
        "Certamen is for real disputes only. Using it to claim precedence "
        "offends the equality of politai, and duelling over a vis find is "
        "thought especially rude: the finders share it, or the richer "
        "yields.",
    ),
    (
        None,
        "Enchanted items sold to mundanes",
        "Through intermediaries, a Theban magus may sell up to five "
        "enchanted items a year to mundanes, where many Tribunals allow "
        "one. Items of Quality are not counted as enchanted items. Both "
        "rules are Stouritus of Ingasia's work.",
    ),
    (
        None,
        "No preying on Hermetic ships",
        "Magi and covenants may not prey on one another's shipping. Piracy "
        "against mundanes is not forbidden, though frowned on.",
    ),
    (
        848,
        "Classical Greek",
        "Just before the Sundering, the Tribunal's magi recast Hermetic "
        "magic in Classical Greek, chosen over the spoken tongue for its "
        "weight and the power of a dead language, and it remains the "
        "Tribunal's Hermetic language. A magus with no Classical Greek has "
        "-10 to tell the Form of a Greek spell, or -5 below an effective "
        "score of 4; Theban magi suffer the same against Latin. The app "
        "does not enforce this.",
    ),
)


# -- the fallen covenants --

#: Each ruined, abandoned or lost covenant: (key, name, region key in
#: `theban.places`, realm, aura, status, summary, secret).
RUINS: tuple[tuple[str, str, str, str, int, str, str, Secrets], ...] = (
    (
        "dorostolon",
        "Dorostolon",
        "greece",
        "Magic",
        0,
        "Known",
        "Founded 815, destroyed 848. A Tremere fortress-covenant on the "
        "south bank of the Danube where the Founder's chief lieutenants "
        "gathered to plan his rule over the Order. Theban magi read his "
        "messages and struck there in secret; the fortress was torn apart, "
        "most say by the titan Typhon, loosed and pointed at it by magi "
        "probably of Hedyosmos, and Tremere's lieutenants were broken in "
        "mind and loyalty. This was the Sundering of Tremere, and no one "
        "has ever owned it. The site now probably lies in Transylvanian "
        "lands, outside the Tribunal.",
        "",
    ),
    (
        "estropi",
        "Estropi",
        "anatolia",
        "Magic",
        0,
        "Known",
        "Founded 914, abandoned 1069. A sept of Bjornaer whose heartbeasts "
        "were all birds of prey, high on Mount Erciyes, the tallest peak of "
        "central Anatolia. Its magi fled when the Seljuks overran the "
        "plateau, and no Theban magus has gone back.",
        "",
    ),
    (
        "grammaton",
        "Grammaton",
        "greece",
        "Magic",
        0,
        "Known",
        "Founded 980, disbanded 1092. The covenant of Grammaton of "
        "Bonisagus and his filii, built for one great work of research "
        "into binding magic. After more than a century it was plain the "
        "goal was out of reach, despite some notable discoveries along the "
        "way, and its magi went to other covenants. The book does not say "
        "where it stood.",
        "",
    ),
    (
        "diadelphia",
        "Diadelphia",
        "islands",
        "Magic",
        0,
        "Known",
        "Founded 1004, disbanded 1067. A Verditius covenant on Kalymnos, "
        "founded by the brothers Cosmas and Baztas, whose feud drove away "
        "every other magus who joined. When Cosmas was ostracised in 1067, "
        "Baztas surprised everyone by leaving the Tribunal with him, and "
        "with no one left the covenant lapsed.",
        "",
    ),
    (
        "kyddopetre",
        "Kyddopetre",
        "anatolia",
        "Magic",
        0,
        "Known",
        "Founded 1039, disbanded 1076. A Flambeau covenant at the Cilician "
        "Gates, the narrow pass through the Taurus into southern Anatolia. "
        "After Manzikert the empire lost Cilicia to the Sultanate of Rum; "
        "the law did not oblige the magi to go, but cut off from the other "
        "Greek covenants they broke up.",
        "",
    ),
    (
        "miphoria",
        "Miphoria",
        "anatolia",
        "Magic",
        0,
        "Known",
        "Faded by about 1063. The first all-Mercere covenant, on the "
        "seaward edge of Smyrna, whose Redcaps travelled by openly magical "
        "means, riding giant magical sea turtles among them. The Tribunal "
        "asked them to stop drawing mundane eyes; without the turtles the "
        "covenant withered, and most of its Redcaps had moved elsewhere "
        "by 1063. Alexandria was founded in its place.",
        "",
    ),
    (
        "court_of_fools",
        "The Court of Fools",
        "constantinople",
        "Magic",
        0,
        "Known",
        "Founded 1101, destroyed 1204. A wandering Ex Miscellanea covenant "
        "of mystics and seers that toured mainland Greece. It happened to "
        "be in Constantinople when the crusaders sacked it, and burned "
        "with the city. Some of its magi have lately reappeared.",
        "",
    ),
    (
        "wilusa",
        "Wilusa",
        "ilion",
        "Faerie",
        0,
        "Rumoured",
        "Founded 1109, lost. Droserius of Merinita and four companions were "
        "allowed to found a covenant at Ilion, claiming the spirit of the "
        "river Scamander dwelt in one of its regiones and would be their "
        "patron. By the next meeting covenant and magi had vanished without "
        "a trace, and the Tribunal has turned down every later proposal to "
        "settle at Ilion. See the Wilusa story.",
        [
            titled(
                "Odysseus's trick",
                "A faerie calling himself Odysseus tricked Droserius into "
                "building Wilusa in the wrong regio, then shut its boundaries.",
            ),
            titled(
                "Wilusa dressed as Troy",
                "Odysseus has dressed the covenant of Wilusa as Troy and replays "
                "the last assault on it endlessly; the magi defend it by reflex, "
                "and have lived only a few months while a century has passed "
                "outside.",
            ),
            titled(
                "The other regiones at Ilion",
                "Other regiones at Ilion stage the same war as Wilusa, to "
                "mislead searchers.",
            ),
            titled(
                "Leaving Wilusa",
                "The lost magi of Wilusa will be slow to leave unless told how "
                "long they have been gone.",
            ),
            titled("Storyguide Notes", "Wilusa's regio has a Faerie aura of 4."),
        ],
    ),
    (
        "thermakopolis",
        "Thermakopolis",
        "constantinople",
        "Magic",
        0,
        "Known",
        "Founded 1115, destroyed 1204. An urban covenant of five Jerbiton "
        "under the Archmagus Mathieus, masters of Mentem, sworn to preserve "
        "and protect Constantinople. They promised the Tribunal all was well "
        "as the Latins gathered, failed to make peace by magic, and then "
        "stood on the walls, where their spells scared off the defenders "
        "beside them. Four died in the assault and the fires, as did the "
        "famed Michael, who gave his name to Michael's Tabula; Mathieus "
        "alone survived and went to Normandy, where he founded Eboris. It "
        "is the great shame of House Jerbiton, and young Jerbiton magi want "
        "to found a covenant in the city again: its site is the obvious "
        "ruin to refound on.",
        [
            titled(
                "Why Thermakopolis's magic failed",
                "Thermakopolis's mind magic failed because several crusade "
                "leaders carried protections born of a union of men and demons.",
            )
        ],
    ),
    (
        "lamites",
        "Lamites",
        "anatolia",
        "Magic",
        0,
        "Known",
        "Founded 1123, destroyed 1127. A brief covenant of Anatolian "
        "prophets who named the Phrygian Sibyl, Lamia, as their patron. "
        "All were killed within four years, most think by the sibyl for "
        "their presumption, though the faerie of the same name may have "
        "resented the rivalry.",
        "",
    ),
    (
        "thumachia",
        "Thumachia",
        "greece",
        "Magic",
        0,
        "Known",
        "Founded 1151, sacked 1185. A mostly Jerbiton covenant set up to "
        "guard the western border after the harm done by the Second "
        "Crusade, walking the narrow line between meddling with mundanes "
        "and protecting its sodales. The Sicilian Normans sacked it in "
        "their war with the empire, and its survivors joined Thermakopolis "
        "rather than rebuild.",
        "",
    ),
    (
        "novocastrum",
        "Novocastrum",
        "greece",
        "Magic",
        0,
        "Known",
        "Founded 1207, destroyed 1212. A Frankish covenant on the western "
        "edge of the Kingdom of Thessaloniki, in land Epiros has since "
        "taken. It had little time to prepare before the Greeks came, and "
        "its magi died resisting them. Few Theban magi grieved.",
        "",
    ),
)


def _ruins(theban: Theban) -> None:
    b = theban.b
    for key, name, _region, realm, aura, status, summary, hidden in RUINS:
        levels = (
            [
                b.level(
                    "Wilusa's false Troy",
                    4,
                    "Faerie",
                    notes="Its boundaries are shut by the faerie Odysseus.",
                )
            ]
            if key == "wilusa"
            else None
        )
        theban.places[f"ruin_{key}"] = b.place(
            name,
            ruined=True,
            summary=summary,
            secrets=hidden,
            realm=realm,
            aura=aura,
            status=status,
            known="In the Tribunal",
            levels=levels,
        )


# -- the docket --


def _docket(theban: Theban) -> None:
    b, tribunal = theban.b, theban.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "The logothete's succession",
        kind="motion",
        brought_by="Leontius of Mercere (the logothete)",
        charge="Leontius regrets taking the office and means to resign at "
        "the meeting of 1221, so a new logothete must be chosen. House "
        "Mercere's choice is the subject of much guessing; Proximios of "
        "Alexandria is the name most often heard.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
    )
    b.case(
        tribunal,
        "The faulty register of tokens and shards",
        kind="motion",
        brought_by="",
        against="Leontius of Mercere (the logothete)",
        charge="Under Leontius records have gone astray and the book of "
        "tokens and shards has been found unreliable. He narrowly escaped "
        "ostracism in 1214, and the polity will want the register put "
        "right before ostracism or the Longevity Ritual depends on it.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Against the Ceremony of Propitiation",
        kind="motion",
        brought_by="The League Against Idolatry (Oikos tou Eleous and Gigas)",
        charge="The league asks the Legislative Board to end the Ceremony "
        "of Propitiation and the Tribunal's recognition of patrons, saying "
        "the altars and vis offerings on Delos have passed from veneration "
        "into worship, a mortal sin that endangers every magus who takes "
        "part. Under the Code its petition must offer a replacement ruling. "
        "Artoud of Xylinites gives it fitful support; the issue stirs "
        "anger every time it is raised.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Caterina da Vigonovo's citizenship",
        kind="motion",
        brought_by="Caterina da Vigonovo of Jerbiton (Polyaigos)",
        charge="A Venetian Gauntleted in Rome and newly settled at "
        "Polyaigos, Caterina is a metoikos and distrusted for her city's "
        "part in the sack. She wants the Tribunal to sponsor her Longevity "
        "Ritual and is working to build her name; as a metoikos she can "
        "hold no tokens, so she needs a decree of citizenship, with an "
        "arche to sponsor her, first.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Nanno and Ampelius",
        kind="motion",
        brought_by="Ziper of Tytalus (Moero's Garden)",
        charge="Ziper wants the craftsmen Nanno and Ampelius, unGifted "
        "makers of minor enchanted wares, taken into Moero's Garden as "
        "members of House Jerbiton; Proximios backs him and Syagricus does "
        "not object, but the rest of the covenant is appalled at admitting "
        "tradesmen. The two artisans threaten to sail to Delos and ask the "
        "whole Tribunal.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Passara and the Latin emperor",
        kind="charge",
        brought_by="Formosos of Guernicus",
        against="Passara of Verditius",
        charge="Formosos, grandson in the Art of Vaanes, holds that Vaanes "
        "wrongly shielded Aella, the maker of the Magnaura's automata, and "
        "means to prove that Passara, her heir who tends them from rooms in "
        "the palace, actually works for the Latin emperor. He is looking "
        "for magi to investigate her quietly.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "The mysterious knight of 1211",
        kind="charge",
        brought_by="(not yet brought)",
        against="Unknown",
        charge="Greek chroniclers say an unknown Frankish knight appeared "
        "from nowhere at Antioch-on-the-Maeander and killed Sultan "
        "Kaykhusraw as he stood over the fallen Theodore Laskaris, saving "
        "the Empire of Nicaea. Rumour says it was a magus in disguise, "
        "which would be gross interference; a senior magus wants it solved "
        "before the meeting of 1221.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Normalising the Tribunal",
        kind="motion",
        brought_by="Gigas and the Frankish newcomers",
        charge="Gigas condemns the polity's 'vulgar paganism' and works to "
        "bring the Tribunal into line with the rest of the Order: Latin "
        "over Greek, new precedents, and reviewing every law it can when "
        "one of its magi sits on the Legislative Board. It helped make the "
        "logothete permanent. The few Frankish magi who came east after "
        "1204 are pushing for changes of their own.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "A covenant in Constantinople again",
        kind="motion",
        brought_by="Young Jerbiton magi and their apprentices",
        charge="Many Jerbiton, above all the apprentices soon to be "
        "Gauntleted, want to reclaim the city and found a covenant inside "
        "its walls, as Thermakopolis was. The Tribunal has not decided "
        "whether to encourage it, and most would rather wait and see.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Tremere's appeal over the League of Advisors",
        kind="motion",
        brought_by="House Tremere",
        against="The two surviving magi of the League of Advisors",
        charge="The League of Advisors sat openly at the emperor's court "
        "from 1185, claiming only to advise. After 1204 it was blamed for "
        "meddling and broke up, and the Tribunal failed to convict its "
        "members. Tremere has asked the Grand Tribunal of 1228 to hear the "
        "case of its last two members again; if it succeeds, the autonomy "
        "of every Tribunal, and the Theban polity above all, may suffer.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Ingasia's sales to Nicaea",
        kind="charge",
        brought_by="(no one: it is not known)",
        against="Gemma and Bobila of Verditius (Ingasia)",
        charge="Secret. Without their parens Stouritus noticing, the twins "
        "sell more enchanted items to mundanes than the Code's five a year, "
        "favouring the Nicene Greeks, Venice's sworn enemies, and raise "
        "Ingasia's wealth slowly so no one remarks it. Their autocrat sees "
        "the money but asks no questions. A case can be brought only once "
        "someone finds out.",
        filed_year=1220,
        filed_season="Spring",
    )


# -- the Redcaps described with the polity --


def _redcaps(theban: Theban) -> None:
    b = theban.b
    m = theban.magi
    m["lysandros"] = b.magus(
        "Lysandros",
        covenant=None,
        house=MERCERE,
        age=None,
        summary="An unGifted Redcap and perhaps the finest authority on "
        "the Code of Hermes in the Tribunal. He always serves an arche of "
        "the Judicial Board, and every arche comes to him over hard points "
        "of law; but he is rude and pedantic beyond bearing, and answers "
        "precisely the question put to him, adding nothing the asker did "
        "not think to ask for.",
        traits={"Pedantic": 3, "Abrasive": 2},
    )
    m["diantha"] = b.magus(
        "Diantha",
        covenant=None,
        house=MERCERE,
        age=None,
        summary="An unGifted Redcap, beautiful and charming, who makes "
        "friends of men and women alike, so that the logothete has to field "
        "several requests for her each term. She is most use to archai "
        "whose work brings them among mundanes, for she can bring almost "
        "anyone round to her view of a matter.",
        traits={"Charming": 3, "Friendly": 2},
    )
    m["niko"] = b.magus(
        "Niko",
        covenant=None,
        house=MERCERE,
        age=None,
        summary="A young, keen Redcap, son of a magus and raised inside "
        "the Order, for whom the red cap seemed the natural calling. He "
        "has never yet assisted an arche and longs for his first posting.",
        traits={"Eager": 3},
    )
    m["aristides"] = b.magus(
        "Aristides",
        covenant=None,
        house=MERCERE,
        age=58,
        summary="One of the Redcaps in the logothete's own service, nearly "
        "sixty but still vigorous, and widely thought to carry the blood of "
        "Odysseus. He has certainly travelled everywhere: his little "
        "fishing skiff, which he sails alone, is hardly ever still, and he "
        "seldom sleeps two nights running ashore.",
        traits={"Restless": 3},
    )


#: The Redcaps' generated stats: none has a printed stat block.
PROFILES: dict[str, Profile] = {
    "lysandros": Profile(
        gifted=False,
        strong="int per com",
        weak="pre",
        native=GREEK,
        age=70,
        abilities={
            "Code of Hermes": (6, "the Peripheral Code"),
            "Organization Lore: Order of Hermes": 3,
            "Artes Liberales": 3,
            "Dead Language: Classical Greek": 3,
            "Dead Language: Latin": 2,
        },
        virtues=["Redcap", "Social Handicap", "Dutybound", "Proud (Minor)"],
    ),
    "diantha": Profile(
        gifted=False,
        strong="pre com per",
        native=GREEK,
        age=34,
        abilities={
            "Charm": (5, "first impressions"),
            "Folk Ken": 4,
            "Etiquette": 3,
            "Guile": 2,
        },
        virtues=["Redcap", "Venus' Blessing", "Curse of Venus", "Dutybound"],
    ),
    "niko": Profile(
        gifted=False,
        strong="qik sta dex",
        native=GREEK,
        age=20,
        abilities={"Ride": 3, "Athletics": 2, "Organization Lore: Order of Hermes": 2},
        virtues=[
            "Redcap",
            "Overconfident (Minor)",
            "Sheltered Upbringing",
            "Dutybound",
        ],
    ),
    "aristides": Profile(
        gifted=False,
        strong="sta per str",
        native=GREEK,
        abilities={
            "Profession: Sailor": (5, "small boats"),
            "Survival": 3,
            "Athletics": 2,
        },
        virtues=["Redcap", "Well-Traveled", "Compulsion (Major)", "Dutybound"],
    ),
}


def stats(theban: Theban) -> None:
    """Generated stats for the Redcaps described with the polity."""
    for key, profile in PROFILES.items():
        apply(theban.b, theban.magi[key], profile)


# -- after every part has built --

#: Each Theban covenant, by phyle: (phyle, slug, names it may go by).
PHYLAI: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Ionian", "erebos", ("Erebos",)),
    ("Ionian", "epidauros", ("Epidauros",)),
    ("Ionian", "hedyosmos", ("Hedyosmos",)),
    ("Aegean", "aegaea", ("Aegaea",)),
    ("Aegean", "oikos_tou_eleous", ("Oikos tou Eleous", "Oikos Tou Eleous")),
    ("Aegean", "ingasia", ("Ingasia",)),
    ("Kretan", "alexandria", ("Alexandria",)),
    ("Kretan", "favonius", ("Favonius",)),
    ("Kretan", "polyaigos", ("Polyaigos",)),
    ("Propontian", "moeros_garden", ("Moero's Garden", "Moero’s Garden")),
    ("Propontian", "gigas", ("Gigas",)),
    ("Propontian", "xylinites", ("Xylinites",)),
    ("Propontian", "michaels_tabula", ("Michael's Tabula", "Michael’s Tabula")),
)

#: Each fallen covenant's ties to living covenants: (ruin key, covenant
#: slug, note).
TIES: tuple[tuple[str, str, str], ...] = (
    ("dorostolon", "hedyosmos", "Its magi are credited with the Sundering"),
    ("miphoria", "alexandria", "Founded to take its place"),
    ("thermakopolis", "michaels_tabula", "Founded by survivors of the sack"),
)

#: Every living magus the book names in the Tribunal, by slug, in the
#: order of their covenants' phylai, then those who live outside a
#: covenant. Magi the book gives only a name are entered if a part made
#: them, but not looked for.
NAMED_MAGI: tuple[str, ...] = (
    # Ionian.
    "destasia",
    "xenias",
    "galla",
    "ausculator",
    "aiakia",
    "tisiphon",
    "celaenea",
    # Aegean.
    "lucian",
    "leukothea",
    "delfini",
    "krum",
    "anna",
    "theocharista",
    "nereida",
    "nonna",
    "stouritus",
    "theorus",
    "hydatius",
    "eudoxia",
    "gemma",
    "bobila",
    # Kretan.
    "leontius",
    "proximios",
    "catella",
    "memnos",
    "verecunda",
    "aeliophanes",
    "maria_laskarina",
    "gerasimos",
    "ioannes",
    "caterina",
    "satabus",
    # Propontian.
    "ionnia",
    "syagricus",
    "ziper",
    "boustaphan",
    "monorchis",
    "allectores",
    "artoud",
    "theoderet",
    "trasaricus",
    "petros",
    "wilrich",
    # Outside a covenant.
    "pythia",
    "zacharias",
    "passara",
    "formosos",
    "kristophoros",
    "marcus_tauros",
)

#: What the book implies of a magus's holdings (T2): (tokens, shards,
#: services, why). Everyone else starts at none.
HOLDINGS: dict[str, tuple[int, int, int, str]] = {
    "maria_laskarina": (
        5,
        0,
        0,
        "Five for her first term as polemarch, 1207 to 1214; she serves a "
        "second term to 1221.",
    ),
    "ioannes": (
        7,
        0,
        0,
        "Two terms on the Council of Magistrates: two as arche, then two "
        "as arche and three as archon.",
    ),
    "pythia": (
        1,
        0,
        1,
        "She gathers Delphi's vis for the Tribunal.",
    ),
    "leontius": (
        0,
        1,
        0,
        "The book implies a shard: he narrowly escaped ostracism in 1214. "
        "The logothete earns no tokens for his office.",
    ),
}

#: The apparent ages the book prints beside each magus's age (The
#: Sundered Eagle pp. 63-102); Anatolia's magi have theirs in
#: anatolia.APPARENT_AGES.
APPARENT_AGES: dict[str, int] = {
    "xenias": 107,  # p. 63
    "galla": 52,  # p. 64
    "destasia": 37,  # p. 65
    "boustaphan": 64,
    "monorchis": 42,  # p. 66
    "allectores": 33,
    "ausculator": 88,  # p. 68
    "aiakia": 53,
    "tisiphon": 51,
    "celaenea": 44,
    "anna": 62,  # p. 70
    "theocharista": 63,
    "nereida": 22,
    "nonna": 31,
    "lucian": 65,  # p. 83
    "leukothea": 25,
    "delfini": 43,
    "krum": 40,
    "memnos": 58,  # p. 85
    "verecunda": 38,
    "aeliophanes": 19,
    "stouritus": 93,  # p. 87
    "eudoxia": 42,
    "gemma": 35,
    "bobila": 35,
    "maria_laskarina": 58,  # p. 89
    "gerasimos": 44,
    "ioannes": 41,  # p. 90
    "caterina": 53,
    "petros": 11,  # p. 100
    "wilrich": 43,
    "artoud": 71,  # p. 102
    "theoderet": 43,
}

#: Magi from other Tribunals, who are metoikoi.
METOIKOI: dict[str, str] = {
    "caterina": "Gauntleted in the Roman Tribunal; newly arrived from Venice.",
    "wilrich": "A Saxon, trained outside the Tribunal; came east with the "
    "Fourth Crusade.",
    "artoud": "Trained in the Levant, where his old Clutch was destroyed.",
}

REGISTER_NOTE = "The register is in doubt; the storyguide may adjust."

#: What finish could not find, for the report.
MISSING: list[str] = []


def _covenant(theban: Theban, slug: str, names: tuple[str, ...]) -> Covenant | None:
    for name in names:
        try:
            return theban.covenant_named(name)
        except KeyError:
            continue
    found = theban.covenants.get(slug)
    if found is None:
        MISSING.append(f"covenant {names[0]}")
    return found


def _office(
    office: str, holder: Character | None, term_ends: int | None, duties: str
) -> dict[str, Any]:
    return {
        "office": office,
        "holder_id": holder.id if holder is not None else None,
        "term_ends": term_ends,
        "duties": duties,
    }


def _magus(theban: Theban, slug: str, role: str) -> Character | None:
    found = theban.magi.get(slug)
    if found is None:
        MISSING.append(f"{slug} ({role})")
    return found


def _patrons(saga: Saga, tribunal: Tribunal) -> None:
    """Each covenant's patron, named in its Powerful or Local Ally line
    (The Sundered Eagle p. 30), for the Ceremony of Propitiation."""
    patrons = package.data(tribunal, package.KEY).setdefault("patrons", {})
    for covenant in saga.covenants:
        for line in covenant.what_matters.splitlines():
            for ally in ("Boon: Powerful Ally (", "Boon: Local Ally ("):
                if line.startswith(ally) and "patron" in line:
                    name = line.removeprefix(ally).split(",")[0].strip()
                    patrons[covenant.id] = {"name": name}


def _apparent_ages(theban: Theban) -> None:
    for slug, apparent in APPARENT_AGES.items():
        magus = theban.magi.get(slug)
        if magus is None:
            MISSING.append(f"{slug} (apparent age)")
        else:
            magus.aging.apparent_age = apparent


#: The covenants' shared laboratories the book gives bonuses for: the
#: covenant, its name, its Specializations and what the book says.
SHARED_LABS: tuple[tuple[str, str, dict[str, int], str], ...] = (
    (
        "Ingasia",
        "The Forge of Hephaistos",
        {"Rego": 8, "Items": 5},
        "The Sundered Eagle p. 86: the ancient forge at the volcano's heart, "
        "made a Hermetic laboratory shared by the magi, +8 to Rego and +5 "
        "to making enchanted items",
    ),
    (
        "Epidauros",
        "The Hall of Repose (Enkoimeteria)",
        {"Longevity Rituals": 6},
        "The Sundered Eagle p. 63: the shared laboratory specialized in "
        "longevity and healing; +6 to a Longevity Ritual's Lab Total for "
        "one who sleeps here, who also gains +12 to the next Wound "
        "Recovery roll",
    ),
)


def _shared_labs(theban: Theban) -> None:
    for covenant_name, name, specializations, says in SHARED_LABS:
        try:
            covenant = theban.covenant_named(covenant_name)
        except KeyError:
            MISSING.append(f"covenant {covenant_name} (laboratory)")
            continue
        theban.b.laboratory(
            covenant,
            name,
            characteristics={},
            specializations=specializations,
            source=says.split(":")[0],
            rooms={"As the book describes it": says},
        )


def finish(theban: Theban) -> None:
    tribunal = theban.tribunal
    assert tribunal is not None
    b, saga = theban.b, theban.b.saga
    MISSING.clear()

    aiakia = _magus(theban, "aiakia", "the archon and Praeco")
    maria = _magus(theban, "maria_laskarina", "the polemarch")
    leontius = _magus(theban, "leontius", "the logothete")
    tribunal.praeco_id = aiakia.id if aiakia is not None else None
    # No Presiding Quaesitor: the boards do the Quaesitors' work.
    tribunal.quaesitor_id = None
    package.archai(tribunal)[:] = [
        _office(
            "Archon",
            aiakia,
            1221,
            "Chairs the Council of Magistrates and is the Tribunal's "
            "Praeco; keeps the key of the treasury on Delos",
        ),
        _office(
            "Polemarch",
            maria,
            1221,
            "Enforces sentences and decrees and leads Wizard's Marches, "
            "with the Tribunal's restraining devices",
        ),
        _office(
            "Logothete",
            leontius,
            None,
            "The Chief Redcap, for life since 1186: records the Council's "
            "business and the register of tokens and shards; resigning in "
            "1221",
        ),
        _office(
            "Tamias",
            None,
            1221,
            "Treasurer, drawn by lot from the Treasury Council; the book "
            "does not name the holder",
        ),
    ]

    _patrons(saga, tribunal)
    phylai = package.phylai(tribunal)
    phylai.clear()
    covenants: dict[str, Covenant] = {}
    for phyle, slug, names in PHYLAI:
        covenant = _covenant(theban, slug, names)
        if covenant is not None:
            phylai[covenant.id] = phyle
            covenants[slug] = covenant

    _apparent_ages(theban)
    _shared_labs(theban)
    entries = package.magi(tribunal)
    entries.clear()
    seen: set[str] = set()
    order = [*NAMED_MAGI, *(k for k in theban.magi if k not in NAMED_MAGI)]
    for slug in order:
        character = theban.magi.get(slug)
        if character is None:
            if slug in NAMED_MAGI:
                MISSING.append(f"{slug} (tokens and shards)")
            continue
        if character.type != "magus" or character.id in seen:
            continue
        seen.add(character.id)
        tokens, shards, services, why = HOLDINGS.get(slug, (0, 0, 0, ""))
        metoikos = slug in METOIKOI
        entries.append(
            {
                "character_id": character.id,
                "status": "metoikos" if metoikos else "polites",
                "tokens": 0 if metoikos else tokens,
                "shards": 0 if metoikos else shards,
                "services": services,
                "ostracised_until": None,
                "why": METOIKOI[slug] if metoikos else (why or REGISTER_NOTE),
            }
        )

    for key, _name, region, *_ in RUINS:
        site, around = theban.places[f"ruin_{key}"], theban.places.get(region)
        if around is None:
            if f"region place {region!r}" not in MISSING:
                MISSING.append(f"region place {region!r}")
        elif site.place_id is None:
            site.place_id = around.id
    for key, slug, note in TIES:
        covenant = covenants.get(slug)
        if covenant is not None:
            b.link(theban.places[f"ruin_{key}"], "covenants", covenant, note)
    tribunal.covenants_total = len(
        [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    )
