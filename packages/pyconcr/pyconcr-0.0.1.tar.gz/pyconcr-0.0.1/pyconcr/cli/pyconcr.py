"""Console script for pyconcr."""

import argparse
import sys


def main():
    """Console script for pyconcr."""
    parser = argparse.ArgumentParser()
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()

    str0 = "🚀🚀🚀 Replace this message by putting your code into pyconcr.cli.pyconcr:main"

    print("Arguments: " + str(args._))
    print(str0)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
