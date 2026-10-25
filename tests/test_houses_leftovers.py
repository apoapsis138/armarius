"""The Houses of Hermes leftovers: folios (True Lineages pp. 22-23), the
example discoveries once learned (pp. 30-34), the Code's crimes and
penalties (pp. 45-61), Fenicil's rituals (pp. 76-77), the lineages'
Mastery abilities (p. 99; Societates p. 33) and the Curious Common Magics
(The Mysteries Revised Edition pp. 25-36)."""

from test_lab_virtues import _plan, _saga, _total

from ars_magica_manager import (
    book_kinds,
    books,
    casting_text,
    code_of_hermes,
    ruling_templates,
    sheet_text,
)
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Breakthrough,
    Case,
    Character,
    Characteristics,
    Codex,
    KnownSpell,
    MasteryAbility,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import (
    casting_virtues,
    common_magics,
    fenicil,
    house_discoveries,
    house_mastery,
)
from ars_magica_manager.rules import house_discoveries as hd
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(parma: int = 4) -> Character:
    m = Character(id="m", name="Tillitus", type="magus")
    m.abilities = [Ability("Parma Magica", xp=ability_xp(parma))]
    m.arts = {"ignem": ArtScore(xp=art_xp(10))}
    return m


# -- folios --


def test_a_folio_holds_magnitudes_and_qualities_up_to_the_colentes_theory():
    # The book's example: tractatus 8 and 10, Lab Texts of magnitude 6, 7, 4.
    assert book_kinds.folio_size([6, 7, 4], [8, 10]) == 35
    assert book_kinds.folio_capacity([7] * 5) == 35
    assert book_kinds.folio_copy_points(3) == 9
    assert book_kinds.folio_copy_points(3, quick=True) == 27


def test_a_folios_details_give_its_size_and_copying():
    saga = Saga(id="s", name="S")
    saga.codices = [Codex(id="f", name="Folio of 1213", collection=book_kinds.FOLIO)]
    saga.books = [
        Book(id="t", name="On Herbs", type="Tractatus", quality=8, codex_id="f"),
        Book(id="l", name="Ball", type="Lab Text", level=35, codex_id="f"),
    ]
    text = books.folio_text(saga, saga.books[0])
    assert "Folio of 15" in text  # 8 + magnitude 7
    assert "6 + Profession: Scribe" in text


# -- the example discoveries --


def test_a_fold_is_known_from_a_reached_goal_up_to_parma():
    m = _magus(parma=1)
    m.breakthroughs = [
        Breakthrough("Arma Magica: Parma Ablativa", kind="Major", reached=True),
        Breakthrough("Arma Magica: Parma Condensa", kind="Major", reached=True),
        Breakthrough("Arma Magica: Parma Custodia", kind="Major"),
    ]
    assert hd.known_folds(m) == [hd.ABLATIVA]  # Parma 1: one fold only


def test_the_folds_change_parma_before_it_is_multiplied():
    assert hd.folded_parma(4, hd.ABLATIVA) == 8
    assert hd.folded_parma(5, hd.ABSORBEA) == 3  # half, rounded up
    assert hd.folded_parma(5, hd.CONDENSA, chosen_form=True) == 10
    assert hd.folded_parma(5, hd.CONDENSA) == 3
    assert hd.folded_parma(4, hd.CUSTODIA) == 0
    assert hd.folded_parma(2, hd.RESTRICTA) == 0  # never below 0
    m = _magus(parma=4)
    assert hd.fold_resistance(m, "Ignem", hd.ABLATIVA) == 10 + 40
    assert hd.custodia_defense(m) == 8


def test_the_casting_notes_name_a_known_discovery():
    m = _magus(parma=4)
    m.breakthroughs = [
        Breakthrough("Arma Magica: Parma Ablativa", kind="Major", reached=True),
        Breakthrough("Parmulae", reached=True),
        Breakthrough("Realm-aligned spells", reached=True),
    ]
    found = " ".join(casting_virtues.reminders(m))
    assert "Parma Ablativa" in found and "counts 8" in found
    assert "Magic Resistance 30" in found
    assert "Realm-aligned spells" in found


def test_the_realm_aligned_table():
    assert hd.aligned_aura_modifier("Faerie", "Divine", 3) == -12
    assert hd.aligned_aura_modifier("Faerie", "Magic", 5) == 2
    assert hd.aligned_aura_modifier("Infernal", "Infernal", 5) == 0
    assert hd.aligned_magic_theory(5, 1) == 1
    assert hd.aligned_botch_dice(3, 5) == 0


def test_figurine_ease_factors():
    assert hd.figurine_ease("Minor General Virtue") == 12
    assert hd.figurine_ease("Minor Supernatural Virtue") == 15
    assert hd.figurine_ease("spell", 3) == 12


def test_a_reached_discovery_says_what_it_gives():
    goal = Breakthrough("Parmulae", reached=True)
    assert "Once learned: Parmulae" in sheet_text.goal_text(goal)


# -- the Code --


def test_high_and_low_crimes():
    assert code_of_hermes.high_crime("Slaying Talus of Merinita").name == (
        "Slaying a Magus"
    )
    assert code_of_hermes.high_crime("Refused to share knowledge").house == "Bonisagus"
    assert code_of_hermes.high_crime("Breach of contract") is None
    assert "Wizard's March" in code_of_hermes.crime_note("Dealing with a demon")
    assert "low crime" in code_of_hermes.crime_note("Breach of contract")
    assert code_of_hermes.fine_shares(10) == (3, 7)


def test_the_penalty_templates():
    saga = Saga(id="s", name="S")
    found = ruling_templates.named(saga, "Fined (shared)")
    assert found is not None
    case = Case("Arnhaven v. Fengheld", brought_by="Arnhaven", against="Fengheld")
    blanks = {
        b: ruling_templates.suggested(case, b, None)
        for b in ruling_templates.blanks(found["text"])
    }
    assert blanks["party"] == "Fengheld" and blanks["prosecutor"] == "Arnhaven"
    names = {t["name"] for t in ruling_templates.templates(saga)}
    assert {"Seasons of service", "Loss of a familiar", "Cast out"} <= names


# -- Fenicil's rituals --


def test_fenicils_rituals():
    thoth = fenicil.BY_NAME["Curse of Thoth"]
    # The book's example: Stamina 2, abilities 130, aura 4, die 3.
    total = fenicil.casting_total(2, [130], 4, 3)
    assert total == 139 and fenicil.penetration(total, thoth) == 61
    assert fenicil.penetration(70, thoth) is None
    assert fenicil.vis_and_silver(thoth, materials=True) == (39, 39)
    athena = fenicil.BY_NAME["Wisdom of Athena"]
    assert fenicil.casting_time(athena) == "60 minutes"
    m = _magus()
    m.abilities.append(Ability("Wisdom of Athena", xp=ability_xp(2)))
    assert any("Ease Factor 12" in r for r in casting_virtues.reminders(m))


# -- Mastery --


def test_lineage_mastery_abilities_on_the_spell():
    abilities = {house_mastery.STALWART: 1, house_mastery.DISGUISED: 1}
    found = house_mastery.notes(abilities, 3, ritual=True, general=False)
    assert any("half the Fatigue" in f for f in found)
    assert any("+3" in f for f in found)
    assert house_mastery.stalwart_ritual_fatigue(3) == 2
    assert house_mastery.problems(
        {house_mastery.TETHERED: 1}, ritual=True, general=False
    )


def test_lab_mastery_adds_the_mastery_score_for_a_similar_spell():
    saga = _saga()
    magus = saga.characters[0]
    magus.spells_known = [KnownSpell("spark", mastery_score=2)]
    assert _total(saga, _plan(similar_spell_id="spark")) == 17
    magus.spells_known[0].mastery_abilities = [MasteryAbility("Lab Mastery")]
    assert _total(saga, _plan(similar_spell_id="spark")) == 19


def test_the_known_spell_lines_name_a_lineage_ability():
    saga = _saga()
    magus = saga.characters[0]
    magus.spells_known = [
        KnownSpell(
            "spark",
            mastery_score=2,
            mastery_abilities=[MasteryAbility("Harnessed Casting")],
        )
    ]
    spell = saga.spells[2]
    lines = casting_text.known_spell_casting_lines(
        saga, magus, magus.spells_known[0], spell
    )
    assert any("ended at will" in line for line in lines)


# -- the Curious Common Magics --


def test_art_of_memory():
    c = Character(id="c", name="Petrus", type="companion")
    c.characteristics = Characteristics(intelligence=2)
    assert common_magics.memorize_total(c) == (2, 3)
    c.abilities = [Ability("Art of Memory", xp=ability_xp(6))]
    assert common_magics.memorize_total(c) == (8, 0)
    assert common_magics.memory_palace(6) == (6, 30)


def test_spell_binding_and_performance_magic():
    assert common_magics.binding_problems(15, 25, 15) == []
    assert len(common_magics.binding_problems(20, 15, 10, ritual=True)) == 3
    assert common_magics.freeing_level(25) == 26
    assert (
        common_magics.form_ease(2, hermetic_words=True, hermetic_gestures=False) == 10
    )
    assert (
        common_magics.form_ease(2, hermetic_words=False, hermetic_gestures=False) == 16
    )
    m = _magus()
    m.virtues_flaws = [
        VirtueFlawInstance(common_magics.PERFORMANCE_MAGIC, params={"ability": "Music"})
    ]
    assert any("Performance Magic (Music)" in r for r in casting_virtues.reminders(m))


def test_vulgar_alchemy_adds_magic_lore_when_experimenting_on_a_device():
    assert common_magics.component_ease(4) == 15
    assert common_magics.component_ease(3, story=3) == 9
    assert common_magics.thesis_quality(4) == 8
    m = _magus()
    m.abilities.append(Ability("Magic Lore", xp=ability_xp(5)))
    m.virtues_flaws = [VirtueFlawInstance(common_magics.VULGAR_ALCHEMY)]
    lines, notes = common_magics.lab_lines(m, enchanting=True, experimenting=True)
    assert lines[0].amount == 5 and notes
    assert common_magics.lab_lines(m, enchanting=True, experimenting=False) == ([], [])


def test_house_discoveries_has_a_source():
    assert "pp. 30-34" in house_discoveries.SOURCE
