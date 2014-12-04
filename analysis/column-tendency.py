"""
Reads in a pitcher data file and visualizes a particular
column over time (pitches).

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

from collections import Counter

import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


def run(filename, column_name, pitches_per_window, out_dir):
    """
    Loads in the pitcher data and visualizes the column.
    """

    # Read in the dataframe.
    df = pd.read_csv(filename)

    # Determine all the possible distinct types in the column.
    column_types = df[column_name] \
                    .value_counts().reset_index()['index'].tolist()

    # Initialize the dictionary that keeps track of the average
    #  occurrences for a particular column value per sliding window.
    type_avgs = dict.fromkeys(column_types, None)
    for k, v in type_avgs.items():
        type_avgs[k] = []

    # Calculate the total occurrences of a type
    # per sliding window per game for a pitchers entire career.
    type_by_range = {}
    for gid, gid_group in df.groupby('gid'):
        # Find the total number of pitches for this game.
        num_pitches = gid_group.shape[0]

        # Evaluate the pitches in a sliding window (pitches_per_group).
        i = pitches_per_window
        while (i < num_pitches):
            # Gather the pitches in this sliding range.
            pitches = gid_group.iloc[i - pitches_per_window:i]
            # Determine the counts per pitch type.
            type_counts = Counter(
                dict(pitches[column_name].value_counts())
            )

            # Add the counts to a dictionary for the current range (window).
            if (not i in type_by_range):
                type_by_range[i] = [type_counts]
            else:
                type_by_range[i].append(type_counts)

            # Increment the sliding range.
            i += pitches_per_window

    # For each sliding window, determine the average per type.
    for pitch_window, type_counts in iter(sorted(type_by_range.iteritems())):
        type_counts_total = Counter()
        # Add up the pitch counts for the current window.
        for type_count in type_counts:
            type_counts_total += type_count

        # Convert back into a dictionary to calculate averages.
        for k, v in dict(type_counts_total).iteritems():
            type_avgs[k].append(float(v) / len(type_counts))

    # Find the pitch that occurred in the most amount of sliding windows
    #  per game and extend all the other pitches so they are the same size
    #  This is done so the visualization generates properly.
    max_windows = 0
    for k, v in type_avgs.iteritems():
        max_windows = max(max_windows, len(v))
    for k, v in type_avgs.items():
        v.extend([0.0] * (max_windows - len(v)))

    ind = np.arange(max_windows)
    width = 0.15

    # Visualize each pitch type individually so we can see how
    #  the pitch type occurrences change over time (number of pitches)
    i = 0
    for column_type, type_counts in type_avgs.iteritems():
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        ax.bar(ind, type_counts)
        ax.set_xticks(ind)
        ax.set_xticklabels(
            [str(i * pitches_per_window) + "-" + str((i + 1) * pitches_per_window) \
            for i in xrange(max_windows)]
        )
        ax.set_title(
            "\"" + str(column_type) + "\"" + \
            " Over Time for Column " + column_name)
        ax.set_xlabel("Pitch Range")
        ax.set_ylabel("Number of Occurrences")

        fig.savefig(
            os.path.join(
                out_dir,
                str(int(df['pitcher_id'][0])) + "-" + column_name + "-" + \
                str(column_type) + "-n" + str(pitches_per_window) + ".png"
            )
        )
        i += 1


def main():
    """Main execution."""

    # Determine command line arguments.
    try:
        rawopts, _ = getopt.getopt(sys.argv[1:], 'i:c:n:o:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    opts = {}

    # Process each command line argument.
    for o, a in rawopts:
        opts[o[1]] = a

    # The following arguments are required in all cases.
    for opt in ['i', 'c', 'n', 'o']:
        if not opt in opts:
            usage()
            sys.exit(2)

    run(opts['i'], opts['c'], int(opts['n']), opts['o'])


def usage():
    """Prints the usage of the program."""

    print("\n" +
    "The following are arguments required:\n" +
    "\t-i: the input pitcher (csv) file.\n" +
    "\t-r: the number of pitches per pitch window (e.g. 10 for 0-10, 10-20, ...).\n" +
    "\t-o: the output directory.\n" +
    "\n" +
    "Example Usage:\n" +
    "\tpython pitch-tendency.py -i \"./data.csv\"\n" +
    "\n")


"""Main execution."""
if __name__ == "__main__":
    main()
