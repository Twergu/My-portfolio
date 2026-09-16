"""Create a persistent private Compose database password on first startup."""

import os
import secrets
from pathlib import Path


def initialize(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "postgres_password"
    if target.exists() and target.stat().st_size:
        return
    temporary = folder / "postgres_password.tmp"
    temporary.write_text(secrets.token_urlsafe(32), encoding="utf-8")
    temporary.chmod(0o444)
    os.replace(temporary, target)


if __name__ == "__main__":
    initialize("/run/knowbase-secrets")
