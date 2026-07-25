import pandas as pd

df = pd.read_csv(
    "data/raw/bulletin_data_statistics.csv"
)

print(df.shape)
print(df.columns.tolist())
print(df.head())
print(df.columns.tolist())