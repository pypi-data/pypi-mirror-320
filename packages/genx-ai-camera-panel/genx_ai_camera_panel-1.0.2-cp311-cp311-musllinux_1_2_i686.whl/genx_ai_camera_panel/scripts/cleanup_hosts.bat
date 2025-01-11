@echo off

REM Remove domains from hosts file
findstr /v /c:"127.0.0.1 cameras.genx.ai" %WINDIR%\System32\drivers\etc\hosts > %WINDIR%\System32\drivers\etc\hosts.tmp
move /y %WINDIR%\System32\drivers\etc\hosts.tmp %WINDIR%\System32\drivers\etc\hosts

echo Domain removed from hosts file
