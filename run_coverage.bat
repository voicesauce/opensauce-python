REM This is a Windows batch file for running coverage and generating a report
REM on the core OpenSauce code
coverage run -m unittest test
coverage report -m --include=opensauce\*
