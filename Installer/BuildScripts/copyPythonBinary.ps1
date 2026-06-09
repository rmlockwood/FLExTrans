$URL = "https://www.python.org/ftp/python/3.13.12/python-3.13.12-amd64.exe"
$PTH = "c:\FLExTrans\python-3.13.12-amd64.exe"
Invoke-WebRequest -URI $URL -OutFile $PTH