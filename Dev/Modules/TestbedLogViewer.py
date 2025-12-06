#
#   TestbedLogViewer
#
#   Ron Lockwood
#   SIL International
#   6/22/18
#
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 7/23/25 - Ron Lockwood
#    Fixes #1016. Repeat the expected result in the actual result column.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/15/24 - Ron Lockwood
#    Fixes #200. Don't cache the result object. For some reason it causes gaps in the tree view for duplicate results.
#
#   Version 3.10.1 - 2/15/24 - Ron Lockwood
#    Fixes #563. Give a path to the check mark and other icons so they can be found in the Tools folder.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7.3 - 1/10/23 - Ron Lockwood
#    Renamed some functions to be camel case.
#
#   earlier version history removed on 3/10/25
#
#   Show the testbed log which shows the results of tests run for a certain
#   date/time. See design doc at: https://app.moqups.com/pNl8pLlTB6/edit/page/a8dd9b3cb
#

import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from subprocess import call

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialogButtonBox, QApplication
from PyQt5.QtCore import QCoreApplication, QDateTime

from SIL.LCModel import *   # type: ignore
from flextoolslib import *                                                 

import Mixpanel
import FTPaths
import Utils
import ReadConfig
from Testbed import *
from TestbedLog import Ui_TestbedLogWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TestbedLogViewer'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'TestbedLog', 'Testbed', 'TestbedValidator'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("TestbedLogViewer", "Testbed Log Viewer"),
        FTM_Version    : "3.14.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("TestbedLogViewer", "View testbed run results."),
        FTM_Help       : "", 
        FTM_Description: _translate("TestbedLogViewer", 
"""View testbed run results. The number of results to display is set by default to 25. Change MAX_RESULTS_TO_DISPLAY to a different value as needed.""")}
                 
#app.quit()
#del app

GREEN_CHECK =     'Light_green_check.png'        
RED_X =           'Red_x.png'
YELLOW_TRIANGLE = 'Yellow_triangle.png'
MAX_RESULTS_TO_DISPLAY = 25

color_re = re.compile('color:#......')
colorNumPunc = 'color:#'+PUNC_COLOR

class Stats():
    def __init__(self, dateTimeStart, dateTimeEnd, totalTests, numFailed, numInvalid):
        self.dateTimeStart = dateTimeStart
        self.dateTimeEnd = dateTimeEnd
        self.totalTests = totalTests
        self.numFailed = numFailed
        self.numInvalid = numInvalid
    
    def getTestElapsedSeconds(self):
        try:
            # Turn the strings into datetime objects
            startDT = QDateTime.fromString(self.dateTimeStart, XML_DATETIME_FORMAT_QT)
            endDT = QDateTime.fromString(self.dateTimeEnd, XML_DATETIME_FORMAT_QT)
        except:
            return 0
        
        return startDT.secsTo(endDT)
        
    def getTestResultSummary(self):
        if self.numFailed > 0:
            myColor = NOT_FOUND_COLOR
        elif self.numInvalid > 0:
            myColor = PUNC_COLOR
        else:
            myColor = SUCCESS_COLOR

        myStr = _translate("TestbedLogViewer", '{total} Tests, {failed} Failed, {invalid} Invalid').format(total=self.totalTests, failed=self.numFailed, invalid=self.numInvalid)

        p = ET.Element('p')
        outputLUSpan(p, myColor, myStr, False) #rtl
        return ET.tostring(p, encoding='unicode')

    
# An item that can be used to populate a tree view, knowing it's place in the model
class BaseTreeItem(object):
    
    def __init__(self, inParentItem, rtl):
        self.parent = inParentItem
        self.rtl = rtl
        self.children = []
        self.index = None
        self.widget = [None, None, None]
    
    def isRTL(self):
        return self.rtl
    
    def AddChild(self, inChild):
        self.children.append(inChild)
    
    def GetChildCount(self):
        return len(self.children)
        
    def GetChild(self, row):
        return self.children[row]
    
    def GetParent(self):
        return self.parent
    
    def ColumnCount(self):
        raise Exception(_translate("TestbedLogViewer", "Column Count Not Specified!!"))
    
    def Data(self, inColumn):
        raise Exception(_translate("TestbedLogViewer", "Data gather method not implemented!"))
    
    def Parent(self):
        return self.parent
    
    def Row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0
    def createTheWidget(self, col):
        return QtWidgets.QLabel()
    
# Represents the root of the tree    
class RootTreeItem(BaseTreeItem):
    def __init__(self):
        super(RootTreeItem, self).__init__(None, False)
        
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        # These become the column headers
        if inColumn == 0:
            return _translate("TestbedLogViewer", "Source Lexical Unit(s)")
        if inColumn == 1:
            return _translate("TestbedLogViewer", "Expected Result")
        if inColumn == 2:
            return _translate("TestbedLogViewer", "Actual Result")
        return ""
    
class TestStatsItem(BaseTreeItem):
    def __init__(self, inParent, rtl, statsObj):
        
        super(TestStatsItem, self).__init__(inParent, rtl)
        self.statsObj = statsObj
        self.localizedDTformatter = Utils.LocalizedDateTimeFormatter()
        
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        # Date and time of the test
        if inColumn == 0:
            
            try:
                # Reformat the time string according the locale
                startDT = QDateTime.fromString(self.statsObj.dateTimeStart, XML_DATETIME_FORMAT_QT)
                retStr = self.localizedDTformatter.formatDateTime(startDT)
            except:
                retStr = _translate("TestbedLogViewer", "Date format error.")
            return retStr
        # Results summary
        elif inColumn == 1:
            return self.statsObj.getTestResultSummary()
        return ''

    def createTheWidget(self, col):
        myLabel = QtWidgets.QLabel()
        myLabel.setText(self.Data(col))
        if self.isRTL():
            myLabel.setAlignment(QtCore.Qt.AlignRight)
        
        # Create the elapsed time tooltip
        total_secs = self.statsObj.getTestElapsedSeconds()
        minutes = total_secs // 60
        sec = total_secs % 60
        
        if minutes == 1:
            tipStr = _translate("TestbedLogViewer", 'Test completed in 1 minute and {seconds} seconds').format(seconds=sec)
        else:
            tipStr = _translate("TestbedLogViewer", 'Test completed in {minutes} minute and {seconds} seconds').format(seconds=sec, minutes=minutes)
        
        myLabel.setToolTip(tipStr)
        return myLabel

class TestResultItem(BaseTreeItem):
    
    def __init__(self, inParent, rtl, LUString, formattedLexicalUnitsString, expectedStr, actualStr, valid, origin, invalidReason, greenCheck, redX, yellowTriangle):
        super(TestResultItem, self).__init__(inParent, rtl)
        self.unformattedLexicalUnitsString = LUString
        self.formattedLexicalUnitsString = formattedLexicalUnitsString
        self.expectedStr = expectedStr
        self.actualStr = actualStr
        self.invalid = not valid
        self.origin = origin
        self.invalidReason = invalidReason
        self.greenCheck = greenCheck
        self.redX = redX
        self.yellowTriangle = yellowTriangle
        
    def testFailed(self):
        if self.expectedStr != self.actualStr:
            return True

        return False
        
    def isInvalid(self):
        return self.invalid
    
    def getFormattedLUString(self):
        return self.formattedLexicalUnitsString
    
    def getLUString(self):
        return self.unformattedLexicalUnitsString
    
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        # Lexical units
        if inColumn == 0:
            if self.isInvalid():
                
                myStr = self.getFormattedLUString()
                
                # Change the colors to orange when it's invalid
                myStr = color_re.sub(colorNumPunc, myStr) 
                
                return myStr
            else:
                return self.getFormattedLUString() 
            
        # Expected results
        elif inColumn == 1:
            return self.expectedStr
        
        # Actual results
        elif inColumn == 2:
            if self.isInvalid():
                return 'n/a'
            elif self.testFailed():
                p = ET.Element('p')
                outputLUSpan(p, NOT_FOUND_COLOR, self.actualStr, False) #rtl
                return ET.tostring(p, encoding='unicode')
            else:
                # Repeate the expected result in the actual result column
                p = ET.Element('p')
                outputLUSpan(p, SUCCESS_COLOR, self.expectedStr, False) #rtl
                return ET.tostring(p, encoding='unicode')
        return ''
    
    def createTheWidget(self, col):
        
        # Lexical units
        if col == 0:
            myWidget = ITWidget(self.isRTL())
            myWidget.setText(self.Data(col))

            # Get the appropriate icon
            if self.isInvalid():
                myIcon = self.yellowTriangle
            elif self.testFailed():
                myIcon = self.redX
            else:
                myIcon = self.greenCheck

            myWidget.setIcon(myIcon)
            
            # Set the tool tip text
            tip = 'Source text: ' + self.origin + '.'
            
            # if a lexical unit is invalid add the reason it's invalid to the tooltip
            if self.isInvalid():
                tip += ' ' + self.invalidReason
            myWidget.setToolTip(tip)

        # Expected and actual results
        else:
            myWidget = QtWidgets.QLabel(self.Data(col))
            
        return myWidget

# A widget for an icon and text
class ITWidget(QtWidgets.QWidget):

    def __init__(self, rtl):
        super(ITWidget, self).__init__()
        self.rtl = rtl
        self.autoFillBackground()
        self.__create()

    def __create(self):
        layout = QtWidgets.QHBoxLayout()
        self.iconLabel = QtWidgets.QLabel()
        self.textLabel = QtWidgets.QLabel()
        
        if self.rtl:
            layout.addWidget(self.iconLabel)
            layout.addWidget(self.textLabel,1)
        else:
            layout.addWidget(self.iconLabel)
            layout.addWidget(self.textLabel,1)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def setText(self, myText):
        self.textLabel.setText(myText)
        
    def setIcon(self, myIcon):
        self.iconLabel.setPixmap(myIcon)
        
    def setToolTip(self, myTip):
        self.textLabel.setToolTip(myTip)
        
class TestbedLogModel(QtCore.QAbstractItemModel):
    
    def __init__(self, resultsXMLObj, parent = None):

        self.__view = None
        self.rtl = resultsXMLObj.isRTL()
        self.greenCheck = QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, GREEN_CHECK)) 
        self.redX = QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, RED_X))
        self.yellowTriangle = QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, YELLOW_TRIANGLE))
        self.__cache = {}
        
        # initialize base class
        super(TestbedLogModel, self).__init__(parent)
        
        self.resultsXMLObj = resultsXMLObj
        
        # set the root item to add other items to
        self.rootItem = RootTreeItem()
        
        # setup the data
        self.SetupModelData()
    
    def getRTL(self):
        return self.rtl
    
    def setView(self, view):
        self.__view = view

    def getStats(self, resultObj):
        
        dateTimeStart = resultObj.getStartDateTime()
        dateTimeEnd = resultObj.getEndDateTime()
        
        totalTests = resultObj.getNumTests()
        
        (numFailed, numInvalid) = resultObj.getFailedAndInvalid()
        
        # Create a statistics object with the data from this result
        statsObj = Stats(dateTimeStart, dateTimeEnd, totalTests, numFailed, numInvalid)
        
        return statsObj
        
    def SetupModelData(self):
        
        objList = self.resultsXMLObj.getTestbedResultXMLObjectList()
        maxResults = len(objList)
        
        # Set max test results to display
        if maxResults > MAX_RESULTS_TO_DISPLAY:
            maxResults = MAX_RESULTS_TO_DISPLAY

        resultsCount = 1
        
        # Loop through the test results
        for resultObj in objList: # Just show the last X
            
            if resultsCount > maxResults:
                break
            
            # If this is an incomplete test (no end date-time), skip it
            if resultObj.isIncomplete():
                continue
            
            resultsCount += 1
            
            # Set the stats branch of the tree
            statsObj = self.getStats(resultObj)
            statsItem = TestStatsItem(self.rootItem, self.getRTL(), statsObj)
            
            ## Set the leaves on this branch -- each individual test result
            # Loop through the testbeds
            for testbed in resultObj.getFLExTransTestbedXMLObjectList():
                # Loop through the tests
                for i, test in enumerate(testbed.getTestXMLObjectList()):
                    
                    # Use the dump of the test XML node as the hash key
                    testNodeStr = ET.tostring(test.getTestNode(), encoding='unicode')

                    # But remove the unique id in the string
                    myHash = 1 # hash(Utils.removeTestID(testNodeStr))
                    
                    # Check if we have cached this test object and use it if we have
                    if myHash in self.__cache:
                        
                        resultItem = self.__cache[myHash]
                    # Otherwise build the TestResultItem object and then add it to the cache
                    else:
                        resultItem = TestResultItem(statsItem,  self.getRTL(), test.getLUString(), test.getFormattedLUString(self.getRTL()), test.getExpectedResult(), \
                                  test.getActualResult(), test.isValid(), test.getOrigin(), test.getInvalidReason(), self.greenCheck, self.redX, self.yellowTriangle)
                        
                        #self.__cache[myHash] = resultItem
                                     
                    # Add the result item to the current stats item
                    statsItem.AddChild(resultItem)
            
            # Add to the root
            self.rootItem.AddChild(statsItem)

    def index(self, row, column, parentindex): 
        
        if parentindex.isValid():
            nodeS = parentindex.internalPointer()
            nodeX = nodeS.GetChild(row)
            index = self.__createIndex(row, column, nodeX)
        else:
            nodeS = self.rootItem
            nodeX = nodeS.GetChild(row)
            index = self.__createIndex(row, column, nodeX)
        return index


    def __createIndex(self, row, column, node):
        if node.index == None:
            index = self.createIndex(row, column, node)
            node.index = index
        if node.widget[column] is None:
            # Create the needed widget depending on item type
            widget = node.createTheWidget(column)
            node.widget[column] = widget
            self.__view.setIndexWidget(self.createIndex(row, column, node), widget)

        return node.index

    def parent(self, childindex):

        if not childindex.isValid():
            return QtCore.QModelIndex()
        
        child_item = childindex.internalPointer()
        if not child_item:
            return QtCore.QModelIndex()
        
        parent_item = child_item.GetParent()
        
        if parent_item == self.rootItem:
            return QtCore.QModelIndex()
        
        return self.createIndex(parent_item.Row(), 0, parent_item)
                    
    def rowCount(self, parentindex):
        
        if parentindex.column() > 0:
            return 0
        
        item = None
        if not parentindex.isValid():
            item = self.rootItem
        else:
            item = parentindex.internalPointer()
            
        return item.GetChildCount()

    def columnCount(self, parentindex):
        
        if not parentindex.isValid():
            return self.rootItem.ColumnCount()
        
        return parentindex.internalPointer().ColumnCount()
    
    def data(self, index, role):

        # handled in the widgets
        return None
    
    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return self.rootItem.Data(column)
            except IndexError:
                pass

        if role == QtCore.Qt.TextAlignmentRole:
            if self.getRTL():
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter
        
        return QtCore.QVariant()
                
class LogViewerMain(QMainWindow):

    def __init__(self, resultsXMLObj, testbedPath):
        QMainWindow.__init__(self)
        self.ui = Ui_TestbedLogWindow()
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.testbedPath = testbedPath
        self.__model = TestbedLogModel(resultsXMLObj)
        self.ui.logTreeView.setModel(self.__model)
        self.__model.setView(self.ui.logTreeView)

        # check the text direction of the test language
        if self.__model.getRTL():
            self.ui.logTreeView.setLayoutDirection(QtCore.Qt.RightToLeft)
        
        self.ui.OKButton.clicked.connect(self.okClicked)
        self.ui.editTestbedButton.clicked.connect(self.EditTestbedClicked)
        self.ui.fontSizeSpinBox.valueChanged.connect(self.FontSizeSpinBoxClicked)

        # Start the font size at 12
        self.ui.fontSizeSpinBox.setValue(12)
        
        # Make the header text bold
        headerFont = self.ui.logTreeView.header().font()
        headerFont.setBold(True)
        self.ui.logTreeView.header().setFont(headerFont)

    def FontSizeSpinBoxClicked(self):
        myFont = self.ui.logTreeView.font()
        currentSize = self.ui.fontSizeSpinBox.value()
        myFont.setPointSize(currentSize)
        self.ui.logTreeView.setFont(myFont)
        
    def getModel(self):
        return self.__model
    
    def okClicked(self):
        self.retValue = QDialogButtonBox.Ok
        self.close()

    def EditTestbedClicked(self):
        progFilesFolder = os.environ['ProgramFiles(x86)']
        
        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
        
        call([xxe, self.testbedPath])

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.myResize()
        
    def myResize(self):    
        myWidth = self.ui.logTreeView.width()
        
        colWidthReduction = 7 # so we don't go over total width and get a horizontal scrollbar
        
        # Set the width of the columns
        self.ui.logTreeView.setColumnWidth(0, myWidth*5//10-colWidthReduction) 
        self.ui.logTreeView.setColumnWidth(1, myWidth*3//10-colWidthReduction) 
        self.ui.logTreeView.setColumnWidth(2, myWidth*2//10-colWidthReduction)
    
def RunTestbedLogViewer(report):
        
    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file 
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    testbedPath = ReadConfig.getConfigVal(configMap, ReadConfig.TESTBED_FILE, report)

    if not testbedPath:
        return 
    
    # We can't do anything if there is no testbed
    if os.path.exists(testbedPath) == False:
        report.Error(_translate("TestbedLogViewer", 'Testbed file: {testbedPath} does not exist. Please add tests to the testbed.').format(testbedPath=testbedPath))
        return None
    
    ## Load the testbed results
    
    # Create an object for the testbed results file
    resultsFileObj = FlexTransTestbedResultsFile(report)
    
    # Get previous results
    resultsXMLObj = resultsFileObj.getResultsXMLObj()

    window = LogViewerMain(resultsXMLObj, testbedPath)
    
    window.show()
    window.myResize()
    if len(window.getModel().rootItem.children) > 0:
        
        firstIndex = window.getModel().rootItem.children[0].index
        window.ui.logTreeView.expand(firstIndex)
        
    app.exec_()

def MainFunction(DB, report, modify):
    
    RunTestbedLogViewer(report)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
