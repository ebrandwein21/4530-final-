"""
NBA Team Spending vs Performance - Simple Version
==================================================
This version closely matches the example code structure provided.
Uses Player_Salary table with nameTeam, value, and slugSeason columns.

Database: nba.sqlite from https://www.kaggle.com/datasets/wyattowalsh/basketball
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import plotly.express as px
from scipy import stats

# Configuration
DB_PATH = './nba.sqlite'  # Update this path
SEASON = '2020-21'  # Change to analyze different season
OUTPUT_DIR = './output/'

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Connect to database
print(f"Connecting to database: {DB_PATH}")
connection = sqlite3.connect(DB_PATH)

# ============================================================================
# 1. GET TOP 10 HIGHEST PAYING TEAMS (Like the example)
# ============================================================================

query = """
    SELECT 
        nameTeam AS team_name,
        ROUND(AVG(value/1000000), 2) AS avg_salary_in_millions,
        ROUND(SUM(value/1000000), 2) AS total_payroll_millions,
        COUNT(*) AS num_players
    FROM Player_Salary
    WHERE slugSeason = ?
    GROUP BY team_name
    ORDER BY total_payroll_millions DESC
    LIMIT 10;
"""

team_top_10_paying = pd.read_sql(query, connection, params=(SEASON,))

# Create bar chart like the example
fig = px.bar(
    team_top_10_paying, 
    x="team_name", 
    y="total_payroll_millions", 
    text="total_payroll_millions",
    title=f"Top 10 Highest Paying NBA Teams ({SEASON})",
    labels={
        'team_name': 'Team',
        'total_payroll_millions': 'Total Payroll ($ Millions)'
    }
)
fig.update_traces(texttemplate='$%{text:.1f}M', textposition='outside')
fig.write_html(f'{OUTPUT_DIR}top_10_paying_teams.html')
fig.show()

print("\n" + "="*70)
print(f"TOP 10 HIGHEST PAYING TEAMS - {SEASON}")
print("="*70)
print(team_top_10_paying.to_string(index=False))

# ============================================================================
# 2. GET ALL TEAM SALARIES FOR THE SEASON
# ============================================================================

query_all_teams = """
    SELECT 
        nameTeam AS team_name,
        ROUND(SUM(value/1000000), 2) AS total_payroll_millions,
        ROUND(AVG(value/1000000), 2) AS avg_salary_millions,
        COUNT(*) AS num_players
    FROM Player_Salary
    WHERE slugSeason = ?
    GROUP BY team_name
    ORDER BY total_payroll_millions DESC;
"""

team_salaries = pd.read_sql(query_all_teams, connection, params=(SEASON,))

# ============================================================================
# 3. GET TEAM PERFORMANCE (WINS, LOSSES, WIN%)
# ============================================================================

# First check what columns exist in the Team table
check_query = "PRAGMA table_info(Team)"
team_columns = pd.read_sql(check_query, connection)
print(f"\nAvailable columns in Team table: {team_columns['name'].tolist()[:10]}...")

# Get team performance data
performance_query = """
    SELECT 
        nameTeam AS team_name,
        slugSeason AS season,
        SUM(CASE WHEN outcomeGame = 'W' THEN 1 ELSE 0 END) AS wins,
        SUM(CASE WHEN outcomeGame = 'L' THEN 1 ELSE 0 END) AS losses,
        COUNT(*) AS games_played
    FROM Team
    WHERE slugSeason = ?
    GROUP BY nameTeam, slugSeason
"""

team_performance = pd.read_sql(performance_query, connection, params=(SEASON,))

# Calculate win percentage
team_performance['win_pct'] = team_performance['wins'] / team_performance['games_played']

# ============================================================================
# 4. MERGE SALARY AND PERFORMANCE DATA
# ============================================================================

spending_vs_performance = pd.merge(
    team_salaries,
    team_performance,
    on='team_name',
    how='inner'
)

print("\n" + "="*70)
print(f"TEAM SPENDING VS PERFORMANCE - {SEASON}")
print("="*70)
print(spending_vs_performance[['team_name', 'total_payroll_millions', 'wins', 
                               'losses', 'win_pct']].to_string(index=False))

# ============================================================================
# 5. CALCULATE EFFICIENCY METRICS
# ============================================================================

spending_vs_performance['wins_per_million'] = (
    spending_vs_performance['wins'] / spending_vs_performance['total_payroll_millions']
)

spending_vs_performance['cost_per_win_millions'] = (
    spending_vs_performance['total_payroll_millions'] / spending_vs_performance['wins']
)

# ============================================================================
# 6. STATISTICAL ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("STATISTICAL ANALYSIS")
print("="*70)

# Correlation
correlation = spending_vs_performance['total_payroll_millions'].corr(
    spending_vs_performance['win_pct']
)
print(f"\nCorrelation (Payroll vs Win%): {correlation:.4f}")

# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(
    spending_vs_performance['total_payroll_millions'],
    spending_vs_performance['win_pct']
)

print(f"\nLinear Regression:")
print(f"  R-squared: {r_value**2:.4f}")
print(f"  P-value: {p_value:.6f}")
print(f"  Interpretation: Each $1M increase → {slope*100:.3f}% higher win%")

# ============================================================================
# 7. IDENTIFY MOST AND LEAST EFFICIENT TEAMS
# ============================================================================

print("\n" + "="*70)
print("MOST EFFICIENT TEAMS (Best Value)")
print("="*70)
most_efficient = spending_vs_performance.nlargest(5, 'wins_per_million')[
    ['team_name', 'total_payroll_millions', 'wins', 'win_pct', 'wins_per_million']
]
print(most_efficient.to_string(index=False))

print("\n" + "="*70)
print("LEAST EFFICIENT TEAMS (Overspending)")
print("="*70)
least_efficient = spending_vs_performance.nsmallest(5, 'wins_per_million')[
    ['team_name', 'total_payroll_millions', 'wins', 'win_pct', 'wins_per_million']
]
print(least_efficient.to_string(index=False))

# ============================================================================
# 8. CREATE VISUALIZATIONS
# ============================================================================

# Visualization 1: Payroll vs Win Percentage Scatter
fig1, ax1 = plt.subplots(figsize=(12, 8))
scatter = ax1.scatter(
    spending_vs_performance['total_payroll_millions'],
    spending_vs_performance['win_pct'],
    s=200,
    alpha=0.6,
    c=spending_vs_performance['wins'],
    cmap='RdYlGn'
)

# Add team labels
for idx, row in spending_vs_performance.iterrows():
    ax1.annotate(
        row['team_name'],
        (row['total_payroll_millions'], row['win_pct']),
        fontsize=8,
        ha='center'
    )

# Add regression line
x_line = np.linspace(
    spending_vs_performance['total_payroll_millions'].min(),
    spending_vs_performance['total_payroll_millions'].max(),
    100
)
y_line = slope * x_line + intercept
ax1.plot(x_line, y_line, 'r--', linewidth=2, label=f'R² = {r_value**2:.3f}')

ax1.set_xlabel('Total Payroll ($ Millions)', fontsize=12)
ax1.set_ylabel('Win Percentage', fontsize=12)
ax1.set_title(f'Team Spending vs Performance - {SEASON}', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
plt.colorbar(scatter, label='Wins', ax=ax1)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}payroll_vs_winpct.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualization 2: Efficiency Rankings
fig2, ax2 = plt.subplots(figsize=(12, 10))
sorted_data = spending_vs_performance.sort_values('wins_per_million', ascending=True)
colors = ['red' if x < sorted_data['wins_per_million'].median() else 'green' 
          for x in sorted_data['wins_per_million']]

ax2.barh(sorted_data['team_name'], sorted_data['wins_per_million'], color=colors, alpha=0.7)
ax2.set_xlabel('Wins per Million Dollars', fontsize=12)
ax2.set_ylabel('Team', fontsize=12)
ax2.set_title(f'Team Efficiency Rankings - {SEASON}', fontsize=14, fontweight='bold')
ax2.axvline(sorted_data['wins_per_million'].median(), color='black', 
            linestyle='--', linewidth=2, label='Median')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}efficiency_rankings.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualization 3: Spending Tiers
fig3, ax3 = plt.subplots(figsize=(10, 6))
spending_vs_performance['spending_tier'] = pd.qcut(
    spending_vs_performance['total_payroll_millions'],
    q=3,
    labels=['Low Spenders', 'Mid Spenders', 'High Spenders']
)

spending_vs_performance.boxplot(
    column='win_pct',
    by='spending_tier',
    ax=ax3
)
ax3.set_xlabel('Spending Tier', fontsize=12)
ax3.set_ylabel('Win Percentage', fontsize=12)
ax3.set_title(f'Win % by Spending Tier - {SEASON}', fontsize=14, fontweight='bold')
plt.suptitle('')  # Remove automatic title
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}spending_tiers.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# 9. SAVE RESULTS
# ============================================================================

# Save the merged data
spending_vs_performance.to_csv(f'{OUTPUT_DIR}spending_vs_performance_{SEASON}.csv', index=False)
print(f"\n✅ Results saved to {OUTPUT_DIR}")

# Close database connection
connection.close()

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print(f"\nFiles created:")
print(f"  • {OUTPUT_DIR}top_10_paying_teams.html")
print(f"  • {OUTPUT_DIR}payroll_vs_winpct.png")
print(f"  • {OUTPUT_DIR}efficiency_rankings.png")
print(f"  • {OUTPUT_DIR}spending_tiers.png")
print(f"  • {OUTPUT_DIR}spending_vs_performance_{SEASON}.csv")