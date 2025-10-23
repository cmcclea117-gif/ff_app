#!/usr/bin/env python3
"""
Quick Start Script for Fantasy Football Dashboard V3.4

This script checks if you have all the required files and helps you generate the dashboard.
"""

import os
from pathlib import Path

def check_requirements():
    """Check if all required files are present."""
    print("🔍 Checking requirements...\n")
    
    # Check for data folder
    data_folder = Path('historical_data')
    if not data_folder.exists():
        print("❌ 'historical_data' folder not found")
        print("   Create it with: mkdir historical_data")
        return False
    else:
        print("✅ 'historical_data' folder found")
    
    # Check for required files
    required_files = [
        '2022_FantasyPros_Fantasy_Football_Points_PPR.csv',
        '2023_FantasyPros_Fantasy_Football_Points_PPR.csv',
        '2024_FantasyPros_Fantasy_Football_Points_PPR.csv',
        '2022_FantasyPros_Fantasy_Football_Points_HALF.csv',
        '2023_FantasyPros_Fantasy_Football_Points_HALF.csv',
        '2024_FantasyPros_Fantasy_Football_Points_HALF.csv',
        '2022_FantasyPros_Fantasy_Football_Points.csv',
        '2023_FantasyPros_Fantasy_Football_Points.csv',
        '2024_FantasyPros_Fantasy_Football_Points.csv',
        '2025_results.csv'
    ]
    
    missing = []
    for file in required_files:
        filepath = data_folder / file
        if filepath.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing.append(file)
    
    # Check for projection files
    proj_files = list(data_folder.glob('*2025*Week*.csv'))
    print(f"\n📊 Found {len(proj_files)} weekly projection files")
    for pf in sorted(proj_files):
        print(f"   ✅ {pf.name}")
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} required files")
        print("\nAdd these files to the 'historical_data/' folder:")
        for m in missing:
            print(f"   - {m}")
        return False
    
    if len(proj_files) == 0:
        print("\n⚠️  No weekly projection files found")
        print("   Add files like: '2025_Week_1.csv', '2025_Week_2.csv', etc.")
        print("   The dashboard will still work, but projections will be limited.")
    
    print("\n✅ All required files present!")
    return True

def run_generator():
    """Run the dashboard generator."""
    print("\n" + "="*60)
    print("🚀 Running Fantasy Football Dashboard Generator V3.4")
    print("="*60 + "\n")
    
    import subprocess
    result = subprocess.run(['python3', 'generate_dashboard.py'], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✅ Dashboard generated successfully!")
        print("\n📂 Open 'fantasy_dashboard_v34_complete.html' in your browser")
        print("\n💡 Tips:")
        print("   - Connect to Sleeper for roster tracking")
        print("   - Change scoring format to see different rankings")
        print("   - Use the lineup optimizer to set your roster")
    else:
        print("\n❌ Generation failed. Check the error messages above.")
    
    return result.returncode == 0

def main():
    """Main execution."""
    print("""
╔══════════════════════════════════════════════════════════╗
║  Fantasy Football Dashboard V3.4 - Quick Start          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if generate_dashboard.py exists
    if not Path('generate_dashboard.py').exists():
        print("❌ 'generate_dashboard.py' not found in current directory")
        print("\n📁 Make sure you're in the same folder as the generator script")
        print("   Current directory:", os.getcwd())
        return
    
    # Check requirements
    if not check_requirements():
        print("\n" + "="*60)
        print("⚠️  Setup incomplete. Fix the issues above and try again.")
        print("="*60)
        return
    
    # Ask user if they want to proceed
    print("\n" + "="*60)
    response = input("Generate dashboard now? (y/n): ").lower().strip()
    
    if response == 'y':
        success = run_generator()
        if success:
            print("\n" + "="*60)
            print("🎉 All done! Enjoy your dashboard!")
            print("="*60)
    else:
        print("\n👋 Okay! Run this script again when you're ready.")

if __name__ == "__main__":
    main()
