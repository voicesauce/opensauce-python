Test data
=========

Sound files (.wav and corresponding .TextGrid files) are in the directory
`sound-files`.  These are the input data to the algorithms.

The other directories contain test data for various test scripts.  The name of
the directory corresponds with the name of the test script.  For example, the
directory `shrp` contains the test data for `test_shrp.py`.

The JSON files can be rather large.  Since they contain test data and will
never be changed, we use [Git LFS](https://git-lfs.github.com/) to manage these
files.
