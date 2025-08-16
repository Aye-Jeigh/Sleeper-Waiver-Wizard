import json
import os
from typing import Dict, Optional
from pathlib import Path

class ScoringManager:
    def __init__(self, config_path: str = "./config/scoring_settings.json"):
        self.config_path = Path(config_path)
        self.presets = {}
        self.custom_settings = None
        self.load_scoring_config()
    
    def load_scoring_config(self):
        """Load scoring configuration from JSON file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.presets = config.get('presets', {})
        else:
            print(f"Warning: Scoring config not found at {self.config_path}")
            self.presets = self._get_default_presets()
    
    def get_scoring_settings(self, preset_name: Optional[str] = None, 
                            league_settings: Optional[Dict] = None,
                            use_league_settings: bool = True) -> Dict:
        """
        Get scoring settings with priority:
        1. Custom settings from .env if exists
        2. Specified preset (e.g., 'ppr', 'standard')
        3. League settings from Sleeper API
        4. Default to standard scoring
        """
        
        # Check for custom scoring file
        custom_path = Path("./.env.scoring.json")
        if custom_path.exists():
            with open(custom_path, 'r') as f:
                return json.load(f)
        
        # Use specified preset
        if preset_name and preset_name in self.presets:
            return self.presets[preset_name]['settings']
        
        # Try to detect scoring type from league settings
        if use_league_settings and league_settings:
            # Check if it's PPR
            pts_rec = league_settings.get('pts_rec', 0)
            if pts_rec == 1:
                print("Detected PPR scoring from league settings")
                return self.presets.get('ppr', {}).get('settings', league_settings)
            elif pts_rec == 0.5:
                print("Detected Half-PPR scoring from league settings")
                return self.presets.get('half_ppr', {}).get('settings', league_settings)
            else:
                # Use league settings as-is
                return league_settings
        
        # Default to standard scoring
        return self.presets.get('standard', {}).get('settings', {})
    
    def save_custom_scoring(self, settings: Dict, name: str = "custom"):
        """Save custom scoring settings to a file"""
        custom_path = Path("./.env.scoring.json")
        with open(custom_path, 'w') as f:
            json.dump(settings, f, indent=2)
        print(f"Custom scoring settings saved to {custom_path}")
    
    def list_presets(self) -> Dict:
        """List all available scoring presets"""
        return {name: preset['description'] for name, preset in self.presets.items()}
    
    def get_preset_details(self, preset_name: str) -> Optional[Dict]:
        """Get detailed information about a specific preset"""
        return self.presets.get(preset_name)
    
    def _get_default_presets(self) -> Dict:
        """Return default presets if config file not found"""
        return {
            "standard": {
                "name": "Standard Scoring",
                "description": "Traditional fantasy football scoring without PPR",
                "settings": {
                    "pts_pass_yd": 0.04,
                    "pts_pass_td": 4,
                    "pts_pass_int": -2,
                    "pts_rush_yd": 0.1,
                    "pts_rush_td": 6,
                    "pts_rec": 0,
                    "pts_rec_yd": 0.1,
                    "pts_rec_td": 6,
                    "pts_fum_lost": -2,
                    "pts_pass_2pt": 2,
                    "pts_rush_2pt": 2,
                    "pts_rec_2pt": 2
                }
            },
            "ppr": {
                "name": "PPR (Point Per Reception)",
                "description": "Full point per reception scoring",
                "settings": {
                    "pts_pass_yd": 0.04,
                    "pts_pass_td": 4,
                    "pts_pass_int": -2,
                    "pts_rush_yd": 0.1,
                    "pts_rush_td": 6,
                    "pts_rec": 1,
                    "pts_rec_yd": 0.1,
                    "pts_rec_td": 6,
                    "pts_fum_lost": -2,
                    "pts_pass_2pt": 2,
                    "pts_rush_2pt": 2,
                    "pts_rec_2pt": 2
                }
            }
        }
    
    def compare_scoring(self, stats: Dict, preset1: str = "standard", preset2: str = "ppr") -> Dict:
        """Compare how a player would score under different scoring systems"""
        settings1 = self.presets.get(preset1, {}).get('settings', {})
        settings2 = self.presets.get(preset2, {}).get('settings', {})
        
        score1 = self._calculate_points(stats, settings1)
        score2 = self._calculate_points(stats, settings2)
        
        return {
            preset1: round(score1, 2),
            preset2: round(score2, 2),
            'difference': round(score2 - score1, 2)
        }
    
    def _calculate_points(self, stats: Dict, settings: Dict) -> float:
        """Calculate fantasy points based on stats and settings"""
        points = 0.0
        
        stat_mappings = {
            'pass_yd': 'pts_pass_yd',
            'pass_td': 'pts_pass_td',
            'pass_int': 'pts_pass_int',
            'rush_yd': 'pts_rush_yd',
            'rush_td': 'pts_rush_td',
            'rec': 'pts_rec',
            'rec_yd': 'pts_rec_yd',
            'rec_td': 'pts_rec_td',
            'fum_lost': 'pts_fum_lost',
            'pass_2pt': 'pts_pass_2pt',
            'rush_2pt': 'pts_rush_2pt',
            'rec_2pt': 'pts_rec_2pt'
        }
        
        for stat_key, scoring_key in stat_mappings.items():
            if stat_key in stats and scoring_key in settings:
                stat_value = stats.get(stat_key, 0) or 0
                points_per = settings.get(scoring_key, 0) or 0
                points += stat_value * points_per
        
        return points