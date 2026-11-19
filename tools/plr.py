"""Required Performance Level (PLr) from the ISO 13849-1 risk graph.

Inputs:
    S  severity of injury        S1 = slight (normally reversible)
                                 S2 = serious (normally irreversible, or death)
    F  frequency / exposure      F1 = seldom to less often, or short exposure
                                 F2 = frequent to continuous, or long exposure
    P  possibility of avoidance  P1 = possible under specific conditions
                                 P2 = scarcely possible
"""

RISK_GRAPH = {
    ("S1", "F1", "P1"): "a",
    ("S1", "F1", "P2"): "b",
    ("S1", "F2", "P1"): "b",
    ("S1", "F2", "P2"): "c",
    ("S2", "F1", "P1"): "c",
    ("S2", "F1", "P2"): "d",
    ("S2", "F2", "P1"): "d",
    ("S2", "F2", "P2"): "e",
}

PL_ORDER = "abcde"


def required_pl(s: str, f: str, p: str) -> str:
    """Return the required Performance Level 'a'..'e' for one hazard."""
    key = (s.strip().upper(), f.strip().upper(), p.strip().upper())
    if key not in RISK_GRAPH:
        raise ValueError(f"Invalid risk parameters: S={s!r}, F={f!r}, P={p!r}")
    return RISK_GRAPH[key]


def pl_at_least(achieved: str, required: str) -> bool:
    """True if PL 'achieved' is equal to or higher than PL 'required'."""
    return PL_ORDER.index(achieved.lower()) >= PL_ORDER.index(required.lower())


def highest_pl(levels) -> str:
    """Return the highest PL in an iterable of levels."""
    return max(levels, key=lambda pl: PL_ORDER.index(pl.lower()))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python plr.py S2 F1 P2")
        sys.exit(1)
    print(f"PLr = {required_pl(*sys.argv[1:])}")
