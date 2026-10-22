from ars_magica_manager import paths


def main() -> None:
    # The data folder is settled before the app (and so storage and
    # settings, which read it on import) is loaded: the default folder
    # takes the app's new name, and if the folder can't be used, another
    # is, and the app says why.
    renamed = paths.move_old_default_folder()
    problem = paths.settle_data_dir()
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


if __name__ == "__main__":
    main()
