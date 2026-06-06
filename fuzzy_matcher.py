"""
Fuzzy matching utilities using rapidfuzz (preferred) with difflib fallback.
"""
try:
    from rapidfuzz import process, fuzz
    _HAS_RAPIDFUZZ = True
except Exception:
    _HAS_RAPIDFUZZ = False

from difflib import get_close_matches
from typing import Iterable, Optional, Tuple


def best_match(query: str, candidates: Iterable[str], threshold: float = 80.0) -> Optional[Tuple[str, float]]:
    """Return the best candidate and score for `query` from `candidates`.

    If rapidfuzz is available, returns (candidate, score) with score in 0-100.
    Otherwise uses difflib and returns (candidate, score) with score in 0-100.
    """
    candidates = list(map(str, candidates))
    if not candidates:
        return None

    q = str(query).strip()
    if not q:
        return None

    # quick exact/ci-substring checks
    ql = q.lower()
    for c in candidates:
        if c.lower() == ql:
            return c, 100.0
    for c in candidates:
        if c.lower() in ql or ql in c.lower():
            return c, 100.0

    if _HAS_RAPIDFUZZ:
        match = process.extractOne(q, candidates, scorer=fuzz.WRatio)
        if match and match[1] >= threshold:
            return match[0], float(match[1])
        return None

    # difflib fallback: get_close_matches returns list
    # map similarity roughly by ratio of matches
    close = get_close_matches(q, candidates, n=1, cutoff=threshold / 100.0)
    if close:
        # approximate score using sequence matcher
        from difflib import SequenceMatcher

        s = SequenceMatcher(None, q, close[0])
        return close[0], float(s.ratio() * 100)
    return None
