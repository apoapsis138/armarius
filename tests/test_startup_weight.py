"""Opening either front-end loads none of the heavy libraries only some of
its screens need (the network, keychain and crypto ones Remote seats and
hosting use): those screens import them when first opened, with a
'# start-up:' comment (test_function_imports.py)."""

from __future__ import annotations

import os
import subprocess
import sys

#: Loaded only by the screens that need them.
HEAVY = ("aiohttp", "keyring", "cryptography", "asyncssh")

#: Each front-end's first module, as the app opens it.
FRONT_ENDS = ("ars_magica_manager.gui.window", "ars_magica_manager.tui.app")


def test_opening_a_front_end_leaves_the_heavy_libraries_unloaded():
    script = (
        "import importlib, sys\n"
        f"for name in {FRONT_ENDS!r}:\n"
        "    importlib.import_module(name)\n"
        f"print(','.join(m for m in {HEAVY!r} if m in sys.modules))\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    loaded = done.stdout.strip()
    assert not loaded, (
        f"opening the app loads {loaded}: import it inside the function that "
        "needs it, with a '# start-up:' comment"
    )
