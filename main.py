#!/usr/bin/env python3
"""Entry for the make.fun bounty "The joke about the demo"
(the-joke-about-the-demo-20261121-0551).

A program that writes one joke to /output/entry.txt: a one-line joke
about working beside AI coding agents, set at a live demo. The agent
nails the rehearsal, then crashes the app in front of fifty people —
and the punch is that the crash is the one piece of code it ever
wrote that behaved exactly like its human's.

Python 3.13, standard library only. No network access at runtime.
Deterministic: every run writes the same bytes.
"""

import hashlib
import os
import sys
import tempfile

# The joke, one line, plus a trailing newline: 155 characters,
# 157 bytes (the em-dash is 3 bytes in UTF-8).
JOKE = (
    "My AI coding agent demoed perfectly in rehearsal, "
    "then crashed live in front of fifty people — "
    "the only code it ever wrote that behaved exactly like mine."
)

# sha256 of the exact bytes written to /output/entry.txt.
# Measured 2026-11-21 ~13:20 WIB, two runs byte-identical (see NOTES.md).
EXPECTED_SHA256 = "89a317c670d7bf089c97c67ede34b21d9da485035011971b2c8613ebf9863806"

MIN_CHARS = 1
MAX_CHARS = 280
ON_SUBJECT_WORDS = ("ai", "agent")
# The judge's first criterion is a joke about a demo that crashed:
# the entry must be set at a demo and involve a crash.
DEMO_WORDS = ("demo", "rehearsal")
CRASH_WORDS = ("crash", "crashed")


def joke_text():
    """Assemble the joke: the single line, trailing newline."""
    return JOKE + "\n"


def validate_joke(text):
    """Check the joke against the bounty requirements."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        raise ValueError(
            f"joke is {len(text)} characters, must be {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        raise ValueError("joke must not be only whitespace")
    if text.count("\n") != 1 or not text.endswith("\n"):
        raise ValueError("joke must be exactly one line plus trailing newline")
    lowered = text.lower()
    if not all(word in lowered for word in ON_SUBJECT_WORDS):
        raise ValueError("joke must be about an AI coding agent")
    if not any(word in lowered for word in DEMO_WORDS):
        raise ValueError("joke must be set at a demo")
    if not any(word in lowered for word in CRASH_WORDS):
        raise ValueError("joke must involve a crash")
    text.encode("utf-8")  # raises if not valid UTF-8-encodable
    return text


def resolve_out_dir():
    """Output directory: $MAKEFUN_OUTPUT_DIR, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def write_entry(out_dir):
    """Write the joke to <out_dir>/entry.txt and return its path."""
    text = validate_joke(joke_text())
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def verify_written(path):
    """Read the entry back and check it byte-for-byte."""
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    if text != joke_text():
        raise ValueError("written entry differs from the joke")
    digest = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256 != "0" * 64 and digest != EXPECTED_SHA256:
        raise ValueError(f"sha256 mismatch: got {digest}")
    return digest


def run_once(out_dir):
    """One full run: write, verify, report. Returns the sha256."""
    path = write_entry(out_dir)
    digest = verify_written(path)
    text = joke_text()
    print(f"wrote {path}: {len(text)} chars, {len(text.encode('utf-8'))} bytes")
    print(f"sha256: {digest}")
    return digest


def self_test():
    """Run the pipeline twice into temp dirs; outputs must be identical."""
    digests = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp:
            digests.append(run_once(tmp))
    if digests[0] != digests[1]:
        raise ValueError(f"non-deterministic: {digests[0]} != {digests[1]}")
    print("self-test PASSED: two runs byte-identical")
    return True


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    try:
        run_once(resolve_out_dir())
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
