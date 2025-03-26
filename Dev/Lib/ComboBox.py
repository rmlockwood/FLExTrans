#
#   CheckableComboBox
#
#   Lærke Roager Christensen
#   6/30/22
#
#   Version 3.12.1 - 1/15/25 - Ron Lockwood
#    Export from FLEx to Paratext, optionally across cluster projects.
#
#   Version 3.12 - 12/24/24 - Ron Lockwood
#    Add signal for when an item is checked.
#
#   Version 3.9.1 - 9/4/23 - Ron Lockwood
#    Fixes #466. Disable wheel scrolling.
#
#   Version 3.6 - 10/21/22 - Ron Lockwood
#   Fixes #236 Added Close and Apply/Close buttons. Detect Check Combo Box changes.
#
#   Version 3.5.1 - 7/1/22 - Ron Lockwood
#    Undo color change to lineEdit part
#
#   This is a custom ComboBox where you can select multiple items on a list.
#   Used in the Settings Tool.
#   The code is found on: https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
#   with some modifications made by Lærke.

from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate
from PyQt5.QtGui import QStandardItem, QFontMetrics
from PyQt5.QtCore import QEvent, Qt, pyqtSignal

class CheckableComboBox(QComboBox):

    # Define a custom signal
    itemCheckedStateChanged = pyqtSignal(int)

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(29)
            size.setWidth(436)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Needed to use wheelEvent method below to disable wheel scrolling
        self.setFocusPolicy(Qt.StrongFocus)

        self.modified = False

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())


        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
            
                # Emit the custom signal when an item is checked/unchecked
                self.itemCheckedStateChanged.emit(index.row())
                return True

        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

        # Assume if the user pop's up the list, they changed something
        self.modified = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def check(self, text):
        for i in range(self.model().rowCount()):
            if self.model().item(i).text() == text:
                self.model().item(i).setCheckState(Qt.Checked)

    def unCheck(self, text):
        for i in range(self.model().rowCount()):
            if self.model().item(i).text() == text:
                self.model().item(i).setCheckState(Qt.Unchecked)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        texts.sort()
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).text())
        return res
    
    def wheelEvent(self, *args, **kwargs):
        # Disable wheel scrolling. This prevents inadvertent changes.
        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)
        else:
            return    