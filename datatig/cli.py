import datatig.process
import argparse
import os


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="subparser_name")

    foo_parser = subparsers.add_parser('build')
    foo_parser.add_argument('source')
    foo_parser.add_argument('destination')

    args = parser.parse_args()

    if args.subparser_name == 'build':

        datatig.process.go(args.source, os.path.join(args.source, 'datatig.json'), args.destination)

if __name__ == "__main__":
    main()
