from ars_magica_manager import paths
from ars_magica_manager.app import ArsMagicaManagerApp


def main() -> None:
    app = ArsMagicaManagerApp()
    # Saves made before STORY-1127 move from the repo's data/ folder to the
    # user's data folder, once.
    app.startup_notes = tuple(paths.move_legacy_data())
    app.run()


if __name__ == "__main__":
    main()
