# Scoring System Examples

## Quick Start with PPR

If your league uses PPR scoring, simply add the `--scoring ppr` flag:

```bash
python main.py --scoring ppr
```

## Available Scoring Presets

View all available scoring presets:

```bash
python main.py --list-scoring
```

Output:
```
┌─────────────────────────────────────────────────┐
│             Available Scoring Presets          │
└─────────────────────────────────────────────────┘
  standard: Traditional fantasy football scoring without PPR
  ppr: Full point per reception scoring
  half_ppr: Half point per reception scoring
  superflex: 6-point passing TD scoring for superflex leagues
  dynasty: PPR with TE premium for dynasty leagues
```

## Common Usage Examples

### PPR League
```bash
python main.py --scoring ppr --user "YourUsername"
```

### Half-PPR League
```bash
python main.py --scoring half_ppr --position WR
```

### Superflex League (6pt passing TDs)
```bash
python main.py --scoring superflex --position QB
```

### Dynasty League (TE Premium)
```bash
python main.py --scoring dynasty --top 20
```

## Saving Your League's Custom Scoring

If your league has unique scoring settings, save them for future use:

```bash
python main.py --save-scoring
```

This creates a `.env.scoring.json` file that will be automatically used in future runs.

## Scoring Impact Examples

### Wide Receiver Performance
**Player stats: 5 catches, 75 yards, 1 TD**

- Standard scoring: 13.5 points
- PPR scoring: 18.5 points (+5.0 points)
- Half-PPR: 16.0 points (+2.5 points)

### Running Back Comparison
**Player A: 15 carries, 80 yards, 1 TD, 2 catches, 15 yards**
**Player B: 10 carries, 60 yards, 0 TD, 6 catches, 45 yards**

Standard scoring:
- Player A: 14.5 points (better choice)
- Player B: 10.5 points

PPR scoring:
- Player A: 16.5 points 
- Player B: 16.5 points (tied!)

This shows how PPR can make pass-catching backs more valuable.

## Environment Variable Setup

Add to your `.env` file:
```bash
LEAGUE_ID=your_league_id_here
SEASON=2024
CURRENT_WEEK=8
```

## Custom Scoring File Format

Create `.env.scoring.json` for completely custom scoring:

```json
{
  "pts_pass_yd": 0.04,
  "pts_pass_td": 4,
  "pts_pass_int": -2,
  "pts_rush_yd": 0.1,
  "pts_rush_td": 6,
  "pts_rec": 1.0,
  "pts_rec_yd": 0.1,
  "pts_rec_td": 6,
  "pts_fum_lost": -2
}
```