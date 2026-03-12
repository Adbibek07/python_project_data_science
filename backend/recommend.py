import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

DIR = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(os.path.join(DIR, "movies.csv"))

# replace string "null" with NaN first
df = df.replace("null", pd.NA)

# then drop rows with missing genre_ids
df.dropna(subset=['genre_ids'], inplace=True)
df.reset_index(drop=True, inplace=True)

# Fill missing genre values
df['genre_names'] = df['genre_names'].fillna('')

# Convert genres into numerical vectors
tfidf = TfidfVectorizer(token_pattern=r'[^,]+')
tfidf_matrix = tfidf.fit_transform(df['genre_names'])

# Calculate similarity between movies
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Reset index
df = df.reset_index()

# ── Save pkl files ─────────────────────────────────────────
with open(os.path.join(DIR, "similarity.pkl"), "wb") as f:
    pickle.dump(cosine_sim, f)

with open(os.path.join(DIR, "movies_list.pkl"), "wb") as f:
    pickle.dump(df, f)

print("✅ Recommendation model trained and saved.")