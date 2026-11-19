"""Where: the page on show as a kind and an id, answered from the saga."""

import pytest
from support import everything_saga

from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.where import Where

#: Each kind of record's page in the test saga: its id and name.
RECORDS = [
    (NodeKind.CHARACTER, "mag1", "Leandro"),
    (NodeKind.COVENANT, "cov1", "Keep"),
    (NodeKind.LABORATORY, "lab1", "Tower"),
    (NodeKind.FAMILIAR, "fam1", "Corax"),
    (NodeKind.TRIBUNAL, "rhine", "Rhine"),
    (NodeKind.NEIGHBOUR, "gottfried", "Gottfried of Arnsberg"),
    (NodeKind.CREATURE, "aeolus", "Aeolus"),
]


@pytest.mark.parametrize(("kind", "record_id", "name"), RECORDS)
def test_a_records_page_finds_it_names_it_and_keys_it(kind, record_id, name):
    saga = everything_saga()
    where = Where(kind, record_id)
    record = where.record(saga)
    assert record is not None and record.id == record_id
    assert where.name(saga) == name
    assert where.presence_key() == f"{_ref(kind)}:{record_id}"
    assert where.shows_record and not where.whole_saga
    assert Where.of(record) == where


@pytest.mark.parametrize(("kind", "record_id", "name"), RECORDS)
def test_a_deleted_record_is_gone(kind, record_id, name):
    saga = everything_saga()
    assert not Where(kind, record_id).gone(saga)
    assert Where(kind, "deleted").gone(saga)
    assert Where(kind, "deleted").record(saga) is None
    assert Where(kind, "deleted").name(saga) == ""


def test_only_a_character_covenant_or_laboratory_has_a_creation_record():
    saga = everything_saga()
    made = {
        kind
        for kind, record_id, _ in RECORDS
        if Where(kind, record_id).creation_record(saga)
    }
    assert made == {NodeKind.CHARACTER, NodeKind.COVENANT, NodeKind.LABORATORY}


def test_a_page_brings_its_covenant_and_a_familiars_magus():
    saga = everything_saga()
    assert Where(NodeKind.CHARACTER, "mag1").covenant(saga).id == "cov1"
    assert Where(NodeKind.LABORATORY, "lab1").covenant(saga).id == "cov1"
    familiar = Where(NodeKind.FAMILIAR, "fam1")
    assert familiar.character(saga).id == "mag1"
    assert familiar.covenant(saga).id == "cov1"
    # A laboratory's page is no character's.
    assert Where(NodeKind.LABORATORY, "lab1").character(saga) is None


def test_the_whole_sagas_pages_and_a_covenants_lists_are_named():
    saga = everything_saga()
    assert Where().name(saga) == saga.name
    assert Where(NodeKind.REGION).name(saga) == "The Region"
    assert Where(NodeKind.REGION).whole_saga
    assert Where(NodeKind.CHARACTER_GROUP, "cov1").name(saga) == "Characters in Keep"
    assert Where(NodeKind.LABORATORY_GROUP).name(saga) == "Laboratories"
    assert Where(NodeKind.CHARACTER_GROUP, "cov1").covenant(saga).id == "cov1"
    for where in (Where(), Where(NodeKind.CHARACTER_GROUP, "cov1")):
        assert where.record(saga) is None
        assert where.presence_key() is None
        assert not where.gone(saga)


def test_the_menu_page_is_built_from_where():
    saga = everything_saga()
    page = menu_forms.page_at(saga, Where(NodeKind.FAMILIAR, "fam1"), section="x")
    assert page.kind == NodeKind.FAMILIAR and page.section == "x"
    assert page.familiar.id == "fam1"
    assert page.character.id == "mag1" and page.covenant.id == "cov1"
    assert page.record_to_delete().id == "fam1"


def _ref(kind: NodeKind) -> str:
    return {
        NodeKind.CHARACTER: "characters",
        NodeKind.COVENANT: "covenants",
        NodeKind.LABORATORY: "laboratories",
        NodeKind.FAMILIAR: "familiars",
        NodeKind.TRIBUNAL: "tribunals",
        NodeKind.NEIGHBOUR: "neighbours",
        NodeKind.CREATURE: "creatures",
    }[kind]
