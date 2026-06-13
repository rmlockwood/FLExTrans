@echo off
rem ---------------------------------------------------------------------------
rem Run the Rule Assistant (CreateApertiumRules) test suite.
rem
rem Usage:
rem   run_tests.bat                 Run every test
rem   run_tests.bat SplitBantu      Run one test class
rem   run_tests.bat SplitBantuMany  Run one test class
rem
rem The suite needs two things set up, which this script handles:
rem   * PYTHONPATH must include this folder so "test_rule_assistant" and the
rem     "RuleAssistantTests" package can be imported.
rem   * The working directory must be the Apertium4Windows tools folder, because
rem     the tests locate apertium-preprocess-transfer.exe / apertium-transfer.exe
rem     relative to the current directory.
rem ---------------------------------------------------------------------------

setlocal

rem Folder containing this script (Dev\TestRuleAssistant), minus trailing slash.
set "TEST_DIR=%~dp0"
if "%TEST_DIR:~-1%"=="\" set "TEST_DIR=%TEST_DIR:~0,-1%"

rem Apertium command-line tools, two levels up then into the installer resources.
set "APERTIUM_DIR=%TEST_DIR%\..\..\Installer\InstallerResources\Apertium4Windows"

if not exist "%APERTIUM_DIR%\apertium-preprocess-transfer.exe" (
    echo ERROR: Could not find the Apertium tools at:
    echo        "%APERTIUM_DIR%"
    exit /b 1
)

set "PYTHONPATH=%TEST_DIR%"

pushd "%APERTIUM_DIR%"

if "%~1"=="" (
    python -m unittest test_rule_assistant -v
) else (
    python -m unittest test_rule_assistant.%1 -v
)
set "RC=%ERRORLEVEL%"

popd
exit /b %RC%
