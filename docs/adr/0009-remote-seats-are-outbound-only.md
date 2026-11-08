---
status: proposed
---

# Remote seats are outbound-only, invited and approved

A player's desktop app reaches a hosted saga by connecting out to the host over a WebSocket on HTTPS, so no player machine ever accepts a connection and players never see one another. The storyguide issues each player a single-use, short-lived Invite carrying the host's address and the hash of its self-signed certificate's public key; a second TLS session runs inside the WebSocket and is pinned to that hash, on top of the tunnel's own TLS, so the tunnel provider cannot read or alter the traffic. Nested TLS was chosen over a Noise handshake (the usual Python package, `noiseprotocol`, last released 0.3.1 around 2019 to 2020, supports only older spec revisions and officially only Linux) and over libsodium primitives (we would compose the handshake ourselves). Redeeming it asks for a Remote seat, the storyguide approves it, and the Invite becomes a revocable Device credential. The player still signs in with their passcode, and the host answers only a fixed set of core-validated messages: per-record changes checked by `players.guard_changes` and merged as in ADR 0005, never a terminal, a shell or a whole-saga upload.

## Considered options

- Keep the VPN plus browser terminal: needs extra software on every player's machine.
- Peer-to-peer (WebRTC): exposes players' addresses to one another.
- A relay run by the app's author: makes the author answerable for every table's traffic. Each storyguide brings their own tunnel (Cloudflare Tunnel first); the invite carries any HTTPS address.
- Login at the edge (Cloudflare Access): a desktop client has no browser to complete it, so the app authenticates for itself.

## Consequences

A Device credential lives only in the operating system's keychain (never in the synced data folder). With no keychain the app refuses to keep one, says why, and the player redeems a fresh Invite each time. A credential expires after a storyguide-set idle period per saga (default 90 days), and the storyguide can list and revoke Remote seats at once. The host takes only messages in a registry of allowed types; any other is refused.

The terminal and VPN path stays for those who use it. The public endpoint answers only the handshake and invite redemption, and rate-limits and locks out bad attempts.
