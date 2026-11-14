#!/usr/bin/env python3
"""Run the uWSC runway and ArduPlane using this project's Pixi builds."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

from pixi_plane import build_directory


ROOT = Path(__file__).resolve().parents[1]


def prepend(env: dict[str, str], name: str, *paths: Path) -> None:
    values = [str(path) for path in paths]
    if env.get(name):
        values.append(env[name])
    env[name] = os.pathsep.join(values)


def stop(processes: list[subprocess.Popen]) -> None:
    previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        running = [p for p in processes if p.poll() is None]
        for process in running:
            try:
                process.send_signal(signal.SIGINT)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 5
        for process in running:
            try:
                process.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    finally:
        signal.signal(signal.SIGINT, previous)


def gui_config(prefix: Path, directory: Path) -> Path:
    source = prefix / "share/gz/gz-sim8/gui/gui.config"
    text = source.read_text()
    text, count = re.subn(
        r"<camera_pose>[^<]*</camera_pose>",
        "<camera_pose>12 -16 9 0 0.35 2.214</camera_pose>", text,
    )
    if count != 1:
        raise RuntimeError(f"Could not find a unique camera pose in {source}")
    result = directory / "gui.config"
    result.write_text(text)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true", help="omit the Gazebo GUI")
    parser.add_argument("--instance", type=int, default=0, help="isolated port offset (default: 0)")
    parser.add_argument("--run-dir", type=Path, help="new directory for runtime files and logs")
    parser.add_argument("--dry-run", action="store_true", help="write runtime files without launching")
    args = parser.parse_args()
    if not 0 <= args.instance <= 5000:
        parser.error("instance must be between 0 and 5000")
    prefix_string = os.environ.get("CONDA_PREFIX")
    if not prefix_string:
        raise RuntimeError("Run this through 'pixi run uwsc'.")
    prefix = Path(prefix_string)
    plugin = ROOT / ".pixi-build/ardupilot_gazebo"
    if not (plugin / "libArduPilotPlugin.dylib").is_file():
        raise RuntimeError("ArduPilot Gazebo plugin is missing; run 'pixi run setup'.")
    binary = build_directory() / "sitl/bin/arduplane"
    if not binary.is_file():
        raise RuntimeError("ArduPlane SITL is missing; run 'pixi run setup'.")
    bridge = Path(os.environ.get("ARDUPILOT_GAZEBO_DIR", ROOT / ".pixi-deps/ardupilot_gazebo")).expanduser().resolve()
    if not (bridge / "models/runway/model.sdf").is_file():
        raise RuntimeError("The bridge's runway model is missing; run 'pixi run setup'.")
    gz = shutil.which("gz")
    if not gz:
        raise RuntimeError("Gazebo is missing from the Pixi environment.")
    fdm_port, mavlink_port = 9002 + 10 * args.instance, 5760 + 10 * args.instance
    if not args.dry_run:
        for port in (fdm_port, mavlink_port):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test:
                test.bind(("127.0.0.1", port))
    if args.run_dir:
        directory = args.run_dir.expanduser().resolve()
        directory.mkdir(parents=True, exist_ok=False)
    else:
        directory = Path(tempfile.mkdtemp(prefix="uwsc-"))

    # A runtime model copy isolates the JSON port without changing source files.
    model = directory / "models/wsc_aircraft"
    shutil.copytree(ROOT / "models/wsc_aircraft", model)
    tree = ET.parse(model / "model.sdf")
    port = tree.getroot().find("./model/plugin[@name='ArduPilotPlugin']/fdm_port_in")
    if port is None:
        raise RuntimeError("uWSC ArduPilotPlugin FDM port was not found")
    port.text = str(fdm_port)
    tree.write(model / "model.sdf", encoding="unicode")
    world = ET.parse(ROOT / "worlds/wsc_aircraft_runway.sdf")
    world.find("./world/physics/real_time_factor").text = "1.0"
    world_file = directory / "runway.sdf"
    world.write(world_file, encoding="unicode")
    state = directory / "sitl"
    state.mkdir()
    env = os.environ.copy()
    env.update(GZ_VERSION="harmonic", GZ_IP="127.0.0.1", IGN_IP="127.0.0.1",
               GZ_PARTITION=f"uwsc_{os.getpid()}", GZ_CONFIG_PATH=str(prefix / "share/gz"),
               OGRE2_RESOURCE_PATH=str(prefix / "lib/OGRE-Next"))
    env["IGN_PARTITION"] = env["GZ_PARTITION"]
    prepend(env, "GZ_SIM_SYSTEM_PLUGIN_PATH", plugin)
    prepend(env, "GZ_SIM_RESOURCE_PATH", directory / "models", ROOT / "models", ROOT / "worlds",
            bridge / "models", bridge / "worlds")
    commands = [[gz, "sim", "-s", "-r", "-v3", str(world_file)]]
    if not args.headless:
        commands.append([gz, "sim", "-g", "-v3", "--gui-config", str(gui_config(prefix, directory))])
    commands.append([
        str(binary), "-w", "--model", "JSON", "--speedup", "1", f"-I{args.instance}",
        "--home", "37.523648,-122.255122,584,0", "--defaults", str(ROOT / "config/wsc_aircraft.param"),
        "--sim-address", "127.0.0.1", "--serial0", f"udpclient:127.0.0.1:{mavlink_port}",
    ])
    (directory / "launch.json").write_text(json.dumps({
        "commands": commands, "partition": env["GZ_PARTITION"],
        "fdm_port": fdm_port, "mavlink_udp_port": mavlink_port,
    }, indent=2) + "\n")
    print(f"Runtime and logs: {directory}", flush=True)
    print(f"Connect MAVProxy to UDP {mavlink_port}; instance 0 uses 'pixi run mavproxy'.", flush=True)
    if args.dry_run:
        for command in commands:
            print(command)
        return 0
    processes, logs = [], []
    try:
        for command in commands:
            name = "arduplane.log" if command[0] == str(binary) else ("gui.log" if "-g" in command else "gazebo.log")
            log = (directory / name).open("w")
            logs.append(log)
            processes.append(subprocess.Popen(command, cwd=state if name == "arduplane.log" else directory,
                                              env=env, stdout=log, stderr=subprocess.STDOUT))
        print("Press Ctrl-C to stop the simulation.", flush=True)
        while True:
            for process in processes:
                if process.poll() is not None:
                    if process.returncode == 0:
                        return 0
                    raise RuntimeError(f"Simulation process exited with status {process.returncode}; see {directory}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        return 0
    finally:
        stop(processes)
        for log in logs:
            log.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"uwsc: {error}", file=sys.stderr)
        raise SystemExit(1)
