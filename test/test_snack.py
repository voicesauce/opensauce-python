from __future__ import division

import math
import unittest
import numpy as np

from sys import platform

# Import user-defined global configuration variables
from tools.userconf import user_default_snack_method

from opensauce.snack import snack_pitch

from test.support import TestCase, wav_fns, get_test_data, get_sample_data


class TestSnack(TestCase):

    longMessage = True

    _valid_snack_methods = ['exe', 'python', 'tcl']
    if user_default_snack_method is not None:
        if user_default_snack_method in _valid_snack_methods:
            if user_default_snack_method == 'exe' and (platform != 'win32' and platform != 'cygwin'):
                raise ValueError("Cannot use 'exe' as Snack calling method, when using non-Windows machine")
            default_snack_method = user_default_snack_method
        else:
            raise ValueError("Invalid Snack calling method. Choices are 'exe', 'python', and 'tcl'")
    elif platform == "win32" or platform == "cygwin":
        default_snack_method = 'exe'
    elif platform.startswith("linux"):
        default_snack_method = 'tcl'
    elif platform == "darwin":
        default_snack_method = 'tcl'
    else:
        default_snack_method = 'tcl'

    #
    # XXX This test fails because the data we generate does not match the data
    # Kristine generated from Voicesauce.  We do not at this time know why, so
    # the test is marked as an expected failure.  The fact that the data does
    # not match does not affect the design of the port to python, but clearly
    # the issue needs to be understood and addressed in some way.
    #
    # Since all other data generated by voicesauce depends on the F0 data, none
    # of the additional snack based sample data can be tested at this time.
    #
    @unittest.expectedFailure
    def test_against_voicesauce_data(self):
        # XXX I think these are the voicesauce defaults (vs expresses them
        # in ms, but snack expects seconds).
        f_len = 0.001
        w_len = 0.025
        for fn in wav_fns:
            # XXX I think voicesauce will optionally emit the Voice data, but I
            # don't have example output data for it, so I'm ignoring it for now.
            F0, V = snack_pitch(fn, self.default_snack_method, frame_length=f_len, window_length=w_len)
            # The first samples in all of our test data yield 0.
            self.assertEqual(F0[:10], [0.0]*10)
            # The snack esps data starts in the middle of the first window,
            # but the voicesauce output data starts counting frames from 0,
            # so pad our F0 with invalid frames.
            # XXX I'm not sure why -1 seems to make the data match up better,
            # voicesauce doesn't have the -1 term.
            F0[:0] = [float('NaN')] * int(math.floor(w_len/f_len/2)-1)
            # NB: It doesn't matter which output file we use, the sF0 column is
            # the same in all of them.
            voicesauce_data = get_test_data(fn, 'sF0', 'sf0', '1ms')
            os_data = []
            vs_data = []
            for ms, fs0 in voicesauce_data:
                ms = int(ms)
                # Voicesauce rounds to three places.
                os_data.append(round(F0[ms], 3))
                vs_data.append(fs0)
            # XXX debug prints.
            #for i in range(len(os_data)):
            #    print((i, os_data[i], voicesauce_data[i]))
            #print(fn)
            for i in range(len(os_data)):
                if (abs(os_data[i] - vs_data[i]) >= 40 and (os_data[i] == 0 or vs_data[i] == 0)):
                    continue
                self.assertLess(abs(os_data[i] - vs_data[i]), 0.6, "row %s" % i)

    def test_raw(self):
        # Test against previously generated data to make sure nothing has
        # broken and that there are no cross platform or snack version issues.
        # Data was generated by snack 2.2.10 on Manjaro Linux.
        for fn in wav_fns:
            F0, V = snack_pitch(fn, self.default_snack_method, frame_length=0.001, window_length=0.025, max_pitch=500, min_pitch=40)
            # Voice is 0 or 1, so (hopefully) no FP rounding issues.
            sample_data = get_sample_data(fn, 'V', 'sf0', '1ms')
            self.assertEqual(len(V), len(sample_data))
            self.assertTrue(np.allclose(V, sample_data))
            sample_data = get_sample_data(fn, 'sF0', 'sf0', '1ms')
            self.assertEqual(len(F0), len(sample_data))
            # Check that F0 and sample_data are "close enough" for
            # floating precision
            self.assertTrue(np.allclose(F0, sample_data))
