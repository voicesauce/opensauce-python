import os
import shutil
import numpy as np

from sys import platform

from opensauce.helpers import wavread
from opensauce.soundfile import SoundFile

from test.support import TestCase, data_file_path


class TestSoundFile(TestCase):

    def test_bad_wav_path(self):
        with self.assertRaisesRegex(IOError, 'nosuchfile'):
            SoundFile('nosuchfile')

    def test_load_wav_file(self):
        spath = data_file_path('beijing_f3_50_a.wav')
        s = SoundFile(spath)
        self.assertEqual(s.wavpath, spath)
        data, fs = wavread(spath)
        np.testing.assert_array_equal(data, s.wavdata)
        self.assertEqual(fs, s.fs)

    def test_no_textgrid(self):
        fn = 'beijing_f3_50_a.wav'
        t = self.tmpdir()
        spath = os.path.join(t, fn)
        shutil.copy(data_file_path(fn), spath)
        s = SoundFile(spath)
        self.assertEqual(s.textgrid, None)
        with self.assertRaises(ValueError) as cx:
            s.textgrid_intervals
        msg = str(cx.exception)

        # HACK: On Windows systems, the number of backslashes is doubled
        if platform == 'win32' or platform == 'cygwin':
            msg = msg.replace('\\\\', '\\')

        self.assertIn(os.path.basename(fn)[0], msg)
        self.assertIn(t, msg)
        self.assertIn('TextGrid', msg)

    def test_find_textgrid_using_defaults(self):
        spath = data_file_path('beijing_f3_50_a.wav')
        s = SoundFile(spath)
        self.assertNotEqual(s.textgrid, None)
        # For this test, just make sure this doesn't raise.
        s.textgrid_intervals

    def test_find_textgrid_in_alternate_dir(self):
        wfn = 'beijing_f3_50_a.wav'
        tfn = 'beijing_f3_50_a.TextGrid'
        tmp1 = self.tmpdir()
        tmp2 = self.tmpdir()
        shutil.copy(data_file_path(wfn), tmp1)
        shutil.copy(data_file_path(tfn), tmp2)
        s = SoundFile(os.path.join(tmp1, wfn), tgdir=tmp2)
        self.assertNotEqual(s.textgrid, None)
        self.assertEqual(s.tgpath, os.path.join(tmp2, tfn))

    def test_find_textgrid_using_full_spec(self):
        wfn = 'beijing_f3_50_a.wav'
        tfn = 'beijing_f3_50_a.TextGrid'
        tmp1 = self.tmpdir()
        tmp2 = self.tmpdir()
        shutil.copy(data_file_path(wfn), tmp1)
        newtpath = os.path.join(tmp2, 'foo.bar')
        shutil.copy(data_file_path(tfn), newtpath)
        s = SoundFile(os.path.join(tmp1, wfn), tgdir=tmp2, tgfn='foo.bar')
        self.assertNotEqual(s.textgrid, None)
        self.assertEqual(s.tgpath, newtpath)

    def test_textgrid_intervals(self):
        s = SoundFile(data_file_path('beijing_f3_50_a.wav'))
        expected = (
            ('', 0, 0.7660623496874233),
            ('C1', 0.7660623496874233, 0.865632223379142),
            ('V1', 0.865632223379142, 1.0740775664347026),
            ('C2', 1.0740775664347026, 1.1922586314706678),
            ('V2', 1.1922586314706678, 1.350453757896763),
            ('', 1.350453757896763, 2.34),
            )
        actual = s.textgrid_intervals
        for i in range(len(actual)):
            self.assertEqual(actual[i][0], expected[i][0], 'row %s' % i)
            self.assertAlmostEqual(actual[i][1], expected[i][1], 'elt %s,1' % i)
            self.assertAlmostEqual(actual[i][2], expected[i][2], 'elt %s,2' % i)
