import httpx
import streamlit as st
import plotly.graph_objects as go

api_key = st.secrets["tmdb_api"]


def safe_execute(default, exceptions, function, *args):
    try:
        return function(*args)
    except exceptions as e:
        print(f"{function}: {e}")
        return default


def plot_gauge(rating):
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


def plot_general_info(movie):
    col1, col2 = st.columns([1, 4])
    col1.image(
        f"https://image.tmdb.org/t/p/original{movie.poster_link}", use_column_width=True)

    col2.markdown(f"""
    # {movie.title}
    ##### *Release Date: {movie.release_date}*
    ###### *Original Language: {movie.language}*
    ###### *Country(ies): {movie.countries}*
    ###### *Genre(s): {movie.genres}*
    ###### *Run Time (HH:MM:SS): {movie.run_time}*
    *{movie.synopsis}*
    """)


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
    print("Hello World")
