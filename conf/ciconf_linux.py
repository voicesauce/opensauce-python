# Licensed under Apache v2 (see LICENSE)

# Additional configuration for testing purposes specific to Travis CI
# Do not change these options unless you are a developer or advanced user
# Users should set these options through the command line interface

# Snack calling method (equivalent to --snack-method CLI option)
# Choices are 'exe', 'python', 'tcl'
# Setting it to None, uses the default which is 'tcl'
user_default_snack_method = 'tcl'

# Tcl shell command name (equivalent to --tcl-cmd CLI option)
# Typically, something like 'tclsh', 'tclsh8.4', 'wish', 'wish8.4', etc.
# This can be useful for calling a particular version of Tcl, e.g. call Tcl8.5
# by setting the variable to 'tclsh8.5'
# If the variable is set to None, 'tclsh8.4' is used on OS X;
# otherwise 'tclsh' is used
user_tcl_shell_cmd = 'tclsh'

# Path for Praat executable
# If the variable is set to None, the default is used.  For Mac OS X, the
# default is '/Applications/Praat.app/Contents/MacOS/Praat'.  On Windows,
# the default is 'C:\Program Files\Praat.exe'.  On Linux, the default is
# '/usr/bin/praat'.
user_praat_path = '/usr/bin/praat'

# Path for REAPER executable
# An example for setting the path:
# user_reaper_path = '/home/myusername/REAPER/build/reaper'
user_reaper_path = '/usr/bin/reaper'
