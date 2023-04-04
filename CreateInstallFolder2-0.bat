SET FLEXTRANS_VERSION=3.8
SET INSTALL_FOLDER_VERSION=2.1.2
rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Delete everything in Install%INSTALL_FOLDER_VERSION%
rd /s /q Install%INSTALL_FOLDER_VERSION%

rem Now do steps to create a zip that has FLExTools FLExTrans and SenseLinker all in one file
rem mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Collections
rem mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Output
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\__icons
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\docs
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans\Lib
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config\Collections
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Output
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config\Collections
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Output

rem flextools files
xcopy flextools-%INSTALL_FOLDER_VERSION%\requirements.txt Install%INSTALL_FOLDER_VERSION%\FLExTrans 
xcopy flextools-%INSTALL_FOLDER_VERSION%\FlexTools\* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools 
xcopy /s flextools-%INSTALL_FOLDER_VERSION%\FlexTools\__icons\* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\__icons
xcopy /s flextools-%INSTALL_FOLDER_VERSION%\docs\* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\docs
rem add the FLExTrans version to the FlexTools version
py -3 updateVersion.py %INSTALL_FOLDER_VERSION% %FLEXTRANS_VERSION%
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

rem other stuff
copy /Y subdirs.pth Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules
copy stamp32.exe Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools
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
copy "Doc\Transfer Rules Tutorial\*" "Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial"
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
copy FLExTransWindowIcon.ico Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools

rem Live Rule Tester pieces
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester
mkdir Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Build\LiveRuleTester
copy LiveRuleTesterTool.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy LiveRuleTester.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy UpArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools
copy DownArrow.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools
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
copy Light_green_check.png Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools   
copy Red_x.png             Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools             
copy Yellow_triangle.png   Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools    

rem Paratext Import/Export Tools
copy ImportFromParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ExportToParatext.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
copy ParatextChapSelectionDlg.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ChapterSelection.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem Settings tool
copy ComboBox.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools\Modules\FLExTrans\lib
copy SettingsGUI.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans

rem Apertium files
copy Apertium4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools

rem Make for Windows files
copy Make4Windows\*.* Install%INSTALL_FOLDER_VERSION%\FLExTrans\FLExTools

rem Other Tools
copy CleanFiles.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\FlexTools\Modules\FLExTrans
rem copy SetWorkingProject.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\German-Swedish\Config
rem copy SetWorkingProject.py Install%INSTALL_FOLDER_VERSION%\FLExTrans\WorkProjects\TemplateProject\Config

SET ADD_ON_ZIP_FILE=AddOnsForXMLmind%FLEXTRANS_VERSION%.zip
cd XXEaddon
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumDictionaryXMLmind
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumInterchunkXMLmind
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumPostchunkXMLmind 
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumTransferXMLmind  
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% FLExTransTestbedXMLmind  
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% FLExTransReplDictionaryXMLmind  

copy /Y %ADD_ON_ZIP_FILE% ..
copy /Y %ADD_ON_ZIP_FILE% ..\"previous versions"
del %ADD_ON_ZIP_FILE%
cd ..

SET ZIP_FILE=FLExToolsWithFLExTrans%FLEXTRANS_VERSION%.zip
cd Install%INSTALL_FOLDER_VERSION%
"%SEVENZ_PATH%"\7z a %ZIP_FILE% FLExTrans
copy /Y %ZIP_FILE% ..
copy /Y %ZIP_FILE% ..\"previous versions"
del %ZIP_FILE%
cd ..

pause

