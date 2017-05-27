from __future__ import division

import argparse
import csv
import os
import shlex
import sys
from sys import platform

# Import user-defined global configuration variables
import userconf

# Import from soundfile.py in opensauce package
from .soundfile import SoundFile


# Override default 'error' method so that it doesn't print out the noisy usage
# prefix on the error messages, and so that we get a useful command name
# when opensauce is run using -m.
class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        if self.prog.startswith('__main__'):
            self.prog = os.path.split(os.path.split(__file__)[0])[1]
        self.exit(2, "{}: error: {}\n".format(self.prog, message))


class CLI(object):

    settings_locs = ('./opensauce.settings',
                     '~/.config/opensauce/settings',
                     '~/.opensaucerc')
    measurements_locs = ('./opensauce.measurements',
                         '~/.config/opensauce/measurements',
                         '~/.opensauce.measurements')

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
        if self.args.include_f0_column:
            self.args.measurements.append(self.args.f0)
        if not self.args.measurements:
            self.parser.error("No measurements requested")
        self._cached_results = {}

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
        return ([filename] + (textgrid_data if self.args.use_textgrid else []) + [offset] + data)

    def _get_value(self, vector, index):
        try:
            res = vector[index]
        except IndexError:
            res = self.args.NaN
        else:
            res = format(res, '.3f')
        return res

    def process(self):
        use_stdout = self.args.output_filepath in (None, '-')
        if use_stdout:
            of = sys.stdout
        else:
            of = open(self.args.output_filepath, 'w')
        try:
            self._process(of)
        finally:
            if not use_stdout:
                of.close()

    def _process(self, of):
        output = csv.writer(of, dialect=csv.excel_tab)
        output.writerow(
            self._assemble_fields(
                filename='Filename',
                textgrid_data=['Label', 'seg_Start', 'seg_End'],
                offset='t_ms',
                data=self.args.measurements
            ))
        for wavfile in self.args.wavfiles:
            self._cached_results.clear()
            soundfile = SoundFile(wavfile)
            results = {}
            results[self.args.f0] = self._algorithm(self.args.f0)(soundfile)
            for measurement in self.args.measurements:
                if measurement in self._cached_results:
                    results[measurement] = self._cached_results[measurement]
                else:
                    compute_measurement = self._algorithm(measurement)
                    results[measurement] = compute_measurement(soundfile)
            if self.args.use_textgrid and soundfile.textgrid:
                intervals = soundfile.textgrid_intervals
            else:
                if self.args.use_textgrid:
                    # XXX covert this to use logging.
                    print("Found no TextGrid for {}, reporting all"
                          " data".format(soundfile.wavfn))
                intervals = (('no textgrid', 0,
                              int(soundfile.ms_len//self.args.frame_shift)),)
            frame_shift = self.args.frame_shift
            for (label, start, stop) in intervals:
                if label in self.args.ignore_label:
                    continue
                if not label.strip() and not self.args.include_empty_labels:
                    continue
                fstart = int(round(start*1000/frame_shift))
                fstop = min(int(round(stop*1000/frame_shift)),
                            int(soundfile.ms_len//self.args.frame_shift))
                start_str = format(start, '.3f')
                stop_str = format(stop, '.3f')
                for s in range(fstart, fstop+1):
                    output.writerow(
                        self._assemble_fields(
                            filename=soundfile.wavfn,
                            textgrid_data=[label, start_str, stop_str],
                            offset=format(s * frame_shift, '.3f'),
                            data=[self._get_value(results[x], s)
                                  for x in self.args.measurements]
                        ))

    #
    # Algorithm wrappers.
    #

    def DO_snackF0(self, soundfile):
        from .snack import snack_pitch
        F0, V = snack_pitch(soundfile.wavpath,
                            method=self.args.snack_method,
                            frame_length=self.args.frame_shift/1000,
                            window_length=self.args.window_size/1000,
                            min_pitch=self.args.min_f0,
                            max_pitch=self.args.max_f0,
                            )
        self._cached_results['snackF0'] = F0
        return F0

    def DO_shrF0(self, soundfile):
        from .shrp import shr_pitch
        SHR, F0 = shr_pitch(soundfile.wavdata,
                            soundfile.fs,
                            window_length=self.args.window_size,
                            frame_shift=self.args.frame_shift,
                            # XXX need to add shrp_min_f0 etc
                            min_pitch=self.args.min_f0,
                            max_pitch=self.args.max_f0,
                            datalen=soundfile.ms_len,
                            frame_precision=1,
                            )
        self._cached_results['shrF0'] = F0
        self._cached_results['SHR'] = SHR
        return F0

    def DO_SHR(self, soundfile):
        self.DO_shrF0(soundfile)
        return self._cached_results['SHR']

    _valid_measurements = [x[3:] for x in list(locals()) if x.startswith('DO_')]
    _valid_f0 = [x for x in _valid_measurements if x.endswith('F0')]
    _valid_snack_methods = ['exe', 'python', 'tcl']
    # Determine default method for calling Snack

    if userconf.user_default_snack_method is not None:
        if userconf.user_default_snack_method in _valid_snack_methods:
            if userconf.user_default_snack_method == 'exe' and (platform != 'win32' and platform != 'cygwin'):
                raise ValueError("Cannot use 'exe' as Snack calling method, when using non-Windows machine")
            default_snack_method = userconf.user_default_snack_method
        else:
            raise ValueError("Invalid Snack calling method. Choices are 'exe', 'python', and 'tcl'")
    elif platform == "win32" or platform == "cygwin":
        default_snack_method = 'exe'
    elif platform == "linux" or platform == "linux2":
        default_snack_method = 'python'
    elif platform == "darwin":
        default_snack_method = 'tcl'
    else:
        default_snack_method = 'tcl'

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
                        help="wav file to analyze")
    # Need to include settings in main parser also so it doesn't cause an error
    # during the full parse and so it shows up in help.
    parser.add_argument(*_settings_op_args[0], **_settings_op_args[1])
    del _settings_op_args
    # These options control where we get our measurements.
    parser.add_argument('-m', '--default-measurements-file',
                        help="Path to measurements file.  Defaults to the first"
                             " of {} that is found.".format(measurements_locs))
    parser.add_argument('--measurements', nargs="+",
                        choices=_valid_measurements,
                        help="Measurement to be computed for each input file."
                             " The specified measurements appear as columns"
                             " in the output file in the same order as"
                             " specified on the command line.  When"
                             " --measurements is specified the default"
                             " measurements file is ignored."
                             " The supported values for measurements are:"
                             " {}".format(_valid_measurements))
    # These options control the analysis.
    parser.add_argument('-f', '--f0', '--F0', default='snackF0',
                        choices=_valid_f0,
                        help="The algorithm to use to compute F0 for use as"
                             " input to the other measurements.  It will appear"
                             " in the output as the first column if"
                             " --include-f0-output is specified.  It defaults"
                             " to %(default)s.")
    parser.add_argument('--frame-shift', default=1, type=int,
                        help="Number of milliseonds the analysis frame is"
                             " shifted between computed data points.  Default"
                             " is %(default)s milliseconds.")
    parser.add_argument('--window-size', default=15, type=int,
                        help="Width of each analysis frame in milliseconds."
                             " Default is %(default)s milliseconds.")
    parser.add_argument('--min-f0', '--min-F0', default=40, type=int,
                        help="Lowest frequency considered in F0 analysis."
                             " Default is %(default)s Hz.")
    parser.add_argument('--max-f0', '--max-F0', default=500, type=int,
                        help="Highest frequency considered in F0 analysis."
                             " Default is %(default)s Hz.")
    parser.add_argument('--include-empty-labels', default=False,
                        action='store_true',
                        help="Include TextGrid entries with empty or blank"
                             " labels in the analysis and output.  Default"
                             " is %(default)s.")
    parser.add_argument('--ignore-label', action='append', default=[],
                        help="A TextGrid label to exclude from the analysis"
                             " and output.  May be specified more than once.")
    # These options control the output.
    parser.add_argument('--no-f0-column', '--no-F0-column',
                        action="store_false", dest='include_f0_column',
                        help="Do not include the F0 measurement used as input"
                             " to the other algorithms as the first column of"
                             " the output (default True, for compatibility"
                             " with voicesauce).")
    parser.add_argument('--include-f0-column', '--include-F0-column',
                        action="store_true", dest='include_f0_column',
                        help="Include the F0 measurement used as input"
                             " to the other algorithms as the first column of"
                             " the output (default False, for compatibility"
                             " with voicesauce).")
    parser.add_argument('--no-textgrid', action="store_false",
                        dest='use_textgrid',
                        help="Do not include the textgrid interval"
                             " information for analysis.")
    parser.add_argument('--use-textgrid', action="store_true",
                        dest='use_textgrid',
                        help="Include the textgrid interval"
                             " information for analysis (default %(default)s).")
    parser.add_argument('--no-labels', action="store_false",
                        dest='include_labels', default=True,
                        help="Do not include the textgrid labels or interval"
                             " information in the output.")
    parser.add_argument('--include-labels', action="store_true",
                        dest='include_labels',
                        help="Include the textgrid labels and interval"
                             " information in the output"
                             " (default %(default)s).")
    parser.set_defaults(include_f0_column=False, use_textgrid=True,
                        include_labels=True)
    parser.add_argument('--NaN', default='NaN',
                        help="String to use for measurement values that do not"
                             " exist or whose valid is invalid"
                             " (default %(default)s).")
    parser.add_argument('-o', '--output-filepath',
                        help="Path to the output file.  If the file already"
                             " exists it will be overwritten.  Default"
                             " is to write to the shell standard output,"
                             " which can also be specified explicitly by"
                             " specifying '-' as the OUTPUT_FILEPATH.")
    parser.add_argument('--snack-method', default=default_snack_method,
                        choices=_valid_snack_methods,
                        help="Method to use in calling Snack.  On Windows,"
                             " the default is 'exe'.  On Linux, the default"
                             " is 'python'.  On OS X, the default is 'tcl'.")


if __name__ == '__main__':
    try:
        my_cli = CLI()
        my_cli.process()
    except (OSError, IOError) as err:
        print(err)
        sys.exit(1)
