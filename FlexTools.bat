@echo off

REM Assume that the default Python will match FLEx for 32/64 bit.
REM If it doesn't, then the user needs to install the correct Python
REM or call FLExTools.py manually with the correct Python.exe.

rem Edit FTPaths.py with the current work project
cd Build
py -3.7-64 SetWorkingProject.py

rem change flextools default and go to the flextools folder before running
cd ..\..\..\FlexTools
py -3.7-64 FlexTools.py %*

:END
