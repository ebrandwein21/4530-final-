"""
NBA Team Spending vs Performance Analysis
==========================================
This script analyzes the relationship between team spending (payroll) and 
performance metrics using NBA data from Kaggle.

Requirements:
- pandas
- numpy
- matplotlib
- seaborn
- sqlite3 (built-in)
- scipy

Dataset: Download from https://www.kaggle.com/datasets/wyattowalsh/basketball
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from scipy import stats
from pathlib import Path

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


def load_data_from_sqlite(db_path):
    """
    Load data from SQLite database (Wyatt Walsh NBA Database format)
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary containing relevant dataframes
    """
    conn = sqlite3.connect(db_path)
    
    # Load team stats
    team_stats_query = """
    SELECT * FROM team
    """
    team_stats = pd.read_sql_query(team_stats_query, conn)
    
    # Load salary data if available
    try:
        salary_query = """
        SELECT * FROM team_salary
        """
        salary_data = pd.read_sql_query(salary_query, conn)
    except:
        print("Warning: team_salary table not found. Will attempt alternative approach.")
        salary_data = None
    
    conn.close()
    
    return {
        'team_stats': team_stats,
        'salary_data': salary_data
    }


def load_data_from_csv(data_dir):
    """
    Load data from CSV files (alternative method)
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Dictionary containing relevant dataframes
    """
    data_dir = Path(data_dir)
    
    # Common CSV file names in NBA Kaggle datasets
    possible_files = {
        'team_stats': ['team_stats.csv', 'teams.csv', 'team.csv'],
        'salary': ['team_salary.csv', 'salaries.csv', 'team_salaries.csv', 'payroll.csv']
    }
    
    data = {}
    
    for key, filenames in possible_files.items():
        for filename in filenames:
            filepath = data_dir / filename
            if filepath.exists():
                data[key] = pd.read_csv(filepath)
                print(f"Loaded {filename}")
                break
    
    return data


def calculate_team_performance(team_stats, season_col='season', team_col='team_abbreviation'):
    """
    Calculate performance metrics for each team by season
    
    Args:
        team_stats: DataFrame with team statistics
        season_col: Name of season column
        team_col: Name of team identifier column
        
    Returns:
        DataFrame with calculated performance metrics
    """
    # Group by season and team
    if season_col not in team_stats.columns:
        # Try to find season column
        season_cols = [col for col in team_stats.columns if 'season' in col.lower() or 'year' in col.lower()]
        if season_cols:
            season_col = season_cols[0]
        else:
            raise ValueError("Cannot find season column")
    
    if team_col not in team_stats.columns:
        # Try to find team column
        team_cols = [col for col in team_stats.columns if 'team' in col.lower() and 'abbr' in col.lower()]
        if not team_cols:
            team_cols = [col for col in team_stats.columns if 'team' in col.lower()]
        if team_cols:
            team_col = team_cols[0]
        else:
            raise ValueError("Cannot find team column")
    
    # Calculate win percentage and other performance metrics
    performance = team_stats.groupby([season_col, team_col]).agg({
        'wins': 'sum' if 'wins' in team_stats.columns else 'count',
        'losses': 'sum' if 'losses' in team_stats.columns else 'count',
    })
    
    # Calculate win percentage
    if 'wins' in performance.columns and 'losses' in performance.columns:
        performance['win_pct'] = performance['wins'] / (performance['wins'] + performance['losses'])
    
    # Calculate additional metrics if available
    if 'pts' in team_stats.columns:
        performance['avg_points'] = team_stats.groupby([season_col, team_col])['pts'].mean()
    
    if 'plus_minus' in team_stats.columns:
        performance['avg_plus_minus'] = team_stats.groupby([season_col, team_col])['plus_minus'].mean()
    
    performance.reset_index(inplace=True)
    
    return performance


def merge_spending_performance(salary_data, performance_data, season_col='season', team_col='team_abbreviation'):
    """
    Merge salary and performance data
    
    Args:
        salary_data: DataFrame with salary/payroll information
        performance_data: DataFrame with performance metrics
        season_col: Name of season column
        team_col: Name of team identifier column
        
    Returns:
        Merged DataFrame
    """
    # Aggregate salary by team and season
    salary_cols = [col for col in salary_data.columns if 'salary' in col.lower() or 'payroll' in col.lower()]
    
    if salary_cols:
        salary_col = salary_cols[0]
    else:
        raise ValueError("Cannot find salary column in data")
    
    # Group and sum salaries
    team_payroll = salary_data.groupby([season_col, team_col])[salary_col].sum().reset_index()
    team_payroll.columns = [season_col, team_col, 'total_payroll']
    
    # Merge with performance
    merged = pd.merge(
        performance_data,
        team_payroll,
        on=[season_col, team_col],
        how='inner'
    )
    
    # Convert salary to millions for easier interpretation
    merged['payroll_millions'] = merged['total_payroll'] / 1_000_000
    
    return merged


def analyze_spending_performance(merged_data):
    """
    Perform statistical analysis on spending vs performance
    
    Args:
        merged_data: DataFrame with merged salary and performance data
        
    Returns:
        Dictionary with analysis results
    """
    results = {}
    
    # Correlation analysis
    if 'win_pct' in merged_data.columns and 'payroll_millions' in merged_data.columns:
        correlation = merged_data[['payroll_millions', 'win_pct']].corr().iloc[0, 1]
        results['correlation'] = correlation
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            merged_data['payroll_millions'],
            merged_data['win_pct']
        )
        
        results['regression'] = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'p_value': p_value,
            'std_err': std_err
        }
    
    # Calculate efficiency: wins per million dollars
    merged_data['efficiency'] = merged_data['wins'] / merged_data['payroll_millions']
    
    # Find most and least efficient teams
    results['most_efficient'] = merged_data.nlargest(5, 'efficiency')[
        ['team_abbreviation', 'season', 'payroll_millions', 'wins', 'win_pct', 'efficiency']
    ]
    
    results['least_efficient'] = merged_data.nsmallest(5, 'efficiency')[
        ['team_abbreviation', 'season', 'payroll_millions', 'wins', 'win_pct', 'efficiency']
    ]
    
    return results, merged_data


def create_visualizations(merged_data, results, output_dir='./output'):
    """
    Create visualizations for spending vs performance analysis
    
    Args:
        merged_data: DataFrame with merged salary and performance data
        results: Dictionary with analysis results
        output_dir: Directory to save plots
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. Scatter plot: Payroll vs Win Percentage
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=merged_data, x='payroll_millions', y='win_pct', 
                    alpha=0.6, s=100)
    
    # Add regression line
    if 'regression' in results:
        x_line = np.linspace(merged_data['payroll_millions'].min(), 
                             merged_data['payroll_millions'].max(), 100)
        y_line = results['regression']['slope'] * x_line + results['regression']['intercept']
        plt.plot(x_line, y_line, 'r--', linewidth=2, 
                label=f"R² = {results['regression']['r_squared']:.3f}")
    
    plt.xlabel('Team Payroll ($ Millions)', fontsize=12)
    plt.ylabel('Win Percentage', fontsize=12)
    plt.title('NBA Team Spending vs Performance', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/payroll_vs_winpct.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Box plot: Win percentage by payroll quartiles
    plt.figure(figsize=(10, 6))
    merged_data['payroll_quartile'] = pd.qcut(merged_data['payroll_millions'], 
                                                q=4, labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    sns.boxplot(data=merged_data, x='payroll_quartile', y='win_pct', palette='Set2')
    plt.xlabel('Payroll Quartile', fontsize=12)
    plt.ylabel('Win Percentage', fontsize=12)
    plt.title('Win Percentage Distribution by Payroll Quartile', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/winpct_by_quartile.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Efficiency plot: Wins per million dollars
    plt.figure(figsize=(14, 8))
    top_20_efficient = merged_data.nlargest(20, 'efficiency')
    sns.barplot(data=top_20_efficient, 
                x='efficiency', 
                y='team_abbreviation',
                hue='season',
                dodge=False)
    plt.xlabel('Wins per Million Dollars', fontsize=12)
    plt.ylabel('Team', fontsize=12)
    plt.title('Top 20 Most Efficient Teams (Wins per $M)', fontsize=14, fontweight='bold')
    plt.legend(title='Season', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/efficiency_rankings.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Time series: Average payroll and win pct by season
    if 'season' in merged_data.columns:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        season_avg = merged_data.groupby('season').agg({
            'payroll_millions': 'mean',
            'win_pct': 'mean'
        }).reset_index()
        
        ax1.plot(season_avg['season'], season_avg['payroll_millions'], 
                'b-o', linewidth=2, label='Avg Payroll')
        ax1.set_xlabel('Season', fontsize=12)
        ax1.set_ylabel('Average Payroll ($ Millions)', fontsize=12, color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2 = ax1.twinx()
        ax2.plot(season_avg['season'], season_avg['win_pct'], 
                'r-s', linewidth=2, label='Avg Win %')
        ax2.set_ylabel('Average Win Percentage', fontsize=12, color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        plt.title('NBA Payroll and Performance Trends Over Time', 
                 fontsize=14, fontweight='bold')
        fig.tight_layout()
        plt.savefig(f'{output_dir}/trends_over_time.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"\nVisualizations saved to {output_dir}/")


def print_analysis_summary(results):
    """
    Print summary of analysis results
    
    Args:
        results: Dictionary with analysis results
    """
    print("\n" + "="*70)
    print("NBA TEAM SPENDING VS PERFORMANCE ANALYSIS")
    print("="*70)
    
    if 'correlation' in results:
        print(f"\nCorrelation between Payroll and Win%: {results['correlation']:.4f}")
    
    if 'regression' in results:
        reg = results['regression']
        print(f"\nLinear Regression Results:")
        print(f"  - R-squared: {reg['r_squared']:.4f}")
        print(f"  - Slope: {reg['slope']:.6f}")
        print(f"  - P-value: {reg['p_value']:.6f}")
        print(f"  - Interpretation: For every $1M increase in payroll,")
        print(f"    win percentage increases by {reg['slope']:.4f} (or {reg['slope']*100:.2f}%)")
    
    print("\n" + "-"*70)
    print("MOST EFFICIENT TEAMS (Highest Wins per $M):")
    print("-"*70)
    print(results['most_efficient'].to_string(index=False))
    
    print("\n" + "-"*70)
    print("LEAST EFFICIENT TEAMS (Lowest Wins per $M):")
    print("-"*70)
    print(results['least_efficient'].to_string(index=False))
    print("\n" + "="*70)


def main():
    """
    Main execution function
    """
    print("NBA Team Spending vs Performance Analysis")
    print("=" * 70)
    
    # Option 1: Load from SQLite database
    print("\nChoose data source:")
    print("1. SQLite database (nba.sqlite)")
    print("2. CSV files (directory)")
    
    # For demonstration, assuming CSV files
    # Modify these paths based on your data location
    db_dir = "./nba.sqlite"  # Change this to your data directory
    
    print(f"\nAttempting to load data from {db_dir}...")
    
    # Load data
    # data = load_data_from_csv(data_dir)
    data = load_data_from_sqlite(db_dir)
    
    if 'team_stats' not in data:
        print("Error: Could not find team statistics file.")
        print("\nPlease ensure you have downloaded the NBA dataset from Kaggle:")
        print("https://www.kaggle.com/datasets/wyattowalsh/basketball")
        return
    
    if 'salary' not in data:
        print("Warning: Could not find salary data file.")
        print("This analysis requires both team statistics and salary data.")
        return
    
    # Calculate performance metrics
    print("\nCalculating team performance metrics...")
    performance = calculate_team_performance(data['team_stats'])
    
    # Merge spending and performance
    print("Merging spending and performance data...")
    merged_data = merge_spending_performance(data['salary'], performance)
    
    print(f"Successfully merged {len(merged_data)} team-seasons")
    
    # Analyze
    print("\nPerforming statistical analysis...")
    results, merged_data = analyze_spending_performance(merged_data)
    
    # Print summary
    print_analysis_summary(results)
    
    # Create visualizations
    print("\nCreating visualizations...")
    create_visualizations(merged_data, results)
    
    # Save processed data
    output_file = './output/spending_vs_performance_data.csv'
    merged_data.to_csv(output_file, index=False)
    print(f"\nProcessed data saved to {output_file}")
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()