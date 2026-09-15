"""A throwaway pgvector Postgres for one reproduction.

The harness writes to a real database because the dedup write path, the schema
triggers and Row-Level Security are all enforced in Postgres. This starts one in
Docker, bound to loopback only, and provisions it the way a deployment is
provisioned: every migration applied in order, then the app role created by the
engine's own `deploy/provision-app-role.sql`.

Nothing here connects to any database it did not start.
"""

from __future__ import annotations

import shutil
import subprocess
import time

DB_NAME = "engraphy_bench"

# Both passwords are fixed by the pinned engine, not chosen here. The harness
# derives its app-role connection by replacing `postgres:engraphy@` in the
# superuser URL with `engraphy_app:engraphy_app_test_only@` (bench/core/run.py,
# APP_DB), so any other value breaks the run. They are the engine test suite's
# public test credentials, and they only ever reach a container bound to
# 127.0.0.1 that this script created and can remove with --remove-db.
SUPERUSER_PASSWORD = "engraphy"
APP_ROLE_PASSWORD = "engraphy_app_test_only"


class DatabaseError(RuntimeError):
    pass


def url(port: int) -> str:
    return (f"postgres://postgres:{SUPERUSER_PASSWORD}@127.0.0.1:{port}/{DB_NAME}"
            "?sslmode=disable")


def _docker(*args: str, check: bool = True, **kw) -> subprocess.CompletedProcess:
    if not shutil.which("docker"):
        raise DatabaseError("docker is not on PATH; the benchmark needs a pgvector container")
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check, **kw)


def start(name: str, port: int, image: str, *, timeout_s: float = 120.0) -> None:
    """Start the container, or reuse it if one by this name is already running."""
    state = _docker("inspect", "-f", "{{.State.Running}}", name, check=False)
    if state.returncode == 0 and state.stdout.strip() == "true":
        return
    if state.returncode == 0:
        _docker("start", name)
    else:
        _docker("run", "-d", "--name", name,
                "-p", f"127.0.0.1:{port}:5432",
                "-e", f"POSTGRES_PASSWORD={SUPERUSER_PASSWORD}",
                "-e", f"POSTGRES_DB={DB_NAME}",
                image)
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        ready = _docker("exec", name, "pg_isready", "-U", "postgres", "-d", DB_NAME, check=False)
        if ready.returncode == 0:
            return
        time.sleep(1.0)
    raise DatabaseError(f"{name} did not become ready within {timeout_s:.0f}s")


def provision_app_role(name: str, sql: str) -> None:
    """Run the engine's shipped provisioning script inside the container."""
    proc = _docker("exec", "-i", name, "psql", "-U", "postgres", "-d", DB_NAME,
                   "-v", f"app_role_password={APP_ROLE_PASSWORD}", "-f", "-",
                   input=sql, check=False)
    if proc.returncode != 0:
        raise DatabaseError(f"provision-app-role.sql failed: {proc.stderr[-800:]}")


def server_facts(name: str) -> dict:
    """Postgres and pgvector versions, for provenance."""
    q = ("SELECT current_setting('server_version') || '|' || "
         "coalesce((SELECT extversion FROM pg_extension WHERE extname = 'vector'), '')")
    out = _docker("exec", name, "psql", "-U", "postgres", "-d", DB_NAME, "-tAc", q,
                  check=False).stdout.strip()
    pg, _, vec = out.partition("|")
    return {"postgres": pg, "pgvector": vec}


def stop(name: str) -> None:
    _docker("rm", "-f", name, check=False)
