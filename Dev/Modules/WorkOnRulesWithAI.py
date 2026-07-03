#
#   WorkOnRulesWithAI
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. New module that uses a configured AI provider (Anthropic by default, Gemini selectable) to create a new Apertium transfer rule or modify an existing one in the transfer
#    rules file. Gathers the project's real categories/features/affixes from FLEx, grounds the model with the house conventions + DTD + example rules, validates every generated rule
#    (DTD + apertium-preprocess-transfer), and previews it before the user approves. See WorkOnRulesWithAI-Plan.md.
#

import os
import xml.etree.ElementTree as ET

from flextoolslib import *                                       # type: ignore

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

# Libraries whose strings we load when the module runs.
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'RuleAssistant', 'CreateApertiumRules']

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("WorkOnRulesWithAI", """This module uses AI to create new Apertium transfer rules or modify existing ones in the transfer rules file. You describe the rule you want; the AI drafts it, it is validated, and you review and approve it before it is written.""")
docs = {FTM_Name       : _translate("WorkOnRulesWithAI", "Work on Rules with AI"),
        FTM_Version    : "3.16",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("WorkOnRulesWithAI", "Create or modify Apertium transfer rules with AI assistance."),
        FTM_Help       : "",
        FTM_Description : descr}

def buildProjectDataText(startData) -> str:
    '''Turn the FLEx-derived StartData (source and target) into the grounding text the model needs: real categories, features with their values, and per-category features/affixes.'''

    lines = []

    for label, db in (('SOURCE', startData.src), ('TARGET', startData.tgt)):

        lines.append('{label} project: {name}'.format(label=label, name=db.projectName))
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

def getSampleRulesText(transferPath: str, howMany: int = 2) -> str:
    '''Pull the first few existing rules from the project's transfer file to show the model the house style.'''

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.parse(transferPath, parser=parser).getroot()

    rules = root.findall('.//rule')[:howMany]
    return '\n\n'.join(ET.tostring(r, encoding='unicode') for r in rules)

def checkConsent(configMap, report, providerDisplay: str) -> bool:
    '''One-time opt-in, mirroring the Mixpanel consent pattern. Returns whether the user consents to sending rule/lexical data to the configured AI provider.'''

    asked = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_CONSENT_ASKED, None, giveError=False)

    if asked != 'y':

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle(_translate('WorkOnRulesWithAI', 'Work on Rules with AI'))
        msgBox.setText(_translate('WorkOnRulesWithAI', "This module sends your rule description, the transfer file's categories, and the project's grammatical categories, features, and affixes to " \
                       "your configured AI provider ({provider}) to generate transfer rules. Your lexicon glosses and texts are not sent. Do you want to allow this?").format(provider=providerDisplay))
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

    # Determine the AI provider (Anthropic by default; set AIRulesProvider to switch).
    providerName = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_PROVIDER, report, giveError=False) or AIRules.DEFAULT_PROVIDER
    provider = AIRules.getProvider(providerName)

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

    # Gather the project grounding data from FLEx (source and target).
    TargetDB = Utils.openTargetProject(configMap, report)

    from RuleAssistant import GetRuleAssistantStartData
    startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)
    projectData = buildProjectDataText(startData)

    defs = AIRules.extractExistingDefs(transferPath)

    conventionsText = open(conventionsPath, encoding='utf-8').read()
    sampleRulesText = getSampleRulesText(transferPath)

    model = ReadConfig.getConfigVal(configMap, ReadConfig.AI_RULES_MODEL, report, giveError=False) or None
    systemInstruction = AIRules.buildSystemInstruction(conventionsText, sampleRulesText)
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
