"""
Getting FLExTrans' code to run outside FlexTools.

FLExTrans modules assume they are loaded by FlexTools from a work project:
  * FTPaths and flextoolslib's FTConfig read os.getcwd() when imported, so the
    working directory must be <WorkProject>\\Config before any FT import;
  * the modules and Lib folders must be on sys.path (FlexTools does that with
    Modules\\subdirs.pth);
  * modules create a QApplication when imported (no window is shown on the
    drafting path, so Qt runs offscreen);
  * Mixpanel.LogModuleStarted can pop up a message box and calls the network.

bootstrap() takes care of all of this. It must run before anything imports
FLExTrans modules, and it can only be done once per process.
"""

import os
import sys
from pathlib import Path

_state = None
DEV_DIR = Path(__file__).resolve().parents[2]  # FLExTrans\Dev


class Env:
    def __init__(self, work_dir, ft_root, modules_dir):
        self.work_dir = work_dir        # the FLExTrans work project
        self.ft_root = ft_root          # holds FlexTools\ and WorkProjects\
        self.modules_dir = modules_dir  # FLExTrans modules (…\Modules\FLExTrans or Dev\Modules)
        self.lib_dirs = []

    @property
    def config_dir(self):
        return self.work_dir / "Config"

    @property
    def modules_root(self):
        """The folder collection entries like 'FLExTrans\\X.py' are relative to."""
        return self.modules_dir.parent

    @property
    def tools_dir(self):
        return self.ft_root / "FlexTools" / "Tools"


def locate(work_dir, modules_dir=None):
    """Work out the FLExTrans folders for a work project without importing anything."""
    work_dir = Path(work_dir).resolve()
    if not (work_dir / "Config" / "FlexTrans.config").exists():
        raise SystemExit(f"'{work_dir}' is not a FLExTrans work project "
                         f"(no Config\\FlexTrans.config)")
    ft_root = work_dir.parent.parent  # FTPaths.ROOT_DIR is derived the same way
    if modules_dir == "dev":
        # This package lives in FLExTrans\Dev\FTtranslator; use the repo's own Dev\Modules.
        modules_dir = DEV_DIR / "Modules"
    elif modules_dir:
        modules_dir = Path(modules_dir).resolve()
    else:
        modules_dir = ft_root / "FlexTools" / "Modules" / "FLExTrans"
    if not (modules_dir / "ExtractSourceText.py").exists():
        raise SystemExit(f"No FLExTrans modules in '{modules_dir}'. Use --modules to point at "
                         f"an installed ...\\FlexTools\\Modules\\FLExTrans or a FLExTrans Dev\\Modules folder.")
    env = Env(work_dir, ft_root, modules_dir)
    if (modules_dir / "Lib").is_dir():          # installed layout
        env.lib_dirs = [modules_dir / "Lib"]
    else:                                       # FLExTrans repo: Dev\Modules + Dev\Lib
        dev = modules_dir.parent
        env.lib_dirs = [p for p in (dev / "Lib", dev / "Lib" / "Windows", dev / "TopLevel") if p.is_dir()]
    return env


def bootstrap(work_dir, modules_dir=None):
    global _state
    if _state is not None:
        if _state.work_dir != Path(work_dir).resolve():
            raise RuntimeError("FLExTrans is already set up for another work project in this process")
        return _state
    env = locate(work_dir, modules_dir)

    # parse_priority sits next to this package; keep it importable after the chdir.
    here = str(Path(__file__).resolve().parent.parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    os.chdir(env.config_dir)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    extra = [str(env.modules_dir)] + [str(p) for p in env.lib_dirs]
    if (env.ft_root / "FlexTools").is_dir():
        extra.append(str(env.ft_root / "FlexTools"))  # Version.py lives here when installed
    sys.path[:0] = [p for p in extra if p not in sys.path]

    # flexicon (used for our own steps) and flexlibs (used inside FLExTrans) both
    # need FieldWorks loaded before SIL.LCModel can be imported. flexlibs has to
    # go first: it fails if the SLDR is already initialized, flexicon doesn't.
    import flexlibs
    flexlibs.FLExInitialize()
    from parse_priority import fw
    fw.load_lcm()

    from PyQt6.QtWidgets import QApplication
    if QApplication.instance() is None:
        env.qt_app = QApplication(["FTtranslator"])

    import Mixpanel
    Mixpanel.LogModuleStarted = lambda *args, **kwargs: None

    _state = env
    return env


def cleanup():
    if _state is None:
        return
    import flexlibs
    flexlibs.FLExCleanup()
