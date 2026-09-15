#!/usr/bin/env python3
"""Reproduce Engraphy's LoCoMo figure end to end, in one command.

    python reproduce.py

What it does, in order, every step resumable:

1. Clones the engine at the commit pinned in config/locomo.json and refuses any
   other commit or a modified tree.
2. Builds a virtualenv with the engine installed from that checkout.
3. Starts a pgvector Postgres in Docker on 127.0.0.1, applies every migration,
   and provisions the app role with the engine's own deploy script.
4. Downloads LoCoMo from snap-research and verifies its sha256 against the pin.
5. Runs the engine's harness with exactly the arm, conversations, models, judge
   and phases in the config, under its supervisor, which pauses across a usage
   limit and resumes from the checkpoint.
6. Records the host, runtime and database versions beside the run.
7. Writes the committable subset of the run to results/locomo/<run-id>/, with
   every piece of dataset text removed, and prints the headline table.

Run the same command again to resume an interrupted run. Nothing touches a
database this script did not start.

Requires git, Docker, Python 3.12 or later, and the route named in the config.
At the pinned engine commit that route is the Claude Code CLI (`claude` on PATH,
signed in). See METHODOLOGY.md for what the number means and what it is
comparable to.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from benchkit import (
    ROOT,
    WORK,
    database,
    dataset,
    engine,
    load_config,
    provenance,
    redact,
)


def _step(n: int, text: str) -> None:
    print(f"\n[{n}/7] {text}", flush=True)


def preflight(cfg: dict) -> None:
    missing = [tool for tool in ("git", "docker") if not shutil.which(tool)]
    if cfg["models"]["route"] == "claude-cli" and not shutil.which("claude"):
        missing.append("claude (the Claude Code CLI, signed in)")
    if missing:
        raise SystemExit("missing prerequisites: " + ", ".join(missing))
    # Kept although pyproject declares 3.12: this script is run directly, not
    # installed, so nothing else stops an older interpreter reaching step 1.
    if sys.version_info < (3, 12):  # noqa: UP036
        raise SystemExit(f"Python 3.12 or later is required, this is {sys.version.split()[0]}")


def harness_command(cfg: dict, py: pathlib.Path, run_id: str, supervised: bool) -> list[str]:
    run = cfg["run"]
    core = [
        str(py), "-m", "bench.core.run",
        "--dataset", "datasets/locomo10.json",
        "--haystacks", ",".join(run["haystacks"]),
        "--arm", run["arm"],
        "--judge", run["judge"],
        "--reader-stance", run["reader_stance"],
        "--phases", run["phases"],
        "--concurrency", str(run["concurrency"]),
        "--judge-concurrency", str(run["judge_concurrency"]),
        "--calibration-sample", str(run["calibration_sample"]),
        "--run-id", run_id,
    ]
    if not supervised:
        return core
    return [str(py), "-m", "bench.supervise",
            "--run-dir", f"runs/{run_id}", "--log", f"runs/{run_id}.supervise.log",
            "--", *core]


def harness_env(cfg: dict, port: int) -> dict:
    env = dict(os.environ)
    # The CLI route runs on a signed-in subscription. An API key in the
    # environment would switch it to API billing, so it never reaches the run.
    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(var, None)
    env["ENGRAPHY_TEST_DATABASE_URL"] = database.url(port)
    env["ENGRAPHY_EMBEDDING_PROFILE"] = cfg["embedder"]["profile"]
    return env


def summarise(manifest: dict) -> str:
    lines = []
    for arm, agg in (manifest.get("aggregate") or {}).items():
        lines.append(f"arm {arm}")
        rows = [("overall", agg.get("overall")),
                ("excluding adversarial", agg.get("overall_excl_adversarial"))]
        rows += sorted((agg.get("categories") or {}).items())
        for name, b in rows:
            if not b or not b.get("n"):
                continue
            lo, hi = b["wilson_95"]
            lines.append(f"  {name:24s} {100 * b['accuracy']:5.1f}%  "
                         f"[{100 * lo:.0f} to {100 * hi:.0f}]  "
                         f"{b['correct']}/{b['n']}")
    return "\n".join(lines) or "(no aggregate in the manifest yet)"


def publish(cfg: dict, run_dir: pathlib.Path, dest: pathlib.Path,
            index: dict, facts: dict) -> None:
    """Write the committable subset, then refuse it if any dataset text survived."""
    written = redact.redact_run(run_dir, dest)
    (dest / "provenance.json").write_text(json.dumps(facts, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    (dest / "config.json").write_text(json.dumps(cfg, indent=2) + "\n",
                                      encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "render_provenance.py"), str(dest)],
                   check=True)
    hits = redact.check_clean(dest, index)
    if hits:
        raise SystemExit(f"refusing to publish {dest}: dataset questions quoted in {hits}")
    for name, what in written.items():
        print(f"  {name}: {what}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="reproduce.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--run-id", default=f"locomo-{datetime.date.today():%Y%m%d}")
    ap.add_argument("--port", type=int, default=5439,
                    help="loopback port for the Postgres container")
    ap.add_argument("--container", default="engraphy-benchmarks-pg")
    ap.add_argument("--no-supervisor", action="store_true",
                    help="run the harness directly rather than under its usage-limit supervisor")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan and the exact command, run nothing")
    ap.add_argument("--remove-db", action="store_true",
                    help="remove the Postgres container afterwards")
    args = ap.parse_args()

    cfg = load_config()
    py = engine.venv_python(WORK)
    cmd = harness_command(cfg, py, args.run_id, not args.no_supervisor)
    if args.dry_run:
        print(json.dumps({"engine": cfg["engine"], "dataset": cfg["dataset"]["sha256"],
                          "database": database.url(args.port), "command": cmd}, indent=2))
        return 0

    preflight(cfg)

    _step(1, f"engine at {cfg['engine']['commit'][:12]}")
    eng = engine.ensure_checkout(cfg, WORK)

    _step(2, "virtualenv with the pinned engine installed")
    py = engine.ensure_venv(WORK, eng)

    _step(3, f"Postgres in Docker on 127.0.0.1:{args.port}")
    database.start(args.container, args.port, cfg["database"]["image"])
    subprocess.run([str(py), "-m", "benchkit.migrate", "--url", database.url(args.port),
                    "--engine", str(eng)], cwd=ROOT, check=True)
    database.provision_app_role(
        args.container, (eng / "deploy" / "provision-app-role.sql").read_text(encoding="utf-8"))

    _step(4, "LoCoMo from snap-research, sha256 verified")
    data_path = dataset.fetch(cfg, eng / "datasets")
    print(f"  {data_path} {cfg['dataset']['sha256']}")

    _step(5, "the harness (resumable; run this command again to continue)")
    print("  " + " ".join(cmd[cmd.index("bench.core.run") - 2:]), flush=True)
    engine.assert_pinned(cfg, eng)
    proc = subprocess.run(cmd, cwd=eng, env=harness_env(cfg, args.port))

    run_dir = eng / "runs" / args.run_id
    manifest_path = run_dir / "manifest.json"
    manifest = (json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest_path.exists() else {})
    if proc.returncode != 0 or manifest.get("quota_stop") or not manifest.get("aggregate"):
        print("\nThe run stopped before it finished. Run the same command again to resume "
              f"from runs/{args.run_id}.")
        return proc.returncode or 1

    _step(6, "provenance")
    facts = provenance.capture(python=str(py), db=database.server_facts(args.container),
                               engine_commit=cfg["engine"]["commit"],
                               engine_ref=cfg["engine"]["ref"])

    _step(7, "committable results")
    dest = ROOT / "results" / "locomo" / args.run_id
    publish(cfg, run_dir, dest, dataset.question_index(data_path), facts)
    print(f"  written to {dest.relative_to(ROOT)}")

    print("\n" + summarise(manifest))
    if args.remove_db:
        database.stop(args.container)
    return 0


if __name__ == "__main__":
    sys.exit(main())
