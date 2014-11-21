"""
Takes data from brooksbaseball and sorts the data (html) files
in the respective pitcher folder.

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

    # Use a reg expression to find the PID which is in the file name.
    regex = re.compile("pid_(?P<pid>\d*?)\.html|$")
    for root, dirs, files in os.walk(opts['i']):
        for file in files:
            r = regex.search(file)
            pid = r.groups()[0]
            # Make sure we can find the PID in the file name.
            if pid:
                # Copy the file over to the PID's folder.
                outdir = os.path.join(opts['o'], pid)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)

                shutil.copyfile(
                    os.path.join(root, file),
                    os.path.join(outdir, file))


def usage():
    """Prints the usage of the program."""

    print("\n" +
    "The following are arguments required:\n" +
    "\t-i: the input directory.\n" +
    "\t-o: the output directory.\n" +
    "\n" +
    "Example Usage:\n" +
    "\tpython filter.py -i \"./data\" -o \"./pitchers\"\n" +
    "\n")


"""Main execution."""
if __name__ == "__main__":
    main()
