from types import NoneType
import streamlit as st
import requests
from langcodes import Language
import functions
import numpy as np

api_key = st.secrets["tmdb_api"]

st.set_page_config(layout="wide")

st.markdown(
    "<style>.css-15zrgzn {display: none}</style>", unsafe_allow_html=True)

with st.sidebar:
    with st.form("Main Form"):

        search = st.text_input("Enter the title of the Movie: ")

        submit_bttn = st.form_submit_button("Search")

if submit_bttn:
    query = search.replace(" ", "%20")

    movie_id = requests.get(
        f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page=1&include_adult=false").json()["results"][0]["id"]

    movie_data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}").json()

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
        None, AttributeError, functions.get_imdb_rating, imdb_id)
    rt_rating = functions.safe_execute(
        None, AttributeError, functions.get_rt_ratings, title, release_date[:4])

    ratings_list = [float(imdb_rating), tmdb_rating, rt_rating]

    rating = np.mean(np.array([rating for rating in ratings_list if type(rating) != NoneType]))

    st.metric("Movie Rating", f"{np.round(rating*10, 2)}%")
