Rem convert_ui_py.bat [ui file name without extension, e.g. Linker]
%python3%\python -m PyQt5.uic.pyuic %1.ui -o %1.py