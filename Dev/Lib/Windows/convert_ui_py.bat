Rem convert_ui_py.bat [ui file name without extension, e.g. Linker]
rem %~n1 strips the extension from the first argument, leaving just the filename.
set FILENAME=%~n1

py -m PyQt6.uic.pyuic %FILENAME%.ui -o %FILENAME%.py