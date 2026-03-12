import pandas as pd
import os

DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(DIR, "movies.csv")

# load
df = pd.read_csv(csv_path)

# cleaning
df = df.replace("null", pd.NA)   
df.dropna(subset=["genre_ids"], inplace=True)
df.reset_index(drop=True, inplace=True)
df.drop_duplicates(subset=["id"], inplace=True)
df.dropna(subset=["title", "overview"], inplace=True)
df = df[df["title"].str.strip() != ""]
df = df[df["overview"].str.strip() != ""]
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df["release_date"] = df["release_date"].dt.date
df = df[df["vote_average"].between(0, 10)]
df.reset_index(drop=True, inplace=True)

# overwrite same CSV
df.to_csv(csv_path, index=False)
print(f"✅ Cleaning done — {len(df)} movies saved.")