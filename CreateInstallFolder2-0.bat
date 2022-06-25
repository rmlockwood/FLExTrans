SET FLEXTRANS_VERSION=3.5.2
rem Delete everything in Install2.1.1
rd /s /q Install2.1.1

rem Delete everything in Install2.1.1
rd /s /q Install2.1.1

rem Now do steps to create a zip that has FLExTools FLExTrans and SenseLinker all in one file
rem mkdir Install2.1.1\FLExTrans\FlexTools\Collections
rem mkdir Install2.1.1\FLExTrans\FlexTools\Output
mkdir Install2.1.1\FLExTrans\FlexTools\__icons
mkdir Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
mkdir Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans\Lib
mkdir Install2.1.1\FLExTrans\WorkProjects
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Build
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Config
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Config\Collections
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Output

xcopy FlexTools2.1.1\requirements.txt Install2.1.1\FLExTrans 
xcopy FlexTools2.1.1\FlexTools\* Install2.1.1\FLExTrans\FlexTools 
xcopy /s FlexTools2.1.1\FlexTools\__icons\* Install2.1.1\FLExTrans\FlexTools\__icons
echo fuzzywuzzy >> Install2.1.1\FLExTrans\requirements.txt
echo Levenshtein >> Install2.1.1\FLExTrans\requirements.txt
echo PyQt5==5.14 >> Install2.1.1\FLExTrans\requirements.txt
echo PyQtWebEngine==5.14 >> Install2.1.1\FLExTrans\requirements.txt

rem core models
copy CatalogTargetPrefixes.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractSourceText.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy ExtractTargetLexicon.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy InsertTargetText.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy RunApertium.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans
copy RunTreeTran.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans

rem libraries
copy readconfig.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans\Lib
copy MyTableView.py Install2.1.1\FLExTrans\FlexTools\Modules\FLExTrans\Lib

rem other stuff
copy /Y subdirs.pth Install2.1.1\FLExTrans\FlexTools\Modules
copy stamp32.exe Install2.1.1\FLExTrans\FlexTools
copy Makefile Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Build
copy FlexTools.vbs Install2.1.1\FLExTrans\WorkProjects\German-Swedish
copy source_text.txt Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Output

rem Documentation
mkdir "Install2.1.1\FLExTrans\FLExTrans Documentation"
mkdir "Install2.1.1\FLExTrans\FLExTrans Documentation\Images"
mkdir "Install2.1.1\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial"
mkdir "Install2.1.1\FLExTrans\FLExTrans Documentation\Agreement"
mkdir "Install2.1.1\FLExTrans\FLExTrans Documentation\Irregular Form"
copy Doc\*.htm "Install2.1.1\FLExTrans\FLExTrans Documentation"
copy Doc\Images\* "Install2.1.1\FLExTrans\FLExTrans Documentation\Images"
copy "Doc\Transfer Rules Tutorial\*" "Install2.1.1\FLExTrans\FLExTrans Documentation\Transfer Rules Tutorial"
copy "Doc\Agreement\*" "Install2.1.1\FLExTrans\FLExTrans Documentation\Agreement"
copy "Doc\Irregular Form\*" "Install2.1.1\FLExTrans\FLExTrans Documentation\Irregular Form"

rem SampleProjects
mkdir "Install2.1.1\FLExTrans\SampleProjects"
copy "Sample Projects\German-FLExTrans-Sample 2016-10-19 2109.fwbackup" "Install2.1.1\FLExTrans\SampleProjects"
copy "Sample Projects\Swedish-FLExTrans-Sample 2016-10-19 2110.fwbackup" "Install2.1.1\FLExTrans\SampleProjects"

rem Sense Linker pieces
copy LinkSenseTool.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy Linker.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem Live Rule Tester pieces
mkdir Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester
copy LiveRuleTesterTool.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy LiveRuleTester.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy UpArrow.png Install2.1.1\FLExTrans\FLExTools
copy DownArrow.png Install2.1.1\FLExTrans\FLExTools
copy MakefileForLiveRuleTester Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Build\LiveRuleTester\Makefile

rem View Source-Target pieces
copy ViewSrcTgt.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy SrcTgtViewer.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem SetUp Gramm Categories pieces
copy SetUpTransferRuleGramCat.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans

rem Testbed pieces
copy TestbedValidator.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy StartTestbed.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy EndTestbed.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy OverWriteTestDlg.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy TestbedLogViewer.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy TestbedLog.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy Light_green_check.png Install2.1.1\FLExTrans\FLExTools   
copy Red_x.png             Install2.1.1\FLExTrans\FLExTools             
copy Yellow_triangle.png   Install2.1.1\FLExTrans\FLExTools    

rem Paratext Import/Export Tools
copy ImportFromParatext.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy ExportToParatext.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy ParatextChapSelectionDlg.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ChapterSelection.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib

rem Settings tool
copy Settings.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\Lib
copy ComboBox.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans\lib
copy SettingsGUI.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans

rem Apertium files
copy Apertium4Windows\*.* Install2.1.1\FLExTrans\FLExTools

rem Make for Windows files
copy Make4Windows\*.* Install2.1.1\FLExTrans\FLExTools

rem Other Tools
copy CleanFiles.py Install2.1.1\FLExTrans\FLExTools\Modules\FLExTrans
copy SetWorkingProject.py Install2.1.1\FLExTrans\WorkProjects\German-Swedish\Build

SET ADD_ON_ZIP_FILE=AddOnsForXMLmind%FLEXTRANS_VERSION%.zip
cd XXEaddon
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumDictionaryXMLmind
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumInterchunkXMLmind
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumPostchunkXMLmind 
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% ApertiumTransferXMLmind  
"%SEVENZ_PATH%"\7z a %ADD_ON_ZIP_FILE% FLExTransTestbedXMLmind  

copy /Y %ADD_ON_ZIP_FILE% ..
copy /Y %ADD_ON_ZIP_FILE% ..\"previous versions"
del %ADD_ON_ZIP_FILE%
cd ..

SET ZIP_FILE=FLExToolsWithFLExTrans%FLEXTRANS_VERSION%.zip
cd Install2.1.1
"%SEVENZ_PATH%"\7z a %ZIP_FILE% FLExTrans
copy /Y %ZIP_FILE% ..
copy /Y %ZIP_FILE% ..\"previous versions"
del %ZIP_FILE%
cd ..

pause

