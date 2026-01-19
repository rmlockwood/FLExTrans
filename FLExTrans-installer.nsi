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
!define MUI_ICON "${GIT_FOLDER}\Tools\FLExTransWindowIcon.ico"
!define MUI_UNICON "${GIT_FOLDER}\Tools\FLExTransWindowIcon.ico"

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
Var /GLOBAL REAL_USER_APPDATA
Var /GLOBAL REAL_USER_SID
Var /GLOBAL DESKTOP_FOLDER

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

Section "MainSection" SEC01
  InitPluginsDir

  SetOutPath "$INSTDIR\install_files"

  # Install python 
  MessageBox MB_YESNO "$(InstallPythonMsg)" /SD IDYES IDNO endPythonSync
        File "${RESOURCE_FOLDER}\python-3.11.7-amd64.exe"
        ExecWait "$INSTDIR\install_files\python-3.11.7-amd64.exe InstallAllUsers=1 PrependPath=1"
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

    skip:
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

  FindFirst $0 $1 "${WORKPROJECTSDIR}\*.*"
  loop3:
    StrCmp $1 "" done3
    StrCmp $1 "." nextfolder3
    StrCmp $1 ".." nextfolder3
    
	SetOutPath "${WORKPROJECTSDIR}\$1\Config\Collections"

	File "${GIT_FOLDER}\Drafting.ini"
	File "${GIT_FOLDER}\Run Testbed.ini"
	File "${GIT_FOLDER}\Tools.ini"
	File "${GIT_FOLDER}\Synthesis Test.ini"
	File "${GIT_FOLDER}\FLExTrans.ini"
	File "${GIT_FOLDER}\Clusters.ini"
	
    nextfolder3:  
    FindNext $0 $1
    Goto loop3
  done3:
    FindClose $0
	
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
  !define mycmd 'py -3.11 -m pip install -r "$OUT_FOLDER\${FLEXTRANS_FOLDER}\requirements.txt"'
  #  !define mycmd '"$LocalAppdata\Programs\Python\Python311\python.exe" -m pip install -r "$OUT_FOLDER\${FLEXTRANS_FOLDER}\requirements.txt"'
  
  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}"
  File "${GIT_FOLDER}\Command.bat"
  ExecWait '${mycmd}'
  # if the above failed, call the command.bat to do the same thing, but if this was the first time run, pip might not be in the path.
  # Capture the exit code in $0
  nsExec::ExecToStack '${mycmd}'
  Pop $0 ; Get exit code
  
  ${If} $0 != 0
    ExecWait '"$OUT_FOLDER\${FLEXTRANS_FOLDER}\Command.bat"'
  ${EndIf}
  
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
  WriteRegStr HKEY_USERS "$REAL_USER_SID\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithList" "a" "xxe.exe"
  WriteRegStr HKEY_USERS "$REAL_USER_SID\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithList" "MRUList" "a"
  WriteRegStr HKEY_USERS "$REAL_USER_SID\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$R1\OpenWithProgids" "XXE_XML_File" ""
  
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
  nsisunz::Unzip "$INSTDIR\install_files\${ADD_ON_ZIP_FILE}" "$REAL_USER_APPDATA\XMLmind\XMLEditor8\addon"
  
  # Now overwrite some of the files with the Language specific ones
  ${If} $LANGUAGE == ${LANG_GERMAN}
    nsisunz::Unzip "$INSTDIR\install_files\AddOnsForXMLmind_de${PRODUCT_VERSION}.zip" "$REAL_USER_APPDATA\XMLmind\XMLEditor8\addon"
  ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
    nsisunz::Unzip "$INSTDIR\install_files\AddOnsForXMLmind_es${PRODUCT_VERSION}.zip" "$REAL_USER_APPDATA\XMLmind\XMLEditor8\addon"
  ${EndIf}
  
  # Update the XXE properties file
  # Define paths
  StrCpy $R0 "$REAL_USER_APPDATA\XMLmind\XMLEditor8\preferences.properties"
  StrCpy $R1 "$REAL_USER_APPDATA\XMLmind\XMLEditor8\prefs_temp.properties"

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

  # --- Create Desktop Shortcut ---
  
  # Syntax: CreateShortcut "Path\To\Shortcut.lnk" "Path\To\Target.exe" "Parameters" "IconFile" IconIndex
  CreateShortcut "$DESKTOP_FOLDER\FLExTrans.lnk" "$OUT_FOLDER\${FLEXTRANS_FOLDER}" "" "" 0
  # Remove the install_files folder
  RMDir /r "$INSTDIR\install_files"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  SetRegView 64
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR"
  
  # NEW: Save the FLExTrans data path so the uninstaller can find it
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "InstallPath" "$OUT_FOLDER\${FLEXTRANS_FOLDER}"
  
  # Store the identity of the user for the uninstaller
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "UserSID" "$REAL_USER_SID"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "UserAppData" "$REAL_USER_APPDATA"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "UserDesktop" "$DESKTOP_FOLDER"

  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  
  # Update DisplayIcon to point to the actual folder
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\uninst.exe"
  
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr HKLM "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
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
  SetRegView 64
  
  # Read back the saved user info
  ReadRegStr $7 HKLM "${PRODUCT_DIR_REGKEY}" "UserDesktop"
  ReadRegStr $8 HKLM "${PRODUCT_DIR_REGKEY}" "UserSID"
  ReadRegStr $9 HKLM "${PRODUCT_DIR_REGKEY}" "UserAppData"
  
  Delete "$INSTDIR\uninst.exe"
  
  # 1. Get the path where we actually installed FLExTrans from the registry
  ReadRegStr $R0 HKLM "${PRODUCT_DIR_REGKEY}" "InstallPath" 
  
  SetRegView 32
  
  # Check if the requirements file exists before trying to do pip uninstall
  ${If} ${FileExists} "$R0\requirements.txt"
    # Use the -y flag to skip the "Are you sure?" confirmation prompt from pip
    ExecWait 'py -3.11 -m pip uninstall -r "$R0\requirements.txt" -y'
  ${EndIf}
  
  # Note: You'll need to write this "InstallPath" during installation in the Post section
  MessageBox MB_YESNO "Delete the FLExTrans data folder at $R0?" IDNO endFlexDel
    RMDir /r "$R0"
  endFlexDel:

  # 2. Delete the user-specific shortcut
  Delete "$7\FLExTrans.lnk"

  # Remove file associations from the user's registry hive
  DeleteRegKey HKEY_USERS "$8\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.t1x"
  DeleteRegKey HKEY_USERS "$8\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.t2x"
  DeleteRegKey HKEY_USERS "$8\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.t3x"
  DeleteRegKey HKEY_USERS "$8\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.dix"
  
  # Notify Windows that icons/associations have changed
  System::Call 'Shell32::SHChangeNotify(i 0x8000000, i 0, i 0, i 0)'

  MessageBox MB_YESNO "Remove FLExTrans add-ons and preferences from XMLmind?" IDNO skip_xmlmind
    # Define the base search path
    StrCpy $R1 "$9\XMLmind\XMLEditor8\addon"

    # Start searching for folders in the addon directory
    FindFirst $0 $1 "$R1\*.*"
    loop_addons:
      StrCmp $1 "" done_addons ; End of folder list
      
      # Skip the . and .. directory markers
      StrCmp $1 "." next_addon
      StrCmp $1 ".." next_addon

      # Check if the folder name starts with "Apertium"
      StrCpy $2 $1 8 ; Get first 8 characters
      StrCmp $2 "Apertium" found_target
      
      # Check if the folder name starts with "FLExTrans"
      StrCpy $2 $1 9 ; Get first 9 characters
      StrCmp $2 "FLExTrans" found_target
      
      Goto next_addon

    found_target:
      # If we reach here, $1 is a folder name we want to delete.
      # We combine the base path ($R1) and the folder name ($1) for a full path.
      RMDir /r "$R1\$1"

    next_addon:
      FindNext $0 $1
      Goto loop_addons

    done_addons:
      FindClose $0
  skip_xmlmind:

  # Remove Admin/System level files
  Delete "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}"
  RMDir /r "$INSTDIR"

  # Clean up Registry
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  MessageBox MB_OK "Note: Python, XMLmind XML Editor and the FLExTrans Rule Assistant were installed separately. If you wish to remove them, please use the Windows 'Apps & Features' settings."
  
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
    Var /GLOBAL REAL_USERNAME
    Var /GLOBAL USER_PROFILE_PATH
    Var /GLOBAL DOCS_FOLDER_NAME
    Var /GLOBAL DESKTOP_FOLDER_NAME
    
    # 1. Get the username of the person who owns explorer.exe (the real logged-in user)
	nsExec::ExecToStack 'powershell -NoProfile -ExecutionPolicy Bypass -Command "$$p = Get-Process explorer | Select-Object -First 1; (Get-WmiObject Win32_Process -Filter \"ProcessId=$$($$p.Id)\").GetOwner().User"'
    Pop $0  # Return code
    Pop $REAL_USERNAME  # The actual username
    
	# REMOVE NEWLINE/CARRIAGE RETURN
	${StrRep} $REAL_USERNAME $REAL_USERNAME "$\r" ""
	${StrRep} $REAL_USERNAME $REAL_USERNAME "$\n" ""
  
    ${If} $REAL_USERNAME != ""
        # 2. Build the user profile path
        StrCpy $USER_PROFILE_PATH "C:\Users\$REAL_USERNAME"

		# Get the local appdata path
        StrCpy $REAL_USER_APPDATA "$USER_PROFILE_PATH\AppData\Roaming"

        # 3. Get the full localized path (e.g., C:\Users\Name\Documentos)
		# Even if redirected to OneDrive, this gives us the "correct" name
		StrCpy $1 $DOCUMENTS
        
        # 4. Extract just the folder name (e.g., "Documents", "Documentos", "Dokumente")
        ${If} $1 != ""
            ${GetFileName} "$1" $DOCS_FOLDER_NAME
            StrCpy $OUT_FOLDER "$USER_PROFILE_PATH\$DOCS_FOLDER_NAME"
		${Else}
			# Default to Documents
			StrCpy $OUT_FOLDER "$USER_PROFILE_PATH\Documents"
        ${EndIf}
		
        # 3. Get the full localized path (e.g., C:\Users\Name\Schreibtisch)
		# Even if redirected to OneDrive, this gives us the "correct" name
		StrCpy $1 $DESKTOP
        
        # 4. Extract just the folder name (e.g., "Desktop", "Schreibtisch")
        ${If} $1 != ""
            ${GetFileName} "$1" $DESKTOP_FOLDER_NAME
            StrCpy $DESKTOP_FOLDER "$USER_PROFILE_PATH\$DESKTOP_FOLDER_NAME"
		${Else}
			# Default to Documents
			StrCpy $DESKTOP_FOLDER "$USER_PROFILE_PATH\Desktop"
        ${EndIf}
    ${Else}
		# Ultimate fallback
		StrCpy $OUT_FOLDER "C:\FLExTrans"
    ${EndIf}
	
    # 5. Create the folder
    CreateDirectory "$OUT_FOLDER"
    
	# get the SID of the local user for registry work
	nsExec::ExecToStack 'powershell -NoProfile -ExecutionPolicy Bypass -Command "$$objUser = New-Object System.Security.Principal.NTAccount(\"$REAL_USERNAME\"); $$strSID = $$objUser.Translate([System.Security.Principal.SecurityIdentifier]); $$strSID.Value"'
	Pop $0
	Pop $REAL_USER_SID

	${StrRep} $REAL_USER_SID $REAL_USER_SID "$\r" ""
	${StrRep} $REAL_USER_SID $REAL_USER_SID "$\n" ""
  
    nsDialogs::Create 1018
    Pop $Dialog
    ${If} $Dialog == error
        Abort
    ${EndIf}
    
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
	# Use the $OUT_FOLDER we calculated in nsDialogsPage
	nsDialogs::SelectFolderDialog "Select Destination Folder" "$OUT_FOLDER"
	Pop $R0

	${If} $R0 != "error"
		StrCpy $OUT_FOLDER $R0
		${NSD_SetText} $DESTTEXT $OUT_FOLDER
	${EndIf}
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
