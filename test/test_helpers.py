import numpy as np

from opensauce.helpers import wavread

from test.support import TestCase, data_file_path, loadmat


class TestSupport(TestCase):

    def test_wavread(self):
        fn = data_file_path('beijing_f3_50_a.wav')
        samples, Fs = wavread(fn)
        expected = loadmat('beijing_f3_50_a-wavread-expected')
        self.assertEqual(Fs, expected['Fs'])
        self.assertTrue(np.array_equal(samples, expected['y']))
        # XXX may need to use allclose here instead of array_equal.
        if not np.array_equal(samples, expected['y']):
            # Produce a useful error message for debugging.
            self.assertEqual(list(samples), list(expected['y']))
