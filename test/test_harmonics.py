from __future__ import division

import random
import unittest
import numpy as np

from opensauce.harmonics import correction_iseli_i, bandwidth_hawks_miller

from test.support import TestCase, wav_fns, get_raw_data, get_harmonics_internal_test_data

# Shuffle wav filenames, to make sure testing doesn't depend on order
random.shuffle(wav_fns)


class TestHarmonicsInternal(TestCase):
    # Test internal functions from harmonics.py

    def test_iseli_against_voicesauce_data(self):
        # This table contains the names of the parameters used as arguments
        # to the correction_iseli_i() function.
        # For example, the first row ['F0', 'F1', 'B1'] would specify that
        # for the first calculation, the arguments are given to the function as
        # correction_iseli_i(F0, F1, B1, Fs) [note that the last parameter
        # is always Fs, the sampling frequency].
        # Each row of the table represents a calculation.
        iseli_param_table = np.array([['F0', 'F1', 'B1'],
                                      ['F0', 'F2', 'B2'],
                                      ['F3', 'F1', 'B1'],
                                      ['F3', 'F2', 'B2'],
                                      ['F3', 'F3', 'B3'],
                                      ['F1', 'F1', 'B1'],
                                      ['F1', 'F2', 'B2'],
                                      ['F2', 'F1', 'B1'],
                                      ['F2', 'F2', 'B2']])

        for fn in wav_fns:
            # Get some sample F0 and formant data
            # There's nothing special about this data, it's just some
            # realistic data for testing the internal harmonics functions
            sample = {}
            sample['Fs'] = get_raw_data(fn, 'Fs', 'strF0', 'FMTs', 'estimated')
            sample['F0'] = get_raw_data(fn, 'sF0', 'strF0', 'FMTs', 'estimated')
            sample['F1'] = get_raw_data(fn, 'sF1', 'strF0', 'FMTs', 'estimated')
            sample['F2'] = get_raw_data(fn, 'sF2', 'strF0', 'FMTs', 'estimated')
            sample['F3'] = get_raw_data(fn, 'sF3', 'strF0', 'FMTs', 'estimated')
            sample['B1'] = get_raw_data(fn, 'sB1', 'strF0', 'FMTs', 'estimated')
            sample['B2'] = get_raw_data(fn, 'sB2', 'strF0', 'FMTs', 'estimated')
            sample['B3'] = get_raw_data(fn, 'sB3', 'strF0', 'FMTs', 'estimated')

            # Compute a bunch of Iseli-Alwan harmonic amplitude corrections
            num_calcs = iseli_param_table.shape[0]
            # Initialize table for storing OpenSauce Iseli calculations
            # We expect each Iseli calculation to be the same length as the
            # frequency vectors input to the arguments
            os_iseli = np.empty((num_calcs, len(sample['F1'])))
            # Fill in the table, computing Iseli-Alwan corrections
            for i in range(num_calcs):
                p1 = sample[iseli_param_table[i, 0]]
                p2 = sample[iseli_param_table[i, 1]]
                p3 = sample[iseli_param_table[i, 2]]
                os_iseli[i, :] = correction_iseli_i(p1, p2, p3, sample['Fs'])

            # Get the test data that was computed in VoiceSauce
            vs_iseli = get_harmonics_internal_test_data(fn, 'iseli')

            # Check number of entries is consistent
            self.assertEqual(os_iseli.shape[0], vs_iseli.shape[0])
            self.assertEqual(os_iseli.shape[1], vs_iseli.shape[1])

            # Check that Iseli-Alwan corrections computed by OpenSauce
            # and VoiceSauce are "close enough" for floating precision
            for i in range(num_calcs):
                self.assertAllClose(os_iseli[i, :], vs_iseli[i, :], rtol=1e-05, atol=1e-08, equal_nan=True)

    def test_hawks_miller_against_voicesauce_data(self):
        # This table contains the names of the parameters used as arguments
        # to the bandwidth_hawks_miller() function.
        # For example, the first row ['F1'] would specify that
        # for the first calculation, the first argument given to the function
        # is bandwidth_hawks_miller(F1, F0) [note that the second parameter
        # is always F0, the fundamental frequency].
        # Each row of the table represents a calculation.

        hawks_param_table = np.array([['F1'],['F2'],['F3']])

        for fn in wav_fns:
            # Get some sample F0 and formant data
            # There's nothing special about this data, it's just some
            # realistic data for testing the internal harmonics functions
            sample = {}
            sample['F0'] = get_raw_data(fn, 'sF0', 'strF0', 'FMTs', 'estimated')
            sample['F1'] = get_raw_data(fn, 'sF1', 'strF0', 'FMTs', 'estimated')
            sample['F2'] = get_raw_data(fn, 'sF2', 'strF0', 'FMTs', 'estimated')
            sample['F3'] = get_raw_data(fn, 'sF3', 'strF0', 'FMTs', 'estimated')

            # Compute a bunch of bandwidths using Hawks-Miller method
            num_calcs = hawks_param_table.shape[0]
            # Initialize table for storing OpenSauce bandwidth calculations
            # We expect each bandwidth calculation to be the same length as the
            # frequency vectors input to the arguments
            os_hawks = np.empty((num_calcs, len(sample['F1'])))
            # Fill in the table, computing bandwidths
            for i in range(num_calcs):
                p1 = sample[hawks_param_table[i, 0]]
                os_hawks[i, :] = bandwidth_hawks_miller(p1, sample['F0'])

            # Get the test data that was computed in VoiceSauce
            vs_hawks = get_harmonics_internal_test_data(fn, 'hawks')

            # Check number of entries is consistent
            self.assertEqual(os_hawks.shape[0], vs_hawks.shape[0])
            self.assertEqual(os_hawks.shape[1], vs_hawks.shape[1])

            # Check that bandwidths computed by OpenSauce and VoiceSauce
            # are "close enough" for floating precision
            for i in range(num_calcs):
                self.assertAllClose(os_hawks[i, :], vs_hawks[i, :], rtol=1e-05, atol=1e-08, equal_nan=True)
