Set WshShell = CreateObject("WScript.Shell")

PYTHON = "py -3.11"
CMD = "cmd.exe /k " & PYTHON & " ..\..\FlexTools\FLExTrans.py .\Config\flextools.ini"

WshShell.Run CMD, 1, False

Set WshShell = Nothing
