# Security and sharing boundaries

Public portfolio deployment uses `compose.demo.yaml`, required authentication, read-only HTTP APIs, pre-retrieval ACL, Strict/all evidence verification, trusted-host/HTTPS checks, request quotas and persistent estimated API spend reservations. See [deployment guide](docs/portfolio-sharing.md) for defaults and exact limits.

The ordinary `compose.yaml` is a localhost development configuration with an explicit single-user bypass. Do not expose that listener to the internet. Demo mode is single-process, not a distributed rate limiter. Estimated token budgets do not guarantee a provider billing hard cap. Tokens have no automatic expiry; revoke each reviewer when access is no longer needed.

Do not upload private documents, access tokens, `.env*` secrets, database volumes or logs to Issues, PRs or releases. Use only fictional material for public demonstrations. If a credential has been exposed, revoke/rotate it at its issuer before considering history cleanup. Removing it from the current file is insufficient.

Report a suspected vulnerability through GitHub's private vulnerability reporting if the repository enables it; otherwise request a private contact channel without posting credentials or exploit-sensitive data publicly. This project has no external security audit or availability SLA.

`python -m scripts.release_check --git .` checks the generated ZIP and reachable Git blobs for private paths, known local credential values and common secret patterns. It is not comprehensive secret detection or a security certification. GitHub secret scanning/push protection, where enabled, provide a separate layer; their settings are not automatically changed by this project.
