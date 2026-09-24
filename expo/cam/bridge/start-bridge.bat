@echo off
rem Windows (the show machine): double-click. Downloads go2rtc once, then runs it.
cd /d "%~dp0"
set VER=v1.9.14
if not exist bin\go2rtc.exe (
  if not exist bin mkdir bin
  echo downloading go2rtc %VER% ...
  powershell -NoProfile -Command "Invoke-WebRequest -Uri https://github.com/AlexxIT/go2rtc/releases/download/%VER%/go2rtc_win64.zip -OutFile bin\go2rtc.zip; Expand-Archive -Force bin\go2rtc.zip bin; Remove-Item bin\go2rtc.zip" || goto :eof
)
if not exist camera.env (
  echo camera.env is missing - copy camera.env.example and fill it in
  pause & goto :eof
)
for /f "usebackq eol=# tokens=1,* delims==" %%a in ("camera.env") do set "%%a=%%b"
echo bridge on http://127.0.0.1:1984  (open it to see the camera)
bin\go2rtc.exe -config go2rtc.yaml
pause
