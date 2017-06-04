import os
import shutil
import numpy as np

from opensauce.helpers import wavread, round_half_away_from_zero, remove_empty_lines_from_file

from test.support import TestCase, data_file_path, load_json


class TestSupport(TestCase):

    def test_wavread(self):
        fn = data_file_path('beijing_f3_50_a.wav')
        samples, Fs = wavread(fn)
        expected = load_json('beijing_f3_50_a-wavread-expected')
        self.assertEqual(Fs, expected['Fs'])
        self.assertTrue(np.allclose(samples, expected['y']))

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
        shutil.copy(data_file_path(fn), tmp_path)
        remove_empty_lines_from_file(tmp_path)
        # Read lines from original test file
        with open(data_file_path(fn)) as f:
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
