

# this file contains Media Manager class

# importing libraries and modules
import sqlite3
import os
import glob
from .message_generator import MessageGenerator
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from dotenv import load_dotenv
from media_manager.message_generator import MessageGenerator
from email.mime.image import MIMEImage
from datetime import datetime
from email.utils import formataddr
from email.message import EmailMessage
from email.header import Header
from email.mime.base import MIMEBase
from email import encoders
import re
import time
from warnings import deprecated


class MediaManager:
    """Used in handling media related items.
    """

    # data members
    WARNING = "WARNING: "
    ERROR = "ERROR: "
    MESSAGE = ""
    conn = None
    __receipents_emails = None

    # utility functions
    # send_email_core
    def __send_email_core(self, username: str, receiver: str,
                        message: str, host: str, port: int,
                        password: str, context) -> None:
        msg = MIMEMultipart('related')
        msg['From'] = formataddr((str(Header('ZED', 'utf-8')), username))
        msg['To'] = receiver
        # subject [Updates] ZED Media Server
        msg['Subject'] = "Test Mail 27"
        msg.preamble = "This is a multi-part message in MIME format."

        # attaching msgAlternative to the msg
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        # attaching message to the msgAlternative
        msgText = MIMEText(message, 'html')
        msgAlternative.attach(msgText)

        # opening image in binary
        with open('C:\\Users\\salma\\OneDrive\\Desktop\\Media_Manager\\media_manager\\test.png', 'rb') as fb:
            msgImage = MIMEImage(fb.read(), _subtype='png')
        
        del msgImage['Content-Disposition']
        msgImage.add_header('Content-Disposition', 'inline')
        msgImage.add_header('Content-ID', '<image1>')
        msgImage.add_header('X-Attachment-Id', 'image1')  # optional but may help

        msg.attach(msgImage)

        # send email    
        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, msg.as_string())

    # private data mambers
    # constructor
    def __init__(self, db_name: str = None):
        # connecting to the DB
        self.conn = sqlite3.connect(db_name)
        # fetch customer emails here
        cursor = self.conn.cursor()
        query = '''
SELECT email, full_name from emails
'''
        cursor.execute(query)
        self.__receipents_emails = cursor.fetchall()

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
                conn.close()
                return
            # closing connecting to the db
            conn.close()
        else:
            raise TypeError("db_name cannot be none.")
        

    # amtd (add movies to database)
    def amtd(self, verbose: bool = False, path: str = None, db_name: str = "movies.db") -> list:

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

        cursor = self.conn.cursor()
        movies = []
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
            # creating tuple
            data_tuple = (movie_name, release_year)
            # inserting into DB
            try:
                cursor.execute(db_query,data_tuple)
                # appending the name of movie to the movies list for email purposes
                movies.append(movie_name)
            except sqlite3.IntegrityError:
                if verbose:
                    print(f"{self.WARNING}Movie --> {movie_name} already present in DB.")
                continue      
        # Return
        return movies


    # ctvtid (create_tv_shows_table_in_database)
    def ctstid(self, db_name: str = None):
        """Creates a database for the tv shows with the provided name.

        Args:
            db_name (str, optional): Name of the database. Defaults to None.
        """
        if db_name:    
            cursor = self.conn.cursor()

            # database query
            # query to create Episodes table
            query_1 = """CREATE TABLE "episodes" (
	"episode_id"	INTEGER NOT NULL UNIQUE,
	"episode_name"	TEXT NOT NULL,
	"tv_show_id"	INTEGER,
	"created_date"	TEXT NOT NULL,
	PRIMARY KEY("episode_id" AUTOINCREMENT),
	FOREIGN KEY("tv_show_id") REFERENCES "tv_shows"("tv_show_id")
);
"""
            # query to create TV Shows table
            query_2 = """CREATE TABLE "tv_shows" (
	"tv_show_id"	INTEGER NOT NULL UNIQUE,
	"tv_show_name"	TEXT NOT NULL UNIQUE,
	"created_date"	TEXT NOT NULL DEFAULT 0,
	"last_modified_date"	TEXT,
	PRIMARY KEY("tv_show_id" AUTOINCREMENT)
);
"""
            # executing query
            try:
                cursor.execute(query_1)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}Table 'episodes' already exists in DB.")
                return
            try:
                cursor.execute(query_2)
            except sqlite3.OperationalError:
                print(f"{self.ERROR}Table 'tv_shows' already exists in DB.")
                return
        else:
            raise TypeError("db_name cannot be none.")


    # atstd (add_tv_shows_to_database)
    @deprecated("This method is deprecated and will no longer receive updates. Use nmtatstd() instead.")
    def atstd(self, verbose: bool = False, path: str = None, db_name: str = "tv_shows.db") -> dict:
        """iterate on path and add all tv_shows to the given db.

        Args:
            path (str): path to iterate on.
            db_name (str, optional): Name of the database. Defaults to "tv_shows.db".
        """
        cursor = self.conn.cursor()
        tv_shows = {}

        # iterating on path and adding tv_shows to db
        for root, folders, files in os.walk(path):
            for folder in folders:
                query = """INSERT INTO "tv_shows"
                            (tv_show_name)
                            VALUES(?);
"""
                data_tuple = (folder, )     # folder is the name of tv_show
                # tv_shows[folder] = []
                try:
                    # inserting tv_show name into the DB
                    self.conn.execute(query, data_tuple)
                    # adding tv_show name to the dict with an empty list (for episodes) as value
                    tv_shows[folder] = []
                except sqlite3.IntegrityError:
                    if verbose: 
                        print(f"{self.WARNING}Tv Show --> {folder} already present in DB.")
                    continue
            
            for file in files:      # file is the episode for that tv_show
                # need to strip episode name for just its number
                # e.g Dil e Nadaan Episode 23 - [Eng Sub] ......
                # we just need the episode number
                episode_number = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", file)

                if episode_number == None:
                    print(file)

                tv_show_dir_name = root.replace(path, "")
                # get tv_show_id based on the tv_show_dir_name
                query = """SELECT (tv_show_id)
                            FROM "tv_shows"
                            WHERE tv_show_name=?
"""
                data_tuple = (tv_show_dir_name, )
                cursor.execute(query, data_tuple)
                tv_show_id = cursor.fetchone()[0]
                
                # insert tv_show_name into the db
                query = """INSERT INTO "episodes"
                            (episode_name, tv_show_id)
                            VALUES(?,?);
"""
                # file is the name of the episode
                data_tuple = (episode_number.group(), tv_show_id)
                try:
                    self.conn.execute(query, data_tuple)
                    # adding episode for that tv_show
                    tv_shows[tv_show_dir_name].append(episode_number.group())
                except sqlite3.IntegrityError:
                    if verbose:
                        print(f"{self.WARNING}Episode {file} is already present in the {tv_show_dir_name}.")
                    continue
        return tv_shows
    

    # autstd(add_updated_tv_shows_to_db)
    @deprecated("This method is deprecated and will no longer receive updates. Use nmtatstd() instead.")
    def autstd(self, db_name: str = None, path: str = None) -> None:
        """Updates already added TV Shows in DB. Updates their episodes.

        Args:
            db_name (str, optional): Name of the DB to retrive tv_show name from. Defaults to None.
            path (str, optional): path to read from. Defaults to None.

        Raises:
            TypeError: _description_
            TypeError: _description_
        """

        # aquiring cursor
        cursor = self.conn.cursor()
        tv_shows_id = {}
        # walking the path
        for root, folders, files in os.walk(path):
            for folder in folders:
                query = '''SELECT tv_show_id
                FROM tv_shows
                WHERE tv_show_name=?'''
                cursor.execute(query, (folder, ))
                tv_shows_id[folder] = cursor.fetchone()[0]
            for file in files:  # file is the name of the episode
                episode_number = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", file)
                
                # adding new episodes to the DB
                query = '''INSERT INTO "episodes"
                (episode_name, tv_show_id)
                VALUES(?,?);'''
                tv_show_dir_name = root.replace(path, "")
                data_tuple = (episode_number.group(), tv_shows_id[tv_show_dir_name])
                cursor.execute(query, data_tuple)
                self.conn.commit()
        print(tv_shows_id)
                
    
    # nmtatstd (new_method_to_add_tv_shows_to_database)
    def nmtatstd(self, verbosity: bool = False, db_name: str = None, path: str = None) -> dict:
        """Add TV Shows from 'path' to the db. Also updates the previously added tv shows along with their episodes.

        Args:
            verbosity (bool, optional): Set to True to increase the verbosity of the method. Defaults to False.
            db_name (str, optional): Name of the db to perform actions on. Defaults to None.
            path (str, optional): Path from where to read tv_shows. Defaults to None.
        """

        # retrieving cursor
        cursor = self.conn.cursor()
        
        # walking on the given path
        obj = os.scandir(path=path)
        tv_shows = {}
        for e in obj:
            # retreive last modified time fromt the DB
            query = '''
            SELECT tv_show_id
            FROM tv_shows
            WHERE tv_show_name=?
'''
            data_tuple = (e.name,)
            tv_show_id = cursor.execute(query, data_tuple).fetchone()
            # if no id is fetched, it means no tv_shows has added for that name, so we need to add it
            # we also add episodes for that tv_show
            if tv_show_id == None:
                a = {}
                # inserting tv_show for that name
                query = '''
                INSERT INTO "tv_shows"
                (tv_show_name, created_date, last_modified_date)
                VALUES (?,?,?);
'''
                created_date = time.ctime(e.stat().st_birthtime)
                last_modified_date = time.ctime(e.stat().st_mtime)

                data_tuple = (e.name, created_date, last_modified_date)
                cursor.execute(query, data_tuple)
                a[e.name] = []
                # adding it to the dict that will be used for email purposes
                tv_shows[e.name] = []
                if verbosity:
                    print(f"[TV SHOW]: {e.name} inserted.")
                # fetching tv_show_id again after inserting it into the
                query = '''
                SELECT tv_show_id
                FROM tv_shows
                WHERE tv_show_name=?
'''
                data_tuple = (e.name,)
                tv_show_id = cursor.execute(query, data_tuple).fetchone()[0]
                # inserting episodes into db now,
                for episode in os.scandir(path=e.path):
                    query = '''
                    INSERT INTO "episodes"
                    (episode_name, tv_show_id, created_date)
                    VALUES (?,?,?);
'''
                    episode_name = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", episode.name).group()
                    data_tuple = (episode_name, tv_show_id, time.ctime(episode.stat().st_birthtime))
                    cursor.execute(query, data_tuple)
                    a[e.name].append(episode_name)
                    # adding to the dict that will be used for email purposes
                    tv_shows[e.name].append(episode_name)
                if verbosity:
                    print(f"[TV_SHOW_EPISODES]: ({e.name})--> {a[e.name]}")

            else:   # it means a tv_show with that name is already present
                # now, we need to check the last modification date for that id,
                # if it is different from the modification date of the tv_show present in the directory,
                # then it means, new episodes/material has been added

                # query to fetch all episodes for that tv_show
                query = '''
                SELECT episode_name
                FROM episodes
                WHERE tv_show_id=?
'''
                # fetching all episodes for that tv_show
                episodes = cursor.execute(query, (tv_show_id[0], )).fetchall()
                episodes = [c[0] for c in episodes]
                if verbosity:
                    print(f"[EPISODES]: {episodes}")
                a = {}
                episode_inserted_flag = False
                # iterating on that tv_show
                for episode in os.scandir(path=e.path):
                    episode_name = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", episode.name).group()
                    if episode_name not in episodes:
                        # append to list if that episode is already not present in db
                        a[episode_name] = time.ctime(episode.stat().st_birthtime)
                        # query to insert episode along with its details into the db
                        query = '''
                        INSERT INTO "episodes"
                        (episode_name, tv_show_id, created_date)
                        VALUES(?,?,?);
                        '''
                        data_tuple = (episode_name, tv_show_id[0], time.ctime(episode.stat().st_birthtime))
                        cursor.execute(query, data_tuple)
                        # setting the episode_inserted_flag to True, as we will be updating last_modified_date for it later
                        episode_inserted_flag = True
                        # adding it to the dict that will be returned for email purposes
                        tv_shows[e.name] = []
                        tv_shows[e.name].append(episode_name)
                if episode_inserted_flag:
                    # now we also need to upadte last_modified_date in tv_shows
                    query = '''
                    UPDATE tv_shows
                    SET last_modified_date=?
                    WHERE tv_show_id=?
'''
                    data_tuple = (time.ctime(), tv_show_id[0])
                    cursor.execute(query, data_tuple)
                    # now reverting the flag
                    episode_inserted_flag = False
                # controllig output with verbosity statements
                if verbosity:
                    print(f"{e.name}: {a}")
        return tv_shows


    # cetid(create_email_table_in_database)
    def cetid(self, db_name: str = None):
        """Creates Emails table in the given db.
        Args:
            db_name (str, optional): _description_. Defaults to None. Name of the DB in which "emails" table to be initialized
        """

        if db_name:
            cursor = self.conn.cursor()

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
                return 
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
            cursor = self.conn.cursor()

            import pandas as pd
            df = pd.read_excel(file)
            full_names = df['full name'].to_list()
            emails = df['emails'].to_list()

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

    
    # send_emails
    def send_emails(self, verbose: bool = False, db_name: str = None, movies_list: list = None, tv_shows: dict = None) -> bool:
        if verbose:
            print(f"[MOVIES]: {movies_list}")
            print(f"[TV SHOWS]: {tv_shows}")
        for receipent in self.__receipents_emails:
            # message (email markup) for the user is generated by the .__ce() method.
            message = self.__ce(verbose=verbose, db_name=db_name, movies_list=movies_list, tv_shows=tv_shows, 
                                full_name=receipent[1])
            # email is sent by using the .se() method, it receives message markup and user name for the receipent
            if verbose:
                print(f"[SENDING EMAIL]: to {receipent[1].capitalize()} @ {receipent[0]}")
            flag = self.__se(message=message, receiver_email=receipent[0])
            if verbose and flag:
                print(f"[EMAIL SENT]: to {receipent[1].capitalize()} @ {receipent[0]}")
            if not flag:
                if verbose:
                    print(f"[EMAIL NOT SENT]: to {receipent[1].capitalize()} @ {receipent[0]}")
                return False
        return True


    # se (send_email)
    def __se(self, message: str = None, receiver_email: str = None) -> bool:
        """Sends an email to the receiver's. Receipent(s) are fetched from the DB. In order to add
        more receipent(s) to the server, use aetd() method.

        Args:
            message (str, optional): Contains the HTML format of message to be sent. Defaults to None.
        """
        # Validations
        if message:
            host = "smtpout.secureserver.net"
            port = 465

            username = "no-reply@zed149.com"
            password = "NFAKisAlive@123"

            context = ssl.create_default_context()
            # core functionality to send email
            # self.__send_email_core(username, receiver_email, message, host, port, password, context)
            return True
        else:
            return False


    # ce (create_email)
    def __ce(self, verbose: bool = False, db_name: str = None, movies_list: list = None, tv_shows: dict = None, full_name: str = None) -> str:
        # Validations
        # movies_list = ["Interstellar", "John Wick 2", "Iron Man", "The Day After Tomorrow"]
        # tv_shows = {
        #     "Parizaad": [],
        #     "BOL": [],
        #     "Meem Se Muhabbat": [],
        #     "Zindagi Gulzar Hai": []
        # }
        if not movies_list and not tv_shows:
            return ""
        if not movies_list and tv_shows:
            message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
            return message
        if not tv_shows and movies_list:
            message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
            return message
        message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
        return message
    

    # commit
    def commit(self):
        self.conn.commit()
        self.conn.close()