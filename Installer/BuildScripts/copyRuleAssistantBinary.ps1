$URL = "https://software.sil.org/downloads/r/flextrans/FLExTransRuleAssistant-setup.exe"
$PTH = "c:\FLExTrans\Installer\FLExTransRuleAssistant-setup.exe"
Invoke-WebRequest -URI $URL -OutFile $PTH