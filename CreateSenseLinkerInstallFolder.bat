if exist LinkerInstall (
    rem delete contents
    rmdir /s /q LinkerInstall\Python27.NET\FW8\PyQt4
    rmdir /s /q LinkerInstall\Python27.NET\FW8
    rmdir /s /q LinkerInstall\Python27.NET
    rmdir /s /q LinkerInstall\FLExTools\Modules\FLExTrans\Lib
    rmdir /s /q LinkerInstall\FLExTools\Modules\FLExTrans
    rmdir /s /q LinkerInstall\FLExTools\Modules
    rmdir /s /q LinkerInstall\FLExTools
    rmdir /s /q LinkerInstall\FLExTools\Collections
    rmdir /s /q LinkerInstall
)
mkdir LinkerInstall                         
mkdir LinkerInstall\Python27.NET            
mkdir LinkerInstall\Python27.NET\FW8        
mkdir LinkerInstall\Python27.NET\FW8\PyQt4  
mkdir LinkerInstall\FLExTools                 
mkdir LinkerInstall\FLExTools\Modules                 
mkdir LinkerInstall\FLExTools\Modules\FLExTrans       
mkdir LinkerInstall\FLExTools\Modules\FLExTrans\Lib      
mkdir LinkerInstall\FLExTools\Collections             
copy LinkSenseTool.py LinkerInstall\FLExTools\Modules\FLExTrans
copy Linker.py LinkerInstall\FLExTools\Modules\FLExTrans\Lib
copy Linker.ui LinkerInstall\FLExTools\Modules\FLExTrans\Lib
copy "FLExTrans Sense Linker.ini" LinkerInstall\FLExTools\Collections
copy Qt*.* LinkerInstall\Python27.NET\FW8\PyQt4
copy __init__.py LinkerInstall\Python27.NET\FW8\PyQt4
copy sip.pyd LinkerInstall\Python27.NET\FW8
cd LinkerInstall
"C:\Program Files (x86)\7-Zip\7z" a FlexTransSenseLinker.zip FLExTools Python27.NET SenseLinkerReadme.txt
copy /Y FlexTransSenseLinker.zip ..
cd ..
rem pause

