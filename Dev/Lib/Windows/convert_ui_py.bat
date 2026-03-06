Rem convert_ui_py.bat [ui file name without extension, e.g. Linker]
py -m PyQt6.uic.pyuic %1.ui -o %1.py