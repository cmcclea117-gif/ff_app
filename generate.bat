@echo off
REM generate.bat - Windows batch script to generate the dashboard
REM Double-click this file to run it

echo ================================================
echo 🏈 Fantasy Football Dashboard Generator
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

REM Check if historical_data folder exists
if not exist "historical_data\" (
    echo.
    echo ❌ 'historical_data' folder not found!
    echo.
    echo Creating folder...
    mkdir historical_data
    echo ✅ Folder created: historical_data\
    echo.
    echo 📁 Next steps:
    echo    1. Add your CSV files to the 'historical_data\' folder
    echo    2. Run this script again
    echo.
    echo Required files:
    echo    - 2022_FantasyPros_Fantasy_Football_Points_PPR.csv
    echo    - 2023_FantasyPros_Fantasy_Football_Points_PPR.csv
    echo    - 2024_FantasyPros_Fantasy_Football_Points_PPR.csv
    echo    - 2022_FantasyPros_Fantasy_Football_Points_HALF.csv
    echo    - 2023_FantasyPros_Fantasy_Football_Points_HALF.csv
    echo    - 2024_FantasyPros_Fantasy_Football_Points_HALF.csv
    echo    - 2022_FantasyPros_Fantasy_Football_Points.csv
    echo    - 2023_FantasyPros_Fantasy_Football_Points.csv
    echo    - 2024_FantasyPros_Fantasy_Football_Points.csv
    echo.
    pause
    exit /b 1
)

REM Count CSV files in historical_data folder
set CSV_COUNT=0
for %%f in (historical_data\*.csv) do set /a CSV_COUNT+=1

echo 📊 Found %CSV_COUNT% CSV files in historical_data\

if %CSV_COUNT%==0 (
    echo.
    echo ❌ No CSV files found in historical_data\ folder!
    echo Please add your FantasyPros CSV files and run this script again.
    echo.
    pause
    exit /b 1
)

echo.
echo 🔨 Running dashboard generator...
echo.

REM Run the Python script
python generate_dashboard.py

REM Check if generation was successful
if exist "fantasy_dashboard_v33.html" (
    echo.
    echo ================================================
    echo ✅ SUCCESS!
    echo ================================================
    
    REM Get file size
    for %%A in ("fantasy_dashboard_v33.html") do set FILE_SIZE=%%~zA
    set /a FILE_SIZE_MB=%FILE_SIZE% / 1048576
    
    echo 📄 Generated: fantasy_dashboard_v33.html
    echo 📊 File size: ~%FILE_SIZE_MB% MB
    echo.
    echo 🚀 To use your dashboard:
    echo    1. Double-click 'fantasy_dashboard_v33.html'
    echo    2. Upload your 2025 results CSV
    echo    3. Upload Week 1-7 FantasyPros projection CSVs
    echo    4. Click 'Initialize Dashboard'
    echo.
    echo 🌐 To host online:
    echo    - GitHub Pages: Push to repo and enable Pages
    echo    - Netlify: Drag file to app.netlify.com/drop
    echo    - Vercel: Run 'vercel' command in this folder
    echo.
    
    REM Ask if user wants to open the HTML file
    set /p OPEN="Would you like to open the dashboard now? (Y/N): "
    if /i "%OPEN%"=="Y" (
        start fantasy_dashboard_v33.html
    )
) else (
    echo.
    echo ❌ Generation failed!
    echo Check the error messages above for details.
    echo.
)

echo.
pause