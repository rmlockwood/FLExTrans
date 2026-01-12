@echo off
setlocal enabledelayedexpansion

REM Set the variables testing_folder and git_repo to the appropriate directories on your machine.

REM testing_folder points to a folder inside of where you have FLExTrans installed for testing your development work.
REM Under this you would see folders like FlexTools, Workprojects, etc.

REM git_repo points to the FLExTrans github repo folder. Under this you would see folders like Apertium4Windows, Dev, Doc, etc.
REM This path must not have any spaces in it (in order for the symbolic linking to work).

REM You will probably need to run this .bat file "as Administrator"
REM This script now deletes all symbolic links in each folder before recreating them.

REM To get the translation binaries, create a translations folder under FlexTools\Modules\FLExTrans
REM Then run this script to get links to all the translation binary files.

REM set testing_folder=C:\Users\<user>\Documents\FLExTrans
REM set git_repo=C:\Users\<user>\Documents\GitHub\FLExTrans
set testing_folder="C:\Data\FLExTrans\Dev\Active Projects"
set git_repo=c:\users\rlboo\GitHub\flextrans

REM add to the paths
set modules_ft=%testing_folder%\FlexTools\Modules\FLExTrans
set git_dev=%git_repo%\Dev

cd /d %modules_ft%

REM List of current directories relative to %batch_dir%
set current_dirs=.;Lib;Lib;..\..;translations

REM List of target directories relative to %git_dev%
set target_dirs=Modules;Lib;Lib\Windows;TopLevel;CompiledTranslations

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
    echo Changing to directory: %modules_ft%\!current_dir!
    cd /d "%modules_ft%\!current_dir!"
    
    REM Delete existing symbolic links if current_dir is different from last_dir
    if not "!current_dir!"=="!last_dir!" (
        for /f "delims=" %%k in ('dir /a:l /b') do (
            echo Deleting symbolic link: %%k
            del "%%k"
        )
    )

    REM Loop through Python files in the target directory
    for %%f in ("%git_dev%\!target_dir!\*.py") do (
        REM Extract just the file name
        set file_name=%%~nf
        REM Create the symbolic link in the current directory
        echo Creating symbolic link for Python file: %%~nxf
        mklink "!file_name!.py" "%%f"
    )
    
    REM Loop through QM files in the target directory
    for %%f in ("%git_dev%\!target_dir!\*.qm") do (
        REM Extract just the file name
        set file_name=%%~nf
        REM Create the symbolic link in the current directory
        echo Creating symbolic link for QM file: %%~nxf
        mklink "!file_name!.qm" "%%f"
    )
    
    REM Update last_dir to the current directory
    set last_dir=!current_dir!
)

endlocal
pause