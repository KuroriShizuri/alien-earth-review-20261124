#!/usr/bin/env python3
"""Alien Field Notes: The Two Day Earth Review.

Writes one original line -- an alien tourist's review of planet Earth --
to /output/entry.txt (or a path given with --output).

Usage:
    python3 main.py                 # writes /output/entry.txt
    python3 main.py --output PATH   # writes PATH instead
    python3 main.py --check         # write, then verify the file
    python3 main.py --self-test     # run the built-in self-test
"""

import argparse
import sys

ENTRY = (
    "Earth: gorgeous views, confusing customs. "
    "They drink bean water to wake up, then complain about being awake. "
    "Lost my ship to a parking meter. 4/5."
)

MIN_CHARS = 1
MAX_CHARS = 200


def entry_bytes() -> bytes:
    """The entry as its exact UTF-8 bytes (what the gate measures)."""
    return ENTRY.encode("utf-8")


def validate_entry() -> None:
    """Fail loudly if the entry ever breaks the gate (cap / whitespace)."""
    if not MIN_CHARS <= len(ENTRY) <= MAX_CHARS:
        raise ValueError(
            f"ENTRY is {len(ENTRY)} chars, outside {MIN_CHARS}-{MAX_CHARS}")
    if not ENTRY.strip():
        raise ValueError("ENTRY is only whitespace")
    if ENTRY != ENTRY.strip():
        raise ValueError("ENTRY has leading/trailing whitespace")


def write_entry(path: str) -> str:
    """Write the entry text to *path* and return it.

    Validates the cap first, then proves the round trip: the bytes read
    back must be byte-identical to entry_bytes().
    """
    validate_entry()
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(ENTRY)
    with open(path, "rb") as f:
        written = f.read()
    if written != entry_bytes():
        raise ValueError("round-trip mismatch: file bytes != entry bytes")
    return ENTRY


def check(path: str) -> bool:
    """Verify the file at *path* holds the entry and is within the cap."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw != entry_bytes():
        print("FAIL: file bytes differ from entry_bytes()", file=sys.stderr)
        return False
    text = raw.decode("utf-8")
    if text != ENTRY:
        print(f"FAIL: file content differs from ENTRY", file=sys.stderr)
        return False
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        print(f"FAIL: {len(text)} chars, outside {MIN_CHARS}-{MAX_CHARS}",
              file=sys.stderr)
        return False
    if not text.strip():
        print("FAIL: entry is only whitespace", file=sys.stderr)
        return False
    print(f"OK: {len(text)} chars, within {MIN_CHARS}-{MAX_CHARS}")
    return True


def self_test() -> bool:
    """Self-test: write to a temp file, check it, and confirm the cap."""
    global ENTRY
    import tempfile
    import os

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "entry.txt")
        write_entry(path)
        if not check(path):
            ok = False
    if not (MIN_CHARS <= len(ENTRY) <= MAX_CHARS):
        print(f"FAIL: ENTRY is {len(ENTRY)} chars", file=sys.stderr)
        ok = False
    # Byte-level round trip: entry_bytes() must decode back to ENTRY.
    if entry_bytes().decode("utf-8") != ENTRY:
        print("FAIL: entry_bytes() does not round-trip", file=sys.stderr)
        ok = False
    # Cap guard must fire on an over-long entry (tested via monkeypatch).
    saved = ENTRY
    try:
        ENTRY = "x" * (MAX_CHARS + 1)
        try:
            validate_entry()
            print("FAIL: validate_entry accepted an over-cap entry",
                  file=sys.stderr)
            ok = False
        except ValueError:
            pass  # expected
    finally:
        ENTRY = saved
    print("self-test:", "PASS" if ok else "FAIL")
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="/output/entry.txt",
                        help="where to write the entry (default: /output/entry.txt)")
    parser.add_argument("--check", action="store_true",
                        help="verify the written file afterwards")
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in self-test and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        return 0 if self_test() else 1

    write_entry(args.output)
    if args.check:
        return 0 if check(args.output) else 1
    print(f"wrote {len(ENTRY)} chars to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
