#!/usr/bin/env python
import argparse
from like_profile_fit import go
import glob
import os


def find_profiles(intervals_dir):
    intervals_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(intervals_dir)))
    intervals = glob.glob(os.path.join(intervals_dir, "profile*.npz"))
    print("Found %i intervals in directory %s" % (len(intervals), intervals_dir))
    if len(intervals) == 0:
        print("No interval found, nothing to do.")
        return {}
    # Find files
    profiles_dict = {}
    for interval in intervals:
        #print interval
        _=os.path.basename(interval).replace("profile", "").replace(".npz", "").split("_")
        start=float(_[2])
        stop=float(_[3])
        profiles_dict[(start, stop)] = interval
        pass
    
    return profiles_dict


def main(arguments):
    profiles_dict = find_profiles(arguments.intervals_dir)
    outroot= '%s/profile' % os.path.abspath(os.path.expandvars(os.path.expanduser(arguments.intervals_dir)))
    po_best_fit, bknpo_best_fit, TS = go(profiles_dict, arguments.tstart, arguments.tstop, outroot, arguments.local_minimizer)
    return po_best_fit, bknpo_best_fit, TS
# Main code
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--intervals_dir", help="Directory containing the intervals produced during the ExtendedEmission analysis. ",
                        type=str, required=True)
    parser.add_argument("--tstart", help="Use only time intervals with tstart after this time", type=float,
                        required=True, default=None)
    parser.add_argument("--tstop", help="Use only time intervals with tstop before this time", type=float,
                        required=True, default=None)
    parser.add_argument("--local_minimizer", help="Minimizer to use as local minimizer (default: ROOT)", type=str,
                        required=False, default="ROOT")


    args = parser.parse_args()
    main(args)
