import argparse
import os

import datatig.process


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subparser_name")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("source")
    build_parser.add_argument(
        "--staticsiteoutput", help="Location of Static Site Output"
    )
    build_parser.add_argument("--sqliteoutput", help="Location of SQLite file Output")

    args = parser.parse_args()

    if args.subparser_name == "build":

        staticsite_output = args.staticsiteoutput
        sqlite_output = args.sqliteoutput

        if not staticsite_output and not sqlite_output:
            print("You must specify one of the build options when running build.")
            exit(-1)

        datatig.process.go(
            args.source,
            os.path.join(args.source, "datatig.json"),
            staticsite_output=staticsite_output,
            sqlite_output=sqlite_output,
        )


if __name__ == "__main__":
    main()
