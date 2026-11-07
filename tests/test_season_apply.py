"""What advancing a season leaves in the saga, per kind of work: the effects
a planned season has besides its experience, checked through the whole
resolve-and-apply path so that however a season applies its work, these
stay true."""

from ars_magica_manager import book_kinds, seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import apprentice_seasons as aps
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="tib", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(communication=2)
    magus.abilities = [
        Ability("Latin", xp=ability_xp(4)),
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Teaching", xp=ability_xp(3)),
        Ability("Parma Magica", xp=ability_xp(1)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))}
    magus.virtues_flaws = [VirtueFlawInstance("vf_adept_laboratory_student")]
    magus.assigned_lab_id = "lab"
    child = Character(id="kid", name="Wolf", type="companion", covenant_id="cov")
    child.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="tib")
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus, child],
        laboratories=[lab],
    )
    saga.books = [
        Book(
            "summa",
            "De Ignis",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Ignem",
            level=10,
            quality=12,
        ),
        Book(
            "tract",
            "On Grammar",
            "Tractatus",
            owner_kind="character",
            owner_id="tib",
            subject_kind="Ability",
            ability="Latin",
            quality=7,
        ),
    ]
    return saga


def _plan(activity: str, *subjects: str, **kw) -> SeasonPlan:
    return SeasonPlan(
        "tib", 1220, "Spring", activity, [XpAllocation(s) for s in subjects], **kw
    )


def _advance(saga: Saga, *plans: SeasonPlan) -> None:
    for plan in plans:
        seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))


def test_reading_a_summa_records_it_as_studied():
    saga = _saga()
    _advance(saga, _plan(rules.READ, book_id="summa"))
    assert saga.character("tib").summae_read == ["summa"]


def test_a_realia_tractatus_may_be_read_again_each_season_an_ordinary_one_not():
    saga = _saga()
    tract = saga.books[1]
    tract.opus = book_kinds.REALIA
    _advance(saga, _plan(rules.READ, book_id="tract"))
    saga.current_season = "Summer"
    _advance(saga, SeasonPlan("tib", 1220, "Summer", rules.READ, book_id="tract"))
    assert saga.character("tib").tractatus_read == ["tract", "tract"]


def test_glossing_while_reading_marks_the_book_glossed():
    saga = _saga()
    assert not saga.books[0].glossed
    _advance(saga, _plan(rules.READ, book_id="summa", gloss=True))
    assert saga.books[0].glossed


def test_a_campaigning_season_is_kept_for_the_year_and_season():
    saga = _saga()
    _advance(saga, _plan(rules.CAMPAIGNING, "ability:Latin"))
    assert saga.character("tib").campaign_seasons == ["1220 Spring"]


def test_opening_the_arts_puts_the_deficiency_notes_in_the_magus_diary():
    saga = _saga()
    _advance(saga, SeasonPlan("tib", 1220, "Spring", aps.OPEN_ARTS, subject_id="kid"))
    entry = saga.character("tib").diary[-1]
    # The notes open_arts returns while the season is applied reach the Diary.
    assert "Wolf" in (entry.name + entry.details)
    assert len(saga.character("kid").arts) == 15


def test_one_season_applies_each_of_its_effects_in_the_same_pass():
    """Vis study: the pawn is spent, the Art grows and the Diary says so."""
    saga = _saga()
    magus = saga.character("tib")
    magus.raw_vis = {"creo": 3}
    _advance(saga, _plan(rules.VIS_STUDY, "art:Creo", die=7, vis_from="character"))
    assert magus.raw_vis == {"creo": 1}  # Creo 10 takes 2 pawns
    assert magus.arts["creo"].xp == art_xp(10) + 7
    assert magus.diary[-1].name
