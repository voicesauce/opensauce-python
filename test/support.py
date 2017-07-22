import contextlib
import csv
import collections
import json
import os
import sys
import unittest
import numpy as np
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import scipy.io

from opensauce.__main__ import CLI
from opensauce.textgrid import TextGrid

try:
    from tempfile import TemporaryDirectory
except ImportError:
    # Copied from Python3.
    from tempfile import mkdtemp
    import shutil as _shutil

    class TemporaryDirectory(object):
        name = None
        _finalizer = None
        _closed = False

        def __init__(self, suffix="", prefix='tmp', dir=None):
            self.name = mkdtemp(suffix, prefix, dir)

        @classmethod
        def _cleanup(cls, name, warn_message=None):
            _shutil.rmtree(name)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def cleanup(self):
            if self.name is not None and not self._closed:
                _shutil.rmtree(self.name)
                self._closed = True

        def __del__(self):
            self.cleanup()

py2 = sys.version_info[0] < 3

data_path = os.path.join(os.path.dirname(__file__), 'data')
sound_path = os.path.join(data_path, 'sound-files')


def data_file_path(fn):
    return os.path.join(data_path, fn)

def sound_file_path(fn):
    return os.path.join(data_path, 'sound-files', fn)


wav_fns = sorted([sound_file_path(fn) for fn in os.listdir(sound_path) if fn.endswith('.wav')])


def sample_data_fn(fn, folder, col_name, sample):
    """Return the filename corresponding to fn, folder, col_name, f0_base,
       and sample.

    Which is those components separated by dashes, with '.txt' appended,
    with the data_file_path as prefix.  The data contains raw Snack samples.
    """
    fn = os.path.splitext(os.path.basename(fn))[0]
    fn = '-'.join(('sample', fn, col_name, sample))
    fn = os.path.join(data_path, folder, fn) + '.txt'
    return fn

def get_raw_data(fn, var, f0_alg, fmt_alg, bw_method):
    """ Get raw VoiceSauce output data for variable `var` for analysis on file `fn`

    The parameters f0_alg, fmt_alg, bw_method correspond to
        f0_alg   - F0 algorithm used for F0 and harmonic parameter estimation
        fmt_alg  - Algorithm used for formant parameter estimation
        bw_method - Method for estimating bandwidth

    These parameters are used in VoiceSauce settings
    """
    base_fn = os.path.splitext(os.path.basename(fn))[0]
    data_dir = os.path.join(data_path, 'raw-vs-output', f0_alg + '-' + fmt_alg + '-' + bw_method)
    fn_path = os.path.join(data_dir, base_fn + '.json')
    with open(fn_path, 'r') as f:
        json_data = json.load(f)

    if isinstance(json_data[var], list):
        var_data = np.array(json_data[var])
    else:
        var_data = json_data[var]

    return var_data

def get_test_data(fn, col_name, f0_base, sample):
    """Get frame and col_name data from output file named by f0_base and sample.

    That is, given fn, return the data produced from that input file
    (the filenames appear in the first column), taking the data from the output
    file whose name has f0_base (sf0, pf0, shrf0, strf0) and sample (1ms, 9seg)
    in it.  Return a list of tuples consisting of the frame offset (t_ms) and
    the data from the column named by col_name, converted to floats.

    """
    in_name = os.path.splitext(os.path.basename(fn))[0]
    fn = os.path.join(data_path, 'output-' + f0_base + '-' + sample + '.txt')
    res = []
    with open(fn) as f:
        c = csv.DictReader(f, dialect=csv.excel_tab)
        for row in c:
            if row['Filename'].startswith(in_name):
                res.append((float(row['t_ms']), float(row[col_name])))
    return res


def get_sample_data(*args):
    """Return sample python data from sample_data_fn(*args).
    """
    return np.loadtxt(sample_data_fn(*args), dtype=float)


def load_json(fn):
    """Load the json file fn"""
    with open(data_file_path(fn) + '.json') as f:
        data = json.load(f)
    # Convert lists of numbers to NumPy arrays
    for k in data:
        if isinstance(data[k], list):
            data[k] = np.array(data[k])

    return data


class TestCase(unittest.TestCase):

    longMessage = True

    def tmpdir(self):
        tmpdir = TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        return tmpdir.name

    # Python3 compat
    if py2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
        assertRegex = unittest.TestCase.assertRegexpMatches

    def assertAllClose(self, first, second, rtol=1e-05, atol=1e-08, equal_nan=False, msg=None):
        """Fail if the two NumPy arrays are not close enough as determined by
        relative tolerance (rtol) and absolute tolerance (atol)
        """
        if not isinstance(first, np.ndarray):
            raise self.failureException('First object is not a NumPy array')
        if not isinstance(second, np.ndarray):
            raise self.failureException('Second object is not a NumPy array')

        if first.shape != second.shape:
            raise self.failureException('Numpy arrays being compared have different shapes')

        if equal_nan:
            all_close = (np.isclose(first, second, rtol=rtol, atol=atol) | (np.isnan(first) & np.isnan(second))).all()
            if not all_close:
                idx = np.where(np.isclose(first, second, rtol=rtol, atol=atol) | (np.isnan(first) & np.isnan(second)) == False)
        else:
            all_close = np.allclose(first, second, rtol=rtol, atol=atol)
            if not all_close:
                idx = np.where(np.isclose(first, second, rtol=rtol, atol=atol) == False)

        if not all_close:
            msg = self._formatMessage(msg, "NumPy arrays fail to be close within rtol = %s and atol = %s.  Out of %s entries, %s differ." % (rtol, atol, first.size, len(idx[0])))
            raise self.failureException(msg)

    @contextlib.contextmanager
    def assertArgparseError(self, expected_regex, expected_regex_3=None):
        with self.assertRaises(SystemExit):
            with self.captured_output('stderr') as out:
                yield out
        msg = out.getvalue()
        if not py2 and expected_regex_3 is not None:
            expected_regex = expected_regex_3

        # HACK: Change backslashes to normal slashes on Windows
        #       because backslashes are special characters in regex
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            msg = msg.replace('\\\\', '/')
            expected_regex = [regex.replace('\\', '/') for regex in expected_regex]

        for regex in expected_regex:
            self.assertRegex(msg, regex)

    @contextlib.contextmanager
    def captured_output(self, stream_name):
        """Return a context manager that temporarily replaces the sys stream
        *stream_name* with a StringIO and returns it."""
        orig_stdout = getattr(sys, stream_name)
        setattr(sys, stream_name, StringIO())
        try:
            yield getattr(sys, stream_name)
        finally:
            setattr(sys, stream_name, orig_stdout)

    # A minimal version of patch good enough for our needs.
    @contextlib.contextmanager
    def patch(self, obj, attr, value):
        old_val = getattr(obj, attr)
        setattr(obj, attr, value)
        yield
        obj.attr = old_val


def parameterize(cls):
    """A test method parameterization class decorator.

    Parameters are specified as the value of a class attribute that ends with
    the string '_params'.  Call the portion before '_params' the prefix.  Then
    a method to be parameterized must have the same prefix, the string
    '_as_', and an arbitrary suffix.

    The value of the _params attribute may be either a dictionary or a list.
    The values in the dictionary and the elements of the list may either be
    single values, or a list.  If single values, they are turned into single
    element tuples.  However derived, the resulting sequence is passed via
    *args to the parameterized test function.

    In a _params dictionary, the keys become part of the name of the generated
    tests.  In a _params list, the values in the list are converted into a
    string by joining the string values of the elements of the tuple by '_' and
    converting any blanks into '_'s, and this become part of the name.
    The  full name of a generated test is a 'test_' prefix, the portion of the
    test function name after the  '_as_' separator, plus an '_', plus the name
    derived as explained above.

    For example, if we have:

        count_params = range(2)

        def count_as_foo_arg(self, foo):
            self.assertEqual(foo+1, myfunc(foo))

    we will get parameterized test methods named:
        test_foo_arg_0
        test_foo_arg_1
        test_foo_arg_2

    Or we could have:

        example_params = {'foo': ('bar', 1), 'bing': ('bang', 2)}

        def example_as_myfunc_input(self, name, count):
            self.assertEqual(name+str(count), myfunc(name, count))

    and get:
        test_myfunc_input_foo
        test_myfunc_input_bing

    Note: if and only if the generated test name is a valid identifier can it
    be used to select the test individually from the unittest command line.

    """
    paramdicts = {}
    testers = collections.defaultdict(list)
    for name, attr in cls.__dict__.items():
        if name.endswith('_params'):
            if not hasattr(attr, 'keys'):
                d = {}
                for x in attr:
                    if not hasattr(x, '__iter__') or hasattr(x, 'encode'):
                        x = (x,)
                    n = '_'.join(str(v) for v in x).replace(' ', '_')
                    d[n] = x
                attr = d
            paramdicts[name[:-7] + '_as_'] = attr
        if '_as_' in name:
            testers[name.split('_as_')[0] + '_as_'].append(name)
    testfuncs = {}
    for name in paramdicts:
        if name not in testers:
            raise ValueError("No tester found for {}".format(name))
    for name in testers:
        if name not in paramdicts:
            raise ValueError("No params found for {}".format(name))
    for name, attr in cls.__dict__.items():
        for paramsname, paramsdict in paramdicts.items():
            if name.startswith(paramsname):
                testnameroot = 'test_' + name[len(paramsname):]
                for paramname, params in paramsdict.items():
                    test = (lambda self, name=name, params=params: getattr(self, name)(*params))
                    testname = testnameroot + '_' + paramname
                    test.__name__ = testname
                    testfuncs[testname] = test
    for key, value in testfuncs.items():
        setattr(cls, key, value)
    return cls

def CLI_output(test_case, delimiter, args):
    with test_case.captured_output('stdout') as sout:
        CLI(args).process()
    lines = sout.getvalue().splitlines()
    return [l.split(delimiter) for l in lines]
