import pandas as pd
import matplotlib.pyplot as plt
import ast
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ✅ Load files (no path needed if they’re in the same folder)
df_russia = pd.read_csv('Russia_invade.csv')
df_ukraine = pd.read_csv('StandWithUkraine.csv')

# Extract user creation date
def extract_user_creation_date(user_str):
    try:
        user_dict = ast.literal_eval(user_str)
        return pd.to_datetime(user_dict.get('created', pd.NaT), errors='coerce')
    except:
        return pd.NaT

df_russia['user_created_at'] = df_russia['user'].apply(extract_user_creation_date)
df_ukraine['user_created_at'] = df_ukraine['user'].apply(extract_user_creation_date)

# Drop rows with no creation date
df_russia = df_russia.dropna(subset=['user_created_at'])
df_ukraine = df_ukraine.dropna(subset=['user_created_at'])

# Group by month
df_russia['user_created_month'] = df_russia['user_created_at'].dt.to_period('M')
df_ukraine['user_created_month'] = df_ukraine['user_created_at'].dt.to_period('M')

# Count accounts by creation month
russia_counts = df_russia['user_created_month'].value_counts().sort_index()
ukraine_counts = df_ukraine['user_created_month'].value_counts().sort_index()

# Convert to datetime
russia_counts.index = russia_counts.index.to_timestamp()
ukraine_counts.index = ukraine_counts.index.to_timestamp()

# Plot
plt.figure(figsize=(12, 6))
plt.plot(russia_counts.index, russia_counts.values, label='Russia-related Tweets', marker='o')
plt.plot(ukraine_counts.index, ukraine_counts.values, label='Ukraine-related Tweets', marker='o')
plt.axvline(pd.Timestamp('2022-02-24'), color='red', linestyle='--', label='Invasion Begins')
plt.title('Tweet Volume by Account Creation Date')
plt.xlabel('Account Creation Date')
plt.ylabel('Number of Tweets')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()



from datetime import datetime

# Reference point: invasion date
invasion_date = pd.Timestamp('2022-02-24')

def summarize_account_ages(df, label):
    df = df.copy()
    
    # Calculate account age in days as of the invasion
    df['account_age_days'] = (invasion_date - df['user_created_at']).dt.days

    # Basic stats
    avg_age = df['account_age_days'].mean()
    med_age = df['account_age_days'].median()

    # Bucketing by account age
    total = len(df)
    feb_2022 = df[df['user_created_at'].dt.to_period('M') == '2022-02']
    dec_to_feb = df[df['user_created_at'].dt.to_period('M').isin(['2021-12', '2022-01', '2022-02'])]
    in_2020 = df[df['user_created_at'].dt.year == 2020]
    before_2020 = df[df['user_created_at'].dt.year < 2020]

    print(f"\n📊 Stats for {label}")
    print(f"Total tweets analyzed: {total}")
    print(f"Average account age (days): {avg_age:.2f}")
    print(f"Median account age (days): {med_age:.2f}")
    print(f"Accounts created in Feb 2022: {len(feb_2022)} ({100 * len(feb_2022)/total:.2f}%)")
    print(f"Accounts created Dec–Feb (3 mo before invasion): {len(dec_to_feb)} ({100 * len(dec_to_feb)/total:.2f}%)")
    print(f"Accounts created in 2020: {len(in_2020)} ({100 * len(in_2020)/total:.2f}%)")
    print(f"Accounts created before 2020: {len(before_2020)} ({100 * len(before_2020)/total:.2f}%)")

# Run on both datasets
summarize_account_ages(df_russia, 'Russia-related Tweets')
summarize_account_ages(df_ukraine, 'Ukraine-related Tweets')
