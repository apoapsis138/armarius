"""Opus types, physical forms and collections (Covenants, Chapter Seven:
Library; Houses of Hermes: True Lineages, Folios)."""

from ars_magica_manager import book_kinds as kinds
from ars_magica_manager import books as bk
from ars_magica_manager.models import Book, Character, Codex, Covenant, Saga, SeasonPlan
from ars_magica_manager.rules import activities
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
    assert bk.effective_quality(saga, gloss) == 10
    assert bk.cost(gloss, saga) == 9
    # A florilegium's tractatus: +2 here, also left out of the cost.
    assert bk.effective_quality(saga, t1) == 10
    assert bk.cost(t1, saga) == 8
    # An exemplar: -3, counted in the cost.
    assert bk.effective_quality(saga, t2) == 5
    assert bk.cost(t2, saga) == 5
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
    assert outcome.summa == "physics"
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
    assert bk.effective_quality(saga, physics) == 12  # the rule is off
    saga.rule_options = {"extended_book_quality": True}
    assert bk.effective_quality(saga, physics) == 17  # +1 +1 +1 +2
    assert bk.cost(physics, saga) == 17 + 3 * 6  # craftsmanship is paid for
    assert "skilled scribe +1" in bk.detail_text(saga, physics)


def test_extended_quality_warns_of_what_cant_go_together():
    saga = _saga()
    saga.rule_options = {"extended_book_quality": True}
    t1 = saga.books[2]  # in the florilegium
    t1.craft = ["glossed", "resonance", "clarified"]
    t1.physical_form = "Juvenilia"
    warnings = bk.craft_warnings(saga, t1)
    assert any("gloss expresses resonance" in w for w in warnings)
    assert any("florilegium expresses resonance" in w for w in warnings)
    assert any("Juvenilia copies have no resonances" in w for w in warnings)
    tract = Book(id="x", name="X", type="Tractatus", subject_kind="Art", art="Vim",
                 quality=16, craft=["scribe", "binder"])  # fmt: skip
    assert any("over the 17" in w for w in bk.craft_warnings(saga, tract))
