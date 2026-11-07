"""Opus types, physical forms and collections (Covenants, Chapter Seven:
Library; Houses of Hermes: True Lineages, Folios)."""

from support import literate

from ars_magica_manager import book_kinds as kinds
from ars_magica_manager import books as bk
from ars_magica_manager.models import Book, Character, Codex, Covenant, Saga, SeasonPlan
from ars_magica_manager.rules import activities, enchantment, library
from ars_magica_manager.seasons import advance


def _saga() -> Saga:
    def book(book_id: str, book_type: str, **kwargs) -> Book:
        return Book(
            id=book_id,
            name=book_id.capitalize(),
            type=book_type,
            owner_kind="covenant",
            owner_id="cov",
            **kwargs,
        )

    return Saga(
        id="s",
        name="Saga",
        covenants=[Covenant("cov", "Keep", "s")],
        characters=[
            Character(id="ana", name="Ana", type="companion", covenant_id="cov")
        ],
        books=[
            book(
                "physics", "Ability Summa", ability="Philosophiae", level=6, quality=12
            ),
            book(
                "gloss",
                "Tractatus",
                subject_kind="Ability",
                ability="Philosophiae",
                quality=9,
                opus=kinds.COMMENTARY,
                commentary_on="physics",
            ),
            book(
                "t1",
                "Tractatus",
                subject_kind="Ability",
                ability="Medicine",
                quality=8,
                codex_id="flor",
            ),
            book(
                "t2",
                "Tractatus",
                subject_kind="Ability",
                ability="Medicine",
                quality=8,
                codex_id="folio",
                physical_form="Exemplar",
            ),
        ],
        codices=[
            Codex(
                "flor",
                "Flowers of Medicine",
                collection=kinds.FLORILEGIUM,
                florilegium_bonus=2,
            ),
            Codex("folio", "Bonisagus Folio", collection=kinds.FOLIO),
        ],
    )


def _read(saga: Saga, book_id: str) -> SeasonPlan:
    plan = SeasonPlan("ana", 1220, "Spring", activities.READ, book_id=book_id)
    saga.season_plans.append(plan)
    return plan


def test_quality_adjustments_and_what_cost_counts():
    saga = _saga()
    gloss, t1, t2 = saga.books[1], saga.books[2], saga.books[3]
    # A commentary: +1, which its Build Point cost ignores.
    assert library.effective_quality(saga, gloss) == 10
    assert library.cost(gloss, saga) == 9
    # A florilegium's tractatus: +2 here, also left out of the cost.
    assert library.effective_quality(saga, t1) == 10
    assert library.cost(t1, saga) == 8
    # An exemplar: -3, counted in the cost.
    assert library.effective_quality(saga, t2) == 5
    assert library.cost(t2, saga) == 5
    assert "Quality:[/] 10 (written 9; commentary +1)" in bk.detail_text(saga, gloss)
    assert "Kind:[/] Commentary on Physics" in bk.detail_text(saga, gloss)
    assert "Codex:[/] Flowers of Medicine (florilegium, +2)" in bk.detail_text(saga, t1)


def test_a_commentary_notes_an_unread_summa_until_it_is_read():
    saga = _saga()
    ana = saga.characters[0]
    plan = _read(saga, "gloss")
    notes = activities.outcome(ana, plan, saga).notes
    assert any("no season studying on record" in n for n in notes)
    # A season on the summa is recorded when it is applied.
    summa_plan = SeasonPlan("ana", 1220, "Spring", activities.READ, book_id="physics")
    outcome = activities.outcome(ana, summa_plan, saga)
    assert outcome.effect_of(activities.ReadBook).summa == "physics"
    advance.apply(saga, [outcome])
    assert ana.summae_read == ["physics"]
    notes = activities.outcome(ana, plan, saga).notes
    assert not any("commentary" in n for n in notes)


def test_a_folio_also_teaches_order_of_hermes_lore():
    saga = _saga()
    gains = activities.outcome(saga.characters[0], _read(saga, "t2"), saga).gains
    assert [g.subject for g in gains] == [
        "ability:Medicine",
        f"ability:{kinds.FOLIO_LORE}",
    ]


def test_a_csv_reads_opus_and_physical_form():
    result = bk.parse_books_csv(
        "name,type,ability,quality,opus,physical_form\n"
        "Gloss,Tractatus,Philosophiae,9,commentary,exemplar\n"
        "Bad,Ability Summa,Medicine,9,commentary,\n"
        "Odd,Tractatus,Medicine,9,,Scroll\n"
    )
    [gloss] = result.books
    assert (gloss.opus, gloss.physical_form) == (kinds.COMMENTARY, "Exemplar")
    assert [s.split(":")[0] for s in result.skipped] == ["Row 3 (Bad)", "Row 4 (Odd)"]


def test_extended_quality_counts_craftsmanship_only_when_on():
    saga = _saga()
    physics = saga.books[0]
    physics.craft = ["scribe", "binder", "illuminator", "story_resonance"]
    assert library.effective_quality(saga, physics) == 12  # the rule is off
    saga.rule_options = {"extended_book_quality": True}
    assert library.effective_quality(saga, physics) == 17  # +1 +1 +1 +2
    assert library.cost(physics, saga) == 17 + 3 * 6  # craftsmanship is paid for
    assert "skilled scribe +1" in bk.detail_text(saga, physics)


def test_extended_quality_warns_of_what_cant_go_together():
    saga = _saga()
    saga.rule_options = {"extended_book_quality": True}
    t1 = saga.books[2]  # in the florilegium
    t1.craft = ["resonance", "clarified"]
    t1.glossed = True
    t1.physical_form = "Juvenilia"
    warnings = bk.craft_warnings(saga, t1)
    assert any("gloss expresses resonance" in w for w in warnings)
    assert any("florilegium expresses resonance" in w for w in warnings)
    assert any("Juvenilia copies have no resonances" in w for w in warnings)
    tract = Book(id="x", name="X", type="Tractatus", subject_kind="Art", art="Vim",
                 quality=16, craft=["scribe", "binder"])  # fmt: skip
    assert any("over the 17" in w for w in bk.craft_warnings(saga, tract))


def test_useful_correspondence_adds_one_xp_to_the_season():
    from ars_magica_manager.models import Ability

    saga = _saga()
    ana = saga.characters[0]
    ana.abilities = [Ability("Philosophiae"), *literate()]
    plan = _read(saga, "physics")
    plan.correspondence = "ability:Medicine"
    outcome = activities.outcome(ana, plan, saga)
    assert [(g.subject, g.result.xp) for g in outcome.gains] == [
        ("ability:Philosophiae", 12),
        ("ability:Medicine", 1),
    ]
    assert any("Useful correspondence" in n for n in outcome.notes)


def test_a_bound_correspondence_is_a_kind_of_tractatus():
    result = bk.parse_books_csv(
        "name,type,ability,quality,opus\n"
        "Letters,Tractatus,Magic Theory,5,correspondence\n"
    )
    assert [b.opus for b in result.books] == [kinds.CORRESPONDENCE]
    # It is read at the Quality typed (the writers' Communication added).
    assert library.effective_quality(None, result.books[0]) == 5


def test_glossing_while_reading():
    from ars_magica_manager.models import Ability, Characteristics

    saga = _saga()
    ana = saga.characters[0]
    ana.characteristics = Characteristics(communication=2)
    author = Character(id="aut", name="Author", type="companion")
    author.characteristics = Characteristics(communication=1)
    saga.characters.append(author)
    physics = saga.books[0]
    physics.author_id = "aut"
    plan = _read(saga, "physics")
    plan.gloss = True
    # Philosophiae 0: less than half the Level (6).
    found = activities.problems(ana, plan, saga)
    assert any("half Physics's Level" in p for p in found)
    from ars_magica_manager.rules.xp import ability_xp

    ana.abilities = [Ability("Philosophiae", xp=ability_xp(3)), *literate()]
    assert activities.problems(ana, plan, saga) == []
    outcome = activities.outcome(ana, plan, saga)
    advance.apply(saga, [outcome])
    assert physics.glossed and library.effective_quality(saga, physics) == 13
    # Old saves kept a gloss as craftsmanship.
    old = Book.from_dict(
        {"id": "x", "name": "X", "type": "Tractatus", "craft": ["glossed", "scribe"]}
    )
    assert (old.glossed, old.craft) == (True, ["scribe"])


def test_editing_a_florilegium():
    from ars_magica_manager.models import Ability
    from ars_magica_manager.rules import book_seasons as bs
    from ars_magica_manager.rules.xp import ability_xp
    from ars_magica_manager.seasons.lab_apply import apply_book_work

    saga = _saga()
    ana = saga.characters[0]
    ana.abilities = [Ability("Medicine", xp=ability_xp(6))]
    for i in range(6):
        saga.books.append(
            Book(f"m{i}", f"Med {i}", "Tractatus", subject_kind="Ability",
                 ability="Medicine", quality=5 + i, owner_kind="covenant",
                 owner_id="cov")
        )  # fmt: skip
    plan = SeasonPlan("ana", 1220, "Spring", bs.EDIT_FLORILEGIUM,
                      florilegium_subject="ability:Medicine")  # fmt: skip
    found, work = bs.work(saga, ana, plan)
    assert found == []
    # Medicine 6: three tractatus (6 / 2), from six (twice as many); +1.
    title, bound, bonus = work.florilegium
    assert (title, bound, bonus) == ("Florilegium of Medicine", ["m5", "m4", "m3"], 1)
    apply_book_work(saga, ana, plan, work)
    codex = library.codex_of(saga, next(b for b in saga.books if b.id == "m5"))
    assert (codex.collection, codex.florilegium_bonus) == (kinds.FLORILEGIUM, 1)
    ana.abilities = [Ability("Medicine", xp=ability_xp(5))]
    found, _ = bs.work(saga, ana, plan)
    assert found and "needs a score of 6" in found[0]


def test_lecture_commentaries_have_their_own_limit():
    from ars_magica_manager.models import Ability, XpAllocation
    from ars_magica_manager.rules.xp import ability_xp

    saga = _saga()
    scribe = saga.characters[0]
    teacher = Character(id="t", name="Master", type="companion", covenant_id="cov")
    teacher.abilities = [Ability("Artes Liberales", xp=ability_xp(1))]
    saga.characters.append(teacher)
    plan = SeasonPlan(
        "ana", 1220, "Spring", "record_lectures", teacher_id="t",
        allocations=[XpAllocation("ability:Artes Liberales")],
    )  # fmt: skip
    assert activities.problems(scribe, plan, saga) == []
    saga.books.append(
        Book("lec", "Lectures", "Tractatus", subject_kind="Ability",
             ability="Artes Liberales", quality=5, author_id="t",
             opus=kinds.LECTURE_COMMENTARY)
    )  # fmt: skip
    assert "the most a score of 1 allows" in activities.problems(scribe, plan, saga)[0]
    plan.allocations = [XpAllocation("art:Creo")]
    assert "Arts" in activities.problems(scribe, plan, saga)[0]


def test_an_epitome_is_the_book_enchanted():

    saga = _saga()
    physics = saga.books[0]
    device = bk.enchant_as_epitome(saga, physics)
    assert bk.epitome_device(saga, physics) is device
    assert enchantment.capacity(saga, device) == 8  # material 2 x size 4
    assert (device.holder_kind, device.holder_id) == ("covenant", "cov")
    assert "Epitome:[/] Physics" in bk.detail_text(saga, physics)
    # It goes where the book goes.
    bk.set_owner(saga, physics, "character", "ana")
    assert (device.holder_kind, device.holder_id) == ("character", "ana")
