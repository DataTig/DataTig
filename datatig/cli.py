import datatig.process
import argparse
import os


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subparser_name")

    build_parser = subparsers.add_parser('build')
    build_parser.add_argument('source')
    build_parser.add_argument("--staticsite", help="Location of Static Site")

    args = parser.parse_args()

    if args.subparser_name == 'build':

        if not args.staticsite:
            print("You must specify one of the build options when running build.")
            exit(-1)

        datatig.process.go(args.source, os.path.join(args.source, 'datatig.json'), args.staticsite)

if __name__ == "__main__":
    main()
