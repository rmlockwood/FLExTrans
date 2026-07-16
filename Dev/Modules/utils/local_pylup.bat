set FILENAME=%~n1

rem Load the translation language codes (LANG_CODES) from the generated file - the authoritative list is Dev\Lib\UILanguages.py
call "%~dp0..\..\lang_codes.bat"

for %%L in (%LANG_CODES%) do pylupdate5 -verbose %FILENAME%.py -ts translations\%FILENAME%_%%L.ts

rem The French .ts doubles as the base (untranslated-source) .ts after pylupdate has refreshed it
copy /y translations\%FILENAME%_fr.ts translations\%FILENAME%.ts
