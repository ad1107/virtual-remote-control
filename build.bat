@echo off
set /p ver=Enter version number:
cls
echo Installing PyInstaller...
echo:
pip install pyinstaller
cls
echo Building executable...
echo:
pyinstaller --add-data "templates;templates" --onefile main.py
cls
echo Moving file to root destination...
echo:
cd dist
move main.exe ..
cd ..
rmdir dist
ren main.exe virtual-remote-control-%ver%.exe 
del *.spec /s /q /f
rmdir build /s /f
cls
echo Complete building version %ver%.
echo:
pause
