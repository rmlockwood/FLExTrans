rem Delete everything in Install
del /S /Q /F Install\* >nul
for /d %%i in (Install\*) do @rmdir /s /q "%%i"
mkdir Install\Collections
mkdir Install\Modules\FLExTrans\Lib
copy CatalogTargetPrefixes.py Install\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install\Modules\FLExTrans
copy ExtractSourceText.py Install\Modules\FLExTrans
copy ExtractTargetLexicon.py Install\Modules\FLExTrans
copy InsertTargetText.py Install\Modules\FLExTrans
copy Sleep.py Install\Modules\FLExTrans
copy readconfig.py Install\Modules\FLExTrans\Lib
copy Utils.py Install\Modules\FLExTrans\Lib
copy subdirs.pth Install\Modules
copy FlexTrans.config Install
copy "FLExTrans Step 1.ini" Install\Collections
copy "FLExTrans Step 3.ini" Install\Collections
copy "FlexTrans All Steps.ini" Install\Collections
copy flextools.ini Install
copy *.t1x Install
copy replace.dix Install
copy stamp32.exe Install
cd Install
"C:\Program Files (x86)\7-Zip\7z" a FlexTrans.zip Modules Collections *.config *.ini *.t1x *.dix stamp32.exe
copy /Y FlexTrans.zip ..
cd ..

rem Now do steps to create a zip that has FLExTools FLExTrans and SenseLinker all in one file
mkdir Install\FLExTools1.2.4\FlexTools\Output
mkdir Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
xcopy /s FLExTools1.2.4 Install\FLExTools1.2.4 
copy CatalogTargetPrefixes.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy ConvertTextToSTAMPformat.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy ExtractBilingualLexicon.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy ExtractSourceText.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy ExtractTargetLexicon.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy InsertTargetText.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy Sleep.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy readconfig.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
copy MyTableView.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
copy /Y subdirs.pth Install\FLExTools1.2.4\FlexTools\Modules
copy /Y FlexTrans.config Install\FLExTools1.2.4\FlexTools
copy "FLExTrans Step 1.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy "FLExTrans Step 3.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy "FLExTrans All Steps.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy /Y flextools.ini Install\FLExTools1.2.4\FlexTools
copy transfer_rules.t1x Install\FLExTools1.2.4\FlexTools\Output
copy replace.dix Install\FLExTools1.2.4\FlexTools\Output
copy stamp32.exe Install\FLExTools1.2.4\FlexTools
copy VirtualMachineFiles\do_make.sh Install\FLExTools1.2.4\FlexTools\Output
copy VirtualMachineFiles\do_make_direct.sh Install\FLExTools1.2.4\FlexTools\Output
copy VirtualMachineFiles\crontab.txt Install\FLExTools1.2.4\FlexTools\Output
copy VirtualMachineFiles\ForXXE\Makefile Install\FLExTools1.2.4\FlexTools\Output
copy VirtualMachineFiles\ForXXE\fix.py Install\FLExTools1.2.4\FlexTools\Output
copy VirtualMachineFiles\setup.sh Install\FLExTools1.2.4\FlexTools\Output

rem Documentation
mkdir "Install\FLExTools1.2.4\FLExTrans Documentation"
mkdir "Install\FLExTools1.2.4\FLExTrans Documentation\Images"
mkdir "Install\FLExTools1.2.4\FLExTrans Documentation\Transfer Rules Tutorial"
copy Doc\*.htm "Install\FLExTools1.2.4\FLExTrans Documentation"
copy Doc\Images\* "Install\FLExTools1.2.4\FLExTrans Documentation\Images"
copy "Doc\Transfer Rules Tutorial\*" "Install\FLExTools1.2.4\FLExTrans Documentation\Transfer Rules Tutorial"

rem Sample projects
mkdir "Install\FLExTools1.2.4\Sample Projects"
copy "Sample Projects\German-FLExTrans-Sample 2016-10-19 2109.fwbackup" "Install\FLExTools1.2.4\Sample Projects"
copy "Sample Projects\Swedish-FLExTrans-Sample 2016-10-19 2110.fwbackup" "Install\FLExTools1.2.4\Sample Projects"

rem Sense Linker pieces
mkdir Install\FLExTools1.2.4\Python27.NET\FW8\PyQt4  
mkdir Install\FLExTools1.2.4\Python27.NET\FW8\Levenshtein  
mkdir Install\FLExTools1.2.4\Python27.NET\FW8\fuzzywuzzy  
copy LinkSenseTool.py Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans
copy Linker.py Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans\Lib
copy Linker.ui Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans\Lib
copy "FLExTrans Sense Linker.ini" Install\FLExTools1.2.4\FLExTools\Collections
copy Qt*.* Install\FLExTools1.2.4\Python27.NET\FW8\PyQt4
copy __init__.py Install\FLExTools1.2.4\Python27.NET\FW8\PyQt4
copy fuzzywuzzy Install\FLExTools1.2.4\Python27.NET\FW8\fuzzywuzzy
copy Levenshtein Install\FLExTools1.2.4\Python27.NET\FW8\Levenshtein
copy sip.pyd Install\FLExTools1.2.4\Python27.NET\FW8

rem Live Rule Tester pieces
mkdir Install\FLExTools1.2.4\FlexTools\Output\LiveRuleTester
copy LiveRuleTesterTool.py Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans
copy LiveRuleTester.py Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans\Lib
copy LiveRuleTester.ui Install\FLExTools1.2.4\FLExTools\Modules\FLExTrans\Lib
copy "FlexTrans Live Rule Tester.ini" Install\FLExTools1.2.4\FLExTools\Collections
copy UpArrow.png Install\FLExTools1.2.4\FLExTools
copy DownArrow.png Install\FLExTools1.2.4\FLExTools
copy VirtualMachineFiles\ForLiveRuleTester\do_make.sh Install\FLExTools1.2.4\FlexTools\Output\LiveRuleTester
copy VirtualMachineFiles\ForXXE\Makefile Install\FLExTools1.2.4\FlexTools\Output\LiveRuleTester
copy VirtualMachineFiles\ForXXE\fix.py Install\FLExTools1.2.4\FlexTools\Output\LiveRuleTester

cd Install
"C:\Program Files (x86)\7-Zip\7z" a FLExToolsWithFLExTrans.zip FLExTools1.2.4
copy /Y FLExToolsWithFLExTrans.zip ..
cd ..

pause

