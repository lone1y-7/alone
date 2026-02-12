@echo off
chcp 65001 >nul
echo Building Forensic Tool C Module - Windows x64
echo.

if not exist build mkdir build
if not exist src mkdir src
if not exist include mkdir include

if not defined VSCMD_VER (
    echo ERROR: Please run in "x64 Native Tools Command Prompt for VS"!
    echo.
    echo How to open:
    echo 1. Click Windows Start menu
    echo 2. Search "x64 Native Tools Command Prompt for VS"
    echo 3. Open command prompt
    echo 4. cd to this directory
    echo 5. Run build.bat
    echo.
    pause
    exit /b 1
)

echo VS x64 environment detected, starting compilation...
echo.

echo [1/2] Compiling C source file...
cl.exe /c /D BUILD_DLL /DWIN32 /D_WINDOWS /W3 /Ox /Oi /Oy /GL /DNDEBUG /MD /EHsc /I include /wd4133 /wd4996 /Fo:src\file_scanner.obj src\file_scanner.c /nologo
if errorlevel 1 (
    echo.
    echo FAILED: Compiling object file!
    echo.
    pause
    exit /b 1
)
echo Object file compiled successfully!

echo [2/2] Linking to generate DLL...
link.exe /DLL /OUT:build\scanner.dll /IMPLIB:build\scanner.lib src\file_scanner.obj user32.lib kernel32.lib /nologo
if errorlevel 1 (
    echo.
    echo FAILED: Linking DLL!
    echo.
    pause
    exit /b 1
)
echo DLL linked successfully!

if exist build\scanner.dll (
    echo.
    echo ================================================
    echo Build SUCCESS!
    echo ================================================
    echo.
    echo Generated files:
    echo   - build\scanner.dll      (Dynamic Link Library)
    echo   - build\scanner.lib       (Import Library)
    echo   - src\file_scanner.obj    (Object File)
    echo.
    echo File info:
    dir build\scanner.dll
    echo.
    echo You can now run Python program!
) else (
    echo.
    echo FAILED: DLL file not generated!
    echo.
    pause
    exit /b 1
)

pause
exit /b 0
