"""Remote seats: how a player's desktop reaches a hosted saga over the internet.

The host listens on this computer only (`host.py`); the storyguide's own
HTTPS tunnel carries players to it. Inside the tunnel's connection runs a
second, private TLS session pinned to the host's key (`secure.py`), so the
tunnel provider carries traffic it cannot read or change. The host answers
only the message types in its registry (`protocol.py`), within the limits
in `limits.py`. The host's key is made and kept by `identity.py`.

The player's side of the same conversation is `client.py`.

Nothing here draws a screen: the core never imports a UI library.
"""
