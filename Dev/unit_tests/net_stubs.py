"""
Populate sys.modules with lightweight stubs for .NET / SIL / Qt imports so
that FLExTrans source modules can be imported without FLEx or pythonnet.

Import this module BEFORE importing any FLExTrans module that has SIL or
clr at module level.  Uses setdefault() so real assemblies are never evicted
when FLEx *is* available.
"""
import sys
import types
from unittest.mock import MagicMock


def _qt_class(name, **extra):
    """Return a plain Python class usable as a Qt base class."""
    attrs = {
        '__init__': lambda self, *a, **kw: None,
        '__init_subclass__': classmethod(lambda cls, **kw: None),
    }
    attrs.update(extra)
    return type(name, (object,), attrs)


def _empty_mock():
    """MagicMock with __all__ = [] so `from mod import *` imports nothing."""
    m = MagicMock()
    m.__all__ = []
    return m


# ── Qt ────────────────────────────────────────────────────────────────────────
_qtwidgets = MagicMock()
for _n in (
    'QCheckBox', 'QComboBox', 'QDialog', 'QFileDialog', 'QFrame',
    'QGroupBox', 'QHBoxLayout', 'QInputDialog', 'QLabel', 'QLineEdit',
    'QListWidget', 'QMainWindow', 'QMessageBox', 'QPushButton',
    'QScrollArea', 'QSizePolicy', 'QSplitter', 'QTableWidget', 'QTextEdit',
    'QTreeWidget', 'QVBoxLayout', 'QWidget',
):
    setattr(_qtwidgets, _n, _qt_class(_n))

# QApplication needs instance() and exec() as class/static methods because
# ChapterSelection.py calls QApplication.instance() at module level.
_qtwidgets.QApplication = _qt_class(
    'QApplication',
    instance=classmethod(lambda cls: None),
    exec=lambda self: 0,
    exec_=lambda self: 0,
    quit=classmethod(lambda cls: None),
    processEvents=classmethod(lambda cls: None),
    setAttribute=classmethod(lambda cls, *a: None),
)

sys.modules.update({
    'PyQt6':           MagicMock(),
    'PyQt6.QtCore':    MagicMock(),
    'PyQt6.QtGui':     MagicMock(),
    'PyQt6.QtWidgets': _qtwidgets,
})

# ── .NET / SIL ────────────────────────────────────────────────────────────────
for _mod in (
    'clr',
    'System', 'System.IO', 'System.Collections',
    'SIL', 'SIL.LCModel',
    'SIL.LCModel.Core', 'SIL.LCModel.Core.Text',
    'SIL.LCModel.Core.KernelInterfaces',
    'SIL.LCModel.DomainServices', 'SIL.LCModel.Infrastructure',
):
    sys.modules.setdefault(_mod, _empty_mock())

# ── flexlibs ──────────────────────────────────────────────────────────────────
sys.modules.setdefault('flexlibs', _empty_mock())

# ── flextoolslib — export the FTM_* constants that modules use via `import *` ─
_ftlib = types.ModuleType('flextoolslib')
_ftlib_names = [
    'FTM_Name', 'FTM_Version', 'FTM_ModifiesDB', 'FTM_Synopsis',
    'FTM_Help', 'FTM_Description', 'FTM_Language', 'FTM_Scope',
    'FTM_Type', 'FTM_ResearchState', 'FTConfig', 'FlexToolsModuleClass',
]
setattr(_ftlib, '__all__', _ftlib_names)  # setattr avoids type-checker complaint on ModuleType
for _n in _ftlib_names:
    setattr(_ftlib, _n, MagicMock())
sys.modules.setdefault('flextoolslib', _ftlib)

# ── Project-specific deps that pull in .NET transitively ─────────────────────
for _mod in ('ClusterUtils', 'ComboBox', 'FTPaths', 'Mixpanel',
             'ReadConfig', 'RunApertium', 'TestbedValidator'):
    sys.modules.setdefault(_mod, MagicMock())
