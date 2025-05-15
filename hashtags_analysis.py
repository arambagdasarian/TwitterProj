import pandas as pd
import matplotlib.pyplot as plt
import os

# List of CSV files you want to merge and analyze
file_paths = [
    'Data/Russia_invade.csv',
    'Data/Russian_border_Ukraine.csv',
    'Data/Russian_troops.csv',
    'Data/StandWithUkraine.csv',
    'Data/Ukraine_border.csv',
    'Data/Ukraine_nato.csv',
    'Data/Ukraine_troops.csv',
    'Data/Ukraine_war.csv'
]

# Load and combine all datasets
df_list = []
for path in file_paths:
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['hashtag_source'] = path.replace('.csv', '')  # Tag by source
        df_list.append(df)
    else:
        print(f"File not found: {path}")

combined_df = pd.concat(df_list, ignore_index=True)

# Ensure 'date' is datetime format
combined_df['date'] = pd.to_datetime(combined_df['date'])

# Count tweets per day
volume_df = combined_df.groupby(combined_df['date'].dt.date).size().reset_index(name='tweet_count')

# Plotting
plt.figure(figsize=(15, 6))
plt.plot(volume_df['date'], volume_df['tweet_count'], marker='o', linestyle='-', color='blue')
plt.title('Tweet Volume Around Russian Invasion of Ukraine', fontsize=14)
plt.xlabel('Date')
plt.ylabel('Tweet Count')
plt.xticks(rotation=45)

# Highlighting key dates
highlight_dates = {
    '2022-02-24': 'Invasion Day',
    '2022-02-28': 'EU Application',
    '2022-03-02': 'UN Condemnation',
    '2022-03-05': 'Protests/Sanctions'
}

for date_str, label in highlight_dates.items():
    date = pd.to_datetime(date_str)
    plt.axvline(date, color='red', linestyle='--', alpha=0.7)
    plt.text(date, plt.ylim()[1]*0.95, label, rotation=90, verticalalignment='top', color='red', fontsize=9)

plt.tight_layout()
plt.grid(True)
plt.show()
