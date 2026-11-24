"""Manage the scanner receiver in a workspace-specific tmux session."""

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

WORKSPACE = Path(sys.prefix).parent
STATE = WORKSPACE / ".local"
LOG = STATE / "receiver.log"
SESSION = "receiver"
TARGET = f"={SESSION}"


def tmux(*args, **kwargs):
    return subprocess.run(
        ["tmux", "-f", "/dev/null", "-S", str(STATE / "tmux.sock"), *args],
        text=True, **kwargs,
    )


def running():
    return tmux("has-session", "-t", TARGET, stderr=subprocess.DEVNULL).returncode == 0


def start():
    if running():
        print("FTP already running.")
        return
    for name in ("config.toml", "password"):
        if not (STATE / name).is_file():
            raise SystemExit(f"Missing {STATE / name}. See README.md.")
    command = shlex.join([sys.executable, "-I", "-m", "sharp_scan_ftp"])
    tmux("new-session", "-d", "-s", SESSION, "-c", str(WORKSPACE),
         f"exec {command} >> {shlex.quote(str(LOG))} 2>&1", check=True)
    for _ in range(50):
        pane = tmux("display-message", "-p", "-t", f"{SESSION}:", "#{pane_pid}", capture_output=True)
        if pane.returncode or not pane.stdout.strip():
            break
        listener = subprocess.run(
            ["lsof", "-nP", "-a", "-p", pane.stdout.strip(), "-iTCP", "-sTCP:LISTEN"],
            stdout=subprocess.DEVNULL,
        )
        if listener.returncode == 0:
            print("FTP started.")
            return
        time.sleep(0.1)
    raise SystemExit(f"Could not confirm startup. See {LOG}.")


def stop():
    if running():
        tmux("kill-session", "-t", TARGET, check=True)
    print("FTP stopped.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "stop", "restart", "status", "logs", "test"))
    args = parser.parse_args()
    os.umask(0o077)
    try:
        match args.command:
            case "start":
                start()
            case "stop":
                stop()
            case "restart":
                stop()
                start()
            case "status":
                print("FTP running." if running() else "FTP stopped.")
            case "logs":
                os.execlp("tail", "tail", "-n", "30", "-f", str(LOG))
            case "test":
                os.chdir(WORKSPACE)
                os.execv(sys.executable, [sys.executable, "-I", "-m", "sharp_scan_ftp", "--test"])
    except FileNotFoundError as error:
        parser.exit(1, f"Missing file or executable: {error.filename}\n")
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"{error.cmd[0]} exited with status {error.returncode}\n")
