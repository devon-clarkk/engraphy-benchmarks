"""The pinned engine checkout and the virtualenv that runs it.

The harness is not copied into this repository. It is run from a checkout of the
engine at the exact commit `config/locomo.json` names, so there is one harness,
and the commit in the config is the commit that ran. A checkout at any other
commit, or with local edits, is refused.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys


class EngineError(RuntimeError):
    pass


def _git(*args: str, cwd: pathlib.Path | None = None) -> str:
    if not shutil.which("git"):
        raise EngineError("git is not on PATH")
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise EngineError(f"git {' '.join(args)} failed: {proc.stderr.strip()[-500:]}")
    return proc.stdout.strip()


def ensure_checkout(cfg: dict, work: pathlib.Path) -> pathlib.Path:
    """Clone the engine if needed and put it at the pinned commit, on a branch
    named for the pinned ref so the run manifest records a meaningful name."""
    eng = cfg["engine"]
    path = work / "engraphy"
    if not (path / ".git").exists():
        work.mkdir(parents=True, exist_ok=True)
        _git("clone", "--quiet", eng["repository"], str(path))
    head = _git("rev-parse", "HEAD", cwd=path)
    if head != eng["commit"]:
        try:
            _git("cat-file", "-e", f"{eng['commit']}^{{commit}}", cwd=path)
        except EngineError:
            _git("fetch", "--quiet", "origin", eng["fetch_refspec"], cwd=path)
        _git("checkout", "--quiet", "-B", eng["ref"], eng["commit"], cwd=path)
    assert_pinned(cfg, path)
    return path


def assert_pinned(cfg: dict, path: pathlib.Path) -> None:
    head = _git("rev-parse", "HEAD", cwd=path)
    if head != cfg["engine"]["commit"]:
        raise EngineError(f"{path} is at {head}, not the pinned {cfg['engine']['commit']}")
    dirty = _git("status", "--porcelain", "--untracked-files=no", cwd=path)
    if dirty:
        raise EngineError(f"{path} has local modifications; a reproduction runs the pinned "
                          f"tree unmodified:\n{dirty}")


def venv_python(work: pathlib.Path) -> pathlib.Path:
    sub = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    return work / "venv" / sub


def ensure_venv(work: pathlib.Path, engine: pathlib.Path) -> pathlib.Path:
    """A virtualenv with the engine installed from the pinned checkout.

    The engine's default install, not its `dev` extra: the benchmark needs the
    ONNX embedder and Postgres drivers, and the `dev` extra adds PyTorch for the
    legacy embedding profile, which a benchmark on the default profile never loads.
    """
    py = venv_python(work)
    if not py.exists():
        subprocess.run([sys.executable, "-m", "venv", str(work / "venv")], check=True)
        subprocess.run([str(py), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
                       check=True)
    stamp = work / "venv" / ".engine-commit"
    commit = _git("rev-parse", "HEAD", cwd=engine)
    if not stamp.exists() or stamp.read_text().strip() != commit:
        subprocess.run([str(py), "-m", "pip", "install", "--quiet", "-e", str(engine)],
                       check=True)
        stamp.write_text(commit)
    return py
