#
#   ClustwerUtils
#
#   Ron Lockwood
#   SIL International
#   12/30/2024
#
#   Version 3.12 - 12/30/2024 - Ron Lockwood
#    Initial version.
#

from ComboBox import CheckableComboBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QComboBox

IMP_EXP_WINDOW_HEIGHT = 260
IMP_EXP_WINDOW_WIDTH = 440

def initClusterWidgets(self, widgetClass, parentWin, header1TextStr, header2TextStr, width, specialProcessFunc=None):

    self.originalOKyPos = self.ui.OKButton.y()
    self.originalMainWinHeight = IMP_EXP_WINDOW_HEIGHT
    self.widgetList = []
    self.keyWidgetList = []

    # Initialize label and ptx combo boxes for all cluster projects
    for x in range(len(self.clusterProjects)):

        # Create the label
        labelWidget = QLabel(parentWin)
        labelWidget.setGeometry(QtCore.QRect(10, 190, 191, 21))
        labelWidget.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        labelWidget.setObjectName(f"label{x}")
        labelWidget.setText(self.clusterProjects[x])
        labelWidget.setVisible(False)
        
        # Create the combo box
        keyWidget = widgetClass(parentWin) 
        keyWidget.setGeometry(QtCore.QRect(210, 190, width, 22))
        keyWidget.setObjectName(f"combo{x}")
        keyWidget.setVisible(False)

        # Do special processing
        if specialProcessFunc:

            specialProcessFunc(keyWidget) # do we need to pass self as the 1st param?

        self.widgetList.append((labelWidget, keyWidget))

    if len(self.clusterProjects) > 0:

        # Create header widgets
        font = QtGui.QFont()
        font.setUnderline(True)
        self.headWidg1 = QLabel(parentWin)
        self.headWidg1.setGeometry(QtCore.QRect(10, 190, 191, 22))
        self.headWidg1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.headWidg1.setObjectName("headerLabel1")
        self.headWidg1.setText(header1TextStr)
        self.headWidg1.setVisible(False)
        self.headWidg1.setFont(font)

        self.headWidg2 = QLabel(parentWin)
        self.headWidg2.setGeometry(QtCore.QRect(210, 190, 221, 22))
        self.headWidg2.setObjectName("headerLabel2")
        self.headWidg2.setText(header2TextStr)
        self.headWidg2.setVisible(False)
        self.headWidg2.setFont(font)

def initClusterProjects(self, allClusterProjects, savedClusterProjects, parentWin):

    # Setup the checkable combo box for cluster projects. ***Replace*** the one from the designer tool.
    geom = self.ui.clusterProjectsComboBox.geometry() # same as old control
    self.ui.clusterProjectsComboBox.hide()
    self.ui.clusterProjectsComboBox = CheckableComboBox(parentWin)
    self.ui.clusterProjectsComboBox.setGeometry(geom)
    self.ui.clusterProjectsComboBox.setObjectName("clusterProjectsComboBox")
    self.ui.clusterProjectsComboBox.addItems([proj for proj in allClusterProjects if proj])

    # Connect a custom signal a function
    self.ui.clusterProjectsComboBox.itemCheckedStateChanged.connect(self.clusterSelectionChanged)

    # Check all of them at the start
    for projectName in allClusterProjects:

        # Check the ones that were saved.
        if savedClusterProjects:
            
            if projectName in savedClusterProjects:
        
                self.ui.clusterProjectsComboBox.check(projectName)

    # Set up the display the first time
    self.clusterSelectionChanged()

def showClusterWidgets(self):

    WIDGET_SIZE_PLUS_SPACE = 33
    addY = 0
    self.keyWidgetList = []
    startYpos = self.ui.clusterProjectsComboBox.y() + WIDGET_SIZE_PLUS_SPACE - 10
    comboStartXpos = self.ui.clusterProjectsComboBox.x()
    labelStartXpos = self.ui.clusterProjectsLabel.x()

    # Show the header labels if we have cluster projects selected
    if len(self.ui.clusterProjectsComboBox.currentData()) > 0:

        self.headWidg1.setGeometry(labelStartXpos, startYpos+10, self.headWidg1.width(), self.headWidg1.height())
        self.headWidg1.setVisible(True)
        self.headWidg2.setGeometry(comboStartXpos, startYpos+10, self.headWidg2.width(), self.headWidg2.height())
        self.headWidg2.setVisible(True)

        # Show the user the normal Paratext abbreviation won't be used
        self.topWidget1.setEnabled(False)
        self.topWidget2.setEnabled(False)
    else:
        self.headWidg1.setVisible(False)
        self.headWidg2.setVisible(False)
        self.topWidget1.setEnabled(True)
        self.topWidget2.setEnabled(True)
        
    # See which new widgets need to be shown
    for i, proj in enumerate(self.clusterProjects):

        currentList = self.ui.clusterProjectsComboBox.currentData()

        if proj in currentList:

            addY += WIDGET_SIZE_PLUS_SPACE

            ## Position the widgets and unhide them
            # First the label
            wid = self.widgetList[i][0]
            wid.setGeometry(labelStartXpos, startYpos+addY, wid.width(), wid.height())
            wid.setVisible(True)
            
            # Now the key widget
            wid = self.widgetList[i][1]
            wid.setGeometry(comboStartXpos, startYpos+addY, wid.width(), wid.height())
            wid.setVisible(True)
            self.keyWidgetList.append(wid)
        else:
            # Hide the widgets
            self.widgetList[i][0].setVisible(False)
            self.widgetList[i][1].setVisible(False)

    # Calculate how many pixels to move things
    pixels = len(self.ui.clusterProjectsComboBox.currentData()) * WIDGET_SIZE_PLUS_SPACE

    if pixels > 0:
        pixels += WIDGET_SIZE_PLUS_SPACE

    # Move some widgets down
    widgetsToMove = [
        self.ui.OKButton,
        self.ui.CancelButton,
    ]
    for wid in widgetsToMove:

        wid.setGeometry(wid.x(), self.originalOKyPos+pixels, wid.width(), wid.height())

    # Increase the height of the main window
    self.resize(self.width(), self.originalMainWinHeight+pixels)
