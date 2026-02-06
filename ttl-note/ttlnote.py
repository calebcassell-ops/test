#!/usr/bin/env python3
"""
ttl-note: Time-To-Live code annotations. TODO comments with teeth.

Attach expiration conditions to code notes — a date, a semver threshold,
or a dependency version — and surface expired ones as actionable warnings.
A dead man's switch for technical debt.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

NOTES_FILE = ".ttlnotes"
VERSION = "0.1.0"

# ─── Data Model ───────────────────────────────────────────────────────────────

def make_note(file_path, line, message, condition_type, condition_value, tag=None):
    return {
        "id": uuid.uuid4().hex[:8],
        "file": file_path,
        "line": line,
        "message": message,
        "condition": {
            "type": condition_type,     # "date" | "semver" | "dependency"
            "value": condition_value,
        },
        "tag": tag,
        "created": datetime.now(timezone.utc).isoformat(),
    }

# ─── Storage ──────────────────────────────────────────────────────────────────

def find_root():
    """Walk up to find the nearest directory containing .ttlnotes or .git."""
    current = Path.cwd()
    while True:
        if (current / NOTES_FILE).exists():
            return current
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            return Path.cwd()
        current = parent


def load_notes(root=None):
    root = root or find_root()
    path = root / NOTES_FILE
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("notes", [])


def save_notes(notes, root=None):
    root = root or find_root()
    path = root / NOTES_FILE
    with open(path, "w") as f:
        json.dump({"version": VERSION, "notes": notes}, f, indent=2)
        f.write("\n")

# ─── Condition Evaluation ─────────────────────────────────────────────────────

def parse_semver(v):
    """Parse a semver string like '1.2.3' into a tuple of ints."""
    v = v.lstrip("v")
    parts = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", v)
    if not parts:
        return None
    return tuple(int(x) if x else 0 for x in parts.groups())


def evaluate_condition(condition):
    """
    Returns (expired: bool, reason: str).
    """
    ctype = condition["type"]
    cvalue = condition["value"]

    if ctype == "date":
        try:
            deadline = datetime.fromisoformat(cvalue)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if now >= deadline:
                return True, f"expired on {cvalue}"
            days_left = (deadline - now).days
            return False, f"{days_left}d remaining"
        except ValueError:
            return False, f"unparseable date: {cvalue}"

    elif ctype == "semver":
        # value format: ">=2.0.0" — check against project version
        project_version = detect_project_version()
        if not project_version:
            return False, "project version not detected"
        match = re.match(r"^(>=|>|<=|<|==|!=)(.+)$", cvalue)
        if not match:
            return False, f"bad semver condition: {cvalue}"
        op, target_str = match.groups()
        target = parse_semver(target_str)
        current = parse_semver(project_version)
        if not target or not current:
            return False, "unparseable version"
        ops = {
            ">=": current >= target,
            ">":  current > target,
            "<=": current <= target,
            "<":  current < target,
            "==": current == target,
            "!=": current != target,
        }
        triggered = ops.get(op, False)
        if triggered:
            return True, f"project is v{project_version}, condition {cvalue} met"
        return False, f"project is v{project_version}, waiting for {cvalue}"

    elif ctype == "dependency":
        # value format: "package@>=2.0.0" or "package@removed"
        match = re.match(r"^(.+?)@(.+)$", cvalue)
        if not match:
            return False, f"bad dependency condition: {cvalue}"
        pkg, ver_cond = match.groups()
        installed = detect_dependency_version(pkg)
        if ver_cond == "removed":
            if installed is None:
                return True, f"'{pkg}' has been removed"
            return False, f"'{pkg}' still installed at v{installed}"
        if installed is None:
            return False, f"'{pkg}' not found"
        match2 = re.match(r"^(>=|>|<=|<|==|!=)(.+)$", ver_cond)
        if not match2:
            return False, f"bad version condition: {ver_cond}"
        op, target_str = match2.groups()
        target = parse_semver(target_str)
        current = parse_semver(installed)
        if not target or not current:
            return False, "unparseable version"
        ops = {
            ">=": current >= target,
            ">":  current > target,
            "<=": current <= target,
            "<":  current < target,
            "==": current == target,
            "!=": current != target,
        }
        triggered = ops.get(op, False)
        if triggered:
            return True, f"'{pkg}' is v{installed}, condition {ver_cond} met"
        return False, f"'{pkg}' is v{installed}, waiting for {ver_cond}"

    return False, f"unknown condition type: {ctype}"


def detect_project_version():
    """Try to read version from package.json, pyproject.toml, or Cargo.toml."""
    root = find_root()

    # package.json
    pjson = root / "package.json"
    if pjson.exists():
        try:
            with open(pjson) as f:
                return json.load(f).get("version")
        except (json.JSONDecodeError, OSError):
            pass

    # pyproject.toml (simple regex, avoids toml dependency)
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        try:
            text = pyproj.read_text()
            m = re.search(r'version\s*=\s*"([^"]+)"', text)
            if m:
                return m.group(1)
        except OSError:
            pass

    # Cargo.toml
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            text = cargo.read_text()
            m = re.search(r'version\s*=\s*"([^"]+)"', text)
            if m:
                return m.group(1)
        except OSError:
            pass

    return None


def detect_dependency_version(package):
    """Try to detect installed version of a dependency."""
    root = find_root()

    # Node: check node_modules
    pkg_json = root / "node_modules" / package / "package.json"
    if pkg_json.exists():
        try:
            with open(pkg_json) as f:
                return json.load(f).get("version")
        except (json.JSONDecodeError, OSError):
            pass

    # Python: try importlib.metadata
    try:
        from importlib.metadata import version as pkg_version
        return pkg_version(package)
    except Exception:
        pass

    return None

# ─── Display ──────────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
DIM = "\033[2m"
CYAN = "\033[36m"

def supports_color():
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def c(code, text):
    if supports_color():
        return f"{code}{text}{RESET}"
    return text


def format_note(note, expired, reason):
    status = c(RED, "EXPIRED") if expired else c(GREEN, "active")
    tag_val = note.get("tag", "")
    tag_str = f" {c(CYAN, '[' + tag_val + ']')}" if tag_val else ""
    line_num = note.get("line")
    location = f"{note['file']}:{line_num}" if line_num else note["file"]
    cond = note["condition"]
    cond_str = f"condition: {cond['type']}={cond['value']} — {reason}"
    return (
        f"  {c(BOLD, note['id'])} {status}{tag_str}\n"
        f"    {c(DIM, location)}\n"
        f"    {note['message']}\n"
        f"    {c(DIM, cond_str)}"
    )

# ─── CLI Commands ─────────────────────────────────────────────────────────────

def cmd_init(args):
    root = Path.cwd()
    path = root / NOTES_FILE
    if path.exists():
        print(f"{NOTES_FILE} already exists in {root}")
        return 0
    save_notes([], root)
    print(f"Initialized {NOTES_FILE} in {root}")

    # Add to .gitignore if not already there
    gitignore = root / ".gitignore"
    if gitignore.exists():
        text = gitignore.read_text()
        if NOTES_FILE not in text:
            with open(gitignore, "a") as f:
                f.write(f"\n# ttl-note annotations\n{NOTES_FILE}\n")
            print(f"Added {NOTES_FILE} to .gitignore")
    return 0


def cmd_add(args):
    ctype = "date"
    cvalue = args.expires

    if args.semver:
        ctype = "semver"
        cvalue = args.semver
    elif args.dependency:
        ctype = "dependency"
        cvalue = args.dependency

    note = make_note(
        file_path=args.file,
        line=args.line,
        message=args.message,
        condition_type=ctype,
        condition_value=cvalue,
        tag=args.tag,
    )

    notes = load_notes()
    notes.append(note)
    save_notes(notes)
    print(f"Added note {c(BOLD, note['id'])} on {note['file']}:{note['line'] or '-'}")
    return 0


def cmd_list(args):
    notes = load_notes()
    if not notes:
        print("No notes found.")
        return 0

    if args.tag:
        notes = [n for n in notes if n.get("tag") == args.tag]
    if args.file:
        notes = [n for n in notes if n["file"] == args.file]

    for note in notes:
        expired, reason = evaluate_condition(note["condition"])
        print(format_note(note, expired, reason))
        print()
    return 0


def cmd_check(args):
    notes = load_notes()
    if not notes:
        return 0

    expired_notes = []
    active_notes = []

    for note in notes:
        expired, reason = evaluate_condition(note["condition"])
        if expired:
            expired_notes.append((note, reason))
        else:
            active_notes.append((note, reason))

    if not expired_notes:
        if not args.quiet:
            print(c(GREEN, f"All clear. {len(active_notes)} note(s) still ticking."))
        return 0

    print(c(RED, f"\n  {len(expired_notes)} expired note(s) need attention:\n"))
    for note, reason in expired_notes:
        print(format_note(note, True, reason))
        print()

    if not args.quiet:
        print(c(DIM, f"  ({len(active_notes)} active note(s) remaining)\n"))

    return 1  # nonzero exit for CI integration


def cmd_remove(args):
    notes = load_notes()
    before = len(notes)
    notes = [n for n in notes if n["id"] != args.id]
    if len(notes) == before:
        print(f"No note with id '{args.id}' found.")
        return 1
    save_notes(notes)
    print(f"Removed note {args.id}.")
    return 0


def cmd_sweep(args):
    """Remove all expired notes at once."""
    notes = load_notes()
    kept = []
    removed = 0
    for note in notes:
        expired, _ = evaluate_condition(note["condition"])
        if expired:
            removed += 1
            if not args.quiet:
                print(f"  swept {c(BOLD, note['id'])}: {note['message']}")
        else:
            kept.append(note)
    save_notes(kept)
    print(f"\nSwept {removed} expired note(s). {len(kept)} remaining.")
    return 0


def cmd_scan(args):
    """Scan source files for inline ttl-note comments and auto-register them."""
    # Pattern: // ttl-note(<type>=<value>): <message>  [#tag]
    # Also supports # ttl-note(...) for Python/Ruby/shell
    pattern = re.compile(
        r'(?://|#)\s*ttl-note\((\w+)=([^)]+)\):\s*(.+?)(?:\s+\[#(\w+)\])?\s*$'
    )

    root = find_root()
    existing = load_notes()
    existing_locs = {(n["file"], n.get("line")) for n in existing}

    target = Path(args.path) if args.path else root
    if target.is_file():
        files = [target]
    else:
        files = sorted(target.rglob("*"))

    SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
    added = 0

    for fpath in files:
        if any(part in SKIP_DIRS for part in fpath.parts):
            continue
        if not fpath.is_file():
            continue
        try:
            text = fpath.read_text(errors="ignore")
        except OSError:
            continue

        for i, raw_line in enumerate(text.splitlines(), 1):
            m = pattern.search(raw_line)
            if not m:
                continue
            ctype, cvalue, message, tag = m.groups()
            rel = str(fpath.relative_to(root))
            if (rel, i) in existing_locs:
                continue
            note = make_note(rel, i, message.strip(), ctype, cvalue, tag)
            existing.append(note)
            existing_locs.add((rel, i))
            added += 1
            print(f"  found {c(BOLD, note['id'])} at {rel}:{i}")

    save_notes(existing)
    print(f"\nScanned and registered {added} new note(s).")
    return 0

# ─── Entrypoint ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="ttl-note",
        description="Time-To-Live code annotations. TODO comments with teeth.",
    )
    parser.add_argument("--version", action="version", version=f"ttl-note {VERSION}")
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize .ttlnotes in the current project")

    # add
    p_add = sub.add_parser("add", help="Add a new note")
    p_add.add_argument("file", help="File the note is about")
    p_add.add_argument("message", help="The annotation message")
    p_add.add_argument("-l", "--line", type=int, default=None, help="Line number")
    p_add.add_argument("-e", "--expires", help="Expiry date (ISO 8601, e.g. 2025-06-01)")
    p_add.add_argument("-s", "--semver", help="Semver condition (e.g. >=2.0.0)")
    p_add.add_argument("-d", "--dependency", help="Dependency condition (e.g. react@>=19.0.0)")
    p_add.add_argument("-t", "--tag", help="Optional tag for grouping")

    # list
    p_list = sub.add_parser("list", help="List all notes")
    p_list.add_argument("-t", "--tag", help="Filter by tag")
    p_list.add_argument("-f", "--file", help="Filter by file")

    # check
    p_check = sub.add_parser("check", help="Check for expired notes (exit 1 if any)")
    p_check.add_argument("-q", "--quiet", action="store_true", help="Suppress non-error output")

    # remove
    p_rm = sub.add_parser("remove", help="Remove a note by id")
    p_rm.add_argument("id", help="Note ID to remove")

    # sweep
    p_sweep = sub.add_parser("sweep", help="Remove all expired notes")
    p_sweep.add_argument("-q", "--quiet", action="store_true")

    # scan
    p_scan = sub.add_parser("scan", help="Scan source files for inline ttl-note comments")
    p_scan.add_argument("path", nargs="?", help="File or directory to scan (default: project root)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "list": cmd_list,
        "check": cmd_check,
        "remove": cmd_remove,
        "sweep": cmd_sweep,
        "scan": cmd_scan,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
