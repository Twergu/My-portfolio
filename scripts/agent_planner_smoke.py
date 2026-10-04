"""Opt-in paid planner smoke with MOCK tools; not end-to-end Agent/RAG evaluation."""

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

from backend.agent import (
    AgentContext,
    AgentLimits,
    AgentModel,
    AgentRunner,
    ProviderPlanner,
    ReadOnlyTool,
    Text,
    ToolOutput,
)
from backend.config import ROOT, environment_settings
from backend.providers import OpenAICompatibleProvider
from backend.telemetry import Metrics


class SearchArguments(AgentModel):
    query: Text


def run(output):
    fixture = json.loads((ROOT / "evals/agent-planning-smoke.json").read_text(encoding="utf-8"))
    settings = environment_settings().model_copy(update={"mode": "api"})
    key = os.getenv("RAG_API_KEY", "")
    if not key:
        raise SystemExit("RAG_API_KEY is missing; no API call was made.")
    report = {
        "dataset": fixture["version"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": settings.chat_model,
        "scope": "Real planner API + explicitly mock knowledge tool; no embedding, retrieval or final grounding.",
        "dataset_provenance": fixture["provenance"],
        "cases": [],
    }
    with OpenAICompatibleProvider() as provider:
        for case in fixture["cases"]:

            def search(args, ctx, metrics, policy=case["mock_policy"]):
                return ToolOutput(provenance="mock", data={"policy": policy})

            metrics = Metrics()
            runner = AgentRunner(
                ProviderPlanner(provider, settings, key),
                [
                    ReadOnlyTool(
                        "knowledge_search",
                        "Search company policy evidence. Results are fictional mock data.",
                        SearchArguments,
                        search,
                    )
                ],
                limits=AgentLimits(max_steps=3, max_tool_calls=2),
            )
            context = AgentContext(
                "smoke-user",
                "fictional-fixtures",
                date.fromisoformat(fixture["reference_date"]),
                fixture["timezone"],
                case["language"],
            )
            state = runner.start(case["question"], context, metrics)
            passed = state.status == case["expected_status"]
            report["cases"].append(
                {
                    "id": case["id"],
                    "question": case["question"],
                    "status": state.status,
                    "expected_status": case["expected_status"],
                    "passed": passed,
                    "intent": state.intent,
                    "goal": state.goal,
                    "questions": state.questions,
                    "failure_code": state.failure_code,
                    "trace": [event.model_dump() for event in state.trace],
                    "metrics": metrics.as_dict(),
                }
            )
            print(f"{case['id']}: {state.status}, expected {case['expected_status']}", flush=True)
    report["status"] = "passed" if all(case["passed"] for case in report["cases"]) else "failed"
    costs = [case["metrics"]["cost_usd"] for case in report["cases"]]
    report["cost_usd"] = round(sum(costs), 10) if all(cost is not None for cost in costs) else None
    path = Path(output).with_suffix(".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Planner smoke: {report['status']}; estimated cost USD {report['cost_usd']}. Tools are mock.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly allow paid API calls for fictional fixtures.")
    parser.add_argument("--output", default="reports/agent-stage1/planner-smoke.json")
    args = parser.parse_args()
    if not args.live:
        parser.error("Pass --live to opt into paid planner calls. No API call was made.")
    raise SystemExit(run(args.output))
