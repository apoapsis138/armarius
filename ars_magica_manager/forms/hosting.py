"""Host for Players and Stop Hosting: the forms that start and stop the
host (hosting.HOST) from either front-end's saga page."""

from __future__ import annotations

from typing import Any

from .. import hosting
from ..commands import Command, Confirm, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..remote.plan import RemotePlan

#: The address choice that opens a field to type one in.
OTHER = "other"


def _address_options(current: str) -> list[tuple[str, str]]:
    found = [hosting.LOCALHOST, *hosting.addresses()]
    if current not in found and current != OTHER:
        found.append(current)
    return [(hosting.address_label(a), a) for a in found] + [
        ("Another address...", OTHER)
    ]


def plan_of(values: dict[str, Any]) -> hosting.Plan:
    """Where the form's values say to host."""
    address = values.get("address") or hosting.LOCALHOST
    if address == OTHER:
        address = (values.get("other_address") or "").strip()
    return hosting.Plan(
        address,
        values.get("port") or hosting.DEFAULT_PORT,
        (values.get("ssh_port") or hosting.DEFAULT_SSH_PORT)
        if values.get("ssh")
        else None,
        public_ok=bool(values.get("public_ok")) and _may_be_public(values),
    )


def _may_be_public(values: dict[str, Any]) -> bool:
    """Whether the form asks the storyguide to insist: an address typed in
    (a name is looked up only when hosting starts), or one the internet
    can reach."""
    address = values.get("address") or hosting.LOCALHOST
    return address == OTHER or hosting.is_public(address, resolve=False)


def _problem(values: dict[str, Any]) -> str | None:
    plan = plan_of(values)
    if not plan.address:
        return "Type the address to host on."
    ports = [plan.port] + ([plan.ssh_port] if plan.ssh_port is not None else [])
    if any(not 1 <= port <= 65535 for port in ports):
        return "A port is a number from 1 to 65535."
    if len(set(ports)) < len(ports):
        return "The browser port and the SSH port must differ."
    return None


def _live(values: dict[str, Any]) -> str:
    if _problem(values) is not None:
        return ""
    return reached_at(plan_of(values))


def reached_at(plan: hosting.Plan, *, markup: bool = True) -> str:
    """Where players reach the saga (markup, or plain text)."""

    def bold(words: str) -> str:
        return f"[b]{escape(words)}[/]" if markup else words

    lines = [f"Players open {bold(plan.browser_url())} in their browser"]
    if plan.ssh_port is not None:
        lines.append(f"or run {bold(plan.ssh_command())}")
    found = " ".join(lines) + "."
    if plan.address == hosting.LOCALHOST:
        found += " On localhost only this computer can: choose your network's address."
    return found


def host_form() -> Form:
    """Host for Players: where to listen, then start the host."""
    last = hosting.last_plan()

    def apply(values: dict[str, Any]) -> Command | list[str]:
        plan = plan_of(values)
        problem = hosting.HOST.start(plan)
        if problem is not None:
            return Refuse("Host for Players", escape(problem))
        return notes(
            f"Hosting the app. {reached_at(plan)}",
            "Stop Hosting, in Saga Management, ends it; so does closing the app.",
        )

    return Form(
        "Host for Players",
        lambda: [
            DialogField(
                "_what",
                "Hosting",
                "info",
                "Players open the app in a browser on their own computers and "
                "sign in with the name and passcode you gave them on Saga "
                "Content's Players. Host on your private network's address "
                "(Tailscale or ZeroTier), never one the internet can reach.",
            ),
            DialogField(
                "address",
                "Address",
                "select",
                last.address,
                options=_address_options(last.address),
                hint="This computer's address on the network you share with the "
                "players.",
            ),
            DialogField(
                "other_address",
                "Other address",
                "text",
                "",
                show_if=lambda values: values.get("address") == OTHER,
            ),
            DialogField(
                "public_ok",
                "I know this is reachable from the internet",
                "check",
                False,
                hint="Hosting on such an address is refused unless this is "
                "ticked: anyone on the internet could open the app and try "
                "passcodes, and nothing is encrypted.",
                show_if=_may_be_public,
            ),
            DialogField(
                "port",
                "Browser port",
                "int",
                last.port,
                required=True,
                hint=f"{hosting.DEFAULT_PORT} unless another program has it.",
            ),
            DialogField(
                "ssh",
                "Also over SSH",
                "check",
                last.ssh_port is not None,
                hint="For players who would rather use a terminal.",
            ),
            DialogField(
                "ssh_port",
                "SSH port",
                "int",
                last.ssh_port or hosting.DEFAULT_SSH_PORT,
                required=True,
                show_if=lambda values: bool(values.get("ssh")),
            ),
        ],
        apply,
        validate=_problem,
        live=_live,
        save_label="Host",
    )


def hosting_note() -> str:
    """What Saga Management says beside Stop Hosting (plain text): where
    it is hosted."""
    plan = hosting.HOST.plan
    if isinstance(plan, RemotePlan):
        return (
            f"Hosted now for Remote seats, through your tunnel at {plan.public_url}. "
            "Stopping ends every player's connection."
        )
    if not isinstance(plan, hosting.Plan):
        return "End the host, and every player's copy of the app with it."
    return f"Hosted now. {reached_at(plan, markup=False)} Stopping ends every player's copy."


def stop_hosting() -> Command:
    """Stop Hosting, after asking: players lose what they haven't saved."""
    if not hosting.HOST.running:
        return Refuse("Stop Hosting", "The saga isn't hosted.")

    def apply() -> list[str]:
        hosting.HOST.stop()
        return notes("Stopped hosting. The players' copies of the app have closed.")

    return Confirm(
        "Stop hosting? Every player's copy of the app closes at once; what "
        "they have saved is kept.",
        apply,
        yes_label="Stop Hosting",
        title="Stop Hosting",
    )
