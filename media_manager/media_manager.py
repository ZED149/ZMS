

# this file contains Media Manager class

# importing libraries and modules
import sqlite3
import glob


class MediaManager:
    """Used in handling media related items.
    """

    # private data mambers
    # constructor
    def MediaManager(self):
        pass

    # methods

    # cmtid (create_movies_table_in_db)
    def cmtid(self, db_name: str = None):
        """creates a movies table in the db provided.

        Args:
            db_name (str): name of the db
        """
        if db_name:
            # connecting to the database
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            # creating movies table in db
            cursor.execute("""
CREATE TABLE "movies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"release_year"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
                           """)
            # closing connecting to the db
            conn.close()
        else:
            raise TypeError("db_name cannot be none.")
        

    # amtd (add movies to database)
    def amtd(self, path: str, db_name: str = "movies.db"):
        """Read movie media from the given path and add them to the database.
        If none db name is passed, media.db is created.\n
        Movie name should follow this pattern:
        1. It should be inside a directory.
        2. Directory name should be e.g if the name of the movie is pulp fiction
        then, directory name should be Pupl Fiction (year) [quality] ===> Pulp Fiction (1994) [4k].

        NOTE: If the pattern is not followed, then the code behaviour can lead to unexpected results, including corrupted database.

        Args:
            path (str): path to read media from
            db_name (str): name of the database file. Defaults to "movies.db".
        """

        # connecting to database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # iterating on the given path and adding them to the db_name
        for dir_name in glob.glob(path + "*"):
            altered_name = dir_name.split("\\")[1]
            altered_name = altered_name.split("[")[0]
            movie_name = altered_name.split(" (")[0]
            release_year = altered_name.split(" (")[1]
            release_year = release_year.replace(")", "")
            # now that we have our movie_name and year in a proper format, we can insert into db
            db_query = """INSERT INTO "movies"
                           (name, release_year)
                           VALUES(?,?);
"""
            data_tuple = (movie_name, release_year)
            try:
                cursor.execute(db_query,data_tuple)
            except sqlite3.IntegrityError:
                raise NameError(f"movie({movie_name}) already present in the {db_name}.")
            
            # commiting changes to db
            conn.commit()
            # closing connection to the db
            conn.close()


    # atstd (add_tv_shows_to_database)
    def atstd(self, path: str, db_name: str = "tv_shows.db"):
        """iterate on path and add all tv_shows to the given db.

        Args:
            path (str): path to iterate on.
            db_name (str, optional): Name of the database. Defaults to "tv_shows.db".
        """

        # connecting to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # iterating on path and adding tv_shows to db
        for tv_show in glob.glob(path + "*"):
            print(tv_show)
