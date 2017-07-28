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


def main(wav_dir, fs_rs):
    """Compare original data vs resampled data for all wav files in wav_dir,
    where resampling frequency is given in Hz by fs_rs
    """
    # Find all .wav files in test/data directory
    wav_files = glob.glob(os.path.join(wav_dir, '*.wav'))

    for wav_file in wav_files:
        print('Processing wav file {}'.format(wav_file))
        # y is data points, fs is sampling frequency
        y, fs = wavread(wav_file)
        # ns is number of samples
        ns = len(y)
        period = 1.0 / fs
        # Time points corresponding to samples
        t = np.arange(0, ns*period, period)

        # Resample to 16 kHz
        period_rs = 1.0 / fs_rs
        # Number of points in resample
        ns_rs = round_half_away_from_zero(ns * fs_rs / fs)
        # Do resample
        y_rs, t_rs = resample(y, ns_rs, t)

        # Number of points to plot
        n = 1000
        # Start plotting from this data point
        s = randint(10000, 35015-n)
        plt.figure()
        plt.plot(t, y, 'b-', markersize=1)
        plt.plot(t_rs, y_rs, 'ro', markersize=3)
        plt.xlim(s*period, (s+n)*period)
        plt.title(os.path.basename(wav_file))
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.savefig(os.path.splitext(os.path.basename(wav_file))[0] + '.pdf')

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
