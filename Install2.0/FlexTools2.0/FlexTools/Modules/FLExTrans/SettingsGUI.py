#
#   Settings GUI
#   Lærke Roager Christensen
#   28/3/2022
#
#   To make it easier to change the configfile
#

import os
import re
import tempfile
import sys
import shutil
import unicodedata

from FTModuleClass import FlexToolsModuleClass
from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from SIL.LCModel.Core.Text import TsStringUtils
from UIProjectChooser import ProjectChooser

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication, QFileDialog

from Settings import Ui_MainWindow
from flexlibs.FLExProject import FLExProject, GetProjectNames
import xml.etree.ElementTree as ET

import Utils
import ReadConfig

# ----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name: "Settings Tool",
        FTM_Version: "1.0",
        FTM_ModifiesDB: True,
        FTM_Synopsis: "Configuration settings",
        FTM_Help: "",
        FTM_Description:
            """
            
            """}


# ----------------------------------------------------------------
# The main processing function
class Main(QMainWindow):

    def __init__(self, configMap, report, targetDB):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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

        self.report = report
        self.configMap = configMap

        self.init_load(targetDB)

    def open_a_text(self):
        self.browse(self.ui.output_filename, "(*.aper)")

    def open_ana_file(self):
        self.browse(self.ui.output_ANA_filename, "(*.ana)")

    def open_syn_file(self):
        self.browse(self.ui.output_syn_filename, "(*.syn)")

    def open_tranfer_result(self):
        self.browse(self.ui.transfer_result_filename, "(*.aper)")

    def open_bi_dic_file(self):
        self.browse(self.ui.bilingual_dictionary_output_filename, "(*.dix)")

    def open_bi_dic_replacefile(self):
        self.browse(self.ui.bilingual_dictionary_repalce_file_2, "(*.dix)")

    def open_affix_list(self):
        self.browse(self.ui.taget_affix_gloss_list_filename, "(*.txt)")

    def open_a_treetran(self):
        self.browse(self.ui.a_treetran_output_filename, "(*.*)")

    def open_insert_words(self):
        self.browse(self.ui.treetran_insert_words_file_2, "(*.*)")

    def open_transfer_rules(self):
        self.browse(self.ui.transfer_rules_filename, "(*.t1x)")

    def open_testbed(self):
        self.browse(self.ui.testbed_filename, "(*.xml)")

    def open_testbed_result(self):
        self.browse(self.ui.testbed_result_filename, "(*.xml)")

    def browse(self, name, end):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", end)
        if filename:
            name.setText(os.path.relpath(filename))

    def read(self, key):
        return ReadConfig.getConfigVal(self.configMap, key, self.report)

    def init_load(self, targetDB):
        #self.ui.chose_sourc_text.addItem(self.read('SourceTextName'))
        for item in targetDB.ObjectsIn(ITextRepository):
            self.ui.chose_sourc_text.addItem(str(item))
        #Find the list of sense-level custom fields (location: sense, type: single-line text)
        #TODO: Probably use somthing in the FLExProject.py ??
        self.ui.chose_entry_link.addItem(self.read('SourceCustomFieldForEntryLink'))
        self.ui.chose_sense_number.addItem(self.read('SourceCustomFieldForEntryLink'))
        #self.ui.chose_target_project.addItem(self.read('TargetProject'))
        i = 0
        for item in GetProjectNames():
            self.ui.chose_target_project.addItem(item)
            if item == self.read('TargetProject'):
                self.ui.chose_target_project.setCurrentIndex(i)
            i += 1
        self.ui.output_filename.setText(self.read('AnalyzedTextOutputFile'))
        self.ui.output_ANA_filename.setText(self.read('TargetOutputANAFile'))
        self.ui.output_syn_filename.setText(self.read('TargetOutputSynthesisFile'))
        self.ui.transfer_result_filename.setText(self.read('TargetTranferResultsFile'))
        #From the Complex Form Types list
        #TODO: find said list, under list in Feildwork, how to get those lists??
        if self.read('SourceComplexTypes'):
            self.ui.chose_source_compex_types.addItem(self.read('SourceComplexTypes'))
        self.ui.bilingual_dictionary_output_filename.setText(self.read('BilingualDictOutputFile'))
        self.ui.bilingual_dictionary_repalce_file_2.setText(self.read('BilingualDictReplacementFile'))
        #Target Prefix list??
        self.ui.taget_affix_gloss_list_filename.setText(self.read('TargetAffixGlossListFile'))
        #From the Complex Form Types list
        #TODO: find the list, see previouse todo. how to make multiple select??
        if self.read('TargetComplexFormsWithInflectionOn1stElement'):
            self.ui.chose_infelction_first_element.addItem(self.read('TargetComplexFormsWithInflectionOn1stElement'))
        if self.read('TargetComplexFormsWithInflectionOn2ndElement'):
            self.ui.chose_infelction_second_element.addItem(self.read('TargetComplexFormsWithInflectionOn2ndElement'))
        #From the Morpheme Types list
        #TODO: find the list, and select multiple
        for item in self.read('TargetMorphNamesCountedAsRoots'):
            self.ui.chose_target_morpheme_types.addItem(item)
        for item in self.read('SourceMorphNamesCountedAsRoots'):
            self.ui.chose_source_morpheme_types.addItem(item)
        #From the Complex Form Types list.
        if self.read('SourceDiscontigousComplexTypes'):
            self.ui.chose_source_discontiguous_compex.addItem(self.read('SourceDiscontigousComplexTypes'))
        #From the category abbreviation list.
        #TODO: Find the list, Look at get_categories() in Utils.py ??
        if self.read('SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'):
            self.ui.chose_skipped_source_words.addItem(
                self.read('SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'))
        if self.read('AnalyzedTextTreeTranOutputFile'):
            self.ui.a_treetran_output_filename.setText(self.read('AnalyzedTextTreeTranOutputFile'))
        if self.read('TreeTranInsertWordsFile'):
            self.ui.treetran_insert_words_file_2.setText(self.read('TreeTranInsertWordsFile'))
        self.ui.transfer_rules_filename.setText(self.read('TransferRulesFile'))
        self.ui.testbed_filename.setText(self.read('TestbedFile'))
        self.ui.testbed_result_filename.setText(self.read('TestbedResultsFile'))
        # From the category abbreviation list.
        # TODO: Find the list, Look at get_categories() in Utils.py ??, be able to select more pairs??
        if self.read('CategoryAbbrevSubstitutionList'):
            self.ui.category_abbreviation_one.addItem(self.read('CategoryAbbrevSubstitutionList')[0])
            self.ui.category_abbreviation_one.addItem(self.read('CategoryAbbrevSubstitutionList')[1])
        if self.read('CleanUpUnknownTargetWords') == 'y':
            self.ui.cleanup_yes.setChecked(True)
        self.ui.punctuation.setText(self.read('SentencePunctuation'))

    def save(self):
        n='n'
        if self.ui.cleanup_yes.isChecked():
            n='y'
        f = open("FlexTrans.config", "w")
        f.write("SourceTextName="+self.ui.chose_sourc_text.currentText()+"\n"+
                "AnalyzedTextOutputFile="+self.ui.output_filename.text()+"\n"+
                "TargetOutputANAFile="+self.ui.output_ANA_filename.text()+"\n"+
                "TargetOutputSynthesisFile="+self.ui.output_syn_filename.text()+"\n"+
                "TargetTranferResultsFile="+self.ui.transfer_result_filename.text()+"\n"+
                "SourceComplexTypes="+self.optional(self.ui.chose_source_compex_types)+"\n"+
                "SourceCustomFieldForEntryLink="+self.ui.chose_entry_link.currentText()+"\n"+
                "SourceCustomFieldForSenseNum="+self.ui.chose_sense_number.currentText()+"\n"+
                "TargetAffixGlossListFile="+self.ui.taget_affix_gloss_list_filename.text()+"\n"+
                "BilingualDictOutputFile="+self.ui.bilingual_dictionary_output_filename.text()+"\n"+
                "BilingualDictReplacementFile="+self.ui.bilingual_dictionary_repalce_file_2.text()+"\n"+
                "TargetProject="+self.ui.chose_target_project.currentText()+"\n"+
                "TargetPrefixGlossListFile=Output\\target_pfx_glosses.txt\n"+
                "TargetComplexFormsWithInflectionOn1stElement="+self.optional(self.ui.chose_infelction_first_element)+"\n"+
                "TargetComplexFormsWithInflectionOn2ndElement="+self.optional(self.ui.chose_infelction_second_element)+"\n"+
                "TargetMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase\n"+
                "SourceMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase\n"+
                "SourceDiscontigousComplexTypes="+self.optional(self.ui.chose_source_discontiguous_compex)+"\n"+
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories="+self.optional(self.ui.chose_skipped_source_words)+"\n"+
                "AnalyzedTextTreeTranOutputFile="+self.ui.a_treetran_output_filename.text()+"\n"+
                "TreeTranInsertWordsFile="+self.ui.treetran_insert_words_file_2.text()+"\n"+
                "TransferRulesFile="+self.ui.transfer_rules_filename.text()+"\n"+
                "TestbedFile="+self.ui.testbed_filename.text()+"\n"+
                "TestbedResultsFile="+self.ui.testbed_result_filename.text()+"\n"+
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n"+
                "CategoryAbbrevSubstitutionList=\n"+
                "CleanUpUnknownTargetWords="+n+"\n"+
                "SentencePunctuation="+self.ui.punctuation.text()+"\n")
        f.close()

    def optional(self, string):
        write = ''
        if string.currentText() != '...':
            write = string.currentText()
        return write

    def reset(self):
        f = open("FlexTrans.config", "w")
        f.write("SourceTextName=Text1\n" +
                "AnalyzedTextOutputFile=Output\\source_text.aper\n" +
                "TargetOutputANAFile=Output\\myText.ana\n" +
                "TargetOutputSynthesisFile=Output\\myText.syn\n" +
                "TargetTranferResultsFile=Output\\target_text.aper\n" +
                "SourceComplexTypes=\n" +
                "SourceCustomFieldForEntryLink=Target Equivalent\n" +
                "SourceCustomFieldForSenseNum=Target Sense Number\n" +
                "TargetAffixGlossListFile=Output\\target_affix_glosses.txt\n" +
                "BilingualDictOutputFile=Output\\bilingual.dix\n" +
                "BilingualDictReplacementFile=..\\replace.dix\n" +
                "TargetProject=Swedish-FLExTrans-Sample\n" +
                "TargetPrefixGlossListFile=Output\\target_pfx_glosses.txt\n" +
                "TargetComplexFormsWithInflectionOn1stElement=\n" +
                "TargetComplexFormsWithInflectionOn2ndElement=\n" +
                "TargetMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase\n" +
                "SourceMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase\n" +
                "SourceDiscontigousComplexTypes=\n" +
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories=\n" +
                "AnalyzedTextTreeTranOutputFile=\n" +
                "TreeTranInsertWordsFile=\n" +
                "TransferRulesFile=..\\transfer_rules.t1x\n" +
                "TestbedFile=..\\testbed.xml\n" +
                "TestbedResultsFile=Output\\testbed_results.xml\n" +
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n" +
                "CategoryAbbrevSubstitutionList=\n" +
                "CleanUpUnknownTargetWords=n\n" +
                "SentencePunctuation=.?;:!\"\'\n")
        f.close()



def MainFunction(DB, report, modify=True):
    # Read the configuration file which we assume is in the current directory.
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenProject(targetProj, True)
    except:
        raise

    # Show the window
    app = QApplication(sys.argv)

    window = Main(configMap, report, TargetDB)

    window.show()
    app.exec_()


# ----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs=docs)

# ----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
