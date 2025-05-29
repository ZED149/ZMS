

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
    
    # proceeding script
    o.proceed(verbosity=VERBOSITY, crawling_path_movies=MOVIES_CRAWLING_PATH,
              crawling_path_tv_shows=TV_SHOWS_CRAWLING_PATH)
    