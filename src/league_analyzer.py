import pandas as pd
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

class LeagueAnalyzer:
    def __init__(self, league_data: Dict, rosters: List[Dict], users: List[Dict], all_players: Dict):
        self.league = league_data
        self.rosters = rosters
        self.users = users
        self.all_players = all_players
        self.roster_positions = league_data.get('roster_positions', [])
        self.scoring_settings = league_data.get('scoring_settings', {})
        
        self._process_rosters()
        
    def _process_rosters(self):
        self.user_map = {user['user_id']: user['display_name'] for user in self.users}
        
        self.roster_by_user = {}
        self.all_rostered_players = set()
        
        for roster in self.rosters:
            user_id = roster['owner_id']
            player_ids = roster.get('players', [])
            self.roster_by_user[user_id] = {
                'players': player_ids,
                'starters': roster.get('starters', []),
                'reserve': roster.get('reserve', []),
                'taxi': roster.get('taxi', []),
                'roster_id': roster['roster_id'],
                'username': self.user_map.get(user_id, 'Unknown')
            }
            self.all_rostered_players.update(player_ids)
    
    def get_available_players(self, position: Optional[str] = None) -> List[Dict]:
        available = []
        
        for player_id, player_data in self.all_players.items():
            if player_id in self.all_rostered_players:
                continue
                
            if player_data.get('active') != True:
                continue
            
            if position and position not in player_data.get('fantasy_positions', []):
                continue
            
            player_info = {
                'player_id': player_id,
                'name': f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip(),
                'position': player_data.get('position'),
                'team': player_data.get('team'),
                'fantasy_positions': player_data.get('fantasy_positions', []),
                'injury_status': player_data.get('injury_status'),
                'depth_chart_order': player_data.get('depth_chart_order'),
                'search_rank': player_data.get('search_rank', 99999)
            }
            available.append(player_info)
        
        return sorted(available, key=lambda x: x['search_rank'])
    
    def analyze_roster_needs(self, user_id: str) -> Dict[str, List[str]]:
        if user_id not in self.roster_by_user:
            return {}
        
        roster_info = self.roster_by_user[user_id]
        player_ids = roster_info['players']
        
        position_counts = defaultdict(int)
        position_players = defaultdict(list)
        
        for player_id in player_ids:
            if player_id in self.all_players:
                player = self.all_players[player_id]
                pos = player.get('position')
                if pos:
                    position_counts[pos] += 1
                    player_name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
                    position_players[pos].append({
                        'name': player_name,
                        'team': player.get('team'),
                        'injury_status': player.get('injury_status')
                    })
        
        ideal_roster = {
            'QB': 2,
            'RB': 5,
            'WR': 5,
            'TE': 2,
            'K': 1,
            'DEF': 1
        }
        
        needs = {
            'critical': [],
            'moderate': [],
            'depth': []
        }
        
        for pos, ideal_count in ideal_roster.items():
            current_count = position_counts.get(pos, 0)
            deficit = ideal_count - current_count
            
            if deficit > 1:
                needs['critical'].append(pos)
            elif deficit == 1:
                needs['moderate'].append(pos)
            elif deficit == 0 and pos in ['RB', 'WR']:
                needs['depth'].append(pos)
        
        return {
            'needs': needs,
            'position_counts': dict(position_counts),
            'position_players': dict(position_players)
        }
    
    def get_waiver_priority(self) -> List[Tuple[str, int]]:
        priority = []
        for roster in self.rosters:
            user_id = roster['owner_id']
            username = self.user_map.get(user_id, 'Unknown')
            waiver_position = roster.get('settings', {}).get('waiver_position', 999)
            priority.append((username, waiver_position))
        
        return sorted(priority, key=lambda x: x[1])
    
    def get_recent_transactions(self, transactions: List[Dict], limit: int = 20) -> pd.DataFrame:
        if not transactions:
            return pd.DataFrame()
        
        processed = []
        for trans in transactions[:limit]:
            if trans['type'] in ['waiver', 'free_agent']:
                adds = trans.get('adds', {})
                drops = trans.get('drops', {})
                
                for player_id, user_id in adds.items():
                    player = self.all_players.get(player_id, {})
                    processed.append({
                        'type': 'ADD',
                        'player': f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
                        'position': player.get('position'),
                        'team': player.get('team'),
                        'user': self.user_map.get(user_id, 'Unknown'),
                        'timestamp': trans.get('created')
                    })
        
        if processed:
            df = pd.DataFrame(processed)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df.sort_values('timestamp', ascending=False)
        
        return pd.DataFrame()