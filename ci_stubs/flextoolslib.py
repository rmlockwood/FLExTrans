# Minimal stub for flextoolslib used in CI/tests.

class FTConfig:
    UILanguage = 'en'  # Default to English
    
    @staticmethod
    def setUILanguage(lang_code: str):
        FTConfig.UILanguage = lang_code

# Export for convenience
FTM_Name = 'FTM'