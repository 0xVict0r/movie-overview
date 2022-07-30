from bs4 import BeautifulSoup
import requests
import json


def get_imdb_rating(imdb_id):
    url = f"https://www.imdb.com/title/{imdb_id}/?ref_=nv_sr_srsg_0"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    return float(soup.find("span", class_="sc-7ab21ed2-1 jGRxWM").text)


def get_rt_ratings(movie_name, year_str):
    search_query = movie_name.replace(" ", "%20")
    search_page = requests.get(
        f"https://www.rottentomatoes.com/search?search={search_query}")
    search_soup = BeautifulSoup(search_page.text, 'html.parser')

    movie_search = search_soup.find(
        "search-page-result", attrs={"slot": "movie"})

    first_movie = movie_search.find(
        "search-page-media-row", attrs={"releaseyear": year_str})

    movie_link = first_movie.find(
        "a", attrs={"data-qa": "thumbnail-link"})["href"]

    movie_page = requests.get(movie_link)
    search_soup = BeautifulSoup(movie_page.text, 'html.parser')

    movie_rating = json.loads(search_soup.find(
        "script", attrs={"id": "score-details-json"}).text)["modal"]["audienceScoreAll"]["averageRating"]

    return float(movie_rating)*2


def safe_execute(default, exceptions, function, *args):
    try:
        return function(*args)
    except exceptions:
        return default


if __name__ == "__main__":
    print(get_rt_ratings("The Dark Knight", "2008"))
