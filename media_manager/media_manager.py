

# this file contains Media Manager class

# importing libraries and modules
import sqlite3
import os
import glob
from .message_generator import MessageGenerator
import pandas as pd
from dotenv import load_dotenv
from media_manager.message_generator import MessageGenerator
from email.utils import formataddr
import re
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from .classes import TVShow, Episode, Movie
import requests
from .classes.logging import Logging
import http.client as httplib
import shutil
from .classes.mail_handling import MailHandling
import os
import subprocess
from datetime import datetime
from .admin import Admin, E_Channel
from dotenv import load_dotenv

# loading enviournmental varables into our scope
load_dotenv(dotenv_path='/home/salman/ZMS/media_manager/.env')

class MediaManager(Admin):
    """Used in handling media related items.
    """

    # data members
    WARNING = "WARNING: "
    ERROR = "ERROR: "
    MESSAGE = ""
    conn = None
    __receipents_emails = None
    __logger = None
    __channel_name_scraper_driver = None
    __db_name = None
    __MASTER_PATH_MOVIES = None
    __MASTER_PATH_TV_SHOWS = None
    __Mail_Handler = MailHandling()
    __MOVIES_CRAWLING_PATH = None
    __TV_SHOWS_CRAWLING_PATH = None

    # server_email_credentials
    __SERVER_EMAIL = os.getenv('EMAIL_FROM_USERNAME')           # user_name for the no_reply email
    __SERVER_PASSWORD = os.getenv("EMAIL_FROM_PASSWORD")        # password for the account
    __SERVER_EMAIL_SUBJECT = os.getenv('EMAIL_FROM_SUBJECT')    # subject of the server generated email

    # utility functions

    # get_creation_time
    def __get_creation_time(self, file_path: str = None) -> str:
    # Use stat to try to get birth time (%w)
        try:
            result = subprocess.run(
                ["stat", "-c", "%w", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            creation_time = result.stdout.strip()
            if creation_time == "-" or creation_time == "":
                return None
            else:
                # Strip timezone and nanoseconds, parse datetime
                creation_time = creation_time.split("+")[0].split(".")[0]
                dt = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S")
                creation_time = dt.isoformat()
                return creation_time
        except subprocess.CalledProcessError:
            return None
        
    # get_modification_time
    def __get_modification_time(self, file_path: str = None) -> str:
        return datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
    
    # move_movies_and tv_shows
    def __move_media(self, verbosity: bool = False, movies_from_path: str = None, tv_shows_from_path: str = None):
        """Move movies and tv_shows from their crawling paths to the Master path.

        Args:
            movies_from_path (str, optional): Path from movies are to be moved. Defaults to None.
            tv_shows_from_path (str, optional): Path from where tv_shows are to be moved. Defaults to None.
        """
        if verbosity:
            self.__logger.write("-------------------------Move Media, __move_media()-------------------------\n")

        if verbosity:
            self.__logger.write("Moving Movies:\n")
        # moving movies
        for movie in os.scandir(path=movies_from_path):
            if verbosity:
                self.__logger.write(f"Moving Movie=({movie.path}) TO dst=({self.__MASTER_PATH_MOVIES}).\n")
                try:
                    shutil.move(src=movie.path, dst=self.__MASTER_PATH_MOVIES, copy_function=shutil.copytree)   # move files recursively
                except Exception as excep:
                    self.__logger.write(f"Cannot move {movie} to dst=({self.__MASTER_PATH_MOVIES}). Both on different disks.\n")

        if verbosity:
            self.__logger.write("Moving movies DONE.\n")
            self.__logger.write("Moving TV Shows:\n")
        # moving tv_shows
        for tv_show in os.scandir(path=tv_shows_from_path):
            if verbosity:
                self.__logger.write(f"Moving TV_SHOW=({tv_show.path}) TO dst=({self.__MASTER_PATH_TV_SHOWS}).\n")
            try:    
                shutil.move(src=tv_show.path, dst=self.__MASTER_PATH_TV_SHOWS, copy_function=shutil.copytree)
            except shutil.Error:
                if verbosity:
                    self.__logger.write(f"Tv_Show dst='{self.__MASTER_PATH_TV_SHOWS}' already exists. Copying each episode 1 by 1 now.\n")
                    # it means that a directory for that tv_show already exists, now we will iterate on that tv_show
                    # to move each episode 1 by 1
                    for episode in os.scandir(path=tv_show.path):
                        if verbosity:
                            self.__logger.write(f"Moving episode='{episode.path}' to dst='{self.__MASTER_PATH_TV_SHOWS + tv_show.name + '/'}'.\n")
                        shutil.move(src=episode.path, dst=self.__MASTER_PATH_TV_SHOWS + tv_show.name + '/')

        if verbosity:
            self.__logger.write("Moving tv_shows DONE.\n")
            self.__logger.write("-------------------------__move_media(), DONE-------------------------\n")

    # scrap_channel_name
    def __scrap_channel_name(self, verbose: bool = False, tv_show_name: str = None) -> str:
        """Scrap TV Channel name for the given tv show and returns it.

        Args:
            tv_show_name (str, optional): Name of the show to scrap channel of. Defaults to None.

        Returns:
            str: Channel Name.
        """
        if verbose:
            self.__logger.write("-------------------------Scrap Channel Name, __scrap_channel_name()-------------------------\n")
            self.__logger.write("Initializing driver.\n")
        # initializing driver
        self.__channel_name_scraper_driver = uc.Chrome()
        url = "https://www.youtube.com/"
        if verbose:
            self.__logger.write(f"Making request to the url({url}) and fetching frontend code.\n")
        # making request to the url(youtube.com) and fetching frontend code
        self.__channel_name_scraper_driver.get(url)
        if verbose:
            self.__logger.write(f"Searching for tv_show({tv_show_name}) and sending ENTER keys.\n")
        # searching for drama name (tv_show_name) in the search bar and pressing ENTER
        self.__channel_name_scraper_driver.find_element(by="xpath", value='/html/body/ytd-app/div[1]/div[2]/ytd-masthead/div[4]/div[2]/yt-searchbox/div[1]/form/input').send_keys(f"{tv_show_name} drama" + Keys.RETURN)
        time.sleep(5)
        if verbose:
            self.__logger.write("Scraping channel name.\n")
        # scraping tv channel name for that drama
        channel = self.__channel_name_scraper_driver.find_element(by='xpath', value='/html/body/ytd-app/div[1]/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/yt-lockup-view-model[1]/div/div/yt-lockup-metadata-view-model/div[1]/div[1]/yt-content-metadata-view-model/div[1]/span[1]/span/a')
        if verbose:
            self.__logger.write(f"[CHANNEL NAME FOR]: {tv_show_name} is ({channel.text}).\n")
            print(f"[CHANNEL NAME FOR]: {tv_show_name} is ({channel.text}).")
        channel_name =  channel.text
        if verbose:
            self.__logger.write("Closing driver.\n")
        # closing driver
        time.sleep(5)
        self.__channel_name_scraper_driver.close()
        if verbose:
            self.__logger.write("-------------------------__scrap_channel_name(), DONE-------------------------\n")
        # Return
        return channel_name
    
    # extract_movie_details
    def __extract_movie_details(self, verbosity: bool = False, movie_name: str = None) -> dict:
        """Returns basic details of the movie. Details are fetched by YTS API.

        Args:
            movie_name (str, optional): Name of the movie to fetch details of. Defaults to None.

        Returns:
            dict: Returns the dictionary of basic movie details.
        """

        if verbosity:
            self.__logger.write("-------------------------Extract Movie Details, __extract_movie_details()-------------------------\n")
        movie_details = {}
        # contructing url
        url_for_id = f"https://yts.mx/api/v2/list_movies.json?&query_term='{movie_name}"
        if verbosity:
            self.__logger.write("Attempting to make GET request.\n")
        # making request
        response = requests.get(url=url_for_id)
        if verbosity:
            if response.status_code == 200:
                self.__logger.write("Request succeeded.\n")
        if response.status_code != 200:
            # it means our request to fetch movie_details has failed due to some YTS server issue
            if verbosity:
                self.__logger.write("Failed to fetch data.\n")
                self.__logger.write("Exiting program.\nCode 0\n")
                self.__logger.write("-------------------------extract_movie_details(), DONE-------------------------\n")
        #   print(f"[MOVIE] [MOVIE DETAILS] [REQUEST] Failed to request movie details from the YTS.mx")
            exit(0)
        if response.json()["data"]["movie_count"] == 0:
        # it means this movie is not present in YTS server.
            if verbosity:
                self.__logger.write("Movie details are not present in the YTS server.\n")
                self.__logger.write("-------------------------extract_movie_details(), DONE-------------------------\n")
            return movie_details

        if verbosity:
            self.__logger.write("Fetchig ID.\n")
        movie_id = response.json()["data"]["movies"][0]["id"]
        # now extract basic movie details based on this id
        url_for_basic_movie_details = f"https://yts.mx/api/v2/movie_details.json?movie_id={movie_id}"
        if verbosity:
            self.__logger.write("Making GET request to fetch details now.\n")
        # making request
        response = requests.get(url=url_for_basic_movie_details)
        movie_details["year"] = response.json()["data"]["movie"]["year"]
        movie_details["genres"] = response.json()["data"]["movie"]["genres"]
        movie_details["rating"] = response.json()["data"]["movie"]["rating"]
        movie_details["small_cover_image"] = response.json()["data"]["movie"]["small_cover_image"]
        if verbosity:
            self.__logger.write("Sucessfully fetched details.\n")
            self.__logger.write("-------------------------extract_movie_details(), DONE-------------------------\n")
        return movie_details

    # check_internet_connectivity
    def __check_internet_connectivity(self, verbosity: bool = False) -> bool:
        """Checks the internet connection by making a request to the Youtube.com

        Args:
            verboseity (bool, optional): Set to True to increase verbosity otherwise False. Defaults to False.
        Returns:
            bool: True if request is successful otherwise False.
        """
        if verbosity:
            self.__logger.write("-------------------------Check Internet Connectivity, __check_internet_connectivity()-------------------------\n")
        url = "www.youtube.com"
        timeout = 3
        if verbosity:
            self.__logger.write(f"Constructing url({url}) with timeout={timeout}\n")
        try:
            if verbosity:
                self.__logger.write("Attempting connection with the server.\n")
            connection = httplib.HTTPConnection(url, timeout=timeout)
            if verbosity:
                self.__logger.write("Sending http request to the url and requesting headers.\n")
            connection.request("HEAD", "/")
            if verbosity:
                self.__logger.write("Closing connection.\n")
                self.__logger.write("-------------------------__check_internet_connectivity(), DONE-------------------------\n")
            connection.close()
            return True
        except Exception as excep:
            if verbosity:
                self.__logger.write("-------------------------__check_internet_connectivity(), DONE-------------------------\n")
            return False

    # ce (create_email)
    def __ce(self, verbose: bool = False, db_name: str = None, movies_list: list = None, 
             tv_shows: TVShow = None, full_name: str = None) -> str:
        if verbose:
            self.__logger.write("-------------------------Create Email, __ce()-------------------------\n")
        # Validations
        if verbose:
            self.__logger.write("Performing validations on attributes 'movies_list' and 'tv_shows'.\n")
        if not movies_list and not tv_shows:
            if verbose:
                self.__logger.write("Attributes 'movies_list' and 'tv_shows' are none.\n")
                self.__logger.write("-------------------------__ce(), DONE-------------------------\n")
            return ""
        if not movies_list and tv_shows:
            if verbose:
                self.__logger.write("Attribute 'movies_list' is none.\n")
                self.__logger.write(f"Generating message(email markup) for the user {full_name}\n")
            message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
            if verbose:
                self.__logger.write("-------------------------__ce(), DONE-------------------------\n")
            return message
        if not tv_shows and movies_list:
            if verbose:
                self.__logger.write("Attribute 'tv_shows' is none.\n")
                self.__logger.write(f"Generating message(email markup) for the user {full_name}\n")
            message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
            if verbose:
                self.__logger.write("-------------------------__ce(), DONE-------------------------\n")
            return message
        if verbose:
            self.__logger.write("Attributes 'movies_list' and 'tv_shows' both are VALID.\n")
            self.__logger.write(f"Generating message(email_markup) for the user {full_name}\n")
        message = MessageGenerator.no_reply_movies_added(full_name, movies_list, tv_shows=tv_shows)
        if verbose:
            self.__logger.write("-------------------------__ce(), DONE-------------------------\n")
        return message
    
        """Sends an email to the receiver's. Receipent(s) are fetched from the DB. In order to add
        more receipent(s) to the server, use aetd() method.

        Args:
            message (str, optional): Contains the HTML format of message to be sent. Defaults to None.
        """
        
    # private data mambers
    # constructor
    def __init__(self, verbosity:bool = False, db_name: str = None, logger_name: str = None,
                 a_name: str = None, a_email: str = None, a_password: str = None) -> None:
        super().__init__(a_name, a_email, a_password)
        # assigning db_name to private data member
        self.__db_name = db_name
        self.__MASTER_PATH_MOVIES = os.getenv("MASTER_PATH_MOVIES")
        self.__MASTER_PATH_TV_SHOWS = os.getenv("MASTER_PATH_TV_SHOWS")

        # initializing Logger
        if logger_name:
            self.__logger = Logging(logger_name=logger_name)
            self.__logger.log_starting_details_to_file()
        if verbosity:
            self.__logger.write("-------------------------Constructor, __init__()-------------------------\n")
        if verbosity:
            self.__logger.write("Checking internet connectivity.\n")
        # checking internet connection before proceeding.
        connected = self.__check_internet_connectivity(verbosity=verbosity)
        if connected:
            if verbosity:
                self.__logger.write("Connection successful.\n")
                self.__logger.write("Can proceed the script.\nInitializing private data members and preparing context.\n")
            if verbosity:
                self.__logger.write(f"Connecting to the Database ({db_name}).\n")
            # connecting to the DB
            self.conn = sqlite3.connect(db_name)
            if verbosity:
                self.__logger.write("Acquiring cursor.\n")
            # fetch customer emails here
            cursor = self.conn.cursor()
            # query to fetch all emails from db
            query = '''SELECT email, full_name 
                        FROM emails'''
            try:
                if verbosity:
                    self.__logger.write("Executing query to fetch emails from DB and store them in __receipent_emails.\n")
                cursor.execute(query)
                self.__receipents_emails = cursor.fetchall()
                if verbosity:
                    self.__logger.write("Query successful.\n")
                    self.__logger.write("-------------------------__init__(), DONE-------------------------")
            except:
                if verbosity:
                    self.__logger.write("-------------------------__init__(), DONE-------------------------")
        else:
            self.__logger.write("Connection not successful.\n")
            self.__logger.write("Terminating script.\n")
            self.__logger.write("-------------------------__init__(), DONE-------------------------")
            exit(0)
    
    # Methods
    # cmtid (create_movies_table_in_db)
    def cmtid(self, verbosity: bool = False, db_name: str = None):
        """creates a movies table in the db provided.

        Args:
            db_name (str): name of the db
        """
        if verbosity:
            self.__logger.write('-------------------------CREATING MOVIES TABLE IN DB, cmtid()-------------------------\n')
        if db_name:
            if verbosity:
                self.__logger.write(f'Attempting connection to the DB {db_name}\n')
            if verbosity:
                self.__logger.write(f"Successfully connected to the DB.\n")
            cursor = self.conn.cursor()
            # creating movies table in db
            try:
                if verbosity:
                    self.__logger.write("Attempting to execute query to create 'movies' table in db.\n")
                cursor.execute("""
CREATE TABLE "movies" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"release_year"	TEXT NOT NULL,
	"genre"	TEXT,
	"rating"	TEXT,
	"small_cover_image"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
                           """)
                if verbosity:
                    self.__logger.write("Sucessfully created 'movies' table in db.\n")
            except sqlite3.OperationalError:
                if verbosity:
                    self.__logger.write("Error creating 'movies' table as it already exists.\n")
                # print(f"{self.ERROR}Table 'moveis' already exists in DB.")
                self.__logger.write('------------------------- cmtid() DONE -------------------------\n')
                return
            # closing connecting to the db
        else:
            if verbosity:
                self.__logger.write("Attribute 'db_name' cannot be none.\n")
            # raise TypeError("db_name cannot be none.")
        if verbosity:
            self.__logger.write('------------------------- cmtid() DONE -------------------------\n')
        
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

        if verbose:
            self.__logger.write('-------------------------Add Movies To The DB, amtd()-------------------------\n')
            self.__logger.write("Acquiring cursor.\n")
        cursor = self.conn.cursor()
        if verbose:
            self.__logger.write("Cursor sucessfully acquired.\n")
        movies = []
        # iterating on the given path and adding them to the db_name
        for dir_name in glob.glob(path + "*"):
            altered_name = dir_name.split("/")[4]
            altered_name = altered_name.split("[")[0]
            movie_name = altered_name.split(" (")[0]
            release_year = altered_name.split("(")[1]
            release_year = release_year.replace(")", "")
            if verbose:
                self.__logger.write(f"[EXTRACTING MOVIE DETAILS]: of ({movie_name}).\n")
            # try to insert movie into DB. If an exception occurs it means the movie is alreay present in the DB.
            # So, no need to proceed futher any code for this movie_name and can return back
            
            query = '''SELECT id
            FROM movies
            WHERE name=?
            '''
            data_tuple = (movie_name, )
            data = cursor.execute(query, data_tuple).fetchone()
            if data:
                # it means that the movie is already present so we can exit here
                if verbose:
                    self.__logger.write("[MOVIE] (movie_name) is already present in the DB.\n")
                    self.__logger.write('-------------------------amtd() DONE-------------------------\n')
                continue
            movie_details = self.__extract_movie_details(verbosity=verbose, movie_name=movie_name)
            if verbose:
                if movie_details:
                    self.__logger.write("[EXTRACTING MOVIE DETAILS]: GREEN\n")
            # now that we have our movie_name and year in a proper format, we can insert into db
            db_query = """INSERT INTO "movies"
                           (name, release_year,genre,rating,small_cover_image)
                           VALUES(?,?,?,?,?);
"""
            # creating tuple
            if movie_details == {}:
                data_tuple = (movie_name, release_year, None, None, None)
            else:
                data_tuple = (movie_name, release_year, movie_details['genres'][0], movie_details['rating'], movie_details['small_cover_image'])
            # inserting into DB
            try:
                if verbose:
                    self.__logger.write("Attempting to insert movie into db.\n")
                cursor.execute(db_query,data_tuple)
                if verbose:
                    self.__logger.write("Sucessfully inserted.\n")
                # appending all details of movie in a Movie object to be returned and later used in email purposes
                if movie_details == {}:
                    movies.append(Movie(movie_name=movie_name))
                else:
                    movies.append(Movie(movie_name=movie_name, release_year=release_year, genres=movie_details['genres'],
                                    rating=movie_details['rating'], small_cover_image=movie_details['small_cover_image']))
            except sqlite3.IntegrityError:
                if verbose:
                    self.__logger.write(f"{self.WARNING}Movie --> {movie_name} already present in DB.\n")
                    # print(f"{self.WARNING}Movie --> {movie_name} already present in DB.")
                continue      
        # Return
        self.__logger.write('-------------------------amtd() DONE-------------------------\n')
        return movies

    # ctvtid (create_tv_shows_table_in_database)
    def ctstid(self, verbosity: bool = False, db_name: str = None):
        """Creates a database for the tv shows with the provided name.

        Args:
            db_name (str, optional): Name of the database. Defaults to None.
        """

        if verbosity:
            self.__logger.write('-------------------------Create TV Shows Table In DB, ctstid()-------------------------\n')
        if db_name:
            if verbosity:
                self.__logger.write("Acquiring cursor from the db.\n")
            cursor = self.conn.cursor()
            if verbosity:
                self.__logger.write("Cursor successfully acquired.\n")
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
    "channel_name"	TEXT,
	PRIMARY KEY("tv_show_id" AUTOINCREMENT)
);
"""
            # executing query
            try:
                if verbosity:
                    self.__logger.write("Attempting to execute query to create episodes table.\n")
                cursor.execute(query_1)
                if verbosity:
                    self.__logger.write("Episodes table GREEN.\n")
            except sqlite3.OperationalError:
                if verbosity:
                    self.__logger.write(f"{self.ERROR}Table 'episodes' already exists in DB.\nExiting program.\n")
                # print(f"{self.ERROR}Table 'episodes' already exists in DB.")
                return
            try:
                if verbosity:
                    self.__logger.write("Attempting to execute query to create tv_shows table.\n")
                cursor.execute(query_2)
                if verbosity:
                    self.__logger.write("TVShows table GREEN.\n")
            except sqlite3.OperationalError:
                if verbosity:
                    self.__logger.write(f"{self.ERROR}Table 'tv_shows' already exists in DB.\nExiting program.\n")
                # print(f"{self.ERROR}Table 'tv_shows' already exists in DB.")
                return
        else:
            if verbosity:
                self.__logger.write("Attribute error. 'db_name' cannot be none.\n")
            raise TypeError("db_name cannot be none.")
        if verbosity:
            self.__logger.write('-------------------------ctstid(), DONE-------------------------\n')

    # nmtatstd (new_method_to_add_tv_shows_to_database)
    def nmtatstd(self, verbosity: bool = False, db_name: str = None, path: str = None) -> TVShow:
        """Add TV Shows from 'path' to the db. Also updates the previously added tv shows along with their episodes.

        Args:
            verbosity (bool, optional): Set to True to increase the verbosity of the method. Defaults to False.
            db_name (str, optional): Name of the db to perform actions on. Defaults to None.
            path (str, optional): Path from where to read tv_shows. Defaults to None.
        """

        if verbosity:
            self.__logger.write('-------------------------New Method To Add TV Shows To DB, nmtatstd()-------------------------\n')
        # retrieving cursor
        if verbosity:
            self.__logger.write("Acquiring cursor from the db.\n")
        cursor = self.conn.cursor()
        if verbosity:
            self.__logger.write("Cursor successfully acquired.\n")
        
        # walking on the given path
        obj = os.scandir(path=path)
        tv_shows = {}
        tv_shows_list = []  # list to be used for return purpose, will contain all the tv_shows along with their episodes that are now inserted
        for e in obj:   # for each tv_show in provided path
            # retreive last modified time fromt the DB
            query = '''
            SELECT tv_show_id, channel_name
            FROM tv_shows
            WHERE tv_show_name=?
'''
            data_tuple = (e.name,)
            if verbosity:
                self.__logger.write("Executing query to fetch tv_show_id and channel_name.\n")
            data = cursor.execute(query, data_tuple).fetchall()
            if verbosity:
                self.__logger.write("Query successfully done.\n")
            tv_show_id = None
            channel_name = None
            if data:
                tv_show_id = data[0][0]
                channel_name = data[0][1]
            # if no id is fetched, it means no tv_shows has added for that name, so we need to add it
            # we also add episodes for that tv_show
            if tv_show_id == None:      # add tv_show for the first time
                a = {}
                # scraping channel name from web
                if verbosity:
                    print(f"[CHANNEL NAME]: --> {e.name}")
                    self.__logger.write(f"Attempting to scrap channel name for the tv_show ({e.name})\n")
                try:
                    channel_name = self.__scrap_channel_name(verbose=verbosity, tv_show_name=e.name)
                except Exception as excep:
                    if verbosity:
                        self.__logger.write("Exception occurred. Exiting program.\nSending details to the admin.")
                    self.notify_admin(verbose=verbosity, channel=E_Channel.email, excep=excep, logger=self.__logger)
                    self.conn.close()
                    self.__logger.write("-------------------------nmtatstd(), DONE-------------------------\n")
                    exit(0)

                if verbosity:
                    self.__logger.write("Scraping done.\n")
                # inserting tv_show for that name
                query = '''
                INSERT INTO "tv_shows"
                (tv_show_name, created_date, last_modified_date, channel_name)
                VALUES (?,?,?,?);
'''
                created_date = self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name)     # /media/from/tv_shows/ + Ae Dil
                last_modified_date = self.__get_modification_time(self.__TV_SHOWS_CRAWLING_PATH + e.name)                           # /media/from/tv_shows/ + Ae Dil

                data_tuple = (e.name, created_date, last_modified_date, channel_name)
                if verbosity:
                    self.__logger.write(f"Attempting to insert tv_show({e.name}) in the db.\n")
                cursor.execute(query, data_tuple)
                a[e.name] = []
                # adding it to the dict that will be used for email purposes
                tv_shows[e.name] = []
                tv_shows[e.name].append("na")
                if verbosity:
                    self.__logger.write(f"[TV SHOW]: {e.name} inserted.\n")
                    # print(f"[TV SHOW]: {e.name} inserted.")
                # fetching tv_show_id again after inserting it into the
                query = '''
                SELECT tv_show_id
                FROM tv_shows
                WHERE tv_show_name=?
'''
                data_tuple = (e.name,)
                if verbosity:
                    self.__logger.write("Fetching tv_show_id for the newly inserted tv_show\n")
                tv_show_id = cursor.execute(query, data_tuple).fetchone()[0]
                if verbosity:
                    self.__logger.write("ID fetched done.\n")
                # inserting episodes into db now,
                episodes_list = []
                for episode in os.scandir(path=e.path):
                    query = '''
                    INSERT INTO "episodes"
                    (episode_name, tv_show_id, created_date)
                    VALUES (?,?,?);
'''
                    episode_name = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", episode.name).group()
                    data_tuple = (episode_name, tv_show_id, self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name + '/' + episode.name))     # /media/from/tv_shows/ + Ae Dil/ + episode1.mp4
                    if verbosity:
                        self.__logger.write(f"Attempting to insert episodes now ({episode_name}).\n")
                    cursor.execute(query, data_tuple)
                    a[e.name].append(episode_name)
                    # adding to the dict that will be used for email purposes
                    tv_shows[e.name].append(episode_name)
                    # appending it to the Episodes object to be then inserted into TVShow object
                    episodes_list.append(Episode(episode_name=episode_name, created_date=created_date))
                # appending a TVShow object along with its all data to the tv_shows_list to be used in emailing purpose
                tv_shows_list.append(TVShow(tv_show_id=tv_show_id, tv_show_name=e.name, created_date=created_date, 
                                            last_modified_date=last_modified_date, channel_name=channel_name,
                                            episodes=episodes_list, newly_added=True))
                if verbosity:
                    # print(f"[TV_SHOW_EPISODES]: ({e.name})--> {a[e.name]}")
                    self.__logger.write("Episodes sucessfully inserted.\n")
                # setting GLOBAL New_Added_TV_Shows to True, to find out whether new tv_shows were added or not
                tv_shows_list[0].NEW_TV_SHOW_ADDED = True

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
                self.__logger.write(f"Executing query to fetch all inserted episodes for the tv_show_id({tv_show_id}).\n")
                episodes = cursor.execute(query, (tv_show_id, )).fetchall()
                episodes = [c[0] for c in episodes]     # these are all the episodes that are already present in DB and are now fetched
                if verbosity:
                    # print(f"[EPISODES]: {episodes}")
                    self.__logger.write("Episodes successfully fetched.\n")
                a = {}
                episode_inserted_flag = False
                episodes_list = []      # to be used for email purpose

                # iterating on that tv_show
                for episode in os.scandir(path=e.path): # for each episode of that tv_show
                    episode_name = re.search(r"Ep[ -_#@]\d{0,3}|Episode[ -_#@]{,3}\d{0,3}|Last[ -_#]{,3}Episode|2nd[ -_#@]{,3}Last Episode[ -_#@]{,3}\d{0,3}", episode.name).group()
                    if episode_name not in episodes:    # if current_episode is not present in already fethced episodes
                        # append to list with name as its key and birth_time as its value, if that episode is already not present in db
                        a[episode_name] = self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name + '/' + episode.name)
                        # also appending it to the episodes_list for that tv_show
                        episodes_list.append(Episode(episode_name=episode_name, 
                                                     created_date=self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name + '/' + episode.name)))
                        # query to insert episode along with its details into the db
                        query = '''
                        INSERT INTO "episodes"
                        (episode_name, tv_show_id, created_date)
                        VALUES(?,?,?);
                        '''
                        data_tuple = (episode_name, tv_show_id, self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name + '/' + episode.name))
                        if verbosity:
                            self.__logger.write(f"Attemtping to insert episode in the tv_show ({e.name}).\n")
                        cursor.execute(query, data_tuple)
                        if verbosity:
                            self.__logger.write("Sucessfully inserted.\n")
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
                    data_tuple = (time.ctime(), tv_show_id)
                    if verbosity:
                        self.__logger.write(f"Updating last_modified_date for the tv_show ({e.name}).\n")
                    cursor.execute(query, data_tuple)
                    if verbosity:
                        self.__logger.write('Last modified date updated successfully.\n')
                    # now reverting the flag
                    episode_inserted_flag = False
                    # appending a TVShow object to the tv_show_list to be further used in email purpose
                    tv_shows_list.append(TVShow(tv_show_id=tv_show_id, tv_show_name=e.name,
                                                channel_name=channel_name, episodes=episodes_list,
                                                created_date=self.__get_creation_time(self.__TV_SHOWS_CRAWLING_PATH + e.name + '/' + episode.name)))
                    # setting the UPDATED_TV_Show to True to check either tv_shows were updated or not
                    tv_shows_list[0].UPDATED_TV_SHOWS = True
                # controllig output with verbosity statements
                if verbosity:
                    print(f"{e.name}: {a}")
        if verbosity:
            self.__logger.write("-------------------------nmtatstd(), DONE-------------------------\n")
        # Return point
        # return tv_shows
        return tv_shows_list

    # cetid(create_email_table_in_database)
    def cetid(self, verbosity:bool = False, db_name: str = None):
        """Creates Emails table in the given db.
        Args:
            db_name (str, optional): _description_. Defaults to None. Name of the DB in which "emails" table to be initialized
        """
        
        if verbosity:
            self.__logger.write("-------------------------Create Email Table in DB, cetid()-------------------------\n")
        if db_name:
            if verbosity:
                self.__logger.write("Acquiring cursor from the db.\n")
            cursor = self.conn.cursor()
            if verbosity:
                self.__logger.write("Cursor successfully acquired.\n")
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
                if verbosity:
                    self.__logger.write("Executing query to create 'emails' table in db.\n")
                cursor.execute(query)
                if verbosity:
                    self.__logger.write("Table successfully created.\n")
            except sqlite3.OperationalError:
                if verbosity:
                    self.__logger.write("Table 'emails' already exists in DB.\n")
                # print(f"{self.ERROR}table 'emails' already exists in DB.")
                self.__logger.write("-------------------------cetid(), DONE-------------------------\n")
                return 
            self.__logger.write("-------------------------cetid(), DONE-------------------------\n")
        else:
            self.__logger.write("Attribute error, 'db_name' cannot be none.\n")
            self.__logger.write("-------------------------cetid(), DONE-------------------------\n")
            raise TypeError("db_name cannot be none.")
        
    # aetd (add_emails_to_database)
    def aetd(self, verbosity: bool = False, file: str = None, db_name: str = None):
        """Add emails to the db_name. If either of file or db_name is None, the program quits.

        Args:
            file (str, optional): _description_. Defaults to None. Name of the file from which emails to be extracted from,
            can be of .xlsx or .csv. Must includes only two headers in the columns. These are... email, full_name
            db_name (str, optional): _description_. Defaults to None. Name of the database in which emails to be inserted.
        """

        if verbosity:
            self.__logger.write("-------------------------Add Emails To Database, aetd()-------------------------\n")
        if file is None or db_name is None:
            if verbosity:
                self.__logger.write("Attribute 'db_name' OR/AND 'file' cannot be none.\n")
                self.__logger.write("-------------------------aetd(), DONE-------------------------\n")
            raise TypeError("db_name or file cannot be none.")
        else:
            if verbosity:
                self.__logger.write("Acquiring cursor from db.\n")
            cursor = self.conn.cursor()
            if verbosity:
                self.__logger.write("Cursor sucessfully acquired.\n")
                self.__logger.write(f"Reading from excel file ({file}) and creating df object.\n")
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
                    if verbosity:
                        self.__logger.write("Executing query to insert full_name and email into DB.\n")
                    cursor.execute(query, data_tuple)
                    if verbosity:
                        self.__logger.write("Query successfully executed.\n")
                except sqlite3.IntegrityError:
                    if verbosity:
                        self.__logger.write(f"{self.WARNING}email \"{d[1]}\" already exists in the DB.")
                    # print(f"{self.WARNING}email \"{d[1]}\" already exists in the DB.")
        self.__logger.write("-------------------------aetd(), DONE-------------------------\n")
 
    # send_emails
    def send_emails(self, verbose: bool = False, db_name: str = None, movies_list: list = None, tv_shows: TVShow = None,
                    sender_mail: str = None, sender_password: str = None, sender_name: str = None,
                    sender_subject: str = None) -> bool:
        if verbose:
            self.__logger.write("-------------------------SEND EMAILS, send_emails()-------------------------\n")
        for receipent in self.__receipents_emails:
            # message (email markup) for the user is generated by the .__ce() method.
            if verbose:
                self.__logger.write(f"Constructing message (email markup) for the receipent ({receipent}).\n")
            message = self.__ce(verbose=verbose, db_name=db_name, movies_list=movies_list, tv_shows=tv_shows, 
                                full_name=receipent[1])
            if verbose:
                self.__logger.write(f"[SENDING EMAIL]: to {receipent[1].capitalize()} @ {receipent[0]}\n")
            flag = self.__Mail_Handler.send_email(verbose=verbose, logger=self.__logger,
                                                  message=message, receiver_email=receipent[0],
                                                  sender_email=sender_mail, sender_password=sender_password,
                                                  sender_name=sender_name, email_subject=sender_subject)
            if verbose and flag:    # if verbosity is enabled and email is being sent
                self.__logger.write(f"[EMAIL SENT]: to {receipent[1].capitalize()} @ {receipent[0]}\n")
            if not flag:    # if verbosity is enabled but the email is not sent due to some reason
                if verbose:
                    self.__logger.write(f"[EMAIL NOT SENT]: to {receipent[1].capitalize()} @ {receipent[0]}\n")
                self.__logger.write("-------------------------send_emails(), DONE-------------------------\n")
                return False
        if verbose:
            self.__logger.write("-------------------------send_emails(), DONE-------------------------\n")
        return True

    # commit
    def commit(self, verbosity: bool=False):
        if verbosity:
            self.__logger.write("-------------------------Commit, commit()-------------------------\n")
            self.__logger.write("Committing to the db.\n")
        self.conn.commit()
        if verbosity:
            self.__logger.write("Closing connection to the db.\n")
        self.conn.close()
        if verbosity:
            self.__logger.write("-------------------------commit(), DONE-------------------------\n")

    # proceed
    def proceed(self, verbosity: bool = False, crawling_path_movies: str = None, crawling_path_tv_shows: str = None) -> None:
        """Proceed the script for the user. User just needs to provide the directory paths for the movies and tv_shows to crawl from.

        Args:
            verbosity (bool, optional): Set to True to increase output else False. Defaults to False.
            crawling_path_movies (str, optional): Directory path for the movies to add/look/crawl from. Defaults to None.
            crawling_path_tv_shows (str, optional): Directory path for the tv_shows to add/look/crawl from. Defaults to None.
        """
        self.__MOVIES_CRAWLING_PATH = crawling_path_movies
        self.__TV_SHOWS_CRAWLING_PATH = crawling_path_tv_shows
        if verbosity:
            self.__logger.write("-------------------------Proceed, proceed()-------------------------\n")
            self.__logger.write(f"Fetching 'movies' from the crawling_path={crawling_path_movies}.\n")
        movies = self.amtd(verbose=verbosity, path=crawling_path_movies, db_name=self.__db_name)
        if verbosity:
            self.__logger.write("Movies fetched successfully.\n")
            self.__logger.write(f"Fetching tv_shows from the crawling_path={crawling_path_tv_shows}.\n")
        tv_shows = self.nmtatstd(verbosity=verbosity, path=crawling_path_tv_shows, db_name=self.__db_name)
        if verbosity:
            self.__logger.write("Tv Show fetched successfully.\n")
            self.__logger.write("Preparing to send emails to the receipents.\n")
        email_flag = self.send_emails(verbose=verbosity, db_name=self.__db_name, movies_list=movies, tv_shows=tv_shows,
                                      sender_mail=self.__SERVER_EMAIL, sender_password=self.__SERVER_PASSWORD,
                                      sender_name='ZMS', sender_subject=self.__SERVER_EMAIL_SUBJECT)
        # email_flag = True
        if verbosity:
            self.__logger.write(f"EMAIL_FLAG={email_flag}.\n")
        if email_flag:  # if email is sent
            if verbosity:
                self.__logger.write("Email sent successfully.\nNow commiting changes to the DB.\n")
            self.commit(verbosity=verbosity)
            if verbosity:
                self.__logger.write("Commiting changes done.\n")
                self.__logger.write(f"Now, moving movies=({crawling_path_movies}) and tv_shows=({crawling_path_tv_shows}).\n")
            self.__move_media(verbosity=verbosity, movies_from_path=crawling_path_movies, 
                              tv_shows_from_path=crawling_path_tv_shows)
            if verbosity:
                self.__logger.write("Moving movies and tv_shows successful.\n")
        else:   # if email is not sent
            if verbosity:
                self.__logger.write("Email not sent.\n")
            pass
        if verbosity:
            self.__logger.write("-------------------------proceed(), DONE-------------------------\n")
            self.__logger.write("Closing Script...\n")