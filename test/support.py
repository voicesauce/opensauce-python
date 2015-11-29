import csv
import os
import unittest

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


data_path = os.path.join(os.path.dirname(__file__), 'data')

def data_file_path(fn):
    return os.path.join(data_path, fn)

wav_fns = sorted([data_file_path(fn) for fn in os.listdir(data_path)
                                     if fn.endswith('.wav')])

def get_test_data(fn, col_name, f0_base, sample):
    """Get frame and col_name data from output file named by f0_base and sample.

    That is, given fn as input, return the data produced from that input file
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
                res.append(( float(row['t_ms']), float(row[col_name])))
    return res

def get_text_grid(fn):
    in_name = os.path.splitext(os.path.basename(fn))[0]
    tg_fn = data_file_path(in_name + '.TextGrid')
    return TextGrid.load(tg_fn)


# My past experience is that I eventually write helpers that wrap unittest
# resources and use them in a number of test cases.  These helpers need access
# to the underlying unittest.TestCase, so it is easiest to write them as
# methods on a subclass.  So, I'll create a subclass now that doesn't have any
# extra methods, to make it easy to add them later without having to touch all
# the then-existing test cases.

class TestCase(unittest.TestCase):
    pass
