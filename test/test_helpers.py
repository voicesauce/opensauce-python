import numpy as np
from scipy.io import loadmat

from opensauce.helpers import wavread

from test.support import TestCase, data_file_path

class TestSupport(TestCase):

    def test_wavread(self):
        fn = data_file_path('beijing_f3_50_a.wav')
        samples, Fs = wavread(fn)
        expected = loadmat(data_file_path('beijing_f3_50_a-wavread-expected.mat'),
                           squeeze_me=True)
        self.assertEqual(Fs, expected['Fs'])
        # XXX may need to use allclose here instead of array_equal.
        if not np.array_equal(samples, expected['y']):
            # Produce a useful error message for debugging.
            self.assertEqual(list(samples), list(expected['y']))
