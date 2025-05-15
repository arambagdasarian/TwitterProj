import pandas as pd

# Load the CSV file
df = pd.read_csv('Data/tweets_clean.csv', dtype={'id': str, 'url': str}, low_memory=False)

n_rows = df.shape[0]   # option 1
# or
n_rows = len(df)       # option 2
# or
n_rows = len(df.index) # option 3 (same result)

print("The dataframe has", n_rows, "rows.")
