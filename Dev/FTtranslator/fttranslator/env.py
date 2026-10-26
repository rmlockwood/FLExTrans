#
#   fttranslator/env
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Sets up the process so FLExTrans modules can be imported and run outside FlexTools.
#
#   OVERVIEW (AI generated, then edited)
#
#   FLExTrans modules assume FlexTools has loaded them from a work project. FTtranslator runs them from a plain Python process, so this file recreates what FlexTools would have set up, once,
#   before anything imports a FLExTrans module. Everything else in FTtranslator calls bootstrap() first (through Translator) and then imports FLExTrans code lazily inside its functions.
#
#   WHAT FLEXTRANS EXPECTS
#
#    - The working directory is <work project>\Config. FTPaths and flextoolslib's FTConfig read os.getcwd() when they are imported, so the chdir must happen before the first FLExTrans or
#      flextoolslib import. Doing it later silently points FLExTrans at the wrong project.
#    - The FLExTrans Modules folder and its Lib folder are on sys.path. FlexTools does this with Modules\subdirs.pth. Two layouts are supported: an installed FLExTrans (Modules\FLExTrans with a
#      Lib folder inside it) and this repo (Dev\Modules beside Dev\Lib, Dev\Lib\Windows and Dev\TopLevel). The installed FlexTools folder is also added, since Version.py lives there.
#    - A QApplication exists. FLExTrans modules create one when imported; no window opens on the drafting path, so Qt is told to run offscreen.
#    - Mixpanel.LogModuleStarted is harmless. It can show a modal message box and calls the network, so it is replaced with a no-op.
#
#   FIELDWORKS START-UP ORDER
#
#   Two libraries load FieldWorks: flexlibs (used inside FLExTrans) and flexicon (used by FTtranslator's own steps, through parse_priority.fw). Both need FieldWorks loaded before SIL.LCModel can
#   be imported. flexlibs must go first: it fails if the SLDR is already initialized, and flexicon doesn't mind. Swapping the two gives "SLDR has already been initialized".
#
#   ONE WORK PROJECT PER PROCESS
#
#   The chdir and sys.path changes can't be undone safely once FLExTrans modules are imported, so bootstrap() only sets up once. A second call for the same work project returns the same Env; a
#   call for a different one raises.
#
#   CODE STRUCTURE
#
#   Env holds the folders found for a work project. locate() works them out without importing anything, so it can be used (and tested) before set-up. bootstrap() calls locate() and then makes
#   the process changes described above. cleanup() shuts FieldWorks down at the end; cli.main() calls it.
#

import os
import sys
from pathlib import Path

# The Env for this process once bootstrap() has run, otherwise None
_state = None

# FLExTrans\Dev, the folder this package sits two levels below. --modules dev uses its Modules folder.
DEV_DIR = Path(__file__).resolve().parents[2]

class Env:
    '''The FLExTrans folders for one work project. libDirs is filled in by locate(); qtApp by bootstrap() when it has to create the QApplication.'''

    def __init__(self, workDir, ftRoot, modulesDir):

        # The FLExTrans work project, the folder holding FlexTools\ and WorkProjects\, and the FLExTrans modules folder (...\Modules\FLExTrans or Dev\Modules)
        self.workDir = workDir
        self.ftRoot = ftRoot
        self.modulesDir = modulesDir
        self.libDirs = []
        self.qtApp: object | None = None

    @property
    def configDir(self):

        return self.workDir / "Config"

    @property
    def modulesRoot(self):
        '''The folder that collection entries like 'FLExTrans\\X.py' are relative to.'''

        return self.modulesDir.parent

    @property
    def toolsDir(self):

        return self.ftRoot / "FlexTools" / "Tools"

def locate(workDir, modulesDir=None):
    '''Work out the FLExTrans folders for a work project without importing anything. modulesDir is None (the installed modules next to the work project), 'dev' (this repo's Dev\\Modules)
       or a path to a modules folder.'''

    workDir = Path(workDir).resolve()

    if not (workDir / "Config" / "FlexTrans.config").exists():

        raise SystemExit(f"'{workDir}' is not a FLExTrans work project (no Config\\FlexTrans.config)")

    # FTPaths.ROOT_DIR is derived the same way: two levels above the work project
    ftRoot = workDir.parent.parent

    if modulesDir == "dev":

        # This package lives in FLExTrans\Dev\FTtranslator; use the repo's own Dev\Modules
        modulesDir = DEV_DIR / "Modules"

    elif modulesDir:

        modulesDir = Path(modulesDir).resolve()
    else:
        modulesDir = ftRoot / "FlexTools" / "Modules" / "FLExTrans"

    if not (modulesDir / "ExtractSourceText.py").exists():

        raise SystemExit(f"No FLExTrans modules in '{modulesDir}'. Use --modules to point at an installed ...\\FlexTools\\Modules\\FLExTrans or a FLExTrans Dev\\Modules folder.")

    env = Env(workDir, ftRoot, modulesDir)

    # An installed FLExTrans keeps Lib inside the modules folder; the repo has Dev\Modules beside Dev\Lib
    if (modulesDir / "Lib").is_dir():

        env.libDirs = [modulesDir / "Lib"]
    else:
        devDir = modulesDir.parent
        env.libDirs = [path for path in (devDir / "Lib", devDir / "Lib" / "Windows", devDir / "TopLevel") if path.is_dir()]

    return env

def bootstrap(workDir, modulesDir=None):
    '''Make FLExTrans importable and runnable headless for the given work project, and return its Env. Must run before anything imports a FLExTrans module. See WHAT FLEXTRANS EXPECTS above.'''

    global _state

    # Only once per process, and only for one work project
    if _state is not None:

        if _state.workDir != Path(workDir).resolve():

            raise RuntimeError("FLExTrans is already set up for another work project in this process")

        return _state

    env = locate(workDir, modulesDir)

    # parse_priority sits next to this package; keep it importable after the chdir
    packageParent = str(Path(__file__).resolve().parent.parent)

    if packageParent not in sys.path:

        sys.path.insert(0, packageParent)

    # The chdir has to come before any FLExTrans or flextoolslib import
    os.chdir(env.configDir)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    extraPaths = [str(env.modulesDir)] + [str(path) for path in env.libDirs]

    # Version.py lives in the FlexTools folder when FLExTrans is installed
    if (env.ftRoot / "FlexTools").is_dir():

        extraPaths.append(str(env.ftRoot / "FlexTools"))

    sys.path[:0] = [path for path in extraPaths if path not in sys.path]

    # flexlibs has to initialize FieldWorks before flexicon does. See FIELDWORKS START-UP ORDER above.
    import flexlibs
    flexlibs.FLExInitialize()

    from parse_priority import fw
    fw.loadLcm()

    # FLExTrans modules expect a QApplication; it runs offscreen
    from PyQt6.QtWidgets import QApplication

    if QApplication.instance() is None:

        env.qtApp = QApplication(["FTtranslator"])

    # Mixpanel can show a modal message box and calls the network, so turn it into a no-op
    import Mixpanel
    Mixpanel.LogModuleStarted = lambda *args, **kwargs: None

    _state = env
    return env

def cleanup():
    '''Shut FieldWorks down, if bootstrap() started it.'''

    if _state is None:

        return

    import flexlibs
    flexlibs.FLExCleanup()
