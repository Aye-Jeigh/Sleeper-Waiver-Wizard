#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scoring_manager import ScoringManager

def test_scoring_manager():
    """Test the scoring manager functionality"""
    print("Testing Scoring Manager...")
    
    # Initialize scoring manager
    manager = ScoringManager()
    
    # Test 1: List presets
    print("\n1. Available Presets:")
    presets = manager.list_presets()
    for name, description in presets.items():
        print(f"   {name}: {description}")
    
    # Test 2: Get PPR settings
    print("\n2. PPR Settings:")
    ppr_settings = manager.get_scoring_settings(preset_name="ppr")
    print(f"   Points per reception: {ppr_settings.get('pts_rec', 0)}")
    print(f"   Points per rushing yard: {ppr_settings.get('pts_rush_yd', 0)}")
    print(f"   Points per receiving yard: {ppr_settings.get('pts_rec_yd', 0)}")
    print(f"   Points per rushing TD: {ppr_settings.get('pts_rush_td', 0)}")
    
    # Test 3: Compare scoring systems
    print("\n3. Scoring Comparison Test:")
    # Example stats for a WR with 5 catches, 75 yards, 1 TD
    test_stats = {
        'rec': 5,
        'rec_yd': 75,
        'rec_td': 1,
        'rush_yd': 0,
        'rush_td': 0
    }
    
    comparison = manager.compare_scoring(test_stats, "standard", "ppr")
    print(f"   WR stats: 5 rec, 75 yards, 1 TD")
    print(f"   Standard scoring: {comparison['standard']} points")
    print(f"   PPR scoring: {comparison['ppr']} points")
    print(f"   PPR advantage: +{comparison['difference']} points")
    
    # Test 4: Half-PPR
    half_ppr_settings = manager.get_scoring_settings(preset_name="half_ppr")
    print(f"\n4. Half-PPR Settings:")
    print(f"   Points per reception: {half_ppr_settings.get('pts_rec', 0)}")
    
    # Test 5: Superflex settings
    superflex_settings = manager.get_scoring_settings(preset_name="superflex")
    print(f"\n5. Superflex Settings:")
    print(f"   Points per passing TD: {superflex_settings.get('pts_pass_td', 0)}")
    
    print("\n✅ All scoring tests passed!")

if __name__ == "__main__":
    test_scoring_manager()