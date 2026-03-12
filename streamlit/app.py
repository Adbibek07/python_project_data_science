from copyreg import pickle
import os

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import ast
import pickle

import subprocess
if not os.path.exists(os.path.join(os.path.dirname(__file__), "../backend/movies.csv")):
    subprocess.run(["python", os.path.join(os.path.dirname(__file__), "../backend/fetch.py")])
    subprocess.run(["python", os.path.join(os.path.dirname(__file__), "../backend/clean.py")])
    subprocess.run(["python", os.path.join(os.path.dirname(__file__), "../backend/recommend.py")])


# ── Recommendation functions ──────────────────────────────
@st.cache_resource
def load_recommendation_model():
    pkl_path = os.path.join(os.path.dirname(__file__), "../backend")
    with open(os.path.join(pkl_path, "similarity.pkl"), "rb") as f:
        cosine_sim = pickle.load(f)
    with open(os.path.join(pkl_path, "movies_list.pkl"), "rb") as f:
        movies_df = pickle.load(f)
    return cosine_sim, movies_df

def get_recommendations(movie_title, cosine_sim, movies_df, num_recommendations=6):
    idx = movies_df[movies_df["title"] == movie_title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    movie_indices = [i[0] for i in sim_scores]
    result = movies_df.iloc[movie_indices].copy()

    # add genre_list column if missing
    if "genre_list" not in result.columns:
        result["genre_list"] = result["genre_names"].apply(
            lambda x: [g.strip() for g in str(x).split(",")]
        )
    return result
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Movie Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
      background-color: #0a0a0f;
      color: #e8e0d0;
      font-family: 'Inter', sans-serif;
  }
    div[class*="block-container"] {
    padding-top: 2rem !important;
  }
  h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; }

/* Sidebar */
  section[data-testid="stSidebar"] {
      background: #10101a;
      border-right: 1px solid #2a2a3a;
      padding-top: 0.5rem !important;
  }

  div[data-testid="stSidebar"] div[data-testid="stButton"] button {
      background: transparent !important;
      border: none !important;
      border-left: 2px solid transparent !important;
      border-radius: 0 !important;
      color: #666 !important;
      font-size: 0.95rem !important;
      letter-spacing: 1px !important;
      padding: 10px 14px !important;
      text-align: left !important;
      width: 100% !important;
  }
  div[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
      border-left-color: #c9a84c !important;
      color: #e8e0d0 !important;
      background: transparent !important;
  }
  /* Target all text inside sidebar radio */
  div[data-testid="stSidebar"] label p {
      font-size: 1.1rem !important;
      font-family: 'Bebas Neue', sans-serif !important;
      letter-spacing: 2px !important;
  }

  div[data-testid="stSidebar"] label {
      padding: 8px 12px !important;
      border-radius: 8px !important;
      margin-bottom: 6px !important;
      border: 1px solid transparent !important;
      transition: all 0.2s !important;
  }

  div[data-testid="stSidebar"] label:hover {
      background: #1a1a2a !important;
      border-color: #2a2a3a !important;
  }

  div[data-testid="stSidebar"] label:hover p {
      color: #c9a84c !important;
  }

  /* Metric cards */
  div[data-testid="metric-container"] {
      background: #14141f;
      border: 1px solid #2a2a3a;
      border-radius: 10px;
      padding: 16px;
  }
  div[data-testid="metric-container"] label { color: #c9a84c !important; }
  div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
      color: #f5f0e8 !important; font-size: 2rem !important;
  }

  /* Movie cards */
 .movie-card {
      background: #14141f;
      border: 1px solid #2a2a3a;
      border-radius: 12px;
      overflow: hidden;
      transition: transform .2s, box-shadow .2s;
      height: 620px;
      display: flex;
      flex-direction: column;
  }
  .movie-card-body {
      padding: 14px;
      flex: 1;
      overflow-y: auto;
  }
  .movie-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(201,168,76,.25);
  }
  .movie-card img {
      width: 100%;
      height: 320px;
      object-fit: cover;
      display: block;
  }
  .movie-card-body { padding: 14px; }
  .movie-card-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1.2rem;
      letter-spacing: 1px;
      color: #f5f0e8;
      margin: 0 0 6px;
  }
  .movie-card-genre {
      font-size: .72rem;
      color: #c9a84c;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
  }
  .movie-card-overview {
      font-size: .8rem;
      color: #999;
      line-height: 1.5;
  }
  .badge {
      display: inline-block;
      background: #1e1e2e;
      border: 1px solid #2a2a3a;
      border-radius: 20px;
      padding: 2px 10px;
      font-size: .72rem;
      color: #c9a84c;
      margin-right: 4px;
      margin-top: 6px;
  }
  .star { color: #c9a84c; }

  /* Section headers */
  .section-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 1.6rem;
      letter-spacing: 3px;
      color: #c9a84c;
      border-bottom: 1px solid #2a2a3a;
      padding-bottom: 6px;
      margin-bottom: 16px;
  }

  /* Recommendation placeholder */
  .rec-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 400px;
      border: 2px dashed #2a2a3a;
      border-radius: 16px;
      color: #444;
      font-size: 1.1rem;
      letter-spacing: 1px;
  }
  .rec-placeholder span { font-size: 3rem; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

import os

@st.cache_data(ttl=3600)  # refreshes every 1 hour
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "../backend/movies.csv")
    df = pd.read_csv(csv_path)
    df["genre_list"] = df["genre_names"].apply(
        lambda x: [g.strip() for g in str(x).split(",")]
    )
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year
    return df

df = load_data()

# Sidebar
st.sidebar.markdown(
"<p style='font-family:Bebas Neue,sans-serif; font-size:2rem; letter-spacing:4px; color:#c9a84c; padding: 8px 14px 0 14px; line-height:1.1;'>🎬 Movie<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Analysis</p>",    unsafe_allow_html=True
)
st.sidebar.markdown("<hr style='border-color:#2a2a3a;'>", unsafe_allow_html=True)

params = st.query_params
if "page" not in st.session_state:
    st.session_state.page = params.get("page", "Dashboard")

for p in ["Dashboard", "Browse Movies", "Recommendations"]:
    if st.sidebar.button(p, key=f"nav_{p}", use_container_width=True):
        st.session_state.page = p
        st.query_params["page"] = p
        st.rerun()

page = st.session_state.page

st.sidebar.markdown("<hr style='border-color:#2a2a3a;'>", unsafe_allow_html=True)
st.sidebar.caption(f"{len(df)} movies loaded")
st.sidebar.markdown("""
<div style='padding: 8px 4px; font-size: 1 rem; color: #666; line-height: 1.7;'>
    Data scraped from the <strong style='color:#777'>TMDB API</strong>.<br>
    <span style='color:#666'>Updated on every run via the scraper pipeline.</span>
</div>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════════════

# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("# 📊 DASHBOARD")
    st.markdown("An overview of the movie dataset.")

    # ── KPI row ──────────────────────────────────────────────────────────────
    all_genres = [g for sublist in df["genre_list"] for g in sublist]
    top_genre = Counter(all_genres).most_common(1)[0][0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Movies", len(df))
    c2.metric("Avg Rating", f"{df['vote_average'].mean():.2f} ⭐")
    c3.metric("Avg Popularity", f"{df['popularity'].mean():.0f}")
    c4.metric("Top Genre", top_genre)
    c5.metric("Languages", df["original_language"].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dynamic insight summaries ─────────────────────────────────────────────
    highest_rated = df.nlargest(2, "vote_average")[["title", "vote_average"]]
    most_popular = df.nlargest(2, "popularity")[["title", "popularity"]]
    most_voted = df.nlargest(2, "vote_count")[["title", "vote_count"]]

    # hidden gem: high rating but low popularity
    gem = df[df["vote_average"] >= 7].nsmallest(1, "popularity").iloc[0]

    # most active month
    df["month_year"] = df["release_date"].dt.to_period("M").astype(str)
    active_month = df["month_year"].value_counts().idxmax()

    # dominant language
    top_lang = df["original_language"].value_counts()
    top_lang_pct = (top_lang.iloc[0] / len(df) * 100)
    second_lang = top_lang.index[1] if len(top_lang) > 1 else ""
    third_lang = top_lang.index[2] if len(top_lang) > 2 else ""

    st.markdown("""
    <style>
    .insight-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    .insight-card {
        background: #14141f;
        border: 1px solid #2a2a3a;
        border-radius: 10px;
        padding: 16px;
        border-top: 2px solid #c9a84c;
    }
    .insight-icon { font-size: 1.3rem; margin-bottom: 6px; }
    .insight-title { font-size: .72rem; font-weight: 600; color: #c9a84c; margin-bottom: 6px; letter-spacing: 1px; text-transform: uppercase; }
    .insight-text { font-size: .78rem; color: #888; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-grid">
        <div class="insight-card">
            <div class="insight-icon">🏆</div>
            <div class="insight-title">Highest Rated</div>
            <div class="insight-text"><strong style="color:#e8e0d0">{highest_rated.iloc[0]['title']}</strong> leads with a <strong style="color:#c9a84c">{highest_rated.iloc[0]['vote_average']:.1f}</strong> rating, followed by <strong style="color:#e8e0d0">{highest_rated.iloc[1]['title']}</strong> at {highest_rated.iloc[1]['vote_average']:.1f}</div>
        </div>
        <div class="insight-card">
            <div class="insight-icon">🔥</div>
            <div class="insight-title">Most Popular</div>
            <div class="insight-text"><strong style="color:#e8e0d0">{most_popular.iloc[0]['title']}</strong> dominates popularity at <strong style="color:#c9a84c">{most_popular.iloc[0]['popularity']:.0f}</strong>, nearly {most_popular.iloc[0]['popularity']/most_popular.iloc[1]['popularity']:.1f}x the second most popular movie</div>
        </div>
        <div class="insight-card">
            <div class="insight-icon">👥</div>
            <div class="insight-title">Most Voted</div>
            <div class="insight-text"><strong style="color:#e8e0d0">{most_voted.iloc[0]['title']}</strong> leads vote count with <strong style="color:#c9a84c">{most_voted.iloc[0]['vote_count']:,}</strong> votes, followed by {most_voted.iloc[1]['title']} at {most_voted.iloc[1]['vote_count']:,}</div>
        </div>
        <div class="insight-card">
            <div class="insight-icon">💎</div>
            <div class="insight-title">Hidden Gem</div>
            <div class="insight-text"><strong style="color:#e8e0d0">{gem['title']}</strong>: <strong style="color:#c9a84c">{gem['vote_average']:.1f}</strong> rating but relatively low popularity of {gem['popularity']:.0f} — criminally underexposed</div>
        </div>
        <div class="insight-card">
            <div class="insight-icon">📅</div>
            <div class="insight-title">Most Active Period</div>
            <div class="insight-text"><strong style="color:#c9a84c">{active_month}</strong> has the most releases in the dataset with <strong style="color:#e8e0d0">{df['month_year'].value_counts().iloc[0]}</strong> movies dropping that month</div>
        </div>
        <div class="insight-card">
            <div class="insight-icon">🌍</div>
            <div class="insight-title">Dominant Language</div>
            <div class="insight-text"><strong style="color:#c9a84c">{top_lang.index[0].upper()}</strong> movies make up <strong style="color:#e8e0d0">{top_lang_pct:.0f}%</strong> of the dataset, with <strong style="color:#e8e0d0">{second_lang.upper()}</strong> and <strong style="color:#e8e0d0">{third_lang.upper()}</strong> as runner-ups</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Genre distribution + Rating distribution ───────────────────────
    all_genres = [g for sublist in df["genre_list"] for g in sublist]
    genre_counts = Counter(all_genres)
    gdf = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"]).sort_values("Count", ascending=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Genre Distribution</p>', unsafe_allow_html=True)
        st.caption("How many movies belong to each genre")
        fig = px.bar(
            gdf, x="Count", y="Genre", orientation="h",
            color="Count", color_continuous_scale=["#1e1e2e", "#c9a84c"],
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None, xaxis_title=None,
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-title">Rating Distribution</p>', unsafe_allow_html=True)
        st.caption("How ratings are spread across the dataset")
        rating_bins = pd.cut(df["vote_average"], bins=[0,4,5,6,7,8,9,10], labels=["0-4","4-5","5-6","6-7","7-8","8-9","9-10"])
        rating_dist = rating_bins.value_counts().sort_index().reset_index()
        rating_dist.columns = ["Range", "Count"]
        fig_rd = px.bar(
            rating_dist, x="Range", y="Count",
            color="Count", color_continuous_scale=["#1e1e2e", "#c9a84c"],
            template="plotly_dark",
        )
        fig_rd.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title=None, yaxis_title="Movies",
        )
        st.plotly_chart(fig_rd, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    # ── Row 2: Popularity vs votes + Language breakdown ───────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">Popularity vs Vote Count</p>', unsafe_allow_html=True)
        st.caption("Do popular movies get more votes?")
        fig_pv = px.scatter(
            df, x="popularity", y="vote_count",
            hover_name="title", color="vote_average",
            color_continuous_scale=["#2a2a3a", "#c9a84c", "#ff6b35"],
            template="plotly_dark", size_max=20,
        )
        fig_pv.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Popularity", yaxis_title="Vote Count",
        )
        st.plotly_chart(fig_pv, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    with col4:
        st.markdown('<p class="section-title">Language Breakdown</p>', unsafe_allow_html=True)
        st.caption("Movie count by original language")
        lang_df = df["original_language"].value_counts().reset_index()
        lang_df.columns = ["Language", "Count"]
        fig_lang = px.pie(
            lang_df.head(8), values="Count", names="Language",
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            template="plotly_dark", hole=0.4,
        )
        fig_lang.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color="#888", size=11))
        )
        st.plotly_chart(fig_lang, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    # ── Row 3: Top movies by vote count + Release timeline ────────────────────
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<p class="section-title">Top Movies by Vote Count</p>', unsafe_allow_html=True)
        st.caption("Most voted movies in the dataset")
        top_voted = df.nlargest(8, "vote_count")[["title", "vote_count", "vote_average"]]
        fig3 = px.bar(
            top_voted.sort_values("vote_count"), x="vote_count", y="title", orientation="h",
            color="vote_average", color_continuous_scale=["#1e1e2e", "#c9a84c"],
            template="plotly_dark", text="vote_count",
        )
        fig3.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None, xaxis_title="Votes",
        )
        st.plotly_chart(fig3, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    with col6:
        st.markdown('<p class="section-title">Release Timeline</p>', unsafe_allow_html=True)
        st.caption("Are newer movies rated higher or lower?")
        timeline_df = df.dropna(subset=["release_date"]).sort_values("release_date")
        fig4 = px.scatter(
            timeline_df, x="release_date", y="vote_average",
            hover_name="title", color="popularity",
            color_continuous_scale=["#2a2a3a", "#c9a84c"],
            template="plotly_dark",
        )
        fig4.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Release Date", yaxis_title="Rating",
        )
        st.plotly_chart(fig4, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    # ── Row 4: Avg rating by genre + Hidden gems scatter ─────────────────────
    col7, col8 = st.columns(2)
    with col7:
        st.markdown('<p class="section-title">Average Rating by Genre</p>', unsafe_allow_html=True)
        st.caption("Which genres are rated highest on average")
        genre_rating = []
        for genre in set(all_genres):
            genre_movies = df[df["genre_list"].apply(lambda x: genre in x)]
            genre_rating.append({"Genre": genre, "Avg Rating": genre_movies["vote_average"].mean()})
        grating_df = pd.DataFrame(genre_rating).sort_values("Avg Rating", ascending=True)
        fig5 = px.bar(
            grating_df, x="Avg Rating", y="Genre", orientation="h",
            color="Avg Rating", color_continuous_scale=["#1e1e2e", "#c9a84c"],
            template="plotly_dark",
        )
        fig5.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_range=[0, 10], yaxis_title=None,
        )
        st.plotly_chart(fig5, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)


    with col8:
        st.markdown('<p class="section-title">Hidden Gems vs Overhyped</p>', unsafe_allow_html=True)
        st.caption("High rating + low popularity = hidden gem | Low rating + high popularity = overhyped")

        def classify(row):
            if row["vote_average"] >= 7 and row["popularity"] < 50:
                return "💎 Hidden Gem"
            elif row["vote_average"] < 6 and row["popularity"] >= 50:
                return "🔥 Overhyped"
            elif row["vote_average"] >= 7 and row["popularity"] >= 50:
                return "🏆 Blockbuster"
            else:
                return "😴 Sleeper"

        df["category"] = df.apply(classify, axis=1)
        fig6 = px.scatter(
            df, x="popularity", y="vote_average",
            color="category", hover_name="title",
            color_discrete_map={
                "💎 Hidden Gem": "#6bff6b",
                "🔥 Overhyped": "#ff6b6b",
                "🏆 Blockbuster": "#c9a84c",
                "😴 Sleeper": "#6b9fff",
            },
            template="plotly_dark",
        )
        fig6.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Popularity", yaxis_title="Rating",
            legend=dict(font=dict(color="#888", size=10))
        )
        st.plotly_chart(fig6, width='stretch')
        st.markdown("<br><br>", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — BROWSE MOVIES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Browse Movies":
    st.markdown("# 🎥 BROWSE MOVIES")

    # ── Filters ───────────────────────────────────────────────────────────────
    all_genres_list = sorted(set(g for sublist in df["genre_list"] for g in sublist))
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        search = st.text_input("🔍 Search by title", placeholder="e.g. Shelter...")
    with fc2:
        sel_genres = st.multiselect("Filter by genre", all_genres_list)
    with fc3:
        sort_by = st.selectbox("Sort by", ["Popularity ↓", "Rating ↓", "Votes ↓", "Release Date ↓"])

    # Apply filters
    filtered = df.copy()
    if search:
        filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]
    if sel_genres:
        filtered = filtered[filtered["genre_list"].apply(lambda g: any(x in g for x in sel_genres))]

    sort_map = {
        "Popularity ↓": ("popularity", False),
        "Rating ↓": ("vote_average", False),
        "Votes ↓": ("vote_count", False),
        "Release Date ↓": ("release_date", False),
    }
    col_s, asc_s = sort_map[sort_by]
    filtered = filtered.sort_values(col_s, ascending=asc_s)


        # ── Pagination ────────────────────────────────────────────────────────────────
    MOVIES_PER_PAGE = 12 # 3 columns × 2 rows

    total_pages = max(1, -(-len(filtered) // MOVIES_PER_PAGE))  # ceiling division

    if "page_num" not in st.session_state:
        st.session_state.page_num = 1

    # Reset to page 1 when filters change
    st.session_state.page_num = max(1, min(st.session_state.page_num, total_pages))

    start = (st.session_state.page_num - 1) * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    paginated = filtered.iloc[start:end]

    st.caption("Showing 12 per page movies")
    st.markdown("---")

    # ── Movie grid ────────────────────────────────────────────────────────────
    cols = st.columns(3)
    for i, (_, row) in enumerate(paginated.iterrows()):
        with cols[i % 3]:
            poster_url = f"{TMDB_IMG}{row['poster_path']}" if pd.notna(row.get("poster_path")) else "https://via.placeholder.com/300x450/14141f/c9a84c?text=No+Poster"
            genres_html = "".join(f'<span class="badge">{g}</span>' for g in row["genre_list"][:3])
            stars = "★" * int(round(row["vote_average"] / 2)) + "☆" * (5 - int(round(row["vote_average"] / 2)))
            st.markdown(f"""
            <div class="movie-card">
              <img src="{poster_url}" alt="{row['title']}" onerror="this.src='https://via.placeholder.com/300x450/14141f/c9a84c?text=No+Poster'"/>
              <div class="movie-card-body">
                <p class="movie-card-title">{row['title']}</p>
                <div class="movie-card-genre">{row['release_date'].strftime('%Y-%m-%d') if pd.notna(row['release_date']) else ''}</div>
                <span class="star">{stars}</span> <small style="color:#888">{row['vote_average']:.1f} ({row['vote_count']:,} votes)</small>
                {genres_html}
                <p class="movie-card-overview">{row.get('overview','')}</p>
              </div>
            </div>
            <br/>
            """, unsafe_allow_html=True)
            # ── Pagination controls ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3, p4, p5 = st.columns([2, 1, 1, 1, 2])

    with p2:
        if st.button("◀ Prev", disabled=st.session_state.page_num <= 1):
            st.session_state.page_num -= 1
            st.rerun()

    with p3:
        st.markdown(
            f"<div style='text-align:center; padding:8px; color:#c9a84c; font-family:Bebas Neue,sans-serif; font-size:1.1rem; letter-spacing:2px;'>"
            f"{st.session_state.page_num} / {total_pages}</div>",
            unsafe_allow_html=True
        )

    with p4:
        if st.button("Next ▶", disabled=st.session_state.page_num >= total_pages):
            st.session_state.page_num += 1
            st.rerun()

    st.caption(f"Showing {start+1}–{min(end, len(filtered))} of {len(filtered)} movies")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — RECOMMENDATIONS 
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Recommendations":
    st.markdown("# 🤖 RECOMMENDATIONS")
    st.markdown(" ## Find movies similar to your favorites.")

    pkl_path = os.path.join(os.path.dirname(__file__), "../backend/similarity.pkl")

    if not os.path.exists(pkl_path):
        st.info("⏳ Recommendation model is still loading, please wait...")
        if st.button("🔄 Check again"):
            st.rerun()
    else:
        # ── called here ──────────────────────────────────
        cosine_sim, movies_df = load_recommendation_model()
        # ─────────────────────────────────────────────────

        selected_movie = st.selectbox(
            "🎬 Type or select a movie",
            options=movies_df["title"].tolist(),
            index=None,
            placeholder="Search a movie..."
        )

        if selected_movie:
            st.markdown(f"**Movies similar to:** `{selected_movie}`")
            st.markdown("---")

            # ── called here ──────────────────────────────
            recommendations = get_recommendations(selected_movie, cosine_sim, movies_df)
            # ─────────────────────────────────────────────

            cols = st.columns(3)
            for i, (_, row) in enumerate(recommendations.iterrows()):
                with cols[i % 3]:
                    poster_url = f"{TMDB_IMG}{row['poster_path']}" if pd.notna(row.get("poster_path")) else f"https://via.placeholder.com/300x450/14141f/c9a84c?text={row['title'].replace(' ', '+')}"
                    genres_html = "".join(f'<span class="badge">{g}</span>' for g in row["genre_list"][:3])
                    stars = "★" * int(round(row["vote_average"] / 2)) + "☆" * (5 - int(round(row["vote_average"] / 2)))
                    st.markdown(f"""
                    <div class="movie-card">
                      <img src="{poster_url}" alt="{row['title']}"/>
                      <div class="movie-card-body">
                        <p class="movie-card-title">{row['title']}</p>
                        <div class="movie-card-genre">{row['release_date']}</div>
                        <span class="star">{stars}</span>
                        <small style="color:#888">{row['vote_average']:.1f} ({row['vote_count']:,} votes)</small>
                        {genres_html}
                        <p class="movie-card-overview">{row.get('overview','')}</p>
                      </div>
                    </div>
                    <br/>
                    """, unsafe_allow_html=True)
