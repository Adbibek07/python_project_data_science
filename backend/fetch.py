import requests
from dotenv import load_dotenv
import os
import csv

load_dotenv()

token = os.getenv("YOUR_TOKEN")


def get_movies(map):
    url = "https://api.themoviedb.org/3/movie/popular"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    movies = []
    for page in range(1, 51):   # first 60 pages
        params = {"page": page}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        for movie in data["results"]:
            genre_names = [map[g] for g in movie["genre_ids"]]
            genre_ids = ", ".join(str(g) for g in movie["genre_ids"])
            genres_str = ", ".join(genre_names)
            movie["genre_names"] = genres_str
            movie["genre_ids"] = genre_ids
        
        # movies = movies.append(movies1)
        movies.extend(data["results"]) # adds movies 
            
        # print(type(movies))
    # print(movies)
    print(len(movies)) #40 movies for 2 pages
    return movies


def map_genre():
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    url = "https://api.themoviedb.org/3/genre/movie/list"

    response = requests.get(url, headers=headers)
    data = response.json()

    # create dictionary: {id: name}
    genre_map = {g["id"]: g["name"] for g in data["genres"]}
    
    return genre_map

# def convert_genreid_to_genre():
map_genre()
movies = get_movies(map=map_genre())

# print (movies)

# Get the CSV headers (all keys from the first dictionary)
headers = movies[0].keys()

import os

DIR = os.path.dirname(os.path.abspath(__file__))

# # clean null and boolean values before writing
# for movie in movies:
#     for key, value in movie.items():
#         if value is None:
#             movie[key] = ""
#         elif isinstance(value, bool):
#             movie[key] = str(value)

# Write to CSV
with open(os.path.join(DIR, "movies.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(movies)