' Run the FlexTools application
'
' The '0' parameter to Run hides the console window.

Set WshShell = CreateObject("WScript.Shell")

PYTHON = "py -3.11"

WshShell.Run PYTHON & " ..\..\FlexTools\FLExTrans.py .\Config\flextools.ini", 0, False

WshShell = Null
