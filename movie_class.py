import httpx
import datetime
from langcodes import Language
from bs4 import BeautifulSoup
import json


class Movie:
    def __init__(self, movie_id, api_key):
        self.id = movie_id

        with httpx.Client() as client:
            self.movie_data = client.get(
                f"https://api.themoviedb.org/3/movie/{self.id}?api_key={api_key}").json()

            self.cast_data = client.get(
                f"https://api.themoviedb.org/3/movie/{self.id}/credits?api_key={api_key}").json()["cast"]

        self.poster_link = self.movie_data["poster_path"]
        self.title = self.movie_data["original_title"]
        self.release_date = self.movie_data["release_date"]
        self.synopsis = self.movie_data["overview"]
        self.language = Language.make(
            language=self.movie_data["original_language"]).display_name()
        self.countries = ', '.join(
            map(str, [country["name"] for country in self.movie_data["production_countries"]]))
        self.genres = ', '.join(
            map(str, [genre["name"] for genre in self.movie_data["genres"]]))
        self.cast = ', '.join(
            map(str, [cast["name"] for cast in self.cast_data][:6]))
        self.imdb_id = self.movie_data["imdb_id"]
        self.tmdb_rating = self.movie_data["vote_average"]
        self.run_time = datetime.timedelta(minutes=self.movie_data["runtime"])

    def get_imdb_rating(self):
        imdb_response = httpx.get(
            f"https://www.imdb.com/title/{self.imdb_id}/")

        imdb_soup = BeautifulSoup(imdb_response.text, 'html.parser')

        rating = float(imdb_soup.find(
            "span", class_="sc-7ab21ed2-1 jGRxWM").text)

        return rating

    def get_allocine_ratings(self):
        search_query = self.title.replace(" ", "%20")
        search_page = httpx.get(
            f"https://www.allocine.fr/rechercher/movie/?q={search_query}")
        search_soup = BeautifulSoup(search_page.text, 'html.parser')

        movie_search = search_soup.find(
            "section", class_="section movies-results")
        movie_list = movie_search.find_all("li", class_="mdl")

        rating = 0

        for movie in movie_list:
            try:
                year = movie.find("span", class_="date").text[-4:]
            except AttributeError:
                year = '0'

            if year == self.release_date[:4]:
                rating = float(movie.find_all(
                    "span", class_="stareval-note")[1].text.replace(',', '.'))

        return rating*2

    def get_rt_ratings(self):
        rt_query = self.title.replace(" ", "%20")
        rt_page = httpx.get(
            f"https://www.rottentomatoes.com/search?search={rt_query}/")
        rt_soup = BeautifulSoup(rt_page.text, 'html.parser')

        rt_search = rt_soup.find(
            "search-page-result", attrs={"slot": "movie"})

        rt_first_movie = rt_search.find(
            "search-page-media-row", attrs={"releaseyear": self.release_date[:4]})

        rt_movie_link = rt_first_movie.find(
            "a", attrs={"data-qa": "thumbnail-link"})["href"]

        rt_movie_page = httpx.get(rt_movie_link)
        rt_second_search_soup = BeautifulSoup(
            rt_movie_page.text, 'html.parser')

        rt_movie_rating = json.loads(rt_second_search_soup.find(
            "script", attrs={"id": "score-details-json"}).text)["modal"]["audienceScoreAll"]["averageRating"]

        return float(rt_movie_rating)*2
