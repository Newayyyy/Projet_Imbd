import streamlit as st
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
import streamlit.components.v1 as components
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_elements import elements, mui, html, sync
import enum
import logging
import random
import time
from typing import List, Tuple
import plotly.graph_objects as go
import requests
from streamlit_searchbox import st_searchbox
from streamlit_modal import Modal
#from contextlib import contextmanager
#from deprecation import deprecated


# Configuration de la page et caches
st.set_page_config(
    page_title = "Imbd",
    page_icon = "🎥",
    layout="wide",
)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                }

        </style>
        """, unsafe_allow_html=True)

@st.cache_data
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

@st.cache_data
def load_data():
    df = pd.read_csv("recommendation_ML.csv")
    df['startYear'] = df['startYear'].astype(int)
    df['runtimeMinutes'] = df['runtimeMinutes'].astype(int)
    return df
df_final = load_data()

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" />
        </a>'''
    return html_code


logging.getLogger("streamlit_searchbox").setLevel(logging.DEBUG)

logo = Image.open('popcorn.png')

with st.sidebar:
    st.image(logo)
    
    selected = option_menu (None, ['📣 Mission 📣','✨ Présentation ✨', '📈 PowerBI 📈', '🎥 Recommandations 🎥', 'Fiche'], 
                         icons=['✨','✨', '✨', '✨'],    
                          menu_icon="cast", default_index=0, 
                          styles={
        "container": {"padding": "0!important", "background-color": "#e13102", "text-align": "center"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "18px", "text-align": "center", "margin":"0px", "--hover-color": "#e13102"},
        "nav-link-selected": {"background-color": "#910c00"},
         })
selected



# Diapo présentation

if selected == '📣 Mission 📣':
    col1, col2, col3 = st.columns([1, 3, 1])
    col1.write('')
    with col2 :
        video_file = open('Luca1.mp4', 'rb')
        video_bytes = video_file.read()

        st.video(video_bytes)
    col3.write('')

# Diapo présentation

elif selected == '✨ Présentation ✨':

    IMAGES = [
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/1.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/2.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/3.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/4.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/5.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/6.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/7.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/8.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/9.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/10.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/11.png",
        "https://www.obs-ed.fr/wp-content/uploads/2023/05/12.png",


    ]

    def slideshow_swipeable(images):
        # Generate a session state key based on images.
        key = f"slideshow_swipeable_{str(images).encode().hex()}"

        # Initialize the default slideshow index.
        if key not in st.session_state:
            st.session_state[key] = 0

        # Get the current slideshow index.
        index = st.session_state[key]

        # Create a new elements frame.
        with elements(f"frame_{key}"):

            # Use mui.Stack to vertically display the slideshow and the pagination centered.
            # https://mui.com/material-ui/react-stack/#usage
            with mui.Stack(spacing=2, alignItems="center"):

                # Create a swipeable view that updates st.session_state[key] thanks to sync().
                # It also sets the index so that changing the pagination (see below) will also
                # update the swipeable view.
                # https://mui.com/material-ui/react-tabs/#full-width
                # https://react-swipeable-views.com/demos/demos/
                with mui.SwipeableViews(index=index, resistance=True, onChangeIndex=sync(key)):
                    for image in images:
                        html.img(src=image, css={"width": "100%"})

                # Create a handler for mui.Pagination.
                # https://mui.com/material-ui/react-pagination/#controlled-pagination
                def handle_change(event, value):
                    # Pagination starts at 1, but our index starts at 0, explaining the '-1'.
                    st.session_state[key] = value-1

                # Display the pagination.
                # As the index value can also be updated by the swipeable view, we explicitely
                # set the page value to index+1 (page value starts at 1).
                # https://mui.com/material-ui/react-pagination/#controlled-pagination
                mui.Pagination(page=index+1, count=len(images), color="primary", onChange=handle_change)


    if __name__ == '__main__':

    
        slideshow_swipeable(IMAGES)    


# KPI
elif selected == '📈 PowerBI 📈':

    st.markdown('<iframe title="my_movies" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=7f5a7697-c1ca-46ff-b313-8fe2804b4504&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)



# Système de recommendation

elif selected == '🎥 Recommandations 🎥':



    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
    from streamlit_searchbox import st_searchbox


    X = df_final[['press_rating','spec_rating', 
                'rating_Imbd', 'oscar_count', 'BAFTA', 'Cannes_Palme_Or',
                'Cesar', 'Golden_Globes', 'Action', 'Animation', 'Arts Martiaux', 'Aventure', 'Biopic', 'Bollywood', 'Comédie',
                'Comédie dramatique', 'Comédie musicale', 'Divers', 'Drame', 'Epouvante-horreur', 'Erotique',
                'Espionnage', 'Expérimental', 'Famille', 'Fantastique', 'Guerre', 'Historique', 'Judiciaire',
                'Musical', 'Policier', 'Péplum', 'Romance', 'Science fiction', 'Sport event', 'Thriller',
                'Western']]

    distanceKNN = NearestNeighbors(n_neighbors=9).fit(X)

    def search_sth_fast(searchterm: str) -> List[str]:
        if not searchterm:
            return []
        result = df_final.loc[df_final['title'].str.contains(searchterm, case=False)] \
            .sort_values(by='spec_rating', ascending=False)[['title', 'directors_x']].values

        formatted_result = [f"{name_tuple[0]} par {name_tuple[1]}" for name_tuple in result]
        return formatted_result


    # Search box


    selected_values2 = st_searchbox(
        search_sth_fast,
        default=None,
        label="Entrez le nom d'un film",
        clear_on_submit=True,
        key='movie_names'
    )


    def get_recommendations(selected_movie, selected_director):
        movie = df_final.loc[df_final['title'] == selected_movie]
        movie = movie.loc[movie['directors_x'].apply(lambda x: selected_director in x)]

        if movie.empty:
            st.error(f"{selected_movie} par {selected_director} n'a pas été trouvé .. Désolé !")
            return -1, [], [], [], [], [], [], [], []

        stats = movie[X.columns]
        distances, indices = distanceKNN.kneighbors(stats)

        selected_movie_id = movie.iloc[0]['id']
        selected_movie_index = indices[0][0]  # Index of the selected movie in the recommendations

        # Exclude the selected movie from the recommendations
        movie_names = df_final.iloc[indices[0][1:]]['title'].tolist()
        director_names = df_final.iloc[indices[0][1:]]['directors_x'].tolist()
        preview_urls = df_final.iloc[indices[0][1:]]['poster_path'].tolist()
        ids = df_final.iloc[indices[0][1:]]['id'].tolist()

        # Additional columns
        genres_x = df_final.iloc[indices[0][1:]]['genres_x'].tolist()
        nationality = df_final.iloc[indices[0][1:]]['nationality'].tolist()
        press_rating = df_final.iloc[indices[0][1:]]['press_rating'].tolist()
        spec_rating = df_final.iloc[indices[0][1:]]['spec_rating'].tolist()
        rating_Imbd = df_final.iloc[indices[0][1:]]['rating_Imbd'].tolist()
        startYear = df_final.iloc[indices[0][1:]]['startYear'].tolist()
        runtimeMinutes = df_final.iloc[indices[0][1:]]['runtimeMinutes'].tolist()
        summary = df_final.iloc[indices[0][1:]]['summary'].tolist()

        return selected_movie_index, movie_names, director_names, preview_urls, ids, genres_x, nationality, press_rating, spec_rating, rating_Imbd, startYear, runtimeMinutes, summary



    if selected_values2:
        my_movie = selected_values2.split(" par ")[0]
        my_director = selected_values2.split(" par ")[1]
        selected_movie_index, movie_names, director_names, preview_urls, ids, genres_x, nationality, press_rating, spec_rating, rating_Imbd, startYear, runtimeMinutes, summary = get_recommendations(my_movie, my_director)
        st.subheader(f"Recommendations reliées à {my_movie} par {my_director}")
        
        num_columns = 4
        num_recommendations = len(movie_names)
        num_rows = (num_recommendations + num_columns - 1) // num_columns

        for row in range(num_rows):
            row_start = row * num_columns
            row_end = min((row + 1) * num_columns, num_recommendations)

            columns = st.columns(num_columns)
            for i, col in enumerate(columns):
                if row_start + i < row_end:
                    col.write('')
                    col.image(f'https://image.tmdb.org/t/p/original/{preview_urls[row_start + i]}', use_column_width=True)

                    button_label = "🍿"
                    modal = Modal(key=f"modal_{row_start + i}", title='' , max_width=700)
                    if col.button(button_label, key=f"know_more_button_{row_start + i}"):
                        modal.open()

                    if modal.is_open():
                        with modal.container():
                            st.title('')
                            st.divider()
                            st.header(f'{movie_names[row_start + i]} ({startYear[row_start + i]}) - {runtimeMinutes[row_start + i]} minutes ')
                            st.subheader(f'Réalisation par {director_names[row_start + i]} - {nationality[row_start + i]} ')
                            st.subheader(f'Genre(s) : {genres_x[row_start + i]}')
                            st.divider()
                            st.write('')
                            st.write(f'{summary[row_start + i]}')





















elif selected == 'Fiche':
    import requests
    from sklearn.neighbors import NearestNeighbors
    from sklearn.preprocessing import StandardScaler
    from streamlit_searchbox import st_searchbox



    X = df_final[['press_rating','spec_rating', 
                'rating_Imbd', 'oscar_count', 'BAFTA', 'Cannes_Palme_Or',
                'Cesar', 'Golden_Globes', 'Action', 'Animation', 'Arts Martiaux', 'Aventure', 'Biopic', 'Bollywood', 'Comédie',
                'Comédie dramatique', 'Comédie musicale', 'Divers', 'Drame', 'Epouvante-horreur', 'Erotique',
                'Espionnage', 'Expérimental', 'Famille', 'Fantastique', 'Guerre', 'Historique', 'Judiciaire',
                'Musical', 'Policier', 'Péplum', 'Romance', 'Science fiction', 'Sport event', 'Thriller',
                'Western']]

    distanceKNN = NearestNeighbors(n_neighbors=9).fit(X)

    def search_sth_fast(searchterm: str) -> List[str]:
        if not searchterm:
            return []
        result = df_final.loc[df_final['title'].str.contains(searchterm, case=False)] \
            .sort_values(by='spec_rating', ascending=False)[['title', 'directors_x']].values

        formatted_result = [f"{name_tuple[0]} par {name_tuple[1]}" for name_tuple in result]
        return formatted_result


    # Search box
    selected_values2 = st_searchbox(
        search_sth_fast,
        default=None,
        label="Entrez le nom d'un film",
        clear_on_submit=True,
        key='movie_names'
    )



    if selected_values2:
        movie_name = selected_values2.split(" par ")[0]  # Assuming only one movie is selected

        import requests

        url = "https://streaming-availability.p.rapidapi.com/v2/search/title"

        querystring = {"title":movie_name,"country":"fr","show_type":"movie","services":"netflix,prime.buy,hulu.addon.hbo,disney","output_language":"fr"}

        headers = {
            "X-RapidAPI-Key": "d27956f135msh62f76f18fb2c748p13987fjsna8986ed74fc3",
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }


        response = requests.get(url, headers=headers, params=querystring)

        response_data = response.json()



        # Process the response_data and print movie information
        if 'result' in response_data:
            col1, col2 = st.columns([3, 1])
            with col1 :
                    first_result = response_data['result'][0]
                    st.title(first_result['title'])
                    st.subheader(first_result['tagline'])
                    st.write(str(first_result['year']))
                    pays = first_result.get('countries', [])
                    if pays:
                        st.write("Pays d'origine:", pays[0])
                    st.write("Durée:", str(first_result['runtime']), 'minutes')
                    st.write("Age minimum recommandé:", str(first_result['advisedMinimumAudienceAge']), 'ans')
                    trailer_link = first_result.get('youtubeTrailerVideoLink')
                    if trailer_link:
                        st.video(trailer_link)
                    st.write("Résumé:", first_result['overview'])


                    
            with col2 :
                    #st.write("Backdrop URLs:", first_result['backdropURLs'])

                    #st.write("IMDb ID:", first_result['imdbId'])
                    #st.write("IMDb Rating:", first_result['imdbRating'])
                    #st.write("IMDb Vote Count:", first_result['imdbVoteCount'])
                    #st.write("TMDB ID:", first_result['tmdbId'])
                    #st.write("TMDB Rating:", first_result['tmdbRating'])
                    #st.write("Original Title:", first_result['originalTitle'])
                    #st.write("Backdrop Path:", first_result['backdropPath'])
                    #st.write("Backdrop URLs:", first_result['backdropURLs'])
                    #st.write("Genres:", first_result['genres'])
                    #st.write("Original Language:", first_result['originalLanguage'])
                    directors = first_result.get('directors', [])
                    if directors:
                        st.subheader("Réalisateur:")
                        st.write(directors[0])                        
                    st.subheader("Casting:")
                    for i, cast_member in enumerate(first_result.get('cast', [])):
                        st.write(f"{cast_member}")
                        streaming_info = first_result.get('streamingInfo', {})
                        if isinstance(streaming_info, dict):
                            streaming_info_fr = streaming_info.get('fr', {})
                            if streaming_info_fr:
                                st.subheader("Streaming :")
                                for platform, options in streaming_info_fr.items():
                                    st.subheader(f"{platform}:")
                                    if isinstance(options, list):
                                        for i, option in enumerate(options):
                                            if isinstance(option, dict):
                                                st.write("Link:", option.get('link'))
                                            else:
                                                st.write("Streaming n'est pas disponible.")
                                            st.write()  # Add a blank line between options
                                    else:
                                        st.write("Streaming info is not available.")
                                    st.write()  # Add a blank line between platforms
                            else:
                                st.write("No streaming information available.")
                        else:
                            st.write("No streaming information available.")



                    #st.write("YouTube Trailer Video ID:", first_result['youtubeTrailerVideoId'])

                    #st.write("Poster Path:", first_result['posterPath'])
                    #st.write("Poster URLs:", first_result['posterURLs'])
                    
                    st.write()
        else:
            st.write("No movie items found in the response data.")