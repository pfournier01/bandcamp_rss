from database import AlbumDatabaseManager
from webquery import get_followed_artists_urls, update_artist
from rss_generator import initialize_rss_feed, update_rss_feed
import argparse
import os
import re

class ParserError(Exception):
    pass

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--username",
        type=str, required=False,
        help="Username of the bandcamp user for whom to generate the feed"
    )
    parser.add_argument(
        "--follow-list",
        type=str, required=False,
        help="Path to the follow-list file"
    )
    parser.add_argument(
        "-d", "--database",
        default="request_cache.db",
        required=False, type=str,
        help="Path of the database used to cache requests. Default: 'request_cache.db'."
    )
    parser.add_argument(
        "--feed-location",
        default=".",
        required=False, type=str,
        help="Path of the directory in which to store the feed files. Default: '.'"
    )
    parser.add_argument(
        "--force",
        action='store_true',
        help="Force wiping existing cache if conflict"
    )
    return parser

def is_url(string):
    url_regex = r"(https?://)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    return bool(re.match(url_regex, string))

def parse_follow_list(flist_path):
    artists_url = []
    artists_name = []
    with open(flist_path, 'r') as flist_fd:
        while line := flist_fd.readline():
            line = line.strip()
            if line[0] == "#": continue
            if is_url(line):
                if not re.match(r"https?://.*", line):
                    line = "https://" + line
                if not re.match(r".*/?music/?", line):
                    if line[-1] == "/":
                        line = line[:-1]
                    line = f"{line}/music/"
                artists_url.append(line)
                artists_name.append(line.split('//')[1].split('.')[0])
            elif line != "":
                artists_url.append(f"https://{line}.bandcamp.com/music/")
                artists_name.append(line)
    return artists_url, artists_name

class ProcessedArgs:
    @staticmethod
    def from_namespace(arguments: argparse.Namespace):
        if not (arguments.username is None) ^ (arguments.follow_list is None):
            raise ParserError(
                "Excatly one of --username or --follow-list must be defined"
            )
        out = ProcessedArgs
        
        using_username = arguments.username is not None
        if using_username:
            out.followed_artists_urls, out.followed_artists_names \
                = get_followed_artists_urls(arguments.username)
        else:
            if not os.path.isfile(arguments.follow_list):
                raise ParserError(f"Follow list {follow_list} does not exist")
            else:
                out.followed_artists_urls, out.followed_artists_names \
                    = parse_follow_list(arguments.follow_list)

        out.database_path = arguments.database
        if not os.path.isdir(arguments.feed_location):
            if arguments.force:
                os.makedirs(arguments.feed_location)
            else:
                raise ParserError(
                    f"Feed location target {arguments.feed_location} does not exist"
                )
        out.feed_location = arguments.feed_location
        out.force = arguments.force

        return out


def main():
    parser = create_parser()
    arguments = parser.parse_args()
    processed_args = ProcessedArgs.from_namespace(arguments)
    
    database_path =             processed_args.database_path
    feed_location =             processed_args.feed_location
    force =                     processed_args.force
    followed_artists_urls =     processed_args.followed_artists_urls
    followed_artists_names =    processed_args.followed_artists_names

    db_manager = AlbumDatabaseManager(database_path, force=force)
    updated = {}
    for artist_url in followed_artists_urls:
        new_albums = update_artist(artist_url, db_manager)
        if new_albums:
            artist_id = new_albums[0].artist_id
            updated[artist_id] = new_albums

    if len(updated) > 0:
        # create the new ones
        created_feeds = initialize_rss_feed(
            feed_location,
            followed_artists_names,
            db_manager,
            force=force
        )
        for artist_id in created_feeds:
            if artist_id in updated:
                del updated[artist_id]
        for artist_id, albums in updated.items():
            # feed already exists but needs update
            artist_name = albums[0].artist_name
            update_rss_feed(feed_location, db_manager, artist_name, albums)



if __name__ == "__main__":
    main()
