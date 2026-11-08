"""The passcode proof: showing the passcode is known without sending it.

The host sends the salt it stores for the player and a fresh nonce. The
player's app derives the scrypt digest of the passcode under that salt and
answers HMAC(digest, nonce + pin), where the pin is the host key the app has
verified. The passcode never crosses the channel, the answer is good for
that nonce only, and an answer made for one host key is worthless at another.

Accepted limits (see the threat model): the stored digest is password-
equivalent for anyone who holds the host's saga file, and a fake host can
guess a weak passcode offline from one challenge, which is why a Remote
seat needs a long one.
"""

from __future__ import annotations

import hashlib
import hmac

NONCE_BYTES = 32


def make_proof(digest: bytes, nonce: bytes, pin: str) -> str:
    """The answer to a challenge, as hex."""
    return hmac.new(digest, nonce + pin.encode(), hashlib.sha256).hexdigest()


def proof_is_good(proof: str, digest: bytes, nonce: bytes, pin: str) -> bool:
    return hmac.compare_digest(proof, make_proof(digest, nonce, pin))
