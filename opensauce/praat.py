"""Estimate F0 and formants using Praat
"""

from __future__ import division

import os
import numpy as np

from subprocess import call

valid_praat_f0_methods = ['ac', 'cc']

praat_script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'praat-scripts')

# Praat will sometimes set numerical values to the string '--undefined--'
# But NumPy can't have a string in a float array, so we convert the
# '--undefined--' values to NaN
# Python 3 reads the undefined strings as byte literals, so we also have to
# check for the byte literal b'--undefined--'
undef = lambda x: np.nan if x =='--undefined--' or x == b'--undefined--' else x

#def praat_pitch(wav_fn, data_len, praat_path, frame_shift=1, method='cc',
#                    frame_precision=1, min_pitch=40, max_pitch=500,
#                    silence_threshold=0.03, voice_threshold=0.45,
#                    octave_cost=0.01, octave_jumpcost=0.35,
#                    voiced_unvoiced_cost=0.14, smooth_bandwidth=5,
#                    kill_octave_jumps=0, smooth=0, interpolate=0):

def praat_raw_pitch(wav_fn, praat_path, frame_shift=1, method='cc',
                    min_pitch=40, max_pitch=500, silence_threshold=0.03,
                    voice_threshold=0.45, octave_cost=0.01,
                    octave_jumpcost=0.35, voiced_unvoiced_cost=0.14,
                    smooth_bandwidth=5, kill_octave_jumps=0, smooth=0,
                    interpolate=0):
    """
    """
    # Determine extension of Praat output file
    if method == 'ac':
        ext = '.praatac'
    elif method == 'cc':
        ext = '.praatcc'
    else:
        raise ValueError('Invalid Praat F0 method. Choices are {}'.format(valid_praat_f0_methods))

    # Setup command to call Praat F0 script
    praat_cmd = [praat_path, '--run']
    praat_cmd.append(os.path.join(praat_script_dir, 'praatF0.praat'))
    praat_cmd.extend([os.path.abspath(wav_fn), os.path.splitext(wav_fn)[1]])
    praat_cmd.extend([str(frame_shift / 1000), str(min_pitch), str(max_pitch)])
    praat_cmd.extend([str(silence_threshold), str(voice_threshold)])
    praat_cmd.extend([str(octave_cost), str(octave_jumpcost)])
    praat_cmd.extend([str(voiced_unvoiced_cost), str(kill_octave_jumps)])
    praat_cmd.extend([str(smooth), str(smooth_bandwidth)])
    praat_cmd.extend([str(interpolate), str(method)])

    # Run Praat F0 script
    return_code = call(praat_cmd)

    if return_code != 0:
        raise OSError('Praat error')

    # Path for Praat F0 output file corresponding to wav_fn
    f0_fn = wav_fn.split('.')[0] + ext
    # Load data from f0 file
    if os.path.isfile(f0_fn):
        t_raw, F0_raw = np.loadtxt(f0_fn, unpack=True, converters={0: undef, 1: undef})
        # Cleanup and remove f0 file
        os.remove(f0_fn)
    else:
        raise OSError('Praat error -- unable to locate {} file'.format(ext))

    return t_raw, F0_raw

def praat_raw_formants(wav_fn, praat_path, frame_shift=1, window_size=25, num_formants=4, max_formant_freq=6000):
    """
    """
    # Setup command to call Praat F0 script
    praat_cmd = [praat_path, '--run']
    praat_cmd.append(os.path.join(praat_script_dir, 'praatformants.praat'))
    praat_cmd.extend([os.path.abspath(wav_fn), os.path.splitext(wav_fn)[1]])
    praat_cmd.extend([str(frame_shift / 1000), str(window_size / 1000)])
    praat_cmd.extend([str(num_formants), str(max_formant_freq)])

    # Run Praat F0 script
    return_code = call(praat_cmd)

    if return_code != 0:
        raise OSError('Praat error')

    # Path for Praat output file corresponding to wav_fn
    fmt_fn = wav_fn.split('.')[0] + '.pfmt'
    # Load data from Praat file
    if os.path.isfile(fmt_fn):
        num_cols = 2 + num_formants * 2
        # Define dictionary that uses undef for all columns
        undef_dict = {i: undef for i in range(num_cols)}
        data_raw = np.loadtxt(fmt_fn, dtype=float, skiprows=1, converters=undef_dict)
        # Cleanup and remove Praat file
        os.remove(fmt_fn)
    else:
        raise OSError('Praat error -- unable to locate .pfmt file')

    # Put data into dictionary
    estimates_raw = {}
    estimates_raw['pt'] = data_raw[:, 0]
    for i in range(1, num_formants + 1):
        estimates_raw['pF' + str(i)] = data_raw[:, 2*i]
        estimates_raw['pB' + str(i)] = data_raw[:, 2*i+1]

    return estimates_raw
