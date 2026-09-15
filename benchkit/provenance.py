"""What a run ran on, captured at the time it ran.

The engine's manifest already records the dataset digest, the models, the prompt
hashes, the pack hashes, the embedding model and the thresholds. This adds what
the engine cannot see from inside: the host, the runtime versions and the
container, so a second run on different hardware can say what differed.

Every field is best-effort and platform-aware. A field that cannot be read is
recorded as unknown rather than guessed.
"""

from __future__ import annotations

import datetime
import os
import platform
import shutil
import subprocess

PACKAGES = ("onnxruntime", "tokenizers", "numpy", "psycopg", "psycopg-pool",
            "huggingface-hub", "pyyaml")


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def cpu_name() -> str:
    system = platform.system()
    if system == "Windows":
        out = _run(["powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name"])
        return out or platform.processor() or "unknown"
    if system == "Darwin":
        return _run(["sysctl", "-n", "machdep.cpu.brand_string"]) or "unknown"
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


def ram_gb() -> float | None:
    system = platform.system()
    try:
        if system == "Windows":
            out = _run(["powershell", "-NoProfile", "-Command",
                        "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"])
            return round(int(out) / 2**30, 1) if out else None
        if system == "Darwin":
            out = _run(["sysctl", "-n", "hw.memsize"])
            return round(int(out) / 2**30, 1) if out else None
        with open("/proc/meminfo", encoding="utf-8") as fh:
            kb = int(fh.readline().split()[1])
        return round(kb / 2**20, 1)
    except (OSError, ValueError, IndexError):
        return None


_VERSIONS = """
import importlib.metadata as m, json, sys
out = {}
for name in sys.argv[1:]:
    try:
        out[name] = m.version(name)
    except m.PackageNotFoundError:
        out[name] = None
print(json.dumps(out))
"""


def package_versions(python: str) -> dict[str, str | None]:
    """Versions as the run's own interpreter sees them, not this one."""
    import json

    try:
        return json.loads(_run([python, "-c", _VERSIONS, *PACKAGES]))
    except ValueError:
        return {}


def capture(*, python: str, db: dict, engine_commit: str, engine_ref: str) -> dict:
    return {
        "captured_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "host": {
            "os": f"{platform.system()} {platform.release()} ({platform.version()})",
            "machine": platform.machine(),
            "cpu": cpu_name(),
            "logical_cpus": os.cpu_count(),
            "ram_gb": ram_gb(),
        },
        "runtime": {
            "python": _run([python, "-c", "import sys; print(sys.version.split()[0])"]),
            "packages": package_versions(python),
            "docker_server": _run(["docker", "version", "--format", "{{.Server.Version}}"]),
            "claude_cli": _run(["claude", "--version"]) if shutil.which("claude") else "",
        },
        "database": db,
        "engine": {"commit": engine_commit, "ref": engine_ref},
    }
