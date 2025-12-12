#
#   ClusterUtils
#
#   Ron Lockwood
#   SIL International
#   12/30/2024
#
#   Version 3.14.2 - 8/20/25 - Ron Lockwood
#   Fixes crash in Import Paratext and missing OK button in other dialogs with cluster support.
#
#   Version 3.14.1 - 8/8/25 - Ron Lockwood
#   Fixes #1017. Support cluster projects in TextInOut.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 12/30/2024 - Ron Lockwood
#    Initial version.
#

from ComboBox import CheckableComboBox
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QComboBox, QLayout, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy

IMP_EXP_WINDOW_HEIGHT = 260
IMP_EXP_WINDOW_WIDTH = 626

def initClusterWidgets(self, widgetClass, parentWin, header1TextStr, header2TextStr, comboWidth, specialProcessFunc=None, 
                       originalWinHeight=0, noCancelButton=False, containerWidgetToMove=None):

    self.noCancelButton = noCancelButton
    self.containerWidgetToMove = containerWidgetToMove

    if not self.containerWidgetToMove:
        self.originalOKyPos = self.ui.OKButton.y()
    else:
        self.originalOKyPos = self.containerWidgetToMove.y()

    if originalWinHeight > 0:
        self.originalMainWinHeight = originalWinHeight  
    else:
        self.originalMainWinHeight = IMP_EXP_WINDOW_HEIGHT

    self.widgetList = []
    self.keyWidgetList = []

    use_layout = isinstance(parentWin, QLayout)
    self.clusterUseLayout = use_layout

    # If parent is a layout, create a container widget with a grid layout so headers align with columns
    if use_layout:
        self.clusterContainer = QWidget()
        self.clusterContainer.setVisible(False)
        self.clusterVLayout = QVBoxLayout(self.clusterContainer)
        self.clusterVLayout.setContentsMargins(0, 0, 0, 0)
        self.clusterVLayout.setSpacing(4)
        # Insert the container into the provided parent layout and place it on the right for horizontal layouts
        if isinstance(parentWin, QHBoxLayout):
            parentWin.addStretch()
            parentWin.addWidget(self.clusterContainer)
        else:
            parentWin.addWidget(self.clusterContainer)

        # Create a grid layout so header widgets occupy the same columns as label/key widgets
        self.clusterGrid = QGridLayout()
        self.clusterGrid.setContentsMargins(0, 0, 0, 0)
        self.clusterGrid.setSpacing(6)

        # Header widgets in row 0, columns 0 and 1
        font = QtGui.QFont()
        font.setUnderline(True)

        self.headWidg1 = QLabel()
        self.headWidg1.setObjectName("headerLabel1")
        self.headWidg1.setText(header1TextStr)
        self.headWidg1.setVisible(False)
        self.headWidg1.setFont(font)
        self.headWidg1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.clusterGrid.addWidget(self.headWidg1, 0, 0, alignment=QtCore.Qt.AlignRight)

        self.headWidg2 = QLabel()
        self.headWidg2.setObjectName("headerLabel2")
        self.headWidg2.setText(header2TextStr)
        self.headWidg2.setVisible(False)
        self.headWidg2.setFont(font)
        self.headWidg2.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.clusterGrid.addWidget(self.headWidg2, 0, 1, alignment=QtCore.Qt.AlignLeft)

        # Make column 1 take remaining space so key widgets can expand
        self.clusterGrid.setColumnStretch(0, 0)
        self.clusterGrid.setColumnStretch(1, 1)

        # Add grid to the vertical layout
        self.clusterVLayout.addLayout(self.clusterGrid)

    # Initialize label and ptx combo boxes for all cluster projects
    for x in range(len(self.clusterProjects)):

        # Create the label and widget differently depending on layout usage
        if use_layout:
            labelWidget = QLabel()
            labelWidget.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
            labelWidget.setObjectName(f"label{x}")
            labelWidget.setText(self.clusterProjects[x])
            labelWidget.setVisible(False)

            keyWidget = widgetClass()
            keyWidget.setObjectName(f"widget{x}")
            keyWidget.setVisible(False)
            if comboWidth:
                keyWidget.setFixedWidth(comboWidth)
            else:
                keyWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Add label and key into the grid at row x+1 so headers are in row 0
            self.clusterGrid.addWidget(labelWidget, x + 1, 0, alignment=QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            self.clusterGrid.addWidget(keyWidget, x + 1, 1, alignment=QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        else:
            labelWidget = QLabel(parentWin)
            labelWidget.setGeometry(QtCore.QRect(10, 190, self.ui.clusterProjectsLabel.width(), 21))
            labelWidget.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
            labelWidget.setObjectName(f"label{x}")
            labelWidget.setText(self.clusterProjects[x])
            labelWidget.setVisible(False)

            keyWidget = widgetClass(parentWin) 
            keyWidget.setGeometry(QtCore.QRect(210, 190, comboWidth, 22))
            keyWidget.setObjectName(f"widget{x}")
            keyWidget.setVisible(False)

        # Do special processing
        if specialProcessFunc:
            specialProcessFunc(keyWidget)

        self.widgetList.append((labelWidget, keyWidget))

    # If not using layout, create header widgets in old absolute-position style (kept for compatibility)
    if not use_layout and len(self.clusterProjects) > 0:

        font = QtGui.QFont()
        font.setUnderline(True)
        self.headWidg1 = QLabel(parentWin)
        self.headWidg1.setGeometry(QtCore.QRect(10, 190, self.ui.clusterProjectsLabel.width(), 22))
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
    use_layout = isinstance(parentWin, QLayout)

    # hide the designer widget; we'll reparent/insert it either into a layout or keep geometry
    self.ui.clusterProjectsComboBox.hide()
    # create the new checkable combo as a child of parentWin (or same parent for geometry mode)
    combo_parent = None if use_layout else parentWin
    self.ui.clusterProjectsComboBox = CheckableComboBox(combo_parent)
    self.ui.clusterProjectsComboBox.setObjectName("clusterProjectsComboBox")
    self.ui.clusterProjectsComboBox.addItems([proj for proj in allClusterProjects if proj])

    if use_layout:
        # Put the label and the new combo into a small horizontal row aligned to the right
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        # push the pair to the right
        row_layout.addStretch()

        # Reparent the designer label into the row layout (keeps its text/style)
        self.ui.clusterProjectsLabel.setParent(row_widget)
        row_layout.addWidget(self.ui.clusterProjectsLabel)
        row_layout.addWidget(self.ui.clusterProjectsComboBox)

        # Add the composed row to the parent layout (appears at top/right)
        parentWin.addWidget(row_widget)
    else:
        # Preserve old geometry-based placement for dialogs that are not layout-based
        geom = self.ui.clusterProjectsComboBox.geometry() # same as old control
        self.ui.clusterProjectsComboBox.setGeometry(geom)
        # ensure the designer label keeps its geometry too (no change)
        # (designer label already has its geometry; nothing else to do)
 
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

    # Layout-mode: show/hide widgets in the layouts; Absolute-mode: position with geometry
    if getattr(self, 'clusterUseLayout', False):

        currentList = self.ui.clusterProjectsComboBox.currentData()

        # Show or hide headers
        if len(currentList) > 0:
            self.headWidg1.setVisible(True)
            self.headWidg2.setVisible(True)
            self.topWidget1.setEnabled(False)
            self.topWidget2.setEnabled(False)
            self.clusterContainer.setVisible(True)
        else:
            self.headWidg1.setVisible(False)
            self.headWidg2.setVisible(False)
            self.topWidget1.setEnabled(True)
            self.topWidget2.setEnabled(True)
            self.clusterContainer.setVisible(False)

        # Show/hide each project row
        for i, proj in enumerate(self.clusterProjects):
            if proj in currentList:
                self.widgetList[i][0].setVisible(True)
                self.widgetList[i][1].setVisible(True)
                self.keyWidgetList.append(self.widgetList[i][1])
            else:
                self.widgetList[i][0].setVisible(False)
                self.widgetList[i][1].setVisible(False)

        # When using layouts, do not manually move widgets or resize via geometry.
        # Layout system will manage sizing; if you still need to nudge main window
        # you can call resize or adjustSize from the caller, but keep it optional.

    else:
        # existing absolute-position behavior
        startYpos = self.ui.clusterProjectsComboBox.y() + WIDGET_SIZE_PLUS_SPACE - 10
        comboStartXpos = self.ui.clusterProjectsComboBox.x()
        labelStartXpos = self.ui.clusterProjectsLabel.x()

        # Show the header labels if we have cluster projects selected
        if len(self.ui.clusterProjectsComboBox.currentData()) > 0:

            self.headWidg1.setGeometry(labelStartXpos, startYpos+10, self.headWidg1.width(), self.headWidg1.height())
            self.headWidg1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
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

        currentList = self.ui.clusterProjectsComboBox.currentData()

        # See which new widgets need to be shown
        for i, proj in enumerate(self.clusterProjects):

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
        pixels = len(currentList) * WIDGET_SIZE_PLUS_SPACE

        if pixels > 0:
            pixels += WIDGET_SIZE_PLUS_SPACE

        # Move some widgets down
        widgetsToMove = [
            # self.ui.OKButton,
        ]

        # Include the cancel button for the move if it exists
        if not self.noCancelButton:
            widgetsToMove.append(self.ui.CancelButton) 

        # Include the container widget to move if it exists
        if self.containerWidgetToMove:
            widgetsToMove.append(self.containerWidgetToMove)
        else:
            widgetsToMove.append(self.ui.OKButton)

        for wid in widgetsToMove:
            wid.setGeometry(wid.x(), self.originalOKyPos+pixels, wid.width(), wid.height())

        # Increase the height of the main window
        self.resize(self.width(), self.originalMainWinHeight+pixels)