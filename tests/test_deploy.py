"""The headless host's container (deploy/): the hardening the threat model
counts on stays in the files, and the listener takes its saga from the
container's setting."""

from __future__ import annotations

from pathlib import Path

import pytest

from ars_magica_manager import ROOT
from ars_magica_manager.remote import serve
from ars_magica_manager.remote.plan import SAGA_VARIABLE

DEPLOY = ROOT / "deploy"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_the_image_runs_as_its_own_user_with_the_file_key_store() -> None:
    dockerfile = _text(DEPLOY / "Dockerfile")
    for line in (
        "USER 10001:10001",
        "ARMARIUS_KEYSTORE=file",
        "ARMARIUS_KEYS=/keys",
        "ARMARIUS_DATA=/data",
        "uv sync --frozen --no-dev",
        'ENTRYPOINT ["python", "main.py"]',
        'CMD ["seats"]',
    ):
        assert line in dockerfile, line
    assert ":latest" not in dockerfile


def test_only_the_app_reaches_the_image() -> None:
    """An allow-list: nothing but the app's own files is sent to the builder,
    so no virtual environment, notes, key or saga can slip in."""
    lines = [
        line
        for line in _text(DEPLOY / "Dockerfile.dockerignore").splitlines()
        if line and not line.startswith("#")
    ]
    assert lines[0] == "*"
    allowed = {
        line.removeprefix("!").rstrip("/") for line in lines if line.startswith("!")
    }
    assert allowed == {
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "LICENSE",
        "NOTICE.md",
        "CHANGELOG.md",
        "main.py",
        "ars_magica_manager",
        "data",
    }


def test_compose_keeps_the_listener_locked_down_and_unpublished() -> None:
    compose = _text(DEPLOY / "compose.yaml")
    for line in (
        "read_only: true",
        "cap_drop: [ALL]",
        'security_opt: ["no-new-privileges:true"]',
        "mem_limit: 512m",
        'network_mode: "service:armarius"',
        "env_file: [tunnel.env]",
        "${KEYS_DIR:-./keys}:/keys",
    ):
        assert line in compose, line
    assert "ports:" not in compose
    assert ":latest" not in compose
    assert "TUNNEL_TOKEN=" not in compose


def test_the_backup_service_never_sees_the_keys_or_the_network() -> None:
    compose = _text(DEPLOY / "compose.yaml")
    backup = compose.split("\n  backup:\n", 1)[1]
    assert "admin backup" in backup
    assert "network_mode: none" in backup
    assert "disable: true" in backup  # the listener's health check isn't its own
    assert "read_only: true" in backup and "cap_drop: [ALL]" in backup
    assert "/keys" not in backup
    assert "${BACKUPS_DIR:-./backups}:/backups" in backup


def test_the_tunnel_token_and_settings_are_never_committed() -> None:
    ignored = _text(ROOT / ".gitignore").splitlines()
    for path in ("deploy/.env", "deploy/tunnel.env", "deploy/keys/", "deploy/data/"):
        assert path in ignored, path
    assert _text(DEPLOY / "tunnel.env.example").strip().endswith("TUNNEL_TOKEN=")


def test_the_image_is_published_by_version_only() -> None:
    workflow = _text(ROOT / ".github" / "workflows" / "image.yml")
    assert "linux/amd64,linux/arm64" in workflow
    assert "ghcr.io/apoapsis138/armarius:${{ env.VERSION }}" in workflow
    assert ":latest" not in workflow
    tags = [line for line in workflow.splitlines() if line.strip().startswith("tags:")]
    assert len(tags) == 2  # the trigger's, and the one image tag pushed


def test_the_listener_takes_its_saga_from_the_container(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[str] = []

    def build(saga_id: str, tunnel: str) -> tuple[object, object]:
        seen.append(saga_id)
        raise SystemExit(0)

    monkeypatch.setattr(serve, "build", build)
    monkeypatch.setenv(SAGA_VARIABLE, "dammerstein")
    with pytest.raises(SystemExit):
        serve.main([])
    assert seen == ["dammerstein"]
    monkeypatch.delenv(SAGA_VARIABLE)
    with pytest.raises(SystemExit) as refused:
        serve.main([])  # no saga named anywhere: argparse refuses
    assert refused.value.code == 2
