# SPDX-FileCopyrightText: 2024-present Robert Kormann <rokor@kormann.info>
#
# SPDX-License-Identifier: Unlicense
import sys

if __name__ == "__main__":
    from bankr.cli import bankr

    sys.exit(bankr())
