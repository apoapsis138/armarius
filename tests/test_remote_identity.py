"""The host's identity: made once, kept in the keychain, the pin stable."""

from __future__ import annotations

import keyring
import keyring.errors
import pytest

from ars_magica_manager.remote import identity as ident


def test_identity_is_made_once_and_the_pin_is_stable() -> None:
    store = ident.MemoryStore()
    first = ident.load_or_create(store, "saga-1")
    again = ident.load_or_create(store, "saga-1")
    assert first.pin == again.pin
    assert len(first.pin) == 64


def test_pin_follows_the_key_not_the_certificate() -> None:
    store = ident.MemoryStore()
    first = ident.load_or_create(store, "saga-1")
    rebuilt = ident.build(first.key)
    assert rebuilt.cert_pem != first.cert_pem  # a new certificate...
    assert rebuilt.pin == first.pin  # ...for the same key


def test_a_pasted_pin_is_put_in_the_stored_form() -> None:
    pin = "ab" * 32
    assert ident.normalise_pin(pin) == pin
    assert ident.normalise_pin(" AB:" * 31 + " AB ") == pin
    for bad in ("", "xyz", "é" * 64, "ab" * 31, "ab" * 33):
        with pytest.raises(ValueError, match="not a host fingerprint"):
            ident.normalise_pin(bad)


def test_each_saga_has_its_own_key() -> None:
    store = ident.MemoryStore()
    assert ident.load_or_create(store, "a").pin != ident.load_or_create(store, "b").pin


def test_rotating_changes_the_pin_and_keeps_the_new_one() -> None:
    store = ident.MemoryStore()
    old = ident.load_or_create(store, "saga-1")
    new = ident.rotate(store, "saga-1")
    assert new.pin != old.pin
    assert ident.load_or_create(store, "saga-1").pin == new.pin


def test_a_damaged_stored_key_is_reported_not_replaced() -> None:
    store = ident.MemoryStore()
    store.set("saga-1", "not a key")
    with pytest.raises(ValueError, match="cannot be read"):
        ident.load_or_create(store, "saga-1")


def test_no_keychain_is_a_plain_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object) -> None:
        raise keyring.errors.NoKeyringError

    monkeypatch.setattr(keyring, "get_password", fail)
    monkeypatch.setattr(keyring, "set_password", fail)
    monkeypatch.setattr(keyring, "delete_password", fail)
    store = ident.KeychainStore()
    for call in (
        lambda: store.get("x"),
        lambda: store.set("x", "y"),
        lambda: store.delete("x"),
    ):
        with pytest.raises(ident.NoKeychainError, match="no keychain"):
            call()


def test_deleting_what_is_not_there_is_fine(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(*args: object) -> None:
        raise keyring.errors.PasswordDeleteError

    monkeypatch.setattr(keyring, "delete_password", missing)
    ident.KeychainStore().delete("x")
