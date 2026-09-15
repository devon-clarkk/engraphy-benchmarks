"""Apply the engine's migrations to a fresh database, as dbmate would.

Run under the reproduction's virtualenv, which carries psycopg:

    python -m benchkit.migrate --url <superuser-url> --engine work/engraphy

Each file's `-- migrate:up` section runs in its own transaction and its version
is recorded in `schema_migrations`, which is dbmate's contract. None of the
engine's migrations opts out of the transaction (`transaction:false`), and this
refuses to run one that does rather than guess at the semantics. Doing it here
instead of shelling out to dbmate keeps a reproduction to Docker, git and Python
on every platform.
"""

from __future__ import annotations

import argparse
import pathlib
import sys


def migrate(url: str, migrations: pathlib.Path) -> list[str]:
    import psycopg

    files = sorted(migrations.glob("*.sql"))
    if not files:
        raise SystemExit(f"no migrations under {migrations}")
    applied: list[str] = []
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations "
                     "(version varchar(128) PRIMARY KEY)")
        done = {r[0] for r in conn.execute("SELECT version FROM schema_migrations").fetchall()}
        for f in files:
            version = f.name.split("_", 1)[0]
            if version in done:
                continue
            text = f.read_text(encoding="utf-8")
            header = text.split("\n", 1)[0]
            if "transaction:false" in header:
                raise SystemExit(f"{f.name} opts out of the transaction; apply it with dbmate")
            up = text.split("-- migrate:up", 1)[1].split("-- migrate:down", 1)[0]
            with conn.transaction():
                conn.execute(up)
                conn.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
            applied.append(f.name)
        latest = conn.execute("SELECT max(version) FROM schema_migrations").fetchone()[0]
    print(f"migrations: {len(applied)} applied, schema at {latest}")
    return applied


def main() -> int:
    ap = argparse.ArgumentParser(prog="benchkit.migrate")
    ap.add_argument("--url", required=True)
    ap.add_argument("--engine", required=True, type=pathlib.Path)
    args = ap.parse_args()
    migrate(args.url, args.engine / "engraphy" / "db" / "migrations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
