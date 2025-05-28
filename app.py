import streamlit as st
import pickle
import pandas as pd
import requests
import lz4.frame
import io

# Placeholder image for missing posters
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

# Fetch movie poster using TMDb API
def fetch_poster(movie_id):
    api_key = '1998efeeeb2ff2ad444bfa1179f4ec43'  # Replace with your real API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return PLACEHOLDER_POSTER
    except:
        return PLACEHOLDER_POSTER

# Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_indices:
        movie_row = movies.iloc[i[0]]
        title = movie_row['title']
        movie_id = movie_row.get('movie_id')

        poster = fetch_poster(movie_id) if pd.notna(movie_id) else PLACEHOLDER_POSTER

        recommended_movies.append(title)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters

# Load movie data (still assumes movies.pkl is local)
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)

# Load similarity from Hugging Face
@st.cache_resource
def load_similarity():
    url = "https://huggingface.co/bhushanp9/Movie-recommender-system/resolve/main/similarity.pkl.lz4"
    response = requests.get(url)
    compressed_data = io.BytesIO(response.content)
    with lz4.frame.open(compressed_data, mode='rb') as f:
        return pickle.load(f)

similarity = load_similarity()

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend Movies'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(len(names))
    for idx, (name, poster) in enumerate(zip(names, posters)):
        with cols[idx]:
            st.text(name)
            st.image(poster)
