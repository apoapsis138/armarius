"""The Scenes lists' forms, independent of how they are drawn (scenes.py).

The saga's Scenes library: Add, Edit and Delete a Scene. The Scene form
asks for its title; its place (a covenant, a Place or one of its levels,
or a name typed), whose aura and realm fill in when it is chosen and can
be changed; its regulars (the actors usually there); the open story it
plays; a map; what to show from it; and notes, the storyguide's prep
sheet.

A Session's Scenes: Load a Scene (from the library, or a New Scene made
there, which joins the library), Edit a use (who is present this time,
its place in the order, and which planned Session it is in) and Take it
out. What a use's form offers follows its state (scenes.allows): an Ended
use's form changes only its notes.

Pattern: one core Form per record, with each list's verbs one
commands.SectionOps registered in section_verbs (the library for the
saga, a Session's Scenes for the Session)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import scenes
from .. import sessions as ss
from ..commands import (
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Picked,
    Refuse,
    SectionOps,
)
from ..form_spec import DialogField, ListEditor, pairs
from ..markup import escape
from ..models import Saga, Scene, SceneUse, Session

SCENES_HELP = "scenes"

#: The key of a present cast member's tick, before the character's id.
PRESENT = "present_"


def _refs_field(
    saga: Saga,
    key: str,
    label: str,
    chosen: list[str],
    choose: Callable[[Any], Command],
    title: str,
    hint: str,
) -> DialogField:
    """A list of "kind:id" references, each added by choosing it."""

    def name(ref: str) -> str:
        return scenes.name_of(saga, ref)

    return DialogField(
        key,
        label,
        "picker",
        list(chosen),
        display=lambda refs: (
            "; ".join(name(r) for r in dict.fromkeys(refs)) or "(none)"
        ),
        items=ListEditor(name, choose, title),
        hint=hint,
    )


def _choose_actor(saga: Saga, leave_out: set[str]) -> Command:
    """An actor not already listed as the form opened (one added twice
    while it is open is kept once on saving)."""
    return Choose(
        "Choose an Actor",
        lambda: [
            Choice(escape(name), ref)
            for name, ref in scenes.actor_choices(saga)
            if ref not in leave_out
        ],
        Picked,
        empty="Everyone in the saga is listed already.",
    )


def _choose_showable(saga: Saga) -> Command:
    return Choose(
        "Choose What to Show",
        lambda: [
            Choice(escape(name), ref, facets=(("Kind", heading),))
            for heading, name, ref in scenes.showable_choices(saga)
        ],
        Picked,
        empty="The saga has nothing with a page to show yet.",
        filters=("Kind",),
    )


# -- the library: a Scene --


def scene_title(existing: Scene | None) -> str:
    if existing is None:
        return "Add a Scene"
    return f"Edit the Scene: {escape(existing.title or '(untitled)')}"


def _where_fields(saga: Saga, existing: Scene | None) -> list[DialogField]:
    def fills(values: dict[str, Any]) -> dict[str, Any]:
        found = scenes.aura_of(saga, values.get("where"))
        if found is None:
            return {}
        aura, realm = found
        return {"aura": aura, "realm": realm}

    return [
        DialogField(
            "where",
            "Place",
            "select",
            scenes.where_value(existing),
            options=scenes.where_options(saga),
            allow_blank=True,
            placeholder="(somewhere else: type it below)",
            fills=fills,
            hint="A covenant, or a Place or one of its levels: its aura and "
            "realm fill in below, and you can change them.",
        ),
        DialogField(
            "place_name",
            "Place name",
            "text",
            existing.place_name if existing else "",
            show_if=lambda values: not values.get("where"),
            hint="Somewhere that isn't a record of the saga: a passing glade.",
        ),
        DialogField("aura", "Aura", "int", existing.aura if existing else 0),
        DialogField(
            "realm",
            "Realm",
            "select",
            existing.realm if existing else "",
            options=pairs(scenes.REALM_CHOICES),
            allow_blank=True,
            placeholder="(none)",
        ),
    ]


def scene_fields(saga: Saga, existing: Scene | None) -> list[DialogField]:
    stories = scenes.story_options(saga)
    maps = scenes.picture_options(saga)
    regulars = list(existing.regulars) if existing else []
    return [
        DialogField(
            "title",
            "Title",
            "text",
            existing.title if existing else "",
            required=True,
        ),
        *_where_fields(saga, existing),
        _refs_field(
            saga,
            "regulars",
            "Regulars",
            regulars,
            lambda _current: _choose_actor(saga, set(regulars)),
            "Regulars",
            "The actors usually there: characters, Bestiary creatures, lords. "
            "Each time it is loaded into a Session they're present, with "
            "that evening's cast.",
        ),
        DialogField(
            "story",
            "Story",
            "select",
            existing.story_id if existing else None,
            options=stories,
            allow_blank=True,
            placeholder="(none)" if stories else "(no open story)",
            hint="The open story this Scene plays.",
        ),
        DialogField(
            "picture",
            "Picture",
            "select",
            existing.picture if existing else None,
            options=maps,
            allow_blank=True,
            placeholder="(none)" if maps else "(no map with a picture)",
            hint="A map already in the saga's Atlas, shown when the Scene is set.",
        ),
        _refs_field(
            saga,
            "to_show",
            "To show",
            list(existing.to_show) if existing else [],
            lambda _current: _choose_showable(saga),
            "To Show",
            "What you may show the players from here: a map, a person, a "
            "place, any record with a page.",
        ),
        DialogField(
            "notes",
            "Notes",
            "area",
            existing.notes if existing else "",
            hint="Your prep sheet: what's here, what to remember.",
        ),
    ]


def _store_scene(saga: Saga, existing: Scene | None, values: dict[str, Any]) -> Scene:
    scene = existing or Scene(id=scenes.new_scene_id())
    scene.title = (values.get("title") or "").strip()
    scenes.put_where(scene, values.get("where"))
    scene.place_name = (
        "" if values.get("where") else (values.get("place_name") or "").strip()
    )
    scene.aura = values.get("aura") or 0
    scene.realm = values.get("realm") or ""
    scene.regulars = list(dict.fromkeys(values.get("regulars") or []))
    scene.story_id = scenes.story_from(saga, values.get("story"))
    scene.picture = values.get("picture") or ""
    scene.to_show = list(dict.fromkeys(values.get("to_show") or []))
    scene.notes = values.get("notes") or ""
    if existing is None:
        saga.scenes.append(scene)
    return scene


def scene_form(
    saga: Saga,
    existing: Scene | None,
    then: Callable[[Scene], Any] | None = None,
) -> Form:
    """Add (None) or Edit a Scene of the library; `then` follows saving."""

    def apply(values: dict[str, Any]) -> Any:
        scene = _store_scene(saga, existing, values)
        return then(scene) if then is not None else None

    return Form(
        scene_title(existing),
        lambda: scene_fields(saga, existing),
        apply,
        help_id=SCENES_HELP,
    )


def delete_scene(saga: Saga, scene: Scene) -> Confirm | Refuse:
    """Delete a Scene, asking first; one a Session played stays."""
    why = scenes.why_not_delete(saga, scene)
    if why is not None:
        return Refuse("Delete the Scene", escape(why))
    used = {s.id for s, _u in scenes.uses_of(saga, scene)}
    also = (
        f" It is loaded into {len(used)} Session{'' if len(used) == 1 else 's'}, "
        "and goes from them too."
        if used
        else ""
    )
    return Confirm(
        f"Delete the Scene {escape(scene.title or '(untitled)')}?{also}",
        lambda: scenes.delete(saga, scene),
    )


def library_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the saga's Scenes library."""
    return SectionOps(
        add=lambda: scene_form(saga, None),
        edit=lambda index: scene_form(saga, saga.scenes[index]),
        remove=lambda index: delete_scene(saga, saga.scenes[index]),
        rows=lambda: [s.title or "(untitled)" for s in saga.scenes],
    )


# -- a Session's Scenes: uses --


def load_scene(saga: Saga, session: Session) -> Choose:
    """Load a Scene into `session`: one from the library, or a new one."""

    def apply(choice: str) -> Any:
        if choice == scenes.NEW_SCENE:
            return scene_form(
                saga, None, then=lambda scene: _loaded(saga, session, scene)
            )
        scene = scenes.find(saga, choice)
        return _loaded(saga, session, scene) if scene is not None else None

    return Choose(
        "Load a Scene",
        lambda: [
            Choice(
                "[b]New Scene…[/]", scenes.NEW_SCENE, "Make a Scene for the library."
            ),
            *(
                Choice(
                    escape(s.title or "(untitled)"),
                    s.id,
                    scenes.scene_detail(saga, s),
                )
                for s in saga.scenes
            ),
        ],
        apply,
        help_id=SCENES_HELP,
    )


def _loaded(saga: Saga, session: Session, scene: Scene) -> None:
    scenes.load(saga, session, scene)


def _present_fields(saga: Saga, session: Session, use: SceneUse) -> list[DialogField]:
    """A tick for each of tonight's cast, then anyone else present, added
    by name."""
    cast = scenes.cast_refs(session)
    ticks = [
        DialogField(
            f"{PRESENT}{ref.partition(':')[2]}",
            f"Present: {escape(scenes.name_of(saga, ref))}",
            "check",
            ref in use.present,
        )
        for ref in cast
        if scenes.record_of(saga, ref) is not None
    ]
    others = [r for r in use.present if r not in cast]
    return [
        *ticks,
        _refs_field(
            saga,
            "also_present",
            "Also present",
            others,
            lambda _current: _choose_actor(saga, {*cast, *others}),
            "Also Present",
            "Anyone else here this time: grogs, creatures, your own characters.",
        ),
    ]


def _order_fields(saga: Saga, session: Session, use: SceneUse) -> list[DialogField]:
    """Which use it comes after, and which planned Session it is in."""
    at = session.scenes.index(use)
    others = [u for u in session.scenes if u is not use]
    return [
        DialogField(
            "after",
            "Comes after",
            "select",
            session.scenes[at - 1].id if at else "",
            options=[("(first)", "")]
            + [(escape(scenes.title(saga, u)), u.id) for u in others],
            hint="Its place in this Session's order.",
        ),
        DialogField(
            "session",
            "Session",
            "select",
            session.id,
            options=[
                (escape(ss.when(s)), s.id)
                for s in scenes.sessions_to_move_to(saga, session)
            ],
            hint="Choose another planned Session to move it there: it goes "
            "last in that Session's order.",
        ),
    ]


def use_fields(saga: Saga, session: Session, use: SceneUse) -> list[DialogField]:
    """A use's form, as its state allows."""
    allows = scenes.allows(session, use)
    fields: list[DialogField] = []
    if allows.present:
        fields += _present_fields(saga, session, use)
    else:
        fields.append(
            DialogField(
                "_ended",
                "",
                "info",
                escape(
                    f"{scenes.title(saga, use)} has ended this evening: who was "
                    "there stays as it was. Its notes can still change."
                ),
            )
        )
    if allows.move:
        fields += _order_fields(saga, session, use)
    fields.append(
        DialogField(
            "notes",
            "Notes",
            "area",
            use.notes,
            hint="This evening's notes on the Scene.",
        )
    )
    return fields


def _store_use(
    saga: Saga, session: Session, use: SceneUse, values: dict[str, Any]
) -> None:
    allows = scenes.allows(session, use)
    if allows.present:
        ticked = [
            ref
            for ref in scenes.cast_refs(session)
            if values.get(f"{PRESENT}{ref.partition(':')[2]}", False)
        ]
        also = [r for r in values.get("also_present") or [] if r not in ticked]
        use.present = list(dict.fromkeys([*ticked, *also]))
        scenes.keep_names(saga, use)
    use.notes = values.get("notes") or ""
    if allows.move:
        target = ss.find(saga, values.get("session")) or session
        if target is session:
            scenes.put_after(session, use, values.get("after"))
        else:
            scenes.move_to(use, session, target)


def use_form(saga: Saga, session: Session, use: SceneUse) -> Form:
    """Edit a use of a Scene in `session`."""
    return Form(
        f"{escape(scenes.title(saga, use))}: {escape(ss.when(session))}",
        lambda: use_fields(saga, session, use),
        lambda values: _store_use(saga, session, use, values),
        help_id=SCENES_HELP,
    )


def take_out(saga: Saga, session: Session, use: SceneUse) -> Confirm | Refuse:
    """Take a Prepared use out of `session`, asking first; the Scene stays
    in the library. A Playing or Ended one stays."""
    name = escape(scenes.title(saga, use))
    if not scenes.allows(session, use).take_out:
        return Refuse(
            "Take the Scene out",
            f"{name} is {scenes.state_label(session, use)}: only a Prepared "
            "Scene can be taken out.",
        )

    def apply() -> None:
        session.scenes[:] = [u for u in session.scenes if u is not use]

    return Confirm(
        f"Take {name} out of this Session? It stays in the Scenes library.",
        apply,
        yes_label="Take Out",
    )


def use_ops(saga: Saga, session: Session) -> SectionOps:
    """Load, Edit and Take out for `session`'s Scenes, in the evening's
    order."""
    return SectionOps(
        add=lambda: load_scene(saga, session),
        edit=lambda index: use_form(saga, session, session.scenes[index]),
        remove=lambda index: take_out(saga, session, session.scenes[index]),
        rows=lambda: [scenes.title(saga, u) for u in session.scenes],
    )
