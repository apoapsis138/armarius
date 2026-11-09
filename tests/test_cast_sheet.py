"""The cast at a glance: each cast member's figures, traits and chosen
spells, for a window and for paper."""

from ars_magica_manager import cast_sheet, commands, print_layout
from ars_magica_manager.forms import sessions as session_forms
from ars_magica_manager.models import (
    Casting,
    Character,
    KnownSpell,
    Saga,
    ScoredTrait,
    Session,
    Spell,
)


def _saga() -> Saga:
    saga = Saga(id="s", name="Saga")
    magus = Character(id="m", name="Aelfric", type="magus")
    magus.personality_traits.append(ScoredTrait("Brave", 2))
    magus.spells_known = [
        KnownSpell("pilum", mastery_score=2),
        KnownSpell("ward", favourite=True),
        KnownSpell("other"),
    ]
    saga.spells = [
        Spell("pilum", "Pilum of Fire", "Creo", "Ignem", 20),
        Spell("ward", "Ward Against Heat", "Rego", "Ignem", 25),
        Spell("other", "Unseen", "Perdo", "Imaginem", 15),
    ]
    grog = Character(id="g", name="Gus", type="grog")
    saga.characters = [magus, grog]
    saga.sessions = [Session("n", castings=[Casting("ana", "m"), Casting("ben", "g")])]
    return saga


def test_the_cast_is_who_plays_at_the_session_with_mastered_and_favourite_spells():
    saga = _saga()
    cast = cast_sheet.session_cast(saga)
    assert [c.name for c in cast] == ["Aelfric", "Gus"]
    rows = cast_sheet.rows(saga, cast)
    assert len(rows[0].figures) == len(cast_sheet.COLUMNS)
    assert rows[0].spells == "Pilum of Fire (Mastery 2); Ward Against Heat"
    assert rows[0].traits == "Brave +2"
    assert rows[1].weapon  # bare hands when no weapon is carried
    assert rows[1].figures[4] == "-"  # no Parma, no Magic Resistance


def test_the_cast_prints_as_one_table_then_each_ones_traits_and_spells():
    saga = _saga()
    doc = print_layout.cast_document(saga, "Friday", cast_sheet.session_cast(saga))
    tables = [b for b in doc.blocks if isinstance(b, print_layout.Table)]
    assert len(tables) == 1 and len(tables[0].rows) == 2
    assert any(
        isinstance(b, print_layout.Heading) and b.text == "Aelfric" for b in doc.blocks
    )


def test_cast_at_a_glance_opens_to_read():
    saga = _saga()
    form = session_forms.cast_glance(saga, saga.sessions[0])
    assert isinstance(form, commands.Form)
    [info] = form.fields()
    assert "Aelfric" in str(info.value) and "Init" in str(info.value)
