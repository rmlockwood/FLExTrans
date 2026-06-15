@echo off
rem ---------------------------------------------------------------------------
rem Run the Rule Assistant (CreateApertiumRules) test suite the same way the
rem GitHub CI does, so a local pass means CI will pass too.
rem
rem Usage:
rem   run_tests.bat                 Run every test
rem   run_tests.bat SplitBantu      Run one test class
rem   run_tests.bat SplitBantuMany  Run one test class
rem
rem Like CI, this runs from this folder (so "test_rule_assistant" and the
rem "RuleAssistantTests" package import) with the ci_stubs folder on PYTHONPATH
rem (so the FLEx/PyQt libraries are stubbed). The test locates the Apertium
rem tools relative to its own file, so no special working directory is needed.
rem ---------------------------------------------------------------------------

setlocal

rem Folder containing this script (Dev\TestRuleAssistant), minus trailing slash.
set "TEST_DIR=%~dp0"
if "%TEST_DIR:~-1%"=="\" set "TEST_DIR=%TEST_DIR:~0,-1%"

rem Repo root is two levels up; the stub libraries live under it.
set "PYTHONPATH=%TEST_DIR%\..\..\ci_stubs;%PYTHONPATH%"

pushd "%TEST_DIR%"

if "%~1"=="" (
    py -3.13 -m unittest test_rule_assistant -v
) else (
    py -3.13 -m unittest test_rule_assistant.%1 -v
)
set "RC=%ERRORLEVEL%"

popd
exit /b %RC%
