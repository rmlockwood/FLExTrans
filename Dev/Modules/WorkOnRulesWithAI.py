#
#   WorkOnRulesWithAI
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.7 - 7/10/26 - Ron Lockwood
#    Dropped the transfer.dtd dependency (apertium-preprocess-transfer validates without it): the module no longer locates, requires, or passes a DTD path to the dialog.
#
#   Version 3.16.6 - 7/10/26 - Ron Lockwood
#    The AI runtime data moved to a Lib/AI subfolder: the conventions doc (system prompt) and the derived preview specs are now read from Lib/AI, and the missing-resources error points there.
#
#   Version 3.16.5 - 7/10/26 - Ron Lockwood
#    The information, warning, and consent message boxes now show the FLExTrans window icon. When the provider/model aren't set yet, the module now asks (yes/no) whether to open the
#    Settings tool and, if yes, opens it in the Full view scrolled to the AI Assistant section so the user can set them without hunting for the tool.
#
#   Version 3.16.4 - 7/9/26 - Ron Lockwood
#    The transfer file is now parsed only once at startup (parsed here and the tree handed to both extractExistingDefs and getSampleRulesAndMacros) instead of being read and parsed twice.
#
#   Version 3.16.3 - 7/7/26 - Ron Lockwood
#    The target FLEx project is now guarded (bail out cleanly if it can't be opened) and closed in a finally so it isn't left locked for the rest of the session; the conventions .md is
#    read with a with-block.
#
#   Version 3.16.2 - 7/6/26 - Ron Lockwood
#    PasteDataDlg UI moved to separate Windows/PasteDataWindow.ui file compiled with pyuic; translations split into Windows/translations/PasteDataWindow*.ts files.
#
#   Version 3.16.1 - 7/3/26 - Ron Lockwood
#    The provider and model now must be chosen in the Settings tool before the module will run. New settings: include FLEx project names in the prompt (privacy) and prompt logging
#    for debugging. Prompt grounding now uses the four longest rules and two longest macros from the transfer file.
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. New module that uses a configured AI provider (Gemini by default, Anthropic and OpenAI selectable) to create a new Apertium transfer rule or modify an existing one in
#    the transfer rules file. Gathers the project's real categories/features/affixes from FLEx, grounds the model with the house conventions + example rules, validates every generated
#    rule (well-formedness + apertium-preprocess-transfer), and previews it before the user approves. See WorkOnRulesWithAI-Plan.md.
#

import os

from flextoolslib import FlexToolsModuleClass, FTM_Name, FTM_Version, FTM_ModifiesDB, FTM_Synopsis, FTM_Help, FTM_Description  

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox

import Mixpanel
import Utils
import ReadConfig
import FTPaths
import AIRules

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'WorkOnRulesWithAI'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# Libraries whose strings we load when the module runs. The dialog logic and its pyuic-generated window file each have their own .ts/.qm.
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'RuleAssistant', 'CreateApertiumRules', 'WorkOnRulesWithAIDlg', 'WorkOnRulesWithAIWindow', 'PasteDataWindow']

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("WorkOnRulesWithAI", """This module uses AI to create new Apertium transfer rules or modify existing ones in the transfer rules file. You describe the rule you want; the AI drafts it, it is validated, and you review and approve it before it is written.""")
docs = {FTM_Name       : _translate("WorkOnRulesWithAI", "Work on Rules with AI"),
        FTM_Version    : "3.16.7",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("WorkOnRulesWithAI", "Create or modify Apertium transfer rules with AI assistance."),
        FTM_Help       : "",
        FTM_Description : descr}

def buildProjectDataText(startData, includeProjectNames: bool) -> str:
    '''Turn the FLEx-derived StartData (source and target) into the grounding text the model needs: real categories, features with their values, and per-category features/affixes.
    The FLEx project names are only included when the user opted in via the AIRulesIncludeProjectNames setting - a project name can itself be sensitive information.'''

    lines = []

    for label, db in (('SOURCE', startData.src), ('TARGET', startData.tgt)):

        if includeProjectNames:
            lines.append('{label} project: {name}'.format(label=label, name=db.projectName))
        else:
            lines.append('{label} project:'.format(label=label))
        lines.append('  Categories: ' + ', '.join(db.categoryList))
        lines.append('  Features (name: values):')

        for name, values in db.featureList:
            lines.append('    {name}: {values}'.format(name=name, values=', '.join(values)))

        lines.append('  Category features / affixes (side in brackets):')

        for cat in sorted(db.categoryFeatures):

            feats = db.categoryFeatures[cat]

            if not feats:
                continue

            parts = ['{f}[{sides}]'.format(f=f, sides='|'.join(sorted(sides))) for f, sides in sorted(feats.items())]
            lines.append('    {cat}: {parts}'.format(cat=cat, parts=', '.join(parts)))

        lines.append('')

    return '\n'.join(lines)

def checkConsent(configMap, report, providerDisplay: str) -> bool:
    '''One-time opt-in, mirroring the Mixpanel consent pattern. Returns whether the user consents to sending rule/lexical data to the configured AI provider.'''

    asked = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_CONSENT_ASKED, None, giveError=False)

    if asked != 'y':

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        msgBox.setWindowTitle(_translate('WorkOnRulesWithAI', 'Work on Rules with AI'))
        msgBox.setText(_translate('WorkOnRulesWithAI', "This module sends your rule description, the transfer file's categories, attributes, and the project's grammatical categories, features, and affixes to " \
                       "your configured AI provider ({provider}) to generate transfer rules. Also, if you chose to include example language data, that will be sent as well. Your lexicon entries and texts are " \
                       "not sent (except for what is in the example data). Do you want to allow this?\nThere is a separate setting for sending FLEx project names.").format(provider=providerDisplay))
        msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        allow = (msgBox.exec() == QMessageBox.StandardButton.Yes)

        ReadConfig.writeConfigValue(report, ReadConfig.AI_RULES_CONSENT, 'y' if allow else 'n', createIfMissing=True)
        ReadConfig.writeConfigValue(report, ReadConfig.AI_RULES_CONSENT_ASKED, 'y', createIfMissing=True)
        return allow

    return ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_CONSENT, None, giveError=False) == 'y'

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    thisApp = QApplication.instance()

    if thisApp is None:
        thisApp = QApplication(['FLExTrans'])

    localTranslators = []
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], localTranslators, loadBase=True)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # The provider and model must be chosen in the Settings tool before this module can run; there are no silent defaults, so the user always knows which service their data goes to.
    providerName = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_PROVIDER, report, giveError=False)
    model = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_MODEL, report, giveError=False)
    provider = AIRules.findProvider(providerName)

    if not provider or not model:

        msg = _translate('WorkOnRulesWithAI', 'Before you can use this module, choose the AI Provider and AI Model in the FLExTrans Settings tool, in the AI Assistant section (shown in the Full view). Then come back to this module; it will ask for your API key.\n\nDo you want to open the Settings tool now?')

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        msgBox.setWindowTitle(_translate('WorkOnRulesWithAI', 'Work on Rules with AI'))
        msgBox.setText(msg)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        report.Info(msg)

        # If the user says yes, open the Settings tool for them so they don't have to hunt for it. Force the Full view and scroll to the bottom, where the AI Assistant settings (provider, model) live.
        if msgBox.exec() == QMessageBox.StandardButton.Yes:

            import SettingsGUI # type: ignore
            SettingsGUI.MainFunction(DB, report, forceFullView=True, scrollToBottom=True)

        return

    # Reject a model that belongs to a different provider (possible via a hand-edited config file; the Settings tool itself prevents this pairing). A model no provider claims is
    # allowed - it may simply be newer than this release's model lists.
    owner = AIRules.findModelOwner(model)

    if owner is not None and owner is not provider:

        msg = _translate('WorkOnRulesWithAI', 'The configured AI model ({model}) goes with {owner}, not {provider}. Fix the AI Model setting in the FLExTrans Settings tool.').format(model=model, owner=owner.displayName, provider=provider.displayName)

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Warning)
        msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        msgBox.setWindowTitle(_translate('WorkOnRulesWithAI', 'Work on Rules with AI'))
        msgBox.setText(msg)
        msgBox.exec()

        report.Error(msg)
        return

    # Get consent to send data to the external service.
    if not checkConsent(configMap, report, provider.displayName):

        report.Info(_translate('WorkOnRulesWithAI', 'AI rule assistance was declined. No data was sent.'))
        return

    # Resolve the API key for the selected provider: OS credential vault, then env var (bring-your-own-key).
    apiKey = AIRules.resolveApiKey(provider)

    # If none is stored yet, prompt for one and save it to the vault (never a project file).
    if not apiKey:

        from WorkOnRulesWithAIDlg import promptForApiKey
        apiKey = promptForApiKey(provider)

    if not apiKey:

        report.Info(_translate('WorkOnRulesWithAI', 'No API key provided for {provider}; nothing was done.').format(provider=provider.displayName))
        return

    # Find the transfer rules file.
    transferPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)

    if not transferPath:
        return

    if not os.path.isfile(transferPath):

        report.Error(_translate('WorkOnRulesWithAI', 'Transfer rules file not found: {path}').format(path=Utils.shortenPathForDisplay(transferPath)))
        return

    # The Work-on-Rules-with-AI runtime resources ship in the Lib/AI subfolder beside AIRules.py's Lib folder. Use realpath so this resolves through a per-file symlink (dev deploy) to the real
    # Lib folder. The conventions doc (system prompt) lives in Lib/AI with the derived preview specs.
    libDir = os.path.dirname(os.path.realpath(AIRules.__file__))
    aiDataDir = os.path.join(libDir, 'AI')
    conventionsPath = os.path.join(aiDataDir, 'WorkOnRulesWithAI-Conventions.md')

    if not os.path.isfile(conventionsPath):

        report.Error(_translate('WorkOnRulesWithAI', 'Missing WorkOnRulesWithAI-Conventions.md in the Lib/AI subfolder under {libDir}. Reinstall FLExTrans or copy that file there.').format(libDir=libDir))
        return

    compilerExe = os.path.join(FTPaths.TOOLS_DIR, 'apertium-preprocess-transfer.exe')

    if not os.path.isfile(compilerExe):
        compilerExe = None

    # Turn prompt logging on or off (debugging aid, normally off; see the AIRulesLogPrompts setting). The log holds everything sent to and received from the provider.
    if ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_LOG_PROMPTS, report, giveError=False) == 'y':

        AIRules.PROMPT_LOG_PATH = os.path.join(FTPaths.BUILD_DIR, 'AIRulesPromptLog.txt')
        report.Info(_translate('WorkOnRulesWithAI', 'AI prompt logging is on. Prompts and responses are appended to: {path}').format(path=Utils.shortenPathForDisplay(AIRules.PROMPT_LOG_PATH)))
    else:
        AIRules.PROMPT_LOG_PATH = None

    # Gather the project grounding data from FLEx (source and target). The FLEx project names go into the prompt only if the user opted in (they can be sensitive).
    TargetDB = Utils.openTargetProject(configMap, report)

    # Bail out if the target project couldn't be opened (openTargetProject returns None on failure) - otherwise GetRuleAssistantStartData would crash on None.
    if TargetDB is None:

        report.Error(_translate('WorkOnRulesWithAI', 'Could not open the target FLEx project. Check the target-project setting and try again.'))
        return

    # Close the target project no matter how we leave this function (normal close, or an exception building the prompt / running the dialog) so it isn't left locked for the rest of the
    # FlexTools session. We hold it open across the dialog because GetRuleAssistantStartData's data may reference the open project.
    try:

        from RuleAssistant import GetRuleAssistantStartData
        startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)

        includeProjectNames = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_INCLUDE_PROJECT_NAMES, report, giveError=False) == 'y'
        projectData = buildProjectDataText(startData, includeProjectNames)

        # Parse the transfer file once and feed the same tree to both extractors, rather than each re-reading and re-parsing the whole file (extractExistingDefs walks it for the def
        # summary and the {comment: rule-XML} cache; getSampleRulesAndMacros pulls the longest rules/macros out of the same tree).
        transferRoot = AIRules.parseTransferFile(transferPath)
        defs = AIRules.extractExistingDefs(root=transferRoot)

        with open(conventionsPath, encoding='utf-8') as conventionsFile:
            conventionsText = conventionsFile.read()

        # Ground the model with the project's longest rules and macros - the richest examples of the house style the file has to offer.
        sampleRulesText, sampleMacrosText = AIRules.getSampleRulesAndMacros(root=transferRoot)

        systemInstruction = AIRules.buildSystemInstruction(conventionsText, sampleRulesText, sampleMacrosText)
        engine = AIRules.buildEngine(providerName, apiKey, model)

        # Launch the dialog. FlexTools has no running Qt event loop, so we show the dialog and run the Qt application loop (matching RuleAssistantPy / LiveRuleTesterTool). A bare dlg.exec()
        # returns immediately here and the dialog would flash open and close. app.exec() returns when the dialog (the only top-level Qt window) is closed.
        from WorkOnRulesWithAIDlg import WorkOnRulesWithAIDlg
        dlg = WorkOnRulesWithAIDlg(transferPath, defs['ruleNames'], defs['ruleXml'], systemInstruction, defs['summaryText'], projectData, engine, compilerExe)
        dlg.show()
        thisApp.exec()

    finally:
        TargetDB.CloseProject()

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction, docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
