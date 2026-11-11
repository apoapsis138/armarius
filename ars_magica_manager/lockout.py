"""How long wrong passcodes make someone wait: one rule for every sign-in.

A Remote seat (remote/devices.py) and a hosted copy's sign-in dialog
(hosted_signin.py) both count wrong passcodes and ask this module how long
the next try must wait. Three are free; then the waits grow, the last
repeating, and a right passcode clears the count.

Pattern: the one policy both sign-ins call (a Strategy with a single
implementation, which in Python is a pair of plain functions), so the two
roads in can't drift apart.
"""

from __future__ import annotations

#: Wrong passcodes allowed before the first wait.
FREE_FAILURES = 3
#: Seconds to wait after the third wrong passcode, then each further one
#: (the last repeats).
LOCK_STEPS = (30.0, 120.0, 600.0, 3600.0)


def locked_until(failures: int, now: float) -> float:
    """When someone with `failures` wrong passcodes in a row may try again
    (clock time), or 0.0 if they may now."""
    if failures < FREE_FAILURES:
        return 0.0
    step = min(failures - FREE_FAILURES, len(LOCK_STEPS) - 1)
    return now + LOCK_STEPS[step]


def wait_text(seconds: int) -> str:
    """What someone locked out is told."""
    return f"Too many wrong passcodes: try again in {seconds} seconds."
