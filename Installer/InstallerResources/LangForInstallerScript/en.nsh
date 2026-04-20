; ==============================================================
; Lang\en.nsh — English UI strings for FLExTrans installer
;
; HOW TO ADD A NEW LANGUAGE:
;   1. Copy this file to Lang\XX.nsh  (XX = ISO 639-1 code, e.g. "pt")
;   2. Change every EN_ prefix to XX_  (e.g. PT_)
;   3. Translate every string value
;   4. Follow the remaining steps listed in FLExTrans-installer.nsi
; ==============================================================

; ---- LangStrings (referenced at runtime as $(Key) for collection tab names) ----
LangString Drafting       ${LANG_ENGLISH} "Drafting"
LangString Run_Testbed    ${LANG_ENGLISH} "Run Testbed"
LangString Tools          ${LANG_ENGLISH} "Tools"
LangString Synthesis_Test ${LANG_ENGLISH} "Synthesis Test"
LangString Clusters       ${LANG_ENGLISH} "Clusters"

; ---- Runtime UI strings (assigned to $STR_* variables in SetLanguageCode) ----
!define EN_LANGCODE           "en"
!define EN_CHOOSE_FOLDER      "Choose where to put FLExTrans folder."
!define EN_BROWSE             "Browse"
!define EN_PROD_LABEL1        "Production use?"
!define EN_PROD_LABEL2        "To install a simpler FLExTrans interface for production use, choose 'Yes'. For FLExTrans development work choose 'No'."
!define EN_YES                "Yes"
!define EN_NO                 "No"
!define EN_PYTHON_OLD         "is installed, but FLExTrans requires Python ${PYTHON_MAJOR}.${PYTHON_MINOR}. When installing, use the 'Install now' option.$\nInstall Python ${PYTHON_VERSION} now?"
!define EN_INSTALL_PYTHON     "FLExTrans requires Python ${PYTHON_MAJOR}.${PYTHON_MINOR} to run. It is recommended that you install it now. When installing, use the 'Install now' option.$\nInstall Python ${PYTHON_VERSION}?"
!define EN_INSTALL_XMLMIND    "FLExTrans relies on XMLmind XML Editor for editing transfer rule files. It is recommended that you install it now.$\nInstall XMLmind?"
; Display name shown in the LangDLL language-picker dialog
!define EN_DISPLAY_NAME       "English"
