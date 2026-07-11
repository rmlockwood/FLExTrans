set FILENAME=%~n1

rem Load the translation language codes (LANG_CODES) from the generated file - the authoritative list is Dev\Lib\UILanguages.py
call "%~dp0..\lang_codes.bat"

for %%L in (%LANG_CODES%) do lrelease translations\%FILENAME%_%%L.ts -qm "C:\Data\FLExTrans\Dev\Active Projects\FlexTools\Modules\FLExTrans\translations\%FILENAME%_%%L.qm"
