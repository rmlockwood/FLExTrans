@echo off
rem Start FLExTrans for the project in this folder with a console window that stays open, so any startup error can be read.
rem Not installed; copy it into a WorkProjects\[project] folder when helping a user whose FLExTrans won't start.
cd /d "%~dp0"
py -3.13 ..\..\FlexTools\FLExTrans.py .\Config\flextools.ini
pause
