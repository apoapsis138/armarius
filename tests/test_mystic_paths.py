"""Mystic paths and the Divine: contemplative and monistic mysticism, the
Spiritual Path, the monist's Revelations and True Faith's gifts (The
Church pp. 19-24, with Realms of Power: The Divine pp. 40, 63-64),
invoking God's aid (RoP: The Divine pp. 41-42), Font of Knowledge (DE p.
165; Antagonists p. 109) and the Commanding Aura withdrawn (DE pp. 74,
420; Antagonists p. 38)."""

import random
from dataclasses import replace

import pytest

from ars_magica_manager import mystic_paths as forms
from ars_magica_manager import seasons
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Aging,
    Character,
    Characteristics,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import derived, penetration
from ars_magica_manager.rules import devotion as dv
from ars_magica_manager.rules import divine_state as ds
from ars_magica_manager.rules import font_of_knowledge as fok
from ars_magica_manager.rules import gods_aid as aid
from ars_magica_manager.rules import mysticism as my
from ars_magica_manager.rules.season_work import mysticism as path_seasons
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.sections import FAITH_SECTION


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _clara(pious: int = 3) -> Character:
    """A lay mystic: Pious +3, Sense Holiness and Unholiness 1,
    Concentration 4, Intelligence +2."""
    clara = Character(id="c", name="Clara", type="companion")
    clara.characteristics = Characteristics(intelligence=2, communication=1, presence=1)
    clara.abilities = [
        Ability("Sense Holiness and Unholiness", "Supernatural", xp=ability_xp(1)),
        Ability("Concentration", xp=ability_xp(4)),
        Ability("Dominion Lore", xp=ability_xp(2)),
    ]
    clara.personality_traits = [ScoredTrait("Pious", pious)]
    clara.background.confidence_score = 1
    clara.background.confidence_points = 3
    clara.aging = Aging()
    return clara


def _saga(*books: str) -> Saga:
    saga = Saga(
        id="s",
        name="S",
        characters=[_clara()],
        books_in_play=list(books) or ["TC", "RoP:D"],
    )
    saga.current_season, saga.current_year = "Spring", 1220
    return saga


def _form(command) -> Form:
    assert isinstance(command, Form)
    return command


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields()}
    values.update(changes)
    return values


# -- the paths (TC pp. 21, 23) --


def test_a_contemplative_needs_piety_no_sin_and_a_tie_to_the_divine():
    clara = _clara()
    assert my.path_problems(clara, my.CONTEMPLATIVE) == []
    assert my.divine_ties(clara) == ["Sense Holiness and Unholiness"]
    clara.personality_traits.append(ScoredTrait("Proud", 2))
    assert "leans to Proud" in my.path_problems(clara, my.CONTEMPLATIVE)[0]
    impious = _clara(pious=0)
    assert any(
        "positive Pious" in p for p in my.path_problems(impious, my.CONTEMPLATIVE)
    )
    impious.abilities = []
    assert any(
        "tied to the Divine" in p for p in my.path_problems(impious, my.CONTEMPLATIVE)
    )
    # Warping from a Divine source is a tie too.
    impious.aging.warping_realms = {"Divine": 1}
    assert "Divine Warping" in my.divine_ties(impious)


def test_a_monist_needs_visions_or_true_faith():
    clara = _clara()
    assert any("Visions" in p for p in my.path_problems(clara, my.MONISTIC))
    clara.virtues_flaws.append(VirtueFlawInstance("vf_visions"))
    assert my.path_problems(clara, my.MONISTIC) == []


def test_the_mystic_path_form_follows_and_keeps_the_path():
    saga = _saga()
    clara = saga.character("c")
    form = _form(forms.mystic_path_form(saga, clara))
    assert form.validate is not None
    values = _values(form, path=my.CONTEMPLATIVE)
    assert form.validate(values) is None
    assert form.live is not None and "Divine Form" in form.live(values)
    form.apply(values)
    assert ds.path(clara) == my.CONTEMPLATIVE
    assert clara.diary[-1].name == "Mystic Path"
    assert "already" in str(form.validate(values))
    # After an Ascent the form stays for life.
    ds.note_ascent(clara)
    assert "stays for life" in str(form.validate(_values(form, path=forms.NONE)))
    assert "stays for life" in my.path_problems(clara, my.MONISTIC)[-1]


# -- the Spiritual Path (TC p. 22) --


def test_quest_components_must_reach_the_path_total():
    # TC p. 22: the components reach the Path Total; Pious isn't taken off.
    assert [r.total for r in my.REVELATIONS.values()] == [15, 18, 27, 30]
    clara = _saga().character("c")
    assert my.begin(clara, "Premonitions", "major_virtue").target == 30


def test_true_faith_is_never_a_revelation():
    saga = _saga()
    clara = saga.character("c")
    for key in my.REVELATIONS:
        ids = {d.id for d in my.revelations(clara, forms._catalog(saga), key)}
        assert my.TRUE_FAITH not in ids
    ds.set_path(clara, my.CONTEMPLATIVE)
    assert "never a Revelation" in str(my.begin_problem(clara, "True Faith"))


def test_a_spiritual_path_is_walked_and_its_revelation_claimed():
    saga = _saga()
    clara = saga.character("c")
    ds.set_path(clara, my.CONTEMPLATIVE)
    form = _form(forms.spiritual_path_form(saga, clara))
    begin = _values(
        form, what=forms.BEGIN, kind="minor_holy", virtue_minor_holy="vf_premonitions"
    )
    assert form.validate is not None and form.validate(begin) is None
    form.apply(begin)
    [record] = my.spiritual_paths(clara)
    assert (record.name, record.target) == ("Premonitions", 15)
    form = _form(forms.spiritual_path_form(saga, clara))
    vow = _values(form, what=forms.COUNT, component="vow", vow="to eat no meat")
    assert form.validate is not None and form.validate(vow) is None
    form.apply(vow)
    assert record.points == 6
    assert any(vf.vf_id == "vf_vow" for vf in clara.virtues_flaws)
    form.apply(_values(form, what=forms.COUNT, component="quest"))
    assert not record.done and record.points == 12
    form.apply(_values(form, what=forms.COUNT, component="quest"))
    assert record.done and record.points == 18
    claim = _values(form, what=forms.CLAIM, record="Premonitions")
    assert form.validate(claim) is None
    form.apply(claim)
    assert any(vf.vf_id == "vf_premonitions" for vf in clara.virtues_flaws)
    premonitions = next(a for a in clara.abilities if a.name == "Premonitions")
    assert premonitions.level == 1
    assert my.spiritual_paths(clara) == []


def test_alms_and_the_cross():
    saga = _saga()
    clara = saga.character("c")
    clara.virtues_flaws.append(VirtueFlawInstance("vf_wealthy"))
    ds.set_path(clara, my.CONTEMPLATIVE)
    my.begin(clara, "Premonitions", "major_virtue")
    form = _form(forms.spiritual_path_form(saga, clara))
    form.apply(_values(form, what=forms.COUNT, component="alms"))
    assert not any(vf.vf_id == "vf_wealthy" for vf in clara.virtues_flaws)
    form.apply(_values(form, what=forms.COUNT, component="alms"))
    assert any(vf.vf_id == "vf_poor" for vf in clara.virtues_flaws)
    assert form.validate is not None
    assert "Poor already" in str(
        form.validate(_values(form, what=forms.COUNT, component="alms"))
    )
    faith = clara.background.faith_points
    form.apply(_values(form, what=forms.COUNT, component="crusade"))
    assert clara.background.faith_points == faith + 1


def _plan(saga: Saga, activity: str, title: str, details: str = "") -> SeasonPlan:
    return SeasonPlan(
        "c",
        saga.current_year,
        saga.current_season,
        activity,
        [XpAllocation("ability:Dominion Lore")],
        title=title,
        details=details,
    )


def test_seasons_on_the_path_count_and_preaching_counts_once():
    saga = _saga()
    clara = saga.character("c")
    ds.set_path(clara, my.CONTEMPLATIVE)
    dv.set_patron(clara, "Saint Clare")
    record = my.begin(clara, "Premonitions", "minor_holy")
    seasons.set_plan(saga, _plan(saga, "path_devotion", "Premonitions"))
    seasons.apply(saga, seasons.resolve(saga))
    assert record.points == 1
    assert dv.devotion(clara, "Saint Clare") is not None
    assert dv.devotion(clara, "Saint Clare").points == 1
    seasons.set_plan(saga, _plan(saga, "path_preaching", "Premonitions"))
    seasons.apply(saga, seasons.resolve(saga))
    assert record.points == 4
    assert path_seasons.preached(clara, "Premonitions")
    again = _plan(saga, "path_preaching", "Premonitions")
    assert any(
        "once" in p for p in path_seasons._check("preaching")(saga, clara, again)
    )
    unnamed = _plan(saga, "path_service", "Nothing")
    assert any(
        "Name the Spiritual Path" in p
        for p in path_seasons._check("service")(saga, clara, unnamed)
    )


# -- the Divine Ascent of the mystics (TC pp. 20-24) --


def test_a_monist_ascends_at_one_point_to_the_gloom():
    saga = _saga()
    clara = saga.character("c")
    ds.set_path(clara, my.MONISTIC)
    assert ds.trigger(clara) == 1
    # Her die 2: 1 + 4 + 2 = 7; theirs 9: 0 + 1 + 0 + 0 + 9 = 10.
    notes = seasons.gain_warping(saga, clara, 1, Faces(2, 9), aura=0, realm="Divine")
    assert any("Divine Gloom" in line for line in notes)
    assert ds.ascents(clara) == 1 and ds.divine_gloom(clara)
    assert clara.diary[-1].name == "Divine Ascent"
    assert any("Monistic Revelation" in line for line in notes)
    assert any("4 experience point(s)" in line for line in notes)  # 1 + 3 margin
    later = seasons.gain_warping(saga, clara, 1, Faces(9, 0), aura=0, realm="Divine")
    assert any("1 experience point(s)" in line for line in later)


def test_a_contemplative_ascends_to_the_divine_form():
    saga = _saga()
    clara = saga.character("c")
    clara.virtues_flaws.append(VirtueFlawInstance("vf_true_faith"))
    clara.background.true_faith_score = 1
    ds.set_path(clara, my.CONTEMPLATIVE)
    assert ds.trigger(clara) == 2
    seasons.gain_warping(saga, clara, 1, Faces(2, 9), aura=0, realm="Divine")
    assert ds.ascents(clara) == 0  # one point: no test
    seasons.gain_warping(saga, clara, 2, Faces(2, 9), aura=0, realm="Divine")
    assert ds.divine_form(clara)
    warping = clara.aging.warping_score
    assert warping >= 1
    assert penetration.faith_magic_resistance(clara) == 10 + warping
    assert "Divine Form" in penetration.resistance_from(clara)
    assert ds.form_soak(clara) == (10 + warping) // 5
    assert any(
        line.label == "Divine Form" and line.amount == ds.form_soak(clara)
        for line in derived.soak(clara).lines
    )
    assert ds.form_penetration(clara) == warping + 5
    assert ds.impious_botch_dice(clara) == 3 * warping


def test_without_true_faith_the_divine_form_soaks_a_fifth_of_warping():
    clara = _clara()
    ds.set_path(clara, my.CONTEMPLATIVE)
    ds.note_ascent(clara)
    clara.aging.warping_score = 6
    assert ds.form_resistance(clara) == 0
    assert ds.form_soak(clara) == 1


def test_a_monist_practises_holy_abilities_at_his_concentration():
    clara = _clara()
    assert my.practice_xp(clara, "Sense Holiness and Unholiness") == 4
    ds.set_path(clara, my.MONISTIC)
    clara.abilities[1].xp = ability_xp(8)
    assert my.practice_xp(clara, "Sense Holiness and Unholiness") == 8
    assert my.practice_xp(clara, "Dominion Lore") == 4


# -- the monist's Revelations (TC p. 24) --


def test_the_first_revelation_is_second_sight():
    saga = _saga()
    clara = saga.character("c")
    ds.set_path(clara, my.MONISTIC)
    ds.note_ascent(clara)
    form = _form(forms.monistic_revelation_form(saga, clara, Faces(9, 2)))
    values = _values(form, points=3, choice=my.MINOR_VIRTUE)
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert any(vf.vf_id == "vf_second_sight" for vf in clara.virtues_flaws)
    assert not my.first_revelation(clara)


def test_revelations_need_their_warping_points_and_order():
    clara = _clara()
    ds.set_path(clara, my.MONISTIC)
    assert "had none" in str(my.integration_problem(clara, my.KEEP_MUNDANE, 1))
    ds.note_ascent(clara)
    assert my.integration_problem(clara, my.KEEP_MUNDANE, 1) is None
    assert "needs 5" in str(my.integration_problem(clara, my.MAJOR_VIRTUE, 4))
    assert "needs 7" in str(my.integration_problem(clara, my.REALM_LORE, 6, "Magic"))
    assert "both" in str(my.integration_problem(clara, my.INFERNAL_LORE, 7))
    my.note_revelation(clara, "Magic Lore")
    my.note_revelation(clara, "Faerie Lore")
    assert "already" in str(my.integration_problem(clara, my.REALM_LORE, 7, "Magic"))
    assert my.integration_problem(clara, my.INFERNAL_LORE, 7) is None
    assert my.lore_realms(clara) == ["Magic", "Faerie"]


def test_a_failed_integration_brings_only_the_gloom():
    saga = _saga()
    clara = saga.character("c")
    ds.set_path(clara, my.MONISTIC)
    ds.note_ascent(clara)
    clara.aging.warping_score = 9
    form = _form(forms.monistic_revelation_form(saga, clara, Faces(2, 9)))
    form.apply(_values(form, points=1, choice=my.KEEP_MUNDANE))
    assert "no Revelation" in clara.diary[-1].details


# -- True Faith as it rises (TC p. 23) --


def test_true_faith_brings_gifts_as_it_rises():
    assert my.faith_gifts(1) == []
    assert len(my.faith_gifts(3)) == 2
    assert "Empyreal" in my.faith_gifts(5)[-1]
    assert (my.faith_point_bonus(2), my.faith_point_bonus(3)) == (3, 6)


# -- God's aid (RoP: The Divine pp. 41-42) --


def test_gods_aid_rolls_communication_and_dominion_lore():
    clara = _clara()
    assert aid.total(clara) == 1 + 2
    clara.abilities.append(Ability("Ceremony", "Supernatural", xp=ability_xp(2)))
    assert aid.total(clara, ceremony=True, others=4) == 3 + 2 + 4
    assert aid.bonus(14) == 1 and aid.bonus(24) == 3
    assert "infidels" in aid.war_problem(aid.BELIEVER)


def test_gods_aid_spends_a_point_and_its_zero_rolls_three_botch_dice():
    saga = _saga()
    clara = saga.character("c")
    form = _form(forms.gods_aid_form(saga, clara, Faces(9)))
    values = _values(form, aim="the fight")
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert clara.background.confidence_points == 2
    assert "+1 to his rolls toward the fight" in clara.diary[-1].details
    botched = _form(forms.gods_aid_form(saga, clara, Faces(0, 0, 5, 5)))
    botched.apply(_values(botched, aim="the vote"))
    assert "A botch (1 zero(s))" in clara.diary[-1].details


def test_gods_aid_is_refused_a_grog_and_against_believers():
    saga = _saga()
    clara = saga.character("c")
    form = _form(forms.gods_aid_form(saga, clara))
    assert form.validate is not None
    assert "infidels" in str(
        form.validate(_values(form, aim="x", war=True, foe=aid.BELIEVER))
    )
    clara.type = "grog"
    assert "Confidence" in str(form.validate(_values(form, aim="x")))


def test_the_odds_of_a_stress_die():
    assert aid.stress_chance(0, 1) == pytest.approx(0.9)
    assert aid.stress_chance(0, 10) == pytest.approx(0.069)
    assert aid.stress_chance(5, 3) == 1.0
    assert 0.5 < aid.opposed_chance(0, 0) < 0.6


# -- Font of Knowledge (DE p. 165; Antagonists p. 109) --


def test_font_of_knowledge_rises_with_each_use():
    clara = _clara()
    clara.abilities.append(
        Ability("Font of Knowledge", "Supernatural", xp=ability_xp(3))
    )
    assert fok.holds(clara)
    assert (fok.ease(0), fok.ease(2)) == (6, 12)
    assert fok.total(clara) == 2 + 3
    assert fok.untrained(clara, "Magic Lore")
    assert not fok.untrained(clara, "Concentration")


def test_the_font_form_rolls_against_the_days_uses():
    saga = _saga()
    clara = saga.character("c")
    clara.abilities.append(
        Ability("Font of Knowledge", "Supernatural", xp=ability_xp(1))
    )
    form = _form(forms.font_form(saga, clara, Faces(9)))
    values = _values(form, ability="Magic Lore", uses=1)
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert "may use Magic Lore at 2" in clara.diary[-1].details
    assert "already" in str(form.validate(_values(form, ability="Concentration")))


# -- the Commanding Aura (DE pp. 74, 420; RoP: The Divine p. 43) --


def test_a_withdrawn_commanding_aura_gives_nothing():
    saga = _saga()
    clara = saga.character("c")
    clara.background.church_rank = "Legatus missus"
    assert penetration.office_resistance(clara) == 15
    form = _form(forms.commanding_aura_form(saga, clara))
    form.apply(_values(form, withdrawn=True, why="he lingered in Bologna"))
    assert ds.aura_withdrawn(clara)
    assert penetration.office_resistance(clara) == 0
    assert not any(line.label == "Legatus missus" for line in derived.soak(clara).lines)
    assert form.validate is not None
    assert "Nothing changes" in str(form.validate(_values(form, withdrawn=True)))
    form.apply(_values(form, withdrawn=False))
    assert penetration.office_resistance(clara) == 15


def test_the_other_faiths_leaders_have_their_resistance():
    offices = derived.OFFICE_RESISTANCE
    assert offices["Caliph or Shi'i imam"] == 25
    assert offices["Chief rabbi"] == 20
    assert offices["Sultan (invested)"] == 10


# -- where they are offered --


@pytest.mark.parametrize(
    ("action", "book", "prepare"),
    [
        ("mystic_path", "TC", None),
        ("spiritual_path", "TC", my.CONTEMPLATIVE),
        ("monistic_revelation", "TC", my.MONISTIC),
        ("gods_aid", "RoP:D", None),
    ],
)
def test_offered_on_a_person_with_the_books(action, book, prepare):
    saga = _saga(book)
    clara = saga.character("c")
    if prepare:
        ds.set_path(clara, prepare)
        ds.note_ascent(clara)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    faith = replace(page, section=FAITH_SECTION)
    assert available(action, faith)
    assert action in {i.action for i in menu_forms.placed(page, "Faith")}
    assert isinstance(menu_forms.command(faith, action), Form)
    saga.books_in_play = ["HoH:S"]
    assert not available(action, replace(faith))


def test_a_mystic_path_needs_piety_and_a_divine_tie():
    saga = _saga("TC")
    clara = saga.character("c")
    faith = replace(
        menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c"),
        section=FAITH_SECTION,
    )
    assert available("mystic_path", faith)
    clara.personality_traits = []
    assert not available("mystic_path", faith)
    ds.set_path(clara, my.CONTEMPLATIVE)
    assert available("mystic_path", faith)


def test_the_font_and_the_aura_are_offered_to_those_who_have_them():
    saga = _saga()
    clara = saga.character("c")
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    assert not available("font_of_knowledge", page)
    assert not available("commanding_aura", page)
    clara.virtues_flaws.append(VirtueFlawInstance("vf_font_of_knowledge"))
    clara.background.church_rank = "Archbishop"
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    assert available("font_of_knowledge", page)
    assert available("commanding_aura", page)
