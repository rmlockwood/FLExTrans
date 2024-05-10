SET FLEXTRANS_VERSION=3.10.2
rem It doesn't matter so much what this next version # is, 1) we get requirements.txt from it. So this folder, with flextools- prepended, has to exist
rem  2) we create a folder named this in the install
SET INSTALL_FOLDER_VERSION=2.2.1
rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Create the folder structure 
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib

rem Create identical folder structures for two work project folders
set workprojects=Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects

for %%d in (German-Swedish TemplateProject) do (
    mkdir %workprojects%\%%d\Build
    mkdir %workprojects%\%%d\Build\LiveRuleTester
    mkdir %workprojects%\%%d\Config\Collections
    mkdir %workprojects%\%%d\Output
	
	rem copy makefiles
	copy Makefile %workprojects%\%%d\Build
	copy Makefile.advanced %workprojects%\%%d\Build
	copy MakefileForLiveRuleTester %workprojects%\%%d\Build\LiveRuleTester\Makefile
	copy MakefileForLiveRuleTester.advanced %workprojects%\%%d\Build\LiveRuleTester\Makefile.advanced
)

mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Images"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Agreement"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Irregular Form"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Synthesis Self-Test"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"

rem copy the FlexTrans.config file and force it to be overwritten. 
copy FlexTrans-Swedish.config Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config\FlexTrans.config
copy FlexTrans.config Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config\FlexTrans.config

rem build Python requirements file
xcopy flextools-%INSTALL_FOLDER_VERSION%\FlexTools\scripts\requirements.txt Install%INSTALL_FOLDER_VERSION%\FLExTrans 
echo fuzzywuzzy >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt
echo Levenshtein >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt
echo PyQt5==5.15.9 >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt

rem special flextrans stub files for flextools plus settings tool
copy FLExTrans.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy Version.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy FLExTransMenu.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy FLExTransStatusbar.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy SettingsGUI.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools

rem sub directory paths to Modules
copy /Y subdirs.pth Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules

rem core models
copy CatalogTargetAffixes.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractSourceText.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy DoSynthesis.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy DoHermitCrabSynthesis.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy DoStampSynthesis.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy InsertTargetText.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RunApertium.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RunTreeTran.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem tools
copy LinkSenseTool.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy LiveRuleTesterTool.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ViewSrcTgt.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy SetUpTransferRuleGramCat.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ImportFromParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExportToParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy CleanFiles.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy GenerateParses.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RuleAssistant.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem testbed-specific modules
copy StartTestbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy EndTestbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy TestbedLogViewer.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem support code to Lib
copy readconfig.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy TextClasses.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Testbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy FTPaths.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy TestbedValidator.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy CreateApertiumRules.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib

rem dialog code (generated from .ui files) to Lib
copy MyTableView.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Linker.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy LiveRuleTester.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy TestbedLog.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy RuleCatsAndAttribs.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy ParatextChapSelectionDlg.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy SrcTgtViewer.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ChapterSelection.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ComboBox.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\lib
copy OverWriteTestDlg.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem UI resources
copy FLExTransWindowIcon.ico Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy UpArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy DownArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy Light_green_check.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy Red_x.png             Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools       
copy Yellow_triangle.png   Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

rem support programs
copy stamp64.exe Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
copy treetran.exe Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
copy Apertium4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy Make4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

rem Documentation
copy Doc\*.htm "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation"
copy Doc\Images\* "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Images"
copy "Doc\Agreement\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Agreement"
copy "Doc\Irregular Form\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Irregular Form"
copy "Doc\Synthesis Self-Test\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Synthesis Self-Test"
xcopy "Doc\Transfer Rules Tutorial\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial" /s /e

rem SampleProjects
copy "Sample Projects\German-FLExTrans-Sample*.fwbackup" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"
copy "Sample Projects\Swedish-FLExTrans-Sample*.fwbackup" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"

SET ADD_ON_ZIP_FILE=AddOnsForXMLmind%FLEXTRANS_VERSION%.zip
cd XXEaddon
7z a %ADD_ON_ZIP_FILE% ApertiumDictionaryXMLmind
7z a %ADD_ON_ZIP_FILE% ApertiumInterchunkXMLmind
7z a %ADD_ON_ZIP_FILE% ApertiumPostchunkXMLmind 
7z a %ADD_ON_ZIP_FILE% ApertiumTransferXMLmind  
7z a %ADD_ON_ZIP_FILE% FLExTransTestbedXMLmind  
7z a %ADD_ON_ZIP_FILE% FLExTransReplDictionaryXMLmind  

copy /Y %ADD_ON_ZIP_FILE% ..
copy /Y %ADD_ON_ZIP_FILE% ..\"previous versions"
del %ADD_ON_ZIP_FILE%
cd ..

SET ZIP_FILE=FLExToolsWithFLExTrans%FLEXTRANS_VERSION%.zip
cd Install%INSTALL_FOLDER_VERSION%
7z a %ZIP_FILE% FLExTrans
copy /Y %ZIP_FILE% ..
copy /Y %ZIP_FILE% ..\"previous versions"
del %ZIP_FILE%
cd ..

SET HC_ZIP_FILE=HermitCrabTools%FLEXTRANS_VERSION%.zip
cd HermitCrabSynthesis
7z a %HC_ZIP_FILE% *
copy /Y %HC_ZIP_FILE% ..
copy /Y %HC_ZIP_FILE% ..\"previous versions"
del %HC_ZIP_FILE%
cd ..

if %COMPUTERNAME% == RONS-XPS (
  cd C:\Data\Flextrans\Installer
  "C:\Program Files (x86)\NSIS\Bin\makensis.exe" -DGIT_FOLDER=C:\Users\rlboo\GitHub\FLExTrans -DBUILD_NUM=99 -DRESOURCE_FOLDER=c:\data\FLExTrans\installer FLExTrans-installer.nsi
  cd C:\Users\rlboo\GitHub\FLExTrans
  pause
) else (
  echo listing the FLExTrans folder:
  dir c:\FLExTrans
  echo calling makensis now ...
  "C:\Program Files (x86)\NSIS\Bin\makensis" -V4 -DGIT_FOLDER=. -DBUILD_NUM=%BUILD_NUMBER% -DRESOURCE_FOLDER=c:\FLExTrans FLExTrans-installer.nsi
  sign FLExTrans%FLEXTRANS_VERSION%.exe
)

