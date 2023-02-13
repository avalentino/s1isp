"""Sentinel-1 Instrument Souce Packets decoder Coommans Line Intervace."""

import sys
import logging
import pathlib
import argparse
from typing import Optional

from . import __version__
from .decoder import decode_stream

import pandas as pd

try:
    from os import EX_OK
except ImportError:
    EX_OK = 0
EX_FAILURE = 1
EX_INTERRUPT = 130

PROG = __package__
LOGFMT = "%(asctime)s %(levelname)-8s -- %(message)s"
DEFAULT_LOGLEVEL = "INFO"


def dump_metadata(
    filename,
    outfile: Optional[str] = None,
    skip: Optional[int] = None,
    maxcount: Optional[int] = None,
    bytes_offset: int = 0,
    enum_value: bool = False,
    force: bool = False,
):
    """Dump content od primary and secondary headers into an XLSX file."""
    if outfile is None:
        outfile = pathlib.Path(filename).stem + ".xlsx"

    if not force and pathlib.Path(outfile).exists():
        raise FileExistsError(f"File already exists: {outfile}")

    records = decode_stream(
        filename,
        skip=skip,
        maxcount=maxcount,
        bytes_offset=bytes_offset,
        enum_value=enum_value,
    )
    df = pd.DataFrame(records)

    log = logging.getLogger(__name__)
    log.info("Writing metadata ...")
    df.to_excel(outfile)
    log.info("Metadata written to %s", outfile)


def _autocomplete(parser: argparse.ArgumentParser):
    try:
        import argcomplete
    except ImportError:
        pass
    else:
        argcomplete.autocomplete(parser)


def _add_logging_control_args(
    parser: argparse.ArgumentParser, default_loglevel: str = DEFAULT_LOGLEVEL,
):
    """Add command line options for logging control."""
    loglevels = [logging.getLevelName(level) for level in range(10, 60, 10)]

    parser.add_argument(
        "--loglevel",
        default=default_loglevel,
        choices=loglevels,
        help="logging level (default: %(default)s)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="loglevel",
        action="store_const",
        const="ERROR",
        help="suppress standard output messages, "
        "only errors are printed to screen",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        action="store_const",
        const="INFO",
        help="print verbose output messages",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="loglevel",
        action="store_const",
        const="DEBUG",
        help="print debug messages",
    )


def get_parser(subparsers=None) -> argparse.ArgumentParser:
    """Instantiate the command line argument (sub-)parser."""
    name = PROG
    synopsis = __doc__.splitlines()[0]
    doc = __doc__

    if subparsers is None:
        parser = argparse.ArgumentParser(prog=name, description=doc)
        parser.add_argument(
            "--version", action="version", version="%(prog)s v" + __version__
        )
    else:
        parser = subparsers.add_parser(name, description=doc, help=synopsis)
        # parser.set_defaults(func=info)

    _add_logging_control_args(parser)

    # Command line options
    parser.add_argument(
        "-o",
        "--outfile",
        help="output file name for metadata (XLSX format)",
    )
    parser.add_argument(
        "--skip",
        type=int,
        help="number of ISPs to skip at the beginning of the file",
    )
    parser.add_argument(
        "--maxcount",
        type=int,
        help="number of ISPs to dump",
    )
    parser.add_argument(
        "--bytes_offset",
        type=int,
        help="number bytes to skip at the beginning of the file",
    )
    parser.add_argument(
        "--enum-value",
        action='store_true',
        default=False,
        help="dump the enum numeric value instead of the symbolic name",
    )
    parser.add_argument(
        "-f",
        "--force",
        action='store_true',
        default=False,
        help="overwtire the output file if it already exists",
    )

    # Positional arguments
    parser.add_argument("filename", help="RAW data file name")

    # Sub-command management
    # if subparsers is None:
    #     sp = parser.add_subparsers(
    #         title="sub-commands", metavar=""
    #     )  # dest="func"
    #     get_subcommand_parser(sp)
    #     # ...

    if subparsers is None:
        _autocomplete(parser)

    return parser


def parse_args(args=None, namespace=None, parser=None):
    """Parse command line arguments."""
    if parser is None:
        parser = get_parser()

    args = parser.parse_args(args, namespace)

    # Common pre-processing of parsed arguments and consistency checks
    # ...

    # if getattr(args, "func", None) is None:
    #     parser.error("no sub-command specified.")

    return args


def main(*argv):
    """Implement the main CLI interface."""
    # setup logging
    logging.basicConfig(format=LOGFMT, level=DEFAULT_LOGLEVEL)
    logging.captureWarnings(True)
    log = logging.getLogger(__name__)

    # parse cmd line arguments
    args = parse_args(argv if argv else None)

    # execute main tasks
    exit_code = EX_OK
    try:
        log.setLevel(args.loglevel)

        log.debug("args: %s", args)

        dump_metadata(
            args.filename,
            args.outfile,
            skip=args.skip,
            maxcount=args.maxcount,
            bytes_offset=args.bytes_offset,
            enum_value=args.enum_value,
            force=args.force,
        )
    except Exception as exc:  # noqa: B902
        log.critical(
            "unexpected exception caught: {!r} {}".format(
                type(exc).__name__, exc
            )
        )
        log.debug("stacktrace:", exc_info=True)
        exit_code = EX_FAILURE
    except KeyboardInterrupt:
        log.warning("Keyboard interrupt received: exit the program")
        exit_code = EX_INTERRUPT

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
