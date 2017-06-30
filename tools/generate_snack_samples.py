# Script to generate raw Snack samples from test wav files
# The data is used for comparison in unit tests

# Licensed under Apache v2 (see LICENSE)

import sys
import os
import glob
import numpy as np

from opensauce.snack import snack_raw_pitch, snack_raw_formants, sformant_names


def save_samples(data, fn, col_name, sample, out_dir):
    """Dump data in txt format using fn, col_name, and sample strings
       in file name
    """
    fn = os.path.splitext(os.path.basename(fn))[0]
    fn = '-'.join(('sample', fn, col_name, sample))
    fn = os.path.join(out_dir, fn) + '.txt'
    np.savetxt(fn, data)

def main(wav_dir, out_dir):
    # Find all .wav files in test/data directory
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

    # Generate Snack data for each wav file and save it to text files
    method = 'tcl'
    for wav_file in wav_files:
        print('Processing wav file {}'.format(wav_file))
        # Generate raw Snack pitch samples
        # Use VoiceSauce default parameter values
        F0_raw, V_raw = snack_raw_pitch(wav_file, method, frame_shift=1, window_size=25, max_pitch=500, min_pitch=40)

        # Save raw Snack pitch samples
        wav_basename = os.path.basename(wav_file)
        # Save F0 and V data to separate text files
        save_samples(F0_raw, wav_basename, 'sF0', '1ms', out_dir)
        save_samples(V_raw, wav_basename, 'sV', '1ms', out_dir)

        # Generate raw Snack formant samples
        # Use VoiceSauce default parameter values
        estimates_raw = snack_raw_formants(wav_file, method, frame_shift=1, window_size=25, pre_emphasis=0.96, lpc_order=12)

        # Save raw Snack formant samples
        wav_basename = os.path.basename(wav_file)
        # Save data to separate text files
        for n in sformant_names:
            save_samples(estimates_raw[n], wav_basename, n, '1ms', out_dir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
