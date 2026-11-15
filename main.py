"""Start the terminal version, or, given one of launch's words first, the
copy of the app that word names: `host` (the host for players), `seats`
(the listener for Remote seats) or `play` (a player's copy, the same as no
word). A Build's terminal program is this script, and hosting runs it
with a word in place of `python -m` (see launch.py)."""

import sys
from collections.abc import Callable

from ars_magica_manager import launch, paths


def main() -> None:
    # The data folder is settled first: the default folder takes the app's
    # new name, and if the folder can't be used, another is, and the app
    # says why. The app then keeps to that folder until another is chosen.
    renamed = paths.move_old_default_folder()
    problem = paths.settle_data_dir()
    paths.use_data_dir(paths.data_dir())
    from ars_magica_manager import hosting
    from ars_magica_manager.tui.app import ArsMagicaManagerApp

    app = ArsMagicaManagerApp()
    # The storyguide's own window opens on the title page; a player's copy
    # of a hosted saga goes straight to the sagas, to sign in.
    app.show_title = not hosting.transport()
    # Saves made by older versions move from the repo's data/ folder to the
    # user's data folder, once.
    notes = [problem] if problem else paths.move_legacy_data()
    app.startup_notes = tuple(([renamed] if renamed else []) + notes)
    app.run()


def _host(argv: list[str]) -> None:
    # Imported here, not at the top, to keep start-up quick: a player's copy
    # never loads the servers.
    from ars_magica_manager.tui import serve

    serve.main(argv)


def _seats(argv: list[str]) -> None:
    # Imported here to keep start-up quick, as in _host.
    from ars_magica_manager.remote import serve

    serve.main(argv)


def _play(argv: list[str]) -> None:
    main()


#: What each word runs, given the arguments after it (Command: one
#: function per word, looked up by name).
WORDS: dict[str, Callable[[list[str]], None]] = {
    launch.HOST: _host,
    launch.SEATS: _seats,
    launch.PLAY: _play,
}


def run(argv: list[str]) -> None:
    """Run the word `argv` starts with, or the terminal version if it
    starts with none."""
    if argv and argv[0] in WORDS:
        WORDS[argv[0]](argv[1:])
    else:
        main()


if __name__ == "__main__":
    run(sys.argv[1:])
