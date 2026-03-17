import os
import sys
from datetime import datetime

try:
    import colorama
    colorama.init()
except ImportError:
    pass

# ANSI escape codes
RESET   = "\033[0m"
BOLD    = "\033[1m"
REVERSE = "\033[7m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
GRAY    = "\033[90m"
RED     = "\033[31m"

CLEAR   = "\033[2J\033[H"
HIDE_C  = "\033[?25l"
SHOW_C  = "\033[?25h"


def getch():
    """Read one keypress and return a normalised key name or character."""
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {
                "\xe0H": "UP",
                "\xe0P": "DOWN",
                "\xe0G": "HOME",
                "\xe0O": "END",
                "\xe0S": "DEL",
            }.get(ch + ch2, "UNKNOWN")
        return ch
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                a = sys.stdin.read(1)
                b = sys.stdin.read(1)
                return {
                    "[A": "UP",
                    "[B": "DOWN",
                    "[H": "HOME",
                    "[F": "END",
                }.get(a + b, "UNKNOWN")
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def format_age(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        d = (datetime.now() - dt).days
        s = (datetime.now() - dt).seconds
        if d == 0:
            h = s // 3600
            return "just now" if h == 0 else f"{h}h ago"
        if d == 1:
            return "yesterday"
        if d < 7:
            return f"{d}d ago"
        if d < 14:
            return "1 week ago"
        if d < 30:
            return f"{d // 7} weeks ago"
        if d < 60:
            return "1 month ago"
        return f"{d // 30} months ago"
    except Exception:
        return ""


def trunc(path, width=56):
    return path if len(path) <= width else "…" + path[-(width - 1):]


def render(options, idx):
    rows = []
    rows.append(f"  {BOLD}{CYAN}claunch{RESET}{BOLD} — Claude Code Launcher{RESET}")
    rows.append("")

    for i, opt in enumerate(options):
        is_cur  = opt.get("is_current", False)
        exists  = os.path.isdir(opt["path"])
        age     = format_age(opt.get("last_used", ""))

        # Left badge
        if is_cur:
            badge = f"{GREEN}*{RESET} {YELLOW}[here]{RESET}"
            pad   = ""
        else:
            badge = f"{GRAY}{i}{RESET}      "
            pad   = ""

        path_col = RESET if exists else GRAY
        path_str = trunc(opt["path"])
        age_str  = f"  {GRAY}{age}{RESET}" if age else ""

        if not exists:
            path_str += f"  {RED}(missing){RESET}"

        line = f"    {badge}  {path_col}{path_str}{RESET}{age_str}"

        if i == idx:
            # Highlight selected row with a leading arrow
            line = "\033[K" + f"  {BOLD}{GREEN}▶{RESET} " + line.lstrip()
        else:
            line = "    " + line.lstrip()

        rows.append(line)

    rows.append("")
    rows.append(
        f"  {GRAY}↑↓ navigate   Enter select   1-9 jump   "
        f"c launch here   d delete   q quit{RESET}"
    )

    sys.stdout.write(CLEAR + HIDE_C + "\n".join(rows))
    sys.stdout.flush()


def pick_location(current_dir: str, saved_locations: list, db) -> str | None:
    """
    Show the interactive picker.
    Returns the chosen path, or None if the user quits.
    `db` is used to handle inline deletions.
    """
    # Build option list: current dir first (not duplicated below)
    options = [{"path": current_dir, "is_current": True}]
    for loc in saved_locations:
        if loc["path"] != current_dir:
            options.append(loc)

    selected = 0

    try:
        while True:
            render(options, selected)
            key = getch()

            # ── quit ──────────────────────────────────────────────
            if key in ("q", "Q", "\x03", "\x1b"):
                return None

            # ── confirm / select ──────────────────────────────────
            elif key in ("\r", "\n"):
                return options[selected]["path"]

            # ── launch in current dir immediately ─────────────────
            elif key in ("c", "C"):
                return current_dir

            # ── navigation ────────────────────────────────────────
            elif key == "UP":
                selected = max(0, selected - 1)
            elif key == "DOWN":
                selected = min(len(options) - 1, selected + 1)
            elif key == "HOME":
                selected = 0
            elif key == "END":
                selected = len(options) - 1

            # ── number jump (1-9 map to saved entries, not current) ──
            elif key.isdigit() and key != "0":
                n = int(key)
                if n < len(options):
                    return options[n]["path"]

            # ── delete a saved entry (not current dir) ────────────
            elif key in ("d", "D"):
                if selected > 0:
                    path_to_del = options[selected]["path"]
                    db.remove_location(path_to_del)
                    options.pop(selected)
                    if selected >= len(options):
                        selected = len(options) - 1

    finally:
        sys.stdout.write(SHOW_C + CLEAR)
        sys.stdout.flush()
