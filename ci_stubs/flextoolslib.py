# Minimal stub for flextoolslib used in CI/tests.

class FTConfig:
    UILanguage = 'en'  # Default to English
    
    @staticmethod
    def setUILanguage(lang_code: str):
        FTConfig.UILanguage = lang_code

class FlexToolsModuleClass:
    """Mock FlexToolsModuleClass - base class for FlexTools modules"""
    def __init__(self):
        pass

# Export for convenience
FTM_Name = 'FTM'