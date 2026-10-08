"""Operator CLI: provision identities, rotate/revoke tokens and assign role grants.

Tokens are written once to a specified private file; never printed to stdout.
Run against the same RAG_DATA_DIR / RAG_DATABASE_URL as the application.
"""

import argparse
import os
from pathlib import Path

from backend.config import DATA_DIR
from backend.store import create_store


def write_token(path, token):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(token + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    create = sub.add_parser("create-user")
    create.add_argument("username")
    create.add_argument("--roles", nargs="+", default=["reader"])
    create.add_argument("--token-file", type=Path, required=True)
    role = sub.add_parser("create-role")
    role.add_argument("name")
    assign = sub.add_parser("set-roles")
    assign.add_argument("user_id")
    assign.add_argument("roles", nargs="+")
    for action in ("disable-user", "enable-user", "rotate-token"):
        cmd = sub.add_parser(action)
        cmd.add_argument("user_id")
        if action == "rotate-token":
            cmd.add_argument("--token-file", type=Path, required=True)
    grant = sub.add_parser("grant")
    grant.add_argument("document_id")
    grant.add_argument("role")
    grant.add_argument("permission", choices=["read", "write", "revoke"])
    sub.add_parser("list-users")
    args = p.parse_args()
    if hasattr(args, "token_file") and args.token_file.exists():
        p.error("Token file already exists; choose a new private path")
    store = create_store(DATA_DIR, recover=False)
    try:
        if args.action == "create-user":
            user_id, token = store.provision_user(args.username, args.roles)
            try:
                write_token(args.token_file, token)
            except Exception:
                store.set_user_active(user_id, False)
                raise
            print("Created user:", user_id, "Token saved to the specified private file.")
        elif args.action == "create-role":
            store.create_role(args.name)
        elif args.action == "set-roles":
            store.set_user_roles(args.user_id, args.roles)
        elif args.action in ("disable-user", "enable-user"):
            store.set_user_active(args.user_id, args.action == "enable-user")
        elif args.action == "rotate-token":
            write_token(args.token_file, store.rotate_token(args.user_id))
        elif args.action == "grant":
            store.grant_document(args.document_id, args.role, None if args.permission == "revoke" else args.permission)
        else:
            for user in store.list_users():
                print(user)
    finally:
        store.close()


if __name__ == "__main__":
    main()
