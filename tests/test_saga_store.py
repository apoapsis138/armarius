"""The saga store (saga_store.py, ADR 0011) both front-ends save through and
read pictures from: a refused save is a result, what picking up another
copy's save means is worded once, and a Joined game's pictures come from
its host."""

from support import everything_saga

from ars_magica_manager import picture_files, storage
from ars_magica_manager.saga_store import (
    LocalStore,
    PickedUp,
    Refreshed,
    RemoteStore,
    picked_up,
)


def test_a_save_the_shape_check_refuses_is_a_result_and_writes_nothing():
    saga = everything_saga()
    storage.save_saga(saga)
    before = storage.saga_path(saga.id).read_bytes()
    saga.characters[0].covenant_id = "../x"
    saved = LocalStore().save(saga)
    assert saved.not_saved == (
        f"Not saved: characters[{saga.characters[0].id}].covenant_id: not a plain id. "
        "The file is unchanged."
    )
    assert storage.saga_path(saga.id).read_bytes() == before


def test_a_save_that_is_written_says_nothing_is_wrong():
    saga = everything_saga()
    assert LocalStore().save(saga).not_saved == ""


def _found(saved_by: str = "Ana", changed=(("characters", "mag1"),)) -> Refreshed:
    saga = everything_saga()
    saga.saved_by = saved_by
    return Refreshed(saga, list(changed))


def test_another_save_elsewhere_is_an_update():
    told = picked_up(_found(), open_id="comp1", open_name="Alys")
    assert told == PickedUp("Ana")
    assert told.lines == ["Updated by Ana."]


def test_the_record_on_show_changed_is_reloaded():
    told = picked_up(_found(), open_id="mag1", open_name="Leandro")
    assert told.lines == ["Ana changed Leandro; reloaded."]


def test_the_record_on_show_deleted_is_gone():
    told = picked_up(_found(), open_id="mag1", open_name="Leandro", open_gone=True)
    assert told.gone
    assert told.lines == ["Ana deleted what you had open."]


def test_no_name_saved_is_the_storyguide():
    assert picked_up(_found(saved_by=""), open_id=None).lines == [
        "Updated by The storyguide."
    ]


def test_the_season_moving_on_or_back_is_said():
    found = _found()
    saga = found.saga
    now = (saga.current_year, saga.current_season)
    on = picked_up(found, open_id=None, season_was=(now[0] - 1, now[1]))
    assert on.lines[-1] == f"Ana advanced the season to {now[1]} {now[0]}."
    back = picked_up(found, open_id=None, season_was=(now[0] + 1, now[1]))
    assert back.season_back
    assert back.lines[-1] == (
        f"Ana undid {now[1]} {now[0] + 1}: the saga is back to {now[1]} {now[0]}."
    )
    assert picked_up(found, open_id=None, season_was=now).season is None


# -- pictures, read through the store --


def test_this_computers_store_reads_its_own_pictures():
    folder = picture_files.kind(picture_files.PORTRAITS)
    assert folder is not None
    folder.directory().mkdir(parents=True, exist_ok=True)
    (folder.directory() / "alys.png").write_bytes(b"png")
    store = LocalStore()
    assert store.picture(picture_files.PORTRAITS, "alys.png") == b"png"
    assert store.picture(picture_files.PORTRAITS, "nobody.png") is None
    assert store.picture(picture_files.PORTRAITS, "../alys.png") is None


class _Seat:
    """A Remote seat whose host has one portrait, and can drop out."""

    def __init__(self) -> None:
        self.asked: list[tuple[str, str]] = []
        self.down = False

    def picture(self, folder: str, name: str) -> bytes | None:
        self.asked.append((folder, name))
        if self.down:
            raise ConnectionError
        return b"host" if name == "alys.png" else None


def test_a_joined_games_pictures_come_from_the_host_once_each():
    seat = _Seat()
    store = RemoteStore(seat)  # type: ignore[arg-type]
    assert store.picture(picture_files.PORTRAITS, "alys.png") == b"host"
    assert store.picture(picture_files.PORTRAITS, "alys.png") == b"host"
    assert store.picture(picture_files.PORTRAITS, "nobody.png") is None
    assert store.picture(picture_files.PORTRAITS, "nobody.png") is None
    assert seat.asked == [
        (picture_files.PORTRAITS, "alys.png"),
        (picture_files.PORTRAITS, "nobody.png"),
    ]
    # Never a name that isn't a picture's, nor a folder that isn't a kind.
    assert store.picture(picture_files.PORTRAITS, "../saga.json") is None
    assert store.picture("sagas", "alys.png") is None
    assert len(seat.asked) == 2


def test_a_picture_the_host_cant_be_reached_for_is_asked_again():
    seat = _Seat()
    store = RemoteStore(seat)  # type: ignore[arg-type]
    seat.down = True
    assert store.picture(picture_files.MAPS, "alys.png") is None
    seat.down = False
    assert store.picture(picture_files.MAPS, "alys.png") == b"host"
