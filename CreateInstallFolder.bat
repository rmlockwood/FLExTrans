if exist Install (
    rem delete contents
    rmdir /s /q Install\Modules\Lib
    rmdir /s /q Install\Modules\FLExTrans
    rmdir /s /q Install\Modules
    rmdir /s /q Install\Collections
    rmdir /s /q Install
)
mkdir Install                  
mkdir Install\Collections
mkdir Install\Modules
mkdir Install\Modules\FLExTrans
mkdir Install\Modules\FLExTrans\Lib
for /f %%f in ('dir /ad /b') do copy %%f\*.py Install\Modules\FLExTrans
copy readconfig.py Install\Modules\FLExTrans\Lib
copy Utils.py Install\Modules\FLExTrans\Lib
copy subdirs.pth Install\Modules
copy FlexTrans.config Install
copy "FLExTrans Step 1.ini" Install\Collections
copy "FLExTrans Step 3.ini" Install\Collections
copy flextools.ini Install
copy *.t1x Install
copy replace.dix Install
copy stamp32.exe Install
cd Install
"C:\Program Files (x86)\7-Zip\7z" a FlexTrans.zip Modules Collections *.config *.ini *.t1x *.dix stamp32.exe
copy /Y FlexTrans.zip ..
cd ..
pause

