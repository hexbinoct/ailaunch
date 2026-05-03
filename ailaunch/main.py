import os
import sys
import subprocess
from pathlib import Path

from .db import Database
from .ui import pick_location


def launch_claude(directory: str, extra_args: list = None):
    """Save the directory and launch claude in it."""
    extra_args = extra_args or []
    db = Database()
    db.save_location(directory)
    db.close()

    if sys.platform == "win32":
        cmd = " ".join(["claude"] + extra_args)
        subprocess.run(cmd, shell=True, cwd=directory)
    else:
        subprocess.run(["claude"] + extra_args, cwd=directory)


def main():
    # Everything after '--' is forwarded to claude
    extra_args = []
    if "--" in sys.argv:
        extra_args = sys.argv[sys.argv.index("--") + 1:]

    db = Database()
    current_dir = str(Path.cwd())
    saved = db.get_locations()

    chosen = pick_location(current_dir, saved, db)
    db.close()

    if chosen is None:
        sys.exit(0)

    if not os.path.isdir(chosen):
        print(f"Directory no longer exists: {chosen}")
        sys.exit(1)

    launch_claude(chosen, extra_args)


if __name__ == "__main__":
    main()
