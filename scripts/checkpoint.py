"""Atomic, configuration-bound experiment checkpoints; no credentials."""

import hashlib
import json
from pathlib import Path


def evaluation_identity(dataset, settings, split, judge_model, concurrency):
    from evals.judge import EVALUATION_PROTOCOL

    return {
        "dataset_sha256": hashlib.sha256(json.dumps(dataset, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "configuration": settings.model_dump(exclude={"base_url"}),
        "embedding_profile": settings.profile,
        "split": split,
        "judge_model": judge_model,
        "concurrency": concurrency,
        "protocol": EVALUATION_PROTOCOL,
        "checkpoint_version": 1,
    }


class EvaluationCheckpoint:
    def __init__(self, path, identity):
        self.path, self.identity = Path(path), identity

    def load(self):
        if not self.path.exists():
            return None
        result = json.loads(self.path.read_text(encoding="utf-8"))
        if result["identity"] != self.identity:
            raise ValueError("Checkpoint configuration differs; choose a new output path")
        return result["state"]

    def save(self, state):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps({"identity": self.identity, "state": state}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)
