# Minimal stub for PyQt5.QtCore used in CI/tests.

class QObject:
    """Mock QObject base class"""
    pass

class QCoreApplication(QObject):
    @staticmethod
    def translate(context: str, text: str) -> str:
        # Return the untranslated text (CI/tests expect a no-op).
        return text

    @staticmethod
    def installTranslator(translator):
        # No-op for CI/tests
        pass

class QApplication(QObject):
    """Mock QApplication"""
    pass

class QTranslator(QObject):
    def load(self, filename: str, path: str = "") -> bool:
        # Return False (no translation file found) - acceptable for CI/tests
        return False

class QLibraryInfo:
    TranslationsPath = 0
    
    @staticmethod
    def location(path_type: int) -> str:
        # Return empty string for translations path
        return ""

class QLocale:
    # Common language/country codes
    German = 6
    Germany = 86
    
    def __init__(self, lang=None):
        pass

class QTimer(QObject):
    """Mock QTimer"""
    pass

class QDateTime:
    """Mock QDateTime"""
    @staticmethod
    def currentDateTime():
        return QDateTime()

class Qt:
    """Mock Qt namespace with common flags"""
    class AlignmentFlag:
        pass
    Spanish = 28
    Spain = 214
    English = 29
    UnitedStates = 225

class QEvent:
    """Mock QEvent class"""
    pass

def pyqtSignal(*args, **kwargs):
    """Mock pyqtSignal decorator - no-op for CI/tests"""
    def decorator(func):
        return func
    return decorator
    
    def __init__(self, language=None, country=None):
        self.language = language
        self.country = country
    
    def toString(self, datetime_obj, format_str: str = "d MMM yyyy hh:mm:ss") -> str:
        # Simple string representation for tests
        return str(datetime_obj)