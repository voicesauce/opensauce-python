import os
import numpy as np

from opensauce.shrp import (window, toframes, two_max, compute_shr,
                            get_log_spectrum, shrp, shr_pitch, vda,
                            ethreshold, postvda, zcr)
from opensauce.helpers import wavread

from test.support import TestCase, parameterize, load_json, sound_file_path


@parameterize
class TestWindow(TestCase):

    window_params = dict(
        rect10=('rect', 10, None, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
        rect3=('rectangular', 3, None, [1, 1, 1]),
        rect4=('rectan', 4, None, [1, 1, 1, 1]),
        tria10=('tria', 10, None,
            [0.00000, 0.22222, 0.44444, 0.66667, 0.88889,
             0.88889, 0.66667, 0.44444, 0.22222, 0.00000]),
        tria3=('triangular', 3, None, [0, 1, 0]),
        hann10=('hann', 10, None,
            [0.00000, 0.11698, 0.41318, 0.75000, 0.96985,
             0.96985, 0.75000, 0.41318, 0.11698, 0.00000]),
        hann3=('hanning', 3, None, [0, 1, 0]),
        hamm10=('hamm', 10, None,
            [0.080000, 0.187620, 0.460122, 0.770000, 0.972259,
             0.972259, 0.770000, 0.460122, 0.187620, 0.080000]),
        hamm3=('hamming', 3, None, [0.080000, 1.00000, 0.080000]),
        blac10=('blac', 10, None,
            [-1.3878e-17, 5.0870e-02, 2.5800e-01, 6.3000e-01, 9.5113e-01,
              9.5113e-01, 6.3000e-01, 2.5800e-01, 5.0870e-02, -1.3878e-17]),
        black3=('blackman', 3, None, [-1.3878e-17, 1.0000e+00, -1.3878e-17]),
        # XXX: I don't know what beta is, and don't need to find the answer for
        # this project.
        #kais10=('kais', 10, ?, []),
        #kais10_2=('kaiser', 10, ?, []),
        #kais3=('kais', 3, ?, []),
        #kais3_2=('kais', 3, ?, []),
        )

    def window_as_window_args(self, window_type, window_width, beta, expected):
        res = window(window_width, window_type, beta)
        self.assertIsInstance(res, np.ndarray)
        # octave gives results to five places (single precision float?)
        for i in range(len(expected)):
            self.assertAlmostEqual(res[i], expected[i], places=5,
                                   msg='at index {}:\n{}\n  vs\n{}'.format(
                                        i, res, expected))

    def test_window_bad_window_type(self):
        with self.assertRaises(ValueError):
            window(10, 'bad')
        with self.assertRaises(ValueError):
            window(10, 'longerbad')
        with self.assertRaises(ValueError):
            window(10, 'rec')   # Not four chars.

    def test_kais_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            window(10, 'kais', 0)


class TestToframes(TestCase):

    def test_with_matlab_data(self):
        data = load_json(os.path.join('shrp', 'toframes_data'))
        res = toframes(data['input'],
                       data['curpos'].astype(int)-1,
                       int(data['segmentlen']),
                       'hamm')
        np.testing.assert_array_almost_equal(res, data['frames'])


@parameterize
class Test_two_max(TestCase):

    matlab_fn_params = (['twomax_data'], ['two_max_183'])

    def matlab_fn_as_matlab_input_data(self, filename):
        data = load_json(os.path.join('shrp',filename))
        mag, index = two_max(data['x'],
                             int(data['lowerbound'])-1,
                             int(data['upperbound'])-1,
                             data['unitlen'])
        np.testing.assert_array_almost_equal(mag, data['mag'])
        np.testing.assert_array_almost_equal(index, int(data['index'])-1)

    def test_second_peak_index(self):
        data = load_json(os.path.join('shrp', 'twomax_data'))
        x = data['x']
        for i in range(142, 146):
            # Zap the values in the second peak range to exercise the branch.
            x[i] = 0.0001*i
        mag, index = two_max(x,
                             int(data['lowerbound'])-1,
                             int(data['upperbound'])-1,
                             data['unitlen'])
        np.testing.assert_array_almost_equal(mag,
                                             np.append(data['mag'], 0.0145))
        np.testing.assert_array_equal(index, [int(data['index'])-1, 145])


@parameterize
class Test_compute_shr(TestCase):

    matlab_fn_params = (['ComputeSHR_data'], ['compute_shr_183'])

    def matlab_fn_as_matlab_input_data(self, filename):
        data = load_json(os.path.join('shrp', filename))
        peak_index, shr, shshift, index = compute_shr(
            data['log_spectrum'],
            data['min_bin'],
            data['startpos'].astype(int)-1,
            data['endpos'].astype(int)-1,
            int(data['lowerbound'])-1,
            int(data['upperbound'])-1,
            int(data['N']),
            int(data['shift_units']),
            data['SHR_Threshold'])
        np.testing.assert_array_equal(peak_index, int(data['peak_index'])-1)
        np.testing.assert_array_almost_equal(shr, data['SHR'])
        np.testing.assert_array_almost_equal(shshift, data['shshift'])
        np.testing.assert_array_almost_equal(index, data['index']-1)

    # XXX Need test data that exercises each of the if branches.  The
    # one above has only one peak.  Test_shrp exercises more.


class Test_get_log_spectrum(TestCase):

    def test_with_matlab_data(self):
        data = load_json(os.path.join('shrp', 'GetLogSpectrum_data'))
        interp_amplitude = get_log_spectrum(
            data['segment'],
            int(data['fftlen']),
            int(data['limit']) - 1,
            data['logf'],
            data['interp_logf'])
        np.testing.assert_array_almost_equal(interp_amplitude,
                                             data['interp_amplitude'])


class Test_shrp(TestCase):

    def test_with_matlab_data(self):
        data = load_json(os.path.join('shrp', 'shrp_data'))
        f0_time, f0_value, shr, f0_candidates = shrp(
            data['Y'],
            int(data['Fs']),
            [int(x) for x in data['F0MinMax']],
            int(data['frame_length']),
            int(data['timestep']),
            data['SHR_Threshold'],
            data['ceiling'],
            data['med_smooth'],
            data['CHECK_VOICING'])
        np.testing.assert_array_almost_equal(f0_time, data['f0_time'])
        np.testing.assert_array_almost_equal(f0_value, data['f0_value'])
        np.testing.assert_array_almost_equal(shr, data['SHR'])
        np.testing.assert_array_almost_equal(f0_candidates,
                                             data['f0_candidates'])

    def test_check_voicing(self):
        data = load_json(os.path.join('shrp', 'shrp_data'))
        with self.assertRaises(NotImplementedError):
            f0_time, f0_value, shr, f0_candidates = shrp(
                data['Y'],
                int(data['Fs']),
                [int(x) for x in data['F0MinMax']],
                int(data['frame_length']),
                int(data['timestep']),
                data['SHR_Threshold'],
                data['ceiling'],
                data['med_smooth'],
                CHECK_VOICING=True)

    def test_med_smooth_greater_than_zero(self):
        data = load_json(os.path.join('shrp', 'shrp_data'))
        with self.assertRaises(NotImplementedError):
            f0_time, f0_value, shr, f0_candidates = shrp(
                data['Y'],
                int(data['Fs']),
                [int(x) for x in data['F0MinMax']],
                int(data['frame_length']),
                int(data['timestep']),
                data['SHR_Threshold'],
                data['ceiling'],
                med_smooth=5,
                CHECK_VOICING=False)

class Test_shr_pitch(TestCase):

    def test_with_matlab_data(self):
        data = load_json(os.path.join('shrp', 'shr_pitch_data'))
        wav_data, wavdata_int, fps = wavread(sound_file_path('beijing_f3_50_a.wav'))
        shr, f0 = shr_pitch(wav_data, fps, 25, 1, 50, 550, 0.4, 5, 200)
        np.testing.assert_array_almost_equal(f0, data['F0'])
        np.testing.assert_array_almost_equal(shr, data['SHR'])

    def test_with_min_max_pitch_not_specified(self):
        data = load_json(os.path.join('shrp', 'shr_pitch_data'))
        wav_data, wavdata_int, fps = wavread(sound_file_path('beijing_f3_50_a.wav'))

        with self.assertRaisesRegex(ValueError, 'none or both of min_pitch, max_pitch must be specified'):
            shr, f0 = shr_pitch(wav_data, fps, min_pitch=50, datalen=200)

        with self.assertRaisesRegex(ValueError, 'none or both of min_pitch, max_pitch must be specified'):
            shr, f0 = shr_pitch(wav_data, fps, max_pitch=550, datalen=200)

class Test_not_implemented(TestCase):

    def test_vda(self):
        with self.assertRaises(NotImplementedError):
            vda(None, None, None, None)

    def test_ethreshold(self):
        with self.assertRaises(NotImplementedError):
            ethreshold(None)

    def test_postvda(self):
        with self.assertRaises(NotImplementedError):
            postvda(None, None, None, None)

    def test_zcr(self):
        with self.assertRaises(NotImplementedError):
            zcr(None, None)
