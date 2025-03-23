

# this file contains Media Manager class

# importing libraries and modules
import sqlite3
import os
import glob


class MediaManager:
    """Used in handling media related items.
    """

    # data members
    WARNING = "WARNING: "
    ERROR = "ERROR: "

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
            try:
                cursor.execute("""
CREATE TABLE "movies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"release_year"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
                           """)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}Table 'moveis' already exists in DB.")
                # print("Exiting Program...")
                conn.close()
                return
                # exit(0)
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
        already_added_movies = []
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
                # raise NameError(f"movie({movie_name}) already present in the {db_name}.")
                already_added_movies.append(movie_name)
                continue
            
        # commiting changes to db
        conn.commit()
        # closing connection to the db
        conn.close()
        # print to screen if already present movies are not added in the DB
        if len(already_added_movies) > 0:
            print(f"{self.WARNING}Already added movies were not committed to the DB.")
            print(f"Movies includes...\n{already_added_movies}")
            # print(already_added_movies)


    # ctvtid (create_tv_shows_table_in_database)
    def ctstid(self, db_name: str = None):
        """Creates a database for the tv shows with the provided name.

        Args:
            db_name (str, optional): Name of the database. Defaults to None.
        """
        if db_name:    
            # connecting to database
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # database query
            query_1 = """CREATE TABLE "episodes" (
	"episode_id"	INTEGER NOT NULL UNIQUE,
	"episode_name"	TEXT NOT NULL UNIQUE,
	"tv_show_id"	INTEGER,
	PRIMARY KEY("episode_id" AUTOINCREMENT),
	FOREIGN KEY("tv_show_id") REFERENCES "tv_shows"("tv_show_id")
);
"""
            query_2 = """CREATE TABLE "tv_shows" (
	"tv_show_id"	INTEGER NOT NULL UNIQUE,
	"tv_show_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("tv_show_id" AUTOINCREMENT)
);
"""
            # executing query
            try:
                cursor.execute(query_1)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}Table 'episodes' already exists in DB.")
                # print("Exiting Program...")
                conn.close()
                return
                # exit with status 1. Status 1 means that an error occured while creating table in the database.
                exit(1)
            try:
                cursor.execute(query_2)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}Table 'tv_shows' already exists in DB.")
                # print("Exiting Program...")
                conn.close()
                return
                # exit with status 1. Status 1 means that an error occured while creating table in the database.
                exit(1)

            # closing the connection to the database
            conn.close()
        else:
            raise TypeError("db_name cannot be none.")


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
        for root, folders, files in os.walk(path):
            for folder in folders:
                query = """INSERT INTO "tv_shows"
                            (tv_show_name)
                            VALUES(?);
"""
                data_tuple = (folder, )
                try:
                    # inserting tv_show name into the DB
                    conn.execute(query, data_tuple)
                except sqlite3.IntegrityError:
                    print(f"{self.WARNING}Tv Show --> {folder} already present in DB.")
                    continue
            
            for file in files:      # file is the episode for that tv_show
                tv_show_dir_name = root.replace(path, "")
                # get tv_show_id based on the tv_show_dir_name
                query = """SELECT (tv_show_id)
                            FROM "tv_shows"
                            WHERE tv_show_name=?
"""
                data_tuple = (tv_show_dir_name, )
                cursor.execute(query, data_tuple)
                # print(f"{tv_show_dir_name}:----> {file}")
                tv_show_id = cursor.fetchone()[0]
                # print(tv_show_id)  # printing assiciated tv_show with that episode
                
                # insert tv_show_name into the db
                query = """INSERT INTO "episodes"
                            (episode_name, tv_show_id)
                            VALUES(?,?);
"""
                data_tuple = (file, tv_show_id)
                try:
                    conn.execute(query, data_tuple)
                except sqlite3.IntegrityError:
                    print(f"{self.WARNING}Episode {file} is already present in the {tv_show_dir_name}.")
                    continue

        conn.commit()
        conn.close()    


    # cetid(create_email_table_in_database)
    def cetid(self, db_name: str = None):
        """Creates Emails table in the given db.
        Args:
            db_name (str, optional): _description_. Defaults to None. Name of the DB in which "emails" table to be initialized
        """

        if db_name:
            # connecting to the DB
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # writing query
            query = """CREATE TABLE "emails" (
        "email"	TEXT NOT NULL UNIQUE,
        "full_name"	TEXT NOT NULL,
        "id"	INTEGER NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    """
            # executing query
            try:
                cursor.execute(query)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}table 'emails' already exists in DB.")
                # closing connection
                conn.close()
                return 
            # if query is executed sucessfully
            # closing connection to the DB
            conn.close()
        else:
            raise TypeError("db_name cannot be none.")
        
    
    # aetd (add_emails_to_database)
    def aetd(self, file: str = None, db_name: str = None):
        """Add emails to the db_name. If either of file or db_name is None, the program quits.

        Args:
            file (str, optional): _description_. Defaults to None. Name of the file from which emails to be extracted from,
            can be of .xlsx or .csv. Must includes only two headers in the columns. These are... email, full_name
            db_name (str, optional): _description_. Defaults to None. Name of the database in which emails to be inserted.
        """

        if file is None or db_name is None:
            raise TypeError("db_name or file cannot be none.")
        else:
            # connecting to the db
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            import pandas as pd
            df = pd.read_excel(file)
            full_names = df['full name'].to_list()
            emails = df['emails'].to_list()
            # print(full_names)
            # print(emails)

            # generating query
            query = """INSERT INTO "emails"
            (full_name, email)
            VALUES (?, ?);
"""
            data = [(a, b) for a , b in zip(full_names, emails)]
            for d in data:
                data_tuple = d
                try:
                    cursor.execute(query, data_tuple)
                except sqlite3.IntegrityError:
                    print(f"{self.WARNING}email \"{d[1]}\" already exists in the DB.")
            # data_tuple = (full_names, emails)
            # cursor.execute(query, data_tuple)
            conn.commit()
            conn.close()


    # se (send_email)
    def se(self):
        pass


    # ce (create_email)
    def ce(self, db_name: str) -> None:
        # fetch all movies from DB
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # fetching all movies names from DB
        query = """
SELECT name FROM movies
"""
        cursor.execute(query)
        list_of_movie_names = cursor.fetchall()
        list_of_movie_names = [m_movie[0] for m_movie in list_of_movie_names]

        # Now, fetching all tv shows from the DB


        conn.close()