#
#   ViewSrcTgt
#
#   Ron Lockwood
#   SIL International
#   12/28/17
#
#   Version 1.1 - 4/12/18 - Ron
#    Fixed bug in message box call.
#
#   Version 1.0 - 12/30/17 - Ron
#    Initial version.
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


from FTModuleClass import FlexToolsModuleClass
import Utils
import ReadConfig
import os
import re
import tempfile
import sys
import shutil

#----------------------------------------------------------------
# Configurables:

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "View Source/Target Apertium Text Tool",
        'moduleVersion'    : "1.1",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "View a more readable source or target text file.",
        'moduleDescription'   :
u"""
This module will display a more readable view of the Apertium source or target 
file. The lexical unit (^$) and symbol (<>) notation is removed and parts of 
the lexical unit are color coded as follows: black-lemma, blue-grammatical 
category, green-affix or feature or class, yellow-non-sentence punctuation, 
dark pink-unknown lemma, pink-unknown category, red-lemma not found. 
""" }
                 
#----------------------------------------------------------------
# The main processing function

from PyQt4 import QtGui, QtCore, QtWebKit
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFontDialog, QMessageBox

from SrcTgtViewer import Ui_MainWindow
import xml.etree.ElementTree as ET

class Main(QtGui.QMainWindow):

    def __init__(self, srcFile, tgtFile, htmlFile):
        QtGui.QMainWindow.__init__(self)
        self.src = srcFile
        self.tgt = tgtFile
        self.html = htmlFile
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.FontButton.clicked.connect(self.FontClicked)
        self.ui.SourceRadio.clicked.connect(self.SourceClicked)
        self.ui.TargetRadio.clicked.connect(self.TargetClicked)
        self.ui.RTL.clicked.connect(self.RTLClicked)
        self.ui.ZoomIncrease.clicked.connect(self.ZoomIncreaseClicked)
        self.ui.ZoomDecrease.clicked.connect(self.ZoomDecreaseClicked)

        # default to source file for initial view
        self.viewFile = srcFile
        
        # get the default font
        font = self.ui.webView.font()
        self.font_family = str(font.family())
        
        self.ui.FontNameLabel.setText(font.family())
        
        # load the viewer()
        self.load()
        
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        
        buttonHeight = self.ui.OKButton.height()
        buttonWidth = self.ui.OKButton.width()
        
        # Stretch the table view to fit
        self.ui.webView.setGeometry(10, 10, self.width() - 20, \
                                    self.height() - 90)
        
        # Change the y value of widgets depending on the window size
        y = self.ui.webView.height() + 35
        
        self.ui.OKButton.setGeometry(self.ui.OKButton.x(), y, buttonWidth, buttonHeight)
        self.ui.FontButton.setGeometry(self.ui.FontButton.x(), y, buttonWidth, buttonHeight)
        self.ui.ZoomIncrease.setGeometry(self.ui.ZoomIncrease.x(), y, self.ui.ZoomIncrease.width(), buttonHeight)
        self.ui.ZoomDecrease.setGeometry(self.ui.ZoomDecrease.x(), y, self.ui.ZoomDecrease.width(), buttonHeight)
        self.ui.FontNameLabel.setGeometry(self.ui.FontNameLabel.x(), y+2, self.ui.FontNameLabel.width(), self.ui.FontNameLabel.height())
        self.ui.ZoomLabel.setGeometry(self.ui.ZoomLabel.x(), y+2, self.ui.ZoomLabel.width(), self.ui.ZoomLabel.height())
        self.ui.SourceRadio.setGeometry(self.ui.SourceRadio.x(), y+2, self.ui.SourceRadio.width(), self.ui.SourceRadio.height())
        self.ui.TargetRadio.setGeometry(self.ui.TargetRadio.x(), y+2, self.ui.TargetRadio.width(), self.ui.TargetRadio.height())
        self.ui.RTL.setGeometry(self.ui.RTL.x(), y+2, self.ui.RTL.width(), self.ui.RTL.height())
        self.ui.linkLabel.setGeometry(self.ui.linkLabel.x(), y+2, self.ui.linkLabel.width(), self.ui.linkLabel.height())
    def ZoomIncreaseClicked(self):
        factor = self.ui.webView.zoomFactor()
        factor = factor * 1.25
        self.ui.webView.setZoomFactor(factor)
    def ZoomDecreaseClicked(self):
        factor = self.ui.webView.zoomFactor()
        factor = factor * .8
        self.ui.webView.setZoomFactor(factor)
    def OKClicked(self):
        self.close()
    def FontClicked(self):
        (font, ret) = QFontDialog.getFont()
        if ret:
            self.font_family = str(font.family())
            self.ui.FontNameLabel.setText(font.family())
            #self.ui.webView.setFont(font)
        self.load()
    def SourceClicked(self):
        #self.ui.TargetRadio.setDown()
        self.viewFile = self.src
        self.load()
    def TargetClicked(self):
        #self.ui.SourceRadio.setDown()
        self.viewFile = self.tgt
        self.load()
    def RTLClicked(self):
        self.load()
    def load(self):
        # Open the input file
        try:
            f = open(self.viewFile)
        except IOError:
            QMessageBox.warning(self, 'File Error', 'There was a problem opening the file: '+self.viewFile+'. ')
            return
        
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
        
        # Process all lines in the input file
        for line in f:
            
            line = unicode(line,'utf-8')
            
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
                    Utils.output_span(list_item, Utils.PUNC_COLOR, tokens[i], rtl_flag)
                elif i > 0:
                    Utils.output_span(list_item, Utils.PUNC_COLOR, ' ', rtl_flag)
                
                # parse the lexical unit and add the elements needed to the list item element
                Utils.process_lexical_unit(tokens[i+1], list_item, rtl_flag, show_unk_symbol)
                
        # process last token
        if len(tokens[-1]) > 0:
                Utils.output_span(list_item, Utils.PUNC_COLOR, tokens[-1], rtl_flag)
                
        # Write out the html file as utf-8
        tree.write(self.html, 'UTF-8', None, None, 'html')
        
        # Convert the file to utf-16. Using utf-16 to write the tree above doesn't seem to work
        # The webView widget seems to only display non-ascii characters if it is
        # in utf-16
        utf16_name = self.html+'16'
        original = open(self.html)
        utf16 = open(utf16_name, "w")

        utf16.write(unicode(original.read(), 'UTF-8').encode('UTF-16'))
        original.close()
        utf16.close()
        shutil.copy2(utf16_name, self.html)
        f.close()
        
        # Give the html file location to the web viewer widget
        self.ui.webView.setUrl(QtCore.QUrl(QtCore.QString("file:///"+self.html)))
        
        # Set the link label address
        rich_str = '<a href="file:///'+self.html+'">Open in Browser</a>'

        self.ui.linkLabel.setText(rich_str)
   
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # get the path to the source file
    srcFile = ReadConfig.getConfigVal(configMap, 'AnalyzedTextOutputFile', report)
    if not srcFile:
        return
    
    # get the path to the target file
    tgtFile = ReadConfig.getConfigVal(configMap, 'TargetTranferResultsFile', report)
    if not tgtFile:
        return
    
    # get temporary file name for html results
    htmlFile = os.path.join(tempfile.gettempdir(), 'FlexTransFileViewer.html')
    
    # Show the window
    app = QtGui.QApplication(sys.argv)

    window = Main(srcFile, tgtFile, htmlFile)
    
    window.show()
    app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
