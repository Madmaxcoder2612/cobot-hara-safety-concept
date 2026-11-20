"""Achieved Performance Level of a safety function from subsystem PFHd values.

A safety function is a chain of subsystems in series (input, logic, output).
For a series chain the average probabilities of dangerous failure per hour
add up:

    PFHd_total = PFHd_input + PFHd_logic + PFHd_output

The Performance Level that PFHd_total corresponds to is read from the bands
of ISO 13849-1 (table of PL against PFHd):

    PL a   1e-5  <= PFHd < 1e-4
    PL b   3e-6  <= PFHd < 1e-5
    PL c   1e-6  <= PFHd < 3e-6
    PL d   1e-7  <= PFHd < 1e-6
    PL e   1e-8  <= PFHd < 1e-7

A PFHd below 1e-8 is still PL e, the highest level. A PFHd of 1e-4 or more
reaches no PL.

IMPORTANT: PFHd is necessary, not sufficient. A real claim of PL d also needs
the required category (structure), diagnostic coverage, common cause failure
measures and systematic failure measures. In practice the PFHd of each
subsystem comes from the manufacturer's data sheet or from a calculation with
MTTFd, DC and category (ISO 13849-1, Annex K). This tool does not do that
calculation; it combines values you already have. The band limits above are
from public summaries and must be checked against the purchased standard.

Usage:
    python tools/achieved_pl.py 2e-7 1.5e-7 3e-7
    python tools/achieved_pl.py 2e-7 1.5e-7 3e-7 --target d
"""

import sys

# (lower limit inclusive, PL), highest first. Upper limit of PL a is 1e-4.
PL_BANDS = (
    (1e-8, "e"),
    (1e-7, "d"),
    (1e-6, "c"),
    (3e-6, "b"),
    (1e-5, "a"),
)
PFHD_UPPER_LIMIT = 1e-4
PL_ORDER = "abcde"


def total_pfhd(pfhd_values):
    """PFHd of a series chain of subsystems: the plain sum, in 1/h."""
    values = list(pfhd_values)
    if not values:
        raise ValueError("at least one subsystem PFHd is needed")
    if any(v < 0 for v in values):
        raise ValueError("PFHd must not be negative")
    return sum(values)


def pl_from_pfhd(pfhd):
    """Performance Level letter for a PFHd in 1/h, or None if no PL is reached."""
    if pfhd < 0:
        raise ValueError("PFHd must not be negative")
    if pfhd >= PFHD_UPPER_LIMIT:
        return None
    # PL_BANDS runs from the strictest limit to the loosest. The PL is that of
    # the loosest band whose lower limit the value has reached. Anything below
    # the strictest limit is still the top level.
    for limit, pl in reversed(PL_BANDS):
        if pfhd >= limit:
            return pl
    return PL_BANDS[0][1]


def meets_target(achieved, target):
    """True if the achieved PL letter is at least the target PL letter."""
    if target not in PL_ORDER:
        raise ValueError(f"unknown PL {target!r}, expected one of a, b, c, d, e")
    if achieved is None:
        return False
    return PL_ORDER.index(achieved) >= PL_ORDER.index(target)


def margin_to_next_level(pfhd):
    """Factor by which PFHd could grow before the PL drops one level (None if already lowest or none)."""
    pl = pl_from_pfhd(pfhd)
    if pl is None:
        return None
    i = [p for _, p in PL_BANDS].index(pl)
    upper = PL_BANDS[i + 1][0] if i + 1 < len(PL_BANDS) else PFHD_UPPER_LIMIT
    return upper / pfhd if pfhd > 0 else float("inf")


def main(argv):
    args = list(argv[1:])
    target = None
    if "--target" in args:
        i = args.index("--target")
        try:
            target = args[i + 1]
        except IndexError:
            print("--target needs a PL letter", file=sys.stderr)
            return 2
        del args[i : i + 2]
    if not args:
        print(__doc__)
        return 0

    try:
        values = [float(a) for a in args]
        total = total_pfhd(values)
        achieved = pl_from_pfhd(total)
        ok = meets_target(achieved, target) if target else None
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    print(f"subsystems: {len(values)}, total PFHd = {total:.3g} 1/h")
    print(f"achieved PL (from PFHd alone): {achieved if achieved else 'none'}")
    if target:
        print(f"target PL {target}: {'met' if ok else 'NOT met'}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
