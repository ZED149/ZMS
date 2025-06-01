

# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="/home/salman/ZMS/media_manager/.env")

# GLOBAL Variables
DB_NAME = os.getenv('DB_NAME')                                  # name of the database
VERBOSITY = bool(os.getenv("VERBOSITY"))                        # either to increase output
LOGGER_NAME = os.getenv("LOGGER_NAME")                          # name of the logger to be used for all logs (verbosity needs to be true for this purpose)
MOVIES_CRAWLING_PATH = os.getenv("MOVIES_CRAWLING_PATH")        # path to crawl to read movies from
TV_SHOWS_CRAWLING_PATH = os.getenv("TV_SHOWS_CRAWLING_PATH")    # path to crawl to read tv_shows from
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')                          # email of the admin
ADMIN_NAME = os.getenv('ADMIN_NAME')                            # name of the admin
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")                    # password of the admin email account

# MAIN
if __name__ == "__main__":
    print("Script initiated...")

    # Instanciating MediaManager object
    o = MediaManager(verbosity=VERBOSITY, db_name=DB_NAME, logger_name=LOGGER_NAME,
                     a_name=ADMIN_NAME, a_email=ADMIN_EMAIL, a_password=ADMIN_PASSWORD)
    
    # proceeding script
    o.proceed(verbosity=VERBOSITY, crawling_path_movies=MOVIES_CRAWLING_PATH,
              crawling_path_tv_shows=TV_SHOWS_CRAWLING_PATH)
    