from bs4 import BeautifulSoup
import httpx
import json
import streamlit as st

api_key = st.secrets["tmdb_api"]


def get_imdb_rating(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}/?ref_=nv_sr_srsg_0"
    response = httpx.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    return float(soup.find("span", class_="sc-7ab21ed2-1 jGRxWM").text)


def get_rt_ratings(movie_name, year_str):
    search_query = movie_name.replace(" ", "%20")
    search_page = httpx.get(
        f"https://www.rottentomatoes.com/search?search={search_query}")
    search_soup = BeautifulSoup(search_page.text, 'html.parser')

    movie_search = search_soup.find(
        "search-page-result", attrs={"slot": "movie"})

    first_movie = movie_search.find(
        "search-page-media-row", attrs={"releaseyear": year_str})

    movie_link = first_movie.find(
        "a", attrs={"data-qa": "thumbnail-link"})["href"]

    movie_page = httpx.get(movie_link)
    search_soup = BeautifulSoup(movie_page.text, 'html.parser')

    movie_rating = json.loads(search_soup.find(
        "script", attrs={"id": "score-details-json"}).text)["modal"]["audienceScoreAll"]["averageRating"]

    return float(movie_rating)*2


def get_rt_ratings(movie_name, year_str):
    search_query = movie_name.replace(" ", "%20")
    search_page = httpx.get(
        f"https://www.allocine.fr/rechercher/movie/?q={search_query}")
    search_soup = BeautifulSoup(search_page.text, 'html.parser')

    movie_search = search_soup.find("section", class_="section movies-results")
    movie_list = movie_search.find_all("li", class_="mdl")

    rating = 0

    for movie in movie_list:
        try:
            year = movie.find("span", class_="date").text[-4:]
        except AttributeError:
            year = '0'

        if year == year_str:
            rating = float(movie.find_all(
                "span", class_="stareval-note")[1].text.replace(',', '.'))

    return rating*2


def safe_execute(default, exceptions, function, *args):
    try:
        return function(*args)
    except exceptions:
        return default


def plot_cast(movie_id):
    title_alignment = """
        <style>
        #the-subheader {
        text-align: center
        }
        </style>
        """

    st.markdown(title_alignment, unsafe_allow_html=True)

    data = httpx.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}").json()

    images = []
    names = []
    character = []

    for i in range(6):
        images.append("https://image.tmdb.org/t/p/original" +
                      data['cast'][i]["profile_path"])
        names.append(data['cast'][i]["name"])
        character.append(data['cast'][i]['character'])

    st.subheader("Main Cast: ")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.image(images[0], use_column_width=True)
    col1.markdown(
        f"<h6 style='text-align: center;'>{names[0]} ({character[0]})</h6>", unsafe_allow_html=True)
    col2.image(images[1], use_column_width=True)
    col2.markdown(
        f"<h6 style='text-align: center;'>{names[1]} ({character[1]})</h6>", unsafe_allow_html=True)
    col3.image(images[2], use_column_width=True)
    col3.markdown(
        f"<h6 style='text-align: center;'>{names[2]} ({character[2]})</h6>", unsafe_allow_html=True)
    col4.image(images[3], use_column_width=True)
    col4.markdown(
        f"<h6 style='text-align: center;'>{names[3]} ({character[3]})</h6>", unsafe_allow_html=True)
    col5.image(images[4], use_column_width=True)
    col5.markdown(
        f"<h6 style='text-align: center;'>{names[4]} ({character[4]})</h6>", unsafe_allow_html=True)
    col6.image(images[5], use_column_width=True)
    col6.markdown(
        f"<h6 style='text-align: center;'>{names[5]} ({character[5]})</h6>", unsafe_allow_html=True)


if __name__ == "__main__":
    print(get_rt_ratings("star wars", "1977"))
