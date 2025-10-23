#!/bin/bash
# generate.sh - Quick script to generate the dashboard
# Usage: ./generate.sh

echo "================================================"
echo "🏈 Fantasy Football Dashboard Generator"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 not found!"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if historical_data folder exists
if [ ! -d "historical_data" ]; then
    echo ""
    echo "❌ 'historical_data' folder not found!"
    echo ""
    echo "Creating folder..."
    mkdir historical_data
    echo "✅ Folder created!"
    echo ""
    echo "📁 Please add your CSV files to the 'historical_data/' folder, then run this script again."
    echo ""
    echo "Required files:"
    echo "  - 2022_FantasyPros_Fantasy_Football_Points_PPR.csv"
    echo "  - 2023_FantasyPros_Fantasy_Football_Points_PPR.csv"
    echo "  - 2024_FantasyPros_Fantasy_Football_Points_PPR.csv"
    echo "  - 2022_FantasyPros_Fantasy_Football_Points_HALF.csv"
    echo "  - 2023_FantasyPros_Fantasy_Football_Points_HALF.csv"
    echo "  - 2024_FantasyPros_Fantasy_Football_Points_HALF.csv"
    echo "  - 2022_FantasyPros_Fantasy_Football_Points.csv"
    echo "  - 2023_FantasyPros_Fantasy_Football_Points.csv"
    echo "  - 2024_FantasyPros_Fantasy_Football_Points.csv"
    exit 1
fi

# Count CSV files
CSV_COUNT=$(find historical_data -name "*.csv" | wc -l)
echo "📊 Found $CSV_COUNT CSV files in historical_data/"

if [ "$CSV_COUNT" -eq 0 ]; then
    echo ""
    echo "❌ No CSV files found in historical_data/ folder!"
    echo "Please add your FantasyPros CSV files."
    exit 1
fi

echo ""
echo "🔨 Running dashboard generator..."
echo ""

# Run the Python script
python3 generate_dashboard.py

# Check if generation was successful
if [ -f "fantasy_dashboard_v33.html" ]; then
    FILE_SIZE=$(du -h fantasy_dashboard_v33.html | cut -f1)
    echo ""
    echo "================================================"
    echo "✅ SUCCESS!"
    echo "================================================"
    echo "📄 Generated: fantasy_dashboard_v33.html"
    echo "📊 File size: $FILE_SIZE"
    echo ""
    echo "🚀 To use your dashboard:"
    echo "   1. Open fantasy_dashboard_v33.html in your browser"
    echo "   2. Upload your 2025 results CSV"
    echo "   3. Upload Week 1-7 FantasyPros projection CSVs"
    echo "   4. Click 'Initialize Dashboard'"
    echo ""
    echo "🌐 To host online:"
    echo "   - GitHub Pages: Push to a repo and enable Pages"
    echo "   - Netlify: Drag file to app.netlify.com/drop"
    echo "   - Vercel: Run 'vercel' in this folder"
    echo ""
else
    echo ""
    echo "❌ Generation failed! Check error messages above."
    exit 1
fi

# ============================================
# Windows batch file version (save as generate.bat)
# ============================================
: '
@echo off
echo ================================================
echo 🏈 Fantasy Football Dashboard Generator
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if historical_data folder exists
if not exist "historical_data\" (
    echo.
    echo ❌ 'historical_data' folder not found!
    echo.
    echo Creating folder...
    mkdir historical_data
    echo ✅ Folder created!
    echo.
    echo 📁 Please add your CSV files to the 'historical_data\' folder
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

echo 📊 Checking for CSV files...

REM Run the Python script
echo.
echo 🔨 Running dashboard generator...
echo.
python generate_dashboard.py

if exist "fantasy_dashboard_v33.html" (
    echo.
    echo ================================================
    echo ✅ SUCCESS!
    echo ================================================
    echo 📄 Generated: fantasy_dashboard_v33.html
    echo.
    echo 🚀 Double-click the HTML file to open in your browser
    echo.
) else (
    echo.
    echo ❌ Generation failed! Check errors above.
)

pause
'