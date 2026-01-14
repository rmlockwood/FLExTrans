!include "StrRep.nsh"
#!include "ReplaceInFile.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "LangFile.nsh"


; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "FLExTrans"
!define PRODUCT_PUBLISHER "SIL International"
!define PRODUCT_WEB_SITE "https://software.sil.org/flextrans"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_VERSION "3.14"
!define PRODUCT_ZIP_FILE "FLExToolsWithFLExTrans${PRODUCT_VERSION}.zip"
!define ADD_ON_ZIP_FILE "AddOnsForXMLmind${PRODUCT_VERSION}.zip"
!define HERMIT_CRAB_ZIP_FILE "HermitCrabTools${PRODUCT_VERSION}.zip"
!define FLEXTRANS_FOLDER "FLExTrans"
!define WORKPROJECTSDIR "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects"
!define TEMPLATEDIR "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject"
!define RULEASSISTANT "FLExTrans.Rule Assistant"
!define REPLACEMENTEDITOR "FLExTrans.Replacement Dictionary Editor"
!define TEXTIN "FLExTrans.Text In Rules"
!define TEXTOUT "FLExTrans.Text Out Rules"
!define EXPORTFROMFLEX "FLExTrans.Export Text from Target FLEx to Paratext"

; MUI 1.67 compatible ------
!include "MUI.nsh"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" ""
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalTrademarks" ""
VIAddVersionKey "LegalCopyright" "? 2015-2025 SIL International"
VIAddVersionKey "FileDescription" ""
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"

; Always 4 numerals
VIProductVersion 3.14.0.${BUILD_NUM}

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; Directory page
Page custom nsDialogsPage

; Production mode radio buttons (Yes or No)
Page custom ProdModeDialog ProdModeDlgLeave ; Link the custom page with ProdModeDlgLeave

!include nsDialogs.nsh
Var Dialog
Var Label
Var RadioYes
Var RadioNo
Var /GLOBAL PRODUCTION_MODE
Var /GLOBAL LANGCODE

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"

#!macro _ReplaceInFile SOURCE_FILE SEARCH_TEXT REPLACEMENT
#  Push "${SOURCE_FILE}"
#  Push "${SEARCH_TEXT}"
#  Push "${REPLACEMENT}"
#  Call RIF
#!macroend

; Define a macro for copying transfer rules files based on language
!macro InstallLocalizedRulesFile DEST_NAME SRC_BASE
    ${If} $LANGUAGE == ${LANG_GERMAN}
        File /oname=${DEST_NAME} "${GIT_FOLDER}\${SRC_BASE}_de.t1x"
    ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
        File /oname=${DEST_NAME} "${GIT_FOLDER}\${SRC_BASE}_es.t1x"
    ${Else}
        File /oname=${DEST_NAME} "${GIT_FOLDER}\${SRC_BASE}.t1x"
    ${EndIf}
!macroend

; MUI end ------
Icon "${GIT_FOLDER}\Tools\FLExTransWindowIcon.ico"
Name "${PRODUCT_NAME}"

OutFile "${PRODUCT_NAME}${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\FLExTrans_Installer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

# Set up variables to hold installation messages in different UI languages
LangString InstallPythonMsg ${LANG_ENGLISH} "Install Python 3.11.7?$\nIMPORTANT! Check the box: 'Add Python 3.11 to Path'.$\nUse the 'Install now' option"
LangString InstallPythonMsg ${LANG_GERMAN} "Python 3.11.7 installieren?$\nWICHTIG! Aktivieren Sie das Kontrollkästchen: 'Add Python 3.11 to Path'.$\nVerwenden Sie die Option 'Install now'."
LangString InstallPythonMsg ${LANG_SPANISH} "¿Instalar Python 3.11.7?$\n¡IMPORTANTE! Marque la casilla: 'Add Python 3.11 to Path'.$\nUse la opción 'Install now'."
LangString InstallXMLmindMsg ${LANG_ENGLISH} "Install XMLmind?"
LangString InstallXMLmindMsg ${LANG_GERMAN} "XMLmind installieren?"
LangString InstallXMLmindMsg ${LANG_SPANISH} "¿Instalar XMLmind?"

# English
LangString Drafting       ${LANG_ENGLISH} "Drafting"
LangString Run_Testbed    ${LANG_ENGLISH} "Run Testbed"
LangString Tools          ${LANG_ENGLISH} "Tools"
LangString Synthesis_Test ${LANG_ENGLISH} "Synthesis Test"
LangString Clusters       ${LANG_ENGLISH} "Clusters"

# German
LangString Drafting       ${LANG_GERMAN} "Entwerfen"
LangString Run_Testbed    ${LANG_GERMAN} "Tests durchführen"
LangString Tools          ${LANG_GERMAN} "Werkzeuge"
LangString Synthesis_Test ${LANG_GERMAN} "Synthesetest"
LangString Clusters       ${LANG_GERMAN} "Clusters"

# Spanish
LangString Drafting       ${LANG_SPANISH} "Redacción"
LangString Run_Testbed    ${LANG_SPANISH} "Ejecutar testbed"
LangString Tools          ${LANG_SPANISH} "Herramientas"
LangString Synthesis_Test ${LANG_SPANISH} "Prueba de síntesis"
LangString Clusters       ${LANG_SPANISH} "Racimos"

Section -Prerequisites
InitPluginsDir

  SetOutPath "$INSTDIR\install_files"

  # Install python 
  MessageBox MB_YESNO "$(InstallPythonMsg)" /SD IDYES IDNO endPythonSync
        File "${RESOURCE_FOLDER}\python-3.11.7-amd64.exe"
        ExecWait "$INSTDIR\install_files\python-3.11.7-amd64.exe PrependPath=1"
        Goto endPythonSync
  endPythonSync:
  
  Var /GLOBAL OUT_FOLDER
  # Unzip FLExTrans to the desired folder
  # GIT_FOLDER needs to be set to your local git FLExTrans folder in the compiler settings
  File "${GIT_FOLDER}\${PRODUCT_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${PRODUCT_ZIP_FILE}" "$OUT_FOLDER"

  # Create empty Output folders
  CreateDirectory "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\Output"
  CreateDirectory "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\Output"
  
  ## Copy files only if they don't already exist. These are files users may change.
  SetOverwrite off
  
  # Replacement dictionary  
  ; German-Swedish project folder
  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\Output"
  File "${GIT_FOLDER}\replace.dix"

  ; template project folder
  SetOutPath "${TEMPLATEDIR}\Output"
  File "${GIT_FOLDER}\replace.dix"
    
# Transfer rule files for German-Swedish folder
SetOutPath "${WORKPROJECTSDIR}\German-Swedish"
; Pass the file name that it should be called in the destination folder and the starting part of the original filename in GIT (without _de, etc.)
!insertmacro InstallLocalizedRulesFile "transfer_rules-Swedish.t1x" "transfer_rules-Swedish"

# Transfer rule files for TemplateProject folder
SetOutPath "${WORKPROJECTSDIR}\TemplateProject"
; Pass the file name that it should be called in the destination folder and the starting part of the original filename in GIT (without _de, etc.)
!insertmacro InstallLocalizedRulesFile "transfer_rules.t1x" "transfer_rules-Swedish"
!insertmacro InstallLocalizedRulesFile "transfer_rules-Sample1.t1x" "transfer_rules-Sample1"
    
;old
  # Transfer rule files for each language.
  ; First copy them to the install folder
;  SetOutPath "$INSTDIR\install_files"
;  File "${GIT_FOLDER}\transfer_rules-Swedish.t1x"
;  File "${GIT_FOLDER}\transfer_rules-Swedish_de.t1x"
;  File "${GIT_FOLDER}\transfer_rules-Swedish_es.t1x"
;  ${If} $LANGUAGE == ${LANG_GERMAN}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish_de.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\transfer_rules-Swedish.t1x"
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish_de.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules.t1x"
;  ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish_es.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\transfer_rules-Swedish.t1x"
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish_es.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules.t1x"
;  ${Else}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish"
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Swedish.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules.t1x"
;  ${EndIf}
  
  # Sample transfer rule files for each language.
  ; First copy them to the install folder
;  SetOutPath "$INSTDIR\install_files"
;  File "${GIT_FOLDER}\transfer_rules-Sample1.t1x"
;  File "${GIT_FOLDER}\transfer_rules-Sample1_de.t1x"
;  File "${GIT_FOLDER}\transfer_rules-Sample1_es.t1x"
  
  ; Then copy them to the right name, depending on install language. We only copy the sample rules file to the template project folder.
;  ${If} $LANGUAGE == ${LANG_GERMAN}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Sample1_de.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules-Sample1.t1x"
;  ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Sample1_es.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules-Sample1.t1x"
;  ${Else}
;    CopyFiles "$INSTDIR\install_files\transfer_rules-Sample1.t1x" "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\transfer_rules-Sample1.t1x"
;  ${EndIf}

  ## Now we overwrite the following files.
  SetOverwrite on
  
  # Find where FLEx is installed
  ReadRegStr $0 HKLM Software\WOW6432Node\SIL\FieldWorks\9 "RootCodeDir"
  
  # Unzip the HermitCrab files in the FLEx programs folder
  SetOutPath "$INSTDIR\install_files"
  File "${GIT_FOLDER}\${HERMIT_CRAB_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${HERMIT_CRAB_ZIP_FILE}" "$0"

  # Delete SettingGui.py from the Modules\FLExTrans folder, it now lives right under FlexTools
  Delete "$OUT_FOLDER\${FLEXTRANS_FOLDER}\FlexTools\Modules\FLExTrans\SettingsGUI.py"

  # Delete FTPaths.py from the FlexTools folder (for old installs), otherwise it inteferes with the one in Modules\FLExTrans\Lib
  Delete "$OUT_FOLDER\${FLEXTRANS_FOLDER}\FlexTools\FTPaths.py"
  
  # Fix up ini files, both collection ones and flextools.ini in all work project folders
  SetOutPath ${WORKPROJECTSDIR}
  FindFirst $0 $1 "${WORKPROJECTSDIR}\*.*"
  loop1:
    StrCmp $1 "" done1
    StrCmp $1 "." nextfolder
    StrCmp $1 ".." nextfolder
    
    # Get two values from flextools.ini to save for later after the new .ini file is installed.
    ReadIniStr $8 "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentproject"
    ReadIniStr $9 "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentcollection"

    # If currentcollection is set to FLExTrans (likely from a previous install in production mode) change it to Tools
    # Otherwise a developer-type user will get this collection added as a tab.
    ${If} $9 == "FLExTrans"
      StrCpy $9 "Tools"
    ${EndIf}

    # Overwrite FLExTrans.vbs
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\*.*"
       ; Delete a old FlexTools.vbs file if it exists
       ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\FlexTools.vbs"
          Delete "${WORKPROJECTSDIR}\$1\FlexTools.vbs"
      ${EndIf}
      SetOutPath "${WORKPROJECTSDIR}\$1"
      File "${GIT_FOLDER}\FLExTrans.vbs"
    ${EndIf}
    
    # Overwrite flextools.ini
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Config\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Config"
      
      # Use a production mode ini file if the user chose that
      ${If} $PRODUCTION_MODE <> ${BST_UNCHECKED}
        File "/oname=${WORKPROJECTSDIR}\$1\Config\flextools.ini" "${GIT_FOLDER}\flextools_basic.ini"
      ${Else}
        File "${GIT_FOLDER}\flextools.ini"
      ${EndIf}
    ${EndIf}
    
	# Overwrite FLExTrans.ini - the production mode collection
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Config\Collections\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Config\Collections"
      File "${GIT_FOLDER}\FLExTrans.ini"
    ${EndIf}
	
	# Overwrite Makefiles
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Build\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Build"
      File "${GIT_FOLDER}\Makefile"
      File "${GIT_FOLDER}\Makefile.advanced"
    ${EndIf}
	
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Build\LiveRuleTester"
      File "/oname=${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\Makefile" "${GIT_FOLDER}\MakefileForLiveRuleTester"
      File "/oname=${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\Makefile.advanced" "${GIT_FOLDER}\MakefileForLiveRuleTester.advanced"
    ${EndIf}
	
    # Replace the default currentproject and currentcollection values with what we read above
    StrCmp $8 "" skip
    # We use WriteINIStr instead of _ReplaceInFile for better non-admin compatibility
    WriteINIStr "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentproject" "'$8'"
    WriteINIStr "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentcollection" "'$9'"
#    !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "currentproject = 'German-FLExTrans-Sample'" "currentproject = '$8'"
#    !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "currentcollection = 'Drafting'" "currentcollection = '$9'"
			
    # Find all collection ini files (e.g. tools.ini)
    skip:
    FindFirst $3 $4 "${WORKPROJECTSDIR}\$1\Config\Collections\*.ini"
    loop2:
      StrCmp $4 "" done2
      ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Config\Collections\$4"
      
		# If the Tools collection doesn't have disablerunall set yet, set it to True
		${If} $4 == "Tools.ini" 
		
			# Get the current disablerunall setting
			ReadIniStr $5 "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "DEFAULT" "disablerunall"
			
			# If we have no value, set disablerunall to True
			StrCmp $5 "" 0 skip3
		
				WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "DEFAULT" "disablerunall" "True"

			skip3:      
		${EndIf}
      ${EndIf}
      FindNext $3 $4
      Goto loop2
    done2:
      FindClose $3
    nextfolder:  
    FindNext $0 $1
    Goto loop1
  done1:
    FindClose $0
  
  # if we are installing for the same language that is already there, skip adding/renaming files for the language
  ${If} $LANGUAGE == ${LANG_GERMAN}
  
    ${If} ${FileExists} "${WORKPROJECTSDIR}\German-Swedish\Config\Collections\Werkzeuge.ini"
	
	  Goto skip4
    ${EndIf}
  ${EndIf}
	
  ${If} $LANGUAGE == ${LANG_SPANISH}
  
    ${If} ${FileExists} "${WORKPROJECTSDIR}\German-Swedish\Config\Collections\Herramientas.ini"
	
	  Goto skip4
    ${EndIf}
  ${EndIf}
	
  # Install the collection .ini files if they don't exist already.
  SetOverwrite off

  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\Config\Collections"
  File "${GIT_FOLDER}\Drafting.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"
  File "${GIT_FOLDER}\Synthesis Test.ini"
  File "${GIT_FOLDER}\FLExTrans.ini"
  File "${GIT_FOLDER}\Clusters.ini"

  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\Config\Collections"
  File "${GIT_FOLDER}\Drafting.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"
  File "${GIT_FOLDER}\Synthesis Test.ini"
  File "${GIT_FOLDER}\FLExTrans.ini"
  File "${GIT_FOLDER}\Clusters.ini"

  skip4:
  
  SetOverwrite on

  # If we are not installing for English, rename the .ini files appropriately.
  # We are only supporting renaming from English to something else. For other situations they must delete their .ini files
  ${If} $LANGUAGE != ${LANG_ENGLISH}
  
    # Fix up ini files, for UI language chosen
    SetOutPath ${WORKPROJECTSDIR}
    FindFirst $0 $1 "${WORKPROJECTSDIR}\*.*"
    loop8:
      StrCmp $1 "" done8
      StrCmp $1 "." nextfolder8
      StrCmp $1 ".." nextfolder8
        
      # Replace collection names that are in collectiontabs (or current) with the language equivalent
      ${If} $LANGUAGE != ${LANG_ENGLISH}

		; 1. Define the file path
		StrCpy $R0 "${WORKPROJECTSDIR}\$1\Config\flextools.ini"

		; 2. Read the current list from the INI
		; Format: ['Drafting', 'Run Testbed', 'Tools']
		ReadINIStr $R1 "$R0" "DEFAULT" "collectiontabs"

		; If the key doesn't exist, $R1 will be empty. 
		StrCmp $R1 "" done4

		# 3. Perform replacements using the macro 
		${StrRep} $R1 "$R1" "Drafting" "$(Drafting)"
		${StrRep} $R1 "$R1" "Run Testbed" "$(Run_Testbed)"
		${StrRep} $R1 "$R1" "Tools" "$(Tools)"
		${StrRep} $R1 "$R1" "Synthesis Test" "$(Synthesis_Test)"
		${StrRep} $R1 "$R1" "Clusters" "$(Clusters)"

		; 4. Write the final modified string back to the file
		WriteINIStr "$R0" "DEFAULT" "collectiontabs" "$R1"

		done4:

 #       !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "Drafting" "$(Drafting)"
 #       !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "Run Testbed" "$(Run_Testbed)"
 #       !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "'Tools'" "'$(Tools)'"  # replace 'Tools' so we don't mistakenly match FlexTools
 #       !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "Synthesis Test" "$(Synthesis_Test)"
 #       !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "Clusters" "$(Clusters)"
      ${EndIf}
      
	  # Change the interface language setting
	  WriteINIStr "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "uilanguage" "'$LANGCODE'"
	  
      # Renaming
      SetOutPath "${WORKPROJECTSDIR}\$1\Config\Collections"

      StrCpy $R0 "$(Drafting)"
      Rename "$OUTDIR\Drafting.ini" "$OUTDIR\$R0.ini" 
      StrCpy $R0 "$(Run_Testbed)"
      Rename "$OUTDIR\Run Testbed.ini" "$OUTDIR\$R0.ini" 
      StrCpy $R0 "$(Tools)"
      Rename "$OUTDIR\Tools.ini" "$OUTDIR\$R0.ini" 
      StrCpy $R0 "$(Synthesis_Test)"
      Rename "$OUTDIR\Synthesis Test.ini" "$OUTDIR\$R0.ini" 
      StrCpy $R0 "$(Clusters)"
      Rename "$OUTDIR\Clusters.ini" "$OUTDIR\$R0.ini" 

      nextfolder8:  
      FindNext $0 $1
      Goto loop8
    done8:
      FindClose $0

  ${EndIf}

  # Set the folder permission to be writable by all in the Users group
  # old that didn't seem to work as reported in issue 1125:      nsExec::Exec '"icacls" "$OUT_FOLDER\${FLEXTRANS_FOLDER}" /grant *S-1-1-0:(OI)(CI)(M) /T /C'
  # version that purported to fix 1125 had 'grant Users', but 'grant "Authenticated Users"' includes 'Users' and is a system managed group
  #nsExec::Exec '"icacls" "$OUT_FOLDER\${FLEXTRANS_FOLDER}" /grant "Authenticated Users":(OI)(CI)(M) /T /C'
  nsExec::Exec '"icacls" "$OUT_FOLDER\${FLEXTRANS_FOLDER}" /grant *S-1-5-11:(OI)(CI)(M) /T /C'
  
  # Attempt to run pip to install FlexTools dependencies
  !define mycmd '"$LocalAppdata\Programs\Python\Python311\python.exe" -m pip install -r "$OUT_FOLDER\${FLEXTRANS_FOLDER}\requirements.txt"'
  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}"
  File "${GIT_FOLDER}\Command.bat"
  # assume pip3 got installed in the default folder under %appdata%. If it did pip will run successfully the first time it gets installed.
  ExecWait '${mycmd}'
  # if the above failed, call the command.bat to do the same thing, but if this was the first time run, pip won't be in the path.
  IfErrors 0 +2
        Exec '"$OUT_FOLDER\${FLEXTRANS_FOLDER}\Command.bat"'

  # Install Rule Assistant in silent mode
  SetOutPath "$INSTDIR\install_files"
  File "${RESOURCE_FOLDER}\FLExTransRuleAssistant-setup.exe"
  ExecWait "$INSTDIR\install_files\FLExTransRuleAssistant-setup.exe /SILENT"
  
  SetOutPath "$INSTDIR\install_files"
  MessageBox MB_YESNO "$(InstallXMLmindMsg)" /SD IDYES IDNO endXXeSync 
        File "${RESOURCE_FOLDER}\xxe-perso-8_2_0-setup.exe"
        ExecWait "$INSTDIR\install_files\xxe-perso-8_2_0-setup.exe /SILENT"
        Goto endXXeSync
  endXXeSync:
    
  # Associate file extensions with XMLmind XML Editor
  
  # Start extension association loop
  StrCpy $R1 ".t1x"
  Goto associate_extension
  
next_t2x:
  StrCpy $R1 ".t2x"
  Goto associate_extension
  
next_t3x:
  StrCpy $R1 ".t3x"
  Goto associate_extension
  
next_dix:
  StrCpy $R1 ".dix"
  Goto associate_extension
  
associate_extension:
  # Create OpenWithList entry
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithList" "a" "xxe.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithList" "MRUList" "a"
  
  # Create OpenWithProgids entry
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithProgids" "XXE_XML_File" ""
  
  # Check which extension we just processed and jump to next one
  ${If} $R1 == ".t1x"
    Goto next_t2x
  ${ElseIf} $R1 == ".t2x"
    Goto next_t3x
  ${ElseIf} $R1 == ".t3x"
    Goto next_dix
  ${EndIf}
  
  # Notify Windows of the change
  System::Call 'Shell32::SHChangeNotify(i 0x8000000, i 0, i 0, i 0)'


  # Retrieve all the XXE addons, including the language specific ones
  File "${GIT_FOLDER}\${ADD_ON_ZIP_FILE}"
  File "${GIT_FOLDER}\AddOnsForXMLmind_de${PRODUCT_VERSION}.zip"
  File "${GIT_FOLDER}\AddOnsForXMLmind_es${PRODUCT_VERSION}.zip"
  
  # Install the English one first
  nsisunz::Unzip "$INSTDIR\install_files\${ADD_ON_ZIP_FILE}" "$APPDATA\XMLmind\XMLEditor8\addon"
  
  # Now overwrite some of the files with the Language specific ones
  ${If} $LANGUAGE == ${LANG_GERMAN}
    nsisunz::Unzip "$INSTDIR\install_files\AddOnsForXMLmind_de${PRODUCT_VERSION}.zip" "$APPDATA\XMLmind\XMLEditor8\addon"
  ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
    nsisunz::Unzip "$INSTDIR\install_files\AddOnsForXMLmind_es${PRODUCT_VERSION}.zip" "$APPDATA\XMLmind\XMLEditor8\addon"
  ${EndIf}
  
  # Update the XXE properties file
  # Define paths
  StrCpy $R0 "$APPDATA\XMLmind\XMLEditor8\preferences.properties"
  StrCpy $R1 "$APPDATA\XMLmind\XMLEditor8\prefs_temp.properties"

  ${If} ${FileExists} "$R0"
    FileOpen $R2 "$R0" "r"               ; Open original for reading
    FileOpen $R3 $R1 "w"                 ; Open temp for writing
    
    loop_lines:
      FileRead $R2 $R4                   ; Read one line (up to 1024 chars)
      IfErrors done_lines
      
      # Check if this line contains our target string
      # If so, replace it using the macro
      ${StrRep} $R4 "$R4" "autoCheckForUpdates=true" "autoCheckForUpdates=false"
      
      FileWrite $R3 "$R4"                ; Write the (potentially modified) line
      Goto loop_lines

    done_lines:
    FileClose $R3
    FileClose $R2

    # Copy the temp file back to the original location
    # This is safer than 'Rename' for non-admins as it only requires Write permission
    CopyFiles /SILENT "$R1" "$R0"
    Delete "$R1"
  ${EndIf}
#  !insertmacro _ReplaceInFile "$APPDATA\XMLmind\XMLEditor8\preferences.properties" "autoCheckForUpdates=true" "autoCheckForUpdates=false"

  # Remove the install_files folder
  RMDir /r "$INSTDIR\install_files"
SectionEnd


Section "MainSection" SEC01

SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${FLEXTRANS_FOLDER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
#Take a look here and make sure that you uninstall XXE, ask about git, python and the FLExTools folder.
  Delete "$INSTDIR\uninst.exe"
  MessageBox MB_YESNO "Delete the ${FLEXTRANS_FOLDER} folder?" /SD IDYES IDNO endFlexDel
        RMDir /r "$DOCUMENTS\${FLEXTRANS_FOLDER}"
        Goto endFlexDel
  endFlexDel:

  # Not sure what this does - RL 10Jan2022
  Delete "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Uninstall.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Website.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}${PRODUCT_VERSION}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\${PRODUCT_NAME}${PRODUCT_VERSION}.lnk"

  RMDir "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}"
  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

# Define the string in each language
LangString ChooseFolderText ${LANG_ENGLISH} "Choose where to put FLExTrans folder."
LangString ChooseFolderText ${LANG_GERMAN} "Wählen Sie, wo der FLExTrans-Ordner abgelegt werden soll."
LangString ChooseFolderText ${LANG_SPANISH} "Elija dónde colocar la carpeta FLExTrans."
LangString BrowseText ${LANG_ENGLISH} "Browse"
LangString BrowseText ${LANG_GERMAN} "Durchsuchen"
LangString BrowseText ${LANG_SPANISH} "Navegar"

#--Select folder function
!include nsDialogs.nsh
var /global BROWSEDEST
var /global DESTTEXT
;Var Dialog
Function nsDialogsPage

        #Create Dialog and quit if error
        nsDialogs::Create 1018
        Pop $Dialog
        ${If} $Dialog == error
                Abort
        ${EndIf}
        
        StrCpy $OUT_FOLDER $DOCUMENTS

        ${NSD_CreateLabel} 0 60 100% 12u "$(ChooseFolderText)"
        ${NSD_CreateText} 0 80 70% 12u "$OUT_FOLDER"
        pop $DESTTEXT
        SendMessage $DESTTEXT ${EM_SETREADONLY} 1 0
        ${NSD_CreateBrowseButton} 320 80 20% 12u "$(BrowseText)"
        pop $BROWSEDEST

        ${NSD_OnClick} $BROWSEDEST Browsedest

nsDialogs::Show
FunctionEnd

# Set up the Browse step
Function Browsedest
nsDialogs::SelectFolderDialog "Select Destination Folder" $DOCUMENTS
Pop $OUT_FOLDER
${NSD_SetText} $DESTTEXT $OUT_FOLDER
FunctionEnd

LangString ProdModeLabelText1 ${LANG_ENGLISH} "Production use?"
LangString ProdModeLabelText1 ${LANG_GERMAN}  "Produktivbetrieb?"
LangString ProdModeLabelText1 ${LANG_SPANISH} "¿Uso en producción?"
LangString ProdModeLabelText2 ${LANG_ENGLISH} "To install a simpler FLExTrans interface for production use, choose 'Yes'. For FLExTrans development work choose 'No'."
LangString ProdModeLabelText2 ${LANG_GERMAN}  "Um eine einfachere FLExTrans-Oberfläche für den Produktivbetrieb zu installieren, wählen Sie „Ja“. Für die FLExTrans-Entwicklung wählen Sie „Nein“."
LangString ProdModeLabelText2 ${LANG_SPANISH} "Para instalar una interfaz FLExTrans más sencilla para uso en producción, elija Sí. Para trabajo de desarrollo de FLExTrans, elija No"
LangString NoText ${LANG_ENGLISH} "No"
LangString NoText ${LANG_GERMAN} "Nein"
LangString NoText ${LANG_SPANISH} "No"

LangString YesText ${LANG_ENGLISH} "Yes"
LangString YesText ${LANG_GERMAN} "Ja"
LangString YesText ${LANG_SPANISH} "Sí"

# Set up the Production mode step
Function ProdModeDialog
  nsDialogs::Create 1018
  Pop $Dialog

  ${NSD_CreateLabel} 0 0 450 40 "$(ProdModeLabelText1)"
  Pop $Label
  ${NSD_CreateLabel} 0 30 450 40 "$(ProdModeLabelText2)"
  Pop $Label

  ${NSD_CreateRadioButton} 10 80 200 12 "$(YesText)"
  Pop $RadioYes

  ${NSD_CreateRadioButton} 10 100 200 12 "$(NoText)"
  Pop $RadioNo
  SendMessage $RadioNo ${BM_SETCHECK} ${BST_CHECKED} 0 ; Default to 'No'

  nsDialogs::Show
FunctionEnd

Function ProdModeDlgLeave
  ${NSD_GetChecked} $RadioYes $PRODUCTION_MODE
FunctionEnd

Function .onInit

	;Initial language selection dialog

	Push ""
	Push ${LANG_ENGLISH} 
	Push English
	Push ${LANG_SPANISH}
	Push Español
	Push ${LANG_GERMAN}
	Push Deutsch
	Push A ; A means auto count languages
	       ; for the auto count to work the first empty push (Push "") must remain
	LangDLL::LangDialog "Installer Language" "Please select the language to use with FLExTrans."

	Pop $LANGUAGE
	StrCmp $LANGUAGE "cancel" 0 +2
		Abort
		
	; Assign two-character code for use elsewhere
    ${If} $LANGUAGE == ${LANG_ENGLISH}
        StrCpy $LANGCODE "en"
    ${ElseIf} $LANGUAGE == ${LANG_GERMAN}
        StrCpy $LANGCODE "de"
    ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
        StrCpy $LANGCODE "es"
    ${Else}
        StrCpy $LANGCODE "en" ; fallback
    ${EndIf}
	
FunctionEnd

