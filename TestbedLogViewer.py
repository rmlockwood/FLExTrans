#
#   TestbedLogViewer
#
#   Ron Lockwood
#   SIL International
#   6/22/18
#
#   Version 1.0 - ??/??/18 - Ron Lockwood
#
#   Show the testbed log which shows the results of tests run for a certain
#   date/time.
#

from FTModuleClass import FlexToolsModuleClass
import ReadConfig
import os
import re
import tempfile
import sys
import unicodedata
import copy
import datetime
import Utils

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Testbed Log Viewer",
        'moduleVersion'    : "1.0",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "View testbed run results.",
        'moduleDescription'   :
u"""
View testbed run results.
""" }
                 
#----------------------------------------------------------------
# The main processing function

from SIL.FieldWorks.FDO import ILexPronunciation
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import ITextFactory, IStTextFactory, IStTxtParaFactory
from SIL.FieldWorks.FDO import ILexEntryRepository
from SIL.FieldWorks.FDO import ILexSenseRepository
from SIL.FieldWorks.FDO import ILexEntry, ILexSense
from SIL.FieldWorks.FDO import SpecialWritingSystemCodes
from SIL.FieldWorks.FDO.DomainServices import SegmentServices
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import IUndoStackManager
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
from System import Guid
from System import String
 
from PyQt4 import QtGui, QtCore
from PyQt4 import QtWebKit
from TestbedLog import Ui_MainWindow

# An item that can be used to populate a tree view, knowing it's place in the model
class BaseTreeItem(object):
    
    def __init__(self, inParentItem):
        self.parent = inParentItem
        self.children = []
        
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
    
class Stats():
    def __init__(self, dateTime, totalTests, numFailed, numInvalid):
        self.dateTime = dateTime
        self.totalTests = totalTests
        self.numFailed = numFailed
        self.numInvalid = numInvalid
    
    def getFormatedResult(self):
        return str(self.totalTests) + ' Tests, ' + str(self.numFailed) + ' Failed, ' + str(self.numInvalid) + ' Invalid'
    
# Represents the root of the tree    
class RootTreeItem(BaseTreeItem):
    def __init__(self):
        super(RootTreeItem, self).__init__(None)
        
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
    def __init__(self, inParent, statsObj):
        
        super(TestStatsItem, self).__init__(inParent)
        self.statsObj = statsObj
        
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        if inColumn == 0:
            return self.statsObj.dateTime
        elif inColumn == 2:
            return self.statsObj.getFormatedResult()
        return ''
    
class TestResultItem(BaseTreeItem):
    
    def __init__(self, inParent, lexicalUnitList, expectedStr, actualStr):
        super(TestResultItem, self).__init__(inParent)
        self.lexicalUnitList = lexicalUnitList
        self.expectedStr = expectedStr
        self.actualStr = actualStr
        
    def getLUString(self):
        ret_str = ''
        
        for lu in self.lexicalUnitList:
            ret_str += ' ' + lu.toString()
        
        return ret_str.strip()
    
    def ColumnCount(self):
        return 3
    
    def Data(self, inColumn):
        if inColumn == 0:
            return self.getLUString()
        elif inColumn == 1:
            return self.expectedStr
        elif inColumn == 2:
            return self.actualStr
        return ''
    
class TestbedLogModel(QtCore.QAbstractItemModel):
    
    def __init__(self, resultsXMLObj, parent = None):
        
        # initialize base class
        super(TestbedLogModel, self).__init__(parent)
        
        self.resultsXMLObj = resultsXMLObj
        
        # set the root item to add other items to
        self.rootItem = RootTreeItem()
        
        # setup the data
        self.SetupModelData()
    
    def getStats(self, resultObj):
        
        dateTime = resultObj.getStartDateTime()
        
        totalTests = resultObj.getNumTests()
        
        (numFailed, numInvalid) = resultObj.getFailedAndInvalid()
        
        # Create a statistics object with the data from this result
        statsObj = Stats(dateTime, totalTests, numFailed, numInvalid)
        
        return statsObj
        
    def SetupModelData(self):
        
        # Loop through the test results
        for resultObj in self.resultsXMLObj.getTestbedResultXMLObjectList():
            
            # If this is an incomplete test (no end date-time), skip it
            if resultObj.isIncomplete():
                continue
            
            # Set the stats branch of the tree
            statsObj = self.getStats(resultObj)
            statsItem = TestStatsItem(self.rootItem, statsObj)
            
            ## Set the leaves on this branch -- each individual test result
            # Loop through the testbeds
            for testbed in resultObj.getFLExTransTestbedXMLObjectList():
                # Loop through the tests
                for test in testbed.getTestXMLObjectList():
                    
                    resultItem = TestResultItem(statsItem, test.getLexicalUnitList(), test.getExpectedResult(), test.getActualResult())
                    
                    # Add the result item to the current stats item
                    statsItem.AddChild(resultItem)
            
            # Add to the root
            self.rootItem.AddChild(statsItem)

    def index(self, row, column, parentindex): 
        
        # if the index does not exist, return a default index
        if not self.hasIndex(row, column, parentindex):
            return QtCore.QModelIndex()
        
        # make sure the parent exists, if not assume it's the root
        parent_item = None
        if not parentindex.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parentindex.internalPointer()
            
        # get the child from that parent and create an index for it
        child_item = parent_item.GetChild(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()
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
        
        if not index.isValid():
            return QtCore.QVariant()
        
        # get the item out of the index
        parent_item = index.internalPointer()
        
        # Return the data associated with the column
        if role == QtCore.Qt.DisplayRole:
            return parent_item.Data(index.column())
        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(50,50)
        
        # Otherwise return default
        return QtCore.QVariant()
    
    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return self.rootItem.Data(column)
            except IndexError:
                pass

        return QtCore.QVariant()
                
class Main(QtGui.QMainWindow):

    def __init__(self, resultsXMLObj):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__model = TestbedLogModel(resultsXMLObj)
        self.ui.logTreeView.setModel(self.__model)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.okClicked)

        #self.makeWebViews()
        #self.setGeometry(500,500,1200,800)
        #self.myResize()

    def okClicked(self):
        self.retValue = QtGui.QDialogButtonBox.Ok
        self.close()

    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        self.myResize()
        
    def myResize(self):    
        myWidth = self.ui.logTreeView.width()
        
        # Set the width of the lexical unit to 40%, the other two columns to 30%
        self.ui.logTreeView.setColumnWidth(0, myWidth*4/10)
        self.ui.logTreeView.setColumnWidth(1, myWidth*3/10)
        self.ui.logTreeView.setColumnWidth(2, myWidth*3/10)
    
    def makeWebViews(self):
        
        myIndex = self.__model.index(2,2, QtCore.QModelIndex())
        webView = QtWebKit.QWebView()
        #webView.setGeometry(QtCore.QRect(10, 10, 100, 100))
        self.ui.logTreeView.setIndexWidget(myIndex, webView)
        
def MainFunction(DB, report, modify):
        
    ## Load the testbed results
    
    # Create an object for the testbed results file
    resultsFileObj = Utils.FlexTransTestbedResultsFile()
    
    # Initialize the testbed run
    resultsXMLObj = resultsFileObj.getResultsXMLObj()

    app = QtGui.QApplication(sys.argv)

    window = Main(resultsXMLObj)
    
    window.show()
    exec_val = app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
