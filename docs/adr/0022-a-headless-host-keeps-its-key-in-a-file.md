---
status: proposed
---

# A headless host keeps its key in a file on its own volume

This amends the keychain-only rule of `remote/identity.py` (and ADR 0009) for a host with no keychain, such as a container on a NAS or a small server. With `ARMARIUS_KEYSTORE=file`, and only then, the host's private key is kept in a file through the existing `KeyStore` protocol: mode 0600, owned by the app's non-root user, on a `/keys` volume apart from the saga's data, meant to sit in an encrypted shared folder on the NAS. Without that setting the keychain-only rule stands unchanged, and a desktop never uses a file.

The Cloudflare tunnel token is as sensitive as the key: whoever holds it can stand in for the host's address. Both are kept and backed up the same way, apart from the saga's backups.

## Considered options

- **Docker secrets:** mounted read-only, so rotating the key would need a write the container cannot make.
- **A passphrase-wrapped key opened with `admin unlock`:** stronger at rest, but the host could not restart on its own after a power cut. Deferred.

## Consequences

- Rotation runbook: `admin rotate-key`, issue a new tunnel token, and re-invite every seat, since their pins name the old key.
- The Remote seats threat model gains a self-hosted section: the NAS's admins and root, a compromised listener, theft of the disk, and backups kept separate and encrypted.
