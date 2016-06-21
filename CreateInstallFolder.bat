rem Delete everything in Install
del /S /Q /F Install\* >nul
for /d %%i in (Install\*) do @rmdir /s /q "%%i"
mkdir Install\Collections
mkdir Install\Modules\FLExTrans\Lib
for /f %%f in ('dir /ad /b') do copy %%f\*.py Install\Modules\FLExTrans
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
mkdir Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
xcopy /s FLExTools1.2.4 Install\FLExTools1.2.4 
for /f %%f in ('dir /ad /b') do copy %%f\*.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans
copy readconfig.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
copy Utils.py Install\FLExTools1.2.4\FlexTools\Modules\FLExTrans\Lib
copy /Y subdirs.pth Install\FLExTools1.2.4\FlexTools\Modules
copy /Y FlexTrans.config Install\FLExTools1.2.4\FlexTools
copy "FLExTrans Step 1.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy "FLExTrans Step 3.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy "FLExTrans All Steps.ini" Install\FLExTools1.2.4\FlexTools\Collections
copy /Y flextools.ini Install\FLExTools1.2.4\FlexTools
copy *.t1x Install\FLExTools1.2.4\FlexTools
copy replace.dix Install\FLExTools1.2.4\FlexTools
copy stamp32.exe Install\FLExTools1.2.4\FlexTools

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

cd Install
"C:\Program Files (x86)\7-Zip\7z" a FLExToolsWithFLExTrans.zip FLExTools1.2.4
copy /Y FLExToolsWithFLExTrans.zip ..
cd ..

pause

