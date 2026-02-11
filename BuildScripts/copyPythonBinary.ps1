$URL = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
$PTH = "c:\FLExTrans\python-3.11.7-amd64.exe"
Invoke-WebRequest -URI $URL -OutFile $PTH