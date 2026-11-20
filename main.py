#!/usr/bin/env python3
"""news-image-20261120 v2: publish the day's front page to /output/entry.png.

The picture itself is a fixed asset shipped in this repository (entry.png):
a split-screen front page for Friday 20 November 2026 led by the first-ever
Trump-Xi-Putin summit in Shenzhen ("WE ARE REALLY MAKING HISTORY"), with the
other five stories of the day as photo rows. This program only copies that
asset into the output directory, after checking it is a whole PNG or JPEG
inside the competition's size limit. Pure standard library, no network, no
clock, no randomness: two runs write identical bytes.
"""

import hashlib
import os
import sys

SIZE_LIMIT = 1048576  # 1 MiB
KINDS = {
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"\xff\xd8\xff": "JPEG",
}


def die(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def sniff(data):
    for magic, kind in KINDS.items():
        if data[: len(magic)] == magic:
            return kind
    return None


def run():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(source):
        die(f"entry image missing: {source}")

    with open(source, "rb") as handle:
        data = handle.read()

    kind = sniff(data)
    if kind is None:
        die("entry image is neither PNG nor JPEG (bad magic bytes)")
    if len(data) > SIZE_LIMIT:
        die(f"entry image is {len(data)} bytes, over the {SIZE_LIMIT} byte limit")

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())

    with open(target, "rb") as handle:
        written = handle.read()
    if len(written) != len(data):
        die("copy verification failed: output size differs from source")
    if written != data:
        die("copy verification failed: output bytes differ from source")
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(data).hexdigest():
        die("copy verification failed: output digest differs from source")

    digest = hashlib.sha256(written).hexdigest()
    print(f"wrote {target} ({kind}, {len(written)} bytes, sha256 {digest})")


if __name__ == "__main__":
    run()
