"""Shared multilingual analyzer for SQLite FTS5 and PostgreSQL full-text search.

Hashed ASCII lexemes avoid backend-specific tokenization of Japanese, policy
identifiers and dates. They are search terms, never SQL or FTS query syntax.
"""

import hashlib
import re
import unicodedata

STOP = frozenset("the a an is are what how to of for in and do does please".split())


def tokens(text):
    result = []
    text = unicodedata.normalize("NFKC", text).casefold()
    for part in re.findall(r"[a-z0-9]+(?:[-./][a-z0-9]+)*|[\u3040-\u30ff\u3400-\u9fff]+", text):
        if re.fullmatch(r"[\u3040-\u30ff\u3400-\u9fff]+", part):
            result.extend(part[i : i + 2] for i in range(len(part) - 1))
            if len(part) == 1:
                result.append(part)
        elif part not in STOP:
            result.append(part)
            if re.search(r"[-./]", part):
                result.extend(p for p in re.split(r"[-./]", part) if p not in STOP)
    return result


def lexemes(text):
    return ["t" + hashlib.blake2b(token.encode(), digest_size=12).hexdigest() for token in tokens(text)]


def indexed_text(text):
    return " ".join(lexemes(text))


def query_terms(text):
    # Bound query complexity, preserving stable order and exact identifiers.
    return list(dict.fromkeys(lexemes(text)))[:128]


def reciprocal_rank_fusion(*rankings, k=60, limit=20):
    """Fuse ranks, not incomparable cosine/BM25/ts_rank scores."""
    scores, rows = {}, {}
    for ranking in rankings:
        seen = set()
        for rank, row in enumerate(ranking, 1):
            key = row["id"]
            if key in seen:
                continue
            seen.add(key)
            rows.setdefault(key, dict(row))
            scores[key] = scores.get(key, 0) + 1 / (k + rank)
    return [rows[key] | {"score": scores[key]} for key in sorted(scores, key=lambda key: (-scores[key], key))[:limit]]
