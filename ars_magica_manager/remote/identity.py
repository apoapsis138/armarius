"""The host's identity: a private key kept in the operating system's keychain.

A Player's Invite carries the *pin*, the SHA-256 of the host's public key.
Only the private key is stored; the certificate the secure channel needs is
rebuilt from it on every start, so there is nothing else to keep safe and
a certificate that has aged out costs nothing (the pin is on the key).

The key lives only in the keychain, never in the synced data folder. With
no keychain there is no identity, and Remote seats are refused.
"""

from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass
from typing import Protocol

import keyring
import keyring.errors
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

KEYCHAIN_SERVICE = "Armarius remote seats"
_CERT_NAME = "armarius-host"
_CERT_YEARS = 10


class NoKeychainError(RuntimeError):
    """This computer has no keychain to keep the host's key in."""


class KeyStore(Protocol):
    """Somewhere to keep one secret string per name (the keychain, or a
    stand-in for tests)."""

    def get(self, name: str) -> str | None: ...

    def set(self, name: str, value: str) -> None: ...

    def delete(self, name: str) -> None: ...


class KeychainStore:
    """The operating system's keychain (Windows Credential Manager, macOS
    Keychain, Secret Service on Linux), through the `keyring` library."""

    def get(self, name: str) -> str | None:
        try:
            return keyring.get_password(KEYCHAIN_SERVICE, name)
        except keyring.errors.NoKeyringError as exc:
            raise NoKeychainError(_NO_KEYCHAIN) from exc

    def set(self, name: str, value: str) -> None:
        try:
            keyring.set_password(KEYCHAIN_SERVICE, name, value)
        except keyring.errors.NoKeyringError as exc:
            raise NoKeychainError(_NO_KEYCHAIN) from exc

    def delete(self, name: str) -> None:
        try:
            keyring.delete_password(KEYCHAIN_SERVICE, name)
        except keyring.errors.PasswordDeleteError:
            pass  # nothing was stored
        except keyring.errors.NoKeyringError as exc:
            raise NoKeychainError(_NO_KEYCHAIN) from exc


_NO_KEYCHAIN = (
    "This computer has no keychain to keep the host's key in, so Remote seats "
    "cannot be offered. Install or unlock one (Credential Manager, Keychain, or "
    "a Secret Service such as GNOME Keyring) and try again."
)


class MemoryStore:
    """A KeyStore that forgets everything when the program ends (tests)."""

    def __init__(self) -> None:
        self._items: dict[str, str] = {}

    def get(self, name: str) -> str | None:
        return self._items.get(name)

    def set(self, name: str, value: str) -> None:
        self._items[name] = value

    def delete(self, name: str) -> None:
        self._items.pop(name, None)


@dataclass(frozen=True)
class HostIdentity:
    """The host's key, its self-signed certificate, and the pin an Invite carries."""

    key: ec.EllipticCurvePrivateKey
    cert_pem: bytes
    pin: str

    def key_pem(self) -> bytes:
        return self.key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )


def public_key_hash(cert_der: bytes) -> str:
    """The pin: SHA-256 of a certificate's public key (not of the certificate)."""
    cert = x509.load_der_x509_certificate(cert_der)
    spki = cert.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return hashlib.sha256(spki).hexdigest()


_PIN_LENGTH = 64  # hex digits of a SHA-256


def normalise_pin(text: str) -> str:
    """A pin as typed or pasted (any case, with spaces or colons between
    digits) in the form `public_key_hash` gives, or ValueError if it cannot
    be a pin. A typo is refused plainly instead of crashing a comparison."""
    pin = "".join(text.split()).replace(":", "").lower()
    if len(pin) != _PIN_LENGTH or any(c not in "0123456789abcdef" for c in pin):
        raise ValueError("That is not a host fingerprint.")
    return pin


def build(key: ec.EllipticCurvePrivateKey) -> HostIdentity:
    """A self-signed certificate for `key`, and the pin of its public key."""
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, _CERT_NAME)])
    now = datetime.datetime.now(datetime.UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=365 * _CERT_YEARS))
        .sign(key, hashes.SHA256())
    )
    der = cert.public_bytes(serialization.Encoding.DER)
    return HostIdentity(
        key=key,
        cert_pem=cert.public_bytes(serialization.Encoding.PEM),
        pin=public_key_hash(der),
    )


def _parse_key(pem: str) -> ec.EllipticCurvePrivateKey:
    try:
        key = serialization.load_pem_private_key(pem.encode(), password=None)
    except ValueError as exc:
        raise ValueError("The host's stored key cannot be read.") from exc
    if not isinstance(key, ec.EllipticCurvePrivateKey):
        raise ValueError("The host's stored key is not the kind this app makes.")
    return key


def _new(store: KeyStore, name: str) -> HostIdentity:
    identity = build(ec.generate_private_key(ec.SECP256R1()))
    store.set(name, identity.key_pem().decode())
    return identity


def load_or_create(store: KeyStore, name: str) -> HostIdentity:
    """The identity kept under `name`, made and stored on first use."""
    pem = store.get(name)
    if pem is None:
        return _new(store, name)
    return build(_parse_key(pem))


def rotate(store: KeyStore, name: str) -> HostIdentity:
    """A new identity in place of the old: every Invite and Device credential
    made against the old pin stops working."""
    store.delete(name)
    return _new(store, name)
