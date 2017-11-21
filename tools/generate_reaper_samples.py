# Script to generate raw REAPER samples from test wav files
# The data is used for comparison in unit tests

# Licensed under Apache v2 (see LICENSE)

import sys
import os
import glob
import numpy as np

from opensauce.reaper import creaper_pitch


def save_samples(data, fn, col_name, sample, out_dir):
    """Dump data in txt format using fn, col_name, and sample strings
       in file name
    """
    fn = os.path.splitext(os.path.basename(fn))[0]
    fn = '-'.join(('sample', fn, col_name, sample))
    fn = os.path.join(out_dir, fn) + '.txt'
    np.savetxt(fn, data)

def main(wav_dir, out_dir, reaper_path):
    # Find all .wav files in test/data directory
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

    # Generate Praat data for each wav file and save it to text files
    for wav_file in wav_files:
        wav_basename = os.path.basename(wav_file)

        print('Processing wav file {}'.format(wav_file))
        # Generate raw REAPER pitch samples
        # Use VoiceSauce default parameter values
        F0_times, F0 = creaper_pitch(wav_file, reaper_path=reaper_path,
                                     frame_shift=1, max_pitch=500,
                                     min_pitch=40, high_pass=True,
                                     hilbert_transform=False, inter_mark=10)
        # Save raw Praat pitch samples to text files
        save_samples(F0_times, wav_basename, 'rtF0', '1ms', out_dir)
        save_samples(F0, wav_basename, 'reaperF0', '1ms', out_dir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
