import streamlit as st
import pickle
import pandas as pd
import requests

# Styling for the page
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .movie-container {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin: 10px;
        width: 130px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .movie-title {
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
        word-wrap: break-word;
        max-width: 130px;
        color: #333;
    }
    .movie-poster {
        width: 130px;
        height: 195px;
        margin: 0 auto;
        border-radius: 5px;
    }
    .tooltip {
        display: none;
        position: absolute;
        top: 210px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.75);
        color: #fff;
        text-align: left;
        padding: 10px;
        border-radius: 5px;
        z-index: 1;
        width: 200px;
        font-size: 12px;
    }
    .movie-container:hover .tooltip {
        display: block;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for language selection
st.sidebar.header("Movie Recommendation System")
language_choice = st.sidebar.radio("Select Language", ["English", "Hindi"])

# Button keys
button1_key = "button1"
button2_key = "button2"

# Function to get fallback image for missing poster
def get_fallback_image():
    return "https://via.placeholder.com/130x195?text=Poster+Not+Available"

# English Movie Recommendations
if language_choice == "English":
    def fetch_movie_details(movie_id):
        api_key = "8265bd1679663a7ea12ac168da84d2e8"  
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        )
        if response.status_code == 200:
            data = response.json()
            credits_response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
            )
            credits_data = credits_response.json() if credits_response.status_code == 200 else {}
            cast = ", ".join([member['name'] for member in credits_data.get('cast', [])[:5]])
            director = ", ".join([member['name'] for member in credits_data.get('crew', []) if member['job'] == 'Director'])
            rating = data.get('vote_average', None)
            poster_path = data.get('poster_path', None)
            if not poster_path:
                poster_path = get_fallback_image()  # Fallback image if poster is not available
            details = {
                'title': data['title'],
                'overview': data['overview'],
                'poster_path': poster_path,
                'cast': cast,
                'director': director,
                'rating': rating
            }
            return details
        return None

    def recommend(movie):
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            details = fetch_movie_details(movie_id)
            if details:
                recommended_movies.append(details)
        return recommended_movies

    movies_dict = pickle.load(open('movies.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity_english.pkl', 'rb'))

    st.title('Movie Recommendation System (English)')

    selected_movie_name = st.selectbox('Select Movie:', movies['title'].values)

    if st.button('Recommend Movies', key=button1_key):
        with st.container():
            st.subheader('Similar Recommendations:')
            recommendations = recommend(selected_movie_name)
            col1, col2, col3, col4, col5 = st.columns(5)
            cols = [col1, col2, col3, col4, col5]
            for i, movie in enumerate(recommendations):
                with cols[i]:
                    st.markdown(f"""
                        <div class="movie-container">
                            <img src="https://image.tmdb.org/t/p/w500/{movie['poster_path']}" class="movie-poster" alt="{movie['title']} poster">
                            <div class="movie-title">{movie['title']}</div>
                            <div class="tooltip">
                                <strong>Title:</strong> {movie['title']}<br>
                                <strong>Description:</strong> {movie['overview']}<br>
                                <strong>Cast:</strong> {movie['cast']}<br>
                                <strong>Director:</strong> {movie['director']}<br>
                                <strong>Rating:</strong> {movie['rating']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# Hindi Movie Recommendations
if language_choice == "Hindi":
    def fetch_movie_details(imdb_id):
        response = requests.get(
            f"https://www.omdbapi.com/?i={imdb_id}&apikey=34d877ac&language=en-US"
        )
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('Poster', None)
            if not poster_path:
                poster_path = get_fallback_image()  # Fallback image if poster is not available
            details = {
                'title': data['Title'],
                'overview': data['Plot'],
                'poster_path': poster_path,
                'cast': data['Actors'],
                'director': data['Director'],
                'rating': data['imdbRating']
            }
            return details
        return None

    def recommend(movie):
        movie_index = movies[movies['original_title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies = []
        for i in movies_list:
            imdb_id = movies.iloc[i[0]].imdb_id
            details = fetch_movie_details(imdb_id)
            if details:
                recommended_movies.append(details)
        return recommended_movies

    movies_dict = pickle.load(open('movies2.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity_hindi.pkl', 'rb'))

    st.title('Movie Recommendation System (Hindi)')

    selected_movie_name = st.selectbox('Select Movie:', movies['original_title'].values)

    if st.button('Recommend Movies', key=button2_key):
        with st.container():
            st.subheader('Similar Recommendations:')
            recommendations = recommend(selected_movie_name)
            col1, col2, col3, col4, col5 = st.columns(5)
            cols = [col1, col2, col3, col4, col5]
            for i, movie in enumerate(recommendations):
                with cols[i]:
                    st.markdown(f"""
                        <div class="movie-container">
                            <img src="{movie['poster_path']}" class="movie-poster" alt="{movie['title']} poster">
                            <div class="movie-title">{movie['title']}</div>
                            <div class="tooltip">
                                <strong>Title:</strong> {movie['title']}<br>
                                <strong>Description:</strong> {movie['overview']}<br>
                                <strong>Cast:</strong> {movie['cast']}<br>
                                <strong>Director:</strong> {movie['director']}<br>
                                <strong>Rating:</strong> {movie['rating']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
