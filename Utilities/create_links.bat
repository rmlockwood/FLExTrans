@echo off
setlocal enabledelayedexpansion

REM Set the variables git_repo  and testing_folder (below) to the appropriate directories on your machine.
REM If the path has spaces in it (e.g., in one of the folder names), the linking will fail, and you'll 
REM need to put your files into a path that doesn't have spaces in it.

REM You will probably need to run this .bat file "as Administrator"
REM This script now deletes all symbolic links in each folder before recreating them.

REM To get the localized binaries, create a translations folder under FlexTools\Modules\FLExTrans
REM Then run this script to get links to all the translation binary files.

REM This is your GitHub repo, where your source files are
REM Under this you would see folders like Apertium4Windows, Dev, Doc, etc.
set git_repo=C:\Users\<User>\Documents\GitHub\FLExTrans

REM This is the folder where you have your installation for testing.
REM Under this you would see folders like FlexTools, WorkProjects, etc.
REM The symbolic links (that point back to the repo files) will be created here.
set testing_folder=C:\Users\<User>\Documents\FLExTrans

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
    
    REM Delete existing FILE symbolic links if current_dir is different from last_dir. /a:l-d lists reparse points that are not directories, so the Lib\css and Lib\AI directory links
    REM created below are left alone here (they are refreshed in their own block after the loop).
    if not "!current_dir!"=="!last_dir!" (
        for /f "delims=" %%k in ('dir /a:l-d /b') do (
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

REM Link the Lib data subfolders as whole directories so the testing Lib mirrors the repo: css (transfer_preview.css plus the Rule Assistant treeflex.css/rulegen.css) and AI (the derived
REM preview specs and the Work-on-Rules-with-AI conventions doc). These hold non-.py data files, so a directory link keeps every current and future file in them in sync with the repo.
REM cd into Lib first and use a relative link name (like the file loops above) so a space in the testing path doesn't break mklink's quoting.
cd /d "%modules_ft%\Lib"
for %%d in (css AI) do (
    if exist "%%d" (
        echo Removing existing directory link: Lib\%%d
        rmdir "%%d"
    )
    echo Creating directory link: Lib\%%d
    mklink /D "%%d" "%git_dev%\Lib\%%d"
)

endlocal
pause