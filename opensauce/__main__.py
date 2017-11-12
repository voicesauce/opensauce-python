"""Command line interface for OpenSauce, process measurements for output

"""

# Licensed under Apache v2 (see LICENSE)
# Based on VoiceSauce files vs_ParameterEstimation.m, vs_OutputToText.m,
# vs_Initialize.m, and vs_Settings.m

from __future__ import division
from __future__ import print_function

import argparse
import csv
import os
import shlex
import sys
import numpy as np

# Import user-defined global configuration variables
from conf.userconf import user_default_snack_method, user_tcl_shell_cmd, user_praat_path

# Import from soundfile.py in opensauce package
from .soundfile import SoundFile
# Import from helpers.py in opensauce package
from .helpers import remove_empty_lines_from_file, round_half_away_from_zero
# Import from snack.py in opensauce package
from .snack import valid_snack_methods, sformant_names
# Import from praat.py in opensauce package
from .praat import valid_praat_f0_methods

# Override default 'error' method so that it doesn't print out the noisy usage
# prefix on the error messages, and so that we get a useful command name
# when opensauce is run using -m.
class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        if self.prog.startswith('__main__'): # pragma: no cover
            self.prog = os.path.split(os.path.split(__file__)[0])[1]
        self.exit(2, "{}: error: {}\n".format(self.prog, message))

    def positive_int(self, value):
        """Check that type is positive integer
        """
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive integer value" % value)

        return ivalue

    def pos_half_int(self, value):
        """Check that type is positive half integer
        """
        fvalue = float(value)
        if (fvalue <= 0):
            # Not positive
            raise argparse.ArgumentTypeError("%s is an invalid positive half integer value" % value)
        if ('.' in value) and (value[-2:] != '.5'):
            # Not half integer
            raise argparse.ArgumentTypeError("%s is an invalid positive half integer value" % value)

        if ('.' in value):
            # Half integer given, return float
            return fvalue
        else:
            # Whole integer given, return integer
            return int(value)


class CLI(object):

    # Default settings file locations
    settings_locs = ('./opensauce.settings',
                     '~/.config/opensauce/settings',
                     '~/.opensaucerc')
    # Default measurements file locations
    measurements_locs = ('./opensauce.measurements',
                         '~/.config/opensauce/measurements',
                         '~/.opensauce.measurements')
    # Order to print arguments in output measurement file
    included_args_order = ['default_measurements_file', 'measurements',
                           'include_f0_column', 'include_formant_cols',
                           'use_textgrid', 'include_labels',
                           'include_empty_labels', 'ignore_label',
                           'time_starts_at_zero', 'include_interval_endpoint',
                           'NaN', 'output_delimiter', 'resample_freq', 'f0',
                           'formants', 'frame_shift', 'window_size',
                           'frame_precision', 'snack_method', 'tcl_cmd',
                           'snack_min_f0', 'snack_max_f0', 'pre_emphasis',
                           'lpc_order', 'shr_min_f0', 'shr_max_f0',
                           'praat_path', 'praat_f0_method', 'praat_min_f0',
                           'praat_max_f0', 'silence_threshold',
                           'voice_threshold', 'octave_cost', 'octave_jumpcost',
                           'voiced_unvoiced_cost', 'kill_octave_jumps',
                           'interpolate', 'smooth', 'smooth_bandwidth',
                           'num_formants', 'max_formant_freq']
    excluded_args = ['wavfiles', 'settings', 'output_filepath',
                     'output_settings', 'output_settings_path']

    #
    # Command Line Parsing and Execution.
    #

    def __init__(self, args=None):
        ns, _ = self.settings_option_parser.parse_known_args(args)
        if ns.settings:
            settings = self._settings_from_file(ns.settings)
        else:
            settings = self._settings_from_default_file()
        args = sys.argv[1:] if args is None else args
        self.args = self.parser.parse_args(settings + args)
        if not self.args.measurements:
            if self.args.default_measurements_file:
                self.args.measurements = self._measurements_from_file(
                                            self.args.default_measurements_file)
            else:
                self.args.measurements = self._measurements_from_default_file()
        if self.args.include_f0_column and self.args.f0 not in self.args.measurements:
            self.args.measurements.append(self.args.f0)
        if self.args.include_formant_cols and self.args.formants not in self.args.measurements:
            self.args.measurements.append(self.args.formants)
        if not self.args.measurements:
            self.parser.error("No measurements requested")
        # Cache for measurement results
        self._cached_results = {}
        # Cache for keys of measurements with multiple measurement vectors
        self._cached_measurement_keys = {}
        # Initialize length of measurement vectors
        # There is a distinct data_len for each sound file
        self.data_len = 0

    def _settings_from_file(self, filepath):
        with open(filepath) as fp:
            lines = [shlex.split(x) for x in fp.readlines()]
        # XXX this abbreviation check is a bit fragile in the face of a new
        # option starting with --me being added, but I haven't come up with a
        # better solution.
        lastoptname = lines[-1][0].lstrip('-')[1:]
        if lastoptname and 'easurements'.startswith(lastoptname):
            self.parser.error('"--measurements" may not be the last line'
                              ' in settings file {!r}'.format(filepath))
        # The strip and add of '--' makes '--' optional in the settings
        # file but ensures the '--' is there for parsing by argparse.
        settings = sum([['--' + tokens[0].lstrip('-')] + tokens[1:]
                       for tokens in lines], [])
        if any(x.startswith('--settings') for x in settings):
            self.parser.error(
                'invalid option "--settings" in settings file {!r}'.format(
                    filepath))
        return settings

    def _settings_from_default_file(self):
        for filepath in self.settings_locs:
            # Expand path for paths that start with tilde,
            # e.g. '~/.opensaucerc'
            filepath = os.path.expanduser(filepath)
            if os.path.isfile(filepath):
                return self._settings_from_file(filepath)
        return []

    def _measurements_from_file(self, filepath):
        measurements = []
        with open(filepath) as f:
            for i, line in enumerate(f):
                m = line.strip()
                if not hasattr(self, 'DO_' + m):
                    self.parser.error(
                        "Unknown measurement {} on line"
                        " {} of {!r}".format(m, i, filepath))
                measurements.append(m)
        return measurements

    def _measurements_from_default_file(self):
        for filepath in self.measurements_locs:
            # Expand path for paths that start with tilde,
            # e.g. '~/.opensauce.measurements'
            filepath = os.path.expanduser(filepath)
            if os.path.isfile(filepath):
                return self._measurements_from_file(filepath)
        return []

    def _algorithm(self, name):
        return getattr(self, 'DO_' + name)

    def _assemble_fields(self, filename, textgrid_data, offset, data):
        return ([filename] + (textgrid_data if self.args.use_textgrid and self.args.include_labels else []) + [offset] + data)

    def _get_value(self, vector, index):
        try:
            res = vector[index]
        except IndexError:
            res = self.args.NaN
        else:
            if isinstance(res, float) and np.isnan(res):
                res = self.args.NaN
            else:
                res = format(res, '.3f')

        return res

    def _write_settings(self, args_dict, path):
        with open(path, 'w') as oset:
            for a in self.included_args_order:
                val = args_dict[a]
                # Skip argument for these cases
                if val is None:
                    continue
                if isinstance(val, list) and (not val):
                    # Case of empty list
                    continue
                if (a == 'smooth_bandwidth') and (not args_dict['smooth']):
                    # Don't put --smooth-bandwidth in settings output
                    # unless --smooth is set to True
                    continue

                # Print argument in output settings file
                if isinstance(val, list):
                    # Case where arg is a list of unknown size
                    print('--{} {}'.format(a.replace('_', '-'), ' '.join(val)), file=oset)
                elif isinstance(val, bool):
                    # Boolean args have to be handled on case-by-case basis
                    if a == 'include_f0_column':
                        if val:
                            print('--include-f0-column', file=oset)
                        else:
                            print('--no-f0-column', file=oset)
                    elif a == 'include_formant_cols':
                        if val:
                            print('--include-formant-cols', file=oset)
                        else:
                            print('--no-formant-cols', file=oset)
                    elif a == 'use_textgrid':
                        if val:
                            print('--use-textgrid', file=oset)
                        else:
                            print('--no-textgrid', file=oset)
                    elif a == 'include_labels':
                        if val:
                            print('--include-labels', file=oset)
                        else:
                            print('--no-labels', file=oset)
                    elif a == 'time_starts_at_zero':
                        if val:
                            print('--time-starts-at-zero', file=oset)
                        else:
                            print('--time-starts-at-frameshift', file=oset)
                    elif a == 'include_interval_endpoint':
                        if val:
                            print('--include-interval-endpoint', file=oset)
                        else:
                            print('--exclude-interval-endpoint', file=oset)
                    elif a == 'include_empty_labels':
                        if val:
                            print('--include-empty-labels', file=oset)
                    elif a == 'kill_octave_jumps':
                        if val:
                            print('--kill-octave-jumps', file=oset)
                    elif a == 'interpolate':
                        if val:
                            print('--interpolate', file=oset)
                    elif a == 'smooth':
                        if val:
                            print('--smooth', file=oset)
                    else: # pragma: no cover
                        raise ValueError('Unknown Boolean argument {} while writing settings file'.format(a))
                elif a == 'praat_path':
                    # Put quotes around path, in case the path contains spaces
                    print('--{} \"{}\"'.format(a.replace('_', '-'), val), file=oset)
                else:
                    # Generic case
                    print('--{} {}'.format(a.replace('_', '-'), val), file=oset)

    def process(self):
        use_stdout = self.args.output_filepath in (None, '-')
        if use_stdout:
            of = sys.stdout
        else:
            of = open(self.args.output_filepath, 'w')
        try:
            self._process(of)
        except:
            raise
        else:
            # Write settings file
            if self.args.output_settings:
                args_dict = vars(self.args)
                # Make sure args we have are the same as the ones from the parser
                assert set(self.included_args_order + self.excluded_args) == set(args_dict.keys())
                # Path for output settings file
                if self.args.output_settings_path:
                    # User defined settings file path
                    output_settings_path = self.args.output_settings_path
                elif use_stdout:
                    # Default for stdout
                    output_settings_path = 'stdout.settings'
                else:
                    # Default if user requests output file
                    output_settings_path = self.args.output_filepath.split('.')[0] + '.settings'
                # Write settings to file
                self._write_settings(args_dict, output_settings_path)
        finally:
            if not use_stdout:
                of.close()
                remove_empty_lines_from_file(self.args.output_filepath)

    def _process(self, of):
        # Data fields to be printed to output
        data_fields = []
        for m in self.args.measurements:
            if m == 'snackFormants':
                data_fields.extend(sformant_names)
            elif m == 'praatFormants':
                for i in range(1, round_half_away_from_zero(self.args.num_formants) + 1):
                    data_fields.append('pF' + str(i))
                for i in range(1, round_half_away_from_zero(self.args.num_formants) + 1):
                    data_fields.append('pB' + str(i))
            else:
                data_fields.append(m)

        if self.args.output_delimiter == 'comma':
            output = csv.writer(of, dialect=csv.excel)
        elif self.args.output_delimiter == 'tab':
            output = csv.writer(of, dialect=csv.excel_tab)
        else: # pragma: no cover
            raise ValueError('Unknown output delimiter {}'.format(self.args.output_delimiter))

        output.writerow(
            self._assemble_fields(
                filename='Filename',
                textgrid_data=['Label', 'seg_Start', 'seg_End'],
                offset='t_ms',
                data=data_fields
            ))

        for wavfile in self.args.wavfiles:
            self._cached_results.clear()
            self._cached_measurement_keys.clear()

            if self.args.resample_freq is None:
                soundfile = SoundFile(wavfile)
                # Length of all measurement vectors written to output
                self.data_len = np.int_(np.floor(soundfile.ns / soundfile.fs / self.args.frame_shift * 1000))
            else:
                soundfile = SoundFile(wavfile, resample_freq=self.args.resample_freq)
                # Length of all measurement vectors written to output
                self.data_len = np.int_(np.floor(soundfile.ns_rs / soundfile.fs_rs / self.args.frame_shift * 1000))

            results = {}
            # Compute default F0 for parameters dependent on F0
            results[self.args.f0] = self._algorithm(self.args.f0)(soundfile)
            # Compute default formants for parameters dependent on formants
            formant_results = self._algorithm(self.args.formants)(soundfile)
            for k in formant_results:
                results[k] = formant_results[k]
            # Compute other measurements
            for measurement in self.args.measurements:
                # Check if result previously cached
                if measurement in self._cached_results:
                    results[measurement] = self._cached_results[measurement]
                elif measurement in self._cached_measurement_keys:
                    for k in self._cached_measurement_keys[measurement]:
                        results[k] = self._cached_results[k]
                # Otherwise, compute measurement
                else:
                    compute_measurement = self._algorithm(measurement)
                    computed_result = compute_measurement(soundfile)
                    if isinstance(computed_result, dict):
                        # Case of multiple measurements in dictionary
                        for k in computed_result:
                            results[k] = computed_result[k]
                    else:
                        # Case of single measurement vector
                        results[measurement] = computed_result

            # end_time is time for last sample in seconds
            # Time starts at zero
            beg_time = 0
            if self.args.resample_freq is None:
                end_time = soundfile.ns / soundfile.fs
            else:
                end_time = soundfile.ns_rs / soundfile.fs_rs
            # Determine intervals
            # Intervals are expressed in seconds
            if self.args.use_textgrid and soundfile.textgrid:
                intervals = soundfile.textgrid_intervals
            else:
                if self.args.use_textgrid:
                    # XXX covert this to use logging.
                    print("Found no TextGrid for {}, reporting all"
                          " data".format(soundfile.wavfn))
                intervals = (('no textgrid', beg_time, end_time),)

            frame_shift = self.args.frame_shift
            for (label, start, stop) in intervals:
                if label in self.args.ignore_label:
                    continue
                if not label.strip() and not self.args.include_empty_labels:
                    continue
                # Convert intervals from seconds to frame number
                fstart = np.int_(round_half_away_from_zero(start * 1000 / frame_shift))
                fstop = min(np.int_(round_half_away_from_zero(stop * 1000 / frame_shift)),
                            np.int_(np.floor(end_time * 1000 / frame_shift)))
                if not self.args.time_starts_at_zero:
                    fstart = fstart + 1
                    fstop = fstop + 1
                # Print intervals in milliseconds
                start_str = format(start * 1000, '.3f')
                stop_str = format(stop * 1000, '.3f')
                if self.args.include_interval_endpoint:
                    fstop = fstop + 1
                for s in range(fstart, fstop):
                    output.writerow(
                        self._assemble_fields(
                            filename=soundfile.wavfn,
                            textgrid_data=[label, start_str, stop_str],
                            offset=format(s * frame_shift, 'd'),
                            data=[self._get_value(results[x], s)
                                  for x in data_fields]
                        ))
            # Cleanup: remove wav file corresponding to resample,
            #          if necessary
            if self.args.resample_freq is not None:
                os.remove(soundfile.wavpath_rs)

    #
    # Algorithm wrappers.
    #

    def DO_snackF0(self, soundfile):
        from .snack import snack_pitch
        if soundfile.fs_rs is None:
             wavpath = soundfile.wavpath
        else:
             wavpath = soundfile.wavpath_rs
        F0, V = snack_pitch(wavpath,
                            self.args.snack_method,
                            self.data_len,
                            frame_shift=self.args.frame_shift,
                            window_size=self.args.window_size,
                            min_pitch=self.args.snack_min_f0,
                            max_pitch=self.args.snack_max_f0,
                            tcl_shell_cmd=self.args.tcl_cmd
                            )

        self._cached_results['snackF0'] = F0
        return F0

    def DO_praatF0(self, soundfile):
        from .praat import praat_pitch
        if soundfile.fs_rs is None:
             wavpath = soundfile.wavpath
        else:
             wavpath = soundfile.wavpath_rs
        F0 = praat_pitch(wavpath, self.data_len,
                         self.args.praat_path,
                         frame_shift=self.args.frame_shift,
                         method=self.args.praat_f0_method,
                         frame_precision=self.args.frame_precision,
                         min_pitch=self.args.praat_min_f0,
                         max_pitch=self.args.praat_max_f0,
                         silence_threshold=self.args.silence_threshold,
                         voice_threshold=self.args.voice_threshold,
                         octave_cost=self.args.octave_cost,
                         octave_jumpcost=self.args.octave_jumpcost,
                         voiced_unvoiced_cost=self.args.voiced_unvoiced_cost,
                         kill_octave_jumps=self.args.kill_octave_jumps,
                         interpolate=self.args.interpolate,
                         smooth=self.args.smooth,
                         smooth_bandwidth=self.args.smooth_bandwidth)

        self._cached_results['praatF0'] = F0
        return F0

    def DO_shrF0(self, soundfile):
        from .shrp import shr_pitch
        if soundfile.fs_rs is None:
             wavdata = soundfile.wavdata
             fs = soundfile.fs
        else:
             wavdata = soundfile.wavdata_rs
             fs = soundfile.fs_rs
        SHR, F0 = shr_pitch(wavdata, fs,
                            window_length=self.args.window_size,
                            frame_shift=self.args.frame_shift,
                            min_pitch=self.args.shr_min_f0,
                            max_pitch=self.args.shr_max_f0,
                            datalen=self.data_len,
                            frame_precision=self.args.frame_precision,
                            )
        self._cached_results['shrF0'] = F0
        self._cached_results['SHR'] = SHR
        return F0

    def DO_SHR(self, soundfile):
        self.DO_shrF0(soundfile)
        return self._cached_results['SHR']

    def DO_snackFormants(self, soundfile):
        from .snack import snack_formants
        if soundfile.fs_rs is None:
             wavpath = soundfile.wavpath
        else:
             wavpath = soundfile.wavpath_rs
        estimates = snack_formants(wavpath,
                                   self.args.snack_method,
                                   self.data_len,
                                   frame_shift=self.args.frame_shift,
                                   window_size=self.args.window_size,
                                   pre_emphasis=self.args.pre_emphasis,
                                   lpc_order=self.args.lpc_order,
                                   tcl_shell_cmd=self.args.tcl_cmd
                                  )

        self._cached_measurement_keys['snackFormants'] = estimates.keys()
        for k in estimates:
            self._cached_results[k] = estimates[k]

        return estimates

    def DO_praatFormants(self, soundfile):
        from .praat import praat_formants
        if soundfile.fs_rs is None:
             wavpath = soundfile.wavpath
        else:
             wavpath = soundfile.wavpath_rs
        estimates = praat_formants(wavpath, self.data_len,
                                   self.args.praat_path,
                                   frame_shift=self.args.frame_shift,
                                   window_size=self.args.window_size,
                                   frame_precision=self.args.frame_precision,
                                   num_formants=self.args.num_formants,
                                   max_formant_freq=self.args.max_formant_freq)

        self._cached_measurement_keys['praatFormants'] = estimates.keys()
        for k in estimates:
            self._cached_results[k] = estimates[k]

        return estimates

    _valid_measurements = [x[3:] for x in list(locals()) if x.startswith('DO_')]
    _valid_f0 = [x for x in _valid_measurements if x.endswith('F0')]
    _valid_formants = [x for x in _valid_measurements if x.endswith('Formants')]
    _valid_delimiters = ['comma', 'tab']
    # Determine default method for calling Snack

    if user_default_snack_method is not None: # pragma: no cover
        if user_default_snack_method in valid_snack_methods:
            if user_default_snack_method == 'exe' and (sys.platform != 'win32' and sys.platform != 'cygwin'):
                raise ValueError("Cannot use 'exe' as Snack calling method, when using non-Windows machine")
            default_snack_method = user_default_snack_method
        else:
            raise ValueError("Invalid Snack calling method. Choices are 'exe', 'python', and 'tcl'")
    elif sys.platform == 'win32' or sys.platform == 'cygwin': # pragma: no cover
        default_snack_method = 'tcl'
    elif sys.platform.startswith('linux'): # pragma: no cover
        default_snack_method = 'tcl'
    elif sys.platform == 'darwin': # pragma: no cover
        default_snack_method = 'tcl'
    else: # pragma: no cover
        default_snack_method = 'tcl'

    if user_tcl_shell_cmd is not None: # pragma: no cover
        default_tcl_shell_cmd = user_tcl_shell_cmd
    elif sys.platform == 'darwin': # pragma: no cover
        default_tcl_shell_cmd = 'tclsh8.4'
    else: # pragma: no cover
        default_tcl_shell_cmd = 'tclsh'

    if user_praat_path is not None: # pragma: no cover
        default_praat_path = user_praat_path
    elif sys.platform == 'darwin': # pragma: no cover
        default_praat_path = '/Applications/Praat.app/Contents/MacOS/Praat'
    elif sys.platform == 'win32' or sys.platform == 'cygwin': # pragma: no cover
        default_praat_path = 'C:\Program Files\Praat\Praat.exe'
    else: # pragma: no cover
        default_praat_path = '/usr/bin/praat'

    #
    # Parsing Declarations
    #

    # Special parser used to get the settings file name so we can read that
    # first before doing the main CLI parse.
    _settings_op_args = (('-s', '--settings'), dict(
                         help="Path to settings file.  Defaults to the first"
                              " of {} that is found.  Command line arguments"
                              " override file-based settings.".format(
                                 settings_locs)))
    settings_option_parser = MyArgumentParser(add_help=False)
    settings_option_parser.add_argument(*_settings_op_args[0],
                                        **_settings_op_args[1])

    # Main CLI parser.
    parser = MyArgumentParser()
    # The arguments (as opposed to the options) are a list of filenames to
    # analyze.
    parser.add_argument('wavfiles', nargs="+", metavar='wavfile',
                        help="WAV file to analyze")
    # Need to include settings in main parser also so it doesn't cause an error
    # during the full parse and so it shows up in help.
    parser.add_argument(*_settings_op_args[0], **_settings_op_args[1])
    del _settings_op_args
    # These options control where we get our measurements
    parser.add_argument('-m', '--default-measurements-file',
                        help="Path to measurements file.  Defaults to the "
                             "first of "
                             "{} that is found.".format(measurements_locs))
    parser.add_argument('--measurements', nargs="+",
                        choices=_valid_measurements,
                        help="Measurement to be computed for each input "
                             "file.  The specified measurements appear as "
                             "columns in the output file in the same order as "
                             "specified on the command line.  When "
                             "--measurements is specified, the default "
                             "measurements file is ignored.  The supported "
                             "values for measurements are: "
                             "{}".format(_valid_measurements))
   # These options control the output
    parser.add_argument('--no-f0-column', '--no-F0-column',
                        action="store_false", dest='include_f0_column',
                        help="Do not include the F0 measurement used as input "
                             "to the other algorithms as the first column of "
                             "the output (default is True, for compatibility "
                             "with VoiceSauce).")
    parser.add_argument('--include-f0-column', '--include-F0-column',
                        action="store_true", dest='include_f0_column',
                        help="Include the F0 measurement used as input to the "
                             "other algorithms as the first column of the "
                             "output (default is False, for compatibility "
                             "with VoiceSauce).")
    parser.add_argument('--no-formant-cols',
                        action="store_false", dest='include_formant_cols',
                        help="Do not include the formant measurements used as "
                             "input to the other algorithms as the first "
                             "column of the output (default is True, for "
                             "compatibility with VoiceSauce).")
    parser.add_argument('--include-formant-cols',
                        action="store_true", dest='include_formant_cols',
                        help="Include the formant measurements used as input "
                             "to the other algorithms as the first column of "
                             "the output (default is False, for compatibility "
                             "with VoiceSauce).")
    parser.add_argument('--no-textgrid', action="store_false",
                        dest='use_textgrid',
                        help="Do not include the TextGrid interval "
                             "information for analysis.")
    parser.add_argument('--use-textgrid', action="store_true",
                        dest='use_textgrid', default=True,
                        help="Include the TextGrid interval information for "
                             "analysis (default %(default)s).")
    parser.add_argument('--no-labels', action="store_false",
                        dest='include_labels',
                        help="Do not include the TextGrid labels or interval "
                             "information in the output.")
    parser.add_argument('--include-labels', action='store_true',
                        dest='include_labels',
                        help="Include the TextGrid labels and interval "
                             "information in the output "
                             "(default %(default)s).")
    parser.add_argument('--include-empty-labels', default=False,
                        action='store_true',
                        help="Include TextGrid entries with empty or blank"
                             " labels in the analysis and output. "
                             "Default is %(default)s.")
    parser.add_argument('--ignore-label', action='append', default=[],
                        help="A TextGrid label to exclude from the analysis"
                             " and output.  May be specified more than once.")
    parser.add_argument('--time-starts-at-zero', action="store_true",
                        dest='time_starts_at_zero', default=True,
                        help="First time point in each measurement vector is "
                             " t = 0. "
                             "(default %(default)s).")
    parser.add_argument('--time-starts-at-frameshift', action='store_false',
                        dest='time_starts_at_zero',
                        help="First time point in each measurement vector is "
                             " t = frame shift.")
    parser.add_argument('--include-interval-endpoint', action='store_true',
                        dest='include_interval_endpoint',
                        help="Include interval endpoint in measurement "
                              "output, so that the upper endpoint is "
                              "included in the reported time points, i.e. "
                              "[a,b].")
    parser.add_argument('--exclude-interval-endpoint', action='store_false',
                        dest='include_interval_endpoint',
                        help="Exclude interval endpoint in measurement "
                              "output, so that the upper endpoint is not in "
                              "the reported time points, i.e. [a,b). "
                             "By default, endpoints are excluded.")

    parser.set_defaults(include_f0_column=False, include_formant_cols=False,
                        use_textgrid=True, include_labels=True,
                        time_starts_at_zero=True,
                        include_interval_endpoint=False)
    parser.add_argument('--NaN', default='NaN',
                        help="String to use for measurement values that do "
                             "not exist or whose value is invalid "
                             "(default %(default)s).")
    parser.add_argument('-o', '--output-filepath',
                        help="Path to the output file.  If the file already "
                             "exists, it will be overwritten.  Default is to "
                             "write to the shell standard output, which can "
                             "also be specified explicitly by specifying "
                             "'-' as the OUTPUT_FILEPATH.")
    parser.add_argument('--output-delimiter', default='tab',
                        choices=_valid_delimiters,
                        help="Delimiter to use for output file.  It defaults "
                             "to %(default)s.")
    parser.add_argument('--no-output-settings', action="store_false",
                        dest='output_settings',
                        help="Do not write settings file corresponding to "
                             "this command line execution.")
    parser.add_argument('--output-settings', action="store_true",
                        dest='output_settings', default=True,
                        help="Write settings file corresponding to this "
                             "command line execution. "
                             "(default %(default)s).")
    parser.add_argument('--output-settings-path',
                        help="Path to use for writing settings file.  If not "
                             "specified, then the defaults are as follows. "
                             "If output is written to stdout, the default is "
                             "'stdout.settings'. If output is written to "
                             "file, the default is the basename of the output "
                             "file plus the file extension '.settings' (e.g. "
                             "if the output file is 'output.txt', the settings "
                             "file path used is 'output.settings').")
    # These options are general settings for the analysis
    parser.add_argument('--resample-freq', type=parser.positive_int,
                        help="Resample sound files at specified frequency in"
                             " Hz.")
    parser.add_argument('-f', '--f0', '--F0', default='snackF0',
                        choices=_valid_f0,
                        help="The algorithm to use to compute F0 for use as "
                             "input to the other measurements.  It will "
                             "appear in the output as the first column if "
                             "--include-f0-column is specified.  It defaults "
                             "to %(default)s.")
    parser.add_argument('--formants', default='praatFormants',
                        choices=_valid_formants,
                        help="The algorithm to use to compute formants for "
                             "use as input to the other measurements.  It will "
                             "appear in the output as the first column if "
                             "--include-formant-cols is specified.  It defaults "
                             "to %(default)s.")
    parser.add_argument('--frame-shift', default=1, type=parser.positive_int,
                        help="Number of milliseconds the analysis frame is "
                             "shifted between computed data points (global "
                             "parameter).  Default is %(default)s "
                             "milliseconds.")
    parser.add_argument('--window-size', default=25, type=parser.positive_int,
                        help="Width of each analysis frame in milliseconds "
                             "(global parameter).  Default is %(default)s "
                             "milliseconds.")
    parser.add_argument('--frame-precision', default=1,
                        type=parser.positive_int,
                        help="Frame precision for interpolating measurement "
                             "vectors, in multiples of frame shift (global "
                             "parameter).  Default is %(default)s.")
    # These options control the Snack analysis
    parser.add_argument('--snack-method', default=default_snack_method,
                        choices=valid_snack_methods,
                        help="Method to use in calling Snack (Snack F0 and "
                             "Snack formants parameter). "
                             "The default is '%(default)s'.")
    parser.add_argument('--tcl-cmd', default=default_tcl_shell_cmd,
                        help="Command to use when calling Tcl shell for Snack "
                             "F0 analysis (Snack F0 and Snack formants "
                             "parameter).  On OS X, the default is "
                             "'tclsh8.4'.  On Linux and Windows, the default "
                             "is 'tclsh'.")
    parser.add_argument('--snack-min-f0', '--snack-min-F0', default=40,
                        type=parser.positive_int,
                        help="Lowest frequency considered in Snack F0 "
                             "analysis (Snack F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--snack-max-f0', '--snack-max-F0', default=500,
                        type=parser.positive_int,
                        help="Highest frequency considered in Snack F0 "
                             "analysis (Snack F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--pre-emphasis', default=0.96, type=float,
                        help="Pre-emphasis factor for Snack formant analysis "
                             "(Snack formants parameter). "
                             "Default is %(default)s")
    parser.add_argument('--lpc-order', default=12, type=parser.positive_int,
                        help="LPC order used in Snack formant analysis "
                             "(Snack formants parameter). "
                             "Default is %(default)s.")
    # These options control the SHR analysis
    parser.add_argument('--shr-min-f0', '--shr-min-F0', default=40,
                        type=parser.positive_int,
                        help="Lowest frequency considered in SHR F0 "
                             "analysis (SHR and SHR F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--shr-max-f0', '--shr-max-F0', default=500,
                        type=parser.positive_int,
                        help="Highest frequency considered in SHR F0 "
                             "analysis (SHR and SHR F0 parameter). "
                             "Default is %(default)s Hz.")
    # These options control the Praat analysis
    parser.add_argument('--praat-path', default=default_praat_path,
                        help="Path to Praat program executable (Praat F0 "
                             "and Praat formants parameter).  On OS X, "
                             "the default is "
                             "'/Applications/Praat.app/Contents/MacOS/Praat'. "
                             "On Windows, the default is "
                             "'C:\Program Files\Praat\Praat.exe'. On Linux, "
                             "the default is '/usr/bin/praat'.")
    parser.add_argument('--praat-f0-method', '--praat-F0-method', default='cc',
                        choices=valid_praat_f0_methods,
                        help="Method to use in calculating Praat F0, either "
                             "autocorrelation 'ac' or cross-correlation 'cc' "
                             "(Praat F0 parameter). "
                             "Default is %(default)s.")
    parser.add_argument('--praat-min-f0', '--praat-min-F0', default=40,
                        type=parser.positive_int,
                        help="Lowest frequency considered in Praat F0 "
                             "analysis (Praat F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--praat-max-f0', '--praat-max-F0', default=500,
                        type=parser.positive_int,
                        help="Highest frequency considered in Praat F0 "
                             "analysis (Praat F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--silence-threshold', default=0.03, type=float,
                        help="Relative silence threshold for Praat F0 "
                              "analysis (Praat F0 parameter). "
                             "Default is %(default)s")
    parser.add_argument('--voice-threshold', default=0.45, type=float,
                        help="Strength of unvoiced candidate for Praat F0 "
                              "analysis (Praat F0 parameter). "
                             "Default is %(default)s")
    parser.add_argument('--octave-cost', default=0.01, type=float,
                        help="Degree of favoring of high-frequency candidates "
                             "for Praat F0 analysis (Praat F0 parameter). "
                             "Default is %(default)s")
    parser.add_argument('--octave-jumpcost', default=0.35, type=float,
                        help="Degree of disfavoring of pitch changes "
                             "for Praat F0 analysis (Praat F0 parameter). "
                             "Default is %(default)s")
    parser.add_argument('--voiced-unvoiced-cost', default=0.14, type=float,
                        help="Degree of disfavouring of voiced/unvoiced "
                             "transitions for Praat F0 analysis (Praat F0 "
                             "parameter). "
                             "Default is %(default)s")
    parser.add_argument('--kill-octave-jumps', default=False,
                        action="store_true",
                        help="Remove pitch halving and doubling in "
                             "post-processing for Praat F0 analysis (Praat "
                             "F0 parameter). "
                             "Default is %(default)s.")
    parser.add_argument('--interpolate', default=False,
                        action="store_true",
                        help="Interpolate missing pitch values in "
                             "post-processing for Praat F0 analysis (Praat "
                             "F0 parameter). "
                             "Default is %(default)s.")
    parser.add_argument('--smooth', default=False,
                        action="store_true",
                        help="Smooth pitch in post-processing of Praat F0 "
                             "analysis using bandwidth specified by "
                             "--smooth-bandwidth argument (Praat F0 "
                             "parameter). "
                             "Default is %(default)s.")
    parser.add_argument('--smooth-bandwidth', default=5,
                        type=parser.positive_int,
                        help="Bandwidth in Hz to use for smoothing if smooth "
                             "is set to True (Praat F0 parameter). "
                             "Default is %(default)s Hz.")
    parser.add_argument('--num-formants', default=4, type=parser.pos_half_int,
                        help="Number of formants to extract, usually an "
                             "integer but half-integer values are allowed "
                             "(Praat formants parameter). "
                             "Default is %(default)s.")
    parser.add_argument('--max-formant-freq', default=6000,
                        type=parser.positive_int,
                        help="Maximum allowed frequency for formant search "
                             "range in Hz (Praat formants parameter). "
                             "Default is %(default)s.")


if __name__ == '__main__':
    try: # pragma: no cover
        my_cli = CLI()
        my_cli.process()
    except (OSError, IOError, ValueError) as err: # pragma: no cover
        print(err)
        sys.exit(1)
