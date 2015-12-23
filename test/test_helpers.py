from opensauce.helpers import wavread

from test.support import TestCase, data_file_path

class TestSupport(TestCase):

    def test_wavfile(self):
        fn = data_file_path('beijing_f3_50_a.wav')
        os_samples, Fs = wavread(fn)
        with open(data_file_path('beijing_f3_50_a-y.mat')) as f:
            lines = iter(f)
            line = next(lines)
            while line.strip().startswith('#'):
                line = next(lines)
            ml_samples = [float(line.strip())]
            for line in lines:
                line = line.strip()
                if line:
                    ml_samples.append(float(line))
        self.assertEqual(Fs, 22050)   # agrees with octave value
        # Both Python and Matlab/octave implement IEEE 754, so this should be
        # an exact match.
        self.assertEqual(list(os_samples), ml_samples)
