#!/usr/bin/env python3

import os
import sys
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich import box

from src.sleeper_client import SleeperClient
from src.league_analyzer import LeagueAnalyzer
from src.player_scorer import PlayerScorer
from src.waiver_recommender import WaiverRecommender

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Sleeper Fantasy Football Waiver Wire Assistant")
    parser.add_argument('--league-id', type=str, help='Sleeper league ID')
    parser.add_argument('--season', type=int, default=2024, help='NFL season (default: 2024)')
    parser.add_argument('--week', type=int, help='Current NFL week')
    parser.add_argument('--user', type=str, help='Username to analyze')
    parser.add_argument('--position', type=str, choices=['QB', 'RB', 'WR', 'TE', 'K', 'DEF'], 
                       help='Filter by position')
    parser.add_argument('--top', type=int, default=15, help='Number of recommendations (default: 15)')
    parser.add_argument('--clear-cache', action='store_true', help='Clear the cache before running')
    
    args = parser.parse_args()
    
    load_dotenv()
    
    league_id = args.league_id or os.getenv('LEAGUE_ID')
    season = args.season or int(os.getenv('SEASON', 2024))
    week = args.week or int(os.getenv('CURRENT_WEEK', 1))
    
    if not league_id:
        console.print("[red]Error: League ID is required. Set via --league-id or LEAGUE_ID in .env file[/red]")
        sys.exit(1)
    
    console.print(Panel(f"[bold cyan]Sleeper Waiver Wire Assistant[/bold cyan]\n"
                       f"League: {league_id}\n"
                       f"Season: {season} | Week: {week}", 
                       box=box.DOUBLE))
    
    client = SleeperClient()
    
    if args.clear_cache:
        client.clear_cache()
        console.print("[green]Cache cleared![/green]")
    
    with console.status("[bold green]Fetching league data...") as status:
        league = client.get_league(league_id)
        if not league:
            console.print("[red]Error: Could not fetch league data[/red]")
            sys.exit(1)
        
        status.update("[bold green]Fetching rosters...")
        rosters = client.get_rosters(league_id)
        
        status.update("[bold green]Fetching users...")
        users = client.get_users(league_id)
        
        status.update("[bold green]Fetching all players (this may take a moment)...")
        all_players = client.get_all_players()
        
        status.update("[bold green]Fetching trending players...")
        trending = client.get_trending_players()
        
        weekly_stats = []
        for w in range(max(1, week - 5), week + 1):
            status.update(f"[bold green]Fetching stats for week {w}...")
            stats = client.get_stats(season, w)
            if stats:
                weekly_stats.append(stats)
        
        status.update(f"[bold green]Fetching projections for week {week + 1}...")
        projections = client.get_projections(season, week + 1)
        
        status.update(f"[bold green]Fetching recent transactions...")
        transactions = client.get_transactions(league_id, week)
    
    analyzer = LeagueAnalyzer(league, rosters, users, all_players)
    scorer = PlayerScorer(league.get('scoring_settings', {}))
    recommender = WaiverRecommender(analyzer, scorer)
    
    if args.user:
        target_user = None
        for user_id, roster_info in analyzer.roster_by_user.items():
            if roster_info['username'].lower() == args.user.lower():
                target_user = user_id
                break
        
        if not target_user:
            console.print(f"[red]User '{args.user}' not found in league[/red]")
            console.print("\nAvailable users:")
            for user_id, roster_info in analyzer.roster_by_user.items():
                console.print(f"  - {roster_info['username']}")
            sys.exit(1)
    else:
        console.print("\n[bold]Select a team to analyze:[/bold]")
        user_list = list(analyzer.roster_by_user.items())
        for idx, (user_id, roster_info) in enumerate(user_list, 1):
            console.print(f"  {idx}. {roster_info['username']}")
        
        selection = IntPrompt.ask("Enter number", default=1)
        if 1 <= selection <= len(user_list):
            target_user = user_list[selection - 1][0]
        else:
            console.print("[red]Invalid selection[/red]")
            sys.exit(1)
    
    console.print("\n" + "="*80 + "\n")
    
    recommender.display_roster_analysis(target_user)
    
    console.print("\n" + "="*80 + "\n")
    
    with console.status("[bold green]Analyzing available players...") as status:
        available = analyzer.get_available_players(position=args.position)
        
        status.update("[bold green]Scoring waiver candidates...")
        scored = scorer.score_waiver_candidates(available[:200], weekly_stats, projections, trending)
        
        status.update("[bold green]Generating recommendations...")
        recommendations = recommender.generate_recommendations(target_user, scored, 
                                                              top_n=args.top, 
                                                              position_filter=args.position)
    
    if not recommendations.empty:
        recommender.display_recommendations(recommendations, analyzer.roster_by_user[target_user])
    else:
        console.print("[yellow]No recommendations found matching your criteria[/yellow]")
    
    if trending and not args.position:
        console.print("\n" + "="*80 + "\n")
        recommender.display_trending_players(trending, all_players)
    
    if transactions:
        recent_trans = analyzer.get_recent_transactions(transactions, limit=10)
        if not recent_trans.empty:
            console.print("\n" + "="*80 + "\n")
            console.print(Panel("[bold green]Recent League Transactions[/bold green]", box=box.DOUBLE))
            console.print(recent_trans.to_string(index=False))
    
    console.print("\n[dim]Recommendations based on recent performance, projections, and roster needs[/dim]")
    console.print("[dim]Cache expires after 24 hours for player data, 1 hour for roster data[/dim]")

if __name__ == "__main__":
    main()