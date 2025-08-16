# Sleeper Waiver Wire Assistant - Project Context

## Project Overview
A Python tool that analyzes Sleeper fantasy football leagues and provides intelligent waiver wire recommendations based on player performance, roster needs, and trends. The tool uses the Sleeper API to fetch league data and provides recommendations through a rich CLI interface.

## Tech Stack
- **Language**: Python 3.x
- **Key Libraries**:
  - `requests` - HTTP client for API calls
  - `pandas` - Data manipulation and analysis
  - `python-dotenv` - Environment variable management
  - `ratelimit` - API rate limiting (100 calls/minute for Sleeper API)
  - `diskcache` - Persistent caching to minimize API calls
  - `rich` - Beautiful terminal output with tables and formatting

## Project Structure
```
/
├── main.py                  # Entry point, CLI argument parsing, orchestration
├── requirements.txt         # Python dependencies
├── README.md               # User documentation
├── .gitignore              # Standard Python gitignore
├── .env                    # Environment variables (not in repo)
├── cache/                  # Disk cache storage (auto-created)
├── data/                   # Data storage directory
├── config/                 # Configuration directory (currently empty)
└── src/
    ├── sleeper_client.py       # Sleeper API client with caching
    ├── league_analyzer.py      # League data analysis logic
    ├── player_scorer.py        # Player scoring algorithm
    └── waiver_recommender.py   # Recommendation generation and display
```

## Key Components

### 1. SleeperClient (`src/sleeper_client.py`)
- Handles all Sleeper API interactions
- Implements rate limiting (100 calls/minute)
- Intelligent caching with different TTLs:
  - Player data: 7 days
  - League settings: 24 hours
  - Rosters: 1 hour
  - Stats/Projections: 6 hours
  - Trending players: 1 hour
- Base URL: `https://api.sleeper.app/v1`

### 2. LeagueAnalyzer (`src/league_analyzer.py`)
- Processes league structure and rosters
- Identifies available players
- Analyzes roster composition and needs
- Handles transaction history

### 3. PlayerScorer (`src/player_scorer.py`)
- Scoring algorithm weights:
  - Recent Performance: 35%
  - Season Average: 20%
  - Projections: 25%
  - Consistency: 10%
  - Trending bonus: 10%
- Uses league-specific scoring settings

### 4. WaiverRecommender (`src/waiver_recommender.py`)
- Generates personalized recommendations
- Prioritizes based on roster needs
- Rich terminal display with tables
- Shows trending players and recent transactions

## Configuration

### Environment Variables (.env)
```bash
LEAGUE_ID=your_league_id_here
SEASON=2024
CURRENT_WEEK=1
```

### Command Line Arguments
- `--league-id`: Override league ID
- `--season`: NFL season (default: 2024)
- `--week`: Current NFL week
- `--user`: Username to analyze
- `--position`: Filter by position (QB, RB, WR, TE, K, DEF)
- `--top`: Number of recommendations (default: 15)
- `--clear-cache`: Clear cache before running

## API Endpoints Used
- `/league/{league_id}` - League settings
- `/league/{league_id}/rosters` - Team rosters
- `/league/{league_id}/users` - League users
- `/league/{league_id}/matchups/{week}` - Weekly matchups
- `/league/{league_id}/transactions/{week}` - Transactions
- `/players/nfl` - All NFL players
- `/players/nfl/trending/{type}` - Trending players
- `/stats/nfl/regular/{season}/{week}` - Weekly stats
- `/projections/nfl/regular/{season}/{week}` - Projections

## Development Guidelines

### Code Style
- Uses standard Python conventions
- Rich console for all output formatting
- Error handling with try/except blocks
- Type hints for function parameters

### Testing
- No test framework currently implemented
- Manual testing via CLI usage

### Performance Considerations
- Limits available player pool to top 200 per position
- Fetches stats for last 5 weeks only
- Uses disk cache to minimize API calls
- Rate limiting prevents API throttling

## Common Tasks

### Running the Application
```bash
python main.py
```

### Adding New Features
1. Check existing patterns in `src/` modules
2. Follow the established architecture:
   - API calls through `SleeperClient`
   - Data processing in `LeagueAnalyzer`
   - Scoring logic in `PlayerScorer`
   - Display logic in `WaiverRecommender`

### Debugging
- Check cache directory for persisted data
- Use `--clear-cache` to force fresh API calls
- API responses are JSON format
- Rate limit: 100 calls per minute

## Known Limitations
- Sleeper API rate limit: 100 requests/minute
- Player pool limited to top 200 per position
- Historical stats limited to last 5 weeks
- No automated tests
- No logging framework (uses print statements)

## Future Enhancements
Consider implementing:
- Logging framework for better debugging
- Unit tests for core logic
- Configuration file support
- Database storage option
- Web interface
- Advanced analytics (strength of schedule, matchup analysis)
- Trade recommendations
- Automated lineup optimization

## Dependencies Security
All dependencies use stable versions. Run `pip list --outdated` periodically to check for updates.