import streamlit as st
import pickle
import pandas as pd
import requests


# Function to fetch movie poster
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2bf8199a4e8b295e84b2e77365a38d61")
        response.raise_for_status()  # Ensure request was successful
        data = response.json()

        poster_path = data.get("poster_path")  # Use `.get()` to avoid KeyError
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/500"  # Placeholder image if no poster found
    except requests.exceptions.RequestException as e:
        st.write(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500"  # Return placeholder on error


# Load Data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))  # ✅ Ensure similarity is loaded


# Recommendation function
def recommend(movie):
    if movie not in movies["title"].values:
        return [], []

    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    if "id" not in movies.columns:  # ✅ Check for "id" instead of "movie_id"
        st.write("Error: 'id' column missing in DataFrame!")
        return [], []

    for i in movies_list:
        if i[0] >= len(movies):  # Ensure index is valid
            continue

        movie_entry = movies.iloc[i[0]]
        movie_id = movie_entry["id"]  # ✅ Use "id" instead of "movie_id"

        recommended_movies.append(movie_entry["title"])
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters



# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie for recommendations:",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    if names:
        cols = st.columns(len(names))  # ✅ Adjust column count dynamically
        for idx, col in enumerate(cols):
            with col:
                st.text(names[idx])
                st.image(posters[idx])
    else:
        st.write("No recommendations found!")
