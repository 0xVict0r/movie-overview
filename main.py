import streamlit as st
import httpx
from movie_class import Movie
import functions
import numpy as np

api_key = st.secrets["tmdb_api"]

st.set_page_config(layout="wide")

st.title("Movie Overview & Rating Aggregator")

st.write("When looking at potential movies to watch, I always found it boring to look at multiple websites to see if it was even worth my time, or if the website I was looking at was biased in any way. Hence why I created this movie lookup tool. It aggregates movie data from multiple sources (TMDB, IMDB, Rotten Tomatoes, Allocine) to give a nice overview. It also gives an aggregated movie rating from the before mentionned sources. Simply enter the name of the movie (no TV) and the program will find the relevant information for you.")

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

    movie = Movie(movie_id, api_key)

    functions.plot_general_info(movie)

    imdb_rating = functions.safe_execute(
        None, (AttributeError, TypeError), movie.get_imdb_rating)
    rt_rating = functions.safe_execute(
        None, (AttributeError, TypeError, IndexError, ValueError), movie.get_rt_ratings)
    allocine_rating = functions.safe_execute(
        None, (AttributeError, TypeError, IndexError, ValueError), movie.get_allocine_ratings)

    ratings_list = [imdb_rating, movie.tmdb_rating, rt_rating, allocine_rating]

    rating = np.round(np.mean(
        np.array([rating for rating in ratings_list if type(rating) != type(None)]))*10, 1)

    functions.plot_cast(movie_id)

    functions.plot_gauge(rating)
