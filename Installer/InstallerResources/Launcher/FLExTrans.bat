@echo off
rem Start FLExTrans for the project in this folder. The installer puts a copy of this file in each WorkProjects\[project] folder.
rem Change to the folder this file is in (%~dp0) so the relative paths below, and any FLExTrans uses, resolve against this project, even when the file is started from elsewhere.
rem That also keeps a copied project folder (e.g. "TemplateProject - Copy") pointing at its own settings, which a Windows shortcut would not, since it stores absolute paths.
cd /d "%~dp0"

rem pyw runs Python without a console window, and start lets this window close straight away.
start "" pyw -3.13 ..\..\FlexTools\FLExTrans.py .\Config\flextools.ini
