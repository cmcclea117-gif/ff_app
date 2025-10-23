#!/usr/bin/env python3
"""
ECR Fix Patcher v2 - Fixes the .proj vs .ecr field issue

This fixes the critical bug where JavaScript looks for .proj but Python stores .ecr
"""

import sys
import re

def patch_ecr_fields(html_content):
    """Fix all instances where JavaScript checks for .proj instead of .ecr"""
    
    changes = []
    
    # Fix 1: calculateFPAccuracy - check for .ecr not .proj
    old1 = "if (proj && proj.proj > 0) {"
    new1 = "if (proj && proj.ecr > 0) {"
    if old1 in html_content:
        html_content = html_content.replace(old1, new1)
        changes.append("✅ Fixed calculateFPAccuracy() to check for .ecr field")
    
    # Fix 2: Alternative check for proj.proj
    old2 = "if (ecrData && ecrData.proj > 0) {"
    new2 = "if (ecrData && ecrData.ecr > 0) {"
    if old2 in html_content:
        html_content = html_content.replace(old2, new2)
        changes.append("✅ Fixed calculateProjections() to check for .ecr field")
    
    # Fix 3: hasFP should be hasECR
    old3 = "p.hasFP"
    new3 = "p.hasECR"
    if old3 in html_content:
        html_content = html_content.replace(old3, new3)
        changes.append("✅ Fixed hasFP references to hasECR")
    
    # Fix 4: Add console logging to calculateProjections
    old_calc_start = "function calculateProjections() {\n  if (!SEASON_2025 || !SEASON_2025.data) return [];"
    new_calc_start = """function calculateProjections() {
  if (!SEASON_2025 || !SEASON_2025.data) return [];
  
  const projections = [];
  const nextWeekECR = WEEKLY_PROJECTIONS[NEXT_WEEK] || [];
  const baselines = calculatePositionalBaselines();
  
  console.log(`Calculating projections with ${nextWeekECR.length} ECR entries for Week ${NEXT_WEEK}`);
  
  // Debug: Check first ECR entry structure
  if (nextWeekECR.length > 0) {
    console.log('Sample ECR entry:', nextWeekECR[0]);
  }
  
  let ecrMatchCount = 0;"""
    
    if old_calc_start in html_content:
        html_content = html_content.replace(old_calc_start, new_calc_start)
        changes.append("✅ Added debug logging to calculateProjections()")
    
    # Fix 5: Add console logging to calculateFPAccuracy
    old_acc_start = "function calculateFPAccuracy() {\n  FP_ACCURACY = {};"
    new_acc_start = """function calculateFPAccuracy() {
  FP_ACCURACY = {};
  
  if (!SEASON_2025 || !SEASON_2025.data) {
    console.log('No 2025 season data');
    return;
  }
  
  const seasonData = SEASON_2025.data;
  const weekNums = Object.keys(WEEKLY_PROJECTIONS).map(Number).sort((a,b) => a-b);
  
  console.log(`Checking ${seasonData.length} players against ${weekNums.length} weeks of ECR data`);
  
  let matchCount = 0;"""
    
    if old_acc_start in html_content:
        html_content = html_content.replace(old_acc_start, new_acc_start)
        changes.append("✅ Added debug logging to calculateFPAccuracy()")
    
    # Fix 6: Update reliability table empty state
    old_reliability = """tbody.innerHTML = data.map(p => {
    const avgScoreWeeks = Object.values(p.weeks).map(w => w.actual);
    const avgScore = avgScoreWeeks.reduce((a,b) => a+b, 0) / avgScoreWeeks.length;"""
    
    new_reliability = """if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#95a5a6;">No reliability data available. Check console for ECR matching issues.</td></tr>';
    return;
  }
  
  tbody.innerHTML = data.map(p => {
    const playerData = SEASON_2025.data.find(pd => pd.p === p.name);
    let avgScore = 0;
    if (playerData && playerData.w) {
      const scores = Object.values(playerData.w);
      avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
    }"""
    
    if old_reliability in html_content:
        html_content = html_content.replace(old_reliability, new_reliability)
        changes.append("✅ Fixed renderReliabilityTable() avgScore calculation")
    
    return html_content, changes

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 patch_ecr_fix.py <input_html_file>")
        print("\nThis patcher specifically fixes the .proj vs .ecr field bug")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = input_file.replace('.html', '_ecr_fixed.html')
    
    print("=" * 60)
    print("🔧 ECR Field Fix Patcher v2")
    print("=" * 60)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        print(f"\n📂 Reading: {input_file}")
        
        # Apply patches
        html, changes = patch_ecr_fields(html)
        
        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Patched file saved to: {output_file}\n")
        
        if changes:
            print("📋 Changes applied:")
            for change in changes:
                print(f"  {change}")
        else:
            print("⚠️  No changes needed - file may already be patched")
        
        print("\n" + "=" * 60)
        print("🎯 Next Steps:")
        print("=" * 60)
        print(f"1. Open: {output_file}")
        print("2. Press F12 to open console")
        print("3. Look for these messages:")
        print("   - 'Sample ECR entry: {p: ..., pos: ..., ecr: X, std: Y}'")
        print("   - 'FP Accuracy calculated for X players'")
        print("   - 'Generated Y projections, Z with ECR data'")
        print("\n4. If 'With FP Data' still shows 0:")
        print("   - Check console for player name mismatches")
        print("   - Verify ECR CSV has PLAYER NAME column")
        print("   - Check for Jr/Sr/II/III name differences")
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
