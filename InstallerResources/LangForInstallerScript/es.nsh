; ==============================================================
; Lang\es.nsh — Spanish (Español) UI strings for FLExTrans installer
; ==============================================================

; ---- LangStrings (referenced at runtime as $(Key) for collection tab names) ----
LangString Drafting       ${LANG_SPANISH} "Redacción"
LangString Run_Testbed    ${LANG_SPANISH} "Ejecutar testbed"
LangString Tools          ${LANG_SPANISH} "Herramientas"
LangString Synthesis_Test ${LANG_SPANISH} "Prueba de síntesis"
LangString Clusters       ${LANG_SPANISH} "Racimos"

; ---- Runtime UI strings (assigned to $STR_* variables in SetLanguageCode) ----
!define ES_LANGCODE           "es"
!define ES_CHOOSE_FOLDER      "Elija dónde colocar la carpeta FLExTrans."
!define ES_BROWSE             "Navegar"
!define ES_PROD_LABEL1        "¿Uso en producción?"
!define ES_PROD_LABEL2        "Para instalar una interfaz FLExTrans más sencilla para uso en producción, elija Sí. Para trabajo de desarrollo de FLExTrans, elija No."
!define ES_YES                "Sí"
!define ES_NO                 "No"
!define ES_PYTHON_OLD         "está instalado, pero FLExTrans requiere Python ${PYTHON_MAJOR}.${PYTHON_MINOR}. Al instalar, use la opción 'Install now'.$\n¿Instalar Python ${PYTHON_VERSION} ahora?"
!define ES_INSTALL_PYTHON     "FLExTrans requiere Python ${PYTHON_MAJOR}.${PYTHON_MINOR} para ejecutarse. Se recomienda instalarlo ahora. Al instalar, use la opción 'Install now'.$\n¿Instalar Python ${PYTHON_VERSION}?"
!define ES_INSTALL_XMLMIND    "FLExTrans utiliza XMLmind XML Editor para editar archivos de reglas de transferencia. Se recomienda instalarlo ahora.$\n¿Instalar XMLmind?"
; Display name shown in the LangDLL language-picker dialog
!define ES_DISPLAY_NAME       "Español"
