"""Galdor and trollskap (Land of Fire & Ice, with Hedge Magic RE's frame):
the song's total, what it may ask, holding it, the deal with a lord, the
item bound, the fylgja, and the pack's working sheets."""

import random

import pytest

from ars_magica_manager import actions, catalog, tradition_text, traditions
from ars_magica_manager.book_packs import iceland
from ars_magica_manager.book_packs.fourth import Fourth, convert
from ars_magica_manager.forms import galdor as forms
from ars_magica_manager.forms import hedge_cast
from ars_magica_manager.forms import tradition as tradition_forms
from ars_magica_manager.models import (
    FATIGUE_LEVELS,
    Ability,
    BoundBeing,
    Character,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import galdor, realms
from ars_magica_manager.rules import hedge_casting as hc
from ars_magica_manager.rules.dice import DieResult


def galdraman(**songs: int) -> Character:
    """Einar of the book's worked example (p. 48): Com +2, Sing 8, Galdor
    Wisdom 8, Ol-galdor 6."""
    c = Character("c1", "Einar", "companion")
    c.traditions = [galdor.TRADITION_ID]
    c.characteristics.communication = 2
    c.characteristics.stamina = 2
    c.virtues_flaws = [
        VirtueFlawInstance(vf)
        for vf in ("vf_the_gift", galdor.CONJURING, galdor.ENCHANTMENT)
    ]
    c.abilities = [
        Ability("Music", xp=180),
        Ability("Galdor Wisdom", xp=180),
        Ability("Craft: Weaving", xp=75),
        *(
            Ability(name.replace("_", "-"), xp=score * (score + 1) // 2, xp_table="art")
            for name, score in (songs or {"Ol_galdor": 6}).items()
        ),
    ]
    return c


def saga() -> Saga:
    return Saga(id="s", name="S", books_in_play=["LFI"])


def tradition():
    return traditions.find(galdor.TRADITION_ID)


def conjuring_score(c: Character, aura: int = 2, realm: str = "Magic") -> int:
    rule = galdor.tradition_rule(tradition(), galdor.CONJURE_RULE)
    score = hc.casting_score(
        c, tradition(), rule, ("Ol-galdor",), aura=aura, aura_realm=realm
    )
    return int(score.total)


def test_the_books_worked_example_fails_at_the_level_and_works_above_it():
    assert conjuring_score(galdraman()) == 26
    # His roll of 3 is 29, short of the ritual's 30; a 6 makes 32.
    assert not galdor.conjured(29, 30, "Momentary").works
    assert galdor.conjured(32, 30, "Momentary").works
    assert galdor.conjured(32, 30, "Momentary").might == 32


def test_a_total_equal_to_the_level_is_not_greater():
    assert not galdor.conjured(30, 30, "Momentary").works


def test_the_ground_halves_the_total_rounding_down():
    rule = galdor.tradition_rule(tradition(), galdor.GROUND_RULE)
    assert hc.casting_total(rule, 26, 5) == 15


def test_a_song_counts_no_higher_than_galdor_wisdom():
    c = galdraman(Ol_galdor=10)
    assert galdor.song_score(c, "Ol-galdor") == 8
    assert conjuring_score(c) == 2 + 8 + 8 + 8 + 2


def test_a_service_of_more_magnitudes_than_the_song_is_refused():
    c = galdraman()
    assert galdor.song_problem(c, "Ol-galdor", 30) is None
    assert "magnitude 7" in galdor.song_problem(c, "Ol-galdor", 35)


def test_a_song_takes_a_minute_a_magnitude_and_a_ritual_fifteen_and_vis():
    assert galdor.song_minutes(30) == 6
    assert galdor.song_minutes(30, ritual=True) == 90  # The book's hour and a half.
    assert galdor.ritual_vis(30) == 6


def test_twice_the_level_leaves_only_a_concentration_effect_working():
    assert galdor.conjured(40, 20, "Concentration").lingers
    assert not galdor.conjured(39, 20, "Concentration").lingers
    assert not galdor.conjured(40, 20, "Momentary").lingers


@pytest.mark.parametrize(
    ("total", "goes_on", "tired"),
    [(8, True, False), (7, True, True), (5, True, True), (4, False, False)],
)
def test_holding_a_song_tires_within_three_and_fails_beyond(total, goes_on, tired):
    assert galdor.holds_song(total, 2) == (goes_on, tired)  # Ease Factor 8.


def test_landvaettir_read_a_magic_aura_as_magic_and_any_other_as_faerie():
    c = galdraman()
    rule = galdor.tradition_rule(tradition(), galdor.CONJURE_RULE)
    realm = hc.power_realm(c, tradition(), rule, ("Ol-galdor",), aura_realm="Divine")
    assert realm == "Faerie"
    assert conjuring_score(c, 3, "Magic") == 27
    assert conjuring_score(c, 3, "Faerie") == 27
    assert conjuring_score(c, 3, "Divine") == 24 + realms.aura_modifier(
        "Faerie", "Divine", 3
    )


def test_a_magic_summoning_reads_auras_as_magic():
    rule = traditions.find("trad_sahirs").casting[0]
    c = Character("c2", "S", "companion")
    assert hc.SUMMONING_REALMS["(Magic) Summoning"] == "Magic"
    c.abilities = [Ability("(Magic) Summoning", xp=15, xp_table="art")]
    realm = hc.power_realm(
        c, traditions.find("trad_sahirs"), rule, ("(Magic) Summoning",)
    )
    assert realm == "Magic"


def test_cast_a_power_leaves_the_songs_to_their_own_form():
    c = galdraman()
    c.abilities.append(Ability("Hamfarir", xp=15))
    rules = [t.casting[i].name for t, i, _ in hedge_cast._rules(c)]
    assert rules == ["Curse", "Hamfarir"]


def test_more_offers_a_character_the_forms_their_virtues_open():
    menu = {item.action for item in actions.MORE_MENU}
    assert {"galdor_conjure", "galdor_bargain", "galdor_bind"} <= menu
    assert galdor.conjures(galdraman()) and galdor.enchants(galdraman())
    assert not galdor.bargains(Character("c2", "No", "companion"))


# ---------------------------------------------------------------------------
# The Conjure form


def values(**more):
    return {
        "song": "Ol-galdor",
        "level": 30,
        "duration": "Momentary",
        "aura": 2,
        "aura_realm": "Magic",
        **more,
    }


def test_conjure_writes_the_might_and_penetration_in_the_diary():
    c = galdraman()
    said = forms.conjure(saga(), c, values(die=6, ritual=True))
    assert c.diary[-1].name == "Conjured: Ol-galdor"
    assert "A spirit of Might 32 comes; Penetration 2." in said
    assert "It takes 6 pawns on arrival." in said


def test_conjure_on_the_ground_can_fail_what_a_platform_would_not():
    c = galdraman()
    said = forms.conjure(saga(), c, values(die=9, ground=True))
    assert "No spirit comes." in said


def test_conjure_holds_the_song_hour_by_hour_at_a_fatigue_cost(monkeypatch):
    monkeypatch.setattr(
        forms.dice, "stress_die", lambda *a, **k: DieResult(value=2, faces=(2,))
    )
    c = galdraman()
    c.abilities[0].xp = 15  # Music 2: Sta + Music + die is 6, short of 7, 8, 9.
    said = forms.conjure(
        saga(), c, values(level=10, duration="Concentration", die=9, hours=3)
    )
    assert "He holds the song 3 hours, for 3 Fatigue levels." in said
    assert c.fatigue_level == FATIGUE_LEVELS[3]


def test_conjure_ends_when_a_song_falls_more_than_three_short(monkeypatch):
    monkeypatch.setattr(
        forms.dice, "stress_die", lambda *a, **k: DieResult(value=2, faces=(2,))
    )
    c = galdraman()
    c.abilities[0].xp = 0  # Music 0: 4 against hour 2's 8.
    said = forms.conjure(
        saga(), c, values(level=10, duration="Concentration", die=9, hours=5)
    )
    assert any("The song fails in hour 2" in line for line in said)
    assert not any("after he stops" in line for line in said)


def test_conjure_refuses_a_level_above_the_song_or_none():
    c = galdraman()
    assert forms.conjure_problem(c, values(level=0))
    assert forms.conjure_problem(c, values(level=35))
    assert forms.conjure_problem(c, values()) is None


# ---------------------------------------------------------------------------
# Deals


def test_the_bargain_ease_factor_adds_the_book_modifiers():
    assert (
        galdor.bargain_ease("General", "A month", "None", standard=12, offered=12) == 24
    )
    assert (
        galdor.bargain_ease(
            "A single task", "A day", "An onerous duty", standard=4, offered=4
        )
        == 6
    )


def test_vis_under_the_standard_adds_two_a_pawn_and_over_takes_two():
    assert galdor.vis_modifier(12, 9) == 6
    assert galdor.vis_modifier(12, 14) == -4
    assert galdor.vis_modifier(12, 12) == 0


def test_the_standard_is_double_the_magnitude():
    assert galdor.standard_vis(30) == 12  # The Ol lord's 12 pawns (p. 48).


def test_a_lord_who_agrees_makes_a_deal_with_its_terms():
    c = galdraman()
    forms.bargain(
        saga(),
        c,
        {
            "lord": "The Ol lord",
            "service": "Ward the path",
            "vis_yearly": 9,
            "favour": "One day he will call it in",
            "how": forms.AGREES,
        },
    )
    deal = galdor.deals(c)[0]
    assert (deal.name, deal.vis_yearly, deal.tradition) == (
        "The Ol lord",
        9,
        galdor.TRADITION_ID,
    )
    assert galdor.tithes(c) == 9
    row = tradition_text.bond_rows(c, tradition())[0][1]
    assert "Ward the path; 9 pawns a year; owes: One day he will call it in" in row


def test_a_lord_who_refuses_leaves_no_deal():
    c = galdraman()
    forms.bargain(saga(), c, {"lord": "L", "service": "S", "how": forms.REFUSES})
    assert not galdor.deals(c)
    assert c.diary[-1].name == "Bargain: L"


def rolled(c: Character, die: int) -> dict:
    return {
        "lord": "L",
        "service": "S",
        "how": forms.ROLLS,
        "level": 20,
        "scope": "Specific",
        "length": "A week",
        "duty": "None",
        "offered": 8,
        "die": die,
    }


def test_rolling_the_bargain_com_plus_bargain_plus_die_against_18():
    c = galdraman()
    c.abilities.append(Ability("Bargain", xp=30))  # 3
    forms.bargain(saga(), c, rolled(c, 12))
    assert not galdor.deals(c)  # 2 + 3 + 12 = 17
    forms.bargain(saga(), c, rolled(c, 13))
    assert len(galdor.deals(c)) == 1


def test_a_botched_bargain_lays_the_flaw_for_the_lords_strength():
    class Zeroes(random.Random):
        def randrange(self, *args):
            return 0

        def randint(self, a, b):
            return 0

    c = galdraman()
    forms.bargain(saga(), c, {**rolled(c, 0), "die": None, "weak": True}, Zeroes())
    assert galdor.NUISANCE in [vf.vf_id for vf in c.virtues_flaws]
    assert not galdor.deals(c)
    assert galdor.botch_flaw(weak=False) == galdor.PLAGUED


class _Zeroes(random.Random):
    def randrange(self, *args):
        return 0

    def randint(self, a, b):
        return 0


def test_the_galdor_forms_leave_exports_key_alone():
    letters = {item.action: item.letter for item in actions.MORE_MENU}
    assert letters["export_record"] not in (
        letters["galdor_conjure"],
        letters["galdor_bargain"],
        letters["galdor_bind"],
    )


def test_a_typed_zero_rolls_the_botch_dice():
    c = galdraman()
    forms.bargain(saga(), c, {**rolled(c, 0), "weak": True}, _Zeroes())
    assert galdor.NUISANCE in [vf.vf_id for vf in c.virtues_flaws]
    assert "It botches." in forms.conjure(saga(), c, values(die=0), _Zeroes())


def test_a_lone_minute_and_pawn_are_singular():
    c = galdraman()
    said = forms.conjure(saga(), c, values(level=5, die=9, ritual=True))
    assert "It takes 1 pawn on arrival." in said
    assert not any("1 minutes" in line for line in said)
    said = forms.conjure(saga(), c, values(level=5, die=9))
    assert any("1 minute of song" in line for line in said)


def test_with_nothing_to_choose_the_forms_still_open():
    """A terminal Select can't be empty unless it may be blank: with no Song,
    deal or Craft the form opens, and Save says what is missing."""
    c = Character("c2", "Asgeir", "companion")
    c.virtues_flaws = [
        VirtueFlawInstance(galdor.CONJURING),
        VirtueFlawInstance(galdor.ENCHANTMENT),
    ]
    fields = {f.key: f for f in forms.bind_fields(saga(), c)}
    assert all(fields[key].allow_blank for key in ("deal", "song", "craft"))
    assert forms.conjure_problem(c, values(song=None)) == "Asgeir knows no Song Talent."


def test_a_lords_brackets_stay_in_the_deal_a_binding_names():
    c = galdraman()
    c.bound_beings.append(
        BoundBeing("The [old] lord", galdor.TRADITION_ID, galdor.DEAL)
    )
    field = next(f for f in forms.bind_fields(saga(), c) if f.key == "deal")
    assert field.value == "The [old] lord"
    assert field.options[0][1] == "The [old] lord"


def test_a_deal_is_edited_among_the_bound_beings():
    c = galdraman()
    c.bound_beings.append(
        BoundBeing("L", galdor.TRADITION_ID, galdor.DEAL, service="S")
    )
    ops = tradition_forms.bond_ops(saga(), c, tradition())
    form = ops.edit(0)
    shown = {f.key: f for f in form.fields()}
    assert shown["service"].value == "S"
    form.apply(
        {
            "name": "L",
            "kind": galdor.DEAL,
            "service": "T",
            "vis_yearly": 2,
            "favour": "F",
            "applies_to": "none",
        }
    )
    assert (c.bound_beings[0].service, c.bound_beings[0].vis_yearly) == ("T", 2)


# ---------------------------------------------------------------------------
# Binding


def test_binding_for_life_needs_double_the_level_and_the_frequency():
    assert galdor.bind_needs(10, lifetime=True, frequency=3) == 23
    assert galdor.bind_needs(10, lifetime=False) == 10
    assert galdor.bind_level(10, constant=True) == 15


def test_the_craft_limits_galdor_wisdom_and_the_song():
    c = galdraman()
    # Com 2 + Music 8 + min(8, 5) + min(6, 5) + bonuses 3 + aura 2.
    assert galdor.bind_score(c, "Ol-galdor", "Craft: Weaving", bonuses=3, aura=2) == 25


def bind_values(**more):
    return {
        "name": "Blue Cloak",
        "deal": "The Ol lord",
        "binding": forms.LIFETIME,
        "song": "Ol-galdor",
        "level": 10,
        "duration": "Momentary",
        "uses": 1,
        "craft": "Craft: Weaving",
        "bonuses": 0,
        "aura": 0,
        "aura_realm": "Magic",
        **more,
    }


def test_binding_needs_a_deal_first():
    c = galdraman()
    assert "bargain" in forms.bind_problem(c, bind_values())
    c.bound_beings.append(BoundBeing("The Ol lord", galdor.TRADITION_ID, galdor.DEAL))
    assert forms.bind_problem(c, bind_values()) is None


def test_a_binding_that_takes_goes_on_the_chapters_list():
    c = galdraman()
    # 20: just enough for life.
    forms.bind(saga(), c, bind_values(die=1, bonuses=-1))
    item = c.tradition_effects[-1]
    assert (item.kind, item.rule, item.uses) == (
        galdor.BOUND_ITEM,
        "Galdor Enchantment",
        ["Ol-galdor"],
    )
    assert item.item


def test_a_single_service_has_one_charge_and_a_failed_binding_no_item():
    c = galdraman()
    forms.bind(saga(), c, bind_values(die=1, binding=forms.SERVICE))
    assert c.tradition_effects[-1].charges == 1
    before = len(c.tradition_effects)
    forms.bind(saga(), c, bind_values(die=1, level=25, bonuses=-6))
    assert len(c.tradition_effects) == before


def test_a_years_mead_takes_a_pawn_a_decade():
    assert galdor.mead_pawns(76) == 8


# ---------------------------------------------------------------------------
# The fylgja


def premonitory(*vfs: str) -> Character:
    c = Character("c3", "F", "companion")
    c.virtues_flaws = [VirtueFlawInstance(vf) for vf in ("vf_premonitions", *vfs)]
    return c


def test_premonitions_brings_a_fylgja_of_might_10_and_size_minus_3():
    found = galdor.fylgja_of(premonitory())
    assert (found.might, found.powers, found.size) == (10, (), -3)


def test_no_premonitions_no_fylgja():
    assert galdor.fylgja_of(Character("c3", "F", "companion")) is None


def test_the_books_bear_is_six_virtues():
    bear = premonitory(*["vf_mighty_fylgja"] * 3, *["vf_large_fylgja"] * 3)
    found = galdor.fylgja_of(bear)
    assert found.might == 40
    assert found.powers == ("Phantom", "Spirit Voice", "Corporeality")
    assert found.size == 2


def test_a_first_large_fylgja_allows_size_0():
    assert galdor.fylgja_of(premonitory("vf_large_fylgja")).size == 0


def test_a_trollsons_fetch_is_his_fylgja_and_the_chapter_shows_it():
    c = Character("c3", "T", "companion", traditions=[galdor.TROLLSYNIR_ID])
    c.virtues_flaws = [
        VirtueFlawInstance("vf_fetch"),
        VirtueFlawInstance("vf_mighty_fylgja"),
    ]
    text = tradition_text.bonds_text(traditions.find(galdor.TROLLSYNIR_ID), c)
    assert "Fylgja: Might 20; powers Phantom; Size up to -3." in text


def test_the_fylgja_virtues_repeat_without_limit():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id in (galdor.MIGHTY_FYLGJA, galdor.LARGE_FYLGJA):
        entry = by_id[vf_id]
        assert entry.repeatable and entry.tier == "Minor"
        assert entry.max_count is None


# ---------------------------------------------------------------------------
# The catalog


def test_the_ranks_of_iceland_are_tiered_from_their_printed_points():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    tiers = {
        "vf_bondi": "Free",
        "vf_landowner": "Minor",
        "vf_storbondi": "Minor",
        "vf_godi": "Major",
        "vf_storgodi": "Major",
    }
    for vf_id, tier in tiers.items():
        assert by_id[vf_id].tier == tier
        assert by_id[vf_id].category == "Social Status"


def test_a_song_is_on_the_art_table_and_either_galdor_virtue_opens_it():
    assert access.ability_xp_table("Ol-galdor") == "art"
    c = Character("c3", "S", "companion")
    c.virtues_flaws = [VirtueFlawInstance(galdor.CONJURING)]
    assert access.may_learn(c, "Ol-galdor")
    assert access.may_learn(c, "Galdor Wisdom")


def test_trollsynir_are_gruagachan_with_jotnar_and_no_tattoos():
    trolls = traditions.find(galdor.TROLLSYNIR_ID)
    words = str(trolls)
    assert "Jotnar" in trolls.abilities and "Pictish" not in trolls.abilities
    assert "Pictish" not in str(trolls.training) and "tattoo" not in str(
        trolls.activities
    )
    assert "vf_no_tattoo_magic" in trolls.virtues
    assert "Magic Resistance" in words  # The note that it is dropped.
    assert not trolls.warping is None and trolls.warping.replaces_twilight


def test_a_galdraman_has_warping_not_twilight():
    rule = tradition().warping
    assert rule.replaces_twilight and rule.name == "The Long Hamfaring"


# ---------------------------------------------------------------------------
# Fourth Edition, and the pack


def block(*abilities) -> Fourth:
    return Fourth(
        age=40,
        apparent=None,
        characteristics={},
        confidence=3,
        twilight=0,
        decrepitude=0,
        virtues=[],
        abilities=abilities,
        arts={},
        spells=[],
        traits={},
    )


def test_fourth_keeps_scribe_runes_jotunn_and_curse_as_themselves():
    stat, _ = convert(
        "k",
        block(
            ("Scribe Runes", 3, ""),
            ("Speak Jotunn", 5, ""),
            ("Curse", 4, ""),
            ("Scribe Latin", 2, ""),
        ),
        area="Iceland",
    )
    held = {name: score for name, score, _ in stat["abilities"]}
    assert held["Craft: Runes"] == 3
    assert held["Jotnar"] == 5
    assert held["Curse"] == 4
    assert held["Artes Liberales"] == 2
    assert "Curse" in stat["virtues_flaws"]


def test_the_muspelli_tongue_is_a_catalog_entry():
    names = {e.name for e in catalog.load_ability_catalog()}
    assert "Dead Language: Jotun" in names


@pytest.fixture(scope="module")
def pack() -> Saga:
    return iceland.build()


def person(pack: Saga, name: str) -> Character:
    return next(c for c in pack.characters if c.name == name)


def test_einar_sings_from_a_working_sheet(pack):
    einar = person(pack, "Einar Gamlisson")
    assert einar.traditions == [galdor.TRADITION_ID]
    assert hc.score(einar, "Orlog-galdor") == 11
    assert hc.score(einar, "Music") == 11
    assert galdor.conjures(einar) and galdor.enchants(einar)
    assert hc.holds(einar, "Craft: Runes") and hc.holds(einar, "Jotnar")
    assert hc.holds(einar, "(Magic) Summoning")
    assert not hc.holds(einar, "Summoning")
    # Com +5 + Sing 11 + Galdor Wisdom 12 + Biarg-galdor 10.
    rule = galdor.tradition_rule(tradition(), galdor.CONJURE_RULE)
    score = hc.casting_score(einar, tradition(), rule, ("Biarg-galdor",))
    assert int(score.total) == 38


def test_vifil_holds_two_statuses_and_his_songs(pack):
    vifil = person(pack, "Vifil Halldorson")
    held = [vf.vf_id for vf in vifil.virtues_flaws]
    assert {"vf_galdraman", "vf_bondi"} <= set(held)
    assert hc.score(vifil, "Ol-galdor") == 5
    assert hc.score(vifil, "Hamfarir") == 3
    assert "vf_hamfarir" in held


def test_biorn_and_signy_belong_to_their_traditions(pack):
    assert person(pack, "Biorn Egilsson").traditions == [galdor.TRADITION_ID]
    signy = person(pack, "Signy Grettisdottir")
    assert signy.traditions == [galdor.TROLLSYNIR_ID]
    assert "Magic Resistance 63" in signy.secrets


def test_bard_stays_a_creature_with_named_powers(pack):
    bard = next(c for c in pack.creatures if c.name.startswith("Bard"))
    assert bard.might == 71
    assert "Jotunn Affinity with Frost" in [p.name for p in bard.powers]


def test_the_ranks_of_iceland_points_to_the_catalog(pack):
    ranks = next(n for n in pack.neighbours if n.name == "The Ranks of Iceland")
    assert "Social Status" in ranks.secrets
    assert "Freeman +0" not in ranks.secrets


def test_the_galdor_virtue_alone_shows_the_chapter():
    character = Character(id="c", name="Vifil", type="companion")
    assert not traditions.of(character)
    character.virtues_flaws.append(VirtueFlawInstance("vf_galdor_enchantment", {}))
    assert [t.id for t in traditions.of(character)] == ["trad_galdramen"]
    assert not character.traditions
