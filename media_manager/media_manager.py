

# this file contains Media Manager class

# importing libraries and modules
import sqlite3

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
	"name"	INTEGER NOT NULL UNIQUE
);""")
            # closing connecting to the db
            conn.close()
        else:
            raise TypeError("db_name cannot be none.")
        

    # aftd (add folders to database)
    def aftd(self, path: str, db_name: str = "media.db"):
        """Read all media from the given path and add them to the database.
        If none db name is passed, media.db is created.

        Args:
            path (str): path to read media from
            db_name (str): name of the database file
        """

        # connecting to database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        # iterating on the given path and adding them to the db_name
        
        

