from __future__ import division

import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import csv
import os
import shlex
import sys

from .soundfile import SoundFile


class CmdError(Exception):
    pass


settings_locs = ('./opensauce.settings',
                 '~/.config/opensauce/settings',
                 '~/.opensaucerc')
measurements_locs = ('./opensauce.measurements',
                    '~/.config/opensauce/measurements',
                    '~/.opensauce.measurements')



class CLI(argparse.Namespace):

    def __init__(self, args=None):
        args = self.parser.parse_args(args)
        if args.measurements and args.default_measurements_file:
            raise CmdError("Cannot specify both --measurements and"
                           " -m/--default-measurements-file")
        if args.settings:
            self._load_settings(args, args.settings)
        else:
            self._load_default_settings()
        self.__dict__.update(args.__dict__)
        if self.default_measurements_file:
            self._load_default_measurements_file(self.default_measurements_file)
        elif not self.measurements:
            self._load_default_measurements()
        self._cached_results = {}

    def _load_settings_file(self, filepath):
        cp = configparser.ConfigParser()
        with open(filepath) as fp:
            cp.readfp(fp)
        args = sum([['--' + k] + shlex.split(v)
                    for k, v in cp.defaults.values()], [])
        args, argv = self.parser.parse_known_args(args)
        if args.measurements:
            argv.extend(['--measurements'] + args.measurements)
        if args.settings:
            argv.extend(['--settings', args.settings])
        if argv:
            raise CmdError(
                "Unrecognized options in settings file {!r}: {}".format(
                    filepath, argv))
        self.__dict__.update(args.__dict__)

    def _load_default_settings(self):
        for filepath in settings_locs:
            if os.path.isfile(filepath):
                self._load_settings_file(filepath)
                return

    def _load_default_measurements_file(self, filepath):
        self.measurements = []
        with open(filepath) as f:
            for i, line in enumerate(f):
                m = line.strip()
                if not hasattr(self, 'DO_' + m):
                    raise CmdError(
                        "Unknown measurement {} on line"
                        "{} of {!r}".format(m, i, filepath))
                self.measurements.append(m)

    def _load_default_measurements(self):
        for filepath in measurements_locs:
            if os.path.isfile(filepath):
                self._load_default_measurements_file(filepath)
                return

    def _algorithm(self, name):
        return getattr(self, 'DO_' + name)


    def _assemble_fields(self, filename, textgrid_data, offset, f0, data):
        return ([filename]
                + (textgrid_data if self.use_textgrid else [])
                + [offset]
                + ([f0] if self.include_f0_column else [])
                + data)

    def _get_value(self, vector, index):
        try:
            res = vector[index]
        except IndexError:
            res = self.NaN
        else:
            res = format(res, '.3f')
        return res

    def process(self):
        with open(self.output_filepath, 'w') as of:
            output = csv.writer(of, dialect=csv.excel_tab)
            output.writerow(
                self._assemble_fields(
                    filename='Filename',
                    textgrid_data=['Label', 'seg_Start', 'seg_End'],
                    offset='t_ms',
                    f0=self.f0,
                    data=self.measurements
                ))
            for wavfile in self.wavfiles:
                self._cached_results.clear()
                soundfile = SoundFile(wavfile)
                results = {}
                results[self.f0] = self._algorithm(self.f0)(soundfile)
                for measurement in self.measurements:
                    compute_measurement = self._algorithm(measurement)
                    results[measurement] = compute_measurement(soundfile)
                if self.use_textgrid and soundfile.textgrid:
                    intervals = soundfile.textgrid_intervals
                else:
                    if self.use_textgrid:
                        # XXX covert this to use logging.
                        print("Found no TextGrid for {}, reporting all"
                               " data".format(soundfile.wavfn))
                    intervals = (('no textgrid', 0,
                                  int(soundfile.ms_len//self.frame_shift)),)
                frame_shift = self.frame_shift
                for (label, start, stop) in intervals:
                    if label in self.ignore_label:
                        continue
                    if not label.strip() and not self.include_empty_labels:
                        continue
                    fstart = int(round(start*1000/frame_shift))
                    fstop = min(int(round(stop*1000/frame_shift)),
                                int(soundfile.ms_len//self.frame_shift))
                    start_str = format(start, '.3f')
                    stop_str = format(stop, '.3f')
                    for s in range(fstart, fstop+1):
                        output.writerow(
                            self._assemble_fields(
                                filename=soundfile.wavfn,
                                textgrid_data=[label, start_str, stop_str],
                                offset=format(s * frame_shift, '.3f'),
                                f0=self._get_value(results[self.f0], s),
                                data=[self._get_value(results[x], s)
                                      for x in self.measurements]
                            ))

    def DO_snackF0(self, soundfile):
        if 'snackF0' in self._cached_results:
            return self._cached_results['snackF0']
        from .snack import snack_pitch
        F0, V = snack_pitch(soundfile.wavpath,
                            frame_length=self.frame_shift/1000,
                            window_length=self.window_size/1000,
                            min_pitch=self.min_F0,
                            max_pitch=self.max_F0,
                            )
        self._cached_results['snackF0'] = F0
        return F0

    _valid_measurements = [x[3:] for x in list(locals()) if x.startswith('DO_')]

    parser = argparse.ArgumentParser()
    # The arguments (as opposed to the options) are a list of filenames to
    # analyze.
    parser.add_argument('wavfiles', nargs="+", metavar='wavfile',
                        help="wav file to analyze")
    # These options control where we get our settings and measurements.
    parser.add_argument('-s', '--settings',
                        help="Path to settings file.  Defaults to the first"
                             " of {} that is found.  Command line arguments"
                             " override file-based settings.".format(
                                settings_locs))
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
                             " measurements file is ignored, and specifying"
                             " -m/--default-measurements-file is an error."
                             " The supported values for measurements are:"
                             " {}".format(_valid_measurements))
    # These options control the analysis.
    parser.add_argument('-f', '--f0', default='snackF0',
                        help="The algorithm to use to compute F0 for use as"
                             " input to the other measurements.  It will appear"
                             " in the output as the first column unless"
                             " --no-f0-output is specified.  It defaults to"
                             " %(default)s.")
    parser.add_argument('--frame-shift', default=1, type=int,
                        help="Number of milliseonds the analysis frame is"
                             " shifted between computed data points.  Default"
                             " is %(default)s milliseconds.")
    parser.add_argument('--window-size', default=15, type=int,
                        help="Width of each analysis frame in milliseconds."
                             " Default is %(default)s milliseconds.")
    parser.add_argument('--min-F0', default=40, type=int,
                        help="Lowest frequency considered in F0 analysis."
                             " Default is %(default)s Hz.")
    parser.add_argument('--max-F0', default=500, type=int,
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
    parser.add_argument('--no-f0-column', action="store_false",
                        dest='include_f0_column',
                        help="Do not include the F0 measurement used as input"
                             " to the other algorithms as the first column of"
                             " the output (default True, for compatibility"
                             " with voicesauce).")
    parser.add_argument('--include-f0-column', action="store_true",
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
                        help="Do not include the textgrid interval"
                             " information for analysis.")
    parser.add_argument('--no-labels', action="store_false",
                        dest='include_labels', default=True,
                        help="Do not include the textgrid labels or interval"
                             " information in the output.")
    parser.add_argument('--include-labels', action="store_true",
                        dest='include_labels',
                        help="Include the textgrid labels and interval"
                             " information in the output.")
    parser.set_defaults(include_f0_column=False, use_textgrid=True,
                        include_labels=True)
    parser.add_argument('--NaN', default='NaN',
                        help="String to use for measurement values that do not"
                             " exist or whose valid is invalid.")
    parser.add_argument('-o', '--output-filepath', default='output.txt',
                        help="Path to the output file.  If the file already"
                             " exists it will be overwritten.  Default"
                             " is %(default)s.")


if __name__ == '__main__':
    try:
        CLI().process()
    except (CmdError, OSError, IOError) as err:
        print(err)
        sys.exit(1)
