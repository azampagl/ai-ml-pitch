"""
Reads in a pitcher data file and visualizes the pitches
over the course of a game.

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


def run(filename, pitches_per_window, out_dir):
    """
    Loads in the pitcher data and visualizes pitches.
    """

    # Read in the dataframe.
    df = pd.read_csv(filename)

    # Determine the pitch types
    pitch_types = df['mlbam_pitch_name'] \
                    .value_counts().reset_index()['index'].tolist()

    # Initialize the dictionary that keeps track of the average
    #  pitches per sliding window for a particular pitch.
    pitches_by_type = dict.fromkeys(pitch_types, None)
    for k, v in pitches_by_type.items():
        pitches_by_type[k] = []

    # Calculate the total pitches per sliding window for a pitchers
    #  entire career.
    pitches_by_range = {}
    for gid, gid_group in df.groupby('gid'):
        # Find the total number of pitches for this game.
        num_pitches = gid_group.shape[0]

        # Evaluate the pitches in a sliding window (pitches_per_group).
        i = pitches_per_window
        while (i < num_pitches):
            # Gather the pitches in this sliding range.
            pitches = gid_group.iloc[i - pitches_per_window:i]
            # Determine the counts per pitch type.
            pitch_counts = Counter(
                dict(pitches['mlbam_pitch_name'].value_counts())
            )

            # Add the counts to a dictionary for the current range (window).
            if (not i in pitches_by_range):
                pitches_by_range[i] = [pitch_counts]
            else:
                pitches_by_range[i].append(pitch_counts)

            # Increment the sliding range.
            i += pitches_per_window

    # For each sliding window, determine the average pitches per
    #  pitch type.
    for pitch_window, pitch_counts in iter(sorted(pitches_by_range.iteritems())):
        pitch_counts_total = Counter()
        # Add up the pitch counts for the current window.
        for pitch_count in pitch_counts:
            pitch_counts_total += pitch_count

        # Convert back into a dictionary to calculate averages.
        for k, v in dict(pitch_counts_total).iteritems():
            pitches_by_type[k].append(float(v) / len(pitch_counts))

    # Find the pitch that occurred in the most amount of sliding windows
    #  per game and extend all the other pitches so they are the same size
    #  This is done so the visualization generates properly.
    max_windows = 0
    for k, v in pitches_by_type.iteritems():
        #print len(v)
        max_windows = max(max_windows, len(v))
    for k, v in pitches_by_type.items():
        v.extend([0.0] * (max_windows - len(v)))

    ind = np.arange(max_windows)
    width = 0.15

    # Visualize each pitch type individually so we can see how
    #  the pitch type occurrences change over time (number of pitches)
    i = 0
    for pitch_type, pitch_counts in pitches_by_type.iteritems():
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        ax.bar(ind, pitch_counts)
        ax.set_xticks(ind)
        ax.set_xticklabels(
            [str(i * pitches_per_window) + "-" + str((i + 1) * pitches_per_window) \
            for i in xrange(max_windows)]
        )
        ax.set_title(pitch_type + " Over Time (Pitches)")
        ax.set_xlabel("Pitch Range")
        ax.set_ylabel("Number of Pitches")

        fig.savefig(
            os.path.join(
                out_dir,
                str(df['pitcher_id'][0]) + "-" + \
                pitch_type + "-n" + str(pitches_per_window) + ".png"
            )
        )
        i += 1


def main():
    """Main execution."""

    # Determine command line arguments.
    try:
        rawopts, _ = getopt.getopt(sys.argv[1:], 'i:n:o:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    opts = {}

    # Process each command line argument.
    for o, a in rawopts:
        opts[o[1]] = a

    # The following arguments are required in all cases.
    for opt in ['i', 'n', 'o']:
        if not opt in opts:
            usage()
            sys.exit(2)

    run(opts['i'], int(opts['n']), opts['o'])


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
