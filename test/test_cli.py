import contextlib
import os
import sys
import textwrap
import unittest
import numpy as np
from sys import platform
from shutil import copytree
from subprocess import Popen, PIPE

from opensauce.__main__ import CLI

from opensauce.snack import sformant_names

from test.support import TestCase, data_file_path, sound_file_path, py2, parameterize, CLI_output


class TestCommandIO(TestCase):

    def _make_file(self, lines):
        lines = textwrap.dedent(lines.lstrip('\n'))
        tmp = self.tmpdir()
        settingsfn = os.path.join(tmp, 'settings')
        with open(settingsfn, 'w') as f:
            f.write(lines)
        return settingsfn

    def test_m(self):
        here = os.path.dirname(os.path.dirname(__file__))
        here = here if here else '.'
        p = Popen([sys.executable, '-m', 'opensauce'], cwd=here,
                  stdout=PIPE,
                  stderr=PIPE,
                  universal_newlines=True,
                  )
        out, err = p.communicate()
        self.assertEqual(out, '')
        if py2:
            self.assertIn('too few arguments', err)
        else:
            self.assertIn('the following arguments are required', err)
        self.assertEqual(p.returncode, 2)

    def test_ignore_label(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--ignore-label', 'C2',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585 - 118)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_ignore_multiple_labels(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--ignore-label', 'C2',
            '--ignore-label', 'V1',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585 - 118 - 208)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_include_empty_labels(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--include-empty-labels',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)

    def test_no_f0_column(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'SHR',
            '--no-f0-column',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines[0] if 'F0' in x]), 0)

    def test_include_f0_column(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'SHR',
            '--include-f0-column',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 7)
        self.assertEqual(len([x for x in lines[0] if 'F0' in x]), 1)

    def test_no_formant_cols(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'SHR',
            '--no-formant-cols',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines[0] if 'pF' in x]), 0)
        self.assertEqual(len([x for x in lines[0] if 'pB' in x]), 0)

    def test_include_formant_cols(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'praatFormants',
            '--include-formant-cols',
            '--num-formants', '4',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        formant_col_names = ['pF1', 'pF2', 'pF3', 'pF4',
                             'pB1', 'pB2', 'pB3', 'pB4']
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 13)
        self.assertListEqual(lines[0][-8:], formant_col_names)

    def test_no_textgrid(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--no-textgrid',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 3)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)

    def test_use_textgrid(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_use_textgrid_but_doesnt_exist(self):
        lines = CLI_output(self, '\t', [
            data_file_path(os.path.join('cli', 'beijing_f3_50_a.wav')),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2342)
        self.assertEqual(len(lines[0]), 6)
        self.assertIn('Found no TextGrid for', lines[1][0])
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)

    def test_no_labels(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--no-labels',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav')
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 3)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)

    def test_include_labels(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--include-labels',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_multiple_input_files(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--include-empty-labels',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            sound_file_path('beijing_m5_17_c.wav'),
            sound_file_path('hmong_f4_24_d.wav'),
            ])
        self.assertEqual(len(lines), 6100)
        # The first of these is one less than the number lines in the single
        # file equivalent test above because there we were counting the header
        # line and here we are not.
        self.assertEqual(len([x for x in lines
                              if 'beijing_f3_50_a.wav' in x]), 2340)
        self.assertEqual(len([x for x in lines
                              if 'beijing_m5_17_c.wav' in x]), 1667)
        self.assertEqual(len([x for x in lines
                              if 'hmong_f4_24_d.wav' in x]), 2092)

    def test_at_least_one_input_file_required(self):
        with self.assertArgparseError(['too few arguments'], ['required', 'wavfile']):
            CLI([])

    def test_at_least_one_measurement_required(self):
        with self.assertArgparseError(['[Nn]o measurements']):
            CLI([sound_file_path('beijing_f3_50_a.wav')])

    def test_settings(self):
        settingsfn = self._make_file("""
            include-empty-labels
            ignore-label C2
            """)
        lines = CLI_output(self, '\t', [
            '--settings', settingsfn,
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341 - 118)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)

    def test_settings_default_file(self):
        settingsfn = self._make_file("""
            include-empty-labels
            """)
        with self.patch(CLI, 'settings_locs', [settingsfn]):
            lines = CLI_output(self, '\t', [
                sound_file_path('beijing_f3_50_a.wav'),
                '--measurements', 'snackF0',
                '--no-output-settings',
                ])
            self.assertEqual(len(lines), 2341)

    def test_settings_option_invalid_in_settings_file(self):
        settingsfn = self._make_file("""
            include-empty-labels
            settings somefile
            ignore-label
            """)
        with self.assertArgparseError(['settings', settingsfn]):
            CLI(['--settings', settingsfn])

    def test_measurements_in_settings(self):
        settingsfn = self._make_file("""
            measurements snackF0
            include-empty-labels
            """)
        lines = CLI_output(self, '\t', [
            '--settings', settingsfn,
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 2341)
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
        settingsfn = self._make_file("""
            measurements thereisnosuchmeasurement
            include-empty-labels
            """)
        with self.assertArgparseError(['thereisnosuchmeasurement']):
            CLI(['--settings', settingsfn])

    def test_multiple_measurements(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'shrF0', 'snackF0', 'SHR',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-3:], ['shrF0', 'snackF0', 'SHR'])
        self.assertEqual(len(lines[1]), 8)

    def test_measurements_from_file(self):
        measurefn = self._make_file("""
            snackF0
            shrF0
            """)
        lines = CLI_output(self, '\t', [
            '--default-measurements-file', measurefn,
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-2:], ['snackF0', 'shrF0'])
        self.assertEqual(len(lines[1]), 7)

    def test_measurements_default_file(self):
        measurefn = self._make_file("""
            snackF0
            shrF0
            """)
        with self.patch(CLI, 'measurements_locs', [measurefn]):
            lines = CLI_output(self, '\t', [
                '--no-output-settings',
                sound_file_path('beijing_f3_50_a.wav'),
                ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-2:], ['snackF0', 'shrF0'])
        self.assertEqual(len(lines[1]), 7)

    def test_invalid_measurements_from_file(self):
        measurefn = self._make_file("""
            nosuchmeasurement
            """)
        with self.assertArgparseError(['nosuchmeasurement', '0', measurefn]):
            CLI(['-m', measurefn, 'NA'])

    def test_output_filepath(self):
        tmp = self.tmpdir()
        outfile = os.path.join(tmp, 'output.txt')
        CLI(['--include-f0-column',
             '-o', outfile,
             sound_file_path('beijing_f3_50_a.wav')]).process()

        with open(outfile) as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 585)

    def test_output_delimiter_tab(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--no-textgrid',
            '--output-delimiter', 'tab',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])

    def test_output_delimiter_comma(self):
        lines = CLI_output(self, ',', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--no-textgrid',
            '--output-delimiter', 'comma',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])

    def test_output_settings_stdout(self):
        # Make sure there isn't already a settings file
        # If so, remove it
        if os.path.isfile('stdout.settings'):
            os.remove('stdout.settings')
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertTrue(os.path.isfile('stdout.settings'))
        # Check generated settings file
        with open('stdout.settings') as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 33)
            self.assertEqual(slines[0].strip(), '--measurements snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 33)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-f0-column')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)
        # Cleanup
        os.remove('stdout.settings')

    def test_output_settings_with_output_filepath(self):
        tmp = self.tmpdir()
        outfile = os.path.join(tmp, 'output.txt')
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            '-o', outfile,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        settings_path = outfile.split('.')[0] + '.settings'
        self.assertTrue(os.path.isfile(settings_path))
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 33)
            self.assertEqual(slines[0].strip(), '--measurements snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 33)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-f0-column')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)

    def test_no_output_settings_stdout(self):
        if os.path.isfile('stdout.settings'):
            os.remove('stdout.settings')
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertFalse(os.path.isfile('stdout.settings'))

    def test_no_output_settings_with_output_filepath(self):
        tmp = self.tmpdir()
        outfile = os.path.join(tmp, 'output.txt')
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            '-o', outfile,
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        settings_path = outfile.split('.')[0] + '.settings'
        self.assertFalse(os.path.isfile(settings_path))

    def test_output_settings_path_stdout(self):
        tmp = self.tmpdir()
        settings_path = os.path.join(tmp, 'output.settings')
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            '--output-settings-path', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 33)
            self.assertEqual(slines[0].strip(), '--measurements snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 33)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-f0-column')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)

    def test_output_settings_path_with_output_filepath(self):
        tmp = self.tmpdir()
        outfile = os.path.join(tmp, 'output.txt')
        settings_path = outfile.split('.')[0] + '_unittest.settings'
        lines = CLI_output(self, '\t', [
            '--include-f0-column',
            '-o', outfile,
            '--output-settings-path', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertTrue(os.path.isfile(settings_path))
        self.assertFalse(os.path.isfile(outfile.split('.')[0] + '.settings'))
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 33)
            self.assertEqual(slines[0].strip(), '--measurements snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 33)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-f0-column')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)

    def test_output_settings_check_consistency(self):
        # Output from using the generated settings file should match
        # the original CLI execution
        tmp = self.tmpdir()
        settings_path = os.path.join(tmp, 'output.settings')
        lines_stdout = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--no-labels',
            '--output-settings-path', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        lines_sfile = CLI_output(self, '\t', [
            '--settings', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])

        self.assertEqual(len(lines_stdout), 585)
        self.assertEqual(len(lines_stdout[0]), 3)
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 33)
            self.assertEqual(slines[0].strip(), '--measurements snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 33)
            self.assertEqual(sum([1 for l in slines if l.startswith('--use-textgrid')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--no-labels')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)
        # Check consistency of output using generated settings file
        self.assertEqual(lines_sfile, lines_stdout)

    def test_output_settings_check_consistency_alternate_parameters(self):
        # Output from using the generated settings file should match
        # the original CLI execution
        tmp = self.tmpdir()
        settings_path = os.path.join(tmp, 'output.settings')
        lines_stdout = CLI_output(self, '\t', [
            '--measurements', 'praatFormants',
            '--include-f0-column',
            '--no-textgrid',
            '--time-starts-at-frameshift',
            '--include-interval-endpoint',
            '--kill-octave-jumps',
            '--interpolate',
            '--smooth',
            '--smooth-bandwidth', '10',
            '--output-settings-path', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        lines_sfile = CLI_output(self, '\t', [
            '--settings', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])

        self.assertEqual(len(lines_stdout), 2342)
        self.assertEqual(len(lines_stdout[0]), 11)
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 37)
            self.assertEqual(slines[0].strip(), '--measurements praatFormants snackF0')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 37)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-f0-column')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--no-textgrid')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--time-starts-at-frameshift')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-interval-endpoint')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 2)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth-bandwidth')]), 1)
        # Check consistency of output using generated settings file
        self.assertEqual(lines_sfile, lines_stdout)

    def test_output_settings_check_consistency_more_alternate_parameters(self):
        # Output from using the generated settings file should match
        # the original CLI execution
        tmp = self.tmpdir()
        settings_path = os.path.join(tmp, 'output.settings')
        lines_stdout = CLI_output(self, '\t', [
            '--measurements', 'snackF0',
            '--include-formant-cols',
            '--use-textgrid',
            '--include-empty-labels',
            '--output-settings-path', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        lines_sfile = CLI_output(self, '\t', [
            '--settings', settings_path,
            sound_file_path('beijing_f3_50_a.wav'),
            ])

        self.assertEqual(len(lines_stdout), 2341)
        self.assertEqual(len(lines_stdout[0]), 14)
        # Check generated settings file
        with open(settings_path) as f:
            slines = f.readlines()
            self.assertEqual(len(slines), 34)
            self.assertEqual(slines[0].strip(), '--measurements snackF0 praatFormants')
            self.assertEqual(sum([1 for l in slines if l.startswith('--')]), 34)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-formant-cols')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--use-textgrid')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--include-empty-labels')]), 1)
            self.assertEqual(sum([1 for l in slines if l.startswith('--kill-octave-jumps')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--interpolate')]), 0)
            self.assertEqual(sum([1 for l in slines if l.startswith('--smooth')]), 0)
        # Check consistency of output using generated settings file
        self.assertEqual(lines_sfile, lines_stdout)

    def test_time_starts_at_zero_no_textgrid(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--no-textgrid',
            '--time-starts-at-zero',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 3)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)
        self.assertEqual(lines[1][1], '0')
        self.assertEqual(lines[-1][1], '2339')

    def test_time_starts_at_zero_use_textgrid(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--include-empty-labels',
            '--time-starts-at-zero',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 6)
        C1_lines = [x for x in lines if 'C1' in x]
        V1_lines = [x for x in lines if 'V1' in x]
        C2_lines = [x for x in lines if 'C2' in x]
        V2_lines = [x for x in lines if 'V2' in x]
        self.assertEqual(len(C1_lines), 100)
        self.assertEqual(len(V1_lines), 208)
        self.assertEqual(len(C2_lines), 118)
        self.assertEqual(len(V2_lines), 158)
        self.assertEqual(lines[1][-2], '0')
        self.assertEqual(lines[-1][-2], '2339')
        self.assertEqual(C1_lines[0][-2], '766')
        self.assertEqual(C1_lines[-1][-2], '865')
        self.assertEqual(V1_lines[0][-2], '866')
        self.assertEqual(V1_lines[-1][-2], '1073')
        self.assertEqual(C2_lines[0][-2], '1074')
        self.assertEqual(C2_lines[-1][-2], '1191')
        self.assertEqual(V2_lines[0][-2], '1192')
        self.assertEqual(V2_lines[-1][-2], '1349')

    def test_time_starts_at_frameshift_no_textgrid(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--no-textgrid',
            '--time-starts-at-frameshift',
            '--frame-shift', '1',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 3)
        self.assertEqual(lines[0], ['Filename', 't_ms', 'snackF0'])
        self.assertEqual(len([x for x in lines if 'C1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 0)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 0)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 0)
        self.assertEqual(lines[1][1], '1')
        self.assertEqual(lines[-1][1], '2340')

    def test_time_starts_at_frameshift_use_textgrid(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--include-empty-labels',
            '--time-starts-at-frameshift',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 6)
        C1_lines = [x for x in lines if 'C1' in x]
        V1_lines = [x for x in lines if 'V1' in x]
        C2_lines = [x for x in lines if 'C2' in x]
        V2_lines = [x for x in lines if 'V2' in x]
        self.assertEqual(len(C1_lines), 100)
        self.assertEqual(len(V1_lines), 208)
        self.assertEqual(len(C2_lines), 118)
        self.assertEqual(len(V2_lines), 158)
        self.assertEqual(lines[1][-2], '1')
        self.assertEqual(lines[-1][-2], '2340')
        self.assertEqual(C1_lines[0][-2], '767')
        self.assertEqual(C1_lines[-1][-2], '866')
        self.assertEqual(V1_lines[0][-2], '867')
        self.assertEqual(V1_lines[-1][-2], '1074')
        self.assertEqual(C2_lines[0][-2], '1075')
        self.assertEqual(C2_lines[-1][-2], '1192')
        self.assertEqual(V2_lines[0][-2], '1193')
        self.assertEqual(V2_lines[-1][-2], '1350')

    def test_exclude_interval_endpoint(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--include-empty-labels',
            '--time-starts-at-zero',
            '--exclude-interval-endpoint',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(len(lines[1]), 6)
        C1_lines = [x for x in lines if 'C1' in x]
        V1_lines = [x for x in lines if 'V1' in x]
        C2_lines = [x for x in lines if 'C2' in x]
        V2_lines = [x for x in lines if 'V2' in x]
        self.assertEqual(len(C1_lines), 100)
        self.assertEqual(len(V1_lines), 208)
        self.assertEqual(len(C2_lines), 118)
        self.assertEqual(len(V2_lines), 158)
        self.assertEqual(lines[1][-2], '0')
        self.assertEqual(lines[-1][-2], '2339')
        self.assertEqual(C1_lines[0][-2], '766')
        self.assertEqual(C1_lines[-1][-2], '865')
        self.assertEqual(V1_lines[0][-2], '866')
        self.assertEqual(V1_lines[-1][-2], '1073')
        self.assertEqual(C2_lines[0][-2], '1074')
        self.assertEqual(C2_lines[-1][-2], '1191')
        self.assertEqual(V2_lines[0][-2], '1192')
        self.assertEqual(V2_lines[-1][-2], '1349')

    def test_include_interval_endpoint(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--use-textgrid',
            '--include-empty-labels',
            '--time-starts-at-zero',
            '--include-interval-endpoint',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2347)
        self.assertEqual(len(lines[1]), 6)
        C1_lines = [x for x in lines if 'C1' in x]
        V1_lines = [x for x in lines if 'V1' in x]
        C2_lines = [x for x in lines if 'C2' in x]
        V2_lines = [x for x in lines if 'V2' in x]
        self.assertEqual(len(C1_lines), 101)
        self.assertEqual(len(V1_lines), 209)
        self.assertEqual(len(C2_lines), 119)
        self.assertEqual(len(V2_lines), 159)
        self.assertEqual(lines[1][-2], '0')
        self.assertEqual(lines[-1][-2], '2340')
        self.assertEqual(C1_lines[0][-2], '766')
        self.assertEqual(C1_lines[-1][-2], '866')
        self.assertEqual(V1_lines[0][-2], '866')
        self.assertEqual(V1_lines[-1][-2], '1074')
        self.assertEqual(C2_lines[0][-2], '1074')
        self.assertEqual(C2_lines[-1][-2], '1192')
        self.assertEqual(V2_lines[0][-2], '1192')
        self.assertEqual(V2_lines[-1][-2], '1350')

    def test_default_NaN(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0', 'shrF0', 'SHR',
            '--include-empty-labels',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(lines[0][-3:], ['snackF0', 'shrF0', 'SHR'])
        self.assertEqual(len(lines[1]), 8)
        self.assertEqual(lines[1][-2:], ['NaN', 'NaN'])
        self.assertEqual(lines[-1][-3:], ['NaN', 'NaN', 'NaN'])

    def test_alternate_NaN(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0', 'shrF0', 'SHR',
            '--include-empty-labels',
            '--NaN', 'mylabel',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(lines[0][-3:], ['snackF0', 'shrF0', 'SHR'])
        self.assertEqual(len(lines[1]), 8)
        self.assertEqual(lines[1][-2:], ['mylabel', 'mylabel'])
        self.assertEqual(lines[-1][-3:], ['mylabel', 'mylabel', 'mylabel'])

    def test_resample_negative_integer(self):
        with self.assertRaisesRegex(ValueError, 'Resample frequency must be positive'):
            lines = CLI_output(self, '\t', [
                sound_file_path('beijing_f3_50_a.wav'),
                '--measurements', 'snackF0',
                '--resample-freq', '-5',
                ])

    def test_resample_output(self):
        spath = sound_file_path('beijing_f3_50_a.wav')
        lines = CLI_output(self, '\t', [
            spath,
            '--measurements', 'snackF0',
            '--include-empty-labels',
            '--resample-freq', '16000',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 2341)
        self.assertEqual(lines[0][-1], 'snackF0')
        self.assertEqual(len(lines[1]), 6)
        self.assertFalse(os.path.exists(spath.split('.')[0] + '-resample-16000Hz.wav'))


@parameterize
class TestCommandF0(TestCase):

    def test_alternate_F0(self):
        lines = CLI_output(self, '\t', [
            '--F0', 'shrF0',
            '--include-F0-column',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['shrF0'])
        self.assertEqual(len(lines[1]), 6)

    def test_invalid_F0(self):
        with self.assertArgparseError(['nosuchpitch']):
            CLI(['--f0', 'nosuchpitch'])

    def test_invalid_snack_method(self):
        with self.assertArgparseError(['nosuchmethod']):
            CLI(['--snack-method', 'nosuchmethod'])

    def test_invalid_tcl_shell_cmd(self):
        with self.assertRaisesRegex(OSError, 'nosuchcmd'):
            lines = CLI_output(self, '\t', [
                sound_file_path('beijing_f3_50_a.wav'),
                '--measurements', 'snackF0',
                '--snack-method', 'tcl',
                '--tcl-cmd', 'nosuchcmd',
                ])

    def test_invalid_praat_f0_method(self):
        with self.assertArgparseError(['nosuchmethod']):
            CLI(['--praat-f0-method', 'nosuchmethod'])

    def test_snackF0_method_tcl(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--snack-method', 'tcl',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['snackF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    @unittest.skipIf(platform == 'darwin',
                     'Not supported on Mac OS X')
    def test_snackF0_method_python(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--snack-method', 'python',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['snackF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    @unittest.skipUnless(platform == 'win32' or platform == 'cygwin',
                         'Requires Windows operating system')
    def test_snackF0_method_exe(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackF0',
            '--snack-method', 'exe',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['snackF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_praatF0(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'praatF0',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['praatF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    def test_praat_f0_empty_output_file(self):
        err_msg = 'Praat error -- pitch calculation failed, check input parameters'
        with self.assertRaisesRegex(OSError, err_msg):
            lines = CLI_output(self, '\t', [
                sound_file_path('beijing_f3_50_a.wav'),
                '--measurements', 'praatF0',
                '--praat-min-f0', '400',
                ])

    # XXX There is as yet no confirmation that the values being tested against
    # here are accurate; these tests just prove the options have *some* effect.
    def test_praat_F0_alternate_method(self):
        lines = CLI_output(self, '\t', [
            '--measurements', 'praatF0',
            '--praat-f0-method', 'ac',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-1:], ['praatF0'])
        self.assertEqual(len(lines[1]), 6)
        self.assertEqual(lines[100],
            ['beijing_f3_50_a.wav', 'C1', '766.062', '865.632', '865',
             '216.620'])

    line100_prefix = ['beijing_f3_50_a.wav', 'C1', '766.062', '865.632', '865']

    def _check_algos(self, algo_list):
        self.assertEqual(sorted(algo_list), sorted(CLI._valid_f0), "Tests we have do not match tests we need")

    pitch_algo1_params = {
        'snackF0': ('snackF0', 585, '219.992'),
        'praatF0': ('praatF0', 585, '224.726'),
        'shrF0': ('shrF0', 585, '222.251'),
        }

    def test_have_default_settings_tests(self):
        self._check_algos(self.pitch_algo1_params.keys())

    def pitch_algo1_as_default_settings(self, pitch_algo, line_count, v100):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), line_count)
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo2_params = CLI._valid_f0

    def pitch_algo2_as_frame_shift(self, pitch_algo):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--frame-shift', '2',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 293)

    pitch_algo3_params = {
        'snackF0': ('snackF0', '221.386'),
        'praatF0': ('praatF0', '224.726'),
        'shrF0': ('shrF0', '238.159'),
        }

    # Note that Praat F0 doesn't use window size as a parameter
    def test_have_window_size_tests(self):
        self._check_algos(self.pitch_algo3_params.keys())

    def pitch_algo3_as_window_size(self, pitch_algo, v100):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--window-size', '10',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo4_params = {
        'snackF0': ('snackF0', '--snack-min-f0', '0.000'),
        'praatF0': ('praatF0', '--praat-min-f0', '229.865'),
        'shrF0': ('shrF0', '--shr-min-f0', '222.251'),
        }

    def test_have_min_f0_tests(self):
        self._check_algos(self.pitch_algo4_params.keys())

    def pitch_algo4_as_min_f0(self, pitch_algo, min_f0_arg, v100):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--no-output-settings',
            min_f0_arg, '200',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo5_params = {
        'snackF0': ('snackF0', '--snack-max-f0', '108.907'),
        'praatF0': ('praatF0', '--praat-max-f0', '112.061'),
        'shrF0': ('shrF0', '--shr-max-f0', '112.172'),
        }

    def test_have_max_f0_tests(self):
        self._check_algos(self.pitch_algo5_params.keys())

    def pitch_algo5_as_max_f0(self, pitch_algo, max_f0_arg, v100):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--no-output-settings',
            max_f0_arg, '200',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(lines[100], self.line100_prefix + [v100])

    pitch_algo6_params = {
        'snackF0': ('snackF0', 585, '216.709'),
        'praatF0': ('praatF0', 585, '224.755'),
        'shrF0': ('shrF0', 585, '219.583'),
        }

    def test_f0_resample_tests(self):
        self._check_algos(self.pitch_algo6_params.keys())

    def pitch_algo6_as_resample(self, pitch_algo, line_count, v100):
        lines = CLI_output(self, '\t', [
            '--f0', pitch_algo,
            '--include-F0-column',
            '--resample-freq', '16000',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), line_count)
        self.assertEqual(lines[100], self.line100_prefix + [v100])


@parameterize
class TestCommandFormants(TestCase):

    def test_default_formants(self):
        lines = CLI_output(self, '\t', [
            '--include-formant-cols',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        formant_col_names = ['pF1', 'pF2', 'pF3', 'pF4',
                             'pB1', 'pB2', 'pB3', 'pB4']
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 13)
        self.assertListEqual(lines[0][-8:], formant_col_names)

    def test_alternate_formants(self):
        lines = CLI_output(self, '\t', [
            '--formants', 'snackFormants',
            '--include-formant-cols',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(len(lines[1]), 13)
        self.assertEqual(lines[0][-8:], sformant_names)

    def test_invalid_formants(self):
        with self.assertArgparseError(['nosuchalgorithm']):
            CLI(['--formants', 'nosuchalgorithm'])

    def test_snackFormants_method_tcl(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackFormants',
            '--snack-method', 'tcl',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-8:], sformant_names)
        self.assertEqual(len(lines[1]), 13)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    @unittest.skipIf(platform == 'darwin',
                     'Not supported on Mac OS X')
    def test_snackFormants_method_python(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackFormants',
            '--snack-method', 'python',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-8:], sformant_names)
        self.assertEqual(len(lines[1]), 13)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    @unittest.skipUnless(platform == 'win32' or platform == 'cygwin',
                         'Requires Windows operating system')
    def test_snackFormants_method_exe(self):
        lines = CLI_output(self, '\t', [
            sound_file_path('beijing_f3_50_a.wav'),
            '--measurements', 'snackFormants',
            '--snack-method', 'exe',
            '--no-output-settings',
            ])
        self.assertEqual(len(lines), 585)
        self.assertEqual(lines[0][-8:], sformant_names)
        self.assertEqual(len(lines[1]), 13)
        self.assertEqual(len([x for x in lines if 'C1' in x]), 100)
        self.assertEqual(len([x for x in lines if 'V1' in x]), 208)
        self.assertEqual(len([x for x in lines if 'C2' in x]), 118)
        self.assertEqual(len([x for x in lines if 'V2' in x]), 158)

    line100_prefix = ['beijing_f3_50_a.wav', 'C1', '766.062', '865.632', '865']

    def _check_algos(self, algo_list):
        self.assertEqual(sorted(algo_list), sorted(CLI._valid_formants), "Tests we have do not match tests we need")

    formant_algo1_params = {
        'snackFormants': ('snackFormants', 585,
                          ['sF1', 'sF2', 'sF3', 'sF4', 'sB1', 'sB2', 'sB3', 'sB4'],
                          ['573.595', '1658.767', '3277.449', '4422.382'],
                          ['447.585', '139.099', '163.150', '405.460']),
        'praatFormants': ('praatFormants', 585,
                          ['pF1', 'pF2', 'pF3', 'pF4', 'pB1', 'pB2', 'pB3', 'pB4'],
                          ['502.944', '1681.375', '3320.657', '4673.634'],
                          ['406.819', '1058.742', '979.097', '646.462']),
        }

    def test_formant_default_settings_tests(self):
        self._check_algos(self.formant_algo1_params.keys())

    def formant_algo1_as_default_settings(self, formant_algo, line_count, formant_names, fvals, bvals):
        lines = CLI_output(self, '\t', [
            '--formants', formant_algo,
            '--include-formant-cols',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), line_count)
        self.assertEqual(len(lines[0]), 13)
        self.assertEqual(lines[0][:5], ['Filename', 'Label', 'seg_Start', 'seg_End', 't_ms'])
        self.assertEqual(lines[0][-8:], formant_names)
        self.assertEqual(lines[100][:5], self.line100_prefix)
        self.assertEqual(lines[100][-8:-4], fvals)
        self.assertEqual(lines[100][-4:], bvals)

    formant_algo2_params = {
        'snackFormants': ('snackFormants', 585,
                          ['sF1', 'sF2', 'sF3', 'sF4', 'sB1', 'sB2', 'sB3', 'sB4'],
                          ['554.578', '1439.016', '3262.044', '4233.911'],
                          ['153.172', '200.412', '426.036', '484.933']),
        'praatFormants': ('praatFormants', 585,
                          ['pF1', 'pF2', 'pF3', 'pF4', 'pB1', 'pB2', 'pB3', 'pB4'],
                          ['502.939', '1682.293', '3320.815', '4674.554'],
                          ['407.850', '1063.602', '982.643', '651.033']),
        }

    def test_formant_resample_tests(self):
        self._check_algos(self.formant_algo2_params.keys())

    def formant_algo2_as_resample(self, formant_algo, line_count, formant_names, fvals, bvals):
        lines = CLI_output(self, '\t', [
            '--formants', formant_algo,
            '--include-formant-cols',
            '--resample-freq', '16000',
            '--no-output-settings',
            sound_file_path('beijing_f3_50_a.wav'),
            ])
        self.assertEqual(len(lines), line_count)
        self.assertEqual(len(lines[0]), 13)
        self.assertEqual(lines[0][:5], ['Filename', 'Label', 'seg_Start', 'seg_End', 't_ms'])
        self.assertEqual(lines[0][-8:], formant_names)
        self.assertEqual(lines[100][:5], self.line100_prefix)
        if lines[100][-8:-4] != fvals:
            f_rtol = 1e-05
            f_atol = 1e-08
            print('\nAbsolute equality check for formant values using {} algorithm failed, try equality with rtol={}, atol={}'.format(formant_algo, f_rtol, f_atol))
            self.assertAllClose(np.float_(lines[100][-8:-4]), np.float_(fvals), rtol=f_rtol, atol=f_atol)
        else:
            self.assertEqual(lines[100][-8:-4], fvals)
        if lines[100][-4:] != bvals:
            b_rtol = 1e-05
            b_atol = 1e-08
            print('\nAbsolute equality check for bandwidth values {} algorithm failed, try equality with rtol={}, atol={}'.format(formant_algo, b_rtol, b_atol))
            self.assertAllClose(np.float_(lines[100][-4:]), np.float_(bvals), rtol=b_rtol, atol=b_atol)
        else:
            self.assertEqual(lines[100][-4:], bvals)
