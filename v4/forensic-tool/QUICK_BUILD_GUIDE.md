# Quick Build Guide for Windows

## Prerequisites

- Windows 10 or higher
- Visual Studio 2019 or 2022 with C++ Development Tools
- Python 3.8 or higher

## Build Steps

### Step 1: Open VS x64 Command Prompt

1. Click Windows Start menu
2. Search for "x64 Native Tools Command Prompt for VS"
3. Select Visual Studio 2019 or 2022
4. Open the command prompt

### Step 2: Navigate to Project Directory

```cmd
cd /d D:\sqlite-tool\v3\workspace\forensic-tool
```

### Step 3: Run Build Script

```cmd
build.bat
```

### Step 4: Verify Output

If successful, you will see:
```
================================================
Build SUCCESS!
================================================

Generated files:
  - build\scanner.dll      (Dynamic Link Library)
  - build\scanner.lib       (Import Library)
  - src\file_scanner.obj    (Object File)
```

## Run the Application

### Install Dependencies

```cmd
cd forensic-tool
pip install -r requirements.txt
pip install fakeredis
```

### Start API Server

```cmd
python main.py
```

The server will run on: http://localhost:8000

### Test the Service

Open new command prompt:

```cmd
curl http://localhost:8000/
```

## Troubleshooting

### Error: "'b' is not recognized"

**Cause**: File encoding issue

**Solution**: Use the new `build.bat` file (saved in UTF-8 encoding without BOM)

### Error: "Please run in x64 Native Tools Command Prompt"

**Cause**: Not running in VS x64 environment

**Solution**: Open "x64 Native Tools Command Prompt for VS" and try again

### Error: "Cannot open include file 'dirent.h'"

**Cause**: Missing dirent.h header file

**Solution**: Ensure `include/dirent.h` exists in the project directory

## File Structure

```
forensic-tool/
├── src/
│   └── file_scanner.c      # C source code (cross-platform)
├── include/
│   └── dirent.h            # Windows-compatible dirent header
├── build/
│   ├── scanner.dll          # Windows DLL (generated)
│   ├── scanner.lib          # Import library (generated)
│   └── scanner.exp          # Export file (generated)
├── main.py                 # FastAPI backend
├── ui.py                   # GUI application
├── build.bat               # Windows build script
└── requirements.txt         # Python dependencies
```

## API Documentation

After starting the service, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps

1. Build the project using the steps above
2. Test the functionality with test data
3. Verify all features work correctly

## Support

For issues, check:
- WINDOWS_BUILD_GUIDE.md (Chinese version)
- README.md (project overview)
- GitHub Issues (if applicable)
