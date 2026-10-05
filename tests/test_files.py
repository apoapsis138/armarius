import os

import pytest

from ars_magica_manager import files


def test_write_atomic_replaces_the_file_and_leaves_no_temp_file(tmp_path):
    path = tmp_path / "sub" / "saga.json"
    files.write_atomic(path, "old")
    files.write_atomic(path, "new")
    assert path.read_text(encoding="utf-8") == "new"
    assert [p.name for p in path.parent.iterdir()] == ["saga.json"]


def test_a_failed_write_keeps_the_old_file(tmp_path, monkeypatch):
    """A crash before the rename (here, the rename itself failing) leaves the
    previous file whole and cleans up the temp file (STORY-1125)."""
    path = tmp_path / "saga.json"
    files.write_atomic(path, "old")

    def refuse(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", refuse)
    with pytest.raises(OSError, match="disk full"):
        files.write_atomic(path, "new")

    assert path.read_text(encoding="utf-8") == "old"
    assert [p.name for p in tmp_path.iterdir()] == ["saga.json"]


def test_a_briefly_locked_file_is_retried(tmp_path, monkeypatch):
    """Windows refuses the rename while another program (a sync client) has
    the file open; the write tries again rather than failing."""
    path = tmp_path / "saga.json"
    real_replace = os.replace
    refusals = iter([True, True])

    def locked_twice(src, dst):
        if next(refusals, False):
            raise PermissionError("in use")
        real_replace(src, dst)

    monkeypatch.setattr(files, "_REPLACE_WAIT", 0)
    monkeypatch.setattr(os, "replace", locked_twice)
    files.write_atomic(path, "new")
    assert path.read_text(encoding="utf-8") == "new"
