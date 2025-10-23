#!/usr/bin/env python3
"""
Quick debug script to see what files are in historical_data/
"""
import re
from pathlib import Path

DATA_FOLDER = 'historical_data'

print("=" * 60)
print("📁 Files in historical_data/")
print("=" * 60)

data_folder = Path(DATA_FOLDER)

if not data_folder.exists():
    print(f"❌ Folder not found: {data_folder.absolute()}")
    exit(1)

all_files = sorted(data_folder.glob('*.csv'))

print(f"\nTotal CSV files: {len(all_files)}\n")

# Categorize files
historical_files = []
results_files = []
projection_files = []
other_files = []

for f in all_files:
    name = f.name
    if any(year in name for year in ['2022', '2023', '2024']) and 'FantasyPros' in name:
        historical_files.append(name)
    elif '2025' in name and 'ALL' in name:
        projection_files.append(name)
    elif '2025' in name and 'Week' in name:
        projection_files.append(name)
    elif '2025' in name:
        results_files.append(name)
    else:
        other_files.append(name)

print("📚 HISTORICAL FILES (2022-2024):")
for f in historical_files:
    print(f"   ✅ {f}")

print(f"\n📅 2025 RESULTS FILES:")
if results_files:
    for f in results_files:
        print(f"   ✅ {f}")
else:
    print(f"   ❌ No 2025 results file found!")
    print(f"   Expected: Something like '2025_results.csv' or 'FantasyPros_2025_Fantasy_Football_Points_PPR.csv'")

print(f"\n📊 2025 PROJECTION FILES:")
if projection_files:
    for f in projection_files:
        # Try to extract week number
        week_match = re.search(r'(\d+)', f)
        week_num = week_match.group(1) if week_match else '?'
        print(f"   Week {week_num}: {f}")
else:
    print(f"   ❌ No projection files found!")

if other_files:
    print(f"\n❓ OTHER FILES:")
    for f in other_files:
        print(f"   {f}")

print("\n" + "=" * 60)
print("🔍 WHAT TO NAME YOUR FILES:")
print("=" * 60)
print("\n2025 Results file (weekly actual scores):")
print("   Name it: 2025_results.csv")
print("   OR update line 43 in generate_dashboard.py with actual name")

print("\nProjection files are already detected!")
print("   Your '2025 - ALL - X.csv' files should work")
print("   Your 'FantasyPros_2025_Week_8_OP_Rankings.csv' should work")

print("\n" + "=" * 60)
