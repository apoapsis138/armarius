"""More on a character's sheet, by section: rolls, deeds, faith, magic and the books' own actions."""

from __future__ import annotations

from functools import partial

from ... import (
    aging_due,
    deeds,
    disputations,
    guest_stays,
    health,
    labor,
    melee_events,
    selling,
    session_end,
    study_path,
    teaching,
    theban_customs,
    tourney_season,
    traditions,
)
from ... import baraka as baraka_forms
from ... import devotion as devotion_forms
from ... import mystic_paths as mystic_forms
from ... import theban_customs as byzantine
from ...actions import NodeKind
from ...rules import apothecary, galdor, merchants
from ...rules import theban_customs as byzantine_rules
from ...rules import tmre_alchemy as tmre_alchemy_rules
from ...sections import FAITH_SECTION
from .. import acclaim as acclaim_forms
from .. import apothecary as apothecary_forms
from .. import beast as beast_forms
from .. import boost as boost_forms
from .. import careers
from .. import certamen_duel as certamen_forms
from .. import church as church_forms
from .. import covers as cover_forms
from .. import craft_magic as craft_forms
from .. import criamon as criamon_forms
from .. import faerie_dealings as faerie_forms
from .. import galdor as galdor_forms
from .. import gauntlet as gauntlet_forms
from .. import goetic as goetic_forms
from .. import grog_story as grog_story_forms
from .. import grogs as grog_forms
from .. import hedge_cast as hedge_cast_forms
from .. import holy_influence as holy_influence_forms
from .. import hubris as hubris_forms
from .. import lacuna as lacuna_forms
from .. import mystery_cults as cult_forms
from .. import pilgrimage as pilgrimage_forms
from .. import season as season_forms
from .. import sessions as session_forms
from .. import sin as sin_forms
from .. import tmre_alchemy as tmre_alchemy_forms
from .. import tmre_divination as tmre_divination_forms
from .. import tmre_dreams as tmre_dream_forms
from .. import tmre_spirits as tmre_spirit_forms
from .. import trait_roll as trait_roll_forms
from .. import tunnel as tunnel_forms
from .. import turbulence as turbulence_forms
from .. import twilight as twilight_forms
from .. import vf_change as vf_change_forms
from .. import whereabouts as whereabouts_forms
from ..menu_refresh import calculator, changes
from ..menu_steps import (
    character,
    character_traditions,
    lab_text_access,
    needs,
    share_command,
    sheet_roll_step,
)
from .entry import MoreAction
from .rules import (
    adds_purity,
    bargains_with_faeries,
    boosts_spell,
    casts_hedge_magic,
    casts_in_lacuna,
    commands_beast,
    disputes,
    exorcises,
    experiments,
    faces_gauntlet,
    gives_silver,
    goes_on_pilgrimage,
    grog_has_plan,
    grog_season,
    has_asks,
    has_reputation,
    influences,
    is_proud,
    joins_traditions,
    keeps_acclaim,
    keeps_byzantine_custom,
    keeps_faith,
    learns_cantation,
    makes_art,
    makes_ligature,
    may_lose_gift,
    moves_to_source,
    offers_to_faerie,
    on_covenfolk,
    on_known_spells,
    plans_goal,
    plans_journey,
    reads_signs,
    rolls_from_sheet,
    rop_divine,
    shares_spell,
    sings,
    sins,
    studies,
    turbulent,
    walks_in_faith,
    works_for_labor,
    works_goetia,
    works_with_spirits,
)

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "share_spell",
        "s",
        "Share Spell",
        step=share_command,
        refresh=changes("section-known-spells", tree=True),
        places=((NodeKind.CHARACTER, "Known Spells"),),
        in_section=shares_spell,
    ),
    MoreAction(
        "boost_spell",
        "b",
        "Boost a Spell",
        step=needs(character, boost_forms.boost_form),
        refresh=calculator(),
        places=((NodeKind.CHARACTER, "Known Spells"),),
        in_section=boosts_spell,
    ),
    MoreAction(
        "give_silver",
        "s",
        "Give Silver",
        refresh=changes(whole_page=True),
        places=(
            (NodeKind.CHARACTER, "Personal Gear"),
            (NodeKind.COVENANT, "Wealth"),
        ),
        on_record=gives_silver,
    ),
    MoreAction(
        "lab_text_access",
        "l",
        "Lab Texts Read",
        step=needs(character, lab_text_access),
        refresh=changes("section-hermetic-background", "section-books"),
        section="section-hermetic-background",
        places=(
            (NodeKind.CHARACTER, "Hermetic Background"),
            (NodeKind.LABORATORY, "Lab Texts"),
        ),
    ),
    MoreAction(
        "edit_traditions",
        "t",
        "Traditions",
        step=needs(character, character_traditions),
        refresh=changes("section-char-info", "tab-abilities", reshow=True),
        places=((NodeKind.CHARACTER, "Abilities"),),
        on_record=joins_traditions,
    ),
    MoreAction(
        "disputatio",
        "d",
        "Disputatio",
        step=needs(character, disputations.disputatio_form),
        refresh=changes("section-char-info"),
        places=((NodeKind.CHARACTER, deeds.SCHOLARLY),),
        on_record=disputes,
    ),
    MoreAction(
        "hedge_cast",
        "c",
        "Cast a Power",
        step=needs(character, hedge_cast_forms.cast_form),
        refresh=changes("section-aging", "tab-diary"),
        places=((NodeKind.CHARACTER, "Abilities"),),
        on_record=casts_hedge_magic,
    ),
    MoreAction(
        "galdor_conjure",
        "j",
        "Conjure a Spirit",
        step=needs(character, galdor_forms.conjure_form),
        refresh=changes("section-aging", "section-char-health", "tab-diary"),
        places=((NodeKind.CHARACTER, "Abilities"),),
        on_record=partial(sings, galdor.conjures),
    ),
    MoreAction(
        "galdor_bargain",
        "q",
        "Bargain with a Lord",
        step=needs(character, galdor_forms.bargain_form),
        refresh=changes(traditions.bonds_section(galdor.TRADITION_ID), "tab-diary"),
        places=((NodeKind.CHARACTER, "Abilities"),),
        on_record=partial(sings, galdor.bargains),
    ),
    MoreAction(
        "galdor_bind",
        "z",
        "Bind an Item",
        step=needs(character, galdor_forms.bind_form),
        refresh=changes(
            traditions.effects_section(galdor.TRADITION_ID),
            "section-aging",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, "Abilities"),),
        on_record=partial(sings, galdor.enchants),
    ),
    MoreAction(
        "edit_fatigue",
        "f",
        "Edit Fatigue",
        section="section-char-health",
        on_page=False,
    ),
    MoreAction(
        "take_harm",
        "h",
        "Take Harm",
        step=needs(character, health.take_harm_form),
        refresh=changes("section-char-health"),
        section="section-char-health",
        places=((NodeKind.CHARACTER, "Health"),),
    ),
    MoreAction(
        "recovery_roll",
        "y",
        "Recovery Roll",
        step=needs(character, health.recovery_form),
        refresh=changes("section-char-health"),
        section="section-char-health",
        places=((NodeKind.CHARACTER, "Health"),),
    ),
    MoreAction(
        "end_session",
        "e",
        "End of Session",
        step=needs(character, session_end.end_session_form),
        refresh=changes("section-reputations", "section-char-info"),
        section="section-reputations",
        places=((NodeKind.CHARACTER, deeds.SESSION),),
    ),
    MoreAction(
        "what_changed",
        "w",
        "What Changed Since the Last Session",
        step=needs(character, session_forms.since_last_session),
        refresh=calculator(),
        section="section-reputations",
        places=((NodeKind.CHARACTER, deeds.SESSION),),
    ),
    # Roll from the sheet, at the Session Under way (forms/sheet_roll.py).
    MoreAction(
        "sheet_roll",
        "o",
        "Roll",
        step=lambda page: sheet_roll_step(page),
        refresh=calculator(),
        places=(
            (NodeKind.CHARACTER, "Abilities"),
            (NodeKind.CHARACTER, "Characteristics"),
        ),
        in_section=rolls_from_sheet,
    ),
    MoreAction(
        "teaching_requests",
        "q",
        "Teaching Requests",
        step=needs(character, teaching.requests_command),
        refresh=changes("section-char-season", "section-char-ahead", "tab-planning"),
        section="section-char-season",
        places=((NodeKind.CHARACTER, "This Season"),),
        on_record=has_asks,
    ),
    MoreAction(
        "study_path",
        "y",
        "Study Path",
        step=needs(character, study_path.study_path_form),
        refresh=changes("section-char-season", "section-char-ahead", "tab-planning"),
        section="section-char-season",
        places=((NodeKind.CHARACTER, "This Season"),),
    ),
    MoreAction(
        "tourney_season",
        "t",
        "Tournament",
        step=needs(character, tourney_season.tourney_form),
        refresh=changes("section-reputations", "tab-diary"),
        section="section-reputations",
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
    ),
    MoreAction(
        "melee_event",
        "v",
        "Melee Event",
        step=needs(character, melee_events.melee_form),
        refresh=changes("section-reputations", "tab-diary"),
        section="section-reputations",
        places=((NodeKind.CHARACTER, deeds.KNIGHTLY),),
    ),
    MoreAction(
        "command_beast",
        "c",
        "Command the Beast",
        step=needs(character, beast_forms.command_form),
        refresh=changes("section-personality-traits"),
        section="section-personality-traits",
        places=((NodeKind.CHARACTER, "Personality Traits"),),
        on_record=commands_beast,
    ),
    MoreAction(
        "place_aging_points",
        "a",
        "Place Aging Points",
        step=needs(character, aging_due.character_form),
        refresh=changes("section-aging", "section-char-characteristics"),
        section="section-aging",
        places=((NodeKind.CHARACTER, "Aging"),),
    ),
    MoreAction(
        "resolve_twilight",
        "w",
        "Resolve Twilight",
        step=needs(character, twilight_forms.resolve_twilight_form),
        refresh=changes("section-aging"),
        section="section-aging",
        places=((NodeKind.CHARACTER, "Aging"),),
    ),
    MoreAction(
        "disguise_roll",
        "g",
        "Disguise Roll",
        step=needs(character, cover_forms.disguise_form),
        refresh=calculator(),
        section="section-char-covers",
        places=((NodeKind.CHARACTER, "Covers"),),
    ),
    MoreAction(
        "trait_roll",
        "o",
        "Roll",
        step=needs(character, trait_roll_forms.roll_form),
        refresh=calculator(),
        section="section-personality-traits",
        places=((NodeKind.CHARACTER, "Personality Traits"),),
    ),
    # A player's goal of a score to reach (forms/notes_goals.py).
    MoreAction(
        "plan_goal", "p", "Plan the Study Path", on_page=False, in_section=plans_goal
    ),
    MoreAction(
        "add_purity", "p", "Add a Purity", on_page=False, in_section=adds_purity
    ),
    MoreAction(
        "move_to_source",
        "s",
        "Move to Source",
        on_page=False,
        in_section=moves_to_source,
    ),
    MoreAction("plan_journey", "j", "Travel", on_page=False, in_section=plans_journey),
    MoreAction(
        "labor_story",
        "l",
        "Labor Points from a Story",
        step=needs(character, labor.story_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=works_for_labor(lambda c: bool(merchants.work_abilities(c))),
    ),
    # A grog's story experience, counted against the yearly update.
    MoreAction(
        "grog_story_xp",
        "s",
        "Story Experience",
        step=needs(character, grog_story_forms.story_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=grog_season,
    ),
    # A grog's season of copying, planned like anyone's (DE p. 380).
    MoreAction(
        "plan_copying",
        "c",
        "Plan Copying",
        step=needs(character, season_forms.copying_form),
        refresh=changes("section-char-season"),
        places=((NodeKind.CHARACTER, "This Season"),),
        in_section=lambda facts, section: (
            grog_season(facts, section) and not grog_has_plan(facts)
        ),
    ),
    MoreAction(
        "clear_copying",
        "x",
        "Clear Copying",
        step=needs(character, season_forms.clear_copying_form),
        refresh=changes("section-char-season"),
        places=((NodeKind.CHARACTER, "This Season"),),
        in_section=lambda facts, section: (
            grog_season(facts, section) and grog_has_plan(facts)
        ),
    ),
    MoreAction(
        "invest_labor",
        "v",
        "Invest Time or Money",
        step=needs(character, labor.invest_form),
        refresh=changes(
            "section-char-season",
            "section-reputations",
            "section-inventory",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=works_for_labor(merchants.earns_labor),
    ),
    MoreAction(
        "discipline_grog",
        "r",
        "Reward or Punish",
        step=needs(character, grog_forms.discipline_form),
        refresh=changes(
            "section-personality-traits",
            "section-char-health",
            "section-char-info",
            tree=True,
        ),
        places=((NodeKind.CHARACTER, deeds.COVENFOLK),),
        on_record=on_covenfolk,
    ),
    MoreAction(
        "grog_pension",
        "n",
        "Pension",
        step=needs(character, grog_forms.pension_form),
        refresh=changes("section-char-info", tree=True),
        places=((NodeKind.CHARACTER, deeds.COVENFOLK),),
        on_record=on_covenfolk,
    ),
    MoreAction(
        "craft_by_magic",
        "f",
        "Craft by Magic",
        step=needs(character, craft_forms.craft_form),
        refresh=calculator(),
        section="section-known-spells",
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
    ),
    # A craftsman's sale of his finished goods (City & Guild).
    MoreAction(
        "sell_goods",
        "s",
        "Sell Finished Goods",
        step=needs(character, selling.sell_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=works_for_labor(lambda c: bool(selling.crafts(c))),
    ),
    # Art & Academe's ligatures and the apothecary's store.
    MoreAction(
        "make_ligature",
        "l",
        "Make a Ligature",
        step=needs(character, apothecary_forms.ligature_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SCHOLARLY),),
        on_record=makes_ligature,
    ),
    MoreAction(
        "apothecary_store",
        "o",
        "Apothecary's Store",
        step=needs(character, apothecary_forms.store_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=works_for_labor(apothecary.keeps_store),
    ),
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    MoreAction(
        "theban_letter",
        "e",
        "Hermetic Letter",
        step=needs(character, byzantine.letter_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.TRIBUNAL),),
        on_record=keeps_byzantine_custom(lambda _s, _c: True),
    ),
    MoreAction(
        "invoke_oath",
        "s",
        "Invoke a Broken Oath",
        step=needs(character, byzantine.oath_form),
        refresh=changes("section-vf-virtues", "section-vf-flaws", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.TRIBUNAL),),
        on_record=keeps_byzantine_custom(lambda _s, _c: True),
    ),
    MoreAction(
        "make_greek_fire",
        "f",
        "Make Greek Fire",
        step=needs(character, byzantine.greek_fire_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        on_record=keeps_byzantine_custom(lambda _s, _c: True),
    ),
    MoreAction(
        "paint_icon",
        "i",
        "Paint an Icon",
        step=needs(character, byzantine.icon_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_byzantine_custom(
            lambda saga, c: (
                byzantine_rules.icon_problem(c) is None
                and bool(theban_customs.church_list(saga))
            )
        ),
    ),
    MoreAction(
        "venerate_icon",
        "v",
        "Venerate an Icon",
        step=needs(character, byzantine.venerate_form),
        refresh=changes("section-char-health", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_byzantine_custom(
            lambda saga, _c: bool(theban_customs.icon_choices(saga))
        ),
    ),
    MoreAction(
        "mothers_curse",
        "a",
        "A Mother's Curse",
        step=needs(character, byzantine.curse_form),
        refresh=changes("section-vf-virtues", "section-vf-flaws", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_byzantine_custom(lambda _s, _c: True),
    ),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    MoreAction(
        "indulge_sin",
        "n",
        "Confidence through Sin",
        step=needs(character, sin_forms.sin_form),
        refresh=changes("section-char-info", "section-aging", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.INFERNAL),),
        on_record=sins,
    ),
    MoreAction(
        "infernal_influence",
        "u",
        "Infernal Influence",
        step=needs(character, sin_forms.influence_form),
        refresh=changes("section-char-info", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.INFERNAL),),
        on_record=influences,
    ),
    MoreAction(
        "ars_goetia",
        "g",
        "Ars Goetia",
        step=needs(character, goetic_forms.goetic_form),
        refresh=calculator(),
        places=((NodeKind.CHARACTER, deeds.INFERNAL),),
        on_record=works_goetia,
    ),
    MoreAction(
        "hunt_on_journey", "h", "The Hunt", on_page=False, in_section=plans_journey
    ),
    MoreAction(
        "area_lore_on_journey",
        "l",
        "Area Lore",
        on_page=False,
        in_section=plans_journey,
    ),
    # An apprentice's magic and the Gauntlet (Apprentices).
    MoreAction(
        "turbulence",
        "b",
        "Turbulence",
        step=needs(character, turbulence_forms.turbulence_form),
        refresh=changes("section-char-info", "section-char-season", "tab-diary"),
        places=(
            (NodeKind.CHARACTER, deeds.APPRENTICESHIP),
            (NodeKind.CHARACTER, deeds.SEASON_WORK),
        ),
        on_record=turbulent,
    ),
    MoreAction(
        "gauntlet",
        "u",
        "The Gauntlet",
        step=needs(character, gauntlet_forms.gauntlet_form),
        refresh=changes(
            "section-char-info",
            "section-vf-virtues",
            "section-vf-flaws",
            "tab-diary",
            tree=True,
        ),
        places=((NodeKind.CHARACTER, deeds.APPRENTICESHIP),),
        on_record=faces_gauntlet,
    ),
    MoreAction(
        "lose_the_gift",
        "z",
        "Lose the Gift",
        step=needs(character, gauntlet_forms.lose_gift_form),
        refresh=changes(
            "section-char-info", "section-vf-virtues", "section-vf-flaws", "tab-diary"
        ),
        places=((NodeKind.CHARACTER, deeds.APPRENTICESHIP),),
        on_record=may_lose_gift,
    ),
    MoreAction(
        "learn_cantation",
        "c",
        "Learn a Cantation",
        step=needs(character, gauntlet_forms.cantation_form),
        refresh=changes("section-known-spells", "tab-diary"),
        places=((NodeKind.CHARACTER, "Known Spells"),),
        on_record=learns_cantation,
    ),
    # Art & Academe's artists and scholars, between their seasons.
    MoreAction(
        "artist_career",
        "t",
        "An Artist's Career",
        step=needs(character, careers.artist_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        on_record=makes_art,
    ),
    MoreAction(
        "scholar_career",
        "k",
        "A Scholar's Career",
        step=needs(character, careers.scholar_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        on_record=studies,
    ),
    # Dealing with faeries: the Ars Fabulosa, bargains and offers (RoP: Faerie).
    MoreAction(
        "ars_fabulosa",
        "y",
        "Ars Fabulosa",
        step=needs(character, faerie_forms.ars_fabulosa_form),
        refresh=changes(
            "section-char-health", "section-personality-traits", "tab-diary"
        ),
        places=((NodeKind.CHARACTER, deeds.FAERIE),),
        on_record=bargains_with_faeries,
    ),
    MoreAction(
        "faerie_bargain",
        "q",
        "A Faerie Bargain",
        step=needs(character, faerie_forms.faerie_bargain_form),
        refresh=changes("section-personality-traits", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.FAERIE),),
        on_record=bargains_with_faeries,
    ),
    MoreAction(
        "faerie_offer",
        "o",
        "An Offer to Faerie",
        step=needs(character, faerie_forms.faerie_offer_form),
        refresh=changes("section-char-health", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.FAERIE),),
        on_record=offers_to_faerie,
    ),
    # The lacuna and the pilgrim (HoH:S, The Church).
    MoreAction(
        "cast_in_lacuna",
        "m",
        "Cast in a Lacuna",
        step=needs(character, lacuna_forms.lacuna_form),
        refresh=calculator(),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        in_section=casts_in_lacuna,
    ),
    MoreAction(
        "pilgrimage",
        "j",
        "Pilgrimage",
        step=needs(character, pilgrimage_forms.pilgrimage_form),
        refresh=changes(
            "section-char-season",
            "section-vf-virtues",
            "section-vf-flaws",
            "section-personality-traits",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=goes_on_pilgrimage,
    ),
    # Devotion and the saints (The Church, RoP: The Divine).
    MoreAction(
        "invoke_saint",
        "w",
        "Invoke a Saint",
        step=needs(character, devotion_forms.invoke_form),
        refresh=changes(FAITH_SECTION, "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("invoke_saint", lambda s, _c: devotion_forms.invokes(s)),
    ),
    MoreAction(
        "threaten_saint",
        "x",
        "Threaten a Saint",
        step=needs(character, devotion_forms.threaten_form),
        refresh=changes(FAITH_SECTION, "section-personality-traits", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith(
            "threaten_saint", lambda s, _c: devotion_forms.threatens(s)
        ),
    ),
    MoreAction(
        "patron_saint",
        "p",
        "Patron Saint",
        step=needs(character, devotion_forms.patron_form),
        refresh=changes(FAITH_SECTION, "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("patron_saint", lambda s, _c: devotion_forms.invokes(s)),
    ),
    MoreAction(
        "devotion_points",
        "d",
        "Devotion Points",
        step=needs(character, devotion_forms.points_form),
        refresh=changes(FAITH_SECTION, "section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith(
            "devotion_points", lambda s, _c: devotion_forms.the_church(s)
        ),
    ),
    MoreAction(
        "act_of_piety",
        "g",
        "Indulgence, Vigil or Fast",
        step=needs(character, devotion_forms.piety_form),
        refresh=changes(
            "section-char-health",
            "section-personality-traits",
            "section-reputations",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith(
            "act_of_piety", lambda s, _c: devotion_forms.the_church(s)
        ),
    ),
    # A Muslim's baraka and the Hajj (RoP: The Divine).
    MoreAction(
        "invoke_baraka",
        "b",
        "Invoke Baraka",
        step=needs(character, baraka_forms.baraka_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("invoke_baraka", lambda s, _c: rop_divine(s)),
    ),
    MoreAction(
        "hajj",
        "j",
        "The Hajj",
        step=needs(character, baraka_forms.hajj_form),
        refresh=changes(
            FAITH_SECTION,
            "section-personality-traits",
            "section-char-info",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("hajj", lambda s, _c: rop_divine(s)),
    ),
    # Holy influence and tempers (RoP: The Divine).
    MoreAction(
        "holy_influence",
        "h",
        "Holy Influence",
        step=needs(character, holy_influence_forms.holy_influence_form),
        refresh=changes("section-char-info", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("holy_influence", lambda s, _c: rop_divine(s)),
    ),
    # Mystic paths, God's aid, the Font and the Commanding Aura (The
    # Church, RoP: The Divine, DE).
    MoreAction(
        "mystic_path",
        "k",
        "Mystic Path",
        step=needs(character, mystic_forms.mystic_path_form),
        refresh=changes(FAITH_SECTION, "section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("mystic_path", mystic_forms.offers_path),
    ),
    MoreAction(
        "spiritual_path",
        "q",
        "Spiritual Path",
        step=needs(character, mystic_forms.spiritual_path_form),
        refresh=changes(
            "section-char-season",
            "section-char-info",
            "section-vf-virtues",
            "section-vf-flaws",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("spiritual_path", mystic_forms.offers_spiritual),
    ),
    MoreAction(
        "monistic_revelation",
        "z",
        "Monistic Revelation",
        step=needs(character, mystic_forms.monistic_revelation_form),
        refresh=changes("section-vf-virtues", "section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("monistic_revelation", mystic_forms.offers_revelation),
    ),
    MoreAction(
        "gods_aid",
        "i",
        "Invoke God's Aid",
        step=needs(character, mystic_forms.gods_aid_form),
        refresh=changes("section-char-info", "tab-diary"),
        places=((NodeKind.CHARACTER, "Faith"),),
        on_record=keeps_faith("gods_aid", mystic_forms.offers_aid),
    ),
    MoreAction(
        "font_of_knowledge",
        "o",
        "Font of Knowledge",
        step=needs(character, mystic_forms.font_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.INSIGHT),),
        on_record=walks_in_faith(mystic_forms.offers_font),
    ),
    MoreAction(
        "commanding_aura",
        "c",
        "Commanding Aura",
        step=needs(character, mystic_forms.commanding_aura_form),
        refresh=changes("section-char-health", "tab-diary"),
        places=((NodeKind.CHARACTER, "Health"),),
        on_record=walks_in_faith(mystic_forms.offers_aura),
    ),
    # House Verditius's Hubris and vendettas (HoH:MC, DE).
    MoreAction(
        "verditius_hubris",
        "b",
        "Hubris",
        step=needs(character, hubris_forms.hubris_form),
        refresh=changes(
            "section-personality-traits", "section-reputations", "tab-diary"
        ),
        places=((NodeKind.CHARACTER, "Personality Traits"),),
        on_record=is_proud,
    ),
    # Hermetic spirit magic and theurgy (The Mysteries Revised Edition).
    MoreAction(
        "spirits_and_names",
        "y",
        "Spirits and Names",
        step=needs(character, tmre_spirit_forms.spirits_form),
        refresh=calculator(),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        on_record=works_with_spirits,
    ),
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    MoreAction(
        "dream_working",
        "v",
        "Dream Working",
        step=needs(character, tmre_dream_forms.dream_form),
        refresh=changes("section-known-spells", "tab-diary"),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        on_record=on_known_spells(tmre_dream_forms.offers_dreams),
    ),
    MoreAction(
        "hermetic_sacrifice",
        "a",
        "Hermetic Sacrifice",
        step=needs(character, tmre_dream_forms.sacrifice_form),
        refresh=changes("section-known-spells", "tab-diary"),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        on_record=on_known_spells(tmre_dream_forms.offers_sacrifice),
    ),
    # A certamen duel with another magus (DE pp. 231-233).
    MoreAction(
        "certamen_duel",
        "z",
        "Certamen",
        step=needs(character, certamen_forms.duel_form),
        refresh=changes("section-known-spells", "tab-diary"),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        on_record=on_known_spells(certamen_forms.offers),
    ),
    # Where a character is now: the aura his casting counts.
    MoreAction(
        "whereabouts",
        "h",
        "Current Location",
        step=needs(character, whereabouts_forms.where_form),
        refresh=changes("section-casting"),
        section="section-casting",
        places=((NodeKind.CHARACTER, "Current Location"),),
    ),
    # A stay as a guest at another covenant (DE pp. 381, 518).
    MoreAction(
        "guest_stay",
        "u",
        "Stay as Guest",
        step=needs(character, guest_stays.stay_form),
        refresh=changes("section-casting"),
        section="section-casting",
        places=((NodeKind.CHARACTER, "Current Location"),),
    ),
    # Divination and Hermetic astrology (The Mysteries Revised Edition).
    MoreAction(
        "tmre_divination",
        "n",
        "Divination",
        step=needs(character, tmre_divination_forms.divination_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.INSIGHT),),
        on_record=reads_signs(tmre_divination_forms.offers_divination),
    ),
    MoreAction(
        "tmre_astrology",
        "s",
        "Astrology",
        step=needs(character, tmre_divination_forms.astrology_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.INSIGHT),),
        on_record=reads_signs(tmre_divination_forms.offers_astrology),
    ),
    # House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).
    MoreAction(
        "house_acclaim",
        "h",
        "House Acclaim",
        step=needs(character, acclaim_forms.acclaim_form),
        refresh=changes("section-reputations", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SESSION),),
        on_record=keeps_acclaim,
    ),
    MoreAction(
        "reputation_roll",
        "r",
        "Reputation Roll",
        step=needs(character, acclaim_forms.roll_form),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SESSION),),
        on_record=has_reputation,
    ),
    # Philosophic Alchemy's digestions (The Mysteries Revised Edition).
    MoreAction(
        "philosophic_alchemy",
        "q",
        "Philosophic Alchemy",
        step=needs(character, tmre_alchemy_forms.digestion_form),
        refresh=changes("section-char-season", "tab-diary"),
        places=((NodeKind.CHARACTER, deeds.SEASON_WORK),),
        in_section=works_for_labor(
            lambda c: bool(tmre_alchemy_rules.philosophic_tier(c))
        ),
    ),
    # The Great Elixir's test (The Mysteries Revised Edition).
    MoreAction(
        "great_elixir",
        "x",
        "Test the Great Elixir",
        step=needs(character, tmre_alchemy_forms.great_elixir_form),
        refresh=changes("section-aging", "tab-diary"),
        places=((NodeKind.CHARACTER, "Aging"),),
        in_section=lambda facts, section: (
            section == "section-aging"
            and facts.selected_character is not None
            and tmre_alchemy_rules.has_great_elixir(facts.selected_character)
        ),
    ),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    MoreAction(
        "change_virtues_flaws",
        "g",
        "Gain or Lose in Play",
        step=needs(character, vf_change_forms.change_form),
        refresh=changes(
            "section-vf-virtues",
            "section-vf-flaws",
            "section-char-characteristics",
            "tab-diary",
        ),
        places=((NodeKind.CHARACTER, "Virtues & Flaws"),),
        in_section=lambda facts, section: (
            section in ("section-vf-virtues", "section-vf-flaws")
            and facts.selected_kind == NodeKind.CHARACTER
            and facts.selected_character is not None
        ),
    ),
    # A cleric's career (The Church).
    MoreAction(
        "perform_exorcism",
        "x",
        "Perform an Exorcism",
        step=needs(character, church_forms.exorcism_step),
        refresh=changes("tab-diary"),
        section="section-char-orders",
        on_page=False,
        on_record=exorcises,
    ),
    # Saga Content's Mystery Cults.
    MoreAction(
        "experiment_script",
        "y",
        "Experiment on a Script",
        step=needs(character, cult_forms.mystagogue_experiment),
        refresh=changes("tab-diary"),
        places=((NodeKind.CHARACTER, deeds.MYSTERY_CULTS),),
        on_record=experiments,
    ),
    MoreAction(
        "open_tunnel",
        "o",
        "Open a Tunnel",
        step=needs(character, tunnel_forms.tunnel_form),
        refresh=calculator(),
        places=((NodeKind.CHARACTER, "Magic Outside the Lab"),),
        on_record=on_known_spells(tunnel_forms.offers),
    ),
    # A Criamon magus's path: plan the next avenue (HoH:MC pp. 58-73).
    MoreAction(
        "follow_avenue",
        "v",
        "Follow an Avenue",
        step=needs(character, criamon_forms.avenue_step),
        refresh=changes(
            "section-char-criamon-path",
            "section-char-ahead",
            "tab-planning",
            "tab-diary",
        ),
        section="section-char-criamon-path",
        on_page=False,
    ),
)
