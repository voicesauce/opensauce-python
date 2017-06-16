# Script to generate raw Snack samples from test wav files
# The data is used for comparison in unit tests

import os
import glob
from opensauce.snack import snack_pitch, snack_formants, formant_names
from test.support import save_sample_data

def main():
    # Find all .wav files in test/data directory
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    wav_files = glob.glob(os.path.join(cur_dir, 'test', 'data', '*.wav'))

    # Generate Snack data for each wav file and save it to text files
    method = 'tcl'
    for wav_file in wav_files:
        # Generate Snack pitch samples
        # Use VoiceSauce default parameter values
        F0, V = snack_pitch(wav_file, method, frame_length=0.001, window_length=0.025, max_pitch=500, min_pitch=40)

        # Save Snack pitch samples
        wav_basename = os.path.basename(wav_file)
        # Save F0 and V data to separate text files
        save_sample_data(F0, wav_basename, 'sF0', '1ms')
        save_sample_data(V, wav_basename, 'sV', '1ms')

        # Generate Snack formant samples
        # Use VoiceSauce default parameter values
        estimates = snack_formants(wav_file, method, frame_length=0.001, window_length=0.025, pre_emphasis=0.96, lpc_order=12)

        # Save Snack formant samples
        wav_basename = os.path.basename(wav_file)
        # Save F0 and V data to separate text files
        for n in formant_names:
            save_sample_data(estimates[n], wav_basename, n, '1ms')


if __name__ == '__main__':
    main()
