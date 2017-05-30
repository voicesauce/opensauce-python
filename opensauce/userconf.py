# Additional configuration

# User defined global variables

# Snack calling method
# Choices are 'exe', 'python', 'tcl'
# Setting it to None, uses the default for your operating system
user_default_snack_method = None

# Tcl shell command name
# Typically, something like 'tclsh', 'tclsh8.4', 'wish', 'wish8.4', etc.
# If the variable is set to None, 'tclsh' is used
user_tcl_shell_cmd = None

# Python command name
# On some Linux distributions, the 'python' command refers to Python 2,
# whereas on other Linux distributions, it refers to Python 3
# For greater flexibility, you can set which Python you want to use,
# e.g. 'python', 'python2', 'python3'
# If the variable is set to None, 'python' is used
#
# This variable only matters for running the unit tests
user_python_cmd = None
