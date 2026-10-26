"""The schools of certamen and Tremere Promotion by Force (HoH: True
Lineages pp. 123-125, 135-139)."""

import pytest

from ars_magica_manager.forms.character import hermetic_fields
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    HermeticBackground,
    Saga,
)
from ars_magica_manager.models.character import CERTAMEN_STYLES
from ars_magica_manager.rules import certamen, certamen_styles, sigils
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(
    school: str = "",
    house: str = "house_tremere",
    finesse: int = 3,
    heartbeast: int = 0,
) -> Character:
    abilities = [
        Ability("Finesse", xp=ability_xp(finesse)),
        Ability("Penetration", xp=ability_xp(2)),
        Ability("Parma Magica", xp=ability_xp(4)),
    ]
    if heartbeast:
        abilities.append(Ability("Heartbeast", xp=ability_xp(heartbeast)))
    return Character(
        id="m",
        name="Gaius",
        type="magus",
        characteristics=Characteristics(
            quickness=1, presence=2, perception=1, intelligence=2, stamina=1
        ),
        arts={
            "muto": ArtScore(xp=art_xp(8)),
            "corpus": ArtScore(xp=art_xp(8)),
            "rego": ArtScore(xp=art_xp(8)),
            "mentem": ArtScore(xp=art_xp(8)),
        },
        abilities=abilities,
        hermetic=HermeticBackground(house=house, certamen_school=school),
    )


def _base(magus: Character, technique: str = "Rego", form: str = "Mentem"):
    return certamen.certamen_totals(magus, technique, form)


def test_every_style_has_a_page_in_the_chapter_and_a_way_to_fight():
    assert len(certamen_styles.STYLES) == 15
    for style in certamen_styles.STYLES:
        assert 135 <= style.page <= 138, style.id
        assert style.follower or style.dabbler, style.id
    assert {s.id for s in certamen_styles.STYLES} - {
        s.id for s in certamen_styles.SCHOOLS
    } == {"bone_biting", "charon"}


def test_the_model_knows_every_style_id():
    assert CERTAMEN_STYLES == tuple(s.id for s in certamen_styles.STYLES)


def test_the_gladiator_school_is_the_basic_rules():
    magus = _magus("gladiator")
    styled = certamen.styled_totals(magus, "Rego", "Mentem", "gladiator", follower=True)
    assert styled == _base(magus)
    assert certamen.trade_limit(magus, "gladiator", "Rego", follower=True) == 0


def test_an_andabatus_trades_defence_for_attack():
    magus = _magus("andabatus")
    base = _base(magus)
    # A follower: up to twice Finesse on Attack, the same off Defence.
    assert certamen.trade_limit(magus, "andabatus", "Rego", follower=True) == 6
    t = certamen.traded(magus, base, "andabatus", "Rego", 6, follower=True)
    assert t.attack_technique == base.attack_technique + 6
    assert t.attack_form == base.attack_form + 6
    assert t.defence_form == base.defence_form - 6
    # In his style: up to Finesse on Attack, twice that off Defence.
    assert certamen.trade_limit(magus, "andabatus", "Rego", follower=False) == 3
    t = certamen.traded(magus, base, "andabatus", "Rego", 3, follower=False)
    assert t.attack_technique == base.attack_technique + 3
    assert t.defence_technique == base.defence_technique - 6
    with pytest.raises(ValueError):
        certamen.traded(magus, base, "andabatus", "Rego", 4, follower=False)


def test_a_follower_must_belong_to_the_school():
    magus = _magus("gladiator")
    with pytest.raises(ValueError, match="not a follower"):
        certamen.trade_limit(magus, "andabatus", "Rego", follower=True)
    # Anyone may fight in a style.
    assert certamen.trade_limit(magus, "andabatus", "Rego", follower=False) == 3


def test_a_hoplomachus_turns_attack_into_twice_the_defence():
    magus = _magus("hoplomachus")
    base = _base(magus)
    t = certamen.traded(magus, base, "hoplomachus", "Rego", 3, follower=True)
    assert t.attack_technique == base.attack_technique - 3
    assert t.defence_form == base.defence_form + 6
    held = certamen.held_back(magus, base, "hoplomachus", "Rego", follower=True)
    assert held.defence_form == base.defence_form + 9
    held = certamen.held_back(magus, base, "hoplomachus", "Rego", follower=False)
    assert held.defence_form == base.defence_form + 6
    # His style has no trade, only the held-back round.
    assert certamen.trade_limit(magus, "hoplomachus", "Rego", follower=False) == 0


def test_a_provocator_trades_initiative_for_resistance_in_later_rounds():
    magus = _magus("provocator")
    base = _base(magus)
    t = certamen.traded(magus, base, "provocator", "Rego", 2, follower=True)
    assert (t.initiative, t.resistance) == (base.initiative - 2, base.resistance + 2)
    assert certamen_styles.style("provocator").follower.lasting


def test_a_retiarius_pays_for_initiative_from_his_next_advantages():
    magus = _magus("retiarius")
    base = _base(magus)
    t = certamen.traded(magus, base, "retiarius", "Rego", 3, follower=True)
    assert t.initiative == base.initiative + 3
    assert t.attack_technique == base.attack_technique
    assert certamen.advantage_cost("retiarius", 3, follower=True) == 6
    assert certamen.advantage_cost("andabatus", 3, follower=True) == 0


def test_a_saggitarius_hit_costs_one_fatigue_level_at_most():
    magus = _magus()
    base = _base(magus)
    assert certamen.trade_limit(magus, "saggitarius", "Rego", follower=False) == 9
    t = certamen.traded(magus, base, "saggitarius", "Rego", 9, follower=False)
    assert t.attack_form == base.attack_form + 9
    assert t.defence_form == base.defence_form - 9
    rule = certamen_styles.style("saggitarius").dabbler
    assert certamen.fatigue_lost(30, 5, most=rule.max_fatigue) == 1


def test_a_laquerius_noose_costs_his_defence_only():
    magus = _magus("laquerius")
    base = _base(magus)
    t = certamen.traded(magus, base, "laquerius", "Rego", 2, follower=True)
    assert t.defence_form == base.defence_form - 2
    assert t.attack_technique == base.attack_technique
    assert "rest of the duel" in certamen_styles.style("laquerius").follower.forgo
    assert "one round" in certamen_styles.style("laquerius").dabbler.forgo


@pytest.mark.parametrize(
    ("follower", "levels"),
    [(True, 4), (False, 3)],  # (21 - 10) / 3 -> 4; / 4 -> 3, a fraction counting
)
def test_a_scissor_hit_after_a_skipped_attack_cuts_deeper(follower, levels):
    rule = certamen_styles.style("scissor").rule(follower)
    assert rule is not None and rule.divisor_after_skip is not None
    assert certamen.fatigue_lost(21, 10, divisor=rule.divisor_after_skip) == levels
    assert certamen.fatigue_lost(21, 10) == 3


def test_a_velitus_wears_down_resistance():
    assert certamen.worn_resistance(1, 5, "velitus", follower=True) == -1
    assert certamen.worn_resistance(1, 5, "velitus", follower=False) == 0
    assert certamen.worn_resistance(6, 7, "velitus", follower=False) == 4
    assert certamen.worn_resistance(6, 7, "andabatus", follower=True) == 6


def test_a_bestiarius_uses_his_heartbeast_in_muto_duels():
    magus = _magus("bestiarius", house="house_bjornaer", finesse=1, heartbeast=4)
    base = certamen.certamen_totals(magus, "Muto", "Corpus")
    styled = certamen.styled_totals(
        magus, "Muto", "Corpus", "bestiarius", follower=True
    )
    assert styled.initiative == 1 + 4  # Quickness + Heartbeast
    assert styled.resistance == base.resistance + 8
    dabbling = certamen.styled_totals(
        magus, "Muto", "Corpus", "bestiarius", follower=False
    )
    assert (dabbling.initiative, dabbling.resistance) == (
        base.initiative,
        base.resistance + 4,
    )
    assert certamen.style_score(magus, "bestiarius", "Muto") == 4
    assert certamen.style_score(magus, "bestiarius", "Rego") == 1
    # Outside Muto, a follower fights by the basic rules, Finesse and all.
    rego = certamen.styled_totals(magus, "Rego", "Mentem", "bestiarius", follower=True)
    assert rego == _base(magus)
    # A Bjornaer in the style adds Heartbeast to Resistance in any duel.
    rego_style = certamen.styled_totals(
        magus, "Rego", "Mentem", "bestiarius", follower=False
    )
    assert rego_style.resistance == _base(magus).resistance + 4
    assert rego_style.initiative == _base(magus).initiative
    muto_mentem = certamen.styled_totals(
        magus, "Muto", "Mentem", "bestiarius", follower=False
    )
    base_mentem = certamen.certamen_totals(magus, "Muto", "Mentem")
    assert muto_mentem.resistance == base_mentem.resistance + 4
    with pytest.raises(ValueError, match="house_bjornaer"):
        certamen.styled_totals(_magus(), "Muto", "Corpus", "bestiarius", follower=False)


def test_styles_with_no_followers_are_fought_only_in_their_style():
    magus = _magus()
    with pytest.raises(ValueError):
        certamen.styled_totals(magus, "Rego", "Mentem", "charon", follower=True)
    certamen.styled_totals(magus, "Rego", "Mentem", "bone_biting", follower=False)


def test_the_essedarius_brave_check():
    assert certamen_styles.essedarius_target(0) == 3
    assert certamen_styles.essedarius_target(2) == 7


def test_an_unknown_school_is_refused_on_load():
    with pytest.raises(ValueError, match="school of certamen"):
        HermeticBackground.from_dict({"certamen_school": "boxing"})
    assert HermeticBackground.from_dict({}).certamen_school == ""
    with pytest.raises(LookupError):
        certamen_styles.style("boxing")


def test_the_sheet_names_the_school():
    assert certamen.school_text(_magus()) == ""
    text = certamen.school_text(_magus("hoplomachus"))
    assert text.startswith("Certamen school: Hoplomachus, the Hoplites")
    assert "HoH: TL p. 137" in text
    assert "not his House's style" in certamen.school_text(_magus("bestiarius"))


def test_the_hermetic_form_offers_the_schools():
    fields = {f.key: f for f in hermetic_fields(HermeticBackground())}
    school = fields["certamen_school"]
    values = [value for _, value in school.options]
    assert values[0] == "" and "gladiator" in values and "charon" not in values
    challenged = fields["sigil_challenged"]
    assert challenged.show_if is not None
    assert challenged.show_if({"house": "house_tremere"})
    assert not challenged.show_if({"house": "house_tremere", "holds_own_sigil": True})


# -- Promotion by Force ---------------------------------------------------------


def _tremere(
    name: str,
    parens: str = "",
    holds_own_sigil: bool = False,
    sigil_challenged: bool = False,
) -> Character:
    return Character(
        id=name,
        name=name,
        type="magus",
        hermetic=HermeticBackground(
            house="house_tremere",
            parens=parens,
            holds_own_sigil=holds_own_sigil,
            sigil_challenged=sigil_challenged,
        ),
    )


def test_decennials_fall_every_ten_years_from_1218():
    assert sigils.decennial(1218) and sigils.decennial(1228)
    assert not sigils.decennial(1220)
    assert sigils.next_decennial(1220) == 1228
    assert sigils.next_decennial(1228) == 1228


def test_a_filius_has_one_free_challenge_then_waits_for_decennials():
    young = _tremere("Young", parens="Elder")
    assert sigils.sigil_challenge(young, 1220)[0]
    sigils.challenge_for_sigil(young, 1220, won=False)
    assert young.hermetic.sigil_challenged and not young.hermetic.holds_own_sigil
    may, why = sigils.sigil_challenge(young, 1221)
    assert not may and "1228" in why
    with pytest.raises(ValueError, match="1228"):
        sigils.challenge_for_sigil(young, 1221, won=True)
    sigils.challenge_for_sigil(young, 1228, won=True)
    assert young.hermetic.holds_own_sigil
    assert sigils.sigil_challenge(young, 1238) == (False, "")


def test_the_sheet_line_says_when_he_may_challenge():
    elder = _tremere("Elder", holds_own_sigil=True)
    young = _tremere("Young", parens="Elder", sigil_challenged=True)
    saga = Saga(id="s", name="S", characters=[elder, young])
    saga.current_year = 1222
    assert "Decennial of 1228" in sigils.sigil_text(saga, young)


def test_exarch_challenges_and_vis_between_tremere():
    assert sigils.may_challenge_exarch(
        challenged_before=False, house_faces_rivals=False, deposed_exarch=False
    )
    for blocked in ("challenged_before", "house_faces_rivals", "deposed_exarch"):
        flags = {
            "challenged_before": False,
            "house_faces_rivals": False,
            "deposed_exarch": False,
        }
        flags[blocked] = True
        assert not sigils.may_challenge_exarch(**flags)
    a, b = _tremere("A"), _tremere("B")
    assert not sigils.vis_honourable(a, b)
    b.hermetic.house = "house_flambeau"
    assert sigils.vis_honourable(a, b)
    assert [p.page for p in sigils.PROMOTIONS] == [123, 123, 124, 125]
