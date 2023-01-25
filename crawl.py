import pandas as pd
import requests
from bs4 import BeautifulSoup

def extract_movies_essentials(bs_entities):  

    for entitiy in bs_entities:
        rating_entry = entitiy.find('td', {'class': 'ratingColumn imdbRating'})
        if rating_entry == None:
            continue
        movie_imdb_rating = rating_entry.strong.text
        
        entries = entitiy.find('td', {'class': 'titleColumn'})
        movie_title = entries.a.text
        movie_published_year = entries.span.text[1:-1]
        title_ref = entries.a['href']
        movie_title_url = "{}{}".format(base_url, title_ref)
        # reference for id: https://developer.imdb.com/documentation/key-concepts
        movie_id = entries.a['href'].split('/')[2]
        yield movie_id, movie_title, movie_published_year, movie_title_url, movie_imdb_rating



def extract_movies_detail(title_url):
    response = requests.get(title_url, headers=header)

    soup = BeautifulSoup(response.content, 'html.parser')
    movie_popularity = soup.find('div', {'data-testid': 'hero-rating-bar__popularity__score'})
    if movie_popularity == None:
        movie_popularity = '0'
    else:
        movie_popularity = movie_popularity.get_text()
    movie_director = soup.find('div', {'class': 'ipc-metadata-list-item__content-container'}).get_text()
    movie_genre_entries = soup.find('div', {'data-testid': 'genres'}).findAll('a')
    movie_genre = []
    for movie_genre_entry in movie_genre_entries:
        movie_genre.append(movie_genre_entry.text)
    movie_introduction = soup.find('p', {'data-testid': 'plot'})
    if movie_introduction == None:
        movie_introduction = soup.find('div', {'data-testid': 'plot'})
    movie_introduction = movie_introduction.find('span', {'data-testid': 'plot-xs_to_m'}).get_text()
    movie_casts = []
    cast_section = soup.find('section', {'data-testid': 'title-cast'})
    cast_entries = cast_section.findAll('div', {'data-testid': 'title-cast-item'})
    for cast_entry in cast_entries:
        movie_casts.append(cast_entry.contents[1].a.text)
    return movie_popularity, movie_director, movie_casts, movie_genre, movie_introduction


base_url = "https://www.imdb.com"
url = "{}/chart/top".format(base_url)
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
entities = soup.findAll('tr')
columns = ['Movie ID', 'Name', 'Year', 'Movie link', 'Movie rating']
columns.extend(['Popularity', 'Director', 'Casts', 'Type', 'Introduction'])
df_imdb = pd.DataFrame(columns=columns)
movie_essentials = extract_movies_essentials(entities)

for i in range(250):
    movie_id, movie_title, movie_published_year, movie_title_url, movie_imdb_rating = next(movie_essentials)
    movie_data = [movie_id, movie_title, movie_published_year, movie_title_url, movie_imdb_rating]
    detailed_movie_data = extract_movies_detail(movie_title_url)
    movie_data.extend(detailed_movie_data)
    print(movie_data)
    df_imdb.loc[len(df_imdb)] = movie_data
# print(df_imdb)