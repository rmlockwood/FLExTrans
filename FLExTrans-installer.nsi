!include StrRep.nsh
!include ReplaceInFile.nsh

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "FLExTrans"
!define PRODUCT_PUBLISHER "SIL International"
!define PRODUCT_WEB_SITE "https://software.sil.org/flextrans"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_VERSION "3.6.4"

!define PRODUCT_ZIP_FILE "FLExToolsWithFLExTrans${PRODUCT_VERSION}.zip"
!define ADD_ON_ZIP_FILE "AddOnsForXMLmind${PRODUCT_VERSION}.zip"
!define FLEX_TOOLS_WITH_VERSION "FLExTrans"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
#; Directory page
Page custom nsDialogsPage
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
Icon "${GIT_FOLDER}\FLExTransInstallIcon32.ico"
Name "${PRODUCT_NAME}"

OutFile "${PRODUCT_NAME}${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\FLExTrans_Installer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section -Prerequisites
InitPluginsDir

  SetOutPath "$INSTDIR\install_files"
  #Connect to apertium
  #File "Command2.sh"
  #ExecWait "bash -ExecutionPolicy Bypass -WindowStyle Hidden -File $INSTDIR\install_files\Command2.sh -FFFeatureOff"

  # Install python 3.7.4
  MessageBox MB_YESNO "Install Python 3.7.4? $\nIMPORTANT! Check the box: 'Add Python 3.7 to Path'. $\nUse the 'Install now' option" /SD IDYES IDNO endPythonSync
        File "python-3.7.4-amd64.exe"
        ExecWait "$INSTDIR\install_files\python-3.7.4-amd64.exe"
        Goto endPythonSync
  endPythonSync:

  # Install Git
#  MessageBox MB_YESNO "Install Git for Windows? $\nUse the default settings." /SD IDYES IDNO endGitSync
#        File "Git-2.31.1-64-bit.exe"
#        ExecWait "$INSTDIR\install_files\Git-2.31.1-64-bit.exe"
#        Goto endGitSync
#  endGitSync:
  
  Var /GLOBAL OUT_FOLDER
  # Unzip FLExTrans to the desired folder
  # GIT_FOLDER needs to be set to your local git FLExTrans folder in the compiler settings
  File "${GIT_FOLDER}\${PRODUCT_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${PRODUCT_ZIP_FILE}" "$OUT_FOLDER"

  # Copy files users may change only if they don't already exist
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish"
  SetOverwrite off

  File "${GIT_FOLDER}\FlexTools.vbs"
  File "${GIT_FOLDER}\replace.dix"
  File "${GIT_FOLDER}\transfer_rules.t1x"
  
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject"

  File "${GIT_FOLDER}\FlexTools.vbs"
  File "${GIT_FOLDER}\replace.dix"
  File "${GIT_FOLDER}\transfer_rules.t1x"
  
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config"
  
  File "${GIT_FOLDER}\SetWorkingProject.py"
  File "${GIT_FOLDER}\FlexTrans.config"
  File "${GIT_FOLDER}\flextools.ini"
  File "${GIT_FOLDER}\FlexTools.bat"

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject\Config"
  
  File "${GIT_FOLDER}\SetWorkingProject.py"
  File "${GIT_FOLDER}\FlexTrans.config"
  File "${GIT_FOLDER}\flextools.ini"
  File "${GIT_FOLDER}\FlexTools.bat"

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections"
  File "${GIT_FOLDER}\All Steps.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"

  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\TemplateProject\Config\Collections"
  File "${GIT_FOLDER}\All Steps.ini"
  File "${GIT_FOLDER}\Run Testbed.ini"
  File "${GIT_FOLDER}\Tools.ini"
  SetOverwrite on

  # Rename modules in the .ini (for old installs)
  !insertmacro _ReplaceInFile "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections\FLExTrans All Steps.ini" "FLExTrans.Extract Target Lexicon" "FLExTrans.Synthesize Text with STAMP"
  !insertmacro _ReplaceInFile "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections\FLExTrans All Steps.ini" "FLExTrans.Catalog Target Prefixes" "FLExTrans.Catalog Target Affixes"
  !insertmacro _ReplaceInFile "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections\FLExTrans Run Testbed.ini" "FLExTrans.Extract Target Lexicon" "FLExTrans.Synthesize Text with STAMP"
  !insertmacro _ReplaceInFile "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections\FLExTrans Run Testbed.ini" "FLExTrans.Catalog Target Prefixes" "FLExTrans.Catalog Target Affixes"
  !insertmacro _ReplaceInFile "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\WorkProjects\German-Swedish\Config\Collections\FLExTrans Tools.ini" "FLExTrans.Set Up Transfer Rule Grammatical Categories" "FLExTrans.Set Up Transfer Rule Categories and Attributes"

  # Attempt to run pip to install FlexTools dependencies
  !define mycmd '"$LocalAppdata\Programs\Python\Python37\Scripts\pip3.exe" install -r "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\requirements.txt"'
  SetOutPath "$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}"
  File "${GIT_FOLDER}\Command.bat"
  # assume pip3 got installed in the default folder under %appdata%. If it did pip will run successfully the first time it gets installed.
  ExecWait '${mycmd}'
  # if the above failed, call the command.bat to do the same thing, but if this was the first time run, pip won't be in the path.
  IfErrors 0 +2
        Exec '"$OUT_FOLDER\${FLEX_TOOLS_WITH_VERSION}\Command.bat"'

  # Install XMLmind
  SetOutPath "$INSTDIR\install_files"
  MessageBox MB_YESNO "Install XMLmind?" /SD IDYES IDNO endXXeSync
        File "xxe-perso-8_2_0-setup.exe"
        ExecWait "$INSTDIR\install_files\xxe-perso-8_2_0-setup.exe /SILENT"
        Goto endXXeSync
  endXXeSync:
  File "${GIT_FOLDER}\${ADD_ON_ZIP_FILE}"
  nsisunz::Unzip "$INSTDIR\install_files\${ADD_ON_ZIP_FILE}" "$APPDATA\XMLmind\XMLEditor8\addon"
  SetOutPath "$INSTDIR"
  #Delete $DOCUMENTS\FLExTools2.0\Command.bat
  RMDir /r "$INSTDIR\install_files"
SectionEnd


Section "MainSection" SEC01

SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}${PRODUCT_VERSION}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\FLExTools20WithFLExTrans.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\FLExTools20WithFLExTrans.exe"
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
Var Dialog
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
