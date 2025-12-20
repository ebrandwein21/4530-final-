import pandas as pd

# loading the csv files
cPI = commonPlayerInfo = pd.read_csv('archive/csv/common_player_info.csv')
dCS = draftCombineStats = pd.read_csv('archive/csv/draft_combine_stats.csv')

# grab columns needed from each file, and make them smaller datasets
cPI_Col = commonPlayerInfoColumns = ['person_id', 'first_name', 'last_name', 'position', 'school', 'draft_round', 'draft_number']

dCS_Col = draftCombineStatsColumns = ['player_id', 'height_wo_shoes', 'weight', 'wingspan', 'standing_vertical_leap', 'max_vertical_leap', 'lane_agility_time', 'three_quarter_sprint', 'bench_press']

cPI_Trimmed = cPI[cPI_Col]
dCS_Trimmed = dCS[dCS_Col]

# ensure columns that should contain numbers are not empty or some other value
number_Col = ['height_wo_shoes', 'weight', 'wingspan', 'standing_vertical_leap', 'max_vertical_leap', 'lane_agility_time', 'three_quarter_sprint', 'bench_press']

for i in number_Col:
    dCS_Trimmed[i] = pd.to_numeric(dCS_Trimmed[i], errors='coerce')

# combine the tables
combinedStatsByPosition = dCS_Trimmed.merge(cPI_Trimmed, left_on='player_id', right_on='person_id', how='inner')

# if players do not have a position, drop them
combinedStatsByPosition = combinedStatsByPosition.dropna(subset=['position'])

#grab columns
StatsByPosition = combinedStatsByPosition[['player_id', 'position', 'school', 'height_wo_shoes', 'weight', 'wingspan', 'standing_vertical_leap', 'max_vertical_leap', 'lane_agility_time', 
    'three_quarter_sprint', 'bench_press', 'draft_round', 'draft_number']]


# drop rows with any missing values, can be removed if not needed for machine learning portion
StatsByPosition = StatsByPosition.dropna()

#exporting to csv and printing to console
StatsByPosition.to_csv('StatsByPosition.csv', index=False)
print(StatsByPosition.head(25))
