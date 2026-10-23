"""Virtues and Flaws during a season of study: Advancement Total
multipliers, experience shared with other subjects, Study Bonus and Study
Requirement, what a character can't learn, Master of None, and the working
seasons a companion owes."""

from ars_magica_manager import seasons
from ars_magica_manager.arts import FORMS, TECHNIQUES
from ars_magica_manager.commands import Form, Picked, Refuse
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Covenant,
    KnownSpell,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import study
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params=params)


def _magus(*virtues: VirtueFlawInstance, type: str = "magus") -> Character:
    magus = Character(id="tib", name="Tiberius", type=type, covenant_id="cov")
    magus.abilities = [
        Ability("Latin", xp=ability_xp(4)),
        Ability("Living Language: French", xp=ability_xp(5)),
        Ability("Magic Lore", xp=ability_xp(1)),
        Ability("Ride", xp=ability_xp(2)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(4)), "auram": ArtScore(xp=art_xp(2))}
    magus.raw_vis = {"creo": 3, "ignem": 3}
    magus.virtues_flaws = list(virtues)
    return magus


def _saga(*virtues: VirtueFlawInstance, type: str = "magus") -> Saga:
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep")],
        characters=[_magus(*virtues, type=type)],
    )
    saga.books = [
        Book(
            "ignem",
            "De Ignis",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Ignem",
            level=20,
            quality=13,
        ),
        Book(
            "creo",
            "De Creatione",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Creo",
            level=20,
            quality=10,
        ),
        Book(
            "lore",
            "Of Spirits",
            "Ability Summa",
            owner_kind="covenant",
            owner_id="cov",
            ability="Magic Lore",
            level=6,
            quality=9,
        ),
    ]
    return saga


def _plan(activity: str, *subjects: str, season="Spring", **kw) -> SeasonPlan:
    return SeasonPlan(
        "tib", 1220, season, activity, [XpAllocation(s) for s in subjects], **kw
    )


def _xp(saga: Saga, plan: SeasonPlan) -> dict[str, int]:
    worked = rules.outcome(saga.characters[0], plan, saga)
    assert worked.ok, worked.problems
    return {g.subject: g.result.xp for g in worked.gains}


def _problems(saga: Saga, plan: SeasonPlan) -> list[str]:
    return rules.outcome(saga.characters[0], plan, saga).problems


# -- Advancement Total multipliers ---------------------------------------------


def test_linguist_raises_a_languages_advancement_total_by_a_quarter_rounded_up():
    student = _magus(_vf("vf_linguist"))
    result = study.season_of_study(
        student, "Living Language: French", 9, activity="reading", is_art=False
    )
    assert (result.advancement_total, result.xp) == (12, 12)  # 11.25 -> 12
    other = study.season_of_study(student, "Latin", 9, activity="reading", is_art=False)
    assert other.xp == 9


def test_savantism_halves_every_advancement_total_but_the_favoured_abilitys():
    student = _magus(_vf("vf_savantism", ability="ride"))
    halved = study.season_of_study(
        student, "Latin", 9, activity="reading", is_art=False
    )
    assert halved.xp == 4  # rounded down
    favoured = study.season_of_study(
        student, "Ride", 9, activity="practice", is_art=False
    )
    assert favoured.xp == 9


def test_flawless_magic_doubles_and_loose_magic_halves_spell_mastery():
    saga = _saga(_vf("vf_flawless_magic"))
    saga.characters[0].spells_known = [KnownSpell("pilum")]
    assert _xp(saga, _plan(rules.PRACTICE, "mastery:pilum")) == {"mastery:pilum": 10}
    assert _xp(saga, _plan(rules.PRACTICE, "ability:Latin")) == {"ability:Latin": 4}
    saga.characters[0].virtues_flaws = [_vf("vf_loose_magic")]
    assert _xp(saga, _plan(rules.PRACTICE, "mastery:pilum")) == {"mastery:pilum": 2}


def test_the_gain_line_names_the_terms_that_changed_it():
    saga = _saga(_vf("vf_linguist"))
    plan = _plan(rules.PRACTICE, "ability:Living Language: French")
    text = seasons.live_text(saga, saga.characters[0], plan)
    assert "Advancement Total 5 (Linguist x1.25)" in text


# -- experience shared with other subjects -------------------------------------


def test_elemental_magic_gives_half_the_source_quality_to_the_other_elements():
    # The book's example: Ignem from a Quality 13 book, 7 xp in each other.
    saga = _saga(_vf("vf_elemental_magic"))
    gains = _xp(saga, _plan(rules.READ, book_id="ignem"))
    assert gains == {"art:Ignem": 13, "art:Aquam": 7, "art:Auram": 7, "art:Terram": 7}
    assert _xp(saga, _plan(rules.READ, book_id="creo")) == {"art:Creo": 10}


def test_secondary_insight_gives_one_xp_in_the_arts_chosen_or_the_lowest():
    saga = _saga(_vf("vf_secondary_insight"))
    chosen = _plan(
        rules.READ, book_id="creo", insight_arts=["Ignem", "Vim", "Aquam", "Mentem"]
    )
    gains = _xp(saga, chosen)
    assert gains == {
        "art:Creo": 10,
        "art:Ignem": 1,
        "art:Vim": 1,
        "art:Aquam": 1,
        "art:Mentem": 1,
    }
    # None named: the four lowest Forms (Auram has 3 xp, so it isn't one).
    picked = _xp(saga, _plan(rules.READ, book_id="creo"))
    assert set(picked) - {"art:Creo"} == {
        "art:Animal",
        "art:Aquam",
        "art:Corpus",
        "art:Herbam",
    }
    # A Form gives two Techniques; a Technique named for it doesn't count.
    form = _xp(saga, _plan(rules.READ, book_id="ignem", insight_arts=["Auram", "Rego"]))
    assert form == {"art:Ignem": 13, "art:Rego": 1, "art:Intellego": 1}


def test_shared_experience_is_applied_and_named_in_the_diary():
    saga = _saga(_vf("vf_elemental_magic"))
    seasons.set_plan(saga, _plan(rules.READ, book_id="ignem"))
    seasons.apply(saga, seasons.resolve(saga))
    magus = saga.characters[0]
    assert magus.arts["terram"].xp == 7
    assert "Terram: +7 xp from Elemental Magic" in magus.diary[-1].details


def test_hermetic_sorcery_gives_half_a_lores_xp_in_vim():
    saga = _saga(_vf("vf_hermetic_sorcery"))
    assert _xp(saga, _plan(rules.READ, book_id="lore")) == {
        "ability:Magic Lore": 9,
        "art:Vim": 4,
    }


def test_magian_lineage_shares_half_with_its_connected_abilities():
    saga = _saga(
        _vf(
            "vf_magian_lineage_major",
            connected="Magic Lore, Dominion Lore, Second Sight",
        )
    )
    gains = rules.outcome(
        saga.characters[0], _plan(rules.READ, book_id="lore"), saga
    ).gains
    assert {g.subject: g.result.xp for g in gains} == {
        "ability:Magic Lore": 9,
        "ability:Dominion Lore": 5,
        "ability:Second Sight": 0,  # a Supernatural Ability not yet open
    }
    assert "lost" in gains[-1].result.notes[0]


# -- where the season is spent -------------------------------------------------


def test_study_bonus_adds_two_when_the_art_is_present():
    saga = _saga(_vf("vf_study_bonus"))
    assert _xp(saga, _plan(rules.READ, book_id="creo")) == {"art:Creo": 10}
    present = _plan(rules.READ, book_id="creo", art_present=True)
    assert _xp(saga, present) == {"art:Creo": 12}
    vis = _plan(rules.VIS_STUDY, "art:Creo", die=5, art_present=True)
    assert _xp(saga, vis) == {"art:Creo": 7}


def test_study_requirement_refuses_an_art_away_from_its_substance():
    saga = _saga(_vf("vf_study_requirement"))
    assert "Study Requirement" in _problems(saga, _plan(rules.READ, book_id="creo"))[0]
    assert _xp(saga, _plan(rules.READ, book_id="creo", art_present=True))
    assert not _problems(saga, _plan(rules.READ, book_id="lore"))


# -- what a character can't learn ----------------------------------------------


def test_ability_block_rules_out_the_abilities_or_category_it_names():
    saga = _saga(_vf("vf_ability_block", abilities="Arcane"))
    assert "Ability Block" in _problems(saga, _plan(rules.READ, book_id="lore"))[0]
    assert not _problems(saga, _plan(rules.PRACTICE, "ability:Latin"))
    saga.characters[0].virtues_flaws = [_vf("vf_ability_block", abilities="Latin")]
    assert _problems(saga, _plan(rules.PRACTICE, "ability:Latin"))


def test_restricted_learning_needs_a_teacher_beyond_its_five():
    saga = _saga(_vf("vf_restricted_learning", chosen="Latin, Ride"), type="companion")
    assert not _problems(saga, _plan(rules.PRACTICE, "ability:Latin"))
    refused = _problems(saga, _plan(rules.PRACTICE, "ability:Magic Lore"))
    assert "Restricted Learning" in refused[0]


# -- Master of None ------------------------------------------------------------


def test_master_of_none_loses_xp_in_a_subject_already_raised_this_year():
    saga = _saga(_vf("vf_master_of_none"), _vf("vf_secondary_insight"))
    seasons.set_plan(saga, _plan(rules.PRACTICE, "ability:Latin"))
    later = _plan(rules.PRACTICE, "ability:Latin", season="Summer")
    seasons.set_plan(saga, later)
    # Planned before Spring is played, Summer's practice already counts it.
    assert _xp(saga, later) == {"ability:Latin": 0}
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.characters[0].advanced == {"ability:Latin": 1220}
    assert _xp(saga, later) == {"ability:Latin": 0}
    assert _xp(saga, _plan(rules.PRACTICE, "ability:Ride", season="Summer"))
    # Next year it can be raised again.
    next_year = SeasonPlan(
        "tib", 1221, "Spring", rules.PRACTICE, [XpAllocation("ability:Latin")]
    )
    assert _xp(saga, next_year) == {"ability:Latin": 4}


# -- working seasons -----------------------------------------------------------


def test_wealthy_poor_and_license_of_absence_change_the_working_seasons():
    companion = _magus(type="companion")
    assert rules.working_seasons(companion) == 2
    companion.virtues_flaws = [_vf("vf_wealthy")]
    assert rules.working_seasons(companion) == 1
    companion.virtues_flaws = [_vf("vf_poor")]
    assert rules.working_seasons(companion) == 3
    companion.virtues_flaws = [_vf("vf_wealthy"), _vf("vf_license_of_absence")]
    assert rules.working_seasons(companion) == 0


# -- the plan form -------------------------------------------------------------


def test_the_plan_form_asks_only_holders_of_the_virtues():
    saga = _saga()
    keys = {f.key for f in season_forms.study_fields(saga, saga.characters[0], None)}
    assert not {"art_present", "insight_arts"} & keys
    saga.characters[0].virtues_flaws = [
        _vf("vf_study_bonus"),
        _vf("vf_secondary_insight"),
    ]
    keys = {f.key for f in season_forms.study_fields(saga, saga.characters[0], None)}
    assert {"art_present", "insight_arts"} <= keys
    values = {"activity": rules.READ, "book_id": "creo", "art_present": True}
    plan = season_forms.season_plan_from(
        saga, saga.characters[0], {**values, "insight_arts": ["Ignem", "Vim"]}
    )
    assert (plan.art_present, plan.insight_arts) == (True, ["Ignem", "Vim"])


def test_secondary_insights_grid_offers_the_other_kind_of_art_up_to_its_count():
    saga = _saga(_vf("vf_secondary_insight"))
    magus = saga.characters[0]
    grid = season_forms.insight_choice(
        saga, magus, ["Ignem"], {"activity": rules.READ, "book_id": "creo"}
    )
    assert isinstance(grid, Form)
    fields = {f.key: f for f in grid.fields()}
    # Studying Creo, a Technique: the ten Forms, Creo itself not among them.
    assert set(fields) - {"studied"} == set(FORMS)
    assert fields["Auram"].label == "Auram (2)" and fields["Ignem"].value is True
    five = {art: True for art in FORMS[:5]}
    assert grid.validate is not None and "no more than 4" in grid.validate(five)
    assert grid.apply({"Vim": True, "Aquam": True}) == Picked(["Aquam", "Vim"])
    # A Form gives two Techniques.
    form_grid = season_forms.insight_choice(
        saga, magus, None, {"activity": rules.VIS_STUDY, "subject_1": "art:Ignem"}
    )
    assert isinstance(form_grid, Form)
    assert {f.key for f in form_grid.fields()} - {"studied"} == set(TECHNIQUES)
    # Nothing studied yet: nothing to tick.
    refused = season_forms.insight_choice(saga, magus, None, {"activity": rules.READ})
    assert isinstance(refused, Refuse)
