chcp 65001
@echo off

REM Uncomment the following line to enable add relative paths to system PATH
@REM set "CURRENT_DIR=%cd%"

@REM set "FFMPEG_PATH=%CURRENT_DIR%\ffmpeg-7.1.1-full_build\bin"
@REM set "PYTHON_PATH=%CURRENT_DIR%\python311"

@REM set "PATH=%FFMPEG_PATH%;%PYTHON_PATH%;%PATH%"'

IF NOT EXIST venv (
    echo Creating venv...
    python.exe -m venv venv
)

call .\venv\Scripts\deactivate.bat

call .\venv\Scripts\activate.bat

REM first make sure we have setuptools available in the venv    
python.exe -m pip install --require-virtualenv --no-input -q -q  setuptools

REM Check if the batch was started via double-click
IF /i "%%comspec%% /c %%~0 " equ "%%cmdcmdline:"=%%" (
    REM echo This script was started by double clicking.
    cmd /k python.exe .\setup\setup_windows.py
) ELSE (
    REM echo This script was started from a command prompt.
    python.exe .\setup\setup_windows.py %*
)

:: Deactivate the virtual environment
call .\venv\Scripts\deactivate.bat