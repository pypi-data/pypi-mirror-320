#!/usr/bin/env python3
# Given a pyproject.toml convert it to a spack package.py

import logging
import argparse
from pathlib import Path

from pyproject2spack.parser.pyproject import PyProject
from pyproject2spack.matcher.spack import Spack
from pyproject2spack.renderer.jinja2 import Renderer
from pyproject2spack.logger.logger import ColorFormatter, FixedLineHandler


def main(args: argparse.Namespace) -> None:
    logging.info("running main function")

    prj = PyProject(giturl=args.gitlab_url)
    constraints = prj.dependencies()
    metadata = prj.metadata()

    matcher = Spack(constraints=constraints, dbpath=args.dbpath, updatedb=args.update_spackdb)
    matches = matcher.match()

    renderer = Renderer(matches=matches, metadata=metadata,
                        templates_dir=args.templates_dir,
                        template_name=args.template_name,
                        output=args.output)
    renderer.render()
    logging.info("finished!")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(prog="pyproject2spack",
                                         description="Convert pyproject.toml python package\
                                         to spack python package.",
                                         epilog="Square Kilometre Array Observatory (SKAO)")
    arg_parser.add_argument("--no-log", default=False, action="store_true",
                            help="wether to print log messages or not")
    arg_parser.add_argument("--log-max-lines", type=int, default=0,
                            help="number of fixed lines in the logger output, default is 0, the normal behaviour")
    arg_parser.add_argument("--log-delay", type=float, default=0.0,
                            help="the delay between log messages in seconds, default is 0")
    arg_parser.add_argument("--update-spackdb", default=False, action="store_true",
                            help="wether to update the spack json database file or not")
    arg_parser.add_argument("--gitlab-url", nargs='?', type=str, required=True,
                            help="URL of python project's gitlab repo")
    arg_parser.add_argument("--dbpath", nargs='?', default=Path("spackdb.json"),
                            type=Path, help="path to spack database json file")
    arg_parser.add_argument("--templates-dir", nargs='?', default=Path("templates/"),
                            type=Path, help="path to jinja2 templates dir")
    arg_parser.add_argument("--template-name", nargs='?', default="package.py.j2",
                            type=str, help="template name to be rendered")
    arg_parser.add_argument("--output", nargs='?', default="package.py",
                            type=str, help="rendered output file path")
    args = arg_parser.parse_args()

    log_fmt_str = "%(asctime)s%(name)s%(filename)s%(levelname)s%(message)s"
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if args.no_log:
        root_logger.setLevel(logging.ERROR)
    else:
        root_logger.setLevel(logging.DEBUG)

    handler = FixedLineHandler(max_lines=args.log_max_lines, delay=args.log_delay)
    handler.setFormatter(ColorFormatter(log_fmt_str))
    root_logger.addHandler(handler)

    main(args=args)
