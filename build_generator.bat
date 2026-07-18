@echo off

set NAME_ORIGINAL = generator
set NAME_NEW = "I Wanna Launcher"

Python38\\python.exe -m PyInstaller -F --icon=Generated\\icon.ico %NAME_ORIGINAL%.py

move /Y "dist\%NAME_ORIGINAL%.exe" "%~dp0%NAME_NEW%.exe"

rmdir /S /Q build
rmdir /S /Q dist
del /Q "%NAME_ORIGINAL%.spec"

echo %NAME_NEW%.exe generated!
pause