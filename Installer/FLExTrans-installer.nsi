Unicode True
!include "StrRep.nsh"   # local file
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "LangFile.nsh"


; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "FLExTrans"
!define PRODUCT_PUBLISHER "SIL International"
!define PRODUCT_WEB_SITE "https://software.sil.org/flextrans"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_VERSION "3.15"
!define PYTHON_MAJOR "3"
!define PYTHON_MINOR "13"
!define PYTHON_PATCH "12"
!define PYTHON_VERSION "${PYTHON_MAJOR}.${PYTHON_MINOR}.${PYTHON_PATCH}"
!define PYTHON_LAUNCHER_ARG "-${PYTHON_MAJOR}.${PYTHON_MINOR}"
!define PYTHON_EXE    "python-${PYTHON_VERSION}-amd64.exe"
!define XXE_EXE "xxe-perso-8_2_0-setup.exe"
!define PRODUCT_ZIP_FILE "FLExToolsWithFLExTrans${PRODUCT_VERSION}.zip"
!define ADD_ON_ZIP_FILE "AddOnsForXMLmind${PRODUCT_VERSION}.zip"
;!define HERMIT_CRAB_ZIP_FILE "HermitCrabTools${PRODUCT_VERSION}.zip"
!define FLEXTRANS_FOLDER "FLExTrans"
!define WORKPROJECTSDIR "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects"
!define GERMAN_SWEDISHDIR "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish"
!define TEMPLATEDIR "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject"
!define RULEASSISTANT "FLExTrans.Rule Assistant"
!define REPLACEMENTEDITOR "FLExTrans.Replacement Dictionary Editor"
!define TEXTIN "FLExTrans.Text In Rules"
!define TEXTOUT "FLExTrans.Text Out Rules"
!define EXPORTFROMFLEX "FLExTrans.Export Text from Target FLEx to Paratext"
!define INSTALLER_RESOURCES "Installer\InstallerResources"
!define GIT_RESOURCES "${GIT_FOLDER}\${INSTALLER_RESOURCES}"
!define MAKEFILESDIR "${GIT_RESOURCES}\Makefiles"
!define TRANSFER_RULESDIR "${GIT_RESOURCES}\TransferRules"
!define VBSDIR "${GIT_RESOURCES}\VBS"
!define INIDIR "${GIT_RESOURCES}\INI"
!define REPLACEMENT_FILE "${GIT_RESOURCES}\replace.dix"

; MUI 1.67 compatible ------
!include "MUI.nsh"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "Comments" ""
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalTrademarks" ""
VIAddVersionKey "LegalCopyright" "? 2015-2026 SIL International"
VIAddVersionKey "FileDescription" ""
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"

; Always 4 numerals
VIProductVersion 3.15.0.${BUILD_NUM}

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${GIT_RESOURCES}\DialogImages\FLExTransWindowIcon.ico"
!define MUI_UNICON "${GIT_RESOURCES}\DialogImages\FLExTransWindowIcon.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; Language selection page
Page custom LanguageDialog LanguageDialogLeave

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
Var /GLOBAL LANG_PAGE_VISITED
Var /GLOBAL LANG_PAGE_GOING_BACK
Var /GLOBAL STR_CHOOSE_FOLDER
Var /GLOBAL STR_BROWSE
Var /GLOBAL STR_PROD_LABEL1
Var /GLOBAL STR_PROD_LABEL2
Var /GLOBAL STR_YES
Var /GLOBAL STR_NO
Var /GLOBAL STR_PYTHON_OLD
Var /GLOBAL STR_INSTALL_PYTHON
Var /GLOBAL STR_INSTALL_XMLMIND

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; ==============================================================
; TO ADD A NEW LANGUAGE — touch only the items marked (*)
; ==============================================================
; (*) 1. Copy LangForInstallerScript\en.nsh to LangForInstallerScript\XX.nsh, change EN_ prefix to XX_,
;        translate all string values, set XX_DISPLAY_NAME.
; (*) 2. Add one !insertmacro MUI_LANGUAGE line below.
; (*) 3. Add one !include "LangForInstallerScript\XX.nsh" line below.
; (*) 4. Add one Push pair in ShowLanguageDialog (search for that function).
; (*) 5. Add one ${ElseIf} block in SetLanguageCode (search for that function).
;     6. Add the language-specific transfer rules files
;        (e.g. transfer_rules-Swedish_XX.t1x) to the TransferRules folder.
; (*) 7. Add the XXE addon folder to XXEaddon\translations\XX and modify the CreateInstaller LangForInstallerScript
;        to zip this folder and add a File line in the XXE section below.
; ==============================================================

; MUI language registrations — add one line per language (*)
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "French"

; Per-language string definitions — add one !include per language (*)
; Each file defines LangStrings and XX_* compile-time string constants.
!include "InstallerResources\LangForInstallerScript\de.nsh"
!include "InstallerResources\LangForInstallerScript\en.nsh"
!include "InstallerResources\LangForInstallerScript\es.nsh"
!include "InstallerResources\LangForInstallerScript\fr.nsh"

; Macro for copying localized transfer rules files.
; Uses $LANGCODE set at runtime — no edits needed here when adding a language.
; All language-specific source files must exist in ${TRANSFER_RULESDIR}.
!macro InstallLocalizedRulesFile DEST_NAME SRC_BASE
    ; 1. Save the current output directory
    Push $OUTDIR
    
    ; 2. (Compile-time) Package all matching rule files into a temporary folder
    SetOutPath "$INSTDIR\install_files\rules"
    File "${TRANSFER_RULESDIR}\${SRC_BASE}*.t1x"
    
    ; 3. Restore the target output directory
    Pop $0
    SetOutPath $0

    ; 4. (Run-time) Copy and rename the correct file based on the selected language
    ${If} ${FileExists} "$INSTDIR\install_files\rules\${SRC_BASE}_$LANGCODE.t1x"
        CopyFiles /SILENT "$INSTDIR\install_files\rules\${SRC_BASE}_$LANGCODE.t1x" "$OUTDIR\${DEST_NAME}"
    ${Else}
        ; Fall back to the base (English) file if the localized version isn't found
        CopyFiles /SILENT "$INSTDIR\install_files\rules\${SRC_BASE}.t1x" "$OUTDIR\${DEST_NAME}"
    ${EndIf}
!macroend

; MUI end ------
Icon "${MUI_ICON}"
Name "${PRODUCT_NAME}"

OutFile "${OUT_FOLDER}\${PRODUCT_NAME}${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\FLExTrans_Installer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  InitPluginsDir

  SetOutPath "$INSTDIR\install_files"

  # Check if Python ${PYTHON_MAJOR}.${PYTHON_MINOR} specifically is installed
  nsExec::ExecToStack 'py -${PYTHON_MAJOR}.${PYTHON_MINOR} --version 2>&1'
  Pop $0  ; exit code
  Pop $1  ; output (e.g. "Python 3.13.2") or empty if not found

  ; Treat non-zero exit code OR empty output as not found
  ${If} $0 != 0
    Goto needPythonNotFound
  ${EndIf}
  ${If} $1 == ""
    Goto needPythonNotFound
  ${EndIf}

  ; Python 3.13.x is installed - strip prefix and whitespace
  StrCpy $2 $1 "" 7        ; remove leading "Python "
  ${StrRep} $2 $2 "$\r" ""
  ${StrRep} $2 $2 "$\n" ""

  ; Skip past "major.minor." to get patch number
  StrCpy $4 0
  StrCpy $7 0  ; dot counter
  extractPatchLoop:
    StrCpy $5 $2 1 $4
    StrCmp $5 "" extractPatchDone
    StrCmp $5 "." countDot
    IntOp $4 $4 + 1
    Goto extractPatchLoop
  countDot:
    IntOp $7 $7 + 1
    IntOp $4 $4 + 1
    IntCmp $7 2 extractPatchNumber 0 0  ; after 2nd dot, start collecting patch
    Goto extractPatchLoop
  extractPatchNumber:
    StrCpy $6 ""
  extractPatchNumberLoop:
    StrCpy $5 $2 1 $4
    StrCmp $5 "" extractPatchDone
    StrCpy $6 "$6$5"
    IntOp $4 $4 + 1
    Goto extractPatchNumberLoop
  extractPatchDone:

  ; Check patch version is >= ${PYTHON_PATCH}
  IntCmp $6 ${PYTHON_PATCH} endPythonSync needPythonOldPatch endPythonSync 
  ; equal=ok, less=needPythonOldPatch, greater=ok

  needPythonOldPatch:
    MessageBox MB_YESNO "Python $2 $STR_PYTHON_OLD" /SD IDYES IDNO endPythonSync
      File "${RESOURCE_FOLDER}\${PYTHON_EXE}"
      ExecWait "$INSTDIR\install_files\${PYTHON_EXE} InstallAllUsers=1 PrependPath=1"
      Goto endPythonSync

  needPythonNotFound:
    MessageBox MB_YESNO "$STR_INSTALL_PYTHON" /SD IDYES IDNO endPythonSync
      File "${RESOURCE_FOLDER}\${PYTHON_EXE}"
      ExecWait "$INSTDIR\install_files\${PYTHON_EXE} InstallAllUsers=1 PrependPath=1"
      Goto endPythonSync

  endPythonSync:
  
  Var /GLOBAL OUT_FOLDER
  # Unzip FLExTrans to the desired folder
  # GIT_FOLDER needs to be set to your local git FLExTrans folder in the compiler settings
  File "${GIT_FOLDER}\Installer\${PRODUCT_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${PRODUCT_ZIP_FILE}" "$OUT_FOLDER"

  # Create empty Output folders
  CreateDirectory "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\German-Swedish\Output"
  CreateDirectory "$OUT_FOLDER\${FLEXTRANS_FOLDER}\WorkProjects\TemplateProject\Output"
  
  ## Copy files only if they don't already exist. These are files users may change.
  SetOverwrite off
  
  # Replacement dictionary  
  ; German-Swedish project folder
  SetOutPath "${GERMAN_SWEDISHDIR}\Output"
  File "${REPLACEMENT_FILE}"

  ; template project folder
  SetOutPath "${TEMPLATEDIR}\Output"
  File "${REPLACEMENT_FILE}"
    
  # Transfer rule files for German-Swedish folder
  SetOutPath "${GERMAN_SWEDISHDIR}"
  ; Pass the file name that it should be called in the destination folder and the starting part of the original filename in GIT (without _de, etc.)
  !insertmacro InstallLocalizedRulesFile "transfer_rules-Swedish.t1x" "transfer_rules-Swedish"
  
  # Transfer rule files for TemplateProject folder
  SetOutPath "${TEMPLATEDIR}"
  ; Pass the file name that it should be called in the destination folder and the starting part of the original filename in GIT (without _de, etc.)
  !insertmacro InstallLocalizedRulesFile "transfer_rules.t1x" "transfer_rules-Swedish"
  !insertmacro InstallLocalizedRulesFile "transfer_rules-Sample1.t1x" "transfer_rules-Sample1"
    
  ## Now we overwrite the following files.
  SetOverwrite on
  
  # Find where FLEx is installed
  ReadRegStr $0 HKLM Software\WOW6432Node\SIL\FieldWorks\9 "RootCodeDir"
  
  # Unzip the HermitCrab files in the FLEx programs folder
  #SetOutPath "$INSTDIR\install_files"
  #File "${GIT_FOLDER}\${HERMIT_CRAB_ZIP_FILE}"
  #nsisunz::Unzip "$INSTDIR\install_files\${HERMIT_CRAB_ZIP_FILE}" "$0"

  # Delete SettingGui.py from the Modules\FLExTrans folder (for old installs), it now lives right under FlexTools
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
      File "${VBSDIR}\FLExTrans.vbs"
    ${EndIf}
    
    # Overwrite flextools.ini
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Config\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Config"
      
      # Use a production mode ini file if the user chose that
      ${If} $PRODUCTION_MODE <> ${BST_UNCHECKED}
        File "/oname=${WORKPROJECTSDIR}\$1\Config\flextools.ini" "${INIDIR}\flextools_basic.ini"
      ${Else}
        File "${INIDIR}\flextools.ini"
      ${EndIf}
    ${EndIf}
    
	# Overwrite FLExTrans.ini - the production mode collection
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Config\Collections\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Config\Collections"
      File "${INIDIR}\FLExTrans.ini"
    ${EndIf}
	
	# Overwrite Makefiles
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Build\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Build"
      File "${MAKEFILESDIR}\Makefile"
      File "${MAKEFILESDIR}\Makefile.advanced"
    ${EndIf}
	
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1\Build\LiveRuleTester"
      File "/oname=${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\Makefile" "${MAKEFILESDIR}\MakefileForLiveRuleTester"
      File "/oname=${WORKPROJECTSDIR}\$1\Build\LiveRuleTester\Makefile.advanced" "${MAKEFILESDIR}\MakefileForLiveRuleTester.advanced"
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
	
  ${If} $LANGUAGE == ${LANG_FRENCH}
  
    ${If} ${FileExists} "${WORKPROJECTSDIR}\German-Swedish\Config\Collections\Outils.ini"
	
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

	File "${INIDIR}\Drafting.ini"
	File "${INIDIR}\Run Testbed.ini"
	File "${INIDIR}\Tools.ini"
	File "${INIDIR}\Synthesis Test.ini"
	File "${INIDIR}\FLExTrans.ini"
	File "${INIDIR}\Clusters.ini"
	
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
  !define mycmd 'py ${PYTHON_LAUNCHER_ARG} -m pip install -r "$OUT_FOLDER\${FLEXTRANS_FOLDER}\requirements.txt"'
  
  SetOutPath "$OUT_FOLDER\${FLEXTRANS_FOLDER}"
  File "${GIT_RESOURCES}\Command.bat"
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
  # RESOURCE_FOLDER is a variable like GIT_FOLDER that is passed to the makensis program when compiling the installer
  File "${RESOURCE_FOLDER}\FLExTransRuleAssistant-setup.exe"
  ExecWait "$INSTDIR\install_files\FLExTransRuleAssistant-setup.exe /SILENT"
  
  SetOutPath "$INSTDIR\install_files"


  # Check if XMLmind XML Editor (XXE) is installed
  ReadRegStr $0 HKLM "SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\XMLmind XML Editor_is1" "DisplayName"

  ${If} $0 == ""
    # XMLmind not found - prompt to install
    MessageBox MB_YESNO "$STR_INSTALL_XMLMIND" /SD IDYES IDNO endXXESync
      File "${RESOURCE_FOLDER}\${XXE_EXE}"
      ExecWait "$INSTDIR\install_files\${XXE_EXE} /SILENT"
      Goto endXXESync
  ${EndIf}
  endXXESync:
    
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


  # Bundle the base (English) XXE addon zip and all language-specific ones.
  # (*) ADD A NEW LANGUAGE: add one File line here for the new language zip.
  File "${GIT_FOLDER}\Installer\${ADD_ON_ZIP_FILE}"
  File "${GIT_FOLDER}\Installer\AddOnsForXMLmind_de${PRODUCT_VERSION}.zip"
  File "${GIT_FOLDER}\Installer\AddOnsForXMLmind_es${PRODUCT_VERSION}.zip"
  File "${GIT_FOLDER}\Installer\AddOnsForXMLmind_fr${PRODUCT_VERSION}.zip"

  # Install the base (English) addon first, then overwrite with the
  # language-specific zip if one exists. 
  nsisunz::Unzip "$INSTDIR\install_files\${ADD_ON_ZIP_FILE}" "$REAL_USER_APPDATA\XMLmind\XMLEditor8\addon"
  ${If} $LANGCODE != "en"
    ${If} ${FileExists} "$INSTDIR\install_files\AddOnsForXMLmind_$LANGCODE${PRODUCT_VERSION}.zip"
      nsisunz::Unzip "$INSTDIR\install_files\AddOnsForXMLmind_$LANGCODE${PRODUCT_VERSION}.zip" "$REAL_USER_APPDATA\XMLmind\XMLEditor8\addon"
    ${EndIf}
  ${EndIf}
  


# Write PowerShell script to temp file that will add xxeVersion=8.2.0 and autoCheckForUpdates=false if not present
# autoCheckForUpdates=false gets written if its not false.
# ReadFile was having problems so Claude and I went with this solution
FileOpen $R0 "$TEMP\xxe_prefs.ps1" "w"
FileWrite $R0 '$$prefs = "$$env:APPDATA\XMLmind\XMLEditor8\preferences.properties"$\r$\n'
FileWrite $R0 '$$dir = Split-Path $$prefs$\r$\n'
FileWrite $R0 'if (-not (Test-Path $$dir)) { New-Item -ItemType Directory -Path $$dir | Out-Null }$\r$\n'
FileWrite $R0 'if (Test-Path $$prefs) {$\r$\n'
FileWrite $R0 '    $$lines = Get-Content $$prefs$\r$\n'
FileWrite $R0 '    $$hasVersion = ($$lines -match "^xxeVersion=").Count -gt 0$\r$\n'
FileWrite $R0 '    $$hasAutoCheck = ($$lines -match "^autoCheckForUpdates=").Count -gt 0$\r$\n'
FileWrite $R0 '    $$lines = $$lines -replace "autoCheckForUpdates=true","autoCheckForUpdates=false"$\r$\n'
FileWrite $R0 '    if (-not $$hasVersion) { $$lines += "xxeVersion=8.2.0" }$\r$\n'
FileWrite $R0 '    if (-not $$hasAutoCheck) { $$lines += "autoCheckForUpdates=false" }$\r$\n'
FileWrite $R0 '    $$lines | Set-Content $$prefs -Encoding ASCII$\r$\n'
FileWrite $R0 '} else {$\r$\n'
FileWrite $R0 '    $$lines = @("xxeVersion=8.2.0", "autoCheckForUpdates=false")$\r$\n'
FileWrite $R0 '    $$lines | Set-Content $$prefs -Encoding ASCII$\r$\n'
FileWrite $R0 '}$\r$\n'
FileWrite $R0 'Write-Output "Done"$\r$\n'
FileClose $R0

; Execute it and log the output
nsExec::ExecToLog 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$TEMP\xxe_prefs.ps1"'
Pop $R1
FileWrite $9 "PowerShell exit code: $R1$\r$\n"

; Clean up
Delete "$TEMP\xxe_prefs.ps1"


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
    ExecWait 'py ${PYTHON_LAUNCHER_ARG} -m pip uninstall -r "$R0\requirements.txt" -y'
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

  MessageBox MB_YESNO "Remove FLExTrans add-ons and preferences from XMLmind? The XMLmind program itself will remain." IDNO skip_xmlmind
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
  
  MessageBox MB_OK "Note: Python, XMLmind XML Editor and the FLExTrans Rule Assistant were installed separately. If you wish to remove them, please use the Windows 'Installed apps' setting."
  
  SetAutoClose true
SectionEnd

#--Select folder function
!include nsDialogs.nsh
var /global BROWSEDEST
var /global DESTTEXT
;Var Dialog
Function nsDialogsPage

    StrCpy $LANG_PAGE_GOING_BACK "1"
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
  
	# 3. Get the full localized path (e.g., C:\Users\Name\Schreibtisch)
	# Even if redirected to OneDrive, this gives us the "correct" name
	SetRegView 64
	ReadRegStr $5 HKU "$REAL_USER_SID\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" "Desktop"
	SetRegView 32
	
	StrCpy $1 $5
	StrCpy $DESKTOP_FOLDER $5
	
	# 4. Extract just the folder name (e.g., "Desktop", "Schreibtisch")
	${If} $1 != ""
		${GetFileName} "$1" $DESKTOP_FOLDER_NAME
		
		Push $DESKTOP_FOLDER
		Push "%USERPROFILE%"
		Call StrStr
		Pop $0

		# If the shellfolder path contains USERPROFILE, build the string with our user profile variable
		${If} $0 != ""
			StrCpy $DESKTOP_FOLDER "$USER_PROFILE_PATH\$DESKTOP_FOLDER_NAME"
		${Else}
			# No %USERPROFILE%, now check for OneDrive
			Push $DESKTOP_FOLDER
			Push "OneDrive"
			Call StrStr
			Pop $0
			
			# No OneDrive
			${If} $0 == ""
				# default to Desktop
				StrCpy $DESKTOP_FOLDER "$USER_PROFILE_PATH\Desktop"
			${EndIf}
				
			# otherwise the whole path is already in the variable $DESKTOP_FOLDER
		${EndIf}
	${Else}
		# default to Desktop
		StrCpy $DESKTOP_FOLDER "$USER_PROFILE_PATH\Desktop"
	${EndIf}

    nsDialogs::Create 1018
    Pop $Dialog
    ${If} $Dialog == error
        Abort
    ${EndIf}
    
    ${NSD_CreateLabel} 0 60 100% 12u "$STR_CHOOSE_FOLDER"
    ${NSD_CreateText} 0 80 70% 12u "$OUT_FOLDER"
    pop $DESTTEXT
    SendMessage $DESTTEXT ${EM_SETREADONLY} 1 0
    ${NSD_CreateBrowseButton} 320 80 20% 12u "$STR_BROWSE"
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

# Set up the Production mode step
Function ProdModeDialog
  nsDialogs::Create 1018
  Pop $Dialog

  ${NSD_CreateLabel} 0 0 450 40 "$STR_PROD_LABEL1"
  Pop $Label
  ${NSD_CreateLabel} 0 30 450 40 "$STR_PROD_LABEL2"
  Pop $Label

  ${NSD_CreateRadioButton} 10 80 200 12 "$STR_YES"
  Pop $RadioYes

  ${NSD_CreateRadioButton} 10 100 200 12 "$STR_NO"
  Pop $RadioNo
  SendMessage $RadioNo ${BM_SETCHECK} ${BST_CHECKED} 0 ; Default to 'No'

  nsDialogs::Show
FunctionEnd

Function ProdModeDlgLeave
  ${NSD_GetChecked} $RadioYes $PRODUCTION_MODE
FunctionEnd

Function .onInit

  StrCpy $LANG_PAGE_VISITED "0"
  StrCpy $LANG_PAGE_GOING_BACK "0"
  Call ShowLanguageDialog
  Call SetLanguageCode
  
FunctionEnd

Function LanguageDialog
  ${If} $LANG_PAGE_VISITED == "0"
    StrCpy $LANG_PAGE_VISITED "1"
    Abort
  ${ElseIf} $LANG_PAGE_GOING_BACK == "1"
    StrCpy $LANG_PAGE_GOING_BACK "0"
    Call ShowLanguageDialog
	Call SetLanguageCode
  ${Else}
    Abort
  ${EndIf}
FunctionEnd

Function LanguageDialogLeave
  Call SetLanguageCode
FunctionEnd

Function ShowLanguageDialog
  ; (*) ADD A NEW LANGUAGE: add a Push ${LANG_XX} / Push ${XX_DISPLAY_NAME}
  ;     pair before the final 'Push A' line. Order = dialog order.

  Push ""
  Push ${LANG_ENGLISH}
  Push ${EN_DISPLAY_NAME}
  Push ${LANG_SPANISH}
  Push ${ES_DISPLAY_NAME}
  Push ${LANG_FRENCH}
  Push ${FR_DISPLAY_NAME}
  Push ${LANG_GERMAN}
  Push ${DE_DISPLAY_NAME}
  Push A ; A means auto count languages
         ; for the auto count to work the first empty push (Push "") must remain
  LangDLL::LangDialog "Installer Language" "Please select the language to use with FLExTrans."
  
  Pop $LANGUAGE
  StrCmp $LANGUAGE "cancel" 0 +2
  	Abort
  	
FunctionEnd

!macro ASSIGN_LANG_STRINGS PREFIX
    StrCpy $LANGCODE             "${${PREFIX}_LANGCODE}"
    StrCpy $STR_CHOOSE_FOLDER    "${${PREFIX}_CHOOSE_FOLDER}"
    StrCpy $STR_BROWSE           "${${PREFIX}_BROWSE}"
    StrCpy $STR_PROD_LABEL1      "${${PREFIX}_PROD_LABEL1}"
    StrCpy $STR_PROD_LABEL2      "${${PREFIX}_PROD_LABEL2}"
    StrCpy $STR_YES              "${${PREFIX}_YES}"
    StrCpy $STR_NO               "${${PREFIX}_NO}"
    StrCpy $STR_PYTHON_OLD       "${${PREFIX}_PYTHON_OLD}"
    StrCpy $STR_INSTALL_PYTHON   "${${PREFIX}_INSTALL_PYTHON}"
    StrCpy $STR_INSTALL_XMLMIND  "${${PREFIX}_INSTALL_XMLMIND}"
!macroend

Function SetLanguageCode
  ; (*) ADD A NEW LANGUAGE: copy one ${ElseIf} block and fill in the new XX two letter code.
  ;     the same code you are using in LangForInstallerScript\XX.nsh file.
  ${If} $LANGUAGE == ${LANG_ENGLISH}
    !insertmacro ASSIGN_LANG_STRINGS "EN"
  ${ElseIf} $LANGUAGE == ${LANG_GERMAN}
    !insertmacro ASSIGN_LANG_STRINGS "DE"
  ${ElseIf} $LANGUAGE == ${LANG_SPANISH}
    !insertmacro ASSIGN_LANG_STRINGS "ES"
  ${ElseIf} $LANGUAGE == ${LANG_FRENCH}
    !insertmacro ASSIGN_LANG_STRINGS "FR"
  ${Else}
    ; Fallback to English
    !insertmacro ASSIGN_LANG_STRINGS "EN"
  ${EndIf}
FunctionEnd

; ==========================================================
; StrStr - Searches for a string within another string
; Input: Top of stack = string to search for
;        Second on stack = string to search in
; Output: Top of stack = result (string from start of match)
; ==========================================================
Function StrStr
  Exch $R1 ; string to search for
  Exch
  Exch $R2 ; string to search in
  Push $R3
  Push $R4
  Push $R5
  StrLen $R3 $R1
  StrCpy $R4 0
  loop:
    StrCpy $R5 $R2 $R3 $R4
    StrCmp $R5 $R1 done
    StrCmp $R5 "" done
    IntOp $R4 $R4 + 1
    Goto loop
  done:
  StrCpy $R1 $R2 "" $R4
  Pop $R5
  Pop $R4
  Pop $R3
  Pop $R2
  Exch $R1
FunctionEnd