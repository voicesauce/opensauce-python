# Script to generate raw Snack samples from test wav files
# The data is used for comparison in unit tests

import sys
import os
import glob
import numpy as np

from opensauce.snack import snack_pitch, snack_formants, sformant_names


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
        # Generate Snack pitch samples
        # Use VoiceSauce default parameter values
        F0, V = snack_pitch(wav_file, method, frame_length=0.001, window_length=0.025, max_pitch=500, min_pitch=40)

        # Save Snack pitch samples
        wav_basename = os.path.basename(wav_file)
        # Save F0 and V data to separate text files
        save_samples(F0, wav_basename, 'sF0', '1ms', out_dir)
        save_samples(V, wav_basename, 'sV', '1ms', out_dir)

        # Generate Snack formant samples
        # Use VoiceSauce default parameter values
        estimates = snack_formants(wav_file, method, frame_length=0.001, window_length=0.025, pre_emphasis=0.96, lpc_order=12)

        # Save Snack formant samples
        wav_basename = os.path.basename(wav_file)
        # Save F0 and V data to separate text files
        for n in sformant_names:
            save_samples(estimates[n], wav_basename, n, '1ms', out_dir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
