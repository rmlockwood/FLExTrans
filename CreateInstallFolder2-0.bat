rem Delete everything in Install2.0
rd /s /q Install2.0

rem Delete everything in Install2.0
rd /s /q Install2.0

rem Now do steps to create a zip that has FLExTools FLExTrans and SenseLinker all in one file
mkdir Install2.0\FlexTools2.0\FlexTools\Collections
mkdir Install2.0\FlexTools2.0\FlexTools\Output
mkdir Install2.0\FlexTools2.0\FlexTools\__icons
mkdir Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
mkdir Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans\Lib

xcopy FlexTools2.0\* Install2.0\FlexTools2.0 
xcopy FlexTools2.0\FlexTools\* Install2.0\FlexTools2.0\FlexTools 
xcopy /s FlexTools2.0\FlexTools\__icons\* Install2.0\FlexTools2.0\FlexTools\__icons
echo fuzzywuzzy >> Install2.0\FlexTools2.0\requirements.txt
echo Levenshtein >> Install2.0\FlexTools2.0\requirements.txt
echo PyQt5 >> Install2.0\FlexTools2.0\requirements.txt
copy install_flextools_libs.bat Install2.0\FlexTools2.0

rem core models
copy CatalogTargetPrefixes.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy ExtractSourceText.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy ExtractTargetLexicon.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy InsertTargetText.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy RunApertium.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans
copy RunTreeTran.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans

rem libraries
copy readconfig.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans\Lib
copy MyTableView.py Install2.0\FlexTools2.0\FlexTools\Modules\FLExTrans\Lib

rem other stuff
copy /Y subdirs.pth Install2.0\FlexTools2.0\FlexTools\Modules
copy /Y FlexTrans.config Install2.0\FlexTools2.0\FlexTools
copy "FlexTrans All Steps.ini" Install2.0\FlexTools2.0\FlexTools\Collections
copy "FlexTrans Run Testbed.ini" Install2.0\FlexTools2.0\FlexTools\Collections
copy "FlexTrans Tools.ini" Install2.0\FlexTools2.0\FlexTools\Collections
copy /Y flextools.ini Install2.0\FlexTools2.0\FlexTools
copy transfer_rules.t1x Install2.0\FlexTools2.0\FlexTools\Output
copy replace.dix Install2.0\FlexTools2.0\FlexTools\Output
copy stamp32.exe Install2.0\FlexTools2.0\FlexTools
copy VirtualMachineFiles\do_make_direct.sh Install2.0\FlexTools2.0\FlexTools\Output
copy VirtualMachineFiles\ForXXE\Makefile Install2.0\FlexTools2.0\FlexTools\Output
copy VirtualMachineFiles\ForXXE\fix.py Install2.0\FlexTools2.0\FlexTools\Output

rem Documentation
mkdir "Install2.0\FlexTools2.0\FLExTrans Documentation"
mkdir "Install2.0\FlexTools2.0\FLExTrans Documentation\Images"
mkdir "Install2.0\FlexTools2.0\FLExTrans Documentation\Transfer Rules Tutorial"
copy Doc\*.htm "Install2.0\FlexTools2.0\FLExTrans Documentation"
copy Doc\Images\* "Install2.0\FlexTools2.0\FLExTrans Documentation\Images"
copy "Doc\Transfer Rules Tutorial\*" "Install2.0\FlexTools2.0\FLExTrans Documentation\Transfer Rules Tutorial"

rem Sample projects
mkdir "Install2.0\FlexTools2.0\Sample Projects"
copy "Sample Projects\German-FLExTrans-Sample 2016-10-19 2109.fwbackup" "Install2.0\FlexTools2.0\Sample Projects"
copy "Sample Projects\Swedish-FLExTrans-Sample 2016-10-19 2110.fwbackup" "Install2.0\FlexTools2.0\Sample Projects"

rem Sense Linker pieces
copy LinkSenseTool.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy Linker.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy Linker.ui Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
rem mkdir Install2.0\FlexTools2.0\Python27.NET\FW8\PyQt4  
rem mkdir Install2.0\FlexTools2.0\Python27.NET\FW8\Levenshtein  
rem mkdir Install2.0\FlexTools2.0\Python27.NET\FW8\fuzzywuzzy  
rem copy Qt*.* Install2.0\FlexTools2.0\Python27.NET\FW8\PyQt4
rem copy __init__.py Install2.0\FlexTools2.0\Python27.NET\FW8\PyQt4
rem copy libeay32.dll Install2.0\FlexTools2.0\Python27.NET\FW8\PyQt4
rem copy ssleay32.dll Install2.0\FlexTools2.0\Python27.NET\FW8\PyQt4
rem copy fuzzywuzzy Install2.0\FlexTools2.0\Python27.NET\FW8\fuzzywuzzy
rem copy Levenshtein Install2.0\FlexTools2.0\Python27.NET\FW8\Levenshtein
rem copy sip.pyd Install2.0\FlexTools2.0\Python27.NET\FW8

rem Live Rule Tester pieces
mkdir Install2.0\FlexTools2.0\FlexTools\Output\LiveRuleTester
copy LiveRuleTesterTool.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy LiveRuleTester.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy LiveRuleTester.ui Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy UpArrow.png Install2.0\FlexTools2.0\FLExTools
copy DownArrow.png Install2.0\FlexTools2.0\FLExTools
copy VirtualMachineFiles\ForLiveRuleTester\do_make.sh Install2.0\FlexTools2.0\FlexTools\Output\LiveRuleTester
copy VirtualMachineFiles\ForXXE\Makefile Install2.0\FlexTools2.0\FlexTools\Output\LiveRuleTester
copy VirtualMachineFiles\ForXXE\fix.py Install2.0\FlexTools2.0\FlexTools\Output\LiveRuleTester

rem View Source-Target pieces
copy ViewSrcTgt.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy SrcTgtViewer.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy SrcTgtViewer.ui Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib

rem SetUp Gramm Categories pieces
copy SetUpTransferRuleGramCat.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans

rem Testbed pieces
copy TestbedValidator.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy StartTestbed.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy EndTestbed.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy OverWriteTestDlg.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy OverWriteTestDlg.ui Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy TestbedLogViewer.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans
copy TestbedLog.py Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy TestbedLog.ui Install2.0\FlexTools2.0\FLExTools\Modules\FLExTrans\Lib
copy Light_green_check.png Install2.0\FlexTools2.0\FLExTools   
copy Red_x.png             Install2.0\FlexTools2.0\FLExTools             
copy Yellow_triangle.png   Install2.0\FlexTools2.0\FLExTools    

cd Install2.0
"%SEVENZ_PATH%"\7z a FLExTools20WithFLExTrans.zip FlexTools2.0
copy /Y FLExTools20WithFLExTrans.zip ..
cd ..

pause

