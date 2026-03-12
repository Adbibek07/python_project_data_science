from copyreg import pickle
import os

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import ast
import pickle

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
    page_title="CineScope",
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
    padding-top: 1rem !important;
  }
  h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
      background: #10101a;
      border-right: 1px solid #2a2a3a;
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

@st.cache_data
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

# ── Sidebar nav ───────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎬 Movie Analysis")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🎥 Browse Movies", "🤖 Recommendations"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: **{len(df)} movies**")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("# 📊 DASHBOARD")
    st.markdown("An overview of your movie dataset.")

    # ── KPI row ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Movies", len(df))
    c2.metric("Avg Rating", f"{df['vote_average'].mean():.2f} ⭐")
    c3.metric("Avg Popularity", f"{df['popularity'].mean():.0f}")
    c4.metric("Languages", df["original_language"].nunique())

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Genre distribution ────────────────────────────────────────────────────
    all_genres = [g for sublist in df["genre_list"] for g in sublist]
    genre_counts = Counter(all_genres)
    gdf = pd.DataFrame(genre_counts.items(), columns=["Genre", "Count"]).sort_values("Count", ascending=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Genre Distribution</p>', unsafe_allow_html=True)
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
        st.plotly_chart(fig, use_container_width=True)

    # ── Popularity vs Rating scatter ──────────────────────────────────────────
    with col2:
        st.markdown('<p class="section-title">Popularity vs Rating</p>', unsafe_allow_html=True)
        fig2 = px.scatter(
            df, x="popularity", y="vote_average",
            size="vote_count", color="vote_average",
            hover_name="title",
            color_continuous_scale=["#2a2a3a", "#c9a84c", "#ff6b35"],
            template="plotly_dark",
            size_max=40,
        )
        fig2.update_layout(
            paper_bgcolor="#0a0a0f", plot_bgcolor="#0a0a0f",
            coloraxis_showscale=False, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Popularity", yaxis_title="Rating",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top movies by vote count ──────────────────────────────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<p class="section-title">Top Movies by Vote Count</p>', unsafe_allow_html=True)
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
        st.plotly_chart(fig3, use_container_width=True)

    # ── Release timeline ──────────────────────────────────────────────────────
    with col4:
        st.markdown('<p class="section-title">Release Timeline</p>', unsafe_allow_html=True)
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
        st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — BROWSE MOVIES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎥 Browse Movies":
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

    st.caption(f"Showing **{len(filtered)}** movies")
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
# PAGE 3 — RECOMMENDATIONS (placeholder)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Recommendations":
    st.markdown("# 🤖 RECOMMENDATIONS")
    st.markdown("Find movies similar to your favorites.")

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
