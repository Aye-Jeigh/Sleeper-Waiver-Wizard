# Sleeper Waiver Wire Assistant

A Python tool that analyzes your Sleeper fantasy football league and provides intelligent waiver wire recommendations based on player performance, roster needs, and trends.

## Features

- **Smart Recommendations**: Analyzes your roster composition and suggests players based on positional needs
- **Performance Scoring**: Evaluates players using recent performance, season averages, projections, and consistency
- **Flexible Scoring Systems**: Supports PPR, Half-PPR, Standard, Superflex, and custom scoring configurations
- **Auto-Detection**: Automatically detects your league's scoring system from Sleeper API
- **Trend Analysis**: Identifies trending players being added across Sleeper leagues
- **Rate Limiting**: Respects Sleeper API limits with built-in rate limiting (100 calls/minute)
- **Intelligent Caching**: Caches API responses to minimize requests and improve performance
- **Rich Display**: Beautiful terminal output with tables and colored indicators

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd sleeper-waiver-wire
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp .env.example .env
```

4. Edit `.env` with your league information:
```
LEAGUE_ID=your_league_id_here
SEASON=2024
CURRENT_WEEK=1
```

To find your league ID:
- Go to your Sleeper league in a web browser
- The URL will be: `https://sleeper.com/leagues/LEAGUE_ID/...`
- Copy the numeric league ID

## Usage

### Basic Usage
```bash
python main.py
```
This will prompt you to select a team and show recommendations.

### Command Line Options
```bash
# Specify user directly
python main.py --user "YourUsername"

# Filter by position
python main.py --position RB

# Show more recommendations
python main.py --top 20

# Clear cache before running
python main.py --clear-cache

# Override league/week settings
python main.py --league-id 123456789 --week 5

# Use PPR scoring (overrides league settings)
python main.py --scoring ppr

# Use Half-PPR scoring
python main.py --scoring half_ppr

# List available scoring presets
python main.py --list-scoring

# Save your league's scoring as custom
python main.py --save-scoring
```

### Scoring Systems

The tool supports multiple scoring systems:

#### Built-in Presets
- **standard**: Traditional scoring without PPR
- **ppr**: Full point per reception
- **half_ppr**: Half point per reception  
- **superflex**: 6-point passing TDs for 2QB/superflex leagues
- **dynasty**: PPR with TE premium

#### Using Custom Scoring
1. **Auto-detect**: By default, the tool uses your league's Sleeper scoring settings
2. **Override with preset**: Use `--scoring ppr` to force a specific system
3. **Save custom**: Use `--save-scoring` to save your league settings for future use
4. **Manual configuration**: Create a `.env.scoring.json` file with custom point values

#### Scoring Impact Example
PPR vs Standard scoring for a WR with 5 catches, 75 yards, 1 TD:
- **Standard**: 13.5 points (7.5 rec yards + 6 TD)
- **PPR**: 18.5 points (+5.0 points for receptions)
- **Half-PPR**: 16.0 points (+2.5 points for receptions)

This shows how PPR significantly increases the value of pass-catching players.

## How It Works

The assistant evaluates waiver wire candidates using multiple factors:

### Scoring Algorithm
- **Recent Performance (35%)**: Average points from last 3 games
- **Season Average (20%)**: Overall season performance
- **Projections (25%)**: Next week's projected points
- **Consistency (10%)**: How reliable the player's scoring is
- **Trending (10%)**: Bonus if player is trending on Sleeper

### Roster Need Analysis
Players are prioritized based on your roster needs:
- **Critical**: Positions where you're significantly below ideal roster size
- **Moderate**: Positions needing one more player
- **Depth**: Positions where additional depth would be beneficial

## Caching

The tool uses intelligent caching to minimize API calls:
- Player data: 7 days
- League settings: 24 hours  
- Rosters: 1 hour
- Stats/Projections: 6 hours
- Trending players: 1 hour

Cache is stored in `./cache` directory.

## Example Output

```
╔══════════════════════════════════════════════════╗
║     Waiver Wire Recommendations for UserName      ║
╚══════════════════════════════════════════════════╝

┌──────┬────────────────────┬─────┬─────┬────────┬────────┬────────┬────────┬──────────┬──────────┐
│ Rank │ Player             │ Pos │ Team│  Score │ Avg Pts│ Recent │  Proj  │   Need   │  Status  │
├──────┼────────────────────┼─────┼─────┼────────┼────────┼────────┼────────┼──────────┼──────────┤
│  1   │ Player Name        │ RB  │ LAR │  18.5  │  12.3  │  15.7  │  14.2  │ critical │ 🔥 TRENDING│
│  2   │ Another Player     │ WR  │ SF  │  16.2  │  10.5  │  13.2  │  11.8  │ moderate │          │
└──────┴────────────────────┴─────┴─────┴────────┴────────┴────────┴────────┴──────────┴──────────┘
```

## Limitations

- Sleeper API rate limit: 100 requests per minute
- Player pool limited to top 200 available players per position for performance
- Historical stats limited to last 5 weeks for analysis

## Troubleshooting

### "Error: League ID is required"
Make sure you've either:
- Set `LEAGUE_ID` in your `.env` file, or
- Pass it via command line: `python main.py --league-id YOUR_ID`

### Rate limit errors
The tool has built-in rate limiting, but if you encounter issues:
- Use `--clear-cache` sparingly
- Wait a minute between runs if fetching fresh data

### No recommendations showing
- Check that you're using the correct week number
- Verify players are actually available (not on waivers)
- Try a different position filter

### Scoring System Issues
- Use `--list-scoring` to see available presets
- Check your league's scoring settings match expectations
- Use `--save-scoring` to persist your league's custom scoring
- PPR players will have higher values in PPR modes

## Advanced Usage

### Creating Custom Scoring
Create a `.env.scoring.json` file for completely custom scoring:

```json
{
  "pts_pass_yd": 0.04,
  "pts_pass_td": 6,
  "pts_pass_int": -2,
  "pts_rush_yd": 0.1,
  "pts_rush_td": 6,
  "pts_rec": 1.0,
  "pts_rec_yd": 0.1,
  "pts_rec_td": 6,
  "pts_te_rec": 1.5,
  "pts_fum_lost": -2
}
```

### Scoring Preset Details
- **Standard**: Traditional 0.04 per passing yard, 0.1 per rushing/receiving yard
- **PPR**: Adds 1 point per reception
- **Half-PPR**: Adds 0.5 points per reception
- **Superflex**: 6-point passing TDs (vs 4 standard) for 2QB leagues
- **Dynasty**: PPR + TE premium (1.5 points per TE reception)