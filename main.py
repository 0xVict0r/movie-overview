import streamlit as st
import httpx
from langcodes import Language
import functions
import numpy as np
import plotly.graph_objects as go

api_key = st.secrets["tmdb_api"]

st.set_page_config(layout="wide")

st.title("Movie Overview & Rating Aggregator")

st.write("A tool that aggregates movie data from multiple sources (TMDB, IMDB, Rotten Tomatoes, Allocine) to give a nice overview. It also gives an aggregated movie rating from the before mentionned sources. Simply enter the name of the movie (no TV) and the program will find the relevant information for you.")

st.markdown(
    "<style>.css-15zrgzn {display: none}</style>", unsafe_allow_html=True)
st.markdown(
    """<style> div.stButton > button:first-child { width: 100% ; } </style>""", unsafe_allow_html=True)

with st.sidebar:
    with st.form("Main Form"):

        search = st.text_input("Enter the title of the Movie: ")

        submit_bttn = st.form_submit_button("Search")

if submit_bttn:
    query = search.replace(" ", "%20")

    movie_id = httpx.get(
        f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page=1&include_adult=false").json()["results"][0]["id"]

    movie_data = httpx.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}").json()

    cast_data = httpx.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}").json()["cast"]

    poster_link = movie_data["poster_path"]
    title = movie_data["original_title"]
    release_date = movie_data["release_date"]
    synopsis = movie_data["overview"]
    movie_language = Language.make(
        language=movie_data["original_language"]).display_name()
    movie_countries = ', '.join(
        map(str, [country["name"] for country in movie_data["production_countries"]]))
    movie_genres = ', '.join(
        map(str, [genre["name"] for genre in movie_data["genres"]]))
    movie_cast = ', '.join(
        map(str, [cast["name"] for cast in cast_data][:6]))
    imdb_id = movie_data["imdb_id"]
    tmdb_rating = movie_data["vote_average"]

    col1, col2 = st.columns([1, 4])
    col1.image(
        f"https://image.tmdb.org/t/p/original{poster_link}", use_column_width=True)
    col2.markdown(f"""
    # {title}
    ##### *Release Date: {release_date}*
    ###### *Original Language: {movie_language}*
    ###### *Country(ies): {movie_countries}*
    ###### *Genre(s): {movie_genres}*
    *{synopsis}*
    """)

    imdb_rating = functions.safe_execute(
        None, (AttributeError, TypeError), functions.get_imdb_rating, imdb_id)
    rt_rating = functions.safe_execute(
        None, (AttributeError, TypeError, IndexError, ValueError), functions.get_rt_ratings, title, release_date[:4])
    allocine_rating = functions.safe_execute(
        None, (AttributeError, TypeError, IndexError, ValueError), functions.get_rt_ratings, title, release_date[:4])

    ratings_list = [imdb_rating, tmdb_rating, rt_rating, allocine_rating]

    rating = np.round(np.mean(
        np.array([rating for rating in ratings_list if type(rating) != type(None)]))*10, 1)

    functions.plot_cast(movie_id)

    if rating <= 20:
        color = "darkred"
    elif 20 < rating <= 40:
        color = "red"
    elif 40 < rating <= 60:
        color = "orange"
    elif 60 < rating <= 80:
        color = "green"
    else:
        color = "darkgreen"

    empty1, figspace, empty2 = st.columns([1.5, 5, 1])

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        number={'suffix': "%"},
        domain={'x': [0, 1], 'y': [0, 1]},
        value=rating,
        gauge={'axis': {'range': [0, 100],
                        "ticksuffix": "%"}, "bar": {"color": color}},
        title={'text': "Movie Aggregated Rating"}))

    figspace.plotly_chart(fig)
