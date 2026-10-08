"""Seed only fictional bundled policies; no identities, private files or default passwords."""

import argparse
import json

from backend.config import ROOT, environment_settings
from backend.governance import DocumentMetadata
from backend.main import create_app
from scripts.agent_live_smoke import make_pdf


def seed(service):
    role = "demo-reviewer"
    service.store.create_role(role)
    pages = json.loads((ROOT / "evals/agent_dataset.json").read_text(encoding="utf-8"))["pages"]
    # ReportLab defaults contain a timestamp/random ID. Invariant rendering makes repeat seeding idempotent.
    from reportlab import rl_config

    old_invariant = rl_config.invariant
    try:
        rl_config.invariant = 1
        content = make_pdf(pages)
    finally:
        rl_config.invariant = old_invariant
    document = service.register("Fictional portfolio policies.pdf", content)
    service.store.set_metadata(
        document["id"],
        DocumentMetadata(policy_status="current", document_version="fictional-demo-v1").model_dump(mode="json"),
    )
    existing = service.store.document(document["id"])
    if not document["duplicate"] or existing["status"] != "ready" or existing["profile"] != service.settings.profile:
        service.enqueue(document["id"])
        service.wait_for_jobs()
    if service.store.document(document["id"])["status"] != "ready":
        raise RuntimeError("Demo indexing failed; inspect private service logs, then retry")
    service.store.grant_document(document["id"], role, "read")
    return {
        "document_id": document["id"],
        "role": role,
        "source": "Fictional bundled Agent policies",
        "pages": len(pages),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly allow billable embedding when RAG_MODE=api")
    args = parser.parse_args()
    if environment_settings().mode == "api" and not args.live:
        parser.error("API indexing requires --live; local mode needs no API key")
    app = create_app()
    service = app.state.knowledge
    try:
        if service.settings.mode == "api" and not args.live:
            parser.error("Saved API mode requires --live")
        print(json.dumps(seed(service), ensure_ascii=False))
    finally:
        service.close()


if __name__ == "__main__":
    main()
