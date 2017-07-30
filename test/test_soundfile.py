import os
import shutil
import unittest
import numpy as np

from sys import platform

from opensauce.helpers import wavread
from opensauce.soundfile import SoundFile

from test.support import TestCase, parameterize, load_json, data_file_path, sound_file_path, wav_fns


@parameterize
class TestSoundFile(TestCase):

    def test_bad_wav_path(self):
        with self.assertRaisesRegex(IOError, 'nosuchfile'):
            SoundFile('nosuchfile')

    def test_load_wav_file(self):
        spath = sound_file_path('beijing_f3_50_a.wav')
        s = SoundFile(spath)
        self.assertEqual(s.wavpath, spath)
        data, fs = wavread(spath)
        self.assertAllClose(data, s.wavdata)
        self.assertEqual(fs, s.fs)
        self.assertEqual(s.fs, 22050)
        self.assertEqual(s.ns, 51597)
        self.assertEqual(s.ms_len, 2340)
        self.assertIsNone(s.wavdata_rs)
        self.assertIsNone(s.fs_rs)
        self.assertIsNone(s.ns_rs)

    def test_resample_properties(self):
        spath = sound_file_path('beijing_f3_50_a.wav')
        s = SoundFile(spath, resample_freq=16000)
        self.assertEqual(s.wavpath, spath)
        y, fs = wavread(spath)
        self.assertAllClose(y, s.wavdata)
        self.assertEqual(fs, s.fs)
        self.assertEqual(s.fs, 22050)
        self.assertEqual(s.ns, 51597)
        self.assertEqual(s.ms_len, 2340)
        self.assertEqual(s.fs_rs, 16000)
        self.assertEqual(s.ns_rs, 37440)

    @unittest.expectedFailure
    def test_resample_data_against_matlab(self):
        # XXX: This test fails because SciPy is using a different algorithm
        #      for resampling than Matlab.  When the SciPy and Matlab
        #      resampled data are plotted against each other, they look
        #      reasonably similar, so the fact that this test fails is
        #      probably okay.
        for fn in wav_fns:
            s = SoundFile(fn, resample_freq=16000)
            resample_fn = os.path.splitext(os.path.basename(fn))[0] + '-matlab-resample'
            data = load_json(os.path.join('soundfile', resample_fn))
            self.assertAllClose(s.wavdata_rs, data['y_rs'], rtol=1e-01)

    def test_no_textgrid(self):
        fn = 'beijing_f3_50_a.wav'
        t = self.tmpdir()
        spath = os.path.join(t, fn)
        shutil.copy(sound_file_path(fn), spath)
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
        spath = sound_file_path('beijing_f3_50_a.wav')
        s = SoundFile(spath)
        self.assertNotEqual(s.textgrid, None)
        # For this test, just make sure this doesn't raise.
        s.textgrid_intervals

    def test_find_textgrid_in_alternate_dir(self):
        wfn = 'beijing_f3_50_a.wav'
        tfn = 'beijing_f3_50_a.TextGrid'
        tmp1 = self.tmpdir()
        tmp2 = self.tmpdir()
        shutil.copy(sound_file_path(wfn), tmp1)
        shutil.copy(sound_file_path(tfn), tmp2)
        s = SoundFile(os.path.join(tmp1, wfn), tgdir=tmp2)
        self.assertNotEqual(s.textgrid, None)
        self.assertEqual(s.tgpath, os.path.join(tmp2, tfn))

    def test_find_textgrid_using_full_spec(self):
        wfn = 'beijing_f3_50_a.wav'
        tfn = 'beijing_f3_50_a.TextGrid'
        tmp1 = self.tmpdir()
        tmp2 = self.tmpdir()
        shutil.copy(sound_file_path(wfn), tmp1)
        newtpath = os.path.join(tmp2, 'foo.bar')
        shutil.copy(sound_file_path(tfn), newtpath)
        s = SoundFile(os.path.join(tmp1, wfn), tgdir=tmp2, tgfn='foo.bar')
        self.assertNotEqual(s.textgrid, None)
        self.assertEqual(s.tgpath, newtpath)

    intervals_ascii = (
        ('', 0, 0.7660623496874233),
        ('C1', 0.7660623496874233, 0.865632223379142),
        ('V1', 0.865632223379142, 1.0740775664347026),
        ('C2', 1.0740775664347026, 1.1922586314706678),
        ('V2', 1.1922586314706678, 1.350453757896763),
        ('', 1.350453757896763, 2.34),
        )

    intervals_utf8 = (
        (u'\u30cb\u30b3\u30cb\u30b3', 0, 0.7660623496874233),
        ('C1', 0.7660623496874233, 0.865632223379142),
        ('V1', 0.865632223379142, 1.0740775664347026),
        ('C2', 1.0740775664347026, 1.1922586314706678),
        ('V2', 1.1922586314706678, 1.350453757896763),
        (u'\u306b\u3083\u3042', 1.350453757896763, 2.34),
        )

    intervals_utf16 = (
        (u'\u3042\u306f\u306f\u306f', 0, 0.7660623496874233),
        ('C1', 0.7660623496874233, 0.865632223379142),
        ('V1', 0.865632223379142, 1.0740775664347026),
        ('C2', 1.0740775664347026, 1.1922586314706678),
        ('V2', 1.1922586314706678, 1.350453757896763),
        (u'\u304a\u3063\u3068\u3063\u3068', 1.350453757896763, 2.34),
        )

    example_params = {'typical_ascii': ('beijing_f3_50_a', intervals_ascii), 'texttier_ascii': ('beijing_f3_50_a-texttier', intervals_ascii), 'utf8': ('beijing_f3_50_a-utf8', intervals_utf8), 'utf16': ('beijing_f3_50_a-utf16', intervals_utf16)}

    def example_as_textgrid_input(self, basename, expected):
        wav_fn = 'beijing_f3_50_a.wav'
        t = self.tmpdir()
        tmp_path = os.path.join(t, wav_fn)
        shutil.copy(sound_file_path(wav_fn), tmp_path)
        shutil.copy(data_file_path(os.path.join('soundfile', basename + '.TextGrid')), os.path.join(t, 'beijing_f3_50_a.TextGrid'))

        s = SoundFile(tmp_path)
        actual = s.textgrid_intervals
        for i in range(len(actual)):
            self.assertEqual(actual[i][0], expected[i][0], 'row %s' % i)
            self.assertAlmostEqual(actual[i][1], expected[i][1], msg='elt %s,1' % i)
            self.assertAlmostEqual(actual[i][2], expected[i][2], msg='elt %s,2' % i)
