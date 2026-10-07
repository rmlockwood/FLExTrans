@echo off
setlocal

REM Compiles every translation .ts file in the Dev source folders into a .qm file in Dev\CompiledTranslations. Works from any current directory in any developer's clone.
REM It is driven by the .ts files rather than the .py files, so there is no list of .py files to exclude, and a .ts whose name doesn't match a .py (e.g. RuleAssistant_*.ts,
REM used by RuleAssistantPy.py) still gets compiled. The base <name>.ts (no language suffix) is the untranslated source copy and is skipped because it doesn't match *_<lang>.ts.

REM Load the translation language codes (LANG_CODES) from the generated file - the authoritative list is Dev\Lib\UILanguages.py
call "%~dp0lang_codes.bat"

REM Define directories to process
set directories=TopLevel Modules Lib Lib\Windows

REM Define target folder - the CompiledTranslations folder beside this script (%~dp0 is this script's folder, with a trailing backslash)
set destination=%~dp0CompiledTranslations

REM Make sure the compiler is available - it comes from PySide6-Essentials in Dev\requirements-dev.txt
where pyside6-lrelease >nul 2>&1

if errorlevel 1 (

    echo pyside6-lrelease was not found. Install it with: python -m pip install -r "%~dp0requirements-dev.txt"
    pause
    exit /b 1
)

REM Loop through each directory
for %%D in (%directories%) do (

    echo Processing directory %%D...

    REM Compile each <name>_<lang>.ts in the directory's translations folder to <name>_<lang>.qm
    for %%L in (%LANG_CODES%) do (

        for %%T in ("%~dp0%%D\translations\*_%%L.ts") do (

            pyside6-lrelease "%%T" -qm "%destination%\%%~nT.qm"
        )
    )
)

echo Done!
endlocal
pause
