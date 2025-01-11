import argparse
from pathlib import Path

from . import build_header


def main():
    parser = argparse.ArgumentParser(description="Input headers")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="the directory where output files will be saved",
    )
    parser.add_argument(
        "files", metavar="F", type=str, nargs="+", help="a file to be processed"
    )
    args = parser.parse_args()

    for file_path in args.files:
        with open(file_path, "r") as f:
            path = Path(file_path)
            source_code = f.read()
            code = build_header(path.stem, source_code)

            output_file = Path(args.output.strip()) / f"bind_{path.stem}.h"

            with open(output_file, "w") as f:
                f.write(code)


if __name__ == "__main__":
    main()
