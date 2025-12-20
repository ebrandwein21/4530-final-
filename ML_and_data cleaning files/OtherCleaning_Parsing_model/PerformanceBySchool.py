import pandas as pd

# load source files
commonPlayerInfo = pd.read_csv('archive/csv/common_player_info.csv')
draftCombineStats = pd.read_csv('archive/csv/draft_combine_stats.csv')

# pick columns needed
cPI_Col = commonPlayerInfoColumns = ['person_id', 'first_name', 'last_name', 'school']
dCS_Col = draftCombineStatsColumns = [
    'player_id',
    'height_wo_shoes',
    'weight',
    'wingspan',
    'standing_vertical_leap',
    'max_vertical_leap',
    'lane_agility_time',
    'three_quarter_sprint',
    'bench_press'
]

playerTrimmed = commonPlayerInfo[cPI_Col]
combineTrimmed = draftCombineStats[dCS_Col]

# make sure combine metrics are numeric
numberCols = dCS_Col[1:]  # everything except player_id
for col in numberCols:
    combineTrimmed[col] = pd.to_numeric(combineTrimmed[col], errors='coerce')

# merge combine metrics with school info
merged = combineTrimmed.merge(
    playerTrimmed,
    left_on='player_id',
    right_on='person_id',
    how='inner'
)

# drop rows with no school
merged = merged.dropna(subset=['school'])

# group by school and compute average combine metrics + number of players
schoolPerformance = (
    merged
    .groupby('school')[numberCols]
    .mean()
    .reset_index()
)

schoolPerformance['num_players'] = merged.groupby('school')['player_id'].count().values

# save + preview
schoolPerformance.to_csv('PerformanceBySchool.csv', index=False)
print(schoolPerformance.head(20))
