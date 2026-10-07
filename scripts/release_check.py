"""Check source ZIP and optional reachable Git history without printing secret values.

This is a bounded pattern/known-value check, not a penetration test or proof of
absence of every possible credential. No remote publishing or history rewriting.
"""

import argparse
import hashlib
import io
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    rb"sk-(?:proj-)?[A-Za-z0-9_-]{30,}",
    rb"gh[pousr]_[A-Za-z0-9]{30,}",
    rb"github_pat_[A-Za-z0-9_]{30,}",
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]
DENIED_PARTS = {".git", ".delivery", ".secrets", ".venv", "data", "pgdata", "test-results", "__pycache__"}


def private_path(name):
    path = Path(name)
    return (
        any(p in DENIED_PARTS for p in path.parts)
        or (path.name.startswith(".env") and not path.name.endswith(".example"))
        or path.suffix.lower() in (".sqlite3", ".db", ".log", ".pem", ".key")
    )


def sensitive(content, secrets=()):
    return any(secret in content for secret in secrets if secret) or any(re.search(p, content) for p in PATTERNS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "exports/knowbase-source-latest.zip")
    parser.add_argument("--git", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "exports/knowbase-release-check.json")
    args = parser.parse_args()
    secrets = []
    for env_file in (ROOT / ".env", ROOT / ".env.demo"):
        if env_file.exists():
            secrets += [
                v.encode()
                for k, v in dotenv_values(env_file).items()
                if re.search(r"_(KEY|TOKEN|PASSWORD|SECRET)$", k) and v and len(v) >= 12
            ]
    findings = []
    with ZipFile(args.archive) as archive:
        if archive.testzip():
            raise SystemExit("Archive integrity failed")
        names = archive.namelist()
        for name in names:
            if private_path(name) or sensitive(archive.read(name), secrets):
                findings.append({"scope": "archive", "file": name})
    history_blobs = 0
    git_head = None
    if args.git:

        def git(*arguments, **kwargs):
            return subprocess.run(
                ["git", "-C", str(args.git), *arguments], capture_output=True, check=True, **kwargs
            ).stdout

        git_head = git("rev-parse", "HEAD").decode().strip()
        objects = git("rev-list", "--objects", "--all").decode().splitlines()
        object_names = dict(line.split(" ", 1) if " " in line else (line, "") for line in objects)
        stream = io.BytesIO(git("cat-file", "--batch", input=("\n".join(object_names) + "\n").encode()))
        while header := stream.readline():
            oid, kind, size = header.decode().strip().split()
            data = stream.read(int(size))
            assert stream.read(1) == b"\n"
            if kind == "blob":
                history_blobs += 1
                if private_path(object_names[oid]) or sensitive(data, secrets):
                    findings.append({"scope": "git-history", "object": oid, "file": object_names[oid]})
    result = {
        "at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not findings else "failed",
        "archive": args.archive.name,
        "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        "archive_files": len(names),
        "reachable_git_blobs_checked": history_blobs,
        "git_head": git_head,
        "findings": findings,
        "scope": "Known local credential values, common key/private-key patterns and private paths; no guarantee for unknown secret formats, unreachable Git objects, or provider billing/security",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
