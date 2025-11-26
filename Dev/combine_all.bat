@echo off
setlocal enabledelayedexpansion

REM Define language codes
set lang_codes=de es

REM Define target folder
set destination=C:\Users\rlboo\GitHub\FLExTrans\Dev\

REM Define directories to process
set directories=TopLevel Modules Lib Lib\Windows

REM Loop through each directory
for %%D in (%directories%) do (

    REM Change to the directory
    pushd %destination%\%%D\translations
    echo Processing directory %%D...

	py %destination%\combine_ts_files.py

    REM Return to previous directory
    popd
)

echo Done!
endlocal
pause

