@echo off

REM Add domains to hosts file
findstr /c:"127.0.0.1 cameras.genx.ai" %WINDIR%\System32\drivers\etc\hosts >nul
if errorlevel 1 (
    echo 127.0.0.1 cameras.genx.ai >> %WINDIR%\System32\drivers\etc\hosts
    echo Domain added successfully to hosts file
) else (
    echo Domain already exists in hosts file
)