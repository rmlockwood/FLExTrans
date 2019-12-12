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
