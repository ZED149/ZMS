

# including important libraries
from media_manager import MediaManager
import os
from dotenv import load_dotenv

# loading enviournmental variables into our scope
load_dotenv(dotenv_path="media_manager/.env")

# GLOBAL
DB_NAME = os.getenv('DB_NAME')

# MAIN
if __name__ == "__main__":
    print("Working")
    o = MediaManager()
    
    # creating movies table in the db
    # o.cmtid(DB_NAME)

    # adding all movies to the db
    o.amtd("media_manager/movies/", DB_NAME)

    # creating tv_shows table in the db
    # o.ctstid(DB_NAME)
    
    # adding tv_shows to the db
    o.atstd("media_manager/tv_shows/", DB_NAME)