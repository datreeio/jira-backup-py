@echo off

pushd %~dp0
set script_dir=%CD%
popd

cd %script_dir%
cmd /k venv\\bin\\activate
python wizard.py >> backup_script.log 2>&1
