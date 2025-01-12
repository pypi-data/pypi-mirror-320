# © Reuben Thomas <rrt@sc3d.org> 2024
# Released under the GPL version 3, or (at your option) any later version.

import argparse
import importlib.metadata
import os
import sys
import warnings

from .subcommand import init, publish, serve
from .warnings_util import simple_warning


VERSION = importlib.metadata.version("linton")


def main(argv: list[str] = sys.argv[1:]) -> None:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="Make a web site from Markdown files and other resources.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION} by Reuben Thomas <rrt@sc3d.org>",
    )
    warnings.showwarning = simple_warning(parser.prog)

    subparsers = parser.add_subparsers(required=True, title="subcommands", metavar="SUBCOMMAND")
    publish.add_subparser(subparsers)
    serve.add_subparser(subparsers)
    init.add_subparser(subparsers)

    args = parser.parse_args(argv)
    if "base_url" not in args:
        args.base_url = "/"

    args.func(args, dict(os.environ))
