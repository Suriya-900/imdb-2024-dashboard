import streamlit as st

st.set_page_config(page_title="IMDb 2024 Dashboard", layout="wide")
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pymysql
from sqlalchemy import create_engine
import numpy as np


st.markdown(
    """
    <style>
        .stApp {
            background-color: #e6e6fa;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- DATABASE CONNECTION --- #
engine = create_engine("mysql+pymysql://root:root@localhost:3306/imdb_movies_2024")
connection = engine.connect()

# --- LOAD DATA --- #
df = pd.read_sql("SELECT * FROM movies_2024", con=connection)

# --- DATA CLEANING --- #
df['Ratings'] = pd.to_numeric(df['Ratings'], errors='coerce')
df['Voting Counts'] = pd.to_numeric(df['Voting Counts'], errors='coerce')
df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')

# --- MAIN PAGE LAYOUT --- #
st.title("🎬 IMDb 2024 Movies Data Project")

# --- HOME PAGE NAVIGATION --- #
page = st.radio("Navigate to:", ["Home", "Dashboard"], horizontal=True)

# --- HOME PAGE CONTENT --- #
if page == "Home":
    st.header("📌 Project Overview")
    st.subheader("🎯 Project Title:")
    st.markdown("**IMDb 2024 Data Scraping and Visualizations**")

    st.subheader("💼 Domain:")
    st.markdown("**Entertainment / Data Analytics**")

    st.subheader("🧠 Skills Takeaway:")
    st.markdown("""
    - Web Scraping using **Selenium**
    - Data Analysis using **Pandas** and **SQL**
    - Dashboard creation with **Streamlit**
    - Interactive visual filtering
    - Data Visualization using **Matplotlib** and **Seaborn**
    - Real-world project structure: ETL → Analysis → UI
    """)

    st.subheader("📊 Project Description:")
    st.markdown("""
    This project focuses on scraping IMDb's 2024 movie dataset and building an end-to-end interactive dashboard for analysis.
    It enables users to:
    - Explore movie trends based on genres, duration, and ratings
    - Analyze popularity via voting patterns
    - Compare top-rated movies per genre
    - Visualize trends using charts and heatmaps

    The dashboard is built to assist analysts, movie enthusiasts, and production studios in understanding patterns in newly released content.
    """)

    st.subheader("👨‍💻 Developed by:")
    st.markdown("**Suriya Jagan**")

   

# --- DASHBOARD PAGE --- #
elif page == "Dashboard":
    st.title("📊 IMDb 2024 Movies Dashboard")

    # --- SIDEBAR FILTERS --- #
    st.sidebar.header("🔍 Filter Options")
    genre_filter = st.sidebar.multiselect("Select Genre", df['Genre'].dropna().unique())
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0)

    min_votes = int(np.nan_to_num(df['Voting Counts'].min(), nan=0))
    max_votes = int(np.nan_to_num(df['Voting Counts'].max(), nan=100000))
    vote_range = st.sidebar.slider("Select Voting Count Range", min_value=min_votes, max_value=max_votes, value=(min_votes, max_votes))

    duration_filter = st.sidebar.selectbox("Duration Filter (in minutes)", ["All", "< 120 mins", "120–180 mins", "> 180 mins"])

    # --- APPLY FILTERS --- #
    filtered_df = df.copy()
    if genre_filter:
        filtered_df = filtered_df[filtered_df['Genre'].isin(genre_filter)]
    filtered_df = filtered_df[filtered_df['Ratings'] >= min_rating]
    filtered_df = filtered_df[
        (filtered_df['Voting Counts'] >= vote_range[0]) &
        (filtered_df['Voting Counts'] <= vote_range[1])
    ]
    if duration_filter == "< 120 mins":
        filtered_df = filtered_df[filtered_df['Duration'] < 120]
    elif duration_filter == "120–180 mins":
        filtered_df = filtered_df[(filtered_df['Duration'] >= 120) & (filtered_df['Duration'] <= 180)]
    elif duration_filter == "> 180 mins":
        filtered_df = filtered_df[filtered_df['Duration'] > 180]

    # --- DISPLAY FILTERED DATA --- #
    st.subheader("🎬 Filtered Movies")
    st.dataframe(filtered_df)

    # --- VISUALIZATIONS --- #
    st.subheader("📊 Top 10 Movies by Rating and Voting Counts")
    top_movies = df.sort_values(['Ratings', 'Voting Counts'], ascending=False).head(10)
    st.bar_chart(top_movies.set_index('Movie Name')[['Ratings', 'Voting Counts']])

    st.subheader("📚 Genre Distribution")
    genre_count = df['Genre'].value_counts()
    st.bar_chart(genre_count)

    st.subheader("⏱️ Average Duration by Genre")
    avg_duration = df.groupby('Genre')['Duration'].mean().sort_values()
    st.bar_chart(avg_duration)

    st.subheader("🗳️ Voting Trends by Genre")
    avg_votes = df.groupby('Genre')['Voting Counts'].mean()
    st.bar_chart(avg_votes)

    st.subheader("⭐ Rating Distribution")
    st.write("Histogram of Ratings")
    st.bar_chart(df['Ratings'])

    st.write("Boxplot of Ratings")
    fig1, ax1 = plt.subplots()
    sns.boxplot(data=df, x='Ratings', ax=ax1)
    st.pyplot(fig1)

    st.subheader("🎯 Top-Rated Movie Per Genre")
    top_per_genre = df.loc[df.groupby('Genre')['Ratings'].idxmax()]
    st.dataframe(top_per_genre[['Movie Name', 'Genre', 'Ratings']])

    st.subheader("🥧 Most Popular Genres by Voting")
    votes_by_genre = df.groupby('Genre')['Voting Counts'].sum().dropna()
    votes_by_genre = votes_by_genre[votes_by_genre > 0]
    fig2 = votes_by_genre.plot.pie(autopct='%1.1f%%', figsize=(6, 6)).figure
    st.pyplot(fig2)

    st.subheader("📏 Duration Extremes")
    st.write("Shortest Movie:")
    st.dataframe(df.nsmallest(1, 'Duration'))
    st.write("Longest Movie:")
    st.dataframe(df.nlargest(1, 'Duration'))

    st.subheader("🔥 Ratings by Genre (Heatmap)")
    heatmap_data = df.pivot_table(index='Genre', values='Ratings', aggfunc='mean')
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", cbar=True, ax=ax3)
    st.pyplot(fig3)

