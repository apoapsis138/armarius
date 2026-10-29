"""Art & Academe's scholars and artists: schools, posts and the Academic
Reputation (pp. 79-89, 102-103), works of art, the Artist Reputation,
sponsors and a maestro's magic (pp. 123-135)."""

import random
from dataclasses import replace

from ars_magica_manager import deeds, seasons
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import careers, scholar_seasons
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    ArtworkPlan,
    Book,
    Character,
    Characteristics,
    Progress,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import artistry, scholarship, theban_customs
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp, art_xp

PAINTING = "Craft: Painting"


def _grifo(**abilities: int) -> Character:
    """Grifo the maestro (A&A p. 134): Dexterity +3, Painter 8, Puissant
    Painting, Free Expression, Hermetic Inclination in Imaginem 10."""
    grifo = Character(id="g", name="Grifo", type="mythic companion")
    grifo.characteristics = Characteristics(dexterity=3, communication=1, presence=1)
    grifo.abilities = [
        Ability(PAINTING, xp=ability_xp(8)),
        *(Ability(name, xp=ability_xp(score)) for name, score in abilities.items()),
    ]
    grifo.virtues_flaws = [
        VirtueFlawInstance("vf_maestro"),
        VirtueFlawInstance("vf_puissant_ability", {"ability": PAINTING}),
        VirtueFlawInstance("vf_free_expression"),
        VirtueFlawInstance("vf_hermetic_inclination_in_form", {"form": "Imaginem"}),
    ]
    grifo.arts = {"imaginem": ArtScore(xp=art_xp(10))}
    return grifo


def _brogo() -> Character:
    """Brogo the Dwarf (A&A p. 122): Communication +4, Trouvère 5,
    Puissant Trouvère, Artes Liberales 2."""
    brogo = Character(id="b", name="Brogo", type="companion")
    brogo.characteristics = Characteristics(communication=4, perception=1)
    brogo.abilities = [
        Ability("Profession: Trouvère", xp=ability_xp(5)),
        Ability("Artes Liberales", xp=ability_xp(2)),
        Ability("Bargain", xp=ability_xp(4)),
        Ability("Folk Ken", xp=ability_xp(2)),
    ]
    brogo.virtues_flaws = [
        VirtueFlawInstance("vf_puissant_ability", {"ability": "Profession: Trouvère"})
    ]
    brogo.reputations = [ScoredTrait("Trouvère", 2, type="Artist")]
    return brogo


def _scholar() -> Character:
    julian = Character(id="j", name="Julian", type="companion")
    julian.characteristics = Characteristics(presence=1, communication=3)
    julian.abilities = [
        Ability("Artes Liberales", xp=ability_xp(4)),
        Ability("Theology", xp=ability_xp(3)),
        Ability("Charm", xp=ability_xp(2)),
        Ability("Teaching", xp=ability_xp(2)),
        Ability("Latin", xp=ability_xp(5)),
        Ability("Greek", xp=ability_xp(6)),
    ]
    julian.virtues_flaws = [VirtueFlawInstance("vf_educated")]
    return julian


def _saga(*characters: Character) -> Saga:
    return Saga(id="s", name="S", characters=list(characters))


def _art(character: Character, craft: str = PAINTING, **kw) -> SeasonPlan:
    return SeasonPlan(
        character.id,
        1220,
        "Spring",
        "create_art",
        [XpAllocation(f"ability:{craft}")],
        title="Calvary",
        **kw,
    )


# -- Aesthetic Quality and time ------------------------------------------------


def test_grifos_mural_is_nineteen_in_his_church_and_takes_two_seasons():
    grifo = _grifo()
    plan = ArtworkPlan()
    found = artistry.aesthetic_quality(grifo, PAINTING, plan)
    # Dex 3 + Painting 8 + Puissant 2 + Free Expression 3 + Imaginem 10 / 5.
    assert found.quality == 18
    assert artistry.creation_time(grifo, plan, 18).seasons == 2
    # In the Divine aura 3 of his church, a maestro of the Divine adds the
    # aura / 5, rounded up (p. 124): 19, where the book's example (p. 134)
    # leaves the +1 out and gives 18.
    aligned = ArtworkPlan(realm="Divine", aura=3, aura_realm="Divine")
    assert artistry.aesthetic_quality(grifo, PAINTING, aligned).quality == 19
    assert (
        artistry.aesthetic_quality(
            grifo, PAINTING, replace(aligned, aura_realm="Faerie")
        ).quality
        == 18
    )
    # Neither the aura itself nor anything for an ordinary artist; a
    # legendary artist (Artist Reputation 11) gains it too.
    plain = _grifo()
    plain.virtues_flaws = [
        vf for vf in plain.virtues_flaws if vf.vf_id != artistry.MAESTRO
    ]
    strong = replace(aligned, aura=6)
    assert artistry.aligned_aura_bonus(grifo, strong) == 2
    assert artistry.aligned_aura_bonus(plain, strong) == 0
    assert artistry.aligned_aura_bonus(plain, strong, reputation=11) == 2


def test_brogos_songs_are_twelve():
    brogo = _brogo()
    craft = "Profession: Trouvère"
    found = artistry.aesthetic_quality(brogo, craft, ArtworkPlan(liberal_arts=True))
    # Com 4 + Trouvère 5 + Puissant 2 + Artes Liberales 2 / 3 rounded up.
    assert found.quality == 12
    assert artistry.characteristic_name("Craft: Poetry") == "communication"


def test_the_bonuses_and_halving():
    grifo = _grifo(Leadership=2)
    grifo.virtues_flaws.append(VirtueFlawInstance("vf_life_linked_art"))
    plan = ArtworkPlan(double_time=True, overtime=True, muse_might=10, wound="Medium")
    # 18 + 1 + 1 + 2 + 3.
    assert artistry.aesthetic_quality(grifo, PAINTING, plan).quality == 25
    rushed = artistry.aesthetic_quality(grifo, PAINTING, ArtworkPlan(rushed=True))
    assert rushed.quality == 9
    renowned = artistry.aesthetic_quality(grifo, PAINTING, ArtworkPlan(), reputation=10)
    assert renowned.quality == 21
    assert (
        artistry.aesthetic_quality(
            grifo, PAINTING, ArtworkPlan(experiment=True), experiment_die=5
        ).quality
        == 21
    )


def test_time_with_assistants_rushing_and_size():
    grifo = _grifo(Leadership=3)
    # A year's piece of Quality 12: two years; three assistants take 3 weeks.
    year = artistry.creation_time(grifo, ArtworkPlan(base="year", assistants=3), 12)
    assert year.days == 2 * 364 - 21 and year.seasons == 8
    # No fewer than half the time, however many assistants.
    capped = artistry.creation_time(grifo, ArtworkPlan(assistants=200), 5)
    assert capped.days == 91 - 10.5  # Leadership 3: three of them
    many = artistry.creation_time(_grifo(Leadership=30), ArtworkPlan(assistants=30), 5)
    assert many.days == 91 / 2
    assert artistry.creation_time(grifo, ArtworkPlan(assistants=3), 5).days == 80.5
    rushed = artistry.creation_time(grifo, ArtworkPlan(rushed=True), 5)
    assert rushed.days == 45.5 and rushed.seasons == 1
    church = artistry.creation_time(grifo, ArtworkPlan(base="years", size=3), 9)
    assert church.seasons == 12
    cathedral = artistry.creation_time(grifo, ArtworkPlan(base="decades", size=2), 21)
    assert cathedral.seasons == 2 * 40 * 3
    grifo.virtues_flaws.append(VirtueFlawInstance("vf_prolific_artist"))
    prolific = artistry.creation_time(grifo, ArtworkPlan(assistants=3), 5)
    assert prolific.days == 91 * 0.75


def test_the_experimentation_table():
    assert artistry.experiment_result(0, True) == "disaster"
    assert [artistry.experiment_result(r, False) for r in (3, 5, 8, 9, 11)] == [
        "ruined",
        "disparaged",
        "no_effect",
        "work_praised",
        "artist_praised",
    ]


# -- the Artist Reputation --------------------------------------------------------


def test_reputation_xp_and_benefits():
    assert artistry.season_xp(7, 2) == 1 and artistry.season_xp(6, 2) == 0
    assert artistry.benefits(5) == []
    lines = artistry.benefits(10)
    assert lines[0].startswith("+5 to social rolls")
    assert any("signs his work" in line for line in lines)
    assert any("never lost" in line for line in lines)
    assert artistry.muse_kind(15) == "minor" and artistry.muse_warping(20) == 3
    legend = artistry.legendary(_grifo(), PAINTING)
    assert (legend.might, legend.powers, legend.magnitude) == (16, 8, 3)
    rep = ScoredTrait("Painting", 2, deeds=4)
    assert artistry.xp_to_next(rep) == 11 and artistry.xp_of_a_level(rep) == 10


def test_sponsors_performing_and_magic_art():
    brogo = _brogo()
    craft = "Profession: Trouvère"
    # Com 4 + Bargain 4 + Trouvère Reputation 2.
    assert artistry.sponsor_total(brogo, craft) == 10
    assert artistry.sponsor_ease("benefactor", "minor", 2) == 12 - 3 + 3 + 2
    assert artistry.sponsor_ease("patron", "major", 0) == 27
    assert "anyone" in artistry.sponsor_needs(3)
    assert "patron" in artistry.sponsor_needs(8)
    assert artistry.performance_ease(12) == 6
    assert artistry.performance_total(brogo, craft) == 11
    magus = Character(id="m", name="M", type="magus")
    magus.characteristics = Characteristics(intelligence=3)
    magus.abilities = [Ability("Finesse", xp=ability_xp(4))]
    assert artistry.magical_quality(magus, "season") == -2
    assert artistry.magical_quality(magus, "pair") == 1


def test_grifos_magic_takes_two_seasons():
    grifo = _grifo()
    plan = ArtworkPlan(realm="Divine", aura=3, aura_realm="Divine", instill_level=14)
    # Dex 3 + Painting 8 + Puissant 2 + Imaginem 10 + Divine aura 3.
    assert artistry.instill_total(grifo, PAINTING, plan) == 26
    assert artistry.instill_fatigue(14) == 2  # Weary
    assert artistry.instill_problem(grifo, PAINTING, plan) is None
    plain = _brogo()
    assert "Hermetic Inclination" in str(
        artistry.instill_problem(plain, "Profession: Trouvère", plan)
    )


def test_an_icon_starts_from_the_artists_quality():
    painter = Character(id="p", name="Theodore", type="companion")
    painter.characteristics = Characteristics(dexterity=2)
    painter.abilities = [Ability(PAINTING, xp=ability_xp(5))]
    painter.virtues_flaws = [VirtueFlawInstance("vf_free_expression")]
    assert theban_customs.eikon(painter, standard=1).quality == 2 + 5 + 3 + 1


# -- the Create a Work of Art season --------------------------------------------------


def _work(saga: Saga, plan: SeasonPlan, rng: random.Random | None = None):
    character = saga.character(plan.character_id)
    assert character is not None
    return sw.work(saga, character, plan, rng)


def test_the_season_records_progress_and_reputation():
    grifo = _grifo()
    saga = _saga(grifo)
    work = _work(saga, _art(grifo))
    assert work.progress == [("artwork", "Calvary", 2, 1)]
    assert work.reputation_xp == [("Painting", 1)]
    assert work.notes[0].startswith("Aesthetic Quality 18 = Dexterity +3")
    # The second season finishes it: the Arcane Connection lasts 13 weeks.
    grifo.progress.append(Progress("artwork", "Calvary", 2, 1))
    done = _work(saga, _art(grifo, artwork=ArtworkPlan(overtime=True)))
    assert done.aging_roll
    assert any("Calvary finished: Aesthetic Quality 19" in n for n in done.notes)
    assert any("for 13 weeks" in n for n in done.notes)


def test_the_season_instills_magic_and_checks_its_choices():
    grifo = _grifo()
    saga = _saga(grifo)
    plan = _art(
        grifo,
        artwork=ArtworkPlan(
            realm="Divine", aura=3, aura_realm="Divine", instill_level=14
        ),
    )
    assert ("instilling", "Calvary", 14, 12) in _work(saga, plan).progress
    assert sw.problems(saga, grifo, plan) == []
    bad = _art(grifo, artwork=ArtworkPlan(assistants=1, wound="Light"))
    found = sw.problems(saga, grifo, bad)
    assert any("at most 0 assistants" in p for p in found)
    assert any("Life-Linked Art" in p for p in found)
    wrong = _art(grifo, craft="Artes Liberales")
    assert "Craft or Profession" in sw.problems(saga, grifo, wrong)[0]


def test_an_experiment_is_rolled_as_the_piece_is_finished():
    brogo = _brogo()
    saga = _saga(brogo)
    plan = _art(brogo, "Profession: Trouvère", artwork=ArtworkPlan(experiment=True))
    brogo.progress.append(Progress("artwork", "Calvary", 2, 1))  # Quality 11
    assert any("rolled when the season is played" in n for n in _work(saga, plan).notes)
    results = set()
    for seed in range(40):
        work = _work(saga, plan, random.Random(seed))
        line = next(n for n in work.notes if n.startswith("Experimenting"))
        results.add(line.split(": ", 2)[1])
        if "Disaster" in line:
            assert ("Trouvère", -10) in work.reputation_xp
        if "ruined" in line:
            assert work.reputation_xp[0][1] < 0
    assert len(results) >= 3


def test_playing_the_season_raises_the_artist_reputation():
    grifo = _grifo()
    saga = _saga(grifo)
    seasons.set_plan(saga, _art(grifo))
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    rep = next(r for r in grifo.reputations if r.name == "Painting")
    assert (rep.score, rep.deeds) == (0, 1)
    assert grifo.progress[0].kind == "artwork" and grifo.progress[0].points == 1


def test_the_season_form_reads_the_works_choices():
    grifo = _grifo(Leadership=2)
    grifo.virtues_flaws.append(VirtueFlawInstance("vf_life_linked_art"))
    saga = _saga(grifo)
    keys = {f.key for f in season_forms.season_plan_fields(saga, grifo, None)}
    assert {"art_base", "art_wound", "art_realm", "art_instill"} <= keys
    values = {
        "activity": "create_art",
        "subject_1": f"ability:{PAINTING}",
        "work_name": "Calvary",
        "art_base": "year",
        "art_assistants": 2,
        "art_overtime": True,
        "art_wound": "Heavy",
        "art_instill": 14,
    }
    plan = season_forms.season_plan_from(saga, grifo, values)
    assert plan.artwork == ArtworkPlan(
        base="year", assistants=2, overtime=True, wound="Heavy", instill_level=14
    )
    again = SeasonPlan.from_dict(
        {**plan.__dict__, "artwork": plan.artwork.__dict__, "allocations": []}
    )
    assert again.artwork == plan.artwork
    assert scholar_seasons.artwork_from({}) == ArtworkPlan()


# -- scholars ------------------------------------------------------------------


def test_school_limits_and_entry():
    assert scholarship.limit("cathedral", "Theology") == 6
    assert scholarship.limit("cathedral", "Philosophiae") == 3
    assert scholarship.limit("rural_parish", "Theology") == 0
    assert scholarship.limit("tutor", "Medicine") == 3
    julian = _scholar()
    julian.reputations = [ScoredTrait("Heretic", -2)]
    # Pre 1 + Charm 2 + gift 2 - Bad Reputation 2 at a cathedral school.
    assert scholarship.entry_total(julian, "cathedral", "Charm", 2) == 3
    assert scholarship.entry_total(julian, "rural_parish", "Charm") == 3


def test_a_post_its_total_and_its_needs():
    julian = _scholar()
    julian.reputations = [ScoredTrait("Learned", 2, type="Academic")]
    categories = {"vf_educated": ("General", "Minor")}
    bonus = scholarship.status_bonus(julian, categories)
    assert bonus == 1
    assert (
        scholarship.status_bonus(julian, {"vf_educated": ("Social Status", "Major")})
        == 3
    )
    # Pre 1 + Artes Liberales 4 + Good 2 + 1.
    assert scholarship.post_total(julian, "Artes Liberales", bonus) == 8
    assert "licence" in str(scholarship.post_problem(julian, "magister"))
    assert "monk" in str(scholarship.post_problem(julian, "monastic_teacher"))
    assert scholarship.post_problem(julian, "cathedral_teacher") is None
    assert scholarship.student_dice(julian) == 3
    assert scholarship.students_taught(julian) == 10


def test_academic_reputation_xp_good_and_bad():
    julian = _scholar()
    good = scholarship.add_academic_xp(julian, 5)
    assert (good.name, good.score, good.type) == ("Learned Scholar", 1, "Academic")
    bad = scholarship.add_academic_xp(julian, -5)
    # A Bad one is its own entry with a positive score (A&A p. 103).
    assert (bad.name, bad.score, bad.bad) == ("Idle Scholar", 1, True)
    assert scholarship.highest_bad_academic(julian) == 1
    assert scholarship.highest_good_academic(julian) == 1
    again = scholarship.add_academic_xp(julian, -1)
    assert again is bad and bad.deeds == 1
    named = scholarship.add_academic_xp(julian, 1, "Good Disputer")
    assert named.name == "Good Disputer" and len(julian.reputations) == 3
    # A Good and a Bad one of the same name are kept apart.
    argued = scholarship.add_academic_xp(julian, -5, "Good Disputer")
    assert argued is not named and argued.bad and argued.score == 1
    assert not named.bad and len(julian.reputations) == 4


def test_a_saved_negative_academic_reputation_becomes_a_bad_one():
    data = {
        "id": "j",
        "name": "Julian",
        "type": "companion",
        "reputations": [
            {"name": "Argumentative", "score": -2, "type": "Academic"},
            {"name": "Drunkard", "score": -2, "type": "Local"},
        ],
    }
    julian = Character.from_dict(data)
    argumentative, drunkard = julian.reputations
    assert (argumentative.score, argumentative.bad) == (2, True)
    assert (drunkard.score, drunkard.bad) == (-2, False)
    assert scholarship.highest_bad_academic(julian) == 2


def test_translating():
    assert scholarship.translation_artes("Greek", "Latin") == 2
    assert scholarship.translation_artes("French", "Latin") == 1
    assert scholarship.translation_loss(5, 5, False, False) == 2
    assert scholarship.translation_loss(6, 6, False, True) == 0
    assert scholarship.translation_loss(6, 6, True, False) == 0
    assert scholarship.translation_loss(5, 6, True, False) == 1


def test_a_translation_needs_artes_liberales_and_loses_less_with_elegance():
    julian = _scholar()
    julian.abilities = [a for a in julian.abilities if a.name != "Artes Liberales"]
    saga = _saga(julian)
    saga.books.append(
        Book(
            "summa",
            "Organon",
            "Ability Summa",
            language="Greek",
            ability="Logic",
            level=3,
            quality=10,
            owner_kind="character",
            owner_id="j",
        )
    )
    plan = SeasonPlan(
        "j", 1220, "Spring", bs.TRANSLATE_BOOK, book_id="summa", language="Latin"
    )
    found, _ = bs.work(saga, julian, plan)
    assert "needs Artes Liberales 2" in found[0]
    julian.abilities.append(Ability("Artes Liberales", xp=ability_xp(2)))
    found, work = bs.work(saga, julian, plan)
    assert found == [] and work is not None and work.made is not None
    # Greek 6, Latin 5: the languages' point and the culture's are lost.
    assert work.made.quality == 8
    # Greece Lore 3 keeps the culture's point.
    found, work = bs.work(saga, julian, replace(plan, culture_lore=True))
    assert work is not None and work.made is not None and work.made.quality == 9


def test_a_magus_translating_a_hermetic_text_keeps_the_culture_point():
    julian = _scholar()
    saga = _saga(julian)
    saga.books.append(
        Book(
            "art",
            "De Igne",
            "Art Summa",
            language="Greek",
            art="Ignem",
            level=10,
            quality=10,
            owner_kind="character",
            owner_id="j",
        )
    )
    plan = SeasonPlan(
        "j", 1220, "Spring", bs.TRANSLATE_BOOK, book_id="art", language="Latin"
    )
    _found, work = bs.work(saga, julian, plan)
    # A scholar who is no magus loses both points.
    assert work is not None and work.made is not None and work.made.quality == 8
    julian.type = "magus"
    _found, work = bs.work(saga, julian, plan)
    assert work is not None and work.made is not None and work.made.quality == 9


def test_lectures_edited_and_counted():
    julian = _scholar()
    scribe = Character(id="s", name="Scribe", type="companion")
    saga = _saga(julian, scribe)
    saga.books.append(
        Book(
            "l1",
            "Lectures",
            "Tractatus",
            author_id="j",
            ability="Theology",
            quality=4,
            opus="Lecture commentary",
        )
    )
    record = SeasonPlan(
        "s",
        1220,
        "Spring",
        "record_lectures",
        [XpAllocation("ability:Theology")],
        teacher_id="j",
    )
    work = sw.work(saga, scribe, record, None)
    assert work.academic_xp == [("j", 1)]
    edit = SeasonPlan(
        "j",
        1220,
        "Spring",
        "edit_lectures",
        [XpAllocation("ability:Theology")],
        book_id="l1",
    )
    assert sw.problems(saga, julian, edit) == []
    assert sw.work(saga, julian, edit, None).book_quality == [("l1", 1)]
    seasons.set_plan(saga, edit)
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    assert saga.books[0].quality == 5 and saga.books[0].glossed
    assert "already" in sw.problems(saga, julian, edit)[0]


def test_seeking_a_post():
    julian = _scholar()
    saga = _saga(julian)
    plan = SeasonPlan("j", 1220, "Spring", "seek_post", title="cathedral_teacher")
    assert sw.problems(saga, julian, plan) == []
    assert "Choose the post" in sw.problems(saga, julian, replace(plan, title=""))[0]
    preview = sw.work(saga, julian, plan, None).notes
    # Pre 1 + Artes Liberales 4 + 0 + Educated 1, against 18.
    assert "= 6, + a stress die against 18" in preview[0]
    outcomes = {
        n
        for seed in range(60)
        for n in sw.work(saga, julian, plan, random.Random(seed)).notes[1:2]
    }
    assert any("no post" in n for n in outcomes)
    won = next(
        sw.work(saga, julian, plan, random.Random(seed))
        for seed in range(400)
        if "post is his"
        in " ".join(sw.work(saga, julian, plan, random.Random(seed)).notes)
    )
    assert won.academic_xp == [("", 1)]
    assert any("students come" in n for n in won.notes)


# -- the More forms -------------------------------------------------------------------


def test_the_artists_career_form():
    brogo = _brogo()
    saga = _saga(brogo)
    form = careers.artist_form(saga, brogo, random.Random(3))
    assert isinstance(form, Form) and form.live and form.validate
    values = {"roll": careers.SPONSOR, "craft": "Profession: Trouvère"}
    assert "[b]10[/] + a stress die against [b]9[/]" in form.live(values)
    assert form.validate({**values, "sponsor_reputation": -1})
    lines = form.apply({**values, "kind": "benefactor"})
    assert brogo.diary[-1].name == "Sought a sponsor"
    assert any("against 9" in line for line in lines)
    deed = form.apply(
        {"roll": careers.DEED, "craft": "Profession: Trouvère", "deed": "patron"}
    )
    assert any("+6 xp in the Trouvère Reputation" in line for line in deed)
    lost = form.apply(
        {
            "roll": careers.DEED,
            "craft": "Profession: Trouvère",
            "deed": "abandoned_work",
            "amount": 3,
        }
    )
    assert any("-3 xp" in line for line in lost)
    perform = form.apply(
        {"roll": careers.PERFORM, "craft": "Profession: Trouvère", "quality": 12}
    )
    assert any("against 6" in line or "Die a botch" in line for line in perform)
    keep = form.apply({"roll": careers.KEEP, "craft": "Profession: Trouvère"})
    assert keep[0].startswith("Simple die")
    assert isinstance(careers.artist_form(saga, _scholar()), Refuse)


def test_the_scholars_career_form():
    julian = _scholar()
    saga = _saga(julian)
    form = careers.scholar_form(saga, julian, random.Random(2))
    assert isinstance(form, Form) and form.live and form.validate
    values = {"roll": careers.ENTRY, "school": "rural_parish", "ability": "Intrigue"}
    assert "isn't won with Intrigue" in str(form.validate(values))
    values["ability"] = "Charm"
    assert form.validate(values) is None
    live = form.live(values)
    assert "against [b]6[/]" in live and "Artes Liberales, Latin to 2" in live
    form.apply(values)
    assert julian.diary[-1].name.startswith("Sought a place")
    deed = form.apply(
        {"roll": careers.ACADEMIC, "deed": "no_summa", "interfaith": True}
    )
    assert any("10 xp toward the Bad Academic Reputation" in line for line in deed)
    assert scholarship.highest_bad_academic(julian) == 1


def test_more_offers_the_careers():
    brogo = _brogo()
    saga = _saga(brogo)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="b")
    assert available("artist_career", page) and available("scholar_career", page)
    assert "artist_career" in {
        i.action for i in menu_forms.placed(page, deeds.SEASON_WORK)
    }
    brogo.abilities = []
    assert not available("artist_career", page)
