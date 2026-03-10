#
#   MyTableView
#
#   Ron Lockwood
#   SIL International
#   11/1/2016
#
#   Version 1.0 - 11/1/2016 - Ron
#
#   TableView & CheckBox delegate classes used to show check boxes in the linker table view. 

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QTableView, QStyleOptionButton, QStyledItemDelegate, QStyle, QItemDelegate


class MyTableView(QTableView):
    """
    A simple table to demonstrate the QComboBox delegate.
    """
    def __init__(self, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)
        self.setItemDelegateForColumn(0, CheckBoxDelegate(self))

class CheckBoxDelegate(QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)
        
    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''

        checked = index.data()
        check_box_style_option = QStyleOptionButton()
 
        flags = int(index.flags())
        if (flags & QtCore.Qt.ItemFlag.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly
 
        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off
 
        check_box_style_option.rect = self.getCheckBoxRect(option)
 
        check_box_style_option.state |= QStyle.State_Enabled
 
        QApplication.style().drawControl(QStyle.ControlElement.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        # Do not change the checkbox-state
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            return False
        if event.type() == QtCore.QEvent.Type.MouseButtonRelease or event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
            if event.button() != QtCore.Qt.MouseButton.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
                return True
        elif event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() != QtCore.Qt.Key.Type.Key_Space and event.key() != QtCore.Qt.Key.Type.Key_Select:
                return False
            else:
                return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        #print 'SetModelData'
        newValue = not index.data()
        #print 'New Value : {0}'.format(newValue)
        model.setData(index, newValue, QtCore.Qt.ItemDataRole.EditRole)
        # Crude way to cause repaint
        mn = self.parent().parent()
        mn.setGeometry(mn.x()+1,mn.y()+1,mn.width(),mn.height()+1)
        mn.setGeometry(mn.x()-1,mn.y()-1,mn.width(),mn.height()-1)

    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (option.rect.x() +
                            option.rect.width() // 2 -
                            check_box_rect.width() // 2,
                            option.rect.y() +
                            option.rect.height() // 2 -
                            check_box_rect.height() // 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())

