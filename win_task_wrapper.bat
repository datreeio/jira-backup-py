@echo off

pushd %~dp0
set script_dir=%CD%
popd

cd %script_dir%

REM print output and error to file and then to console:
REM powershell -window minimized -Command "& venv\Scripts\activate.bat; python backup.py 2>&1 | tee backup_script.log"

REM print output and error to console:
powershell -Command "& venv\Scripts\activate.bat; python backup.py"

REM print output and error to file:
REM powershell -window minimized -Command "& venv\Scripts\activate.bat; python backup.py >> backup_script.log 2>&1"

pause
