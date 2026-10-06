from ars_magica_manager import paths


def main() -> None:
    # The data folder is settled before the app (and so storage and
    # settings, which read it on import) is loaded: if it can't be used,
    # another is, and the app says why.
    problem = paths.settle_data_dir()
    from ars_magica_manager.app import ArsMagicaManagerApp

    app = ArsMagicaManagerApp()
    # Saves made by older versions move from the repo's data/ folder to the
    # user's data folder, once.
    notes = [problem] if problem else paths.move_legacy_data()
    app.startup_notes = tuple(notes)
    app.run()


if __name__ == "__main__":
    main()
