import filecmp
import os
import unittest
from shutil import copytree
from subprocess import Popen, PIPE

from test.support import TemporaryDirectory, data_file_path

class TestCLI(unittest.TestCase):

    def test_default_setup(self):
        with TemporaryDirectory() as tmp:
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
            self.assertTrue(filecmp.cmp(d('defaults/sounds/cant_c5_19a.f0'),
                                        data_file_path('cant_c5_19a.f0')))
