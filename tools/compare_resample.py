# Script to plot original wav file against wav file resampled at 16 kHz

# Licensed under Apache v2 (see LICENSE)

from __future__ import division

import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt

from numpy.random import randint
from scipy.signal import resample

# Problems doing this import
# May need to move this file to top level directory
from opensauce.helpers import wavread, round_half_away_from_zero
from test.support import load_json

def main(wav_dir, fs_rs):
    """Compare original data vs resampled data for all wav files in wav_dir,
    where resampling frequency is given in Hz by fs_rs
    """
    # Find all .wav files in test/data directory
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

    for wav_file in wav_files:
        print('Processing wav file {}'.format(wav_file))
        # y is data points, fs is sampling frequency
        y, y_int, fs = wavread(wav_file)
        # ns is number of samples
        ns = len(y)
        period = 1.0 / fs
        # Time points corresponding to samples
        t = np.arange(0, ns*period, period)

        # Resample to 16 kHz
        period_rs = 1.0 / fs_rs
        # Number of points in resample
        ns_rs = np.int_(np.ceil(ns * fs_rs / fs))
        # Do resample
        y_rs, t_rs = resample(y, ns_rs, t)
        y_h, t_h = resample(y, ns_rs, t, window='hamming')

        # Number of points to plot
        n = 1000
        # Start plotting from this data point
        # Choose random starting point
        s = randint(10000, 35015-n)

        fig = plt.figure()
        fig.suptitle(os.path.basename(wav_file))
        # Compare original data with resampled ata
        ax = plt.subplot(2,1,1)
        ax.plot(t, y, 'b-', markersize=1)
        ax.plot(t_rs, y_rs, 'ro', markersize=3)
        ax.set_xlim([s*period, (s+n)*period])
        ax.set_ylabel('Amplitude')
        ax.set_title('Normal resample')
        # Compare original data with resampling + Hamming window
        ax = plt.subplot(2,1,2)
        ax.plot(t, y, 'b-', markersize=1)
        ax.plot(t_h, y_h, 'ro', markersize=3)
        ax.set_xlim([s*period, (s+n)*period])
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time (s)')
        ax.set_title('Hamming window')
        plt.savefig(os.path.splitext(os.path.basename(wav_file))[0] + '.pdf')

        fn = os.path.splitext(os.path.basename(wav_file))[0] + '-matlab-resample'
        data = load_json(os.path.join('soundfile', fn))
        y_rs_matlab = data['y_rs']

        # Compare SciPy resampled data with Matlab resampled data
        plt.figure()
        plt.plot(np.linspace(0, period * ns, len(y_rs_matlab)), y_rs_matlab, 'b-', markersize=1)
        plt.plot(t_rs, y_rs, 'ro', markersize=3)
        plt.xlim(s*period, (s+n)*period)
        plt.title(os.path.basename(wav_file) + ' - Matlab comparison')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.savefig(os.path.splitext(os.path.basename(wav_file))[0] + '-matlab.pdf')

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
