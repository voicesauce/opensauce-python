import contextlib
import filecmp
import os
import textwrap
import numpy as np
from shutil import copytree
from subprocess import Popen, PIPE

from opensauce.__main__ import CLI

from test.support import TestCase, data_file_path, py2, parameterize


class TestOldCLI(TestCase):

    def test_default_setup(self):
        tmp = self.tmpdir()

        def d(fn):
            return os.path.join(tmp, fn)
        os.mkdir(d('output'))
        copytree('defaults', d('defaults'))
        p = Popen(['python', 'opensauce/process.py',
                        '-i', d('defaults/sounds'),
                        '-o', d('output'),
                        '-s', d('defaults/settings/default.csv'),
                        '-p', d('defaults/parameters/default.csv'),
                        ],
                    stdout=PIPE,
                    )
        # For now, just ignore the output.
        p.stdout.read()
        rc = p.wait()
        self.assertEqual(rc, 0)
        # f0 calculated by command from process.py
        f0 = np.loadtxt(d('defaults/sounds/cant_c5_19a.f0'))
        # f0 loaded from data
        f0_data = np.loadtxt(data_file_path('cant_c5_19a.f0'))
        # Check that calculated f0 and data f0 are "close"
        self.assertTrue(np.allclose(f0, f0_data))


@parameterize
class TestCLI(TestCase):

    def test_m(self):
        here = os.path.dirname(os.path.dirname(__file__))
        here = here if here else '.'
        p = Popen(['python', '-m', 'opensauce'], cwd=here,
                  stdout=PIPE,
                  stderr=PIPE,
                  universal_newlines=True,
                  )
        out, err = p.communicate()
        self.assertEqual(out, '')
        # XXX assumes python is python2.  Fix?
        self.assertIn('too few arguments', err)
        self.assertEqual(p.returncode, 2)

    def _CLI_output(self, args):
        with self.captured_output('stdout') as sout:
            CLI(args).process()
        lines = sout.getvalue().splitlines()
        return [l.split('\t') for l in lines]

    def test_snackF0(self):
        lines = self._CLI_output([
            data_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            ])
        self.assertEqual(len(lines), 589)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 101)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 209)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 119)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 159)

    def test_ignore_label(self):
        lines = self._CLI_output([
            '--measurements', 'snackF0',
            '--ignore-label', 'C2',
            data_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 589 - 119)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 101)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 209)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 159)

    def test_ignore_multiple_labels(self):
        lines = self._CLI_output([
            '--measurements', 'snackF0',
            '--ignore-label', 'C2',
            '--ignore-label', 'V1',
            data_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 589 - 119 - 209)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 101)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 159)

    def test_include_empty_lables(self):
        lines = self._CLI_output([
            '--measurements', 'snackF0',
            '--include-empty-labels',
            data_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 2347)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 101)

    def test_no_textgrid(self):
        lines = self._CLI_output([
            '--measurements', 'snackF0',
            '--no-textgrid',
            data_file_path('beijing_f3_50_a.wav')
            ])
        # The textgrid output has a repeated frame offset at the end and
        # beginning of each block.  Since there are six blocks (including the
        # ones with blank labels) in this sample, there are five more records
        # in the --include-empty-labels case above than there are here, where
        # we have no repeated frames.
        self.assertEqual(len(lines), 2342)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)

    def test_multiple_input_files(self):
        lines = self._CLI_output([
            '--measurements', 'snackF0',
            '--include-empty-labels',
            data_file_path('beijing_f3_50_a.wav'),
            data_file_path('beijing_m5_17_c.wav'),
            data_file_path('hmong_f4_24_d.wav'),
            ])
        self.assertEqual(len(lines), 6121)
        # The first of these is one less than the number lines in the single
        # file equivalent test above because there we were counting the header
        # line and here we are not.
        self.assertEqual(len([x for x in lines
                              if 'beijing_f3_50_a.wav' in x]), 2346)
        self.assertEqual(len([x for x in lines
                              if 'beijing_m5_17_c.wav' in x]), 1673)
        self.assertEqual(len([x for x in lines
                              if 'hmong_f4_24_d.wav' in x]), 2101)

    @contextlib.contextmanager
    def assertArgparseError(self, expected_regex, expected_regex_3=None):
        with self.assertRaises(SystemExit):
            with self.captured_output('stderr') as out:
                yield out
        msg = out.getvalue()
        if not py2 and expected_regex_3 is not None:
            expected_regex = expected_regex_3
        for regex in expected_regex:
            self.assertRegex(msg, regex)

    def test_at_least_one_input_file_required(self):
        with self.assertArgparseError(['too few arguments'], ['required', 'wavfile']):
            CLI([])

    def test_at_least_one_measurement_required(self):
        with self.assertArgparseError(['[Nn]o measurements']):
            CLI([data_file_path('beijing_f3_50_a.wav')])

    def _make_file(self, lines):
        lines = textwrap.dedent(lines.lstrip('\n'))
        tmp = self.tmpdir()
        settingsfn = os.path.join(tmp, 'settings')
        with open(settingsfn, 'w') as f:
            f.write(lines)
        return settingsfn

    def test_settings(self):
        settingsfn = self._make_file("""
            include-empty-labels
            ignore-label C2
            """)
        lines = self._CLI_output([
            '--settings', settingsfn,
            data_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            ])
        self.assertEqual(len(lines), 2347 - 119)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)

    def test_settings_default_file(self):
        settingsfn = self._make_file("""
            include-empty-labels
            """)
        with self.patch(CLI, 'settings_locs', [settingsfn]):
            lines = self._CLI_output([
                data_file_path('beijing_f3_50_a.wav'),
                '--measurements', 'snackF0',
                ])
            self.assertEqual(len(lines), 2347)

    def test_settings_option_invalid_in_settings_file(self):
        settingsfn = self._make_file("""
            include-empty-labels
            settings somefile
            ignore-lables
            """)
        with self.assertArgparseError(['settings', settingsfn]):
            CLI(['--settings', settingsfn])

    def test_measurements_in_settings(self):
        settingsfn = self._make_file("""
            measurements snackF0
            include-empty-labels
            """)
        lines = self._CLI_output([
            '--settings', settingsfn,
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 2347)
        self.assertIn('snackF0', lines[0])
        self.assertEqual(len(lines[1]), 6)

    def test_measurements_cant_be_last_line_in_settings(self):
        # This is because it would eat filenames if it was and no other options
        # were specified on the command line before the filenames.
        settingsfn = self._make_file("""
            include-empty-labels
            measurements snackF0
            """)
        with self.assertArgparseError(['measurements', settingsfn, 'last']):
            CLI(['--settings', settingsfn])

    def test_invalid_measurement_rejected(self):
        # This is because it would eat filenames if it was and no other options
        # were specified on the command line before the filenames.
        settingsfn = self._make_file("""
            measurements thereisnosuchmeasurement
            include-empty-labels
            """)
        with self.assertArgparseError(['thereisnosuchmeasurement']):
            CLI(['--settings', settingsfn])

    def test_multiple_measurements(self):
        lines = self._CLI_output([
            data_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'shrF0', 'snackF0', 'SHR',
            ])
        self.assertEqual(len(lines), 589)
        self.assertEqual(lines[0][-3:], ['shrF0', 'snackF0', 'SHR'])
        self.assertEqual(len(lines[1]), 8)

    def test_measurements_from_file(self):
        measurefn = self._make_file("""
            snackF0
            shrF0
            """)
        lines = self._CLI_output([
            "--default-measurements-file", measurefn,
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 589)
        self.assertEqual(lines[0][-2:], ['snackF0', 'shrF0'])
        self.assertEqual(len(lines[1]), 7)

    def test_measurements_default_file(self):
        measurefn = self._make_file("""
            snackF0
            shrF0
            """)
        with self.patch(CLI, 'measurements_locs', [measurefn]):
            lines = self._CLI_output([
                data_file_path('beijing_f3_50_a.wav'),
                ])
        self.assertEqual(len(lines), 589)
        self.assertEqual(len(lines[1]), 7)

    def test_invalid_measurements_from_file(self):
        measurefn = self._make_file("""
            nosuchmeasurement
            """)
        with self.assertArgparseError(['nosuchmeasurement', '0', measurefn]):
            CLI(['-m', measurefn, 'NA'])

    def test_alternate_F0(self):
        lines = self._CLI_output([
            '--F0', 'shrF0',
            '--include-F0',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 589)
        self.assertEqual(lines[0][-1:], ['shrF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(lines[100],
            ['beijing_f3_50_a.wav', 'C1', '0.766', '0.866', '865.000',
             '230.220'])

    def test_invalid_F0(self):
        with self.assertArgparseError(['nosuchpitch']):
            CLI(['--f0', 'nosuchpitch'])

    def test_output_filepath(self):
        tmp = self.tmpdir()
        outfile = os.path.join(tmp, 'output.txt')
        CLI(['--include-f0',
             '-o', outfile,
             data_file_path('beijing_f3_50_a.wav')]).process()
        with open(outfile) as f:
            self.assertEqual(len(list(f.readlines())), 589)

    # XXX There is as yet no confirmation that the values being tested against
    # here are accurate; these tests just prove the options have *some* effect.

    line100_prefix = ['beijing_f3_50_a.wav', 'C1', '0.766', '0.866', '865.000']

    def _check_algos(self, algo_list):
        self.assertEqual(sorted(algo_list), sorted(CLI._valid_f0), "Tests we have do not match tests we need")

    pitch_algo1_params = {
        'snackF0': ('snackF0', 589, '216.184'),
        'shrF0': ('shrF0', 589, '230.220'),
        }

    def test_have_default_settings_tests(self):
        self._check_algos(self.pitch_algo1_params.keys())

    def pitch_algo1_as_default_settings(self, pitch_algo, line_count, v100):
        lines = self._CLI_output([
            '--f0', pitch_algo,
            '--include-F0',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), line_count)
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo2_params = CLI._valid_f0

    def pitch_algo2_as_frame_shift(self, pitch_algo):
        lines = self._CLI_output([
            '--f0', pitch_algo,
            '--include-F0',
            '--frame-shift', '2',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 297)

    pitch_algo3_params = {
        'snackF0': ('snackF0', '220.058'),
        'shrF0': ('shrF0', '238.159'),
        }

    def test_have_window_size_tests(self):
        self._check_algos(self.pitch_algo3_params.keys())

    def pitch_algo3_as_window_size(self, pitch_algo, v100):
        lines = self._CLI_output([
            '--f0', pitch_algo,
            '--include-F0',
            '--window-size', '10',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo4_params = {
        'snackF0': ('snackF0', '0.000'),
        'shrF0': ('shrF0', '251.043'),
        }

    def test_have_min_f0_tests(self):
        self._check_algos(self.pitch_algo4_params.keys())

    def pitch_algo4_as_min_f0(self, pitch_algo, v100):
        lines = self._CLI_output([
            '--f0', pitch_algo,
            '--include-F0',
            '--min-f0', '400',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo5_params = {
        'snackF0': ('snackF0', '106.820'),
        'shrF0': ('shrF0', '100.512'),
        }

    def test_have_max_f0_tests(self):
        self._check_algos(self.pitch_algo5_params.keys())

    def pitch_algo5_as_max_f0(self, pitch_algo, v100):
        lines = self._CLI_output([
            '--f0', pitch_algo,
            '--include-F0',
            '--max-f0', '200',
            data_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])
