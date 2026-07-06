#
#   WorkOnRulesWithAI
#
#   Ron Lockwood
#   SIL International
#   7/2/26
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
        FTM_Version    : "3.16.2",
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

        msg = _translate('WorkOnRulesWithAI', 'Before you can use this module, choose the AI Provider and AI Model in the FLExTrans Settings tool, in the AI Assistant section (shown in the Full view). Then come back to this module; it will ask for your API key.')
        QMessageBox.information(None, _translate('WorkOnRulesWithAI', 'Work on Rules with AI'), msg)
        report.Info(msg)
        return

    # Reject a model that belongs to a different provider (possible via a hand-edited config file; the Settings tool itself prevents this pairing). A model no provider claims is
    # allowed - it may simply be newer than this release's model lists.
    owner = AIRules.findModelOwner(model)

    if owner is not None and owner is not provider:

        msg = _translate('WorkOnRulesWithAI', 'The configured AI model ({model}) goes with {owner}, not {provider}. Fix the AI Model setting in the FLExTrans Settings tool.').format(model=model, owner=owner.displayName, provider=provider.displayName)
        QMessageBox.warning(None, _translate('WorkOnRulesWithAI', 'Work on Rules with AI'), msg)
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

    # The bundled resources ship in the same Lib folder as AIRules.py. Use realpath so this resolves through a per-file symlink (dev deploy) to the real Lib folder.
    libDir = os.path.dirname(os.path.realpath(AIRules.__file__))
    conventionsPath = os.path.join(libDir, 'WorkOnRulesWithAI-Conventions.md')
    dtdPath = os.path.join(libDir, 'transfer.dtd')

    if not os.path.isfile(conventionsPath) or not os.path.isfile(dtdPath):

        report.Error(_translate('WorkOnRulesWithAI', 'Missing WorkOnRulesWithAI-Conventions.md and/or transfer.dtd in {libDir}. Reinstall FLExTrans or copy those files there.').format(libDir=libDir))
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

    from RuleAssistant import GetRuleAssistantStartData
    startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)

    includeProjectNames = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_INCLUDE_PROJECT_NAMES, report, giveError=False) == 'y'
    projectData = buildProjectDataText(startData, includeProjectNames)

    defs = AIRules.extractExistingDefs(transferPath)

    conventionsText = open(conventionsPath, encoding='utf-8').read()

    # Ground the model with the project's longest rules and macros - the richest examples of the house style the file has to offer.
    sampleRulesText, sampleMacrosText = AIRules.getSampleRulesAndMacros(transferPath)

    systemInstruction = AIRules.buildSystemInstruction(conventionsText, sampleRulesText, sampleMacrosText)
    engine = AIRules.buildEngine(providerName, apiKey, model)

    # Launch the dialog. FlexTools has no running Qt event loop, so we show the dialog and run the Qt application loop (matching RuleAssistantPy / LiveRuleTesterTool). A bare dlg.exec()
    # returns immediately here and the dialog would flash open and close. app.exec() returns when the dialog (the only top-level Qt window) is closed.
    from WorkOnRulesWithAIDlg import WorkOnRulesWithAIDlg
    dlg = WorkOnRulesWithAIDlg(transferPath, defs['ruleNames'], systemInstruction, defs['summaryText'], projectData, engine, dtdPath, compilerExe)
    dlg.show()
    thisApp.exec()

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction, docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
