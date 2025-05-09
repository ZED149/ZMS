

# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="media_manager/.env")

# GLOBAL Variables
DB_NAME = os.getenv('DB_NAME')
VERBOSITY = bool(os.getenv("VERBOSITY"))
LOGGER_NAME = os.getenv("LOGGER_NAME")
MOVIES_CRAWLING_PATH = os.getenv("MOVIES_CRAWLING_PATH")
TV_SHOWS_CRAWLING_PATH = os.getenv("TV_SHOWS_CRAWLING_PATH")

# MAIN
if __name__ == "__main__":
    print("Script initiated...")

    # Instanciating MediaManager object
    o = MediaManager(verbosity=VERBOSITY, db_name=DB_NAME, logger_name=LOGGER_NAME)

    # crawling the directory for new movies
    movies = o.amtd(verbose=True, path=MOVIES_CRAWLING_PATH, db_name=DB_NAME)
    # crawling the directory for new or updated tv_shows
    tv_shows = o.nmtatstd(verbosity=True, db_name=DB_NAME, path=TV_SHOWS_CRAWLING_PATH)

    # sending emails to receipents
    flag = o.send_emails(verbose=True, db_name=DB_NAME, movies_list=movies, tv_shows=tv_shows)
    if flag:
        # print("Being committed to the DB.")
        o.commit(verbosity=True)
    else:
        # print("email not send and not committed to the DB.")
        pass