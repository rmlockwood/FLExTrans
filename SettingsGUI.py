#
#   Settings GUI
#   Lærke Roager Christensen
#   28/3/2022
#
#   Version 3.5.2 - 6/21/22 - Ron Lockwood
#    Fixes for #141 and #144. Alphabetize source text list. Correctly load
#    and save source complex types. Also change double loop code for multiple
#    select settings to use x in y instead of the outer loop. This is easier to
#    understand and is maybe more efficient.
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   To make it easier to change the configfile
#

import os
import sys


from FTModuleClass import FlexToolsModuleClass
from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication, QFileDialog

from Settings import Ui_MainWindow
from ComboBox import CheckableComboBox
from flexlibs import FLExProject, AllProjectNames

import Utils
import ReadConfig
from FTPaths import CONFIG_PATH

# ----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name: "Settings Tool",
        FTM_Version: "3.5.2",
        FTM_ModifiesDB: False,
        FTM_Synopsis: "Change FLExTrans settings.",
        FTM_Help: "",
        FTM_Description:
            """
Change FLExTrans settings.            
            """}

# ----------------------------------------------------------------
# The main processing function
class Main(QMainWindow):

    def __init__(self, configMap, report, targetDB, DB):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), ReadConfig.CONFIG_FILE)
        
        self.config = myPath

        #Buttons
        self.ui.apply_button.clicked.connect(self.save)
        self.ui.a_text_button.clicked.connect(self.open_a_text)
        self.ui.ana_file_button.clicked.connect(self.open_ana_file)
        self.ui.syn_file_button.clicked.connect(self.open_syn_file)
        self.ui.transfer_result_file_button.clicked.connect(self.open_tranfer_result)
        self.ui.bi_dictionary_uotfile_button.clicked.connect(self.open_bi_dic_file)
        self.ui.bi_dictionary_replacefile_button.clicked.connect(self.open_bi_dic_replacefile)
        self.ui.target_affix_list_button.clicked.connect(self.open_affix_list)
        self.ui.a_tretran_outfile_button.clicked.connect(self.open_a_treetran)
        self.ui.tretran_insert_words_button.clicked.connect(self.open_insert_words)
        self.ui.transfer_rules_button.clicked.connect(self.open_transfer_rules)
        self.ui.testbed_button.clicked.connect(self.open_testbed)
        self.ui.testbed_result_button.clicked.connect(self.open_testbed_result)
        self.ui.reset_button.clicked.connect(self.reset)
        self.report = report
        self.configMap = configMap
        self.targetDB = targetDB
        self.DB = DB

        self.init_load()

    def open_a_text(self):
        self.browse(self.ui.output_filename, "(*.*)")

    def open_ana_file(self):
        self.browse(self.ui.output_ANA_filename, "(*.*)")

    def open_syn_file(self):
        self.browse(self.ui.output_syn_filename, "(*.*)")

    def open_tranfer_result(self):
        self.browse(self.ui.transfer_result_filename, "(*.*)")

    def open_bi_dic_file(self):
        self.browse(self.ui.bilingual_dictionary_output_filename, "(*.*)")

    def open_bi_dic_replacefile(self):
        self.browse(self.ui.bilingual_dictionary_repalce_file_2, "(*.*)")

    def open_affix_list(self):
        self.browse(self.ui.taget_affix_gloss_list_filename, "(*.*)")

    def open_a_treetran(self):
        self.browse(self.ui.a_treetran_output_filename, "(*.*)")

    def open_insert_words(self):
        self.browse(self.ui.treetran_insert_words_file_2, "(*.*)")

    def open_transfer_rules(self):
        self.browse(self.ui.transfer_rules_filename, "(*.*)")

    def open_testbed(self):
        self.browse(self.ui.testbed_filename, "(*.*)")

    def open_testbed_result(self):
        self.browse(self.ui.testbed_result_filename, "(*.*)")

    def browse(self, name, end):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", end)
        if filename:
            name.setText(os.path.relpath(filename).replace(os.sep, '/'))
            name.setToolTip(os.path.abspath(filename).replace(os.sep, '/'))

    def read(self, key):
        return ReadConfig.getConfigVal(self.configMap, key, self.report)

    def init_load(self):
        #Clear all
        self.ui.chose_sourc_text.clear()
        self.ui.chose_entry_link.clear()
        self.ui.chose_sense_number.clear()
        self.ui.chose_target_project.clear()
        self.ui.chose_source_compex_types.clear()
        self.ui.chose_infelction_first_element.clear()
        self.ui.chose_infelction_second_element.clear()
        self.ui.chose_target_morpheme_types.clear()
        self.ui.chose_source_morpheme_types.clear()
        self.ui.chose_source_discontiguous_compex.clear()
        self.ui.chose_skipped_source_words.clear()
        self.ui.category_abbreviation_one.clear()
        self.ui.category_abbreviation_one.addItem("...")
        self.ui.category_abbreviation_two.clear()
        self.ui.category_abbreviation_two.addItem("...")
        #load all
        #TODO: Find the files in source?
        source_list = []
        for item in self.DB.ObjectsIn(ITextRepository):
            source_list.append(str(item).strip())
        sorted_source_list = sorted(source_list, key=str.casefold)
        
        i = 0
        config_source = self.read('SourceTextName')
        for item_str in sorted_source_list:
            self.ui.chose_sourc_text.addItem(item_str)
            if item_str == config_source:
                self.ui.chose_sourc_text.setCurrentIndex(i)
            i += 1
        i = 0
        for item in self.DB.LexiconGetSenseCustomFields():
            self.ui.chose_entry_link.addItem(str(item[1]))
            self.ui.chose_sense_number.addItem(str(item[1]))
            if item[1] == self.read('SourceCustomFieldForEntryLink'):
                self.ui.chose_entry_link.setCurrentIndex(i)
            if item[1] == self.read('SourceCustomFieldForSenseNum'):
                self.ui.chose_sense_number.setCurrentIndex(i)
            i += 1
        i = 0 #TODO Make this disable the other stuff that uses target??
        for item in AllProjectNames():
            self.ui.chose_target_project.addItem(item)
            if item == self.read('TargetProject'):
                self.ui.chose_target_project.setCurrentIndex(i)
            i += 1
        #TODO: Some kind of safe file thing ??
        self.ui.output_filename.setText(self.read('AnalyzedTextOutputFile').replace(os.sep, '/'))
        self.ui.output_filename.setToolTip(os.path.abspath(self.read('AnalyzedTextOutputFile')).replace(os.sep, '/'))
        self.ui.output_ANA_filename.setText(self.read('TargetOutputANAFile').replace(os.sep, '/'))
        self.ui.output_ANA_filename.setToolTip(os.path.abspath(self.read('TargetOutputANAFile')).replace(os.sep, '/'))
        self.ui.output_syn_filename.setText(self.read('TargetOutputSynthesisFile').replace(os.sep, '/'))
        self.ui.output_syn_filename.setToolTip(os.path.abspath(self.read('TargetOutputSynthesisFile')).replace(os.sep, '/'))
        self.ui.transfer_result_filename.setText(self.read('TargetTranferResultsFile').replace(os.sep, '/'))
        self.ui.transfer_result_filename.setToolTip(os.path.abspath(self.read('TargetTranferResultsFile')).replace(os.sep, '/'))
        #From the Complex Form Types list TODO make multiple select
        array = []
        for item in self.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            array.append(str(item))
        self.ui.chose_source_compex_types.addItems(array)
        if self.read('SourceComplexTypes'):
            for test in self.read('SourceComplexTypes'):
                if test in array:
                    self.ui.chose_source_compex_types.check(test)
        self.ui.bilingual_dictionary_output_filename.setText(self.read('BilingualDictOutputFile').replace(os.sep, '/'))
        self.ui.bilingual_dictionary_output_filename.setToolTip(os.path.abspath(self.read('BilingualDictOutputFile')).replace(os.sep, '/'))
        self.ui.bilingual_dictionary_repalce_file_2.setText(self.read('BilingualDictReplacementFile').replace(os.sep, '/'))
        self.ui.bilingual_dictionary_repalce_file_2.setToolTip(os.path.abspath(self.read('BilingualDictReplacementFile')).replace(os.sep, '/'))
        self.ui.taget_affix_gloss_list_filename.setText(self.read('TargetAffixGlossListFile').replace(os.sep, '/'))
        self.ui.taget_affix_gloss_list_filename.setToolTip(os.path.abspath(self.read('TargetAffixGlossListFile')).replace(os.sep, '/'))
        #From the Complex Form Types list
        #TODO: how to make multiple select??
        array = []
        for item in self.targetDB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            array.append(str(item))
        self.ui.chose_infelction_first_element.addItems(array)
        self.ui.chose_infelction_second_element.addItems(array)
        if self.read('TargetComplexFormsWithInflectionOn1stElement'):
            for test in self.read('TargetComplexFormsWithInflectionOn1stElement'):
                if test in array:
                    self.ui.chose_infelction_first_element.check(test)
        if self.read('TargetComplexFormsWithInflectionOn2ndElement'):
            for test in self.read('TargetComplexFormsWithInflectionOn2ndElement'):
                if test in array:
                    self.ui.chose_infelction_second_element.check(test)
        #From the Morpheme Types list
        #TODO: select multiple
        array = []
        for item in self.targetDB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
            array.append(str(item).strip("-=~*"))
        self.ui.chose_target_morpheme_types.addItems(array)
        for test in self.read('TargetMorphNamesCountedAsRoots'):
            if test in array:
                self.ui.chose_target_morpheme_types.check(test)
        array = []
        for item in self.DB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
            array.append(str(item).strip("-=~*"))
        self.ui.chose_source_morpheme_types.addItems(array)
        for test in self.read('SourceMorphNamesCountedAsRoots'):
            if test in array:
                self.ui.chose_source_morpheme_types.check(test)
        #From the Complex Form Types list.
        #TODO: Mulitiple select
        array = []
        for item in self.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            array.append(str(item))
        self.ui.chose_source_discontiguous_compex.addItems(array)
        if self.read('SourceDiscontigousComplexTypes'):
            for test in self.read('SourceDiscontigousComplexTypes'):
                if test in array:
                    self.ui.chose_source_discontiguous_compex.check(test)
        #From the category abbreviation list.
        #TODO: make multiple select
        array = []
        for pos in self.DB.lp.AllPartsOfSpeech:
            posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            array.append(posAbbrStr)
        self.ui.chose_skipped_source_words.addItems(array)
        if self.read('SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'):
            for test in self.read('SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'):
                if test in array:
                    self.ui.chose_skipped_source_words.check(test)
        if self.read('AnalyzedTextTreeTranOutputFile'):
            self.ui.a_treetran_output_filename.setText(self.read('AnalyzedTextTreeTranOutputFile').replace(os.sep, '/'))
            self.ui.a_treetran_output_filename.setToolTip(os.path.abspath(self.read('AnalyzedTextTreeTranOutputFile')).replace(os.sep, '/'))
        if self.read('TreeTranInsertWordsFile'):
            self.ui.treetran_insert_words_file_2.setText(self.read('TreeTranInsertWordsFile').replace(os.sep, '/'))
            self.ui.treetran_insert_words_file_2.setToolTip(os.path.abspath(self.read('TreeTranInsertWordsFile')).replace(os.sep, '/'))
        self.ui.transfer_rules_filename.setText(self.read('TransferRulesFile').replace(os.sep, '/'))
        self.ui.transfer_rules_filename.setToolTip(os.path.abspath(self.read('TransferRulesFile')).replace(os.sep, '/'))
        self.ui.testbed_filename.setText(self.read('TestbedFile').replace(os.sep, '/'))
        self.ui.testbed_filename.setToolTip(os.path.abspath(self.read('TestbedFile')).replace(os.sep, '/'))
        self.ui.testbed_result_filename.setText(self.read('TestbedResultsFile').replace(os.sep, '/'))
        self.ui.testbed_result_filename.setToolTip(os.path.abspath(self.read('TestbedResultsFile')).replace(os.sep, '/'))
        #From the category abbreviation list.
        #TODO: be able to select more pairs??
        i = 1
        for pos in self.DB.lp.AllPartsOfSpeech:
            posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            self.ui.category_abbreviation_one.addItem(posAbbrStr)
            if self.read('CategoryAbbrevSubstitutionList'):
                if posAbbrStr == self.read('CategoryAbbrevSubstitutionList')[0]:
                    self.ui.category_abbreviation_one.setCurrentIndex(i)
            i += 1
        i = 1
        for pos in self.targetDB.lp.AllPartsOfSpeech:
            posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            self.ui.category_abbreviation_two.addItem(posAbbrStr)
            if self.read('CategoryAbbrevSubstitutionList'):
                if posAbbrStr == self.read('CategoryAbbrevSubstitutionList')[1]:
                    self.ui.category_abbreviation_two.setCurrentIndex(i)
            i += 1
        if self.read('CleanUpUnknownTargetWords') == 'y':
            self.ui.cleanup_yes.setChecked(True)
        self.ui.punctuation.setText(self.read('SentencePunctuation'))
        self.ui.punctuation.setAlignment(Qt.AlignLeft) #TODO make this work

    def save(self):
        n='n'
        if self.ui.cleanup_yes.isChecked():
            n='y'
        f = open(self.config, "w", encoding='utf-8')
        f.write("SourceTextName="+self.ui.chose_sourc_text.currentText()+"\n"+
                "AnalyzedTextOutputFile="+self.ui.output_filename.text()+"\n"+
                "TargetOutputANAFile="+self.ui.output_ANA_filename.text()+"\n"+
                "TargetOutputSynthesisFile="+self.ui.output_syn_filename.text()+"\n"+
                "TargetTranferResultsFile="+self.ui.transfer_result_filename.text()+"\n"+
                "SourceComplexTypes="+self.optional_mul(self.ui.chose_source_compex_types.currentData())+"\n"+
                "SourceCustomFieldForEntryLink="+self.ui.chose_entry_link.currentText()+"\n"+
                "SourceCustomFieldForSenseNum="+self.ui.chose_sense_number.currentText()+"\n"+
                "TargetAffixGlossListFile="+self.ui.taget_affix_gloss_list_filename.text()+"\n"+
                "BilingualDictOutputFile="+self.ui.bilingual_dictionary_output_filename.text()+"\n"+
                "BilingualDictReplacementFile="+self.ui.bilingual_dictionary_repalce_file_2.text()+"\n"+
                "TargetProject="+self.ui.chose_target_project.currentText()+"\n"+
                "TargetComplexFormsWithInflectionOn1stElement="+self.optional_mul(self.ui.chose_infelction_first_element.currentData())+"\n"+
                "TargetComplexFormsWithInflectionOn2ndElement="+self.optional_mul(self.ui.chose_infelction_second_element.currentData())+"\n"+
                "TargetMorphNamesCountedAsRoots="+self.optional_mul(self.ui.chose_target_morpheme_types.currentData())+"\n"+ #stem,bound stem,root,bound root,phrase
                "SourceMorphNamesCountedAsRoots="+self.optional_mul(self.ui.chose_source_morpheme_types.currentData())+"\n"+#stem,bound stem,root,bound root,phrase
                "SourceDiscontigousComplexTypes="+self.optional_mul(self.ui.chose_source_discontiguous_compex.currentData())+"\n"+
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories="+self.optional_mul(self.ui.chose_skipped_source_words.currentData())+"\n"+
                "AnalyzedTextTreeTranOutputFile="+self.ui.a_treetran_output_filename.text()+"\n"+
                "TreeTranInsertWordsFile="+self.ui.treetran_insert_words_file_2.text()+"\n"+
                "TransferRulesFile="+self.ui.transfer_rules_filename.text()+"\n"+
                "TestbedFile="+self.ui.testbed_filename.text()+"\n"+
                "TestbedResultsFile="+self.ui.testbed_result_filename.text()+"\n"+
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n"+
                "CategoryAbbrevSubstitutionList="+self.optional(self.ui.category_abbreviation_one)+","+self.optional(self.ui.category_abbreviation_two)+"\n"+
                "CleanUpUnknownTargetWords="+n+"\n"+
                "SentencePunctuation="+self.ui.punctuation.text()+"\n")
        f.close()
        msgBox = QMessageBox()
        msgBox.setText("Your file has been successfully saved.")
        msgBox.setWindowTitle("Successful save")
        msgBox.exec()

    def optional(self, string):
        write = ''
        if string.currentText() != '...':
            write = string.currentText()
        return write

    def optional_mul(self, array):
        write = ''
        if array:
            for text in array:
                write += text + ","
        return write

    def reset(self):
        f = open(self.config, "w", encoding='utf-8') # TODO change here when new standard
        f.write("SourceTextName=Text1\n" +
                "AnalyzedTextOutputFile=Output\\source_text.aper\n" +
                "TargetOutputANAFile=Build\\myText.ana\n" +
                "TargetOutputSynthesisFile=Output\\myText.syn\n" +
                "TargetTranferResultsFile=Output\\target_text.aper\n" +
                "SourceComplexTypes=\n" +
                "SourceCustomFieldForEntryLink=Target Equivalent\n" +
                "SourceCustomFieldForSenseNum=Target Sense Number\n" +
                "BilingualDictOutputFile=Output\\bilingual.dix\n" +
                "BilingualDictReplacementFile=replace.dix\n" +
                "TargetProject=Swedish-FLExTrans-Sample\n" +
                "TargetAffixGlossListFile=Build\\target_affix_glosses.txt\n" +
                "TargetComplexFormsWithInflectionOn1stElement=\n" +
                "TargetComplexFormsWithInflectionOn2ndElement=\n" +
                "TargetMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase,\n" +
                "SourceMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase,\n" +
                "SourceDiscontigousComplexTypes=\n" +
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories=\n" +
                "AnalyzedTextTreeTranOutputFile=\n" +
                "TreeTranInsertWordsFile=\n" +
                "TransferRulesFile=transfer_rules.t1x\n" +
                "TestbedFile=testbed.xml\n" +
                "TestbedResultsFile=Output\\testbed_results.xml\n" +
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n" +
                "CategoryAbbrevSubstitutionList=\n" +
                "CleanUpUnknownTargetWords=n\n" +
                "SentencePunctuation=.?;:!\"\'\n")
        f.close()
        self.init_load()



def MainFunction(DB, report, modify=True):
    # Read the configuration file which we assume is in the current directory.

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        report.error('Error reading configuration file.')
        return

    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenProject(targetProj, False)
    except:
        raise

    # Show the window
    app = QApplication(sys.argv)

    window = Main(configMap, report, TargetDB, DB,) #sourceDB

    window.show()

    app.exec_()
    msgBox = QMessageBox()
    if QMessageBox().question(msgBox, 'Save?', "Do you want to save before you leave?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
        window.save()


# ----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs=docs)

# ----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
