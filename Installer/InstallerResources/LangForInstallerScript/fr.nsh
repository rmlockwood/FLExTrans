; ==============================================================
; Lang\fr.nsh — French (Français) UI strings for FLExTrans installer
; ==============================================================

; ---- LangStrings (referenced at runtime as $(Key) for collection tab names) ----
LangString Drafting       ${LANG_FRENCH} "Rédaction"
LangString Run_Testbed    ${LANG_FRENCH} "Lancer le banc d`essai"
LangString Tools          ${LANG_FRENCH} "Outils"
LangString Synthesis_Test ${LANG_FRENCH} "Test de synthèse"
LangString Clusters       ${LANG_FRENCH} "Grappes"

; ---- Runtime UI strings (assigned to $STR_* variables in SetLanguageCode) ----
!define FR_LANGCODE           "fr"
!define FR_CHOOSE_FOLDER      "Choisissez l'emplacement du dossier FLExTrans."
!define FR_BROWSE             "Parcourir"
!define FR_PROD_LABEL1        "Utilisation en production?"
!define FR_PROD_LABEL2        "Pour installer une interface FLExTrans simplifiée destinée à une utilisation en production, choisissez Oui. Pour les travaux de développement sur FLExTrans, choisissez Non."
!define FR_YES                "Oui"
!define FR_NO                 "Non"
!define FR_PYTHON_OLD         "est installé, mais FLExTrans nécessite Python ${PYTHON_MAJOR}.${PYTHON_MINOR}. Lors de l'installation, utilisez l'option 'Install now'$\nInstaller Python ${PYTHON_VERSION} maintenant?"
!define FR_INSTALL_PYTHON     "FLExTrans nécessite Python ${PYTHON_MAJOR}.${PYTHON_MINOR} pour fonctionner. Il est recommandé de l'installer maintenant. Lors de l'installation, utilisez l'option 'Install now'.$\nInstaller Python ${PYTHON_VERSION}?"
!define FR_INSTALL_XMLMIND    "FLExTrans utilise XMLmind XML Editor pour éditer les fichiers de règles de transfert. Il est recommandé de l'installer maintenant.$\nInstaller XMLmind?"
; Display name shown in the LangDLL language-picker dialog
!define FR_DISPLAY_NAME       "Français"
