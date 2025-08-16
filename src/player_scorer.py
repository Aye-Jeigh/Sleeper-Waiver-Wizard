import pandas as pd
from typing import Dict, List, Optional
import numpy as np

class PlayerScorer:
    def __init__(self, scoring_settings: Dict):
        self.scoring_settings = scoring_settings
        self.default_weights = {
            'recent_performance': 0.35,
            'season_average': 0.20,
            'projections': 0.25,
            'consistency': 0.10,
            'trending': 0.10
        }
    
    def calculate_fantasy_points(self, stats: Dict) -> float:
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
            if stat_key in stats and scoring_key in self.scoring_settings:
                stat_value = stats[stat_key] or 0
                points_per = self.scoring_settings[scoring_key] or 0
                points += stat_value * points_per
        
        return round(points, 2)
    
    def analyze_player_performance(self, player_id: str, weekly_stats: List[Dict], projections: Dict) -> Dict:
        if not weekly_stats:
            return {
                'player_id': player_id,
                'avg_points': 0,
                'recent_avg': 0,
                'projected': 0,
                'consistency': 0,
                'trend': 0,
                'games_played': 0
            }
        
        points_history = []
        for week_stats in weekly_stats:
            if player_id in week_stats:
                points = self.calculate_fantasy_points(week_stats[player_id])
                points_history.append(points)
        
        if not points_history:
            return {
                'player_id': player_id,
                'avg_points': 0,
                'recent_avg': 0,
                'projected': 0,
                'consistency': 0,
                'trend': 0,
                'games_played': 0
            }
        
        avg_points = np.mean(points_history)
        recent_games = min(3, len(points_history))
        recent_avg = np.mean(points_history[-recent_games:]) if recent_games > 0 else 0
        
        consistency = 1 - (np.std(points_history) / (avg_points + 1)) if avg_points > 0 else 0
        
        if len(points_history) >= 3:
            x = np.arange(len(points_history))
            y = np.array(points_history)
            z = np.polyfit(x, y, 1)
            trend = z[0]
        else:
            trend = 0
        
        projected_points = 0
        if projections and player_id in projections:
            projected_points = self.calculate_fantasy_points(projections[player_id])
        
        return {
            'player_id': player_id,
            'avg_points': round(avg_points, 2),
            'recent_avg': round(recent_avg, 2),
            'projected': round(projected_points, 2),
            'consistency': round(consistency, 2),
            'trend': round(trend, 2),
            'games_played': len(points_history),
            'points_history': points_history
        }
    
    def score_waiver_candidates(self, candidates: List[Dict], weekly_stats: List[Dict], 
                               projections: Dict, trending_data: Optional[List[Dict]] = None) -> pd.DataFrame:
        
        trending_players = set()
        if trending_data:
            for player in trending_data:
                trending_players.add(player.get('player_id'))
        
        scored_players = []
        
        for candidate in candidates:
            player_id = candidate['player_id']
            performance = self.analyze_player_performance(player_id, weekly_stats, projections)
            
            waiver_score = 0
            score_components = {}
            
            if performance['games_played'] > 0:
                score_components['recent'] = performance['recent_avg'] * self.default_weights['recent_performance']
                score_components['average'] = performance['avg_points'] * self.default_weights['season_average']
                score_components['projected'] = performance['projected'] * self.default_weights['projections']
                score_components['consistency'] = performance['consistency'] * 10 * self.default_weights['consistency']
                
                is_trending = 1 if player_id in trending_players else 0
                score_components['trending'] = is_trending * 5 * self.default_weights['trending']
                
                waiver_score = sum(score_components.values())
                
                if performance['trend'] > 0:
                    waiver_score *= (1 + min(performance['trend'] * 0.1, 0.3))
            
            scored_players.append({
                'player_id': player_id,
                'name': candidate['name'],
                'position': candidate['position'],
                'team': candidate['team'],
                'waiver_score': round(waiver_score, 2),
                'avg_points': performance['avg_points'],
                'recent_avg': performance['recent_avg'],
                'projected': performance['projected'],
                'consistency': performance['consistency'],
                'trend': performance['trend'],
                'games_played': performance['games_played'],
                'is_trending': player_id in trending_players,
                'injury_status': candidate.get('injury_status'),
                **score_components
            })
        
        df = pd.DataFrame(scored_players)
        return df.sort_values('waiver_score', ascending=False)