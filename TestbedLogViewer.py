#
#   TestbedLogViewer
#
#   Ron Lockwood
#   SIL International
#   6/22/18
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.0 - 4/19/2019 - Ron Lockwood
#
#   Show the testbed log which shows the results of tests run for a certain
#   date/time.
#

import os
import re
import tempfile
import sys
import unicodedata
import copy
import datetime
import xml.etree.ElementTree as ET
from System import Guid
from System import String
from datetime import datetime
from PyQt4 import QtGui, QtCore
from PyQt4 import QtWebKit
import ReadConfig
import Utils

from flexlibs.FLExDBAccess import *                                         
from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
 
from TestbedLog import Ui_MainWindow

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Testbed Log Viewer",
        FTM_Version    : "1.7",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "View testbed run results.",
        FTM_Help   : "", 
        FTM_Description:  
u"""
View testbed run results.
""" }
                 
#----------------------------------------------------------------

GREEN_CHECK =     'Light_green_check.png'        
RED_X =           'Red_x.png'
YELLOW_TRIANGLE = 'Yellow_triangle.png'

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
            startDT = datetime.strptime(self.dateTimeStart, Utils.XML_DATETIME_FORMAT)
            endDT = datetime.strptime(self.dateTimeEnd, Utils.XML_DATETIME_FORMAT)
        except:
            return 0
        
        elapsedSecs = endDT - startDT
        
        return elapsedSecs.seconds
        
    def getTestResultSummary(self):
        if self.numFailed > 0:
            myColor = Utils.NOT_FOUND_COLOR
        elif self.numInvalid > 0:
            myColor = Utils.PUNC_COLOR
        else:
            myColor = Utils.AFFIX_COLOR

        myStr = str(self.totalTests) + ' Tests, ' + str(self.numFailed) + ' Failed, ' + str(self.numInvalid) + ' Invalid'

        p = ET.Element('p')
        Utils.output_span(p, myColor, myStr, False) #rtl
        return ET.tostring(p)

    
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
        raise Exception("Column Count Not Specified!!")
    
    def Data(self, inColumn):
        raise Exception("Data gather method not implemented!")
    
    def Parent(self):
        return self.parent
    
    def Row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0
    def createTheWidget(self, col):
        return QtGui.QLabel()
    
# Represents the root of the tree    
class RootTreeItem(BaseTreeItem):
    def __init__(self):
        super(RootTreeItem, self).__init__(None, False)
        
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        # These become the column headers
        if inColumn == 0:
            return "Source Lexical Unit(s)"
        if inColumn == 1:
            return "Expected Result"
        if inColumn == 2:
            return "Actual Result"
        return ""
    
class TestStatsItem(BaseTreeItem):
    def __init__(self, inParent, rtl, statsObj):
        
        super(TestStatsItem, self).__init__(inParent, rtl)
        self.statsObj = statsObj
        
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        # Date and time of the test
        if inColumn == 0:
            
            try:
                # Reformat the time string
                startDT = datetime.strptime(self.statsObj.dateTimeStart, Utils.XML_DATETIME_FORMAT)
                retStr = startDT.strftime('%d %b %Y %H:%M:%S')
            except:
                retStr = "Date format error."
            return retStr
        # Results summary
        elif inColumn == 1:
            return self.statsObj.getTestResultSummary()
        return ''

    def createTheWidget(self, col):
        myLabel = QtGui.QLabel()
        myLabel.setText(self.Data(col))
        if self.isRTL():
            myLabel.setAlignment(QtCore.Qt.AlignRight)
        
        # Create the elapsed time tooltip
        total_secs = self.statsObj.getTestElapsedSeconds()
        
        minutes = total_secs / 60
        sec = total_secs % 60
        
        if minutes == 1:
            myStr = '1 minute and '
        elif minutes > 1:
            myStr = str(minutes) + ' minutes and ' 
        else:
            myStr = ''
            
        myStr += str(sec) + ' seconds'
        
        tipStr = 'Test completed in ' + myStr
        
        myLabel.setToolTip(tipStr)
        
        return myLabel

class TestResultItem(BaseTreeItem):
    
    def __init__(self, inParent, rtl, LUString, formattedLexicalUnitsString, expectedStr, actualStr, valid, origin, invalidReason):
        super(TestResultItem, self).__init__(inParent, rtl)
        self.unformattedLexicalUnitsString = LUString
        self.formattedLexicalUnitsString = formattedLexicalUnitsString
        self.expectedStr = expectedStr
        self.actualStr = actualStr
        self.invalid = not valid
        self.origin = origin
        self.invalidReason = invalidReason
        self.greenCheck = QtGui.QPixmap(GREEN_CHECK)
        self.redX = QtGui.QPixmap(RED_X)
        self.yellowTriangle = QtGui.QPixmap(YELLOW_TRIANGLE)
        
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
                myStr = re.sub('color:#......', 'color:#'+Utils.PUNC_COLOR, myStr)
                
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
                Utils.output_span(p, Utils.NOT_FOUND_COLOR, self.actualStr, False) #rtl
                return ET.tostring(p)
            else:
                retStr = '---'
                # keep ltr unless the expected data is rtl
                if isinstance(self.expectedStr[0], str) == False and unicodedata.bidirectional(self.expectedStr[0]) in (u'R', u'AL'):
                #if self.isRTL():
                    retStr = u'\u200F' + retStr
                return retStr
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
            myWidget = QtGui.QLabel(self.Data(col))
#             if self.isRTL():
#                 myWidget.setAlignment(QtCore.Qt.AlignRight)
            
        return myWidget

# A widget for an icon and text
class ITWidget(QtGui.QWidget):

    def __init__(self, rtl):
        super(ITWidget, self).__init__()
        self.rtl = rtl
        self.autoFillBackground()
        self.__create()

    def __create(self):
        layout = QtGui.QHBoxLayout()
        self.iconLabel = QtGui.QLabel()
        self.textLabel = QtGui.QLabel()
        
        if self.rtl:
            layout.addWidget(self.iconLabel)
            layout.addWidget(self.textLabel,1)
            #layout.setDirection(0)
            #self.iconLabel.setAlignment(QtCore.Qt.AlignRight)
            #self.textLabel.setAlignment(QtCore.Qt.AlignRight)
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
        
        # Loop through the test results
        for resultObj in self.resultsXMLObj.getTestbedResultXMLObjectList():
            
            # If this is an incomplete test (no end date-time), skip it
            if resultObj.isIncomplete():
                continue
            
            # Set the stats branch of the tree
            statsObj = self.getStats(resultObj)
            statsItem = TestStatsItem(self.rootItem, self.getRTL(), statsObj)
            
            ## Set the leaves on this branch -- each individual test result
            # Loop through the testbeds
            for testbed in resultObj.getFLExTransTestbedXMLObjectList():
                # Loop through the tests
                for test in testbed.getTestXMLObjectList():
                    
                    resultItem = TestResultItem(statsItem,  self.getRTL(), test.getLUString(), test.getFormattedLUString(self.getRTL()), \
                                                test.getExpectedResult(), test.getActualResult(), \
                                                test.isValid(), test.getOrigin(), test.getInvalidReason())
                    
                    # Add the result item to the current stats item
                    statsItem.AddChild(resultItem)
            
            # Add to the root
            self.rootItem.AddChild(statsItem)

    def index(self, row, column, parentindex): 
        
        node = QtCore.QModelIndex()
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
                
class LogViewerMain(QtGui.QMainWindow):

    def __init__(self, resultsXMLObj):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__model = TestbedLogModel(resultsXMLObj)
        self.ui.logTreeView.setModel(self.__model)
        self.__model.setView(self.ui.logTreeView)

        # check the text direction of the test language
        if self.__model.getRTL():
            self.ui.logTreeView.setLayoutDirection(QtCore.Qt.RightToLeft)
        
        self.ui.OKButton.clicked.connect(self.okClicked)
        self.ui.editTestbedButton.clicked.connect(self.EditTestbedClicked)
        self.ui.fontSizeSpinBox.valueChanged.connect(self.FontSizeSpinBoxClicked)

        # Start the font size at 9
        self.ui.fontSizeSpinBox.setValue(9)
        
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
        self.retValue = QtGui.QDialogButtonBox.Ok
        self.close()

    def EditTestbedClicked(self):
        pass

    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        self.myResize()
        
    def myResize(self):    
        myWidth = self.ui.logTreeView.width()
        
        # Set the width of the columns
        self.ui.logTreeView.setColumnWidth(0, myWidth*5/10-3) # -3 so we don't go over total
        self.ui.logTreeView.setColumnWidth(1, myWidth*3/10-3) # width and get a horizontal
        self.ui.logTreeView.setColumnWidth(2, myWidth*2/10-3) # scrollbar
    
def MainFunction(DB, report, modify):
        
    # Create an object for the testbed file
    testbedFileObj = Utils.FlexTransTestbedFile(None)

    # We can't do anything if there is no testbed
    if testbedFileObj.exists() == False:
        report.Error('Testbed does not exist. Please add tests to the testbed.')
        return None
    
    ## Load the testbed results
    
    # Create an object for the testbed results file
    resultsFileObj = Utils.FlexTransTestbedResultsFile()
    
    # Get previous results
    resultsXMLObj = resultsFileObj.getResultsXMLObj()

    app = QtGui.QApplication(sys.argv)

    window = LogViewerMain(resultsXMLObj)
    
    window.show()
    window.myResize()
    firstIndex = window.getModel().rootItem.children[0].index
    window.ui.logTreeView.expand(firstIndex)
    exec_val = app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
