# Script to generate raw Praat samples from test wav files
# The data is used for comparison in unit tests

import sys
import os
import glob
import numpy as np

from opensauce.praat import praat_raw_pitch, praat_raw_formants


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

    # Generate Praat data for each wav file and save it to text files
    praat_path = '/usr/bin/praat'
    for wav_file in wav_files:
        wav_basename = os.path.basename(wav_file)

        print('Processing wav file {}'.format(wav_file))
        # Generate raw Praat pitch samples
        # Use VoiceSauce default parameter values
        t_raw, F0_raw = praat_raw_pitch(wav_file, praat_path, frame_shift=1,
                                        method='cc', min_pitch=40,
                                        max_pitch=500, silence_threshold=0.03,
                                        voice_threshold=0.45, octave_cost=0.01,
                                        octave_jumpcost=0.35,
                                        voiced_unvoiced_cost=0.14,
                                        kill_octave_jumps=0,
                                        interpolate=0
                                        smooth=0,
                                        smooth_bandwidth=5)
        # Save raw Praat pitch samples
        # Save F0 data to text file
        save_samples(t_raw, wav_basename, 'ptF0', '1ms', out_dir)
        save_samples(F0_raw, wav_basename, 'pF0', '1ms', out_dir)

        # Generate raw Praat formant samples
        # Use VoiceSauce default parameter values
        estimates_raw = praat_raw_formants(wav_file, praat_path, frame_shift=1,
                                           window_size=25, num_formants=4,
                                           max_formant_freq=6000)

        # Save raw Praat formant samples to text files
        for n in estimates_raw:
            save_samples(estimates_raw[n], wav_basename, n, '1ms', out_dir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
