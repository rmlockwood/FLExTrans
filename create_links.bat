@echo off
setlocal enabledelayedexpansion

REM Set the variables batch_dir and git_dev to the appropriate directories on your machine.

REM batch_dir points to a folder inside of where you have FLExTrans installed for testing your development work.
REM More specifically, inside that installation, find the path FlexTools\Modules\FLExTrans

REM git_dev points to the Dev folder inside your FLExTrans github repo folder.
REM This path must not have any spaces in it (in order for the symbolic linking to work).

REM You will probably need to run this .bat file "as Administrator"
REM This script now deletes all symbolic links in each folder before recreating them.

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

REM Initialize last_dir to an empty value
set last_dir=

REM Loop through each pair of current and target directories
for /L %%j in (0, 1, %array_size%) do (
    set current_dir=!current_dir_array[%%j]!
    set target_dir=!target_dir_array[%%j]!
    
    REM Change to the corresponding current directory
    echo Changing to directory: %batch_dir%\!current_dir!
    cd /d "%batch_dir%\!current_dir!"
    
    REM Delete existing symbolic links if current_dir is different from last_dir
    if not "!current_dir!"=="!last_dir!" (
        for /f "delims=" %%k in ('dir /a:l /b') do (
            echo Deleting symbolic link: %%k
            del "%%k"
        )
    )

    REM Loop through each file in the target directory
    for %%f in ("%git_dev%\!target_dir!\*.py") do (
        REM Extract just the file name
        set file_name=%%~nf
        REM Create the symbolic link in the current directory
        echo Creating symbolic link
        mklink "!file_name!.py" "%%f"
    )
    
    REM Update last_dir to the current directory
    set last_dir=!current_dir!
)

endlocal
pause