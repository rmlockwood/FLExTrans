@echo off
setlocal enabledelayedexpansion

REM Define language codes
set lang_codes=de es fr

REM Define directories to process
set directories=TopLevel Modules Lib Lib\Windows

REM Define excluded files
set exclude_files=FLExTrans.py Version.py ClusterUtils.py ComboBox.py FTPaths.py MyTableView.py

REM Define target folder
set destination="C:\Data\FLExTrans\Dev\Active Projects\FlexTools\Modules\FLExTrans"

REM Loop through each directory
for %%D in (%directories%) do (

    REM Change to the directory
    pushd %%D
    echo Processing directory %%D...

    REM Find all .py files and process them
    for %%F in (*.py) do (
	
        set "filename=%%~nF"
		
        REM Check if the file is in the exclusion list
        set "skip=0"
        for %%X in (%exclude_files%) do (
            if /I "%%F"=="%%X" set "skip=1"
        )

        if !skip!==0 (
		
			for %%L in (%lang_codes%) do (
			
				lrelease translations\!filename!_%%L.ts -qm %destination%\translations\!filename!_%%L.qm
			)
        )

    )

    REM Return to previous directory
    popd
)

echo Done!
endlocal
pause

