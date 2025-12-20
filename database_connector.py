"""
NBA Database to CSV - Simple Export for Machine Learning
=========================================================
This script exports your NBA database tables to CSV files
for easy machine learning processing.
"""

import pandas as pd
import sqlite3

# Configuration
DB_PATH = './nba.sqlite'  # UPDATE THIS PATH
OUTPUT_DIR = './csv_exports/'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("NBA DATABASE TO CSV EXPORT")
print("="*70)

connection = sqlite3.connect(DB_PATH)

# ============================================================================
# 1. TEAM GAME DATA - Ready for ML
# ============================================================================

print("\n1. Exporting team game data...")

# Get all team data
team_query = """
SELECT *
FROM team
LIMIT 10000
"""

team_df = pd.read_sql(team_query, connection)
print(f"   Loaded {len(team_df)} rows with {len(team_df.columns)} columns")

# Save to CSV
team_df.to_csv(f'{OUTPUT_DIR}team_games.csv', index=False)
print(f"   ✓ Saved: {OUTPUT_DIR}team_games.csv")

# Show sample
print("\nSample data (first 3 rows):")
print(team_df.head(3).to_string())

# ============================================================================
# 2. AGGREGATED TEAM SEASON DATA - Ready for ML
# ============================================================================

print("\n" + "="*70)
print("2. Creating aggregated season data...")

# Try to detect column names
sample = team_df.head()
season_col = None
team_col = None
outcome_col = None

# Find season column
for col in ['slugSeason', 'season', 'SEASON', 'yearSeason']:
    if col in sample.columns:
        season_col = col
        break

# Find team column
for col in ['nameTeam', 'teamName', 'TEAM_NAME', 'team']:
    if col in sample.columns:
        team_col = col
        break

# Find outcome column
for col in ['outcomeGame', 'WL', 'outcome', 'W_L']:
    if col in sample.columns:
        outcome_col = col
        break

if season_col and team_col and outcome_col:
    print(f"   Detected: season={season_col}, team={team_col}, outcome={outcome_col}")
    
    # Get numeric columns for aggregation
    numeric_cols = team_df.select_dtypes(include=['int64', 'float64']).columns
    
    # Create aggregation dictionary
    agg_dict = {}
    
    # Count wins and losses
    team_df['wins'] = (team_df[outcome_col] == 'W').astype(int)
    team_df['losses'] = (team_df[outcome_col] == 'L').astype(int)
    
    agg_dict['wins'] = 'sum'
    agg_dict['losses'] = 'sum'
    
    # Average key stats
    stat_keywords = ['pts', 'ast', 'reb', 'stl', 'blk', 'tov', 'pct', 'fg', 'ft']
    for col in numeric_cols:
        if any(keyword in col.lower() for keyword in stat_keywords):
            agg_dict[col] = 'mean'
    
    # Aggregate by team and season
    season_agg = team_df.groupby([team_col, season_col]).agg(agg_dict).reset_index()
    
    # Calculate win percentage
    season_agg['win_pct'] = season_agg['wins'] / (season_agg['wins'] + season_agg['losses'])
    season_agg['total_games'] = season_agg['wins'] + season_agg['losses']
    
    print(f"   Created {len(season_agg)} team-season records")
    
    # Save
    season_agg.to_csv(f'{OUTPUT_DIR}team_season_aggregated.csv', index=False)
    print(f"   ✓ Saved: {OUTPUT_DIR}team_season_aggregated.csv")
    
    print("\nSample aggregated data:")
    print(season_agg.head(3).to_string())
else:
    print("   ⚠ Could not detect necessary columns for aggregation")

# ============================================================================
# 3. PLAYER DATA - Ready for ML
# ============================================================================

print("\n" + "="*70)
print("3. Exporting player data...")

player_query = """
SELECT *
FROM player
LIMIT 10000
"""

try:
    player_df = pd.read_sql(player_query, connection)
    print(f"   Loaded {len(player_df)} rows with {len(player_df.columns)} columns")
    
    player_df.to_csv(f'{OUTPUT_DIR}player_data.csv', index=False)
    print(f"   ✓ Saved: {OUTPUT_DIR}player_data.csv")
    
    print("\nPlayer data columns:")
    print(f"   {list(player_df.columns[:10])}...")
except Exception as e:
    print(f"   ⚠ Could not export player data: {e}")

# ============================================================================
# 4. GAME SUMMARY DATA
# ============================================================================

print("\n" + "="*70)
print("4. Exporting game summary data...")

game_query = """
SELECT *
FROM game_summary
LIMIT 10000
"""

try:
    game_df = pd.read_sql(game_query, connection)
    print(f"   Loaded {len(game_df)} rows with {len(game_df.columns)} columns")
    
    game_df.to_csv(f'{OUTPUT_DIR}game_summary.csv', index=False)
    print(f"   ✓ Saved: {OUTPUT_DIR}game_summary.csv")
except Exception as e:
    print(f"   ⚠ Could not export game summary: {e}")

# ============================================================================
# 5. CREATE DATA DICTIONARY
# ============================================================================

print("\n" + "="*70)
print("5. Creating data dictionary...")

# Save column information
with open(f'{OUTPUT_DIR}DATA_DICTIONARY.txt', 'w') as f:
    f.write("NBA DATABASE - CSV EXPORTS DATA DICTIONARY\n")
    f.write("="*70 + "\n\n")
    
    # Team games
    f.write("1. team_games.csv\n")
    f.write("-"*70 + "\n")
    f.write(f"Rows: {len(team_df)}\n")
    f.write(f"Columns: {len(team_df.columns)}\n")
    f.write("Description: Game-by-game team statistics\n\n")
    f.write("Columns:\n")
    for col in team_df.columns:
        dtype = team_df[col].dtype
        non_null = team_df[col].notna().sum()
        f.write(f"  • {col:30s} ({dtype}) - {non_null}/{len(team_df)} non-null\n")
    
    f.write("\n\n")
    
    # Season aggregated
    if season_col and team_col:
        f.write("2. team_season_aggregated.csv\n")
        f.write("-"*70 + "\n")
        f.write(f"Rows: {len(season_agg)}\n")
        f.write(f"Columns: {len(season_agg.columns)}\n")
        f.write("Description: Aggregated team statistics by season\n")
        f.write("Perfect for: Predicting season outcomes, team comparisons\n\n")
        f.write("Columns:\n")
        for col in season_agg.columns:
            f.write(f"  • {col}\n")

print(f"   ✓ Saved: {OUTPUT_DIR}DATA_DICTIONARY.txt")