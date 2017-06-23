# Script to convert proprietary .mat files into json

import sys
import os
import glob
import json
import numpy as np
from scipy.io import loadmat

def main(mat_dir, out_dir):
    """ Script to convert all .mat files in mat_dir into corresponding json files
        in out_dir

    Any Matlab arrays are converted to lists of floats
    .json files have the same basename as the .mat files
    """
    # Find all .mat files in mat_dir
    mat_files = glob.glob(os.path.join(mat_dir, '*.mat'))

    # Iterate through each .mat file
    for mat_file in mat_files:
        json_dict = {}
        mat_dict = loadmat(mat_file, squeeze_me=True)
        # Iterate through all entries of mat_dict
        # For each entry, convert data type if necessary
        for k in mat_dict:
            if isinstance(mat_dict[k], np.ndarray):
                json_dict[k] = mat_dict[k].tolist()
            elif isinstance(mat_dict[k], unicode):
                json_dict[k] = mat_dict[k]
            elif isinstance(mat_dict[k], str):
                json_dict[k] = mat_dict[k]
            elif isinstance(mat_dict[k], int):
                json_dict[k] = mat_dict[k]
            elif isinstance(mat_dict[k], float):
                json_dict[k] = mat_dict[k]
            elif isinstance(mat_dict[k], list):
                json_dict[k] = mat_dict[k]
            else:
                print('Did not convert key {} of type {}'.format(k, type(k)))
        # Write converted dict to json
        # Check that output directory exists, if not create it
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        fn = os.path.join(out_dir, os.path.splitext(os.path.basename(mat_file))[0]) + '.json'
        with open(fn, 'w') as f:
            json.dump(json_dict, f)
        print('Wrote data in {} to JSON in {}'.format(mat_file, fn))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
