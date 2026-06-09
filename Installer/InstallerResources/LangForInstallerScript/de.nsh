; ==============================================================
; Lang\de.nsh - German (Deutsch) UI strings for FLExTrans installer
; ==============================================================

; ---- LangStrings (referenced at runtime as $(Key) for collection tab names) ----
LangString Drafting       ${LANG_GERMAN} "Entwerfen"
LangString Run_Testbed    ${LANG_GERMAN} "Tests durchführen"
LangString Tools          ${LANG_GERMAN} "Werkzeuge"
LangString Synthesis_Test ${LANG_GERMAN} "Synthesetest"
LangString Clusters       ${LANG_GERMAN} "Clusters"

; ---- Runtime UI strings (assigned to $STR_* variables in SetLanguageCode) ----
!define DE_LANGCODE           "de"
!define DE_CHOOSE_FOLDER      "Wählen Sie, wo der FLExTrans-Ordner abgelegt werden soll."
!define DE_BROWSE             "Durchsuchen"
!define DE_PROD_LABEL1        "Produktivbetrieb?"
!define DE_PROD_LABEL2        "Um eine einfachere FLExTrans-Oberfläche für den Produktivbetrieb zu installieren, wählen Sie Ja. Für die FLExTrans-Entwicklung wählen Sie Nein."
!define DE_YES                "Ja"
!define DE_NO                 "Nein"
!define DE_PYTHON_OLD         "ist installiert, aber FLExTrans benötigt Python ${PYTHON_MAJOR}.${PYTHON_MINOR}. Verwenden Sie bei der Installation die Option 'Install now'.$\nPython ${PYTHON_VERSION} jetzt installieren?"
!define DE_INSTALL_PYTHON     "FLExTrans benötigt Python ${PYTHON_MAJOR}.${PYTHON_MINOR} zum Ausführen. Es wird empfohlen, es jetzt zu installieren. Verwenden Sie bei der Installation die Option 'Install now'.$\nPython ${PYTHON_VERSION} installieren?"
!define DE_INSTALL_XMLMIND    "FLExTrans verwendet XMLmind XML Editor zum Bearbeiten von Transferregeldateien. Es wird empfohlen, es jetzt zu installieren.$\nXMLmind installieren?"
; Display name shown in the LangDLL language-picker dialog
!define DE_DISPLAY_NAME       "Deutsch"
