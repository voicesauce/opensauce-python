import numpy as np

from opensauce.helpers import wavread

from test.support import TestCase, data_file_path, load_json


class TestSupport(TestCase):

    def test_wavread(self):
        fn = data_file_path('beijing_f3_50_a.wav')
        samples, Fs = wavread(fn)
        expected = load_json('beijing_f3_50_a-wavread-expected')
        self.assertEqual(Fs, expected['Fs'])
        self.assertTrue(np.allclose(samples, expected['y']))
