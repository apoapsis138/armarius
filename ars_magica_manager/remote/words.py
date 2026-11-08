"""Short fingerprints a person can read aloud: a few common words.

Two uses, with different strength:

* The host's key fingerprint is six words (66 bits). The Storyguide reads
  them out on the group's voice call and the player's app shows the same
  six, so an Invite altered in chat is noticed. Six words cannot be matched
  by an attacker generating keys until one fits.
* A device's fingerprint is three words (33 bits). The Storyguide compares
  it on a screen with a named player, once, so an attacker has no way to
  try many.

The words are the 2,048 of BIP-39's English list (assets/words), eleven
bits each. Both ends derive the words from the same hash, so nothing is
stored.
"""

from __future__ import annotations

import hashlib
from functools import cache
from pathlib import Path

from .identity import normalise_pin

WORDS_FILE = Path(__file__).resolve().parent.parent / "assets" / "words" / "english.txt"
BITS_PER_WORD = 11
HOST_WORDS = 6
DEVICE_WORDS = 3
_LIST_SIZE = 2**BITS_PER_WORD
_DIGEST_BITS = 256


@cache
def wordlist() -> tuple[str, ...]:
    words = tuple(WORDS_FILE.read_text(encoding="utf-8").split())
    if len(words) != _LIST_SIZE or len(set(words)) != _LIST_SIZE:
        raise ValueError("The word list is not the 2,048 distinct words expected.")
    return words


def words_from_digest(digest_hex: str, count: int) -> tuple[str, ...]:
    """The first `count` words of a 256-bit hash given as 64 hex digits."""
    if not 1 <= count <= _DIGEST_BITS // BITS_PER_WORD:
        raise ValueError("Too many words asked for.")
    number = int(digest_hex, 16) >> (_DIGEST_BITS - count * BITS_PER_WORD)
    words = wordlist()
    return tuple(
        words[(number >> (BITS_PER_WORD * (count - 1 - i))) & (_LIST_SIZE - 1)]
        for i in range(count)
    )


def host_words(pin: str) -> tuple[str, ...]:
    """The host's six words, from its pin (any form a player may paste)."""
    return words_from_digest(normalise_pin(pin), HOST_WORDS)


def device_words(secret: str) -> tuple[str, ...]:
    """A device's three words, from the secret its app made for the request."""
    digest = hashlib.sha256(
        b"armarius device fingerprint\0" + secret.encode()
    ).hexdigest()
    return words_from_digest(digest, DEVICE_WORDS)


def two_lines(words: tuple[str, ...]) -> str:
    """Words laid out for reading aloud: three to a line."""
    return "\n".join(" ".join(words[i : i + 3]) for i in range(0, len(words), 3))
