"""Start the desktop (Qt) version. Needs the gui dependency group:
`uv sync --group gui`."""

from ars_magica_manager.gui.app import main

if __name__ == "__main__":
    raise SystemExit(main())
