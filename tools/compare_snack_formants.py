# Script to compare Snack formant methods on Windows
# There is a known discrepancy between Snack formants calculated using
# the full Snack Tcl library ('tcl' method) and the Windows standalone
# executable ('exe' method)

import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

from opensauce.snack import snack_raw_formants, sformant_names


wav_dir = 'test/data/sound-files'
# Find all .wav files in test/data directory
wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

for wav_file in wav_files:
    print('Processing wav file {}'.format(wav_file))
    # Generate raw Snack formant samples
    # Use VoiceSauce default parameter values
    estimates_raw_tcl = snack_raw_formants(wav_file, 'tcl', frame_shift=1, window_size=25, pre_emphasis=0.96, lpc_order=12, tcl_shell_cmd = 'tclsh')
    estimates_raw_exe = snack_raw_formants(wav_file, 'exe', frame_shift=1, window_size=25, pre_emphasis=0.96, lpc_order=12)

    fig = plt.figure(figsize=(8,8))
    fig.suptitle('Snack formants - ' + os.path.basename(wav_file))
    for i, n in enumerate(sformant_names):
        ax = plt.subplot(4,2,i+1)
        ax.plot(estimates_raw_exe[n], 'r.', estimates_raw_tcl[n], 'bo', markersize=1)
        #ax.plot(estimates_raw_tcl[n], 'bo', estimates_raw_exe[n], 'r.', markersize=1)
        ax.set_xticklabels([])
        plt.title(n)
        plt.savefig(os.path.splitext(os.path.basename(wav_file))[0] + '.pdf')
        plt.savefig(os.path.splitext(os.path.basename(wav_file))[0] + '.png')
