@echo off
setlocal enabledelayedexpansion

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
