# Script to generate resampled data from test wav files
# The data is used for comparison in unit tests

# Licensed under Apache v2 (see LICENSE)

import sys
import os
import glob
import numpy as np

from opensauce.soundfile import SoundFile


def main(wav_dir, out_dir):
    # Find all .wav files in directory
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

    # Generate resampled data for each wav file and save it
    for wav_file in wav_files:
        #wav_basename = os.path.basename(wav_file)
        print('Processing wav file {}'.format(wav_file))
        # Process soundfile
        s = SoundFile(wav_file, resample_freq=16000)
        # Save resampled data to text file
        fn = os.path.splitext(os.path.basename(wav_file))[0]
        fn = os.path.join(out_dir, fn) + '-raw-resample-16kHz.txt'
        np.savetxt(fn, s.wavdata_rs)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
