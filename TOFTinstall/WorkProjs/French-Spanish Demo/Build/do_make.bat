set DICTIONARY_PATH=..\Output\bilingual.dix
set SOURCE_PATH=source_text-aper.txt
set TARGET_PATH=target_text-aper.txt
set FLEXTOOLS_PATH=..\..\..\FlexTools\Tools
set PATH=""
cd "C:\Users\rlboo\Documents\FLExTrans\WorkProjects\French-Spanish Demo\Build"
"C:\Users\rlboo\Documents\FLExTrans\FlexTools\Tools\make.exe" 2>"apertium_error.txt"
