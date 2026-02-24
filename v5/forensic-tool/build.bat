@echo off
chcp 65001 >nul
echo Building Forensic Tool C Module - Windows x64
echo.

if not exist build mkdir build

if not defined VSCMD_VER (
    echo ERROR: Please run in "x64 Native Tools Command Prompt for VS"!
    pause
    exit /b 1
)

echo VS x64 environment detected, starting compilation...
echo.

echo [1/2] Compiling C source file...
cl.exe /c ^
/D BUILD_DLL ^
/DNDEBUG ^
/O2 ^
/MD ^
/Fo:build\file_scanner.obj ^
src\file_scanner.c ^
/nologo

if errorlevel 1 (
    echo.
    echo FAILED: Compiling object file!
    pause
    exit /b 1
)

echo Object file compiled successfully!

echo [2/2] Linking to generate DLL...
link.exe /DLL ^
/OUT:build\scanner.dll ^
/IMPLIB:build\scanner.lib ^
build\file_scanner.obj ^
kernel32.lib user32.lib ^
/nologo

if errorlevel 1 (
    echo.
    echo FAILED: Linking DLL!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Build SUCCESS!
echo ================================================
echo.
dir build\scanner.dll
echo.

pause
exit /b 0
