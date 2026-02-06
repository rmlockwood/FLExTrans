# Minimal stub for flextoolslib used in CI/tests.

class FTConfig:
    UILanguage = 'en'  # Default to English
    
    @staticmethod
    def setUILanguage(lang_code: str):
        FTConfig.UILanguage = lang_code

class FlexToolsModuleClass:
    """Mock FlexToolsModuleClass - base class for FlexTools modules"""
    def __init__(self, runFunction=None, docs=None):
        self.runFunction = runFunction
        self.docs = docs or {}
    
    def Help(self):
        """Mock Help method - prints documentation"""
        if self.docs:
            print(self.docs)

# Export constants for convenience
FTM_Name = 'FTM_Name'
FTM_Version = 'FTM_Version'
FTM_ModifiesDB = 'FTM_ModifiesDB'
FTM_Synopsis = 'FTM_Synopsis'
FTM_Help = 'FTM_Help'
FTM_Description = 'FTM_Description'