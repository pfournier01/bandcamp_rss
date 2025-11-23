from database import AlbumDatabaseManager
from albums import FullAlbumSpec
import os
from utils import adapt_date_iso
import datetime

def which_feed_to_create(rss_prefix, db:AlbumDatabaseManager):
    all_albums_in_db = db.select_simple(db.TABLE_NAME, "*").fetchall()
    all_albums_in_db = [FullAlbumSpec(*album) for album in all_albums_in_db]
    artists = set([album.artist_id for album in all_albums_in_db])
    to_create = []
    for artist_id in artists:
        artist_rss_path = f"{rss_prefix}_{artist_id}.atom"
        if not os.path.isfile(artist_rss_path):
            to_create.append(artists)
    return to_create


def feed_item_from_album(album: FullAlbumSpec, item_template: str):
    item = item_template.replace('{album_name}', album.title)\
                        .replace('{album_link}', album.url)\
                        .replace('{album_release}', adapt_date_iso(album.release_date))\
                        .replace('{artist_id}', str(album.artist_id))\
                        .replace('{album_id}', str(album.album_id))\
                        .replace('{image_url}', album.img_link)\
                        .replace('{artist_name}', album.artist_name)
    return item


def initialize_rss_feed(rss_prefix, db:AlbumDatabaseManager, force=False):
    all_albums_in_db = db.select_simple(db.TABLE_NAME, "*").fetchall()
    all_albums_in_db = [FullAlbumSpec(*album) for album in all_albums_in_db]
    artists = set([album.artist_id for album in all_albums_in_db])
    created_feeds = []
    for artist_id in artists:
        artist_rss_path = f"{rss_prefix}_{artist_id}.atom"
        if os.path.isfile(artist_rss_path):
            # feed already exists
            if not force:
                continue
        created_feeds.append(artist_id)
        albums_of_artist = [album for album in all_albums_in_db if album.artist_id == artist_id]
        last_update = max([datetime.date.fromisoformat(album.release_date) for album in albums_of_artist])
        if albums_of_artist == []:
            continue
        artist_name = albums_of_artist[0].artist_name
        artist_url = albums_of_artist[0].url
        artist_url = "/".join(artist_url.split("/")[:3]+["music"])
        with open('header.xml', 'r') as header_fd:
            header_raw = header_fd.read()
        header = header_raw.replace('{artist}', artist_name)
        header = header.replace('{last_update}', last_update.isoformat())
        header = header.replace('{artist_id}', str(artist_id))
        header = header.replace('{artist_url}', artist_url) 
        
        with open('item.xml', 'r') as item_fd:
            item_template = item_fd.read()

        items = []
        for album in albums_of_artist:
            item = feed_item_from_album(album, item_template)
            items.append(item)
        items = "".join(items)
        rss = header.replace('{items}', items)
        with open(artist_rss_path, 'w') as rss_fd:
            rss_fd.write(rss)
    return created_feeds

def update_rss_feed(rss_prefix:str, db:AlbumDatabaseManager, artist_id:int, albums: list[FullAlbumSpec]):
    with open('item.xml', 'r') as item_fd:
        item_template = item_fd.read()
    artist_rss_path = f"{rss_prefix}_{artist_id}.atom"
    with open(artist_rss_path, 'r') as feed_fd:
        feed = feed_fd.read()
    # header: rows 0-8
    feed_lines = feed.split('\n')
    header = '\n'.join(feed_lines[:9])
    previous_entries = '\n'.join(feed_lines[9:])
    new_items = [
        feed_item_from_album(album, item_template)
        for album in albums
    ]
    new_feed = header + '\n'.join(new_items) + previous_entries
    with open(artist_rss_path, 'w') as feed_fd:
        feed_fd.write(new_feed)

    
    
    

