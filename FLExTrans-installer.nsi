!include "StrRep.nsh"
!include "ReplaceInFile.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "FLExTrans"
!define PRODUCT_PUBLISHER "SIL International"
!define PRODUCT_WEB_SITE "https://software.sil.org/flextrans"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_VERSION "3.13"
!define PRODUCT_ZIP_FILE "FLExToolsWithFLExTrans${PRODUCT_VERSION}.zip"
!define ADD_ON_ZIP_FILE "AddOnsForXMLmind${PRODUCT_VERSION}.zip"
!define HERMIT_CRAB_ZIP_FILE "HermitCrabTools${PRODUCT_VERSION}.zip"
!define FLEX_TOOLS_WITH_VERSION "FLExTrans"
!define WORKPROJECTSDIR "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects"
!define TEMPLATEDIR "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject"
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
VIAddVersionKey "LegalCopyright" "© 2015-2025 SIL International"
VIAddVersionKey "FileDescription" ""
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"

; Always 4 numerals
VIProductVersion 3.13.0.${BUILD_NUM}

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

Function ProdModeDialog
  nsDialogs::Create 1018
  Pop $Dialog

  ${NSD_CreateLabel} 0 0 450 40 "Do you want to set FLExTrans up for production use? If you choose Yes, the installer will set up a simpler interface for production use. For normal development work with FLExTrans leave this as 'No'."
  Pop $Label

  ${NSD_CreateRadioButton} 10 50 200 12 "Yes"
  Pop $RadioYes

  ${NSD_CreateRadioButton} 10 70 200 12 "No"
  Pop $RadioNo
  SendMessage $RadioNo ${BM_SETCHECK} ${BST_CHECKED} 0 ; Default to 'No'

  nsDialogs::Show
FunctionEnd

Function ProdModeDlgLeave
  ${NSD_GetChecked} $RadioYes $PRODUCTION_MODE
FunctionEnd

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

!macro _ReplaceInFile SOURCE_FILE SEARCH_TEXT REPLACEMENT
  Push "${SOURCE_FILE}"
  Push "${SEARCH_TEXT}"
  Push "${REPLACEMENT}"
  Call RIF
!macroend

; MUI end ------
Icon "${GIT_FOLDER}\Tools\FLExTransWindowIcon.ico"
Name "${PRODUCT_NAME}"

OutFile "${PRODUCT_NAME}${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\FLExTrans_Installer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section -Prerequisites
InitPluginsDir

  SetOutPath "$INSTDIR\install_files"

  # Install python 
  MessageBox MB_YESNO "Install Python 3.11.7? $\nIMPORTANT! Check the box: 'Add Python 3.11 to Path'. $\nUse the 'Install now' option" /SD IDYES IDNO endPythonSync
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
  CreateDirectory "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Output"
  CreateDirectory "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject\Output"
  
  SetOverwrite off

  # Copy files users may change only if they don't already exist
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Output"

  File "${GIT_FOLDER}\replace.dix"

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish"
  
  File "${GIT_FOLDER}\transfer_rules-Swedish.t1x"
  
  SetOutPath "${TEMPLATEDIR}\Output"

  File "${GIT_FOLDER}\replace.dix"
  
  SetOutPath "${TEMPLATEDIR}"

  File "${GIT_FOLDER}\transfer_rules-Sample1.t1x"
  
  # Copy and rename the file in the Template folder to not have -Swedish
  File "/oname=${TEMPLATEDIR}\transfer_rules.t1x" "${GIT_FOLDER}\transfer_rules-Swedish.t1x"

  SetOverwrite on
  
  # Find where FLEx is installed
  ReadRegStr $0 HKLM Software\WOW6432Node\SIL\FieldWorks\9 "RootCodeDir"
  
  # Unzip the HermitCrab files in the FLEx programs folder
  SetOutPath "$INSTDIR\install_files"
  File "${GIT_FOLDER}\${HERMIT_CRAB_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${HERMIT_CRAB_ZIP_FILE}" "$0"

  # Delete SettingGui.py from the Modules\FLExTrans folder, it now lives right under FlexTools
  Delete "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\FlexTools\Modules\FLExTrans\SettingsGUI.py"

  # Delete FTPaths.py from the FlexTools folder (for old installs), otherwise it inteferes with the one in Modules\FLExTrans\Lib
  Delete "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\FlexTools\FTPaths.py"
  
  # Fix up ini files, both collection ones and flextools.ini
  SetOutPath ${WORKPROJECTSDIR}
  FindFirst $0 $1 "${WORKPROJECTSDIR}\*.*"
  loop1:
    StrCmp $1 "" done1
    StrCmp $1 "." nextfolder
    StrCmp $1 ".." nextfolder
    
    # Get two values from flextools.ini
    ReadIniStr $8 "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentproject"
    ReadIniStr $9 "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "DEFAULT" "currentcollection"

    # If currentcollection is set to FLExTrans (likely from a previous install in production mode) change it to Tools
    # Otherwise a developer-type user will get this collection added as a tab.
    ${If} $9 == "FLExTrans"
      StrCpy $9 "Tools"
    ${EndIf}

    # Overwrite FlexTools.vbs
    ${If} ${FileExists} "${WORKPROJECTSDIR}\$1\*.*"
      SetOutPath "${WORKPROJECTSDIR}\$1"
      File "${GIT_FOLDER}\FlexTools.vbs"
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
    !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "currentproject = 'German-FLExTrans-Sample'" "currentproject = '$8'"
    !insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\flextools.ini" "currentcollection = 'Drafting'" "currentcollection = '$9'"
    
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
			
			# Delete extra section if needed. Mainly for MB.
			DeleteINISec "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${EXPORTFROMFLEX}"
			# Need to do this before we write EXPORTFROMFLEX below so that we don't get duplicate sections
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Export FLEx Text to Paratext" "Export Text from Target FLEx to Paratext"

			# Write new tools to the tools.ini file. For ones that already exist, X=Y gets added.
			WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${RULEASSISTANT}" "X" "Y"
			WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${REPLACEMENTEDITOR}" "X" "Y"
			WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${TEXTIN}" "X" "Y"
			WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${TEXTOUT}" "X" "Y"
			WriteINIStr "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "${EXPORTFROMFLEX}" "X" "Y"

			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Set Up Transfer Rule Grammatical Categories" "Set Up Transfer Rule Categories and Attributes"
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Export Translated Text to Paratext" "Export FLExTrans Draft to Paratext"
			
		${Else}
			# Rename modules in the all the .ini files (for old installs)
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Extract Bilingual Lexicon" "Build Bilingual Lexicon"
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Convert Text to STAMP Format" "Convert Text to Synthesizer Format"
			# older module names
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Extract Target Lexicon" "Synthesize Text"
			!insertmacro _ReplaceInFile "${WORKPROJECTSDIR}\$1\Config\Collections\$4" "Catalog Target Prefixes" "Catalog Target Affixes"
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
    
  SetOverwrite off

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections"
  File "${GIT_FOLDER}\Drafting.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"
  File "${GIT_FOLDER}\Synthesis Test.ini"
  File "${GIT_FOLDER}\FLExTrans.ini"
  File "${GIT_FOLDER}\Clusters.ini"

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject\Config\Collections"
  File "${GIT_FOLDER}\Drafting.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"
  File "${GIT_FOLDER}\Synthesis Test.ini"
  File "${GIT_FOLDER}\FLExTrans.ini"
  File "${GIT_FOLDER}\Clusters.ini"

  SetOverwrite on
  
# Attempt to run pip to install FlexTools dependencies
  !define mycmd '"$LocalAppdata\Programs\Python\Python311\python.exe" -m pip install -r "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\requirements.txt"'
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}"
  File "${GIT_FOLDER}\Command.bat"
  # assume pip3 got installed in the default folder under %appdata%. If it did pip will run successfully the first time it gets installed.
  ExecWait '${mycmd}'
  # if the above failed, call the command.bat to do the same thing, but if this was the first time run, pip won't be in the path.
  IfErrors 0 +2
        Exec '"$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\Command.bat"'

  # Install Rule Assistant in silent mode
  SetOutPath "$INSTDIR\install_files"
  File "${RESOURCE_FOLDER}\FLExTransRuleAssistant-setup.exe"
  ExecWait "$INSTDIR\install_files\FLExTransRuleAssistant-setup.exe /SILENT"
  
  # Install XMLmind
  SetOutPath "$INSTDIR\install_files"
  MessageBox MB_YESNO "Install XMLmind?" /SD IDYES IDNO endXXeSync
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

  File "${GIT_FOLDER}\${ADD_ON_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${ADD_ON_ZIP_FILE}" "$APPDATA\XMLmind\XMLEditor8\addon"
  SetOutPath "$APPDATA\XMLmind\XMLEditor8"
  File "${GIT_FOLDER}\preferences.properties"
  SetOutPath "$INSTDIR"

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
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${FLEX_TOOLS_WITH_VERSION}"
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
  MessageBox MB_YESNO "Delete the ${FLEX_TOOLS_WITH_VERSION} folder?" /SD IDYES IDNO endFlexDel
        RMDir /r "$DOCUMENTS\${FLEX_TOOLS_WITH_VERSION}"
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

        ${NSD_CreateLabel} 0 60 100% 12u "Choose where to put FLExTrans folder."
        ${NSD_CreateText} 0 80 70% 12u "$OUT_FOLDER"
        pop $DESTTEXT
        SendMessage $DESTTEXT ${EM_SETREADONLY} 1 0
        ${NSD_CreateBrowseButton} 320 80 20% 12u "Browse"
        pop $BROWSEDEST

        ${NSD_OnClick} $BROWSEDEST Browsedest

nsDialogs::Show
FunctionEnd

Function Browsedest
nsDialogs::SelectFolderDialog "Select Destination Folder" $DOCUMENTS
Pop $OUT_FOLDER
${NSD_SetText} $DESTTEXT $OUT_FOLDER
FunctionEnd
