"""Run the dependency-free frontend tests and derive a report from Node's TAP output."""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    tests = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "tests/frontend").glob("*.test.cjs"))
    if not tests:
        raise SystemExit("No frontend test files found")
    result = subprocess.run(
        ["node", "--test", "--test-reporter=tap", *tests], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    folder = ROOT / "reports/agent-stage3"
    folder.mkdir(parents=True, exist_ok=True)
    raw = result.stdout + result.stderr
    (folder / "frontend-tests.tap").write_text(raw, encoding="utf-8")
    counts = {key: int(value) for key, value in re.findall(r"^# (tests|pass|fail|skipped|cancelled) (\d+)$", raw, re.M)}
    passed = result.returncode == 0 and counts.get("tests", 0) > 0 and counts.get("pass") == counts["tests"]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": "python -m scripts.check_frontend",
        "status": "passed" if passed else "failed",
        "counts": counts,
        "tests": tests,
        "raw_output": "frontend-tests.tap",
    }
    (folder / "frontend-tests.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(raw)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
