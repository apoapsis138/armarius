"""Marriage, the dowry and what follows, on a lord's Marriages tab (Lords
of Men pp. 10-11, 81-82; City & Guild p. 113 with the errata p. 57; the
Definitive Edition pp. 148, 512-513; The Church pp. 37, 47)."""

import dataclasses

import pytest

from ars_magica_manager import actions, manors, marriages, neighbours, place_events
from ars_magica_manager.commands import Confirm, Form, Refuse, Then
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import Character, Marriage, Neighbour, Saga
from ars_magica_manager.models.marriage import (
    ENDED,
    MARRIED,
    MERCHANT,
    VILLEIN,
)
from ars_magica_manager.rules import marriage as rules
from ars_magica_manager.sections import (
    CORE_SECTIONS,
    MARRIAGE_TERMS_SECTION,
    MARRIAGES_SECTION,
)


def _saga() -> Saga:
    karlotte = Character(id="karlotte", name="Karlotte Schönburg", type="companion")
    karlotte.background.year_born = 1201
    wolfram = Character(id="wolfram", name="Wolfram von Schattenbach", type="companion")
    wolfram.background.year_born = 1180
    return Saga(
        id="m",
        name="Marriages",
        characters=[karlotte, wolfram],
        neighbours=[
            Neighbour(id="jurgen", name="Jürgen, Baron Schönburg", kind="lord"),
            Neighbour(id="schatt", name="The Schattenbachs", kind="lord"),
            Neighbour(id="soest", name="Soest", kind="town"),
        ],
        current_year=1220,
        current_season="Summer",
    )


def _lord(saga: Saga, lord_id: str = "jurgen") -> Neighbour:
    found = saga.neighbour(lord_id)
    assert found is not None
    return found


def _form(command: object) -> Form:
    assert isinstance(command, Form)
    return command


def _values(form: Form, **changes: object) -> dict[str, object]:
    """The form's values as it opens (its shown fields), with `changes`."""
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return {
        f.key: values[f.key]
        for f in form.fields()
        if f.show_if is None or f.show_if(values)
    } | {k: v for k, v in changes.items()}


def _arrange(saga: Saga, **changes: object) -> Marriage:
    form = _form(marriages.arrange_form(saga, _lord(saga)))
    values = _values(form, **changes)
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    return saga.marriages[-1]


def _betrothal(saga: Saga) -> Marriage:
    return _arrange(
        saga,
        bride_ref="character:karlotte",
        groom_ref="character:wolfram",
        groom_house="schatt",
        heiress=True,
        lands=6,
        father_consent=False,
        pt_no_bequest=True,
        pt_few_siblings=True,
        note="Proposed by the Schattenbachs.",
    )


# -- the rules --


def test_a_noble_dowry_is_a_share_of_the_land_less_the_eldest_son_and_patrimony():
    """In the French sphere both the eldest son and his patrimony come out
    of the division (LoM p. 11)."""
    m = Marriage(lands=8, patrimony=2, children=4, points=["wealthier", "many"])
    assert rules.noble_sharing(m) == 3
    assert rules.noble_share(m) == 2
    assert rules.larger_and_smaller(m) == (2, 7)
    text = " ".join(rules.dowry_lines(m))
    assert (
        "8 manors less the eldest son's patrimony of 2 / 3 (her parents' 4 "
        "children less the eldest son) = [b]2 manors[/]"
    ) in text
    assert "larger for 2" in text and "smaller for 7" in text
    # Without a patrimony every child shares.
    assert rules.noble_sharing(Marriage(lands=8, children=4)) == 4


def test_a_patrimony_needs_the_eldest_son_counted_among_the_children():
    saga = _saga()
    form = _form(marriages.arrange_form(saga, _lord(saga)))
    assert form.validate is not None
    values = {"bride": "Ada", "groom_ref": "neighbour:jurgen", "family": "noble"}
    assert form.validate(values | {"patrimony": 1, "children": 1})
    assert form.validate(values | {"patrimony": 1, "children": 2}) is None
    assert form.validate(values | {"patrimony": 0, "children": 1}) is None
    assert (
        form.validate(values | {"patrimony": 1, "children": 1, "heiress": True}) is None
    )


def test_an_heiress_brings_no_dowry_but_perhaps_a_dower():
    text = " ".join(rules.dowry_lines(Marriage(heiress=True, lands=6)))
    assert "No dowry" in text and "dower" in text


def test_a_merchants_dowry_is_ten_years_profit_shared_by_his_children():
    m = Marriage(family=MERCHANT, profit=12, children=4)
    assert rules.merchant_coin(m) == 30
    assert "30 Mythic Pounds" in " ".join(rules.dowry_lines(m))
    raised = Marriage(family=MERCHANT, profit=12, standing="two")
    assert "Poor member" in " ".join(rules.dowry_lines(raised))


def test_the_errata_corrects_the_merchants_points_and_nobles_lack_two():
    """C&G p. 113's first and third statements, as the errata p. 57 has
    them; instalments and a show of wealth are a merchant's only."""
    labels = [p.label for p in rules.points_for(MERCHANT)]
    assert labels[0] == "The groom's family is wealthier"
    assert labels[2] == "Not a virgin"
    assert len(rules.points_for(MERCHANT)) == 11
    assert len(rules.points_for("noble")) == 9
    assert rules.points_for(VILLEIN) == ()


def test_how_the_dowry_is_paid_is_worded_for_each_kind_of_bride():
    """A noble's is smaller paid in land or money rather than other rights
    (LoM p. 11); a merchant's larger paid in assets, land among them,
    rather than money (C&G p. 113)."""
    noble = {p.key: p.label for p in rules.points_for("noble")}
    merchant = {p.key: p.label for p in rules.points_for(MERCHANT)}
    assert noble["rights"] == "Paid in other rights, not land or money"
    assert merchant["assets"] == "Paid in assets (land or goods), not money"
    assert "assets" not in noble and "rights" not in merchant


def test_a_saved_shared_goods_statement_loads_as_her_kinds():
    noble = Marriage.from_dict({"bride": "A", "points": ["goods", "many"]})
    assert noble.points == ["rights", "many"]
    merchant = Marriage.from_dict(
        {"bride": "B", "family": "merchant", "points": ["goods"]}
    )
    assert merchant.points == ["assets"]


def test_missing_consent_and_close_kin_are_warned_of():
    found = " ".join(
        rules.warnings(Marriage(her_consent=False, father_consent=False, kin=True))
    )
    assert "no sacrament" in found
    assert "no Christian father may choose" in found
    assert "canon crime" in found
    assert rules.warnings(Marriage()) == []


def test_the_widow_keeps_the_definitive_editions_portion():
    m = Marriage(heiress=True)
    text = rules.ending_text(m, "husband", "Karlotte", "Wolfram")
    assert "profit (not the income) of a third of his land" in text
    assert "returned to her outright" in text
    assert manors.WIDOWS_SHARE == rules.WIDOWS_PORTION


def test_what_her_death_or_a_parting_does_with_the_dowry():
    assert "children" in rules.ending_text(Marriage(custom="italy"), "wife", "K", "W")
    # Only Italy's custom sends it to her children or parents (LoM p. 11):
    # for much of France the books are silent.
    france = rules.ending_text(Marriage(custom="france_manages"), "wife", "K", "W")
    assert "troupe decides" in france and "children" not in france
    assert Marriage.from_dict({"bride": "A", "custom": "italy"}).custom == "italy"
    assert rules.CUSTOM_LABELS["italy"].startswith("Italy:")
    assert rules.CUSTOM_KEEPS["france_manages"] == rules.CUSTOM_KEEPS["italy"]
    assert "keep much" in rules.ending_text(Marriage(custom="france"), "wife", "K", "W")
    heiress = rules.ending_text(Marriage(heiress=True), "wife", "K", "W")
    assert "eldest son" in heiress
    assert "feud" in rules.ending_text(Marriage(), "part", "K", "W")


# -- the record --


def test_a_marriage_survives_a_save_and_a_bad_one_is_named():
    saga = _saga()
    m = _betrothal(saga)
    again = Saga.from_dict(dataclasses.asdict(saga))
    assert again.marriages == [m]
    bad = dataclasses.asdict(m) | {"custom": "Ruritania"}
    with pytest.raises(ValueError, match="Marriage of .*custom"):
        Marriage.from_dict(bad)
    with pytest.raises(ValueError, match="lands can't be negative"):
        Marriage.from_dict(dataclasses.asdict(m) | {"lands": -1})
    with pytest.raises(ValueError, match="should name a character"):
        Marriage.from_dict(dataclasses.asdict(m) | {"bride_ref": "karlotte"})


# -- the form --


def test_arranging_a_marriage_puts_it_on_both_houses_pages():
    saga = _saga()
    m = _betrothal(saga)
    assert m.heiress and m.father_consent is False
    assert m.points == ["no_bequest", "few_siblings"]
    assert marriages.involving(saga, _lord(saga)) == [m]
    assert marriages.involving(saga, _lord(saga, "schatt")) == [m]
    assert (
        marriages.couple(saga, m, "jurgen") == "Karlotte and Wolfram von Schattenbach"
    )
    assert marriages.couple(saga, m, "schatt") == "Wolfram and Karlotte Schönburg"


def test_the_contract_works_the_dowry_out_as_the_form_is_filled():
    saga = _saga()
    form = _form(marriages.arrange_form(saga, _lord(saga)))
    assert form.live is not None and form.inspector == "The Contract"
    text = form.live({"family": "noble", "lands": 6, "children": 2, "pt_many": True})
    assert "6 manors / 2 = [b]3 manors[/]" in text
    assert "larger for 1" in text
    assert "Petition" in text or "petition" in text
    text = form.live({"family": "noble", "lands": "6x", "her_consent": False})
    assert "no sacrament" in text


def test_the_form_refuses_a_marriage_no_page_would_show():
    saga = _saga()
    form = _form(marriages.arrange_form(saga, _lord(saga)))
    assert form.validate is not None
    assert form.validate({"bride_ref": "", "bride": "", "groom": "Otto"})
    assert form.validate(
        {"bride": "Ada", "groom": "Otto", "bride_house": None, "groom_house": None}
    )
    assert form.validate(
        {"bride_ref": "character:wolfram", "groom_ref": "character:wolfram"}
    )
    assert form.validate({"bride": "Ada", "groom_ref": "neighbour:jurgen"}) is None


def test_a_lord_himself_may_marry_and_is_named_for_his_ruler():
    saga = _saga()
    m = _arrange(
        saga,
        groom_ref="neighbour:jurgen",
        bride="Adelheid of Sayn",
        bride_house=None,
        state=MARRIED,
        dowry="Hof Sayn, a manor",
    )
    assert marriages.couple(saga, m, "jurgen") == "Jürgen and Adelheid of Sayn"
    assert marriages.houses(m) == ["jurgen"]


# -- the tab --


def test_a_lord_has_a_marriages_tab_after_his_manors():
    tab_ids = [t.tab_id for t in neighbours.KINDS["lord"].more]
    assert tab_ids == [
        "tab-nb-manors",
        "tab-nb-marriages",
        "tab-nb-tables",
        "tab-nb-lord-diary",
    ]
    assert CORE_SECTIONS[MARRIAGES_SECTION] == {"add", "edit", "remove"}
    assert CORE_SECTIONS[MARRIAGE_TERMS_SECTION] == {"edit"}
    saga = _saga()
    ops = neighbour_forms.neighbour_ops(saga, _lord(saga))
    assert MARRIAGES_SECTION in ops and MARRIAGE_TERMS_SECTION in ops


def test_the_tab_lists_the_marriages_and_the_terms_of_the_standing_one():
    saga = _saga()
    lord = _lord(saga)
    late = _arrange(
        saga, groom_ref="neighbour:jurgen", bride="Adelheid of Sayn",
        dowry="Hof Sayn, a manor",
    )  # fmt: skip
    late.ended, late.state, late.end_year = "wife", ENDED, 1208
    _betrothal(saga)
    grid = marriages.marriages_grid(saga, lord)
    assert [r[0] for r in grid.rows] == [
        "Jürgen and Adelheid of Sayn",
        "Karlotte and Wolfram von Schattenbach",
    ]
    assert grid.rows[0][3] == "Ended: her death, 1208"
    assert grid.rows[1][2:] == ["none: she is the heiress", "Betrothed"]
    assert marriages.terms_title(saga, lord) == "Karlotte and Wolfram: the Terms"
    facts = {f.label: f.value for f in marriages.terms_facts(saga, lord)}
    assert facts["Bride"] == "Karlotte Schönburg, 19, heiress"
    assert facts["Groom"] == "Wolfram von Schattenbach, 40"
    assert facts["Consent"] == "hers: given; her father's: withheld"
    text = marriages.terms_text(saga, lord)
    assert "keeps her inheritance in her own right" in text
    assert "Her father has not consented" in text
    ledger = marriages.marriages_ledger(saga, lord)
    assert ledger[1].badge == "Betrothed" and ledger[1].tone == "text-warning"
    info = marriages.marriage_info(saga, lord, 0)
    assert "Ended: her death, 1208" in info


def test_delete_asks_and_removes_the_marriage_from_both_pages():
    saga = _saga()
    _betrothal(saga)
    confirm = marriages.ops(saga, _lord(saga)).remove(0)  # type: ignore[misc]
    assert isinstance(confirm, Confirm)
    assert "Karlotte and Wolfram von Schattenbach" in confirm.question
    confirm.apply()
    assert saga.marriages == []


def test_edit_terms_edits_the_standing_marriage_or_refuses():
    saga = _saga()
    assert isinstance(marriages.terms_edit(saga, _lord(saga)), Refuse)
    _betrothal(saga)
    form = _form(marriages.terms_edit(saga, _lord(saga)))
    assert form.title == "Edit the Marriage"


# -- End a Marriage, and the inheritance --


def test_end_a_marriage_is_more_on_the_marriages_list():
    assert actions.MORE_SECTIONS["end_marriage"] == MARRIAGES_SECTION
    assert "end_marriage" in menu_forms.NOT_ON_PAGES


def test_ending_a_marriage_notes_both_houses_diaries():
    saga = _saga()
    m = _betrothal(saga)
    form = _form(marriages.end_form(saga, _lord(saga), 0))
    assert form.live is not None and "feud" in form.live({"how": "part"})
    lines = form.apply({"how": "part", "season": "Winter", "year": 1231})
    assert m.ended == "part" and m.state == ENDED and m.end_year == 1231
    assert "feud" in " ".join(lines)
    for lord in ("jurgen", "schatt"):
        assert "separated" in place_events.diary(_lord(saga, lord))[-1]["text"]
    for who in ("karlotte", "wolfram"):
        character = saga.character(who)
        assert character is not None and character.diary[-1].season == "Winter"
    assert isinstance(marriages.end_form(saga, _lord(saga), 0), Refuse)


def test_a_lord_who_dies_first_goes_on_to_settle_his_inheritance():
    saga = _saga()
    _arrange(saga, groom_ref="neighbour:jurgen", bride="Adelheid", state=MARRIED)
    assert manors.settle_fields(saga, _lord(saga))[3].value is True
    form = _form(marriages.end_form(saga, _lord(saga), 0))
    follows = form.apply({"how": "husband", "season": "Winter", "year": 1231})
    assert isinstance(follows, Then)
    settle = _form(follows.step)
    widow = next(f for f in settle.fields() if f.key == "widow")
    assert widow.value is True
    lines = settle.apply({"heir": "Karlotte", "custom": "Primogeniture", "widow": True})
    assert "profit (not the income) of a third" in " ".join(lines)


def test_settle_an_inheritance_leaves_no_widow_without_a_marriage():
    saga = _saga()
    widow = next(f for f in manors.settle_fields(saga, _lord(saga)) if f.key == "widow")
    assert widow.value is False


def test_the_daughters_hint_gives_both_customs_and_the_shared_siblings():
    """DE p. 512 (LoM p. 10 agrees): where the eldest takes all, custom
    decides between the land intact and divided between the sisters; where
    all the siblings share, daughters inherit beside their brothers."""
    saga = _saga()
    by = next(f for f in manors.settle_fields(saga, _lord(saga)) if f.key == "custom")
    assert by.hint == manors.DAUGHTERS_HINT
    assert "intact" in by.hint and "divided between the sisters" in by.hint
    assert "alongside their brothers" in by.hint
