"""Write one joke about a coding-agent demo to the entry file.

The program is deterministic: every run produces the same bytes.
It uses only the standard library and touches only the output file.
Run with --self-test to check the output twice in throwaway folders.
"""

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path


JOKE = (
    "My AI coding agent demoed perfectly in rehearsal, "
    "then crashed live in front of fifty people \u2014 "
    "the only code it ever wrote that behaved exactly like mine."
)

EXPECTED_SHA256 = (
    "89a317c670d7bf089c97c67ede34b21d9da485035011971b2c8613ebf9863806"
)

DEMO_MARKERS = ("demo", "demoed", "rehearsal")
CRASH_MARKERS = ("crash", "crashed")


def entry_bytes():
    """Return the exact bytes for the entry file."""
    return (JOKE + "\n").encode("utf-8")


def digest_hex(data):
    """Return the lowercase sha256 hex digest of data."""
    return hashlib.sha256(data).hexdigest()


def joke_covers_demo_and_crash(text):
    """Check the joke names both a demo and a crash.

    The judge wants a rehearsal/demo that goes wrong live, so the
    joke must carry a word from each side of that contrast.
    """
    lowered = text.lower()
    demo_found = any(word in lowered for word in DEMO_MARKERS)
    crash_found = any(word in lowered for word in CRASH_MARKERS)
    return demo_found and crash_found



def output_folder():
    """Pick the output folder from the environment, else /output."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if raw.strip():
        return Path(raw)
    return Path("/output")


def write_entry(folder):
    """Write the joke to entry.txt inside folder and return its path."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "entry.txt"
    target.write_bytes(entry_bytes())
    return target


def problems_in_file(path):
    """List anything wrong with a written entry file."""
    found = []
    data = path.read_bytes()
    if digest_hex(data) != EXPECTED_SHA256:
        found.append("sha256 mismatch")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        found.append("not valid utf-8")
        return found
    if text.count("\n") != 1 or not text.endswith("\n"):
        found.append("must be exactly one line plus a trailing newline")
    if len(text) != 155:
        found.append("must be 155 characters including the newline")
    if len(data) != 157:
        found.append("must be 157 bytes")
    if not joke_covers_demo_and_crash(text):
        found.append("joke must mention a demo/rehearsal and a crash")
    return found


def run_self_test():
    """Write the entry twice into fresh folders and compare them."""
    runs = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp_dir:
            runs.append(write_entry(Path(tmp_dir)).read_bytes())
    first_bytes, second_bytes = runs
    if first_bytes != second_bytes:
        print("self-test FAILED: two runs differ", file=sys.stderr)
        return 1
    if digest_hex(first_bytes) != EXPECTED_SHA256:
        print("self-test FAILED: sha256 mismatch", file=sys.stderr)
        print("got: " + digest_hex(first_bytes), file=sys.stderr)
        return 1
    print("self-test OK: two runs byte-identical")
    print("sha256: " + digest_hex(first_bytes))
    print("bytes: " + str(len(first_bytes)))
    return 0


def build_parser():
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Write the demo joke to the entry file."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="write twice to temp folders and check the result",
    )
    return parser


def main(argv=None):
    """Entry point: write the joke, or run the self-test."""
    args = build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not joke_covers_demo_and_crash(JOKE):
        print(
            "error: joke must mention a demo/rehearsal and a crash",
            file=sys.stderr,
        )
        return 2
    target = write_entry(output_folder())
    problems = problems_in_file(target)
    if problems:
        for item in problems:
            print("error: " + item, file=sys.stderr)
        return 1
    print("wrote " + str(target))
    print("sha256: " + digest_hex(entry_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
