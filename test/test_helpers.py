import os
import shutil

from opensauce.helpers import wavread, round_half_away_from_zero, remove_empty_lines_from_file, convert_boolean_for_praat

from test.support import TestCase, data_file_path, sound_file_path, load_json


class TestSupport(TestCase):

    def test_wavread(self):
        fn = sound_file_path('beijing_f3_50_a.wav')
        samples, samples_int, Fs = wavread(fn)
        expected = load_json(os.path.join('helpers', 'beijing_f3_50_a-wavread-expected'))
        self.assertEqual(Fs, expected['Fs'])
        self.assertAllClose(samples, expected['y'], rtol=1e-05, atol=1e-08)

    def test_wavread_formats(self):
        # 16-bit PCM file should be read correctly
        fn = data_file_path(os.path.join('helpers', 'wav-formats', 'pcm-16bit.wav'))
        samples, samples_int, Fs = wavread(fn)
        # Other WAV file formats should raise IOError
        with self.assertRaisesRegex(IOError, 'Input WAV file must be in 16-bit integer PCM format'):
            fn = data_file_path(os.path.join('helpers', 'wav-formats', 'pcm-8bit.wav'))
            samples, samples_int, Fs = wavread(fn)
        with self.assertRaisesRegex(IOError, 'Input WAV file must be in 16-bit integer PCM format'):
            fn = data_file_path(os.path.join('helpers', 'wav-formats', 'pcm-32bit.wav'))
            samples, samples_int, Fs = wavread(fn)
        with self.assertRaisesRegex(IOError, 'Input WAV file must be in 16-bit integer PCM format'):
            fn = data_file_path(os.path.join('helpers', 'wav-formats', 'float-32bit.wav'))
            samples, samples_int, Fs = wavread(fn)
        with self.assertRaisesRegex(IOError, 'Input WAV file must be in 16-bit integer PCM format'):
            fn = data_file_path(os.path.join('helpers', 'wav-formats', 'float-64bit.wav'))
            samples, samples_int, Fs = wavread(fn)
        # SciPy does not support 24-bit PCM format
        with self.assertRaisesRegex(ValueError, 'Unsupported bit depth: the wav file has 24-bit data.'):
            fn = data_file_path(os.path.join('helpers', 'wav-formats', 'pcm-24bit.wav'))
            samples, samples_int, Fs = wavread(fn)

    def test_round_half_away_from_zero(self):
        self.assertEqual(round_half_away_from_zero(3.5), 4)
        self.assertEqual(round_half_away_from_zero(3.2), 3)
        self.assertEqual(round_half_away_from_zero(-2.7), -3)
        self.assertEqual(round_half_away_from_zero(-4.3), -4)

    def test_remove_empty_lines_from_file(self):
        # Copy test file and remove extra newlines from it
        fn = 'extra_newlines.txt'
        t = self.tmpdir()
        tmp_path = os.path.join(t, fn)
        shutil.copy(data_file_path(os.path.join('helpers', fn)), tmp_path)
        remove_empty_lines_from_file(tmp_path)
        # Read lines from original test file
        with open(data_file_path(os.path.join('helpers', fn))) as f:
            lines_orig = f.readlines()
        # Read lines from copy with extra newlines removed
        with open(tmp_path) as f:
            lines_rm = f.readlines()
        # Original file should be longer than copy with extra newslines removed
        self.assertTrue(len(lines_orig) > len(lines_rm))
        # Original and copy should match except for the removed newlines
        idx = 0
        for line_orig in lines_orig:
            if line_orig.rstrip():
                self.assertEqual(line_orig, lines_rm[idx])
                idx += 1
        # Copy should not contain any extra information
        self.assertEqual(idx, len(lines_rm))

    def test_convert_boolean_for_praat(self):
        self.assertEqual(convert_boolean_for_praat(True), "yes")
        self.assertEqual(convert_boolean_for_praat(False), "no")
        with self.assertRaisesRegex(ValueError, 'Input must be a Boolean'):
            convert_boolean_for_praat(42)
