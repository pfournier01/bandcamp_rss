from database import AlbumDatabaseManager
from webquery import get_followed_artists_urls, update_artist
from rss_generator import initialize_rss_feed, update_rss_feed
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", type=str, help="Username of the bandcamp user for whom to generate the feed")
    parser.add_argument("-d", "--database", default="request_cache.db", required=False, type=str, help="Path of the database used to cache requests. Default: 'request_cache.db'.")
    parser.add_argument("-p", "--prefix", default="", required=False, type=str, help="Prefix of the feed files. Default: ''")
    return parser
    

def main():
    parser = create_parser()
    arguments = parser.parse_args()
    
    username = arguments.username
    database_path = arguments.database
    feed_prefix = arguments.prefix

    db_manager = AlbumDatabaseManager(database_path, force=False)
    followed_artists_urls, _ = get_followed_artists_urls(username)
    updated = {}
    for artist_url in followed_artists_urls:
        new_albums = update_artist(artist_url, db_manager)
        if new_albums:
            artist_id = new_albums[0].artist_id
            updated[artist_id] = new_albums

    if len(updated) > 0:
        # create the new ones
        created_feeds = initialize_rss_feed(feed_prefix, db_manager, force=False)
        for artist_id in created_feeds:
            if artist_id in updated:
                del updated[artist_id]
        for artist_id, albums in updated.items():
            # feed already exists but needs update
            update_rss_feed(feed_prefix, db_manager, artist_id, albums)



if __name__ == "__main__":
    main()
