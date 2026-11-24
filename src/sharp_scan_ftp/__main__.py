import argparse
import os
import tomllib
from pathlib import Path

from .server import serve
from .upload_check import check_upload


def main():
    parser = argparse.ArgumentParser(description="Workspace FTP scan receiver")
    parser.add_argument("--test", action="store_true", help="verify a local FTP upload")
    args = parser.parse_args()
    os.umask(0o077)
    state = Path.cwd() / ".local"
    inbox = Path.cwd() / "scans"
    config = tomllib.loads((state / "config.toml").read_text())
    password = (state / "password").read_text().strip()
    if not password:
        parser.error("Set a password in .local/password")
    if args.test:
        check_upload(inbox, config, password)
    else:
        inbox.mkdir(mode=0o700, exist_ok=True)
        serve(inbox, config, password)


if __name__ == "__main__":
    main()
