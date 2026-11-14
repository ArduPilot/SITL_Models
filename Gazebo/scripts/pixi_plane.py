#!/usr/bin/env python3
"""Build ArduPlane SITL in this project's Pixi build directory.

An existing checkout can be selected with ARDUPILOT_DIR. Its source and
submodules are never updated by this helper; missing submodules are reported.
The default checkout is private to this project and pinned to a known revision.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / ".pixi-deps" / "ardupilot"
REVISION = "8f5f690771a1cef002fa71ec559fb86ab8091385"
URL = "https://github.com/ArduPilot/ardupilot.git"


def build_directory() -> Path:
    """Keep default and user-selected sources in separate build directories."""
    override = os.environ.get("ARDUPILOT_DIR")
    if override:
        source = Path(override).expanduser().resolve()
        if source != DEFAULT_SOURCE.resolve():
            key = hashlib.sha256(str(source).encode()).hexdigest()[:12]
            return ROOT / ".pixi-build" / f"ardupilot-{key}"
    return ROOT / ".pixi-build" / "ardupilot"


def run(command: list[str], cwd: Path | None = None, env: dict | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def checkout_default() -> Path:
    if DEFAULT_SOURCE.exists():
        if not (DEFAULT_SOURCE / ".git").exists():
            raise RuntimeError(f"{DEFAULT_SOURCE} exists but is not a Git checkout")
        revision = subprocess.check_output(
            ["git", "-C", str(DEFAULT_SOURCE), "rev-parse", "HEAD"], text=True
        ).strip()
        if revision != REVISION:
            raise RuntimeError(
                f"{DEFAULT_SOURCE} is at {revision}, expected {REVISION}; "
                "it has not been changed. Set ARDUPILOT_DIR to your checkout "
                "or move the existing project-local checkout aside."
            )
        dirty = subprocess.check_output(
            ["git", "-C", str(DEFAULT_SOURCE), "status", "--porcelain", "--untracked-files=no"],
            text=True,
        ).strip()
        if dirty:
            raise RuntimeError(f"Project ArduPilot checkout has tracked changes: {DEFAULT_SOURCE}; it was not changed")
        return DEFAULT_SOURCE

    DEFAULT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="ardupilot-clone-", dir=DEFAULT_SOURCE.parent))
    try:
        run(["git", "init", str(staging)])
        run(["git", "remote", "add", "origin", URL], cwd=staging)
        run(["git", "fetch", "--depth=1", "--filter=blob:none", "origin", REVISION], cwd=staging)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=staging)
        run(["git", "submodule", "update", "--init", "--recursive", "--depth=1", "--jobs=4"], cwd=staging)
        # Never replace a checkout that appeared while the clone was running.
        if DEFAULT_SOURCE.exists():
            raise RuntimeError(f"{DEFAULT_SOURCE} appeared during clone; it was not replaced")
        staging.rename(DEFAULT_SOURCE)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return DEFAULT_SOURCE


def main() -> int:
    override = os.environ.get("ARDUPILOT_DIR")
    source = Path(override).expanduser().resolve() if override else checkout_default().resolve()
    build = build_directory()
    if not (source / "waf").is_file():
        raise RuntimeError(f"ArduPilot checkout not found at {source}; set ARDUPILOT_DIR")
    if not (source / "modules/waf/waf-light").is_file():
        raise RuntimeError(
            f"ArduPilot waf submodule is missing in {source}. "
            "Initialize that checkout's required submodules before building; "
            "this helper does not change an existing checkout."
        )

    build.mkdir(parents=True, exist_ok=True)
    marker = build / ".source.json"
    fingerprint = {"source": str(source)}
    if marker.exists():
        try:
            existing = json.loads(marker.read_text())
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Cannot read build source marker {marker}; it was not changed") from error
        if not isinstance(existing, dict):
            raise RuntimeError(f"Invalid build source marker {marker}; it was not changed")
        if existing != fingerprint:
            raise RuntimeError(
                f"{build} belongs to {existing.get('source')}; refusing to reuse it "
                f"for {source}. Move that build directory aside first."
            )
    elif any(build.iterdir()):
        raise RuntimeError(f"{build} already contains an unrecognised build; it was not changed")
    else:
        marker.write_text(json.dumps(fingerprint, indent=2) + "\n")

    env = os.environ.copy()
    if sys.platform == "darwin":
        env.setdefault("CC", "/usr/bin/clang")
        env.setdefault("CXX", "/usr/bin/clang++")
    prefix = [sys.executable, str(source / "waf"), f"--out={build}"]
    run(prefix + ["configure", "--board", "sitl", "--no-submodule-update"], source, env)
    jobs = str(min(os.cpu_count() or 2, 4))
    run(prefix + ["plane", "-j", jobs], source, env)
    binary = build / "sitl/bin/arduplane"
    if not binary.is_file():
        raise RuntimeError(f"Build completed but {binary} was not created")
    print(f"ArduPlane SITL ready: {binary}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"plane-build: {exc}", file=sys.stderr)
        raise SystemExit(1)
