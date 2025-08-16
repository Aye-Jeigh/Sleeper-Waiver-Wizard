import pandas as pd
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

class WaiverRecommender:
    def __init__(self, league_analyzer, player_scorer):
        self.analyzer = league_analyzer
        self.scorer = player_scorer
        self.console = Console()
    
    def generate_recommendations(self, user_id: str, scored_players: pd.DataFrame, 
                                top_n: int = 10, position_filter: Optional[str] = None) -> pd.DataFrame:
        
        roster_analysis = self.analyzer.analyze_roster_needs(user_id)
        needs = roster_analysis['needs']
        
        recommendations = []
        
        if position_filter:
            filtered = scored_players[scored_players['position'] == position_filter]
        else:
            filtered = scored_players.copy()
        
        priority_boost = {
            'critical': 1.5,
            'moderate': 1.2,
            'depth': 1.0
        }
        
        for _, player in filtered.iterrows():
            position = player['position']
            adjusted_score = player['waiver_score']
            
            for need_level, positions in needs.items():
                if position in positions:
                    adjusted_score *= priority_boost[need_level]
                    player['need_level'] = need_level
                    break
            else:
                player['need_level'] = 'luxury'
            
            player['adjusted_score'] = adjusted_score
            recommendations.append(player)
        
        df = pd.DataFrame(recommendations)
        return df.nlargest(top_n, 'adjusted_score')
    
    def display_recommendations(self, recommendations: pd.DataFrame, user_roster: Dict):
        username = user_roster.get('username', 'Unknown User')
        
        self.console.print(Panel(f"[bold cyan]Waiver Wire Recommendations for {username}[/bold cyan]", 
                                box=box.DOUBLE))
        
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Player", style="cyan", width=20)
        table.add_column("Pos", justify="center", width=5)
        table.add_column("Team", justify="center", width=5)
        table.add_column("Score", justify="right", width=8)
        table.add_column("Avg Pts", justify="right", width=8)
        table.add_column("Recent", justify="right", width=8)
        table.add_column("Proj", justify="right", width=8)
        table.add_column("Need", justify="center", width=10)
        table.add_column("Status", justify="center", width=10)
        
        for idx, row in recommendations.iterrows():
            rank = str(idx + 1)
            
            need_colors = {
                'critical': 'red',
                'moderate': 'yellow',
                'depth': 'green',
                'luxury': 'dim'
            }
            need_color = need_colors.get(row.get('need_level', 'luxury'), 'dim')
            
            status = ""
            if row.get('is_trending'):
                status = "🔥 TRENDING"
            if row.get('injury_status'):
                status = f"⚠️ {row['injury_status']}"
            
            table.add_row(
                rank,
                row['name'],
                row['position'],
                row.get('team', 'FA'),
                f"{row['adjusted_score']:.1f}",
                f"{row['avg_points']:.1f}",
                f"{row['recent_avg']:.1f}",
                f"{row['projected']:.1f}",
                f"[{need_color}]{row.get('need_level', 'luxury')}[/{need_color}]",
                status
            )
        
        self.console.print(table)
    
    def display_roster_analysis(self, user_id: str):
        analysis = self.analyzer.analyze_roster_needs(user_id)
        username = self.analyzer.roster_by_user[user_id]['username']
        
        self.console.print(Panel(f"[bold yellow]Roster Analysis for {username}[/bold yellow]", 
                                box=box.DOUBLE))
        
        needs_table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        needs_table.add_column("Priority", style="bold", width=15)
        needs_table.add_column("Positions", width=40)
        
        for level, positions in analysis['needs'].items():
            if positions:
                color = {'critical': 'red', 'moderate': 'yellow', 'depth': 'green'}.get(level, 'white')
                needs_table.add_row(
                    f"[{color}]{level.upper()}[/{color}]",
                    ", ".join(positions) if positions else "None"
                )
        
        self.console.print(needs_table)
        
        self.console.print("\n[bold]Current Roster Composition:[/bold]")
        comp_table = Table(show_header=True, header_style="bold green", box=box.SIMPLE)
        comp_table.add_column("Position", width=10)
        comp_table.add_column("Count", width=8)
        comp_table.add_column("Players", width=60)
        
        for pos, players in analysis['position_players'].items():
            player_names = []
            for p in players:
                name = p['name']
                if p.get('injury_status'):
                    name += f" [red]({p['injury_status']})[/red]"
                player_names.append(name)
            
            comp_table.add_row(
                pos,
                str(len(players)),
                ", ".join(player_names[:5])
            )
        
        self.console.print(comp_table)
    
    def display_trending_players(self, trending: List[Dict], all_players: Dict):
        self.console.print(Panel("[bold magenta]🔥 Trending Players (Last 24 Hours)[/bold magenta]", 
                                box=box.DOUBLE))
        
        table = Table(show_header=True, header_style="bold yellow", box=box.SIMPLE)
        table.add_column("#", width=5)
        table.add_column("Player", width=25)
        table.add_column("Position", width=8)
        table.add_column("Team", width=8)
        table.add_column("Status", width=15)
        
        for idx, player_data in enumerate(trending[:15], 1):
            player_id = player_data.get('player_id')
            if player_id in all_players:
                player = all_players[player_id]
                name = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
                
                status = "Available"
                if player_id in self.analyzer.all_rostered_players:
                    status = "[red]Rostered[/red]"
                elif player.get('injury_status'):
                    status = f"[yellow]{player['injury_status']}[/yellow]"
                
                table.add_row(
                    str(idx),
                    name,
                    player.get('position', 'N/A'),
                    player.get('team', 'FA'),
                    status
                )
        
        self.console.print(table)