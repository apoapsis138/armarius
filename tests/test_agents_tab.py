"""The Agents tab's rules and wording (Lords of Men pp. 22-25): the limit
counts recruited agents only, those being won are a separate count, an
Adventure season brings as much Agency experience, and More's commands
are offered only for a chosen agent they can act on."""

import random
from dataclasses import dataclass, field

from ars_magica_manager import actions, seasons
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Act, Form, Refuse
from ars_magica_manager.forms import agents as agent_forms
from ars_magica_manager.models import (
    Ability,
    Agent,
    Character,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from ars_magica_manager.rules import activities as season_rules
from ars_magica_manager.rules import agents as ag
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.sections import AGENTS_SECTION


def _lord() -> Character:
    """Presence +2, Communication +1, Intrigue 2, Leadership 3, Charm 4."""
    lord = Character(id="lord", name="Lord Robert", type="companion")
    lord.characteristics.presence = 2
    lord.characteristics.communication = 1
    lord.abilities = [
        Ability("Intrigue", xp=ability_xp(2)),
        Ability("Leadership", xp=ability_xp(3)),
        Ability("Charm", xp=ability_xp(4)),
    ]
    lord.agents = [
        Agent("Sir Konrad", resistance=0, impressed=True, bond_trait="Owes", bond=2),
        Agent("Udo", resistance=0, impressed=True, bond=0),
        Agent("Father Bertolf", status="minor_virtue", impressed=True, resistance=2),
        Agent("Magister Hartwig", status="minor_virtue", modifiers=["rival"]),
    ]
    lord.agency_xp = 7
    return lord


def test_the_limit_counts_recruited_agents_and_the_others_are_pending():
    lord = _lord()
    # 2 x (Presence 2 + the higher of Intrigue 2 and Leadership 3 - Gift 0).
    assert ag.character_max_agents(lord) == 10
    assert ag.kept(lord) == 2
    assert ag.pending(lord) == 2
    header = agent_forms.header(lord)
    assert "Agents: [b]2 of 10[/]" in header
    assert "Leadership 3" in header
    assert "2 being recruited" in header
    assert "Agency experience: [b]7[/] unspent" in header


def test_the_limit_is_at_least_one_and_turns_red_when_passed():
    lord = Character(id="x", name="Shy", type="companion")
    lord.characteristics.presence = -3
    assert ag.character_max_agents(lord) == 1
    lord.agents = [Agent("A", resistance=0), Agent("B", resistance=0)]
    assert "[$text-error]2 of 1[/]" in agent_forms.header(lord)
    assert "being recruited" not in agent_forms.header(lord)


def test_the_list_shows_status_bond_resistance_and_resources():
    lord = _lord()
    lord.agents[0].resources = "Single Weapon 6; six men-at-arms"
    table = agent_forms.table(lord)
    assert table.columns == ["Name", "Status", "Bond", "Resistance", "Resources"]
    assert table.rows[0][1:4] == [
        "Free Social Virtue",
        "Owes +2",
        "[$text-success]agent[/]",
    ]
    assert table.rows[2][3] == "2, impressed"
    # Minor Social Virtue 1 + serves a rival 9.
    assert table.rows[3][3] == "10"
    rows = [row for _, row in agent_forms.rows(lord)]
    assert "Minor Virtue" in rows[2] and "Single Weapon 6…" in rows[0]


def test_the_details_follow_how_far_he_is_won():
    lord = _lord()
    hartwig = agent_forms.info(lord, 3, wide=True)
    assert "Resistance[/] [b]10[/]" in hartwig
    # Stress die + Presence 2 + Leadership 3 - Gift 0 against 6.
    assert "Stress die + [b]5[/]" in hartwig and "against 6" in hartwig
    assert "55 Agency experience" in hartwig  # 10 + 9 + ... + 1
    bertolf = agent_forms.info(lord, 2, wide=False)
    assert "3 Agency experience recruits him (2 + 1)" in bertolf
    konrad = agent_forms.info(lord, 0, wide=True)
    # Communication 1 + Charm 4 + Bond 2 - Gift 0.
    assert "stress die + [b]7[/]" in konrad
    assert "Tasks for Agents" in konrad
    udo = agent_forms.info(lord, 1, wide=True)
    assert "A Bond of +1 is needed" in udo


def test_a_coerced_agent_notes_difficult_underlings_and_a_story_flaw():
    lord = _lord()
    lord.agents[0].coerced = True
    text = agent_forms.info(lord, 0, wide=False)
    assert "Difficult Underlings" in text and "Blackmail or Dark Secret" in text
    assert agent_forms.table(lord).rows[0][1].endswith(", coerced")
    assert ag.hates_principal(Agent("X", modifiers=["dominated"]))


def test_an_adventure_season_brings_as_much_agency_experience():
    lord = _lord()
    lord.agency_xp = 0
    saga = Saga(id="s", name="S", characters=[lord])
    seasons.set_plan(
        saga,
        SeasonPlan(
            lord.id,
            1220,
            "Spring",
            season_rules.ADVENTURE,
            [XpAllocation("ability:Charm", 5), XpAllocation("ability:Intrigue", 3)],
            source_quality=8,
        ),
    )
    seasons.apply(saga, seasons.resolve(saga))
    assert lord.agency_xp == 8
    assert "Agency experience +8" in lord.diary[-1].details


def test_other_seasons_bring_no_agency_experience():
    for activity in (season_rules.EXPOSURE, season_rules.PRACTICE):
        lord = _lord()
        saga = Saga(id="s", name="S", characters=[lord])
        seasons.set_plan(
            saga,
            SeasonPlan(
                lord.id, 1220, "Spring", activity, [XpAllocation("ability:Charm")]
            ),
        )
        seasons.apply(saga, seasons.resolve(saga))
        assert lord.agency_xp == 7, activity


def test_impress_rolls_and_marks_him_impressed_on_a_success():
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord])
    step = agent_forms.impress(saga, lord, 3, random.Random(3))
    assert isinstance(step, Act)
    assert step.title == "Impress: Magister Hartwig"
    lines = step.apply()
    assert lord.agents[3].impressed == ("is impressed" in "\n".join(lines))
    assert isinstance(agent_forms.impress(saga, lord, 2), Refuse)


def test_spending_wears_resistance_down_and_raises_a_bond():
    lord = _lord()
    step = agent_forms.spend(lord, 2)
    assert isinstance(step, Form)
    assert step.validate is not None
    assert step.validate({"how": "resistance", "xp": 1})  # less than 2
    step.apply({"how": "resistance", "xp": 3})
    assert lord.agents[2].resistance == 0 and lord.agency_xp == 4
    bond = agent_forms.spend(lord, 0)
    assert isinstance(bond, Form)
    bond.apply({"how": "bond", "xp": 4})
    assert lord.agents[0].bond == 2 and lord.agents[0].bond_xp == 4
    lord.silver = 3
    assert bond.validate is not None
    assert bond.validate({"how": "pounds", "pounds": 4})
    said = bond.apply({"how": "pounds", "pounds": 1})  # 5 xp: 9 of 15 to +3
    assert lord.agents[0].bond_xp == 9 and lord.silver == 2
    assert said[0].startswith("1 pound for 5 Agency experience")
    assert "carries only 2 pounds" in bond.validate({"how": "pounds", "pounds": 4})
    lord.silver = 1
    unspent = agent_forms._spend_fields(lord, lord.agents[0])[0].value
    assert "1 pound of silver" in str(unspent)


def test_a_task_needs_a_bond_and_its_inspector_reads_the_chosen_ability():
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord])
    assert isinstance(agent_forms.set_task(saga, lord, 1), Refuse)
    step = agent_forms.set_task(saga, lord, 0)
    assert isinstance(step, Form) and step.live is not None
    text = step.live(
        {"ability": "Leadership", "task": "secret", "timeframe": "day", "risk": "death"}
    )
    # 9 + 3 + 6; Communication 1 + Leadership 3 + Bond 2.
    assert "Ease Factor [b]18[/]" in text
    assert "a stress die + [b]6[/]" in text and "5 botch dice" in text


@dataclass
class _Facts:
    """What actions.available asks, on Lord Robert's Agents list."""

    character: Character
    row: int | None
    saga: Saga = field(default_factory=lambda: Saga(id="s", name="S"))
    selected_kind: NodeKind | None = NodeKind.CHARACTER
    selected_covenant: None = None
    selected_laboratory: None = None

    @property
    def selected_character(self) -> Character:
        return self.character

    def active_section(self) -> str | None:
        return AGENTS_SECTION

    def player_may(self, action: str) -> bool:
        return True

    def on_record(self) -> bool:
        return False

    def chosen_row(self, section: str) -> int | None:
        return self.row


def test_more_offers_each_command_only_for_an_agent_it_can_act_on():
    lord = _lord()

    def offered(row: int) -> list[str]:
        facts = _Facts(lord, row)
        return [
            action
            for action in (
                "impress_agent",
                "spend_agency_xp",
                "set_agent_task",
                "resolve_agent_task",
            )
            if actions.available(action, facts)  # type: ignore[arg-type]
        ]

    assert offered(0) == [
        "spend_agency_xp",
        "set_agent_task",
        "resolve_agent_task",
    ]  # Bond +2
    assert offered(1) == ["spend_agency_xp", "resolve_agent_task"]  # Bond 0
    assert offered(2) == ["spend_agency_xp"]  # impressed, being won
    assert offered(3) == ["impress_agent"]  # not yet impressed
    lord.agency_xp = 0
    assert offered(2) == []


def test_a_task_band_sets_the_ease_factor_and_the_risk_its_botch_dice():
    assert {key: top for key, (_, top) in ag.TASK_BANDS.items()} == {
        "easy": 6,
        "hard": 12,
        "impressive": 18,
    }
    assert [ag.band_of(ease) for ease in (3, 6, 7, 12, 18, 19)] == [
        "easy",
        "easy",
        "hard",
        "hard",
        "impressive",
        None,
    ]
    assert [ag.botch_dice(r) for r in ag.RISK] == [None, 1, 3, 5]
    band = next(f for f in agent_forms.resolve_fields(Agent("A")) if f.key == "band")
    assert band.fills is not None and band.fills({"band": "hard"}) == {"ease": 12}


def test_resolving_needs_an_agent_and_its_inspector_reads_his_roll():
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord])
    assert isinstance(agent_forms.resolve(saga, lord, 2), Refuse)  # being won
    assert isinstance(agent_forms.resolve(saga, lord, 9), Refuse)
    assert isinstance(agent_forms.resolve(saga, lord, 1), Form)  # Bond 0 too
    step = agent_forms.resolve(saga, lord, 0)
    assert isinstance(step, Form) and step.live is not None
    assert step.help_id == "agent-task-resolve"
    values = {
        "using": "Dexterity + Legerdemain",
        "total": 7,
        "band": "hard",
        "ease": 12,
        "risk": "injury",
    }
    text = step.live(values)
    assert "a stress die + [b]7[/]" in text and "Ease Factor [b]12[/]" in text
    assert "3 botch dice" in text and "a die of [b]5+[/]" in text
    assert "text-warning" not in text
    calm = step.live({**values, "risk": "none", "ease": 15})
    assert "a simple die" in calm and "botch" not in calm
    assert "more than this band's 12: an impressive task" in calm


def test_resolving_rolls_his_scores_and_writes_the_diary():
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord])
    step = agent_forms.resolve(saga, lord, 0, random.Random(1))
    assert isinstance(step, Form)
    said = step.apply(
        {
            "what": "steal the ring",
            "using": "Dex + Legerdemain",
            "total": 20,
            "band": "easy",
            "ease": 6,
            "risk": "none",
        }
    )
    entry = lord.diary[-1]
    assert entry.name == "Sir Konrad's task: steal the ring"
    assert "+ 20 (Dex + Legerdemain)" in entry.details
    assert "He does it, by" in entry.details  # a simple die can't botch
    assert (entry.year, entry.season) == (saga.current_year, saga.current_season)
    assert said[-1] == "Written in Lord Robert's Diary."
    hopeless = agent_forms.resolve(saga, lord, 0, random.Random(1))
    assert isinstance(hopeless, Form)
    hopeless.apply({"total": -20, "band": "impressive", "ease": 18, "risk": "none"})
    assert "He fails, by" in lord.diary[-1].details
    assert lord.diary[-1].name == "Sir Konrad's task"
