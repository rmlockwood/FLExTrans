# Stub for PyQt5.QtWidgets

class QWidget:
    """Mock QWidget base class"""
    def __init__(self, parent=None):
        self.parent_widget = parent

class QApplication(QWidget):
    """Mock QApplication"""
    pass

class QMainWindow(QWidget):
    """Mock QMainWindow"""
    pass

class QMessageBox(QWidget):
    """Mock QMessageBox"""
    @staticmethod
    def information(parent, title, message):
        pass
    
    @staticmethod
    def warning(parent, title, message):
        pass
    
    @staticmethod
    def critical(parent, title, message):
        pass
    
    @staticmethod
    def question(parent, title, message):
        return True

class QCheckBox(QWidget):
    """Mock QCheckBox"""
    pass

class QComboBox(QWidget):
    """Mock QComboBox"""
    pass

class QDialog(QWidget):
    """Mock QDialog"""
    pass

class QInputDialog(QDialog):
    """Mock QInputDialog"""
    @staticmethod
    def getText(parent, title, label):
        return ("", True)

class QFileDialog(QDialog):
    """Mock QFileDialog"""
    @staticmethod
    def getOpenFileName(parent, caption, directory):
        return ("", None)
    
    @staticmethod
    def getExistingDirectory(parent, caption, directory):
        return ""

class QFontDialog(QDialog):
    """Mock QFontDialog"""
    pass

class QAbstractItemView(QWidget):
    """Mock QAbstractItemView"""
    pass

class QListWidget(QAbstractItemView):
    """Mock QListWidget"""
    pass

class QPushButton(QWidget):
    """Mock QPushButton"""
    pass

class QLabel(QWidget):
    """Mock QLabel"""
    pass

class QLineEdit(QWidget):
    """Mock QLineEdit"""
    pass

class QCompleter:
    """Mock QCompleter"""
    pass

class QLayout:
    """Mock QLayout base class"""
    pass

class QVBoxLayout(QLayout):
    """Mock QVBoxLayout"""
    pass

class QHBoxLayout(QLayout):
    """Mock QHBoxLayout"""
    pass

class QDialogButtonBox(QWidget):
    """Mock QDialogButtonBox"""
    pass

class QToolTip:
    """Mock QToolTip"""
    pass

class QStyledItemDelegate:
    """Mock QStyledItemDelegate"""
    pass

class QGridLayout(QLayout):
    """Mock QGridLayout"""
    pass

class QSizePolicy:
    """Mock QSizePolicy"""
    def __init__(self, horizontal=None, vertical=None):
        pass
