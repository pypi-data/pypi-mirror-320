#  _____             _        _____                            _
# /  __ \           | |      /  __ \                          | |
# | /  \/  ___    __| |  ___ | /  \/  __ _  _ __   ___  _   _ | |  ___
# | |     / _ \  / _` | / _ \| |     / _` || '_ \ / __|| | | || | / _ \
# | \__/\| (_) || (_| ||  __/| \__/\| (_| || |_) |\__ \| |_| || ||  __/
#  \____/ \___/  \__,_| \___| \____/ \__,_|| .__/ |___/ \__,_||_| \___|
#                                          | |
#                                          |_|

import argparse
import json
import sys

from .core import create_capsule, prepare_output_path
from .version import __version__


def main():
    parser = argparse.ArgumentParser(
        description="CodeCapsule is a powerful Python utility that transforms entire project directories into a single, portable JSON file. Perfect for sharing code with AI models, archiving projects, or creating compact code representations."
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s {0}".format(__version__),
        help="Show the program version and exit.",
    )

    # Positional argument for directory (default to current dir)
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Path to the directory you want to process (default: current directory).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="project_capsule.json",
        type=prepare_output_path,
        help="Path to the output JSON file. Can be absolute or relative path. "
        "If only a filename is provided, it will be saved in the current working directory. "
        "Automatically adds .json extension if not provided.",
        metavar="OUTPUT_FILE",
    )
    parser.add_argument(
        "--ignore",
        "-i",
        action="append",
        default=[],
        help='Additional patterns to ignore. Can be specified multiple times. Example: -i "*.log" -i "temp/"',
        metavar="PATTERN",
    )
    args = parser.parse_args()

    try:
        ignore_patterns = set(args.ignore)
        capsule = create_capsule(args.directory, ignore_patterns=ignore_patterns)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(capsule, f, indent=2, ensure_ascii=False)

        print(f"Project capsule successfully saved to: {args.output} ...")
    except IOError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Conversion error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
