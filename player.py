"""
NBA Player-Team Matching Script
================================
Quick script to match players to their teams and export to CSV
"""

import pandas as pd
import sqlite3

# Configuration
DB_PATH = './nba.sqlite'  # UPDATE THIS
OUTPUT_DIR = './csv_exports/'

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("NBA PLAYER-TEAM MATCHING")
print("="*70)

connection = sqlite3.connect(DB_PATH)

# ============================================================================
# EXPLORE AVAILABLE DATA
# ============================================================================

print("\n1. Checking available tables...")

# Get table names
tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
tables = pd.read_sql(tables_query, connection)
print(f"   Found {len(tables)} tables")

# ============================================================================
# PLAYER DATA
# ============================================================================

print("\n2. Loading player data...")

# Check player table structure
player_sample = pd.read_sql("SELECT * FROM player LIMIT 5", connection)
print(f"   Player table columns: {list(player_sample.columns)[:10]}...")

# Load all players
player_query = "SELECT * FROM player"
players = pd.read_sql(player_query, connection)
print(f"   Loaded {len(players)} player records")

# ============================================================================
# FIND TEAM INFORMATION IN PLAYER TABLE
# ============================================================================

print("\n3. Finding team information...")

# Look for team-related columns in player table
team_cols = [col for col in players.columns if 'team' in col.lower()]
print(f"   Team-related columns in player table: {team_cols}")

# Common column patterns
possible_team_cols = ['teamAbbreviation', 'teamName', 'team', 'TEAM_ABBREVIATION']
possible_name_cols = ['namePlayer', 'playerName', 'PLAYER_NAME', 'name']
possible_season_cols = ['slugSeason', 'season', 'SEASON']

# Detect columns
team_col = next((col for col in possible_team_cols if col in players.columns), None)
name_col = next((col for col in possible_name_cols if col in players.columns), None)
season_col = next((col for col in possible_season_cols if col in players.columns), None)

print(f"   Detected player name column: {name_col}")
print(f"   Detected team column: {team_col}")
print(f"   Detected season column: {season_col}")

# ============================================================================
# CREATE PLAYER-TEAM ROSTER
# ============================================================================

print("\n4. Creating player-team roster...")

if name_col and team_col:
    # Basic roster
    roster_cols = [name_col, team_col]
    if season_col:
        roster_cols.insert(0, season_col)
    
    # Add other useful columns
    useful_cols = []
    for col in ['position', 'pos', 'POSITION', 'jersey', 'numberJersey', 'height', 'weight']:
        if col in players.columns:
            useful_cols.append(col)
    
    roster_cols.extend(useful_cols)
    
    # Create roster dataframe
    roster = players[roster_cols].copy()
    
    # Rename to standard names
    rename_map = {}
    if name_col: rename_map[name_col] = 'player_name'
    if team_col: rename_map[team_col] = 'team'
    if season_col: rename_map[season_col] = 'season'
    
    roster = roster.rename(columns=rename_map)
    
    # Remove duplicates (player might appear multiple times)
    if season_col:
        roster = roster.drop_duplicates(subset=['season', 'player_name', 'team'])
    else:
        roster = roster.drop_duplicates(subset=['player_name', 'team'])
    
    print(f"   Created roster with {len(roster)} player-team combinations")
    
    # Show summary
    print(f"\n   Unique players: {roster['player_name'].nunique()}")
    print(f"   Unique teams: {roster['team'].nunique()}")
    if 'season' in roster.columns:
        print(f"   Seasons covered: {roster['season'].nunique()}")
    
    # Save roster
    roster.to_csv(f'{OUTPUT_DIR}player_team_roster.csv', index=False)
    print(f"\n   ✓ Saved: {OUTPUT_DIR}player_team_roster.csv")
    
    # Show sample
    print("\n   Sample roster:")
    print(roster.head(10).to_string(index=False))
    
    # ========================================================================
    # TEAM SUMMARIES
    # ========================================================================
    
    print("\n5. Creating team summaries...")
    
    # Players per team
    team_summary = roster.groupby('team').agg({
        'player_name': 'count'
    }).reset_index()
    team_summary.columns = ['team', 'num_players']
    team_summary = team_summary.sort_values('num_players', ascending=False)
    
    print("\n   Players per team:")
    print(team_summary.head(10).to_string(index=False))
    
    team_summary.to_csv(f'{OUTPUT_DIR}team_roster_counts.csv', index=False)
    print(f"\n   ✓ Saved: {OUTPUT_DIR}team_roster_counts.csv")
    
    # ========================================================================
    # PLAYER TEAM HISTORY
    # ========================================================================
    
    if 'season' in roster.columns:
        print("\n6. Creating player team history...")
        
        # Count teams per player
        player_teams = roster.groupby('player_name').agg({
            'team': lambda x: list(x.unique()),
            'season': 'count'
        }).reset_index()
        player_teams.columns = ['player_name', 'teams_played_for', 'total_seasons']
        player_teams['num_teams'] = player_teams['teams_played_for'].apply(len)
        
        # Convert list to string for CSV
        player_teams['teams_played_for'] = player_teams['teams_played_for'].apply(
            lambda x: ', '.join(sorted(x))
        )
        
        # Find players who played for multiple teams
        multi_team = player_teams[player_teams['num_teams'] > 1].sort_values('num_teams', ascending=False)
        
        print(f"\n   Players who played for multiple teams: {len(multi_team)}")
        print("\n   Top 10 journeymen (most teams):")
        print(multi_team.head(10).to_string(index=False))
        
        player_teams.to_csv(f'{OUTPUT_DIR}player_team_history.csv', index=False)
        print(f"\n   ✓ Saved: {OUTPUT_DIR}player_team_history.csv")
    
    # ========================================================================
    # SEASON-SPECIFIC ROSTERS
    # ========================================================================
    
    if 'season' in roster.columns:
        print("\n7. Creating season-specific rosters...")
        
        # Get latest season
        latest_season = roster['season'].max()
        print(f"\n   Latest season: {latest_season}")
        
        latest_roster = roster[roster['season'] == latest_season].copy()
        latest_roster = latest_roster.sort_values(['team', 'player_name'])
        
        print(f"   Players in {latest_season}: {len(latest_roster)}")
        
        latest_roster.to_csv(f'{OUTPUT_DIR}roster_{latest_season}.csv', index=False)
        print(f"\n   ✓ Saved: {OUTPUT_DIR}roster_{latest_season}.csv")
        
        # Show sample team
        if len(latest_roster) > 0:
            sample_team = latest_roster['team'].iloc[0]
            print(f"\n   Sample: {sample_team} roster in {latest_season}:")
            print(latest_roster[latest_roster['team'] == sample_team]['player_name'].to_string(index=False))
    
else:
    print("\n   ⚠ Could not find necessary columns for player-team matching")
    print(f"   Available columns: {list(players.columns)}")

# ============================================================================
# ALTERNATIVE: CHECK COMMON_PLAYER_INFO TABLE
# ============================================================================

print("\n" + "="*70)
print("8. Checking common_player_info table...")

try:
    player_info_sample = pd.read_sql("SELECT * FROM common_player_info LIMIT 5", connection)
    print(f"   Columns: {list(player_info_sample.columns)[:15]}...")
    
    player_info = pd.read_sql("SELECT * FROM common_player_info", connection)
    print(f"   Loaded {len(player_info)} records")
    
    player_info.to_csv(f'{OUTPUT_DIR}common_player_info.csv', index=False)
    print(f"   ✓ Saved: {OUTPUT_DIR}common_player_info.csv")
    
except Exception as e:
    print(f"   Could not load common_player_info: {e}")

# ============================================================================
# CHECK TEAM TABLE FOR PLAYER PARTICIPATION
# ============================================================================

print("\n" + "="*70)
print("9. Checking team table for player data...")

try:
    team_sample = pd.read_sql("SELECT * FROM team LIMIT 5", connection)
    
    # Look for player-related columns
    player_cols = [col for col in team_sample.columns if 'player' in col.lower() or 'name' in col.lower()]
    
    if player_cols:
        print(f"   Found player-related columns: {player_cols[:10]}")
    else:
        print("   No player-specific columns in team table")
        
except Exception as e:
    print(f"   Error: {e}")

# ============================================================================
# SUMMARY
# ============================================================================

connection.close()

print("\n" + "="*70)
print("MATCHING COMPLETE!")
print("="*70)

print(f"\nFiles created in {OUTPUT_DIR}:")
print("  1. player_team_roster.csv - Complete player-team roster")
print("  2. team_roster_counts.csv - Number of players per team")
# if 'season' in roster.columns:
#     print("  3. player_team_history.csv - Players and teams they've played for")
#     print(f"  4. roster_{latest_season}.csv - Latest season roster")
# print("  5. common_player_info.csv - Additional player information")

print("\n" + "="*70)
print("USAGE EXAMPLES")
print("="*70)

print("""
# Load the roster
import pandas as pd
roster = pd.read_csv('csv_exports/player_team_roster.csv')

# Find all players on a specific team
lakers = roster[roster['team'] == 'LAL']
print(lakers['player_name'])

# Find which team a player is on
lebron = roster[roster['player_name'].str.contains('LeBron', case=False)]
print(lebron)

# Count players per team
team_counts = roster.groupby('team').size()
print(team_counts.sort_values(ascending=False))

# Filter by season
season_2021 = roster[roster['season'] == '2020-21']
""")

print("\n✓ Player-team matching complete! 🏀")