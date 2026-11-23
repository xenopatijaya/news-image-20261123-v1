#!/usr/bin/env python3
"""Entry point: copy the pre-rendered broadsheet to the output directory.

The image (entry.png, 1024x1024) was drawn in this repository by draw.py
during the build session, from facts verified live against their sources on
Monday 23 November 2026. This program does no drawing and needs no network:
it only copies the bundled image to $MAKEFUN_OUTPUT_DIR/entry.png, so two
runs always write the same bytes.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    sys.exit(main())
