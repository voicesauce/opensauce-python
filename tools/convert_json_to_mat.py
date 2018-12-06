# Script to convert json into proprietary .mat files

# Licensed under Apache v2 (see LICENSE)

import sys
import os
import glob
import json
from scipy.io import savemat


def main(json_dir, out_dir):
    """ Script to convert all .json files in json_dir into corresponding .mat
        files in out_dir

    .mat files have the same basename as the .json files

    This script is meant for data files that contain data from
    OpenSauce / VoiceSauce variables.
    """
    # Find all .json files in json_dir
    json_files = glob.glob(os.path.join(json_dir, '*.json'))

    # Iterate through each .mat file
    for json_file in json_files:
        with open(json_file) as f:
            json_dict = json.load(f)
        # Write json dict to mat
        # Check that output directory exists, if not create it
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        fn = os.path.join(out_dir, os.path.splitext(os.path.basename(json_file))[0]) + '.mat'
        savemat(fn, json_dict)
        print('Wrote data in {} to {}'.format(json_file, fn))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
