@echo off

set NAME=updater

Python38\\python.exe -m PyInstaller -F --noconsole %NAME%.py

move /Y "dist\%NAME%.exe" "%~dp0Generated\%NAME%.upt"

rmdir /S /Q build
rmdir /S /Q dist
del /Q "%NAME%.spec"

echo %NAME%.upt generated!
pause