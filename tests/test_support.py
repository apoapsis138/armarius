"""The shared test helpers that lean on Textual internals fail clearly."""

from types import SimpleNamespace

import pytest
from support import screen_lines


def test_screen_lines_says_what_to_update_if_textual_moves_the_api():
    app = SimpleNamespace(screen=SimpleNamespace())  # no _compositor
    with pytest.raises(AssertionError, match="update support.screen_lines"):
        screen_lines(app)
