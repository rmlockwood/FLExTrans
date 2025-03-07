@echo off
setlocal enabledelayedexpansion

set batch_dir="C:\Data\FLExTrans\Dev\Active Projects\FlexTools\Modules\FLExTrans"
set git_dev=c:\users\rlboo\GitHub\flextrans\Dev

cd /d %batch_dir%

REM List of current directories relative to %batch_dir%
set current_dirs=.;Lib;Lib;..\..

REM List of target directories relative to %git_dev%
set target_dirs=Modules;Lib;Lib\Windows;TopLevel

REM Convert the lists to arrays
set i=0
for %%d in (%current_dirs:;= %) do (
    set current_dir_array[!i!]=%%d
    set /a i+=1
)

set i=0
for %%d in (%target_dirs:;= %) do (
    set target_dir_array[!i!]=%%d
    set /a i+=1
)

set /a array_size=i-1

REM Loop through each pair of current and target directories
for /L %%j in (0, 1, %array_size%) do (
    set current_dir=!current_dir_array[%%j]!
    set target_dir=!target_dir_array[%%j]!
    
    REM Change to the corresponding current directory
    echo Changing to directory: %batch_dir%\!current_dir!
    cd /d "%batch_dir%\!current_dir!"
    
    REM Delete existing symbolic links
    for /f "delims=" %%k in ('dir /a:l /b') do (
        echo Deleting symbolic link: %%k
        del "%%k"
    )

    REM Loop through each file in the target directory
    for %%f in ("%git_dev%\!target_dir!\*.py") do (
        REM Extract just the file name
        set file_name=%%~nf
        REM Create the symbolic link in the current directory
        echo Creating symbolic link
        mklink "!file_name!.py" "%%f"
    )
)

endlocal
pause