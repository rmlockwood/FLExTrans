set DICTIONARY_PATH=..\Output\bilingual.dix
set SOURCE_PATH=source_text-aper.txt
set TARGET_PATH=target_text-aper.txt
set FLEXTOOLS_PATH=..\..\..\FlexTools\Tools
set PATH=""
C:
cd "C:\Data\FLExTrans\Dev\Test Projects\WorkProjects\Ejagham-Ejagham-Sample\Build"
"C:\Data\FLExTrans\Dev\Test Projects\FlexTools\Tools\make.exe" 2>"apertium_error.txt"
