"""Host the app for players, from a terminal.

    uv run python tools/serve.py [--host ADDRESS] [--port N] [--ssh-port N]

The same host the app's Host for Players starts (ars_magica_manager/
tui/serve.py has the details), run here in the foreground until Ctrl+C.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # run as a script: the package is beside tools/
from ars_magica_manager.tui.serve import main

if __name__ == "__main__":
    main()
