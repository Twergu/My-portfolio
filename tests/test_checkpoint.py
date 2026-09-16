import pytest

from backend.config import Settings
from scripts.checkpoint import EvaluationCheckpoint, evaluation_identity
from scripts.evaluate import HARD_DATASET, evaluate_dataset, load_dataset


def test_checkpoint_identity_rejects_changed_scope_and_retrieval(tmp_path):
    dataset, settings = load_dataset(HARD_DATASET), Settings()
    identity = evaluation_identity(dataset, settings, "dev", "", 1)
    checkpoint = EvaluationCheckpoint(tmp_path / "run.json", identity)
    checkpoint.save({"queries": [], "indexing_attempts": []})
    assert checkpoint.load()["queries"] == []
    changed = evaluation_identity(dataset, settings.model_copy(update={"retrieval_mode": "hybrid"}), "dev", "", 1)
    with pytest.raises(ValueError, match="configuration differs"):
        EvaluationCheckpoint(checkpoint.path, changed).load()


def test_resume_preserves_completed_questions_and_indexing_cost_history(tmp_path):
    dataset, settings = load_dataset(HARD_DATASET), Settings()
    ids = [q["id"] for q in dataset["queries"] if q["split"] == "dev"][:2]
    states = []
    first = evaluate_dataset(
        dataset, settings, split="dev", only_ids=ids[:1], checkpoint=lambda s: states.append(dict(s))
    )
    completed = first["queries"][0]
    result = evaluate_dataset(dataset, settings, split="dev", only_ids=ids, resume=states[-1])
    assert len(result["queries"]) == 2
    assert result["queries"][0] == completed
    assert len(result["indexing_attempts"]) == 2
