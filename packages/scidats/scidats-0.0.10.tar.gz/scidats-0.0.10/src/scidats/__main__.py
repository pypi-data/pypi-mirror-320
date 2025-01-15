#!/usr/bin/env python3
# vim:fileencoding=utf-8
"""_____________________________________________________________________

:PROJECT: SciDatS

* Main module command line interface *

:details:  Main module command line interface. 
           !!! Warning: it should have a diffent name than the package name.

.. note:: -
.. todo:: - 
________________________________________________________________________
"""

"""Main module implementation. !!! Warning: it should have a diffent name than the package name. """
"""Console script for scidats."""

import argparse
import sys
import logging
from scidats import __version__

from scidats.scidats_impl import SciDatS

logging.basicConfig(
    format="%(levelname)-4s| %(module)s.%(funcName)s: %(message)s",
    level=logging.DEBUG,
)    

def parse_command_line():
    """ Looking for command line arguments"""

    description = "scidats"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("_", nargs="*")

    parser.add_argument("filename")

    parser.add_argument(
        "-m", "--metadata", action="store_true", help="print metadata"
    )

    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)

    # add more arguments here

    return parser.parse_args()

def main():
    """Console script for scidats."""
        # or use logging.INFO (=20) or logging.ERROR (=30) for less output
    logging.basicConfig(
        format='%(levelname)-4s| %(module)s.%(funcName)s: %(message)s', level=logging.DEBUG)
    
    
    args = parse_command_line()
        
    if len(sys.argv) <= 2:
        logging.debug("no arguments provided !")

    print("Arguments: ", args._)


    sd = SciDatS()
    sd.read_parquet(args.filename)

    if args.metadata:
        print(sd.metadata_jsonld)

    return 0


if __name__ == "__main__":

    sys.exit(main())  # pragma: no cover
