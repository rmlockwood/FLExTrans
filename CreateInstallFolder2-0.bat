SET FLEXTRANS_VERSION=3.11
rem It doesn't matter so much what this next version # is, 1) we get requirements.txt from it. So this folder, with flextools- prepended, has to exist
rem  2) we create a folder named this in the install
SET INSTALL_FOLDER_VERSION=2.2.1
rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem A second time just to be sure
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Name the folders
set flextransfolder=Install%INSTALL_FOLDER_VERSION%\FLExTrans
 set flextransdoc=  "%flextransfolder%\FLExTrans Documentation"
 set sampleproject= "%flextransfolder%\SampleFLExProjects"
 set flextoolsfolder=%flextransfolder%\FlexTools
  set toolsflextools=  %flextoolsfolder%\Tools
  set flextoolsmodules=%flextoolsfolder%\Modules
   set modulesflextrans=%flextoolsmodules%\FLExTrans
    set flextranslib=    %modulesflextrans%\Lib

rem Create the folder structure
mkdir %toolsflextools%
mkdir %flextransdoc%
mkdir %sampleproject%
mkdir %flextranslib%

rem Create identical folder structures for two work project folders
set workprojects=%flextransfolder%\WorkProjects
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

rem copy the FlexTrans.config file and force it to be overwritten.
copy FlexTrans-Swedish.config %workprojects%\German-Swedish\Config\FlexTrans.config
copy FlexTrans.config %workprojects%\TemplateProject\Config\FlexTrans.config

rem build Python requirements file
xcopy flextools-%INSTALL_FOLDER_VERSION%\FlexTools\scripts\requirements.txt %flextransfolder%
echo fuzzywuzzy >> %flextransfolder%\requirements.txt
echo Levenshtein >> %flextransfolder%\requirements.txt
echo PyQt5==5.15.9 >> %flextransfolder%\requirements.txt
echo regex >> %flextransfolder%\requirements.txt

rem special flextrans stub files for flextools plus settings tool to top FlexTools folder
copy FLExTrans.py %flextoolsfolder%
copy Version.py %flextoolsfolder%
copy FLExTransMenu.py %flextoolsfolder%
copy FLExTransStatusbar.py %flextoolsfolder%
copy SettingsGUI.py %flextoolsfolder%

rem sub directory paths file to Modules
copy /Y subdirs.pth %flextoolsmodules%

rem core models to Modules\FLExTrans
copy CatalogTargetAffixes.py %modulesflextrans%
copy ConvertTextToSTAMPformat.py %modulesflextrans%
copy ExtractBilingualLexicon.py %modulesflextrans%
copy ExtractSourceText.py %modulesflextrans%
copy DoSynthesis.py %modulesflextrans%
copy DoHermitCrabSynthesis.py %modulesflextrans%
copy DoStampSynthesis.py %modulesflextrans%
copy InsertTargetText.py %modulesflextrans%
copy RunApertium.py %modulesflextrans%
copy RunTreeTran.py %modulesflextrans%

rem tools to Modules\FLExTrans
copy LinkSenseTool.py %modulesflextrans%
copy LiveRuleTesterTool.py %modulesflextrans%
copy ViewSrcTgt.py %modulesflextrans%
copy SetUpTransferRuleGramCat.py %modulesflextrans%
copy ImportFromParatext.py %modulesflextrans%
copy ExportToParatext.py %modulesflextrans%
copy CleanFiles.py %modulesflextrans%
copy GenerateParses.py %modulesflextrans%
copy RuleAssistant.py %modulesflextrans%
copy TextInRules.py %modulesflextrans%
copy TextOutRules.py %modulesflextrans%
copy FixUpSynthText.py %modulesflextrans%
copy LinkAllSensesAsDup.py %modulesflextrans%

rem testbed-specific modules to Modules\FLExTrans
copy StartTestbed.py %modulesflextrans%
copy EndTestbed.py %modulesflextrans%
copy TestbedLogViewer.py %modulesflextrans%

rem support code to Lib
copy readconfig.py %flextranslib%
copy Utils.py %flextranslib%
copy TextClasses.py %flextranslib%
copy Testbed.py %flextranslib%
copy FTPaths.py %flextranslib%
copy TestbedValidator.py %flextranslib%
copy CreateApertiumRules.py %flextranslib%
copy TextInOutUtils.py %flextranslib%
copy TextInOut.py %flextranslib%

rem dialog code (generated from .ui files) to Lib
copy MyTableView.py %flextranslib%
copy Linker.py %flextranslib%
copy LiveRuleTester.py %flextranslib%
copy TestbedLog.py %flextranslib%
copy RuleCatsAndAttribs.py %flextranslib%
copy ParatextChapSelectionDlg.py %flextranslib%
copy SrcTgtViewer.py %flextranslib%
copy ChapterSelection.py %flextranslib%
copy ComboBox.py %flextranslib%
copy OverWriteTestDlg.py %flextranslib%

rem UI resources to Tools
copy FLExTransWindowIcon.ico %toolsflextools%
copy UpArrow.png %toolsflextools%
copy DownArrow.png %toolsflextools%
copy Light_green_check.png %toolsflextools%
copy Red_x.png             %toolsflextools%
copy Yellow_triangle.png   %toolsflextools%

rem support programs to Tools
copy stamp64.exe %toolsflextools%
copy treetran.exe %toolsflextools%
copy Apertium4Windows\*.* %toolsflextools%
copy Make4Windows\*.* %toolsflextools%

rem documentation
copy Doc\*.htm %flextransdoc%

for %%d in (Images Agreement "Irregular Form" "Synthesis Self-Test" "Transfer Rules Tutorial") do (
    mkdir %flextransdoc%\%%d
    xcopy Doc\%%d\* %flextransdoc%\%%d   /s /e
)

rem SampleProjects
copy "Sample Projects\German-FLExTrans-Sample*.fwbackup" %sampleproject%
copy "Sample Projects\Swedish-FLExTrans-Sample*.fwbackup" %sampleproject%

SET ADD_ON_ZIP_FILE=AddOnsForXMLmind%FLEXTRANS_VERSION%.zip
cd XXEaddon
7z a %ADD_ON_ZIP_FILE% ApertiumDictionaryXMLmind
7z a %ADD_ON_ZIP_FILE% ApertiumInterchunkXMLmind
7z a %ADD_ON_ZIP_FILE% ApertiumPostchunkXMLmind
7z a %ADD_ON_ZIP_FILE% ApertiumTransferXMLmind
7z a %ADD_ON_ZIP_FILE% FLExTransTestbedXMLmind
7z a %ADD_ON_ZIP_FILE% FLExTransReplDictionaryXMLmind
7z a %ADD_ON_ZIP_FILE% FLExTransRuleGeneratorXMLmind

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
