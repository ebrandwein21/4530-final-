# NBA Team Spending vs Performance Analysis

This Python script analyzes the relationship between NBA team spending (payroll) and performance metrics using data from Kaggle.

## 📊 What This Script Does

1. **Loads NBA data** from Kaggle datasets (SQLite or CSV format)
2. **Calculates performance metrics** (win percentage, efficiency, etc.)
3. **Merges salary and performance data** by team and season
4. **Performs statistical analysis**:
   - Correlation between payroll and win percentage
   - Linear regression analysis
   - Identifies most/least efficient teams (wins per million dollars)
5. **Creates visualizations**:
   - Scatter plot with regression line
   - Win percentage by payroll quartile
   - Efficiency rankings
   - Trends over time

## 📦 Requirements

```bash
pip install pandas numpy matplotlib seaborn scipy
```

## 📥 Data Sources

### Recommended Kaggle Datasets:

1. **Wyatt Walsh's NBA Database** (Recommended)
   - URL: https://www.kaggle.com/datasets/wyattowalsh/basketball
   - Format: SQLite database with comprehensive stats and salary data

2. **Alternative Datasets**:
   - https://www.kaggle.com/datasets/nathanlauga/nba-games
   - https://www.kaggle.com/datasets/loganlauton/nba-players-and-team-data

## 🚀 How to Use

### Option 1: Using the Script Directly

1. Download the NBA dataset from Kaggle
2. Extract the files to a directory (e.g., `./nba_data`)
3. Update the `data_dir` path in the script's `main()` function
4. Run the script:

```bash
python nba_spending_vs_performance.py
```

### Option 2: Custom Data Loading

Modify the script to match your specific dataset structure:

```python
# In the main() function, update:
data_dir = "./your_data_directory"

# Or use SQLite:
db_path = "./nba.sqlite"
data = load_data_from_sqlite(db_path)
```

## 📁 Expected Data Structure

The script expects datasets with the following information:

### Team Stats File (CSV or table)
- `season` or `year`: Season identifier
- `team_abbreviation` or `team`: Team identifier
- `wins`: Number of wins
- `losses`: Number of losses
- Additional stats (optional): `pts`, `plus_minus`, etc.

### Salary File (CSV or table)
- `season` or `year`: Season identifier
- `team_abbreviation` or `team`: Team identifier
- `salary` or `payroll`: Salary amount

## 📈 Output

The script generates:

1. **Console Output**:
   - Correlation coefficient
   - Regression statistics (R², p-value, slope)
   - Most efficient teams (top 5)
   - Least efficient teams (bottom 5)

2. **Visualizations** (saved to `./output/`):
   - `payroll_vs_winpct.png`: Scatter plot with regression line
   - `winpct_by_quartile.png`: Box plot by payroll quartile
   - `efficiency_rankings.png`: Top 20 most efficient teams
   - `trends_over_time.png`: Time series of payroll and performance

3. **Data File**:
   - `spending_vs_performance_data.csv`: Merged dataset with calculations

## 🔧 Customization

### Modify Performance Metrics

```python
# In calculate_team_performance(), add custom metrics:
if 'offensive_rating' in team_stats.columns:
    performance['off_rating'] = team_stats.groupby([season_col, team_col])['offensive_rating'].mean()
```

### Change Visualization Styles

```python
# Update in create_visualizations():
sns.set_style("darkgrid")  # Options: white, dark, whitegrid, darkgrid, ticks
plt.rcParams['figure.figsize'] = (16, 10)  # Adjust figure size
```

### Focus on Specific Seasons

```python
# Filter data before analysis:
merged_data = merged_data[merged_data['season'] >= 2015]
```

## 📊 Example Analysis Questions

This script can help answer:

- Does higher spending lead to more wins?
- Which teams are most efficient with their payroll?
- How has the spending-performance relationship changed over time?
- What's the average payroll for playoff teams vs non-playoff teams?
- Is there a salary cap effect on competitive balance?

## 🔍 Interpretation Guide

### Correlation Coefficient
- **0.5 to 1.0**: Strong positive correlation (higher spending → better performance)
- **0.3 to 0.5**: Moderate positive correlation
- **0.0 to 0.3**: Weak correlation
- **Negative values**: Inverse relationship (rare in this context)

### R-squared Value
- **0.7 to 1.0**: Strong predictive model
- **0.4 to 0.7**: Moderate predictive power
- **0.0 to 0.4**: Weak predictive power

### Efficiency Metric
- Calculated as: `wins / payroll_millions`
- Higher values indicate better value for money
- Useful for identifying teams with smart roster construction

## 🐛 Troubleshooting

**Problem**: "Cannot find season column"
- **Solution**: Check your data column names and update `season_col` parameter

**Problem**: "Cannot find salary column in data"
- **Solution**: Ensure your salary file is in the correct directory and has salary data

**Problem**: No visualizations generated
- **Solution**: Check that the `./output/` directory has write permissions

## 📝 Notes

- The script handles various NBA dataset formats from Kaggle
- Salary data should be in dollars (will be converted to millions automatically)
- Missing data will be filtered out automatically
- For large datasets, processing may take 1-2 minutes

## 📚 Additional Resources

- [Kaggle NBA Datasets](https://www.kaggle.com/search?q=nba+in%3Adatasets)
- [NBA Advanced Stats Glossary](https://www.nba.com/stats/help/glossary)
- [Salary Cap Information](https://www.basketball-reference.com/contracts/)

## 🤝 Contributing

Feel free to modify and enhance this script for your specific analysis needs!

## 📄 License

This script is provided as-is for educational and analysis purposes.