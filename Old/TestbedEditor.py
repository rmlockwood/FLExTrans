#
#   TestbedEditor
#
#   Ron Lockwood
#   SIL International
#   8/29/18
#
#   Version 1.0 - ??/??/18 - Ron Lockwood
#
#   Show a table which holds the testbed data. It basically consists of a collection
#   of tests. Each test is composed of a set of lexical units and the target text
#   that you get when you run FLExTrans on those lexical units. You can edit a test,
#   add a test or delete a test.
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
import TestbedValidator
import xml.etree.ElementTree as ET
from PyQt4.QtGui import QInputDialog, QMessageBox
from _sqlite3 import Row

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Testbed Editor",
        'moduleVersion'    : "1.0",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Edit, add or delete tests in the testbed.",
        'moduleDescription'   :
u"""
Edit, add or delete tests in the testbed.
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
from datetime import datetime
 
from PyQt4 import QtGui, QtCore
from PyQt4 import QtWebKit
from TestbedEdit import Ui_mainWindow

RED_X =           'Red_x.png'

class MyLabel(QtGui.QLabel):
    
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)
    
    def setModel(self, model):
        self.__model = model
        
    def mouseDoubleClickEvent(self, event):
        
        myStr = self.text()
        myStr = re.sub('<.+?>', '', str(myStr))
        (myStr, ret) = QtGui.QInputDialog.getText(self, 'Edit Lexical Unit(s)', 'Lexical Unit(s)',\
                                           QtGui.QLineEdit.Normal, QtCore.QString(myStr))
        # exit if they cancelled
        if ret == False:
            return
        
        # Get Lexical Unit Objects from the string
        myParser = Utils.LexicalUnitParser(str(myStr))
        
        if myParser.isWellFormed() == False:
            # Error message
            QMessageBox.warning(self, 'Lexical unit error', 'The lexical unit(s) is/are incorrectly formed.')
            return
        
        myValidator = TestbedValidator.TestbedValidator(self.__model.getDB(), self.__model.getReport())

        myStr = ''
        
        # Loop through all the lexical units
        for lu in myParser.getLexicalUnits():
            
            # Do validation
            if myValidator.isValid(lu) == False:
                
                reason = myValidator.getInvalidReason()
                QMessageBox.warning(self, 'Lexical unit invalid', 'For the lexical unit: ' + lu.toString() + ' -- ' + reason)
                return
            
            # Convert to colored and formated version
            myStr += ' ' + lu.toFormattedString()
        
        myStr = myStr.strip()
        
        # Set the internal text value
        self.setText(QtCore.QString(myStr))
        
class MyToolButton(QtGui.QToolButton):
    
    def __init__(self, parent):
        QtGui.QToolButton.__init__(self, parent)
        
        self.clicked.connect(self.yo)
        
    def setModel(self, model):
        self.__model = model
        
    def setRow(self, row):
        self.__row = row
        
    def yo(self):
        
        # Delete the row
        self.__model.removeRows(self.__row, 1)

class TestbedTable(QtCore.QAbstractTableModel):
    
    def __init__(self, testObjList, DB, report, parent = None):
        self.__view = None
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__testObjList = testObjList
        self.__DB = DB
        self.__report = report
        self.__myHeaderData = ['', 'Source Lexical Units', 'Expected Result']
        self.__widgetMap = {}
        self.__buttonMap = {}
    def getDB(self):
        return self.__DB
    def getReport(self):
        return self.__report
    def setView(self, view):
        self.__view = view
    def getInternalData(self):
        return self.__testObjList
    def setInternalData(self, Data):
        self.__testObjList = Data
    def rowCount(self, parent):
        return len(self.__testObjList)
    def columnCount(self, parent):
        return 3 
    def headerData(self, section, orientation, role):
        # Set the background color
        if role == QtCore.Qt.BackgroundRole:
            qColor = QtGui.QColor(QtCore.Qt.gray)
            return qColor
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.__myHeaderData[section]
            else:
                return

    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
    
        self.beginRemoveRows(parent, row, row+1) # assume 1 row
        
        # Remove this row from our data
        self.__testObjList.pop(row)
       
#        self.__widgetMap.clear()
#        self.__buttonMap.clear()
         
        # Remove the widgets from the widget maps
#         for key, val in sorted(self.__buttonMap.items(), key=lambda x: x[0]):
#             nextKey = key+1
#             if key > row and nextKey in self.__buttonMap:
#                 self.__buttonMap[key] = self.__buttonMap[nextKey]
#         
#         j = row+1
#         if j in self.__buttonMap:
#             self.__buttonMap.pop(j)
#         
#         for key, val in sorted(self.__widgetMap.items(), key=lambda x: x[0]):
#             nextKey = key+1
#             if key > row and nextKey in self.__widgetMap:
#                 self.__widgetMap[key] = self.__widgetMap[nextKey]
# 
#         if j in self.__widgetMap:
#             self.__widgetMap.pop(j)
        
        self.endRemoveRows()
        return True
        
    def index(self, row, column, parentindex):
        myIndex = None 
        
        # Delete button
        if column == 0 and row == 0:
            if row not in self.__buttonMap:
                myIndex = self.createIndex(row, column)

                # Create a toolbar button
                myToolButton = MyToolButton(self.__view)
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("grey_x"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                myToolButton.setIcon(icon)

                myToolButton.setModel(self)
                myToolButton.setRow(row)
                
                self.__buttonMap[row] = (myToolButton, myIndex)
                
                self.__view.setIndexWidget(myIndex, myToolButton)
            else:
                myIndex = parentindex            
        
        # If we are on the lexical units column, use a QLabel for displaying html data
        elif column == 1 and row == 0: # lexical units
            
            # add to the map
            if row not in self.__widgetMap:
                myIndex = self.createIndex(row, column)
                widget = MyLabel(self.getDataByCol(row, column))
                widget.setModel(self)

                #widget.clicked.connect(self.luLabelClicked)
                self.__widgetMap[row] = (widget, myIndex)
                
                self.__view.setIndexWidget(myIndex, widget)
            else:
                myIndex = parentindex
        else:
            myIndex = self.createIndex(row, column)
    
        return myIndex
    
    def getDataByCol(self, row, col):
        if col == 1:
            return self.__testObjList[row].getFormattedLUString()
        elif col == 2:
            return self.__testObjList[row].getExpectedResult()
        else:
            return None
                
    def data(self, index, role):
        row = index.row()
        col = index.column()
        
        if role == QtCore.Qt.EditRole:
            return self.getDataByCol(row, col)
        
        if role == QtCore.Qt.DisplayRole:
            
            value = self.getDataByCol(row, col)
                
            if type(value) == str:
                return QtCore.QString(value)
            
#        elif role == QtCore.Qt.TextAlignmentRole:
            # Check if we have right to left data in a column, if so align it right
#             if col > 0 and len(self.__testObjList[row].getDataByColumn(col)) > 0:
#                 
#                 # check first character of the given cell
#                 if unicodedata.bidirectional(self.__testObjList[row].getDataByColumn(col)[0]) in (u'R', u'AL'): 
#                     
#                     return QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter
    def flags(self, index):
        # Columns 0 and 1 are editable
        val = QtCore.Qt.ItemIsEnabled
        if index.column() == 1:
            val = val | QtCore.Qt.ItemIsEditable 
        if index.column() == 2:
            val = val | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable 
        return val
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            # is this where we set the local data in the array?
            # self.__testObjList[row][col] = str(value)
        return True
            
class Main(QtGui.QMainWindow):

    def __init__(self, testObjList, DB, report):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.okClicked)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.cancelClicked)

        self.__model = TestbedTable(testObjList, DB, report)
        self.ui.tableView.setModel(self.__model)
        self.__model.setView(self.ui.tableView)
        
        # Create delete buttons
#         for i in range(0, len(testObjList)):
# 
#             myToolButton = QtGui.QToolButton(self.centralwidget)
#             
#             icon = QtGui.QIcon()
#             icon.addPixmap(QtGui.QPixmap(_fromUtf8("Red_x.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         self.toolButton_2.setIcon(icon)
#         self.toolButton_2.setObjectName(_fromUtf8("toolButton_2"))

        
    def okClicked(self):
        
        # write out changed data
        pass
    
    def cancelClicked(self):
        
        # close
        pass
    
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        self.myResize()
        
    def myResize(self):    
        myWidth = self.ui.tableView.width()
        
        # Set the width of the columns
        iconColWidth = 26
        self.ui.tableView.setColumnWidth(0, iconColWidth) 
        self.ui.tableView.setColumnWidth(1, (myWidth-iconColWidth)*6/10-15) # -15 so we don't go over total
        self.ui.tableView.setColumnWidth(2, (myWidth-iconColWidth)*4/10-15) # width and get a horizontal
        
def MainFunction(DB, report, modify):
        
    testbedXMLObj = None
    
    # Create an object for the testbed file
    testbedFileObj = Utils.FlexTransTestbedFile(None)
    
    # If there's no testbed, start with a blank table
    if testbedFileObj.exists() == False:
        
        pass

    else:
    
        # Validate the source lexical units in the testbed XML file and write the changes if needed
        testbedFileObj.validate(DB, report)
        
        # Get the testbed XML object
        testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
        
        # Get a 2-dimensional array. List of tests with each test containing two things:
        # 1) Source Lexical Units and 2) Expected Result
        testObjList = testbedXMLObj.getTestXMLObjectList()

    app = QtGui.QApplication(sys.argv)

    window = Main(testObjList, DB, report)
    
    window.show()
    window.myResize()
    
    
    #firstIndex = window.getModel().rootItem.children[0].index
    #window.ui.logTreeView.expand(firstIndex)
    
    exec_val = app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
