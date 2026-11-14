#!/usr/bin/env python3
"""Build the ArduPilot Gazebo bridge against this project's Pixi Gazebo.

The source is checked out separately from the build. Set ARDUPILOT_GAZEBO_DIR
to use an existing clean checkout at the pinned revision, or let this script
fetch one into the project's ignored dependency cache.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REVISION = "f116b03552d05c8d0b0bed5ed67033a1183121d1"
SOURCE_URL = "https://github.com/ArduPilot/ardupilot_gazebo.git"


def run(*args: str, cwd: Path | None = None, env: dict | None = None) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def output(*args: str, cwd: Path) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def bridge_source() -> Path:
    selected = os.environ.get("ARDUPILOT_GAZEBO_DIR")
    path = Path(selected).expanduser().resolve() if selected else ROOT / ".pixi-deps/ardupilot_gazebo"
    if not path.exists():
        if selected:
            raise RuntimeError(f"ARDUPILOT_GAZEBO_DIR does not exist: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        # A failed or interrupted clone must not leave a broken cached source.
        # Only the temporary directory created here is cleaned up on failure.
        with tempfile.TemporaryDirectory(prefix=".bridge-clone-", dir=path.parent) as tmp:
            checkout = Path(tmp) / "source"
            run("git", "clone", "--no-checkout", SOURCE_URL, str(checkout))
            run("git", "checkout", "--detach", REVISION, cwd=checkout)
            checkout.rename(path)
    if not (path / "CMakeLists.txt").is_file():
        raise RuntimeError(f"Not an ArduPilot Gazebo source checkout: {path}")
    try:
        revision = output("git", "rev-parse", "HEAD", cwd=path)
        dirty = output("git", "status", "--porcelain", "--untracked-files=no", cwd=path)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Cannot inspect bridge checkout: {path}") from error
    if revision != REVISION:
        raise RuntimeError(f"Bridge checkout {path} is at {revision}; expected {REVISION}. It was not changed.")
    if dirty:
        raise RuntimeError(f"Bridge checkout has tracked changes: {path}. It was not changed.")
    return path


def prepare_build(source: Path) -> Path:
    """Reuse only a build directory known to belong to this source checkout."""
    build = ROOT / ".pixi-build/ardupilot_gazebo"
    build.mkdir(parents=True, exist_ok=True)
    marker = build / ".source.json"
    expected = {"source": str(source.resolve())}
    if marker.exists():
        try:
            existing = json.loads(marker.read_text())
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Cannot read bridge build source marker {marker}; it was not changed.") from error
        if not isinstance(existing, dict):
            raise RuntimeError(f"Invalid bridge build source marker {marker}; it was not changed.")
        if existing != expected:
            raise RuntimeError(
                f"{build} belongs to {existing.get('source')}; refusing to reuse it for {source}. "
                "Move the existing bridge build directory aside before switching checkouts."
            )
    else:
        cache = build / "CMakeCache.txt"
        if cache.is_file():
            entries = [line.split("=", 1)[1] for line in cache.read_text().splitlines()
                       if line.startswith("CMAKE_HOME_DIRECTORY:INTERNAL=")]
            if len(entries) != 1 or Path(entries[0]).resolve() != source.resolve():
                raise RuntimeError(
                    f"{build} contains a CMake build for a different or unknown source; "
                    "it was not changed. Move it aside before switching checkouts."
                )
        elif any(build.iterdir()):
            raise RuntimeError(f"{build} contains an unrecognised build; it was not changed.")
        marker.write_text(json.dumps(expected, indent=2) + "\n")

    # Also protect against an inconsistent marker / CMake cache pair.
    cache = build / "CMakeCache.txt"
    if cache.is_file():
        entries = [line.split("=", 1)[1] for line in cache.read_text().splitlines()
                   if line.startswith("CMAKE_HOME_DIRECTORY:INTERNAL=")]
        if len(entries) != 1 or Path(entries[0]).resolve() != source.resolve():
            raise RuntimeError(f"The CMake cache in {build} does not match {source}; it was not changed.")
    return build


def main() -> None:
    if sys.platform != "darwin" or os.uname().machine != "arm64":
        raise RuntimeError("This Pixi environment currently supports Apple Silicon macOS only.")
    prefix_string = os.environ.get("CONDA_PREFIX")
    if not prefix_string:
        raise RuntimeError("Run this script through 'pixi run bridge-build'.")
    prefix = Path(prefix_string).resolve()
    if not shutil.which("git") or not Path("/usr/bin/clang++").is_file():
        raise RuntimeError("Git and Xcode Command Line Tools are required; run xcode-select --install.")
    pkg_config = prefix / "bin/pkg-config.bin"
    if not pkg_config.is_file():
        raise RuntimeError(f"Pixi pkg-config binary was not found: {pkg_config}")
    source = bridge_source()
    build = prepare_build(source)
    env = os.environ.copy()
    env["GZ_VERSION"] = "harmonic"
    env["PKG_CONFIG_PATH"] = str(prefix / "lib/pkgconfig")
    run(
        str(prefix / "bin/cmake"), "-S", str(source), "-B", str(build), "-G", "Ninja",
        f"-DCMAKE_MAKE_PROGRAM={prefix / 'bin/ninja'}",
        f"-DCMAKE_PREFIX_PATH={prefix}",
        "-DCMAKE_C_COMPILER=/usr/bin/clang", "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
        f"-DPKG_CONFIG_EXECUTABLE={pkg_config}", "-DPKG_CONFIG_ARGN=--define-prefix",
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo", env=env,
    )
    run(str(prefix / "bin/cmake"), "--build", str(build), "--target", "ArduPilotPlugin", "--parallel", "3", env=env)
    print(f"Bridge built: {build / 'libArduPilotPlugin.dylib'}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(f"Bridge setup failed: {error}", file=sys.stderr)
        sys.exit(1)
