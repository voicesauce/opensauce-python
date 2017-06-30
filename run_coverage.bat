REM This is a Windows batch file for running coverage and generating a report
REM on the core OpenSauce code
coverage run --branch --source=opensauce --omit=opensauce\textgrid.py -m unittest test
coverage report -m
coverage html
