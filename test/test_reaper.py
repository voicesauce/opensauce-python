from __future__ import division

import random
import unittest
import numpy as np
from sys import platform

# Import user-defined global configuration variables
from conf.userconf import user_reaper_path

from opensauce.reaper import reaper_pitch, pyreaper_pitch, creaper_pitch

from opensauce.soundfile import SoundFile

from test.support import TestCase, wav_fns, get_sample_data

# Shuffle wav filenames, to make sure testing doesn't depend on order
random.shuffle(wav_fns)

# Determine default path to REAPER executable
if user_reaper_path is not None:
    default_reaper_path = user_reaper_path
else:
    default_reaper_path = None


class TestReaperPitchWrapper(TestCase):
    # Test the wrapper function reaper_pitch()

    longMessage = True

    def test_pitch_using_creaper(self):
        # Test against previously generated data to make sure nothing has
        # broken and that there are no cross platform or REAPER version issues.
        # Data was generated on Manjaro Linux.
        for fn in wav_fns:
            # Frame shift
            f_len = 1

            # Need ns (number of samples) and sampling rate (Fs) from wav file
            # to compute data length
            sound_file = SoundFile(fn)
            data_len = np.int_(np.floor(sound_file.ns / sound_file.fs / f_len * 1000))

            # Estimate F0 using REAPER, use default VoiceSauce values
            F0_os = reaper_pitch(sound_file, data_len, use_pyreaper=False,
                                 reaper_path=default_reaper_path,
                                 frame_shift=f_len, max_pitch=500,
                                 min_pitch=40, high_pass=True,
                                 hilbert_transform=False, inter_mark=10)
            # Get sample F0 data
            F0_sample_from_data = get_sample_data(fn, 'reaper', 'reaperF0', '1ms')
            # Fill full length F0 vector
            F0_sample = np.full(data_len, np.nan)
            F0_sample[:len(F0_sample_from_data)] = F0_sample_from_data
            # Check that F0 values are "close"
            self.assertAllClose(F0_os, F0_sample, rtol=1e-05, atol=1e-08, equal_nan=True)

    @unittest.skipIf(platform == 'win32' or platform == 'cygwin',
                         'No Windows support for pyreaper package')
    def test_pitch_using_pyreaper(self):
        # Test against previously generated data to make sure nothing has
        # broken and that there are no cross platform or REAPER version issues.
        # Data was generated on Manjaro Linux.
        for fn in wav_fns:
            # Frame shift
            f_len = 1

            # Need ns (number of samples) and sampling rate (Fs) from wav file
            # to compute data length
            sound_file = SoundFile(fn)
            data_len = np.int_(np.floor(sound_file.ns / sound_file.fs / f_len * 1000))

            # Estimate F0 using REAPER, use default VoiceSauce values
            F0_os = reaper_pitch(sound_file, data_len, use_pyreaper=True,
                                 frame_shift=f_len, max_pitch=500,
                                 min_pitch=40, high_pass=True,
                                 hilbert_transform=False, inter_mark=10)
            # Get sample F0 data
            F0_sample_from_data = get_sample_data(fn, 'reaper', 'reaperF0', '1ms')
            # Fill full length F0 vector
            F0_sample = np.full(data_len, np.nan)
            F0_sample[:len(F0_sample_from_data)] = F0_sample_from_data
            # Check that F0 values are "close"
            self.assertAllClose(F0_os, F0_sample, rtol=1e-05, atol=1e-08, equal_nan=True)


class TestReaperPitch(TestCase):
    # Test functions creaper_pitch() and pyreaper_pitch()

    def test_bad_reaper_path(self):
        fn = wav_fns[0]
        with self.assertRaisesRegex(OSError, 'Error while attempting to call REAPER.  Is REAPER path badpath correct?'):
            t_raw, F0_raw = creaper_pitch(fn, reaper_path='badpath',
                                          frame_shift=1, max_pitch=500,
                                          min_pitch=40, high_pass=True,
                                          hilbert_transform=False, inter_mark=10)

    def test_pitch_raw_using_creaper(self):
        # Test against previously generated data to make sure nothing has
        # broken and that there are no cross platform or REAPER version issues.
        # Data was generated on Manjaro Linux.

        for fn in wav_fns:
            # Estimate F0 using REAPER, use default VoiceSauce values
            t_raw, F0_raw = creaper_pitch(fn, reaper_path=default_reaper_path,
                                          frame_shift=1, max_pitch=500,
                                          min_pitch=40, high_pass=True,
                                          hilbert_transform=False, inter_mark=10)

            # Get sample time data
            time_sample = get_sample_data(fn, 'reaper', 'rtF0', '1ms')
            # Check number of entries is consistent
            self.assertEqual(len(t_raw), len(time_sample))
            # Check that computed time and sample_data are "close enough" for
            # floating precision
            self.assertAllClose(t_raw, time_sample, rtol=1e-05, atol=1e-08)

            # Get sample F0 data
            F0_sample = get_sample_data(fn, 'reaper', 'reaperF0', '1ms')
            # Check number of entries is consistent
            self.assertEqual(len(F0_raw), len(F0_sample))
            # Check that computed F0 and sample_data are "close enough" for
            # floating precision
            self.assertAllClose(F0_raw, F0_sample, rtol=1e-05, atol=1e-08, equal_nan=True)

    @unittest.skipIf(platform == 'win32' or platform == 'cygwin',
                         'No Windows support for pyreaper package')
    def test_pitch_raw_using_pyreaper(self):
        # Test against previously generated data to make sure nothing has
        # broken and that there are no cross platform or REAPER version issues.
        # Data was generated on Manjaro Linux.

        for fn in wav_fns:
            sound_file = SoundFile(fn)
            # Estimate F0 using REAPER, use default VoiceSauce values
            t_raw, F0_raw = pyreaper_pitch(sound_file.wavdata_int,
                                           sound_file.fs, frame_shift=1,
                                           max_pitch=500, min_pitch=40,
                                           high_pass=True,
                                           hilbert_transform=False,
                                           inter_mark=10)

            # Get sample time data
            time_sample = get_sample_data(fn, 'reaper', 'rtF0', '1ms')
            # Check number of entries is consistent
            self.assertEqual(len(t_raw), len(time_sample))
            # Check that computed time and sample_data are "close enough" for
            # floating precision
            self.assertAllClose(t_raw, time_sample, rtol=1e-05, atol=1e-08)

            # Get sample F0 data
            F0_sample = get_sample_data(fn, 'reaper', 'reaperF0', '1ms')
            # Check number of entries is consistent
            self.assertEqual(len(F0_raw), len(F0_sample))
            # Check that computed F0 and sample_data are "close enough" for
            # floating precision
            self.assertAllClose(F0_raw, F0_sample, rtol=1e-05, atol=1e-08, equal_nan=True)
