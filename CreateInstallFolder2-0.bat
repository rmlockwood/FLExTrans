SET FLEXTRANS_VERSION=3.8.1
SET INSTALL_FOLDER_VERSION=2.2.1
rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Now do steps to create a zip that has FLExTools and FLExTrans 
rem mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools\HermitCrabSynthesis\GenerateHCConfig4FLExTrans
rem mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools\HermitCrabSynthesis\HCSynthByGloss
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config\Collections
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Output
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config\Collections
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Output

rem NOT ANYMORE!
rem copy the flextools.ini file and force it to be overwritten. 
rem previously we only did this in the install script and replaced them if they didn't exit
rem but now we need to get the new settings forced. This means they will have to manually change their
rem Flex project selection
rem copy flextools.ini Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config
rem copy flextools.ini Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config

rem special flextrans stub files for flextools
copy FLExTrans.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy Version.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy FLExTransMenu.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
copy FLExTransStatusbar.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools

rem Settings tool
copy ComboBox.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\lib
copy SettingsGUI.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools

rem flextools files
xcopy flextools-%INSTALL_FOLDER_VERSION%\FlexTools\scripts\requirements.txt Install%INSTALL_FOLDER_VERSION%\FLExTrans 
echo fuzzywuzzy >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt
echo Levenshtein >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt
echo PyQt5==5.14 >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt
echo PyQtWebEngine==5.14 >> Install%INSTALL_FOLDER_VERSION%\FLExTrans\requirements.txt

rem core models
copy CatalogTargetAffixes.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractSourceText.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy DoStampSynthesis.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy InsertTargetText.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RunApertium.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RunTreeTran.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem libraries
copy readconfig.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy MyTableView.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy TextClasses.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Testbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy FTPaths.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib

rem other stuff
copy /Y subdirs.pth Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules
copy stamp64.exe Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
copy treetran.exe Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Tools
copy Makefile Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build
copy Makefile.advanced Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build
copy Makefile Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build
copy Makefile.advanced Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build
copy source_text.txt Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Output
copy source_text.txt Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Output

rem Documentation
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Images"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Agreement"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Irregular Form"
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Synthesis Self-Test"
copy Doc\*.htm "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation"
copy Doc\Images\* "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Images"
xcopy "Doc\Transfer Rules Tutorial\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial" /s /e
copy "Doc\Agreement\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Agreement"
copy "Doc\Irregular Form\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Irregular Form"
copy "Doc\Synthesis Self-Test\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Synthesis Self-Test"

rem SampleProjects
mkdir "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"
copy "Sample Projects\German-FLExTrans-Sample*.fwbackup" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"
copy "Sample Projects\Swedish-FLExTrans-Sample*.fwbackup" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\SampleFLExProjects"

rem Sense Linker pieces
copy LinkSenseTool.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy Linker.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy FLExTransWindowIcon.ico Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

rem Live Rule Tester pieces
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build\LiveRuleTester
copy LiveRuleTesterTool.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy LiveRuleTester.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy UpArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy DownArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy MakefileForLiveRuleTester Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester\Makefile
copy MakefileForLiveRuleTester Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build\LiveRuleTester\Makefile
copy MakefileForLiveRuleTester.advanced Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester\Makefile.advanced
copy MakefileForLiveRuleTester.advanced Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build\LiveRuleTester\Makefile.advanced

rem View Source-Target pieces
copy ViewSrcTgt.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy SrcTgtViewer.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem SetUp Gramm Categories pieces
copy SetUpTransferRuleGramCat.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy RuleCatsAndAttribs.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib

rem Testbed pieces
copy TestbedValidator.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy StartTestbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy EndTestbed.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy OverWriteTestDlg.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy TestbedLogViewer.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy TestbedLog.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy Light_green_check.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools
copy Red_x.png             Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools       
copy Yellow_triangle.png   Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

rem Paratext Import/Export Tools
copy ImportFromParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExportToParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ParatextChapSelectionDlg.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ChapterSelection.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem Other Tools
copy CleanFiles.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy GenerateParses.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem HermitCrab sythesis
copy DoHermitCrabSynthesis.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem Apertium files
copy Apertium4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

rem HermitCrab generate and sythesize program files
rem copy HermitCrabSynthesis\GenerateHCConfig4FLExTrans\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools\HermitCrabSynthesis\GenerateHCConfig4FLExTrans
rem copy HermitCrabSynthesis\HCSynthByGloss\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools\HermitCrabSynthesis\HCSynthByGloss

rem Make for Windows files
copy Make4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Tools

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
7z a %HC_ZIP_FILE% *.*
copy /Y %HC_ZIP_FILE% ..
copy /Y %HC_ZIP_FILE% ..\"previous versions"
del %HC_ZIP_FILE%
cd ..

if %COMPUTERNAME% == RONS-DELL-XPS (
  cd C:\Data\Flextrans\Installer
  makensis -DGIT_FOLDER=C:\Users\rlboo\GitHub\FLExTrans -DBUILD_NUM=99 -DRESOURCE_FOLDER=c:\data\FLExTrans\installer FLExTrans-installer.nsi
  cd C:\Users\rlboo\GitHub\FLExTrans
  pause
) else (
  echo listing the FLExTrans folder:
  dir c:\FLExTrans
  echo calling makensis now ...
  "C:\Program Files (x86)\NSIS\Bin\makensis" -V4 -DGIT_FOLDER=. -DBUILD_NUM=%BUILD_NUMBER% -DRESOURCE_FOLDER=c:\FLExTrans FLExTrans-installer.nsi
  sign FLExTrans%FLEXTRANS_VERSION%.exe
)

