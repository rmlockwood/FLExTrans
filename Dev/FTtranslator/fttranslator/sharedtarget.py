#
#   fttranslator/sharedtarget
#
#   Ron Lockwood
#   SIL International
#   10/27/26
#
#   Version 3.17.1 - 10/27/26 - Ron Lockwood
#    Initial version. Keeps the target project open across steps and runs, handing every FLExTrans module that opens it the one open copy.
#
#   OVERVIEW (AI generated, then edited)
#
#   The FLExTrans modules each open the target project themselves (Build Bilingual Lexicon, Catalog Target Affixes, the synthesis and Insert Target Text), always with flexlibs' FLExProject, and
#   close it again before they return. The first open in a process takes a couple of seconds - FieldWorks reads the whole .fwdata file and .NET compiles the code path - and every later open
#   about 0.2 s. SharedTarget opens the target once and keeps it open for the Translator's lifetime, so a session of translations (the interactive command) pays the first-open cost only once.
#
#   HOW THE MODULES GET THE SHARED COPY
#
#   The modules aren't changed. For the length of a run, patched() replaces FLExProject.OpenProject and FLExProject.CloseProject on the flexlibs class itself, which every module imports
#   (from flexlibs import FLExProject). When a module opens the configured target project, OpenProject opens it for real the first time, into an object SharedTarget owns, and makes the
#   module's own FLExProject a view over the same LcmCache, as Translator's flexlibsView() does for the source. The module's CloseProject() on that view does nothing but drop the view's
#   reference. Opening any other project goes through to the real OpenProject unchanged.
#
#   SAVING
#
#   flexlibs opens a write-enabled project inside one session-long non-undoable task and only saves when the project is closed. A shared target is never closed between runs, so save() ends
#   the task, saves if anything changed and starts a new task; Translator calls it after every run. Insert Target Text is what changes the target, and Generate HC Config (HermitCrab synthesis)
#   reads the .fwdata file from disk, so the file must be current before the next run.
#
#   TRAPS
#
#    - The shared copy is always opened write-enabled, even when a module asks for read-only, since a later module in the same run may write to it. A view still reports writeEnabled=True.
#    - The view's CloseProject() deletes its project attribute. If a module kept its FLExProject and called CloseProject() again after the patch is gone, the real CloseProject() finds no
#      project and does nothing, instead of disposing the cache everyone else is still using.
#    - Changes made in FLEx (with sharing on) while the target is held open may not be seen until the Translator is closed and created again.
#
#   CODE STRUCTURE
#
#   projectKey() reduces a project setting (a name or a .fwdata path) to a comparable key. SharedTarget holds the open target: patched() installs the OpenProject/CloseProject replacements
#   for a run, _openFor() makes a module's FLExProject a view, save() writes changes, and close() saves and closes it for good.
#

import contextlib
from pathlib import Path

def projectKey(projectName):
    '''A project setting as a comparable key: its name, lowercased. A .fwdata path is reduced to the file's stem, which is the project name.'''

    name = str(projectName)

    if name.lower().endswith(".fwdata"):

        name = Path(name).stem

    return name.casefold()

class SharedTarget:
    '''The target project, opened once and shared by every FLExTrans module that opens it. See the OVERVIEW above.'''

    def __init__(self, projectName):

        self.projectName = projectName
        self.owner = None   # the flexlibs FLExProject that really opened the target, once something has asked for it

    @contextlib.contextmanager
    def patched(self):
        '''For the length of the with block, make every flexlibs FLExProject that opens the target project share this one open copy.'''

        from flexlibs import FLExProject

        originalOpen = FLExProject.OpenProject
        originalClose = FLExProject.CloseProject
        shared = self

        # These become FLExProject methods, so their first parameter is the module's FLExProject. It is named self to match the methods they replace; this SharedTarget is shared.
        def openProject(self, projectName, writeEnabled=False):

            if projectKey(projectName) != projectKey(shared.projectName):

                return originalOpen(self, projectName, writeEnabled)

            shared._openFor(self, originalOpen)

        def closeProject(self):

            # A view: drop the reference and leave the shared copy open
            if getattr(self, "fttSharedView", False):

                del self.project
                return

            originalClose(self)

        FLExProject.OpenProject = openProject
        FLExProject.CloseProject = closeProject

        try:
            yield
        finally:
            FLExProject.OpenProject = originalOpen
            FLExProject.CloseProject = originalClose

    def _openFor(self, project, originalOpen):
        '''Make project (a module's FLExProject) a view over the shared target, opening the target first if this is the first time. An error opening it reaches the module as usual.'''

        from flexlibs import FLExProject

        if self.owner is None:

            owner = FLExProject()

            # Write-enabled even if this module only reads; see TRAPS above
            originalOpen(owner, self.projectName, True)
            self.owner = owner

        project.project = self.owner.project
        project.lp = self.owner.lp
        project.lexDB = self.owner.lexDB
        project.writeEnabled = self.owner.writeEnabled
        project.fttSharedView = True

    def save(self):
        '''Write the shared target's changes to disk, keeping it open. Does nothing if the target hasn't been opened. See SAVING above.'''

        if self.owner is None:

            return

        # IUndoStackManager is imported by flexlibs, which uses it the same way in CloseProject()
        from flexlibs.code.FLExProject import IUndoStackManager  # type: ignore

        accessor = self.owner.project.MainCacheAccessor
        accessor.EndNonUndoableTask()

        try:
            undoStackManager = self.owner.ObjectRepository(IUndoStackManager)

            if undoStackManager.HasUnsavedChanges:

                undoStackManager.Save()

        finally:
            accessor.BeginNonUndoableTask()

    def close(self):
        '''Save and close the shared target for good. Safe to call when it was never opened, or more than once.'''

        if self.owner is None:

            return

        owner = self.owner
        self.owner = None

        # The real CloseProject: the patch is only in place during a run, and owner is not a view anyway
        owner.CloseProject()
