import argparse

import datatig.process


def main() -> None:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subparser_name")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("source")
    build_parser.add_argument(
        "--staticsiteoutput", help="Location of Static Site Output"
    )
    build_parser.add_argument("--staticsiteurl", help="URL for Static Site Output")
    build_parser.add_argument("--sqliteoutput", help="Location of SQLite file Output")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("source")

    args = parser.parse_args()

    if args.subparser_name == "build":

        staticsite_output = args.staticsiteoutput
        sqlite_output = args.sqliteoutput

        if not staticsite_output and not sqlite_output:
            print("You must specify one of the build options when running build.")
            exit(-1)

        datatig.process.go(
            args.source,
            staticsite_output=staticsite_output,
            staticsite_url=args.staticsiteurl,
            sqlite_output=sqlite_output,
            check_errors=True,
            check_record_errors=False,
            verbose=True,
            sys_exit=True,
        )

    elif args.subparser_name == "check":

        datatig.process.go(
            args.source,
            check_errors=True,
            check_record_errors=True,
            verbose=True,
            sys_exit=True,
        )


if __name__ == "__main__":
    main()
