#
#   ViewSrcTgt
#
#   Ron Lockwood
#   SIL International
#   12/28/17
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 1/3/25 - Ron Lockwood
#    Fixes #241. Error message now includes which modules need to be run.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10 - 12/28/23 - Ron Lockwood
#    Fixes #513. Use text edit control instead of web view to prevent crashing.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7.4 - 1/10/23 - Ron Lockwood
#    Renamed some functions to be camel case.
#
#   Version 3.7.3 - 1/8/23 - Ron Lockwood
#    Fixed bug in last fix. Don't require advance transfer file to be there.
#
#   earlier version history removed on 3/10/25
#
# This module reads the source or target Apertium files whose paths are defined
# in the configuration file and displays them in a user-friendly way. The 
# data stream symbols such as ^$<> are removed and elements of the lexical 
# entries are color coded. Lemmas, grammatical categories, affixes/features/
# classes and punctuation each get their own color. Unknown categories get
# their own color along with the lemma for them. Lemmas with @ in front of them
# get a special color. @ (which only shows up in the target file) indicates
# that a lemma wasn't found in the bilingual dictionary.
# This modules allows the user to increase or decrease the zoom (makes the text
# bigger or smaller), change to RTL layout, switch between target or source 
# files or change the font. 


import os
import re
import tempfile
import sys
import unicodedata
import xml.etree.ElementTree as ET

from flextoolslib import *                                                 

from PyQt5 import QtGui
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

from SrcTgtViewer import Ui_MainWindow
import FTPaths
from LiveRuleTesterTool import TARGET_FILE1, TARGET_FILE2
import ReadConfig
import ExtractSourceText
import RunApertium
from Testbed import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "View Source/Target Apertium Text Tool",
        FTM_Version    : "3.13",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "View an easy-to-read source or target text file.",    
        FTM_Help   : "",
        FTM_Description: 
f"""
This module will display a more readable view of the Apertium source or target 
file. The lexical units are color coded as follows: black-lemma, blue-grammatical 
category, green-affix or feature or class, yellow-non-sentence punctuation, 
dark pink-unknown lemma, pink-unknown category, red-lemma not found. Important! You
must run the modules through {RunApertium.docs[FTM_Name]} before running this module.
""" }
                 
#----------------------------------------------------------------
# The main processing function
class Main(QMainWindow):

    def __init__(self, srcFile, tgtFile, htmlFile, advanced):
        QMainWindow.__init__(self)
        self.src = srcFile
        self.tgt = tgtFile
        self.html = htmlFile
        self.advanced = advanced
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        if advanced:
            
            buildFolder = FTPaths.BUILD_DIR
            self.tgt1 = buildFolder + '\\' + TARGET_FILE1
            self.tgt2 = buildFolder + '\\' + TARGET_FILE2
            self.tgt3 = self.tgt
            
            self.ui.TargetRadio.setEnabled(False)
        else:
            self.ui.targetRadio1.setVisible(False)
            self.ui.targetRadio2.setVisible(False)
            self.ui.targetRadio3.setVisible(False)
              
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.FontButton.clicked.connect(self.FontClicked)
        self.ui.SourceRadio.clicked.connect(self.SourceClicked)
        self.ui.TargetRadio.clicked.connect(self.TargetClicked)
        self.ui.targetRadio1.clicked.connect(self.Target1Clicked)
        self.ui.targetRadio2.clicked.connect(self.Target2Clicked)
        self.ui.targetRadio3.clicked.connect(self.Target3Clicked)
        self.ui.RTL.clicked.connect(self.RTLClicked)
        self.ui.ZoomIncrease.clicked.connect(self.ZoomIncreaseClicked)
        self.ui.ZoomDecrease.clicked.connect(self.ZoomDecreaseClicked)
  
        # default to source file for initial view
        self.viewFile = srcFile
          
        # get the default font
        font = self.ui.largeTextEdit.font()
        self.font_family = str(font.family())
          
        #self.ui.FontNameLabel.setText(font.family())
          
        # load the viewer()
        self.load()
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        
        # buttonHeight = self.ui.OKButton.height()
        # buttonWidth = self.ui.OKButton.width()
        
        # Stretch the view to fit
        self.ui.largeTextEdit.setGeometry(10, 10, self.width() - 20, \
                                    self.height() - 84)
        
        # # Change the y value of widgets depending on the window size
        # y = self.ui.largeTextEdit.height() + 35
        
        # self.ui.OKButton.setGeometry(self.ui.OKButton.x(), y, buttonWidth, buttonHeight)
        # self.ui.FontButton.setGeometry(self.ui.FontButton.x(), y, buttonWidth, buttonHeight)
        # self.ui.ZoomIncrease.setGeometry(self.ui.ZoomIncrease.x(), y, self.ui.ZoomIncrease.width(), buttonHeight)
        # self.ui.ZoomDecrease.setGeometry(self.ui.ZoomDecrease.x(), y, self.ui.ZoomDecrease.width(), buttonHeight)
        # self.ui.FontNameLabel.setGeometry(self.ui.FontNameLabel.x(), y+2, self.ui.FontNameLabel.width(), self.ui.FontNameLabel.height())
        # self.ui.ZoomLabel.setGeometry(self.ui.ZoomLabel.x(), y+2, self.ui.ZoomLabel.width(), self.ui.ZoomLabel.height())
        # self.ui.SourceRadio.setGeometry(self.ui.SourceRadio.x(), y+2, self.ui.SourceRadio.width(), self.ui.SourceRadio.height())
        # self.ui.TargetRadio.setGeometry(self.ui.TargetRadio.x(), y+2, self.ui.TargetRadio.width(), self.ui.TargetRadio.height())
        # self.ui.targetRadio1.setGeometry(self.ui.targetRadio1.x(), y+2-20, self.ui.targetRadio1.width(), self.ui.targetRadio1.height())
        # self.ui.targetRadio2.setGeometry(self.ui.targetRadio2.x(), y+2, self.ui.targetRadio2.width(), self.ui.targetRadio2.height())
        # self.ui.targetRadio3.setGeometry(self.ui.targetRadio3.x(), y+2+20, self.ui.targetRadio3.width(), self.ui.targetRadio3.height())
        # self.ui.RTL.setGeometry(self.ui.RTL.x(), y+2, self.ui.RTL.width(), self.ui.RTL.height())
        # self.ui.linkLabel.setGeometry(self.ui.linkLabel.x(), y+2, self.ui.linkLabel.width(), self.ui.linkLabel.height())

    def ZoomIncreaseClicked(self):
        myFont = self.ui.largeTextEdit.font()
        mySize = myFont.pointSizeF()
        mySize = mySize * 1.25
        myFont.setPointSizeF(mySize)
        self.ui.largeTextEdit.setFont(myFont)

    def ZoomDecreaseClicked(self):
        myFont = self.ui.largeTextEdit.font()
        mySize = myFont.pointSizeF()
        mySize = mySize * .889
        myFont.setPointSizeF(mySize)
        self.ui.largeTextEdit.setFont(myFont)

    def OKClicked(self):
        self.close()

    def FontClicked(self):
        (font, ret) = QFontDialog.getFont(self.ui.largeTextEdit.font(), parent=self)
        if ret:
            self.font_family = str(font.family())
            self.ui.FontNameLabel.setText(font.family())
            self.ui.largeTextEdit.setFont(font)

        self.load()
    def SourceClicked(self):
        self.viewFile = self.src
        self.load()
    def TargetClicked(self):
        self.viewFile = self.tgt
        self.load()
    def Target1Clicked(self):
        self.viewFile = self.tgt1
        self.load()
    def Target2Clicked(self):
        self.viewFile = self.tgt2
        self.load()
    def Target3Clicked(self):
        self.viewFile = self.tgt3
        self.load()
    def RTLClicked(self):
        self.load()

    def getLastFolderAndFile(self, path):

        # Get the base name (file name) from the path
        fileName = os.path.basename(path)
        
        # Get the directory name from the path
        dirName = os.path.dirname(path)
        
        # Get the last folder name from the directory path
        lastFolder = os.path.basename(dirName)
        
        # Join the last folder and the file name
        result = os.path.join(lastFolder, fileName)
        
        return result

    def load(self):
        # Open the input file
        try:
            f = open(self.viewFile, encoding='utf-8')
        except IOError:
            if self.viewFile == self.src:
                QMessageBox.warning(self, 'File Error', f'There was a problem opening the Source Apertium Text file: {self.getLastFolderAndFile(self.viewFile)}. '\
                                    f'Make sure you have run the {ExtractSourceText.docs[FTM_Name]} module first.')
            else:
                QMessageBox.warning(self, 'File Error', f'There was a problem opening a Target Apertium Text file: {self.getLastFolderAndFile(self.viewFile)}. '\
                                    f'Make sure you have run the modules up through {RunApertium.docs[FTM_Name]} first.')
            return
        
        # Remove extra carriage returns apertium is giving us in the target file.
        if self.viewFile != self.src:
            fileContent = f.read()
            f.close()
            
            fileContent = re.sub('\n\n', '\n', fileContent)
            f = open(self.viewFile, 'w', encoding='utf-8')
            f.write(fileContent)
            f.close()
            
            f = open(self.viewFile, encoding='utf-8')

        # Create the root element
        root = ET.Element('html')
        body = ET.SubElement(root, 'body')
        ord_list = ET.SubElement(body, 'ol')
        
        # Check for RTL
        rtl_flag = False
        if self.ui.RTL.isChecked():
            # Set the direction of the entire ordered list to be RTL
            ord_list.attrib['dir'] = 'RTL'
            rtl_flag = True
        
        # Set the font style in the html
        ord_list.attrib['style']='font-family:"'+self.font_family+'"'
        
        # Create a new tree
        tree = ET.ElementTree(root)
        
        show_unk_symbol = False
        
        # Process advanced transfer output differently
        if self.viewFile != self.src and self.advanced and self.viewFile != self.tgt3:
            
            # Process all lines in the input file
            for line in f:
                
                # Normalize to composed form
                line = unicodedata.normalize('NFC', line)
                
                list_item = ET.SubElement(ord_list, 'li')
                
                # Call testbed.py function to format the line
                processAdvancedResults(line, list_item, rtl_flag, dummy=True, punctuationPresent=True)
                
        else: # not advanced
            # Process all lines in the input file
            for line in f:
                
                line = unicodedata.normalize('NFC', line)
                
                list_item = ET.SubElement(ord_list, 'li')
                
                # parse the lexical units. This will give us tokens before, between 
                # and after each lu. E.g. ^hi1.1<n>$, ^there2.3<dem><pl>$ gives
                #                         ['', 'hi1.1<n>', ', ', 'there2.3<dem><pl>', '']
                tokens = re.split('\^|\$', line)
                
                # process pairs of tokens (punctuation and lexical unit)
                for i in range(0,len(tokens)-1,2):
                    # First, put out the punctuation. If the punctuation is null, put
                    # out a space. Except if it's the first punctuation and it null.
                    if len(tokens[i]) > 0:
                        outputLUSpan(list_item, PUNC_COLOR, tokens[i], rtl_flag)
                    elif i > 0:
                        outputLUSpan(list_item, PUNC_COLOR, ' ', rtl_flag)
                    
                    # parse the lexical unit and add the elements needed to the list item element
                    processLexicalUnit(tokens[i+1], list_item, rtl_flag, show_unk_symbol)
                    
                # process last token
                if len(tokens[-1].rstrip()) > 0:
                    outputLUSpan(list_item, PUNC_COLOR, tokens[-1].rstrip(), rtl_flag)
                
        # Write out the html file as utf-8
        tree.write(self.html, encoding='utf-16', xml_declaration=None, default_namespace=None, method='html')
        
        # Get the html as a string
        myStr = ET.tostring(root, encoding='utf-8', method='html')

        # Turn in back to unicode from bytes
        myStr = myStr.decode('utf-8')

        # Set the text box
        self.ui.largeTextEdit.setText(myStr)

        # Set the link label address
        rich_str = '<a href="file:///'+self.html+'">Open in Browser</a>'

        self.ui.linkLabel.setText(rich_str)
   
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # get the path to the source file
    srcFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not srcFile:
        return
    
    # get the path to the target file
    tgtFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    if not tgtFile:
        return
    
    advanced = False
        
    # get the path to the 3rd transfer rule file
    postChunkRuleFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE3, report)
    
    # see if we have advanced transfer going on by seeing if the .t3x file is present
    if postChunkRuleFile and os.path.isfile(postChunkRuleFile):   
        advanced = True
            
    # get temporary file name for html results
    htmlFile = os.path.join(tempfile.gettempdir(), 'FlexTransFileViewer.html')
    
    # Show the window
    app = QApplication(sys.argv)

    # Load translations
    langCode = 'es'
    translator = QTranslator()

    if translator.load(FTPaths.TRANSL_DIR+f"/SrcTgtViewer_{langCode}.qm"):

        QCoreApplication.installTranslator(translator)

    window = Main(srcFile, tgtFile, htmlFile, advanced)
    
    window.show()
    app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
