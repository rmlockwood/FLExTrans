Python installer
----------------
If there's a new Python installer to include, here's what you do:
-Edit the file GitHub\FLExTrans\copyPythonBinary.ps1 with the new Python version (2 places)
-Verify the url is valid
-The script will copy it from there to the TeamCity server FLExTrans folder for the NSI installer to find
-Copy the exe locally for doing local installer builds (Installer folder)

Rule Assistant installer
------------------------
If there's a new Rule Assistant installer to include, here's what you do:
-Rename the installer to the standard name: FLExTransRuleAssistant-setup.exe
-Upload it to the FLExTrans website upload area, overwriting the existing file.
-The script copyRuleAssistantBinary.ps1 will copy it from there to the TeamCity server FLExTrans folder for the NSI installer to find
-Copy the exe locally for doing local installer builds (Installer folder)
