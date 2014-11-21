"""
Takes the html files from brooksbaseball and compresses
all the games for one pitcher into a single csv.

The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampaglione@g.harvard.edu>
@author Fil Piasevoli <fpiasevoli@g.harvard.edu>
@author Lyla Fadden <lylafadden@g.harvard.edu>

@requires Python >=2.7
@copyright 2014
"""
import getopt
import os
import re
import shutil
import sys

import pandas as pd


def main():
    """Main execution."""

    # Determine command line arguments.
    try:
        rawopts, _ = getopt.getopt(sys.argv[1:], 'i:o:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    opts = {}

    # Process each command line argument.
    for o, a in rawopts:
        opts[o[1]] = a

    # The following arguments are required in all cases.
    for opt in ['i', 'o']:
        if not opt in opts:
            usage()
            sys.exit(2)

    # Make sure the output directory exists.
    if not os.path.exists(opts['o']):
        os.makedirs(opts['o'])

    # Traverse the root folder that contains sub folders
    #  that represent each pitcher.
    for root, dirs, _ in os.walk(opts['i']):
        # Traverse each folder in the root.
        for pid in dirs:
            outfile = os.path.join(opts['o'], pid + ".csv")

            # Check if this pitcher was already processed.
            if os.path.isfile(outfile):
                continue

            for proot, _, files in os.walk(os.path.join(root, pid)):
                try:
                    # Read in the first game for this pitcher.
                    with open(os.path.join(proot, files[0]), 'r') as f:
                        df = pd.read_html(f.read(), header=0)[0]
                    # Read in the subsequent games and append to the
                    #  running DataFrame.
                    for file in files[1:]:
                        with open(os.path.join(proot, file), 'r') as f:
                            df = df.append(pd.read_html(f.read(), header=0)[0])
                    # Save to disk as a csv file.
                    df.to_csv(outfile)
                except ValueError:
                    print("Error processing " + pid)
                    continue


def usage():
    """Prints the usage of the program."""

    print("\n" +
    "The following are arguments required:\n" +
    "\t-i: the input directory.\n" +
    "\t-o: the output directory.\n" +
    "\n" +
    "Example Usage:\n" +
    "\tpython compress.py -i \"./pitchers\" -o \"./pitchers-compressed\"\n" +
    "\n")


"""Main execution."""
if __name__ == "__main__":
    main()
