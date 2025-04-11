@echo off
setlocal enabledelayedexpansion

:: Make sure the folder that stores the builds exists
set binaryFolder=BuildBin
if not exist "%binaryFolder%" (
    mkdir "%binaryFolder%"
)

set finalFolder=ToNCodes

:: Trying to extract the version number
set "file=Globals.py"

:: Find the line with _VERSION=
for /f "delims=" %%A in ('findstr "^_VERSION = " "%file%"') do (
    set "line=%%A"
    goto ProcessVersion
)

:ProcessVersion
:: Extract the value
for /f "tokens=2 delims==" %%B in ("!line!") do (
    set "version=%%B"
)

:: Clean the value a little, single coma and spaces
set "version=%version:'=%"
set "version=%version:~1%"

set zipFile=ToNCodes-win64-%version%.zip

:: Copy the project, I don't want to clog the original with junk from the compilation
for /f %%i in ('cd') do set folder=%%~nxi
set folderCopy=%folder%_compcopy
cd "%binaryFolder%"
xcopy /E /I ..\..\%folder% ..\..\%folderCopy%
move ..\..\%folderCopy% .\

:: Go in and compile
cd "%folderCopy%"
python -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --include-package=websockets --windows-console-mode=disable --assume-yes-for-downloads ToNCodes.py

:: Create structure and clean up
mkdir "%finalFolder%"
move ToNCodes.exe "%finalFolder%"
move Templates "%finalFolder%"
move CHANGELOG.md "%finalFolder%"
move LICENSE.txt "%finalFolder%"
move README.md "%finalFolder%"
mkdir "%finalFolder%\Codes"
mkdir "%finalFolder%\Logs"
mkdir "%finalFolder%\Temp"
mkdir "%finalFolder%\Tools"
mkdir "%finalFolder%\Tools\Items"
mkdir "%finalFolder%\Tools\Locale"
mkdir "%finalFolder%\Tools\Themes"
mkdir "%finalFolder%\Tools\OSC"
move Tools\Items\silly.json "%finalFolder%\Tools\Items"
move Tools\Locale\* "%finalFolder%\Tools\Locale"
move Tools\Themes\* "%finalFolder%\Tools\Themes"
del "%finalFolder%\Tools\Themes\*-test.json"
move "%finalFolder%" ..\

cd ..
rmdir /S /Q "%folderCopy%"

7z a -tzip "%zipFile%" %finalFolder%
CertUtil -hashfile "%zipFile%" SHA256 > sha256win.txt

rmdir /S /Q "%finalFolder%"