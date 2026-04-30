"""Handicap math for 9-hole rounds (USGA-style, simplified for a league)."""

from __future__ import annotations

from statistics import mean


def differential(adj_gross: float, course_rating: float, slope: float) -> float:
    """Standard handicap differential: (Score - CR) * 113 / Slope."""
    return (adj_gross - course_rating) * 113.0 / slope


# USGA "best N of last 20" table (9-hole equivalent same idea).
# (rounds_used_in_avg, adjustment) keyed by total rounds available.
BEST_OF_TABLE = {
    3: (1, -2.0),
    4: (1, -1.0),
    5: (1, 0.0),
    6: (2, -1.0),
    7: (2, 0.0),
    8: (2, 0.0),
    9: (3, 0.0),
    10: (3, 0.0),
    11: (3, 0.0),
    12: (4, 0.0),
    13: (4, 0.0),
    14: (4, 0.0),
    15: (5, 0.0),
    16: (5, 0.0),
    17: (6, 0.0),
    18: (6, 0.0),
    19: (7, 0.0),
    20: (8, 0.0),
}


def handicap_index(diffs):
    """Compute handicap index from a list of recent differentials.

    Uses USGA best-of-table on the most recent 20. Returns None with <3 rounds.
    """
    if len(diffs) < 3:
        return None
    recent = diffs[-20:]
    n = len(recent)
    if n >= 20:
        n = 20
    count, adj = BEST_OF_TABLE[n]
    best = sorted(recent)[:count]
    return round(mean(best) * 0.96 + adj, 1)


def course_handicap(index: float, slope: float, rating: float, par: float) -> int:
    """Course handicap from index for a specific tee box."""
    return round(index * (slope / 113.0) + (rating - par))
