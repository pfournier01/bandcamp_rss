import requests
from bs4 import BeautifulSoup
from albums import AlbumSpec, FullAlbumSpec
from database import AlbumDatabaseManager
import datetime
import re
from utils import MONTHS_TO_INT

def find_release_date(album: AlbumSpec) -> datetime.date:
    album_page_response = requests.get(album.url)
    album_page = album_page_response.content
    album_soup = BeautifulSoup(album_page, 'html.parser')
    album_credits= album_soup.find('div', class_='tralbumData tralbum-credits').text.strip()
    album_release_date_raw = album_credits.split('\n')[0]
    match = re.match(r'released ([a-zA-Z]*) (\d*), (\d*)', album_release_date_raw)
    month, day, year = match.groups()
    date = datetime.date(int(year), MONTHS_TO_INT[month.upper()], int(day))
    return date

def request_albums_from_artist_page(artist_url) -> list[FullAlbumSpec]:
    response = requests.get(artist_url)
    page_content = response.content
    soup = BeautifulSoup(page_content, 'html.parser')
    artist_container = soup.find('p', id='band-name-location')
    artist_name = artist_container.find('span', class_='title').text.strip()
    albums_container = soup.find('div', class_='leftMiddleColumns')
    albums = []
    for album in albums_container.find_all('li', class_='music-grid-item'):
        title = album.find('p', class_='title').text.strip().split('\n')[0]
        album_rel_url = album.find('a', href=True)['href']
        img = album.find('div', class_='art').find('img')
        img_link = img['src'] if img['src'] != "/img/0.gif" else img['data-original']
        artist_id = int(album['data-band-id'])
        # [6:] to remove 'album-' prefix
        album_id = int(album['data-item-id'][6:])
        artist_url_simple = artist_url[:-6] if artist_url[-6:] == "music/" else artist_url
        albums.append(AlbumSpec(
                      title=title,
                      # url[:-6] to remove "music/"
                      url=artist_url_simple+album_rel_url,
                      img_link=img_link,
                      artist_id=artist_id,
                      album_id=album_id,
                      artist_name=artist_name
                     )
        )
    return albums
def update_artist(artist_url, db: AlbumDatabaseManager):
    albums = request_albums_from_artist_page(artist_url)
    new_albums = [album for album in albums if album.query_db(db) is None]
    new_full_albums = []
    for album in new_albums:
        date = find_release_date(album)
        full_album = FullAlbumSpec.from_album_spec(album, release_date = date)
        full_album.add_to_db(db)
        new_full_albums.append(full_album)
    return new_full_albums
    
def get_followed_artists_urls(username):
    profile_url = f"https://bandcamp.com/{username}/following/artists_and_labels"
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.content, "html.parser")
    following = soup.find_all("a", class_="fan-username")
    following_url = []
    following_name = []
    for block in following:
        following_url.append(block['href'])
        following_name.append(block.text)
    
    return following_url, following_name
