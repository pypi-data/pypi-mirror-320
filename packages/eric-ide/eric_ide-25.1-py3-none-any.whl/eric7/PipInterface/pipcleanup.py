#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
pipcleanup utility script.

Script to delete all leftovers of upgrading packages currently in use. These
leftover directories are still located in the 'site-packages' directory and
their names start with a '~' character.
"""

import glob
import os
import shutil
import sys
import sysconfig


def main():
    """
    Function implementing the main logic.
    """
    sitepackages = sysconfig.get_path("platlib")
    leftovers = glob.glob("~*", root_dir=sitepackages)
    for leftover in leftovers:
        directory = os.path.join(sitepackages, leftover)
        print(f"Removing '{directory}'.")  # noqa: M801
        shutil.rmtree(directory, ignore_errors=True)

    # check again for leftovers and report via exit code
    leftovers = glob.glob("~*", root_dir=sitepackages)
    sys.exit(1 if bool(leftovers) else 0)


if __name__ == "__main__":
    main()
