import os

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
