import pandas as pd

# load csv
commonPlayerInfo = pd.read_csv('archive/csv/common_player_info.csv')
draftCombineStats = pd.read_csv('archive/csv/draft_combine_stats.csv')


player_small = commonPlayerInfo[['person_id','first_name','last_name','school']]


perf_cols = [
    'standing_vertical_leap',
    'max_vertical_leap',
    'lane_agility_time',
    'three_quarter_sprint',
    'bench_press'
]

combine_small = draftCombineStats[['player_id'] + perf_cols]

#cleaning, making sure its numeric
for col in perf_cols:
    combine_small[col] = pd.to_numeric(combine_small[col], errors='coerce')

combine_small['player_performance'] = combine_small[perf_cols].mean(axis=1, skipna=True)


merged = combine_small.merge(
    player_small,
    left_on='player_id',
    right_on='person_id',
    how='inner'
)

#clean players with no school info 
merged = merged.dropna(subset=['school'])


school_perf = (
    merged.groupby('school')['player_performance']
    .agg(['mean','count'])
    .reset_index()
    .rename(columns={'mean':'avg_player_performance',
                     'count':'num_players'})
)

school_perf = school_perf.sort_values(
    by='avg_player_performance',
    ascending=False
)

print(school_perf.head(20))





