from dataclasses import dataclass
from database import AlbumDatabaseManager, Filter

class AlbumError(Exception):
    pass

@dataclass
class AlbumSpec:
    title: str
    url: str
    img_link: str
    artist_id: int
    album_id: int
    artist_name: str

    def query_db(self, db: AlbumDatabaseManager):
        result = db.select_filter(
                db.TABLE_NAME, "*",
                Filter.And([
                    FilterAtom.Equal("IDArtist", f"{self.artist_id}"),
                FilterAtom.Equal("IDALbum", f"{self.album_id}")
                ])
        )
        matching_albums_id = result.fetchall()
        if len(matching_albums_id) > 1:
            raise AlbumError(f"More than one album matching {album} in the database.\nResponse: {matching_album_id}")
        elif len(matching_albums_id) == 1:
            return FullAlbumSpec(*matching_albums_id[0])
        else:
            return None
        

        

@dataclass
class FullAlbumSpec(AlbumSpec):
    release_date: datetime.date

    @classmethod
    def from_album_spec(cls, album_spec, release_date):
        arg_dict = {}
        for field in fields(AlbumSpec):
            arg_dict[field.name] = getattr(album_spec, field.name)
        return cls(**arg_dict, release_date=release_date)

    def add_to_db(self, db: AlbumDatabaseManager):
        return db.insert(db.TABLE_NAME,
                  (
                  self.title,
                  self.url,
                  self.img_link,
                  self.artist_id,
                  self.album_id,
                  self.artist_name,
                  self.release_date
                  )
                )

