import sqlite3
import os
import enum
import dataclasses
import functools
from typing import Any
from utils import adapt_date_iso
import datetime

class DatabaseError(Exception):
    pass

class InitializedStatus(enum.Enum):
    INITIALIZED = 0
    FILE_DOES_NOT_EXIST = -1
    TABLE_DOES_NOT_EXIST = -2
    COLUMNS_DO_NOT_EXIST = -3

    def __bool__(self):
        # Exit code for success is 0
        # for failure: < 0
        return self.value >= 0

@dataclasses.dataclass
class FilterEqual:
    col_name: str
    value: Any

    def __str__(self):
        return f"{self.col_name} = {self.value}"

class FilterAtom:
    Equal = FilterEqual


@dataclasses.dataclass
class FilterAnd:
    filters: list

    def __str__(self):
        return " AND ".join([str(f) for f in self.filters]) 

@dataclasses.dataclass
class FilterOr:
    filters: list

    def __str__(self):
        return  " OR ".join([str(f) for f in self.filters])

class Filter:
    Atom = FilterAtom
    And = FilterAnd
    Or = FilterOr



def adapt_int(py_value):
    return int(py_value)

def adapt_text(py_value):
    return str(py_value)

def adapt_real(py_value):
    return float(py_value)

def adapt_blob(py_value):
    return bytes(py_value)

def adapt_null(py_value):
    return None

def adapt_date(py_value):
    if isinstance(py_value, datetime.date):
        return adapt_date_iso(py_value)
    else:
        return ""

def adapt_data(py_value, sql_dtype):
    match sql_dtype.upper():
        case "INT":
            return adapt_int(py_value)
        case "TEXT":
            return adapt_text(py_value)
        case "REAL":
            return adapt_real(py_value)
        case "BLOB":
            return adapt_blob(py_value)
        case "NULL":
            return adapt_null(py_value)
        case "DATE":
            return adapt_date(py_value)

class DatabaseManager():
    def __init__(self, database_path, *args, **kwargs):
        self.db_path = database_path
        self.connector = sqlite3.connect(self.db_path)
        self.cursor = self.connector.cursor()
        return self.__post_init__(*args, **kwargs)

    def __post_init__(self, *args, **kwargs):
        pass

    @functools.cache
    def columns(self, table):
        return list(self.cursor.execute(f"PRAGMA TABLE_INFO({table})"))

    def execute_query(self, query):
        return self.cursor.execute(query)

    def select_simple(self, table, columns):
        query = f"SELECT {", ".join(columns)} FROM {table}"
        return self.execute_query(query)

    def select_filter(self, table, columns, filter_):
        query = f"SELECT {", ".join(columns)} FROM {table} WHERE {str(filter_)}"
        return self.execute_query(query)


    def insert(self, table, values):
        columns = self.columns(table)
        if len(columns) != len(values):
            raise DatabaseError(f"Trying to insert an incorrect amount of values in {table}")
        types = [x[2] for x in columns]
        values_adapted = [adapt_data(v, t) for v, t in zip(values, types)]
        query = f"INSERT into {table} VALUES({','.join(['?']*len(values))})"
        return self.cursor.execute(query, values_adapted)
        

class AlbumDatabaseManager(DatabaseManager):
    TABLE_NAME = "Albums"
    COLUMNS = ["Title", "Url", "Image_Link", "IDArtist", "IDAlbum", "ArtistName", "ReleaseDate"]
    COLUMN_TYPES = ["TEXT", "TEXT", "TEXT", "INT", "INT", "TEXT", "DATE"]

    def __post_init__(self, force):
        super().__post_init__()
        self.init_db(force)
    

    def is_db_initialized(self):
        file_exists = os.path.isfile(self.db_path)
        if file_exists:
            tables = self.cursor.execute("SELECT Name FROM SQLITE_SCHEMA")
            tables = list(tables)
            if self.TABLE_NAME not in tables:
                if len(tables) == 0:
                    return InitializedStatus.TABLE_DOES_NOT_EXIST
                else:
                    raise DatabaseError(f"Table {self.TABLE_NAME} does not exist in {self.db_path} and database is not empty.")
            else:
                columns = self.cursor.execute(f"PRAGMA TABLE_INFO({self.TABLE_NAME})")
                # columns: id, name, type, ?, ?, ?
                column_names = [x[1] for x in columns]
                if not(set(self.COLUMNS) <= set(column_names)):
                    if len(column_names) == 0:
                        return InitializedStatus.COLUMNS_DO_NOT_EXIST
                    else:
                        raise DatabaseError(f"In table {self.TABLE_NAME}, all of the columns {self.COLUMNS} do not exist in {self.db_path} and the table is not empty.")
                else:
                    return InitializedStatus.INITIALIZED
        else:
            return InitializedStatus.FILE_DOES_NOT_EXIST

    def init_db(self, force):
        def create_table():
            columns_desc = [
                f"{c_name} {c_type},"
                for c_name, c_type
                in zip(self.COLUMNS, self.COLUMN_TYPES)
            ]
            columns_desc = "\n".join(columns_desc)
            query = f"CREATE TABLE {self.TABLE_NAME} ( {columns_desc} )"
            self.cursor.execute(query)

        def wipe_table():
            self.cursor.execute(f"DROP TABLE {self.TABLE_NAME}")

        try:
            initialized_status = self.is_db_initialized()
            if not initialized_status:
                if initialized_status == InitializedStatus.COLUMNS_DO_NOT_EXIST:
                    if force:
                        wipe_table()
                    else:
                        raise DatabaseError(f"Table {self.TABLE_NAME} exists but it has no columns. Why does this happen??")
                create_table()
                return None
