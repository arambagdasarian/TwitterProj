import pandas as pd
import ast

# === Load CSVs ===
df_russia = pd.read_csv('Russia_invade.csv')
df_ukraine = pd.read_csv('StandWithUkraine.csv')

print("✅ CSVs loaded.")
print("Sample user (Russia):", df_russia['user'].iloc[0])

# === Extract account creation datetime from the 'user' JSON string ===
def extract_user_created(user_str):
    try:
        user_dict = ast.literal_eval(user_str)
        return pd.to_datetime(user_dict.get('created'), errors='coerce')
    except Exception as e:
        print("❌ Failed to parse:", user_str[:100], "| Error:", e)
        return pd.NaT

# Apply to both datasets
df_russia['user_created_at'] = df_russia['user'].apply(extract_user_created)
df_ukraine['user_created_at'] = df_ukraine['user'].apply(extract_user_created)

# Check that it worked
print("✅ Parsed user_created_at (Russia):", df_russia['user_created_at'].dropna().head())

# === Clean timezone and drop NaNs ===
df_russia = df_russia.dropna(subset=['user_created_at'])
df_ukraine = df_ukraine.dropna(subset=['user_created_at'])

df_russia['user_created_at'] = df_russia['user_created_at'].dt.tz_localize(None)
df_ukraine['user_created_at'] = df_ukraine['user_created_at'].dt.tz_localize(None)

# === Account Age Analysis ===
from datetime import datetime

invasion_date = pd.Timestamp('2022-02-24')

def summarize_account_ages(df, label):
    df = df.copy()
    df['account_age_days'] = (invasion_date - df['user_created_at']).dt.days

    total = len(df)
    avg_age = df['account_age_days'].mean()
    med_age = df['account_age_days'].median()

    # Buckets
    feb_2022 = df[df['user_created_at'].dt.to_period('M') == pd.Period('2022-02', freq='M')]
    dec_to_feb = df[df['user_created_at'].dt.to_period('M').isin([
        pd.Period('2021-12', freq='M'),
        pd.Period('2022-01', freq='M'),
        pd.Period('2022-02', freq='M'),
    ])]
    in_2020 = df[df['user_created_at'].dt.year == 2020]
    before_2020 = df[df['user_created_at'].dt.year < 2020]
    after_invasion = df[df['user_created_at'] > invasion_date]

    # Print results
    print(f"\n📊 Stats for {label}")
    print(f"Total tweets analyzed: {total}")
    print(f"Average account age (days): {avg_age:.2f}")
    print(f"Median account age (days): {med_age:.2f}")
    print(f"Accounts created in Feb 2022: {len(feb_2022)} ({100 * len(feb_2022)/total:.2f}%)")
    print(f"Accounts created Dec–Feb (3 mo before invasion): {len(dec_to_feb)} ({100 * len(dec_to_feb)/total:.2f}%)")
    print(f"Accounts created in 2020: {len(in_2020)} ({100 * len(in_2020)/total:.2f}%)")
    print(f"Accounts created before 2020: {len(before_2020)} ({100 * len(before_2020)/total:.2f}%)")
    print(f"🚨 Accounts created *after* Feb 24: {len(after_invasion)} ({100 * len(after_invasion)/total:.2f}%)")

# Run
summarize_account_ages(df_russia, 'Russia-related Tweets')
summarize_account_ages(df_ukraine, 'Ukraine-related Tweets')
