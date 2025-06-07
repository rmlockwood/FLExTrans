SET FLEXTRANS_VERSION=3.13.1

rem It doesn't matter so much what this next version # is, 1) we get requirements.txt from it. So this folder, with flextools- prepended, has to exist
rem  2) we create a folder named this in the install
SET INSTALL_FOLDER_VERSION=2.2.1

rem User interface language codes
set LANG_CODES=de es

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
    set translations=    %modulesflextrans%\translations

rem Create the folder structure
mkdir %toolsflextools%
mkdir %flextransdoc%
mkdir %sampleproject%
mkdir %flextranslib%
mkdir %translations%

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
echo mixpanel >> %flextransfolder%\requirements.txt
echo PyQt5==5.15.9 >> %flextransfolder%\requirements.txt
echo regex >> %flextransfolder%\requirements.txt
echo wildebeest-nlp >> %flextransfolder%\requirements.txt
echo pygetwindow >> %flextransfolder%\requirements.txt

rem special flextrans stub files for flextools plus settings tool to top FlexTools folder
copy Dev\TopLevel\*.py %flextoolsfolder%

rem sub directory paths file to Modules
copy /Y subdirs.pth %flextoolsmodules%

rem copy all module code files
copy Dev\Modules\*.py %modulesflextrans%

rem copy all shared code files
copy Dev\Lib\*.py %flextranslib%

rem copy all window ui code files
copy Dev\Lib\Windows\*.py %flextranslib%

rem copy compiled translation files
copy Dev\CompiledTranslations\*.qm %translations%
pause
rem UI resources and supporting executables to Tools
copy Tools\* %toolsflextools%

rem Copy Apertium and Make tool files
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

rem Zip XXE AddOns
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

setlocal enabledelayedexpansion

rem List of language codes
set LANG_CODES=de es

for %%L in (%LANG_CODES%) do (

    cd translations\%%L
    set "ADD_ON_ZIP_FILE_LANG=AddOnsForXMLmind_%%L%FLEXTRANS_VERSION%.zip"
    7z a "!ADD_ON_ZIP_FILE_LANG!" ApertiumTransferXMLmind

    copy /Y "!ADD_ON_ZIP_FILE_LANG!" ..\..\..
    copy /Y "!ADD_ON_ZIP_FILE_LANG!" ..\..\..\"previous versions"
    del "!ADD_ON_ZIP_FILE_LANG!"
    cd ..\..
)
endlocal
cd ..

rem Zip the FlexTools folder
SET ZIP_FILE=FLExToolsWithFLExTrans%FLEXTRANS_VERSION%.zip
cd Install%INSTALL_FOLDER_VERSION%
7z a %ZIP_FILE% FLExTrans
copy /Y %ZIP_FILE% ..
copy /Y %ZIP_FILE% ..\"previous versions"
del %ZIP_FILE%
cd ..

rem Zip the HermitCrap tools
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
