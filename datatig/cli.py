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
    build_parser.add_argument(
        "--frictionlessoutput", help="Location of Frictionless Data file Output"
    )

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("source")

    versionedbuild_parser = subparsers.add_parser("versionedbuild")
    versionedbuild_parser.add_argument("source")
    versionedbuild_parser.add_argument(
        "--sqliteoutput", help="Location of SQLite file Output"
    )
    versionedbuild_parser.add_argument(
        "--staticsiteoutput", help="Location of Static Site Output"
    )
    versionedbuild_parser.add_argument(
        "--staticsiteurl", help="URL for Static Site Output"
    )
    versionedbuild_parser.add_argument(
        "--refs", help="Refs to build, comma sep", default=""
    )
    versionedbuild_parser.add_argument(
        "--allbranches", help="Build all branches", action="store_true"
    )
    versionedbuild_parser.add_argument(
        "--defaultref", help="The Default ref.", default=""
    )

    versionedcheck_parser = subparsers.add_parser("versionedcheck")
    versionedcheck_parser.add_argument("source")
    versionedcheck_parser.add_argument("base_ref")
    versionedcheck_parser.add_argument("new_ref")
    versionedcheck_parser.add_argument(
        "--mode", choices=["new", "all_in_changed_records"], help="", default="new"
    )

    args = parser.parse_args()

    if args.subparser_name == "build":

        staticsite_output = args.staticsiteoutput
        sqlite_output = args.sqliteoutput
        frictionless_output = args.frictionlessoutput

        if not staticsite_output and not sqlite_output and not frictionless_output:
            print("You must specify one of the build options when running build.")
            exit(-1)

        datatig.process.go(
            args.source,
            staticsite_output=staticsite_output,
            staticsite_url=args.staticsiteurl,
            sqlite_output=sqlite_output,
            frictionless_output=frictionless_output,
            check_errors=True,
            check_record_errors=False,
            verbose=True,
            sys_exit_on_error=True,
        )

    elif args.subparser_name == "check":

        datatig.process.go(
            args.source,
            check_errors=True,
            check_record_errors=True,
            verbose=True,
            sys_exit_on_error=True,
        )

    elif args.subparser_name == "versionedbuild":

        staticsite_output = args.staticsiteoutput
        sqlite_output = args.sqliteoutput

        if not staticsite_output and not sqlite_output:
            print("You must specify one of the build options when running build.")
            exit(-1)

        datatig.process.versioned_build(
            args.source,
            staticsite_output=staticsite_output,
            staticsite_url=args.staticsiteurl,
            sqlite_output=sqlite_output,
            refs_str=args.refs,
            all_branches=args.allbranches,
            default_ref=args.defaultref,
        )

    elif args.subparser_name == "versionedcheck":

        datatig.process.versioned_build(
            args.source,
            refs=[args.base_ref, args.new_ref],
            default_ref=args.base_ref,
            check_errors_on_ref=args.new_ref,
            check_errors_on_ref_mode=args.mode,
            verbose=True,
            sys_exit_on_error=True,
        )


# DEPRECATED
# Executing the datatig module directly is now the official way to call the CLI,
# But the following code is left for backwards compatibility
if __name__ == "__main__":
    main()
