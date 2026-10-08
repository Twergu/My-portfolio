import json

import pytest

from backend.config import Settings
from backend.lexical import reciprocal_rank_fusion
from backend.providers import ModelError
from backend.reranking import rerank
from backend.telemetry import Metrics


def test_rrf_combines_ranks_not_raw_scores_and_deduplicates():
    dense = [{"id": "a", "score": 0.99}, {"id": "b", "score": 0.7}]
    sparse = [{"id": "b", "score": 500}, {"id": "c", "score": 100}]
    assert [r["id"] for r in reciprocal_rank_fusion(dense, sparse)] == ["b", "a", "c"]
    assert len(reciprocal_rank_fusion(dense, dense, limit=1)) == 1


@pytest.mark.parametrize("ranking", [[1, 1], [0, 2], [1], [True, 2], [1, 2, 3]])
def test_reranker_rejects_missing_duplicate_or_invented_ids(ranking):
    class Provider:
        def chat(self, *args, **kwargs):
            return json.dumps({"ranked_ids": ranking})

    rows = [{"id": i, "name": "policy", "page": 1, "text": str(i)} for i in range(2)]
    with pytest.raises(ModelError, match="Reranker"):
        rerank("question", rows, Settings(), "", Provider(), Metrics())


def test_reranker_only_reorders_existing_evidence():
    class Provider:
        def chat(self, settings, key, messages, **kwargs):
            assert kwargs["role"] == "reranker"
            assert len(json.loads(messages[1]["content"])["candidates"]) == 20
            return json.dumps({"ranked_ids": list(range(20, 0, -1))})

    rows = [{"id": i, "name": "policy", "page": 1, "text": str(i)} for i in range(20)]
    result = rerank("question", rows, Settings(), "", Provider(), Metrics())
    assert [r["id"] for r in result[:5]] == [19, 18, 17, 16, 15]
    assert all(row is rows[row["id"]] for row in result)


def test_reranker_repairs_format_once_and_keeps_failure_record():
    class Provider:
        calls = 0

        def chat(self, *args, **kwargs):
            self.calls += 1
            return json.dumps({"ranked_ids": [2] if self.calls == 1 else [2, 1]})

    provider, metrics = Provider(), Metrics()
    rows = [{"id": i, "name": "policy", "page": 1, "text": str(i)} for i in range(2)]
    assert rerank("question", rows, Settings(), "", provider, metrics)[0]["id"] == 1
    assert provider.calls == 2 and len(metrics.validation_failures) == 1
