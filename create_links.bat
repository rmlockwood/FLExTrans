@echo off
setlocal enabledelayedexpansion

REM Set the variables current_dir and git_dev to the appropriate directories on your machine.

REM current_dir points to a folder inside of where you have FLExTrans installed for testing your development work.
REM More specifically, inside that installation, find the path FlexTools\Modules\FLExTrans
REM After you install FLExTrans in this location, you will need to delete all the .py files that
REM got installed in the folders: FlexTools, FlexTools\Modules\FLExTrans, and FlexTools\Modules\FLExTrans\Lib
REM so that this script can create symbolic links in place of those real files.

REM git_dev points to the Dev folder inside your FLExTrans github repo folder.
REM This path must not have any spaces in it (in order for the symbolic linking to work).

REM You will probably need to run this .bat file "as Administrator"

set current_dir="C:\Data\FLExTrans\Dev\Test Projects\FlexTools\Modules\FLExTrans"
set git_dev=c:\users\rlboo\GitHub\flextrans\Dev

cd /d %current_dir%

REM Set the target directory path here
set target_dir=%git_dev%\Modules

REM Loop through each file in the target directory
for %%f in ("%target_dir%\*.py") do (
    REM Extract just the file name
    set file_name=%%~nf
    REM Create the symbolic link in the current directory
    mklink "%cd%\!file_name!%%~xf" "%%f"
)

cd %current_dir%\Lib

REM Set the target directory path here
set target_dir=%git_dev%\Lib

REM Loop through each file in the target directory
for %%f in ("%target_dir%\*.py") do (
    REM Extract just the file name
    set file_name=%%~nf
    REM Create the symbolic link in the current directory
    mklink "%cd%\!file_name!%%~xf" "%%f"
)

REM Set the target directory path here
set target_dir=%git_dev%\Lib\Windows

REM Loop through each file in the target directory
for %%f in ("%target_dir%\*.py") do (
    REM Extract just the file name
    set file_name=%%~nf
    REM Create the symbolic link in the current directory
    mklink "%cd%\!file_name!%%~xf" "%%f"
)

cd %current_dir%\..\..

REM Set the target directory path here
set target_dir=%git_dev%\TopLevel

REM Loop through each file in the target directory
for %%f in ("%target_dir%\*.py") do (
    REM Extract just the file name
    set file_name=%%~nf
    REM Create the symbolic link in the current directory
    mklink "%cd%\!file_name!%%~xf" "%%f"
)

endlocal
pause
